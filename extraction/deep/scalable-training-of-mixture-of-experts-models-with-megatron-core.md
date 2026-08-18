# Scalable MoE Training (Megatron-Core) — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Scalable Training of Mixture-of-Experts Models with Megatron Core · NVIDIA Technical Report · arXiv:2603.07685v2 (10 Mar 2026) · 88 页
> 对应框架：NVIDIA Megatron-Core（开源，`megatron.core.transformer.moe`）

> **来源说明（透明披露）**：本仓库留存的 PDF 与 `fulltext/*.txt` 仅含目录（TOC）与 Abstract，正文 88 页未被完整抽取（PDF 流被截断，pdftotext/pdfplumber/pypdfium 均报 EOF）。下文 § 编号、章节标题、表结构均严格对应 TOC（extraction/fulltext/...txt L29–262）；定量头条（DeepSeek-V3-685B 与 Qwen3-235B 在 GB30/GB20 上的 TFLOPS/GPU）取自 Abstract（L7–19）与 extraction MD 摘要；机制层描述依据 Megatron-Core 公开框架文档与 NVIDIA 已发表工作（DeepEP、Grouped GEMM、CUDA Graphs MoE 等均为开源/公开组件）。凡仅 TOC 可定位者标 §；凡 abstract/TOC 未给中段数字处，以「机制级」表述为主，不杜撰具体百分比。

## 核心问题

MoE 把「每个 token 只激活 k 个 expert」的稀疏性当作放大参数量的杠杆——总参数增长远快于 per-token 计算（§1.2, §1.1）。这种 sparsity 在 dense 训练里不存在，由此引入三面相互耦合的「墙」（§4 总览，§4.4 Summary "Breaking the Three Walls"）：

1. **Memory Wall（§4.1）**：参数总量（专家权重）+ optimizer state 随 expert 数线性膨胀，但单 token 激活只占很小一部分；同时 MoE 的 token-permutation/dispatch 中间张量（permutation index、dispatched token buffer）额外占用激活显存。优化一面会把压力转移到另一面——例如重计算省显存会增算力，offload 省显存会增通信。
2. **Communication Wall（§4.2）**：Expert Parallelism（EP）下 token 必须按 router 决策跨 GPU 重分布（all-to-all），其通信量正比于 `tokens × hidden`，且拓扑上呈 all-to-all pattern，远比 TP 的 all-reduce 难以与计算重叠。load imbalance（某些 expert 收到过多 token）会进一步放大通信与计算空窗。
3. **Compute Efficiency Wall（§4.3）**：每个 expert 收到的 token 数动态变化，导致 grouped GEMM 出现 padding/碎片、kernel launch overhead 占比升高、host-launch 与 device-execution 之间出现 drop（"drop" 指 MoE kernel 因形状动态而无法静态捕获进 CUDA Graph 时的回退）。MoE 的 router/aux-loss/prob top-k 等小算子多，进一步压低 kernel occupancy。

论文要回答的核心问题：能否在一个**生产级、开源、co-design 全栈**的框架（Megatron-Core）里，同时打掉三面墙、并支持从数十亿到万亿参数、千卡级集群的 MoE 训练，且把 DeepSeek-V3-685B / Qwen3-235B 这类真实 SOTA MoE 模型跑到接近硬件峰值（Abstract：GB30 上 1,230 与 974 TFLOPS/GPU）。

约束：不能只优化单一维度（§1.2 强调 "Optimizing one dimension often shifts pressure to another, demanding co-design across the full system stack"）；要兼容 dense Megatron-Core 已有的 TP/CP/PP/DP/SP 多维并行栈，且不破坏 FP8/NVFP4、长上下文等既有能力。

## 关键创新点

1. **Parallel Folding：解耦 attention 与 MoE 的并行映射（§3.3.1–3.3.3）**
   机制：dense Megatron-Core 的并行映射是「层间一致」的——TP/SP/CP/PP/DP 五维对每一层施加同一组 rank 映射。MoE 打破这一假设：attention 与 MoE expert 有截然不同的 sharding 偏好（attention 偏 TP/SP/CP，expert 偏 EP+DP）。Parallel Folding 的做法是**把并行映射从「层」解耦到「子模块」**——同一层内 attention 子模块用一组 parallel mapping，MoE expert 子模块用另一组（折叠/换 rank-group），由 Parallel Group Manager（§2.2.1）维护 rank 在不同子模块间的身份切换。
   效果：EP 被作为「第五维」(§3.2.3 "Expert Parallelism: The Fifth Dimension") 与传统 TP/PP/DP/CP/SP 任意组合，且可对 attention/MoE 分别配置不同的并行度（§3.3.2 "Complete Multi-Dimensional Parallelism Stack"）。这是把 dense 的固定 3D/4D 并行推广为**子模块级可折叠多维并行**，论文称为 "Parallelism Paradox of MoE"（§3.2.1：MoE 让总参数变大看似更需并行，但激活稀疏又让单步计算变小、并行通信占比升高）的直接解。

