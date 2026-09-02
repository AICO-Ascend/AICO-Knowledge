# Block Sparse Attention backend 实现设计

> 仓 `msmodeling` · 路径 `docs/design/block_sparse_attention_backend_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/block_sparse_attention_backend_design.md

# 《Block Sparse Attention backend 实现设计》深度解读

---

## 【定位】

这篇文档定义 TensorCast/MindStudio-Modeling 中 **Block Sparse Attention (BSA) backend** 的端到端实现契约——即在 Diffusers attention dispatch 与 `scaled_dot_product_attention` (SDPA) context 入口上，新增 route generation 和 block sparse attention 语义，固化 capability validation、fallback 统计、route plan 生命周期、analytic 性能模型与 Diffusers 注册边界等跨层行为；它**不**修改真实数值 kernel、**不**引入经验 mapping、**不**重构现有 SDPA monkey patch 与 SP 通信模型。

---

## 【技术要点】

1. **Estimator 采用离散 padded block-count 模型**：以 `Qb = ceil(Sq/B)`、`Kb = ceil(Sk/B)`、`Kkeep = max(1, ceil(Kb*(1-s)))` 表达；不采用"连续 sparsity × token 精确计数"模型，原因是 block kernel 必须按 padded tile 执行，且必须支持 block size 与 edge tile 的取整表达。
2. **K/V memory 采用保守 selected-union 模型**：每次完整 K/V HBM read 一次，**不**按 sparsity 线性缩放；因为 route metadata 不提供 route union/reuse，禁止在内存估算中作无依据线性缩放。
3. **Unsupported call 走聚合可见 dense fallback**：保留含 cross-attention 的视频模型兼容性；fallback 在进入 dense path 前**仅记录一次**，最终在 context 退出时聚合为一条 warning。
4. **Route plan 生命周期为 Run-scoped**：`AttentionRoutePlan` 由 CLI 构造并直接传给 `use_custom_sdpa(...)`；`DiffusersTransformerConfig` 与 model config 不写入 plan 字段（model config 状态重复且无效）；一次 `run_inference(...)` 只创建一个 plan，main/cache model 在同一 context 内共享。
5. **Backend 边界硬约束**：`dense` 只接受 `DEFAULT_BLOCK_SPARSE_ATTENTION_BLOCK_SIZE = 128` 与 `sparsity == 0.0`；拒绝 `dense + nonzero sparsity` 与 `dense + 非默认 block_size`；BSA context 与任何**非空 attention quant config**互斥，linear 量化不受影响；CLI quantization 检查只提供更早反馈，不可替代 context validation。
6. **Capability 判定顺序与 7 个 reason code**：`non_4d_qkv` → `qkv_shape_mismatch` → `unsupported_attention_mask` → `dropout` → `causal` → `custom_scale` → `gqa`；每 call 仅归入首要原因。支持条件：Q/K/V 全 4D 且 shape 一致、mask 为 `None` 或 bool/4D/`(batch,1,query_len,key_len)`、`dropout=0`、非 causal、无 custom scale、不启用 GQA。

---

## 【关键机制与数据】

**入口与执行路径（原文 §4.3）**
```text
# 合格 BSA call
Q/K/V
  -> attention_route_generate(Q, K, block_size, sparsity)
  -> block_sparse_attention(Q, K, V, mask, route_metadata, block_size, sparsity)

# 不合格 BSA call
Q/K/V
  -> record fallback reason
  -> dense tensor_cast.attention
