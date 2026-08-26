"""Fresh-seed study for counterfactual Bellman advantage distillation."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from cbad_agent import CBADAgentConfig, CBADDQNAgent
from environment import EnvConfig, SatelliteSchedulingEnv
from run_cfba_study import bootstrap, candidate_scores
from run_crgr_study import (
    CONFIRMATORY_SCENARIOS,
    evaluate,
    seed_level,
    set_deterministic,
    summarize,
)


LAMBDA_GRID = (0.1, 0.3, 1.0, 3.0)
CALIBRATION_SEED_START = 700
CONFIRMATORY_SEED_START = 800
CALIBRATION_TRACE_START = 2_100_000
CONFIRMATORY_TRACE_START = 2_300_000
TREATMENT = "md_cbad_dqn"


def make_config(enabled: bool, episodes: int, horizon: int, weight: float) -> CBADAgentConfig:
    return CBADAgentConfig(
        epsilon_decay_steps=max(1_000, int(episodes * horizon * 0.35)),
        advantage_lambda=weight if enabled else 0.0,
        use_advantage_distillation=enabled,
    )


def train(
    variant: str,
    seed: int,
    episodes: int,
    horizon: int,
    weight: float,
    device: torch.device,
) -> CBADDQNAgent:
    enabled = variant == TREATMENT
    set_deterministic(seed)
    agent = CBADDQNAgent(
        21, 3, make_config(enabled, episodes, horizon, weight), device, seed
    )
    env = SatelliteSchedulingEnv(EnvConfig(horizon=horizon, scenario="nominal"))
    for episode in range(episodes):
        state = env.reset(seed=seed * 1_000_000 + episode)
        done = False
        while not done:
            if enabled:
                preview_costs, preview_resources = env.preview_all_actions()
            else:
                preview_costs = preview_resources = None
            action = agent.act(state, explore=True)
            next_state, reward, done, _ = env.step(action)
            agent.observe(
                state, action, reward, next_state, done,
                preview_costs, preview_resources,
            )
            if agent.steps % 4 == 0:
                update = agent.update()
                if update is not None and not np.isfinite(list(update.values())).all():
                    raise FloatingPointError(f"non-finite update: {update}")
            state = next_state
    return agent


def train_or_load(
    args,
    device: torch.device,
    stage: str,
    variant: str,
    configuration: str,
    seed: int,
    weight: float,
) -> CBADDQNAgent:
    directory = args.output / "models" / stage
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{variant}__{configuration}__seed_{seed}.pth"
    enabled = variant == TREATMENT
    config = make_config(enabled, args.episodes, args.horizon, weight)
    if args.resume and path.exists():
        payload = torch.load(path, map_location=device, weights_only=False)
        expected = {
            "algorithm": "pure_dqn_cbad",
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
        agent = CBADDQNAgent(21, 3, config, device, seed)
        agent.online.load_state_dict(payload["online_state_dict"])
        agent.target.load_state_dict(payload["target_state_dict"])
        agent.optimizer.load_state_dict(payload["optimizer_state_dict"])
        agent.steps = int(payload["training_steps"])
        agent.epsilon = float(payload["epsilon"])
        print(f"loaded {stage} {variant} {configuration} seed={seed}", flush=True)
        return agent
    print(f"training {stage} {variant} {configuration} seed={seed}", flush=True)
    agent = train(
        variant, seed, args.episodes, args.horizon, weight, device
    )
    torch.save(
        {
            "algorithm": "pure_dqn_cbad",
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
    rows = pd.read_csv(partial).to_dict("records") if args.resume and partial.exists() else []

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
                args, device, stage, variant, configuration, seed, weight
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("calibration", "confirmatory", "all"), default="all")
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--calibration-seeds", type=int, default=4)
    parser.add_argument("--confirmatory-seeds", type=int, default=5)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("outputs_cbad_study"))
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
    (args.output / "metadata.json").write_text(
        json.dumps({
            "method": "counterfactual Bellman advantage distillation",
            "episodes": args.episodes,
            "horizon": args.horizon,
            "device": str(device),
            "calibration_seed_start": CALIBRATION_SEED_START,
            "confirmatory_seed_start": CONFIRMATORY_SEED_START,
            "target": "standard target-network max; not Double DQN",
            "network": "original QNetwork",
            "replay": "uniform one-step",
        }, indent=2), encoding="utf-8"
    )
    selected_path = args.output / "selected_config.json"

    if args.stage in {"calibration", "all"}:
        variants = [("standard_dqn", "standard", 0.0)] + [
            (TREATMENT, item["name"], item["weight"]) for item in grid
        ]
        data = run_stage(
            args, device, "calibration", variants,
            CALIBRATION_SEED_START, args.calibration_seeds, CALIBRATION_TRACE_START,
        )
        scores = candidate_scores(data, TREATMENT)
        scores.to_csv(args.output / "candidate_scores.csv", index=False)
        print(scores.to_string(index=False), flush=True)
        eligible = scores.drop_duplicates("configuration")
        eligible = eligible[eligible.all_five_better]
        if eligible.empty and not args.smoke:
            raise RuntimeError("CBAD failed the all-five calibration screen")
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
            (TREATMENT, selected["name"], float(selected["weight"])),
        ]
        data = run_stage(
            args, device, "confirmatory", variants,
            CONFIRMATORY_SEED_START, args.confirmatory_seeds, CONFIRMATORY_TRACE_START,
        )
        summarize(data).to_csv(args.output / "confirmatory_summary.csv", index=False)
        comparison = bootstrap(data, TREATMENT)
        comparison["passed"] = (
            (comparison.mean_difference < 0) & (comparison.ci95_high < 0)
        )
        comparison.to_csv(args.output / "confirmatory_comparison.csv", index=False)
        success = bool(len(comparison) == 5 and comparison.passed.all())
        (args.output / "success_criterion.json").write_text(
            json.dumps({"passed": success, "results": comparison.to_dict("records")}, indent=2),
            encoding="utf-8",
        )
        print(comparison.to_string(index=False), flush=True)
        print(f"all-five-scenario criterion passed={success}", flush=True)


if __name__ == "__main__":
    main()
