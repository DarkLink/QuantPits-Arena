/**
 * web/js/views/disclaimer.js
 * =========================
 * Full Research & Legal Disclaimer View
 * Directly aligned with DRAFT.md
 */

window.DisclaimerView = {
  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    el.innerHTML = `
      <div class="view-header">
        <div>
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
            <h1 class="view-title">Research & Legal Disclaimer</h1>
            <span class="badge badge-warning">Mandatory Notice</span>
          </div>
          <p class="view-subtitle">Terms of access, research-boundary disclosures, and risk acknowledgments for QuantPits Arena</p>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 24px; max-width: 980px;">
        <!-- 1. General Notice & Educational Boundary -->
        <div class="card" style="border-left: 4px solid var(--accent-amber); background: rgba(245, 158, 11, 0.03);">
          <h2 style="font-size: 18px; font-weight: 700; color: var(--accent-amber); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🛡️</span> General Notice & Educational Boundary
          </h2>
          <p style="font-size: 14px; color: var(--text-primary); line-height: 1.8; margin-bottom: 12px; font-weight: 500;">
            QuantPits Arena is provided solely for <b>research, educational, experimental, and informational purposes</b>.
          </p>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Nothing presented on this website constitutes investment advice, a recommendation, solicitation, endorsement, or offer to buy or sell any security, financial instrument, investment strategy, or financial product.
          </p>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Content made available through QuantPits Arena — including interactive visualizations, model outputs, strategy leaderboards, downloadable data, research notes, experiment reports, and historical records — should not be construed as personalized financial, investment, legal, tax, or professional advice.
          </p>
          <p style="font-size: 13px; color: var(--text-muted); line-height: 1.7; margin-bottom: 0;">
            No fiduciary, advisory, brokerage, client, or similar professional relationship is created through access to or use of this website.
          </p>
        </div>

        <!-- 2. Nature of Results & Past Performance -->
        <div class="card" style="border-left: 4px solid var(--accent-cyan);">
          <h3 style="font-size: 17px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🔬</span> Nature of Results & Past Performance
          </h3>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Results presented on QuantPits Arena may include:
          </p>
          <ul style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-left: 20px; margin-bottom: 16px;">
            <li>historical live performance;</li>
            <li>delayed production records;</li>
            <li>shadow-trading results;</li>
            <li>simulated or backtested results;</li>
            <li>frozen-artifact replay experiments;</li>
            <li>counterfactual decision trials;</li>
            <li>randomized benchmark simulations;</li>
            <li>exploratory stress-test variants.</li>
          </ul>
          <p style="font-size: 13px; color: var(--text-primary); line-height: 1.7; margin-bottom: 14px; font-weight: 500;">
            Each result should be interpreted only within the methodology, evaluation period, assumptions, and experimental boundaries stated for that specific experiment.
          </p>

          <div style="background: rgba(0,0,0,0.25); padding: 16px; border-radius: var(--radius-sm); display: flex; flex-direction: column; gap: 12px; font-size: 13px; line-height: 1.7; color: var(--text-secondary);">
            <div>
              <strong style="color: var(--text-primary);">No Guarantee of Future Results:</strong>
              <div>Historical, live, out-of-sample, simulated, counterfactual, or shadow-trading performance does not guarantee or predict future investment results.</div>
            </div>
            <div>
              <strong style="color: var(--text-primary);">Execution Approximations:</strong>
              <div>Simulations may rely on predefined transaction-cost assumptions, 100-share trading-lot rounding, finite capital constraints, simplified liquidity assumptions, and other execution approximations. Actual market execution may differ materially.</div>
            </div>
            <div>
              <strong style="color: var(--text-primary);">Counterfactual and Experimental Variants:</strong>
              <div>Counterfactual decision trials, animal-policy stress tests, frozen-model replays, randomized agents, and similar variants are experimental research constructs. They are not proposed trading strategies or recommendations for capital deployment.</div>
            </div>
            <div>
              <strong style="color: var(--text-primary);">Leaderboard Interpretation:</strong>
              <div>Leaderboard position describes performance within a particular experimental configuration and observation window only. It does not represent investment suitability, expected profitability, or a recommendation to adopt the displayed model or policy.</div>
            </div>
          </div>
        </div>

        <!-- 3. Research Integrity & Statistical Interpretation -->
        <div class="card" style="border-left: 4px solid var(--accent-indigo);">
          <h3 style="font-size: 17px; font-weight: 700; color: var(--accent-indigo); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🧪</span> Research Integrity & Statistical Interpretation
          </h3>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            QuantPits Arena contains both confirmatory and exploratory research. Some experiments involve historically selected models, recovered artifacts, multiple policy variants, repeated comparisons, or post-hoc research questions. Accordingly, raw rankings, percentiles, empirical p-values, and other statistical measures should not automatically be interpreted as independent confirmatory evidence.
          </p>
          <div style="background: rgba(255, 255, 255, 0.02); padding: 14px 16px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); font-size: 13px; color: var(--text-secondary); line-height: 1.7;">
            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">Unless explicitly stated otherwise:</div>
            <ul style="margin: 0; padding-left: 18px;">
              <li>model inclusion may be historically or experimentally selected;</li>
              <li>multiple comparisons may be present;</li>
              <li>short evaluation windows may materially increase uncertainty;</li>
              <li>statistical significance in one experiment does not establish persistent investment alpha;</li>
              <li>exploratory findings should be treated as hypothesis-generating rather than definitive evidence.</li>
            </ul>
            <p style="margin-top: 10px; margin-bottom: 0; color: var(--text-muted); font-size: 12px;">
              Matched random-ranking agents and other null benchmarks are intended to characterize experimental reference distributions, not to certify investment performance.
            </p>
          </div>
        </div>

        <!-- 4. Market Data Latency & Copy-Trading Policy -->
        <div class="card" style="border-left: 4px solid var(--accent-purple);">
          <h3 style="font-size: 17px; font-weight: 700; color: var(--accent-purple); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>⏱️</span> Market Data Latency & Copy-Trading Policy
          </h3>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Market, model, and portfolio information displayed on QuantPits Arena is intentionally published with an approximate delay of <b>one week</b>.
          </p>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            This delay is a publication policy, <b>not a representation that the information is incapable of being acted upon</b>. Certain research variants may themselves study delayed execution, stale signals, or intentionally deferred portfolio actions.
          </p>
          <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: var(--radius-sm); padding: 12px 16px; font-size: 13px; line-height: 1.7; color: var(--text-secondary);">
            <p style="margin: 0 0 8px 0; font-weight: 600; color: var(--accent-rose);">
              QuantPits Arena is not a real-time or delayed trading-signal service, copy-trading service, portfolio-management service, or trade-replication system.
            </p>
            <p style="margin: 0;">
              Displayed positions, rankings, model outputs, orders, portfolio states, or experimental policies should not be treated as instructions to reproduce, mirror, synchronize, or otherwise base actual securities transactions upon, regardless of their publication delay or the execution timing used by the experiment itself.
            </p>
          </div>
        </div>

        <!-- 5. Research Subject Status & Absence of Endorsement -->
        <div class="card" style="border-left: 4px solid var(--accent-cyan);">
          <h3 style="font-size: 17px; font-weight: 700; color: var(--accent-cyan); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>🧬</span> Research Subject Status & Absence of Endorsement
          </h3>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            All models, strategies, portfolio policies, benchmarks, experimental animals, randomized agents, and historical artifacts displayed on QuantPits Arena are presented as <b>research subjects</b>.
          </p>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            Inclusion in an experiment, continued publication, historical profitability, leaderboard ranking, statistical percentile, or survival in the Arena does not constitute endorsement or imply expected future profitability.
          </p>
          <p style="font-size: 12px; color: var(--text-muted); line-height: 1.6; margin: 0;">
            References to individual securities, benchmark indices such as CSI 300 / SH000300, quantitative frameworks, software packages, model architectures, or third-party services are made solely for research attribution, experimental reproducibility, historical description, or academic comparison.
          </p>
        </div>

        <!-- 6. Data Quality & Experimental Limitations -->
        <div class="card" style="border-left: 4px solid var(--accent-amber);">
          <h3 style="font-size: 17px; font-weight: 700; color: var(--accent-amber); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>📊</span> Data Quality & Experimental Limitations
          </h3>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 12px;">
            QuantPits Arena attempts to preserve reproducibility and methodological transparency, but research data and reconstructed historical experiments may remain subject to:
          </p>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 16px; font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">
            <div>• missing or incomplete historical artifacts;</div>
            <div>• software defects;</div>
            <div>• data revisions;</div>
            <div>• historical infrastructure changes;</div>
            <div>• corporate-action adjustments;</div>
            <div>• unavailable runtime records;</div>
            <div>• model-version uncertainty;</div>
            <div>• survivorship or recoverability limitations;</div>
            <div style="grid-column: span 2;">• differences between simulated and actual execution.</div>
          </div>
          <p style="font-size: 12px; color: var(--text-muted); line-height: 1.6; margin: 0;">
            Where known, material limitations are disclosed in the relevant experiment documentation. No representation is made that all information is complete, error-free, continuously available, or suitable for investment use.
          </p>
        </div>

        <!-- 7. Inherent Risk of Loss -->
        <div class="card" style="border-left: 4px solid var(--accent-rose); background: rgba(244, 63, 94, 0.03);">
          <h3 style="font-size: 17px; font-weight: 700; color: var(--accent-rose); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
            <span>⚠️</span> Inherent Risk of Loss
          </h3>
          <p style="font-size: 14px; font-weight: 600; color: var(--text-primary); line-height: 1.7; margin-bottom: 10px;">
            Investing and trading involve substantial risk, including the possible loss of principal.
          </p>
          <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 10px;">
            Quantitative and systematic strategies may be affected by, among other factors:
          </p>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px 16px; font-size: 12px; color: var(--text-secondary); margin-bottom: 14px;">
            <div>• market turbulence;</div>
            <div>• structural liquidity changes;</div>
            <div>• regime changes;</div>
            <div>• transaction costs;</div>
            <div>• model instability;</div>
            <div>• implementation defects;</div>
            <div>• estimation error;</div>
            <div>• data errors;</div>
            <div>• infrastructure failures;</div>
            <div>• unexpected model & rule interactions.</div>
          </div>
          <p style="font-size: 13px; color: var(--text-primary); line-height: 1.7; margin: 0; font-weight: 500;">
            Users considering actual investment decisions should conduct their own independent analysis and, where appropriate, consult qualified financial, legal, tax, or other professional advisers.
          </p>
        </div>

        <!-- 8. Final Research Boundary -->
        <div class="card" style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(244, 63, 94, 0.08)); border: 1px solid rgba(245, 158, 11, 0.3); text-align: center; padding: 24px;">
          <h3 style="font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: var(--accent-amber); margin-bottom: 12px;">
            Final Research Boundary
          </h3>
          <div style="font-size: 15px; font-weight: 500; color: var(--text-primary); line-height: 1.9; margin: 0;">
            QuantPits Arena is a research testbed.<br>
            It studies models.<br>
            It studies portfolio policies.<br>
            It studies historical decisions.<br>
            It studies failures.<br>
            It occasionally studies monkeys.<br>
            <strong style="font-size: 17px; font-weight: 800; color: var(--accent-rose); display: block; margin-top: 6px;">
              It does not tell you what to buy.
            </strong>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div style="display: flex; gap: 12px; justify-content: flex-start; margin-top: 4px;">
          <button class="btn btn-secondary" onclick="window.appRouter.navigate('intro')">
            &larr; Back to Exhibition
          </button>
          <button class="btn btn-primary" onclick="window.appRouter.navigate('methodology')">
            Read Methodology &amp; Axioms &rarr;
          </button>
        </div>
      </div>
    `;
  }
};
