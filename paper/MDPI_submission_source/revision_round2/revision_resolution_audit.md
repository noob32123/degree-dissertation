# Revision resolution audit (internal/editor-facing; not reviewer-facing)

Decision type: Major Revision  
Audit date: 22 September 2026  
Redline baseline: `paper/MDPI_submission_source.zip!/MDPI_submission_source/manuscript.tex`  
Current clean source: `paper/MDPI_submission_source/manuscript.tex`

| ID | Concern | Verified manuscript action and evidence | Final clean-PDF location | Status |
|---|---|---|---|---|
| R1.1 | Limit claims to the clipped, soft-constraint benchmark and discuss hard constraints | Scope is delimited in the Abstract, Introduction, Discussion, limitations, and Conclusions; hard constraints are explained as changes to the feasible action set that may reverse the ordering | p. 1; p. 3; p. 23, Section 5.1; p. 24 | `VERIFIED_DONE` |
| R1.2 | Motivate six objectives and avoid causal claims under shared $\lambda=0.3$ | Six objectives are organized as matched design controls; Tables 7--8 and surrounding text explicitly describe fixed-coefficient implementation comparisons that do not factorially isolate centering or bootstrapping | p. 11, Section 3.4.1; pp. 17--18, Tables 7--8; p. 23 | `VERIFIED_DONE` |
| R1.3 | Discuss MILP/dynamic programming and add a lightweight baseline | Related Work discusses MILP, dynamic programming, PPO, and SAC; an eight-step greedy rollout was evaluated with the same perfect preview as MPC and separately corrected inference | pp. 2--3; pp. 12--13; pp. 20--21, Section 4.6 and Table 12; p. 23 | `VERIFIED_DONE` |
| R1.4 | Add discount-factor/training-length sensitivity and six-objective learning curves | Four discount factors, three training checkpoints, all six learning curves, 20 seeds, paired traces, bootstrap intervals, and separate Holm families are reported | p. 14, Section 3.4.5; pp. 19--20, Figures 6--7 | `VERIFIED_DONE` |
| R1.5 | Acknowledge that preview misspecification tested amplitude rather than structural error | Limitations distinguish uniform scaling from wrong thermal recurrence, actuator saturation, and state-dependent contact loss; future work specifies telemetry-calibrated and hardware-in-the-loop tests | pp. 22--23, Sections 5--5.2 | `VERIFIED_DONE` |
| R2.1 | Explain operational scheduling difficulties and hard versus soft constraints | Introduction covers model calibration, combinatorial growth, forecast dependence, and onboard decision budgets; operational hard-constraint consequences and non-transferability are explicit | pp. 2--3; p. 23, Section 5.1; p. 24 | `VERIFIED_DONE` |
| R2.2 | Address missing PPO/SAC/MILP/rolling-horizon comparators | A rolling greedy look-ahead baseline is added; PPO, SAC, MILP, and dynamic programming are discussed as unevaluated comparator frontiers; universal-optimality language is removed | pp. 2--3; pp. 20--21, Table 12; p. 23, Section 5.2 | `VERIFIED_DONE` through added baseline and explicit scope limitation |
| R2.3 | Do not infer module contributions from a shared auxiliary coefficient | Component comparisons are recast as descriptive; objective-specific tuning, gradient normalization, and factorial controls are listed as necessary future mechanism studies | p. 11; pp. 17--18; p. 23 | `VERIFIED_DONE` through claim moderation and limitation disclosure |
| R2.4 | Highlight perfect-preview information asymmetry and address forecast error | Methods and Results identify that only MPC and greedy rollout receive future tasks/link states; Discussion explains why an informative noisy-MPC test requires mission-calibrated forecast distributions | pp. 12--13; p. 16, Figure 5 caption; p. 21; p. 22 | `VERIFIED_DONE` through explicit information accounting and permitted discussion alternative |
| R3.1 | Justify MPC-4 and compare decision time on matched hardware | MPC-4 is justified through the planning-depth/computation trade-off; matched single-thread, batch-one, shared-state timing reports mean, median, and P95 for all policies | pp. 12--13; p. 18, Table 10; pp. 20--21, Table 12 | `VERIFIED_DONE` |
| R3.2 | Clarify parameter provenance and limitations of synthetic data | Methods now separates engineering-scale anchors, synthetic workload assumptions, and normalized accounting states; Discussion and Conclusions require telemetry, real-mission, and hardware-in-the-loop validation | p. 6, Section 3.1.2; p. 7, Table 3; pp. 23--24 | `VERIFIED_DONE` |

## Red-marking audit

- The original submission archive, rather than the intermediate `manuscript_pre_round2.tex` label alone, was used as the redline baseline; the two files were verified to have identical SHA-256 content.
- All substantive changed manuscript lines are enclosed by `\revised{}`, `revisedblock`, or `\revisedcaption`, except unchanged document-control commands and the retained title.
- Floating environments had reset the outer `revisedblock` color. Explicit red captions were therefore added for revised Table 10 and new Figures 6--7 and Table 12; the new Table 12 body now receives an explicit marked-mode red color.
- The parameter-provenance paragraph added for R3.2 is explicitly marked in red.
- Clean and marked manuscripts are generated from the same body source. The marked source differs only by the `\ShowRevisions` switch.

## Package readiness

All 11 reviewer comments have one complete response and inspectable manuscript evidence. No response relies on another reviewer's file, no result placeholder remains, and no unresolved author input is required. Package readiness: `ready_to_submit`.
