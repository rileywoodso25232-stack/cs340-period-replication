# 本机环境配置与验证记录

更新：2026-10-28。当前状态：工具链构建和两个小用例的运行验证通过；尚未开展正式论文结果对比。

## 记录归属与贡献范围

本记录属于刘竞辰（1240013942）本机的独立环境验证。
主分支已有吴明阳（1240014957）的 WSL2 + Docker 环境及 doubleFree 重放材料，见 [Docker 环境材料](https://github.com/rileywoodso25232-stack/cs340-period-replication/blob/main/environment/setup-evidence/README.md)。

本分支补充 WSL2 内直接构建路线、工具链构建日志、依赖版本、SCHED_DEADLINE 独立探测与排障记录，以及 reorder_3 三次独立预实验和首轮失败调度重放。
doubleFree 是在另一环境中的重复验证，不计为新增缺陷；reorder_3 是新增的预实验记录，不构成正式论文结果对比。AI 辅助范围见 [AI 使用记录](../docs/ai-usage.md)。

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

## 本机继续工作

在 PowerShell 中进入 Linux：

```powershell
wsl -d CS340-PERIOD
```

在 Linux bash 中加载本组环境脚本（仓库位置不同需修改路径）：

```bash
source /mnt/c/Users/13989/Desktop/OS复现/cs340-period-replication/scripts/linux/period_env.sh
cd "$ROOT_DIR"
```

随后按[安装验证说明](../experiments/smoke/README.md)运行。源码目录保存构建产物，预实验使用独立目录，避免清理脚本删除旧观测。

## 新机器搭建边界

当前脚本是已配置 Linux 中的构建辅助，不是一键 Windows 安装器。

1. 准备 Ubuntu 18.04 Linux 环境，确认实际内核、root/调度权限和网络；运行 `scripts/linux/probe_deadline.py`。
2. 使用 `config/upstream.json` 固定源码，放入 Linux 文件系统。现有脚本默认 `/root/cs340-period/source/<commit>`，换路径时须同步修改环境与构建脚本。
3. 按固定版本 `INSTALL.md` 安装系统构建依赖，安装 LLVM 10.0.0 到源码根目录的 `clang+llvm`。本次实际包版本和安装日志在 `records/linux-setup/`。
4. 根据 `records/linux-setup/line-endings.json` 将 Linux 副本中相关脚本 CRLF 转 LF；reorder_3 的两个 shell 脚本也需转换。
5. 执行 `bash scripts/linux/configure_period.sh` 构建 SVF、分析插件和插桩工具；该脚本要求前述依赖和 LLVM 已就绪。每阶段日志存入 `/root/cs340-period/setup-logs/`。
6. 编译最小程序并进行搜索、失败重放，保留全部尝试。新机器必须重新验证，不能复用本机结果充当新结果。

## 记录规则

- 固定源码、依赖、编译参数、资源、命令、日志和退出状态；偏差登记在 `docs/deviations.csv`。
- 保留真实失败调度和重放证据；小实验与正式结果分开。
- `records/windows-setup/` 中早期已提交文件属于历史快照，当前状态以最终环境记录与 Linux 验证为准。
- `scripts/windows/` 中原有脚本属于初期安装辅助，不是此次已验证的完整搭建路线。临时排障脚本已移至本机归档。
- 原作者推荐的 Docker 路线尚未在本机验证；当前使用 WSL2 内直接构建。
