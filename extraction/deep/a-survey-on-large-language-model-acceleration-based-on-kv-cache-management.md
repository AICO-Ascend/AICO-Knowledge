# KV Cache Management Survey — 技术点深读（DEEP 2026-08-18）

> Source: `extraction/fulltext/a-survey-on-large-language-model-acceleration-based-on-kv-cache-management.txt` (arXiv:2412.19442v3, 30 Jul 2025). Li, Li, Tian, Tang, Xu, Chen, Hu, Dong, Li, Chen (PolyU / HKUST / HUST / CUHK / NTU). Survey — taxonomy paper, not a single mechanism. Curated list: github.com/TreeAI-Lab/Awesome-KV-Cache-Management.

## 核心问题

本文攻击的不是单一机制，而是一个 **组织性/认知性问题**：KV cache 优化技术已爆炸式增长（token-level / model-level / system-level 散落数百篇），但缺乏统一、机制级、可对照的分类法，导致研究者难以判断"在某约束下该选哪一类、彼此是否正交、与 vLLM/FlashAttention 是否兼容"。

底层动机来自 KV cache 的 **二次复杂度与线性内存增长的张力**（§2.2.2）。在解码步 `t`，新 token 的 Q/K/V 经线性投影生成（§2.2.1, Eq.(7)），其 K/V 被拼接到历史缓存上，attention 在 cached 集合上做 scaled dot-product（§2.2.1, Eq.(9)）：

$$
\mathbf{z}^t_i = \text{Softmax}\left(\frac{\mathbf{q}_i^t {\mathbf{K}_i^t}^\top}{\sqrt{d_k}}\right) \mathbf{V}_i^t,
$$

其中 `\mathbf{K}_i^t = \text{Concat}(\hat{\mathbf{K}}_i^{t-1}, \mathbf{k}_i^t)`、`\mathbf{V}_i^t` 同理——即 `t` 步的复杂度仍随已缓存 token 数线性增长，不经缓存则需对全部历史重算。缓存 `t_c` 个 token 在 `L` 层 `h` 头上节省的 **计算量**（§2.2.2, Eq.(10)）为：

$$
O\left(L\cdot h \cdot t_c \cdot t \cdot (d_k+d_v)+ L\cdot h \cdot t_c\left(\triangle_1 + \triangle_2\right)\right)
$$

（`t` 为序列长度，`\triangle_1,\triangle_2` 分别对应 Eq.(1) 的 QKV 投影与 Eq.(3) 的多头合并耗时），随 `t` 线性增长、长序列收益放大。但其 **空间代价**（§2.2.2, Eq.(11)）同步线性膨胀：

$$
O(L\cdot h \cdot t_c \cdot (d_k+d_v) \cdot sizeof(Float16))
$$

Float16 下随序列与层数线性膨胀，长上下文下逼近 GPU HBM 上限。LaTeX↔M3 校验：本文无对应 figure PNG（`minimax_captions.json` 未收录本 slug 图），故以 formulas.json LaTeX 为唯一权威源渲染，未引入 M3 caption 旁证。

由此衍生 §2.3 列出的六大挑战：Cache Eviction Policies（LRU/LFU 与 LLM attention pattern 不匹配）、Memory Management（GPU/CPU/external 协同）、Latency Bottlenecks（每步解码的 cache 访问）、Compression Trade-offs（压缩 vs 精度）、Dynamic Workloads、Distributed Coordination。本文的产出是 **三级 taxonomy（Token / Model / System，§3, Fig.2）** 作为对这六大挑战的系统性应答，并对每个叶子节点给出机制级比较表（Tab.2–Tab.12）和未来方向。

## 关键创新点

作为 survey，"创新点"指其分类法骨架与跨方法对照贡献，而非新算法：

1. **三级 taxonomy：Token-level / Model-level / System-level（§3, Fig.2）**
   - 机制：按"是否改模型架构 / 是否动系统底层"分层。其判别基准是 transformer block 的标准前向：输入 `X` 经 QKV 线性投影（§2.1.1, Eq.(1)）

