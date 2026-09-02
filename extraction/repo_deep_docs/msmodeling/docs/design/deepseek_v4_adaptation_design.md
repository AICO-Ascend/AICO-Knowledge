# 特性设计：TensorCast 适配 DeepSeek-V4 模型（Flash/Pro）

> 仓 `msmodeling` · 路径 `docs/design/deepseek_v4_adaptation_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/deepseek_v4_adaptation_design.md

# TensorCast 适配 DeepSeek-V4 模型 — 一体化深度解读

## 【定位】
本文档解决 DeepSeek-V4 (Flash/Pro) 模型接入 TensorCast 仿真工具链的能力补齐问题——V4 在 V3/V3.2 基础上新增了 Head Compression (HC) 机制、分层 KV 压缩、共享 KV attention、Lightning Indexer、Hash 路由 MoE、Clamped SwiGLU 等关键架构变化，导致原有 V3.2 路径无法直接复用,本文档设计了一整套语义算子、模型画像与性能模型以使 TensorCast 能正确编译和仿真 V4 模型。

---

## 【技术要点】

1. **五层适配架构**：模型注册层 (`deepseek_v4` profile)、HC 语义算子层、KV 压缩算子层、稀疏注意力算子层、MoE 路由算子层。
2. **HC 机制 4 个语义算子**：`hc_pre_inv_rms`、`hc_pre_sinkhorn`、`hc_post`、`hc_head`，完成 `[B,S,D] ↔ [B,S,Hc,D]` 双向展开/还原；Sinkhorn iterations 与 weighted reduction 合并进同一算子保证成本统计算法一致。
3. **分层 KV 压缩策略 (per-layer compress_ratios)**：仅支持 ratio ∈ {0, 4, 128} 三种取值，分别对应 sliding_attention / compressed_sparse_attention / heavily_compressed_attention 三种层类型；`compressor` + `scatter_nd_update_mla` 实现 KV 写入与压缩。
4. **共享 KV attention + Lightning Indexer**：`sparse_attn_sharedkv`（online softmax block=64, 支持 attention sink）替代 V3 的 MLA kv_b 分解；ratio=4 层配 `quant_lightning_indexer`，输出宽度使用动态 `min(topk_limit, active_seq_len)`。
5. **MoE 路由双模式**：非 hash 层用 `moe_gating_top_k`、hash 层用 `moe_gating_top_k_hash`（token-id based routing, 层数由 `num_hash_layers` 控制，默认 0）；expert activation 用 `v4_clamped_swiglu` = `clamp(gate) * SiLU(up)`，当 `swiglu_limit > 0` 时启用。
6. **并行维度差异**：O projection 使用独立的 `o_proj_tp_group`，与 attention 的 `tp_group` 可分离，需在 TP plan 中单独处理；约束 `o_proj_tp_group.world_size ≤ o_groups`，否则报错。

---

## 【关键机制与数据】

### HC 流程
- **HC Pre**：`hc_pre_inv_rms` + `hc_pre_sinkhorn` 串联，将 hidden state 从 `[B,S,D]` 经 Sinkhorn-based 混合展开为 `[B,S,Hc,D]`，生成 `pre`、`post`、`comb` 三组张量，最后用 `pre` 做 weighted sum reduction 回到 `[B,S,D]`。
- **HC Post** (`hc_post`)：输出公式为 `post.unsqueeze(-1) * x + sum(comb * residual, dim=hc)`，residual 已被折叠进算子输出，caller 不再重复累加。
- **HC Head** (`hc_head`)：模型输出层将 `[B,S,Hc,D]` 还原为 `[B,S,D]`，包含 RMS + linear + sigmoid + weighted reduction。
- **HC 形状与算法参数**：`hc_mult`、`hc_sinkhorn_iters`、`hc_eps` 三个配置项控制 shape 与 Sinkhorn 数值。

### KV 压缩与注意力链
- **Compressor** (`tensor_cast.compressor`)：对 hidden_states 执行 `wkv`、`wgate` 投影生成 coarse-grained KV stream；对最后 `rope_head_dim` 维度执行 RoPE（主压缩器）或 Hadamard+FP4（索引压缩器），写入 kv_cache 并返回 `compressed_kv`。
- **成本模型分阶段**：prefill 按 `query_len` 分段统计完整压缩成本；decode 单 token 成本由 `start_pos` 是否整除 compress_ratio 决定是否压缩（原文）。
- **Scatter KV 写入** (`tensor_cast.scatter_nd_update_mla`)：prefill short (`sl ≤ W`) 单次 scatter；prefill split tail (`sl > W`) 两次 scatter 处理循环缓冲语义；decode 单行 scatter（原文）。
- **Sparse Attention SharedKV** (`tensor_cast.sparse_attn_sharedkv`)：有效 KV 长度由 `topk_indices.shape[-1]` 限制；每个 iteration 两个 GEMM（Q*K^T 和 S*V）+ per-iter scalar work（max/reduce/scale）+ 按实际 topk 宽度统计的 KV gather traffic。

### Lightning Indexer (`quant_lightning_indexer`)
- **Wrapper 已执行**：RoPE 后的 `q_states`、`weights_proj` 输出的 `weights`、`indexer_cache`。
- **算子内语义**：`rotate_activation(q)` + `fp4_act_quant(q)` → `einsum("bshd,btd->bsht", q, kv_cache)` → `relu + weighted sum across heads` → `all_reduce_sum`（TP > 1 时）→ prefill 加 causal mask (`where(causal_mask, -inf, 0)`) → `topk(min(topk_limit, active_seq_len))` → prefill validity_mask postprocess / decode offset（原文）。

### MoE 路由
- **`moe_gating_top_k`**：bias add（可选）→ topk on scores → weight gather from pre-bias scores → normalize（当 `score_func != softmax`）→ `route_scale` multiply。
- **`moe_gating_top_k_hash`**：`tid2eid[input_ids]` 查表 → weight gather from scores → normalize（可选）→ `route_scale` multiply。
- **`v4_clamped_swiglu`**：公式为 `clamp(gate) * SiLU(up)`（原文，区别于标准 `SiLU(gate) * up`）。

### 性能模型注册
位置：`tensor_cast/performance_model/builtin_model/deepseek_v4.py`（原文），为所有 V4 新算子提供成本统计。

### 仿真输入参数（原文命令）
- `--context-length 65500`（context 长度）
- `--query-length 1`（query 长度）
- `--num-queries 80`（query 数量）
- `--tp-size 4`、`--dp-size 16`、`--ep-size 64`、`--num-devices 64`
- 设备：`ATLAS_800_A3_752T_128G_DIE`
- `--compile` 启用编译

> 注：原文第 4 章「测试设计」在 4.1「V4 配置解析」与「HC 语义算子」两个单元测试点之后出现 `**` 截断,后续内容未在原文中给出。

---

## 【表格解读】

### 表 A — 修订记录（原文逐字还原）

| 日期 | 修订版本 | 修改描述 | 作者 | RFC 文档 |
| -- | -- | -- | -- | -- |
| 2026-06-03 | 1.0 | 初稿完成，归档 TensorCast 适配 DeepSeek-V4 模型的设计与实现 | — | — |

解读：本文为初稿归档版本，日期标注 2026-06-03，归属「TensorCast 适配 DeepSeek-V4 模型（Flash/Pro）」特性,无 RFC 关联文档。

### 表 B — V4 分层压缩策略（原文逐字还原）

| ratio | 层类型 | KV 缓存 | 注意力 |
|-------|--------|---------|--------|
| 0 | sliding_attention | 滑动窗口 KV | 窗口 top-k |
| 4 | compressed_sparse_attention | 窗口 + 索引压缩 KV | 窗口 + indexer top-k |
| 128 | heavily_compressed_attention | 窗口 + 重度压缩 KV | 窗口 + 压缩 top-k |

解读：V4 通过 `compress_ratios` 配置为每一层选择一种 KV 缓存与注意力模式。ratio 越大,压缩越重：
- ratio=0 走最简路径,只有滑动窗口 KV,注意力只取窗口内的 top-k；
- ratio=4 引入 Lightning Indexer,在窗口基础上叠加索引式稀疏选择（indexer top-k）；
- ratio=128 走重度压缩路径,注意力窗口内的 top-k 从压缩 KV 流中检索。
配置约束（原文）：`compress_ratios` 必须定义、长度不少于 `num_hidden_layers`、仅支持 ratio ∈ {0, 4, 128}、`layer_types` 必须与 `compress_ratios` 一致。

### 表 C — V4 性能模型算子成本（原文逐字还原）

| 算子 | 主要成本 |
|------|----------|
| `hc_pre_inv_rms` | bf16→fp32 cast + RMS inverse |
| `hc_pre_sinkhorn` | Sinkhorn iterations + weighted reduction |
| `hc_post` | HC 维度 contraction + residual fold |
| `hc_head` | RMS + linear + sigmoid + weighted reduction |
| `scatter_nd_update_mla` | KV 行写入 |
| `compressor` | 投影 MMA + softmax + norm + RoPE |
| `quant_lightning_indexer` | FP4 quant + einsum + all_reduce + topk |
| `sparse_attn_sharedkv` | GEMM + online softmax + KV gather |
| `moe_gating_top_k` | bias add + topk + gather + normalize |
| `moe_gating_top_k_hash` | hash lookup + gather + normalize |
| `v4_clamped_swiglu` | clamp + SiLU + multiply |

解读：每个 V4 语义算子都有对应的成本模型条目,覆盖从 HC 包装（4 算子）、KV 写入与压缩（2 算子）、稀疏注意力与 indexer（2 算子）到 MoE 路由与 expert activation（3 算子）的完整链路。性能模型文件位于 `tensor_cast/performance_model/builtin_model/deepseek_v4.py`（原文）。

---

## 【公式解读】

### 公式 1 — HC Post 输出（原文）
```
post.unsqueeze(-1) * x + sum(comb * residual, dim=hc)
```
符号说明：
- `post`：HC Pre 阶段生成的 post 系数张量，shape `[B, S, Hc]`（原文未明确标 shape,从 `hc_pre_*` 流程推断）；
- `x`：经过 HC Pre weighted reduction 后回到 `[B, S, D]` 的 hidden state；
- `unsqueeze(-1)`：在最后一个维度插入维度使 `post` 广播对齐到 `x` 的 `[B, S, 1, D]`；
- `comb`：HC Pre 阶段生成的组合系数张量，shape `[B, S, Hc]`；
- `residual`：来自 HC Pre 包装前的输入残差,shape `[B, S, Hc, D]`（与 HC 展开后的隐藏张量对齐,原文描述 residual 被折叠进输出）；
- `sum(..., dim=hc)`：沿 hc 维度（HC 头维度）做 reduction,得到 `[B, S, D]` 输出。
作用：表达 HC Post 算子的输出语义——`post` 对当前 hidden state 加权、`comb` 对历史 residual 加权,二者合并后折叠回原始 D 维,避免 caller 再做 `+ residual`。

### 公式 2 — qK score 计算（原文）
```
einsum("bshd,btd->bsht", q, kv_cache)
```
符号说明：
- `q`：rotate_activation + fp4_act_quant 后的 query 张量,shape `[B, S, Hq, D]`（b=batch, s=seq, h=head, d=dim）；
- `kv_cache`：索引压缩 KV cache,shape `[B, T, D]`（t=压缩后时间维度）；
- `bshd`：q 的下标记号；
- `btd`：kv_cache 的下标记号；
- `bsht`：输出的下标记号——在 (s, t) 维度做内积,得到 `[B, S, Hq, T]` 的 qK 分数。
作用：表达 Lightning Indexer 中 query 与压缩 KV 的匹配得分计算。

### 公式 3 — Indexer top-k 选择（原文）
```
topk(min(topk_limit, active_seq_len))
```
符号说明：
- `topk_limit`：上层配置 `topk_limit`/`index_topk` 指定的最大 top-k 上限；
- `active_seq_len`：当前实际活跃序列长度（prefill 为 `query_len`,decode 为 1 + 历史 KV）；
- `min(...)`：保证 top-k 不超过实际可选项数；
作用：表达输出索引宽度的动态选择策略，避免在短序列场景下请求超出可用候选数的 top-k。

### 公式 4 — V4 Clamped SwiGLU（原文）
```
clamp(gate) * SiLU(up)
```
对比标准 SwiGLU：`SiLU(gate) * up`（原文）。
符号说明：
- `gate`：expert gate 投影输出；
- `up`：expert up 投影输出；
- `clamp(gate)`：将 gate 裁剪到 `[-swiglu_limit, swiglu_limit]`（原文：`swiglu_limit > 0` 时启用）；
- `SiLU(up)`：对 up 应用 SiLU 激活；
作用：表达 V4 expert activation 的核心差异——clamp 作用于 gate 而非 SiLU 之后,且与 SiLU(up) 相乘,顺序与标准 SwiGLU 完全不同。

### 公式 5 — Prefill causal mask 注入（原文）
```
mask += where(causal_mask, -inf, 0)
```
符号说明：
- `mask`：Lightning Indexer 当前的 qK 分数张量；
- `causal_mask`：prefill 阶段使用的因果掩码,shape 与 `[B, S, Hq, T]` 对齐；
- `where(causal_mask, -inf, 0)`：对不允许位置产生 -inf,允许位置产生 0；
- `+=`：原位累加。
作用：保证 prefill 阶段 Lightning Indexer 的 top-k 选择严格遵守因果性（decode 阶段不执行该步骤,改为 offset 调整）。

---

## 【关联】

本文未给出文末内部链接（"内部链接: (无)"）,但文档内容中明确提及以下上下游关系：

- **V3/V3.2 TensorCast 路径（上游）**：本文是对 V3.2 sparse MLA 抽象的扩展,设计原则是"尽量复用既有 V3.2 sparse MLA 抽象,只在新语义算子、HC wrapping、compressor 和 grouped O projection 等处补齐差异"。V4 直接复用 V3.2 路径会失败（背景描述列出 7 类缺失），本文即补齐路径。
- **Hugging Face `AutoConfig`（上游识别机制）**：`model_type="deepseek_v4"` 被 `AutoConfig` 识别后,由新增的 `tensor_cast/transformers/builtin_model/deepseek_v4.py` model profile 接入既有 transformation pipeline。
- **`DeepseekV3Config`（父类配置）**：`DeepseekV4Config` 子类化 `DeepseekV3Config`,在父类基础上新增 V4 特有字段（`compress_ratios`/`layer_types`、`topk_limit`/`index_topk`、`num_hash_layers`、`hc_mult`/`hc_sinkhorn_iters`/`hc_eps`、`o_groups`/`o_lora_rank`、`score_func`/`route_scale`、`expert_dtype`、`swiglu_limit`/`compress_rope_theta`）。
- **既有 transformation pipeline（下游消费方）**：通过 `patch_method=patch_method_for_deepseek_v4` 与 `moe_gate_router=route_deepseek_v4_gate` 将 V4 attention/MoE/HC 模块接入既有 transformation pipeline。
- **`tensor_cast` 命名空间下的算子库（下游执行）**：`tensor_cast.hc_pre_inv_rms`、`tensor_cast.hc_pre_sinkhorn`、`tensor_cast.hc_post`、`tensor_cast.hc_head`、`tensor_cast.compressor`、`tensor_cast.scatter_nd_update_mla`、`tensor_cast.sparse_attn_sharedkv`、`tensor_cast.quant_lightning_indexer`、`tensor_cast.moe_gating_top_k`、`tensor_cast.moe_gating_top_k_hash`、`tensor_cast.v4_clamped_swiglu`、`tensor_cast.rms_norm` 等算子为 V4 trace 提供关键语义块（原文 3.3 列出 trace 应体现的语义块）。
- **并行策略（横切关注点）**：TP plan 需单独处理 `o_proj_tp_group`,与 attention 的 `tp_group` 分离；约束 `o_proj_tp_group.world_size ≤ o_groups`。

---

## 【使用方法】

### 运行环境（原文）
- Python ≥ 3.10
- PyTorch ≥ 2.5（需支持 `torch.compile`）
- 需要 Hugging Face 连接

### 仿真命令（原文）
```bash
python -m cli.inference.text_generate "deepseek-ai/DeepSeek-V4-Flash" \
  --device ATLAS_800_A3_752T_128G_DIE \
  --num-devices 64 \
  --tp-size 4 \
  --dp-size 16 \
  --ep-size 64 \
  --context-length 65500 \
  --query-length 1 \
  --num-queries 80 \
  --compile
