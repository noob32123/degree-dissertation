"""Pure-DQN agent with counterfactual resource-divergence-gated ranking.

The implementation intentionally keeps the original network, uniform replay,
one-step Bellman target, epsilon schedule, and update cadence.  CRGR is the
only optional change to the baseline loss.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import copy
import random

import numpy as np
import torch
from torch import nn

from agent import QNetwork, ReplayBuffer


RESOURCE_SCALES = (1.3, 1.0, 1.3, 1.2, 1.0, 1.0)


@dataclass(frozen=True)
class CRGRAgentConfig:
    gamma: float = 0.97
    lr: float = 3e-4
    batch_size: int = 128
    buffer_size: int = 100_000
    target_interval: int = 250
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    epsilon_decay_steps: int = 18_000
    ranking_lambda: float = 0.0
    gate_tau: float = 0.06
    use_ranking: bool = False
    use_gate: bool = False


class CRGRDQNAgent:
    """Standard DQN plus an optional CRGR auxiliary loss."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        config: CRGRAgentConfig,
        device: torch.device,
        seed: int,
    ):
        if action_dim != 3:
            raise ValueError("CRGR currently requires exactly three actions")
        if config.use_ranking and config.ranking_lambda <= 0:
            raise ValueError("ranking_lambda must be positive when ranking is enabled")
        if config.use_gate and not config.use_ranking:
            raise ValueError("resource gating requires ranking to be enabled")
        if config.gate_tau <= 0:
            raise ValueError("gate_tau must be positive")

        self.config = config
        self.device = device
        self.action_dim = action_dim
        self.rng = random.Random(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        self.online = QNetwork(state_dim, action_dim).to(device)
        self.target = copy.deepcopy(self.online).to(device).eval()
        self.optimizer = torch.optim.Adam(self.online.parameters(), lr=config.lr)
        self.buffer = ReplayBuffer(config.buffer_size)
        self.steps = 0
        self.epsilon = config.epsilon_start

    def act(self, state: np.ndarray, explore: bool = True) -> int:
        if explore and self.rng.random() < self.epsilon:
            return self.rng.randrange(self.action_dim)
        with torch.no_grad():
            x = torch.as_tensor(
                state, dtype=torch.float32, device=self.device
            ).unsqueeze(0)
            return int(self.online(x).argmax(dim=1).item())

    def decay_epsilon(self) -> None:
        fraction = min(1.0, self.steps / self.config.epsilon_decay_steps)
        self.epsilon = self.config.epsilon_start + fraction * (
            self.config.epsilon_end - self.config.epsilon_start
        )
        self.epsilon = max(self.config.epsilon_end, self.epsilon)

    def observe(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        preview_costs: np.ndarray | None = None,
        preview_resources: np.ndarray | None = None,
    ) -> None:
        if preview_costs is None:
            preview_costs = np.zeros(3, dtype=np.float32)
        if preview_resources is None:
            preview_resources = np.zeros((3, 6), dtype=np.float32)
        self.buffer.add(
            (
                state,
                action,
                reward,
                next_state,
                float(done),
                preview_costs,
                preview_resources,
            )
        )
        self.steps += 1
        self.decay_epsilon()

    def _ranking_loss(
        self,
        q_values: torch.Tensor,
        costs: torch.Tensor,
        resources: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        scales = torch.as_tensor(
            RESOURCE_SCALES, dtype=torch.float32, device=self.device
        )
        terms: list[torch.Tensor] = []
        gates: list[torch.Tensor] = []
        for left, right in ((0, 1), (0, 2), (1, 2)):
            divergence = (
                (resources[:, left] - resources[:, right]).abs() / scales
            ).mean(dim=1)
            if self.config.use_gate:
                gate = torch.clamp(1.0 - divergence / self.config.gate_tau, min=0.0)
            else:
                gate = torch.ones_like(divergence)
            cost_gap = costs[:, left] - costs[:, right]
            confidence = torch.tanh(cost_gap.abs() / 5.0)
            direction = torch.where(
                cost_gap < 0,
                torch.ones_like(cost_gap),
                -torch.ones_like(cost_gap),
            )
            q_gap = q_values[:, left] - q_values[:, right]
            terms.append(gate * confidence * nn.functional.softplus(-direction * q_gap / 5.0))
            gates.append(gate)

        stacked_terms = torch.stack(terms, dim=1)
        stacked_gates = torch.stack(gates, dim=1)
        loss = stacked_terms.sum(dim=1).div(3.0).mean()
        return loss, stacked_gates.mean(), (stacked_gates > 0).float().mean()

    def update(self) -> dict[str, float] | None:
        if len(self.buffer) < self.config.batch_size:
            return None
        (
            states,
            actions,
            rewards,
            next_states,
            dones,
            preview_costs,
            preview_resources,
        ) = self.buffer.sample(self.config.batch_size, self.rng)
        states = torch.as_tensor(states, dtype=torch.float32, device=self.device)
        actions = torch.as_tensor(actions, dtype=torch.int64, device=self.device)
        rewards = torch.as_tensor(rewards, dtype=torch.float32, device=self.device)
        next_states = torch.as_tensor(next_states, dtype=torch.float32, device=self.device)
        dones = torch.as_tensor(dones, dtype=torch.float32, device=self.device)

        q_values = self.online(states)
        q = q_values.gather(1, actions[:, None]).squeeze(1)
        with torch.no_grad():
            # Deliberately standard DQN: the target network both selects and
            # evaluates the maximizing action.  This is not Double DQN.
            target = rewards + self.config.gamma * (1 - dones) * (
                self.target(next_states).max(1).values
            )
        td_loss = nn.functional.smooth_l1_loss(q, target)

        ranking_loss = torch.zeros((), dtype=torch.float32, device=self.device)
        gate_mean = torch.zeros((), dtype=torch.float32, device=self.device)
        gate_active_fraction = torch.zeros((), dtype=torch.float32, device=self.device)
        if self.config.use_ranking:
            costs = torch.as_tensor(
                preview_costs, dtype=torch.float32, device=self.device
            )
            resources = torch.as_tensor(
                preview_resources, dtype=torch.float32, device=self.device
            )
            ranking_loss, gate_mean, gate_active_fraction = self._ranking_loss(
                q_values, costs, resources
            )

        total_loss = td_loss + self.config.ranking_lambda * ranking_loss
        self.optimizer.zero_grad(set_to_none=True)
        total_loss.backward()
        nn.utils.clip_grad_norm_(self.online.parameters(), 10.0)
        self.optimizer.step()
        if self.steps % self.config.target_interval == 0:
            self.target.load_state_dict(self.online.state_dict())

        return {
            "loss": float(total_loss.item()),
            "td_loss": float(td_loss.item()),
            "ranking_loss": float(ranking_loss.item()),
            "gate_mean": float(gate_mean.item()),
            "gate_active_fraction": float(gate_active_fraction.item()),
        }

    def checkpoint_config(self) -> dict:
        return asdict(self.config)
