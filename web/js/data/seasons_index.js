window.ARENA_SEASONS_INDEX = [
  {
    id: "season_01",
    title: "Season 1: csirun300 Subset",
    short_title: "S1 · csirun300 (246)",
    status: "ACTIVE",
    badge_type: "active",
    period: "2026.07 - 2026.10",
    anchor_date: "2026-07-03",
    end_date: "2026-10-09",
    trading_days: 65,
    contestants_count: 6,
    animals_count: 28,
    benchmarks: ["CSI300", "Taotie", "11 × 1,000 Matched Monkeys"],
    description: "246-stock csirun300 subset of CSI 300: 6 anonymous contestants × 28 handlers. Separate from the full CSI 300 season.",
    dispatches_banner: {
      tag: "🎙️ Season 1 Dispatches",
      title: "Episodes 13–14 available: The Three-Day Trial & The Two-Day Return. Updated through October 9.",
      link: "#dispatches?episode=ep14",
      link_text: "Read S1 Dispatches &rarr;"
    },
    methodology: {
      framework_name: "Empirical Strategy Testbed & Historical Reconstruction",
      anchor_spec: "Single-Anchor Common Prospective Baseline (2026-07-03)",
      capital_spec: "Standardized simulation budget with strict 100-share round-lot constraints",
      benchmarks_summary: "Tripartite Reference System: CSI 300 (Market Beta) + Taotie (Executable Universe) + Matched Monkeys (Statistical Null)",
      execution_flow: "Monday Open Rebalance; Holiday Mondays Skip Trading; Daily Valuation"
    }
  },
  {
    "id": "season_csi300",
    "title": "CSI 300 Full-Universe Arena",
    "short_title": "CSI 300 Full (300)",
    "status": "ACTIVE",
    "badge_type": "active",
    "period": "2026.07 - 2026.10",
    "anchor_date": "2026-07-03",
    "end_date": "2026-10-09",
    "trading_days": 65,
    "contestants_count": 6,
    "animals_count": 28,
    "benchmarks": [
      "CSI 300",
      "Taotie (csi300)",
      "Ghost Taotie (csi300)",
      "11 Matched Specifications / 11,000 Monkeys"
    ],
    "description": "Retrospective full 300-stock CSI 300 evaluation, independent of the 246-stock csirun300 subset. Separate predictions, checkpoints and matched controls.",
    "dispatches_banner": {
      "tag": "🔬 CSI 300 Full-Universe Dispatches",
      "title": "Independent M1–M2 and M3 reports; October 8–9 valuation appendix through October 9.",
      "link": "#dispatches?episode=csi300_m3",
      "link_text": "Read CSI 300 Full-Pool Dispatches &rarr;"
    },
    "methodology": {
      "framework_name": "CSI 300 Full Universe (300 Stocks) Empirical Evaluation",
      "anchor_spec": "Retrospective Common Anchor (2026-07-03)",
      "capital_spec": "Standardized simulation budget with 100-share trading lots; normalized NAV",
      "benchmarks_summary": "Market Index (CSI 300) + Taotie + Ghost Taotie + 11 matching groups of 1,000 monkeys",
      "execution_flow": "Monday Open Rebalance; Holiday Mondays Skip Trading; Daily Valuation"
    }
  },
  {
    id: "season_csi500",
    title: "Tech Preview: CSI 500 Mid-Cap Arena",
    short_title: "CSI 500 (Tech Preview)",
    status: "PREVIEW",
    badge_type: "preview",
    period: "2026.07 - 2026.10",
    anchor_date: "2026-07-03",
    end_date: "2026-10-09",
    trading_days: 65,
    contestants_count: 6,
    animals_count: 28,
    benchmarks: [
      "CSI 500",
      "Taotie 500",
      "Ghost Taotie 500",
      "11 × 1,000 Matched Monkeys"
    ],
    description: "CSI 500 mid-cap universe testbed (SH000905 benchmark) evaluating the 6 candidate models across 28 execution containers.",
    dispatches_banner: {
      tag: "🔬 CSI 500 Tech Preview",
      title: "CSI 500 M3: Two Survivors, Two Different Crowns. October valuation appendix included.",
      link: "#dispatches?episode=csi500_m3",
      link_text: "Read CSI 500 Dispatches &rarr;"
    },
    methodology: {
      framework_name: "CSI 500 Mid-Cap Empirical Evaluation",
      anchor_spec: "Parallel Calibration Anchor (2026-07-03 Initiation)",
      capital_spec: "Standardized simulation budget with 100-share trading lots over the CSI 500 universe",
      benchmarks_summary: "CSI 500 Index + Taotie 500 + Ghost Taotie 500 + 11 matching groups of 1,000 monkeys",
      execution_flow: "Monday Open Rebalance; Holiday Mondays Skip Trading; Daily Valuation"
    }
  },
  {
    id: "season_csi800",
    title: "Tech Preview: CSI 800 Broad-Cap Arena",
    short_title: "CSI 800 (Tech Preview)",
    status: "PREVIEW",
    badge_type: "preview",
    period: "2026.07 - 2026.10",
    anchor_date: "2026-07-03",
    end_date: "2026-10-09",
    trading_days: 65,
    contestants_count: 6,
    animals_count: 28,
    benchmarks: [
      "CSI 800",
      "Taotie 800",
      "Ghost Taotie 800",
      "11 × 1,000 Matched Monkeys"
    ],
    description: "CSI 800 broad-cap universe benchmark: evaluating the 6 Alpha candidate models and 28 execution containers against CSI 800 (SH000906) benchmark.",
    dispatches_banner: {
      tag: "🔬 CSI 800 Tech Preview",
      title: "CSI 800 M3: Rabbit Crown, Eagle Month. October valuation appendix included.",
      link: "#dispatches?episode=csi800_m3",
      link_text: "Read CSI 800 Dispatches &rarr;"
    },
    methodology: {
      framework_name: "CSI 800 Universe (~800 Stocks) Empirical Evaluation",
      anchor_spec: "Parallel Calibration Anchor (2026-07-03 Initiation)",
      capital_spec: "Standardized simulation budget with 100-share trading lots over the CSI 800 universe",
      benchmarks_summary: "CSI 800 Index + Taotie + Ghost Taotie + 11 matching groups of 1,000 monkeys",
      execution_flow: "Monday Open Rebalance; Holiday Mondays Skip Trading; Daily Valuation"
    }
  },
  {
    id: "season_csi1000",
    title: "Tech Preview: CSI 1000 Small-Cap Arena",
    short_title: "CSI 1000 (Tech Preview)",
    status: "PREVIEW",
    badge_type: "preview",
    period: "2026.07 - 2026.10",
    anchor_date: "2026-07-03",
    end_date: "2026-10-09",
    trading_days: 65,
    contestants_count: 6,
    animals_count: 28,
    benchmarks: ["CSI 1000", "Taotie 1000", "Ghost Taotie 1000", "11 × 1,000 Matched Monkeys"],
    description: "CSI 1000 small-cap universe testbed (SH000852 benchmark) evaluating the 6 candidate models across 28 execution containers.",
    dispatches_banner: {
      tag: "🔬 CSI 1000 Tech Preview",
      title: "CSI 1000 M3: Eagle Rally, Sloth Lead. October valuation appendix included.",
      link: "#dispatches?episode=csi1000_m3",
      link_text: "Read CSI 1000 Chronicles &rarr;"
    },
    methodology: {
      framework_name: "Small-Cap Breadth Empirical Evaluation & Liquidity Frictions",
      anchor_spec: "Parallel Calibration Anchor (2026-07-03 Initiation)",
      capital_spec: "Standardized simulation budget with 100-share trading lots over the CSI 1000 universe",
      benchmarks_summary: "CSI 1000 Index + Taotie 1000 + Ghost Taotie 1000 + 11 matching groups of 1,000 monkeys",
      execution_flow: "Monday Open Rebalance; Holiday Mondays Skip Trading; Daily Valuation"
    }
  }
];
