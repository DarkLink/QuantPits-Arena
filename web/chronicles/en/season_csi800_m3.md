# season_csi800 — repaired dispatch through 2026-09-30

This dispatch is a retrospective repair replay using the actual raw weekly signals preserved in legacy checkpoints and a frozen current daily-bar snapshot. Reporting anchor: 2026-08-28; cutoff: 2026-09-30. Period returns are NAV ratios; differences in returns are percentage points. Legacy artifacts are archived separately. This refreshed document is not evidence of a historical pre-market commitment.

## ⚡ TL;DR

- 2026-08-28 → 2026-09-30: 22 return sessions, 23 NAV observations including the reporting anchor; 5 scheduled rebalances.
- Period leader CONTESTANT_E_eagle-5-1: +1.8603%; end NAV 1.012307.
- Cumulative leader CONTESTANT_B_rabbit-2: +11.1967%; end NAV 1.111967.
- 4/168 contestant paths gained during this segment; median path return -4.0480%.
- Market index segment return -5.5598%; end normalized NAV 0.885768.
- Taotie -0.4042% for the segment, end NAV 1.000486; Ghost scenario -4.2849%, NAV 0.923820.
- Cumulative leader raw p=9.9999e-06, Bonferroni p=0.00839992; N=100,000 per matched random spec.
- At this cutoff: 45/168 raw p<0.05 and 12/168 Bonferroni p<0.05 in this pool, within the visible 840-item family.

## Period and cumulative standings

Top ten for the reporting segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_E_eagle-5-1 | 1.8603 | 1.2307 | 1.0123 | 5.5440 | 0.128359 | 1 |
| CONTESTANT_B_eagle-11-2 | 0.2010 | 5.2268 | 1.0523 | 2.8365 | 0.00940991 | 1 |
| CONTESTANT_B_robot | 0.1346 | 4.6796 | 1.0468 | 1.8025 | 0.00122999 | 1 |
| CONTESTANT_E_turtle | 0.0039 | -5.4690 | 0.9453 | 4.7222 | 0.455855 | 1 |
| CONTESTANT_A_meerkat-40 | -0.0899 | 5.2074 | 1.0521 | 3.0298 | 0.000679993 | 0.571194 |
| CONTESTANT_B_rabbit-1 | -0.1774 | 7.9526 | 1.0795 | 3.7855 | 0.000149999 | 0.125999 |
| CONTESTANT_B_eagle-66-9 | -0.3528 | 5.8284 | 1.0583 | 2.9767 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_rabbit-2 | -0.3594 | 11.1967 | 1.1120 | 3.8971 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-88-12 | -0.4521 | 5.3345 | 1.0533 | 2.9623 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_F_koala | -0.4984 | -0.8153 | 0.9918 | 3.6438 | 0.0658093 | 1 |

Top ten cumulatively through this cutoff:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_B_rabbit-2 | -0.3594 | 11.1967 | 1.1120 | 3.8971 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_D_rabbit-1 | -2.0689 | 10.0495 | 1.1005 | 4.8252 | 1.99998e-05 | 0.0167998 |
| CONTESTANT_B_rabbit-1 | -0.1774 | 7.9526 | 1.0795 | 3.7855 | 0.000149999 | 0.125999 |
| CONTESTANT_D_meerkat-10 | -1.4367 | 7.8199 | 1.0782 | 4.0082 | 4.99995e-05 | 0.0419996 |
| CONTESTANT_B_sloth-1 | -1.2848 | 6.6205 | 1.0662 | 3.1346 | 0.000209998 | 0.176398 |
| CONTESTANT_A_rabbit-1 | -2.1210 | 6.3234 | 1.0632 | 3.9502 | 0.000649994 | 0.545995 |
| CONTESTANT_B_whale-shark | -0.9435 | 6.2200 | 1.0622 | 3.4185 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_B_eagle-66-9 | -0.3528 | 5.8284 | 1.0583 | 2.9767 | 9.9999e-06 | 0.00839992 |
| CONTESTANT_A_sloth-2 | -6.9078 | 5.8053 | 1.0581 | 7.7355 | 0.000369996 | 0.310797 |
| CONTESTANT_B_eagle-44-6 | -0.5993 | 5.6479 | 1.0565 | 2.9851 | 9.9999e-06 | 0.00839992 |

