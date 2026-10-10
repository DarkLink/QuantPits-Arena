# Agent 行为准则与保密安全铁律 (AGENTS.md)

> **适用于所有协助维护、开发本仓库的 AI Agent 与自动化脚本。**
> 本仓库（QuantPits-Arena）计划未来向全网公开开源。仓库内的一切文件必须具备“完全公开就绪”的安全性。

---

## 一、核心认知：公网预设 (Public-by-Default Mindset)

每一位 Agent 在执行任何读写、复制、分析或生成任务时，必须建立如下**绝对认知**：
1. **本仓库即将在 GitHub 公开**。
2. 一旦有敏感信息写入任何被 Git 跟踪的文件，即使后续删除，也会永久残留在 Git 历史对象中，造成不可逆泄漏。
3. **严禁在未经过滤的情况下从外部生产环境直接拷贝配置或数据文件**。

---

## 二、五大保密安全红线 (Absolute Red Lines)

### 🔴 红线 1：禁止“反向泄漏”（严防史翠珊效应）
- **绝不允许**以“说明什么数据不能公开”、“举例警告”或“脱敏对比”为由，在文档、代码、注释、提交信息或测试用例中记录任何真实的实盘资金数值、零头余额、真实收益金额或真实持仓标的代码。
- 凡需说明敏感类型，**必须使用纯抽象术语**（如“实盘资金规模”、“相对净值时序”），禁止出现任何“例如 370xxx.xx 元”、“例如 SH600xxx”的具象化举例！

### 🔴 红线 2：实盘账户与资金零指纹
- 严禁将包含真实生产账户状态的文件（如包含实盘账户资金余额、实盘个股持仓明细、真实挂单流水的任何 JSON/CSV）复制或写入本仓库。
- 回测配置（如 `strategy_config.yaml`）中的资金基数必须统一设定为标准化整数基准（如 `100000000`），禁止保留任何生产实盘的零头资金数字。
- 所有对外报告、图表、指标输出一律采用**归一化净值（初始 NAV 恒等于 1.0000）**与百分比，严禁出现绝对人民币金额。

### 🔴 红线 3：模型二进制资产零入库
- 所有的模型权重、序列化对象（包括但不限于 `*.pkl`、`*.bin`、`trained_model` 以及任何网络权重二进制）**绝对禁止加入 Git 跟踪**。
- 权重仅限保存在受 `.gitignore` 严格排查的本地私有目录（`artifacts/models/`）中，仅供本地推理读取。
- 仓库内只公开模型架构配置文件（YAML）、特征列名清单以及不含权重的元数据 Manifest。

### 🔴 红线 4：本地环境与具体标的脱敏
- 公开文件（包括 Manifest、文档、配置）中，严禁暴露开发者主机的私有绝对路径（如 `/home/<用户名>/...`），必须统一采用仓库内相对路径（如 `artifacts/configs/...`）。
- 公开的基准对比、排行榜与衰减矩阵报告中，严禁列出真实的个股证券代码。若微观分析确需展示，必须进行确定性匿名代号替换（如 `STOCK_01`, `STOCK_02`）。

### 🔴 红线 5：模型身份匿名化（防止架构推测）
- 所有被 Git 跟踪的公开文件中，严禁暴露真实的模型生产代号（如具体 ensemble 组合名称）、模型类名（如具体深度学习或机器学习算法类名）、模型家族名称或 ensemble 子成员名称与组合方式。
- 公开的 Manifest、报告和代码中，Contestant 必须统一使用匿名代号（如 `CONTESTANT_A`、`Ensemble-A`）；模型成员使用 `member_1`、`member_2` 等通用编号。
- 真实名称仅保留在 `manifests/private/`（gitignored）目录中的私有 Manifest 和映射表中，供本地运行时加载使用。
- 禁止在公开文档中出现任何可推测具体模型架构、训练框架、特征集选型或模型历史演化关系的具体描述。

---

## 三、Agent 关键操作规程

### 1. 外部资产导入前置审查
在从外部生产环境或历史运行空间引入任何文件前，Agent 必须先执行内容审查：
- 确认该文件仅为模型超参、特征工程规则或回测参数；
- 确认不含有账户流水、持仓标的或实盘现金信息。

### 2. 任务完成前强制运行本地隐私审计
Agent 在声称完成任何涉及文件修改、文档编制或资产准备的任务前，**必须主动在终端运行本地脱敏扫描工具**：

```bash
python3 scripts/audit_privacy.py
```

若扫描器返回任何非零状态（FAIL），必须立即就地修正，直至扫描器通过（PASS），方可向用户汇报。

---

## 四、本地隐私审计工具的设计原则（严防扫描器泄密）

本地扫描脚本 `scripts/audit_privacy.py` 必须遵守以下原则：
1. **输出零泄密**：检测到疑似敏感内容时，**绝对不能在终端或日志中打印匹配到的敏感字符本身**！只能输出 `[FAIL] 文件名:行号 - 触发规则类别 (特征指纹或长度)`。
2. **退出码严谨**：发现任何违规项退出码必须为 `1`；全检通过退出码为 `0`。

---

## 五、常规周频维护标准姿势 (Weekly Operations Standard Procedure)

### 0. 更新授权与假期实盘对齐（用户指定）

