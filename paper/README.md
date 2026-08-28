# Current manuscript package

The authoritative source is source.tex. References are stored in ref.bib. All included figures and LaTeX table inputs are retained under figures and generated.

Primary and extended numerical tables are generated from ../md_cbad_dqn/results/reviewer_revision_state_complete by:

```powershell
H:\anaconda\envs\yolo\python.exe -m md_cbad_dqn.reviewer_reporting
H:\anaconda\envs\yolo\python.exe -m md_cbad_dqn.extended_reporting
```

Run H:\anaconda\envs\yolo\python.exe paper/audit_manuscript.py from the repository root for manuscript checks.

The clean release files are:

- output/pdf/dqn_variants_satellite_ground_manuscript.pdf
- output/pdf/dqn_variants_satellite_ground_manuscript.log
- output/pdf/SHA256SUMS.txt

Superseded source snapshots, marked manuscripts, duplicate PDFs, auxiliary files and rendered page previews are preserved under ../archive/history_before_current_2026-08-27/paper.
