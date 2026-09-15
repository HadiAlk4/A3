#!/usr/bin/env python3
"""Simultaneous pad occupancy from activity × named crew.

Mitigated A-125 uses ES--EF. Unmitigated A-125 uses LS--LF (the late bar).
Surge is four named heads on the seven-day static-fire window only.
Unmitigated overtime is four named heads on WDR + static fire only.
Daily occupancy is the unique-head union; weekly demand is the max day in the week.
Week 1 starts on the campaign start date. Weeks continue through finish (week 17).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


def D(s) -> date:
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, date):
        return s
    return date.fromisoformat(str(s)[:10])


def campaign_weeks(start: date, finish: date) -> list[tuple[int, date, date]]:
    weeks = []
    w = 1
    ws = start
    while ws <= finish:
        we = ws + timedelta(days=6)
        weeks.append((w, ws, we))
        w += 1
        ws = we + timedelta(days=1)
    return weeks


def _crew_map(model: dict) -> dict[str, list[str]]:
    return {row["id"]: list(row["crew"]) for row in model["crews"]}


def _in_span(day: date, es: date, ef: date) -> bool:
    return es <= day <= ef


def live_people(data: dict, day: date, *, mitigated: bool) -> dict[str, Any]:
    model = data["resource_model"]
    crews = _crew_map(model)
    acts = {a["id"]: a for a in data["activities"]}
    people: set[str] = set()
    activities: list[str] = []
    for aid, a in acts.items():
        if aid not in crews:
            continue
        if aid == "A-125" and not mitigated:
            es, ef = D(a["ls"]), D(a["lf"])
        else:
            es, ef = D(a["es"]), D(a["ef"])
        if _in_span(day, es, ef) and crews[aid]:
            people.update(crews[aid])
            activities.append(aid)
    rf_set = set(model["rf"])
    surge_set = set(model["surge"])
    ot_set = set(model["overtime"])
    rf_n = len(people & rf_set)
    surge_n = 0
    ot_n = 0
    if mitigated and D(model["surge_start"]) <= day <= D(model["surge_end"]):
        people.update(surge_set)
        surge_n = len(surge_set)
    if not mitigated and D(model["overtime_start"]) <= day <= D(model["overtime_end"]):
        people.update(ot_set)
        ot_n = len(ot_set)
    total = len(people)
    base = total - rf_n - surge_n - ot_n
    return {
        "total": total,
        "base": base,
        "rf": rf_n,
        "surge": surge_n,
        "ot": ot_n,
        "activities": activities,
        "people": sorted(people),
    }


def weekly_peaks(data: dict, *, mitigated: bool) -> list[dict[str, Any]]:
    start = D(data["project"]["start"])
    finish = D(data["project"]["finish"])
    rows = []
    for w, ws, we in campaign_weeks(start, finish):
        best = None
        day = ws
        while day <= we:
            if start <= day <= finish:
                occ = live_people(data, day, mitigated=mitigated)
                if best is None or occ["total"] > best["total"]:
                    best = {**occ, "day": day}
            day += timedelta(days=1)
        assert best is not None
        rows.append({"week": w, "ws": ws, "we": we, **best})
    return rows


def demand_series(data: dict) -> tuple[list[int], list[int]]:
    mit = [r["total"] for r in weekly_peaks(data, mitigated=True)]
    unmit = [r["total"] for r in weekly_peaks(data, mitigated=False)]
    return mit, unmit


def surge_days(model: dict) -> int:
    return (D(model["surge_end"]) - D(model["surge_start"])).days + 1
