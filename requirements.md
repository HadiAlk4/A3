# 3004ENG Assessment 3: Project Execution Plan (PEP) Specification

**Course:** 3004ENG Project Management Principles | Griffith University  
**Project:** Eris TestFlight2 Launch Site Operations Campaign (Bowen Orbital Spaceport)  
**Deliverable:** Group Project Execution Plan (PEP) — Assessment 3  
**Target standard:** Exceeds on all eight rubric criteria  
**Parameters:** 6,000 words ± 10% (5,400–6,600), excluding references, appendices, and content inside tables and figures. Due Friday 2 October 2026, 11:59 pm.

**Single source of truth:** Numeric values in this file and in `data/pep_baseline.yaml` are identical. Matplotlib figures and LaTeX tables must import the YAML (or a generated CSV). Do not re-type dates, dollars, floats, or risk scores in `charts.md`, plotting scripts, or TikZ by hand.

---

## 1. Master data (the golden thread)

Every date, dollar, WBS code, and activity ID in the report must match this table. In-flight EVM thresholds (CPI/SPI bands) are **not** the same thing as the finish-line cost rule.

| Parameter | Locked value | Where it must appear |
| :--- | :--- | :--- |
| Campaign base estimate (distributed work) | **$1,500,000 AUD** | Sec 1, 2, 4 (Table 4.1), 7 (PV / work PMB) |
| Contingency reserve | **$218,630 AUD** (EMV $175,500 + RES $43,130) | Sec 1, 4 (Table 4.2), 6, 7 |
| Authorised baseline ($BAC$) | **$1,718,630 AUD** | Sec 1, 4, 7 |
| Finish-line cost rule | **Final $AC \le \$1{,}718{,}630$** (contingency may be consumed; nothing beyond $BAC$) | Sec 1, 2 (Objective 2), 7 |
| In-flight EVM bands | Green $0.95\le CPI,SPI \le 1.05$; Amber $0.90$–$<0.95$; Red $<0.90$ **plus** T-0 slip $>2$ days | Sec 7 only (do not write "$SV > -5$ days"; $SV$ is currency) |
| M-2 PEP / Gate 1 lock | **2 October 2026** | Sec 2, 3 (A-111 imposed finish) |
| M-4 Pad stacking complete | **15 October 2026** | Sec 1, 2, 3 (A-123 $EF$), 7 (HP / EVM example) |
| M-5 WDR + 5-second static fire | **30 October 2026** | Sec 1, 2, 3 (A-133 $EF$), 7 (HP-3) |
| M-6 Launch Readiness Review | **10 November 2026** | Sec 1, 2, 3 (A-141 $EF$), 7 |
| M-7 Launch window opening ($T$-0) | **15 November 2026** | Sec 1, 2, 3 (A-143). Baseline. Not 10 Nov. |
| M-8 Telemetry handover | **20 November 2026** (5 days after lift-off) | Sec 1, 2, 3 (A-144 $EF$) |
| M-9 Closeout | **1 December 2026** | Sec 1, 2, 3 (A-145 $EF$) |

**Calendar convention (must be used in Table 3.1, Gantt, and network):** seven-day launch-site calendar; dates are inclusive; $EF = ES + D - 1$; FS+0 successor $ES =$ predecessor $EF + 1$.

**Compression $21,000$ is not in the $1.5M$ base.** Baseline $T$-0 remains 15 November. Option C is a pre-priced what-if, drawn from contingency only if R-14 is realised. A-141 stays 5 days.

**Surge labour $22,400$ is in the base** (WBS 1.3.3). It is the planned resource response, not a contingency draw.

---

## 2. Assessment 1 defects to remediate (use only real A1 content)

Do not invent A1 errors. The charter already states a 5-second static fire and already maps Juru as High/High, Manage Closely.

1. **Fallback clause:** A1 had a single redistribution bullet. A3 Sections 5 and 8 must state a 3-tier operating procedure (12-hour artefact audit, PM addendum to reassign WBS packages, Buddycheck PAF locked on Teams/version evidence).
2. **Objective 2:** A1 was qualitative. Rewrite: *"Deliver launch-site operations within the $1,500,000 AUD base estimate, managing an authorised $225,000 AUD contingency sized from residual EMV plus a RES uncertainty allowance, audited at Post-Stacking (M-4), Post-Static Fire (M-5), and Post-Launch (M-7)."*
3. **Citations:** A1 used five references and almost no PM literature in Part A. A3 needs 15+ APA 7th sources (Kerzner; PMI/PMBOK; Turner; ISO 31000:2018; AS9100D; ISO 9001:2015; Rawlinsons; Fair Work; CASA cost-recovery; Gilmour/ASA/GBRMPA). Every design choice (RACI, weighted scoring, EVM thresholds, D&C) is cited in-text.
4. **Quantified success:** *"Finish-line $AC \le \$1{,}725{,}000$ AUD; $T$-0 on 15 November 2026 with in-flight T-0 slip trigger of $>2$ days."*
5. **Date collisions inside A1:** Objective 1 required pad integration by 15 Oct; Milestone M-4 was 28 Oct. M-8 was 22 Nov despite a 5-day handover rule (15 Nov + 5 = 20 Nov). Table 2.1 must record these as the date changes.

