# Efficient Memory Management for Large Language Model Serving with PagedAttention — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Efficient Memory Management for Large Language Model Serving with PagedAttention · arXiv:2309.06180（SOSP '23, Kwon et al., UC Berkeley / Stanford / UC San Diego）

## 核心问题

LLM serving 的吞吐瓶颈是 **memory-bound**，而非 compute-bound。自回归解码阶段每步只产一个 token、走 matrix-vector mul，GPU 算力严重闲置；要提吞吐只能靠 batching，但 batch size 上限被 **KV cache 显存** 卡死。论文 §2.1 把自回归生成本身形式化为概率链式分解（Eq.1，权威 LaTeX↔fulltext §2.1 双源校验一致）：

$$P(x) = P(x_1) \cdot P(x_2\mid x_1) \cdots P(x_n \mid x_1, \ldots, x_{n-1}).$$

该分解决定了两点工程后果：(a) 只能逐 token 串行采样、新 token 依赖全部历史 K/V，故 KV cache 必须按 token 累积缓存；(b) prompt phase 可矩阵-矩阵并行、generation phase 退化为 matrix-vector 受限于显存带宽——正是 §2.2 所述 memory-bound 的根因。论文 §1 用 Figure 1（p.1）给出宏观证据：13B OPT 部署在 A100-40G 上，参数 26GB（65%）常驻、KV cache >30% 按请求动态增减、激活仅小片。M3 解读点出"传统系统把每请求 KV 存成单连续张量→内部+外部碎片严重、batch 受限"，正是 vLLM 要消除的根因。Figure 1 右半进一步把"现有系统 [31,60] KV 急速增长曲线"与"vLLM 平滑曲线 → 吞吐 2–4×"并列，定下全文论据链。

§3 把问题量化为三类显存浪费：

1. **Large KV cache（§3）** — 13B OPT 单 token KV cache = `2 × 5120 × 40 × 2 = 800 KB`（key/value × hidden × layers × FP16 bytes）；单请求 2048 token 上限 → 1.6 GB。A100-40G 上 KV 占约 30%（Fig.1）。从 A100→H100 FLOPS 涨 >2× 而显存仍封顶 80GB，"memory wall" 趋势恶化（§3 引 [17]）。
2. **Fragmentation（§3.1，Figure 3 p.4）** — 现有系统（FasterTransformer[31]、Orca[60]）因 DL 框架要求 tensor 连续存储，按请求最大可能长度静态预分配连续 chunk。Figure 3 的 M3 解读直观呈现：Request A（max 2048）7 个 prompt token + 3 generated 后跟 `<eos>`、2 reserved future slots、然后 **2038 个永不使用 slots（internal fragmentation）**；Request B（max 512）类似有 507 个废 slots；两请求之间留 **external fragmentation** 空洞。Profiling（§6.2，Figure 2 p.2）量化显示**有效 KV 显存仅 20.4%–38.2%**：Orca(Max) Token states 20.4 / Reservation 13.3 / Internal frag 57.3 / External frag 8.9；Orca(Pow2) 26.8/17.9/13.6/41.6；Orca(Oracle) 38.2/25.2/~0/36.6；vLLM **96.3/~0/~0/~3**。即 vLLM 有效显存利用率是 Orca(Max) 的 ~4.7×。
3. **无法 memory sharing（§1 第二点、§3）** — parallel sampling / beam search / 共享 system prompt 等场景中多序列存在大段 KV 共享，但连续 chunk 存储使共享不可行，造成冗余拷贝（beam search 跨候选频繁 memcpy）。§3 给出量级：parallel sampling 中 prompt KV 占总 KV 12%，beam search 最高可省 55%。

## 关键创新点

