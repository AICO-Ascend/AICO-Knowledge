# CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion — 技术点深读（DEEP 2026-08-18）

> Yao et al., EuroSys '25, arXiv:2405.16444v3. 代码：https://github.com/LMCache/LMCache
> 独立文件：深读内容，不依赖 extract_phase1 重新生成的 MD body（参见 MEMORY overwrite gotcha）。

## 核心问题

RAG 场景下，一次 LLM 输入往往拼接了多个被检索回来的 text chunks（§1: "applications often prepend multiple text chunks in the LLM input"）。这些 context chunks 是 prefill 延迟的主要来源——§2 给出实测：4K-token 输入在 Llama-34B 上 prefill 需 3 秒，Llama-70B 上需 6 秒（A40 GPU）。已有两类 KV cache 复用方案都失效：

1. **Prefix caching**（vLLM/SGLang/RAGCache，§3.2）：只能复用输入第一个 chunk 作为前缀的 KV cache，因为前缀的 KV 不受后续文本影响、质量无损。但当输入含多个 reused chunks 时，"except the first chunk, all other chunks' KV caches are not reused"（§3.2），节省近乎边缘。Figure 1（p.2，M3：四面板对比 full recompute / prefix caching / full KV reuse / CacheBlend 四范式，CacheBlend 在 (d) 面板复用全部三个 stored KV cache 但只重算小部分 token，箭头指向 "Much faster + Good quality"）以一图概括了这一困境。图 2 实证：Musique / 2WikiMQA 上，relevant chunks 从 5 增到 45 时，full KV recompute（带 cross-attention）的 F1 从 ~0.15 涨到 ~0.30+，而 full KV reuse（无 cross-attention）的 F1 明显更低且 gap 随 chunk 数扩大——说明多 chunk 拼接既是刚需、又放大了 cross-attention 缺失的代价。

2. **Full KV reuse**（PromptCache，§3.3）：把各 chunk 的预计算 KV cache 通过 buffer 拼接，用 RoPE 旋转矩阵恢复位置编码。但它**完全忽略了 chunk 之间的 cross-attention**——预计算时前置文本未知。§3.3 用 Messi vs Ronaldo 进球数的例子（Figure 3，p.4；M3：三面板，(a) setup 给出 Messi 13 球 / Ronaldo 8 球两 chunk + 比较查询，(b) full KV recompute 拼接两 chunk 一次 prefill 给出正确答案，(c) full KV reuse 各 chunk 独立预计算 KV 后拼接，LLM 输出 "Lionel Messi scored more goals than at FIFA World Cups than Cristiano Ronaldo" 这种破碎、跑题的回答）证明：忽略 cross-attention 会导致 LLM "start to ramble and not produce the right answer"。Figure 4（p.4，M3：两行 heatmap 对比，(a) full recompute 的 attention matrix 中黄框 cross-attention 区域有分散激活，forward-attention 呈合理分布；(b) full reuse 的 cross-attention 黄框几乎为空，forward-attention 出现明显的竖直亮条纹——token 均匀地 attend 到少数位置，是 cross-attention 缺失的典型伪影）从 attention matrix 层面给出根因。

CacheBlend 攻击的就是这一个精确挑战（§1, §4 Goal）：**当 LLM 输入含多个 reused text chunks 时，如何快速融合它们各自的预计算 KV cache，使得 forward attention matrix（及最终生成）与 full KV recompute 的差异最小**——既要 full KV reuse 的速度，又要 full KV recompute 的质量。Figure 1(d)（p.2，M3）正是这一目标的可视化：复用全部三个 stored KV cache，只对一小部分 token 做 selective recompute（红色高亮），最终 KV cache of [1,2,3] 同时达到 "Much faster + Good quality"。

## 关键创新点