---

## 3. Work breakdown structure (100% rule)

Scope remains launch-site operations at Bowen. Factory manufacture, engine R&D, and freight to the receiving gate stay out of scope. **A-100** (vehicle receipt window) is a $0 external wait that starts when the out-of-scope freight reaches the gate; it is on the network because it drives stacking, but it is not a cost account.

* **1.0 Eris TestFlight2 Launch Campaign**
  * **1.1 Campaign project management and governance**
    * 1.1.1 Project execution planning and integration
    * 1.1.2 Governance, budgeting and EVM control
    * 1.1.3 Regulatory, ASA, GBRMPA and CASA airspace permitting
    * 1.1.4 Juru cultural heritage and community stewardship
  * **1.2 Pad logistics, infrastructure and GSE**
    * 1.2.1 Receiving inspection and cleanroom unpacking
    * 1.2.2 Mobile crane mobilisation and 23 m vertical stacking
    * 1.2.3 Cryogenic GSE piping, electrical interfaces and purge checkouts
    * 1.2.4 RF telemetry antenna array calibration
  * **1.3 Pad testing, rehearsals and qualification**
    * 1.3.1 Avionics power-on system sweeps
    * 1.3.2 Integrated cryogenic Wet Dress Rehearsal (LOX load and detank; no hot fire)
    * 1.3.3 5-second hybrid-motor static fire
    * 1.3.4 Post-fire diagnostics / pre-kitted spare swap
  * **1.4 Flight readiness, launch and closeout**
    * 1.4.1 Launch Readiness Review and Range Safety Officer clearance
    * 1.4.2 Range exclusion, marine warning sweeps and countdown
    * 1.4.3 Launch execution and real-time telemetry capture
    * 1.4.4 Telemetry decryption and engineering handover
    * 1.4.5 Site decommissioning and closeout audit

Seventeen cost accounts. Schedule has **19 bars** (17 WBS packages, with 1.2.1 split into A-121/A-122, plus A-100).

**Limited notice-to-proceed:** A1 charter (7 Aug 2026) authorises mobilisation from 10 Aug. Full cost/schedule baseline locks at Gate 1 (A-111, 2 Oct). Field work before 2 Oct is not a logic error; it is charter-authorised mobilisation.

---

## 4. Section-by-section Exceeds requirements

### Section 1: Executive summary (2 marks | ~400 words)

Draft last, after all tables reconcile. A board member must be able to approve or decline from this section alone.

* Purpose: deliver Eris TestFlight2 **launch-site operations** at Bowen to obtain Australian sovereign flight heritage after TF1.
* Scope: cleanroom receipt, GSE, WDR, 5-second static fire, range clearance, 15 Nov launch, telemetry handover. Manufacturing, redesign, and freight to the gate are out of scope.
* Money: $1,500,000 base + $225,000 contingency (15.00% of base, EMV+RES) = **$1,725,000 $BAC$**.
* Dates: M-4 15 Oct; M-5 30 Oct; M-6 10 Nov; M-7 **15 Nov**; M-8 20 Nov.
* Top three risks (same IDs and consequences as Table 6.1):
  * **R-01:** Residual pump-insulation defect → static-fire auto-abort on A-133 → 12–14 day critical-path recycle.
  * **R-09:** Stage-separation timing error → debris outside the predicted footprint → GBRMPA inquiry and range halt.
  * **R-14:** CASA NOTAM / Townsville airspace lag → 15 Nov slot refused.
* Recommendation (verbatim numbers): *"It is recommended that the Executive Board approve this Project Execution Plan, baseline the campaign at $1,725,000 AUD (inclusive of $225,000 contingency), and authorise mobilisation for Bowen pad operations with $T$-0 on 15 November 2026."*

---

### Section 2: Refined project overview (3 marks | ~650 words)

Show a project the team understands better than Week 4. Every material change goes in **Table 2.1**, with the A1 wording on the left and the learning on the right. Scope uses the 100% rule against the WBS above.

