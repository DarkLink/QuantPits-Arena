# season_csi1000 — repaired dispatch through 2026-09-30

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-08-28; cutoff: 2026-09-30. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-08-28 → 2026-09-30: 22 return sessions, 23 NAV observations including the reporting anchor; 5 scheduled rebalances.
- Period leader CONTESTANT_B_eagle-5-1: +6.1803%; end NAV 1.140624.
- Cumulative leader CONTESTANT_A_sloth-2: +14.3581%; end NAV 1.143581.
- 6/168 contestant paths gained during this segment; median path return -3.9327%.
- Market index segment return -5.2720%; end normalized NAV 0.846653.
- Taotie -0.3035% for the segment, end NAV 1.003894; Ghost scenario -3.7150%, NAV 0.916306.
- Cumulative leader raw p=2.99997e-05, Bonferroni p=0.0251997; N=100,000 per matched random spec.
- At this cutoff: 53/168 raw p<0.05 and 3/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 6.1803 | 14.0624 | 1.1406 | 7.5661 | 0.0152098 | 1 |
| CONTESTANT_C_eagle-5-1 | 2.4684 | -2.2764 | 0.9772 | 7.3406 | 0.237008 | 1 |
| CONTESTANT_A_eagle-11-2 | 1.3215 | 7.6288 | 1.0763 | 6.3988 | 0.0123999 | 1 |
| CONTESTANT_D_eagle-5-1 | 0.4786 | -3.0099 | 0.9699 | 4.4944 | 0.261707 | 1 |
| CONTESTANT_B_meerkat-30 | 0.4230 | 0.4056 | 1.0041 | 4.0897 | 0.0396796 | 1 |
| CONTESTANT_A_snail-1 | 0.1464 | 3.5478 | 1.0355 | 4.8662 | 0.0099399 | 1 |
| CONTESTANT_A_sloth-1 | -0.1551 | 7.8218 | 1.0782 | 4.9486 | 0.00131999 | 1 |
| CONTESTANT_E_meerkat-60 | -0.2190 | -7.5943 | 0.9241 | 4.0513 | 0.512615 | 1 |
| CONTESTANT_B_turtle | -0.3613 | 3.1634 | 1.0316 | 5.9281 | 0.0136399 | 1 |
| CONTESTANT_B_eagle-11-2 | -0.3786 | -2.9314 | 0.9707 | 3.5597 | 0.194078 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | -3.0555 | 14.3581 | 1.1436 | 6.5568 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_B_eagle-5-1 | 6.1803 | 14.0624 | 1.1406 | 7.5661 | 0.0152098 | 1 |
| CONTESTANT_A_sloth-3 | -3.7925 | 10.5204 | 1.1052 | 7.4676 | 0.000309997 | 0.260397 |
| CONTESTANT_C_sloth-4 | -5.2943 | 10.3313 | 1.1033 | 7.0780 | 0.000369996 | 0.310797 |
| CONTESTANT_B_sloth-2 | -4.7697 | 9.6132 | 1.0961 | 6.4249 | 0.000559994 | 0.470395 |
| CONTESTANT_B_sloth-3 | -4.1128 | 8.0892 | 1.0809 | 6.0020 | 0.00115999 | 0.97439 |
| CONTESTANT_C_sloth-2 | -6.9076 | 7.9979 | 1.0800 | 7.0998 | 0.00119999 | 1 |
| CONTESTANT_A_sloth-1 | -0.1551 | 7.8218 | 1.0782 | 4.9486 | 0.00131999 | 1 |
| CONTESTANT_B_sloth-1 | -2.6663 | 7.8127 | 1.0781 | 5.8239 | 0.00131999 | 1 |
| CONTESTANT_A_eagle-11-2 | 1.3215 | 7.6288 | 1.0763 | 6.3988 | 0.0123999 | 1 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_koala | -7.3898 | -34.5134 | 0.6549 | 10.0322 | 1 | 1 |
| CONTESTANT_E_eagle-5-1 | -8.8906 | -10.9513 | 0.8905 | 9.3785 | 0.597404 | 1 |
| CONTESTANT_C_meerkat-70 | -9.0938 | -15.4206 | 0.8458 | 9.5502 | 0.98011 | 1 |
| CONTESTANT_B_meerkat-90 | -9.1046 | -24.4600 | 0.7554 | 10.0069 | 1 | 1 |
| CONTESTANT_E_meerkat-30 | -9.3830 | -10.4659 | 0.8953 | 10.5546 | 0.775102 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -2.6211 | -2.5947 | 2 | 1.3215 | -6.2930 | 5.5834 |
| CONTESTANT_B | -3.0631 | -2.7871 | 2 | 6.1803 | -9.1046 | 5.8455 |
| CONTESTANT_C | -4.2271 | -4.4430 | 1 | 2.4684 | -9.0938 | 6.4057 |
| CONTESTANT_D | -3.9372 | -3.7969 | 1 | 0.4786 | -7.1880 | 6.3262 |
| CONTESTANT_E | -4.7490 | -4.6879 | 0 | -0.2190 | -9.3830 | 6.5954 |
| CONTESTANT_F | -3.9066 | -4.1023 | 0 | -0.9607 | -6.8892 | 6.1364 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -2.5237 | -2.7793 | 1.3215 | -6.8892 |
| eagle-44-6 | -2.1917 | -2.3775 | -0.5783 | -4.2476 |
| eagle-5-1 | -0.8321 | -0.9207 | 6.1803 | -8.8906 |
| eagle-66-9 | -2.2512 | -2.5930 | -0.7155 | -3.1099 |
| eagle-88-12 | -3.0253 | -2.6117 | -1.9105 | -4.7606 |
| koala | -5.6634 | -6.1646 | -2.8165 | -7.3898 |
| meerkat-10 | -2.5848 | -2.5323 | -0.4558 | -4.5879 |
| meerkat-20 | -2.6565 | -2.5148 | -1.1956 | -4.2269 |
| meerkat-30 | -4.0589 | -4.1114 | 0.4230 | -9.3830 |
| meerkat-40 | -2.9495 | -2.6586 | -1.9248 | -5.1231 |
| meerkat-50 | -4.6327 | -5.1867 | -1.6342 | -5.9165 |
| meerkat-60 | -4.5325 | -4.7463 | -0.2190 | -7.1880 |
| meerkat-70 | -3.9283 | -2.9886 | -0.9607 | -9.0938 |
| meerkat-80 | -4.1703 | -4.1350 | -3.1907 | -5.3338 |
| meerkat-90 | -5.7459 | -5.9606 | -1.2319 | -9.1046 |
| rabbit-1 | -3.2269 | -3.4837 | -0.7351 | -5.0971 |
| rabbit-2 | -2.9009 | -2.2798 | -1.5773 | -5.6659 |
| robot | -2.9356 | -3.2334 | -0.7897 | -5.1176 |
| sloth-1 | -3.4709 | -3.1658 | -0.1551 | -5.8813 |
| sloth-2 | -4.9464 | -5.2292 | -2.8776 | -6.9076 |
| sloth-3 | -4.7426 | -4.3885 | -3.7925 | -6.2453 |
| sloth-4 | -5.4158 | -5.2107 | -4.2451 | -6.5996 |
| snail-1 | -3.4700 | -3.4814 | 0.1464 | -5.6905 |
| snail-2 | -4.9292 | -5.1726 | -3.0681 | -6.7556 |
| snail-3 | -4.6736 | -4.6824 | -3.6464 | -5.6218 |
| snail-4 | -5.2018 | -4.8909 | -4.0610 | -6.7924 |
| turtle | -3.9872 | -4.7938 | -0.3613 | -7.0497 |
| whale-shark | -3.3719 | -3.3231 | -2.5664 | -4.3614 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 15.0709 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.

