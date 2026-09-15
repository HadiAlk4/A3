#!/usr/bin/env python3
"""Write Section 8 LaTeX fragments from data/pep_baseline.yaml.

Table 8.1 is the golden-thread reconciliation. Contribution hours and
percentages are the same records as the title page.

    python3 scripts/export_section8.py
"""
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "pep_baseline.yaml"
OUT = ROOT / "sections" / "generated"


def D(s) -> date:
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, date):
        return s
    return date.fromisoformat(str(s))


def load():
    with YAML_PATH.open() as f:
        return yaml.safe_load(f)


def aud(n) -> str:
    return f"\\${int(round(n)):,}".replace(",", "{,}")


def aud_plain(n) -> str:
    return f"{int(round(n)):,}".replace(",", "{,}")


def day_mon_year(d) -> str:
    d = D(d)
    return f"{d.day}~{d.strftime('%b')}~{d.year}"


def tex_escape(s: str) -> str:
    return s.replace("&", "\\&").replace("%", "\\%")


def reconcile_table(data: dict) -> str:
    proj = data["project"]
    miles = data["milestones"]
    contrib = data["contribution"]
    pct = sum(c["pct"] for c in contrib)
    hours = sum(c["hours"] for c in contrib)
    n = len(contrib)
    colspec = (
        r"@{}>{\raggedright\arraybackslash}p{2.55cm}"
        r" >{\raggedright\arraybackslash}p{4.55cm}"
        r" X@{}"
    )
    rows = [
        (
            f"Work PMB & {aud(proj['base_estimate'])} & "
            f"Sec.~\\ref{{sec:exec}}; Sec.~\\ref{{sec:overview-objectives}}; "
            f"Table~\\ref{{tab:wbs-cost}}; "
            f"Table~\\ref{{tab:cashflow}} (ends here); Fig.~\\ref{{fig:scurve}}; "
            f"Sec.~\\ref{{sec:delivery-evm}} distributed $PV$ \\\\"
        ),
        (
            f"Contingency & {aud(proj['contingency'])} $=$ "
            f"EMV {aud(proj['emv_sum'])} $+$ RES {aud(proj['res_allowance'])} & "
            f"Table~\\ref{{tab:contingency}}; Table~\\ref{{tab:risk-register}} "
            f"dollar column; {proj['contingency_pct']:.2f}\\% of base, not a 15\\% markup \\\\"
        ),
        (
            f"Authorised $BAC$ & {aud(proj['bac'])} & "
            f"Finish-line $AC \\le BAC$ in Sec.~\\ref{{sec:exec}}, "
            f"Sec.~\\ref{{sec:overview-objectives}} "
            f"and Sec.~\\ref{{sec:delivery-evm}} \\\\"
        ),
        (
            f"M-4 stacking & {day_mon_year(miles['M4']['date'])} $=$ A-123 $EF$ & "
            f"Table~\\ref{{tab:charter-pep}}; Table~\\ref{{tab:precedence}}; "
            f"Fig.~\\ref{{fig:gantt_chart}}; Fig.~\\ref{{fig:evm}} status date \\\\"
        ),
        (
            f"M-5 static fire & {day_mon_year(miles['M5']['date'])} $=$ A-133 $EF$ & "
            f"Cold WDR A-132 then hot fire A-133; HP-3 on A-133 \\\\"
        ),
        (
            f"M-6 LRR & {day_mon_year(miles['M6']['date'])} $=$ A-141 $EF$ & "
            f"LRR waits on A-134, not on A-133; HP-4 \\\\"
        ),
        (
            f"M-7 $T$-0 & {day_mon_year(miles['M7']['date'])} $=$ A-143 $EF$ & "
            f"Baseline (Sec.~\\ref{{sec:exec}}). Option~C {day_mon_year(data['compression']['option_c_t0'])} "
            f"is contingent only; not redrawn on Fig.~\\ref{{fig:gantt_chart}} \\\\"
        ),
        (
            f"M-8 handover & {day_mon_year(miles['M8']['date'])} $=$ A-144 $EF$ & "
            f"Five days after M-7; Table~\\ref{{tab:charter-pep}} closes the 22~Nov collision \\\\"
        ),
        (
            f"Pad occupancy & {proj['organic_crew']} org.\\ / {proj['hse_pad_cap']} cap / "
            f"{proj['unmitigated_peak']} unmit.\\ / {proj['mitigated_peak']} mit.\\ "
            f"(simultaneous unique heads) & "
            f"Fig.~\\ref{{fig:resources}}; Table~\\ref{{tab:resource-build}}; R-13; "
            f"Sec.~\\ref{{sec:delivery-hse}} \\\\"
        ),
        (
            f"Surge labour & {aud(proj['surge_hire_cost'])} $=$ $4 \\times 7$~d "
            f"$\\times$ 8~h $\\times$ \\$100 inside WBS~1.3.3 "
            f"(24--30~Oct only) & "
            f"In the {aud(proj['base_estimate'])} base, not a contingency draw \\\\"
        ),
        (
            f"EMV pool & residual $P'\\%$ $\\times$ $I_{{\\$}}$ $=$ {aud(proj['emv_sum'])} "
            f"(not inherent $P\\%$) & "
            f"Table~\\ref{{tab:contingency}}; Table~\\ref{{tab:risk-register}} EMV column \\\\"
        ),
        (
            "HP-4 & Launch Director / RSO / Juru Officer / Abdul / Ziyad; "
            "payload sponsor witnesses & "
            "Table~\\ref{tab:holdpoints}; Table~\\ref{tab:raci} 1.4.1; A1 M-6 \\\\"
        ),
        (
            f"Option~C & {aud(proj['option_c_cost'])} from contingency if R-14 fires & "
            f"Not in Table~\\ref{{tab:cashflow}}; Board draw under the "
            f"Sec.~\\ref{{sec:delivery-governance}} DoA \\\\"
        ),
        (
            f"Contribution & {contrib[0]['pct']:.1f}\\% $\\times$ {n} $=$ {pct:.1f}\\% "
            f"({hours}~h equalised) & Title page; Table~\\ref{{tab:contribution}} \\\\"
        ),
    ]
    return (
        "% Generated by scripts/export_section8.py — do not edit by hand.\n"
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\small\n"
        "\\setlength{\\tabcolsep}{3.8pt}\n"
        "\\renewcommand{\\arraystretch}{1.18}\n"
        "\\caption[Golden-thread reconciliation]{Golden-thread reconciliation. Every view in this PEP is required to "
        "show the value in the middle column; the right-hand column is where the "
        "marker should look.}\n"
        "\\label{tab:reconcile}\n"
        f"\\begin{{tabularx}}{{\\textwidth}}{{{colspec}}}\n"
        "\\toprule\n"
        "Thread & Locked value & Views that must agree \\\\\n"
        "\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n"
        "\\end{tabularx}\n"
        "\\end{table}\n"
    )


