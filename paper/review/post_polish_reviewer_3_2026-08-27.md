## Reviewer 3

### Overall assessment

This manuscript presents a carefully documented synthetic benchmark for resource-coupled satellite-ground scheduling and evaluates six closely matched DQN objectives against myopic, heuristic, contextual-bandit, and finite-horizon planning comparators. The strongest aspect is the unusually explicit evidence chain. The simulator equations, training protocol, seed structure, multiplicity handling, sensitivity analyses, generated tables, checkpoints, and validation metadata are all visible locally. The manuscript also moderates several claims appropriately. It acknowledges that the utility weights are assumed, constraints are soft, between-family inference is descriptive, and operational validation remains future work.

The main weakness is that the broad scientific case remains substantially narrower than the title and satellite-engineering framing suggest. The central result is a large benchmark-internal separation between DQN and the implemented short-horizon comparators. It is not yet evidence of an operationally feasible scheduling advantage, nor is the comparative claim supported by direct uncertainty estimates against the non-DQN frontier. The manuscript is readable sentence by sentence, but the hierarchy of claims is difficult for a nonspecialist to follow. A centered full-action method dominates the graphical and methodological presentation, whereas the reported principal contribution is the much broader and less method-specific observation that all six DQN variants occupy a similar performance band.

### Who would be interested and why

The work should interest researchers in reinforcement learning for sequential control, satellite edge computing, model-assisted value learning, and reproducible algorithm benchmarking. The analytical all-action preview is also relevant to readers studying simulators that can label unexecuted discrete actions during training. Space-systems engineers may value the explicit decomposition of compute, communication, energy, queue, and thermal state variables. Their confidence in operational relevance will remain limited, however, until the benchmark enforces feasible resource dynamics and is connected to mission-derived tasks or traces.

### Major strengths

- The manuscript states the simulator and its assumptions with uncommon transparency. Sections 3 and 4 expose the task generator, action loads, state, transition, reward, and terminal behavior.
- Twenty independently trained seeds and twenty held-out traces per seed provide a substantially stronger empirical basis than a small-seed demonstration.
- The distinction between the family-level result and smaller within-family effects is scientifically responsible. Tables 7 and 9 do not claim a universally superior DQN objective.
- The authors explicitly account for unequal modeled information in Table 10 and distinguish training stabilization from mathematical convergence.
- The local result package contains raw evaluations, checkpoints, seed-level summaries, metadata, validation status, and generated manuscript tables. The reported validation files indicate complete expected row counts and finite numerical outputs.
- The prose audit passes for citation keys, cross-references, long sentences, and prohibited dash punctuation. Local sentence clarity is generally good even where the overall narrative remains dense.

### Major Concerns

#### R3-M1

- **Concern ID** R3-M1
- **Severity** Major
- **Blocking** Yes
- **Axis** Scientific importance and technical soundness
- **Claim pointer** The title, Abstract, Introduction, Discussion, and Conclusion frame the result as an advantage for resource-coupled satellite-ground scheduling.
- **Evidence pointer** Sections 3.2 and 3.3, Section 6.3, Table 13, Section 8.1, and Section 9
- **Concern** The evaluated task does not yet establish an engineering scheduling result beyond its synthetic objective. Utility weights are fixed assumptions rather than mission-derived quantities. Energy is a clipped accounting coordinate rather than a conserved resource, actions remain available at zero energy, and episodes do not terminate when feasibility is lost. Table 13 shows that both learned policies reach zero remaining energy in every displayed regime. Conversely, the thermal-stress condition does not approach the modeled heat threshold. Its reported maximum heat is 0.364, compared with the penalty threshold of 0.78. The current operating envelope therefore permits a persistent energy failure while barely activating the claimed thermal boundary.
- **Why it matters** Lower dimensionless cost can describe policy behavior inside this simulator, but it does not yet demonstrate that the resulting schedules satisfy the engineering requirements that motivate the paper. Nonspecialists may reasonably interpret the satellite framing as evidence of feasible resource management, even though the present benchmark does not require feasibility.
- **Resolution test** Either provide an independently motivated engineering specification with hard resource accounting, infeasible-action handling, meaningful failure modes, and mission-derived or otherwise validated utilities, then show that the comparative ordering persists, or narrow the title, Abstract, Discussion, and Conclusion to an explicitly synthetic soft-constraint control benchmark. If thermal stress remains a named regime, it should demonstrably probe a relevant thermal boundary.

