# Prompt: Draft Section 3 Schedule Management (`sections/03_schedule.tex`)

Write the complete LaTeX for Section 3 of the 3004ENG Project Execution Plan. Target **Exceeds (8/8)**. Do not invent dates, IDs, or dollars.

## Sources of truth (zero drift)

Read and obey, in this order:

1. `data/pep_baseline.yaml`
2. `requirements.md` (Section 3)
3. `charts.md` (figure filenames and what each figure must prove)

If this prompt and those files disagree, **the YAML wins**.

## Remove / do not use

These items from earlier drafts are **retired**. Using them will fail Exceeds.

| Retired | Why it is wrong |
| :--- | :--- |
| Activity IDs A-101 … A-110 | Replaced by A-100 and A-111–A-145, mapped to the WBS |
| Single critical path `A-101 → A-103 → A-105 → A-107 → A-108 → A-109 → A-110` | Dual $TF=0$ merge at **A-133**; LRR waits on **A-134**, not on static fire |
| M-4 = EF of A-103, M-5 = A-105, M-6 = A-107, M-7 = A-108, M-8 = A-109, M-9 = A-110 | Correct EF owners: **A-123, A-133, A-141, A-143, A-144, A-145** |
| A-105 as the network merge | Technical merge is **A-132** (stack + GSE + avionics + Juru). Regulatory merge is **A-133** (WDR + A-113 permits) |
| Coral Sea / cyclonic season as the 5-day driver | Rubric treats generic weather as **Near**. Driver is **R-14** (CASA NOTAM) or **R-12** (payload LEO window 10–12 Nov) |
| Option A: overlap stacking (A-123) with GSE (A-124) | A-124 already runs in parallel and has $TF=3$; that overlap does **not** move $T$-0 |
| Option B: crash A-105 from 14 to 9 days | No A-105. A-133 is 6 days. Crashing stacking or static fire **alone saves 0 days** because A-113 still gates A-133 |
| Option C: crash A-102 + A-105 and fast-track A-106 | None of those IDs are on the launch critical path |
| Baseline $T$-0 moved to 10 Nov; $21k$ baked into BAC | Baseline $T$-0 stays **15 Nov**. Option C is a **contingent** draw on the $218,630$ reserve if R-14 fires |
| “48-hour diagnostic buffer before LRR” under Option C | Option C **shortens** diagnostics. What is preserved is **A-141 at 5 days** (HP-4). A-142 is crashed 4→2; that shorter sweep is the R-15 residual |
| Compression “curve” of three points all at $x=5$ days | That is a vertical line. Use the grouped-bar trade-off in `charts.md` |
| `\includegraphics{compression_curve.pdf}` | File is `figures/compression_tradeoff.pdf` |
| PMBOK 8th edition as a default cite | Cite PMI (2021) PMBOK 7th unless an 8th-edition bibliographic record is in `references.bib` |
| Persona / “elite consultant” preamble | Unnecessary. Write as the Group 1 PEP |
| Crashing A-121, A-124, A-125, or A-112 to “save” $T$-0 | Not launch-critical. A-125 $TF=39$; moving RF does not change 15 Nov |

## Locked figures

- Window: **10 Aug 2026 – 1 Dec 2026**. Seven-day pad calendar. Inclusive dates: $EF = ES + D - 1$; FS+0 successor $ES = EF_{\text{pred}} + 1$.
- Milestones: M-2 **2 Oct** (A-111 imposed finish, **not** launch-critical); M-4 **15 Oct** (A-123); M-5 **30 Oct** (A-133); M-6 **10 Nov** (A-141); M-7 **15 Nov** (A-143); M-8 **20 Nov** (A-144); M-9 **1 Dec** (A-145).
- Launch-critical ($TF=0$): `A-100 → A-122 → A-123 → A-132 → A-133 → A-134 → A-141 → A-142 → A-143 → A-144 → A-145` and in parallel `A-113 → A-133`.
- Near-critical: A-131 $TF=1$; A-124 and A-121 $TF=3$ (A-121 has $FF=0$).
- A-124 = cryo GSE. A-125 = RF calibration. Do not swap.

### Compression what-if (not the baseline)

Board question: can $T$-0 move from **15 Nov to 10 Nov** if R-14 is realised?

Only the **post-A-133 tail** can give five days without also crashing A-113.

| Option | What actually changes | Days | Cost | Slope | Verdict |
| :--- | :--- | ---: | ---: | :--- | :--- |
| A Pure fast-track | A-134 → A-141 from FS to SS+1 (LRR overlaps diagnostics) | 5 | $0 | $0/d | **Rejected** — LRR on incomplete post-fire data; AS9100D hold-point failure / rework |
| B Pure crash | A-134 crashed 6 → 1 day | 5 | $40,000 | $8,000/d | **Rejected** — fatigue, skipped thermal/electrical screens |
| C Hybrid (if R-14 fires) | A-134 6→3 d ($9,000); A-141 kept at 5 d; A-142 4→2 d ($12,000) | 5 | **$21,000** | **$4,200/d** | **Contingent** — keep HP-4; $21k from contingency, **not** added to the $1.5M base |

