# 特性设计：TensorCast 适配 MiniMax-M3 / MiniMax-M3-VL 模型

> 仓 `msmodeling` · 路径 `docs/design/minimax_m3_adaptation_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/minimax_m3_adaptation_design.md

# 一体化深度解读：TensorCast 适配 MiniMax-M3 / MiniMax-M3-VL 模型

---

## 【定位】

本文档描述了 TensorCast 如何在不复制 Transformers 上游 `minimax_m3_vl` 完整模型源码的前提下，通过「最小化 ModelProfile + 自定义 patch_method + 专用 Attention Wrapper + 语义 virtual op + Roofline 注册」六层适配方案，让 MiniMax-M3 / MiniMax-M3-VL（含 sparse attention、indexer cache、OAI SwiGLU、Gemma RMSNorm、fused gate_up_proj 等结构差异）在 decode/prefill 仿真与 trace 输出中获得与实测算子边界对齐的专用语义算子。

---

## 【技术要点】

1. **Sparse Attention 双分支建模**：MiniMax-M3 部分 decoder layer 为 sparse attention，链路在常规 Q/K/V attention 之外新增 indexer 分支，依次发射 `indexer.q_proj / k_proj → indexer q/k norm → indexer fused_rope → siso_reshape_and_cache → tensor_cast.minimax_indexer.default → tensor_cast.minimax_sparse_attention.default → o_proj`。

2. **SISO Indexer Cache**：MiniMax-M3 indexer 仅缓存 index key（无 index value），通过新增 `siso_reshape_and_cache` 表达 single-input single-output 写入。shape 为 `index_k: [T, indexer_heads, index_head_dim]` → `index cache: [num_blocks, block_size, index_head_dim]`；与普通 KV cache `[2, num_blocks, block_size, kv_heads, head_dim]` 区分。

4. **fused `gate_up_proj` 拆解**：把 Transformers 中 dense MLP 与 MoE expert 的 fused `gate_up_proj(hidden) → chunk → OAI SwiGLU → down_proj` 拆为 `gate_proj / up_proj → m3_swiglu → down_proj`，以便 `SinkSplitPass`、grouped matmul + SwiGLU 融合 pass 识别；量化场景使用 `m3_swiglu_quant`，把 `int8 activation + activation_scale` 显式传给 `TensorCastQuantLinear.down_proj(external_activation_scale)`。

5. **OAI SwiGLU 与 Gemma RMSNorm 显式化**：`m3_swiglu` 携带 `alpha`、`limit` 参数；RMSNorm 使用 Gemma 风格的 `1 + weight` 有效权重语义，并在 decoder layer 内显式融合 `add_rms_norm2`，保证 trace 中残差+norm 边界可见。

6. **Sparse Config 双路径兼容**：优先路径读取 `text_config.layer_types / index_n_heads / index_head_dim / index_topk_blocks / index_block_size / index_local_blocks`；兼容路径读取 `text_config.sparse_attention_config.sparse_attention_freq / sparse_num_index_heads / sparse_index_dim / sparse_topk_blocks / sparse_block_size / sparse_local_block`。MTP 层若 `layer_idx` 超数组长度则继承主干最后一层 sparse 配置。

7. **MoE 注册最小化**：`ModelProfile(model_type="minimax_m3_vl", moe_module_name="MiniMaxM3VLSparseMoeBlock", moe_num_experts_key="num_local_experts", moe_gate_router=route_minimax_m3_gate, patch_method=patch_method_for_minimax_m3, language_layers_path_str="language_model.layers", custom_expert_module_type=MiniMaxM3MoeExpertMLP)`，不新增通用 profile 字段。

8. **Patch 流水线六步**：依次执行 `cache_rotary_embedding=False → patch_minimax_m3_attention → patch_minimax_m3_layernorm → patch_minimax_m3_dense_mlp → patch_minimax_m3_moe_gate_attrs → patch_moe`，把 MoE 的 `routed_scaling_factor` 挂到 gate 对象供通用 router 读取。

---

## 【关键机制与数据】

### 工作原理

整体链路（原文 §2.1）：
```text
HF MiniMax-M3-VL model
  → TensorCast ModelProfile(minimax_m3_vl)
  → patch_method_for_minimax_m3
  → MiniMaxM3AttentionWrapper / MLP Wrapper / MoE Expert Adapter
  → TensorCast virtual ops
  → AnalyticPerformanceModel Roofline
  → op-bound table / chrome trace / shape dump
