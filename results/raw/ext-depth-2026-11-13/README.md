# 扩展实验:深度上限 -d 对 PERIOD 的影响(2026-11-13,吴明阳)

- 唯一变量:run_PDS.py 的 -d,取 1/2/3/4/5;其他不变(同一 Docker 环境、三个 CVE、每个设置 3 轮)
- 汇总:各 CVE 目录下 summary.txt;脚本:/workdir/runs/run_depth.sh
- 结果:三个缺陷深度均为 2;-d 1 均未找到;首次发现位置不随 -d 变化;-d 3 起总调度饱和(7911: 19,9806: 42,15265: 96)
- 试运行崩溃(Dry Run 阶段 ASan 报错,run_PDS 中止,未进入正式测试):cve-2016-7911/d5/run3、cve-2017-15265/d2/run3,分别以 run4 替代,见 NOTE.txt
- 偶发额外报错(CVE-2017-15265):d5/run3 第 50 个调度、d2/run4 第 9 个调度报 heap-use-after-free;同一调度在其他轮次的线程顺序相同但未报错;单独重放各 10 次均未复现(replay50-*.log、replay9-*.log);对照组第 11 个调度重放 5 次均复现(replay11-control-*.log)
