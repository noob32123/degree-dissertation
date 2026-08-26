"""Deterministic tests for the CRGR environment and agent invariants."""

from __future__ import annotations

import copy
import unittest

import numpy as np
import torch

from agent import AgentConfig, DQNAgent
from cbad_agent import CBADAgentConfig, CBADDQNAgent
from cfba_agent import CFBAAgentConfig, CFBADQNAgent
from cpsr_agent import CPSRAgentConfig, CPSRDQNAgent
from crgr_agent import CRGRAgentConfig, CRGRDQNAgent
from environment import EnvConfig, SatelliteSchedulingEnv


class PreviewTests(unittest.TestCase):
    def test_preview_is_side_effect_free_and_matches_step(self) -> None:
        env = SatelliteSchedulingEnv(EnvConfig(horizon=8))
        env.reset(seed=12345)
        before_t = env.t
        before_resources = env.resources.copy()
        before_tasks = env.tasks.copy()
        before_links = env.link_trace.copy()
        before_rng = copy.deepcopy(env.rng.bit_generator.state)

        costs, resources = env.preview_all_actions()

        self.assertEqual(env.t, before_t)
        np.testing.assert_array_equal(env.resources, before_resources)
        np.testing.assert_array_equal(env.tasks, before_tasks)
        np.testing.assert_array_equal(env.link_trace, before_links)
        self.assertEqual(env.rng.bit_generator.state, before_rng)
        for action in range(3):
            clone = copy.deepcopy(env)
            _, _, _, info = clone.step(action)
            self.assertEqual(float(costs[action]), float(np.float32(info["total_cost"])))
            np.testing.assert_array_equal(resources[action], clone.resources)

    def test_counterfactual_next_states_match_all_real_steps(self) -> None:
        env = SatelliteSchedulingEnv(EnvConfig(horizon=8))
        env.reset(seed=54321)
        before = copy.deepcopy(env)
        _, resources = env.preview_all_actions()
        actual_next, _, _, _ = env.step(0)
        for action in range(3):
            clone = copy.deepcopy(before)
            expected_next, _, _, _ = clone.step(action)
            constructed = actual_next.copy()
            constructed[-6:] = resources[action]
            np.testing.assert_array_equal(constructed, expected_next)


class RankingLossTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = CRGRDQNAgent(
            21,
            3,
            CRGRAgentConfig(
                ranking_lambda=0.3,
                gate_tau=0.06,
                use_ranking=True,
                use_gate=True,
            ),
            torch.device("cpu"),
            seed=7,
        )

    def test_correct_cost_order_has_lower_loss(self) -> None:
        costs = torch.tensor([[1.0, 6.0, 11.0]])
        resources = torch.full((1, 3, 6), 0.5)
        correct_q = torch.tensor([[10.0, 5.0, 0.0]])
        reversed_q = torch.tensor([[0.0, 5.0, 10.0]])
        correct, gate, active = self.agent._ranking_loss(correct_q, costs, resources)
        reversed_loss, _, _ = self.agent._ranking_loss(reversed_q, costs, resources)
        self.assertLess(float(correct), float(reversed_loss))
        self.assertEqual(float(gate), 1.0)
        self.assertEqual(float(active), 1.0)

    def test_large_resource_divergence_disables_pairs(self) -> None:
        q_values = torch.zeros((1, 3))
        costs = torch.tensor([[1.0, 10.0, 20.0]])
        resources = torch.zeros((1, 3, 6))
        resources[:, 1, :] = torch.tensor([1.3, 1.0, 1.3, 1.2, 1.0, 1.0])
        _, gate, active = self.agent._ranking_loss(q_values, costs, resources)
        self.assertLess(float(gate), 1.0)
        self.assertLess(float(active), 1.0)


class ParetoSafeRankingLossTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = CPSRDQNAgent(
            21,
            3,
            CPSRAgentConfig(
                ranking_lambda=1.0,
                pareto_rho=0.05,
                use_ranking=True,
                use_gate=True,
            ),
            torch.device("cpu"),
            seed=19,
        )

    def test_resource_dominating_cheaper_action_gets_full_gate(self) -> None:
        q_values = torch.zeros((1, 3))
        costs = torch.tensor([[1.0, 6.0, 11.0]])
        # Risks are [heat, 1-energy, queue, util, 1-bandwidth, 1-contact].
        # Action 0 is cheaper and strictly safer than actions 1 and 2.
        resources = torch.tensor(
            [[
                [0.10, 0.90, 0.10, 0.10, 0.90, 0.90],
                [0.30, 0.70, 0.30, 0.30, 0.70, 0.70],
                [0.50, 0.50, 0.50, 0.50, 0.50, 0.50],
            ]]
        )
        _, gate, active = self.agent._ranking_loss(q_values, costs, resources)
        self.assertEqual(float(gate), 1.0)
        self.assertEqual(float(active), 1.0)

    def test_one_resource_bottleneck_can_veto_cheaper_action(self) -> None:
        q_values = torch.zeros((1, 3))
        costs = torch.tensor([[1.0, 6.0, 11.0]])
        resources = torch.full((1, 3, 6), 0.5)
        # The cheapest action has normalized queue regret > rho relative to
        # both alternatives, so both pairs involving it must receive no gate.
        resources[:, 0, 2] = 0.70
        _, gate, active = self.agent._ranking_loss(q_values, costs, resources)
        self.assertLessEqual(float(gate), 1.0 / 3.0 + 1e-7)
        self.assertLessEqual(float(active), 1.0 / 3.0 + 1e-7)


