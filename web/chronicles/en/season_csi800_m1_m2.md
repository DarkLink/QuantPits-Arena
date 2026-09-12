# 🏛️ Month 01–02: The Baseline & Broad-Cap Rabbit Supremacy

> **Evaluation Window**: Anchored at 2026-07-03 inception NAV 1.0000; covers 41 trading days up to 2026-08-28 close (Months 1 & 2 Combined Baseline).  
> **Tournament Phase**: **Retrospective Backtest Calibration (Fixed Historical Weights)**  
> **Executable Universe Benchmark**: Taotie 800 (`1.0000` $\to$ `0.9625`, Cumulative **-3.75%**; full 51d horizon NAV `0.9307`, **-6.93%**).  
> **Market Index Benchmark**: CSI 800 Index (`SH000906`, Cumulative **-7.90%**).  
> *(Under standardized CNY 1,600,000 capital and strict 100-share round-lot trading constraints across the 800 broad-market stock universe, utilizing greedy waterfall allocation to achieve ~99.9% capital utilization across 634 equities).*  
> **Core Narrative**: Combining large-cap liquidity with mid-cap growth dispersion, the CSI 800 arena delivered outstanding multi-factor alpha. Agile execution handlers crushed the market benchmark by over 20 percentage points, with `CONTESTANT_B_rabbit-2` topping the podium at **+12.84%**.

---

## I. Nature of the Evaluation: Broad-Market Universe Calibration

This 41-day opening baseline covers the combined Month 1 and Month 2 evaluation window (Weeks 1 to 8):

* **Monthly Reporting Cadence**: Unlike Season 01 (CSI 300) which follows weekly episodic dispatches (`Episodes 01–08`, `Episode 09`, ...), the broader-cap testbeds follow a monthly cadence: the initial baseline covers Month 01 and Month 02 combined (`M1–M2`), with subsequent dispatches updated monthly as `M3`, `M4`, and beyond.
* **Retrospective Calibration**: Simulated retrospectively across the 800 constituent universe (CSI 300 large caps + CSI 500 mid caps) using model candidate weights frozen prior to June 30, 2026.
* **Why Combine Months 1 and 2**: Establishing a unified 41-day baseline provides a robust statistical baseline across two full monthly rebalance cycles (`M1–M2`) without premature mid-course noise.
* **The Broad-Cap Opportunity Spectrum**: The CSI 800 index represents roughly 70% of total Chinese equity capitalization. Over July and August 2026, the broad market fell **-7.90%**, as defensive mega-caps diverged sharply from cyclical mid-caps. This cross-sector polarization created rich fertile ground for quantitative sorting engines.

---

## II. The Battlefield: Leaderboard Standings across the 800 Universe

The executable full-universe reference benchmark (**Taotie 800**) ended the calibration baseline at `0.9625` (**-3.75%**, outperforming the market index by +4.15pp). Under greedy waterfall allocation, Taotie 800 holds an average of 634 constituent equities with near-zero idle cash, accurately capturing equal-weighted market friction across large and mid caps.

Among the active execution paths, aggressive turnover handlers unlocked substantial active returns:

```text
[CSI 800 Cumulative NAV Top 5 Standings as of August 28, 2026 (41 Trading Days)]
🥇 CONTESTANT_B_rabbit-2   : NAV 1.1284 (+12.84%, +20.74pp vs CSI 800, +16.59pp vs Taotie)
🥈 CONTESTANT_B_rabbit-1   : NAV 1.0984 (+9.84%, +17.74pp vs CSI 800, +13.59pp vs Taotie)
🥉 CONTESTANT_B_whale-shark : NAV 1.0830 (+8.30%, +16.20pp vs CSI 800, +12.05pp vs Taotie)
🎖️ CONTESTANT_A_rabbit-2   : NAV 1.0821 (+8.21%, +16.11pp vs CSI 800, +11.96pp vs Taotie)
🎖️ CONTESTANT_D_rabbit-2   : NAV 1.0805 (+8.05%, +15.95pp vs CSI 800, +11.80pp vs Taotie)
```

### The Crowning of the Broad-Cap Rabbit King
Pioneered under `CONTESTANT_B`, **`rabbit-2`** vaulted to **NAV `1.1284` (+12.84%)**, delivering an extraordinary **20.74 percentage points of excess return** over the CSI 800 market index.

---

## III. Execution Zoo Autopsy: Capital Allocation Across Dual Horizons

The 800-stock universe spans two distinct regimes: high-liquidity large caps and high-beta mid caps. How did different Zoo handlers navigate this blended territory?

### 1. 🐇 The Rabbits (Optimal Trade Execution in Large Universes)
* **Mechanistic Fact**: With 800 assets to choose from, model ranking scores spread across a wider distribution. Rabbit-2 (DropN=22) rotates through the top tier with maximum agility, capturing fast-moving momentum shifts between mega-cap leaders and mid-cap breakouts.
* **Controlled Pairwise Comparison**:
  * Baseline Robot (DropN=3) achieved `+5.18%` under `CONTESTANT_B`.
  * Rabbit-1 (DropN=11) delivered `+9.84%`.
  * Rabbit-2 (DropN=22) delivered `+12.84%` (+7.66pp over Robot).
* In broad universes, portfolio turnover friction is easily absorbed by abundant liquidity, while signal freshness yields massive compounding advantages.

### 2. 🐋 The Whale-Shark (Capacity-Scaled Robustness)
* `whale-shark` finished third overall at `+8.30%`. Designed to test wider portfolio breadth with controlled turnover, it demonstrated remarkable resilience, navigating the 41-day run with a maximum drawdown of only `-2.15%`.

### 3. 🦅 The Eagles (Concentration vs Diversification Balance)
* Unlike in CSI 300 where `eagle-5-1` captured Rank 1 (+19.71%), in the 800 universe `eagle-5-1` placed 6th (+7.95%). The vast opportunity set in CSI 800 meant that selecting only 5 stocks missed valuable breadth advantages, allowing well-diversified Rabbits (TopK=22) to take the crown.

### 4. 🦥 vs 🐌 The Sloths & Snails: Cash Shield Disentanglement
* Sloth variants (`sloth-1` at `+5.27%`, `sloth-2` at `+4.36%`) recorded positive returns partly through their initial cold-start cash buffer during July's broad-market drawdown (-7.90%).
* The exposure-matched control **Snail-1 (蜗牛)** held equities continuously (mean cash 2.56%), delivering **+2.37%** (+10.27pp over the falling index). This isolates genuine full-exposure alpha from the timing buffer, proving that model stock selection added positive value even when turnover was deliberately suppressed.

---

## IV. The Null Court: Monte Carlo Jurisdiction

Subjected to the **colony of 1,000 matched pseudo-random monkeys** operating across the CSI 800 universe under identical TopK=22, DropN=22 rules:

* **Colony Median**: The 1,000 random monkeys posted a median return of **`-0.85%`**.
* **Empirical Percentile**: `CONTESTANT_B_rabbit-2` (+12.84%) placed in the **`>99.8%` empirical percentile** ($p \approx 0.002$).
* Even after accounting for finite-sample Monte Carlo constraints, active signal selection proved definitively superior to random broad-market exposure.

---

## V. Baseline Summary

The Months 1 & 2 baseline confirms that broad-cap universes provide an ideal balance of liquidity and dispersion, allowing high-refresh alpha strategies to excel.

Subsequent CSI 800 dispatches will update on a monthly (4-week) cadence.

> **Please do not feed the models.**  
> **The broad-cap zoo is open.**
