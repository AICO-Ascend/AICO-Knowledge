# DeFT — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：DeFT: Decoding with Flash Tree-attention for Efficient Tree-structured LLM Inference · arXiv:2404.00242 (ICLR 2025)

## 核心问题

LLM 推理由 sequence-based decoding 转向 tree-based decoding（few-shot prompting、多步推理/ToT、speculative decoding 等），单次迭代生成的 token 数急剧膨胀。论文给出一个直观对照（§1, Table 1）：对"排序 128 个数字"任务，CoT 仅生成 525 token，而 ToT 生成 38,315 token；对应端到端延迟从 21s 飙到 380–429s。

tree-based decoding 的核心瓶颈不在计算而在 **memory access (IO)**——LLM decoding 本就是 memory-bound（§3.1 引 Shazeer 2019, Kim 2023），A100 HBM 1.5–2 TB/s、shared memory 19 TB/s 的层级差使 KV cache 在 HBM↔shared memory 之间的搬运主导延迟。现有系统在三个层面存在 prefix 冗余：(1) computation（重复重算共享 prompt 的 KV），(2) memory storage（重复存储共享前缀 KV），(3) **memory access / IO**（在 attention 计算中反复加载共享前缀 KV）。前两者已被 vLLM/SGLang/Medusa/SpecInfer 部分解决，但 IO 层面几乎被忽视，而这恰是 memory-bound 场景下最关键的一层。

DeFT 锁定两个挑战（§1）：
- **C1 — prefix-awareness in KV IO**：现有 memory-efficient attention（FlashAttention/FlashDecoding）面向 sequence decoding，不感知树拓扑，共享前缀 KV 被反复加载。
- **C2 — load balancing of tree-structured KV**：FlashDecoding 的 sequence KV chunking 不能直接套到树上；按 node 切分会导致 token 长度严重不均（speculative decoding 中某 node 可能只有 1 token，root 却有数千），SM 空闲严重。

## 关键创新点

1. **KV-Guided Grouping（§3.3）— 反转 Q/KV 分组指示器，消除前缀 KV 冗余 IO**
   - 机制：现有 FlashAttention/FlashDecoding/Radix Attention 采用 **Q-Guided Grouping**——以 query 为指示器，把每个 query 与其对应 KV 组成一组；于是 prefix KV0 会被 Qa 和 Qb 各加载一次。DeFT 反过来以 KV 为指示器，把每个 node 的 KV 与 **所有共享它的 queries** 组成一组，则 prefix KV0 只加载一次。代价是 query 被多次加载，但 query 长度通常是 root-to-leaf 路径数（数十 token），KV 是数百–数千 token，故 query IO 开销可忽略（§3.3 末段）。
   - 效果：对两 cascade 树示例，prefix KV0 IO 从 2 次降为 1 次；在 IO 复杂度上（Table 12, Appendix A.5），DEFT-Node/Flatten 的 KV cache IO 为 `O(2·dhead·Ntree)`，而 sequence-based 方法为 `O(2·dhead·ΣNi)` = `Fs` 倍冗余（`Fs = ΣNi/Ntree` 为前缀复用因子）。这是 DeFT 一切收益的根源。

2. **Flattened Tree KV Splitting（§3.3, Remark 3.1）— 三子机制保证负载均衡**
   - (a) **Depth-first Flatten strategy**：把树按深度优先展平成线性 KV 序列再切块。关键洞察：父节点（如 KV0）的 queries 包含子节点（KV1）的 queries，深度优先（而非广度优先）展平能最大化"被分配到同一 chunk 的不同 node 之间的 query 重叠"，减少 `QK^T` 中被 mask 掉的冗余计算。
   - (b) **Evenly block-wise strategy**（核心）：把展平后的 KV 按固定 block size（实现取 128，§4.4/GEMM 常规尺寸）均匀切块，使每个 QKV group 的 KV 长度近似相等，从而各 SM 计算量一致，避免全局归约时某 SM 长时间空等（§3.2 指出 Equation 1 的 global reduction 需要所有 partial attention，木桶效应）。
   - (c) **Bit Causal Mask（BCM）**（借自 SpecInfer, Miao 2023）：用一组 64-bit int 记录因果信息，单 chunk mask IO 仅几十 byte，远低于 Medusa 的 dense causal mask（`nq×nkv` 矩阵，materialize 在 HBM）。
   - 效果：DEFT-Node 单 SM 利用率 7.6% compute / 17.4% memory、低利用率时间 82.35%；DEFT-Flatten 提升到 21.2% / 51.9% / 0.00%（Table 14, A100, 64 queries + 4k prompt）。

