# 本机环境配置与验证记录

更新：2026-10-28。当前状态：工具链构建和两个小用例的运行验证通过；尚未开展正式论文结果对比。

## 已验证环境

- Windows 11 + WSL2，发行版 `CS340-PERIOD`，Ubuntu 18.04.5；Linux 内核 `6.18.54.1-microsoft-standard-WSL2`，32 个逻辑 CPU，当前使用 root。
- GCC 7.5.0、LLVM/Clang 10.0.0、Python 2.7/3.6、NumPy 1.13.3、sysv_ipc 0.6.8、wllvm 1.1.6。精确包版本见 [包清单](records/linux-setup/packages.tsv)。
- 固定源码：`cb8deb9a176e5bb292d70d46557dd61dc0e98069`。Linux 目录：`/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069`。
- SCHED_DEADLINE 独立探测成功并恢复原策略；[原始记录](records/linux-setup/deadline-probe.json)。这不等于所有实际线程调度都已被独立追踪验证。
- SVF、静态分析插件、插桩工具及 doubleFree/reorder_3 均编译成功。构建日志和版本记录在 `records/linux-setup/`。

## 小实验结果（非正式实验）

| 用例 | 调度数 | 失败调度数 | 超时 | 重放 |
| --- | --- | --- | --- | --- |
| doubleFree，一次 | 6 | 4 | 0 | ASAN 明确报告 double-free |
| reorder_3，三次独立运行 | 每次 27 | 每次 6 | 每次 0 | 首轮保存调度重现预期断言失败 |

[原始日志与汇总](../results/raw/local-smoke-20261028/summary.json)保留所有本轮运行及重放证据。失败调度数不是不同缺陷数量。reorder_3 工具报告耗时为 4.18727、2.11832、2.15469 秒，未控制后台负载，仅作可行性参考。

## 重要偏差与已解决问题

1. Windows 组件损坏和部署挂起曾导致 vmcompute 缺失。首次修复失败；清理缓存后重试于 02:17:57 成功，CBS 报告修复 2003 项损坏记录。不能据此断言缓存就是最初故障原因。
2. 13:24 重启后 vmcompute/hns 恢复、待部署队列消失；随后 Ubuntu 导入及启动成功，见 [Linux 首次启动记录](records/windows-setup/linux-first-boot.json)。无需在正常机器上复用清缓存、离线镜像或系统修复步骤。
3. git archive 导出的部分上游脚本仍含 CRLF，首轮 doubleFree 构建失败。仅在 Linux 副本转换换行后通过；[修改清单](records/linux-setup/line-endings.json)，另有 reorder_3/build.sh 和 cleanDIR.sh。没有修改算法逻辑。
4. Windows localhost 代理未同步到 WSL 的提示仍存在；Ubuntu 官方软件源实测下载成功，不代表所有外部站点均可访问。
5. LLVM 压缩包已核对本地 SHA-256，但发布者签名尚未独立验证，详见 [包记录](records/windows-setup/llvm-package.json)。

完整试错记录保留在本机忽略目录 `.cache/commit-cleanup-20261028/`，本次提交保留上述必要经过和最终验证证据。失败研究观测没有被删除。

## 下一步

进入工作流阶段 5：固定研究问题、正式用例和 Serial 基线。尚未验证 Serial、更大规模用例及跨机器复现；不能将初步运行验收称为完整论文复现成功。