### 1. Selective KV recompute（选择性 KV 重算）——核心机制
**机制**（§4.2, Figure 5 p.5）：不做传统整段 prefill，而是逐层处理。Figure 5（M3：两面板对比，(a) full recompute 中 layer-i 输入经 Q_i→K_i→Attn Matrix→×V_i 产下一层输入；(b) selective recompute 在同一 Q×K→Attn→×V 流水上，仅对两个被选 token 重算（深色 Re-computed），其余 token 直接用预存 KV（浅色 Re-used），两条流水线结构完全相同，差别仅在重算范围）说明这是对原 transformer 流水的最小侵入式改造。每一层 i：(a) 对输入加 mask，缩减到该层被选中的 token 子集；(b) 仅对选中 token 计算 Q_i、K_i、V_i；(c) 用未选中 token 的预计算 KV cache 条目"扩展"K_i、V_i，使 attention matrix 仍覆盖"选中 token × 全部 token"；(d) 跑同一个 attention module 产出下一层输入。

步骤 (c) 中预计算 K 条目携带有旧位置编码，直接拼接会错位——CacheBlend 的 **positional recovery**（§4 脚注 3，Appendix A Definition 1）将每个复用 chunk 的 K 向量乘以其新绝对位置 m 对应的 RoPE 旋转矩阵，RoPE 对每对维度 [2i, 2i+1] 独立施加 2D 旋转：

$$q_{m}, k_{m}= \begin{pmatrix} \cos m\theta & -\sin m\theta\\ \sin m\theta & \cos m\theta\\ \end{pmatrix} \{ \begin{pmatrix} q_{[0]}\\ q_{[1]}\\ \end{pmatrix}, \begin{pmatrix} k_{[0]}\\ k_{[1]}\\ \end{pmatrix} \}$$

该乘法只执行一次、开销可忽略（§4 脚注 3: "this correction is done simply by multiplying the K vector by a rotation matrix... This step has negligible overhead"）。

重旋转之所以在数学上成立，依据是 RoPE 的**相对位置不变性**（Appendix A, Proposition A.1）。先在 2D 情形：位置 m 的 key 与位置 m-n 的 query 的点积化简后只含相对偏移 n——

$$\begin{aligned} {q}_{im} {k}_{j(m-n)} &= q_{[0]i}k_{[0]j}\cos (m-m+n)\theta\\ & \quad +q_{[1]i}k_{[1]j}\cos (m-m+n)\theta \\ &= (q_{[0]i}k_{[0]j}+q_{[1]i}k_{[1]j})\cos n\theta \\ \end{aligned}$$

推广到 d 维（对 d/2 个维度对求和），位置 m+l 的 query 与位置 m 的 key 的 attention score 推导为（Appendix A, Eq. (1)）：

$$\begin{aligned} {q}_{m+l} {k}_{m} &={(\mathbb{R}^{d}_{\Theta, m+l}q)}^{T}{(\mathbb{R}^{d}_{\Theta, m}k)}\\ &= \sum_{i=0}^{d/2-1}({q_{[2i]}k_{[2i]}\cos (m+l-m)\theta_{i}}\\ & \quad +{q_{[2i+1]}k_{[2i+1]}\cos (m+l-m)\theta_{i}}) \\ &= \sum_{i=0}^{d/2-1}({q_{[2i]}k_{[2i]}+ {q_{[2i+1]}k_{[2i+1]}})\cos l\theta_{i}} \\ \end{aligned}$$

即 attention score 只依赖相对距离 l 而与绝对位置 m 无关（Proposition A.1: "The attention score only depends on the relative distance l rather than the absolute position m"）——因此把复用 chunk 的 K 重旋转到其在拼接输入中的新绝对位置后，selective recompute 的 attention 计算与 full prefill 的位置语义严格一致，这正是 cache fuse 步骤合法性的数学基础。
**效果**（§4.2 末）：计算开销正比于选中 token 数——若每层重算 r% 的 token，总开销即为 full prefill 的 r%。§1 给出经验值："an update fraction of less than 15% can typically generate same-quality responses"。

