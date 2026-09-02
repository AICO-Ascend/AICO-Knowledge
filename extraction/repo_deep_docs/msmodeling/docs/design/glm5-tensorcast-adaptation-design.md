# GLM5 TensorCast 适配设计

> 仓 `msmodeling` · 路径 `docs/design/glm5-tensorcast-adaptation-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/glm5-tensorcast-adaptation-design.md

```markdown
# GLM5 TensorCast 适配设计 — 一体化深度解读

## 【定位】
本文档描述 TensorCast（MindStudio-Modeling 性能建模仿真工具）如何适配 GLM5 系列模型（包括 GLM-5.2），使其能够正确编译与仿真 sparse attention、MLA、MoE、MTP、RMSNorm fusion 及 DSA Indexer 相关性能估算，重点解决 GLM5 与既有 DeepSeek-V3.2 稀疏 MLA 路径在模型类型、配置字段、语义算子、归一化 epsilon、indexer cache dtype 及 IndexShare 共享机制上的差异。

---

## 【技术要点】

1. **模型注册（model profile）层**：新增 `tensor_cast/transformers/builtin_model/glm5.py`，将 HF `model_type="glm_moe_dsa"` 映射到 `Glm5SparseAttention`、`GlmMoeDsaMoE`、`GlmMoeDsaDecoderLayer` 等 GLM5 命名模块；关键字段包括 `moe_module_name="GlmMoeDsaMoE"`、`moe_num_experts_key="n_routed_experts"`、`moe_gate_returns_raw_logits=True`、`mla_module_name="GlmMoeDsaAttention"`、`mla_module_class_type=Glm5SparseAttention`、`mtp_block_module_name="GlmMoeDsaDecoderLayer"`、`custom_expert_module_type=MoeExpertMLP`。

2. **Sparse MLA 配置兼容**：在 `DeepseekSparseAttention` / `DeepseekSparseAttentionIndexer` 中通过 `_resolve_sparse_topk_limit(...)` 收敛 GLM5 的 `index_topk` 与 DeepSeek 的 `topk_limit`，优先级为：显式 `topk_limit` → indexer 自身 `topk_limit` → attention/indexer config 的 `topk_limit` → GLM5 风格 `index_topk` → `AttributeError("topk_limit")`；indexer 在构造时一次性缓存解析结果，避免 `torch.compile` 路径动态属性查找。

3. **GLM-5.2 IndexShare 共享层**：通过 HF config 的 `indexer_types`（取值 `full` / `shared`）控制跨层 top-k 数据流。`full` 层执行 DSA indexer 并生成 `topk_indices`；`shared` 层通过 `prev_topk_indices` 复用最近前序 `full` 层结果，连续 `shared` 链原样转发同一份 top-k。MTP 扩展通过 `extend_glm5_indexer_types_for_mtp(...)` 追加 `full`，避免 MTP block 错误消费主栈 `prev_topk_indices`；启用 IndexShare 时 `maybe_reuse_layers(...)` 仅复用 MLP 子模块，attention 与 top-k 数据流仍逐层执行。

4. **Transformers 兼容 wrapper**：`patch_glm5_model(...)` 仅在原生 decoder 不支持 `prev_topk_indices` 时安装 `Glm5ModelCompat` / `Glm5DecoderLayerCompat`。后者要求 attention 明确返回 `(attention_output, attention_weights, topk_indices)`，缺第三项则 `ValueError`；`RegionMarkerWrapper` / `CopyLayerWrapper` 与 MTP patch 协同避免重复包装。

6. **`mlapo` / `mlapo_quant` 返回值扩展**：返回值由三元组扩展为 `(q_states, kv_c_normed, k_rot, qa_normed)` 四元组；当 `q_lora_rank` 不存在时 `qa_normed` 用空 last-dim tensor 作为 shape-only 占位，调用侧再转为 `None`，从而避免 indexer wrapper 重复执行 `q_a_proj` 与 `q_a_layernorm`。

