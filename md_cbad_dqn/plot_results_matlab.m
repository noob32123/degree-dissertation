function plot_results_matlab(projectRoot)
%PLOT_RESULTS_MATLAB Rebuild all quantitative manuscript figures in MATLAB.
%
% The script reads only the locked CSV summaries. It preserves the scenario
% order, policy order, seed-level SD error bars, paired bootstrap intervals,
% and action-fraction definitions used by the manuscript. Outputs are written
% as vector PDF/SVG and 600-dpi TIFF, then synchronized to paper/figures.

if nargin < 1 || strlength(string(projectRoot)) == 0
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
end
projectRoot = char(projectRoot);

resultsDir = fullfile(projectRoot, 'md_cbad_dqn', 'results');
outputDir = fullfile(projectRoot, 'md_cbad_dqn', 'figures_matlab');
paperFigureDir = fullfile(projectRoot, 'paper', 'figures');
if ~isfolder(outputDir), mkdir(outputDir); end
if ~isfolder(paperFigureDir), mkdir(paperFigureDir); end

summaryPath = fullfile(resultsDir, 'seven_scenarios_summary.csv');
comparisonPath = fullfile(resultsDir, 'seven_scenarios_paired_bootstrap.csv');
assert(isfile(summaryPath), 'Missing locked summary CSV: %s', summaryPath);
assert(isfile(comparisonPath), 'Missing locked bootstrap CSV: %s', comparisonPath);

summary = readtable(summaryPath, 'TextType', 'string', ...
    'VariableNamingRule', 'preserve');
comparison = readtable(comparisonPath, 'TextType', 'string', ...
    'VariableNamingRule', 'preserve');

scenarioKeys = ["static", "reduced_coupling", "nominal", "burst", ...
    "link_limited", "energy_limited", "thermal_stress"];
scenarioLabels = {'Static (c=0)', 'Reduced (c=0.5)', 'Nominal', 'Burst', ...
    'Link-limited', 'Energy-limited', 'Thermal-stress'};
policyKeys = ["immediate_argmin", "contextual_bandit", "threshold", ...
    "standard_dqn", "md_cfba_dqn", "md_cbad_dqn"];
policyLabels = {'Immediate argmin', 'Contextual bandit', 'Threshold', ...
    'Standard DQN', 'CFBA ablation', 'MD-CBAD-DQN'};
policyColors = [hexrgb('#7f8c8d'); hexrgb('#9b59b6'); hexrgb('#d68910'); ...
    hexrgb('#2874a6'); hexrgb('#17a589'); hexrgb('#c0392b')];

validateLockedData(summary, comparison, scenarioKeys, policyKeys);
plotSevenScenarios(summary, scenarioKeys, scenarioLabels, policyKeys, ...
    policyLabels, policyColors, outputDir, paperFigureDir);
plotAblation(comparison, scenarioKeys(3:end), scenarioLabels(3:end), ...
    outputDir, paperFigureDir);
plotActions(summary, scenarioKeys, scenarioLabels, outputDir, paperFigureDir);
writeQaNotes(outputDir, summaryPath, comparisonPath);

fprintf('MATLAB figures written to %s\n', outputDir);
fprintf('PDF figures synchronized to %s\n', paperFigureDir);
end


function validateLockedData(summary, comparison, scenarios, policies)
assert(height(summary) == 56, 'Expected 56 summary rows, found %d.', height(summary));
assert(numel(unique(string(summary.scenario))) == 7, 'Expected seven scenarios.');

for s = scenarios
    for p = policies
        idx = string(summary.scenario) == s & string(summary.policy) == p;
        assert(nnz(idx) == 1, 'Expected one summary row for %s / %s.', s, p);
        values = [summary.total_cost_mean(idx), summary.total_cost_sd(idx)];
        assert(all(isfinite(values)), 'Non-finite summary value for %s / %s.', s, p);
        assert(summary.n_model_seeds(idx) == 5, 'Expected five model seeds for %s / %s.', s, p);
    end
end

cbad = string(summary.policy) == "md_cbad_dqn";
fractions = summary.onboard_fraction_mean(cbad) + ...
    summary.ground_fraction_mean(cbad) + summary.hybrid_fraction_mean(cbad);
