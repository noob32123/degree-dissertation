## Reviewer 2

### Overall assessment

This is a carefully documented computational study with a transparent synthetic simulator, substantial seed-level replication, and unusually explicit statements about evidential limits. The family-level observation is clear. Under the five fully coupled regimes, all six DQN objectives have lower observed mean episode cost than MPC-4, the strongest implemented non-DQN comparator. The manuscript also appropriately avoids presenting the centered full-action objective as uniformly superior within the DQN family.

The main weakness is not whether the reported ordering occurred. It is whether that ordering constitutes an original and scientifically important advance beyond this author-defined benchmark. The current evidence does not establish that broader case. The headline result concerns a family of largely established value-learning formulations, the comparator frontier is narrow, and the benchmark lacks independent physical calibration, hard feasibility, or transfer to a second task. Moreover, the central DQN versus MPC claim is supported only by observed means, without direct uncertainty estimates for the between-family differences. I therefore view the work as a credible and potentially useful specialist benchmark study, but not yet as a compelling Nature-style contribution.

### Who would be interested and why

Researchers in reinforcement learning, model-assisted value learning, resource-constrained control, satellite edge computing, and reproducible algorithm benchmarking would be interested. The work offers a well-specified setting in which long-horizon policies can be compared with transparent myopic and finite-horizon alternatives. Satellite-systems engineers may also find the resource accounting and explicit simulator equations useful as a starting point. Interest beyond these communities will remain limited until the result is connected to independently calibrated physical evidence, a broader algorithmic frontier, or a transferable principle demonstrated across tasks.

### Major strengths

- The simulator, reward, transition equations, episode objective, state construction, training protocol, and planning objective are specified in substantial detail.

- The study uses 20 independently trained model seeds, held-out traces, paired seed-level inference, leave-one-seed-out checks, preview-error perturbations, and prespecified parameter sensitivity analyses.

- The manuscript clearly distinguishes the family-level result from smaller objective-specific differences. It also acknowledges that the component comparisons do not factorially isolate centering or bootstrapping.

- Table 14 reports unequal modeled-information and training-time budgets rather than presenting equal real interactions as equal computational effort.

- The discussion identifies several important boundaries, including soft constraints, coupled changes in dynamics and penalty scale, limited planning depth, unmatched inference latency, and the absence of mission-derived validation.

### Major Concerns

#### R2-M1

- **Concern ID** R2-M1
- **Severity** Major
- **Blocking** Yes
- **Axis** Originality and scientific importance
- **Claim pointer** The title, Abstract, Introduction contributions, Discussion, and Conclusion present the consistent DQN-family advantage as the principal contribution and interpret long-horizon DQN value learning as an effective scheduling strategy.
- **Evidence pointer** Abstract; Section 1; Section 2 and Table 1; Section 7, especially Tables 9 and 10; Section 8; Section 9
- **Concern** The manuscript does not yet show why the family-level ordering is an original scientific advance rather than a result specific to this benchmark. The central conclusion deliberately shifts away from the new centered full-action objective toward the shared DQN family. However, standard DQN and Double DQN are not introduced here, while the more distinctive objective-specific effects are small and incompletely identified. Centered full-action improves standard DQN by only 0.45% to 0.85% across the five coupled regimes, and the complete prespecified rule supports three regimes. The supplied centering and bootstrapping contrasts support no regime. Table 1 distinguishes mechanisms by features, but feature distinction alone does not establish scientific importance.
- **Why it matters** A reproducible outcome on one synthetic benchmark can be useful, but Nature-style originality and importance require either a general methodological advance or a result that changes understanding across a meaningful class of systems. The present evidence establishes neither route.
- **Resolution test** The revision should define one primary contribution and provide evidence commensurate with it. A methodological claim would require tuned and appropriately factorial comparisons that isolate the proposed mechanism, together with confirmation on independent tasks or environments. A benchmark claim would require a clear account of what new scientific question the benchmark enables, evidence that conclusions transfer beyond one generator, and substantially narrower methodological language. If neither route is feasible, the work should be positioned explicitly as a specialist synthetic benchmark study.

#### R2-M2

