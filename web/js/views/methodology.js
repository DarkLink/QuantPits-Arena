/**
 * web/js/views/methodology.js
 * ===========================
 * Methodology & Axioms Documentation View (English Edition)
 */

window.MethodologyView = {
  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    el.innerHTML = `
      <div class="view-header">
        <div>
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
            <h1 class="view-title">Methodology & Statistical Axioms</h1>
            <span class="badge badge-primary">Empirical Quantitative Standards</span>
          </div>
          <p class="view-subtitle">The testing architecture, null benchmark suite, and execution constraints of QuantPits-Arena</p>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 24px; max-width: 1000px;">
        <!-- 1. First Axiom: Biography vs Arena -->
        <div class="card" style="border-left: 4px solid var(--accent-amber);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-amber); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>⚖️</span> 1. Core Axiom: Historical Biography ≠ Arena Record
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            In traditional quantitative presentations, models are often showcased by blending their original in-sample backtests with live results. QuantPits Arena enforces strict decoupling:
          </p>
          <ul style="font-size: 13px; color: var(--text-secondary); line-height: 1.8; margin-left: 20px; margin-bottom: 0;">
            <li><strong>Historical Biography & Context</strong>: Qualitative background recording the original research thesis, historical training period, in-sample Sharpe ratio, and the reasons for retirement or replacement. This serves as historical context only and carries zero weight in arena rankings.</li>
            <li><strong>Arena Out-of-Sample Record</strong>: Regardless of past reputation, every candidate starts at an identical anchor date (2026-07-03) with a normalized base NAV of 1.0000 and initial capital of CNY 500,000. All metrics reflect pure out-of-sample forward simulation.</li>
          </ul>
        </div>

        <!-- 2. Parametric Monkey Null Benchmark Suite -->
        <div class="card" style="border-left: 4px solid var(--accent-purple);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-purple); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🐒</span> 2. High-Resolution Parametric Monkey Null Benchmark
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Absolute return in isolation is statistically uninformative. A model might generate positive return simply by riding market beta, or negative return during a sharp market drawdown while still delivering extraordinary alpha. QuantPits Arena deploys a high-resolution null model suite:
          </p>
          <div style="background: rgba(0,0,0,0.25); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 14px;">
            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">Statistical Testing Specifications:</div>
            <ul style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-left: 18px; margin-bottom: 0;">
              <li><strong>Policy-Matched Groups</strong>: For every distinct portfolio execution policy (combinations of TOPK and DROPN), an independent colony of <strong>1,000 deterministic pseudo-random monkeys</strong> is evaluated (11 groups, 11,000 monkeys total).</li>
              <li><strong>Identical Constraints</strong>: Each monkey trades under identical capital (CNY 500,000), 100-share trading lots, and unaffordable skip constraints, driven solely by scrambled pseudo-random stock rankings.</li>
              <li><strong>Empirical Significance &amp; p-value</strong>:
                <div style="font-family: monospace; color: var(--accent-cyan); margin: 6px 0; font-size: 13px;">
                  Empirical p-value = ( #{Monkey Return &ge; Candidate Return} + 1 ) / ( N + 1 )
                </div>
                A candidate is designated statistically significant (Alpha) only when it outperforms &ge; 95% of its matched monkey colony (p &lt; 0.05).
              </li>
            </ul>
          </div>
        </div>

        <!-- 3. Execution Zoo Framework -->
        <div class="card" style="border-left: 4px solid var(--accent-cyan);">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
            <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-cyan); margin: 0; display: flex; align-items: center; gap: 8px;">
              <span>🦁</span> 3. The 28-Animal Execution Zoo Framework
            </h2>
            <a href="#animals" class="btn btn-sm btn-primary" style="font-size: 11px; padding: 4px 10px; text-decoration: none;">
              Explore In The Zoo &rarr;
            </a>
          </div>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Signal value is deeply entangled with execution mechanics. An identical alpha prediction behaves drastically differently under varying lag, turnover, and concentration regimes. You can inspect cross-model overlay curves interactively in <a href="#animals">The Zoo</a>:
          </p>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 13px;">
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-sm);">
              <strong style="color: var(--accent-cyan);">🤖 Robot (Baseline 22/3)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">TOPK=22, DROPN=3, weekly immediate execution. Acts as the control baseline.</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-sm);">
              <strong style="color: var(--accent-cyan);">🦥 Sloth 1~4 (Cash Lag)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">Delays trade execution by 1~4 weeks while holding uninvested cash. Measures pure signal decay speed.</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-sm);">
              <strong style="color: var(--accent-cyan);">🐌 Snail 1~4 (Holding Lag)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">Extends rebalance frequency to 1~4 weeks while maintaining existing holdings. Measures friction from stale positions.</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-sm);">
              <strong style="color: var(--accent-cyan);">🐢 Turtle & 🐇 Rabbit (Turnover Extremes)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">Turtle replaces only 1 stock per cycle (ultra-low turnover); Rabbit replaces half or entire portfolio weekly (high friction).</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-rose);">
              <strong style="color: var(--accent-rose);">🐨 Koala (Inverted Polarity)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">Buys the lowest-ranked stocks predicted by the model. A sound model must significantly outperform Koala.</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-sm);">
              <strong style="color: var(--accent-amber);">🦡 Meerkat 10%~90% (Decile Slices)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">Slices the ranked cross-section into uniform deciles to test monotonic signal decay.</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-sm);">
              <strong style="color: var(--accent-indigo);">🦅 Eagle Suite & 🐋 Whale Shark</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">Concentration spectrum: 5/1, 11/2, 44/6, 66/9, 88/12, and Whale Shark (50% pool, 123 stocks). Evaluates capacity scalability.</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px 12px; border-radius: var(--radius-sm);">
              <strong style="color: var(--accent-emerald);">🐉 Taotie (100% Full Universe)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">Equal-weight executable portfolio of all 246 stocks, rebalancing passively on universe entry/exit.</div>
            </div>
          </div>
        </div>

        <!-- 4. Finite Capital & Real Trading Constraints -->
        <div class="card" style="border-left: 4px solid var(--accent-emerald);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-emerald); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>💰</span> 4. Real Trading & Finite Capital Constraints
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Many theoretical backtests display inflated performance due to fractional share purchases or frictionless cash reallocations. QuantPits Arena enforces real-world execution rules:
          </p>
          <ul style="font-size: 13px; color: var(--text-secondary); line-height: 1.8; margin-left: 20px; margin-bottom: 0;">
            <li><strong>Fixed Initial Capital</strong>: Exactly <strong>CNY 500,000</strong> per portfolio.</li>
            <li><strong>Minimum Trading Lot</strong>: 1 lot = 100 shares. No fractional shares permitted.</li>
            <li><strong>Unaffordable Order Skipping</strong>: If allocated capital for a target stock cannot purchase 100 shares, the order is <strong>strictly skipped</strong> without rounding up or redistributing residual cash.</li>
            <li><strong>Universe Exit Priority</strong>: Stocks removed from the eligible universe are sold first, capped at the portfolio DROPN limit.</li>
          </ul>
        </div>
      </div>
    `;
  }
};
