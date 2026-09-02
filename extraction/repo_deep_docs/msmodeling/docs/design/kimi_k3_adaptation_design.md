# 特性设计：TensorCast 适配 Kimi K3 模型

> 仓 `msmodeling` · 路径 `docs/design/kimi_k3_adaptation_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/kimi_k3_adaptation_design.md

# 一体化深度解读：TensorCast 适配 Kimi K3 模型（`docs/design/kimi_k3_adaptation_design.md`）

---

## 【定位】

本文档系统性描述了 **TensorCast（msmodeling 中负责 prefill/decode 仿真与算子级性能建模的子系统）如何适配 Moonshot AI 发布的 2.8T 参数原生多模态 agentic 模型 Kimi K3**——重点解决 K3 因引入全新自研结构（KDA 线性注意力、Latent MoE、SiTU-GLU 激活、AttnRes 跨层残差、MLA Output Gate、MoonViT-V2）而无法被现有仿真框架直接加载、编译和建模的 10 类适配缺口，同时给出三种部署拓扑（A3 4 节点混合、A3 16 节点 PD 分离、A2 8 节点混合）以支撑 TP/EP/PP 并行配置选型与算子级瓶颈分析。

---

## 【技术要点】

1. **核心隔离原则**：所有 K3 适配集中在单个文件 `kimi_k3.py`，通过 `model_type == "kimi_k3"` 门控严格隔离，绝不污染已有模型路径，采用 "最小侵入 + 单文件隔离" 原则。
2. **K3 模型规格基础参数**（原文）：总参 2.8T / 激活约 104B；上下文 `max_position_embeddings=1048576`（1M token）；`hidden_size=7168`；文本 decoder 93 层 = 69 层 KDA + 24 层 Gated MLA；MoE `896 专家选 16 + 2 共享专家`；`first_k_dense_replace=1`（层 0 为 Dense MLP）；`attn_res_block_size=12`。
3. **三种部署拓扑**（原文）：① A3 4 节点混合 — DP4/TP16/EP64；② A3 16 节点 PD 分离 — 8 Prefill + 8 Decode，两侧均 DP8/TP16/PP1；③ A2 8 节点混合 — DP8/TP8/EP64。
4. **10 项核心适配缺口**（原文 §1.4 表）：`fla-core` 缺失导致 import 阶段 raise ImportError；`SituAndMul` 激活（`beta*tanh(g/beta)*sigmoid(g)*up`）找不到对应算子；混合注意力路由（KDA vs MLA）；Latent MoE 的 `routed_expert_down_proj/norm/up_proj` 包裹层被 `patch_moe` 丢弃；MLA `mla_use_output_gate=True` 不在现有 `multihead_latent_attention` op 路径中；AttnRes `block_residual` 跨层状态需 stub；`KimiDynamicCache` 的 `conv_states/recurrent_states/key_cache/value_cache` 需识别；VL forward kwargs 过滤与 `image_grid_thw vs grid_thws` 映射；视觉 `nn.RMSNorm` 受 `_dynamo.disable` 阻断 pattern pass 融合；Transformers v5.x 移除 `is_torch_fx_available` 等 API 引起的兼容问题。
5. **算子复用矩阵**（原文 §2.4–§2.6）：KDA 复用 `linear_attn_causal_conv` / `linear_attn_fused_gdn_gating` / `linear_attn_chunk + linear_attn_recurrent_gated_delta_rule` / `linear_attn_gated_rmsnorm` 并补 `full_rank_gate` 标志位；Gated MLA 复用 K2.5 MLA patch 并新增 `g_proj + sigmoid` 输出门控路径（TP 切片关注点见 §2.5 ⑤TP 要点）；Latent MoE 新增降维/升维两次 grouped_matmul 与中间 `KimiRMSNorm`，并引入 `situ` 算子替代 swiglu。
6. **关键 hidden bugs**（原文 §2.4）：① KDA 按 q 形状与 KV cache 自动判路径，MTP 开启会改 `query-length`，已由 P9 `_patched_kda_forward` 将整个 forward 替换为单一 `torch.ops.tensor_cast.linear_attention`，由性能模型按 `cache_position/seq_len` 自区分；② `chunk_kda="矩阵乘+状态递推"` 混合，仿真器可能漏掉状态递推，待精度需求明确后拆分。

---

## 【关键机制与数据】

### 工作原理（基于原文 §2.3–§2.6 数据流）

**整体分层与路由机制**：每个 `KimiDecoderLayer` 由两个 `config.is_kda_layer(layer_idx)` 类型分支选择注意力——`True` 走 `KimiDeltaAttention`（KDA 线性注意力，69 层），`False` 走 `KimiMLAAttention`（Gated MLA 全注意力，24 层）；MLP 侧由 `layer_idx >= first_k_dense_replace (=1)` 决定——`False` 走 `KimiMLP`（dense，仅层 0），`True` 走 `KimiSparseMoeBlock`（MoE，层 1..92）；输入归一化 `input_layernorm` 映射为仿真算子 `tensor_cast.rms_norm`，`post_attention_layernorm` 映射为 `tensor_cast.add_rms_norm2`；AttnRes 以 12 层为粒度跨层传递 `block_residual`，含 `self_attention_res_norm + self_attention_res_proj` 与 `mlp_res_norm + mlp_res_proj` 四个子模块。

**KDA 数据流（原文 §2.4，6 步流水）**：
- ① QKV 标准 Linear → q/k/v 形状 `[B,S, 96×128]`（`num_heads=96`, `head_dim=128`）
- ② 三路独立 `ShortConvolution`（`kernel=4`）+ silu，复用算子 `linear_attn_causal_conv`，作用是补线性注意力 "局部感知弱" 缺陷
- ③ 并行门控生成：`f_a_proj + f_b_proj → g [B,S,96,128]`（控 S 老状态衰减），`b_proj → beta [B,S,96]`（控 S 新信息写入），复用 `linear_attn_fused_gdn_gating`
- ④ KDA 核心：prefill 走 `chunk_kda`（并行展开），decode 走 `fused_recurrent_kda`（逐 token 递归），需 stub `fla.ops.kda`
- ⑤ 输出门控：`g_proj` `7168→12288` 一步 GEMM（`full_rank_gate` 变体），后接 `FusedRMSNormGated(o, g)`，复用 `linear_attn_gated_rmsnorm`
- ⑥ `o_proj` 标准 Linear 回 `[B, S, 7168]`

**Gated MLA 数据流（原文 §2.5，6 步流水）**：
- ① Q 低秩 `q_a_proj → q_a_layernorm → q_b_proj`：7168→1536（`q_lora_rank`）→12288，Q 不进 KV cache
- ② KV 低秩 `kv_a_proj_with_mqa → kv_a_layernorm → kv_b_proj`：7168→512（`kv_lora_rank`）→12288，瓶颈 r=512 比标准 MHA 的 12288 维小 24×，维度拆分为 `qk_nope_head_dim=128`（不加 RoPE）+ `qk_rope_head_dim=64`（加 RoPE）
- ③ RoPE 旋转位置编码（复用 `apply_rope`；`mla_use_nope=True` 时为 identity；需 position_ids patch 同 K2.5 P9）
- ④ `multihead_latent_attention` op（复用现有）
- ⑤ ★K3 独有 Output Gate：`g_proj: 7168→96×128` + sigmoid 门控乘法，要求 TP 切片后按 rank 切片再乘
- ⑥ `o_proj` 标准 Linear

**Latent MoE 数据流（原文 §2.6，6 步流水）**：
- ① `KimiMoEGate`：`sigmoid + noaux_tc top-k`，复用 K2.5 gate patch
- ② ★新增 `routed_expert_down_proj: 7168→3584`（`routed_expert_hidden_size`），P1.7 保留以免被 `patch_moe` 丢弃
- ③ 896 个 `KimiBlockSparseMLP` 每专家 = `w1(gate) + w3(up) → situ → w2(down)`（grouped_matmul），命名采用 `w1/w2/w3` 而非标准的 `gate_proj/up_proj/down_proj`
- ④ `dispatch_ffn_combine` 按 `topk_weight` 加权求和
- ⑤ ★新增 `routed_expert_norm`（KimiRMSNorm，作用于 3584 维 latent，`latent_moe_use_norm=true`）+ `routed_expert_up_proj: 3584→7168`
- ⑥ 共享专家 `shared_experts = KimiMLP × 2`（`num_shared_experts=2`）

### 关键性能数据（原文出现）

| 类别 | 关键数据 | 原文位置 |
|------|---------|---------|
| 模型规模 | 2.8T 总参，约 104B 激活 | §1.1 |
| 上下文窗口 | `max_position_embeddings=1048576`（1M token） | §1.1 |
| KDA 配置 | 69 层 KDA / 24 层 MLA；短卷积 `kernel=4`（`short_conv_kernel_size`）；head 96×128 | §1.1, §2.4 |
| MLA 低秩 | `q_lora_rank=1536`，`kv_lora_rank=512`，`hidden_size=7168`；KV cache 压缩比 24× | §2.5 |
| MoE 专家 | 896 选 16 + 2 共享；`routed_expert_hidden_size=3584` | §1.1, §2.6 |
| SiTU-GLU 参数 | `beta=4.0`，`linear_beta=25.0`，公式 `beta*tanh(g/beta)*sigmoid(g)*up` | §1.1, §1.4 |
| MXFP4 量化 | `compressed-tensors`，`group_size=32` | §1.1 |
| AttnRes | `attn_res_block_size=12` | §1.4 |
| MoonViT-V2 | 27 层 3D ViT；显式定义 `use_deterministic_attn` | §1.1, §2.2 |
| 拓扑规模 | A3 4 节点（DP4/TP16/EP64）；A3 16 节点 PD 分离（DP8/TP16/PP1）；A2 8 节点（DP8/TP8/EP64） | §1.2 |

> 备注：原文 §1.4 表 P9 明确 `_patched_kda_forward` 通过整体替换为 `torch.ops.tensor_cast.linear_attention` 让性能模型自区分路径；文本明示 "chunk_kda 可能漏状态递推，待精度需求明确后拆分"，尚未给出具体的仿真耗时/吞吐量数字。

---

## 【表格解读】

### 表 1：§1.1 模型概览规格表（原文逐字还原）

| 维度 | 规格 |
|------|------|
| 总参 / 激活 | 2.8T 总参，约 104B 激活 |
| 上下文窗口 | 1M token（`max_position_embeddings=1048576`） |
| 文本架构 | KDA（Kimi Delta Attention，K3 自研线性注意力）+ AttnRes（跨层注意力残差）混合，69 层 KDA + 24 层 MLA |
| MoE 框架 | Stable LatentMoE（专家前后含降维/升维投影），896 专家选 16，2 共享专家 |
| 激活函数 | SiTU-GLU（K3 自定义激活，`beta=4.0`，`linear_beta=25.0`） |
| 视觉编码器 | MoonViT-V2（27 层 3D 视觉 transformer） |
| 量化 | 权重自带 MXFP4 压缩（`compressed-tensors`，`group_size=32`） |

**逐行解读**：
- **总参 / 激活**：2.8T 是 "权重总量"，104B 是 "每 token 计算时实际激活" 的部分，激活量直接决定单步算力消耗与 TP/EP 设计边界。
- **上下文窗口**：1M token 是 `max_position_embeddings=1048576` 的字面含义，长上下文下 KV cache 内存压力激增，是 KDA 用线性注意力替代 softmax 注意力的关键驱动因素之一。
- **文本架构**：69 KDA + 24 MLA 混合由 `config.is_kda_layer(layer_idx)` 路由；AttnRes 跨层补偿 KDA 的长程记忆损失。
- **MoE 框架**：Stable LatentMoE 在标准 MoE 之上额外做 `hidden_size → routed_expert_hidden_size` 的降维与升维，是本文档需要单独适配 §2.6 ⑤ 路径的根因。
- **激活函数**：SiTU 公式 `beta*tanh(g/beta)*sigmoid(g)*up` 与标准 SwiGLU 不同，导致 §1.4 表 "act_fn 映射失败" 与 §2.6 ③★ "situ 替代 swiglu" 的具体任务。
- **视觉编码器**：27 层 3D ViT 比 K2.5 更简单，因显式定义 `use_deterministic_attn`，但视觉 `nn.RMSNorm` 因 `_dynamo.disable` 无法被融合。
- **量化**：MXFP4 `group_size=32` 表示每 32 个权重共享一组 scale/zero，原文强调 "权重自带"，不在仿真中触发重压缩。

---

### 表 2：§1.4 核心适配缺口表（原文逐字还原，10 项）

| # | 缺口 | 影响 |
|---|------|------|
| 1 | `fla-core` 依赖缺失 | `modeling_kimi_linear.py` 顶部硬性 `raise ImportError`，import 阶段即失败，需 stub `fla` 到 `sys.modules` |
| 2 | `situ` 激活算子缺失 | expert MLP 用 `SituAndMul`（`beta*tanh(g/beta)*sigmoid(g)*up`），现有 `swiglu` / `v4_clamped_swiglu` 无法识别，grouped_matmul 性能模型 act_fn 映射失败 |
| 3 | 混合注意力路由 | 93 层中 69 层 KDA + 24 层 Gated MLA，由 `config.is_kda_layer(layer_idx)` 分支控制；KDA 层需路由到 `linear_attention` op |
| 4 | Latent MoE 结构差异 | `KimiSparseMoeBlock` 在专家前后增加 `routed_expert_down_proj` → 专家 → `routed_expert_norm` → `routed_expert_up_proj` 包裹层，`patch_moe` 会丢弃这些投影 |
| 5 | MLA Output Gate | K3 MLA 设 `mla_use_output_gate=True`，输出经 `g_proj` + sigmoid 门控乘法，`multihead_latent_attention` op 不含此路径 |
| 6 | AttnRes 跨层残差 | `attn_res_block_size=12` 的 `_forward_attn_residual` 含 `block_residual` 跨层状态，torch.compile 追踪需 stub |
| 7 | KimiDynamicCache | `_supports_default_dynamic_cache=False`，自定义 cache 含 `conv_states`/`recurrent_states`/`key_cache`/`value_cache`，需识别并 stub |
| 8 | VL Forward 接口差异 | kwargs 过滤、`image_grid_thw` vs `grid_thws` 参数名映射、meta device merge 失败（同 K2.5） |
| 9 | 视觉编码器适配 | K3 `MoonViT3dEncoder` 已显式定义 `use_deterministic_attn`（比 K2.5 简单），但仍需注册 `tensor_cast` attention backend；视觉 `nn.RMSNorm` 因 `_dynamo.disable` 无法被 pattern pass 融合 |
| 10 | Transformers 环境兼容 | 依赖 `is_torch_fx_available`（transformers v5.x 已移除）、`flash_attention_2`（未安装不可用）、`OutputRecorder`（5.13+ 移除）、`create_causal_mask` 签名变更 |

**逐行解读**：
- **1 fla-core**：原文将 KDA 实现放在 `fla` 库，仿真侧无法安装，遂用 `sys.modules` stub 让 import 通过，再用 P9 替换 forward。
- **2 situ**：与 `#1` 不同的是该缺口在 expert MLP 的 grouped_matmul 中通过 `act_fn` 字段被性能模型识别，所以需要新增 `situ` 算子的映射分支。
- **3 路由**：仿真器需要读取 `config.is_kda_layer` 决定走 `linear_attention` 还是 `multihead_latent_attention` 算子，否则整图算子表填错。
- **4 Latent MoE**：降维/升维两次 grouped_matmul + 中间 RMSNorm 是 K3 与 K2.5 DeepseekV3 路径最本质差异；`patch_moe` 默认会重写 wrapper，包裹层被无声丢弃，必须 P1.7 标记保留。
- **5 MLA Output Gate**：`g_proj` 输出 `[B,S,96,128]` 与 attn_out 同形，逐元素相乘；但 TP 下 `attn_out` 已按 head 切分，`gate` 必须按 rank 切片后才能相乘（参 §2.5 P13b）。
- **6 AttnRes**：`block_residual` 跨 12 层传递，torch.compile 追踪跨函数状态需 stub。
- **7 KimiDynamicCache**：K3 把 cache 拆为 `conv_states`（短卷积状态）+ `recurrent_states`（线性注意力递推状态）+ 标准 `key_cache/value_cache`，仿真器需识别全部 4 个 buffer。
- **8 VL Forward**：文本侧仿真通常不触发视觉，但若做多模态端到端仿真则需修复 kwargs 过滤。
- **9 视觉编码器**：MoonViT-V2 比 K2.5 简单，但仍需注册 TC attention backend（含 sdpa key 见 P8）；视觉 `nn.RMSNorm` 因 `_dynamo.disable` 阻断 P1.14 融合。
- **10 Transformers 兼容**：四项全是版本兼容性问题，`is_torch_fx_available` 在 v5.x 被移除，需要在 kimi_k3.py 中按 K2.5 的方式补齐 mock。

