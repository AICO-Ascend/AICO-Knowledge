# ChunkLoss

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/chunkloss.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/chunkloss.md

# ChunkLoss 文档深度解读

## 【定位】
这篇文档描述了在多模态理解模型训练中，针对 `lm_head` 输出词表维度远大于隐空间维度导致的 loss 计算显存峰值过高问题，通过沿序列维度分块计算损失来显著降低显存占用的 ChunkLoss 特性，包括其设计动机、原理概述、两种 FSDP2 后端下的 YAML/JSON 配置方法与使用效果。

---

## 【技术要点】

1. **显存峰值来源（背景痛点）**：`lm_head` 输出维度 `vocab_size` 远大于 `hidden_size`，传统 loss 计算需显式构造 `[bs, seq, vocab_size]` 的 logits 张量，词表越大或序列越长，显存峰值越显著；动态 shape 场景下还会引发大块内存碎片。
2. **核心机制（分块计算）**：将序列维度切分为 `sub_seq` 长度的子段（chunk），每个子段完成前向计算后立即执行反向传播，任意时刻最多只需缓存 `sub_seq` 长度的 logits。
3. **后端约束**：当前仅支持 FSDP2 后端，提供两种配置通道——原生 FSDP2（推荐）与基于 Megatron 的 FSDP2（过渡态，将退出）。
4. **静态 vs 动态二选一**：通过 `enable_chunk_loss`（默认 `false`）与 `enable_dynamic_chunk_loss`（默认 `false`）互斥启用静态/动态分块，不可混用。
5. **关键参数默认值**：静态模式下 `chunkloss_plan.chunk_size = 1024`（每块 token 数）；动态模式下 `chunkloss_plan.total_chunk_size = 4096`（单次计算总 token 上限，每块大小按批大小自动推导）；`apply_module` 默认 `lm_head`。
6. **loss 计算方式兼容性**：不改变 loss 计算方式本身，可与 default、per sample loss、per token loss 三种方式配合使用。

---

## 【关键机制与数据】

- **工作原理（原文）**："通过对序列维度进行分块（chunking），将 loss 计算拆分为多个长度为 `sub_seq` 的子段依次进行。在完成每个子段的前向计算后，立即执行对应的反向传播，从而避免同时保留整个序列的 logits。"
- **数据流（原文）**：每个子段独立走完「前向 → 反向」闭环，不跨块累积 logits，显存占用与子段长度线性相关而非与全序列长度相关。
- **动态分块约束（原文）**：`total_chunk_size` 默认 4096，"每块大小按批大小自动推导"，即动态分块通过 batch_size 反算单块长度，以约束总计算量上限避免显存溢出。
- **使用效果（原文）**："在多模态理解模型中启用 ChunkLoss 特性后，通过合理设置 `chunk_size`，可在显著降低显存峰值的同时保持相同的损失曲线。"（原文未给出具体数值/倍数/显存占用数据）
- **静态分块固定参数（原文）**：`chunk_size` 默认 `1024`（token 数），`apply_module` 默认 `lm_head`。

---

## 【表格解读】

**原文无表格**。文档以两个 YAML/JSON 配置代码块形式展示配置项，未以表格形式罗列参数对照；其参数对照关系已在上文【技术要点】与【使用方法】中按原文逐项还原。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 数学式或伪代码公式；其中 `chunk_size`、`total_chunk_size`、`sub_seq` 等仅以自然语言变量名出现，含义在正文【技术要点】与【使用方法】中已有解释。

---

## 【关联】

- **与 loss 计算方式的关联（核心下游）**：ChunkLoss 仅改变 loss 计算的显存/调度模式，不改变 loss 数值结果；与 default、per sample loss、per token loss 三种计算方式正交组合，三种方式的细节详见文末内部链接 **[VLM 模型 loss 计算方式](vlm_model_loss_calculate_type.md)**。
- **与 FSDP2 后端的依赖**：当前特性仅在 FSDP2 后端可用，对原生 FSDP2 与 Megatron-based FSDP2 提供两套不同的配置语法（前者走 `features` + `chunkloss_plan`，后者走 `model.json` 的 `loss_cfg`），且明确 Megatron-based 方案为过渡态，将退出，新增模型应优先使用原生 FSDP2。
- **与多模态理解模型的关联**：特性面向"多模态理解模型"（区别于多模态生成），典型配置示例见 `examples/qwen3_5/qwen3_5_4B_config.yaml`。
- **与 `lm_head` 模块的关联**：`chunkloss_plan.apply_module` 默认指向 `lm_head`，这正是传统方式构造 `[bs, seq, vocab_size]` 大张量的源头模块。

---

## 【使用方法】

### 方式一：原生 FSDP2（推荐）

在模型 YAML 配置文件的 `features` 段启用，二选一开启静态/动态分块：

```yaml
features:
  enable_chunk_loss: true          # 静态分块（与 enable_dynamic_chunk_loss 二选一）
  chunkloss_plan:
    apply_module: lm_head          # 应用模块，默认 lm_head
    chunk_size: 1024               # 静态分块每块 token 数，默认 1024
```

或动态分块配置：

```yaml
features:
  enable_dynamic_chunk_loss: true  # 动态分块
  chunkloss_plan:
    apply_module: lm_head
    total_chunk_size: 4096         # 单次计算总 token 上限，默认 4096，每块按 batch_size 自动推导
```

可参考 `examples/qwen3_5/qwen3_5_4B_config.yaml`。

### 方式二：基于 Megatron 的 FSDP2（过渡态，将退出）

在支持 ChunkLoss 的理解模型配置文件 `model.json` 的 `loss_cfg` 字段中设置：

```json
"loss_cfg": {
    "compute_mode": "chunk",
    "chunk_size": 1024
}
```

- `compute_mode` 取值：
  - `"default"`：原始 loss 计算方式；
  - `"chunk"`：启用 ChunkLoss 静态分块；
  - `"dynamic_chunk"`：启用 ChunkLoss 动态分块。
- `chunk_size` 取值含义随 `compute_mode` 变化：
  - `compute_mode = "chunk"` 时：每个子序列的最大长度（token 数）；
  - `compute_mode = "dynamic_chunk"` 时：每个子序列长度 × `batch_size` 的最大长度，用于约束动态分块总计算量。

通过合理设置 `chunk_size`，可在保证训练正确性的同时有效控制显存占用。