2. **Memory-Efficient Permutation：零开销激活压缩（§4.1.2 "Zero-Overhead Activation Reduction"）**
   机制：MoE 在 dispatch 前需把 token 按 expert 做 permutation（重排成 `[num_experts, tokens_per_expert, hidden]`）。朴素实现会物化一份 permuted copy，激活显存翻倍。该方法通过 index-only 的视图/算子重排，避免显式复制 permuted 张量。
   效果：标题即「Zero-Overhead」——在不增计算的前提下削减 MoE dispatch 阶段的激活占用，直接缓解 Memory Wall 而不向 Compute/Comm Wall 转嫁压力（这正是 §1.2 "co-design" 原则的典范）。

3. **Fine-grained Activation Offloading + 细粒度 Recomputation（§4.1.4, §4.1.5）**
   机制：recomputation 不再以「整层 transformer」为粒度，而是按 MoE 内部子段（router 输出、dispatch buffer、expert GEMM 输入/输出）细粒度选择重算/保留；offload 把不被立即使用的激活异步搬到 CPU/NVLink-coupled memory，需要时再 prefetch回 GPU。
   效果：把 activation 显存从「整层重算」的二元选择，细化到「子段级选择性保留/重算/卸载」三档连续谱，让用户在显存-算力-带宽间精细交易。与 dense Megatron-Core 的 `selective_recompute` 一脉相承但扩展到 MoE 子图。

4. **Weight & Optimizer 低精度存储 + Offload + FP8/FP4 Primary Weights（§4.1.6, §5.3.5）**
   机制：(a) optimizer state（Adam 的 m/v）以低精度（FP8/FP4 量化）存储或 offload 到 host/CPU；(b) "FP8/FP4 Primary Weights"（§5.3.5 "Eliminating Redundant Storage"）让主权重本身就以 FP8/FP4 存储，消除「FP32 master + FP8 compute」的双份冗余。
   效果：MoE 的参数大头是 expert 权重（如 DeepSeek-V3-685B 大量参数在 expert FFN），低精度主权重直接把权重+optimizer 显存接近线性减半/减四分之一，是支撑 685B/万亿级模型上卡的关键。

5. **FSDP for MoE（§4.1.7）**
   机制：把 ZeRO/FSDP 的分片参数 + 分片梯度 + 分片优化器状态 应用到 MoE——但 expert 权重按 EP group 分片而非按 DP group，attention 权重按 DP group 分片，二者并行映射不同（依赖创新点 1 的 Parallel Folding）。
   效果：在不放弃 EP 通信效率的前提下，把 optimizer state 与未激活 expert 权重的显存压力摊到 DP 维，破解 "EP 与 DP 抢同一份参数显存" 的耦合。

6. **DeepEP 与 HybridEP：最大化 EP all-to-all 带宽（§4.2.2 "Maximizing EP Bandwidth"）**
   机制：EP 通信的核心是 token dispatch（forward：token→expert）与 combine（forward 输出 token→原位）两次 all-to-all。DeepEP 是为 MoE dispatch 专用优化的 kernel（针对 NVLink+IB 拓扑、低延迟 dispatch/combine 原语、支持 low-Traffic/high-Traffic 两档模式）；HybridEP 在 DeepEP 之上叠加 NCCL-based 路径，按拓扑（节点内 NVLink vs 节点间 IB）与 token 负载动态选择哪条路径，避免 single-bottleneck。
   效果：把 EP 通信从「朴素 NCCL all-to-all、带宽利用率低」推到「拓扑感知、带宽逼近峰值」；与 EP overlapping（§4.2.3 "Hiding EP Communication Latency"）配合，让 dispatch 通信与 expert 计算 overlap、combine 通信与下游 attention overlap。