5. **DSA Indexer 融合语义算子**：新增 `torch.ops.tensor_cast.dsa_indexer.default`，将 query/key projection、RoPE、cache 写入、score 计算、top-k selection 收拢为单个可 trace 算子；输入包括 `hidden_states`、`qa_normed`、`cos`/`sin`、`indexer_cache`、`slot_mapping`、`block_tables`、`seq_lens`、`wq_b_weight`、`wk_weight`、`weights_proj_weight`、`k_norm_weight`、`num_heads`、`head_dim`、`qk_rope_head_dim`、`topk_limit`；`indexer_cache` 声明为 mutable argument；返回 `topk_indices`，shape 为 `(batch, seq_len, min(topk_limit, active_seq_len))`，FakeTensor/`torch.compile` 路径下使用静态 `topk_limit` 上限，不从 `seq_lens` 抽取 Python int。

7. **性能模型 bucket 拆分（原文截断）**：`tensor_cast/performance_model/__init__.py` 新增 `_estimate_dsa_indexer_breakdown(...)`，将 DSA Indexer 拆分为 compute / memory bucket，包括 `qa_normed @ wq_b`（q projection MMA）、`hidden_states @ wk`（k projection MMA）、`hidden_states` 开头的 head routing projection MMA 等（原文第 3 条起被截断）。

---

## 【关键机制与数据】

### 数据流（GLM-5.2 完整路径）
1. **Attention 输出三元组**：GLM5 attention forward 始终返回 `(attn_output, attn_weights, next_topk_indices)`。当下一层为 `shared` 时，第三项传递当前 layer 的 active top-k；`full` 层转发新生成的 top-k，连续 `shared` 链原样转发复用的 top-k；后续不再需要时第三项置 `None`。基类 MLA 默认输出仍为二元 `(attn_output, attn_weights)`。
2. **跨层 IndexShare 解析**：`get_glm5_indexer_types(...)` 与 `resolve_glm5_indexer_source_layer(...)` 解析并校验 `indexer_types`；配置长度不足、未知类型、无前序 `full` source 的 `shared` 层均抛 `ValueError`。
3. **MTP 兼容**：主 decoder stack 之外的 MTP proposal block 无法消费主栈 `prev_topk_indices`，因此 `extend_glm5_indexer_types_for_mtp(...)` 为启用 IndexShare 的 GLM5.2 在每个新增 MTP block 上追加 `full`，空列表或 MTP=0 时保持不变。
4. **Repetition 共存**：启用 IndexShare 时 `maybe_reuse_layers(...)` 仅复用无跨层状态的 MLP 子模块（如标准 `.mlp`）；`CopyLayerWrapper` 只能重放首个 tensor 输出，无法保留 `topk_indices`；未启用 IndexShare 的 GLM5 沿用既有完整 layer 复用行为。
5. **DSA Indexer cache dtype 推导**：FP8 attention 下 indexer cache 使用 FP8 dtype，非 FP8/GLM5 bf16 路径下保持 bf16/fp16 语义，以使性能模型与内存估算贴近实际路径。
6. **RMSNorm pattern matching**：原有 pattern 将 `eps` 固定在闭包内，导致非默认 epsilon 无法稳定融合到 `tensor_cast.rms_norm`、`tensor_cast.add_rms_norm`、`tensor_cast.add_rms_norm2`；本方案补齐该 pattern matching 能力。

### 路径覆盖（dsa_indexer 语义算子）
- **DeepSeek-V3.2 FP8 路径**：query/key projection → RoPE → `rotate_activation` → activation quantization → FP8 key cache / scale cache 写入 → FP8 index score → top-k selection。
- **GLM5 / BF16 路径**：移除 FP8 特有的 activation rotation、quantization、scale cache、FP8 score shaping；使用 bf16/fp16 cache scoring、head weight mixing、head reduction、top-k selection。

> 注：原文章节"性能模型设计"在列出前两条 bucket 后被截断，后续 compute/memory bucket 拆分细节原文未给出。