$$
\mathbf{Q}_i = \mathbf{X}\mathbf{W}_{Q_i}, \quad \mathbf{K}_i = \mathbf{X}\mathbf{W}_{K_i}, \quad \mathbf{V}_i = \mathbf{X}\mathbf{W}_{V_i},
$$

     每头做 scaled dot-product attention（§2.1.1, Eq.(2)）

$$
\mathbf{Z}_i = \text{Attention}(\mathbf{Q}_i, \mathbf{K}_i, \mathbf{V}_i) = \text{Softmax}\left(\frac{\mathbf{Q}_i \mathbf{K}_i^\top}{\sqrt{d_k}}\right) \mathbf{V}_i,
$$

     多头拼接后线性合并（§2.1.1, Eq.(3)）：

$$
\mathbf{Z}=\text{Concat}(\mathbf{Z}_1, \mathbf{Z}_2, \dots, \mathbf{Z}_h)\mathbf{W}_O,
$$

     再过 FFN（§2.1.1, Eq.(4)）：

$$
\text{FFN}(\mathbf{Z}) = \sigma(\mathbf{Z}\mathbf{W}_1 + \mathbf{b}_1)\mathbf{W}_2 + \mathbf{b}_2
$$

     整个 block 由自回归生成驱动（§2.1.2）：每步建模下一 token 条件概率（Eq.(5)）：

$$
P(x_{t+1} | x_1, x_2, \cdots, x_t) = \text{Softmax}(\mathbf{h}_t \mathbf{W}_{\text{out}} + \mathbf{b}_{\text{out}}),
$$

     并采样（Eq.(6)）：

$$
x_{t+1} \sim P(x_{t+1} | x_1, x_2, \cdots, x_t).
$$

     Token-level（§4）不动上述任一公式，只按 KV 对的特征做选择/预算/合并/量化/低秩；Model-level（§5）改 Eq.(2) 的 attention 结构或引入非 transformer；System-level（§6）做内存管理/调度/硬件感知，不改公式只改 K/V 的存放与搬运。
   - 效果：将 §2.3 的六大挑战归口到三类正交技术轴，使"压缩 vs 重用 vs 调度"可组合性显式化。每类再二/三分子类（如 Token 下分 selection/budget/merging/quantization/low-rank），共 12 张对照表覆盖 ~150 个方法。

2. **Token-level 五子类的精细再分（§4, Fig.3）**
   - 机制：Token-level 全部作用于 KV cache 的增量机制本身。解码步 `t` 新 token 经投影生成单步 Q/K/V（§2.2.1, Eq.(7)）：

$$
\mathbf{q}_i^t = \mathbf{x}_t \mathbf{W}_{Q_i}, \quad \mathbf{k}_i^t = \mathbf{x}_t \mathbf{W}_{K_i}, \quad \mathbf{v}_i^t = \mathbf{x}_t \mathbf{W}_{V_i},
$$

     新 K/V 拼接到历史缓存（§2.2.1, Eq.(8)）：

$$
\mathbf{K}_i^{t} = \text{Concat}(\mathbf{\hat{K}}_i^{t-1}, \mathbf{k}_i^t ), \ \mathbf{V}_i^{t} = \text{Concat}(\mathbf{\hat{V}}^{t-1}_i, \mathbf{V}_i^t ),
$$

     Token-level 五子类即对 `\hat{\mathbf{K}}/\hat{\mathbf{V}}` 的"选哪些保留 / 各层分多少预算 / 合并相似 KV / 降精度 / 降秩"——全部不改 Eq.(7)/(8) 的形式，只改缓存内容与表示。其中低秩子类的 **Tensor Decomposition**（§4.5.2, DecoQuant[66]）以 Matrix Product Operator (MPO) 分解权重矩阵 `W`（Eq.(12)）：

