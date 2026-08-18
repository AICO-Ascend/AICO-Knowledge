# Kimi Linear: An Expressive, Efficient Attention Architecture — 技术点深读（DEEP 2026-08-18）

> 独立文件，extract_phase1 重跑不丢。深读 = 全文 + 公式 + 图表（M3 caption）+ ablation 交织。
> 论文：Kimi Linear (Kimi Team 技术报告) · arXiv:2510.26692v2 · 48B 总参 / 3B 激活 MoE · 1.4T 预训练 tokens · 6 张 figure

## 核心问题

标准 softmax attention 有**二次时间复杂度 + 线性增长 KV cache**，在 agentic decoding、RL test-time scaling、million-token 上下文场景下是吞吐/内存的核心瓶颈（§1）。线性注意力把复杂度降为线性但**历史质量一直不如 softmax**：expressivity 受限 + finite-state RNN 容量有限，导致长序列 in-context retrieval 与 exact copying 理论上受限 [4,45,104]。混合架构（少量全注意力 + 多数线性）是实用折中，但既往工作**规模有限、缺跨场景全面评测，且未在公平规模下真正超越全注意力**（§1, §7.2）。

Kimi Linear 给出的解：KDA（Kimi Delta Attention）= Gated DeltaNet [111] + **channel-wise 细粒度门控**（类比 GLA [114]）+ **DPLR 变体的定制 chunkwise 算法**；与 Full MLA 全注意力按 **3:1** 均匀交织；首次在 1.4T 同配方公平对比下于**短上下文 / 长上下文 / RL 三场景全面超越全注意力**，同时 KV cache 砍 75%、1M 上下文解码吞吐 6.3×（§1, §5.5）。

## 关键创新点

### 1. KDA = Gated DeltaNet + Channel-wise 细粒度门控（§3, §6.1, Table 7）
- **机制**：GDN [111] 与 Mamba2 [16] 用**粗粒度 head-wise scalar forget gate** αt∈[0,1]（每头一个遗忘率）；KDA 改为 **diagonalized channel-wise gate Diag(αt)∈R^{dk×dk}**（每特征维度独立遗忘率，类比 GLA [114]）。递推式见 Eq.(1)：St = (I − βt·ktk_t^T)·Diag(αt)·St-1 + βt·ktv_t^T。Table 7 把 KDA 与 LA/RetNet/Mamba2/GLA/Comba/RWKV7/GDN 同列于 TTT [90] 框架下的 objective + update rule，KDA 的 objective βt/2·||S̃^Tkt − vt||² 即 decayed state 上的 SGD。
- **效果**：细粒度门控 → 更有效利用有限 RNN 记忆 + 等价于"relax RoPE 正交约束的可学习 multiplicative positional encoding"（§6.1）。Figure 4（p.7, M3）的 Palindrome / MQAR / Stack 三合成任务：KDA 在 256→2048 序列上保持近 100% peak accuracy，GDN 在 2048 处明显下滑，Mamba2（仅 multiplicative decay 无 delta rule）在 Palindrome/Stack 上 >512 token 完全崩溃（0%）；收敛速度 KDA ≈5K steps 即饱和，GDN 慢，Mamba2 不收敛——直接验证"channel-wise 细门控 + delta rule"对长序列 retrieval/state-tracking 的关键作用。

