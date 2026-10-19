/**
 * web/js/components/charts.js
 * ===========================
 * QuantPits-Arena ECharts Visualization Suite (English Edition)
 * Includes:
 *   1. Return vs. Monkey Percentile Significance Scatter Plot
 *   2. Contestant × Animal Handler Heatmap Matrix
 *   3. Multi-Line Equity Curves with daily pointwise monkey quantiles & Benchmarks (Taotie & CSI 300)
 *   4. Monkey Null Distribution Boxplot with Significance Marker
 *   5. Decision Archaeology Regret Curve & Area Spread
 *   6. Behavioral Fingerprint Analysis Group (Delay, Turnover, Capacity, Polarity, Meerkat)
 *   7. Contestant Multi-Animal Execution Comparison Chart
 */

window.ArenaCharts = {
  charts: new Set(),
  renderTokens: new WeakMap(),

  formatCurveValue(value, metric = 'nav') {
    if (!Number.isFinite(value)) return 'N/A';
    if (metric === 'drawdown') return `${value.toFixed(2)}%`;
    if (metric === 'excess_csi300') return `${value >= 0 ? '+' : ''}${value.toFixed(2)} pp`;
    return value.toFixed(4);
  },

  trackChart(chart) {
    this.charts.add(chart);
    if (!this.resizeBound) {
      this.resizeBound = true;
      window.addEventListener('resize', () => {
        for (const current of this.charts) {
          if (current.isDisposed?.() || current.getDom?.()?.isConnected === false) {
            if (!current.isDisposed?.()) current.dispose?.();
            this.charts.delete(current);
          } else current.resize();
        }
      });
    }
    return chart;
  },

  disposeWithin(container) {
    for (const chart of this.charts) {
      const dom = chart.getDom?.();
      if (dom && container.contains?.(dom)) {
        chart.dispose?.();
        this.charts.delete(chart);
      }
    }
  },

  disposeAll() {
    for (const chart of this.charts) chart.dispose?.();
    this.charts.clear();
    this.renderTokens = new WeakMap();
  },

  beginViewRender(container) {
    if (!container) return () => false;
    this.disposeWithin(container);
    const tokens = this.renderTokens, token = {};
    const adapter = window.arenaAdapter;
    tokens.set(container, token);
    return () => container.isConnected !== false && this.renderTokens === tokens && tokens.get(container) === token && window.arenaAdapter === adapter;
  },

  renderPairComparison(domId, data) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const chart = this.trackChart(echarts.getInstanceByDom(dom) || echarts.init(dom));
    const colors = this.getThemeColors();
    const color = id => window.ArenaColors.subject(id);
    chart.setOption({backgroundColor:'transparent',color:[color(data.referenceId),color(data.candidateId),colors.spread],
      legend:{data:[data.referenceId,data.candidateId,'Difference (pp)'],textStyle:{color:colors.textPrimary}},
      grid:[{left:65,right:25,top:45,height:'48%'},{left:65,right:25,top:'64%',height:'20%'}],
      axisPointer:{link:[{xAxisIndex:'all'}]},tooltip:{trigger:'axis',valueFormatter:v => typeof v==='number'?v.toFixed(4):'—'},
      xAxis:[{type:'category',data:data.dates,gridIndex:0},{type:'category',data:data.dates,gridIndex:1}],
      yAxis:[{type:'value',scale:true,name:'NAV',gridIndex:0},{type:'value',name:'pp',gridIndex:1}],
      dataZoom:[{type:'inside',xAxisIndex:[0,1]},{type:'slider',xAxisIndex:[0,1],bottom:5}],
      series:[{name:data.referenceId,type:'line',data:data.reference,smooth:false,symbol:'none'},
        {name:data.candidateId,type:'line',data:data.candidate,smooth:false,symbol:'none'},
        {name:'Difference (pp)',type:'line',data:data.spread,xAxisIndex:1,yAxisIndex:1,smooth:false,symbol:'none',
          markLine:{silent:true,symbol:'none',data:[{yAxis:0}]}}]},true);
  },

  getThemeColors() {
    const isDark = window.ArenaColors.isDark();
    const semantic = window.ArenaColors.semantic();
    return {
      isDark,
      bg: "transparent",
      textPrimary: isDark ? "#f8fafc" : "#0f172a",
      textSecondary: isDark ? "#94a3b8" : "#475569",
      textMuted: "#64748b",
      gridLine: isDark ? "rgba(255, 255, 255, 0.07)" : "rgba(0, 0, 0, 0.08)",
      tooltipBg: isDark ? "rgba(15, 23, 42, 0.92)" : "rgba(255, 255, 255, 0.95)",
      tooltipBorder: isDark ? "rgba(255, 255, 255, 0.15)" : "rgba(0, 0, 0, 0.15)",
      ...semantic,
      accentBlue: semantic.info,
      accentPurple: semantic.purple,
      accentGreen: semantic.positive,
      accentRose: semantic.negative,
      accentAmber: semantic.warning
    };
  },

  toggleBenchmark(domId, benchmarkKey, forceState) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    const chart = echarts.getInstanceByDom(dom);
    if (!chart) return;
    const opt = chart.getOption();
    if (!opt || !opt.series) return;

    const currentLegend = (Array.isArray(opt.legend) ? opt.legend[0] : opt.legend) || {};
    const selected = Object.assign({}, currentLegend.selected || {});

    opt.series.forEach(s => {
      const sName = s.name || "";
      const marketName = window.arenaAdapter.getMarketBenchmarkName().toLowerCase();
      // A spread can mention two references. Its owner, rather than its denominator, controls visibility.
      const role = s.benchmarkKey || (/ghost/i.test(sName) ? 'ghost'
        : /taotie|executable passive/i.test(sName) ? 'taotie'
        : /monkey/i.test(sName) ? 'monkey'
        : (s.isMarketBenchmark || sName.toLowerCase().includes(marketName)) ? 'market' : null);
      const match = role === (benchmarkKey === 'csi300' ? 'market' : benchmarkKey);
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

    const data = paths.filter(p => p.full_season_eligible !== false && Number.isFinite(p.percentile_rank)).map(p => {
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
          const pct = window.formatPercentile ? window.formatPercentile(rawPct) : window.formatNumber(rawPct, 1, '%');
          const rawP = p.empirical_p_value !== undefined ? p.empirical_p_value : p.p_value;
          const pVal = window.formatPValue ? window.formatPValue(rawP) : window.formatNumber(rawP, 4);
          const pLabel = pVal.startsWith("<") ? `p ${pVal}` : `p = ${pVal}`;
          return `
            <div style="font-weight:700; color:${tc.accentBlue}; margin-bottom:4px;">${p.path_id}</div>
            <div style="font-size:12px; line-height:1.5;">
              <div>Model: <b>${p.contestant_id}</b> | Handler: <b>${p.animal_id}</b></div>
              <div>Return: <b style="color:${p.total_return_pct >= 0 ? tc.accentGreen : tc.accentRose}">${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</b></div>
              <div>Monkey Percentile: <b>${pct}</b> (${pLabel})</div>
              <div>Max Drawdown: <b style="color:${tc.accentRose};">${window.formatNumber(p.max_drawdown_pct, 2, '%')}</b> | Sharpe: <b>${window.formatNumber(p.sharpe_ratio)}</b></div>
              <div style="margin-top:4px; font-size:11px; color:${tc.textSecondary};">Click bubble to inspect path details</div>
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
        name: "Matched Null Percentile Rank (%)",
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
            color: params => window.ArenaColors.animal(params.data[3].animal_id),
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
                lineStyle: { color: tc.accentGreen, type: "dashed", width: 2 },
                label: { formatter: "p = 0.05 (95th Percentile)", position: "insideEndTop", color: tc.accentGreen, fontSize: 10 }
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

    this.trackChart(chart);
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
    // Legacy matrix rows can predate admissions; paths provide each metric on its own period.
    const contestants = window.arenaAdapter.getAllContestants().map(c => c.id);
    const animals = (matrixData.columns || []).filter(a => a !== "taotie");

    const data = [];
    let minVal = Infinity;
    let maxVal = -Infinity;

    contestants.forEach((cId, yIdx) => {
      animals.forEach((aId, xIdx) => {
        const pathId = `${cId}_${aId}`;
        const path = window.arenaAdapter.getPath(pathId);
        let val = null;
        if (path) {
          if (metricKey === "total_return_pct") val = path.total_return_pct;
          else if (metricKey === "percentile_rank" || metricKey === "monkey_percentile") {
            val = path.percentile_rank ?? path.monkey_percentile ?? null;
          } else if (metricKey === "max_drawdown_pct") val = path.max_drawdown_pct;
          else if (metricKey === "sharpe_ratio") val = path.sharpe_ratio;
        }
        // Dimension 0: xIdx, Dimension 1: yIdx, Dimension 2: val (numeric metric for visualMap), Dimension 3: pathId
        if (Number.isFinite(val)) {
          minVal = Math.min(minVal, val);
          maxVal = Math.max(maxVal, val);
          data.push([xIdx, yIdx, val, pathId]);
        } else {
          data.push({value:[xIdx, yIdx, null, pathId],
            itemStyle:{color:tc.isDark ? '#1e293b' : '#e2e8f0'}, label:{show:true,formatter:'N/A'}});
        }
      });
    });

    if (minVal === Infinity) { minVal = 0; maxVal = 10; }

    const isPctRank = metricKey.includes("percentile");
    const inRangeColors = isPctRank
      ? [tc.isDark ? "#1e293b" : "#e2e8f0", "#4338ca", "#7c3aed", "#c026d3", tc.accentGreen]
      : (metricKey === "max_drawdown_pct"
        ? ["#047857", tc.accentGreen, tc.accentAmber, tc.accentRose, "#991b1b"]
        : (metricKey === "sharpe_ratio"
          ? ["#dc2626", "#f97316", tc.accentBlue, tc.accentGreen, "#059669"]
          : ["#dc2626", "#ea580c", tc.isDark ? "#334155" : "#e2e8f0", "#0ea5e9", tc.accentGreen, "#059669"]));

    const option = {
      backgroundColor: tc.bg,
      tooltip: {
        position: "top",
        backgroundColor: tc.tooltipBg,
        borderColor: tc.tooltipBorder,
        textStyle: { color: tc.textPrimary },
        formatter: (params) => {
          const cell = params.value || params.data?.value || params.data;
          const pathId = cell && cell[3];
          const p = window.arenaAdapter.getPath(pathId);
          if (!p) return "No data";
          const rank = p.percentile_rank ?? p.monkey_percentile ?? null;
          const pct = window.formatPercentile ? window.formatPercentile(rank) : window.formatNumber(rank, 1, '%');
          return `
            <div style="font-weight:700; color:${tc.accentBlue};">${p.path_id}</div>
            <div>${p.observation_start ? 'Observation' : 'Full season'}: ${p.observation_start || window.arenaAdapter.getNavDates()[0]} → ${window.arenaAdapter.getNavDates().at(-1)}</div>
            <div>Return: <b style="color:${p.total_return_pct >= 0 ? tc.accentGreen : tc.accentRose}">${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%</b></div>
            <div>Drawdown: <b>${window.formatNumber(p.max_drawdown_pct, 2, '%')}</b> | Sharpe: <b>${window.formatNumber(p.sharpe_ratio)}</b></div>
            <div>Monkey Percentile: <b>${pct}</b></div>
            <div style="font-size:10px; color:${tc.textSecondary}; margin-top:3px;">Click cell to inspect details</div>
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
        axisLabel: {
          color: tc.textSecondary, fontWeight: 600, fontSize: 11,
          formatter: id => {
            const start = window.arenaAdapter.getContestant(id)?.observation_start;
            return start ? `${id}\nsince ${start}` : id;
          }
        }
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
              const cell = params.value || params.data?.value || params.data;
              const text = window.formatNumber(cell[2], isPctRank ? 0 : 1);
              // Read the rendered fill so dragging visualMap also keeps labels legible.
              const rendered = chart.getModel?.()?.getSeriesByIndex(0)?.getData();
              const background = rendered?.getItemVisual(params.dataIndex, 'style')?.fill;
              const ink = background && window.ArenaColors.textOn(background);
              return ink ? `{${ink === '#000000' ? 'dark' : 'light'}|${text}}` : text;
            },
            rich: {dark: {color: '#000000'}, light: {color: '#ffffff'}},
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
      const cell = params.value || params.data?.value || params.data;
      const pathId = cell && cell[3];
      if (pathId && typeof onCellClick === "function") {
        const path = window.arenaAdapter.getPath(pathId);
        if (path) onCellClick(path);
      }
    });

    this.trackChart(chart);
    return chart;
  },

  /**
   * 3. Multi-Line Equity Curves with daily pointwise monkey quantiles & Benchmarks (Taotie & CSI 300)
   */
  renderEquityCurves(domId, dates, targetPath, taotieCurve = [], csi300Curve = [], monkeyDist = null, metricType = "nav") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    if (!dates || !Array.isArray(dates) || dates.length === 0) return null;
    const tc = this.getThemeColors();
    const pathColor = targetPath.contestant_id === "BENCHMARK" ? window.ArenaColors.subject(targetPath.path_id) : window.ArenaColors.animal(targetPath.animal_id);
    if (targetPath.observation_start) {
      const first=dates.indexOf(targetPath.observation_start);
      if(first<0)return null;
      const windowDates=dates.slice(first);
      const normalize=values=>{
        const selected=values.slice(first);
        const base=selected[0];
        return windowDates.map((_,i)=>Number.isFinite(base)&&base>0&&Number.isFinite(selected[i])&&selected[i]>0
          ? selected[i]/base : null);
      };
      const target=normalize(window.arenaAdapter.getNavCurve(targetPath.path_id));
      const market=normalize(csi300Curve), passive=normalize(taotieCurve);
      const underwater=values=>{let peak=1;return values.map(v=>{if(v==null)return null;peak=Math.max(peak,v);return(v/peak-1)*100;});};
      let selected=[{name:targetPath.contestant_id,data:target},
        {name:window.arenaAdapter.getMarketBenchmarkName(),data:market,benchmarkKey:'market'},
        {name:window.arenaAdapter.getTaotieShortName(),data:passive,benchmarkKey:'taotie'}];
      if(window.arenaAdapter.hasGhostTaotie())selected.push({name:'Ghost Capital Scenario',benchmarkKey:'ghost',
        data:normalize(window.arenaAdapter.getBenchmarkGhostTaotieCurve())});
      if(metricType==='drawdown')selected=selected.map(s=>({...s,data:underwater(s.data)}));
      if(metricType==='excess_csi300')selected=selected.map(s=>({...s,data:s.data.map((v,i)=>v==null||market[i]==null?null:(v-market[i])*100)}));
      chart.setOption({backgroundColor:tc.bg,tooltip:{trigger:'axis',backgroundColor:tc.tooltipBg,borderColor:tc.tooltipBorder,
        textStyle:{color:tc.textPrimary},valueFormatter:v=>this.formatCurveValue(v,metricType)},
        legend:{data:selected.map(s=>s.name),textStyle:{color:tc.textSecondary}},grid:{left:65,right:25,top:45,bottom:55},
        xAxis:{type:'category',data:windowDates,axisLabel:{color:tc.textSecondary}},yAxis:{type:'value',scale:true,
          axisLabel:{color:tc.textSecondary},nameTextStyle:{color:tc.textSecondary},splitLine:{lineStyle:{color:tc.gridLine}},name:metricType==='nav'?'NAV':metricType==='drawdown'?'%':'pp'},
        series:selected.map(s=>{const color=s.benchmarkKey?tc[s.benchmarkKey]:pathColor;
          return {...s,type:'line',smooth:false,symbol:'none',itemStyle:{color},
            lineStyle:{color,type:s.benchmarkKey?({market:[6,6],taotie:[4,4],ghost:[8,4]})[s.benchmarkKey]:'solid'}};}),dataZoom:[{type:'inside'},{type:'slider'}]},true);
      this.trackChart(chart);
      return chart;
    }
    const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
    const taotieName = (window.arenaAdapter && window.arenaAdapter.getTaotieShortName) ? window.arenaAdapter.getTaotieShortName() : "Taotie";

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
          color: tc.market,
          itemStyle: { color: tc.market },
          lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 }
        },
        {
          name: taotieName,
          type: "line",
          data: taotieDD,
          smooth: true,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        }
      ];

      legendData = [
        `Path: ${targetPath.path_id}`
      ];

      if (ghostDD && ghostDD.length > 0) {
        series.push({
          name: "Ghost Capital Scenario",
          type: "line",
          data: ghostDD,
          smooth: true,
          showSymbol: false,
          color: tc.ghost,
          itemStyle: { color: tc.ghost },
          lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
        });
      }

      series.push({
        name: `Path: ${targetPath.path_id}`,
        type: "line",
        data: targetDD,
        smooth: true,
        showSymbol: false,
        color: pathColor,
        itemStyle: { color: pathColor },
        lineStyle: { width: 2.5, color: pathColor, type: "solid" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: window.ArenaColors.alpha(pathColor, 0.35) },
            { offset: 1, color: window.ArenaColors.alpha(pathColor, 0.04) }
          ])
        }
      });

    } else if (metricType === "excess_csi300") {
      yAxisName = `Active Excess Return vs. ${marketBmName} (pp)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)} pp`;

      const targetExcess = window.arenaAdapter.getPathExcessMarket(targetPath.path_id);
      const taotieExcess = window.arenaAdapter.getPathExcessMarket("BENCHMARK_taotie");
      const ghostExcess = window.arenaAdapter.hasGhostTaotie() ? window.arenaAdapter.getPathExcessMarket("BENCHMARK_ghost_taotie") : null;
      const zeroBase = dates.map(() => 0.0);

      series = [
        {
          name: `${marketBmName} (0.00%)`,
          type: "line",
          data: zeroBase,
          color: tc.market,
          itemStyle: { color: tc.market },
          lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 },
          showSymbol: false
        },
        {
          name: `Taotie vs ${marketBmName}`,
          type: "line",
          data: taotieExcess,
          smooth: true,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
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
          color: tc.ghost,
          itemStyle: { color: tc.ghost },
          lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
        });
      }

      series.push({
        name: `Active Spread: ${targetPath.path_id}`,
        type: "line",
        data: targetExcess,
        smooth: true,
        showSymbol: false,
        color: pathColor,
        itemStyle: { color: pathColor },
        lineStyle: { width: 2.5, color: pathColor, type: "solid" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: window.ArenaColors.alpha(pathColor, 0.30) },
            { offset: 1, color: window.ArenaColors.alpha(pathColor, 0.02) }
          ])
        }
      });

    } else {
      // Default: Cumulative NAV
      const targetCurve = window.arenaAdapter.getNavCurve(targetPath.path_id);
      const dailySnapshots = monkeyDist?.daily_quantiles;
      const hasDaily = dailySnapshots && Object.keys(dailySnapshots).length > 0;
      const snapshots = hasDaily ? dailySnapshots : (monkeyDist?.settlement_quantiles || {});
      const sample = key => dates.map(d => snapshots[d]?.[key] ?? null);
      const targetLabel = `Path: ${targetPath.path_id}`;
      series = [
        ...[['p05','Monkey P05',tc.monkey],['p95','Monkey P95',tc.monkey],['median','Monkey Median',tc.monkey]].map(([key,name,color]) => ({
          name,type:hasDaily ? 'line' : 'scatter',data:sample(key),color,
          smooth:false,showSymbol:false,symbolSize:4,connectNulls:false,
          lineStyle:{width:key==='median' ? 1.5 : 1,type:'dashed'}
        })),
        {
          name: marketBmName,
          type: "line",
          data: csi300Curve && csi300Curve.length ? csi300Curve : [],
          smooth: true,
          showSymbol: false,
          color: tc.market,
          itemStyle: { color: tc.market },
          lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 }
        },
        {
          name: taotieName,
          type: "line",
          data: taotieCurve && taotieCurve.length ? taotieCurve : [],
          smooth: true,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        }
      ];

      legendData = [
        "Monkey P05", "Monkey P95", "Monkey Median", targetLabel
      ];

      if (window.arenaAdapter && window.arenaAdapter.hasGhostTaotie()) {
        const ghostCurve = window.arenaAdapter.getBenchmarkGhostTaotieCurve();
        if (ghostCurve && ghostCurve.length > 0) {
          series.push({
            name: "Ghost Capital Scenario",
            type: "line",
            data: ghostCurve,
            smooth: true,
            showSymbol: false,
            color: tc.ghost,
            itemStyle: { color: tc.ghost },
            lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
          });
        }
      }

      series.push({
        name: targetLabel,
        type: "line",
        data: targetCurve,
        smooth: true,
        showSymbol: false,
        color: pathColor,
        itemStyle: { color: pathColor },
        lineStyle: { width: 3, color: pathColor, type: "solid" },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: window.ArenaColors.alpha(pathColor, 0.28) },
            { offset: 1, color: window.ArenaColors.alpha(pathColor, 0.0) }
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
          let html = `<div style="font-weight:700; margin-bottom:6px; color:${tc.accentBlue};">${date}</div>`;
          params.forEach(item => {
            if (item.seriesName === "Monkey P05 Base") return;
            let val = item.value;
            if (item.seriesName.includes("Null Envelope")) {
              const idx = item.dataIndex;
              const low = monkeyLower[idx] || 0;
              const high = (low + val).toFixed(4);
              html += `<div style="display:flex; justify-content:space-between; align-items:center; gap:12px; font-size:11px; color:${tc.taotie};">
                <span>${item.marker || '🟣'} 90% Monkey Envelope:</span>
                <b>${low.toFixed(4)} ~ ${high}</b>
              </div>`;
            } else {
              const formattedVal = this.formatCurveValue(val, metricType);
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
    this.trackChart(chart);
    return chart;
  },

  /**
   * 4. Monkey Null Distribution Boxplot with Significance Marker
   */
  renderMonkeyDistribution(domId, monkeyDist, actualReturnPct, pctRank, pValue, animalId = "robot") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    const tc = this.getThemeColors();
    if (!monkeyDist) return null;

    const parse = v => {
      if (v === undefined || v === null || isNaN(parseFloat(String(v).replace("%", "")))) return 0;
      return parseFloat(String(v).replace("%", ""));
    };
    const minVal = parse(monkeyDist.monkey_min ?? monkeyDist.min_return_pct);
    const p05 = parse(monkeyDist.monkey_p05 ?? monkeyDist.p05_return_pct);
    const med = parse(monkeyDist.monkey_median ?? monkeyDist.median_return_pct);
    const p95 = parse(monkeyDist.monkey_p95 ?? monkeyDist.p95_return_pct);
    const maxVal = parse(monkeyDist.monkey_max ?? monkeyDist.max_return_pct);

    const xMin = Math.min(minVal, actualReturnPct) - 2.0;
    const xMax = Math.max(maxVal, actualReturnPct) + 3.0;

    const option = {
      backgroundColor: tc.bg,
      title: {
        text: monkeyDist.deterministic ? "Deterministic Passive Reference (p N/A)" : `${Number(monkeyDist.colony_size || 0).toLocaleString()}-Path Null Range [P05 ~ P95] vs Actual Return`,
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
          name: "Random-control P05/P95 Range",
          tooltip: {formatter: () => `Min ${minVal.toFixed(4)}%<br>P05 ${p05.toFixed(4)}%<br>Median ${med.toFixed(4)}%<br>P95 ${p95.toFixed(4)}%<br>Max ${maxVal.toFixed(4)}%`},
          type: "boxplot",
          data: [[minVal, p05, med, p95, maxVal]],
          itemStyle: {
            color: window.ArenaColors.alpha(tc.monkey, 0.2),
            borderColor: tc.monkey,
            borderWidth: 2
          },
          markLine: {
            silent: false,
            symbol: ["none", "none"],
            lineStyle: { color: window.ArenaColors.animal(animalId), width: 3, type: "solid" },
            data: [
              {
                xAxis: actualReturnPct,
                label: {
                  formatter: () => {
                    const pctStr = window.formatPercentile ? window.formatPercentile(pctRank, monkeyDist.colony_size) : window.formatNumber(pctRank, 1, '%');
                    const pValStr = window.formatPValue ? window.formatPValue(pValue) : window.formatNumber(pValue, 4);
                    const pLabel = pValStr.startsWith("<") ? `p ${pValStr}` : `p = ${pValStr}`;
                    return `Actual: ${actualReturnPct >= 0 ? '+' : ''}${actualReturnPct.toFixed(2)}%\n(Rank: ${pctStr}, ${pLabel})`;
                  },
                  position: "end",
                  color: window.ArenaColors.animal(animalId),
                  fontWeight: 700
                }
              }
            ]
          }
        }
      ]
    };

    chart.setOption(option, true);
    this.trackChart(chart);
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
        color: window.ArenaColors.subject(chosenName),
        itemStyle: { color: window.ArenaColors.subject(chosenName) },
        lineStyle: { width: 2.5, color: window.ArenaColors.subject(chosenName) },
        showSymbol: false
      },
      {
        name: `Rejected: ${rejectedName}`,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: rejectedCurve,
        color: window.ArenaColors.subject(rejectedName),
        itemStyle: { color: window.ArenaColors.subject(rejectedName) },
        lineStyle: { width: 2.5, color: window.ArenaColors.subject(rejectedName), type: "dashed" },
        showSymbol: false
      },
      {
        name: "Counterfactual Regret (NAV_rej - NAV_cho)",
        type: "line",
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: regretCurve,
        color: tc.spread,
        itemStyle: { color: tc.spread },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: window.ArenaColors.alpha(tc.spread, 0.3) },
            { offset: 1, color: window.ArenaColors.alpha(tc.spread, 0.03) }
          ])
        },
        lineStyle: { width: 2, color: tc.spread },
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
            const color = item.color || tc.accentBlue;
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
      color: [window.ArenaColors.subject(chosenName), window.ArenaColors.subject(rejectedName), tc.spread],
      series: series
    };

    chart.setOption(option, true);
    this.trackChart(chart);
    return chart;
  },

  /**
   * 6. Behavioral Fingerprints Group
   */
  renderFingerprintGroup(domDelayId, domTurnoverId, domBreadthId, domDirectionId, fingerprints) {
    const tc = this.getThemeColors();
    const tooltip = {trigger: "axis", backgroundColor:tc.tooltipBg, borderColor:tc.tooltipBorder, textStyle:{color:tc.textPrimary}};
    const point = (value, animal) => value == null ? null : ({value, itemStyle:{color:window.ArenaColors.animal(animal)}});

    // A. Delay Sensitivity
    const domDelay = document.getElementById(domDelayId);
    if (domDelay) {
      let c1 = echarts.getInstanceByDom(domDelay) || echarts.init(domDelay);
      c1.setOption({
        backgroundColor: tc.bg,
        title: { text: "Delay Sensitivity (Execution Lag)", textStyle: { color: tc.textPrimary, fontSize: 12 } },
        tooltip,
        legend: { data: ["Sloth (Cash Lag)", "Snail (Holding Lag)"], textStyle: { color: tc.textSecondary, fontSize:10 }, top: 22 },
        grid: { left: "8%", right: "8%", top: 55, bottom: "15%" },
        xAxis: { type: "category", data: ["0W", "1W", "2W", "3W", "4W"], axisLabel: { color: tc.textSecondary } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [['sloth', 'Sloth (Cash Lag)'], ['snail', 'Snail (Holding Lag)']].map(([family, name]) => {
          const color = window.ArenaColors.animal(`${family}-2`);
          return {name, type:'line', showSymbol:true, symbolSize:6, color,
            data: fingerprints.delayData[family].map((value,i)=>point(value,i?`${family}-${i}`:'robot')),
            itemStyle:{color}, lineStyle:{color,width:2}};
        })
      }, true);
      this.trackChart(c1);
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
        tooltip,
        grid: { left: "8%", right: "8%", top: "20%", bottom: "15%" },
        xAxis: { type: "category", data: names, axisLabel: { color: tc.textSecondary, fontSize: 10 } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [{ type: "bar", data: vals, itemStyle: { color: params => window.ArenaColors.animal(fingerprints.turnoverData[params.dataIndex].animal_id), borderRadius: [4, 4, 0, 0] } }]
      }, true);
      this.trackChart(c2);
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
        tooltip,
        grid: { left: "8%", right: "8%", top: "20%", bottom: "25%" },
        xAxis: { type: "category", data: bLabels, axisLabel: { color: tc.textSecondary, rotate: 30, fontSize: 9 } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [{type:'line', smooth:true, showSymbol:true, symbolSize:7,
          color:tc.monkey, itemStyle:{color:tc.monkey}, lineStyle:{color:tc.monkey,width:2.5},
          data:bVals.map((value,i)=>{
            if(value == null)return null;
            const row=fingerprints.breadthData[i];
            const color=row.subject_id?window.ArenaColors.subject(row.subject_id):window.ArenaColors.animal(row.animal_id);
            return {value,itemStyle:{color}};
          })
        }]
      }, true);
      this.trackChart(c3);
    }

    // D. Direction Sanity (Robot vs Koala)
    const domDir = document.getElementById(domDirectionId);
    if (domDir) {
      let c4 = echarts.getInstanceByDom(domDir) || echarts.init(domDir);
      c4.setOption({
        backgroundColor: tc.bg,
        title: { text: "Direction Sanity (Robot vs. Koala Reverse)", textStyle: { color: tc.textPrimary, fontSize: 12 } },
        tooltip,
        grid: { left: "10%", right: "8%", top: "20%", bottom: "15%" },
        xAxis: { type: "category", data: ["Robot (Top)", "Koala (Bottom)", "Spread"], axisLabel: { color: tc.textSecondary } },
        yAxis: { type: "value", splitLine: { lineStyle: { color: tc.gridLine } }, axisLabel: { color: tc.textSecondary, formatter: "{value}%" } },
        series: [{
          type: "bar",
          data: [
            { value: fingerprints.directionData.robot, itemStyle: { color: window.ArenaColors.animal("robot") } },
            { value: fingerprints.directionData.koala, itemStyle: { color: window.ArenaColors.animal("koala") } },
            { value: fingerprints.directionData.spread, itemStyle: { color: tc.spread } },
          ]
        }]
      }, true);
      this.trackChart(c4);
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
    const adapter=window.arenaAdapter;
    const anchor=paths.map(p=>p.observation_start).filter(Boolean).sort().at(-1);
    const offset=anchor?dates.indexOf(anchor):0;
    if(offset<0)throw Error('The observation anchor is not covered.');
    const normalize=values=>{
      if(!anchor)return values;
      const rows=values.slice(offset);
      const base=rows[0];
      return dates.map((_,i)=>Number.isFinite(base)&&base>0&&Number.isFinite(rows[i])&&rows[i]>0
        ? rows[i]/base : null);
    };
    if(anchor)dates=dates.slice(offset);
    taotieCurve=normalize(taotieCurve);csi300Curve=normalize(csi300Curve);
    const nav=id=>normalize(id==='BENCHMARK_taotie'?adapter.getBenchmarkTaotieCurve():
      id==='BENCHMARK_ghost_taotie'?adapter.getBenchmarkGhostTaotieCurve():adapter.getNavCurve(id));
    const drawdown=curve=>{let peak=1;return curve.map(v=>{if(v==null)return null;peak=Math.max(peak,v);return(v/peak-1)*100;});};
    const excess=curve=>curve.map((v,i)=>v==null||csi300Curve[i]==null?null:(v-csi300Curve[i])*100);
    const tc = this.getThemeColors();
    const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
    const taotieName = (window.arenaAdapter && window.arenaAdapter.getTaotieShortName) ? window.arenaAdapter.getTaotieShortName() : "Taotie";


    const series = [];
    let titleText = "Multi-Animal Execution Trajectories";
    let yAxisName = "NAV";
    let yAxisFormatter = v => v.toFixed(4);

    if (metricType === "drawdown") {
      titleText = "Multi-Animal Underwater Drawdown Trajectories";
      yAxisName = "Drawdown (%)";
      yAxisFormatter = v => `${v.toFixed(1)}%`;

      paths.forEach((p, idx) => {
        const curve = anchor?drawdown(nav(p.path_id)):adapter.getPathDrawdown(p.path_id);
        if (curve && curve.length > 0) {
          const color = window.ArenaColors.animal(p.animal_id);
          series.push({
            name: `${p.animal_id} (MDD: -${p.max_drawdown_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: false,
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

      const ghostDD = adapter.hasGhostTaotie() ? (anchor?drawdown(nav("BENCHMARK_ghost_taotie")):adapter.getGhostTaotieDrawdown()) : null;
      if (ghostDD && ghostDD.length > 0) {
        series.push({
          name: "Ghost Taotie Drawdown",
          type: "line",
          data: ghostDD,
          smooth: false,
          showSymbol: false,
          color: tc.ghost,
          itemStyle: { color: tc.ghost },
          lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
        });
      }

      const taotieDD = anchor?drawdown(taotieCurve):adapter.getTaotieDrawdown();
      if (taotieDD && taotieDD.length > 0) {
        series.push({
          name: "Taotie Drawdown",
          type: "line",
          data: taotieDD,
          smooth: false,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        });
      }

      const csi300DD = anchor?drawdown(csi300Curve):adapter.getMarketDrawdown();
      if (csi300DD && csi300DD.length > 0) {
        series.push({
          name: `${marketBmName} Drawdown`,
          type: "line",
          data: csi300DD,
          smooth: false,
          showSymbol: false,
          color: tc.market,
          itemStyle: { color: tc.market },
          lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 }
        });
      }

    } else if (metricType === "excess_csi300") {
      titleText = `Multi-Animal Active Spread vs. ${marketBmName}`;
      yAxisName = `Excess vs. ${marketBmName} (pp)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)} pp`;

      paths.forEach((p, idx) => {
        const curve = anchor?excess(nav(p.path_id)):adapter.getPathExcessMarket(p.path_id);
        if (curve && curve.length > 0) {
          const color = window.ArenaColors.animal(p.animal_id);
          series.push({
            name: `${p.animal_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: false,
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
        color: tc.market,
        itemStyle: { color: tc.market },
        lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 },
        showSymbol: false
      });

      const taotieExcess = anchor?excess(taotieCurve):adapter.getPathExcessMarket("BENCHMARK_taotie");
      if (taotieExcess && taotieExcess.length > 0) {
        series.push({
          name: `Taotie vs ${marketBmName}`,
          type: "line",
          data: taotieExcess,
          smooth: false,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        });
      }

      const ghostExcess = adapter.hasGhostTaotie() ? (anchor?excess(nav("BENCHMARK_ghost_taotie")):adapter.getPathExcessMarket("BENCHMARK_ghost_taotie")) : null;
      if (ghostExcess && ghostExcess.length > 0) {
        series.push({
          name: `Ghost Taotie vs ${marketBmName}`,
          type: "line",
          data: ghostExcess,
          smooth: false,
          showSymbol: false,
          color: tc.ghost,
          itemStyle: { color: tc.ghost },
          lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
        });
      }

    } else {
      // Default: NAV
      titleText = "Multi-Animal Execution NAV Trajectories";
      yAxisName = "NAV";
      yAxisFormatter = v => v.toFixed(4);

      paths.forEach((p, idx) => {
        const curve = nav(p.path_id);
        if (curve && curve.length > 0) {
          const color = window.ArenaColors.animal(p.animal_id);
          series.push({
            name: `${p.animal_id} (${p.total_return_pct >= 0 ? '+' : ''}${p.total_return_pct.toFixed(2)}%)`,
            type: "line",
            data: curve,
            smooth: false,
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
        const ghostCurve = nav("BENCHMARK_ghost_taotie");
        if (ghostCurve && ghostCurve.length > 0) {
          series.push({
            name: "Ghost Capital Scenario",
            type: "line",
            data: ghostCurve,
            smooth: false,
            showSymbol: false,
            color: tc.ghost,
            itemStyle: { color: tc.ghost },
            lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
          });
        }
      }

      if (taotieCurve && taotieCurve.length > 0) {
        series.push({
          name: taotieName,
          type: "line",
          data: taotieCurve,
          smooth: false,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        });
      }

      if (csi300Curve && csi300Curve.length > 0) {
        series.push({
          name: marketBmName,
          type: "line",
          data: csi300Curve,
          smooth: false,
          showSymbol: false,
          color: tc.market,
          itemStyle: { color: tc.market },
          lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 }
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
          let html = `<div style="font-weight:700; margin-bottom:6px; color:${tc.accentBlue};">${date}</div>`;
          params.forEach(item => {
            let val = item.value;
            const formattedVal = this.formatCurveValue(val, metricType);
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
        data: series.filter(s => !s.isBenchmark && !s.name.includes("Taotie") && !s.name.includes("Ghost") && !s.name.toLowerCase().includes(marketBmName.toLowerCase())).map(s => s.name),
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
    this.trackChart(chart);
    return chart;
  },

  /**
   * 8. Cross-Model Comparative Curves for a Single Animal Handler
   * Plots contestant models under the selected animal execution handler.
   * Supports: "nav", "drawdown", "excess_csi300"
   */
  renderCrossModelAnimalCurves(domId, dates, animalPaths, taotieCurve, csi300Curve, metricType = "nav") {
    const dom = document.getElementById(domId);
    if (!dom) return null;
    let chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);

    const adapter = window.arenaAdapter;
    const nav = id => adapter.getNavCurve(id);
    const tc = this.getThemeColors();
    const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";
    const taotieName = (window.arenaAdapter && window.arenaAdapter.getTaotieShortName) ? window.arenaAdapter.getTaotieShortName() : "Taotie";

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

    const getColor = p => window.ArenaColors.path(p, animalPaths).color;

    const series = [];
    let titleText = "";
    let yAxisName = "";
    let yAxisFormatter = null;

    if (metricType === "drawdown") {
      titleText = isMultiAnimal ? "Multi-Animal Underwater Drawdown Comparison" : "Cross-Model Underwater Drawdown Comparison";
      yAxisName = "Drawdown (%)";
      yAxisFormatter = v => `${v.toFixed(1)}%`;

      animalPaths.forEach((p, idx) => {
        const dd = adapter.getPathDrawdown(p.path_id);
        if (dd && dd.length > 0) {
          const color = getColor(p, idx);
          series.push({
            name: getSeriesName(p, "drawdown"),
            type: "line",
            data: dd,
            smooth: false,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: { ...window.ArenaColors.path(p, animalPaths).lineStyle, width: 2, color: color }
          });
        }
      });

      const ghostDD = adapter.hasGhostTaotie() ? adapter.getGhostTaotieDrawdown() : null;
      if (ghostDD && ghostDD.length > 0) {
        series.push({
          name: "Ghost Taotie Drawdown",
          type: "line",
          data: ghostDD,
          smooth: false,
          showSymbol: false,
          color: tc.ghost,
          itemStyle: { color: tc.ghost },
          lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
        });
      }

      const taotieDD = adapter.getTaotieDrawdown();
      if (taotieDD && taotieDD.length > 0) {
        series.push({
          name: "Taotie Drawdown",
          type: "line",
          data: taotieDD,
          smooth: false,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        });
      }

      const csi300DD = adapter.getMarketDrawdown();
      if (csi300DD && csi300DD.length > 0) {
        series.push({
          name: `${marketBmName} Drawdown`,
          type: "line",
          data: csi300DD,
          smooth: false,
          showSymbol: false,
          color: tc.market,
          itemStyle: { color: tc.market },
          lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 }
        });
      }

    } else if (metricType === "excess_csi300") {
      titleText = isMultiAnimal ? `Multi-Animal Active Excess Return vs. ${marketBmName}` : `Cross-Model Active Excess Return vs. ${marketBmName}`;
      yAxisName = `Excess vs. ${marketBmName} (pp)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)} pp`;

      animalPaths.forEach((p, idx) => {
        const curve = adapter.getPathExcessMarket(p.path_id);
        if (curve && curve.length > 0) {
          const color = getColor(p, idx);
          series.push({
            name: getSeriesName(p, "excess"),
            type: "line",
            data: curve,
            smooth: false,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: { ...window.ArenaColors.path(p, animalPaths).lineStyle, width: 2.2, color: color }
          });
        }
      });

      const zeroBase = dates.map(() => 0.0);
      series.push({
        name: `${marketBmName} (0.00%)`,
        type: "line",
        data: zeroBase,
        color: tc.market,
        itemStyle: { color: tc.market },
        lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 },
        showSymbol: false
      });

      const taotieExcess = adapter.getPathExcessMarket("BENCHMARK_taotie");
      if (taotieExcess && taotieExcess.length > 0) {
        series.push({
          name: `Taotie vs ${marketBmName}`,
          type: "line",
          data: taotieExcess,
          smooth: false,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        });
      }

      const ghostExcess = adapter.hasGhostTaotie() ? adapter.getPathExcessMarket("BENCHMARK_ghost_taotie") : null;
      if (ghostExcess && ghostExcess.length > 0) {
        series.push({
          name: `Ghost Taotie vs ${marketBmName}`,
          type: "line",
          data: ghostExcess,
          smooth: false,
          showSymbol: false,
          color: tc.ghost,
          itemStyle: { color: tc.ghost },
          lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
        });
      }

    } else {
      // Default: NAV
      titleText = isMultiAnimal ? "Multi-Animal Trajectory Overlay" : "Cross-Model Trajectory Overlay";
      yAxisName = "Cumulative NAV";
      yAxisFormatter = v => v.toFixed(4);

      animalPaths.forEach((p, idx) => {
        const curve = nav(p.path_id);
        if (curve && curve.length > 0) {
          const color = getColor(p, idx);
          series.push({
            name: getSeriesName(p, "nav"),
            type: "line",
            data: curve,
            smooth: false,
            showSymbol: false,
            color: color,
            itemStyle: { color: color },
            lineStyle: { ...window.ArenaColors.path(p, animalPaths).lineStyle, width: 2.2, color: color }
          });
        }
      });

      if (window.arenaAdapter && window.arenaAdapter.hasGhostTaotie()) {
        const ghostCurve = adapter.getBenchmarkGhostTaotieCurve();
        if (ghostCurve && ghostCurve.length > 0) {
          series.push({
            name: "Ghost Capital Scenario",
            type: "line",
            data: ghostCurve,
            smooth: false,
            showSymbol: false,
            color: tc.ghost,
            itemStyle: { color: tc.ghost },
            lineStyle: { width: 2.2, color: tc.ghost, type: [8, 4], opacity: 0.9 }
          });
        }
      }

      if (taotieCurve && taotieCurve.length > 0) {
        series.push({
          name: taotieName,
          type: "line",
          data: taotieCurve,
          smooth: false,
          showSymbol: false,
          color: tc.taotie,
          itemStyle: { color: tc.taotie },
          lineStyle: { width: 2.2, color: tc.taotie, type: [4, 4], opacity: 0.9 }
        });
      }

      if (csi300Curve && csi300Curve.length > 0) {
        series.push({
          name: marketBmName,
          type: "line",
          data: csi300Curve,
          smooth: false,
          showSymbol: false,
          color: tc.market,
          itemStyle: { color: tc.market },
          lineStyle: { width: 2.0, color: tc.market, type: [6, 6], opacity: 0.9 }
        });
      }
    }

    series.forEach(s => { s.connectNulls = false; });
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
          let html = `<div style="font-weight:700; margin-bottom:6px; color:${tc.accentBlue};">${date}</div>`;
          params.forEach(item => {
            const val = item.value;
            const formattedVal = this.formatCurveValue(val, metricType);
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
        data: series.filter(s => !s.isBenchmark && !s.name.includes("Taotie") && !s.name.includes("Ghost") && !s.name.toLowerCase().includes(marketBmName.toLowerCase())).map(s => s.name),
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
    this.trackChart(chart);
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
    const marketBmName = (window.arenaAdapter && window.arenaAdapter.getMarketBenchmarkName) ? window.arenaAdapter.getMarketBenchmarkName() : "CSI 300";

    let yAxisName = "Normalized NAV (Starting 1.0000)";
    let yAxisFormatter = v => v.toFixed(3);

    if (isExcess) {
      if (metricMode === "excess_taotie") yAxisName = "Excess Return vs Taotie (pp)";
      else if (metricMode === "excess_ghost") yAxisName = "Excess Return vs Ghost Taotie (pp)";
      else yAxisName = `Excess Return vs ${marketBmName} (pp)`;
      yAxisFormatter = v => `${v >= 0 ? '+' : ''}${v.toFixed(1)} pp`;
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
        connectNulls: false,
        showSymbol: false,
        lineStyle: {width: 2.5, color: item.color, ...item.lineStyle},
        itemStyle: { color: item.color }
      };

      if (isGhost) {
        s.lineStyle = {
          width: 2.2,
          type: [8, 4],
          color: tc.ghost,
          opacity: 0.95
        };
      } else if (isTaotie) {
        s.lineStyle = {
          width: 2.2,
          type: [4, 4],
          color: tc.taotie,
          opacity: 0.95
        };
      } else if (isCsi) {
        s.lineStyle = {
          width: 2.0,
          type: [6, 6],
          color: tc.market,
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
          let html = `<div style="font-weight:700; margin-bottom:6px; color:${tc.accentBlue};">${params[0].axisValue}</div>`;
          params.forEach(p => {
            const val = p.value;
            const displayVal = Number.isFinite(val)
              ? (isExcess || isDD ? `${val >= 0 ? '+' : ''}${val.toFixed(2)}${isExcess ? ' pp' : '%'}` : val.toFixed(4))
              : 'N/A';
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
        data: series.filter(s => !s.isBenchmark && !s.name.includes("Taotie") && !s.name.includes("Ghost") && !s.name.toLowerCase().includes(marketBmName.toLowerCase())).map(s => s.name),
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
    this.trackChart(chart);
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

    if(modelsData.some(m=>m.curve.length!==dates.length||m.curve[0]!==1||m.curve.some(v=>!Number.isFinite(v)||v<=0)))
      throw Error('Comparison curves must share the rebased window.');
    const len = dates.length;
    const spreadM1M2 = [];
    for (let i = 0; i < len; i++) {
      spreadM1M2.push((m1.curve[i] - m2.curve[i]) * 100);
    }

    const series = [
      {
        name: m1.name,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: m1.curve,
        smooth: false,
        showSymbol: false,
        lineStyle: { width: 3, color: window.ArenaColors.subject(m1.id || m1.name) },
        itemStyle: { color: window.ArenaColors.subject(m1.id || m1.name) }
      },
      {
        name: m2.name,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: m2.curve,
        smooth: false,
        showSymbol: false,
        lineStyle: { width: 3, color: window.ArenaColors.subject(m2.id || m2.name) },
        itemStyle: { color: window.ArenaColors.subject(m2.id || m2.name) }
      }
    ];

    if (m3 && m3.curve && m3.curve.length > 0) {
      series.push({
        name: m3.name,
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: m3.curve,
        smooth: false,
        showSymbol: false,
        lineStyle: {
          width: 2.5,
          color: window.ArenaColors.subject(m3.id || m3.name),
          type: m3.isBenchmark ? [8, 4, 2, 4] : "solid"
        },
        itemStyle: { color: window.ArenaColors.subject(m3.id || m3.name) }
      });
    }

    series.push({
      name: `Spread (${m1.name} − ${m2.name})`,
      type: "line",
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: spreadM1M2,
      smooth: false,
      showSymbol: false,
      lineStyle: { width: 2, color: tc.spread },
      itemStyle: { color: tc.spread },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: window.ArenaColors.alpha(tc.spread, 0.35) },
          { offset: 1, color: window.ArenaColors.alpha(tc.spread, 0.02) }
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
          name: "Spread (pp)",
          nameTextStyle: { color: tc.textSecondary, fontSize: 10 },
          splitLine: { lineStyle: { color: tc.gridLine } },
          axisLabel: { color: tc.textSecondary, formatter: v => `${v >= 0 ? '+' : ''}${v.toFixed(2)} pp` }
        }
      ],
      series: series
    };

    chart.setOption(option, true);
    this.trackChart(chart);
    return chart;
  }
};

