# 📊 图表素材索引（figures_index）


> 按主题分类的图表清单，含 caption + 页码 + 本地图片路径，便于技术报告快速插入与引用。

> 标 ⭐ 的图已用 MiniMax 多模态深度解读（技术解读见对应论文 MD 的 Figure [!tip]）。

共 388 张图，来自 41 篇论文；其中 ⭐16 张已深度解读。

## ⭐ 精选架构图（MiniMax 深度解读，可直接插入技术报告）

### IndexCache: Accelerating Sparse Attention via Cross-Layer In — Fig.2 (p.3)
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
> [!tip] 【MiniMax 解读】IndexCache 架构图(Fig.2)：对比 (a) 标准 DSA（每层跑 lightning indexer）与 (b) IndexCache（加条件分支：F 层算并缓存索引到临时 buffer T_cache，S 层直接复用 T_cache 跳过 indexer）。T_cache 仅存当前索引张量、每 F 层覆写、无额外显存。利用 token 选择跨层冗余消除稳定层 indexer 计算。架构核心图。
*caption: Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branc… ｜ 论文 [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.2 (p.3)
![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p03.png]]
> [!tip] 【MiniMax 解读】MEDUSA 框架：在 LLM 最后隐藏层挂多个轻量解码头，第 k 个头预测 t+k+1 位 token，单次前向并行产出多候选；候选组织成树，用 tree attention 掩掩码保证因果正确，一次前向验证多分支、接受最长有效续写。无需独立 draft model，2-3x 加速，兼容分布式 serving。架构核心图。
*caption: Remarkably, similar ideas have also been explored in independent works like Miao et al. (2023); Spector & Re (2023), where they follow a bottom-up app… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.2 (p.2)
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
> [!tip] 【MiniMax 解读】EAGLE-3 加速比柱状图（temp=0）：在 Vicuna-13B/LLaMA-3.1-8B/3.3-70B/DeepSeek-R1-LLaMA-8B 上对比 Vanilla/SpecDec/Medusa/HASS/EAGLE/EAGLE-2/EAGLE-3，EAGLE-3 分别达 5.6x/4.4x/4.1x/5.0x，全面最优。适合做「EAGLE-3 性能优势」论据。
*caption: Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1… ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.2 (p.2)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
> [!tip] 【MiniMax 解读】EAGLE 架构图(Fig.4)：目标 LLM 产出第二顶层特征 f_t 与下一 token t_{t+1}；轻量 draft model 在特征层自回归，输入 f_t + 超前一拍的 t_{t+1}，预测 f_{t+1}，再经 LM head 得 draft token t_{t+2}。「特征+超前 token」消除采样下 f_{t+1} 的不确定性→接受率↑，Vicuna/LLaMA2-70B 上 2.68x。架构核心图。
*caption: Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medu… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### DFlash: Block Diffusion for Flash Speculative Decoding — Fig.2 (p.4)
![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]]
> [!tip] 【MiniMax 解读】DFlash 设计：block-diffusion draft model 块内并行生成多 token（非逐 token 自回归）→低 draft 延迟；目标 LLM 先 prefill 产首 token 并取若干层隐藏态，concat 后过投影层融成 target context feature，注入每个 draft 层的 KV cache 并跨轮复用，持续提供上下文引导→接受长度随 draft 深度增长，无 token-embedding 稀释（优于 EAGLE 式输入融合）。架构核心图。
*caption: DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s… ｜ 论文 [[dflash-block-diffusion-for-flash-speculative-decoding]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.2 (p.3)
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]
> [!tip] 【MiniMax 解读】JetSpec 因果并行草稿头(Fig.3)：轻量 draft head 接冻结目标模型 M_q 中间层融合特征，单次前向并行预测所有 γ 个 draft 位的 top-k 候选→组成 k^γ 候选树；输出重排为广度优先、分支级因果序列再回灌 M_q 验证（满足 tree-SD 左到右依赖）。M_q 冻结只训 head。把草稿成本 c 压到 head 级、接受率 α 保持高→加速随 γ 单调增长，破解 c/α 鱼与熊掌。架构核心图。
*caption: Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Compa… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.2 (p.3)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]]
> [!tip] 【MiniMax 解读】SARATHI chunked-prefill：把 prompt 切成等长 prefill chunk（匹配流水级算力），在途 decode 请求 piggyback 到每个 prefill chunk 上→单次前向混合 prefill+decode token。解耦长 prefill 与 decode 延迟：每个流水级跑统一 hybrid-phase 步、消除 prefill-decode bubble、打满 GPU。更高单卡利用率+decode 吞吐+更大 batch。架构核心图。
*caption: High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V4: Towards Highly Efficient Million-Token Context  — Fig.5 (p.15)
![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
> [!tip] 【MiniMax 解读】DeepSeek-V4 细粒度 EP(Fig.5)：MoE 层拆 Dispatch/Linear-1/Linear-2/Combine 四段。Comet 仅粗粒度重叠 Dispatch↔L1、L2↔Combine；本方案把 expert 再切 wave，一波 dispatch 完即开算、下一波并行 dispatch→稳态下「当前波计算+下一波 token 传输+上一波结果回送」三路并发=连续计算-通信流水。因单层通信<计算，融合成单流水 kernel 藏住互连延迟→低带宽互连也不掉吞吐。架构核心图，与 MoE/EP 相关。
*caption: This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling… ｜ 论文 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.4 (p.8)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
> [!tip] 【MiniMax 解读】Step-3 attention 设计对比(Fig.5)：Decode 计算 vs 内存访问(8K→32K ctx)，对比 DSv3 MLA / Qwen3-MoE GQA / Step-3 MFA，叠 H800/910B/A800/H20 roofline。DSv3 MLA 算术强度512=H800 compute-bound；Qwen3 GQA 强度32=H20 memory-bound；Step-3 MFA 强度128≈910B(175)/A800(156) ridge 点→计算仅 DSv3 1/4、访存仅 Qwen3 1/3，跨硬件都省。⭐直击 910B roofline，与昇腾相关。
*caption: Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.1 (p.2)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]]
> [!tip] 【MiniMax 解读】SGLang 系统架构(Fig.1)：Python 嵌入式前端+高性能 runtime，流式 interpreter 提交原语(extend/gen/fork)异步执行并保留依赖。RadixAttention 用 LRU 基数树缓存 KV，跨请求共享前缀自动复用中间注意力态。Frontiers&Dependencies 跟踪就绪原语+数据依赖→批独立操作、重叠执行藏延迟。DSL+radix-cache+依赖调度统一，比 vLLM/Guidance/LMQL 快至 6.4x。架构核心图。
*caption: System architecture: An interpreter executes language primitives with optimized runtime.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.2 (p.4)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]
> [!tip] 【MiniMax 解读】Mooncake 解耦式 KVCache 服务架构：prefill（compute-bound，注意力二次复杂度）与 decode（memory-bound，自回归批处理）分到独立节点池。核心是 disaggregated KVCache 层，池化 CPU/DRAM/SSD/RDMA 资源→跨节点 cache 复用、减冗余计算；调度器做 early rejection + SLO 准入(TTFT/TBT)+负载均衡。把计算阶段与 KVCache 存储解耦→弹性扩展、严 SLO 下更高吞吐。架构核心图。
*caption: Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the co… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.1 (p.1)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p01.png]]
> [!tip] 【MiniMax 解读】PagedAttention 内存布局(Fig.1)：13B 模型在 A100-40G 上参数占 65%（26GB 常驻）、KV cache >30%（每请求动态）、激活小片。传统系统把每请求 KV 存成单连续张量→内部+外部碎片严重、batch 受限。PagedAttention 借 OS 虚拟内存分页：KV 切成固定块（如 16 token）存非连续物理显存，每请求 block table 映射逻辑→物理（类比页表）；请求间可共享物理块（并行采样/beam search/前缀共享）；碎片仅剩 sub-block 余量（~1 token vs GB 级）→近乎零 KV 浪费、吞吐 2-4x。架构核心图，KV-cache/serving 基石。
*caption: Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.2 (p.5)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]
> [!tip] 【MiniMax 解读】DeFT flash 树注意力(Fig.2)：① Input Metadata（Q + 共享前缀 K0 + 分支 K1/K2 + 树拓扑）载入 SM；② Phase1 QKV 准备(HBM 2TB/s)：KV-Guided Grouping 跨分支复用 K0、Flattened Tree KV Splitting 把树切成均衡组 G0/G1/G2 并行；③ Phase2 注意力计算(Shared Mem 19TB/s)：DeFT kernel 各 split 跑部分注意力 + 树拓扑感知全局归约(A0/A1/A2→Final)，避免跨全分支全局同步。消除共享前缀冗余 KV IO、平衡 SM 负载→内存高效、硬件友好的树结构投机解码注意力。架构核心图。
*caption: Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.1 (p.3)
![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p03.png]]
> [!tip] 【MiniMax 解读】NanoFlow Transformer 流水(Fig.1)：算子分三类——compute-bound（W_O/K/V/up/down/gate 密集投影，跨请求共享权重、大 batch 摊权重载入）、memory-bound（prefill/decode attention，载每请求 KV、小 batch 避压 KV）、network-bound（AllGather/AllReduce，NVLink 同步）。device-stream 级算子融合：沿关键路径重排+协调度，单设备内只跨 CUDA stream 注入 micro-batch 状态→串行依赖转并行，吞吐 1.91x、达理论峰 68.5%。异构 batch 是关键。架构核心图。
*caption: Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### Gated Delta Networks: Improving Mamba2 with Delta Rule — Fig.1 (p.7)
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]
> [!tip] 【MiniMax 解读】Gated DeltaNet 架构(Fig.1)：delta-rule 线性注意力 + 乘性门控(α,β)增联想召回；H1/H2 混合变体把 Gated DeltaNet 与 Mamba2(SSM) + Sliding-Window Attention 交错，融合选择性长程记忆+结构化递归+局部上下文。block 设计：q/k 路径=线性投影+shortconv+SiLU+L2norm，v=线性投影+shortconv+SiLU，α/β=线性投影，输出 gate=线性投影+SiLU。Wiki ppl 16.42、zero-shot 55.32，H2 混合 ppl 15.91 最优。线性注意力/SSM 架构核心图。
*caption: Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.… ｜ 论文 [[gated-delta-networks-improving-mamba2-with-delta-rule]] ｜ arxiv 见 MD 元信息*