#### R3-M2

- **Concern ID** R3-M2
- **Severity** Major
- **Blocking** Yes
- **Axis** Originality, scientific importance, and technical soundness
- **Claim pointer** The manuscript describes a consistent DQN-family advantage over the strongest implemented non-DQN comparator and interprets MPC-6 as evidence that the family-level ordering persists with deeper exact planning.
- **Evidence pointer** Abstract, Section 6.4, Table 6, Table 12, Section 7.3, Section 8, and Section 8.1
- **Concern** The strength of the principal comparative claim is determined by a limited and unmatched baseline frontier. The planners enumerate only horizons up to six in a 64-step episode, whereas DQN receives 38,400 offline training interactions per model. Planner runtime includes online action selection, but DQN inference latency and the cost of training are not part of a matched comparison. The manuscript itself identifies scalable tree search, dynamic programming, mixed-integer optimization, and satellite-specific schedulers as missing future baselines. Accordingly, a result against MPC-4 or MPC-6 does not yet establish that DQN is preferable to a competitive long-horizon scheduling method under a common information and computation contract.
- **Why it matters** The central novelty is not a large, independently isolated gain from the new auxiliary objective. It is the family-level comparison against non-DQN methods. If the comparator frontier is weak or unmatched, the scientific importance of that central result cannot be judged.
- **Resolution test** Add at least one tuned, scalable long-horizon comparator and state a common information, forecast, optimization, and compute budget for all policies. Report end-to-end deployment latency for learned and planning methods. If this comparison is not undertaken, the title and principal claims should be restricted to the specific implemented short-horizon comparator set without suggesting a broader scheduling advantage.

#### R3-M3

- **Concern ID** R3-M3
- **Severity** Major
- **Blocking** Yes
- **Axis** Statistical rigor and technical soundness
- **Claim pointer** The central family-level conclusion is that all 30 DQN objective-regime means are below the corresponding MPC-4 means.
- **Evidence pointer** Table 6 and the first subsection of Section 7
- **Concern** The headline family-level advantage is established only by ordering sample means. The manuscript explicitly states that between-family inference remains descriptive because learned and deterministic methods express different sources of variation. The careful paired bootstrap and Holm-adjusted inference apply to within-family contrasts, not to the DQN versus MPC comparison that supports the title. Different sources of variance do not preclude estimating a paired cost difference on shared held-out traces while treating model training seed as an additional level.
- **Why it matters** A universal ordering of 30 estimated means is visually strong, but without uncertainty on the corresponding DQN minus comparator differences, the reader cannot assess the precision, worst-case margin, or robustness of the central comparative claim. The paper currently gives its secondary within-family claim stronger inferential support than its primary between-family claim.
- **Resolution test** Report prespecified DQN versus comparator effect sizes and uncertainty for every fully coupled regime, using the shared trace structure and an analysis that respects training-seed and trace-level dependence. Define any multiplicity family used for the 30 comparisons. At minimum, provide the smallest family-level margin with a defensible confidence interval and show that the conclusion does not depend on pooling incompatible variance estimates.

#### R3-M4