Bottom five for the segment:

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_F_eagle-5-1 | -8.3932 | -20.5260 | 0.7947 | 10.0823 | 0.95362 | 1 |
| CONTESTANT_D_sloth-3 | -8.5668 | -3.6189 | 0.9638 | 8.9643 | 0.240818 | 1 |
| CONTESTANT_D_snail-3 | -8.7425 | -9.3154 | 0.9068 | 9.1577 | 0.831602 | 1 |
| CONTESTANT_D_sloth-4 | -9.1983 | -8.7332 | 0.9127 | 9.9212 | 0.785102 | 1 |
| CONTESTANT_D_snail-4 | -9.3978 | -11.1214 | 0.8888 | 10.5207 | 0.930681 | 1 |

## Six anonymous contestants

Each row includes all 28 animals; no selection of winning combinations.

| contestant | mean_pct | median_pct | positive | best_pct | worst_pct | mean_mdd_pct |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | -4.5203 | -5.1774 | 0 | -0.0899 | -7.8898 | 6.1634 |
| CONTESTANT_B | -2.5048 | -2.4784 | 2 | 0.2010 | -6.8191 | 4.5184 |
| CONTESTANT_C | -3.5422 | -3.5658 | 0 | -0.5634 | -6.2844 | 5.7054 |
| CONTESTANT_D | -4.7460 | -4.7095 | 0 | -0.5671 | -9.3978 | 6.3498 |
| CONTESTANT_E | -3.7148 | -4.1651 | 2 | 1.8603 | -6.6936 | 6.4522 |
| CONTESTANT_F | -4.4419 | -4.4729 | 0 | -0.4984 | -8.3932 | 6.2577 |

## All animal policies

Each row summarizes segment returns across the six contestants; the range describes contestant-policy interaction.

| animal | mean_pct | median_pct | best_pct | worst_pct |
| --- | --- | --- | --- | --- |
| eagle-11-2 | -3.4660 | -3.8237 | 0.2010 | -6.8294 |
| eagle-44-6 | -3.2636 | -3.5687 | -0.5993 | -5.5322 |
| eagle-5-1 | -3.8216 | -3.7920 | 1.8603 | -8.3932 |
| eagle-66-9 | -2.9704 | -2.9432 | -0.3528 | -5.6158 |
| eagle-88-12 | -2.8210 | -2.4518 | -0.4521 | -6.0618 |
| koala | -3.5725 | -3.7918 | -0.4984 | -5.8987 |
| meerkat-10 | -2.3607 | -1.4104 | -0.7445 | -5.3041 |
| meerkat-20 | -2.7376 | -2.4477 | -0.5671 | -6.1768 |
| meerkat-30 | -4.2477 | -4.9157 | -1.5684 | -6.0547 |
| meerkat-40 | -3.4969 | -3.8704 | -0.0899 | -5.8398 |
| meerkat-50 | -4.0505 | -3.9148 | -2.6884 | -6.1278 |
| meerkat-60 | -3.8324 | -3.9011 | -0.5634 | -6.1623 |
| meerkat-70 | -4.7339 | -5.0841 | -2.6315 | -5.9537 |
| meerkat-80 | -6.2003 | -6.4447 | -4.7848 | -7.4417 |
| meerkat-90 | -4.8553 | -5.2320 | -2.8796 | -6.2844 |
| rabbit-1 | -3.6902 | -3.3028 | -0.1774 | -7.0461 |
| rabbit-2 | -3.5387 | -3.2567 | -0.3594 | -6.8037 |
| robot | -3.3100 | -3.7753 | 0.1346 | -4.7879 |
| sloth-1 | -3.5870 | -3.5585 | -1.2848 | -5.7629 |
| sloth-2 | -4.5832 | -4.1738 | -1.9868 | -7.1316 |
| sloth-3 | -4.8673 | -4.1223 | -1.9223 | -8.5668 |
| sloth-4 | -5.2103 | -5.0670 | -2.6742 | -9.1983 |
| snail-1 | -3.7214 | -3.9936 | -1.3516 | -5.8312 |
| snail-2 | -4.5364 | -4.0466 | -2.0617 | -7.3092 |
| snail-3 | -4.7104 | -3.9971 | -1.7152 | -8.7425 |
| snail-4 | -5.1841 | -5.1347 | -2.1719 | -9.3978 |
| turtle | -3.6164 | -3.9135 | 0.0039 | -7.0520 |
| whale-shark | -2.5409 | -1.7483 | -0.9435 | -5.1135 |

