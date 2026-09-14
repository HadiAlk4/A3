#!/usr/bin/env python3
"""Generate Section 6 risk matrix from data/pep_baseline.yaml."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle

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

# Forced offsets so (2,5) R-02/R-09/R-12 and the (1,2) residual cluster stay readable.
JITTER = {
    "R-01": {"in": (-0.12, 0.10), "res": (-0.10, 0.10)},
    "R-04": {"in": (0.12, -0.10), "res": (0.10, 0.16)},
    "R-02": {"in": (-0.16, 0.14), "res": (-0.10, 0.08)},
    "R-09": {"in": (0.16, -0.04), "res": (0.10, -0.08)},
    "R-03": {"in": (-0.14, 0.12), "res": (-0.16, 0.12)},
    "R-05": {"in": (0.00, -0.02), "res": (-0.10, 0.10)},
    "R-07": {"in": (0.14, -0.12), "res": (0.16, 0.04)},
    "R-17": {"in": (0.00, 0.14), "res": (0.12, 0.12)},
    "R-08": {"in": (0.00, 0.00), "res": (-0.16, -0.08)},
    "R-11": {"in": (0.12, -0.10), "res": (0.16, -0.12)},
    "R-10": {"in": (-0.12, 0.10), "res": (0.00, 0.00)},
    "R-15": {"in": (-0.10, 0.00), "res": (-0.04, -0.16)},
    "R-16": {"in": (0.10, 0.00), "res": (0.04, 0.00)},
    "R-06": {"in": (0.00, 0.08), "res": (0.10, -0.10)},
    "R-13": {"in": (0.00, 0.00), "res": (0.00, 0.00)},
    "R-12": {"in": (0.00, -0.20), "res": (0.12, 0.10)},
}


def load():
    with YAML_PATH.open() as f:
        return yaml.safe_load(f)


def save(fig, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    out = FIG / name
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def band_colour(p: int, i: int) -> str:
    s = p * i
    if s >= 15:
        return "#F5B7B1"
    if s >= 10:
        return "#F5C6AA"
    if s >= 5:
        return "#F9E79F"
    return "#D5F5E3"


def xy(rid: str, p: int, i: int, which: str) -> tuple[float, float]:
    dx, dy = JITTER.get(rid, {}).get(which, (0.0, 0.0))
    return i + dx, p + dy


def plot_matrix(data) -> None:
    risks = data["risks"]
    fig, ax = plt.subplots(figsize=(7.6, 7.2))

    for p in range(1, 6):
        for i in range(1, 6):
            ax.add_patch(
                Rectangle(
                    (i - 0.5, p - 0.5),
                    1,
                    1,
                    facecolor=band_colour(p, i),
                    edgecolor="white",
                    linewidth=1.4,
                    zorder=0,
                )
            )

    for r in risks:
        rid = r["id"]
        x0, y0 = xy(rid, r["p"], r["i"], "in")
        x1, y1 = xy(rid, r["p_res"], r["i_res"], "res")
        same = r["p"] == r["p_res"] and r["i"] == r["i_res"]
        if not same:
            ax.add_patch(
                FancyArrowPatch(
                    (x0, y0),
                    (x1, y1),
                    arrowstyle="-|>",
                    mutation_scale=8,
                    linewidth=0.7,
                    color=NAVY,
                    alpha=0.55,
                    zorder=2,
                    shrinkA=4,
                    shrinkB=4,
                )
            )
        ax.scatter(x0, y0, s=36, facecolor=CRIMSON, edgecolor=NAVY, linewidth=0.4, zorder=3)
        ax.scatter(x1, y1, s=28, facecolor=TEAL, edgecolor=NAVY, linewidth=0.4, zorder=4)
        ax.text(x0, y0 + 0.16, rid, ha="center", va="bottom", fontsize=5.6, color=NAVY, zorder=5)

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.55)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Impact $I$ (1–5; max of schedule and cost bands)")
    ax.set_ylabel("Probability $P$ (1–5)")
    ax.set_aspect("equal")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=CRIMSON, markeredgecolor=NAVY, markersize=7, label="Inherent"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=TEAL, markeredgecolor=NAVY, markersize=6.5, label="Residual"),
        Line2D([0], [0], color=NAVY, linewidth=0.8, label="Treatment"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=True, fontsize=7.2, edgecolor=GREY)
    fig.tight_layout()
    save(fig, "risk_matrix.pdf")


def main() -> None:
    plot_matrix(load())


if __name__ == "__main__":
    main()
