## Reviewer 3

- **Overall assessment**

The manuscript presents a carefully bounded simulator-level study of full-action Bellman supervision for satellite-ground scheduling. The matched training design, explicit implementation, seed-level inference, component controls, validation records, and unusually candid limitations are substantial strengths. The graphics and main narrative are generally readable.

The current evidence supports a narrow result within the specified synthetic objective. It does not yet establish outstanding scientific importance or compelling interdisciplinary reach. Several secondary interpretations also exceed the manuscript's own multiplicity-adjusted evidence. The report therefore places greatest weight on broad readership, practical interpretability, and claim calibration.

- **Who would be interested in the results, and why**

Researchers in reinforcement learning, model-assisted control, satellite edge computing, and sequential resource allocation may value the controlled demonstration that analytically available outcomes for unexecuted actions can provide useful training supervision without deployment-time preview. Readers beyond these groups could be interested in the general question of exploiting counterfactual action models. That general relevance is presently more prospective than demonstrated because all evidence comes from one three-action synthetic scheduling environment.

- **Major strengths**

The manuscript defines the simulator and training objective with considerable transparency. Standard DQN and CBAD are closely matched, and the supplied implementation preserves the factual Bellman loss while adding the stated auxiliary path. The authors provide independent model-seed blocks, shared held-out traces, leave-one-seed-out summaries, paired and unpaired sensitivity analyses, component controls, a Double-DQN pair, planning-depth comparisons, preview-error tests, source hashes, and machine-readable validation files.

The graphical overview and mechanism figure communicate the training architecture effectively. The manuscript also states important negative findings. Centering is not isolated as necessary, the Double-DQN transfer is directional after multiplicity control, the simulator is not mission-fitted, and neither learned policy is hard-feasible. This restraint materially improves trust.

- **Major Concerns**

### R3-M1

**Severity** Major

**Blocking** No

**Axis** Interdisciplinary readership

**Claim pointer** The full-action Bellman auxiliary design is presented as a scientific contribution with relevance beyond the immediate satellite scheduling task.

**Evidence pointer** Introduction, contribution items 2 and 3; Related Work and Novelty Positioning; Table 6; Discussion and Limitations; Conclusion.

**Concern** The transferable conclusion is not yet separated convincingly from a field-specific simulator result. The only empirical setting has three actions, a deterministic analytical preview, one satellite, one ground path, and a hand-defined objective. The uncentered full-action target matches CBAD within uncertainty, so the supported algorithmic idea is narrower than the named centered method. No distinct task class, structural analysis, or benchmark shows when this idea should matter outside this simulator.

**Why it matters** Technical papers need a clear account of significant impact on a community of researchers. Nonspecialists can understand the mechanism, but the manuscript does not show why the observed result changes reinforcement learning, control, or autonomous-system practice beyond this constructed setting.

**Resolution test** State a precise transferable proposition about full-action Bellman supervision and test it in at least one meaningfully distinct decision problem, or provide analysis that identifies the conditions under which it should help. Compare that proposition explicitly with the closest model-assisted and multi-action objectives. If this evidence is unavailable, narrow the significance framing to a satellite-simulator case study.

### R3-M2

**Severity** Major

**Blocking** No

**Axis** Scientific importance

**Claim pointer** CBAD reduces composite cost across five fully coupled regimes and offers an engineering-relevant scheduling improvement.

**Evidence pointer** Abstract; Equations 4 and 13; Tables 3, 4, and 8; Section 7.1; Discussion and Limitations.

**Concern** The headline reduction is 0.87% to 1.72% in a dimensionless composite objective whose weights are fixed simulator assumptions. The engineering decomposition shows modest latency and modeled-energy changes, increased transmitted data, and zero remaining energy for both principal policies. Sensitivity tests vary physical inputs but not the utility weights that determine the reported ranking. A broad reader therefore cannot judge whether the improvement is operationally meaningful or stable under plausible mission priorities.

**Why it matters** Statistical separation in an artificial scalar objective is not equivalent to engineering importance. The lack of objective-weight sensitivity and hard-feasibility analysis limits the significance of the central performance result even though its simulator-level direction is well documented.

**Resolution test** Evaluate ranking and effect size across justified utility-weight profiles, report outcomes against interpretable operational thresholds, and include a constrained or action-masked analysis if deployability remains part of the motivation. Alternatively, frame the contribution strictly as optimization behavior under one declared synthetic objective and remove broader engineering implications.

### R3-M3

**Severity** Major

**Blocking** No

**Axis** Technical soundness

**Claim pointer** Component controls identify Bellman bootstrapping as the supported distinction and localize the contribution to full-action Bellman supervision.

**Evidence pointer** Section 7.2 and its heading; Table 6; Conclusion; `extended_ablation_inference.csv`, rows comparing CBAD with the immediate-advantage auxiliary.

**Concern** The direct CBAD versus immediate-advantage contrast has a nominal paired interval below zero, but its Holm-adjusted sign-test value is 0.0828 in both the nominal and link-limited regimes. It meets the package's stated support rule in only three of five fully coupled regimes. Table 6 omits these adjusted values, while the prose uses stronger attribution language than the complete inferential record warrants.

**Why it matters** The central mechanistic interpretation depends on distinguishing bootstrapped all-action targets from immediate multi-action labels. Readers should not infer uniform confirmatory support from intervals alone when the manuscript prespecifies an additional multiplicity-adjusted criterion.

