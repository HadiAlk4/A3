# 3004ENG Assessment 3: Figure pipeline

**Project:** Eris TestFlight2 Launch Site Operations Campaign  
**Data:** `data/pep_baseline.yaml` (identical to the locked tables in `requirements.md`)  
**Outputs:** `figures/*.pdf` (vector)  
**Rule:** Scripts and TikZ must **load YAML**. If a number is not in the YAML, it does not belong on a figure.

---

## 1. Tool split

| Tool | Use for | Do not use for |
| :--- | :--- | :--- |
| **LaTeX / TikZ** | WBS tree, PERT node network, governance org chart, all numbered tables | S-curves, histograms, heatmaps, Gantt |
| **Python (Matplotlib + NumPy)** | Gantt, compression comparison, cash-flow S-curve, resource histogram, 5×5 risk matrix, EVM worked-example panel | PERT boxes (NetworkX node graphs look like software diagrams, not a board PEP) |
| **LaTeX `tabular`** | Tables 3.1, 3.2, 4.1, 4.2, 4.3, 5.1, 6.1 | Recreating those tables as images |

Palette (all Matplotlib figures):

| Role | Hex | Use |
| :--- | :--- | :--- |
| Navy | `#0B2545` | Non-critical bars, PV, base lines |
| Crimson | `#C0392B` | Launch-critical path, Red band, over-allocation |
| Teal | `#2A9D8F` | EV, mitigated demand, residual-safe zone |
| Amber | `#E76F51` | Amber band, Option C, medium risk |
| Grey | `#E0E0E0` | Grid |

Save with `bbox_inches='tight'` to `figures/`. Captions must state what the figure **proves**, then the body cites `\ref{...}` **before** the float.

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.95\textwidth]{figures/filename.pdf}
  \caption{...}
  \label{fig:sec_name}
