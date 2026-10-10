# 🏛️ QuantPits Arena Chronicles: Season 1 Log & Dispatches

> **An empirical tournament log tracking quantitative alpha models through execution frictions, market regime shifts, and monkey null courts.**

---

## 🧭 Season 1 Overview: Summer 2026

* **Tournament Baseline**: July 3, 2026 – August 28, 2026 (41 trading days post-training OOS).
* **Contestants**: 6 anonymous contestants evaluated under a standardized simulation budget and strict 100-share trading lots.
* **The Execution Zoo**: 28 distinct portfolio policies (Eagles, Rabbits, Sloths, Snails, Koalas, Meerkats) testing selection intensity, signal lag, turnover, and concentration.
* **The Null Court**: 11,000 deterministic pseudo-random monkey portfolios across 11 matched parameter groups (1,000 monkeys per jurisdiction).

---

## 📜 Episode Dispatches (Season 1: csirun300 Subset)

| Episode | Evaluation Window | Tournament Phase | Core Narrative & Empirical Boundary | Status |
| :---: | :---: | :---: | :--- | :---: |
| [**Episodes 01–08**](en/episodes_01_08_the_forty_one_day_king.md) | `2026-07-03 ~ 2026-08-28`<br/>(41 Trading Days, Weeks 1–8) | **Retrospective Backtest Baseline** | **The Forty-One Day Baseline**: Simulated retrospectively with knowledge of July–August market conditions. `CONTESTANT_B_eagle-5-1` topped the leaderboard at NAV `1.1971` (+19.71%, raw $p \approx 0.001$, Bonferroni $0.168 > 0.05$). | **Released** |
| [**Episode 09**](en/episode_09_the_september_02_breadth_shock_and_rabbit_rampage.md) | `2026-08-31 ~ 2026-09-04`<br/>(Days 42~46, Cycle 1) | **Prospective Forward Tracking** | **The September 02 Breadth Shock & Rabbit Rampage**: 99.4% of paths suffered active exposure pullbacks on Wednesday; `CONTESTANT_D_rabbit-1` gained +2.41% on the week, compressing the crown margin to 1.89pp. | **Released** |
| [**Episode 10**](en/episode_10_the_apex_strike_and_the_120_milestone.md) | `2026-09-07 ~ 2026-09-11`<br/>(Days 47~51, Cycle 2) | **Prospective Forward Tracking** | **The Apex Strike & The 1.20 Milestone**: High-conviction Eagles counter-attacked; `CONTESTANT_B_eagle-5-1` (+2.06%) became the first strategy to breach the 1.20 NAV milestone (NAV `1.2071`, +20.71%). | **Released** |
| [**Episode 11**](en/episode_11_the_mid_september_turbulence_and_contestant_d_surge.md) | `2026-09-14 ~ 2026-09-18`<br/>(Days 52~56, Cycle 3) | **Prospective Forward Tracking** | **The Mid-September Turbulence & CONTESTANT_D's Charge**: Eagle King pulled back (-2.18%, lead compressed to 4.51pp); `CONTESTANT_D` family took 3 of the Top 5 seats, led by `eagle-5-1` (+1.77% on the week). | **Released** |
| [**Episode 12**](en/episode_12_the_mid_autumn_trial_and_apex_resurgence.md) | `2026-09-21 ~ 2026-09-24`<br/>(4 sessions) | **Continued Forward Tracking** | **The Apex Resurgence**: B's cumulative leader reached NAV 1.1952 (+19.52%); C's concentrated variant won the period at +1.57%. | **Released** |
| [**Episode 13**](en/episode_13_the_three_day_trial.md) | `2026-09-28 ~ 2026-09-30`<br/>(3 sessions; 63 NAV observations including anchor) | **Continued Forward Tracking** | **The Three-Day Trial**: C won at +2.24%; B retained the crown at NAV 1.2054, with a 6.12pp lead and cumulative matched upper-tail p = 0.0020. | **Released** |
| [**Episode 14**](en/episode_14_the_two_day_return.md) | `2026-10-08 ~ 2026-10-09`<br/>(2 valuation sessions; 65 NAV observations including anchor) | **Continued Forward Tracking** | **The Same Holdings, a Wider Crown**: No new trades; E's meerkat-50 won at +2.02%; B reached NAV 1.2240 (+22.40%) and a 7.14pp cumulative lead. | **Released** |

---

## 🏛️ Broad-Market Testbeds: Monthly Season Baselines (Months 01–02)

Alongside the original csirun300 subset arena, broader-market testbeds evaluate capital constraints, discrete lot indivisibility, and signal decay on a monthly cadence:

| Testbed | Evaluation Universe | Budget Convention | Inception Baseline (M1–M2) | Status |
| :---: | :---: | :---: | :--- | :---: |
| [**CSI 300 Full Universe**](en/season_csi300_m1_m2.md) | 300 Large Caps | Standardized | **Eagle Lead, Rabbit Pursuit**: Retrospective baseline reconstructed October 10. B's eagle-5-1 leads at NAV 1.1945 (+19.45%); D's rabbit-1 follows at +16.57%. Independent of the csirun300 subset. | **Released** |
| [**CSI 1000**](en/season_csi1000_m1_m2.md) | 1,000 Small Caps | Standardized | **Small-Cap Sloth Dominance & The Cash Shield**: Amid a -12.91% index collapse, `CONTESTANT_B_sloth-2` finished at NAV `1.1343` (+13.43%); Snail controls returned +2.49% to +4.88%; differing exposure histories limit selection attribution. | **Released** |
| [**CSI 500**](en/season_csi500_m1_m2.md) | 500 Mid Caps | Standardized | **Mid-Cap Dispersion & The Rabbit Surge**: Across a -12.49% index drawdown, agile Rabbit handlers generated nearly +10% absolute return led by `CONTESTANT_B_rabbit-1` (NAV `1.0998`, +9.98%, +22.47pp vs index). | **Released** |
| [**CSI 800**](en/season_csi800_m1_m2.md) | 800 Broad Caps | Standardized | **Broad-Cap Rabbit Supremacy**: Combining large-cap liquidity with mid-cap dispersion, `CONTESTANT_B_rabbit-2` vaulted to NAV `1.1284` (+12.84%, +20.74pp vs index); scaled Whale-Shark achieved NAV `1.0830`. | **Released** |

September 28 is the last rebalance for Episodes 13–14; October 8–9 only values the same holdings. The next scheduled rebalance is October 12. Dispatch numbers do not count trades.

The full CSI 300 season was reconstructed on 2026-10-10 using the common July 3 anchor and an independent 300-stock cache. It is distinct from the 246-stock csirun300 subset; its historical reports are retrospective.

Each expanded testbed has an independent M3 report, anchored at August 28 and ending at September 30 (22 sessions). October 8–9 appears in a separate holdings-only appendix:

| Testbed | Independent M3 report | September winner | September cumulative leader |
| :--- | :--- | :--- | :--- |
| CSI 300 Full Universe | [Rabbit Crown, Eagle Month](en/season_csi300_m3.md) | E eagle-11-2, +2.52% | D rabbit-1, +17.99% |
| CSI 500 | [Two Survivors, Two Different Crowns](en/season_csi500_m3.md) | A meerkat-10, +0.42% | A sloth-2, +7.91% |
| CSI 800 | [Rabbit Crown, Eagle Month](en/season_csi800_m3.md) | E eagle-5-1, +1.86% | B rabbit-2, +10.83% |
| CSI 1000 | [Eagle Rally, Sloth Lead](en/season_csi1000_m3.md) | B eagle-5-1, +6.18% | A sloth-2, +14.74% |

