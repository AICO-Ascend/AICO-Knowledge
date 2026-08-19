# Scalable MoE Training (Megatron-Core) — 技术点深读（DEEP 2026-08-20 回填）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Scalable Training of Mixture-of-Experts Models with Megatron Core · NVIDIA Technical Report · arXiv:2603.07685v2 (10 Mar 2026) · 88 页
> 对应框架：NVIDIA Megatron-Core（开源，`megatron.core.transformer.moe`），benchmark 基于 Megatron-Core v0.16 + TransformerEngine dev 分支
> 全文 266 KB 完整抽取（88 页，EOF 完整）。本回填版所有数字均取自正文 Table 3/5/7/8/9/11/17/18 与各 § 正文，标注 §号 / Figure N / Table N 出处。formulas.json 为空（无 e-print 公式），故公式一律散文引用，不写 `$`/`$$`。

## 核心问题

MoE 把「每个 token 只激活 k 个 expert」的稀疏性当作放大参数量的杠杆——总参数增长远快于 per-token 计算（§1.1, §1.2）。这种 sparsity 在 dense 训练里不存在：dense 模型每 token 约 6N_total FLOPs（前向+反向），参数与 per-token 计算同步增长；MoE 则打破了这一锁步关系。**DeepSeek-V3 是论文反复使用的标尺**：685B 总参数（671B Main Model + 14B MTP Module）但仅 37B per-token 激活，18× 的参数-计算错配（§1.2, §3.2.1）；**Kimi-K2 更极端**：1T 总参数 / 32B 激活 = 31× 错配（§4.1.5）。论文用 **Figure 3** 的 log-log 散点图把「Parallelism Paradox of MoE」可视化：dense 模型沿 2N 参考线分布（参数与计算同步），MoE 模型显著落在 2N 线下方——DeepSeek-V3 在图上呈现的 gap 正是这三面墙的几何起源（M3 caption p13）。

由此引入三面相互耦合的「墙」（§4 总览，§4.4 Summary "Breaking the Three Walls"）：

1. **Memory Wall（§4.1）**：参数+optimizer state 随 expert 数线性膨胀，但单 token 激活只占一小部分。论文给出**DeepSeek-V3 BF16、PP4×VPP4×EP64、256 GPU**的 per-GPU 显存解剖（Table 3）：Weights & Gradients 36.4 GB + Main Weights & Optimizer States 32.1 GB + Activations **131.0 GB = 总 199.5 GB**，远超 H100 的 80 GB（§4.1.1）。激活是最大头，超过权重与 optimizer 之和——这是把激活优化列为最高优先级的硬证据。DeepSeek-V3 的 256 experts + top-8 routing 是其具象来源：685B 参数但仅 37B 激活。
2. **Communication Wall（§4.2）**：EP 下 token 必须按 router 决策跨 GPU 重分布（all-to-all），其通信量正比于 `tokens × hidden`，且拓扑上呈 all-to-all pattern，远比 TP 的 all-reduce 难以与计算重叠。**优化前 EP all-to-all 占训练时间 20–60%**：EP 留在 NVLink 域内（如 DeepSeek-V3 EP64 on GB200 NVL72）约 20%；EP 跨节点（DeepSeek-V3 EP64 on H100 across nodes）升至 40–60%（§4.2 引言）。DeepSeek-V3 有 58 MoE 层，每层 2 次 all-to-all（dispatch+combine），单次前向 116 次，反向翻倍；50 GB/s 跨节点带宽下单次 200 MB payload 即需数毫秒（§4.2.1）。
3. **Compute Efficiency Wall（§4.3）**：每个 expert 收到的 token 数动态变化。DeepSeek-V3 的 256 小专家每 expert GEMM 的 M 维约 128 tokens，远低于 Tensor Core 峰值所需的数千（§4.3.1）。叠加两个子问题：**(a) kernel efficiency**——细粒度专家产生小 GEMM + router/dispatch 一堆小算子无法饱和 GPU；**(b) host overhead**——众多小算子的 launch 开销让 CPU 跟不上派发，profiling trace 出现 GPU idle bubbles（§4.3.1）。细粒度专家（多个独立 GEMM）、低精度量化 kernel（额外 launch）、dropless routing（需 host-device 同步查 token 数）三者叠加放大 host-boundedness。

论文要回答的核心问题：能否在一个**生产级、开源、co-design 全栈**的框架里，同时打掉三面墙、并支持从数十亿到万亿参数、千卡级集群的 MoE 训练，且把 DeepSeek-V3-685B / Qwen3-235B 这类真实 SOTA MoE 模型跑到接近硬件峰值。约束（§1.2）："Optimizing one dimension often shifts pressure to another, demanding co-design across the full system stack"；且要兼容 dense Megatron-Core 已有的 TP/CP/PP/DP/SP 多维并行栈与 FP8/NVFP4、长上下文等既有能力。

## 关键创新点

1. **Parallel Folding：解耦 attention 与 MoE 的并行映射（§3.3.1–3.3.3）**
   机制：dense 的并行映射是「层间一致」的 TP/SP/CP/PP/DP 五维对每层施加同一组 rank 映射。MoE 打破这一假设：attention 偏 TP/SP/CP，expert 偏 EP+DP。**Figure 5（M3 caption p17）**对比了三种配置下 attention（上行）与 MoE（下行）的并行映射，黑虚线为「Legacy Mappings」刚性 1:1 耦合（强制 EP≤DP），绿线为「MoE Parallel Folding」让 EP 跨 TP×CP×DP 子群独立折叠。做法是**把并行映射从「层」解耦到「子模块」**——attention 子模块用一组 parallel mapping，MoE expert 子模块用另一组，由 Parallel Group Manager（§2.2.1）维护 rank 在不同子模块间的身份切换。
   效果：EP 作为「第五维」（§3.2.3）与 TP/PP/DP/CP/SP 任意组合。在 256-expert 模型 + NVL72 系统上（§9.1.2 Example），Parallel Folding 设 expert TP=1（每 expert 单卡运行，最大化 GEMM 效率），EP64 全部落在 NVLink 域内。案例研究（§9.2.2）的 DeepSeek-V3 选 EP64 让每 GPU 恰持 4 个 experts（256/EP64），消除本地 token permutation 开销。

