# QuantPits Arena: 系统架构重构规划与实施规范 (REFACTORING_SPEC)
> **文档版本:** 1.0.0 (Release Candidate)  
> **保密安全标准:** 严格遵守 `AGENTS.md` 零泄密与公开开源规范（禁止出现私有开发机绝对路径、真实资金与未脱敏个股）  

---

## 1. 重构背景与核心愿景

在量化投研实践中，Qlib 等框架切换标的池（如 CSI 300 切换到 CSI 1000）本质上只是 Dataset 的参数调整。然而此前 QuantPits Arena 的原型开发中存在职责边界不清的问题：
1. **推理与回测强耦合**：路径写死在适配器中，换池子不得不另写 `infer_csi1000.py`；
2. **导出脚本重复建设**：每个赛季手工复制 `export_season_xxx.py`，产生数百行重复代码与字段不一致；
3. **运转协议需要兼顾时效与保密**：如何在每周五既能实时发布最新 NAV 满足追踪时效，又能对未来调仓与信号绝对保密？

本次重构的愿景是：**建立一套以“声明式配置”自驱动、兼顾“真实物理摩擦”与“零 Alpha 泄露存证”的工业级量化竞技场内核**。

---

## 2. 核心架构设计原则 (Axiomatic Principles)

### 原则一：物理摩擦真实性第一（猴群保持现状，拒绝假性“幽灵猴群”）
* **量化实盘真实性不可妥协**：在中小资金（如 500,000 元）下，高价股（股价 > 100 元）每手买入占用数万元，100 股离散圆整会导致实际持仓偏离理论等权；资金边界会引发拒单与现金闲置拖累；双边印花税、佣金与滑点直接削减收益。
* **拒绝无摩擦幽灵猴**：如果参赛模型在经受 100 股离散圆整和摩擦的残酷考验，而对照组猴群却享受无摩擦的“数学特权”，则显著性检验（p-value）将发生系统性偏倚。
* **结论**：**猴群保持当前 100 股离散圆整与物理摩擦机制不变**。10 分钟在周频离线跑批中完全健康合理；后续仅通过 CPU 多进程（ProcessPool）并行提速，绝不削弱物理真实性。

### 原则二：时效性与保密性兼备的周五运转协议（思路 1：NAV 实时公开 + 订单 1 个月延期解密）
* **周五盘后 (15:30 ~ 17:00)**：
  1. **结算当周持仓**：依据周五收盘行情撮合上周持仓，计算当周真实盈亏与资金变动；
  2. **NAV 曲线实时公开发布**：**立即更新并对外发布最新归一化净值（NAV）与风险收益指标**，大盘看板与排行榜时效性得到 100% 保证；
  3. **下周调仓冻结与加盐存证 (Seal & Hash)**：依据最新收盘数据生成下周一目标调仓 `orders.csv`，计算不可逆加盐摘要：
     $$H = \text{SHA-256}(\text{orders.csv} \,\|\, \text{Secret Salt} \,\|\, \text{Timestamp})$$
     将哈希 $H$ 立即公开写入 `commitments/embargo_commitments.yaml` 并推送到 GitHub。
* **外界视角（零 Alpha 泄露）**：外界在周五盘后能看到策略最新战绩（NAV 涨跌），但面对未来调仓时，**只能看到一串 64 位不可逆十六进制摘要，持仓 0 标的、0 权重、0 信号**，没有任何人可以抄单、跟单或逆向拆解信号。
* **延期解密窗口 (4-Week Embargo Reveal)**：
  * 明文 `orders.csv` 与 Salt 封存在本地私有目录中保留 4 周（约 1 个月）；
  * 4 周之后，短周期 Alpha 已经彻底衰减失效，不再具备商业抄单价值；
  * 此时自动将明文与 Salt 解密推送到公开仓库，全网任何人皆可执行 `python cli.py verify` 校验明文哈希，证明其与 4 周前提交的 Hash 完全一致。**实时 100% 保密，历史 100% 不可篡改**。

---

---

## 3. 赛季标准化管线全景时序 (The Season Pipeline Specification)

为了将整个系统从“依赖手工编排脚本”升级为“标准化量化工程管线”，系统以 **赛季标准化管线 (Season Pipeline)** 为核心骨架。全流程分为清晰解耦的五大阶段：

