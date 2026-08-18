# KV Cache Optimization Strategies for Scalable and Efficient LLM Inference — 技术点深读（DEEP 2026-08-18，公式重跑）

> 独立文件：本 deep note 与 extract_phase1 生成的论文 MD body 分离，按 MEMORY 铁律独立维护，不受 extract 重写覆盖影响。
> Source: `extraction/fulltext/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.txt` (arXiv:2603.20397v1, 20 Mar 2026). Yichun Xu, Navjot K. Khaira, Tejinder Singh (Dell Technologies). Survey — five-direction taxonomy paper mapping 36 representative methods to 7 deployment scenarios. Sister survey to [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] (PolyU/HKUST 三级 taxonomy paper)；本文偏 inference scalability & practitioner-facing deployment mapping，姊妹篇偏 academic taxonomy + 12 mechanism-level tables。
> **公式权威源**：以下所有 `$$` 公式引自 `extraction/formulas.json`（LaTeX 原文，完全正确，不凭训练知识重写/补全）；与 M3 caption 对架构图的解读逐式做 LaTeX↔M3 双源校验。

## 核心问题

本文攻击的是一个 **部署侧的实践性问题**。开篇 Figure 1（p.2，M3 解读：两步自回归生成 "The apple tastes sweet." → "."，橙色 query 对全部 cyan 历史 token 做因果 attention，callout 标出 KV Cache 存历史 K/V 避免每步重算）即点明：KV cache 把每步 per-token 成本从 O(n²) 降到 O(n)，代价是 **内存随上下文线性增长**。

Figure 2（p.3，M3 解读：单 transformer 层内 x_t 经 W_K/W_Q/W_V 三投影，K_t/V_t 被 append 进各自 per-layer cache K_c=[K_1,…,K_t]、V_c=[V_1,…,V_t]，Q_t 对全 cache 做 scaled dot-product attention）量化了这个线性代价。M3 caption 直接给出了该层的输出公式：

$$o_t = \mathrm{softmax}\!\left(\tfrac{Q_t \mathbf{K}_c^{\top}}{\sqrt{d_k}}\right)\mathbf{V}_c.$$

> **LaTeX↔M3 双源校验**：M3 对 Figure 2 的图解公式与 formulas.json [3] 的通用 softmax 形式 `α_{ij} = softmax(Q_i·K_j^T/√d_k)`（Eq.4）一致——前者是 single-query 对全 cache 的实例化，后者是逐元素 (i,j) 形式；分子分母结构、√d_k 缩放、softmax 归一化三要素双源吻合，cache 规模 O(T) per head per layer 同向。cache 规模的量化来自 §2.2 Eq.1–Eq.2（formulas.json [0][1]）：

$$KV_{per\ token} = 2 \times H\times D \times B \times L$$

$$KV_{cache\ size} = KV_{per\ token} \times \mathrm{Context Length}$$

其中 H=head 数、D=每 head 维度、B=每元素字节数（fp16 时 B=2，fp32 时 B=4）、L=transformer 层数（§2.2）。当上下文窗口从数千 token 扩到百万级（§1, §3 引言引 GPT-5 [7] / Llama 4 [8]），线性增长对 GPU 显存容量、显存带宽、推理吞吐同时形成 critical bottleneck。Figure 3（p.3，verbar caption 在 fulltext，无 M3 caption）给出量化：7B 模型（0.50 MB/token, 32L×32H）在 128K 上下文下 KV cache ≈64 GB，已超 A100 80GB 上限；13B（0.78 MB/token）更早触顶；70B-GQA（0.31 MB/token, 80L×8H）因 GQA head 共享而 per-token 更省，但绝对量仍大。这张图把"为什么 KV cache 是 first-order 部署难题"用三条曲线 + 两条 GPU VRAM 虚线（RTX 4090 24GB / A100 80GB）一刀切清。

进一步，§2.3 的 Figure 4（p.4，M3 解读：4×4 因果 attention 权重矩阵，Viridis 配色，"sweet" query 把 65% 注意力集中到 "apple"（0.65），"The" 仅 0.05，低权重 KV 标为 eviction candidate）用一句话的 toy example 奠定了全文 eviction 路线的经验前提：**KV entries 的贡献高度非均匀**——这是 H2O/SnapKV 等用 attention score 做 eviction 信号的合法性来源。该 toy example 的数值就是 Eq.3–Eq.5（formulas.json [2][3][4]）的实例：

$$\mathrm{Score}\left( Q_i, K_j\right) = \frac{Q_i \cdot K_j^{T}}{\sqrt{d_k}}$$

$$\alpha_{ij} = \mathrm{softmax}\!\left( \frac{Q_i \cdot K_j^{T}}{\sqrt{d_k}} \right)$$

$$\mathrm{output}_i = \sum_{j} \alpha_{ij} V_j$$

> **LaTeX↔M3 双源校验**：Figure 4 的 4×4 权重矩阵每行和为 1（post-softmax）正是 Eq.4 `α_{ij}=softmax(·)` 行归一化的可视化；"sweet"→"apple" 0.65 即 Eq.3 `Score(Q_i,K_j)=Q_i·K_j^T/√d_k` 经 softmax 后的高权重项；最终 token 输出由 Eq.5 `output_i=Σα_{ij}V_j` 加权聚合。formulas.json [2][3][4] 与 M3 对 Figure 4 的数值解读逐项对齐。

