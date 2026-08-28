# Reviewer 1

## Overall assessment

The manuscript presents a carefully implemented simulator-level study of counterfactual full-action Bellman supervision for a synthetic single-satellite scheduling problem. The primary CBAD versus standard DQN comparison is unusually transparent, with 20 paired model-seed blocks, shared held-out traces within blocks, component controls, source code, checkpoints, raw results, and validation records. The authors also moderate several important claims, including the lack of hard-constrained deployability, flight validation, multisatellite evidence, and a demonstrated centering advantage.

Two issues currently prevent the technical interpretation from being established. First, the reported 21-dimensional state is not demonstrably Markov because the exogenous link process and stress intervals depend on omitted time and episode phase. Second, the manuscript’s mechanistic attribution to bootstrapped full-action labels is stronger than the supplied adjusted inference supports. The engineering application remains a synthetic proof of concept because every principal policy reaches zero energy and no external physical validation is supplied.

## Who would be interested in the results, and why

Researchers in reinforcement learning, model-assisted control, satellite edge computing, and resource scheduling may value the demonstration that analytical one-step alternatives can provide useful training supervision without being available at deployment. The work is also relevant to engineers comparing learned long-horizon policies with short-horizon exact planning under computational constraints. Interest outside these communities will depend on establishing that the effect survives a valid state formulation, feasible operating constraints, and more realistic model uncertainty.

## Major strengths

- The manuscript states the simulator equations, task generator, transition functions, reward, network, training budget, randomization blocks, and inference procedure with substantial precision.
- Standard DQN and CBAD share the same factual loss, architecture, replay, optimizer, exploration schedule, target-network construction, and real-interaction budget.
- The component controls appropriately reveal that centering itself is not supported as the source of the observed improvement.
- The primary paired effects are consistent across the five fully coupled regimes. Mean reductions range from 0.87% to 1.72%, all paired bootstrap intervals are below zero, and 16 to 18 of 20 seed-block differences favor CBAD.
- The paper openly reports the weaker unpaired inference, the nonconfirmatory Double-DQN result, energy depletion, synthetic utility weights, and lack of flight-readiness evidence.
- The supplied source and primary validation hashes match the immutable packet identifiers.

## Major Concerns

### R1-M1

**Severity** Major

**Blocking** Yes

**Axis** Technical soundness and statistical rigor

**Claim pointer** The abstract, component-control Results, Discussion, and Conclusion state that the controls localize the supported contribution to action-specific bootstrapped full-action values rather than three immediate labels alone.

**Evidence pointer** Table `tab:extended_ablation`; Results subsection “Component controls identify Bellman bootstrapping, but not centering, as the supported distinction”; `extended_ablation_inference.csv`, nominal comparison `md_cbad_dqn - md_immediate_advantage_dqn`.

**Concern** The direct nominal CBAD versus immediate-advantage comparison has a mean difference of -0.585 and an unadjusted paired bootstrap interval of [-0.997, -0.135]. Its exact sign-test value is 0.04139, its Holm-adjusted value across the five regimes is 0.08278, and the supplied analysis marks `supported=False`. The manuscript nevertheless treats this comparison as positive mechanistic evidence. This differs from its treatment of Double-CBAD, for which a similarly negative bootstrap interval is explicitly called directional because the adjusted sign test is 0.05909. The immediate-advantage versus standard DQN comparison is also marked unsupported by the supplied combined criterion.

**Why it matters** Distinguishing Bellman bootstrapping from the effect of supplying three analytical labels is central to the method’s mechanistic contribution. The current manuscript applies its directional-consistency criterion selectively and overstates what the component controls establish.

**Resolution test** Report the complete adjusted inference for every mechanism comparison and apply one prespecified evidentiary rule consistently. Either provide multiplicity-consistent confirmatory evidence that CBAD improves on the immediate-advantage control, or revise the abstract, Results, Discussion, and Conclusion to describe the mechanism result as an exploratory mean pattern rather than established attribution.

### R1-M2

**Severity** Major

**Blocking** Yes

**Axis** Technical soundness and experimental design

