# Episode 15 — Weekly review through 2026-10-16

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-10-09; cutoff: 2026-10-16. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-10-09 → 2026-10-16: 5 return sessions, 6 NAV observations including the reporting anchor; 1 scheduled rebalances.
- Period leader CONTESTANT_C_snail-1: +1.7621%; end NAV 1.059209.
- Cumulative leader CONTESTANT_B_eagle-5-1: +18.6436%; end NAV 1.186436.
- 51/168 contestant paths gained during this segment; median path return -0.9176%.
- Market index segment return -3.3966%; end normalized NAV 0.861310.
- Taotie -0.5839% for the segment, end NAV 1.007690; Ghost scenario -1.9862%, NAV 0.947332.
- Cumulative leader raw p=0.000649994, Bonferroni p=0.545995; N=100,000 per matched random spec.
- At this cutoff: 73/168 raw p<0.05 and 29/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_C_snail-1 | 1.7621 | 5.9209 | 1.0592 | 0.7751 | 0.000599994 | 0.503995 |
| CONTESTANT_C_sloth-1 | 1.7328 | 7.5281 | 1.0753 | 0.7799 | 8.99991e-05 | 0.0755992 |
| CONTESTANT_C_robot | 1.6496 | 7.5983 | 1.0760 | 0.4594 | 6.99993e-05 | 0.0587994 |
| CONTESTANT_C_meerkat-20 | 1.5631 | 1.2497 | 1.0125 | 0.4183 | 0.0301597 | 1 |
| CONTESTANT_D_meerkat-10 | 1.5461 | 3.8138 | 1.0381 | 0.7756 | 0.00401996 | 1 |
| CONTESTANT_B_rabbit-1 | 1.4716 | 15.4287 | 1.1543 | 0.4796 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | 1.4557 | 13.4243 | 1.1342 | 0.4781 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-44-6 | 1.3763 | 14.0693 | 1.1407 | 0.4991 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-66-9 | 1.3647 | 9.2437 | 1.0924 | 0.7366 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_meerkat-20 | 1.2677 | 9.7739 | 1.0977 | 1.0613 | 9.9999e-06 | 0.00839992 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | -2.1470 | 18.6436 | 1.1864 | 2.2504 | 0.000649994 | 0.545995 |
| CONTESTANT_B_rabbit-1 | 1.4716 | 15.4287 | 1.1543 | 0.4796 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-1 | -0.2964 | 14.9057 | 1.1491 | 1.0686 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_rabbit-1 | 0.2575 | 14.2853 | 1.1429 | 0.7387 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-44-6 | 1.3763 | 14.0693 | 1.1407 | 0.4991 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | 1.4557 | 13.4243 | 1.1342 | 0.4781 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | -1.5728 | 12.8318 | 1.1283 | 2.3206 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_B_robot | 0.7010 | 12.3722 | 1.1237 | 0.8398 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-11-2 | 0.3381 | 11.6332 | 1.1163 | 1.1071 | 0.000299997 | 0.251997 |
| CONTESTANT_D_rabbit-2 | -0.3214 | 11.5866 | 1.1159 | 1.0348 | 9.9999e-06 | 0.00839992 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_eagle-5-1 | -5.8545 | 2.1274 | 1.0213 | 5.8545 | 0.130579 | 1 |
| CONTESTANT_B_meerkat-90 | -6.1961 | -22.0478 | 0.7795 | 6.1961 | 1 | 1 |
| CONTESTANT_D_koala | -6.6409 | -25.6026 | 0.7440 | 6.6409 | 1 | 1 |
| CONTESTANT_C_meerkat-90 | -7.2126 | -14.6780 | 0.8532 | 7.5056 | 0.99834 | 1 |
| CONTESTANT_B_koala | -7.2156 | -24.8782 | 0.7512 | 7.2156 | 1 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -1.5502 | -0.4703 | 9 | 1.1786 | -5.8545 | 2.4845 |
| CONTESTANT_B | -0.8901 | 0.1942 | 17 | 1.4716 | -7.2156 | 2.0316 |
| CONTESTANT_C | -0.4410 | 0.4521 | 16 | 1.7621 | -7.2126 | 1.6897 |
| CONTESTANT_D | -1.4412 | -1.2645 | 6 | 1.5461 | -6.6409 | 2.3375 |
| CONTESTANT_E | -2.1598 | -2.1138 | 1 | 0.5451 | -3.6217 | 2.4943 |
| CONTESTANT_F | -1.0727 | -1.0015 | 2 | 0.8344 | -3.4021 | 1.7141 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -1.0165 | -0.7182 | 0.3381 | -3.3249 |
| eagle-44-6 | 0.2859 | 0.9873 | 1.3763 | -1.5712 |
| eagle-5-1 | -1.9586 | -1.3891 | 0.8344 | -5.8545 |
| eagle-66-9 | 0.4394 | 0.9104 | 1.3647 | -0.9371 |
| eagle-88-12 | 0.0743 | 0.5268 | 0.8639 | -1.1555 |
| koala | -5.0129 | -5.6048 | -1.7232 | -7.2156 |
| meerkat-10 | 0.0778 | 1.0697 | 1.5461 | -2.8973 |
| meerkat-20 | 0.4750 | 0.6890 | 1.5631 | -1.4896 |
| meerkat-30 | -0.4452 | 0.1644 | 1.1596 | -3.2126 |
| meerkat-40 | -1.0018 | -0.9614 | 0.2078 | -2.3051 |
| meerkat-50 | -1.1661 | -1.1201 | -0.6063 | -1.9370 |
| meerkat-60 | -3.0686 | -3.2026 | -2.2537 | -3.5277 |
| meerkat-70 | -3.7841 | -3.7581 | -3.4021 | -4.2022 |
| meerkat-80 | -3.7001 | -3.8453 | -1.1604 | -5.2319 |
| meerkat-90 | -4.4010 | -5.1730 | -1.1116 | -7.2126 |
| rabbit-1 | -0.0642 | -0.0195 | 1.4716 | -1.6934 |
| rabbit-2 | -0.1814 | 0.2137 | 1.4557 | -3.0401 |
| robot | -0.0490 | -0.1855 | 1.6496 | -1.5584 |
| sloth-1 | -0.5460 | -0.4383 | 1.7328 | -3.5062 |
| sloth-2 | -0.5504 | -0.3619 | 0.4989 | -2.3238 |
| sloth-3 | -0.9576 | -0.7326 | 0.9271 | -3.5246 |
| sloth-4 | -1.7613 | -1.7681 | 0.1088 | -3.6322 |
| snail-1 | -0.5268 | -0.4241 | 1.7621 | -3.3813 |
| snail-2 | -0.5370 | -0.2653 | 0.4718 | -2.2923 |
| snail-3 | -0.9055 | -0.6960 | 0.8654 | -3.2288 |
| snail-4 | -1.7101 | -1.5879 | -0.0192 | -3.8903 |
| turtle | -2.8148 | -2.5059 | -0.5411 | -4.9646 |
| whale-shark | -0.4502 | -0.1653 | 0.0502 | -1.3545 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 6.6888 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.

