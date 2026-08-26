# MD-CBAD-DQN: method, evidence, and novelty boundary

## Method

MD-CBAD-DQN retains the original 21-input `QNetwork`, uniform replay,
single-step transitions, epsilon-greedy exploration, optimizer, target update
cadence, gradient clipping, and the standard DQN target.  It does not use
Double DQN, Dueling, PER, n-step return, Noisy Networks, or distributional RL.

For the factual action, the unchanged TD target is

\[
y_t=r_t+\gamma(1-d_t)\max_b Q_{\text{target}}(s_{t+1},b).
\]

The side-effect-free environment preview provides the exact one-step cost
\(c_{t,a}\) and post-action resource vector \(z'_{t,a}\) for every action.
The next task descriptor \(x_{t+1}\) is exogenous and action-independent, so
after observing the real transition the exact counterfactual next states are

\[
\tilde{s}'_{t,a}=[x_{t+1},z'_{t,a}],
\qquad
\tilde y_{t,a}=-c_{t,a}+\gamma(1-d_t)
\max_b Q_{\text{target}}(\tilde{s}'_{t,a},b).
\]

CBAD removes the common state-value offset before distillation:

\[
\hat A_{t,a}=Q(s_t,a)-\frac{1}{3}\sum_b Q(s_t,b),
\qquad
\tilde A_{t,a}=\tilde y_{t,a}-\frac{1}{3}\sum_b\tilde y_{t,b}.
\]

The only algorithmic treatment is

\[
L=L_{\mathrm{DQN}}+\lambda\,
\operatorname{Huber}(\hat A,\tilde A).
\]

Calibration on model seeds 700--703 selected \(\lambda=0.3\) from
\(\{0.1,0.3,1,3\}\).  Confirmation used untouched seeds 800--804.  Every
model used 600 episodes × 64 real environment steps and 20 held-out traces per
scenario.  Inference uses only the original Q network and does not call the
preview.

## Confirmatory results

Lower cost is better.  Intervals are fixed-seed, 10,000-resample paired
bootstrap intervals over five independently trained model seeds after first
averaging each seed's 20 traces.

| Scenario | CBAD mean | Standard DQN mean | Difference | 95% interval | Improvement |
|---|---:|---:|---:|---:|---:|
| nominal | 324.034 | 329.215 | -5.181 | [-10.063, -2.389] | 1.57% |
| burst | 345.093 | 350.397 | -5.303 | [-10.392, -2.513] | 1.51% |
| link_limited | 431.266 | 444.382 | -13.116 | [-22.918, -3.263] | 2.95% |
| energy_limited | 358.621 | 364.016 | -5.395 | [-9.692, -2.468] | 1.48% |
| thermal_stress | 345.473 | 351.031 | -5.558 | [-10.734, -2.532] | 1.58% |

The same model and trace seeds were also used to retrain the repository's
existing MD-DQN-RSF comparator:

| Scenario | CBAD mean | MD-DQN-RSF mean | Difference | 95% interval | Improvement |
|---|---:|---:|---:|---:|---:|
| nominal | 324.034 | 338.151 | -14.117 | [-36.956, -1.619] | 4.17% |
| burst | 345.093 | 363.950 | -18.856 | [-49.800, -2.330] | 5.18% |
| link_limited | 431.266 | 457.573 | -26.307 | [-46.496, -12.066] | 5.75% |
| energy_limited | 358.621 | 371.663 | -13.042 | [-34.031, -0.631] | 3.51% |
| thermal_stress | 345.473 | 364.397 | -18.925 | [-49.862, -2.611] | 5.19% |

Thus both prespecified all-five-scenario criteria pass.

## Same-seed component ablation

The component ablation uses the same model seeds 800--804, the same 20 test
traces per seed, and the same auxiliary weight \(\lambda=0.3\).  The three
policies differ only as follows:

1. `standard_dqn`: factual TD loss only;
2. `md_cfba_dqn`: adds absolute full-action counterfactual Bellman regression;
3. `md_cbad_dqn`: replaces absolute regression with within-state centered
   counterfactual advantage distillation.

| Scenario | CFBA − standard | 95% interval | CBAD − CFBA | 95% interval |
|---|---:|---:|---:|---:|
| nominal | -4.498 | [-8.622, -1.975] | -0.683 | [-1.720, 0.354] |
| burst | -4.575 | [-9.537, -1.172] | -0.729 | [-1.523, 0.163] |
| link_limited | -9.783 | [-17.318, -2.286] | -3.333 | [-6.203, -0.462] |
| energy_limited | -4.967 | [-8.807, -2.678] | -0.428 | [-1.467, 0.611] |
| thermal_stress | -4.759 | [-9.828, -1.246] | -0.799 | [-1.757, 0.198] |

Absolute counterfactual Bellman augmentation is therefore independently
significant in all five scenarios.  Centering further lowers the mean in all
five scenarios and has a statistically resolved additional contribution in
`link_limited`; its separate intervals cross zero in the other four scenarios.
The evidence supports centering as a targeted improvement for coupled link
bottlenecks, not a claim of an independently significant gain everywhere.

## Novelty boundary

A literature search completed on 2026-08-26 found established neighboring
ideas, so an absolute "no prior work" claim would not be defensible:

- Dyna-style methods learn from model-generated experience; for example,
  [Switch-Based Active Deep Dyna-Q](https://doi.org/10.1609/aaai.v33i01.33017289).
- [Counterfactual-based data augmentation](https://arxiv.org/abs/2012.09092)
  uses structural causal models to generate alternative-treatment transitions
  and applies Q-learning to the augmented data.
- [Counterfactual Credit Assignment](https://proceedings.mlr.press/v139/mesnard21a.html)
  learns future-conditioned baselines/critics for lower-variance model-free
  policy gradients.
- [Learning Dynamics and Generalization in Reinforcement Learning](https://proceedings.mlr.press/v162/lyle22a.html)
  studies all-action value distillation from a separately pretrained teacher.
- [Distilling Policy Distillation](https://proceedings.mlr.press/v89/czarnecki19a.html)
  analyzes policy/value distillation objectives broadly.

Within that search, no paper was found that combines all of the following:

1. an exact factorization into an action-independent exogenous next task and
   action-dependent resource transition;
2. one factual standard-DQN transition plus simultaneous Bellman targets for
   every unexecuted discrete action;
3. within-state centering of both predicted Q values and counterfactual
   Bellman targets;
4. an auxiliary advantage-gap loss on an otherwise unchanged pure-DQN
   backbone, with no additional inference input or model rollout.

The defensible claim is therefore that **the components have precedents, but
their specific CBAD composition and its use for coupled satellite resource
scheduling appear to be rarely proposed or not directly reported in the
searched literature**.  A publication should use that qualified wording and
include a broader systematic review before claiming first authorship.

## Reproduction

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_cbad_study.py --stage all --output H:\degree-dissertation\md_dqn_rsf\outputs_cbad_study --resume
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\compare_cbad_rsf.py --output H:\degree-dissertation\md_dqn_rsf\outputs_cbad_study --resume
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\compare_cbad_ablation.py --output H:\degree-dissertation\md_dqn_rsf\outputs_cbad_study --resume
H:\anaconda\envs\yolo\python.exe -m unittest -v test_crgr.py
```
