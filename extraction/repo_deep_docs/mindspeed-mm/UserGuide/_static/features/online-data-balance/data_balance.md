# Data balance

> 仓 `mindspeed-mm` · 路径 `UserGuide/_static/features/online-data-balance/data_balance.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/UserGuide/_static/features/online-data-balance/data_balance.md

# Data Balance 模块深度解读

## 【定位】
本文档描述 mindspeed-mm 中**在线数据负载均衡（Online Data Balance）** 能力：针对多模态模型因原生分辨率差异导致分布式训练中 DP（数据并行）间数据负载不均的问题，通过在线重排数据并结合 All2All 通信，实现 DP 间负载均衡，从而提升集群资源利用率。

---

## 【技术要点】

1. **问题域聚焦**：当前仅支持 **ViT（视觉编码器）部分**的负载均衡；LLM 部分尚未启用 packing 策略，文档明确"后续将支持 LLM 部分 packing"以实现整网资源利用率提升。
2. **主控类 `DataBalance`**：作为协调数据平衡流程的主类，需注入 5 个关键参数：`virtual_pipeline_model_parallel_size`（虚拟流水线并行度）、`model_config_path`（模型配置路径）、`sorting_algo_name`（排序算法名）、`len_model`（模型长度信息）、`train_data_iterator`（训练数据迭代器）。
3. **排序算法**：默认采用 `post_global_balancing_greedy_without_pad`（无 padding 的后置全局贪心均衡），文档指出"后续将支持更多排序算法"。
4. **异步隐藏延迟**：通过 `PrefetchMicroBatchIterator` 异步预取数据，将 I/O 与计算重叠以隐藏延迟。
5. **核心执行流程（7 步闭环）**：获取原始 GBS → DP 间数据长度获取 → 负载均衡索引重排 → ranktable mapping → All2All 数据分发 → 负载均衡迭代器构建 → 训练步骤；每轮迭代从步骤 B 重新开始。
6. **启用方式**：在 Qwen 2.5 Omni 模型训练命令中追加一行参数 `--use-data-balance` 即可开启。

---

## 【关键机制与数据】

### 工作原理（依据 2.2 节流程图与 2.2.1 节样例）

1. **触发与采集**：每个训练步骤开始时，从数据源拉取一个原始全局批次（GBS, Global Batch Size）。
2. **长度感知**：在 DP 间收集每条样本的长度信息（与原生分辨率相关）。
3. **索引重排**：调用排序算法对数据索引进行重排，使各 DP 接收到的样本总长度尽可能均衡——这是负载均衡的核心计算步骤。
4. **ranktable mapping**：将重排后的索引映射到具体 rank（通信拓扑），为下一步通信做准备。
5. **All2All 通信分发**：通过集合通信原语 All2All 将重排后的数据分片交换到目标 rank，完成数据"再分配"。
6. **迭代器构建**：依据已分发到本 rank 的数据构建负载均衡迭代器 `batch_generator`，供训练步骤消费。
7. **预取与计算重叠**：迭代器内部使用 `PrefetchMicroBatchIterator` 异步预取下一批数据，隐藏通信/准备开销。

> 原文 2.2.1 节以"紫色为初始状态，蓝色为目标状态"的示意图说明：通过"数据映射路径 + All2All 通信"实现数据从初始分布到均衡分布的重排布。

### 性能数据

> 原文："**训练速度**：计算负载均衡，缩短训练时间，**典型场景收益 5%+**。"

（原文仅给出"5%+ 训练速度收益"一个量化点，未提供绝对基准数值、测试硬件配置、batch size、模型规模等更详细信息——解读时不臆造。）

---

## 【表格解读】

原文 2.1 节给出关键组件表，逐字还原如下：

| 组件 | 说明 |
|------|------|
| **DataBalance 类** | 协调数据平衡流程的主类 |
| **排序算法** | 如 `post_global_balancing_greedy_without_pad`（后续将支持更多排序算法） |
| **PrefetchMicroBatchIterator** | 异步预取数据，隐藏延迟 |
| **辅助函数** | 数据分割、映射、重组和通信等功能 |

**逐行解读：**

- **DataBalance 类**：作为对外的主入口，封装了"采集长度 → 排序重排 → All2All 通信 → 构建迭代器"全流程，对应 `__init__` 与 `build_balanced_train_data_iterator` 两个核心 API（见 3.2 节）。
- **排序算法**：策略可插拔（通过 `sorting_algo_name` 参数传入），当前默认 `post_global_balancing_greedy_without_pad`，是一种"无 padding 的后置全局贪心"策略——意即通过贪心分配但不引入 padding 样本（即不靠"凑长度"打补丁），从而避免引入额外计算开销。
- **PrefetchMicroBatchIterator**：通过异步预取将数据准备与模型前反向/梯度更新在时间轴上重叠，缓解因 All2All 与索引重排带来的延迟——这是性能收益 5%+ 的关键工程手段之一。
- **辅助函数**：负责底层数据切分、ranktable 映射、数据重组与集合通信调用等细粒度操作，承载整个流程的可复用基础能力。

---

## 【公式解读】

原文无公式。

> 备注：流程图中的步骤以 mermaid `flowchart` 形式呈现，属于控制流描述而非数学公式；排序算法的具体数学表达（如贪心分配的目标函数/约束条件）原文未给出——故本节按要求标注"原文无公式"。

---

## 【关联】

### 与本特性上下游相关的能力

- **上游/输入侧**：
  - **多模态模型（ViT 图像编码器）**：本特性解决 ViT 部分的负载不均问题，依赖 ViT 的样本级长度信息（与原生分辨率直接相关）。
  - **Qwen 2.5 Omni 模型**：作为首个/代表性支持模型，使用方式以该模型训练命令为例（见 3.1 节）。
  - **模型配置 `model_config_path`**：排序算法需要读取模型配置信息，属于上游依赖。

- **并行维度**：
  - **数据并行（DP）**：本特性作用于 DP 间负载均衡，要求图像编码器 **DP 度 > 1**（见第 5 节最佳实践）。
  - **虚拟流水线并行（`virtual_pipeline_model_parallel_size`）**：作为 `DataBalance` 初始化的入参，需与整体并行策略保持一致。

- **下游/未来工作**：
  - **LLM 部分 packing 支持**：文档明确"后续将支持 LLM 部分 packing，结合当前 ViT 部分在线负载均衡方案，提升整网资源利用率"——即 LLM 侧的对齐策略是下一阶段目标，与本特性互补共同构成"整网均衡"。

- **集合通信依赖**：All2All 通信属于底层基础设施，依赖训练框架对集合通信原语的封装（具体后端库/HCCL 等原文未指明）。

---

## 【使用方法】

### 3.1 启用配置
在 Qwen 2.5 Omni 模型训练命令中追加命令行参数即可启用：

```bash
--use-data-balance
```

### 3.2 核心 API

#### 3.2.1 `DataBalance` 初始化

```python
from mindspeed_mm.utils.data_balance.data_balance import DataBalance

