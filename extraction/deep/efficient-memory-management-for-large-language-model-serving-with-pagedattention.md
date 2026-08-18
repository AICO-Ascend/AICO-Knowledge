# vLLM/PagedAttention — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Efficient Memory Management for Large Language Model Serving with PagedAttention · arXiv:2309.06180（SOSP '23, Kwon et al., UC Berkeley / Stanford / UC San Diego）

## 核心问题

LLM serving 的吞吐瓶颈是 **memory-bound**，而非 compute-bound。自回归解码阶段每步只产一个 token、用 matrix-vector mul，GPU 算力严重闲置；要提升吞吐只能靠 batching，但 batch size 上限被 **KV cache 显存** 卡死。论文 §1、§3 量化指出三类显存浪费：

1. **Large KV cache**（§3）：13B OPT 单 token KV cache = `2 × 5120 × 40 × 2 = 800 KB`（key/value × hidden size × layers × FP16 bytes）；单请求 2048 token 上限 → 1.6 GB。A100-40G 仅 KV 部分约 30%（Fig.1），且从 A100→H100 FLOPS 涨 2× 而显存仍封顶 80GB，"memory wall" 趋势恶化（§3）。
2. **Fragmentation**（§3.1）：现有系统（FasterTransformer[31]、Orca[60]）因 DL 框架要求 tensor 连续存储，按请求最大可能长度静态预分配连续 chunk → 内部碎片（actual ≪ max，如 2048 槽位中 2038 永不使用，Fig.3）+ 外部碎片（buddy allocator 留洞）+ reserved 浪费（整段保留期不可复用）。Profiling（§6.2/Fig.2）显示 **有效 KV 显存仅 20.4%–38.2%**，最低 Orca(Max) 20.4%、vLLM 96.3%。
3. **无法 memory sharing**（§1 第二点、§3）：parallel sampling / beam search / 共享 system prompt 等场景中多个序列存在大段 KV 共享，但连续 chunk 存储使共享不可行，造成冗余拷贝（beam search 跨候选频繁 memcpy）。

## 关键创新点

1. **PagedAttention 算法（§4.1）** — 借鉴 OS virtual memory paging[25]：把 KV cache 切成固定大小 `B`-token 的 KV block，key/value 向量存于**非连续**物理显存。注意力改写为 block-wise 形式（Eq.4）：

   $$A_{ij}=\frac{\exp(q_i^\top K_j/\sqrt d)}{\sum_{t=1}^{\lceil i/B\rceil}\exp(q_i^\top K_t\mathbf{1}/\sqrt d)},\quad o_i=\sum_{j=1}^{\lceil i/B\rceil}V_j A_{ij}^\top$$

   其中 `K_j=(k_{(j-1)B+1},...,k_{jB})`。Kernel 逐 block 读取、并行度由 block size 控制。类比：blocks=pages, tokens=bytes, requests=processes。

2. **逻辑/物理分离 + Block Table（§4.2）** — 每请求维护一张 block table，记录 logical block → physical block 映射与 #filled。物理 block 按需分配，从左填满才开新块。**整请求浪费被限制在 ≤1 block**，消除内部+外部碎片，达到 near-zero waste（§4.3 末、Fig.2 的 96.3%）。

3. **Copy-on-Write 共享（§4.3–§4.4）** — physical block 引入 reference count；写共享块时 refcount>1 触发 copy-on-write（类比 fork）。直接支持：
   - **Parallel sampling**（Fig.8）：prompt KV 物理块共享，仅最后一块 COW。
   - **Beam search**（Fig.9）：跨候选动态共享 prompt+生成块，共享模式随 decoding 演化（类比 compound fork 进程树）；vLLM 仅在新 token 落入旧共享块时拷贝一块，对比传统系统大规模 KV memcpy。
   - **Shared prefix / system prompt**（§4.4 末、Fig.10）：预缓存共享前缀物理块，新请求逻辑块映射过去（类比 OS shared library）。

4. **Preemption + All-or-Nothing Eviction（§4.5）** — FCFS 调度，后到先抢占；同 request 的多序列（如 beam 候选）gang-schedule 为 sequence group。因一序列所有 block 必同时被访问，采用 **all-or-nothing** 淘汰（LLM-specific 优化，§8）。恢复两种手段：(a) **Swapping** — 换到 CPU RAM，CPU block allocator 管理，swap 容量上界=GPU KV 总量；(b) **Recomputation** — 把已生成 token 与原 prompt 拼接重跑一次 prefill，可在单次 prompt-phase iteration 重建全部 KV（OS 里不可行，是 LLM 特有）。