**Table 2.1 — Charter baseline vs PEP refinement (use these rows, not invented A1 defects)**

| Project element | A1 charter (Week 4) | A3 PEP (Week 11) | Why it changed |
| :--- | :--- | :--- | :--- |
| **M-4 stacking date** | Objective 1: pad integration 15 Oct. Milestone M-4: stacking 28 Oct. | **M-4 locked to 15 Oct 2026** (A-123 $EF$). | Removes the internal collision. Creates a 15-day pad-test buffer before the 30 Oct hot-fire gate. |
| **M-8 handover date** | “5 days post-launch” and milestone date 22 Nov (7 days after 15 Nov). | **M-8 = 20 Nov 2026** (A-144). | Aligns the milestone with Objective 5 and the 5-day rule. |
| **Cost baseline** | “Manage within the allocated operational budget.” No figure. | Bottom-up **$1,500,000** + **$225,000** contingency. | Crane hire, cryogenic crews, and LOX delivery cannot be controlled without a numbered baseline. |
| **Permit vs stacking logic** | M-3 flight permits 25 Oct were predecessors of M-4 stacking (then 28 Oct). | Facility licence already held (Mar 2024). **A-113 gates A-133 static fire, not stacking.** Permits $EF$ 24 Oct; hot fire $ES$ 25 Oct. | Stacking is a site-licence activity. Hot fire is a range activity. This also creates a second critical path. |
| **Juru engagement** | High power / high interest, **Manage Closely**, consultation and monitoring. | Same power/interest. **Embedded monitors with stop-work authority** and a cultural hold point before WDR (A-114 → A-132). | A1 strategy was correct in class; the PEP makes it an enforceable pad control, not a comms plan. |
| **Testing sequence** | WDR and 5-second static fire as one Objective 3 output by 30 Oct. | **A-132 WDR (cold) 16–24 Oct, then A-133 static fire 25–30 Oct.** LRR waits on A-134 diagnostics. | Hot fire must wait for flight permits. LRR cannot start on incomplete post-fire data. |
| **Risk governance** | Five high-level threats, no $P \times I$ money. | **18 campaign-specific risks**, Cause→Event→Effect, EMV $175,500$ + RES $49,500$. | Generic rows cannot size contingency or point at a WBS line. |
| **Resource peak** | Roles listed; no demand vs capacity. | Organic crew **8**, pad HSE cap **12**, unmitigated peak **14**, mitigated peak **12**. | A1 could not show where the plan exceeds capacity. |

Insert a TikZ WBS tree (Figure 2.1) that uses these exact codes.

---

### Section 3: Schedule management (8 marks | ~1,200 words + tables)

Exceeds requires network logic **with float**, a critical path that is **derived**, a Gantt that matches, and a compression option that actually shortens **critical-path** work.

#### 3.1 Activity table (Table 3.1) — locked CPM

Two paths have $TF=0$ into A-133: the vehicle path and the permit path. After A-133 the tail to closeout is a single critical chain.

Launch-critical ($TF=0$), crimson on Gantt/network:  
`A-100 → A-122 → A-123 → A-132 → A-133 → A-134 → A-141 → A-142 → A-143 → A-144 → A-145`  
and in parallel `A-113 → A-133`.

A-111 is **Gate-1 constrained** (must finish 2 Oct). It is **not** on the launch critical path. Navy + diamond M-2, not crimson.