$$
\text{TD}(\mathbf{W}) = \prod_{k=1}^n \mathcal{T}_{(k)}[d_{k-1}, i_k, j_k, d_k],
$$

     其中 `\mathcal{T}_{(k)}` 为第 `k` 个局部张量（尺寸 `d_{k-1} \times i_k \times j_k \times d_k`），将 KV 权重矩阵因子化为局部张量乘积以最小化冗余。KV cache selection（§4.1）按"prefill 一次性 / decode 永久驱逐 / decode 多层缓存不驱逐"三分；budget allocation（§4.2）按 layer-wise vs head-wise；merging（§4.3）按 intra-layer vs cross-layer；quantization（§4.4）按 fixed / mixed / outlier-redistribution；low-rank（§4.5）按 SVD / tensor / learned。
   - 效果：Tab.2 给出 selection 方法的 (initial tokens / top-k / recent / permanent eviction / dynamic / granularity) 六维布尔对照；Tab.3 给 budget allocation 的 (layer/head/retrieval-head/input-specific/extra-calibration) 五维对照；Tab.5 给 mixed-precision 的 (Keys/Vals 策略 × 重要 token × outlier × channel reorder × initial/mid/recent) 对照；Tab.6 给 outlier redistribution 的 (operation/formula/learn) 对照。这是机制级而非口号级比较。

3. **Model-level 区分 "grouping/sharing" vs "alteration" vs "non-transformer"（§5, Fig.7）**
   - 机制：Intra-layer grouping（MQA/GQA/AsymGQA 等，§5.1.1）按 head 共享 KV；Cross-layer sharing（CLA/LCKV/SA/MLKV/LISA 等，§5.1.2）跨层共享；Architecture alteration（MLA/FLASH/Infini-Attention/YOCO/CEPE/XC-Cache/Block Transformer，§5.2）；Non-transformer（RWKV/Mamba/RetNet/MCSD + hybrid MixCon/GoldFinch/RecurFormer，§5.3）。
   - 效果：量化数字——MLKV 把 cache 压到 "GQA 的 ~1%"（§5.1.2）；CLA 在 MQA 基础上再 "2× KV cache 缩减"；LISA "6× 压缩 Q/K 参数"；CLLA "压到原始模型 <2%"；Wu et al. 指出 "2× 缩减可超标准 transformer 吞吐且无显著精度损失，进一步缩减需额外训练成本"。MLA（DeepSeek-V2 [28]）支持 128K 上下文。

4. **System-level 三轴：Memory / Scheduling / Hardware（§6, Fig.10）**
   - 机制：Memory（§6.1）分 architectural（vLLM/PagedAttention paging、vTensor 虚拟内存、LeanKV unified paging + Hetero-KV、eLLM memory ballooning、Apt-Serve hybrid cache）与 prefix-aware（ChunkAttention prefix tree、MemServe 分布式 MemPool、FlashForge shared-prefix kernel）；Scheduling（§6.2）分 prefix-aware（BatchLLM/RadixAttention/Echo）、preemptive+fairness（FastServe/FastSwitch/FlowKV）、layer-specific/hierarchical（LayerKV/CachedAttention/ALISA/LAMPS）；Hardware（§6.3）分 single/multi-GPU、I/O-based、heterogeneous、SSD-based。
   - 效果：Tab.10/11/12 给出方法-特性布尔矩阵；明确 InstInfer 用 computational storage drives 在存储层内做 attention 以绕过 PCIe 带宽限制；DistServe 把 prefill/decode 物理分到不同 GPU；HeadInfer head-wise offloading 实现"任何层都不需在 GPU 上完整存 KV"且无近似。

