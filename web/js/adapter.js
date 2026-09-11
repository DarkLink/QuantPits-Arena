/**
 * QuantPits-Arena: Unified Data Adapter & Selector Layer
 * Provides index lookups, metric aggregations, and filtered queries across paths and contestants.
 */

class ArenaDataAdapter {
  constructor(rawData) {
    if (!rawData) {
      const activeSid = window.ArenaApp?.currentSeasonId || "season_01";
      if (window.ARENA_SEASONS_DATA && window.ARENA_SEASONS_DATA[activeSid]) {
        rawData = window.ARENA_SEASONS_DATA[activeSid];
      } else if (window.ARENA_DATA_PREVIEW) {
        window.ARENA_DATA = window.ARENA_DATA_PREVIEW;
        window._ARENA_IS_PREVIEW = true;
        rawData = window.ARENA_DATA_PREVIEW;
      } else {
        rawData = window.ARENA_DATA;
      }
    }
    this.raw = rawData || window.ARENA_DATA || {};
    this.metadata = this.raw.metadata || this.raw.meta || {};
    this.meta = this.metadata;
    this.isPreview = !!this.metadata.preview || !!window._ARENA_IS_PREVIEW;
    this.contestants = this.raw.contestants || [];
    this.paths = this.raw.paths || [];
    this.navTimeline = this.raw.nav_timeline || { dates: [], curves: {} };
    this.monkeyDistributions = this.raw.monkey_null_distributions || [];
    this.decisionForks = this.raw.decision_forks || [];
    this.matrix = this.raw.matrix || { rows: [], columns: [], data: {} };

    // Index lookup maps
    this.contestantMap = new Map();
    this.contestants.forEach(c => {
      // Standardize fields for view compatibility
      c.id = c.id || c.contestant_id;
      c.anonymous_name = c.anonymous_name || c.display_name || c.contestant_id;
      c.bio = c.bio || c.historical_role || "Historical quantitative model candidate.";
      c.retire_date = c.burial_date || c.retire_date || c.train_cutoff || "2026-06-26";
      c.retire_reason = c.retire_reason || c.historical_role || "Archived candidate model.";
      c.status = c.status || "RETIRED";
      c.architecture_type = c.architecture_type || c.training_mode || "Multi-Factor Ensemble";
      c.lineage = c.lineage || c.family || "Family-Alpha";
      c.historical_is_sharpe = c.historical_is_sharpe !== undefined ? c.historical_is_sharpe : (c.legacy_is_sharpe || 1.85);
      c.legacy_is_sharpe = c.historical_is_sharpe;
      c.historical_is_return_pct = c.historical_is_return_pct !== undefined ? c.historical_is_return_pct : 20.0;
      c.historical_is_mdd_pct = c.historical_is_mdd_pct !== undefined ? c.historical_is_mdd_pct : 8.0;
      c.historical_sys_ann_return_pct = c.historical_sys_ann_return_pct !== undefined ? c.historical_sys_ann_return_pct : null;
      c.historical_metric_basis = c.historical_metric_basis || "Cashflow-adjusted cumulative system return from weekly inception (2024-10-21) up to burial date";

      this.contestantMap.set(c.contestant_id, c);
      this.contestantMap.set(c.id, c);
    });

    this.decisionForks.forEach(f => {
      f.id = f.id || f.fork_id;
      f.date = f.date || f.decision_date;
      f.chosen_contestant_id = f.chosen_contestant_id || f.chosen_id;
      f.rejected_contestant_id = f.rejected_contestant_id || f.rejected_id;
      f.description = f.description || f.historical_context;
      f.chosen_reason = f.chosen_reason || "Promoted based on model validation criteria across market regimes.";
      f.rejected_reason = f.rejected_reason || "Retired or demoted per selection protocol.";
    });

    this.pathMap = new Map();
    this.paths.forEach(p => {
      // Statistical data normalization: preserve empirical values, floor p-values at 0.001 (plus-one limit)
      if (p.percentile_rank !== undefined && p.percentile_rank !== null) {
        p.percentile_rank = Number(p.percentile_rank);
      }
      if (p.monkey_percentile !== undefined && p.monkey_percentile !== null) {
        p.monkey_percentile = Number(p.monkey_percentile);
      }
      if (p.empirical_p_value !== undefined && p.empirical_p_value !== null) {
        p.empirical_p_value = Math.max(Number(p.empirical_p_value), 0.001);
      }
      if (p.p_value !== undefined && p.p_value !== null) {
        p.p_value = Math.max(Number(p.p_value), 0.001);
      }
      // Badge text normalization: replace any legacy "Alpha (p < 0.05)" or "Monkey Slayer"
      if (Array.isArray(p.badges)) {
        p.badges = p.badges.map(b => {
          if (b === "Top 1% Monkey Slayer") return "Top 1% vs Null";
          if (b === "Alpha (p < 0.05)") return "p < 0.05 vs Null";
          return b;
        });
      }
      this.pathMap.set(p.path_id, p);
    });

    this.monkeyMap = new Map();
    this.monkeyDistributions.forEach(m => this.monkeyMap.set(m.strategy_spec, m));
  }

  formatPValue(pVal) {
    if (pVal === undefined || pVal === null || isNaN(pVal)) return "N/A";
    const num = Number(pVal);
    if (num <= 0.001) return "< 0.001";
    return num.toFixed(4);
  }