## Mechanisms and interpretation

The TopK=5/DropN=1 segment spread across contestants is 10.2536 percentage points. A winning concentrated path does not establish a universal concentration advantage. Rabbit DropN changes weekly replacement capacity, not trading frequency. Sloth delay and cold-start cash, and Snail warm-start stale signals, jointly alter exposure and path dependence; these are whole-strategy comparisons, not an identified prediction half-life. Percentile Meerkats and inverted Koala should be read against the full contestant distribution above.

Contestant averages describe consistency across animals; the best row describes realized performance in this window. Pool membership, fees, lots, cash exposure and signal cross-sections all contribute to differences across environments. The results do not identify a single macro cause or disclose contestant architecture.

## Random-control and execution contract

Matching uses TopK/DropN only: ten random specifications and one deterministic passive reference. Delay, warm/cold starts, inversion and percentile selection do not introduce extra species. The p values above test cumulative returns from inception, not segment returns. The upper tail includes ties: p=(k+1)/(N+1). At N=100,000, minimum p is 9.9999e-06, never zero. Bonferroni/Holm/BH/BY are stored separately. The 840-item raw threshold is 5.952381e-05, with strict inequality; at the formal count, up to four exceedances can pass Bonferroni. Earlier cutoffs and repeated weekly reviews are descriptive monitoring. Correction does not cover all historical windows jointly or hidden prior research selection. Monte Carlo intervals measure simulation tail uncertainty and add no market history.

Execution requires finite positive same-day quotes; missing-price sells retain the position. Valuation may carry the last valid close with stale-mark counts. Pool membership is separate from affordability. Decision-close intent is frozen before Monday execution. Taotie uses a 1.0 standard-account capital ratio and the same allocation policy. Ghost is a capital-granularity scenario, not a costless equal-weight index. Turnover is gross buys plus gross sells divided by starting assets.

This remains daily-bar research: full-day volume is a retrospective tradability proxy. Complete verified corporate-action, opening direction-limit and capacity data are unavailable. Factor changes are not guessed into dividend payments, and adjusted prices are not mixed with unchanged nominal shares to claim a total-return repair. Strict execution fails its preflight without required coverage.

## Separate October appendix

September 30 close to October 9 contains two return sessions. The holiday Monday produces no makeup rebalance. October is reported separately from September.

| path | period_pct | cumulative_pct | nav | period_mdd_pct | raw_p | bonferroni_p |
| --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_E_meerkat-50 | 1.8368 | 4.6075 | 1.0461 | -0.0000 | 0.0012 | 1.0000 |
| CONTESTANT_E_meerkat-90 | 1.5703 | -1.9301 | 0.9807 | -0.0000 | 0.1085 | 1.0000 |
| CONTESTANT_A_rabbit-2 | 1.5327 | 7.1014 | 1.0710 | -0.0000 | 0.0002 | 0.1428 |
| CONTESTANT_D_turtle | 1.4790 | -6.0387 | 0.9396 | -0.0000 | 0.5066 | 1.0000 |
| CONTESTANT_B_eagle-5-1 | 1.4755 | 6.9812 | 1.0698 | 0.2990 | 0.0319 | 1.0000 |
| CONTESTANT_D_rabbit-2 | 1.3101 | 6.8380 | 1.0684 | -0.0000 | 0.0002 | 0.1932 |
| CONTESTANT_A_meerkat-10 | 1.2468 | 1.5394 | 1.0154 | -0.0000 | 0.0143 | 1.0000 |
| CONTESTANT_B_eagle-66-9 | 1.2390 | 7.1396 | 1.0714 | -0.0000 | 0.0000 | 0.0084 |
| CONTESTANT_B_eagle-11-2 | 1.1942 | 6.4834 | 1.0648 | 0.0638 | 0.0046 | 1.0000 |
| CONTESTANT_B_robot | 1.1913 | 5.9266 | 1.0593 | -0.0000 | 0.0003 | 0.2856 |
