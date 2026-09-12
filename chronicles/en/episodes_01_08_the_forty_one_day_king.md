# 🏛️ Episodes 01–08: The 41-Day Baseline & The Eagle King
*(Evaluation Window: Anchored at 2026-07-03 inception NAV 1.0000; covers 41 trading days up to 2026-08-28 close)*

> **Phase Classification**: **Retrospective Backtest Baseline (Fixed Historical Weights)**  
> **Executable Universe Benchmark**: Taotie (`1.0000` $\to$ `0.9928`, Cumulative -0.72%)  
> *(A capital-constrained, round-lot-constrained full-universe portfolio designed to approximate broad exposure with minimal active selection; utilizing greedy waterfall allocation across 500k capital to hold ~205 stocks with near-zero idle cash)*  
> **Summary**: High selection intensity variants gained strong upside in this period. `CONTESTANT_B_eagle-5-1` finished the baseline at **+19.71%**, while delayed-signal Sloths also retained positive performance.

---

## I. Nature of the Evaluation: Retrospective Backtest

This 41-day baseline covers the opening 8 weeks of the tournament calendar (Episodes 01–08):

* **Retrospective Execution**: The simulation for these 41 trading days was conducted after July and August market data was already known. While the underlying model candidates had their training data cut off prior to June 30, 2026, the selection of models, execution handlers, and testbed parameters was performed with full knowledge of the market environment during this period.
* **Purpose**: This phase serves as a standardized backtest baseline to establish initial contestant positions, cash balances, and behavioral fingerprints before forward tracking begins.
* **Transition to Prospective Tracking & Cryptographic Provenance**: From the August 28 close onward, the evaluation transitions to prospective forward tracking (beginning with Episode 09). Evaluation results packages are sealed under SHA-256 cryptographic digests upon cycle completion for institutional anti-tampering embargo periods prior to public unlock (which proves zero modification during the embargo window, rather than serving as a pre-market prediction digest).

---

## II. The Battlefield: Leaderboard Standings & The Coronation

Across the 41-day baseline stretch, the executable universe benchmark (**Taotie**) ground through choppy terrain under its finite-capital and round-lot constraints, ending at `0.9928` (**-0.72%**). Under greedy waterfall allocation, Taotie held ~205 constituent stocks with ~0.02% idle cash, accurately reflecting equal-weighted market drag.

Yet among the 168 living execution paths battling inside the Zoo, strategies with elevated selection intensity unlocked remarkable upside leverage:

```text
[Cumulative NAV Top 5 Standings as of August 28, 2026 (41 Trading Days)]
🥇 CONTESTANT_B_eagle-5-1 : NAV 1.1971 (+19.71%, +20.43pp vs executable Taotie benchmark)
🥈 CONTESTANT_A_eagle-11-2: NAV 1.1468 (+14.68%, +15.40pp vs executable Taotie benchmark)
🥉 CONTESTANT_B_sloth-1   : NAV 1.1438 (+14.38%, +15.10pp vs executable Taotie benchmark)
🎖️ CONTESTANT_A_rabbit-1  : NAV 1.1313 (+13.13%, +13.85pp vs executable Taotie benchmark)
🎖️ CONTESTANT_D_rabbit-1  : NAV 1.1247 (+12.47%, +13.19pp vs executable Taotie benchmark)
```

### The Crowning of the Eagle King
Pioneered under the `CONTESTANT_B` banner, **`CONTESTANT_B_eagle-5-1`** soared to **NAV `1.1971` (+19.71%)**, generating a staggering **20.43 percentage points of excess return** over the executable universe benchmark (Taotie).

* **Short-Window Caveat**: Over this 41-day run, the Eagle posted an annualized Sharpe ratio of `2.64` with a maximum drawdown of just `-2.41%`. Spectacular short-window metrics in trending regimes must never be confused with long-horizon structural invariance.

---

## III. Execution Zoo Autopsy: Dual Resonances in a Summer Tailwind

### 1. The Eagles (High Selection Intensity)
* **Mechanistic Fact (Level A)**: `eagle-5-1` concentrates its capital into the top 5 predicted assets (Top 5 quantile, Drop 1), exerting the highest selection intensity in the tournament.
* **Attribution Hypothesis (Level B)**: In a persistent trending market, concentrating capital into the top 5 positions amplifies both exposure to the model signal and idiosyncratic concentration risk (magnifying both genuine signal and concentrated luck). Whatever the underlying macro driver, the Eagle King firmly claimed the crown.

