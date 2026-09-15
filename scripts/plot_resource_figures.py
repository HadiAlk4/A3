#!/usr/bin/env python3
"""Generate Section 5 resource histogram from activity × named crew."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from resource_occupancy import demand_series, surge_days, weekly_peaks  # noqa: E402

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
    mit = data["resource_weeks"]["demand_mitigated"]
    unmit = data["resource_weeks"]["demand_unmitigated"]
    proj = data["project"]
    n = len(mit)
    weeks = list(range(1, n + 1))
    organic = proj["organic_crew"]
    cap = proj["hse_pad_cap"]
    built_m, built_u = demand_series(data)
    assert mit == built_m and unmit == built_u
    assert max(unmit) == proj["unmitigated_peak"]
    assert max(mit) == proj["mitigated_peak"]
    assert max(mit) <= cap
    assert surge_days(data["resource_model"]) == 7

    fig, ax = plt.subplots(figsize=(10.8, 5.25))
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
    ax.text(n + 0.35, organic + 0.18, "Organic crew  8", ha="right", va="bottom", fontsize=7.5, color=NAVY)
    ax.text(n + 0.35, cap + 0.18, "HSE pad cap  12", ha="right", va="bottom", fontsize=7.5, color=CRIMSON)

    ax.annotate(
        "A-125 RF at ES--EF: +2 unique heads in weeks 3--6.\n"
        "Unmitigated RF uses the late bar (LS--LF, weeks 9--11).",
        xy=(4.2, 8.2),
        xytext=(0.55, 15.15),
        fontsize=7.1,
        color=NAVY,
        ha="left",
        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.9),
        bbox=dict(boxstyle="round,pad=0.32", facecolor="white", edgecolor=GREY),
        zorder=5,
    )
    ax.annotate(
        "Surge: four heads, 24--30 Oct only (7~d).\n"
        "Replaces unmitigated OT; not stacked.",
        xy=(11.2, 12.05),
        xytext=(7.15, 15.45),
        fontsize=7.1,
        color=NAVY,
        ha="left",
        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=0.9),
        bbox=dict(boxstyle="round,pad=0.32", facecolor="white", edgecolor=GREY),
        zorder=5,
    )
    ax.text(10.0, 14.45, "Unmitigated peak 14", ha="center", fontsize=7.4, color=CRIMSON, fontweight="bold")

    ax.set_xlim(0.4, n + 0.6)
    ax.set_ylim(0, 16.4)
    ax.set_xticks(weeks)
    ax.set_xlabel("Campaign week (week 1 starts 10 August 2026; week 17 holds 30 Nov--1 Dec)")
    ax.set_ylabel("People on pad (simultaneous)")
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


def _fmt_day(d) -> str:
    return f"{d.day}~{d.strftime('%b')}"


def write_build_table(data) -> None:
    mit_rows = weekly_peaks(data, mitigated=True)
    un_rows = weekly_peaks(data, mitigated=False)
    lines = []
    for m, u in zip(mit_rows, un_rows):
        lines.append(
            f"{m['week']} & {_fmt_day(m['day'])} & {m['base']} & {m['rf']} & {m['surge']} & "
            f"{m['total']} & {_fmt_day(u['day'])} & {u['base']} & {u['rf']} & {u['ot']} & {u['total']} \\\\"
        )
    n_surge = surge_days(data["resource_model"])
    tex = (
        "% Generated by scripts/plot_resource_figures.py — do not edit by hand.\n"
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\footnotesize\n"
        "\\setlength{\\tabcolsep}{3.2pt}\n"
        "\\caption[Weekly simultaneous pad occupancy]{Weekly simultaneous pad occupancy, "
        "from activity $\\times$ named crew. Each weekly total is the maximum unique-head "
        "count on any calendar day that week (HSE cap is simultaneous, not weekly unique). "
        f"Mitigated A-125 uses $ES$--$EF$; unmitigated uses the late bar $LS$--$LF$. "
        f"Surge is four heads on 24--30~Oct only ({n_surge}~days). Unmitigated overtime is four "
        "heads on WDR and static fire (16--30~Oct). Base, RF, surge and OT are disjoint name "
        "sets, so they add on the peak day.}\n"
        "\\label{tab:resource-build}\n"
        "\\begin{tabular}{@{}r l r r r r l r r r r@{}}\n"
        "\\toprule\n"
        "Week & Mit.\\ day & Base & RF & Surge & Mit. & Unmit.\\ day & Base & RF & OT & Unmit. \\\\\n"
        "\\midrule\n"
        + "\n".join(lines)
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n"
    )
    out = ROOT / "sections" / "generated" / "s5_resource_build.tex"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tex)
    print("wrote", out)


def main() -> None:
    data = load()
    plot_histogram(data)
    write_build_table(data)


if __name__ == "__main__":
    main()
