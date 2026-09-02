# 开箱优化-大模型并行策略自动搜索 Auto settings 特性说明

> 仓 `mindspeed` · 路径 `docs/zh/features/auto_settings.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/auto_settings.md

# mindspeed · Auto settings 特性文档深度解读

## 【定位】
Auto settings 是针对大模型分布式训练中并行策略配置（DP/TP/PP/ZeRO/VPP/CP/EP/MBS/重计算等）"维度爆炸、人工调优困难"问题设计的**自动并行策略搜索特性**，其核心能力是**完全基于 profiling 数据建模（不依赖网络结构假设）并支持"以小仿大"**（用小集群 profiling 预估大集群较优配置），从而在千卡级训练场景下规避传统白盒/灰盒自动调优对模型结构敏感、profiling 开销与负载规模挂钩两大痛点。

---

## 【技术要点】

1. **三类搜索方案并行提供**：Auto settings 整体提供 **白盒搜索、黑盒搜索、混合搜索** 三种方案（通过 `--auto-settings-type {black, white, mixed}` 选择），用户可根据效率/精度需求在三者之间取舍。

2. **白盒搜索采用三阶段流水线建模**：
   - 阶段1：用少量机器 + **裁剪网络规模** + 生成多个 profiling 配置，自动多次拉起，产出供后续建模的原始数据；
   - 阶段2：对 profiling 结果做**内存**（各 tensor 在不同配置下的切分情况）和**性能**（算子增减、shape 变化、机内/机间通信效率、各候选重计算模块的性能与内存）双维度建模；
   - 阶段3：基于阶段2 建模 + **算子性能知识库** 做配置搜索。**最终推荐"内存充足 + 性能最好的三组配置"**。

3. **算子性能知识库 + 自适应二次 profiling 机制**：阶段3 会查询不同 shape 的算子性能，未覆盖的新算子被加入知识库；当某配置下知识库覆盖算子比例**小于阈值**时，会**额外拉起一组 profiling**，并通过"同时缩小网络规模和并行参数"以小仿大获得相同 shape 的算子；仍未覆盖的少量算子通过**回归**估算性能。

4. **"以小仿大"思想贯穿全流程**：原文明确给出 `--auto-settings-ranks` **最低 16 卡**的搜索门槛，配合 `--target-nnodes $NNODES`（与基线训练节点数保持一致），意味着可在大规模目标集群上、用 16 卡的小 profiling 推测更大规模训练的最优配置。

5. **黑盒搜索为"穷举 profiling"路线**：阶段1 与白盒相同（用于建模与搜索空间剪枝），**阶段2 对搜索空间内每个配置都执行 profiling**，实测获取内存与算子/通信耗时后选优。代价是 profiling 量随搜索空间膨胀，精度最高。

6. **混合搜索用 M→N→topk 串联两类方案**：阶段1 由白盒搜索圈定 **M 组候选**；阶段2 在其中选 **N 组**再用黑盒方案实测；最终输出 **top k 组**配置，兼顾白盒的效率与黑盒的精度。

---

## 【关键机制与数据】

### 工作原理与数据流（白盒方案为例）

```
[少量机器拉起] 
    → 裁剪网络 + 多 profiling 配置 → 自动多次拉起 profiling 
    → 解析结果文件, 提取 tensor 切分 / 算子 shape 变化 / 算子增减信息 
    ── 阶段1 结束 ──
[阶段2 建模] 
    → 内存侧: 分析各 tensor 在不同配置下的切分 
    → 性能侧: 推断算子增减与 shape 变化 + 回归机内/机间通信效率 
    → 重计算: 评估各候选模块的性能/内存影响 
    ── 阶段2 结束 ──
[阶段3 搜索] 
    → 算子性能知识库查询 + 新算子入库 + 覆盖率阈值触发二次 profiling (以小仿大) 
    → 未覆盖算子回归估算 
    → 输出"内存充足 + 性能最好"的 3 组配置