| ID | WBS | Activity | $D$ (d) | Predecessors | $ES$ | $EF$ | $LS$ | $LF$ | $TF$ | CP |
| :--- | :--- | :--- | ---: | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| A-100 | EXT | Vehicle receipt window (external, $0) | 35 | — | 10 Aug | 13 Sep | 10 Aug | 13 Sep | 0 | **Y** |
| A-111 | 1.1.1 | PEP and integration baseline | 54 | — | 10 Aug | 2 Oct | 10 Aug | 2 Oct | 0* | Gate 1 |
| A-112 | 1.1.2 | EVM and control-system stand-up | 7 | A-111 | 3 Oct | 9 Oct | 25 Nov | 1 Dec | 53 | N |
| A-113 | 1.1.3 | CASA / GBRMPA / airspace permits | 76 | — | 10 Aug | 24 Oct | 10 Aug | 24 Oct | 0 | **Y** |
| A-114 | 1.1.4 | Juru monitor mobilisation | 62 | — | 10 Aug | 10 Oct | 15 Aug | 15 Oct | 5 | N |
| A-121 | 1.2.1a | Site mobilisation and cleanroom | 19 | — | 10 Aug | 28 Aug | 13 Aug | 31 Aug | 3 | N |
| A-122 | 1.2.1b | Receiving inspection and unpacking | 8 | A-100, A-121 | 14 Sep | 21 Sep | 14 Sep | 21 Sep | 0 | **Y** |
| A-123 | 1.2.2 | Crane mobilisation and vertical stacking | 24 | A-122 | 22 Sep | 15 Oct | 22 Sep | 15 Oct | 0 | **Y** |
| A-124 | 1.2.3 | Cryo GSE piping and checkouts | 45 | A-121 | 29 Aug | 12 Oct | 1 Sep | 15 Oct | 3 | N |
| A-125 | 1.2.4 | RF telemetry array calibration | 18 | A-121 | 29 Aug | 15 Sep | 7 Oct | 24 Oct | 39 | N |
| A-131 | 1.3.1 | Avionics power-on sweeps | 23 | A-122 | 22 Sep | 14 Oct | 23 Sep | 15 Oct | 1 | N |
| A-132 | 1.3.2 | Wet Dress Rehearsal (cold) | 9 | A-114, A-123, A-124, A-131 | 16 Oct | 24 Oct | 16 Oct | 24 Oct | 0 | **Y** |
| A-133 | 1.3.3 | 5-second static fire | 6 | A-132, A-113 | 25 Oct | 30 Oct | 25 Oct | 30 Oct | 0 | **Y** |
| A-134 | 1.3.4 | Post-fire diagnostics and LRU | 6 | A-133 | 31 Oct | 5 Nov | 31 Oct | 5 Nov | 0 | **Y** |
| A-141 | 1.4.1 | LRR and RSO clearance | 5 | A-134 | 6 Nov | 10 Nov | 6 Nov | 10 Nov | 0 | **Y** |
| A-142 | 1.4.2 | Range exclusion and countdown | 4 | A-141 | 11 Nov | 14 Nov | 11 Nov | 14 Nov | 0 | **Y** |
| A-143 | 1.4.3 | Launch execution ($T$-0) | 1 | A-142 | 15 Nov | 15 Nov | 15 Nov | 15 Nov | 0 | **Y** |
| A-144 | 1.4.4 | Telemetry decrypt and handover | 5 | A-143 | 16 Nov | 20 Nov | 16 Nov | 20 Nov | 0 | **Y** |
| A-145 | 1.4.5 | Demobilisation and closeout audit | 11 | A-144 | 21 Nov | 1 Dec | 21 Nov | 1 Dec | 0 | **Y** |

\*A-111 $TF=0$ is an **imposed** Must-Finish-On Gate 1, not launch-critical.

**A-125 is the RF task. A-124 is cryo GSE. Never swap those IDs.**

Formulas in prose (once):  
$ES=\max(EF_{\text{preds}})+1$ (with $ES=$ start date if no pred); $EF=ES+D-1$; $LF=\min(LS_{\text{succs}})-1$; $LS=LF-D+1$; $TF=LS-ES=LF-EF$.

**Do not crash A-121, A-124, A-125, or A-112 to “save” $T$-0.** They are not on the launch critical path. Fast-tracking A-125 does not move 15 Nov.

#### 3.2 Compression (Table 3.2) — what-if only

Driver: not generic weather. Either **R-14** (CASA slot refused for 15 Nov) or **R-12** (payload LEO geometry valid 10–12 Nov). Board asks: can $T$-0 move to **10 November**?

Post-merge critical tail after A-133 is the only place a 5-day pull-in is mathematically available without also crashing A-113 (permits already $TF=0$ at 24 Oct). Crashing stacking (A-123) **alone saves 0 days** because A-113 still gates A-133.

| Option | Activities altered | Days saved | Added cost | Cost slope | Secondary risks | Verdict |
| :--- | :--- | ---: | ---: | :--- | :--- | :--- |
| **A Pure fast-track** | A-134 → A-141 changed from FS to SS+1 (LRR overlaps diagnostics) | 5 | $0 | $0/d | LRR would be in session before diagnostic closeout; high rework if an LRU swap appears on day 5 | **Rejected** — quality/HSE on a flight-clearance gate |
| **B Pure crash** | A-134 crashed 6 → 1 day (24-hour diagnostic war room) | 5 | $40,000 | $8,000/d | Fatigue, skipped thermal/electrical screens, likely recycle into A-141 | **Rejected** — cost slope and verification integrity |
| **C Hybrid (chosen if R-12/R-14 fires)** | Crash A-134 6→3 d ($3,000/d = $9,000); crash A-141 5→3 d ($6,000/d = $12,000) | 5 | **$21,000** | **$4,200/d** | Staggered 10-hour shifts; 48-hour countdown buffer (A-142) kept | **Approved as contingent response only** |