### 2. HKVD token 选择 + 渐进式过滤（cross-attention 稀疏性利用）
**机制**（§4.3）：定义 KV deviation Δkv(KV_i, KV_full_i)[j] 与 attention deviation Δattn(A_i, A_full_i)。**Insight 1**（Figure 6, p.6；M3：折线图，x 轴 recomputation ratio 0–50%，y 轴 forward attention deviation 0–1，Mistral-7B / Yi-34B / Llama-70B 三曲线在 ~10% 重算处出现最大跌幅，之后边际收益骤降）：重算 KV deviation 最高的 token（HKVD tokens）对降低 attention deviation 收益最大。背后是 attention sparsity（Figure 7, p.6；M3：CDF 图，Mistral-7B / Yi-34B / Llama-70B 三模型的某层 KV deviation 分布均呈长尾，约 10–15% 的 token 的 KV deviation 远高于其余 token，印证 cross-attention 稀疏）。
但 HKVD 需要知道 ground-truth KV_full，self-defeating。于是 **Insight 2**（Figure 8, p.7；M3：三模型 Spearman rank correlation 柱图，相邻层对（如 5 vs 6、31 vs 32）的相关性普遍显著高，部分层对接近 0.8+，但深层个别层对 <0.6）：相邻层间 HKVD token 的 rank correlation 显著高（transformer 各层 input embedding 变化缓慢），可用上一层结果指认下一层。
**渐进式过滤**（Figure 9, p.7；M3：layer-wise 流水图，Layer 1 全量重算并标 HKVD，Layer 2 只重算继承来的 r1% HKVD token 再筛 r2%，Layer 3 进一步收窄，Updated-KV 与 Precomputed-KV 并存于当前层，进入下一层时 Precomputed-KV 立即丢弃）：第 1 层全量 prefill，按 r1% (>r) 选 HKVD；第 2 层只对这 r1% token 重算，再按 attention deviation 选 r2% (<r1)；逐层收窄，最终每层平均 r% 的 token 被重算。内存开销"negligible"——层 i 的额外 Precomputed-KV 在进入 i+1 层时立即丢弃（§4.3 末）。
**效果**（§7.3, Figure 16 p.12；M3：四散点图，CacheBlend 红方块聚集在 5–18% 重算 + 接近满分区间，full recompute 与 prefix caching 蓝点堆在 ~90–100% 重算，full KV reuse 橙×质量明显偏低；Yi-34B）：5%-18% 重算比例下，F1/Rouge-L 相对 full KV recompute 损失 ≤0.002；对应 4.1-6.6× TTFT 降（vs full recompute）、3.4-6.1× 降（vs prefix caching）。

### 3. Pipelining：KV 加载 与 selective recompute 流水线
**机制**（§5, Figure 10 p.8, Figure 11 p.9）：核心 insight——"如果 selective recompute 的延迟 ≤ KV 从存储载入 GPU 的延迟，则流水线可完全隐藏重算延迟"。Figure 10(a)（M3：prefill delay vs recompute ratio，"w/o pipelining" 虚线从 ~1s 陡升至 ~3.5s，"w. pipelining" 实线近乎平缓仅升至 ~2s，标注 26.8% 为 1GB/s SSD 下的最优重算比）可视化这一隐藏效应；Figure 10(b)（M3：GPU / CPU RAM / SSD(32Gbps) / SSD(4Gbps) 四设备的 TTFT 柱状对比，w/ pipelining 实柱明显低于 w/o 虚柱，标注 CPU RAM 为 15% 重算下不增延迟的最便宜设备）展示存储设备选择空间。具体：层 i 的 recompute 与层 i+1 的 KV 加载并行（§6 实现：两个 thread，prefill_layer 与 fetch_kv）。Figure 11（M3：系统数据流，User 查询 "Can we use drones in agriculture?" → Loading Controller 查 KV Cache Store（CPU/SSD/Slower Disks 分级）→ KV Cache #1-4 + recompute ratio 送 KV Cache Fusor → Fused KV Cache → LLM 生成答案；绿色虚线框标出 CacheBlend 系统）给出端到端架构。fusor 等上一层 recompute 完成 + 当前层 KV 已载入 GPU 队列后执行。
**效果**（§5 实测）：Llama-7B + 4K context，15% 重算每层仅 3ms，而 NVMe SSD 每层 KV 加载 16ms → 加载完全隐藏重算，TTFT 无额外延迟。Llama-70B：15% 重算 7ms vs 加载 4ms → 加载无法完全隐藏，需 controller 介入。