**Claim pointer** The manuscript formulates a 21-dimensional sequential state and interprets the auxiliary targets as Bellman targets for that state.

**Evidence pointer** Section “Complete stochastic generator and action-load specification,” Eqs. `eq:link_trace`; Section “Sequential Scheduling Formulation,” state definition and Eqs. `eq:factual` and `eq:cf_target`; `environment.py`, `_generate_link_trace`, `_generate_physics_tasks`, and `_state`.

**Concern** The stated observation contains the current task and six resource coordinates but omits time, episode phase, and history. Future bandwidth and contact depend on an episode-level hidden phase and absolute time through two periodic processes. Burst and thermal-stress task distributions also depend on a fixed interval determined by the time index. Current noisy bandwidth and contact values do not uniquely recover these omitted variables. Consequently, the 21-dimensional observation is not shown to satisfy the Markov property, and the target-network bootstrap is not demonstrably a Bellman target for the stated state. The one-step preview can be exact for the simulator program while the bootstrapped value remains affected by state aliasing.

**Why it matters** The method’s interpretation relies on action values and counterfactual Bellman targets for a well-defined state. Hidden phase and time can change the distribution of future costs for observationally similar states, weakening both the theoretical formulation and the explanation of why the auxiliary targets work.

**Resolution test** Demonstrate state sufficiency, or add the relevant time and phase information and repeat the comparisons. A valid alternative is to formulate the problem explicitly as partially observed and compare a history-aware or recurrent implementation. The revised analysis must show that the principal and component-control conclusions survive the corrected formulation.

### R1-M3

**Severity** Major

**Blocking** No

**Axis** Technical soundness and claim moderation

**Claim pointer** The satellite-ground scheduling application is presented as an engineered resource-allocation problem, with robustness assessed across coupled and stressed regimes.

**Evidence pointer** Table `tab:engineering`; Results subsection “Planning depth improves cost at a rapidly increasing computational price”; Discussion and Limitations; `seven_regimes_raw.csv`.

**Concern** Both principal learned policies reach exactly zero remaining energy, and no evaluated episode is threshold free. The thermal-stress condition does not cross the stated heat threshold. Feasibility is represented only through clipped states and soft penalties, with no action masking, termination, constrained objective, or hard safety comparator. Thus the evaluation demonstrates a small reduction in an assumed composite cost, but not a feasible satellite schedule or improved constraint satisfaction. The authors acknowledge this limitation, which prevents it from becoming an unsupported deployability claim, but it leaves the engineering case substantially weaker than the scheduling motivation suggests.

**Why it matters** An algorithm can improve a soft composite score while producing schedules that are unusable under the physical constraints motivating the problem. This limits scientific importance and the transferability of the result beyond the defined simulator.

**Resolution test** Evaluate a hard-constrained or explicitly constrained formulation with feasible-action handling and report feasibility rates, cost conditional on feasibility, and matched constrained baselines. If this evidence is outside scope, the title, summary, and significance framing should consistently present the work as an unconstrained synthetic training-objective experiment.

### R1-M4

**Severity** Major

**Blocking** No

**Axis** Scientific importance and experimental design

**Claim pointer** The study presents full-action counterfactual supervision as a useful technical advance over standard DQN at an equal real-interaction budget.

**Evidence pointer** Algorithm 1; Experimental Design and Settings; Reproducible result entry point; Discussion and Limitations.

**Concern** Equal real interactions do not imply equal information or computational budgets. CBAD obtains analytical outcomes for all three actions at every factual state and performs additional target-network evaluations and gradient calculations. The manuscript reports deployment latency and planner latency but not training wall time, preview-query cost, auxiliary forward-pass cost, or learning curves normalized by compute. It also lacks a comparator designed to exploit the same model-query budget through replay augmentation, supervised policy learning, or another model-assisted value-learning scheme.

**Why it matters** The reported 0.87% to 1.72% deployment-cost improvement may be worthwhile, but its technical impact cannot be judged without the training cost and an information-matched alternative. The present design establishes an objective change against standard DQN, not a general efficiency advantage.

