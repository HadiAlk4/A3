#!/usr/bin/env python3
"""Generate Section 7 EVM figure from data/pep_baseline.yaml.

Two panels at a single status date (M-4). Not a 14-week progress history.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

from datetime import date, datetime
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
AMBER = "#E76F51"
GREY = "#E0E0E0"
GREEN_BAND = "#D5F5E3"
AMBER_BAND = "#FDEBD0"
RED_BAND = "#F5B7B1"

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


def D(s) -> date:
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, date):
        return s
    return date.fromisoformat(str(s))


def save(fig, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    out = FIG / name
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def money(v: float) -> str:
    return f"${v:,.0f}"


def plot_evm(data) -> None:
    proj = data["project"]
    evm = data["evm"]
    m4 = data["evm_m4"]
    pv = m4["pv"]
    onp = m4["on_plan"]
    late = m4["late_stack"]
    assert pv == proj["pv_at_m4"]

    # Reported indices must match the locked table (2 d.p.), not a hidden third decimal.
    for case, label in ((onp, "on_plan"), (late, "late_stack")):
        cpi = case["ev"] / case["ac"]
        spi = case["ev"] / pv
        if round(cpi + 1e-12, 2) != case["cpi"]:
            raise SystemExit(f"{label} CPI {case['cpi']} != round(EV/AC,2)={round(cpi, 2)}")
        if round(spi + 1e-12, 2) != case["spi"]:
            raise SystemExit(f"{label} SPI {case['spi']} != round(EV/PV,2)={round(spi, 2)}")
        eac = case["ac"] + (proj["base_estimate"] - case["ev"]) / case["cpi"]
        if abs(eac - case["eac_work"]) > 0.51:
            raise SystemExit(f"{label} eac_work {case['eac_work']} != {eac:.1f}")
        ieac = proj["bac"] / case["cpi"]
        if abs(ieac - case["ieac_bac"]) > 0.51:
            raise SystemExit(f"{label} ieac_bac {case['ieac_bac']} != {ieac:.1f}")

    fig, (ax_bar, ax_band) = plt.subplots(
        2, 1, figsize=(10.4, 7.15), gridspec_kw={"height_ratios": [1.15, 0.95]}
    )

    # --- Upper: PV / EV / AC at the single M-4 status date ---
    x = [0.0, 1.0]
    width = 0.22
    series = [
        (pv, pv, NAVY, "PV"),
        (onp["ev"], late["ev"], TEAL, "EV"),
        (onp["ac"], late["ac"], CRIMSON, "AC"),
    ]
    offsets = [-width, 0.0, width]
    for (v0, v1, colour, _name), dx in zip(series, offsets):
        ax_bar.bar(
            [x[0] + dx, x[1] + dx],
            [v0, v1],
            width=width * 0.92,
            color=colour,
            edgecolor="none",
            zorder=3,
        )
        for xi, val in ((x[0] + dx, v0), (x[1] + dx, v1)):
            ax_bar.text(
                xi,
                val + 12000,
                money(val),
                ha="center",
                va="bottom",
                fontsize=6.8,
                color=NAVY,
                fontweight="bold",
                zorder=4,
            )

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(
        [
            f"On-plan illustration\nCPI {onp['cpi']:.2f}  SPI {onp['spi']:.2f}  {onp['band']}",
            f"Late stack illustration\nCPI {late['cpi']:.2f}  SPI {late['spi']:.2f}  {late['band']}",
        ]
    )
    ax_bar.set_xlim(-0.55, 1.55)
    ax_bar.set_ylim(0, 980000)
    ax_bar.set_ylabel("AUD")
    ax_bar.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"${v/1_000:.0f}k"))
    ax_bar.grid(axis="y", color=GREY, linewidth=0.7, zorder=1)
    ax_bar.set_axisbelow(True)
    for spine in ("top", "right"):
        ax_bar.spines[spine].set_visible(False)
    m4_date = D(data["milestones"]["M4"]["date"])
    ax_bar.text(
        0.0,
        1.02,
        (
            f"Status date {m4_date.day} {m4_date.strftime('%b')} {m4_date.year} (M-4)"
            "  ·  illustrative only; campaign not yet executed"
        ),
        transform=ax_bar.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.0,
        color=NAVY,
        fontweight="bold",
    )
    ax_bar.legend(
        handles=[
            Patch(facecolor=NAVY, edgecolor="none", label="PV (work PMB)"),
            Patch(facecolor=TEAL, edgecolor="none", label="EV"),
            Patch(facecolor=CRIMSON, edgecolor="none", label="AC"),
        ],
        loc="upper right",
        frameon=True,
        fontsize=7.4,
        edgecolor=GREY,
    )

    # --- Lower: Green / Amber / Red index bands with the two M-4 readings ---
    green_lo, green_hi = evm["green_lo"], evm["green_hi"]
    amber_lo, red_lt = evm["amber_lo"], evm["red_lt"]
    ax_band.axhspan(0.80, red_lt, facecolor=RED_BAND, edgecolor="none", zorder=0)
    ax_band.axhspan(amber_lo, green_lo, facecolor=AMBER_BAND, edgecolor="none", zorder=0)
    ax_band.axhspan(green_lo, green_hi, facecolor=GREEN_BAND, edgecolor="none", zorder=0)
    ax_band.axhline(1.0, color=NAVY, linewidth=0.8, linestyle=":", zorder=1)
    ax_band.axhline(green_lo, color=TEAL, linewidth=0.6, linestyle="--", zorder=1)
    ax_band.axhline(amber_lo, color=AMBER, linewidth=0.6, linestyle="--", zorder=1)

    ax_band.scatter(
        [0 - 0.08], [onp["cpi"]], s=70, color=TEAL, edgecolor=NAVY, linewidth=0.5, zorder=4
    )
    ax_band.scatter(
        [0 + 0.08], [onp["spi"]], s=70, marker="s", color=NAVY, edgecolor=NAVY, linewidth=0.5, zorder=4
    )
    ax_band.scatter(
        [1 - 0.08], [late["cpi"]], s=70, color=AMBER, edgecolor=NAVY, linewidth=0.5, zorder=4
    )
    ax_band.scatter(
        [1 + 0.08], [late["spi"]], s=70, marker="s", color=NAVY, edgecolor=NAVY, linewidth=0.5, zorder=4
    )
    ax_band.annotate(
        f"CPI {onp['cpi']:.2f}",
        (0 - 0.08, onp["cpi"]),
        textcoords="offset points",
        xytext=(-18, 8),
        fontsize=7.2,
        color=TEAL,
        fontweight="bold",
    )
    ax_band.annotate(
        f"SPI {onp['spi']:.2f}",
        (0 + 0.08, onp["spi"]),
        textcoords="offset points",
        xytext=(10, 8),
        fontsize=7.2,
        color=NAVY,
        fontweight="bold",
    )
    ax_band.annotate(
        f"CPI {late['cpi']:.2f}",
        (1 - 0.08, late["cpi"]),
        textcoords="offset points",
        xytext=(-22, -14),
        fontsize=7.2,
        color=AMBER,
        fontweight="bold",
    )
    ax_band.annotate(
        f"SPI {late['spi']:.2f}",
        (1 + 0.08, late["spi"]),
        textcoords="offset points",
        xytext=(10, -14),
        fontsize=7.2,
        color=NAVY,
        fontweight="bold",
    )

    ax_band.set_xticks(x)
    ax_band.set_xticklabels(
        [f"On-plan ({onp['band']} band)", f"Late stack ({late['band']} band)"]
    )
    ax_band.set_xlim(-0.55, 1.55)
    ax_band.set_ylim(0.82, 1.10)
    ax_band.set_ylabel("CPI / SPI")
    ax_band.set_yticks(sorted({red_lt, amber_lo, green_lo, 1.0, green_hi}))
    for spine in ("top", "right"):
        ax_band.spines[spine].set_visible(False)
    ax_band.text(
        1.52,
        1.00,
        f"Green  {green_lo:.2f}–{green_hi:.2f}",
        ha="right",
        va="center",
        fontsize=7.0,
        color=NAVY,
    )
    ax_band.text(
        1.52,
        0.925,
        f"Amber  {amber_lo:.2f}–<{green_lo:.2f}",
        ha="right",
        va="center",
        fontsize=7.0,
        color=NAVY,
    )
    ax_band.text(
        1.52,
        0.86,
        f"Red  <{red_lt:.2f}  or  T-0 slip >{evm['t0_slip_trigger_days']} d",
        ha="right",
        va="center",
        fontsize=7.0,
        color=CRIMSON,
        fontweight="bold",
    )
    ax_band.legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=TEAL,
                markeredgecolor=NAVY,
                markersize=7,
                label="CPI",
            ),
            Line2D(
                [0],
                [0],
                marker="s",
                color="none",
                markerfacecolor=NAVY,
                markeredgecolor=NAVY,
                markersize=7,
                label="SPI",
            ),
        ],
        loc="upper left",
        frameon=True,
        fontsize=7.4,
        edgecolor=GREY,
    )

    fig.tight_layout()
    save(fig, "evm_example.pdf")


def main() -> None:
    plot_evm(load())


if __name__ == "__main__":
    main()
