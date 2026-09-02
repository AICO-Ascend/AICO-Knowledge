# 在线权重重切分（Resharding）特性说明

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/resharding.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/resharding.md

# mindspeed-rl · Resharding 特性文档深度解读

---

## 【定位】

本文档系统阐述 mindspeed-rl 在 RL 后训练场景下"训练-推理共卡部署"所必需的**在线权重重切分（Resharding）** 能力——即在 Actor 模型既参与推理（vLLM 引擎）又参与训练（Megatron 引擎）的同一张昇腾卡上，通过 ShardingManager 在训练态与推理态之间动态切换模型权重的并行切分形状、调度参数内存，使得两个阶段可独立配置各自最优的并行策略而无需在显存中长期保留多份模型权重。

---

## 【技术要点】

1. **训推共卡后训练的引擎异构性**：训练阶段采用 Megatron 格式（带优化器、梯度管理），推理阶段采用 vLLM 引擎加速；Actor 模型在两种引擎间反复切换，权重形态需随之变化。
2. **统一接口层 ActorHybridWorker**：由 `TrainEngine`（训练引擎）、`InferenceEngine`（推理引擎）、`ShardingManager`（训推切换管理器）三部分构成，控制节点只需通过该类统一封装即可完成算法编排与资源调度。
3. **三大解耦子模块**：
   - **ShardingManager**：训转推 / 推转训的统一入口，承担权重重切分与内存调度，与具体引擎解耦（支持 Megatron、vLLM 及其他）；
   - **WeightContainer**：根据训练/推理并行策略完成权重重切分；
   - **WeightAdaptor**：Megatron ↔ vLLM 权重格式转换接口，通过实现不同 WeightAdaptor 即可支持新模型/新训推引擎。
4. **训推内存 0 冗余切换方案**：基于"参数分桶"思想，由 ShardingManager 在初始化阶段按推理并行策略的 MetaInfo 预分配每个 PP Stage 的 MemoryBuffer（推理参数桶），推理态权重直接落桶、训练态权重全部卸载至 CPU，训练时反向加载，从而避免形状变化后训练 MemoryBuffer 中出现不可卸载的冗余空间。
5. **MegatronOffloader**：训练引擎侧的权重 / 优化器 / 梯度统一内存管理模块，可通过实现不同 Offloader 适配不同训练引擎。
6. **配置即启用**：用户只需在 `actor_config`（训练并行策略）与 `generate_config`（推理并行策略）中分别填写 TP / PP / EP，并通过 `offload_train_*` 系列开关控制推理时是否卸载训练态优化器/梯度/权重，即可自动启用 Resharding。

---

## 【关键机制与数据】

**工作原理（数据流四步切换流程，原文步骤）**：

- **步骤 (1) ShardingManager 初始化**：原文"根据推理并行策略切分或推理引擎提供的权重元信息（MetaInfo）分配每个 PP Stage 所需的 MemoryBuffer（推理参数桶）"。即推理参数桶的大小严格按推理引擎的权重元信息精确分配，本身不含冗余。
- **步骤 (2) 进入推理态**：原文"为每个 PP 申请推理参数桶内存，将训练态权重参数经过并行策略转换为推理态权重参数，并拷贝至推理参数桶中，同时，将训练态模型权重、优化器、梯度等全部卸载至 CPU 侧"。
- **步骤 (3) 进入训练态**：原文"从 CPU 侧加载并使用训练态参数据桶中的权重参数、优化器、梯度等，同时释放推理侧参数桶内存空间"。
- **步骤 (4) 回到推理态**：原文"完成训练态计算后，再次通过步骤（2）变为推理态进行计算"。

**关键设计取舍（原文表述）**：

- ShardingManager 仅接收已初始化的训练/推理引擎模型权重，**内部不进行权重初始化**，因此不耦合训练及推理引擎类型，可扩展至 Megatron、VLLM 之外的其他引擎。
- 当并行策略发生变化（如 TP、EP 变化）导致权重张量形状变化时，形状变化后的权重可能无法置于训练引擎所分配的**连续 MemoryBuffer** 中——这正是引入"分桶隔离 + 训练态装卸载"方案的根因。
- 训练 MemoryBuffer 与推理参数桶物理上相互隔离，推理参数桶"由于推理态 MemoryBuffer 尺寸分配是根据推理引擎的权重元信息分配的……不存在任何冗余内存"。