### Parallel Scan on Ascend AI Accelerators — Fig.3 (p.3)
![[assets/parallel-scan-on-ascend-ai-accelerators-p03.png]]
> [!tip] 【MiniMax 解读】⭐Ascend 910B AI Core 架构(Fig.3)：单 AI Core = 1 个 AI Cube(AIC 矩阵乘引擎) + 2 个 AI Vector(AIV SIMD 核)，各有独立 Unified Buffer(UB) scratchpad，加 Memory Transfer Engine(MTE)+标量+控制块。AIC/AIV 共享全局 HBM/L2，Cube↔Vector 数据交换须走全局内存/L2（AIC 无直接写 AIV UB 的本地路径）。并行 scan：AIV 跑 element-wise/局部 scan + 解耦 look-back（在 UB 上），AIC 改作跨块前缀累积（矩阵乘式），MTE 编排块级 tile 传输。⭐结论：Ascend 非对称 Cube/Vector 划分 + UB 局部计算 + Cube↔Vector 仅全局通信→偏好 block-tiled、通信最小化的解耦 scan 设计，而非密集 GEMM 中心。直击昇腾线性注意力/SSM scan。
*caption: 1 shows the Ascend architecture where the… ｜ 论文 [[parallel-scan-on-ascend-ai-accelerators]] ｜ arxiv 见 MD 元信息*

## 按主题分类

### architecture (45)

- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p01.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.1 (p.1): ATOP search results on different GPU scales, each point representing a topology.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p03.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.2 (p.3): GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p04.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.3 (p.4): (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs t…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p05.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.4 (p.5): Overview of ATOP allows the system to explore novel topology designs automatical…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p06.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.5 (p.6): Examples of constructing inter-layer and intra-layer connections in ATOP. Unment…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.6 (p.9): During the 4k GPUs search process: (a) The Pareto- optimal topologies generated …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.7 (p.9): (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The se…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p10.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.8 (p.10): (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An exam…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.9 (p.11): The training iteration time for GPT-3 175B and MoE-GPT models and the correspond…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.10 (p.11): CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.11 (p.12): The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.12 (p.12): Collective communication performance on real- world deployment. ZCube and ROFT a…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.13 (p.15): In the search results of Case 3, the comparison between the number of modified l…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.14 (p.15): The search results of ATOP when building a new data center for multi-tenancy.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.15 (p.15): The search results of ATOP when building a new heterogeneous data center with st…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p16.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.16 (p.16): During the ATOP optimization process: (a) The relationship between the number of…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.17 (p.17): Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-bl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.18 (p.17): The average JCT for group all-to-all communica- tion under different topologies …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p18.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.19 (p.18): Comparison between packet-level network simulation (with packet spraying for loa…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p19.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.20 (p.19): Comparison of the CDF of flow completion times between NS-3 and flow-level simul…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.21 (p.20): ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.22 (p.20): Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rai…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.23 (p.20): HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.24 (p.20): ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]] — **Efficient Large-Scale Language Model Training on G** Fig.1 (p.1): Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models wi…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.2 (p.3): Combination of tensor and pipeline model parallelism (MP) used in this work for …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.3 (p.3): GPipe pipeline schedule with forward passes (blue) for all microbatches (represe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.4 (p.3): Default and interleaved 1F1B pipeline schedules. The top figure shows the defaul…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.5 (p.5): Blocks of transformer model partitioned with tensor model parallelism (figures b…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.6 (p.5): Fraction of time spent idling due to pipeline flush (pipeline bubble size) versu…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.7 (p.6): Per-GPU throughput versus microbatch size for a GPT model with a billion paramet…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.8 (p.6): Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]] — **Efficient Large-Scale Language Model Training on G** Fig.9 (p.7): Scatter/gather communication optimization. Light blue blocks are layers in the f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]] — **Efficient Large-Scale Language Model Training on G** Fig.10 (p.8): Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.11 (p.9): Throughput per GPU of pipeline parallelism using two different batch sizes in a …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.12 (p.9): Throughput per GPU of interleaved and non-interleaved schedules for a GPT model …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.13 (p.9): Throughput per GPU of various parallel configurations that combine pipeline and …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.14 (p.10): Throughput per GPU of various parallel configurations that combine data and pipe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.15 (p.10): Throughput per GPU of various parallel configurations that combine data and tens…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.16 (p.10): Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different m…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.17 (p.11): Throughput (in sequences per second) with and without activation recomputation f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.18 (p.11): Throughput per GPU with and without the scatter/gather optimization for a GPT mo…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.1 (p.7): Visualization of the (hybrid) architecture and block design of Gated DeltaNet mo…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`
- ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.2 (p.8): Length extrapolation on six long benchmarks.…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`
- ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.3 (p.9): Training throughput comparison of 1.3B models on a single H100 GPU. standalone m…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`

### disaggregated-serving (66)

- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p01.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.1 (p.1): Example two-stage pipeline parallel schedule. (a)…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.2 (p.3): High-level architecture of a decoder block. sequence length of each request (i.e…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.3 (p.4): Per-token prefill and decode time with different batch sizes (sequence length = …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.4 (p.4): Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.5 (p.5): Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] acros…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.6 (p.6): Example of how attention mask is set across dif- ferent chunk prefill iterations…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.7 (p.7): The effect of tile quantization on the runtime of one iteration of LLaMA-13B on …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.8 (p.9): Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 25…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.9 (p.10): Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequ…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.10 (p.10): Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.11 (p.11): Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. confi…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.12 (p.12): Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p13.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.13 (p.13): Ablation study: Effect of varying the chunk size on different components of the …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p01.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.1 (p.1): Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation tr…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.2 (p.2): Current LLM serving systems involve a tradeoff be- tween throughput and latency …  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.3 (p.5): Throughput of the prefill and decode phases with different batch sizes for Mistr…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.4 (p.5): Prefill and decode time with different input sizes for Mistral-7B running on sin…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.5 (p.6): Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different num…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.6 (p.6): Linear layer execution time as function of number of tokens in a batch for LLaMA…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.7 (p.6): A generation stall occurs when one or more prefills are scheduled in between con…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.8 (p.7): A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p08.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.9 (p.8): The incremental cost of coalescing prefills with decode batches. We consider two…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.10 (p.11): Capacity (in queries per second) of Mistral-7B and…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.11 (p.11): Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.12 (p.12): Latency – Throughput tradeoff in vLLM and…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.13 (p.12): TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross nod…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p13.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.14 (p.13): Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]] — **SGLang: Efficient Execution of Structured Language** Fig.1 (p.2): System architecture: An interpreter executes language primitives with optimized …  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]] — **SGLang: Efficient Execution of Structured Language** Fig.2 (p.3): The implementation of a multi-dimensional essay judge in SGLang utilizes the bra…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]] — **SGLang: Efficient Execution of Structured Language** Fig.3 (p.5): Examples of RadixAttention operations with an LRU eviction policy, illustrated a…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]] — **SGLang: Efficient Execution of Structured Language** Fig.4 (p.6): The decoding process of normal and compressed FSMs (the underscore _ means a spa…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]] — **SGLang: Efficient Execution of Structured Language** Fig.5 (p.7): Normalized throughput on Llama-7B models. Higher is better. pattern: s += contex…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]] — **SGLang: Efficient Execution of Structured Language** Fig.6 (p.8): Normalized latency on Llama-7B models. Lower is better. MMLU…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]] — **SGLang: Efficient Execution of Structured Language** Fig.7 (p.8): Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is …  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]] — **SGLang: Efficient Execution of Structured Language** Fig.8 (p.9): (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]] — **SGLang: Efficient Execution of Structured Language** Fig.9 (p.14): KV cache sharing examples. Blue boxes represent shareable prompt parts, green bo…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]] — **SGLang: Efficient Execution of Structured Language** Fig.10 (p.17): Example of how regex is converted into FSM and how FSM guides the decoding proce…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]] — **SGLang: Efficient Execution of Structured Language** Fig.11 (p.18): Comparison of decoding using Compressed FSM versus normal FSM: The left subfigur…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]] — **SGLang: Efficient Execution of Structured Language** Fig.12 (p.19): Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is b…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]] — **SGLang: Efficient Execution of Structured Language** Fig.13 (p.19): Achieved cache hit rate and optimal cache hit rate on various benchmarks. opport…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]] — **SGLang: Efficient Execution of Structured Language** Fig.14 (p.20): An SGLang program and its corresponding dataflow graph.…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.1 (p.1): Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggre…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.2 (p.2): Impact of disaggregation on supported batch size and number of images per reques…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.3 (p.3): The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migrati…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.4 (p.4): System architecture of the proposed EPD Disaggregated Inference. the data associ…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.5 (p.6): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.6 (p.7): Distribution of TTFT (Y-axis) across varying numbers of images per request (X-ax…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.7 (p.7): SLO attainment (↑) versus request rate on the…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.8 (p.7): As seen, EPD consistently outperforms vLLM and Dist-…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.9 (p.9): As shown, EPD is the only configuration that achieves the SLO requirements, whil…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.10 (p.13): Left: Impact of varying the number of encoding workers in the EPD method. The no…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.11 (p.13): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.12 (p.16): Breakdown of latency for encode and prefill stages using the InternVL2-8B model …  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.1 (p.2): Mooncake Architecture. remote location will prolong the TTFT, and a large batch …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.2 (p.4): Normalized throughput and latency of prefill and decoding stages with different …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.3 (p.5): The KVCache pool in CPU memory. Each block is attached with a hash value determi…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.4 (p.6): Workflow of inference instances. ( ) For prefill instances, the load and store …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.5 (p.6): Input and output length distributions in the request trace. 4…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.6 (p.7): CDF (Cumulative Distribution…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.7 (p.9): Latency of storing KVCache of different request lengths (Layer-wise latency refe…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.8 (p.11): The prefill scheduling experiment in the Mooncake cluster.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.9 (p.13): The load of prefill and decoding instances over 20 minutes, before using the pre…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.10 (p.14): Instance load when applying Early Rejection and Early Rejection Based on Predict…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.11 (p.16): End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eva…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.12 (p.16): End-to-end experiments of Mooncake and vLLM on simulated data.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.13 (p.17): Request TTFT and TBT distributions of Mooncake and vLLM under real workloads…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`

### kv-cache (17)

- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.1 (p.1): Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.2 (p.3): Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning …  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.3 (p.8): Relative speedup of IndexCache over the DSA baseline across three inference sett…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.4 (p.16): Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.1 (p.2): Mooncake Architecture. remote location will prolong the TTFT, and a large batch …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.2 (p.4): Normalized throughput and latency of prefill and decoding stages with different …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.3 (p.5): The KVCache pool in CPU memory. Each block is attached with a hash value determi…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.4 (p.6): Workflow of inference instances. ( ) For prefill instances, the load and store …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.5 (p.6): Input and output length distributions in the request trace. 4…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.6 (p.7): CDF (Cumulative Distribution…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.7 (p.9): Latency of storing KVCache of different request lengths (Layer-wise latency refe…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.8 (p.11): The prefill scheduling experiment in the Mooncake cluster.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.9 (p.13): The load of prefill and decoding instances over 20 minutes, before using the pre…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.10 (p.14): Instance load when applying Early Rejection and Early Rejection Based on Predict…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.11 (p.16): End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eva…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.12 (p.16): End-to-end experiments of Mooncake and vLLM on simulated data.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.13 (p.17): Request TTFT and TBT distributions of Mooncake and vLLM under real workloads…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`

### long-context (2)

- ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p14.png]] — **DeepSeek-V4: Towards Highly Efficient Million-Toke** Fig.1 (p.14): 2.4. Muon Optimizer…  `[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]`
- ⭐ ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]] — **DeepSeek-V4: Towards Highly Efficient Million-Toke** Fig.5 (p.15): This forms a fine-grained pipeline among experts, keeping both computation and c…  `[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]`

### multimodal (42)

- ![[assets/kimi-k2-5-visual-agentic-intelligence-p01.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.1 (p.1): Kimi K2.5 main results. 1…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.2 (p.4): Vision RL training curves on vision benchmarks starting from minimal zero-vision…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p05.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.3 (p.5): An agent swarm has a trainable orchestrator that dynamically creates specialized…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p06.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.4 (p.6): In our parallel-agent reinforcement learning environment, the training accuracy …  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.5 (p.10): Comparison of model performance and token usage for Kimi K2 Thinking following t…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.6 (p.14): The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instan…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.7 (p.14): Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context …  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.8 (p.15): Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent base…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.9 (p.21): Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixe…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.10 (p.23): Overview of our agentic RL framework. environments with minimal overhead. Our de…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.11 (p.28): Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth:…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.12 (p.29): Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 2…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p01.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.1 (p.1): Left: Conventional large multimodal models (LMMs) string all visual tokens into …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.2 (p.4): Architecture of DeepStack. The main innovation lies in the DeepStack strategy th…  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.3 (p.8): Analysis on using LLM layers to process visual tokens. (a) We insert the visual …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.4 (p.10): Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.5 (p.9): Visualization of three sam- pling methods for DeepStack.…  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/kimi-vl-technical-report-p01.png]] — **KIMI-VL TECHNICAL REPORT** Fig.1 (p.1): Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, includin…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p02.png]] — **KIMI-VL TECHNICAL REPORT** Fig.2 (p.2): Highlights of Kimi-VL performance for a wide range of benchmarks like, general b…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p03.png]] — **KIMI-VL TECHNICAL REPORT** Fig.3 (p.3): The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT …  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p04.png]] — **KIMI-VL TECHNICAL REPORT** Fig.4 (p.4): The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-onl…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p06.png]] — **KIMI-VL TECHNICAL REPORT** Fig.5 (p.6): The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages o…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p08.png]] — **KIMI-VL TECHNICAL REPORT** Fig.6 (p.8): Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p12.png]] — **KIMI-VL TECHNICAL REPORT** Fig.7 (p.12): Kimi-VL exhibits strong visual reasoning capabilities by grounding visual conten…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p13.png]] — **KIMI-VL TECHNICAL REPORT** Fig.8 (p.13): Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric …  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p14.png]] — **KIMI-VL TECHNICAL REPORT** Fig.9 (p.14): Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across v…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p15.png]] — **KIMI-VL TECHNICAL REPORT** Fig.10 (p.15): Kimi-VL is capable of following multi-step reasoning processes to complete compl…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p16.png]] — **KIMI-VL TECHNICAL REPORT** Fig.11 (p.16): Video scene splitting. Kimi-VL processes a long-form video by segmenting it into…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p17.png]] — **KIMI-VL TECHNICAL REPORT** Fig.12 (p.17): Catching and understanding key details from an hour-long video course. Kimi-VL d…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p16.png]] — **KIMI-VL TECHNICAL REPORT** Fig.13 (p.16): Specifically, increasing the max thinking token length at inference time consist…  `[[kimi-vl-technical-report]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.1 (p.1): Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggre…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.2 (p.2): Impact of disaggregation on supported batch size and number of images per reques…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.3 (p.3): The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migrati…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.4 (p.4): System architecture of the proposed EPD Disaggregated Inference. the data associ…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.5 (p.6): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.6 (p.7): Distribution of TTFT (Y-axis) across varying numbers of images per request (X-ax…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.7 (p.7): SLO attainment (↑) versus request rate on the…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.8 (p.7): As seen, EPD consistently outperforms vLLM and Dist-…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.9 (p.9): As shown, EPD is the only configuration that achieves the SLO requirements, whil…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.10 (p.13): Left: Impact of varying the number of encoding workers in the EPD method. The no…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.11 (p.13): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.12 (p.16): Breakdown of latency for encode and prefill stages using the InternVL2-8B model …  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`

### rl (73)

- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.1 (p.1): A comparison of learning behavior of the GEPA prompt optimizer against a state-o…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.2 (p.3): This figure shows an example prompt generated by GEPA for the second-hop documen…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.3 (p.5): GEPA proposes a new candidate in every iteration by improving existing candidate…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.4 (p.4): GEPA receives the following inputs: A system  instan- tiated with simple prompt…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.5 (p.7): GEPA’s reflective prompt mutation systematically incorporates task-specific nuan…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.6 (p.10): Comparing the impact of different candidate selection strategies. (Left) As can …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.7 (p.13): GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector ut…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.8 (p.13): GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.9 (p.24): Details of System Aware Merge. r represents a seeded stochastic sampler.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.10 (p.28): Final test set performance for aggregate and individual benchmarks.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.11 (p.28): This figure compares the learning behaviour of GEPA against GRPO with full-param…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.12 (p.29): Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.13 (p.29): IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIP…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.14 (p.29): HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.15 (p.29): PUPA: rollout vs. score for different models/settings. 29…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.16 (p.30): Generalization gaps for different optimization methods. Following Wan et al. (20…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.17 (p.30): These plots visualize the final aggregate scores against the aggregate prompt si…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.18 (p.31): Comparing the token counts of optimized programs across benchmarks. (a) Abl:Sele…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.19 (p.31): HotpotQA GPT-4.1 Mini 31…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.20 (p.32): HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.21 (p.32): IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.22 (p.32): IFBench Qwen3 8B 32…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.23 (p.33): HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.24 (p.33): HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.25 (p.33): PUPA GPT-4.1 Mini 33…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.26 (p.34): PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.27 (p.12): We also note that generation stochasticity (temperature based sampling) is elimi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.1 (p.1): A comparison of learning behavior of the GEPA prompt optimizer against a state-o…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.2 (p.3): This figure shows an example prompt generated by GEPA for the second-hop documen…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.3 (p.5): GEPA proposes a new candidate in every iteration by improving existing candidate…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.4 (p.4): GEPA receives the following inputs: A system  instan- tiated with simple prompt…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.5 (p.7): GEPA’s reflective prompt mutation systematically incorporates task-specific nuan…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.6 (p.10): Comparing the impact of different candidate selection strategies. (Left) As can …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.7 (p.13): GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector ut…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.8 (p.13): GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.9 (p.24): Details of System Aware Merge. r represents a seeded stochastic sampler.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.10 (p.28): Final test set performance for aggregate and individual benchmarks.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.11 (p.28): This figure compares the learning behaviour of GEPA against GRPO with full-param…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.12 (p.29): Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.13 (p.29): IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIP…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.14 (p.29): HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.15 (p.29): PUPA: rollout vs. score for different models/settings. 29…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.16 (p.30): Generalization gaps for different optimization methods. Following Wan et al. (20…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.17 (p.30): These plots visualize the final aggregate scores against the aggregate prompt si…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.18 (p.31): Comparing the token counts of optimized programs across benchmarks. (a) Abl:Sele…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.19 (p.31): HotpotQA GPT-4.1 Mini 31…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.20 (p.32): HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.21 (p.32): IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.22 (p.32): IFBench Qwen3 8B 32…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.23 (p.33): HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.24 (p.33): HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.25 (p.33): PUPA GPT-4.1 Mini 33…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.26 (p.34): PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.27 (p.12): We also note that generation stochasticity (temperature based sampling) is elimi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.1 (p.4): Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.2 (p.9): (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability af…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.3 (p.17): Retrieved Token Loss Masking Study instruction-tuned models exhibit faster conve…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.4 (p.17): Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges fa…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.5 (p.18): Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across fo…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.6 (p.19): The training dynamics of SEARCH-R1 with a different number of retrieved pas- sag…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.7 (p.19): We observe that a larger group size generally leads to faster convergence but ma…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.1 (p.4): Execution timeline of a synchronous (left) and a one-step overlap (right) RL sys…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.2 (p.4): The AREAL architecture featuring asynchronous generation and training components…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.3 (p.4): Illustration of generation management in AREAL. Vertical lines show the ready ti…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p08.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.4 (p.8): The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consi…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.5 (p.9): Ablation studies of the decoupled PPO objective and staleness control with a 1.5…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.6 (p.10): Ablation studies on system optimizations. experimental setup, we configured 32 m…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p06.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.2 (p.6): In the initial stage, we collect thousands of cold-start data that exhibits a co…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.3 (p.14): For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g fro…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.6 (p.35): B.6. Ablation Study of Language Consistency Reward…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.7 (p.37): As can be seen, without the LC reward, language consistency gradually deteriorat…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.13 (p.48): We have categorized potential content safety challenges faced by language models…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.14 (p.53): For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and …  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`

### sparse-attention (4)

- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.1 (p.1): Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.2 (p.3): Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning …  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.3 (p.8): Relative speedup of IndexCache over the DSA baseline across three inference sett…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.4 (p.16): Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`

### speculative (66)

- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p02.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.1 (p.2): MEDUSA introduces multiple heads on top of the last hidden states of the LLM, en…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p03.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.2 (p.3): Remarkably, similar ideas have also been explored in independent works like Miao…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p07.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.3 (p.7): Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDU…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p08.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.4 (p.8): Effectiveness of numbers of candidate tokens for decoding introduced by trees (d…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p05.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.5 (p.5): 5…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.6 (p.15): Visualization of a sparse tree setting for MEDUSA-2 Vicuna-7B. The tree has 64 n…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.7 (p.15): Inference speed of various models using speculative decoding on MT-Bench. Baseli…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p16.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.8 (p.16): Speedup of various models with MEDUSA-2. MEDUSA-2 shows significant speed improv…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.9 (p.18): The figure shows the relationship between FLOP/s and Operational Intensity for a…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.10 (p.18): Llama-13B operators on A100-80GB-PCIe. 18…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.11 (p.19): Llama-33B operators on A100-80GB-PCIe. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.12 (p.19): Llama-7B operators on A40. 19…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.13 (p.20): Llama-13B operators on A40. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.14 (p.20): Llama-33B operators on A40. 20…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.15 (p.21): Llama-7B operators on A6000. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.16 (p.21): Llama-13B operators on A6000. 21…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p22.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.17 (p.22): Llama-33B operators on A6000. 22…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p23.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.18 (p.23): FLOP/s vs. Operational Intensity of attention matrix multiplication with batch s…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.19 (p.24): FLOP/s vs. Operational Intensity of attention matrix multiplication with sequenc…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.20 (p.24): FLOP/s vs. Operational Intensity of Linear layers. 24…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p26.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.21 (p.26): Simulated acceleration rate, speedup, and normalized latency ablation using diff…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.22 (p.27): Simulated speedup with sequence length 1024 for Llama-7B. 1 16 32 48 64 80 96 11…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.23 (p.27): Simulated speedup with batch size 4 for Llama-7B. 27…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.1 (p.1): Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target …  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For the standard speculati…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.3 (p.3): Illustration of training-time test (the bottom part) and its comparison with oth…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.4 (p.2): We can address this issue by incorporating Step 1 into the training process (the…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.5 (p.4): Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the d…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.6 (p.5): All attention masks are diagonal, except when the original training data is used…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.7 (p.8): Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LL…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p01.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.1 (p.1): Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for gr…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.2 (p.2): Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.3 (p.2): Uncertainty in feature sequences. The next fea- ture following fI is contingent …  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.4 (p.3): Accuracy and speedup ratio of draft models based on tokens, features and feature…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.5 (p.4): A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5.…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.6 (p.4): Pipeline of EAGLE. The upper section illustrates the computational process, whil…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.7 (p.7): Speedup ratios of EAGLE with and without the use of tree attention. The evaluati…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p08.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.8 (p.8): Performance of draft models with varying inputs. The target LLM is Vicuna 7B, an…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p12.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.9 (p.12): However, the optimal tree structure is likely context-dependent. For instance, a…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p01.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.1 (p.1): Speedup ratios of different methods at tempera- ture=1. For speculative sampling…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For speculative sampling, …  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.3 (p.3): Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s t…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.4 (p.3): Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. …  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.5 (p.3): Overall, the acceptance rate of draft tokens is position-dependent, with the hig…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.6 (p.4): Average acceptance rates for different confidence score intervals of the draft m…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.7 (p.5): Illustration of EAGLE-2. The numbers beside the edges represent the confidence s…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.1 (p.2): Block diffusion sequentially generates blocks of tokens by performing diffusion …  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.2 (p.6): Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on …  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.3 (p.21): x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.4 (p.22): We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible spar…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.5 (p.23): Attention computation using FlexAttention with our proposed custom mask.…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.6 (p.26): Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion s…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.7 (p.27): Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffus…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.8 (p.28): Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p02.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.1 (p.2): Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qw…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ⭐ ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.2 (p.4): DFlash Inference Design. Hidden context features extracted from the target model…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.3 (p.3): Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.4 (p.5): DFlash training attention. The target model provides context features (blue) tha…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.5 (p.13): The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-p04.png]] — **DSpark: Confidence-Scheduled Speculative Decoding ** Fig.1 (p.4): Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= …  `[[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.1 (p.2): End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs a…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.2 (p.3): Expected speculative decoding speedup scales as a function of draft length γ, un…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.3 (p.4): JetSpec design overview. JetSpec extracts fused hidden features from the frozen …  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.4 (p.15): Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.5 (p.18): Figure 5: Causal attention mask used for training with multiple sampled blocks. …  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.6 (p.19): Each sampled block includes an anchor position and multiple future token positio…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`

### training (62)

- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.1 (p.1): Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target …  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For the standard speculati…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.3 (p.3): Illustration of training-time test (the bottom part) and its comparison with oth…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.4 (p.2): We can address this issue by incorporating Step 1 into the training process (the…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.5 (p.4): Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the d…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.6 (p.5): All attention masks are diagonal, except when the original training data is used…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.7 (p.8): Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LL…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p01.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.1 (p.1): ATOP search results on different GPU scales, each point representing a topology.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p03.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.2 (p.3): GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p04.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.3 (p.4): (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs t…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p05.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.4 (p.5): Overview of ATOP allows the system to explore novel topology designs automatical…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p06.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.5 (p.6): Examples of constructing inter-layer and intra-layer connections in ATOP. Unment…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.6 (p.9): During the 4k GPUs search process: (a) The Pareto- optimal topologies generated …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.7 (p.9): (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The se…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p10.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.8 (p.10): (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An exam…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.9 (p.11): The training iteration time for GPT-3 175B and MoE-GPT models and the correspond…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.10 (p.11): CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.11 (p.12): The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.12 (p.12): Collective communication performance on real- world deployment. ZCube and ROFT a…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.13 (p.15): In the search results of Case 3, the comparison between the number of modified l…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.14 (p.15): The search results of ATOP when building a new data center for multi-tenancy.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.15 (p.15): The search results of ATOP when building a new heterogeneous data center with st…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p16.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.16 (p.16): During the ATOP optimization process: (a) The relationship between the number of…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.17 (p.17): Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-bl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.18 (p.17): The average JCT for group all-to-all communica- tion under different topologies …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p18.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.19 (p.18): Comparison between packet-level network simulation (with packet spraying for loa…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p19.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.20 (p.19): Comparison of the CDF of flow completion times between NS-3 and flow-level simul…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.21 (p.20): ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.22 (p.20): Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rai…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.23 (p.20): HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.24 (p.20): ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.1 (p.4): Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.2 (p.9): (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability af…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.3 (p.17): Retrieved Token Loss Masking Study instruction-tuned models exhibit faster conve…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.4 (p.17): Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges fa…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.5 (p.18): Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across fo…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.6 (p.19): The training dynamics of SEARCH-R1 with a different number of retrieved pas- sag…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.7 (p.19): We observe that a larger group size generally leads to faster convergence but ma…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p01.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.1 (p.1): Overview of conversion from multi-head to multi-query attention. Key and value p…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p02.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.2 (p.2): Overview of grouped-query method. Multi-head attention has H query, key, and val…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p03.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.3 (p.3): Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality an…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.4 (p.4): Performance comparison of different check- point conversion methods for T5-Large…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.5 (p.4): Performance as a function of uptraining pro- portion for T5 XXL models with MQA …  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.6 (p.4): Time per sample for GQA-XXL as a function of the number of GQA groups with input…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]] — **Efficient Large-Scale Language Model Training on G** Fig.1 (p.1): Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models wi…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.2 (p.3): Combination of tensor and pipeline model parallelism (MP) used in this work for …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.3 (p.3): GPipe pipeline schedule with forward passes (blue) for all microbatches (represe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.4 (p.3): Default and interleaved 1F1B pipeline schedules. The top figure shows the defaul…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.5 (p.5): Blocks of transformer model partitioned with tensor model parallelism (figures b…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.6 (p.5): Fraction of time spent idling due to pipeline flush (pipeline bubble size) versu…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.7 (p.6): Per-GPU throughput versus microbatch size for a GPT model with a billion paramet…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.8 (p.6): Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]] — **Efficient Large-Scale Language Model Training on G** Fig.9 (p.7): Scatter/gather communication optimization. Light blue blocks are layers in the f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]] — **Efficient Large-Scale Language Model Training on G** Fig.10 (p.8): Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.11 (p.9): Throughput per GPU of pipeline parallelism using two different batch sizes in a …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.12 (p.9): Throughput per GPU of interleaved and non-interleaved schedules for a GPT model …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.13 (p.9): Throughput per GPU of various parallel configurations that combine pipeline and …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.14 (p.10): Throughput per GPU of various parallel configurations that combine data and pipe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.15 (p.10): Throughput per GPU of various parallel configurations that combine data and tens…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.16 (p.10): Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different m…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.17 (p.11): Throughput (in sequences per second) with and without activation recomputation f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.18 (p.11): Throughput per GPU with and without the scatter/gather optimization for a GPT mo…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`

## 按论文

### #1 IndexCache: Accelerating Sparse Attention via Cross-Layer In

- Fig.1 (p.1) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]]
  - Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50% of indexer computations while maintaining comparable performance across both long-context and reasoning tasks, deliver
- ⭐ Fig.2 (p.3) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
  - Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branch (red lines): F layers compute and cache fresh in
- Fig.3 (p.8) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]]
  - Relative speedup of IndexCache over the DSA baseline across three inference settings on the 30B model. DSA baseline is normalized to 100%.
- Fig.4 (p.16) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]]
  - Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.

