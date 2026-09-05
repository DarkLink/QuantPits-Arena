/**
 * web/js/views/discussion.js
 * ==========================
 * Community Discussion & Research Feedback View
 * Powered by Giscus (GitHub Discussions #2)
 */

window.DiscussionView = {
  isGiscusLoaded: false,

  render(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    // Render structural container if not already initialized
    if (!this.isGiscusLoaded) {
      el.innerHTML = `
        <div class="doc-page-container">
          <div class="view-header" style="text-align: center; margin-bottom: 1.75rem;">
            <div class="hero-tag" style="margin-bottom: 0.75rem;">
              <span>💬 Open Peer Review &amp; Community Feedback</span>
            </div>
            <h1 class="view-title" style="font-size: 2.2rem; margin-bottom: 0.5rem;">Arena Research Discussion</h1>
            <p class="view-subtitle" style="max-width: 680px; margin: 0 auto; font-size: 0.95rem; color: var(--text-secondary);">
              Discuss empirical model durability, propose new execution animal handlers, or share observations on regime shifts. Comments are synchronized with GitHub Discussions.
            </p>
          </div>

          <!-- Discussion Info & GitHub Direct Link Banner -->
          <div class="discussion-info-banner">
            <div class="info-text">
              <strong>GitHub Discussions Integration:</strong> All comments and replies here are directly linked to 
              <span style="color: var(--brand-cyan); font-family: var(--font-mono);">DarkLink/QuantPits-Arena</span> discussion thread 
              <span style="color: var(--brand-purple); font-weight: 700;">#2</span>.
            </div>
            <a href="https://github.com/DarkLink/QuantPits-Arena/discussions/2" target="_blank" rel="noopener" class="discussion-github-link">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>View Thread on GitHub &rarr;</span>
            </a>
          </div>

          <!-- Discussion Community Standards -->
          <div class="card" style="margin-bottom: 1.5rem; background: rgba(15, 23, 42, 0.45); padding: 1rem 1.25rem; font-size: 0.85rem; color: var(--text-tertiary); display: flex; gap: 1.5rem; flex-wrap: wrap;">
            <div>📌 <strong>Empirical Focus:</strong> Discussions should center on models, execution handlers, and econometric methodology.</div>
            <div>🛡️ <strong>Zero-Leakage:</strong> Never post real production cash numbers, account balances, or proprietary trade secrets.</div>
          </div>

          <!-- Giscus Frame Card Container -->
          <div class="discussion-frame-card">
            <div id="giscus-embed-target" class="giscus"></div>
          </div>
        </div>
      `;

      this.injectGiscusScript();
    } else {
      // If already loaded, synchronize theme
      this.syncTheme();
    }
  },

  injectGiscusScript() {
    const target = document.getElementById("giscus-embed-target");
    if (!target) return;

    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const giscusTheme = currentTheme === "light" ? "light" : "transparent_dark";

    const script = document.createElement("script");
    script.src = "https://giscus.app/client.js";
    script.setAttribute("data-repo", "DarkLink/QuantPits-Arena");
    script.setAttribute("data-repo-id", "R_kgDOUOAkSg");
    script.setAttribute("data-mapping", "number");
    script.setAttribute("data-term", "2");
    script.setAttribute("data-reactions-enabled", "1");
    script.setAttribute("data-emit-metadata", "0");
    script.setAttribute("data-input-position", "top");
    script.setAttribute("data-theme", giscusTheme);
    script.setAttribute("data-lang", "en");
    script.setAttribute("data-loading", "lazy");
    script.crossOrigin = "anonymous";
    script.async = true;

    target.appendChild(script);
    this.isGiscusLoaded = true;
  },

  syncTheme() {
    const iframe = document.querySelector("iframe.giscus-frame");
    if (!iframe) return;

    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const giscusTheme = currentTheme === "light" ? "light" : "transparent_dark";

    iframe.contentWindow.postMessage(
      {
        giscus: {
          setConfig: {
            theme: giscusTheme
          }
        }
      },
      "https://giscus.app"
    );
  }
};
