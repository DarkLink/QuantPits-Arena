# QuantPits Graveyard Arena — Parametric Monkey Colony Diagnostics

Run ID: `tournament_real_1000_monkeys`

## 1. Methodology & Scientific Rationale

The **Parametric Monkey Colony** serves as the rigorous empirical null model for evaluating whether contestants' alpha returns are statistically distinguishable from pure random stock picking.

- **Zero Future Information**: Every monkey draws uniform random scores across the cross-section using deterministic seeds: `seed = (2026 + m * 10007 + t * 37) % (2**31 - 1)`.
- **Strict Parity**: Each monkey group operates under the **exact same 100-share minimum trading lot and CNY 500,000 capital constraints** as the real models.
- **Complete Parameter Coverage**: All 11 distinct portfolio execution policies (TopK / DropN pairs, including Taotie passive full-universe) are individually benchmarked by 100 random monkeys (1,100 monkeys total).
- **Empirical P-Value**: Formally defined as $p = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{monkey}_i \ge \text{actual_return})$. $p < 0.05$ indicates significant alpha superiority over random chance at 95% confidence.

## 2. Null Distributions by Strategy Parameter Group (11 Groups × 100 Monkeys)

| strategy_spec | topk | n_drop | description | colony_size | monkey_min | monkey_p05 | monkey_median | monkey_mean | monkey_p95 | monkey_max | monkey_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_22_3 | 22 | 3 | Robot, Sloth-1~4, Snail-1~4, Meerkat-10~90, Koala | 1000 | -6.02% | -3.40% | 1.07% | 1.09% | 5.45% | 9.62% | 2.73% |
| P_22_11 | 22 | 11 | Rabbit-1 (半仓换手) | 1000 | -8.09% | -4.04% | 0.70% | 0.71% | 5.75% | 11.46% | 2.97% |
| P_22_22 | 22 | 22 | Rabbit-2 (全仓换手) | 1000 | -9.54% | -4.74% | 0.03% | 0.02% | 4.89% | 9.16% | 2.96% |
| P_22_1 | 22 | 1 | Turtle (极低换手) | 1000 | -7.80% | -3.44% | 1.21% | 1.13% | 5.68% | 10.65% | 2.79% |
| P_5_1 | 5 | 1 | Eagle-5/1 (极端集中组合) | 1000 | -19.93% | -10.22% | 0.35% | 0.45% | 11.05% | 25.46% | 6.45% |
| P_11_2 | 11 | 2 | Eagle-11/2 (紧凑半数组合) | 1000 | -11.86% | -6.09% | 0.84% | 0.76% | 7.45% | 15.00% | 4.13% |
| P_44_6 | 44 | 6 | Eagle-44/6 (2 倍容量宽度) | 1000 | -4.38% | -1.23% | 1.59% | 1.59% | 4.53% | 6.64% | 1.75% |
| P_66_9 | 66 | 9 | Eagle-66/9 (3 倍容量宽度) | 1000 | -2.62% | -0.24% | 1.94% | 1.97% | 4.30% | 6.79% | 1.37% |
| P_88_12 | 88 | 12 | Eagle-88/12 (4 倍容量宽度) | 1000 | -0.47% | 0.86% | 2.60% | 2.54% | 4.15% | 5.82% | 1.01% |
| P_123_17 | 123 | 17 | WhaleShark (半池大容量组合) | 1000 | 1.28% | 2.58% | 3.70% | 3.70% | 4.76% | 5.71% | 0.67% |
| P_ALL_0 | 全池 | 被动 | Taotie (全池吞噬被动组合) | 1000 | 2.32% | 2.32% | 2.32% | 2.32% | 2.32% | 2.32% | 0.00% |

## 3. Contestant Significance vs. Corresponding Monkey Colony

