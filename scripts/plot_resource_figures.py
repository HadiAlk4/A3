#!/usr/bin/env python3
"""Generate Section 5 resource histogram from data/pep_baseline.yaml."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "pep_baseline.yaml"
FIG = ROOT / "figures"

NAVY = "#0B2545"
CRIMSON = "#C0392B"
TEAL = "#2A9D8F"
GREY = "#E0E0E0"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 8.5,
        "axes.edgecolor": NAVY,
        "axes.labelcolor": NAVY,
        "xtick.color": NAVY,
        "ytick.color": NAVY,
        "text.color": NAVY,
        "pdf.fonttype": 42,
    }
)


def load():
    with YAML_PATH.open() as f:
        return yaml.safe_load(f)


def save(fig, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    out = FIG / name
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def plot_histogram(data) -> None:
    weeks = list(range(1, 17))
    mit = data["resource_weeks"]["demand_mitigated"]
    unmit = data["resource_weeks"]["demand_unmitigated"]
    proj = data["project"]
    organic = proj["organic_crew"]
    cap = proj["hse_pad_cap"]
    assert max(unmit) == proj["unmitigated_peak"]
    assert max(mit) == proj["mitigated_peak"]

    fig, ax = plt.subplots(figsize=(10.6, 5.15))
    x = weeks
    w = 0.38
    ax.bar(
        [i - w / 2 for i in x],
        unmit,
        width=w,
        facecolor="white",
        edgecolor=CRIMSON,
        linewidth=1.15,
        hatch="///",
        label="Unmitigated demand",
        zorder=2,
    )
    ax.bar(
        [i + w / 2 for i in x],
        mit,
        width=w,
        color=TEAL,
        edgecolor="none",
        label="Mitigated demand",
        zorder=3,
    )
    ax.axhline(organic, color=NAVY, linestyle="--", linewidth=1.25, zorder=4)
    ax.axhline(cap, color=CRIMSON, linestyle=":", linewidth=1.45, zorder=4)
    ax.text(16.35, organic + 0.18, "Organic crew  8", ha="right", va="bottom", fontsize=7.5, color=NAVY)
    ax.text(16.35, cap + 0.18, "HSE pad cap  12", ha="right", va="bottom", fontsize=7.5, color=CRIMSON)

    ax.annotate(
        "A-125 RF hours in weeks 3–6\n(mitigated above unmitigated).",
        xy=(4.2, 9.15),
        xytext=(0.7, 13.35),
        fontsize=7.4,
        color=NAVY,
        ha="left",
        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.9),
        bbox=dict(boxstyle="round,pad=0.32", facecolor="white", edgecolor=GREY),
        zorder=5,
    )
    ax.annotate(
        "+4 surge techs in 1.3.3\n($22,400 in base).",
        xy=(11.2, 12.05),
        xytext=(6.85, 15.15),
        fontsize=7.4,
        color=NAVY,
        ha="left",
        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.9),
        bbox=dict(boxstyle="round,pad=0.32", facecolor="white", edgecolor=GREY),
        zorder=5,
    )
    ax.text(11, 14.45, "Unmitigated peak 14", ha="center", fontsize=7.4, color=CRIMSON, fontweight="bold")

    ax.set_xlim(0.4, 16.6)
    ax.set_ylim(0, 16.2)
    ax.set_xticks(weeks)
    ax.set_xlabel("Campaign week (week 1 starts 10 August 2026)")
    ax.set_ylabel("People on pad")
    ax.grid(axis="y", color=GREY, linewidth=0.7, zorder=1)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    handles = [
        Patch(facecolor="white", edgecolor=CRIMSON, hatch="///", label="Unmitigated demand"),
        Patch(facecolor=TEAL, edgecolor="none", label="Mitigated demand"),
        Line2D([0], [0], color=NAVY, linestyle="--", linewidth=1.25, label="Organic crew (8)"),
        Line2D([0], [0], color=CRIMSON, linestyle=":", linewidth=1.45, label="HSE pad cap (12)"),
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.02),
        ncol=4,
        frameon=False,
        fontsize=7.4,
    )
    fig.tight_layout()
    save(fig, "resource_histogram.pdf")


def main() -> None:
    plot_histogram(load())


if __name__ == "__main__":
    main()