2. **Memory-Efficient Permutation：零开销激活压缩（§4.1.2 "Zero-Overhead Activation Reduction"）**
   机制：MoE dispatch 前需把 token 按 expert 做 permutation（重排成 per-expert 连续）。朴素实现物化一份 permuted copy，激活显存翻倍。该方法以 index-only 视图/算子重排，避免显式复制。
   效果：对 DeepSeek-V3（Table 3 配置）**节省约 26.3 GB 激活显存**（§4.1.2，约 131 GB 激活预算的 20%）。标题即「Zero-Overhead」——不增计算即可削显存，不向 Comm/Compute Wall 转嫁压力，是 §1.2 co-design 原则的典范。

3. **Reduced-Precision 激活：FP8/FP4 削激活（§4.1.3）**
   机制：linear layer 为反向保存的输入张量改用 FP8/FP4 而非 BF16 存储。
   效果：对 DeepSeek-V3 配置，启用 FP8 训练**减少约 16 GB 激活显存**（约占 131 GB 预算的 12%，对应 32 GB 可 FP8 化的 linear-layer 输入的一半；attention scores、SDPA 等仍留 BF16）（§4.1.3）。Table 8 给出统一账本：**FP8 激活减 50%、FP4 减 75%**（§5.2.1）。

4. **Fine-grained Recomputation + 细粒度 Offloading（§4.1.4, §4.1.5）**
   机制：recomputation 不再以「整层」为粒度，而按 MoE 内部子段（router 输出、dispatch buffer、expert GEMM 输入/输出，H100 上为 `mlp, mla_up_proj, moe_act, layernorm`，GB200 上仅 `mlp`）选择重算/保留；offload 把不被立即使用的激活异步搬到 CPU，需时再 prefetch。**Figure 9（M3 caption p28）**与**Figure 10（p26）**描绘了 stream overlap：compute stream 跑 forward/backward，D2H stream 在 FC2 后立即 offload、在 backward FC1 前 prefetch，因为 Copy Engine 与 Compute Engine 独立，只要 compute 时间≥transfer 时间，PCIe 开销即被完全隐藏。
   效果：Table 5 给出实测——DeepSeek-V3 full（TP1PP8EP32VPP4 MXFP8）：169→151 GB（**−10.7%**），945→930 TF/s（**−1.6%**）；Qwen3-235B 经 offload 把 TP2→TP1 + EP16→EP64：172→175 GB（+1.7%）但 800→920 TF/s（**+15.0%**）。总体 fine-grained offloading 降显存 10–18%，吞吐开销仅 1.6–2%（§4.1.5）。对 60+ 层深模型，offloading 把峰值显存从 L×layer_input+intermediate 降到 1×layer_input+intermediate，独立于模型深度——这是 full recompute 无法达到的（§4.1.5）。

5. **Weight & Optimizer 低精度存储 + Offload（§4.1.6）**
   机制：(a) Precision-aware Optimizer——Adam 的 first/second moment 从 FP32（8 bytes/param）降到 BF16（4）或 FP8（2），但 update 仍在 FusedAdam kernel 内动态 cast 回 FP32 计算。四级可配精度（main grad/param、moment1/2）。(b) State Offloading——`optimizer.step()` 后把 moment + master weights 移到 CPU，前向/反向时 GPU 显存被释放。
   效果：BF16 moments 约省 optimizer state 50%（~10–12 GB，对应 Table 3 的 32.1 GB 预算）；DeepSeek-V3 DP 分片后 per-param-per-rank 从 6+12/d 字节降到 6+8/d 字节（§4.1.6）。State offloading 在 GB200 NVLink-C2C 上省 **15–20 GB**（占 32.1 GB optimizer+weight 预算的 47–62%），每 iter 仅 **0.1–0.2 秒**开销。GB200 上因 C2C 带宽高 offload 实用、H100 上则更多依赖 recompute（§9.2.2）。

6. **FSDP for MoE：Dual DeviceMesh + Zero-Copy（§4.1.7）**
   机制：把 ZeRO/FSDP 的分片参数+梯度+optimizer 应用于 MoE，但 expert 权重按 EDP（expert data-parallel）group 分片而非全 DP group，attention 权重按全 DP group 分片——由 **dual DeviceMesh**（primary 管 DP-Shard/DP-Outer/TP/CP，auxiliary Expert DeviceMesh 管 EP+EDP）自动路由。**Figure 11**对比 FSDP2 的 per-parameter uniform sharding 与 Megatron-FSDP 的 per-module non-uniform sharding（flatten+concat 后跨设备非均匀切片，shard 边界与通信 buffer 对齐）。
   效果：**Llama3-405B** 训练中 non-uniform sharding 减通信约 **10%**；持久双 buffer + NCCL User Buffer Registration 实现 zero-copy，NVLink 系统通信 kernel 的 SM 占用从 8–32 SMs 降到 **1–4 SMs**，SHARP IB 上网络交换机承担 reduce、SM 全部释放（§4.1.7 Zero-Copy）。还消去 PP 的 stage balancing/MTP 放置/Vision encoder 分区等工程痛点。