  formatPercentile(rank, n = 1000) {
    if (rank === undefined || rank === null || isNaN(rank)) return "N/A";
    const num = Number(rank);
    const resolution = 100 / (n + 1);
    if (num <= 0) {
      return `<${resolution.toFixed(1)}%`;
    }
    if (num >= 100 - resolution - 0.005) {
      return `>${(100 - resolution).toFixed(1)}%`;
    }
    return `${num.toFixed(1)}%`;
  }

  getContestants() {
    return this.contestants;
  }

  getAllContestants() {
    return this.contestants;
  }

  getContestant(cid) {
    if (!cid) return this.contestants[0] || null;
    if (typeof cid === "object") {
      cid = cid.contestant_id || cid.id || cid.cid;
    }
    return this.contestantMap.get(cid) || this.contestants.find(c => c.id === cid || c.contestant_id === cid) || this.contestants[0] || null;
  }

  getAllPaths() {
    return this.paths;
  }

  getPath(pathId) {
    return this.pathMap.get(pathId) || null;
  }

  getMonkeyDistribution(specId) {
    return this.monkeyMap.get(specId) || null;
  }

  getAnimalPaths(animalId) {
    return this.paths
      .filter(p => p.contestant_id !== "BENCHMARK" && p.animal_id === animalId)
      .sort((a, b) => b.total_return_pct - a.total_return_pct);
  }

  getAllAnimals() {
    return [
      // 1. Baseline
      {
        id: "robot",
        name: "Robot 22/3 (Baseline)",
        category: "Baseline",
        badge: "Standard Canonical",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Canonical execution container. Selects top-22 stocks by model score, rebalancing 3 positions each week. Serves as the primary reference policy."
      },
      // 2. Execution Lag (Sloth)
      {
        id: "sloth-1",
        name: "Sloth-1 (1-Week Lag)",
        category: "Execution Lag",
        badge: "Latency Stress",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Delays deployment of newly allocated cash into buying targets by 1 week, holding funds in cash before execution. Tests signal half-life."
      },
      {
        id: "sloth-2",
        name: "Sloth-2 (2-Week Lag)",
        category: "Execution Lag",
        badge: "Latency Stress",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Delays entry into new target stocks by 2 weeks. Measures whether alpha decays exponentially or retains multi-week persistence."
      },
      {
        id: "sloth-3",
        name: "Sloth-3 (3-Week Lag)",
        category: "Execution Lag",
        badge: "Latency Stress",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Delays new position deployment by 3 weeks, measuring severe operational latency resilience."
      },
      {
        id: "sloth-4",
        name: "Sloth-4 (4-Week Lag)",
        category: "Execution Lag",
        badge: "Latency Stress",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Delays entry by a full month (4 weeks). A non-negative return indicates exceptional multi-month signal durability."
      },
      // 3. Stale Holding (Snail)
      {
        id: "snail-1",
        name: "Snail-1 (1-Week Holding Delay)",
        category: "Stale Holding",
        badge: "Exit Inertia",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Postpones forced liquidation of dropped positions by 1 week, keeping stale holdings longer in portfolio."
      },
      {
        id: "snail-2",
        name: "Snail-2 (2-Week Holding Delay)",
        category: "Stale Holding",
        badge: "Exit Inertia",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Postpones liquidation of dropped positions by 2 weeks, measuring downside drag from stale factor exposure."
      },
      {
        id: "snail-3",
        name: "Snail-3 (3-Week Holding Delay)",
        category: "Stale Holding",
        badge: "Exit Inertia",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Postpones liquidation by 3 weeks, evaluating exit inertia impact."
      },
      {
        id: "snail-4",
        name: "Snail-4 (4-Week Holding Delay)",
        category: "Stale Holding",
        badge: "Exit Inertia",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Holds dropped positions for 4 extra weeks, testing tolerance to stale momentum."
      },
      // 4. Turnover & Friction (Turtle & Rabbit)
      {
        id: "turtle",
        name: "Turtle (Low Turnover)",
        category: "Turnover Friction",
        badge: "Friction Minimization",
        spec: "P_22_1",
        topk: 22,
        n_drop: 1,
        description: "Ultra-low rebalancing frequency. Replaces only 1 stock per week (4.5% turnover), minimizing transaction slippage and commission."
      },
      {
        id: "rabbit-1",
        name: "Rabbit-1 (50% Turnover)",
        category: "Turnover Friction",
        badge: "High Turnover",
        spec: "P_22_11",
        topk: 22,
        n_drop: 11,
        description: "High turnover handler. Rotates half the portfolio (11 stocks) weekly. Tests whether incremental ranking turnover pays for trading friction."
      },
      {
        id: "rabbit-2",
        name: "Rabbit-2 (100% Full Liquidation)",
        category: "Turnover Friction",
        badge: "Extreme Turnover",
        spec: "P_22_22",
        topk: 22,
        n_drop: 22,
        description: "Total portfolio liquidation and replacement each week. Tests pure single-period signal predictive power with maximum transaction friction."
      },
      // 5. Polarity Inversion (Koala)
      {
        id: "koala",
        name: "Koala (Inverted Polarity)",
        category: "Polarity Inversion",
        badge: "Falsification Test",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: "Selects from the bottom of the ranking as a directional sanity check. A sound ranking should maintain meaningful positive separation from its inverted selection."
      },
      // 6. Capacity & Breadth (Eagle & Whale Shark)
      {
        id: "eagle-5-1",
        name: "Eagle-5/1 (Ultra Concentrated)",
        category: "Capacity & Breadth",
        badge: "Concentration Stress",
        spec: "P_5_1",
        topk: 5,
        n_drop: 1,
        description: "Extreme concentration in top 5 stocks. High idiosyncratic risk, tests extreme top-percentile signal purity."
      },
      {
        id: "eagle-11-2",
        name: "Eagle-11/2 (Compact Portfolio)",
        category: "Capacity & Breadth",
        badge: "Compact Breadth",
        spec: "P_11_2",
        topk: 11,
        n_drop: 2,
        description: "Compact 11-stock portfolio. Half the size of Robot, balancing idiosyncratic focus with factor diversification."
      },
      {
        id: "eagle-44-6",
        name: "Eagle-44/6 (2x Capacity Breadth)",
        category: "Capacity & Breadth",
        badge: "Capacity Expansion",
        spec: "P_44_6",
        topk: 44,
        n_drop: 6,
        description: "Double capacity breadth (44 stocks). Tests whether alpha is concentrated or spans deep into the cross-section."
      },
      {
        id: "eagle-66-9",
        name: "Eagle-66/9 (3x Capacity Breadth)",
        category: "Capacity & Breadth",
        badge: "Capacity Expansion",
        spec: "P_66_9",
        topk: 66,
        n_drop: 9,
        description: "Triple capacity breadth (66 stocks). Simulates medium-large fund deployment capacity."
      },
      {
        id: "eagle-88-12",
        name: "Eagle-88/12 (4x Capacity Breadth)",
        category: "Capacity & Breadth",
        badge: "Capacity Expansion",
        spec: "P_88_12",
        topk: 88,
        n_drop: 12,
        description: "Quadruple capacity breadth (88 stocks). Tests scalability towards institutional fund size."
      },
      {
        id: "whale-shark",
        name: "Whale Shark (50% Universe Breadth)",
        category: "Capacity & Breadth",
        badge: "Large Cap Breadth",
        spec: "P_123_17",
        topk: 123,
        n_drop: 17,
        description: "Holds exactly half of the available universe (123 stocks). Evaluates overall cross-sectional monotonic ranking ability."
      },
      // 7. Percentile Decile Slices (Meerkat)
      ...[10, 20, 30, 40, 50, 60, 70, 80, 90].map(p => ({
        id: `meerkat-${p}`,
        name: `Meerkat-${p} (${p}% Decile Slice)`,
        category: "Percentile Deciles",
        badge: "Monotonicity Test",
        spec: "P_22_3",
        topk: 22,
        n_drop: 3,
        description: `Selects 22 stocks centered around the ${p}th percentile of model ranking. Tests for clean monotonic return decay across deciles.`
      }))
    ];
  }

