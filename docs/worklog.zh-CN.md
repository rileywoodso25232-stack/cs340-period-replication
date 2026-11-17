# 本地推进日志（2026-11-17 起）

> 规则：每个小任务结束或遇到问题时追加一条；只追加，不改写历史条目。
> 本文件记录本机执行过程（命令、结果、证据、问题），课程面向的摘要仍写入
> [weekly-log](weekly-log.md)。在分支任务完成并经确认前不提交 Git。

## 2026-11-17 00:55 | experiments/table1-cve-pilot | 建立阶段分支骨架

- 目的：让每个阶段任务有独立分支，后续按阶段切换与保存。
- 操作：使用 GitHub Desktop 自带 git（`app-3.6.10/resources/app/git/cmd/git.exe`），
  以当前 HEAD `a246883` 为基线创建 5 个后续分支，不切换当前分支。
- 结果：新增 `experiments/table1-local-runs`、`experiments/table2-local-comparison`、
  `analysis/local-reproduction`、`experiments/local-extension`、`report/final-delivery`。
  当前 HEAD 仍为 `experiments/table1-cve-pilot` @ `a246883`。
- 工作区状态：`docs/research-workflow.zh-CN.md`（修改）；`config/table1-cve-pilot.json`、
  `docs/local-branch-workflow.zh-CN.md`、`scripts/linux/run_table1_pilot.py`（未跟踪）。
  未执行 `git add` / `commit` / `push`。
- 问题：无。
- 下一步：审查并修正试跑脚本的 ASan 退出码判断，然后做 WSL 预检。

## 2026-11-17 01:05 | experiments/table1-cve-pilot | 脚本修正与 WSL 预检

- 目的：让试跑脚本可在 Python 3.6 下重复执行，并确认 WSL 实验环境与旧证据。
- 脚本修改：
  - `run_table1_pilot.py`：重放子进程退出码接受 `{1, -6}` 并单独记录 `last_child_exit`、
    `replay_exit_confirmed`（仍以 ASan 报告文本+预期缺陷+二进制名为准）；`pilots` 目录改为
    `parents=True`。
  - 新增 `run_stage6_pilot.sh`（一次完成预检+prepare+run+export，全部 tee 到日志）；
    新增 `export_table1_pilot.py`（哈希校验、生成 summary/summary_by_case/packaging）。
  - `.gitignore` 增加本次证据目录的 `out_*/Errors` 例外。
- WSL 预检：root；内核 6.18.58.1；32 逻辑 CPU；31G 内存；`/` 余量 952G；无遗留驱动进程；
  共享内存为空；`python3` 3.6.9；`gcc` 7.5.0；`clang` 仅存在于
  `$ROOT/clang+llvm/bin`（已把脚本检查改到该路径）；WSL git 2.17 不支持
  `branch --show-current`（已改用 `rev-parse --abbrev-ref HEAD`）。
- 发现的旧证据（未删除、未改写）：
  - `/root/cs340-period/pilots/local-table1-pilot-20261116-t20urt4f`：11/16 22:22 创建，
    `status=pilot_completed`，9/9 完成，首次/总/错误为 7911 3/19/8、9806 6/42/4、
    15265 11/96/1，重放均确认，原文件哈希未变；但 manifest 无 `runner_sha256`/
    `frozen_driver_files`，属较早脚本版本，证据链弱于当前要求。
  - `/root/cs340-period/pilots/local-table1-cve-pilot-20261117-fojyh1ug`：11/17 00:17 创建，
    `status=prepared`、0 次运行，3 个目标已编译；因脚本其后被修改，当前脚本拒绝在其上运行。
- 决定：保留两个旧目录作对照，不复用、不改写；用当前脚本重新 `prepare` + `run`，生成带
  runner/driver/冻结文件哈希与逐次退出码的完整证据。
- 问题：无阻塞。
- 下一步：后台执行 `scripts/linux/run_stage6_pilot.sh`，完成后导出并核对。

## 2026-11-17 01:03 | experiments/table1-cve-pilot | 首次执行失败：git 2.17 参数不兼容

- 现象：`prepare` 在写 manifest 时调用 `git branch --show-current`，WSL git 2.17 返回 129
  （unknown option），`CalledProcessError` 使 prepare 中止；wrapper 正常捕获并退出。
- 影响：只生成 `/root/cs340-period/pilots/local-table1-cve-pilot-20261117-w1by5ssa/`
  配置副本，没有 manifest，未执行任何搜索或重放；未触碰旧目录与仓库文件。
