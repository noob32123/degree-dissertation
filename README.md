# Current DQN-family satellite-ground scheduling manuscript

This workspace contains the active materials for **A Statistically Supported DQN-Family Advantage in a Resource-Coupled Satellite-Ground Scheduling Benchmark**.

## Active package

- paper/source.tex is the authoritative manuscript source.
- paper/output/pdf/dqn_variants_satellite_ground_manuscript.pdf is the clean current PDF.
- paper/figures and paper/generated contain only the figures and generated LaTeX inputs retained for the current manuscript.
- md_cbad_dqn contains the active Python implementation, MATLAB figure generator, tests, reporting scripts and requirements.
- md_cbad_dqn/results/reviewer_revision_state_complete is the locked current result set, including 180 checkpoints, 180 training-curve files and 39 top-level result or validation files.
- md_cbad_dqn/figures_matlab/reviewer_revision_state_complete and md_cbad_dqn/tables/reviewer_revision_state_complete contain current generated scientific assets.
- paper/review contains the latest three blind reviews, the synthesis, and the current polishing and revision audits.
- CURRENT_VERSION_MANIFEST.md documents the complete active layout and key hashes.
- CURRENT_VERSION_SHA256SUMS.txt is the machine-readable checksum inventory for active research materials.

## Historical package

Superseded manuscripts, older result sets, smoke runs, unused figure iterations and build previews were moved without deletion to archive/history_before_current_2026-08-27. Original relative paths are preserved under that directory.

## Validation

Run from the repository root:

```powershell
H:\anaconda\envs\yolo\python.exe -m unittest md_cbad_dqn.tests.test_core -v
H:\anaconda\envs\yolo\python.exe -m md_cbad_dqn.reviewer_experiments validate --seeds 800-819
H:\anaconda\envs\yolo\python.exe -m md_cbad_dqn.reviewer_reporting
H:\anaconda\envs\yolo\python.exe -m md_cbad_dqn.extended_reporting
```

Compile the manuscript from paper with:

```powershell
H:\degree-dissertation\.tools\tectonic-env\Library\bin\tectonic.exe source.tex --outdir output\build_current --keep-logs
```
