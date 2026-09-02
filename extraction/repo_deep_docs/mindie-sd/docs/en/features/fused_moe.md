# Fused MoE

> 仓 `mindie-sd` · 路径 `docs/en/features/fused_moe.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/fused_moe.md

# 一体化深度解读: `docs/en/features/fused_moe.md`

## 【定位】
这篇文档定义了 MindIE-SD 在 NPU 上对 MoE（Mixture of Experts）前向推理的统一入口 `fused_moe`，对外暴露 expert 选择、token 派发、expert 计算与结果合并的一体化 API，让上层框架（vLLM Omni 等）只需传入激活、路由 logits、专家权重与通信配置即可复用同一份 MoE 计算入口。

---

## 【技术要点】

1. **双路径设计**: `fused_moe` 当前版本包含两条路径——**fused operator path**（尚未支持）与 **non-fused operator path**（当前默认）。`use_fused_op=True` 会被回退到非融合路径，因此默认 `use_fused_op=False` 直接走非融合路径。

2. **统一 API 与上层解耦**: 调用方只需提供 `hidden_states`、`router_logits`、`w13_weight`、`w2_weight` 等输入与通信组，框架侧的重复适配成本被下沉到 MindIE-SD 内部，不同并行策略（单卡 / TP / EP）共享同一 MoE 计算入口。

3. **六阶段执行流（non-fused path）**: `prepare` → `select_experts` → `dispatch` → `mlp` → `combine` → `finalize`，分别承担数据组织、top-k 选专家、token 派发重排、分组 MLP、结果回收与通信后处理。

4. **两种 dispatcher 策略**: `static dispatcher`（适用于单卡 / TP 及部分 EP 场景，基于 NPU MoE routing 算子完成 token 排序与恢复）与 `dynamic dispatcher`（专用于 EP 全对全通信场景）。`dispatcher_type=None` 时按平台 + 通信模式自动选择：`Atlas 800I A3 SuperPoD Server / Ascend 950PR / Ascend 950DT` 在 EP 下走 dynamic，`Atlas 800I A2` 在 EP 下走 static；非 EP 场景一律 static。

5. **通信策略互斥**: 同一时刻只启用一种 MoE 通信策略——优先级为 `ep_group > tp_group > 单卡`。调用方需自行保证 `hidden_states` / `router_logits` 的布局与 `inputs_sharded` 一致。

6. **分组路由（grouped routing）参数**: 通过 `k_group`（每 token 选几个专家组，范围 `[1, group_count]`）、`group_count`（专家组总数，`num_experts` 必须可被其整除）、`group_select_mode`（`0`=组内最大分，`1`=组内 top-2 求和，需每组 ≥2 个专家）支持 DeepSeek 式分组路由。

---

## 【关键机制与数据】

### 工作原理（基于原文 non-fused path 描述）

`fused_moe` 接收若干张量后，按以下顺序推进：

1. **prepare**：依据输入布局整理 `hidden_states` 与 `router_logits`，为后续计算准备数据。
2. **select_experts**：根据 router 输出选 top-k 专家并生成路由权重。可通过 `routing_method`（`"softmax"` / `"sigmoid"`）、`renormalize`、`routed_scaling_factor`（默认 `1.0`）、`custom_routing_function`（签名为 `f(hidden_states, gating_output, topk, renormalize) → (topk_weights, topk_ids)`）定制路由策略。
3. **dispatch**：依据选专家结果把 token 重排到对应专家的输入缓冲区；当 EP 启用时还会涉及跨卡 token 交换（dynamic dispatcher 通过 all-to-all 完成）。`inputs_sharded` 声明输入是否已经在 token 维度沿当前 MoE 通信组做过切分。
4. **mlp**：执行专家侧分组 MLP（gate/up 用融合权重 `w13_weight`，down 用 `w2_weight`），完成 routed experts 的前馈计算。
5. **combine**：把专家输出按原 token 顺序恢复为 routed MoE 输出。
6. **finalize**：在结果回收与通信之后做收尾后处理。

### 量化路径

`quant_config`（`QuantConfig`/`None`）启用 MoE 前向中的量化；对应的量化缩放因子通过 `w13_weight_scale` 与 `w2_weight_scale` 传入。

### 性能数据

原文无任何 benchmark / 吞吐 / 延迟数字。

### 数据流（按原文描述）

```
hidden_states ─┐
router_logits ─┼─► prepare ─► select_experts ─► dispatch ─► mlp ─► combine ─► finalize ─► output
w13_weight ────┤                                                                ▲
w2_weight ─────┘                                                                │
(quant_config / weight_scale / tp_group / ep_group / dispatcher_type /         │
 inputs_sharded / routing params 共同控制上述各阶段行为)                        │
                                                                               │