5. **统一评测视角：文本 + 多模态 benchmarks（§7）**
   - 机制：§7.1 收录 13 个长上下文文本 benchmark（MultiTurnBench/NumericBench/RULER/OneRuler/L-Eval/M4LE/BAMBOO/LongBench/SCROLLS/ZEROSCROLLS/LooGLE/LongEval/StreamingEval），按 Q-A/Summarization/Reasoning/Retrieval/Generation/Aggregation 任务维 + EN/ZH 语言维制表（Tab.13）；§7.2 收录 9 个多模态 benchmark（LLaVA-Bench/MMBench/MileBench/MLVU/LongVideoBench/Video-MME/NExT-QA/MVBench/MSVD-QA/MSRVTT-QA，Tab.14）；§7.3 列 18 个评测指标（EM/PM/Accuracy/Recall/Precision/F1/BLEU/SacreBLEU/Rouge/METEOR/BERT/Edit Similarity/Pass@k/Exponential Similarity/Concordance Index/MRR/Relative Score/M-Avg/G-Avg/WUPS）。
   - 效果：填补 KV cache 评测"重算法轻下游任务"的空白，特别强调 multi-turn（MultiTurnBench）与 streaming（StreamingEval）场景——这恰是 static selection 方法的软肋（§4.1.4）。

## 表格（原文结构化）

### 表 A — Survey 三级 taxonomy 总览（据 Fig.2/Fig.3/Fig.7/Fig.10 重构）

| 一级 | 二级 | 三级 | 代表方法（原文编号） | 仓库对应 deep note |
|---|---|---|---|---|
| Token-level (§4) | KV Cache Selection (§4.1) | Static (§4.1.1) | FastGen[137], SnapKV[138], L2Compress[139], Attention-Gate[140] | — |
| | | Dynamic + Permanent Eviction (§4.1.2) | H2O[131], BUZZ[132], NACL[133], Scissorhands[134], Keyformer[135], SepLLM[136], StreamingLLM[141], LM-Infinite[142] | — |
| | | Dynamic w/o Permanent Eviction (§4.1.3) | InfLLM[125], Quest[126], PQCache[101], SqueezedAttention[127], RetrievalAttention[128], EM-LLM[129], ClusterKV[130], SparQ[143], InfiniGen[144], RecycledAttention[145], MagicPIG[146], Loki[74], LoopServe[1] | [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] |
| | KV Cache Budget (§4.2) | Layer-wise (§4.2.1) | PyramidKV[120], PyramidInfer[121], DynamicKV[122], PrefixKV[123], CAKE[147], SimLayerKV[124] | — |
| | | Head-wise (§4.2.2) | AdaKV[114], CriticalKV[115], LeanKV[116], RazorAttention[117], HeadKV[118], DuoAttention[119] | — |
| | KV Cache Merging (§4.3) | Intra-layer (§4.3.1) | CCM[104], LoMA[105], DMC[106], CaM[107], D2O[108], AIM[109], Look-M[110], ZeroMerge[111], KVMerger[112], CHAI[113] | — |
| | | Cross-layer (§4.3.2) | MiniCache[102], KVSharer[103] | — |
| | KV Cache Quantization (§4.4) | Fixed-precision (§4.4.1) | ZeroQuant[98], FlexGen[99], QJL[100], PQCache[101] | — |
| | | Mixed-precision (§4.4.2) | KVQuant[87], IntactKV[88], SKVQ[89], KIVI[90], WKVQuant[91], GEAR[92], MiKV[93], ZIPVL[94], ZipCache[95], PrefixQuant[96], MiniKV[97], QAQ[156], CacheGen[157], Atom[158] | — |
| | | Outlier Redistribution (§4.4.3) | MassiveActivation[75], QuaRot[76], Qserve[77], Q-INT4[78], SpinQuant[79], DuQuant[80], SmoothQuant[81], OS+[82], AffineQuant[83], FlatQuant[84], AWQ[85], OmniQuant[86] | — |
| | KV Cache Low-rank (§4.5) | SVD (§4.5.1) | ECKVH[67], EigenAttention[68], ZDC[69], LoRC[70], ShadowKV[71], Palu[72], Q-Filters[73], Loki[74] | — |
| | | Tensor Decomp (§4.5.2) | DecoQuant[66] | — |
| | | Learned (§4.5.3) | LESS[64], MatryoshkaKV[65] | — |
| Model-level (§5) | Attention Grouping/Sharing (§5.1) | Intra-layer (§5.1.1) | MQA[206], GQA[207], AsymGQA[208], Weighted GQA[209], QCQA[210], KDGQA[211], GQKVA[212] | [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] |
| | | Cross-layer (§5.1.2) | CLA[197], LCKV[198], SA[199], MLKV[200], LISA[201], Wu et al.[202], CLLA[203], DHA[204], SVFormer[205] | — |
| | Architecture Alteration (§5.2) | Enhanced Attention (§5.2.1) | MLA[28], FLASH[195], Infini-Attention[196] | [[deepseek-v3-technical-report]] (MLA) |
| | | Augmented Arch (§5.2.2) | YOCO[191], CEPE[192], XC-Cache[193], Block Transformer[194] | — |
| | Non-transformer (§5.3) | Adaptive Seq Proc (§5.3.1) | RWKV[187], Mamba[188], RetNet[189], MCSD[190] | — |
| | | Hybrid (§5.3.2) | MixCon[184], GoldFinch[185], RecurFormer[186] | — |
| System-level (§6) | Memory Management (§6.1) | Architectural (§6.1.1) | vLLM[149], vTensor[229], LeanKV[116], eLLM[261], Apt-Serve[252], DMS[262] | [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] |
| | | Prefix-aware (§6.1.2) | ChunkAttention[258], MemServe[259], FlashForge[260] | — |
| | Scheduling (§6.2) | Prefix-aware (§6.2.1) | BatchLLM[255], RadixAttention[256], Echo[257] | [[sglang-efficient-execution-of-structured-language-models-programs]] (RadixAttention) |
| | | Preemptive+Fairness (§6.2.2) | FastServe[231], FastSwitch[238], FlowKV[254] | — |
| | | Layer/Hierarchical (§6.2.3) | LayerKV[248], CachedAttention[249], ALISA[250], LAMPS[251], Apt-Serve[252], FGOS[253] | — |
| | Hardware-aware (§6.3) | Single/Multi-GPU (§6.3.1) | HydraGen[239], DeFT[240], vLLM[149], ORCA[241], DistServe[242], Multi-Bin Batching[243], Tree Attention[244], gLLM[245], FairKV[246], MELL[247] | — |
| | | I/O-based (§6.3.2) | FlashAttention[150–152], Bifurcated Attention[235], PartKVRec[232], HCache[236], Cake[237], FastSwitch[238] | — |
| | | Heterogeneous (§6.3.3) | NEO[227], FastDecode[228], FlexInfer[229], InfiniGen[144], Pensieve[230], FastServe[231], PartKVRec[232], HeadInfer[233], APEX[234] | — |
| | | SSD-based (§6.3.4) | FlexGen[99], InstInfer[226] | — |