### 4. Loading Controller（联合优化重算比例与存储设备）
**机制**（§5.1）：两个延迟估计器——T_recompute(r%, LLM, L) = r% × P_prefill(LLM, L)（P_prefill 离线 profile）；T_load = PerTokenKVSize × L / Throughput。控制器先求 T_recompute = T_load 的 r%，再与质量下限 r*%=15% 取 max（保证质量即便存储很快，对应 Figure 10(b) M3 解读）。另一模式：固定 r=15%，用 storage cost estimator C_store 在所有满足 T_recompute ≥ T_load 的设备中挑最便宜的（CPU RAM / SSD / 慢盘）。
**效果**（§5, §7.3 Figure 17 p.12；M3：CPU RAM 与 4Gbps Slower Disk 两场景下 CacheBlend / Full KV Reuse / Prefix Caching / Full Recomp 的 TTFT-F1 散点，CacheBlend 在慢盘下与 Full KV Reuse 的 TTFT gap 缩小——loading 主导，但仍保持质量优势）：使 KV cache 可下沉到 NVMe SSD 甚至更慢的 4Gbps disk，而不增加 TTFT——容量更大、成本更低。

### 5. KV cache store + Fusor 系统化集成
**机制**（§5.1, §6）：输入按应用切分为 chunks，每 chunk hash 检索（同 vLLM block hashing）；LRU 驱逐。三个接口集成进 vLLM：fetch_kv / prefill_layer（input_dict 含 input_org、check_flag、HKVD_indices）/ synchronize。~3K 行 Python，基于 PyTorch v2.0。
**效果**（§1, §7）：TTFT 降低 2.2-3.3×，吞吐提升 2.8-5×（vs full KV recompute），且不增加存储成本。

## 表格（原文结构化）

### 表 1：四种 KV 复用范式对比（Figure 1 p.2 + §1 + §3；M3 四面板对照）

| 方案 | 是否复用非前缀 chunk | 是否考虑 cross-attention | 速度 | 质量 |
|---|---|---|---|---|
| Full KV recompute（默认 prefill，Figure 1(a)） | 否（全算） | 是 | 最慢（基线） | 最优（基线） |
| Prefix caching（vLLM/SGLang/RAGCache，Figure 1(b)） | 否（仅前缀） | N/A | 边际加速 | 与 full recompute 持平 |
| Full KV reuse（PromptCache，Figure 1(c)） | 是 | **否** | 最快 | 低（多 chunk 时显著掉） |
| **CacheBlend（selective KV recompute，Figure 1(d)）** | 是 | **部分重算恢复** | 接近 full reuse | 接近 full recompute |

### 表 2：评估配置（§7.1）

| 维度 | 取值 |
|---|---|
| 模型 | Mistral-7B；Yi-34B（8-bit 量化）；Llama-70B（8-bit 量化） |
| 硬件 | Runpod，128GB RAM，2×Nvidia A40，1TB NVMe SSD（实测 4.8 GB/s） |
| GPU 数 | 1（Mistral/Yi）；2（Llama-70B） |
| 数据集 | 2WikiMQA（200 例）；Musique（150 例）；SAMSum（200 例）；MultiNews（60 例） |
| Chunk 切分 | 512 token（SAMSum 用原始 200-400）；Langchain |
| 合成扩展集 | Musique/2WikiMQA 各取 1500 query + GPT4 生成 4500 相似 query = 6000，top-6 检索 |
| 检索 | SentenceTransformers embedding，L2 距离 |
| 质量指标 | F1-score（2WikiMQA/Musique，答案 ≤5 词）；Rouge-L（MultiNews/SAMSum） |

### 表 3：核心定量结果（§1 摘要 + §7.2，对照 Figure 12 p.10 M3 四象限散点）

| 指标 | vs Full KV recompute | vs Prefix caching | vs Full KV reuse |
|---|---|---|---|
| TTFT 降低 | 2.2-3.3× | 2.2-3.3× | 几乎相同（略慢） |
| 吞吐提升 | 2.8-5× | 最高 3.3× | — |
| 质量差 | F1/Rouge-L 降 ≤0.02（Figure 12 ≤0.01-0.03） | 同上 | QA F1 高 0.1-0.2；摘要 Rouge-L 高 0.03-0.25 |
| 重算比例 | 5%-18%（Figure 16，Yi-34B） | — | — |