### 2. DPLR 变体 + 定制 chunkwise-parallel 算法（§3.1-3.2, §6.2, Listing 1, Figure 2）
- **机制**：KDA 限定 DPLR 转移矩阵的特化变体（§6.2）：原 DPLR 形式 St = (D − a_t·b_t^T)·St-1 + k_t·v_t^T，KDA 通过 **binding a=b=k**（即 a_t=βt·kt, b_t=kt⊙αt, D=Diag(αt)）将 DPLR 退化为可 factor-out 的 fine-grained multiplicative decay + Householder 风格 delta 更新。配合 WY representation（Comba [40]）/ UT transform（§3.1 Eq.3-9）推导出 chunkwise 算法：inter-block recurrent + intra-block parallel。Appendix B Proposition 1/2 给出 P_r[t]/H_r[t] 的归纳法证明。
- **效果**：对比 Listing 8a (DPLR) vs Listing 8b (KDA) 伪代码：① 删掉 1/Γ 的 secondary chunking 两步（DPLR line 13-16 → KDA line 14-15）；② 进一步去掉 inter-chunk/output 阶段约 3 个 matmul（DPLR line 25-27,31-32 → KDA line 26,29）。**KDA kernel 相对 DPLR 提速约 2×**（§3.2, §6.2）。Figure 2（p.5, M3）实测：batch=1, 16 heads, 2K→64K 输入下 DPLR 时间近似指数增长（64K 处 ~48ms），KDA 在 2K-32K 近乎平坦（~0-8ms）、64K 仅 ~30ms，差距随序列拉长而扩大。

### 3. 3:1 KDA : Full MLA 混合架构 + NoPE（§4, §5.2, §6.1, Figure 3, Table 1）
- **机制**：每 3 层 KDA 夹 1 层 Full MLA（layer-wise inter-layer hybrid，非 head-wise），全程均匀重复（Figure 3 架构图 p.5, M3：KDA 块含 Linear-Conv-L2/Swish 的 q/k/v 投影、低秩 α/β 门控、head-wise RMSNorm + 低秩 Sigmoid output gate、MoE 通道混合）。MLA 层用 **NoPE**（不用 RoPE），把位置编码/recency bias 全部委托给 KDA 承担——KDA 因此成为主 position-aware 算子。Neural parameterization：q,k,v 走 ShortConv+Swish，q/k 加 L2Norm 保 eigenvalue stability；αt 经低秩 W↑_α W↓_α 投影 + decay function f(·)；dk=dv=128。
- **效果**：Table 1（p.7）ablation 给出 Training/Validation PPL——**3:1 最佳（train 9.23 / val 5.65）**；7:1 train 持平但 val 显著劣（5.70）；1:1 val 持平但推理开销高；0:1（纯全注意力）最差（train 9.45 / val 5.77）。组件 ablation：去 output gate→val 5.67；Swish output gate（GDN 默认）→val 5.81 显著劣于 Sigmoid；去 conv 层→val 5.70。§5.2 进一步证明 NoPE 优于 RoPE：Kimi Linear (RoPE) 短上下文持平但长上下文（Table 5）RULER 仅 78.8 < NoPE 84.3——因 RoPE 把强 positional bias 集中在 global 层造成短程偏置过度、长程外推不灵活。

### 4. 公平规模验证 + Scaling Law（§5.3, §5.4, Table 2, Figure 5）
- **机制**：5 个 MoE 检查点（653M/878M/1.1B/1.4B/1.7B activated，Moonlight 架构，8/64 experts，Muon optimizer，ctx=4096，token 38.8B-128B，Table 2），MLA 走 Chinchilla 网格搜索超参，KDA 严格沿用 MLA 配置仅替换 hybrid ratio=3:1。
- **效果**：Figure 5（p.9, M3）log-log 拟合曲线 **MLA: 2.3092·C^−0.0536 vs Kimi Linear: 2.2879·C^−0.0527**，红色曲线全程位于蓝色之下，两条曲线指数相近（平行），等 loss 处 KDA 所需 compute 少 **~1.16×**——架构级效率增益而非调参，且跨 653M-1.7B 规模保持。