3. **DeFT Attention Kernel — 两阶段、融合、树拓扑感知（§3.2, Appendix A.4, Figure 9/10）**
   - 机制：在 QKV Preparation Phase 之后，Attention Calculation Phase 分两 Stage：
     - Stage 1: 对每个 QKV group `Gi` 在一个 thread block 上跑 FlashAttention（含 Kernel Fusion + Tiling，避免 `QK^T` / `Softmax` 等 partial result 落 HBM），输出 partial attention `PAi` 与 `LSEi`。
     - Stage 2: **Tree-Topology-Aware Global Reduction**——FlashDecoding 的 global reduction 只懂序列，不感知树；DeFT 按 query 重新映射各 group 的 `PA`/`LSE`，按树拓扑聚合得到每个 query 的最终 attention（Equation 1 的 online Softmax 合并）。
   - 效果：相比 Tree Attention-Medusa（PyTorch GEMM，无 fusion/tiling，partial result 在 HBM↔shared memory 来回搬运，Figure 8），DeFT 几乎消除 partial result IO。在 IO 复杂度表（Table 12）中，DEFT-Flatten 的 `QK^T`/`Softmax`/mask 项全为 0 或 `O(Ntree)`（仅 BCM 项非零），而 Medusa 各项为 `O(ln·Ntree)`。论文指出 Llama（`dhead=128`）下当 `ln=29` 时 partial result IO 已与 KV cache IO 相当——节点数一大 Medusa 就崩。

4. **理论 IO 复杂度证明（Appendix A.5, Table 11/12）**
   - 给出共享因子 `Fs = (ΣNi)/Ntree`，证明 sequence-based 方法（Naive/FlashDecoding/Radix）KV IO 是 DeFT 的 `Fs` 倍。并证明 Medusa 的 partial result IO 随 `ln` 线性增长，DeFT 几乎不增长。配合 online Softmax 合并的数学等价性证明（Equation 1, Appendix A.3），DeFT 与 vanilla attention 数学等价，实测 relative attention error ~0.4%、relative PPL error ~1e-6（Table 15）——误差来自浮点非结合律，与 FlashDecoding/Radix 同量级。

5. **系统支持：树结构 KV 管理 + 可编程 branch/prune（Appendix A.1）**
   - 四组件：Branch Controller（用户自定义函数控制分支/剪枝）、Sequence Tree Manager（维护树拓扑）、KV Cache Manager（树结构 KV，支持 paged 与 unpaged）、Model Interface。paged 内存额外好处：非连续存储按指针寻址，无需把树结构 KV materialize 成单 tensor 即可喂给 attention kernel。

## 表格（原文结构化）

**Table 1（§1）— CoT vs ToT 在排序 128 数字任务上的效率对比**

| Method | Latency (s) | IO-KV (TB) | IO-PA (TB) |
|---|---|---|---|
| Flash-Decoding + CoT | 21 | 0.6 | 0 |
| Flash-Decoding + ToT | 429.65 | 59.96 | 0 |
| Tree Attention + ToT | 380.87 | 12.40 | 3.69 |
| **DeFT-Flatten + ToT** | **94.67** | **12.40** | **0** |
| Speedup over best baseline | 4.02× | — | — |

**Table 2（§3.3）— QKV 分组策略对比**

| Attention Algorithm | Grouping Indicator | KV Split Granularity | IO Redundancy | Load-balancing |
|---|---|---|---|---|
| Flash-Attention | Q-guided | - | KV | ⋆ |
| Flash-Decoding | Q-guided | by block | KV | ⋆⋆⋆ |
| Radix Attention | Q-guided | by block | KV | ⋆⋆⋆ |
| Tree Attention-S (SpecInfer) | Q-guided | by block | KV and BCM | ⋆⋆⋆ |
| Tree Attention-M (Medusa) | entire tree | by GEMM in PyTorch | DCM and PA | ⋆⋆⋆ |
| Vanilla Tree Attention | entire tree | no split | DCM and PA | ⋆ |
| DEFT-Node | KV-guided | by tree node | Q | ⋆ |
| DEFT-Node-Chunk | KV-guided | by node then block | Q | ⋆⋆ |
| DEFT-Flatten | KV-guided | by block | Q and BCM | ⋆⋆⋆ |

**Table 5（§4.3）— 平均 decoding latency (s)，DEFT-Flatten vs baselines（A100 80GB, Llama3-8B）**

