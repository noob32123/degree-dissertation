from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import re
import shutil

import torch


WORKSPACE = Path(r"H:\degree-dissertation")
SOURCE_PACKAGE = WORKSPACE / "md_cbad_dqn"
SOURCE_RESULTS = SOURCE_PACKAGE / "results" / "revision_round2"
TARGET_ROOT = Path(r"H:\dqn_family_satellite_ground_reproducibility")
TARGET_PACKAGE = TARGET_ROOT / "dqn_family_satellite_ground"
TARGET_RESULTS = TARGET_PACKAGE / "results" / "revision_round2"

REPLACEMENTS = (
    ("md_cbad_dqn.", "dqn_family_satellite_ground."),
    ("md_cbad_dqn/", "dqn_family_satellite_ground/"),
    ("md_cbad_dqn\\", "dqn_family_satellite_ground\\"),
    ("double_cbad_dqn", "double_centered_full_action_dqn"),
    ("md_immediate_advantage_dqn", "immediate_advantage_dqn"),
    ("md_fullq_dqn", "full_action_q_dqn"),
    ("md_cbad_dqn", "centered_full_action_dqn"),
    ("MD-CBAD-DQN", "DQN-family implementation"),
)
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".tsv"}
LOCKED_TAGS = {
    "standard_dqn": "standard",
    "full_action_q_dqn": "lambda_0p3_uncentered",
    "immediate_advantage_dqn": "lambda_0p3_immediate",
    "centered_full_action_dqn": "lambda_0p3",
    "double_dqn": "double",
    "double_centered_full_action_dqn": "double_lambda_0p3",
}


def replace_text(value: str) -> str:
    for old, new in REPLACEMENTS:
        value = value.replace(old, new)
    return value


def replace_object(value):
    if isinstance(value, str):
        return replace_text(value)
    if isinstance(value, dict):
        return {replace_object(k): replace_object(v) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_object(v) for v in value]
    if isinstance(value, tuple):
        return tuple(replace_object(v) for v in value)
    return value


def transformed_name(name: str) -> str:
    return replace_text(name)


def locked_gamma97_source(target_name: str) -> Path | None:
    match = re.fullmatch(
        r"(.+)__gamma_0p97__seed_(\d+)(?P<curve>__curve\.csv|\.pth)", target_name
    )
    if not match or match.group(1) not in LOCKED_TAGS:
        return None
    variant, seed = match.group(1), match.group(2)
    suffix = "__curve.csv" if match.group("curve") == "__curve.csv" else ".pth"
    return (TARGET_PACKAGE / "results" / "reviewer_revision_state_complete" / "models" /
            f"{variant}__{LOCKED_TAGS[variant]}__seed_{seed}{suffix}")


def copy_source_files() -> None:
    for name in ("experiment.py", "revision_experiments.py", "revision_reporting.py"):
        source = SOURCE_PACKAGE / name
        target = TARGET_PACKAGE / name
        target.write_text(replace_text(source.read_text(encoding="utf-8")), encoding="utf-8")
    source_test = SOURCE_PACKAGE / "tests" / "test_revision_experiments.py"
    target_test = TARGET_PACKAGE / "tests" / "test_revision_experiments.py"
    target_test.write_text(replace_text(source_test.read_text(encoding="utf-8")), encoding="utf-8")


def copy_results() -> None:
    if TARGET_RESULTS.exists():
        shutil.rmtree(TARGET_RESULTS)
    TARGET_RESULTS.mkdir(parents=True)
    for source in sorted(SOURCE_RESULTS.rglob("*")):
        if not source.is_file() or source.name == "artifact_manifest.csv":
            continue
        relative = Path(*(transformed_name(part) for part in source.relative_to(SOURCE_RESULTS).parts))
        target = TARGET_RESULTS / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        locked = locked_gamma97_source(target.name) if "gamma_models" in relative.parts else None
        if locked is not None:
            if not locked.exists():
                raise FileNotFoundError(locked)
            shutil.copy2(locked, target)
        elif source.suffix.lower() == ".pth":
            payload = torch.load(source, map_location="cpu", weights_only=False)
            torch.save(replace_object(payload), target)
        elif source.suffix.lower() in TEXT_SUFFIXES:
            target.write_text(replace_text(source.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(source, target)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def role(path: Path) -> str:
    rel = path.relative_to(TARGET_ROOT).as_posix()
    if rel == "dqn_family_satellite_ground_manuscript.pdf":
        return "current_manuscript_pdf"
    if rel == "README.md":
        return "package_documentation"
    if "/results/" in f"/{rel}":
        return "locked_experiment_artifact"
    return "reproduction_source"


def rebuild_inventory() -> None:
    manifest = TARGET_ROOT / "MANIFEST.tsv"
    checksum = TARGET_ROOT / "SHA256SUMS.txt"
    files = []
    for path in TARGET_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(TARGET_ROOT).parts
        if ".git" in rel_parts or path in {manifest, checksum}:
            continue
        files.append(path)
    files.sort(key=lambda item: item.relative_to(TARGET_ROOT).as_posix())
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(("path", "bytes", "sha256", "role"))
        for path in files:
            writer.writerow((path.relative_to(TARGET_ROOT).as_posix(), path.stat().st_size,
                             digest(path), role(path)))
    checksum_files = files + [manifest]
    checksum_files.sort(key=lambda item: item.relative_to(TARGET_ROOT).as_posix())
    checksum.write_text("".join(
        f"{digest(path)}  {path.relative_to(TARGET_ROOT).as_posix()}\n"
        for path in checksum_files
    ), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    if args.inventory_only and args.source_only:
        parser.error("choose at most one partial mode")
    if not args.inventory_only:
        copy_source_files()
    if not args.inventory_only and not args.source_only:
        copy_results()
    rebuild_inventory()
