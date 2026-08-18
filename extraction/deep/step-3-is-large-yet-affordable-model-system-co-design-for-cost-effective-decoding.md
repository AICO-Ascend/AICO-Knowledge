# Step-3 — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Step-3 is Large yet Affordable: Model-system Co-design for Cost-effective Decoding · StepFun Inc. · arXiv:2507.19427v1

## 核心问题

在 test-time scaling 范式下，LLM 推理的 **decoding 阶段** 成为最昂贵环节（§1）：相比训练与 prefill，decoding 因 MFU 极低而单 token 成本最高；对 reasoning 模型，decoding 成本直接决定固定预算下的智能上限；同时 cheaper decoding 还能加速 RL 训练。然而当前开源大模型在 decoding 成本优化上存在两个系统性 suboptimal 实践（§1）：

1. **注意力侧**：过度追求压缩 KV cache，却以过高计算开销为代价 —— 导致模型难以跑在更廉价、更弱算力的硬件上，同时挤压了 KV 量化与 speculative decoding 等后续加速技术的空间（§1, §5.1）。
2. **FFN 侧**：过度追求 MoE 稀疏度而不考虑硬件 roofline —— 在今日硬件上跑不出高 MFU，或牺牲模型性能却换不来成本优势（§1, §5.4）。

更关键地，论文首次量化证明：**总参数量与激活参数量都不是 decoding 成本的好指标**（§4.2 Observation 2）。例如 Qwen3-32B 总参与激活均小于 DSv3 与 Step-3，却 decoding 成本最高；而 Qwen3 MoE 235B 总参比 DSv3 少 65%、激活少 40%，在各自最优硬件上 decoding 成本只低 10%（§1）。Step-3 的攻击点是用 **model-system co-design** 把 decoding 成本从两个维度同时压下来：在 38B 激活参数（高于 DSv3 37B、Qwen3 MoE 22B）的前提下，把 8K/32K 上下文 decoding 成本压到 **0.055 / 0.129 USD per 1M tokens**（AFD + H800+H20），相比 DSv3 的 0.068 / 0.211 与 Qwen3 MoE 的 0.062 / 0.193 降低 ~40%，且优势随上下文变长扩大（§4.2 Observation 1）。生产侧实测：Hopper GPU 上 4K 上下文、50ms TPOT SLA、FP8、不开 MTP 时 **4,039 tokens/GPU/s**（peak），比 DSv3 同条件 2,324 TGS 高 74%（§7.3, Table 8），建立新的 LLM decoding Pareto frontier。

## 关键创新点

1. **Multi-Matrix Factorization Attention (MFA) —— 算术强度对齐硬件的 KV/计算双低注意力**（§2, §5.1）。机制：64 个 query head 共享 1 个 K head 与 1 个 V head，head dim 均为 256；query 先从 hidden dim 7168 下投影到低秩 2048，做 normalization，再上投影到 64×256=16384（§2）。这等价于在 QK 电路里做 low-rank matrix factorization（Elhage 2021 的 transformer circuits 框架），既保留高 attention effective rank（**16,384**，与 DSv3 MLA 同，是 Qwen3 MoE GQA 的 8,192 两倍），又把 KV cache 与算术强度同时压低。
   - 效果（§5.1, Tables 2-3, 6）：8K 下 KV 访问 **2.56×10⁸ bytes**，仅比 DSv3 MLA 的 2.88×10⁸ 低 ~10%，但 attention cost 在 H800 上从 DSv3 的 0.054 USD/M 降到 0.048（持平略低），在 H20 上从 0.128 降到 0.040（降 ~69%）；32K 下 Step-3 attention cost 在 H800 上 0.176 vs DSv3 的 0.197、在 H20 上 0.114 vs 0.460（降 ~75%）。**关键不是 KV 体积本身，而是 arithmetic intensity 与硬件 roofline 的匹配**：MFA 的 arithmetic intensity = **128**（8-bit KV），DSv3 MLA = **512**，GQA Qwen3 = **32**；硬件 roofline 分别为 H800 591、H20 74、A800 156、910B 175。MFA 128 介于 A800/910B 之间，与 H20 差距小，因此在廉价硬件上成本低；MLA 512 远超除 H800 外所有硬件 → 在 H20 上成本飙升数倍。
   - 论文还指出（§5.1）：Step-3 的计算是 DSv3 的 **1/4**、KV 访问是 Qwen3 的 **1/3**，同时实现"低算 + 低访"。