5. **Distributed Execution（§4.6）** — Megatron-LM tensor parallelism[47] SPMD，attention 按 head 维切分。关键观察：**各 shard 处理相同 token 位置**，故 scheduler 内单一 KV cache manager + 单一 logical→physical 映射被所有 worker 共享；每步广播 control message（token IDs + block table），all-reduce 同步中间结果无需 scheduler 介入。

6. **Kernel 融合优化（§5.1）** — (1) fused reshape+block write；(2) fused block read+attention，改造 FasterTransformer attention kernel，每 GPU warp 读一块保证 coalesced access，支持 batch 内变长；(3) fused block copy（COW 用，避免多次 cudaMemcpyAsync）。

7. **解码原语 fork/append/free（§5.2）** — 三个方法组合即可表达 parallel sampling、beam search、prefix sharing 及未来算法。

## 表格（原文结构化）

### Table 1（§6.1）— 模型规模与服务器配置

| Model size | 13B | 66B | 175B |
|---|---|---|---|
| GPUs | A100 | 4×A100 | 8×A100-80GB |
| Total GPU memory | 40 GB | 160 GB | 640 GB |
| Parameter size | 26 GB | 132 GB | 346 GB |
| Memory for KV cache | 12 GB | 21 GB | 264 GB |
| Max. # KV cache slots | 15.7K | 9.7K | 60.1K |

### Fig.2（§6.2）— KV cache 显存浪费分解（%），越低越浪费

| 系统 | Token states 有效 | Reservation+Internal+External frag & Others |
|---|---|---|
| Orca (Max) | 20.4 | 79.6 |
| Orca (Pow2) | 13.3 / 17.9（两组并列） | — |
| Orca (Oracle) | 57.3 / 41.6 | — |
| vLLM | **96.3** | 3.7 |

> vLLM 有效显存利用率为 Orca(Max) 的 ~4.7×。

### Fig.11（§6.1）— 数据集输入/输出长度分布

| Dataset | Input mean (tokens) | Output mean (tokens) |
|---|---|---|
| ShareGPT | 161.31 | 337.99 |
| Alpaca | 19.31 | 58.45 |

> ShareGPT 输入 8.4×、输出 5.8× 长于 Alpaca，方差更高。

### Fig.13（§6.2）— OPT-13B 平均 batch 请求数

| 系统 | ShareGPT (2 req/s) | Alpaca (30 req/s) |
|---|---|---|
| Orca (Max) | 7.00 | 7.00 |
| Orca (Pow2) | 9.81 | 43.24 |
| Orca (Oracle) | 13.62 | 72.75 |
| vLLM | **30.42** | **132.44** |

> 同等延迟约束下 vLLM 并发 batch 为 Orca(Oracle) 的 2.2×（ShareGPT）/1.8×（Alpaca），为 Orca(Max) 的 4.3×/18.9×。

### Fig.15（§6.3）— KV block 共享带来的显存节省（OPT-13B/Alpaca）

| # Output / Beam width | Parallel sampling 节省% | Beam search 节省% |
|---|---|---|
| 2 | 6.09 | 37.56 |
| 4 | 8.53 | 53.13 |
| 6 | 9.79 | 55.16 |

> ShareGPT 同实验：parallel sampling 16.2%–30.5%，beam search 44.3%–66.3%（§6.3 文本）。

### Fig.18a（§7.1）— attention kernel 微基准

| 配置 | vLLM 相对 FasterTransformer kernel |
|---|---|
| bs=8 / bs=32，ctx 64/128/256 | 高 20%–26% latency |

> Overhead 仅影响 attention 算子，不波及 Linear 等；end-to-end vLLM 仍显著优于 FT。

### Fig.18b（§7.2）— block size 影响

| Trace | 最佳 block size |
|---|---|
| ShareGPT | 16–128 |
| Alpaca | 16–32（更大则序列短于 block → 性能崩） |

> 默认 `B=16`，兼顾 GPU 并行度与碎片。

### Fig.19（§7.3）— Recompute vs Swap

| 机制 | 小 block | 中 block (16–64) | 大 block |
|---|---|---|---|
| Recompute | 更优（开销恒定，不依赖 block） | 相当 | swap 略优 |
| Swap | 差（小数据传输打满 PCIe 带宽差） | 相当 | 更优 |

> Recompute 开销永远 ≤ swap 延迟的 20%。

