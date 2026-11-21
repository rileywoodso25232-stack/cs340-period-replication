# AI usage record

## 2026-11-21 表二 PR 主线同步

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-21 | OpenAI Codex | Merged main into the Table 2 branch, reconciled both members' records, checked evidence integrity and statistics, and prepared the pull request | Human review pending | Based on archived experiments, clean-machine rebuild remains pending |

## 2026-11-21 表二提交摘要核查

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-21 | OpenAI Codex | Compared commit messages with archived results, corrected the Serial reorder_5 summary, and drafted provenance, member contributions and publication records | Human review pending | Uses archived experiments and existing statistics, summary and documentation correction only |

核对发现 `e0e63d7` 把 Serial reorder_5 简写为与论文一致，现补充其错误调度均值
816.67 对论文 816 的差异，并记录 21 次检出和 3 次未检出。
相关说明见[提交摘要与更正](table2-submission-summary.zh-CN.md)。

## 2026-11-19 表二 reorder 子集（C2）

DeepSeek Harness（deepseek-flash）编写表二配置、运行/导出脚本与测量/对比脚本，
执行 24 次尝试（4 个 reorder × Period/Serial × 3 次），处理一次 300 秒整轮超时
（提高到 600 秒后重跑），并生成表二统计与差异分析。人工复核待完成。见
[表二批次](../results/raw/local-table2-local-comparison-20261118/README.md) 与
[表二差异分析](table2-analysis.md)。

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-19 | DeepSeek Harness (deepseek-flash) | Table 2 reorder subset runner, 24 attempts, timeout fix, measurements and comparison | Pending human review | 4 programs, 3 attempts, candidate Serial; not full SCTBench |

## 2026-11-18 阶段 9 控制变量检查

DeepSeek Harness（deepseek-flash）编写并执行两个单因素控制实验：15265 单独重复
（改变交错因素）与同/新 IPC 命名空间重放（改变状态隔离因素），并整理证据与差异分析。
第一次命名空间脚本因 rc=126 失败，已归档失败证据并修正后重跑。人工复核待完成。见
[solo](../results/raw/local-table1-15265-solo-20261118/README.md) 与
[namespace](../results/raw/local-table1-15265-namespace-20261118/README.md)。

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-18 | DeepSeek Harness (deepseek-flash) | Two single-factor checks; evidence export; analysis update | Pending human review | n=10 and n=4; environment and driver identity not isolated |

## 2026-11-18 阶段 8 统计与差异分析

DeepSeek Harness（deepseek-flash）根据正式数据生成 Paper vs Ours 表、差异分析与图表，
并更新 claims；没有产生新的实验观测。数值来自 `results/processed/summary.csv`，
判断与局限写入 `docs/analysis.md`；人工复核待完成。见
[Paper vs Ours](../results/processed/table1-paper-vs-ours.md) 与
[差异分析](analysis.md)。

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-18 | DeepSeek Harness (deepseek-flash) | Paper vs Ours table, discrepancy analysis, SVG figures, claims verdict | Pending human review | Based on the scoped formal data; no new experiments; 15265 mechanism unresolved |

## 2026-11-18 阶段 7 正式表一 scoped 批次

DeepSeek Harness（deepseek-flash）编写正式配置与 prepare/run/export 脚本，执行 50 次正式尝试
（PERIOD 三例 + Serial 两例，各 10 次尝试，48 次纳入统计），处理 dry-run 中止、`invalid_replay`、证据导出与
`measurements.csv`/`summary.csv` 生成，并整理日志与文档。实验在本机 WSL2（root）执行，
两套驱动与目标哈希、逐次命令和日志均已保存；人工复核待完成。见[正式批次](../results/raw/local-table1-local-runs-20261118-scoped/README.md)。

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-18 | DeepSeek Harness (deepseek-flash) | Formal scoped Table 1 runs; 50 attempts and 48 included; invalid-replay handling; evidence export; measurements and descriptive summary | Pending human review | Serial covers 2 of 3 CVEs; 15265 instability documented |

## 2026-11-17 阶段 6 表一 CVE 试跑

