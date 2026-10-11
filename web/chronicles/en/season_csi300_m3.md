# season_csi300 — repaired dispatch through 2026-09-30

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-08-28; cutoff: 2026-09-30. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-08-28 → 2026-09-30: 22 return sessions, 23 NAV observations including the reporting anchor; 5 scheduled rebalances.
- Period leader CONTESTANT_E_eagle-11-2: +2.5205%; end NAV 1.021378.
- Cumulative leader CONTESTANT_D_rabbit-1: +17.9894%; end NAV 1.179894.
- 16/168 contestant paths gained during this segment; median path return -3.8790%.
- Market index segment return -5.4578%; end normalized NAV 0.899931.
- Taotie -0.6585% for the segment, end NAV 1.008678; Ghost scenario -4.3321%, NAV 0.942049.
- Cumulative leader raw p=9.9999e-06, Bonferroni p=0.00839992; N=100,000 per matched random spec.
- At this cutoff: 58/168 raw p<0.05 and 22/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_E_eagle-11-2 | 2.5205 | 2.1378 | 1.0214 | 2.6928 | 0.0655993 | 1 |
| CONTESTANT_B_robot | 2.4347 | 11.3408 | 1.1134 | 2.3126 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | 1.9402 | 12.5368 | 1.1254 | 2.1130 | 0.000169998 | 0.142799 |
| CONTESTANT_B_rabbit-1 | 1.7635 | 13.9653 | 1.1397 | 2.5692 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | 1.7458 | 12.8432 | 1.1284 | 2.5583 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_robot | 1.7216 | 12.4391 | 1.1244 | 2.2404 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_snail-1 | 1.5186 | 10.1554 | 1.1016 | 1.6769 | 1.99998e-05 | 0.0167998 |
| CONTESTANT_B_sloth-1 | 1.4554 | 12.1741 | 1.1217 | 1.6134 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-1 | 1.2139 | 17.9894 | 1.1799 | 2.5610 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-44-6 | 0.8810 | 9.4046 | 1.0940 | 2.5047 | 9.9999e-06 | 0.00839992 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_D_rabbit-1 | 1.2139 | 17.9894 | 1.1799 | 2.5610 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-5-1 | -1.3473 | 17.8439 | 1.1784 | 4.1396 | 0.00129999 | 1 |
| CONTESTANT_D_rabbit-2 | 0.5137 | 16.6518 | 1.1665 | 2.5976 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-1 | 1.7635 | 13.9653 | 1.1397 | 2.5692 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-11-2 | -1.1017 | 13.1088 | 1.1311 | 4.1838 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_B_rabbit-2 | 1.7458 | 12.8432 | 1.1284 | 2.5583 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | 1.9402 | 12.5368 | 1.1254 | 2.1130 | 0.000169998 | 0.142799 |
| CONTESTANT_D_robot | 1.7216 | 12.4391 | 1.1244 | 2.2404 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_sloth-1 | 1.4554 | 12.1741 | 1.1217 | 1.6134 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_C_rabbit-2 | 0.0839 | 11.5934 | 1.1159 | 3.0725 | 1.99998e-05 | 0.0167998 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_snail-4 | -9.2524 | -7.0186 | 0.9298 | 10.6219 | 0.841432 | 1 |
| CONTESTANT_A_sloth-4 | -9.4407 | -7.8212 | 0.9218 | 10.8193 | 0.895521 | 1 |
| CONTESTANT_C_koala | -10.1104 | -23.0677 | 0.7693 | 12.3197 | 1 | 1 |
| CONTESTANT_B_meerkat-90 | -12.0444 | -19.7736 | 0.8023 | 13.2802 | 1 | 1 |
| CONTESTANT_A_eagle-5-1 | -13.0161 | -4.2636 | 0.9574 | 13.9617 | 0.421706 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -5.1625 | -5.0228 | 0 | -0.2297 | -13.0161 | 6.8019 |
| CONTESTANT_B | -2.5394 | -2.0883 | 7 | 2.4347 | -12.0444 | 4.8085 |
| CONTESTANT_C | -3.8584 | -4.1132 | 2 | 0.0839 | -10.1104 | 5.5488 |
| CONTESTANT_D | -2.8045 | -2.8194 | 6 | 1.9402 | -7.6780 | 4.8386 |
| CONTESTANT_E | -2.8472 | -3.0513 | 1 | 2.5205 | -5.8186 | 4.9356 |
| CONTESTANT_F | -4.6975 | -4.3220 | 0 | -1.5194 | -8.3013 | 6.4076 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -1.9730 | -1.1882 | 2.5205 | -8.3013 |
| eagle-44-6 | -1.5941 | -1.7519 | 0.8810 | -5.2602 |
| eagle-5-1 | -5.0641 | -3.2833 | -1.3473 | -13.0161 |
| eagle-66-9 | -1.5667 | -0.8952 | -0.0278 | -4.1497 |
| eagle-88-12 | -1.8797 | -1.4545 | -0.8830 | -3.4180 |
| koala | -7.3895 | -7.6565 | -4.3672 | -10.1104 |
| meerkat-10 | -1.4067 | -1.5118 | 0.7543 | -4.0110 |
| meerkat-20 | -2.2632 | -2.3648 | -0.3526 | -3.9653 |
| meerkat-30 | -2.8636 | -2.3563 | -0.2297 | -5.5010 |
| meerkat-40 | -3.7592 | -3.9782 | -1.1791 | -6.8594 |
| meerkat-50 | -3.5863 | -3.7166 | -1.1709 | -5.8186 |
| meerkat-60 | -5.6008 | -5.0259 | -4.4766 | -7.6780 |
| meerkat-70 | -5.6379 | -5.8827 | -4.1034 | -7.0177 |
| meerkat-80 | -4.7492 | -4.4601 | -2.8986 | -7.1387 |
| meerkat-90 | -6.1778 | -4.8745 | -2.8138 | -12.0444 |
| rabbit-1 | -1.3510 | -0.9631 | 1.7635 | -6.1529 |
| rabbit-2 | -1.5641 | -0.6534 | 1.7458 | -5.9722 |
| robot | -1.3725 | -1.3076 | 2.4347 | -5.0953 |
| sloth-1 | -2.3206 | -2.1442 | 1.4554 | -7.0062 |
| sloth-2 | -4.5558 | -4.5097 | -0.9958 | -7.8590 |
| sloth-3 | -5.2735 | -4.9543 | -2.9363 | -9.0382 |
| sloth-4 | -5.6535 | -5.4430 | -1.9577 | -9.4407 |
| snail-1 | -2.4636 | -2.3517 | 1.5186 | -7.2833 |
| snail-2 | -4.5313 | -4.3814 | -0.7402 | -8.1329 |
| snail-3 | -4.8757 | -4.5831 | -1.9888 | -8.9123 |
| snail-4 | -5.4714 | -4.8424 | -1.1689 | -9.2524 |
| turtle | -4.7746 | -3.6956 | -3.1850 | -8.0890 |
| whale-shark | -2.5243 | -2.3325 | -1.5521 | -3.4002 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 11.6689 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.

