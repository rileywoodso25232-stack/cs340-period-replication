# 本机环境搭建记录

日期：2026-10-27。当前目标：先验证本机能运行 PERIOD，再决定是否用于正式实验。

## 已观测的硬件与系统

| 项目 | 实测信息 |
| --- | --- |
| 操作系统 | Windows 11 家庭版中文版，10.0.26200，64 位 |
| CPU | Intel Core i9-14900HX，24 核／32 逻辑处理器 |
| 系统可见内存 | 约 63.7 GiB |
| BIOS 虚拟化与二级地址转换 | 已开启／支持 |
| 初始 Hypervisor 状态 | 未运行 |
| 初始 WSL／Docker 状态 | WSL 未安装；未检测到 Docker 命令或默认安装位置 |
| 初始磁盘空闲 | C 盘约 61.8 GiB；D、E 盘有更多空间；后续安装仍需复查 |

上述资源足以尝试小规模验证；正式实验适用性尚未证实。
详细原始记录见 [host-preflight.json](records/windows-setup/host-preflight.json)
和 [windows-tools.json](records/windows-setup/windows-tools.json)。

## 本轮已完成

1. 在管理员授权后启用了 Microsoft-Windows-Subsystem-Linux 和 VirtualMachinePlatform。
   两个功能均从 Disabled 变为 Enabled，Windows 返回 RestartNeeded=true。
2. 获取并检出了上游固定提交 cb8deb9a176e5bb292d70d46557dd61dc0e98069，未修改上游代码。
3. 直连 GitHub Git 和 codeload 曾失败；使用本机现有系统代理进行单次 Git fetch 后成功，
   没有将代理写入全局或仓库 Git 配置。见 [源码获取记录](records/windows-setup/source-retrieval.json)。
4. 准备了 [Linux 调度能力探测脚本](../scripts/linux/probe_deadline.py)，
   用于进入 Linux 后实际请求 SCHED_DEADLINE，再恢复普通调度。
   本轮只验证了它在 Windows 下正确拒绝运行；未执行 Linux 调度探测。

## WSL 安装渠道与当前状态

在线命令 wsl --install --no-distribution --web-download 未及时完成下载。
微软官方 GitHub API 可访问，但 GitHub 网页下载端点出现 TLS 握手失败；
通过发布资产 API 的大型包下载速度较慢，已停止本任务的重复下载并保留其部分文件。
准备使用微软手动安装文档提供的 Windows 内置 WSL2 内核包作为后备路线。

安装是否完成以 [wsl-install-state.json](records/windows-setup/wsl-install-state.json) 为准。
此记录中 restart_required=true 表示必须先重启系统，不能据此声称 Linux 已可运行。
系统不会被脚本自动重启；没有创建开机自动任务。

本轮最终状态：官方内核包已下载，SHA-256 已保存，Authenticode 签名为有效的 Microsoft Corporation。
安装尝试返回 MSI 1603，日志的 LaunchConditions 提示
“This update only applies to machines with the Windows Subsytem for Linux”。
结合 Windows 功能启用时明确返回的重启要求，下一步必须先重启，再重新检查 WSL 和内核安装条件；
不能据此断言重启后所有兼容性问题均已解决。
精简诊断见 [kernel-install-diagnostic.json](records/windows-setup/kernel-install-diagnostic.json)。
详细 MSI 日志保留在本机并被 Git 忽略，避免把安装器收集的个人系统信息上传。

官方说明：[WSL 安装](https://learn.microsoft.com/en-us/windows/wsl/install)、
[手动安装及内核包](https://learn.microsoft.com/en-us/windows/wsl/install-manual)。
安装包、虚拟磁盘等大型文件位于被忽略的目录，不提交到课程仓库。

## 重启后的执行顺序

1. 核对 Hypervisor 状态、WSL 运行时与实际内核，确认 Windows 功能已生效。
   若内核包因待重启而未能安装，再安装已下载并验证签名的微软内核包。
2. 安装／导入独立的 Ubuntu 实验发行版，记录版本；优先对齐 Ubuntu 18.04，
   或在经过验证的宿主 Linux 上使用 Ubuntu 18.04 容器。路线尚未确定，不宣称已兼容。
3. 在 Linux 文件系统内建立实验目录，从本机现有 Git 对象重新检出固定源码。
   Windows 工作副本受换行转换影响，build.sh 当前为 CRLF，而 Git 中原始文件为 LF；
   不直接把 Windows 工作副本当作可运行的 Linux 脚本。
4. 以实际实验权限运行 Linux 调度探测脚本，记录内核、CPU 亲和性、errno 和恢复结果。
   请求失败时先区分权限、内核和资源限制，不能直接判定机器硬件不适用。
5. 探测通过后，选择原作者 Docker 镜像或固定源码构建路线；记录实际镜像摘要或依赖、补丁。
   镜像内源码版本也需核对，不因标签名为 stable 就默认等于本仓库固定 commit。
6. 编译 doubleFree，运行受控调度并保存诊断，重放失败调度。
7. 最小示例能解释后，再运行一个正式 evaluation 用例，独立重复三次，估算耗时和波动。
   若需要确认并行优势，还需验证 Serial；安装示例不能替代该基线。

## 小实验的通过标准

- Linux 和工具版本可记录，所需调度权限可实际使用。
- 编译成功，运行日志未出现被忽略的调度初始化错误。
- 缺陷由明确诊断及失败调度支持，可重放；非零退出或超时本身不代表检出。
- 三次独立尝试都有日志，包含失败，指标可解释且耗时可接受。
- 能根据这些证据分别判断安装可用性和小规模实验适用性。

当前没有编译 PERIOD、没有运行 doubleFree，也没有收集正式研究观测值。
尚不能判断本机已具备完成全部复现和拓展实验的条件。