7. **DeepEP 与 HybridEP：最大化 EP all-to-all 带宽（§4.2.2）**
   机制：MoE 层的 forward 是 **Figure 1（M3 caption p09）**描绘的四阶段流水线——Route（router 产 top-k + routing weights）→ Dispatch（token 按 expert permutation 后经 AllGather/all-to-all/Flex/DeepEP/HybridEP 跨 GPU 重分布，permutation 使 per-expert 工作连续致密从而能被单个 Grouped GEMM 服务）→ Compute（每 GPU 在单个 fused Grouped GEMM 内跑本地 experts）→ Combine（inverse permutation + 加权求和，shared expert 输出在此可选合并）。EP 通信的核心即 Dispatch 与 Combine 两次 all-to-all。标准 NCCL all-to-all 需先做 permutation（每 token 复制 top-k 次），产生冗余流量与 host 开销。Megatron-Core 提供两个 **token-based dispatch** 后端，消除 permutation、不送冗余 token：**DeepEP**（DeepSeek 开源，低延迟 dispatch/combine 原语）与 **HybridEP**（NVIDIA 自研，遵循同样 token-based 原理，利用 TMA + IBGDA 硬件原语，目标同等或更高带宽、更低 SM 占用，支持 MNNVL）。**Figure 14/15（M3 p30/31）**展示 HybridEP 的 dispatch/combine kernel 设计：dispatch 经 shared memory + FIFO queue，跨节点用 RDMA warp group 先跨节点同 local-index 交换再节点内转发，减少跨节点流量并让节点间/节点内 transfer overlap；combine 把 reduction 融进通信 kernel（标准 all-to-all dispatch 后需单独 unpermute，HybridEP 一步到位）。
   效果：Table 7 实测（hidden=7168, seq=4096, 256 experts）——GB200 上 EP64 dispatch：HybridEP **675 µs** vs all-to-all 930 µs；H100 上 EP64 dispatch：**4626 µs** vs 9164 µs（约 2× 提升），combine 同量级。跨节点场景增益最大。表只报通信延迟，端到端含 permutation+host 开销时差距更大。

8. **EP Communication Overlapping：1F1B + W/D Split（§4.2.3）**
   机制：用 dedicated 1F1B all-to-all overlap 把相邻 micro-batch 的 forward/backward 合并、跨 CUDA stream 交错 compute 与 all-to-all（§4.2.3）。对比两种 pattern：Merged FWD-FWD/BWD-BWD（2× 峰值激活显存，forward 仅 backward 一半计算量、overlap 机会少）与 **Merged FWD-BWD（DualPipe 等价，首选）**——无额外显存开销（forward 激活被 backward 复用），但首 FWD 与末 BWD 仍在关键路径上无法隐藏。进一步用 **W/D Split（Weight-Gradient / Data-Gradient Split）**：把 backward MLP 拆成 W/mlp（weight gradient，与 B/dispatch 无依赖）和 D/mlp（data gradient，喂给 B/dispatch），W/mlp 可与 F/mlp overlap 来隐藏 B/dispatch。**Figure 18（M3 caption p34）**对比 baseline 顺序执行 vs 1F1B + W/D split 的 pipeline 时间线；**Figure 19**展示与 Interleaved PP（VPP）结合的三阶段（warmup/1F1B/flush）schedule。还可配 Flexible Asymmetric VPP 做混合 dense/MoE 层的逐 stage 负载均衡。
   效果：在 DeepSeek-V3 H100 训练上，DeepEP 用 **20 SMs/GPU**、引入约 **20% GEMM-efficiency overhead**（SM carve-out 代价），但 combined with overlap 后实现 **93% overlap ratio**，expert 通信占比从 30–40% 降到 **<5%**（§4.2.3）。整 §4.2 合计把 all-to-all 占比降到 **<10%**（§4.2.4 Summary）。1F1B 在大 VPP 下比 DualPipeV 更快，大 PP+大 micro-batch 下两者都趋近最优。

9. **Grouped GEMM + Permutation Fusion + Router/Aux-Loss Fusion（§4.3.2/4.3.3/4.3.4）**
   机制：MoE 的 expert FFN 是「同形状多个 GEMM」，朴素逐 expert 调 cuBLAS 有 launch+padding 浪费。Grouped GEMM 一次 launch 处理所有 expert，**通过重叠 kernel 的 wave tail effect 提升利用率**（§4.3.2）。四档实现：(i) 多 stream cuBLASLt GEMM（支持 BF16/各 FP8/NVFP4）；(ii) CUTLASS Grouped GEMM（单 kernel，TE 当前仅 BF16 on Hopper）；(iii) cuBLASLt Grouped GEMM via `CUBLASLT_BATCH_MODE_GROUPED`（shape 在 device 端，解锁 CUDA Graph，覆盖所有精度，意在取代 i/ii）；(iv) cuteDSL Grouped GEMM with fusions（融 activation+quantization+scaling swizzle，MXFP8/NVFP4 on Blackwell，针对 FC1 fprop 与 FC2 dgrad）。**Figure 20（M3 p37）**是 permute fusion pipeline：Preprocessing 生成 Row ID offset map（每前向一次复用）→ Permute 按 map 散射 token 到 per-expert buffer（memory-efficient 变体同时 permute probabilities）→ Unpermute 反向 gather+sum（memory-efficient 路径 plain sum，否则 probability 加权，累加一律 FP32）。**Figure 21**是 router fusion：把 score computation（top-k + softmax/sigmoid，含 group top-k、sigmoid/softmax 组合、scaling）、aux-loss score、aux-loss 计算分别融进三个 kernel。
   效果：消除 per-expert kernel launch overhead、减少中间张量落 HBM、把 router 一堆小算子压到 3 个 kernel。

