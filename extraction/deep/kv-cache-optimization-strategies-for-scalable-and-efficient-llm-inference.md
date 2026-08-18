# KV Cache Optimization Strategies Survey — 技术点深读（DEEP 2026-08-18）

> Source: `extraction/fulltext/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference.txt` (arXiv:2603.20397v1, 20 Mar 2026). Yichun Xu, Navjot K. Khaira, Tejinder Singh (Dell Technologies). Survey — five-direction taxonomy paper mapping 36 representative methods to 7 deployment scenarios. Sister survey to [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] (the PolyU/HKUST 三级 taxonomy paper); this one偏 inference scalability & practitioner-facing deployment mapping, the other偏 academic taxonomy + 12 mechanism-level tables.

## 核心问题

本文攻击的是一个 **部署侧的实践性问题**：KV cache 的线性内存增长（§2.2，式 1–2：`KVper token = 2 × H × D × B × L`，`KVcache size = KVper token × ContextLength`）在上下文窗口从数千 token 扩张到百万级（§1, §3 引言引 GPT-5 / Llama 4）时，对 GPU 显存容量、显存带宽、推理吞吐同时形成 critical bottleneck（§2.2, Fig.3：7B 模型在 128K 上下文下 KV cache ≈64 GB，已超 A100 80GB 上限）。

不同于单篇方法论文"只攻一处"或既有 survey "broad but shallow"（§1 自述），本文提供 **middle-ground perspective**：
1. 把 KV cache 优化系统性归入 **五大方向**（Cache Eviction / Cache Compression / Hybrid Memory / New Attention Mechanism / Combination Methods, §2.4 Fig.5, Tab.1），每个方向给机制级深度解释而非点名；
2. 再把每个方向的方法 **映射到 7 个实际部署场景**（§5.1–5.8：long-context single request / minimal model modification / high-throughput serving / edge devices / multi-turn conversations / prefill-heavy / accuracy-critical reasoning / hardware-specific），给从业者"在该约束下选哪一类"的可执行答案。

核心结论（§6）：**没有任何单一技术 dominate 所有 setting**——最优策略取决于 context length / hardware constraints / workload characteristics，未来方向是 **adaptive, multi-stage optimization pipelines**。

## 关键创新点

作为 survey，"创新点"指其分类骨架与部署映射贡献：

1. **五方向 taxonomy（§2.4, Fig.5, Tab.1）——以"系统级优化目标"为切分轴**
   - 机制：不同于姊妹 survey 的 Token/Model/System 三级轴，本文按"优化目标 + trade-off 类型"分五类——Cache Eviction（降 footprint 与 decoding latency，代价是 accuracy）、Cache Compression（降 size 提 throughput，代价是 dequant/reconstruction overhead）、Hybrid Memory（降 TTFT 提系统效率，代价是硬件依赖与管理复杂度）、New Attention（降计算复杂度提速，代价是 accuracy 与 retraining）、Combination（平衡 throughput/latency，代价是设计复杂度）。
   - 效果：每类直接绑定 "Good for" 部署场景（Tab.1 末列），把"方法—trade-off—场景"三段式打通。这是本文与姊妹 survey 最大差异：后者偏 mechanism-level对照表，本文偏 deployment-scenario mapping。

2. **Cache Eviction 的 9 方法精细对比（§3.1, Tab.2）——按 eviction phase 与 importance signal 分轴**
   - 机制：H2O [1]（accumulated attention, decoding）→ SnapKV [2]（observation window voting + 1D pooling, after prefill）→ NACL [9]（proxy-token + random 单次 prefill eviction, O(1) 单 shot）→ InfiniPot [10]（Continual Context Distillation, CaP + NuC 双指标, prefill）→ HASHEVICT [11]（pre-attention LSH + Hamming distance, decoding, attention-free）→ MorphKV [13]（recent attention pattern + Sum/Max Fusion, decoding）→ RocketKV [14]（SnapKV 粗驱逐 + Hybrid Sparse Attention 细检索, 两阶段）→ KVzip [15]（query-agnostic, 自监督 context reconstruction 评分, prefill）→ Ada-KV [3]（head-wise adaptive budget, plug-and-play with SnapKV）。
   - 效果：Tab.2 + Tab.6 给出内存/速度/精度三维权衡——RocketKV up to 400× 压缩（§4 Tab.6）；HASHEVICT 30–70% 压缩 + 1.5–2× prefill speedup；Ada-KV 4× cache reduction + ~5% 精度提升。明确"固定 budget 均匀分配到所有 head"是传统方法的 key limitation，Ada-KV 把"sparse head 预算让给 dispersed head"形成理论 eviction loss 上界（§3.1 末）。