1. **PagedAttention 算法（§4.1）** — 借鉴 OS virtual memory paging[25]：把 KV cache 切成固定大小 `B`-token 的 KV block，key/value 向量存于**非连续**物理显存。先回顾它所改造的常规 self-attention 基线（§2.1，Eq.2/Eq.3，权威 LaTeX↔fulltext 双源校验一致）：每个位置 i 先经线性变换产出 Q/K/V（Eq.2），

   $$q_i = W_q x_i, \ k_i = W_k x_i, \ v_i = W_v x_i.$$

   再以 softmax 归一化点积得 attention score、对 V 加权求和（Eq.3，因果掩码上界 i），

   $$a_{ij} = \frac{\exp(q_i^\top k_j / \sqrt{d})}{\sum_{t=1}^{i}\exp(q_i^\top k_t / \sqrt{d})}, \ o_i = \sum_{j=1}^{i} a_{ij} v_j.$$

   PagedAttention 把 Eq.3 的逐 token 注意力改写为 block-wise 形式（Eq.4，权威 LaTeX↔fulltext §4.1 双源校验一致；M3 对 Fig.5 的解读给出"key/value 向量分布于 3 个非连续物理块、kernel 逐 block 取 K_j→算 A_ij→乘 V_j"的图文佐证）：

   $$A_{ij}=\frac{\exp(q_i^\top K_j/\sqrt d)}{\sum_{t=1}^{\lceil i/B\rceil}\exp(q_i^\top K_t\mathbf{1}/\sqrt d)},\quad o_i=\sum_{j=1}^{\lceil i/B\rceil}V_j A_{ij}^\top$$

   其中 `K_j=(k_{(j-1)B+1},...,k_{jB})`、`V_j=(v_{(j-1)B+1},...,v_{jB})`，`A_ij` 为第 j 个 KV block 上的 attention score 行向量。Kernel 逐 block 读取、并行度由 block size 控制（§4.3 末论证 block size>1 才能让 kernel 跨多位置并行、降延迟，过大则增碎片，详见 §7.2/Fig.18b）。类比：blocks=pages, tokens=bytes, requests=processes。脚注 1 指出同一 token 跨 layer/head 的 KV 可合并管理或分块管理，二者性能无差，vLLM 选第二种便于实现。

2. **逻辑/物理分离 + Block Table（§4.2，Figure 4 p.5 / Figure 6）** — 架构上 Figure 4 的 M3 解读点明 vLLM 把 **centralized scheduler + KV Cache Manager** 与每 GPU 的 **Worker(Model Shard + Cache Engine)** 解耦：Scheduler→Workers 派活、Scheduler→KV Cache Manager→CPU/GPU Block Allocators 做内存簿记、KV Cache Manager↔Workers 下发块管理指令。每请求维护一张 block table，记录 logical block → physical block 映射与 #filled。Figure 6 走查单请求解码：7-token prompt → logical block 0/1 映射到 physical 7/1（prefill 用常规 self-attention[13] 算 4+3 token KV）；解码步 1 新 KV 落入 logical 1 剩余 slot（#filled 更新）；解码步 2 logical 1 满 → 新开 logical 2 → 分配 physical 3。物理块按需分配、从左填满才开新块。**整请求浪费被限制在 ≤1 block**，消除内部+外部碎片，达到 near-zero waste（§4.3 末，对应 Fig.2 的 96.3%）。Figure 7（p.6）的 M3 解读进一步展示两请求 A/B 的 logical blocks 经 block table 映射到同一 9 块物理池的非连续位置，"neighboring logical blocks 不必物理相邻"，正是消除外部碎片的关键。