### 表 B — KV cache selection 维度对照（据 Tab.2 精简）

| Method | Initial | Top-k | Recent | Perm. Evict | Dynamic | Granularity | Remark |
|---|---|---|---|---|---|---|---|
| FastGen | ✗ | ✗ | ✗ | ✗ | — | token | 5 attention structures |
| SnapKV | ✗ | ✗ | ✗ | ✗ | — | token | observation window-based |
| H2O | ✓ | ✓ | ✓ | ✓ | ✓ | token | cumulative attention score |
| StreamingLLM | ✓ | ✗ | ✓ | ✓ | ✗ | token | initial+recent (attention sink) |
| InfLLM | ✗ | ✓ | ✗ | ✗ | ✓ | block | block-level KV mgmt |
| Quest | ✗ | ✓ | ✗ | ✗ | ✓ | block | min/max key block repr |
| PQCache | ✗ | ✓ | ✗ | ✗ | ✓ | block | product quantization + MIPS |
| SqueezedAttention | ✗ | ✓ | ✗ | ✗ | ✓ | cluster | K-means centroids |
| RetrievalAttention | ✗ | ✓ | ✗ | ✗ | ✓ | token | ANN search |
| EM-LLM | ✓ | ✓ | ✗ | ✗ | ✓ | event | episodic events |
| MagicPIG | ✗ | ✓ | ✗ | ✗ | ✓ | token | LSH (critiques top-k) |
| LoopServe | ✗ | ✓ | ✓ | ✗ | ✓ | token | progressive selection |

