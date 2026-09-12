# 🏛️ Episodes 01–08: The M1–M2 Baseline & Small-Cap Sloth Dominance

> **Evaluation Window**: Anchored at 2026-07-03 inception NAV 1.0000; covers 41 trading days up to 2026-08-28 close (Months 1 & 2 Combined Baseline).  
> **Tournament Phase**: **Retrospective Backtest Calibration (Fixed Historical Weights)**  
> **Executable Universe Benchmark**: Taotie 1000 (`1.0000` $\to$ `1.0165`, Cumulative +1.65%).  
> **Market Index Benchmark**: CSI 1000 Index (`SH000852`, Cumulative **-12.91%**).  
> *(Under standardized CNY 500,000 capital and strict 100-share round-lot trading constraints across the 1,000 small-cap stock universe).*  
> **Core Narrative**: Confronted with a brutal -12.91% collapse in the small-cap index, the tournament revealed a profound structural insight: delayed-signal Sloth containers dominated the field, capturing +13.43% led by `CONTESTANT_B_sloth-2`. Small-cap alpha demonstrated extended signal persistence, rewarding patient inertia over hyperactive turnover.

---

## I. Nature of the Evaluation: Small-Cap Alpha & Frictional Realities

This 41-day opening baseline covers the combined Month 1 and Month 2 evaluation window (Weeks 1 to 8):

* **Retrospective Calibration**: Simulated retrospectively across the 1,000 small-cap constituent universe using model candidate weights frozen prior to June 30, 2026.
* **Why Combine Months 1 and 2**: Months 1 and 2 represent the foundational backtest calibration to measure capital constraints, lot-size indivisibility, and signal half-life under finite CNY 500,000 capital. Evaluating them as a combined 41-day retrospective block ensures an empirically sound baseline before forward prospective cycles.
* **The Small-Cap Crucible**: The CSI 1000 represents the growth and speculative frontier of Chinese equities. Over July and August 2026, the index suffered an aggressive **-12.91%** drawdown as market liquidity contracted. In this hostile territory, active selection engines faced a severe test of signal durability.

---

## II. The Battlefield: Leaderboard Standings in the 1,000 Universe

The executable full-universe reference benchmark (**Taotie 1000**) demonstrated outstanding downside insulation, finishing at `1.0165` (**+1.65%**, beating the market index by **+14.56 percentage points**).

Yet among the active execution containers, an unexpected champion emerged:

```text
[CSI 1000 Cumulative NAV Top 5 Standings as of August 28, 2026 (41 Trading Days)]
🥇 CONTESTANT_B_sloth-2  : NAV 1.1343 (+13.43%, +26.34pp vs CSI 1000, +11.78pp vs Taotie)
🥈 CONTESTANT_B_sloth-3  : NAV 1.1184 (+11.84%, +24.75pp vs CSI 1000, +10.19pp vs Taotie)
🥉 CONTESTANT_B_sloth-1  : NAV 1.1119 (+11.19%, +24.10pp vs CSI 1000, +9.54pp vs Taotie)
🎖️ CONTESTANT_B_robot    : NAV 1.1098 (+10.98%, +23.89pp vs CSI 1000, +9.33pp vs Taotie)
🎖️ CONTESTANT_A_sloth-2  : NAV 1.1045 (+10.45%, +23.36pp vs CSI 1000, +8.80pp vs Taotie)
```

### The Crowning of the Sloth Kings
In stark contrast to large-cap arenas where agile Rabbits or concentrated Eagles seized the spotlight, the CSI 1000 podium was completely swept by **Sloths**. Under `CONTESTANT_B`, **`sloth-2` (2-week delayed signal)** topped the tournament at **NAV `1.1343` (+13.43%)**, with `sloth-3` taking silver at `+11.84%` and `sloth-1` taking bronze at `+11.19%`.

---

## III. Execution Zoo Autopsy: Why Delayed Signals Won in Small Caps

Why did deliberately delaying trading signals by 1 to 3 weeks produce superior returns in small-cap equities?

### 1. 🦥 The Sloths (Informational Inefficiency & Extended Half-Life)
* **Mechanistic Fact**: Sloth variants deliberately lag incoming model prediction signals by 1, 2, 3, or 4 weekly cycles before rebalancing, while also holding uninvested cash during delay periods.
* **Economic Attribution**:
  * **Slower Price Discovery**: Small-cap equities have sparse sell-side analyst coverage and lower institutional participation. Mispricings discovered by multi-factor models take multiple weeks to fully correct, resulting in a substantially longer alpha half-life compared to heavily arbitrated large caps.
  * **Turnover Friction Immunity**: Rebalancing every week in small caps incurs significant transaction costs, wider bid-ask spreads, and market impact. By slowing down portfolio churn, Sloths avoided friction drag while allowing slow-moving structural alpha to mature.
* **Controlled Pairwise Comparison**:
  * Under `CONTESTANT_B`: Robot (0 delay) delivered `+10.98%`.
  * `sloth-1` (1-week delay) delivered `+11.19%`.
  * `sloth-2` (2-week delay) delivered `+13.43%` (**+2.45pp higher than real-time Robot!**).
  * `sloth-3` (3-week delay) delivered `+11.84%`.
  * Only at `sloth-4` (4-week delay) did decay begin to erode returns (`+8.52%`).

### 2. 🐇 The Rabbits (Friction Fatigue in Small Caps)
* High-turnover Rabbit variants (`rabbit-1` at `+7.85%`, `rabbit-2` at `+6.92%`) underperformed Sloths. In small-cap space, hyperactive weekly turnover incurred cumulative commission drag and round-lot rounding penalties without corresponding signal improvement.

### 3. 🦅 The Eagles (Liquidity Shocks in Micro Holdings)
* `eagle-5-1` finished at `+7.90%`, but suffered a maximum drawdown of `-5.84%`. Holding just 5 small-cap stocks exposed the portfolio to extreme idiosyncratic shocks. When market liquidity dried up in August, concentrated single-name pullbacks hit Eagle portfolios hard.

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
