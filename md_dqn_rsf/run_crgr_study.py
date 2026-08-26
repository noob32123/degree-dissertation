"""Calibrate and confirm the pure-DQN MD-CRGR-DQN method.

No Double DQN, dueling network, prioritized replay, multi-step return, or
alternative exploration mechanism is used.  The only treatment is the CRGR
auxiliary loss computed from side-effect-free one-step resource previews.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import random

import numpy as np
import pandas as pd
import torch

from crgr_agent import CRGRAgentConfig, CRGRDQNAgent
from environment import EnvConfig, SatelliteSchedulingEnv
from run_experiments import evaluate_policy


CONFIRMATORY_SCENARIOS = [
    ("nominal", 1.0),
    ("burst", 1.0),
    ("link_limited", 1.0),
    ("energy_limited", 1.0),
    ("thermal_stress", 1.0),
]
ALL_SCENARIOS = [
    ("static", 0.0),
    ("nominal", 0.5),
    *CONFIRMATORY_SCENARIOS,
]
LAMBDA_GRID = (0.1, 0.3, 1.0)
TAU_GRID = (0.04, 0.06, 0.08)


def set_deterministic(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def config_name(ranking_lambda: float, gate_tau: float) -> str:
    return f"lambda_{ranking_lambda:g}__tau_{gate_tau:g}".replace(".", "p")


def make_config(
    variant: str,
    episodes: int,
    horizon: int,
    ranking_lambda: float,
    gate_tau: float,
) -> CRGRAgentConfig:
    if variant not in {"standard_dqn", "ungated_ranking_dqn", "md_crgr_dqn"}:
        raise ValueError(f"unknown variant {variant}")
    return CRGRAgentConfig(
        epsilon_decay_steps=max(1_000, int(episodes * horizon * 0.35)),
        ranking_lambda=ranking_lambda if variant != "standard_dqn" else 0.0,
        gate_tau=gate_tau,
        use_ranking=variant != "standard_dqn",
        use_gate=variant == "md_crgr_dqn",
    )


def train_agent(
    variant: str,
    configuration: str,
    model_seed: int,
    episodes: int,
    horizon: int,
    ranking_lambda: float,
    gate_tau: float,
    device: torch.device,
) -> tuple[CRGRDQNAgent, list[dict]]:
    set_deterministic(model_seed)
    config = make_config(variant, episodes, horizon, ranking_lambda, gate_tau)
    agent = CRGRDQNAgent(21, 3, config, device, model_seed)
    env = SatelliteSchedulingEnv(
        EnvConfig(horizon=horizon, coupling=1.0, scenario="nominal")
    )
    curve: list[dict] = []
    rolling: list[float] = []
    for episode in range(episodes):
        state = env.reset(seed=model_seed * 1_000_000 + episode)
        episode_cost = 0.0
        update_rows: list[dict[str, float]] = []
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
                update_rows.append(update)
            episode_cost += info["total_cost"]
            state = next_state
        rolling.append(episode_cost)
        if episode % 10 == 0 or episode == episodes - 1:
            aggregate = {
                key: float(np.mean([row[key] for row in update_rows]))
                if update_rows
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
                    **aggregate,
                }
            )
    return agent, curve


def checkpoint_path(
    model_root: Path,
    stage: str,
    variant: str,
    configuration: str,
    model_seed: int,
) -> Path:
    directory = model_root / stage
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{variant}__{configuration}__seed_{model_seed:03d}.pth"


def curve_path(checkpoint: Path) -> Path:
    return checkpoint.with_name(checkpoint.stem + "__training_curve.csv")


def save_checkpoint(
    path: Path,
    agent: CRGRDQNAgent,
    variant: str,
    configuration: str,
    model_seed: int,
    episodes: int,
    horizon: int,
) -> None:
    torch.save(
        {
            "format_version": 1,
            "algorithm_family": "pure_dqn_crgr",
            "bellman_target": "target_network_max",
            "replay": "uniform_one_step",
            "network": "original_q_network",
            "variant": variant,
            "configuration": configuration,
            "model_seed": model_seed,
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
            "torch_version": torch.__version__,
        },
        path,
    )


def load_checkpoint(
    path: Path,
    variant: str,
    configuration: str,
    model_seed: int,
    episodes: int,
    horizon: int,
    ranking_lambda: float,
    gate_tau: float,
    device: torch.device,
) -> CRGRDQNAgent:
    config = make_config(variant, episodes, horizon, ranking_lambda, gate_tau)
    agent = CRGRDQNAgent(21, 3, config, device, model_seed)
    payload = torch.load(path, map_location=device, weights_only=False)
    expected = {
        "algorithm_family": "pure_dqn_crgr",
        "bellman_target": "target_network_max",
        "replay": "uniform_one_step",
        "network": "original_q_network",
        "variant": variant,
        "configuration": configuration,
        "model_seed": model_seed,
        "episodes": episodes,
        "horizon": horizon,
        "state_dim": 21,
        "action_dim": 3,
        "agent_config": asdict(config),
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise ValueError(
                f"checkpoint mismatch for {path}: {key}={payload.get(key)!r}, "
                f"expected {value!r}"
            )
    agent.online.load_state_dict(payload["online_state_dict"])
    agent.target.load_state_dict(payload["target_state_dict"])
    agent.optimizer.load_state_dict(payload["optimizer_state_dict"])
    agent.steps = int(payload["training_steps"])
    agent.epsilon = float(payload["epsilon"])
    return agent


def train_or_load(
    model_root: Path,
    stage: str,
    variant: str,
    configuration: str,
    model_seed: int,
    episodes: int,
    horizon: int,
    ranking_lambda: float,
    gate_tau: float,
    device: torch.device,
    resume: bool,
) -> tuple[CRGRDQNAgent, list[dict]]:
    checkpoint = checkpoint_path(
        model_root, stage, variant, configuration, model_seed
    )
    saved_curve = curve_path(checkpoint)
    if resume and checkpoint.exists() and saved_curve.exists():
        print(f"loading {stage} {variant} {configuration} seed={model_seed}", flush=True)
        return (
            load_checkpoint(
                checkpoint,
                variant,
                configuration,
                model_seed,
                episodes,
                horizon,
                ranking_lambda,
                gate_tau,
                device,
            ),
            pd.read_csv(saved_curve).to_dict("records"),
        )
    print(f"training {stage} {variant} {configuration} seed={model_seed}", flush=True)
    agent, curve = train_agent(
        variant,
        configuration,
        model_seed,
        episodes,
        horizon,
        ranking_lambda,
        gate_tau,
        device,
    )
    save_checkpoint(
        checkpoint,
        agent,
        variant,
        configuration,
        model_seed,
        episodes,
        horizon,
    )
    pd.DataFrame(curve).to_csv(saved_curve, index=False)
    return agent, curve


def evaluate(
    agent: CRGRDQNAgent,
    variant: str,
    configuration: str,
    model_seed: int,
    trace_seeds: list[int],
    horizon: int,
    scenarios: list[tuple[str, float]],
) -> list[dict]:
    rows: list[dict] = []
    for scenario, coupling in scenarios:
        actual_scenario = "nominal" if scenario == "static" else scenario
        result = evaluate_policy(
            variant,
            agent,
            model_seed,
            trace_seeds,
            horizon,
            coupling,
            actual_scenario,
        )
        for row in result:
            row["variant"] = row.pop("policy")
            row["configuration"] = configuration
            if scenario == "static":
                row["scenario"] = "static"
        rows.extend(result)
    return rows


def seed_level(raw: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "total_cost",
        "immediate_cost",
        "penalty",
        "thermal_violation",
        "energy_violation",
        "queue_violation",
        "contact_violation",
        "onboard_fraction",
        "ground_fraction",
        "hybrid_fraction",
    ]
    return raw.groupby(
        ["scenario", "coupling", "variant", "configuration", "model_seed"],
        as_index=False,
    )[metrics].mean()


def summarize(seed_data: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "total_cost",
        "immediate_cost",
        "penalty",
        "thermal_violation",
        "energy_violation",
        "queue_violation",
        "contact_violation",
    ]
    grouped = seed_data.groupby(
        ["scenario", "coupling", "variant", "configuration"]
    )[metrics]
    mean = grouped.mean().add_suffix("_mean")
    sd = grouped.std(ddof=1).add_suffix("_sd")
    n = grouped.size().rename("n_model_seeds")
    return pd.concat([mean, sd, n], axis=1).reset_index()


def score_candidates(calibration_seed: pd.DataFrame) -> pd.DataFrame:
    standard = calibration_seed[calibration_seed.variant == "standard_dqn"][[
        "scenario",
        "coupling",
        "model_seed",
        "total_cost",
    ]].rename(columns={"total_cost": "standard_cost"})
    candidates = calibration_seed[
        calibration_seed.variant == "md_crgr_dqn"
    ].merge(standard, on=["scenario", "coupling", "model_seed"], how="inner")
    candidates["paired_difference"] = (
        candidates.total_cost - candidates.standard_cost
    )
    candidates["relative_improvement_percent"] = (
        -100 * candidates.paired_difference / candidates.standard_cost
    )
    by_scenario = candidates.groupby(
        ["configuration", "scenario", "coupling"], as_index=False
    ).agg(
        mean_paired_difference=("paired_difference", "mean"),
        sd_paired_difference=("paired_difference", lambda x: x.std(ddof=1)),
        relative_improvement_percent=("relative_improvement_percent", "mean"),
        n_model_seeds=("model_seed", "nunique"),
    )
    aggregate = by_scenario.groupby("configuration", as_index=False).agg(
        worst_relative_improvement_percent=("relative_improvement_percent", "min"),
        all_scenarios_mean_better=("mean_paired_difference", lambda x: bool((x < 0).all())),
    )
    nominal = by_scenario[
        (by_scenario.scenario == "nominal") & (by_scenario.coupling == 1.0)
    ][["configuration", "relative_improvement_percent"]].rename(
        columns={
            "relative_improvement_percent": "nominal_relative_improvement_percent"
        }
    )
    aggregate = aggregate.merge(nominal, on="configuration", how="left")
    result = by_scenario.merge(aggregate, on="configuration", how="left")
    return result.sort_values(
        [
            "all_scenarios_mean_better",
            "worst_relative_improvement_percent",
            "configuration",
        ],
        ascending=[False, False, True],
    )


def selected_candidate(
    scores: pd.DataFrame, grid: list[dict], require_eligible: bool = True
) -> dict:
    aggregate = scores.drop_duplicates("configuration")
    eligible = aggregate[aggregate.all_scenarios_mean_better]
    if eligible.empty and require_eligible:
        best = aggregate.iloc[0]
        raise RuntimeError(
            "no calibration configuration improved mean cost in all five scenarios; "
            f"best was {best.configuration} with worst improvement "
            f"{best.worst_relative_improvement_percent:.4f}%"
        )
    selected_name = str(
        (eligible.iloc[0] if not eligible.empty else aggregate.iloc[0]).configuration
    )
    return next(item for item in grid if item["name"] == selected_name)


def paired_bootstrap(seed_data: pd.DataFrame, bootstrap_seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(bootstrap_seed)
    rows: list[dict] = []
    for scenario, coupling in CONFIRMATORY_SCENARIOS:
        subset = seed_data[
            (seed_data.scenario == scenario) & (seed_data.coupling == coupling)
        ]
        pivot = subset.pivot(index="model_seed", columns="variant", values="total_cost")
        for variant, reference in (
            ("ungated_ranking_dqn", "standard_dqn"),
            ("md_crgr_dqn", "ungated_ranking_dqn"),
            ("md_crgr_dqn", "standard_dqn"),
        ):
            diff = (pivot[variant] - pivot[reference]).dropna().to_numpy()
            boot = np.asarray(
                [rng.choice(diff, size=len(diff), replace=True).mean() for _ in range(10_000)]
            )
            rows.append(
                {
                    "scenario": scenario,
                    "coupling": coupling,
                    "comparison": f"{variant} - {reference}",
                    "n_pairs": len(diff),
                    "mean_difference": float(diff.mean()),
                    "sd_difference": float(diff.std(ddof=1)),
                    "ci95_low": float(np.quantile(boot, 0.025)),
                    "ci95_high": float(np.quantile(boot, 0.975)),
                    "relative_improvement_percent": float(
                        -100 * diff.mean() / pivot[reference].mean()
                    ),
                }
            )
    return pd.DataFrame(rows)


def write_manifest(model_root: Path) -> None:
    rows = []
    for path in sorted(model_root.rglob("*.pth")):
        payload = torch.load(path, map_location="cpu", weights_only=False)
        rows.append(
            {
                "file": str(path.relative_to(model_root)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
                "variant": payload["variant"],
                "configuration": payload["configuration"],
                "model_seed": payload["model_seed"],
                "episodes": payload["episodes"],
                "horizon": payload["horizon"],
                "training_steps": payload["training_steps"],
                "bellman_target": payload["bellman_target"],
                "replay": payload["replay"],
                "network": payload["network"],
            }
        )
    pd.DataFrame(rows).to_csv(model_root / "model_manifest.csv", index=False)


def run_calibration(args, device: torch.device, grid: list[dict]) -> dict:
    model_root = args.output / "models"
    raw_rows: list[dict] = []
    curve_rows: list[dict] = []
    partial = args.output / "calibration_raw.partial.csv"
    if args.resume and partial.exists():
        raw_rows = pd.read_csv(partial).to_dict("records")

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

    for index in range(args.calibration_seeds):
        seed = 100 + index
        trace_seeds = [1_100_000 + index * 1_000 + i for i in range(args.test_traces)]
        if not complete("standard_dqn", "standard", seed):
            agent, curve = train_or_load(
                model_root,
                "calibration",
                "standard_dqn",
                "standard",
                seed,
                args.episodes,
                args.horizon,
                0.0,
                0.06,
                device,
                args.resume,
            )
            curve_rows.extend(curve)
            raw_rows.extend(
                evaluate(
                    agent,
                    "standard_dqn",
                    "standard",
                    seed,
                    trace_seeds,
                    args.horizon,
                    CONFIRMATORY_SCENARIOS,
                )
            )
            pd.DataFrame(raw_rows).to_csv(partial, index=False)
        for item in grid:
            if complete("md_crgr_dqn", item["name"], seed):
                continue
            agent, curve = train_or_load(
                model_root,
                "calibration",
                "md_crgr_dqn",
                item["name"],
                seed,
                args.episodes,
                args.horizon,
                item["ranking_lambda"],
                item["gate_tau"],
                device,
                args.resume,
            )
            curve_rows.extend(curve)
            raw_rows.extend(
                evaluate(
                    agent,
                    "md_crgr_dqn",
                    item["name"],
                    seed,
                    trace_seeds,
                    args.horizon,
                    CONFIRMATORY_SCENARIOS,
                )
            )
            pd.DataFrame(raw_rows).to_csv(partial, index=False)

    raw = pd.DataFrame(raw_rows)
    seed_data = seed_level(raw)
    scores = score_candidates(seed_data)
    selected = selected_candidate(scores, grid, require_eligible=not args.smoke)
    locked = {
        "selection_endpoint": (
            "maximize worst scenario seed-level paired relative improvement vs standard_dqn; "
            "all five scenario means must improve"
        ),
        "selected": selected,
        "candidate_grid": grid,
        "calibration_model_seeds": [100 + i for i in range(args.calibration_seeds)],
        "calibration_trace_namespace": "1100000 + seed_index*1000 + trace_index",
        "confirmatory_model_seeds": [i for i in range(args.confirmatory_seeds)],
        "confirmatory_trace_namespace": "500000 + model_seed*1000 + trace_index",
    }
    canonical = json.dumps(locked, sort_keys=True, separators=(",", ":"))
    locked["lock_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    raw.to_csv(args.output / "calibration_raw.csv", index=False)
    seed_data.to_csv(args.output / "calibration_seed_level.csv", index=False)
    scores.to_csv(args.output / "candidate_scores.csv", index=False)
    if curve_rows:
        pd.DataFrame(curve_rows).to_csv(
            args.output / "calibration_training_curves.csv", index=False
        )
    (args.output / "selected_config.json").write_text(
        json.dumps(locked, indent=2), encoding="utf-8"
    )
    print(scores.to_string(index=False), flush=True)
    print(f"locked configuration={selected['name']}", flush=True)
    return locked


def load_locked_config(path: Path) -> dict:
    locked = json.loads(path.read_text(encoding="utf-8"))
    digest = locked.pop("lock_sha256")
    canonical = json.dumps(locked, sort_keys=True, separators=(",", ":"))
    actual = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if actual != digest:
        raise ValueError(f"selected configuration hash mismatch: {actual} != {digest}")
    locked["lock_sha256"] = digest
    return locked


def run_confirmatory(args, device: torch.device, locked: dict) -> None:
    selected = locked["selected"]
    model_root = args.output / "models"
    raw_rows: list[dict] = []
    curve_rows: list[dict] = []
    partial = args.output / "confirmatory_raw.partial.csv"
    if args.resume and partial.exists():
        raw_rows = pd.read_csv(partial).to_dict("records")

    def complete(variant: str, seed: int) -> bool:
        if not raw_rows:
            return False
        frame = pd.DataFrame(raw_rows)
        return len(
            frame[(frame.variant == variant) & (frame.model_seed == seed)]
        ) == len(ALL_SCENARIOS) * args.test_traces

    variants = [
        ("standard_dqn", "standard", 0.0, selected["gate_tau"]),
        (
            "ungated_ranking_dqn",
            f"ungated__lambda_{selected['ranking_lambda']:g}".replace(".", "p"),
            selected["ranking_lambda"],
            selected["gate_tau"],
        ),
        (
            "md_crgr_dqn",
            selected["name"],
            selected["ranking_lambda"],
            selected["gate_tau"],
        ),
    ]
    for seed in range(args.confirmatory_seeds):
        trace_seeds = [500_000 + seed * 1_000 + i for i in range(args.test_traces)]
        for variant, configuration, ranking_lambda, gate_tau in variants:
            if complete(variant, seed):
                continue
            agent, curve = train_or_load(
                model_root,
                "confirmatory",
                variant,
                configuration,
                seed,
                args.episodes,
                args.horizon,
                ranking_lambda,
                gate_tau,
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
                    ALL_SCENARIOS,
                )
            )
            pd.DataFrame(raw_rows).to_csv(partial, index=False)

    raw = pd.DataFrame(raw_rows)
    seed_data = seed_level(raw)
    summary = summarize(seed_data)
    comparison = paired_bootstrap(seed_data, bootstrap_seed=20260825)
    primary = comparison[
        comparison.comparison == "md_crgr_dqn - standard_dqn"
    ].copy()
    primary["passed"] = (
        (primary.mean_difference < 0) & (primary.ci95_high < 0)
    )
    success = {
        "criterion": (
            "mean_difference < 0 and paired percentile-bootstrap ci95_high < 0 "
            "for all five prespecified full-coupling scenarios"
        ),
        "passed": bool(len(primary) == 5 and primary.passed.all()),
        "scenario_results": primary.to_dict("records"),
        "bootstrap_seed": 20260825,
        "bootstrap_resamples": 10_000,
    }
    raw.to_csv(args.output / "confirmatory_raw.csv", index=False)
    seed_data.to_csv(args.output / "confirmatory_seed_level.csv", index=False)
    summary.to_csv(args.output / "confirmatory_summary.csv", index=False)
    comparison.to_csv(args.output / "confirmatory_comparison.csv", index=False)
    if curve_rows:
        pd.DataFrame(curve_rows).to_csv(
            args.output / "confirmatory_training_curves.csv", index=False
        )
    (args.output / "success_criterion.json").write_text(
        json.dumps(success, indent=2), encoding="utf-8"
    )
    print(summary.to_string(index=False), flush=True)
    print(comparison.to_string(index=False), flush=True)
    print(f"all-five-scenario criterion passed={success['passed']}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["calibration", "confirmatory", "all"], default="all")
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--calibration-seeds", type=int, default=4)
    parser.add_argument("--confirmatory-seeds", type=int, default=5)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("outputs_crgr_confirmatory"))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        args.episodes = 12
        args.horizon = 16
        args.calibration_seeds = 1
        args.confirmatory_seeds = 1
        args.test_traces = 3
    if min(
        args.episodes,
        args.horizon,
        args.calibration_seeds,
        args.confirmatory_seeds,
        args.test_traces,
    ) <= 0:
        parser.error("all experiment counts must be positive")

    args.output.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    grid = [
        {
            "name": config_name(ranking_lambda, gate_tau),
            "ranking_lambda": ranking_lambda,
            "gate_tau": gate_tau,
        }
        for ranking_lambda in LAMBDA_GRID
        for gate_tau in TAU_GRID
    ]
    if args.smoke:
        grid = [grid[4]]
    metadata = {
        "device": str(device),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "episodes": args.episodes,
        "horizon": args.horizon,
        "calibration_model_seeds": args.calibration_seeds,
        "confirmatory_model_seeds": args.confirmatory_seeds,
        "test_traces_per_seed": args.test_traces,
        "algorithm_invariants": {
            "bellman_target": "standard DQN target-network max; not Double DQN",
            "network": "original QNetwork",
            "replay": "uniform one-step replay",
            "exploration": "original epsilon-greedy schedule",
        },
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(
        f"device={device}; stage={args.stage}; episodes={args.episodes}; "
        f"grid={len(grid)}",
        flush=True,
    )

    locked_path = args.output / "selected_config.json"
    if args.stage in {"calibration", "all"}:
        locked = run_calibration(args, device, grid)
    else:
        if not locked_path.exists():
            raise FileNotFoundError(
                "confirmatory stage requires a locked selected_config.json"
            )
        locked = load_locked_config(locked_path)
    if args.stage in {"confirmatory", "all"}:
        locked = load_locked_config(locked_path)
        run_confirmatory(args, device, locked)
    write_manifest(args.output / "models")


if __name__ == "__main__":
    main()