3. **Copy-on-Write 共享（§4.3–§4.4）** — physical block 引入 reference count；写共享块时 refcount>1 触发 copy-on-write（类比 fork）。直接支持三种场景：
   - **Parallel sampling（§4.4，Figure 8）** — 两 sample 共享 prompt，logical 0/1 → physical 7/1（refcount=2）；sample A1 写 logical 1 时 refcount>1 → 分配 physical 3、拷贝、refcount 2→1；A2 再写时 refcount 已为 1 → 直接写入。除最后一块外全 prompt KV 共享。
   - **Beam search（§4.4，Figure 9 p.7）** — 跨候选动态共享 prompt+生成块，共享模式随 decoding 演化。Figure 9 的 M3 解读给出 k=4 案例：虚线前候选 0–2 共享 block 1–3、候选 3 自 block 2 分叉；虚线后仅候选 1/2 留在 top-4 → 候选 0/3 的 logical 块释放（refcount 归 0 触发 physical block 2/4/5/8 释放），新分配 physical 9–12；最终所有候选共享 0/1/3，候选 0/1 共享 6，候选 2/3 共享 7。类比 OS compound fork 进程树。对比传统系统候选 3 需大规模 memcpy 候选 2 KV，vLLM 仅在新 token 落入旧共享块时拷贝一块。
   - **Shared prefix / system prompt（§4.4 末，Figure 10 p.8）** — Figure 10 的 M3 解读展示机器翻译 few-shot 模板：共享 prefix（"Translate English to French: sea otter=>loutre de mer, peppermint=>menthe poivrée, plush girafe=>girafe en peluche"）+ 每请求 task input（"cheese"=>/ "I love you"=>）。服务方预缓存共享前缀物理块，新请求 logical blocks 映射过去（最后一块标 COW），prompt phase 只需算 task input 部分。类比 OS shared library。

4. **Preemption + All-or-Nothing Eviction（§4.5）** — FCFS 调度，后到先抢占；同 request 多序列（如 beam 候选）gang-schedule 为 sequence group。因一序列所有 block 必同时被访问，采用 **all-or-nothing** 淘汰（LLM-specific 优化，§8）。恢复两种手段：(a) **Swapping** — 换到 CPU RAM，CPU block allocator 管理（Fig.4 架构支持），swap 容量上界=GPU KV 总量；(b) **Recomputation** — 把已生成 token 与原 prompt 拼接重跑一次 prefill，可在单次 prompt-phase iteration 重建全部 KV（OS 里不可行，是 LLM 特有）。

5. **Distributed Execution（§4.6）** — Megatron-LM[47] tensor parallelism SPMD，attention 按 head 维切分。关键观察：**各 shard 处理相同 token 位置**，故 scheduler 内单一 KV cache manager + 单一 logical→physical 映射被所有 worker 共享；每步广播 control message（token IDs + block table），all-reduce 同步中间结果无需 scheduler 介入。各 worker 虽持相同 physical block ID，但只存自己 head 子集的 KV。

6. **Kernel 融合优化（§5.1）** — (1) fused reshape+block write（每 layer 新 KV 切块/重排/按 block table 落盘合一）；(2) fused block read+attention，改造 FasterTransformer attention kernel，每 GPU warp 读一块保证 coalesced access，支持 batch 内变长；(3) fused block copy（COW 用，把多块 discontinuous 拷贝合并为单 kernel launch，避免大量小 cudaMemcpyAsync）。

7. **解码原语 fork/append/free（§5.2）** — 三方法组合即可表达 parallel sampling、beam search、prefix sharing 及未来算法。

## 表格（原文结构化）

### Table 1（§6.1）— 模型规模与服务器配置

| Model size | 13B | 66B | 175B |
|---|---|---|---|
| GPUs | A100 | 4×A100 | 8×A100-80GB |
| Total GPU memory | 40 GB | 160 GB | 640 GB |
| Parameter size | 26 GB | 132 GB | 346 GB |
| Memory for KV cache | 12 GB | 21 GB | 264 GB |
| Max. # KV cache slots | 15.7K | 9.7K | 60.1K |

### Fig.2（§6.2，p.2）— KV cache 显存浪费分解（%），越低越浪费

| 系统 | Token states 有效 | Reservation | Internal frag. | External frag. |
|---|---|---|---|---|
| Orca (Max) | 20.4 | 13.3 | 57.3 | 8.9 |
| Orca (Pow2) | 26.8 | 17.9 | 13.6 | 41.6 |
| Orca (Oracle) | 38.2 | 25.2 | ~0 | 36.6 |
| vLLM | **96.3** | ~0 | ~0 | ~3 |

