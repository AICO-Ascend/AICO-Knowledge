# 核心加速API

> 仓 `mindie-sd` · 路径 `docs/zh/features/core_layers.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/core_layers.md

# mindie-sd 核心加速API 文档深度解读

## 【定位】

本文档系统性地描述了 `mindiesd` 包通过 `layers` 模块对外暴露的核心加速API集合，覆盖昇腾亲和的**注意力计算**（Flash Attention 系列）与**基础融合算子**（位置编码、归一化、激活函数）两大类接口，作为上层框架（vLLM Omni、Diffusers+CacheDit、lightx2v 等）调用底层昇腾高性能算子的统一入口。

---

## 【技术要点】

1. **三层注意力接口分层覆盖场景**：标准注意力（`attention_forward`，自动算子寻优 PFA/FASCore/LaserAttention）、变长序列（`attention_forward_varlen`，cu_seqlens 累加式索引）、稀疏注意力（`sparse_attention`，支持 `rf_v2`/`rf_v3`/`ada_bsa` 三种稀疏策略）。

2. **布局双轨兼容 `[B,S,N,D]` / `[B,N,S,D]`**：通过 `head_first` 开关或 `input_layout="BNSD"/"BSND"` 显式声明，所有接口默认以 `[B,S,N,D]` 为主布局，与 `flash_attn` 生态保持一致；`rotary_position_embedding` 还额外支持 `[S,B,N,D]`。

3. **算子调度三级模式 (`opt_mode`)**：仅在 `attention_forward` 中通过 `**kwargs` 暴露——`"runtime"`（运行时自动寻优，默认）、`"static"`（静态编译期选型）、`"manual"`（手动指定 `op_type` 与 `layout`，支持 `"prompt_flash_attn"`、`"fused_attn_score"`、`"ascend_laser_attention"`）。

4. **缩放因子统一约定**：所有注意力接口中 `scale=None` 时自动取 `head_dim ** -0.5`，与 SDPA / FlashAttention 习惯一致，无需上层显式计算。

5. **融合算子覆盖 Transformer 核心基础组件**：RoPE 旋转位置编码（含 `rotated_half` / `rotated_interleaved` 两种模式）、RMSNorm、`fast_layernorm`、`layernorm_scale_shift`（AdaLayerNorm）、激活函数工厂 `get_activation_layer`（含 NPU 加速版）。

6. **varlen 累加长度约定**：`cu_seqlens_q` / `cu_seqlens_k` 形状为 `(batch_size + 1,)`，dtype 为 `torch.int32`；varlen 输入布局为 3D `[T, N, D]`（T 为 token 总数），输出形状为 `(total, nheads, headdim)`。

7. **稀疏策略参数语义差异化**：`sparse_type="rf_v2"` 时启用 `txt_len` / `latent_shape_q` / `latent_shape_k`（多模态潜空间形状）；`sparse_type="ada_bsa"` 时启用 `keep_sink` / `keep_recent` / `cdf_threshold` / `sparsity`（自适应块稀疏）。

---

## 【关键机制与数据】

### 注意力前向寻优机制（原文：`attention_forward`）
- 接口内部封装 PFA、FASCore、LaserAttention 等多种底层算子，通过 `opt_mode` 控制寻优时机。
- `fused=True`（默认）走融合算子路径，`fused=False` 回退到原生 SDPA 风格计算。
- 关键限制：**仅提供前向推理，不支持反向梯度计算**；迁移时需去除 `dropout` 并将 `requires_grad` 设为 `False`。

### 变长序列寻址（原文：`attention_forward_varlen`）
- 通过 `cu_seqlens_q` / `cu_seqlens_k`（累积和）描述 batch 内每个序列在扁平 token 张量 `[T, N, D]` 中的边界。
- 示例中 4 个序列均分 8192 tokens：`[0, 2048, 4096, 6144, 8192]`，每段 2048 tokens。
- 多个参数标记为"预留参数"（`max_seqlen_q/k`、`window_size`、`softcap`、`alibi_slopes`、`deterministic`、`return_attn_probs`、`block_table`），当前版本未启用。

### 稀疏注意力策略（原文：`sparse_attention`）
- **RainFusion（rf_v2 / rf_v3）**：面向多模态场景，需提供 `txt_len` 与 `latent_shape_q/k=[t,h,w]`（满足 `t*h*w = qseqlen/kseqlen`），将潜空间形状注入以指导稀疏模式。
- **AdaBSA（自适应块稀疏）**：通过 `keep_sink`（首部 sink token）、`keep_recent`（尾部 recent token）、`cdf_threshold`（CDF 阈值，`1.0` 默认）、`sparsity`（稀疏率 `[0,1]`）四个开关控制保留范围与稀疏强度。
- `block_size=128` 当前固定；`inner_precise=0`（高精度，默认）/ `1`（高性能）。

### RoPE 双旋转模式（原文：`rotary_position_embedding`）
- `rotated_half`：将 `x` 沿最后一维拆为前后两半旋转——对应 **OpenSoraPlan、Stable Audio**。
- `rotated_interleaved`：将 `x` 沿最后一维按相邻元素交错旋转——对应 **HunyuanDiT、OpenSora、Flux、CogVideox**。
- `cos` / `sin` 预计算频率张量支持 2D `[S,D]` 或 4D 广播形态 `[1,1,S,D]` / `[1,S,1,D]` / `[S,1,1,D]`。

### varlen → flash_attn 接口兼容性（原文：迁移指南）
- 从 `flash_attn.flash_attn_varlen_func` 迁移时参数基本一致，**可直接替换调用**（这一条是文档明确给出的迁移友好性证据）。

### 标准注意力迁移差异（原文：迁移指南）
- 从 `torch.nn.functional.scaled_dot_product_attention` 迁移：输入需从 `[B,N,S,D]` 调整为 `[B,S,N,D]`，并去掉 `transpose` 操作。
- 从 `flash_attn.flash_attn_func` 迁移：布局已为 `[B,S,N,D]`，可直接替换。

> 备注：原文未涉及具体的端到端性能数据（如时延、吞吐、加速比）。

---

## 【表格解读】

### 表 A — FA 系列接口总览

| 接口名 | 类型 | 功能描述 |
|--------|------|----------|
| `attention_forward` | 函数 | 标准注意力前向计算，支持自动算子寻优 |
| `attention_forward_varlen` | 函数 | 变长序列注意力前向计算 |
| `sparse_attention` | 函数 | 稀疏注意力前向计算，支持 rf_v2 / ada_bsa 稀疏策略 |

**逐行解读**：三个接口构成"通用→变长→稀疏"的能力金字塔。`attention_forward` 面向等长场景并承担自动算子选型职责；`attention_forward_varlen` 解决 LLM 推理中同 batch 序列长度参差的现实问题（典型场景为请求调度后的 padding 消除）；`sparse_attention` 则是面向长序列/多模态场景通过 RainFusion、AdaBSA 降低计算量的进阶能力。

---

### 表 B — `attention_forward` 参数说明

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | `torch.Tensor` | 是 | - | 查询张量，4D，布局为 `[B,S,N,D]` 或 `[B,N,S,D]` |
| `key` | `torch.Tensor` | 是 | - | 键张量，4D，布局与 `query` 一致 |
| `value` | `torch.Tensor` | 是 | - | 值张量，4D，布局与 `query` 一致 |
| `attn_mask` | `torch.Tensor` | 否 | `None` | 注意力掩码 |
| `scale` | `float` | 否 | `None` | 缩放因子，为 `None` 时自动取 `head_dim ** -0.5` |
| `fused` | `bool` | 否 | `True` | 是否使用融合算子，`False` 时回退到原生计算 |
| `head_first` | `bool` | 否 | `False` | 头维度是否在序列维度之前，`True` 表示 `[B,N,S,D]`，`False` 表示 `[B,S,N,D]` |
| `kwargs.opt_mode` | `str` | 否 | `"runtime"` | 算子调度模式，支持 `"runtime"`、`"static"`、`"manual"` |
| `kwargs.op_type` | `str` | 否 | `"fused_attn_score"` | 算子类型，仅在 `opt_mode="manual"` 时生效，支持 `"prompt_flash_attn"`、`"fused_attn_score"`、`"ascend_laser_attention"` |
| `kwargs.layout` | `str` | 否 | `"BNSD"` | 算子布局，仅在 `opt_mode="manual"` 时生效，支持 `"BNSD"`、`"BSND"`、`"BSH"` |

**逐行解读**：
- 三元组 Q/K/V 必选且布局绑定一致，由 `head_first` 统一切换 BSND/BNSD。
- `fused` 为容灾开关——遇到融合算子不支持的 shape/edge case 时可回退。
- `kwargs` 中三个参数组成 `opt_mode="manual"` 模式下的"算子三件套"：调度模式 + 算子类型 + 布局；默认组合为 runtime + fused_attn_score + BNSD。

---

### 表 C — `attention_forward_varlen` 参数说明

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | `torch.Tensor` | 是 | - | 查询张量，3D，布局为 `[T, N, D]`（T 为所有序列 token 总数） |
| `k` | `torch.Tensor` | 是 | - | 键张量，3D，布局为 `[T, N, D]` |
| `v` | `torch.Tensor` | 是 | - | 值张量，3D，布局为 `[T, N, D]` |
| `cu_seqlens_q` | `torch.Tensor` | 是 | - | 查询序列的累积长度，1D 张量，形状为 `(batch_size + 1,)`，dtype 为 `torch.int32` |
| `cu_seqlens_k` | `torch.Tensor` | 是 | - | 键序列的累积长度，1D 张量，形状为 `(batch_size + 1,)`，dtype 为 `torch.int32` |
| `max_seqlen_q` | `int` | 否 | `None` | 预留参数 |
| `max_seqlen_k` | `int` | 否 | `None` | 预留参数 |
| `dropout_p` | `float` | 否 | `0.0` | Dropout 概率，当前仅支持 `0.0` |
| `softmax_scale` | `float` | 否 | `None` | 缩放因子，为 `None` 时自动取 `head_dim ** -0.5` |
| `causal` | `bool` | 否 | `False` | 是否使用因果注意力掩码 |
| `window_size` | `int` | 否 | `None` | 预留参数 |
| `softcap` | `float` | 否 | `None` | 预留参数 |
| `alibi_slopes` | `torch.Tensor` | 否 | `None` | 预留参数 |
| `deterministic` | `bool` | 否 | `None` | 预留参数 |
| `return_attn_probs` | `bool` | 否 | `None` | 预留参数 |
| `block_table` | `torch.Tensor` | 否 | `None` | 预留参数 |

**逐行解读**：
- 必选仅 5 项：Q/K/V + 两条 cu_seqlens，足以驱动 varlen 计算。
- "预留参数"多达 6 项（`max_seqlen_q/k`、`window_size`、`softcap`、`alibi_slopes`、`deterministic`、`return_attn_probs`、`block_table`），表明接口签名对标 FlashAttention 上游完整能力，但当前仅暴露 subset。
- `causal=False` 默认值意味着非自回归场景同样适配（cross-attention、encoder-decoder 等）。
- `block_table` 预留暗示未来会支持 PagedAttention 类能力（vLLM 常用）。

---

### 表 D — `sparse_attention` 参数说明

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `q` | `torch.Tensor` | 是 | - | 查询张量，4D，布局由 `input_layout` 决定 |
| `k` | `torch.Tensor` | 是 | - | 键张量，4D，布局由 `input_layout` 决定 |
| `v` | `torch.Tensor` | 是 | - | 值张量，4D，布局由 `input_layout` 决定 |
| `attn_mask` | `torch.Tensor` | 否 | `None` | 注意力掩码，预留参数 |
| `scale` | `float` | 否 | `None` | 缩放因子，为 `None` 时自动取 `head_dim ** -0.5` |
| `is_causal` | `bool` | 否 | `False` | 是否使用因果注意力掩码 |
| `head_num` | `int` | 否 | `1` | 注意力头数量 |
| `input_layout` | `str` | 否 | `"BNSD"` | 张量布局，支持 `"BNSD"` 或 `"BSND"` |
| `inner_precise` | `int` | 否 | `0` | 计算精度模式，`0` 为高精度，`1` 为高性能 |
| `sparse_type` | `str` | 否 | `None` | 稀疏类型，支持 `None`、`"rf_v2"`、`"rf_v3"`、`"ada_bsa"` |
| `txt_len` | `int` | 否 | `0` | 文本序列长度，仅在 `sparse_type="rf_v2"` 时生效 |
| `block_size` | `int` | 否 | `128` | 块大小，当前仅支持 `128` |
| `latent_shape_q` | `list` | 否 | `None` | 查询的潜空间形状 `[t, h, w]`，`t*h*w = qseqlen`，仅在 `sparse_type="rf_v2"` 时生效 |
| `latent_shape_k` | `list` | 否 | `None` | 键的潜空间形状 `[t, h, w]`，`t*h*w = kseqlen`，仅在 `sparse_type="rf_v2"` 时生效 |
| `keep_sink` | `bool` | 否 | `True` | 是否保留 sink token，仅在 `sparse_type="ada_bsa"` 时生效 |
| `keep_recent` | `bool` | 否 | `True` | 是否保留 recent token，仅在 `sparse_type="ada_bsa"` 时生效 |
| `cdf_threshold` | `float` | 否 | `1.0` | CDF 阈值，仅在 `sparse_type="ada_bsa"` 时生效 |
| `sparsity` | `float` | 否 | `0.0` | 稀疏率，取值范围 `[0, 1]`，`0` 表示不使用稀疏算法 |

**逐行解读**：
- 参数分两组：通用部分（Q/K/V、scale、is_causal、head_num、input_layout、inner_precise）与"策略触发"部分（按 `sparse_type` 二选一启用）。
- `rf_v2` 参数组（`txt_len`、`latent_shape_q/k`）将稀疏路由与多模态潜空间结构强耦合——`t*h*w` 必须精确匹配实际 seqlen，否则路由失效。
- `ada_bsa` 参数组（`keep_sink`、`keep_recent`、`cdf_threshold`、`sparsity`）是更通用的"窗口+自适应"控制面，类比 StreamingLLM 思路但增加 CDF 阈值做块级筛选。
- `sparsity=0.0`（默认）退化为稠密计算，方便上层做能力开关而无须换接口。
- `head_num=1` 默认值相对保守，实际多 head 场景需显式声明（示例中即 `head_num=24`）。

---

### 表 E — 融合算子接口总览

| 接口名 | 类型 | 功能描述 |
|--------|------|----------|
| `rotary_position_embedding` | 函数 | 旋转位置编码（RoPE）融合算子 |
| `RMSNorm` | 类 | RMS 归一化融合算子 |
| `fast_layernorm` | 函数 | 高性能 LayerNorm 融合算子 |
| `layernorm_scale_shift` | 函数 | 自适应 LayerNorm（AdaLayerNorm）融合算子 |
| `get_activation_layer` | 函数 | 获取激活函数实例（含 NPU 加速版本） |

**逐行解读**：构成 Transformer block 中除注意力外的"附属计算"全集——位置编码、两种归一化（标准 RMS / Ada）、激活工厂。注意 `RMSNorm` 是**类**（带 `__init__` 的实例化对象），其余四个为**函数式**调用。

---

### 表 F — `rotary_position_embedding` 参数说明

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `x` | `torch.Tensor` | 是 | - | 查询或键张量，4D，支持布局 `[B,N,S,D]`、`[B,S,N,D]`、`[S,B,N,D]` |
| `cos` | `torch.Tensor` | 是 | - | 预计算的余弦频率张量，2D `[S,D]` 或 4D `[1,1,S,D]`/`[1,S,1,D]`/`[S,1,1,D]` |
| `sin` | `torch.Tensor` | 是 | - | 预计算的正弦频率张量，维度与 `cos` 一致 |
| `rotated_mode` | `str` | 否 | `"rotated_half"` | 旋转模式：`"rotated_half"` 为半旋转，`"rotated_interleaved"` 为交错旋转 |
| `head_first` | `bool` | 否 | `False` | 头维度是否在序列维度之前 |
| `fused` | `bool` | 否 | `True` | 是否使用融合算子 |

**逐行解读**：
- `x` 的三种 4D 布局覆盖了 attention 之前注入 RoPE 的常见插入点。
- `cos/sin` 的 4 种形状（含 2D 和 3 种 4D 广播形态）降低了上层预计算的复杂度。
- `rotated_mode` 是模型族的关键开关——选错会导致旋转后的 Q/K 与预训练权重不兼容，这是 DiT 多模态生态长期痛点。

---

> 备注：原文档在 `RMSNorm` 构造参数表处被截断（表头已给出，但表体未渲染），后文 `fast_layernorm`、`layernorm_scale_shift`、`get_activation_layer` 的参数与示例在当前原文中不可见，无法逐字还原。

---

## 【公式解读】

原文无公式。

> 注：文档中虽出现 `head_dim ** -0.5` 这一标准注意力缩放约定，但它以参数默认值形式给出，并非以公式/伪代码方式呈现，因此不作为独立公式条目处理。该表达式的语义为"以头维度平方根的倒数作为缩放因子"，与 SDPA / FlashAttention 的实现一致。

---

## 【关联】

文档本身未提供内部链接（`内部链接: (无)`），但从文档内容可识别出以下结构性关联：

1. **FA 系列内部三件套**：`attention_forward`（通用等长）、`attention_forward_varlen`（cu_seqlens 索引）、`sparse_attention`（rf_v2/rf_v3/ada_bsa）形成完整的注意力能力矩阵——上层推理框架（vLLM Omni、Diffusers+CacheDit 等）按场景挑选调用。

2. **FA 系列 ↔ 融合算子**：在 Transformer block 中，FA 系列接口承担"主路径"注意力计算，`rotary_position_embedding` 在 Q/K 投影后注入位置信息，`RMSNorm`/`fast_layernorm`/`layernorm_scale_shift` 在 FFN 前后做归一化，`get_activation_layer` 提供激活函数——五者组合构成完整 Transformer block 的算子全集。

3. **上游框架适配关系**：文档示例中 `2, 4096, 24, 128` 的张量 shape（batch=2、seqlen=4096、head=24、head_dim=128）以及 `8192, 24, 128` 的 varlen shape 暗示接口针对**大模型典型配置**做了参数化设计，可直接对接到 vLLM Omni（LLM 推理）、Diffusers（扩散模型）、lightx2v（视频扩散）的注意力路径。

4. **与上游生态的兼容边界**：迁移指南明确指向 `torch.nn.functional.scaled_dot_product_attention`、`flash_attn.flash_attn_func`、`flash_attn.flash_attn_varlen_func` 三个上游入口，构成迁移兼容性矩阵——`flash_attn` 路径几乎零成本替换，PyTorch SDPA 路径需做 layout 转置。

5. **预留参数暗含的未来扩展**：varlen 接口中 `block_table` 预留、`max_seqlen_q/k` 预留，暗示后续可能支持 PagedAttention（vLLM 风格）和更长序列的精确调度。

---

## 【使用方法】

### 标准注意力

```python
from mindiesd import attention_forward

