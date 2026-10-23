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

以下以 Windows 上的 GitHub Desktop 为例，界面名称可能随版本略有变化。
“仓库根目录”指电脑上的 `cs340-period-replication` 文件夹，里面有 `README.md`。

### 3.1 先分清几个动作

| 动作 | 实际作用 | 组员能否看到 |
| --- | --- | --- |
| 保存（编辑器中的 Ctrl+S） | 将修改写入电脑上的文件 | 否 |
| Commit（提交） | 在本地 Git 历史中记录一次修改 | 否 |
| Publish branch / Push origin（发布分支／推送） | 把本地分支和提交上传到 GitHub | 能，但通常还在任务分支上 |
| Pull Request，简称 PR（合并请求） | 请求组员检查并将任务分支并入主分支 | 能审阅，但尚未合并 |
| Merge（合并） | 将审核通过的修改并入主分支 `main` | 能，主分支已包含修改 |
| Fetch origin（检查远端更新） | 检查 GitHub 上有没有新提交 | 不会自动更新正在编辑的文件 |
| Pull origin（拉取） | 将远端当前分支的更新整合到本地 | 让本地版本跟上远端 |

**保存后还要 Commit，Commit 后还要 Push；Push 任务分支不等于合并到 main。**
`main` 汇总小组确认过的成果；任务分支用于独立完成一项修改。
切换分支会切换本地文件内容，不会复制出另一个文件夹。

### 3.2 开工前：确认账号、仓库和修改状态

1. 打开 Desktop，确认左上角 **Current Repository** 是 `cs340-period-replication`。
2. 首次使用时，在 **File > Options > Accounts** 确认登录的是自己的 GitHub 账号；
   在 **Git** 设置中确认自己的姓名和邮箱。邮箱应关联到自己的 GitHub 账号，
   也可以使用 GitHub 提供给自己的隐私邮箱。不要使用组员的身份。
3. 查看 **Changes**。若有上次未提交的修改，先确认它们属于哪个任务。
   属于当前任务分支的，就先检查并提交在该分支上。
   如果误改在 `main`，先创建任务分支；若提示如何处理修改，选择带到新分支。
   不要为了切换分支点击 **Discard changes**，那会丢弃修改。

Git 设置决定提交的作者身份；Summary 中写学号和全名是另一项课程要求，两者都要正确。

### 3.3 新任务：更新 main，再建立自己的分支

1. 点击顶部 **Current Branch**，切换到 `main`。
2. 点击 **Fetch origin**。若随后出现 **Pull origin**，再点击它，
   将其他组员已合并的成果下载到本地；没有出现则表示当前无需拉取。
3. 点击 **Current Branch > New Branch**，确认从更新后的 `main` 创建新分支。
4. 输入能说明任务的名称，例如 `docs/1240013942-environment-notes`，
   点击 **Create Branch**。其他同学将示例学号换成自己的。
5. 确认顶部显示的是刚建立的分支，再开始编辑。

**继续旧任务时**：切回原来尚未合并的任务分支，检查远端更新并按需拉取，
不必每天重新建分支。在任务分支上 Pull 只拉取该分支的远端更新，
不会自动将 `main` 的新内容合入任务分支。

### 3.4 编辑文件，检查实际改动

1. 在 Desktop 中选择 **Repository > Show in Explorer** 打开本地仓库，
   用编辑器打开要修改的文件。不要编辑下载到其他位置的旧副本。
2. 编辑后按 **Ctrl+S** 保存。
3. 回到 **Changes**，逐个点击文件查看差异：通常绿色表示新增，红色表示删除。
4. 勾选本次需要提交的文件，检查是否混入无关修改。
   不要提交凭据、镜像或编译产物。未勾选的修改仍留在本地，不会随本次提交上传。
5. 做与改动相符的检查：文档检查文字、链接和命令；代码或实验修改执行对应检查，
   并记录实际结果。

已安装 Python 的同学可在仓库根目录运行：

```sh
python scripts/check_repository.py
```

此命令只检查仓库结构等基础问题，不会运行 PERIOD 实验。
没有运行过的检查，不能在提交或 PR 中写成“已通过”。

### 3.5 Commit：在本地记录一次修改

在 Desktop 左下角 **Summary** 中按下面的格式填写提交标题：

```text
学号 全名: 具体做了什么
```

例如，刘竞辰本人的提交可以写：

```text
1240013942 刘竞辰: 补充 Linux 环境搭建步骤与待验证项
```

其他组员必须填写自己的学号和全名，不要直接复制示例身份。
不要只写“更新”“修改”。**Description** 可补充修改原因、检查结果和未完成事项。