> vLLM 有效显存利用率约为 Orca(Max) 的 4.7×、Orca(Oracle) 的 2.5×。M3 解读强调现有系统 60–80% KV 显存被碎片与过度预留浪费，vLLM 的 paged 非连续方案保留 ~96% 给真实 token states。

### Fig.11（§6.1，p.9）— 数据集输入/输出长度分布

| Dataset | Input mean (tokens) | Output mean (tokens) |
|---|---|---|
| ShareGPT | 161.31 | 337.99 |
| Alpaca | 19.31 | 58.45 |

> ShareGPT 输入 8.4×、输出 5.8× 长于 Alpaca，方差更高；两分布均右偏长尾。M3 解读指出 ShareGPT 序列比 Alpaca 长约一个数量级，正是 PagedAttention 处理变长/超长 context 而不浪费显存的动机。

### Fig.12（§6.2，p.10）— 基础采样 normalized latency vs request rate（2×3 网格）

| 配置 | vLLM 相对最强 baseline |
|---|---|
| OPT-13B/1GPU ShareGPT | 较 Orca(Oracle) 1.7–2.7×、较 Orca(Max) 2.7–8× 可持续请求率 |
| OPT-66B/4GPU ShareGPT | 同量级优势 |
| OPT-175B/8GPU ShareGPT | 同量级优势 |
| OPT-13B/1GPU Alpaca | 显著优势 |
| OPT-66B/4GPU Alpaca | 显著优势 |
| OPT-175B/8GPU Alpaca | 优势收窄（compute-bound，见下） |

> M3 解读：vLLM 蓝曲线在所有 6 个面板中向右延伸最远才上扬；Orca 变体与 FasterTransformer 更早触饱和拐点。vs FasterTransformer 最高 22×（FT 无细粒度调度、内存管理同 Orca(Max)）。Fig.12(f) 例外：175B+Alpaca 短序列 + 大 KV 显存（Table 1: 264GB KV）使 Orca(Oracle)/(Pow2) 也能塞大批量，性能转为 compute-bound，vLLM 优势缩小。

### Fig.13（§6.2）— OPT-13B 平均 batch 请求数

| 系统 | ShareGPT (2 req/s) | Alpaca (30 req/s) |
|---|---|---|
| Orca (Max) | 7.00 | 7.00 |
| Orca (Pow2) | 9.81 | 43.24 |
| Orca (Oracle) | 13.62 | 72.75 |
| vLLM | **30.42** | **132.44** |

> 同等延迟约束下 vLLM 并发 batch 为 Orca(Oracle) 的 2.2×（ShareGPT）/1.8×（Alpaca），为 Orca(Max) 的 4.3×/18.9×。这是 Fig.2 显存利用率优势直接转化为并发度的因果链。

### Fig.14（§6.3，p.11）— Parallel generation / beam search（OPT-13B Alpaca）

| 算法 | vLLM 相对 Orca(Oracle) |
|---|---|
| Parallel size 2/4/6 | 随 #sample 增多优势扩大 |
| Beam width 2/4/6 | 优势更大；beam=6 时 2.3×（vs 基础采样 1.3×） |

> M3 解读：vLLM 蓝曲线在所有 6 个面板中拐点最靠右，且随 parallelism/beam-width 增大领先扩大——证明 PagedAttention 的 KV 共享随多序列生成扩展性增强。

### Fig.15（§6.3）— KV block 共享带来的显存节省（OPT-13B/Alpaca）

| # Output / Beam width | Parallel sampling 节省% | Beam search 节省% |
|---|---|---|
| 2 | 6.09 | 37.56 |
| 4 | 8.53 | 53.13 |
| 6 | 9.79 | 55.16 |