query = torch.randn(2, 4096, 24, 128, device="npu", dtype=torch.float16)
key   = torch.randn(2, 4096, 24, 128, device="npu", dtype=torch.float16)
value = torch.randn(2, 4096, 24, 128, device="npu", dtype=torch.float16)
out = attention_forward(query, key, value)
```

> 原文默认布局为 `[B,S,N,D]`，示例 shape 即 `B=2, S=4096, N=24, D=128`。

### 变长序列注意力

```python
from mindiesd import attention_forward_varlen

q = torch.randn(8192, 24, 128, device="npu", dtype=torch.float16)
k = torch.randn(8192, 24, 128, device="npu", dtype=torch.float16)
v = torch.randn(8192, 24, 128, device="npu", dtype=torch.float16)
cu_seqlens_q = torch.tensor([0, 2048, 4096, 6144, 8192], dtype=torch.int32, device="npu")
cu_seqlens_k = torch.tensor([0, 2048, 4096, 6144, 8192], dtype=torch.int32, device="npu")
out = attention_forward_varlen(q, k, v, cu_seqlens_q, cu_seqlens_k, causal=False)
```

### 稀疏注意力（AdaBSA 示例）

```python
from mindiesd import sparse_attention

q = torch.randn(2, 24, 4096, 128, device="npu", dtype=torch.float16)
k = torch.randn(2, 24, 4096, 128, device="npu", dtype=torch.float16)
v = torch.randn(2, 24, 4096, 128, device="npu", dtype=torch.float16)

