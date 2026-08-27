# MD-CBAD-DQN

The implementation deliberately uses a standard DQN backbone. It does not use Double DQN, dueling heads, prioritized replay, multi-step targets, noisy exploration, or distributional value learning.

## Variants

- `standard_dqn`: factual Huber loss with the standard target-network maximum.
- `md_cbad_dqn`: the same factual loss plus all-action, within-state centered Bellman advantage distillation.
- `contextual_bandit`: the same learner and training budget with `gamma=0`, used as a one-step learned baseline.

The locked auxiliary weight is `lambda=0.3`. Every DQN/CBAD model receives 600 episodes x 64 steps = 38,400 real interactions, uniform one-step replay, one update per four interactions, and the same epsilon schedule.

## Manuscript result entry point

```powershell
python -m md_cbad_dqn.reviewer_experiments all --seeds 800-819 --resume
python -m md_cbad_dqn.reviewer_reporting
matlab -batch "addpath(fullfile(pwd,'md_cbad_dqn')); plot_reviewer_results_matlab(pwd)"
```

This is the unique entry point for the reported 20-seed reviewer-revision study.
It writes 22,400 seven-regime rows, 12,800 sensitivity rows, 8,000 preview-error
rows, checkpoint manifests, SHA-256 hashes, and an end-to-end validation file.

## Results and validation

- `results/reviewer_revision/seven_regimes_raw.csv`: trace-level source of truth.
- `results/reviewer_revision/seven_regimes_seed_level.csv`: traces averaged within model seed.
- `results/reviewer_revision/seven_regimes_paired_bootstrap.csv`: paired intervals, exact sign tests, Holm corrections, and leave-one-seed-out ranges.
- `results/reviewer_revision/model_manifest.csv`: checkpoint hashes and budgets.
- `results/reviewer_revision/validation.json`: finite-value, shape, load, row-count, checkpoint-count, and artifact-hash checks.

## Study design

It uses correlated data/workload primitives and derives heat, energy, latency,
and transmitted volume from them. It evaluates eight policies, including an
four-step perfect-forecast rolling planner that is exact only for its stated
finite-horizon objective, on 7 regimes x 20 model seeds
x 20 paired traces (22,400 raw rows), plus 12,800 sensitivity rows. The main
inference uses seed-level paired effects, exact sign tests, Holm adjustment,
bootstrap intervals, and leave-one-seed-out checks. Two additional 20-seed
CBAD sets test training-preview consequence scales of 0.85 and 1.15. Quantitative
figures remain MATLAB-only and use Arial throughout.
