from __future__ import annotations

import copy
from pathlib import Path
import random
import unittest

import numpy as np
import torch

from md_cbad_dqn.agent import AgentConfig, DQNAgent, QNetwork
from md_cbad_dqn.environment import EnvConfig, SatelliteSchedulingEnv
from md_cbad_dqn.planner import PlannerConfig, RecedingHorizonPlanner


class EnvironmentPreviewTests(unittest.TestCase):
    def test_preview_is_side_effect_free(self) -> None:
        env = SatelliteSchedulingEnv(EnvConfig(horizon=16, scenario="burst"))
        env.reset(seed=1234)
        before = copy.deepcopy(env.snapshot())
        env.preview_all_actions()
        after = env.snapshot()
        self.assertEqual(before["t"], after["t"])
        np.testing.assert_array_equal(before["resources"], after["resources"])
        np.testing.assert_array_equal(before["tasks"], after["tasks"])
        np.testing.assert_array_equal(before["link_trace"], after["link_trace"])
        np.testing.assert_array_equal(
            before["task_primitives"], after["task_primitives"]
        )
        self.assertEqual(before["rng"], after["rng"])

    def test_preview_matches_real_step(self) -> None:
        for action in range(3):
            env = SatelliteSchedulingEnv(
                EnvConfig(horizon=16, coupling=1.0, scenario="link_limited")
            )
            env.reset(seed=771)
            costs, resources = env.preview_all_actions()
            _, _, _, info = env.step(action)
            np.testing.assert_allclose(resources[action], env.resources, rtol=0, atol=0)
            self.assertAlmostEqual(float(costs[action]), info["total_cost"], places=5)

    def test_physics_preview_matches_real_step(self) -> None:
        for action in range(3):
            env = SatelliteSchedulingEnv(
                EnvConfig(
                    horizon=16,
                    coupling=1.0,
                    scenario="thermal_stress",
                    generator="physics_correlated",
                )
            )
            env.reset(seed=908)
            before = copy.deepcopy(env.snapshot())
            costs, resources = env.preview_all_actions()
            after = env.snapshot()
            self.assertEqual(before["rng"], after["rng"])
            np.testing.assert_array_equal(before["resources"], after["resources"])
            np.testing.assert_array_equal(before["tasks"], after["tasks"])
            _, _, _, info = env.step(action)
            np.testing.assert_allclose(resources[action], env.resources, rtol=0, atol=0)
            self.assertAlmostEqual(float(costs[action]), info["total_cost"], places=5)


class PhysicsGeneratorTests(unittest.TestCase):
    def test_task_descriptors_obey_dataflow_constraints(self) -> None:
        env = SatelliteSchedulingEnv(
            EnvConfig(horizon=20_000, generator="physics_correlated")
        )
        env.reset(seed=9_117_031)
        raw = env.task_primitives[:, 0]
        workload = env.task_primitives[:, 1]
        result = env.tasks[:, 5]
        feature = env.tasks[:, 14]
        self.assertTrue(np.isfinite(env.tasks).all())
        self.assertTrue((env.task_primitives > 0).all())
        self.assertTrue((result <= feature).all())
        self.assertTrue((feature <= raw).all())
        self.assertGreater(float(np.corrcoef(raw, workload)[0, 1]), 0.45)
        self.assertGreater(float(np.corrcoef(workload, env.tasks[:, 0])[0, 1]), 0.90)
        self.assertGreater(float(np.corrcoef(raw, env.tasks[:, 6])[0, 1]), 0.99)

    def test_parameter_scales_have_declared_direction(self) -> None:
        base = SatelliteSchedulingEnv(
            EnvConfig(horizon=128, generator="physics_correlated")
        )
        scaled = SatelliteSchedulingEnv(
            EnvConfig(
                horizon=128,
                generator="physics_correlated",
                compute_scale=1.2,
                data_scale=1.2,
            )
        )
        base.reset(seed=44)
        scaled.reset(seed=44)
        np.testing.assert_allclose(
            scaled.task_primitives[:, 0],
            1.2 * base.task_primitives[:, 0],
            rtol=2e-7,
        )
        np.testing.assert_allclose(
            scaled.task_primitives[:, 1],
            1.2 * base.task_primitives[:, 1],
            rtol=2e-7,
        )


