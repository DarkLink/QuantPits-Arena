# 周度增量推进

仅在收到用户更新通知并核对指定截止、决策截面和实际调仓安排后执行。行情入库、名义周频日期、报告拆分或月末结算不会自动授权推进或补交易。目前周一休市不补调仓；未来假期例外须按用户通知先实现并验证。

使用已准备的 `qlib_cupy` 环境；常规维护不写外挂更新脚本、不全量重跑历史，不使用固定历史截止的旧推理脚本。

```bash
conda activate qlib_cupy
TARGET_DATE=<authorized-cutoff>
for universe in csirun300 csi300 csi500 csi800 csi1000; do
    python cli.py infer-update --universe "$universe" --end-date "$TARGET_DATE" || exit 1
done
python cli.py rollforward --end-date "$TARGET_DATE"
```

`rollforward` 恢复各池的 `latest_state.pkl`，在独立staging generation内顺序执行全部缺失周期；同周延长仅补新增估值日，不重复撮合或费用。先完成实际截止、完整猴群、统计、网页和战报，最后才更新可见日期。重复同截止会检查已完成状态并返回，不重复成交。

猴群保持11个规格入口，只有10个随机规格；每规格固定100000条路径，五池共5000000条随机路径，另有5条确定性全池参考。只匹配TopK/DropN，不增加延迟、暖冷启动等种类。兼容版本的紧凑状态按新增日期续算，旧行情或规则修订会拒绝静默拼接。统计族为全部840动物比较，k/N和p全精度落盘；确定性参考没有随机检验p。

命令应在前台或设定明确超时运行，监控 `[controls]` 进度与实际快照/NAV/null截止。中断后重用同generation恢复；源输入变化应开新版本。不要因看到显著性过线就停止或扩大N。仅本地隔离诊断可使用 `step --no-monkeys`；共享发布要求五池同截止且随机对照完整。

全量历史修复必须得到明确授权，并使用原生 `refresh` 命令。它冻结旧信号与旧运行、分别生成修复回放和固定20000工程pilot，然后执行固定100000正式预算及整体发布；不能用当前预测缓存静默替换旧信号。详见 [EVALUATION_V2.md](EVALUATION_V2.md)。

现有回放仍为日线研究。报价有效性、最后有效估值、确定排序、事件台账接口和恢复机制已实现；没有完整核验的企业行为、开盘方向限制或容量数据时，严格执行profile预检失败。不要将此版写成完整实盘可执行总回报复现。

战报采用归一化净值和百分比，中文开头保留5–8条数值TL;DR。重算文稿明确事后回放性质；累计p与区间收益分开，月度及重复周度监测不自动成为联合确认性结论。公开文件只出现匿名模型身份，不出现真实证券、私有绝对路径或账户状态。

完成前运行：

```bash
PYTHONPATH=. pytest tests/test_rollforward_automation.py tests/test_holiday_rebalance.py tests/test_incremental_inference.py tests/test_execution_repair.py tests/test_statistics_precision.py
python3 scripts/audit_privacy.py
```

需同时核验五池NAV实际末日、快照和null截止一致、随机路径数量完整、全部战报源与网页副本一致、active bundle包含同一evaluation generation。隐私扫描FAIL时先修正再汇报。
