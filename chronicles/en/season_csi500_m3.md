# season_csi500 — repaired dispatch through 2026-09-30

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-08-28; cutoff: 2026-09-30. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-08-28 → 2026-09-30: 22 return sessions, 23 NAV observations including the reporting anchor; 5 scheduled rebalances.
- Period leader CONTESTANT_A_meerkat-10: +0.3776%; end NAV 1.025008.
- Cumulative leader CONTESTANT_A_sloth-2: +8.1326%; end NAV 1.081326.
- 2/168 contestant paths gained during this segment; median path return -3.5231%.
- Market index segment return -5.8298%; end normalized NAV 0.850193.
- Taotie -1.0037% for the segment, end NAV 0.998900; Ghost scenario -4.3558%, NAV 0.915281.
- Cumulative leader raw p=2.99997e-05, Bonferroni p=0.0251997; N=100,000 per matched random spec.
- At this cutoff: 58/168 raw p<0.05 and 10/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_meerkat-10 | 0.3776 | 2.5008 | 1.0250 | 2.5481 | 0.00332997 | 1 |
| CONTESTANT_F_eagle-5-1 | 0.2471 | -10.5854 | 0.8941 | 7.7672 | 0.586144 | 1 |
| CONTESTANT_B_eagle-11-2 | -0.0733 | 2.9136 | 1.0291 | 3.5506 | 0.0188098 | 1 |
| CONTESTANT_B_sloth-4 | -0.7652 | -1.5618 | 0.9844 | 3.7621 | 0.0529895 | 1 |
| CONTESTANT_A_koala | -1.0405 | -26.0972 | 0.7390 | 6.0328 | 1 | 1 |
| CONTESTANT_C_meerkat-20 | -1.1173 | 2.0566 | 1.0206 | 2.7810 | 0.00479995 | 1 |
| CONTESTANT_B_snail-4 | -1.2437 | -1.7904 | 0.9821 | 3.7827 | 0.0602794 | 1 |
| CONTESTANT_B_turtle | -1.3810 | 1.9341 | 1.0193 | 4.2204 | 0.00653993 | 1 |
| CONTESTANT_B_robot | -1.4190 | 4.4100 | 1.0441 | 3.1597 | 0.000579994 | 0.487195 |
| CONTESTANT_B_sloth-1 | -1.5071 | 7.2615 | 1.0726 | 3.3664 | 6.99993e-05 | 0.0587994 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | -3.9050 | 8.1326 | 1.0813 | 6.3180 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_B_eagle-5-1 | -3.1274 | 7.4843 | 1.0748 | 4.8831 | 0.0246698 | 1 |
| CONTESTANT_B_sloth-1 | -1.5071 | 7.2615 | 1.0726 | 3.3664 | 6.99993e-05 | 0.0587994 |
| CONTESTANT_B_rabbit-1 | -2.1118 | 7.1565 | 1.0716 | 4.8020 | 0.000119999 | 0.100799 |
| CONTESTANT_D_rabbit-1 | -3.1257 | 6.9955 | 1.0700 | 4.6844 | 0.000139999 | 0.117599 |
| CONTESTANT_A_sloth-1 | -3.4490 | 6.9579 | 1.0696 | 6.3159 | 8.99991e-05 | 0.0755992 |
| CONTESTANT_B_rabbit-2 | -2.1348 | 6.5832 | 1.0658 | 4.8004 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_A_eagle-11-2 | -1.6782 | 6.4659 | 1.0647 | 7.0015 | 0.00348997 | 1 |
| CONTESTANT_D_robot | -1.8317 | 4.5569 | 1.0456 | 4.1474 | 0.000519995 | 0.436796 |
| CONTESTANT_B_snail-1 | -1.7260 | 4.5167 | 1.0452 | 3.4494 | 0.000519995 | 0.436796 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_F_rabbit-1 | -7.5604 | -10.6934 | 0.8931 | 7.7082 | 0.793922 | 1 |
| CONTESTANT_D_snail-3 | -7.5865 | -7.8466 | 0.9215 | 7.7835 | 0.557624 | 1 |
| CONTESTANT_D_sloth-4 | -8.3894 | -7.5122 | 0.9249 | 9.3784 | 0.519855 | 1 |
| CONTESTANT_E_meerkat-50 | -8.4101 | -2.0802 | 0.9792 | 8.8424 | 0.0704793 | 1 |
| CONTESTANT_D_snail-4 | -8.5731 | -9.6857 | 0.9031 | 9.5014 | 0.752622 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -3.4851 | -3.5739 | 1 | 0.3776 | -6.6376 | 5.7154 |
| CONTESTANT_B | -2.8657 | -2.6998 | 0 | -0.0733 | -7.2632 | 4.8076 |
| CONTESTANT_C | -4.4171 | -4.3531 | 0 | -1.1173 | -6.9481 | 6.2738 |
| CONTESTANT_D | -4.2083 | -3.5272 | 0 | -1.6804 | -8.5731 | 5.7432 |
| CONTESTANT_E | -3.7923 | -3.4003 | 0 | -1.6423 | -8.4101 | 5.4372 |
| CONTESTANT_F | -4.2277 | -4.2803 | 1 | 0.2471 | -7.5604 | 5.8699 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -3.1353 | -2.9781 | -0.0733 | -5.7842 |
| eagle-44-6 | -3.1431 | -3.4186 | -1.7516 | -4.3592 |
| eagle-5-1 | -4.1319 | -4.1626 | 0.2471 | -6.9481 |
| eagle-66-9 | -3.3206 | -3.2508 | -2.3452 | -4.5131 |
| eagle-88-12 | -3.5858 | -3.2919 | -2.6387 | -5.0007 |
| koala | -3.5180 | -3.7124 | -1.0405 | -5.2267 |
| meerkat-10 | -3.2855 | -3.1775 | 0.3776 | -7.0820 |
| meerkat-20 | -3.0977 | -2.9442 | -1.1173 | -4.9946 |
| meerkat-30 | -3.7798 | -3.5084 | -1.9093 | -6.4882 |
| meerkat-40 | -3.7447 | -3.7964 | -1.8342 | -6.2514 |
| meerkat-50 | -4.6814 | -4.1029 | -1.7306 | -8.4101 |
| meerkat-60 | -4.7011 | -4.9664 | -3.1055 | -5.8947 |
| meerkat-70 | -4.5024 | -4.1254 | -1.7438 | -7.2632 |
| meerkat-80 | -4.0304 | -3.3107 | -2.7610 | -6.7380 |
| meerkat-90 | -4.1295 | -3.9684 | -2.9097 | -5.8068 |
| rabbit-1 | -4.3159 | -4.0029 | -2.1118 | -7.5604 |
| rabbit-2 | -3.6645 | -3.6803 | -2.1348 | -4.9469 |
| robot | -3.4018 | -3.2036 | -1.4190 | -6.2473 |
| sloth-1 | -3.2547 | -3.4513 | -1.5071 | -5.1741 |
| sloth-2 | -4.3113 | -3.6255 | -2.5871 | -6.6079 |
| sloth-3 | -4.3033 | -3.7556 | -2.6295 | -7.2882 |
| sloth-4 | -3.7551 | -3.0629 | -0.7652 | -8.3894 |
| snail-1 | -3.4220 | -3.5439 | -1.7260 | -5.1943 |
| snail-2 | -4.3245 | -3.5559 | -2.3733 | -6.8851 |
| snail-3 | -4.3255 | -3.8617 | -2.8885 | -7.5865 |
| snail-4 | -3.9276 | -2.6221 | -1.2437 | -8.5731 |
| turtle | -3.8881 | -4.0266 | -1.3810 | -5.6965 |
| whale-shark | -3.6339 | -3.0089 | -2.3725 | -5.6900 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 7.1953 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.

