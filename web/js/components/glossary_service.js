/**
 * web/js/components/glossary_service.js
 * ====================================
 * Dynamic Season-Aware Glossary & Specification Service
 * Synthesizes definitions and plain-English tooltips directly from the active season's adapter.
 * Supports:
 *   - Dynamic Model Candidates (Contestants)
 *   - Dynamic Execution Zoo Handlers (Animals)
 *   - Dynamic Tripartite Benchmarks (Market, Taotie, Ghost Taotie, Monkeys)
 *   - Universal Quantitative & Tournament Metrics
 */

window.ArenaGlossaryService = {
  // Static dictionary for universal quant metrics & tournament mechanics
  coreMetrics: {
    "nav": {
      id: "nav",
      term: "NAV",
      name: "Normalized Net Asset Value (NAV)",
      category: "Metrics",
      tagline: "Standardized Wealth Index",
      tooltip: "Cumulative portfolio wealth starting strictly at 1.0000 on common inception date (2026-07-03). Eliminates real-money cash differences for apples-to-apples comparison.",
      details: "In QuantPits Arena, all strategy variants, benchmark indices, and monkey controls begin at exactly NAV = 1.0000. Subsequent daily marked-to-market valuations track compounding value net of trading commissions, slippage, and stamp taxes."
    },
    "total_return_pct": {
      id: "total_return_pct",
      term: "Return",
      name: "Total Cumulative Return (%)",
      category: "Metrics",
      tagline: "Out-of-Sample Performance",
      tooltip: "Total percentage gain or loss over the evaluation window: (Current NAV - 1.0000) × 100%.",
      details: "Measures overall economic payoff across the evaluation period under strict execution constraints and round lots."
    },
    "sharpe_ratio": {
      id: "sharpe_ratio",
      term: "Sharpe Ratio",
      name: "Annualized Sharpe Ratio",
      category: "Metrics",
      tagline: "Risk-Adjusted Return",
      tooltip: "Risk-adjusted return ratio: (Annualized Return - Risk-Free Rate) / Annualized Volatility. Higher is better (>1.0 is solid, >2.0 is elite in short windows).",
      details: "Calculated from daily return time series annualized by √244. Evaluates whether returns stem from consistent excess alpha or erratic volatility bursts."
    },
    "max_drawdown_pct": {
      id: "max_drawdown_pct",
      term: "Max Drawdown",
      name: "Maximum Drawdown (MDD)",
      category: "Metrics",
      tagline: "Peak-to-Trough Pain",
      tooltip: "The largest percentage drop from a historical portfolio peak to a subsequent trough. Measures worst-case loss risk.",
      details: "Indicates the maximum capital decline an investor would have endured during the tournament."
    },
    "empirical_p_value": {
      id: "empirical_p_value",
      term: "p-value",
      name: "Empirical p-value (vs Matched Monkeys)",
      category: "Metrics",
      tagline: "Statistical Significance",
      tooltip: "The empirical probability that a pure random monkey strategy could match or exceed this performance. p < 0.05 indicates statistical significance.",
      details: "Computed via finite-sample plus-one correction against 1,000 deterministic pseudo-random monkeys sharing identical portfolio rules: p = (Count_beaten + 1) / (1,000 + 1). p < 0.05 represents statistical dismissal of pure luck."
    },
    "monkey_percentile": {
      id: "monkey_percentile",
      term: "Monkey %ile",
      name: "Matched Monkey Null Percentile",
      category: "Metrics",
      tagline: "Ranking Against Pure Luck",
      tooltip: "Percentage of matched random monkeys this strategy outperforms (0% ~ 100%). >95.0% means it beats 95% of random portfolios.",
      details: "Directly evaluates whether model ranking skill extracts genuine alpha above the statistical null colony. Computed per animal rule container."
    },
    "topk": {
      id: "topk",
      term: "TopK",
      name: "Holding Capacity (TopK)",
      category: "Zoo Mechanics",
      tagline: "Portfolio Breadth",
      tooltip: "The target number of assets held simultaneously in the portfolio (e.g., TopK=22 holds 22 stocks).",
      details: "Lower TopK (e.g. 5) implies extreme concentration and higher single-stock risk; higher TopK (e.g. 88) demands broader alpha breadth across equities."
    },
    "dropn": {
      id: "dropn",
      term: "DropN",
      name: "Turnover Capacity (DropN)",
      category: "Zoo Mechanics",
      tagline: "Weekly Rebalance Bandwidth",
      tooltip: "Number of worst-ranked positions forcefully liquidated and replaced each weekly rebalancing cycle.",
      details: "Governs portfolio agility vs. trading friction. High DropN flushes out stale ranks faster at the expense of higher commissions and market impact."
    },
    "waterfall_allocation": {
      id: "waterfall_allocation",
      term: "Waterfall Allocation",
      name: "Greedy Waterfall Capital Allocation",
      category: "Zoo Mechanics",
      tagline: "Discrete Lot Packing",
      tooltip: "An integer-programming allocation algorithm that purchases constituent stocks in 100-share round lots, distributing available capital until cash is fully utilized.",
      details: "Simulates realistic retail execution constraints where small portfolios cannot buy fractional shares, leaving fractional cash drag."
    }
  },

  // Synthesize comprehensive season-aware dictionary
  getDictionary() {
    const adapter = window.arenaAdapter;
    const seasonMeta = adapter ? adapter.getCurrentSeasonMeta() : {};
    const dict = {
      contestants: {},
      animals: {},
      benchmarks: {},
      metrics: { ...this.coreMetrics }
    };

    // 1. Dynamic Contestants from active season adapter
    const contestants = adapter ? adapter.getAllContestants() : [];
    const contestantArchetypes = {
      "CONTESTANT_A": { archetype: "Multi-Factor Ensemble", tagline: "The Expert Committee", desc: "A multi-factor ensemble integrating diverse cross-sectional features. Designed like an investment committee to deliver broad market coverage and strong resilience against single-factor failure." },
      "CONTESTANT_B": { archetype: "Cross-Validation Ensemble", tagline: "The High-Conviction Hunter", desc: "A time-series cross-validation ensemble with extreme conviction in top-tier assets. Displays explosive upside velocity in concentrated, high-intensity portfolios (e.g. Eagle)." },
      "CONTESTANT_C": { archetype: "Multi-Factor Ensemble", tagline: "The Momentum Sprinter", desc: "An early baseline ensemble with elevated sensitivity to short-term price-volume momentum and rapid cross-sectional sector rotations." },
      "CONTESTANT_D": { archetype: "Multi-Factor Ensemble", tagline: "The Resilient Marathoner", desc: "A multi-factor model engineered for low factor correlation and turnover tolerance. Demonstrates remarkable structural consistency and parameter invariance across diverse execution containers." },
      "CONTESTANT_E": { archetype: "High-Dimensional Single Model (52-dim)", tagline: "The Complex Non-Linear Explorer", desc: "A single deep/statistical model trained on an expanded 52-dimensional feature space to probe the capacity limits of complex non-linear factor interactions." },
      "CONTESTANT_F": { archetype: "Condensed Core Single Model (20-dim)", tagline: "The Minimalist Benchmark", desc: "A compact single model relying on just 20 classic, economically intuitive factors. Highly resistant to overfitting, validating the 'less is more' principle." }
    };

    contestants.forEach(c => {
      const cid = c.id || c.contestant_id;
      const staticMeta = contestantArchetypes[cid] || {
        archetype: c.training_mode || "Quantitative Model Candidate",
        tagline: c.historical_role || "Tournament Contestant",
        desc: `Anonymized tournament candidate model evaluated under ${seasonMeta.short_title || "Arena"}.`
      };
      dict.contestants[cid] = {
        id: cid,
        term: cid,
        name: c.display_name || cid,
        category: "Contestants",
        tagline: staticMeta.tagline,
        tooltip: `【${staticMeta.tagline}】${staticMeta.desc}`,
        details: `Architectural Archetype: ${staticMeta.archetype}. Evaluated on ${seasonMeta.title || "Arena Baseline"} across all 28 animal containers.`
      };
    });

    // 2. Dynamic Animals from active season adapter
    const animals = adapter ? adapter.getAllAnimals() : [];
    animals.forEach(a => {
      const aid = a.id;
      dict.animals[aid] = {
        id: aid,
        term: aid,
        name: a.name || aid,
        category: a.category || "Zoo Animals",
        tagline: a.badge || "Execution Policy",
        tooltip: `【${a.badge || a.category}】${a.description || "Simulated execution policy."}`,
        details: `TopK: ${a.topk} holdings | DropN: ${a.n_drop} weekly turnover | Spec: ${a.spec}. Simulates controlled behavioral friction.`
      };
    });

    // Also add umbrella animal keywords for general terms in text
    dict.animals["sloth"] = {
      id: "sloth",
      term: "Sloth",
      name: "Sloth Cohort (Execution Latency)",
      category: "Zoo Animals",
      tagline: "Signal Half-Life Test",
      tooltip: "【Signal Latency Test】Delays buying recommended stocks by 1 to 4 weeks while holding uninvested cash. Evaluates alpha persistence and half-life decay.",
      details: "Includes Sloth-1 (1-week lag), Sloth-2 (2-week lag), Sloth-3 (3-week lag), and Sloth-4 (1-month lag)."
    };
    dict.animals["snail"] = {
      id: "snail",
      term: "Snail",
      name: "Snail Cohort (Stale Holding)",
      category: "Zoo Animals",
      tagline: "Exit Inertia Test",
      tooltip: "【Exit Hesitation Test】Keeps dropped/downgraded stocks for 1 to 4 extra weeks before selling. Measures portfolio drag from reluctant selling.",
      details: "Includes Snail-1, Snail-2, Snail-3, and Snail-4 with incremental liquidation delays."
    };
    dict.animals["rabbit"] = {
      id: "rabbit",
      term: "Rabbit",
      name: "Rabbit Cohort (High Turnover)",
      category: "Zoo Animals",
      tagline: "Agile Sector Rotator",
      tooltip: "【High Turnover Bandwidth】Rotates 50% (Rabbit-1) or 100% (Rabbit-2) of holdings every week, testing if fresh signals outearn transaction costs.",
      details: "Rabbit-1 flushes 11 positions weekly; Rabbit-2 executes complete weekly liquidation (22 positions)."
    };
    dict.animals["eagle"] = {
      id: "eagle",
      term: "Eagle",
      name: "Eagle Cohort (Conviction & Capacity)",
      category: "Zoo Animals",
      tagline: "Precision & Capacity Scaling",
      tooltip: "【Conviction & Capacity】Ranges from ultra-concentrated snipers (Eagle-5/1: Top 5 stocks) to institutional capacity tests (Eagle-44, 66, 88).",
      details: "Eagle-5/1 exerts the highest selection intensity in the tournament; expanded Eagles test capital scalability."
    };
    dict.animals["koala"] = {
      id: "koala",
      term: "Koala",
      name: "Koala (Inverted Polarity)",
      category: "Zoo Animals",
      tagline: "Falsification Test",
      tooltip: "【Scientific Falsification Test】Intentionally buys the bottom 22 lowest-scoring stocks. If a model has true predictive alpha, Koala must lose heavily.",
      details: "A critical sanity check. Positive returns in Koala reveal inverse signal ranking or spurious factor loadings."
    };
    dict.animals["meerkat"] = {
      id: "meerkat",
      term: "Meerkat",
      name: "Meerkat Decile Cohort",
      category: "Zoo Animals",
      tagline: "Cross-Sectional CT Scan",
      tooltip: "【Monotonicity CT Scan】Slices model rankings into 10%~90% deciles (Meerkat-10 to Meerkat-90). Verifies clean monotonic return decay from top to bottom.",
      details: "Confirms that performance stems from broad ranking skill rather than isolated luck in the extreme tails."
    };

    // 3. Dynamic Benchmarks from active season adapter
    const mktName = adapter ? adapter.getMarketBenchmarkName() : "Market Benchmark";
    const mktCode = adapter ? adapter.getMarketBenchmarkCode() : "SH000300";
    const taotieName = adapter ? adapter.getTaotieDisplayName() : "Taotie";
    const taotieShort = adapter ? adapter.getTaotieShortName() : "Taotie";
    const hasGhost = adapter ? adapter.hasGhostTaotie() : false;

    dict.benchmarks["market"] = {
      id: "market",
      term: mktName,
      name: `${mktName} (${mktCode})`,
      category: "Benchmarks",
      tagline: "External Market Beta Anchor",
      tooltip: `【The Macro Thermometer】Official capitalization-weighted index (${mktCode}). Measures broad macroeconomic trends to isolate market beta from model selection skill.`,
      details: `Represents the external market environment for ${seasonMeta.title || "the tournament"}. Outperforming it indicates positive market-relative spread.`
    };
    dict.benchmarks["csi300"] = dict.benchmarks["market"];

    dict.benchmarks["taotie"] = {
      id: "taotie",
      term: "Taotie",
      name: `${taotieName} (Physical Benchmark)`,
      category: "Benchmarks",
      tagline: "Executable Universe Baseline",
      tooltip: `【The Real-World Floor】Capital-constrained full-universe portfolio with strict 100-share round lots and retail cash constraints. Reflects the true unselected market floor.`,
      details: `Operates under identical capital (${seasonMeta.methodology?.capital_spec || 'CNY 500k'}) and lot constraints as contestant portfolios via greedy waterfall allocation.`
    };

    if (hasGhost) {
      dict.benchmarks["ghost_taotie"] = {
        id: "ghost_taotie",
        term: "Ghost Taotie",
        name: "Ghost Taotie (Theoretical Equal-Weight)",
        category: "Benchmarks",
        tagline: "Frictionless Mathematical Ideal",
        tooltip: "【The Frictionless Utopia】Theoretical 100M portfolio buying all stocks with zero lot exclusions and zero cash drag. Measures how much alpha real frictions devour.",
        details: "Eliminates discrete retail lot frictions to measure the theoretical pure equal-weighted universe drift."
      };
    }

    dict.benchmarks["monkeys"] = {
      id: "monkeys",
      term: "Matched Monkeys",
      name: "Matched Monkeys (Statistical Null Colony)",
      category: "Benchmarks",
      tagline: "1,000 Dart-Throwing Monkeys",
      tooltip: "【1,000 Dart-Throwing Monkeys】Deterministic pseudo-random portfolios sharing each animal's exact capital, lot constraints, and turnover rules, but zero model signals.",
      details: "Answers: 'Could 1,000 monkeys achieve this return through pure luck?' Isolates skill from portfolio mechanics."
    };

    dict.benchmarks["null_court"] = {
      id: "null_court",
      term: "Null Court",
      name: "Null Court (Monte Carlo Jurisdiction)",
      category: "Benchmarks",
      tagline: "The Truth Tribunal",
      tooltip: "【Significance Tribunal】Statistical jurisdiction where strategies must outperform at least 95% of their matched random monkeys (p < 0.05) to claim authentic alpha.",
      details: "Standard finite-sample plus-one correction with Bonferroni multiple-testing sensitivity bounds."
    };

    return dict;
  },

  // Lookup single term metadata by key or alias
  lookup(key) {
    if (!key) return null;
    const cleanKey = key.trim();
    const dict = this.getDictionary();

    // Direct match across categories
    if (dict.contestants[cleanKey]) return dict.contestants[cleanKey];
    if (dict.animals[cleanKey]) return dict.animals[cleanKey];
    if (dict.benchmarks[cleanKey]) return dict.benchmarks[cleanKey];
    if (dict.metrics[cleanKey]) return dict.metrics[cleanKey];

    // Case-insensitive / prefix matching
    const lower = cleanKey.toLowerCase();
    for (const cat of ["contestants", "animals", "benchmarks", "metrics"]) {
      for (const [k, item] of Object.entries(dict[cat])) {
        if (k.toLowerCase() === lower || item.term.toLowerCase() === lower || item.name.toLowerCase() === lower) {
          return item;
        }
      }
    }

    // Heuristic prefix matching (e.g. eagle-5-1 -> eagle, sloth-2 -> sloth)
    if (lower === "mdd" || lower === "max_drawdown") return dict.metrics["max_drawdown_pct"];
    if (lower === "sharpe") return dict.metrics["sharpe_ratio"];
    if (lower === "p_value" || lower === "p-value") return dict.metrics["empirical_p_value"];
    if (lower === "calmar") return {
      id: "calmar",
      term: "Calmar Ratio",
      name: "Calmar Ratio",
      category: "Metrics",
      tagline: "Return vs Max Drawdown",
      tooltip: "Annualized return divided by maximum drawdown. Measures return earned per unit of peak-to-trough downside risk.",
      details: "A stricter downside risk measure than Sharpe, penalizing deep tail drawdowns."
    };
    if (lower === "market_benchmark") return dict.benchmarks["market"];
    if (lower === "execution_handler") return {
      id: "execution_handler",
      term: "Execution Handler",
      name: "Execution Handler (Animal Policy)",
      category: "Zoo Mechanics",
      tagline: "Behavioral Sandbox Container",
      tooltip: "A simulated portfolio execution policy (one of 28 animals) with distinct holding constraints, rebalancing frequency, and trading frictions.",
      details: "Stress-tests strategy signals across execution delay, turnover intensity, concentration, and polarity."
    };

    if (lower.startsWith("contestant_")) {
      const base = cleanKey.toUpperCase().split("_").slice(0, 2).join("_");
      if (dict.contestants[base]) return dict.contestants[base];
    }
    if (lower.includes("taotie")) {
      if (lower.includes("ghost")) return dict.benchmarks["ghost_taotie"] || dict.benchmarks["taotie"];
      return dict.benchmarks["taotie"];
    }
    if (lower.includes("monkey")) return dict.benchmarks["monkeys"];
    if (lower.includes("null court") || lower.includes("court")) return dict.benchmarks["null_court"];
    if (lower.includes("sloth")) return dict.animals[cleanKey] || dict.animals["sloth"];
    if (lower.includes("snail")) return dict.animals[cleanKey] || dict.animals["snail"];
    if (lower.includes("rabbit")) return dict.animals[cleanKey] || dict.animals["rabbit"];
    if (lower.includes("eagle")) return dict.animals[cleanKey] || dict.animals["eagle"];
    if (lower.includes("koala")) return dict.animals["koala"];
    if (lower.includes("meerkat")) return dict.animals[cleanKey] || dict.animals["meerkat"];

    return null;
  }
};
