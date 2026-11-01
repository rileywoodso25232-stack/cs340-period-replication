# 环境配置与验证

本组保留两套独立环境的验证材料，分别记录配置、证据和成员贡献。

## 吴明阳：WSL2 + Docker

已完成 Docker 环境配置，并成功重放 doubleFree 示例的一个失败调度，AddressSanitizer 报告 double-free。
详见 [Docker 环境材料](https://github.com/rileywoodso25232-stack/cs340-period-replication/blob/main/environment/setup-evidence/README.md)。其材料注明：尚未确认当前镜像是否由保存的 Dockerfile 构建，也未完成全新机器重建验证。

## 刘竞辰：WSL2 内直接构建

已完成工具链构建、SCHED_DEADLINE 独立探测、doubleFree 搜索与重放，以及 reorder_3 三次独立预实验和首轮失败调度重放。
详见 [WSL2 环境材料](LOCAL_SETUP_STATUS.zh-CN.md)，其中保留本机使用方法、新机器搭建边界和记录规则。

## 成果关系与验证范围

两人的 doubleFree 材料属于不同环境下的独立验证，不计为新增缺陷，也不能合并当作同一配置下的重复运行。
刘竞辰本分支另补充工具链构建与搜索日志、环境探测和排障记录，以及 reorder_3 三次预实验与首轮失败重放。
两套环境材料及原始证据均保留，具体配置、步骤和限制以各自说明为准。

当前成果用于环境验收与预实验；尚未完成 Serial 基线及正式论文结果对比。
Docker 材料目前链接到主分支的已存在文件，避免环境搭建分支缺少该目录时出现失效链接。
