"""Generate reviewer-revision manuscript tables from locked CSV outputs.

This module formats tables only. All quantitative manuscript figures are
drawn by MATLAB in ``plot_reviewer_results_matlab.m``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil

import numpy as np
import pandas as pd

from .experiment import FULL_COUPLING, SCENARIOS
from .reviewer_experiments import paired_bootstrap


ROOT = Path(__file__).resolve().parent
POLICIES = (
    "immediate_argmin",
    "mpc_h4",
    "contextual_bandit",
    "threshold",
    "standard_dqn",
    "md_cfba_dqn",
    "md_cbad_dqn",
)
POLICY_LABELS = {
    "immediate_argmin": "Argmin",
    "mpc_h4": "MPC-4",
    "contextual_bandit": "Bandit",
    "threshold": "Threshold",
    "standard_dqn": "DQN",
    "md_cfba_dqn": "CFBA",
    "md_cbad_dqn": "CBAD",
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
PROFILE_LABELS = {
    "reference": "Reference",
    "compute_minus20": r"Compute demand $-20\%$",
    "compute_plus20": r"Compute demand $+20\%$",
    "data_minus20": r"Input data $-20\%$",
    "data_plus20": r"Input data $+20\%$",
    "energy_plus20": r"Energy use $+20\%$",
    "heat_plus20": r"Heat load $+20\%$",
    "link_minus20": r"Link capacity $-20\%$",
}


def _metric(summary: pd.DataFrame, scenario: str, policy: str, column: str) -> float:
    row = summary[(summary.scenario == scenario) & (summary.policy == policy)]
    if len(row) != 1:
        raise ValueError(f"expected one row for {scenario}/{policy}, found {len(row)}")
    return float(row.iloc[0][column])


def _write_main(summary: pd.DataFrame, output: Path) -> None:
    lines = [
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r"Regime & Argmin & MPC-4 & Bandit & Threshold & DQN & CFBA & CBAD \\",
        r"\midrule",
    ]
    for scenario, _, _ in SCENARIOS:
        values = {p: _metric(summary, scenario, p, "total_cost_mean") for p in POLICIES}
        best = min(values.values())
        cells = []
        for policy in POLICIES:
            mean = values[policy]
            sd = _metric(summary, scenario, policy, "total_cost_sd")
            cell = f"{mean:.2f} $\\pm$ {sd:.2f}"
            if np.isclose(mean, best):
                cell = rf"\textbf{{{cell}}}"
            cells.append(cell)
        lines.append(SCENARIO_LABELS[scenario] + " & " + " & ".join(cells) + r" \\")
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (output / "table_reviewer_main.tex").write_text("\n".join(lines), encoding="utf-8")


def _write_ablation(comparison: pd.DataFrame, output: Path) -> None:
    comparisons = (
        ("md_cfba_dqn - standard_dqn", "CFBA $-$ DQN"),
        ("md_cbad_dqn - md_cfba_dqn", "CBAD $-$ CFBA"),
        ("md_cbad_dqn - standard_dqn", "CBAD $-$ DQN"),
    )
    lines = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Regime & Comparison & Mean difference & 95\% interval & Supported \\",
        r"\midrule",
    ]
    for scenario, _, _ in FULL_COUPLING:
        for key, label in comparisons:
            row = comparison[
                (comparison.scenario == scenario) & (comparison.comparison == key)
            ].iloc[0]
            supported = "yes" if bool(row.supported) else "no"
            lines.append(
                f"{SCENARIO_LABELS[scenario]} & {label} & {row.mean_difference:.2f} & "
                f"[{row.ci95_low:.2f}, {row.ci95_high:.2f}] & {supported} \\\\"
            )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (output / "table_reviewer_ablation.tex").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def _write_sensitivity(sensitivity: pd.DataFrame, output: Path) -> None:
    selected = sensitivity[sensitivity.comparison == "md_cbad_dqn - standard_dqn"]
    lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Parameter profile & Mean difference & 95\% interval & Improvement \\",
        r"\midrule",
    ]
    for profile in PROFILE_LABELS:
        row = selected[selected.profile == profile].iloc[0]
        lines.append(
            f"{PROFILE_LABELS[profile]} & {row.mean_difference:.2f} & "
            f"[{row.ci95_low:.2f}, {row.ci95_high:.2f}] & "
            f"{row.relative_improvement_percent:.2f}\\% \\\\"
        )
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (output / "table_sensitivity.tex").write_text("\n".join(lines), encoding="utf-8")


def _write_parameters(output: Path) -> None:
    rows = (
        ("Raw task data", "8--64 Mbit", "Engineering envelope; sensitivity $\\pm20\\%$"),
        ("Arithmetic workload", "0.25--4.0 GFLOP", "Engineering envelope; correlated with data size"),
        ("Result / raw-data ratio", "1--5\\%", "Bounded compression assumption"),
        ("Feature / raw-data ratio", "8--30\\%", "Bounded collaborative-processing assumption"),
        ("Preprocessing fraction", "20--45\\%", "Deterministic function of workload quantile"),
        ("Onboard / ground rate", "4 / 80 GFLOP s$^{-1}$", "Fixed simulator hardware envelope"),
        ("Compute power", "4--20 W", "Bracketed by NASA SmallSat avionics examples"),
        ("Effective RF return rate", "2.2--220 Mbit s$^{-1}$", "NASA SmallSat ground-system examples"),
        ("Transmit power", "6 W", "Fixed simulator assumption"),
        ("Burst multiplier", "$1.45\\times$", "Contiguous prespecified stressor"),
    )
    lines = [
        r"\begin{tabular}{lll}",
        r"\toprule",
        r"Quantity & Implemented range & Basis \\",
        r"\midrule",
    ]
    lines.extend(" & ".join(row) + r" \\" for row in rows)
    lines.extend((r"\bottomrule", r"\end{tabular}"))
    (output / "table_parameter_provenance.tex").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def _write_macros(
    summary: pd.DataFrame,
    comparison: pd.DataFrame,
    sensitivity: pd.DataFrame,
    validity: dict,
    output: Path,
) -> None:
    full_names = [row[0] for row in FULL_COUPLING]
    cbad_dqn = comparison[
        (comparison.comparison == "md_cbad_dqn - standard_dqn")
        & comparison.scenario.isin(full_names)
    ]
    cbad_cfba = comparison[
        (comparison.comparison == "md_cbad_dqn - md_cfba_dqn")
        & comparison.scenario.isin(full_names)
    ]
    sens = sensitivity[sensitivity.comparison == "md_cbad_dqn - standard_dqn"]
    planning_per_step = _metric(
        summary, "nominal", "mpc_h4", "planning_time_ms_mean"
    ) / 64.0
    macros = {
        "PhysicalCBADMinPct": f"{cbad_dqn.relative_improvement_percent.min():.2f}\\%",
        "PhysicalCBADMaxPct": f"{cbad_dqn.relative_improvement_percent.max():.2f}\\%",
        "SensitivityMinPct": f"{sens.relative_improvement_percent.min():.2f}\\%",
        "SensitivityMaxPct": f"{sens.relative_improvement_percent.max():.2f}\\%",
        "PhysicalCorrDataWork": f"{validity['corr_raw_workload']:.3f}",
        "MPCNominalPlanningMs": f"{planning_per_step:.2f}",
        "MPCNominalCost": f"{_metric(summary, 'nominal', 'mpc_h4', 'total_cost_mean'):.2f}",
        "PhysicalNominalDQNCost": f"{_metric(summary, 'nominal', 'standard_dqn', 'total_cost_mean'):.2f}",
        "PhysicalNominalCBADCost": f"{_metric(summary, 'nominal', 'md_cbad_dqn', 'total_cost_mean'):.2f}",
        "CenteringSupportedCount": str(int(cbad_cfba.supported.sum())),
        "PhysicalAuditTasks": f"{int(validity['n_tasks']):,}",
    }
    lines = [f"\\newcommand{{\\{key}}}{{{value}\\xspace}}" for key, value in macros.items()]
    (output / "reviewer_macros.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results" / "reviewer_revision")
    parser.add_argument("--tables", type=Path, default=ROOT / "tables" / "reviewer_revision")
    parser.add_argument("--paper", type=Path, default=ROOT.parent / "paper")
    args = parser.parse_args()
    args.tables.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(args.results / "seven_regimes_raw.csv")
    summary = pd.read_csv(args.results / "seven_regimes_summary.csv")
    comparison = paired_bootstrap(
        raw,
        (
            ("md_cfba_dqn", "standard_dqn"),
            ("md_cbad_dqn", "md_cfba_dqn"),
            ("md_cbad_dqn", "standard_dqn"),
            ("md_cbad_dqn", "mpc_h4"),
            ("mpc_h4", "immediate_argmin"),
        ),
    )
    comparison.to_csv(args.results / "seven_regimes_paired_bootstrap_complete.csv", index=False)
    sensitivity = pd.read_csv(args.results / "sensitivity_paired_bootstrap.csv")
    validity = pd.read_json(args.results / "parameter_validity.json", typ="series").to_dict()

    _write_main(summary, args.tables)
    _write_ablation(comparison, args.tables)
    _write_sensitivity(sensitivity, args.tables)
    _write_parameters(args.tables)
    _write_macros(summary, comparison, sensitivity, validity, args.tables)

    generated = args.paper / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    for source in args.tables.glob("*.tex"):
        shutil.copy2(source, generated / source.name)


if __name__ == "__main__":
    main()