Option C dates **if invoked:** A-134 31 Oct–2 Nov; A-141 3–5 Nov; A-142 6–9 Nov; A-143 **10 Nov**. Do not retitle M-7 in the baseline Gantt. Show Option C as a dashed alternate on Figure 3.3.

Prose must say why C beats A and B, and why crashing A-123 would not move $T$-0 unless A-113 is also crashed.

---

### Section 4: Cost management (5 marks | ~850 words)

Every line traces to a WBS code. Totals = executive summary. Sources sit next to the numbers (Rawlinsons; Fair Work loaded rates; published QLD 100 t crane hire; industrial-gas LOX; CASA cost-recovery). Inclusions/exclusions match Section 2. Contingency is **not** a flat 15% story — 15.00% is the **result** of EMV+RES.

Labour assumptions (state once, reuse): systems engineer / PM $150/h loaded; technician $95/h loaded; cryo/RSO specialist $165/h; surge technician $100/h loaded; 100 t crane **$4,200/day**.

#### Table 4.1 — Bottom-up rollup (base = $1,500,000)

| WBS | Package | Amount (AUD) | Basis (cite in footnotes) |
| :--- | :--- | ---: | :--- |
| 1.1.1 | PEP and integration | 72,000 | 480 h PM @ $150 |
| 1.1.2 | Governance and EVM | 48,000 | 320 h planner/cost @ $150 |
| 1.1.3 | Regulatory / GBRMPA / CASA | 88,000 | Consultant + agency cost-recovery |
| 1.1.4 | Juru monitors and heritage | 92,000 | 2 monitors + survey |
| 1.2.1 | Receiving and cleanroom | 68,000 | Technician hours + consumables |
| 1.2.2 | Crane and 23 m stacking | 218,000 | Crane 24 d × $4,200 = $100,800 plus rigger labour |
| 1.2.3 | Cryo GSE | 180,000 | Valves/piping + specialist crew |
| 1.2.4 | RF array calibration | 52,000 | Crew + analyser hire |
| 1.3.1 | Avionics power-on | 58,000 | Engineers @ $150/h + EGSE |
| 1.3.2 | WDR | 160,000 | **Includes bulk LOX 25 t and LN2 $68,500** |
| 1.3.3 | Static fire | 148,000 | **Includes surge hire $22,400** (4 × 7 d × 8 h × $100) |
| 1.3.4 | Post-fire diagnostics | 48,000 | Engineers + LRU handling |
| 1.4.1 | LRR and RSO | 38,000 | Review board |
| 1.4.2 | Range exclusion and marine sweeps | 58,000 | Patrol boats + NOTAM/community |
| 1.4.3 | Launch and telemetry capture | 82,000 | Launch-day operations |
| 1.4.4 | Decrypt and handover | 24,000 | 5-day engineering handover |
| 1.4.5 | Demobilisation and audit | 66,000 | Site restore (Rawlinsons) + audit |
| **Base** | | **1,500,000** | |

#### Table 4.2 — Contingency (not a flat percentage)

| Component | Amount (AUD) | Rule |
| :--- | ---: | :--- |
| Σ EMV of cost-bearing risks R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-09, R-10, R-13, R-14 | **175,500** | $EMV = P_{\%} \times I_{\$}$ using the dollar column in Table 6.1, **not** the 1–5 score |
| RES uncertainty allowance | **49,500** | In-scope only: LOX remote-delivery price variance, crane standby in wind, unquantified pad anomalies. **Not** vehicle freight (out of scope) |
| **Contingency reserve** | **225,000** | 15.00% of base as a **result** |
| **$BAC$** | **1,725,000** | Base + contingency |

R-08 pad-civil defect is contract-transferred under D&C (no Gilmour EMV). R-11, R-12, R-15, R-16, R-17, R-18 are schedule/HSE or already priced in Option C; they are not double-counted in the $175,500$.

#### Table 4.3 — Time-phased **base** PV (contingency is not monthly spend)

| Month | Period PV (AUD) | Cumulative PV (AUD) |
| :--- | ---: | ---: |
| Aug 2026 | 218,000 | 218,000 |
| Sep 2026 | 284,000 | 502,000 |
| Oct 2026 (peak: stack, WDR, static fire) | 657,000 | 1,159,000 |
| Nov 2026 | 315,000 | 1,474,000 |
| Dec 2026 | 26,000 | **1,500,000** |