```

### 配置约束（原文 3.4 逐条）
1. V4 必须定义 `compress_ratios`,每个 ratio 值必须为 0、4 或 128。
2. `layer_types` 必须与 `compress_ratios` 一致。
3. `o_proj_tp_group.world_size` 必须 ≤ `o_groups`,否则抛出错误。
4. Hash routing 层数由 `num_hash_layers` 控制,默认 0。
5. `swiglu_limit > 0` 时使用 `v4_clamped_swiglu`,否则使用标准 SiLU。

### 模型识别机制（原文）
TensorCast 通过 HF `AutoConfig` 识别 `model_type="deepseek_v4"`,加载 V4 原生配置,并通过 model profile 将 V4 attention/MoE/HC 模块接入既有 transformation pipeline（原文 3.2）。

### Trace 应体现的关键语义块（原文 3.3）
- `tensor_cast.hc_pre_inv_rms.default` / `tensor_cast.hc_pre_sinkhorn.default`
- `tensor_cast.rms_norm.default`
- `tensor_cast.DeepseekV4SparseAttention` wrapper 内：`tensor_cast.scatter_nd_update_mla.default`、`tensor_cast.compressor.default`（ratio > 0）、`tensor_cast.quant_lightning_indexer.default`（ratio=4）、`tensor_cast.sparse_attn_sharedkv.default`
- `tensor_cast.hc_post.default`
- FFN 阶段 `tensor_cast.hc_pre_*`
- `tensor_cast.moe_gating_top_k.default` / `tensor_cast.moe_gating_top_k_hash.default`

### 测试（原文）
原文第 4 章「测试设计」已列出两类单元测试点（V4 配置解析、HC 语义算子），但文本在 4.1 节 `**` 处截断,后续测试用例与集成测试在原文中未给出（标注："原文未涉及——原文 4 章测试设计在 4.1 节末尾截断"）。
