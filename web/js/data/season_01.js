/**
 * web/js/data/season_01.js
 * =======================
 * Season 1: Graveyard Arena Data Package Provider
 */

(function() {
  window.ARENA_SEASONS_DATA = window.ARENA_SEASONS_DATA || {};

  function registerSeason01() {
    var baseData = window.ARENA_DATA_PREVIEW || window.ARENA_DATA;
    if (baseData) {
      // Ensure dispatches metadata is cleanly packaged for Season 1
      if (!baseData.dispatches) {
        baseData.dispatches = {
          executive: {
            tag: "🏆 Official Released Standing",
            badge: "Episodes 01–08 Active",
            title: "The 41-Day Retrospective Baseline",
            window_label: "2026-07-03 ~ 2026-08-28 (41 Trading Days, Weeks 1–8)",
            nature_label: "Retrospective backtest baseline simulated with knowledge of July–August market conditions to establish initial tournament standings.",
            leader_summary: "CONTESTANT_B_eagle-5-1 finished the baseline at NAV 1.1971 (+19.71%), outperforming benchmark by +17.39pp (zero of 1,000 matched monkeys exceeded it, p ≈ 0.001)."
          },
          climate: {
            tag: "🌪️ Weekly Market Climate (Aug 31 – Sep 04)",
            status_badge: "🔒 Embargoed until Sep 11",
            title: "The September 02 Breadth Shock (Arena Designation: \"Black Wednesday\")",
            summary: "The weather outside the cage is public knowledge. How the animals inside handled the storm remains sealed under institutional embargo.",
            bullets: [
              "<strong>Sep 02 Market Breadth Shock</strong>: Growth-heavy and previously strong market segments experienced a sharp reversal, pushing over 80% of traded equities into localized pullbacks within 48 hours.",
              "<strong>Structural Suspense</strong>: Did prolonged signal persistence hold? Did the Eagle's extreme concentration survive, or did high-turnover Rabbits strike back?"
            ],
            decrypt_label: "Full performance decrypts: Friday, September 11, 2026"
          },
          episodes: [
            {
              id: "ep08",
              tab_label: "📜 Ep 01–08: The Forty-One Day King",
              badge: "Released",
              title: "Episodes 01–08: The 41-Day Baseline & The Eagle King",
              content_type: "ep08_baseline"
            },
            {
              id: "ep09",
              tab_label: "🔒 Ep 09: Sep 02 Breadth Shock",
              badge: "Embargoed",
              title: "Episode 09: The September 02 Breadth Shock (Arena Designation: \"Black Wednesday\")",
              content_type: "ep09_embargoed"
            }
          ]
        };
      }
      window.ARENA_SEASONS_DATA["season_01"] = baseData;
    }
  }

  registerSeason01();
  if (typeof document !== 'undefined') {
    document.addEventListener("DOMContentLoaded", registerSeason01);
  }
})();