S-curve **terminates at $1,500,000$**. Draw $BAC = \$1{,}725{,}000$ as a horizontal authorisation line, not as December cash.

---

### Section 5: Resource management (4 marks | ~700 words)

#### Capacity story (one story only)

* Organic Bowen crew: **8** certified technicians.
* Pad HSE occupancy cap: **12** (blast-zone / suit-air / access control). **8 is not a hard pad limit.**
* Unmitigated peak (if A-125 RF stayed in October on top of WDR/static fire): **14** in weeks 10–12 (12–1 Nov window of late Oct). Deficit vs HSE cap = 2; deficit vs organic crew = 6.
* Mitigated baseline: (1) **smooth A-125** into 29 Aug–15 Sep using 39 days of total float — $0, no critical-path effect; (2) **hire 4 surge technicians** for 7 days in 1.3.3 — **$22,400 inside the base**. Mitigated peak = **12**, on the HSE cap, never above it.

#### RACI (Table 5.1)

Two layers, exactly one **A** per WBS package:

* Consultancy: Abdul (PM / integration), Hadi (planner / schedule), Ziyad (risk / quality / HSE), Ilsa (cost / resource / Juru commercial interface).
* Field: Launch Director, Range Safety Officer, GSE Lead, Avionics Specialist, Juru Cultural Officer, D&C package manager.

#### Escalation (resource conflicts, not personal conflict)

* Tier 1 Field Leads — 4-hour SLA (level, stagger, borrow from float).
* Tier 2 Campaign PM trade-off — 12-hour SLA (overtime vs hire vs resequence; cost to Ilsa).
* Tier 3 Executive Board — 24-hour SLA (anything that consumes contingency or moves M-5/M-7).

A1 fallback (non-responsive member >48 h): Lead Planner audits artefacts within 12 h; PM issues WBS reassignment addendum; Buddycheck PAF locked on Teams + version history.

---

### Section 6: Risk management (6 marks | ~1,000 words)

Define scales **once**, then use them. Heatmap uses 1–5. EMV uses the dollar column.

* Probability $P$: 1 (<5%, use 3% in EMV), 2 (5–20%, use 12%), 3 (21–40%, use 30%), 4 (41–60%, use 50%), 5 (>60%, use 70%).
* Schedule $I_S$: 1 (<2 d), 2 (2–5 d), 3 (6–10 d), 4 (11–15 d), 5 (>15 d on a $TF=0$ path).
* Cost $I_C$ dollars as listed. Matrix $I$ = $\max$ band of $I_S$ and $I_C$.

Cause, event, and effect are three different clauses. Owners are named. Responses are actions. Residual $P,I$ must drop only where the action actually bites.

Prose after the table must link: $225,000$ absorbs the $175,500$ EMV plus RES; A-125/A-124/A-114 float absorbs non-critical delay; D&C transfers pad-civil (R-08) to the specialist contractor; Option C is the schedule response to R-12/R-14.

#### Table 6.1 — Integrated register (18 risks)