### 5. 三场景全面超越 + RL 收敛优势（§5.5, Table 3/4/5, Figure 6）
- **短上下文预训练**（Table 3）：Kimi Linear @ 1.4T 在 BBH 72.9、MMLU 73.8、MMLU-Pro 51.0、TriviaQA 71.7、CRUXEval-I 56.6/O 62.0、CEval 79.5 全面领先 MLA / GDN-H；GSM8K 83.9、MATH 54.7（持平）；EvalPlus 60.2 略低于 GDN-H 63.1。
- **SFT 后**（Table 4）：MMLU 77.0、MMLU-Pro 67.4、MMLU-Redux 80.3、GPQA-Diamond 62.1、AIME 2025 21.3、HMMT 2025 12.5、PolyMath-en 43.6、LiveCodeBench v6 26.0 全面领先；MATH500 81.2 / EvalPlus 61.0 略低。
- **长上下文**（Table 5）：RULER 84.3、RepoQA 68.5、Long Code Arena 37.1、Avg 54.5 均列第一；GDN-H 在长上下文反退到 MLA 之后（51.2 < MLA 52.2），唯 Kimi Linear 保持顶端。
- **RL**（Figure 6 p.12, M3）：Math RL 训练曲线 KDA@1.4T vs MLA@1.4T，(a) train accuracy 全程领先且 gap 扩大；(b) MATH500 test 70-94 区间 Kimi Linear 全程在上；(c) AIME 2025（10-25 区间）gap 最大，Kimi Linear ~22% vs MLA ~19%。证明线性化注意力对 reasoning-intensive 长序列生成的优化动力学更好。

### 6. 效率：KV cache −75%，1M 解码 6.3×（§5.6, Figure 1, Figure 7）
- **机制**：KDA 维持 fixed-size state（dk×dv=128×128 per head），prefill 走 FLOP-intensive chunk kernel（Eq.9），autoregressive 生成切到 recurrent kernel（Eq.2）。Hybrid 模型 I/O-bound 解码理论加速比上限 = 3:1。
- **效果**：Figure 1（p.1, M3）(a) Performance vs Acceleration 散点——RULER 128k 上 Kimi Linear 84.3 处 Pareto 最优，加速 3.98×；MMLU-Pro 4k 上 Kimi Linear 51.0 在相近速度下领先 MLA 47.2。(b) TPOT vs Decoding Length：MLA/GDN-H 曲线陡升，Kimi Linear 近乎平坦，标注 **4.8× @ 256K / 5.7× @ 128K / 6.3× @ 1M**（1.84ms vs MLA 11.48ms）。Figure 7（p.13, M3）单 batch 下 prefill latency 2.6×@512K / 2.9×@1M，TPOT 1.8×@512K / 2.2×@1M；KDA 与 GDN-H prefill 曲线几乎重合（细粒度门控不引入额外 latency）。
- **5.7T 大版本**（Appendix D, Table 8/9）：Kimi-Linear-Instruct @5.7T 在 RULER@1M 达 **94.8**，RULER@128k 95.4，AIME 2025 58.6，MATH500 94.6，全面碾压 Moonlight-Instruct。

### 7. 全开源 drop-in（§1, §4）
开源 KDA kernel（flash-linear-attention `fla/ops/kda`）+ vLLM 实现 + pre-trained/instruct checkpoint（HuggingFace `moonshotai/Kimi-Linear-48B-A3B-Instruct`），不改 caching/scheduling 接口，drop-in 兼容现有 full-attention 管线。

## 表格（原文结果）

### Table 1 — 混合比与组件 ablation（§5.2，PPL 越低越好）
| 配置 | Train PPL | Val PPL |
|---|---|---|
| **3:1（默认）** | **9.23** | **5.65** |
| 0:1（纯全注意力） | 9.45 | 5.77 |
| 1:1 | 9.29 | 5.66 |
| 7:1 | 9.23 | 5.70 |
| 15:1 | 9.34 | 5.82 |
| w/o output gate | 9.25 | 5.67 |
| w/ swish output gate | 9.43 | 5.81 |
| w/o convolution layer | 9.29 | 5.70 |

