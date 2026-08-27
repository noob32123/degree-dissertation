# Manuscript

The clean manuscript source is `source.tex`. The baseline for the current
state-completeness revision is `source_pre_state_complete_revision_2026-08-27.tex`; the marked manuscript is
generated from that baseline after the clean text is finalized. Primary and
second-round numerical tables are generated from
`../md_cbad_dqn/results/reviewer_revision_state_complete/` rather than maintained manually.
Run `python -m md_cbad_dqn.reviewer_reporting` followed by
`python -m md_cbad_dqn.extended_reporting` to synchronize the LaTeX tables.

Run `python paper/audit_manuscript.py` from the repository root to check sentence length, citation keys, cross-references, and prohibited dash-based prose before compilation.

Final outputs:

- `output/pdf/dqn_variants_satellite_ground_manuscript.pdf`
- `output/pdf/dqn_variants_satellite_ground_manuscript_marked.pdf`

The source uses a generic 11pt single-column preprint layout and replaces the superseded manuscript in full. The marked PDF shows inserted or replaced visible blocks in red relative to `source_pre_state_complete_revision_2026-08-27.tex`.
