# MATLAB quantitative figures

These files are generated exclusively by `../plot_results_matlab.m` from the
locked CSV summaries in `../results/`.

- `fig_seven_scenarios`: seven-regime mean total cost with model-seed SD, plus
  the temporal-coupling boundary relative to immediate argmin.
- `fig_cbad_ablation`: seed-paired mean differences with fixed-seed 95% paired
  bootstrap intervals.
- `fig_action_distribution`: mean MD-CBAD-DQN deployment action fractions.

Each figure is exported as editable vector PDF/SVG and 600-dpi TIFF. The PDF
and SVG versions are synchronized to `paper/figures/`. Data assertions verify
all seven scenarios, required policies, five model seeds, interval ordering,
and action-fraction sums before drawing.