---

### 表 3：§2.2 VL 三件套顶层结构表（原文逐字还原）

| 组件 | 类 | 职责 | 适配要点 |
|------|-----|------|----------|
| `vision_tower` | `MoonVit3dPretrainedModel` | 3D 视觉编码器（27 层 `MoonViTEncoderLayer`），含 patch 化 + 2D RoPE + 注意力；详细算子级结构见 §2.8 视觉部分 | `use_deterministic_attn` 已显式定义（比 K2.5 简单）；需注册 `tensor_cast` attention backend（含 sdpa key，见 P8）；视觉 `nn.RMSNorm` 需 P1.14 融合 |
| `mm_projector` | `PatchMergerMLPV2` | 多模态投影器，视觉特征对齐到语言维度 `hidden_size=7168`；`tpool_patch_merger` 对时间维度下采样；详细结构见 §2.8 MM Projector 部分 | 未 TP 切分（文本仿真不触发） |
| `language_model` | `KimiLinearForCausalLM`（`model_type="kimi_linear"`，全新自研） | 文本 decoder：`embed_tokens` + 93 层 `KimiDecoderLayer`（见 §2.3）+ 模型级最终 `norm` + AttnRes 输出归一化/投影 + `lm_head` | 实际切分树见 §2.8；`lm_head` 需 P1.13 修复 VL 嵌套 TP |

