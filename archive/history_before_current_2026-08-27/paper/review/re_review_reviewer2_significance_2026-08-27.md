# Reviewer 2

## Overall assessment

The manuscript presents a carefully documented simulator-level study of training a DQN with model-generated targets for every available action. The implementation, prespecified seed structure, component controls, validation files, and unusually explicit limitations are strengths. The narrow result that full-action Bellman supervision improves a matched standard-DQN backbone within the specified simulator is supported.

The larger originality and scientific-importance case is not yet established. The centered component that gives CBAD its distinctive formulation does not outperform uncentered full-action supervision. The remaining gain is 0.87% to 1.72% against standard DQN on an author-defined synthetic objective. No mission-fitted utility, hard-feasible policy, independent physical evidence, prior satellite scheduler, or competitive scalable optimizer is supplied. These limitations are acknowledged, but they leave the work closer to a well-controlled algorithmic case study than a result of outstanding and far-reaching scientific importance.

This assessment covers the 25-page manuscript, source, bibliography, generated tables and figures, listed implementation files, result summaries, and supplied validation records. Flight telemetry, hardware-in-the-loop evidence, multisatellite validation, and an external immutable archive were not available.

## Who would be interested in the results, and why

Researchers in model-assisted reinforcement learning may value the controlled demonstration that analytical outcomes for unexecuted actions can provide useful Bellman supervision without deployment-time preview. Satellite edge-computing researchers may also find the three-mode scheduling formulation and transparent simulator useful as a reproducible test case. The current evidence is less compelling for the wider aerospace, operations-research, autonomy, and interdisciplinary readership because operational validity and advantage over competitive domain methods remain untested.

## Major strengths

- The manuscript states a narrow novelty claim and does not present counterfactual simulation, model-assisted learning, advantage learning, or centering as individually new.

- The component study directly compares centered CBAD, uncentered full-action targets, and immediate-cost advantages. This is more informative than a simple DQN ablation.

- Twenty independently trained seed blocks, shared held-out traces, paired intervals, sign tests, multiplicity adjustment, leave-one-seed-out checks, and an unpaired sensitivity analysis provide transparent statistical reporting.

- The analytical preview is restricted to training, implemented as a side-effect-free one-step operation, and checked against factual transitions.

- The manuscript clearly discloses synthetic assumptions, arbitrary utility weights, universal low-energy exposure, absent flight fidelity, limited planning comparisons, and the failure to isolate centering.

## Major Concerns

### R2-M1

**Severity**  
Major

**Blocking**  
Yes

**Axis**  
Originality and novelty-significance

**Claim pointer**  
The manuscript claims novelty for an evaluated full-action Bellman auxiliary objective whose centered implementation supervises action gaps.

**Evidence pointer**  
Introduction and Related Work and Novelty Positioning, page 3; Model-Driven Counterfactual Bellman Advantage Distillation, pages 9 to 11; Table 6 and Section 7.2, page 17; Discussion and Limitations, page 22.

**Concern**  
The manuscript does not establish how the remaining contribution differs from the closest methods that learn from model-evaluated alternatives or full-information action feedback. The related-work discussion distinguishes CBAD conceptually from Dyna, local rollout acceleration, causal augmentation, and advantage learning, but it does not provide a feature-level comparison with the most proximal objective constructions or test a closest existing method. This matters because centering, the most distinctive stated operation, has no detectable increment over uncentered full-action Bellman supervision. The nominal CBAD-minus-full-action difference is only minus 0.07 with a 95% interval from minus 0.32 to 0.20.

**Why it matters**  
Once centering is not supported as necessary, the demonstrated contribution reduces to adding Bellman targets for all model-evaluable actions. The manuscript must show that this objective is genuinely distinct from prior model-assisted or full-action learning formulations. Without that demonstration, originality remains asserted through prose rather than established through scholarship and evidence.

**Resolution test**  
Provide a systematic comparison with the closest prior objective formulations, identifying whether they use all-action outcomes, factual anchoring, bootstrapped alternative targets, centering, replay synthesis, or deployment-time models. Add a matched empirical comparison to the closest implementable method. If no material distinction remains, recast the contribution as an application-specific evaluation of full-action supervision and remove claims that imply a distinct general reinforcement-learning method.

### R2-M2

**Severity**  
Major

**Blocking**  
Yes

**Axis**  
Scientific importance and claim moderation

**Claim pointer**  
The manuscript presents the method as a consequential approach to temporally coupled satellite-ground scheduling and motivates broad value from teaching action gaps without deployment-time preview.

**Evidence pointer**  
Abstract, page 1; System Model and Immediate-Cost Quantification, pages 4 to 8; Tables 3 to 5, pages 14 to 16; Table 8 and Section 7.3, page 18; Discussion and Limitations and Conclusion, pages 22 to 23.

**Concern**  
The evidence does not yet support outstanding scientific importance. The reported improvement over standard DQN is 0.87% to 1.72% on a synthetic composite cost whose weights are fixed simulator assumptions rather than mission utilities. Both learned policies reach zero energy, every evaluated episode has threshold exposure, and the thermal-stress condition never reaches the modeled thermal threshold. The improved policy also transmits substantially more data. Thus the reported cost change is not shown to correspond to feasibility, safety, mission value, or a qualitatively different operating capability.

**Why it matters**  
A statistically consistent improvement in an internally defined objective can establish an algorithmic effect, but it does not by itself establish scientific or engineering importance. The present operating envelope does not demonstrate that the method solves the resource-constrained scheduling problem motivating the manuscript. The authors’ careful limitations prevent direct overclaiming, but they also reveal that the broad significance case is presently unsupported.

