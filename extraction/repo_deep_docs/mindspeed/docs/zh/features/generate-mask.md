# MindSpeed Mask归一实现阐述

> 仓 `mindspeed` · 路径 `docs/zh/features/generate-mask.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/generate-mask.md

# MindSpeed Mask 归一实现阐述 · 一体化深度解读

## 【定位】
这篇文档阐述 **MindSpeed 如何针对昇腾硬件（FA 算子）对 AttnMask 的需求，统一并优化 Megatron 原生 mask 生成流程**，解决非 PP 首尾节点 AttnMask 为 None、每 micro_step 重复生成/拷贝/广播、长序列显存占用过大等问题，使 Mask 生成能够契合昇腾 FA 加速场景。

---

## 【技术要点】

1. **统一 Mask 生成入口**：在 `mindspeed/model/transformer.py` 中定义全局变量 `global _GLOBAL_ATTN_MASK`，让同一进程内的 Attention 调用复用同一份 Mask，避免每次 `get_batch` 重复生成、拷贝与 broadcast。

2. **替代 Megatron 原生 mask 流程**：直接默认启用归一化 AttnMask，弃用原生"按 rank 各自生成"的方式；针对非 PP 首尾节点 AttnMask 为 None 导致 FA 无法启用的问题，通过 `parallel_transformer_forward_wrapper` 在第一次前向时调用 `generate_attention_mask` 来补齐 Mask。

3. **Mask 压缩模式自适应**：当 FA 场景下序列长度 **> 2048** 或使用 **ring_cp_algo** 时，默认走压缩模式（mask.shape 固定为 **[2048, 2048]**），其他场景仍使用完整 Mask，从而降低显存占用。

4. **稀疏模式参数化**：通过 `--sparse-mode` 传参对接 `torch_npu.npu_fusion_attention` 算子的多种稀疏模式（如压缩模式下 `sparse_mode=2`），用于下三角与 Band 等模式调用。

5. **三段式对外接口**：在 `mindspeed/model/transformer.py` 提供 `set_attention_mask`、`get_attention_mask`、`generate_attention_mask` 三个接口，覆盖正常流程外的设置、获取与生成能力，便于用户处理自定义 Mask。

6. **可选关闭原生行为**：Megatron 原有 AttnMask 生成可通过 `--no-create-attention-mask-in-dataloader` 关闭；MindSpeed 默认即覆盖此路径，不再依赖原生 mask 生成。

---

## 【关键机制与数据】

**Mask 生成链路（原文）：**
- Megatron 原生：每个 device 通过 `pretrain_gpt.py#L93 def get_batch` 取 AttnMask。
- PP 首尾节点：通过 `megatron/training/utils.py#L276 def get_batch_on_this_tp_rank` 取 AttnMask；其他 PP 节点直接返回 None。
- TP 首节点：通过 `megatron/core/datasets/gpt_dataset.py#L675 def _get_ltor_masks_and_position_ids` 真正生成 AttnMask。
- TP 其他节点：生成同 shape 的 empty 矩阵，通过 broadcast 从首节点拉取。
- 默认输出形态：全部为下三角形状；可通过 `--no-create-attention-mask-in-dataloader` 关闭。

**昇腾 FA 的矛盾（原文）：**
- 昇腾 FA 需要**外部**生成 AttnMask，且除下三角外还要支持**自定义**形状 → 原生 `_get_ltor_masks_and_position_ids` 接口不足。
- 非 PP 首尾节点 AttnMask 为 None → FA 无法启用加速。
- AttnMask 的生成、拷贝、广播每个 micro_step 都会跟随 `get_batch` 重复发生。
- 长序列下生成的 AttnMask 占用显存过大。

**MindSpeed 归一方案（原文）：**
- 复用全局变量 `_GLOBAL_ATTN_MASK`，避免重复生成/拷贝。
- 适配 AttnMask **压缩模式**，减少显存占用。

**使用场景与判定条件（原文）：**
- 同时支持 **FA 与非 FA** 的 Mask 生成；输入 AttnMask 可为 **None 或下三角**。
- **FA 场景触发压缩模式**的条件：序列长度 **> 2048** 或使用 **ring_cp_algo**。
- 其他场景使用**完整 Mask**。

**使用效果（原文）：**
- 下三角模式 + 压缩模式 + `sparse_mode=2`：`mask.shape` 固定为 **`[2048, 2048]`**，性能大幅提升、显存显著下降。

**当前边界（原文 NOTE）：**
- 当前 FA 场景**仅支持下三角与 Band 模式**。
- 其他自定义 AttnMask 模式需手动调用 `set_attention_mask`，或修改 `get_attention_mask` 逻辑。

---

## 【表格解读】
**原文无表格。**

---

## 【公式解读】
**原文无公式。**

---

## 【关联】

本特性面向**昇腾 FA 算子**（`torch_npu.npu_fusion_attention`）做适配，因此与以下上下文密切相关：

- **上游/被替代**：Megatron 原生 Mask 生成链路中的 `pretrain_gpt.py get_batch`、`megatron/training/utils.py get_batch_on_this_tp_rank`、`megatron/core/datasets/gpt_dataset.py _get_ltor_masks_and_position_ids`，以及原生开关 `--no-create-attention-mask-in-dataloader`。
- **下游/依赖硬件特性**：昇腾 `torch_npu.npu_fusion_attention` 算子（其 `--sparse-mode` 决定 sparse 模式选择，详见原文给出的算子文档链接）。
- **本仓内部模块**：`mindspeed/model/transformer.py` 中的 `global _GLOBAL_ATTN_MASK`、`set_attention_mask`、`get_attention_mask`、`generate_attention_mask`、`parallel_transformer_forward_wrapper`。
- **并行/通信策略**：与 **PP（Pipeline Parallel）**、**TP（Tensor Parallel）** 拓扑强相关——非 PP 首尾节点、TP 非首节点正是问题触发的位置；压缩模式的触发条件之一是 `ring_cp_algo`，与上下文并行（Context Parallel / Ring Attention）策略联动。
- **内部链接**：原文未提供文末内部链接。

---

## 【使用方法】

依据原文，使用方式包括：

1. **默认启用**：在 MindSpeed 中直接默认启用归一化 AttnMask，**不再使用原生 mask 生成方式**（即原生默认开启的下三角 mask 流程被本特性取代）。

2. **关闭原生 mask 生成**：可通过 Megatron 原生开关 `--no-create-attention-mask-in-dataloader` 关闭原生行为（原文标注此选项"默认开启"）。

3. **稀疏模式选择**：通过命令行传参 `--sparse-mode` 配合 `torch_npu.npu_fusion_attention` 算子多种调用模式，例如压缩模式下使用 `sparse_mode=2`。

4. **程序化接口**：通过 `mindspeed/model/transformer.py` 的三个对外接口使用：
   - `set_attention_mask`：设置 Mask；
   - `get_attention_mask`：获取 Mask；
   - `generate_attention_mask`：生成 Mask。
   处理正常流程之外的自定义 Mask 场景（FA 当前仅支持下三角与 Band，其他自定义模式需手动 `set_attention_mask` 或修改 `get_attention_mask` 逻辑）。

5. **首次前向补齐 Mask**：`parallel_transformer_forward_wrapper` 在第一次前向时调用 `generate_attention_mask`，绕过 `get_batch` 阶段无法在非 PP 首尾节点拿到 Mask 的缺陷。

> 原文未涉及更多具体的环境变量、配置项 yaml 字段或多卡启动命令；以上即为原文给出的全部启用与配置信息。