不同于单篇方法论文"只攻一处"或既有 survey "broad but shallow"（§1 自述），本文提供 **middle-ground perspective**：(1) 把 KV cache 优化系统性归入 **五大方向**（Cache Eviction / Cache Compression / Hybrid Memory / New Attention Mechanism / Combination Methods, §2.4 Figure 5 p.5, Tab.1）；(2) 再把每方向方法 **映射到 7 个实际部署场景**（§5.1–5.8），给从业者"在该约束下选哪一类"的可执行答案。核心结论（§6）：**没有任何单一技术 dominate 所有 setting**——最优策略取决于 context length / hardware constraints / workload characteristics，未来方向是 **adaptive, multi-stage optimization pipelines**。

## 关键创新点

作为 survey，"创新点"指其分类骨架与部署映射贡献：

1. **五方向 taxonomy（§2.4, Figure 5 p.5, Tab.1）——以"系统级优化目标"为切分轴**
   - 机制：Figure 5（p.5，M3 解读：根节点 "KV Cache Optimization" 平行分五支，每支挂代表方法——Cache Eviction: H2O/SnapKV/NACL/Ada-KV；Cache Compression: KIVI/PALU/MiniCache/KVQuant；Hybrid Memory: PagedAttention/InfiniGen/LayerKV；New Attention: Linear/Log-Linear/KIMI Linear；Combination: FlexGen/ShadowKV/TailorKV）显式把"五类各自攻不同瓶颈"可视化：memory footprint / decoding latency / TTFT / throughput / attention complexity。本文据此构建 Tab.1：每方向列 Optimization Goal / Tradeoffs / Representative Methods / Good for，与 Figure 5 一一对应。
   - 效果：不同于姊妹 survey 的 Token/Model/System 三级轴，本文按"优化目标 + trade-off 类型"分五类——Eviction（降 footprint 与 decoding latency，代价 accuracy）/ Compression（降 size 提 throughput，代价 dequant/reconstruction overhead）/ Hybrid Memory（降 TTFT 提系统效率，代价硬件依赖与管理复杂度）/ New Attention（降计算复杂度提速，代价 accuracy 与 retraining）/ Combination（平衡 throughput/latency，代价设计复杂度）。每类直接绑定 "Good for" 部署场景（Tab.1 末列），把"方法—trade-off—场景"三段式打通。这是本文与姊妹 survey 最大差异：后者偏 mechanism-level 对照表，本文偏 deployment-scenario mapping。

2. **Cache Eviction 的 9 方法精细对比（§3.1, Tab.2）——按 eviction phase 与 importance signal 分轴**
   - 机制：H2O [1]（accumulated attention, decoding，Figure 6 p.6 M3 解读：上排四张 symbolic attention-map 对比 Dynamic/Static-Strided/Static-Local/Static+H2O 的稀疏模式，H2O 保留 heavy-hitter 列 + local band 的 hybrid 模式；左下图 token 序列 "Children laughed and played in the sunny park…" 各 token KV 评分 0.2/0.1/0.1/0.6，Query 累积 attention (1, 1.4, 1.5, ✗, 0.6) 丢弃最低分保持 budget；右下 accuracy-vs-memory reduction 曲线显示 H2O 与 Dynamic 在 ~80% 压缩下仍 >75% 精度，而 Static Strided/Local 超 60–80% 即崩塌）→ SnapKV [2]（observation window voting + 1D pooling, after prefill，Figure 7 p.7 M3 解读：多轮对话 prompt 进 stacked Layers 的 Input Sequence KVs，每层分 Prefix 橙区 + Obs. window 绿区，经 "Attention Weight Calc → Voting & Selecting Important Features → Clustering & Concatenating Features" 跨 head 聚合产生 Compressed KVs）→ NACL [9]（proxy-token + random 单次 prefill eviction, O(1) 单 shot，softmax 概率采样填剩余 eviction budget）→ InfiniPot [10]（Continual Context Distillation, CaP "Summarize the critical points" prompt + NuC novelty 双指标, prefill, pot 溢出触发蒸馏）→ HASHEVICT [11]（pre-attention SimHash LSH + Hamming distance, decoding, attention-free, GPU-friendly 位运算）→ MorphKV [13]（recent attention pattern + Sum/Max Fusion, decoding，Sum 适合 contextual consistency，Max 适合 sharp focused retrieval）→ RocketKV [14]（SnapKV 粗驱逐 + Hybrid Sparse Attention 细检索, 两阶段，page 粒度存 max/min key 做近似）→ KVzip [15]（query-agnostic, "Repeat the previous content" 自监督 context reconstruction 评分, prefill，autoencoder-like）→ Ada-KV [3]（head-wise adaptive budget, plug-and-play with SnapKV）。
   - 效果：Tab.2 + Tab.6 给出内存/速度/精度三维权衡——H2O 5–10× memory reduction + up to 29× throughput / ≤1.9× lower latency vs FlexGen，但其 accumulated-attention bias 与 heavy-hitter 丢失风险是 Figure 6 右下图精度曲线在极端压缩下也承压的根因；RocketKV up to 400× 压缩（§4 Tab.6）；HASHEVICT 30–70% 压缩 + 1.5–2× prefill speedup（17× prefill / 2× decoding vs FastGen），但 10% cache budget 下精度急降；NACL 5× KV reduction + 95% 性能保留 + O(1) 单 shot；Ada-KV 4× cache reduction + ~5% 精度提升。明确"固定 budget 均匀分配到所有 head"是传统方法 key limitation，Ada-KV 把"sparse head 预算让给 dispersed head"并给出 eviction loss 上界（§3.1 末）。