static dispatcher: 在 finalize 阶段按 inputs_sharded 决定是否对 routed 输出 all-reduce（reduce_routed_out）
dynamic dispatcher: 走 all-to-all，结果在 combine 前后恢复 token 顺序
```

---

## 【表格解读】

原文包含 1 张关键参数表（**API 参数表**），下面逐字还原后逐行解读。

| Parameter | Type | Required | Default | Description |
| ------ | ------ | ------ | -------- | ------ |
| `hidden_states` | `torch.Tensor` | Yes | - | Input activations, shape `[..., hidden_size]`, at least 2 dimensions. |
| `router_logits` | `torch.Tensor` | Yes | - | Router logits, shape `[..., num_experts]`, at least 2 dimensions; leading dimensions must match `hidden_states`. |
| `num_experts` | `int` | Yes | - | Total number of experts, must match the last dimension of `router_logits`. Must be divisible by EP group size when using EP. |
| `top_k` | `int` | Yes | - | Number of experts selected per token, range `[1, num_experts]`. |
| `w13_weight` | `torch.Tensor` | Yes | - | Fused gate/up projection weight, shape `[local_experts, hidden_size, 2 * intermediate_size]`, must be a 3D tensor. |
| `w2_weight` | `torch.Tensor` | Yes | - | Down projection weight, shape `[local_experts, intermediate_size, hidden_size]`, must have the same `local_experts` as `w13_weight`. |
| `w13_bias` | `torch.Tensor` / `None` | No | `None` | Gate/up projection bias, shape `[local_experts, 2 * intermediate_size]`, must match `w13_weight` expert and output dimensions. |
| `w2_bias` | `torch.Tensor` / `None` | No | `None` | Down projection bias, shape `[local_experts, hidden_size]`, must match `w2_weight` expert and output dimensions. |
| `quant_config` | `QuantConfig` / `None` | No | `None` | MindIE-SD quantization config for enabling quantization in the MoE forward flow. |
| `w13_weight_scale` | `torch.Tensor` / `None` | No | `None` | Quantization scale for `w13_weight`. |
| `w2_weight_scale` | `torch.Tensor` / `None` | No | `None` | Quantization scale for `w2_weight`. |
| `tp_group` | `dist.ProcessGroup` / `None` | No | `None` | TP communication group. Takes effect when EP is not enabled and TP group size > 1. |
| `ep_group` | `dist.ProcessGroup` / `None` | No | `None` | EP communication group. Takes priority when EP group size > 1. |
| `dispatcher_type` | `str` / `None` | No | `None` | Token dispatch strategy. Options: `"static"`, `"dynamic"`; `None` auto-selects based on platform and communication config. `"dynamic"` is only supported in EP scenarios. |
| `inputs_sharded` | `bool` | No | `False` | Whether inputs are already sharded along the token dimension across the current MoE communication group. |
| `k_group` | `int` | No | `1` | Number of expert groups selected per token in grouped routing, range `[1, group_count]`. |
| `group_count` | `int` | No | `1` | Total number of expert groups; `num_experts` must be divisible by `group_count`. |
| `group_select_mode` | `int` | No | `0` | Expert group scoring method. `0` uses max score within group, `1` uses sum of top-2 scores within group. Each group must have at least 2 experts when using `1`. |
| `routing_method` | `str` | No | `"softmax"` | Router logit scoring method, options: `"softmax"` or `"sigmoid"`. |
| `renormalize` | `bool` | No | `False` | Whether to re-normalize top-k routing weights selected by softmax routing. Sigmoid routing outputs normalized weights per NPU gating top-k operator semantics. |
| `routed_scaling_factor` | `float` | No | `1.0` | Routing weight scaling factor, applied during expert selection. |
| `custom_routing_function` | `callable` / `None` | No | `None` | Custom routing function, called as `custom_routing_function(hidden_states, gating_output, topk, renormalize)`, must return `(topk_weights, topk_ids)`. |
| `reduce_routed_out` | `bool` | No | `True` | Whether the static dispatcher all-reduces routed output when `inputs_sharded=False`. |
| `return_dispatcher_type` | `bool` | No | `False` | Whether to return the resolved dispatcher type together with the MoE output. The dispatcher type is `"static"` or `"dynamic"`. |
| `use_fused_op` | `bool` | No | `False` | Whether to prefer the fused operator path. Currently unsupported; setting `True` falls back to the non-fused path. Default `False` directly uses the non-fused path. |

### 逐行解读

- **`hidden_states` / `router_logits`（必填）**：输入激活与路由器 logits，均要求至少 2 维，前导维度必须一致——这是 select_experts 阶段按 token 维度对应打分的前置条件。
- **`num_experts` / `top_k`（必填）**：`num_experts` 必须等于 `router_logits` 最后一维；EP 场景下还需被 EP group size 整除（专家在 EP 组内可均匀切分）。`top_k ∈ [1, num_experts]`，限定单 token 路由专家数上界。
- **`w13_weight` / `w2_weight`（必填，3D 张量）**：LLaMA / DeepSeek 系 MoE 常见布局——`w13_weight` 把 gate 与 up projection 拼到同一张量的最后一维（`2 * intermediate_size`），`w2_weight` 走 down projection。两者必须保持相同的 `local_experts` 维度（即本卡持有专家数一致）。
- **`w13_bias` / `w2_bias`（可选，默认 `None`）**：是否启用 bias 由调用方决定；若提供，shape 必须与对应权重的专家与输出维对齐。
- **`quant_config` / `w13_weight_scale` / `w2_weight_scale`（可选）**：三件套联合启用 MoE 量化路径——`quant_config` 给出 MindIE-SD 的量化配置对象，两个 `*_weight_scale` 分别喂入 gate/up 与 down 的量化缩放因子。
- **`tp_group` / `ep_group`（可选通信组）**：互斥生效。`ep_group` 优先级最高，`tp_group` 仅在 EP 未启用且 TP size > 1 时生效。
- **`dispatcher_type`（`"static"` / `"dynamic"` / `None`）**：`None` 时由平台 + 通信模式自动选；`"dynamic"` 仅在 EP 下支持；非 EP 一律 static。
- **`inputs_sharded`（默认 `False`）**：声明输入是否已经在 token 维度沿 MoE 通信组切分，决定 dispatcher / reducer 是否还需要做额外的通信。
- **`k_group` / `group_count` / `group_select_mode`（分组路由三件套）**：实现 DeepSeek 风格的专家组路由——先把专家分组再选专家组，`group_select_mode=1` 时要求每组 ≥ 2 个专家才能用 top-2 求和打分。
- **`routing_method` / `renormalize` / `routed_scaling_factor`（路由打分）**：softmax 与 sigmoid 两种打分方式；softmax 可选是否对 top-k 权重 renormalize，sigmoid 则按 NPU gating top-k 算子语义直接产出归一化权重。`routed_scaling_factor` 在选专家阶段对权重做缩放（默认 `1.0`）。
- **`custom_routing_function`（完全自定义）**：签名 `f(hidden_states, gating_output, topk, renormalize) → (topk_weights, topk_ids)`，可在 select_experts 阶段替换默认路由逻辑。
- **`reduce_routed_out`（默认 `True`）**：仅 static dispatcher 在 `inputs_sharded=False` 时对 routed 输出做 all-reduce；`inputs_sharded=True` 时调用方已自行处理。
- **`return_dispatcher_type`（默认 `False`）**：开启后返回 `(output, dispatcher_type)`，便于上层框架做日志/分支判断。
- **`use_fused_op`（默认 `False`，目前不支持）**：开启会被静默回退到非融合路径，是为未来 fused operator path 预留的开关。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 MindIE-SD 主入口 / 量化体系**：本 API 通过 `from mindiesd import fused_moe` 暴露，依赖 MindIE-SD 内部的 `QuantConfig`（`quant_config` 参数）才能启用 MoE 量化路径，因此与 MindIE-SD 的量化配置模块紧耦合。
- **与 vLLM Omni 框架适配**：原文明确"`fused_moe` is the MindIE-SD entry point for MoE … targets open-source framework integration scenarios"，对应上层框架在 NPU 上的 MoE 适配。
- **与 TP / EP 并行策略**：通信优先级 `ep_group > tp_group > 单卡` 决定了它在分布式推理栈中的位置——EP 场景下由 `ep_group` 接管 token 派发，TP 场景下由 `tp_group` 接管专家切分，二者互斥。
- **与硬件平台分支**：dispatcher 自动选择逻辑直接绑定到具体 NPU 型号——`Atlas 800I A3 SuperPoD Server / Ascend 950PR / Ascend 950DT` 走 dynamic dispatcher（EP 下），`Atlas 800I A2` 走 static dispatcher；非 EP 场景一律 static。
- **内部链接**: 原文无内部链接。

---

## 【使用方法】

启用方式（原文给出的最简调用形式）：

```python
from mindiesd import fused_moe
```

随后按 `Function Signature` 调用 `fused_moe(hidden_states, router_logits, num_experts, top_k, w13_weight, w2_weight, ...)` 即可获得 MoE 前向结果；若 `return_dispatcher_type=True`，返回 `(output, dispatcher_type)`。

关键配置项（原文给出，按需启用）：

- **启用 EP**：传入有效 `ep_group`（size > 1）；同步保证 `num_experts` 可被 EP group size 整除；可选 `dispatcher_type="dynamic"`（仅 EP 支持）或 `"static"`。
- **启用 TP**：EP 不启用时传入有效 `tp_group`（size > 1），自动走 TP 路径（默认 static dispatcher）。
- **启用量化**：传 `quant_config=QuantConfig(...)` + 对应 `w13_weight_scale` / `w2_weight_scale`。
- **分组路由**：设置 `k_group`、`group_count`、`group_select_mode`（`group_select_mode=1` 时要求每组 ≥ 2 个专家）；保证 `num_experts` 可被 `group_count` 整除。
- **自定义路由**：提供 `custom_routing_function`，签名 `custom_routing_function(hidden_states, gating_output, topk, renormalize) → (topk_weights, topk_ids)`。
- **切换 routing 方法**：通过 `routing_method="softmax"` / `"sigmoid"`、`renormalize`、`routed_scaling_factor`。
- **输入已切分时**：置 `inputs_sharded=True`，避免 static dispatcher 再做一次 all-reduce（配合 `reduce_routed_out`）。
- **调试 / 日志**：置 `return_dispatcher_type=True` 获取实际生效的 dispatcher 类型。

注意：原文在 `Communication Configuration` 一节末尾被截断（以 "Wh" 结束），完整使用约束（如通信组与输入布局一致性的更具体说明）原文未给出。