3. **Cache Compression 的四象限（§3.2, Tab.3）——quantization / cross-layer merge / low-rank projection**
   - 机制：KIVI [5]（key per-channel + value per-token 非对称量化 + group/residual 动态合并，2-bit plug-and-play）→ KVQuant [20]（per-channel pre-RoPE + sensitivity-weighted non-uniform + dense-and-sparse outlier 分离 + attention-sink-aware，支持 10M token 上下文）→ MiniCache [21]（跨相邻层 KV 相似度，SLERP 合并 + 方向/幅度/角度存储重建）→ PALU [19]（SVD 把 W ≈ A×B，缓存 latent H，Matrix Fusion 离线融合 B，对 RoPE key 用 custom GPU kernel 动态重建；G-LRD 折中 joint vs per-head decomposition）。
   - 效果：Tab.6 量化数字——KIVI 2.6× peak memory / 2.35–3.47× throughput / <2% accuracy drop；KVQuant 3.7–6.9× memory / <0.1 perplexity degradation @3-bit；MiniCache 41% memory reduction / ~5× throughput；PALU ~50% KV 压缩 / 1.89× (RoPE)–2.91× (with quant)。明确 KVQuant 的 Pre-RoPE 量化是 KIVI 之外的独立创新——RoPE 旋转后量化更难，pre-RoPE 保持结构完整性（§3.2）。

4. **Hybrid Memory 七系统的硬件感知谱系（§3.3, Tab.4）——从 paging 到 near-storage 计算**
   - 机制：PagedAttention [22]（OS virtual memory 启发，KV block + block table + copy-on-write，并行采样共享 prompt block）→ InfiniGen [23]（Partial Q = `X(layer)·M·W_Q^(layer+1)` 预测下一层所需 KV，CPU→GPU 预取与计算重叠）→ LayerKV [24]（层粒度 offload，选最小 GPU 层数使 `offload time ≤ prefill time`，SLO-aware TPOT scheduler）→ INF2 [25]（Computational Storage Devices with FPGA/ASIC，attention-near-storage，PCIe private switch，GPU 并行做 MLP）→ KVPR [26]（partial KV 重算与传输重叠，profiling 决定 row-wise (latency) / column-wise (throughput) 调度）→ Oneiros [27]（parameter remapping：解码期把 inactive model 参数 offload 出 GPU 腾出 KV 空间，逐层均匀分布 remapped layer 隐藏传输）→ CLO [28]（query 相邻步高相似度→复用上一轮 KV；低相似度则 InfiniGen 式 prefetch；GDRCopy zero-copy engine；critical head 永驻 GPU）。
   - 效果：Tab.6——PagedAttention 2–4× throughput lossless；LayerKV up to 69× TTFT 改善；INF2 3.46× throughput / KV I/O 降低 >80%；Oneiros 44.8–82.5% TBT 降低 / 6.6–86.7% throughput 提升 vs vLLM；CLO 9.3–66.6% throughput 提升 vs RetroInfer/InfiniGen。

5. **New Attention 的复杂度阶梯（§3.4, Tab.5）——O(N²) → O(N log N) → O(N)**
   - 机制：Softmax O(N²)/O(T)/O(T) → Linear (Transformers-are-RNNs [29]，kernel feature map `φ(·)` 把 `softmax(q·k)` 近似为 `φ(q)·φ(k)`，递归式累积 S_i，O(N)/O(1)/O(1)) → Log-Linear [30]（Fenwick tree 桶，每桶 summary matrix S_t^(ℓ)，O(N log N)/O(log N)/O(log N)) → Local Linear Attention [31]（把 attention 类比为 regression，softmax=local constant, linear=global linear, LLA=local linear regression，O(N²)/~O(N)/O(N)) → KIMI Linear [32]（Kimi Delta Attention KDA，forget gate α + update rate β 双门控，`St = (I − βt·kt·kt^T)·Diag(αt)·St−1 + βt·kt·vt^T`，与 full attention 3:1 hybrid ratio）。
   - 效果：Tab.6——LinearAttention up to 4000× 长序列提速；KIMI up to 75% KV reduction + up to 6× throughput @1M context，且作者称 outperforms full attention；Log-Linear 3× speedup；LLA 在 associative/regression 任务上 outperforms softmax & linear。关键结论：linear 类方法需 full retrain，accuracy-critical reasoning 仍落后 full attention，是"未来 transformer 继任者"方向而非 drop-in 优化（§6）。

