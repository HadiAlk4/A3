#!/usr/bin/env python3
"""Generate Section 3 figures from data/pep_baseline.yaml."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import yaml
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "pep_baseline.yaml"
FIG = ROOT / "figures"

NAVY = "#0B2545"
CRIMSON = "#C0392B"
TEAL = "#2A9D8F"
AMBER = "#E76F51"
GREY = "#E0E0E0"
LIGHT = "#F4F4F4"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 8,
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


def parse(d: str) -> datetime:
    return datetime.fromisoformat(str(d))


def save(fig, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    out = FIG / name
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def plot_gantt(data) -> None:
    acts = data["activities"]
    miles = data["milestones"]
    fig, ax = plt.subplots(figsize=(11.2, 8.4))
    n = len(acts)
    for i, a in enumerate(reversed(acts)):
        y = i
        es, ef, lf = parse(a["es"]), parse(a["ef"]), parse(a["lf"])
        # matplotlib barh width is in days; inclusive duration = ef-es+1
        width = (ef - es).days + 1
        colour = CRIMSON if a["critical"] else NAVY
        ax.barh(
            y,
            width,
            left=es,
            height=0.55,
            color=colour,
            edgecolor="none",
            zorder=3,
        )
        if not a["critical"] and lf > ef:
            ax.plot(
                [ef, lf],
                [y, y],
                color=TEAL,
                lw=2.0,
                solid_capstyle="butt",
                zorder=2,
            )

    ax.set_yticks(range(n))
    ax.set_yticklabels(
        [f"{a['id']}  {a['name'][:42]}" for a in reversed(acts)],
        fontsize=7,
    )
    ax.set_xlim(parse("2026-08-08"), parse("2026-12-05"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlabel("Date (2026)")
    ax.grid(axis="x", color=GREY, lw=0.6, zorder=0)
    ax.set_axisbelow(True)

    markers = [
        ("M-2", miles["M2"]["date"], NAVY, ":"),
        ("M-4", miles["M4"]["date"], CRIMSON, "--"),
        ("M-5", miles["M5"]["date"], CRIMSON, "--"),
        ("M-6", miles["M6"]["date"], CRIMSON, "--"),
        ("M-7", miles["M7"]["date"], CRIMSON, "--"),
        ("M-8", miles["M8"]["date"], CRIMSON, "--"),
        ("M-9", miles["M9"]["date"], CRIMSON, "--"),
    ]
    for name, raw, col, ls in markers:
        x = parse(raw)
        ax.axvline(x, color=col, ls=ls, lw=0.9, zorder=1)
        ax.text(
            x,
            -1.15,
            name,
            rotation=90,
            va="top",
            ha="center",
            fontsize=6.5,
            color=col,
        )

    legend = [
        Rectangle((0, 0), 1, 1, color=CRIMSON, label="Launch-critical ($TF=0$)"),
        Rectangle((0, 0), 1, 1, color=NAVY, label="Non-critical / Gate 1"),
        Line2D([0], [0], color=TEAL, lw=2, label="Total float to $LF$"),
    ]
    ax.legend(
        handles=legend,
        loc="upper left",
        bbox_to_anchor=(0.0, -0.12),
        ncol=3,
        frameon=False,
        fontsize=7,
    )
    ax.set_ylim(-1.55, n - 0.35)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    save(fig, "gantt_chart.pdf")


def plot_compression(data) -> None:
    opts = data["compression"]["options"]
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2))

    labels = [o["id"] for o in opts]
    costs = [o["cost"] / 1000 for o in opts]
    risk_map = {"High": 3, "Medium": 2, "Low": 1}
    risks = [risk_map[o["risk"]] for o in opts]
    colours = [NAVY, CRIMSON, AMBER]

    ax = axes[0]
    bars = ax.bar(labels, costs, color=colours, width=0.62, zorder=3)
    ax.set_ylabel("Added cost (thousand AUD)")
    ax.set_xlabel("Option (all save 5 days)")
    ax.grid(axis="y", color=GREY, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for bar, o in zip(bars, opts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.8,
            f"${o['cost']:,.0f}\n{o['verdict']}",
            ha="center",
            va="bottom",
            fontsize=7,
        )
    ax.set_ylim(0, 52)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("Direct added cost", loc="left", fontsize=9, color=NAVY)

    ax = axes[1]
    ax.bar(labels, risks, color=colours, width=0.62, zorder=3)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["Low", "Medium", "High"])
    ax.set_ylim(0, 3.6)
    ax.set_xlabel("Option (all save 5 days)")
    ax.set_ylabel("Residual schedule/quality risk")
    ax.grid(axis="y", color=GREY, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title("Secondary risk after treatment", loc="left", fontsize=9, color=NAVY)
    for x, o in enumerate(opts):
        slope = o["slope_per_day"]
        ax.text(x, risks[x] + 0.12, f"${slope:,}/d", ha="center", fontsize=7)

    fig.tight_layout()
    save(fig, "compression_tradeoff.pdf")


def plot_network(data) -> None:
    w, h = 1.55, 1.05
    pos = {
        "A-111": (0.0, 6.15),
        "A-112": (1.85, 6.15),
        "A-113": (0.0, 4.65),
        "A-114": (1.85, 4.65),
        "A-100": (0.0, 3.05),
        "A-122": (1.85, 3.05),
        "A-123": (3.70, 3.05),
        "A-121": (0.0, 1.50),
        "A-124": (1.85, 1.50),
        "A-125": (3.70, 1.50),
        "A-131": (3.70, 0.05),
        "A-132": (5.70, 2.40),
        "A-133": (7.50, 3.05),
        "A-134": (9.30, 3.05),
        "A-141": (7.50, 1.35),
        "A-142": (9.30, 1.35),
        "A-143": (11.10, 1.35),
        "A-144": (9.30, -0.25),
        "A-145": (11.10, -0.25),
    }

    def box_centre(aid):
        x, y = pos[aid]
        return x + w / 2, y + h / 2

    fig, ax = plt.subplots(figsize=(11.2, 7.4))
    crit_ids = {a["id"] for a in data["activities"] if a["critical"]}
    for a in data["activities"]:
        for pred in a["predecessors"]:
            x0, y0 = box_centre(pred)
            x1, y1 = box_centre(a["id"])
            both = pred in crit_ids and a["critical"]
            ax.add_patch(
                FancyArrowPatch(
                    (x0 + w / 2 - 0.02, y0),
                    (x1 - w / 2 + 0.02, y1),
                    arrowstyle="-|>",
                    mutation_scale=9,
                    lw=1.35 if both else 0.55,
                    color=CRIMSON if both else "#7A8699",
                    zorder=1,
                )
            )

    for a in data["activities"]:
        x, y = pos[a["id"]]
        crit = a["critical"]
        edge = CRIMSON if crit else (NAVY if a.get("gate_constrained") else "#7A8699")
        lw = 1.6 if crit or a.get("gate_constrained") else 0.8
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02,rounding_size=0.04",
                facecolor="white",
                edgecolor=edge,
                linewidth=lw,
                zorder=2,
            )
        )
        es = datetime.fromisoformat(str(a["es"])).strftime("%d %b")
        ef = datetime.fromisoformat(str(a["ef"])).strftime("%d %b")
        ls = datetime.fromisoformat(str(a["ls"])).strftime("%d %b")
        lf = datetime.fromisoformat(str(a["lf"])).strftime("%d %b")
        cx, cy = x + w / 2, y + h / 2
        ax.text(cx, cy + 0.32, f"{es}  {a['id']}  {ef}", ha="center", va="center", fontsize=5.6, zorder=3)
        ax.text(cx, cy + 0.04, f"{ls}  D={a['d']}  {lf}", ha="center", va="center", fontsize=5.3, zorder=3)
        tf_lab = f"TF={a['tf']}" + ("  Gate 1" if a.get("gate_constrained") else "")
        ax.text(cx, cy - 0.28, tf_lab, ha="center", va="center", fontsize=5.6, color=CRIMSON if crit else NAVY, zorder=3)

    ax.text(0.0, 7.35, "Governance / permits / heritage", fontsize=8, color=NAVY)
    ax.text(0.0, 4.20, "Vehicle / stack", fontsize=8, color=NAVY)
    ax.text(0.0, 2.70, "GSE / RF / avionics", fontsize=8, color=NAVY)
    ax.text(7.50, 4.20, "Hot fire then LRR tail (wrapped)", fontsize=8, color=NAVY)
    ax.set_xlim(-0.35, 13.0)
    ax.set_ylim(-0.55, 7.65)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    save(fig, "network_logic.pdf")


def main() -> None:
    data = load()
    plot_gantt(data)
    plot_compression(data)
    plot_network(data)


if __name__ == "__main__":
    main()