3. **Cache Compression 的四象限（§3.2, Tab.3）——quantization / cross-layer merge / low-rank projection**
   - 机制：KIVI [5]（key per-channel + value per-token 非对称量化，因 key cache "a few fixed channels whose magnitudes are very large" 而 value cache "no obvious outlier pattern"；group（32 tokens/group）+ residual（recent full precision）动态合并，key 每 residual 达阈值触发量化、value 每新 token 触发；2-bit plug-and-play。Figure 8 p.8 仅有 verbatim fulltext caption 无 M3 caption，该图定义 per-token vs per-channel 量化：X ∈ R^{l_prompt×d}，z_X 零点、s_X scaling factor）→ KVQuant [20]（per-channel pre-RoPE + sensitivity-weighted non-uniform + dense-and-sparse outlier 分离（top 1% 存 fp16）+ attention-sink-aware（首 token 全 fp16），支持 10M token 上下文；pre-RoPE 量化保持结构完整性，因 RoPE 旋转使量化更难）→ MiniCache [21]（跨相邻层 KV 相似度（angular distance/cosine），中深层 representation 稳定，SLERP 合并 + 方向/幅度/角度存储重建，不达阈值则不合并）→ PALU [19]（SVD 把 W ≈ A×B，cache latent H 不 cache Y，Matrix Fusion 离线融合 B 到既有 weight 矩阵，RoPE key 用 custom GPU kernel 动态重建；G-LRD 折中 joint vs per-head decomposition，给 critical layer 分配更高 rank。Figure 9 p.9 M3 解读：X → A → H（latent bottleneck，缓存）→ B → Ỹ（重建），红色标注 "Cache H instead of Y"，强调 W 的分解离线预计算使重建误差最小）。
   - 效果：Tab.6 量化数字——KIVI 2.6× peak memory / 2.35–3.47× throughput / <2% accuracy drop（单 KV head 模型可能需 4-bit）；KVQuant 3.7–6.9× memory / <0.1 perplexity degradation @3-bit / ~1.7× speedup；MiniCache 41% memory reduction / ~5× throughput（仅合并两层，更高压缩受限）；PALU ~50% KV 压缩 / 1.89×（RoPE）–2.91×（with quant）。明确 KVQuant 的 Pre-RoPE 量化是 KIVI 之外的独立创新——pre-RoPE 保持结构完整性（§3.2）。

4. **Hybrid Memory 七系统的硬件感知谱系（§3.3, Tab.4）——从 paging 到 near-storage 计算**
   - 机制：PagedAttention [22]（OS virtual memory 启发，KV block + block table + copy-on-write，并行采样共享 prompt block。Figure 10 p.11 M3 解读：vLLM 系统——中心 Scheduler 调度 N 个并行 Worker，每 Worker 持 Cache Engine + Model Shard on GPU；Scheduler 接 KV Cache Manager，维护 Block tables（类 OS page table）+ CPU/GPU Block Allocator 双分配器，decouple 集中调度与分散 cache 管理，支持非连续 block 级 KV 存储）→ InfiniGen [23]（Partial Q 预测下一层所需 KV，CPU→GPU 预取与计算重叠，预测公式见 Eq.6 / formulas.json [5]）：

$$\tilde Q^{(\text{layer}+1)} = X^{(\text{layer})} \cdot M \cdot W_Q^{(\text{layer}+1)}$$

其中 M 为离线 SVD 学的低秩变换矩阵。Figure 11 p.12 M3 解读：三阶段流水——Offline Skewing 预计算 attention weight skewness profile；Prefill 期 GPU 跑 Partial Weight Index Generation 标记重要 token id；Decoding 期 GPU 跑 KV selector → Attention → FFN，CPU 并行发 Prefetching，selected token id（橙）CPU→GPU、selected K/V（蓝）喂下一层 selector，实现"决定哪些 token 重要"与"只取这些 token"解耦。

> **LaTeX↔M3 双源校验**：Eq.6 的 Partial Q 公式 `Q̃^(layer+1)=X^(layer)·M·W_Q^(layer+1)` 与 M3 对 Figure 11 的解读"Partial Weight Index Generation 在 Prefill 期由当前层输入 + 下一层 W_Q 预测"一致；M3 未给公式但描述的 "X(layer) → M (low-rank, SVD offline) → W_Q(layer+1) → 预测下一层所需 KV" 因果链与 formulas.json [5] 严格对应，M 即公式中的低秩变换。

→ LayerKV [24]（层粒度 offload，选最小 GPU 层数使 `offload time ≤ prefill time`，如 8 层留 1/3/5/7 在 GPU 而 0/2/4/6 offload，CPU 传回 layer 0 时 GPU 在算 layer 1；SLO-aware TPOT scheduler）→ INF2 [25]（Computational Storage Devices with FPGA/ASIC，attention-near-storage，PCIe private switch，KV 存 SSD+CSD，GPU 并行做 MLP，新 KV 批量回写）→ KVPR [26]（partial KV 重算与传输重叠，profiling 决定 row-wise（latency）/ column-wise（throughput）调度，使小部分 KV 重算时间 = 其余 KV 传输时间）→ Oneiros [27]（parameter remapping：解码期把 inactive model 参数 offload 出 GPU 腾出 KV 空间，逐层均匀分布 remapped layer 隐藏传输，KV 压力消退则 reverse remapping）→ CLO [28]（query 相邻步高相似度→复用上一轮 KV；低相似度则 InfiniGen 式 prefetch；GDRCopy zero-copy engine；critical head 永驻 GPU 防 latency spike）。
   - 效果：Tab.6——PagedAttention offload based + 2–4× throughput + lossless（kernel overhead / block table 管理）；InfiniGen 1.63–32.9× speedup + 需 >15% Relative KV Cache Size + 需额外 GPU 存 partial weight；LayerKV up to 69× TTFT 改善 + lossless（高负载解码 throughput 略降）；INF2 3.46× throughput / KV I/O 降低 >80% + lossless（需 CSD 硬件）；KVPR 35.8% lower latency / 46.2% higher throughput vs DeepSpeed+HF Accelerate；Oneiros 44.8–82.5% TBT 降 / 20.7–99.3% TTFT 降 / 6.6–86.7% throughput 提升 vs vLLM（需高 CPU–GPU 带宽 450–900 GB/s）；CLO 9.3–66.6% throughput 提升 vs RetroInfer/InfiniGen + ≤0.42% drop（PCIe 4.0 依赖）。

