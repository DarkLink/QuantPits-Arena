# QuantPits Arena: Season & Universe Expansion Architecture Guide
> **Document Version:** 1.0.0  
> **Audience:** Quant Developers, AI Agents, Strategy Researchers  
> **Security Compliance:** AGENTS.md Zero-Leakage & Public-Ready Standard  

---

## 1. 痛点复盘：为什么本次 CSI 1000 处理流程显得“过于沉重”？

在本次接入 CSI 1000（中证 1000 小盘千股池）的实际操作中，暴露了早期原型开发遗留的**架构耦合与碎片化**问题。按量化工程常识，Qlib 原生处理股票池变换（如从 `csi300` 切换到 `csi1000`）仅是数据层 `instruments` 参数的单点配置，推理过程标准且统一。但在本次回测中，整个流程却牵扯了大量临时脚本和繁琐补丁：

```
【原有脆弱流程：高摩擦与手工编排】
1. 手工编写 scripts/infer_csi1000.py 进行模型打分
2. 手工修改 HistoricalReplayAdapter 的 auth_store_path 硬编码路径
3. 手工配置 CLI 运行回测并串行生成 11,000 只猴子（高计算等待）
4. 手工复制并定制 scripts/export_season_csi1000.py（多达 330 行冗余代码）
5. 手工往 web/js/data/seasons_index.js 登记元数据与 Dispatches 节点
6. 前端代码存在 hardcoded 'season_01' 逻辑分支，产生串台与 +- 格式 bug
```

### 核心痛点归因

1. **Qlib 推理与 Arena Runner 强耦合且路径硬编码**：
   原有适配器（`arena/contestants/adapters/`）多处硬编码了 `all_contestants_oos.pkl`，未将“数据生成（Inference）”与“组合模拟（Execution）”通过资产池抽象（Universe Abstraction）解耦。
2. **缺乏声明式赛季配置（Declarative Season Manifest）**：
   资产池、基准代码、起止日期、选手名单、猴群规格散落在 Python 脚本中，而不是由一份 `season.yaml` 自驱动。
3. **缺少通用 Web 导出器（Universal Exporter）**：
   每个新赛季都写一份 `export_season_xxx.py`，造成数据字典拼装逻辑重复，极易遗漏 `dispatches` 或字段别名（如 `percentile_rank` vs `monkey_percentile`）。
4. **猴群生成缺少向量化批处理**：
   将 11 组策略规格 × 1,000 只猴子放入单进程逐周期生成订单循环，导致 11,000 次组合回测计算耗时冗长。

---

## 2. 目标架构：四层解耦与标准化流水线 (The 4-Layer Standard)

为了让后续资产池（如中证 500、全 A、红利/微盘定制池）或新模型（深度学习、树模型、外部因子）的接入变得**极轻量、自驱动、开箱即用**，系统确立四层解耦架构：

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Layer 1: Declarative Season Spec (声明式配置层)                           │
│   seasons/<season_id>/season.yaml 驱动一切，单点配置资产池、模型、基准与文案 │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Layer 2: Universal Qlib Inference Engine (标准 Qlib 推理适配层)           │
│   以 Qlib Dataset 为核心，根据 season.yaml 自动执行批量预测，输出统一格式  │
│   DataFrame: MultiIndex [datetime, instrument] -> score                   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Layer 3: Vectorized Arena Matrix Engine (向量化执行与猴群矩阵)             │
│   - 28 Animal Handlers (TopK, 迟钝, 拖延, 换手等策略容器)                │
│   - Dual Baselines (Taotie 500k 物理摩擦 + Ghost 100M 理论等权)           │
│   - Vectorized Monkey Matrix (NumPy 矩阵置换，秒级完成 11,000 猴群分布)  │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Layer 4: Automated Dual-Tier Exporter (全自动报告与前端交付)              │
│   - 自动导出脱敏公开 CSV / 指标矩阵 / 零假设显著性检验报告                │
│   - 自动生成 web/js/data/<season_id>.js，无需手写任何定制导出脚本！       │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 标准化实施规范 (SOP)

未来新增任何新资产池或新模型时，**只需要执行以下 3 步**，无需编写任何额外的导出脚本：

### 第一步：编写声明式赛季清单 (`seasons/<season_id>/season.yaml`)

