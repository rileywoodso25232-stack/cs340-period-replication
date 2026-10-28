# 环境配置与运行验收

本机 WSL2 环境已通过工具链构建及两个小用例验证，详见[最终环境记录](LOCAL_SETUP_STATUS.zh-CN.md)。

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