  getNavDates() {
    return this.navTimeline.dates || [];
  }

  getTimelineDates() {
    return this.getNavDates();
  }

  getMarketBenchmarkName() {
    let name = this.metadata.market_benchmark_name || "CSI 300";
    name = name.replace(/\s*\(Market Benchmark\)/i, "").replace(/\(\)/g, "").trim();
    return name || "CSI 300";
  }

  getMarketBenchmarkCode() {
    return this.metadata.market_benchmark_code || "SH000300";
  }

  getMarketBenchmarkReturn() {
    if (this.metadata.market_benchmark_return_pct !== undefined) {
      return this.metadata.market_benchmark_return_pct;
    }
    return this.metadata.csi300_return_pct !== undefined ? this.metadata.csi300_return_pct : -4.81;
  }

  getBenchmarkMarketCurve() {
    if (this.navTimeline && this.navTimeline.curves) {
      const code = (this.metadata.universe_code || "").toLowerCase();
      if (code && this.navTimeline.curves[`BENCHMARK_${code}`]) return this.navTimeline.curves[`BENCHMARK_${code}`];
      if (this.navTimeline.curves["BENCHMARK_market"]) return this.navTimeline.curves["BENCHMARK_market"];
      if (this.navTimeline.curves["BENCHMARK_csi500"]) return this.navTimeline.curves["BENCHMARK_csi500"];
      if (this.navTimeline.curves["BENCHMARK_csi1000"]) return this.navTimeline.curves["BENCHMARK_csi1000"];
      if (this.navTimeline.curves["BENCHMARK_csi300"]) return this.navTimeline.curves["BENCHMARK_csi300"];
    }
    return [];
  }

  getMarketDrawdown() {
    if (this.navTimeline && this.navTimeline.drawdowns) {
      const code = (this.metadata.universe_code || "").toLowerCase();
      if (code && this.navTimeline.drawdowns[`BENCHMARK_${code}`]) return this.navTimeline.drawdowns[`BENCHMARK_${code}`];
      if (this.navTimeline.drawdowns["BENCHMARK_market"]) return this.navTimeline.drawdowns["BENCHMARK_market"];
      if (this.navTimeline.drawdowns["BENCHMARK_csi500"]) return this.navTimeline.drawdowns["BENCHMARK_csi500"];
      if (this.navTimeline.drawdowns["BENCHMARK_csi1000"]) return this.navTimeline.drawdowns["BENCHMARK_csi1000"];
      if (this.navTimeline.drawdowns["BENCHMARK_csi300"]) return this.navTimeline.drawdowns["BENCHMARK_csi300"];
    }
    return [];
  }

