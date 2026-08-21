"""Create publication figures from the final experiment CSV files.

Figure contract
---------------
Core conclusion: model-driven RL reduces cumulative cost by avoiding delayed
resource violations, whereas its advantage should disappear without temporal
coupling.
Archetype: quantitative grid.  Panel a is the hero comparison; b identifies
the constraint mechanism; c is the zero-coupling control; d audits RSF.
Output: 180 mm wide, editable SVG/PDF plus 600-dpi TIFF.
Statistics: mean and SD across independent model seeds after averaging the 20
paired held-out traces within each seed.
Reviewer risk: do not treat task traces as independent replicates and do not
hide an unfavorable ablation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'
mpl.rcParams.update({
    "svg.fonttype": "none", "pdf.fonttype": 42, "font.size": 7.5, "axes.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
})

COLORS = {
    "immediate_argmin": "#767676", "contextual_bandit": "#7884B4",
    "standard_dqn": "#3775BA", "dqn_r": "#AADCA9",
    "dqn_rs": "#8BCF8B", "md_dqn_rsf": "#B64342",
}
LABELS = {
    "immediate_argmin": "Immediate argmin", "contextual_bandit": "Contextual bandit",
    "standard_dqn": "Standard DQN", "dqn_r": "DQN+R",
    "dqn_rs": "DQN+R+S", "md_dqn_rsf": "MD-DQN-RSF",
}


def seed_level(raw: pd.DataFrame) -> pd.DataFrame:
    metrics = ["total_cost", "immediate_cost", "penalty", "thermal_violation",
               "energy_violation", "queue_violation", "contact_violation"]
    return raw.groupby(
        ["scenario", "coupling", "policy", "model_seed"], as_index=False
    )[metrics].mean()


def mean_sd(frame: pd.DataFrame, policies: list[str], metric: str):
    grouped = frame[frame.policy.isin(policies)].groupby("policy")[metric]
    return (
        np.array([grouped.mean()[p] for p in policies]),
        np.array([grouped.std(ddof=1)[p] for p in policies]),
    )


def panel_label(ax, label: str):
    ax.text(-0.14, 1.04, label, transform=ax.transAxes, fontsize=9,
            fontweight="bold", ha="left", va="bottom")


def save_all(fig, stem: Path):
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight")


def make_main_figure(raw: pd.DataFrame, output: Path):
    seeds = seed_level(raw)
    nominal = seeds[(seeds.scenario == "nominal") & (seeds.coupling == 1.0)]
    fig, axes = plt.subplots(2, 2, figsize=(7.09, 4.85), constrained_layout=True)

    # a | Primary cumulative-cost comparison.
    ax = axes[0, 0]
    policies = ["immediate_argmin", "contextual_bandit", "standard_dqn", "md_dqn_rsf"]
    means, sds = mean_sd(nominal, policies, "total_cost")
    x = np.arange(len(policies))
    ax.bar(x, means, yerr=sds, capsize=3, color=[COLORS[p] for p in policies],
           edgecolor="#333333", linewidth=0.6)
    ax.set_xticks(x, [LABELS[p] for p in policies], rotation=22, ha="right")
    ax.set_ylabel("Cumulative cost per episode")
    panel_label(ax, "a")

    # b | Mechanistic evidence: post-decision violations.
    ax = axes[0, 1]
    violations = ["thermal_violation", "energy_violation", "queue_violation", "contact_violation"]
    violation_labels = ["Thermal", "Energy", "Queue", "Contact"]
    bottom = np.zeros(len(policies))
    stack_colors = ["#E9A6A1", "#FFD08A", "#42949E", "#9A4D8E"]
    for metric, label, color in zip(violations, violation_labels, stack_colors):
        vals, _ = mean_sd(nominal, policies, metric)
        ax.bar(x, vals, bottom=bottom, label=label, color=color,
               edgecolor="white", linewidth=0.4)
        bottom += vals
    ax.set_xticks(x, [LABELS[p] for p in policies], rotation=22, ha="right")
    ax.set_ylabel("Constraint violations per episode")
    ax.legend(ncol=2, fontsize=6.5, handlelength=1.2, columnspacing=0.8)
    panel_label(ax, "b")

    # c | Falsification/control: strength of temporal coupling.
    ax = axes[1, 0]
    coupling_policies = ["immediate_argmin", "standard_dqn", "md_dqn_rsf"]
    for policy in coupling_policies:
        sub = seeds[(seeds.scenario == "nominal") & (seeds.policy == policy)]
        stats = sub.groupby("coupling").total_cost.agg(["mean", "std"]).reset_index()
        ax.errorbar(stats.coupling, stats["mean"], yerr=stats["std"], marker="o",
                    ms=4, lw=1.5, capsize=2.5, color=COLORS[policy], label=LABELS[policy])
    ax.set_xlabel("Evaluation coupling (no retraining)")
    ax.set_ylabel("Cumulative cost per episode")
    ax.set_xticks([0, 0.5, 1.0])
    ax.legend(fontsize=6.5)
    panel_label(ax, "c")

    # d | RSF ablation, retained even if an intervention is neutral/adverse.
    ax = axes[1, 1]
    ablations = ["standard_dqn", "dqn_r", "dqn_rs", "md_dqn_rsf"]
    means, sds = mean_sd(nominal, ablations, "total_cost")
    xa = np.arange(len(ablations))
    ax.bar(xa, means, yerr=sds, capsize=3, color=[COLORS[p] for p in ablations],
           edgecolor="#333333", linewidth=0.6)
    ax.set_xticks(xa, [LABELS[p] for p in ablations], rotation=20, ha="right")
    ax.set_ylabel("Cumulative cost per episode")
    panel_label(ax, "d")

    save_all(fig, output / "fig_results")
    plt.close(fig)


def make_training_figure(curves: pd.DataFrame, output: Path):
    fig, ax = plt.subplots(figsize=(3.54, 2.45), constrained_layout=True)
    for policy in ["standard_dqn", "md_dqn_rsf"]:
        sub = curves[curves.policy == policy]
        stats = sub.groupby("episode").rolling_cost.agg(["mean", "std"]).reset_index()
        ax.plot(stats.episode, stats["mean"], lw=1.5, color=COLORS[policy], label=LABELS[policy])
        ax.fill_between(stats.episode, stats["mean"] - stats["std"],
                        stats["mean"] + stats["std"], color=COLORS[policy], alpha=0.16,
                        linewidth=0)
    ax.axvline(270, color="#767676", lw=0.8, ls="--")
    ax.axvline(432, color="#767676", lw=0.8, ls=":")
    ax.text(270, 0.98, "reset", transform=ax.get_xaxis_transform(), rotation=90,
            ha="right", va="top", fontsize=6.5, color="#606060")
    ax.text(432, 0.98, "flush", transform=ax.get_xaxis_transform(), rotation=90,
            ha="right", va="top", fontsize=6.5, color="#606060")
    ax.set_xlabel("Training episode")
    ax.set_ylabel("20-episode rolling cost")
    ax.legend()
    save_all(fig, output / "fig_training")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(args.input / "evaluation_raw.csv")
    curves = pd.read_csv(args.input / "training_curves.csv")
    make_main_figure(raw, args.output)
    make_training_figure(curves, args.output)


if __name__ == "__main__":
    main()