## Separate October appendix

September 30 close to October 9 contains two return sessions. The holiday Monday produces no makeup rebalance. October is reported separately from September.

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_F_eagle-5-1 | 3.0731 | -1.9409 | 0.9806 | 1.0560 | 0.2975 | 1.0000 |
| CONTESTANT_D_robot | 1.6870 | 14.3359 | 1.1434 | -0.0000 | 0.0000 | 0.0084 |
| CONTESTANT_D_snail-1 | 1.5270 | 11.0249 | 1.1102 | 0.1890 | 0.0000 | 0.0084 |
| CONTESTANT_D_sloth-1 | 1.3586 | 10.5921 | 1.1059 | 0.3203 | 0.0000 | 0.0084 |
| CONTESTANT_C_turtle | 1.2330 | -1.5559 | 0.9844 | -0.0000 | 0.2841 | 1.0000 |
| CONTESTANT_A_meerkat-30 | 1.2308 | 5.5904 | 1.0559 | 0.2971 | 0.0021 | 1.0000 |
| CONTESTANT_B_turtle | 1.1633 | 6.3050 | 1.0630 | 0.0237 | 0.0023 | 1.0000 |
| CONTESTANT_B_meerkat-40 | 1.1590 | 2.9373 | 1.0294 | -0.0000 | 0.0201 | 1.0000 |
| CONTESTANT_A_meerkat-20 | 1.1483 | 2.2474 | 1.0225 | -0.0000 | 0.0328 | 1.0000 |
| CONTESTANT_D_eagle-44-6 | 1.1460 | 9.6515 | 1.0965 | -0.0000 | 0.0000 | 0.0084 |