| Memory | Method | Few-shot b=20 | b=30 | b=50 | Sorting | Document | Keyword | Set | Spec t=32 | t=64 | t=128 | t=256 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Unpaged | Flash-Decoding | 78.96 | 131.19 | 191.09 | 429.65 | 241.20 | 32.75 | 51.76 | 574.50 | 1128.45 | ⋆(OOM) | ⋆ |
| Unpaged | Tree Attention-Medusa | 52.58 | 103.90 | 144.07 | 380.87 | 236.86 | 33.52 | 50.10 | 263.40 | 483.35 | 924.97 | 1881.51 |
| Paged | Radix Attention | 12.37 | 14.08 | 16.54 | 104.79 | 69.61 | 11.25 | 17.03 | 54.66 | 69.75 | 108.56 | 188.66 |
| Paged | **DEFT-Flatten** | **9.98** | **10.99** | **12.48** | **94.67** | **66.95** | **10.90** | **16.10** | **42.23** | **46.60** | **56.96** | **84.27** |
| | Attention Speedup / Radix | 1.73× | 1.63× | 1.70× | 1.39× | 1.15× | 1.21× | 1.34× | 1.96× | 2.41× | 3.11× | 3.59× |
| | Decoding Speedup / Radix | 1.24× | 1.28× | 1.33× | 1.10× | 1.03× | 1.03× | 1.05× | 1.29× | 1.50× | 1.91× | 2.23× |
| | Speedup Upper-bound (no attn) | 1.71× | 2.08× | 2.51× | 1.96× | 1.82× | 1.70× | 1.76× | 1.89× | 2.89× | 3.34× | 4.36× |

**Table 12（Appendix A.5）— IO 复杂度分解（`O(1)` = 单数据跨所有 layer/head 的 IO）**

| Method | KV cache | QK^T | QK^T/sc | Mask | M+QK^T/sc | Softmax |
|---|---|---|---|---|---|---|
| Naive Attention | `O(2d·ΣNi)` | `O(2ΣNi)` | `O(2ΣNi)` | 0 | 0 | `O(2ΣNi)` |
| Flash-Decoding | `O(2d·ΣNi)` | 0 | 0 | 0 | 0 | 0 |
| Radix Attention | `O(2d·ΣNi)` | 0 | 0 | 0 | 0 | 0 |
| Tree Attention-M (Medusa) | `O(2d·Ntree)` | `O(2ln·Ntree)` | `O(2ln·Ntree)` | `O(ln·Ntree)` | `O(2ln·Ntree)` | `O(2ln·Ntree)` |
| Tree Attention-S (SpecInfer) | `O(2d·Ntree·ln)` | 0 | 0 | `O(ln·Ntree/64)` | 0 | 0 |
| DEFT-Node | `O(2d·Ntree)` | 0 | 0 | 0 | 0 | 0 |
| DEFT-Node-Chunk | `O(2d·Ntree)` | 0 | 0 | 0 | 0 | 0 |
| DEFT-Flatten | `O(2d·Ntree)` | 0 | 0 | `O(Ntree)` | 0 | 0 |

（注：SpecInfer 的 KV IO 为 `O(2d·Ntree·ln)` 因其 Q-Guided Grouping 让每个 query 独立加载整棵树 KV——见 Remark A.3。）

**Table 17（Appendix A.7）— 端到端 IO (TB)，格式 KV-IO / partial-result-IO**

| Method | Few-shot b=20 | b=30 | b=50 | Sorting | Document | Keyword | Set | Spec t=32 | t=64 | t=128 | t=256 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Flash-Decoding | 17.62/0 | 26.43/0 | 44.05/0 | 59.96/0 | 39.74/0 | 4.68/0 | 7.01/0 | 128.72/0 | 255.16/0 | ⋆ | ⋆ |
| Tree Attention-Medusa | 1.68/1.05 | 2.10/1.98 | 2.94/4.61 | 12.40/3.69 | 10.57/3.24 | 0.58/0.18 | 1.04/0.27 | 4.02/4.03 | 4.15/8.33 | 4.18/16.77 | 4.32/34.70 |
| Radix Attention | 17.62/0 | 26.43/0 | 44.05/0 | 59.96/0 | 39.74/0 | 4.68/0 | 7.01/0 | 131.45/0 | 256.79/0 | 522.05/0 | 1044.10/0 |
| DEFT-Flatten | 1.68/0 | 2.10/0 | 2.94/0 | 12.40/0.01 | 10.57/0.01 | 0.58/0 | 1.04/0 | 4.10/0 | 4.11/0 | 4.16/0 | 4.35/0 |
| IO reduction % | 90.47/100 | 92.1/100 | 93.33/100 | 79.32/99.73 | 73.40/99.70 | 87.61/100 | 85.16/100 | 96.88/100 | 98.40/100 | 99.20/100 | 99.58/100 |

