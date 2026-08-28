# Reviewer 1

## Overall assessment

This is an unusually transparent and carefully scoped simulation study. The manuscript defines the synthetic environment, DQN variants, training budgets, held-out evaluation, uncertainty procedures, planning comparators, and limitations in substantial detail. The visible evidence supports a reproducible descriptive finding. Across the five fully coupled regimes, the reported means of all six DQN objectives are lower than those of the implemented non-DQN comparators. The smaller centered full-action effects are reported with seed-level paired analyses and appropriately cautious interpretation.

The central claim is not yet established at the strength implied by “DQN-family advantage.” The comparison with non-DQN methods lacks direct inferential support, and the comparator frontier does not include a matched long-horizon optimization or learning baseline. The engineering interpretation is further limited by an energy state that reaches zero while actions continue, a simulator whose utilities and dynamics lack independent physical calibration, and a validation envelope confined to variants of the same synthetic task. These limitations do not erase the reported benchmark ordering, but they materially restrict what that ordering demonstrates.

## Who would be interested and why

The study should interest researchers in reinforcement learning, model-assisted value learning, spacecraft autonomy, satellite edge computing, and resource-constrained scheduling. The full-action training interface is also relevant to control problems in which an analytical simulator can label unexecuted discrete actions. The manuscript may additionally interest reproducibility researchers because it connects equations, checkpoints, seed-level results, generated tables, and transition audits. Broader engineering interest will depend on validation under operational constraints and mission-derived data.

## Major strengths

- The simulator, state, transition, reward, action loads, and stochastic generator are specified in enough detail to permit close scrutiny.

- The manuscript clearly distinguishes a synthetic engineering envelope from a fitted flight distribution.

- Twenty independently trained model seeds and shared held-out traces are used without reported seed exclusion or replacement.

- The within-family inference treats trained model seeds as the independent units, reports paired intervals, sign tests, multiplicity adjustment, leave-one-seed-out ranges, and an unpaired sensitivity analysis.

- The paper separates the robust family-level ordering from the much smaller and scenario-dependent differences among DQN objectives.

- Training information and computation are reported explicitly. The manuscript acknowledges that equal real interactions do not imply equal modeled-information budgets.

- The planning-depth experiment and the explicit statements about soft constraints, perfect forecasts, and absent DQN latency measurements make important limitations visible.

## Major Concerns

### R1-M1

- **Concern ID** R1-M1
- **Severity** Major
- **Blocking** Yes
- **Axis** Technical soundness and statistical rigor
- **Claim pointer** The title, Abstract, Section 7, Discussion, and Conclusion describe a consistent DQN-family advantage because all 30 DQN objective-regime means are below the corresponding MPC-4 means.
- **Evidence pointer** Abstract; Section 6, Planning comparator, outcomes, and inference; Section 7, first Results subsection; Table 6; Table 9; Discussion; Conclusion
- **Concern** The central between-family result is based on ordering of means. The manuscript explicitly states that between-family inference remains descriptive because learned and deterministic methods express different sources of variation. The 30 objective-regime cells are also correlated because objectives share seeds and traces, and regimes are repeated evaluations rather than independent replications. Mean ordering alone does not quantify whether the DQN to MPC separation is robust to model-seed variability, held-out trace variability, or the family-level multiplicity created by several objectives and regimes.
- **Why it matters** “Advantage” is the principal claim and appears in the title. Without a direct estimand and uncertainty analysis for DQN versus the strongest comparator, the manuscript establishes descriptive ordering rather than a statistically supported family-level advantage.
- **Resolution test** Define a prespecified between-family estimand and report matched contrasts using the shared trace structure. A hierarchical or otherwise justified resampling procedure should propagate model-seed and held-out trace variation. Report effect sizes and uncertainty for the relevant DQN versus MPC comparisons, with an explicit multiplicity or family-level decision rule. If such inference is not supported, revise the title, Abstract, Results, and Conclusion to describe a consistent ordering of reported means rather than an established advantage.

### R1-M2

- **Concern ID** R1-M2
- **Severity** Major
- **Blocking** Yes
- **Axis** Technical soundness and experimental design
- **Claim pointer** The manuscript concludes that long-horizon DQN value learning is an effective strategy and that its family-level ordering persists as exact planning depth increases.
- **Evidence pointer** Section 2; Section 6, Design principles and Planning comparator, outcomes, and inference; Tables 6, 10, and 12; Section 7, Deeper exact planning improves cost; Discussion; Section 8.1
- **Concern** The non-DQN frontier consists mainly of myopic policies, a hand-specified threshold rule, a contextual bandit, and exact planners truncated at at most six steps. The DQN policies learn from 38,400 interactions and approximate consequences over a substantially longer effective horizon, whereas MPC-6 has no terminal value and is exact only for its six-step objective. No scalable long-horizon planner, approximate dynamic programming method, mixed-integer scheduler, satellite-specific sequential method, or alternative long-horizon RL family is evaluated. Training cost and modeled information are reported, but DQN inference latency is not measured. The comparison therefore does not isolate a DQN-family advantage from an advantage over a deliberately truncated baseline frontier.
- **Why it matters** The principal scientific interpretation depends on whether the learned policies outperform credible alternatives under comparable objectives, forecast information, and computational constraints. The current design demonstrates superiority over the implemented baselines, but it does not yet establish that DQN is the source of the advantage.
- **Resolution test** Add at least one competitive long-horizon baseline under a clearly matched information and computation protocol. Appropriate options could include a planner with terminal-value approximation, scalable tree search, dynamic programming, mixed-integer optimization, or a strong alternative sequential-learning method. Report DQN inference latency and define whether comparisons are matched by forecast access, offline computation, online latency, or another engineering budget. Otherwise narrow the contribution consistently to the specific implemented comparator set.

