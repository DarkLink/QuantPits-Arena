# 🏛️ Episode 10: The Apex Strike & The 1.20 Milestone

> **Evaluation Window**: Anchored at 2026-09-04 close; prospective evaluation cycle covers 2026-09-07 ~ 2026-09-11 (5 trading days, Days 47 ~ 51 of the tournament calendar).  
> **Tournament Phase**: **Prospective Forward Tracking (Cycle 2, Week 10)**  
> **Executable Universe Benchmark**: Taotie (`0.9906` $\to$ `0.9685`, weekly return -2.23%, cumulative -3.15%).  
> *(Capital-constrained CNY 500,000, 100-share round-lot full-universe reference portfolio under greedy waterfall allocation).*  
> **Market Index Benchmark**: CSI 300 (`-6.07%` $\to$ `-6.86%`, weekly return -0.84%).  
> **Core Narrative**: Facing a persistent downward drift in broad equities, high-selection intensity Eagles mounted a ferocious counter-strike. `CONTESTANT_A_eagle-5-1` led the entire tournament with **+4.38%** on the week, while reigning champion `CONTESTANT_B_eagle-5-1` (+2.06%) became the first strategy in tournament history to breach the **1.20 NAV milestone (+20.71%)**, expanding its tournament lead to **5.51 percentage points**.

---

> ### 💡 Cycle Core Epiphany
> **Episode 09 demonstrated**: Agile rotation (Rabbit) swiftly adapts when cross-sectional dispersion explodes and prior leaders suffer breadth pullbacks.  
> **Episode 10 proves**: When market direction shifts back into a steady contraction regime, high-conviction concentration (Eagle) re-exerts devastating precision. The apex predator reclaimed the battlefield, while inverse-alpha containers (Koala) suffered massive single-week drawdowns.

---

## I. Market Backdrop: Drift, Contraction, and Factor Divergence

During the 10th tournament week (2026-09-04 Friday close to 2026-09-11 Friday close), broader equity markets continued to slip under macroeconomic pressure:

```text
[Daily Path Average vs Executable Taotie Benchmark: Sep 07 – Sep 11]
• 09-07 (Mon): Taotie -0.77% | Broad market gap-down; defensive containers hold
• 09-08 (Tue): Taotie +0.28% | Choppy consolidation; high-rank assets diverge
• 09-09 (Wed): Taotie +0.32% | Midweek technical rebound; Eagles initiate ascent
• 09-10 (Thu): Taotie -0.61% | Secondary retreat; Koalas and low-percentiles break down
• 09-11 (Fri): Taotie -1.48% | Friday settlement; CONTESTANT_B_eagle-5-1 crowns at 1.2071
```

### 1. Empirical Observations (Level A: Directly Proved by Data)
* **Persistent Benchmark Softening**:
  * The CSI 300 benchmark index (SH000300) retreated another **`-0.84%`**, extending its cumulative tournament deficit to **`-6.86%`**.
  * The executable Taotie universe benchmark fell **`-2.23%`** on the week, closing at `0.9685` (cumulative `-3.15%`).
  * Theoretical equal-weight Ghost Taotie slid **`-1.83%`** to `0.9837` (cumulative `-1.63%`), demonstrating negative broad-market drag on unselected assets.
* **Intra-Zoo Dispersion Explosion**:
  * While the median execution path absorbed a mild weekly slip of `-0.31%`, the spread between the week's top performer (`+4.38%`) and worst casualty (`-5.01%`) stretched to **9.39 percentage points**.
* **The Inverted Alpha Penalty**:
  * Inverse-selection containers (`koala`, selecting bottom-ranked candidates) suffered catastrophic weekly pullbacks across all models (mean `-4.41%` on the week), confirming that bottom-tier model scores experienced heavy idiosyncratic losses.

---

## II. The Battlefield: Weekly Gainers & Casualties

While broad indices drifted lower, apex concentration delivered stunning alpha divergence ($\text{Return} = \text{NAV}_{0911} / \text{NAV}_{0904} - 1$):

### 🏆 Top 5 Weekly Gainers (Week 10)
1. **`CONTESTANT_A_eagle-5-1`**: **`+4.38%`** (NAV `1.0744` $\to$ `1.1215`) — **Rank 1 Overall for the Week**
2. **`CONTESTANT_B_eagle-5-1`**: **`+2.06%`** (NAV `1.1827` $\to$ `1.2071`) — **First Strategy to Cross 1.20 NAV**
3. **`CONTESTANT_A_eagle-11-2`**: **`+1.31%`** (NAV `1.1093` $\to$ `1.1238`)
4. **`CONTESTANT_C_eagle-11-2`**: **`+1.09%`** (NAV `1.0538` $\to$ `1.0653`)
5. **`CONTESTANT_D_eagle-5-1`**: **`+0.50%`** (NAV `1.0933` $\to$ `1.0988`)

