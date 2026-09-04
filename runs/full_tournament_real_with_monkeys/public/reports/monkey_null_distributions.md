# QuantPits Graveyard Arena — Parametric Monkey Colony Diagnostics

Run ID: `full_tournament_real_with_monkeys`

## 1. Methodology & Scientific Rationale

The **Parametric Monkey Colony** serves as the rigorous empirical null model for evaluating whether contestants' alpha returns are statistically distinguishable from pure random stock picking.

- **Zero Future Information**: Every monkey draws uniform random scores across the cross-section using deterministic seeds: `seed = (2026 + m * 10007 + t * 37) % (2**31 - 1)`.
- **Strict Parity**: Each monkey group operates under the **exact same 100-share minimum trading lot and CNY 500,000 capital constraints** as the real models.
- **Complete Parameter Coverage**: All 11 distinct portfolio execution policies (TopK / DropN pairs, including Taotie passive full-universe) are individually benchmarked by 100 random monkeys (1,100 monkeys total).
- **Empirical P-Value**: Formally defined as $p = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{monkey}_i \ge \text{actual_return})$. $p < 0.05$ indicates significant alpha superiority over random chance at 95% confidence.

## 2. Null Distributions by Strategy Parameter Group (11 Groups × 100 Monkeys)

| strategy_spec | topk | n_drop | description | colony_size | monkey_min | monkey_p05 | monkey_median | monkey_mean | monkey_p95 | monkey_max | monkey_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_22_3 | 22 | 3 | Robot, Sloth-1~4, Snail-1~4, Meerkat-10~90, Koala | 100 | -5.14% | -3.26% | 0.89% | 0.88% | 4.79% | 9.62% | 2.60% |
| P_22_11 | 22 | 11 | Rabbit-1 (半仓换手) | 100 | -5.99% | -4.14% | 0.75% | 0.49% | 4.51% | 5.78% | 2.60% |
| P_22_22 | 22 | 22 | Rabbit-2 (全仓换手) | 100 | -7.93% | -4.17% | 0.12% | 0.14% | 4.95% | 7.80% | 2.90% |
| P_22_1 | 22 | 1 | Turtle (极低换手) | 100 | -5.41% | -3.01% | 1.02% | 0.91% | 4.27% | 10.19% | 2.50% |
| P_5_1 | 5 | 1 | Eagle-5/1 (极端集中组合) | 100 | -18.23% | -10.18% | 0.68% | 0.15% | 11.46% | 12.52% | 6.16% |
| P_11_2 | 11 | 2 | Eagle-11/2 (紧凑半数组合) | 100 | -11.86% | -5.99% | 0.66% | 0.67% | 6.13% | 11.50% | 3.84% |
| P_44_6 | 44 | 6 | Eagle-44/6 (2 倍容量宽度) | 100 | -3.95% | -1.75% | 1.52% | 1.50% | 4.13% | 5.19% | 1.74% |
| P_66_9 | 66 | 9 | Eagle-66/9 (3 倍容量宽度) | 100 | -2.62% | -0.72% | 1.97% | 1.96% | 4.06% | 5.80% | 1.42% |
| P_88_12 | 88 | 12 | Eagle-88/12 (4 倍容量宽度) | 100 | 0.48% | 0.92% | 2.50% | 2.57% | 4.05% | 5.04% | 0.94% |
| P_123_17 | 123 | 17 | WhaleShark (半池大容量组合) | 100 | 1.68% | 2.54% | 3.72% | 3.71% | 4.60% | 5.27% | 0.63% |
| P_ALL_0 | 全池 | 被动 | Taotie (全池吞噬被动组合) | 100 | 2.32% | 2.32% | 2.32% | 2.32% | 2.32% | 2.32% | 0.00% |

## 3. Contestant Significance vs. Corresponding Monkey Colony

