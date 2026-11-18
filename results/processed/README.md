# 处理后的结果

收集独立观测值后，运行 `python scripts/summarize.py` 生成 `summary.csv`。
脚本计算算术平均值和样本标准差（分母为 `n-1`），每组至少需要三次运行。
不得将不同实验设置的数据合并统计。

`paper_vs_ours.csv` 只能根据已核实的论文数值和本组生成的统计结果填写。
使用相同指标、单位及明确注明的设置；量化差距，标明原论文表格／图中的具体行或数据位置，
列出偏差，并关联控制变量实验的证据。只有表头的文件是模板，不是研究结果。

为区分 Period 与 Serial，本仓库的 `paper_vs_ours.csv` 在模板基础上增加了 `mode` 列；
`table1-paper-vs-ours.md` 是同一数据的可读表格，二者都由
`scripts/build_paper_vs_ours.py` 从 `summary.csv` 生成。

表二子集使用单独的文件：`table2-paper-vs-ours.csv` / `.md`，由
`scripts/build_table2_paper_vs_ours.py` 从表二证据目录的 `summary_by_case.csv` 生成；
对应的测量值已追加到 `results/raw/measurements.csv`（experiment_id 以
`local-table2-local-comparison` 开头）。