10. **CUDA Graphs（full / layer-wise / partial）+ Sync-Free Kernels + ECHO + Paged Stashing：Dropless MoE 全图覆盖（§4.3.6, §4.3.7）**
    机制：CUDA Graphs 要求 static shapes，但 dropless MoE 的 per-expert token 数动态变化——这是「drop」的根本来源。三种 mode（**Figure 23**）：**Full CUDA Graphs**（捕获整前向-反向到单 graph，仅适用于 droppable+pad-to-max 的静态 shape 场景）；**Layer-wise / Partial CUDA Graphs**（每层单独捕获，只捕静态部分：attention/router/EP preprocessing/shared expert，留下 dispatch/expert GEMM/combine 动态部分跑 eager，**Figure 24/25**）；Sync-Free + ECHO + Paged Stashing 三件套进一步让 dropless 也能进 full graph。
    - **Sync-Free Kernels / Device-Initiated**：device-initiated Grouped GEMM（cuBLASLt 自 CUDA 13.1 支持 shape 作为 device array；cuteDSL 把 SwiGLU+quantization 融进 epilogue）与 sync-free dispatch with HybridEP（传 upper bound、预分配 output buffer），消除 host-device 同步点。
    - **ECHO（Elastic Cloning for Hot Experts）**：bin-packing 算法把 hot expert 的 spillover token 匹配到 underutilized rank 的 spare capacity，动态克隆 hot expert（forward 经 HybridEP sync-free 通信复制权重，backward 经 Expert Gradient Dispatch 把梯度 reduce 回 home expert），降低 per-rank token 方差，使 worst-case buffer 接近实际 usage。**Figure 27（M3 p45）**展示 planner 生成 hot expert map + routing map 的工作流。
    - **Paged Stashing**：把动态 dispatch buffer 拆成固定大小 page 池（默认 64 tokens/page，free list 为 circular buffer，stash/reload 均为 device-initiated kernel）。**Figure 28（M3 p46）**对比三种内存布局：eager（按实际用量动态分配）vs baseline static（每层 worst-case buffer 独立预留，O(layers×worst_case) 严重碎片）vs Paged Stashing（单一 worst-case tmp buffer 跨层共享 + paged stashing buffer 只存实际 token）。**Figure 29**展示 Pack/Unpack stream 与 Compute stream overlap，stash 与下一层 compute 并行、reload 提前 prefetch。
    效果：partial CUDA Graphs 在 DeepSeek-V3 GB200 训练上**端到端 +10% 速度，代价仅 ~7 GB 额外显存**（§4.3.6）。三件套合起来把 dropless MoE 也纳入 full CUDA Graphs 覆盖（§4.3.7 标题 "Full CUDA Graphs Coverage for Dropless MoE"）。Paged Stashing 把显存从 O(layers×worst_case) 降到 O(worst_case+actual_total)。Memory 优化上：graphed 与 non-graphed 操作需独立 PyTorch memory pool；PP 下每 microbatch 需独立 graph（L×M×2 个），非 PP 可共享（L×2 个），pool sharing + buffer reuse 把开销压到最小。

11. **Reduced-Precision Recipes + MoE-specific Fusion：Per-Tensor FP8 → Blockwise FP8 → MXFP8 → NVFP4（§5.3.1–5.3.4, §5.4）**
    机制与精确参数：四档逐级更细量化粒度（**Figure 30**）。**Per-Tensor FP8**（Hopper+Blackwell，hybrid E4M3 输入/权重 + E5M2 梯度；分 delayed scaling（历史 amax）与 current/live scaling（JIT amax，推荐））。**Blockwise FP8**（Hopper 推荐；E4M3；激活/梯度 1×128 tile、权重 128×128 block；DeepSeek-V3、Minimax-M2、Ant Ling-2.0 等大模型生产验证）。**MXFP8**（Blackwell 默认；1×32 microscaling，E8M0 scale factor，第五代 Tensor Core 原生支持，硬件加速 scaling）。**NVFP4**（Blackwell；E2M1 FP4 元素 + 两级 microscaling：per-tensor FP32 scale + per-block E4M3 8-bit scale，block=16 元素；配 RHT（Random Hadamard Transform，用于 weight gradient 抑制 outlier）、2D scaling（16×16 weight block）、stochastic rounding（用于 gradient）三件算法技术保收敛）。
    MoE-specific 挑战与解（§5.4）：(a) **Padding/Unpadding Fusion**（§5.4.1）——FP8/FP4 GEMM 需 16 对齐（per-tensor/blockwise）或 32（MXFP8/NVFP4），TMA 需 dot-product 维 16-byte 对齐；weight-gradient GEMM 的 dot-product 维是动态的 M（token）维，需 zero-padding，进一步把 tokens-per-expert padding 到 128（为 grouped quantization kernel）。解法：routing map padding（pad routing map 而非 token，只多发少量 token）或把 padding 融进 permutation（默认）。(b) **Grouped Quantization + Grouped GEMM**（§5.4.2/4.4.3）——把多 expert 的 quantization 融进单 kernel；NVFP4 的 RHT 必须与 quantization 融合（否则需额外全精度 BF16 读写，带宽爆炸）；Wgrad 路径还需 absorb transpose；scale-factor swizzling 需 128×4 对齐、per-expert GEMM 应用，故强制 128-token per-expert 对齐（在 token-permute kernel 里 fuse zero-padding 保证）。per-tensor FP32 第二级 scale 在 MoE 里是 per-expert scale（非全局共享），需 online 从 routed token 算 amax，用 128-aligned guarantee 适配为 CUDA-Graph-safe grouped Hadamard-amax kernel。
    效果：FP8 在大规模 MoE 上**端到端 +10–25%**，FP4 更甚（§4.3.5）。**Table 8** 总结跨三墙收益：Memory（激活 50%/75% 减 + 消 BF16 weight copy + BF16 optimizer states）、Communication（parameter AllGather 减 50%，1 byte vs 2 byte；NVFP4 因需 row-wise+column-wise 两份 FP4 weight 仍只省 50%；MXFP8 因 fwd/bwd 不同量化方向需 BF16 通信，无优势）、Compute（FP8/FP4 Tensor Core 快于 BF16；代价是 quantization kernel overhead，由 fusion + grouped quantization + CUDA Graph 管理）。**FP8/FP4 Primary Weights**（§5.3.5）消除 BF16 中间层，从 FP32 master 直接量化到 FP8/FP4，省一份 BF16 权重内存 + 加速 parameter AllGather。