### Table 2 — Scaling law 模型配置（§5.3）
| Act. Params | Heads | Layers | Hidden | Tokens | LR | Batch |
|---|---|---|---|---|---|---|
| 653M | 16 | 16 | 1216 | 38.8B | 2.006e-3 | 336 |
| 878M | 18 | 18 | 1376 | 59.8B | 1.790e-3 | 432 |
| 1.1B | 20 | 20 | 1536 | 85.2B | 1.617e-3 | 512 |
| 1.4B | 22 | 22 | 1632 | 102.5B | 1.486e-3 | 576 |
| 1.7B | 24 | 24 | 1776 | 128.0B | 1.371e-3 | 640 |

### Table 3 — 短上下文预训练（1.4T，Base 模型）
| 基准 | MLA | GDN-H | Kimi Linear |
|---|---|---|---|
| HellaSwag | 81.7 | 82.2 | **82.9** |
| ARC-challenge | 64.6 | 66.5 | **67.3** |
| Winogrande | 78.1 | 77.9 | **78.6** |
| BBH | 71.6 | 70.6 | **72.9** |
| MMLU | 71.6 | 72.2 | **73.8** |
| MMLU-Pro | 47.2 | 47.9 | **51.0** |
| TriviaQA | 68.9 | 70.1 | **71.7** |
| GSM8K | 83.7 | 81.7 | **83.9** |
| MATH | 54.7 | 54.1 | 54.7 |
| EvalPlus | 59.5 | **63.1** | 60.2 |
| CRUXEval-I-cot | 51.6 | 56.0 | **56.6** |
| CRUXEval-O-cot | 61.5 | 58.1 | **62.0** |
| CEval | 79.3 | 79.1 | **79.5** |
| CMMLU | 79.5 | 80.7 | **80.8** |

### Table 4 — 短上下文 SFT（Instruct）
| 基准 | MLA | GDN-H | Kimi Linear |
|---|---|---|---|
| BBH | 68.2 | 68.5 | **69.4** |
| MMLU | 75.7 | 75.6 | **77.0** |
| MMLU-Pro | 65.7 | 64.8 | **67.4** |
| MMLU-Redux | 79.2 | 78.7 | **80.3** |
| GPQA-Diamond (Avg@8) | 57.1 | 58.6 | **62.1** |
| LiveBench (Pass@1) | 45.7 | **46.4** | 45.2 |
| AIME 2025 (Avg@64) | 20.6 | 21.1 | **21.3** |
| MATH500 | 80.8 | **83.0** | 81.2 |
| HMMT 2025 (Avg@32) | 11.3 | 11.3 | **12.5** |
| PolyMath-en (Avg@4) | 41.3 | 41.5 | **43.6** |
| LiveCodeBench v6 (Pass@1) | 25.1 | 25.4 | **26.0** |
| EvalPlus | 62.6 | 62.5 | 61.0 |

### Table 5 — 长上下文 128k（4 模型对比）
| 基准 | MLA | GDN-H | Kimi Linear (RoPE) | Kimi Linear |
|---|---|---|---|---|
| RULER | 81.3 | 80.5 | 78.8 | **84.3** |
| MRCR | 22.6 | 23.9 | 22.0 | **29.6** |
| HELMET-ICL | 88.0 | 85.5 | 88.0 | **90.0** |
| LongBench V2 | 36.1 | 32.6 | 35.4 | 35.0 |
| Frames | 60.5 | 58.7 | 59.9 | 58.8 |
| RepoQA | 63.0 | 63.0 | 66.5 | **68.5** |
| Long Code Arena | 33.2 | 30.5 | 32.5 | 32.7 |
| Long Code Arena (Commit) | — | — | — | — |
| **Avg** | 52.2 | 51.2 | 51.8 | **54.5** |

