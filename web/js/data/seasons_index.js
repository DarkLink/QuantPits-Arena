window.ARENA_SEASONS_INDEX = [
  {
    id: "season_01",
    title: "Season 1: Graveyard Arena",
    short_title: "Season 1",
    status: "ACTIVE",
    badge_type: "active",
    period: "2026.07 - 2026.09",
    anchor_date: "2026-07-03",
    end_date: "2026-09-11",
    trading_days: 51,
    contestants_count: 6,
    animals_count: 29,
    benchmarks: ["CSI300", "Taotie (500k)", "1100 Monkeys"],
    description: "6 Model Candidates × 29 Animal Handlers with empirical Monkey null distributions.",
    dispatches_banner: {
      tag: "🎙️ Season 1 Dispatches",
      title: "Episode 10 Released (\"The Apex Strike & The 1.20 Milestone\"). Week 10 evaluation active.",
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
    id: "season_csi500",
    title: "Tech Preview: CSI 500 Mid-Cap Arena",
    short_title: "CSI 500 (Tech Preview)",
    status: "PREVIEW",
    badge_type: "preview",
    period: "2026.07 - 2026.09",
    anchor_date: "2026-07-03",
    end_date: "2026-09-11",
    trading_days: 51,
    contestants_count: 6,
    animals_count: 28,
    benchmarks: [
      "CSI 500",
      "Taotie 500 (1M)",
      "Ghost Taotie 500 (100M)",
      "1,000 Monkeys"
    ],
    description: "CSI 500 mid-cap universe testbed (SH000905 benchmark) evaluating the 6 candidate models across 28 execution containers.",
    dispatches_banner: {
      tag: "🔬 CSI 500 Tech Preview",
      title: "CSI 500 Mid-Cap Calibration Active: Evaluating Alpha Breadth in Liquid Mid-Caps.",
      link: "#dispatches",
      link_text: "Read CSI 500 Dispatches &rarr;"
    },
    methodology: {
      framework_name: "CSI 500 Mid-Cap Empirical Evaluation",
      anchor_spec: "Parallel Calibration Anchor (2026-07-03 Initiation)",
      capital_spec: "CNY 500,000 baseline cash with 100-share trading lots over 500 constituent stocks",
      benchmarks_summary: "CSI 500 Tripartite System: CSI 500 Index (SH000905 Beta) + Taotie 500 + Ghost Taotie 500 (100M) + 1,000 Matched Monkeys",
      execution_flow: "Weekly Rebalance, Monday Open Execution, Daily Marked-to-Market"
    }
  },
  {
    id: "season_csi800",
    title: "Tech Preview: CSI 800 Broad-Cap Arena",
    short_title: "CSI 800 (Tech Preview)",
    status: "PREVIEW",
    badge_type: "preview",
    period: "2026.07 - 2026.09",
    anchor_date: "2026-07-03",
    end_date: "2026-09-11",
    trading_days: 51,
    contestants_count: 6,
    animals_count: 28,
    benchmarks: [
      "CSI 800",
      "Taotie 800 (1.6M)",
      "Ghost Taotie 800 (100M)",
      "1,000 Monkeys"
    ],
    description: "CSI 800 broad-cap universe benchmark: evaluating the 6 Alpha candidate models and 28 execution containers against CSI 800 (SH000906) benchmark.",
    dispatches_banner: {
      tag: "🔬 CSI 800 Tech Preview",
      title: "CSI 800 Broad-Cap Calibration Active: Broad-market coverage and execution dynamics.",
      link: "#dispatches",
      link_text: "Read CSI 800 Dispatches &rarr;"
    },
    methodology: {
      framework_name: "CSI 800 Universe (~800 Stocks) Empirical Evaluation",
      anchor_spec: "Parallel Calibration Anchor (2026-07-03 Initiation)",
      capital_spec: "CNY 500,000 baseline capital with 100-share trading lots",
      benchmarks_summary: "Market Index (CSI 800) + Taotie + Ghost Taotie (100M) + 1,000 Matched Monkeys",
      execution_flow: "Weekly Rebalance, Monday Open Execution, Daily Marked-to-Market"
    }
  },
  {
    id: "season_csi1000",
    title: "Tech Preview: CSI 1000 Small-Cap Arena",
    short_title: "CSI 1000 (Tech Preview)",
    status: "PREVIEW",
    badge_type: "preview",
    period: "2026.07 - 2026.09",
    anchor_date: "2026-07-03",
    end_date: "2026-09-11",
    trading_days: 51,
    contestants_count: 6,
    animals_count: 28,
    benchmarks: ["CSI 1000", "Taotie 1000 (2M)", "Ghost Taotie 1000 (100M)", "1000 Monkeys"],
    description: "CSI 1000 small-cap universe testbed (SH000852 benchmark) evaluating the 6 candidate models across 28 execution containers.",
    dispatches_banner: {
      tag: "🔬 CSI 1000 Tech Preview",
      title: "CSI 1000 Small-Cap Calibration Active: Comparing Alpha Breadth vs. Liquidity Constraints.",
      link: "#dispatches",
      link_text: "Read CSI 1000 Chronicles &rarr;"
    },
    methodology: {
      framework_name: "Small-Cap Breadth Empirical Evaluation & Liquidity Frictions",
      anchor_spec: "Parallel Calibration Anchor (2026-07-03 Initiation)",
      capital_spec: "CNY 500,000 baseline cash with 100-share trading lots over 1,000 constituent stocks",
      benchmarks_summary: "CSI 1000 Tripartite System: CSI 1000 Index (SH000852 Beta) + Taotie 1000 + Ghost Taotie 1000 (100M) + 1,000 Matched Monkeys",
      execution_flow: "Weekly Rebalance, Monday Open Execution, Daily Marked-to-Market"
    }
  }
];

window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};