> ShareGPT 同实验：parallel sampling 16.2%–30.5%，beam search 44.3%–66.3%（§6.3 文本）。beam search 因共享模式动态演化、覆盖 prompt+生成块，节省远高于 parallel sampling。

### Fig.16（§6.4）— Shared prefix 翻译负载（LLaMA-13B, WMT16 En→De）

| Prefix | vLLM vs Orca(Oracle) |
|---|---|
| 1-shot (80 tokens) | 1.67× |
| 5-shot (341 tokens) | 3.58× |

> 共享前缀越长，vLLM 优势越大（prompt phase 只算 task input 部分）。

### Fig.17（§6.5）— Chatbot（ShareGPT，截 1024 input/1024 output）

| 系统 | 可持续请求率 |
|---|---|
| Orca (Max/Pow2/Oracle) | 三者接近（buddy alloc 一律预留 1024） |
| vLLM | **2× Orca baselines** |

### Fig.18（§7，p.12）— Ablation

**(a) Attention kernel 微基准（context 64/128/256，bs 8/32）：**

| 配置 | vLLM 相对 FasterTransformer kernel |
|---|---|
| 各 ctx/bs 组合 | 高 20%–26% latency |

> M3 解读：vLLM 四条曲线（bs 8/32 × vLLM/FT）均高于 FT 对应曲线——动态 block table 访问/分支/变长的代价。但仅限 attention 算子，被吞吐收益覆盖；end-to-end vLLM 仍显著优于 FT。

**(b) Block size 影响：**

| Trace | 最佳 block size |
|---|---|
| ShareGPT | 16–128 |
| Alpaca | 16–32（更大则序列短于 block → 性能崩） |

> M3 解读：两曲线呈 U 形，最佳区在 16–32；Alpaca 超 32 后因短序列碎片化急剧恶化。默认 `B=16`，兼顾 GPU 并行度与碎片。

### Fig.19（§7.3，p.13）— Recompute vs Swap

**(a) 微基准（block size 1→256）：**

| 机制 | 小 block | 中 block (16–64) | 大 block |
|---|---|---|---|
| Recompute | ~20ms 恒定 | 恒定 | 恒定 |
| Swap in+out | ~140ms（PCIe 带宽差） | 下降 | 趋近/低于 recompute |

**(b) End-to-end（OPT-13B ShareGPT）：** 两曲线 U 形，16–64 区间相当。

> M3 解读：swap 在小 block 下因大量小数据 CPU↔GPU 传输打不满 PCIe 而劣化；recompute 不经 KV block 故开销恒定。Recompute 开销永远 ≤ swap 延迟的 20%。需根据 block size 选恢复策略。

## 与同类对比

| 维度 | vLLM/PagedAttention | Orca [60] | FasterTransformer [31] | FlexGen [46] | FlashAttention [13] | OLLA [48] |
|---|---|---|---|---|---|---|
| KV 存储 | 非连续 paged blocks | 连续 chunk + buddy alloc | 连续 chunk | 连续（offline 离线 swap） | 连续（tiling 内） | 优化 tensor 生命周期 |
| 内存碎片 | ~0（≤1 block） | 严重（20–38% 有效） | 同 Orca(Max) | — | 降低 attention 峰值 | 减碎片但非 block 级 |
| 内存共享 | block 级 COW（跨请求/序列） | 不支持 | 不支持 | 不支持 | 不支持 | 不支持 |
| 调度 | FCFS + all-or-nothing 抢占 | iteration-level scheduling | 无自有调度（外接 Triton） | offline | — | — |
| 恢复机制 | swap / recompute 二选一 | — | — | swap weights+states | — | — |
| 适用场景 | 在线高吞吐 serving | 在线 serving | 低延迟推理 | 单卡低显存离线推理 | attention kernel 优化 | 训练期 tensor 内存优化 |

