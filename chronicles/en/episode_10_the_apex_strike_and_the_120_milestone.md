# season_01 — repaired dispatch through 2026-09-11

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-09-04; cutoff: 2026-09-11. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-09-04 → 2026-09-11: 5 return sessions, 6 NAV observations including the reporting anchor; 1 scheduled rebalances.
- Period leader CONTESTANT_A_eagle-5-1: +4.3853%; end NAV 1.121490.
- Cumulative leader CONTESTANT_B_eagle-5-1: +19.5822%; end NAV 1.195822.
- 22/168 contestant paths gained during this segment; median path return -1.2284%.
- Market index segment return -0.8331%; end normalized NAV 0.931434.
- Taotie -0.9299% for the segment, end NAV 1.017040; Ghost scenario -1.8213%, NAV 0.983715.
- Cumulative leader raw p=0.00100999, Bonferroni p=0.848392; N=100,000 per matched random spec.
- At this cutoff: 63/168 raw p<0.05 and 18/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_eagle-5-1 | 4.3853 | 12.1490 | 1.1215 | 1.0669 | 0.0178598 | 1 |
| CONTESTANT_B_eagle-5-1 | 2.1441 | 19.5822 | 1.1958 | 0.9410 | 0.00100999 | 0.848392 |
| CONTESTANT_A_eagle-11-2 | 1.3069 | 12.3820 | 1.1238 | 0.7319 | 0.000849992 | 0.713993 |
| CONTESTANT_C_eagle-11-2 | 1.0846 | 6.5276 | 1.0653 | 0.5031 | 0.0306797 | 1 |
| CONTESTANT_D_eagle-5-1 | 0.5036 | 9.8847 | 1.0988 | 2.2000 | 0.0382696 | 1 |
| CONTESTANT_C_meerkat-10 | 0.4039 | 4.1092 | 1.0411 | 1.0533 | 0.0356696 | 1 |
| CONTESTANT_A_rabbit-1 | 0.3881 | 14.7500 | 1.1475 | 0.7010 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_meerkat-20 | 0.3731 | 6.8057 | 1.0681 | 0.7750 | 0.00330997 | 1 |
| CONTESTANT_D_eagle-11-2 | 0.3520 | 12.9018 | 1.1290 | 1.0265 | 0.000569994 | 0.478795 |
| CONTESTANT_A_robot | 0.3210 | 6.6244 | 1.0662 | 1.3006 | 0.00390996 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 2.1441 | 19.5822 | 1.1958 | 0.9410 | 0.00100999 | 0.848392 |
| CONTESTANT_D_rabbit-1 | 0.0374 | 15.1709 | 1.1517 | 0.7619 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_rabbit-1 | 0.3881 | 14.7500 | 1.1475 | 0.7010 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-1 | 0.0202 | 13.1607 | 1.1316 | 0.9305 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | 0.3520 | 12.9018 | 1.1290 | 1.0265 | 0.000569994 | 0.478795 |
| CONTESTANT_D_rabbit-2 | -0.4659 | 12.4709 | 1.1247 | 0.9357 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_eagle-11-2 | 1.3069 | 12.3820 | 1.1238 | 0.7319 | 0.000849992 | 0.713993 |
| CONTESTANT_A_eagle-5-1 | 4.3853 | 12.1490 | 1.1215 | 1.0669 | 0.0178598 | 1 |
| CONTESTANT_A_rabbit-2 | 0.0588 | 11.6518 | 1.1165 | 0.9935 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-44-6 | -0.4207 | 11.6495 | 1.1165 | 1.2006 | 9.9999e-06 | 0.00839992 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_koala | -3.9456 | -15.1819 | 0.8482 | 3.9456 | 1 | 1 |
| CONTESTANT_D_koala | -4.3181 | -17.4887 | 0.8251 | 4.4538 | 1 | 1 |
| CONTESTANT_C_koala | -4.3550 | -14.2229 | 0.8578 | 4.3550 | 0.99999 | 1 |
| CONTESTANT_C_meerkat-70 | -4.4286 | -10.5145 | 0.8949 | 4.4286 | 0.99933 | 1 |
| CONTESTANT_B_koala | -5.0069 | -15.9457 | 0.8405 | 5.0069 | 1 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -0.6851 | -0.8049 | 10 | 4.3853 | -3.9456 | 1.8942 |
| CONTESTANT_B | -1.0863 | -0.9512 | 5 | 2.1441 | -5.0069 | 1.8928 |
| CONTESTANT_C | -1.2620 | -0.8131 | 3 | 1.0846 | -4.4286 | 1.8913 |
| CONTESTANT_D | -1.3440 | -1.0696 | 4 | 0.5036 | -4.3181 | 1.8541 |
| CONTESTANT_E | -1.6874 | -1.8607 | 0 | -0.7301 | -2.8405 | 1.8538 |
| CONTESTANT_F | -1.6785 | -1.5994 | 0 | -0.6624 | -2.8783 | 2.0574 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | 0.1446 | 0.3142 | 1.3069 | -1.4896 |
| eagle-44-6 | -0.9132 | -0.5315 | -0.2264 | -1.9400 |
| eagle-5-1 | 0.7558 | -0.1077 | 4.3853 | -1.0035 |
| eagle-66-9 | -1.1887 | -0.9692 | -0.5833 | -1.9935 |
| eagle-88-12 | -1.3387 | -1.1278 | -0.8311 | -2.0257 |
| koala | -3.5139 | -4.1318 | -0.7416 | -5.0069 |
| meerkat-10 | -0.9609 | -0.7689 | 0.4039 | -2.4925 |
| meerkat-20 | -0.7652 | -0.5812 | 0.3731 | -2.0189 |
| meerkat-30 | -1.4450 | -1.2321 | -0.7640 | -2.7719 |
| meerkat-40 | -2.0764 | -2.1883 | -1.6314 | -2.4149 |
| meerkat-50 | -1.8680 | -1.8520 | -0.6851 | -2.9401 |
| meerkat-60 | -2.1852 | -2.2941 | -1.2421 | -2.8783 |
| meerkat-70 | -2.8886 | -2.5551 | -2.0875 | -4.4286 |
| meerkat-80 | -2.7494 | -2.7280 | -1.9938 | -3.3831 |
| meerkat-90 | -2.9737 | -3.2840 | -1.5799 | -3.7107 |
| rabbit-1 | -0.4762 | -0.3055 | 0.3881 | -1.9416 |
| rabbit-2 | -0.8228 | -0.6065 | 0.0588 | -2.0542 |
| robot | -0.4113 | -0.3158 | 0.3210 | -1.4176 |
| sloth-1 | -0.6487 | -0.7415 | 0.1020 | -1.2727 |
| sloth-2 | -0.8649 | -1.0928 | 0.3190 | -1.2442 |
| sloth-3 | -1.1762 | -1.3402 | -0.2045 | -1.8341 |
| sloth-4 | -1.1288 | -1.2831 | 0.3112 | -1.8980 |
| snail-1 | -0.6468 | -0.7117 | 0.0421 | -1.2673 |
| snail-2 | -0.8807 | -1.0427 | 0.2135 | -1.2665 |
| snail-3 | -1.1688 | -1.3309 | -0.2211 | -1.7283 |
| snail-4 | -1.2130 | -1.2766 | -0.1421 | -1.8975 |
| turtle | -1.2961 | -1.4456 | -0.0887 | -2.0120 |
| whale-shark | -1.4352 | -1.3365 | -1.1782 | -1.9338 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 5.3888 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
