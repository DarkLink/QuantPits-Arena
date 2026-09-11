/**
 * web/js/components/charts.js
 * ===========================
 * QuantPits-Arena ECharts Visualization Suite (English Edition)
 * Includes:
 *   1. Return vs. Monkey Percentile Significance Scatter Plot
 *   2. Contestant × Animal Handler Heatmap Matrix
 *   3. Multi-Line Equity Curves with Monkey 90% Confidence Envelope (P05 ~ P95) & Benchmarks (Taotie & CSI 300)
 *   4. Monkey Null Distribution Boxplot with Significance Marker
 *   5. Decision Archaeology Regret Curve & Area Spread
 *   6. Behavioral Fingerprint Analysis Group (Delay, Turnover, Capacity, Polarity, Meerkat)
 *   7. Contestant Multi-Animal Execution Comparison Chart
 */

window.ArenaCharts = {
  getThemeColors() {
    const isDark = document.documentElement.getAttribute("data-theme") !== "light";
    return {
      isDark,
      bg: "transparent",
      textPrimary: isDark ? "#f8fafc" : "#0f172a",
      textSecondary: isDark ? "#94a3b8" : "#475569",
      textMuted: isDark ? "#64748b" : "#94a3b8",
      gridLine: isDark ? "rgba(255, 255, 255, 0.07)" : "rgba(0, 0, 0, 0.08)",
      tooltipBg: isDark ? "rgba(15, 23, 42, 0.92)" : "rgba(255, 255, 255, 0.95)",
      tooltipBorder: isDark ? "rgba(255, 255, 255, 0.15)" : "rgba(0, 0, 0, 0.15)",
      accentBlue: "#38bdf8",
      accentPurple: "#a855f7",
      accentGreen: "#10b981",
      accentRose: "#f43f5e",
      accentAmber: "#f59e0b"
    };
  },

  toggleBenchmark(domId, benchmarkKey, forceState) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const chart = echarts.getInstanceByDom(dom);
    if (!chart) return;
    const opt = chart.getOption();
    if (!opt || !opt.series) return;

    const currentLegend = (opt.legend && opt.legend[0]) || {};
    const selected = Object.assign({}, currentLegend.selected || {});

    opt.series.forEach(s => {
      const sName = s.name || "";
      let match = false;
      if (benchmarkKey === "ghost") {
        match = sName.includes("Ghost");
      } else if (benchmarkKey === "taotie") {
        match = sName.includes("Taotie") && !sName.includes("Ghost");
      } else if (benchmarkKey === "csi300" || benchmarkKey === "market") {
        const mBm = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
        match = sName.includes("CSI 300") || sName.includes("CSI300") || sName.includes("CSI-300") || sName.includes("CSI 1000") || sName.includes("CSI1000") || sName.includes(mBm);
      } else if (benchmarkKey === "monkey") {
        match = sName.includes("Monkey");
      }
      if (match) {
        if (typeof forceState === "boolean") {
          selected[sName] = forceState;
        } else {
          const isVisible = selected[sName] !== false;
          selected[sName] = !isVisible;
        }
      }
    });

    chart.setOption({
      legend: {
        selected: selected
      }
    });
  },

  toggleSeries(domId, seriesName) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const chart = echarts.getInstanceByDom(dom);
    if (!chart) return;
    chart.dispatchAction({
      type: "legendToggleSelect",
      name: seriesName
    });
  },

  /**
   * 1. Return vs Monkey Percentile Significance Scatter Plot
   */
  renderScatter(domId, paths, onPointClick) {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    const tc = this.getThemeColors();

    const data = paths.map(p => {
      const pctRank = p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile !== undefined ? p.monkey_percentile : (p.monkey_percentile_rank || 50));
      const ret = p.total_return_pct;
      const sharpe = Math.max(0.2, p.sharpe_ratio || 0.5);
      return [pctRank, ret, sharpe, p];
    });

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        trigger: "item",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary },
        formatter: (params) => {
          const p = params.data[3];
          const rawPct = p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile !== undefined ? p.monkey_percentile : p.monkey_percentile_rank);
          const pct = window.formatPercentile ? window.formatPercentile(rawPct) : (rawPct !== undefined ? rawPct.toFixed(1) + "%" : "N/A");
          const rawP = p.empirical_p_value !== undefined ? p.empirical_p_value : p.p_value;
          const pVal = window.formatPValue ? window.formatPValue(rawP) : (rawP !== undefined ? rawP.toFixed(4) : "N/A");
          const pLabel = pVal.startsWith("<") ? `p ${pVal}` : `p = ${pVal}`;
          return `
            <div style="font-weight:700; color:#38bdf8; margin-bottom:4px;">${p.path_id}</div>
            <div style="font-size:12px; line-height:1.5;">
              <div>Model: <b>${p.contestant_id}</b> | Handler: <b>${p.animal_id}</b></div>
              <div>Return: <b style="color:${p.total_return_pct >= 0 ? '#10b981' : '#f43f5e'}">${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</b></div>
              <div>Monkey Percentile: <b>${pct}</b> (${pLabel})</div>
              <div>Max Drawdown: <b style="color:#f43f5e;">${p.max_drawdown_pct.toFixed(2)}%</b> | Sharpe: <b>${p.sharpe_ratio}</b></div>
              <div style="margin-top:4px; font-size:11px; color:#94a3b8;">Click bubble to inspect path details</div>
            </div>
          `;
        }
      },
      grid: {
        left: "4%",
        right: "6%",
        top: "10%",
        bottom: "12%",
        containLabel: true
      },
      xAxis: {
        type: "value",
        name: "1,000-Monkey Null Percentile Rank (%)",
        nameLocation: "middle",
        nameGap: 28,
        min: 0,
        max: 100,
        splitLine: { lineStyle: { color: tc.gridLine } },
        axisLabel: { color: tc.textSecondary, formatter: "{value}%" },
        nameTextStyle: { color: tc.textSecondary, fontSize: 11 }
      },
      yAxis: {
        type: "value",
        name: "OOS Total Return (%)",
        nameTextStyle: { color: tc.textSecondary, fontSize: 11 },
        splitLine: { lineStyle: { color: tc.gridLine } },
        axisLabel: { color: tc.textSecondary, formatter: "{value}%" }
      },
      series: [
        {
          name: "Arena Strategy Paths",
          type: "scatter",
          data: data,
          symbolSize: (val) => Math.min(26, Math.max(8, val[2] * 5.5)),
          itemStyle: {
            color: (params) => {
              const p = params.data[3];
              const pct = p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0);
              if (pct >= 95) return "#10b981";
              if (p.total_return_pct >= 0) return "#38bdf8";
              return "#f43f5e";
            },
            opacity: 0.82,
            shadowBlur: 8,
            shadowColor: "rgba(0, 0, 0, 0.3)"
          },
          markLine: {
            silent: true,
            symbol: ["none", "none"],
            data: [
              {
                xAxis: 95,
                lineStyle: { color: "#10b981", type: "dashed", width: 2 },
                label: { formatter: "p = 0.05 (95th Percentile)", position: "insideEndTop", color: "#10b981", fontSize: 10 }
              },
              {
                yAxis: 0,
                lineStyle: { color: tc.gridLine, width: 1.5, type: "solid" },
                label: { show: false }
              }
            ]
          }
        }
      ]
    };

    chart.setOption(option, true);
    chart.off("click");
    chart.on("click", (params) => {
      if (params.data && params.data[3] && typeof onPointClick === "function") {
        onPointClick(params.data[3]);
      }
    });

    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 2. Contestant × Animal Handler Heatmap Matrix
   */
  renderHeatmap(domId, matrixData, metricKey = "total_return_pct", onCellClick) {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    const tc = this.getThemeColors();
    const contestants = (matrixData.rows || []).filter(r => !String(r).toUpperCase().includes("BENCHMARK"));
    const animals = (matrixData.columns || []).filter(a => a !== "taotie");

    const data = [];
    let minVal = Infinity;
    let maxVal = -Infinity;

    contestants.forEach((cId, yIdx) => {
      animals.forEach((aId, xIdx) => {
        const pathId = `${cId}_${aId}`;
        const path = window.arenaAdapter.getPath(pathId);
        let val = 0;
        if (path) {
          if (metricKey === "total_return_pct") val = path.total_return_pct;
          else if (metricKey === "percentile_rank" || metricKey === "monkey_percentile") {
            val = path.percentile_rank !== undefined ? path.percentile_rank : (path.monkey_percentile || 0);
          } else if (metricKey === "max_drawdown_pct") val = path.max_drawdown_pct;
          else if (metricKey === "sharpe_ratio") val = path.sharpe_ratio || 0;
        }
        if (val < minVal) minVal = val;
        if (val > maxVal) maxVal = val;
        // Dimension 0: xIdx, Dimension 1: yIdx, Dimension 2: val (numeric metric for visualMap), Dimension 3: pathId
        data.push([xIdx, yIdx, val, pathId]);
      });
    });

    if (minVal === Infinity) { minVal = 0; maxVal = 10; }

    const isPctRank = metricKey.includes("percentile");
    const inRangeColors = isPctRank
      ? ["#1e293b", "#4338ca", "#7c3aed", "#c026d3", "#10b981"]
      : (metricKey === "max_drawdown_pct"
        ? ["#047857", "#10b981", "#f59e0b", "#f43f5e", "#991b1b"]
        : (metricKey === "sharpe_ratio"
          ? ["#dc2626", "#f97316", "#38bdf8", "#10b981", "#059669"]
          : ["#dc2626", "#ea580c", "#334155", "#0ea5e9", "#10b981", "#059669"]));

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        position: "top",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary },
        formatter: (params) => {
          const pathId = params.data && params.data[3];
          const p = window.arenaAdapter.getPath(pathId);
          if (!p) return "No data";
          const pct = (p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0)).toFixed(1);
          return `
            <div style="font-weight:700; color:#38bdf8;">${p.path_id}</div>
            <div>Return: <b style="color:${p.total_return_pct >= 0 ? '#10b981' : '#f43f5e'}">${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</b></div>
            <div>Drawdown: <b>${p.max_drawdown_pct.toFixed(2)}%</b> | Sharpe: <b>${p.sharpe_ratio}</b></div>
            <div>Monkey Percentile: <b>${pct}%</b></div>
            <div style="font-size:10px; color:#94a3b8; margin-top:3px;">Click cell to inspect details</div>
          `;
        }
      },
      grid: {
        left: "14%",
        right: "8%",
        top: "4%",
        bottom: "22%"
      },
      xAxis: {
        type: "category",
        data: animals,
        splitArea: { show: true },
        axisLabel: { color: tc.textSecondary, rotate: 45, fontSize: 10 }
      },
      yAxis: {
        type: "category",
        data: contestants,
        splitArea: { show: true },
        axisLabel: { color: tc.textSecondary, fontWeight: 600, fontSize: 11 }
      },
      visualMap: {
        dimension: 2, // Explicitly map dimension 2 to the color scale!
        min: Math.floor(minVal),
        max: Math.ceil(maxVal),
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: "0%",
        inRange: { color: inRangeColors },
        textStyle: { color: tc.textSecondary }
      },
      series: [
        {
          name: "Metric Matrix",
          type: "heatmap",
          data: data,
          label: {
            show: true,
            fontSize: 9,
            formatter: (params) => {
              const v = params.data[2];
              return isPctRank ? Math.round(v) : (typeof v === "number" ? v.toFixed(1) : v);
            },
            color: tc.isDark ? "#ffffff" : "#0f172a"
          },
          itemStyle: {
            borderWidth: 1,
            borderColor: tc.isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.08)"
          }
        }
      ]
    };

    chart.setOption(option, true);
    chart.off("click");
    chart.on("click", (params) => {
      const pathId = params.data && params.data[3];
      if (pathId && typeof onCellClick === "function") {
        const path = window.arenaAdapter.getPath(pathId);
        if (path) onCellClick(path);
      }
    });

    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 3. Multi-Line Equity Curves with Monkey 90% Confidence Envelope (P05 ~ P95) & Benchmarks (Taotie & CSI 300)
   */
  renderEquityCurves(domId, dates, targetPath, taotieCurve = [], csi300Curve = [], monkeyDist = null, metricType = "nav") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    if (!dates || !Array.isArray(dates) || dates.length === 0) return null;
    const tc = this.getThemeColors();

    function round(num, dec = 4) {
      return Number(Math.round(num + "e" + dec) + "e-" + dec);
    }

    const parsePct = (val) => {
      if (!val) return 0.0;
      return parseFloat(String(val).replace("%", ""));
    };

    let series = [];
    let yAxisName = "Normalized NAV (Starting 1.0000)";
    let yAxisFormatter = v => v.toFixed(4);
    let legendData = [];
    let monkeyLower = [];

    if (metricType === "drawdown") {
      yAxisName = "Underwater Drawdown (%)";
      yAxisFormatter = v => `${v.toFixed(1)}%`;

      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      const targetDD = window.arenaAdapter.getPathDrawdown(targetPath.path_id);
      const csi300DD = window.arenaAdapter.getMarketDrawdown();
      const taotieDD = window.arenaAdapter.getTaotieDrawdown();
      const ghostDD = window.arenaAdapter.hasGhostTaotie() ? window.arenaAdapter.getGhostTaotieDrawdown() : null;

      series = [
        {
          name: marketBmName,
          type: "line",
          data: csi300DD,
          smooth: true,
          showSymbol: false,
          color: "#f59e0b",
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 }
        },
        {
          name: "Taotie (500k)",
          type: "line",
          data: taotieDD,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        }
      ];

      legendData = [
        `Path: ${targetPath.path_id}`
      ];

      if (ghostDD && ghostDD.length > 0) {
        series.push({
          name: "Ghost Taotie (100M)",
          type: "line",
          data: ghostDD,
          smooth: true,
          showSymbol: false,
          color: "#00f0ff",
          itemStyle: { color: "#00f0ff" },
          lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
        });
      }

      series.push({
        name: `Path: ${targetPath.path_id}`,
        type: "line",
        data: targetDD,
        smooth: true,
        showSymbol: false,
        color: "#f43f5e",
        itemStyle: { color: "#f43f5e" },
        lineStyle: { width: 2.5, color: "#f43f5e", type: "solid" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(244, 63, 94, 0.35)" },
            { offset: 1, color: "rgba(244, 63, 94, 0.04)" }
          ])
        }
      });

    } else if (metricType === "excess_csi300") {
      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      yAxisName = `Active Excess Return vs. ${marketBmName} (%)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;

      const targetExcess = window.arenaAdapter.getPathExcessMarket(targetPath.path_id);
      const taotieExcess = window.arenaAdapter.getPathExcessMarket("BENCHMARK_taotie");
      const ghostExcess = window.arenaAdapter.hasGhostTaotie() ? window.arenaAdapter.getPathExcessMarket("BENCHMARK_ghost_taotie") : null;
      const zeroBase = dates.map(() => 0.0);

      series = [
        {
          name: `${marketBmName} (0.00%)`,
          type: "line",
          data: zeroBase,
          color: "#f59e0b",
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 },
          showSymbol: false
        },
        {
          name: `Taotie vs ${marketBmName}`,
          type: "line",
          data: taotieExcess,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        }
      ];

      legendData = [
        `Active Spread: ${targetPath.path_id}`
      ];

      if (ghostExcess && ghostExcess.length > 0) {
        series.push({
          name: `Ghost Taotie vs ${marketBmName}`,
          type: "line",
          data: ghostExcess,
          smooth: true,
          showSymbol: false,
          color: "#00f0ff",
          itemStyle: { color: "#00f0ff" },
          lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
        });
      }

      series.push({
        name: `Active Spread: ${targetPath.path_id}`,
        type: "line",
        data: targetExcess,
        smooth: true,
        showSymbol: false,
        color: "#10b981",
        itemStyle: { color: "#10b981" },
        lineStyle: { width: 2.5, color: "#10b981", type: "solid" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(16, 185, 129, 0.30)" },
            { offset: 1, color: "rgba(16, 185, 129, 0.02)" }
          ])
        }
      });

    } else {
      // Default: Cumulative NAV
      const targetCurve = window.arenaAdapter.getNavCurve(targetPath.path_id);
      let p05 = -3.40;
      let p95 = 5.45;
      let med = 1.07;
      if (monkeyDist) {
        p05 = parsePct(monkeyDist.monkey_p05);
        p95 = parsePct(monkeyDist.monkey_p95);
        med = parsePct(monkeyDist.monkey_median);
      }

      const numPoints = dates.length;
      monkeyLower = dates.map((_, i) => round(1.0 + (p05 / 100) * (i / Math.max(1, numPoints - 1)), 4));
      const monkeyDiff = dates.map((_, i) => {
        const upper = 1.0 + (p95 / 100) * (i / Math.max(1, numPoints - 1));
        return round(Math.max(0, upper - monkeyLower[i]), 4);
      });
      const monkeyMedCurve = dates.map((_, i) => round(1.0 + (med / 100) * (i / Math.max(1, numPoints - 1)), 4));

      const targetLabel = `Path: ${targetPath.path_id}`;

      series = [
        {
          name: "Monkey P05 Base",
          type: "line",
          stack: "monkey-envelope",
          data: monkeyLower,
          showSymbol: false,
          color: "transparent",
          lineStyle: { opacity: 0 },
          tooltip: { show: false }
        },
        {
          name: "Monkey 90% Null",
          type: "line",
          stack: "monkey-envelope",
          data: monkeyDiff,
          showSymbol: false,
          color: "rgba(192, 132, 252, 0.18)",
          itemStyle: { color: "rgba(192, 132, 252, 0.18)" },
          lineStyle: { opacity: 0 },
          areaStyle: { color: "rgba(192, 132, 252, 0.18)" }
        },
        {
          name: "Monkey Median",
          type: "line",
          data: monkeyMedCurve,
          smooth: true,
          showSymbol: false,
          color: "#94a3b8",
          itemStyle: { color: "#94a3b8" },
          lineStyle: { width: 1.8, color: "#94a3b8", type: [3, 3], opacity: 0.85 }
        },
        {
          name: (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300",
          type: "line",
          data: csi300Curve && csi300Curve.length ? csi300Curve : [],
          smooth: true,
          showSymbol: false,
          color: "#f59e0b",
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 }
        },
        {
          name: "Taotie (500k)",
          type: "line",
          data: taotieCurve && taotieCurve.length ? taotieCurve : [],
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        }
      ];

      legendData = [
        targetLabel
      ];

      if (window.arenaAdapter && window.arenaAdapter.hasGhostTaotie()) {
        const ghostCurve = window.arenaAdapter.getBenchmarkGhostTaotieCurve();
        if (ghostCurve && ghostCurve.length > 0) {
          series.push({
            name: "Ghost Taotie (100M)",
            type: "line",
            data: ghostCurve,
            smooth: true,
            showSymbol: false,
            color: "#00f0ff",
            itemStyle: { color: "#00f0ff" },
            lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
          });
        }
      }

      series.push({
        name: targetLabel,
        type: "line",
        data: targetCurve,
        smooth: true,
        showSymbol: false,
        color: "#38bdf8",
        itemStyle: { color: "#38bdf8" },
        lineStyle: { width: 3, color: "#38bdf8", type: "solid" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(56, 189, 248, 0.28)" },
            { offset: 1, color: "rgba(56, 189, 248, 0.0)" }
          ])
        }
      });
    }

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        trigger: "axis",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary, fontSize: 12 },
        formatter: (params) => {
          if (!params || params.length === 0) return "";
          const date = params[0].axisValue;
          let html = `<div style="font-weight:700; margin-bottom:6px; color:#38bdf8;">${date}</div>`;
          params.forEach(item => {
            if (item.seriesName === "Monkey P05 Base") return;
            let val = item.value;
            if (item.seriesName.includes("Null Envelope")) {
              const idx = item.dataIndex;
              const low = monkeyLower[idx] || 0;
              const high = (low + val).toFixed(4);
              html += `<div style="display:flex; justify-content:space-between; align-items:center; gap:12px; font-size:11px; color:#c084fc;">
                <span>${item.marker || '🟣'} 90% Monkey Envelope:</span>
                <b>${low.toFixed(4)} ~ ${high}</b>
              </div>`;
            } else {
              const formattedVal = (metricType === "drawdown" || metricType === "excess_csi300")
                ? `${typeof val === 'number' ? (val >= 0 && metricType === "excess_csi300" ? '+' : '') + val.toFixed(2) : val}%`
                : (typeof val === 'number' ? val.toFixed(4) : val);
              const marker = item.marker || `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${item.color};"></span>`;
              html += `<div style="display:flex; justify-content:space-between; align-items:center; gap:12px; font-size:11px;">
                <span style="display:flex; align-items:center;">${marker}${item.seriesName.split(' (')[0]}:</span>
                <b style="color:${item.color};">${formattedVal}</b>
              </div>`;
            }
          });
          return html;
        }
      },
      legend: {
        type: "scroll",
        data: legendData,
        textStyle: { color: tc.textSecondary, fontSize: 11 },
        pageTextStyle: { color: tc.textSecondary },
        top: 0
      },
      grid: {
        left: "3%",
        right: "4%",
        top: "14%",
        bottom: "12%",
        containLabel: true
      },
      dataZoom: [
        { type: "inside" },
        { type: "slider", bottom: "0%", height: 18, textStyle: { color: tc.textSecondary } }
      ],
      xAxis: {
        type: "category",
        data: dates,
        axisLabel: { color: tc.textSecondary }
      },
      yAxis: {
        type: "value",
        scale: true,
        name: yAxisName,
        nameTextStyle: { color: tc.textSecondary },
        splitLine: { lineStyle: { color: tc.gridLine } },
        axisLabel: {
          color: tc.textSecondary,
          formatter: yAxisFormatter
        }
      },
      color: series.map(s => s.color || (s.itemStyle && s.itemStyle.color)).filter(c => c && c !== 'transparent'),
      series: series
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 4. Monkey Null Distribution Boxplot with Significance Marker
   */
  renderMonkeyDistribution(domId, monkeyDist, actualReturnPct, pctRank, pValue) {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    const tc = this.getThemeColors();
    if (!monkeyDist) return null;

    const parse = v => parseFloat(String(v).replace("%", ""));
    const minVal = parse(monkeyDist.monkey_min);
    const p05 = parse(monkeyDist.monkey_p05);
    const med = parse(monkeyDist.monkey_median);
    const p95 = parse(monkeyDist.monkey_p95);
    const maxVal = parse(monkeyDist.monkey_max);

    const xMin = Math.min(minVal, actualReturnPct) - 2.0;
    const xMax = Math.max(maxVal, actualReturnPct) + 3.0;

    const option = {
      backgroundColor: tc.bg,
      title: {
        text: `1,000-Monkey Null Distribution [P05 ~ P95] vs Actual Return`,
        textStyle: { color: tc.textPrimary, fontSize: 13, fontWeight: 600 },
        left: "center",
        top: 0
      },
      tooltip: {
        trigger: "item",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary }
      },
      grid: {
        left: "6%",
        right: "6%",
        top: "20%",
        bottom: "15%",
        containLabel: true
      },
      xAxis: {
        type: "value",
        min: Math.floor(xMin),
        max: Math.ceil(xMax),
        name: "Total Return (%)",
        nameLocation: "middle",
        nameGap: 25,
        nameTextStyle: { color: tc.textSecondary },
        splitLine: { lineStyle: { color: tc.gridLine } },
        axisLabel: { color: tc.textSecondary, formatter: "{value}%" }
      },
      yAxis: {
        type: "category",
        data: ["Null Model"],
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false }
      },
      series: [
        {
          name: "1,000 Random Monkey Distribution",
          type: "boxplot",
          data: [[minVal, p05, med, p95, maxVal]],
          itemStyle: {
            color: "rgba(168, 85, 247, 0.2)",
            borderColor: "#a855f7",
            borderWidth: 2
          },
          markLine: {
            silent: false,
            symbol: ["none", "none"],
            lineStyle: { color: "#38bdf8", width: 3, type: "solid" },
            data: [
              {
                xAxis: actualReturnPct,
                label: {
                  formatter: () => {
                    const pctStr = window.formatPercentile ? window.formatPercentile(pctRank) : `${pctRank.toFixed(1)}%`;
                    const pValStr = window.formatPValue ? window.formatPValue(pValue) : pValue.toFixed(4);
                    const pLabel = pValStr.startsWith("<") ? `p ${pValStr}` : `p = ${pValStr}`;
                    return `Actual: ${actualReturnPct >= 0 ? '+' : ''}${actualReturnPct.toFixed(2)}%\n(Rank: ${pctStr}, ${pLabel})`;
                  },
                  position: "end",
                  color: "#38bdf8",
                  fontWeight: 700
                }
              }
            ]
          }
        }
      ]
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 5. Decision Regret Chart (NAV_rejected - NAV_chosen)
   */
  renderDecisionRegret(domId, dates, chosenCurve, rejectedCurve, chosenName, rejectedName, animalName = "Robot") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    if (!dates || !Array.isArray(dates) || dates.length === 0) return null;
    chosenCurve = chosenCurve || [];
    rejectedCurve = rejectedCurve || [];

    const tc = this.getThemeColors();
    const regretCurve = dates.map((_, i) => {
      const c = chosenCurve[i] !== undefined ? chosenCurve[i] : 1.0;
      const r = rejectedCurve[i] !== undefined ? rejectedCurve[i] : 1.0;
      return Number((r - c).toFixed(4));
    });

    const series = [
      {
        name: `Chosen: ${chosenName}`,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: chosenCurve,
        color: "#10b981",
        itemStyle: { color: "#10b981" },
        lineStyle: { width: 2.5, color: "#10b981" },
        showSymbol: false
      },
      {
        name: `Rejected: ${rejectedName}`,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: rejectedCurve,
        color: "#f43f5e",
        itemStyle: { color: "#f43f5e" },
        lineStyle: { width: 2.5, color: "#f43f5e", type: "dashed" },
        showSymbol: false
      },
      {
        name: "Counterfactual Regret (NAV_rej - NAV_cho)",
        type: "line",
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: regretCurve,
        color: "#f59e0b",
        itemStyle: { color: "#f59e0b" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(244, 63, 94, 0.3)" },
            { offset: 1, color: "rgba(16, 185, 129, 0.3)" }
          ])
        },
        lineStyle: { width: 2, color: "#f59e0b" },
        showSymbol: false
      }
    ];

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        trigger: "axis",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary, fontSize: 12 },
        formatter: (params) => {
          if (!params || !params.length) return "";
          let html = `<div style="font-weight:700; margin-bottom:6px; color:${tc.textPrimary};">${params[0].axisValue}</div>`;
          params.forEach(item => {
            const val = typeof item.value === "number" ? item.value.toFixed(4) : item.value;
            const color = item.color || "#38bdf8";
            const marker = `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:9px;height:9px;background-color:${color};"></span>`;
            html += `<div style="display:flex; justify-content:space-between; align-items:center; gap:14px; font-size:11px; margin-bottom:2px;">
              <span style="display:flex; align-items:center;">${marker}${item.seriesName}:</span>
              <b style="color:${color}; font-family:monospace;">${val}</b>
            </div>`;
          });
          return html;
        }
      },
      legend: {
        data: [`Chosen: ${chosenName}`, `Rejected: ${rejectedName}`, "Counterfactual Regret (NAV_rej - NAV_cho)"],
        textStyle: { color: tc.textSecondary, fontSize: 11 },
        top: 0
      },
      grid: [
        { left: "4%", right: "4%", top: "12%", height: "45%" },
        { left: "4%", right: "4%", top: "68%", height: "24%" }
      ],
      xAxis: [
        { type: "category", data: dates, gridIndex: 0, axisLabel: { show: false } },
        { type: "category", data: dates, gridIndex: 1, axisLabel: { color: tc.textSecondary } }
      ],
      yAxis: [
        {
          type: "value",
          scale: true,
          gridIndex: 0,
          name: `NAV (${animalName})`,
          nameTextStyle: { color: tc.textSecondary },
          splitLine: { lineStyle: { color: tc.gridLine } },
          axisLabel: { color: tc.textSecondary }
        },
        {
          type: "value",
          gridIndex: 1,
          name: "Regret (Spread)",
          nameTextStyle: { color: tc.textSecondary },
          splitLine: { lineStyle: { color: tc.gridLine } },
          axisLabel: { color: tc.textSecondary }
        }
      ],
      color: ["#10b981", "#f43f5e", "#f59e0b"],
      series: series
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 6. Behavioral Fingerprints Group
   */
  renderFingerprintGroup(domDelayId, domTurnoverId, domBreadthId, domDirectionId, fingerprints) {
    const tc = this.getThemeColors();

    // A. Delay Sensitivity
    const domDelay = document.getElementById(domDelayId);
    if (domDelay) {
      let c1 = echarts.getInstanceByDom(domDelay) || echarts.init(domDelay);
      c1.setOption({
        backgroundColor: tc.bg,
        title: { text: "Delay Sensitivity (Execution Lag)", textStyle: { color: tc.textPrimary, fontSize: 12 } },
        tooltip: { trigger: "axis" },
        legend: { data: ["Sloth (Cash Lag)", "Snail (Holding Lag)"], textStyle: { color: tc.textSecondary }, top: 0 },
        grid: { left: "8%", right: "8%", top: "25%", bottom: "15%" },
        xAxis: { type: "category", data: ["0W", "1W", "2W", "3W", "4W"], axisLabel: { color: tc.textSecondary } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [
          { name: "Sloth (Cash Lag)", type: "line", data: fingerprints.delayData.sloth, color: "#38bdf8", itemStyle: { color: "#38bdf8" }, lineStyle: { color: "#38bdf8", width: 2 } },
          { name: "Snail (Holding Lag)", type: "line", data: fingerprints.delayData.snail, color: "#f59e0b", itemStyle: { color: "#f59e0b" }, lineStyle: { color: "#f59e0b", width: 2 } }
        ]
      }, true);
      window.addEventListener("resize", () => c1.resize());
    }

    // B. Turnover Sensitivity
    const domTurnover = document.getElementById(domTurnoverId);
    if (domTurnover) {
      let c2 = echarts.getInstanceByDom(domTurnover) || echarts.init(domTurnover);
      const names = fingerprints.turnoverData.map(d => d.name);
      const vals = fingerprints.turnoverData.map(d => d.return);
      c2.setOption({
        backgroundColor: tc.bg,
        title: { text: "Turnover Sensitivity (Friction Stress)", textStyle: { color: tc.textPrimary, fontSize: 12 } },
        tooltip: { trigger: "axis" },
        grid: { left: "8%", right: "8%", top: "20%", bottom: "15%" },
        xAxis: { type: "category", data: names, axisLabel: { color: tc.textSecondary, fontSize: 10 } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [{ type: "bar", data: vals, itemStyle: { color: "#10b981", borderRadius: [4, 4, 0, 0] } }]
      }, true);
      window.addEventListener("resize", () => c2.resize());
    }

    // C. Capacity & Breadth
    const domBreadth = document.getElementById(domBreadthId);
    if (domBreadth) {
      let c3 = echarts.getInstanceByDom(domBreadth) || echarts.init(domBreadth);
      const bLabels = fingerprints.breadthData.map(d => d.label);
      const bVals = fingerprints.breadthData.map(d => d.return);
      c3.setOption({
        backgroundColor: tc.bg,
        title: { text: "Capacity & Portfolio Breadth Expansion", textStyle: { color: tc.textPrimary, fontSize: 12 } },
        tooltip: { trigger: "axis" },
        grid: { left: "8%", right: "8%", top: "20%", bottom: "25%" },
        xAxis: { type: "category", data: bLabels, axisLabel: { color: tc.textSecondary, rotate: 30, fontSize: 9 } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [{ type: "line", data: bVals, smooth: true, color: "#a855f7", itemStyle: { color: "#a855f7" }, lineStyle: { color: "#a855f7", width: 2.5 } }]
      }, true);
      window.addEventListener("resize", () => c3.resize());
    }

    // D. Direction Sanity (Robot vs Koala)
    const domDir = document.getElementById(domDirectionId);
    if (domDir) {
      let c4 = echarts.getInstanceByDom(domDir) || echarts.init(domDir);
      c4.setOption({
        backgroundColor: tc.bg,
        title: { text: "Direction Sanity (Robot vs. Koala Reverse)", textStyle: { color: tc.textPrimary, fontSize: 12 } },
        tooltip: { trigger: "axis" },
        grid: { left: "10%", right: "8%", top: "20%", bottom: "15%" },
        xAxis: { type: "category", data: ["Robot (Top)", "Koala (Bottom)", "Spread"], axisLabel: { color: tc.textSecondary } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [{
          type: "bar",
          data: [
            { value: fingerprints.directionData.robot, itemStyle: { color: "#38bdf8" } },
            { value: fingerprints.directionData.koala, itemStyle: { color: "#f43f5e" } },
            { value: fingerprints.directionData.spread, itemStyle: { color: "#10b981" } },
          ]
        }]
      }, true);
      window.addEventListener("resize", () => c4.resize());
    }
  },

  /**
   * 7. Contestant Multi-Animal Execution Curves Comparison Chart
   */
  renderMultiAnimalCurves(domId, dates, paths = [], taotieCurve = [], csi300Curve = [], metricType = "nav") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    if (!dates || !Array.isArray(dates) || dates.length === 0) return null;
    const tc = this.getThemeColors();

    const colorPalette = [
      "#38bdf8", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6",
      "#06b6d4", "#84cc16", "#f43f5e", "#d946ef", "#6366f1"
    ];

    const series = [];
    let titleText = "Multi-Animal Execution Trajectories";
    let yAxisName = "NAV";
    let yAxisFormatter = v => v.toFixed(4);

    if (metricType === "drawdown") {
      titleText = "Multi-Animal Underwater Drawdown Trajectories";
      yAxisName = "Drawdown (%)";
      yAxisFormatter = v => `${v.toFixed(1)}%`;

      paths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getPathDrawdown(p.path_id);
        if (curve && curve.length > 0) {
          const color = p.animal_id === "robot" ? "#38bdf8" : (p.animal_id === "koala" ? "#f43f5e" : colorPalette[idx % colorPalette.length]);
          series.push({
            name: `${p.animal_id} (MDD: -${p.max_drawdown_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: {
              width: p.animal_id === "robot" ? 3 : (p.animal_id === "koala" ? 2.5 : 1.8),
              color: color,
              type: p.animal_id === "koala" ? "dashed" : "solid"
            }
          });
        }
      });

      const ghostDD = window.arenaAdapter.hasGhostTaotie() ? window.arenaAdapter.getGhostTaotieDrawdown() : null;
      if (ghostDD && ghostDD.length > 0) {
        series.push({
          name: "Ghost Taotie Drawdown",
          type: "line",
          data: ghostDD,
          smooth: true,
          showSymbol: false,
          color: "#00f0ff",
          itemStyle: { color: "#00f0ff" },
          lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
        });
      }

      const taotieDD = window.arenaAdapter.getTaotieDrawdown();
      if (taotieDD && taotieDD.length > 0) {
        series.push({
          name: "Taotie Drawdown",
          type: "line",
          data: taotieDD,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        });
      }

      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      const csi300DD = window.arenaAdapter.getMarketDrawdown();
      if (csi300DD && csi300DD.length > 0) {
        series.push({
          name: `${marketBmName} Drawdown`,
          type: "line",
          data: csi300DD,
          smooth: true,
          showSymbol: false,
          color: "#f59e0b",
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 }
        });
      }

    } else if (metricType === "excess_csi300") {
      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      titleText = `Multi-Animal Active Spread vs. ${marketBmName}`;
      yAxisName = `Excess vs. ${marketBmName} (%)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;

      paths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getPathExcessMarket(p.path_id);
        if (curve && curve.length > 0) {
          const color = p.animal_id === "robot" ? "#38bdf8" : colorPalette[idx % colorPalette.length];
          series.push({
            name: `${p.animal_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: {
              width: p.animal_id === "robot" ? 2.8 : 1.8,
              color: color,
              type: "solid"
            }
          });
        }
      });

      const zeroBase = dates.map(() => 0.0);
      series.push({
        name: `${marketBmName} (0.00%)`,
        type: "line",
        data: zeroBase,
        color: "#f59e0b",
        itemStyle: { color: "#f59e0b" },
        lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 },
        showSymbol: false
      });

      const taotieExcess = window.arenaAdapter.getPathExcessMarket("BENCHMARK_taotie");
      if (taotieExcess && taotieExcess.length > 0) {
        series.push({
          name: `Taotie vs ${marketBmName}`,
          type: "line",
          data: taotieExcess,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        });
      }

      const ghostExcess = window.arenaAdapter.hasGhostTaotie() ? window.arenaAdapter.getPathExcessMarket("BENCHMARK_ghost_taotie") : null;
      if (ghostExcess && ghostExcess.length > 0) {
        series.push({
          name: `Ghost Taotie vs ${marketBmName}`,
          type: "line",
          data: ghostExcess,
          smooth: true,
          showSymbol: false,
          color: "#00f0ff",
          itemStyle: { color: "#00f0ff" },
          lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
        });
      }

    } else {
      // Default: NAV
      titleText = "Multi-Animal Execution NAV Trajectories";
      yAxisName = "NAV";
      yAxisFormatter = v => v.toFixed(4);

      paths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getNavCurve(p.path_id);
        if (curve && curve.length > 0) {
          const color = p.animal_id === "robot" ? "#38bdf8" : colorPalette[idx % colorPalette.length];
          series.push({
            name: `${p.animal_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: {
              width: p.animal_id === "robot" ? 2.8 : 1.8,
              color: color,
              type: "solid"
            }
          });
        }
      });

      if (window.arenaAdapter && window.arenaAdapter.hasGhostTaotie()) {
        const ghostCurve = window.arenaAdapter.getBenchmarkGhostTaotieCurve();
        if (ghostCurve && ghostCurve.length > 0) {
          series.push({
            name: "Ghost Taotie (100M)",
            type: "line",
            data: ghostCurve,
            smooth: true,
            showSymbol: false,
            color: "#00f0ff",
            itemStyle: { color: "#00f0ff" },
            lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
          });
        }
      }

      if (taotieCurve && taotieCurve.length > 0) {
        series.push({
          name: "Taotie (500k)",
          type: "line",
          data: taotieCurve,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        });
      }

      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      if (csi300Curve && csi300Curve.length > 0) {
        series.push({
          name: marketBmName,
          type: "line",
          data: csi300Curve,
          smooth: true,
          showSymbol: false,
          color: "#f59e0b",
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 }
        });
      }
    }

    const option = {
      backgroundColor: tc.bg,
      title: {
        text: titleText,
        textStyle: { color: tc.textPrimary, fontSize: 13, fontWeight: 600 },
        left: "left"
      },
      tooltip: {
        trigger: "axis",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary, fontSize: 11 },
        formatter: (params) => {
          if (!params || params.length === 0) return "";
          const date = params[0].axisValue;
          let html = `<div style="font-weight:700; margin-bottom:6px; color:#38bdf8;">${date}</div>`;
          params.forEach(item => {
            let val = item.value;
            const formattedVal = (metricType === "drawdown" || metricType === "excess_csi300")
              ? `${typeof val === 'number' ? (val >= 0 && metricType === "excess_csi300" ? '+' : '') + val.toFixed(2) : val}%`
              : (typeof val === 'number' ? val.toFixed(4) : val);
            const marker = item.marker || `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${item.color};"></span>`;
            html += `<div style="display:flex; justify-content:space-between; align-items:center; gap:12px; font-size:11px;">
              <span style="display:flex; align-items:center;">${marker}${item.seriesName.split(' (')[0]}:</span>
              <b style="color:${item.color};">${formattedVal}</b>
            </div>`;
          });
          return html;
        }
      },
      legend: {
        type: "scroll",
        top: 25,
        data: series.filter(s => !s.name.includes("Taotie") && !s.name.includes("Ghost") && !s.name.includes("CSI 300") && !s.name.includes("CSI 1000")).map(s => s.name),
        textStyle: { color: tc.textSecondary, fontSize: 10 },
        pageTextStyle: { color: tc.textSecondary }
      },
      grid: {
        left: "3%",
        right: "4%",
        top: "22%",
        bottom: "12%",
        containLabel: true
      },
      dataZoom: [
        { type: "inside" },
        { type: "slider", bottom: "0%", height: 16, textStyle: { color: tc.textSecondary } }
      ],
      xAxis: {
        type: "category",
        data: dates,
        axisLabel: { color: tc.textSecondary }
      },
      yAxis: {
        type: "value",
        scale: true,
        name: yAxisName,
        nameTextStyle: { color: tc.textSecondary },
        splitLine: { lineStyle: { color: tc.gridLine } },
        axisLabel: { color: tc.textSecondary, formatter: yAxisFormatter }
      },
      color: series.map(s => s.color || (s.itemStyle && s.itemStyle.color)).filter(Boolean),
      series: series
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 8. Cross-Model Comparative Curves for a Single Animal Handler
   * Plots all 6 contestant models under the selected animal execution handler.
   * Supports: "nav", "drawdown", "excess_csi300"
   */
  renderCrossModelAnimalCurves(domId, dates, animalPaths, taotieCurve, csi300Curve, metricType = "nav") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    const tc = this.getThemeColors();

    const modelColors = {
      'CONTESTANT_A': '#38bdf8', // Sky Blue
      'CONTESTANT_B': '#10b981', // Emerald Green
      'CONTESTANT_C': '#a855f7', // Purple
      'CONTESTANT_D': '#ec4899', // Pink
      'CONTESTANT_E': '#f97316', // Orange
      'CONTESTANT_F': '#eab308'  // Amber/Gold
    };
    const fallbackPalette = [
      '#38bdf8', '#10b981', '#a855f7', '#ec4899', '#f97316', '#eab308',
      '#06b6d4', '#84cc16', '#f43f5e', '#d946ef', '#6366f1', '#14b8a6',
      '#fb923c', '#c084fc', '#4ade80', '#facc15', '#94a3b8'
    ];

    const uniqueAnimals = new Set(animalPaths.map(p => p.animal_id));
    const uniqueModels = new Set(animalPaths.map(p => p.contestant_id));
    const isMultiAnimal = uniqueAnimals.size > 1;
    const isSingleModel = uniqueModels.size === 1;

    const getSeriesName = (p, metric) => {
      let label = "";
      if (isMultiAnimal && isSingleModel) {
        label = p.animal_name || p.animal_id;
      } else if (isMultiAnimal) {
        label = `${p.contestant_id} · ${p.animal_name || p.animal_id}`;
      } else {
        label = p.contestant_id;
      }

      if (metric === "drawdown") {
        return `${label} (Max: -${p.max_drawdown_pct.toFixed(1)}%)`;
      } else {
        return `${label} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`;
      }
    };

    const getColor = (p, idx) => {
      if (isMultiAnimal && isSingleModel) {
        return fallbackPalette[idx % fallbackPalette.length];
      }
      return modelColors[p.contestant_id] || fallbackPalette[idx % fallbackPalette.length];
    };

    const series = [];
    let titleText = "";
    let yAxisName = "";
    let yAxisFormatter = null;

    if (metricType === "drawdown") {
      titleText = isMultiAnimal ? "Multi-Animal Underwater Drawdown Comparison" : "Cross-Model Underwater Drawdown Comparison";
      yAxisName = "Drawdown (%)";
      yAxisFormatter = v => `${v.toFixed(1)}%`;

      animalPaths.forEach((p, idx) => {
        const dd = window.arenaAdapter.getPathDrawdown(p.path_id);
        if (dd && dd.length > 0) {
          const color = getColor(p, idx);
          series.push({
            name: getSeriesName(p, "drawdown"),
            type: "line",
            data: dd,
            smooth: true,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: { width: 2, color: color }
          });
        }
      });

      const ghostDD = window.arenaAdapter.hasGhostTaotie() ? window.arenaAdapter.getGhostTaotieDrawdown() : null;
      if (ghostDD && ghostDD.length > 0) {
        series.push({
          name: "Ghost Taotie Drawdown",
          type: "line",
          data: ghostDD,
          smooth: true,
          showSymbol: false,
          color: "#00f0ff",
          itemStyle: { color: "#00f0ff" },
          lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
        });
      }

      const taotieDD = window.arenaAdapter.getTaotieDrawdown();
      if (taotieDD && taotieDD.length > 0) {
        series.push({
          name: "Taotie Drawdown",
          type: "line",
          data: taotieDD,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        });
      }

      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      const csi300DD = window.arenaAdapter.getMarketDrawdown();
      if (csi300DD && csi300DD.length > 0) {
        series.push({
          name: `${marketBmName} Drawdown`,
          type: "line",
          data: csi300DD,
          smooth: true,
          showSymbol: false,
          color: "#f59e0b",
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 }
        });
      }

    } else if (metricType === "excess_csi300") {
      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      titleText = isMultiAnimal ? `Multi-Animal Active Excess Return vs. ${marketBmName}` : `Cross-Model Active Excess Return vs. ${marketBmName}`;
      yAxisName = `Excess vs. ${marketBmName} (%)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;

      animalPaths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getPathExcessMarket(p.path_id);
        if (curve && curve.length > 0) {
          const color = getColor(p, idx);
          series.push({
            name: getSeriesName(p, "excess"),
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: { width: 2.2, color: color, type: "solid" }
          });
        }
      });

      const zeroBase = dates.map(() => 0.0);
      series.push({
        name: `${marketBmName} (0.00%)`,
        type: "line",
        data: zeroBase,
        color: "#f59e0b",
        itemStyle: { color: "#f59e0b" },
        lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 },
        showSymbol: false
      });

      const taotieExcess = window.arenaAdapter.getPathExcessMarket("BENCHMARK_taotie");
      if (taotieExcess && taotieExcess.length > 0) {
        series.push({
          name: `Taotie vs ${marketBmName}`,
          type: "line",
          data: taotieExcess,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        });
      }

      const ghostExcess = window.arenaAdapter.hasGhostTaotie() ? window.arenaAdapter.getPathExcessMarket("BENCHMARK_ghost_taotie") : null;
      if (ghostExcess && ghostExcess.length > 0) {
        series.push({
          name: `Ghost Taotie vs ${marketBmName}`,
          type: "line",
          data: ghostExcess,
          smooth: true,
          showSymbol: false,
          color: "#00f0ff",
          itemStyle: { color: "#00f0ff" },
          lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
        });
      }

    } else {
      // Default: NAV
      titleText = isMultiAnimal ? "Multi-Animal Trajectory Overlay" : "Cross-Model Trajectory Overlay";
      yAxisName = "Cumulative NAV";
      yAxisFormatter = v => v.toFixed(4);

      animalPaths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getNavCurve(p.path_id);
        if (curve && curve.length > 0) {
          const color = getColor(p, idx);
          series.push({
            name: getSeriesName(p, "nav"),
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: { width: 2.2, color: color, type: "solid" }
          });
        }
      });

      if (window.arenaAdapter && window.arenaAdapter.hasGhostTaotie()) {
        const ghostCurve = window.arenaAdapter.getBenchmarkGhostTaotieCurve();
        if (ghostCurve && ghostCurve.length > 0) {
          series.push({
            name: "Ghost Taotie (100M)",
            type: "line",
            data: ghostCurve,
            smooth: true,
            showSymbol: false,
            color: "#00f0ff",
            itemStyle: { color: "#00f0ff" },
            lineStyle: { width: 2.2, color: "#00f0ff", type: [8, 4], opacity: 0.9 }
          });
        }
      }

      if (taotieCurve && taotieCurve.length > 0) {
        series.push({
          name: "Taotie (500k)",
          type: "line",
          data: taotieCurve,
          smooth: true,
          showSymbol: false,
          color: "#c084fc",
          itemStyle: { color: "#c084fc" },
          lineStyle: { width: 2.2, color: "#c084fc", type: [4, 4], opacity: 0.9 }
        });
      }

      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      if (csi300Curve && csi300Curve.length > 0) {
        series.push({
          name: marketBmName,
          type: "line",
          data: csi300Curve,
          smooth: true,
          showSymbol: false,
          color: "#f59e0b",
          itemStyle: { color: "#f59e0b" },
          lineStyle: { width: 2.0, color: "#f59e0b", type: [6, 6], opacity: 0.9 }
        });
      }
    }

    const option = {
      backgroundColor: tc.bg,
      title: {
        text: titleText,
        textStyle: { color: tc.textPrimary, fontSize: 13, fontWeight: 600 },
        left: "left"
      },
      tooltip: {
        trigger: "axis",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary, fontSize: 11 },
        formatter: (params) => {
          if (!params || params.length === 0) return "";
          const date = params[0].axisValue;
          let html = `<div style="font-weight:700; margin-bottom:6px; color:#38bdf8;">${date}</div>`;
          params.forEach(item => {
            let val = item.value;
            const formattedVal = (metricType === "drawdown" || metricType === "excess_csi300")
              ? `${typeof val === 'number' ? (val >= 0 && metricType === "excess_csi300" ? '+' : '') + val.toFixed(2) : val}%`
              : (typeof val === 'number' ? val.toFixed(4) : val);
            const marker = item.marker || `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${item.color};"></span>`;
            html += `<div style="display:flex; justify-content:space-between; align-items:center; gap:12px; font-size:11px;">
              <span style="display:flex; align-items:center;">${marker}${item.seriesName.split(' (')[0]}:</span>
              <b style="color:${item.color};">${formattedVal}</b>
            </div>`;
          });
          return html;
        }
      },
      legend: {
        type: "scroll",
        top: 25,
        data: series.filter(s => !s.name.includes("Taotie") && !s.name.includes("Ghost") && !s.name.includes("CSI 300") && !s.name.includes("CSI 1000")).map(s => s.name),
        textStyle: { color: tc.textSecondary, fontSize: 11 },
        pageTextStyle: { color: tc.textSecondary }
      },
      grid: {
        left: "3%",
        right: "4%",
        top: "22%",
        bottom: "12%",
        containLabel: true
      },
      dataZoom: [
        { type: "inside" },
        { type: "slider", bottom: "0%", height: 16, textStyle: { color: tc.textSecondary } }
      ],
      xAxis: {
        type: "category",
        data: dates,
        axisLabel: { color: tc.textSecondary }
      },
      yAxis: {
        type: "value",
        scale: true,
        name: yAxisName,
        nameTextStyle: { color: tc.textSecondary },
        splitLine: { lineStyle: { color: tc.gridLine } },
        axisLabel: { color: tc.textSecondary, formatter: yAxisFormatter }
      },
      color: series.map(s => s.color || (s.itemStyle && s.itemStyle.color)).filter(Boolean),
      series: series
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 8. Arena Horizon & Benchmark Zoo Trajectories (Macro Panorama)
   */
  renderMacroPanorama(domId, panoramaData) {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    const { dates, seriesList, metricMode } = panoramaData;
    if (!dates || dates.length === 0) return null;
    const tc = this.getThemeColors();

    const isExcess = metricMode && metricMode.startsWith("excess_");
    const isDD = metricMode === "drawdown";

    let yAxisName = "Normalized NAV (Starting 1.0000)";
    let yAxisFormatter = v => v.toFixed(3);

    if (isExcess) {
      const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
      if (metricMode === "excess_taotie") yAxisName = "Excess Return vs Taotie (%)";
      else if (metricMode === "excess_ghost") yAxisName = "Excess Return vs Ghost Taotie (%)";
      else yAxisName = `Excess Return vs ${marketBmName} (%)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;
    } else if (isDD) {
      yAxisName = "Underwater Drawdown (%)";
      yAxisFormatter = v => `${v.toFixed(1)}%`;
    }

    const series = seriesList.map(item => {
      const isBenchmark = item.type.startsWith("benchmark");
      const isGhost = item.type === "benchmark_ghost";
      const isTaotie = item.type === "benchmark_taotie";
      const isCsi = item.type === "benchmark_csi300";
      const isZero = item.type === "benchmark_zero";

      const s = {
        name: item.name,
        type: "line",
        data: item.data,
        smooth: true,
        showSymbol: false,
        lineStyle: item.lineStyle || {
          width: isBenchmark ? 2.5 : 2.5,
          color: item.color
        },
        itemStyle: { color: item.color }
      };

      if (isGhost) {
        s.lineStyle = {
          width: 2.2,
          type: [8, 4],
          color: "#00f0ff",
          opacity: 0.95
        };
      } else if (isTaotie) {
        s.lineStyle = {
          width: 2.2,
          type: [4, 4],
          color: "#c084fc",
          opacity: 0.95
        };
      } else if (isCsi) {
        s.lineStyle = {
          width: 2.0,
          type: [6, 6],
          color: "#f59e0b",
          opacity: 0.95
        };
      } else if (isZero) {
        s.lineStyle = {
          width: 2,
          type: "solid",
          color: item.color
        };
        s.markLine = {
          silent: true,
          symbol: ["none", "none"],
          data: [{ yAxis: 0, lineStyle: { color: item.color, width: 1.5, type: "solid" } }]
        };
      }

      return s;
    });

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        trigger: "axis",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary },
        axisPointer: { type: "cross", lineStyle: { color: tc.gridLine } },
        formatter: (params) => {
          if (!params || !params.length) return "";
          let html = `<div style="font-weight:700; margin-bottom:6px; color:#38bdf8;">${params[0].axisValue}</div>`;
          params.forEach(p => {
            const val = p.value;
            const displayVal = (isExcess || isDD)
              ? `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`
              : (typeof val === "number" ? val.toFixed(4) : val);
            const marker = p.marker || `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${p.color};"></span>`;
            html += `<div style="display:flex; justify-content:space-between; align-items:center; gap:14px; font-size:11px; margin-bottom:2px;">
              <span style="display:flex; align-items:center;">${marker} ${p.seriesName}</span>
              <b style="color:${p.color};">${displayVal}</b>
            </div>`;
          });
          return html;
        }
      },
      legend: {
        type: "scroll",
        top: 0,
        data: series.filter(s => !s.name.includes("Taotie") && !s.name.includes("Ghost") && !s.name.includes("CSI 300") && !s.name.includes("CSI 1000")).map(s => s.name),
        textStyle: { color: tc.textSecondary, fontSize: 11 },
        pageTextStyle: { color: tc.textSecondary }
      },
      grid: {
        left: "3%",
        right: "4%",
        top: "14%",
        bottom: "12%",
        containLabel: true
      },
      dataZoom: [
        { type: "inside" },
        { type: "slider", bottom: "0%", height: 16, textStyle: { color: tc.textSecondary } }
      ],
      xAxis: {
        type: "category",
        data: dates,
        axisLabel: { color: tc.textSecondary, fontSize: 11 }
      },
      yAxis: {
        type: "value",
        scale: true,
        name: yAxisName,
        nameTextStyle: { color: tc.textSecondary, fontSize: 11 },
        splitLine: { lineStyle: { color: tc.gridLine } },
        axisLabel: { color: tc.textSecondary, formatter: yAxisFormatter }
      },
      series: series
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  },

  /**
   * 9. Interactive Decision Archaeology Head-to-Head Comparison
   */
  renderCustomArchaeology(domId, dates, modelsData, activeAnimal = "robot") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    if (!dates || dates.length === 0 || !modelsData || modelsData.length < 2) return null;
    const tc = this.getThemeColors();

    const m1 = modelsData[0];
    const m2 = modelsData[1];
    const m3 = modelsData[2] || null;

    const len = Math.min(m1.curve.length, m2.curve.length);
    const spreadM1M2 = [];
    for (let i = 0; i < len; i++) {
      spreadM1M2.push(Number(((m1.curve[i] - m2.curve[i]) * 100).toFixed(2)));
    }

    const series = [
      {
        name: m1.name,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: m1.curve,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 3, color: m1.color || "#10b981" },
        itemStyle: { color: m1.color || "#10b981" }
      },
      {
        name: m2.name,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: m2.curve,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 3, color: m2.color || "#f43f5e" },
        itemStyle: { color: m2.color || "#f43f5e" }
      }
    ];

    if (m3 && m3.curve && m3.curve.length > 0) {
      series.push({
        name: m3.name,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: m3.curve,
        smooth: true,
        showSymbol: false,
        lineStyle: {
          width: 2.5,
          color: m3.color || "#38bdf8",
          type: m3.isBenchmark ? "dashDot" : "solid"
        },
        itemStyle: { color: m3.color || "#38bdf8" }
      });
    }

    series.push({
      name: `Spread (${m1.name} − ${m2.name})`,
      type: "line",
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: spreadM1M2,
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2, color: "#a855f7" },
      itemStyle: { color: "#a855f7" },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(168, 85, 247, 0.35)" },
          { offset: 1, color: "rgba(168, 85, 247, 0.02)" }
        ])
      },
      markLine: {
        silent: true,
        symbol: ["none", "none"],
        data: [{ yAxis: 0, lineStyle: { color: tc.gridLine, width: 1.5, type: "solid" } }]
      }
    });

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        trigger: "axis",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary },
        axisPointer: { type: "cross", lineStyle: { color: tc.gridLine } }
      },
      legend: {
        top: 0,
        textStyle: { color: tc.textSecondary, fontSize: 11 }
      },
      axisPointer: { link: [{ xAxisIndex: "all" }] },
      grid: [
        { left: "3%", right: "4%", top: "12%", height: "50%", containLabel: true },
        { left: "3%", right: "4%", top: "70%", height: "22%", containLabel: true }
      ],
      xAxis: [
        {
          type: "category",
          gridIndex: 0,
          data: dates,
          axisLabel: { show: false },
          axisTick: { show: false }
        },
        {
          type: "category",
          gridIndex: 1,
          data: dates,
          axisLabel: { color: tc.textSecondary, fontSize: 11 }
        }
      ],
      yAxis: [
        {
          type: "value",
          gridIndex: 0,
          scale: true,
          name: "Cumulative NAV",
          nameTextStyle: { color: tc.textSecondary, fontSize: 11 },
          splitLine: { lineStyle: { color: tc.gridLine } },
          axisLabel: { color: tc.textSecondary, formatter: v => v.toFixed(3) }
        },
        {
          type: "value",
          gridIndex: 1,
          scale: true,
          name: "Spread (%)",
          nameTextStyle: { color: tc.textSecondary, fontSize: 10 },
          splitLine: { lineStyle: { color: tc.gridLine } },
          axisLabel: { color: tc.textSecondary, formatter: v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%` }
        }
      ],
      series: series
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  }
};