### 🩸 Top 5 Weekly Casualties (Week 10)
1. **`CONTESTANT_B_koala`**: **`-5.01%`** (NAV `0.8848` $\to$ `0.8405`)
2. **`CONTESTANT_C_meerkat-70`**: **`-4.42%`** (NAV `0.9363` $\to$ `0.8949`)
3. **`CONTESTANT_C_koala`**: **`-4.35%`** (NAV `0.8968` $\to$ `0.8578`)
4. **`CONTESTANT_D_koala`**: **`-4.31%`** (NAV `0.8623` $\to$ `0.8251`)
5. **`CONTESTANT_A_koala`**: **`-3.94%`** (NAV `0.8830` $\to$ `0.8482`)

---

## III. Execution Zoo Autopsy: Re-coronation of the Apex Predator

```text
[Cumulative NAV Leaderboard as of September 11, 2026 (51 Trading Days)]
🥇 CONTESTANT_B_eagle-5-1 : NAV 1.2071 (+20.71%, +23.86pp vs Taotie benchmark)
🥈 CONTESTANT_D_rabbit-1  : NAV 1.1520 (+15.20%, +18.35pp vs Taotie benchmark)
🥉 CONTESTANT_A_rabbit-1  : NAV 1.1475 (+14.75%, +17.90pp vs Taotie benchmark)
🎖️ CONTESTANT_B_rabbit-1  : NAV 1.1298 (+12.98%, +16.13pp vs Taotie benchmark)
🎖️ CONTESTANT_D_eagle-11-2: NAV 1.1290 (+12.90%, +16.05pp vs Taotie benchmark)
```

### 1. The Eagle King Crosses the 1.20 Threshold
After seeing its crown lead compressed to 1.89pp during Episode 09's Rabbit surge, **`CONTESTANT_B_eagle-5-1`** executed a clinical weekly gain of `+2.06%`, closing Friday at **NAV `1.2071` (+20.71%)**.
* **Lead Expansion**: The gap between the Eagle King and runner-up `CONTESTANT_D_rabbit-1` (+15.20%) dramatically widened from 1.89pp back to **5.51 percentage points**.
* **Sister Eagle Surge**: `CONTESTANT_A_eagle-5-1` gained **`+4.38%`** on the week, validating that top-5 quantile concentration across independent alpha models captured positive idiosyncratic payoff during this window.

### 2. Rabbits Provide Unshakable Foundation
While unable to match the explosive single-week velocity of the top-5 concentrated Eagles, agile Rabbits displayed elite defensive behavior:
* `CONTESTANT_D_rabbit-1` (+0.02% weekly, cum +15.20%) and `CONTESTANT_A_rabbit-1` (+0.38% weekly, cum +14.75%) absorbed the market's -0.94% drag without breaking stride.
* The Rabbit cohort continues to monopolize Ranks 2, 3, and 4 on the cumulative leaderboard, highlighting the trade-off between the Eagle's volatile peak upside and the Rabbit's smooth compound path.

### 3. Snail & Sloth Mechanics: The Cash Shield
* Sloths and Snails maintained mild movements (-0.1% to +0.3% weekly).
* Delayed-signal containers continued to demonstrate how uninvested cash buffers dampen drawdown velocity during persistent market corrections.

---

## IV. Contestant Baseline Integrity: Full Positive Alpha Retention

All 6 candidate models' default canonical execution containers (`robot`, TopK=22, DropN=3) maintained positive cumulative performance against the market:

| Contestant Robot | Weekly Return | Cumulative NAV | Cumulative Return | vs CSI 300 |
| :--- | :---: | :---: | :---: | :---: |
| **`CONTESTANT_B_robot`** | **+0.23%** | **1.1133** | **+11.33%** | **+18.19pp** |
| **`CONTESTANT_D_robot`** | **-0.40%** | **1.0762** | **+7.62%** | **+14.48pp** |
| **`CONTESTANT_A_robot`** | **+0.32%** | **1.0662** | **+6.62%** | **+13.48pp** |
| **`CONTESTANT_C_robot`** | **-0.23%** | **1.0516** | **+5.16%** | **+12.02pp** |
| **`CONTESTANT_F_robot`** | **-1.42%** | **1.0313** | **+3.13%** | **+9.99pp** |
| **`CONTESTANT_E_robot`** | **-0.97%** | **1.0080** | **+0.80%** | **+7.66pp** |
| *CSI 300 Index* | *-0.84%* | *0.9314* | *-6.86%* | *0.00pp* |

Even in the most challenging regime, all 6 models retain positive absolute cumulative returns and strong double-digit active alpha spreads against the broad market index.

---

## V. Outlook: Week 11 and Beyond

Fifty-one trading days into the Summer 2026 tournament, the field has separated into distinct, mathematically verifiable behavioral regimes:
* **Apex Concentrators (Eagle)**: Capable of generating extraordinary single-week alpha bursts (+4.38%), carrying CONTESTANT_B across the historic 1.20 milestone.
* **Agile Compounders (Rabbit)**: Delivering unyielding stability and commanding the upper podium.
* **Passive Drift vs Execution Friction**: Demonstrating that passive equal-weight exposure (Taotie -3.15%) and market beta (CSI 300 -6.86%) are completely outclassed by dynamic alpha selection.

The tournament marches into Week 11.