```

### 七个背景问题（原文 §1）

| # | 问题 | 后果 |
|---|------|------|
| 1 | Sparse Attention 链路缺失 | 通用 attention op 无法表达 indexer score、TopK block 选择和 sparse QK/PV 边界 |
| 2 | Indexer cache ≠ 普通 KV cache | 仅有 K 无 V，需要 `siso_reshape_and_cache` |
| 3 | fused `gate_up_proj` | 不利于 `SinkSplitPass`、grouped matmul + SwiGLU 融合识别 |
| 4 | OAI SwiGLU ≠ 普通 SwiGLU | 带 `alpha`、`limit` 参数，量化需传 activation scale |
| 5 | Gemma RMSNorm | `1 + weight` 有效权重，需融合为 `add_rms_norm2` |
| 6 | `torch.compile` / meta tensor 下真实长度易丢失 | sparse indexer / sparse attention 成本强依赖 `seq_len`、`query_len`、decode/prefill 阶段 |
| 7 | Transformers 新旧配置字段不一致 | `layer_types`+`index_*` vs `text_config.sparse_attention_config` 下 `sparse_*` |

### Sparse Attention 配置字段映射（原文 §2.4.0）

| 优先路径字段 | 兼容路径字段 | 含义 |
|---|---|---|
| `text_config.layer_types` | `text_config.sparse_attention_config.sparse_attention_freq` | 标识 sparse/dense 层 |
| `text_config.index_n_heads` | `text_config.sparse_attention_config.sparse_num_index_heads` | indexer head 数 |
| `text_config.index_head_dim` | `text_config.sparse_attention_config.sparse_index_dim` | indexer head dim |
| `text_config.index_topk_blocks` | `text_config.sparse_attention_config.sparse_topk_blocks` | 每个 query 选 TopK 个 KV block |
| `text_config.index_block_size` | `text_config.sparse_attention_config.sparse_block_size` | KV block 大小 |
| `text_config.index_local_blocks` | `text_config.sparse_attention_config.sparse_local_block` | 局部 block 数量 |

### Dense / Sparse Attention 数据流（原文 §2.4.1, §2.4.2）

- **Dense**：`hidden_states → q/k/v_proj → q/k_norm → fused_rope → reshape_and_cache → tensor_cast.attention.default → o_proj`
- **Sparse**：在 dense 链路之外**并行**增加 indexer 分支：`indexer.q_proj / k_proj → indexer q/k norm → indexer fused_rope → siso_reshape_and_cache → tensor_cast.minimax_indexer.default → tensor_cast.minimax_sparse_attention.default → o_proj`

### Cache shape 对比（原文 §2.5）

| 类型 | Shape |
|---|---|
| 普通 KV cache | `[2, num_blocks, block_size, kv_heads, head_dim]` |
| Indexer key cache | `[num_blocks, block_size, index_head_dim]` |
| Indexer 输入 key | `[T, indexer_heads, index_head_dim]` |

### Roofline 建模维度（原文 §2.1 第 6 项）

为 MiniMax-M3 专用 op 注册 Roofline 属性时区分：MMA（矩阵乘算力）、GP（通用/elementwise 算力）、Q/O/topk metadata 访存、K/V cache 访存、通信边界。

---

## 【表格解读】

### 表 1：修订记录（原文表格 1）

| 日期 | 版本 | 修改描述 | 作者 | 关联文档 |
| --- | --- | --- | --- | --- |
| 2026-07-27 | 1.0 | 初稿完成，归档 MiniMax-M3 在 TensorCast 中的模型适配、算子边界、Roofline 建模和验证方案 | - | - |

**逐行解读**：
- **第 1 行**：2026-07-27 发布 v1.0 初稿，定位为「MiniMax-M3 在 TensorCast 中的模型适配、算子边界、Roofline 建模和验证方案」的归档文档；作者与关联文档字段为空。

### 表 2：Patch Method 各步骤职责（原文 §2.3 表格）

| 步骤 | 作用 | 必要性 |
| --- | --- | --- |
| `cache_rotary_embedding=False` | 关闭通用 rotary cache rewrite | MiniMax-M3 有 partial/3D RoPE，通用缓存形状可能不兼容 |
| `patch_minimax_m3_attention` | 替换每层 `self_attn` 为 `MiniMaxM3AttentionWrapper` | 显式区分 dense attention 与 sparse attention |
| `patch_minimax_m3_layernorm` | 替换 RMSNorm wrapper，并 patch decoder layer forward | 建模 Gemma RMSNorm 和 `add_rms_norm2` |
| `patch_minimax_m3_dense_mlp` | 替换 dense MLP fused `gate_up_proj` | 让 dense MLP 与 MoE expert 使用统一 split gate/up 结构 |
| `patch_minimax_m3_moe_gate_attrs` | 把 MoE block 的 `routed_scaling_factor` 挂到 gate | 通用 router 只拿到 gate 对象，需要从 gate 读取缩放因子 |
| `patch_moe` | 复用 TensorCast 通用 MoE patch | 继续使用 dispatch、grouped matmul、combine 等现有能力 |

**逐行解读**：
- **第 1 行**：通过 `model.model_config.cache_rotary_embedding = False` 关闭通用 rotary 缓存重写，因为 MiniMax-M3 的 partial/3D RoPE 与通用缓存形状不兼容。
- **第 2 行**：将每层 `self_attn` 替换为 `MiniMaxM3AttentionWrapper`，让 dense 与 sparse attention 在同一 wrapper 中显式分流。
- **第 3 行**：替换 RMSNorm wrapper 并 patch decoder layer forward，把 Gemma RMSNorm 的 `1+weight` 与残差+norm 融合为 `add_rms_norm2`，保证 trace 边界与实测对齐。
- **第 4 行**：把 dense MLP 的 fused `gate_up_proj` 拆为 split `gate_proj / up_proj`，让 dense MLP 与 MoE expert 共享同一套 SwiGLU 融合 pass。
- **第 5 行**：把 MoE block 的 `routed_scaling_factor` 属性挂到 gate 对象，使通用 router 仅持有 gate 引用即可读取缩放因子。
- **第 6 行**：复用 TensorCast 通用 `patch_moe`，继续受益于现有 dispatch、grouped matmul、combine 等能力。

---

## 【公式解读】

> 原文未给出显式 LaTeX/伪代码数学公式，但包含以下结构化数据描述（按「公式式」形式逐字保留并解释每个符号含义与作用）：

### 公式 A：普通 KV Cache Shape（原文 §2.5）

$$
\text{KV cache} \in \mathbb{R}^{[2,\ \text{num\_blocks},\ \text{block\_size},\ \text{kv\_heads},\ \text{head\_dim}]}
$$

| 符号 | 含义 |
|---|---|
| `2` | 第一维固定为 2，分别表示 K 路与 V 路缓存 |
| `num_blocks` | KV cache 分块管理的总 block 数 |
| `block_size` | 每个 block 容纳的 token 数 |
| `kv_heads` | K/V 的 head 数（可能小于 attention head 数） |
| `head_dim` | 每个 head 的特征维度 |

### 公式 B：Indexer Key Cache Shape（原文 §2.5）

$$
\text{index\_key} \in \mathbb{R}^{[T,\ \text{indexer\_heads},\ \text{index\_head\_dim}]}
$$
$$
\text{index\_cache} \in \mathbb{R}^{[\text{num\_blocks},\ \text{block\_size},\ \text{index\_head\_dim}]}
$$

| 符号 | 含义 |
|---|---|
| `T` | 当前 request 的 token 数（query 长度） |
| `indexer_heads` | indexer 的 head 数（`index_n_heads` / `sparse_num_index_heads`） |
| `index_head_dim` | indexer 每个 head 的维度（`index_head_dim` / `sparse_index_dim`） |
| `num_blocks`、`block_size` | 与 KV cache 相同的分块管理维度 |

**作用**：原文用此对比说明 indexer cache 不含 value 维，因此需要 `siso_reshape_and_cache`（single-input single-output）来写入，而不能复用普通 `reshape_and_cache`（双输入 K、V）。

### 公式 C：sparse attention block 选择逻辑（原文 §1, §2.4.0）

$$
\text{topk\_blocks} = \text{TopK}\!\left(\text{indexer\_score}(q_{\text{idx}}, k_{\text{idx}}),\ \text{index\_topk\_blocks}\right)
$$
$$
\text{sparse\_attn}(q,k,v) = \text{softmax}\!\left(\frac{q \cdot k_{\text{selected}}^T}{\sqrt{d}}\right) v_{\text{selected}}
$$

| 符号 | 含义 |
|---|---|
| `indexer_score(q_idx, k_idx)` | learned indexer 对每个 query token × KV block 计算重要性分数 |
| `TopK(·, index_topk_blocks)` | 为每个 query token 选出 TopK 个 KV block |
| `q · k_selected^T` | 仅在 `index_topk_blocks` 个被选中的 KV block 上做 QK |
| `d` | attention head dim，用于 softmax 缩放 |

**作用**：原文以此说明通用 attention op 无法表达 indexer score 与 sparse QK/PV 边界，因此必须把 `minimax_indexer`（只表达 index score、block reduce、TopK block 选择）与 `minimax_sparse_attention`（只表达 sparse QK/PV/softmax attention body）拆为两个独立 virtual op。

---

## 【关联】

文档中显式提及的模块/算子/上下游关系（按文中出现顺序）：

- **上游 Transformers**：`model_type="minimax_m3_vl"` 原生模型源码；`MiniMaxM3VLSparseMoeBlock`；HF 原始 attention、RMSNorm、dense MLP、`gate_up_proj`。
- **TensorCast 模型注册入口**：`tensor_cast/transformers/builtin_model/minimax_m3.py`（`register_model_profile`、`ModelProfile`、`language_model.layers`）。
- **TensorCast Patch 工具链**：`patch_method_for_minimax_m3`、`patch_minimax_m3_attention`、`patch_minimax_m3_layernorm`、`patch_minimax_m3_dense_mlp`、`patch_minimax_m3_moe_gate_attrs`、`patch_moe`、`SinkSplitPass`、`_get_minimax_m3_effective_text_config`、`_resolve_minimax_m3_sparse_attention_config`。
- **TensorCast 自定义类**：`MiniMaxM3AttentionWrapper`、`MiniMaxM3MoeExpertMLP`、`route_minimax_m3_gate`。
- **TensorCast virtual ops（语义算子层）**：
  - 通用：`tensor_cast.attention.default`、`fused_rope`、`reshape_and_cache`、`TensorCastQuantLinear.down_proj(external_activation_scale)`。
  - MiniMax-M3 专用：`tensor_cast.minimax_indexer.default`、`tensor_cast.minimax_sparse_attention.default`、`m3_swiglu`、`m3_swiglu_quant`、`siso_reshape_and_cache`、`tensor_cast.moe_gating_top_k_sigmoid.default`（sigmoid top-k）。
- **TensorCast 性能模型**：`tensor_cast/performance_model/__init__.py`（Roofline 注册）、`AnalyticPerformanceModel Roofline`。
- **下游产物**：`op-bound table`（算子边界表）、`chrome trace`、`shape dump`。
- **横向兼容**：DeepSeek、GLM 等已有 MoE expert 的 split gate/up 结构（原文 §2.6 对齐依据）；`moe_module_name`、`moe_num_experts_key`、`moe_gate_router`、`patch_method`、`custom_expert_module_type` 等通用 MoE 框架字段。
- **未给出内部链接**：原文末尾标注「(无)」，本文据未引用内链，按文件路径 + 模块名组织上述关联。

---

## 【使用方法】

文档未单独列出「启动命令」「配置文件」「开关项」一节，原始注册入口与 patch 入口已在前文给出。可总结为以下**启用方式**：

1. **注册入口**（原文 §2.2）：
   - 文件：`tensor_cast/transformers/builtin_model/minimax_m3.py`
   - 调用：`register_model_profile(ModelProfile(model_type="minimax_m3_vl", moe_module_name="MiniMaxM3VLSparseMoeBlock", moe_num_experts_key="num_local_experts", moe_gate_router=route_minimax_m3_gate, patch_method=patch_method_for_minimax_m3, language_layers_path_str="language_model.layers", custom_expert_module_type=MiniMaxM3MoeExpertMLP))`

2. **Patch 入口**（原文 §2.3）：
   - 函数：`patch_method_for_minimax_m3(model: TransformerModel) -> TransformerModel`
   - 内部按序调用：`patch_minimax_m3_attention → patch_minimax_m3_layernorm → patch_minimax_m3_dense_mlp → patch_minimax_m3_moe_gate_attrs → patch_moe`

3. **Sparse Config 解析**（原文 §2.4.0）：
   - 通过 `_get_minimax_m3_effective_text_config` 定位真正的语言模型 config。
   - 通过 `_resolve_minimax_m3_sparse_attention_config` 统一返回 sparse attention 配置。

4. **Trace 输出位置**（原文 §2.1）：
   - op-bound table / chrome trace / shape dump（由 `AnalyticPerformanceModel Roofline` 产出）。

> 注：文档 §2.7「MiniMax-M3 MoE Gate Router」与后续小节原文在「调用 `tensor_cast.moe_gating_top_k_sigmoid.defau」处被截断，启用细节以原文实际章节为准，原文未给出的具体配置项/开关/CLI 命令本文不臆测。
