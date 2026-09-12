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

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "pep_baseline.yaml"
TEX_PATH = ROOT / "sections" / "03_schedule.tex"
OVERVIEW_TEX = ROOT / "sections" / "02_overview.tex"
WBS_TEX = ROOT / "sections" / "02_wbs.tex"
DELIVERY_TEX = ROOT / "sections" / "07_delivery.tex"
INTEGRATION_TEX = ROOT / "sections" / "08_integration.tex"
MAIN_TEX = ROOT / "A3.tex"
GEN_DIR = ROOT / "sections" / "generated"

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

    evm = data["evm"]
    if evm["pm_doa_aud"] != 20000 or evm["pm_doa_hours"] != 48:
        errors.append("PM DoA must be $20,000 and 48 hours")
    if evm["t0_slip_trigger_days"] != 2:
        errors.append("T-0 slip trigger must be 2 days")
    if evm["measurement_0_100"] != ["A-113", "A-132", "A-133", "A-141", "A-143"]:
        errors.append("0/100 list != [A-113, A-132, A-133, A-141, A-143]")
    if evm["measurement_milestone"] != ["A-123", "A-124"]:
        errors.append("milestone-percent list != [A-123, A-124]")
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
        eac = case["ac"] + (proj["base_estimate"] - case["ev"]) / case["cpi"]
        if abs(eac - case["eac_work"]) > 0.51:
            errors.append(f"{key} eac_work {case['eac_work']} != {eac:.1f}")
        ieac = proj["bac"] / case["cpi"]
        if abs(ieac - case["ieac_bac"]) > 0.51:
            errors.append(f"{key} ieac_bac {case['ieac_bac']} != {ieac:.1f}")

    hp_ids = [h["id"] for h in data["hold_points"]]
    if hp_ids != ["HP-1", "HP-2", "HP-3", "HP-4"]:
        errors.append(f"hold points {hp_ids} != HP-1..HP-4")
    for hp in data["hold_points"]:
        if "Ziyad" not in hp.get("release", ""):
            errors.append(f"{hp['id']} release must include Ziyad")
    if "stacking 0/100 complete, GSE HP-2 complete" not in data["evm_m4"]["planned_label"]:
        errors.append("evm_m4.planned_label must keep locked stacking 0/100 + HP-2 wording")

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
            # duration is the first numeric column after the name
            if not re.search(rf"&\s*{a['d']}\s*&", line):
                errors.append(f"Table 3.1 {a['id']} duration != {a['d']}")
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
        "stacking 0/100 complete, GSE HP-2 complete",
        "0.96",
        "0.98",
        "0.92",
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
    if re.search(r"week(?:s)?\s+(1|14)\b", tex, re.I):
        errors.append("07_delivery.tex looks like a fake weekly EV history")
    if "SV > -5" in tex or r"$SV > -5" in tex:
        errors.append("do not write SV in days")
    if "every cost-bearing EMV" in tex:
        errors.append("DoA comparison must not call dollar impacts EMVs")
    if "HP-1 / HP-2 complete" in tex:
        errors.append("planned M-4 row must not mark HP-1 complete")
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
        r"Deliver launch-site operations within the \$1{,}500{,}000 AUD base estimate",
        r"authorised \$225{,}000 AUD contingency",
        r"\$1{,}725{,}000",
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
        "gbrmpa2019",
        "pmi2021",
        "kerzner2017",
        r"five-second",
        "gates static fire",
        r"organic crew eight",
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


def main() -> int:
    data = load()
    export_section2 = _load_exporter("export_section2")
    export_section7 = _load_exporter("export_section7")
    export_section8 = _load_exporter("export_section8")
    errors = (
        check(data)
        + check_table_31(data)
        + export_section2.check(data)
        + export_section7.check(data)
        + export_section8.check(data)
        + check_section_2(data)
        + check_section_7(data)
        + check_section_8(data)
    )
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS  pep_baseline.yaml identities hold")
    print("      Table 3.1 dates/durations match YAML")
    print("      Table 2.1 A3 cells generated from YAML")
    print("      Table 8.1 / contribution hours generated from YAML")
    print("      Section 7 DoA / EVM / hold-point numbers match YAML")
    print("      A-125 LF is imposed before A-133 (not project finish)")
    print("      R-12 EMV is 0 by design (Option C not double-counted)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
