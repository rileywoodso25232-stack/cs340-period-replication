# Weekly progress log

以下按实际工作日期保留双方记录。各阶段条目中的状态对应记录当时，当前发布范围截至表二。
本机表一为 50 次尝试、48 次纳入统计。表二加入后，测量记录共 429 行、统计共 77 组。
本次 PR 同步主线并保留双方材料，拓展与交付发布安排在下周。
## 2026-11-21：Table 1 最终归档与完整性验收

- 完成 Table 1 最终实验材料的分批归档，保留 PERIOD、Serial、Native 的原始实验数据、处理结果及审计证据。
- 吴明阳（1240014957）负责整理并上传 Table 1 实验证据，采用分批提交方式保留原始材料和 Git 历史。
- 罗力汗（1240014507，GitHub：Luolihan663）完成两批材料的 GitHub 提交：
  - Batch-01：3 个 depth-5 审计 CSV，提交 `8c9d1b0`。
  - Batch-02：5 个 Table 1 处理结果及审计文件，提交 `82c26c4`。
- Batch-02 初次上传路径不正确，随后通过补充提交将文件放入 `results/processed/table1-final/`，并清理仓库根目录的重复副本。
- 吴明阳恢复缺失的 `docs/table1-final/README.md`，提交 `9e78249`。
- 使用 `results/audit/table1-final/PACKAGE-SHA256.txt` 核对 GitHub `table1-integration` 分支中的文件：785 条清单记录全部通过 SHA256 验证，失败数为 0。
- 本次完成的是归档完整性验证，不代表所有实验结果均与论文完全一致。实验结论及限制仍以 `docs/claims.md` 和 `docs/analysis.md` 为准。
- 后续工作：完善文档索引、检查实验偏差记录、准备 Presentation 和 Final Report。

## 2026-11-21：表二提交摘要复核