### #2 MEDUSA: Simple LLM Inference Acceleration Framework with Mul

- Fig.1 (p.2) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p02.png]]
  - MEDUSA introduces multiple heads on top of the last hidden states of the LLM, enabling the prediction of several sub- sequent tokens in parallel (Section 2.1.1). During inference, each head generates 
- ⭐ Fig.2 (p.3) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p03.png]]
  - Remarkably, similar ideas have also been explored in independent works like Miao et al. (2023); Spector & Re (2023), where they follow a bottom-up approach and construct the tree by merging mul- tiple
- Fig.3 (p.7) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p07.png]]
  - Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDUSA-1 achieves more than 2× wall-time speedup compared to the baseline implementation while MEDUSA-2 further improves the
- Fig.4 (p.8) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p08.png]]
  - Effectiveness of numbers of candidate tokens for decoding introduced by trees (default number of candidate token for decoding is 1 when using KV cache). Left: The acceleration rate for randomly sample
- Fig.5 (p.5) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p05.png]]
  - 5
- Fig.6 (p.15) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]]
  - Visualization of a sparse tree setting for MEDUSA-2 Vicuna-7B. The tree has 64 nodes representing candidate tokens and a depth of 4 which indicates 4 MEDUSA heads involved in calculation. Each node in
- Fig.7 (p.15) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]]
  - Inference speed of various models using speculative decoding on MT-Bench. Baseline model speeds are presented by grey dotted lines for comparison. γ denotes the draft token number. E. Additional Resul
- Fig.8 (p.16) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p16.png]]
  - Speedup of various models with MEDUSA-2. MEDUSA-2 shows significant speed improvement over all the models, while models trained with self-distillation (Zephyr-7B, Vicuna-13/33B) have weaker speedup du
- Fig.9 (p.18) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]]
  - The figure shows the relationship between FLOP/s and Operational Intensity for all benchmarked datapoints of Llama-7B operators on A100-80GB-PCIe. The dashed lines represent the HBM bandwidth limit (1
- Fig.10 (p.18) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]]
  - Llama-13B operators on A100-80GB-PCIe. 18
- Fig.11 (p.19) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]]
  - Llama-33B operators on A100-80GB-PCIe. 1 10 100 1k 10k
- Fig.12 (p.19) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]]
  - Llama-7B operators on A40. 19
- Fig.13 (p.20) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]]
  - Llama-13B operators on A40. 1 10 100 1k 10k
