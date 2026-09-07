/**
 * web/js/data/seasons_index.js
 * ============================
 * QuantPits-Arena Seasons Global Registry Index
 * Defines all available seasons, their lifecycle states, methodology specifications, and dispatches.
 */

window.ARENA_SEASONS_INDEX = [
  {
    id: "season_01",
    title: "Season 1: Graveyard Arena",
    short_title: "Season 1",
    status: "ACTIVE",
    badge_type: "active",
    period: "2026.07 - 2026.08",
    anchor_date: "2026-07-03",
    end_date: "2026-08-28",
    trading_days: 41,
    contestants_count: 6,
    animals_count: 29,
    benchmarks: ["CSI300", "Taotie (500k)", "1100 Monkeys"],
    description: "6 Model Candidates × 29 Animal Handlers with empirical Monkey null distributions.",
    dispatches_banner: {
      tag: "🎙️ Season 1 Dispatches",
      title: "Episodes 01–08 Released (\"The 41-Day King\", Retrospective Baseline). Week 9 Market Climate active.",
      link: "#dispatches",
      link_text: "Read S1 Dispatches &rarr;"
    },
    methodology: {
      framework_name: "Empirical Strategy Testbed & Historical Reconstruction",
      anchor_spec: "Single-Anchor Common Prospective Baseline (2026-07-03)",
      capital_spec: "CNY 500,000 base capital with strict 100-share round-lot constraint",
      benchmarks_summary: "Tripartite Reference System: CSI 300 (Market Beta) + Taotie (Executable Universe) + Matched Monkeys (Statistical Null)",
      execution_flow: "Weekly Rebalance, Daily Marked-to-Market Valuation"
    }
  },
  {
    id: "season_02",
    title: "Season 2: Next-Gen & Theoretical Benchmarks",
    short_title: "Season 2 (Preview)",
    status: "DRAFT",
    badge_type: "draft",
    period: "2026.09 - 2026.10",
    anchor_date: "2026-09-04",
    end_date: "2026-10-30",
    trading_days: 40,
    contestants_count: 6,
    animals_count: 29,
    benchmarks: ["CSI300", "Taotie (500k)", "Ghost Taotie (100M)", "1100 Monkeys"],
    description: "Next-gen testbed featuring decoupled two-phase timeline and Ghost Taotie theoretical unconstrained universe tracking.",
    dispatches_banner: {
      tag: "⚡ Season 2 Dispatches",
      title: "Season 2 Calibration: Two-Phase Order Commitment & Ghost Taotie (100M) Active.",
      link: "#dispatches",
      link_text: "Explore S2 Chronicles &rarr;"
    },
    methodology: {
      framework_name: "Decoupled Cryptographic Pipeline & Dual-Universe Benchmark Architecture",
      anchor_spec: "Two-Phase Pre-Commitment Epoch (2026-09-04 Initiation)",
      capital_spec: "Dual-Tier Sizing: CNY 500,000 (Executable Contestants) vs. CNY 100,000,000 (Ghost Taotie Theoretical)",
      benchmarks_summary: "Four-Pillar Hierarchy: CSI 300 (Index Beta) + Taotie (Physical Executable) + Ghost Taotie (Theoretical Equal-Weight) + Matched Monkeys (Null Arbiter)",
      execution_flow: "Two-Phase Decoupled Pipeline: Friday Close Order Commitment (SHA-256) &rarr; Monday Open Execution &rarr; Friday Settle"
    }
  }
];

window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};