- 证据：`/root/cs340-period/pilots/stage6-20261116-165749.log`。
- 处理：
  - `run_table1_pilot.py` 改用 `git rev-parse --abbrev-ref HEAD`；
  - wrapper 固定 `LC_ALL/LANG=C.UTF-8`，避免 Python 3.6 对中文路径产生 surrogate 转义；
  - wrapper 仅在 manifest 存在时尝试导出，避免无意义报错。
- 下一步：重跑完整阶段 6。

## 2026-11-17 01:00 | experiments/table1-cve-pilot | 阶段 6 停在 15265 的 dry-run ASan 中止

- 本轮结果（新证据目录，当前脚本）：
  - CVE-2016-7911 第 1 次：19 总调度 / 8 错误 / 0 超时 / 首次 3，重放确认 SEGV，子进程退出 -6；
  - CVE-2016-9806 第 1 次：42 / 4 / 0 / 首次 6，重放确认 double-free，退出 -6；
  - CVE-2017-15265 第 1 次：搜索在 `Perform Dry Run!` 阶段即触发
    `AddressSanitizer: heap-use-after-free`（0.315s，日志无 `End Testing!`），
    脚本按停止规则判 `incomplete_search` 并停止；未进入受控搜索，也未重放。
- 处理：manifest 记为 `stopped_for_inspection`；证据已导出到
  `results/raw/local-table1-cve-pilot-20261117/`（143 份文件、8+4 条失败调度、
  约 0.55 MB、逐文件哈希校验）；未补跑、未删除异常轮次、未提交。
- 对照：
  - 本机 11/16 22:22 旧批次 15265 三次均完成；
  - 组员 11/14 深度 5 的 10 次尝试中有 1 次 ASan 中止。
  说明该目标在非受控 dry run 阶段偶发真实 UAF，属于需要单独报告的稳定性问题。
- 影响：本批次目前只有 2/3 用例得到受控搜索指标；15265 缺少总调度/错误调度。
- 待定：先做 dry-run 稳定性诊断，还是改批次规则继续，或等组员 15265 原始日志。
- 证据：`results/raw/local-table1-cve-pilot-20261117/`、
  WSL `/root/cs340-period/pilots/local-table1-cve-pilot-20261117-198pg1ik/`、
  `stage6-20261116-165830.log`。
- 下一步：等用户选择处理方式后再继续。

## 2026-11-17 01:10 | experiments/table1-cve-pilot | 用户选择：先诊断 15265 稳定性

- 决定：不改正式试跑配置，先用冻结的驱动/二进制统计 dry-run 中止率。
- 新增 `scripts/linux/diagnose_15265_stability.py`：校验 pilot 的驱动与目标哈希后，运行
  10 次最小预算（`-f 1`，含 dry run）与 10 次完整搜索（`-f 10000`）；每次独立目录、
  `unshare --ipc --fork` 隔离，记录日志、命令、退出码、分类（dry_run_asan_abort /
  search_abort / completed）与完整搜索指标。
- 证据输出：`results/raw/local-table1-15265-diagnostic-20261117/`（逐文件哈希）。
- 使用的 pilot：`/root/cs340-period/pilots/local-table1-cve-pilot-20261117-198pg1ik`
  （driver 10ab60b5…，target 哈希来自该 manifest）。
- 下一步：读取诊断结果，向用户汇报中止率与建议。

## 2026-11-17 01:15 | experiments/table1-cve-pilot | 15265 稳定性诊断结果

- 最小预算探针（`-f 1`，10 次）：10/10 完成，每次 2 个调度、0 错误、0 超时。
- 完整搜索（`-f 10000`，10 次）：6/10 完成，4/10 在 `Perform Dry Run!` 之后、
  `Perform DBDS Run` 之前中止；4 次均为同一位置 `heap-use-after-free`
  （`2017-15265+0x4df3a7`，约 0.315 秒）。
- 完成的 6 次全部为 96 总调度 / 1 错误 / 0 超时 / 首次 11，与论文表一一致。
- 解释：dry run 用同一个目标程序、`ASAN_OPTIONS=abort_on_error=1`；该 UAF 在非受控
  初始化阶段偶发触发，驱动把 -6 视为失败并退出。短预算探针未复现（0/10），说明中止率
  随时序/随机性波动，短探针不能预测正式批次。
- 影响：3 次尝试的 15265 很可能会出现 1 次以上中止；若规则仍是“一遇 incomplete_search
  就整批停”，批次大概率反复中断。
- 证据：`results/raw/local-table1-15265-diagnostic-20261117/`
  （aggregate.json、summary.csv、20 份日志与命令/结果，149 份文件，哈希校验）。