12. **Long-Context MoE Training（§6）**
    机制：长序列下 SDPA 的 O(s²) 凌驾于 MoE/FFN 的 O(s) 之上。**Figure 34（M3 p57）**画 SDPA 二次曲线 vs MoE 线性曲线的交叉：4K–8K 时 MoE 占主导（**MoE 59.4%**），64K 时 **SDPA 占 69.7%** FLOPs（短序列仅 10–15%）（§6.1）。SDPA 本身已被 FlashAttention/cuDNN 高度优化（**Table 9**：Hopper 4K forward 553 / backward 422 TF，16K 638/523；Blackwell 4K 1324/1083，16K 1698/1298 TF），不构成瓶颈——焦点转向 memory/communication。**Figure 35（M3 p59）**对比 CP(P2P)/CP(A2A)/TP 三种 attention 并行的通信与权重 sharding 模式：P2P CP ring 式交换 KV 与 SDPA 计算自然 overlap（节点间首选）；A2A CP 把 sequence-sharded 转 head-sharded 再 SDPA（介于 P2P 与 TP 之间）；TP 额外 shard linear 权重但 linear 层多出 collectives（节点内首选）。Hierarchical CP 可两者结合。
    效果：256 Hopper GPU、256K 序列长度上，DeepSeek-V3 达短上下文 MFU 的 **88%**（TP + optimizer CPU offload + selective recompute），Qwen3-235B-A22B 达 **129%**（>100% 因 SDPA 在长序列主导且 kernel 极高效）（§6.5）。optimizer CPU offload 在 16K+、~50% MFU 下最坏开销约 2%。64K 时 SDPA 占 72% compute，重算 SDPA 加 18% compute、降 16% 性能、仅省 9 GB；改重算 non-SDPA 组件可省 **89.8 GB** 且性能影响更低——故推荐禁用 core attention recompute。**Packed Sequences（§6.4.1, THD 格式）**对 RL/SFT 变长序列省 40–60% 显存、提 1.5–2× 吞吐；**Dynamic-CP（§6.4.2）**每 micro-batch 自适应选 CP size（候选 1..dp×cp，2 的幂），避免短序列被强塞大 CP，在高度不均衡的多模态场景**端到端 +35–60%**。

13. **生产特性：Load Balancing / Token Dropping / Shared/Latent Expert / Distributed Checkpoint / Upcycling / MTP / Muon（§7）**
    - **Router & Load Balancing（§7.1, Figure 2）**：router = gating linear projection + score function（softmax 或 sigmoid，DeepSeek-V3 用 sigmoid 归一）/ top-k selection；产出 per-token probabilities（combine 权重）与 boolean routing map（dispatcher 用）。**Figure 2（M3 p10）**列出 load balancing 机制谱系：z-loss、Sinkhorn（assignment-based，非可微硬均衡）、Aux_loss / Seq_aux_loss / Global_aux_loss（gradient-based，可微软均衡）、Auxiliary-loss-free（Expert Bias，feedback-based 自适应均衡）。Token Dropping 两档：dropless（默认，无 capacity 约束，最大化表达力但 per-expert 负载动态）与 droppable（explicit capacity limit，超额 token 经 residual 旁路，给静态 shape 与 pad-to-max，解锁 full CUDA Graphs，适合训练早期 router 未稳定时）。
    - **Shared Experts（§7.2, Figure 40）**：DeepSeek-V2/V3、Qwen 等含处理全部 token 的 shared expert，提供一致 baseline 容量；`--moe-shared-expert-overlap` 时 shared expert 与 all-to-all + routed expert 并行执行隐藏延迟。
    - **Latent MoE（§7.3）**：在 dispatch 前插 shared down-projection W↓（R^{ℓ×d}）、combine 后插 W↑（R^{d×ℓ}），ℓ<d；routing 仍走全 hidden 维，routed expert 在压缩 latent 空间运行。压缩比 α=d/ℓ 同时减 all-to-all 通信与 expert 权重大小 α 倍。ℓ-MoEacc（推荐，E 和 K 同乘 α）在 iso 推理成本下指数级扩大 expert 选择组合空间，95B 规模下一致优于标准 MoE；已被 NVIDIA Nemotron-3 Super/Ultra 采用。
    - **Distributed Checkpointing（§7.4）**：ShardedTensor descriptor 编码 global shape/offset/sharding pattern，任意 TP/EP/PP 重配置可 any-to-any resharding（如 TP=2,EP=4 存的 checkpoint 可 TP=4,EP=8 加载），支持 Zarr（默认）与 PyTorch Distributed 后端，fully parallel saving 无 coordinator 瓶颈。
    - **Flexible Asymmetric VPP（§7.5, Table 10/Figure 41）**：传统 VPP 要求均匀层分布，MoE 因 dense/MoE/embedding/loss/MTP 层 cost 差异大而难均衡。DeepSeek-V3（61 decoder + 1 MTP）PP=16, VPP=2 配置：rank0 = embedding + 3 dense decoder（cost≈2 MoE 层）；rank1–13 每 stage 2 个 MoE decoder；rank14 放 MTP；rank15 放 loss（Table 10）。Figure 41（M3 p66）可视化这种 strategic placement。
    - **Upcycling（§7.6, Figure 42）**：把预训练 dense 模型转成稀疏 MoE，免从头训练。**Figure 42（M3 p67）**展示 granular upcycling 到 **E2G2T2**（4 experts, top-2, half intermediate size）：(1) MLP 权重在 intermediate 维 shard（4h→2h）然后 duplicate；(2) router 权重初始化一半然后 duplicate。这保证 Top2 必选每对 shard 各一，使 MoE 输出在训练 step 0 与 dense 模型 bit-equivalent——lossless warm-start。配 softmax-then-topK routing。
    - **MTP / Muon / MuonClip（§7.7, §7.8）**：Multi-Token Prediction 与 flexible PP 结合做 VPP 内 strategic placement；Muon optimizer（matrix-aware，正交化整权重矩阵，减训练步数）集成 QKV split layout + 分布式 optimizer sharding + CPU offload；MuonClip 用 cuDNN/cudnn-frontend/TE 的硬件加速实现防止 trillion 参数 QK dot-product 无界增长致 attention 爆炸。

