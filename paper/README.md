# Manuscript

The manuscript source is `source.tex`. Numerical results, LaTeX tables, and plotted figures are generated from `../md_cbad_dqn/results/seven_scenarios_raw.csv`; they are not maintained manually. Running `python -m md_cbad_dqn.reporting` regenerates and synchronizes the manuscript assets.

Run `python paper/audit_manuscript.py` from the repository root to check sentence length, citation keys, cross-references, and prohibited dash-based prose before compilation.

Final output:

`output/pdf/md_cbad_dqn_manuscript.pdf`

The source uses a generic 11pt single-column preprint layout and replaces the superseded manuscript in full.
