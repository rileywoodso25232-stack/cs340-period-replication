# 安装验证（冒烟测试）

## 已完成的验证与结果归属

- 吴明阳（1240014957）：在 WSL2 + Docker 环境成功重放 doubleFree 失败调度，ASAN 确认 double-free。见 [Docker 环境材料](https://github.com/rileywoodso25232-stack/cs340-period-replication/blob/main/environment/setup-evidence/README.md)。
- 刘竞辰（1240013942）：在 WSL2 内直接构建环境完成 doubleFree 搜索与重放，补充 reorder_3 三次独立预实验及首轮失败重放。见 [WSL2 环境材料](../../environment/LOCAL_SETUP_STATUS.zh-CN.md)。

两人的 doubleFree 记录属于不同环境下的独立验证，不计为新增缺陷，也不合并统计为同一环境的重复次数。
以下调度数、耗时及重放结果属于刘竞辰本机 2026-10-28 的预实验，原始日志位于 `results/raw/local-smoke-20261028/`；不代表正式论文复现完成。

- doubleFree：深度 3，6 个调度，4 个 double-free 失败调度，0 超时；一次保存调度重放出现明确 ASAN double-free 诊断。
- 基准用例 reorder_3（本轮仅作预实验）：深度 3、最多 1000 个调度、外层时限 120 秒，三个独立目录各运行一次；每次 27 个调度、6 个失败调度、0 超时。首轮保存调度重放出现 `reorder_bad.c:80` 的预期断言失败。
- 工具报告三轮耗时为 4.18727、2.11832、2.15469 秒，均值 2.82009 秒、样本标准差 1.18415 秒。仅为预实验描述，未控制后台负载，不解释为论文性能对比。
- 搜索驱动和重放驱动退出码均为 0；驱动退出码不代表目标没有缺陷，缺陷判断依赖重放中的 ASAN/断言诊断。
- reorder_3 的 build.sh、cleanDIR.sh 在 Linux 副本转换为 LF 后编译成功；未修改算法。两类示例均保留二进制哈希，原始二进制在 Linux 独立运行目录。
- 验证支持本机开展当前小规模用例。尚未验证 Serial 基线、更大用例或严格调度一致性，不代表全部论文实验可行。

固定版本的上游源码包含 `test/doubleFree/` 示例。
从上游源码根目录开始执行：

```sh
source tool/init_env.sh
cd test/doubleFree
./cleanDIR.sh
./build.sh
"$ROOT_DIR/tool/DBDS/run_PDS.py" -y -d 3 ./df
```

上游 README 对该示例的演示结果是：深度为 3 时测试了 6 个调度，
其中 4 个调度触发失败。这是安装参考，不是本组实测结果。
多个失败调度可能对应同一个缺陷。

保存标准输出／标准错误、退出状态、运行命令、环境以及生成的调度文件。
使用上游命令 `run_PDS.py -r <saved-file> ./df` 重放已保存的失败调度。
将需要引用的小型日志复制到 `results/raw/`，大型输出不要提交到 Git。
在运行正式测试用例前，先记录与参考结果的差异或安装失败情况。

下一步：在已验证 reorder_3 的基础上，固定正式用例范围并验证 Serial 基线，
再确定实际的主实验配置。安装验证通过本身不能证明论文的研究主张成立。