## 表格（原文结构化，全部数字取自全文 Table）

**Table A — 头条 benchmark（Table 11，force-balanced routing，Megatron-Core v0.16 + TE dev）**

| 模型 | 系统 | #GPUs | SeqLen | Dtype | Per-GPU TF | Tokens/s/GPU |
|---|---|---|---|---|---|---|
| DeepSeek-V3 | GB300 | 256 | 4,096 | MXFP8 | 1,233 | 4,730 |
| DeepSeek-V3 | GB200 | 256 | 4,096 | MXFP8 | 1,048 | 4,020 |
| DeepSeek-V3 | GB200 | 256 | 4,096 | BF16 | 857 | 3,298 |
| DeepSeek-V3 | H100 | 1,024 | 4,096 | FP8-BLK | 368 | 1,412 |
| Qwen3-235B | GB300 | 256 | 4,096 | MXFP8 | 974 | 6,583 |
| Qwen3-235B | GB200 | 256 | 4,096 | MXFP8 | 919 | 6,212 |
| Qwen3-235B | GB200 | 256 | 4,096 | BF16 | 750 | 5,100 |
| Qwen3-235B | H100 | 256 | 4,096 | BF16 | 320 | 2,132 |
| Qwen3-235B | GB300 | 128 | 131,072 | MXFP8 | 1,150 | 1,556 |

> Abstract 头条（GB300/GB200）= DeepSeek-V3-685B 1,233/1,048、Qwen3-235B 974/919 TFLOPS/GPU，与 Table 11 一致。GB200/GB300 相比 H100 在同等或更少 GPU 数下约 3× token 吞吐（更高内存带宽 + 原生 MXFP8 Tensor Core）。长上下文 131K Qwen3 仍持 1,150 TF/GPU。

**Table B — DeepSeek-V3 per-GPU 显存解剖（Table 3，BF16, PP4×VPP4×EP64, 256 GPUs）**

| Component | Memory/GPU | Optimization Techniques |
|---|---|---|
| Weights & Gradients | 36.4 GB | PP, EP, or TP sharding |
| Main Weights & Optimizer States | 32.1 GB | Distributed optimizer, BF16 moments |
| Activations | 131.0 GB | Low Precision, Recomputation, Offloading |
| **Total** | **199.5 GB** | （H100 仅 80 GB，必须优化） |

> DeepSeek-V3 = 685B 总参（671B Main + 14B MTP）/ 37B 激活 / 18× gap / 256 experts / top-8 / 58 MoE 层。

**Table C — Fine-grained Offloading 实测（Table 5）**

| Model & Config | Baseline | +Offload | Mem ∆ | Throughput ∆ |
|---|---|---|---|---|
| DeepSeek-V3 full (TP1PP8EP32VPP4, MXFP8) | 169 GB / 945 TF/s | 151 GB / 930 TF/s | −10.7% | −1.6% |
| Qwen3-235B (TP2→TP1 + EP16→EP64) | 172 GB / 800 TF/s | 175 GB / 920 TF/s | +1.7% | +15.0% |

**Table D — HybridEP vs all-to-all 通信延迟（Table 7, µs；hidden=7168, seq=4096, 256 experts）**

| EP size | GB200 HybridEP | GB200 a2a | H100 HybridEP | H100 a2a |
|---|---|---|---|---|
| dispatch 8 | 391 | 735 | 661 | 1,265 |
| dispatch 16 | 578 | 743 | 1,485 | 5,774 |
| dispatch 32 | 612 | 769 | 3,064 | 8,059 |
| dispatch 64 | 675 | 930 | 4,626 | 9,164 |
| combine 8 | 353 | 741 | 624 | 1,277 |
| combine 16 | 527 | 765 | 1,688 | 5,628 |
| combine 32 | 646 | 758 | 3,088 | 7,815 |
| combine 64 | 744 | 827 | 4,398 | 8,727 |

**Table E — SDPA 性能（Table 9, DeepSeek-V3, cuDNN）**

| Platform | SeqLen | Forward TF | Backward TF |
|---|---|---|---|
| Hopper | 4,096 | 553 | 422 |
| Hopper | 16,384 | 638 | 523 |
| Blackwell | 4,096 | 1,324 | 1,083 |
| Blackwell | 16,384 | 1,698 | 1,298 |

**Table F — Reduced-Precision 跨三墙收益（Table 8）**