## Separate October appendix

September 30 close to October 9 contains two return sessions. The holiday Monday produces no makeup rebalance. October is reported separately from September.

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_F_eagle-5-1 | 2.4719 | -8.3752 | 0.9162 | 0.0939 | 0.4387 | 1.0000 |
| CONTESTANT_D_eagle-11-2 | 1.6580 | 3.0084 | 1.0301 | -0.0000 | 0.0138 | 1.0000 |
| CONTESTANT_B_meerkat-10 | 1.6493 | 1.8275 | 1.0183 | -0.0000 | 0.0040 | 1.0000 |
| CONTESTANT_B_rabbit-1 | 1.5704 | 8.8393 | 1.0884 | -0.0000 | 0.0000 | 0.0168 |
| CONTESTANT_B_rabbit-2 | 1.5669 | 8.2532 | 1.0825 | -0.0000 | 0.0000 | 0.0168 |
| CONTESTANT_F_koala | 1.3960 | -4.3597 | 0.9564 | 0.2008 | 0.1712 | 1.0000 |
| CONTESTANT_F_meerkat-90 | 1.3732 | -3.6341 | 0.9637 | 0.0147 | 0.1258 | 1.0000 |
| CONTESTANT_A_meerkat-30 | 1.3438 | 1.8380 | 1.0184 | -0.0000 | 0.0039 | 1.0000 |
| CONTESTANT_B_eagle-44-6 | 1.3382 | 5.0782 | 1.0508 | -0.0000 | 0.0000 | 0.0084 |
| CONTESTANT_D_eagle-5-1 | 1.2956 | -3.4738 | 0.9653 | -0.0000 | 0.2245 | 1.0000 |