class PlannerTests(unittest.TestCase):
    def test_planner_does_not_mutate_environment(self) -> None:
        env = SatelliteSchedulingEnv(
            EnvConfig(horizon=16, generator="physics_correlated")
        )
        env.reset(seed=125)
        before = copy.deepcopy(env.snapshot())
        action = RecedingHorizonPlanner().act(env)
        after = env.snapshot()
        self.assertIn(action, (0, 1, 2))
        self.assertEqual(before["t"], after["t"])
        self.assertEqual(before["rng"], after["rng"])
        for key in ("resources", "tasks", "link_trace", "task_primitives"):
            np.testing.assert_array_equal(before[key], after[key])

    def test_one_step_planner_equals_immediate_argmin(self) -> None:
        env = SatelliteSchedulingEnv(
            EnvConfig(horizon=16, generator="physics_correlated")
        )
        env.reset(seed=126)
        planner = RecedingHorizonPlanner(PlannerConfig(horizon=1, gamma=0.97))
        self.assertEqual(planner.act(env), int(np.argmin(env.immediate_costs())))


class PureDQNTests(unittest.TestCase):
    def _fill(self, agent: DQNAgent, preview_value: float) -> None:
        rng = np.random.default_rng(9)
        for index in range(agent.config.batch_size):
            state = rng.normal(size=21).astype(np.float32)
            next_state = rng.normal(size=21).astype(np.float32)
            agent.observe(
                state,
                index % 3,
                float(rng.normal()),
                next_state,
                index % 11 == 0,
                np.full(3, preview_value, dtype=np.float32),
                np.full((3, 6), preview_value, dtype=np.float32),
            )

    def test_standard_dqn_ignores_counterfactual_payload(self) -> None:
        config = AgentConfig(batch_size=16)
        left = DQNAgent("standard_dqn", config, torch.device("cpu"), seed=17)
        right = DQNAgent("standard_dqn", config, torch.device("cpu"), seed=17)
        self._fill(left, 0.0)
        self._fill(right, 99.0)
        left.update()
        right.update()
        for a, b in zip(left.online.parameters(), right.online.parameters()):
            torch.testing.assert_close(a, b, rtol=0, atol=0)

    def test_centering_is_invariant_to_common_shift(self) -> None:
        values = torch.tensor([[1.0, 4.0, -2.0], [0.5, 0.0, 2.5]])
        shifted = values + torch.tensor([[91.0], [-13.0]])
        torch.testing.assert_close(
            DQNAgent.centered(values), DQNAgent.centered(shifted)
        )

    def test_all_variants_share_network_shape(self) -> None:
        reference = [p.shape for p in QNetwork().parameters()]
        for variant in ("standard_dqn", "md_cfba_dqn", "md_cbad_dqn"):
            agent = DQNAgent(
                variant, AgentConfig(), torch.device("cpu"), seed=1
            )
            self.assertEqual(reference, [p.shape for p in agent.online.parameters()])

    def test_factual_target_is_standard_target_network_max(self) -> None:
        agent = DQNAgent(
            "standard_dqn", AgentConfig(batch_size=2), torch.device("cpu"), seed=3
        )
        self._fill(agent, 0.0)
        batch = agent.buffer.sample(2, random.Random(4))
        states, actions, rewards, next_states, dones, *_ = batch
        losses = agent.compute_losses(batch)
        with torch.no_grad():
            states_t = torch.as_tensor(states)
            actions_t = torch.as_tensor(actions).long()
            next_t = torch.as_tensor(next_states)
            expected_target = torch.as_tensor(rewards, dtype=torch.float32) + agent.config.gamma * (
                1 - torch.as_tensor(dones, dtype=torch.float32)
            ) * agent.target(next_t).max(1).values
            expected = torch.nn.functional.smooth_l1_loss(
                agent.online(states_t).gather(1, actions_t[:, None]).squeeze(1),
                expected_target,
            )
        torch.testing.assert_close(losses["td_loss"], expected)


class SourceGuardTests(unittest.TestCase):
    def test_no_forbidden_dqn_enhancement(self) -> None:
        source = (Path(__file__).parents[1] / "agent.py").read_text(encoding="utf-8").lower()
        forbidden_symbols = (
            "prioritizedreplay", "duelingnetwork", "noisylayer",
            "distributionaldqn", "n_step_return",
        )
        for symbol in forbidden_symbols:
            self.assertNotIn(symbol, source)


if __name__ == "__main__":
    unittest.main()