### R1-M3

- **Concern ID** R1-M3
- **Severity** Major
- **Blocking** No
- **Axis** Technical soundness and claim moderation
- **Claim pointer** The benchmark is presented as resource-coupled satellite-ground scheduling, and lower episode cost is interpreted as better allocation of energy, heat, communication, and compute resources.
- **Evidence pointer** Sections 3 and 4; Eq. 10; Eq. 12; Section 7, Table 13 and its accompanying text; Abstract; Section 8.1
- **Concern** Energy is a clipped accounting coordinate rather than a conserved battery state. Reaching zero neither masks an infeasible action nor terminates an episode, and clipping discards the magnitude of further deficit. Table 13 reports that both learned policies reach zero energy in every displayed regime and spend many steps below the low-energy threshold. Consequently, a policy can continue executing actions after modeled energy exhaustion, and the penalty may saturate rather than represent the physical cost of infeasibility. The reported ranking may therefore partly reflect behavior in an operationally impossible region.
- **Why it matters** The benchmark ordering remains mathematically defined, but its interpretation as resource-aware scheduling is weakened if high-performing policies can exploit clipped infeasible states. This is especially important in the energy-limited regime.
- **Resolution test** Repeat the principal comparisons under at least one feasibility-preserving formulation. Examples include action masking, termination at energy exhaustion, a deficit-retaining energy ledger, or a constrained-control formulation. Report whether the family-level ordering persists and how many actions become infeasible. If this is deferred, describe the result consistently as performance in a soft-penalty simulator and avoid operational resource-efficiency implications.

### R1-M4

- **Concern ID** R1-M4
- **Severity** Major
- **Blocking** No
- **Axis** Scientific importance and technical soundness
- **Claim pointer** The manuscript presents the benchmark as relevant to satellite-ground scheduling and suggests that its resource coupling captures an engineering problem of practical interest.
- **Evidence pointer** Abstract; Sections 1, 3.2, 3.3, and 6.3; Table 2; sensitivity and preview-mismatch analyses; Discussion; Section 8.1
- **Concern** All central evidence is generated within one synthetic simulator. Utility weights are fixed assumptions, resource equations are not calibrated against mission telemetry, and the stress regimes are perturbations of the same generator. There is no second scheduling task, unseen mission distribution, telemetry-backed simulator, or hardware-in-the-loop validation. The NASA-derived ranges support the plausibility of selected primitive scales but do not validate the joint workload distribution, reward weights, resource dynamics, or policy ranking.
- **Why it matters** Internal consistency is not equivalent to engineering validity. The current evidence can support a controlled benchmark result, but it cannot establish transferability to satellite operations or broad significance across resource-coupled scheduling systems.
- **Resolution test** Add independent validation using mission-derived distributions, telemetry, a separately constructed simulator, hardware-in-the-loop traces, or a second scheduling task with meaningfully different dynamics. Alternatively, keep all claims explicitly benchmark-specific and present operational transfer as untested.

### R1-M5

- **Concern ID** R1-M5
- **Severity** Major
- **Blocking** No
- **Axis** Technical soundness and mechanism evidence
- **Claim pointer** The preview-scale experiment is presented as evidence that centered full-action supervision retains a favorable pattern under training-time model misspecification.
- **Evidence pointer** Section 6, Preview-model misspecification test; Table 14; Section 7, Preview-scale perturbations; Discussion and Section 8.1
- **Concern** The misspecification experiment applies only uniform 0.85 and 1.15 scaling to immediate consequences and action-induced resource changes for one model-assisted variant. Uniform scaling preserves much of the simulator structure and may preserve action ordering. It does not test the errors most likely to corrupt full-action supervision, including action-specific bias, state-dependent error, incorrect resource coupling, altered exogenous dependence, or errors that reverse within-state action gaps. Several regimes also fail the manuscript’s complete support rule under the scale perturbations.
- **Why it matters** The distinctive model-assisted mechanism learns from the relative values of unexecuted actions. Robustness to uniform scale error does not establish robustness of those relative labels to structural model error.
- **Resolution test** Evaluate prespecified action-specific, state-dependent, and structural preview errors, including at least one perturbation capable of changing action rankings. Report calibration error, action-gap error, and deployment performance. Otherwise describe the current analysis only as sensitivity to two uniform scale perturbations.

### R1-M6

