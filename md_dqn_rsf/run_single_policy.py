"""Train and evaluate one learned policy with the main-experiment protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch

from run_experiments import (
    curve_path,
    evaluate_policy,
    load_agent_checkpoint,
    model_path,
    save_agent_checkpoint,
    set_deterministic,
    summarize,
    train_agent,
    write_model_manifest,
)


LEARNED_POLICIES = [
    "contextual_bandit",
    "standard_dqn",
    "dqn_r",
    "dqn_rs",
    "md_dqn_rsf",
]

STRESS_CASES = [
    ("static", 0.0),
    ("nominal", 0.5),
    ("nominal", 1.0),
    ("burst", 1.0),
    ("link_limited", 1.0),
    ("energy_limited", 1.0),
    ("thermal_stress", 1.0),
]


def validate_or_write_run_config(path: Path, config: dict) -> None:
    """Prevent --resume from mixing outputs from incompatible runs."""
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing != config:
            raise ValueError(
                f"run configuration mismatch for {path}: "
                f"existing={existing!r}, requested={config!r}"
            )
        return
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=LEARNED_POLICIES, required=True)
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Load matching saved models and completed seed evaluations when present.",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    if args.smoke:
        args.episodes, args.horizon, args.seeds, args.test_traces = 12, 16, 1, 3
    if min(args.episodes, args.horizon, args.seeds, args.test_traces) <= 0:
        parser.error("episodes, horizon, seeds, and test-traces must all be positive")

    args.output.mkdir(parents=True, exist_ok=True)
    model_dir = args.output / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    run_config = {
        "policy": args.policy,
        "episodes": args.episodes,
        "horizon": args.horizon,
        "model_seeds": args.seeds,
        "test_traces_per_seed": args.test_traces,
        "stress_cases": [list(item) for item in STRESS_CASES],
    }
    validate_or_write_run_config(args.output / "run_config.json", run_config)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(
        f"device={device}; torch={torch.__version__}; policy={args.policy}; "
        f"episodes={args.episodes}",
        flush=True,
    )

    partial_evaluation = args.output / "evaluation_raw.partial.csv"
    if args.resume and partial_evaluation.exists():
        all_rows = pd.read_csv(partial_evaluation).to_dict("records")
    else:
        all_rows: list[dict] = []
    all_curves: list[dict] = []

    for seed in range(args.seeds):
        set_deterministic(seed)
        checkpoint_path = model_path(model_dir, args.policy, seed)
        saved_curve = curve_path(model_dir, args.policy, seed)
        if args.resume and checkpoint_path.exists() and saved_curve.exists():
            print(
                f"loading {args.policy} seed={seed} from {checkpoint_path}",
                flush=True,
            )
            agent = load_agent_checkpoint(
                checkpoint_path,
                args.policy,
                seed,
                args.episodes,
                args.horizon,
                device,
            )
            curve = pd.read_csv(saved_curve).to_dict("records")
        else:
            print(f"training {args.policy} seed={seed}", flush=True)
            agent, curve = train_agent(
                args.policy, seed, args.episodes, args.horizon, device
            )
            save_agent_checkpoint(
                checkpoint_path,
                agent,
                args.policy,
                seed,
                args.episodes,
                args.horizon,
            )
            pd.DataFrame(curve).to_csv(saved_curve, index=False)
        all_curves.extend(curve)

        trace_seeds = [
            500_000 + seed * 1_000 + i for i in range(args.test_traces)
        ]
        expected_seed_rows = len(STRESS_CASES) * args.test_traces
        existing_seed_rows = sum(
            1 for row in all_rows if int(row["model_seed"]) == seed
        )
        if args.resume and existing_seed_rows == expected_seed_rows:
            print(f"resume skip evaluation seed={seed}", flush=True)
            continue

        all_rows = [
            row for row in all_rows if int(row["model_seed"]) != seed
        ]
        for scenario, coupling in STRESS_CASES:
            actual_scenario = "nominal" if scenario == "static" else scenario
            all_rows.extend(
                evaluate_policy(
                    args.policy,
                    agent,
                    seed,
                    trace_seeds,
                    args.horizon,
                    coupling,
                    actual_scenario,
                )
            )
        pd.DataFrame(all_rows).to_csv(partial_evaluation, index=False)

    raw = pd.DataFrame(all_rows)
    curves = pd.DataFrame(all_curves)
    summary = summarize(raw)
    raw.to_csv(args.output / "evaluation_raw.csv", index=False)
    curves.to_csv(args.output / "training_curves.csv", index=False)
    summary.to_csv(args.output / "summary.csv", index=False)
    metadata = {
        "device": str(device),
        "torch": torch.__version__,
        "policy": args.policy,
        "episodes": args.episodes,
        "horizon": args.horizon,
        "model_seeds": args.seeds,
        "test_traces_per_seed": args.test_traces,
        "evaluation_settings": len(STRESS_CASES),
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    write_model_manifest(model_dir)
    nominal = summary[
        (summary.scenario == "nominal") & (summary.coupling == 1.0)
    ]
    print(nominal.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
