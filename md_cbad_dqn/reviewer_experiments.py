"""Reviewer-driven physical-consistency, planning, sensitivity, and convergence study.

This module writes to ``results/reviewer_revision`` and never overwrites the
locked confirmation artifacts used by the preceding manuscript version.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
import torch

from .agent import DQNAgent
from .environment import EnvConfig, SatelliteSchedulingEnv
from .experiment import (
    AUXILIARY_LAMBDA,
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    EPISODES,
    HORIZON,
    MODEL_SEEDS,
    SCENARIOS,
    curve_path,
    load_checkpoint,
    save_checkpoint,
    threshold_action,
    train_model,
)
from .planner import PlannerConfig, RecedingHorizonPlanner


ROOT = Path(__file__).resolve().parent
DEFAULT_RESULTS = ROOT / "results" / "reviewer_revision"
TRACE_BASE = 3_300_000
LEARNED = ("contextual_bandit", "standard_dqn", "md_cfba_dqn", "md_cbad_dqn")
POLICIES = (
    "immediate_argmin",
    "mpc_h4",
    "contextual_bandit",
    "threshold",
    "standard_dqn",
    "md_cfba_dqn",
    "md_cbad_dqn",
    "fixed_onboard",
    "fixed_ground",
)
MAIN_POLICIES = POLICIES[:7]
METRICS = (
    "total_cost",
    "immediate_cost",
    "penalty",
    "energy_use",
    "latency_ms",
    "transmitted_mbit",
    "thermal_violation",
    "energy_violation",
    "queue_violation",
    "contact_violation",
    "planning_time_ms",
    "onboard_fraction",
    "ground_fraction",
    "hybrid_fraction",
)
SENSITIVITY_PROFILES = {
    "reference": {},
    "compute_minus20": {"compute_scale": 0.8},
    "compute_plus20": {"compute_scale": 1.2},
    "data_minus20": {"data_scale": 0.8},
    "data_plus20": {"data_scale": 1.2},
    "energy_plus20": {"energy_scale": 1.2},
    "heat_plus20": {"heat_scale": 1.2},
    "link_minus20": {"link_scale": 0.8},
}


def revision_env(horizon: int, scenario: str = "nominal", coupling: float = 1.0,
                 **overrides: float) -> EnvConfig:
    return EnvConfig(
        horizon=horizon,
        scenario=scenario,
        coupling=coupling,
        generator="physics_correlated",
        **overrides,
    )


def revision_model_path(results: Path, variant: str, seed: int) -> Path:
    tag = {
        "contextual_bandit": "gamma_0",
        "standard_dqn": "standard",
        "md_cfba_dqn": "lambda_0p3_uncentered",
        "md_cbad_dqn": "lambda_0p3",
    }[variant]
    return results / "models" / f"{variant}__{tag}__seed_{seed}.pth"


def train_or_load_revision(
    results: Path,
    variant: str,
    seed: int,
    episodes: int,
    horizon: int,
    device: torch.device,
    resume: bool,
) -> DQNAgent:
    path = revision_model_path(results, variant, seed)
    if resume and path.exists():
        return load_checkpoint(
            path, variant, seed, device, episodes, horizon, AUXILIARY_LAMBDA
        )
    agent, curve = train_model(
        variant,
        seed,
        episodes,
        horizon,
        device,
        AUXILIARY_LAMBDA,
        environment_config=revision_env(horizon),
    )
    save_checkpoint(path, agent, seed, episodes, horizon)
    pd.DataFrame(curve).to_csv(curve_path(path), index=False)
    return agent


def collect_curves(results: Path) -> pd.DataFrame:
    paths = sorted((results / "models").glob("*__curve.csv"))
    if not paths:
        raise FileNotFoundError("no revision training curves found")
    curves = pd.concat((pd.read_csv(path) for path in paths), ignore_index=True)
    curves.to_csv(results / "training_curves.csv", index=False)
    return curves


def write_model_manifest(results: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for path in sorted((results / "models").glob("*.pth")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        payload = torch.load(path, map_location="cpu", weights_only=False)
        rows.append(
            {
                "file": path.name,
                "sha256": digest,
                "variant": payload["variant"],
                "model_seed": payload["model_seed"],
                "episodes": payload["episodes"],
                "horizon": payload["horizon"],
                "training_steps": payload["training_steps"],
                "bellman_target": payload["bellman_target"],
                "replay": payload["replay"],
            }
        )
    manifest = pd.DataFrame(rows)
    if len(manifest) == 0:
        raise FileNotFoundError("no revision checkpoints found")
    if not (manifest.training_steps == manifest.episodes * manifest.horizon).all():
        raise AssertionError("checkpoint interaction budget mismatch")
    manifest.to_csv(results / "model_manifest.csv", index=False)
    return manifest


def evaluate_policy(
    policy: str,
    agent: DQNAgent | None,
    model_seed: int,
    trace_seeds: list[int],
    config: EnvConfig,
    scenario_label: str,
) -> list[dict]:
    planner = RecedingHorizonPlanner(PlannerConfig(horizon=4, gamma=0.97))
    rows: list[dict] = []
    for trace_seed in trace_seeds:
        env = SatelliteSchedulingEnv(config)
        state = env.reset(seed=trace_seed)
        totals = {key: 0.0 for key in METRICS[:11]}
        actions = np.zeros(3, dtype=int)
        done = False
        while not done:
            costs = env.immediate_costs()
            planning_ms = 0.0
            if policy == "immediate_argmin":
                action = int(np.argmin(costs))
            elif policy == "mpc_h4":
                started = time.perf_counter()
                action = planner.act(env)
                planning_ms = 1000.0 * (time.perf_counter() - started)
            elif policy == "threshold":
                action = threshold_action(state, costs)
            elif policy == "fixed_onboard":
                action = 0
            elif policy == "fixed_ground":
                action = 1
            else:
                if agent is None:
                    raise ValueError(f"missing trained agent for {policy}")
                action = agent.act(state, explore=False)
            state, _, done, info = env.step(action)
            actions[action] += 1
            for key in METRICS[:10]:
                totals[key] += info[key]
            totals["planning_time_ms"] += planning_ms
        rows.append(
            {
                "policy": policy,
                "model_seed": model_seed,
                "trace_seed": trace_seed,
                "scenario": scenario_label,
                "environment_scenario": config.scenario,
                "coupling": config.coupling,
                "generator": config.generator,
                "compute_scale": config.compute_scale,
                "data_scale": config.data_scale,
                "energy_scale": config.energy_scale,
                "heat_scale": config.heat_scale,
                "link_scale": config.link_scale,
                **totals,
                "onboard_fraction": actions[0] / config.horizon,
                "ground_fraction": actions[1] / config.horizon,
                "hybrid_fraction": actions[2] / config.horizon,
            }
        )
    return rows


def seed_level(raw: pd.DataFrame, group: str = "scenario") -> pd.DataFrame:
    return raw.groupby([group, "policy", "model_seed"], as_index=False)[
        list(METRICS)
    ].mean()


def summarize(raw: pd.DataFrame, group: str = "scenario") -> pd.DataFrame:
    by_seed = seed_level(raw, group)
    grouped = by_seed.groupby([group, "policy"])[list(METRICS)]
    result = pd.concat(
        [
            grouped.mean().add_suffix("_mean"),
            grouped.std(ddof=1).add_suffix("_sd"),
            grouped.size().rename("n_model_seeds"),
        ],
        axis=1,
    ).reset_index()
    return result


def paired_bootstrap(
    raw: pd.DataFrame,
    comparisons: tuple[tuple[str, str], ...],
    group: str = "scenario",
) -> pd.DataFrame:
    by_seed = seed_level(raw, group)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    rows: list[dict] = []
    for label in dict.fromkeys(by_seed[group].tolist()):
        pivot = by_seed[by_seed[group] == label].pivot(
            index="model_seed", columns="policy", values="total_cost"
        )
        for treatment, reference in comparisons:
            difference = (pivot[treatment] - pivot[reference]).dropna().to_numpy()
            boot = rng.choice(
                difference,
                size=(BOOTSTRAP_RESAMPLES, len(difference)),
                replace=True,
            ).mean(axis=1)
            reference_mean = float(pivot[reference].mean())
            rows.append(
                {
                    group: label,
                    "comparison": f"{treatment} - {reference}",
                    "n_pairs": len(difference),
                    "mean_difference": float(difference.mean()),
                    "ci95_low": float(np.quantile(boot, 0.025)),
                    "ci95_high": float(np.quantile(boot, 0.975)),
                    "relative_improvement_percent": float(
                        -100.0 * difference.mean() / reference_mean
                    ),
                }
            )
    result = pd.DataFrame(rows)
    result["mean_better"] = result.mean_difference < 0
    result["supported"] = result.ci95_high < 0
    return result


def train_revision_models(
    results: Path,
    seeds: tuple[int, ...],
    episodes: int,
    horizon: int,
    device: torch.device,
    resume: bool,
) -> dict[tuple[str, int], DQNAgent]:
    agents: dict[tuple[str, int], DQNAgent] = {}
    for seed in seeds:
        for variant in LEARNED:
            print(f"training/loading {variant} seed={seed}", flush=True)
            agents[(variant, seed)] = train_or_load_revision(
                results, variant, seed, episodes, horizon, device, resume
            )
    collect_curves(results)
    write_model_manifest(results)
    return agents


def load_revision_models(
    results: Path,
    seeds: tuple[int, ...],
    episodes: int,
    horizon: int,
    device: torch.device,
) -> dict[tuple[str, int], DQNAgent]:
    return {
        (variant, seed): load_checkpoint(
            revision_model_path(results, variant, seed),
            variant,
            seed,
            device,
            episodes,
            horizon,
            AUXILIARY_LAMBDA,
        )
        for seed in seeds
        for variant in LEARNED
    }


def run_seven_regimes(
    results: Path,
    agents: dict[tuple[str, int], DQNAgent],
    seeds: tuple[int, ...],
    horizon: int,
    test_traces: int,
) -> pd.DataFrame:
    rows: list[dict] = []
    for seed_index, seed in enumerate(seeds):
        traces = [TRACE_BASE + seed_index * 1000 + i for i in range(test_traces)]
        for label, scenario, coupling in SCENARIOS:
            config = revision_env(horizon, scenario=scenario, coupling=coupling)
            for policy in POLICIES:
                rows.extend(
                    evaluate_policy(
                        policy, agents.get((policy, seed)), seed, traces, config, label
                    )
                )
    raw = pd.DataFrame(rows)
    raw.to_csv(results / "seven_regimes_raw.csv", index=False)
    seed_level(raw).to_csv(results / "seven_regimes_seed_level.csv", index=False)
    summarize(raw).to_csv(results / "seven_regimes_summary.csv", index=False)
    paired_bootstrap(
        raw,
        (
            ("md_cbad_dqn", "standard_dqn"),
            ("md_cbad_dqn", "md_cfba_dqn"),
            ("md_cbad_dqn", "mpc_h4"),
            ("mpc_h4", "immediate_argmin"),
        ),
    ).to_csv(results / "seven_regimes_paired_bootstrap.csv", index=False)
    return raw


def run_sensitivity(
    results: Path,
    agents: dict[tuple[str, int], DQNAgent],
    seeds: tuple[int, ...],
    horizon: int,
    test_traces: int,
) -> pd.DataFrame:
    rows: list[dict] = []
    policies = ("immediate_argmin", "mpc_h4", "standard_dqn", "md_cbad_dqn")
    for seed_index, seed in enumerate(seeds):
        traces = [TRACE_BASE + 100_000 + seed_index * 1000 + i for i in range(test_traces)]
        for profile, overrides in SENSITIVITY_PROFILES.items():
            config = revision_env(horizon, **overrides)
            for policy in policies:
                profile_rows = evaluate_policy(
                    policy, agents.get((policy, seed)), seed, traces, config, profile
                )
                for row in profile_rows:
                    row["profile"] = profile
                rows.extend(profile_rows)
    raw = pd.DataFrame(rows)
    raw.to_csv(results / "sensitivity_raw.csv", index=False)
    seed_level(raw, "profile").to_csv(
        results / "sensitivity_seed_level.csv", index=False
    )
    summarize(raw, "profile").to_csv(results / "sensitivity_summary.csv", index=False)
    paired_bootstrap(
        raw,
        (("md_cbad_dqn", "standard_dqn"), ("md_cbad_dqn", "mpc_h4")),
        "profile",
    ).to_csv(results / "sensitivity_paired_bootstrap.csv", index=False)
    return raw


def audit_parameter_generator(results: Path) -> dict:
    env = SatelliteSchedulingEnv(revision_env(20_000))
    env.reset(seed=9_117_031)
    primitive_names = (
        "raw_mbit",
        "workload_gflop",
        "result_ratio",
        "feature_ratio",
        "preprocess_fraction",
        "compute_power_w",
        "onboard_rate_gflops",
        "ground_rate_gflops",
        "reference_link_mbps",
    )
    primitives = pd.DataFrame(env.task_primitives, columns=primitive_names)
    descriptors = pd.DataFrame(
        {
            "result_mbit": env.tasks[:, 5],
            "feature_mbit": env.tasks[:, 14],
            "onboard_heat_j": env.tasks[:, 0],
            "ground_tx_heat_j": env.tasks[:, 6],
            "onboard_latency_ms": env.tasks[:, 2],
            "ground_compute_ms": env.tasks[:, 7],
        }
    )
    sample = pd.concat([primitives, descriptors], axis=1)
    sample.to_csv(results / "parameter_audit_sample.csv", index=False)
    summary = sample.agg(["min", "median", "max"]).T.reset_index()
    summary.columns = ["parameter", "minimum", "median", "maximum"]
    summary.to_csv(results / "parameter_ranges_empirical.csv", index=False)
    sample.corr(numeric_only=True).to_csv(results / "parameter_correlations.csv")
    validity = {
        "n_tasks": int(len(sample)),
        "finite": bool(np.isfinite(sample.to_numpy()).all()),
        "result_le_feature": bool((sample.result_mbit <= sample.feature_mbit).all()),
        "feature_le_raw": bool((sample.feature_mbit <= sample.raw_mbit).all()),
        "positive_primitives": bool((sample[list(primitive_names)] > 0).all().all()),
        "corr_raw_workload": float(sample.raw_mbit.corr(sample.workload_gflop)),
        "corr_workload_heat": float(
            sample.workload_gflop.corr(sample.onboard_heat_j)
        ),
        "corr_raw_ground_tx_heat": float(
            sample.raw_mbit.corr(sample.ground_tx_heat_j)
        ),
        "generator": "physics_correlated",
        "seed": 9_117_031,
    }
    if not all(
        validity[key]
        for key in ("finite", "result_le_feature", "feature_le_raw", "positive_primitives")
    ):
        raise AssertionError(f"physical validity gate failed: {validity}")
    (results / "parameter_validity.json").write_text(
        json.dumps(validity, indent=2), encoding="utf-8"
    )
    return validity


def write_metadata(
    results: Path,
    seeds: tuple[int, ...],
    episodes: int,
    horizon: int,
    test_traces: int,
) -> None:
    metadata = {
        "training_environment": asdict(revision_env(horizon)),
        "episodes": episodes,
        "horizon": horizon,
        "real_steps_per_model": episodes * horizon,
        "model_seeds": list(seeds),
        "test_traces_per_seed": test_traces,
        "planner": asdict(PlannerConfig(horizon=4, gamma=0.97)),
        "planner_forecast": "perfect next-four-task and link-state forecast",
        "sensitivity_profiles": SENSITIVITY_PROFILES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "backbone": "standard DQN; no DDQN, dueling, PER, n-step, noisy, or distributional components",
    }
    (results / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=("train", "evaluate", "sensitivity", "audit", "all")
    )
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--episodes", type=int, default=EPISODES)
    parser.add_argument("--horizon", type=int, default=HORIZON)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seeds = MODEL_SEEDS
    if args.smoke:
        args.episodes, args.horizon, args.test_traces = 12, 16, 3
        seeds = (MODEL_SEEDS[0],)
        if args.results == DEFAULT_RESULTS:
            args.results = ROOT / "results" / "reviewer_revision_smoke"
    args.results.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"stage={args.stage} device={device} results={args.results}", flush=True)
    audit_parameter_generator(args.results)
    write_metadata(args.results, seeds, args.episodes, args.horizon, args.test_traces)
    agents: dict[tuple[str, int], DQNAgent] | None = None
    if args.stage in {"train", "all"}:
        agents = train_revision_models(
            args.results,
            seeds,
            args.episodes,
            args.horizon,
            device,
            args.resume,
        )
        if args.stage == "train":
            return
    if args.stage == "audit":
        return
    if agents is None:
        agents = load_revision_models(
            args.results, seeds, args.episodes, args.horizon, device
        )
    if args.stage in {"evaluate", "all"}:
        raw = run_seven_regimes(
            args.results, agents, seeds, args.horizon, args.test_traces
        )
        expected = len(SCENARIOS) * len(POLICIES) * len(seeds) * args.test_traces
        if len(raw) != expected:
            raise AssertionError(f"expected {expected} evaluation rows, found {len(raw)}")
        if args.stage == "evaluate":
            return
    if args.stage in {"sensitivity", "all"}:
        raw = run_sensitivity(
            args.results, agents, seeds, args.horizon, args.test_traces
        )
        expected = len(SENSITIVITY_PROFILES) * 4 * len(seeds) * args.test_traces
        if len(raw) != expected:
            raise AssertionError(f"expected {expected} sensitivity rows, found {len(raw)}")


if __name__ == "__main__":
    main()
