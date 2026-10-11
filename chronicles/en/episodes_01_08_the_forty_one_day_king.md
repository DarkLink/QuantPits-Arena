# season_01 — repaired baseline through 2026-08-28

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-07-03; cutoff: 2026-08-28. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-07-03 → 2026-08-28: 40 return sessions, 41 NAV observations including the reporting anchor; 8 scheduled rebalances.
- Period leader CONTESTANT_B_eagle-5-1: +19.7050%; end NAV 1.197050.
- Cumulative leader CONTESTANT_B_eagle-5-1: +19.7050%; end NAV 1.197050.
- 145/168 contestant paths gained during this segment; median path return +4.4656%.
- Market index segment return -4.8117%; end normalized NAV 0.951883.
- Taotie +2.3228% for the segment, end NAV 1.023228; Ghost scenario +0.3705%, NAV 1.003705.
- Cumulative leader raw p=0.00171998, Bonferroni p=1; N=100,000 per matched random spec.
- At this cutoff: 68/168 raw p<0.05 and 9/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 19.7050 | 19.7050 | 1.1971 | 7.1286 | 0.00171998 | 1 |
| CONTESTANT_A_eagle-11-2 | 14.6836 | 14.6836 | 1.1468 | 6.5849 | 0.000399996 | 0.335997 |
| CONTESTANT_A_rabbit-1 | 13.1345 | 13.1345 | 1.1313 | 4.0574 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_D_eagle-11-2 | 12.9625 | 12.9625 | 1.1296 | 2.5349 | 0.00143999 | 1 |
| CONTESTANT_D_eagle-5-1 | 12.7888 | 12.7888 | 1.1279 | 3.3810 | 0.0237398 | 1 |
| CONTESTANT_A_eagle-5-1 | 12.6742 | 12.6742 | 1.1267 | 8.1718 | 0.0246598 | 1 |
| CONTESTANT_B_sloth-1 | 12.4160 | 12.4160 | 1.1242 | 4.2772 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_D_rabbit-1 | 12.3746 | 12.3746 | 1.1237 | 5.0213 | 7.99992e-05 | 0.0671993 |
| CONTESTANT_C_eagle-5-1 | 12.1397 | 12.1397 | 1.1214 | 5.7589 | 0.0296897 | 1 |
| CONTESTANT_B_robot | 12.0665 | 12.0665 | 1.1207 | 5.6491 | 2.99997e-05 | 0.0251997 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 19.7050 | 19.7050 | 1.1971 | 7.1286 | 0.00171998 | 1 |
| CONTESTANT_A_eagle-11-2 | 14.6836 | 14.6836 | 1.1468 | 6.5849 | 0.000399996 | 0.335997 |
| CONTESTANT_A_rabbit-1 | 13.1345 | 13.1345 | 1.1313 | 4.0574 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_D_eagle-11-2 | 12.9625 | 12.9625 | 1.1296 | 2.5349 | 0.00143999 | 1 |
| CONTESTANT_D_eagle-5-1 | 12.7888 | 12.7888 | 1.1279 | 3.3810 | 0.0237398 | 1 |
| CONTESTANT_A_eagle-5-1 | 12.6742 | 12.6742 | 1.1267 | 8.1718 | 0.0246598 | 1 |
| CONTESTANT_B_sloth-1 | 12.4160 | 12.4160 | 1.1242 | 4.2772 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_D_rabbit-1 | 12.3746 | 12.3746 | 1.1237 | 5.0213 | 7.99992e-05 | 0.0671993 |
| CONTESTANT_C_eagle-5-1 | 12.1397 | 12.1397 | 1.1214 | 5.7589 | 0.0296897 | 1 |
| CONTESTANT_B_robot | 12.0665 | 12.0665 | 1.1207 | 5.6491 | 2.99997e-05 | 0.0251997 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_C_koala | -8.8381 | -8.8381 | 0.9116 | 11.4693 | 0.99979 | 1 |
| CONTESTANT_B_meerkat-90 | -10.3239 | -10.3239 | 0.8968 | 12.1729 | 0.99995 | 1 |
| CONTESTANT_A_koala | -10.4825 | -10.4825 | 0.8952 | 13.2716 | 0.99995 | 1 |
| CONTESTANT_B_koala | -10.5967 | -10.5967 | 0.8940 | 13.4733 | 0.99995 | 1 |
| CONTESTANT_D_koala | -13.5181 | -13.5181 | 0.8648 | 15.0155 | 1 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | 4.8457 | 4.9516 | 24 | 14.6836 | -10.4825 | 5.4608 |
| CONTESTANT_B | 5.9247 | 6.8361 | 24 | 19.7050 | -10.5967 | 5.2520 |
| CONTESTANT_C | 4.4946 | 5.7849 | 24 | 12.1397 | -8.8381 | 4.5068 |
| CONTESTANT_D | 4.2777 | 4.0727 | 26 | 12.9625 | -13.5181 | 4.5156 |
| CONTESTANT_E | 2.2310 | 2.3469 | 23 | 8.5629 | -3.0846 | 4.2381 |
| CONTESTANT_F | 2.7130 | 2.9257 | 24 | 8.5053 | -4.3023 | 3.5101 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | 9.1097 | 9.2272 | 14.6836 | 4.2060 |
| eagle-44-6 | 6.2724 | 6.6399 | 10.7448 | 1.2911 |
| eagle-5-1 | 12.2846 | 12.4069 | 19.7050 | 7.8943 |
| eagle-66-9 | 4.8030 | 5.4360 | 6.7084 | 1.3716 |
| eagle-88-12 | 5.4944 | 6.3649 | 7.2389 | 2.7008 |
| koala | -5.9361 | -9.6603 | 5.0966 | -13.5181 |
| meerkat-10 | 2.2955 | 2.6347 | 6.3438 | -0.8669 |
| meerkat-20 | 6.0007 | 6.8038 | 8.5629 | 1.0267 |
| meerkat-30 | 4.4227 | 4.9354 | 9.0557 | -1.3801 |
| meerkat-40 | 4.5979 | 4.3935 | 8.7673 | 0.7484 |
| meerkat-50 | 3.2293 | 2.3328 | 7.6162 | 0.6412 |
| meerkat-60 | 2.1415 | 2.1120 | 5.5790 | -0.8496 |
| meerkat-70 | -1.6977 | -1.1206 | 1.8723 | -6.6283 |
| meerkat-80 | -1.4962 | -0.7426 | 0.9553 | -7.4040 |
| meerkat-90 | -4.3346 | -3.6935 | -1.4732 | -10.3239 |
| rabbit-1 | 7.4105 | 7.9979 | 13.1345 | -1.9396 |
| rabbit-2 | 6.9181 | 7.8452 | 10.9002 | 0.7288 |
| robot | 7.0955 | 7.2998 | 12.0665 | 1.9929 |
| sloth-1 | 6.8889 | 6.9758 | 12.4160 | 2.7494 |
| sloth-2 | 7.2472 | 7.2442 | 9.2700 | 5.2235 |
| sloth-3 | 4.0457 | 4.1363 | 6.1021 | 1.9771 |
| sloth-4 | 1.7932 | 1.4481 | 4.2207 | 0.1702 |
| snail-1 | 5.1367 | 5.6697 | 9.2399 | 0.1347 |
| snail-2 | 3.7370 | 3.5042 | 6.8786 | 0.7588 |
| snail-3 | 3.8005 | 3.7113 | 8.0229 | 0.2431 |
| snail-4 | 3.5686 | 3.6516 | 6.7936 | 0.5818 |
| turtle | 5.2000 | 5.7939 | 10.5992 | 1.1443 |
| whale-shark | 4.2428 | 4.3250 | 5.9196 | 2.7509 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 11.8107 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