5. **New Attention 的复杂度阶梯（§3.4, Tab.5）——O(N²) → O(N log N) → O(N)**
   - 机制：Softmax O(T²)/O(T)/O(T)（Eq.3–Eq.5，scaled dot-product，§2.3）→ Linear (Transformers-are-RNNs [29]，kernel feature map `φ(·)` 把 `softmax(q·k)` 近似为 `φ(q)·φ(k)`，递归累积，O(N)/O(1)/O(1))。线性注意力的完整定义见 formulas.json [6]–[9]（§3.4 Eq.7–Eq.9 等价组）：

$$V_i' = \frac{\phi(Q_i)^T \sum_{j=1}^{i} \phi(K_j) V_j^T} {\phi(Q_i)^T \sum_{j=1}^{i} \phi(K_j)}$$

$$V_i' = \frac{\phi(Q_i)^T S_i}{\phi(Q_i)^T Z_i}$$

$$S_i = \sum_{j=1}^{i} \phi(K_j) V_j^T$$

$$Z_i = \sum_{j=1}^{i} \phi(K_j)$$

其中 `φ(·)` 是 feature map（elementwise，把 `similarity(q,k)=softmax(q^T k)` 近似为 `similarity(q,k)≈φ(q)·φ(k)`），S_i 与 Z_i 可增量累积，从而把 attention 重排为线性时间/常数空间的递归。

→ Log-Linear [30]（Fenwick tree 桶，每桶 summary matrix `S_t^(ℓ)`，older token 渐入 coarser bucket，至多 log₂(t) 桶活跃，O(N log N)/O(log N)/O(log N)。其输出聚合公式见 formulas.json [10]（§3.4 Eq.10）：

$$o_t = \sum_{\ell=0}^{L-1} \lambda_t^{(\ell)} q_t^T \left(\sum_{s \in B_t^{(\ell)}} v_s k_s^T \right) = \sum_{\ell=0}^{L-1} \lambda_t^{(\ell)} q_t^T S_t^{(\ell)}$$

其中 `B_t^(ℓ)` 是桶 ℓ 的 token 集合、`λ_t^(ℓ)` 是桶权重、`S_t^(ℓ)=Σ_{s∈B} v_s k_s^T` 是桶级 summary matrix。Figure 12 p.15 M3 解读：上图 Linear Attention 是扁平顺序 block 链，输出严格 left-to-right 无层级聚合；下图 Log-Linear 是树形层级聚合，⊕ 节点局部 pool 邻近 KV 再逐级向上归并，使远距 token 间路径长从 O(n) 降到 O(log n)，保线性效率同时提升表征力。

> **LaTeX↔M3 双源校验**：Eq.10 的 `Σ_{ℓ=0}^{L-1} λ^(ℓ) q^T S^(ℓ)` 树形多桶聚合与 M3 对 Figure 12 下图"⊕ 节点局部 pool 邻近 KV 再逐级向上归并"的层级树结构一致——公式中的桶 ℓ 对应 M3 图中的层级聚合层，S_t^(ℓ) 对应 ⊕ merge 节点产出的 summary；log₂(t) 活跃桶 ↔ M3 "logarithmic-depth reduction"。双源吻合。

→ Local Linear Attention [31]（attention 类比为 regression：softmax=local constant（看邻近 key 平均 value）、linear=global linear regression（拟合全局直线）、LLA=local linear regression（每 query 局部拟合小线性模型），O(N²)/~O(N)/O(N)，适应 non-stationary/time-varying 分布）→ KIMI Linear [32]（Kimi Delta Attention KDA，forget gate α + update rate β 双门控，状态更新与输出公式见 formulas.json [11][12]（§3.4 Eq.11–Eq.12）：

$$S_t = (I - \beta_t k_t k_t^T)\,\mathrm{Diag}(\alpha_t)S_{t-1} + \beta_t k_t v_t^T \in \mathbb{R}^{d_k \times d_v}$$

$$o_t = S_t^T q_t \in \mathbb{R}^{d_v}$$

其中 `Diag(α_t)` 是 forget gate 对角矩阵（α 接近 1 保留旧记忆、接近 0 快速遗忘），`(I − β_t k_t k_t^T)` 防过拟合旧关联、`β_t k_t v_t^T` 存新 KV 对；与 full attention 3:1 hybrid ratio，chunk 化处理增并行）。
   - 效果：Tab.6——LinearAttention O(1) memory + up to 4000× 长序列提速（feature map kernel 敏感，复杂任务弱）；Log-Linear O(log T) memory + 3× speedup（性能介于 linear 与 full attention 间）；LLA outperforms softmax & linear on associative/regression 任务（trades speedups for accuracy）；KIMI up to 75% KV reduction + up to 6× throughput @1M context（§5.1 实为 6.3×），作者称 outperforms full attention，但需 retrain + kernel 依赖。关键结论：linear 类方法需 full retrain，accuracy-critical reasoning 仍落后 full attention，是"未来 transformer 继任者"方向而非 drop-in 优化（§6）。

