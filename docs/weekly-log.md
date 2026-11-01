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