### Table 7 — 注意力机制 update rule 总览（§7.1, TTT 视角，节选）
| 方法 | Objective L | Update rule |
|---|---|---|
| LA [48] | −⟨S^T k, v⟩ | St = St-1 + k_t v_t^T |
| Mamba2 [16] | −β⟨S^T k, v⟩ + ½‖√(1−α) S‖²_F | St = αt St-1 + βt k_t v_t^T |
| GLA [114] | −⟨S^T k, v⟩ + ½‖√Diag(1−α) S‖²_F | St = Diag(αt) St-1 + k_t v_t^T |
| RWKV7 [71] | ½‖S^T k̃ − v‖² + ½‖√Diag(1−α) S‖²_F | St = (Diag(αt) − (b⊙k̂)k̂^T) St-1 + k_t v_t^T |
| GDN [111] | β/2‖S̃^T k − v‖² | St = (I − βt k_t k_t^T) αt St-1 + βt k_t v_t^T |
| **KDA (ours)** | β/2‖S̃^T k − v‖² | St = (I − βt k_t k_t^T) Diag(αt) St-1 + βt k_t v_t^T |

### Table 8/9 — Kimi Linear @5.7T vs Moonlight（节选，Instruct）
| 基准 | Kimi-Linear-Instruct | Moonlight-Instruct |
|---|---|---|
| RULER@128k | 95.4 | — |
| RULER@1M | 94.8 | — |
| GPQA-Diamond (Avg@8) | 71.7 | 24.7 |
| MMLU-Pro (EM) | 72.7 | 43.8 |
| AIME 2025 (Avg@64) | 58.6 | — |
| MATH500 | 94.6 | 58.0 |
| LiveCodeBench v6 (Pass@1) | 45.7 | 11.9 |

## 与同类对比

- **vs Gated DeltaNet (GDN) [111] / Mamba2 [16]**：GDN/Mamba2 是 head-wise 粗粒度 scalar forget gate；KDA 用 channel-wise Diag(αt) 细门控（Table 7，KDA 行相对 GDN 行仅把 αt 提到 Diag 内）。Figure 4 合成任务上 KDA 在长序列保持精度 + 收敛更快；Figure 7 显示 KDA 与 GDN-H prefill 曲线几乎重合（细门控不增 latency），但长上下文质量全面领先（Table 5 GDN-H Avg 51.2 < Kimi Linear 54.5）。
- **vs GLA [114]**：channel-wise 门控思想借鉴 GLA，但 KDA 结合 DPLR 变体 + chunkwise + delta rule（householder）；GLA 用 log-domain + secondary chunking 解决 1/Γ 数值不稳定，KDA 通过 binding a=b=k 直接删掉 secondary chunking，运算量减半（§3.2）。
- **vs RWKV7 [71]**：RWKV7 用一般 DPLR (Diag(α) − b⊙k̂·k̂^T)；KDA 是其特化变体（a=b=k 约束），表达力等价但 kernel 提速 ~2×（Figure 2）。
- **vs 纯 softmax / MLA**：首次在公平规模（同 48B/3B MoE、1.4T tokens、同 WSD LR 1.1e-3、batch 32M tokens、K2 corpus）下混合线性架构**全面超越**全注意力（Table 3/4/5 + Figure 6 RL）；既往混合模型要么规模小要么未超越。
- **vs Sparse Attention (NSA [119] / MoBA [63] / DSA [18])**：§7.1 指出 sparse attention 仍需存全 KV cache 做选择，且理论上界 = full attention；linear attention "compression as intelligence" 用 fixed-size state + delta rule 理论上更强。KDA kernel + vLLM 解决了 linear attention "缺优化推理基础设施"的痛点。

## 跨论文关系（→ MOC 谱系）

