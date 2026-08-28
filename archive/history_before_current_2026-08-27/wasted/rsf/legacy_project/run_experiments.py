"""Train, evaluate, and summarize sequential scheduling policies."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import random
from typing import Callable, Dict

import numpy as np
import pandas as pd
import torch

from agent import AgentConfig, DQNAgent
from environment import EnvConfig, SatelliteSchedulingEnv


def set_deterministic(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_agent_config(name: str, episodes: int, horizon: int) -> AgentConfig:
    flags = {
        "contextual_bandit": dict(gamma=0.0),
        "standard_dqn": {},
        "dqn_r": dict(use_reset=True),
        "dqn_rs": dict(use_reset=True, use_selective=True),
        "md_dqn_rsf": dict(use_reset=True, use_selective=True, use_flush=True),
    }[name]
    return AgentConfig(
        steps_per_episode=horizon,
        epsilon_decay_steps=max(1_000, int(episodes * horizon * 0.35)),
        **flags,
    )


def train_agent(name: str, seed: int, episodes: int, horizon: int,
                device: torch.device) -> tuple[DQNAgent, list[dict]]:
    config = make_agent_config(name, episodes, horizon)
    agent = DQNAgent(21, 3, config, device, seed, episodes)
    env = SatelliteSchedulingEnv(EnvConfig(horizon=horizon, coupling=1.0, scenario="nominal"))
    curve = []
    rolling = []
    for episode in range(episodes):
        agent.schedule_episode_events(episode)
        state = env.reset(seed=seed * 1_000_000 + episode)
        episode_cost = 0.0
        losses = []
        done = False
        while not done:
            action = agent.act(state, explore=True)
            next_state, reward, done, info = env.step(action)
            agent.observe(state, action, reward, next_state, done)
            # A small fully connected network is memory-latency bound on the
            # GPU; one update per four environment steps is both faster and
            # less correlated than updating on every adjacent transition.
            loss = agent.update() if agent.steps % 4 == 0 else None
            if loss is not None:
                losses.append(loss)
            episode_cost += info["total_cost"]
            state = next_state
        rolling.append(episode_cost)
        if episode % 10 == 0 or episode == episodes - 1:
            curve.append({
                "policy": name, "seed": seed, "episode": episode,
                "cost": episode_cost,
                "rolling_cost": float(np.mean(rolling[-20:])),
                "loss": float(np.mean(losses)) if losses else np.nan,
                "epsilon": agent.epsilon,
                "skipped_updates": agent.skipped_updates,
            })
    return agent, curve


def model_path(model_dir: Path, name: str, seed: int) -> Path:
    return model_dir / f"{name}_seed_{seed:03d}.pth"


def curve_path(model_dir: Path, name: str, seed: int) -> Path:
    return model_dir / f"{name}_seed_{seed:03d}_training_curve.csv"


def save_agent_checkpoint(
    path: Path,
    agent: DQNAgent,
    name: str,
    seed: int,
    episodes: int,
    horizon: int,
) -> None:
    payload = {
        "format_version": 1,
        "policy": name,
        "model_seed": seed,
        "episodes": episodes,
        "horizon": horizon,
        "state_dim": 21,
        "action_dim": 3,
        "agent_config": asdict(agent.config),
        "online_state_dict": agent.online.state_dict(),
        "target_state_dict": agent.target.state_dict(),
        "optimizer_state_dict": agent.optimizer.state_dict(),
        "training_steps": agent.steps,
        "epsilon": agent.epsilon,
        "did_reset": agent.did_reset,
        "did_flush": agent.did_flush,
        "loss_ema": agent.loss_ema,
        "skipped_updates": agent.skipped_updates,
        "torch_version": torch.__version__,
    }
    torch.save(payload, path)


def load_agent_checkpoint(
    path: Path,
    name: str,
    seed: int,
    episodes: int,
    horizon: int,
    device: torch.device,
) -> DQNAgent:
    config = make_agent_config(name, episodes, horizon)
    agent = DQNAgent(21, 3, config, device, seed, episodes)
    payload = torch.load(path, map_location=device, weights_only=False)
    expected = {
        "policy": name,
        "model_seed": seed,
        "episodes": episodes,
        "horizon": horizon,
        "state_dim": 21,
        "action_dim": 3,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise ValueError(
                f"checkpoint mismatch for {path}: {key}={payload.get(key)!r}, "
                f"expected {value!r}"
            )
    if payload.get("agent_config") != asdict(config):
        raise ValueError(f"agent configuration mismatch for {path}")
    agent.online.load_state_dict(payload["online_state_dict"])
    agent.target.load_state_dict(payload["target_state_dict"])
    agent.optimizer.load_state_dict(payload["optimizer_state_dict"])
    agent.steps = int(payload["training_steps"])
    agent.epsilon = float(payload["epsilon"])
    agent.did_reset = bool(payload["did_reset"])
    agent.did_flush = bool(payload["did_flush"])
    agent.loss_ema = payload["loss_ema"]
    agent.skipped_updates = int(payload["skipped_updates"])
    return agent


def write_model_manifest(model_dir: Path) -> None:
    rows = []
    for path in sorted(model_dir.glob("*.pth")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        rows.append({
            "file": path.name,
            "sha256": digest,
            "bytes": path.stat().st_size,
            "policy": checkpoint["policy"],
            "model_seed": checkpoint["model_seed"],
            "episodes": checkpoint["episodes"],
            "horizon": checkpoint["horizon"],
            "training_steps": checkpoint["training_steps"],
        })
    pd.DataFrame(rows).to_csv(model_dir / "model_manifest.csv", index=False)


def threshold_action(state: np.ndarray, costs: np.ndarray) -> int:
    heat, energy, queue, _, bandwidth, contact = state[-6:]
    if heat > 0.72 or energy < 0.24:
        return 1 if bandwidth > 0.28 and contact > 0.18 else 2
    if bandwidth < 0.22 or contact < 0.14:
        return 0
    if queue > 0.70:
        return 2
    return int(np.argmin(costs))


def evaluate_policy(policy_name: str, agent: DQNAgent | None, model_seed: int,
                    trace_seeds: list[int], horizon: int, coupling: float,
                    scenario: str) -> list[dict]:
    rows = []
    for trace_seed in trace_seeds:
        env = SatelliteSchedulingEnv(EnvConfig(
            horizon=horizon, coupling=coupling, scenario=scenario
        ))
        state = env.reset(seed=trace_seed)
        totals = {k: 0.0 for k in [
            "total_cost", "immediate_cost", "penalty", "thermal_violation",
            "energy_violation", "queue_violation", "contact_violation"
        ]}
        actions = np.zeros(3, dtype=int)
        done = False
        while not done:
            costs = env.immediate_costs()
            if policy_name == "immediate_argmin":
                action = int(np.argmin(costs))
            elif policy_name == "fixed_onboard":
                action = 0
            elif policy_name == "fixed_ground":
                action = 1
            elif policy_name == "threshold":
                action = threshold_action(state, costs)
            else:
                assert agent is not None
                action = agent.act(state, explore=False)
            state, _, done, info = env.step(action)
            actions[action] += 1
            for key in totals:
                totals[key] += info[key]
        rows.append({
            "policy": policy_name, "model_seed": model_seed,
            "trace_seed": trace_seed, "scenario": scenario,
            "coupling": coupling, **totals,
            "onboard_fraction": actions[0] / horizon,
            "ground_fraction": actions[1] / horizon,
            "hybrid_fraction": actions[2] / horizon,
        })
    return rows


def summarize(raw: pd.DataFrame) -> pd.DataFrame:
    metrics = ["total_cost", "immediate_cost", "penalty", "thermal_violation",
               "energy_violation", "queue_violation", "contact_violation"]
    # Trace-level observations are averaged within each independently trained
    # model seed; the seed, rather than an individual task trace, is the
    # inferential unit.
    by_seed = raw.groupby(
        ["scenario", "coupling", "policy", "model_seed"], as_index=False
    )[metrics].mean()
    grouped = by_seed.groupby(["scenario", "coupling", "policy"])[metrics]
    mean = grouped.mean().add_suffix("_mean")
    sd = grouped.std(ddof=1).add_suffix("_sd")
    n = grouped.size().rename("n")
    return pd.concat([mean, sd, n], axis=1).reset_index()


def paired_comparison(raw: pd.DataFrame) -> pd.DataFrame:
    subset = raw[(raw.scenario == "nominal") & (raw.coupling == 1.0)]
    pivot = subset.pivot_table(
        index="model_seed", columns="policy",
        values="total_cost", aggfunc="mean"
    )
    if not {"md_dqn_rsf", "immediate_argmin"}.issubset(pivot.columns):
        return pd.DataFrame()
    diff = pivot["md_dqn_rsf"] - pivot["immediate_argmin"]
    n = len(diff)
    rng = np.random.default_rng(20260819)
    bootstrap = np.array([
        rng.choice(diff.to_numpy(), size=n, replace=True).mean()
        for _ in range(10_000)
    ])
    return pd.DataFrame([{
        "comparison": "md_dqn_rsf - immediate_argmin", "n_pairs": n,
        "mean_difference": diff.mean(), "sd_difference": diff.std(ddof=1),
        "ci95_low": np.quantile(bootstrap, 0.025),
        "ci95_high": np.quantile(bootstrap, 0.975),
        "relative_improvement_percent": -100 * diff.mean() / pivot["immediate_argmin"].mean(),
    }])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument(
        "--resume", action="store_true",
        help="Load matching saved models and completed seed evaluations when present.",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        args.episodes, args.horizon, args.seeds, args.test_traces = 12, 16, 1, 3
    args.output.mkdir(parents=True, exist_ok=True)
    model_dir = args.output / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"device={device}; torch={torch.__version__}; episodes={args.episodes}", flush=True)

    learned_names = ["contextual_bandit", "standard_dqn", "dqn_r", "dqn_rs", "md_dqn_rsf"]
    baseline_names = ["immediate_argmin", "fixed_onboard", "fixed_ground", "threshold"]
    partial_evaluation = args.output / "evaluation_raw.partial.csv"
    if args.resume and partial_evaluation.exists():
        all_rows = pd.read_csv(partial_evaluation).to_dict("records")
    else:
        all_rows = []
    all_curves = []
    stress_cases = [
        ("static", 0.0), ("nominal", 0.5), ("nominal", 1.0),
        ("burst", 1.0), ("link_limited", 1.0),
        ("energy_limited", 1.0), ("thermal_stress", 1.0),
    ]

    for seed in range(args.seeds):
        set_deterministic(seed)
        agents: Dict[str, DQNAgent] = {}
        for name in learned_names:
            checkpoint_path = model_path(model_dir, name, seed)
            saved_curve = curve_path(model_dir, name, seed)
            if args.resume and checkpoint_path.exists() and saved_curve.exists():
                print(f"loading {name} seed={seed} from {checkpoint_path}", flush=True)
                agent = load_agent_checkpoint(
                    checkpoint_path, name, seed, args.episodes, args.horizon, device
                )
                curve = pd.read_csv(saved_curve).to_dict("records")
            else:
                print(f"training {name} seed={seed}", flush=True)
                agent, curve = train_agent(
                    name, seed, args.episodes, args.horizon, device
                )
                save_agent_checkpoint(
                    checkpoint_path, agent, name, seed, args.episodes, args.horizon
                )
                pd.DataFrame(curve).to_csv(saved_curve, index=False)
            agents[name] = agent
            all_curves.extend(curve)
        # The 100,000-series traces were used during calibration.  Final test
        # traces use a disjoint 500,000-series namespace and are never used for
        # hyperparameter or budget selection.
        trace_seeds = [500_000 + seed * 1_000 + i for i in range(args.test_traces)]
        expected_seed_rows = len(stress_cases) * (
            len(baseline_names) + len(learned_names)
        ) * args.test_traces
        existing_seed_rows = sum(
            1 for row in all_rows if int(row["model_seed"]) == seed
        )
        if args.resume and existing_seed_rows == expected_seed_rows:
            print(f"resume skip evaluation seed={seed}", flush=True)
        else:
            all_rows = [
                row for row in all_rows if int(row["model_seed"]) != seed
            ]
            for scenario, coupling in stress_cases:
                actual_scenario = "nominal" if scenario == "static" else scenario
                for name in baseline_names:
                    all_rows.extend(evaluate_policy(
                        name, None, seed, trace_seeds, args.horizon, coupling, actual_scenario
                    ))
                for name, agent in agents.items():
                    all_rows.extend(evaluate_policy(
                        name, agent, seed, trace_seeds, args.horizon, coupling, actual_scenario
                    ))
            pd.DataFrame(all_rows).to_csv(partial_evaluation, index=False)

    raw = pd.DataFrame(all_rows)
    curves = pd.DataFrame(all_curves)
    summary = summarize(raw)
    comparison = paired_comparison(raw)
    raw.to_csv(args.output / "evaluation_raw.csv", index=False)
    curves.to_csv(args.output / "training_curves.csv", index=False)
    summary.to_csv(args.output / "summary.csv", index=False)
    comparison.to_csv(args.output / "paired_comparison.csv", index=False)
    metadata = {
        "device": str(device), "torch": torch.__version__, "numpy": np.__version__,
        "pandas": pd.__version__, "episodes": args.episodes, "horizon": args.horizon,
        "model_seeds": args.seeds, "test_traces_per_seed": args.test_traces,
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_model_manifest(model_dir)
    print(summary[(summary.scenario == "nominal") & (summary.coupling == 1.0)].to_string(index=False))
    print(comparison.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
