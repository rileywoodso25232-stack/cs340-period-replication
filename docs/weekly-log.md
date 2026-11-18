# Weekly progress log

## 2026-11-19：表二 reorder 子集（C2）

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行整理，人工复核待完成。
- 范围：CS.reorder_3/4/5/10，Period/Serial 各 3 次（论文 10 次，声明性缩小），
  深度 3、预算 10000、整轮 600 秒；24/24 完成，0 超时。
- 结果：Period reorder_3/4/5 三项与论文完全一致，reorder_10 仅错误 90 vs 89；
  Serial reorder_3 一致、reorder_4 首次 47 vs 37、reorder_5 错误 816.67 vs 816、
  reorder_10 三次未找到（与论文 `%/L/0` 一致）。
- 核心现象复现：线程数增加时 Serial 需要的调度远多于 Period（27→30、100→384、
  225→5040、2350→10000+未找到）。
- C2 判定：partially supported（scoped）；证据
  [表二批次](../results/raw/local-table2-local-comparison-20261118/README.md)、
  [对比表](../results/processed/table2-paper-vs-ours.md)、
  [差异分析](table2-analysis.md)。
- 提交/推送：尚未执行；等待确认后提交，不推送。

## 2026-11-18：阶段 9 控制变量检查

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行整理，人工复核待完成。
- CC1（单独跑 15265，改变是否交错）：9 完成、1 dry-run 中止、0 invalid replay，
  完成轮全部 96/1/首次 11；正式交错批次有 1 invalid replay 和一次错误 3。
  交错可能是因素但 n=10 不定论；dry-run 中止仍出现。
- CC2（同/新 IPC 命名空间重放，改变状态隔离）：4 次可比较，同命名空间确认 3/4，
  新命名空间确认 4/4；状态隔离假设不支持，早触发更像目标时序假阳性。
- 首次 CC2 脚本 rc=126 的失败证据已归档，不用于结论。
- 结论写入 `docs/analysis.md`；C1 仍为 partially supported（scoped）。
- 证据：[solo](../results/raw/local-table1-15265-solo-20261118/README.md)、
  [namespace](../results/raw/local-table1-15265-namespace-20261118/README.md)。
- 提交/推送：阶段 8–9 已在本地提交 `2d36326`；按用户要求不推送。

## 2026-11-18：阶段 8 统计与 Paper vs Ours

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行整理，人工复核待完成。
- 由 `summary.csv` 生成 `paper_vs_ours.csv`（增加 mode 列）与可读表 `table1-paper-vs-ours.md`：
  18 行中 12 supported、3 partially supported、3 excluded（Serial 15265）。
- 关键差值：Period 7911/9806 三项精确一致；Period 15265 错误调度 1.22（+22.2%）；
  Serial 7911/9806 错误调度 7.9（-1.25%）/4.1（+2.5%）；首次与总调度全部一致。
- C1 判定为 partially supported（scoped）；差异分析写入 `docs/analysis.md`，
  未解释的 15265 早触发列为待阶段 9 控制变量检查。
- 图表：`results/figures/table1-schedules.svg/.png`、`table1-time.svg/.png`。
- 提交/推送：尚未执行；阶段 9 尚未做，分析分支任务未整体完成。

## 2026-11-18：正式表一 scoped 批次（阶段 7）

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行命令并辅助整理，人工复核待完成。
- 正式配置：深度 5、预算 10000、每例 10 次；PERIOD 三例 + Serial 的 7911/9806。
- 结果（首次 / 总调度 / 错误调度）：PERIOD 7911 3/19/8（n=9）、9806 6/42/4（n=10）、
  15265 11/96/1.22（n=9，1 次 invalid replay）；Serial 7911 3/19/7.9（n=10）、
  9806 6/42/4.1（n=10）。无超时，深度 5 全部确认。
- 差异：论文称 Period/Serial 在 CVE 基准完全相同；本机 7911/9806 的首次与总调度一致，
  错误调度有 ±1 波动；15265 的 Period 错误数在 1/3 间波动，Serial 候选不可靠故不纳入正式对比。
- 数据：`results/raw/measurements.csv`（288 行）、`results/processed/summary.csv`（30 组）；
  证据：[主批次](../results/raw/local-table1-local-runs-20261118-scoped/README.md)、
  [停止批次 1](../results/raw/local-table1-local-runs-20261118-attempt1-stopped/README.md)、
  [停止批次 2](../results/raw/local-table1-local-runs-20261118-scoped-attempt1-stopped/README.md)。
- 提交/推送：尚未执行；等待确认后提交，不推送。

