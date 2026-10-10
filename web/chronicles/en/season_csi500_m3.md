# 🏛️ CSI 500 — Month 03: Two Survivors, Two Different Crowns

> **M3 anchor**: August 28 close; **August 31–September 30, 2026**, 22 trading sessions.<br />
> **Cumulative M3 cutoff**: July 3–September 30, 63 NAV observations including the initial anchor.<br />
> **Scope**: CSI 500 only, 168 contestant paths; market index, executable Taotie, Ghost Taotie and matched monkeys. October belongs to the separate appendix.

## ⚡ Season Review TL;DR

- **September breadth**: only **2/168** paths gained; mean return **-3.73%**, median **-3.49%**, against the CSI 500 index's **-5.83%**.
- **Monthly winner**: `CONTESTANT_A_meerkat-10` returned **+0.42%**, ending at NAV **1.0144**; F's concentrated Eagle was the other positive path, at **+0.25%**.
- **Cumulative crown**: A's `sloth-2` ended September at NAV **1.0791** (**+7.91%**), despite losing **-4.10%** in M3; B's `eagle-5-1` followed at **+7.48%** cumulative.
- **Baseline split**: September Taotie returned **-1.00%** and Ghost Taotie **-4.57%**; their cumulative returns were **-0.11%** and **-9.21%**.
- **Exposure matters**: Taotie averaged **72.63%** cash and **165.11** holdings through September, versus Ghost's **0.33%** cash and **499.84** holdings.
- **Delay comparison**: A's Sloth-2 and Snail-2 returned **+7.91%** and **-0.26%** cumulatively, with mean cash ratios **17.82%** and **2.58%**.
- **Cumulative null court**: September's cumulative leader had matched raw plus-one **p = 0.0010**, median monkey return **-7.16%**, and maximum drawdown **8.93%**; the limited 168-path Bonferroni sensitivity is **0.168**.

## I. September: Almost Everyone Lost, but Not Equally

| September rank | Path | M3 return | September 30 NAV |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_A_meerkat-10 | +0.42% | 1.0144 |
| 2 | CONTESTANT_F_eagle-5-1 | +0.25% | 0.8941 |
| 3 | CONTESTANT_B_eagle-11-2 | -0.07% | 1.0291 |
| 4 | CONTESTANT_B_sloth-4 | -0.77% | 0.9844 |
| 5 | CONTESTANT_A_koala | -1.04% | 0.7390 |

F's small monthly gain did not restore its NAV above 1.0000. A's Koala ranked fifth for September yet remained far below its initial NAV. Monthly resilience and cumulative recovery are different claims.

At the other end, E's `meerkat-50` lost **-8.41%**, D's `sloth-4` **-7.83%**, and F's `rabbit-1` **-7.59%**. The monthly leader's **4.43%** cumulative maximum drawdown was lower than B's concentrated Eagle's **11.91%**. These are observed paths, without an identified industry or factor explanation.

## II. The September Crown Stayed with Sloth

| Cumulative rank at September 30 | Path | Cumulative return | NAV |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_A_sloth-2 | +7.91% | 1.0791 |
| 2 | CONTESTANT_B_eagle-5-1 | +7.48% | 1.0748 |
| 3 | CONTESTANT_B_sloth-1 | +7.26% | 1.0726 |
| 4 | CONTESTANT_B_rabbit-1 | +7.16% | 1.0716 |
| 5 | CONTESTANT_D_rabbit-1 | +7.00% | 1.0700 |

The monthly winner and cumulative leader belonged to A but used different handlers. The Sloth crown inherited earlier gains; it did not win September.

| Robot | September return | Cumulative return at September 30 |
| :--- | ---: | ---: |
| A | -4.28% | +0.95% |
| B | -1.42% | +4.41% |
| C | -6.25% | -11.21% |
| D | -1.42% | +4.34% |
| E | -1.64% | -8.26% |
| F | -4.69% | -7.97% |

## III. Cash and the September Null Court

Taotie's **72.63%** mean cash and **96.21%** unaffordable-buy ratio describe a constrained execution baseline, while Ghost's **0.33%** cash describes much fuller exposure. Their September difference cannot be assigned entirely to selection. The same caution applies to A's cold-start Sloth-2 and warm-start Snail-2: both use delayed signals after their entry phase, but their exposure histories differ.

The cumulative Sloth leader sits above the matching `P_22_3` monkey median of **-7.16%**, with raw upper-tail plus-one **p = 0.0010** among **1,000** simulations. This tests cumulative return through **September 30**, not M3 return alone. The limited **168-path** Bonferroni sensitivity of **0.168** exceeds 0.05; it also leaves historical selection and handler design outside its adjustment. Delayed paths have further exposure differences from the matched trading-policy null.

## IV. October Appendix — The Same Holdings Resume

October 8–9 contains two valuation sessions after the September 28 rebalance. No rebalance occurs on either day; the next scheduled rebalance is October 12. CSI 500 returns **-2.48%** here, reaching **-17.09%** cumulatively. Only **78/168** contestant paths gain; the mean two-day return is **-0.18%**.

| Rank at October 9 | Path | Two-day return | NAV | Cumulative return |
| ---: | :--- | ---: | ---: | ---: |
| 1 | CONTESTANT_B_eagle-5-1 | +1.27% | 1.0885 | +8.85% |
| 2 | CONTESTANT_B_rabbit-1 | +1.57% | 1.0884 | +8.84% |
| 3 | CONTESTANT_B_rabbit-2 | +1.57% | 1.0825 | +8.25% |

The Eagle's lead is narrow at displayed precision. Taotie gains **+0.25%** to **+0.14%** cumulative; Ghost loses **-0.73%** to **-9.88%**. The October cumulative leader's maximum drawdown is **11.91%**; its matched `P_5_1` median is **-9.25%**, with raw upper-tail plus-one **p = 0.0150**. Its limited 168-path Bonferroni sensitivity is capped at **1.000**. These are cumulative tests through October 9, separate from the September Sloth test and the two-day return.

**Evidence boundary**: returns, ranks, cash, drawdowns and null placement are Level A. Sector, style, liquidity and durable forecasting explanations remain unidentified. Source: CSI 500 public NAV, diagnostics, metrics and date-matched significance exports, plus its market-index series. Returns use unrounded NAV; displayed NAV has four decimals.