**Resolution test** Report training time, preview calls, network evaluations, and learning curves against both real interactions and compute. Add at least one reasonably tuned comparator using the same analytical full-action information, or narrow the significance claim to the specific matched-backbone attribution experiment.

## Minor Comments

### R1-m1

**Severity** Minor

**Axis** Figures and tables

**Affected element** Variability labels for nonlearned policies in Table `tab:main`.

**Evidence pointer** Table `tab:main` caption and `reviewer_experiments.py`, `seed_level`.

**Issue** The caption describes all values as variability across model-seed blocks. Argmin, MPC, threshold, and fixed policies have no trained model seed. Their blocks are distinct trace namespaces assigned through the model-seed loop.

**Required correction** Distinguish trained-model seed blocks from trace-set blocks and state precisely what the reported SD represents for each policy class.

### R1-m2

**Severity** Minor

**Axis** Reproducibility

**Affected element** Target-network synchronization cadence.

**Evidence pointer** Training configuration; `agent.py`, `DQNAgent.update`; `experiment.py`, update every four interactions.

**Issue** `target_interval=250` is checked against the interaction counter only when an optimizer update occurs. Synchronization therefore happens every 500 real interactions, corresponding to 125 optimizer updates, not every 250 updates.

**Required correction** Report the cadence directly in real interactions and optimizer updates, and rename the checkpoint field or clarify its semantics.

### R1-m3

**Severity** Minor

**Axis** Reproducibility and data-resource quality

**Affected element** Extended-control validation chain.

**Evidence pointer** `extended_revision_validation.json`; `validation.json`; generated extended-ablation tables.

**Issue** The extended validation records row counts, finiteness, and checkpoint hashes, but it does not hash the extended raw, summary, inference, metadata, reporting code, or generated table inputs. The primary validation has broader artifact and source coverage.

**Required correction** Extend the machine-readable manifest to hash the full extended result chain and verify that generated tables are deterministic transforms of the archived inference files.

### R1-m4

**Severity** Minor

**Axis** Figures and tables

**Affected element** Engineering outcome decomposition.

**Evidence pointer** Table `tab:engineering`; primary Results include five fully coupled regimes.

**Issue** The engineering decomposition omits the Burst regime even though it is one of the five primary fully coupled conditions.

**Required correction** Include Burst or explain its exclusion in the table caption.

## Technical failings that need to be addressed before the case is established

R1-M1 and R1-M2 are blocking. The mechanistic attribution must follow the manuscript’s stated adjusted inference standard, and the state representation must support the Bellman formulation or be recast as partially observed.

## Assessment against Nature-style criteria

**Originality** The evaluated combination of full-action analytical preview, factual DQN anchoring, and auxiliary Bellman supervision appears narrowly differentiated from the cited Dyna, counterfactual learning, and advantage-learning literature. The centering element is not independently supported, and broader originality relative to information-matched model-assisted learning remains underdeveloped.

**Scientific importance** The work is potentially useful within model-assisted reinforcement learning and satellite scheduling. Outstanding or far-reaching importance is not established by a 0.87% to 1.72% gain in one synthetic, soft-constrained simulator with arbitrary utility weights and universal energy depletion.

**Interdisciplinary readership** Researchers in autonomous systems, reinforcement learning, operations research, and satellite computing could find the model-use question interesting. The current evidence is unlikely to command broad interdisciplinary interest without feasible-control validation or a more general demonstration.

**Technical soundness** The primary paired CBAD versus standard DQN effect is well documented within the supplied simulator. Technical confidence is limited by the non-Markov observation, inconsistent interpretation of adjusted component-control inference, absence of hard-constrained evaluation, and lack of information-matched compute accounting.

**Readability for nonspecialists** The manuscript is generally well structured, defines the method precisely, and uses useful schematics. The distinction among simulator-exact one-step preview, Bellman correctness, physical fidelity, and deployability should be made more explicit because these concepts can otherwise appear equivalent to nonspecialist readers.

## Recommendation posture

Currently not established from the supplied evidence. The simulator-level primary effect is promising, but support would require resolution of R1-M1 and R1-M2, together with appropriately bounded claims about engineering relevance and efficiency.
