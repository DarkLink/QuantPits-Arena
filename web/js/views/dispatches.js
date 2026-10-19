/**
 * web/js/views/dispatches.js
 * ==========================
 * Tournament Dispatches & Market Climate View
 * Decoupled into Executive Status (README Layer) & Episodic Narrative (Reader Layer).
 */

window.DispatchesView = {
  currentEpisode: null,

  render(containerId, params = {}) {
    const el = document.getElementById(containerId);
    if (!el) return;
    this.isCurrentRender = window.ArenaCharts.beginViewRender(el);
    const isCurrent = this.isCurrentRender;

    const seasonMeta = window.arenaAdapter ? window.arenaAdapter.getCurrentSeasonMeta() : {};
    const dispatches = window.arenaAdapter ? window.arenaAdapter.getDispatchesData() : null;

    // Fallback if no dispatches object exists
    const exec = dispatches?.executive || {
      tag: "🏆 Official Released Standing",
      badge: "Active",
      title: "Tournament Standing & Baseline",
      window_label: seasonMeta.period || "Current Season Window",
      nature_label: "Empirical strategy evaluation under execution constraints.",
      leader_summary: "Evaluation active across all animal variants."
    };

    const climate = dispatches?.climate || {
      tag: "🌪️ Market Climate Report",
      status_badge: "Active",
      title: "Cross-Market Volatility & Execution Dynamics",
      summary: "Tracking market liquidity, factor dispersion, and execution friction.",
      bullets: [
        "Active monitoring of cross-sectional return dispersion.",
        "Zero alpha leakage under cryptographic verification."
      ],
      decrypt_label: "Standard Weekly Cycle"
    };

    const episodes = dispatches?.episodes || [];

    // Determine latest released episode (or fallback to the last entry in chronological list)
    const latestEpisode = episodes.length > 0 
      ? (episodes.slice().reverse().find(e => e.badge === "Released") || episodes[episodes.length - 1])
      : null;
    const latestEpId = latestEpisode?.id || null;

    // Ensure valid current episode:
    // If params.episode is provided and valid, honor it; otherwise default to the latest episode!
    if (params.episode && episodes.some(e => e.id === params.episode)) {
      this.currentEpisode = params.episode;
    } else {
      this.currentEpisode = latestEpId;
    }

    el.innerHTML = `
      <div class="doc-page-container">
        <!-- View Header -->
        <div class="view-header document-header">
          <div class="hero-tag" style="margin-bottom: 0.75rem;">
            <span>📜 ${seasonMeta.title || "QuantPits Arena"} Dispatches &amp; Market Climate</span>
          </div>
          <h1 class="view-title">Arena Dispatches</h1>
          <p class="view-subtitle" style="max-width: 720px; margin: 0 auto; font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6;">
            Empirical chronicles of quantitative alpha models facing execution zoo frictions, regime shifts, and the Monte Carlo Null Court.
          </p>
        </div>

        <!-- Layer 1: Executive Status & Market Climate (The README Layer) -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 1.25rem; margin-bottom: 2rem;">
          
          <!-- Card 1: Official Baseline Status -->
          <div class="card" style="border-left: 4px solid var(--brand-cyan); background: var(--bg-surface); padding: 1.25rem 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
              <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand-cyan); font-weight: 700;">
                ${exec.tag || "🏆 Official Baseline"}
              </span>
              <span class="badge badge-positive" style="font-size: 0.75rem;">
                ${exec.badge || "Active"}
              </span>
            </div>
            <h3 style="font-size: 1.15rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
              ${exec.title}
            </h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0.75rem;">
              <strong>Window:</strong> ${exec.window_label}<br>
              <strong>Nature:</strong> ${exec.nature_label}<br>
              <strong>Status:</strong> ${exec.leader_summary}
            </p>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              ${latestEpId ? `
              <button class="btn btn-sm btn-primary" onclick="window.DispatchesView.selectEpisode('${latestEpId}', true)" style="font-size: 0.8rem; padding: 4px 10px;">
                <span>📖 Read Latest Dispatch &rarr;</span>
              </button>
              ` : ''}
              <a href="#leaderboard" class="btn btn-sm btn-secondary" style="font-size: 0.8rem; padding: 4px 10px; text-decoration: none;">
                <span>🏆 View Leaderboard</span>
              </a>
            </div>
          </div>

          <!-- Card 2: Weekly Market Climate Report (Public facts, zero alpha leak) -->
          <div class="card" style="border-left: 4px solid var(--accent-warning); background: var(--bg-surface); padding: 1.25rem 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
              <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent-warning); font-weight: 700;">
                ${climate.tag || "🌪️ Market Climate"}
              </span>
              <span class="badge badge-warning" style="font-size: 0.75rem;">
                ${climate.status_badge || "Active"}
              </span>
            </div>
            <h3 style="font-size: 1.15rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
              ${climate.title}
            </h3>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; margin-bottom: 0.75rem;">
              <em>${climate.summary}</em>
            </p>
            <ul style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; margin: 0 0 0.75rem 1.25rem; padding: 0;">
              ${(climate.bullets || []).map(b => `<li>${b}</li>`).join("")}
            </ul>
            <div style="font-size: 0.78rem; color: var(--accent-warning); display: flex; align-items: center; gap: 6px;">
              <span>⏳</span> <strong>${climate.decrypt_label || "Continuous Monitoring"}</strong>
            </div>
          </div>
        </div>

        <!-- Layer 2: Episodic Reader Container -->
        <div class="card" style="background: var(--bg-surface); border: 1px solid var(--border-subtle); padding: 1.75rem; border-radius: var(--radius-md);">
          
          <!-- Dispatch Navigation Tabs -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 1rem; margin-bottom: 1.5rem;">
            
            <!-- Episode Tabs -->
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;" id="dispatch-tabs-container">
              ${episodes.map(ep => `
                <button id="tab-btn-${ep.id}" class="btn btn-sm ${this.currentEpisode === ep.id ? 'btn-primary' : 'btn-secondary'}" onclick="window.DispatchesView.selectEpisode('${ep.id}')">
                  <span>${ep.tab_label}</span>
                  ${ep.badge ? `<span style="font-size: 10px; opacity: 0.8; margin-left: 4px;">(${ep.badge})</span>` : ''}
                </button>
              `).join("")}
            </div>

            <div style="font-size: 0.8rem; color: var(--text-tertiary);">
              Official Tournament Log · ${seasonMeta.short_title || "Arena"}
            </div>
          </div>

          <!-- Dynamic Episode Content Area -->
          <div id="dispatch-article-body">
            ${this.renderArticleContent()}
          </div>

        </div>
      </div>
    `;

    // Post process math and triggers on initial render
    const initialBody = document.getElementById("dispatch-article-body");
    if (initialBody) this.postProcessArticle(initialBody);

    // Trigger async direct file loading if available
    setTimeout(() => {
      if (!isCurrent()) return;
      this.loadArticle(this.currentEpisode);
    }, 0);
  },

  selectEpisode(epId, shouldScroll = false) {
    this.currentEpisode = epId;
    this.loadArticle(epId);
    
    // Update button states dynamically
    const container = document.getElementById("dispatch-tabs-container");
    if (container) {
      const btns = container.querySelectorAll("button");
      btns.forEach(btn => {
        if (btn.id === `tab-btn-${epId}`) {
          btn.className = "btn btn-sm btn-primary";
        } else {
          btn.className = "btn btn-sm btn-secondary";
        }
      });
    }

    // Synchronize route hash with episode parameter without reloading page
    try {
      const hashParts = (window.location.hash || "#dispatches").split("?");
      const baseHash = hashParts[0];
      window.history.replaceState(null, "", `${baseHash}?episode=${epId}`);
    } catch (e) {
      // Fallback for older browsers
    }

    if (shouldScroll) {
      const articleEl = document.getElementById("dispatch-article-body");
      if (articleEl) {
        articleEl.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
  },

  decorateArticle(html) {
    if (!html) return "";

    // Comprehensive term regex: matches longest candidates first
    const regex = /\b(Ghost\s+Taotie|Taotie|Null\s+Court|Matched\s+Monkeys|random\s+monkeys|matched\s+null\s+colony|CSI\s*300|CSI300|CONTESTANT_[A-Z]+_[a-z0-9-]+|CONTESTANT_[A-Z]+|eagle-[0-9-]+|rabbit-[0-9-]+|sloth-[0-9-]+|snail-[0-9-]+|meerkat-[0-9-]+|turtle-[0-9-]+|whale-shark|whale\s+shark|koala|robot|Sharpe\s+ratio|Sharpe|maximum\s+drawdown|Max\s+Drawdown|MDD|empirical\s+p-value|p-value|empirical\s+percentile)\b/gi;

    const temp = document.createElement("div");
    temp.innerHTML = html;

    const walk = (node) => {
      // Never process inside pre blocks, buttons, scripts, or existing glossary terms
      if (node.nodeType === Node.ELEMENT_NODE) {
        const tag = node.tagName.toLowerCase();
        if (tag === "pre" || tag === "button" || tag === "script" || tag === "style") return;
        if (node.classList.contains("arena-glossary-term")) return;
        Array.from(node.childNodes).forEach(walk);
      } else if (node.nodeType === Node.TEXT_NODE) {
        const text = node.nodeValue;
        if (!text || text.trim().length < 3) return;

        if (regex.test(text)) {
          regex.lastIndex = 0; // Reset regex state
          const newHtml = text.replace(regex, (match) => {
            let termKey = match;
            const lower = match.toLowerCase();
            if (lower.includes("taotie")) {
              termKey = lower.includes("ghost") ? "ghost_taotie" : "taotie";
            } else if (lower.includes("null court")) {
              termKey = "null_court";
            } else if (lower.includes("monkey") || lower.includes("colony")) {
              termKey = "monkeys";
            } else if (lower.includes("csi")) {
              termKey = "market";
            } else if (lower.includes("sharpe")) {
              termKey = "sharpe_ratio";
            } else if (lower.includes("drawdown") || lower === "mdd") {
              termKey = "max_drawdown_pct";
            } else if (lower.includes("p-value") || lower.includes("percentile")) {
              termKey = "empirical_p_value";
            }
            return `<span class="arena-glossary-term" data-tooltip-term="${termKey}">${match}</span>`;
          });

          const span = document.createElement("span");
          span.innerHTML = newHtml;
          node.parentNode.replaceChild(span, node);
        }
      }
    };

    walk(temp);
    temp.querySelectorAll('table').forEach(table => {
      const wrapper = document.createElement('div');
      wrapper.className = 'table-wrapper';
      table.classList.add('data-table');
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    });
    return temp.innerHTML;
  },

  renderMathFallback(html) {
    if (!html) return "";
    return html
      .replace(/\${1,2}\s*(?:\\{1,2})to\s*\${1,2}/gi, ' &rarr; ')
      .replace(/\${1,2}\s*(?:\\{1,2})approx\s*\${1,2}/gi, ' &asymp; ')
      .replace(/\${1,2}\s*(?:\\{1,2})times\s*\${1,2}/gi, ' &times; ')
      .replace(/\${1,2}\s*(?:\\{1,2})pm\s*\${1,2}/gi, ' &plusmn; ')
      .replace(/\${1,2}\s*(?:\\{1,2})ge(?:q)?\s*\${1,2}/gi, ' &ge; ')
      .replace(/\${1,2}\s*(?:\\{1,2})le(?:q)?\s*\${1,2}/gi, ' &le; ')
      .replace(/\${1,2}\s*(?:\\{1,2})neq\s*\${1,2}/gi, ' &ne; ');
  },

  wrapArticle(activeEp, innerHtml) {
    const mathCleaned = this.renderMathFallback(innerHtml);
    const decoratedHtml = this.decorateArticle(mathCleaned);
    return `
      <article class="prose" style="max-width: 820px; margin: 0 auto; color: var(--text-secondary); line-height: 1.75; font-size: 0.95rem;">
        <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
          <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem;">
            <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: var(--brand-cyan); border: 1px solid rgba(56, 189, 248, 0.3);">
              ${activeEp?.badge || "Released"}
            </span>
            <span style="font-size: 0.8rem; color: var(--text-tertiary);">
              Date: ${activeEp?.date || "2026"} · ${activeEp?.read_time || "6 min read"}
            </span>
          </div>
          <h2 style="font-size: 1.9rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
            ${activeEp?.title || "Tournament Chronicle"}
          </h2>
          ${activeEp?.summary ? `
            <p style="font-size: 0.95rem; color: var(--text-muted); margin-top: 0.5rem; font-style: italic;">
              ${activeEp.summary}
            </p>
          ` : ''}
        </div>
        ${decoratedHtml}
        <div style="margin-top: 2.5rem; padding-top: 1.25rem; border-top: 1px solid var(--border-subtle); text-align: center; font-size: 0.85rem; color: var(--text-tertiary);">
          🏛️ <em>QuantPits Arena Official Tournament Log</em>
        </div>
      </article>
    `;
  },

  async loadArticle(epId) {
    const bodyEl = document.getElementById("dispatch-article-body");
    if (!bodyEl) return;
    const adapter = window.arenaAdapter;
    const request = this.articleRequest = (this.articleRequest || 0) + 1;
    const currentRender = this.isCurrentRender;
    const isCurrent = () => this.articleRequest === request && this.currentEpisode === epId &&
      window.arenaAdapter === adapter && (!currentRender || currentRender());

    const dispatches = window.arenaAdapter ? window.arenaAdapter.getDispatchesData() : null;
    const episodes = dispatches?.episodes || [];
    const activeEp = episodes.find(e => e.id === epId);

    // If file is specified and marked parser is available, fetch and render directly!
    if (activeEp?.file && window.marked) {
      try {
        const res = await fetch(activeEp.file);
        if (res.ok) {
          const md = await res.text();
          if (!isCurrent()) return;
          bodyEl.innerHTML = this.wrapArticle(activeEp, window.marked.parse(md));
          this.postProcessArticle(bodyEl);
          return;
        }
      } catch (err) {
        console.warn("Direct file fetch failed, falling back to embedded content:", err);
      }
    }

    // Fallback to synchronous renderer
    if (!isCurrent()) return;
    bodyEl.innerHTML = this.renderArticleContent();
    this.postProcessArticle(bodyEl);
  },

  postProcessArticle(container) {
    if (!container) return;

    // 1. Fallback regex replacement for math arrows and basic symbols
    const walkTextForMath = (node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        let val = node.nodeValue;
        if (val && /\${1,2}\s*(?:\\{1,2})(?:to|approx|times|pm|ge|le|neq)/i.test(val)) {
          const span = document.createElement("span");
          span.innerHTML = this.renderMathFallback(val);
          node.parentNode.replaceChild(span, node);
        }
      } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() !== "script") {
        Array.from(node.childNodes).forEach(walkTextForMath);
      }
    };
    walkTextForMath(container);

    // 2. Invoke KaTeX auto-renderer if available
    if (window.renderMathInElement) {
      try {
        window.renderMathInElement(container, {
          delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false }
          ],
          throwOnError: false
        });
      } catch (e) {
        console.warn("[Dispatches] KaTeX auto-render warning:", e);
      }
    }
  },

  renderArticleContent() {
    const dispatches = window.arenaAdapter ? window.arenaAdapter.getDispatchesData() : null;
    const episodes = dispatches?.episodes || [];
    const activeEp = episodes.find(e => e.id === this.currentEpisode);

    if (activeEp) {
      if (activeEp.content_html) {
        return this.wrapArticle(activeEp, activeEp.content_html);
      }
      if (activeEp.content_type === "ep08_baseline" || activeEp.id === "ep08") {
        return this.decorateArticle(this.renderMathFallback(this.renderEp08En()));
      }
      if (activeEp.content_type === "ep09_released" || activeEp.id === "ep09") {
        return this.decorateArticle(this.renderMathFallback(this.renderEp09En()));
      }
    }

    if (this.currentEpisode === "ep09") {
      return this.decorateArticle(this.renderMathFallback(this.renderEp09En()));
    }
    if (this.currentEpisode === "ep08") {
      return this.decorateArticle(this.renderMathFallback(this.renderEp08En()));
    }

    return `
      <article class="prose" style="max-width: 820px; margin: 0 auto; color: var(--text-secondary); line-height: 1.75; font-size: 0.95rem;">
        <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
          <h2 style="font-size: 1.9rem; color: var(--text-primary); margin: 0 0 0.5rem 0;">
            ${activeEp?.title || "Season Chronicles"}
          </h2>
          <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0;">
            ${activeEp?.summary || "Official empirical dispatch."}
          </p>
        </div>
        <p>Detailed dispatch chronicle active for this tournament season.</p>
      </article>
    `;
  },

  renderEp08En() {
    return `<div class="card"><h2>Recalculated baseline dispatch</h2><p>The current report belongs to the retrospective repair release. Load the Markdown article for verified results.</p><a href="chronicles/en/episodes_01_08_the_forty_one_day_king.md">Read the current baseline</a></div>`;
  },

  renderEp09Embargoed() {
    return `
      <div style="text-align: center; padding: 3rem 1.5rem; max-width: 680px; margin: 0 auto;">
        
        <div style="width: 72px; height: 72px; border-radius: 50%; background: rgba(245, 158, 11, 0.1); border: 2px solid rgba(245, 158, 11, 0.4); display: flex; align-items: center; justify-content: center; font-size: 2rem; margin: 0 auto 1.5rem auto;">
          🔒
        </div>

        <div class="hero-tag" style="margin-bottom: 0.75rem; background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.3); color: var(--accent-warning);">
          <span>Institutional Embargo Active · Evaluation Cycle Unlocking</span>
        </div>

        <h2 style="font-size: 1.8rem; color: var(--text-primary); margin-bottom: 0.75rem;">
          Episode 09: The September 02 Breadth Shock (Arena Designation: "Black Wednesday")
        </h2>

        <p style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.7; margin-bottom: 1.5rem;">
          The forward trading window from <strong>August 31 to September 04, 2026</strong> (anchored at the August 28 close) has concluded. The completed performance evaluation package was sealed under an SHA-256 cryptographic digest on Saturday, September 05, 2026 for institutional anti-tampering embargo until public reveal on September 11.
        </p>

        <!-- Public Market Climate Summary Box -->
        <div class="card" style="background: var(--bg-subtle); border: 1px solid var(--border-subtle); padding: 1.25rem; text-align: left; margin-bottom: 1.75rem; font-size: 0.88rem; line-height: 1.6;">
          <strong style="color: var(--accent-warning); display: block; margin-bottom: 6px;">
            🌪️ Public Market Climate Overview (Aug 31 – Sep 04, 2026):
          </strong>
          During this 5-day cycle, the broader market experienced what the Arena designates as its "Black Wednesday" intraday breadth shock on September 2. Turnover contracted, and growth-heavy and previously strong segments experienced sharp localized drawdowns.
          <br><br>
          <em>Individual model trajectories and animal handler performance remain cryptographically sealed under institutional embargo.</em>
        </div>

        <div style="background: rgba(56, 189, 248, 0.08); border: 1px dashed var(--brand-cyan); padding: 12px 18px; border-radius: 6px; font-size: 0.85rem; color: var(--brand-cyan); margin-bottom: 1.5rem;">
          ⏳ <strong>Official Public Decryption Date:</strong> Friday, September 11, 2026 at 18:00 UTC+8
        </div>

        <div style="margin-top: 2rem;">
          <button class="btn btn-secondary" onclick="window.DispatchesView.selectEpisode('ep08')">
            <span>&larr; Return to Episodes 01–08 Baseline Dispatch</span>
          </button>
        </div>

      </div>
    `;
  }
};
