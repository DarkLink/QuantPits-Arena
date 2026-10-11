# season_csi500 — repaired baseline through 2026-08-28

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-07-03; cutoff: 2026-08-28. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-07-03 → 2026-08-28: 40 return sessions, 41 NAV observations including the reporting anchor; 8 scheduled rebalances.
- Period leader CONTESTANT_A_sloth-2: +12.5267%; end NAV 1.125267.
- Cumulative leader CONTESTANT_A_sloth-2: +12.5267%; end NAV 1.125267.
- 82/168 contestant paths gained during this segment; median path return -0.1795%.
- Market index segment return -9.7174%; end normalized NAV 0.902826.
- Taotie +0.9028% for the segment, end NAV 1.009028; Ghost scenario -4.3035%, NAV 0.956965.
- Cumulative leader raw p=9.9999e-06, Bonferroni p=0.00839992; N=100,000 per matched random spec.
- At this cutoff: 56/168 raw p<0.05 and 9/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | 12.5267 | 12.5267 | 1.1253 | 5.0766 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-5-1 | 10.9544 | 10.9544 | 1.1095 | 11.9115 | 0.0234098 | 1 |
| CONTESTANT_A_sloth-1 | 10.7786 | 10.7786 | 1.1078 | 5.8220 | 4.99995e-05 | 0.0419996 |
| CONTESTANT_C_sloth-2 | 10.5625 | 10.5625 | 1.1056 | 4.6242 | 5.99994e-05 | 0.0503995 |
| CONTESTANT_D_rabbit-1 | 10.4477 | 10.4477 | 1.1045 | 10.2636 | 8.99991e-05 | 0.0755992 |
| CONTESTANT_B_rabbit-1 | 9.4683 | 9.4683 | 1.0947 | 8.3355 | 0.000229998 | 0.193198 |
| CONTESTANT_B_rabbit-2 | 8.9081 | 8.9081 | 1.0891 | 8.9561 | 0.000309997 | 0.260397 |
| CONTESTANT_B_sloth-1 | 8.9028 | 8.9028 | 1.0890 | 4.2451 | 0.000259997 | 0.218398 |
| CONTESTANT_A_snail-1 | 8.2977 | 8.2977 | 1.0830 | 7.2261 | 0.000389996 | 0.327597 |
| CONTESTANT_A_eagle-11-2 | 8.2832 | 8.2832 | 1.0828 | 15.1663 | 0.00873991 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | 12.5267 | 12.5267 | 1.1253 | 5.0766 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-5-1 | 10.9544 | 10.9544 | 1.1095 | 11.9115 | 0.0234098 | 1 |
| CONTESTANT_A_sloth-1 | 10.7786 | 10.7786 | 1.1078 | 5.8220 | 4.99995e-05 | 0.0419996 |
| CONTESTANT_C_sloth-2 | 10.5625 | 10.5625 | 1.1056 | 4.6242 | 5.99994e-05 | 0.0503995 |
| CONTESTANT_D_rabbit-1 | 10.4477 | 10.4477 | 1.1045 | 10.2636 | 8.99991e-05 | 0.0755992 |
| CONTESTANT_B_rabbit-1 | 9.4683 | 9.4683 | 1.0947 | 8.3355 | 0.000229998 | 0.193198 |
| CONTESTANT_B_rabbit-2 | 8.9081 | 8.9081 | 1.0891 | 8.9561 | 0.000309997 | 0.260397 |
| CONTESTANT_B_sloth-1 | 8.9028 | 8.9028 | 1.0890 | 4.2451 | 0.000259997 | 0.218398 |
| CONTESTANT_A_snail-1 | 8.2977 | 8.2977 | 1.0830 | 7.2261 | 0.000389996 | 0.327597 |
| CONTESTANT_A_eagle-11-2 | 8.2832 | 8.2832 | 1.0828 | 15.1663 | 0.00873991 | 1 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_E_eagle-5-1 | -18.2807 | -18.2807 | 0.8172 | 21.0777 | 0.97012 | 1 |
| CONTESTANT_C_koala | -19.1637 | -19.1637 | 0.8084 | 24.6696 | 1 | 1 |
| CONTESTANT_B_meerkat-90 | -20.1578 | -20.1578 | 0.7984 | 22.6646 | 1 | 1 |
| CONTESTANT_B_koala | -24.6664 | -24.6664 | 0.7533 | 26.7200 | 1 | 1 |
| CONTESTANT_A_koala | -25.3201 | -25.3201 | 0.7468 | 29.6022 | 1 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | 1.6126 | 3.7774 | 21 | 12.5267 | -25.3201 | 8.8785 |
| CONTESTANT_B | 1.2161 | 3.0444 | 18 | 10.9544 | -24.6664 | 7.7023 |
| CONTESTANT_C | -0.5364 | 0.7963 | 16 | 10.5625 | -19.1637 | 8.9641 |
| CONTESTANT_D | 0.9377 | 1.4341 | 17 | 10.4477 | -13.6728 | 7.8692 |
| CONTESTANT_E | -3.6349 | -3.5546 | 6 | 6.9111 | -18.2807 | 8.6082 |
| CONTESTANT_F | -3.4817 | -3.4104 | 4 | 1.8972 | -10.8058 | 7.9409 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -2.6203 | -2.6097 | 8.2832 | -13.4018 |
| eagle-44-6 | 1.5589 | 2.7103 | 5.5392 | -3.7401 |
| eagle-5-1 | -1.2049 | 2.1243 | 10.9544 | -18.2807 |
| eagle-66-9 | 1.5959 | 2.4882 | 6.7307 | -3.9062 |
| eagle-88-12 | 2.9925 | 3.8163 | 6.1171 | -1.0225 |
| koala | -14.4027 | -16.4182 | -1.4679 | -25.3201 |
| meerkat-10 | -0.3598 | 1.8593 | 3.0998 | -6.4786 |
| meerkat-20 | 0.0767 | 1.1448 | 3.2097 | -4.6373 |
| meerkat-30 | -1.3238 | -0.1864 | 4.1064 | -10.4081 |
| meerkat-40 | -0.3786 | -0.0245 | 3.7280 | -5.1543 |
| meerkat-50 | -1.1497 | -3.2512 | 6.9111 | -4.7904 |
| meerkat-60 | -4.3642 | -4.6316 | -1.3825 | -6.1998 |
| meerkat-70 | -3.9351 | -4.3654 | 1.8972 | -9.7934 |
| meerkat-80 | -7.6873 | -5.8577 | -3.1088 | -15.1348 |
| meerkat-90 | -8.5681 | -7.6835 | -1.5266 | -20.1578 |
| rabbit-1 | 2.6153 | 3.3404 | 10.4477 | -7.5156 |
| rabbit-2 | 2.2876 | 4.2546 | 8.9081 | -7.3362 |
| robot | 0.4037 | 1.0120 | 6.5078 | -6.7270 |
| sloth-1 | 4.5692 | 5.1449 | 10.7786 | -2.5089 |
| sloth-2 | 6.3903 | 7.1344 | 12.5267 | 0.4508 |
| sloth-3 | 4.1648 | 4.5365 | 6.3221 | 1.3048 |
| sloth-4 | 0.9971 | 1.0904 | 2.5901 | -0.8028 |
| snail-1 | 2.0668 | 1.9894 | 8.2977 | -3.2773 |
| snail-2 | -0.3675 | 1.6798 | 4.0520 | -6.7283 |
| snail-3 | -2.3750 | -1.2688 | -0.2815 | -5.5389 |
| snail-4 | -2.4269 | -1.2160 | -0.5536 | -5.9061 |
| turtle | -0.6249 | -0.4820 | 3.3614 | -4.7742 |
| whale-shark | 3.9323 | 5.6996 | 6.4885 | -0.9732 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 29.2350 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
