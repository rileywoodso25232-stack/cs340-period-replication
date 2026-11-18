# 表二本机复现：SCTBench reorder 线程数系列（2026-11-18）

状态：**formal_completed**，24/24 次尝试完成。这是表二的缩小规模子集，不是完整 SCTBench 复现。

## 范围

- 用例：`CS.reorder_3_bad`、`CS.reorder_4_bad`、`CS.reorder_5_bad`、`CS.reorder_10_bad`
  （SCTBench 的线程数系列，bug 类型均为 AF，深度 2）。
- 方法：Period、Serial；每例每方法 **3 次**（课程最低要求；论文为 10 次，属声明性偏差）。
- 参数：深度 3、预算 10000、子进程 5 秒、整轮 600 秒、非交互。
- 选择理由：该系列直接检验论文“并行 Period 比串行 Serial 搜索空间更小”的现象；
  reorder_3 已有本机兼容验证，风险最低。
- 排除：SCTBench 其余程序（CB、其他 CS）未纳入；结论只限这个子集。

## 结果（均值，3 次；首次/总调度/错误调度）

| 方法 | 用例 | 首次 | 总调度 | 错误调度 | 论文（表二） |
|---|---|---:|---:|---:|---|
| period | reorder_3 | 6 | 27 | 6 | 6 / 27 / 6 |
| period | reorder_4 | 9 | 100 | 12 | 9 / 100 / 12 |
| period | reorder_5 | 12 | 225 | 20 | 12 / 225 / 20 |
| period | reorder_10 | 27 | 2350 | 90 | 27 / 2350 / 89 |
| serial | reorder_3 | 10 | 30 | 10 | 10 / 30 / 10 |
| serial | reorder_4 | 47 | 384 | 90 | 37 / 384 / 90 |
| serial | reorder_5 | 283 | 5040 | 816.67 | 283 / 5040 / 816 |
| serial | reorder_10 | 未找到 | 10001 | 0 | `%` / `L` / 0 |

- Period 的 3/4/5 三项与论文完全一致；reorder_10 只差 1 个错误调度。
- Serial 的 reorder_3 完全一致；reorder_4 总调度/错误数一致但首次触发为 47（论文 37）；
  reorder_5 总调度/首次一致，错误数 815–819（均值 816.67，论文 816）；
  reorder_10 三次都在 10000 调度上限内未找到，和论文 `% / L / 0` 一致。
- 0 超时；所有找到的失败调度均重放确认（断言 `reorder_bad.c:80`，目标退出 -6）。

## 与论文的核心对照

| 用例 | Period 总调度 | Serial 总调度 | 论文 Period → Serial | 本机 Period → Serial |
|---|---:|---:|---|---|
| reorder_3 | 27 | 30 | 27 → 30 | 27 → 30 |
| reorder_4 | 100 | 384 | 100 → 384 | 100 → 384 |
| reorder_5 | 225 | 5040 | 225 → 5040 | 225 → 5040 |
| reorder_10 | 2350 | 10001（未找到） | 2350 → L | 2350 → 10001 |

**核心现象复现**：线程数越多，Serial 需要的调度数相对 Period 越多；到 reorder_10，
Serial 在 10000 上限内找不到，Period 仍只需 2350。

## 异常与解释

1. **Serial reorder_4 首次触发 47 vs 论文 37**：总调度和错误数完全一致，只有首次位置不同。
   候选 Serial 驱动的调度顺序/记录可能与论文实现不同；不能排除驱动身份问题。
2. **Serial reorder_5 错误数 815/819/816，均值 816.67**：有 ±2 的重复运行波动；
   首次和总调度稳定。与论文 816 的差异很小，但不是逐次精确。
3. **Period reorder_10 错误数 90 vs 论文 89**：差 1，首次/总调度完全一致。
4. **Serial reorder_10 总调度 10001 vs 论文 L（10000）**：多 1 个调度；
   这是驱动计数上限的边界差，未找到的结论一致。

## 证据

- `manifest.json`：配置/驱动/目标哈希、逐次结果、原文件不变检查；
- `summary.csv` / `summary_by_case.csv`：24 次尝试与聚合；
- 失败调度：所有找到的轮次均保存 `out_*/Errors/`（reorder_5 每轮 815–819 条）；
- 共 3555 份文件，约 18.8 MB；`packaging.json` 记录逐文件 SHA-256，二进制未导出；
- WSL 完整目录：`/root/cs340-period/table2/local-table2-local-comparison-20261118-xgo0jv7h/`；
- 运行入口：`scripts/linux/run_stage_table2.sh`；配置：`config/table2-local-comparison.json`。

## 偏差与局限

1. 每例每方法 3 次，不是论文的 10 次；只作描述统计。
2. 只选 4 个 reorder 程序（同一 bug 类型、深度 2），不能代表完整 SCTBench；
   存在选择偏差，不能外推整个表二。
3. Serial 是组员补丁的候选实现，身份未独立证明；reorder_4 的首次差异可能与此有关。
4. WSL2 内核 6.18 vs 论文 Ubuntu 18.04；整轮超时从 300 提到 600 秒（reorder_5 约 350 秒）。
5. 计时只作描述，不用于方法优劣结论。