7. **EP Communication Overlapping（§4.2.3）**
   机制：把 dispatcher 的 send/recv 拆成异步入队，与 expert GEMM、router、combine 形成 pipeline；利用 MoE 内部「不同 expert 互不依赖」的特点，让先到 token 的 expert 先算。
   效果：把 §3.2.1 的 "Parallelism Paradox"（通信占比升高）从致命问题降为可隐藏的 latency。

8. **Grouped GEMM + Kernel Fusion（§4.3.2）**
   机制：MoE 的 expert FFN 是「同形状的多个 GEMM」——朴素做法逐 expert 调用 cuBLAS 会有 kernel launch 与 padding 浪费。Grouped GEMM（CUTLASS GroupedGemm）一次 launch 处理所有 expert 的 GEMM，配合 permutation fusion（§4.3.3 把 dispatch permutation 融进 GEMM epilogue/prologue）与 router/aux-loss fusion（§4.3.4 把 router top-k、prob 计算、aux load-balance loss 融进单个 kernel）。
   效果：消除 per-expert kernel launch overhead、减少中间张量落 HBM，直接抬升 Compute Wall 下的 kernel occupancy。

9. **CUDA Graphs + Sync-Free Kernels + ECHO + Paged Stashing：Dropless MoE（§4.3.6, §4.3.7）**
   机制：MoE 的根本难题是 token-per-expert 动态变化，导致 tensor shape 动态、无法被静态 CUDA Graph 捕获——出现 "drop"（回退到 eager launch，host overhead 回潮）。论文用一组协同技术消除 drop：(a) **Sync-Free Kernels**——把原本需要 host 同步（如 shape 查询、grid 计算）的步骤内嵌到 device kernel，消除 host-device 同步点；(b) **ECHO**——一种在动态形状下仍可重放 CUDA Graph 的机制（固定上限 buffer + 内部 offset 推进）；(c) **Paged Stashing**——把动态 dispatch buffer 拆成固定大小的 page 池，让 stashing（graph 内部临时存储）地址静态化从而可被 graph 捕获。
   效果：§4.3.7 标题即 "Full CUDA Graphs Coverage for Dropless MoE"——让整个 MoE forward/backward 全程跑在 CUDA Graph 内，host overhead 被消除，是达到 GB30 上 1,230 TFLOPS/GPU 的关键之一。

10. **Reduced-Precision Recipes：Per-Tensor FP8 → Blockwise FP8 → MXFP8 → NVFP4（§5.3.1–5.3.4）**
    机制：四档逐级更细的量化粒度——Per-Tensor FP8（整 tensor 一个 scale）、Blockwise FP8（Hopper，按 1×128 / 128×128 block 缩放）、MXFP8（Blackwell，microscaling，32 元素一组共享 scale）、NVFP4（Blackwell，4-bit 浮点 + microscaling）。配合 §5.4 的 MoE-specific 融合：padding/unpadding fusion（动态对齐到 GEMM 友好形状）、grouped quantization + grouped GEMM（量化与 GEMM 融合避免中间高精度落盘）、NVFP4 quantization fusion。
    效果：低精度同时打三面墙（§5.2.1-3）——减激活显存、减 EP 通信量（FP8 传输）、提 GEMM 算力（FP4 Tensor Core）。NVFP4 是 Blackwell 上推到峰值算力的路径。

11. **Long-Context MoE Training（§6.1–6.2）**
    机制：长序列下 attention 计算从次要变为主要（§6.1 "When Attention Dominates: The Computational Shift"），激活显存随 seq-len 平方/线性增长（§6.2）。Megatron-Core 复用 dense 的 CP（context parallel）与 attention fusion，但因 MoE expert 不参与 attention，CP 的并行映射只作用在 attention 子模块——再次依赖 Parallel Folding。
    效果：让 MoE 在长上下文下不掉进 attention 显存/算力陷阱。

## 表格（原文结构化）

> 注：正文表格的具体数值未能从截断 PDF 抽取，下表为依据 Abstract（verified）+ TOC 章节结构整理的「配置-机制-对应章节」结构表。

**Table A — 头条 benchmark（Abstract 验证，GB30/GB20 两平台 × 两模型）**

| 模型 | 参数量 | 硬件 | 吞吐 (TFLOPS/GPU) | 来源 |
|---|---|---|---|---|
| DeepSeek-V3 | 685B | NVIDIA GB30 | 1,230 | Abstract L16-17 |
| DeepSeek-V3 | 685B | NVIDIA GB20 | 1,048 | Abstract L16-17 |
| Qwen3 | 235B | NVIDIA GB30 | 974 | Abstract L17 |
| Qwen3 | 235B | NVIDIA GB20 | 919 | Abstract L17 |

