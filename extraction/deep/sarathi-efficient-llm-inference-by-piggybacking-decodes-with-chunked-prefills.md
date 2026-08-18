# SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills — 技术点深读（DEEP 2026-08-18）

> 独立文件，extract_phase1 重跑不丢。一体化深读：文本/图/表/公式交织分析，图解读织进各节（cite Figure N（p.X）+ M3 要点）。
> 论文：SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills · Agrawal, Panwar, Mohan, Kwatra, Gulavani, Ramjee · Microsoft Research India + Georgia Tech · arXiv:2308.16369v1 (31 Aug 2023)

## 核心问题

LLM 推理每个请求分两阶段：prefill 阶段并行处理整段 prompt、单条即可饱和 GPU compute；decode 阶段每步自回归生成 1 token、memory-bound 且 GPU 利用率极低。论文 §1、§3.1 用 LLaMA-13B/A6000 实测给出两条关键数据，并与 arithmetic intensity 直接挂钩：

- **Decode-per-token vs prefill-per-token**：batch size=1 时 decode 每 token 代价是 prefill 的 **~200×**，batch=2 时 ~100×，batch=18 时仍 ~16.7×（§3.1，Figure 3（p.3））。M3 解读 Figure 3/4（p.3-4）进一步指出：prefill 即使 batch=1 即 compute-bound、吞吐近恒定（≈180 tokens/ms），而 decode 因 vector-matrix 乘法 arithmetic intensity 比 prefill 低**两个数量级**——这就是 200× 差距的根因；只有到 batch=256（单层测试）decode 才转向 compute-bound，但全模型下因 KV-cache 占用只能塞下 batch=18（seq=1K），实际可承载范围内 decode 始终 memory-bound（§3.1，Figure 4（p.4），M3：bottom 子图 4b 显示 decode 各 op 的 arithmetic intensity 比 prefill top 子图低 >100×）。
- **饱和点差异**：prefill 在 B×L≥512 即达 ~180 tokens/ms 峰值（单条 prompt L≥512 即饱和）；decode 单层要到 batch=256 才转 compute-bound，但全模型 batch 上限 18，"practical 范围内 decode 仍 memory-bound"。

第二个问题来自 **Pipeline Parallelism（PP）**：PP 跨节点部署是 large model 的唯一可行方案（TP 需 NVLink，cluster-scale 无 NVLink 时只能 PP），但 Orca iteration-level scheduling 在 inference 下仍有 bubbles。论文 §3.2（Figure 5（p.5））识别三类 bubble，M3 解读其物理图景：2-way PP 跨 GPU1/GPU2 调度 4 请求 A-D，micro-batch 在 GPU1 上 A₂→B₂→C₂→D₂ 后跟三段 hatched 空闲 PB₁/PB₂/PB₃，GPU2 时间偏移同样空转：

- **PB1**：连续微批 prefill token 数不同（prompt 长度差异）；
- **PB2**：prefill 后接 decode 的计算时差（cost 量级差）；
- **PB3**：decode attention cost 随 KV-cache 累积上下文长度变化（同是 decode、时长各异）。

bubbles 即 GPU 空转、直接掉吞吐。FasterTransformer/FastServe 用 micro-batch 但不处理 bubble；Orca [48] 声称 iteration-level scheduling 消除 bubble，论文证明其仍存在。§1（Figure 1（p.1））同时给出对照：M3 解读 (a) baseline 下每请求整段 prefill（A_p/B_p/C_p/D_p）+ decode，prefill 时长不均造成下游 GPU "Bubble" 空闲；(b) SARATHI 把 prefill 切成等长 chunk（A_p1/A_p2/…）并 piggyback decode，uniform chunk 消除跨 GPU bubble、decode 几乎零成本搭便车——这正是后文 chunked-prefills + decode-maximal batching 的可视化总览。

## 关键创新点