2. **Attention-FFN Disaggregation (AFD) —— 注意力与 FFN 物理解耦的 distributed decoding 系统**（§3, §7）。机制：把 Transformer 的 attention 与 FFN 层分别部署到独立的 GPU 集合上，hidden state 通过高速网络在两侧实例间流式传输，形成紧密耦合的多级流水线。设计目标（§3.1）：50ms TPOT（≥20 tokens/s）通过 3-stage pipeline，每级 16.6ms（A/F/communication）；或 4-stage（A→comm→F→comm）每级 12.5ms。对 Step-3（61 层）每层预算 ≈ **272µs**（16.6ms/61，§6）。
   - 效果（§3.2, §7.3）：DSv3 EP 部署需 320 GPU/decoding 实例，Step-3 仅需 **32 GPU（2A2F）**；Step-3 上 AFD 把 attention 与 FFN 各自推到理想 MFU 区，attention 实例基于 vLLM 改造，FFN 实例仅基于轻量 C++ 通信库 + PyTorch 接口（§7.1）。AFD 还允许两侧硬件异构（attention 可换 4×L20 ≈ 1×H800，§6）。

3. **MoE sparsity 与硬件 roofline 的联合设计 —— 反 over-sparsity**（§5.3-5.4）。机制：FFN 的 GEMM 计算访存比 = 2×B（B=batch size）；MoE 把理想 batch 推到 `B_MoE = B_dense / S`（S 为稀疏度）。再叠加 AFD 3-stage pipeline 要求网络传输 `3×H×B_MoE` 在 16.6ms 内完成，推导出"最优 MoE 稀疏度下限"：`S ≥ H×FLOPs×L / (Net×Bandwidth×11.1ms)`（§5.4 公式）。
   - 效果（§5.4 Table 7）：H800 最小 S=**0.058**，H20=0.007，A800=0.031，910B=0.034。Step-3 选 S≈**0.08**（含 shared expert），刚好覆盖 H800 上限；而 DSv3（8/256，S≈0.031）需激活 **14 个 expert**（vs 官方 8）才能在 H800 上跑出高 MFU —— 即 DSv3 在 H800 上"把模型性能留在桌面上"。实测 DeepEP 在 H800 上网络吞吐仅 40 GB/s vs 理论 50 GB/s，进一步把最优 S 推高到 0.073。Llama 4 Maverick / Kimi K2 更稀疏，在 H800 上离高 MFU 区更远。

4. **StepMesh —— AFD 专用 RDMA 通信库（zero-SM、零拷贝、异构加速器）**（§7.2）。机制：(a) 异步 API + 独立收发线程，CPU 端执行 RDMA PostSend/PollCQ（NUMA-aware core binding）以避免与计算抢 SM；(b) 预注册 tensor（unique tensor key），FFN 无需拼接 attention 多实例的张量，直接从 contiguous GPU 内存切片；(c) Rail-Optimized RoCE + Topology-aware 部署（attention/FFN 接同一 ToR 交换机），关拥塞控制、仅用 ToR-NIC PFC 保 lossless，每通信对建 2 个 RDMA QP 分配到两 NIC 端口做流量均衡；(d) 后端抽象 `AFTensorWorker` / `AFTensorServer`，新加速器实现 backend interface 即可接入（为异构硬件铺路）。
   - 效果（§7.2）：满足 AFD 在 272µs 内完成 FP8 token + scale + expert distribution + BF16 activation 跨实例传输的硬要求；NCCL/DeepEP 因额外占 SM 抢算力被排除；open-source：github.com/stepfun-ai/StepMesh。

5. **非旗舰硬件支持 —— AFD × 算术强度匹配打开廉价硬件路径**（§6）。机制：AFD 把 attention/FFN 各自可独立 scale，attention 实例可换更廉价卡（因 Step-3 MFA 是 memory-bandwidth bound，4×L20 ≈ 1×H800，L20 内存带宽 >25% H800）。每层 272µs 预算下，单 L20（864 GB/s）能访问 235 MB，扣除 linear 部分 67 MB 余 168 MB 给 KV cache → 单请求最大上下文 328K，8K 平均上下文时 batch ≤41 仍可满足 SLA；FFN 需 6 个 L20 server（48 卡）承载 ~300 GB FFN 权重。
   - 效果/边界：L4（300 GB/s）连 linear 部分都吃不下 → 不可用，推荐 ≥ L20。

