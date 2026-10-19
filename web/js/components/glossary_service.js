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
      tooltip: "Cumulative portfolio wealth starting at 1.0000 on the declared observation anchor. Eliminates real-money cash differences for apples-to-apples comparison.",
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
      tooltip: "Daily mean / daily sample standard deviation × √250; short-window descriptive annualization.",
      details: "Daily mean return divided by sample standard deviation, multiplied by √250, with zero risk-free baseline; this short-window annualization is descriptive."
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
      tooltip: "Upper-tail probability under the specified random-ranking control. Raw p < 0.05 is nominal evidence; the declared family correction is assessed separately.",
      details: "Upper-tail p = (k+1)/(N+1), where k counts random returns >= the actual return. Matching uses TopK/DropN only. Raw p < 0.05 is nominal; the declared cumulative family has 840 comparisons."
    },
    "monkey_percentile": {
      id: "monkey_percentile",
      term: "Monkey %ile",
      name: "Matched Monkey Null Percentile",
      category: "Metrics",
      tagline: "Ranking Against Pure Luck",
      tooltip: "Finite-simulation percentile against the matched random-ranking controls over the declared evaluation window.",
      details: "Computed as 100 × count(null return < actual return)/(N+1), using the matched TopK/DropN specification. It describes the specified null comparison and does not establish persistent future alpha."
    },
    "topk": {
      id: "topk",
      term: "TopK",
      name: "Holding Capacity (TopK)",
      category: "Zoo Mechanics",
      tagline: "Portfolio Breadth",
      tooltip: "The target number of holdings. Actual holdings can be lower because of affordability, missing quotes, round lots or other execution constraints.",
      details: "Lower TopK (e.g. 5) implies extreme concentration and higher single-stock risk; higher TopK (e.g. 88) demands broader alpha breadth across equities."
    },
    "dropn": {
      id: "dropn",
      term: "DropN",
      name: "Turnover Capacity (DropN)",
      category: "Zoo Mechanics",
      tagline: "Weekly Rebalance Bandwidth",
      tooltip: "The scheduled replacement budget at each rebalance, not a guaranteed number of completed trades.",
      details: "Actual turnover depends on ranking changes, universe membership and execution constraints. A larger replacement budget can increase trading costs, while an unchanged target can retain existing holdings."
    },
    "waterfall_allocation": {
      id: "waterfall_allocation",
      term: "Waterfall Allocation",
      name: "Greedy Waterfall Capital Allocation",
      category: "Zoo Mechanics",
      tagline: "Discrete Lot Packing",
      tooltip: "An optional greedy mode that attempts additional round-lot purchases using cash left after the initial allocation.",
      details: "This heuristic does not guarantee full investment. Its active setting follows the release execution policy; it is separate from the standard allocation policy and from fractional-share trading."
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
    contestants.forEach(c => {
      const cid = c.id || c.contestant_id;
      const name = c.display_name || cid;
      const anchor = c.observation_start || seasonMeta.anchor_date || adapter.getNavDates()[0];
      const scope = c.observation_start ? 'observation' : 'full-season';
      dict.contestants[cid] = {
        id: cid,
        term: cid,
        name,
        category: 'Contestants',
        tagline: c.observation_start ? 'Observation Participant' : 'Full-season Participant',
        tooltip: `${name} is an anonymous ${scope} participant evaluated in ${seasonMeta.short_title || 'Arena'}.`,
        details: `Observation anchor: ${anchor}. Evaluated in ${seasonMeta.title || 'Arena'} across 28 execution containers. Comparisons use a common observation window.`
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
        details: `TopK target: ${a.topk} holdings | DropN replacement budget: ${a.n_drop} | Spec: ${a.spec}. Actual trades remain subject to execution constraints.`
      };
    });

    // Also add umbrella animal keywords for general terms in text
    dict.animals["sloth"] = {
      id: "sloth",
      term: "Sloth",
      name: "Sloth Cohort (Execution Latency)",
      category: "Zoo Animals",
      tagline: "Signal Delay with Cash Start",
      tooltip: "Starts in cash for 1–4 weekly cycles, then rebalances using rankings delayed by that many cycles.",
      details: "Includes Sloth-1 through Sloth-4. Results combine signal latency with the initial cash-exposure gap and do not isolate pure signal half-life."
    };
    dict.animals["snail"] = {
      id: "snail",
      term: "Snail",
      name: "Snail Cohort (Invested Start)",
      category: "Zoo Animals",
      tagline: "Signal Delay with Invested Start",
      tooltip: "Enters immediately using the initial ranking, reuses that ranking during the transition, then follows rankings delayed by 1–4 weekly cycles.",
      details: "Includes Snail-1 through Snail-4. Orders follow delayed rankings; each position is not assigned a fixed extra holding period. Unlike Sloth, there is no initial cash-only period."
    };
    dict.animals["rabbit"] = {
      id: "rabbit",
      term: "Rabbit",
      name: "Rabbit Cohort (High Turnover)",
      category: "Zoo Animals",
      tagline: "Replacement Budget Stress",
      tooltip: "Targets 22 holdings with replacement budgets of 11 (Rabbit-1) or 22 (Rabbit-2) positions per rebalance.",
      details: "Tests sensitivity to faster rotation and trading costs. These are replacement budgets; unchanged targets and execution constraints can result in fewer trades."
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
    dict.animals["meerkat"] = {
      id: "meerkat",
      term: "Meerkat",
      name: "Meerkat Decile Cohort",
      category: "Zoo Animals",
      tagline: "Cross-Sectional CT Scan",
      tooltip: "Samples holdings around ranking percentiles from 10% through 90% (Meerkat-10 to Meerkat-90), exploring how results vary across ranking regions.",
      details: "Targets 22 holdings around each selected percentile. Nearby selections can overlap; observed monotonicity is descriptive and does not establish causal ranking skill."
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
      tooltip: `Official capitalization-weighted index (${mktCode}) providing external market context. Outperformance alone does not isolate ranking skill.`,
      details: `Represents the external market environment for ${seasonMeta.title || "the tournament"}. Outperforming it indicates positive market-relative spread.`
    };
    dict.benchmarks["csi300"] = dict.benchmarks["market"];

    dict.benchmarks["taotie"] = {
      id: "taotie",
      term: "Taotie",
      name: `${taotieName} (Physical Benchmark)`,
      category: "Benchmarks",
      tagline: "Executable Universe Baseline",
      tooltip: `Capital-constrained full-universe portfolio with round lots and the declared allocation policy. It is an executable reference, not a guaranteed floor for returns.`,
      details: `Operates under identical capital (${seasonMeta.methodology?.capital_spec || 'the standard simulation budget'}) and lot constraints as contestant portfolios using the standard allocation policy, with residual cash preserved.`
    };

    if (hasGhost) {
      dict.benchmarks["ghost_taotie"] = {
        id: "ghost_taotie",
        term: "Ghost Taotie",
        name: "Ghost Taotie (Capital Scenario)",
        category: "Benchmarks",
        tagline: "Capital Granularity Reference",
        tooltip: "Larger standardized capital reduces lot-granularity effects; costs, residual cash and round lots remain.",
        details: "Passive holdings are retained between membership changes; no weekly full equal-weight reset."
      };
    }

    dict.benchmarks["monkeys"] = {
      id: "monkeys",
      term: "Matched Monkeys",
      name: "Matched Monkeys (Statistical Null Colony)",
      category: "Benchmarks",
      tagline: "100,000 Random Controls",
      tooltip: "100,000 deterministic pseudo-random portfolios per random TopK/DropN specification, under the declared capital, lot and cost constraints. Animal-specific ranking transformations and delay rules are not replicated.",
      details: "Answers: 'How unusual is this return under the declared random-ranking baseline?' Delay and initial exposure remain properties of the animal, not new control species."
    };

    dict.benchmarks["null_court"] = {
      id: "null_court",
      term: "Null Court",
      name: "Null Court (Monte Carlo Jurisdiction)",
      category: "Benchmarks",
      tagline: "The Truth Tribunal",
      tooltip: "【Significance Tribunal】Random-ranking diagnostic court. Raw p and family corrections are separate; exploratory results do not establish universal alpha.",
      details: "Standard finite-sample plus-one correction with Bonferroni multiple-testing sensitivity bounds."
    };

    return dict;
  },

  // Lookup single term metadata by key or alias
  lookup(key) {
    if (typeof key !== 'string' || !key.trim()) return null;
    const aliases = {metric_monkey_percentile:'monkey_percentile', whale_shark:'whale-shark', 'turtle-22-3':'turtle'};
    const trimmed = key.trim();
    const cleanKey = Object.prototype.hasOwnProperty.call(aliases, trimmed.toLowerCase()) ? aliases[trimmed.toLowerCase()] : trimmed;
    const dict = this.getDictionary();

    // Direct match across categories
    for (const group of Object.values(dict)) {
      if (Object.prototype.hasOwnProperty.call(group, cleanKey)) return group[cleanKey];
    }

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

    // Composite Path matching (e.g. CONTESTANT_D_eagle-5-1 or CONTESTANT_B_rabbit-1)
    if (lower.startsWith("contestant_")) {
      const parts = cleanKey.split("_");
      if (parts.length >= 3) {
        const modelId = parts.slice(0, 2).join("_").toUpperCase();
        const animalId = parts.slice(2).join("_").toLowerCase();
        const modelData = dict.contestants[modelId] || this.lookup(modelId);
        let animalData = dict.animals[animalId] || this.lookup(animalId);
        
        if (!animalData) {
          const prefix = animalId.split("-")[0];
          animalData = dict.animals[prefix] || this.lookup(prefix) || {
            id: animalId,
            term: animalId,
            name: animalId,
            category: "Zoo Animals",
            tagline: "Execution Policy",
            tooltip: `Execution policy container (${animalId}) with specialized holding and turnover parameters.`,
            details: `Simulated trading container parameterizing portfolio frictions and bandwidth.`
          };
        }

        if (modelData && animalData) {
          return {
            id: cleanKey,
            term: cleanKey,
            isComposite: true,
            modelId: modelId,
            animalId: animalId,
            model: modelData,
            animal: animalData,
            category: "Composite Path",
            tagline: `${modelData.name} × ${animalData.name}`,
            name: `${modelData.name} × ${animalData.name}`,
            tooltip: `Tournament path coupling <strong>${modelData.name}</strong> with the <strong>${animalData.name}</strong> execution container.`,
            details: `<strong>🧬 Model Candidate (${modelId}):</strong> ${modelData.tooltip}<br/><br/><strong>🐾 Execution Policy (${animalId}):</strong> ${animalData.tooltip}`
          };
        }
      }
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