**Table 14（A.7）— GPU 利用率 microbench（speculative decoding, 64 queries, 4k prompt, Llama3-8B）**

| Method | Attn Latency (µs) | Compute Throughput | Memory Throughput | Low-Util Time Ratio |
|---|---|---|---|---|
| DEFT-Node | 961.38 | 7.60% | 17.39% | 82.35% |
| DEFT-Flatten | 226.82 | 21.19% | 51.91% | 0.00% |

**Table 9（Appendix A.3）— 与 concurrent works（single-context batch sampling）对比**

| Method | IO-aware levels | Tree KV split | Load-balanced | Goal |
|---|---|---|---|---|
| Chunk-Attention | 2 (depth≤1) | by tree depth | ⋆⋆⋆ | throughput |
| Hygragen | 2 (depth≤1) | by tree depth | ⋆⋆ | throughput |
| Bifurcated-Attention | 2 (depth≤1) | by tree node | ⋆⋆ | latency |
| DEFT-Node | all (every depth) | by tree node | ⋆ | latency |
| DEFT-Node-Chunk | all (every depth) | node then block | ⋆⋆⋆ | latency |
| DEFT-Flatten | all (every depth) | flatten then block | ⋆⋆⋆⋆ | latency |

**Table 8（§4.4）— 模型尺寸影响（Codellama-7B vs 34B）**

| Metric | Model | Few-shot b=30 | Sorting | Spec t=64 |
|---|---|---|---|---|
| Decoding Speedup | 7B | 1.34× | 1.09× | 1.85× |
| | 34B | 1.23× | 1.03× | 1.78× |
| Radix A/F-LR | 7B | 1.27 | 1.12 | 2.12 |
| | 34B | 0.80 | 0.48 | 1.66 |
| DeFT A/F-LR | 7B | 0.68 | 0.89 | 0.69 |
| | 34B | 0.45 | 0.42 | 0.49 |

## 与同类对比

- **vs FlashAttention / FlashDecoding（Dao 2022/2023）**：二者面向 sequence decoding，Q-Guided Grouping，KV IO 为 `O(2d·ΣNi)`（带 `Fs` 倍冗余）；DeFT 为 `O(2d·Ntree)`。FlashDecoding 的 sequence KV splitting 不能处理树拓扑；DeFT 的 Tree-Topology-Aware Global Reduction 是其树结构扩展。
- **vs Tree Attention-Medusa（Cai 2024）**：Medusa 用 PyTorch GEMM 切 Q/KV，无 kernel fusion/tiling，partial result（`QK^T`、Softmax）在 HBM 来回搬运 + dense causal mask，IO 随 leaf 数 `ln` 线性增长。DeFT 用 Triton fused kernel + BCM，partial result IO 归零，mask IO 降为 `O(Ntree)`。实测 speculative decoding t=256 时 DeFT attention 3.59× 加速。但 Medusa 在树宽=10 时 attention 开销与 DeFT 接近（DCM 小）。
- **vs Tree Attention-SpecInfer（Miao 2023）**：SpecInfer 用 BCM（IO 友好）但 Q-Guided Grouping，每个 query 独立加载整棵树 KV，KV IO 为 `O(2d·Ntree·ln)`——最差。且 BCM 限 64 token，不适合 tree-structured KV（论文未将其列入主 baseline，仅因 64 token 上限）。
- **vs Radix Attention / SGLang（Zheng 2023）**：本质是 FlashDecoding + paged/树结构内存管理，IO 行为同 FlashDecoding（Remark A.4）；是 decoding latency 最强 baseline，但 attention 层仍是 Q-Guided，prefix KV 不复用。DeFT 在其基础上仅替换 attention kernel 即获 1.03–2.23× decoding speedup。
- **vs concurrent single-context sampling（Hydragen / Bifurcated-Attention / ChunkAttention / RelayAttention / Cascade-inference）**：这些只处理 depth≤1（root prefix + depth-1 suffix）的特殊树，无法复用非根前缀 IO；且未解决 node 长度不均的负载均衡。DeFT 支持任意深度前缀复用 + flatten 均衡。DeFT 在 throughput 目标外更聚焦 latency。