  getNavCurve(pathId) {
    if (!pathId) return [];
    if (pathId === "BENCHMARK_taotie" || pathId === "taotie") return this.getBenchmarkTaotieCurve();
    if (pathId === "BENCHMARK_ghost_taotie" || pathId === "ghost_taotie") return this.getBenchmarkGhostTaotieCurve();
    if (pathId === "BENCHMARK_csi300" || pathId === "csi300" || pathId === "BENCHMARK_csi1000" || pathId === "csi1000" || pathId === "BENCHMARK_market") {
      return this.getBenchmarkMarketCurve();
    }
    return (this.navTimeline && this.navTimeline.curves && this.navTimeline.curves[pathId]) || [];
  }

  getBenchmarkTaotieCurve() {
    return (this.navTimeline && this.navTimeline.curves && this.navTimeline.curves["BENCHMARK_taotie"]) || [];
  }

  getBenchmarkCsi300Curve() {
    return this.getBenchmarkMarketCurve();
  }

  getPathDrawdown(pathId) {
    if (!pathId) return [];
    if (pathId === "BENCHMARK_taotie" || pathId === "taotie") return this.getTaotieDrawdown();
    if (pathId === "BENCHMARK_ghost_taotie" || pathId === "ghost_taotie") return this.getGhostTaotieDrawdown();
    if (pathId === "BENCHMARK_csi300" || pathId === "csi300" || pathId === "BENCHMARK_csi1000" || pathId === "csi1000" || pathId === "BENCHMARK_market") {
      return this.getMarketDrawdown();
    }
    return (this.navTimeline && this.navTimeline.drawdowns && this.navTimeline.drawdowns[pathId]) || [];
  }

  getPathExcessMarket(pathId) {
    return this.getPathExcessCSI300(pathId);
  }

  getPathExcessCSI300(pathId) {
    if (this.navTimeline && this.navTimeline.excess_csi300 && this.navTimeline.excess_csi300[pathId]) {
      return this.navTimeline.excess_csi300[pathId];
    }
    if (pathId === "BENCHMARK_ghost_taotie" || pathId === "ghost_taotie") {
      const gCurve = this.getBenchmarkGhostTaotieCurve();
      const cCurve = this.getBenchmarkMarketCurve();
      if (gCurve && gCurve.length && cCurve && cCurve.length) {
        const len = Math.min(gCurve.length, cCurve.length);
        const res = [];
        for (let i = 0; i < len; i++) {
          res.push(Number(((gCurve[i] - cCurve[i]) * 100).toFixed(2)));
        }
        return res;
      }
    }
    if (pathId === "BENCHMARK_taotie" || pathId === "taotie") {
      const tCurve = this.getBenchmarkTaotieCurve();
      const cCurve = this.getBenchmarkMarketCurve();
      if (tCurve && tCurve.length && cCurve && cCurve.length) {
        const len = Math.min(tCurve.length, cCurve.length);
        const res = [];
        for (let i = 0; i < len; i++) {
          res.push(Number(((tCurve[i] - cCurve[i]) * 100).toFixed(2)));
        }
        return res;
      }
    }
    return [];
  }

  getCsi300Drawdown() {
    return this.getMarketDrawdown();
  }

  getTaotieDrawdown() {
    return (this.navTimeline && this.navTimeline.drawdowns && this.navTimeline.drawdowns["BENCHMARK_taotie"]) || [];
  }

  getCsi300Return() {
    return this.getMarketBenchmarkReturn();
  }

  getTaotieReturn() {
    return this.metadata.taotie_return_pct !== undefined ? this.metadata.taotie_return_pct : 2.32;
  }

  hasGhostTaotie() {
    return !!this.paths.find(p => p.animal_id === "ghost_taotie") || !!this.navTimeline.curves?.["BENCHMARK_ghost_taotie"];
  }

  getGhostTaotieReturn() {
    const p = this.paths.find(p => p.animal_id === "ghost_taotie");
    return p ? p.total_return_pct : 3.85;
  }

  getBenchmarkGhostTaotieCurve() {
    return this.navTimeline.curves?.["BENCHMARK_ghost_taotie"] || [];
  }

  getPathExcessTaotie(pathId) {
    const pCurve = this.getNavCurve(pathId);
    const bCurve = this.getBenchmarkTaotieCurve();
    if (!pCurve || !bCurve || pCurve.length === 0) return [];
    const len = Math.min(pCurve.length, bCurve.length);
    const res = [];
    for (let i = 0; i < len; i++) {
      res.push(Number(((pCurve[i] - bCurve[i]) * 100).toFixed(2)));
    }
    return res;
  }

  getPathExcessGhostTaotie(pathId) {
    const pCurve = this.getNavCurve(pathId);
    const bCurve = this.getBenchmarkGhostTaotieCurve();
    if (!pCurve || !bCurve || pCurve.length === 0) return [];
    const len = Math.min(pCurve.length, bCurve.length);
    const res = [];
    for (let i = 0; i < len; i++) {
      res.push(Number(((pCurve[i] - bCurve[i]) * 100).toFixed(2)));
    }
    return res;
  }

  getSpreadCurve(pathIdA, pathIdB) {
    const curveA = this.getNavCurve(pathIdA);
    const curveB = this.getNavCurve(pathIdB);
    if (!curveA || !curveB || curveA.length === 0) return [];
    const len = Math.min(curveA.length, curveB.length);
    const res = [];
    for (let i = 0; i < len; i++) {
      res.push(Number(((curveA[i] - curveB[i]) * 100).toFixed(2)));
    }
    return res;
  }