### 1. Chunked-prefills（§4.2）
- **机制**：把一条 prefill 请求切成等大 chunk，每个 chunk 跨一个 iteration 计算。两条 insight 支撑：(i) 单条 prefill 在 512 token 即可饱和 GPU（LLaMA-13B/A6000），chunk=256 时仅损失 ~12.5% 峰值吞吐；hidden dim 越大饱和点越低（GPT-3 hidden=12288，A100 单层在 chunk=256 即达峰，§4.2）。(ii) 生产 prompt 通常 1K–4K，足够切片。
- **数学等价**（Figure 6（p.6））：通过精心设 attention mask 保证 chunked-prefill 与 full prefill 数学等价。M3 解读：三 successive iteration 的二值 mask 矩阵——iteration 1（q0-q3/k0-k3）标准下三角 causal；iteration 2（q4-q7/k0-k7）当前 chunk 内下三角 + 对之前 chunk 所有 key（k0-k3，绿色）full attention；iteration 3 同模式。每个 query token `q_i` 只能 attend 到其之前的 key/value（含同 chunk 内前序 token），后续 chunk 的 KV 在本 chunk 不可见。这种 mask 设置使 chunked-prefill **数学等价于 full prefill**，同时启用 compute-saturation 调度。
- **两类开销**（§4.2 Overhead + §5.4 消融）：
  1. **Arithmetic intensity 下降**：chunk 越小 GPU 利用率越低，可一次 profile 选 chunk size。
  2. **KV cache 重复加载**：N 个 chunk 时第 1 个 KV 被加载 N 次、第 2 个 N−1 次……但 attention 仅占 forward pass 的小头（Table 2 显示 attention 在 prefill 仅 ~10/234.8ms），故对端到端影响有限。
- **§5.4 量化**（Figure 13（p.13），M3 三 panel：a=prefill-only attention 开销，b=chunked vs full prefill，c=端到端 batch）：chunk=64 时 attention 开销 ~3×、整体 prefill 开销 ~5×；chunk=256 限制 prefill 损失 ≤20%，chunk=512 ≤10%。chunk=64 靠 piggybacking 补回、最终匹配 baseline；chunk=128 反超 +1.16×（piggyback 更多 decode 抵消 prefill 慢）。M3 还点出**可见的 tile-quantization 效应**：chunk size 为 128 倍数（如 256）优于 320——直接呼应 §4.4 的 tile 陷阱。

### 2. Decode-maximal batching（§4.3）
- **机制**：一个 hybrid batch = **1 个 prefill chunk + 尽可能多的 decode token 填满剩余 slot**。关键操作是 **fused linear operation**：prefill chunk 与 decode token 在 preproj/postproj/ffn 等线性算子上合并成单次 matmul，prefill 的 weight 一旦从 HBM 取出即被 decode 复用——decode 从 memory-bound 转为 compute-bound。attention 仍 prefill/decode 分开算（decode 之间 batched，prefill chunk 单独）。
- **关键 insight**：每请求只有 1 个 prefill phase 但多个 decode phase，prefill 请求数远不够给所有 decode 配 piggyback。Chunked-prefill 把 1 个 prefill 切成 N 个 chunk → 单条 prefill 即可服务 N 个 hybrid batch → 把 piggyback 覆盖率从"请求级"放大到"chunk 级"（§1 末、§4.1）。
- **最大 batch size**（§4.3.1 Decode batch）：`B = ⌊(M_G − M_S) / (L·m_kv)⌋`，其中 `M_G` GPU 总显存、`M_S` 模型参数显存、L 最大序列长度、`m_kv` 每 token 的 K/V pair 显存。baseline decode-only 可用 B，SARATHI 只能 B−1（多出 1 个 slot 给 prefill chunk，其 KV cache 须驻留到对应 decode 启动）。
- **效果**（§4.3.1 Table 2，LLaMA-13B/A6000）：baseline decode-only 每 token 12.49ms，decode-maximal 仅 1.2ms，**~10× 提速**；prefill per-token 0.229ms 不变。decode 的 marginal cost 几乎为零（线性算子）。这与 Figure 8（p.9，M3 解读 grouped bar：batch=2/seq=1K 时 decode speedup 峰值 ~10×，随 batch 增大单调下降至 batch=18 的 2.5–3×，短序列始终优于长序列）一致——speedup 随 batch 上升而下降的原因：baseline decode 越大越高效；随序列长度上升，attention 二次增长蚕食 SARATHI 改进空间（仅线性算子受益）。论文给出 decode speedup 总区间 **2.8×–10×**（§5.1.1）。

