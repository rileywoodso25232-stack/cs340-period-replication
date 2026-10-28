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
- doubleFree：6 个调度、4 个失败调度、0 超时，ASAN 重放确认。
- reorder_3：三次独立预实验均为 27 个调度、6 个失败调度、0 超时，首轮失败重放确认断言失败。
- 解决 CRLF 脚本错误；保留修改清单、版本及真实观测。试错临时文件留本机归档，提交整理后的最终说明。
- 下一步：固定研究范围并验证 Serial；本轮不作为正式论文结果。
- 提交与推送：本条在提交前编写，尚无本次提交链接；由 GitHub Desktop 实际提交和推送后补充。