  getGhostTaotieDrawdown() {
    const curve = this.getBenchmarkGhostTaotieCurve();
    if (!curve || curve.length === 0) return [];
    let peak = curve[0] || 1.0;
    const dds = [];
    for (let i = 0; i < curve.length; i++) {
      if (curve[i] > peak) peak = curve[i];
      const dd = peak > 0 ? ((curve[i] - peak) / peak) * 100 : 0;
      dds.push(Number(dd.toFixed(2)));
    }
    return dds;
  }

  getAllContestantsAndBenchmarks() {
    const list = this.contestants.map(c => ({
      id: c.id || c.contestant_id,
      name: c.display_name || c.anonymous_name || c.id,
      isBenchmark: false,
      tag: "Model Candidate"
    }));

    list.push({
      id: "BENCHMARK_taotie",
      name: "Taotie (Physical Baseline 500k)",
      isBenchmark: true,
      tag: "Executable Benchmark"
    });

    if (this.hasGhostTaotie()) {
      list.push({
        id: "BENCHMARK_ghost_taotie",
        name: "Ghost Taotie (Theoretical Equal-Weight 100M)",
        isBenchmark: true,
        tag: "Theoretical Benchmark"
      });
    }

    const mName = this.getMarketBenchmarkName();
    list.push({
      id: "BENCHMARK_csi300",
      name: `${mName} (Market Benchmark)`,
      isBenchmark: true,
      tag: "Market Anchor"
    });

    return list;
  }

  getSubjectProfile(subjectId, animalId = "robot") {
    if (!subjectId) return null;

    if (subjectId === "BENCHMARK_taotie" || subjectId === "taotie") {
      const curve = this.getBenchmarkTaotieCurve();
      const dd = this.getTaotieDrawdown();
      const minDd = dd && dd.length ? Math.min(...dd) * 100 : 0;
      const lastVal = curve && curve.length ? curve[curve.length - 1] : 1.0;
      return {
        id: "BENCHMARK_taotie",
        name: "Taotie (Physical Baseline 500k)",
        shortName: "Taotie",
        isBenchmark: true,
        tag: "Executable Benchmark",
        curve: curve,
        totalReturnPct: Number(((lastVal - 1.0) * 100).toFixed(2)),
        maxDrawdownPct: Math.abs(Number(minDd.toFixed(2))),
        sharpeRatio: null,
        nullCourt: "Physical Floor"
      };
    }

    if (subjectId === "BENCHMARK_ghost_taotie" || subjectId === "ghost_taotie") {
      const curve = this.getBenchmarkGhostTaotieCurve();
      const dd = this.getGhostTaotieDrawdown();
      const minDd = dd && dd.length ? Math.min(...dd) * 100 : 0;
      const lastVal = curve && curve.length ? curve[curve.length - 1] : 1.0;
      return {
        id: "BENCHMARK_ghost_taotie",
        name: "Ghost Taotie (Theoretical Equal-Weight 100M)",
        shortName: "Ghost Taotie",
        isBenchmark: true,
        tag: "Theoretical Benchmark",
        curve: curve,
        totalReturnPct: Number(((lastVal - 1.0) * 100).toFixed(2)),
        maxDrawdownPct: Math.abs(Number(minDd.toFixed(2))),
        sharpeRatio: null,
        nullCourt: "Theoretical Ceiling"
      };
    }

    if (subjectId === "BENCHMARK_csi300" || subjectId === "csi300" || subjectId === "BENCHMARK_market") {
      const curve = this.getBenchmarkCsi300Curve();
      const dd = this.getCsi300Drawdown();
      const minDd = dd && dd.length ? Math.min(...dd) * 100 : 0;
      const lastVal = curve && curve.length ? curve[curve.length - 1] : 1.0;
      const mName = this.getMarketBenchmarkName();
      return {
        id: "BENCHMARK_csi300",
        name: `${mName} (Market Benchmark)`,
        shortName: mName,
        isBenchmark: true,
        tag: "Market Anchor",
        curve: curve,
        totalReturnPct: Number(((lastVal - 1.0) * 100).toFixed(2)),
        maxDrawdownPct: Math.abs(Number(minDd.toFixed(2))),
        sharpeRatio: null,
        nullCourt: "Beta Anchor"
      };
    }

    const contestant = this.getContestant(subjectId);
    const path = this.getPath(`${subjectId}_${animalId}`) || this.getPath(`${subjectId}_robot`) || (this.paths.find(p => p.contestant_id === subjectId));
    const curve = path ? this.getNavCurve(path.path_id) : [];
    const ret = path ? path.total_return_pct : (curve && curve.length ? Number(((curve[curve.length - 1] - 1.0) * 100).toFixed(2)) : 0);
    const mdd = path ? path.max_drawdown_pct : 0;
    const sharpe = path ? path.sharpe_ratio : null;
    const nullCourt = path && path.null_court && path.null_court.verdict ? path.null_court.verdict : "Pass";

    return {
      id: subjectId,
      name: contestant ? (contestant.display_name || contestant.anonymous_name || contestant.id) : subjectId,
      shortName: contestant ? (contestant.display_name || contestant.anonymous_name || contestant.id) : subjectId,
      isBenchmark: false,
      tag: contestant ? (contestant.role || contestant.category || "Contestant") : "Model Candidate",
      curve: curve,
      totalReturnPct: ret,
      maxDrawdownPct: mdd,
      sharpeRatio: sharpe,
      nullCourt: nullCourt,
      contestant: contestant,
      path: path
    };
  }

