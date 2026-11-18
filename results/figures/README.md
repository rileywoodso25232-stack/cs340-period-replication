# 结果图表

此目录存放根据处理后数据生成的图表。
每张图都应注明源 CSV、绘图脚本、单位、重复次数，以及误差或不确定性的表示方式。
重复测量结果优先使用误差条，调度数量与实际运行耗时应分别展示。

## 2026-11-18 生成的表一图表

- `table1-schedules.svg` / `.png`：三栏分别为首次触发、总调度、错误调度；
  柱为本地均值，误差条为样本标准差（n-1），虚线为论文值，柱下标明方法首字母与 n。
  数据源 `results/processed/summary.csv`；绘图脚本 `scripts/make_table1_figures.py`。
  Serial/CVE-2017-15265 未纳入，图中已注明。
- `table1-time.svg` / `.png`：工具耗时均值 ± 样本标准差，仅作描述；论文表一没有该指标，
  不同主机不可直接比较。
- 本机没有 matplotlib；SVG 由脚本用标准库生成，PNG 由 Edge headless 从同一 SVG 渲染，
  两者内容一致。图表中的“paper”值来自论文表一第 8 页 Period/Serial 合并列。
