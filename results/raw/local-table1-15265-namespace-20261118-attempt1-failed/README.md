# 15265 命名空间对照 attempt1（脚本失败，保留审计）

日期：2026-11-18。状态：脚本错误，未产生任何实验结论。

## 原因

首次运行 `scripts/linux/check_15265_replay_state.py` 时，生成的 shell 片段直接把
`observe_driver.py`/`run_PDS.py` 当成可执行程序启动，而不是 `python3 -u ...`，导致
`rc=126`（不可执行），搜索日志未生成；5 次试验均显示 `no_search_log`。

## 处理

- 修正脚本为显式 `python3 -u` 后重跑，正式结果在
  `../local-table1-15265-namespace-20261118/`；
- 本目录只作审计，不参与结论、不与正式结果合并；
- 共 70 份文件，约 0.57 MB。
