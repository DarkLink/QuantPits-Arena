/**
 * web/js/views/methodology.js
 * ===========================
 * Methodology & Statistical Axioms Documentation View
 * Directly aligned with DRAFT.md (Empirical Quantitative Standards)
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
          <p class="view-subtitle">The testing architecture, null benchmark suite, execution constraints, and statistical interpretation rules of QuantPits Arena</p>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 24px; max-width: 1000px;">
        <!-- 1. Core Axiom: Historical Biography != Arena Record -->
        <div class="card" style="border-left: 4px solid var(--accent-amber);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-amber); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>⚖️</span> 1. Core Axiom: Historical Biography ≠ Arena Record
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Traditional quantitative presentations often blur together historical backtests, development-period performance, and later live results. QuantPits Arena does not. Every contestant maintains two strictly separated records:
          </p>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 8px;">
            <div style="background: rgba(255, 255, 255, 0.02); padding: 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-amber); display: block; margin-bottom: 6px;">Historical Biography & Context</strong>
              <p style="font-size: 12px; color: var(--text-secondary); line-height: 1.6; margin: 0;">
                Includes original research thesis, architecture, feature set, training period, historical backtest statistics, former production role, replacement history, and retirement reason. 
                <br><br>
                <b style="color: var(--text-primary);">These records exist only as biography and contribute zero weight to Arena rankings.</b> A former production champion receives no starting advantage; a historically retired model receives no penalty.
              </p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); padding: 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-cyan); display: block; margin-bottom: 6px;">Arena Out-of-Sample Record</strong>
              <p style="font-size: 12px; color: var(--text-secondary); line-height: 1.6; margin: 0;">
                Every eligible artifact enters the common Arena at the same anchor:
                <br>• <b>Anchor Date:</b> 2026-07-03
                <br>• <b>Initial NAV:</b> 1.0000
                <br>• <b>Initial Capital:</b> CNY 500,000
                <br><br>
                All Arena metrics are calculated from this common starting point. The frozen artifacts had no access to Arena-period market data during training. <b>Historical reputation is biography; Arena performance starts from zero.</b>
              </p>
            </div>
          </div>
        </div>

        <!-- 2. Parametric Monkey Null Benchmark Suite -->
        <div class="card" style="border-left: 4px solid var(--accent-purple);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-purple); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🐒</span> 2. High-Resolution Parametric Monkey Null Benchmark
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Absolute return alone says very little about signal quality. A strategy can earn money because its universe rises, or lose money during a drawdown while still selecting unusually well. A highly concentrated random portfolio can occasionally generate spectacular returns purely by chance. QuantPits Arena therefore maintains a large empirical <b>random-ranking null benchmark</b>:
          </p>

          <div style="background: rgba(0,0,0,0.25); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 14px; font-size: 13px; color: var(--text-secondary); line-height: 1.7;">
            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">Colony Construction & Rules:</div>
            <ul style="margin-left: 18px; margin-bottom: 10px;">
              <li><b>1,000 Pseudo-Random Paths per Policy</b>: For each distinct TOPK / DROPN parameter specification, an independent colony of 1,000 deterministic pseudo-random ranking paths is evaluated (11 parameter groups, 11,000 monkey portfolios total).</li>
              <li><b>Identical Constraints</b>: Same eligible stock universe, same market observations, same CNY 500,000 initial capital, 100-share trading lots, affordability rules, and transaction cost model — but <b>zero model signal</b>.</li>
              <li><b>Monkeys Do Not Imitate the Animals</b>: Monkeys are a no-signal reference, not a behavioral sympathy program. They do not sleep or delay rebalances; if a Sloth sleeps through a useful signal, that is the Sloth's problem.</li>
            </ul>

            <div style="font-weight: 600; color: var(--text-primary); margin-top: 12px; margin-bottom: 6px;">Empirical Upper-Tail p-value Formula:</div>
            <div style="font-family: monospace; background: rgba(0,0,0,0.35); padding: 8px 12px; border-radius: 4px; color: var(--accent-cyan); display: inline-block;">
              p_upper = ( #{Monkey Return &ge; Candidate Return} + 1 ) / ( N + 1 )
            </div>
            <p style="margin-top: 8px; margin-bottom: 8px; font-size: 12px;">
              With N = 1,000, minimum reportable empirical p-value is 1 / 1001 &approx; 0.001, providing &approx; 0.1 percentage-point empirical rank resolution.
            </p>

            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 10px 14px; margin-top: 10px;">
              <strong style="color: var(--accent-amber); display: block; margin-bottom: 4px;">Important Interpretation Nuance:</strong>
              <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
                A candidate may be labeled as exhibiting <i>"Statistically significant upper-tail outperformance versus its random-ranking null"</i> when <code>p_upper &lt; 0.05</code> (above the 95th percentile).
                <br>
                <b>The Arena deliberately does NOT automatically translate this label into "Alpha confirmed."</b> A low empirical p-value means the observed result is difficult to reproduce with the specified random-ranking null. It does not, by itself, establish: persistent future alpha, causal model superiority, independence from all factor exposures, or immunity from multiple-comparison effects.
              </div>
            </div>
          </div>
        </div>

        <!-- 3. The 28-Animal Execution Zoo Framework -->
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
            A prediction model produces a ranking. What happens after that ranking exists is a separate research question. QuantPits Zoo applies deliberately different portfolio behaviors to the <b>same underlying model signal</b> to study timing, persistence, turnover, ranking geometry, and concentration:
          </p>

          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 13px;">
            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-cyan);">🤖 Robot (Baseline 22/3)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">TOPK=22, DROPN=3, weekly immediate execution. Represents the baseline production-style portfolio policy and control animal.</div>
            </div>

            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-cyan);">🦥 Sloth 1–4 (Cash Lag)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">Delays signal execution by 1~4 weeks while capital remains uninvested. Measures signal timing decay and delayed-entry robustness.</div>
            </div>

            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-cyan);">🐌 Snail 1–4 (Holding Lag)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">Constructs initial portfolio normally, but delays subsequent rebalance actions by 1~4 weeks. Measures holding inertia cost or benefit.</div>
            </div>

            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-cyan);">🐢 Turtle & 🐇 Rabbit (Turnover Extremes)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">Turtle replaces only 1 stock/cycle (low turnover); Rabbit replaces half or entire portfolio weekly. Tests whether rapid deployment helps or accelerates noise ingestion.</div>
            </div>

            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-rose); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-rose);">🐨 Koala (Inverted Polarity)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">Directional sanity check: selects from the bottom of the ranking. If Koala consistently beats Robot, checking the model sign convention is recommended.</div>
            </div>

            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-amber);">🦡 Meerkat 10%–90% (Rank Slices)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">Samples decile regions (10% to 90%) to study the geometry of the ranking, monotonic decay, and whether signal is concentrated in extreme tails.</div>
            </div>

            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-indigo);">🦅 Eagle Suite (5, 11, 44, 66, 88)</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">Concentration spectrum (5/1 to 88/12). Measures signal concentration vs diversification. Highest return and strongest statistical evidence are not necessarily the same thing.</div>
            </div>

            <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
              <strong style="color: var(--accent-emerald);">🐋 Whale Shark & 🐉 Taotie</strong>
              <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px; line-height: 1.5;">Whale Shark holds &approx;50% of the universe (123 stocks). Taotie holds 100% of universe, acting as the structural reference where selection intensity &rarr; zero.</div>
            </div>
          </div>
        </div>

        <!-- 4. Finite Capital & Real Trading Constraints -->
        <div class="card" style="border-left: 4px solid var(--accent-emerald);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-emerald); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>💰</span> 4. Real Trading & Finite-Capital Constraints
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Arena portfolios are simulated as finite-capital executable portfolios rather than frictionless continuous-weight portfolios:
          </p>
          <ul style="font-size: 13px; color: var(--text-secondary); line-height: 1.8; margin-left: 20px; margin-bottom: 0;">
            <li><strong>Fixed Initial Capital:</strong> Every portfolio begins with exactly <strong>CNY 500,000</strong>. No strategy receives capital proportional to its holdings.</li>
            <li><strong>Minimum Trading Lot:</strong> Mainland-equity rules obey <strong>1 lot = 100 shares</strong>. Fractional-share purchases are strictly prohibited.</li>
            <li><strong>Unaffordable Order Skipping:</strong> If allocated capital cannot purchase one complete 100-share lot, the order is <strong>skipped</strong>. No rounding upward, borrowing, or cash redistribution. Finite-capital cash drag is intentionally preserved.</li>
            <li><strong>Transaction Costs:</strong> All contestants and monkeys apply identical predefined one-way transaction cost models. No strategy receives a frictionless execution exemption.</li>
            <li><strong>Universe Exit Priority:</strong> Securities no longer belonging to the eligible universe receive exit priority, interacting with the applicable DROPN budget according to engine rules.</li>
          </ul>
        </div>

        <!-- 5. Statistical Interpretation & Multiple Comparisons -->
        <div class="card" style="border-left: 4px solid var(--accent-indigo);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-indigo); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🔬</span> 5. Statistical Interpretation & Multiple Comparisons
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            QuantPits Arena contains multiple historical artifacts, multiple animal policies, multiple concentration levels, and multiple exploratory comparisons. Therefore the Arena is not interpreted as a collection of independent confirmatory hypothesis tests.
          </p>
          <div style="background: rgba(0,0,0,0.25); padding: 14px; border-radius: var(--radius-sm); font-size: 13px; color: var(--text-secondary); line-height: 1.7;">
            <p style="margin: 0 0 10px 0;">
              A nominal <code>p &lt; 0.05</code> for one contestant means only that its observed Arena return lies unusually high relative to the specified random-ranking null. It does <b>not</b> mean that searching across the entire Graveyard and Zoo carries a family-wise false-positive probability of 5%.
            </p>
            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">Arena statistics are used primarily to answer:</div>
            <ol style="margin-left: 18px; margin-bottom: 0;">
              <li>Is this model/policy behaving unusually relative to random ranking?</li>
              <li>How sensitive is the signal to timing, turnover, concentration, or inversion?</li>
              <li>Do historical artifacts retain useful predictive structure in a common future environment?</li>
              <li>Did a specific historical replacement decision appear beneficial or regrettable in subsequent out-of-sample data?</li>
            </ol>
            <p style="margin-top: 10px; margin-bottom: 0; color: var(--accent-amber);">
              <b>They are not used to manufacture a single post-hoc "winning model" and retroactively declare it proven.</b>
            </p>
          </div>
        </div>

        <!-- 6. External Simplicity Reference (The Rock) -->
        <div class="card" style="border-left: 4px solid var(--accent-rose);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-rose); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🪨</span> 6. External Simplicity Reference (The Permanent Portfolio)
          </h2>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            The Permanent Portfolio is displayed separately from the stock-selection Arena. It is not a random-ranking null and does not participate in monkey significance testing.
          </p>
          <div style="background: rgba(255, 255, 255, 0.02); padding: 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); font-size: 13px; color: var(--text-secondary); line-height: 1.8;">
            <blockquote style="margin: 0; padding-left: 14px; border-left: 3px solid var(--accent-rose); color: var(--text-primary); font-style: italic;">
              Four buckets. No ranking. No ensemble. No retraining. No comment.
            </blockquote>
            <p style="margin-top: 10px; margin-bottom: 0;">
              Its purpose is not to answer whether QuantPits has stock-selection alpha. Its purpose is to remind the Arena that <b>complexity is not free</b>.
            </p>
          </div>
        </div>

        <!-- Final Axiom Banner -->
        <div class="card" style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(168, 85, 247, 0.08)); border: 1px solid rgba(56, 189, 248, 0.3); text-align: center; padding: 24px;">
          <h3 style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: var(--accent-cyan); margin-bottom: 10px;">
            Final Axiom
          </h3>
          <p style="font-size: 15px; font-weight: 600; color: var(--text-primary); line-height: 1.8; margin: 0;">
            “Absolute return determines who wins the race.<br>
            Monkey percentile determines how surprised we should be.<br>
            The Zoo explains what the model's signal survives.<br>
            The Rock asks whether any of this complexity was worth it.”
          </p>
        </div>
      </div>
    `;
  }
};