## 与同类对比

| 维度 | vLLM/PagedAttention | Orca [60] | FasterTransformer [31] | FlexGen [46] |
|---|---|---|---|---|
| KV 存储 | 非连续 paged blocks | 连续 chunk + buddy alloc | 连续 chunk | 连续（offline 离线 swap） |
| 内存碎片 | ~0（≤1 block） | 严重（20–38% 有效） | 同 Orca(Max) | — |
| 内存共享 | block 级 COW（跨请求/序列） | 不支持 | 不支持 | 不支持 |
| 调度 | FCFS + all-or-nothing 抢占 | iteration-level scheduling | 无自有调度（外接 Triton） | offline |
| 恢复机制 | swap / recompute 二选一 | — | — | swap weights+states |
| 适用场景 | 在线高吞吐 serving | 在线 serving | 低延迟推理 | 单卡低显存离线推理 |

- **vs Orca**（§9 Comparison to Orca）：互补——Orca 靠 iteration-level scheduling 提升并发，vLLM 靠内存利用率让更多请求 working set 装入显存。vLLM 在 Orca 之上再 2–4×。Orca 的细粒度调度反而使内存管理更难，凸显 vLLM 技术的必要性。
- **vs FlashAttention [13]**（§9）：FlashAttention 做 tiling+kernel 优化降低 attention 峰值显存与 I/O；vLLM 引入的是**在线服务场景下的 block-level 内存管理新范式**，正交方向。
- **vs OLLA [48]**（§9）：OLLA 优化 tensor 生命周期/位置减碎片，但不做 block 级管理或在线 serving。

## 跨论文关系（→ MOC 谱系）

vLLM/PagedAttention 是 **KV-cache paged-memory 谱系的根节点**，OS virtual memory 思想首次系统化引入 LLM serving：

- **根（本论文）** [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] — paged KV block + block table + COW + preemptive swap/recompute。
- → **RadixAttention / SGLang** [[sglang-efficient-execution-of-structured-language-model-programs]] — 在 paged KV 之上引入 Radix Tree 自动复用共享前缀；把 vLLM 的"显式预定义 prefix 共享"升级为"自动 prefix 树"，扩展到 structured programs。
- → **Mooncake** [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — 跨节点 KV pool，把单机 paged KV 概念推广到 disaggregated prefill/decode 架构，KV cache 作为全局可寻址资源；vLLM 的 block 抽象是其跨节点迁移的基础单元。
- → **Sarathi** [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — chunked prefill + piggybacking decode，与 paged KV 协同：分块 prefill 写入 block table，复用 vLLM 的非连续块存储自然容纳 chunk 边界。
- → **KV-cache 管理综述** [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — PagedAttention 是综述中"memory management / paging"主线的奠基工作，后续 eviction、compression、hierarchy（GPU/CPU/disk）均建立在其 block 抽象之上。

## 局限与边界

1. **Kernel 开销**（§7.1）：PagedAttention kernel 比 FasterTransformer 高 20–26% latency（block table 访问、分支、变长）；但仅限 attention 算子，被吞吐收益覆盖。极端低 batch、纯延迟敏感场景需权衡。
2. **Block size 折中**（§7.2）：过小→GPU 并行不足；过大→内部碎片+共享概率下降。默认 16 是经验值，非通用最优。
3. **Swap 在小 block 下劣化**（§7.3）：小 block 导致大量小数据传输，PCIe 带宽利用率差；此时 recompute 更优。需根据 block size 选恢复策略。
4. **适用边界**（§8 Discussion）：paging 不普适于所有 GPU 工作负载。DNN 训练（tensor shape 静态，可提前优化）、非 LLM DNN serving（compute-bound）引入 paging 反而因 memory indirection 与非连续块访问降性能。前提是工作负载满足"动态分配 + 显存容量瓶颈"。
5. **未触及 KV 量化/压缩**：本文只做内存管理，不涉及 KV cache 的精度压缩（后续工作 int8/int4 KV、H2O 等正交方向）。
6. **Prefix 共享需显式预定义**（§4.4）：原论文要求服务提供方预先 reserve 共享前缀物理块；自动 prefix 共享是后续 RadixAttention 才补齐。
7. **单 GPU 中心化 scheduler**（§4.6）：scheduler 单点；跨节点 KV 池未覆盖（Mooncake 方向）。
8. **仅评估 1 小时 trace**（175B 仅 15 分钟，§6.1），长尾分布、突发流量下抢占行为未充分评估。
