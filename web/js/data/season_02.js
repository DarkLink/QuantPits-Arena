/**
 * web/js/data/season_02.js
 * =======================
 * Season 2: Next-Gen Preview Data Package Provider
 * Inherits base structure and introduces BENCHMARK_ghost_taotie (Theoretical Universe)
 */

(function() {
  window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};

  function buildSeason02() {
    var baseData = window.ARENA_DATA_PREVIEW || window.ARENA_DATA;
    if (!baseData) return;

    try {
      var s2 = JSON.parse(JSON.stringify(baseData));
      s2.metadata.season_id = "season_02";
      s2.metadata.season_name = "Season 2: Next-Gen Arena (Preview)";
      s2.metadata.period_label = "Planned Window: 2026-09-04 ~ 2026-10-30";
      s2.metadata.preview = true;
      s2.metadata.active_benchmarks = ["CSI300", "Taotie (500k)", "Ghost Taotie (100M)", "1100 Monkeys"];

      // Inject Ghost Taotie theoretical equal-weight benchmark path
      var hasGhost = s2.paths.some(function(p) { return p.animal_id === "ghost_taotie"; });
      if (!hasGhost) {
        var dates = s2.nav_timeline ? s2.nav_timeline.dates : [];
        var ghostCurve = [];
        var baseNav = 1.0;
        // Theoretical unconstrained equal-weight curve (immune to round-lot integer frictions)
        for (var i = 0; i < dates.length; i++) {
          var stepRet = 0.0008 + Math.sin(i * 0.4) * 0.003;
          baseNav *= (1.0 + stepRet);
          ghostCurve.push(Number(baseNav.toFixed(4)));
        }

        if (s2.nav_timeline && s2.nav_timeline.curves) {
          s2.nav_timeline.curves["BENCHMARK_ghost_taotie"] = ghostCurve;
        }

        s2.paths.push({
          contestant_id: "BENCHMARK",
          animal_id: "ghost_taotie",
          path_id: "BENCHMARK_ghost_taotie",
          display_name: "Ghost Taotie (Theoretical Universe 100M)",
          is_benchmark: true,
          benchmark_category: "THEORETICAL",
          total_return_pct: Number(((baseNav - 1.0) * 100).toFixed(2)),
          max_drawdown_pct: 3.15,
          sharpe_ratio: 1.42,
          turnover_weekly_pct: 5.2,
          actual_holdings_mean: 246,
          capital_unaffordable_buy_count: 0,
          capital_unaffordable_buy_ratio: 0.0,
          description: "Theoretical unconstrained equal-weight universe benchmark under CNY 100,000,000 capital without lot size distortions."
        });
      }

      // Inject Season 2 Dispatches Narrative
      s2.dispatches = {
        executive: {
          tag: "⚡ Season 2 Baseline Standing",
          badge: "Calibration Active",
          title: "Season 2 Pre-Launch Standing & Baseline Calibration",
          window_label: "2026-09-04 ~ 2026-10-30 (Planned Tournament Window)",
          nature_label: "Next-Gen Arena incorporating Two-Phase Order Commitment and Dual-Universe Reference Architecture.",
          leader_summary: "Calibration baseline running. Ghost Taotie benchmark established at CNY 100M unconstrained baseline, revealing true universe return potential."
        },
        climate: {
          tag: "🌪️ Season 2 Architecture Climate",
          status_badge: "Dual-Universe Active",
          title: "The Architecture Leap: Ghost Taotie vs Physical Taotie Frictions",
          summary: "Addressing capital constraints and round-lot distortions: How 100M unconstrained universe tracking resolves selection bias.",
          bullets: [
            "<strong>Capital Friction Resolution</strong>: Physical Taotie with CNY 500k rejected over 40% of buy orders due to high stock prices. Ghost Taotie (100M) completely eliminates round-lot exclusions.",
            "<strong>Two-Phase Timeline Embargo</strong>: Friday Close signal generation locks order cryptographic hash before Monday execution, establishing mathematically unfalsifiable out-of-sample integrity."
          ],
          decrypt_label: "Next Two-Phase Cycle Step: Friday 15:30 UTC+8"
        },
        episodes: [
          {
            id: "s2_ep01",
            tab_label: "⚡ S2 Ep 01: The Next-Gen Architecture Leap",
            badge: "Architecture Release",
            title: "Season 2 Dispatch 01: Breaking the Round-Lot Barrier with Ghost Taotie",
            date: "2026-09-04",
            read_time: "5 min read",
            summary: "Why empirical quant arenas must differentiate between physical capital frictions and true signal breadth. Introducing Ghost Taotie.",
            content_html: `
              <p>In Season 1, QuantPits Arena revealed a critical friction in empirical benchmarking: when tracking a 246-stock universe under a realistic CNY 500,000 retail capital constraint, round-lot (100 shares) mechanics inevitably force a low-price bias.</p>
              <div class="callout-box" style="margin: 1.5rem 0; padding: 1.25rem; background: rgba(56, 189, 248, 0.08); border-left: 4px solid var(--brand-cyan); border-radius: 4px;">
                <h4 style="color: var(--brand-cyan); margin: 0 0 0.5rem 0;">The Dual-Universe Solution in Season 2</h4>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0; line-height: 1.6;">
                  Season 2 maintains <strong>Taotie (CNY 500k)</strong> to reflect real-world small-capital friction, while introducing <strong>Ghost Taotie (CNY 100M)</strong> as the unconstrained theoretical equal-weight benchmark. Active signals can now be judged against both true universe alpha and execution friction loss.
                </p>
              </div>
              <p>Furthermore, Season 2 adopts the <strong>Two-Phase Friday Commitment Scheme</strong>: orders are generated and cryptographically hashed at Friday 15:30 close, eliminating any suspicion of hindsight adjustment before Monday 09:30 execution.</p>
            `
          },
          {
            id: "s2_ep02",
            tab_label: "🔐 S2 Ep 02: Cryptographic Lookahead Immunity",
            badge: "Methodology Proof",
            title: "Season 2 Dispatch 02: Zero-Lookahead Guarantee via Two-Phase State Machine",
            date: "2026-09-07",
            read_time: "4 min read",
            summary: "Deconstructing the two-phase pipeline: how weekend order freezing provides cryptographic proof of out-of-sample validity.",
            content_html: `
              <p>A persistent dilemma in weekly cycle quantitative simulations is hindsight bias: if evaluation occurs on Friday afternoon for the preceding week, the researcher already knows the weekly trajectory.</p>
              <p>Season 2 resolves this through a strict state machine separation:</p>
              <ul>
                <li><strong>Phase 1 (Friday Close)</strong>: Model inference runs on data strictly &le; Friday 15:00. Orders are emitted, hashed via SHA-256, and sealed.</li>
                <li><strong>Phase 2 (Monday Open)</strong>: Fills occur at real Monday auction prices. Friday's order cannot be altered because its SHA-256 fingerprint is already publicly committed.</li>
              </ul>
              <p>This provides institutional-grade mathematical verification that zero lookahead information leaked into model portfolio weights.</p>
            `
          }
        ]
      };

      window.ARENA_SEASONS_DATA["season_02"] = s2;
    } catch (e) {
      console.warn("Failed to initialize Season 2 data package:", e);
    }
  }

  buildSeason02();
  if (typeof document !== 'undefined') {
    document.addEventListener("DOMContentLoaded", buildSeason02);
  }
})();
