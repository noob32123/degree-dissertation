"""Same-seed component ablation for standard DQN, CFBA, and CBAD."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_cbad_study import (
    CONFIRMATORY_SEED_START,
    CONFIRMATORY_TRACE_START,
    CONFIRMATORY_SCENARIOS,
)
from run_cfba_study import train_or_load
from run_crgr_study import evaluate, seed_level


CFBA_WEIGHT = 0.3
COMPARISONS = (
    ("md_cfba_dqn", "standard_dqn", "counterfactual absolute target contribution"),
    ("md_cbad_dqn", "md_cfba_dqn", "within-state centering contribution"),
    ("md_cbad_dqn", "standard_dqn", "complete CBAD contribution"),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=600)
    parser.add_argument("--horizon", type=int, default=64)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--test-traces", type=int, default=20)
    parser.add_argument(
        "--output", type=Path, default=Path("outputs_cbad_study")
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    partial = args.output / "cfba_ablation_raw.partial.csv"
    cfba_rows = (
        pd.read_csv(partial).to_dict("records")
        if args.resume and partial.exists()
        else []
    )

    for index in range(args.seeds):
        seed = CONFIRMATORY_SEED_START + index
        complete = len([
            row for row in cfba_rows if int(row["model_seed"]) == seed
        ]) == len(CONFIRMATORY_SCENARIOS) * args.test_traces
        if complete:
            continue
        agent = train_or_load(
            args,
            "ablation",
            "md_cfba_dqn",
            "lambda_0p3_uncentered",
            seed,
            CFBA_WEIGHT,
            device,
        )
        traces = [
            CONFIRMATORY_TRACE_START + index * 1_000 + trace_index
            for trace_index in range(args.test_traces)
        ]
        cfba_rows = [
            row for row in cfba_rows if int(row["model_seed"]) != seed
        ]
        cfba_rows.extend(
            evaluate(
                agent,
                "md_cfba_dqn",
                "lambda_0p3_uncentered",
                seed,
                traces,
                args.horizon,
                CONFIRMATORY_SCENARIOS,
            )
        )
        pd.DataFrame(cfba_rows).to_csv(partial, index=False)

    factual = pd.read_csv(args.output / "confirmatory_raw.csv")
    factual = factual[
        factual.variant.isin(["standard_dqn", "md_cbad_dqn"])
    ]
    raw = pd.concat([factual, pd.DataFrame(cfba_rows)], ignore_index=True)
    expected = args.seeds * args.test_traces
    counts = raw.groupby(["scenario", "variant"]).size()
    for scenario, _ in CONFIRMATORY_SCENARIOS:
        for variant in ("standard_dqn", "md_cfba_dqn", "md_cbad_dqn"):
            if int(counts.get((scenario, variant), 0)) != expected:
                raise ValueError(
                    f"incomplete ablation: {scenario} {variant} "
                    f"has {counts.get((scenario, variant), 0)}, expected {expected}"
                )

    seeds = seed_level(raw)
    rng = np.random.default_rng(20260829)
    rows: list[dict] = []
    for scenario, coupling in CONFIRMATORY_SCENARIOS:
        pivot = seeds[
            (seeds.scenario == scenario) & (seeds.coupling == coupling)
        ].pivot(index="model_seed", columns="variant", values="total_cost")
        for treatment, reference, interpretation in COMPARISONS:
            diff = (pivot[treatment] - pivot[reference]).dropna().to_numpy()
            boot = rng.choice(
                diff, size=(10_000, len(diff)), replace=True
            ).mean(axis=1)
            rows.append(
                {
                    "scenario": scenario,
                    "comparison": f"{treatment} - {reference}",
                    "interpretation": interpretation,
                    "n_pairs": len(diff),
                    "mean_difference": float(diff.mean()),
                    "ci95_low": float(np.quantile(boot, 0.025)),
                    "ci95_high": float(np.quantile(boot, 0.975)),
                    "relative_improvement_percent": float(
                        -100.0 * diff.mean() / pivot[reference].mean()
                    ),
                }
            )
    comparison = pd.DataFrame(rows)
    comparison["mean_better"] = comparison.mean_difference < 0
    comparison["significant"] = comparison.ci95_high < 0

    means = seeds.groupby(
        ["scenario", "variant"], as_index=False
    ).agg(
        total_cost_mean=("total_cost", "mean"),
        immediate_cost_mean=("immediate_cost", "mean"),
        penalty_mean=("penalty", "mean"),
        queue_violation_mean=("queue_violation", "mean"),
    )
    raw.to_csv(args.output / "ablation_raw.csv", index=False)
    seeds.to_csv(args.output / "ablation_seed_level.csv", index=False)
    means.to_csv(args.output / "ablation_means.csv", index=False)
    comparison.to_csv(args.output / "ablation_comparison.csv", index=False)
    (args.output / "ablation_result.json").write_text(
        json.dumps(
            {
                "design": {
                    "model_seeds": [
                        CONFIRMATORY_SEED_START + i for i in range(args.seeds)
                    ],
                    "test_traces_per_seed": args.test_traces,
                    "real_steps_per_model": args.episodes * args.horizon,
                    "shared_counterfactual_weight": CFBA_WEIGHT,
                    "bootstrap_resamples": 10_000,
                    "bootstrap_seed": 20260829,
                },
                "results": comparison.to_dict("records"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(means.to_string(index=False), flush=True)
    print(comparison.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
