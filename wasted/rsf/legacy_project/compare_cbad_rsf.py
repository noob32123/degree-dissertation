"""Train the existing MD-DQN-RSF on CBAD's untouched confirmation seeds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from run_cbad_study import CONFIRMATORY_SEED_START, CONFIRMATORY_TRACE_START
from run_crgr_study import CONFIRMATORY_SCENARIOS, evaluate, seed_level
from run_experiments import (
    load_agent_checkpoint,
    save_agent_checkpoint,
    set_deterministic,
    train_agent,
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
    model_dir = args.output / "rsf_models"
    model_dir.mkdir(parents=True, exist_ok=True)
    rsf_rows: list[dict] = []
    partial = args.output / "rsf_confirmatory_raw.partial.csv"
    if args.resume and partial.exists():
        rsf_rows = pd.read_csv(partial).to_dict("records")

    for index in range(args.seeds):
        seed = CONFIRMATORY_SEED_START + index
        complete = len([
            row for row in rsf_rows if int(row["model_seed"]) == seed
        ]) == len(CONFIRMATORY_SCENARIOS) * args.test_traces
        if complete:
            continue
        path = model_dir / f"md_dqn_rsf_seed_{seed}.pth"
        set_deterministic(seed)
        if args.resume and path.exists():
            print(f"loading md_dqn_rsf seed={seed}", flush=True)
            agent = load_agent_checkpoint(
                path, "md_dqn_rsf", seed, args.episodes, args.horizon, device
            )
        else:
            print(f"training md_dqn_rsf seed={seed}", flush=True)
            agent, _ = train_agent(
                "md_dqn_rsf", seed, args.episodes, args.horizon, device
            )
            save_agent_checkpoint(
                path, agent, "md_dqn_rsf", seed, args.episodes, args.horizon
            )
        traces = [
            CONFIRMATORY_TRACE_START + index * 1_000 + i
            for i in range(args.test_traces)
        ]
        rsf_rows = [
            row for row in rsf_rows if int(row["model_seed"]) != seed
        ]
        rsf_rows.extend(evaluate(
            agent,
            "md_dqn_rsf",
            "existing_rsf",
            seed,
            traces,
            args.horizon,
            CONFIRMATORY_SCENARIOS,
        ))
        pd.DataFrame(rsf_rows).to_csv(partial, index=False)

    rsf_raw = pd.DataFrame(rsf_rows)
    cbad_raw = pd.read_csv(args.output / "confirmatory_raw.csv")
    combined = pd.concat([
        cbad_raw[cbad_raw.variant == "md_cbad_dqn"], rsf_raw
    ], ignore_index=True)
    seeds = seed_level(combined)
    rng = np.random.default_rng(20260828)
    rows = []
    for scenario, _ in CONFIRMATORY_SCENARIOS:
        pivot = seeds[seeds.scenario == scenario].pivot(
            index="model_seed", columns="variant", values="total_cost"
        )
        diff = (pivot.md_cbad_dqn - pivot.md_dqn_rsf).dropna().to_numpy()
        boot = rng.choice(diff, size=(10_000, len(diff)), replace=True).mean(axis=1)
        rows.append({
            "scenario": scenario,
            "comparison": "md_cbad_dqn - md_dqn_rsf",
            "n_pairs": len(diff),
            "mean_difference": float(diff.mean()),
            "ci95_low": float(np.quantile(boot, 0.025)),
            "ci95_high": float(np.quantile(boot, 0.975)),
            "relative_improvement_percent": float(
                -100 * diff.mean() / pivot.md_dqn_rsf.mean()
            ),
        })
    comparison = pd.DataFrame(rows)
    comparison["passed"] = (
        (comparison.mean_difference < 0) & (comparison.ci95_high < 0)
    )
    success = bool(len(comparison) == 5 and comparison.passed.all())
    rsf_raw.to_csv(args.output / "rsf_confirmatory_raw.csv", index=False)
    seeds.to_csv(args.output / "cbad_rsf_seed_level.csv", index=False)
    comparison.to_csv(args.output / "cbad_rsf_comparison.csv", index=False)
    (args.output / "cbad_rsf_success.json").write_text(
        json.dumps({"passed": success, "results": comparison.to_dict("records")}, indent=2),
        encoding="utf-8",
    )
    print(comparison.to_string(index=False), flush=True)
    print(f"CBAD significantly beats RSF in all five scenarios={success}", flush=True)


if __name__ == "__main__":
    main()
