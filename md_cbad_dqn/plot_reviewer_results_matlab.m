function plot_reviewer_results_matlab(projectRoot)
%PLOT_REVIEWER_RESULTS_MATLAB Draw reviewer-revision quantitative figures.
%
% Conclusion: physically coupled tasks retain the CBAD-versus-DQN effect
% across prespecified parameter envelopes; learning curves report cost,
% energy, latency, and delayed penalties; MPC-4 bounds the planning claim.
% Inference uses five model seeds. No Python plotting code is used.

if nargin < 1 || strlength(string(projectRoot)) == 0
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
end
projectRoot = char(projectRoot);
resultsDir = fullfile(projectRoot, 'md_cbad_dqn', 'results', 'reviewer_revision');
outputDir = fullfile(projectRoot, 'md_cbad_dqn', 'figures_matlab', 'reviewer_revision');
paperDir = fullfile(projectRoot, 'paper', 'figures');
if ~isfolder(outputDir), mkdir(outputDir); end
if ~isfolder(paperDir), mkdir(paperDir); end

summary = readtable(fullfile(resultsDir, 'seven_regimes_summary.csv'), ...
    'TextType', 'string', 'VariableNamingRule', 'preserve');
curves = readtable(fullfile(resultsDir, 'training_curves.csv'), ...
    'TextType', 'string', 'VariableNamingRule', 'preserve');
sensitivity = readtable(fullfile(resultsDir, 'sensitivity_paired_bootstrap.csv'), ...
    'TextType', 'string', 'VariableNamingRule', 'preserve');
sample = readtable(fullfile(resultsDir, 'parameter_audit_sample.csv'), ...
    'TextType', 'string', 'VariableNamingRule', 'preserve');

validateData(summary, curves, sensitivity, sample);
plotPhysicalGenerator(sample, outputDir, paperDir);
plotTrainingDiagnostics(curves, outputDir, paperDir);
plotPrimaryResults(summary, outputDir, paperDir);
plotSensitivityPlanning(summary, sensitivity, outputDir, paperDir);
plotActionDistribution(summary, outputDir, paperDir);
writeQa(outputDir, resultsDir);
fprintf('Reviewer-revision MATLAB figures written to %s\n', outputDir);
end


function validateData(summary, curves, sensitivity, sample)
assert(height(summary) == 63, 'Expected 7 x 9 = 63 summary rows.');
assert(height(curves) == 12000, 'Expected 4 x 5 x 600 = 12000 curve rows.');
assert(height(sensitivity) == 16, 'Expected 8 profiles x 2 comparisons.');
assert(height(sample) == 20000, 'Expected 20,000 generator-audit tasks.');
assert(all(isfinite(summary.total_cost_mean)), 'Non-finite main result.');
assert(all(isfinite(sample.raw_mbit)) && all(isfinite(sample.workload_gflop)), ...
    'Non-finite physical primitive.');
assert(all(sample.result_mbit <= sample.feature_mbit), ...
    'Result data exceed collaborative feature data.');
assert(all(sample.feature_mbit <= sample.raw_mbit), ...
    'Feature data exceed raw input data.');
assert(numel(unique(curves.model_seed)) == 5, 'Expected five training seeds.');
end