| Wall | Benefit | Details § |
|---|---|---|
| Memory | 激活减 50%(FP8)/75%(FP4)；消 BF16 weight copy；BF16 optimizer states | §4.1.3 / §5.3.5 / §4.1.6 |
| Communication | parameter AllGather 减 50%（FP8/FP4 primary weights） | §5.3.5 |
| Compute | FP8/FP4 Tensor Core 快于 BF16；代价=quantization kernel overhead | §4.3.5 / §4.3.2 |

**Table G — DeepSeek-V3 Case Study 最终配置（Table 17/18）**

| Configuration | GB200 | H100 |
|---|---|---|
| Hardware | 256×GB200 | 1,024×H100 |
| Parallelism (TP/PP/EP)† | 1/4/64 | 2/8/64 |
| VPP | 4 | 4 |
| GBS/MBS/SeqLen | 8192/1/4096 | 8192/1/4096 |
| Precision | MXFP8 | FP8-Blockwise |
| Dispatcher | HybridEP | DeepEP |
| Recompute | mlp | mlp, mla_up_proj, moe_act, layernorm |
| CUDA Graphs | Enabled | — |
| EP all-to-all Overlap | — | Enabled |
| **Performance (TFLOPS/GPU)** | **1,048** | **368** |

> †Parallel Folding：TP 仅作用于 non-MoE 模块，expert TP 恒为 1。GB200 192GB/GPU + NVL72（1.8 TB/s 双向）让 EP64 留在 NVLink 域内，通信墙由拓扑单独解决，瓶颈转为 CPU overhead→用 CUDA Graphs + kernel fusions；H100 80GB + NVL8 让 EP64 跨 8 节点，需 DeepEP + EP overlap 隐藏跨节点延迟，FP8 省下的显存给 overlap buffer 让位。同一模型在两硬件上走向完全不同的优化栈。

**Table H — 三面墙 × 对应技术栈（依 §4 子章节定位）**

| 墙 | 子问题 | Megatron-Core 技术 | § |
|---|---|---|---|
| Memory | 激活显存膨胀 | Memory-Efficient Permutation（省 26.3 GB） | §4.1.2 |
| Memory | 激活显存膨胀 | FP8/FP4 激活（省 16 GB / 50% / 75%） | §4.1.3 |
| Memory | 激活显存膨胀 | 细粒度 Recomputation（H100: mlp+mla_up_proj+moe_act+layernorm） | §4.1.4 |
| Memory | 激活显存膨胀 | Fine-grained Activation Offloading（−10.7%, −1.6%） | §4.1.5 |
| Memory | 权重+optimizer 显存 | Precision-aware Optimizer（−50%）+ State Offload（−15–20 GB） | §4.1.6 |
| Memory | 参数大头在 expert | FSDP for MoE（dual DeviceMesh, non-uniform sharding, zero-copy） | §4.1.7 |
| Comm | EP all-to-all 带宽低 | DeepEP + HybridEP（H100 EP64: 4626 vs 9164 µs） | §4.2.2 |
| Comm | EP 通信延迟 | 1F1B + W/D Split overlap（30–40% → <5%, 93% overlap ratio） | §4.2.3 |
| Compute | kernel 碎片/launch 开销 | Grouped GEMM（4 档实现）+ Permutation/Router Fusion | §4.3.2/3/4 |
| Compute | host overhead | CUDA Graphs（partial, +10% / ~7 GB） | §4.3.6 |
| Compute | 动态形状致 graph drop | Sync-Free Kernels + ECHO + Paged Stashing（O(L×W)→O(W+A)） | §4.3.7 |

## 与同类对比

