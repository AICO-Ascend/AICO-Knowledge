# PP支持多参数传递和动态形状

> 仓 `mindspeed` · 路径 `docs/zh/features/multi_parameter_pipeline_and_variable_seq_lengths.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/multi_parameter_pipeline_and_variable_seq_lengths.md

# 一体化深度解读: PP支持多参数传递和动态形状

## 【定位】

本篇文档描述了 mindspeed 昇腾大模型加速库在流水线并行（Pipeline Parallelism, PP）场景下, 同时支持「跨阶段多参数（非单张量）传递」与「变长序列（动态形状）」两项能力的启用方式、原理概述、适用场景与兼容性约束。

---

## 【技术要点】

1. **多参数传递通信机制**: 针对传统 PP 仅在阶段间传输单一张量的问题, 文档提出一套高效通信机制, 支持多种类型与格式数据的传输, 并要求对每个变量的 `shape`、`dtype` 等属性进行精确管理。
2. **多输出梯度反向传播改进**: 对反向传播算法进行改造, 使系统可自动识别并处理来自多个输出（多参数）的梯度信息, 避免因多参数传递导致的梯度聚合失效。
3. **动态形状（变长序列）支持**: 引入对动态形状的支持, 允许每个 micro-batch 中的序列保持其原始长度, 而不再统一 pad 到同一长度。
4. **形状预通信机制**: 在实际发送张量之前, 先在流水线各阶段间通信张量的形状信息, 提前同步即将接收的数据形状, 以确保内存分配和预处理的准确性。
5. **特性注册 / 参数表校验**: 用户需要在 `mindspeed/features_manager/pipeline_parallel/multi_parameter.py` 模块的 `validate_args` 函数中, 修改 `args.pipeline_tensor_shapes` 的值, 使其与实际模型流水线阶段的张量传输一致（包含 `Shape` 与 `Dtype`）。
6. **兼容性约束**: 该特性**暂不兼容** `--moe-fb-overlap` 和 `dualpipev` 特性。

---

## 【关键机制与数据】

### 多参数传递

- **工作原理（原文）**: "开发了一套高效的通信机制，支持多种类型和格式的数据传输，并改进了反向传播算法，使得系统可以自动识别并处理来自多个输出的梯度信息。"
- **关注属性（原文）**: 每个被传递变量的 `shape` 与 `dtype` 属性是必须精确管理的内容。
- **数据流（原文）**: 跨 PP 阶段之间的张量流, 由原来的「单一张量」扩展为「多参数集合」（多张量、多类型）。

### 动态形状

- **核心做法（原文）**: "引入对动态形状的支持，允许每个微批次中的序列保持其原始长度。"
- **同步流程（原文）**: "这样可以通过在发送张量之前，提前通信张量的形状信息，在各个流水线阶段之间同步即将接收的数据形状，确保内存分配和预处理的准确性。"
- **数据流（原文）**: shape-info 先于 tensor 在阶段间广播 → 接收方按该 shape 预分配内存与预处理 → 再接收真正张量。

### 性能数据

> 原文未提供任何具体的性能数据（如吞吐提升、显存节省数值、时延对比表等）。

---

## 【表格解读】

> 原文无表格

---

## 【公式解读】

> 原文无公式

---

## 【关联】

文档中明确点出的上下游/横向关联:

- **Pipeline Parallelism (PP)**: 本特性的承载基础, 文档核心即围绕 PP 阶段间通信展开。
- **Virtual Pipeline Parallelism (VPP)**: 在 PP 的基础上叠加了 `--num-layers-per-virtual-pipeline-stage` 的虚拟切分场景, 文档单独给出了 VPP 版本的启用命令。
- **`mindspeed/features_manager/pipeline_parallel/multi_parameter.py`**: 多参数特性的功能注册与参数校验模块, 用户需要修改其 `validate_args` 中 `args.pipeline_tensor_shapes` 配置。
- **`--moe-fb-overlap`**: 不兼容项之一（MoE 相关重叠优化）。
- **`dualpipev`**: 不兼容项之一（dualpipev 相关特性）。
- **多模态训练场景**: 在文本/图像/音频等跨模态任务中, 文档指出各 PP 阶段需要传递多参数, 是本特性的主要驱动力。
- **变长文本任务**: 文档分类、机器翻译等序列长度差异大的任务, 是动态形状特性的目标场景。

> 文末**无内部链接**, 上述关联均为正文直接提及的模块/参数名。

---

## 【使用方法】

### 启用准备（必须修改）

- 修改 `mindspeed/features_manager/pipeline_parallel/multi_parameter.py` 中 `validate_args` 函数里 `args.pipeline_tensor_shapes` 的值, 使其与实际模型流水线阶段的张量传输一致（包含 `Shape` 和 `Dtype`）。

### PP 场景启动参数

```shell
# PP >= 2
--pipeline-model-parallel-size ${PP} \
--use-multiparameter-pipeline-model-parallel \
--variable-seq-lengths \
```

- `${PP}` 取值需 `>= 2`。
- 启用多参数传递的开关: `--use-multiparameter-pipeline-model-parallel`
- 启用动态形状（变长序列）的开关: `--variable-seq-lengths`

### VPP 场景启动参数

```shell
# PP >= 2, num-layers-per-virtual-pipeline-stage不为None
--pipeline-model-parallel-size ${PP} \
--num-layers-per-virtual-pipeline-stage 1 \
--use-multiparameter-pipeline-model-parallel \
--variable-seq-lengths \
```

- 在 PP 参数基础上额外加入 `--num-layers-per-virtual-pipeline-stage 1`（文档要求该值不为 `None`）。

### 兼容性约束

> 原文明确说明:
> - 暂不兼容 `--moe-fb-overlap`。
> - 暂不兼容 `dualpipev` 特性。

### 使用效果（原文）

> "同时支持在流水线并行中各阶段间传递多个参数和处理变长输入数据。"

即两项能力（多参数传递 + 动态形状）可同时启用, 在 PP/VPP 场景下联合生效。