- Fig.14 (p.20) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]]
  - Llama-33B operators on A40. 20
- Fig.15 (p.21) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]]
  - Llama-7B operators on A6000. 1 10 100 1k 10k
- Fig.16 (p.21) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]]
  - Llama-13B operators on A6000. 21
- Fig.17 (p.22) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p22.png]]
  - Llama-33B operators on A6000. 22
- Fig.18 (p.23) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p23.png]]
  - FLOP/s vs. Operational Intensity of attention matrix multiplication with batch size 16. 23
- Fig.19 (p.24) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]]
  - FLOP/s vs. Operational Intensity of attention matrix multiplication with sequence length 1024. 1 10 100 1k 10k
- Fig.20 (p.24) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]]
  - FLOP/s vs. Operational Intensity of Linear layers. 24
- Fig.21 (p.26) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p26.png]]
  - Simulated acceleration rate, speedup, and normalized latency ablation using different numbers of candidate tokens under the setting of batch size 1 and sequence length 1024 for Llama-7B on an A100 80G
- Fig.22 (p.27) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]]
  - Simulated speedup with sequence length 1024 for Llama-7B. 1 16 32 48 64 80 96 112
- Fig.23 (p.27) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]]
  - Simulated speedup with batch size 4 for Llama-7B. 27

### #3 EAGLE-3: Scaling up Inference Acceleration of Large Language

- Fig.1 (p.1) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]]
  - Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGPT.
- ⭐ Fig.2 (p.2) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
  - Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1, we present comparisons with additional methods, 
- Fig.3 (p.3) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]]
  - Illustration of training-time test (the bottom part) and its comparison with other draft methods (the upper and middle parts). f denotes the feature, t denotes the token, and a represents the unconstr
- ⭐ Fig.4 (p.2) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
  - We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing training data become more pronounced. We name this t
- Fig.5 (p.4) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]]
  - Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level features of the target model, respectively. e denotes 
- Fig.6 (p.5) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]]
  - All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in significant computational waste, so we can use vec
- Fig.7 (p.8) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]]
  - Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-

### #4 EAGLE: Speculative Sampling Requires Rethinking Feature Unce

- Fig.1 (p.1) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p01.png]]
  - Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead are copied from their original technical reports. W
- ⭐ Fig.2 (p.2) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
  - Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medusa does not guarantee lossless performance. Theref
- ⭐ Fig.3 (p.2) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
  - Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, where both “always” and “am” are possible to follow
- Fig.4 (p.3) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]]
  - Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers t
- Fig.5 (p.4) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
  - A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) signifies the features, with subscripts indicating
- Fig.6 (p.4) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
  - Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, green blocks repr
- Fig.7 (p.7) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]]
  - Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.
- Fig.8 (p.8) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p08.png]]
  - Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench.
- Fig.9 (p.12) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p12.png]]
  - However, the optimal tree structure is likely context-dependent. For instance, as batch size increases and redundant computational resources decrease, a smaller tree might be preferable. Tuning the dr

### #5 EAGLE-2: Faster Inference of Language Models with Dynamic Dr

- Fig.1 (p.1) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p01.png]]
  - Speedup ratios of different methods at tempera- ture=1. For speculative sampling, the Vicuna series uses
- Fig.2 (p.2) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]]
  - Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft m
- Fig.3 (p.3) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
  - Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-
- Fig.4 (p.3) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
  - Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correctly pre- dicted as “1”. However, with a static draf
- Fig.5 (p.3) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
  - Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Draft tokens in the upper left side of the draft tree
- Fig.6 (p.4) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]]
  - Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual assessment. The original LLM is Vicuna 7B. aspects: 
- Fig.7 (p.5) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]]
  - Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the exp

### #6 BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI

- Fig.1 (p.2) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]]
  - Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining strength from autoregressive and diffusion models, b
- Fig.2 (p.6) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]]
  - Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has 
- Fig.3 (p.21) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]]
  - x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3
- Fig.4 (p.22) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]]
  - We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly 
- Fig.5 (p.23) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]]
  - Attention computation using FlexAttention with our proposed custom mask.
- Fig.6 (p.26) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]
  - Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.
- Fig.7 (p.27) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]
  - Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3
- Fig.8 (p.28) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]
  - Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5

### #7 DFlash: Block Diffusion for Flash Speculative Decoding

- Fig.1 (p.2) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p02.png]]
  - Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the
- ⭐ Fig.2 (p.4) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]]
  - DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s
- Fig.3 (p.3) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]]
  - Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.
- Fig.4 (p.5) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]]
  - DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens p and clean response tokens r.
- Fig.5 (p.13) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]]
  - The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING OF MASKED BLOCKS

### #8 DSpark: Confidence-Scheduled Speculative Decoding with Semi-

- Fig.1 (p.4) ![[assets/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-p04.png]]
  - Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= (𝑇draft + 𝑇verify)/𝜏. Autoregressive drafters achieve high 𝜏but pay 𝑇draft ∝𝛾; parallel drafters collapse 𝑇draft to a si

### #9 JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin

- Fig.1 (p.2) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]]
  - End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original block-parallel drafting method, DDTree is tree-base
- ⭐ Fig.2 (p.3) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]
  - Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substant
- Fig.3 (p.4) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]]
  - JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.
- Fig.4 (p.15) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]]
  - Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 branch (“ are told that”) is faithful: target joint Σ 
- Fig.5 (p.18) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]]
  - Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but can
- Fig.6 (p.19) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]]
  - Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token posit

### #10 From ATOP to ZCube: Automated Topology Optimization Pipeline

- Fig.1 (p.1) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p01.png]]
  - ATOP search results on different GPU scales, each point representing a topology. For each scale, we label the three notable points in each plot: Best performance, Most
- Fig.2 (p.3) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p03.png]]
  - GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excluding TP communication as it typically occurs on the intra-server network. • Expert parallelism (EP), used in mixture-of
- Fig.3 (p.4) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p04.png]]
  - (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs topology. (b) The performance degradation of GPT-3 training after a Single ToR Fault in a 4k-GPUs topology. ZCube and Bes
- Fig.4 (p.5) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p05.png]]
  - Overview of ATOP allows the system to explore novel topology designs automatically, not limited to variants or combinations of existing ones. It can produce high-performance asymmetric topologies, suc
- Fig.5 (p.6) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p06.png]]
  - Examples of constructing inter-layer and intra-layer connections in ATOP. Unmentioned hyperparameters = 0.
- Fig.6 (p.9) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]]
  - During the 4k GPUs search process: (a) The Pareto- optimal topologies generated by ATOP; (b) All the topologies generated by ATOP.
- Fig.7 (p.9) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]]
  - (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The search results when expanding a DCN from 1k GPUs to 4k GPUs. be unfair to other topologies. However, in Case 3, even expan
- Fig.8 (p.10) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p10.png]]
  - (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An example of ZCube(2, 3). (c) An example of ZCube(84,3)-partial. ZCube(𝑛,𝑘+ 1) is equipped with (𝑘+ 1) NIC ports numbered from
- Fig.9 (p.11) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]]
  - The training iteration time for GPT-3 175B and MoE-GPT models and the corresponding network costs on various topologies, under different numbers of GPUs.
- Fig.10 (p.11) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]]
  - CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 GPUs. GPU clusters, the failure probability of a single switch is 0.03%.
- Fig.11 (p.12) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]]
  - The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G 4G 16G
- Fig.12 (p.12) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]]
  - Collective communication performance on real- world deployment. ZCube and ROFT achieve the same all-reduce and all-to-all perfor- mance, while ZCube reduces hardware cost by 25% by using only 48×200G 
- Fig.13 (p.15) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]
  - In the search results of Case 3, the comparison between the number of modified links (another cost metric) and training performance.
- Fig.14 (p.15) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]
  - The search results of ATOP when building a new data center for multi-tenancy.
- Fig.15 (p.15) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]
  - The search results of ATOP when building a new heterogeneous data center with strict search space con- straints.
- Fig.16 (p.16) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p16.png]]
  - During the ATOP optimization process: (a) The relationship between the number of Pareto-optimal topologies and the total number of topologies generated by ATOP; (b) The Jaccard distance between the Pa
- Fig.17 (p.17) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]]
  - Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-blocking 2-layer Rail-Optimized
- Fig.18 (p.17) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]]
  - The average JCT for group all-to-all communica- tion under different topologies with link failures on 4096 GPUs, with shading representing the standard deviation of the JCT.
- Fig.19 (p.18) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p18.png]]
  - Comparison between packet-level network simulation (with packet spraying for load balancing) and the real-world testbed in §6.2. I
- Fig.20 (p.19) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p19.png]]
  - Comparison of the CDF of flow completion times between NS-3 and flow-level simulators.
- Fig.21 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.
- Fig.22 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].
- Fig.23 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.
- Fig.24 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880

### #11 KIMI K2.5: VISUAL AGENTIC INTELLIGENCE

- Fig.1 (p.1) ![[assets/kimi-k2-5-visual-agentic-intelligence-p01.png]]
  - Kimi K2.5 main results. 1
- Fig.2 (p.4) ![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]]
  - Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired
- Fig.3 (p.5) ![[assets/kimi-k2-5-visual-agentic-intelligence-p05.png]]
  - An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable subtasks for efficient distributed execution.
- Fig.4 (p.6) ![[assets/kimi-k2-5-visual-agentic-intelligence-p06.png]]
  - In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as train- ing progresses. At the same time, the level of parallelism during training also gradually i
- Fig.5 (p.10) ![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]]
  - Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not fundamentally resolve the load imbalance caused by
- Fig.6 (p.14) ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]
  - The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the
- Fig.7 (p.14) ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]
  - Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.9%). Similarly, WideSearch sees a 6.3% improvement
- Fig.8 (p.15) ![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]]
  - Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testing. rather than context truncation, allowing the sy
- Fig.9 (p.21) ![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]]
  - Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixed vision-text token budget across vision and language tasks. Early fusion with lower vision ratios tend to yield better 
- Fig.10 (p.23) ![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]]
  - Overview of our agentic RL framework. environments with minimal overhead. Our design prioritizes compositional modularity by integrating a suite of plug- gable components, such as a Tolset module for 
- Fig.11 (p.28) ![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]]
  - Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth: Wukong (24 hours of continuous gameplay across 32 videos at 1080p) using parallel visual agents. See generated webpage 
- Fig.12 (p.29) ![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]]
  - Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 29

### #14 DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim

- Fig.1 (p.1) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p01.png]]
  - Left: Conventional large multimodal models (LMMs) string all visual tokens into a sequence for high- and low-resolution images. Middle: Our DeepStack LMMs stack the tokens into a grid and infuse them 
- Fig.2 (p.4) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]]
  - Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LLMs. Given an input image, we feed the tokens extra
