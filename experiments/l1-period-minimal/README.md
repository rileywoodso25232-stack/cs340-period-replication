# L1：周期调度最小复现（教学示例）

本目录用**可运行的代码**解释论文 §3.3 的「周期执行（periodical execution）」语义，
并在论文图 1 的简化程序（CVE-2016-1972）上复现三个并发缺陷：

| 缺陷 | 论文中的 bug depth | 论文中的周期数 | 本示例 |
| --- | --- | --- | --- |
| NPD（空指针解引用） | 2 | 3 | 触发 |
| UAF（释放后使用） | 4 | 5 | 触发 |
| DF（二次释放） | 5 | 6 | 触发 |

> **范围声明**：这是用于理解论文机制的教学示例，**不是**表一／表二的测量证据，
> 不产生 claim，也不与 IPB／IDB／PCT 比较。正式复现见
> [`experiments/baseline`](../baseline/README.md) 与 `results/` 下的批次记录。

## 与小组正式复现的关系

- 正式复现使用上游 PERIOD／Serial 驱动和 SCTBench／CVE 基准程序，统计首次命中调度数；
- 本目录只保留论文图 1 的程序，**手写 5 个调度**，用来看清「换周期 = 换线程」，
  不包含自动调度生成、动态关键点切片（DKPS）和前缀反馈；
- macOS 上即可运行，不需要 Linux 实时调度、root 或虚拟机。

## 环境与运行

已在本机 macOS 14（arm64，Apple clang 15）实测；Linux + gcc/clang 同样可用。

```bash
cd experiments/l1-period-minimal
make            # 编译
make run        # 跑全部 5 个调度
./period_l1 npd # 只跑一个：npd / uaf / df / safe / var
```

典型输出（每行末尾是执行到该关键点**之前**的共享变量状态）：

```text
=== NPD（论文图 3(g) 的配方，末尾补 T1 的尾部）
    调度: {T0×1}·{T1×1}·{T0×8}·{T1×8}
    [P1] T0  L6    (done=0, waiters=0, lock=可用)
    [P2] T1  L6    (done=0, waiters=0, lock=可用)
    ...
    [P3] T0  L16   (done=1, waiters=0, lock=已释放)
    [P4] T1  L8    (done=1, waiters=0, lock=NULL)
    [P4] T1  L9    (done=1, waiters=1, lock=NULL)
    >>> 触发 bug：NPD（空指针解引用）
```

## 调度表怎么读

```text
{T0×4} · {T1×1} · {T0×4} · {T1×7} · {T0×1} · {T1×1}
  P1        P2        P3        P4        P5        P6
```

- `{T0×4}`：本周期只允许 T0 执行 4 个关键点；
- `·`：换周期，等于一次受控的上下文切换；
- 线程每到一个关键点先过检查站 `sched_point()`：配额没用完且轮到自己就放行，
  配额用完就推进周期，不是自己的周期就用 `pthread_cond_wait` 等。

这对应论文的「周期执行」：**不抢占线程，而是让线程等到下一个周期**。

## 三个缺陷的触发条件

被测函数有 9 个关键点（L6、L8、L9、L11、L12、L13、L14、L15、L16），三个共享变量
`done`、`waiters`、`lock` 组合出三类缺陷：

| 缺陷 | 被周期边界切开的两个动作 | 触发条件 |
| --- | --- | --- |
| NPD | T1 的 L6（检查 `done`）与 L9（用锁） | 检查时 `done==0`，用锁时 T0 已把 `lock` 置 NULL |
| UAF | T0 的 L15（`free`）与 L16（置 NULL） | T1 在「已释放、尚未置 NULL」的窗口里使用锁 |
| DF | L14（`--waiters` 判断）与 L15（`free`） | 两个线程都判断出自己是「最后一个」并各自 `free` |

`./period_l1 df` 的关键两步：

```text
[P4] T1  L15   (done=1, waiters=0, lock=可用)     <- 第一次 free
[P5] T0  L15   (done=1, waiters=0, lock=已释放)   <- 第二次 free，触发 DF
```

## 用 AddressSanitizer 独立复核

`make demo-asan` 会关闭代码内的检查（`USE_ORACLE=0`），让真实内存错误暴露：

```bash
make demo-asan
# NPD -> AddressSanitizer: SEGV ... in pthread_mutex_lock
# UAF -> AddressSanitizer: heap-use-after-free ...
# DF  -> AddressSanitizer: attempting double-free ...
```

这说明三类错误不是由示例自带的判定逻辑「制造」的。

## 与论文实现的差异

| 论文 | 本示例 | 原因 |
| --- | --- | --- |
| `SCHED_DEADLINE` 周期执行 | pthread 条件变量 + 周期／配额 | macOS 无 `SCHED_DEADLINE`；语义等价且完全确定 |
| 自动调度生成 + 前缀反馈 | 手写 5 个调度 | 只演示「周期能控制交错」，生成器属于后续阶段 |
| 尾部关键点由时间片放行 | 显式补一个尾部周期 | 把「看不见的尾部」写进调度表，便于观察；因此 NPD 显示 4 个周期、UAF 显示 6 个 |
| 真实崩溃或检测器判定 | 默认用内置检查，`USE_ORACLE=0` 时交给 ASan | 便于一次跑完多个用例 |

## 复现记录

- 环境：macOS 14（Darwin 23.5.0，arm64），Apple clang 15.0.0；
- 命令：`make && ./period_l1`，连续运行 50 次输出一致（确定性调度）；
- 结论：5 个调度中 4 个触发缺陷，`safe` 用例不触发；
- 该示例由 AI 辅助编写，记录见 [`docs/ai-usage.md`](../../docs/ai-usage.md)，人工复核待完成。
