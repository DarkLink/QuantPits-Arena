# QuantPits-Arena 密码学时间戳存证与披露协议规范
*(Proof-of-Timeliness & Delayed Disclosure Protocol)*

---

## 一、基本定位与核心原则 (Core Axioms)

1. **纯粹的学术与研发评测平台**：
   - 本竞技场（QuantPits Arena）内的所有模型均为**历史研发候选模型（Historical Research Candidates / Retired Artifacts）**，**绝非实盘生产模型，亦非实盘运行状态**。
   - 本项目不代表任何真实资金的实盘交易，不包含商业机密，亦不存在需要刻意保护的实盘商业 Alpha。

2. **为什么采取“预先承诺与延迟披露（Commit-and-Reveal）”？**：
   - **杜绝后视镜偏误（Zero Hindsight / Anti-Tampering）**：为了保证量化策略在未来未知行情下评测的绝对纯洁性，杜绝“根据后验行情事后修饰持仓或挑选结果”的学术造假可能；
   - **科学评测缓冲期**：让模型在未受外界实时信号关注的情况下，独立完成多周期的预测与换手跟踪；
   - **从容的跑批节奏**：为研发维护者留出从容的本地运行、数据清洗与校验时间窗口。

---

## 二、公开与披露节奏 (Disclosure Schedule)

| 披露维度 | 公开频率与目标时间 | 机制与保证性质 |
| :--- | :--- | :--- |
| **策略净值 (Weekly NAV)** | **周频更新**（尽量于**下周一 A 股开盘 09:30 前**完成公开） | **尽力而为（Best-effort）**：属于个人/研究性质发布，**不提供任何硬性时间 SLA 或商业公开保证**，视闲暇时间可能有所顺延。 |
| **微观持仓与订单 (Holdings & Orders)** | **延迟 4 周公开**（约 1 个日历月 / 4 个交易周期） | **Git SHA-256 预承诺**：周五生成当期调仓指令的时刻，原始文件的 SHA-256 哈希指纹即刻 Commit 写入 Git；4 周后公开明细，可供数学比对。 |

---

## 三、密码学存证流程 (Two-Phase Protocol)

整个存证与揭盲流程基于 Git 天生的 Merkle DAG 不可篡改特性：

```
[Cycle T 周五收盘]
   │
   ├── 1. 模型根据历史数据生成 Cycle T+1 调仓指令 orders_cycle_T+1.json
   ├── 2. 计算原始文件哈希指纹：SHA-256(orders)
   └── 3. 将哈希值记录至 commitments/embargo_commitments.yaml 并 git commit 入库
         （此时明细文件保留在本地私有目录，公开仓库仅有不可逆指纹）

[Cycle T 周末 / 周一开盘前]
   │
   └── 4. 结算当周 (Cycle T) 盯市净值，更新公开网页曲线与排行榜（尽力而为）

[Cycle T+4 (4 周后)]
   │
   ├── 5. 到达 4 周延迟揭盲窗口，脱敏后的原始订单与持仓明细正式发布入库
   └── 6. 任何人均可比对当前明细的 SHA-256 与 4 周前的 Git Commit 记录，证明 100% 保真
```

---

## 四、独立手工核验指南 (Manual Verification)

本项目坚持“极简、透明、无多余黑盒”，**不提供任何后台自动化公证服务或定时执行机制**。任何独立研究人员或访客，均可自行在本地运行单行命令完成核验：

### 核验步骤
1. **核对 Git Commit 时间戳**：
   在 GitHub 上查看 [`commitments/embargo_commitments.yaml`](./embargo_commitments.yaml) 的历史提交记录，确认对应周期的哈希指纹是在实际交易发生之前即已提交（未被修改）。
2. **运行本地核验脚本**：
   ```bash
   # 核验指定周期的明细文件哈希是否与存证完全一致
   python3 scripts/verify_commitment.py --cycle cycle_9
   ```
   若输出 `[PASS] ALL DIGESTS MATCH`，即从数学上证明该周期的订单与持仓在交易日前已被确定，不存在任何后视镜调参或篡改。