## 跨论文关系（→ MOC 谱系）

- 属于 **speculative-decoding tree-attention 分支**，是 attention kernel 层优化，非 draft 模型/树构造策略优化。
- `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]` — DeFT 的直接 baseline 与 token tree 拓扑来源。Medusa 提供 multi-head 候选生成（树构造）+ Tree Attention-Medusa（验证），DeFT 替换后者：相同树拓扑下 DeFT-Flatten attention 1.02–1.70× over Medusa attention（Table 16），decoding 端到端最高 2.23×。两者是"上层树构造 ↔ 下层 kernel 优化"的互补关系，可叠加。
- `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]` / `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]` — EAGLE 系列改进 draft 质量（feature-level 不确定性、动态 draft tree）。DeFT 不涉及 draft 质量，只优化给定树的验证 kernel；EAGLE-2 的 dynamic draft tree 改变树形状（影响 `Fs`、`ln`），其 attention 验证阶段可直接套 DeFT kernel 获益。树越宽越深，DeFT 收益越大（§4.4 width 消融）。
- `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]` — JetSpec 并行树起草扩大候选规模。draft tree 变大 → `ln` 上升 → Medusa 的 partial-result IO 与 BCM 压力陡增，而 DeFT 的 IO 几乎不随 `ln` 增长（Table 12），是 JetSpec 类大候选树场景的天然搭档。
- `[[sglang-efficient-execution-of-structured-language-model-programs]]` — SGLang 的 Radix Attention（paged + tree 内存管理）是 DeFT 的最强 decoding baseline。DeFT 与 SGLang 同处"结构化 LLM 程序高效执行"谱系，且 DeFT 实验即基于 paged memory（Table 3），可作为 SGLang attention kernel 的 drop-in 升级。
- 旁系（非目标论文但同谱）：FlashDecoding（sequence 分支）、SpecInfer（Tree Attention-S，64-token 限制）、vLLM/PagedAttention（存储层而非 IO 层）。

## 局限与边界

1. **multi-step reasoning 收益有限**：树宽仅 10 时 KV 复用空间小，attention 仅占 decoding 30%（speculative decoding 占 50–80%），decoding speedup 仅 1.03–1.10×（Table 5）。论文自承需树宽 ≥50 才显出 1.2–1.5× 收益（§4.3）。
2. **大模型收益衰减**：Codellama-34B decoding speedup 1.03–1.78×（vs 7B 的 1.09–1.85×），因 FFN 开销随 hidden dim 增大，A/F-LR 下降（Table 8）。DeFT 只优化 attention，对 FFN-bound 的大模型帮助有限。
3. **chunk size 需手调**：实现取 128，但最优值依赖序列长度与 query 数（§4.4, Figure 15）——大 chunk 省 Query IO 冗余但 SM 数不足易空闲，需启发式或自动调优，论文未提供。
4. **BCM 的 64-token 限制迁移**：DeFT-Flatten 借 SpecInfer 的 BCM，但 DeFT 把 BCM 用于 KV block 而非整树 query，规避了 SpecInfer 的 64-token token-tree 上限。然而每个 subtree 内 node 数仍受 64-bit 限制（一个 BCM 对应一个 node 的 query 可见性），极端大 subtree 需多 mask，论文未量化边界。
5. **实现绑定 Triton + A100/RTX 4090**：仅测 NVIDIA GPU（A100 80GB、RTX 4090 24GB, Table 19），未覆盖 HBM 更宽的 H100 或 AMD/其他加速器；Triton kernel 的 portability 与极端长序列（>20k）下的 chunk 调度未充分消融。
6. **prefill 未覆盖**：DeFT 只优化 decoding 阶段 attention；prefill 占 e2e 约 5–10%（§4.3），tree-based prefill 的 IO 优化是开放问题。
7. **未与最新 FlashAttention-3 / H100 kernel 对比**：ICLR 2025 时点未纳入 FlashAttention-3 等 H100 优化 kernel 的对比，绝对加速比可能随硬件演进变化。
8. **speculative decoding 上的实测基于"回放"固定树**：实验用 Medusa 记录的 token tree 形状回放（Table 4），非端到端在线 speculative decoding 系统；在线场景下 draft 接受率波动导致树形状时变，DeFT 的稳定性（Figure 13 显示对树形状敏感的是 DEFT-Node，DEFT-Flatten 较稳）需在线验证。