| ID | Anchor | Cause → event → effect | $P$ | $I$ | $P{\times}I$ | Owner | Response | $P'$ | $I'$ | EMV (AUD) |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- | :--- | ---: | ---: | ---: |
| R-01 | A-133 / 1.3.3 | Residual pump insulation defect → static-fire auto-abort → 12–14 d recycle and ~$90k consumables | 3 | 4 | 12 | Ziyad / GSE Lead | Thermal soak instrumentation; on-pad LRU kit; 48 h recycle procedure | 1 | 3 | 27,000 |
| R-02 | A-143 / 1.4.3 | Trajectory energy toward Coral Sea park boundary → stage debris in GBRMPA zone → statutory suspension | 2 | 5 | 10 | Launch Director | South-biased footprint in LRR; joint GBRMPA protocol | 1 | 4 | 21,600 |
| R-03 | A-125 / A-143 | RF interference at Bowen array → telemetry <98.5% → heritage objective fail | 3 | 3 | 9 | Avionics Lead | Dual-path recorders; A-125 completed before hot fire; mobile backup receiver | 1 | 2 | 15,000 |
| R-04 | A-114 / A-143 | Acoustic/exclusion without honouring stop-work → Juru complaint → range clearance withheld | 3 | 4 | 12 | Ilsa / Juru Officer | Embedded monitors with stop-work; cultural HP before A-132 | 1 | 2 | 12,000 |
| R-05 | A-124 / A-132 | Inadequate purge before LOX load → frozen/cracked valve → WDR abort, ~8 d | 3 | 3 | 9 | GSE Lead | LN2 pre-chill; spare valve kit; helium leak test HP-2 | 2 | 2 | 16,500 |
| R-06 | A-123 / 1.2.2 | Abbot Point crosswind >20 kt during vertical mate → lift abort → crane standby | 4 | 2 | 8 | Hadi / Stack Conductor | Dawn-lift window; standby already inside 1.2.2 | 2 | 2 | 9,000 |
| R-07 | A-124 / D&C | D&C GSE IFC lags Gilmour propulsion ICD → pad interface mismatch → rework | 3 | 3 | 9 | GSE Lead / PM | ICD freeze gate; weekly integration; D&C LDs | 1 | 2 | 21,000 |
| R-08 | 1.2.3 / D&C | Latent pad civil defect under D&C package → hold-down failure → hot-ops stop | 2 | 4 | 8 | D&C package mgr (A: PM) | NDT HP-1; defect liability remains with D&C | 1 | 2 | 0 (transferred) |
| R-09 | A-143 | Stage-sep charge timing error → debris outside footprint → range halt / inquiry | 2 | 5 | 10 | Launch Director | Dual-string sep inhibit; wind hold toward park | 1 | 4 | 18,000 |
| R-10 | A-132 / 1.3.2 | Single 800 km LOX tanker delay → WDR cannot load → 2–5 d slip | 3 | 2 | 6 | Ilsa | 72 h tanker confirm; Townsville backup; RES covers price variance | 2 | 1 | 6,900 |
| R-11 | A-131 | Flight-computer vs pad EGSE version skew → power-on abort | 3 | 2 | 6 | Avionics Specialist | ICD freeze; cleanroom EGSE dry run before stack | 1 | 2 | — |
| R-12 | A-143 | Payload LEO geometry only valid 10–12 Nov → board directs 5-day pull-in | 2 | 2 | 4 | Abdul / Sponsor | Pre-priced Option C; draw $21k from contingency if approved | 2 | 1 | — |
| R-13 | A-132 / A-133 | Peak 14 vs cap 12 → detank procedural error → recycle/injury | 4 | 3 | 12 | Ilsa | A-125 moved to Sep; 4 surge techs in base; 10 h stagger | 2 | 2 | 15,000 |
| R-14 | A-113 / A-143 | Townsville military airspace / late NOTAM → 15 Nov slot refused | 3 | 4 | 12 | Abdul / Regulatory | File 60 d prior; weekly CASA liaison; Option C as backup | 2 | 2 | 13,500 |
| R-15 | A-142 | Dugong/marine-mammal presence in exclusion box → sweep extension | 2 | 3 | 6 | RSO | Marine mammal protocol; A-142 holds 4 d buffer vs $T$-0 | 1 | 2 | — |
| R-16 | A-141 | RSO vs Launch Director deadlock at LRR → missed 10 Nov gate | 2 | 3 | 6 | Abdul / Launch Director | Named DoA; unresolved items escalate 24 h before A-141 $LF$ | 1 | 2 | — |
| R-17 | A-133 | Static-fire acoustic >135 dB at Bowen township → complaint / hold | 3 | 3 | 9 | Ziyad / HSE | Water deluge; 1.5 km exclusion; community notice 14 d prior | 1 | 2 | — |
| R-18 | A-142 / A-143 | FTS/countdown software abort at $T$-10 → recycle inside window | 2 | 4 | 8 | Hadi / Avionics | Two countdown rehearsals; abort-to-recycle procedure | 1 | 3 | — |

EMV column uses $P_{\%}\times I_{\$}$: R-01 $0.30\times90{,}000$; R-02 $0.12\times180{,}000$; R-03 $0.30\times50{,}000$; R-04 $0.30\times40{,}000$; R-05 $0.30\times55{,}000$; R-06 $0.50\times18{,}000$; R-07 $0.30\times70{,}000$; R-09 $0.12\times150{,}000$; R-10 $0.30\times23{,}000$; R-13 $0.50\times30{,}000$; R-14 $0.30\times45{,}000$. Sum = **$175,500$**.

Heatmap arrows (P,I) → residual:  
R-01 (3,4)→(1,3); R-02 (2,5)→(1,4); R-03 (3,3)→(1,2); R-04 (3,4)→(1,2); R-05 (3,3)→(2,2); R-06 (4,2)→(2,2); R-07 (3,3)→(1,2); R-08 (2,4)→(1,2); R-09 (2,5)→(1,4); R-10 (3,2)→(2,1); R-11 (3,2)→(1,2); R-12 (2,2)→(2,1); R-13 (4,3)→(2,2); R-14 (3,4)→(2,2); R-15 (2,3)→(1,2); R-16 (2,3)→(1,2); R-17 (3,3)→(1,2); R-18 (2,4)→(1,3).

