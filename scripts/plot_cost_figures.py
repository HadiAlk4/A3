#!/usr/bin/env python3
"""Generate Section 4 figures from data/pep_baseline.yaml."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "pep_baseline.yaml"
FIG = ROOT / "figures"

NAVY = "#0B2545"
CRIMSON = "#C0392B"
TEAL = "#2A9D8F"
AMBER = "#E76F51"
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


def money(v: float) -> str:
    return f"${v:,.0f}"


def plot_scurve(data) -> None:
    rows = data["monthly_pv"]
    proj = data["project"]
    base = proj["base_estimate"]
    bac = proj["bac"]
    contingency = proj["contingency"]

    labels = ["Aug 2026", "Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026"]
    period = [r["period"] for r in rows]
    cum = [r["cumulative"] for r in rows]
    assert cum[-1] == base, f"S-curve must end at base {base}, got {cum[-1]}"

    fig, ax = plt.subplots(figsize=(10.4, 5.55))
    x = list(range(len(rows)))

    ax.axvspan(-0.5, 1.5, color=NAVY, alpha=0.05, zorder=0)
    ax.axvspan(1.5, 2.5, color=CRIMSON, alpha=0.08, zorder=0)

    bar_colours = [NAVY, NAVY, CRIMSON, NAVY, NAVY]
    ax.bar(
        x,
        period,
        width=0.62,
        color=bar_colours,
        edgecolor="none",
        label="Period PV",
        zorder=2,
        alpha=0.92,
    )
    ax.plot(
        x,
        cum,
        color=TEAL,
        marker="o",
        markersize=7,
        linewidth=2.3,
        label="Cumulative PV",
        zorder=4,
    )
    offsets = {0: (0, 9), 1: (0, 9), 2: (0, 9), 3: (-22, 12), 4: (12, 10)}
    for i, v in enumerate(cum):
        dx, dy = offsets[i]
        ax.annotate(
            money(v),
            (i, v),
            textcoords="offset points",
            xytext=(dx, dy),
            ha="center",
            fontsize=7.2,
            color=TEAL,
            fontweight="bold",
        )

    ax.axhline(base, color=NAVY, linestyle="--", linewidth=1.25, zorder=3)
    ax.axhline(bac, color=CRIMSON, linestyle=":", linewidth=1.45, zorder=3)
    ax.text(
        0.02,
        bac + 22000,
        f"BAC  {money(bac)}",
        ha="left",
        va="bottom",
        fontsize=7.4,
        color=CRIMSON,
    )
    ax.text(
        0.02,
        base - 38000,
        f"Work PMB  {money(base)}",
        ha="left",
        va="top",
        fontsize=7.4,
        color=NAVY,
    )

    ax.annotate(
        f"Contingency {money(contingency)} is undistributed\n— not December cash.",
        xy=(4, period[-1] + 40000),
        xytext=(2.65, 1080000),
        fontsize=8,
        color=NAVY,
        ha="left",
        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.9),
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=GREY),
        zorder=5,
    )
    ax.text(
        2.0,
        880000,
        "October peak\n(stack, WDR, static fire)",
        ha="center",
        va="bottom",
        fontsize=7.4,
        color=CRIMSON,
        fontweight="bold",
    )

    ax.set_xticks(x, labels)
    ax.set_xlim(-0.55, 4.55)
    ax.set_ylim(0, 1800000)
    ax.set_ylabel("AUD")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"${v/1_000_000:.1f}M"))
    ax.grid(axis="y", color=GREY, linewidth=0.7, zorder=1)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    handles = [
        Patch(facecolor=NAVY, edgecolor="none", label="Period PV"),
        Patch(facecolor=CRIMSON, edgecolor="none", label="October period PV (peak)"),
        Line2D([0], [0], color=TEAL, marker="o", linewidth=2.3, label="Cumulative PV"),
        Line2D([0], [0], color=NAVY, linestyle="--", linewidth=1.25, label=f"Work PMB {money(base)}"),
        Line2D([0], [0], color=CRIMSON, linestyle=":", linewidth=1.45, label=f"BAC {money(bac)}"),
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.02),
        ncol=3,
        frameon=False,
        fontsize=7.4,
    )
    fig.tight_layout()
    save(fig, "cash_flow_scurve.pdf")


def main() -> None:
    data = load()
    plot_scurve(data)


if __name__ == "__main__":
    main()