6. **Combination Methods 的四框架（§3.5）——sparsity × quantization × offload**
   - 机制：FlexGen [33]（weights/activations/KV 跨 GPU/CPU/disk 划分，linear programming 解最优 placement，4-bit group-wise 量化，zig-zag block scheduling 最大化 weight reuse）→ Q-Hitter [34]（attention score + quantization error 双指标统一打分 S，选 top-K 量化存储，sparse-quantized KV）→ ShadowKV [35]（pre-RoPE key 强低秩→SVD 压缩存 GPU；value 不低秩→offload CPU；post-RoPE key chunk landmark 检测 outlier 全存 GPU；decoding 期 landmark 估计相关 chunk，按需 fetch value）→ TailorKV [36]（layer-specific：浅层 attention 分散→quantization-friendly 激进量化存 GPU；深层 attention 集中→sparsity-friendly offload CPU 动态 top-K fetch；double buffering 隐藏传输）。
   - 效果：Tab.6——FlexGen up to 10× memory / 40–100× throughput vs DeepSpeed-Zero-Inference；Q-Hitter up to 20× memory / 33× vs HF Accelerate；ShadowKV 6× GPU memory / 3.04× throughput；TailorKV ~73.8% GPU memory reduction / 8–18× faster than standard offloading / near lossless。

7. **场景-方法决策矩阵（§5.1–5.8）——本文最强 practitioner 贡献**
   - 机制：把 7 类部署场景（long-context single request / minimal model modification / high-throughput serving / edge devices / multi-turn conversations / prefill-heavy / accuracy-critical reasoning）+ 1 类 hardware-specific，逐一映射到推荐方法与禁忌方法，并给反例（如 H2O 不适合 multi-turn 因永久丢弃未来 turn 可能需要的 token；FlexGen 不适合 interactive dialogue；linear/log-linear 不适合 minimal model modification 与 accuracy-critical reasoning）。
   - 效果：这是姊妹 survey 未显式提供的"反向 guidance"——不只说"选什么"，更说"不选什么"。

## 表格（原文结构化）

### 表 A — 五方向 taxonomy 与仓库 deep note 对照（据 Fig.5, Tab.1, Tab.2/3/4/5, §3 重构）

| 方向 | 机制 | 代表方法（原文编号） | Phase | 仓库对应 deep note |
|---|---|---|---|---|
| Cache Eviction (§3.1, Tab.2) | 累积 attention / observation window 投票 / proxy-token + random / continual distillation / LSH / correlation-aware / 两阶段 / reconstruction / head-wise budget | H2O[1], SnapKV[2], NACL[9], InfiniPot[10], HASHEVICT[11], MorphKV[13], RocketKV[14], KVzip[15], Ada-KV[3] | decoding / after-prefill / prefill 混 | — |
| Cache Compression (§3.2, Tab.3) | 非对称量化 / non-uniform + pre-RoPE / cross-layer SLERP merge / SVD low-rank projection | KIVI[5], KVQuant[20], MiniCache[21], PALU[19] | decoding | — |
| Hybrid Memory (§3.3, Tab.4) | paging / 预测 prefetch / 层粒度 offload / near-storage 计算 / 重算-传输重叠 / parameter remapping / query 相似度复用 | PagedAttention[22], InfiniGen[23], LayerKV[24], INF2[25], KVPR[26], Oneiros[27], CLO[28] | prefill + decoding | [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] |
| New Attention (§3.4, Tab.5) | kernel linear / Fenwick tree log-linear / local linear regression / KDA + 3:1 hybrid | LinearAttention[29], Log-Linear[30], LLA[31], KIMI Linear[32] | training-time | — |
| Combination (§3.5) | LP offload + 4-bit / sparse-quantized / low-rank key + offload value / layer-specific quant vs sparsity | FlexGen[33], Q-Hitter[34], ShadowKV[35], TailorKV[36] | prefill + decoding | — |

### 表 B — 部署场景 → 推荐方法矩阵（据 §5.1–5.8 重构）

