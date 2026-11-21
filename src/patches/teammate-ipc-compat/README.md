# 复用组员的 IPC 兼容补丁

来源：吴明阳（1240014957）归档于 PR #3 的候选驱动差异。
固定小组仓库提交 `9287fe43e351c650e6d48311e9368062b07f07e6`，精确路径及 Git blob 见 [来源清单](provenance.json)。原实现版权与许可见 [LICENSE.txt](LICENSE.txt)。

- period.diff：修正数组容量，增加 ABI、IPC 附着和容量检查。
- serial.diff：另修正数组元素类型和访问偏移，保留候选搜索控制流。
- 2026-11-15 已通过 patch dry-run，并在独立 Linux 副本以 fuzz=0 实际应用；双方 reorder_3 搜索和失败重放通过，见[验收证据](../../../results/raw/local-ipc-validation-20261115/README.md)。provenance.json 的 status 保留导入时快照；原上游文件未改。
- 不直接覆盖上游；后续在独立副本应用并记录哈希。此补丁不自动证明 Serial 与论文完全对应，也不解决所有实验有效性问题。

复用者：刘竞辰（1240013942）；本次新增贡献为本机 DWARF 布局核验、补丁可应用性检查与交接清单，不将原补丁算作本人原创。
