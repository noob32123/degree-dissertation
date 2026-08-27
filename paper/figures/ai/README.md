# Conceptual figure inventory

## Selected assets

| File | Purpose | Human scientific checks and corrections |
|---|---|---|
| `fig_graphical_abstract_arial.png` | Superseded one-panel overview of the three actions, all-action preview, within-state centering, standard-DQN path, and coupling boundary | Added direct labels for all actions, resources, target cards, the task stream, and Q outputs; converted all visible typography to Arial. The manuscript now uses the simulator-exact-labelled revision below. |
| `fig_system_modes_arial.png` | Three satellite-ground processing pathways and six post-action resource classes | Added component-level labels for computation, transmitted data, link stages, ground completion, and all six post-action resources; converted all visible typography to Arial. |
| `fig_cbad_mechanism_arial.png` | Factual DQN and training-only CBAD auxiliary paths | Added lane, action-key, loss, centering, online-network, synchronization, and test-time restriction labels; converted all visible typography to Arial; verified that no DDQN or other DQN extension is depicted. |
| `fig_experiment_protocol_arial.png` | Disjoint calibration, lock, confirmation, and seven-regime evaluation | Added labels for independent models, locked configuration, shared traces, stage transitions, and the two-plus-five regime grouping; converted all visible typography to Arial; verified all seeds, weights, paired traces, and no-retraining condition. |
| `fig_experiment_protocol_20seeds_arial.png` | Revised confirmatory protocol after statistical review | Explicitly labels all 20 independent model seeds (800--819), the locked configuration, paired traces, and the seven evaluation regimes. |
| `fig_graphical_abstract_simulator_exact_arial.png` | Scope-corrected graphical overview | Replaces “EXACT PREVIEW” with “SIMULATOR-EXACT PREVIEW”; all other visual content is preserved. |
| `fig_cbad_mechanism_simulator_exact_arial.png` | Scope-corrected mechanism diagram | Replaces “EXACT PREVIEW” with “SIMULATOR-EXACT PREVIEW”; all other visual content is preserved. |

The predecessor files remain in this directory as rollback assets. The manuscript references the final Arial-labelled assets identified in `source.tex`.

## Integrity boundary

The quantitative figures are direct MATLAB exports from the locked CSV results. The manuscript captions remain the authoritative interpretation of every conceptual illustration.

## Submission checklist

- Re-check the selected journal's disclosure and AI-generated-image policy before submission.
- Preserve this provenance record with the source package.
- Reconfirm every label and arrow after any later image edit.
- Do not use the conceptual illustrations as evidence for a quantitative claim.