- **线性/混合注意力谱系**：DeltaNet [84] → GDN [111]（+ scalar forget gate）→ **KDA（本文，channel-wise gate + DPLR 约束）** → 3:1 hybrid with Full MLA。延续 gated-delta 线（Mamba2 / GLA / RWKV7 / Comba / Longhorn）。MOC 谱系定位：**delta-rule 线性注意力的当前 SOTA 工业级实现 + 首个全场景超越 softmax 的混合架构**。
- **与 [[gated-delta-networks-improving-mamba2-with-delta-rule]] 直接前置**：GDN 是 KDA 的直接基线，KDA 在 GDN 上仅做 channel-wise gate + DPLR binding 两步改造即拿到全套收益；二者同属 delta-rule 改进分支。
- **与 [[mamba2-transformers-are-ssms]] 对比**：Mamba2 是 multiplicative decay 无 delta rule，Figure 4 上 Mamba2 在 Palindrome/Stack 完全失败——KDA 用 delta rule 修正性更新是关键差异。
- **与 [[rwkv7-goose-with-expressive-dynamic-state-evolution]] 同源**：RWKV7 用一般 DPLR，KDA 是其特化变体 + 定制 chunkwise kernel（§6.2 + Listing 8a/b 对照）。
- **与 [[deepseek-v3-technical-report]]/[[deepseek-v3-2-exp-attention]] 互补**：DeepSeek 用 Full MLA（本文的全注意力对照）+ 后续 DSA 稀疏注意力；Kimi Linear 走 hybrid linear 路线，§7.1 明确指出 linear 与 sparse 不互斥，未来可结合。
- **与 [[kimi-k2-open-agentic-intelligence]] 同源**：Kimi Linear 复用 K2 的预训练 corpus、SFT/RL 数据、WSD schedule、PTX loss、K1.5 RL 算法 + truncated importance sampling；是 Kimi agentic intelligence 的下一代 backbone 候选。
- **与 [[moonlight-muon-is-scalable-for-llm-training]] 同架构基座**：Kimi Linear 直接基于 Moonlight 架构（Muon optimizer），5.7T 版本与 Moonlight 同 token 量对比（Table 8/9）。
- **与 [[ascend-950-npu-architecture-whitepaper]]/[[parallel-scan-on-ascend-ai-accelerators]] 关联**：linear attention 的 chunkwise/scan 算子在 NPU 上的并行实现是落地关键，KDA kernel 可受益于并行 scan。
- **应用层**：混合线性架构服务 agentic / RL test-time scaling 场景（长轨迹、工具调用、repo-level code），与 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] 的长上下文需求同向。

## 局限与边界

- **3:1 比例是经验值**：Table 1 ablation 仅在单一规模测得，作者未给比例随规模/任务的敏感性详析；7:1 train PPL 持平但 val 退化提示比例随规模可能漂移。
- **仍依赖周期性全注意力层**：作者承认 pure linear 在长序列 in-context retrieval / exact copying 上理论受限（finite-state 容量瓶颈未根除，靠 3:1 混合缓解）；LongBench V2 / Frames 上 Kimi Linear 反不如 MLA（Table 5），印证 pure retrieval 任务仍有短板。
- **评测规模有限**：1.4T 公平对比 + 5.7T 释放版，均为 3B 激活；更大规模（百 B 激活）下相对全注意力的优势是否保持，scaling law 仅到 1.7B activated，未延伸。
- **DPLR chunkwise 算法实现复杂**：依赖定制 KDA kernel + vLLM 集成才能拿到效率收益，非通用库开箱即用；Listing 1 伪代码含 secondary chunking（Appendix C line 47-52），数值稳定性仍需精巧处理。
- **GDN-H baseline 工程实现差异**：作者已尽力公平（同 Sigmoid output gate 等），但 GDN-H 的 channel-wise 等价改写是否最优 not-available。
- **NoPE 选择对 MLA 层有利但限制复用**：NoPE 让 MLA 可转高效 MQA 推理，但长上下文外推仍需 KDA 承担全部位置编码责任，纯 KDA 层失效时退化风险存在。
- **RL 评测仅限 Math**：Figure 6 RL 优势仅在数学 RLVR 上验证，code/agentic RL 场景未给曲线。