6. **量化与 MTP 在算术强度框架下的统一分析 —— 揭示 MLA 对 MTP/低比特不友好**（§5.2）。机制：低比特存储 + 高比特计算（如 KV 存 4-bit 算 8-bit）等价于把 arithmetic intensity 翻倍；MTP 同样翻倍算术强度（每 KV byte 多算 token）。
   - 效果：(a) DSv3 MLA arithmetic intensity 512 已接近 H800 roofline 591 且远超其他硬件，4-bit KV / MTP 收益微弱；(b) GQA 32 可借此接近或越过 H20 roofline 74，全硬件受益；(c) MFA 128 翻倍到 256 会超过 A800/910B 的 156/175 但仍不远，在 H800 上有较大增益。论文估计 Step-3 开 MTP 在非 H20 硬件上能获 **~50%+ 吞吐提升**（attention 翻倍、FFN 因已高 MFU 不变）。**MTP 的陷阱**：FFN 成本无条件增加（不论预测准确率），在 AFD 下需谨慎决定是否开启。

7. **对 hybrid 线性注意力模型的批判性分析 —— few slow layers ruin the pipeline**（§4.3）。机制：MM M1（70 linear + 10 GQA）、Llama 4 Maverick 类似 hybrid 架构，看似 KV 增长慢，但 (a) 仅那 8-10 层 full attention 的 KV cache 就比 Step-3 全模型还大（不论上下文多长，总访存都更大，Figure 3）；(b) full GQA 层耗时长 → 与 linear 层时间严重不平衡 → 在 AFD distributed pipeline 里产生显著 bubble。
   - 呼吁：full attention 部分要小心设计避免抵消 linear 的收益；应让每层 hybrid 而非少数 slow 层。

## 表格（原文结构化）

### Table 1 — Step-3 模型卡（§2）
| 项 | 值 |
|---|---|
| Transformer 层数 | 61 |
| Hidden Dimension | 7168 |
| Attention Mechanism | MFA |
| Low-rank Query Dimension | 2048 |
| # Query Heads | 64 |
| Head Dimension | 256 |
| # Shared Experts | 1 |
| MoE Layer Configuration | All layers except first 4 and last layer |
| Total Parameters (LLM) | 316 Billion |
| Activated Params per Token | 38 Billion |
| Total Parameters (VLM) | 321 Billion |
注：另有 5B vision encoder，与 decoding 无关未讨论。

### Table 2 — 8K 上下文理论计算与访存（§4.1）
| Model | KV/State Mem Access (bytes) | Attn Compute w/o Linear (FLOPs) | Linear before/after Attn (FLOPs) | FFN Compute (FLOPs) |
|---|---|---|---|---|
| DSv3 | 2.88×10⁸ | 1.47×10¹¹ | 2.28×10¹⁰ | 4.84×10¹⁰ |
| Kimi K2 | 2.88×10⁸ | 7.37×10¹⁰ | 1.23×10¹⁰ | 4.84×10¹⁰ |
| Qwen3 MoE | 7.89×10⁸ | 2.52×10¹⁰ | 1.34×10¹⁰ | 2.84×10¹⁰ |
| Qwen3 32B | 1.07×10⁹ | 1.72×10¹⁰ | 1.21×10¹⁰ | 5.03×10¹⁰ |
| Llama 4 M | 1.01×10⁹ | 8.05×10⁹ | 6.04×10⁹ | 2.42×10¹⁰ |
| MM M1 | 9.23×10⁸ | 3.42×10⁹ | 3.75×10¹⁰ | 5.44×10¹⁰ |
| ERNIE 4.5 | 9.06×10⁸ | 1.45×10¹⁰ | 1.63×10¹⁰ | 7.61×10¹⁰ |
| Pangu Pro | 8.05×10⁸ | 8.05×10⁹ | 6.04×10⁹ | 2.38×10¹⁰ |
| **Step-3** | **2.56×10⁸** | **3.27×10¹⁰** | **2.07×10¹⁰** | **5.33×10¹⁰** |
注：Step-3 KV 最小（≈ DSv3 的 89%、Qwen3 MoE 的 32%）；attention compute 仅为 DSv3 的 1/4 ≈ 22%。