Figure 12（p.10，M3：4×3 散点网格，行=数据集，列=模型，CacheBlend 红方块稳定落在每子图左上 Pareto 区——低 TTFT + 高质量，全面支配 Full KV reuse（橙×，快但低质）与 Prefix Caching（蓝●））是表 3 的可视化佐证。

### 表 4：Sensitivity 分析关键结论（§7.3，对照 Figure 15 p.11 M3）

| 变量 | 实验 | 结论 |
|---|---|---|
| Chunk 数量 / 长度（Figure 15a/b） | 2WikiMQA + Mistral-7B | 维持 F1 降 ≤0.015 所需计算缩减比例稳定 |
| Batch size（Figure 15c） | — | batch 越大 prefill 占比越主导，CacheBlend 优势越明显 |
| 重算比例（Figure 16 p.12） | Yi-34B 全数据集 | 5%-18% 区间质量损失 ≤0.002 |
| 存储设备（Figure 17 p.12） | Yi-34B + 2WikiMQA，RAM vs 4Gbps SSD | 慢盘下 CacheBlend 与 Full KV reuse 的 TTFT gap 缩小（loading 主导） |

Figure 14（p.11，M3：2×3 折线网格，TTFT vs 请求率，CacheFuse 红线在所有模型×数据集上随请求率上升仍保持最低 TTFT，Llama-70B 列优势最大）佐证表 4 的 batch/request-rate 结论。

### 表 5：Pipeline 隐藏条件实测（§5）

| 模型 | 15% 重算延迟/层 | NVMe 加载/层 | 是否隐藏 |
|---|---|---|---|
| Llama-7B + 4K context | 3 ms | 16 ms | 完全隐藏 |
| Llama-70B | 7 ms | 4 ms | 未完全隐藏（需 controller） |

## 与同类对比

- **vs PromptCache（full KV reuse）**：PromptCache 用 dummy prefix buffer 恢复位置编码（§3.3），但每个 chunk 的 KV cache 必须针对所有可能的 prefix 长度多次预计算（"each chunk's KV cache will have to be precomputed multiple times"），存储放大；且**完全丢弃 cross-attention**——Figure 4（p.4，M3：(b) 的 cross-attention 黄框为空、forward-attention 出现竖直亮条纹）是其失败的直接证据。CacheBlend 仅在固定 15% token 上做 partial recompute 即可恢复 cross-attention，质量上 F1 高 0.1-0.2、Rouge-L 高 0.03-0.25（§1），TTFT 几乎不变。PromptCache 仅在 cross-attention 很低时（prompt template）才工作良好——这是它的主战场，非多 chunk RAG。

- **vs Prefix caching（vLLM/SGLang/RAGCache）**：prefix caching 只复用第一个 chunk（Figure 1(b) M3），且对同一 chunk 若 prefix 不同需存多份 KV cache，固定存储预算下 miss rate 更高（§7.2）。CacheBlend 复用所有 chunks、每 chunk 只存一份。评估中对 prefix caching 做了理想化假设（"no loading delay from RAM or SSD to GPU"），CacheBlend 仍胜出 2.2-3.3× TTFT、最高 3.3× 吞吐（Figure 14 p.11 M3 红线全面低于蓝线）。

- **vs MapReduce / MapRerank**（§7.2, Figure 13 p.10；M3：Yi-34B 上 CacheBlend vs MapReduce vs MapRerank 的 TTFT-F1 散点，CacheBlend 优于两者）：MapReduce 对每 chunk 独立摘要再合并，TTFT 高 2-5× 于 CacheBlend；MapRerank TTFT 略低但质量差（独立处理忽略 chunk 间依赖）。

- **vs Chunked prefill / Sarathi / DistServe**（§8）：这些是通用 serving 引擎优化 prefill 调度，CacheBlend 与之正交、可叠加（§9 明确未集成 DistServe/StableGen 为 future work）。

- **vs KV cache 压缩（KVQuant/GEAR/KIVI/Scissorhands/H2O）**（§8）：压缩减小 KV 体积，CacheBlend 关注复用与融合；两者可叠加——压缩后 KV 更小，加载更快，pipeline 更易隐藏重算。