## Separate observation windows

These anonymous paths are reported over their stated observation windows and are excluded from the full-season cumulative standings and 840-item tests above. Reference paths use the same animal and close anchor; differences are observation returns minus reference returns in percentage points. No random-control p value is assigned to these windows.

| path | anchor | cutoff | return_pct | mdd_pct | reference_path | reference_return_pct | difference_pp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_G_robot | 2026-10-09 | 2026-10-16 | 1.3575 | 0.5443 | CONTESTANT_A_robot | 0.0134 | 1.3441 |
| CONTESTANT_G_sloth-1 | 2026-10-09 | 2026-10-16 | -0.2341 | 1.5000 | CONTESTANT_A_sloth-1 | -0.2341 | 0.0000 |
| CONTESTANT_G_sloth-2 | 2026-10-09 | 2026-10-16 | -0.5057 | 1.5594 | CONTESTANT_A_sloth-2 | -0.5057 | 0.0000 |
| CONTESTANT_G_sloth-3 | 2026-10-09 | 2026-10-16 | -0.9027 | 1.7192 | CONTESTANT_A_sloth-3 | -0.9027 | 0.0000 |
| CONTESTANT_G_sloth-4 | 2026-10-09 | 2026-10-16 | -3.6322 | 4.3172 | CONTESTANT_A_sloth-4 | -3.6322 | 0.0000 |
| CONTESTANT_G_snail-1 | 2026-10-09 | 2026-10-16 | -0.2064 | 1.4749 | CONTESTANT_A_snail-1 | -0.2064 | 0.0000 |
| CONTESTANT_G_snail-2 | 2026-10-09 | 2026-10-16 | -0.4345 | 1.4850 | CONTESTANT_A_snail-2 | -0.4345 | 0.0000 |
| CONTESTANT_G_snail-3 | 2026-10-09 | 2026-10-16 | -0.9984 | 1.7892 | CONTESTANT_A_snail-3 | -0.9984 | 0.0000 |
| CONTESTANT_G_snail-4 | 2026-10-09 | 2026-10-16 | -3.8903 | 4.5811 | CONTESTANT_A_snail-4 | -3.8903 | -0.0000 |
| CONTESTANT_G_rabbit-1 | 2026-10-09 | 2026-10-16 | 0.8313 | 0.5787 | CONTESTANT_A_rabbit-1 | 0.2575 | 0.5739 |
| CONTESTANT_G_rabbit-2 | 2026-10-09 | 2026-10-16 | 1.1307 | 0.5482 | CONTESTANT_A_rabbit-2 | 0.7541 | 0.3767 |
| CONTESTANT_G_turtle | 2026-10-09 | 2026-10-16 | -4.4101 | 4.9055 | CONTESTANT_A_turtle | -4.9646 | 0.5545 |
| CONTESTANT_G_koala | 2026-10-09 | 2026-10-16 | -6.0549 | 6.0823 | CONTESTANT_A_koala | -5.3749 | -0.6801 |
| CONTESTANT_G_meerkat-10 | 2026-10-09 | 2026-10-16 | 1.3111 | 0.5003 | CONTESTANT_A_meerkat-10 | 1.1318 | 0.1793 |
| CONTESTANT_G_meerkat-20 | 2026-10-09 | 2026-10-16 | 0.7825 | 0.7090 | CONTESTANT_A_meerkat-20 | 0.6326 | 0.1499 |
| CONTESTANT_G_meerkat-30 | 2026-10-09 | 2026-10-16 | -0.2482 | 1.6341 | CONTESTANT_A_meerkat-30 | -0.4350 | 0.1867 |
| CONTESTANT_G_meerkat-40 | 2026-10-09 | 2026-10-16 | 0.0101 | 0.8829 | CONTESTANT_A_meerkat-40 | 0.2078 | -0.1977 |
| CONTESTANT_G_meerkat-50 | 2026-10-09 | 2026-10-16 | -0.9992 | 1.5107 | CONTESTANT_A_meerkat-50 | -0.7767 | -0.2225 |
| CONTESTANT_G_meerkat-60 | 2026-10-09 | 2026-10-16 | -2.9661 | 3.2123 | CONTESTANT_A_meerkat-60 | -3.2570 | 0.2909 |
| CONTESTANT_G_meerkat-70 | 2026-10-09 | 2026-10-16 | -4.3636 | 4.8715 | CONTESTANT_A_meerkat-70 | -4.2022 | -0.1614 |
| CONTESTANT_G_meerkat-80 | 2026-10-09 | 2026-10-16 | -5.1837 | 5.4514 | CONTESTANT_A_meerkat-80 | -5.2319 | 0.0483 |
| CONTESTANT_G_meerkat-90 | 2026-10-09 | 2026-10-16 | -4.5819 | 5.3401 | CONTESTANT_A_meerkat-90 | -5.2705 | 0.6887 |
| CONTESTANT_G_eagle-5-1 | 2026-10-09 | 2026-10-16 | 0.4246 | 1.6214 | CONTESTANT_A_eagle-5-1 | -5.8545 | 6.2790 |
| CONTESTANT_G_eagle-11-2 | 2026-10-09 | 2026-10-16 | 1.1960 | 0.3510 | CONTESTANT_A_eagle-11-2 | -3.3249 | 4.5210 |
| CONTESTANT_G_eagle-44-6 | 2026-10-09 | 2026-10-16 | 1.4230 | 0.6561 | CONTESTANT_A_eagle-44-6 | 1.0526 | 0.3704 |
| CONTESTANT_G_eagle-66-9 | 2026-10-09 | 2026-10-16 | 1.5117 | 0.6552 | CONTESTANT_A_eagle-66-9 | 1.1786 | 0.3331 |
| CONTESTANT_G_eagle-88-12 | 2026-10-09 | 2026-10-16 | 1.0430 | 0.6599 | CONTESTANT_A_eagle-88-12 | 0.8639 | 0.1791 |
| CONTESTANT_G_whale-shark | 2026-10-09 | 2026-10-16 | 0.2805 | 0.7824 | CONTESTANT_A_whale-shark | -0.0003 | 0.2808 |
