# season_01 — repaired dispatch through 2026-10-09

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-09-30; cutoff: 2026-10-09. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-09-30 → 2026-10-09: 2 return sessions, 3 NAV observations including the reporting anchor; 0 scheduled rebalances.
- Period leader CONTESTANT_E_meerkat-50: +2.1271%; end NAV 0.963118.
- Cumulative leader CONTESTANT_B_eagle-5-1: +21.2467%; end NAV 1.212467.
- 111/168 contestant paths gained during this segment; median path return +0.5188%.
- Market index segment return -0.9264%; end normalized NAV 0.891594.
- Taotie +0.4623% for the segment, end NAV 1.013608; Ghost scenario +0.2449%, NAV 0.966529.
- Cumulative leader raw p=0.000389996, Bonferroni p=0.327597; N=100,000 per matched random spec.
- At this cutoff: 68/168 raw p<0.05 and 21/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_E_meerkat-50 | 2.1271 | -3.6882 | 0.9631 | -0.0000 | 0.603624 | 1 |
| CONTESTANT_F_eagle-5-1 | 1.7185 | 3.1586 | 1.0316 | -0.0000 | 0.153258 | 1 |
| CONTESTANT_D_meerkat-20 | 1.6224 | 10.0789 | 1.1008 | -0.0000 | 3.99996e-05 | 0.0335997 |
| CONTESTANT_E_meerkat-60 | 1.5656 | -0.2005 | 0.9980 | -0.0000 | 0.193148 | 1 |
| CONTESTANT_D_sloth-3 | 1.5603 | -2.2335 | 0.9777 | -0.0000 | 0.417126 | 1 |
| CONTESTANT_D_sloth-4 | 1.5575 | -6.2370 | 0.9376 | -0.0000 | 0.862481 | 1 |
| CONTESTANT_D_snail-3 | 1.5509 | -3.6387 | 0.9636 | -0.0000 | 0.597184 | 1 |
| CONTESTANT_B_turtle | 1.5452 | 4.6629 | 1.0466 | -0.0000 | 0.0112899 | 1 |
| CONTESTANT_B_eagle-5-1 | 1.5425 | 21.2467 | 1.2125 | 0.2813 | 0.000389996 | 0.327597 |
| CONTESTANT_B_snail-2 | 1.5013 | 3.0767 | 1.0308 | -0.0000 | 0.0268597 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 1.5425 | 21.2467 | 1.2125 | 0.2813 | 0.000389996 | 0.327597 |
| CONTESTANT_D_rabbit-1 | 0.7458 | 15.2473 | 1.1525 | -0.0000 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | 0.4708 | 14.6348 | 1.1463 | 0.4135 | 5.99994e-05 | 0.0503995 |
| CONTESTANT_A_rabbit-1 | 0.7399 | 13.9918 | 1.1399 | -0.0000 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-1 | 0.8234 | 13.7547 | 1.1375 | 0.1776 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-44-6 | 0.9927 | 12.5207 | 1.1252 | -0.0000 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-2 | 0.6723 | 11.9464 | 1.1195 | -0.0000 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | 0.8385 | 11.7968 | 1.1180 | 0.1534 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_eagle-11-2 | 0.8163 | 11.7154 | 1.1172 | -0.0000 | 0.000649994 | 0.545995 |
| CONTESTANT_B_robot | 1.0861 | 11.5900 | 1.1159 | -0.0000 | 1.99998e-05 | 0.0167998 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_eagle-5-1 | -1.0517 | 8.4782 | 1.0848 | 1.0517 | 0.0397796 | 1 |
| CONTESTANT_A_meerkat-70 | -1.0580 | -5.9779 | 0.9402 | 1.1262 | 0.843122 | 1 |
| CONTESTANT_E_eagle-11-2 | -1.2879 | -0.9465 | 0.9905 | 1.5891 | 0.291187 | 1 |
| CONTESTANT_C_meerkat-90 | -1.6472 | -8.0457 | 0.9195 | 2.5336 | 0.95321 | 1 |
| CONTESTANT_E_eagle-5-1 | -1.9011 | 0.4337 | 1.0043 | 1.9011 | 0.265097 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | 0.0660 | 0.2220 | 15 | 1.3830 | -1.0580 | 0.4493 |
| CONTESTANT_B | 0.7074 | 0.8090 | 23 | 1.5452 | -0.8054 | 0.2557 |
| CONTESTANT_C | 0.4705 | 0.5852 | 22 | 1.3746 | -1.6472 | 0.3575 |
| CONTESTANT_D | 0.7699 | 1.0089 | 24 | 1.6224 | -0.9781 | 0.2920 |
| CONTESTANT_E | -0.0797 | -0.2532 | 12 | 2.1271 | -1.9011 | 0.6735 |
| CONTESTANT_F | 0.1651 | 0.0757 | 15 | 1.7185 | -0.8328 | 0.3488 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | 0.3178 | 0.4863 | 1.2084 | -1.2879 |
| eagle-44-6 | 0.6504 | 0.6086 | 1.0511 | 0.0776 |
| eagle-5-1 | -0.0541 | -0.3163 | 1.7185 | -1.9011 |
| eagle-66-9 | 0.6599 | 0.7403 | 0.9853 | 0.2148 |
| eagle-88-12 | 0.5926 | 0.6178 | 0.8030 | 0.2639 |
| koala | -0.4958 | -0.7205 | 0.5636 | -1.0118 |
| meerkat-10 | 0.5891 | 0.8358 | 1.0325 | -0.6208 |
| meerkat-20 | 0.9720 | 0.9984 | 1.6224 | 0.3182 |
| meerkat-30 | 0.9979 | 1.0309 | 1.3992 | 0.4184 |
| meerkat-40 | 0.3749 | 0.3305 | 0.8252 | -0.0854 |
| meerkat-50 | 0.5377 | 0.3376 | 2.1271 | -0.1339 |
| meerkat-60 | 0.2364 | -0.0161 | 1.5656 | -0.8054 |
| meerkat-70 | -0.0691 | 0.0507 | 0.9279 | -1.0580 |
| meerkat-80 | 0.0837 | 0.0468 | 0.6810 | -0.7048 |
| meerkat-90 | -0.1676 | -0.0755 | 0.7913 | -1.6472 |
| rabbit-1 | 0.2038 | 0.3189 | 0.8234 | -0.8328 |
| rabbit-2 | 0.2571 | 0.2910 | 0.8385 | -0.3882 |
| robot | 0.4619 | 0.5327 | 1.1145 | -0.5809 |
| sloth-1 | 0.3760 | 0.2204 | 1.3708 | -0.2576 |
| sloth-2 | 0.4013 | 0.4212 | 1.4466 | -0.7497 |
| sloth-3 | 0.2591 | 0.0737 | 1.5603 | -0.7234 |
| sloth-4 | 0.2636 | 0.2013 | 1.5575 | -0.7976 |
| snail-1 | 0.3751 | 0.2339 | 1.3818 | -0.3576 |
| snail-2 | 0.4212 | 0.5257 | 1.5013 | -0.7774 |
| snail-3 | 0.2737 | 0.1311 | 1.5509 | -0.8540 |
| snail-4 | 0.2539 | 0.2211 | 1.4400 | -0.9493 |
| turtle | 0.3696 | 0.3871 | 1.5452 | -0.8835 |
| whale-shark | 0.6540 | 0.6581 | 0.7674 | 0.5373 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 3.6196 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