### 2. The Sloths (Signal Delay Stress-Testing)
* **Mechanistic Fact (Level A)**: `sloth-1` deliberately delays the incoming model prediction signal by one full rebalance cycle before executing, yet still delivered an NAV of `1.1438` (Rank 3 overall).
* **Attribution Hypothesis (Level B)**: This observation is consistent with relatively slow signal decay over this window; a one-cycle delayed ranking retained substantial economic value. Note that Sloth mechanics combine signal delay with portfolio-path inertia and cash drag (Sloth variants hold substantial uninvested cash during delay windows). A rigorous claim of an extended pure prediction half-life would require cross-sectional verification across the full Sloth-1/2/3/4 lag gradient.

> **Tactical Takeaway**: When market trends persist and signal decay is slow, elevating selection intensity (Eagle) and harvesting delayed alpha (Sloth) both captured significant upside during this period.

---

## IV. The Null Court: Monte Carlo Jurisdiction & Multiple Testing

To determine whether the Eagle King represents genuine predictive skill or an artifact of concentrated luck, we summoned `CONTESTANT_B_eagle-5-1` before its **matched null colony of 1,000 deterministic pseudo-random monkeys** (identical TopK=5, DropN=1 rules, lot constraints, and capital frictions, with zero ranking signal):

> *Note on Monkey Architecture*: Arena simulates 11,000 total monkeys across 11 unique matched portfolio-rule specifications (1,000 monkeys each). Because pseudo-random ranking completely strips out model identity, contestants sharing identical portfolio mechanics share the same matched null colony. Contestants are strictly judged against their own matched colony, not an aggregated pool.

### 1. The Direct Verdict (Level A)
* Across 1,000 matched random simulations, **exactly 0 monkeys outperformed the Eagle King**.
* Under standard finite-sample plus-one correction:
  $$p_{\text{upper}} = \frac{0 + 1}{1000 + 1} = \frac{1}{1001} \approx 0.000999 \approx 0.001$$
* The strategy lands in the **`>99.9%` empirical percentile** (rendered in the UI as `>99.9%`, reflecting the finite simulation size of 1,000 runs). Individual test significance against the matched random baseline is strong.

### 2. Multiple Testing Sensitivity (The Jurisdictional Boundary)
Because `eagle-5-1` was selected as the best among 168 living tournament variants, its raw $p$-value cannot be interpreted as an unselected discovery.

If we conduct a limited sensitivity analysis applying a distribution-free **Bonferroni upper bound** treating the 168 explicitly enumerated execution paths as a single family:
$$168 \times 0.000999 \approx 0.168 > 0.05$$

**The Bonferroni-adjusted $p$-value exceeds 0.05.**

Key methodological nuances:
1. **Monte Carlo Resolution Limitation**: With $N=1,000$ matched monkeys, the minimum reportable empirical $p$-value is $1 / 1001 \approx 0.001$. Across 168 actively tracked variants, an uncorrected $p \approx 0.001$ multiplied by 168 mathematically cannot reach a family-wise 0.05 significance threshold. This represents a known resolution limit of finite matched simulation rather than a mandate to arbitrarily inflate monkey count.
2. **Unadjusted Researcher Degrees of Freedom**: Importantly, this 168-path calculation is only a narrow sensitivity check bounded to the actively tracked paths on the leaderboard. It does **not** represent an adjustment for the broader space of retrospective researcher degrees of freedom—such as prior model candidate screening, Zoo animal taxonomy design, or parameter grid formulation. In any retrospective backtest setting, multiple testing goes far beyond the enumerated paths on the leaderboard.

---

## V. The Cliffhanger: Clouds on the Horizon

As of Friday, August 28, 2026, the Eagle King's tournament record stood supreme:
> **41 Trading Days: Cumulative +19.71% (+17.39pp vs Benchmark); 0 / 1,000 matched monkeys exceeded it (p ≈ 0.001).**

Yet beneath the golden armor of extreme concentration lurks structural fragility. High selection intensity cuts both ways: what happens when steady summer tailwinds vanish overnight? When factor correlations invert and volatility spikes, can a top-heavy predator maneuver?

The throne has been claimed, but the real storm is about to break.

---

> **Please do not feed the models.**  
> **The monkeys are already inside. The zoo is open.**