| 场景 | 推荐 | 禁忌/不推荐 |
|---|---|---|
| Long-context >1M single request (§5.1) | Eviction + Compression 组合；KIMI (75% KV reduction @1M) | — |
| Minimal model modification (§5.2) | Ada-KV / SnapKV / KIVI (plug-and-play, tuning-free) | Linear / Log-Linear / LLA / KIMI (需 retrain + 改架构) |
| High-throughput serving (§5.3) | PagedAttention (vLLM), Oneiros, ShadowKV；单 GPU 极端场景 FlexGen / Q-Hitter | — |
| Edge / memory-limited (§5.4) | InfiniPot (mobile/NPU), TailorKV (8B@128k on RTX 3090) | PagedAttention (需 high-end GPU), Oneiros (需 450–900 GB/s 带宽) |
| Multi-turn conversations (§5.5) | RocketKV-MT, KVzip (overhead amortizable across queries), ShadowKV (multi-turn capability) | H2O (永久丢弃未来 turn 所需 token), FlexGen (latency 不适合交互) |
| Prefill-heavy (§5.6) | NACL (单次 prefill eviction), HASHEVICT (1.5–2× prefill speedup), LayerKV (69× TTFT), MiniCache, CLO (parallel prefill + speculative prefetch) | — |
| Accuracy-critical reasoning (§5.7) | Hybrid Memory (PagedAttention 等 lossless) | Eviction / Compression / Linear / Log-Linear (均有精度代价) |
| Hardware-specific (§5.8) | GH200 高 PCIe 带宽→Oneiros / CLO；CSD (FPGA/ASIC)→INF2；单 GPU 限内存→FlexGen | — |

### 表 C — 性能数字总览（据 Tab.6 重构，按内存/速度/精度三维权衡）

| 方法 | 内存 | 速度 | 精度 | 关键 trade-off |
|---|---|---|---|---|
| H2O | 5–10× reduction | 29× throughput / ≤1.9× lower latency vs FlexGen | comparable | 累积 attention bias；heavy-hitter 丢失风险 |
| SnapKV | 8.2× | 3.6× generation | comparable | 不优化 prefill；不能扩模型固有 context limit |
| RocketKV | up to 400× | 3.7× | negligible loss | 聚焦 decode，prefill 优化有限 |
| KVzip | 70% eviction | 2× FlashAttention decoding | negligible | reconstruction overhead（多 query 可摊销） |
| Ada-KV | 4× | comparable to SnapKV | ~5% improvement | 仅 layer 内分配，不跨 model |
| KIVI | 2.6× peak | 2.35–3.47× throughput | <2% drop | 单 KV head 模型可能需 4-bit；量化初始开销 |
| KVQuant | 3.7–6.9× | ~1.7× | <0.1 PPL @3-bit | 长上下文训练挑战；dequant 复杂 |
| MiniCache | 41% | ~5× | minimal loss | 仅合并两层；更高压缩受限 |
| PALU | ~50% | 1.89× (RoPE) / 2.91× (quant) | comparable | RoPE key 重建开销 |
| PagedAttention | offload based | 2–4× throughput | lossless | kernel overhead；block table 管理 |
| LayerKV | offload based | up to 69× TTFT | lossless | 高负载解码下 throughput 略降 |
| INF2 | offload based | 3.46× throughput / KV I/O >80% 降 | lossless | CPU 协调开销；需 CSD 硬件 |
| Oneiros | offload based | 44.8–82.5% TBT 降 / 20.7–99.3% TTFT 降 / throughput +6.6–86.7% vs vLLM | lossless | 需高 CPU–GPU 带宽（GH200 级） |
| CLO | offload based | 9.3–66.6% throughput vs RetroInfer/InfiniGen | ≤0.42% drop | 近似牺牲少量 cache hit；手动调参；PCIe 4.0 依赖 |
| KIMI | up to 75% KV | up to 6× @1M | outperforms full attention | kernel 依赖；需 retrain |
| FlexGen | up to 10× | 40–100× vs DeepSpeed-Zero | negligible @4-bit | 高延迟；PCIe/Disk 带宽瓶颈；小 batch 不足 |
| Q-Hitter | up to 20× | up to 33× vs HF Accelerate | full preservation | quantization error 计算与 dequant 开销 |
| ShadowKV | 6× GPU memory | 3.04× throughput | high until sparse budget <1.56% | 部分依赖 PCIe 带宽 |
| TailorKV | ~73.8% GPU | 8–18× vs standard offloading | near lossless | prefill 瓶颈；系统复杂 |

## 与同类对比

与 [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]（arXiv:2412.19442v3, PolyU/HKUST/HUST/CUHK/NTU, 30 Jul 2025）构成姊妹篇对照：

