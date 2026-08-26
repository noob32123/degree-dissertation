# MD-CBAD-DQN

The implementation deliberately uses a standard DQN backbone. It does not use Double DQN, dueling heads, prioritized replay, multi-step targets, noisy exploration, or distributional value learning.

## Variants

- `standard_dqn`: factual Huber loss with the standard target-network maximum.
- `md_cfba_dqn`: the same factual loss plus absolute counterfactual Bellman targets for the two unexecuted actions.
- `md_cbad_dqn`: the same factual loss plus all-action, within-state centered Bellman advantage distillation.
- `contextual_bandit`: the same learner and training budget with `gamma=0`, used as a one-step learned baseline.

The locked auxiliary weight is `lambda=0.3`. Every DQN/CFBA/CBAD model receives 600 episodes x 64 steps = 38,400 real interactions, uniform one-step replay, one update per four interactions, and the same epsilon schedule.

## Unified CLI

```powershell
python -m md_cbad_dqn.experiment calibration --resume
python -m md_cbad_dqn.experiment confirmatory --resume
python -m md_cbad_dqn.experiment ablation --resume
python -m md_cbad_dqn.experiment seven-scenarios --resume
python -m md_cbad_dqn.experiment all --resume
```

`seven-scenarios` evaluates static (`c=0`), reduced coupling (`c=0.5`), nominal, burst, link-limited, energy-limited, and thermal-stress regimes. It writes 5,600 raw rows for 7 regimes x 8 policies x 5 model seeds x 20 paired traces.

## Results and validation

- `results/seven_scenarios_raw.csv`: trace-level source of truth.
- `results/seven_scenarios_seed_level.csv`: traces averaged within model seed.
- `results/seven_scenarios_paired_bootstrap.csv`: fixed-seed 10,000-resample paired intervals.
- `results/model_manifest.csv`: checkpoint hashes and budgets.
- `validation.json`: locked-data, finite-value, shape, load, and budget checks.

Generate the quantitative manuscript figures exclusively with MATLAB:

```powershell
matlab -batch "addpath(fullfile(pwd,'md_cbad_dqn')); plot_results_matlab(pwd)"
```

This produces vector PDF/SVG files and 600-dpi TIFF files in
`figures_matlab/`, and synchronizes the PDF/SVG versions to `paper/figures/`.

Generate LaTeX result tables and macros with Python:

```powershell
python -m md_cbad_dqn.reporting
```

The Python reporting module does not draw or overwrite figures.

## Reviewer-revision physical study

The original locked results remain unchanged. The reviewer-response study is
written separately under `results/reviewer_revision/`:

```powershell
python -m md_cbad_dqn.reviewer_experiments all --resume
python -m md_cbad_dqn.reviewer_reporting
matlab -batch "addpath(fullfile(pwd,'md_cbad_dqn')); plot_reviewer_results_matlab(pwd)"
```

It uses correlated data/workload primitives and derives heat, energy, latency,
and transmitted volume from them. It evaluates nine policies, including an
exact four-step perfect-forecast rolling planner, on 7 regimes x 5 model seeds
x 20 paired traces (6,300 raw rows), plus 3,200 sensitivity rows. Quantitative
reviewer figures remain MATLAB-only and use Arial throughout.
