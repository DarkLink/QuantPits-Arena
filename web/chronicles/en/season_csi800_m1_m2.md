# season_csi800 — repaired baseline through 2026-08-28

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-07-03; cutoff: 2026-08-28. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-07-03 → 2026-08-28: 40 return sessions, 41 NAV observations including the reporting anchor; 8 scheduled rebalances.
- Period leader CONTESTANT_A_sloth-2: +13.6564%; end NAV 1.136564.
- Cumulative leader CONTESTANT_A_sloth-2: +13.6564%; end NAV 1.136564.
- 84/168 contestant paths gained during this segment; median path return -0.0512%.
- Market index segment return -6.2085%; end normalized NAV 0.937915.
- Taotie +0.4546% for the segment, end NAV 1.004546; Ghost scenario -3.4824%, NAV 0.965176.
- Cumulative leader raw p=9.9999e-06, Bonferroni p=0.00839992; N=100,000 per matched random spec.
- At this cutoff: 49/168 raw p<0.05 and 7/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | 13.6564 | 13.6564 | 1.1366 | 4.5330 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-1 | 12.3744 | 12.3744 | 1.1237 | 10.4228 | 7.99992e-05 | 0.0671993 |
| CONTESTANT_B_rabbit-2 | 11.5978 | 11.5978 | 1.1160 | 9.7943 | 6.99993e-05 | 0.0587994 |
| CONTESTANT_C_sloth-2 | 11.1191 | 11.1191 | 1.1112 | 3.7804 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_D_meerkat-10 | 9.3915 | 9.3915 | 1.0939 | 1.7361 | 0.000299997 | 0.251997 |
| CONTESTANT_A_rabbit-1 | 8.6274 | 8.6274 | 1.0863 | 10.1074 | 0.00137999 | 1 |
| CONTESTANT_B_rabbit-1 | 8.1445 | 8.1445 | 1.0814 | 10.9683 | 0.00217998 | 1 |
| CONTESTANT_A_rabbit-2 | 8.0647 | 8.0647 | 1.0806 | 11.4412 | 0.00151998 | 1 |
| CONTESTANT_B_sloth-1 | 8.0082 | 8.0082 | 1.0801 | 4.0327 | 0.00120999 | 1 |
| CONTESTANT_A_sloth-1 | 7.7341 | 7.7341 | 1.0773 | 5.5296 | 0.00145999 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | 13.6564 | 13.6564 | 1.1366 | 4.5330 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-1 | 12.3744 | 12.3744 | 1.1237 | 10.4228 | 7.99992e-05 | 0.0671993 |
| CONTESTANT_B_rabbit-2 | 11.5978 | 11.5978 | 1.1160 | 9.7943 | 6.99993e-05 | 0.0587994 |
| CONTESTANT_C_sloth-2 | 11.1191 | 11.1191 | 1.1112 | 3.7804 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_D_meerkat-10 | 9.3915 | 9.3915 | 1.0939 | 1.7361 | 0.000299997 | 0.251997 |
| CONTESTANT_A_rabbit-1 | 8.6274 | 8.6274 | 1.0863 | 10.1074 | 0.00137999 | 1 |
| CONTESTANT_B_rabbit-1 | 8.1445 | 8.1445 | 1.0814 | 10.9683 | 0.00217998 | 1 |
| CONTESTANT_A_rabbit-2 | 8.0647 | 8.0647 | 1.0806 | 11.4412 | 0.00151998 | 1 |
| CONTESTANT_B_sloth-1 | 8.0082 | 8.0082 | 1.0801 | 4.0327 | 0.00120999 | 1 |
| CONTESTANT_A_sloth-1 | 7.7341 | 7.7341 | 1.0773 | 5.5296 | 0.00145999 | 1 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_D_koala | -14.2918 | -14.2918 | 0.8571 | 18.8378 | 0.99993 | 1 |
| CONTESTANT_B_meerkat-90 | -16.5258 | -16.5258 | 0.8347 | 20.2328 | 1 | 1 |
| CONTESTANT_C_koala | -19.9334 | -19.9334 | 0.8007 | 23.2748 | 1 | 1 |
| CONTESTANT_B_koala | -22.0185 | -22.0185 | 0.7798 | 25.7498 | 1 | 1 |
| CONTESTANT_A_koala | -27.5350 | -27.5350 | 0.7247 | 32.4122 | 1 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | 1.2844 | 3.7356 | 19 | 13.6564 | -27.5350 | 8.5842 |
| CONTESTANT_B | 2.0995 | 4.7449 | 23 | 11.5978 | -22.0185 | 7.1769 |
| CONTESTANT_C | -1.0113 | -0.1342 | 13 | 11.1191 | -19.9334 | 9.0430 |
| CONTESTANT_D | 1.3865 | 1.4439 | 17 | 12.3744 | -14.2918 | 6.7894 |
| CONTESTANT_E | -2.1297 | -2.4912 | 7 | 5.5585 | -8.2275 | 7.3395 |
| CONTESTANT_F | -3.8119 | -3.9506 | 5 | 5.8178 | -13.2444 | 7.9627 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -1.3638 | 0.5280 | 5.0158 | -13.1480 |
| eagle-44-6 | 1.3367 | 2.7785 | 6.2848 | -5.1436 |
| eagle-5-1 | -3.5586 | -3.3900 | 6.3206 | -13.2444 |
| eagle-66-9 | 1.5425 | 2.5985 | 6.2031 | -4.0558 |
| eagle-88-12 | 2.8683 | 4.2774 | 6.1740 | -1.9814 |
| koala | -14.7426 | -17.1126 | -0.3185 | -27.5350 |
| meerkat-10 | 1.7767 | 0.1385 | 9.3915 | -2.5246 |
| meerkat-20 | 0.2577 | 1.0900 | 5.0393 | -6.7844 |
| meerkat-30 | 0.1736 | 0.6890 | 3.0599 | -4.0977 |
| meerkat-40 | -0.5859 | -0.2878 | 5.3021 | -6.2233 |
| meerkat-50 | -0.6333 | -2.9636 | 5.9833 | -5.6413 |
| meerkat-60 | -1.5986 | -2.4722 | 2.4868 | -4.6113 |
| meerkat-70 | -3.5568 | -3.2973 | 2.1281 | -9.7951 |
| meerkat-80 | -2.9415 | -4.5989 | 3.9392 | -7.3755 |
| meerkat-90 | -6.1359 | -5.4786 | 1.2368 | -16.5258 |
| rabbit-1 | 2.7207 | 2.8433 | 12.3744 | -6.9444 |
| rabbit-2 | 3.2899 | 5.4169 | 11.5978 | -7.7679 |
| robot | -0.2038 | 1.6930 | 4.5390 | -7.9663 |
| sloth-1 | 3.4799 | 4.9884 | 8.0082 | -3.5897 |
| sloth-2 | 8.0909 | 6.5205 | 13.6564 | 5.3202 |
| sloth-3 | 3.9203 | 3.7747 | 7.1005 | 0.5404 |
| sloth-4 | 1.4898 | 0.9601 | 4.6953 | -0.4730 |
| snail-1 | 0.5354 | 1.9425 | 4.9508 | -7.0668 |
| snail-2 | -0.4299 | 0.1043 | 4.3894 | -4.9598 |
| snail-3 | -4.1705 | -4.0548 | 0.0073 | -8.2275 |
| snail-4 | -3.7588 | -3.6499 | 0.4540 | -7.5656 |
| turtle | -2.1885 | -2.7269 | 1.7484 | -5.4726 |
| whale-shark | 4.2014 | 5.3287 | 7.2317 | 0.4711 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 19.5650 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