**Resolution test**  
Demonstrate the method in an independently justified scheduling setting with mission-relevant utility and active constraints, then report feasible-task completion, violations, resource margins, and decision-relevant effect sizes. Evidence could come from mission-calibrated simulation, an independent benchmark, or another temporally coupled domain that tests the claimed general principle. If such evidence is unavailable, narrow the title, abstract, significance framing, and claimed audience to a synthetic simulator study of a training objective.

### R2-M3

**Severity**  
Major

**Blocking**  
No

**Axis**  
Scientific importance, technical soundness, and experimental design

**Claim pointer**  
The manuscript argues that full-action Bellman supervision offers a useful learned alternative for temporally coupled scheduling and bounds this claim through standard DQN, Double DQN, heuristics, a contextual bandit, and exact finite-horizon planning.

**Evidence pointer**  
Experimental Design and Settings, pages 11 to 14; Table 3, pages 14 to 15; Table 6, page 17; Table 7, pages 17 to 18; Discussion and Limitations, page 22.

**Concern**  
The comparator set is adequate for internal attribution but insufficient for scientific positioning. No cited satellite scheduling method is implemented. The only stronger value-learning backbone is Double DQN, for which the Double-CBAD result does not remain confirmatory after family adjustment. The planning comparator is deliberately restricted to exact enumeration through six steps and is not compared with approximate tree search, dynamic programming, mixed-integer optimization, or another scalable scheduling method. Consequently, CBAD’s large advantage over MPC-4 mainly shows that a learned 64-step policy can outperform a deliberately short-horizon enumerator in this simulator.

**Why it matters**  
The matched standard-DQN experiment supports the existence of an auxiliary-loss effect, but it does not show whether the method is competitive with credible alternatives available to reinforcement-learning or satellite-scheduling practitioners. This weakens both field-level significance and the interpretation of computational advantage.

**Resolution test**  
Add tuned, matched comparisons with at least one competitive enhanced value-learning method, one relevant satellite scheduling approach, and one scalable planning or optimization baseline. Report common information assumptions, training or optimization budgets, end-to-end decision time, feasibility outcomes, and uncertainty. Otherwise confine all comparative conclusions to the matched DQN backbone and the specifically implemented finite-horizon enumerator.

## Minor Comments

### R2-m1

**Severity**  
Minor

**Axis**  
Claim moderation and readability

**Affected element**  
Title and opening framing

**Evidence pointer**  
Title and Abstract, page 1; Conclusion, page 23.

**Issue**  
The title reads as a general satellite-ground scheduling contribution, while the evidence supports only a synthetic, soft-constrained simulator-level result.

**Required correction**  
Signal the simulation boundary in the title or subtitle and retain that qualification in the first statement of significance.

### R2-m2

**Severity**  
Minor

**Axis**  
Figures and tables and internal consistency

**Affected element**  
MPC-4 runtime reporting

**Evidence pointer**  
Section 7.1, page 17; Table 7 and Section 7.3, pages 17 to 18.

**Issue**  
The nominal discussion reports 4.81 ms per decision for MPC-4, while the planning-depth table reports 4.70 ms. The manuscript does not explain whether these values come from different timing runs or aggregations.

**Required correction**  
Reconcile the values or explicitly identify the distinct evaluation sets and timing procedures that produced them.

### R2-m3

**Severity**  
Minor

**Axis**  
Writing clarity

**Affected element**  
Use of the term counterfactual

**Evidence pointer**  
Abstract and Introduction, pages 1 to 3; Related Work and Novelty Positioning, page 3.

**Issue**  
The term can suggest causal counterfactual inference, whereas the implemented operation is deterministic evaluation of alternative actions under the simulator model.

**Required correction**  
Define the term in plain language at first use and consistently distinguish model-evaluated alternative outcomes from causal counterfactual identification.

### R2-m4

**Severity**  
Minor

**Axis**  
Reproducibility

**Affected element**  
Data and Code Availability statement

**Evidence pointer**  
Data and Code Availability, page 23.

**Issue**  
The statement retains an author-owned archive-identifier placeholder.

**Required correction**  
Before submission, the authors should replace the placeholder with the actual immutable archive identifier or an accurate availability statement. No identifier should be invented.

## Technical failings that need to be addressed before the case is established

R2-M1 and R2-M2 are blocking. The manuscript must establish that the full-action Bellman objective is original relative to its closest predecessors and must connect its simulator-level effect to a scientifically or operationally important outcome. R2-M3 should also be addressed to support comparative relevance beyond a matched standard-DQN attribution experiment.

## Assessment against Nature-style criteria

**Originality**  
Potentially interesting, but not established. The closest methodological distinction is insufficiently mapped, and the centering component does not show an incremental effect.

**Scientific importance**  
Currently limited. The result is statistically consistent within the simulator but small, tied to an author-defined utility, and not associated with feasibility or operational capability.

**Interdisciplinary readership**  
There is potential interest across reinforcement learning, autonomous systems, aerospace computing, and operations research. The present evidence remains too narrow and application-internal to establish immediate and far-reaching implications.

**Technical soundness**  
The matched DQN comparison is carefully implemented and transparently reported. Validation, inference, component controls, and limitations are stronger than usual for a simulation study. Broader superiority, physical validity, and deployment relevance are not established.

**Readability for nonspecialists**  
The manuscript is generally well structured, and the graphical overview, three-mode explanation, and explicit limitations help. The density of reinforcement-learning terminology and the ambiguous use of counterfactual still create barriers for nonspecialists.

## Recommendation posture

The simulator-level training-objective result is credible and reproducible, but the originality and broad scientific-importance case is currently not established from the supplied evidence. A substantially stronger novelty comparison, operationally meaningful validation, and competitive baseline suite would be required for a strong Nature-style case.
