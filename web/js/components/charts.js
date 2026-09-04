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
      const pctRank = p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 50);
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
          const pct = (p.percentile_rank !== undefined ? p.percentile_rank : (p.monkey_percentile || 0)).toFixed(1);
          const pVal = (p.empirical_p_value !== undefined ? p.empirical_p_value : (p.p_value || 1.0)).toFixed(4);
          return `
            <div style="font-weight:700; color:#38bdf8; margin-bottom:4px;">${p.path_id}</div>
            <div style="font-size:12px; line-height:1.5;">
              <div>Model: <b>${p.contestant_id}</b> | Handler: <b>${p.animal_id}</b></div>
              <div>Return: <b style="color:${p.total_return_pct >= 0 ? '#10b981' : '#f43f5e'}">${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</b></div>
              <div>Monkey Percentile: <b>${pct}%</b> (p = ${pVal})</div>
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
                label: { formatter: "p = 0.05 (Top 5% Alpha)", position: "insideEndTop", color: "#10b981", fontSize: 10 }
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

      const targetDD = window.arenaAdapter.getPathDrawdown(targetPath.path_id);
      const csi300DD = window.arenaAdapter.getCsi300Drawdown();
      const taotieDD = window.arenaAdapter.getTaotieDrawdown();

      series = [
        {
          name: "CSI 300 Drawdown",
          type: "line",
          data: csi300DD,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#f59e0b", type: "dashed" }
        },
        {
          name: "Taotie Drawdown",
          type: "line",
          data: taotieDD,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#94a3b8", type: "dotted" }
        },
        {
          name: `Current Drawdown (${targetPath.path_id})`,
          type: "line",
          data: targetDD,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2.5, color: "#f43f5e" },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(244, 63, 94, 0.35)" },
              { offset: 1, color: "rgba(244, 63, 94, 0.04)" }
            ])
          }
        }
      ];

      legendData = [
        `Current Drawdown (${targetPath.path_id})`,
        "Taotie Drawdown",
        "CSI 300 Drawdown"
      ];

    } else if (metricType === "excess_csi300") {
      yAxisName = "Active Excess Return vs. CSI 300 (%)";
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;

      const targetExcess = window.arenaAdapter.getPathExcessCSI300(targetPath.path_id);
      const taotieExcess = window.arenaAdapter.getPathExcessCSI300("BENCHMARK_taotie");
      const zeroBase = dates.map(() => 0.0);

      series = [
        {
          name: "CSI 300 Benchmark (0.00%)",
          type: "line",
          data: zeroBase,
          lineStyle: { width: 2, color: "#f59e0b", type: "dashed" },
          showSymbol: false
        },
        {
          name: "Taotie vs. CSI 300",
          type: "line",
          data: taotieExcess,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#94a3b8", type: "dotted" }
        },
        {
          name: `Active Spread: ${targetPath.path_id}`,
          type: "line",
          data: targetExcess,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2.5, color: "#10b981" },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(16, 185, 129, 0.30)" },
              { offset: 1, color: "rgba(16, 185, 129, 0.02)" }
            ])
          }
        }
      ];

      legendData = [
        `Active Spread: ${targetPath.path_id}`,
        "Taotie vs. CSI 300",
        "CSI 300 Benchmark (0.00%)"
      ];

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

      series = [
        {
          name: "Monkey P05 Base",
          type: "line",
          stack: "monkey-envelope",
          data: monkeyLower,
          showSymbol: false,
          lineStyle: { opacity: 0 },
          tooltip: { show: false }
        },
        {
          name: `Monkey 90% Null Envelope (P05 ~ P95)`,
          type: "line",
          stack: "monkey-envelope",
          data: monkeyDiff,
          showSymbol: false,
          lineStyle: { opacity: 0 },
          areaStyle: {
            color: "rgba(168, 85, 247, 0.18)"
          }
        },
        {
          name: `Monkey Median Null (${med >= 0 ? '+' : ''}${med.toFixed(2)}%)`,
          type: "line",
          data: monkeyMedCurve,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#c084fc", type: "dashed" }
        },
        {
          name: "CSI 300 Index (SH000300)",
          type: "line",
          data: csi300Curve && csi300Curve.length ? csi300Curve : [],
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: "#f59e0b", type: "dashed" }
        },
        {
          name: "Taotie Baseline (Full Universe Executable)",
          type: "line",
          data: taotieCurve && taotieCurve.length ? taotieCurve : [],
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: "#94a3b8", type: "dotted" }
        },
        {
          name: `Current: ${targetPath.path_id} (${targetPath.total_return_pct >= 0 ? '+' : ''}${targetPath.total_return_pct.toFixed(2)}%)`,
          type: "line",
          data: targetCurve,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3, color: "#38bdf8" },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(56, 189, 248, 0.28)" },
              { offset: 1, color: "rgba(56, 189, 248, 0.0)" }
            ])
          }
        }
      ];

      legendData = [
        `Current: ${targetPath.path_id} (${targetPath.total_return_pct >= 0 ? '+' : ''}${targetPath.total_pct || targetPath.total_return_pct >= 0 ? '+' : ''}${targetPath.total_return_pct.toFixed(2)}%)`,
        `Monkey 90% Null Envelope (P05 ~ P95)`,
        `Monkey Median Null (${med >= 0 ? '+' : ''}${med.toFixed(2)}%)`,
        "Taotie Baseline (Full Universe Executable)",
        "CSI 300 Index (SH000300)"
      ];
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
              html += `<div style="display:flex; justify-content:space-between; gap:12px; font-size:11px; color:#c084fc;">
                <span>🟣 90% Monkey Envelope:</span>
                <b>${low.toFixed(4)} ~ ${high}</b>
              </div>`;
            } else {
              const formattedVal = (metricType === "drawdown" || metricType === "excess_csi300")
                ? `${typeof val === 'number' ? (val >= 0 && metricType === "excess_csi300" ? '+' : '') + val.toFixed(2) : val}%`
                : (typeof val === 'number' ? val.toFixed(4) : val);
              html += `<div style="display:flex; justify-content:space-between; gap:12px; font-size:11px;">
                <span style="color:${item.color};">${item.seriesName.split(' (')[0]}:</span>
                <b>${formattedVal}</b>
              </div>`;
            }
          });
          return html;
        }
      },
      legend: {
        data: legendData,
        textStyle: { color: tc.textSecondary, fontSize: 11 },
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
                  formatter: `Actual: ${actualReturnPct >= 0 ? '+' : ''}${actualReturnPct.toFixed(2)}%\n(Rank: ${pctRank.toFixed(1)}%, p=${pValue.toFixed(4)})`,
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

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        trigger: "axis",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary }
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
      series: [
        {
          name: `Chosen: ${chosenName}`,
          type: "line",
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: chosenCurve,
          lineStyle: { width: 2.5, color: "#10b981" },
          showSymbol: false
        },
        {
          name: `Rejected: ${rejectedName}`,
          type: "line",
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: rejectedCurve,
          lineStyle: { width: 2.5, color: "#f43f5e", type: "dashed" },
          showSymbol: false
        },
        {
          name: "Counterfactual Regret (NAV_rej - NAV_cho)",
          type: "line",
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: regretCurve,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(244, 63, 94, 0.3)" },
              { offset: 1, color: "rgba(16, 185, 129, 0.3)" }
            ])
          },
          lineStyle: { width: 2, color: "#f59e0b" },
          showSymbol: false
        }
      ]
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
          { name: "Sloth (Cash Lag)", type: "line", data: fingerprints.delayData.sloth, lineStyle: { color: "#38bdf8", width: 2 } },
          { name: "Snail (Holding Lag)", type: "line", data: fingerprints.delayData.snail, lineStyle: { color: "#f59e0b", width: 2 } }
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
        series: [{ type: "line", data: bVals, smooth: true, lineStyle: { color: "#a855f7", width: 2.5 } }]
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
          series.push({
            name: `${p.animal_id} (MDD: -${p.max_drawdown_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            lineStyle: {
              width: p.animal_id === "robot" ? 3 : (p.animal_id === "koala" ? 2.5 : 1.8),
              color: p.animal_id === "robot" ? "#38bdf8" : (p.animal_id === "koala" ? "#f43f5e" : colorPalette[idx % colorPalette.length]),
              type: p.animal_id === "koala" ? "dashed" : "solid"
            }
          });
        }
      });

      const taotieDD = window.arenaAdapter.getTaotieDrawdown();
      if (taotieDD && taotieDD.length > 0) {
        series.push({
          name: "Taotie Drawdown",
          type: "line",
          data: taotieDD,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: "#94a3b8", type: "dotted" }
        });
      }

      const csi300DD = window.arenaAdapter.getCsi300Drawdown();
      if (csi300DD && csi300DD.length > 0) {
        series.push({
          name: "CSI 300 Drawdown",
          type: "line",
          data: csi300DD,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: "#f59e0b", type: "dashed" }
        });
      }

    } else if (metricType === "excess_csi300") {
      titleText = "Multi-Animal Active Spread vs. CSI 300";
      yAxisName = "Excess vs. CSI 300 (%)";
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;

      paths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getPathExcessCSI300(p.path_id);
        if (curve && curve.length > 0) {
          series.push({
            name: `${p.animal_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            lineStyle: {
              width: p.animal_id === "robot" ? 3 : (p.animal_id === "koala" ? 2.5 : 1.8),
              color: p.animal_id === "robot" ? "#38bdf8" : (p.animal_id === "koala" ? "#f43f5e" : colorPalette[idx % colorPalette.length]),
              type: p.animal_id === "koala" ? "dashed" : "solid"
            }
          });
        }
      });

      const zeroBase = dates.map(() => 0.0);
      series.push({
        name: "CSI 300 Benchmark (0.00%)",
        type: "line",
        data: zeroBase,
        lineStyle: { width: 2, color: "#f59e0b", type: "dashed" },
        showSymbol: false
      });

      const taotieExcess = window.arenaAdapter.getPathExcessCSI300("BENCHMARK_taotie");
      if (taotieExcess && taotieExcess.length > 0) {
        series.push({
          name: "Taotie vs. CSI 300",
          type: "line",
          data: taotieExcess,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: "#94a3b8", type: "dotted" }
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
          series.push({
            name: `${p.animal_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            lineStyle: {
              width: p.animal_id === "robot" ? 3 : (p.animal_id === "koala" ? 2.5 : 1.8),
              color: p.animal_id === "robot" ? "#38bdf8" : (p.animal_id === "koala" ? "#f43f5e" : colorPalette[idx % colorPalette.length]),
              type: p.animal_id === "koala" ? "dashed" : "solid"
            }
          });
        }
      });

      if (taotieCurve && taotieCurve.length > 0) {
        series.push({
          name: "Taotie Baseline (+2.32%)",
          type: "line",
          data: taotieCurve,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: "#94a3b8", type: "dotted" }
        });
      }

      if (csi300Curve && csi300Curve.length > 0) {
        series.push({
          name: "CSI 300 Index (-4.81%)",
          type: "line",
          data: csi300Curve,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: "#f59e0b", type: "dashed" }
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
            html += `<div style="display:flex; justify-content:space-between; gap:12px; font-size:11px;">
              <span style="color:${item.color};">${item.seriesName.split(' (')[0]}:</span>
              <b>${formattedVal}</b>
            </div>`;
          });
          return html;
        }
      },
      legend: {
        type: "scroll",
        top: 25,
        textStyle: { color: tc.textSecondary, fontSize: 10 }
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
    const fallbackPalette = ['#38bdf8', '#10b981', '#a855f7', '#ec4899', '#f97316', '#eab308'];

    const series = [];
    let titleText = "";
    let yAxisName = "";
    let yAxisFormatter = null;

    if (metricType === "drawdown") {
      titleText = "Cross-Model Underwater Drawdown Comparison";
      yAxisName = "Drawdown (%)";
      yAxisFormatter = v => `${v.toFixed(1)}%`;

      animalPaths.forEach((p, idx) => {
        const dd = window.arenaAdapter.getPathDrawdown(p.path_id);
        if (dd && dd.length > 0) {
          const color = modelColors[p.contestant_id] || fallbackPalette[idx % fallbackPalette.length];
          series.push({
            name: `${p.contestant_id} (Max: -${p.max_drawdown_pct.toFixed(1)}%)`,
            type: "line",
            data: dd,
            smooth: true,
            showSymbol: false,
            lineStyle: { width: 2, color }
          });
        }
      });

      const csi300DD = window.arenaAdapter.getCsi300Drawdown();
      if (csi300DD && csi300DD.length > 0) {
        series.push({
          name: "CSI 300 Index Drawdown",
          type: "line",
          data: csi300DD,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#64748b", type: "dashed" }
        });
      }

      const taotieDD = window.arenaAdapter.getTaotieDrawdown();
      if (taotieDD && taotieDD.length > 0) {
        series.push({
          name: "Taotie Baseline Drawdown",
          type: "line",
          data: taotieDD,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#94a3b8", type: "dotted" }
        });
      }

    } else if (metricType === "excess_csi300") {
      titleText = "Cross-Model Active Excess Return vs. CSI 300";
      yAxisName = "Excess vs. CSI 300 (%)";
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;

      animalPaths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getPathExcessCSI300(p.path_id);
        if (curve && curve.length > 0) {
          const color = modelColors[p.contestant_id] || fallbackPalette[idx % fallbackPalette.length];
          series.push({
            name: `${p.contestant_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            lineStyle: { width: 2, color }
          });
        }
      });

      const zeroBase = dates.map(() => 0.0);
      series.push({
        name: "CSI 300 Benchmark (0.00%)",
        type: "line",
        data: zeroBase,
        lineStyle: { width: 1.8, color: "#64748b", type: "dashed" },
        showSymbol: false
      });

      const taotieExcess = window.arenaAdapter.getPathExcessCSI300("BENCHMARK_taotie");
      if (taotieExcess && taotieExcess.length > 0) {
        series.push({
          name: "Taotie vs. CSI 300",
          type: "line",
          data: taotieExcess,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#94a3b8", type: "dotted" }
        });
      }

    } else {
      // Default: NAV
      titleText = "Cross-Model Trajectory Overlay";
      yAxisName = "Cumulative NAV";
      yAxisFormatter = v => v.toFixed(4);

      animalPaths.forEach((p, idx) => {
        const curve = window.arenaAdapter.getNavCurve(p.path_id);
        if (curve && curve.length > 0) {
          const color = modelColors[p.contestant_id] || fallbackPalette[idx % fallbackPalette.length];
          series.push({
            name: `${p.contestant_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: true,
            showSymbol: false,
            lineStyle: { width: 2.2, color }
          });
        }
      });

      if (taotieCurve && taotieCurve.length > 0) {
        series.push({
          name: `Taotie Baseline (${window.arenaAdapter.getTaotieReturn() >= 0 ? '+' : ''}${window.arenaAdapter.getTaotieReturn().toFixed(2)}%)`,
          type: "line",
          data: taotieCurve,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#94a3b8", type: "dotted" }
        });
      }

      if (csi300Curve && csi300Curve.length > 0) {
        series.push({
          name: `CSI 300 Index (${window.arenaAdapter.getCsi300Return() >= 0 ? '+' : ''}${window.arenaAdapter.getCsi300Return().toFixed(2)}%)`,
          type: "line",
          data: csi300Curve,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 1.8, color: "#64748b", type: "dashed" }
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
            html += `<div style="display:flex; justify-content:space-between; gap:12px; font-size:11px;">
              <span style="color:${item.color};">${item.seriesName.split(' (')[0]}:</span>
              <b>${formattedVal}</b>
            </div>`;
          });
          return html;
        }
      },
      legend: {
        type: "scroll",
        top: 25,
        textStyle: { color: tc.textSecondary, fontSize: 11 }
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
      series: series
    };

    chart.setOption(option, true);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  }
};
