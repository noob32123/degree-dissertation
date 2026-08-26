"""Counterfactual Pareto-Safe Ranking on the unchanged DQN backbone."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from crgr_agent import CRGRAgentConfig, CRGRDQNAgent, RESOURCE_SCALES


@dataclass(frozen=True)
class CPSRAgentConfig(CRGRAgentConfig):
    pareto_rho: float = 0.05


class CPSRDQNAgent(CRGRDQNAgent):
    """Rank cheap actions only when they are approximately resource-Pareto-safe."""

    config: CPSRAgentConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.config.pareto_rho <= 0:
            raise ValueError("pareto_rho must be positive")

    def _ranking_loss(
        self,
        q_values: torch.Tensor,
        costs: torch.Tensor,
        resources: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        scales = torch.as_tensor(
            RESOURCE_SCALES, dtype=torch.float32, device=self.device
        )
        normalized = resources / scales
        # Higher values consistently mean higher resource pressure.
        risks = torch.stack(
            (
                normalized[:, :, 0],
                1.0 - normalized[:, :, 1],
                normalized[:, :, 2],
                normalized[:, :, 3],
                1.0 - normalized[:, :, 4],
                1.0 - normalized[:, :, 5],
            ),
            dim=2,
        )
        terms: list[torch.Tensor] = []
        gates: list[torch.Tensor] = []
        for left, right in ((0, 1), (0, 2), (1, 2)):
            cost_gap = costs[:, left] - costs[:, right]
            left_is_cheaper = cost_gap < 0
            cheaper_risk = torch.where(
                left_is_cheaper[:, None], risks[:, left], risks[:, right]
            )
            dearer_risk = torch.where(
                left_is_cheaper[:, None], risks[:, right], risks[:, left]
            )
            # Positive regret means that the cheaper action is worse on at
            # least one resource.  A single bottleneck can veto the teacher.
            worst_resource_regret = (cheaper_risk - dearer_risk).max(dim=1).values
            if self.config.use_gate:
                gate = torch.clamp(
                    1.0
                    - torch.relu(worst_resource_regret) / self.config.pareto_rho,
                    min=0.0,
                    max=1.0,
                )
            else:
                gate = torch.ones_like(cost_gap)
            confidence = torch.tanh(cost_gap.abs() / 5.0)
            direction = torch.where(
                left_is_cheaper,
                torch.ones_like(cost_gap),
                -torch.ones_like(cost_gap),
            )
            q_gap = q_values[:, left] - q_values[:, right]
            terms.append(
                gate
                * confidence
                * nn.functional.softplus(-direction * q_gap / 5.0)
            )
            gates.append(gate)

        stacked_terms = torch.stack(terms, dim=1)
        stacked_gates = torch.stack(gates, dim=1)
        return (
            stacked_terms.sum(dim=1).div(3.0).mean(),
            stacked_gates.mean(),
            (stacked_gates > 0).float().mean(),
        )
