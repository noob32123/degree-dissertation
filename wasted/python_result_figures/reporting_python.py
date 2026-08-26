"""Generate manuscript tables and vector figures from locked CSV results."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .experiment import FULL_COUPLING, MAIN_POLICIES, SCENARIOS


POLICY_LABELS = {
    "immediate_argmin": "Immediate argmin",
    "contextual_bandit": "Contextual bandit",
    "threshold": "Threshold",
    "standard_dqn": "Standard DQN",
    "md_cfba_dqn": "CFBA ablation",
    "md_cbad_dqn": "MD-CBAD-DQN",
}
SCENARIO_LABELS = {
    "static": "Static ($c=0$)",
    "reduced_coupling": "Reduced ($c=0.5$)",
    "nominal": "Nominal",
    "burst": "Burst",
    "link_limited": "Link-limited",
    "energy_limited": "Energy-limited",
    "thermal_stress": "Thermal-stress",
}
COLORS = {
    "immediate_argmin": "#7f8c8d",
    "contextual_bandit": "#9b59b6",
    "threshold": "#d68910",
    "standard_dqn": "#2874a6",
    "md_cfba_dqn": "#17a589",
    "md_cbad_dqn": "#c0392b",
}


def configure() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 9,
            "legend.fontsize": 7.5,
            "figure.dpi": 160,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_vector(fig: plt.Figure, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / f"{stem}.pdf")
    fig.savefig(output / f"{stem}.svg")
    plt.close(fig)


def seven_scenario_figure(summary: pd.DataFrame, output: Path) -> None:
    order = [item[0] for item in SCENARIOS]
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.0), height_ratios=(1.15, 1.0))
    x = np.arange(len(order))
    offsets = np.linspace(-0.30, 0.30, len(MAIN_POLICIES))
    for offset, policy in zip(offsets, MAIN_POLICIES):
        subset = summary[summary.policy == policy].set_index("scenario").loc[order]
        axes[0].errorbar(
            x + offset,
            subset.total_cost_mean,
            yerr=subset.total_cost_sd,
            fmt="o",
            ms=3.6,
            capsize=2,
            lw=1,
            color=COLORS[policy],
            label=POLICY_LABELS[policy],
        )
    axes[0].set_ylabel("Episode total cost")
    axes[0].set_xticks(x, [SCENARIO_LABELS[item] for item in order], rotation=18, ha="right")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(ncol=3, frameon=False, loc="upper left")
    axes[0].set_title("(a) Seven-regime paired evaluation")

    cbad = summary[summary.policy == "md_cbad_dqn"].set_index("scenario").loc[order]
    immediate = summary[summary.policy == "immediate_argmin"].set_index("scenario").loc[order]
    improvement = 100 * (immediate.total_cost_mean - cbad.total_cost_mean) / immediate.total_cost_mean
    bars = axes[1].bar(
        x,
        improvement,
        color=["#7f8c8d" if value < 0 else "#c0392b" for value in improvement],
        width=0.68,
    )
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_ylabel("CBAD improvement over\nimmediate argmin (%)")
    axes[1].set_xticks(x, [SCENARIO_LABELS[item] for item in order], rotation=18, ha="right")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].set_title("(b) Temporal-coupling boundary")
    for bar, value in zip(bars, improvement):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            value + (0.5 if value >= 0 else -0.7),
            f"{value:.1f}",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=7,
        )
    fig.tight_layout()
    save_vector(fig, output, "fig_seven_scenarios")


def ablation_figure(comparison: pd.DataFrame, output: Path) -> None:
    scenario_order = [item[0] for item in FULL_COUPLING]
    comparisons = (
        "md_cfba_dqn - standard_dqn",
        "md_cbad_dqn - md_cfba_dqn",
        "md_cbad_dqn - standard_dqn",
    )
    labels = ("CFBA - DQN", "CBAD - CFBA", "CBAD - DQN")
    colors = ("#17a589", "#d68910", "#c0392b")
    fig, ax = plt.subplots(figsize=(7.2, 3.7))
    y = np.arange(len(scenario_order))
    offsets = (-0.22, 0.0, 0.22)
    for offset, name, label, color in zip(offsets, comparisons, labels, colors):
        subset = comparison[comparison.comparison == name].set_index("scenario").loc[scenario_order]
        mean = subset.mean_difference.to_numpy()
        low = subset.ci95_low.to_numpy()
        high = subset.ci95_high.to_numpy()
        ax.errorbar(
            mean,
            y + offset,
            xerr=np.vstack((mean - low, high - mean)),
            fmt="o",
            capsize=2.5,
            color=color,
            label=label,
        )
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y, [SCENARIO_LABELS[item] for item in scenario_order])
    ax.invert_yaxis()
    ax.set_xlabel("Paired total-cost difference (negative favors first method)")
    ax.set_title("Counterfactual supervision and centering ablation")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(
        frameon=False,
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save_vector(fig, output, "fig_cbad_ablation")


def action_figure(summary: pd.DataFrame, output: Path) -> None:
    order = [item[0] for item in SCENARIOS]
    subset = summary[summary.policy == "md_cbad_dqn"].set_index("scenario").loc[order]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    x = np.arange(len(order))
    bottom = np.zeros(len(order))
    for column, label, color in (
        ("onboard_fraction_mean", "Onboard", "#2874a6"),
        ("ground_fraction_mean", "Ground", "#17a589"),
        ("hybrid_fraction_mean", "Collaborative", "#d68910"),
    ):
        values = subset[column].to_numpy()
        ax.bar(x, values, bottom=bottom, label=label, color=color, width=0.68)
        bottom += values
    ax.set_ylim(0, 1)
    ax.set_ylabel("Action fraction")
    ax.set_xticks(x, [SCENARIO_LABELS[item] for item in order], rotation=18, ha="right")
    ax.set_title("MD-CBAD-DQN deployment action distribution")
    ax.legend(frameon=False, ncol=3, loc="upper center")
    fig.tight_layout()
    save_vector(fig, output, "fig_action_distribution")


def _tex_escape(value: str) -> str:
    return value.replace("_", r"\_")


def write_tables(summary: pd.DataFrame, comparison: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    order = [item[0] for item in SCENARIOS]
    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Regime & Argmin & Bandit & Threshold & DQN & CFBA & CBAD \\",
        r"\midrule",
    ]
    for scenario in order:
        row = summary[summary.scenario == scenario].set_index("policy")
        values = []
        best = row.loc[list(MAIN_POLICIES), "total_cost_mean"].min()
        for policy in MAIN_POLICIES:
            value = (
                f"{row.loc[policy, 'total_cost_mean']:.2f} $\\pm$ "
                f"{row.loc[policy, 'total_cost_sd']:.2f}"
            )
            if np.isclose(row.loc[policy, "total_cost_mean"], best):
                value = rf"\textbf{{{value}}}"
            values.append(value)
        lines.append(
            _tex_escape(SCENARIO_LABELS[scenario].replace("$", ""))
            + " & " + " & ".join(values) + r" \\"
        )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (output / "table_main_results.tex").write_text("\n".join(lines), encoding="utf-8")

    fixed_lines = [
        r"\begin{tabular}{lrr}",
        r"\toprule",
        r"Regime & Fixed onboard & Fixed ground \\",
        r"\midrule",
    ]
    for scenario in order:
        row = summary[summary.scenario == scenario].set_index("policy")
        fixed_lines.append(
            f"{_tex_escape(SCENARIO_LABELS[scenario])} & "
            f"{row.loc['fixed_onboard', 'total_cost_mean']:.2f} $\\pm$ "
            f"{row.loc['fixed_onboard', 'total_cost_sd']:.2f} & "
            f"{row.loc['fixed_ground', 'total_cost_mean']:.2f} $\\pm$ "
            f"{row.loc['fixed_ground', 'total_cost_sd']:.2f} \\\\"
        )
    fixed_lines.extend((r"\bottomrule", r"\end{tabular}"))
    (output / "table_fixed_policies.tex").write_text(
        "\n".join(fixed_lines), encoding="utf-8"
    )

    selected = comparison[
        comparison.comparison.isin(
            (
                "md_cfba_dqn - standard_dqn",
                "md_cbad_dqn - md_cfba_dqn",
                "md_cbad_dqn - standard_dqn",
            )
        ) & comparison.scenario.isin([item[0] for item in FULL_COUPLING])
    ]
    lines = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Regime & Comparison & Mean diff. & 95\% CI & Rel. improve. \\",
        r"\midrule",
    ]
    comparison_labels = {
        "md_cfba_dqn - standard_dqn": "CFBA - DQN",
        "md_cbad_dqn - md_cfba_dqn": "CBAD - CFBA",
        "md_cbad_dqn - standard_dqn": "CBAD - DQN",
    }
    for scenario in [item[0] for item in FULL_COUPLING]:
        for _, row in selected[selected.scenario == scenario].iterrows():
            marker = r"\textbf{yes}" if row.significant else "no"
            lines.append(
                f"{_tex_escape(SCENARIO_LABELS[scenario])} & "
                f"{comparison_labels[row.comparison]} & "
                f"{row.mean_difference:.2f} & "
                f"[{row.ci95_low:.2f}, {row.ci95_high:.2f}] & "
                f"{row.relative_improvement_percent:.2f}\\% ({marker}) \\\\"
            )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (output / "table_ablation.tex").write_text("\n".join(lines), encoding="utf-8")

    def metric(scenario: str, policy: str, column: str) -> float:
        row = summary[(summary.scenario == scenario) & (summary.policy == policy)]
        return float(row.iloc[0][column])

    cbad_dqn = comparison[
        (comparison.comparison == "md_cbad_dqn - standard_dqn")
        & comparison.scenario.isin([item[0] for item in FULL_COUPLING])
    ]
    cbad_cfba_link = comparison[
        (comparison.comparison == "md_cbad_dqn - md_cfba_dqn")
        & (comparison.scenario == "link_limited")
    ].iloc[0]
    macros = {
        "CBADvsDQNMinPct": f"{cbad_dqn.relative_improvement_percent.min():.2f}\\%",
        "CBADvsDQNMaxPct": f"{cbad_dqn.relative_improvement_percent.max():.2f}\\%",
        "CBADvsCFBALinkDiff": f"{cbad_cfba_link.mean_difference:.2f}",
        "CBADvsCFBALinkCI": (
            f"[{cbad_cfba_link.ci95_low:.2f}, {cbad_cfba_link.ci95_high:.2f}]"
        ),
        "StaticArgminCost": f"{metric('static', 'immediate_argmin', 'total_cost_mean'):.2f}",
        "StaticCBADCost": f"{metric('static', 'md_cbad_dqn', 'total_cost_mean'):.2f}",
        "ReducedArgminCost": f"{metric('reduced_coupling', 'immediate_argmin', 'total_cost_mean'):.2f}",
        "ReducedCBADCost": f"{metric('reduced_coupling', 'md_cbad_dqn', 'total_cost_mean'):.2f}",
        "NominalDQNCost": f"{metric('nominal', 'standard_dqn', 'total_cost_mean'):.2f}",
        "NominalCFBACost": f"{metric('nominal', 'md_cfba_dqn', 'total_cost_mean'):.2f}",
        "NominalCBADCost": f"{metric('nominal', 'md_cbad_dqn', 'total_cost_mean'):.2f}",
    }
    macro_lines = [
        f"\\newcommand{{\\{name}}}{{{value}\\xspace}}" for name, value in macros.items()
    ]
    (output / "results_macros.tex").write_text(
        "\n".join(macro_lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path(__file__).parent / "results")
    parser.add_argument("--figures", type=Path, default=Path(__file__).parent / "figures")
    parser.add_argument("--tables", type=Path, default=Path(__file__).parent / "tables")
    parser.add_argument(
        "--paper",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "paper",
        help="manuscript directory that receives synchronized generated assets",
    )
    args = parser.parse_args()
    configure()
    summary = pd.read_csv(args.results / "seven_scenarios_summary.csv")
    comparison = pd.read_csv(args.results / "seven_scenarios_paired_bootstrap.csv")
    seven_scenario_figure(summary, args.figures)
    ablation_figure(comparison, args.figures)
    action_figure(summary, args.figures)
    write_tables(summary, comparison, args.tables)
    paper_figures = args.paper / "figures"
    paper_generated = args.paper / "generated"
    paper_figures.mkdir(parents=True, exist_ok=True)
    paper_generated.mkdir(parents=True, exist_ok=True)
    for source in args.figures.glob("fig_*.pdf"):
        shutil.copy2(source, paper_figures / source.name)
    for source in args.tables.glob("*.tex"):
        shutil.copy2(source, paper_generated / source.name)


if __name__ == "__main__":
    main()