- **Concern ID** R2-M2
- **Severity** Major
- **Blocking** Yes
- **Axis** Experimental design
- **Claim pointer** The manuscript states that the six DQN objectives consistently outperform the strongest implemented non-DQN comparator and treats this separation as the main family-level result.
- **Evidence pointer** Section 2; Section 6.4; Table 6; Table 9; Table 12; Section 7.1; Section 7.3; Section 8
- **Concern** The comparator frontier is insufficient to establish a strong advantage for the DQN family. The non-DQN set consists principally of immediate argmin, a hand-specified threshold rule, a contextual bandit, and exact receding-horizon enumeration limited to at most six steps. The manuscript cites satellite-specific scheduling studies and broader model-based learning families but implements none of them. MPC-6 still sees only six of 64 tasks, while DQN is trained on 38,400 interactions from the same generator and can encode longer-horizon distributional regularities. The comparisons are therefore informative about horizon within the implemented setup, but they do not establish competitiveness against current sequential optimization, model-based control, or satellite scheduling methods.
- **Why it matters** The paper’s scientific importance depends on the meaning of “advantage.” Outperforming deliberately shallow planning and simple heuristics does not show that DQN is the preferred solution to the engineering problem or that value learning captures something unavailable to stronger model-based approaches.
- **Resolution test** Add tuned, relevant baselines under clearly matched information and computational conditions. These should include at least one scalable planning or dynamic-programming approach and one competitive satellite-specific or modern sequential-learning method. Report each method’s training information, forecast access, online computation, and tuning budget. If stronger baselines cannot be added, the central claim must be limited to the specific implemented comparator set and any broader superiority or engineering-preference implication must be removed.

#### R2-M3

- **Concern ID** R2-M3
- **Severity** Major
- **Blocking** Yes
- **Axis** Statistical rigor
- **Claim pointer** All 30 DQN objective by regime means are below the corresponding MPC-4 mean, which is presented as the manuscript’s central family-level evidence.
- **Evidence pointer** Abstract; Table 6 and its caption; Section 7.1; Table 9; Section 8; Section 9
- **Concern** The central between-family claim is based on point-mean ordering without direct uncertainty estimates for DQN minus MPC-4. The manuscript explicitly describes between-family inference as descriptive because the displayed standard deviations arise from different sources. That caveat is appropriate, but it also means the main claim lacks an inferential analysis aligned with its estimand. The deterministic status of MPC does not remove uncertainty due to sampled task traces, nor does it prevent construction of DQN minus MPC differences on shared evaluation units. In contrast, the much smaller centered full-action versus standard-DQN effect receives detailed paired inference.
- **Why it matters** Counting 30 favorable means does not quantify uncertainty in the central comparison and can make correlated regime and objective results appear like 30 independent confirmations. The headline conclusion is stronger than its statistical support.
- **Resolution test** Define the target population and estimand for each DQN versus MPC comparison, then report direct effect sizes and confidence intervals using the actual nested model-seed and trace structure. A hierarchical bootstrap, prespecified seed or namespace block analysis, or another justified repeated-training design would be acceptable. Multiplicity across objectives and regimes should be handled through a family-level test or a clearly justified correction. The manuscript should also state that the 30 cells are correlated and are not 30 independent replications.

#### R2-M4

- **Concern ID** R2-M4
- **Severity** Major
- **Blocking** No
- **Axis** Scientific importance and engineering validation
- **Claim pointer** The manuscript frames the study as resource-coupled satellite-ground scheduling and interprets costs, energy, heat, latency, bandwidth, and contact as engineering outcomes.
- **Evidence pointer** Sections 3 and 4; Table 3; Section 6.3; Table 13; Sections 7.3, 8, and 8.1
- **Concern** The engineering operating envelope is not independently validated. Utility weights, power, heat conversion, service dynamics, and action loads are fixed simulator assumptions. Energy is a clipped accounting state rather than a conserved resource, no action becomes infeasible, and episodes continue after energy reaches zero. Table 13 shows both learned policies reaching zero remaining energy, with roughly 24 to 39 low-energy steps per episode. The thermal-stress maximum heat remains far below the stated 0.78 penalty threshold, so that regime does not visibly exercise the advertised thermal boundary. The five fully coupled regimes are perturbations of one generator rather than independent systems or tasks.
- **Why it matters** These choices are acceptable for a synthetic algorithm benchmark, but they prevent the results from demonstrating safe or operationally meaningful satellite scheduling. They also limit the broader scientific importance of the resource-coupling claim.
- **Resolution test** Either add independent mission-derived or hardware-informed validation with hard feasibility, realistic failure modes, and previously unseen operating conditions, or consistently restrict the contribution to a synthetic soft-constrained benchmark. At minimum, the revised study should mask infeasible actions or terminate invalid trajectories, test loads that actually activate the stated thermal and energy boundaries, and show whether the family-level ordering survives on a second task or independently parameterized generator.