**Resolution test** Report the direct multiplicity-adjusted contrasts for every regime and describe the result as a consistent pattern with partial confirmatory support unless further independent evidence satisfies the prespecified rule across the claimed scope.

### R3-M4

**Severity** Major

**Blocking** No

**Axis** Claim moderation

**Claim pointer** Moderate preview error preserves a bounded benefit, and the reported advantage survives the fixed perturbation.

**Evidence pointer** Section 7.6 heading and final sentence; Table 10; `preview_mismatch_inference.csv`.

**Concern** Under the 1.15 preview scale, paired intervals remain below zero, but Holm-adjusted sign-test values are 0.1656 in nominal, burst, and link-limited regimes and 0.2632 in thermal stress. Only the energy-limited result satisfies the stated adjusted criterion. The section heading and survival language treat directional interval evidence as though robustness were confirmed across all five regimes.

**Why it matters** This wording obscures an important dependence on how inferential support is defined. Nonspecialist readers are particularly likely to read “preserves” and “survives” as confirmation rather than a mixed statistical result.

**Resolution test** Label the 1.15 results as directional sensitivity evidence, display which regimes satisfy the complete prespecified criterion, and reserve robustness language for evidence that passes that criterion. A new independent replication could support the stronger claim.

- **Minor Comments**

### R3-m1

**Severity** Minor

**Axis** Readability for nonspecialists

**Affected element** Abstract.

**Evidence pointer** Abstract, page 1.

**Issue** The abstract compresses five result families, several inferential qualifications, planning timings, and a safety limitation into one dense paragraph. The practical meaning of composite cost is not explained.

**Required correction** Retain the central comparison and principal limitation, but replace secondary statistics with one plain-language sentence explaining what the objective measures and why the observed change matters.

### R3-m2

**Severity** Minor

**Axis** Claim moderation

**Affected element** Physical-consistency terminology.

**Evidence pointer** Section 3.2; Figure 3; Section 7.1 heading; Discussion and Limitations.

**Issue** Repeated phrases such as “physical consistency” and “physically coupled generator” can imply physical validation even though the evidence establishes internal consistency among synthetic variables. The later caveats are accurate but arrive after the stronger framing.

**Required correction** Prefer “internally consistent synthetic generator” or equivalent wording in prominent headings and early summaries. Reserve “physical” for quantities or constraints with external validation.

### R3-m3

**Severity** Minor

**Axis** Figures and tables

**Affected element** Action-mix interpretation.

**Evidence pointer** Section 7.7 and Figure 10.

**Issue** Figure 10 shows only CBAD means without uncertainty or a standard-DQN comparator. It supports variation across regimes but not a method-specific adaptation claim.

**Required correction** Retitle the section to describe variation in CBAD action fractions, or add uncertainty and a matched comparator if adaptation relative to another policy is intended.

### R3-m4

**Severity** Minor

**Axis** Writing clarity

**Affected element** Four-step planner runtime.

**Evidence pointer** Section 7.1, page 17; Table 7, page 18.

**Issue** The text reports 4.81 ms per decision for MPC-4, whereas Table 7 reports 4.70 ms for the four-step planner. The manuscript does not explain whether these come from different timing passes.

**Required correction** Reconcile the values or state the distinct measurement sets and use consistent labels.

### R3-m5

**Severity** Minor

**Axis** Reproducibility

**Affected element** Complete simulator specification.

**Evidence pointer** Table 1; Section 3.3; `environment.py`, function `_generate_physics_tasks`.

**Issue** The manuscript states that the subsection generates all 15 task coordinates, but it does not give the implemented formula for the squared co-location count, even though this descriptor contributes to onboard immediate cost.

**Required correction** Define the co-location-count construction and explain its engineering interpretation, or remove it if it is only an arbitrary surrogate.

- **Technical failings that need to be addressed before the case is established**

No `Blocking Yes` technical failing is identified because the manuscript explicitly limits its central conclusion to the defined simulator. R3-M3 and R3-M4 require substantive correction before the mechanistic and preview-robustness subclaims are established at their current scope. R3-M2 must be addressed before broader engineering importance can be inferred.

- **Assessment against Nature-style criteria**

**Originality** The evaluated full-action auxiliary design is plausibly original in this application, but its distinction from the closest model-assisted and multi-action formulations remains too qualitative. The null separation between centered and uncentered targets narrows the contribution.

**Scientific importance** The study is methodologically careful, but a roughly 1% improvement in one synthetic, hand-weighted objective does not yet establish outstanding importance.

**Interdisciplinary readership** Reinforcement learning, autonomous systems, satellite computing, and model-based control communities could find the idea useful. Evidence for interest beyond these neighboring areas is currently limited.

**Technical soundness** The primary CBAD versus standard-DQN comparison is well controlled and traceable. The principal weaknesses concern external and decision validity, omitted utility-weight sensitivity, and overstatement of secondary multiplicity-adjusted findings.

**Readability for nonspecialists** The manuscript has strong visual structure, concise prose, and clear limitations. Accessibility is reduced by dense abstract reporting, specialist terminology, and insufficient interpretation of the composite objective and its operational effect size.

- **Recommendation posture**

Promising and technically credible as a bounded simulator study, but the broad-interest and outstanding-importance case remains underdeveloped. Substantive revision is needed to calibrate the mechanistic and preview-robustness claims and to make the decision relevance legible to readers outside the immediate specialty.
