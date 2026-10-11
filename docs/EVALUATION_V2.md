# Repaired daily-bar evaluation

The October 11 repair release rebuilds all five active testbeds through October 9. It uses the actual raw weekly signals preserved in legacy checkpoints, with a separately frozen current market snapshot. The old results, inputs and dispatches are retained locally in ignored evaluation archives. Historical reconstruction does not establish a historical pre-market commitment.

Executions require finite positive same-day quotes. Invalid sells retain their positions; invalid buys are rejected. Valuation may carry the last valid close, with stale-mark counts. Price fields are mapped by name and independently checked against the source before formal evaluation. Pool membership is independent of affordability, and tie/exit ordering is deterministic. Decision-close rankings and policy are frozen; Monday feasibility is evaluated at execution.

All engines share an explicit policy signature, including costs, lots, allocation and profile. Taotie uses the standard account's capital ratio and allocation. Ghost retains costs and lots as a separate capital-granularity scenario; neither baseline is forced to reset all weights each week. Turnover means gross buys plus gross sells over starting assets.

Ten random TopK/DropN specifications contain 100,000 paths each per pool. P_ALL_0 contains one deterministic passive reference and has no p value. The five pools contain 5,000,000 random paths plus five references. Delay, cold/warm starts, inversion and percentile selection remain animal properties. Across specifications, random scores share the existing seeded prefix.

Upper-tail `p=(k+1)/(N+1)` includes ties. Full-precision k, N, p, finite percentile and Monte Carlo intervals are saved. The visible cumulative family has 840 comparisons. Bonferroni and Holm control familywise error under their assumptions; BH and BY report false-discovery adjustments. Strict Bonferroni requires raw p below 0.05/840. At N=100,000, at most four exceedances can pass. This resolution does not establish a precise tail probability or add market observations. Repeated historical cutoff reviews remain descriptive monitoring and do not control all inspected windows or hidden research selection jointly.

The numeric control executor preserves the reference RNG and execution contract, runs bounded batches, persists cash/holdings/cursors, and resumes without resetting global IDs. It is checked against the Python engine on synthetic edge cases and real frozen prices, including every daily NAV. Historical input or policy changes invalidate a continuation. New controls do not retain millions of Python trade logs. Float64 NAV is saved for every valuation session, alongside weekly settlements. Pointwise P05, median and P95 are calculated from the same continuing controls on each day, with a common NAV 1.0000 anchor. The website shows these observed daily curves, including days without a rebalance. They are null distribution ranges, not confidence bands for future returns. Daily monitoring does not jointly correct all inspected dates.

Compact version 3 requires a fresh evaluation when migrating from weekly-only caches. New incremental runs append daily NAV from persisted cash and positions, preserving the historical daily prefix; same-week continuation updates the existing weekly settlement without repeating trades. Weekly and terminal results remain unchanged when only the daily output resolution is upgraded.

Atomic checkpoint writes, exclusive operation locks, staged generations, a publishing journal and retained backups support recovery. The website reads one complete data bundle, switching only after all five pools and controls pass. The Friday disk interface serializes and verifies complete frozen intents. Same-week append and reentry do not repeat fills or fees; multiweek advancement executes all missing cycles before updating visible dates.

The common operation lock also covers publication recovery. Before refresh or rollforward reads live checkpoints, prepared publication journals restore the prior public files and local run directories. A failed replacement after moving the old run is covered by the write-ahead plan. Repeated publication installs exactly one bundle loader.

The release remains **daily-bar research**. Complete verified corporate-action, opening direction-limit and capacity metadata are unavailable. Full-day volume is a retrospective tradability proxy. Factors are not guessed into cash dividends. Verified split and dividend-record/payment accounting has a tested, idempotent API; the strict profile rejects incomplete coverage. Large compact controls currently reject event-ledger operation until that executor is separately validated for events.

Use the prepared research environment, which also needs a C++17 compiler and OpenMP runtime for the compact controls:

```bash
python cli.py refresh --end-date 2026-10-09 --evaluation-id repair_release
```

Refresh stages are `replay`, `verify-inputs`, `pilot`, `formal` and `publish`. The engineering pilot is fixed at 20,000 and the formal count at 100,000 per random specification. Batch files and source signatures allow restart. Do not stop or extend the sample based on observed p values.

Routine authorized updates use native `infer-update` for all five universes, then `rollforward --end-date <cutoff>`. They preserve historical state and signal prefixes, stage the new generation, append compatible controls and update reports. Use `step --no-monkeys` only for isolated local diagnostics; a shared public release requires complete current controls. Model binaries and private replay assets remain ignored.
