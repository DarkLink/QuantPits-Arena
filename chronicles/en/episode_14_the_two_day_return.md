# 🏛️ Episode 14: The Two-Day Return — The Same Holdings, a Wider Crown

> **Return anchor**: September 30 close.<br />
> **Valuation window**: October 8–9, 2026, 2 trading sessions; 65 cumulative NAV observations including the July 3 anchor.<br />
> **Execution**: No rebalance on October 8 or 9. Holdings continue from September 28; next scheduled rebalance October 12, using October 9 close.<br />
> **Phase**: Continued forward tracking. A separate dispatch and settlement segment does not mean a new trade. Completed results do not establish a prior cryptographic commitment.

## ⚡ TL;DR

- **No new orders**: the two sessions contain **0** new trades across the **168** contestant paths and **2** independent portfolio benchmarks.
- **Market and baselines**: CSI 300 returned **-0.93%**, ending at NAV **0.8916** (**-10.84%** cumulative); Taotie gained **+0.46%** to **1.0136** (**+1.36%** cumulative).
- **The crown widens**: B's `eagle-5-1` gained **+1.55%**, reaching **1.2240** (**+22.40%** cumulative), with a **7.14pp** lead over D's `rabbit-1`, versus **6.12pp** at September close.
- **Two-day winner**: E's `meerkat-50` gained **+2.02%**, from **0.9447** to **0.9639**; E's `meerkat-60` followed at **+1.74%**.
- **Breadth**: **112/168** paths gained; mean period return **+0.36%**, median **+0.54%**. Daily positive counts were **87/168** on October 8 and **128/168** on October 9.
- **Eagles diverge**: F's concentrated Eagle gained **+1.72%**, A's lost **-1.05%**, and E's lost **-1.90%**, despite the same concentration specification.
- **Robot control**: **5/6** Robots gained; D led period returns at **+1.11%**, while B remained their cumulative leader at NAV **1.1159** (**+11.59%**).
- **Cumulative null court**: the champion's matched median was **-3.80%**, raw plus-one **p = 0.0020**, percentile **99.8%**; its cumulative maximum drawdown was **7.13%**.

## I. The Holiday Splits the Dispatch, Not the Portfolio

September 28 was the last rebalance. The Monday in the reopening week was a holiday, so execution did not move to Thursday. Both sessions value existing holdings at their closes; holdings, cash and trade records remain unchanged.

| Session | Mean daily return across 168 paths | Positive paths |
| :--- | ---: | ---: |
| October 8 | +0.06% | 87/168 |
| October 9 | +0.30% | 128/168 |

[Episode 13](episode_13_the_three_day_trial.md) ends at September 30; this episode starts from that close. To combine the windows, multiply their gross returns. B's champion gained **+2.41%** from September 24 close through October 9. Adding two rounded percentages would not be the same calculation.

## II. The Two-Day Sprint

| Period rank | Path | Two-day return | Start NAV | End NAV |
| ---: | :--- | ---: | ---: | ---: |
| 1 | CONTESTANT_E_meerkat-50 | +2.02% | 0.9447 | 0.9639 |
| 2 | CONTESTANT_E_meerkat-60 | +1.74% | 0.9947 | 1.0120 |
| 3 | CONTESTANT_F_eagle-5-1 | +1.72% | 1.0142 | 1.0316 |
| 4 | CONTESTANT_D_meerkat-20 | +1.62% | 1.0832 | 1.1008 |
| 5 | CONTESTANT_D_sloth-3 | +1.56% | 0.9626 | 0.9777 |

| Bottom five | Two-day return | End NAV |
| :--- | ---: | ---: |
| CONTESTANT_E_eagle-5-1 | -1.90% | 1.0043 |
| CONTESTANT_C_meerkat-90 | -1.65% | 0.9195 |
| CONTESTANT_E_eagle-11-2 | -1.29% | 0.9905 |
| CONTESTANT_A_meerkat-70 | -1.06% | 0.9402 |
| CONTESTANT_A_eagle-5-1 | -1.05% | 1.0848 |

The period winner remained below initial NAV. Its rebound does not establish a cumulative win or a universal noise-handler advantage. Concentrated Eagles appear among both gainers and casualties.

## III. The Cumulative Crown

| Rank at October 9 | Path | NAV | Cumulative return |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_B_eagle-5-1 | 1.2240 | +22.40% |
| 2 | CONTESTANT_D_rabbit-1 | 1.1526 | +15.26% |
| 3 | CONTESTANT_D_eagle-11-2 | 1.1463 | +14.63% |
| 4 | CONTESTANT_A_rabbit-1 | 1.1399 | +13.99% |
| 5 | CONTESTANT_B_rabbit-1 | 1.1358 | +13.58% |

The cumulative gap grew by approximately **1.02pp**, calculated from unrounded NAV. It is a cumulative-return difference, distinct from the two-day return difference. No trading was needed for the margin to move.

## IV. Robots and Evidence Boundaries

| Robot | Two-day return | End NAV |
| :--- | ---: | ---: |
| A | +0.64% | 1.0575 |
| B | +1.09% | 1.1159 |
| C | +0.43% | 1.0585 |
| D | +1.11% | 1.0873 |
| E | -0.58% | 0.9738 |
| F | +0.09% | 1.0067 |

Ghost Taotie returned **+0.24%**, ending at **0.9665** (**-3.35%** cumulative). The matched monkey court uses the same no-rebalance holiday calendar: **11 specifications × 1,000 simulations**. For the champion's `P_5_1` group, median cumulative return is **-3.80%**, raw upper-tail plus-one **p = 0.0020**, and percentile **99.8%**. These results concern cumulative performance through October 9, not these two sessions. The limited 168-path Bonferroni sensitivity gives approximately **0.336**, above 0.05, without covering all historical research choices.

**Level A**: NAV, returns, ranks, breadth, holdings continuity and drawdown. **Level D**: sector, factor, liquidity and causal handler explanations remain unidentified. Two sessions cannot establish durable forecasting skill.

Source: corrected October 9 public NAV, metrics and cumulative significance exports for the flagship season, plus its index series. Returns and gaps use unrounded NAV; displayed NAV has four decimals.