**逐行解读**：
- **vision_tower**：3D ViT（27 层）的适配关键在 attention backend 注册和 RMSNorm 融合是否被 `_dynamo.disable` 阻断。
- **mm_projector**：将视觉特征压到语言维度（7168），含时间下采样 `tpool_patch_merger`；原文明示 "文本仿真不触发"，意味着 TP 配置仿真只在 language_model 上做。
- **language_model**：实际承载 TP/EP/PP 切分的容器，93 层 KimiDecoderLayer + 最终 norm + lm_head；`lm_head` 因 VL 嵌套需 P1.13 修复。

---

## 【公式解读】

> **原文无独立数学公式**——文档以文本伪代码与 ASCII 数据流图承载结构与算子关系。但有两处关键算子级伪公式值得逐字保留与解读：

### 伪公式 1：SiTU 激活算子语义（原文 §1.4 表第 2 行 + §1.1 表"激活函数"）

$$\text{SiTU}(g, up) = \beta \cdot \tanh\!\left(\frac{g}{\beta}\right) \cdot \text{sigmoid}(g) \cdot up$$

**符号含义**：
- $\beta = 4.0$（常数，原文 §1.1 表）
- $\text{linear\_beta} = 25.0$（常数，原文 §1.1 表；用于控制线性域段强度）
- $g$：gate 分支输入（专家 MLP 的 w1 输出）
- $up$：up 分支输入（专家 MLP 的 w3 输出）
- 整体语义：先对 $g$ 做截断（$\tanh(g/\beta)$ 限制到 $(-1,1)$），再乘 $\beta$ 恢复量级，同时用 $\text{sigmoid}(g)$ 控制信息流，最后逐元素乘 $up$——与 SwiGLU 的 `silu(g) * up` 形成对比，故 sim 阶段需为 grouped_matmul 注册独立的 `act_fn="situ"` 映射。

