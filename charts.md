# 3004ENG Assessment 3: Visual Asset & Chart Pipeline Specification

**Project:** Eris TestFlight2 Launch Site Operations Campaign  
**Output Directory:** `figures/` (Vector PDF format)  
**Tooling Engine:** Python (Matplotlib, NetworkX, NumPy)  
**Primary Mandate:** All visual assets must strictly reflect the figures and dates defined in `requirements.md`. Every chart must be saved as a vector PDF for inclusion in LaTeX via `\includegraphics`.

---

## 1. Global Visual & Technical Standards

1. **Vector Format:** All scripts must save figures directly to PDF using `bbox_inches='tight'`.
2. **Color Palette Consistency:** Maintain a coherent aerospace palette across all generated plots:
   * Primary Dark / Neutral: Deep Navy `#0B2545` (Base lines, scheduled tasks, normal boundaries)
   * Critical / Highlight: Crimson `#C0392B` (Critical path, over-allocations, Red EVM breaches)
   * Success / Performance: Muted Teal `#2A9D8F` (Earned value, compliant states, float available)
   * Warning / Advisory: Amber `#E76F51` (Amber thresholds, compressed tasks, medium risk)
   * Background / Grid: Light Grey `#E0E0E0` or `#F4F4F4` (Clean, unobtrusive layout)
3. **Typography & Layout:** Let the plotting script generate clean, well-proportioned visual layouts. Keep legends clear, ensure axis labels carry units (e.g., AUD ($), Days, Date), and avoid visual clutter or overlapping text.

---

## 2. Figure Register & Generation Specifications

### Figure 1: Master Campaign Gantt Chart
* **File:** `figures/gantt_chart.pdf`
* **Target Section:** Section 3.2 (Schedule Baseline)
* **Objective:** Display the full campaign schedule from August 10 to December 1, 2026, highlighting the derived critical path and key project milestones.
* **Data Inputs:**
  * WBS activities from Table 3.1:
    * A-101: Site Mobilization & Cleanroom Setup (Aug 10 – Aug 24) [Critical]
    * A-102: GSE Civil & Anchor Checkouts (Aug 24 – Sep 14) [TF = 4]
    * A-103: Stage Receiving & Pad Stacking (Sep 14 – Oct 15) [Critical | M-4 Finish]
    * A-104: Cryo GSE Piping Checkouts (Oct 01 – Oct 18) [TF = 5]
    * A-105: WDR & 5-Second Static Fire (Oct 16 – Oct 30) [Critical | M-5 Finish]
    * A-106: Post-Fire Telemetry Sweep (Oct 31 – Nov 08) [TF = 2]
    * A-107: Range Clearance & LRR Gate (Nov 01 – Nov 10) [Critical | M-6 Finish]
    * A-108: Launch Countdown & Flight Execution (Nov 11 – Nov 15) [Critical | M-7 Finish]
    * A-109: Telemetry Decryption & Handover (Nov 16 – Nov 20) [Critical | M-8 Finish]
    * A-110: Pad Decommissioning & Audit (Nov 21 – Dec 01) [Critical | M-9 Finish]
* **Visual Elements:**
  * Horizontal bar chart plotted against a daily/weekly timeline.
  * Critical path activities colored in Crimson; non-critical activities colored in Navy.
  * Vertical dashed marker lines indicating key milestones: M-4 (Oct 15), M-5 (Oct 30), M-6 (Nov 10), and M-7 (Nov 15).

---

### Figure 2: Activity Precedence Network Logic Diagram
* **File:** `figures/network_logic.pdf`
* **Target Section:** Section 3.1 (Network Logic & Float Analysis)
* **Objective:** Illustrate dependencies, node anatomy, and the mathematical forward/backward pass path for key campaign activities.
* **Data Inputs:**
  * Nodes: A-101 through A-110 with calculated $ES, EF, LS, LF, TF$.
  * Precedence links:
    * A-101 $\rightarrow$ A-102 & A-103
    * A-102 $\rightarrow$ A-104
    * A-103 $\rightarrow$ A-105
    * A-104 $\rightarrow$ A-105
    * A-105 $\rightarrow$ A-106 & A-107
    * A-106 $\rightarrow$ A-108
    * A-107 $\rightarrow$ A-108
    * A-108 $\rightarrow$ A-109 $\rightarrow$ A-110
* **Visual Elements:**
  * Directed acyclic graph layout (left to right).
  * Node boxes formatted with standard scheduling node anatomy (Task ID, Duration, ES, EF, LS, LF, Total Float).
  * Critical path connecting arrows highlighted in bold Crimson; non-critical connecting lines in subtle Slate Grey.

---

### Figure 3: Schedule Compression Trade-Off Curve
* **File:** `figures/compression_curve.pdf`
* **Target Section:** Section 3.3 (Schedule Compression Scenario)
* **Objective:** Compare the three evaluated schedule acceleration scenarios (Pure Fast-Tracking, Pure Crashing, Hybrid Optimization) plotting added cost against days saved.
* **Data Inputs:**
  * Baseline: 0 days saved, $0 added cost.
  * Option A (Pure Fast-Tracking): 5 days saved, $0 direct cost, but carries extreme safety/rework risk.
  * Option B (Pure Crashing): 5 days saved, $40,000 added cost (Cost slope = $8,000/day).
  * Option C (Hybrid Optimization - Chosen): 5 days saved, $21,000 added cost (Cost slope = $4,200/day).