function plotPhysicalGenerator(sample, outputDir, paperDir)
fig = newFigure(18.3, 8.7);
layout = tiledlayout(fig, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

ax1 = nexttile(layout, 1);
idx = 1:10:height(sample);
scatter(ax1, sample.raw_mbit(idx), sample.workload_gflop(idx), 11, ...
    sample.onboard_heat_j(idx), 'filled', 'MarkerFaceAlpha', 0.58);
styleAxes(ax1);
xlabel(ax1, 'Raw task data (Mbit)');
ylabel(ax1, 'Arithmetic workload (GFLOP)');
title(ax1, '(a) Shared task primitives', 'FontWeight', 'normal');
grid(ax1, 'on');
cb = colorbar(ax1);
cb.Label.String = 'Derived onboard heat (J)';
cb.FontName = 'Arial';
cb.FontSize = 7.2;

ax2 = nexttile(layout, 2);
matrix = [sample.raw_mbit, sample.workload_gflop, sample.result_mbit, ...
    sample.feature_mbit, sample.onboard_heat_j, sample.ground_tx_heat_j];
correlations = corrcoef(matrix);
imagesc(ax2, correlations, [-1, 1]);
colormap(ax2, divergingMap(256));
labels = {'Raw data', 'Workload', 'Result data', 'Feature data', ...
    'Onboard heat', 'Tx heat'};
ax2.XTick = 1:6; ax2.YTick = 1:6;
ax2.XTickLabel = labels; ax2.YTickLabel = labels;
xtickangle(ax2, 38);
styleAxes(ax2);
ax2.Box = 'on';
title(ax2, '(b) Empirical parameter correlation', 'FontWeight', 'normal');
for row = 1:6
    for col = 1:6
        if abs(correlations(row, col)) > 0.55
            textColor = 'white';
        else
            textColor = [0.12 0.12 0.12];
        end
        text(ax2, col, row, sprintf('%.2f', correlations(row, col)), ...
            'HorizontalAlignment', 'center', 'FontName', 'Arial', ...
            'FontSize', 6.5, 'Color', textColor);
    end
end
exportFigure(fig, outputDir, paperDir, 'fig_physical_generator');
end


function plotTrainingDiagnostics(curves, outputDir, paperDir)
fig = newFigure(18.3, 13.2);
layout = tiledlayout(fig, 2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
variants = ["standard_dqn", "md_cbad_dqn"];
variantLabels = {'Standard DQN', 'MD-CBAD-DQN'};
colors = [hexrgb('#2874A6'); hexrgb('#C0392B')];
metrics = {'cost', 'energy_use', 'latency_ms', 'penalty'};
ylabels = {'Episode total cost', 'Episode energy use (normalized)', ...
    'Episode latency (s)', 'Delayed penalty'};
titles = {'(a) Total cost', '(b) Energy use', '(c) Latency', ...
    '(d) Delayed feasibility penalty'};
for panel = 1:4
    ax = nexttile(layout, panel);
    hold(ax, 'on');
    handles = gobjects(2, 1);
    for v = 1:2
        [episode, values] = seedMatrix(curves, variants(v), metrics{panel});
        if strcmp(metrics{panel}, 'latency_ms'), values = values / 1000; end
        values = movmean(values, [24, 0], 1, 'omitnan');
        mu = mean(values, 2, 'omitnan');
        sd = std(values, 0, 2, 'omitnan');
        fill(ax, [episode; flipud(episode)], [mu-sd; flipud(mu+sd)], ...
            colors(v, :), 'FaceAlpha', 0.15, 'EdgeColor', 'none');
        handles(v) = plot(ax, episode, mu, 'Color', colors(v, :), ...
            'LineWidth', 1.25);
    end
    styleAxes(ax);
    grid(ax, 'on');
    xlabel(ax, 'Training episode');
    ylabel(ax, ylabels{panel});
    title(ax, titles{panel}, 'FontWeight', 'normal');
    xlim(ax, [1, 600]);
    if panel == 1
        legend(ax, handles, variantLabels, 'Location', 'northeast', ...
            'Box', 'off', 'FontSize', 7.2);
    end
end
exportFigure(fig, outputDir, paperDir, 'fig_training_diagnostics');
end


function [episode, values] = seedMatrix(curves, variant, metric)
subset = curves(string(curves.variant) == variant, :);
seeds = sort(unique(subset.model_seed));
assert(numel(seeds) == 5, 'Expected five seeds for %s.', variant);
episode = (1:600)';
values = nan(600, 5);
for k = 1:5
    one = subset(subset.model_seed == seeds(k), :);
    one = sortrows(one, 'episode');
    assert(height(one) == 600, 'Expected 600 episodes for %s seed %d.', variant, seeds(k));
    values(:, k) = one.(metric);
end
end


function plotPrimaryResults(summary, outputDir, paperDir)
scenarios = ["static", "reduced_coupling", "nominal", "burst", ...
    "link_limited", "energy_limited", "thermal_stress"];
labels = {'Static', 'Reduced', 'Nominal', 'Burst', 'Link-limited', ...
    'Energy-limited', 'Thermal-stress'};
policies = ["immediate_argmin", "mpc_h4", "contextual_bandit", ...
    "threshold", "standard_dqn", "md_cfba_dqn", "md_cbad_dqn"];
policyLabels = {'Argmin', 'MPC-4', 'Bandit', 'Threshold', 'DQN', 'CFBA', 'CBAD'};
colors = [hexrgb('#7F8C8D'); hexrgb('#34495E'); hexrgb('#9B59B6'); ...
    hexrgb('#D68910'); hexrgb('#2874A6'); hexrgb('#17A589'); hexrgb('#C0392B')];

fig = newFigure(18.3, 13.1);
layout = tiledlayout(fig, 2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
for panel = 1:2
    ax = nexttile(layout, panel);
    hold(ax, 'on');
    if panel == 1
        selected = 1:2;
        panelTitle = '(a) Coupling controls';
    else
        selected = 3:7;
        panelTitle = '(b) Fully coupled operating regimes';
    end
    x = 1:numel(selected);
    offsets = linspace(-0.30, 0.30, numel(policies));
    handles = gobjects(numel(policies), 1);
    for p = 1:numel(policies)
        mu = getSeries(summary, scenarios(selected), policies(p), 'total_cost_mean');
        sd = getSeries(summary, scenarios(selected), policies(p), 'total_cost_sd');
        handles(p) = errorbar(ax, x + offsets(p), mu, sd, 'o', ...
            'Color', colors(p, :), 'MarkerFaceColor', colors(p, :), ...
            'MarkerEdgeColor', 'white', 'MarkerSize', 4.0, ...
            'LineWidth', 0.9, 'CapSize', 3.0);
    end
    styleAxes(ax);
    grid(ax, 'on'); ax.XGrid = 'off';
    ax.XTick = x; ax.XTickLabel = labels(selected);
    ylabel(ax, 'Episode total cost');
    title(ax, panelTitle, 'FontWeight', 'normal');
    if panel == 1
        legend(ax, handles, policyLabels, 'Location', 'northoutside', ...
            'Orientation', 'horizontal', 'NumColumns', 7, 'Box', 'off', ...
            'FontSize', 6.8);
    end
end
exportFigure(fig, outputDir, paperDir, 'fig_reviewer_primary');
end


function plotSensitivityPlanning(summary, sensitivity, outputDir, paperDir)
fig = newFigure(18.3, 9.5);
layout = tiledlayout(fig, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

ax1 = nexttile(layout, 1);
profiles = ["reference", "compute_minus20", "compute_plus20", ...
    "data_minus20", "data_plus20", "energy_plus20", "heat_plus20", "link_minus20"];
labels = {'Reference', 'Compute -20%', 'Compute +20%', 'Data -20%', ...
    'Data +20%', 'Energy +20%', 'Heat +20%', 'Link -20%'};
selected = sensitivity(string(sensitivity.comparison) == ...
    "md_cbad_dqn - standard_dqn", :);
hold(ax1, 'on');
for k = 1:numel(profiles)
    row = selected(string(selected.profile) == profiles(k), :);
    assert(height(row) == 1, 'Missing sensitivity profile %s.', profiles(k));
    line(ax1, [row.ci95_low, row.ci95_high], [k, k], ...
        'Color', hexrgb('#C0392B'), 'LineWidth', 1.25);
    plot(ax1, row.mean_difference, k, 'o', 'Color', hexrgb('#C0392B'), ...
        'MarkerFaceColor', hexrgb('#C0392B'), 'MarkerEdgeColor', 'white', ...
        'MarkerSize', 5.0);
end
xline(ax1, 0, 'k-', 'LineWidth', 0.8);
styleAxes(ax1); grid(ax1, 'on'); ax1.YGrid = 'off';
ax1.YTick = 1:8; ax1.YTickLabel = labels; ax1.YDir = 'reverse';
ylim(ax1, [0.5, 8.5]);
xlabel(ax1, 'CBAD - DQN total cost');
title(ax1, '(a) Prespecified parameter envelopes', 'FontWeight', 'normal');

ax2 = nexttile(layout, 2);
scenarios = ["static", "reduced_coupling", "nominal", "burst", ...
    "link_limited", "energy_limited", "thermal_stress"];
labels2 = {'Static', 'Reduced', 'Nominal', 'Burst', 'Link', 'Energy', 'Thermal'};
mpc = getSeries(summary, scenarios, "mpc_h4", 'total_cost_mean');
cbad = getSeries(summary, scenarios, "md_cbad_dqn", 'total_cost_mean');
argmin = getSeries(summary, scenarios, "immediate_argmin", 'total_cost_mean');
data = [argmin(:), mpc(:), cbad(:)];
bars = bar(ax2, 1:7, data, 0.76, 'grouped', 'EdgeColor', 'none');
bars(1).FaceColor = hexrgb('#7F8C8D');
bars(2).FaceColor = hexrgb('#34495E');
bars(3).FaceColor = hexrgb('#C0392B');
styleAxes(ax2); grid(ax2, 'on'); ax2.XGrid = 'off';
ax2.XTick = 1:7; ax2.XTickLabel = labels2; xtickangle(ax2, 32);
ylabel(ax2, 'Episode total cost');
title(ax2, '(b) Four-step planning comparator', 'FontWeight', 'normal');
legend(ax2, bars, {'Argmin', 'MPC-4', 'CBAD'}, 'Location', 'northwest', ...
    'Box', 'off', 'FontSize', 7.2);
exportFigure(fig, outputDir, paperDir, 'fig_sensitivity_planning');
end


function plotActionDistribution(summary, outputDir, paperDir)
scenarios = ["static", "reduced_coupling", "nominal", "burst", ...
    "link_limited", "energy_limited", "thermal_stress"];
labels = {'Static', 'Reduced', 'Nominal', 'Burst', 'Link-limited', ...
    'Energy-limited', 'Thermal-stress'};
actions = [getSeries(summary, scenarios, "md_cbad_dqn", 'onboard_fraction_mean')', ...
    getSeries(summary, scenarios, "md_cbad_dqn", 'ground_fraction_mean')', ...
    getSeries(summary, scenarios, "md_cbad_dqn", 'hybrid_fraction_mean')'];
assert(all(abs(sum(actions, 2) - 1) < 1e-9), 'Action fractions do not sum to one.');
fig = newFigure(18.3, 8.2);
ax = axes(fig);
bars = bar(ax, 1:7, actions, 0.70, 'stacked', 'EdgeColor', 'none');
bars(1).FaceColor = hexrgb('#2874A6');
bars(2).FaceColor = hexrgb('#17A589');
bars(3).FaceColor = hexrgb('#D68910');
styleAxes(ax);
ax.XTick = 1:7; ax.XTickLabel = labels; xtickangle(ax, 18);
ylim(ax, [0, 1]); ylabel(ax, 'Action fraction');
title(ax, 'MD-CBAD-DQN deployment action distribution', 'FontWeight', 'normal');
legend(ax, bars, {'Onboard', 'Ground', 'Collaborative'}, ...
    'Location', 'northoutside', 'Orientation', 'horizontal', ...
    'Box', 'off', 'FontSize', 7.2);
exportFigure(fig, outputDir, paperDir, 'fig_reviewer_actions');
end


function values = getSeries(tbl, scenarios, policy, column)
values = zeros(1, numel(scenarios));
for k = 1:numel(scenarios)
    idx = string(tbl.scenario) == scenarios(k) & string(tbl.policy) == policy;
    assert(nnz(idx) == 1, 'Expected one row for %s/%s.', scenarios(k), policy);
    values(k) = tbl.(column)(idx);
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
objects = findall(fig, '-property', 'FontName');
for k = 1:numel(objects), objects(k).FontName = 'Arial'; end
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
textValue = fileread(svgPath);
textValue = regexprep(textValue, 'font-family="[^"]+"', 'font-family="Arial"');
fid = fopen(svgPath, 'w', 'n', 'UTF-8');
assert(fid ~= -1, 'Could not rewrite SVG font declarations.');
cleanup = onCleanup(@() fclose(fid));
fwrite(fid, textValue, 'char');
clear cleanup;
end


function rgb = hexrgb(hex)
hex = char(erase(string(hex), '#'));
rgb = [hex2dec(hex(1:2)), hex2dec(hex(3:4)), hex2dec(hex(5:6))] ./ 255;
end


function map = divergingMap(n)
anchors = [hexrgb('#2874A6'); 1 1 1; hexrgb('#C0392B')];
x = [0, 0.5, 1]; xi = linspace(0, 1, n);
map = [interp1(x, anchors(:,1), xi)', interp1(x, anchors(:,2), xi)', ...
    interp1(x, anchors(:,3), xi)'];
end


function writeQa(outputDir, resultsDir)
path = fullfile(outputDir, 'MATLAB_REVIEWER_FIGURE_QA.txt');
fid = fopen(path, 'w');
assert(fid ~= -1, 'Could not write QA notes.');
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, 'Backend: MATLAB R%s\n', version('-release'));
fprintf(fid, 'Data source: %s\n', resultsDir);
fprintf(fid, 'Primary summary: 63 rows = 7 scenarios x 9 policies.\n');
fprintf(fid, 'Training curves: 12,000 rows = 4 methods x 5 seeds x 600 episodes.\n');
fprintf(fid, 'Curve bands: mean +/- SD across five seeds after a causal 25-episode mean.\n');
fprintf(fid, 'Sensitivity intervals: fixed-seed paired 95%% bootstrap, 10,000 resamples.\n');
fprintf(fid, 'Physical scatter: every tenth row shown for legibility; all 20,000 rows used for correlations and checks.\n');
fprintf(fid, 'Exports: vector PDF/SVG and 600-dpi TIFF; all figure fonts forced to Arial.\n');
clear cleanup;
end