6. **Combination Methods 的四框架（§3.5）——sparsity × quantization × offload**
   - 机制：FlexGen [33]（weights/activations/KV 跨 GPU/CPU/disk 划分，cost model + linear programming 解最优 placement，4-bit group-wise 量化（每小组共享 min/max scaling range），zig-zag block scheduling 最大化 weight reuse）→ Q-Hitter [34]（attention score + quantization error 双指标统一打分 S，选 top-K 量化存储，sparse-quantized KV，S 高者既重要又 robust to quant noise）→ ShadowKV [35]（pre-RoPE key 强低秩→SVD 保留 top-rank 存 GPU；value 不低秩→offload CPU；post-RoPE key chunk 切分取 landmark（mean）→低 cosine similarity 标 outlier 全存 GPU；decoding 期 landmark 估计相关 chunk，按需 fetch value，GPU 端 low-rank key 重建 + RoPE 后做 sparse attention。Figure 13 p.17 M3 解读：GPU/CPU 水平分界，Pre-filling 期 Pre-RoPE Key Cache 三分支——SVD→Low-rank Key Cache、RoPE & Reduce→Landmarks、Find Outliers→Outliers，Value Cache offload CPU；Decoding 期 GPU 跑 KV Selection（查 Landmarks/Low-rank/Outliers）→ Cache Hit/Miss → Low-rank Key Reconstruction+RoPE → Sparse Attention，CPU 端 Selected Missed Chunk ID 触发 Value Cache Fetching 回 GPU）→ TailorKV [36]（layer-specific：浅层 attention 分散（top-k 之和小说明 spread out）→quantization-friendly 激进量化存 GPU；深层 attention 集中（top-k 之和大）→sparsity-friendly offload CPU 动态 top-K fetch；double buffering 隐藏传输。Figure 14 p.18 仅有 verbatim fulltext caption 无 M3 caption，该图展示 offline identification 把 layer 分 quantization-friendly / sparsity-friendly 两类，critical current query 与 critical key cache 标 outlier）。
   - 效果：Tab.6——FlexGen up to 10× memory / 40–100× throughput vs DeepSpeed-Zero-Inference（@4-bit negligible loss，高延迟，小 batch 不足）；Q-Hitter up to 20× memory / 33× vs HF Accelerate（full quality preservation，dequant 开销）；ShadowKV 6× GPU memory / 3.04× throughput（high until sparse budget <1.56%，部分依赖 PCIe 带宽）；TailorKV ~73.8% GPU memory reduction / 8–18× faster than standard offloading / near lossless（prefill 瓶颈，系统复杂）。

7. **场景-方法决策矩阵（§5.1–5.8）——本文最强 practitioner 贡献**
   - 机制：把 7 类部署场景（long-context single request / minimal model modification / high-throughput serving / edge devices / multi-turn conversations / prefill-heavy / accuracy-critical reasoning）+ 1 类 hardware-specific，逐一映射到推荐方法与禁忌方法，并给反例（H2O 不适合 multi-turn 因永久丢弃未来 turn 所需 token；FlexGen 不适合 interactive dialogue；linear/log-linear 不适合 minimal model modification 与 accuracy-critical reasoning；PagedAttention/Oneiros 不适合 edge 因需 high-end GPU / 450–900 GB/s 带宽）。
   - 效果：这是姊妹 survey 未显式提供的"反向 guidance"——不只说"选什么"，更说"不选什么"，把 Tab.1 的 "Good for" 列落地为可执行禁忌清单。

## 表格（原文结构化）

### 表 A — 五方向 taxonomy 与仓库 deep note 对照（据 Figure 5 p.5, Tab.1, Tab.2/3/4/5, §3 重构）

| 方向 | 机制 | 代表方法（原文编号） | Phase | 仓库对应 deep note |
|---|---|---|---|---|
| Cache Eviction (§3.1, Tab.2, Figure 6/7) | 累积 attention / observation window 投票 / proxy-token + random / continual distillation / LSH / correlation-aware / 两阶段 / reconstruction / head-wise budget | H2O[1], SnapKV[2], NACL[9], InfiniPot[10], HASHEVICT[11], MorphKV[13], RocketKV[14], KVzip[15], Ada-KV[3] | decoding / after-prefill / prefill 混 | — |
| Cache Compression (§3.2, Tab.3, Figure 8/9) | 非对称量化 / non-uniform + pre-RoPE / cross-layer SLERP merge / SVD low-rank projection | KIVI[5], KVQuant[20], MiniCache[21], PALU[19] | decoding | — |
| Hybrid Memory (§3.3, Tab.4, Figure 10/11) | paging / 预测 prefetch / 层粒度 offload / near-storage 计算 / 重算-传输重叠 / parameter remapping / query 相似度复用 | PagedAttention[22], InfiniGen[23], LayerKV[24], INF2[25], KVPR[26], Oneiros[27], CLO[28] | prefill + decoding | [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] |
| New Attention (§3.4, Tab.5, Figure 12) | kernel linear / Fenwick tree log-linear / local linear regression / KDA + 3:1 hybrid | LinearAttention[29], Log-Linear[30], LLA[31], KIMI Linear[32] | training-time | — |
| Combination (§3.5, Figure 13/14) | LP offload + 4-bit / sparse-quantized / low-rank key + offload value / layer-specific quant vs sparsity | FlexGen[33], Q-Hitter[34], ShadowKV[35], TailorKV[36] | prefill + decoding | — |

### 表 B — 部署场景 → 推荐方法矩阵（据 §5.1–5.8 重构）

