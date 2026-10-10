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

## 2. 极简一键全自动滚动推进 (Recommended: The Standard Workflow)

收到用户的更新指令并明确目标截止日后，使用以下原生流程。完整四池猴群重估的实际耗时取决于评估规模，必须监控进度，不能以预估分钟数判定完成。

### 步骤 0：用户通知与实盘执行安排

**假期具体更新时间由用户随时通知，执行安排尽量与实盘一致。** 行情已入库、到了名义周频日期、战报分篇或月末结算，都不构成自动推进、补交易或变更交易日的授权。

执行前依据本次通知核对目标截止日、决策截面和实际调仓安排；假期例外以用户提供的实盘安排为准。若通知要求的安排与当前日历或执行流程不一致，先落实相应规则并验证，再运行增量推进。不能自行把假期复市日当作交易日，也不能把本次“周一休市不补调仓”的案例推成未经通知的未来假期安排。

对齐的是交易日、信号截止及撮合与结算口径；公开产物继续采用匿名选手、归一化净值和百分比。日常维护不得通过导入真实账户状态实现对齐。

### 步骤 1：激活环境与增量推理 (Inference)
若本周行情数据已更新入库，使用原生增量命令补齐四个股票池的预测日期：
```bash
conda activate qlib_cupy
for universe in csirun300 csi500 csi800 csi1000; do
    python cli.py infer-update --universe "$universe" --end-date <YYYY-MM-DD> || exit 1
done
```

`infer-update` 复用原生批量推理引擎，仅推理缺失日期；检查选手资产完整性与预测完整性后原子追加，保留全部既有日期截面。重复执行会直接返回。`csirun300` 对应主赛季权威缓存。

旧的 `scripts/infer_all_contestants.py` 使用固定历史截止日，不适用于周度扩充；`infer` 用于初次生成，已有缓存时会跳过，`--force` 会重新生成整个缓存。

### 步骤 2：一键全自动原子级滚动推进 (The Grand Roll-Forward)
一条命令原子完成：日期推进 -> 4大赛季增量结算与4.4万只猴群评估 -> Web数据Payload导出 -> Chronicles文档同步 -> 隐私脱敏审计：
```bash
python cli.py rollforward --end-date <YYYY-MM-DD>
```

> [!TIP]
> - `rollforward` 默认会自动将变更的交易日数和截止日同步到全局与 4 个活跃赛季配置，依次执行增量 `step`（**默认全自动包含各赛季 11,000 只猴群零假设重估，4赛季共计 44,000 只**）与 `export-web`，自动同步 `chronicles/en/` 到 `web/chronicles/en/`，并在末尾强制执行 `audit_privacy.py`。
> - 使用明确超时并监控原生命令进度，严禁拆分成繁琐的外挂脚本或送入后台隔夜空转。
> - 若仅需极速调试周频撮合或跳过猴群评估，可追加 `--no-monkeys` 参数。

预测补齐与四池完整猴群重估的实际耗时取决于数据与评估规模。必须使用明确超时并监控各赛季进度，以实际净值末日、快照周期与审计结果判断完成，不能根据配置日期或预计用时判断成功。

**跨多个周期补更时**：`rollforward` 每次对每个赛季仅追加一个周期。必须按交易日历依次指定各周期结算日，不能直接跳到最后一天并把配置日期当作结算完成。节假日以当周最后交易日为结算日，例如本次补更：

```bash
python cli.py rollforward --end-date 2026-09-30
python cli.py rollforward --end-date 2026-10-09
```

**交易日与报道窗口分别处理**：当前实现按周一开盘调仓，周一休市则该周不补调仓。本次已核验的 2026-09-28 调仓后，9 月 30 日为月末结算；10 月 8–9 日只延续原持仓盯市，下一名义调仓日为 10 月 12 日，决策截面为 10 月 9 日收盘。实际更新及后续假期例外仍以用户通知的实盘安排为准。两次结算、两篇战报不代表两次交易。无调仓周仍保留决策截面与周期编号，供延迟策略下一周使用。