> 注：原文未提供具体的性能数据（吞吐、时延、显存占用数值），故此处不臆造。

---

## 【表格解读】

原文包含 1 张关键表格，已逐字还原如下：

| 并行策略变换（训练->推理） | 限制 |
| --- | --- |
| TP成倍增大或减小 | TP成倍增大要求 $DP_{train}\times TP_{train}>=TP_{infer}$ |
| PP转DP | 目前vLLM仅支持 $PP=1$ |
| EP成倍增大 | 需要通过TP、PP成倍减小增大DP |

**逐行解读**：

- **TP 成倍增大或减小**：表示 Resharding 支持 TP 维度按倍数缩放。注意原文明确写出"TP成倍增大要求 $DP_{train}\times TP_{train}>=TP_{infer}$"——其语义是：**推理侧单卡分到的总张量份数** 不能超过**训练侧全局张量分片总数**（$DP_{train}\times TP_{train}$），否则单卡无法凑出推理所需的完整 TP 份数。这是 Resharding 在 TP 放大方向上的硬性数学约束。
- **PP 转 DP**：把训练阶段的 PP 维拆分转换为推理阶段的 DP 维。原文给出明确工程约束：**vLLM 引擎目前仅支持 $PP=1$**，意味着推理态 pipeline 必须折叠为单层，所以 PP 转 DP 实质是把"层间拆分"折叠回"数据并行"。
- **EP 成倍增大**：支持推理侧专家并行度按倍数放大。原文指出其前置条件是"需要通过 TP、PP 成倍减小增大 DP"——即必须先通过减小 TP / PP 来放大 DP，留出数据并行维度余量，再据此放大 EP。这与表格第 1 行公式中的"总张量份数守恒"逻辑一脉相承。

---

## 【公式解读】

原文公式均以行内 LaTeX 形式出现，逐字保留：

**公式 1**：$DP_{train}\times TP_{train}>=TP_{infer}$

- $DP_{train}$：训练态的数据并行度（Data Parallel size）；
- $TP_{train}$：训练态的张量并行度（Tensor Parallel size）；
- $TP_{infer}$：推理态的张量并行度（Tensor Parallel size）；
- **作用与含义**：这是 Resharding 在"训练→推理 TP 成倍增大"方向上的合法性约束。左侧 $DP_{train}\times TP_{train}$ 表示训练态下"单张模型副本被切成的总张量分片数"（每个 DP 副本内部再切 TP 份）；右侧 $TP_{infer}$ 是推理态每卡需要承载的 TP 份数。该不等式保证训练侧拆出的最小粒度能够被推理侧重新组合——若 TP 放得过大以致推理 TP 份数超过训练可提供的总份数，则无法完成无损重切。

**公式 2**：$PP=1$

- $PP$：Pipeline Parallel size（流水线并行度）；
- **作用与含义**：限定 vLLM 推理引擎在当前实现下**仅支持单流水线阶段（$PP=1$）**，因此训推切换时若要把 PP 维重切为 DP 维，需先保证推理态 $PP=1$。

> 原文无其他公式（如性能估算公式、重切分张量变换公式等）。

---

## 【关联】

根据原文出现的引用与上下文，本特性与以下模块/文档存在上下游关系：

- **全共卡部署（integrated_worker）**：原文"当前框架默认采用训推全共卡式部署（[全共卡部署](https://gitcode.com/Ascend/MindSpeed-RL/blob/master/docs/zh/features/integrated_worker.md)）"——Resharding 是全共卡部署模式下**默认启用**的能力前提，二者强绑定。
- **Megatron 训练引擎**：作为训练态模型权重、优化器、梯度、MegatronOffloader、Megatron MemoryBuffer 的承载方，是 ShardingManager 的"训侧"对接对象。
- **vLLM 推理引擎**：作为推理态承载方，是 ShardingManager 的"推侧"对接对象；其 $PP=1$ 约束直接决定了"PP 转 DP"功能的可用边界。
- **WeightAdaptor 抽象层**：承上启下，未来若要扩展到非 Megatron/非 vLLM 引擎或新模型，需通过新增 WeightAdaptor 实现，本文是该扩展点的设计依据。
- **Actor / Reference / Critic / Reward Model 角色**：在 RL 后训练全流程中，本文 Resharding 重点针对 Actor 的"训推并存"诉求，但同一架构亦隐含可复用于其他同时承担训推的模型角色。