- Fig.3 (p.8) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]]
  - Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first l
- Fig.4 (p.10) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]]
  - Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.
- Fig.5 (p.9) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]]
  - Visualization of three sam- pling methods for DeepStack.

### #16 GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM

- Fig.1 (p.1) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]]
  - A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can
- Fig.2 (p.3) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]]
  - This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix 
- Fig.3 (p.5) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]]
  - GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first e
- Fig.4 (p.4) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]]
  - GEPA receives the following inputs: A system  instan- tiated with simple prompts to be optimized, training dataset D train (consisting of task instances (x; m) as described in Section 2), the standar
- Fig.5 (p.7) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]]
  - GEPA’s reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEP
- Fig.6 (p.10) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]]
  - Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration led to a local-optima after one iteration, leading t
- Fig.7 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequ
- Fig.8 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast p vs. rollouts plot for p=[0:5; 1], where the speedup is calculated over Pytorch-eager. fast p is a m
- Fig.9 (p.24) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]]
  - Details of System Aware Merge. r represents a seeded stochastic sampler.
- Fig.10 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - Final test set performance for aggregate and individual benchmarks.
- Fig.11 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetun- ing on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against G
- Fig.12 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO 0 50 10 150 20 250
- Fig.13 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.14 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.15 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - PUPA: rollout vs. score for different models/settings. 29
- Fig.16 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved 
- Fig.17 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently pro- 
- Fig.18 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - Comparing the token counts of optimized programs across benchmarks. (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.19 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - HotpotQA GPT-4.1 Mini 31
- Fig.20 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.21 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)
- Fig.22 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench Qwen3 8B 32
- Fig.23 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.24 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.25 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - PUPA GPT-4.1 Mini 33
- Fig.26 (p.34) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]]
  - PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA
- Fig.27 (p.12) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]]
  - We also note that generation stochasticity (temperature based sampling) is eliminated by operating under a cache; this ensures that ob- served improvements tie closely to inference scaling through pro

### #17 SARATHI: Efficient LLM Inference by Piggybacking Decodes wit

- Fig.1 (p.1) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p01.png]]
  - Example two-stage pipeline parallel schedule. (a)
- ⭐ Fig.2 (p.3) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]]
  - High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’s embedding size (e.g., 5120 for LLaMA-13B).
- Fig.3 (p.4) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
  - Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant p
- Fig.4 (p.4) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
  - Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU. operations. Figure 4b shows the arithmetic intensity of each operation separatel
- Fig.5 (p.5) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]]
  - Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. set of layers; 
- Fig.6 (p.6) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]]
  - Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively). The attention mask for v (“values") is set simil
- Fig.7 (p.7) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]]
  - The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com- putes prefill and decode iterations separately. W
- Fig.8 (p.9) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]]
  - Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).
- Fig.9 (p.10) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
  - Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequence lengths, P:D ratios, and chunk sizes. 2 4 6 8 10 12 14 16 18
- Fig.10 (p.10) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
  - Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orang
- Fig.11 (p.11) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]]
  - Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of varying batch sizes. Further, for each run, we also sh
- Fig.12 (p.12) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]]
  - Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of variable sequence lengths on request latencies.
- Fig.13 (p.13) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p13.png]]
  - Ablation study: Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU. measure the time to compute the prefill phase for various se- quence lengths using th

### #18 Taming Throughput-Latency Tradeoff in LLM Inference with Sar

- Fig.1 (p.1) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p01.png]]
  - Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation trace. 1a highlights one of the many generation stalls lasting over several seconds in vLLM [53]. 1b shows the impact of i
- Fig.2 (p.2) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]]
  - Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens
- Fig.3 (p.5) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]
  - Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that diff
- Fig.4 (p.5) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]
  - Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arit
- Fig.5 (p.6) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
  - Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different number of token running on four A100s. Decode batches have low arithmetic intensity i.e., they are bottlenecked by memory f
- Fig.6 (p.6) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
  - Linear layer execution time as function of number of tokens in a batch for LLaMA2-70B on A100(s) with different tensor parallel degrees. When the number of tokens is small, execution time is dictated 
- Fig.7 (p.6) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
  - A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Sub- script d represents a decode i
- Fig.8 (p.7) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]]
  - A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times.
- Fig.9 (p.8) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p08.png]]
  - The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode +
- Fig.10 (p.11) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]
  - Capacity (in queries per second) of Mistral-7B and
- Fig.11 (p.11) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]
  - Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency SLOs.
- Fig.12 (p.12) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]
  - Latency – Throughput tradeoff in vLLM and
- Fig.13 (p.12) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]
  - TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under str
- Fig.14 (p.13) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p13.png]]
  - Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.

### #19 GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM REINFORCEME

- Fig.1 (p.1) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]]
  - A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can
- Fig.2 (p.3) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]]
  - This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix 
- Fig.3 (p.5) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]]
  - GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first e
- Fig.4 (p.4) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]]
  - GEPA receives the following inputs: A system  instan- tiated with simple prompts to be optimized, training dataset D train (consisting of task instances (x; m) as described in Section 2), the standar
- Fig.5 (p.7) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]]
  - GEPA’s reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEP
- Fig.6 (p.10) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]]
  - Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration led to a local-optima after one iteration, leading t
- Fig.7 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequ
- Fig.8 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast p vs. rollouts plot for p=[0:5; 1], where the speedup is calculated over Pytorch-eager. fast p is a m
- Fig.9 (p.24) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]]
  - Details of System Aware Merge. r represents a seeded stochastic sampler.
- Fig.10 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - Final test set performance for aggregate and individual benchmarks.
- Fig.11 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetun- ing on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against G
- Fig.12 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO 0 50 10 150 20 250
- Fig.13 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.14 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.15 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - PUPA: rollout vs. score for different models/settings. 29
- Fig.16 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved 
- Fig.17 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently pro- 
- Fig.18 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - Comparing the token counts of optimized programs across benchmarks. (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.19 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - HotpotQA GPT-4.1 Mini 31
- Fig.20 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.21 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)
- Fig.22 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench Qwen3 8B 32
- Fig.23 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.24 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.25 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - PUPA GPT-4.1 Mini 33
- Fig.26 (p.34) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]]
  - PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA
- Fig.27 (p.12) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]]
  - We also note that generation stochasticity (temperature based sampling) is eliminated by operating under a cache; this ensures that ob- served improvements tie closely to inference scaling through pro

### #20 DeepSeek-V4: Towards Highly Efficient Million-Token Context 

- Fig.1 (p.14) ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p14.png]]
  - 2.4. Muon Optimizer
- ⭐ Fig.5 (p.15) ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
  - This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling speeds up the 15

### #21 KIMI-VL TECHNICAL REPORT

- Fig.1 (p.1) ![[assets/kimi-vl-technical-report-p01.png]]
  - Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, including short-thinking VLMs (e.g. Gemma-3 series, Qwen2.5-VL series) and long-thinking VLMs (QVQ-72B/Max-Preview), on MathVisi
- Fig.2 (p.2) ![[assets/kimi-vl-technical-report-p02.png]]
  - Highlights of Kimi-VL performance for a wide range of benchmarks like, general benchmarks (MMMU, MMBench), OCR (InfoVQA), multi-image (BLINK), long video (LongVideoBench, Video-MME), long document (MM
- Fig.3 (p.3) ![[assets/kimi-vl-technical-report-p03.png]]
  - The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT that allows native- resolution images, an MLP projector, and a Mixture-of-Experts (MoE) language decoder. 1) Kimi-VL is 
- Fig.4 (p.4) ![[assets/kimi-vl-technical-report-p04.png]]
  - The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-only pre-training of its language model. To preserve text abilities, all stages that update the language model are joint tr
- Fig.5 (p.6) ![[assets/kimi-vl-technical-report-p06.png]]
  - The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages of joint SFT in 32K and 128K context, and further long-CoT SFT and RL stages to activate and enhance long thinking abilit
- Fig.6 (p.8) ![[assets/kimi-vl-technical-report-p08.png]]
  - Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to perform historical and scientific inference by analyzing handwritten manuscripts step by step. In this example, our mod
- Fig.7 (p.12) ![[assets/kimi-vl-technical-report-p12.png]]
  - Kimi-VL exhibits strong visual reasoning capabilities by grounding visual content in spatial, contextual, and cultural knowledge. It accurately identifies matching urban locations based on structural 
- Fig.8 (p.13) ![[assets/kimi-vl-technical-report-p13.png]]
  - Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric inference by solving a circle geometry problem step by step. The model analyzes given conditions, applies geometric theo
- Fig.9 (p.14) ![[assets/kimi-vl-technical-report-p14.png]]
  - Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across varied content types, including structured financial tables, complex mathematical formulas, and handwritten Chinese text.
- Fig.10 (p.15) ![[assets/kimi-vl-technical-report-p15.png]]
  - Kimi-VL is capable of following multi-step reasoning processes to complete complex GUI tasks. In this example, it successfully enables the “Do Not Track” feature in the Chrome browser to enhance onlin
- Fig.11 (p.16) ![[assets/kimi-vl-technical-report-p16.png]]
  - Video scene splitting. Kimi-VL processes a long-form video by segmenting it into coherent scenes and providing detailed start/end timestamps along with fine-grained natural language descriptions for e
- Fig.12 (p.17) ![[assets/kimi-vl-technical-report-p17.png]]
  - Catching and understanding key details from an hour-long video course. Kimi-VL demonstrates its ability to comprehend and interpret instructional video content by analyzing frame sequences and extract
- Fig.13 (p.16) ![[assets/kimi-vl-technical-report-p16.png]]
  - Specifically, increasing the max thinking token length at inference time consistently improves test-time accuracy across all three 16

### #23 High-Dimensional Continuous Control Using Generalized Advant

- Fig.1 (p.8) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p08.png]]
  - 6.2.1 ARCHITECTURE
- Fig.2 (p.10) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]
  - Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range
- Fig.3 (p.10) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]
  - Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algo- rithm. Right: learning curves for 3D quadrupedal locomotion, averaged across ﬁve runs.