\end{figure}
```

TikZ figures live in `figures/tikz/` (or inline in `A3.tex`) and must read the same IDs, dates, and $TF$ values as Table 3.1.

---

## 2. Figure register

### Figure 2.1 — WBS tree (TikZ)

* **File:** `figures/wbs_tree.pdf` (or TikZ inline)
* **Section:** 2
* **Proves:** 100% rule; every Level-3 code in Table 4.1 exists here and nowhere else.
* **Content:** Root `1.0` → `1.1` … `1.4` → all 17 Level-3 packages named exactly as in `requirements.md`. A-100 is **not** a WBS box (annotate off to the side: “external $0 receipt window”).
* **Do not:** Invent 1.2.5 or collapse 1.4.4/1.4.5.

---

### Figure 3.1 — Activity precedence network (TikZ)

* **File:** `figures/network_logic.pdf`
* **Section:** 3.1
* **Proves:** Dual $TF=0$ merge at A-133 (vehicle path and permit path) and LRR **after** diagnostics.
* **Nodes:** Every row in Table 3.1. Standard seven-field box:

  ```
  ES | ID | EF
  LS | D  | LF
         TF
  ```

* **Layout (left → right swimlanes, not a force-directed tangle):**
  1. Permitting / heritage: A-113, A-114, A-111, A-112
  2. Vehicle / stack: A-100, A-121, A-122, A-123
  3. GSE / RF / avionics: A-124, A-125, A-131
  4. Test / launch / close: A-132 … A-145
* **Arrows:** FS links from YAML `predecessors`. Crimson + 1.4 pt for $TF=0$ launch-critical links. Navy 0.6 pt otherwise. A-111 outline navy with an M-2 diamond (constrained, not launch-critical).
* **Must show:** `A-134 → A-141` (LRR does not start from A-133). `A-113 → A-133` and `A-123 → A-132 → A-133`.
* **Do not:** Use NetworkX spring_layout. Do not drop A-113. Do not colour A-125 or A-124 crimson.

---

### Figure 3.2 — Master Gantt (Matplotlib)

* **File:** `figures/gantt_chart.pdf`
* **Section:** 3.2
* **Proves:** The same $ES/EF$ as Table 3.1, with launch-critical bars distinct from float bars.
* **Bars:** One row per activity, YAML `es`–`ef`. Crimson if `critical: true`. Navy otherwise. Optional thin teal float whisker from $EF$ to $LF$ on non-critical rows (makes float visible).
* **Markers (vertical dashed):** M-4 15 Oct, M-5 30 Oct, M-6 10 Nov, M-7 15 Nov, M-8 20 Nov, M-9 1 Dec. M-2 2 Oct as a smaller navy marker on A-111.
* **Axis:** 10 Aug 2026 → 1 Dec 2026. Week ticks. Do not start the axis in September (that hides A-100/A-113).
* **Do not:** Hardcode A-101…A-110. Those IDs are retired. Do not mark A-111 as launch-critical. Do not draw Option C on this baseline Gantt (that is Figure 3.3).

---

### Figure 3.3 — Compression comparison (Matplotlib)

* **File:** `figures/compression_tradeoff.pdf`
* **Section:** 3.3
* **Proves:** Only Option C is an acceptable 5-day pull-in, and it costs $4,200/day rather than $8,000/day.
* **Why not a “curve” of three points at x = 5:** that is a vertical line, not a trade-off. Use a **grouped bar** (or two panels):
  * Panel A: added cost ($) for A, B, C.
  * Panel B: qualitative residual-risk rank (High / High / Medium) or a 1–5 risk score from YAML.
  * Annotate each: days saved = 5; verdict Rejected / Rejected / Contingent.
* **Optional overlay:** a small Gantt snippet of the **post-A-133 tail** under Option C (A-134 31 Oct–2 Nov, A-141 3–5 Nov, A-142 6–9 Nov, A-143 **10 Nov**) as a dashed amber bar against the navy baseline tail ending 15 Nov.
* **Do not:** Plot Fast-track of A-123/A-124. Do not claim crashing A-121 or A-125 saves $T$-0. Do not move the baseline M-7 diamond.

---

### Figure 4.1 — Cumulative PV S-curve (Matplotlib)

* **File:** `figures/cash_flow_scurve.pdf`
* **Section:** 4.3
* **Proves:** Peak burn is October; distributed PV ends at **$1,500,000**, not $1,725,000.
* **Data:** Table 4.3 monthly period and cumulative. Secondary bars = period PV; primary line = cumulative PV.
* **Reference lines:** horizontal navy at $1,500,000$ (work PMB); horizontal crimson at $1,718,630$ ($BAC$ / authorisation). Shade August–September vs October peak.
* **Callout:** “Contingency $218,630$ is undistributed — not December cash.”
* **Do not:** Force the S-curve to $1,725,000$. Do not include the $21,000$ Option C cost in PV.

---

### Figure 5.1 — Resource demand vs capacity (Matplotlib)

* **File:** `figures/resource_histogram.pdf`
* **Section:** 5.2
* **Proves:** Unmitigated demand breaks the pad cap; smoothing A-125 plus four surge hires holds the peak at 12.
* **X-axis:** Weeks 1–16 starting 10 Aug 2026 (YAML `resource_weeks`).
* **Series:**
  * Unmitigated demand (crimson hollow or hashed bars) — peaks at **14** in weeks 10–12.
  * Mitigated demand (navy/teal bars) — YAML `demand_mitigated`, peak **12**.
  * Horizontal navy line at **8** labelled “organic crew”.
  * Horizontal crimson line at **12** labelled “HSE pad cap”.
* **Annotation:** “A-125 RF moved to weeks 3–6 using 39 d TF; +4 surge techs in 1.3.3 ($22,400 in base).”
* **Do not:** Draw a “hard limit of 8” and then plot 12 people. 8 is organic headcount, 12 is the occupancy cap.

---

### Figure 6.1 — 5×5 risk matrix with residual arrows (Matplotlib)

* **File:** `figures/risk_matrix.pdf`
* **Section:** 6.2
* **Proves:** All 18 risks exist, and treatment moves the severe set down-left; none are generic “weather / budget overrun” blobs.
* **Grid:** P 1–5 on Y, I 1–5 on X (or standard P vertical / I horizontal — pick one and label). Shade Low / Moderate / High / Extreme.
* **Points:** YAML `p_inherent`,`i_inherent` labelled `R-01` … `R-18`. Arrows to `p_residual`,`i_residual`. If inherent == residual (R-12 cost accepted), a dot without a fake arrow.
* **Do not:** Plot only three example risks. Do not invent coordinates. Crowding: jitter 0.08 and/or a callout list for the (2,5) pair R-02 and R-09.

---

### Figure 7.1 — Governance structure (TikZ)

* **File:** `figures/governance_org.pdf`
* **Section:** 7.1
* **Proves:** Named roles, decision rights, reporting cadence — not a textbook org chart.
* **Boxes:** Executive Board → Campaign PM (Abdul) with DoA “≤ $20k and ≤ 48 h, cannot move M-5/M-7” → Hadi (Planner), Ziyad (Risk/Quality), Ilsa (Cost/Resource) → field row: Launch Director, RSO, GSE Lead, Avionics, Juru Cultural Officer, D&C package manager.
* **Side annotation:** Daily standup / weekly EVM / fortnightly sponsor.

---

### Figure 7.2 — EVM control bands + M-4 worked example (Matplotlib)

* **File:** `figures/evm_example.pdf`
* **Section:** 7.5
* **Proves:** How CPI/SPI **will** be read at the first physical gate; this is a framework, not a progress report.
* **Layout (two panels):**
  * **Upper:** Three dots or a tiny grouped bar at the single date **15 Oct 2026 (M-4)** for PV $865,578, EV $865,578, AC $901,000 (on-plan illustration). Optional second group “late stack” EV $647,578 / AC $870,000 (A-123 milestone 0/100). X-axis is **status date**, not 14 fake weeks.
  * **Lower:** Horizontal Green / Amber / Red bands at 1.05–0.95 / 0.95–0.90 / <0.90. Mark CPI 0.96 and SPI 1.00 (green) and the red pair 0.74 / 0.75.
* **Caption must include the words “illustrative status at M-4; campaign not yet executed.”**
* **Do not:** Draw smooth PV/EV/AC curves from week 1 to 14. That implies the work already happened.

---

## 3. Retired IDs (do not revive)

A-101, A-102, A-103, A-104, A-105, A-106, A-107, A-108, A-109, A-110 from the previous draft are **void**. They mixed RF with cryo GSE, marked site-setup as launch-critical across a 21-day hole, and crashed non-critical work.

---

## 4. Generation order

1. Freeze `data/pep_baseline.yaml` (already matches `requirements.md`).
2. Build LaTeX tables from YAML (or a small `python scripts/export_tables.py`).
3. TikZ: WBS, network, org.
4. Matplotlib: Gantt, compression, S-curve, histogram, risk matrix, EVM example.
5. `pdflatex` — if a figure and a table disagree, the YAML is right and the figure is wrong.