* **Visual Elements:**
  * Scatter plot with discrete trend lines comparing Cost Slope ($\Delta C / \Delta T$).
  * Annotation callouts on each point stating the operational consequence and decision verdict (Rejected vs. Approved).

---

### Figure 4: Cumulative Cash Flow S-Curve
* **File:** `figures/cash_flow_scurve.pdf`
* **Target Section:** Section 4.3 (Time-Phased Budget & Cash Flow)
* **Objective:** Illustrate time-phased planned expenditure ($PV$) across the 5-month project lifecycle, highlighting the peak capital burn period.
* **Data Inputs:**
  * Monthly planned spend:
    * Month 1 (August 2026): $180,000 AUD (Cumulative: $180,000)
    * Month 2 (September 2026): $260,000 AUD (Cumulative: $440,000)
    * Month 3 (October 2026): $640,000 AUD (Cumulative: $1,080,000) — *Peak Burn: Crane leases, bulk propellant, static fire operations*
    * Month 4 (November 2026): $480,000 AUD (Cumulative: $1,560,000) — *Launch operations, marine tracking fleet*
    * Month 5 (December 2026): $165,000 AUD (Cumulative: $1,725,000) — *Decommissioning, final audit*
* **Visual Elements:**
  * Primary axis: Smooth cumulative S-curve line terminating at exactly $1,725,000 AUD ($BAC$).
  * Secondary axis (or overlay bars): Monthly expenditure columns showing period spend.
  * Shaded highlight over Month 3/Month 4 denoting the peak capital expenditure window.

---

### Figure 5: Resource Demand vs. Capacity Histogram
* **File:** `figures/resource_histogram.pdf`
* **Target Section:** Section 5.2 (Capacity Planning & Over-Allocation)
* **Objective:** Demonstrate technician demand over time, identifying the peak deficit during pad testing and proving the effectiveness of the leveling/smoothing strategy.
* **Data Inputs:**
  * Timeline: Weeks 1 to 16.
  * Baseline Site Technician Capacity: Fixed horizontal limit of **8 certified personnel**.
  * Unmitigated Peak Demand: Weeks 10–12 (Mid-to-Late October) spikes to **14 personnel** (Deficit of 6 technicians).
  * Mitigated Demand: Non-critical RF calibration task smoothed using float; 4 specialist contractors hired, bringing effective capacity to 12 and capping scheduled demand at 12.
* **Visual Elements:**
  * Stacked or grouped bar chart showing technician hours/headcount per week.
  * Bold horizontal red threshold line indicating the hard 8-person on-site accommodation/safety limit.
  * Visual annotation indicating where smoothing and contract hiring resolved the over-allocation.

---

### Figure 6: $5 \times 5$ Risk Matrix Heatmap & Migration Plot
* **File:** `figures/risk_matrix.pdf`
* **Target Section:** Section 6.2 (Risk Analysis & Residual Migration)
* **Objective:** Plot all 18 campaign risks on a standard $5 \times 5$ probability-impact grid, displaying arrows showing pre-treatment to post-treatment residual risk migration.
* **Data Inputs:**
  * 18 project risks mapped from Table 6.1 (e.g., R-01 from (3,5) to (1,3); R-04 from (4,3) to (2,2); R-09 from (2,5) to (1,4)).
* **Visual Elements:**
  * $5 \times 5$ heatmap grid with standard risk severity shading (Green for Low, Yellow for Moderate, Amber for High, Red for Critical).
  * Labeled scatter points representing Risk IDs (e.g., *R-01*, *R-04*).
  * Directional arrows connecting initial risk positions to residual positions, demonstrating how engineering mitigations reduce risk exposure below the proactive response threshold.

---

### Figure 7: Earned Value Management (EVM) Variance Dashboard
* **File:** `figures/evm_dashboard.pdf`
* **Target Section:** Section 7.5 (EVM Framework & Performance Thresholds)
* **Objective:** Display simulated performance tracking curves ($PV, EV, AC$) and index trajectories ($SPI, CPI$) relative to Green, Amber, and Red control boundaries.
* **Data Inputs:**
  * Timeline: Reporting Weeks 1 to 14.
  * Tracking curves: Planned Value ($PV$), Earned Value ($EV$), and Actual Cost ($AC$) tracking closely with minor realistic variance.
  * Index tracking: $SPI$ and $CPI$ plotted between $0.85$ and $1.10$.
  * Fixed threshold zones:
    * Green Tier: $0.95 \le \text{Index} \le 1.05$ (Nominal)
    * Amber Tier: $0.90 \le \text{Index} < 0.95$ (Warning / Recovery Plan required)
    * Red Tier: $\text{Index} < 0.90$ (Critical Breach / Stop Work)
* **Visual Elements:**
  * Dual-panel layout:
    * Upper panel: Currency tracking ($PV$ vs. $EV$ vs. $AC$ in AUD) over project weeks.
    * Lower panel: Performance Indices ($CPI$ and $SPI$) over time with background shaded horizontal bands for Green, Amber, and Red control tiers.

---

## 3. LaTeX Inclusion Checklist

When compiling sections, ensure every figure matches this standard LaTeX embedding pattern:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=\linewidth]{figures/[filename].pdf}
    \caption{[Comprehensive caption explaining what the figure proves]}
    \label{fig:[section]_[name]}
\end{figure}