```
┌────────────────────────────────────────────────────────────────────────────┐
│                  赛季管线全景状态机 (The Season Pipeline)                  │
└────────────────────────────────────────────────────────────────────────────┘

[Stage 0: 声明定义 (Define)]
  创建单一配置文件: seasons/<season_id>/season.yaml
  声明: 资产池、基准代码、起止时间、资金参数、参赛模型列表、战报文案
                              │
                              ▼
[Stage 1: Qlib 原生批量推理 (Infer)]  ➔ python cli.py infer --season <id>
  1. 读取 season.yaml 的 universe.code 与参赛模型列表
  2. 启动 Qlib Provider (本地 ~/.qlib/qlib_data/cn_data)
  3. 针对目标股票池一次性计算共享特征 (Alpha158/Alpha360 等，避免重复开销)
  4. 遍历参赛模型执行 Forward Prediction，完成截面 Rank 归一化与集成融合
  5. 产出统一打分缓存: runs/<season_id>/predictions/<cid>.parquet
     标准数据契约: pd.Series(MultiIndex [datetime, instrument]) -> score
                              │
                              ▼
[Stage 2: 物理执行与猴群矩阵 (Run)]    ➔ python cli.py run --season <id> --monkeys
  1. 载入 Stage 1 打分数据，初始化 MarketDataProvider
  2. 执行 6 选手 × 28 动物执行容器 = 168 条策略组合路径回测 (CNY 500k, 100股圆整)
  3. 撮合实盘物理基准 Taotie (500k) 与理论等权基准 Ghost Taotie (100M)
  4. 启动 11 策略规格 × 1,000 只 = 11,000 只真实物理随机猴群
     - 坚持实盘物理现实：100 股离散圆整、高价股拒单现金拖累、双边滑点与税费
     - 采用多进程 (ProcessPool) 调度 11 组规格，压减运行时间至 ~40 秒
  5. 落盘报告至 runs/<season_id>/public/ (NAV时序, 指标矩阵, 显著性报告)
                              │
                              ▼
[Stage 3: 通用 Web 交付导出 (Export)] ➔ python cli.py export-web --season <id>
  1. DualTierExporter 读取 Stage 2 的 run 产物与 season.yaml 元数据
  2. 自动组装前端 Payload: web/js/data/<season_id>.js (零定制 Python 脚本)
  3. 自动同步更新 web/js/data/seasons_index.js
  4. 自动触发本地隐私合规审计 (scripts/audit_privacy.py，0 泄露保障)
  5. 前端立即生效，所有视图（Overview, Leaderboard, Animals, Contestants）开箱即用
                              │
                              ▼
[Stage 4: 周五双轨运转闭环 (Friday Loop)] ➔ python cli.py cycle --season <id>
  1. 【结算当周】撮合上周持仓至周五收盘价，扣除税费，计算当周真实收益
  2. 【实时发布】立即更新并发布最新 NAV 曲线至公开仓库（保证时效性）
  3. 【订单加盐】依据周五最新特征生成下周一目标调仓 orders.csv，计算加盐哈希：
     H = SHA-256(orders.csv || SecretSalt || Timestamp)
  4. 【公开存证】立即将 64 位哈希 H 提交至 commitments/embargo_commitments.yaml
     全网 0 标的、0 权重、0 信号泄露，防跟单、防逆向
  5. 【延期解密】orders.csv 明文存入私有金库；满 4 周（Alpha 衰减失效）后自动解密
```

### 3.1 一键执行全流程命令 (One-Click Pipeline CLI)
开发者在日常研究或新开赛季时，无需关心内部中间文件传递，仅需单条命令：
```bash
# 【一键全自动化赛季管线 (Single Entrypoint)】
python cli.py pipeline --season season_csi1000
```
该命令会自动按顺序依次调用 Stage 1 $\rightarrow$ Stage 2 $\rightarrow$ Stage 3，自动完成：
`Qlib 批量打分` $\rightarrow$ `28 动物回测` $\rightarrow$ `11,000 猴群物理模拟` $\rightarrow$ `前端 Payload 生成` $\rightarrow$ `隐私审计`，3 分钟即可完成一个全新股票池赛季的完全上线。

### 3.2 阶段间数据契约规范 (Inter-Stage Data Contracts)

