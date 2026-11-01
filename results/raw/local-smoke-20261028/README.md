# 本机小实验记录（2026-10-28）

这些记录用于验收环境，不计入正式论文结果。汇总见 `summary.json`。

- 固定源码：cb8deb9a176e5bb292d70d46557dd61dc0e98069；环境见 environment/LOCAL_SETUP_STATUS.zh-CN.md。
- Linux 目录时间戳为 UTC，北京时间加 8 小时。
- doubleFree 命令：`timeout --kill-after=10s 120s python3 "$ROOT_DIR/tool/DBDS/run_PDS.py" -y -d 3 ./df`。
- reorder_3 命令：`timeout --kill-after=10s 120s python3 "$ROOT_DIR/tool/DBDS/run_PDS.py" -y -d 3 -f 1000 ./reorder_3_bad`，三个独立目录顺序执行。
- 重放命令：`timeout --kill-after=10s 60s python3 "$ROOT_DIR/tool/DBDS/run_PDS.py" -y -r <保存的Errors文件> <目标程序>`。
- search/replay.log 是原始输出；对应 .exit 是驱动退出码。目标失败诊断见日志，不能用驱动退出码判断无缺陷。
- out_*/Errors 中是真实保存的失败调度，是必要重放输入，须随日志提交；无需提交 Linux 二进制。
- 一次 doubleFree 和三次 reorder_3 均保留。没有删去较慢的首轮，没有将失败调度伪装成独立缺陷。
