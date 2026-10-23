# CS340：PERIOD 论文复现

本仓库用于小组复现 Cheng Wen 等人在 ICSE 2022 发表的论文
**Controlled Concurrency Testing via Periodical Scheduling**（基于周期调度的受控并发测试）。

**当前状态：仓库骨架已建立，尚未收集复现实验结果。**
选题暂定为该论文；上游运行环境、安装验证、基线方法和最终测试用例仍需确认。

- 论文：https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf
- 原作者实现：https://github.com/wcventure/PERIOD
- 固定的上游起始提交：`cb8deb9a176e5bb292d70d46557dd61dc0e98069`
- 小组仓库：https://github.com/rileywoodso25232-stack/cs340-period-replication
- 初次使用 GitHub，请先阅读[中文上手指南](GETTING_STARTED.zh-CN.md)。

## 复现范围

计划缩小实验规模，复现论文表 1 和表 2 中选定的部分行。测量指标包括：
首次发现缺陷所需的调度数量、总调度数量、触发缺陷的调度数量；实际运行耗时另行记录。
最终用例子集应覆盖不同缺陷类型和线程数量，并在正式收集数据前完成选择与记录。

计划将直接运行程序（Native）作为本地基线。Serial 等其他基线仍需检查是否可用。
在相同或可比设置下完成实验之前，不能得出 PERIOD 优于其他方法的结论。
具体研究主张见[复现主张清单](docs/claims.md)。

## 目录说明

```text
config/                 固定的上游版本信息与实验配置草案
docs/                   研究主张、分工、计划、环境、偏差记录与分析
environment/            实际环境记录与环境搭建说明
experiments/smoke/      安装验证流程
experiments/baseline/   主要复现与基线对比实验方案
experiments/extension/  单因素扩展实验方案
scripts/                源码获取、环境采集、仓库检查与统计脚本
src/                    小组自行编写的适配代码与插桩代码（按需添加）
third_party/            本地下载的上游源码，不纳入小组 Git 历史
licenses/               保留的 PERIOD 原始许可证
results/raw/            原始测量数据与被直接引用的小型运行日志
results/processed/      重新计算的统计结果与论文／本组结果对比表
results/figures/        根据处理后数据生成的图表
report/                 英文报告提纲与参考文献
presentation/           展示计划，等待老师提供单独的展示要求
.github/                任务和合并请求模板
```

## 仓库辅助脚本

辅助脚本使用 **Python 3.10 及以上版本和标准库**；获取源码还需要 Git。
这些是运行仓库辅助工具的要求，并不代表 PERIOD 实验环境已经验证完成。
在仓库根目录执行：

```sh
python scripts/check_repository.py
python scripts/capture_environment.py
python scripts/fetch_upstream.py
```

预期输出如下：

- 仓库检查：报告文件缺失、配置错误或文件过大的问题。
- 环境采集：在 `environment/records/` 中生成带时间戳的 JSON 记录。
- 源码获取：在 `third_party/PERIOD/` 中检出指定的上游提交。

获取源码需要联网，所需时间取决于下载速度，目前没有实测耗时。
此步骤不会安装 LLVM、编译 PERIOD 或运行测试用例。
上游代码的来源说明见[第三方代码声明](THIRD_PARTY_NOTICES.md)。

## PERIOD 环境搭建与安装验证

尽量选择接近原作者实验条件的 Linux 环境。先按[环境搭建说明](environment/README.md)配置，
再执行[安装验证流程](experiments/smoke/README.md)。
仅使用 Docker 不能固定宿主机内核；还需记录宿主机／虚拟机内核和容器镜像摘要。

搭建过程中必须实际验证编译、运行命令，并记录耗时。
当前仓库骨架尚不能证明研究工具可以在全新机器上一键复现。

## 测量与分析

1. 在 `config/` 中固定用例、运行模式、预算、重复次数及错误判定标准。
2. 按[主实验方案](experiments/baseline/README.md)执行。
3. 为每次测量保留原始日志和对应的环境记录。
4. 将真实测量值追加到 `results/raw/measurements.csv`。
5. 执行 `python scripts/summarize.py` 计算统计结果。
6. 填写 `results/processed/paper_vs_ours.csv`，并完成[差异分析表](docs/analysis.md)。

统计脚本要求每组至少包含三次独立运行，输出为 `results/processed/summary.csv`。
初始数据为空时，脚本会明确提示没有数据并退出；研究数据中不混入示例观测值。

## 小组协作与提交

请阅读[协作规范](CONTRIBUTING.md)。每位成员使用自己的 GitHub 账号贡献代码与文档。
每条项目提交信息（包括合并提交）都应包含实际提交者的学号和全名。
每周日 23:59 老师检查之前，需将本周的实质进展推送到 GitHub；之后补推不能补回错过的周记录。

在[成员贡献表](docs/team.md)、[每周工作记录](docs/weekly-log.md)和[项目计划](docs/project-plan.md)
中记录实际工作。最终报告使用英文，以 PDF 提交，并包含贡献说明和 AI 使用声明。
最终交付时，为完成的版本创建 `v1.0` 标签。

报告、展示和 Git 历史分别评分。老师尚未提供详细的展示要求。

## 许可证

小组自行编写的仓库骨架文件采用 [MIT 许可证](LICENSE)。
PERIOD 保留其[原始许可证](licenses/PERIOD-MIT.txt)。