| 场景 | 推荐 | 禁忌/不推荐 |
|---|---|---|
| Long-context >1M single request (§5.1) | Eviction + Compression 组合；KIMI (75% KV reduction @1M, 6.3× throughput) | — |
| Minimal model modification (§5.2) | Ada-KV / SnapKV / KIVI (plug-and-play, tuning-free；KIVI 2-bit tuning-free) | Linear / Log-Linear / LLA / KIMI (需 retrain + 改架构) |
| High-throughput serving (§5.3) | PagedAttention (vLLM), Oneiros (86.7%↑ vs vLLM), ShadowKV (3.04×); 单 GPU 极端 FlexGen / Q-Hitter | — |
| Edge / memory-limited (§5.4) | InfiniPot (mobile/NPU, fixed "pot"), TailorKV (8B@128k on RTX 3090) | PagedAttention (需 high-end GPU), Oneiros (需 450–900 GB/s 带宽) |
| Multi-turn conversations (§5.5) | RocketKV-MT (保留全 KV 跨 turn), KVzip (overhead amortizable across queries), ShadowKV (low-rank 子空间跨 turn 共享) | H2O (永久丢弃未来 turn 所需 token), FlexGen (latency 不适合交互) |
| Prefill-heavy (§5.6) | NACL (单次 prefill eviction), HASHEVICT (1.5–2× prefill speedup), LayerKV (69× TTFT), MiniCache, CLO (parallel prefill + speculative prefetch) | — |
| Accuracy-critical reasoning (§5.7) | Hybrid Memory (PagedAttention 等 lossless) | Eviction / Compression / Linear / Log-Linear (均有精度代价) |
| Hardware-specific (§5.8) | GH200 高 PCIe 带宽→Oneiros / CLO；CSD (FPGA/ASIC)→INF2；单 GPU 限内存→FlexGen | — |

### 表 C — 性能数字总览（据 Tab.6 重构，按内存/速度/精度三维权衡）

| 方法 | 内存 | 速度 | 精度 | 关键 trade-off |
|---|---|---|---|---|
| H2O | 5–10× reduction | 29× throughput / ≤1.9× lower latency vs FlexGen | comparable | 累积 attention bias；heavy-hitter 丢失风险（Figure 6 右下图：>80% 压缩精度承压） |
| SnapKV | 8.2× | 3.6× generation | comparable | 不优化 prefill；不能扩模型固有 context limit |
| NACL | up to 5× KV | O(1) single-shot | 95% retention | proxy-token 选择启发式；ultra-long 行为有限 |
| InfiniPot | 4k–1M token 测试 | regardless of context length | consistent | 固定压缩比未必适配所有数据 |
| HASHEVICT | 30–70% | 1.5–2× prefill / 17× prefill & 2× decoding vs FastGen | decent except 10% budget | 不可逆 eviction；10% cache budget 急降 |
| MorphKV | up to 5× over Full-Attention | up to 4.68× vs SnapKV | comparable to SnapKV | 对 window size / fusion 函数超参敏感 |
| RocketKV | up to 400× | up to 3.7× | negligible loss | 聚焦 decode，prefill 优化有限 |
| KVzip | up to 70% eviction | 2× FlashAttention decoding | negligible loss | reconstruction overhead（多 query 可摊销） |
| Ada-KV | 4× | comparable to SnapKV | ~5% improvement | 仅 layer 内分配，不跨 model |
| KIVI | 2.6× peak | 2.35–3.47× throughput | <2% drop | 单 KV head 模型可能需 4-bit；量化初始开销 |
| KVQuant | 3.7–6.9× | ~1.7× | <0.1 PPL @3-bit | 长上下文训练挑战；dequant 复杂 |
| MiniCache | 41% | ~5× | minimal loss | 仅合并两层；更高压缩受限 |
| PALU | ~50% | 1.89× (RoPE) / 2.91× (quant) | comparable | RoPE key 重建开销 |
| PagedAttention | offload based | 2–4× throughput | lossless | kernel overhead；block table 管理 |
| InfiniGen | offload based | 1.63–32.9× | comparable @ >15% KV size | 需额外 GPU 存 partial weight；专为 CPU-offload 系统 |
| LayerKV | offload based | up to 69× TTFT | lossless | 高负载解码下 throughput 略降 |
| INF2 | offload based | 3.46× throughput / KV I/O >80% 降 | lossless | CPU 协调开销；需 CSD 硬件 |
| KVPR | offload based | 35.8% lower latency / 46.2% higher throughput vs DeepSpeed+HF | lossless | 仅 decoding；限单 GPU / data-parallel |
| Oneiros | offload based | 44.8–82.5% TBT 降 / 20.7–99.3% TTFT 降 / throughput +6.6–86.7% vs vLLM | lossless | 需高 CPU–GPU 带宽（450–900 GB/s，GH200 级） |
| CLO | offload based | 9.3–66.6% throughput vs RetroInfer/InfiniGen | ≤0.42% drop | 近似牺牲少量 cache hit；手动调参；PCIe 4.0 依赖 |
| LinearAttention | O(1) memory | up to 4000× 长序列 | 强合成任务弱复杂任务 | feature map kernel 敏感；reasoning 精度差 |
| Log-Linear | O(log T) memory | 3× | 优于 linear 弱于 full | 性能 gap；engineering 复杂 |
| LLA | similar to softmax | faster than softmax | outperforms softmax & linear (associative/regression) | trades speedups for accuracy |
| KIMI | up to 75% KV | up to 6×（§5.1: 6.3×）@1M | outperforms full attention | kernel 依赖；需 retrain |
| FlexGen | up to 10× | 40–100× vs DeepSpeed-Zero | negligible @4-bit | 高延迟；PCIe/Disk 带宽瓶颈；小 batch 不足 |
| Q-Hitter | up to 20× | up to 33× vs HF Accelerate | full preservation | quantization error 计算与 dequant 开销 |
| ShadowKV | 6× GPU memory | 3.04× throughput | high until sparse budget <1.56% | 部分依赖 PCIe 带宽（Figure 13 双界设计） |
| TailorKV | ~73.8% GPU | 8–18× vs standard offloading | near lossless | prefill 瓶颈；系统复杂（layer-specific 双 regime） |