out = sparse_attention(
    q, k, v,
    head_num=24,
    input_layout="BNSD",
    sparse_type="ada_bsa",
    sparsity=0.5
)
```

### RoPE（旋转位置编码）

```python
from mindiesd import rotary_position_embedding

x   = torch.randn(2, 4096, 24, 128, device="npu", dtype=torch.float16)
cos = torch.randn(1, 4096, 1, 128, device="npu", dtype=torch.float16)
sin = torch.randn(1, 4096, 1, 128, device="npu", dtype=torch.float16)
out = rotary_position_embedding(x, cos, sin, rotated_mode="rotated_half", head_first=False, fused=True)
```

### RMSNorm

```python
from mindiesd import RMSNorm
# 原文仅给出类签名: RMSNorm(hidden_size, eps=1e-6)
# 构造参数表被截断，更详细的使用示例在当前原文中不可见。
```

### `fast_layernorm`、`layernorm_scale_shift`、`get_activation_layer`

原文未涉及（文档在 RMSNorm 表格处截断，这三个接口的使用示例不可见）。

---

> **文档完整性提示**：本篇原文在 `RMSNorm` 构造参数表表头之后被截断（原文表格仅有表头行，无表体行；且后续 `fast_layernorm`、`layernorm_scale_shift`、`get_activation_layer` 的小节在所提供的原文范围内缺失）。本次解读严格基于所提供的原文内容，未对缺失部分做任何推断或补充。
