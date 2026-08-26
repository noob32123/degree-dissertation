"""Calibrate and test Pareto-safe counterfactual ranking on pure DQN.

The network, uniform one-step replay, epsilon schedule, update cadence, and
standard DQN target are identical across variants.  Only the auxiliary
ranking loss differs.  Calibration and confirmation use disjoint model and
trace seed namespaces that were not used by the preceding CRGR experiment.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from cpsr_agent import CPSRAgentConfig, CPSRDQNAgent
from environment import EnvConfig, SatelliteSchedulingEnv
from run_crgr_study import (
    CONFIRMATORY_SCENARIOS,
    evaluate,
    seed_level,
    set_deterministic,
    summarize,
)


LAMBDA_GRID = (0.3, 1.0, 3.0)
RHO_GRID = (0.03, 0.05, 0.08)
CALIBRATION_SEED_START = 300
CONFIRMATORY_SEED_START = 400
CALIBRATION_TRACE_START = 1_300_000
CONFIRMATORY_TRACE_START = 1_500_000


def config_name(ranking_lambda: float, pareto_rho: float) -> str:
    return f"lambda_{ranking_lambda:g}__rho_{pareto_rho:g}".replace(".", "p")


def make_config(
    variant: str,
    episodes: int,
    horizon: int,
    ranking_lambda: float,
    pareto_rho: float,
) -> CPSRAgentConfig:
    if variant not in {"standard_dqn", "ungated_ranking_dqn", "md_cpsr_dqn"}:
        raise ValueError(f"unknown variant {variant}")
    return CPSRAgentConfig(
        epsilon_decay_steps=max(1_000, int(episodes * horizon * 0.35)),
        ranking_lambda=ranking_lambda if variant != "standard_dqn" else 0.0,
        use_ranking=variant != "standard_dqn",
        use_gate=variant == "md_cpsr_dqn",
        pareto_rho=pareto_rho,
    )


def train_agent(
    variant: str,
    configuration: str,
    model_seed: int,
    episodes: int,
    horizon: int,
    ranking_lambda: float,
    pareto_rho: float,
    device: torch.device,
) -> tuple[CPSRDQNAgent, list[dict]]:
    set_deterministic(model_seed)
    config = make_config(
        variant, episodes, horizon, ranking_lambda, pareto_rho
    )
    agent = CPSRDQNAgent(21, 3, config, device, model_seed)
    env = SatelliteSchedulingEnv(
        EnvConfig(horizon=horizon, coupling=1.0, scenario="nominal")
    )
    curve: list[dict] = []
    rolling: list[float] = []
    for episode in range(episodes):
        state = env.reset(seed=model_seed * 1_000_000 + episode)
        episode_cost = 0.0
        updates: list[dict[str, float]] = []
        done = False
        while not done:
            if config.use_ranking:
                preview_costs, preview_resources = env.preview_all_actions()
            else:
                preview_costs = preview_resources = None
            action = agent.act(state, explore=True)
            next_state, reward, done, info = env.step(action)
            agent.observe(
                state,
                action,
                reward,
                next_state,
                done,
                preview_costs,
                preview_resources,
            )
            update = agent.update() if agent.steps % 4 == 0 else None
            if update is not None:
                updates.append(update)
            episode_cost += info["total_cost"]
            state = next_state
        rolling.append(episode_cost)
        if episode % 10 == 0 or episode == episodes - 1:
            row = {
                key: float(np.mean([item[key] for item in updates]))
                if updates
                else np.nan
                for key in (
                    "loss",
                    "td_loss",
                    "ranking_loss",
                    "gate_mean",
                    "gate_active_fraction",
                )
            }
            curve.append(
                {
                    "variant": variant,
                    "configuration": configuration,
                    "model_seed": model_seed,
                    "episode": episode,
                    "cost": episode_cost,
                    "rolling_cost": float(np.mean(rolling[-20:])),
                    "epsilon": agent.epsilon,
                    **row,
                }
            )
    return agent, curve


def checkpoint_path(
    output: Path, stage: str, variant: str, configuration: str, seed: int
) -> Path:
    directory = output / "models" / stage
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{variant}__{configuration}__seed_{seed}.pth"


def train_or_load(
    output: Path,
    stage: str,
    variant: str,
    configuration: str,
    seed: int,
    episodes: int,
    horizon: int,
    ranking_lambda: float,
    pareto_rho: float,
    device: torch.device,
    resume: bool,
) -> tuple[CPSRDQNAgent, list[dict]]:
    path = checkpoint_path(output, stage, variant, configuration, seed)
    curve_path = path.with_name(path.stem + "__curve.csv")
    config = make_config(variant, episodes, horizon, ranking_lambda, pareto_rho)
    if resume and path.exists() and curve_path.exists():
        payload = torch.load(path, map_location=device, weights_only=False)
        expected = {
            "algorithm": "pure_dqn_cpsr",
            "variant": variant,
            "configuration": configuration,
            "model_seed": seed,
            "episodes": episodes,
            "horizon": horizon,
            "agent_config": asdict(config),
        }
        for key, value in expected.items():
            if payload.get(key) != value:
                raise ValueError(f"checkpoint mismatch {path}: {key}")
        agent = CPSRDQNAgent(21, 3, config, device, seed)
        agent.online.load_state_dict(payload["online_state_dict"])
        agent.target.load_state_dict(payload["target_state_dict"])
        agent.optimizer.load_state_dict(payload["optimizer_state_dict"])
        agent.steps = int(payload["training_steps"])
        agent.epsilon = float(payload["epsilon"])
        print(f"loaded {stage} {variant} {configuration} seed={seed}", flush=True)
        return agent, pd.read_csv(curve_path).to_dict("records")

    print(f"training {stage} {variant} {configuration} seed={seed}", flush=True)
    agent, curve = train_agent(
        variant,
        configuration,
        seed,
        episodes,
        horizon,
        ranking_lambda,
        pareto_rho,
        device,
    )
    torch.save(
        {
            "algorithm": "pure_dqn_cpsr",
            "bellman_target": "standard_target_network_max",
            "replay": "uniform_one_step",
            "network": "original_q_network",
            "variant": variant,
            "configuration": configuration,
            "model_seed": seed,
            "episodes": episodes,
            "horizon": horizon,
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
    return agent, curve


def score_candidates(data: pd.DataFrame) -> pd.DataFrame:
    standard = data[data.variant == "standard_dqn"][
        ["scenario", "coupling", "model_seed", "total_cost"]
    ].rename(columns={"total_cost": "standard_cost"})
    candidates = data[data.variant == "md_cpsr_dqn"].merge(
        standard, on=["scenario", "coupling", "model_seed"], how="inner"
    )
    candidates["paired_difference"] = (
        candidates.total_cost - candidates.standard_cost
    )
    candidates["relative_improvement_percent"] = (
        -100.0 * candidates.paired_difference / candidates.standard_cost
    )
    per_scenario = candidates.groupby(
        ["configuration", "scenario", "coupling"], as_index=False
    ).agg(
        mean_paired_difference=("paired_difference", "mean"),
        relative_improvement_percent=("relative_improvement_percent", "mean"),
        n_model_seeds=("model_seed", "nunique"),
    )
    aggregate = per_scenario.groupby("configuration", as_index=False).agg(
        worst_relative_improvement_percent=(
            "relative_improvement_percent", "min"
        ),
        all_scenarios_mean_better=(
            "mean_paired_difference", lambda x: bool((x < 0).all())
        ),
    )
    result = per_scenario.merge(aggregate, on="configuration", how="left")
    return result.sort_values(
        ["all_scenarios_mean_better", "worst_relative_improvement_percent", "configuration"],
        ascending=[False, False, True],
    )


def select_candidate(scores: pd.DataFrame, grid: list[dict], smoke: bool) -> dict:
    aggregate = scores.drop_duplicates("configuration")
    eligible = aggregate[aggregate.all_scenarios_mean_better]
    if eligible.empty and not smoke:
        best = aggregate.iloc[0]
        raise RuntimeError(
            "CPSR calibration failed the all-five mean screen; "
            f"best={best.configuration}, worst improvement="
            f"{best.worst_relative_improvement_percent:.4f}%"
        )
    selected_name = str(
        (eligible.iloc[0] if not eligible.empty else aggregate.iloc[0]).configuration
    )
    return next(item for item in grid if item["name"] == selected_name)


def paired_bootstrap(data: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(20260826)
    rows: list[dict] = []
    for scenario, coupling in CONFIRMATORY_SCENARIOS:
        subset = data[(data.scenario == scenario) & (data.coupling == coupling)]
        pivot = subset.pivot(index="model_seed", columns="variant", values="total_cost")
        for variant, reference in (
            ("ungated_ranking_dqn", "standard_dqn"),
            ("md_cpsr_dqn", "ungated_ranking_dqn"),
            ("md_cpsr_dqn", "standard_dqn"),
        ):
            diff = (pivot[variant] - pivot[reference]).dropna().to_numpy()
            boot = rng.choice(diff, size=(10_000, len(diff)), replace=True).mean(axis=1)
            rows.append(
                {
                    "scenario": scenario,
                    "comparison": f"{variant} - {reference}",
                    "n_pairs": len(diff),
                    "mean_difference": float(diff.mean()),
                    "ci95_low": float(np.quantile(boot, 0.025)),
                    "ci95_high": float(np.quantile(boot, 0.975)),
                    "relative_improvement_percent": float(
                        -100 * diff.mean() / pivot[reference].mean()
                    ),
                }
            )
    return pd.DataFrame(rows)


def run_stage(
    args,
    device: torch.device,
    stage: str,
    variants: list[tuple[str, str, float, float]],
    seed_start: int,
    seed_count: int,
    trace_start: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_path = args.output / f"{stage}_raw.partial.csv"
    raw_rows = (
        pd.read_csv(raw_path).to_dict("records")
        if args.resume and raw_path.exists()
        else []
    )
    curve_rows: list[dict] = []

    def complete(variant: str, configuration: str, seed: int) -> bool:
        if not raw_rows:
            return False
        frame = pd.DataFrame(raw_rows)
        return len(
            frame[
                (frame.variant == variant)
                & (frame.configuration == configuration)
                & (frame.model_seed == seed)
            ]
        ) == len(CONFIRMATORY_SCENARIOS) * args.test_traces

    for index in range(seed_count):
        seed = seed_start + index
        trace_seeds = [trace_start + index * 1_000 + i for i in range(args.test_traces)]
        for variant, configuration, ranking_lambda, pareto_rho in variants:
            if complete(variant, configuration, seed):
                continue
            agent, curve = train_or_load(
                args.output,
                stage,
                variant,
                configuration,
                seed,
                args.episodes,
                args.horizon,
                ranking_lambda,
                pareto_rho,
                device,
                args.resume,
            )
            curve_rows.extend(curve)
            raw_rows.extend(
                evaluate(
                    agent,
                    variant,
                    configuration,
                    seed,
                    trace_seeds,
                    args.horizon,
                    CONFIRMATORY_SCENARIOS,
                )
            )
            pd.DataFrame(raw_rows).to_csv(raw_path, index=False)
    raw = pd.DataFrame(raw_rows)
    seed_data = seed_level(raw)
    raw.to_csv(args.output / f"{stage}_raw.csv", index=False)
    seed_data.to_csv(args.output / f"{stage}_seed_level.csv", index=False)
    if curve_rows:
        pd.DataFrame(curve_rows).to_csv(
            args.output / f"{stage}_training_curves.csv", index=False
        )
    return raw, seed_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("calibration", "confirmatory", "all"), default="all")
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--calibration-seeds", type=int, default=4)
    parser.add_argument("--confirmatory-seeds", type=int, default=5)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("outputs_cpsr_study"))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        args.episodes = 12
        args.horizon = 16
        args.calibration_seeds = 1
        args.confirmatory_seeds = 1
        args.test_traces = 3
    if min(args.episodes, args.horizon, args.calibration_seeds, args.confirmatory_seeds, args.test_traces) <= 0:
        parser.error("experiment counts must be positive")

    args.output.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    grid = [
        {
            "name": config_name(ranking_lambda, pareto_rho),
            "ranking_lambda": ranking_lambda,
            "pareto_rho": pareto_rho,
        }
        for ranking_lambda in LAMBDA_GRID
        for pareto_rho in RHO_GRID
    ]
    if args.smoke:
        grid = [grid[4]]
    metadata = {
        "method": "counterfactual Pareto-safe ranking on standard DQN",
        "device": str(device),
        "episodes": args.episodes,
        "horizon": args.horizon,
        "calibration_model_seed_start": CALIBRATION_SEED_START,
        "confirmatory_model_seed_start": CONFIRMATORY_SEED_START,
        "calibration_trace_start": CALIBRATION_TRACE_START,
        "confirmatory_trace_start": CONFIRMATORY_TRACE_START,
        "invariants": {
            "target": "standard DQN target-network max (not DDQN)",
            "network": "original QNetwork",
            "replay": "uniform one-step",
            "exploration": "unchanged epsilon-greedy",
        },
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    selected_path = args.output / "selected_config.json"

    if args.stage in {"calibration", "all"}:
        calibration_variants = [("standard_dqn", "standard", 0.0, 0.05)] + [
            (
                "md_cpsr_dqn",
                item["name"],
                item["ranking_lambda"],
                item["pareto_rho"],
            )
            for item in grid
        ]
        _, calibration_seed = run_stage(
            args,
            device,
            "calibration",
            calibration_variants,
            CALIBRATION_SEED_START,
            args.calibration_seeds,
            CALIBRATION_TRACE_START,
        )
        scores = score_candidates(calibration_seed)
        scores.to_csv(args.output / "candidate_scores.csv", index=False)
        print(scores.to_string(index=False), flush=True)
        selected = select_candidate(scores, grid, args.smoke)
        selected_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")
        print(f"selected {selected}", flush=True)
    else:
        if not selected_path.exists():
            raise FileNotFoundError("confirmatory stage requires selected_config.json")
        selected = json.loads(selected_path.read_text(encoding="utf-8"))

    if args.stage in {"confirmatory", "all"}:
        # Re-read the locked file so confirmation cannot use an in-memory edit.
        selected = json.loads(selected_path.read_text(encoding="utf-8"))
        lam = float(selected["ranking_lambda"])
        rho = float(selected["pareto_rho"])
        variants = [
            ("standard_dqn", "standard", 0.0, rho),
            ("ungated_ranking_dqn", f"ungated__lambda_{lam:g}".replace(".", "p"), lam, rho),
            ("md_cpsr_dqn", selected["name"], lam, rho),
        ]
        _, confirmation_seed = run_stage(
            args,
            device,
            "confirmatory",
            variants,
            CONFIRMATORY_SEED_START,
            args.confirmatory_seeds,
            CONFIRMATORY_TRACE_START,
        )
        summarize(confirmation_seed).to_csv(
            args.output / "confirmatory_summary.csv", index=False
        )
        comparison = paired_bootstrap(confirmation_seed)
        comparison.to_csv(args.output / "confirmatory_comparison.csv", index=False)
        primary = comparison[comparison.comparison == "md_cpsr_dqn - standard_dqn"].copy()
        primary["passed"] = (primary.mean_difference < 0) & (primary.ci95_high < 0)
        success = bool(len(primary) == 5 and primary.passed.all())
        (args.output / "success_criterion.json").write_text(
            json.dumps(
                {
                    "passed": success,
                    "criterion": "negative mean and negative 95% paired-bootstrap upper bound in all five scenarios",
                    "results": primary.to_dict("records"),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(comparison.to_string(index=False), flush=True)
        print(f"all-five-scenario criterion passed={success}", flush=True)


if __name__ == "__main__":
    main()