创建目录 `seasons/<season_id>/`，放置单一配置文件 `season.yaml`：

```yaml
season_id: season_csi500
title: "Season CSI 500: Mid-Cap Empirical Testbed"
status: ACTIVE                        # DRAFT | ACTIVE | EMBARGOED | ARCHIVED
universe:
  type: qlib_universe                 # qlib_universe | file_list
  code: csi500                        # Qlib 原生 universe 名称或成分股文件路径
  name: "CSI 500 (~500 Stocks)"
  market_benchmark_symbol: "SH000905" # 对应市场大盘基准代码
  market_benchmark_name: "CSI 500"

horizon:
  anchor_date: "2026-07-03"           # 回测起点
  end_date: "2026-08-28"             # 回测截止
  trading_days: 41

capital:
  initial_cash: 500000.0             # 物理基准现金 (CNY 500k)
  ghost_cash: 100000000.0            # 理论无摩擦资金 (CNY 100M)
  lot_size: 100

contestants:                         # 参赛模型选手代号列表
  - CONTESTANT_A
  - CONTESTANT_B
  - CONTESTANT_C
  - CONTESTANT_D
  - CONTESTANT_E
  - CONTESTANT_F

monkeys:
  colony_size_per_spec: 1000         # 每种执行容器 1,000 只随机猴 (总 11,000 只)
  min_p_value_threshold: 0.001

dispatches:                          # 专属战报与市场宏观记叙
  executive:
    tag: "🔬 Mid-Cap Empirical Testbed"
    title: "CSI 500 Empirical Evaluation & Execution Frictions"
    nature: "Evaluating 6 ML contestants across 500 mid-cap constituents."
  climate:
    tag: "🌪️ Mid-Cap Dispersion Dynamics"
    title: "Factor Capacity & Liquidity in Mid-Cap Regimes"
  episodes:
    - id: "csi500_ep01"
      tab_label: "🎯 Ep 01: Mid-Cap Expansion"
      title: "CSI 500 Dispatch 01: Testing Factor Breadth Across Mid-Cap Equities"
      date: "2026-09-08"
      summary: "Deploying the contestant lineup onto the 500-stock CSI 500 universe."
      content_html: "<p>Empirical breakdown of mid-cap signal behavior...</p>"
```

---

### 第二步：单命令运行完整自动化流水线 (One-Command Pipeline)

统一由 `cli.py` 调度，支持分步运行或一键全流程闭环：

```bash
# 【一键全自动化闭环 (推荐)】
# 自动完成：Qlib模型推理 -> 28动物执行容器回测 -> 11,000猴群向量化评估 -> 前端Payload自动导出
python cli.py pipeline --season season_csi500

# -------------------------------------------------------------
# 或者按需执行原子步骤：
# 1. 仅执行 Qlib 批量推理 (生成 parquet 打分缓存)
python cli.py infer --season season_csi500

# 2. 仅执行 28 动物执行矩阵与 11,000 猴群模拟
python cli.py run --season season_csi500 --monkeys --monkey-count 1000

# 3. 仅执行通用数据导出 (自动生成 web/js/data/season_csi500.js)
python cli.py export-web --season season_csi500
```

---

### 第三步：新模型接入协议 (Plugging In a New Model)

当引入全新模型架构（如基于 Qlib 的 Transformer、GRU、LightGBM、或外部 PyTorch 权重）时，只需两步：

1. **注册公开脱敏 Manifest** (`manifests/public/contestant_x.yaml`)：
   ```yaml
   contestant_id: CONTESTANT_X
   display_name: "Candidate-X (Transformer)"
   family: "Family-Attention"
   training_mode: "transformer_multiscale"
   feature_set: "alpha158_enhanced"
   historical_sys_ann_return_pct: 12.5 # 仅作为退役历史档案
   inference_adapter: "qlib_standard"
   adapter_config:
     model_uri: "artifacts/models/candidate_x.pt"   # gitignored 本地私有权重
     dataset_yaml: "artifacts/configs/dataset_x.yaml" # 特征工程配置
   ```
2. **遵守标准预测输出契约 (Prediction Interface Contract)**：
   任何新适配器只需实现统一接口：
   ```python
   def predict(self, start_date: str, end_date: str, universe: str) -> pd.Series:
       """
       返回索引为 [datetime, instrument]，值为 float score 的 Series。
       截面归一化与融合由基类统一处理，模型无需操心调仓与资金逻辑。
       """
       ...
   ```

