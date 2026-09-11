#!/usr/bin/env python3
"""Generate Section 3 figures from data/pep_baseline.yaml.

Swimlane PERT (not NetworkX), baseline Gantt, and compression trade-off bars.
All dates, floats, costs, and verdicts are read from the YAML.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import yaml
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, PathPatch, Rectangle
from matplotlib.path import Path as MPath

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


def parse(d) -> datetime:
    return datetime.fromisoformat(str(d))


def fmt_day(d) -> str:
    return parse(d).strftime("%-d %b")


def save(fig, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    out = FIG / name
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def plot_gantt(data) -> None:
    acts = data["activities"]
    miles = data["milestones"]
    start = parse(data["project"]["start"])
    finish = parse(data["project"]["finish"])
    fig, ax = plt.subplots(figsize=(11.4, 8.5))
    n = len(acts)
    y_gate = None
    for i, a in enumerate(reversed(acts)):
        y = i
        es, ef, lf = parse(a["es"]), parse(a["ef"]), parse(a["lf"])
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
        if (not a["critical"]) and a["tf"] > 0:
            # Inclusive calendar: whisker is EF+1 .. LF (width = TF days).
            ax.barh(
                y,
                a["tf"],
                left=ef + timedelta(days=1),
                height=0.16,
                color=TEAL,
                edgecolor="none",
                zorder=4,
            )
        if a.get("gate_constrained"):
            y_gate = y

    labels = []
    for a in reversed(acts):
        nm = a["name"]
        if a["id"] == "A-100":
            nm = "Vehicle receipt window (ext.)"
        labels.append(f"{a['id']}  {nm}")
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=6.6)
    for tick in ax.get_yticklabels():
        tick.set_clip_on(False)
    ax.set_xlim(start - timedelta(days=1), finish + timedelta(days=2))
    ticks = []
    t = start
    while t <= finish:
        ticks.append(t)
        t += timedelta(days=14)
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_xlabel("Date (2026)")
    ax.grid(axis="x", color=GREY, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(-1.55, n - 0.35)

    # M-4 … M-9: full-height crimson. M-2 is a smaller navy marker on A-111.
    for key, name in (
        ("M4", "M-4"),
        ("M5", "M-5"),
        ("M6", "M-6"),
        ("M7", "M-7"),
        ("M8", "M-8"),
        ("M9", "M-9"),
    ):
        x = parse(miles[key]["date"])
        ax.axvline(x, color=CRIMSON, ls="--", lw=0.9, zorder=1)
        ax.text(
            x,
            -1.15,
            name,
            rotation=90,
            va="top",
            ha="center",
            fontsize=6.5,
            color=CRIMSON,
        )

    if y_gate is not None:
        x_m2 = parse(miles["M2"]["date"])
        y0, y1 = ax.get_ylim()
        span = y1 - y0
        ax.axvline(
            x_m2,
            color=NAVY,
            ls=":",
            lw=1.05,
            ymin=(y_gate - 0.55 - y0) / span,
            ymax=(y_gate + 0.55 - y0) / span,
            zorder=4,
        )
        ax.scatter(
            [x_m2],
            [y_gate],
            marker="D",
            s=32,
            color=NAVY,
            zorder=5,
            edgecolors="white",
            linewidths=0.4,
        )
        ax.text(
            x_m2 + timedelta(days=1.4),
            y_gate + 0.62,
            "M-2",
            fontsize=6.5,
            color=NAVY,
            va="bottom",
            zorder=5,
        )

    legend = [
        Rectangle((0, 0), 1, 1, color=CRIMSON, label="Launch-critical ($TF=0$)"),
        Rectangle((0, 0), 1, 1, color=NAVY, label="Non-critical / Gate 1"),
        Line2D([0], [0], color=TEAL, lw=2, label="Total float to $LF$"),
        Line2D(
            [0],
            [0],
            marker="D",
            color=NAVY,
            ls="None",
            label="Gate 1 lock (M-2)",
        ),
    ]
    ax.legend(
        handles=legend,
        loc="upper left",
        bbox_to_anchor=(0.0, -0.12),
        ncol=4,
        frameon=False,
        fontsize=7,
    )
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.subplots_adjust(left=0.30)
    save(fig, "gantt_chart.pdf")


def plot_compression(data) -> None:
    block = data["compression"]
    opts = block["options"]
    days = block["days_saved"]
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2))

    labels = [o["id"] for o in opts]
    costs = [o["cost"] / 1000 for o in opts]
    risk_map = {"High": 3, "Medium": 2, "Low": 1}
    risks = [risk_map[o["risk"]] for o in opts]
    colours = [NAVY, CRIMSON, AMBER]

    ax = axes[0]
    bars = ax.bar(labels, costs, color=colours, width=0.62, zorder=3)
    ax.set_ylabel("Added cost (thousand AUD)")
    ax.set_xlabel(f"Option (all save {days} days)")
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
    ax.set_xlabel(f"Option (all save {days} days)")
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
    """Left-to-right swimlanes. Seven-field PERT box. YAML predecessors only."""
    w, h = 1.62, 1.18
    # charts.md lanes. A-121 sits on the vehicle/stack row, not GSE.
    # Tail is left-to-right; A-141 is under A-134 (not under A-133).
    pos = {
        "A-113": (0.00, 6.35),
        "A-114": (1.90, 6.35),
        "A-111": (3.80, 6.35),
        "A-112": (5.70, 6.35),
        "A-100": (0.00, 4.45),
        "A-121": (1.90, 4.45),
        "A-122": (3.80, 4.45),
        "A-123": (5.70, 4.45),
        "A-124": (1.90, 2.55),
        "A-125": (3.80, 2.55),
        "A-131": (5.70, 2.55),
        "A-132": (7.70, 3.50),
        "A-133": (9.60, 4.45),
        "A-134": (11.50, 4.45),
        "A-141": (11.50, 2.55),
        "A-142": (11.50, 0.65),
        "A-143": (13.40, 0.65),
        "A-144": (13.40, -1.25),
        "A-145": (15.30, -1.25),
    }

    def centre(aid):
        x, y = pos[aid]
        return x + w / 2, y + h / 2

    def port(aid, side):
        x, y = pos[aid]
        cx, cy = x + w / 2, y + h / 2
        return {
            "E": (x + w, cy),
            "W": (x, cy),
            "N": (cx, y + h),
            "S": (cx, y),
        }[side]

    def draw_link(ax, pred, succ, colour, lw, start_side, end_side, vias=None):
        p0 = port(pred, start_side)
        p1 = port(succ, end_side)
        pts = [p0, *(vias or []), p1]
        if len(pts) == 2:
            ax.add_patch(
                FancyArrowPatch(
                    pts[0],
                    pts[1],
                    arrowstyle="-|>",
                    mutation_scale=9,
                    lw=lw,
                    color=colour,
                    zorder=1,
                    shrinkA=0,
                    shrinkB=1.5,
                )
            )
            return
        verts = pts
        codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 1)
        ax.add_patch(
            PathPatch(
                MPath(verts, codes),
                facecolor="none",
                edgecolor=colour,
                lw=lw,
                capstyle="butt",
                joinstyle="miter",
                zorder=1,
            )
        )
        ax.add_patch(
            FancyArrowPatch(
                verts[-2],
                verts[-1],
                arrowstyle="-|>",
                mutation_scale=9,
                lw=lw,
                color=colour,
                zorder=1,
                shrinkA=0,
                shrinkB=1.5,
            )
        )

    crit_ids = {a["id"] for a in data["activities"] if a["critical"]}
    fig, ax = plt.subplots(figsize=(14.2, 8.2))

    # Explicit ports so long FS links do not punch through unrelated boxes.
    a132 = centre("A-132")
    a133 = centre("A-133")
    link_spec = {
        ("A-111", "A-112"): ("E", "W", None),
        ("A-100", "A-122"): (
            "N",
            "N",
            [
                (centre("A-100")[0], 5.88),
                (centre("A-122")[0], 5.88),
            ],
        ),
        ("A-121", "A-122"): ("E", "W", None),
        ("A-122", "A-123"): ("E", "W", None),
        ("A-121", "A-124"): ("S", "N", None),
        ("A-121", "A-125"): (
            "S",
            "N",
            [
                (centre("A-121")[0], 3.98),
                (centre("A-125")[0], 3.98),
            ],
        ),
        ("A-122", "A-131"): (
            "S",
            "N",
            [
                (centre("A-122")[0] + 0.55, pos["A-122"][1] - 0.12),
                (centre("A-131")[0], pos["A-122"][1] - 0.12),
            ],
        ),
        ("A-114", "A-132"): (
            "S",
            "N",
            [
                (centre("A-114")[0], 6.14),
                (a132[0], 6.14),
            ],
        ),
        ("A-123", "A-132"): ("E", "W", None),
        ("A-124", "A-132"): (
            "E",
            "S",
            [
                (pos["A-132"][0] + w * 0.25, centre("A-124")[1]),
            ],
        ),
        ("A-131", "A-132"): ("E", "S", None),
        ("A-132", "A-133"): ("E", "W", None),
        ("A-113", "A-133"): (
            "N",
            "N",
            [
                (centre("A-113")[0], 7.72),
                (a133[0], 7.72),
            ],
        ),
        ("A-133", "A-134"): ("E", "W", None),
        ("A-134", "A-141"): ("S", "N", None),
        ("A-141", "A-142"): ("S", "N", None),
        ("A-142", "A-143"): ("E", "W", None),
        ("A-143", "A-144"): ("S", "N", None),
        ("A-144", "A-145"): ("E", "W", None),
    }

    drawn = set()
    for a in data["activities"]:
        for pred in a["predecessors"]:
            key = (pred, a["id"])
            both = pred in crit_ids and a["critical"]
            colour = CRIMSON if both else NAVY
            lw = 1.4 if both else 0.6
            spec = link_spec.get(key)
            if spec is None:
                # Fallback: east-west if successor is to the right, else north-south.
                dx = centre(a["id"])[0] - centre(pred)[0]
                dy = centre(a["id"])[1] - centre(pred)[1]
                if abs(dx) >= abs(dy):
                    spec = ("E" if dx > 0 else "W", "W" if dx > 0 else "E", None)
                else:
                    spec = ("N" if dy > 0 else "S", "S" if dy > 0 else "N", None)
            draw_link(ax, pred, a["id"], colour, lw, spec[0], spec[1], spec[2])
            drawn.add(key)

    expected = {(p, a["id"]) for a in data["activities"] for p in a["predecessors"]}
    missing = expected - drawn
    if missing:
        raise RuntimeError(f"undrawn FS links: {missing}")

    col_w = w / 3
    top_h = h * 0.36
    mid_h = h * 0.36
    bot_h = h - top_h - mid_h

    for a in data["activities"]:
        x, y = pos[a["id"]]
        crit = a["critical"]
        gate = bool(a.get("gate_constrained"))
        edge = CRIMSON if crit else NAVY
        lw = 1.65 if crit or gate else 0.85
        ax.add_patch(
            Rectangle(
                (x, y),
                w,
                h,
                facecolor="white",
                edgecolor=edge,
                linewidth=lw,
                zorder=2,
            )
        )
        y_mid = y + bot_h
        y_top = y + bot_h + mid_h
        ax.plot([x, x + w], [y_top, y_top], color=edge, lw=0.55, zorder=3)
        ax.plot([x, x + w], [y_mid, y_mid], color=edge, lw=0.55, zorder=3)
        ax.plot(
            [x + col_w, x + col_w],
            [y_mid, y + h],
            color=edge,
            lw=0.45,
            zorder=3,
        )
        ax.plot(
            [x + 2 * col_w, x + 2 * col_w],
            [y_mid, y + h],
            color=edge,
            lw=0.45,
            zorder=3,
        )
        es, ef = fmt_day(a["es"]), fmt_day(a["ef"])
        ls, lf = fmt_day(a["ls"]), fmt_day(a["lf"])
        ax.text(
            x + col_w / 2,
            y_top + top_h / 2,
            es,
            ha="center",
            va="center",
            fontsize=5.6,
            zorder=4,
        )
        ax.text(
            x + 1.5 * col_w,
            y_top + top_h / 2,
            a["id"],
            ha="center",
            va="center",
            fontsize=6.3,
            fontweight="bold",
            zorder=4,
        )
        ax.text(
            x + 2.5 * col_w,
            y_top + top_h / 2,
            ef,
            ha="center",
            va="center",
            fontsize=5.6,
            zorder=4,
        )
        ax.text(
            x + col_w / 2,
            y_mid + mid_h / 2,
            ls,
            ha="center",
            va="center",
            fontsize=5.4,
            zorder=4,
        )
        ax.text(
            x + 1.5 * col_w,
            y_mid + mid_h / 2,
            str(a["d"]),
            ha="center",
            va="center",
            fontsize=5.8,
            zorder=4,
        )
        ax.text(
            x + 2.5 * col_w,
            y_mid + mid_h / 2,
            lf,
            ha="center",
            va="center",
            fontsize=5.4,
            zorder=4,
        )
        tf_lab = f"TF={a['tf']}"
        if gate:
            tf_lab += "  Gate 1"
        ax.text(
            x + w / 2,
            y + bot_h / 2,
            tf_lab,
            ha="center",
            va="center",
            fontsize=5.8,
            color=CRIMSON if crit else NAVY,
            zorder=4,
        )
        if gate:
            ax.scatter(
                [x + w - 0.10],
                [y + h + 0.10],
                marker="D",
                s=28,
                color=NAVY,
                zorder=5,
                edgecolors="white",
                linewidths=0.35,
            )
            ax.text(
                x + w + 0.04,
                y + h + 0.10,
                "M-2",
                fontsize=6.0,
                color=NAVY,
                va="center",
                zorder=5,
            )

    ax.text(0.00, 7.88, "Permitting / heritage", fontsize=8.2, color=NAVY, va="bottom")
    ax.text(0.00, 5.78, "Vehicle / stack", fontsize=8.2, color=NAVY, va="bottom")
    ax.text(0.00, 3.88, "GSE / RF / avionics", fontsize=8.2, color=NAVY, va="bottom")
    ax.text(9.60, 5.78, "Test / launch / close", fontsize=8.2, color=NAVY, va="bottom")

    legend = [
        Line2D([0], [0], color=CRIMSON, lw=1.4, label="Launch-critical FS ($TF=0$)"),
        Line2D([0], [0], color=NAVY, lw=0.6, label="Feeder / float FS"),
        Line2D(
            [0],
            [0],
            marker="D",
            color=NAVY,
            ls="None",
            label="A-111 Gate 1 (not launch-critical)",
        ),
    ]
    ax.legend(
        handles=legend,
        loc="lower left",
        frameon=False,
        fontsize=7,
        bbox_to_anchor=(0.0, -0.08),
        ncol=3,
    )

    ax.set_xlim(-0.35, 17.15)
    ax.set_ylim(-1.55, 8.05)
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