## 与同类对比

与 [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]（arXiv:2412.19442v3, PolyU/HKUST/HUST/CUHK/NTU, 30 Jul 2025）构成姊妹篇对照：

| 维度 | 本文（Xu et al., Dell, 2026-03） | 姊妹 survey（Li et al., 2025-07） |
|---|---|---|
| **分类轴** | 五方向（Eviction / Compression / Hybrid Memory / New Attention / Combination）按"优化目标 + trade-off 类型"分（Figure 5 p.5） | 三级（Token-level / Model-level / System-level）按"是否改架构/是否动系统底层"分 |
| **覆盖方法数** | 36 个代表方法，深机制解释 | ~150 个方法，机制级布尔对照表 12 张 |
| **表格风格** | Tab.1–6：方向→trade-off→good-for；Tab.2/3/4/5 各方向一张机制表；Tab.6 性能数字总表 | Tab.2–12：每个叶子子类一张布尔特性矩阵；Tab.13/14 benchmark + 18 指标 |
| **图示风格** | Figure 1–14 偏 mechanism 示意（autoregressive/dataflow/attention matrix/taxonomy/H2O 稀疏模式/SnapKV 流程/PALU 投影/vLLM 系统/InfiniGen prefetch/linear vs log-linear 树/ShadowKV 双界/TailorKV 分层） | 偏 taxonomy 树与对照表，机制图较少 |
| **最强贡献** | §5 场景→方法决策矩阵 + 反向 guidance（不选什么） | 三级 taxonomy 正交轴 + 每子类精细布尔对照 + 文本+多模态 benchmark 全集 |
| **视角** | inference scalability / practitioner-facing 部署映射 | academic taxonomy / mechanism-level 对照 |
| **独特覆盖** | New Attention（linear/log-linear/LLA/KIMI）独立成类（Figure 12 p.15）；Combination Methods 独立成类；硬件感知（INF2 CSD、Oneiros GH200）；7 场景映射 | Model-level 把 MQA/GQA/CLA/MLA/FLASH/Infini-Attention/YOCO + non-transformer (RWKV/Mamba/RetNet) 分得很细；System-level 把 vLLM/vTensor/LeanKV/eLLM/Apt-Serve/ChunkAttention/MemServe/FlashForge + DistServe prefill/decode 分离 + HeadInfer head-wise offloading 列得全；评测维更全 |
| **重叠区** | SnapKV/H2O/NACL/Ada-KV/KIVI/KVQuant/MiniCache/PALU/PagedAttention/InfiniGen/LayerKV/FlexGen/ShadowKV 等方法两 survey 都覆盖 | 同左 |
| **互补用法** | 选方法前先查本文 §5 场景表做 deployment scoping，再查姊妹 survey Tab.2–12 做机制级细节对照 | 反之，先查姊妹 survey 三级 taxonomy 定位子类，再查本文 §5 确认该子类是否适配目标场景 |

简言之：**本文偏"何时用哪类"（when/where），姊妹 survey 偏"它到底怎么工作 + 与同类机制级差异在哪"（how/what）**。两篇合起来形成 KV cache 优化的"决策 + 机制"双视图。本文 Figure 6 右下图的 accuracy-vs-memory 曲线、Figure 13 的 ShadowKV GPU/CPU 双界、Figure 12 的 linear vs log-linear 树形对比，都是姊妹 survey 文字描述未能可视化的机制图。

## 跨论文关系（→ MOC 谱系）

- **Hybrid Memory 谱系** — [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]：本文 §3.3 Figure 10（p.11）的 PagedAttention 即 vLLM [22]，是 Hybrid Memory 方向的奠基方法，Tab.4/Tab.6 中 vLLM 2–4× throughput / lossless 是该方向的性能基准；Figure 10 M3 解读的 Block table + CPU/GPU Block Allocator 双分配器 + Scheduler-Worker 解耦架构是该方向的系统模板。
- **KV cache 中心化分离架构** — [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]：Mooncake 把 KV cache 作为 first-class disaggregated 资源，与本文 §3.3 的 PagedAttention/InfiniGen（Figure 11 p.12）/CLO "KV 在 GPU/CPU 间调度"思路一脉相承，可视为本文 Hybrid Memory 方向在数据中心规模的延伸。
- **结构化程序执行** — [[sglang-efficient-execution-of-structured-language-models-programs]]：SGLang 的 RadixAttention 共享 prefix KV 与本文 §3.3 PagedAttention（Figure 10）的 prompt block 共享、copy-on-write 机制同源；姊妹 survey 的 System-level prefix-aware 子类把两者并列。
- **RAG 知识融合** — [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]：CacheBlend 复用 RAG 检索的 KV cache，与本文 §5.5 multi-turn 场景下 KVzip "overhead amortizable across queries" / ShadowKV "low-rank 子空间跨 turn 共享" 思路互补——前者跨 query 复用，后者跨 turn 复用。
- **稀疏注意力跨层索引复用** — [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]：与本文 §3.3 Figure 11（p.12）InfiniGen [23] "Partial Q 预测下一层 KV" + CLO [28] "query 相邻步相似度复用" 同属"用索引/预测减少 KV 传输"的家族，IndexCache 把索引跨层复用做到了极致。
- **跨数据中心 KV** — [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]：把 prefill 当服务、KV cache 跨数据中心迁移，是本文 §3.3 Hybrid Memory 方向"改变 KV 存在哪"思路的跨数据中心外推。
- **KV 压缩 head 共享** — [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]：GQA 通过 head 共享 KV 从结构源头减小 cache，是本文 §2.2 Figure 3 "70B-GQA 0.31 MB/token" 的来源；与 §3.2 量化/低秩正交，可叠加。
- **MLA 低秩 KV** — [[deepseek-v3-technical-report]]：DeepSeek 的 Multi-head Latent Attention 把 KV 压到低秩 latent，与本文 §3.2 Figure 9（p.9）PALU [19] SVD 低秩 projection、§3.5 Figure 13（p.17）ShadowKV [35] pre-RoPE key SVD 同属低秩压缩家族；姊妹 survey 把 MLA 列在 Model-level Architecture Alteration。
- **百万 token 长上下文** — [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]：DeepSeek-V4 的百万 token context intelligence 与本文 §5.1 "long-context >1M single request" 场景直接对应，是 KIMI Linear [32]（§3.4, 75% KV reduction @1M）之外另一条 native 长上下文路径。
- **姊妹 survey** — [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]：见上方"与同类对比"节，本文是其在部署映射维度的互补。

