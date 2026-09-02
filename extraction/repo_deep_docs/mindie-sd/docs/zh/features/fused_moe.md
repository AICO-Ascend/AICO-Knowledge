# Fused MoE

> 仓 `mindie-sd` · 路径 `docs/zh/features/fused_moe.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/fused_moe.md

# MindIE-SD `fused_moe` 文档深度解读

## 【定位】
这篇文档描述 MindIE-SD 在 NPU 上提供的统一 MoE（Mixture of Experts）前向推理入口 `fused_moe`，将 MoE 中的专家选择、Token 分发、专家计算和结果合并封装为单一接口，目的是降低开源框架（vLLM Omni、Diffusers+CacheDit、lightx2v 等）在昇腾 NPU 上接入 MoE 的适配成本，并在不同并行策略下复用同一套计算入口。

---

## 【技术要点】

1. **两条路径，目前仅启用非融合算子**：包含"融合算子路径"和"非融合算子路径"。`use_fused_op=True` 时会回退到非融合算子路径；默认 `use_fused_op=False`，直接走非融合算子路径。原文："当前 `fused_moe` 包含两条路径……当前版本暂不支持"。

2. **6 阶段执行流程**：非融合算子路径将 MoE 前向拆为 prepare → select_experts → dispatch → mlp → combine → finalize 共 6 个阶段，覆盖输入整理、专家选择、Token 重排、专家 MLP、结果合并和收尾。

3. **两种 Token 分发策略**：static dispatcher（适用于单卡、TP 以及部分 EP 场景，通过 NPU MoE routing 算子完成 Token 排序、expert token 统计和结果恢复）；dynamic dispatcher（面向 EP all-to-all Token 交换场景）。`dispatcher_type=None` 时按平台自动选择：EP 下 Atlas 800I A3 超节点服务器 / Ascend 950PR / Ascend 950DT 走 dynamic，Atlas 800I A2 推理服务器走 static；非 EP（单卡/TP）始终 static。

4. **通信策略优先级**：接口一次仅启用一种 MoE 通信策略——传入有效 `ep_group` 时优先 EP；未启用 EP 但传入有效 `tp_group` 时使用 TP；二者均未启用按单卡执行。

5. **路由机制可配置**：默认用 NPU gating top-k 算子完成专家选择；`routing_method` 支持 `"softmax"` / `"sigmoid"`；softmax 路由可通过 `renormalize=True` 对 top-k weights 重新归一化；sigmoid 按算子语义输出归一化权重。支持分组路由 `k_group` / `group_count` / `group_select_mode`（`0`=组内最大分，`1`=组内 top-2 分之和，使用 `1` 时每组至少 2 个 experts）。

6. **量化配置**：当前支持 `QuantConfig(quant_algo=QuantAlgorithm.W8A8_DYNAMIC)`（Atlas 800I A2 / Atlas 800I A3）和 `QuantConfig(quant_algo=QuantAlgorithm.W8A8_MXFP8)`（Ascend 950PR / Ascend 950DT）；未传入 `quant_config` 或 `quant_algo` 为 `None` / `NO_QUANT` 时按非量化执行。

---

## 【关键机制与数据】

- **工作原理（数据流，原文）**：调用方传入 `hidden_states`、`router_logits`、`w13_weight`（融合 gate/up）、`w2_weight`（down）和通信配置后，接口内部顺序执行 6 阶段——prepare 整理输入与 layout；select_experts 用 NPU gating top-k（softmax 或 sigmoid）选出每个 Token 的 top-k experts 并产出 routing weights；dispatch 按专家选择结果把 Token 重排（static 用 NPU MoE routing 算子，dynamic 执行 all-to-all）；mlp 在专家侧做 grouped MLP；combine 把专家输出按原 Token 顺序恢复；finalize 完成通信收尾。

- **权重形状（原文）**：`w13_weight` 形状 `[local_experts, hidden_size, 2 * intermediate_size]`；`w2_weight` 形状 `[local_experts, intermediate_size, hidden_size]`，二者 `local_experts` 必须一致；`hidden_states` 维度不少于 2，形状 `[..., hidden_size]`；`router_logits` 形状 `[..., num_experts]`，前置维度与 `hidden_states` 一致；`top_k` 取值 `[1, num_experts]`。

- **EP 与 TP 互斥（原文）**："当前接口一次仅启用一种 MoE 通信策略"——EP 优先于 TP；同时启用并使用 EP 时 `num_experts` 必须能被 EP group size 整除。

- **分组路由约束（原文）**：`num_experts` 能被 `group_count` 整除；`k_group ∈ [1, group_count]`；`top_k` 不超过被选中 expert group 内的 expert 总数；`group_select_mode=1` 时每个 expert group 至少包含 2 个 experts。

- **`inputs_sharded` 语义（原文）**：表示输入是否已经在当前 MoE 通信组内沿 Token 维度 shard；设为 `True` 但实际未 shard 会"可能产生重复 Token 计算"。

- **性能数据**：原文未提供 benchmark / 性能数字。

---

## 【表格解读】

下表逐字还原原文"参数说明"表格，并逐行做简要解读。

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `hidden_states` | `torch.Tensor` | 是 | - | 输入激活，形状为 `[..., hidden_size]`，维度不少于 2。 |
| `router_logits` | `torch.Tensor` | 是 | - | 路由 logits，形状为 `[..., num_experts]`，维度不少于 2，前置维度需与 `hidden_states` 一致。 |
| `num_experts` | `int` | 是 | - | 全局 expert 数量，必须与 `router_logits` 最后一维一致。使用 EP 时需能被 EP group size 整除。 |
| `top_k` | `int` | 是 | - | 每个 Token 选择的 expert 数量，取值范围为 `[1, num_experts]`。 |
| `w13_weight` | `torch.Tensor` | 是 | - | 融合后的 gate/up 投影权重，形状为 `[local_experts, hidden_size, 2 * intermediate_size]`，必须为 3D Tensor。 |
| `w2_weight` | `torch.Tensor` | 是 | - | down 投影权重，形状为 `[local_experts, intermediate_size, hidden_size]`，必须与 `w13_weight` 具有相同的 `local_experts`。 |
| `w13_bias` | `torch.Tensor` / `None` | 否 | `None` | gate/up 投影 bias，形状为 `[local_experts, 2 * intermediate_size]`，需与 `w13_weight` 的 expert 和输出维度一致。 |
| `w2_bias` | `torch.Tensor` / `None` | 否 | `None` | down 投影 bias，形状为 `[local_experts, hidden_size]`，需与 `w2_weight` 的 expert 和输出维度一致。 |
| `quant_config` | `QuantConfig` / `None` | 否 | `None` | MindIE-SD 量化配置，用于选择 MoE 前向流程的量化算法。 |
| `w13_weight_scale` | `torch.Tensor` / `None` | 否 | `None` | `w13_weight` 的 quantization scale。 |
| `w2_weight_scale` | `torch.Tensor` / `None` | 否 | `None` | `w2_weight` 的 quantization scale。 |
| `tp_group` | `dist.ProcessGroup` / `None` | 否 | `None` | TP 通信组。未启用 EP 且 TP group size 大于 1 时生效。 |
| `ep_group` | `dist.ProcessGroup` / `None` | 否 | `None` | EP 通信组。EP group size 大于 1 时优先生效。 |
| `dispatcher_type` | `str` / `None` | 否 | `None` | Token 分发策略。可选 `"static"`、`"dynamic"`；`None` 表示根据平台和通信配置自动选择。`"dynamic"` 仅支持 EP 通信场景。 |
| `inputs_sharded` | `bool` | 否 | `False` | 表示输入是否已经在当前 MoE 通信组内沿 Token 维度 shard。 |
| `k_group` | `int` | 否 | `1` | 分组路由时每个 Token 选择的 expert group 数量，取值范围为 `[1, group_count]`。 |
| `group_count` | `int` | 否 | `1` | expert group 总数，`num_experts` 需要能被 `group_count` 整除。 |
| `group_select_mode` | `int` | 否 | `0` | expert group 打分方式。`0` 表示取组内最大分数，`1` 表示取组内 top-2 分数之和。使用 `1` 时每组至少需要 2 个 experts。 |
| `routing_method` | `str` | 否 | `"softmax"` | router logits 的打分方式，可选 `"softmax"` 或 `"sigmoid"`。 |
| `renormalize` | `bool` | 否 | `False` | 是否对 softmax 路由选中的 top-k routing weights 重新归一化。sigmoid 路由按 NPU gating top-k 算子语义输出归一化后的权重。 |
| `routed_scaling_factor` | `float` | 否 | `1.0` | 路由权重缩放系数，在专家选择阶段生效。 |
| `custom_routing_function` | `callable` / `None` | 否 | `None` | 自定义路由函数，调用形式为 `custom_routing_function(hidden_states, gating_output, topk, renormalize)`，需返回 `(topk_weights, topk_ids)`。 |
| `reduce_routed_out` | `bool` | 否 | `True` | static dispatcher 在 `inputs_sharded=False` 时是否对 routed output 做 all_reduce。 |
| `return_dispatcher_type` | `bool` | 否 | `False` | 是否在输出中返回实际解析到的 dispatcher 类型，返回值为 `"static"` 或 `"dynamic"`。 |
| `use_fused_op` | `bool` | 否 | `False` | 是否优先启用融合算子路径。当前版本暂不支持该路径，设置为 `True` 时会回退到非融合算子路径；默认 `False` 直接使用非融合算子路径。 |

**逐行解读要点：**

- **必选 6 项**：`hidden_states` / `router_logits` / `num_experts` / `top_k` / `w13_weight` / `w2_weight`——构成 MoE 前向最基本输入；其余参数都有默认值。
- **权重维度约定**：`w13_weight` 把 gate 和 up 两个投影沿最后一维拼接为 `2 * intermediate_size`（典型 Mixtral 风格），因此对应 `w13_bias` 也是 `[..., 2 * intermediate_size]`。
- **量化相关**：`quant_config` + `w13_weight_scale` + `w2_weight_scale` 是量化路径三件套；只有当 `quant_algo` 非空时这些 scale 才会被实际使用。
- **通信互斥**：`tp_group` 与 `ep_group` 不能同时启用（接口优先级为 EP > TP > 单卡），`dispatcher_type="dynamic"` 仅在 EP 场景下可用。
- **`inputs_sharded` 是布局契约**：调用方必须保证 `hidden_states` / `router_logits` 的 Token 维是否已经按通信组 shard 过，与 `inputs_sharded` 标记一致；否则会出现重复 Token 计算。
- **分组路由三参数**：`k_group` / `group_count` / `group_select_mode` 三者需共同满足约束（见技术要点 5）。
- **`renormalize` 仅对 softmax 有意义**：sigmoid 路由的归一化由 NPU gating top-k 算子内部决定，不由该开关控制。
- **`use_fused_op` 当前为预留开关**：即便设为 `True` 也会回退到非融合算子路径，是为后续融合算子版本留出的兼容入口。
- **`return_dispatcher_type`**：开启后返回值变为 `(output, dispatcher_type)`，可用于上层框架校验实际分发路径是否符合预期。

---

## 【公式解读】

原文无公式。

（文档未出现 LaTeX 数学式或伪代码公式；只有参数表的张量形状描述，例如 `[..., hidden_size]`、`[local_experts, hidden_size, 2 * intermediate_size]`，这些是形状约定而非公式。）

---

## 【关联】

- **与上下文的关联（仓库定位）**：mindie-sd 是昇腾亲和的多模态加速系列套件，支持 vLLM Omni、Diffusers+CacheDit、lightx2v 等框架；`fused_moe` 作为统一的 MoE 前向入口，主要服务于这些框架在 NPU 上接入 MoE 模型（如 Mixtral 等）时的专家选择 / Token 路由 / 通信 / 专家计算流程。
- **与 NPU 原生算子的关联**：static dispatcher 依赖 NPU MoE routing 算子完成 Token 排序、expert token 统计与结果恢复；select_experts 阶段默认使用 NPU gating top-k 算子——softmax/sigmoid 路由的归一化与权重排序都封装在该算子内部。
- **与量化体系的关联**：`fused_moe` 的量化路径与 MindIE-SD 的 `QuantConfig` / `QuantAlgorithm` 体系对齐，当前通过 `quant_config` 参数切换 `W8A8_DYNAMIC` / `W8A8_MXFP8`，分别覆盖 Atlas 800I A2 / A3 与 Ascend 950PR / 950DT 硬件。
- **与并行策略的关联**：通过 `tp_group`（TP 通信组）与 `ep_group`（EP 通信组）实现分布式 MoE 推理；EP 与 TP 互斥，EP 优先生效。
- **内部链接**：原文末尾未提供任何内部链接（标注"无"）。

---

## 【使用方法】

### 1. 安装入口
```python
from mindiesd import fused_moe
```

### 2. 单卡 MoE
不传任何通信组；按原文示例设置 `num_tokens=8`、`hidden_size=4096`、`intermediate_size=14336`、`num_experts=8`、`top_k=2`、`dtype=torch.bfloat16`、`device="npu"`，并传入 `w13_weight` / `w2_weight` / `w13_bias` / `w2_bias`，通过 `renormalize=True` 对 softmax 选中的 top-k weights 重新归一化。

### 3. 分组路由 MoE（sigmoid 路由 + 路由权重缩放）
原文示例：`num_experts=16`、`top_k=2`、`k_group=1`、`group_count=4`、`group_select_mode=1`（取组内 top-2 分数之和）、`routing_method="sigmoid"`、`routed_scaling_factor=0.5`——表示每个 Token 先在 4 个 expert group 中按 top-2 分之和选出 1 个 group，再在选中 group 内选 top-2 experts，并按 0.5 缩放路由权重。

### 4. W8A8 dynamic quant MoE（Atlas 800I A2 / A3）
原文：要求 `w13_weight` 与 `w2_weight` 为 `torch.int8`，并传入对应的 quantization scale；MindIE-SD 会在 MLP 计算前检查权重格式，若权重不是 NPU NZ 格式会自动转换为 NPU NZ 格式（原文示例在本节末尾被截断，剩余配置 / 代码片段未在文档中给出）。

### 5. dispatcher 显式指定
通过 `dispatcher_type="static"` 或 `dispatcher_type="dynamic"` 显式指定 Token 分发策略；置 `None` 则按平台自动选择（详见技术要点 3）。

### 6. 自定义路由
通过 `custom_routing_function` 注入自定义路由函数，签名 `custom_routing_function(hidden_states, gating_output, topk, renormalize) -> (topk_weights, topk_ids)`，可覆盖默认 NPU gating top-k 算子行为。

### 7. 返回 dispatcher 类型
设置 `return_dispatcher_type=True`，接口返回 `(output, dispatcher_type)` 元组，便于上层框架校验实际运行的分发路径。

> 注：原文末尾"W8A8 dynamic quant MoE"示例在"自动转换为 N"处被截断，更完整的 Python 示例以仓库源码 / 后续文档为准。