  getMacroPanoramaData(metricMode = "nav", filterGroup = "top5", focusModel = "all") {
    const dates = this.getNavDates();
    if (!dates || dates.length === 0) return { dates: [], seriesList: [] };

    let candidatePaths = [];
    let alphaPaths = this.paths.filter(p => p.contestant_id !== "BENCHMARK");

    if (focusModel && focusModel !== "all") {
      alphaPaths = alphaPaths.filter(p => p.contestant_id === focusModel);
    }

    if (filterGroup === "top5") {
      candidatePaths = [...alphaPaths].sort((a, b) => b.total_return_pct - a.total_return_pct).slice(0, 6);
    } else if (filterGroup === "robot") {
      candidatePaths = alphaPaths.filter(p => p.animal_id === "robot");
    } else if (filterGroup === "eagle") {
      candidatePaths = alphaPaths.filter(p => p.animal_id.startsWith("eagle")).slice(0, 6);
    } else if (filterGroup === "sloth") {
      candidatePaths = alphaPaths.filter(p => p.animal_id.startsWith("sloth")).slice(0, 6);
    } else if (filterGroup === "snail") {
      candidatePaths = alphaPaths.filter(p => p.animal_id.startsWith("snail")).slice(0, 6);
    } else if (filterGroup === "turnover") {
      candidatePaths = alphaPaths.filter(p => p.animal_id.startsWith("rabbit") || p.animal_id === "turtle").slice(0, 6);
    } else if (filterGroup === "koala") {
      candidatePaths = alphaPaths.filter(p => p.animal_id === "koala").slice(0, 6);
    } else {
      candidatePaths = alphaPaths.slice(0, 6);
    }

    const taotieCurve = this.getBenchmarkTaotieCurve();
    const ghostTaotieCurve = this.getBenchmarkGhostTaotieCurve();
    const csi300Curve = this.getBenchmarkCsi300Curve();

    const taotieDD = this.getTaotieDrawdown();
    const ghostDD = this.getGhostTaotieDrawdown();
    const csiDD = this.getCsi300Drawdown();

    const hasGhost = this.hasGhostTaotie();
    const seriesList = [];
    const palette = ["#10b981", "#38bdf8", "#818cf8", "#f43f5e", "#fb923c", "#ec4899"];

    candidatePaths.forEach((p, idx) => {
      let data = [];
      if (metricMode === "nav") {
        data = this.getNavCurve(p.path_id);
      } else if (metricMode === "excess_taotie") {
        data = this.getPathExcessTaotie(p.path_id);
      } else if (metricMode === "excess_ghost") {
        data = this.getPathExcessGhostTaotie(p.path_id);
      } else if (metricMode === "excess_csi300") {
        data = this.getPathExcessCSI300(p.path_id);
      } else if (metricMode === "drawdown") {
        data = this.getPathDrawdown(p.path_id);
      }

      seriesList.push({
        id: p.path_id,
        name: p.path_id,
        type: "candidate",
        color: palette[idx % palette.length],
        data: data || [],
        path: p
      });
    });

    if (metricMode === "nav") {
      if (hasGhost && ghostTaotieCurve.length > 0) {
        seriesList.push({
          id: "BENCHMARK_ghost_taotie",
          name: "Ghost Taotie (100M)",
          type: "benchmark_ghost",
          color: "#00f0ff",
          lineStyle: { type: [8, 4], width: 2.2 },
          data: ghostTaotieCurve
        });
      }

      if (taotieCurve.length > 0) {
        seriesList.push({
          id: "BENCHMARK_taotie",
          name: "Taotie (500k)",
          type: "benchmark_taotie",
          color: "#c084fc",
          lineStyle: { type: [4, 4], width: 2.2 },
          data: taotieCurve
        });
      }

      if (csi300Curve.length > 0) {
        seriesList.push({
          id: "BENCHMARK_csi300",
          name: this.getMarketBenchmarkName(),
          type: "benchmark_csi300",
          color: "#f59e0b",
          lineStyle: { type: [6, 6], width: 2.0 },
          data: csi300Curve
        });
      }
    } else if (metricMode === "drawdown") {
      if (hasGhost && ghostDD.length > 0) {
        seriesList.push({
          id: "BENCHMARK_ghost_taotie",
          name: "Ghost Taotie (100M)",
          type: "benchmark_ghost",
          color: "#00f0ff",
          lineStyle: { type: [8, 4], width: 2.2 },
          data: ghostDD
        });
      }

      if (taotieDD.length > 0) {
        seriesList.push({
          id: "BENCHMARK_taotie",
          name: "Taotie (500k)",
          type: "benchmark_taotie",
          color: "#c084fc",
          lineStyle: { type: [4, 4], width: 2.2 },
          data: taotieDD
        });
      }

      if (csiDD.length > 0) {
        seriesList.push({
          id: "BENCHMARK_csi300",
          name: this.getMarketBenchmarkName(),
          type: "benchmark_csi300",
          color: "#f59e0b",
          lineStyle: { type: [6, 6], width: 2.0 },
          data: csiDD
        });
      }
    } else if (metricMode === "excess_taotie") {
      const zeroBase = dates.map(() => 0.0);
      seriesList.push({
        id: "BENCHMARK_zero_taotie",
        name: "Taotie (500k)",
        type: "benchmark_zero",
        color: "#c084fc",
        lineStyle: { type: [4, 4], width: 2.2 },
        data: zeroBase
      });
    } else if (metricMode === "excess_ghost") {
      const zeroBase = dates.map(() => 0.0);
      seriesList.push({
        id: "BENCHMARK_zero_ghost",
        name: "Ghost Taotie (100M)",
        type: "benchmark_zero",
        color: "#00f0ff",
        lineStyle: { type: [8, 4], width: 2.2 },
        data: zeroBase
      });
    } else if (metricMode === "excess_csi300") {
      const zeroBase = dates.map(() => 0.0);
      seriesList.push({
        id: "BENCHMARK_zero_csi300",
        name: this.getMarketBenchmarkName(),
        type: "benchmark_zero",
        color: "#f59e0b",
        lineStyle: { type: [6, 6], width: 2.0 },
        data: zeroBase
      });
    }

    return {
      dates: dates,
      seriesList: seriesList,
      metricMode: metricMode,
      filterGroup: filterGroup
    };
  }

