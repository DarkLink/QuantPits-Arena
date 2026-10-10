# QuantPits Arena | Empirical Strategy Testbed & Benchmark Zoo

> An empirical research testbed comparing anonymous quantitative contestants under shared execution rules, normalized NAV accounting and matched random-ranking controls.

[![Python](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Live Arena](https://img.shields.io/badge/Live%20Arena-arena.quantpits.com-success.svg)](https://arena.quantpits.com/)

## Current Repository Snapshot

The bundled data cover **2026-07-03 through 2026-10-09** across five parallel testbeds. Each contains **64 evaluated market sessions plus one initial NAV anchor**, for **65 NAV observations**. Every path starts at NAV **1.0000**.

Each testbed evaluates **6 anonymous contestants × 28 animal handlers = 168 contestant paths**, alongside two portfolio benchmarks. Its null court contains **11 matching specifications × 1,000 monkey paths**; the five testbeds together contain **55,000 configured control paths**.

| Testbed | Cumulative leader at October 9 | Final NAV | Cumulative return | Latest dispatch |
| :--- | :--- | ---: | ---: | :--- |
| csirun300 subset (246 stocks) | CONTESTANT_B_eagle-5-1 | 1.2240 | +22.40% | [Episode 14: The Same Holdings, a Wider Crown](chronicles/en/episode_14_the_two_day_return.md) |
| CSI 300 full universe (300 stocks) | CONTESTANT_D_rabbit-1 | 1.1886 | +18.86% | [M3: Rabbit Crown, Eagle Month](chronicles/en/season_csi300_m3.md) |
| CSI 500 | CONTESTANT_B_eagle-5-1 | 1.0885 | +8.85% | [M3: Two Survivors, Two Different Crowns](chronicles/en/season_csi500_m3.md) |
| CSI 800 | CONTESTANT_B_rabbit-2 | 1.1172 | +11.72% | [M3: Rabbit Crown, Eagle Month](chronicles/en/season_csi800_m3.md) |
| CSI 1000 | CONTESTANT_B_eagle-5-1 | 1.1349 | +13.49% | [M3: Eagle Rally, Sloth Lead](chronicles/en/season_csi1000_m3.md) |

These are cumulative standings in the repository snapshot. A monthly or two-day winner can differ from the cumulative leader; the figures do not establish durable forecasting skill.

The flagship's [Episode 13](chronicles/en/episode_13_the_three_day_trial.md) covers September 28–30, and [Episode 14](chronicles/en/episode_14_the_two_day_return.md) covers October 8–9. **September 28 had a rebalance; October 8–9 only valued the same holdings, with zero new trades.** Separate dispatches and settlements do not imply separate rebalances.

The full CSI 300, CSI 500, CSI 800 and CSI 1000 testbeds each have an independent M3 report. Their September body uses August 28 close as the return anchor and September 30 as the cutoff; October 8–9 appears in a separate appendix. The full dispatch index is in [Chronicles](chronicles/README.md).

## Explore the Dashboard

From the repository root:

```bash
python3 -m http.server 8080 --directory web
```

Open `http://localhost:8080`. Use the season selector to switch among the five testbeds, then explore the overview, leaderboard, NAV curves, animal comparisons and dispatches.

The bundled frontend datasets require no model inference or Python analytics stack to browse. The browser loads charting, math-rendering and font assets from external CDNs; completely offline browsing requires local copies of those assets. Interface and data assets use version **6.3** for cache refresh.

## Evaluation Scope and Evidence

- **Common starting point:** historical reputation contributes no weight to Arena rankings. Comparisons use normalized NAV and percentage returns under standardized simulation budgets.
- **Execution constraints:** the portfolio engine applies round-lot constraints, transaction costs, tradability checks, affordability skips and daily marking to market.
- **Matched controls:** random rankings use the corresponding portfolio specification. Cumulative null results must be matched to the same pool and cutoff date; they are not automatically monthly or two-day tests.
- **Statistical limits:** upper-tail empirical probabilities use finite-sample plus-one correction. Winner selection, multiple comparisons and differences in entry exposure limit interpretation; a nominal p-value below 0.05 does not certify alpha.
- **Exposure matters:** constrained Taotie can retain substantial cash. Sloth and Snail have different entry histories. Return differences alone do not isolate selection, cash shelter or signal decay.

`season_01` uses **csirun300**, a **246-stock subset of CSI 300**, preserving its existing evaluation history. The new **`season_csi300`** uses **csi300**, the **full 300-stock universe**, with its own predictions, checkpoints, portfolio benchmarks and 11,000 matched controls. Select it in the dashboard or use `?season=csi300`; `?season=csirun300` selects the original subset. Both use the CSI 300 index, while their executable and theoretical portfolios cover their respective pools.

The full CSI 300 history was reconstructed on **2026-10-10**, from the common July 3 anchor through October 9. Its M1–M2 and M3 reports are retrospective; filling historical data does not constitute a prospective commitment. Other testbeds' July–August baseline was also simulated retrospectively. Later dispatches continue the existing evaluation; a completed report alone does not establish a verifiable pre-market commitment.

The full CSI 300 definition has 300 constituents, but one has no supplied local market rows after September 14. All six contestants therefore have 299 scored names thereafter. Missing quotes prevent trading; existing holdings use the last available price. This data limitation is recorded in the season and its M3 report.

### The 28-Animal Zoo

| Family | Handlers | Execution rule |
| :--- | :--- | :--- |
| Baseline | Robot | TopK=22, DropN=3 |
| Cold-start signal delay | Sloth 1–4 | Begin in cash, then use signals delayed by 1–4 evaluation cycles |
| Warm-start signal delay | Snail 1–4 | Enter with the initial signal, then use delayed signals after the entry phase |
| Turnover | Turtle, Rabbit 1–2 | DropN=1, 11 or 22 with TopK=22 |
| Polarity | Koala | Invert the ranking |
| Rank geometry | Meerkat 10–90 | Nine ranking bands with the canonical portfolio policy |
| Concentration and breadth | Eagle suite | TopK/DropN: 5/1, 11/2, 44/6, 66/9, 88/12 |
| Broad selection | Whale Shark | TopK=123, DropN=17 |

The independent **Taotie** and **Ghost Taotie** portfolios sit outside the 28 contestant handlers. Taotie is the executable universe reference; Ghost is the theoretical broad-exposure reference. Each testbed also has its corresponding external market index and matched monkey distributions. **The Rock** is a separate simplicity reference, not another contestant path.

## Maintainer Operations and Holiday Alignment

**Holiday updates follow the maintainer's explicit notification.** The maintainer determines when to update and supplies any holiday execution arrangement needed to stay as close as possible to live trading. New market data, a report boundary or a nominal weekly date does not by itself authorize an advance, makeup trade or change to the execution schedule.

The current implementation rebalances at Monday open and skips rebalancing when Monday is closed. This matches the recorded September 28–October 9 run. Future holiday exceptions must follow the maintainer's supplied schedule and be supported by the calendar and execution workflow before advancing; they must not be inferred from this single holiday example. Alignment concerns decision cutoffs, execution dates and accounting conventions, while public outputs remain anonymous and normalized.

After an update and target cutoff have been authorized, use the prepared execution environment:

```bash
conda activate qlib_cupy

# Replace the cutoff with the maintainer-specified date.
TARGET_DATE=2026-10-09

# Extend only missing prediction dates; preserve existing history.
for universe in csirun300 csi300 csi500 csi800 csi1000; do
    python cli.py infer-update --universe "$universe" --end-date "$TARGET_DATE" || exit 1
done

# Native roll-forward: configuration -> incremental settlement ->
# matched controls -> frontend export -> English dispatch sync -> privacy audit.
python cli.py rollforward --end-date "$TARGET_DATE"
```

`rollforward` advances **one settlement segment per selected season per invocation**. When catching up across several segments, use their authorized settlement cutoffs in order. Verify actual NAV end dates and checkpoint progress rather than relying on the configured horizon. Preserve historical NAV and prediction prefixes; routine maintenance uses the existing checkpoints.

Full five-pool monkey evaluation can take longer than the earlier two-to-three-minute estimate. Use an explicit timeout and monitor progress. The legacy `scripts/infer_all_contestants.py` has a fixed historical cutoff; `infer-update` is the current incremental entry point.

See the [Roll-Forward SOP](docs/SEASON_ROLLFORWARD_SOP.md), [Holiday Execution Review](docs/HOLIDAY_REBALANCE_REVIEW.md) and [Agent Instructions](AGENTS.md) for operational details.

## Local Execution and Repository Layout

The repository provides the execution engine, animal policies, null controls, export tooling and precompiled frontend data. Running a new tournament additionally requires local market data, private model assets and a configured execution environment. Production order routing and brokerage connectivity belong to the live system.

```text
arena/                  Calendar, execution, inference, controls and exporters
cli.py                  Native inference and roll-forward commands
seasons/                Declarative testbed configurations
manifests/public/       Anonymous public contestant descriptions
manifests/private/      Local private mappings, ignored by Git
artifacts/              Local assets and prediction caches, ignored by Git
runs/                   Local checkpoints and generated evaluation outputs
chronicles/en/          Public English dispatch sources
chronicles/zh/          Local Chinese chronicles
web/                    Dashboard, five season datasets and English dispatch copies
scripts/                Privacy audit and maintenance utilities
tests/                  Calendar, execution, controls and automation regressions
```

Public files contain anonymous contestant identities and relative repository paths. Private assets and serialized state stay outside Git tracking.

## Verification

For changes to execution or maintenance automation:

```bash
PYTHONPATH=. pytest
python3 scripts/audit_privacy.py
```

For documentation changes, verify dates, figures and links against the current repository exports, then run the privacy audit. The full CSI 300 addition passed **92 regression tests**. Validation also includes five-season frontend rendering checks, preserved historical NAV and private-cache checks, and date-matched significance checks.

## Disclaimer

For research, educational and informational purposes only. The Arena evaluates research candidates under declared simulation and execution assumptions; it does not provide investment recommendations. Historical and simulated results do not establish future performance. Interpret every result within its stated window, exposure and statistical limits.

See the [Research & Legal Disclaimer](https://arena.quantpits.com/#disclaimer) for the full disclosure.

## License

MIT License. Copyright (c) QuantPits Research.
