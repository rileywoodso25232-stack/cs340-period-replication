# Claims to test (draft)

2026-11-19 更新：表二 SCTBench reorder 线程数系列（3/4/5/10）完成——Period/Serial 各 3 次。Period 的 reorder_3/4/5 三项与论文完全一致，reorder_10 仅错误调度差 1；Serial 的 reorder_3 一致、reorder_4 首次 47 vs 论文 37、reorder_5 错误均值 816.67 vs 816、reorder_10 三次均未找到（与论文 `%/L/0` 一致）。C2 判定为 **partially supported（scoped）**：并行 Period 的搜索量优势在线程数系列上复现，但完整表二与精确逐项复现未完成。见[表二批次](../results/raw/local-table2-local-comparison-20261118/README.md)、[对比表](../results/processed/table2-paper-vs-ours.md)与[表二差异分析](table2-analysis.md)。

2026-11-18 更新：正式 scoped 表一数据与 Paper vs Ours 对比已完成——PERIOD 三例各 10 次、Serial 的 7911/9806 各 10 次。C1 判定为 **partially supported（范围内）**：首次触发与总调度在全部评估用例上与论文一致；PERIOD 的 7911/9806 错误调度精确一致，15265 的错误调度有波动，Serial 的 7911/9806 错误调度有 ±1 波动，Serial 15265 因候选驱动不可复现而排除。阶段 9 控制变量：单独重复 15265 未出现 invalid replay；同/新命名空间重放为 3/4 对 4/4，状态隔离假设不支持；C1 保持 partially supported。见[正式批次](../results/raw/local-table1-local-runs-20261118-scoped/README.md)、[对比表](../results/processed/table1-paper-vs-ours.md)与[差异分析](analysis.md)。

2026-11-17 更新：三个 CVE 已在本机用 IPC 兼容驱动完成有界试跑（每例 3 次、深度 5、预算 10000），9/9 搜索完成且均有重放证据，调度指标与论文表一一致；这仍是试跑，不是正式复现，正式配置与 Serial 基线未冻结。见[主批次](../results/raw/local-table1-cve-pilot-20261117/README.md)。同日 reorder_3 的 PERIOD/Serial 兼容候选各一次搜索与重放已通过，见[动态验收](../results/raw/local-ipc-validation-20261115/README.md)。

2026-11-15：阶段 5 交接采用表一三个候选用例 CVE-2016-7911、CVE-2016-9806、CVE-2017-15265；表二先以 reorder_3 验证候选基线。当时本机 IPC 兼容问题尚待动态验收，正式配置未冻结。范围、复用边界与补证据清单见[交接核验](stage5-6-handoff.zh-CN.md)。下文最终用例选择待定包含后续表二范围，不表示已有三个 CVE 候选被取消。

Select one to three claims, freeze exact subjects and settings, and link each claim
to a specific original figure/table. Current entries are proposals, not findings.

| ID | Scoped question | Original reference | Metrics | Current verdict |
| --- | --- | --- | --- | --- |
| C1 | Does PERIOD expose the selected real-world CVE examples within the reported search bounds? | Table 1, sections 4.1-4.3 | Schedules to first bug; total schedules; buggy schedules | Partially supported (scoped) |
| C2 | On a representative SCTBench subset, is the stated detection/search advantage observable against validated baselines? | Table 2, sections 4.2-4.3 | Same schedule metrics and buggy-program count; wall time separately | Partially supported (scoped) |

Original setup includes Ubuntu 18.04, GCC 7.5, LLVM 10.0, a 10,000-schedule
budget, depth limits of 5 (CVE) and 3 (SCTBench), and ten repeated runs. Record
deviations when using another setup or fewer runs. Three runs meet the course's
minimum; they do not duplicate the paper's ten-run protocol.

Final subject selection: pending. Include multiple bug types, thread counts and
hard cases; retain a record of failures and exclusions. Installation examples in
`test/` establish installation only and cannot stand in for all research claims.

Use supported, partially supported, not supported, or inconclusive as final
verdicts. Subset results support only the declared subset. No current experiment
establishes discovery of new vulnerabilities or superiority over all baselines.
