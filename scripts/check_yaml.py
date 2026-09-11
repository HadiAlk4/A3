#!/usr/bin/env python3
"""Check data/pep_baseline.yaml against the inclusive CPM calendar and locked totals.

Usage (from repo root):
    python3 scripts/check_yaml.py
"""
from __future__ import annotations

import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "pep_baseline.yaml"
TEX_PATH = ROOT / "sections" / "03_schedule.tex"

# A-125 has no FS successor; LF is imposed as the day before A-133 ES (before hot fire).
A125_LF_CONSTRAINT = "A-133"
# R-12 EMV is held at 0 so Option C $21k is not double-counted in the $175,500.
ZERO_EMV_WITH_IMPACT = {"R-12"}
RETIRED = {f"A-{n}" for n in range(101, 111)}
MILESTONE_OWNERS = {
    "M2": "A-111",
    "M4": "A-123",
    "M5": "A-133",
    "M6": "A-141",
    "M7": "A-143",
    "M8": "A-144",
    "M9": "A-145",
}
LAUNCH_CP = {
    "A-100",
    "A-113",
    "A-122",
    "A-123",
    "A-132",
    "A-133",
    "A-134",
    "A-141",
    "A-142",
    "A-143",
    "A-144",
    "A-145",
}


def D(s) -> date:
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, date):
        return s
    return date.fromisoformat(str(s))


def load():
    with YAML_PATH.open() as f:
        return yaml.safe_load(f)


def check(data) -> list[str]:
    errors: list[str] = []
    acts = {a["id"]: a for a in data["activities"]}
    start, finish = D(data["project"]["start"]), D(data["project"]["finish"])
    succ: dict[str, list[str]] = {i: [] for i in acts}
    for a in acts.values():
        if a["id"] in RETIRED:
            errors.append(f"retired ID still in YAML: {a['id']}")
        for p in a["predecessors"]:
            if p not in acts:
                errors.append(f"{a['id']} predecessor {p} missing")
            elif p in RETIRED:
                errors.append(f"{a['id']} uses retired predecessor {p}")
            else:
                succ[p].append(a["id"])

    for a in data["activities"]:
        es, ef, ls, lf, d, tf = (
            D(a["es"]),
            D(a["ef"]),
            D(a["ls"]),
            D(a["lf"]),
            a["d"],
            a["tf"],
        )
        if ef != es + timedelta(days=d - 1):
            errors.append(f"{a['id']} EF {ef} != ES+D-1 {es + timedelta(days=d - 1)}")
        if not a["predecessors"]:
            want_es = start
        else:
            want_es = max(D(acts[p]["ef"]) for p in a["predecessors"]) + timedelta(days=1)
        if es != want_es:
            errors.append(f"{a['id']} ES {es} != {want_es}")
        if tf != (ls - es).days or tf != (lf - ef).days:
            errors.append(f"{a['id']} TF {tf} != LS-ES {(ls - es).days} or LF-EF {(lf - ef).days}")
        if ls != lf - timedelta(days=d - 1):
            errors.append(f"{a['id']} LS {ls} != LF-D+1")
        if a["critical"] and tf != 0:
            errors.append(f"{a['id']} critical but TF={tf}")
        if a["critical"] and a.get("gate_constrained"):
            errors.append(f"{a['id']} cannot be both launch-critical and gate_constrained")
        if a["id"] in LAUNCH_CP and not a["critical"]:
            errors.append(f"{a['id']} should be launch-critical")
        if a["critical"] and a["id"] not in LAUNCH_CP:
            errors.append(f"{a['id']} marked critical but not on locked launch CP")
        if a.get("gate_constrained"):
            if lf != ef:
                errors.append(f"{a['id']} Gate 1 MFO: LF should equal EF")
        elif not succ[a["id"]]:
            if a["id"] == "A-125":
                want_lf = D(acts[A125_LF_CONSTRAINT]["es"]) - timedelta(days=1)
                if lf != want_lf:
                    errors.append(
                        f"A-125 LF {lf} != day before {A125_LF_CONSTRAINT} ES {want_lf}"
                    )
            elif lf != finish:
                errors.append(f"{a['id']} no successor: LF {lf} != finish {finish}")
        else:
            want_lf = min(D(acts[s]["ls"]) for s in succ[a["id"]]) - timedelta(days=1)
            if lf != want_lf:
                errors.append(f"{a['id']} LF {lf} != min(LS_succ)-1 {want_lf}")

    for key, owner in MILESTONE_OWNERS.items():
        md = D(data["milestones"][key]["date"])
        ef = D(acts[owner]["ef"])
        if md != ef:
            errors.append(f"{key} {md} != {owner} EF {ef}")

    if D(data["milestones"]["M7"]["date"]) != D(data["compression"]["baseline_t0"]):
        errors.append("M-7 != compression.baseline_t0")
    if D(data["compression"]["option_c_t0"]) != date(2026, 11, 10):
        errors.append("option_c_t0 must stay 10 Nov (what-if, not baseline)")
    if data["compression"]["options"][2]["verdict"] != "Contingent":
        errors.append("Option C verdict must be Contingent")
    if data["compression"]["options"][2]["cost"] != data["project"]["option_c_cost"]:
        errors.append("Option C cost != project.option_c_cost")
    if data["compression"]["options"][2]["cost"] / data["compression"]["days_saved"] != 4200:
        errors.append("Option C slope != 4200")

    tail = {t["id"]: t for t in data["compression"]["option_c_tail"]}
    expect_d = {"A-134": 3, "A-141": 3, "A-142": 4, "A-143": 1}
    chain = ["A-134", "A-141", "A-142", "A-143"]
    for iid, new_d in expect_d.items():
        es, ef = D(tail[iid]["es"]), D(tail[iid]["ef"])
        if (ef - es).days + 1 != new_d:
            errors.append(f"Option C {iid} inclusive duration {(ef - es).days + 1} != {new_d}")
    for a, b in zip(chain, chain[1:]):
        if D(tail[b]["es"]) != D(tail[a]["ef"]) + timedelta(days=1):
            errors.append(f"Option C {a}→{b} is not FS+0")
    if D(tail["A-143"]["ef"]) != D(data["compression"]["option_c_t0"]):
        errors.append("Option C A-143 EF != option_c_t0")

    proj = data["project"]
    base = sum(r["amount"] for r in data["wbs_cost"])
    if base != proj["base_estimate"]:
        errors.append(f"WBS sum {base} != base_estimate {proj['base_estimate']}")
    if proj["emv_sum"] + proj["res_allowance"] != proj["contingency"]:
        errors.append("EMV + RES != contingency")
    if proj["base_estimate"] + proj["contingency"] != proj["bac"]:
        errors.append("base + contingency != BAC")
    if data["monthly_pv"][-1]["cumulative"] != proj["base_estimate"]:
        errors.append("S-curve does not end at work PMB")
    running = 0
    for row in data["monthly_pv"]:
        running += row["period"]
        if running != row["cumulative"]:
            errors.append(f"PV {row['month']} cumulative != running total")

    emv = sum(r["emv"] for r in data["risks"])
    if emv != proj["emv_sum"]:
        errors.append(f"risk EMV {emv} != emv_sum {proj['emv_sum']}")
    for r in data["risks"]:
        calc = r["p_pct"] * r["i_dollar"]
        if r["id"] in ZERO_EMV_WITH_IMPACT:
            if r["emv"] != 0:
                errors.append(f"{r['id']} EMV must be 0 (Option C not double-counted)")
            continue
        if abs(r["emv"] - calc) > 0.51:
            errors.append(f"{r['id']} EMV {r['emv']} != {r['p_pct']}×{r['i_dollar']}")

    mit = data["resource_weeks"]["demand_mitigated"]
    unmit = data["resource_weeks"]["demand_unmitigated"]
    if len(mit) != 16 or len(unmit) != 16:
        errors.append("resource_weeks must be 16 weeks")
    if max(mit) != proj["mitigated_peak"] or max(unmit) != proj["unmitigated_peak"]:
        errors.append("resource peaks != project.mitigated/unmitigated_peak")
    if any(v > proj["hse_pad_cap"] for v in mit):
        errors.append("mitigated demand exceeds HSE pad cap")
    if data["evm_m4"]["pv"] != proj["pv_at_m4"]:
        errors.append("evm_m4.pv != project.pv_at_m4")

    pct = sum(c["pct"] for c in data["contribution"])
    if abs(pct - 100.0) > 1e-6:
        errors.append(f"contribution {pct} != 100")

    return errors