| contestant_id | animal_id | strategy_spec | actual_return_pct | monkey_median_pct | excess_over_monkey_pct | percentile_rank | empirical_p_value | significant_95pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | robot | P_22_3 | 8.65% | 1.07% | +7.58% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_A | sloth-1 | P_22_3 | 6.61% | 1.07% | +5.54% | 98.1% | 0.0190 | YES (p < 0.05) |
| CONTESTANT_A | sloth-2 | P_22_3 | 9.25% | 1.07% | +8.18% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_A | sloth-3 | P_22_3 | 6.10% | 1.07% | +5.03% | 97.1% | 0.0290 | YES (p < 0.05) |
| CONTESTANT_A | sloth-4 | P_22_3 | 1.38% | 1.07% | +0.31% | 54.3% | 0.4570 | NO |
| CONTESTANT_A | snail-1 | P_22_3 | 5.59% | 1.07% | +4.52% | 95.5% | 0.0450 | YES (p < 0.05) |
| CONTESTANT_A | snail-2 | P_22_3 | 3.50% | 1.07% | +2.43% | 80.9% | 0.1910 | NO |
| CONTESTANT_A | snail-3 | P_22_3 | 3.85% | 1.07% | +2.78% | 84.6% | 0.1540 | NO |
| CONTESTANT_A | snail-4 | P_22_3 | 2.52% | 1.07% | +1.45% | 68.2% | 0.3180 | NO |
| CONTESTANT_A | rabbit-1 | P_22_11 | 13.13% | 0.70% | +12.44% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_A | rabbit-2 | P_22_22 | 10.40% | 0.03% | +10.38% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_A | turtle | P_22_1 | 5.72% | 1.21% | +4.51% | 95.3% | 0.0470 | YES (p < 0.05) |
| CONTESTANT_A | koala | P_22_3 | -10.48% | 1.07% | -11.55% | 0.0% | 1.0000 | NO |
| CONTESTANT_A | meerkat-10 | P_22_3 | 2.58% | 1.07% | +1.51% | 69.2% | 0.3080 | NO |
| CONTESTANT_A | meerkat-20 | P_22_3 | 4.65% | 1.07% | +3.58% | 90.0% | 0.1000 | NO |
| CONTESTANT_A | meerkat-30 | P_22_3 | 4.36% | 1.07% | +3.29% | 88.7% | 0.1130 | NO |
| CONTESTANT_A | meerkat-40 | P_22_3 | 3.46% | 1.07% | +2.39% | 80.7% | 0.1930 | NO |
| CONTESTANT_A | meerkat-50 | P_22_3 | 4.69% | 1.07% | +3.62% | 90.3% | 0.0970 | NO |
| CONTESTANT_A | meerkat-60 | P_22_3 | 0.50% | 1.07% | -0.57% | 41.0% | 0.5900 | NO |
| CONTESTANT_A | meerkat-70 | P_22_3 | -4.01% | 1.07% | -5.08% | 3.5% | 0.9650 | NO |
| CONTESTANT_A | meerkat-80 | P_22_3 | -1.23% | 1.07% | -2.30% | 20.0% | 0.8000 | NO |
| CONTESTANT_A | meerkat-90 | P_22_3 | -2.01% | 1.07% | -3.08% | 13.2% | 0.8680 | NO |
| CONTESTANT_A | eagle-5-1 | P_5_1 | 12.67% | 0.35% | +12.33% | 97.3% | 0.0270 | YES (p < 0.05) |
| CONTESTANT_A | eagle-11-2 | P_11_2 | 14.68% | 0.84% | +13.84% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_A | eagle-44-6 | P_44_6 | 9.59% | 1.59% | +8.00% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_A | eagle-66-9 | P_66_9 | 6.41% | 1.94% | +4.47% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_A | eagle-88-12 | P_88_12 | 6.80% | 2.60% | +4.20% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_A | whale-shark | P_123_17 | 4.61% | 3.70% | +0.91% | 91.5% | 0.0850 | NO |
| CONTESTANT_B | robot | P_22_3 | 12.20% | 1.07% | +11.13% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | sloth-1 | P_22_3 | 14.38% | 1.07% | +13.31% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | sloth-2 | P_22_3 | 8.69% | 1.07% | +7.62% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_B | sloth-3 | P_22_3 | 4.69% | 1.07% | +3.62% | 90.3% | 0.0970 | NO |
| CONTESTANT_B | sloth-4 | P_22_3 | 0.11% | 1.07% | -0.96% | 35.5% | 0.6450 | NO |
| CONTESTANT_B | snail-1 | P_22_3 | 11.19% | 1.07% | +10.12% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | snail-2 | P_22_3 | 6.29% | 1.07% | +5.22% | 97.3% | 0.0270 | YES (p < 0.05) |
| CONTESTANT_B | snail-3 | P_22_3 | 7.50% | 1.07% | +6.43% | 99.2% | 0.0080 | YES (p < 0.05) |
| CONTESTANT_B | snail-4 | P_22_3 | 6.28% | 1.07% | +5.21% | 97.3% | 0.0270 | YES (p < 0.05) |
| CONTESTANT_B | rabbit-1 | P_22_11 | 10.76% | 0.70% | +10.07% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | rabbit-2 | P_22_22 | 8.95% | 0.03% | +8.93% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_B | turtle | P_22_1 | 10.60% | 1.21% | +9.39% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | koala | P_22_3 | -10.60% | 1.07% | -11.67% | 0.0% | 1.0000 | NO |
| CONTESTANT_B | meerkat-10 | P_22_3 | 6.34% | 1.07% | +5.27% | 97.4% | 0.0260 | YES (p < 0.05) |
| CONTESTANT_B | meerkat-20 | P_22_3 | 7.41% | 1.07% | +6.34% | 99.2% | 0.0080 | YES (p < 0.05) |
| CONTESTANT_B | meerkat-30 | P_22_3 | 5.17% | 1.07% | +4.10% | 93.5% | 0.0650 | NO |
| CONTESTANT_B | meerkat-40 | P_22_3 | 6.76% | 1.07% | +5.69% | 98.3% | 0.0170 | YES (p < 0.05) |
| CONTESTANT_B | meerkat-50 | P_22_3 | 2.39% | 1.07% | +1.32% | 66.5% | 0.3350 | NO |
| CONTESTANT_B | meerkat-60 | P_22_3 | -1.08% | 1.07% | -2.15% | 21.2% | 0.7880 | NO |
| CONTESTANT_B | meerkat-70 | P_22_3 | 0.44% | 1.07% | -0.63% | 40.3% | 0.5970 | NO |
| CONTESTANT_B | meerkat-80 | P_22_3 | -2.96% | 1.07% | -4.03% | 7.1% | 0.9290 | NO |
| CONTESTANT_B | meerkat-90 | P_22_3 | -10.32% | 1.07% | -11.39% | 0.0% | 1.0000 | NO |
| CONTESTANT_B | eagle-5-1 | P_5_1 | 19.71% | 0.35% | +19.36% | 99.7% | 0.0030 | YES (p < 0.05) |
| CONTESTANT_B | eagle-11-2 | P_11_2 | 11.38% | 0.84% | +10.54% | 99.3% | 0.0070 | YES (p < 0.05) |
| CONTESTANT_B | eagle-44-6 | P_44_6 | 10.74% | 1.59% | +9.15% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | eagle-66-9 | P_66_9 | 6.85% | 1.94% | +4.91% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | eagle-88-12 | P_88_12 | 7.19% | 2.60% | +4.59% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_B | whale-shark | P_123_17 | 4.83% | 3.70% | +1.14% | 95.4% | 0.0460 | YES (p < 0.05) |
| CONTESTANT_C | robot | P_22_3 | 6.93% | 1.07% | +5.86% | 98.5% | 0.0150 | YES (p < 0.05) |
| CONTESTANT_C | sloth-1 | P_22_3 | 7.76% | 1.07% | +6.69% | 99.5% | 0.0050 | YES (p < 0.05) |
| CONTESTANT_C | sloth-2 | P_22_3 | 8.09% | 1.07% | +7.02% | 99.7% | 0.0030 | YES (p < 0.05) |
| CONTESTANT_C | sloth-3 | P_22_3 | 5.65% | 1.07% | +4.58% | 95.6% | 0.0440 | YES (p < 0.05) |
| CONTESTANT_C | sloth-4 | P_22_3 | 4.22% | 1.07% | +3.15% | 87.8% | 0.1220 | NO |
| CONTESTANT_C | snail-1 | P_22_3 | 6.38% | 1.07% | +5.31% | 97.5% | 0.0250 | YES (p < 0.05) |
| CONTESTANT_C | snail-2 | P_22_3 | 6.07% | 1.07% | +5.00% | 96.8% | 0.0320 | YES (p < 0.05) |
| CONTESTANT_C | snail-3 | P_22_3 | 5.61% | 1.07% | +4.54% | 95.6% | 0.0440 | YES (p < 0.05) |
| CONTESTANT_C | snail-4 | P_22_3 | 5.60% | 1.07% | +4.53% | 95.6% | 0.0440 | YES (p < 0.05) |
| CONTESTANT_C | rabbit-1 | P_22_11 | 5.23% | 0.70% | +4.54% | 93.1% | 0.0690 | NO |
| CONTESTANT_C | rabbit-2 | P_22_22 | 6.74% | 0.03% | +6.71% | 98.6% | 0.0140 | YES (p < 0.05) |
| CONTESTANT_C | turtle | P_22_1 | 6.36% | 1.21% | +5.15% | 97.2% | 0.0280 | YES (p < 0.05) |
| CONTESTANT_C | koala | P_22_3 | -8.84% | 1.07% | -9.91% | 0.0% | 1.0000 | NO |
| CONTESTANT_C | meerkat-10 | P_22_3 | 3.52% | 1.07% | +2.45% | 81.1% | 0.1890 | NO |
| CONTESTANT_C | meerkat-20 | P_22_3 | 1.03% | 1.07% | -0.04% | 49.1% | 0.5090 | NO |
| CONTESTANT_C | meerkat-30 | P_22_3 | 9.06% | 1.07% | +7.99% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-40 | P_22_3 | 8.17% | 1.07% | +7.10% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-50 | P_22_3 | 7.62% | 1.07% | +6.55% | 99.5% | 0.0050 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-60 | P_22_3 | 5.58% | 1.07% | +4.51% | 95.3% | 0.0470 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-70 | P_22_3 | -6.63% | 1.07% | -7.70% | 0.0% | 1.0000 | NO |
| CONTESTANT_C | meerkat-80 | P_22_3 | -7.33% | 1.07% | -8.40% | 0.0% | 1.0000 | NO |
| CONTESTANT_C | meerkat-90 | P_22_3 | -1.47% | 1.07% | -2.54% | 18.1% | 0.8190 | NO |
| CONTESTANT_C | eagle-5-1 | P_5_1 | 12.14% | 0.35% | +11.79% | 96.9% | 0.0310 | YES (p < 0.05) |
| CONTESTANT_C | eagle-11-2 | P_11_2 | 7.08% | 0.84% | +6.24% | 93.9% | 0.0610 | NO |
| CONTESTANT_C | eagle-44-6 | P_44_6 | 5.27% | 1.59% | +3.68% | 98.0% | 0.0200 | YES (p < 0.05) |
| CONTESTANT_C | eagle-66-9 | P_66_9 | 4.76% | 1.94% | +2.82% | 97.8% | 0.0220 | YES (p < 0.05) |
| CONTESTANT_C | eagle-88-12 | P_88_12 | 6.03% | 2.60% | +3.43% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_C | whale-shark | P_123_17 | 5.57% | 3.70% | +1.87% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_D | robot | P_22_3 | 7.67% | 1.07% | +6.60% | 99.5% | 0.0050 | YES (p < 0.05) |
| CONTESTANT_D | sloth-1 | P_22_3 | 7.34% | 1.07% | +6.27% | 99.2% | 0.0080 | YES (p < 0.05) |
| CONTESTANT_D | sloth-2 | P_22_3 | 6.40% | 1.07% | +5.33% | 97.7% | 0.0230 | YES (p < 0.05) |
| CONTESTANT_D | sloth-3 | P_22_3 | 3.16% | 1.07% | +2.09% | 78.1% | 0.2190 | NO |
| CONTESTANT_D | sloth-4 | P_22_3 | 0.17% | 1.07% | -0.90% | 36.5% | 0.6350 | NO |
| CONTESTANT_D | snail-1 | P_22_3 | 5.75% | 1.07% | +4.68% | 95.8% | 0.0420 | YES (p < 0.05) |
| CONTESTANT_D | snail-2 | P_22_3 | 1.71% | 1.07% | +0.64% | 58.0% | 0.4200 | NO |
| CONTESTANT_D | snail-3 | P_22_3 | 1.50% | 1.07% | +0.44% | 55.8% | 0.4420 | NO |
| CONTESTANT_D | snail-4 | P_22_3 | 1.13% | 1.07% | +0.06% | 51.0% | 0.4900 | NO |
| CONTESTANT_D | rabbit-1 | P_22_11 | 12.47% | 0.70% | +11.77% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_D | rabbit-2 | P_22_22 | 10.90% | 0.03% | +10.87% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_D | turtle | P_22_1 | 1.51% | 1.21% | +0.30% | 54.5% | 0.4550 | NO |
| CONTESTANT_D | koala | P_22_3 | -13.52% | 1.07% | -14.59% | 0.0% | 1.0000 | NO |
| CONTESTANT_D | meerkat-10 | P_22_3 | 2.69% | 1.07% | +1.62% | 70.3% | 0.2970 | NO |
| CONTESTANT_D | meerkat-20 | P_22_3 | 8.15% | 1.07% | +7.08% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_D | meerkat-30 | P_22_3 | 6.39% | 1.07% | +5.32% | 97.6% | 0.0240 | YES (p < 0.05) |
| CONTESTANT_D | meerkat-40 | P_22_3 | 2.53% | 1.07% | +1.46% | 68.3% | 0.3170 | NO |
| CONTESTANT_D | meerkat-50 | P_22_3 | 1.25% | 1.07% | +0.18% | 52.4% | 0.4760 | NO |
| CONTESTANT_D | meerkat-60 | P_22_3 | 3.33% | 1.07% | +2.27% | 79.6% | 0.2040 | NO |
| CONTESTANT_D | meerkat-70 | P_22_3 | 2.68% | 1.07% | +1.62% | 70.1% | 0.2990 | NO |
| CONTESTANT_D | meerkat-80 | P_22_3 | 0.85% | 1.07% | -0.22% | 46.7% | 0.5330 | NO |
| CONTESTANT_D | meerkat-90 | P_22_3 | -5.24% | 1.07% | -6.31% | 0.7% | 0.9930 | NO |
| CONTESTANT_D | eagle-5-1 | P_5_1 | 12.79% | 0.35% | +12.44% | 97.3% | 0.0270 | YES (p < 0.05) |
| CONTESTANT_D | eagle-11-2 | P_11_2 | 12.96% | 0.84% | +12.12% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_D | eagle-44-6 | P_44_6 | 8.31% | 1.59% | +6.72% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_D | eagle-66-9 | P_66_9 | 6.19% | 1.94% | +4.25% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_D | eagle-88-12 | P_88_12 | 6.88% | 2.60% | +4.28% | 99.9% | 0.0010 | YES (p < 0.05) |
| CONTESTANT_D | whale-shark | P_123_17 | 4.33% | 3.70% | +0.63% | 81.5% | 0.1850 | NO |
| CONTESTANT_E | robot | P_22_3 | 1.99% | 1.07% | +0.92% | 61.3% | 0.3870 | NO |
| CONTESTANT_E | sloth-1 | P_22_3 | 2.75% | 1.07% | +1.68% | 71.6% | 0.2840 | NO |
| CONTESTANT_E | sloth-2 | P_22_3 | 5.22% | 1.07% | +4.15% | 93.9% | 0.0610 | NO |
| CONTESTANT_E | sloth-3 | P_22_3 | 1.98% | 1.07% | +0.91% | 61.2% | 0.3880 | NO |
| CONTESTANT_E | sloth-4 | P_22_3 | 1.52% | 1.07% | +0.45% | 56.1% | 0.4390 | NO |
| CONTESTANT_E | snail-1 | P_22_3 | 0.13% | 1.07% | -0.93% | 36.1% | 0.6390 | NO |
| CONTESTANT_E | snail-2 | P_22_3 | 0.76% | 1.07% | -0.31% | 45.5% | 0.5450 | NO |
| CONTESTANT_E | snail-3 | P_22_3 | 0.24% | 1.07% | -0.83% | 37.4% | 0.6260 | NO |
| CONTESTANT_E | snail-4 | P_22_3 | 0.58% | 1.07% | -0.49% | 42.5% | 0.5750 | NO |
| CONTESTANT_E | rabbit-1 | P_22_11 | 4.90% | 0.70% | +4.20% | 92.1% | 0.0790 | NO |
| CONTESTANT_E | rabbit-2 | P_22_22 | 3.79% | 0.03% | +3.76% | 89.8% | 0.1020 | NO |
| CONTESTANT_E | turtle | P_22_1 | 1.14% | 1.21% | -0.07% | 49.5% | 0.5050 | NO |
| CONTESTANT_E | koala | P_22_3 | 2.72% | 1.07% | +1.65% | 71.2% | 0.2880 | NO |
| CONTESTANT_E | meerkat-10 | P_22_3 | -0.87% | 1.07% | -1.94% | 24.0% | 0.7600 | NO |
| CONTESTANT_E | meerkat-20 | P_22_3 | 8.56% | 1.07% | +7.49% | 99.8% | 0.0020 | YES (p < 0.05) |
| CONTESTANT_E | meerkat-30 | P_22_3 | -1.38% | 1.07% | -2.45% | 18.4% | 0.8160 | NO |
| CONTESTANT_E | meerkat-40 | P_22_3 | 5.33% | 1.07% | +4.26% | 94.2% | 0.0580 | NO |
| CONTESTANT_E | meerkat-50 | P_22_3 | 0.64% | 1.07% | -0.43% | 43.7% | 0.5630 | NO |
| CONTESTANT_E | meerkat-60 | P_22_3 | 2.59% | 1.07% | +1.53% | 69.2% | 0.3080 | NO |
| CONTESTANT_E | meerkat-70 | P_22_3 | -1.53% | 1.07% | -2.60% | 17.6% | 0.8240 | NO |
| CONTESTANT_E | meerkat-80 | P_22_3 | -0.25% | 1.07% | -1.32% | 31.3% | 0.6870 | NO |
| CONTESTANT_E | meerkat-90 | P_22_3 | -3.08% | 1.07% | -4.15% | 6.7% | 0.9330 | NO |
| CONTESTANT_E | eagle-5-1 | P_5_1 | 7.89% | 0.35% | +7.55% | 87.7% | 0.1230 | NO |
| CONTESTANT_E | eagle-11-2 | P_11_2 | 4.21% | 0.84% | +3.37% | 79.7% | 0.2030 | NO |
| CONTESTANT_E | eagle-44-6 | P_44_6 | 2.93% | 1.59% | +1.33% | 77.4% | 0.2260 | NO |
| CONTESTANT_E | eagle-66-9 | P_66_9 | 3.34% | 1.94% | +1.40% | 84.3% | 0.1570 | NO |
| CONTESTANT_E | eagle-88-12 | P_88_12 | 2.75% | 2.60% | +0.15% | 57.9% | 0.4210 | NO |
| CONTESTANT_E | whale-shark | P_123_17 | 3.72% | 3.70% | +0.02% | 51.9% | 0.4810 | NO |
| CONTESTANT_F | robot | P_22_3 | 5.27% | 1.07% | +4.20% | 94.0% | 0.0600 | NO |
| CONTESTANT_F | sloth-1 | P_22_3 | 4.45% | 1.07% | +3.38% | 88.9% | 0.1110 | NO |
| CONTESTANT_F | sloth-2 | P_22_3 | 5.26% | 1.07% | +4.19% | 94.0% | 0.0600 | NO |
| CONTESTANT_F | sloth-3 | P_22_3 | 2.27% | 1.07% | +1.20% | 65.2% | 0.3480 | NO |
| CONTESTANT_F | sloth-4 | P_22_3 | 2.95% | 1.07% | +1.88% | 74.4% | 0.2560 | NO |
| CONTESTANT_F | snail-1 | P_22_3 | 3.72% | 1.07% | +2.66% | 83.3% | 0.1670 | NO |
| CONTESTANT_F | snail-2 | P_22_3 | 3.51% | 1.07% | +2.44% | 81.0% | 0.1900 | NO |
| CONTESTANT_F | snail-3 | P_22_3 | 3.57% | 1.07% | +2.50% | 81.7% | 0.1830 | NO |
| CONTESTANT_F | snail-4 | P_22_3 | 4.79% | 1.07% | +3.72% | 91.1% | 0.0890 | NO |
| CONTESTANT_F | rabbit-1 | P_22_11 | -1.94% | 0.70% | -2.63% | 18.6% | 0.8140 | NO |
| CONTESTANT_F | rabbit-2 | P_22_22 | 0.73% | 0.03% | +0.70% | 59.2% | 0.4080 | NO |
| CONTESTANT_F | turtle | P_22_1 | 5.86% | 1.21% | +4.65% | 95.8% | 0.0420 | YES (p < 0.05) |
| CONTESTANT_F | koala | P_22_3 | 5.10% | 1.07% | +4.03% | 93.1% | 0.0690 | NO |
| CONTESTANT_F | meerkat-10 | P_22_3 | 0.33% | 1.07% | -0.74% | 38.8% | 0.6120 | NO |
| CONTESTANT_F | meerkat-20 | P_22_3 | 6.19% | 1.07% | +5.12% | 97.2% | 0.0280 | YES (p < 0.05) |
| CONTESTANT_F | meerkat-30 | P_22_3 | 0.65% | 1.07% | -0.42% | 43.9% | 0.5610 | NO |
| CONTESTANT_F | meerkat-40 | P_22_3 | 0.75% | 1.07% | -0.32% | 45.1% | 0.5490 | NO |
| CONTESTANT_F | meerkat-50 | P_22_3 | 2.90% | 1.07% | +1.83% | 74.0% | 0.2600 | NO |
| CONTESTANT_F | meerkat-60 | P_22_3 | -0.09% | 1.07% | -1.15% | 33.4% | 0.6660 | NO |
| CONTESTANT_F | meerkat-70 | P_22_3 | -0.71% | 1.07% | -1.78% | 25.8% | 0.7420 | NO |
| CONTESTANT_F | meerkat-80 | P_22_3 | 0.96% | 1.07% | -0.11% | 47.8% | 0.5220 | NO |
| CONTESTANT_F | meerkat-90 | P_22_3 | -4.30% | 1.07% | -5.37% | 2.8% | 0.9720 | NO |
| CONTESTANT_F | eagle-5-1 | P_5_1 | 8.51% | 0.35% | +8.16% | 89.2% | 0.1080 | NO |
| CONTESTANT_F | eagle-11-2 | P_11_2 | 4.35% | 0.84% | +3.51% | 80.7% | 0.1930 | NO |
| CONTESTANT_F | eagle-44-6 | P_44_6 | 1.29% | 1.59% | -0.30% | 43.9% | 0.5610 | NO |
| CONTESTANT_F | eagle-66-9 | P_66_9 | 1.49% | 1.94% | -0.45% | 36.1% | 0.6390 | NO |
| CONTESTANT_F | eagle-88-12 | P_88_12 | 3.32% | 2.60% | +0.72% | 77.8% | 0.2220 | NO |
| CONTESTANT_F | whale-shark | P_123_17 | 3.29% | 3.70% | -0.41% | 25.5% | 0.7450 | NO |
| BENCHMARK | taotie | P_ALL_0 | 2.32% | 2.32% | +0.00% | 0.0% | 1.0000 | NO |