### Minor Comments

#### R2-m1

- **Concern ID** R2-m1
- **Severity** Minor
- **Axis** Readability and claim moderation
- **Affected element** Abstract and Conclusion
- **Evidence pointer** Abstract; Section 9
- **Issue** The reported costs appear as mission-like quantitative outcomes, but they are dimensionless values produced by fixed, unfitted utility weights. Nonspecialist readers may not appreciate this boundary from the Abstract.
- **Required correction** State in the Abstract that the comparison uses a synthetic dimensionless objective with unfitted weights. Consider reporting the DQN versus MPC effect as both an absolute and relative difference.

#### R2-m2

- **Concern ID** R2-m2
- **Severity** Minor
- **Axis** Claim moderation
- **Affected element** Planning-time interpretation
- **Evidence pointer** Abstract; Table 12; Section 7.3; Section 8
- **Issue** The manuscript juxtaposes planning quality and planning time, but DQN deployment latency and energy were not measured. This can be read as implying a deployment-efficiency advantage that the experiment does not test.
- **Required correction** Add a matched DQN inference benchmark on the same hardware and reporting boundary, or restrict the language to computational growth within the tested exact planners.

#### R2-m3

- **Concern ID** R2-m3
- **Severity** Minor
- **Axis** Reproducibility
- **Affected element** Data and Code Availability
- **Evidence pointer** Data and Code Availability section
- **Issue** The section contains an unresolved archive placeholder even though reproducibility is presented as a contribution.
- **Required correction** Deposit the complete evidence package in a permanent public archive and replace the placeholder with the identifier before submission. State any licensing or access restrictions.

#### R2-m4

- **Concern ID** R2-m4
- **Severity** Minor
- **Axis** Figures and tables
- **Affected element** Regime-dependent action-mixture interpretation
- **Evidence pointer** Figure 11 and Section 7.7
- **Issue** Mean action fractions are used to support regime-dependent allocation, but no across-seed or across-trace uncertainty is shown.
- **Required correction** Add uncertainty or the underlying distribution for each action fraction. Otherwise retain the panel as illustrative and avoid treating between-regime differences as established behavioral effects.

#### R2-m5

- **Concern ID** R2-m5
- **Severity** Minor
- **Axis** Readability for nonspecialists
- **Affected element** Positioning of the centered full-action mechanism
- **Evidence pointer** Section 2; Sections 5.2 and 5.3; Figure 4
- **Issue** The distinction between full-action targets, centered advantages, and ordinary DQN is technically specified but not distilled into a short conceptual explanation for readers outside reinforcement learning.
- **Required correction** Add two or three plain-language sentences explaining what information each method receives, why state-wise centering can change action gaps but not common value offsets, and why this distinction matters to deployment decisions.

### Technical failings that need to be addressed before the case is established

The central scientific case requires resolution of R2-M1, R2-M2, and R2-M3. These concern the originality and importance of the family-level contribution, the restricted comparator frontier, and the absence of direct inferential support for the headline DQN versus MPC result. R2-M4 must also be addressed before any operational or transferable engineering implication is made.

### Assessment against Nature-style criteria

- **Originality** The centered full-action construction is potentially distinctive, but the paper’s principal conclusion is deliberately family-level. The current experiments do not show that the distinctive construction is responsible for the main performance separation or that the family-level observation reveals a new general principle.

- **Scientific importance** The work is useful as a controlled benchmark, but its importance is constrained by one synthetic generator, shallow model-based comparators, soft feasibility, and no independent task or physical validation.

- **Interdisciplinary readership** The paper should interest reinforcement-learning, control, and satellite edge-computing specialists. Broader readership is unlikely without evidence that the conclusion transfers across systems or changes engineering practice.

- **Technical soundness** The simulator specification, replication, within-family paired analyses, and artifact checks are strong. The central between-family inference, baseline adequacy, and engineering validation remain insufficient.

- **Readability for nonspecialists** The manuscript is organized, candid, and technically precise. Broader accessibility would improve with clearer explanation of the cost scale, the centered mechanism, and the difference between a synthetic benchmark result and an operational scheduling claim.

### Recommendation posture

Substantial additional evidence and repositioning are required before this work supports a strong Nature-style case. In its current form, it is better supported as a transparent specialist benchmark study than as a broadly significant methodological or engineering advance. This is a reviewer assessment, not an editorial decision.

Reviewer 2 report frozen.
