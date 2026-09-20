# QuantPits Arena: 赛季周频增量滚动推进操作规范 (Weekly Roll-Forward SOP)

> **文档版本**: 2.0.0  
> **适用对象**: 研发人员、量化策略维护者、自动化运维脚本、协助开发的 AI Agents  
> **安全合规**: 严格遵守 `AGENTS.md` 本地零泄密与公开就绪铁律  

---

## 1. 核心定位与架构原则

### 1.1 冷启动 (Pipeline) vs 增量推进 (Step) 的职责分离
在 QuantPits Arena 中，回测与评测生命周期严格区分为两种模式：

| 模式 | 核心命令 | 适用场景 | 算力开销 | 历史数据行为 |
| :--- | :--- | :--- | :--- | :--- |
| **全流程冷启动** | `python cli.py pipeline --season <id>` | 建立全新赛季、全量股票池切换、算法架构重大重构 | 高 (全量特征推理 + 11,000 猴群模拟) | 从 T=0 初始日重新生成全部曲线 |
| **周频增量推进** | `python cli.py step --season <id>` | 每周末行情数据更新后，按周向前滚动 1 个周期 | 极低 (~数秒至数十秒) | **基于快照追加，历史数据 100% 物理不可变** |

### 1.2 为什么严禁"手写外挂脚本"与"临时篡改 CLI 既有命令"？
- **自驱动状态机**：`cli.py step` 已完整接入 `SeasonManager` 声明式配置与 `WeeklyCycleRunner` 快照状态机。它会根据 `runs/<run_id>/checkpoints/latest_state.pkl` 自动识别当前进度，并精准仅执行目标这 1 个周期的调仓撮合与盯市估值。
- **历史不可变铁律 (Historical Immutability)**：任何通过手写脚本对底层产物（如预测库、中间状态）进行的非标准化篡改，都极易破坏历史回测净值的一致性，触发 `scripts/validate_incremental_update.py` 报错。
- **原则性新增 vs 临时篡改**：经过正式设计评审并通过全量测试的新子命令（如 `bump-date`、`rollforward`）属于架构演进，不在此禁令范畴内。

---

## 2. 极简一键全自动滚动推进 (Recommended: The Grand Roll-Forward)

当行情数据更新至最新一周收盘（例如从 `2026-09-11` 推进到 `2026-09-18`）时，**推荐使用最简一条命令完成全流程原子闭环**：

```bash
# 激活运行环境并一键原子完成：日期推进 -> 4赛季推进 -> Web导出 -> Chronicles同步 -> 隐私审计
conda activate qlib_cupy
python cli.py rollforward --end-date 2026-09-18
```

> [!TIP]
> - `rollforward` 默认会自动将变更的交易日数和截止日同步到全局与 4 个活跃赛季配置，依次执行增量 `step` 与 `export-web`，自动同步 `chronicles/en/` 到 `web/chronicles/en/`，并在末尾强制执行 `audit_privacy.py`。
> - 若本周需要同时刷新全量猴群零假设评估，只需追加 `--monkeys` 参数。

---

## 3. 标准操作分步流程 (Manual Step-by-Step)

若因调试排查需要分步控制，可按以下标准化命令执行：

### 第一步：一键配置层推进时间截断 (Declarative Horizon Bump)
不再需要手动逐个修改 5 个文件，直接使用内置 `bump-date` 命令原子更新：

```bash
python cli.py bump-date --end-date 2026-09-18
```
该命令会自动基于 `TradingCalendar` 精确计算各赛季的实际交易日数，并原子同步：
1. `arena/config.py` 中的 `DEFAULT_END_DATE`；
2. 各赛季配置 `seasons/<season_id>/season_config.yaml`（更新 `end_date` 与 banner 日期范围）；
3. 前端大盘索引 `web/js/data/seasons_index.js`（更新各赛季卡片的 `end_date`、`trading_days` 及 `period`）。

---

### 第二步：执行原生增量推进 (Rolling Incremental Step)
在包含 Qlib 与 PyTorch 的 Python 环境下，直接依次推进各赛季（`--run-id` 默认自动推导为 `{season_id}_run`）：

```bash
# 依次推进各赛季滚动 1 周
python cli.py step --season season_01
python cli.py step --season season_csi500
python cli.py step --season season_csi800
python cli.py step --season season_csi1000
```

#### `cli.py step` 内部执行细节：
1. **快照加载**：从 `runs/<season_id>_run/checkpoints/latest_state.pkl` 反序列化恢复上周已结算的 Portfolio 引擎及全量动物持仓；
2. **周期目标识别**：比对当前已完成周期 `last_completed_cycle_idx` 与最新周期上限；
3. **两阶段撮合执行**：
   - **决策阶段 (Decision)**：基于最新周五截面特征生成调仓目标订单；
   - **执行阶段 (Execution & Valuation)**：按周一开盘价成交，并记录本周 5 个交易日的 Daily MTM 估值；
4. **状态持久化与导出**：将最新状态更新为 `latest_state.pkl`，并增量写出 `daily_nav_curves.csv` 和指标汇总。

---

### 第三步：前端通用 Web 导出与隐私合规审计
增量推进完成后，使用通用导出器更新前端数据 Payload，并强制执行本地安全审计：

```bash
# 1. 导出各赛季 Web Payload (自动更新 web/js/data/<season_id>.js)
python cli.py export-web --season season_01
python cli.py export-web --season season_csi500
python cli.py export-web --season season_csi800
python cli.py export-web --season season_csi1000

# 2. 运行本地零泄密隐私审计 (强制 PASS 退出码为 0)
python3 scripts/audit_privacy.py
```

---

## 4. 常见误区与高压红线 (Anti-Patterns / Absolute Red Lines)

### 🔴 禁忌 1：严禁编写临时数据拼装脚本
- 绝对不要在 `scripts/` 或根目录下编写任何类似 `update_predictions_*.py`、`patch_*.py` 等一次性脚本；
- 如果数据层确实缺乏最新截面，唯一的正规扩充方式是使用标准命令 `python cli.py infer --universe <code] --oos-end <date>`，由原生引擎统一处理。

### 🔴 禁忌 2：严禁临时篡改 `cli.py` 既有稳定命令逻辑
- `cli.py` 的 `step`、`run`、`export-web`、`bump-date`、`rollforward` 等命令已全面支持配置化赛季解耦与参数传递；
- 绝不能以"增加参数快捷方式"为由随意篡改上述既有稳定子命令的内部撮合、导出、或快照逻辑；
- 经过正式设计评审与全量测试验证的新子命令扩展（新增 `add_parser` + `cmd_xxx`）不在此禁令范畴内。

### 🔴 禁忌 3：严禁在增量维护时全量重跑 `pipeline`
- 全量 `pipeline` 适用于新赛季冷启动，如果在常规每周维护时重跑全量，不仅浪费算力，还会导致历史未锁定的统计量被重写，违背“时间戳预承诺”原则。

### 🔴 禁忌 4：严格保证零泄密
- 导出的所有 Web 数据必须是归一化净值（初始 NAV = 1.0000），严禁出现绝对资金金额；
- 公开的任何曲线和报告中，模型必须严格采用 `CONTESTANT_A` ~ `CONTESTANT_F` 匿名代号，严禁暴露私有生产类名与绝对文件路径。