- **Concern ID** R1-M6
- **Severity** Major
- **Blocking** No
- **Axis** Reproducibility
- **Claim pointer** Contribution 4 and the Data and Code Availability section claim a scripted evidence chain connecting the manuscript, result files, validation metadata, generated tables, and hashes.
- **Evidence pointer** Introduction, Contribution 4; Section 6, Reproducible result entry point; Data and Code Availability; `H:\degree-dissertation\md_cbad_dqn\results\reviewer_revision_state_complete\validation.json`; `H:\degree-dissertation\paper\generated\table_fixed_policies.tex`; `H:\degree-dissertation\md_cbad_dqn\results\reviewer_revision_state_complete\seven_regimes_summary.csv`
- **Concern** The source hash recorded in `validation.json` does not match the current `paper/source.tex`, so the validation record does not authenticate the reviewed manuscript source. A generated artifact is also inconsistent with the machine-readable results. `table_fixed_policies.tex` reports nominal fixed-onboard and fixed-ground costs of 657.66 and 1007.30, whereas the current manuscript and `seven_regimes_summary.csv` report 208.94 and 299.56. The inconsistent table is not included in the current manuscript, but its presence weakens the claimed one-to-one evidence chain.
- **Why it matters** Reproducibility requires the released source, validation manifest, and generated artifacts to identify one coherent result state. Stale hashes and tables make it unclear which files belong to the reported analysis.
- **Resolution test** Regenerate all tables and validation metadata from one clean, versioned result state. Verify the current manuscript hash, remove or correct stale artifacts, and provide an automated check that fails when manuscript-linked tables or source hashes diverge.

## Minor Comments

### R1-m1

- **Concern ID** R1-m1
- **Severity** Minor
- **Axis** Reproducibility
- **Affected element** Data and Code Availability
- **Evidence pointer** Data and Code Availability
- **Issue** The section contains the unresolved text “AUTHOR ARCHIVE IDENTIFIER TO BE INSERTED BEFORE SUBMISSION.”
- **Required correction** Deposit the reviewed code, result tables, validation metadata, and required checkpoints in a permanent archive, then replace the placeholder with the identifier. If checkpoints cannot all be archived, state exactly which artifacts are available and what is required to regenerate the remainder.

### R1-m2

- **Concern ID** R1-m2
- **Severity** Minor
- **Axis** Figures and tables
- **Affected element** Figure 11 and its interpretation
- **Evidence pointer** Section 7, A centered full-action policy uses different action mixtures across regimes; Figure 11
- **Issue** The figure reports mean action fractions for one policy without uncertainty. It therefore shows that the mean is not degenerate but provides limited evidence that action mixtures respond consistently to regimes or explain the performance differences.
- **Required correction** Add uncertainty across the declared independent units and, if mechanism interpretation is retained, include at least one matched comparator. Otherwise keep the figure explicitly descriptive and remove any implication that it identifies the source of the performance advantage.

### R1-m3

- **Concern ID** R1-m3
- **Severity** Minor
- **Axis** Readability for nonspecialists
- **Affected element** Abstract and early benchmark description
- **Evidence pointer** Abstract; Sections 1, 3.3, and 4
- **Issue** “Soft-constrained” is stated, but a nonspecialist reader is unlikely to understand that energy can reach zero while execution continues and that the deficit magnitude is discarded by clipping.
- **Required correction** Add one concise early explanation that the resources are penalty-bearing accounting states rather than enforced feasibility constraints. State that reported costs do not certify operational feasibility.

## Technical failings that need to be addressed before the case is established

The central case requires resolution of R1-M1 and R1-M2. Direct inference is needed for the claimed DQN-family advantage, and the baseline frontier must support attribution of that advantage to long-horizon DQN learning rather than shallow comparator design. R1-M3 through R1-M6 should also be addressed to establish credible engineering interpretation, robustness to model error, external relevance, and a coherent reproducibility package.

## Assessment against Nature-style criteria

- **Originality** The centered full-action objective is a clear construction, but the manuscript itself shows that the larger result is shared across conventional DQN variants. Originality therefore lies mainly in the controlled benchmark and family-level evaluation rather than a decisive new algorithmic mechanism.

- **Scientific importance** The problem is important, and the evidence architecture is valuable. Current importance is limited by the synthetic single-task setting, unenforced feasibility, and incomplete comparator frontier.

- **Interdisciplinary readership** The satellite edge-computing application and full-action learning interface could interest several communities. Broader interest will depend on demonstrating that the result survives realistic constraints or transfers beyond this simulator.

- **Technical soundness** The within-family analyses are carefully designed and transparently reported. The central between-family claim, baseline fairness, constraint semantics, preview-error robustness, and artifact provenance remain substantive weaknesses.

- **Readability for nonspecialists** The manuscript is generally well organized and commendably candid about limitations. Its engineering semantics remain dense, and the practical meaning of soft feasibility should be explained earlier and more plainly.

## Recommendation posture

The manuscript is not yet ready to support a strong Nature-style claim of a DQN-family advantage. A substantial revision should prioritize direct between-family inference, a competitive matched long-horizon baseline, and a feasibility-preserving evaluation. The current work could support a narrower, technically useful benchmark paper if its claims remain explicitly descriptive and simulator-specific.

This Reviewer 1 report is now frozen.