最后核对四个赛季 NAV 曲线末日均等于目标日期，历史前缀保持一致；无调仓周还须核对交易笔数、换手及费用均未新增，持仓和现金与上次结算相同。

若中间结算日的猴群重估触及监控超时，先核验四个赛季的快照周期和 NAV 末日。中间结算日需要月报时，必须在继续之前以同一日期的原生 `rollforward --seasons <id>` 补齐该池猴群重估，并验证显著性表的实际收益与同期净值一致，不能拿旧统计配新曲线。最终日期必须完成全部猴群重估、统一 Web 导出与审计。不要通过重跑 `pipeline` 恢复。

### 步骤 3：编写周度战报 (Battle Report)
增量推进完成后，依据最新生成的净值曲线数据撰写当周战报：
1. **中文战报**：撰写至 `chronicles/zh/episode_<N>_<YYYYMMDD>_<slug>.md`。
   - 必须严格遵循 [chronicles/zh/QUANTPITS_ARENA_EPISODE_RULES.md](../chronicles/zh/QUANTPITS_ARENA_EPISODE_RULES.md)；
   - 必须在正文最前部包含 `## ⚡ 战报速读 (TL;DR)`，提供 5~8 条密集 Level A 硬核数值事实（如大盘跌幅、冠军收益、回撤极值、显著性 p 值）；
   - 恪守事实层（严谨）与归因层（保守克制），严禁事后诸葛亮式杜撰。
2. **英文战报**：撰写至 `chronicles/en/episode_<N>_<slug>.md`，并拷贝同步至 `web/chronicles/en/`。
3. **赛季挂载**：在 `seasons/season_01/season_config.yaml` 的 `dispatches.episodes` 下挂载新 Episode 条目。
4. **扩展池月报**：CSI500、CSI800、CSI1000 分别撰写独立 M3 报告，分别挂载到所属赛季。九月正文固定以 8 月 28 日收盘为收益锚点、9 月 30 日为截止日；十月数据另列附录。单月收益、累计排名、累计猴群检验不得混用。

### 步骤 4：回归测试与合规审计
```bash
PYTHONPATH=. pytest tests/test_rollforward_automation.py tests/test_holiday_rebalance.py tests/test_incremental_inference.py
python scripts/audit_privacy.py
```

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
   - **决策阶段 (Decision)**：保留上次结算日截面；仅在周一有交易时生成调仓目标订单；
   - **执行阶段 (Execution & Valuation)**：按周一开盘价成交；周一休市不顺延成交，仅盯市。记录截止日以内所有交易日的 Daily MTM 估值，节假日短周同样适用；
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
- 如果数据层缺乏最新截面，使用标准命令 `python cli.py infer-update --universe <code> --end-date <date>`，由原生引擎统一处理。

### 🔴 禁忌 2：严禁临时篡改 `cli.py` 既有稳定命令逻辑
- `cli.py` 的 `step`、`run`、`export-web`、`bump-date`、`rollforward` 等命令已全面支持配置化赛季解耦与参数传递；
- 绝不能以"增加参数快捷方式"为由随意篡改上述既有稳定子命令的内部撮合、导出、或快照逻辑；
- 经过正式设计评审与全量测试验证的新子命令扩展（新增 `add_parser` + `cmd_xxx`）不在此禁令范畴内。

### 🔴 禁忌 3：严禁在增量维护时全量重跑 `pipeline`
- 全量 `pipeline` 适用于新赛季冷启动，如果在常规每周维护时重跑全量，不仅浪费算力，还会导致历史未锁定的统计量被重写，违背“时间戳预承诺”原则。

### 🔴 禁忌 4：严格保证零泄密
- 导出的所有 Web 数据必须是归一化净值（初始 NAV = 1.0000），严禁出现绝对资金金额；
- 公开的任何曲线和报告中，模型必须严格采用 `CONTESTANT_A` ~ `CONTESTANT_F` 匿名代号，严禁暴露私有生产类名与绝对文件路径。