## 局限与边界

1. **性能数字非自测，均引自原论文**：Tab.6 的内存/速度/精度数字全部来自各方法原论文自报（§4 表注无统一评测协议），跨方法不可直接横向比较——不同模型、不同上下文长度、不同 batch size 下数字差异巨大。读者应视为"量级参考"而非"基准对比"。Figure 6 右下图的 accuracy-vs-memory 曲线虽同图对比 H2O/Dynamic/Static，但也仅是该图原作者设定，非本文自评。

2. **覆盖方法数有限（36 个）**：相比姊妹 survey 的 ~150 个方法，本文刻意走"middle-ground, 深机制解释"路线，但代价是不少重要方法未被收录——如 Quest、PQCache、SparQ、RetrievalAttention、DuoAttention、PyramidKV、H2O 之外的 Scissorhands/StreamingLLM/LM-Infinite、MLA（仅在 Tab.5 KIMI 行提及 Multi-Head Latent Attention 但未单独展开）、Infini-Attention、YOCO、CLA/MLKV 等结构性 KV 共享方法完全缺席。GQA 仅作为 Figure 3 70B-GQA 的背景出现，未作为优化方法讨论。

3. **New Attention 方向偏窄**：§3.4 只收 4 个方法（Linear / Log-Linear / LLA / KIMI），Figure 12（p.15）仅对比 linear 与 log-linear 两类结构，non-transformer 路线（Mamba/RWKV/RetNet）完全缺席，而姊妹 survey §5.3 把这些单列。本文的"New Attention"实际只覆盖 linear attention 家族。

4. **场景映射偏定性，无量化边界**：§5.1–5.8 的推荐是基于机制特性的定性推理，未给"在多大 context length / 多大 batch / 多大显存下方法 A 优于方法 B"的量化阈值。例如 §5.3 说"Oneiros 比 vLLM 好"（86.7%↑），但未说在何种 KV 压力/带宽下 vLLM 反而更优；Oneiros 需 450–900 GB/s 带宽，低于此阈值时性能如何退化未述。

5. **未覆盖 distributed / 跨节点 KV 协调**：本文 §3.3 Figure 10（p.11）的 Hybrid Memory 主要关注单机 GPU/CPU/SSD 三级（vLLM 多 Worker 是 data-parallel 而非 tensor-parallel KV 协调），未深入 tensor-parallel / pipeline-parallel 下的 KV cache 跨节点传输与协调（如 Mooncake、DistServe 的 prefill/decode 物理分离），这部分是数据中心部署的核心问题，姊妹 survey §6 的 Distributed 维度覆盖更全。

6. **时效性与引用异常**：本文 arXiv:2603.20397v1 标注 20 Mar 2026（编号 2603 暗示 2026-03），引用 [7] GPT-5、[8] Llama 4 作为 context length 膨胀例证，但部分引用编号存在异常：[4] von Laszewski "AI Benchmark Democratization and Carpentry"（arXiv:2512.11588）与 KV cache 主题不直接相关，疑为引用错误；[30] Log-Linear 标注 2026 但 arXiv:2506.04761 实为 2025-06；[31] LLA 标注 2025 但 arXiv:2510.01450 编号暗示 2025-10；[32] KIMI Linear 标注 2025 但 arXiv:2510.26692 同样暗示 2025-10。引用列表需谨慎核对。

7. **Combination 方向未给组合原则**：§3.5 只列 4 个已存在的组合框架（Figure 13 ShadowKV / Figure 14 TailorKV 等），未给"如何系统性选择哪几种 single technique 组合"的设计原则——这正是 §6 总结里点名的"adaptive, multi-stage optimization pipelines"未来方向，但本文未给出该方向的初步框架。

8. **评测维度薄弱**：完全未收录 benchmark（姊妹 survey §7 有 13 文本 + 9 多模态 benchmark + 18 指标），也未给 reproducibility 协议（模型版本/上下文长度/硬件/batch 配置）。读者无法据此复现任何方法对比。

9. **硬件视角偏 Dell-friendly**：作者来自 Dell Technologies，§5.8 Hardware-Specific 场景对 GH200/Grace Hopper（Oneiros、CLO）与 CSD（INF2）着墨较多，但未覆盖 AMD MI300 / Intel Gaudi / 国产 ASIC（如 Ascend）等异构硬件下的 KV cache 优化差异——这一视角与仓库内 [[ascend-950-npu-architecture-whitepaper]] 形成空白互补。
