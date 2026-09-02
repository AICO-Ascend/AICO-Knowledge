# PP支持多参数传递

> 仓 `mindspeed` · 路径 `docs/zh/features/multi_parameter_pipeline.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/multi_parameter_pipeline.md

# 一体化深度解读：PP支持多参数传递

## 【定位】
本文档描述了 mindspeed 库中**流水线并行（PP）支持多参数传递**的特性能力，旨在解决多模态大模型分布式训练场景下，传统 PP 单张量传输无法满足多变量传递需求的问题，使用户能够在 PP 各阶段间灵活传递多个张量/变量。

---

## 【技术要点】

1. **核心开关参数**：通过命令行参数 `--use-multiparameter-pipeline-model-parallel` 启用 PP 多参数传递能力（PP ≥ 2）。
2. **必备配置**：用户需手动修改 `mindspeed/features_manager/pipeline_parallel/multi_parameter.py` 模块中 `validate_args` 函数里的 `args.pipeline_tensor_shapes` 值，使其与实际模型流水线阶段张量传输的 Shape 和 Dtype 保持一致。
3. **双场景支持**：分别支持标准 PP 场景与虚拟流水线并行（VPP）场景，后者需额外设置 `--num-layers-per-virtual-pipeline-stage 1`。
4. **通信机制优化**：针对每个阶段的具体需求定制化配置传输参数，支持多种类型和格式的数据传输，覆盖多变量的 shape、dtype 等属性管理。
5. **梯度计算增强**：改进反向传播算法，使其可自动识别并处理来自**多个输出**的梯度信息，每个输出都能参与最终权重更新。
6. **不兼容性约束**：暂不兼容 `--moe-fb-overlap` 和 `dualpipev` 特性。

---

## 【关键机制与数据】

### 工作原理（原文机制描述）

**1. 通信部分的设计**
- 原文：传统 PP 通常只涉及单一张量的传输，多参数传递需处理多个变量的传递，通信复杂度上升。
- 原文：需对每个变量的 **shape、dtype 等属性**进行精确管理，这些属性与整体模型架构紧密相关，具有高度定制性。

**2. 前向传播的数据流**
- 原文：在前向计算过程中，需根据定义的 shape 正确传递多个变量，并确保每个阶段接收到的数据格式符合预期。

**3. 反向传播的梯度流**
- 原文：除对首个输出进行梯度计算外，还需对其他所有输出进行相应的运算，确保整个训练过程的完整性和准确性。
- 原文：系统可自动识别并处理来自多个输出的梯度信息。

### 性能数据
- 原文未提供具体的性能数据（如加速比、吞吐提升、显存节省等量化指标）。

---

## 【表格解读】

**原文无表格**。原文档主要以段落和代码块形式描述，未提供参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式**。原文档未包含任何 LaTeX 公式或伪代码形式的数学表达式。

---

## 【关联】

### 与其他特性的关系（基于文末约束信息）

- **互斥特性**（原文标注不兼容）：
  - `--moe-fb-overlap`：MoE 场景下的 feature-block overlap 优化与多参数 PP 传递暂不兼容。
  - `dualpipev`：dualpipev 特性与多参数 PP 传递暂不兼容。

### 模块依赖

- **核心配置模块**：`mindspeed/features_manager/pipeline_parallel/multi_parameter.py` 中的 `validate_args` 函数，是用户启用该特性时必须修改配置的地方，决定 `args.pipeline_tensor_shapes` 的具体取值。
- **上游能力**：Pipeline Parallelism（PP）与 Virtual Pipeline Parallelism（VPP）是本特性的基础并行能力。

### 上下游链接

- 原文未提供内部超链接信息（文末标注"内部链接: (无)"）。

---

## 【使用方法】

### 一、标准 PP 场景（PP ≥ 2）

```shell
# PP >= 2
--pipeline-model-parallel-size ${PP} \
--use-multiparameter-pipeline-model-parallel \
```

### 二、VPP（虚拟流水线）场景

```shell
# PP >= 2, num-layers-per-virtual-pipeline-stage 不为 None
--pipeline-model-parallel-size ${PP} \
--num-layers-per-virtual-pipeline-stage 1 \
--use-multiparameter-pipeline-model-parallel \
```

### 三、必做配置（来自原文 NOTE 提示）

> 用户需修改 `mindspeed/features_manager/pipeline_parallel/multi_parameter.py` 模块中 `validate_args` 函数里 `args.pipeline_tensor_shapes` 值，使其与实际模型流水线阶段的张量传输一致，包括张量维度（Shape）和数据类型（Dtype）。

### 四、兼容性约束（原文 NOTE）

- 暂不兼容 `--moe-fb-overlap` 特性。
- 暂不兼容 `dualpipev` 特性。