- **Concern ID** R3-M4
- **Severity** Major
- **Blocking** No
- **Axis** Mechanism evidence and claim moderation
- **Claim pointer** The Abstract concludes that the results identify long-horizon value learning as an effective strategy, and the Results state that the advantage emerges under fully coupled conditions.
- **Evidence pointer** Abstract, Section 6.3, Section 6.4, Section 7.1, Figure 9, and Section 8
- **Concern** The evidence is compatible with a benefit from long-horizon learning, but it does not isolate that explanation. The coupling coefficient simultaneously changes resource carryover and delayed-penalty scale. Policies trained at \(c=1\) are transferred to \(c=0\) and \(c=0.5\) without retraining. The discount factor is fixed at 0.97, and no independent transition-carryover, penalty-scale, or discount sensitivity is reported. The contextual bandit and planning-depth results support a sequential effect, but they do not distinguish horizon, training-distribution alignment, objective scaling, and approximation effects.
- **Why it matters** The family ordering is a valid empirical observation inside the benchmark. The stronger explanatory statement about why the ordering occurs is not yet discriminated from plausible alternatives. This also makes the central lesson difficult to convey to a nonspecialist audience.
- **Resolution test** Independently vary transition carryover and delayed-penalty scale, include a discount or effective-horizon analysis, and retrain policies for the relevant coupling conditions. Otherwise describe long-horizon value learning as a plausible interpretation rather than an identified mechanism.

#### R3-M5

- **Concern ID** R3-M5
- **Severity** Major
- **Blocking** No
- **Axis** Interdisciplinary readership and readability for nonspecialists
- **Claim pointer** The title and main Results prioritize a DQN-family observation, while the graphical abstract, Section 5, Algorithm 1, and several later analyses prioritize centered full-action supervision.
- **Evidence pointer** Title, Abstract, Figure 1, Sections 1, 5, 7.1, 7.2, and 8
- **Concern** The manuscript asks the reader to track three distinct contribution levels. These are the synthetic engineering benchmark, a general DQN-family result, and a centered full-action auxiliary objective whose gains are below 1 percent and satisfy the complete rule in only three of five regimes. The graphical and methodological emphasis suggests that the centered method is the main advance, whereas the text later says that the method-specific effects are secondary. A nonspecialist also receives little intuition for what a change from approximately 90.8 to 77.7 dimensionless cost means operationally.
- **Why it matters** The local prose is controlled, but the manuscript-level argument is not yet easy to summarize accurately. This limits interdisciplinary reach and risks readers attributing the headline result to a method-specific innovation that the ablations do not isolate.
- **Resolution test** Reorganize the opening and principal visual around an explicit claim hierarchy. State separately what is learned about the benchmark, the DQN family, and centered full-action supervision. Add one intuitive operational decomposition of the large DQN versus MPC difference, not only the small centered full-action versus DQN difference. The Abstract should quantify or plainly describe the practical meaning of the cost separation.

### Minor Comments

#### R3-m1

- **Concern ID** R3-m1
- **Severity** Minor
- **Axis** Reproducibility
- **Affected element** Version binding between the manuscript and validation metadata
- **Evidence pointer** `validation.json`, `extended_revision_validation.json`, and the current `paper/source.tex`
- **Issue** The two validation files record different SHA256 values for `paper/source.tex`, and neither matches the current source in the review packet. The generated-table hashes do match the visible generated files, so this appears to be stale manuscript-level provenance rather than evidence of numerical corruption.
- **Required correction** Regenerate the validation metadata against the final manuscript source and provide one authoritative version manifest that binds code, numerical artifacts, generated tables, figures, and manuscript.

#### R3-m2

- **Concern ID** R3-m2
- **Severity** Minor
- **Axis** Reproducibility
- **Affected element** Data and Code Availability
- **Evidence pointer** Data and Code Availability section
- **Issue** The section contains an unresolved archive placeholder and no permanent public identifier.
- **Required correction** Deposit the complete package in a permanent archive and replace the placeholder before submission, or state a concrete access route and release timing if permitted by the target venue.

#### R3-m3

