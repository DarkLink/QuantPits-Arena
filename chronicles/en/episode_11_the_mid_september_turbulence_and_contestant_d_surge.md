# season_01 — repaired dispatch through 2026-09-18

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-09-11; cutoff: 2026-09-18. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-09-11 → 2026-09-18: 5 return sessions, 6 NAV observations including the reporting anchor; 1 scheduled rebalances.
- Period leader CONTESTANT_D_eagle-5-1: +1.7710%; end NAV 1.118308.
- Cumulative leader CONTESTANT_B_eagle-5-1: +16.9799%; end NAV 1.169799.
- 20/168 contestant paths gained during this segment; median path return -0.9409%.
- Market index segment return -0.0614%; end normalized NAV 0.930862.
- Taotie -0.5968% for the segment, end NAV 1.010970; Ghost scenario -0.7944%, NAV 0.975900.
- Cumulative leader raw p=0.00243998, Bonferroni p=1; N=100,000 per matched random spec.
- At this cutoff: 58/168 raw p<0.05 and 12/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_D_eagle-5-1 | 1.7710 | 11.8308 | 1.1183 | 0.4688 | 0.0155998 | 1 |
| CONTESTANT_A_meerkat-60 | 1.7390 | 1.4952 | 1.0150 | 0.5690 | 0.119719 | 1 |
| CONTESTANT_A_meerkat-90 | 1.1998 | -6.0216 | 0.9398 | 1.1516 | 0.928211 | 1 |
| CONTESTANT_B_meerkat-90 | 1.1514 | -14.6511 | 0.8535 | 1.4026 | 0.99998 | 1 |
| CONTESTANT_A_sloth-4 | 0.9787 | -2.8378 | 0.9716 | 1.5592 | 0.634174 | 1 |
| CONTESTANT_A_snail-4 | 0.9109 | -1.8380 | 0.9816 | 1.7621 | 0.497215 | 1 |
| CONTESTANT_E_meerkat-30 | 0.8914 | -4.6111 | 0.9539 | 0.8430 | 0.833832 | 1 |
| CONTESTANT_A_meerkat-70 | 0.8623 | -5.9072 | 0.9409 | 0.8316 | 0.922411 | 1 |
| CONTESTANT_C_meerkat-70 | 0.5464 | -10.0256 | 0.8997 | 1.4966 | 0.99783 | 1 |
| CONTESTANT_E_meerkat-70 | 0.4783 | -3.2728 | 0.9673 | 1.3446 | 0.690393 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | -2.1761 | 16.9799 | 1.1698 | 2.4625 | 0.00243998 | 1 |
| CONTESTANT_D_rabbit-1 | -1.4140 | 13.5424 | 1.1354 | 1.5372 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | 0.1584 | 13.0806 | 1.1308 | 1.0030 | 0.000209998 | 0.176398 |
| CONTESTANT_A_rabbit-1 | -2.1167 | 12.3211 | 1.1232 | 2.2286 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-5-1 | 1.7710 | 11.8308 | 1.1183 | 0.4688 | 0.0155998 | 1 |
| CONTESTANT_A_eagle-11-2 | -0.5259 | 11.7909 | 1.1179 | 1.3510 | 0.000579994 | 0.487195 |
| CONTESTANT_B_rabbit-1 | -1.7266 | 11.2069 | 1.1121 | 2.0493 | 1.99998e-05 | 0.0167998 |
| CONTESTANT_D_rabbit-2 | -1.4426 | 10.8483 | 1.1085 | 1.6203 | 1.99998e-05 | 0.0167998 |
| CONTESTANT_A_eagle-5-1 | -1.5073 | 10.4586 | 1.1046 | 2.3555 | 0.0246398 | 1 |
| CONTESTANT_B_eagle-44-6 | -1.7420 | 9.7047 | 1.0970 | 2.0836 | 9.9999e-06 | 0.00839992 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_E_eagle-11-2 | -2.2040 | 1.1352 | 1.0114 | 2.5377 | 0.214288 | 1 |
| CONTESTANT_A_meerkat-20 | -2.3250 | 4.3225 | 1.0432 | 2.3250 | 0.0150098 | 1 |
| CONTESTANT_B_meerkat-30 | -2.3512 | 2.3345 | 1.0233 | 2.6367 | 0.0705893 | 1 |
| CONTESTANT_C_meerkat-10 | -2.6534 | 1.3467 | 1.0135 | 2.7809 | 0.130339 | 1 |
| CONTESTANT_E_eagle-5-1 | -3.9470 | 4.5721 | 1.0457 | 4.5016 | 0.135669 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -0.6362 | -0.4088 | 9 | 1.7390 | -2.3250 | 1.7018 |
| CONTESTANT_B | -1.0874 | -1.1089 | 2 | 1.1514 | -2.3512 | 1.6820 |
| CONTESTANT_C | -1.2980 | -1.4546 | 3 | 0.5464 | -2.6534 | 1.6478 |
| CONTESTANT_D | -0.8855 | -0.9050 | 4 | 1.7710 | -1.8814 | 1.4808 |
| CONTESTANT_E | -0.9618 | -0.8639 | 2 | 0.8914 | -3.9470 | 1.7504 |
| CONTESTANT_F | -1.0346 | -0.8966 | 0 | -0.0313 | -2.1729 | 1.5653 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -1.3177 | -1.6167 | 0.1584 | -2.2040 |
| eagle-44-6 | -1.6045 | -1.7668 | -0.9799 | -2.0853 |
| eagle-5-1 | -1.5926 | -1.8481 | 1.7710 | -3.9470 |
| eagle-66-9 | -1.6512 | -1.7341 | -1.2132 | -2.0005 |
| eagle-88-12 | -1.4620 | -1.6854 | -0.7898 | -1.8739 |
| koala | -0.5180 | -0.5029 | 0.1679 | -1.5640 |
| meerkat-10 | -1.5458 | -1.6285 | -0.0371 | -2.6534 |
| meerkat-20 | -1.5149 | -1.4298 | -0.7381 | -2.3250 |
| meerkat-30 | -1.3261 | -1.6108 | 0.8914 | -2.3512 |
| meerkat-40 | -1.0416 | -0.9278 | -0.2944 | -1.9942 |
| meerkat-50 | -0.9867 | -0.8763 | -0.0313 | -1.9538 |
| meerkat-60 | -0.5031 | -0.7135 | 1.7390 | -1.8029 |
| meerkat-70 | -0.1073 | -0.1625 | 0.8623 | -0.8714 |
| meerkat-80 | -0.2203 | -0.2982 | 0.4728 | -0.8996 |
| meerkat-90 | -0.2896 | -0.3926 | 1.1998 | -1.9099 |
| rabbit-1 | -1.5178 | -1.5703 | -0.8563 | -2.1167 |
| rabbit-2 | -1.4510 | -1.6114 | -0.4814 | -2.1586 |
| robot | -1.5651 | -1.6325 | -0.6873 | -2.1879 |
| sloth-1 | -0.9869 | -1.0524 | -0.2469 | -1.6550 |
| sloth-2 | -0.8159 | -0.8795 | -0.1632 | -1.2174 |
| sloth-3 | -0.5428 | -0.7109 | 0.3932 | -0.9179 |
| sloth-4 | -0.3337 | -0.5359 | 0.9787 | -0.8936 |
| snail-1 | -1.0016 | -1.0807 | -0.2130 | -1.6862 |
| snail-2 | -0.8640 | -0.9111 | -0.1823 | -1.2900 |
| snail-3 | -0.5706 | -0.7806 | 0.4644 | -0.9655 |
| snail-4 | -0.4075 | -0.6080 | 0.9109 | -0.9456 |
| turtle | -0.5088 | -0.4386 | 0.1210 | -1.4545 |
| whale-shark | -1.3030 | -1.3933 | -0.8628 | -1.6598 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 5.7180 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
