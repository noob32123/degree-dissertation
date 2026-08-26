"""Generate manuscript tables from locked CSV results.

Quantitative manuscript figures are generated exclusively by
``plot_results_matlab.m``.  Keeping table generation here avoids duplicating the
LaTeX formatting logic while preventing a Python reporting run from
overwriting the MATLAB figure exports.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil

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
    parser.add_argument("--tables", type=Path, default=Path(__file__).parent / "tables")
    parser.add_argument(
        "--paper",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "paper",
        help="manuscript directory that receives synchronized generated assets",
    )
    args = parser.parse_args()
    summary = pd.read_csv(args.results / "seven_scenarios_summary.csv")
    comparison = pd.read_csv(args.results / "seven_scenarios_paired_bootstrap.csv")
    write_tables(summary, comparison, args.tables)
    paper_generated = args.paper / "generated"
    paper_generated.mkdir(parents=True, exist_ok=True)
    for source in args.tables.glob("*.tex"):
        shutil.copy2(source, paper_generated / source.name)


if __name__ == "__main__":
    main()
