# MD-DQN-RSF sequential experiments

## Successful pure-DQN CBAD improvement

`MD-CBAD-DQN` is the successful follow-up method.  It adds counterfactual
Bellman advantage distillation to the unchanged standard-DQN backbone.  The
locked configuration (`advantage_lambda=0.3`) passed the five-scenario
confirmatory criterion against both standard DQN and the existing
MD-DQN-RSF.  Relative to RSF, paired mean cost fell by 3.51%--5.75%, with all
five 95% paired-bootstrap interval upper bounds below zero.

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_cbad_study.py --stage all --output H:\degree-dissertation\md_dqn_rsf\outputs_cbad_study --resume
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\compare_cbad_rsf.py --output H:\degree-dissertation\md_dqn_rsf\outputs_cbad_study --resume
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\compare_cbad_ablation.py --output H:\degree-dissertation\md_dqn_rsf\outputs_cbad_study --resume
```

See `CBAD_METHOD_AND_RESULTS.md` for the equations, direct RSF comparison,
same-seed standard/CFBA/CBAD component ablation, novelty boundary, and exact
statistical results.

## Pure-DQN CRGR study

The new `MD-CRGR-DQN` study is intentionally built on the unchanged standard
DQN backbone.  Its only treatment is a training-time counterfactual
resource-divergence-gated action-ranking loss; it does not use Double DQN,
dueling networks, prioritized replay, multi-step targets, noisy networks, or
distributional value learning.

Run and verify the leakage-resistant calibration/confirmation experiment with:

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_crgr_study.py --stage all --resume --episodes 600 --horizon 64 --calibration-seeds 4 --confirmatory-seeds 5 --test-traces 20 --output H:\degree-dissertation\md_dqn_rsf\outputs_crgr_confirmatory
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\verify_crgr_archive.py --output H:\degree-dissertation\md_dqn_rsf\outputs_crgr_confirmatory --reference-models H:\degree-dissertation\md_dqn_rsf\outputs_archive_final_v1\models --report H:\degree-dissertation\md_dqn_rsf\outputs_crgr_confirmatory\verification.json
```

The locked configuration (`ranking_lambda=1.0`, `gate_tau=0.08`) significantly
reduces paired total cost versus standard DQN in nominal, burst,
energy-limited, and thermal-stress evaluation.  It does not improve the
link-limited setting, so the prespecified all-five-scenario success criterion
is false.  See `CRGR_NOVELTY_AND_EXPERIMENT.md` for the exact method, novelty
boundary, statistics, and interpretation.

This directory is independent of the legacy one-step scripts. It implements a
64-step satellite scheduling environment with paired exogenous traces, an
explicit immediate-cost model, dynamic resource transitions, analytical and
heuristic baselines, standard DQN, and the R/RS/RSF ablations.

Run on the remote Windows server with:

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_experiments.py --smoke --output H:\degree-dissertation\md_dqn_rsf\outputs_smoke
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_experiments.py --episodes 600 --horizon 64 --seeds 5 --test-traces 20 --output H:\degree-dissertation\md_dqn_rsf\outputs
```

For the archived rerun that saves every learned model and can resume after an
SSH interruption, use:

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_experiments.py --resume --episodes 600 --horizon 64 --seeds 5 --test-traces 20 --output H:\degree-dissertation\md_dqn_rsf\outputs_archive_final_v1
```

The 25 learned checkpoints are written to
`outputs_archive_final_v1\models`.  The filename identifies the policy and
independent model seed, for example `standard_dqn_seed_003.pth`.  Each
checkpoint contains the online and target networks, optimizer state, complete
agent configuration, training step count, epsilon/RSF state, and software
version.  `models\model_manifest.csv` records SHA-256 hashes and archive
metadata.  Verify every checkpoint with:

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\verify_model_archive.py --models H:\degree-dissertation\md_dqn_rsf\outputs_archive_final_v1\models --report H:\degree-dissertation\md_dqn_rsf\outputs_archive_final_v1\model_verification.json
```

The independent two-stage RSF study uses `run_rsf_confirmatory.py`.  Its
locked confirmatory models are stored under
`outputs_rsf_confirmatory\models\confirmatory`; calibration-only models are
kept separate under `models\calibration` and must not be presented as
confirmatory evidence.

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_rsf_confirmatory.py --resume --episodes 600 --horizon 64 --calibration-seeds 4 --confirmatory-seeds 10 --test-traces 20 --output H:\degree-dissertation\md_dqn_rsf\outputs_rsf_confirmatory
```

The locked confirmatory archive contains 40 checkpoints (four DQN variants
times ten independent seeds).  The full MD-DQN-RSF variant has a lower mean
cost than standard DQN by 1.1324 units (0.3521%), but its paired 95% interval
[-3.0944, 1.0017] crosses zero.  This run therefore does not support a claim
of a statistically stable full-RSF advantage.  The reset-only ablation has a
paired mean difference of -1.2930 with a 95% interval [-2.4431, -0.2548].
All ten prespecified confirmatory seeds are retained.

See `模型与实验归档说明.md` for exact local/remote paths, checkpoint loading,
output-to-script mapping, and the interpretation boundary.

The main experiment uses 5 independent model seeds and 20 held-out task traces
per seed. Policies within a seed receive common traces, whereas different model
seeds receive disjoint traces. Inference first averages traces within each seed,
then uses the independent seed as the experimental unit. Raw episode-level
results are retained for paired analysis.

The 100,000-series trace seeds are reserved for calibration/validation. Final
evaluation uses the disjoint 500,000-series trace seeds to prevent leakage.