```

### 原文关键数字/事实汇总

- 原文：「白盒或灰盒的建模**对网络模型的结构进行了假设**……仅仅是 GQA/MQA 的修改，就会让此类建模的内存出现偏差」——说明对结构假设的敏感性是传统方法的核心缺陷。
- 原文：「**profiling 的规模和实际的负载规模相同**」——指出大规模训练下传统方法 profiling 开销随集群线性膨胀。
- 原文：白盒搜索**最终推荐 3 组**"内存充足 + 性能最好"的配置。
- 原文：白盒搜索阶段1 用"少量机器"，混合搜索阶段1 选 M 组、阶段2 选 N 组、最终输出 top k 组。
- 原文：`--auto-settings-ranks` **最低 16 卡**。
- 原文：算子性能知识库覆盖算子比例 **小于阈值** 时触发二次 profiling。
- 原文：二次 profiling 通过"同时缩小网络规模和并行参数"获得相同 shape 算子（"以小仿大"）。
- 原文：黑盒搜索阶段2 **对搜索空间每个配置都进行 profiling**。

### 已支持模型/特性覆盖（原文列表）

- **模型**：llama2-7b、mixtral-8×7b、gpt3-15b（3 个）
- **已支持特性（12 项）**：DP、TP、Megatron-SP、PP、ZeRO1、VPP、CP (ring attention)、EP (DeepSpeed-MOE)、MicroBatchSize、Token 重排、重计算、MC2
- **未来计划支持（5 项）**：ZeRO2、EP (Megatron-MOE)、swap-attention、激活函数重计算、MoE All2All overlap comm

---

## 【表格解读】

**原文无表格**（文档中所有信息均以有序/无序列表、命令块、复选框列表形式呈现，未出现 markdown 表格或其他结构化表格）。

---

## 【公式解读】

**原文无公式**（文档未给出任何 LaTeX 公式或伪代码数学表达式；其"建模"过程以文字描述阶段行为，未给出具体函数式表达）。

---

## 【关联】

文档**未提供内部链接**（文末内部链接信息标注为"无"），但根据原文上下文可识别出以下模块/特性关联：

1. **与并行策略栈的耦合关系**：Auto settings 调度的是底层一整套并行维度——**DP / TP / Megatron-SP / PP / ZeRO1 / VPP / CP(ring attention) / EP(DeepSpeed-MOE)**，并联动 **MicroBatchSize、Token 重排、重计算、MC2**。已支持的特性列表即为该特性实际能调优的参数空间，**ZeRO2、EP(Megatron-MOE)、swap-attention、激活函数重计算、MoE All2All overlap comm** 则明确标注为未来扩展项。

2. **与模型结构的解耦关系**：原文反复强调"**与网络结构的变化解耦**"，意味着该特性对 llama2-7b、mixtral-8×7b、gpt3-15b 等不同结构模型、以及 GQA/MQA 这类结构变体无须重写建模逻辑；这一解耦是通过"完全依赖 profiling 数据"而非"对结构建模"实现的。

3. **与算子性能知识库的关系**：白盒搜索阶段3 引入**算子性能知识库**作为查询底座，profiling 过程中**未见过的新算子会自动入库**；当覆盖率不足时触发二次 profiling，已覆盖算子直接查询、未覆盖算子回归估计，构成一个"持续积累的知识库 + 兜底回归"的闭环。

4. **与 profiling 子系统的关系**：Auto settings 依赖一个**隔离进程环境**中的 profiling 流程，通过 5 个 `OOTB_OPTIMIZER_*` 环境变量（详见下方"使用方法"）控制阶段性 profiling 的开关与参数文件路径，且**明确禁止**在正常训练流程中设置——说明 profiling 是 Auto settings 的内部子流程，对用户训练脚本完全透明。

5. **三方案之间的关系**：黑盒与白盒共享阶段1（剪枝/建模）；混合搜索显式组合两者——白盒输出 M → 黑盒二次精选 N → 给出 top k。三者并非互斥工具，而是同一条流水线的精度/效率滑条。

---

## 【使用方法】

### 启用方式（原文给出完整训练脚本参数）

在训练脚本参数列表中加入以下配置即可开启 Auto settings：

```bash
--auto-settings \                                 # 开启 Auto settings 特性
--auto-settings-type mixed \                      # 搜索方案，支持【black, white, mixed】三种
--auto-settings-work-dir ./auto_settings_dir \    # 工作目录，在此会保存 profiling 等文件
--auto-settings-ranks 16 \                        # 需要搜索的卡数，最低 16 卡
--auto-settings-log-level debug \                 # Auto settings log 记录等级，可选 warning, info, debug
--target-nnodes $NNODES \                         # Profiling 拉起的节点数，与基线训练脚本保持一致
--nproc-per-node $GPUS_PER_NODE \                 # 每个节点上运行的进程数，一般与单节点卡数相同，与基线训练脚本保持一致
--master-addr $MASTER_ADDR \                      # 主节点 IP，与基线训练脚本保持一致
--master-port 6005 \                              # 主节点端口，设置一个与基线脚本不同的端口
--node-rank $NODE_RANK \                          # 与基线训练脚本保持一致
```

> 关键约束（原文明确）：`--auto-settings-ranks` **最低 16 卡**；`--master-port` 应**与基线脚本不同**以避免端口冲突；其余网络拓扑相关参数须与基线训练脚本保持一致。

### Auto settings 内部专用环境变量（原文列出，**禁止**在正常训练中设置）

| 环境变量 | 作用 |
|---|---|
| `OOTB_OPTIMIZER_MODIFIED_ARGV_PATH=${WORK_DIR}/auto_settings_modified_argv.json` | 修改 Profiling 拉起配置参数的文件位置 |
| `OOTB_OPTIMIZER_PARSE_ARGS=TRUE` | 获取硬件相关信息及模型参数 |
| `OOTB_OPTIMIZER_PARSE_MODEL=TRUE` | 获取模型结构 |
| `OOTB_OPTIMIZER_PROFILING=TRUE` | 获取完整 Profiling 信息及自适应重计算 Profiling 信息 |
| `OOTB_OPTIMIZER_PROFILING_BLACK=TRUE` | 获取完整 Profiling 信息及自适应重计算 Profiling 信息，用于黑盒搜索的场景 |

> 原文强调：上述环境变量**仅为 Auto settings 内部使用**，**禁止**在正常训练流程中设置；Auto settings 会在一个**隔离的进程环境**中设置它们，**不会 export 至用户环境**。