| 维度 | 本文（Xu et al., Dell, 2026-03） | 姊妹 survey（Li et al., 2025-07） |
|---|---|---|
| **分类轴** | 五方向（Eviction / Compression / Hybrid Memory / New Attention / Combination）按"优化目标 + trade-off 类型"分 | 三级（Token-level / Model-level / System-level）按"是否改架构/是否动系统底层"分 |
| **覆盖方法数** | 36 个代表方法，深机制解释 | ~150 个方法，机制级布尔对照表 12 张 |
| **表格风格** | Tab.1–6：方向→trade-off→good-for；Tab.2/3/4/5 各方向一张机制表；Tab.6 性能数字总表 | Tab.2–12：每个叶子子类一张布尔特性矩阵；Tab.13/14 benchmark + 18 指标 |
| **最强贡献** | §5 场景→方法决策矩阵 + 反向 guidance（不选什么） | 三级 taxonomy 正交轴 + 每子类精细布尔对照 + 文本+多模态 benchmark 全集 |
| **视角** | inference scalability / practitioner-facing 部署映射 | academic taxonomy / mechanism-level 对照 |
| **独特覆盖** | New Attention（linear/log-linear/LLA/KIMI）独立成类；Combination Methods 独立成类；硬件感知（INF2 CSD、Oneiros GH200）；7 场景映射 | Model-level 把 MQA/GQA/CLA/MLA/FLASH/Infini-Attention/YOCO + non-transformer (RWKV/Mamba/RetNet) 分得很细；System-level 把 vLLM/vTensor/LeanKV/eLLM/Apt-Serve/ChunkAttention/MemServe/FlashForge + DistServe prefill/decode 分离 + HeadInfer head-wise offloading 列得全；评测维更全 |
| **重叠区** | SnapKV/H2O/NACL/Ada-KV/KIVI/KVQuant/MiniCache/PALU/PagedAttention/InfiniGen/LayerKV/FlexGen/ShadowKV 等方法两 survey 都覆盖 | 同左 |
| **互补用法** | 选方法前先查本文 §5 场景表做 deployment scoping，再查姊妹 survey Tab.2–12 做机制级细节对照 | 反之，先查姊妹 survey 三级 taxonomy 定位子类，再查本文 §5 确认该子类是否适配目标场景 |

简言之：**本文偏"何时用哪类"（when/where），姊妹 survey 偏"它到底怎么工作 + 与同类机制级差异在哪"（how/what）**。两篇合起来形成 KV cache 优化的"决策 + 机制"双视图。

## 跨论文关系（→ MOC 谱系）

- **Hybrid Memory 谱系** — [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]：本文 §3.3 的 PagedAttention 即 vLLM [22]，是 Hybrid Memory 方向的奠基方法，Tab.4/Tab.6 中 vLLM 2–4× throughput / lossless 是该方向的性能基准。
- **KV cache 中心化分离架构** — [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]：Mooncake 把 KV cache 作为 first-class disaggregated 资源，与本文 §3.3 的 PagedAttention/InfiniGen/CLO "KV 在 GPU/CPU 间调度"思路一脉相承，可视为本文 Hybrid Memory 方向在数据中心规模的延伸。
- **结构化程序执行** — [[sglang-efficient-execution-of-structured-language-models-programs]]：SGLang 的 RadixAttention 共享 prefix KV 与本文 §3.3 PagedAttention 的 prompt block 共享、copy-on-write 机制同源；姊妹 survey 的 System-level prefix-aware 子类把两者并列。
- **RAG 知识融合** — [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]：CacheBlend 复用 RAG 检索的 KV cache，与本文 §5.5 multi-turn 场景下 KVzip "overhead amortizable across queries" / ShadowKV "multi-turn capability" 思路互补——前者跨 query 复用，后者跨 turn 复用。
- **稀疏注意力跨层索引复用** — [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]：与本文 §3.3 InfiniGen [23] "Partial Q 预测下一层 KV" + CLO [28] "query 相邻步相似度复用" 同属"用索引/预测减少 KV 传输"的家族，IndexCache 把索引跨层复用做到了极致。
- **跨数据中心 KV** — [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]：把 prefill 当服务、KV cache 跨数据中心迁移，是本文 §3.3 Hybrid Memory 方向"改变 KV 存在哪"思路的跨数据中心外推。
- **KV 压缩 head 共享** — [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]：GQA 通过 head 共享 KV 从结构源头减小 cache，是本文 §2.2 Fig.3 "70B-GQA 0.31 MB/token" 的来源；与 §3.2 量化/低秩正交，可叠加。
- **MLA 低秩 KV** — [[deepseek-v3-technical-report]]：DeepSeek 的 Multi-head Latent Attention 把 KV 压到低秩 latent，与本文 §3.2 PALU [19] SVD 低秩 projection、§3.5 ShadowKV [35] pre-RoPE key SVD 同属低秩压缩家族；姊妹 survey 把 MLA 列在 Model-level Architecture Alteration (§5.2.1)。
- **百万 token 长上下文** — [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]：DeepSeek-V4 的百万 token context intelligence 与本文 §5.1 "long-context >1M single request" 场景直接对应，是 KIMI Linear [32] 之外另一条 native 长上下文路径。
- **姊妹 survey** — [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]：见上方"与同类对比"节，本文是其在部署映射维度的互补。