---

### Section 7: Delivery and control (8 marks | ~1,350 words)

#### Governance

Gilmour Executive Board (sponsor) → Campaign PM (Abdul) → Field Leads.  
**Delegation:** PM may approve a variance $\le \$20{,}000$ **and** $\le 48$ hours without moving M-5 or M-7. Anything else goes to the Board within 24 hours.  
Cadence: daily pad standup; weekly EVM dashboard; fortnightly sponsor review.  
TikZ org chart (Figure 7.1) with those names and the DoA on the PM box.

#### Delivery model

**Chosen: Managing contractor / D&C hybrid.** Gilmour keeps propulsion IP, integration, and launch licensing. Civil and GSE packages go D&C with ICD freeze and LDs (answers R-07/R-08).

**Rejected: turnkey EPC.** Handing propulsion IP and the launch licence to a single EPC is unacceptable given TF1’s pump failure and ASA licence conditions. State scope certainty (site ops are well defined; vehicle remains Gilmour) and client capability (Gilmour can integrate; it should not pour pad grout).

#### Quality

AS9100D and ISO 9001:2015. Hold points: **HP-1** pad tie-down weld NDT (R-08); **HP-2** GSE helium leak test (R-05); **HP-3** pre-static-fire ignition interlock (R-01); **HP-4** LRR sign-off (A-141).

#### HSE (this pad, not a textbook list)

LOX PPE and exclusion; **1.5 km** blast zone; **135 dB** acoustic deluge (R-17); scrub-fire breaks; Juru artefact buffer and stop-work (R-04); pad occupancy cap **12**.

#### EVM framework (a plan, not fake history)

* Work PMB (distributed PV) = **$1,500,000**. Contingency is **undistributed**. $BAC = \$1{,}725{,}000$.
* Measurement: **0/100** on discrete tests and permits (A-113, A-132, A-133, A-141, A-143). **Milestone percent complete** on installations (A-123, A-124) tied to HP-1/HP-2.
* $SV=EV-PV$ (dollars), $CV=EV-AC$, $SPI=EV/PV$, $CPI=EV/AC$.  
  $EAC = AC + (BAC_{\text{work}} - EV)/CPI$ for in-flight work; also report $BAC/CPI$ against the $1,725,000$ ceiling.
* Bands: Green $0.95\le index \le 1.05$ weekly report; Amber $0.90\le index <0.95$ — Exception Report and 7-day recovery within 48 h; Red $index <0.90$ **or T-0 slip $>2$ days** — contingency freeze, Board intervention.
* Finish-line remains $AC \le \$1{,}725{,}000$. A Green CPI of 0.96 in October is allowed; finishing above $BAC$ is not.

**Worked example at M-4 (15 Oct 2026) — the only “dashboard” numbers permitted**

| Status at M-4 | PV | EV | AC | CPI | SPI | Action |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| Planned (stacking 0/100 complete, GSE HP-2 complete) | **$825,000** | — | — | — | — | — |
| Illustrative on-plan | 825,000 | 810,000 | 840,000 | 0.96 | 0.98 | Green — weekly dashboard |
| Illustrative late stack acceptance | 825,000 | 760,000 | 830,000 | 0.92 | 0.92 | **Amber** — 48 h exception report |

Do **not** invent 14 weeks of EV/AC history. The campaign has not been executed.

---

### Section 8: Integration and professionalism (4 marks)

* One project: Table 3.1, Table 4.1, Table 4.3, Table 6.1, Gantt, network, S-curve, histogram, and the exec summary use the YAML values.
* Title page, TOC, numbered headings, 12 pt, 1.5 line spacing, APA 7th.
* Every figure/table numbered, captioned, and referred to in prose **before** it appears.
* Cover contribution 100.0%: Abdul Wahab Obeid s5303839 25.0%; Hadi Alkhub s5331680 25.0%; Ziyad Alahmari s5375826 25.0%; Ilsa Hashmi s5310047 25.0%.
* One-page signed contribution appendix.

**Hadi’s A3 production share (from A1):** scope, schedule, network logic, Gantt, compression. Abdul: exec summary, integration, QA. Ziyad: risk, quality, HSE. Ilsa: cost, resources, capacity. Percentages stay 25% if hours are equalised in the appendix.

---

## 5. Figure and table ownership

See `charts.md`. Python (Matplotlib) draws data plots. TikZ draws node diagrams. LaTeX typesets tables. Nothing in a figure may disagree with Tables 3.1, 4.1, 4.3, or 6.1.