| 阶段转换 | 输入依赖 | 输出产物与格式 | 存储路径 | 访问控制 |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 0 $\rightarrow$ 1** | `seasons/<id>/season.yaml` | 资产池定义、时间区间、模型列表 | `seasons/<id>/` | Git 跟踪 (公开) |
| **Stage 1 $\rightarrow$ 2** | Qlib 原始量价特征 | 标准化打分时序 `pd.Series(MultiIndex)` | `runs/<id>/predictions/*.parquet` | Git 忽略 (本地私有) |
| **Stage 2 $\rightarrow$ 3** | 打分时序 + 行情数据 | 每日净值曲线、持仓诊断、猴群零假设分布 | `runs/<id>/public/*.csv` | Git 忽略 (本地产物) |
| **Stage 3 $\rightarrow$ Web** | public 报表 + season.yaml | 最终前端数据包 `window.ARENA_SEASONS_DATA` | `web/js/data/<id>.js` | Git 跟踪 (公开) |
| **Stage 4 $\rightarrow$ Git** | 周五最新调仓 orders.csv | 加盐哈希存证表 `embargo_commitments.yaml` | `commitments/*.yaml` | Git 跟踪 (公开) |

---

## 4. 模块职责与重组细节

### 4.1 通用 Web 导出器 (`arena.reports.web_exporter`)
* **现状痛点**：`scripts/export_season_csi1000.py` 与 `scripts/export_web_data.py` 代码高度重复（超过 300 行字典拼装），新开赛季极易遗漏字段。
* **重构方案**：
  在 `arena/reports/exporter.py` 中增加通用导出方法：
  ```python
  class DualTierExporter:
      def export_web_payload(self, season_cfg: SeasonConfig, results: Dict, monkey_results: Dict) -> Path:
          """
          通用前端 Payload 导出器：
          1. 自动提取 NAV 曲线、回撤时序、超额时序；
          2. 自动匹配 11 组策略规格的猴群零假设分位数与 p 值（支持所有字段别名）；
          3. 自动注入 season.yaml 中声明的 Dispatches 与宏观市场报告；
          4. 自动生成 web/js/data/{season_id}.js 并注册到 seasons_index.js。
          """
  ```
  彻底废弃并删除所有 `scripts/export_season_xxx.py`。

### 4.2 声明式赛季配置驱动 (`SeasonConfig`)
在 `seasons/<season_id>/season.yaml` 单点声明赛季一切：
```yaml
season_id: season_csi1000
title: "Season CSI 1000: Small-Cap Breadth Arena"
status: ACTIVE
universe:
  type: qlib_universe                 # qlib_universe | file_list
  code: csi1000                        # Qlib 原生 universe 名称或成分股路径
  name: "CSI 1000 Universe (~1,000 Stocks)"
  market_benchmark_symbol: "SH000852" # 对应市场大盘指数代码
  market_benchmark_name: "CSI 1000"
horizon:
  anchor_date: "2026-07-03"
  end_date: "2026-08-28"
capital:
  initial_cash: 500000.0             # 物理基准现金 (CNY 500k)
  ghost_cash: 100000000.0            # 理论无摩擦资金 (CNY 100M)
  lot_size: 100
contestants:
  - CONTESTANT_A
  - CONTESTANT_B
  - CONTESTANT_C
  - CONTESTANT_D
  - CONTESTANT_E
  - CONTESTANT_F
monkeys:
  colony_size_per_spec: 1000         # 每种规格 1,000 只真实物理猴 (总 11,000 只)
dispatches:
  executive:
    ...
  climate:
    ...
  episodes:
    ...
```

### 4.3 多进程物理猴群调度加速 (`arena.runner.WeeklyCycleRunner`)
* 保留 `PortfolioEngine` 内部严格的 100 股圆整、买不起拒单与交易税费逻辑；
* 将 11 组策略规格的猴群模拟分派至 Python `multiprocessing.Pool`，利用 CPU 多核心并行撮合：
  - 16 核心 CPU 上，11 组任务并行完成，耗时直接从 ~10 分钟压减至 ~40 秒；
  - **物理摩擦保真度：100% 保持，不失真**。

### 4.4 周五一键闭环命令 (`python cli.py cycle`)
周五收盘后运行一次即可完成当周全流程：
```bash
python cli.py cycle --season season_csi1000 --delay-weeks 4
```
自动串联执行：
1. **Settle Last Week**：依据周五收盘价撮合成交并生成当周真实净值；
2. **Publish NAV**：更新并导出最新公开 NAV 曲线与排行榜前端 Payload（时效性保证）；
3. **Generate & Isolate Orders**：根据周五特征打分，生成下周一目标调仓订单，执行**严格的分层目录隔离**（详见下文 4.5）；
4. **Salt & Hash Commitment**：对当周所有参赛实体订单计算不可逆加盐哈希（Merkle Root 与分实体 SHA-256），记录至 `commitments/embargo_commitments.yaml`；
5. **Queue Reveal**：在本地调度队列中标记在 4 周后自动解密明文至公开历史归档。

