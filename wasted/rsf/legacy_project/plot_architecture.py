"""Draw the hybrid model-driven scheduling architecture as editable vectors."""

from pathlib import Path
import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'
mpl.rcParams.update({"svg.fonttype": "none", "pdf.fonttype": 42, "font.size": 8})


def box(ax, xy, width, height, text, face, edge="#333333"):
    patch = FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.015,rounding_size=0.02",
                           facecolor=face, edgecolor=edge, linewidth=0.9)
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text,
            ha="center", va="center", linespacing=1.25)
    return patch


def arrow(ax, start, end, label=None, bend=0.0):
    p = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=10,
                        linewidth=1.0, color="#4D4D4D",
                        connectionstyle=f"arc3,rad={bend}")
    ax.add_patch(p)
    if label:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.025,
                label, ha="center", va="bottom", fontsize=7, color="#4D4D4D")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.09, 2.55), constrained_layout=True)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    box(ax, (0.02, 0.60), 0.16, 0.23, "Task descriptor\n$x_t$ (15 variables)", "#E0E0F0")
    box(ax, (0.02, 0.18), 0.16, 0.23, "Resource state $z_t$\nheat, energy, queue,\nutilization, link, contact", "#E0F0F0")
    box(ax, (0.27, 0.58), 0.19, 0.26, "Analytical cost model\n$c_{\\mathrm{model}}(x_t,z_t,a)$\ninterpretable immediate cost", "#DDF3DE")
    box(ax, (0.27, 0.16), 0.19, 0.26, "Value network\n$Q_\\theta([x_t,z_t],a)$\nlong-term consequences", "#E4CCD8")
    box(ax, (0.55, 0.37), 0.15, 0.25, "MD-DQN-RSF\naction selection\n$a_t$", "#F0C0CC", edge="#B64342")
    box(ax, (0.78, 0.37), 0.19, 0.25, "Satellite-ground system\nonboard | ground | hybrid", "#CFCECE")

    arrow(ax, (0.18, 0.715), (0.27, 0.715))
    arrow(ax, (0.18, 0.30), (0.27, 0.29))
    arrow(ax, (0.18, 0.64), (0.27, 0.35), bend=0.14)
    arrow(ax, (0.18, 0.34), (0.27, 0.62), bend=-0.14)
    arrow(ax, (0.46, 0.70), (0.55, 0.54))
    arrow(ax, (0.46, 0.29), (0.55, 0.45))
    arrow(ax, (0.70, 0.495), (0.78, 0.495))
    ax.plot([0.875, 0.875, 0.10], [0.37, 0.07, 0.07], color="#4D4D4D", lw=1.0)
    arrow(ax, (0.10, 0.07), (0.10, 0.18))
    ax.text(0.50, 0.085, "$z_{t+1}$ and next task", ha="center", va="bottom",
            fontsize=7, color="#4D4D4D")

    stem = args.output / "fig_architecture"
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