assert(all(abs(fractions - 1) < 1e-10), 'CBAD action fractions do not sum to one.');

neededComparisons = ["md_cfba_dqn - standard_dqn", ...
    "md_cbad_dqn - md_cfba_dqn", "md_cbad_dqn - standard_dqn"];
for s = scenarios(3:end)
    for c = neededComparisons
        idx = string(comparison.scenario) == s & string(comparison.comparison) == c;
        assert(nnz(idx) == 1, 'Expected one bootstrap row for %s / %s.', s, c);
        mu = comparison.mean_difference(idx);
        lo = comparison.ci95_low(idx);
        hi = comparison.ci95_high(idx);
        assert(all(isfinite([mu, lo, hi])) && lo <= mu && mu <= hi, ...
            'Invalid paired interval for %s / %s.', s, c);
        assert(comparison.n_pairs(idx) == 5, 'Expected five seed pairs for %s / %s.', s, c);
    end
end
end


function plotSevenScenarios(summary, scenarios, labels, policies, policyLabels, ...
    colors, outputDir, paperDir)
fig = newFigure(18.3, 15.2);
layout = tiledlayout(fig, 2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
x = 1:numel(scenarios);

ax1 = nexttile(layout, 1);
hold(ax1, 'on');
offsets = linspace(-0.30, 0.30, numel(policies));
handles = gobjects(numel(policies), 1);
for k = 1:numel(policies)
    mu = getSeries(summary, scenarios, policies(k), 'total_cost_mean');
    sd = getSeries(summary, scenarios, policies(k), 'total_cost_sd');
    handles(k) = errorbar(ax1, x + offsets(k), mu, sd, 'o', ...
        'Color', colors(k, :), 'MarkerFaceColor', colors(k, :), ...
        'MarkerEdgeColor', 'white', 'MarkerSize', 4.2, 'LineWidth', 0.9, ...
        'CapSize', 3.5);
end
styleAxes(ax1);
ax1.XTick = x;
ax1.XTickLabel = labels;
xtickangle(ax1, 18);
ylabel(ax1, 'Episode total cost');
title(ax1, '(a) Seven-regime paired evaluation', 'FontWeight', 'normal');
legend(ax1, handles, policyLabels, 'Location', 'northwest', ...
    'NumColumns', 3, 'Box', 'off', 'FontSize', 7.0);
grid(ax1, 'on');
ax1.XGrid = 'off';

ax2 = nexttile(layout, 2);
cbad = getSeries(summary, scenarios, "md_cbad_dqn", 'total_cost_mean');
argmin = getSeries(summary, scenarios, "immediate_argmin", 'total_cost_mean');
improvement = 100 .* (argmin - cbad) ./ argmin;
barColors = repmat(hexrgb('#c0392b'), numel(improvement), 1);
barColors(improvement < 0, :) = repmat(hexrgb('#7f8c8d'), ...
    nnz(improvement < 0), 1);
bars = bar(ax2, x, improvement, 0.68, 'FaceColor', 'flat', ...
    'EdgeColor', 'none');
bars.CData = barColors;
yline(ax2, 0, 'k-', 'LineWidth', 0.8);
styleAxes(ax2);
ax2.XTick = x;
ax2.XTickLabel = labels;
xtickangle(ax2, 18);
ylabel(ax2, {'CBAD improvement over', 'immediate argmin (%)'});
title(ax2, '(b) Temporal-coupling boundary', 'FontWeight', 'normal');
grid(ax2, 'on');
ax2.XGrid = 'off';
ylim(ax2, [min(improvement) - 4, max(improvement) + 5]);
for k = 1:numel(improvement)
    if improvement(k) >= 0
        y = improvement(k) + 0.8;
        valign = 'bottom';
    else
        y = improvement(k) - 0.8;
        valign = 'top';
    end
    text(ax2, x(k), y, sprintf('%.1f', improvement(k)), ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', valign, ...
        'FontName', 'Arial', 'FontSize', 7.0, 'Color', [0.15 0.15 0.15]);
end

exportFigure(fig, outputDir, paperDir, 'fig_seven_scenarios');
end


function plotAblation(comparison, scenarios, labels, outputDir, paperDir)
comparisonKeys = ["md_cfba_dqn - standard_dqn", ...
    "md_cbad_dqn - md_cfba_dqn", "md_cbad_dqn - standard_dqn"];
comparisonLabels = {'CFBA - DQN', 'CBAD - CFBA', 'CBAD - DQN'};
colors = [hexrgb('#17a589'); hexrgb('#d68910'); hexrgb('#c0392b')];
offsets = [-0.22, 0, 0.22];

fig = newFigure(18.3, 9.4);
ax = axes(fig);
hold(ax, 'on');
legendHandles = gobjects(3, 1);
for k = 1:3
    [mu, lo, hi] = getComparisonSeries(comparison, scenarios, comparisonKeys(k));
    yy = (1:numel(scenarios)) + offsets(k);
    for j = 1:numel(scenarios)
        line(ax, [lo(j), hi(j)], [yy(j), yy(j)], 'Color', colors(k, :), ...
            'LineWidth', 1.15);
        line(ax, [lo(j), lo(j)], yy(j) + [-0.055, 0.055], ...
            'Color', colors(k, :), 'LineWidth', 0.9);
        line(ax, [hi(j), hi(j)], yy(j) + [-0.055, 0.055], ...
            'Color', colors(k, :), 'LineWidth', 0.9);
        plot(ax, mu(j), yy(j), 'o', 'Color', colors(k, :), ...
            'MarkerFaceColor', colors(k, :), 'MarkerEdgeColor', 'white', ...
            'MarkerSize', 5.2, 'LineWidth', 0.6);
    end
    legendHandles(k) = plot(ax, nan, nan, 'o-', 'Color', colors(k, :), ...
        'MarkerFaceColor', colors(k, :), 'MarkerEdgeColor', 'white', ...
        'MarkerSize', 5.2, 'LineWidth', 1.15);
end
xline(ax, 0, 'k-', 'LineWidth', 0.8);
styleAxes(ax);
ax.YTick = 1:numel(scenarios);
ax.YTickLabel = labels;
ax.YDir = 'reverse';
ylim(ax, [0.55, numel(scenarios) + 0.45]);
xlabel(ax, 'Paired total-cost difference (negative favors first method)');
title(ax, 'Counterfactual supervision and centering ablation', ...
    'FontWeight', 'normal');
grid(ax, 'on');
ax.YGrid = 'off';
legend(ax, legendHandles, comparisonLabels, 'Location', 'southoutside', ...
    'Orientation', 'horizontal', 'Box', 'off', 'FontSize', 7.2);

exportFigure(fig, outputDir, paperDir, 'fig_cbad_ablation');
end


function plotActions(summary, scenarios, labels, outputDir, paperDir)
fig = newFigure(18.3, 8.6);
ax = axes(fig);
actions = [getSeries(summary, scenarios, "md_cbad_dqn", 'onboard_fraction_mean')', ...
    getSeries(summary, scenarios, "md_cbad_dqn", 'ground_fraction_mean')', ...
    getSeries(summary, scenarios, "md_cbad_dqn", 'hybrid_fraction_mean')'];
bars = bar(ax, 1:numel(scenarios), actions, 0.68, 'stacked', 'EdgeColor', 'none');
actionColors = [hexrgb('#2874a6'); hexrgb('#17a589'); hexrgb('#d68910')];
for k = 1:3
    bars(k).FaceColor = actionColors(k, :);
end
styleAxes(ax);
ax.XTick = 1:numel(scenarios);
ax.XTickLabel = labels;
xtickangle(ax, 18);
ylim(ax, [0, 1]);
ylabel(ax, 'Action fraction');
title(ax, 'MD-CBAD-DQN deployment action distribution', 'FontWeight', 'normal');
legend(ax, bars, {'Onboard', 'Ground', 'Collaborative'}, ...
    'Location', 'northoutside', 'Orientation', 'horizontal', ...
    'Box', 'off', 'FontSize', 7.2);

exportFigure(fig, outputDir, paperDir, 'fig_action_distribution');
end


function values = getSeries(tbl, scenarios, policy, column)
values = zeros(1, numel(scenarios));
for k = 1:numel(scenarios)
    idx = string(tbl.scenario) == scenarios(k) & string(tbl.policy) == policy;
    assert(nnz(idx) == 1, 'Expected one row for %s / %s.', scenarios(k), policy);
    values(k) = tbl.(column)(idx);
end
assert(all(isfinite(values)), 'Non-finite values in %s.', column);
end


function [mu, lo, hi] = getComparisonSeries(tbl, scenarios, comparisonKey)
mu = zeros(1, numel(scenarios));
lo = zeros(1, numel(scenarios));
hi = zeros(1, numel(scenarios));
for k = 1:numel(scenarios)
    idx = string(tbl.scenario) == scenarios(k) & ...
        string(tbl.comparison) == comparisonKey;
    assert(nnz(idx) == 1, 'Expected one comparison row for %s / %s.', ...
        scenarios(k), comparisonKey);
    mu(k) = tbl.mean_difference(idx);
    lo(k) = tbl.ci95_low(idx);
    hi(k) = tbl.ci95_high(idx);
end
end


function fig = newFigure(widthCm, heightCm)
fig = figure('Visible', 'off', 'Color', 'white', 'Units', 'centimeters', ...
    'Position', [2, 2, widthCm, heightCm], 'PaperPositionMode', 'auto');
end


function styleAxes(ax)
set(ax, 'FontName', 'Arial', 'FontSize', 7.5, 'LineWidth', 0.75, ...
    'TickDir', 'out', 'Box', 'off', 'Color', 'white', ...
    'GridColor', [0.82 0.82 0.82], 'GridAlpha', 0.55, ...
    'TickLabelInterpreter', 'none', 'Layer', 'top');
end


function exportFigure(fig, outputDir, paperDir, stem)
fontObjects = findall(fig, '-property', 'FontName');
for k = 1:numel(fontObjects)
    fontObjects(k).FontName = 'Arial';
end
drawnow;
pdfPath = fullfile(outputDir, stem + ".pdf");
svgPath = fullfile(outputDir, stem + ".svg");
tiffPath = fullfile(outputDir, stem + ".tiff");
exportgraphics(fig, pdfPath, 'ContentType', 'vector', 'BackgroundColor', 'white');
exportgraphics(fig, svgPath, 'ContentType', 'vector', 'BackgroundColor', 'white');
exportgraphics(fig, tiffPath, 'Resolution', 600, 'BackgroundColor', 'white');
forceSvgArial(svgPath);
copyfile(pdfPath, fullfile(paperDir, stem + ".pdf"), 'f');
copyfile(svgPath, fullfile(paperDir, stem + ".svg"), 'f');
close(fig);
end


function forceSvgArial(svgPath)
svgText = fileread(svgPath);
svgText = regexprep(svgText, 'font-family="[^"]+"', 'font-family="Arial"');
fid = fopen(svgPath, 'w', 'n', 'UTF-8');
assert(fid ~= -1, 'Could not rewrite SVG font declarations: %s', svgPath);
cleanup = onCleanup(@() fclose(fid));
fwrite(fid, svgText, 'char');
clear cleanup;
end


function rgb = hexrgb(hex)
hex = char(erase(string(hex), '#'));
assert(numel(hex) == 6, 'Expected six-digit hexadecimal color.');
rgb = [hex2dec(hex(1:2)), hex2dec(hex(3:4)), hex2dec(hex(5:6))] ./ 255;
end


function writeQaNotes(outputDir, summaryPath, comparisonPath)
notesPath = fullfile(outputDir, 'MATLAB_FIGURE_QA.txt');
fid = fopen(notesPath, 'w');
assert(fid ~= -1, 'Could not write QA notes.');
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, 'Backend: MATLAB R%s\n', version('-release'));
fprintf(fid, 'Summary source: %s\n', summaryPath);
fprintf(fid, 'Bootstrap source: %s\n', comparisonPath);
fprintf(fid, 'Summary rows: 56; scenarios: 7; policies: 8.\n');
fprintf(fid, 'Primary error bars: SD across five model seeds.\n');
fprintf(fid, 'Ablation intervals: fixed-seed 95%% paired bootstrap intervals.\n');
fprintf(fid, 'Action fractions: mean deployment fractions; each scenario sums to one.\n');
fprintf(fid, 'Exports: vector PDF/SVG and 600-dpi TIFF.\n');
fprintf(fid, 'No observations, scenarios, policies, or requested comparisons were excluded.\n');
clear cleanup;
end
