# 扩展实验:深度上限 -d 对 PERIOD 的影响(2026-11-13,吴明阳)

- 唯一变量:run_PDS.py 的 -d,取 1/2/3/4/5;其他不变(同一 Docker 环境、三个 CVE、每个设置 3 个有效轮次)
- 汇总:见本文件夹 SUMMARY.md(含均值 ± 样本标准差、计入和未计入统计的轮次);各 CVE 目录下 summary.txt 为脚本自动记录
- 脚本:本文件夹中的 run_depth.sh(在容器内 /workdir/runs/ 下运行);补跑和重放为手动执行,命令同脚本
- 结果:三个缺陷深度均为 2;-d 1 均未找到;首次发现位置总体不随 -d 变化(CVE-2017-15265 d2/run4 因额外报错提前到第 9 个调度,见 SUMMARY.md);-d 3 起总调度饱和(7911: 19,9806: 42,15265: 96)
- 试运行崩溃(Dry Run 阶段 ASan 报错,run_PDS 中止,未进入正式测试):cve-2016-7911/d5/run3、cve-2017-15265/d2/run3,不计入统计,分别以 run4 替代,见 NOTE.txt
- 偶发额外报错(CVE-2017-15265):d5/run3 第 50 个调度、d2/run4 第 9 个调度报 heap-use-after-free;这两轮正常完成,计入统计;同一调度在其他轮次的线程顺序相同但未报错;单独重放各 10 次均未复现(replay50-*.log、replay9-*.log);对照组第 11 个调度重放 5 次均复现(replay11-control-*.log)
- 详细方案与解释:experiments/extension/README.md
