"""Independent calibration and confirmation for pure-DQN MD-CFBA-DQN."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from cfba_agent import CFBAAgentConfig, CFBADQNAgent
from environment import EnvConfig, SatelliteSchedulingEnv
from run_crgr_study import (
    CONFIRMATORY_SCENARIOS,
    evaluate,
    seed_level,
    set_deterministic,
    summarize,
)


LAMBDA_GRID = (0.1, 0.3, 1.0, 3.0)
CALIBRATION_SEED_START = 500
CONFIRMATORY_SEED_START = 600
CALIBRATION_TRACE_START = 1_700_000
CONFIRMATORY_TRACE_START = 1_900_000


def make_config(enabled: bool, episodes: int, horizon: int, weight: float) -> CFBAAgentConfig:
    return CFBAAgentConfig(
        epsilon_decay_steps=max(1_000, int(episodes * horizon * 0.35)),
        counterfactual_lambda=weight if enabled else 0.0,
        use_counterfactual=enabled,
    )


def train(
    variant: str,
    configuration: str,
    seed: int,
    episodes: int,
    horizon: int,
    weight: float,
    device: torch.device,
) -> tuple[CFBADQNAgent, list[dict]]:
    enabled = variant == "md_cfba_dqn"
    set_deterministic(seed)
    config = make_config(enabled, episodes, horizon, weight)
    agent = CFBADQNAgent(21, 3, config, device, seed)
    env = SatelliteSchedulingEnv(EnvConfig(horizon=horizon, scenario="nominal"))
    curve: list[dict] = []
    rolling: list[float] = []
    for episode in range(episodes):
        state = env.reset(seed=seed * 1_000_000 + episode)
        total = 0.0
        updates: list[dict[str, float]] = []
        done = False
        while not done:
            if enabled:
                preview_costs, preview_resources = env.preview_all_actions()
            else:
                preview_costs = preview_resources = None
            action = agent.act(state, explore=True)
            next_state, reward, done, info = env.step(action)
            agent.observe(
                state, action, reward, next_state, done,
                preview_costs, preview_resources,
            )
            update = agent.update() if agent.steps % 4 == 0 else None
            if update is not None:
                updates.append(update)
            total += info["total_cost"]
            state = next_state
        rolling.append(total)
        if episode % 10 == 0 or episode == episodes - 1:
            curve.append(
                {
                    "variant": variant,
                    "configuration": configuration,
                    "model_seed": seed,
                    "episode": episode,
                    "cost": total,
                    "rolling_cost": float(np.mean(rolling[-20:])),
                    "epsilon": agent.epsilon,
                    **{
                        key: float(np.mean([row[key] for row in updates]))
                        if updates else np.nan
                        for key in ("loss", "td_loss", "counterfactual_loss")
                    },
                }
            )
    return agent, curve


def train_or_load(
    args,
    stage: str,
    variant: str,
    configuration: str,
    seed: int,
    weight: float,
    device: torch.device,
) -> CFBADQNAgent:
    directory = args.output / "models" / stage
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{variant}__{configuration}__seed_{seed}.pth"
    curve_path = path.with_name(path.stem + "__curve.csv")
    enabled = variant == "md_cfba_dqn"
    config = make_config(enabled, args.episodes, args.horizon, weight)
    if args.resume and path.exists() and curve_path.exists():
        payload = torch.load(path, map_location=device, weights_only=False)
        expected = {
            "algorithm": "pure_dqn_cfba",
            "variant": variant,
            "configuration": configuration,
            "model_seed": seed,
            "episodes": args.episodes,
            "horizon": args.horizon,
            "agent_config": asdict(config),
        }
        for key, value in expected.items():
            if payload.get(key) != value:
                raise ValueError(f"checkpoint mismatch {path}: {key}")
        agent = CFBADQNAgent(21, 3, config, device, seed)
        agent.online.load_state_dict(payload["online_state_dict"])
        agent.target.load_state_dict(payload["target_state_dict"])
        agent.optimizer.load_state_dict(payload["optimizer_state_dict"])
        agent.steps = int(payload["training_steps"])
        agent.epsilon = float(payload["epsilon"])
        print(f"loaded {stage} {variant} {configuration} seed={seed}", flush=True)
        return agent
    print(f"training {stage} {variant} {configuration} seed={seed}", flush=True)
    agent, curve = train(
        variant, configuration, seed, args.episodes, args.horizon, weight, device
    )
    torch.save(
        {
            "algorithm": "pure_dqn_cfba",
            "bellman_target": "standard_target_network_max",
            "replay": "uniform_one_step",
            "network": "original_q_network",
            "variant": variant,
            "configuration": configuration,
            "model_seed": seed,
            "episodes": args.episodes,
            "horizon": args.horizon,
            "agent_config": asdict(agent.config),
            "online_state_dict": agent.online.state_dict(),
            "target_state_dict": agent.target.state_dict(),
            "optimizer_state_dict": agent.optimizer.state_dict(),
            "training_steps": agent.steps,
            "epsilon": agent.epsilon,
        },
        path,
    )
    pd.DataFrame(curve).to_csv(curve_path, index=False)
    return agent


def run_stage(
    args,
    device: torch.device,
    stage: str,
    variants: list[tuple[str, str, float]],
    seed_start: int,
    seed_count: int,
    trace_start: int,
) -> pd.DataFrame:
    partial = args.output / f"{stage}_raw.partial.csv"
    rows = (
        pd.read_csv(partial).to_dict("records")
        if args.resume and partial.exists() else []
    )

    def complete(variant: str, configuration: str, seed: int) -> bool:
        if not rows:
            return False
        frame = pd.DataFrame(rows)
        return len(frame[
            (frame.variant == variant)
            & (frame.configuration == configuration)
            & (frame.model_seed == seed)
        ]) == len(CONFIRMATORY_SCENARIOS) * args.test_traces

    for index in range(seed_count):
        seed = seed_start + index
        traces = [trace_start + index * 1_000 + i for i in range(args.test_traces)]
        for variant, configuration, weight in variants:
            if complete(variant, configuration, seed):
                continue
            agent = train_or_load(
                args, stage, variant, configuration, seed, weight, device
            )
            rows.extend(evaluate(
                agent, variant, configuration, seed, traces,
                args.horizon, CONFIRMATORY_SCENARIOS,
            ))
            pd.DataFrame(rows).to_csv(partial, index=False)
    raw = pd.DataFrame(rows)
    seeds = seed_level(raw)
    raw.to_csv(args.output / f"{stage}_raw.csv", index=False)
    seeds.to_csv(args.output / f"{stage}_seed_level.csv", index=False)
    return seeds


def candidate_scores(
    data: pd.DataFrame, treatment: str = "md_cfba_dqn"
) -> pd.DataFrame:
    baseline = data[data.variant == "standard_dqn"][
        ["scenario", "coupling", "model_seed", "total_cost"]
    ].rename(columns={"total_cost": "baseline"})
    joined = data[data.variant == treatment].merge(
        baseline, on=["scenario", "coupling", "model_seed"]
    )
    joined["difference"] = joined.total_cost - joined.baseline
    joined["improvement_percent"] = -100 * joined.difference / joined.baseline
    by_scenario = joined.groupby(
        ["configuration", "scenario", "coupling"], as_index=False
    ).agg(
        mean_difference=("difference", "mean"),
        improvement_percent=("improvement_percent", "mean"),
    )
    overall = by_scenario.groupby("configuration", as_index=False).agg(
        all_five_better=("mean_difference", lambda x: bool((x < 0).all())),
        worst_improvement_percent=("improvement_percent", "min"),
    )
    return by_scenario.merge(overall, on="configuration").sort_values(
        ["all_five_better", "worst_improvement_percent", "configuration"],
        ascending=[False, False, True],
    )


def bootstrap(data: pd.DataFrame, treatment: str = "md_cfba_dqn") -> pd.DataFrame:
    rng = np.random.default_rng(20260827)
    rows = []
    for scenario, _ in CONFIRMATORY_SCENARIOS:
        pivot = data[data.scenario == scenario].pivot(
            index="model_seed", columns="variant", values="total_cost"
        )
        diff = (pivot[treatment] - pivot.standard_dqn).dropna().to_numpy()
        boot = rng.choice(diff, size=(10_000, len(diff)), replace=True).mean(axis=1)
        rows.append({
            "scenario": scenario,
            "n_pairs": len(diff),
            "mean_difference": float(diff.mean()),
            "ci95_low": float(np.quantile(boot, 0.025)),
            "ci95_high": float(np.quantile(boot, 0.975)),
            "relative_improvement_percent": float(
                -100 * diff.mean() / pivot.standard_dqn.mean()
            ),
        })
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("calibration", "confirmatory", "all"), default="all")
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--calibration-seeds", type=int, default=4)
    parser.add_argument("--confirmatory-seeds", type=int, default=5)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("outputs_cfba_study"))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        args.episodes, args.horizon = 12, 16
        args.calibration_seeds = args.confirmatory_seeds = 1
        args.test_traces = 3
    args.output.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    grid = [
        {"name": f"lambda_{weight:g}".replace(".", "p"), "weight": weight}
        for weight in LAMBDA_GRID
    ]
    if args.smoke:
        grid = [grid[1]]
    metadata = {
        "method": "full-action counterfactual Bellman augmentation",
        "device": str(device),
        "episodes": args.episodes,
        "horizon": args.horizon,
        "calibration_model_seeds": [CALIBRATION_SEED_START + i for i in range(args.calibration_seeds)],
        "confirmatory_model_seeds": [CONFIRMATORY_SEED_START + i for i in range(args.confirmatory_seeds)],
        "target": "standard DQN target-network max for factual and auxiliary targets; not DDQN",
        "network": "original QNetwork",
        "replay": "uniform one-step",
    }
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    selected_path = args.output / "selected_config.json"

    if args.stage in {"calibration", "all"}:
        variants = [("standard_dqn", "standard", 0.0)] + [
            ("md_cfba_dqn", item["name"], item["weight"]) for item in grid
        ]
        data = run_stage(
            args, device, "calibration", variants,
            CALIBRATION_SEED_START, args.calibration_seeds, CALIBRATION_TRACE_START,
        )
        scores = candidate_scores(data)
        scores.to_csv(args.output / "candidate_scores.csv", index=False)
        print(scores.to_string(index=False), flush=True)
        eligible = scores.drop_duplicates("configuration")
        eligible = eligible[eligible.all_five_better]
        if eligible.empty and not args.smoke:
            raise RuntimeError("CFBA failed the all-five calibration screen")
        name = str((eligible.iloc[0] if not eligible.empty else scores.iloc[0]).configuration)
        selected = next(item for item in grid if item["name"] == name)
        selected_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")
        print(f"selected {selected}", flush=True)
    else:
        selected = json.loads(selected_path.read_text(encoding="utf-8"))

    if args.stage in {"confirmatory", "all"}:
        selected = json.loads(selected_path.read_text(encoding="utf-8"))
        variants = [
            ("standard_dqn", "standard", 0.0),
            ("md_cfba_dqn", selected["name"], float(selected["weight"])),
        ]
        data = run_stage(
            args, device, "confirmatory", variants,
            CONFIRMATORY_SEED_START, args.confirmatory_seeds, CONFIRMATORY_TRACE_START,
        )
        summarize(data).to_csv(args.output / "confirmatory_summary.csv", index=False)
        comparison = bootstrap(data)
        comparison.to_csv(args.output / "confirmatory_comparison.csv", index=False)
        comparison["passed"] = (
            (comparison.mean_difference < 0) & (comparison.ci95_high < 0)
        )
        success = bool(len(comparison) == 5 and comparison.passed.all())
        (args.output / "success_criterion.json").write_text(
            json.dumps({"passed": success, "results": comparison.to_dict("records")}, indent=2),
            encoding="utf-8",
        )
        print(comparison.to_string(index=False), flush=True)
        print(f"all-five-scenario criterion passed={success}", flush=True)


if __name__ == "__main__":
    main()
