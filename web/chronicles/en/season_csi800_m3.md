# 🏛️ CSI 800 — Month 03: The Rabbit Keeps the Crown, the Eagle Wins the Month

> **M3 anchor**: August 28 close; **August 31–September 30, 2026**, 22 trading sessions.<br />
> **Cumulative M3 cutoff**: July 3–September 30, 63 NAV observations including the initial anchor.<br />
> **Scope**: CSI 800 only, 168 contestant paths; market index, executable Taotie, Ghost Taotie and matched monkeys. October is a separate appendix.

## ⚡ Season Review TL;DR

- **September breadth**: **5/168** paths gained; mean return **-3.87%**, median **-3.78%**; the CSI 800 index returned **-5.56%**.
- **Monthly winner**: `CONTESTANT_E_eagle-5-1` gained **+1.86%**, ending at NAV **1.0123** (**+1.23%** cumulative).
- **Rabbit crown**: B's `rabbit-2` ended September at NAV **1.1083** (**+10.83%** cumulative), after **-0.38%** in M3; D's `rabbit-1` followed at **+10.05%** cumulative.
- **Baselines**: September Taotie returned **-0.40%**, Ghost **-4.27%**; cumulative returns were **+0.05%** and **-7.84%**.
- **Exposure split**: Taotie's full-window mean cash was **85.71%**, with **138.81** mean holdings; Ghost's cash was **0.27%**, with **799.60** holdings.
- **Robots diverge**: B's Robot gained **+0.13%** in September; the other five Robots lost between **-2.96%** and **-5.38%**.
- **Risk remains**: cumulative maximum drawdown was **9.79%** for B's Rabbit-2, **10.42%** for D's Rabbit-1 and **10.80%** for September's E Eagle winner.

## I. Five Positive Paths, Not a Broad Revival

| September rank | Path | M3 return | September 30 NAV |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_E_eagle-5-1 | +1.86% | 1.0123 |
| 2 | CONTESTANT_A_meerkat-40 | +0.40% | 1.0573 |
| 3 | CONTESTANT_B_eagle-11-2 | +0.20% | 1.0523 |
| 4 | CONTESTANT_B_robot | +0.13% | 1.0468 |
| 5 | CONTESTANT_E_turtle | +0.00% | 0.9453 |

E's Turtle return is slightly positive before rounding, hence the count of five. E's Eagle won the month without winning the cumulative tournament. Its NAV returned above 1.0000 while most paths still declined.

D's `sloth-4` lost **-9.20%**, D's `sloth-3` **-8.57%**, and F's concentrated Eagle **-8.39%**. Concentration appears at both ends of this month's outcomes; the winning Eagle cannot establish that concentration universally improves results.

## II. The Rabbit's Lead Survives a Negative Month

| Cumulative rank at September 30 | Path | Cumulative return | NAV |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_B_rabbit-2 | +10.83% | 1.1083 |
| 2 | CONTESTANT_D_rabbit-1 | +10.05% | 1.1005 |
| 3 | CONTESTANT_B_rabbit-1 | +7.95% | 1.0795 |
| 4 | CONTESTANT_D_meerkat-10 | +7.82% | 1.0782 |
| 5 | CONTESTANT_B_sloth-1 | +6.62% | 1.0662 |

Three Rabbit paths occupied the cumulative top three. This is a CSI 800 observation through September, not a universal turnover rule or evidence that fresh replacements caused the gains.

| Robot | September return | Cumulative return at September 30 |
| :--- | ---: | ---: |
| A | -5.38% | -0.47% |
| B | +0.13% | +4.68% |
| C | -3.91% | -4.32% |
| D | -2.96% | +0.48% |
| E | -3.10% | -8.39% |
| F | -4.70% | -12.29% |

## III. Broad Exposure Is Not the Executable Baseline's Exposure

Taotie's **85.71%** average cash and **98.36%** unaffordable-buy ratio accompany its near-flat cumulative return. Ghost held almost the whole universe and lost **-7.84%** cumulatively. Taotie's apparent resilience therefore requires an exposure qualification.

A's Sloth-2 ended September at **+4.06%** cumulative, against Snail-2's **-4.65%**. Their mean cash ratios were **17.70%** and **2.66%**. This difference does not isolate signal decay: Sloth begins in cash, whereas Snail enters immediately before using delayed signals.

The September 30 cumulative leader is tested against its own **1,000-member `P_22_22`** group: matched median **-7.30%**, excess over that median **18.13 percentage points**, raw upper-tail plus-one **p = 0.0010**. These date-matched results concern cumulative performance through September 30, not M3 alone. The limited 168-path Bonferroni sensitivity is **0.168**, above 0.05, and does not account for all historical selection and handler design.

## IV. October Appendix — Rabbit Holdings, No New Chase

October 8–9 values the holdings left by September 28. Neither day has a rebalance; October 12 is the next scheduled execution. CSI 800 returns **-1.35%** here and **-12.62%** cumulatively. **92/168** paths gain; the mean two-day return is **-0.14%**.

| Rank at October 9 | Path | Two-day return | NAV | Cumulative return |
| ---: | :--- | ---: | ---: | ---: |
| 1 | CONTESTANT_B_rabbit-2 | +0.81% | 1.1172 | +11.72% |
| 2 | CONTESTANT_D_rabbit-1 | +1.00% | 1.1115 | +11.15% |
| 3 | CONTESTANT_B_rabbit-1 | +0.80% | 1.0882 | +8.82% |

The Rabbit retains the crown without a reopening trade. Taotie gains **+0.14%** to **+0.18%** cumulative; Ghost loses **-0.64%** to **-8.43%**. The leader's cumulative maximum drawdown remains **9.79%**. Its October 9 cumulative `P_22_22` matched median is **-7.53%**, excess **19.25 percentage points**, raw upper-tail plus-one **p = 0.0010**. The limited 168-path Bonferroni sensitivity is **0.168**. This is a new cumulative cutoff, not a p-value for the two-day gain.

**Evidence boundary**: measured NAV, breadth, cash, drawdown and matched-null placement are Level A. Industry, style, liquidity and causal turnover explanations are unresolved. Source: CSI 800 public NAV, diagnostics, metrics and date-matched significance exports, plus its index series. Returns use unrounded NAV; NAV is displayed to four decimals.
