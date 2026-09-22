/**
 * web/js/components/tooltip_manager.js
 * ===================================
 * Global Interactive Tooltip Manager
 * Features:
 *   - Standard delayed hover popover (200ms open, 150ms close grace period)
 *   - Viewport collision detection (auto top/bottom flip, edge clamping)
 *   - Glassmorphic styling with category badges & plain-English explanations
 *   - Deep link into the Picture-in-Picture Spec Drawer ("📖 View in Drawer")
 */

window.ArenaTooltip = {
  container: null,
  showTimer: null,
  hideTimer: null,
  currentAnchor: null,
  isHoveringTooltip: false,

  init() {
    if (this.container) return;

    let popover = document.getElementById("arena-tooltip-popover");
    if (!popover) {
      popover = document.createElement("div");
      popover.id = "arena-tooltip-popover";
      popover.className = "arena-tooltip-popover";
      popover.setAttribute("role", "tooltip");
      popover.style.display = "none";
      document.body.appendChild(popover);
    }
    this.container = popover;

    // Keep tooltip visible when mouse moves over the tooltip itself
    this.container.addEventListener("mouseenter", () => {
      this.isHoveringTooltip = true;
      clearTimeout(this.hideTimer);
    });

    this.container.addEventListener("mouseleave", () => {
      this.isHoveringTooltip = false;
      this.scheduleHide(100);
    });

    // Delegate global mouseover/mouseout on document
    document.addEventListener("mouseover", (e) => {
      const target = e.target.closest(".arena-glossary-term, [data-tooltip-term]");
      if (target) {
        clearTimeout(this.hideTimer);
        this.scheduleShow(target);
      }
    });

    document.addEventListener("mouseout", (e) => {
      const target = e.target.closest(".arena-glossary-term, [data-tooltip-term]");
      if (target && target === this.currentAnchor) {
        this.scheduleHide(150);
      }
    });

    // Click to immediately show/toggle tooltip (ideal for mobile and click-to-pin)
    document.addEventListener("click", (e) => {
      const target = e.target.closest(".arena-glossary-term, [data-tooltip-term]");
      if (target) {
        clearTimeout(this.hideTimer);
        clearTimeout(this.showTimer);
        if (this.currentAnchor === target && this.container.style.display !== "none") {
          this.hide();
        } else {
          this.currentAnchor = target;
          this.render(target);
        }
      } else if (!e.target.closest(".arena-tooltip-popover, .chart-spec-pill, .arena-drawer-fab")) {
        this.hide();
      }
    });

    // Close tooltip on global scroll or Escape key
    window.addEventListener("scroll", () => this.hide(), { passive: true });
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.hide();
    });
  },

  scheduleShow(el) {
    if (this.currentAnchor === el && this.container.style.display !== "none") return;
    clearTimeout(this.showTimer);
    this.currentAnchor = el;

    this.showTimer = setTimeout(() => {
      if (this.currentAnchor === el) {
        this.render(el);
      }
    }, 200); // 200ms delay to avoid trigger when swiftly brushing past
  },

  scheduleHide(delay = 150) {
    clearTimeout(this.showTimer);
    clearTimeout(this.hideTimer);
    this.hideTimer = setTimeout(() => {
      if (!this.isHoveringTooltip) {
        this.hide();
      }
    }, delay);
  },

  hide() {
    clearTimeout(this.showTimer);
    clearTimeout(this.hideTimer);
    if (this.container) {
      this.container.style.display = "none";
      this.container.classList.remove("visible");
    }
    this.currentAnchor = null;
    this.isHoveringTooltip = false;
  },

  render(el) {
    const termKey = el.getAttribute("data-tooltip-term") || el.getAttribute("data-term") || el.textContent;
    const termData = window.ArenaGlossaryService ? window.ArenaGlossaryService.lookup(termKey) : null;

    if (!termData) {
      // Fallback simple title attribute if no dictionary match
      const fallbackTitle = el.getAttribute("title");
      if (!fallbackTitle) return;
      this.container.innerHTML = `
        <div class="tooltip-body">${fallbackTitle}</div>
      `;
      this.container.style.display = "block";
      this.position(el);
      requestAnimationFrame(() => this.container.classList.add("visible"));
      return;
    }

    if (termData.isComposite) {
      this.container.innerHTML = `
        <div class="tooltip-header">
          <div class="tooltip-title-wrap">
            <span class="tooltip-category-badge" style="color: var(--brand-cyan); border-color: rgba(56, 189, 248, 0.3); background: rgba(56, 189, 248, 0.1);">
              🧬 Model × 🐾 Handler
            </span>
            <strong class="tooltip-title">${termData.name}</strong>
          </div>
          <span class="tooltip-tagline">${termData.tagline}</span>
        </div>
        <div class="tooltip-body" style="font-size: 0.82rem; line-height: 1.5; margin-bottom: 6px;">
          <div style="margin-bottom: 6px; padding: 6px 8px; background: rgba(56, 189, 248, 0.06); border-left: 3px solid var(--brand-cyan); border-radius: 3px;">
            <div style="font-weight: 700; color: var(--brand-cyan); font-size: 0.78rem; text-transform: uppercase;">🧬 Model: ${termData.model.name}</div>
            <div style="color: var(--text-secondary); margin-top: 2px;">${termData.model.tooltip}</div>
          </div>
          <div style="padding: 6px 8px; background: rgba(168, 85, 247, 0.06); border-left: 3px solid var(--accent-purple); border-radius: 3px;">
            <div style="font-weight: 700; color: var(--accent-purple); font-size: 0.78rem; text-transform: uppercase;">🐾 Execution: ${termData.animal.name}</div>
            <div style="color: var(--text-secondary); margin-top: 2px;">${termData.animal.tooltip}</div>
          </div>
        </div>
        <div class="tooltip-footer" style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button type="button" class="tooltip-drawer-link" onclick="window.ArenaSpecDrawer && window.ArenaSpecDrawer.openTerm('${termData.modelId}')">
            <span>🧬 Model Spec</span>
          </button>
          <button type="button" class="tooltip-drawer-link" onclick="window.ArenaSpecDrawer && window.ArenaSpecDrawer.openTerm('${termData.animalId}')">
            <span>🐾 Zoo Spec</span>
          </button>
          <button type="button" class="tooltip-drawer-link" style="margin-left: auto;" onclick="window.appRouter && window.appRouter.navigate('path-detail', { pathId: '${termData.id}' })">
            <span>📊 Path Detail &rarr;</span>
          </button>
        </div>
      `;
    } else {
      const categoryColors = {
        "Contestants": "var(--brand-cyan)",
        "Zoo Animals": "var(--accent-purple)",
        "Benchmarks": "#fbbf24",
        "Metrics": "#34d399",
        "Zoo Mechanics": "#f472b6"
      };
      const catColor = categoryColors[termData.category] || "var(--brand-cyan)";

      this.container.innerHTML = `
        <div class="tooltip-header">
          <div class="tooltip-title-wrap">
            <span class="tooltip-category-badge" style="color: ${catColor}; border-color: ${catColor}40; background: ${catColor}15;">
              ${termData.category}
            </span>
            <strong class="tooltip-title">${termData.name || termData.term}</strong>
          </div>
          ${termData.tagline ? `<span class="tooltip-tagline">${termData.tagline}</span>` : ''}
        </div>
        <div class="tooltip-body">
          ${termData.tooltip || termData.details}
        </div>
        ${termData.details && termData.details !== termData.tooltip ? `
          <div class="tooltip-details">${termData.details}</div>
        ` : ''}
        <div class="tooltip-footer">
          <button type="button" class="tooltip-drawer-link" onclick="window.ArenaSpecDrawer && window.ArenaSpecDrawer.openTerm('${termData.id || termData.term}')">
            <span>📖 Inspect in Spec Drawer &rarr;</span>
          </button>
        </div>
      `;
    }

    this.container.style.display = "block";
    this.position(el);
    // Trigger transition
    requestAnimationFrame(() => {
      this.container.classList.add("visible");
    });
  },

  position(anchorEl) {
    const pop = this.container;
    const rect = anchorEl.getBoundingClientRect();
    const popRect = pop.getBoundingClientRect();

    const padding = 10;
    const scrollX = window.scrollX || window.pageXOffset;
    const scrollY = window.scrollY || window.pageYOffset;

    // Prefer placing above the anchor
    let top = rect.top + scrollY - popRect.height - 8;
    let placement = "top";

    // If clipping at the top of the viewport, place below
    if (rect.top - popRect.height - 8 < 10) {
      top = rect.bottom + scrollY + 8;
      placement = "bottom";
    }

    // Align horizontally centered with anchor
    let left = rect.left + scrollX + (rect.width / 2) - (popRect.width / 2);

    // Boundary clamping
    const maxLeft = window.innerWidth + scrollX - popRect.width - padding;
    const minLeft = scrollX + padding;
    if (left < minLeft) left = minLeft;
    if (left > maxLeft) left = maxLeft;

    pop.style.top = `${top}px`;
    pop.style.left = `${left}px`;
    pop.setAttribute("data-placement", placement);
  }
};
