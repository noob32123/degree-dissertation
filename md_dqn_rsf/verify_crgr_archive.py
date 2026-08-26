"""Audit a CRGR experiment archive and its pure-DQN invariants."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from crgr_agent import CRGRAgentConfig


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-models", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    metadata = json.loads((args.output / "metadata.json").read_text(encoding="utf-8"))
    locked = json.loads(
        (args.output / "selected_config.json").read_text(encoding="utf-8")
    )
    digest = locked.pop("lock_sha256")
    canonical = json.dumps(locked, sort_keys=True, separators=(",", ":"))
    require(
        hashlib.sha256(canonical.encode("utf-8")).hexdigest() == digest,
        "selected configuration hash mismatch",
    )
    locked["lock_sha256"] = digest
    selected = locked["selected"]

    episodes = int(metadata["episodes"])
    horizon = int(metadata["horizon"])
    calibration_seeds = int(metadata["calibration_model_seeds"])
    confirmatory_seeds = int(metadata["confirmatory_model_seeds"])
    traces = int(metadata["test_traces_per_seed"])
    calibration = pd.read_csv(args.output / "calibration_raw.csv")
    confirmatory = pd.read_csv(args.output / "confirmatory_raw.csv")
    comparison = pd.read_csv(args.output / "confirmatory_comparison.csv")
    success = json.loads(
        (args.output / "success_criterion.json").read_text(encoding="utf-8")
    )

    grid_count = len(locked["candidate_grid"])
    require(
        len(calibration) == calibration_seeds * traces * 5 * (1 + grid_count),
        "unexpected calibration row count",
    )
    require(
        len(confirmatory) == confirmatory_seeds * traces * 7 * 3,
        "unexpected confirmatory row count",
    )
    require(
        set(confirmatory.variant)
        == {"standard_dqn", "ungated_ranking_dqn", "md_crgr_dqn"},
        "unexpected confirmatory variants",
    )
    numeric = confirmatory.select_dtypes(include=[np.number]).to_numpy()
    require(np.isfinite(numeric).all(), "confirmatory CSV contains non-finite values")
    require(len(comparison) == 15, "expected three comparisons in five scenarios")

    checkpoints = sorted((args.output / "models").rglob("*.pth"))
    expected_checkpoints = calibration_seeds * (1 + grid_count) + confirmatory_seeds * 3
    require(len(checkpoints) == expected_checkpoints, "unexpected checkpoint count")
    variants: dict[str, list[dict]] = {}
    reference_matches = 0
    for path in checkpoints:
        payload = torch.load(path, map_location="cpu", weights_only=False)
        require(payload["algorithm_family"] == "pure_dqn_crgr", f"{path}: family")
        require(payload["bellman_target"] == "target_network_max", f"{path}: target")
        require(payload["replay"] == "uniform_one_step", f"{path}: replay")
        require(payload["network"] == "original_q_network", f"{path}: network")
        require(payload["training_steps"] == episodes * horizon, f"{path}: steps")
        require(payload["state_dim"] == 21 and payload["action_dim"] == 3, f"{path}: dims")
        config = payload["agent_config"]
        require(set(config) == set(asdict(CRGRAgentConfig())), f"{path}: config fields")
        forbidden = {"double_dqn", "dueling", "prioritized_replay", "n_step", "noisy"}
        require(not forbidden.intersection(config), f"{path}: forbidden enhancement")
        variant = payload["variant"]
        variants.setdefault(variant, []).append(config)
        if variant == "standard_dqn":
            require(not config["use_ranking"] and not config["use_gate"], f"{path}: baseline")
        elif variant == "ungated_ranking_dqn":
            require(config["use_ranking"] and not config["use_gate"], f"{path}: ungated")
        elif variant == "md_crgr_dqn":
            require(config["use_ranking"] and config["use_gate"], f"{path}: CRGR")
        else:
            raise ValueError(f"{path}: unknown variant {variant}")

        if (
            args.reference_models
            and "confirmatory" in path.parts
            and variant == "standard_dqn"
        ):
            reference_path = args.reference_models / (
                f"standard_dqn_seed_{int(payload['model_seed']):03d}.pth"
            )
            if reference_path.exists():
                reference = torch.load(reference_path, map_location="cpu", weights_only=False)
                for key, value in payload["online_state_dict"].items():
                    require(
                        torch.equal(value, reference["online_state_dict"][key]),
                        f"{path}: baseline differs from archived reference at {key}",
                    )
                reference_matches += 1

    confirm_ungated = [
        torch.load(path, map_location="cpu", weights_only=False)["agent_config"]
        for path in checkpoints
        if "confirmatory" in path.parts and "ungated_ranking_dqn" in path.name
    ]
    confirm_crgr = [
        torch.load(path, map_location="cpu", weights_only=False)["agent_config"]
        for path in checkpoints
        if "confirmatory" in path.parts and "md_crgr_dqn" in path.name
    ]
    for left, right in zip(confirm_ungated, confirm_crgr):
        differences = {key for key in left if left[key] != right[key]}
        require(differences == {"use_gate"}, "ungated and CRGR differ beyond gate flag")

    report = {
        "status": "passed",
        "scientific_success_criterion_passed": bool(success["passed"]),
        "checkpoints": len(checkpoints),
        "calibration_rows": len(calibration),
        "confirmatory_rows": len(confirmatory),
        "selected_configuration": selected,
        "lock_sha256": digest,
        "reference_standard_models_matched": reference_matches,
        "verified_invariants": [
            "original QNetwork",
            "standard target-network max Bellman target",
            "uniform one-step replay",
            "no Double DQN, dueling, PER, n-step, noisy, or distributional mechanism",
            "ungated and CRGR confirmatory configs differ only by use_gate",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