- **假期具体更新时间由用户随时通知，执行安排尽量与实盘一致。** 不因行情入库、名义周频日期、战报拆分或月末结算自行推进、补调仓或变更交易日。
- 收到更新通知后，以用户指定的目标截止日、决策截面与实际调仓安排为准。当前日历或执行流程若不支持通知中的假期例外，先落实并验证相应规则，再执行原生增量管线；不得自行猜测例外安排。
- 当前“周一休市不补调仓”是已核验运行的实现规则，不能替代用户对未来假期的具体通知。对齐交易与结算口径时，继续遵守匿名化、归一化及真实账户状态零入库的要求。

> **极重要提醒**：当用户要求“更新最新一周数据”、“执行本周滚动”、“策划本周任务并执行”时，**严禁自行手写临时外挂脚本折腾半天**！使用仓库原生的**端到端推进命令**。完整五池猴群重估可能超过早期的 2~3 分钟估计，必须设置明确超时并监控实际进度。详细规范可参阅 [docs/SEASON_ROLLFORWARD_SOP.md](docs/SEASON_ROLLFORWARD_SOP.md)。

### 1. 运行环境指定
必须在包含 Qlib 与 PyTorch 的环境执行，固定使用 Conda 环境：
```bash
conda activate qlib_cupy
# 或直接使用该环境的 Python 解释器:
# /home/tonny/anaconda3/envs/qlib_cupy/bin/python
```

### 2. 标准两步走执行管线 (The Standard 2-Step Pipeline)

#### 第一步：特征推理与预测库增量延长 (Inference)
收到更新通知、核对执行安排且行情已更新入库后，先确保五池权威预测库覆盖至用户指定截止日：
```bash
for universe in csirun300 csi300 csi500 csi800 csi1000; do
    python cli.py infer-update --universe "$universe" --end-date <YYYY-MM-DD> || exit 1
done
```

`infer-update` 仅追加缺失日期并保留预测历史。旧的 `scripts/infer_all_contestants.py` 使用固定历史截止日；常规增量补更不得依赖该脚本或使用强制全量重建缓存。

#### 第二步：一键全自动原子级滚动推进 (The Grand Roll-Forward)
**核心端到端命令（严禁拼装临时更新脚本）**：
```bash
python cli.py rollforward --end-date <YYYY-MM-DD>
```

> **该命令在底层自动执行原子闭环（无需人工干预）**：
> 1. `bump-date`：原子更新 `arena/config.py`、各活跃赛季 `seasons/*/season_config.yaml` 及前端 `web/js/data/seasons_index.js`；
> 2. `step`：全自动依次对 **5 大活跃赛季**（`season_01`, `season_csi300`, `season_csi500`, `season_csi800`, `season_csi1000`）执行增量周期结算、持仓撮合、盯市估值与 **55,000 只对标猴群（11 specs × 1000）零假设重估**；
> 3. `export-web`：全自动重新编译 5 个前端数据文件（`web/js/data/*.js`）并同步 `arena_data.js`；
> 4. `sync_chronicles`：自动同步英文战报文档至 `web/chronicles/en/`；
> 5. `audit`：自动触发本地零泄密隐私审计 `scripts/audit_privacy.py`。

### 3. 周度战报撰写规范 (Battle Report & Dispatches)
增量推进完成后，依据最新生成的净值曲线数据撰写当周战报：
1. **中文战报**：撰写至 `chronicles/zh/episode_<N>_<YYYYMMDD>_<slug>.md`。
   - 必须严格遵守 [chronicles/zh/QUANTPITS_ARENA_EPISODE_RULES.md](chronicles/zh/QUANTPITS_ARENA_EPISODE_RULES.md)；
   - 必须在正文最前部包含 `## ⚡ 战报速读 (TL;DR)`，提供 5~8 条密集 Level A 硬核数值事实（如大盘跌幅、冠军收益、回撤极值、显著性 p 值）；
   - 恪守事实层（严谨）与归因层（保守克制），严禁事后诸葛亮式杜撰。
2. **英文战报**：撰写至 `chronicles/en/episode_<N>_<slug>.md`，并拷贝同步至 `web/chronicles/en/`。
3. **赛季挂载**：在 `seasons/season_01/season_config.yaml` 的 `dispatches.episodes` 下挂载新 Episode 条目。

### 4. 自动化回归与隐私合规终验
```bash
PYTHONPATH=. pytest tests/test_rollforward_automation.py tests/test_holiday_rebalance.py tests/test_incremental_inference.py
python scripts/audit_privacy.py
```

### 5. 三大违规禁令 (Anti-Patterns)
- 🔴 **禁令 1：严禁编写临时 ad-hoc 外挂脚本**：绝不可在 `scratch/` 或根目录下编写任何拼装更新脚本；
- 🔴 **禁令 2：严禁增量维护时全量重跑 `pipeline`**：增量维护必须基于快照 `latest_state.pkl` 进行，重跑全量会破坏历史不可变原则；
- 🔴 **禁令 3：严禁后台挂死与盲目等待**：`cli.py rollforward` 应在前台执行或设置明确超时与监控。完整五池猴群重估可能更久，必须依据各池快照、NAV 末日和统计产物判定进度与完成，切勿盲目后台挂起。