### 4.5 订单隔离与分层组织管理架构 (Order Storage & Embargo Hierarchy)
每个赛季包含 6 个参赛模型 × 28 种动物容器 = 168 条策略组合路径，外加 2 个全池基准（物理 Taotie 与无摩擦 Ghost Taotie），共计 **170 个真实实盘执行主体**（不含 11,000 只仅用于零假设分布校验的纯随机猴群）。必须对其订单文件实施**严格的物理目录分层隔离与生命周期管理**：

#### 1. 物理目录结构规范 (Directory Tree)
```
runs/<season_id>/
  ├── private/                               # [Git 忽略] 私有未解密订单与 Salt 封存金库
  │   └── cycles/
  │       └── cycle_05_20260810/             # 按周期归档
  │           ├── salt.key                   # 本周期高熵机密随机盐 (Secret Salt)
  │           ├── manifest.json              # 周期订单汇总与分项 SHA-256 清单
  │           ├── contestants/               # 6 大模型参赛选手 (Contestants)
  │           │   ├── CONTESTANT_A/
  │           │   │   ├── animal_cheetah.csv # 单一动物容器具体买卖指令
  │           │   │   ├── animal_sloth.csv
  │           │   │   └── ... (28 animals)
  │           │   ├── CONTESTANT_B/
  │           │   └── ... (CONTESTANT_C ~ F)
  │           └── benchmarks/                # 全池基准 (Benchmarks)
  │               ├── taotie_500k.csv        # 物理资金受限全池等权基准
  │               └── ghost_taotie_100m.csv  # 理论无摩擦等权基准
  │
  └── public/                                # [公开层] 满足延期披露要求的对外历史归档
      └── embargo_archive/
          └── cycle_01_20260713/             # 仅在 4 周延期到期后解密封存至此
              ├── verification_manifest.json # 公开校验凭证 (含原始 Salt 与明文 Hash)
              ├── contestants/
              └── benchmarks/
```

#### 2. 核心隔离设计原则
1. **彻底排除猴群 (Exclude Monkeys)**：11,000 只纯随机猴群仅用于离线计算统计显著性零假设分布，不生成持久化调仓 orders 文件，严防文件系统产生数万碎文件导致 I/O 泥潭。
2. **三维正交命名空间 (Three-Dimensional Namespace)**：路径严格遵循 `season_id / cycle_id / entity_type / entity_id / target.csv`，各模型（Contestants）与基准（Benchmarks）完全隔离，杜绝跨模型、跨周期的订单覆盖与污染。
3. **标准化 Order 数据结构**：每个 CSV 统一包含 `trade_date, action(BUY/SELL), instrument, estimated_shares, target_weight, limit_price, reason` 等标准字段。
4. **两级哈希存证结构 (Two-Level Merkle-Like Commitment)**：
   - **分项哈希**：针对每个具体执行实体 $i$ 分别计算 $H_i = \text{SHA-256}(\text{orders}_i \,\|\, \text{Salt} \,\|\, \text{Timestamp})$；
   - **赛季周期根哈希 (Cycle Root Hash)**：将所有 170 个实体的 $H_i$ 排序哈希后生成该周期的单一 Root Hash $H_{\text{cycle}}$，存入公开的 `commitments/embargo_commitments.yaml`。任何一个动物的调仓篡改都将导致全单哈希失效。

---

## 5. 迁移与执行路线图

| 步骤 | 任务名称 | 变更文件与模块 | 交付标准 |
| :---: | :--- | :--- | :--- |
| **Step 1** | **通用 Web 导出器沉淀** | `arena/reports/exporter.py` | 具备通用的 `export_web_payload()`，彻底删除临时定制导出脚本 |
| **Step 2** | **声明式赛季管线串联** | `cli.py` & `arena/seasons/` | `cli.py pipeline --season <id>` 单命令驱动全流程 |
| **Step 3** | **猴群多进程物理加速** | `arena/runner/weekly_cycle.py` | 100 股离散圆整保持不变，多核心并行压减运行耗时 |
| **Step 4** | **周五闭环与 4 周解密协议** | `cli.py cycle` & `scripts/commit_embargo.py` | 周五 NAV 实时公开 + 下周订单加盐 Hash 锁死 + 4 周到期解密 |
| **Step 5** | **合规审计与测试固化** | `tests/` & `scripts/audit_privacy.py` | 全量单元测试 PASS，隐私扫描 0 泄露项 |

---
*本文档为 QuantPits-Arena 官方技术架构重构规范，受 `AGENTS.md` 规则约束。*