DeepSeek Harness（deepseek-flash）审查并修正试跑脚本，执行三个 CVE × 3 次有界试跑、
15265 dry-run 稳定性诊断（10 次最小预算 + 10 次完整搜索）与 1 次补充重放，导出并校验证据、
整理日志与文档。实验在本机 WSL2（root）执行，驱动与目标二进制哈希、逐次命令和日志均已保存；
人工复核待完成。这是试跑，不是正式复现，尚无 Serial 基线。见[主批次](../results/raw/local-table1-cve-pilot-20261117/README.md)。

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-17 | DeepSeek Harness (deepseek-flash) | Stage 6 pilot script fixes; 3 CVE × 3 bounded runs; 15265 dry-run diagnostic; bounded supplementary replay; evidence export and logs | Pending human review | 3 attempts per case, PERIOD only, no formal statistics or Serial comparison |

## 2026-11-15 交接核验

同日后续：Codex 创建 experiments/local-ipc-validation，备份并保留当前改动；在独立 Linux 目录与 IPC 命名空间应用组员补丁，实际执行 PERIOD/Serial 候选各一次 reorder_3 搜索和重放。新增观察包装器记录目标退出状态，完整日志/驱动/失败调度及哈希已导出，原文件哈希不变。Git fetch 超时，尚未同步 main。此次实验人工复核待完成；每方法一次，不作正式统计或速度结论。见[验收证据](../results/raw/local-ipc-validation-20261115/README.md)。以下为此前只读检查记录。

Codex 辅助读取 GitHub 固定提交、核对论文与日志、编写交接清单及只读 IPC 检查脚本，并导入署名组员的兼容补丁。实际读取本机 ELF DWARF 并执行补丁 dry-run；未运行新实验、未应用补丁、未代发消息或提交。检查脚本初次编码错误已修复；仓库结构检查通过，人工复核待完成。具体证据见 [阶段 5—6 交接核验](stage5-6-handoff.zh-CN.md)。

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-10-23 | OpenAI Codex | Paper-selection discussion; initial repository layout, documentation and helper scripts | Pending team review; check outputs are recorded separately | No experimental findings were generated |
| 2026-10-27 | OpenAI Codex | Expanded research workflow; local Windows host preflight, WSL prerequisites, pinned source retrieval and a Linux scheduler probe | Pending team review; observed setup states are saved in environment/records/windows-setup/ | No PERIOD build, smoke-test result or research observation has been produced at this stage |

Update this record throughout the project. Record material AI help with code,
analysis and writing, what was checked by humans, and how it was used. Do not claim
human review before it occurs. The final English report includes an AI usage
statement based on this record and the actual contribution history.

## 2026-10-28 更新

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-10-28 | OpenAI Codex | Diagnosed Windows servicing; configured WSL2/LLVM/SVF; executed and archived real bounded smoke runs and replays; organized commit candidates | Team review pending; diagnostics and raw observations retained | Initial environment validation only; no formal replication or Serial comparison |

## 2026-11-05 更新

<!-- reorder3-compat-20261105 -->

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-05 | OpenAI Codex / ChatGPT | Diagnosed IPC layout mismatch; inspected archived ELF DWARF; wrote candidate adaptation, six-run comparison, summary repair and replay helpers; curated evidence and drafted documentation | User executed container commands and backups; six searches completed, both sampled failures replayed with target exit -6; local evidence hashes and repository checks passed; independent team review pending | Single reorder_3 case; candidate Serial correspondence unverified; different period ranges and initialization remain; no speedup or full-paper replication claim |

The initial summary parser missed ANSI-prefixed lines and reported zero schedules. It was corrected using final Round footers without rerunning experiments. Original summaries, logs, correction audit and failed tool attempts were retained in their respective evidence/backup locations.

Same-day scope also includes the earlier Docker reorder_3 search/replay and three native execution batches: ChatGPT assisted with scripts, output interpretation and write-up; the user executed commands and retained evidence. Earlier PERIOD logs remain historical pre-experiments after the IPC mismatch was identified. Final packaging also reviewed the original conversation, preserved failure excerpts, and prepared browser-upload batches; independent team review is still pending.
