# 本机 IPC 兼容补丁：reorder_3 搜索与重放验收

日期：2026-11-15。成员：1240013942 刘竞辰；Codex 执行命令并辅助整理，人工复核待完成。
分支：`experiments/local-ipc-validation`。本次每种候选驱动各一次搜索、一次重放，属于兼容性验收。

## 结果

| 候选方法 | 首次错误调度 | 总调度 | 失败调度 | 超时 | 搜索驱动退出码 | 重放驱动 / 目标退出码 |
|---|---:|---:|---:|---:|---:|---|
| PERIOD | 6 | 27 | 6 | 0 | 0 | 0 / -6 |
| Serial | 10 | 30 | 10 | 0 | 0 | 0 / -6 |

双方第一条保存的失败调度均重现 `reorder_bad.c:80` 的 `Assertion '0' failed`。
目标 -6 为 SIGABRT；驱动原有代码不传递目标退出码，因此单独观察并记录子进程状态。
失败调度数不是不同漏洞数；本轮只有每方法一次，不能计算运行间标准差或评价稳定性。

## 条件与复用范围

- WSL2 Ubuntu 18.04，本次内核 `6.18.58.1-microsoft-standard-WSL2`，root，32 个逻辑 CPU 可用。
- 沿用本机已编译的 reorder_3，SHA-256 为 `debc8f46f33b0c15b39ef111b6bb17a0ff89bf966ff6e7762c45d6b29472fd24`；没有重新构建。
- 运行前重新探测 SCHED_DEADLINE 成功并恢复 SCHED_OTHER，见 [探测记录](deadline-probe.json)。其中 period_smoke_test_run=false 仅指独立探测脚本自身不运行 PERIOD。
- 补丁来自吴明阳的候选驱动；[来源与许可](../../../src/patches/teammate-ipc-compat/README.md)。在新的 Linux 目录复制完整 Python 驱动及目标，分别应用 period.diff / serial.diff，未改上游文件。
- 补丁以 fuzz=0 应用成功；剔除允许修改的三个 IPC 函数和五个数组/容量定义后，搜索控制流 AST 不变。两份补丁应用输出见各方法 patch.log。
- 双方参数均为 `-y -d 3 -f 10000 -t 5`，整轮上限 120 秒，逐次串行执行。Serial 和 PERIOD 保留各自原有周期范围及初始化逻辑，计时仅描述本轮，不计算速度比。
- 整个验证运行在独立 IPC 命名空间；所有实验使用复制后的文件。原文件前后 SHA-256 一致，见 [manifest](manifest.json)。

## 如何查证

- PERIOD：[搜索日志](period/search/search.log)、[结果](period/search/search.result.json)、[重放日志](period/replay/replay.log)、[目标退出记录](period/replay/target-exits.jsonl)。
- Serial：[搜索日志](serial/search/search.log)、[结果](serial/search/search.result.json)、[重放日志](serial/replay/replay.log)、[目标退出记录](serial/replay/target-exits.jsonl)。
- 所有 16 条失败调度均保留在两方法 search/out_reorder_3_bad_1/Errors 下；各自重放第一条，复制为 replay/failure.schedule。
- 搜索与重放目录各有完整 command.json，记录命令、cwd 和关键环境；observe_driver.py 只增加 Popen 子进程状态记录，不改变驱动源文件或退出判定。
- 完整 Linux 目录：`/root/cs340-period/validation/ipc-reorder3-20261115-5t0qjrec`，包含原二进制；本目录排除可执行程序和缓存，保留日志、配置、驱动与失败调度。
- [打包校验](packaging.json)记录每份复制文件的哈希及排除项。所有复制文件逐字节 SHA-256 校验通过；README 和 .gitattributes 为导出后新增说明。

执行入口：[验证脚本](../../../scripts/linux/validate_reorder3_ipc.py)。在 WSL 中运行：

```bash
LC_ALL=C.UTF-8 unshare --ipc --fork python3 /mnt/c/Users/13989/Desktop/OS复现/cs340-period-replication/scripts/linux/validate_reorder3_ipc.py
```

脚本每次生成新目录，先探测、核对布局，再应用补丁、搜索、重放。任何一项不满足验收条件会停止并保留现场。

## 结论与下一步

两种兼容候选驱动在本机 reorder_3 上通过了此次搜索与失败重放，结果与组员对应单用例记录吻合。
此证据不证明完整论文 Serial 基线身份、不覆盖三个 CVE、不解释 15265 的历史异常；实际每个目标线程是否成功设置调度策略也未独立跟踪。
下一步可以对三个 CVE 开展有界预实验，补齐组员材料后确定哪些批次可用于正式统计。
GitHub fetch 本次超时，分支从本地 b3e9fca 创建并保留当前改动，尚未同步最新 main，未提交或推送本轮材料。
