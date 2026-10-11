# season_csi300 — repaired baseline through 2026-08-28

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-07-03; cutoff: 2026-08-28. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-07-03 → 2026-08-28: 40 return sessions, 41 NAV observations including the reporting anchor; 8 scheduled rebalances.
- Period leader CONTESTANT_B_eagle-5-1: +19.4532%; end NAV 1.194532.
- Cumulative leader CONTESTANT_B_eagle-5-1: +19.4532%; end NAV 1.194532.
- 128/168 contestant paths gained during this segment; median path return +2.8700%.
- Market index segment return -4.8117%; end normalized NAV 0.951883.
- Taotie +1.5364% for the segment, end NAV 1.015364; Ghost scenario -1.5293%, NAV 0.984707.
- Cumulative leader raw p=0.00180998, Bonferroni p=1; N=100,000 per matched random spec.
- At this cutoff: 63/168 raw p<0.05 and 5/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 19.4532 | 19.4532 | 1.1945 | 4.9422 | 0.00180998 | 1 |
| CONTESTANT_D_rabbit-1 | 16.5743 | 16.5743 | 1.1657 | 3.7570 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-2 | 16.0556 | 16.0556 | 1.1606 | 5.3217 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-11-2 | 14.3688 | 14.3688 | 1.1437 | 6.2653 | 0.000419996 | 0.352796 |
| CONTESTANT_B_rabbit-1 | 11.9903 | 11.9903 | 1.1199 | 3.7343 | 0.000149999 | 0.125999 |
| CONTESTANT_C_rabbit-2 | 11.4998 | 11.4998 | 1.1150 | 3.6595 | 0.000129999 | 0.109199 |
| CONTESTANT_A_rabbit-1 | 11.2171 | 11.2171 | 1.1122 | 5.5752 | 0.000319997 | 0.268797 |
| CONTESTANT_A_eagle-11-2 | 11.0846 | 11.0846 | 1.1108 | 6.8793 | 0.00367996 | 1 |
| CONTESTANT_B_sloth-2 | 11.0563 | 11.0563 | 1.1106 | 3.3673 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_B_rabbit-2 | 10.9070 | 10.9070 | 1.1091 | 4.5218 | 0.000299997 | 0.251997 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 19.4532 | 19.4532 | 1.1945 | 4.9422 | 0.00180998 | 1 |
| CONTESTANT_D_rabbit-1 | 16.5743 | 16.5743 | 1.1657 | 3.7570 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-2 | 16.0556 | 16.0556 | 1.1606 | 5.3217 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-11-2 | 14.3688 | 14.3688 | 1.1437 | 6.2653 | 0.000419996 | 0.352796 |
| CONTESTANT_B_rabbit-1 | 11.9903 | 11.9903 | 1.1199 | 3.7343 | 0.000149999 | 0.125999 |
| CONTESTANT_C_rabbit-2 | 11.4998 | 11.4998 | 1.1150 | 3.6595 | 0.000129999 | 0.109199 |
| CONTESTANT_A_rabbit-1 | 11.2171 | 11.2171 | 1.1122 | 5.5752 | 0.000319997 | 0.268797 |
| CONTESTANT_A_eagle-11-2 | 11.0846 | 11.0846 | 1.1108 | 6.8793 | 0.00367996 | 1 |
| CONTESTANT_B_sloth-2 | 11.0563 | 11.0563 | 1.1106 | 3.3673 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_B_rabbit-2 | 10.9070 | 10.9070 | 1.1091 | 4.5218 | 0.000299997 | 0.251997 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_meerkat-90 | -8.7876 | -8.7876 | 0.9121 | 13.1393 | 0.99933 | 1 |
| CONTESTANT_D_koala | -12.6579 | -12.6579 | 0.8734 | 14.3419 | 1 | 1 |
| CONTESTANT_C_koala | -14.4147 | -14.4147 | 0.8559 | 17.0261 | 1 | 1 |
| CONTESTANT_A_koala | -15.2915 | -15.2915 | 0.8471 | 18.0433 | 1 | 1 |
| CONTESTANT_B_koala | -16.5698 | -16.5698 | 0.8343 | 18.3770 | 1 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | 3.6839 | 4.9681 | 23 | 11.2171 | -15.2915 | 5.2387 |
| CONTESTANT_B | 5.5716 | 6.5896 | 23 | 19.4532 | -16.5698 | 4.7040 |
| CONTESTANT_C | 3.2167 | 4.8422 | 22 | 11.4998 | -14.4147 | 5.5968 |
| CONTESTANT_D | 4.5136 | 6.0346 | 21 | 16.5743 | -12.6579 | 4.0078 |
| CONTESTANT_E | 0.7835 | 0.6754 | 17 | 5.5449 | -3.3200 | 4.0326 |
| CONTESTANT_F | 1.0765 | 1.2977 | 22 | 4.1998 | -4.3655 | 3.9168 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | 7.0644 | 8.2234 | 14.3688 | -0.3733 |
| eagle-44-6 | 5.4601 | 6.4886 | 8.4492 | 1.3777 |
| eagle-5-1 | 6.1314 | 4.4130 | 19.4532 | -0.8849 |
| eagle-66-9 | 4.6357 | 5.7141 | 6.4941 | 1.0869 |
| eagle-88-12 | 5.1469 | 6.1347 | 7.4995 | 1.2512 |
| koala | -9.8191 | -13.5363 | 1.1100 | -16.5698 |
| meerkat-10 | 4.3001 | 6.2452 | 7.8932 | -3.9790 |
| meerkat-20 | 4.0151 | 3.8977 | 8.4973 | 1.1355 |
| meerkat-30 | 5.2954 | 5.0458 | 8.7494 | 2.8043 |
| meerkat-40 | 2.0738 | 1.4404 | 6.3818 | -2.2937 |
| meerkat-50 | 2.0140 | 1.3878 | 5.4709 | -0.7318 |
| meerkat-60 | 1.6282 | 1.1898 | 3.5933 | -0.1941 |
| meerkat-70 | -2.6741 | -2.1832 | -0.6116 | -4.9754 |
| meerkat-80 | -1.7105 | -1.6197 | 3.7857 | -6.5618 |
| meerkat-90 | -4.3234 | -4.5995 | 0.6096 | -8.7876 |
| rabbit-1 | 7.5671 | 8.5301 | 16.5743 | -1.6334 |
| rabbit-2 | 7.6906 | 10.4971 | 16.0556 | -3.3200 |
| robot | 5.7848 | 6.2783 | 10.5362 | 0.1324 |
| sloth-1 | 6.1065 | 6.5210 | 10.5650 | 1.3442 |
| sloth-2 | 5.5753 | 6.0464 | 11.0563 | -0.3352 |
| sloth-3 | 3.1988 | 2.9839 | 4.9665 | 1.8959 |
| sloth-4 | 1.3402 | 0.7617 | 7.0716 | -1.2453 |
| snail-1 | 4.8229 | 5.0917 | 9.4971 | 0.0077 |
| snail-2 | 3.1440 | 3.2214 | 9.4804 | -2.4610 |
| snail-3 | 1.9703 | 1.7039 | 6.6851 | -1.1870 |
| snail-4 | 2.3834 | 2.6746 | 4.5313 | -1.8278 |
| turtle | 4.5873 | 5.3820 | 9.4065 | -0.5118 |
| whale-shark | 4.5379 | 4.4708 | 5.3309 | 3.9049 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 20.3381 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
