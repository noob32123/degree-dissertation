"""Counterfactual Bellman advantage distillation on the original DQN."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from cfba_agent import CFBAAgentConfig, CFBADQNAgent


@dataclass(frozen=True)
class CBADAgentConfig(CFBAAgentConfig):
    advantage_lambda: float = 0.0
    use_advantage_distillation: bool = False


class CBADDQNAgent(CFBADQNAgent):
    """Distill centered counterfactual targets while retaining factual TD."""

    config: CBADAgentConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            self.config.use_advantage_distillation
            and self.config.advantage_lambda <= 0
        ):
            raise ValueError(
                "advantage_lambda must be positive when distillation is enabled"
            )

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
        chosen_q = q_values.gather(1, actions[:, None]).squeeze(1)
        with torch.no_grad():
            standard_target = rewards + self.config.gamma * (1.0 - dones) * (
                self.target(next_states).max(dim=1).values
            )
        td_loss = nn.functional.smooth_l1_loss(chosen_q, standard_target)

        advantage_loss = torch.zeros((), dtype=torch.float32, device=self.device)
        if self.config.use_advantage_distillation:
            costs = torch.as_tensor(
                preview_costs, dtype=torch.float32, device=self.device
            )
            resources = torch.as_tensor(
                preview_resources, dtype=torch.float32, device=self.device
            )
            counterfactual_targets = self._counterfactual_targets(
                next_states, dones, costs, resources
            )
            # Centering removes the shared bootstrapped state-value offset.
            # Only action gaps, which determine the deployed argmax, are taught.
            predicted_advantage = q_values - q_values.mean(dim=1, keepdim=True)
            target_advantage = counterfactual_targets - counterfactual_targets.mean(
                dim=1, keepdim=True
            )
            advantage_loss = nn.functional.smooth_l1_loss(
                predicted_advantage, target_advantage
            )

        total_loss = td_loss + self.config.advantage_lambda * advantage_loss
        self.optimizer.zero_grad(set_to_none=True)
        total_loss.backward()
        nn.utils.clip_grad_norm_(self.online.parameters(), 10.0)
        self.optimizer.step()
        if self.steps % self.config.target_interval == 0:
            self.target.load_state_dict(self.online.state_dict())

        return {
            "loss": float(total_loss.item()),
            "td_loss": float(td_loss.item()),
            "advantage_loss": float(advantage_loss.item()),
        }