Option C dates **if invoked:** A-134 31 Oct–2 Nov; A-141 3–7 Nov; A-142 8–9 Nov; A-143 **10 Nov**. Do not move the M-7 diamond on the **baseline** Gantt.

State explicitly: crashing A-123 by five days saves **zero** days on $T$-0 unless A-113 is crashed too.

Cost slope:

$$\text{Cost slope} = \frac{\Delta C}{\Delta T} = \frac{\text{crash cost} - \text{normal cost}}{\text{normal duration} - \text{crash duration}}$$

## Calendar math (use these, not the textbook exclusive-end forms on the YAML dates)

$$
ES = \max(EF_{\text{preds}})+1,\quad
EF = ES + D - 1,\quad
LF = \min(LS_{\text{succs}})-1,\quad
LS = LF - D + 1
$$

$$
TF = LS - ES = LF - EF,\qquad
FF = \min(ES_{\text{succs}}) - EF - 1
$$

(If an activity has no successor, $FF = TF$.) Textbook $EF=ES+D$ may be mentioned once as the discrete-time form; **Table 3.1 numbers must match the YAML**.

### Free float to tabulate (inclusive rule above)

| ID | TF | FF | Note |
| :--- | ---: | ---: | :--- |
| A-100, A-113, A-122, A-123, A-132–A-145 | 0 | 0 | Launch-critical |
| A-111 | 0* | 0 | Imposed Gate 1; not launch-critical |
| A-112 | 53 | 53 | No successor |
| A-114 | 5 | 5 | Feeds A-132 |
| A-121 | 3 | 0 | Delay hits A-124 immediately |
| A-124 | 3 | 3 | Feeds A-132 |
| A-125 | 39 | 39 | No FS successor in YAML; LF constrained before hot fire |
| A-131 | 1 | 1 | Near-critical into A-132 |

## Required structure

Word count **1,100–1,300** of narrative, **excluding** tables and captions. Connected paragraphs, not bullet-point analysis.

**3.1 Network logic and float analysis**

- AON, FS+0, inclusive calendar.
- **Table 3.1** (`booktabs` / `longtable` or `tabularx`): every YAML activity, columns `ID | WBS | Activity | D | Pred. | ES | EF | LS | LF | TF | FF | CP`.
- Prose on path convergence: A-132 then A-133; dual critical paths; how $TF$ vs $FF$ on A-121 protects the project but not the successor.
- Introduce and interpret `\ref{fig:network_logic}` (`figures/network_logic.pdf`) **before** the figure environment.

**3.2 Schedule baseline, Gantt, milestones**

- Convert the pass into the approved baseline. $T$-0 remains 15 Nov.
- Reconcile A1: M-4 was 28 Oct vs Objective 1 on 15 Oct → PEP locks M-4 to **15 Oct**; M-8 22 Nov vs 5-day rule → **20 Nov**. Facility licence already held, so A-113 gates **hot fire**, not stacking.
- Gates: Gate 1 PEP lock (A-111, 2 Oct); Gate 2 flight permits (A-113, 24 Oct); Gate 3 LRR (A-141, 10 Nov).
- Introduce `\ref{fig:gantt_chart}` (`figures/gantt_chart.pdf`) before the figure.

**3.3 Compression (crashing and fast-tracking)**

- Business case = R-12 / R-14, not weather.
- **Table 3.2** as the locked option matrix above, plus a secondary-risks column.
- Introduce `\ref{fig:compression_curve}` pointing at `figures/compression_tradeoff.pdf` before the figure.
- Analyse why A and B fail, why C is the only CPM-valid five-day pull-in that keeps A-142, and whether any feeder (A-131, A-124) becomes $TF \le 2$ **because of C** (C does not shorten A-132/A-133, so those TFs do not change; say so).

## Figures and citations

- Packages already in `A3.tex`: `booktabs`, `tabularx`, `longtable`, `amsmath`, `graphicx`. Add `pdflscape` only if Table 3.1 cannot fit portrait at `\small`.
- Cite in-text with `\cite{}`. Prefer Kerzner (scheduling / crashing), PMI (2021) (critical path, fast-track vs crash), SAE AS9100D (LRR / hold points). Put matching `\bibitem`s in `references.bib` / the bibliography in `A3.tex`.
- Output file: `sections/03_schedule.tex` containing `\section{Schedule management}` and the three subsections. Main file `\input{sections/03_schedule}` in place of the empty Section 3 stubs.

## Output constraints

- No A-101–A-110 IDs anywhere.
- No claim that Option C is already in the $1,500,000$ base.
- No fake 14-week EV/AC (that is Section 7, and it is a plan).
- If a figure PDF is missing, still write the `\ref` and caption; do not invent numbers inside the caption that are not in the YAML.