- [PR #5](https://github.com/rileywoodso25232-stack/cs340-period-replication/pull/5) 已发起，目标为 `main`。主线同步提交为 [b16e2e0](https://github.com/rileywoodso25232-stack/cs340-period-replication/commit/b16e2e007df7e5acc6fa3e45eb0622602e85be82)，README、AI 使用记录和周报三处冲突已解决，双方记录与原始证据已核对保留。PR 处于开放审阅状态。
- 摘要与贡献更正已于本日推送，提交为 [0e98854](https://github.com/rileywoodso25232-stack/cs340-period-replication/commit/0e9885498246df2abd89ed3a4d19f104a826608c)，已从 GitHub 回读核验。
- 本次按用户要求把主线 9287fe4 合入表二分支，解决 README、AI 使用记录和周报冲突，双方原始证据按来源保留。PR 的说明覆盖本分支累计的 IPC、表一、分析和表二工作。

- 成员为 1240013942 刘竞辰，OpenAI Codex 辅助核查提交正文及归档数据。
- 更正 `e0e63d7` 正文中“Serial reorder_3/5 一致”的表述。reorder_5 的首次与总调度一致，错误调度均值为 816.67，论文为 816，详情见[提交摘要与更正](table2-submission-summary.zh-CN.md)。
- 统一最终批次为 24 次搜索、21 次检出并重放确认、3 次未检出、零超时。C2 保持部分支持，候选驱动和缩小范围的局限保留。
- 补充吴明阳的 IPC 兼容补丁与早期验证基础，以及刘竞辰本机重复对照、统计和差异分析的增量。
- 本周安排发布表二累计分支，拓展与交付整理留待下周。此条为发布安排，实际提交和推送以 Git 历史为准。
- 发布入口为 [experiments/table2-local-comparison](https://github.com/rileywoodso25232-stack/cs340-period-replication/tree/experiments/table2-local-comparison)，主要实验提交为 [e0e63d7](https://github.com/rileywoodso25232-stack/cs340-period-replication/commit/e0e63d777b96e534611fd2fd7721326c64cf83b1)。[成员贡献表](team.md)记录组员基础与本机增量，摘要更正在后续提交中明确保留。

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
- 阶段提交为 `e0e63d7`，日志提交为 `140115b`、`a45a514`。11 月 19 日记录时均为本地状态，后续发布安排见上方 11 月 21 日记录。

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
- 阶段 8–9 提交为 `2d36326`，日志提交为 `66f32f5`、`60a35e2`，随表二累计分支发布。

## 2026-11-18：阶段 8 统计与 Paper vs Ours

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行整理，人工复核待完成。
- 由 `summary.csv` 生成 `paper_vs_ours.csv`（增加 mode 列）与可读表 `table1-paper-vs-ours.md`：
  18 行中 12 supported、3 partially supported、3 excluded（Serial 15265）。
- 关键差值：Period 7911/9806 三项精确一致；Period 15265 错误调度 1.22（+22.2%）；
  Serial 7911/9806 错误调度 7.9（-1.25%）/4.1（+2.5%）；首次与总调度全部一致。
- C1 判定为 partially supported（scoped）；差异分析写入 `docs/analysis.md`，
  15265 早触发随后完成阶段 9 控制变量检查，具体机制仍未定位。
- 图表：`results/figures/table1-schedules.svg/.png`、`table1-time.svg/.png`。
- 阶段 8 的统计与随后完成的阶段 9 控制检查已一并提交于 `2d36326`。

## 2026-11-18：正式表一 scoped 批次（阶段 7）

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行命令并辅助整理，人工复核待完成。
- 正式配置：深度 5、预算 10000、每组固定 10 次尝试，覆盖 PERIOD 三例及 Serial 的 7911/9806，共 50 次尝试、48 次纳入统计。
- 结果（首次 / 总调度 / 错误调度）：PERIOD 7911 3/19/8（n=9）、9806 6/42/4（n=10）、
  15265 11/96/1.22（n=9，1 次 invalid replay）；Serial 7911 3/19/7.9（n=10）、
  9806 6/42/4.1（n=10）。无超时，深度 5 全部确认。
- 差异：论文称 Period/Serial 在 CVE 基准完全相同；本机 7911/9806 的首次与总调度一致，
  错误调度有 ±1 波动；15265 的 Period 错误数在 1/3 间波动，Serial 候选不可靠故不纳入正式对比。
- 数据：`results/raw/measurements.csv`（288 行）、`results/processed/summary.csv`（30 组）；
  证据：[主批次](../results/raw/local-table1-local-runs-20261118-scoped/README.md)、
  [停止批次 1](../results/raw/local-table1-local-runs-20261118-attempt1-stopped/README.md)、
  [停止批次 2](../results/raw/local-table1-local-runs-20261118-scoped-attempt1-stopped/README.md)。
- 阶段 7 提交为 `a1933be`，随表二累计分支发布。

## 2026-11-17：表一 CVE 本机试跑（阶段 6）

- 成员：1240013942 刘竞辰；DeepSeek Harness 执行命令并辅助整理，人工复核待完成。
- 预建后续阶段分支（table1-local-runs、table2-local-comparison、analysis/local-reproduction、local-extension、report/final-delivery），当前仍在 experiments/table1-cve-pilot。
- 审查并修正试跑脚本：dry-run 的 ASan 中止记为 aborted_at_dry_run 并继续；新增阶段 6 运行、导出、诊断与补充重放脚本。
- 完成表一三个 CVE 的有界试跑：每例 3 次、深度 5、预算 10000、非交互；9/9 搜索完成，8 次批次内重放 + 1 次补充重放确认。
  - CVE-2016-7911：3 / 19 / 8（3 次一致）；CVE-2016-9806：6 / 42 / 4（3 次一致）；CVE-2017-15265：11 / 96 / 1（3 次一致）。
- 15265 的 dry-run UAF 单独诊断：完整搜索 10 次中 4 次 dry-run 中止，完成 6 次均为 96/1/11；最小预算探针 0/10。
- 证据：[主批次](../results/raw/local-table1-cve-pilot-20261117/README.md)、[attempt1](../results/raw/local-table1-cve-pilot-20261117-attempt1-stopped/README.md)、[诊断](../results/raw/local-table1-15265-diagnostic-20261117/README.md)、[补充重放](../results/raw/local-table1-cve-pilot-20261117-replay-supplement/README.md)。
- 这是试跑，不是正式复现：每例 3 次（论文 10 次）、只有 PERIOD、尚无 Serial；正式配置未冻结。
- 阶段 6 提交为 `290f618`，随表二累计分支发布。

## 2026-11-15：本机 IPC 兼容候选验收

- 成员：1240013942 刘竞辰；Codex 执行命令并辅助整理，人工复核待完成。
- 创建 experiments/local-ipc-validation，保留并备份交接改动；本轮 GitHub fetch 超时，尚未同步最新 main。
- 复用吴明阳 IPC 补丁，在独立 Linux 目录与 IPC 命名空间验证。PERIOD 单次搜索 27 调度/6 失败，Serial 候选单次 30/10，均无超时；各首条失败重放确认 reorder_bad.c:80 断言，目标退出 -6，驱动退出 0。
- 保存命令、日志、全部 16 条失败调度、驱动副本、哈希及原文件前后不变检查。[证据](../results/raw/local-ipc-validation-20261115/README.md)。
- 此轮是兼容性验收，不计为新漏洞或正式多次复现；CVE 预实验、组员补证据和正式 Serial 对应关系仍待完成。
- 本机 IPC 验证提交为 `a246883`，随表二累计分支发布。

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

## 2026-11-05：reorder_3 兼容候选驱动对照与失败重放

<!-- reorder3-compat-20261105 -->

- 执行成员：1240014957 吴明阳；容器命令由本人执行，AI 辅助及复核状态见 ai-usage.md。
- 排查旧串行驱动退出码 139；核验目标二进制 DWARF 布局，将双方独立副本的共享内存布局统一为 100/3964/uint16，原文件与失败记录保留。
- 在相同目标、深度参数、运行预算和超时配置下，交替执行双方各三轮：Serial 每轮 30 个调度、10 个失败调度、0 超时；PERIOD 每轮 27 个调度、6 个失败调度、0 超时。
- 双方各重放首轮第一条保存失败调度，均重现 reorder_bad.c:80 的断言，目标退出码 -6；重放驱动退出码均为 0。
- 修正汇总脚本未处理颜色控制码而误记 schedules=0 的问题；原始搜索日志未改变，未为汇总修正重跑实验，原表及修正表均保留。
- 入库材料保留日志、配置、失败调度、源码快照、补丁、许可证与哈希；二进制和缓存保留于完整本地备份。
- 结果及原始证据：[本轮说明](../results/raw/reorder3-compat-20261105/README.md)。
- 限制：本轮为单用例候选驱动验证；双方实际周期范围与初始化逻辑仍不同，不计算加速比，不宣称完整论文 Serial 基线或整体复现完成。多条失败调度不计为多个缺陷。
- 验证：本轮材料复制后仓库检查已通过；本条写入后应再次运行检查。组员独立复核待完成。
- 提交/PR/推送：待实际提交和推送后补充链接，本记录不作为已推送证据。

### 同日此前完成的预实验与 Native 补充对照

- Docker 单次验证：reorder_3 搜索 27 个调度、6 个失败调度、0 超时，保存失败调度并重放确认第 80 行断言。
- Native 补充对照：三组各 1000 次原生执行，均 0 断言、0 超时、0 其他运行错误；对应旧 PERIOD 三组各 27 个调度、6 个失败调度、0 超时。
- 后续发现旧 Python 驱动数组布局与目标运行时不一致，上述 PERIOD 数据留作历史预实验，不与修复后结果合并。Native 是本次自定义配置，未宣称复现论文全部基线。
- 证据：[Docker 预实验](../results/raw/docker-reorder3-20261105/README.md)、[Native 补充对照](../results/raw/reorder3-native-period-20261105/README.md)。
- 今日提交采用 GitHub 网页分批上传并创建同一个 PR；本地 Git 暂存状态不作为已上传证明。PR 链接待创建后补充。
### 2026-11-07 后续更新

- 11 月 5 日的实验材料已通过 [PR #3](https://github.com/rileywoodso25232-stack/cs340-period-replication/pull/3) 合并至 `main`，罗力汗完成了 PR 审核。

## 2026-11-13：表 1 子集进展

- 吴明阳已将三个选定用例的 PERIOD 运行记录推送到实验分支，每个用例独立运行三次。
- 已更新根目录 README。统计汇总、论文原值对照和组员复核待完成。

## 2026-11-14：Table 1 子集复核与深度 5 检查
- Table 1 深度 3 复核：三个用例各三轮，九轮全部完成，零超时。逐轮数据见 [复核说明和统计](../results/raw/table1-verification/README.md)。
- 深度 5 检查：十轮尝试，九轮完成，完成轮次零超时。15265 第 2 轮因 ASan 报错中止，保留在逐轮表中，排除出完成轮次统计。十份原始日志已在本地核对 SHA-256，具体驱动版本待核实。见 [深度 5 说明、统计和校验记录](../results/raw/depth5-verification/README.md)。
- 计时口径：7911 的 11 月 13 日原始第 1 轮墙钟时间包含等待按键，排除出耗时比较。原始日志和调度计数保留。组员独立复核待完成。
