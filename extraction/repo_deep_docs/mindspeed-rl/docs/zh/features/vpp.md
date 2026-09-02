# VPP/DPP

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/vpp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/vpp.md

【定位】
本篇文档系统介绍了昇腾强化学习加速库「mindspeed-rl」中数据并行（DP）与虚拟流水线并行（VPP）两种并行策略，阐明其背景动机、实现机制与启用配置，用于在不增加硬件的前提下提升大规模模型训练的并行效率与设备利用率。

【技术要点】
- 数据并行三要素：每设备持有完整模型副本、数据按 batch 切分并均匀分配、通过 AllReduce 进行梯度聚合与广播以维持全局参数一致。
- 多维并行分解公式：`data_parallel_size = world_size // (tensor_model_parallel_size × pipeline_model_parallel_size × context_parallel_size)`，且 `global_batch_size` 须能被 `data_parallel_size` 整除，模型总层数须能被 `pipeline_model_parallel_size` 整除。
- 典型混合并行示例：8 GPU 场景下，TP=4、PP=4、DP=2，将 TP+PP 单元复制到剩余 GPU。
- 虚拟流水线并行（VPP）核心权衡：在不增加设备数量的前提下将模型细分为更多阶段，以增加通信量为代价换取更低的空泡率。
- VPP 切片示例（原文）：num_layers=16、TP=1、PP=4、VPP=2 → 总阶段数 = 4×2 = 8，每阶段含 16/8 = 2 层；前向顺序为 Device 0→1→2→3→0→1→2→3。
- VPP 启用约束：`num_layers % N == 0` 且 `pipeline_model_parallel_size ≥ 2`，同时权重转换脚本中必须同步设置 `num_layers_per_virtual_pipeline_stage N`，以保证保存/加载时权重切分模式一致。

【关键机制与数据】
- 原文：数据并行的"模型复制 + 数据分割 + 梯度同步（AllReduce）"机制：每块 worker 完成前向计算得到局部梯度后，由 server GPU 聚合所有梯度并求均值，再广播回各设备，保证全局参数一致。
- 原文：Megatron 传统流水线并行仍存在"较高的空泡率"，VPP 通过"细分计算任务"来降低空泡比、提升训练效率。
- 原文：VPP 是"在不增加设备数量的前提下，将模型进一步细分为更多阶段，以增加通信量为代价，换取更低的空泡比率"。
- 原文：VPP 的工作流示例——模型 16 层被切成 8 段（Device 0 持 [1,2] 与 [9,10]；Device 1 持 [3,4] 与 [11,12]；Device 2 持 [5,6] 与 [13,14]；Device 3 持 [7,8] 与 [15,16]），前向在四设备间交替两轮。
- 原文（外部参考）：文档末尾给出 VPP 原始论文链接 https://people.eecs.berkeley.edu/~matei/papers/2021/sc_megatron_lm.pdf，作为方案出处。
- 注：文档未给出任何基准性能数字、吞吐或加速比数据。

【表格解读】
原文无表格。

【公式解读】

公式 1（数据并行维度分解）：
$$
\text{data\_parallel\_size} = \frac{\text{world\_size}}{\text{tensor\_model\_parallel\_size} \times \text{pipeline\_model\_parallel\_size} \times \text{context\_parallel\_size}}
$$

符号含义：
- `world_size`：参与并行训练的全部 NPU 总数（World Size）。
- `tensor_model_parallel_size`：模型权重在张量维度上的并行切分数。
- `pipeline_model_parallel_size`：模型架构在流水线维度上的切分数。
- `context_parallel_size`：针对长序列数据在序列维度上的并行切分数。
- `data_parallel_size`：推导出的数据并行维度数。
- 作用：将全部 NPU 在三维并行维度（TP/PP/CP）切分后，剩余的设备数即作为数据并行副本数。

公式 2（虚拟流水线并行阶段数计算）：
$$
\text{virtual\_pipeline\_model\_parallel\_size} = \frac{\text{num\_layers}}{\text{pipeline\_model\_parallel\_size} \times \text{num\_layers\_per\_virtual\_pipeline\_stage}}
$$

