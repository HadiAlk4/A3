#!/usr/bin/env python3
"""Check data/pep_baseline.yaml against the inclusive CPM calendar and locked totals.

Usage (from repo root):
    python3 scripts/check_yaml.py
"""
from __future__ import annotations

import re
import sys
import importlib.util
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

from resource_occupancy import demand_series, surge_days

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "pep_baseline.yaml"
TEX_PATH = ROOT / "sections" / "03_schedule.tex"
OVERVIEW_TEX = ROOT / "sections" / "02_overview.tex"
WBS_TEX = ROOT / "sections" / "02_wbs.tex"
DELIVERY_TEX = ROOT / "sections" / "07_delivery.tex"
INTEGRATION_TEX = ROOT / "sections" / "08_integration.tex"
MAIN_TEX = ROOT / "A3.tex"
EXEC_TEX = ROOT / "sections" / "01_exec.tex"
GEN_DIR = ROOT / "sections" / "generated"

# A-125 feeds A-133 so RF is complete before hot fire. LF is derived from that FS link.
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


P_BAND_PCT = {1: 0.03, 2: 0.12, 3: 0.30, 4: 0.50, 5: 0.70}


def employment_oncost(labour: dict, *, pad: bool) -> float:
    leave_load = labour["leave_loading_on_al"] * labour["annual_leave_pct"]
    wc = labour["wc_pad_pct"] if pad else labour["wc_professional_pct"]
    return (
        1.0
        + labour["super_pct"]
        + labour["annual_leave_pct"]
        + labour["personal_leave_pct"]
        + labour["public_holiday_pct"]
        + labour["lsl_pct"]
        + leave_load
        + wc
        + labour["payroll_tax_qld_pct"]
    )


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
        if a.get("external_driver"):
            if a["critical"]:
                errors.append(f"{a['id']} external driver must not be launch-critical")
            if a["id"] in LAUNCH_CP:
                errors.append(f"{a['id']} external driver must not sit in LAUNCH_CP")
        if a["id"] in LAUNCH_CP and not a["critical"]:
            errors.append(f"{a['id']} should be launch-critical")
        if a["critical"] and a["id"] not in LAUNCH_CP:
            errors.append(f"{a['id']} marked critical but not on locked launch CP")
        if a.get("gate_constrained"):
            if lf != ef:
                errors.append(f"{a['id']} Gate 1 MFO: LF should equal EF")
        elif not succ[a["id"]]:
            if lf != finish:
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
    expect_d = {"A-134": 1, "A-141": 5, "A-142": 4, "A-143": 1}
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
    if "A-125" not in acts["A-133"]["predecessors"]:
        errors.append("A-133 predecessors must include A-125 (RF before hot fire)")

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
        band = P_BAND_PCT[r["p_res"]]
        if abs(r.get("p_res_pct", -1) - band) > 1e-9:
            errors.append(f"{r['id']} p_res_pct {r.get('p_res_pct')} != band {band}")
        calc = r["p_res_pct"] * r["i_dollar"]
        if abs(r["emv"] - calc) > 0.51:
            errors.append(f"{r['id']} residual EMV {r['emv']} != {r['p_res_pct']}×{r['i_dollar']}")

    mit = data["resource_weeks"]["demand_mitigated"]
    unmit = data["resource_weeks"]["demand_unmitigated"]
    built_m, built_u = demand_series(data)
    if mit != built_m or unmit != built_u:
        errors.append(
            f"resource_weeks != occupancy model (mit {mit} vs {built_m}; unmit {unmit} vs {built_u})"
        )
    if len(mit) != 17 or len(unmit) != 17:
        errors.append("resource_weeks must be 17 weeks (through 1 Dec)")
    if max(mit) != proj["mitigated_peak"] or max(unmit) != proj["unmitigated_peak"]:
        errors.append("resource peaks != project.mitigated/unmitigated_peak")
    if any(v > proj["hse_pad_cap"] for v in mit):
        errors.append("mitigated occupancy exceeds HSE pad cap")
    if max(unmit) <= proj["hse_pad_cap"]:
        errors.append("unmitigated peak must exceed the HSE pad cap")
    if surge_days(data["resource_model"]) != 7:
        errors.append("surge window must be 7 inclusive days")
    wdr_ef = D(acts["A-132"]["ef"])
    if D(data["resource_model"]["surge_start"]) <= wdr_ef <= D(data["resource_model"]["surge_end"]):
        errors.append("surge window must not include 24 Oct (last WDR day)")
    org = data["resource_model"].get("organic_names", [])
    if len(org) != proj["organic_crew"] or len(set(org)) != proj["organic_crew"]:
        errors.append("organic_names must be unique and equal organic_crew")
    crew_names = {n for row in data["resource_model"]["crews"] for n in row["crew"]}
    missing_org = [n for n in org if n not in crew_names]
    if missing_org:
        errors.append(f"organic_names missing from crews: {missing_org}")
    res_tex = ROOT / "sections" / "05_resource.tex"
    if res_tex.exists() and r"\input{sections/generated/s5_resource_build}" not in res_tex.read_text():
        errors.append("05_resource.tex must input the generated headcount-build table")
    s5 = GEN_DIR / "s5_resource_build.tex"
    if not s5.exists():
        errors.append("s5_resource_build.tex missing; run python3 scripts/plot_resource_figures.py")
    elif "tab:resource-build" not in s5.read_text():
        errors.append("s5_resource_build.tex missing table label")
    # Weeks 3-6: mitigated A-125 at ES--EF. Weeks 9-11: unmitigated A-125 at LS--LF.
    if not all(mit[i] > unmit[i] for i in range(2, 6)):
        errors.append("weeks 3-6 mitigated must exceed unmitigated (A-125 at ES--EF)")
    if not all(unmit[i] > mit[i] for i in range(8, 11)):
        errors.append("weeks 9-11 unmitigated must exceed mitigated (A-125 late bar)")
    lox = next(x for x in data["res_items"] if x["name"].startswith("LOX"))
    if lox["amount"] != round(0.18 * 68500):
        errors.append(f"LOX RES {lox['amount']} != 18% of $68,500")
    res_sum = sum(x["amount"] for x in data.get("res_items", []))
    if res_sum != proj["res_allowance"]:
        errors.append(f"res_items sum {res_sum} != res_allowance {proj['res_allowance']}")
    pct = round(100.0 * proj["contingency"] / proj["base_estimate"], 2)
    if abs(pct - proj.get("contingency_pct", pct)) > 0.011:
        errors.append(f"contingency_pct {proj.get('contingency_pct')} != {pct}")
    if abs(pct - 15.0) < 0.011:
        errors.append("contingency must not be a 15.00% plug")
    if data["evm_m4"]["pv"] != proj["pv_at_m4"]:
        errors.append("evm_m4.pv != project.pv_at_m4")

    evm = data["evm"]
    if evm["pm_doa_aud"] != 20000 or evm["pm_doa_hours"] != 48:
        errors.append("PM DoA must be $20,000 and 48 hours")
    if evm["t0_slip_trigger_days"] != 2:
        errors.append("T-0 slip trigger must be 2 days")
    if evm["measurement_0_100"] != ["A-132", "A-133", "A-141", "A-143"]:
        errors.append("0/100 list != [A-132, A-133, A-141, A-143]")
    if evm.get("measurement_percent") != ["A-113"]:
        errors.append("percent-complete list != [A-113]")
    if evm["measurement_milestone"] != ["A-123", "A-124"]:
        errors.append("milestone-percent list != [A-123, A-124]")
    if float(evm.get("a123_unsigned_hp1_pct", 1)) != 0.0:
        errors.append("unsigned HP-1 must earn 0% of A-123 (milestone 0/100)")
    a123_amt = next(r["amount"] for r in data["wbs_cost"] if r["wbs"] == "1.2.2")
    late_ev_want = data["evm_m4"]["pv"] - a123_amt
    if data["evm_m4"]["late_stack"]["ev"] != late_ev_want:
        errors.append(
            f"late-stack EV {data['evm_m4']['late_stack']['ev']} != PV − A-123 {late_ev_want}"
        )
    if data["evm_m4"]["late_stack"]["band"] != "Red":
        errors.append("unsigned HP-1 late stack must be Red")
    if data["hse"]["blast_zone_km"] != 1.5 or data["hse"]["acoustic_db"] != 135:
        errors.append("HSE blast zone / acoustic != 1.5 km / 135 dB")
    if data["hse"]["blast_zone_km"] and proj["hse_pad_cap"] != 12:
        errors.append("HSE pad cap != 12")

    for key, case in (("on_plan", data["evm_m4"]["on_plan"]), ("late_stack", data["evm_m4"]["late_stack"])):
        cpi = case["ev"] / case["ac"]
        spi = case["ev"] / data["evm_m4"]["pv"]
        if round(cpi + 1e-12, 2) != case["cpi"]:
            errors.append(f"{key} CPI {case['cpi']} != round(EV/AC,2)={round(cpi, 2)}")
        if round(spi + 1e-12, 2) != case["spi"]:
            errors.append(f"{key} SPI {case['spi']} != round(EV/PV,2)={round(spi, 2)}")
        eac = round(proj["base_estimate"] * case["ac"] / case["ev"])
        if case["eac_work"] != eac:
            errors.append(f"{key} eac_work {case['eac_work']} != AC×BAC_work/EV {eac}")
        ieac = round(proj["bac"] * case["ac"] / case["ev"])
        if case["ieac_bac"] != ieac:
            errors.append(f"{key} ieac_bac {case['ieac_bac']} != AC×BAC/EV {ieac}")

    hp_ids = [h["id"] for h in data["hold_points"]]
    if hp_ids != ["HP-1", "HP-2", "HP-3", "HP-4"]:
        errors.append(f"hold points {hp_ids} != HP-1..HP-4")
    for hp in data["hold_points"]:
        if "Ziyad" not in hp.get("release", ""):
            errors.append(f"{hp['id']} release must include Ziyad")
    hp4 = next(h for h in data["hold_points"] if h["id"] == "HP-4")
    for name in ("RSO", "Juru"):
        if name not in hp4["release"]:
            errors.append(f"HP-4 release must include {name}")
    if "payload" in hp4["release"].lower():
        errors.append("HP-4 release must not make the payload sponsor a signatory")
    if "HP-1 signed" not in data["evm_m4"]["planned_label"]:
        errors.append("evm_m4.planned_label must say HP-1 signed")
    if "A-113" not in data["evm_m4"]["planned_label"]:
        errors.append("evm_m4.planned_label must mention A-113 percent-complete")
    r12 = next(r for r in data["risks"] if r["id"] == "R-12")
    if r12["emv"] != 0 or r12["i"] != 5:
        errors.append("R-12 must be the in-flight TF1 row (I=5, site-ops EMV $0)")
    if r12["p_res"] != r12["p"]:
        errors.append("R-12 residual P must stay at inherent P (HP-3 does not treat post-T-0)")
    if "ASA" not in acts["A-113"]["name"]:
        errors.append("A-113 name must include ASA")
    if "LRU" in acts["A-134"]["name"]:
        errors.append("A-134 title must not say LRU")
    labour = data.get("labour", {})
    if labour:
        c10 = labour["c10_ordinary"]
        emp_pro = employment_oncost(labour, pad=False)
        emp_pad = employment_oncost(labour, pad=True)
        fee_keys = [k for k in labour if k.endswith("_fee")]
        if fee_keys:
            errors.append(f"labour still has a fee fudge: {fee_keys}")
        eng = (
            c10
            * emp_pro
            / labour["engineer_utilisation"]
            * labour["engineer_overhead"]
        )
        tech = (
            c10
            * emp_pad
            / labour["technician_utilisation"]
            * labour["technician_overhead"]
        )
        spec = (
            c10
            * emp_pro
            / labour["specialist_utilisation"]
            * labour["specialist_overhead"]
        )
        surge = (
            c10
            * labour["surge_overtime_factor"]
            * emp_pad
            / labour["technician_utilisation"]
            * labour["surge_overhead"]
        )
        if abs(eng - labour["engineer_pm"]) > 0.15:
            errors.append(f"engineer/PM stack {eng:.2f} != {labour['engineer_pm']}")
        if abs(tech - labour["technician"]) > 0.15:
            errors.append(f"technician stack {tech:.2f} != {labour['technician']}")
        if abs(spec - labour["specialist"]) > 0.15:
            errors.append(f"specialist stack {spec:.2f} != {labour['specialist']}")
        if abs(surge - labour["surge"]) > 0.15:
            errors.append(f"surge stack {surge:.2f} != {labour['surge']}")
        if labour["crane_lift_days"] + labour["crane_nonlift_days"] != 24:
            errors.append("crane lift + non-lift days must equal A-123 duration 24")
    cb = data.get("cost_build", {})
    if cb:
        if cb["wbs_113_asa"] + cb["wbs_113_casa"] + cb["wbs_113_gbrmpa"] != 88000:
            errors.append("1.1.3 split must sum to $88,000")
        if cb["gn2_cylinders"] * cb["gn2_unit_aud"] != 8000:
            errors.append("GN2 multiply-out must equal $8,000")
        if cb["cryo_hoses"] * cb["cryo_hose_aud"] + cb["cryo_seal_kit_aud"] != 6000:
            errors.append("cryo multiply-out must equal $6,000")
        opt_h = (
            cb["option_c_specialists"] * labour["specialist"]
            + cb["option_c_technicians"] * labour["technician"]
        )
        opt = opt_h * cb["option_c_hours_per_day"] * cb["option_c_days"]
        if abs(opt - data["project"]["option_c_cost"]) > 250:
            errors.append(f"Option C labour multiply-out {opt} != {data['project']['option_c_cost']}")
    if data["project"].get("pv_at_gate1") != 602301:
        errors.append("pv_at_gate1 must remain $602,301")
    r06 = next(r for r in data["risks"] if r["id"] == "R-06")
    if r06["emv"] != 0 or r06["i_dollar"] != 0:
        errors.append("R-06 must be schedule-only (weather $ live only in RES)")
    r08 = next(r for r in data["risks"] if r["id"] == "R-08")
    if r08["i_res"] != r08["i"] or r08["i"] != 4 or r08["emv"] != 0:
        errors.append("R-08 residual I must stay 4 with $0 transferred")
    a100 = acts["A-100"]
    if not a100.get("external_driver") or a100["critical"]:
        errors.append("A-100 must be an external $0 driver, not launch-critical")
    if data["executive"]["top_risks"] != ["R-01", "R-12", "R-14"]:
        errors.append("top risks must be R-01, R-12, R-14")
    if "A-141" in str(data["compression"]["option_c_tail"]) and expect_d["A-141"] != 5:
        errors.append("Option C must keep A-141 at 5 days")

    pct = sum(c["pct"] for c in data["contribution"])
    if abs(pct - 100.0) > 1e-6:
        errors.append(f"contribution {pct} != 100")
    hours = [c["hours"] for c in data["contribution"]]
    if len(hours) != 4 or len(set(hours)) != 1:
        errors.append("contribution hours must be four equalised values")
    for c in data["contribution"]:
        if abs(c["pct"] - 25.0) > 1e-6:
            errors.append(f"{c['name']} pct {c['pct']} != 25.0")

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
            if not re.search(rf"&\s*{a['d']}\s*&", line):
                errors.append(f"Table 3.1 {a['id']} duration != {a['d']}")
        if a["id"] == "A-100" and not re.search(r"&\s*Ext\s*\\\\", line):
            errors.append("Table 3.1 A-100 CP column must be Ext, not Y")
    for rid in RETIRED:
        if re.search(rf"\b{rid}\b", tex):
            errors.append(f"retired ID {rid} appears in 03_schedule.tex")
    return errors


