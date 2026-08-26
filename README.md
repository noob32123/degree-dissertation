# MD-CBAD-DQN satellite-ground scheduling

This repository accompanies **MD-CBAD-DQN: Model-Driven Counterfactual Bellman Advantage Distillation for Long-Term Satellite-Ground Task Scheduling**.

- `md_cbad_dqn/` contains the independent pure-DQN implementation, locked models, seven-regime data, statistical analysis, tests, a MATLAB figure generator, and a Python LaTeX-table generator.
- `paper/` contains the single-column English manuscript and final PDF.
- `wasted/` preserves superseded one-step code, unsuccessful historical studies, smoke runs, sweeps, and the previous paper version. Nothing was deleted during the restructure.

Quick validation:

```powershell
conda run --no-capture-output -n yolo python -m unittest md_cbad_dqn.tests.test_core -v
conda run --no-capture-output -n yolo python -m md_cbad_dqn.validate
```

Reproduce the reviewer-revision physical-consistency study and manuscript assets:

```powershell
conda run --no-capture-output -n yolo python -m md_cbad_dqn.reviewer_experiments all --resume
conda run --no-capture-output -n yolo python -m md_cbad_dqn.reviewer_reporting
matlab -batch "addpath(fullfile(pwd,'md_cbad_dqn')); plot_reviewer_results_matlab(pwd)"
```

The revision adds a correlated physical generator, a side-effect-free exact
four-step receding-horizon comparator, per-episode cost/energy/latency logs,
and eight prespecified parameter-sensitivity profiles. MATLAB exclusively
generates quantitative figures. Python reporting generates only LaTeX tables
and macros and cannot overwrite the MATLAB exports.