### 伪公式 2：KDA 线性注意力递推语义（原文 §2.4 备注 + 数据流 ④）

原文未给出 $S$ 递推的显式数学形式，但描述为 "矩阵乘+状态递推" 混合：prefill 用 `chunk_kda`（并行展开），decode 用 `fused_recurrent_kda`（逐 token 递归），所有历史 token 压进固定大小的 `recurrent_state` $S$：
$$S_{t+1} = f(g_t, \beta_t, S_t, k_t, v_t, q_t)$$
**符号含义**（原文隐含语义）：
- $S_t$：固定大小递推状态，`KimiDynamicCache.recurrent_states`
- $\beta_t \in \mathbb{R}^{96}$：写入强度（控制新信息写入），由 `b_proj` 生成（原文 §2.4 ③）
- $g_t \in \mathbb{R}^{96,128}$：状态衰减门控，由 `f_a_proj + f_b_proj` 生成（原文 §2.4 ③）
- $q_t, k_t, v_t$：经 `ShortConvolution(k=4)` + silu 预处理后的 QKV
- 隐藏坑：原文明示 "chunk_kda 是矩阵乘+状态递推混合，仿真器可能漏掉状态递推"——意味着仿真在 prefill 路径上既要建 matmul 也要建递推算子。

---

## 【关联】