### 表 C — Model-level 量化缩减（原文散见 §5.1.2 / §5.2）

| 方法 | 缩减倍数 / 上下文 | 机制 |
|---|---|---|
| MQA | 相对 MHA 显著 | 单 K/V head 全共享 |
| GQA | 接近 MQA 速度、近 MHA 质量 | query head 分组共享 K/V |
| CLA | 在 MQA 基础上再 2× | 相邻层共享 K/V |
| MLKV | ~1% of GQA | 单 K/V head 跨多层共享 |
| LISA | 6× Q/K 参数压缩 | 小 FFN 对齐 + 低秩近似 |
| CLLA | <2% of original | head size 缩 + cross-layer + 量化 |
| MLA (DeepSeek-V2) | 128K 上下文 | 低秩 KV 联合压缩，latent vector |
| SVFormer | ~半 | 单 value embedding 跨层共享 |

## 与同类对比

- **vs 通用 LLM 效率 survey（[3]/[40]/[43]/[44]/[45]/[47]/[49]）**：本文在 §1 明确区分——这些 survey 是 holistic（data/model/system 全维），而本文聚焦 KV cache 单一抓手但做到三级 12 子类的机制级深度，并补多模态 benchmark。Ding et al.[43] 跨 data+model；Miao et al.[44] 纯 system 视角；Tang/Wan/Xu[45/47/49] 三层都有但浅。
- **vs 专题 survey**：Zhu et al.[3]/Park[41]/Wang[42]/Tang[47] 聚焦 model compression（quantization/pruning）；Kachris[48] 硬件加速；Xu[49] PEFT；Albalak[50] data selection；Xia[52] 协作式（speculative decoding）；Li[55] prompt compression。这些都是"非 KV cache"专题，本文与之互补。
- **vs 直接竞品 KV cache survey（Shi[56]/Li[57]/Yuan[58]）**：本文自称 "complementary and more comprehensive"——提供 token/model/system 三级 + 文本/多模态 benchmark，并对三级给出"差异与优势"比较，而非仅列举。
- **vs [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]（仓库内另一篇 KV cache survey）**：本 survey 的分类轴是 token/model/system 三级（按"是否改架构/动系统"分层），强调正交性与可组合性；后者更偏向 inference scalability 视角。两者可互为索引：本 survey 提供 12 张方法-特性对照表作为方法选择器，后者可作为 system-side scalability 的深入补充。

## 跨论文关系（→ MOC 谱系）

本 survey 是 **KV cache 谱系的 taxonomy anchor**——它把仓库内多篇具体方法论文归位到三级分类法的叶子节点：