## 局限与边界

1. **性能数字非自测，均引自原论文**：Tab.6 的内存/速度/精度数字全部来自各方法原论文自报（§4 表注无统一评测协议），跨方法不可直接横向比较——不同模型、不同上下文长度、不同 batch size 下数字差异巨大。读者应视为"量级参考"而非"基准对比"。

2. **覆盖方法数有限（36 个）**：相比姊妹 survey 的 ~150 个方法，本文刻意走"middle-ground, 深机制解释"路线，但代价是不少重要方法未被收录——如 Quest、PQCache、SparQ、RetrievalAttention、DuoAttention、PyramidKV、H2O 之外的 Scissorhands/StreamingLLM/LM-Infinite、MLA（仅在 Tab.5 KIMI 行提及 Multi-Head Latent Attention 但未单独展开）、Infini-Attention、YOCO、CLA/MLKV 等结构性 KV 共享方法完全缺席。GQA 仅作为 Fig.3 70B-GQA 的背景出现，未作为优化方法讨论。

3. **New Attention 方向偏窄**：§3.4 只收 4 个方法（Linear / Log-Linear / LLA / KIMI），non-transformer 路线（Mamba/RWKV/RetNet）完全缺席，而姊妹 survey §5.3 把这些单列。本文的"New Attention"实际只覆盖 linear attention 家族。

4. **场景映射偏定性，无量化边界**：§5.1–5.8 的推荐是基于机制特性的定性推理，未给"在多大 context length / 多大 batch / 多大显存下方法 A 优于方法 B"的量化阈值。例如 §5.3 说"Oneiros 比 vLLM 好"，但未说在何种 KV 压力/带宽下 vLLM 反而更优。

5. **未覆盖 distributed / 跨节点 KV 协调**：本文 §3.3 的 Hybrid Memory 主要关注单机 GPU/CPU/SSD 三级，未深入 tensor-parallel / pipeline-parallel 下的 KV cache 跨节点传输与协调（如 Mooncake、DistServe 的 prefill/decode 物理分离），这部分是数据中心部署的核心问题，姊妹 survey §6 的 Distributed 维度覆盖更全。

6. **时效性**：本文 arXiv:2603.20397v1 标注 20 Mar 2026（实际编号 2603 暗示 2026-03），引用 [7] GPT-5、[8] Llama 4 作为 context length 膨胀例证，但部分引用编号存在异常（如 [4] von Laszewski "AI Benchmark Democratization" 与 KV cache 主题不直接相关，疑为引用错误；[30] Log-Linear 标注 2026 但 arXiv:2506.04761 实为 2025-06；[31] LLA 标注 2025 但 arXiv:2510.01450 编号暗示 2025-10），引用列表需谨慎核对。

7. **Combination 方向未给组合原则**：§3.5 只列 4 个已存在的组合框架，未给"如何系统性选择哪几种 single technique 组合"的设计原则——这正是 §6 总结里点名的"adaptive, multi-stage optimization pipelines"未来方向，但本文未给出该方向的初步框架。

8. **评测维度薄弱**：完全未收录 benchmark（姊妹 survey §7 有 13 文本 + 9 多模态 benchmark + 18 指标），也未给 reproducibility 协议（模型版本/上下文长度/硬件/batch 配置）。读者无法据此复现任何方法对比。

9. **硬件视角偏 Dell-friendly**：作者来自 Dell Technologies，§5.8 Hardware-Specific 场景对 GH200/Grace Hopper 着墨较多，但未覆盖 AMD MI300 / Intel Gaudi / 国产 ASIC（如 Ascend）等异构硬件下的 KV cache 优化差异——这一视角与仓库内 [[ascend-950-npu-architecture-whitepaper]] 形成空白互补。
