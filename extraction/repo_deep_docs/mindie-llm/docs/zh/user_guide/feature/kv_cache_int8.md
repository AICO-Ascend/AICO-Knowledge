# KV Cache int8

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/kv_cache_int8.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/kv_cache_int8.md

# KV Cache int8 文档深度解读

## 【定位】

本文档描述了在昇腾推理引擎 MindIE-LLM 中将 KV Cache 量化至 int8 的能力，旨在**通过降低 KV Cache 显存占用，减少长序列场景下的重计算触发次数，从而提升吞吐**。

---

## 【技术要点】

1. **量化对象与位宽**：将 attention 中的 **k cache 与 v cache 量化为 8 bit（C8）**，其余权重走 W8A8 路径；不修改 q_proj 的相关字段，仅在 k_proj、v_proj 上新增 kv_cache_scale / kv_cache_offset。
2. **硬件与模型约束**（原文 NOTE）：
   - 仅 **Atlas 800I A2 推理服务器** 支持；
   - 仅支持与 **W8A8 搭配使用**；
   - 仅支持 **LLaMA3.1-70B、Qwen2-72B、Qwen2.5-72B-Instruct**；
   - 仅支持 **float16** 数据类型。
3. **新增描述字段**：在量化权重描述文件 `quant_model_description_w8a8.json` 中新增 `kv_cache_type` 字段（值为 `"C8"`），并对每个 kv linear 引入 `kv_cache_scale` 与 `kv_cache_offset` 两个 W8A8 类型字段。
4. **缩放/偏移因子派生**：推理时基于 `kv_cache_scale` 与 `kv_cache_offset` 两个权重，**派生出 8 个因子**——`k_quant_scale / k_dequant_scale / v_quant_scale / v_dequant_scale` 与 `k_quant_offset / k_dequant_offset / v_quant_offset / v_dequant_offset`。
5. **因子用途分工**：`quant_scale` 与 `quant_offset` 负责把 k/v 特征量化为 int8；`dequant_scale` 与 `dequant_offset` 负责把 **Paged Attention 输出**反量化回浮点类型。
6. **量化参数张量形状**：kv_cache_scale 与 kv_cache_offset 的 dtype 与原权重保持一致（float16 或 bfloat16），shape 均为 `[kv_head_num * kv_head_dim]`，即**按 head×head_dim 维度逐头/逐通道保存一份**。

---

## 【关键机制与数据】

### 工作原理（原文："推理时会基于这两个权重，推导出……"）

- **量化方向（FP → INT8）**：在 attention 计算之前，利用 `quant_scale / quant_offset` 将 k、v 特征从浮点映射为 int8，缓存入 KV Cache。
- **反量化方向（INT8 → FP）**：在 **Paged Attention** 注意力输出阶段，利用 `dequant_scale / dequant_offset` 将结果还原为浮点参与后续计算。
- 这一"存的时候量化、读的时候反量化"的分工，使得 KV Cache 的存储位宽从 float16 降低到 int8，从而**直接降低显存占用**。
- 显存降低后，在相同显存预算下**可缓存更长的序列**，因此**减少重计算触发次数**（即减少 KV Cache 淘汰后需要重新前向计算的概率），进而提升整体吞吐。

### 量化权重的目录与文件结构（原文）

```
config.json
quant_model_weight_w8a8.safetensors   ← 权重文件
quant_model_description_w8a8.json     ← 权重描述文件
tokenizer_config.json
tokenizer.json
tokenizer.model
```

- `quant_model_weight_w8a8.safetensors`：量化后的权重文件。
- `quant_model_description_w8a8.json`：权重描述文件，包含 dtype、scale/offset 等元信息。
- 其余为模型推理所需配置/tokenizer 文件。

### 量化描述 JSON 内容（原文逐字保留）

```json
{
  "model_quant_type": "W8A8",
  "kv_cache_type": "C8",
  "model.embed_tokens.weight": "FLOAT",
  "model.layers.0.self_attn.q_proj.weight": "FLOAT",
  "model.layers.0.self_attn.k_proj.weight": "FLOAT",
  "model.layers.0.self_attn.k_proj.kv_cache_scale": "W8A8",
  "model.layers.0.self_attn.k_proj.kv_cache_offset": "W8A8",
  "model.layers.0.self_attn.v_proj.weight": "FLOAT",
  "model.layers.0.self_attn.v_proj.kv_cache_scale": "W8A8",
  "model.layers.0.self_attn.v_proj.kv_cache_offset": "W8A8"
}
```

观察要点（原文）：
- q_proj 不带 kv_cache_scale/offset，因为**仅对 k/v 进行 cache 量化**；
- k_proj / v_proj 的 `weight` 本身仍标注为 FLOAT（即走 W8A8 的权重量化路径），新增的是**激活侧**的 scale/offset。

### 性能/收益机制（原文）

> "通过减少KV Cache的显存占用，在显存受限场景（如长序列场景）下，可以减少重计算触发次数以提升吞吐。"

原文未给出具体的吞吐提升百分比、显存节省比例或时延数据；上述结论是基于"显存降低 → 可缓存更长上下文 → 重算减少 → 吞吐提升"这一推理链的定性描述。