### 3. Chunk size 选择 + Tile quantization（§4.4）
- **P:D ratio 分析**：定义 P:D = prefill token / decode token。chunk 越小能 piggyback 的 decode 越多（chunk=128 时 P:D>42 即可覆盖所有 decode；chunk=256 时 P:D>84），但 prefill 效率下降。
- **峰值条件**：完美 piggyback（无 idle slot）发生在 `P:D = C/(B−1)`，即 prefill chunk 数 = 所需 decode iteration 数。例：C=256，B=18，则 P:D≈14 时 throughput 峰值 1.27×（§5.1.3，Figure 9a（p.9））。
- **Tile quantization**（§4.4，Figure 7（p.7），M3 解读：x 轴 seq 0-1024，y 轴 0-250ms，preproj/postproj/ffn/total 四曲线分段线性，在 batch 边界附近 tile-quantization 跳变）：GPU matmul 按 tile 分块，矩阵维度整除 tile size 时效率最高。实验 tile=128，seq 128→256 时 iteration 仅 +27%（55→69.8ms），但 256→257（+1 token）即 +32%（→92.33ms）。M3 进一步点出 FFN 占 per-iteration cost 的 ~2-3× attention，tile-quantization 在长序列上成为 first-order concern。**选 chunk size 第二原则**：保证 `chunk_size + piggybacked_decode_count` 为 tile size 倍数。如 chunk=256、tile=128、最大 B → 实际 chunk size 应取 `256 − (B−1)`。
- **§5.1.3 实测**（Figure 9（p.9）三 subplot：1K/B=18、2K/B=10、3K/B=6，归一化吞吐 vs P:D 0-200）：C=256 在 P:D=14 给 1.27×；C=512 在 P:D=28 给 1.23×；C=128 因 arithmetic intensity 低而表现差。P:D 太低（无足够 prefill chunk）或太高（无足够 decode）都会使增益掉回 ~baseline。峰值增益在 P:D balanced 时取得——"既不 dominated by prefill 也不 dominated by decode"。

### 4. 应用到 Pipeline Parallelism（§5.3）
- **机制**：hybrid batch 计算量近似均匀 → PP 微批执行时间一致 → 消除 PB1/PB2/PB3 三类 bubble。
- **实验设置**：GPT-3（96 层，hidden=12288），64×A100，8-way TP + 8-way PP，profile-driven simulation（回归模型，与 8-GPU DGX 实测误差 ≤5%）。Batch size：TP+PP=27，TP-only=11。P:D=10，序列长 1K–4K（Zipf θ=0.4），10K 请求，chunk=256。
- **效果**（§5.3，Figure 12（p.12），M3 解读两 subplot：a 是 bubble time CDF、SARATHI 在 ~20s 即饱和到 CDF≈1 而 TP+PP 拖到 ~85s；b 是完成时间曲线，10K 请求时 TP+PP ~3700s、TP-only(8 replicas) ~2900s、SARATHI 最快 ~1900s）：
  - **Median bubble time / request 降 6.29×**（SARATHI vs baseline TP+PP Orca-style）。
  - **端到端吞吐**：SARATHI-TP+PP 比 baseline TP+PP **×1.91**，比 TP-only（8 副本）**×1.48**。
  - baseline TP+PP 虽然 batch 比 TP-only 大 2.45×，但因 bubble 太大反被 TP-only ×1.28 反超——SARATHI 把 PP 变成"attractive option"。M3 要点：SARATHI 以较小 batchable KV cache 换更紧的 prefill-decode 融合，使 PP 推理超越 TP-only。

## 表格（原文结构化）