- **System-level / Architectural memory（§6.1.1）**：[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] — vLLM PagedAttention 是本文 Tab.10 的 paged/virtual memory 标杆，OS paging 思想迁移到 KV block。
- **System-level / Prefix-aware scheduling + architectural（§6.1.2, §6.2.1）**：[[sglang-efficient-execution-of-structured-language-models-programs]] — RadixAttention[256] 是 prefix-aware scheduling 的代表（§6.2.1），用 radix tree 做 cache-aware 请求调度。
- **System-level / Disaggregated + KV-centric architecture**：[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — KV-cache-centric 解耦架构，对应本文 §6.3 (hardware-aware) 与 §6.1 (memory) 的融合，把 KV cache 提升为系统一等公民。
- **System-level / Cross-layer index reuse（§4.1.3 dynamic w/o eviction）**：[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] — 跨层 index 复用，对应 §4.1.3 的 block/cluster 级索引检索（InfLLM/Quest/PQCache 谱系）。
- **System-level / RAG KV fusion（§6.1.2 prefix-aware）**：[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] — prefix 复用 + 部分重计算融合，对应 §6.1.2 prefix-aware design 与 §6.2.1 prefix-aware scheduling 的 RAG 特化。
- **System-level / Cross-datacenter KV（§6.3 + §6.1）**：[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] — 把 KV cache 跨数据中心化，对应本文 §6.3.3 heterogeneous 与 §6.1 distributed memory 的延伸（MemServe[259] 分布式 MemPool 同谱）。
- **Model-level / Intra-layer grouping（§5.1.1）**：[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA[207] 是 MQA→MHA 的折中点，本文 §5.1.1 的核心参照系；uptraining 从 MHA checkpoint mean-pool 转 GQA。
- **Model-level / Enhanced Attention（§5.2.1）**：[[deepseek-v3-technical-report]] — MLA（DeepSeek-V2[28] 引入，V3 沿用）低秩 KV joint 压缩，本文 §5.2.1 标杆，支持 128K 上下文；与 GQA 同属 intra-layer 但走 latent compression 路线。
- **对照 survey**：[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]] — 仓库内另一 KV cache survey，与本篇互补（见上节）。

谱系定位：本 survey = **谱系根节点 / 索引层**；上述具体论文 = 三级分类法的叶子实例。仓库内任何 KV cache 相关深读笔记都可在本 survey 的 Tab.A 中找到归位。

## 局限与边界

- **无原创机制，无统一实验**：作为 survey，所有量化数字均引自原论文自报，缺乏在统一模型/数据集/hardware 下的 head-to-head 复现。Tab.2–Tab.12 是布尔特性矩阵，不是精度/吞吐数值对照。§4.2.3 明确承认 "field lacks comprehensive experimental comparisons, particularly regarding compatibility ... with vLLM[149] and FlashAttention[150–152]"。
- **taxonomy 边界处的张力未消解**：§4.2.3 自承 pyramid-shaped[120,121]（下层大预算）与 retrieval-head[117,118]（下层少 retrieval head 故需小预算）存在直接矛盾，survey 只指认不裁决。
- **"dynamic w/o permanent eviction" 与 system-level 边界模糊**：InfLLM/Quest/PQCache（§4.1.3）用 CPU-GPU 多层缓存做不驱逐检索，机制上与 §6.1 memory management / §6.3.3 heterogeneous design 高度重叠，taxonomy 把同一方法在两处归类（如 InfiniGen 在 §4.1.3 与 §6.3.3 同时出现，PartKVRec 在 §6.3.2 与 §6.3.3 同时出现），存在冗余但未显式声明。
- **top-k 选择在 ultra-long 序列的失效**：§4.1.4 指出当前 top-k 选择"在 ultra-long sequence tasks 下可能无法有效识别和提取相关 token"，且现有方法"predominantly rely on attention score-based top-k"——这是整个 selection 子类的集体盲区。
- **Model-level 多需 retraining**：§5 反复强调 MQA/GQA 需 uptrain，LISA/DHA 需 lightweight adaptation，CEPE/XC-Cache 需新 encoder 训练，CLA 需 X——这对已存在的 pretrained 巨型模型采用成本高；§5.2.3 自承 "integrating these novel mechanisms into existing pretrained models often requires extensive retraining, hindering their adoption in resource-constrained environments"。
- **Non-transformer 的长程能力滞后**：§5.3.3 承认 RWKV/Mamba "performance in capturing ultra-long-range dependencies lags behind transformers"，且 hybrid（MixCon/GoldFinch）"complexity introduces challenges in training stability and interpretability"。
- **多模态 KV cache 讨论薄**：尽管 §7.2 收录多模态 benchmark，但 §4–§6 的方法几乎全部面向文本 LLM；§4.4.4 future direction 才提到"extending KV cache quantization to multi-modal and multi-task models"是未竟之业。
- **隐私维度仅作 future direction**：§6.2.4 与 §8 把 multi-user 场景下的 KV cache 隐私泄漏（prefix sharing 跨用户复用可能泄漏）列为未来工作，未覆盖已有 privacy-preserving serving 工作。
- **时效性**：arXiv v3 截止 2025-07-30，2025 H2 起的 KV cache 工作（如更细粒度的 cross-instance 复用、新硬件后端）未被纳入。