data_balancer = DataBalance(
    virtual_pipeline_model_parallel_size=args.virtual_pipeline_model_parallel_size,
    model_config_path=args.model_config_path,
    sorting_algo_name=args.sorting_algo_name,
    len_model=len_model,
    train_data_iterator=train_data_iterator
)
```

参数含义：
- `virtual_pipeline_model_parallel_size`：虚拟流水线并行度，需与整体并行配置一致。
- `model_config_path`：模型配置路径，用于排序算法读取模型信息。
- `sorting_algo_name`：排序算法名称，默认 `post_global_balancing_greedy_without_pad`。
- `len_model`：模型长度信息（用于长度感知阶段）。
- `train_data_iterator`：上游训练数据迭代器，提供原始 GBS。

#### 3.2.2 构建负载均衡数据迭代器

```python
batch_generator = data_balancer.build_balanced_train_data_iterator(
    is_vit_last_stage=is_vit_last_stage,
    max_batch_capacity=max_batch_capacity,
    micro_batch_size=micro_batch_size,
    num_microbatches=num_microbatches,
    data_type='image'
)

# 在训练循环中使用
for batch in batch_generator:
    # 训练步骤
    ...
```

参数含义：
- `is_vit_last_stage`：是否为 ViT 最后一个 stage，用于决定迭代器作用域。
- `max_batch_capacity`：单 micro-batch 最大容量上限。
- `micro_batch_size`：micro-batch 大小。
- `num_microbatches`：每 GBS 切分的 micro-batch 数。
- `data_type='image'`：当前限定为图像数据。

### 5. 最佳实践

- **算法选择**：默认使用 `post_global_balancing_greedy_without_pad`，无需特殊配置；后续将支持更多算法。
- **并行配置**：**确保图像编码器 DP 度 > 1**——这是负载均衡生效的硬性前提（DP 度 = 1 时不存在 DP 间不均问题，均衡无意义）。

## 图文联合解读

- `all2all.png`: ## 图文联合解读

**1) 图中内容：** 左侧（紫色）为初始GBS数据分配，Rank0-3持有数据量不均（2/3/2/3条）；中间展示经排序算法重排后的目标映射索引（Rank0:0,4,9；Rank1:1,5,8；Rank2:2,6；Rank3:3,7）；右侧（蓝色）为All2All通信后的最终分布，每列承载数据均衡对齐。

**2) 技术结论：** 通过排序算法计算最优映射，再借助All2All集合通信实现跨DP rank数据重排布，可消除因数据长度差异导致的负载倾斜。

**3) 与文档关系：** 对应文档2.2.1节"数据分发样例"，直观印证"紫色→蓝色"的负载均衡方案与"All2All数据分发"流程节点，支撑"提升资源利用率"的核心论点。