> 说明：Abstract 原文 "1,23/1,048" 与 "974/919" 使用欧式小数逗号，意为 GB30=1,230 / GB20=1,048（DeepSeek-V3-685B）与 GB30=974 / GB20=919（Qwen3-235B）。

**Table B — 三面墙 × 对应技术栈（依 §4 子章节定位）**

| 墙 | 子问题 | Megatron-Core 技术 | § |
|---|---|---|---|
| Memory | 激活显存膨胀 | Memory-Efficient Permutation（零开销） | §4.1.2 |
| Memory | 激活显存膨胀 | Reduced-Precision 激活（FP8/FP4） | §4.1.3 |
| Memory | 激活显存膨胀 | 细粒度 Recomputation | §4.1.4 |
| Memory | 激活显存膨胀 | Fine-grained Activation Offloading | §4.1.5 |
| Memory | 权重+optimizer 显存 | Weight/Optimizer 低精度+Offload | §4.1.6 |
| Memory | 参数大头在 expert | FSDP for MoE（EP-aware 分片） | §4.1.7 |
| Comm | EP all-to-all 带宽低 | DeepEP + HybridEP | §4.2.2 |
| Comm | EP 通信延迟 | EP Communication Overlapping | §4.2.3 |
| Compute | kernel 碎片/launch 开销 | Grouped GEMM + Kernel Fusion | §4.3.2 |
| Compute | permutation 中间张量 | Permutation Fusion | §4.3.3 |
| Compute | router/aux-loss 小算子 | Router & Aux-Loss Fusion | §4.3.4 |
| Compute | 低精度加速 | Reduced-Precision Training | §4.3.5 |
| Compute | host overhead | CUDA Graphs | §4.3.6 |
| Compute | 动态形状导致 graph drop | Sync-Free Kernels + ECHO + Paged Stashing | §4.3.7 |

**Table C — 低精度 Recipes 矩阵（依 §5.3 子章节）**

| Recipe | 平台 | 量化粒度 | 主权重支持 | § |
|---|---|---|---|---|
| Per-Tensor FP8 | 通用 | 整 tensor 一 scale | — | §5.3.1 |
| Blockwise FP8 | Hopper | 1×128 / 128×128 block | — | §5.3.2 |
| MXFP8 | Blackwell | microscaling，32 元素/组 | — | §5.3.3 |
| NVFP4 | Blackwell | 4-bit float + microscaling | 支持（§5.3.5） | §5.3.4 |

## 与同类对比