### Table 4 — 加速器规格与定价（§4.2）
| Accelerator | $/card/h (USD) | BF16/FP16 FLOPs | FP8 FLOPs | Mem BW (B/s) | Roofline (compute/BW) |
|---|---|---|---|---|---|
| NVIDIA H800 | 2 | 9.89×10¹⁴ | 1.98×10¹⁵ | 3.35×10¹² | 591 |
| NVIDIA H20 | 0.8 | 1.48×10¹⁴ | 2.96×10¹⁴ | 4.00×10¹² | 74 |
| NVIDIA A800 | 0.75 | 3.12×10¹⁴ | N/A | 2.00×10¹² | 156 |
| Ascend 910B | 0.67* | 2.80×10¹⁴ | N/A | 1.60×10¹² | 175 |
*910B 价格按 FLOPs 从 A800 比例估算，存在多版本（取最弱/最便宜已知版本）。

### Table 6 — 各模型各硬件理论 decoding 成本（USD per 1M tokens）（§4.2）
| Model | Attn 8K H800 | Attn 8K H20 | Attn 8K A800 | Attn 8K 910B | Attn 32K H800 | Attn 32K H20 | Attn 32K A800 | Attn 32K 910B | FFN H800 | FFN H20 |
|---|---|---|---|---|---|---|---|---|---|---|
| DSv3 | 0.054 | 0.128 | 0.114 | 0.113 | 0.197 | 0.460 | 0.409 | 0.407 | 0.014 | 0.036 |
| Kimi K2 | 0.051 | 0.065 | 0.057 | 0.057 | 0.194 | 0.231 | 0.205 | 0.204 | 0.014 | 0.036 |
| Qwen3 MoE | 0.135 | 0.054 | 0.091 | 0.101 | 0.527 | 0.185 | 0.338 | 0.376 | 0.008 | 0.021 |
| Qwen3 32B | 0.181 | 0.069 | 0.120 | 0.133 | 0.716 | 0.248 | 0.455 | 0.508 | 0.014 | 0.038 |
| Llama 4 M | 0.169 | 0.060 | 0.109 | 0.121 | 0.369 | 0.128 | 0.235 | 0.262 | 0.007 | 0.018 |
| MM M1 | 0.164 | 0.079 | 0.121 | 0.132 | 0.330 | 0.135 | 0.226 | 0.249 | 0.015 | 0.041 |
| ERNIE 4.5 | 0.155 | 0.063 | 0.105 | 0.116 | 0.606 | 0.214 | 0.388 | 0.432 | 0.021 | 0.057 |
| Pangu Pro MoE | 0.135 | 0.049 | 0.088 | 0.098 | 0.536 | 0.183 | 0.340 | 0.379 | 0.007 | 0.018 |
| **Step-3** | **0.048** | **0.040** | **0.040** | **0.043** | **0.176** | **0.114** | **0.120** | **0.133** | **0.015** | **0.040** |
注：AFD 取 attention 与 FFN 各自最便宜硬件之和。8K AFD 最优：Step-3 = 0.048+0.040=0.088? 论文正文（§4.2 Observation 1）给的是 Step-3 8K=0.055, DSv3=0.068, Qwen3 MoE=0.062; 32K Step-3=0.129, DSv3=0.211, Qwen3=0.193（含单位换算与 AFD 跨硬件组合后取最优，参见 Figure 2）。

### Table 7 — 各硬件最小 MoE 稀疏度（H=7168, L=61, §5.4）
| Accelerator | H800 | H20 | A800 | 910B |
|---|---|---|---|---|
| Minimum S | 0.058 | 0.007 | 0.031 | 0.034 |
注：H800/H20 用 400Gbps×8 NIC；A800/910B 用 200Gbps×8。DeepEP 实测吞吐 40 vs 50 GB/s → H800 实际最优 S 升到 0.073。Step-3 选 S≈0.08；DSv3 需 14 activated experts（vs 官方 8）才能在 H800 上高 MFU。

