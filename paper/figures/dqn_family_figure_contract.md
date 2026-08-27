Core conclusion:
All six DQN objectives have lower mean episode cost than MPC-4 in each of five fully coupled synthetic benchmark regimes, with joint seed-block inference supporting all 30 contrasts.

Results-level question:
Does the DQN-family result remain favorable for every objective and regime when uncertainty is evaluated directly against MPC-4?

Figure archetype:
Quantitative grid with a compact study-design strip and a maximum-statistic summary.

Target journal/output:
Nature-leaning double-column figure; editable PDF/SVG plus 600-dpi TIFF/PNG.

Backend:
Python (matplotlib).

Final size:
183 mm by approximately 112 mm.

Panel map:
  a: synthetic soft-constrained benchmark, comparator set, and paired evaluation unit.
  b: 30 DQN-minus-MPC-4 mean episode-cost differences.
  c: least-favorable DQN objective within each regime and across all 30 contrasts.

Evidence hierarchy:
  hero evidence: complete 5-by-6 matrix of paired mean differences.
  validation evidence: maximum-statistic intervals and simultaneous upper bounds.
  controls/robustness: correlation-preserving joint bootstrap and Holm-adjusted sign tests.

Statistics needed:
Twenty independent model-seed blocks; 20 shared held-out traces averaged within each block; 10,000 joint paired bootstrap resamples; exact two-sided sign tests with Holm correction across 30 contrasts; family-wise simultaneous 95% upper bound.

Source data needed:
dqn_vs_mpc_inference.csv and dqn_vs_mpc_family_inference.csv.

Image-integrity notes:
Deterministic vector drawing only; no generative imagery and no image adjustment.

Reviewer risk:
The figure supports only the internally consistent synthetic, soft-constrained benchmark and does not establish hard operational feasibility or superiority to unimplemented stronger baselines.