class BaselineEquivalenceTests(unittest.TestCase):
    @staticmethod
    def train_original(seed: int) -> DQNAgent:
        config = AgentConfig(epsilon_decay_steps=1_000, steps_per_episode=16)
        agent = DQNAgent(21, 3, config, torch.device("cpu"), seed, 20)
        env = SatelliteSchedulingEnv(EnvConfig(horizon=16))
        for episode in range(20):
            state = env.reset(seed=seed * 1_000_000 + episode)
            done = False
            while not done:
                action = agent.act(state, explore=True)
                next_state, reward, done, _ = env.step(action)
                agent.observe(state, action, reward, next_state, done)
                if agent.steps % 4 == 0:
                    agent.update()
                state = next_state
        return agent

    @staticmethod
    def train_crgr_disabled(seed: int) -> CRGRDQNAgent:
        config = CRGRAgentConfig(epsilon_decay_steps=1_000)
        agent = CRGRDQNAgent(21, 3, config, torch.device("cpu"), seed)
        env = SatelliteSchedulingEnv(EnvConfig(horizon=16))
        for episode in range(20):
            state = env.reset(seed=seed * 1_000_000 + episode)
            done = False
            while not done:
                action = agent.act(state, explore=True)
                next_state, reward, done, _ = env.step(action)
                agent.observe(state, action, reward, next_state, done)
                if agent.steps % 4 == 0:
                    agent.update()
                state = next_state
        return agent

    @staticmethod
    def train_cfba_disabled(seed: int) -> CFBADQNAgent:
        config = CFBAAgentConfig(epsilon_decay_steps=1_000)
        agent = CFBADQNAgent(21, 3, config, torch.device("cpu"), seed)
        env = SatelliteSchedulingEnv(EnvConfig(horizon=16))
        for episode in range(20):
            state = env.reset(seed=seed * 1_000_000 + episode)
            done = False
            while not done:
                action = agent.act(state, explore=True)
                next_state, reward, done, _ = env.step(action)
                agent.observe(state, action, reward, next_state, done)
                if agent.steps % 4 == 0:
                    agent.update()
                state = next_state
        return agent

    @staticmethod
    def train_cbad_disabled(seed: int) -> CBADDQNAgent:
        config = CBADAgentConfig(epsilon_decay_steps=1_000)
        agent = CBADDQNAgent(21, 3, config, torch.device("cpu"), seed)
        env = SatelliteSchedulingEnv(EnvConfig(horizon=16))
        for episode in range(20):
            state = env.reset(seed=seed * 1_000_000 + episode)
            done = False
            while not done:
                action = agent.act(state, explore=True)
                next_state, reward, done, _ = env.step(action)
                agent.observe(state, action, reward, next_state, done)
                if agent.steps % 4 == 0:
                    agent.update()
                state = next_state
        return agent

    def test_disabled_crgr_matches_original_dqn(self) -> None:
        original = self.train_original(seed=11)
        crgr_disabled = self.train_crgr_disabled(seed=11)
        self.assertEqual(original.steps, crgr_disabled.steps)
        self.assertEqual(original.epsilon, crgr_disabled.epsilon)
        for name, value in original.online.state_dict().items():
            self.assertTrue(torch.equal(value, crgr_disabled.online.state_dict()[name]), name)
        for name, value in original.target.state_dict().items():
            self.assertTrue(torch.equal(value, crgr_disabled.target.state_dict()[name]), name)

    def test_disabled_cfba_matches_original_dqn(self) -> None:
        original = self.train_original(seed=23)
        cfba_disabled = self.train_cfba_disabled(seed=23)
        self.assertEqual(original.steps, cfba_disabled.steps)
        self.assertEqual(original.epsilon, cfba_disabled.epsilon)
        for name, value in original.online.state_dict().items():
            self.assertTrue(torch.equal(value, cfba_disabled.online.state_dict()[name]), name)
        for name, value in original.target.state_dict().items():
            self.assertTrue(torch.equal(value, cfba_disabled.target.state_dict()[name]), name)

    def test_disabled_cbad_matches_original_dqn(self) -> None:
        original = self.train_original(seed=29)
        cbad_disabled = self.train_cbad_disabled(seed=29)
        for name, value in original.online.state_dict().items():
            self.assertTrue(torch.equal(value, cbad_disabled.online.state_dict()[name]), name)
        for name, value in original.target.state_dict().items():
            self.assertTrue(torch.equal(value, cbad_disabled.target.state_dict()[name]), name)


if __name__ == "__main__":
    unittest.main()