### Table 1：Transformer decoder block 各算子 tensor shape（§2.1）
| Operation | Input(s) | Weight(s) | Output(s) |
|---|---|---|---|
| preproj | [B,L,H] | [H,H] | [B,L,H] |
| attn | [B,L,H] | - | [B,L,H] |
| postproj | [B,L,H] | [H,H] | [B,L,H] |
| ffn_ln1 | [B,L,H] | [H,H2] | [B,L,H2] |
| ffn_ln2 | [B,L,H2] | [H2,H] | [B,L,H] |

注：L=1 during decode（除 attention），H 为 embedding size（LLaMA-13B=5120、LLaMA-33B=6656、GPT-3=12288）。该表是 §3.1 arithmetic intensity 分析与 §4.3 fused linear op 的 tensor 维度依据——decode 阶段 L=1 使线性算子退化为 vector-matrix（低 arithmetic intensity），正是 decode-maximal batching 把它升回 matrix-matrix 的根本。

### Table 2：Per-token time 对比（LLaMA-13B/A6000，§4.3.1，单位 ms）
| Batching Scheme | Linear | Attn | Total | Prefill/token | Decode/token |
|---|---|---|---|---|---|
| Prefill-only（prompt=1024，batch=4） | 224.8 | 10 | 234.8 | 0.229 | - |
| Decode-only（batch=4，seq=1024） | 44.28 | 5.68 | 49.96 | - | 12.49 |
| **Decode-maximal**（1021 prefill + 3 decode） | 223.2 | 15.2 | 238.4 | 0.229 | **1.2** |

结论：decode per-token **降一个数量级**（12.49→1.2ms）；prefill per-token 不变；attention 开销仅 +5.2ms（decode 部分边际，因线性算子已 fused 复用 weight）。这张表是创新点 2 的核心数字证据，与 Figure 8 的 2.8×-10× 量级一致。

### Table 3：评测配置（§4.5）
| Model | GPU | Num GPUs | Per-GPU Mem(GB) | Mode |
|---|---|---|---|---|
| LLaMA-13B | A6000 | 1 | 48 | Deployment |
| LLaMA-33B | A100 | 1 | 80 | Deployment |
| GPT-3 | A100 | 64 | 80 | Simulation |

模型配置：LLaMA-13B（40 层，40 头，H=5120）、LLaMA-33B（60 层，52 头，H=6656）、GPT-3（96 层，96 头，H=12288）。nanoGPT codebase + xformers attention kernel（§4.5 实测优于 PyTorch 2.0 的 flash/math/memory-efficient variants）；预分配 KV cache。

### Table 4：峰值吞吐增益（§5.1.2，chunk=256）
| Model (GPU) | Seq Len | Batch Size | P:D Ratio | Decode Speedup | E2E Throughput Gain |
|---|---|---|---|---|---|
| LLaMA-13B (A6000) | 1K | 6 | 50:1 | 5.45× | 1.33× |
| LLaMA-13B (A6000) | 2K | 6 | 50:1 | 3.26× | 1.26× |
| LLaMA-13B (A6000) | 3K | 6 | 50:1 | 2.51× | 1.22× |
| LLaMA-33B (A100) | 1K | 10 | 28:1 | 3.83× | 1.25× |
| LLaMA-33B (A100) | 2K | 5 | 63:1 | 4.25× | 1.22× |
| LLaMA-33B (A100) | 3K | 3 | 127:1 | 3.51× | 1.14× |

注意：A100 增益低于 A6000，因 A100 的 FLOPs/MemBandwidth ≈156 vs A6000 ≈53，需要更大 chunk（或更大 hidden）才能不丢 prefill 效率。Decode speedup 范围 2.8×–10×；端到端 ~25%（因只优化 decode，不优化 prefill）。序列变长增益递减：attention 二次增长蚕食改进空间。

### Figure 9/11 关键峰值（§5.1.3, §5.2，LLaMA-13B/A6000，相对 baseline 归一化吞吐）
| Seq Len | Batch | Chunk | Peak P:D (=C/(B-1)) | Peak E2E Throughput |
|---|---|---|---|---|
| 1K | 18 | 256 | 14 | 1.27× |
| 1K | 18 | 512 | 28 | 1.23× |
| 1K | 18 | 128 | (低 arithmetic intensity) | 显著更低 |