---

## 4. 猴群零假设计算的物理摩擦原则与性能取舍 (Execution Physics vs. Pure Math)

### 为什么不能单纯用连续矩阵乘法替代离散回测？
虽然从纯数学角度，$\mathbf{R}_{\text{monkey}} = \mathbf{W}_{\text{random}} \times \mathbf{R}_{\text{stock}}$ 可以在毫秒级完成，但**量化实盘的本质是离散物理摩擦**：
1. **100 股圆整约束 (Lot-Size Rounding)**：
   在中小资金体量（如 CNY 500,000）下，高价股（如股价 > 100 元）每买 1 手（100 股）就需要消耗超过 10,000 元（占总仓位 2% 以上）。离散圆整会导致实际持仓与理论等权出现巨大偏离。
2. **资金边界与拒单现金拖累 (Cash Drag & Rejections)**：
   若某只随机猴抽中了多只超高价股，资金不足以买满整手，将被执行容器直接判定为“买不起拒单”，形成被迫闲置现金，进而产生现金拖累。
3. **双边交易摩擦 (Friction Drag)**：
   印花税、双边佣金与千分之一滑点对换手率高的策略容器具有致命衰减作用。

> **核心结论**：  
> QuantPits Arena 的立足之本是**真实可执行的残酷物理现实**。如果参赛模型在经受 100 股圆整、资金边界和交易摩擦的严酷考验，而对照组的随机猴群却享受无摩擦、无限可分股数的“数学特权”，那么显著性经验检验（p-value）将发生系统性失真！  
> 因此，**11,000 只猴子必须逐一通过相同的物理执行引擎（包含 100 股圆整与交易成本）**。离线跑批 10 分钟在量化投研中完全是健康、可接受的代价。  
> 若未来需要提速，唯一正道是通过 **多进程并行（Python ProcessPool / Ray 并行计算 11 组策略规格）**，在保持 100% 离散物理保真度的前提下，将 10 分钟缩短至 ~40 秒。

---

## 5. 跨池与历史指标对比的严禁事项 (Cross-Universe Warnings)

根据量化统计原理与用户明确要求，文档与前端必须严格执行以下红线：

1. **严禁跨资产池横向比对绝对收益**：
   - 历史生产数据（如 CSI 300 池上的 +5.8% p.a.）与小盘千股池（CSI 1000 上的 +17.96%）不具备横向直接排序意义；
   - 界面上严禁对历史数据标注 `Comparable Standard`；
   - 必须统一显示英文警告：`Cross-Universe Incomparability Notice`；
2. **标的池属性必须在卡片显式对照**：
   - 历史列明：`Historical Stock Pool: Legacy Production Pool`
   - 当前列明：`Current Arena Pool: CSI 1000 (~1,000 Stocks)`

---

## 6. 周五 Seal 存证与持仓/信号零泄密架构 (Proof of Timeliness Without Alpha Leakage)

在每周五盘后密封（Seal）下周一调仓订单时，如何**既向外界数学证明“绝对不存在未来信息与事后偷看”（Zero Hindsight）**，**又绝对不向公众泄漏具体持仓（Holding）与交易信号（Signal）**？

以下是针对量化私募/参赛者核心知识产权保护的四大工程方案：

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    周五 15:30 产生订单与信号 (Phase 1)                     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         ▼                                                         ▼
【方案 A：加盐哈希 + 延期解密】                            【方案 B：纯净值发布 + 终生不公开】
  - 公开: SHA-256(Orders + Salt)                            - 公开: 每日归一化 NAV (1.0000 -> ...)
  - 延期 T+4 周公开明文 (Alpha 已衰减)                       - 真实订单与明细永久保存在本地私有仓
  - 既防抄单，又保留终极可验证性                            - 仅公开行业/风格宏观暴露等无指纹特征
         │                                                         │
         ▼                                                         ▼
【方案 C：单向确定性代码混淆 (HMAC)】                      【方案 D：零知识证明/第三方独立存证】
  - 股票代码经秘钥映射 (SH600519 -> STOCK_8F3A)            - 外部见证人/公信时间戳服务签发 Hash
  - 全流程公开微观持仓分布与换手                            - 任何研究者无法反推真实投资标的
  - 任何人都无法反推真实 A 股个股
