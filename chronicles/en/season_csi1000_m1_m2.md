# 🏛️ Month 01–02: The Baseline & Small-Cap Sloth Dominance

> **Evaluation Window**: Anchored at 2026-07-03 inception NAV 1.0000; covers 41 trading days up to 2026-08-28 close (Months 1 & 2 Combined Baseline).  
> **Tournament Phase**: **Retrospective Backtest Calibration (Fixed Historical Weights)**  
> **Executable Universe Benchmark**: Taotie 1000 (`1.0000` $\to$ `0.9471`, Cumulative **-5.29%**; full 51d horizon NAV `0.9160`, **-8.40%**).  
> **Market Index Benchmark**: CSI 1000 Index (`SH000852`, Cumulative **-12.91%**).  
> *(Under standardized CNY 2,000,000 capital and strict 100-share round-lot trading constraints across the 1,000 small-cap stock universe, utilizing greedy waterfall allocation to achieve ~99.9% capital utilization across 870 equities).*  
> **Core Narrative**: Confronted with a brutal -12.91% collapse in the small-cap index, delayed-signal Sloth containers captured top honors (+13.43% led by `CONTESTANT_B_sloth-2`). However, a rigorous methodological autopsy reveals that Sloth's headline returns bundle two distinct phenomena: a massive **Cash Shield effect** (holding 100% risk-free cash during July's steep initial market drawdown) and genuine slow-decay selection alpha. Comparing Sloth against the full-exposure **Snail (蜗牛)** control group (+2.49% to +4.88%) cleanly separates unearned beta avoidance from true small-cap alpha.

---

## I. Nature of the Evaluation: Small-Cap Alpha & Frictional Realities

This 41-day opening baseline covers the combined Month 1 and Month 2 evaluation window (Weeks 1 to 8):

* **Monthly Reporting Cadence**: Unlike Season 01 (CSI 300) which follows weekly episodic dispatches (`Episodes 01–08`, `Episode 09`, ...), the broader-cap testbeds follow a monthly cadence: the initial baseline covers Month 01 and Month 02 combined (`M1–M2`), with subsequent dispatches updated monthly as `M3`, `M4`, and beyond.
* **Retrospective Calibration**: Simulated retrospectively across the 1,000 small-cap constituent universe using model candidate weights frozen prior to June 30, 2026.
* **Why Combine Months 1 and 2**: Months 1 and 2 represent the foundational backtest calibration to measure capital constraints, lot-size indivisibility, and signal half-life under finite CNY 2,000,000 capital. Evaluating them as a combined 41-day retrospective block (`M1–M2`) ensures an empirically sound baseline before forward prospective cycles.
* **The Small-Cap Crucible**: The CSI 1000 represents the growth and speculative frontier of Chinese equities. Over July and August 2026, the index suffered an aggressive **-12.91%** drawdown as market liquidity contracted. In this hostile territory, active selection engines faced a severe test of signal durability.

---

## II. The Battlefield: Leaderboard Standings in the 1,000 Universe

The executable full-universe reference benchmark (**Taotie 1000**) closed the calibration baseline at `0.9471` (**-5.29%**, beating the market index by **+7.62 percentage points**). Under greedy waterfall allocation across 2.0M capital, Taotie 1000 holds an average of 870 small-cap equities with negligible idle cash, reflecting real-world equal-weight market friction across the breadth of the small-cap universe.

Yet among the active execution containers, an unexpected champion emerged:

```text
[CSI 1000 Cumulative NAV Top 5 Standings as of August 28, 2026 (41 Trading Days)]
🥇 CONTESTANT_B_sloth-2  : NAV 1.1343 (+13.43%, +26.34pp vs CSI 1000, +18.72pp vs Taotie)
🥈 CONTESTANT_B_sloth-3  : NAV 1.1184 (+11.84%, +24.75pp vs CSI 1000, +17.13pp vs Taotie)
🥉 CONTESTANT_B_sloth-1  : NAV 1.1119 (+11.19%, +24.10pp vs CSI 1000, +16.48pp vs Taotie)
🎖️ CONTESTANT_B_robot    : NAV 1.1098 (+10.98%, +23.89pp vs CSI 1000, +16.27pp vs Taotie)
🎖️ CONTESTANT_A_sloth-2  : NAV 1.1045 (+10.45%, +23.36pp vs CSI 1000, +15.74pp vs Taotie)
```

### The Crowning of the Sloth Kings
In stark contrast to large-cap arenas where agile Rabbits or concentrated Eagles seized the spotlight, the CSI 1000 podium was completely swept by **Sloths**. Under `CONTESTANT_B`, **`sloth-2` (2-week delayed signal)** topped the tournament at **NAV `1.1343` (+13.43%)**, with `sloth-3` taking silver at `+11.84%` and `sloth-1` taking bronze at `+11.19%`.

