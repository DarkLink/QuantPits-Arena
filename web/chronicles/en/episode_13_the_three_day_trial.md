# season_01 — repaired dispatch through 2026-09-30

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-09-24; cutoff: 2026-09-30. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-09-24 → 2026-09-30: 3 return sessions, 4 NAV observations including the reporting anchor; 1 scheduled rebalances.
- Period leader CONTESTANT_C_eagle-5-1: +2.2408%; end NAV 1.083447.
- Cumulative leader CONTESTANT_B_eagle-5-1: +19.4049%; end NAV 1.194049.
- 115/168 contestant paths gained during this segment; median path return +0.3504%.
- Market index segment return -1.8364%; end normalized NAV 0.899931.
- Taotie +0.2966% for the segment, end NAV 1.008944; Ghost scenario +0.0132%, NAV 0.964168.
- Cumulative leader raw p=0.000739993, Bonferroni p=0.621594; N=100,000 per matched random spec.
- At this cutoff: 63/168 raw p<0.05 and 21/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_C_eagle-5-1 | 2.2408 | 8.3447 | 1.0834 | 0.0021 | 0.0366196 | 1 |
| CONTESTANT_C_sloth-1 | 1.6534 | 5.1040 | 1.0510 | 0.0962 | 0.00313997 | 1 |
| CONTESTANT_C_snail-1 | 1.6410 | 3.4592 | 1.0346 | 0.1075 | 0.0139099 | 1 |
| CONTESTANT_B_meerkat-10 | 1.4102 | 6.8035 | 1.0680 | 0.0989 | 0.000669993 | 0.562794 |
| CONTESTANT_C_robot | 1.3773 | 5.3988 | 1.0540 | 0.1684 | 0.00247998 | 1 |
| CONTESTANT_C_snail-2 | 1.3665 | 1.2257 | 1.0123 | 0.1235 | 0.0731393 | 1 |
| CONTESTANT_B_eagle-66-9 | 1.3513 | 6.8797 | 1.0688 | 0.0315 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_C_sloth-2 | 1.3480 | 3.0511 | 1.0305 | 0.1071 | 0.0194998 | 1 |
| CONTESTANT_D_eagle-44-6 | 1.3228 | 8.5863 | 1.0859 | 0.1020 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_C_eagle-11-2 | 1.3149 | 7.1266 | 1.0713 | 0.2430 | 0.00854991 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 0.8473 | 19.4049 | 1.1940 | 0.3655 | 0.000739993 | 0.621594 |
| CONTESTANT_D_rabbit-1 | 0.5369 | 14.3941 | 1.1439 | 0.8000 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | 0.8432 | 14.0976 | 1.1410 | 0.8941 | 7.99992e-05 | 0.0671993 |
| CONTESTANT_A_rabbit-1 | 0.9634 | 13.1546 | 1.1315 | 0.7595 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-1 | 1.2261 | 12.8257 | 1.1283 | 0.1805 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-44-6 | 1.2836 | 11.4147 | 1.1141 | 0.0389 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-2 | 0.3286 | 11.1988 | 1.1120 | 0.8383 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | 1.2097 | 10.8672 | 1.1087 | 0.1710 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_eagle-11-2 | -0.0348 | 10.8108 | 1.1081 | 1.2601 | 0.000879991 | 0.739193 |
| CONTESTANT_B_robot | 1.2240 | 10.3910 | 1.1039 | 0.2611 | 9.9999e-06 | 0.00839992 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_meerkat-60 | -1.4104 | -1.4591 | 0.9854 | 2.4078 | 0.288597 | 1 |
| CONTESTANT_A_turtle | -1.7409 | -4.9303 | 0.9507 | 2.8243 | 0.740383 | 1 |
| CONTESTANT_A_koala | -1.7704 | -18.8540 | 0.8115 | 2.6439 | 1 | 1 |
| CONTESTANT_A_sloth-4 | -1.8192 | -7.5338 | 0.9247 | 2.6710 | 0.929231 | 1 |
| CONTESTANT_A_snail-4 | -1.8993 | -6.6646 | 0.9334 | 2.7647 | 0.880451 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -0.1255 | 0.2207 | 15 | 1.1977 | -1.8993 | 1.2810 |
| CONTESTANT_B | 0.4565 | 0.8226 | 19 | 1.4102 | -1.2459 | 0.8307 |
| CONTESTANT_C | 0.7225 | 1.0181 | 24 | 2.2408 | -1.3383 | 0.6378 |
| CONTESTANT_D | 0.3714 | 0.5477 | 20 | 1.3228 | -1.0304 | 0.9270 |
| CONTESTANT_E | 0.0533 | 0.1478 | 18 | 1.2051 | -0.9500 | 1.1856 |
| CONTESTANT_F | 0.2664 | 0.2836 | 19 | 1.0991 | -0.8495 | 0.9874 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | 0.4319 | 0.6589 | 1.3149 | -0.8495 |
| eagle-44-6 | 0.7093 | 1.0253 | 1.3228 | -0.3527 |
| eagle-5-1 | 0.0353 | -0.3891 | 2.2408 | -1.1050 |
| eagle-66-9 | 0.9446 | 1.1210 | 1.3513 | 0.2685 |
| eagle-88-12 | 0.8268 | 0.8593 | 1.1656 | 0.4629 |
| koala | -0.6899 | -0.6477 | 0.2305 | -1.7704 |
| meerkat-10 | 0.8460 | 0.9655 | 1.4102 | 0.1095 |
| meerkat-20 | 0.7622 | 0.8016 | 1.2550 | 0.1174 |
| meerkat-30 | 0.5888 | 0.9624 | 1.2745 | -0.5018 |
| meerkat-40 | 0.0752 | 0.2946 | 1.1977 | -0.9500 |
| meerkat-50 | 0.0134 | 0.0803 | 0.5584 | -0.6689 |
| meerkat-60 | -0.4435 | -0.2564 | 0.1559 | -1.4104 |
| meerkat-70 | -0.3390 | -0.5179 | 0.7730 | -1.2858 |
| meerkat-80 | -0.1175 | -0.0576 | 1.2051 | -1.3571 |
| meerkat-90 | -0.4690 | -0.4917 | 0.2739 | -1.2459 |
| rabbit-1 | 0.5125 | 0.7502 | 1.3119 | -0.5908 |
| rabbit-2 | 0.7247 | 0.8935 | 1.3104 | -0.2874 |
| robot | 0.8686 | 0.9778 | 1.3773 | 0.2987 |
| sloth-1 | 0.7479 | 0.6985 | 1.6534 | 0.1075 |
| sloth-2 | 0.5930 | 0.7965 | 1.3480 | -0.5437 |
| sloth-3 | 0.0975 | 0.2302 | 1.0759 | -1.1470 |
| sloth-4 | -0.2838 | -0.0696 | 0.7657 | -1.8192 |
| snail-1 | 0.7418 | 0.6872 | 1.6410 | 0.1133 |
| snail-2 | 0.5940 | 0.7950 | 1.3665 | -0.6105 |
| snail-3 | 0.1037 | 0.2588 | 1.0991 | -1.2311 |
| snail-4 | -0.2576 | 0.0351 | 0.7991 | -1.8993 |
| turtle | -0.0542 | 0.1187 | 1.1603 | -1.7409 |
| whale-shark | 0.5787 | 0.6076 | 0.7798 | 0.3374 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 3.3458 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
