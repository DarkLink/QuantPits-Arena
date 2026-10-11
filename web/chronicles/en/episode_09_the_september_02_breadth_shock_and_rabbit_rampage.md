# season_01 — repaired dispatch through 2026-09-04

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-08-28; cutoff: 2026-09-04. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-08-28 → 2026-09-04: 5 return sessions, 6 NAV observations including the reporting anchor; 1 scheduled rebalances.
- Period leader CONTESTANT_D_rabbit-1: +2.4500%; end NAV 1.151278.
- Cumulative leader CONTESTANT_B_eagle-5-1: +17.0720%; end NAV 1.170720.
- 62/168 contestant paths gained during this segment; median path return -0.4037%.
- Market index segment return -1.3263%; end normalized NAV 0.939259.
- Taotie +0.3282% for the segment, end NAV 1.026586; Ghost scenario -0.1735%, NAV 1.001964.
- Cumulative leader raw p=0.00563994, Bonferroni p=1; N=100,000 per matched random spec.
- At this cutoff: 53/168 raw p<0.05 and 12/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_D_rabbit-1 | 2.4500 | 15.1278 | 1.1513 | 0.2264 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_meerkat-50 | 2.2451 | 4.0524 | 1.0405 | 0.8143 | 0.127249 | 1 |
| CONTESTANT_B_rabbit-1 | 2.1438 | 13.1379 | 1.1314 | 0.5869 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_B_rabbit-2 | 2.0750 | 11.2132 | 1.1121 | 0.5943 | 0.000209998 | 0.176398 |
| CONTESTANT_D_rabbit-2 | 1.8910 | 12.9974 | 1.1300 | 0.3720 | 5.99994e-05 | 0.0503995 |
| CONTESTANT_E_eagle-5-1 | 1.6923 | 9.7202 | 1.0972 | 0.7192 | 0.0668693 | 1 |
| CONTESTANT_A_meerkat-20 | 1.6767 | 6.4087 | 1.0641 | 0.4126 | 0.0244498 | 1 |
| CONTESTANT_B_eagle-88-12 | 1.4498 | 8.7937 | 1.0879 | 0.4469 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_meerkat-20 | 1.4353 | 8.9555 | 1.0896 | 0.1380 | 0.00220998 | 1 |
| CONTESTANT_A_meerkat-30 | 1.4051 | 6.1750 | 1.0618 | 0.7903 | 0.0297097 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | -2.1996 | 17.0720 | 1.1707 | 2.1996 | 0.00563994 | 1 |
| CONTESTANT_D_rabbit-1 | 2.4500 | 15.1278 | 1.1513 | 0.2264 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_rabbit-1 | 1.0358 | 14.3063 | 1.1431 | 0.7265 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-1 | 2.1438 | 13.1379 | 1.1314 | 0.5869 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_D_rabbit-2 | 1.8910 | 12.9974 | 1.1300 | 0.3720 | 5.99994e-05 | 0.0503995 |
| CONTESTANT_D_eagle-11-2 | -0.4044 | 12.5057 | 1.1251 | 1.2362 | 0.00246998 | 1 |
| CONTESTANT_B_eagle-44-6 | 1.2429 | 12.1212 | 1.1212 | 0.3991 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_rabbit-2 | 1.0731 | 11.5862 | 1.1159 | 0.5583 | 0.000179998 | 0.151198 |
| CONTESTANT_B_rabbit-2 | 2.0750 | 11.2132 | 1.1121 | 0.5943 | 0.000209998 | 0.176398 |
| CONTESTANT_B_robot | -0.8829 | 11.0771 | 1.1108 | 1.4530 | 0.000239998 | 0.201598 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | -4.2847 | 4.5645 | 1.0456 | 4.6408 | 0.0936791 | 1 |
| CONTESTANT_A_snail-3 | -4.3922 | -0.7077 | 0.9929 | 4.5073 | 0.695603 | 1 |
| CONTESTANT_A_sloth-3 | -4.5644 | 1.2592 | 1.0126 | 4.6615 | 0.433356 | 1 |
| CONTESTANT_A_eagle-5-1 | -4.6476 | 7.4376 | 1.0744 | 6.1793 | 0.125079 | 1 |
| CONTESTANT_C_eagle-5-1 | -4.8423 | 6.7096 | 1.0671 | 4.8423 | 0.149059 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -1.4756 | -1.4040 | 11 | 1.6767 | -4.6476 | 2.4535 |
| CONTESTANT_B | -0.7811 | -0.9552 | 12 | 2.2451 | -4.2363 | 1.8604 |
| CONTESTANT_C | -0.8709 | -0.9531 | 13 | 1.3683 | -4.8423 | 1.7468 |
| CONTESTANT_D | -0.6402 | -0.3449 | 13 | 2.4500 | -4.2663 | 1.6715 |
| CONTESTANT_E | -0.2584 | -0.2734 | 8 | 1.6923 | -1.5566 | 1.3402 |
| CONTESTANT_F | -0.5230 | -0.3968 | 5 | 0.6301 | -2.4639 | 1.4912 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -1.0859 | -1.0005 | 0.7410 | -3.2711 |
| eagle-44-6 | 0.5045 | 0.3200 | 1.2467 | -0.0926 |
| eagle-5-1 | -2.4659 | -2.6313 | 1.6923 | -4.8423 |
| eagle-66-9 | 0.5879 | 0.6458 | 1.3800 | -0.3798 |
| eagle-88-12 | 0.7861 | 0.9468 | 1.4498 | 0.0376 |
| koala | -0.6964 | -0.7714 | 0.6301 | -1.6225 |
| meerkat-10 | 0.4233 | 0.6253 | 1.3193 | -0.9639 |
| meerkat-20 | 0.6941 | 0.6845 | 1.6767 | -0.2899 |
| meerkat-30 | 0.5360 | 0.7967 | 1.4051 | -1.3976 |
| meerkat-40 | -0.3241 | -0.3826 | 1.1590 | -1.5823 |
| meerkat-50 | -0.0284 | 0.1484 | 2.2451 | -2.4639 |
| meerkat-60 | -0.1412 | 0.0345 | 0.5091 | -1.1384 |
| meerkat-70 | -0.0657 | 0.1941 | 0.9869 | -1.8734 |
| meerkat-80 | -0.9188 | -0.6238 | -0.2681 | -2.0657 |
| meerkat-90 | -1.2617 | -1.2574 | 0.1441 | -2.4106 |
| rabbit-1 | 0.9625 | 0.7226 | 2.4500 | -0.4045 |
| rabbit-2 | 0.8828 | 1.1208 | 2.0750 | -0.5061 |
| robot | -0.8258 | -0.7506 | 0.3499 | -2.1764 |
| sloth-1 | -1.4434 | -1.2970 | -0.3406 | -3.2695 |
| sloth-2 | -2.0919 | -2.5005 | -0.1516 | -4.2847 |
| sloth-3 | -2.4331 | -2.8246 | -0.3416 | -4.5644 |
| sloth-4 | -2.7555 | -3.5233 | -0.4031 | -4.2663 |
| snail-1 | -1.5046 | -1.3696 | -0.3560 | -3.3863 |
| snail-2 | -2.0592 | -2.5514 | -0.0046 | -4.2497 |
| snail-3 | -2.3088 | -2.6124 | -0.2338 | -4.3922 |
| snail-4 | -2.6223 | -3.2795 | -0.2570 | -4.2363 |
| turtle | -2.1933 | -2.2094 | -0.7123 | -3.7248 |
| whale-shark | 0.6189 | 0.8504 | 0.9670 | 0.0167 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 6.5346 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