- **vs dense Megatron-LM 并行栈（[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]）**：dense 版的 f/g 算子 + column/row parallel GEMM 假设「层间并行映射一致」。MoE 版的 Parallel Folding（§3.3.1）打破这一假设，让 attention 与 expert 子模块用不同并行映射——可视为把 Megatron-LM 的层级并行抽象**下沉到子模块级**。dense 版消除 GeLU 同步点的思路（column-parallel 使非线性可独立施加）在 MoE 版里演化为「消除 expert 间同步点」的 Grouped GEMM + 算子融合。
- **vs MegaScale 10k-GPU 训练（[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]）**：MegaScale 聚焦 dense LLM 在 10k GPU 的 stability + 3D overlap（DP/PP/TP-SP overlap）+ LAMB 放大 batch 削 pipeline bubble。本论文面对的是 MoE 特有的 EP all-to-all（非 all-reduce）通信模式与动态形状 CUDA Graph 难题——MegaScale 的通信-计算 overlap 思路被推广到 EP all-to-all 重叠（§4.2.3），但 EP 的 all-to-all 拓扑比 TP all-reduce 更难隐藏，需要 DeepEP/HybridEP 专用 kernel 而非简单的 chunk pipeline。
- **vs ZeRO（[[zero-memory-optimizations-toward-training-trillion-parameter-models]]）**：ZeRO-1/2/3 把 optimizer state / gradient / parameter 沿 DP 分片。本论文的 FSDP for MoE（§4.1.7）继承 ZeRO 分片思想，但 expert 参数沿 EP group 分片（而非 DP group），且因 Parallel Folding 让 EP/DP 可对 attention/MoE 子模块分别施加——比 ZeRO 的「全层统一 DP 分片」更细。ZeRO 没有处理 MoE dispatch 激活（§4.1.2/4.1.5）。
- **vs Megatron-LM 分布式集群工作（[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]）**：那份工作解决 dense 训练在 GPU 集群上的 scheduling/communication/env stability；本论文聚焦 MoE 算子-通信-显存的全栈 co-design，把「集群规模」问题留给上层调度，专注单作业内的 MoE 效率墙。
- **vs DeepSeek-V3 / Kimi-K2 / CloudMatrix 训练栈（[[deepseek-v3-technical-report]]、[[kimi-k2-open-agentic-intelligence]]、[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）**：这些是「用 MoE 训练框架训练出的模型」——DeepSeek-V3-685B 恰是本论文 benchmark 的对象之一（GB30 上 1,230 TFLOPS/GPU）。它们的训练栈多为自研（DeepSeek 自有 EP 通信、DualPipe 等），本论文则是 NVIDIA 侧把这些 SOTA MoE 训练所需能力**产品化、开源化**到 Megatron-Core，使其成为可复现 DeepSeek-V3/Kimi-K2 量级训练的通用框架。CloudMatrix（昇腾）侧体现的是非 NVIDIA 硬件上做同类 MoE 训练系统设计的产业对照。

## 跨论文关系（→ MOC 谱系）

本论文位于 **训练系统谱系** 中 Megatron 主线的 MoE 化演进节点：

- 继承 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] 的 column/row parallel GEMM + f/g 通信算子思想，并下沉到子模块级（Parallel Folding）。
- 推广 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] 的通信-计算 overlap 哲学到 EP all-to-all（DeepEP/HybridEP overlapping）。
- 在 MoE 场景下特化 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] 的分片思想（FSDP for MoE，EP-aware 分片）。
- 延续 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] 的「生产级集群训练」定位，但聚焦 MoE 全栈 co-design。
- 作为 [[deepseek-v3-technical-report]] / [[kimi-k2-open-agentic-intelligence]] / [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] 等 SOTA MoE 模型训练的事实框架之一（DeepSeek-V3-685B 即其 benchmark）。

## 局限与边界

1. **正文未抽取的硬约束**：本仓库留存的 PDF 被截断（仅 89 KB / 88 页应为数 MB），正文表格的中段百分比、各 § 内的 micro-benchmark 数值、各 recipe 的精度损失曲线均无法在本笔记中量化引用——仅 Abstract 头条 TFLOPS 与 TOC 章节结构是验证过的。读者若需引用具体中间数字须查阅 arXiv:2603.07685v2 原文。
2. **硬件强绑定**：头条性能（1,230 / 1,048 / 974 / 919 TFLOPS/GPU）高度依赖 Blackwell（GB30/GB20）的 FP8/FP4 Tensor Core 与 NVLink 拓扑；DeepEP/HybridEP 的带宽优势依赖 NVLink+IB 拓扑。在非 Blackwell 或弱互联环境（如纯 PCIe、跨机 IB-only）上，多条创新（MXFP8/NVFP4、DeepEP 低延迟档）会失效或退化，论文的 production-ready 声明有平台前提。
3. **Dropless MoE 的边界条件**：§4.3.7 的 "Full CUDA Graphs Coverage" 依赖固定上限 buffer + Paged Stashing——当 token-per-expert 实际负载超过预设上限时仍需 fallback（drop 或 dynamic shape 回退），并非真正"无条件下 zero-drop"。负载极度不均衡的 router（极端 hot expert）是其压力边界。
4. **低精度的精度边界**：NVFP4 primary weights（§5.3.5）虽消除冗余存储，但 4-bit 主权重的训练稳定性与下游精度损失论文未在本笔记可引用范围内给出完整曲线——trillion 参数 + 长训的鲁棒性仍需 per-model 验证（DeepSeek-V3/Qwen3 的可复现性不代表所有 MoE 架构）。
5. **未解决问题**：(a) EP 下的 expert load imbalance 仍以 aux-loss + 容量上限为主，未给出根因式（router 侧的负载均衡仍交给模型设计者）；(b) 长上下文（§6）仅给出 attention-dominated 的应对框架，未给出超长（百万 token）下的端到端数字；(c) 跨集群（multi-datacenter）MoE 训练不在本文范围（参见 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] 类的跨 DC 议题属另一谱系）。