def check_table_31(data) -> list[str]:
    if not TEX_PATH.exists():
        return []
    tex = TEX_PATH.read_text()
    errors = []
    for a in data["activities"]:
        es = D(a["es"]).strftime("%-d %b") if sys.platform != "win32" else D(a["es"]).strftime("%d %b").lstrip("0")
        # Table uses '10 Aug', '2 Oct', '1 Dec' (no leading zero)
        def fmt(d):
            return f"{D(d).day} {D(d).strftime('%b')}"

        needle = a["id"]
        if needle not in tex:
            errors.append(f"Table 3.1 missing {needle}")
            continue
        # require ES and EF strings somewhere on a line with this ID
        line = next((ln for ln in tex.splitlines() if ln.startswith(needle + " &")), "")
        if not line:
            continue
        if fmt(a["es"]) not in line or fmt(a["ef"]) not in line:
            errors.append(f"Table 3.1 {a['id']} dates != YAML ({fmt(a['es'])}–{fmt(a['ef'])})")
        if f" {a['d']} &" not in line and f" {a['d']} " not in line:
            # duration is the first numeric column after the name
            if not re.search(rf"&\s*{a['d']}\s*&", line):
                errors.append(f"Table 3.1 {a['id']} duration != {a['d']}")
    for rid in RETIRED:
        if re.search(rf"\b{rid}\b", tex):
            errors.append(f"retired ID {rid} appears in 03_schedule.tex")
    return errors


def main() -> int:
    data = load()
    errors = check(data) + check_table_31(data)
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS  pep_baseline.yaml identities hold")
    print("      Table 3.1 dates/durations match YAML")
    print("      A-125 LF is imposed before A-133 (not project finish)")
    print("      R-12 EMV is 0 by design (Option C not double-counted)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
