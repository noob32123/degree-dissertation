# Experiment protocol and audit trail

## Scientific question

Does a value-learning policy improve cumulative operational cost when current
satellite--ground scheduling actions change resources available to later tasks?
The immediate analytical argmin is the primary control. At zero action-dependent
coupling it is expected to be optimal; reinforcement learning is justified only
by gains that emerge as coupling is introduced.

## Data partitions

- Training seed for episode `k` of model seed `m`: `1_000_000*m + k`.
- Calibration/validation traces: 100,000-series seeds. These were used to set
  the episode budget and exploration schedule.
- Final test traces: `500_000 + 1_000*m + i`, where `i=0,...,19`.
- Policies within a model seed share traces. Model seeds have disjoint traces.
- The first attempted formal run was stopped before completion when a reused
  calibration trace namespace was detected; it is excluded from all reporting.

## Independent units and summaries

Five independently initialized training seeds are the inferential units. The 20
test traces are averaged within each seed. Main values are seed-level mean and
standard deviation. The primary paired difference uses 10,000 seed-level
bootstrap resamples with fixed seed 20260819. Trace rows remain available for
auditing but are not treated as independent replicates.

## Original result command

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_experiments.py --episodes 600 --horizon 64 --seeds 5 --test-traces 20 --output H:\degree-dissertation\md_dqn_rsf\outputs_final_v2
```

## Model-persistent reproducibility rerun

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_experiments.py --resume --episodes 600 --horizon 64 --seeds 5 --test-traces 20 --output H:\degree-dissertation\md_dqn_rsf\outputs_archive_final_v1
```

This second command repeats the full experimental matrix and additionally
saves every learned model. Its result CSV files reproduce the original final
run byte for byte.

## Required archive before submission

- environment, agent, training, evaluation, and plotting source;
- exact Conda package export and GPU/software metadata;
- raw trace-level evaluation CSV and seed-level summaries;
- training curves and figure source data;
- fixed seeds, this protocol, and a file manifest with checksums;
- a README/data dictionary and an open licence;
- a durable repository record and DOI (not yet assigned; do not invent one).

## Model archive produced by the reproducibility rerun

The full five-seed experiment was rerun with checkpoint persistence at
`outputs_archive_final_v1`.  Its learned-model archive is
`outputs_archive_final_v1/models` and contains 25 checkpoints: five policies
(`contextual_bandit`, `standard_dqn`, `dqn_r`, `dqn_rs`, and `md_dqn_rsf`)
for each of five independent model seeds.  Non-learning baselines have no
model file because their actions are computed directly from fixed rules.

Each checkpoint contains online and target network weights, optimizer state,
the complete `AgentConfig`, training progress and RSF event state.  The file
`models/model_manifest.csv` provides SHA-256 hashes.  The independent verifier
loads every online state dictionary strictly into the declared 21-to-3
network and checks for a finite three-action output; its report is
`model_verification.json`.

The archived CSV outputs are byte-for-byte identical to the prespecified
`outputs_final_v2` results.  Thus model persistence did not change the random
sequence, training result, evaluation result, or manuscript statistics.

## Independent RSF calibration and confirmation

The supplementary RSF study uses `run_rsf_confirmatory.py` and separates
configuration selection from final assessment. Six RSF schedules are compared
only on four calibration seeds (100--103) and 700,000-series traces. The locked
configuration is `c4_early_moderate`: reset fraction 0.35, reset epsilon 0.50,
selective-update factor 2.5, and replay-buffer flush fraction 0.85.

The locked configuration is then evaluated without further tuning on ten new
model seeds (200--209) and disjoint 900,000-series traces. All ten seeds and 20
traces per seed are retained. The confirmatory archive contains 40 checkpoints:
standard DQN, DQN-R, DQN-RS, and MD-DQN-RSF for every seed.

Relative to standard DQN, full MD-DQN-RSF reduces mean total cost by 1.1324
units (0.3521%), but the paired 95% interval [-3.0944, 1.0017] includes zero.
Accordingly, the result may be described as a small mean improvement, not as a
stable or statistically established advantage. The reset-only ablation has a
mean difference of -1.2930 and paired 95% interval [-2.4431, -0.2548]. This
distinction must be preserved in the manuscript and figure captions.

## Scope limitations

The task traces and transition dynamics are synthetic. Transition coefficients
are normalized simulator parameters rather than telemetry-calibrated physical
models. Ground-server computation is set to zero. The experiment is a
single-satellite, single-link, three-action proof of concept and is not evidence
of safe flight readiness or constellation-scale performance.