def _aud(n: int) -> str:
    return f"{n:,}".replace(",", "{,}")


def check_section_7(data) -> list[str]:
    if not DELIVERY_TEX.exists():
        return ["sections/07_delivery.tex missing"]
    tex = DELIVERY_TEX.read_text()
    for p in sorted(GEN_DIR.glob("s7_*.tex")):
        tex += "\n" + p.read_text()
    errors: list[str] = []
    m4 = data["evm_m4"]
    proj = data["project"]
    evm = data["evm"]
    required = [
        _aud(m4["pv"]),
        _aud(m4["on_plan"]["ev"]),
        _aud(m4["on_plan"]["ac"]),
        _aud(m4["late_stack"]["ev"]),
        _aud(m4["late_stack"]["ac"]),
        _aud(m4["on_plan"]["eac_work"]),
        _aud(m4["on_plan"]["ieac_bac"]),
        _aud(m4["late_stack"]["eac_work"]),
        _aud(proj["base_estimate"]),
        _aud(proj["bac"]),
        _aud(proj["contingency"]),
        _aud(evm["pm_doa_aud"]),
        _aud(proj["option_c_cost"]),
        "campaign not yet executed",
        m4["planned_label"],
        "HP-1 signed",
        "0.96",
        "1.00",
        f"{m4['late_stack']['cpi']:.2f}",
        f"{m4['late_stack']['spi']:.2f}",
        m4["late_stack"]["band"],
        "HP-1",
        "HP-2",
        "HP-3",
        "HP-4",
        "evm_example.pdf",
        "1.5~km",
        "135~dB",
        "managing-contractor",
        "s7_holdpoints_table",
        "s7_evm_table",
        "s7_macros",
        "2.6",
        "4.4",
    ]
    for needle in required:
        if needle not in tex:
            errors.append(f"07_delivery.tex missing locked string: {needle}")
    for act in evm["measurement_0_100"] + evm["measurement_milestone"]:
        if act not in tex:
            errors.append(f"07_delivery.tex missing measurement activity {act}")
    for rid in RETIRED:
        if re.search(rf"\b{rid}\b", tex):
            errors.append(f"retired ID {rid} appears in 07_delivery.tex")
    if "70 percent" in tex.lower() or "70~percent" in tex:
        errors.append("late-stack EVM must not mix 70% hours with milestone 0/100")
    if "SV > -5" in tex or r"$SV > -5" in tex:
        errors.append("do not write SV in days")
    if "every cost-bearing EMV" in tex:
        errors.append("DoA comparison must not call dollar impacts EMVs")
    if "remaining A-113 permit hours" in tex and "0/100" in tex.split("remaining A-113")[0][-400:]:
        errors.append("do not explain the M-4 EV-PV gap as 0/100 on A-113")
    unesc = tex.replace("\\&", "&")
    for hp in data["hold_points"]:
        if hp["release"] not in unesc:
            errors.append(f"{hp['id']} release {hp['release']!r} missing from Section 7")
    return errors