文档明示的上下游/横向关系：

1. **与 K2.5 的关系**：§1.4 明确指出 K3 的 `model_type="kimi_linear"` 是 "全新自研架构，与 Kimi K2.5 复用 DeepseekV3 的路径完全不同"；但具体 patch 实现层面**复用**了 K2.5 的 ① K2.5 MLA patch（§2.5 ①/②/③ 与 §2.5 ④ "复用现有 MLA op"）；② K2.5 gate patch（§2.6 ① "复用 K2.5 gate patch"）；③ K2.5 P9（§2.4 MTP 规避与 §2.5 ③ position_ids patch）；④ K2.5 P13（§2.2 `lm_head` 嵌套 TP 修复）。本文适配在结构层是全新，在算子映射层复用。
2. **与 TensorCast 算子库**：所有适配的目标是把 K3 的新结构映射到 TC（TensorCast）的统一 op 抽象层——`linear_attention_causal_conv`、`linear_attn_fused_gdn_gating`、`linear_attn_chunk/recurrent_gated_delta_rule`、`linear_attn_gated_rmsnorm`、`multihead_latent_attention`（复用 K2.5）、`grouped_matmul`（MoE 专家 + Latent MoE 降升维）、`tensor_cast.rms_norm`、`tensor_cast.add_rms_norm2`（对照 §2.3 input/post layernorm）。
3. **与 patch 体系**：文中频繁引用编号 patch，**P1.7** = "保留 Latent MoE 额外 grouped_matmul 不被 `patch_moe` 丢弃"（§1.4#4, §2.6 ②/⑤）；**P1.13** = "VL 嵌套 TP 下修复 `lm_head`"（§2.2）；**P1.14** = "融合视觉 `nn.RMSNorm`"（§2.2, §1.4#9）；**P8** = "注册 `tensor_cast` attention backend（含 sdpa key）"（§2.2, §1.4#9）；**P9** = "MTP 规避与 position_ids patch"（§1.4#3 隐含, §2.4 ④★隐藏坑1, §2.5 ③）；**P13b** = "Output Gate 在 TP head 切分后按 rank 切片"（§2.5 ⑤★）。
4. **与远端依赖**：① `fla-core`——`fla.ops.kda` 模块整体被 stub（§1.4#1, §2.4 ④）；② `transformers` v5.x——`is_torch_fx_available` 移除、`flash_attention_2`、`OutputRecorder`、`create_causal_mask` 签名变更共 4 处需 mock（§1.4#10）；③ `compressed-tensors`（MXFP4 `group_size=32`，§1.1）——仅声明存在，仿真不触发解码。
5. **与 vLLM 运行时**：§1.2 部署拓扑全部使用 vLLM 数据并行跨节点（DP4/DP8），每节点一个 DP rank，节点内 NPU 张量并行（TP16/TP8）；PD 分离将 prefill/decode 拆到 8+8 节点。

