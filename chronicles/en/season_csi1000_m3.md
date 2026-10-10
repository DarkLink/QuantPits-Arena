# 🏛️ CSI 1000 — Month 03: The Eagle's Rally Meets the Sloth's Inherited Lead

> **M3 anchor**: August 28 close; **August 31–September 30, 2026**, 22 trading sessions.<br />
> **Cumulative M3 cutoff**: July 3–September 30, 63 NAV observations including the initial anchor.<br />
> **Scope**: CSI 1000 only, 168 contestant paths; index, executable Taotie, Ghost Taotie and matched monkeys. October is separately reported below.

## ⚡ Season Review TL;DR

- **September breadth**: **6/168** paths gained; mean return **-3.79%**, median **-3.92%**; CSI 1000 returned **-5.27%**.
- **Monthly Eagle**: `CONTESTANT_B_eagle-5-1` gained **+6.18%** in M3, reaching NAV **1.1406** (**+14.06%** cumulative).
- **Inherited Sloth crown**: A's `sloth-2` retained first place at **1.1474** (**+14.74%** cumulative), despite **-2.73%** in September.
- **Risk contrast**: September's cumulative Sloth leader had maximum drawdown **7.00%**; B's monthly Eagle winner had **17.62%**.
- **Baselines**: September Taotie returned **-0.30%** and Ghost **-3.71%**; cumulative returns were **+0.39%** and **-8.45%**.
- **Exposure contrast**: Taotie averaged **89.63%** cash and **122.39** holdings, versus Ghost's **0.21%** cash and **999.68** holdings through September.
- **Cumulative null court**: A's Sloth-2 had raw plus-one **p = 0.0010** against a **-7.50%** matched median; the limited 168-path Bonferroni sensitivity is **0.168**.

## I. A Large Monthly Gain in a Mostly Falling Field

| September rank | Path | M3 return | September 30 NAV |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_B_eagle-5-1 | +6.18% | 1.1406 |
| 2 | CONTESTANT_C_eagle-5-1 | +2.47% | 0.9772 |
| 3 | CONTESTANT_A_eagle-11-2 | +1.32% | 1.0763 |
| 4 | CONTESTANT_D_eagle-5-1 | +0.48% | 0.9699 |
| 5 | CONTESTANT_B_meerkat-30 | +0.42% | 1.0041 |

The first four monthly places were Eagles, but the second and fourth still ended below their initial NAV. The Eagle group did not move together: E's `eagle-5-1` lost **-8.89%**. E's `meerkat-30` lost **-9.38%** and B's `meerkat-90` **-9.10%**. September's upside and downside both require contestant-specific reporting.

## II. Sloth Holds the Cumulative Lead, Eagle Closes In

| Cumulative rank at September 30 | Path | Cumulative return | NAV |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_A_sloth-2 | +14.74% | 1.1474 |
| 2 | CONTESTANT_B_eagle-5-1 | +14.06% | 1.1406 |
| 3 | CONTESTANT_A_sloth-3 | +10.62% | 1.1062 |
| 4 | CONTESTANT_C_sloth-4 | +10.33% | 1.1033 |
| 5 | CONTESTANT_B_sloth-2 | +9.61% | 1.0961 |

Four of the cumulative top five were Sloths, although the monthly top four were Eagles. A's Sloth-2 led B's Eagle by approximately **0.68 percentage points** of cumulative return. The contrast concerns different windows and exposure histories; it does not imply a common cause.

| Robot | September return | Cumulative return at September 30 |
| :--- | ---: | ---: |
| A | -0.74% | +1.72% |
| B | -1.58% | +3.74% |
| C | -3.37% | +1.38% |
| D | -4.59% | -10.69% |
| E | -3.66% | -7.28% |
| F | -5.12% | -10.74% |

All six Robots lost during September, including those still positive cumulatively.

## III. The Cash Qualification and the Null Court

A's Sloth-2 returned **+14.74%** cumulatively with **17.70%** mean cash. A's Snail-2 returned **+1.90%**, with **2.04%** cash. Snail enters at the start and then uses delayed signals; Sloth starts in cash. This control comparison does not cleanly separate selection from cash shelter.

Taotie's **89.63%** average cash and **98.90%** unaffordable-buy ratio make its near-flat return a constrained execution observation. Ghost's almost full exposure provides a different reference. Neither difference identifies an industry or liquidity cause.

At September 30 the cumulative Sloth leader exceeds the matching `P_22_3` monkey median of **-7.50%**, with raw upper-tail plus-one **p = 0.0010** among **1,000** simulations. This is cumulative evidence, not a p-value for September's Eagle rally. The limited **168-path** Bonferroni sensitivity gives **0.168**, above 0.05, without accounting for all historical design and selection. Delayed strategies also differ in exposure from the null's entry convention.

## IV. October Appendix — An Unchanged Portfolio Can Change the Crown

October 8–9 resumes daily valuation of September 28 holdings, with no new trades. The next scheduled rebalance is October 12. CSI 1000 returns **-1.96%** over these two sessions and **-16.99%** cumulatively. **75/168** contestant paths gain; the mean two-day return is **-0.34%**.

| Rank at October 9 | Path | Two-day return | NAV | Cumulative return |
| ---: | :--- | ---: | ---: | ---: |
| 1 | CONTESTANT_B_eagle-5-1 | -0.50% | 1.1349 | +13.49% |
| 2 | CONTESTANT_A_sloth-2 | -2.38% | 1.1201 | +12.01% |
| 3 | CONTESTANT_B_sloth-2 | -0.28% | 1.0930 | +9.30% |

B's Eagle takes the crown while losing over the two days, because A's Sloth loses more. A crown change is therefore not evidence of a new trade or a positive period return. Taotie gains **+0.20%** to **+0.59%** cumulative; Ghost loses **-0.36%** to **-8.78%**.

The new cumulative leader retains **17.62%** maximum drawdown. Its matched `P_5_1` median is **-9.86%**, raw upper-tail plus-one **p = 0.0150**; the limited 168-path Bonferroni sensitivity is capped at **1.000**. This October 9 cumulative test differs from September's Sloth test and is not a test of the two-day crown change.

**Evidence boundary**: measured returns, ranks, cash, drawdown and null placement are Level A. Cash attribution, concentration causality, industry and enduring forecasting explanations remain unproven. Source: CSI 1000 public NAV, diagnostics, metrics and date-matched significance exports, plus its index series. Unrounded NAV determines returns; NAV is displayed to four decimals.
