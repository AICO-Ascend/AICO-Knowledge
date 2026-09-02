# Turn model into Megatron-LM version

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_10_MEGATRON.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_10_MEGATRON.md

# TUTORIAL_10_MEGATRON.md 深度解读

## 【定位】
本文档描述如何将普通 Transformer 模型中的 MLP 层和 Self-/Cross-Attention 层改造为 Megatron-LM 风格的张量并行版本（即 ColumnParallelLinear 与 RowParallelLinear），从而在 `mpu` 模块支撑下完成模型并行（张量并行）的接入。

---

## 【技术要点】

1. **改造入口与目录**：MLP 改造位于 `flagai/model/layers/embeddings_mpu.py`，Self-Attention 改造位于 `flagai/model/layers/attentions_mpu.py`。原文明确："Most of the process in `parallel` are taken from `Megatron-LM`，and is put in `mpu` module"。

2. **MLP 拆分为 Column-first 两段**：将原始 `dense_h_to_4h`（hidden→4h）替换为 `ColumnParallelLinear(hidden_size, 4*hidden_size, gather_output=False)`，将 `dense_4h_to_h`（4h→hidden）替换为 `RowParallelLinear(4*hidden_size, hidden_size, input_is_parallel=True)`。中间仍串接 `gelu`，遵循 column-first 拆分原则。

3. **Self-Attention 拆 QKV 与输出**：将 Q、K、V 三个投影合并为一个 `ColumnParallelLinear(hidden_size, 3*hidden_size, stride=3, gather_output=False)`；输出投影 `dense` 替换为 `RowParallelLinear(hidden_size, hidden_size, input_is_parallel=True)`。

4. **Cross-Attention 同样拆分**：Q 单独为 `ColumnParallelLinear(hidden_size, hidden_size, gather_output=False)`；K、V 合并为 `ColumnParallelLinear(hidden_size, 2*hidden_size, stride=2, gather_output=False)`；输出 `dense` 仍为 `RowParallelLinear(hidden_size, hidden_size, input_is_parallel=True)`。

5. **并行维度关键参数**：通过 `get_model_parallel_world_size()` 获取 `world_size`，进而计算 `hidden_size_per_partition = divide(hidden_size, world_size)`、`hidden_size_per_attention_head = divide(hidden_size, num_attention_heads)`、`num_attention_heads_per_partition = divide(num_attention_heads, world_size)`。

6. **参数配对约束**：原文注释强调"`input_is_parallel=True` 受到 `self.dense_h_to_4h` 的 `gather_output` 设置影响"，即 Column 端不 gather 输出时，Row 端需以 partition 形式接收输入。

---

## 【关键机制与数据】

- **Column-first 拆分原则**：原文："split the two forward1 layers in 1 linear1 layer, following the column-fist principle"。将 MLP 的两次线性变换分别在 column 方向与 row 方向切分到多个 GPU 上。
- **数据流（MLP）**：hidden_states → ColumnParallel（hidden→4h/gather_output=False）→ gelu → RowParallel（4h→hidden/input_is_parallel=True）→ output。
- **数据流（Self-Attention）**：x → ColumnParallel（hidden→3h，stride=3，gather_output=False）得到 partition 后的 q/k/v → attention → RowParallel（hidden→hidden，input_is_parallel=True）。
- **数据流（Cross-Attention）**：x → ColumnParallel（hidden→hidden，gather_output=False）得到 partition 后的 q；context → ColumnParallel（hidden→2h，stride=2，gather_output=False）得到 partition 后的 k/v；最后 RowParallel（hidden→hidden，input_is_parallel=True）输出。
- **stride 参数作用**：在 ColumnParallel 中，`stride=3` 表示将输出按 3 个一组切分（对应 Q/K/V），`stride=2` 表示按 2 个一组切分（对应 K/V）。
- **gather_output 控制通信**：`gather_output=False` 表示输出保持在 partition 状态以避免中间通信；`input_is_parallel=True` 表明输入已经是 partition 状态，跳过再次切分。
- 原文未提供性能数据或基准测试结果。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- 与 **`mpu` 模块**的关系：原文指出 `parallel` 子模块中的大部分流程取自 `Megatron-LM`，并被置于 `mpu` 模块内，本教程的所有改造都依赖于 `mpu` 提供的并行原语。
- 与 **`Megatron-LM` 上游**：本文档明确其方法沿袭 Megatron-LM 的张量并行设计，使用 `ColumnParallelLinear` / `RowParallelLinear` 这两类核心并行线性层。
- 与 **`get_model_parallel_world_size()` 等并行工具函数**：通过 `divide(hidden_size, world_size)` 计算每卡分片维度，构成所有 `ColumnParallelLinear` / `RowParallelLinear` 的内部切分依据。
- 上下游模块衔接：MLP 改造对应 `embeddings_mpu.py`，Self-Attention / Cross-Attention 改造对应 `attentions_mpu.py`，二者都属于 `flagai/model/layers/` 下的并行层实现，是构建整个并行模型的基础组件。
- 文档内部链接：原文未提供内部链接。

---

## 【使用方法】

原文未给出完整的命令行启用方式或配置文件样例，仅说明：
- 改造 MLP 层：在 `flagai/model/layers/embeddings_mpu.py` 中，将 `dense_h_to_4h` 替换为 `ColumnParallelLinear(hidden_size, 4*hidden_size, gather_output=False)`，将 `dense_4h_to_h` 替换为 `RowParallelLinear(4*hidden_size, hidden_size, input_is_parallel=True)`。
- 改造 Self-Attention：在 `flagai/model/layers/attentions_mpu.py` 中，将 `query_key_value` 替换为带 `stride=3, gather_output=False` 的 `ColumnParallelLinear`；将 `dense` 替换为 `RowParallelLinear(hidden_size, hidden_size, input_is_parallel=True)`。
- 改造 Cross-Attention：分别将 `query`、`key_value`（stride=2，gather_output=False）替换为 `ColumnParallelLinear`，将 `dense` 替换为 `RowParallelLinear`。
- 并行规模由 `get_model_parallel_world_size()` 给定，进而推算 `hidden_size_per_partition` 等分片维度。

原文未涉及具体的训练启动命令、配置文件路径或环境变量设置。
