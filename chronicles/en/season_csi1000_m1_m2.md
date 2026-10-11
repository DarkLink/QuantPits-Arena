# season_csi1000 — repaired baseline through 2026-08-28

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-07-03; cutoff: 2026-08-28. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-07-03 → 2026-08-28: 40 return sessions, 41 NAV observations including the reporting anchor; 8 scheduled rebalances.
- Period leader CONTESTANT_A_sloth-2: +17.9625%; end NAV 1.179625.
- Cumulative leader CONTESTANT_A_sloth-2: +17.9625%; end NAV 1.179625.
- 78/168 contestant paths gained during this segment; median path return -0.5242%.
- Market index segment return -10.6227%; end normalized NAV 0.893773.
- Taotie +0.6950% for the segment, end NAV 1.006950; Ghost scenario -4.8340%, NAV 0.951660.
- Cumulative leader raw p=1.99998e-05, Bonferroni p=0.0167998; N=100,000 per matched random spec.
- At this cutoff: 55/168 raw p<0.05 and 4/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | 17.9625 | 17.9625 | 1.1796 | 7.0036 | 1.99998e-05 | 0.0167998 |
| CONTESTANT_C_sloth-4 | 16.4991 | 16.4991 | 1.1650 | 8.0509 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_C_sloth-2 | 16.0115 | 16.0115 | 1.1601 | 8.1044 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_B_sloth-2 | 15.1033 | 15.1033 | 1.1510 | 6.8509 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_A_sloth-3 | 14.8772 | 14.8772 | 1.1488 | 7.2686 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_B_sloth-3 | 12.7254 | 12.7254 | 1.1273 | 6.7156 | 0.000349997 | 0.293997 |
| CONTESTANT_C_sloth-3 | 12.2593 | 12.2593 | 1.1226 | 8.3309 | 0.000459995 | 0.386396 |
| CONTESTANT_B_sloth-1 | 10.7661 | 10.7661 | 1.1077 | 6.8580 | 0.00115999 | 0.97439 |
| CONTESTANT_D_sloth-3 | 10.7385 | 10.7385 | 1.1074 | 6.5682 | 0.00119999 | 1 |
| CONTESTANT_D_sloth-2 | 10.7317 | 10.7317 | 1.1073 | 7.0118 | 0.00119999 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A_sloth-2 | 17.9625 | 17.9625 | 1.1796 | 7.0036 | 1.99998e-05 | 0.0167998 |
| CONTESTANT_C_sloth-4 | 16.4991 | 16.4991 | 1.1650 | 8.0509 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_C_sloth-2 | 16.0115 | 16.0115 | 1.1601 | 8.1044 | 2.99997e-05 | 0.0251997 |
| CONTESTANT_B_sloth-2 | 15.1033 | 15.1033 | 1.1510 | 6.8509 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_A_sloth-3 | 14.8772 | 14.8772 | 1.1488 | 7.2686 | 9.9999e-05 | 0.0839992 |
| CONTESTANT_B_sloth-3 | 12.7254 | 12.7254 | 1.1273 | 6.7156 | 0.000349997 | 0.293997 |
| CONTESTANT_C_sloth-3 | 12.2593 | 12.2593 | 1.1226 | 8.3309 | 0.000459995 | 0.386396 |
| CONTESTANT_B_sloth-1 | 10.7661 | 10.7661 | 1.1077 | 6.8580 | 0.00115999 | 0.97439 |
| CONTESTANT_D_sloth-3 | 10.7385 | 10.7385 | 1.1074 | 6.5682 | 0.00119999 | 1 |
| CONTESTANT_D_sloth-2 | 10.7317 | 10.7317 | 1.1073 | 7.0118 | 0.00119999 | 1 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_meerkat-90 | -16.8935 | -16.8935 | 0.8311 | 21.2935 | 0.99991 | 1 |
| CONTESTANT_D_koala | -17.7546 | -17.7546 | 0.8225 | 21.5538 | 0.99995 | 1 |
| CONTESTANT_C_koala | -22.9127 | -22.9127 | 0.7709 | 29.9382 | 1 | 1 |
| CONTESTANT_A_koala | -23.5637 | -23.5637 | 0.7644 | 32.8664 | 1 | 1 |
| CONTESTANT_B_koala | -29.2879 | -29.2879 | 0.7071 | 38.5544 | 1 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | 1.4572 | 2.7937 | 18 | 17.9625 | -23.5637 | 12.6199 |
| CONTESTANT_B | 1.5385 | 4.0557 | 19 | 15.1033 | -29.2879 | 11.5451 |
| CONTESTANT_C | -0.9748 | -0.8983 | 12 | 16.4991 | -22.9127 | 14.0536 |
| CONTESTANT_D | -1.6750 | -2.7499 | 12 | 10.7385 | -17.7546 | 14.3316 |
| CONTESTANT_E | -1.2804 | -1.8397 | 10 | 8.6669 | -10.0425 | 9.8159 |
| CONTESTANT_F | -2.9185 | -4.7499 | 7 | 10.1836 | -12.6485 | 11.2994 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -0.3207 | -0.5068 | 6.2251 | -6.4122 |
| eagle-44-6 | 0.8301 | 3.1190 | 5.3457 | -6.1425 |
| eagle-5-1 | 0.0404 | -0.5256 | 7.4233 | -4.6305 |
| eagle-66-9 | 1.6290 | 3.9141 | 5.7351 | -5.4241 |
| eagle-88-12 | 1.9756 | 4.0639 | 6.6783 | -4.4234 |
| koala | -13.7531 | -20.3337 | 10.1836 | -29.2879 |
| meerkat-10 | -0.5685 | 2.4782 | 4.2021 | -10.0425 |
| meerkat-20 | -0.7966 | -0.5730 | 4.1316 | -4.2637 |
| meerkat-30 | 0.4745 | -0.6062 | 9.9663 | -7.6659 |
| meerkat-40 | -2.0925 | -0.3830 | 4.9910 | -12.6485 |
| meerkat-50 | -3.2788 | -2.5962 | -1.4177 | -6.8276 |
| meerkat-60 | -3.5388 | -2.8973 | 4.3432 | -11.1290 |
| meerkat-70 | -4.8810 | -6.0157 | -0.1750 | -7.0606 |
| meerkat-80 | -6.0267 | -8.2130 | 2.3796 | -11.8493 |
| meerkat-90 | -8.2431 | -8.5637 | 0.5472 | -16.8935 |
| rabbit-1 | -0.0256 | 0.9694 | 3.7114 | -7.8787 |
| rabbit-2 | -3.4709 | -3.1970 | -0.2184 | -7.5025 |
| robot | -0.4679 | -0.6399 | 5.3989 | -5.9309 |
| sloth-1 | 3.7650 | 3.9149 | 10.7661 | -2.5590 |
| sloth-2 | 11.5585 | 12.9175 | 17.9625 | 4.7152 |
| sloth-3 | 11.0782 | 11.4989 | 14.8772 | 7.2021 |
| sloth-4 | 8.7134 | 7.3338 | 16.4991 | 4.1894 |
| snail-1 | -0.8766 | -0.5611 | 6.5775 | -8.0544 |
| snail-2 | -1.7994 | -2.6846 | 4.7028 | -7.4817 |
| snail-3 | -4.2454 | -5.5563 | 2.5891 | -8.9213 |
| snail-4 | -3.9184 | -4.5145 | 1.3837 | -9.6066 |
| turtle | -3.1627 | -3.8903 | 3.5376 | -9.1215 |
| whale-shark | 3.4217 | 4.1237 | 7.3585 | -1.2177 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 12.0539 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. The same monkeys retain cash and positions across weeks; actual daily NAV and pointwise quantiles are saved, while weekly settlements define reporting segments. Earlier cutoffs and repeated daily or weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.