- Fig.4 (p.11) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p11.png]]
  - (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up. 7 DISCUSSION

### #24 KIMI K2: OPEN AGENTIC INTELLIGENCE

- Fig.1 (p.1) ![[assets/kimi-k2-open-agentic-intelligence-p01.png]]
  - Kimi K2 main results.2 1https://huggingface.co/moonshotai/Kimi-K2-Instruct 2All models evaluated above are non-thinking models. For SWE-bench Multilingual, we evaluated only Claude 4 Sonnet because th
- Fig.2 (p.4) ![[assets/kimi-k2-open-agentic-intelligence-p04.png]]
  - Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training divergence. Right: Maximum logits for Kimi K2 with 
- Fig.3 (p.5) ![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
  - Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity. A k
- Fig.4 (p.5) ![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
  - • Fidelity verification: To ensure consistency between original and rewritten content, we perform fidelity checks that compare the semantic alignment of each rephrased passage with its source. This se
- Fig.5 (p.7) ![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
  - Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of exper
- Fig.6 (p.7) ![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
  - Scaling curves for models with number of atten- tion heads equals to number of layers and their counter- parts with doubled attention heads. Doubling the number of attention heads leads to a reduction
- Fig.7 (p.8) ![[assets/kimi-k2-open-agentic-intelligence-p08.png]]
  - Computation, communication and offloading overlapped in different PP phases.
- Fig.8 (p.10) ![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
  - Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter tra
- Fig.9 (p.10) ![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
  - t-SNE visualizations of tool embeddings. (a) Real-world MCP tools exhibit natural clustering based on their original source categories. (b) Synthetic tools are organized into pre-defined domain catego
- Fig.10 (p.14) ![[assets/kimi-k2-open-agentic-intelligence-p14.png]]
  - Parameter update utilizing a checkpoint engine
- Fig.11 (p.29) ![[assets/kimi-k2-open-agentic-intelligence-p29.png]]
  - Chinese in-house benchmark evaluation. rate, i.e. 98.9. On FaithJudge’s RAG tasks the hallucination rate is 7.4 %, likewise present as 92.6 for table consistency.
- Fig.12 (p.30) ![[assets/kimi-k2-open-agentic-intelligence-p30.png]]
  - Applying QK-Clip to Muon in a small-scale setting with an aggresive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logit
- Fig.13 (p.32) ![[assets/kimi-k2-open-agentic-intelligence-p32.png]]
  - pipeline for RL weight update

### #25 Search-R1: Training LLMs to Reason and Leverage Search Engin

- Fig.1 (p.4) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]]
  - Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).
- Fig.2 (p.9) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]]
  - (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Bas
- Fig.3 (p.17) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
  - Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their base counterparts. Despite this early advantage, 
- Fig.4 (p.17) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
  - Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F
- Fig.5 (p.18) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]]
  - Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO pr
- Fig.6 (p.19) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
  - The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)
- Fig.7 (p.19) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
  - We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability of reinforcement learning.

### #27 BERTopic: Neural topic modeling with a class-based TF-IDF pr

- Fig.1 (p.7) ![[assets/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-p07.png]]
  - Computation time (wall time) in seconds of each topic model on the Trump dataset. Increasing sizes of vocabularies were regulated through selection of documents ranging from 1000 documents until 43000

### #28 Dual-Head Reasoning Distillation: Improving Classifier Accur

- Fig.1 (p.2) ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p02.png]]
  - SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model Gemini 2.5 Flash, with the largest gains on CB/COPA
- Fig.2 (p.3) ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p03.png]]
  - Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train-only reasoning head applies a causal LM loss over

### #29 Dynamic Large Concept Models: Latent Reasoning in an Adaptiv

- Fig.1 (p.4) ![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p04.png]]
  - 3.1
- Fig.9 (p.7) ![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p07.png]]
  - 4.3

### #32 Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with

- Fig.1 (p.1) ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p01.png]]
  - (Left) Asynchronous RL brings substantial improvements: Through RL training, our agent, ASearcher-Web-QwQ, obtains +15.0, +2.4, and +15.6 improvements on GAIA, xBench, and

### #33 AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys

- Fig.1 (p.4) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
  - Execution timeline of a synchronous (left) and a one-step overlap (right) RL system showing underutilized inference devices. … Rollout Controller Reward Service
- Fig.2 (p.4) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
  - The AREAL architecture featuring asynchronous generation and training components.
- Fig.3 (p.4) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
  - Illustration of generation management in AREAL. Vertical lines show the ready time for the next step training. Blue crosses show the interrupted requests when new parameters arrive. 4
- Fig.4 (p.8) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p08.png]]
  - The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing. 8
- Fig.5 (p.9) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]]
  - Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupl
- Fig.6 (p.10) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]]
  - Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget of 32,768 per micro-batch for the dynamic batching 

### #34 DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via 

- Fig.2 (p.6) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p06.png]]
  - In the initial stage, we collect thousands of cold-start data that exhibits a conversational, human-aligned thinking process. RL training is then applied to improve the model perfor- mance with the co
- Fig.3 (p.14) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]]
  - For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g from the old policy 14
- Fig.6 (p.35) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]]
  - B.6. Ablation Study of Language Consistency Reward
- Fig.7 (p.37) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]]
  - As can be seen, without the LC reward, language consistency gradually deteriorates as train- ing steps increase. However, when the LC reward is applied, stable language consistency is maintained throu
- Fig.13 (p.48) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]]
  - We have categorized potential content safety challenges faced by language models into 4 major categories and 28 subcategories.
- Fig.14 (p.53) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]]
  - For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and without the risk control system (introduced in D.3.1). Additionally, we tested the multilingual safety performance of Cl

### #35 Conditional Memory via Scalable Lookup: A New Axis of Sparsi

- Fig.2 (p.6) ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p06.png]]
  - During training, to accommodate large-scale embedding tables, we employ standard model parallelism by sharding the tables across available GPUs. An All-to-All communication primitive is used to gather
- Fig.5 (p.16) ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p16.png]]
  - We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gating, and (iii) tokenizer compression. Removing any o
- Fig.7 (p.18) ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p18.png]]
  - The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations 

### #37 Linear Optimal Topic Transport for Document Similarity

- Fig.1 (p.7) ![[assets/linear-optimal-topic-transport-for-document-similarity-p07.png]]
  - k-NN classification performance across datasets affects mean test error in the CLASSIC dataset. 531
- Fig.2 (p.8) ![[assets/linear-optimal-topic-transport-for-document-similarity-p08.png]]
  - t-SNE on CLASSIC

### #38 Root Mean Square Layer Normalization

- Fig.1 (p.1) ![[assets/root-mean-square-layer-normalization-p01.png]]
  - One major feature of LayerNorm that is widely regarded as contributions to the stabilization is its re-centering invariance property: the summed inputs after LayerNorm remain intact when the inputs or
- Fig.2 (p.6) ![[assets/root-mean-square-layer-normalization-p06.png]]
  - SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.
- Fig.3 (p.7) ![[assets/root-mean-square-layer-normalization-p07.png]]
  - SacreBLEU score on new- stest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorﬂow-version Ne- matus, and change p by a step size of 10%.
- Fig.4 (p.7) ![[assets/root-mean-square-layer-normalization-p07.png]]
  - SacreBLEU score curve of Layer-
- Fig.5 (p.8) ![[assets/root-mean-square-layer-normalization-p08.png]]
  - Error rate on validation set for the attentive reader model.
- Fig.6 (p.8) ![[assets/root-mean-square-layer-normalization-p08.png]]
  - Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is comparable, RMSNorm is around 15% faster than Lay
- Fig.7 (p.13) ![[assets/root-mean-square-layer-normalization-p13.png]]
  - SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.

### #39 GQA: Training Generalized Multi-Query Transformer Models fro

- Fig.1 (p.1) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p01.png]]
  - Overview of conversion from multi-head to multi-query attention. Key and value projection matri- ces from all heads are mean pooled into a single head.
- Fig.2 (p.2) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p02.png]]
  - Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads across all query heads. Grouped-query attention instea
- Fig.3 (p.3) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p03.png]]
  - Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performance with similar speed gains and comparable quality 
- Fig.4 (p.4) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
  - Performance comparison of different check- point conversion methods for T5-Large uptrained to MQA with proportion α = 0.05. ‘Mean’ mean-pools key and value heads, ‘First’ selects the first head and ‘R
- Fig.5 (p.4) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
  - Performance as a function of uptraining pro- portion for T5 XXL models with MQA and GQA-8.
- Fig.6 (p.4) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
  - Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost 

### #42 Step-3 is Large yet Affordable: Model-system Co-design for C

- Fig.1 (p.1) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p01.png]]
  - The Pareto frontier of recent models regarding acti- vated parameters and decoding costs. The darker area is GQA models’ Pareto frontier. Note: Step-3 also has the highest attention effective rank [7]
- Fig.2 (p.6) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
  - With all the results shown, we make the following observations:
- Fig.3 (p.6) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
  - Second, the time spent on each layer will be largely unbal- anced – when running with long context, the full GQA layers consume much more time than the linear attention layers. This may not be a probl
- ⭐ Fig.4 (p.8) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
  - Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.
- ⭐ Fig.5 (p.8) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
  - The compute and memory access of different atten- tion designs during decoding, including DSv3’s MLA, Qwen3
- Fig.6 (p.11) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p11.png]]
  - Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architecture. start to be concerned about other issues like e
- Fig.7 (p.12) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p12.png]]
  - Communication topology and the multi-stages pipeline of the AFD architecture.
- Fig.8 (p.13) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
  - StepMesh communication workflow tailored for AFD.
- Fig.9 (p.13) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
  - StepMesh framework for multiple accelerators. AF-

### #43 SGLang: Efficient Execution of Structured Language Model Pro

- ⭐ Fig.1 (p.2) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]]
  - System architecture: An interpreter executes language primitives with optimized runtime.
- Fig.2 (p.3) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]]
  - The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLang are shown in red. 2
- Fig.3 (p.5) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]]
  - Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution of the radix tree in response to various requests.
- Fig.4 (p.6) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]]
  - The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with longer matched prefixes instead of using a first-com
- Fig.5 (p.7) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]]
  - Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n"). Naively, the two gen primitives correspond to two
- Fig.6 (p.8) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
  - Normalized latency on Llama-7B models. Lower is better. MMLU
- Fig.7 (p.8) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
  - Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism within a single program, and faster constrained deco
- Fig.8 (p.9) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]]
  - (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.
- Fig.9 (p.14) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]]
  - KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot 
- Fig.10 (p.17) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]]
  - Example of how regex is converted into FSM and how FSM guides the decoding process.
- Fig.11 (p.18) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]]
  - Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result compon
- Fig.12 (p.19) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
  - Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU
- Fig.13 (p.19) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
  - Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the graph and perform more static planning. D.1
- Fig.14 (p.20) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]]
  - An SGLang program and its corresponding dataflow graph.

### #44 Efficiently Serving Large Multimodal Models Using EPD Disagg

- Fig.1 (p.1) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]]
  - Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference be- tween encode and prefill stages (e
- Fig.2 (p.2) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]]
  - Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi- cantly increases capacity, enabling larger batche
- Fig.3 (p.3) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]]
  - The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from prefill to de- code, respectively. We denote the inpu
- Fig.4 (p.4) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]]
  - System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM weights for decoding tasks and use the KV cache.