- **vs dense Megatron-LM 并行栈（[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]）**：dense 版的 f/g 算子 + column/row parallel GEMM 假设「层间并行映射一致」。Parallel Folding（§3.3.1）打破这一假设，让 attention 与 expert 子模块用不同并行映射——把 Megatron-LM 的层级并行抽象**下沉到子模块级**。dense 版消除 GeLU 同步点的思路（column-parallel 使非线性可独立施加）在 MoE 版里演化为「消除 expert 间同步点」的 Grouped GEMM + 算子融合。
- **vs MegaScale 10k-GPU 训练（[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]）**：MegaScale 聚焦 dense LLM 在 10k GPU 的 stability + 3D overlap + LAMB 放大 batch 削 pipeline bubble。本论文面对 MoE 特有的 EP all-to-all（非 all-reduce）通信模式与动态形状 CUDA Graph 难题——MegaScale 的通信-计算 overlap 思路被推广到 EP all-to-all 重叠（§4.2.3），但 EP 的 all-to-all 拓扑比 TP all-reduce 更难隐藏，需 DeepEP/HybridEP 专用 kernel + W/D split 而非简单 chunk pipeline。
- **vs ZeRO（[[zero-memory-optimizations-toward-training-trillion-parameter-models]]）**：ZeRO-1/2/3 把 optimizer state/gradient/parameter 沿 DP 分片。FSDP for MoE（§4.1.7）继承 ZeRO 分片思想，但 expert 参数沿 EDP group 分片（而非全 DP group），dual DeviceMesh 让 EP/DP 对 attention/MoE 子模块分别施加——比 ZeRO 的「全层统一 DP 分片」更细。ZeRO 未处理 MoE dispatch 激活（§4.1.2/4.1.5）。
- **vs DeepSeek-V3 / Kimi-K2 / CloudMatrix 训练栈（[[deepseek-v3-technical-report]]、[[kimi-k2-open-agentic-intelligence]]、[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）**：这些是「用 MoE 训练框架训练出的模型」——DeepSeek-V3-685B 恰是本论文 benchmark 的对象之一（GB300 1,233 / GB200 1,048 / H100 368 TFLOPS/GPU），Qwen3-235B 同样（974/919/320）。Kimi-K2（1T 总参/32B 激活/31×）作为细粒度 MoE 的对照被引用。它们的训练栈多为自研（DeepSeek 自有 EP 通信、DualPipe 等），本论文是 NVIDIA 侧把这些 SOTA MoE 训练所需能力**产品化、开源化**到 Megatron-Core，且 Megatron-Bridge 提供 HF↔Megatron 双向转换使 RL 框架（veRL/Slime/NeMo RL）可复用。CloudMatrix（昇腾）侧体现非 NVIDIA 硬件上同类 MoE 训练系统设计的产业对照。
- **vs DualPipe / DeepEP（DeepSeek 自研）**：本论文的 1F1B + W/D split overlap 与 DeepSeek DualPipe 思想等价（§4.2.3 明确 "DualPipe-like bidirectional schedule built on top of standard 1F1B"），并在 latency 对比中纳入 DualPipeV；HybridEP 与 DeepEP 同走 token-based dispatch 原理，但 HybridEP 额外面向 MNNVL + TMA/IBGDA 优化，在 NVL72 上无需 overlap 即可吃满 1.8 TB/s。

## 跨论文关系（→ MOC 谱系）

本论文位于 **训练系统谱系** 中 Megatron 主线的 MoE 化演进节点：
- 继承 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] 的 column/row parallel GEMM + f/g 通信算子思想，并下沉到子模块级（Parallel Folding）。
- 推广 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] 的通信-计算 overlap 哲学到 EP all-to-all（DeepEP/HybridEP + 1F1B W/D split overlapping）。
- 在 MoE 场景下特化 [[zero-memory-optimizations-toward-training-trillion-parameter-models]] 的分片思想（FSDP for MoE，EP-aware dual DeviceMesh 分片）。
- 延续 [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] 的「生产级集群训练」定位，并补上 MoE 全栈 co-design 与 RL 后训练（§10）。
- 作为 [[deepseek-v3-technical-report]] / [[kimi-k2-open-agentic-intelligence]] / [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]] 等 SOTA MoE 模型训练的事实框架之一（DeepSeek-V3/Qwen3 即其 benchmark 对象；MuonClip/Muon 与 [[muon]] 谱系相连；Latent MoE 被 Nemotron-3 采用）。
- 与 [[deepseek-r1]] RL 训练范式呼应：§10 专门讨论 RL 后训练对 MoE 引擎的变长序列、memory offloading、online weight export（Megatron-Bridge）、training-inference routing discrepancy 等挑战。

## 局限与边界

1. **硬件强绑定**：头条性能（1,233 / 1,048 / 974 / 919 / 368 / 320 TFLOPS/GPU）高度依赖 Blackwell（GB300/GB200）的 MXFP8 Tensor Core 与 NVL72 拓扑（1.8 TB/s 双向）/ H100 的 blockwise FP8 + NVL8。DeepEP/HybridEP 的带宽优势依赖 NVLink+IB 拓扑——EP 跨节点时 H100 上 EP64 dispatch 仍需 4,626 µs（Table 7），比 GB200 的 675 µs 高近 7×。在非 Blackwell 或弱互联环境（PCIe、跨机 IB-only）上，MXFP8/NVFP4、DeepEP 低延迟档、NVL72 内通信墙「由拓扑单独解决」等结论均会失效或退化。
2. **Dropless MoE 的边界条件**：§4.3.7 的 "Full CUDA Graphs Coverage" 依赖固定上限 buffer + ECHO + Paged Stashing。ECHO 只克隆 spillover 高于平均负载的少量 expert（bin-packing 最小化克隆数），当 token-per-expert 实际负载超过预设上限、或 router 出现极端 hot expert 时仍需 fallback；worst-case buffer 可达 O(EP_size)× 实际 working set，Paged Stashing 虽降到 O(worst_case+actual_total) 但仍非"零条件 zero-drop"。DeepEP 的 20 SM carve-out 引入约 20% GEMM-efficiency overhead，是 overlap 的固有代价。
3. **低精度的精度边界**：NVFP4 primary weights（§5.3.5）虽消除 BF16 冗余存储，但 4-bit 主权重依赖 RHT + 2D scaling + stochastic rounding 三件算法技术才稳定；MXFP8 的 parameter AllGather 因 fwd/bwd 不同量化方向需 BF16 通信，省不了通信量（§5.2.2）。router/embedding/output layer/optimizer state 仍须 FP32/BF16 保护（selective precision），不能全域量化。论文 benchmark 用 force-balanced routing，真实 router 不均衡时性能会低于表列数字。
4. **benchmark 为「point-in-time snapshot」**：§8 明确基于 Megatron-Core v0.16，非性能上限，配置为经验调参非全局最优（Appendix B 才给完整并行配置）。Table 11 的 H100 DeepSeek-V3 用 1,024 GPU，Qwen3 H100 仅 256 GPU 且用 BF16（非 FP8）——同模型不同硬件配置不严格可比。
5. **未解决问题**：(a) EP 下 expert load imbalance 仍以 aux-loss/Sinkhorn/Expert-Bias/ECHO 为主，router 侧的根因式均衡仍交给模型设计者；(b) 长上下文（§6）虽给 256K 端到端（DeepSeek-V3 88% MFU、Qwen3-235B-A22B 129%），但 SDPA 二次增长意味着百万 token 级需新注意力架构，本文仅给 CP+TP+selective recompute 的应对框架；(c) 跨集群（multi-datacenter）MoE 训练不在本文范围（属 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] 类另一谱系）；(d) Dynamic-CP 的 search 是 1D grid search over microbatch count，非精确求解，强依赖经验 "knee" 点。