def contribution_table(data: dict) -> str:
    rows = []
    for c in data["contribution"]:
        rows.append(
            f"{tex_escape(c['name'])} ({c['id']}) & {c['hours']} & "
            f"{tex_escape(c['deliverables'])} & {c['pct']:.1f} \\\\"
        )
    total_h = sum(c["hours"] for c in data["contribution"])
    total_p = sum(c["pct"] for c in data["contribution"])
    colspec = r"@{}>{\raggedright\arraybackslash}p{0.30\textwidth} r X r@{}"
    return (
        "% Generated by scripts/export_section8.py — do not edit by hand.\n"
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\renewcommand{\\arraystretch}{1.3}\n"
        "\\caption[Agreed contribution]{Agreed contribution after hours equalisation. Each member "
        f"{data['contribution'][0]['hours']}~h; percentages match the title page and sum to "
        f"{total_p:.1f}\\%.}}\n"
        "\\label{tab:contribution}\n"
        f"\\begin{{tabularx}}{{\\textwidth}}{{{colspec}}}\n"
        "\\toprule\n"
        "\\textbf{Team member} & \\textbf{Hours} & \\textbf{Primary deliverables} & \\textbf{\\%} \\\\\n"
        "\\midrule\n"
        + "\n".join(rows)
        + "\n\\midrule\n"
        f"\\textbf{{Total}} & \\textbf{{{total_h}}} & & \\textbf{{{total_p:.1f}}} \\\\\n"
        "\\bottomrule\n"
        "\\end{tabularx}\n"
        "\\end{table}\n"
    )


def render(data) -> dict[str, str]:
    return {
        str(OUT / "s8_reconcile_table.tex"): reconcile_table(data),
        str(OUT / "s8_contribution_table.tex"): contribution_table(data),
    }


def write(data=None) -> None:
    data = data or load()
    OUT.mkdir(parents=True, exist_ok=True)
    for path, content in render(data).items():
        Path(path).write_text(content)
        print("wrote", path)


def check(data=None) -> list[str]:
    data = data or load()
    errors = []
    hours = [c["hours"] for c in data["contribution"]]
    if len(set(hours)) != 1:
        errors.append("contribution hours are not equalised")
    if abs(sum(c["pct"] for c in data["contribution"]) - 100.0) > 1e-6:
        errors.append("contribution pct != 100")
    for path, content in render(data).items():
        p = Path(path)
        if not p.exists():
            errors.append(f"{p} missing; run python3 scripts/export_section8.py")
            continue
        if p.read_text() != content:
            errors.append(f"{p} stale versus YAML; run python3 scripts/export_section8.py")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = load()
    if args.check:
        errors = check(data)
        if errors:
            print("FAIL")
            for e in errors:
                print(" -", e)
            return 1
        print("PASS  generated Section 8 fragments match YAML")
        return 0
    write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
