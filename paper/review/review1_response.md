# Response to Reviewer 1

We thank Reviewer 1 for identifying weaknesses in the original problem formulation, parameter generation, baselines, and reporting. We rebuilt the simulation evidence rather than adding only explanatory text. The revised study uses a physically coupled generator, an exact four-step receding-horizon comparator, per-episode resource diagnostics, and prespecified parameter sensitivity. All new learned models were retrained with five fixed seeds and evaluated on shared traces. We also narrowed claims wherever the new evidence did not reproduce an earlier mechanism-level conclusion.

## Comment 1

> The problem is a static single-satellite/single-ground-station problem, and traditional algorithms can quickly obtain the optimum. Please clarify why reinforcement learning is applicable.

**Response.** We now distinguish the topology from the decision dynamics. The topology remains deliberately limited to one satellite and one ground-processing path, but the decision process is not static: each action changes heat, energy, queue occupancy, compute utilization, bandwidth, and remaining contact before the next task. We added an exact receding-horizon model-based comparator that enumerates all (3^4) four-step action sequences under perfect forecasts. It is exact for the stated four-step objective and is not presented as the 64-step global optimum. Immediate minimization and MPC-4 are preferable when coupling is absent or weak; CBAD is better than MPC-4 in the five fully coupled regimes. We therefore limit the motivation to resource effects that persist beyond a short planning horizon and explicitly state that the comparison does not establish superiority over all traditional optimization.

**Changes.** See “Planning comparator, outcomes, and inference” (manuscript lines 371–375), revised Results (lines 384–404), and Discussion (lines 457–465).

## Comment 2

> Independently sampled parameters ignore coupling and may create physically contradictory samples. No communication model or fitted real distribution is provided.

**Response.** We replaced the independently sampled task generator for all revised experiments. Correlated latent variables now generate raw data volume and arithmetic workload. Result volume, collaborative feature volume, processing time, compute energy, heat, transmission time, and transmission heat are derived from shared primitives. The implementation enforces result data (le) feature data (le) raw data. Effective return rate is a bounded function of link state. An automated audit of 20,000 tasks verifies finite positive values and all data-flow inequalities; the empirical raw-data–workload correlation is 0.660. Figure 3 reports the dependence structure.

We agree that this does not replace telemetry fitting. The revised paper labels the ranges as engineering envelopes, not flight distributions, cites NASA/CCSDS sources for selected bounds, and retains absence of flight-derived joint distributions as a limitation. This component is therefore materially addressed but remains only partially resolved with respect to real-distribution validation.

**Changes.** See “Physically coupled task and communication generator” (lines 183–211), Table 1, Figure 3, and Discussion (lines 463–465).

## Comment 3

> The parameter ranges are unreasonable and require further study.

**Response.** Table 1 now gives units, implemented ranges, and the basis of every physical primitive. NASA Small Spacecraft Technology sources bound computing-system power and representative ground-network return rates; CCSDS supports the stated role of onboard image compression. We then evaluated the locked models under eight prespecified profiles: compute demand ±20%, input volume ±20%, energy use +20%, heat load +20%, link capacity −20%, and the reference profile. CBAD–DQN 95% paired intervals remained below zero in all eight profiles, with relative reductions of 1.81%–7.43%. We explicitly restrict robustness to these envelopes.

**Changes.** See Table 1, “Prespecified sensitivity and training diagnostics” (lines 377–380), Table 4, Figure 8, and Results lines 428–449.

## Comment 4

> The definition and logic of the accuracy metric are unclear.

**Response.** The undefined accuracy metric remains removed. Episode total cost is the primary outcome; resource use, modeled latency, delayed penalties, violations, transmitted data, action fractions, and planning time are named secondary outcomes. No optimal-action label is used.

**Changes.** See lines 371–375 and 417–426.

## Comment 5

> The original figure does not demonstrate convergence. Please show episode-wise performance and critical quantities such as energy and latency.

**Response.** We logged every training episode for five independent model seeds and added four panels for total cost, energy use, modeled latency, and delayed feasibility penalty. Lines show a causal 25-episode moving mean; bands show ±1 SD across seeds. We describe empirical stabilization after approximately 220 episodes and explicitly avoid claiming mathematical convergence.

**Changes.** See Figure 7 and lines 417–426.

## Comment 6

> The proposed method was not compared with unoptimized DQN; relevant mechanisms require ablation.

**Response.** The revised study directly compares the complete MD-CBAD-DQN objective with an unmodified standard DQN using identical networks, standard DQN targets, uniform one-step replay, exploration, update cadence, and training budgets. No Double DQN, dueling network, prioritized replay, n-step return, noisy network, or distributional DQN is used. MD-CBAD-DQN improves on standard DQN in all five fully coupled regimes, with every paired interval below zero. Epsilon reset and replay flushing are not components of the current method and therefore are not presented as ablations.

**Changes.** See the matched-method specification and the seven-regime main results.

## Comment 7

> Remove the superscript “1” in the abstract.

**Response.** The abstract contains no superscript “1”. Affiliation superscripts remain only in the author block.

## Comment 8

> Remove the claim that detailed data are in source files because the project is not open source.

**Response.** The unsupported public-availability wording has been removed. The statement now says that simulator code, checkpoints, raw results, and regeneration scripts are available from the corresponding authors upon reasonable request. It states that a permanent URL or DOI will be inserted only if the materials are made public before publication.

**Changes.** See “Data and Code Availability” (lines 475–477).

## Verified revision status

- Resolved: Comments 1, 3, 4, 5, 6, 7, and 8.
- Partially resolved: Comment 2, because the revised generator is physically constrained and source-bounded but is not fitted to flight telemetry.