- **vs Orca**（§9 Comparison to Orca）：互补——Orca 靠 iteration-level scheduling 提升并发，vLLM 靠内存利用率让更多请求 working set 装入显存。vLLM 在 Orca 之上再 2–4×。Orca 的细粒度调度反而使内存管理更难，凸显 vLLM 技术的必要性。
- **vs FlashAttention [13]**（§9）：FlashAttention 做 tiling+kernel 优化降低 attention 峰值显存与 I/O；vLLM 引入的是**在线服务场景下的 block-level 内存管理新范式**，正交方向（vLLM prefill 阶段还用常规 self-attention 如 FlashAttention）。
- **vs OLLA [48]**（§9）：OLLA 优化 tensor 生命周期/位置减碎片，但不做 block 级管理或在线 serving。
- **vs FlexGen [46]**（§9）：FlexGen 研究 weights+token states 的离线 swap 以在单 GPU 上跑推理，但不针对在线 serving 场景。

## 跨论文关系（→ MOC 谱系）

vLLM/PagedAttention 是 **KV-cache paged-memory 谱系的根节点**，OS virtual memory 思想首次系统化引入 LLM serving：

- **根（本论文）** [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] — paged KV block + block table + COW + preemptive swap/recompute。
- → **RadixAttention / SGLang** [[sglang-efficient-execution-of-structured-language-model-programs]] — 在 paged KV 之上引入 Radix Tree 自动复用共享前缀；把 vLLM 的"显式预定义 prefix 共享"升级为"自动 prefix 树"，扩展到 structured programs。
- → **Mooncake** [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — 跨节点 KV pool，把单机 paged KV 概念推广到 disaggregated prefill/decode 架构，KV cache 作为全局可寻址资源；vLLM 的 block 抽象是其跨节点迁移的基础单元。
- → **Sarathi** [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — chunked prefill + piggybacking decode，与 paged KV 协同：分块 prefill 写入 block table，复用 vLLM 的非连续块存储自然容纳 chunk 边界。
- → **KV-cache 管理综述** [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — PagedAttention 是综述中"memory management / paging"主线的奠基工作，后续 eviction、compression、hierarchy（GPU/CPU/disk）均建立在其 block 抽象之上。

## 局限与边界

1. **Kernel 开销**（§7.1，Fig.18a）：PagedAttention kernel 比 FasterTransformer 高 20–26% latency（block table 访问、分支、变长）；但仅限 attention 算子，被吞吐收益覆盖。极端低 batch、纯延迟敏感场景需权衡。
2. **Block size 折中**（§7.2，Fig.18b）：过小→GPU 并行不足；过大→内部碎片+共享概率下降。Alpaca 短序列超 32 即崩。默认 16 是经验值，非通用最优。
3. **Swap 在小 block 下劣化**（§7.3，Fig.19）：小 block 导致大量小数据传输，PCIe 带宽利用率差；此时 recompute 更优（开销恒定，≤swap 20%）。需根据 block size 选恢复策略。
4. **适用边界**（§8 Discussion）：paging 不普适于所有 GPU 工作负载。DNN 训练（tensor shape 静态，可提前优化）、非 LLM DNN serving（compute-bound）引入 paging 反而因 memory indirection 与非连续块访问降性能。前提是工作负载满足"动态分配 + 显存容量瓶颈"。
5. **未触及 KV 量化/压缩**：本文只做内存管理，不涉及 KV cache 的精度压缩（后续工作 int8/int4 KV、H2O 等正交方向）。
6. **Prefix 共享需显式预定义**（§4.4）：原论文要求服务提供方预先 reserve 共享前缀物理块；自动 prefix 共享是后续 RadixAttention 才补齐。
7. **单 GPU 中心化 scheduler**（§4.6）：scheduler 单点；跨节点 KV 池未覆盖（Mooncake 方向）。
8. **评估 trace 偏短**（§6.1）：多数实验 1 小时 trace，175B 仅 15 分钟（成本限制）；长尾分布、突发流量下抢占与 swap 行为未充分评估。