符号含义：
- `num_layers`：模型总层数。
- `pipeline_model_parallel_size`：流水线并行度（设备级阶段数）。
- `num_layers_per_virtual_pipeline_stage`：每个虚拟流水线阶段包含的层数（用户配置参数 N）。
- `virtual_pipeline_model_parallel_size`（vpp）：虚拟流水线阶段总数，等于"虚拟阶段细分倍数"。
- 作用：判定在给定 PP 与每虚拟阶段层数 N 后，模型被进一步拆成多少个虚拟阶段；亦等价于验证 `num_layers % N == 0` 与 `pipeline_model_parallel_size ≥ 2` 是否成立。

【关联】
文档末尾给出内部链接"（无）"，即本篇不显式引用仓内其他模块；但从内容可推知其与下列要素存在隐式耦合：
- 与「模型权重转换脚本」耦合：`tensor_model_parallel_size` 与 `pipeline_model_parallel_size` 必须在训练配置与模型转换配置之间保持一致；VPP 启用时还需在权重转换脚本中同步加入 `num_layers_per_virtual_pipeline_stage N`，否则会出现权重切分不匹配。
- 与「Megatron 流水线并行（PP）」耦合：VPP 是 PP 的细化增强，启用前提是 `pipeline_model_parallel_size ≥ 2`，因此本文必须先理解 PP 才能正确启用 VPP。
- 与「张量并行（TP）」与「长序列并行（CP）」耦合：通过公式 1 共享同一套设备资源分解，DP、TP、PP、CP 共同决定 `world_size` 的切分。
- 与「混合并行拓扑（TP+PP+DP）」耦合：文档图 1 给出 TP=4、PP=4、DP=2 共 8 GPU 的混合流水线示例，VPP 可进一步在该拓扑上叠加。

【使用方法】

数据并行（Data Parallelism）启用方式（在 actor 配置中）：
```yaml
actor_config:
   tensor_model_parallel_size: 4      ## 跟模型转换里面保持一致
   pipeline_model_parallel_size: 2    ## 跟模型转换里面保持一致
```
启用前置条件：`global_batch_size` 须能被推导出的 `data_parallel_size` 整除；模型总层数须能被 `pipeline_model_parallel_size` 整除。

虚拟流水线并行（VPP）启用方式：
- 在训练脚本的 `actor_config` 中添加参数 `num_layers_per_virtual_pipeline_stage  N`（N 表示每个虚拟流水线阶段的层数）。
- 同时在权重转换脚本中也加入 `num_layers_per_virtual_pipeline_stage  N`，以保证权重切分模式一致。
- 约束条件：`num_layers % N == 0` 且 `pipeline_model_parallel_size ≥ 2`。
- VPP 必须依赖流水线并行（PP）启用，无法单独开启。

原文未涉及的具体项：未给出 NPU `world_size`、`context_parallel_size` 的推荐数值，未给出命令行启动脚本示例，也未给出任何性能基准数据。

## 图文联合解读

- `dp.png`: **图文联合解读：**

1) **图示内容**：8张GPU横向排列，每卡含5层（如GPU0：Layer 0-4，GPU1：Layer 5-9，GPU2：Layer 10-14，GPU3：Layer 15-19）。GPU0-3与GPU4-7各自被虚线框标注为"Model"，两框结构完全一致；框内GPU间有箭头表示流水线数据流。

2) **技术结论**：该图展示了**3D混合并行**架构——组内GPU 0-3构成一个完整模型副本（TP=4张量并行切片 + PP=4流水线分段），GPU 4-7复制相同结构（DP=2数据并行），两组间通过AllReduce同步梯度。

3) **与文档关系**：图1直观验证了文档"典型的混合架构"论点，即DP+PP+TP协同：DP实现数据分片提升吞吐，PP切分模型降低单卡显存，TP进一步切分权重，三个维度共同解决大规模训练的可扩展性问题。
- `vpp.png`: **图文联合解读：**

**1) 图示内容**：横轴为时间，纵轴为Device 1~4，蓝色方块表示前向（Forward Pass），绿色为反向（Backward Pass），数字1~16为微批次；灰色块为空泡/热身区，呈现1F1B流水线调度时间线。

**2) 技术结论**：展示Megatron经典1F1B流水线调度——首尾存在明显空泡（Bubble），揭示标准PP在冷启动与收尾阶段设备利用率低的固有缺陷。

**3) 与文档关系**：作为"虚拟流水线并行（VPP）"小节的引出图，先暴露标准PP空泡率高的痛点，从而论证VPP通过拆分流水线阶段降低空泡、提升效率的必要性。
