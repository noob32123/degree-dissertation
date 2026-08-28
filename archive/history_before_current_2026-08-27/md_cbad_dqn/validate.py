"""Acceptance checks for code, checkpoints, and locked evaluation data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .experiment import ALL_POLICIES, MODEL_SEEDS, SCENARIOS, load_checkpoint


METRICS = (
    "total_cost", "immediate_cost", "penalty", "thermal_violation",
    "energy_violation", "queue_violation", "contact_violation",
    "onboard_fraction", "ground_fraction", "hybrid_fraction",
)


def validate_checkpoints(results: Path) -> list[dict]:
    device = torch.device("cpu")
    rows: list[dict] = []
    for seed in MODEL_SEEDS:
        for variant, name in (
            ("standard_dqn", f"standard_dqn__standard__seed_{seed}.pth"),
            ("md_cbad_dqn", f"md_cbad_dqn__lambda_0p3__seed_{seed}.pth"),
            ("contextual_bandit", f"contextual_bandit__gamma_0__seed_{seed}.pth"),
        ):
            stage = "contextual_bandit" if variant == "contextual_bandit" else "confirmatory"
            path = results / "models" / stage / name
            agent = load_checkpoint(path, variant, seed, device)
            values = torch.cat([parameter.detach().flatten() for parameter in agent.online.parameters()])
            if not torch.isfinite(values).all():
                raise AssertionError(f"non-finite checkpoint: {path}")
            if agent.steps != 38_400:
                raise AssertionError(f"wrong interaction budget: {path}")
            rows.append(
                {
                    "file": path.relative_to(results).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "parameters": int(values.numel()),
                    "training_steps": agent.steps,
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path(__file__).parent / "results")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "validation.json")
    args = parser.parse_args()
    raw = pd.read_csv(args.results / "seven_scenarios_raw.csv")
    expected = len(SCENARIOS) * len(ALL_POLICIES) * len(MODEL_SEEDS) * 20
    if len(raw) != expected:
        raise AssertionError(f"expected {expected} rows, found {len(raw)}")
    counts = raw.groupby(["scenario", "policy", "model_seed"]).size()
    if not (counts == 20).all():
        raise AssertionError("each scenario-policy-seed cell must contain 20 traces")
    if not np.isfinite(raw[list(METRICS)].to_numpy(dtype=float)).all():
        raise AssertionError("non-finite evaluation data")
    checkpoints = validate_checkpoints(args.results)
    report = {
        "status": "passed",
        "evaluation_rows": len(raw),
        "scenario_policy_seed_cells": int(len(counts)),
        "traces_per_cell": 20,
        "checkpoints": checkpoints,
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