### Table 8 — 端到端 decoding 性能对比（§7.3, 50ms TPOT/20 tok·s SLA）
| Model | Avg Ctx | # Hopper GPUs | Peak TGS |
|---|---|---|---|
| DSv3-blog | 4989 | 144 | 1850 |
| DSv3-profile | 4096 | 128 | 2324 |
| Step-3 (BF16 attention) | 4096 | 40 (3A2F) | 3321 |
| **Step-3 (FP8 attention)** | **4096** | **32 (2A2F)** | **4039** |
| Step-3 (FP8 attention) | 8192 | 48 (4A2F) | 2643 |
注：FP8 attention 比 BF16 attention 高 ~18%；4K 用 2A2F，batch 总 6144 分 3 micro-batch × 2048 填 3-stage pipeline；上下文翻倍只需等比扩 attention 实例（"4A2F"→8K, "16A2F"→32K 约 898 TGS）。

### Table 9 — 单 attention 层延迟消融（µs, batch 256, 4 GPUs）（§7.3）
| Ctx | Attention | H800 | H20 | A800 |
|---|---|---|---|---|
| 8K | MFA-Step3 | 281 | 438 | 531 |
| 8K | MLA-DSv3 | 372 | 1252 | - |
| 8K | GQA-Qwen3 | 382 | 812 | 791 |
| 32K | MFA-Step3 | 791 | 1452 | 1484 |
| 32K | MLA-DSv3 | 1125 | 4817 | - |
| 32K | GQA-Qwen3 | 1391 | 3042 | 3010 |
注：MFA 全平台最低；H20 与长上下文下 gap 拉大；FlashMLA 无 SM80 实现 → A800 缺。

### 算术强度与硬件 roofline 对比（§5.1）
| Attention | Arithmetic Intensity (8-bit KV) | Attention Effective Rank |
|---|---|---|
| MLA (DSv3) | 512 | 16,384 |
| GQA (Qwen3 MoE) | 32 | 8,192 |
| **MFA (Step-3)** | **128** | **16,384** |
| H800 roofline | 591 | — |
| H20 roofline | 74 | — |
| A800 roofline | 156 | — |
| 910B roofline | 175 | — |

## 与同类对比

- **vs DeepSeek-V3 (MLA + EP-only, §3.2, §4.2, §7.3)**：DSv3 是最直接的对照。MLA 的 arithmetic intensity 512 远超 H800 外所有硬件 → 在 H20 上 attention cost 暴涨到 0.128（8K）/0.460（32K），是 Step-3 的 3.2×/4.0×；而 Step-3 MFA 的 128 跨硬件几乎持平（H800 0.048 / H20 0.040 / A800 0.040 / 910B 0.043）。EP-only 部署需 320 GPU/实例，AFD 仅需 32 GPU；DSv3 的 8/256 MoE 稀疏度 S≈0.031 低于 H800 最优 0.058，需 14 个激活 expert 才能高 MFU —— "把模型性能留在桌面上"。Step-3 同等规模下 4,039 vs 2,324 TGS（+74%）。但论文承认 Step-3 的优势在"DSv3 最有利的场景"（H800 + 4K 上下文 + EP）下测得，更长上下文与更廉价硬件优势会扩大（§7.3）。
- **vs Qwen3 MoE (GQA, §4.2)**：GQA arithmetic intensity 32 极低、KV 体积大（8K 7.89×10⁸ bytes，是 Step-3 的 3.1×），只在 H20（roofline 74，差距小）上便宜，其他硬件贵；Qwen3 MoE 总参少 65%、激活少 40% 却只比 DSv3 便宜 10%。
- **vs Kimi K2 (§5.4)**：继承 DSv3 over-sparsity（Workaround 1：large EP），但移除 routing 限制（Workaround 2）→ 网络瓶颈比 DSv3 更严重。
- **vs Llama 4 Maverick (hybrid linear, §4.3)**：hybrid 但 full GQA 层的 KV 总量已超 Step-3 全模型，且层间时间不平衡 → 在 AFD pipeline 中产生 bubble。
- **vs MiniMax M1 (hybrid linear, §4.3)**：70 linear + 10 GQA，KV 增长慢但 full attention 部分仍超 Step-3 总访存；FP32 lightning attention state 进一步放大成本。
- **vs Pangu Pro MoE (§4.3, Figure 4)**：号称 910B 优化但 decoding 成本在 910B 上反而高于 Step-3（8K 0.098 vs 0.043, 32K 0.379 vs 0.133），尽管激活参数仅 16.5B（Step-3 38B 不到一半）；但训练成本（基于 FLOPs 估算 100% MFU）比 Step-3 便宜 50%+。说明"训练 optimized ≠ decoding optimized"。
- **vs Megascale-Infer (§3.2)**：首个 AFD 思路的 serving 系统，但只追求吞吐未达低延迟（reported 150ms TPOT vs Step-3 50ms），且只做系统级优化未做 model-system co-design。
- **vs DeepEP (§3.2, §5.4, §7.2)**：DeepEP 是 EP 部署的通信库，需大规模 EP（10+ server）才缓解 over-sparsity，且占 SM 抢算力；StepMesh 走 AFD 路线，零 SM 占用，规模更小（32 GPU vs 320 GPU）。
- **vs MTP-based speculative decoding**（[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]、[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]）：Step-3 论文未实现 MTP，但 §5.2 给出"算术强度翻倍"框架下的分析 —— MFA 因 arithmetic intensity 128 适中可大幅受益于 MTP（估 +50%），而 MLA 512 已近 H800 roofline 收益微弱。这把"MTP 是否值得开"的决策与 attention 算术强度关联起来，是跨方法的统一视角。