### Figure 10 操作分解（§5.1.4，LLaMA-13B/A6000，M3：2×3 grid，baseline 橙/SARATHI 蓝，分解 preproj/attn/postproj/ffn）
M3 关键观察：SARATHI(蓝) 在所有配置下一致优于 baseline(橙)，FFN kernel 占总 runtime ~50-60% 且 SARATHI 下几乎不变——speedup 主要来自 attention 与 postprojection 的降低（实际是线性算子 fused 后复用 weight）。chunk=512 比 chunk=128 绝对吞吐更高（arithmetic intensity 更好），但最优 P:D 点右移。整体改进 10-25% 跨 batch 与 seq 持续存在。论文 §5.1.4 给出量化：linear 算子 runtime 降 1.05×-1.6×，FFN 最高（1.3×-1.6×），preproj/postproj 仅 1.05×-1.38×。

### PP 仿真结果（§5.3，GPT-3，64×A100）
| 部署 | Batch | Median Bubble/req | E2E 完成时间（相对） |
|---|---|---|---|
| TP+PP + Orca-style（baseline） | 27 | 1×（基线） | 1×（~3700s @10K req） |
| TP-only（8 副本） | 11 | - | 1.28×（~2900s） |
| **TP+PP + SARATHI**（chunk=256） | 27 | **降 6.29×** | **1.91×**（~1900s），1.48×（vs TP-only） |

## 与同类对比

- **vs Orca**（iteration-level + 整段 prefill 一 iteration 跑完，§5.2，Figure 11（p.11））：把 Orca 评估为 best-case（整条新 prefill 与 ongoing decode overlap）和 worst-case（请求同步到达，等同 baseline）。M3 解读 Figure 11：a 是 1K/2K/3K 四 bar 组（Baseline/Orca worst/Orca best/SARATHI），SARATHI 三序列稳定 1.27×/1.25×/1.23× 而 Orca best-case 在 1K 仅 1.11×、随序列变长退回 baseline；b 是 1K/B=18 下 P:D 扫描三 chunk size + Orca best，最优 P:D 随 chunk size 右移。**关键差异**：Orca 的 piggybacking 是"side-effect"，且受限于单次整 prefill 的窗口——P:D 高时很快耗尽 prefill token 后退化回 decode-only；SARATHI 用 chunk 把 piggyback 机会放大 N 倍且可控。best-case Orca 可视为 SARATHI 在 `C = max_seq_len` 时的退化特例。
- **vs FasterTransformer**（request-level batching，§4.1）：每 batch 等所有请求完成才换批，短请求要 pad 到最长，浪费 compute；SARATHI 用 iteration-level（与 Orca/vLLM/TGI 同类）但额外做 chunking + piggybacking。
- **vs vLLM/TGI**（iteration-level，§4.1）：同为 iteration-level scheduling，但未关注 batch 内 prefill/decode 组合与执行时间方差，仍产生 bursty utilization 与 pipeline bubble；SARATHI 显式构造 uniform compute hybrid batch。论文未对 vLLM 的 PagedAttention 做单独对比（SARATHI 在 nanoGPT 上实现，用预分配 KV cache）。
- **vs FlashAttention / xformers**（kernel-level，§7.1）：正交，SARATHI 实测用 xformers attention kernel（性能优于 PyTorch 2.0 的 flash/math/memory-efficient variants，§4.5）。
- **vs FlexGen**（offline 大模型单 GPU，§7.1）：FlexGen 走 offload + 量化 + 调度的离线高吞吐路线，与 SARATHI 的在线 serving 场景不同。
- **模型创新类**（multi-query attention [41]、quantization [30-32,47]、MoE [23,33,36]、retentive networks [44]，§7.2）：与 SARATHI 正交，可叠加。

## 跨论文关系（→ MOC 谱系）

