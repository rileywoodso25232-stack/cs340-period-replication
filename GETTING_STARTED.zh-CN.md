# 小组仓库上手指南

当前阶段：已建立仓库骨架，尚未配置或验证 PERIOD 实验环境。

## 1. 邀请组员

仓库所有者进入 GitHub 仓库的 Settings，找到 Collaborators / Manage access，
通过 Add people 邀请另外三位同学；被邀请者需要登录自己的账号接受邀请。
成员名单填写在 `docs/team.md`。每人必须用自己的账号产生实质贡献。

## 2. 下载到自己的电脑

可安装 GitHub Desktop 并登录自己的账号，选择 File > Clone repository，
输入本仓库 URL。命令行用户可运行：

```sh
git clone https://github.com/rileywoodso25232-stack/cs340-period-replication.git
cd cs340-period-replication
```

如果已由助手准备好本地目录，请直接打开该目录，避免在目录里面再克隆一次。
首次提交完成并同步后，该目录应有 `origin` 远程地址。

## 3. 每次工作流程

1. 在 GitHub Desktop 点击 Fetch origin / Pull，更新本地。
2. 为自己的任务建立分支，例如 `docs/environment-notes`。
3. 修改并检查自己的文件。
4. 在 Summary 中填写 `学号 全名: 具体做了什么`，再 Commit。
5. Push origin；需要合并时创建 Pull Request，请另一位同学检查。
6. 合并产生的提交或 squash 提交，也要包含实际合并者的学号和全名。

提交信息示例：

```text
1240013942 刘竞辰: document PERIOD setup and repository layout
```

真实作者的 Git 邮箱应与其 GitHub 账号关联；不要四个人共用一个账号。
不使用伪造或倒填的提交补周进度。每周日 23:59 前确认实质修改已经 Push。

## 4. 文件放在哪里

| 内容 | 位置 |
| --- | --- |
| 分工、计划、每周实际工作 | `docs/` |
| 待验证的实验参数 | `config/` |
| 环境说明、真实机器环境记录 | `environment/` |
| 安装验证、主实验、扩展实验方案 | `experiments/` |
| 自己写的适配代码或上游补丁 | `src/` |
| 原始测量数据及小日志 | `results/raw/` |
| 统计结果和对比表 | `results/processed/` |
| 图表 | `results/figures/` |
| 英文报告、参考文献 | `report/` |
| 展示材料 | `presentation/` |

## 5. 现在的下一项工作

先补齐四人名单和分工，再确定 Linux 实验环境，按照
`environment/README.md` 和 `experiments/smoke/README.md` 验证安装。
Windows 可以用于日常协作；正式实验的 Linux 方案仍需选择并验证。

`third_party/PERIOD/` 由脚本按固定 commit 获取，不直接提交整套依赖。
不要把镜像、编译产物、大型 trace、凭据或超过 50 MB 的文件提交进仓库。
原始小日志需要保留，不能只留下截图。

课程文件要求最终使用 `v1.0` 标签；项目刚开始时不要提前创建该标签。