---

## 【表格解读】

### 表 1（原文逐字还原）：float16 权重量化后 dtype 及 shape 信息

| Tensor信息 | kv_cache_scale | kv_cache_offset |
|---|---|---|
| dtype | float16 | float16 |
| shape | [kv_head_num * kv_head_dim] | [kv_head_num * kv_head_dim] |

**逐行解读**：
- **dtype 行**：当原始权重为 float16 时，新增的 `kv_cache_scale` 与 `kv_cache_offset` 也保持为 **float16**，确保量化因子精度与权重一致。
- **shape 行**：两个张量的形状均为 `[kv_head_num * kv_head_dim]`，即**每个 KV head 的每个 head_dim 都对应一份独立的 scale 与 offset**，而非整层共享一个全局 scale。这是典型的 per-channel / per-head 量化方案。

### 表 2（原文逐字还原）：bfloat16 权重量化后 dtype 及 shape 信息

| Tensor信息 | kv_cache_scale | kv_cache_offset |
|---|---|---|
| dtype | bfloat16 | bfloat16 |
| shape | [kv_head_num * kv_head_dim] | [kv_head_num * kv_head_dim] |

**逐行解读**：
- **dtype 行**：当原始权重为 bfloat16 时，scale/offset 同样为 **bfloat16**，与权重 dtype 保持一致。
- **shape 行**：与表 1 完全一致，仍是 per-head × head_dim 的逐通道量化。
- **对比表 1 与表 2**：两份表格的 shape 完全相同，差异仅在 dtype 与上游权重的 dtype 对齐——这表明 kv_cache_scale/offset 的存储类型**严格跟随权重的浮点精度**，而非固定为某一种。

---

## 【公式解读】

原文无公式。

仅存在量化方向的定性描述：
- 量化：`quant_scale / quant_offset` 将 k、v 特征量化为 int8；
- 反量化：`dequant_scale / dequant_offset` 将 Paged Attention 的输出反量化为浮点。

但原文**未给出任何线性/仿射量化公式（如 `q = round((x - offset)/scale)` 等）**，因此本节不做臆造。

---

## 【关联】

根据文档上下文，KV Cache int8 与以下特性/模块存在耦合关系：

1. **W8A8 量化**：本文档明确指出 KV Cache int8 **必须与 W8A8 搭配使用**，因此上游权重与激活的量化基线是 W8A8。
2. **量化权重描述文件 `quant_model_description_w8a8.json`**：通过新增 `kv_cache_type` 字段（值为 `C8`）与 kv linear 的 `kv_cache_scale / kv_cache_offset` 字段来表达本能力，与 W8A8 的描述体系共用同一 JSON。
3. **Paged Attention**：反量化阶段作用于 Paged Attention 的输出，说明 KV Cache int8 与 **PagedAttention 内存管理** 模块紧耦合——int8 缓存会作为 Paged Attention 的输入源。
4. **硬件后端**：仅支持 Atlas 800I A2 推理服务器，说明该特性绑定到特定的昇腾硬件后端。
5. **支持模型列表**：LLaMA3.1-70B、Qwen2-72B、Qwen2.5-72B-Instruct，表明其实现依赖于这些模型的特定结构（如 GQA、RoPE、head 配置等）。

文末未提供内部链接，但根据描述可推断该文档属于「量化特性」系列，与 W8A8、KV Cache int4 等相邻文档共享同一描述框架（model_quant_type / kv_cache_type 字段命名风格）。

---

## 【使用方法】

**原文未涉及** KV Cache int8 的具体启用命令、环境变量、配置文件修改或 API 调用方式。

文档仅说明了以下**前置条件类信息**（属于启用约束，而非操作步骤）：

1. **硬件**：使用 Atlas 800I A2 推理服务器。
2. **量化组合**：必须配合 **W8A8** 一起使用（即先生成 W8A8 量化权重）。
3. **模型范围**：仅支持 LLaMA3.1-70B、Qwen2-72B、Qwen2.5-72B-Instruct。
4. **数据类型**：仅支持 float16。
5. **产物校验**：通过检查 `quant_model_description_w8a8.json` 中是否存在 `kv_cache_type: "C8"` 字段、以及 k_proj / v_proj 是否携带 `kv_cache_scale` / `kv_cache_offset` 字段，可确认 KV Cache int8 已生效。

具体的 `mindie-llm` 启动命令、参数名称（如是否通过 `--kv-cache-type` 或 service config 等开关启用）**在原文中未给出**，需参考 MindIE-LLM 的部署/量化配置相关文档获取。

## 图文联合解读

- `kv_cache_int8.png`: 图示展示KV Cache int8数据流：float16的K/V特征经量化转为int8，再由ReshapeAndCache算子写入K/V Cache（int8），最后经Paged Attention算子结合反量化得到float16结果。论证了K/V缓存全链路int8存取+反量化恢复的计算路径，与文档论点对应：推理时基于kv_cache_scale和kv_cache_offset推导quant/dequant scale与offset，实现量化存储、还原精度，从而降低显存占用、减少重计算以提升吞吐。