## 跨论文关系（→ MOC 谱系）

- 继承 [[deepseek-v3-technical-report]] 的 DeepSeekMoE shared-expert 设计与 MTP 架构；H=7168、L=61 与 DSv3 完全一致，便于复用部署栈。但 Step-3 用 MFA 替换 MLA、用 AFD 替换 EP-only 部署，是对 DSv3 decoding 路线的直接改造（DSv3 EP+redundant experts 需 320 GPU，Step-3 AFD 仅需 32 GPU，§3.2）。Step-3 引用 DSv3 profiling 数据 2,324 TGS 作为对照基线（§7.3）。
- 与 [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] 同属 KV 架构压缩家族：GQA（Qwen3）/ MLA（DSv3）/ MFA（Step-3）三选一。MFA 在 arithmetic intensity 谱上严格位于 GQA（32）与 MLA（512）之间（128），首次量化证明"KV 体积不是唯一指标，算术强度对硬件的匹配才是"。
- 与 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] 对照：DeepSeek 系继续走 MLA 演化（CSA/HCA 双重压缩+稀疏）推到 1M token；Step-3 走 MFA+AFD 路线压 decoding 成本但未追求超长上下文（4K-32K 为主）。两条都是"低成本 decoding"的差异化路径。
- 与 [[kimi-k2-open-agentic-intelligence]] / [[kimi-k3-open-frontier-intelligence]] 对照：Kimi 系走 hybrid 线性注意力（KDA:MLA=3:1）+ MuonClip 训练稳化；Step-3 论文明确批评 hybrid linear（如 MM M1、Llama 4 M）的 full attention 部分仍拖累整体成本（§4.3）。Kimi K2 还沿 DSv3 over-sparsity 路线（移除 routing 限制，瓶颈更糟，§5.4）。
- 与 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] 互为镜像：CloudMatrix 把 attention/MoE disagg 推到 NPU 全局共享内存语义（UB Memory + AIV persistent kernel + A2E/E2A trampoline）；Step-3 AFD 走 GPU 路线（StepMesh + RDMA + RoCE + PFC）。两者都把 attention 与 FFN 解耦成独立子系统并设计专用通信原语（XCCL vs StepMesh），但 CloudMatrix 是 SuperPod 级全局内存语义，StepMesh 是 Rail-Optimized RoCE + NUMA-aware CPU 线程。两者也都讨论 MTP（CloudMatrix 实测 acceptance 70-90%、降延迟 ≤40%；Step-3 给算术强度框架预测但未实现）。
- 与 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] 互补：Step-3 的算术强度分析（§5.2）把 MTP/speculative decoding 视为"翻倍 arithmetic intensity"的操作，从而解释为何 MLA-friendly 的 DSv3 难以从 MTP 受益、MFA/GQA-friendly 的模型受益 —— 这给 EAGLE-3 类训练-time test drafting 提供了"目标模型 attention 设计是否兼容"的判据。
- 与 [[muon-is-scalable-for-llm-training]] / [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] 对照：Step-3 论文明确区分"训练成本 vs decoding 成本"（§4.3 Pangu Pro MoE 案例），强调训练成本主要绑激活参数、decoding 成本需额外 co-design —— 与 Muon/Megatron-Core 这类训练侧优化正交，未来工作方向是"novel high bandwidth domain designs [19]"以允许更稀疏 MoE，呼应硬件-算法协同设计方法论。
- 与 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] (vLLM) 互补：Step-3 的 attention 实例基于 vLLM 改造（§7.1），AFD 在 PagedAttention 之上叠加 attention/FFN 解耦。
- 与 [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] 主题相邻（硬件拓扑对模型成本的影响），但 Step-3 关注推理 decoding 拓扑（Rail-Optimized RoCE + ToR 同交换机）。
- 与 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] / [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] 同属 disagg 谱系：Step-3 AFD 是 PD-disagg 之后的"attention-FFN disagg"，是 disagg 维度从时间（prefill/decode）向空间（attention/FFN）的延伸。