## 跨论文关系（→ MOC 谱系）

CacheBlend 在 KV cache 复用谱系中的位置：**前缀复用 → 任意位置复用 → 跨层/跨请求复用** 路径上的"任意位置 + 跨 attention 修复"节点。

- [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] —— KV cache 内存管理的根（vLLM/PagedAttention）。CacheBlend 直接构建于 vLLM 之上（§6），复用其 block hashing，是 paged KV 之上的应用层复用方案。
- [[sglang-efficient-execution-of-structured-language-models-programs]] —— SGLang 的 RadixAttention 做 prefix 复用。CacheBlend 在评估中采用 SGLang 技术识别高频 prefix（§7.1 baselines），定位为 prefix caching 的多 chunk 推广。
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] —— Mooncake 以 KVCache 为中心做 disaggregated serving、跨节点前缀复用。CacheBlend §9 明确"未研究跨计算节点共享 KV cache"，是 Mooncake 路线在单节点 RAG 场景的互补。两者结合（Mooncake 跨节点分发 + CacheBlend 跨 chunk 融合）是开放方向。
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] —— IndexCache 做 cross-layer 索引复用以加速 sparse attention。与 CacheBlend 的 HKVD 跨层相关性（Insight 2、Figure 8 p.7 M3）机制上呼应：都利用"相邻层 attention/embedding 相似"这一性质，但 IndexCache 用于加速 attention 计算，CacheBlend 用于挑选待重算 token。
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] —— KV cache 管理综述，CacheBlend 是其中"non-prefix reuse + partial recompute"分支的代表工作。

## 局限与边界

1. **仅限 transformer 架构**（§9）：Insight 1/2 基于 attention sparsity 与层间 embedding 相似性（Figure 7、Figure 8 M3），对 Mamba/Griffin 等非 transformer 架构未验证，留作 future work。

2. **模型与量化覆盖有限**（§9）：仅测 Mistral-7B / Yi-34B / Llama-70B（后两者 8-bit 量化），未覆盖更多模型与不同量化设置。不同模型的 attention sparsity 程度可能不同，15% 默认比例未必普适。

3. **Pipeline 隐藏并非总是成立**（§5）：当存储很快（如 CPU RAM）或模型很大（Llama-70B：7ms 重算 vs 4ms 加载）时，加载无法完全隐藏重算，必须由 controller 牺牲部分重算比例或接受额外延迟——§5 坦承"KV loading does not completely hide the recompute delay"，Figure 10(b)（p.8 M3）也显示 4Gbps SSD 下 w/ pipelining 与 w/o 的差距收窄。

4. **单一存储层级**（§5.1）："we only focus on storing KV cache in one single level of storage device such as CPU RAM or SSD"——未做分层缓存（如 HBM/DRAM/SSD/object store 的多级），与 AttentionStore 等多级方案相比缺层次。

5. **未集成 disaggregated 引擎**（§9）：仅在 vLLM 上集成，未在 DistServe / StableGen 上测试；未研究跨节点 KV 共享。

6. **RAG 模式假设**（§3.2 脚注 1）：默认 "stuff" 模式（所有 chunk 拼接进一个输入）。MapReduce/Rerank 模式因每 chunk 独立处理（永远是前缀），prefix caching 已足够，CacheBlend 无优势——其价值依赖"多 chunk 同输入"这一前提。

7. **HKVD 选择的开销与误判**：第 1 层仍需 full prefill（Figure 9 p.7 M3），对短输入或层数少的模型收益被稀释；渐进式过滤依赖层间相关性，深层相关性弱时（Figure 8 M3 部分层对相关性 <0.6）可能漏选 HKVD token。

8. **质量评估粒度**：F1/Rouge-L 是表层指标，对 cross-attention 错误导致的语义偏差（如 Figure 3(c) p.4 M3 中的"rambling"）未做更细粒度的语义评估；15% 阈值经验性来自 Figure 16（p.12 M3，Yi-34B），对其他模型需重新标定。

9. **未解决长上下文 lost-in-the-middle**（§3.2 引 Figure 2 p.3）：chunk 过多时质量本会下降，CacheBlend 只加速、不改变这一固有现象。