def _load_exporter(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ref_before(tex: str, label: str, needle: str) -> bool:
    ref = tex.find(rf"\ref{{{label}}}")
    at = tex.find(needle)
    return ref >= 0 and at >= 0 and ref < at


def check_section_2(data) -> list[str]:
    if not OVERVIEW_TEX.exists():
        return ["sections/02_overview.tex missing"]
    tex = OVERVIEW_TEX.read_text()
    wbs = WBS_TEX.read_text() if WBS_TEX.exists() else ""
    gen = ""
    p = GEN_DIR / "s2_change_table.tex"
    if p.exists():
        gen = p.read_text()
    blob = tex + "\n" + wbs + "\n" + gen
    errors: list[str] = []
    required = [
        rf"Deliver launch-site operations within the \${_aud(data['project']['base_estimate'])} AUD base estimate",
        rf"authorised \${_aud(data['project']['contingency'])} AUD contingency",
        rf"\${_aud(data['project']['bac'])}",
        "15~October~2026",
        "20~November",
        "Manage Closely",
        "stop-work",
        "s2_change_table",
        "sections/02_wbs",
        "tab:charter-pep",
        "fig:wbs",
        "dougherty2026",
        "gilmour2025",
        "asa2025",
        "smith2025",
        "gbrmpa2019",
        "pmi2021",
        "kerzner2017",
        r"five-second",
        "gates static fire",
        r"organic crew eight",
        "98.5",
        "four first-stage",
        "notice to proceed",
        "Week~8",
        "Objectives~4",
        "LRR attendees",
    ]
    for needle in required:
        if needle not in blob:
            errors.append(f"02_overview.tex missing locked string: {needle}")
    if not _ref_before(tex, "tab:charter-pep", r"\input{sections/generated/s2_change_table}"):
        errors.append("Table 2.1 must be referred to before it is input")
    if not _ref_before(tex + "\n" + wbs, "fig:wbs", r"\begin{figure}"):
        errors.append("Figure 2.1 must be referred to before the WBS TikZ figure")
    for rid in RETIRED:
        if re.search(rf"\b{rid}\b", blob):
            errors.append(f"retired ID {rid} appears in Section 2")
    for needle in (
        _aud(data["project"]["base_estimate"]),
        _aud(data["project"]["contingency"]),
        _aud(data["project"]["emv_sum"]),
        "15~Oct~2026",
        "20~Nov~2026",
        "24~Oct",
        "25~Oct",
        "18 campaign-specific risks",
        "Embedded monitors with stop-work authority",
        "Objective 4 is",
        "Week 8 workshop",
        "Payload sponsor remains a witness",
        "residual EMV",
        "Payload operations remain",
        "stability loss",
        "Next Spaceflight",
        "weekly integration logs",
        "QLD Regional Press",
        "10 seconds before simulated",
        "Stakeholder",
        "40/30/30",
        "Charter has no NTP",
        "Gate~1 PV",
    ):
        if needle not in gen:
            errors.append(f"s2_change_table.tex missing locked A3 cell: {needle}")
    main = MAIN_TEX.read_text() if MAIN_TEX.exists() else ""
    if r"\input{sections/02_overview}" not in main:
        errors.append("A3.tex must input sections/02_overview")
    if r"\section{Refined project overview}" in main:
        errors.append("A3.tex still has empty Section 2 stubs")
    return errors


def check_section_8(data) -> list[str]:
    if not INTEGRATION_TEX.exists():
        return ["sections/08_integration.tex missing"]
    tex = INTEGRATION_TEX.read_text()
    main = MAIN_TEX.read_text() if MAIN_TEX.exists() else ""
    gen = ""
    for name in ("s8_reconcile_table.tex", "s8_contribution_table.tex"):
        p = GEN_DIR / name
        if p.exists():
            gen += "\n" + p.read_text()
    blob = tex + "\n" + main + "\n" + gen
    errors: list[str] = []
    proj = data["project"]
    hours = data["contribution"][0]["hours"]
    required = [
        _aud(proj["base_estimate"]),
        _aud(proj["contingency"]),
        _aud(proj["emv_sum"]),
        _aud(proj["res_allowance"]),
        _aud(proj["bac"]),
        _aud(proj["surge_hire_cost"]),
        _aud(proj["option_c_cost"]),
        "Buddycheck",
        "12~hours",
        f"{hours}~hours",
        "25.0",
        "100.0",
        "tab:reconcile",
        "s8_reconcile_table",
        "s8_contribution_table",
        "tab:contribution",
        "app:contribution",
        "Signature:",
        "one campaign",
        r"$SV$ is currency",
        "dougherty2026",
        "fleming2016",
        "iso31000",
    ]
    for needle in required:
        if needle not in blob:
            errors.append(f"Section 8 / appendix missing locked string: {needle}")
    if not _ref_before(tex, "tab:reconcile", r"\input{sections/generated/s8_reconcile_table}"):
        errors.append("Table 8.1 must be referred to before it is input")
    for rid in RETIRED:
        if re.search(rf"\b{rid}\b", blob):
            errors.append(f"retired ID {rid} appears in Section 8")
    if r"\input{sections/08_integration}" not in main:
        errors.append("A3.tex must input sections/08_integration")
    if r"\section{Integration and professionalism}" in main:
        errors.append("A3.tex still has empty Section 8 stubs")
    for c in data["contribution"]:
        if c["id"] not in main:
            errors.append(f"title/appendix missing student id {c['id']}")
    return errors


def check_section_1(data: dict) -> list[str]:
    """Board-ready executive: locked money, dates, top three risks, verbatim recommendation."""
    if not EXEC_TEX.exists():
        return ["sections/01_exec.tex missing"]
    macros_path = GEN_DIR / "s1_macros.tex"
    if not macros_path.exists():
        return ["sections/generated/s1_macros.tex missing; run python3 scripts/export_section1.py"]

    errors: list[str] = []
    exec_tex = EXEC_TEX.read_text()
    rec_tex = macros_path.read_text()
    a3 = MAIN_TEX.read_text() if MAIN_TEX.exists() else ""
    proj = data["project"]

    required = [
        "launch-site operations",
        "managing-contractor",
        "five-second",
        "gilmour2025",
        "pad occupancy cap of twelve",
        "organic crew is eight",
        r"\PEPrOiBoard",
        r"\PEPrIxBoard",
        r"\PEPrXivBoard",
        r"\textit{\PEPrecommendation}",
        r"\input{sections/generated/s1_macros}",
    ]
    for needle in required:
        if needle not in exec_tex:
            errors.append(f"Section 1 missing {needle!r}")

    if r"\input{sections/01_exec}" not in a3:
        errors.append("A3.tex does not input sections/01_exec")
    if r"\section{Executive summary}" in a3:
        errors.append("A3.tex still contains an inline Executive summary heading")

    blob1 = exec_tex + "\n" + rec_tex
    money_needles = [
        _aud(proj["base_estimate"]),
        _aud(proj["contingency"]),
        _aud(proj["emv_sum"]),
        _aud(proj["res_allowance"]),
        _aud(proj["bac"]),
        _aud(proj["option_c_cost"]),
        _aud(proj.get("pv_at_gate1", 0)),
        "15~October~2026",
        "24~October",
        "30~October~2026",
        "10~November~2026",
        "15~November~2026",
        "20~November~2026",
        "1~December~2026",
    ]
    for needle in money_needles:
        if needle not in blob1:
            errors.append(f"Section 1 missing locked figure {needle!r}")

    for rid in data.get("executive", {}).get("top_risks", ["R-01", "R-09", "R-14"]):
        if rid not in exec_tex:
            errors.append(f"Section 1 missing top risk {rid}")
        if rid not in rec_tex:
            errors.append(f"s1_macros missing {rid}")

    if "It is recommended that the Executive Board approve this Project Execution Plan" not in rec_tex:
        errors.append("Recommendation prefix is not the locked board sentence")
    if _aud(proj["bac"]) not in rec_tex:
        errors.append("Recommendation BAC does not match YAML")
    if _aud(proj["contingency"]) not in rec_tex:
        errors.append("Recommendation contingency does not match YAML")
    if _aud(proj.get("pv_at_gate1", 0)) not in rec_tex:
        errors.append("Recommendation must disclose Gate 1 planned PV")
    return errors


def check_section_4(data: dict) -> list[str]:
    path = ROOT / "sections" / "04_cost.tex"
    if not path.exists():
        return ["sections/04_cost.tex missing"]
    tex = path.read_text()
    errors: list[str] = []
    proj = data["project"]
    for needle in (
        _aud(proj["base_estimate"]),
        _aud(proj["contingency"]),
        _aud(proj["emv_sum"]),
        _aud(proj["res_allowance"]),
        _aud(proj["bac"]),
        "residual",
        "1.378",
        "1.405",
        "602{,}301",
    ):
        if needle not in tex:
            errors.append(f"Section 4 missing locked string: {needle}")
    if "and a fee" in tex or re.search(r"1\.\d{4}", tex):
        errors.append("Section 4 still describes a labour fee or four-decimal factor")
    if "5.09" in tex or "3.23" in tex:
        errors.append("Section 4: reverse-engineered 5.09/3.23 labour multiplier still present")
    if "175{,}500" in tex or "218{,}630" in tex or "1{,}718{,}630" in tex:
        errors.append("Section 4 still quotes inherent-EMV contingency totals")
    return errors


def check_section_6(data: dict) -> list[str]:
    path = ROOT / "sections" / "06_risk.tex"
    if not path.exists():
        return ["sections/06_risk.tex missing"]
    tex = path.read_text()
    errors: list[str] = []
    proj = data["project"]
    for needle in (
        _aud(proj["contingency"]),
        _aud(proj["emv_sum"]),
        _aud(proj["res_allowance"]),
        "0.03\\times90{,}000",
        "2{,}700",
        _aud(proj["emv_sum"]),
    ):
        if needle not in tex:
            errors.append(f"Section 6 missing locked string: {needle}")
    if "Cause $\\rightarrow$ event $\\rightarrow$ effect" in tex or "Cause $\\to$ event $\\to$ effect" in tex:
        errors.append("Table 6.1 still jams cause, event and effect in one cell")
    if "Cause & Event & Effect" not in tex:
        errors.append("Table 6.1 must split Cause, Event and Effect")
    r08_line = next((ln for ln in tex.splitlines() if ln.startswith("R-08")), "")
    if r08_line and not re.search(r"&\s*1\s*&\s*4\s*&", r08_line):
        errors.append("R-08 residual I must stay 4 in Table 6.1")
    if "EMV remains \\$27,000" in tex or "EMV remains $27,000" in tex:
        errors.append("Section 6 still quotes inherent EMV for R-01 as the pool")
    if "175{,}500" in tex:
        errors.append("Section 6 still quotes inherent EMV $175,500")
    return errors


def check_all_tex(data: dict) -> list[str]:
    """Whole-plan scan: no retired WBS ids, no SV-in-days, no stale money."""
    del data
    errors: list[str] = []
    blobs = [p.read_text() for p in sorted((ROOT / "sections").rglob("*.tex"))]
    if MAIN_TEX.exists():
        blobs.append(MAIN_TEX.read_text())
    all_tex = "\n".join(blobs)
    for wid in sorted(RETIRED):
        if re.search(rf"\b{wid}\b", all_tex):
            errors.append(f"retired WBS id {wid} still appears in the plan")
    if "SV > -5" in all_tex:
        errors.append("SV threshold still written as days")
    for stale in (
        "175{,}500",
        "218{,}630",
        "1{,}718{,}630",
        "14.58",
        "5.09",
        "3.23",
        "81{,}050",
        "37{,}920",
        "1{,}581{,}050",
        "1{,}645{,}751",
        "2{,}124{,}089",
        "fwo2020",
    ):
        if stale in all_tex:
            errors.append(f"stale identity {stale} still appears in the plan")
    if "A-142 4~$\\to$~2" in all_tex or "A-142 4~$\\to$~2~d" in all_tex:
        errors.append("Option C still crashes A-142")
    if "engineer_fee" in all_tex:
        errors.append("labour fee key still appears in the plan")
    return errors


def main() -> int:
    data = load()
    export_section1 = _load_exporter("export_section1")
    export_section2 = _load_exporter("export_section2")
    export_section7 = _load_exporter("export_section7")
    export_section8 = _load_exporter("export_section8")
    errors = (
        check(data)
        + check_table_31(data)
        + export_section1.check(data)
        + export_section2.check(data)
        + export_section7.check(data)
        + export_section8.check(data)
        + check_section_1(data)
        + check_section_2(data)
        + check_section_4(data)
        + check_section_6(data)
        + check_section_7(data)
        + check_section_8(data)
        + check_all_tex(data)
    )
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS  pep_baseline.yaml identities hold")
    print("      Table 3.1 dates/durations match YAML")
    print("      Section 1 recommendation / top risks generated from YAML")
    print("      Table 2.1 A3 cells generated from YAML")
    print("      Table 8.1 / contribution hours generated from YAML")
    print("      Section 7 DoA / EVM / hold-point numbers match YAML")
    print("      A-125 is an FS predecessor of A-133")
    print("      R-12 is the in-flight TF1 row (EMV $0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
