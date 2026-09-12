# QuantPits Arena: 赛季周频增量滚动推进操作规范 (Weekly Roll-Forward SOP)

> **文档版本**: 1.0.0  
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

### 1.2 为什么严禁“手写外挂脚本”与“修改 CLI”？
- **自驱动状态机**：`cli.py step` 已完整接入 `SeasonManager` 声明式配置与 `WeeklyCycleRunner` 快照状态机。它会根据 `runs/<run_id>/checkpoints/latest_state.pkl` 自动识别当前进度，并精准仅执行目标这 1 个周期的调仓撮合与盯市估值。
- **历史不可变铁律 (Historical Immutability)**：任何通过手写脚本对底层产物（如预测库、中间状态）进行的非标准化篡改，都极易破坏历史回测净值的一致性，触发 `scripts/validate_incremental_update.py` 报错。

---

## 2. 标准操作三步流程 (SOP)

当行情数据（如 Qlib 离线日线库）更新至最新一周收盘（例如从 `2026-09-04` 推进到 `2026-09-11`）时，**仅需执行以下标准化 3 步**：

### 第一步：配置层推进时间截断 (Declarative Horizon Bump)
修改全局配置与各目标赛季配置文件，声明新的截止交易日（周五收盘日）：

1. **全局默认配置** (`arena/config.py`)：
   ```python
   DEFAULT_END_DATE = "2026-09-11"  # 更新截止周五收盘结算日
   ```
2. **赛季专属配置** (`seasons/<season_id>/season_config.yaml`)：
   ```yaml
   calendar:
     anchor_date: "2026-07-03"        # 保持初始锚定日不变
     first_trade_date: "2026-07-06"   # 保持首周开盘日不变
     end_date: "2026-09-11"           # 推进至最新结算日
     cycle_freq: "weekly"
   ```
   > 需同步更新所有活跃赛季（如 `season_01`, `season_csi500`, `season_csi800`, `season_csi1000`）。

3. **前端索引同步** (`web/js/data/seasons_index.js`)：
   更新对应赛季卡片的 `end_date` 与 `trading_days`（例如 46 天递增 5 天至 51 天）。

---

### 第二步：执行原生增量推进 (Rolling Incremental Step)
在包含 Qlib 与 PyTorch 的 Python 环境（如 `conda activate qlib_cupy`）下，直接使用原生 CLI 命令依次推进各赛季：

```bash
# 依次推进各赛季滚动 1 周
python cli.py step --season season_01
python cli.py step --season season_csi500
python cli.py step --season season_csi800
python cli.py step --season season_csi1000
```

#### `cli.py step` 内部执行细节：
1. **快照加载**：从 `runs/<season_id>_run/checkpoints/latest_state.pkl` 反序列化恢复上周已结算的 Portfolio 引擎及全量动物持仓；
2. **周期目标识别**：比对当前已完成周期 `last_completed_cycle_idx`（如 Cycle 8）与最新周期上限（Cycle 9）；
3. **两阶段撮合执行**：
   - **决策阶段 (Decision)**：基于最新周五截面特征生成调仓目标订单；
   - **执行阶段 (Execution & Valuation)**：按周一开盘价成交，并记录本周 5 个交易日的 Daily MTM 估值；
4. **状态持久化与导出**：将最新状态更新为 `latest_state.pkl`，并增量写出 `daily_nav_curves.csv` 和指标汇总。

> [!TIP]
> 若需一并增量更新该周的参数化猴群分布，可追加 `--monkeys` 参数（默认不带，以实现秒级快速推进）。

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

## 3. 一键批处理脚本范例 (Batch Roll-Forward)

维护者可在终端直接使用单行循环命令完成全部赛季的一键推进与导出：

```bash
# 激活环境并批量滚动推进所有赛季
conda activate qlib_cupy

for s in season_01 season_csi500 season_csi800 season_csi1000; do
    echo "⏩ Rolling forward season: $s..."
    python cli.py step --season $s
    python cli.py export-web --season $s
done

# 强制本地脱敏合规审计
python3 scripts/audit_privacy.py
```

---

## 4. 常见误区与高压红线 (Anti-Patterns / Absolute Red Lines)

### 🔴 禁忌 1：严禁编写临时数据拼装脚本
- 绝对不要在 `scripts/` 或根目录下编写任何类似 `update_predictions_*.py`、`patch_*.py` 等一次性脚本；
- 如果数据层确实缺乏最新截面，唯一的正规扩充方式是使用标准命令 `python cli.py infer --universe <code] --oos-end <date>`，由原生引擎统一处理。

### 🔴 禁忌 2：严禁修改 `cli.py` 源码
- `cli.py` 的 `step`、`export-web`、`run` 等命令已全面支持配置化赛季解耦与参数传递；
- 绝不能以“增加参数快捷方式”为由随意篡改 `cli.py` 既有稳定结构。

### 🔴 禁忌 3：严禁在增量维护时全量重跑 `pipeline`
- 全量 `pipeline` 适用于新赛季冷启动，如果在常规每周维护时重跑全量，不仅浪费算力，还会导致历史未锁定的统计量被重写，违背“时间戳预承诺”原则。

### 🔴 禁忌 4：严格保证零泄密
- 导出的所有 Web 数据必须是归一化净值（初始 NAV = 1.0000），严禁出现绝对资金金额；
- 公开的任何曲线和报告中，模型必须严格采用 `CONTESTANT_A` ~ `CONTESTANT_F` 匿名代号，严禁暴露私有生产类名与绝对文件路径。