> 原文文末内部链接字段标注为"无"，本节仅基于正文出现的引用进行关联梳理。

---

## 【使用方法】

**启用方式**：通过 YAML 配置 `actor_config` 与 `generate_config` 分别声明训练/推理并行策略即可**自动启用** Resharding，无需手动调用 API。

**配置项原文还原**：

```yaml
actor_config:
  tensor_model_parallel_size: 4     # 训练态 TP 切分
  pipeline_model_parallel_size: 2   # 训练态 PP 切分
  expert_model_parallel_size: 1     # 训练态 EP 切分


generate_config:
  infer_tensor_parallel_size: 2     # 推理态 TP 切分
  infer_pipeline_parallel_size: 1   # 推理态 PP 切分
  infer_expert_parallel_size: 1     # 推理态 EP 切分

  offload_train_optimizer: true     # 设置为 true 可以使能在推理时卸载训练态优化器
  offload_train_grad: true          # 设置为 true 可以使能在推理时卸载训练态梯度
  offload_train_param: true         # 设置为 true 可以使能在推理时卸载训练态权重
```

**参数语义说明**：

- `tensor_model_parallel_size / pipeline_model_parallel_size / expert_model_parallel_size`：训练态 TP / PP / EP 切分度。
- `infer_tensor_parallel_size / infer_pipeline_parallel_size / infer_expert_parallel_size`：推理态 TP / PP / EP 切分度；`infer_pipeline_parallel_size` 当前必须设为 `1`（与表格"PP转DP"限制一致）。
- `offload_train_optimizer / offload_train_grad / offload_train_param`：三个 CPU 卸载开关，分别控制进入推理态时是否将训练态的**优化器状态**、**梯度**、**模型权重**卸载到 CPU 侧。原文示例中三个开关均为 `true`，对应"训推内存 0 冗余切换"方案中"训练态参数全部卸载至 CPU"的标准姿态。

**已支持的转换能力（依据表格）**：TP 成倍增大或成倍减小、PP 转 DP、EP 成倍增大；其他组合（如非整数倍缩放、PP→PP 缩放等）原文未涉及。

## 图文联合解读

- `resharding_UML.png`: 图示UML类图：**ActorHybridWorker**聚合**TrainEngine**与**InferenceEngine**，通过**ShardingManager**协调训推切换；后者内部聚合**MegatronOffloader**（内存调度）、**WeightContainer**（PP间/内权重重切分）与**WeightAdaptor**（抽象基类，派生出**MegatronVLLMWeightAdaptor**和**MegatronMindIEWeightAdaptor**，实现权重格式转换）。

论证结论：系统通过解耦设计——ShardingManager与引擎解耦、WeightAdaptor抽象支持多种推理引擎——实现了训推共卡下权重在线重切分与内存统一调度。

与文档关系：UML精确落地文档"方案概述"中四模块（ShardingManager/WeightContainer/WeightAdaptor/MegatronOffloader）的职责划分，印证其"不耦合训推引擎类型"的解耦论点。
- `param_buckets.png`: **1) 图中内容：** 上半部展示不分桶方案——训练态权重在连续内存空间中排列，推理态因TP/EP变化致张量形状改变（MLP呈黄色不同形状），无法完全填回原连续空间，产生"无法offload"冗余；下半部展示分桶方案——训练态独立分配"训练内存Bucket"与"推理内存Bucket"，通过D2D copy与"训推转换Bucket"协作，推理态权重完整放入对应桶中，实现"可以整体offload"。

**2) 技术结论：** 论证了按tensor形状分桶的训推内存调度方案可彻底消除切换时的冗余内存空间。

**3) 与文档关系：** 直观印证文中"基于参数分桶的训推内存0冗余切换技术"的核心论点，支撑ShardingManager内存调度的设计合理性。