  getCurrentSeasonMeta() {
    let sid = this.metadata.season_id || window.ArenaApp?.currentSeasonId || "season_01";
    if (sid === "season_1") sid = "season_01";
    if (sid === "season_2") sid = "season_02";
    const seasons = window.ARENA_SEASONS_INDEX || [];
    const fromIndex = seasons.find(s => s.id === sid) || {};
    return { ...this.metadata, ...fromIndex, id: sid };
  }

  getDispatchesData() {
    return this.raw.dispatches || null;
  }

  getDecisionForks() {
    return this.decisionForks;
  }

  getDecisionFork(forkId) {
    return this.decisionForks.find(f => f.fork_id === forkId || f.id === forkId) || null;
  }

  /**
   * Global KPI summary metrics
   */
  getGlobalKPIs() {
    const alphaPaths = this.paths.filter(p => p.contestant_id !== "BENCHMARK");
    if (alphaPaths.length === 0) {
      return {
        totalPaths: 0,
        statSignificantCount: 0,
        statSignificantPct: "0.0%",
        topReturn: 0,
        medianReturn: 0,
        bestSharpe: 0,
        taotieReturn: 2.32,
        csi300Return: -4.81
      };
    }

    const rets = alphaPaths.map(p => p.total_return_pct);
    const sortedRets = [...rets].sort((a, b) => a - b);
    const medianRet = sortedRets[Math.floor(sortedRets.length / 2)];
    const topRet = Math.max(...rets);
    const bestSharpe = Math.max(...alphaPaths.map(p => p.sharpe_ratio || 0));

    const sigCount = alphaPaths.filter(p => (p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0)) >= 95.0).length;
    const sigPct = ((sigCount / alphaPaths.length) * 100).toFixed(1) + "%";

    const taotieRet = this.getTaotieReturn();
    const csi300Ret = this.getCsi300Return();