- **Concern ID** R3-m3
- **Severity** Minor
- **Axis** Claim moderation
- **Affected element** Planning interpretation
- **Evidence pointer** Table 12, Section 7.3, and the third paragraph of Section 8
- **Issue** The phrase “quality-computation frontier” is stronger than the measurement supports because DQN inference time is not included and training computation is outside the comparison.
- **Required correction** Call this an MPC horizon-cost-runtime curve unless a matched learned-policy latency comparison is added.

#### R3-m4

- **Concern ID** R3-m4
- **Severity** Minor
- **Axis** Figures and tables
- **Affected element** Action-mixture figure
- **Evidence pointer** Figure 11 and Section 7.7
- **Issue** Mean action fractions are shown without uncertainty or a comparison policy, limiting what can be inferred about regime-dependent adaptation.
- **Required correction** Add seed-level uncertainty and at least one relevant comparison, or retain the figure as descriptive and remove any implication that it explains the family-level mechanism.

#### R3-m5

- **Concern ID** R3-m5
- **Severity** Minor
- **Axis** Readability for nonspecialists
- **Affected element** Primary results presentation
- **Evidence pointer** Table 6, Figure 6, and Equation 15
- **Issue** The paper reports a dimensionless aggregate cost without a compact reader-facing explanation of its scale or the relative contribution of immediate cost and feasibility penalties for all principal methods.
- **Required correction** Add a short interpretation guide and decompose the primary DQN versus MPC comparison into understandable resource and penalty components.

#### R3-m6

- **Concern ID** R3-m6
- **Severity** Minor
- **Axis** Writing clarity
- **Affected element** Use of “exact planner”
- **Evidence pointer** Abstract, Section 6.4, and Table 12
- **Issue** “Exact” can be misread as globally optimal over the 64-step task. The Methods and table caption explain that exactness applies only to enumeration within horizon \(H\), but the shorter headline references do not always preserve this qualification.
- **Required correction** Use “exact \(H\)-step receding-horizon planner” at first mention in the Abstract and whenever the horizon-limited nature of exactness could be missed.

### Technical failings that need to be addressed before the case is established

The blocking issues are R3-M1, R3-M2, and R3-M3. The manuscript needs an engineering-valid operating envelope or a substantially narrower benchmark claim, a competitive and matched comparator frontier, and direct uncertainty estimates for the DQN versus non-DQN result. R3-M4 and R3-M5 should also be resolved to support the explanatory and interdisciplinary case.

### Assessment against Nature-style criteria

- **Originality** The centered full-action construction and the controlled six-objective family are potentially useful, but the method-specific gain is small and centering is not factorially isolated. The most original contribution may be the transparent benchmark and evidence package rather than a new learning principle.
- **Scientific importance** The present importance is credible for synthetic sequential-control benchmarking. Broader satellite-engineering importance is not established because utilities and resource dynamics are not mission-validated and hard feasibility is absent.
- **Interdisciplinary readership** Reinforcement-learning and space-systems specialists can follow the work. A wider audience will struggle to identify the single principal advance and to translate dimensionless cost improvements into operational consequences.
- **Technical soundness** Internal simulator specification, seed replication, within-family inference, and artifact validation are strong. The central between-family claim lacks direct inferential support, the baseline frontier is limited, and the engineering stress envelope does not establish feasible operation.
- **Readability for nonspecialists** Sentence-level readability is good. Manuscript-level accessibility is weakened by dense implementation detail, competing contribution levels, and limited intuitive interpretation of the principal outcome.

### Recommendation posture

The manuscript contains a substantial, reproducible benchmark study, but the current Nature-style case requires major revision. The benchmark-internal ordering appears credible from the supplied evidence, while the broader claims of engineering advantage, comparative strength, mechanism, and interdisciplinary importance are not yet established. A specialist algorithm or aerospace-systems venue could find the transparent benchmark valuable after tighter claim calibration. A broad-interest submission would require the blocking evidence additions described above.

This Reviewer 3 report is now frozen.