---

## 【表格解读】

**修订记录表（逐字还原）：**

| 日期 | 修订版本 | 修改描述 | 作者 | RFC文档 |
| -- | -- | -- | -- | -- |
| 2026-04-30 | 1.0 | 初稿完成，归档 TensorCast 适配 GLM5 系列模型及 Sparse MLA/DSA Indexer 融合算子设计 | minghang_c | - |
| 2026-07-22 | 1.1 | 补充 GLM-5.2 IndexShare 执行、cache 分配、MTP 和层复用设计 | minghang_c | - |
| 2026-07-22 | 1.2 | 补充旧版 Transformers 的 IndexShare 兼容 wrapper 与 MTP/repetition 修正 | minghang_c | - |
| 2026-07-23 | 1.3 | 澄清连续 shared layer 的 IndexShare top-k 转发语义 | minghang_c | - |

**逐行解读：**
- **2026-04-30 / v1.0**：文档初始版本，作者 minghang_c，覆盖范围为 GLM5 全系列模型适配以及 Sparse MLA / DSA Indexer 融合算子设计；RFC 文档暂未提供（标记为 `-`）。
- **2026-07-22 / v1.1**：在同一日期下首次扩展，引入 GLM-5.2 IndexShare 的执行机制、cache 分配、MTP 集成以及层复用设计，体现 IndexShare 已成为本设计的核心增量。
- **2026-07-22 / v1.2**：同日再次修订，聚焦旧版 Transformers 的 IndexShare 兼容 wrapper（`Glm5ModelCompat` / `Glm5DecoderLayerCompat`），并修正 MTP 与 repetition 在 IndexShare 场景下的交互。
- **2026-07-23 / v1.3**：仅隔一日的澄清性修订，明确连续 `shared` layer 链中 `topk_indices` 的原样转发语义，避免性能模型高估 indexer 时延。

除修订记录外，原文未给出参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无 LaTeX 数学公式。**

原文中出现的形如公式的伪代码/运算表达式主要为性能模型 bucket 拆分描述：

- `qa_normed @ wq_b` —— q projection MMA：表示 `qa_normed`（MLA 低秩 query 投影并归一化后的 activation）与 `wq_b_weight`（indexer 的 query 投影权重）之间的矩阵乘累加，作为 DSA Indexer q 路径计算 bucket。
- `hidden_states @ wk` —— k projection MMA：表示 `hidden_states` 与 `wk_weight`（indexer 的 key 投影权重）的矩阵乘累加，对应 k 路径计算 bucket。
- `hidden_stat[es] @ ...`（原文被截断）—— head routing projection MMA：表示以 `hidden_states` 作为输入的 head routing 权重投影，原文在第 3 条起未给出完整表达式。

返回 shape 表达式：
- `(batch, seq_len, min(topk_limit, active_seq_len))` —— DSA Indexer 输出 `topk_indices` 的张量形状语义：`batch` 维为批大小，`seq_len` 维为请求内 token 数，第三维取 `topk_limit`（DSA indexer top-k 上限）与 `active_seq_len`（实际可用序列长度）的较小者，避免超出有效 KV 范围。

---

## 【关联】

依据原文，本设计与以下既有特性与模块存在直接关联：

