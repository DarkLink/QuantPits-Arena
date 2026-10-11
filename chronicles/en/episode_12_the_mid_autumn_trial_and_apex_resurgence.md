# season_01 — repaired dispatch through 2026-09-24

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-09-18; cutoff: 2026-09-24. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-09-18 → 2026-09-24: 4 return sessions, 5 NAV observations including the reporting anchor; 1 scheduled rebalances.
- Period leader CONTESTANT_C_eagle-5-1: +1.5735%; end NAV 1.059701.
- Cumulative leader CONTESTANT_B_eagle-5-1: +18.4016%; end NAV 1.184016.
- 23/168 contestant paths gained during this segment; median path return -1.0665%.
- Market index segment return -1.5142%; end normalized NAV 0.916767.
- Taotie -0.4956% for the segment, end NAV 1.005960; Ghost scenario -1.2153%, NAV 0.964040.
- Cumulative leader raw p=0.000819992, Bonferroni p=0.688793; N=100,000 per matched random spec.
- At this cutoff: 62/168 raw p<0.05 and 17/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_C_eagle-5-1 | 1.5735 | 5.9701 | 1.0597 | 1.2737 | 0.0678793 | 1 |
| CONTESTANT_B_eagle-5-1 | 1.2154 | 18.4016 | 1.1840 | 0.2093 | 0.000819992 | 0.688793 |
| CONTESTANT_C_eagle-11-2 | 1.1185 | 5.7363 | 1.0574 | 0.5842 | 0.0158398 | 1 |
| CONTESTANT_C_robot | 0.7612 | 3.9668 | 1.0397 | 0.5877 | 0.00691993 | 1 |
| CONTESTANT_C_meerkat-70 | 0.6756 | -9.4177 | 0.9058 | 2.0769 | 0.98631 | 1 |
| CONTESTANT_C_meerkat-10 | 0.5260 | 1.8798 | 1.0188 | 0.3048 | 0.0416096 | 1 |
| CONTESTANT_B_eagle-11-2 | 0.4930 | 9.0585 | 1.0906 | 0.0305 | 0.00198998 | 1 |
| CONTESTANT_A_eagle-5-1 | 0.3599 | 10.8561 | 1.1086 | 2.3226 | 0.0145099 | 1 |
| CONTESTANT_B_eagle-44-6 | 0.2716 | 10.0026 | 1.1000 | 0.2634 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | 0.2412 | 9.5421 | 1.0954 | 0.3867 | 9.9999e-06 | 0.00839992 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_eagle-5-1 | 1.2154 | 18.4016 | 1.1840 | 0.2093 | 0.000819992 | 0.688793 |
| CONTESTANT_D_rabbit-1 | 0.2121 | 13.7832 | 1.1378 | 0.4871 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_eagle-11-2 | 0.0557 | 13.1436 | 1.1314 | 0.7295 | 0.000119999 | 0.100799 |
| CONTESTANT_A_rabbit-1 | -0.2192 | 12.0749 | 1.1207 | 0.5161 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-1 | 0.2268 | 11.4591 | 1.1146 | 0.3876 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_eagle-5-1 | 0.3599 | 10.8561 | 1.1086 | 2.3226 | 0.0145099 | 1 |
| CONTESTANT_A_eagle-11-2 | -0.8422 | 10.8494 | 1.1085 | 1.8843 | 0.000529995 | 0.445196 |
| CONTESTANT_D_rabbit-2 | -0.0124 | 10.8346 | 1.1083 | 0.5829 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-44-6 | 0.2716 | 10.0026 | 1.1000 | 0.2634 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | 0.2412 | 9.5421 | 1.0954 | 0.3867 | 9.9999e-06 | 0.00839992 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_D_turtle | -2.6932 | -4.9525 | 0.9505 | 2.9412 | 0.749713 | 1 |
| CONTESTANT_A_sloth-4 | -3.0698 | -5.8205 | 0.9418 | 4.0548 | 0.828202 | 1 |
| CONTESTANT_A_snail-4 | -3.0761 | -4.8575 | 0.9514 | 4.0698 | 0.729013 | 1 |
| CONTESTANT_D_eagle-5-1 | -3.1723 | 8.2831 | 1.0828 | 3.5720 | 0.0340697 | 1 |
| CONTESTANT_A_turtle | -3.5736 | -3.2458 | 0.9675 | 4.3543 | 0.536055 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -1.2734 | -1.3152 | 3 | 0.3599 | -3.5736 | 2.0991 |
| CONTESTANT_B | -0.8550 | -0.5403 | 7 | 1.2154 | -2.6203 | 1.5355 |
| CONTESTANT_C | -0.5336 | -0.5254 | 10 | 1.5735 | -2.1944 | 1.4929 |
| CONTESTANT_D | -0.9589 | -0.8743 | 2 | 0.2121 | -3.1723 | 1.5309 |
| CONTESTANT_E | -1.4140 | -1.4254 | 1 | 0.0057 | -2.2690 | 2.1241 |
| CONTESTANT_F | -1.1906 | -1.1946 | 0 | -0.4104 | -2.3110 | 1.9899 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -0.3046 | -0.3933 | 1.1185 | -1.3590 |
| eagle-44-6 | -0.4493 | -0.3005 | 0.2716 | -1.3463 |
| eagle-5-1 | -0.5229 | -0.5029 | 1.5735 | -3.1723 |
| eagle-66-9 | -0.4685 | -0.2672 | -0.1574 | -1.0921 |
| eagle-88-12 | -0.5144 | -0.4235 | -0.2415 | -0.9186 |
| koala | -1.8624 | -2.1825 | -0.9136 | -2.3202 |
| meerkat-10 | -0.0922 | -0.0749 | 0.5260 | -0.8913 |
| meerkat-20 | -0.6323 | -0.4981 | -0.1043 | -1.5298 |
| meerkat-30 | -0.4751 | -0.4413 | 0.0919 | -1.0638 |
| meerkat-40 | -1.0874 | -1.0535 | -0.3349 | -2.1532 |
| meerkat-50 | -1.4017 | -1.4575 | -0.5773 | -2.3110 |
| meerkat-60 | -1.4809 | -1.4325 | -1.1635 | -2.0292 |
| meerkat-70 | -0.8031 | -0.9465 | 0.6756 | -2.1345 |
| meerkat-80 | -1.0924 | -1.2789 | -0.3370 | -1.5051 |
| meerkat-90 | -1.5054 | -1.4400 | -0.7692 | -2.1792 |
| rabbit-1 | -0.3690 | -0.0905 | 0.2268 | -1.4225 |
| rabbit-2 | -0.3879 | -0.2206 | 0.2412 | -1.1768 |
| robot | -0.5341 | -0.6733 | 0.7612 | -1.6413 |
| sloth-1 | -1.0146 | -0.9141 | 0.0251 | -2.0080 |
| sloth-2 | -1.3884 | -1.2771 | -0.7280 | -2.0232 |
| sloth-3 | -1.6640 | -1.5506 | -1.0535 | -2.3279 |
| sloth-4 | -2.0695 | -2.0636 | -0.9541 | -3.0698 |
| snail-1 | -1.0181 | -0.9130 | 0.0117 | -1.9726 |
| snail-2 | -1.3555 | -1.2701 | -0.6669 | -1.9279 |
| snail-3 | -1.6489 | -1.5521 | -1.0572 | -2.2908 |
| snail-4 | -2.0161 | -1.9633 | -0.9197 | -3.0761 |
| turtle | -2.0815 | -2.1346 | -0.4104 | -3.5736 |
| whale-shark | -0.8125 | -0.7758 | -0.5554 | -1.0981 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 4.7458 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
