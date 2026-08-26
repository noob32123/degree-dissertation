# Superseded and unsuccessful work

This directory preserves historical material moved during the MD-CBAD-DQN restructure. Files were moved, not deleted.

- `legacy_one_step/`: original one-step scripts, datasets, CSV evaluations, checkpoints, and baseline directories.
- `rsf/`: reset/selective-update/replay-flush code, outputs, figures, and patent material.
- `failed_methods/crgr/`: counterfactual resource-divergence gated ranking experiments.
- `failed_methods/cpsr/`: counterfactual preference self-regularization experiments.
- `failed_methods/cfba_exploratory/`: early CFBA calibration/confirmation runs that predate the locked CBAD ablation.
- `legacy_cbad_dependent_implementation/`: the original CBAD files retained only because they imported the failed-method inheritance chain; the clean implementation is in `md_cbad_dqn/`.
- `smoke_and_sweeps/`: smoke tests, budget sweeps, partial outputs, and sweep scripts.
- `old_paper_rsf_version/`: the complete previous IEEE/RSF manuscript, figures, source assets, and build products.

The clean repository does not import anything from this directory.