## 局限与边界

- **vision encoder 不讨论**：5B vision encoder 与 decoding 无关被略过（§2），VLM 侧未给评估，仅作为参数总数加成（321B VLM vs 316B LLM）。后续会"release more details on the model side"（§2）。
- **理论成本分析基于 AFD 理想化假设**：(a) 假设 attention/FFN 各自都能跑到硬件峰值 FLOPs/BW 与高 MFU（§4.1）；(b) 假设所有网络通信可被计算完全 overlap，通信成本被忽略（§5.4）；(c) MLA/MFA 的 q/k/v_proj 因 TP-unfriendly 在 H800 上可能未到 compute-bound 区，论文承认"slightly underestimate MLA and MFA costs on H800"（§4.1）；(d) embedding 与 output linear 因 <5% 被忽略（§4.1）。
- **对 over-sparse 模型（DSv3/Kimi K2/Llama 4 M）"给面子"**：§4.1 明确指出"for simplicity, we omit it and give them a favor" —— 即假设它们 FFN 也能跑高 MFU；实际 DSv3 在 H800 上可能 FFN 成本翻倍甚至三倍（worst case）。这意味着 Figure 1 / Table 6 高估了 over-sparse 模型的竞争力，Step-3 的实际优势更大。
- **MTP 未实现**：§5.2 的 +50% 提升仅是估计，§8 列为"immediate next step"。MTP 的 FFN 成本无条件增加陷阱（§5.2）也未实测验证。
- **Pangu Pro MoE 的训练成本估算粗糙**：§4.3 假设 100% MFU（即便用 40% 也只趋势不变），未考虑实际训练系统开销。
- **910B 定价不公开**：Table 4 标注 910B 价格按 FLOPs 从 A800 比例估算，且存在多版本取最弱/最便宜已知版本，存在不确定性。
- **L4 不可用、L20 是下限**：§6 明确 weaker hardware 必须满足 272µs/层 预算，L4（300 GB/s）连 linear 部分 67 MB 都吃不下；推荐 ≥ L20。
- **AFD 是 PD-disagg 的下游假设**：§1/§3 明确"based on the assumption of deploying prior work of Prefill-Decoding disaggregation"，prefill 侧未优化；AFD 自身不解决 prefill。
- **AFD 不是 EP 替代而是互补**：§3.2 明确"AFD is not a replacement for EP, but rather a complementary approach"，Step-3 实际可用 TP-EP 混合。
- **hybrid 线性注意力批判未给出 Step-3 的对照实验**：§4.3 批评 MM M1/Llama 4 M 的 full attention 部分拖累，但未在 Step-3 上做 hybrid 变体对照。
- **非旗舰硬件分析基于理论**：§6 的 L20 部署是理论推导（基于内存带宽与 272µs 预算），未给端到端实测。
- **网络拥塞控制策略激进**：§7.2 关闭拥塞控制仅用 PFC，依赖 ToR-NIC 同交换机拓扑；跨 ToR 或更复杂拓扑下行为未验证。
- **Ablation 600B upcycle 的局限**：§7.3 把 Step-3 FFN upcycle 到 600B（DSv3 规模）后 TGS 降到 3,291，论证 over-sparsity 的影响，但仍未完全对齐 DSv3 的 BF16 attention 配置（profiling 估算 ~2,880 TGS）。
- **成本对比未含精度/质量维度**：Figure 1 Pareto frontier 仅含"激活参数 × decoding 成本"，未含模型质量（benchmark）轴；Step-3 是否在 quality/成本上同样 Pareto 优势需另文验证。
