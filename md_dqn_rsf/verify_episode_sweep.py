"""Verify the three task-specific single-policy experiment archives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch


RUNS = [
    ("outputs_standard_dqn_ep400", "standard_dqn", 400, {}),
    ("outputs_dqn_r_ep470", "dqn_r", 470, {"use_reset": True}),
    (
        "outputs_dqn_rs_ep540",
        "dqn_rs",
        540,
        {"use_reset": True, "use_selective": True},
    ),
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    results = []
    for folder, policy, episodes, enabled_flags in RUNS:
        output = args.root / folder
        raw = pd.read_csv(output / "evaluation_raw.csv")
        summary = pd.read_csv(output / "summary.csv")
        curves = pd.read_csv(output / "training_curves.csv")
        manifest = pd.read_csv(output / "models" / "model_manifest.csv")
        verification = json.loads(
            (output / "model_verification.json").read_text(encoding="utf-8")
        )
        metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))

        require(len(raw) == 700, f"{folder}: expected 700 evaluation rows")
        require(len(summary) == 7, f"{folder}: expected 7 summary rows")
        require(set(summary["n"]) == {5}, f"{folder}: summary n must equal 5")
        require(set(raw["policy"]) == {policy}, f"{folder}: unexpected policy")
        require(set(raw["model_seed"]) == set(range(5)), f"{folder}: bad model seeds")
        require(raw.trace_seed.min() == 500_000, f"{folder}: bad minimum trace seed")
        require(raw.trace_seed.max() == 504_019, f"{folder}: bad maximum trace seed")
        require(raw.trace_seed.nunique() == 100, f"{folder}: expected 100 trace seeds")
        require(len(manifest) == 5, f"{folder}: expected 5 checkpoints")
        require(
            set(manifest["training_steps"]) == {episodes * 64},
            f"{folder}: incorrect training steps",
        )
        require(
            verification.get("status") == "passed"
            and verification.get("n_models") == 5,
            f"{folder}: model verification did not pass 5/5",
        )
        require(metadata.get("policy") == policy, f"{folder}: metadata policy mismatch")
        require(metadata.get("episodes") == episodes, f"{folder}: metadata episode mismatch")
        require(metadata.get("horizon") == 64, f"{folder}: metadata horizon mismatch")
        require(metadata.get("model_seeds") == 5, f"{folder}: metadata seed mismatch")
        require(
            metadata.get("test_traces_per_seed") == 20,
            f"{folder}: metadata trace-count mismatch",
        )
        require(
            (output / "run.err.log").stat().st_size == 0,
            f"{folder}: error log is not empty",
        )

        expected_curve_rows = 5 * (
            len(range(0, episodes, 10))
            + (0 if (episodes - 1) % 10 == 0 else 1)
        )
        require(
            len(curves) == expected_curve_rows,
            f"{folder}: unexpected training-curve row count",
        )

        for checkpoint_path in sorted((output / "models").glob("*.pth")):
            payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            require(payload["policy"] == policy, f"{checkpoint_path}: policy mismatch")
            require(payload["episodes"] == episodes, f"{checkpoint_path}: episode mismatch")
            require(payload["horizon"] == 64, f"{checkpoint_path}: horizon mismatch")
            config = payload["agent_config"]
            for flag in ("use_reset", "use_selective", "use_flush"):
                require(
                    bool(config[flag]) == bool(enabled_flags.get(flag, False)),
                    f"{checkpoint_path}: {flag} mismatch",
                )

        nominal = summary[
            (summary.scenario == "nominal") & (summary.coupling == 1.0)
        ].iloc[0]
        results.append(
            {
                "folder": folder,
                "policy": policy,
                "episodes": episodes,
                "training_steps_per_seed": episodes * 64,
                "evaluation_rows": len(raw),
                "summary_rows": len(summary),
                "checkpoints": len(manifest),
                "trace_seed_min": int(raw.trace_seed.min()),
                "trace_seed_max": int(raw.trace_seed.max()),
                "nominal_total_cost_mean": float(nominal.total_cost_mean),
                "nominal_total_cost_sd": float(nominal.total_cost_sd),
                "status": "passed",
            }
        )

    report = {"status": "passed", "runs": results}
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(pd.DataFrame(results).to_string(index=False), flush=True)
    print(f"report={args.report}", flush=True)


if __name__ == "__main__":
    main()