- **直接被 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] 继承**：Sarathi-Serve 是 SARATHI 的 production-grade serving 演进——chunked-prefills + decode-maximal batching（piggyback）机制与命名直接源自本文。Sarathi-Serve 新增 stall-free batching（Algorithm 3，token-budget 顺序填充）、TBT SLO 反推 token budget τ、PP 优化量化、与 vLLM/Orca 的端到端 capacity 对比。两文同一作者团队（Microsoft Research India + Georgia Tech）。**SARATHI 是 chunked-prefill 思想的根**，Sarathi-Serve 是它做成在线 server 的产物。
- **与 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]（vLLM/PagedAttention）互补**：vLLM 用 virtual-memory 抽象做 KV 增量分配，与 SARATHI 的 chunked-prefill 正交——PagedAttention 天然吸收 chunk 边界（每 chunk 写入自己的 KV page，无需 contiguous），二者可叠加。SARATHI 原实现用预分配 KV cache，Sarathi-Serve 后续在 vLLM fork 上实现即两者合一。论文 §7.1 明确把 vLLM 列为互补工作（dynamic memory allocation 帮 SARATHI 支持更大 batch）。
- **与 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] 对比**：Mooncake 走 disagg 路线（prefill/decode 物理分离到不同 replica + KV 跨节点池化），用"物理隔离"消除 prefill-decode 干扰；SARATHI 走 collocated hybrid batch 路线（同 replica 内 chunk 混合），用"时间分片 + piggyback"消除干扰。SARATHI 的优势是不需 KV 跨 replica 迁移（无 high-bandwidth interconnect 也能用），代价是 prefill 不能完全独立高效（piggyback 时 decode 占部分 slot）。两种哲学对 prefill-decode 干扰的不同解法。
- **与 [[huawei-cloud-model-as-a-service-on-the-cloud-matrix384-superpod]]（CloudMatrix §4.3）关联**：CloudMatrix 讨论 chunk-prefill overhead——SARATHI 是该思想的原始出处，CloudMatrix 在超大规模 superpod 场景下评估其开销与部署考量。
- **PP genealogy**：SARATHI 在 LLM inference PP 调度谱系中位于"chunked-prefill 消除 bubble"的根节点；Orca 是其前置基线（iteration-level scheduling 首次提出），Sarathi-Serve 是其下游演进，vLLM/工业界 serving engine 后续普遍采纳 chunked-prefill 作为基线。

## 局限与边界

- **只优化 decode，不优化 prefill**：端到端吞吐增益 ~25%（1.33×/1.25×）远低于 decode 单项增益（~10×），因 prefill per-token 时间几乎不变（Table 2：0.229ms 不变），整体提升受 prefill 占比限制（§5.1.2 末段）。
- **Chunking 非零开销**：小 chunk 损 prefill 效率（chunk=64 整体 prefill 慢 5×，§5.4，Figure 13b）；需一次性 profile 选 chunk size。论文未做自适应动态 chunk size。
- **Tile-quantization 陷阱**：chunk size + decode count 须整除 tile size（128），否则 prefill 显著变慢（+1 token → +32%，Figure 7）。M3 解读 Figure 7 同样强调 tile-quantization 在长序列上成为 first-order concern。硬件感知调参必要。
- **简化假设**：除仿真实验外，假设同一 batch 内所有请求 prefill/decode token 数相同；真实场景序列长度差异大（§6 Discussion 明确列出）。
- **评测规模有限**：单 GPU 实测仅 LLaMA-13B/A6000 与 LLaMA-33B/A100；GPT-3 大规模为 profile-driven simulation（回归模型，误差 ≤5%），非真实部署。序列长 ≤3K、P:D 范围 1–200。
- **长 context 未覆盖**：论文明确指出 attention cost 随 token 数二次增长，10K–100K 序列是新挑战（§6），本文未评测。
- **未做在线 serving 调度策略**：SARATHI 聚焦 execution layer 的 batch 构造，latency/queuing/fairness 等调度策略需上层补充（§6）——这正是 Sarathi-Serve 后续补齐的方向。
- **未对比 PagedAttention + 动态内存**：原实现用预分配 KV cache（§4.5），batch size 上限受 L 限制；与 vLLM PagedAttention 的协同增益未在本文量化。
- **最优 chunk size 依赖先验 P:D**：理想 chunk size 需匹配 workload 的 P:D，论文承认 P:D 未知时的动态选择是 future work（§6）。
