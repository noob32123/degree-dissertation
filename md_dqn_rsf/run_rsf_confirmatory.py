"""Two-stage, leakage-resistant RSF ablation study.

Stage 1 uses calibration-only model seeds and traces to select one full RSF
configuration from a prespecified candidate set. Stage 2 locks that
configuration and evaluates Standard, R, R+S, and R+S+F on fresh model seeds
and fresh traces. Candidate-wise calibration results are tuning data and must
not be reported as confirmatory evidence.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random

import numpy as np
import pandas as pd
import torch

from agent import AgentConfig, DQNAgent
from environment import EnvConfig, SatelliteSchedulingEnv


@dataclass(frozen=True)
class RSFStudyConfig:
    name: str
    reset_fraction: float
    reset_epsilon: float
    selective_factor: float
    flush_fraction: float


# Prespecified before the new confirmatory traces are generated. The original
# manuscript setting is retained as candidate c0.
CANDIDATES = [
    RSFStudyConfig("c0_original", 0.45, 0.65, 1.8, 0.72),
    RSFStudyConfig("c1_late_gentle", 0.55, 0.35, 3.0, 0.90),
    RSFStudyConfig("c2_late_moderate", 0.55, 0.50, 2.5, 0.85),
    RSFStudyConfig("c3_mid_moderate", 0.45, 0.50, 2.5, 0.85),
    RSFStudyConfig("c4_early_moderate", 0.35, 0.50, 2.5, 0.85),
    RSFStudyConfig("c5_early_explore", 0.35, 0.65, 2.5, 0.85),
]


def set_deterministic(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_agent_config(
    variant: str,
    rsf: RSFStudyConfig,
    episodes: int,
    horizon: int,
) -> AgentConfig:
    flags = {
        "standard_dqn": {},
        "dqn_r": {"use_reset": True},
        "dqn_rs": {"use_reset": True, "use_selective": True},
        "md_dqn_rsf": {
            "use_reset": True,
            "use_selective": True,
            "use_flush": True,
        },
    }[variant]
    return AgentConfig(
        steps_per_episode=horizon,
        epsilon_decay_steps=max(1_000, int(episodes * horizon * 0.35)),
        reset_fraction=rsf.reset_fraction,
        reset_epsilon=rsf.reset_epsilon,
        selective_factor=rsf.selective_factor,
        flush_fraction=rsf.flush_fraction,
        **flags,
    )


def train_variant(
    variant: str,
    rsf: RSFStudyConfig,
    model_seed: int,
    episodes: int,
    horizon: int,
    device: torch.device,
) -> tuple[DQNAgent, list[dict]]:
    set_deterministic(model_seed)
    config = make_agent_config(variant, rsf, episodes, horizon)
    agent = DQNAgent(21, 3, config, device, model_seed, episodes)
    env = SatelliteSchedulingEnv(
        EnvConfig(horizon=horizon, coupling=1.0, scenario="nominal")
    )
    curve: list[dict] = []
    rolling: list[float] = []
    for episode in range(episodes):
        agent.schedule_episode_events(episode)
        state = env.reset(seed=model_seed * 1_000_000 + episode)
        episode_cost = 0.0
        losses: list[float] = []
        done = False
        while not done:
            action = agent.act(state, explore=True)
            next_state, reward, done, info = env.step(action)
            agent.observe(state, action, reward, next_state, done)
            loss = agent.update() if agent.steps % 4 == 0 else None
            if loss is not None:
                losses.append(loss)
            episode_cost += info["total_cost"]
            state = next_state
        rolling.append(episode_cost)
        if episode % 10 == 0 or episode == episodes - 1:
            curve.append(
                {
                    "variant": variant,
                    "configuration": rsf.name,
                    "model_seed": model_seed,
                    "episode": episode,
                    "cost": episode_cost,
                    "rolling_cost": float(np.mean(rolling[-20:])),
                    "loss": float(np.mean(losses)) if losses else np.nan,
                    "epsilon": agent.epsilon,
                    "skipped_updates": agent.skipped_updates,
                }
            )
    return agent, curve


def study_model_path(
    model_root: Path,
    stage: str,
    variant: str,
    configuration: str,
    model_seed: int,
) -> Path:
    stage_dir = model_root / stage
    stage_dir.mkdir(parents=True, exist_ok=True)
    return stage_dir / (
        f"{variant}__{configuration}__seed_{model_seed:03d}.pth"
    )


def study_curve_path(checkpoint: Path) -> Path:
    return checkpoint.with_name(checkpoint.stem + "__training_curve.csv")


def save_study_checkpoint(
    path: Path,
    agent: DQNAgent,
    variant: str,
    configuration: RSFStudyConfig,
    model_seed: int,
    episodes: int,
    horizon: int,
) -> None:
    torch.save(
        {
            "format_version": 1,
            "variant": variant,
            "configuration": asdict(configuration),
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
            "did_reset": agent.did_reset,
            "did_flush": agent.did_flush,
            "loss_ema": agent.loss_ema,
            "skipped_updates": agent.skipped_updates,
            "torch_version": torch.__version__,
        },
        path,
    )


def load_study_checkpoint(
    path: Path,
    variant: str,
    configuration: RSFStudyConfig,
    model_seed: int,
    episodes: int,
    horizon: int,
    device: torch.device,
) -> DQNAgent:
    config = make_agent_config(variant, configuration, episodes, horizon)
    agent = DQNAgent(21, 3, config, device, model_seed, episodes)
    payload = torch.load(path, map_location=device, weights_only=False)
    expected = {
        "variant": variant,
        "configuration": asdict(configuration),
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
    agent.did_reset = bool(payload["did_reset"])
    agent.did_flush = bool(payload["did_flush"])
    agent.loss_ema = payload["loss_ema"]
    agent.skipped_updates = int(payload["skipped_updates"])
    return agent


def write_study_model_manifest(model_root: Path) -> None:
    rows = []
    for path in sorted(model_root.rglob("*.pth")):
        payload = torch.load(path, map_location="cpu", weights_only=False)
        rows.append(
            {
                "file": str(path.relative_to(model_root)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
                "variant": payload["variant"],
                "configuration": payload["configuration"]["name"],
                "model_seed": payload["model_seed"],
                "episodes": payload["episodes"],
                "horizon": payload["horizon"],
                "training_steps": payload["training_steps"],
            }
        )
    pd.DataFrame(rows).to_csv(model_root / "model_manifest.csv", index=False)


def evaluate_agent(
    agent: DQNAgent,
    variant: str,
    configuration: str,
    model_seed: int,
    trace_seeds: list[int],
    horizon: int,
) -> list[dict]:
    rows: list[dict] = []
    for trace_seed in trace_seeds:
        env = SatelliteSchedulingEnv(
            EnvConfig(horizon=horizon, coupling=1.0, scenario="nominal")
        )
        state = env.reset(seed=trace_seed)
        totals = {
            key: 0.0
            for key in [
                "total_cost",
                "immediate_cost",
                "penalty",
                "thermal_violation",
                "energy_violation",
                "queue_violation",
                "contact_violation",
            ]
        }
        actions = np.zeros(3, dtype=int)
        done = False
        while not done:
            action = agent.act(state, explore=False)
            state, _, done, info = env.step(action)
            actions[action] += 1
            for key in totals:
                totals[key] += info[key]
        rows.append(
            {
                "variant": variant,
                "configuration": configuration,
                "model_seed": model_seed,
                "trace_seed": trace_seed,
                **totals,
                "onboard_fraction": actions[0] / horizon,
                "ground_fraction": actions[1] / horizon,
                "hybrid_fraction": actions[2] / horizon,
            }
        )
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
        ["variant", "configuration", "model_seed"], as_index=False
    )[metrics].mean()


def select_candidate(calibration_seed: pd.DataFrame) -> pd.DataFrame:
    standard = calibration_seed[
        calibration_seed.variant == "standard_dqn"
    ][["model_seed", "total_cost"]].rename(columns={"total_cost": "standard_cost"})
    full = calibration_seed[calibration_seed.variant == "md_dqn_rsf"].merge(
        standard, on="model_seed", how="inner"
    )
    full["paired_difference"] = full.total_cost - full.standard_cost
    scores = full.groupby("configuration").agg(
        mean_rsf_cost=("total_cost", "mean"),
        mean_standard_cost=("standard_cost", "mean"),
        mean_paired_difference=("paired_difference", "mean"),
        sd_paired_difference=("paired_difference", lambda x: x.std(ddof=1)),
        n_model_seeds=("model_seed", "nunique"),
    ).reset_index()
    return scores.sort_values(
        ["mean_paired_difference", "configuration"], ascending=[True, True]
    )


def summarize_confirmatory(seed_data: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "total_cost",
        "immediate_cost",
        "penalty",
        "thermal_violation",
        "energy_violation",
        "queue_violation",
        "contact_violation",
    ]
    grouped = seed_data.groupby("variant")[metrics]
    mean = grouped.mean().add_suffix("_mean")
    sd = grouped.std(ddof=1).add_suffix("_sd")
    n = grouped.size().rename("n_model_seeds")
    return pd.concat([mean, sd, n], axis=1).reset_index()


def paired_bootstrap(seed_data: pd.DataFrame, bootstrap_seed: int) -> pd.DataFrame:
    pivot = seed_data.pivot(
        index="model_seed", columns="variant", values="total_cost"
    )
    rng = np.random.default_rng(bootstrap_seed)
    rows: list[dict] = []
    for variant in ["dqn_r", "dqn_rs", "md_dqn_rsf"]:
        diff = (pivot[variant] - pivot["standard_dqn"]).dropna().to_numpy()
        boot = np.asarray(
            [rng.choice(diff, size=len(diff), replace=True).mean() for _ in range(10_000)]
        )
        rows.append(
            {
                "comparison": f"{variant} - standard_dqn",
                "n_pairs": len(diff),
                "mean_difference": float(diff.mean()),
                "sd_difference": float(diff.std(ddof=1)),
                "ci95_low": float(np.quantile(boot, 0.025)),
                "ci95_high": float(np.quantile(boot, 0.975)),
                "relative_improvement_percent": float(
                    -100 * diff.mean() / pivot["standard_dqn"].mean()
                ),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--calibration-seeds", type=int, default=4)
    parser.add_argument("--confirmatory-seeds", type=int, default=10)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("outputs_rsf_confirmatory"))
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from per-model partial CSV checkpoints in the output directory.",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        args.episodes = 12
        args.horizon = 16
        args.calibration_seeds = 2
        args.confirmatory_seeds = 2
        args.test_traces = 3
    args.output.mkdir(parents=True, exist_ok=True)
    model_root = args.output / "models"
    model_root.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(
        f"device={device}; calibration={args.calibration_seeds}; "
        f"confirmatory={args.confirmatory_seeds}",
        flush=True,
    )

    # Stage 1: calibration-only tuning. Model seeds 100+ and trace namespace
    # 700,000+ are never used in the confirmatory stage.
    calibration_partial = args.output / "calibration_raw.partial.csv"
    calibration_curve_partial = args.output / "calibration_training_curves.partial.csv"
    if args.resume and calibration_partial.exists():
        calibration_rows = pd.read_csv(calibration_partial).to_dict("records")
    else:
        calibration_rows: list[dict] = []
    if args.resume and calibration_curve_partial.exists():
        calibration_curves = pd.read_csv(calibration_curve_partial).to_dict("records")
    else:
        calibration_curves: list[dict] = []

    def calibration_complete(variant: str, configuration: str, model_seed: int) -> bool:
        if not calibration_rows:
            return False
        frame = pd.DataFrame(calibration_rows)
        mask = (
            (frame.variant == variant)
            & (frame.configuration == configuration)
            & (frame.model_seed == model_seed)
        )
        return int(mask.sum()) == args.test_traces

    def save_calibration_checkpoint() -> None:
        pd.DataFrame(calibration_rows).to_csv(calibration_partial, index=False)
        pd.DataFrame(calibration_curves).to_csv(calibration_curve_partial, index=False)

    reference = CANDIDATES[0]
    for index in range(args.calibration_seeds):
        model_seed = 100 + index
        traces = [700_000 + index * 1_000 + i for i in range(args.test_traces)]
        if calibration_complete("standard_dqn", "common_standard", model_seed):
            print(f"resume skip calibration standard seed={model_seed}", flush=True)
        else:
            checkpoint = study_model_path(
                model_root, "calibration", "standard_dqn", "common_standard", model_seed
            )
            saved_curve = study_curve_path(checkpoint)
            if args.resume and checkpoint.exists() and saved_curve.exists():
                print(f"loading calibration standard seed={model_seed}", flush=True)
                standard = load_study_checkpoint(
                    checkpoint, "standard_dqn", reference, model_seed,
                    args.episodes, args.horizon, device
                )
                calibration_curves.extend(pd.read_csv(saved_curve).to_dict("records"))
            else:
                print(f"calibration standard seed={model_seed}", flush=True)
                standard, curve = train_variant(
                    "standard_dqn", reference, model_seed, args.episodes,
                    args.horizon, device
                )
                calibration_curves.extend(curve)
                save_study_checkpoint(
                    checkpoint, standard, "standard_dqn", reference, model_seed,
                    args.episodes, args.horizon
                )
                pd.DataFrame(curve).to_csv(saved_curve, index=False)
            calibration_rows.extend(
                evaluate_agent(
                    standard,
                    "standard_dqn",
                    "common_standard",
                    model_seed,
                    traces,
                    args.horizon,
                )
            )
            save_calibration_checkpoint()
        for candidate in CANDIDATES:
            if calibration_complete("md_dqn_rsf", candidate.name, model_seed):
                print(f"resume skip calibration {candidate.name} seed={model_seed}", flush=True)
            else:
                checkpoint = study_model_path(
                    model_root, "calibration", "md_dqn_rsf", candidate.name, model_seed
                )
                saved_curve = study_curve_path(checkpoint)
                if args.resume and checkpoint.exists() and saved_curve.exists():
                    print(f"loading calibration {candidate.name} seed={model_seed}", flush=True)
                    agent = load_study_checkpoint(
                        checkpoint, "md_dqn_rsf", candidate, model_seed,
                        args.episodes, args.horizon, device
                    )
                    calibration_curves.extend(
                        pd.read_csv(saved_curve).to_dict("records")
                    )
                else:
                    print(f"calibration {candidate.name} seed={model_seed}", flush=True)
                    agent, curve = train_variant(
                        "md_dqn_rsf", candidate, model_seed, args.episodes,
                        args.horizon, device
                    )
                    calibration_curves.extend(curve)
                    save_study_checkpoint(
                        checkpoint, agent, "md_dqn_rsf", candidate, model_seed,
                        args.episodes, args.horizon
                    )
                    pd.DataFrame(curve).to_csv(saved_curve, index=False)
                calibration_rows.extend(
                    evaluate_agent(
                        agent,
                        "md_dqn_rsf",
                        candidate.name,
                        model_seed,
                        traces,
                        args.horizon,
                    )
                )
                save_calibration_checkpoint()

    calibration_raw = pd.DataFrame(calibration_rows)
    calibration_seed = seed_level(calibration_raw)
    candidate_scores = select_candidate(calibration_seed)
    selected_name = str(candidate_scores.iloc[0].configuration)
    selected = next(item for item in CANDIDATES if item.name == selected_name)
    calibration_raw.to_csv(args.output / "calibration_raw.csv", index=False)
    calibration_seed.to_csv(args.output / "calibration_seed_level.csv", index=False)
    pd.DataFrame(calibration_curves).to_csv(
        args.output / "calibration_training_curves.csv", index=False
    )
    candidate_scores.to_csv(args.output / "candidate_scores.csv", index=False)
    selection_record = {
        "selection_endpoint": "mean seed-level paired total-cost difference vs standard DQN",
        "selected": asdict(selected),
        "candidate_set": [asdict(item) for item in CANDIDATES],
        "calibration_model_seeds": [100 + i for i in range(args.calibration_seeds)],
        "calibration_trace_namespace": "700000 + seed_index*1000 + trace_index",
        "confirmatory_model_seeds": [200 + i for i in range(args.confirmatory_seeds)],
        "confirmatory_trace_namespace": "900000 + seed_index*1000 + trace_index",
        "note": "All confirmatory results must be reported; no seed-wise exclusions are permitted.",
    }
    (args.output / "selected_config.json").write_text(
        json.dumps(selection_record, indent=2), encoding="utf-8"
    )
    print(candidate_scores.to_string(index=False), flush=True)
    print(f"locked configuration={selected_name}", flush=True)

    # Stage 2: fresh training seeds and trace namespace. The selected settings
    # are locked before any confirmatory model is trained or evaluated.
    confirmatory_partial = args.output / "confirmatory_raw.partial.csv"
    confirmatory_curve_partial = args.output / "confirmatory_training_curves.partial.csv"
    if args.resume and confirmatory_partial.exists():
        confirmatory_rows = pd.read_csv(confirmatory_partial).to_dict("records")
    else:
        confirmatory_rows: list[dict] = []
    if args.resume and confirmatory_curve_partial.exists():
        confirmatory_curves = pd.read_csv(confirmatory_curve_partial).to_dict("records")
    else:
        confirmatory_curves: list[dict] = []

    def confirmatory_complete(variant: str, model_seed: int) -> bool:
        if not confirmatory_rows:
            return False
        frame = pd.DataFrame(confirmatory_rows)
        mask = (frame.variant == variant) & (frame.model_seed == model_seed)
        return int(mask.sum()) == args.test_traces

    def save_confirmatory_checkpoint() -> None:
        pd.DataFrame(confirmatory_rows).to_csv(confirmatory_partial, index=False)
        pd.DataFrame(confirmatory_curves).to_csv(
            confirmatory_curve_partial, index=False
        )

    variants = ["standard_dqn", "dqn_r", "dqn_rs", "md_dqn_rsf"]
    for index in range(args.confirmatory_seeds):
        model_seed = 200 + index
        traces = [900_000 + index * 1_000 + i for i in range(args.test_traces)]
        for variant in variants:
            if confirmatory_complete(variant, model_seed):
                print(f"resume skip confirmatory {variant} seed={model_seed}", flush=True)
                continue
            checkpoint = study_model_path(
                model_root, "confirmatory", variant, selected.name, model_seed
            )
            saved_curve = study_curve_path(checkpoint)
            if args.resume and checkpoint.exists() and saved_curve.exists():
                print(f"loading confirmatory {variant} seed={model_seed}", flush=True)
                agent = load_study_checkpoint(
                    checkpoint, variant, selected, model_seed,
                    args.episodes, args.horizon, device
                )
                confirmatory_curves.extend(
                    pd.read_csv(saved_curve).to_dict("records")
                )
            else:
                print(f"confirmatory {variant} seed={model_seed}", flush=True)
                agent, curve = train_variant(
                    variant, selected, model_seed, args.episodes, args.horizon, device
                )
                confirmatory_curves.extend(curve)
                save_study_checkpoint(
                    checkpoint, agent, variant, selected, model_seed,
                    args.episodes, args.horizon
                )
                pd.DataFrame(curve).to_csv(saved_curve, index=False)
            confirmatory_rows.extend(
                evaluate_agent(
                    agent,
                    variant,
                    selected.name,
                    model_seed,
                    traces,
                    args.horizon,
                )
            )
            save_confirmatory_checkpoint()

    confirmatory_raw = pd.DataFrame(confirmatory_rows)
    confirmatory_seed = seed_level(confirmatory_raw)
    confirmatory_summary = summarize_confirmatory(confirmatory_seed)
    comparison = paired_bootstrap(confirmatory_seed, bootstrap_seed=20260820)
    confirmatory_raw.to_csv(args.output / "confirmatory_raw.csv", index=False)
    confirmatory_seed.to_csv(
        args.output / "confirmatory_seed_level.csv", index=False
    )
    pd.DataFrame(confirmatory_curves).to_csv(
        args.output / "confirmatory_training_curves.csv", index=False
    )
    confirmatory_summary.to_csv(
        args.output / "confirmatory_summary.csv", index=False
    )
    comparison.to_csv(args.output / "confirmatory_comparison.csv", index=False)
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
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    write_study_model_manifest(model_root)
    print(confirmatory_summary.to_string(index=False), flush=True)
    print(comparison.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
