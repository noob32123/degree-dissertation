"""Create publication-ready figures for the CRGR confirmation study."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCENARIO_ORDER = [
    "nominal",
    "burst",
    "link_limited",
    "energy_limited",
    "thermal_stress",
]
LABELS = ["Nominal", "Burst", "Link-limited", "Energy-limited", "Thermal-stress"]
COLORS = {
    "standard_dqn": "#4C78A8",
    "ungated_ranking_dqn": "#F58518",
    "md_crgr_dqn": "#54A24B",
}


def save_all(fig: plt.Figure, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(output / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(output / f"{stem}.tiff", dpi=600, bbox_inches="tight")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary = pd.read_csv(args.results / "confirmatory_summary.csv")
    comparison = pd.read_csv(args.results / "confirmatory_comparison.csv")
    curves = pd.read_csv(args.results / "confirmatory_training_curves.csv")
    selected = summary[
        (summary.scenario.isin(SCENARIO_ORDER)) & (summary.coupling == 1.0)
    ].copy()
    selected["scenario"] = pd.Categorical(
        selected.scenario, categories=SCENARIO_ORDER, ordered=True
    )
    selected = selected.sort_values("scenario")

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.4))
    x = np.arange(len(SCENARIO_ORDER))
    width = 0.25
    variants = ["standard_dqn", "ungated_ranking_dqn", "md_crgr_dqn"]
    names = ["Standard MD-DQN", "Ungated ranking", "MD-CRGR-DQN"]
    for index, (variant, name) in enumerate(zip(variants, names)):
        data = selected[selected.variant == variant].set_index("scenario").reindex(SCENARIO_ORDER)
        axes[0].bar(
            x + (index - 1) * width,
            data.total_cost_mean,
            width,
            yerr=data.total_cost_sd,
            capsize=3,
            color=COLORS[variant],
            label=name,
        )
    axes[0].set_xticks(x, LABELS, rotation=20, ha="right")
    axes[0].set_ylabel("Mean total cost (lower is better)")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].set_title("(a) Seed-level mean ± SD")

    primary = comparison[
        comparison.comparison == "md_crgr_dqn - standard_dqn"
    ].set_index("scenario").reindex(SCENARIO_ORDER)
    means = primary.mean_difference.to_numpy()
    lower = means - primary.ci95_low.to_numpy()
    upper = primary.ci95_high.to_numpy() - means
    colors = ["#54A24B" if high < 0 else "#E45756" for high in primary.ci95_high]
    axes[1].axhline(0, color="black", linewidth=0.9)
    axes[1].errorbar(
        x,
        means,
        yerr=np.vstack([lower, upper]),
        fmt="none",
        ecolor="black",
        capsize=4,
        linewidth=1.2,
    )
    axes[1].scatter(x, means, c=colors, s=42, zorder=3)
    axes[1].set_xticks(x, LABELS, rotation=20, ha="right")
    axes[1].set_ylabel("Paired cost difference (CRGR − standard)")
    axes[1].set_title("(b) Mean difference and paired 95% CI")
    fig.tight_layout()
    save_all(fig, args.output, "fig_crgr_results")
    plt.close(fig)

    curve_summary = curves.groupby(
        ["variant", "episode"], as_index=False
    ).rolling_cost.agg(["mean", "std"]).reset_index()
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    for variant, name in zip(variants, names):
        data = curve_summary[curve_summary.variant == variant]
        ax.plot(data.episode, data["mean"], color=COLORS[variant], label=name)
        ax.fill_between(
            data.episode,
            data["mean"] - data["std"],
            data["mean"] + data["std"],
            color=COLORS[variant],
            alpha=0.16,
            linewidth=0,
        )
    ax.set_xlabel("Training episode")
    ax.set_ylabel("20-episode rolling total cost")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    save_all(fig, args.output, "fig_crgr_training")
    plt.close(fig)


if __name__ == "__main__":
    main()
