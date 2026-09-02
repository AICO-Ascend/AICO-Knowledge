# Megatron数据并行

> 仓 `mindspeed` · 路径 `docs/zh/features/data-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/data-parallel.md

# Megatron数据并行 — 深度解读

## 【定位】
本文档系统性介绍了 Megatron 框架中**数据并行（Data Parallelism, DP）** 的背景、实现原理、使用场景、参数计算公式及约束条件，是 mindspeed 昇腾大模型加速库中关于"如何将大规模数据集拆分到多个 NPU 上并行训练"的基础能力说明。

---

## 【技术要点】

1. **数据并行的两条硬性前提**（原文要点）：
   - 每一台计算设备上部署的**模型结构与参数保持完全一致**；
   - 各设备处理的**数据批次互不相同**。

2. **整体思路三步走**（原文表述）：
   - **模型复制**：每个计算设备上存储完整的模型副本；
   - **数据分割**：原始数据集被细分为若干个批次，均匀分配至各个计算设备；
   - **梯度同步**：前向计算 → 获得局部梯度 → 通过 **All-Reduce** 操作汇集所有设备的梯度 → **计算平均值** → **广播回各设备**，维持全局参数一致性。

3. **数据并行数计算公式**（原文公式，逐字保留）：
   ```
   data_parallel_size = world_size // (tensor_model_parallel_size * pipeline_model_parallel_size * context_parallel_size)
   ```

4. **四个关键并行维度参数**（原文列出的配置项）：
   - `world_size`：参与并行训练的 NPU 总数；
   - `tensor_model_parallel_size`：模型权重的并行分割数；
   - `pipeline_model_parallel_size`：模型架构的流水线并行度；
   - `context_parallel_size`：针对长序列数据处理的并行策略。

5. **两条强约束（NOTE）**：
   - 模型总层数需被 `pipeline_model_parallel_size` 整除；
   - `global_batch_size` 需被 `data_parallel_size` 整除。

6. **适用场景的判定条件**（原文）：
   - **大规模数据集**：单一设备难以在合理时间内完成处理；
   - **计算资源充裕**：拥有足够数量的计算设备，能支撑多份完整模型的存储与并行训练。

---

## 【关键机制与数据】

**工作原理（梯度同步的数据流）**：
> 原文："完成前向计算并获取局部梯度后，通过All-Reduce操作汇集所有设备的梯度，计算平均值，再将结果广播回各设备，以此维持全局参数的一致性。"

其隐含的通信语义即经典的 **All-Reduce = Reduce + Broadcast**：
- 各设备先计算**局部梯度**（前向 + 反向）；
- All-Reduce 阶段对所有设备的梯度做**求和并取平均**；
- 同步后的均值**广播**到所有设备，使每台设备都拥有相同的更新后参数。

**负载均衡机制（原文）**：
> 原文："原始数据集被细分为若干个批次，然后均匀分配至各个计算设备，确保负载均衡。"

**性能特征（原文定性描述，无具体数字）**：
> 原文："数据并行架构具备良好的横向扩展性，能够随着计算资源的增加而线性提升性能"；
> "能够提高硬件资源的利用率"；
> "能够显著缩短训练周期"。

原文未给出具体的加速比、吞吐量数字或基准测试结果，因此无定量性能数据可列。

---

## 【表格解读】

**原文无表格。** 原文以文字段落和列表形式介绍了数据并行的背景、方案、场景、参数与约束，未包含任何表格（无参数表、无性能对比表、无配置项表）。

---

## 【公式解读】

原文仅出现一个公式：

$$
\text{data\_parallel\_size} = \text{world\_size} \; // \; (\text{tensor\_model\_parallel\_size} \times \text{pipeline\_model\_parallel\_size} \times \text{context\_parallel\_size})
$$

**逐符号含义说明：**

| 符号 | 含义（原文定义） | 作用 |
|------|-----------------|------|
| `world_size` | 参与并行训练的 NPU 总数 | 决定总并行规模 |
| `tensor_model_parallel_size` | 模型权重的并行分割数 | 切分单层内的权重矩阵（如 attention/MLP），占据若干 NPU |
| `pipeline_model_parallel_size` | 模型架构的流水线并行度 | 按层切分模型，不同 NPU 负责不同层段 |
| `context_parallel_size` | 针对长序列数据处理的并行策略 | 按序列维度切分，占据若干 NPU |
| `data_parallel_size` | 数据并行数（结果） | 剩余的 NPU 用于复制完整模型 + 切分数据批次 |
| `//` | 整数除法（floor） | 保证结果为正整数个 NPU |

**公式解读（实质语义）**：
在四维混合并行（DP + TP + PP + CP）下，物理 NPU 总数被三维切分（TP/PP/CP）共同占用，**剩余的 NPU** 才用于做数据并行。该公式是 mindspeed/Megatron 体系下混合并行的基本分配律——必须满足整除性，否则会因 NPU 不能被完整分组而报错。

---

## 【关联】

原文涉及的并行维度及相互关系如下：

- **与 Tensor Model Parallel（TP）的关系**：在数据并行的"每个完整模型副本"内部，权重仍可按 TP 进一步切分；TP 占用一部分 NPU。
- **与 Pipeline Model Parallel（PP）的关系**：数据并行要求"模型总层数需被 pipeline_model_parallel_size 整除"，即 PP 的层切分必须均分；PP 占用一部分 NPU。
- **与 Context Parallel（CP）的关系**：CP 针对长序列切分，是数据并行之外的另一种"数据维度"切分；CP 占用一部分 NPU。
- **与 `global_batch_size` 的关系**：全局 batch 必须被 `data_parallel_size` 整除，以确保每个 DP 副本拿到的 micro-batch 大小一致（整数）。

> 注：原文末尾未提供"内部链接"信息（题目给出"内部链接: (无)"），故无法进一步链接至具体其他特性/模块的文档。

---

## 【使用方法】

原文涉及的启用与配置项如下：

**1. 数据并行数自动计算（无需手动指定 DP size）**
> 原文："数据并行根据其他并行策略的设置自行计算。"

数据并行数 **不需要** 用户显式开启或赋值，而是由 `world_size` 与 TP/PP/CP 三个并行规模通过公式自动推导得出。

**2. 需要显式配置的四个参数**

| 参数 | 含义 |
|------|------|
| `world_size` | 参与训练的 NPU 总数 |
| `tensor_model_parallel_size` | 模型权重并行分割数 |
| `pipeline_model_parallel_size` | 模型架构流水线并行度 |
| `context_parallel_size` | 长序列并行切分数 |

**3. 必须满足的两条整除约束（启用前校验）**

- 模型总层数 % `pipeline_model_parallel_size` == 0
- `global_batch_size` % `data_parallel_size` == 0

**4. 具体启动命令**
> 原文未提供具体的 CLI 命令、yaml 配置示例或启动脚本模板，故此节中"具体启动命令"为"**原文未涉及**"。

---

> 整体而言，本文是一份偏**概念性 + 公式定义**的 feature 介绍，未涉及具体的 API、CLI、yaml 模板或性能基准数字；其核心交付物即 `data_parallel_size` 的自动推导公式与两条整除约束。