点击 **Commit to 分支名**。此时只记录在自己的电脑上，组员还看不到。
一个任务可以有多次内容明确的提交，不必攒到全部完成才提交。
已提交的改动会从 Changes 列表消失，可以在 **History** 查看记录。

### 3.6 Push：上传到 GitHub

新分支第一次上传时，点击 **Publish branch**；
已经发布过的分支，点击 **Push origin**。

等待上传成功，点击 **Repository > View on GitHub**，
在网页的分支选择器中切换到自己的任务分支，确认能看到刚才的文件和提交。
如果网页仍停留在 `main`，看不到任务分支上的修改是正常的。

**每周日 23:59 前，确认本周实质修改已经推送到 GitHub。**
仅保存或仅 Commit 都不够。任务尚未完成也可推送已有的真实进展，
并在 `docs/weekly-log.md` 中如实记录。
不要用无意义提交或伪造、倒填时间补周进度。
每周推送和 PR 合并是不同动作，不必为了结束当天工作而仓促合并。

### 3.7 PR：请组员检查，再合并

1. 在 Desktop 中选择 **Preview Pull Request / Create Pull Request**，
   或在 GitHub 仓库网页选择 **Pull requests > New pull request**。
2. 确认 **base** 为 `main`，**compare** 为自己的任务分支，
   即“把我的任务分支合并进主分支”。
3. 填写清楚的标题，按 PR 模板说明修改内容、原因、实际做过的检查和未验证事项。
4. 创建 PR，在 **Reviewers** 中选择另一位组员审阅。
   审阅者在 **Files changed** 中检查差异，有问题就在 PR 中讨论。
5. 若需要修改，继续在原任务分支编辑、Commit、Push；
   新提交会自动加入同一个 PR，不需要每次新建 PR。
6. 检查通过后，由负责合并的同学点击 **Merge pull request**。
   优先使用普通合并，保留每位成员的原始提交记录。
   在最终确认前，编辑合并提交信息，加入**实际合并者自己的学号和全名**，
   例如 `学号 全名: 合并环境说明更新`。
   如选择 squash 合并，生成的提交同样需要正确署名；
   它会压缩原始提交，使用前应与相关成员确认贡献记录如何保留。

如果提示冲突（conflict），先暂停合并，与涉及同一文件的组员确认应保留的内容。
不要只为消除提示就整段删除另一人的修改，也不要强制推送覆盖别人的提交。

### 3.8 合并后：同步 main

1. 回到 Desktop，确认没有未处理的本地修改。
2. 切换到 `main`，点击 **Fetch origin**，有 **Pull origin** 时再点击。
3. 打开本地文件，确认刚合并的内容已经出现。
4. 下一项任务从更新后的 `main` 创建新分支。
   已合并且没有额外未推送修改的旧任务分支，可以确认后删除；保留也不影响继续工作。

当天尚未达到合并阶段时，完成检查、Commit、Push 并记录进度即可，
下次继续同一任务分支。

### 3.9 一个完整例子

以“刘竞辰补充环境说明”为例：

1. 在 `main` 上 Fetch，必要时 Pull。
2. 建立 `docs/1240013942-environment-notes` 分支。
3. 修改 `environment/README.md` 并保存，在 Changes 中检查差异。
4. 使用自己的学号和全名填写 Summary，再 Commit。
5. Publish branch 或 Push origin，在网页切到该分支确认上传成功。
6. 创建目标为 `main` 的 PR，请另一位组员检查，按反馈修改并推送。
7. 审核通过后合并，合并者填写自己的署名。
8. 每位组员下一次开始新任务前，都在自己的电脑上更新 `main`。

### 3.10 常见问题

| 情况 | 先检查什么 |
| --- | --- |
| 编辑后 Changes 没有文件 | 是否保存；是否编辑了当前仓库的文件；内容是否真的发生变化 |
| Commit 后 Changes 空了 | 属于正常现象；到 History 查看提交，再确认是否已 Push |
| 只有 Fetch origin，没有 Push origin | 当前分支可能没有待推送提交；检查分支名称与 History |
| 网页看不到刚上传的修改 | 是否推送成功；网页是否切到正确的任务分支 |
| 推送被拒绝或没有权限 | 是否登录自己的账号并接受协作者邀请；若提示远端领先，先获取更新并处理冲突，不要强制覆盖 |
| 不知道冲突应保留哪一版 | 保留现场，与修改相关内容的组员核对后再解决 |

按钮操作可参考 [GitHub Desktop 官方提交与检查指南](https://docs.github.com/en/desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project-in-github-desktop)。

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
