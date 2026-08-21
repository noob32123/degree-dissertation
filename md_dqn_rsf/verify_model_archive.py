"""Verify saved PyTorch checkpoints and their SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import torch

from agent import QNetwork


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.models / "model_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing manifest: {manifest_path}")
    manifest = pd.read_csv(manifest_path)
    if manifest.empty:
        raise ValueError("model manifest is empty")

    verified = []
    for row in manifest.to_dict("records"):
        path = args.models / row["file"]
        if not path.exists():
            raise FileNotFoundError(f"missing checkpoint: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {path}")
        if path.stat().st_size != int(row["bytes"]):
            raise ValueError(f"file-size mismatch: {path}")
        payload = torch.load(path, map_location="cpu", weights_only=False)
        state_dim = int(payload["state_dim"])
        action_dim = int(payload["action_dim"])
        network = QNetwork(state_dim, action_dim)
        network.load_state_dict(payload["online_state_dict"], strict=True)
        network.eval()
        with torch.no_grad():
            output = network(torch.zeros((1, state_dim), dtype=torch.float32))
        if tuple(output.shape) != (1, action_dim):
            raise ValueError(f"unexpected network output shape: {path}")
        if not torch.isfinite(output).all():
            raise ValueError(f"non-finite network output: {path}")
        verified.append(
            {
                "file": row["file"],
                "sha256": digest,
                "bytes": path.stat().st_size,
                "state_dim": state_dim,
                "action_dim": action_dim,
                "training_steps": int(payload["training_steps"]),
                "load_and_forward": "passed",
            }
        )

    report = {
        "models_directory": str(args.models.resolve()),
        "manifest": str(manifest_path.resolve()),
        "n_models": len(verified),
        "status": "passed",
        "checks": verified,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"verified {len(verified)} checkpoints; report={args.report}", flush=True)


if __name__ == "__main__":
    main()