---

## 【使用方法】

> 原文未明确给出独立的 "启用方式 / CLI 参数" 段落，但散落多处提及配置条件，整理如下：

| 项目 | 配置 / 操作 | 原文位置 |
|------|-------------|---------|
| 加载模型方式 | `trust_remote_code=True`（社区远端模型） | §1.4 引言 |
| 适配文件 | `kimi_k3.py`（单文件隔离） | §1.4 引言 |
| 门控条件 | `model_type == "kimi_k3"` 严格隔离既有模型 | §1.4 引言 |
| fla stub | stub `fla` 到 `sys.modules`，绕过 `raise ImportError` | §1.4 表 #1 |
| MTP 规避 | P9 `_patched_kda_forward` 整体替换为 `torch.ops.tensor_cast.linear_attention` | §2.4 ★隐藏坑1 |
| MLA Output Gate TP | `gate` 须按 head 切分后的 rank 切片再与 `attn_out` 相乘（P13b） | §2.5 ⑤ |
| KDA 标志位 | `use_qk_l2norm` / `use_gate` / `use_beta_sigmoid` / `safe_gate` / `lower_bound` | §2.4 ④ |
| 拓扑选型 | A3 4 节点 DP4/TP16/EP64；A3 16 节点 PD 分离 DP8/TP16/PP1；A2 8 节点 DP8/TP8/EP64 | §1.2 |
| Patch 体系 | P1.7 / P1.13 / P1.14 / P8 / P9 / P13b 在 kimi_k3.py 中按需启用 | §1.4, §2.4, §2.5, §2.6 |
| Transformers 版本约束 | 依赖 v5.x 已移除的 `is_torch_fx_available`，需在 kimi_k3.py 中按 K2.5 mock 方式补齐 | §1.4 表 #10 |

---

### 已知信息缺口（基于原文边界声明）

> 原文在 §2.6 "（shared_out ※ 命名标准 (gate_proj/up_proj/down_" 处被截断，**§2.7 与之后章节（含 §2.8 视觉/MM Projector 详细算子结构）尚未在所提供的原文中呈现**。本解读严格基于已提供的原文内容，未对缺失章节做推测；后续若获得完整原文，可补充（但不臆造）§2.7+ 的逐层算子切分树与视觉/MM Projector 详细算子级结构。
