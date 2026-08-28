# Immutable review packet

## Input scope

- Full polished manuscript source: `H:\degree-dissertation\paper\source.tex`
- Compiled clean manuscript: `H:\degree-dissertation\paper\output\pdf\dqn_variants_satellite_ground_manuscript.pdf`
- Generated tables and macros: `H:\degree-dissertation\paper\generated\`
- Machine-readable result basis: `H:\degree-dissertation\md_cbad_dqn\results\reviewer_revision_state_complete\`
- Manuscript audit output is reproducible with `H:\degree-dissertation\paper\audit_manuscript.py`.

## Assessment boundary

This is a full-manuscript pre-submission review. Assess the scientific case presented in the manuscript and the visible local evidence package. Do not make an editorial decision, draft an author response, conduct a new literature search, or infer experiments absent from the supplied files. Mark any item that cannot be assessed from the packet.

## Common Nature-style criteria

Assess originality, scientific importance, interdisciplinary readership, technical soundness, and readability for nonspecialists. Identify who would be interested in the results and why. Identify technical failings that must be resolved before the authors' case is established.

## Verified manuscript anchors

- Abstract
- Section 1, Introduction
- Section 2, Related Work and Study Positioning
- Section 3, System Model and Immediate-Cost Quantification
- Section 4, Sequential Scheduling Formulation
- Section 5, DQN Variants with Model-Evaluated Full-Action Targets
- Section 6, Experimental Design and Settings
- Section 7, Results
- Section 8, Discussion, including Section 8.1 Future work
- Section 9, Conclusion
- Table 1, closest method families
- Table 6, primary episode total cost comparison
- Table 7, seed-level primary inference
- Table 9, six-objective DQN family performance
- Table 12, planning-depth comparison
- Table 13, engineering outcome decomposition
- Figures 6 through 11, primary results, seed effects, DQN family, planning and sensitivity, training diagnostics, and action fractions

## Shared manuscript claim summary

The manuscript evaluates six DQN objectives in a reproducible synthetic, soft-constrained satellite-ground scheduling benchmark. Its central claim is family-level. Across five fully coupled regimes, all 30 DQN objective-regime means are below the corresponding strongest implemented non-DQN comparator, MPC-4. Differences within the DQN family are smaller and scenario dependent. The manuscript presents exact finite-horizon planning through depth six and organizes hard constraints, mission-derived validation, sharper mechanism identification, and wider baselines as future work.

## Visible evidence base

The manuscript reports 20 independently trained model seeds, 20 shared held-out traces per seed, paired bootstrap intervals, paired sign tests with Holm adjustment, independent-seed sensitivity intervals, planning depths 1, 2, 4, and 6, parameter perturbations, preview-scale perturbations, training diagnostics, and action-mixture summaries. Equations define the simulator, reward, transitions, DQN objectives, and episode total cost. Local code, checkpoints, generated tables, and validation metadata are present in the workspace.

## Missing materials affecting confidence

- No permanent public data or code archive identifier is supplied.
- No mission telemetry, hardware-in-the-loop validation, or second scheduling task is included.
- No target journal beyond Nature-style assessment criteria is specified.

## Common report contract

Return one reviewer report only. Use the sections Overall assessment, Who would be interested and why, Major strengths, Major Concerns, Minor Comments, Technical failings that need to be addressed before the case is established, Assessment against Nature-style criteria, and Recommendation posture.

Each Major Concern must include a stable ID, severity Major, Blocking Yes or No, axis, claim pointer, evidence pointer, concern, why it matters, and resolution test. Each Minor Comment must include a stable ID, severity Minor, axis, affected element, evidence pointer, issue, and required correction. Do not invent identities or use another review. Avoid em-dash and en-dash punctuation in prose.