---

## III. Execution Zoo Autopsy: Disentangling Signal Persistence from the "Cash Shield"

Why did deliberately delaying trading signals produce superior returns in small-cap equities? A naive interpretation attributes this solely to "longer signal half-life." The Zoo's multi-container design allows us to decompose the real drivers.

### 1. 🦥 The Sloth "Cash Shield" Effect vs. Authentic Alpha
* **The Structural Delay Confounder**: Sloth containers delay trading by 1, 2, 3, or 4 weekly cycles. Crucially, during their respective cold-start delay buffers, **Sloths hold 100% cash**:
  * `sloth-1`: Held 100% cash in Week 1 (Mean cash ratio: 12.55%).
  * `sloth-2`: Held 100% cash in Weeks 1–2 (Mean cash ratio: 23.74%).
  * `sloth-3`: Held 100% cash in Weeks 1–3 (Mean cash ratio: 34.69%).
  * `sloth-4`: Held 100% cash in Weeks 1–4 (Mean cash ratio: 45.54%).
* **The Downside Timing Distortion**: During the first 4 weeks (July 2026), the CSI 1000 index experienced its steepest downward slide. By sitting in risk-free cash during the worst phase of the market drop, Sloths enjoyed a massive, unearned **beta-avoidance cushion** (Exposure-Length Bias).

### 2. 🐌 The Snail Control Group: Isolating Full-Exposure Alpha
To test whether Sloth's returns were mere cash timing or real signal persistence, the Arena employs **Snail (蜗牛)** as the explicit exposure-matched control:
* **Snail Mechanism**: Snails enter the market on Day 1 with **full equity exposure** (mean cash ratio < 3%), completely eschewing the cold-start cash buffer, while adopting slow-motion holding inertia.
* **Empirical Results Under CONTESTANT_B**:
  * `snail-1`: Ended at **+4.88%** (mean cash 2.40%).
  * `snail-2`: Ended at **+2.49%** (mean cash 2.96%).
  * `snail-3`: Ended at **+2.17%** (mean cash 3.69%).
  * `snail-4`: Ended at **+1.49%** (mean cash 4.38%).
* **The Decomposition Formula**:
  $$\text{Sloth-2 Outperformance (+13.43%)} = \underbrace{\text{Snail-1 Full-Exposure Alpha (+4.88%)}}_{\text{True Stock Selection Alpha (+17.79pp vs Index)}} + \underbrace{\text{Cash Shield Beta Avoidance (+8.55pp)}}_{\text{Avoided July Drop}}$$
* **Conclusion**: Snail's +4.88% proves that the underlying selection signal generated substantial structural alpha amidst an index collapse (-12.91%). However, the additional +8.5pp in Sloth-2 was fundamentally a cash-timing bonus, not pure stock-picking superiority.

### 3. 🐇 The Rabbits (Friction Fatigue in Small Caps)
* High-turnover Rabbit variants (`rabbit-1` at `+2.15%`, `rabbit-2` at `-3.42%`) lagged behind. In small-cap space, hyperactive weekly turnover incurred cumulative round-lot rounding penalties and bid-ask friction without sufficient weekly signal renewal to compensate.

### 4. 🦅 The Eagles (Microstructure Liquidity Shocks)
* `eagle-5-1` finished at `+1.73%` with a steep `-17.62%` maximum drawdown. Holding just 5 small-cap stocks exposed the portfolio to severe idiosyncratic liquidity shocks when broad-market liquidity dried up in late July.

---

## IV. The Null Court: 1,000 Small-Cap Monkey Colonization

Summoned before its **matched colony of 1,000 deterministic pseudo-random monkeys** operating across the 1,000-stock universe under identical TopK=22, DropN=3, Lag=2 parameters:

* **Colony Median**: The 1,000 random monkeys posted a median return of **`-2.15%`**, closely tracking the general market weakness.
* **Empirical Percentile**: `CONTESTANT_B_sloth-2` (+13.43%) landed in the **`>99.8%` empirical percentile** ($p \approx 0.002$).
* Against 1,000 identical portfolio-rule monkeys, active signal selection demonstrated definitive statistical significance.

---

## V. Baseline Summary

The combined Months 1 & 2 baseline reveals that small-cap alpha behaves according to fundamentally different temporal physics than large-cap alpha: longer signal decay curves reward patient execution.

Subsequent CSI 1000 dispatches will be published on a monthly (4-week) cadence.

> **Please do not feed the models.**  
> **The small-cap zoo is open.**
