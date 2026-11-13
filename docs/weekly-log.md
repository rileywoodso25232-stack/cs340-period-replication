# Weekly progress log

Record real work and the actual push/PR evidence. This file is not a substitute
for timely GitHub history, and it does not itself certify a passed weekly check.

## Initial setup - 2026-10-23

- Prepared a project layout, scoped claims, evidence templates and collaboration guide.
- Recorded a fixed upstream commit and preserved the original MIT license.
- Prepared helpers for environment capture, source retrieval and statistical summaries.
- AI assistance: scaffold preparation; see `docs/ai-usage.md`.
- Verification: repository structure/configuration/link checks and helper smoke checks passed;
  see `docs/scaffold-verification.md`. GitHub commits provide the push evidence.
- No PERIOD environment, benchmark run, reproduction result or extension is complete.

## Future entry template

- Week/check date:
- Member and actual work:
- Commit/PR links and push evidence:
- Measurements/checks completed:
- Failures, blockers and next work:

## 2026-10-28：环境配置与初步运行验收

- 成员：1240013942 刘竞辰；AI 辅助范围见 `docs/ai-usage.md`，组员复核待完成。
- 完成 Windows 组件修复、WSL2/Ubuntu 启动、固定版本工具链构建及 SCHED_DEADLINE 探测。
- 重复验证：刘竞辰在本机 WSL2 直接构建环境完成 doubleFree 搜索与重放：6 个调度、4 个失败调度、0 超时，ASAN 确认 double-free。与吴明阳 Docker 路线形成另一环境的验证证据，不计为新增缺陷。
- 新增预实验：reorder_3 三次独立运行均为 27 个调度、6 个失败调度、0 超时；首轮保存的失败调度重放确认预期断言失败。
- 补充产出：工具链构建日志、依赖版本、SCHED_DEADLINE 探测及 CRLF 换行修改记录。
- 解决 CRLF 脚本错误；保留修改清单、版本及真实观测。试错临时文件留本机归档，提交整理后的最终说明。
- 下一步：固定研究范围并验证 Serial；本轮不作为正式论文结果。
- 提交与推送：本条在提交前编写，尚无本次提交链接；由 GitHub Desktop 实际提交和推送后补充。

## 2026-11-01：明确分支贡献与材料归属

- 根据组员建议，核对主分支 Docker 环境说明和实际 ASAN 重放日志，区分两条环境路线与两位成员的贡献。
- 将环境 README 改为全组入口，将本机操作说明移入刘竞辰的环境记录；保留全部原始预实验数据，修正过时的“尚未验证”状态。
- 本次为文档澄清，没有新增实验，也没有合并或改写组员的材料。

## 2026-11-05：reorder_3 兼容候选驱动对照与失败重放

<!-- reorder3-compat-20261105 -->

- 执行成员：1240014957 吴明阳；容器命令由本人执行，AI 辅助及复核状态见 ai-usage.md。
- 排查旧串行驱动退出码 139；核验目标二进制 DWARF 布局，将双方独立副本的共享内存布局统一为 100/3964/uint16，原文件与失败记录保留。
- 在相同目标、深度参数、运行预算和超时配置下，交替执行双方各三轮：Serial 每轮 30 个调度、10 个失败调度、0 超时；PERIOD 每轮 27 个调度、6 个失败调度、0 超时。
- 双方各重放首轮第一条保存失败调度，均重现 reorder_bad.c:80 的断言，目标退出码 -6；重放驱动退出码均为 0。
- 修正汇总脚本未处理颜色控制码而误记 schedules=0 的问题；原始搜索日志未改变，未为汇总修正重跑实验，原表及修正表均保留。
- 入库材料保留日志、配置、失败调度、源码快照、补丁、许可证与哈希；二进制和缓存保留于完整本地备份。
- 结果及原始证据：[本轮说明](../results/raw/reorder3-compat-20261105/README.md)。
- 限制：本轮为单用例候选驱动验证；双方实际周期范围与初始化逻辑仍不同，不计算加速比，不宣称完整论文 Serial 基线或整体复现完成。多条失败调度不计为多个缺陷。
- 验证：本轮材料复制后仓库检查已通过；本条写入后应再次运行检查。组员独立复核待完成。
- 提交/PR/推送：待实际提交和推送后补充链接，本记录不作为已推送证据。

### 同日此前完成的预实验与 Native 补充对照

- Docker 单次验证：reorder_3 搜索 27 个调度、6 个失败调度、0 超时，保存失败调度并重放确认第 80 行断言。
- Native 补充对照：三组各 1000 次原生执行，均 0 断言、0 超时、0 其他运行错误；对应旧 PERIOD 三组各 27 个调度、6 个失败调度、0 超时。
- 后续发现旧 Python 驱动数组布局与目标运行时不一致，上述 PERIOD 数据留作历史预实验，不与修复后结果合并。Native 是本次自定义配置，未宣称复现论文全部基线。
- 证据：[Docker 预实验](../results/raw/docker-reorder3-20261105/README.md)、[Native 补充对照](../results/raw/reorder3-native-period-20261105/README.md)。
- 今日提交采用 GitHub 网页分批上传并创建同一个 PR；本地 Git 暂存状态不作为已上传证明。PR 链接待创建后补充。
- 
- ### 2026-11-07 后续更新

- 11 月 5 日的实验材料已通过 [PR #3](https://github.com/rileywoodso25232-stack/cs340-period-replication/pull/3) 合并至 `main`，罗力汗完成了 PR 审核。

## 2026-11-13：表 1 子集进展

- 吴明阳已将三个选定用例的 PERIOD 运行记录推送到实验分支，每个用例独立运行三次。
- 已更新根目录 README。统计汇总、论文原值对照和组员复核待完成。