```

### 方案 A（推荐标配）：加盐哈希存证 + 滚动延期解密 (Commit-Reveal with Decay Window)
* **周五 15:30（Phase 1: Freeze & Seal）**：
  在本地私有目录生成目标调仓订单文件 `orders.csv`。
  计算不可逆加盐哈希：
  $$H = \text{SHA-256}(\text{orders.csv} \,\|\, \text{Secret Salt} \,\|\, \text{Timestamp})$$
  立即将哈希值 $H$ 提交并 Push 到 GitHub（如 `commitments/embargo_commitments.yaml`）。
  **此时外界只能看到一串 64 位不可逆十六进制摘要，持有 0 标的、0 权重、0 逻辑，绝无 Alpha 泄露风险**。
* **周一 09:30（Phase 2: Execution）**：
  本地依据 `orders.csv` 正常撮合成交。
* **何时解密公开？（The Decay Window）**：
  不实时公开，而是**延期 $T+4$ 周（或赛季结束时）公开**。
  周频策略的 Alpha 寿命通常只有 1~2 周。4 周之后该批订单早已完成结算且信号衰减，不具备任何抄单价值。此时公开当时的文件与 Salt，任何人运行校验命令：
  $$\text{SHA-256}(\text{orders.csv} \,\|\, \text{Salt}) \stackrel{?}{=} H_{\text{committed}}$$
  **完美平衡：实时零泄密、防跟单、防逆向；历史铁证如山，彻底免除“事后调参”嫌疑**。

### 方案 B：纯净值与宏观属性模式 (Pure Aggregate Metrics — Zero Trade Disclosure Ever)
若用户希望**永久不公开任何历史个股持仓与交易明细**：
* 仓库中只对外发布：
  1. 每日归一化净值时序（NAV 恒等于 1.0000 起始）；
  2. 统计风险指标（Sharpe、MDD、波动率、周胜率）；
  3. 宏观去指纹组合特征（总持仓只数、行业分布百分比、周换手率、现金闲置率）。
* 真实的逐笔订单 `private_trades.csv` 永远受 `.gitignore` 保护留在本地私有盘。

### 方案 C：单向确定性符号掩码 (Keyed HMAC Symbol Masking)
若用户希望公开微观调仓流以展示算法换手与持仓分散度，但不暴露具体 A 股标的：
* 使用私有密钥对个股代码进行确定性单向加密：
  $$\text{Masked ID} = \text{HMAC-SHA256}(\text{Symbol}, \text{SecretKey})[:8]$$
  例如：贵州茅台 `SH600519` 变为 `STOCK_8F3A`，中芯国际变为 `STOCK_12D9`。
* 外界可以看到完整的微观矩阵：例如“该策略持有 22 只股票，其中 `STOCK_8F3A` 连续持有 3 周，权重 4.5%”。
* 研究者能评估其真实的组合构建质量，但**没有任何人能猜出对应的真实股票，知识产权 100% 隔离**。

---

## 7. 核心工具链与代码重构路径图 (Refactoring Roadmap)

| 阶段 | 重构模块 | 目标与交付物 | 现状评估 |
| :--- | :--- | :--- | :--- |
| **P0** | **通用 Web 导出器** | 将 `scripts/export_season_csi1000.py` 抽象并合入 `DualTierExporter.export_web_payload(season_cfg)`，彻底废弃所有按赛季手工定制的 export 脚本 | 待合并沉淀 |
| **P1** | **声明式 Pipeline CLI** | 完善 `python cli.py pipeline --season <id>`，支持自动调用 Qlib 并产出完整前端交付物 | 待串联 pipeline |
| **P2** | **多进程物理猴群加速** | 在严格保持 100 股离散圆整与真实摩擦的前提下，利用 `multiprocessing` 将 11,000 猴群耗时从 10 分钟压至 ~40 秒 | 待加入多进程调度 |
| **P3** | **自动化加盐哈希存证工具** | 完善 `scripts/commit_embargo.py`，支持 `cli.py seal --delay-weeks 4` 一键生成抗篡改加盐哈希并自动纳入延期公开队列 | 原型已具备 |

---
*本文档受 QuantPits-Arena `AGENTS.md` 安全准则保护。*

