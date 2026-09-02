# core_layers

> 仓 `mindie-sd` · 路径 `docs/en/features/core_layers.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/core_layers.md

# mindie-sd `docs/en/features/core_layers.md` 深度解读

## 【定位】

本篇文档系统介绍 `mindiesd` 包通过 `layers` 模块对外暴露的 **FA（Flash Attention）系列核心加速 API**，覆盖标准注意力、变长序列注意力与稀疏注意力三大场景，明确了各接口的函数签名、参数语义、布局约定、算子调度模式与从 PyTorch/Flash-Attention 生态迁移的注意事项，是上层推理框架（vLLM Omni、Diffusers+CacheDit、lightx2v 等）调用昇腾亲和注意力算子的统一接入说明。

---

## 【技术要点】

1. **三类 FA 接口、按需选用**：`attention_forward`（标准定长 batch 注意力）、`attention_forward_varlen`（同 batch 内序列长度不一致场景）、`sparse_attention`（稀疏注意力，支持 `rf_v2` / `rf_v3` RainFusion 与 `ada_bsa` 自适应块稀疏），均通过 `from mindiesd import <interface_name>` 直接导入。

2. **多底层算子 + 自动调度**：`attention_forward` 内置 PFA、FASCore、LaserAttention 等多种底层算子，通过 `opt_mode` 控制——`"runtime"` 自动调优、`"static"` 静态选择、`"manual"` 手动指定 `op_type`（`"prompt_flash_attn"` / `"fused_attn_score"` / `"ascend_laser_attention"`）与 `layout`（`"BNSD"` / `"BSND"` / `"BSH"`）。

3. **张量布局约定**：标准接口支持 `[B,S,N,D]`（`head_first=False`，默认）与 `[B,N,S,D]`（`head_first=True`）；变长接口使用 3D `[T,N,D]` 并以 `cu_seqlens_q/k`（`dtype=torch.int32`，shape `(batch_size+1,)`）描述每条样本的累计长度；稀疏接口由 `input_layout` 指定 `"BNSD"` 或 `"BSND"`。

4. **稀疏策略与精度权衡**：稀疏接口中 `inner_precise=0` 高精度、`1` 高性能；A5 设备使用 `sparse_type="rf_v3"` 时必须在入口处强制设为 `4`；`block_size` 当前仅支持 `128`；`rf_v2/rf_v3` 依赖 `txt_len` 与 `latent_shape_q/k`（要求 `t*h*w = qseqlen/kseqlen`）描述潜空间形状；`ada_bsa` 则通过 `keep_sink`、`keep_recent`、`cdf_threshold`、`sparsity` 等参数控制保留首部/尾部 token 与阈值筛选。

5. **纯前向推理定位**：三个接口均仅提供 forward 推理，不支持反向梯度；迁移时需去掉 `dropout`，并将 `requires_grad` 设为 `False`；变长接口的 `dropout_p` 当前仅支持 `0.0`，其余形如 `window_size`、`softcap`、`alibi_slopes`、`deterministic`、`return_attn_probs`、`max_seqlen_q/k` 均为预留参数。

6. **生态迁移友好**：`attention_forward` 兼容 `torch.nn.functional.scaled_dot_product_attention`（需调整 layout 并去掉 transpose）与 `flash_attn.flash_attn_func`（layout 一致可直替）；`attention_forward_varlen` 与 `flash_attn.flash_attn_varlen_func` 参数大体一致可直替。

---

## 【关键机制与数据】

**工作原理 / 数据流**：
- **标准路径**：调用方传入 Q/K/V（4D，`float16` 为主，`device="npu"`），`attention_forward` 根据 `opt_mode` 选择算子——`runtime` 模式下自动按输入形状/精度寻找最优实现；`manual` 模式下由 `op_type` × `layout` 显式锁定。返回张量布局与输入一致。
- **变长路径**：Q/K/V 被打平为 3D `[T,N,D]`，由 `cu_seqlens_q/k` 在算子内部重新切分出每个样本的子序列，适用于 prefill 阶段不同 prompt 长度混合、或 chunked-prefill 等场景；返回 shape 为 `(total, nheads, headdim)`。
- **稀疏路径**：`sparse_attention` 通过 `sparse_type` 切换实现——`rf_v2/rf_v3`（RainFusion 系列，需配合 `txt_len` 与 `latent_shape_*` 描述视频/图像潜空间 `[t,h,w]`）；`ada_bsa`（自适应块稀疏，按 CDF 阈值动态保留关键 block，可叠加 sink/recent 保留策略）。

**性能/规模数据（原文示例直接给出）**：
- 标准示例：`B=2, S=4096, N=24, D=128, dtype=float16`
- 变长示例：`T=8192, N=24, D=128, dtype=float16`；`cu_seqlens = [0,2048,4096,6144,8192]` 即将 8192 token 拆为 4 条长度均为 2048 的等长子序列

**显式标注的约束/数值（原文）**：
- `scale` 默认值：`head_dim ** -0.5`
- `block_size` 仅支持 `128`
- A5 + `rf_v3`：`inner_precise=4`（入口强制）
- 变长 `cu_seqlens_*`：`dtype=torch.int32, shape=(batch_size+1,)`

---

## 【表格解读】

### 表 1：FA 系列接口总览（原文逐字还原）

| Interface Name | Type | Description |
|--------|------|----------|
| `attention_forward` | Function | Standard attention forward computation, supports automatic operator tuning |
| `attention_forward_varlen` | Function | Variable-length sequence attention forward computation |
| `sparse_attention` | Function | Sparse attention forward computation, supports rf_v2 / ada_bsa sparse strategies |

**解读**：第一行给出默认入口 `attention_forward`，强调"自动算子调优"是其相对于另两者的差异化能力；第二行 `attention_forward_varlen` 用于同 batch 内序列长度不齐的场景，避免 padding 浪费；第三行 `sparse_attention` 在描述中仅列出 `rf_v2 / ada_bsa`，但正文参数表实际还包含 `rf_v3`，读者应以参数表为准。

### 表 2：`attention_forward` 参数表（原文逐字还原）

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `query` | `torch.Tensor` | Yes | - | Query tensor, 4D, layout `[B,S,N,D]` or `[B,N,S,D]` |
| `key` | `torch.Tensor` | Yes | - | Key tensor, 4D, same layout as `query` |
| `value` | `torch.Tensor` | Yes | - | Value tensor, 4D, same layout as `query` |
| `attn_mask` | `torch.Tensor` | No | `None` | Attention mask |
| `scale` | `float` | No | `None` | Scaling factor, defaults to `head_dim ** -0.5` when `None` |
| `fused` | `bool` | No | `True` | Whether to use fused operator, falls back to native computation when `False` |
| `head_first` | `bool` | No | `False` | Whether the head dimension precedes the sequence dimension. `True` means `[B,N,S,D]`, `False` means `[B,S,N,D]` |
| `kwargs.opt_mode` | `str` | No | `"runtime"` | Operator scheduling mode, supports `"runtime"`, `"static"`, `"manual"` |
| `kwargs.op_type` | `str` | No | `"fused_attn_score"` | Operator type, only effective when `opt_mode="manual"`. Supports `"prompt_flash_attn"`, `"fused_attn_score"`, `"ascend_laser_attention"` |
| `kwargs.layout` | `str` | No | `"BNSD"` | Operator layout, only effective when `opt_mode="manual"`. Supports `"BNSD"`, `"BSND"`, `"BSH"` |

**解读**：
- Q/K/V 三者必填且布局一致，`query` 的描述里把两种合法 layout 都列出，强调"必须统一"；
- `scale=None` 自动取 `head_dim ** -0.5`，即标准 Transformer 的 `1/√d`；
- `fused=True` 优先走融合算子（性能路径），`False` 时回退到原生实现（兼容/调试路径）；
- `head_first` 是一个"维度顺序开关"，比显式 `transpose` 更安全，避免 stride 错误；
- `opt_mode` 决定调度哲学：`runtime` 牺牲首次调用时间换长期最优；`static` 适合部署阶段配置锁定；`manual` 留给性能调优工程师精挑算子；
- `op_type` 与 `layout` 只在 `manual` 模式下生效，体现"先选模式再选实现"的两层控制结构。

### 表 3：`attention_forward_varlen` 参数表（原文逐字还原）

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | `torch.Tensor` | Yes | - | Query tensor, 3D, layout `[T, N, D]` (T is the total number of tokens across all sequences) |
| `k` | `torch.Tensor` | Yes | - | Key tensor, 3D, layout `[T, N, D]` |
| `v` | `torch.Tensor` | Yes | - | Value tensor, 3D, layout `[T, N, D]` |
| `cu_seqlens_q` | `torch.Tensor` | Yes | - | Cumulative lengths of query sequences, 1D tensor, shape `(batch_size + 1,)`, dtype `torch.int32` |
| `cu_seqlens_k` | `torch.Tensor` | Yes | - | Cumulative lengths of key sequences, 1D tensor, shape `(batch_size + 1,)`, dtype `torch.int32` |
| `max_seqlen_q` | `int` | No | `None` | Reserved parameter |
| `max_seqlen_k` | `int` | No | `None` | Reserved parameter |
| `dropout_p` | `float` | No | `0.0` | Dropout probability, currently only supports `0.0` |
| `softmax_scale` | `float` | No | `None` | Scaling factor, defaults to `head_dim ** -0.5` when `None` |
| `causal` | `bool` | No | `False` | Whether to use causal attention mask |
| `window_size` | `int` | No | `None` | Reserved parameter |
| `softcap` | `float` | No | `None` | Reserved parameter |
| `alibi_slopes` | `torch.Tensor` | No | `None` | Reserved parameter |
| `deterministic` | `bool` | No | `None` | Reserved parameter |
| `return_attn_probs` | `bool` | No | `None` | Reserved parameter |
| `block_table` | `torch.Tensor` | No | `None` | Reserved parameter |

**解读**：
- Q/K/V 从 4D 降为 3D，`T` 是所有样本 token 总数，通过 flatten + `cu_seqlens` 重组，把 padding 彻底消除；
- `cu_seqlens_q/k` 均为 `int32` 且长度为 `batch_size+1`，是变长方案的"索引骨架"，decode/prefill 混合时尤其关键；
- 当前仅 `causal`、`softmax_scale`、`dropout_p` 与必需张量真正生效；其余 6 个参数均标注"Reserved"，说明接口已对齐 `flash_attn.flash_attn_varlen_func` 的 API 形状，但昇腾后端暂未实现，可直接传入占位以保持上游调用方代码不动。

### 表 4：`sparse_attention` 参数表（原文逐字还原，因原文截断仅呈现到 `spars` 之前的字段）

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `q` | `torch.Tensor` | Yes | - | Query tensor, 4D, layout determined by `input_layout` |
| `k` | `torch.Tensor` | Yes | - | Key tensor, 4D, layout determined by `input_layout` |
| `v` | `torch.Tensor` | Yes | - | Value tensor, 4D, layout determined by `input_layout` |
| `attn_mask` | `torch.Tensor` | No | `None` | Attention mask, reserved parameter |
| `scale` | `float` | No | `None` | Scaling factor, defaults to `head_dim ** -0.5` when `None` |
| `is_causal` | `bool` | No | `False` | Whether to use causal attention mask |
| `head_num` | `int` | No | `1` | Number of attention heads |
| `input_layout` | `str` | No | `"BNSD"` | Tensor layout, supports `"BNSD"` or `"BSND"` |
| `inner_precise` | `int` | No | `0` | Computation precision mode, `0` for high precision, `1` for high performance. On A5 devices, `sparse_type="rf_v3"` requires `4` (enforced at the entry) |
| `sparse_type` | `str` | No | `None` | Sparse type, supports `None`, `"rf_v2"`, `"rf_v3"`, `"ada_bsa"` |
| `txt_len` | `int` | No | `0` | Text sequence length, effective when `sparse_type="rf_v2"` or `"rf_v3"` |
| `block_size` | `int` | No | `128` | Block size, currently only supports `128` |
| `latent_shape_q` | `list` | No | `None` | Latent space shape of query `[t, h, w]`, `t*h*w = qseqlen`, effective when `sparse_type="rf_v2"` or `"rf_v3"` |
| `latent_shape_k` | `list` | No | `None` | Latent space shape of key `[t, h, w]`, `t*h*w = kseqlen`, effective when `sparse_type="rf_v2"` or `"rf_v3"` |
| `keep_sink` | `bool` | No | `True` | Whether to keep sink tokens, only effective when `sparse_type="ada_bsa"` |
| `keep_recent` | `bool` | No | `True` | Whether to keep recent tokens, only effective when `sparse_type="ada_bsa"` |
| `cdf_threshold` | `float` | No | `1.0` | CDF threshold, only effective when `sparse_type="ada_bsa"` |
| `spars` | （原文截断，未呈现完整条目） | - | - | （原文截断，未呈现完整条目） |

**解读**：
- 该接口以 `sparse_type` 为"主开关"将参数划分为两组：`rf_v2/rf_v3` 组（依赖 `txt_len`、`latent_shape_q/k`）与 `ada_bsa` 组（依赖 `keep_sink`、`keep_recent`、`cdf_threshold`），其余参数为通用控制；
- `latent_shape_q/k` 的不变量 `t*h*w == seq_len` 用于把扁平序列折叠回三维时空网格，体现稀疏是为视频/扩散模型时空维度相关性而生；
- `inner_precise` 是一个三层取值：`0` 默认高精度、`1` 高性能、`4` 仅限 A5 + rf_v3，体现硬件/算法耦合的特殊通路；
- 注意：**原文末尾表格在 `spars` 处被截断**（按截断内容推测，下一行应为 `sparsity`，参数表中 "原文示例/签名" 部分也出现了 `sparsity=0.0`），因此 `sparsity` 及之后字段（含 `precision="bf16"` 与后续 `**kwargs` 描述、返回值、Usage Example、Migration Guide 等小节）在提供的原文片段中缺失，本解读不对缺失内容臆造。

---

## 【公式解读】

原文未出现独立成行的数学公式或 LaTeX 表达式，仅以文字形式提及以下与公式相关的关键常量：

- `head_dim ** -0.5` — 即标准 Scaled Dot-Product Attention 中的缩放因子 $1/\sqrt{d}$，其中 $d$ 为 head 维度（`head_dim`）；在 `attention_forward`、`attention_forward_varlen`、`sparse_attention` 三个接口中，当用户未显式传入 `scale` / `softmax_scale` 时均默认采用该值。其作用是在 $QK^\top$ 之后除以 $\sqrt{d}$，避免内积值过大导致 softmax 进入梯度饱和区。

> **注**：原文除此一项外无其它数学公式（无 $QK^\top$、softmax、Flash Attention 的 tiling/recurrence 等推导），故本节不再展开。

---

## 【关联】

- **上层框架接入**：作为 `mindiesd.layers` 模块暴露的底层加速原语，被项目首页提到的 **vLLM Omni**、**Diffusers + CacheDit**、**lightx2v** 等多模态/视频推理框架直接调用，承担注意力计算的算子后端角色；
- **算子下层依赖**：`attention_forward` 内部封装 PFA、FASCore、LaserAttention 等昇腾亲和算子，通过 `opt_mode`/`op_type` 在它们之间调度；
- **生态兼容链路**：参数命名（`softmax_scale`、`causal`、`dropout_p`、`alibi_slopes`、`window_size` 等）与 `flash_attn` / `torch.nn.functional.scaled_dot_product_attention` 对齐，便于上层做"算子后端切换"；
- **稀疏分支与扩散模型的耦合**：`sparse_attention` 的 `latent_shape_q/k` 显式针对扩散模型潜空间 `[t,h,w]` 设计，说明该接口主要服务于 CacheDit 这类 DiT 类稀疏加速场景；
- **内部链接**：原文未提供任何内部链接（任务上下文已标注"内部链接: (无)"），故上下游关系需以本仓库其他文档/源码为准，原文不做交叉引用。

---

## 【使用方法】

**导入方式**（原文直接给出）：
```python
from mindiesd import attention_forward
from mindiesd import attention_forward_varlen
from mindiesd import sparse_attention
```

**标准注意力调用**（原文示例，B=2, S=4096, N=24, D=128, fp16）：
```python
query = torch.randn(2, 4096, 24, 128, device="npu", dtype=torch.float16)
key   = torch.randn(2, 4096, 24, 128, device="npu", dtype=torch.float16)
value = torch.randn(2, 4096, 24, 128, device="npu", dtype=torch.float16)
out = attention_forward(query, key, value)
```

**变长序列调用**（原文示例，T=8192, N=24, D=128, 4 条等长子序列）：
```python
q = torch.randn(8192, 24, 128, device="npu", dtype=torch.float16)
k = torch.randn(8192, 24, 128, device="npu", dtype=torch.float16)
v = torch.randn(8192, 24, 128, device="npu", dtype=torch.float16)
cu_seqlens_q = torch.tensor([0, 2048, 4096, 6144, 8192], dtype=torch.int32, device="npu")
cu_seqlens_k = torch.tensor([0, 2048, 4096, 6144, 8192], dtype=torch.int32, device="npu")
out = attention_forward_varlen(q, k, v, cu_seqlens_q, cu_seqlens_k, causal=False)
```

**关键配置项速查**：
- `fused=True|False`：是否走融合算子；
- `head_first`：在 `[B,S,N,D]` 与 `[B,N,S,D]` 间切换；
- `opt_mode`：`"runtime"` / `"static"` / `"manual"`；
- `op_type`（manual 模式）：`"prompt_flash_attn"` / `"fused_attn_score"` / `"ascend_laser_attention"`；
- `layout`（manual 模式）：`"BNSD"` / `"BSND"` / `"BSH"`；
- `sparse_type`：`None` / `"rf_v2"` / `"rf_v3"` / `"ada_bsa"`；
- `inner_precise=0` 高精度、`=1` 高性能、A5 + rf_v3 时 `=4`；
- `block_size=128`（当前唯一支持值）。

**迁移要点**（原文直接给出）：
- 从 `torch.nn.functional.scaled_dot_product_attention` 迁移：layout 由 `[B,N,S,D]` 改为 `[B,S,N,D]`，并删除外层 `transpose`；
- 从 `flash_attn.flash_attn_func` 迁移：layout 已为 `[B,S,N,D]`，可直接替换；
- 从 `flash_attn.flash_attn_varlen_func` 迁移：参数名/语义基本一致，可直接替换；
- 三者均仅支持前向推理，迁移时需去掉 `dropout` 并设 `requires_grad=False`。

> **原文截断说明**：`sparse_attention` 一节的"Usage Example""Migration Guide"以及参数表中 `sparsity` 之后字段在提供的原文片段中缺失，本节不再据外部信息补全。
