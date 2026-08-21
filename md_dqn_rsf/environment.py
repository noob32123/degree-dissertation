"""Sequential satellite--ground scheduling environment.

The environment retains the manuscript's 15 task descriptors and augments them
with six dynamic resource variables.  Exogenous task and link traces are drawn
once at reset, so all policies evaluated with the same seed face identical
arrivals.  Actions only change endogenous resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class EnvConfig:
    horizon: int = 64
    coupling: float = 1.0
    scenario: str = "nominal"


class SatelliteSchedulingEnv:
    """Small Gym-like environment without an external Gym dependency."""

    task_dim = 15
    resource_dim = 6
    state_dim = task_dim + resource_dim
    action_dim = 3

    def __init__(self, config: EnvConfig):
        self.config = config
        self.rng = np.random.default_rng()
        self.tasks = np.empty((0, self.task_dim), dtype=np.float32)
        self.link_trace = np.empty((0, 2), dtype=np.float32)
        self.resources = np.zeros(self.resource_dim, dtype=np.float32)
        self.t = 0

    def reset(self, seed: int | None = None) -> np.ndarray:
        self.rng = np.random.default_rng(seed)
        self.tasks = self._generate_tasks(self.config.horizon)
        self.link_trace = self._generate_link_trace(self.config.horizon + 1)
        initial_energy = 0.62 if self.config.scenario == "energy_limited" else 0.88
        initial_heat = 0.42 if self.config.scenario == "thermal_stress" else 0.22
        self.resources = np.array(
            [initial_heat, initial_energy, 0.12, 0.18,
             self.link_trace[0, 0], self.link_trace[0, 1]], dtype=np.float32
        )
        self.t = 0
        return self._state()

    def _generate_tasks(self, n: int) -> np.ndarray:
        # Raw ranges reproduce the legacy simulator; the state exposes them in
        # normalized form. Bursty traces increase demand in contiguous periods.
        r = self.rng
        x = np.empty((n, self.task_dim), dtype=np.float32)
        x[:, 0] = r.uniform(0, 1000, n)       # onboard heat
        x[:, 1] = r.uniform(0, 1000, n)       # onboard FLOPs
        x[:, 2] = r.uniform(0, 1000, n)       # onboard processing latency
        x[:, 3] = r.uniform(200, 300, n)      # onboard transfer latency
        x[:, 4] = r.integers(0, 50, n) ** 2   # co-location penalty
        x[:, 5] = r.uniform(0, 1000, n)       # onboard bandwidth
        x[:, 6] = r.uniform(0, 1000, n)       # ground heat proxy
        x[:, 7] = r.uniform(200, 20000, n)    # ground transfer latency
        x[:, 8] = r.uniform(0, 1000, n)       # ground bandwidth
        total_heat = r.uniform(0, 1000, n)
        split = r.uniform(0.2, 0.8, n)
        x[:, 9] = total_heat * split          # hybrid preprocessing heat
        x[:, 10] = total_heat * (1 - split)   # hybrid transmission heat
        x[:, 11] = r.uniform(0, 1000, n)      # hybrid preprocessing latency
        x[:, 12] = r.uniform(200, 20000, n)   # hybrid transfer latency
        x[:, 13] = r.uniform(0, 1000, n)      # hybrid FLOPs
        x[:, 14] = r.uniform(0, 1000, n)      # hybrid bandwidth

        if self.config.scenario in {"burst", "thermal_stress"}:
            start, width = n // 3, max(4, n // 4)
            sl = slice(start, min(n, start + width))
            x[sl, [0, 1, 2, 9, 10, 11, 13]] *= 1.45
        return x

    def _generate_link_trace(self, n: int) -> np.ndarray:
        r = self.rng
        phase = r.uniform(0, 2 * np.pi)
        idx = np.arange(n)
        bandwidth = 0.62 + 0.23 * np.sin(2 * np.pi * idx / 24 + phase)
        bandwidth += r.normal(0, 0.06, n)
        if self.config.scenario == "link_limited":
            bandwidth -= 0.22
        bandwidth = np.clip(bandwidth, 0.12, 1.0)
        contact = 0.55 + 0.35 * np.sin(2 * np.pi * idx / 31 + phase / 2)
        contact += r.normal(0, 0.04, n)
        contact = np.clip(contact, 0.08, 1.0)
        return np.column_stack((bandwidth, contact)).astype(np.float32)

    @staticmethod
    def _normalize_task(raw: np.ndarray) -> np.ndarray:
        scales = np.array(
            [1000, 1000, 1000, 300, 2401, 1000, 1000, 20000, 1000,
             1000, 1000, 1000, 20000, 1000, 1000], dtype=np.float32
        )
        return np.clip(raw / scales, 0.0, 1.5).astype(np.float32)

    def _state(self) -> np.ndarray:
        task = self._normalize_task(self.tasks[min(self.t, len(self.tasks) - 1)])
        return np.concatenate((task, self.resources)).astype(np.float32)

    def immediate_costs(self) -> np.ndarray:
        """Return state-conditioned analytical immediate costs for all actions."""
        x = self.tasks[self.t]
        heat, energy, queue, util, bandwidth, contact = self.resources
        eps = 0.08

        # Legacy decompositions, with measured resource conditions modifying
        # effective latency and contention terms.
        onboard = (
            0.4 * np.tan(np.pi / 2 * np.clip(x[0] / 5000, 0, 0.95))
            + 0.0004 * x[1]
            + 0.0002 * (x[2] * (1 + 1.4 * util + 0.7 * queue) + x[3])
            + 0.004 * x[4] * (1 + queue)
            + 0.4 * np.tan(np.pi / 2 * np.clip(x[5] / 5000, 0, 0.95))
            + 0.35 * heat + 0.12 * (1 - energy)
        )
        ground = (
            (2 / 3) * np.tan(np.pi / 2 * np.clip(x[6] / 5000, 0, 0.95))
            + 0.0005 * x[7] / max(float(bandwidth), eps)
            + 0.4 * np.tan(np.pi / 2 * np.clip(x[8] / 5000, 0, 0.95))
            + 0.35 * max(0.0, 0.28 - float(contact))
        )
        hybrid = (
            0.4 * np.tan(np.pi / 2 * np.clip((x[9] + x[10]) / 5000, 0, 0.95))
            + 0.0004 * x[13]
            + 0.0004 * x[11] * (1 + 0.8 * util)
            + 0.0004 * x[12] / max(float(bandwidth), eps)
            + 0.4 * np.tan(np.pi / 2 * np.clip(x[14] / 5000, 0, 0.95))
            + 0.18 * heat + 0.12 * queue
            + 0.18 * max(0.0, 0.22 - float(contact))
        )
        return np.array([onboard, ground, hybrid], dtype=np.float32)

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, float]]:
        if action not in (0, 1, 2):
            raise ValueError(f"invalid action {action}")
        x = self.tasks[self.t]
        immediate = float(self.immediate_costs()[action])
        h, e, q, u, b, tau = map(float, self.resources)
        c = max(0.0, float(self.config.coupling))

        work = np.array([x[1], 0.18 * x[7] / 20, x[13] + 0.25 * x[12] / 20]) / 1000
        heat_load = np.array([x[0], 0.08 * x[6], x[9] + x[10]]) / 1000
        data_load = np.array([0.20 * x[5], x[8], 0.65 * x[14]]) / 1000
        energy_use = np.array(
            [0.012 + 0.042 * work[0],
             0.007 + 0.025 * data_load[1] / max(b, 0.1),
             0.010 + 0.025 * work[2] + 0.018 * data_load[2] / max(b, 0.1)]
        )
        queue_add = np.array(
            [0.055 * work[0] * (1 + u),
             0.048 * data_load[1] / max(b, 0.1),
             0.030 * (work[2] + data_load[2] / max(b, 0.1))]
        )
        service = np.array([0.030 * (1 - u), 0.035 * b * tau, 0.032 * (1 - 0.5 * u)])

        next_h = np.clip(0.86 * h + c * 0.17 * heat_load[action], 0, 1.3)
        next_e = np.clip(e + 0.006 - c * energy_use[action], 0, 1)
        next_q = np.clip(q + c * (queue_add[action] - service[action]), 0, 1.3)
        target_u = np.array([work[0], 0.10 * data_load[1], 0.55 * work[2]])[action]
        next_u = np.clip(0.68 * u + c * 0.32 * target_u, 0, 1.2)

        next_index = min(self.t + 1, self.config.horizon)
        base_b, base_tau = map(float, self.link_trace[next_index])
        link_occupation = np.array([0.02, 0.18 * data_load[1], 0.12 * data_load[2]])[action]
        next_b = np.clip(base_b - c * link_occupation, 0.08, 1)
        next_tau = np.clip(base_tau - c * 0.10 * data_load[action], 0.05, 1)

        # Penalties are computed on the post-decision state, exposing delayed
        # resource consequences while keeping immediate cost interpretable.
        thermal_violation = max(0.0, next_h - 0.78)
        energy_violation = max(0.0, 0.18 - next_e)
        queue_violation = max(0.0, next_q - 0.75)
        contact_violation = float(action != 0) * max(0.0, 0.14 - tau)
        penalty = c * (
            12.0 * thermal_violation + 15.0 * energy_violation
            + 8.0 * queue_violation + 10.0 * contact_violation
        )
        total_cost = immediate + penalty

        self.resources = np.array(
            [next_h, next_e, next_q, next_u, next_b, next_tau], dtype=np.float32
        )
        self.t += 1
        done = self.t >= self.config.horizon
        next_state = np.zeros(self.state_dim, dtype=np.float32) if done else self._state()
        info = {
            "immediate_cost": immediate,
            "penalty": float(penalty),
            "total_cost": float(total_cost),
            "thermal_violation": float(thermal_violation > 0),
            "energy_violation": float(energy_violation > 0),
            "queue_violation": float(queue_violation > 0),
            "contact_violation": float(contact_violation > 0),
            "heat": float(next_h),
            "energy": float(next_e),
            "queue": float(next_q),
        }
        return next_state, -float(total_cost), done, info