- 建议：把“dry-run 阶段 ASan 中止”定义为 `aborted_at_dry_run`，计入尝试分母但不重放、
  不替换；其余异常（超时、构建失败、重放未确认、搜索中途异常）仍立即停止。之后重跑整批。
- 下一步：等用户确认规则修改与重跑方式。

## 2026-11-17 01:25 | experiments/table1-cve-pilot | 规则修改与 attempt1 归档

- 用户决定：改规则后整批重跑。
- 规则修改：
  - `config/table1-cve-pilot.json`：新增 `dry_run_abort_policy`，`stopping_rule` 改为
    “dry-run 的 ASan 中止记为 aborted_at_dry_run 并继续”；其他异常（构建、超时、
    重放未确认、DBDS 开始后的搜索中止、原文件变化）仍立即停止。
  - `run_table1_pilot.py`：搜索阶段识别 `Perform Dry Run!` 后、`Perform DBDS Run` 前
    的 ASan 中止，记录 `aborted_at_dry_run`、不重放、不替换，继续后续尝试；结束时统计
    `manifest['aborted_at_dry_run']`。
  - `export_table1_pilot.py`：`summary_by_case.csv` 增加 `aborted_at_dry_run` 列。
  - `.gitignore`：证据例外改为 `local-table1-cve-pilot-20261117*` 通配，并覆盖诊断目录。
- 归档：已停止的批证据 `local-table1-cve-pilot-20261117/` 改名为
  `local-table1-cve-pilot-20261117-attempt1-stopped/`，不删除、不改内容；
  新批次将使用原目录名。
- 静态验证：配置 JSON 可解析；两脚本 AST 通过；用真实中止/完成日志验证了
  dry-run 分类条件（中止=True，完成=False）。
- 下一步：重跑 prepare+9 次尝试+导出。

## 2026-11-17 01:35 | experiments/table1-cve-pilot | 第二批：9/9 搜索完成，15265 run3 重放被 dry-run 中止

- 第二批结果（新规则）：
  - 7911：3/3 完成，均 19/8/0/首次 3，重放确认；
  - 9806：3/3 完成，均 42/4/0/首次 6，重放确认；
  - 15265：run1、run2 完成（96/1/0/首次 11）且重放确认；run3 搜索完成
    （96/1/0/首次 11），但重放日志显示它在 `Perform Dry Run!` 阶段再次触发同一 UAF，
    没有进入 `Perform Reproduction!`，脚本判 `replay_not_confirmed` 并停止。
- 重要区分：这不是“保存的失败调度不能重现”，而是重放前的 dry run 又被真实 UAF 打断；
  该次搜索数据本身有效，但缺少独立重放确认。
- 本批搜索阶段没有出现 dry-run 中止，新加的 `aborted_at_dry_run` 分支未被触发；
  manifest 因最后异常停在 `stopped_for_inspection`，9 次尝试均已执行。
- 证据：`results/raw/local-table1-cve-pilot-20261117/`（268 份文件，哈希校验；
  summary.csv 与 summary_by_case.csv 已生成）。
- 待定：对 run3 做补充重放，还是接受 8/9 重放确认并结束阶段 6。
- 下一步：等用户选择。

## 2026-11-17 23:45 | experiments/table1-cve-pilot | 阶段 6 收尾：补充重放确认

- 用户选择“补充重放”。新增 `scripts/linux/replay_15265_supplement.py`：用第二批 15265
  第 3 次保存的失败调度（SHA-256 `97a5df88…`），最多重放 3 次，每次独立目录与 IPC 命名空间，
  所有尝试保留。
- 结果：第 1 次即 `confirmed`——进入 `Perform Reproduction!`、ASan 报告
  `heap-use-after-free`、目标退出 -6；补充证据导出到
  `results/raw/local-table1-cve-pilot-20261117-replay-supplement/`（13 份文件，含 README 与哈希校验）。
- 至此第二批 9/9 次搜索均有重放证据（批次内 8 次 + 补充 1 次）；原始 manifest/summary
  未改写，仍如实记录第 3 次为 `needs_inspection`。
- 证据说明已补齐：主批次、attempt1、诊断、补充重放四个目录各有 README；
  主批次 README 含配置、环境、哈希、逐次结果、与论文/组员对照、局限。
- 阶段 6 验收对照：配置/脚本已审查并实际执行；9 次尝试状态、首次检出、总调度、错误调度、
  超时、重放均可追溯；dry-run 不稳定已量化并单独报告；证据已导出且哈希校验。
- 未提交、未推送；工作区仍包含全部代码、证据和文档改动。
- 下一步：向用户汇报阶段 6 完成情况，等确认后再 commit 并进入
  `experiments/table1-local-runs`。