## 2026-11-17：表一 CVE 本机试跑（阶段 6）

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行命令并辅助整理，人工复核待完成。
- 预建后续阶段分支（table1-local-runs、table2-local-comparison、analysis/local-reproduction、local-extension、report/final-delivery），当前仍在 experiments/table1-cve-pilot。
- 审查并修正试跑脚本：dry-run 的 ASan 中止记为 aborted_at_dry_run 并继续；新增阶段 6 运行、导出、诊断与补充重放脚本。
- 完成表一三个 CVE 的有界试跑：每例 3 次、深度 5、预算 10000、非交互；9/9 搜索完成，8 次批次内重放 + 1 次补充重放确认。
  - CVE-2016-7911：3 / 19 / 8（3 次一致）；CVE-2016-9806：6 / 42 / 4（3 次一致）；CVE-2017-15265：11 / 96 / 1（3 次一致）。
- 15265 的 dry-run UAF 单独诊断：完整搜索 10 次中 4 次 dry-run 中止，完成 6 次均为 96/1/11；最小预算探针 0/10。
- 证据：[主批次](../results/raw/local-table1-cve-pilot-20261117/README.md)、[attempt1](../results/raw/local-table1-cve-pilot-20261117-attempt1-stopped/README.md)、[诊断](../results/raw/local-table1-15265-diagnostic-20261117/README.md)、[补充重放](../results/raw/local-table1-cve-pilot-20261117-replay-supplement/README.md)。
- 这是试跑，不是正式复现：每例 3 次（论文 10 次）、只有 PERIOD、尚无 Serial；正式配置未冻结。
- 提交/推送：尚未执行；等待确认后提交。

## 2026-11-15：本机 IPC 兼容候选验收

- 成员：1240013942 刘竞辰；Codex 执行命令并辅助整理，人工复核待完成。
- 创建 experiments/local-ipc-validation，保留并备份交接改动；本轮 GitHub fetch 超时，尚未同步最新 main。
- 复用吴明阳 IPC 补丁，在独立 Linux 目录与 IPC 命名空间验证。PERIOD 单次搜索 27 调度/6 失败，Serial 候选单次 30/10，均无超时；各首条失败重放确认 reorder_bad.c:80 断言，目标退出 -6，驱动退出 0。
- 保存命令、日志、全部 16 条失败调度、驱动副本、哈希及原文件前后不变检查。[证据](../results/raw/local-ipc-validation-20261115/README.md)。
- 此轮是兼容性验收，不计为新漏洞或正式多次复现；CVE 预实验、组员补证据和正式 Serial 对应关系仍待完成。
- 提交/推送：尚未执行，不能以本条代替实际 GitHub 历史。

Record real work and the actual push/PR evidence. This file is not a substitute
for timely GitHub history, and it does not itself certify a passed weekly check.

## Initial setup - 2026-10-23

- Prepared a project layout, scoped claims, evidence templates and collaboration guide.
- Recorded a fixed upstream commit and preserved the original MIT license.
- Prepared helpers for environment capture, source retrieval and statistical summaries.
- AI assistance: scaffold preparation; see `docs/ai-usage.md`.
- Verification: repository structure/configuration/link checks and helper smoke checks passed;
  see `docs/scaffold-verification.md`. GitHub commits provide the push evidence.
- No PERIOD environment, benchmark run, reproduction result or extension is complete.

## Future entry template

- Week/check date:
- Member and actual work:
- Commit/PR links and push evidence:
- Measurements/checks completed:
- Failures, blockers and next work:

## 2026-10-28：环境配置与初步运行验收

- 成员：1240013942 刘竞辰；AI 辅助范围见 `docs/ai-usage.md`，组员复核待完成。
- 完成 Windows 组件修复、WSL2/Ubuntu 启动、固定版本工具链构建及 SCHED_DEADLINE 探测。
- 重复验证：刘竞辰在本机 WSL2 直接构建环境完成 doubleFree 搜索与重放：6 个调度、4 个失败调度、0 超时，ASAN 确认 double-free。与吴明阳 Docker 路线形成另一环境的验证证据，不计为新增缺陷。
- 新增预实验：reorder_3 三次独立运行均为 27 个调度、6 个失败调度、0 超时；首轮保存的失败调度重放确认预期断言失败。
- 补充产出：工具链构建日志、依赖版本、SCHED_DEADLINE 探测及 CRLF 换行修改记录。
- 解决 CRLF 脚本错误；保留修改清单、版本及真实观测。试错临时文件留本机归档，提交整理后的最终说明。
- 下一步：固定研究范围并验证 Serial；本轮不作为正式论文结果。
- 提交与推送：本条在提交前编写，尚无本次提交链接；由 GitHub Desktop 实际提交和推送后补充。

## 2026-11-01：明确分支贡献与材料归属

- 根据组员建议，核对主分支 Docker 环境说明和实际 ASAN 重放日志，区分两条环境路线与两位成员的贡献。
- 将环境 README 改为全组入口，将本机操作说明移入刘竞辰的环境记录；保留全部原始预实验数据，修正过时的“尚未验证”状态。
- 本次为文档澄清，没有新增实验，也没有合并或改写组员的材料。