| contestant_id | animal_id | strategy_spec | actual_return_pct | monkey_median_pct | excess_over_monkey_pct | percentile_rank | empirical_p_value | significant_95pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONTESTANT_A | robot | P_22_3 | 8.65% | 0.89% | +7.76% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_A | sloth-1 | P_22_3 | 6.61% | 0.89% | +5.72% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_A | sloth-2 | P_22_3 | 9.25% | 0.89% | +8.36% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_A | sloth-3 | P_22_3 | 6.10% | 0.89% | +5.22% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_A | sloth-4 | P_22_3 | 1.38% | 0.89% | +0.49% | 58.0% | 0.4200 | NO |
| CONTESTANT_A | snail-1 | P_22_3 | 5.59% | 0.89% | +4.70% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_A | snail-2 | P_22_3 | 3.50% | 0.89% | +2.61% | 84.0% | 0.1600 | NO |
| CONTESTANT_A | snail-3 | P_22_3 | 3.85% | 0.89% | +2.97% | 89.0% | 0.1100 | NO |
| CONTESTANT_A | snail-4 | P_22_3 | 2.52% | 0.89% | +1.63% | 73.0% | 0.2700 | NO |
| CONTESTANT_A | rabbit-1 | P_22_11 | 13.13% | 0.75% | +12.38% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_A | rabbit-2 | P_22_22 | 10.40% | 0.12% | +10.28% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_A | turtle | P_22_1 | 5.72% | 1.02% | +4.71% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_A | koala | P_22_3 | -10.48% | 0.89% | -11.37% | 0.0% | 1.0000 | NO |
| CONTESTANT_A | meerkat-10 | P_22_3 | 2.58% | 0.89% | +1.69% | 73.0% | 0.2700 | NO |
| CONTESTANT_A | meerkat-20 | P_22_3 | 4.65% | 0.89% | +3.77% | 93.0% | 0.0700 | NO |
| CONTESTANT_A | meerkat-30 | P_22_3 | 4.36% | 0.89% | +3.47% | 92.0% | 0.0800 | NO |
| CONTESTANT_A | meerkat-40 | P_22_3 | 3.46% | 0.89% | +2.57% | 84.0% | 0.1600 | NO |
| CONTESTANT_A | meerkat-50 | P_22_3 | 5.77% | 0.89% | +4.89% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_A | meerkat-60 | P_22_3 | 0.50% | 0.89% | -0.39% | 42.0% | 0.5800 | NO |
| CONTESTANT_A | meerkat-70 | P_22_3 | -4.01% | 0.89% | -4.90% | 3.0% | 0.9700 | NO |
| CONTESTANT_A | meerkat-80 | P_22_3 | -1.23% | 0.89% | -2.12% | 22.0% | 0.7800 | NO |
| CONTESTANT_A | meerkat-90 | P_22_3 | -2.01% | 0.89% | -2.90% | 14.0% | 0.8600 | NO |
| CONTESTANT_A | eagle-5-1 | P_5_1 | 12.67% | 0.68% | +12.00% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_A | eagle-11-2 | P_11_2 | 14.68% | 0.66% | +14.03% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_A | eagle-44-6 | P_44_6 | 9.59% | 1.52% | +8.07% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_A | eagle-66-9 | P_66_9 | 6.41% | 1.97% | +4.44% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_A | eagle-88-12 | P_88_12 | 6.80% | 2.50% | +4.30% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_A | whale-shark | P_123_17 | 4.61% | 3.72% | +0.90% | 95.0% | 0.0500 | NO |
| CONTESTANT_B | robot | P_22_3 | 12.20% | 0.89% | +11.32% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | sloth-1 | P_22_3 | 14.38% | 0.89% | +13.49% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | sloth-2 | P_22_3 | 8.69% | 0.89% | +7.80% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | sloth-3 | P_22_3 | 4.69% | 0.89% | +3.80% | 93.0% | 0.0700 | NO |
| CONTESTANT_B | sloth-4 | P_22_3 | 0.11% | 0.89% | -0.78% | 39.0% | 0.6100 | NO |
| CONTESTANT_B | snail-1 | P_22_3 | 11.19% | 0.89% | +10.30% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | snail-2 | P_22_3 | 6.29% | 0.89% | +5.41% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | snail-3 | P_22_3 | 7.50% | 0.89% | +6.61% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | snail-4 | P_22_3 | 6.28% | 0.89% | +5.39% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | rabbit-1 | P_22_11 | 10.76% | 0.75% | +10.01% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | rabbit-2 | P_22_22 | 8.95% | 0.12% | +8.83% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | turtle | P_22_1 | 10.60% | 1.02% | +9.58% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | koala | P_22_3 | -10.60% | 0.89% | -11.48% | 0.0% | 1.0000 | NO |
| CONTESTANT_B | meerkat-10 | P_22_3 | 6.34% | 0.89% | +5.46% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | meerkat-20 | P_22_3 | 7.41% | 0.89% | +6.53% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | meerkat-30 | P_22_3 | 5.17% | 0.89% | +4.28% | 96.0% | 0.0400 | YES (p < 0.05) |
| CONTESTANT_B | meerkat-40 | P_22_3 | 6.76% | 0.89% | +5.87% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | meerkat-50 | P_22_3 | 2.45% | 0.89% | +1.56% | 72.0% | 0.2800 | NO |
| CONTESTANT_B | meerkat-60 | P_22_3 | -1.08% | 0.89% | -1.97% | 23.0% | 0.7700 | NO |
| CONTESTANT_B | meerkat-70 | P_22_3 | 0.44% | 0.89% | -0.45% | 41.0% | 0.5900 | NO |
| CONTESTANT_B | meerkat-80 | P_22_3 | -2.96% | 0.89% | -3.85% | 7.0% | 0.9300 | NO |
| CONTESTANT_B | meerkat-90 | P_22_3 | -10.32% | 0.89% | -11.21% | 0.0% | 1.0000 | NO |
| CONTESTANT_B | eagle-5-1 | P_5_1 | 19.71% | 0.68% | +19.03% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | eagle-11-2 | P_11_2 | 11.38% | 0.66% | +10.72% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_B | eagle-44-6 | P_44_6 | 10.74% | 1.52% | +9.23% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | eagle-66-9 | P_66_9 | 6.85% | 1.97% | +4.88% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | eagle-88-12 | P_88_12 | 7.19% | 2.50% | +4.68% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_B | whale-shark | P_123_17 | 4.83% | 3.72% | +1.12% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_C | robot | P_22_3 | 6.93% | 0.89% | +6.04% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | sloth-1 | P_22_3 | 7.76% | 0.89% | +6.88% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | sloth-2 | P_22_3 | 8.09% | 0.89% | +7.21% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | sloth-3 | P_22_3 | 5.65% | 0.89% | +4.76% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_C | sloth-4 | P_22_3 | 4.22% | 0.89% | +3.33% | 92.0% | 0.0800 | NO |
| CONTESTANT_C | snail-1 | P_22_3 | 6.38% | 0.89% | +5.49% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | snail-2 | P_22_3 | 6.07% | 0.89% | +5.18% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_C | snail-3 | P_22_3 | 5.61% | 0.89% | +4.72% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_C | snail-4 | P_22_3 | 5.60% | 0.89% | +4.71% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_C | rabbit-1 | P_22_11 | 5.23% | 0.75% | +4.48% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | rabbit-2 | P_22_22 | 6.74% | 0.12% | +6.61% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | turtle | P_22_1 | 6.36% | 1.02% | +5.35% | 98.0% | 0.0200 | YES (p < 0.05) |
| CONTESTANT_C | koala | P_22_3 | -8.84% | 0.89% | -9.73% | 0.0% | 1.0000 | NO |
| CONTESTANT_C | meerkat-10 | P_22_3 | 3.52% | 0.89% | +2.64% | 85.0% | 0.1500 | NO |
| CONTESTANT_C | meerkat-20 | P_22_3 | 1.03% | 0.89% | +0.14% | 51.0% | 0.4900 | NO |
| CONTESTANT_C | meerkat-30 | P_22_3 | 9.06% | 0.89% | +8.17% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-40 | P_22_3 | 8.17% | 0.89% | +7.28% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-50 | P_22_3 | 7.62% | 0.89% | +6.73% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-60 | P_22_3 | 5.58% | 0.89% | +4.69% | 96.0% | 0.0400 | YES (p < 0.05) |
| CONTESTANT_C | meerkat-70 | P_22_3 | -6.63% | 0.89% | -7.52% | 0.0% | 1.0000 | NO |
| CONTESTANT_C | meerkat-80 | P_22_3 | -7.33% | 0.89% | -8.21% | 0.0% | 1.0000 | NO |
| CONTESTANT_C | meerkat-90 | P_22_3 | -1.47% | 0.89% | -2.36% | 20.0% | 0.8000 | NO |
| CONTESTANT_C | eagle-5-1 | P_5_1 | 12.14% | 0.68% | +11.46% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_C | eagle-11-2 | P_11_2 | 7.08% | 0.66% | +6.42% | 98.0% | 0.0200 | YES (p < 0.05) |
| CONTESTANT_C | eagle-44-6 | P_44_6 | 5.27% | 1.52% | +3.75% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_C | eagle-66-9 | P_66_9 | 4.62% | 1.97% | +2.65% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_C | eagle-88-12 | P_88_12 | 6.03% | 2.50% | +3.53% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_C | whale-shark | P_123_17 | 5.57% | 3.72% | +1.85% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | robot | P_22_3 | 7.67% | 0.89% | +6.78% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_D | sloth-1 | P_22_3 | 7.34% | 0.89% | +6.45% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_D | sloth-2 | P_22_3 | 6.40% | 0.89% | +5.51% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_D | sloth-3 | P_22_3 | 3.16% | 0.89% | +2.27% | 82.0% | 0.1800 | NO |
| CONTESTANT_D | sloth-4 | P_22_3 | 0.17% | 0.89% | -0.72% | 40.0% | 0.6000 | NO |
| CONTESTANT_D | snail-1 | P_22_3 | 5.75% | 0.89% | +4.87% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_D | snail-2 | P_22_3 | 1.71% | 0.89% | +0.82% | 63.0% | 0.3700 | NO |
| CONTESTANT_D | snail-3 | P_22_3 | 1.50% | 0.89% | +0.62% | 60.0% | 0.4000 | NO |
| CONTESTANT_D | snail-4 | P_22_3 | 1.13% | 0.89% | +0.25% | 51.0% | 0.4900 | NO |
| CONTESTANT_D | rabbit-1 | P_22_11 | 12.47% | 0.75% | +11.71% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | rabbit-2 | P_22_22 | 10.90% | 0.12% | +10.78% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | turtle | P_22_1 | 1.51% | 1.02% | +0.49% | 58.0% | 0.4200 | NO |
| CONTESTANT_D | koala | P_22_3 | -13.52% | 0.89% | -14.41% | 0.0% | 1.0000 | NO |
| CONTESTANT_D | meerkat-10 | P_22_3 | 2.69% | 0.89% | +1.80% | 75.0% | 0.2500 | NO |
| CONTESTANT_D | meerkat-20 | P_22_3 | 8.15% | 0.89% | +7.27% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_D | meerkat-30 | P_22_3 | 6.39% | 0.89% | +5.50% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_D | meerkat-40 | P_22_3 | 2.53% | 0.89% | +1.64% | 73.0% | 0.2700 | NO |
| CONTESTANT_D | meerkat-50 | P_22_3 | 1.25% | 0.89% | +0.37% | 54.0% | 0.4600 | NO |
| CONTESTANT_D | meerkat-60 | P_22_3 | 3.33% | 0.89% | +2.45% | 84.0% | 0.1600 | NO |
| CONTESTANT_D | meerkat-70 | P_22_3 | 2.68% | 0.89% | +1.80% | 75.0% | 0.2500 | NO |
| CONTESTANT_D | meerkat-80 | P_22_3 | 0.85% | 0.89% | -0.04% | 50.0% | 0.5000 | NO |
| CONTESTANT_D | meerkat-90 | P_22_3 | -5.24% | 0.89% | -6.13% | 0.0% | 1.0000 | NO |
| CONTESTANT_D | eagle-5-1 | P_5_1 | 12.79% | 0.68% | +12.11% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | eagle-11-2 | P_11_2 | 12.96% | 0.66% | +12.30% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | eagle-44-6 | P_44_6 | 8.31% | 1.52% | +6.79% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | eagle-66-9 | P_66_9 | 6.19% | 1.97% | +4.22% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | eagle-88-12 | P_88_12 | 6.88% | 2.50% | +4.38% | 100.0% | 0.0000 | YES (p < 0.05) |
| CONTESTANT_D | whale-shark | P_123_17 | 4.33% | 3.72% | +0.61% | 81.0% | 0.1900 | NO |
| CONTESTANT_E | robot | P_22_3 | 1.99% | 0.89% | +1.11% | 68.0% | 0.3200 | NO |
| CONTESTANT_E | sloth-1 | P_22_3 | 2.75% | 0.89% | +1.86% | 76.0% | 0.2400 | NO |
| CONTESTANT_E | sloth-2 | P_22_3 | 5.22% | 0.89% | +4.34% | 96.0% | 0.0400 | YES (p < 0.05) |
| CONTESTANT_E | sloth-3 | P_22_3 | 1.98% | 0.89% | +1.09% | 68.0% | 0.3200 | NO |
| CONTESTANT_E | sloth-4 | P_22_3 | 1.52% | 0.89% | +0.63% | 60.0% | 0.4000 | NO |
| CONTESTANT_E | snail-1 | P_22_3 | 0.13% | 0.89% | -0.75% | 39.0% | 0.6100 | NO |
| CONTESTANT_E | snail-2 | P_22_3 | 0.76% | 0.89% | -0.13% | 48.0% | 0.5200 | NO |
| CONTESTANT_E | snail-3 | P_22_3 | 0.24% | 0.89% | -0.64% | 40.0% | 0.6000 | NO |
| CONTESTANT_E | snail-4 | P_22_3 | 0.58% | 0.89% | -0.31% | 44.0% | 0.5600 | NO |
| CONTESTANT_E | rabbit-1 | P_22_11 | 4.90% | 0.75% | +4.14% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_E | rabbit-2 | P_22_22 | 3.79% | 0.12% | +3.66% | 88.0% | 0.1200 | NO |
| CONTESTANT_E | turtle | P_22_1 | 1.14% | 1.02% | +0.13% | 54.0% | 0.4600 | NO |
| CONTESTANT_E | koala | P_22_3 | 2.72% | 0.89% | +1.84% | 76.0% | 0.2400 | NO |
| CONTESTANT_E | meerkat-10 | P_22_3 | -0.87% | 0.89% | -1.75% | 27.0% | 0.7300 | NO |
| CONTESTANT_E | meerkat-20 | P_22_3 | 8.56% | 0.89% | +7.68% | 99.0% | 0.0100 | YES (p < 0.05) |
| CONTESTANT_E | meerkat-30 | P_22_3 | -1.38% | 0.89% | -2.27% | 21.0% | 0.7900 | NO |
| CONTESTANT_E | meerkat-40 | P_22_3 | 5.33% | 0.89% | +4.44% | 96.0% | 0.0400 | YES (p < 0.05) |
| CONTESTANT_E | meerkat-50 | P_22_3 | 0.64% | 0.89% | -0.25% | 46.0% | 0.5400 | NO |
| CONTESTANT_E | meerkat-60 | P_22_3 | 2.59% | 0.89% | +1.71% | 73.0% | 0.2700 | NO |
| CONTESTANT_E | meerkat-70 | P_22_3 | -1.53% | 0.89% | -2.41% | 19.0% | 0.8100 | NO |
| CONTESTANT_E | meerkat-80 | P_22_3 | -0.25% | 0.89% | -1.14% | 33.0% | 0.6700 | NO |
| CONTESTANT_E | meerkat-90 | P_22_3 | -3.08% | 0.89% | -3.97% | 6.0% | 0.9400 | NO |
| CONTESTANT_E | eagle-5-1 | P_5_1 | 7.89% | 0.68% | +7.22% | 89.0% | 0.1100 | NO |
| CONTESTANT_E | eagle-11-2 | P_11_2 | 4.21% | 0.66% | +3.55% | 81.0% | 0.1900 | NO |
| CONTESTANT_E | eagle-44-6 | P_44_6 | 2.93% | 1.52% | +1.41% | 76.0% | 0.2400 | NO |
| CONTESTANT_E | eagle-66-9 | P_66_9 | 3.34% | 1.97% | +1.36% | 85.0% | 0.1500 | NO |
| CONTESTANT_E | eagle-88-12 | P_88_12 | 2.75% | 2.50% | +0.25% | 58.0% | 0.4200 | NO |
| CONTESTANT_E | whale-shark | P_123_17 | 3.72% | 3.72% | +0.01% | 51.0% | 0.4900 | NO |
| CONTESTANT_F | robot | P_22_3 | 5.27% | 0.89% | +4.38% | 96.0% | 0.0400 | YES (p < 0.05) |
| CONTESTANT_F | sloth-1 | P_22_3 | 4.45% | 0.89% | +3.57% | 92.0% | 0.0800 | NO |
| CONTESTANT_F | sloth-2 | P_22_3 | 5.26% | 0.89% | +4.37% | 96.0% | 0.0400 | YES (p < 0.05) |
| CONTESTANT_F | sloth-3 | P_22_3 | 2.27% | 0.89% | +1.39% | 71.0% | 0.2900 | NO |
| CONTESTANT_F | sloth-4 | P_22_3 | 2.95% | 0.89% | +2.07% | 78.0% | 0.2200 | NO |
| CONTESTANT_F | snail-1 | P_22_3 | 3.72% | 0.89% | +2.84% | 88.0% | 0.1200 | NO |
| CONTESTANT_F | snail-2 | P_22_3 | 3.51% | 0.89% | +2.62% | 85.0% | 0.1500 | NO |
| CONTESTANT_F | snail-3 | P_22_3 | 3.57% | 0.89% | +2.68% | 87.0% | 0.1300 | NO |
| CONTESTANT_F | snail-4 | P_22_3 | 4.79% | 0.89% | +3.90% | 95.0% | 0.0500 | NO |
| CONTESTANT_F | rabbit-1 | P_22_11 | -1.94% | 0.75% | -2.69% | 18.0% | 0.8200 | NO |
| CONTESTANT_F | rabbit-2 | P_22_22 | 0.73% | 0.12% | +0.60% | 56.0% | 0.4400 | NO |
| CONTESTANT_F | turtle | P_22_1 | 5.86% | 1.02% | +4.85% | 97.0% | 0.0300 | YES (p < 0.05) |
| CONTESTANT_F | koala | P_22_3 | 5.10% | 0.89% | +4.21% | 96.0% | 0.0400 | YES (p < 0.05) |
| CONTESTANT_F | meerkat-10 | P_22_3 | 0.33% | 0.89% | -0.56% | 41.0% | 0.5900 | NO |
| CONTESTANT_F | meerkat-20 | P_22_3 | 6.19% | 0.89% | +5.31% | 98.0% | 0.0200 | YES (p < 0.05) |
| CONTESTANT_F | meerkat-30 | P_22_3 | 0.65% | 0.89% | -0.23% | 46.0% | 0.5400 | NO |
| CONTESTANT_F | meerkat-40 | P_22_3 | 0.75% | 0.89% | -0.14% | 48.0% | 0.5200 | NO |
| CONTESTANT_F | meerkat-50 | P_22_3 | 2.90% | 0.89% | +2.01% | 78.0% | 0.2200 | NO |
| CONTESTANT_F | meerkat-60 | P_22_3 | -0.09% | 0.89% | -0.97% | 34.0% | 0.6600 | NO |
| CONTESTANT_F | meerkat-70 | P_22_3 | -0.71% | 0.89% | -1.60% | 28.0% | 0.7200 | NO |
| CONTESTANT_F | meerkat-80 | P_22_3 | 0.96% | 0.89% | +0.07% | 50.0% | 0.5000 | NO |
| CONTESTANT_F | meerkat-90 | P_22_3 | -4.30% | 0.89% | -5.19% | 2.0% | 0.9800 | NO |
| CONTESTANT_F | eagle-5-1 | P_5_1 | 8.51% | 0.68% | +7.83% | 90.0% | 0.1000 | NO |
| CONTESTANT_F | eagle-11-2 | P_11_2 | 4.35% | 0.66% | +3.69% | 81.0% | 0.1900 | NO |
| CONTESTANT_F | eagle-44-6 | P_44_6 | 1.29% | 1.52% | -0.23% | 44.0% | 0.5600 | NO |
| CONTESTANT_F | eagle-66-9 | P_66_9 | 1.49% | 1.97% | -0.48% | 33.0% | 0.6700 | NO |
| CONTESTANT_F | eagle-88-12 | P_88_12 | 3.32% | 2.50% | +0.82% | 77.0% | 0.2300 | NO |
| CONTESTANT_F | whale-shark | P_123_17 | 3.29% | 3.72% | -0.43% | 22.0% | 0.7800 | NO |
| BENCHMARK | taotie | P_ALL_0 | 2.32% | 2.32% | -0.00% | 3.0% | 0.9700 | NO |