## Separate October appendix

September 30 close to October 9 contains two return sessions. The holiday Monday produces no makeup rebalance. October is reported separately from September.

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_D_meerkat-10 | 2.1096 | 2.1677 | 1.0217 | -0.0000 | 0.0162 | 1.0000 |
| CONTESTANT_B_meerkat-20 | 1.9623 | 3.1393 | 1.0314 | -0.0000 | 0.0103 | 1.0000 |
| CONTESTANT_A_meerkat-90 | 1.6762 | -17.7344 | 0.8227 | 0.0321 | 0.9939 | 1.0000 |
| CONTESTANT_C_meerkat-90 | 1.4282 | -20.4469 | 0.7955 | 1.4468 | 0.9994 | 1.0000 |
| CONTESTANT_F_meerkat-90 | 1.3095 | -4.8700 | 0.9513 | 0.0279 | 0.2448 | 1.0000 |
| CONTESTANT_A_meerkat-10 | 1.2424 | 3.2013 | 1.0320 | -0.0000 | 0.0101 | 1.0000 |
| CONTESTANT_B_eagle-44-6 | 1.1986 | 5.4868 | 1.0549 | -0.0000 | 0.0002 | 0.1680 |
| CONTESTANT_B_robot | 1.1687 | 4.9498 | 1.0495 | -0.0000 | 0.0041 | 1.0000 |
| CONTESTANT_B_whale-shark | 1.1464 | 4.6976 | 1.0470 | -0.0000 | 0.0000 | 0.0168 |
| CONTESTANT_F_rabbit-2 | 1.1398 | -9.9526 | 0.9005 | -0.0000 | 0.6072 | 1.0000 |