    return {
      totalPaths: alphaPaths.length,
      statSignificantCount: sigCount,
      statSignificantPct: sigPct,
      topReturn: topRet,
      medianReturn: medianRet,
      bestSharpe: bestSharpe,
      taotieReturn: taotieRet,
      csi300Return: csi300Ret
    };
  }

  getAnimalCategories() {
    const cats = new Set();
    this.paths.forEach(p => {
      if (p.animal_category) cats.add(p.animal_category);
    });
    return Array.from(cats);
  }

  getFilteredPaths(filters = {}) {
    let result = this.paths.filter(p => p.contestant_id !== "BENCHMARK");

    const cid = filters.contestantId || filters.contestant;
    if (cid && cid !== "ALL") {
      result = result.filter(p => p.contestant_id === cid);
    }

    const cat = filters.animalCategory || filters.category;
    if (cat && cat !== "ALL") {
      result = result.filter(p => p.animal_category === cat);
    }

    const q = (filters.search || filters.searchQuery || "").toLowerCase().trim();
    if (q) {
      result = result.filter(p =>
        (p.path_id && p.path_id.toLowerCase().includes(q)) ||
        (p.animal_id && p.animal_id.toLowerCase().includes(q)) ||
        (p.animal_name && p.animal_name.toLowerCase().includes(q)) ||
        (p.contestant_id && p.contestant_id.toLowerCase().includes(q))
      );
    }

    const sig = filters.significance || filters.statFilter;
    if (sig) {
      if (sig === "SIG" || sig === "SIG_95") {
        result = result.filter(p => (p.monkey_percentile !== undefined ? p.monkey_percentile : (p.percentile_rank || 0)) >= 95.0);
      } else if (sig === "NOT_SIG") {
        result = result.filter(p => (p.monkey_percentile !== undefined ? p.monkey_percentile : (p.percentile_rank || 0)) < 95.0);
      } else if (sig === "SIG_99") {
        result = result.filter(p => (p.monkey_percentile !== undefined ? p.monkey_percentile : (p.percentile_rank || 0)) >= 99.0);
      }
    }

    const retFilter = filters.returnFilter;
    if (retFilter === "POSITIVE") {
      result = result.filter(p => p.total_return_pct > 0);
    } else if (retFilter === "NEGATIVE") {
      result = result.filter(p => p.total_return_pct < 0);
    }

    return result;
  }

  /**
   * Filter paths by multiple criteria (Alias)
   */
  filterPaths(filters = {}) {
    return this.getFilteredPaths(filters);
  }

  /**
   * Extract behavioral fingerprints for contestant profile
   */
  getContestantFingerprints(cid) {
    const cPaths = this.paths.filter(p => p.contestant_id === cid);
    const pathByAnimal = new Map();
    cPaths.forEach(p => pathByAnimal.set(p.animal_id, p));

    // 1. Delay Sensitivity (Robot, Sloth-1~4, Snail-1~4)
    const delayData = {
      lags: [0, 1, 2, 3, 4],
      sloth: [
        pathByAnimal.get("robot")?.total_return_pct ?? null,
        pathByAnimal.get("sloth-1")?.total_return_pct ?? null,
        pathByAnimal.get("sloth-2")?.total_return_pct ?? null,
        pathByAnimal.get("sloth-3")?.total_return_pct ?? null,
        pathByAnimal.get("sloth-4")?.total_return_pct ?? null,
      ],
      snail: [
        pathByAnimal.get("robot")?.total_return_pct ?? null,
        pathByAnimal.get("snail-1")?.total_return_pct ?? null,
        pathByAnimal.get("snail-2")?.total_return_pct ?? null,
        pathByAnimal.get("snail-3")?.total_return_pct ?? null,
        pathByAnimal.get("snail-4")?.total_return_pct ?? null,
      ]
    };

    // 2. Turnover Sensitivity (Turtle, Robot, Rabbit-1, Rabbit-2)
    const turnoverData = [
      { name: "Turtle (Low Turnover)", return: pathByAnimal.get("turtle")?.total_return_pct ?? 0 },
      { name: "Robot (Standard)", return: pathByAnimal.get("robot")?.total_return_pct ?? 0 },
      { name: "Rabbit-1 (50% Turnover)", return: pathByAnimal.get("rabbit-1")?.total_return_pct ?? 0 },
      { name: "Rabbit-2 (100% Turnover)", return: pathByAnimal.get("rabbit-2")?.total_return_pct ?? 0 },
    ];

    // 3. Concentration & Capacity Breadth (Eagle 5, 11, 44, 66, 88, WhaleShark, Taotie)
    const breadthData = [
      { topk: 5, label: "Eagle-5/1", return: pathByAnimal.get("eagle-5-1")?.total_return_pct ?? 0 },
      { topk: 11, label: "Eagle-11/2", return: pathByAnimal.get("eagle-11-2")?.total_return_pct ?? 0 },
      { topk: 22, label: "Robot-22/3", return: pathByAnimal.get("robot")?.total_return_pct ?? 0 },
      { topk: 44, label: "Eagle-44/6", return: pathByAnimal.get("eagle-44-6")?.total_return_pct ?? 0 },
      { topk: 66, label: "Eagle-66/9", return: pathByAnimal.get("eagle-66-9")?.total_return_pct ?? 0 },
      { topk: 88, label: "Eagle-88/12", return: pathByAnimal.get("eagle-88-12")?.total_return_pct ?? 0 },
      { topk: 123, label: "WhaleShark", return: pathByAnimal.get("whale-shark")?.total_return_pct ?? 0 },
      { topk: 246, label: "Taotie (Full Pool)", return: this.getPath("BENCHMARK_taotie")?.total_return_pct ?? 2.32 },
    ];

    // 4. Direction Sanity (Robot vs Koala)
    const directionData = {
      robot: pathByAnimal.get("robot")?.total_return_pct ?? 0,
      koala: pathByAnimal.get("koala")?.total_return_pct ?? 0,
      spread: (pathByAnimal.get("robot")?.total_return_pct ?? 0) - (pathByAnimal.get("koala")?.total_return_pct ?? 0)
    };

    // 5. Meerkat Percentile Slices (10% ~ 90%)
    const meerkatData = [];
    for (let p = 10; p <= 90; p += 10) {
      meerkatData.push({
        percentile: `${p}%`,
        return: pathByAnimal.get(`meerkat-${p}`)?.total_return_pct ?? 0
      });
    }

    return {
      delayData,
      turnoverData,
      breadthData,
      directionData,
      meerkatData
    };
  }

  isPreviewMode() {
    return this.isPreview;
  }

  getPeriodLabel() {
    return this.metadata.period_label || `${this.metadata.anchor_date || '2026-07-03'} ~ ${this.metadata.end_date || '2026-08-28'} (${this.getTradingDays()} trading days)`;
  }

  getTradingDays() {
    return this.metadata.trading_days || (this.navTimeline && this.navTimeline.dates ? this.navTimeline.dates.length : 41);
  }

  getEmbargoDate() {
    return this.metadata.preview_embargo_until || "2026-09-11";
  }
}

// Global statistical formatting helpers
window.formatPValue = function(pVal) {
  if (pVal === undefined || pVal === null || isNaN(pVal)) return "N/A";
  const num = Number(pVal);
  if (num <= 0.001) return "< 0.001";
  return num.toFixed(4);
};

window.formatPercentile = function(rank, n = 1000) {
  if (rank === undefined || rank === null || isNaN(rank)) return "N/A";
  const num = Number(rank);
  const resolution = 100 / (n + 1);
  if (num <= 0) {
    return `<${resolution.toFixed(1)}%`;
  }
  if (num >= 100 - resolution - 0.005) {
    return `>${(100 - resolution).toFixed(1)}%`;
  }
  return `${num.toFixed(1)}%`;
};

// Attach class and singleton adapter to global window scope
window.ArenaDataAdapter = ArenaDataAdapter;
window.arenaAdapter = new ArenaDataAdapter();
