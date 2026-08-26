"""Full-action counterfactual Bellman augmentation on the original DQN."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from crgr_agent import CRGRAgentConfig, CRGRDQNAgent


@dataclass(frozen=True)
class CFBAAgentConfig(CRGRAgentConfig):
    counterfactual_lambda: float = 0.0
    use_counterfactual: bool = False


class CFBADQNAgent(CRGRDQNAgent):
    """Standard DQN plus exact one-step targets for the two unchosen actions."""

    config: CFBAAgentConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.config.use_counterfactual and self.config.counterfactual_lambda <= 0:
            raise ValueError(
                "counterfactual_lambda must be positive when augmentation is enabled"
            )

    def _counterfactual_targets(
        self,
        next_states: torch.Tensor,
        dones: torch.Tensor,
        preview_costs: torch.Tensor,
        preview_resources: torch.Tensor,
    ) -> torch.Tensor:
        batch_size = next_states.shape[0]
        counterfactual_next = next_states[:, None, :].expand(
            batch_size, self.action_dim, next_states.shape[1]
        ).clone()
        # The next task is exogenous and action-independent.  Only the six
        # endogenous resource coordinates differ across counterfactual actions.
        counterfactual_next[:, :, -6:] = preview_resources
        flat_next = counterfactual_next.reshape(-1, next_states.shape[1])
        with torch.no_grad():
            # Deliberately standard DQN, not Double DQN: the target network
            # both selects and evaluates the maximizing next action.
            next_value = self.target(flat_next).max(dim=1).values.reshape(
                batch_size, self.action_dim
            )
            return -preview_costs + self.config.gamma * (1.0 - dones[:, None]) * next_value

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

        counterfactual_loss = torch.zeros((), dtype=torch.float32, device=self.device)
        if self.config.use_counterfactual:
            costs = torch.as_tensor(
                preview_costs, dtype=torch.float32, device=self.device
            )
            resources = torch.as_tensor(
                preview_resources, dtype=torch.float32, device=self.device
            )
            targets = self._counterfactual_targets(
                next_states, dones, costs, resources
            )
            unchosen = ~nn.functional.one_hot(
                actions, num_classes=self.action_dim
            ).bool()
            counterfactual_loss = nn.functional.smooth_l1_loss(
                q_values[unchosen], targets[unchosen]
            )

        total_loss = (
            td_loss
            + self.config.counterfactual_lambda * counterfactual_loss
        )
        self.optimizer.zero_grad(set_to_none=True)
        total_loss.backward()
        nn.utils.clip_grad_norm_(self.online.parameters(), 10.0)
        self.optimizer.step()
        if self.steps % self.config.target_interval == 0:
            self.target.load_state_dict(self.online.state_dict())

        return {
            "loss": float(total_loss.item()),
            "td_loss": float(td_loss.item()),
            "counterfactual_loss": float(counterfactual_loss.item()),
        }