- Fig.5 (p.6) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]]
  - SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively
- Fig.6 (p.7) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
  - Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b)
- Fig.7 (p.7) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
  - SLO attainment (↑) versus request rate on the
- Fig.8 (p.7) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
  - As seen, EPD consistently outperforms vLLM and Dist-
- Fig.9 (p.9) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]]
  - As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low request rates.
- Fig.10 (p.13) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
  - Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill workers. The DistServe method uses a fixed 7P configura
- Fig.11 (p.13) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
  - SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively
- Fig.12 (p.16) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]]
  - Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light gr

### #45 Mooncake: A KVCache-centric Disaggregated Architecture for L

- Fig.1 (p.2) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]]
  - Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these throughput-oriented optimizations may lead to violat
- ⭐ Fig.2 (p.4) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]
  - Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scale
- Fig.3 (p.5) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]]
  - The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.
- Fig.4 (p.6) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
  - Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate tr
- Fig.5 (p.6) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
  - Input and output length distributions in the request trace. 4
- Fig.6 (p.7) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]]
  - CDF (Cumulative Distribution
- Fig.7 (p.9) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]]
  - Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).
- Fig.8 (p.11) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]]
  - The prefill scheduling experiment in the Mooncake cluster.
- Fig.9 (p.13) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]]
  - The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.
- Fig.10 (p.14) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]]
  - Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions part
- Fig.11 (p.16) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
  - End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill and decoding instances generally remains stable ove
- Fig.12 (p.16) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
  - End-to-end experiments of Mooncake and vLLM on simulated data.
- Fig.13 (p.17) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]]
  - Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

### #48 Efficient Large-Scale Language Model Training on GPU Cluster

- Fig.1 (p.1) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]]
  - Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models with time. The number of floating-point op- erations to train these models is increasing at an exponential rate.
- Fig.2 (p.3) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]
  - Combination of tensor and pipeline model parallelism (MP) used in this work for transformer-based models.
- Fig.3 (p.3) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]
  - GPipe pipeline schedule with forward passes (blue) for all microbatches (represented by numbers) followed by backward passes (green). The gray area represents the pipeline bubble. For simplicity, we a
- Fig.4 (p.3) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]
  - Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned mu
- Fig.5 (p.5) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]
  - Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). 𝑓and 𝑔 are conjugate. 𝑓is the identity operator in the forward pass and all- reduce in the 
- Fig.6 (p.5) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]
  - Fraction of time spent idling due to pipeline flush (pipeline bubble size) versus data-parallel size (𝑑), for different numbers of GPUs (𝑛) and ratio of batch size to microbatch size (𝑏′ = 𝐵/𝑏).
- Fig.7 (p.6) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]
  - Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).
- Fig.8 (p.6) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]
  - Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·  𝑡𝑓(𝑏) + 𝑡𝑏(𝑏)) with respect to the mi- crobatch size 𝑏for the same GPT model from Figure 7.
- Fig.9 (p.7) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]]
  - Scatter/gather communication optimization. Light blue blocks are layers in the first pipeline stage, and dark blue blocks are layers in the second pipeline stage. Without the scatter/gather optimizati
- Fig.10 (p.8) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]]
  - Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B GPT-3 model is shown with dotted lines, and the 530B model is shown with solid lines). Global batch sizes are fixed and 
- Fig.11 (p.9) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]
  - Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size). 12 24 36 48 60
- Fig.12 (p.9) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]
  - Throughput per GPU of interleaved and non-interleaved schedules for a GPT model (175 billion parameters) on 96 GPUs. and a microbatch size of 1. As we increase the number of pipeline stages, we also i
- Fig.13 (p.9) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]
  - Throughput per GPU of various parallel configurations that combine pipeline and tensor model parallelism using a GPT model with 162.2 billion parameters and 64 A100 GPUs.
- Fig.14 (p.10) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]
  - Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, mi- crobatch size of 
- Fig.15 (p.10) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]
  - Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, a
- Fig.16 (p.10) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]
  - Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs. importance 
- Fig.17 (p.11) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]
  - Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion param- eters using 128 A100 GPUs ((𝑡, 𝑝) = (8, 16)). 12 24 36 48 60
- Fig.18 (p.11) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]
  - Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved schedule.

### #52 Efficient Memory Management for Large Language Model Serving

- ⭐ Fig.1 (p.1) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p01.png]]
  - Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory for the KV cache (red) is (de)allocated per servi
- Fig.2 (p.2) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p02.png]]
  - Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2. percentage of memory is used for other data, including ac- tivations – the ephemeral tensors created
- Fig.3 (p.4) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p04.png]]
  - KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist that prevent other requests from fitting into the me
- Fig.4 (p.5) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
  - vLLM system overview.
- Fig.5 (p.5) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
  - Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size (𝐵). Denote the key block 𝐾𝑗= (𝑘(𝑗−1)𝐵+1, . . . ,
- Fig.6 (p.6) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
  - Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also maintains block tables—the mapping between logical 
- Fig.7 (p.6) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
  - Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds it into the LLM. During LLM’s computation, vLLM u
- Fig.8 (p.7) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
  - Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates multiple sequences. In parallel sampling, one req
- Fig.9 (p.7) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
  - Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at every step. During decoding, beam search ex- pands ea
- Fig.10 (p.8) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p08.png]]
  - Shared prompt example for machine translation.
- Fig.11 (p.9) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p09.png]]
  - Input and output length distributions of the (a)
- Fig.12 (p.10) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
  - Single sequence generation with OPT models on the ShareGPT and Alpaca dataset
- Fig.13 (p.10) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
  - Average number of batched requests when serv- ing OPT-13B for the ShareGPT (2 reqs/s) and Alpaca (30 reqs/s) traces.
- Fig.14 (p.11) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
  - Parallel generation and beam search with OPT-13B on the Alpaca dataset.
- Fig.15 (p.11) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
  - Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.
- Fig.16 (p.12) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
  - Translation workload where the input prompts share a common prefix. The prefix includes (a) 1 example with 80 tokens or (b) 5 examples with 341 tokens.
- Fig.17 (p.12) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
  - Performance on chatbot workload.
- Fig.18 (p.12) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
  - Ablation experiments. handle the long prompts, as PagedAttention resolves the problem of memory fragmentation and reservation. 7
- Fig.19 (p.13) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p13.png]]
  - (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same request rate.

### #53 DeFT: Decoding with Flash Tree-attention for Efficient Tree-

- Fig.1 (p.1) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p01.png]]
  - Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., 2022; Liu et al., 2023) or selection, as shown in 
- ⭐ Fig.2 (p.5) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]
  - Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV
- Fig.3 (p.6) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p06.png]]
  - Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-
- Fig.4 (p.9) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p09.png]]
  - Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.
- Fig.5 (p.15) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p15.png]]
  - Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decoding tree example.
- Fig.6 (p.16) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p16.png]]
  - Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.
- Fig.7 (p.17) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p17.png]]
  - Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cache in storage and memory access during the tree at
- Fig.8 (p.19) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
  - Operations of Tree Attention-Medusa (Cai et al., 2024). No Kernel Fusion or Tiling strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global
- Fig.9 (p.19) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
  - Overview of two stages in DEFT Attention Kernel (DEFT-Node for example, and DEFT-Flatten is similar). Stage 1–calculate partial attentions. Based on the QKV grouping results after KV-Guided Grouping
- Fig.10 (p.20) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p20.png]]
  - Detailed attention operations of DEFT kernel (DEFT-Node for example, and DEFT-Flatten is similar). Based on the same decoding tree in Figure 3.
- Fig.11 (p.21) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p21.png]]
  - When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For instance, in the Llama models (Touvron et al., 2023a
- Fig.12 (p.23) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p23.png]]
  - The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)
- Fig.13 (p.25) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p25.png]]
  - Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. Tree Node Len std represen
- Fig.14 (p.26) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
  - Per iteration latency for few-shot prompting tasks with different tree width. e2e means decoding latency(optimal end-to-end latency), while Attn means only the attention overhead.
- Fig.15 (p.26) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
  - The chunk size selection is a trade-off between IO redundancy and threadblock scheduling: a larger chunk size means less redundancy of Query IO but may cause potential idle SMs of GPUs due to fewer th
- Fig.16 (p.27) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
  - Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000
- Fig.17 (p.27) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
  - Decoding latency of DEFT with different prompt lengths in speculative decoding.
- Fig.18 (p.28) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p28.png]]
  - Attention latency of DEFT with different prompt lengths in speculative decoding.

### #54 NanoFlow: Towards Optimal Large Language Model Serving Throu

- ⭐ Fig.1 (p.3) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p03.png]]
  - Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are compute-bound. Operations in green boxes require 
- Fig.2 (p.5) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]
  - Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the workload is more network-bound. LMSYS-Chat Splitwise
- Fig.3 (p.5) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]
  - Comparison of compute time and memory time.
- Fig.4 (p.8) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]
  - Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operations in the previous and next layer are denoted by d
- Fig.5 (p.8) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]
  - Interference characteristics between GEMM and GEMV kernels. The points on the x-axis correspond unique GEMM-GEMV implementation pairs. The y-axis denotes the GEMM and GEMV kernels’ normalized performa
- Fig.6 (p.11) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]
  - Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utiliz
- Fig.7 (p.11) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]
  - Offline throughput comparison. NanoFlow outper- forms all baselines for all the workload settings. TP stands for the number of GPUs used with tensor parallelism. • How do the various techniques propos
- Fig.8 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher request within 200ms SLO constraints.
- Fig.9 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - Ablation study results for NanoFlow. Nano-batching and overlapping improves NanoFlow’s performance.
- Fig.10 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - While the non-overlapping baseline sequentially executes operations, which mostly uses only one resource at a given time, the NanoFlow instance can concurrently utilize multiple resources and achieves
- Fig.11 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - We find that

### #55 Gated Delta Networks: Improving Mamba2 with Delta Rule

- ⭐ Fig.1 (p.7) ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]
  - Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.
- Fig.2 (p.8) ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]]
  - Length extrapolation on six long benchmarks.
- Fig.3 (p.9) ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]]
  - Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

### #56 Parallel Scan on Ascend AI Accelerators

- ⭐ Fig.3 (p.3) ![[assets/parallel-scan-on-ascend-ai-accelerators-p03.png]]
  - 1 shows the Ascend architecture where the
- Fig.4 (p.4) ![[assets/parallel-scan-on-ascend-ai-accelerators-p04.png]]
  - 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).
- Fig.5 (p.7) ![[assets/parallel-scan-on-ascend-ai-accelerators-p07.png]]
  - 1: A diagram of well-known parallel scan applica- tions considered here along with their dependencies.
- Fig.6 (p.8) ![[assets/parallel-scan-on-ascend-ai-accelerators-p08.png]]
  - 1:
