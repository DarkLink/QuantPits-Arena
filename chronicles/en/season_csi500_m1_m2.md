# 🏛️ Month 01–02: The Baseline & The Mid-Cap Rabbit Surge

> **Evaluation Window**: Anchored at 2026-07-03 inception NAV 1.0000; covers 41 trading days up to 2026-08-28 close (Months 1 & 2 Combined Baseline).  
> **Tournament Phase**: **Retrospective Backtest Calibration (Fixed Historical Weights)**  
> **Executable Universe Benchmark**: Taotie 500 (`1.0000` $\to$ `0.9472`, Cumulative -5.28% at 41-day baseline; -8.75% across full 51-day horizon).  
> **Market Index Benchmark**: CSI 500 Index (`SH000905`, Cumulative **-12.49%**).  
> *(Under standardized CNY 1,000,000 capital and strict 100-share round-lot trading constraints with greedy waterfall allocation across the 500 mid-cap stock universe).*  
> **Core Narrative**: While the mid-cap index endured a severe -12.49% market drawdown, the executable Taotie reference absorbed a milder -5.28% pullback (+7.21pp over the index), actively covering 403 equities through greedy waterfall allocation. High-refresh Rabbit handlers capitalized on heightened cross-sectional dispersion, generating nearly +10% absolute returns led by `CONTESTANT_B_rabbit-1` (+9.98%).

---

## I. Nature of the Evaluation: Retrospective Calibration Across Mid-Cap Dispersion

This 41-day opening baseline covers the combined Month 1 and Month 2 evaluation window (Weeks 1 to 8):

* **Monthly Reporting Cadence**: Unlike Season 01 (CSI 300) which follows weekly episodic dispatches (`Episodes 01–08`, `Episode 09`, ...), the broader-cap testbeds follow a monthly cadence: the initial baseline covers Month 01 and Month 02 combined (`M1–M2`), with subsequent dispatches updated monthly as `M3`, `M4`, and beyond.
* **Retrospective Calibration**: The evaluation over this 41 trading-day period was conducted post-hoc with knowledge of July and August market data. The 6 core contestant candidate architectures had training data frozen prior to June 30, 2026, but the execution container parameters and testbed calibrations were verified retrospectively against known mid-cap market dynamics.
* **Why Combine Months 1 and 2**: Because both months serve as the calibration baseline to measure execution frictions, capital granularity, and behavioral container mechanics before forward live tracking begins, they are evaluated as a cohesive 41-day foundation (`M1–M2`) rather than artificially split.
* **The Mid-Cap Market Regime**: Unlike large-cap stability, the CSI 500 universe experienced severe downward pressure during this window, with the benchmark index falling **-12.49%**. This challenging environment created an exceptional laboratory for evaluating whether alpha models could extract active returns amidst broader market attrition.

---

## II. The Battlefield: Leaderboard Standings in Mid-Cap Space

Across the 41-day stretch, the executable reference portfolio (**Taotie 500**) demonstrated equal-weight defensive cushioning against the index decline, closing at `0.9472` (**-5.28%**, generating +7.21pp of active protection over the raw CSI 500 index).

Inside the Zoo, execution containers with agile rebalancing capabilities thoroughly decoupled from the market downturn:

```text
[CSI 500 Cumulative NAV Top 5 Standings as of August 28, 2026 (41 Trading Days)]
🥇 CONTESTANT_B_rabbit-1  : NAV 1.0998 (+9.98%, +22.47pp vs CSI 500, +15.26pp vs Taotie)
🥈 CONTESTANT_B_rabbit-2  : NAV 1.0939 (+9.39%, +21.88pp vs CSI 500, +14.67pp vs Taotie)
🥉 CONTESTANT_B_eagle-5-1 : NAV 1.0905 (+9.05%, +21.54pp vs CSI 500, +14.33pp vs Taotie)
🎖️ CONTESTANT_B_whale-shark: NAV 1.0893 (+8.93%, +21.42pp vs CSI 500, +14.21pp vs Taotie)
🎖️ CONTESTANT_A_rabbit-1  : NAV 1.0877 (+8.77%, +21.26pp vs CSI 500, +14.05pp vs Taotie)
```

### The Triumph of Agile Execution
Under `CONTESTANT_B`, **`rabbit-1`** surged to **NAV `1.0998` (+9.98%)**, closely followed by **`rabbit-2` (+9.39%)**. In a universe where 72% of mid-cap assets lost value, these agile variants captured an astounding **+22.47 percentage points of alpha over the benchmark**.

---

## III. Execution Zoo Autopsy: Why Rabbits Dominated Mid-Cap Space

The 500-stock universe possesses structural characteristics distinct from large-cap indices: wider valuation dispersion, lower institutional crowding, and higher cross-sectional turnover opportunities.

### 1. 🐇 The Rabbits (Decisive Rebalancing in Dispersed Markets)
* **Mechanistic Fact**: Rabbit variants feature high turnover quotas (DropN=11 or 22). When market momentum is choppy or downward-trending, stagnant stocks quickly deteriorate. Rabbits aggressively purged declining names every Monday morning, constantly reallocating capital into top-ranked candidates.
* **Controlled Pairwise Comparison**:
  * Baseline Robot (DropN=3) achieved `+4.12%` under `CONTESTANT_B`.
  * Rabbit-1 (DropN=11) delivered `+9.98%` (+5.86pp higher than Robot).
  * Rabbit-2 (DropN=22) delivered `+9.39%` (+5.27pp higher than Robot).
* **Takeaway**: In declining mid-cap regimes, active portfolio agility acts as an essential risk-clearing mechanism rather than an unnecessary transaction drag.

### 2. 🦅 The Eagles (High Concentration Resilience & Volatility)
* `eagle-5-1` finished third overall at `+9.05%`. However, holding only 5 mid-cap stocks exposed the portfolio to sharp localized intraday volatility, suffering a maximum drawdown of `-4.12%` compared to just `-1.85%` for Rabbit-1.
* In mid-cap space, concentration carries heightened idiosyncratic risk due to wider bid-ask spreads and liquidity variation.

### 3. 🦥 vs 🐌 The Sloths & Snails: Cash Shield vs. Sluggish Turnover
* While `sloth-1` (+6.07%) delivered positive absolute returns, its performance was bolstered by holding 100% cash during the initial week when the CSI 500 benchmark fell steeply.
* In contrast, **Snail-1 (蜗牛)** maintained full equity exposure from Day 1 (mean cash 2.11%), achieving **+3.52%** (+16.01pp over the -12.49% index). Snail's positive return confirms robust mid-cap selection alpha without timing assistance, while demonstrating that Sloth's additional margin was partly driven by the unearned cash shield during the early July slide. As signal latency lengthened to 4 weeks, Sloth returns collapsed to -3.35%, illustrating rapid factor half-life decay in mid caps.

---

## IV. The Null Court: 1,000 Mid-Cap Monkey Colonization

To determine whether the Mid-Cap Rabbit's +9.98% return was statistically distinguishable from luck under finite capital constraints, we summoned `CONTESTANT_B_rabbit-1` before its **colony of 1,000 deterministic pseudo-random monkeys** operating on the identical CSI 500 universe with identical TopK=22, DropN=11 execution rules:

* **Colony Median**: The 1,000 matched random monkeys produced a median return of **`-1.42%`** over the 41-day window.
* **Empirical Percentile**: `CONTESTANT_B_rabbit-1` (+9.98%) landed in the **`>99.5%` empirical percentile** ($p \approx 0.005$).
* **Multiple Testing Sensitivity**: With 168 living execution paths in the arena, applying a conservative Bonferroni upper bound ($168 \times 0.005 = 0.84 > 0.05$) indicates that while individual superiority against pure random selection is pronounced, cross-sectional selection among many variants requires caution against selection bias.

---

## V. Baseline Summary & Transition

The combined Months 1 & 2 baseline proves that quantitative alpha models developed on standardized features remain potent inside the mid-cap universe, successfully decoupling from a double-digit index drop.

Subsequent evaluation updates for CSI 500 will follow a 4-week institutional monthly cadence.

> **Please do not feed the models.**  
> **The mid-cap zoo is open.**
