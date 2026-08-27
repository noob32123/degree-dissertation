# DQN-family satellite-ground scheduling study

The study compares six DQN-family objectives under matched architecture, replay,
real-interaction budget, optimizer, seeds, and held-out traces. It also compares
representative family members with myopic, heuristic, fixed, contextual-bandit,
and exact finite-horizon policies. Dueling heads, prioritized replay, multi-step
targets, noisy exploration, and distributional value learning remain outside
the study.

## Variants

- `standard_dqn`: factual Huber loss with the standard target-network maximum.
- `md_cbad_dqn`: the same factual loss plus all-action, within-state centered Bellman advantage distillation.
- `md_fullq_dqn`: the same factual loss plus uncentered all-action Bellman Q supervision.
- `md_immediate_advantage_dqn`: the same factual loss plus centered analytical immediate-cost supervision.
- `double_dqn`: online-network action selection with target-network evaluation.
- `double_cbad_dqn`: Double DQN plus the centered all-action Bellman auxiliary objective.
- `contextual_bandit`: the same learner and training budget with `gamma=0`, used as a one-step learned baseline.

The locked auxiliary weight is `lambda=0.3`. Every learned model receives 600 episodes x 64 steps = 38,400 real interactions, uniform one-step replay, one update per four interactions, and the same epsilon schedule. The observation has 24 coordinates: 15 task descriptors, normalized episode time, sine and cosine of the reset-level link phase, and six persistent resources. Full-action variants additionally evaluate three modeled one-step outcomes per eligible update; the model manifest records this unequal information and computation explicitly.

## Manuscript result entry point

```powershell
python -m md_cbad_dqn.reviewer_experiments all --seeds 800-819 --resume
python -m md_cbad_dqn.extended_revision --seeds 800-819 --stage all --resume
python -m md_cbad_dqn.transition_audit
python -m md_cbad_dqn.reviewer_reporting
python -m md_cbad_dqn.extended_reporting
matlab -batch "addpath(fullfile(pwd,'md_cbad_dqn')); plot_reviewer_results_matlab(pwd)"
```

The first command reproduces the primary 20-seed study. The second adds the
component controls, matched Double-DQN test, independent-seed bootstrap, and
planning horizons 1, 2, 4, and 6. The transition audit writes a fixed-seed
all-action equality check for the preview and executed one-step outcomes.

The state-complete results support a family-level interpretation rather than a
single winning algorithm: all six DQN objectives have lower mean cost than
MPC-4 in all five fully coupled regimes, while nominal DQN-family means span
only 77.66--78.40. Centered full-action versus standard DQN satisfies the full
interval-plus-Holm rule in three of five regimes, and its direct contrasts with
uncentered full-action Q and immediate-advantage supervision are not uniformly
supported.

## Results and validation

- `results/reviewer_revision_state_complete/seven_regimes_raw.csv`: trace-level source of truth.
- `results/reviewer_revision_state_complete/seven_regimes_seed_level.csv`: traces averaged within model seed.
- `results/reviewer_revision_state_complete/seven_regimes_paired_bootstrap.csv`: paired intervals, exact sign tests, Holm corrections, and leave-one-seed-out ranges.
- `results/reviewer_revision_state_complete/model_manifest.csv`: checkpoint hashes, budgets, modeled-outcome counts, optimizer updates, and wall time.
- `results/reviewer_revision_state_complete/validation.json`: finite-value, shape, load, row-count, checkpoint-count, source and artifact-hash checks.
- `results/reviewer_revision_state_complete/extended_ablation_inference.csv`: component and Double-DQN paired inference.
- `results/reviewer_revision_state_complete/primary_unpaired_seed_bootstrap.csv`: sensitivity analysis that ignores seed matching.
- `results/reviewer_revision_state_complete/planner_depth_summary.csv`: exact planning depth and runtime frontier.
- `results/reviewer_revision_state_complete/fixed_transition_audit.csv`: all-action preview-versus-execution example.

## Study design

It uses correlated synthetic data/workload primitives and derives heat, energy, latency,
and transmitted volume from them. It evaluates eight policies, including an
four-step perfect-forecast rolling planner that is exact only for its stated
finite-horizon objective, on 7 regimes x 20 model seeds
x 20 paired traces (22,400 raw rows), plus 12,800 sensitivity rows. The main
inference uses seed-level paired effects, exact sign tests, Holm adjustment,
bootstrap intervals, and leave-one-seed-out checks. Two additional 20-seed
CBAD sets test training-preview consequence scales of 0.85 and 1.15. The
primary quantitative figures remain MATLAB-only and use Arial throughout.
Second-round mechanism and planning additions are reported as LaTeX tables so
that no new plotting backend is introduced.