```
BSA context 进入前已拒绝 attention quantization，因此 unsupported BSA call 不会转入 quantized dense attention。

**Canonical layout（原文 §4.2）**：Diffusers registry backend 接收 canonical `(batch, sequence, heads, head_dim)` layout；direct SDPA 接收 `(batch, heads, sequence, head_dim)` layout，满足条件时**先转置为 canonical、执行 route 与 BSA op、再转回原 layout**。Unsupported direct SDPA 调用保持既有 dense path，不顺带改变 dense layout 语义。

**Route metadata 表示（原文 §6）**：`attention_route_generate` 返回 int32 metadata，shape 为 `(batch, num_heads, ceil(query_len/block_size), ceil(key_len/block_size))`；表示完整 block-pair route matrix。性能模型**只使用 metadata shape 与 plan sparsity，不读取 metadata value**。该表示兼容 meta/FakeTensor/compile，不引入 data-dependent shape。

**Stats 与可观测性（原文 §5）**：Context 创建独立 stats，至少包含 `block_sparse_attention_calls`、`dense_fallback_calls`、`dense_fallback_reasons: Counter[str]`；eligible call 只增加 BSA 计数，unsupported call 只增加 fallback 计数与一个 reason，dense backend 不增加这些计数。退出时若有 fallback，logger 输出聚合 warning（BSA count + fallback 总数 + 按 reason 排序的 map），无 fallback 不输出。

**Lifecycle（原文 §3.2）**：`use_custom_sdpa(...)` 进入时保存原始 SDPA function、quant config、route plan、route stats；退出时按相反顺序恢复；嵌套 context 必须恢复外层状态。现有 `use_custom_sdpa(quant_config)` positional 调用保持兼容，route plan 和 stats 通过可选参数表达。

**与其他能力的交互契约（原文 §9）**：
- **Attention quantization**：BSA 与非空 attention quant config 互斥；linear quantization 不受影响。
- **Sequence parallelism (SP)**：沿用既有 all-to-all；capability 与 route generation 基于 all-to-all **后**的 canonical Q/K/V shape；SP cleanup 只清理 SP group，不提前清理 route plan/stats；统一在 route context 退出时恢复。
- **DiT cache**：main/cache model 共享 run-scoped plan；cache window 只切换 active model，不切换 backend policy；cache model config 不保存 plan。
- **`torch.compile`**：主/cache 模型可在进入 runtime 前调用 `torch.compile`，首次 forward/tracing 发生在 SDPA context 内；eager 与 compiled 路径使用相同 capability、fallback 与 stats 实现。
- **CFG**：batch concat 或 CFG parallel 只改变 batch/layout；满足 shape 条件时仍走 BSA；**不**新增专用 policy。

**Diffusers registration 边界（原文 §8）**：package `__init__` **不**导入 attention adapter；model/adapter setup 负责导入并注册 TensorCast backend。目标：导入 cache/resolver/utils 等无关子模块时不加载私有 Diffusers attention registry API；构建 Diffusers transformer model 时 backend 已注册；重复导入保持幂等、不重复扩展 enum。

---

## 【表格解读】

### 表 1：修订记录

| 日期 | 修订版本 | 修改描述 | 作者 |
| --- | --- | --- | --- |
| 2026-08-05 | 1.0 | 固化 Diffusers BSA dispatch、fallback、route lifecycle 与 analytic estimator 契约 | minghang_c |

**逐行解读**：仅一行修订记录，表明本文档为 v1.0 初始固化的"设计契约"性质文档。其修改描述明确点出本版本固化的四块内容：Diffusers BSA dispatch、fallback 统计、route lifecycle、analytic estimator——这四块恰好覆盖 §4、§5、§3.2、§7 的核心契约，作者署名 `minghang_c`。

### 表 2：决策摘要（原文 §2）

| 决策点 | 结论 | 原因 |
| --- | --- | --- |
| Estimator | 离散 padded block-count | 连续 sparsity 无法表达 block size、取整和 edge tile |
| K/V memory | 保守 selected-union，单次完整 K/V HBM read | Route metadata 不提供 route union/reuse；禁止无依据线性缩放 |
| Unsupported calls | 聚合可见 dense fallback | 保留包含 cross-attention 的视频模型兼容性 |
| Route plan ownership | Run-scoped | 一个 context 包围 main/cache model，model config 状态重复且无效 |
| BSA + attention quantization | Backend boundary 拒绝 | 防止 direct API 产生混合 BSA/quantized-dense 语义 |
| Dense + BSA-only options | 拒绝非默认值 | 防止用户误以为参数生效 |
| Diffusers registration | Model/adapter 边界定向注册 | 减少无关 import 和私有 API 的进程级副作用 |

**逐行解读**：
1. **Estimator → 离散 padded block-count**：核心抉择，决定 §7 的整套公式体系选择 padded tile 模型而非连续 sparsity × token 计数。
2. **K/V memory → 保守 selected-union，单次完整 K/V HBM read**：决定 §7.4 的内存模型不按 sparsity 缩放；traffic 包含 Q/K/V/mask/route metadata/output 各一次完整 HBM。
4. **Route plan ownership → Run-scoped**：决定 §3.2 的一次 inference 只创建一个 plan、main/cache model 共享、`DiffusersTransformerConfig` 不保存 plan。
6. **BSA + attention quantization → Backend boundary 拒绝**：决定 §3.1 第 4 条 validation 与 §9.1 的互斥契约。
7. **Dense + BSA-only options → 拒绝非默认值**：决定 §3.1 第 3 条 validation（`dense` 只接受默认 block size 与 `sparsity == 0.0`），防止误用。
8. **Diffusers registration → Model/adapter 边界定向注册**：决定 §8 的 package `__init__` 不导入 attention adapter，仅在 model/adapter setup 时定向注册。

---

## 【公式解读】

### 公式 A：维度定义（原文 §7.1，逐字保留）

```text
N = batch size
Sq = query sequence length
Sk = key sequence length
H = query head count
D = head size
B = block size
s = sparsity
Qb = ceil(Sq / B)
Kb = ceil(Sk / B)
Kkeep = max(1, ceil(Kb * (1 - s)))
Pairs = N * H * Qb * Kkeep
Interactions = Pairs * B * B
```

**符号含义与作用**：
- `N`、`Sq`、`Sk`、`H`、`D`、`B`、`s` —— 维度与 sparsity 基本参数。
- `Qb`、`Kb` —— query 与 key 方向的 block 数（向上取整）。
- `Kkeep = max(1, ceil(Kb * (1 - s)))` —— 每个 query block 实际保留的 KV block 数；`max(1, ...)` 保证 `s < 1` 时每个 query block 至少保留一个 KV block。
- `Pairs = N * H * Qb * Kkeep` —— 全 batch × head 下需要打分的 (query block, kept-KV block) 对数。
- `Interactions = Pairs * B * B` —— 真实交互的 token-pair 数，把 query/KV edge block 都视为 **padded tile** 计算完整 tile 成本；这是 estimator 与"连续 token 模型"的关键区别。

### 公式 B：Compute 成本（原文 §7.2，逐字保留）

```text
QK MMA ops = Interactions * D * 2
PV MMA ops = Interactions * D * 2
Softmax GP ops = Interactions * 4
```

**符号含义与作用**：
- `Interactions` 来自公式 A。
- `QK MMA ops`、`PV MMA ops` —— 两个 BMM 的 MMA op 数；`* D * 2` 表示对每个交互对按 head_dim 做乘加。
- 总 MMA ops 为两个 BMM 之和。
- `Softmax GP ops = Interactions * 4` —— Softmax elementwise 操作数；Softmax dtype 跟随 query dtype，与既有 BSA semantic-op contract 一致。

**示例（原文 §7.2）**：`Sq = Sk = 5`、`B = 4`、`s = 0.5` 时：
```text
Qb = 2
Kb = 2
Kkeep = 1
Interactions per batch/head = 2 * 1 * 4 * 4 = 32
```
旧连续模型得到 `5 * 5 * 0.5 = 12.5` interactions；新模型表达"两个 padded query tiles 各保留一个完整 KV tile"。该示例用于对比 padded 模型与连续 token 模型的差异——注意新模型表达的是 padded tile 而非 token-exact。

### 公式 C：Route generation 成本（原文 §7.3，逐字保留）

```text
RoutePairs = N * H * Qb * Kb
PooledQK GP ops = RoutePairs * D * 2
Selection GP ops = RoutePairs
```

**符号含义与作用**：
- `RoutePairs = N * H * Qb * Kb` —— 完整 block-pair 空间（**不**按 `Kkeep` 缩减），因为 route 选择前必须评估候选 block pairs。
- `PooledQK GP ops = RoutePairs * D * 2` —— 评分每个 block pair 的 Pooled-QK 通用点积 op 数。
- `Selection GP ops = RoutePairs` —— 选中/未选中决策的 GP op 数（每对一次）。

### 公式 D：Route metadata shape（原文 §6，逐字保留）

```text
(batch, num_heads, ceil(query_len / block_size), ceil(key_len / block_size))
```

**符号含义与作用**：表示完整 block-pair route matrix；dtype 为 int32。该 shape 不读取 metadata value，仅被性能模型用于 shape 取整（meta/FakeTensor/compile 兼容，无 data-dependent shape）。

---

## 【关联】

- **TensorCast semantic ops（上游）**：BSA backend 是 TensorCast 把 attention 调用转换为 semantic ops 这一入口上的扩展（见 §1 背景）。Route generation 与 BSA 都被实现为 semantic ops。
- **Diffusers attention dispatch 与 `scaled_dot_product_attention` context（上游入口）**：BSA 通过 Diffusers dispatch 与 direct SDPA 两条路径接入；direct SDPA 路径需要 canonical layout 转置（§4.2）。
- **`use_custom_sdpa(...)` context（容器）**：保存/恢复原始 SDPA function、quant config、route plan、route stats；嵌套 context 必须正确恢复外层状态（§3.2）。
- **`AttentionRoutePlan`（CLI ↔ Runtime 数据载体）**：由 CLI 构造后直接传入 context；包含 `backend`、`block_size`、`sparsity` 三个字段（§3.1）。
- **Attention quantization（互斥模块）**：BSA context 与任何非空 attention quant config 互斥；linear quantization 不受影响（§3.1 第 4 条、§9.1）。
- **Sequence parallelism (SP)（协作模块）**：capability 与 route generation 基于 **all-to-all 后**的 canonical Q/K/V shape；SP cleanup 仅清理 SP group，不清 route plan/stats，由 route context 退出时统一恢复（§9.2）。
- **DiT cache（协作模块）**：main/cache model 共享 run-scoped plan；cache window 仅切换 active model，不切换 backend policy（§9.3）。
- **`torch.compile`（协作模块）**：主/cache 模型可在进入 runtime 前 compile；首次 forward/tracing 发生在 SDPA context 内；eager/compiled 路径使用相同 capability、fallback、stats 实现（§9.4）。
- **CFG（协作模块）**：batch concat / CFG parallel 仅改变 batch/layout；满足 shape 条件时仍走 BSA，不新增专用 policy（§9.5）。
- **Video generation（含 cross-attention 的视频模型）（兼容性约束）**：unsupported call 聚合为 dense fallback，保留视频模型兼容性（§2 决策点 3）。
- **Diffusers registration（注册边界）**：package `__init__` 不导入 attention adapter；由 model/adapter setup 定向注册，避免无关 import 的进程级副作用（§8）。
- **Analytic performance model 校准（下游扩展点）**：estimator 是 analytic approximation；获得 profiling 数据后优先扩展 K/V query-tile reuse efficiency、selected KV union ratio、edge tile 执行方式、route metadata read efficiency；若 route distribution 成为必要输入，扩展 semantic route summary，而非从 scalar sparsity 推断（§7.5）。
- **CLI 标志（用户侧入口）**：`--attention-backend`、`--attention-block-size`、`--attention-sparsity`（§11 文档交付）。
- **回滚路径（运行控制）**：默认 backend 保持 dense；回滚 BSA 只需停止选择 BSA、移除 route/BSA semantic-op dispatch、保留 dense/quantized dense 路径；registration 收缩可独立回退（§12）。

---

## 【使用方法】

**启用方式**：在 CLI 中通过 `--attention-backend block_sparse_attention` 启用；配合 `--attention-block-size`（正整数）和 `--attention-sparsity`（`[0.0, 1.0)`）构造 `AttentionRoutePlan`，再传入 `use_custom_sdpa(...)` 进入 run-scoped BSA context。CLI 构造 plan 后直接传入 context，`DiffusersTransformerConfig` 不保存 plan；main/cache model config 也不保存 plan。Default block size 为 `DEFAULT_BLOCK_SPARSE_ATTENTION_BLOCK_SIZE = 128`。

**合法配置示例（按原文 §3.1 validation 规则推断）**：
- dense：`backend=dense`、`block_size=128`、`sparsity=0.0`；
- BSA：`backend=block_sparse_attention`、`block_size>0`、`0.0 <= sparsity < 1.0`；
- 量化 dense：使用既有 `use_custom_sdpa(quant_config)` positional 调用即可（保持兼容）；
- BSA + linear quantization：BSA context 与 attention quant config 互斥，但 linear 量化不受影响。

**错误配置示例（按原文 §3.1 validation 规则推断）**：
- `dense + sparsity != 0.0`：被 context 拒绝（防止用户误以为参数生效）；
- `dense + block_size != 128`：被 context 拒绝（防止用户误以为参数生效）；
- `BSA + 非空 attention quant config`：被 context 拒绝（CLI 也会在模型构建前给出更早反馈，但仍需依赖 context validation）；
- `block_size <= 0` 或 `sparsity >= 1.0` 或 `sparsity < 0.0`：被 context 拒绝。

**可观测行为**：context 退出时若存在 fallback，logger 输出一条聚合 warning，包含 BSA call 总数、fallback 总数与按 reason 排序的 fallback reason map（reason 取自 §4.1 的 7 个 reason code）；无 fallback 时不输出 warning。Run-scoped stats 至少包含 `block_sparse_attention_calls`、`dense_fallback_calls`、`dense_fallback_reasons: Counter[str]`。

**与 `torch.compile` 配合**：主/cache 模型可在进入 runtime 前调用 `torch.compile`；首次 forward/tracing 发生在 SDPA context 内；eager 与 compiled 路径使用相同 capability、fallback、stats 实现。

**回滚**：将 `--attention-backend` 保持默认 dense；停止选择 BSA、移除 route/BSA semantic-op dispatch、保留 dense/quantized dense 路径即可，不需要迁移模型或配置数据；registration 收缩可独立回退，不影响 estimator 数据结构。

> 说明：原文未给出完整的命令行调用模板或示例脚本，因此上述"启用方式"是基于 §3、§11、§12 推导的契约级描述，而非引用了原文之外的命令。
