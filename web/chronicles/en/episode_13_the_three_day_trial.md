# 🏛️ Episode 13: The Three-Day Trial & The Crown Above 1.20

> **Return anchor**: 2026-09-24 close.<br />
> **Trading window**: 2026-09-28 ~ 2026-09-30, 3 sessions; 63 cumulative NAV observations including the initial 2026-07-03 anchor.<br />
> **Phase**: Continued forward tracking, thirteenth settlement segment. Report numbers count dispatches, not necessarily rebalances. This report records completed results; it does not establish a pre-window cryptographic commitment.<br />
> **Core narrative**: CONTESTANT_C wins another short-window sprint, while CONTESTANT_B retains the cumulative crown above NAV 1.20.

## ⚡ TL;DR

- **Three sessions, two different baselines**: CSI 300 returned **-1.84%**, finishing at NAV **0.8999** (**-10.01%** cumulative); executable Taotie gained **+0.30%**, reaching **1.0089** (**+0.89%** cumulative).
- **The crown holds**: `CONTESTANT_B_eagle-5-1` gained **+0.85%** to NAV **1.2054** (**+20.54%** cumulative), leading second-place `CONTESTANT_D_rabbit-1` by **6.12pp**, versus **5.72pp** at the previous close.
- **C wins the sprint again**: `CONTESTANT_C_eagle-5-1` led the period with **+2.24%**, moving from NAV **1.0597** to **1.0834**. C also took second and third with `sloth-1` (**+1.65%**) and `snail-1` (**+1.64%**).
- **Monday's narrow green field**: On September 28, only **14/168 paths (8.3%)** gained; the mean path return was **-1.72%**.
- **Wednesday's unanimous recovery**: On September 30, **168/168 paths** gained, with a mean daily return of **+0.96%**.
- **The slowest casualty**: `CONTESTANT_A_snail-4` lost **-1.90%**, ending at NAV **0.9334**; `CONTESTANT_A_sloth-4` followed at **-1.82%**, NAV **0.9247**.
- **All six Robots finish positive**: Their period returns ranged from **+0.30%** to **+1.38%**; `CONTESTANT_B_robot` remained the Robot cumulative leader at NAV **1.1039**.
- **The cumulative monkey court**: The leader's matched upper-tail plus-one **p = 0.0020**, with matched median cumulative return **-4.02%**. This tests cumulative performance, not the three-session sprint.

## I. Three Sessions, Three Turns

The holiday calendar leaves a three-session evaluation window. Returns use September 24 close as the denominator; that anchor is not an extra trading session.

| Session | Mean daily return across 168 paths | Positive paths |
| :--- | ---: | ---: |
| 2026-09-28 | -1.72% | 14/168 (8.3%) |
| 2026-09-29 | +1.13% | 136/168 (81.0%) |
| 2026-09-30 | +0.96% | 168/168 (100.0%) |

These are daily observations, not three independent rebalances. The period's orders were generated from the September 24 decision snapshot and executed on September 28. The table establishes changing path breadth; it does not identify an industry rotation or a liquidity mechanism.

The same holdings continue through October 8–9 without a new rebalance, as reported in [Episode 14](episode_14_the_two_day_return.md). September 30 separates the reporting windows, not the trading policy. The next scheduled rebalance is October 12 using the October 9 close snapshot.

## II. Period Gainers and Casualties

| Top five period gainers | Return | Start NAV | End NAV |
| :--- | ---: | ---: | ---: |
| CONTESTANT_C_eagle-5-1 | +2.24% | 1.0597 | 1.0834 |
| CONTESTANT_C_sloth-1 | +1.65% | 1.0339 | 1.0510 |
| CONTESTANT_C_snail-1 | +1.64% | 1.0179 | 1.0346 |
| CONTESTANT_B_meerkat-10 | +1.41% | 1.0532 | 1.0680 |
| CONTESTANT_B_meerkat-30 | +1.40% | 1.0130 | 1.0272 |

| Bottom five period paths | Return | End NAV |
| :--- | ---: | ---: |
| CONTESTANT_A_snail-4 | -1.90% | 0.9334 |
| CONTESTANT_A_sloth-4 | -1.82% | 0.9247 |
| CONTESTANT_A_koala | -1.77% | 0.8115 |
| CONTESTANT_A_turtle | -1.74% | 0.9507 |
| CONTESTANT_C_meerkat-70 | -1.44% | 0.8916 |

C's three leading paths use different portfolio rules. Their shared placement is a period observation, not proof of a permanent contestant trait or of an independently identified signal half-life.

## III. The Cumulative Crown

| Rank at September 30 | Path | NAV | Cumulative return |
| ---: | :--- | ---: | ---: |
| 1 | CONTESTANT_B_eagle-5-1 | 1.2054 | +20.54% |
| 2 | CONTESTANT_D_rabbit-1 | 1.1441 | +14.41% |
| 3 | CONTESTANT_D_eagle-11-2 | 1.1410 | +14.10% |
| 4 | CONTESTANT_A_rabbit-1 | 1.1315 | +13.15% |
| 5 | CONTESTANT_B_rabbit-1 | 1.1264 | +12.64% |

The leader crossed back above 1.20 while C won the period sprint. A period winner and a cumulative leader answer different questions. Their identities should not be collapsed into a claim about the strongest underlying model.

## IV. Robot Control and Evidence Boundaries

| Robot path | Period return | End NAV |
| :--- | ---: | ---: |
| CONTESTANT_A_robot | +1.06% | 1.0509 |
| CONTESTANT_B_robot | +1.22% | 1.1039 |
| CONTESTANT_C_robot | +1.38% | 1.0540 |
| CONTESTANT_D_robot | +0.89% | 1.0753 |
| CONTESTANT_E_robot | +0.36% | 0.9795 |
| CONTESTANT_F_robot | +0.30% | 1.0059 |

Ghost Taotie returned **+0.01%**, ending at NAV **0.9642** (**-3.58%** cumulative). Taotie, Ghost Taotie, and the market index remain distinct reference portfolios.

**Level A**: The rankings, NAV changes, and daily breadth above are directly observed. **Level D**: These data alone do not establish industry, factor, liquidity, or holdings-overlap explanations. The three-session window cannot establish long-run effectiveness.

The matched monkey court uses 11 specifications with 1,000 simulations each. Its statistic is cumulative tournament performance, not this three-session return. Any upper-tail probability must use the plus-one correction within the matching specification; post-selection and multiple-comparison limits remain applicable.

For the cumulative leader, the reported raw upper-tail p is **0.0020** and percentile **99.8%**. A limited 168-path Bonferroni sensitivity check gives approximately **0.336**, above 0.05; it does not account for all historical research choices.

Source: the September 30 public NAV and metric exports for `season_01_run`, with the local market-index series. Returns and gaps use unrounded data; displayed NAV is rounded to four decimals.
