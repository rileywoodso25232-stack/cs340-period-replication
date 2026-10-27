# PERIOD 环境搭建与安装验证材料

## 提交人
- 学号：1240014957
- 全名：吴明阳

## 完成情况
已完成 PERIOD 环境配置，并成功重放 doubleFree 示例的一个失败调度。
AddressSanitizer 报告 double-free，说明该调度可以再次触发重复释放错误。
本次材料用于环境与安装验证，不代表论文主实验已完成。

## 实际环境
- 运行方式：Docker，使用 WSL2 Linux 内核
- 容器系统：Ubuntu 18.04.6 LTS
- 内核：6.18.33.2-microsoft-standard-WSL2
- GCC：7.5.0
- Clang：10.0.0
- Python 3：3.6.9
- PERIOD 提交：cb8deb9a176e5bb292d70d46557dd61dc0e98069
- Docker 镜像名称：period:cb8deb9
- 本地镜像 ID：sha256:5ab9c6dec0438d00f35f21a02c127aeed628236c470cabf2fcbec453379f57a2
- 容器名称：period-cs340
- 特权模式：开启
- 挂载目录：无
- 容器内代码目录：/workdir/PERIOD

## 材料说明
以下链接以本说明文件所在目录为基准：

- [environment.txt](environment.txt)：系统、内核、代码提交和编译器版本记录。
- [Dockerfile.repro](Dockerfile.repro)：从容器代码目录中保存的搭建文件；尚未确认当前镜像是否由此文件构建。
- 重放日志位置：`results/raw/setup-smoke/replay.log`，相对于仓库根目录。
- 失败调度位置：`results/raw/setup-smoke/out_df_1/Errors/`，相对于仓库根目录。
- 测试日志及失败调度文件将另行上传；4 个失败调度不代表 4 种不同缺陷。
- 容器配置原始记录保留在本地备份中，本次未提交。

## 已验证的重放方法

以下步骤适用于本机已有容器，尚不是全新机器上的完整安装流程。

在 Windows PowerShell 中启动并进入已有容器：

```powershell
docker start -ai period-cs340
```

如果容器已在运行，可改用：

```powershell
docker exec -it period-cs340 /bin/bash
```

进入容器后依次执行：

```bash
cd /workdir/PERIOD
source tool/init_env.sh
cd test/doubleFree
"$ROOT_DIR/tool/DBDS/run_PDS.py" -r out_df_1/Errors/000001_0000003_double-free ./df
```

实际输出包含：

```text
ERROR: AddressSanitizer: attempting double-free
SUMMARY: AddressSanitizer: double-free
ABORTING
```

结论：保存的失败调度成功再次触发 double-free 错误。
ABORTING 表示测试程序检测到错误后终止。

## 当前限制与后续工作
- 尚未完成依据这份材料在全新机器上的构建验证。
- 尚未确认当前镜像是否由备份的 Dockerfile.repro 构建。
- 原始测试的完整控制台日志尚未收集；replay.log 是本次重新执行重放时保存的日志。
- 不能仅凭 4 个失败调度文件推断总调度数、不同缺陷数量或运行耗时。
- 后续需要补充正式实验配置、至少三次独立运行的数据、论文结果对比、差异分析及扩展实验。

## AI 使用说明
使用 ChatGPT 辅助整理操作命令、解释终端输出和编写材料说明。
环境配置及测试执行由本人实际操作，运行结果已核对。
