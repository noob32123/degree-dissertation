# AI-assisted conceptual figure provenance

Status: internal design draft; submission eligibility remains subject to the target journal's current policy.

Generation date: 2026-08-26  
Provider: OpenAI built-in ImageGen (the tool did not expose a model-version identifier)  
Scientific scope: conceptual system, mechanism, and protocol illustrations only. No measured or simulated result was generated, estimated, or altered by an image model.

## Selected assets

| File | Purpose | Human scientific checks and corrections |
|---|---|---|
| `fig_graphical_abstract_arial.png` | One-panel overview of the three actions, exact all-action preview, within-state centering, standard-DQN path, and coupling boundary | Added direct labels for all actions, resources, target cards, the task stream, and Q outputs; converted all visible typography to Arial; verified the centering order, unchanged standard-DQN branch, and absence of numerical performance claims. |
| `fig_system_modes_arial.png` | Three satellite-ground processing pathways and six post-action resource classes | Added component-level labels for computation, transmitted data, link stages, ground completion, and all six post-action resources; converted all visible typography to Arial. |
| `fig_cbad_mechanism_arial.png` | Factual DQN and training-only CBAD auxiliary paths | Added lane, action-key, loss, centering, online-network, synchronization, and test-time restriction labels; converted all visible typography to Arial; verified that no DDQN or other DQN extension is depicted. |
| `fig_experiment_protocol_arial.png` | Disjoint calibration, lock, confirmation, and seven-regime evaluation | Added labels for independent models, locked configuration, shared traces, stage transitions, and the two-plus-five regime grouping; converted all visible typography to Arial; verified all seeds, weights, paired traces, and no-retraining condition. |

The predecessor files remain in this directory as rollback assets. The manuscript references only the four `_arial.png` files.

## Integrity boundary

The quantitative files `fig_seven_scenarios.pdf`, `fig_cbad_ablation.pdf`, and `fig_action_distribution.pdf` are direct MATLAB exports from the locked CSV results. They were not generated, retouched, or relabeled with generative AI. The manuscript captions remain the authoritative interpretation of every conceptual illustration.

## Submission checklist

- Re-check the selected journal's disclosure and AI-generated-image policy before submission.
- Preserve this provenance record with the source package.
- Reconfirm every label and arrow after any later image edit.
- Do not use the conceptual illustrations as evidence for a quantitative claim.