- **DeepSeek-V3.2 sparse MLA 路径**：作为复用基线。GLM5 不新增并行 MLA 实现，而是通过 model profile 接入既有 `DeepseekSparseAttention` / `DeepseekSparseAttentionIndexer` wrapper；配置差异在 wrapper 边界收敛。
- **`DeepseekV32Config` 兼容逻辑**：保留窄范围的 `index_topk -> topk_limit` 兼容，但仅服务于旧 DeepSeek JSON fixture，不作为 GLM5 真实运行路径依赖。
- **`tensor_cast/transformers/transformations.py`（MTP layer type 扩展）**：当 HF config 同时存在 `layer_types` 与 `mlp_layer_types` 时，原有"将整个列表作为元素追加"的扩展方式会破坏结构；本方案改为复制最后一个已有 layer type 作为新增 MTP layer 的类型，以正确支持 GLM5 的双 layer type 列表结构。
- **`tensor_cast/transformers/transformations.py`（`patch_mla(...)`、`maybe_reuse_layers(...)`）**：将 source layer index、`indexer_type`、`skip_topk`、`next_skip_topk` 写入 GLM5 attention wrapper，并依据 IndexShare 启用与否决定 layer 复用粒度。
- **`tensor_cast.mlapo.default` / `tensor_cast.mlapo_quant.default`**：返回值扩展为四元组后，将 `qa_normed` 透传给 indexer，避免重复计算。
- **`tensor_cast.multihead_latent_attention.default` / `tensor_cast.multihead_latent_attention_quant.default`**：作为下游接收 `topk_limit` 与 `topk_indices` 的 sparse attention 语义算子，在性能模型中纳入 mask/top-k 长度约束。
- **`tensor_cast.rms_norm` / `tensor_cast.add_rms_norm` / `tensor_cast.add_rms_norm2`**：RMSNorm pattern matching 补齐的下游目标融合算子，覆盖非默认 epsilon 场景。
- **`RegionMarkerWrapper` / `CopyLayerWrapper`**：与 MTP patch 协同，避免重复包装；`CopyLayerWrapper` 因不可执行 decoder/MTP block 在 IndexShare 场景被排除复用。
- **内部链接**：原文未提供任何 markdown 内部链接。

---

## 【使用方法】

原文未给出独立的"使用方法/启用方式/配置项/命令"小节，但分散在方案描述中可归纳出以下启用与配置要点（均来自原文描述，非外推）：

1. **HF 模型类型识别**：HF config `model_type` 须设置为 `"glm_moe_dsa"`，并在 config 中正确定义 `GlmMoeDsaAttention`、`GlmMoeDsaMoE`、`GlmMoeDsaDecoderLayer` 对应的子结构。
2. **GLM-5.2 IndexShare 启用**：在 HF config 中提供 `indexer_types` 列表，每项取值为 `"full"` 或 `"shared"`；要求 `shared` 项之前存在至少一个 `"full"` 项，否则 `resolve_glm5_indexer_source_layer(...)` 抛 `ValueError`。
3. **DSA indexer top-k 配置**：
   - DeepSeek-V3.2 路径：使用 `topk_limit`（attention config / indexer config / 显式参数均可，按 `_resolve_sparse_topk_limit(...)` 优先级解析）。
   - GLM5 路径：使用 `index_topk`，由 `_resolve_sparse_topk_limit(...)` 自动收敛为内部 `topk_limit`。
4. **MTP 启用**：启用 MTP 时，`transformations.py` 会自动按 `extend_glm5_indexer_types_for_mtp(...)` 在 `indexer_types` 末尾追加 `"full"`，无需手工配置；空列表或 MTP=0 时不追加。
5. **Repetition 行为**：当 `indexer_types` 启用 IndexShare 且 layer 含标准 `.mlp` 子模块时，`maybe_reuse_layers(...)` 仅复用 MLP；不含 `.mlp` 时回退到既有完整 layer 复用。未启用 IndexShare 的 GLM5 沿用既有完整 layer 复用行为。
6. **Transformers 兼容 wrapper**：通过 `patch_glm5_model(...)` 自动按原生 decoder 是否支持 `prev_topk_indices` 决定是否安装 `Glm5ModelCompat`；已具备该接口的版本不会被改写执行路径。
7. **Index dtype 推导**：FP8 attention 场景下 indexer cache 自动使用 FP8 dtype；非 FP8 / GLM5 bf16 路径下保持 bf16/fp16 语义，dtype 由 attention quantization 配置推导。

> 注：原文章节"性能模型设计"在列出前两条 bucket 后被截断，原文未给出后续 bucket 拆分细节，也未提供完整的命令行/配置示例。
```
