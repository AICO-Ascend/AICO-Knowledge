# Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM — 技术点深读（DEEP 2026-08-18，公式重跑）

> 独立文件：本深读内容独立存放，extract_phase1 重跑 MD/MOC 时不会被覆盖。
> 论文：Narayanan et al., "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", arXiv:2104.04473v5 (23 Aug 2021)。NVIDIA / Stanford / MSR。
> 公式权威源：extraction/formulas.json 的 6 条 LaTeX（下文以 `$$` 渲染并 cite Eq./§）；图权威源：M3 caption 文本（禁图直读）。
> 本文是 Megatron-LM 系列第二代系统论文，在 [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] 的 tensor parallelism 之上引入 pipeline，提出 PTD-P 组合与 interleaved schedule。

## 核心问题

本文攻击的不是单点算法，而是一个系统性工程问题：**"在严格 optimizer 语义下、给定 batch size 与固定 GPU 预算，如何把 tensor / pipeline / data 三种并行维度组合到数千卡上仍保持高吞吐"**（§1）。三维度需满足 `p · t · d = n`（§3.1 记法定义）。

动机由 Figure 1（p.1）压出：M3 解读要点是参数量从 ELMo 94M 到 GPT-3 175B 在两年内增长约三个数量级，log-y 轴下呈近指数曲线；叠加单 V100 训练 GPT-3 需约 **288 年**（§1，原文 "approximately 288 years with a single V100"），共同压出"必须并行"的硬约束。三条具体瓶颈：

1. **显存墙**：单卡 80GB-A100 仍无法装下大模型参数（§1 抽象"a) GPU memory capacity is limited"）。
2. **Tensor parallelism 跨节点失效**：Megatron 原生 tensor parallelism 仅在单机 NVLink 内高效，跨服务器 all-reduce 走慢速 inter-server 链路且 GEMM 被切得过小（§1, §3.2）；原生方法在 DGX A100 上对 ≤20B 模型 "works well"，更大模型 "breaks down"，由 §5.4.1 / Figure 13（p.10）定量验证。
3. **Pipeline bubble**：为保证严格 optimizer 语义必须周期性 flush pipeline，**"As much as 50% of time can be spent flushing the pipeline"**（§1，依赖 microbatch 数与 pipeline 大小之比 m/p）。Figure 4（p.3）M3 解读直接可视化：灰色 idle 格即 bubble，interleaved timeline 里 flush 提前发生。

目标产出：在 3072 块 A100 上对 1T 参数 GPT 达 **502 petaFLOP/s 聚合吞吐**，单卡 **163 teraFLOP/s ≈ 52% theoretical peak**（A100 16-bit peak = 312 TF/s，§5.1），端到端训练估计约 3 个月（1T 模型 450B tokens / 84 天，§5.1）。

## 关键创新点

### 1. PTD-P：Pipeline + Tensor + Data 三维组合的放置法则
- **机制**：Pipeline parallelism 横跨多 GPU 服务器（走 inter-node InfiniBand 点对点），tensor parallelism 限定在单机内部（走 NVLink，t ≤ 单机 GPU 数 g），data parallelism 用于继续水平扩展（§1, §2, §3）。三维度满足 `p · t · d = n`（§3.1）。§3.2 给出通信量对照：pipeline 相邻 device 间每 microbatch 传 `bsh`；tensor 每层每 microbatch all-reduce `8bsh·(t−1)/t` per device（§3.2 原文）。
- **Takeaway #1（§3.2）**："tensor model parallelism should generally be used up to degree g when using g-GPU servers, and then pipeline model parallelism can be used to scale up to larger models across servers"。经验上 "sub-optimal combinations ... can lead to up to 2× lower throughput"（§1）。
- **LaTeX↔M3 双源校验（Figure 5, p.5）**：tensor 切分的数学基础是 column-parallel A / row-parallel B 两个 GEMM，formulas.json 给出其矩阵形式：

$$[Y_1, Y_2] = [\textrm{GeLU}(XA_1), \textrm{GeLU}(XA_2)]. \tag{§2.3}$$

$$B=\begin{bmatrix} B_1 \\ B_2 \end{bmatrix}, \ Y = [Y_1, Y_2]. \tag{§2.3}$$

  机制：第一个 GEMM 的权重 A 按列切（`[A_1, A_2]`），GeLU 在切分后逐列独立计算（上式），第二个 GEMM 的权重 B 按行切（下式），`Y = [Y_1,Y_2]·[B_1; B_2]` 在 device 内即得完整结果，只需在 `g` 算子处一次 all-reduce。M3 对 Figure 5 的解读与之完全一致：MLP 中 X 经 f 切分→XA₁/XA₂→GeLU→Y₁/Y₂→与 B 的行块相乘→g 合并→Dropout→Z；Self-Attention 中 Q/K/V 同样按 head 切分。M3 还点破 f/g 共轭性——f 前向 identity / 反向 all-reduce，g 反之——这正是"切分不改变数学结果"的对偶根源，与上两式的列/行切分呼应。
- **§5.4.1 实证（Figure 13, p.10）**：161B GPT on 64 A100，`(p,t)=(8,8)` 达峰；纯 tensor `(2,32)` 因跨节点 all-to-all 主导而急剧下降，纯 pipeline `(32,2)` 因 bubble 膨胀而下降。Figure 14/15（p.10）M3 解读进一步印证：增大 tensor-parallel size 吞吐从 125 跌到 ~25 TF/s（all-to-all 主导），增大 pipeline-parallel size 吞吐从 ~170 跌到 ~40 TF/s（bubble 主导）。

### 2. Interleaved 1F1B Pipeline Schedule（核心算法贡献）
- **机制**：把每个 device 上原本连续的 L 层切成 v 个 "model chunk"，让同一 device 负责非连续多段层（§2.2.2 原例：device 1 持 layer 1,2,9,10 而非 1–4），使 warm-up 更短、flush 提前（§2.2.2, Figure 4 p.3）。要求 microbatch 数 m 是 p 的整数倍（§2.2.2 原文）。
- **效果**：每 chunk 的 forward/backward 时间降为 `t_f/v` 与 `t_b/v`，bubble time fraction 从 `(p−1)/m` 降到 `1/v·(p−1)/m`，即 **bubble 缩小 v 倍**（§2.2.2 原文 "reduces the bubble time by v"）。代价：点对点通信量同步增加 v 倍（§2.2.2 末）——故必须配合 scatter/gather 才可行。
- **LaTeX↔M3 双源校验（Figure 4, p.3）**：M3 对 Figure 4 解读指出 bottom（interleaved）图里每个 device 交替在两个 chunk 间跑 mini 1F1B 循环，"filling idle gaps without changing per-device memory footprint"，且 "pipeline flush happens sooner in the interleaved timeline"——这正是 bubble 缩 v 倍而显存不变的视觉证据，与 §2.2.2 的 `1/v·(p−1)/m` 公式一致。注：bubble 公式来自 .txt 全文（§2.2.1/§2.2.2 有完整推导），不在 formulas.json 6 条之内，故此处仅作文字引用、不补 $$。
- **实证（§5.3.2, Figure 12）**：175B GPT on 96 A100，interleaved 在小 batch 下显著高于 non-interleaved；随 batch 增大差距收窄。作者明确："Without the scatter/gather optimization, the default schedule performs better than the interleaved schedule at larger batch sizes"（§5.3.2 末）——interleaved + scatter/gather 强耦合。

### 3. Scatter/Gather 跨节点通信优化
- **机制**：相邻 pipeline stage 间 tensor-parallel ranks 发送的是**完全相同**的 tensor（每个 transformer layer 输出在 g 之后被复制到 t 个 tensor ranks，§4.1）。Figure 9（p.7）M3 解读：(a) 无优化时同一 tensor 经 8 条 IB 链路冗余发送 8 次；(b) 有优化时 sender 把 tensor 切成 t 块、每张 IB 卡只发 1/t，接收端用机内 NVLink all-gather 重建完整 tensor（rank 1→rank 3、rank 2→rank 4）。
- **效果**：相邻 stage 间通信量从 `bsh` 降到 `bsh/t`，t=8 时**降为 1/8**（§4.1 原文 "reduced to bsh/t, where t is the tensor-model-parallel size ... t=8 in our experiments"）。
- **实证（§5.7, Figure 18, p.11）**：175B GPT on 96 A100 + interleaved，scatter/gather 曲线（橙）始终高于 unoptimized（蓝），batch=60 时约 150 vs 130 TF/s/GPU；abstract + §4.1 称该优化使 interleaved 这类通信密集 schedule 可行，并最高带来 ~11% throughput 提升（§5.7 "up to 11% in throughput for communication-intensive schedules"）。没有此优化时 interleaved 在大 batch 下反输给默认 schedule（§5.3.2 末）。

### 4. 计算图重排 + 算子融合
- **机制（§4.2）**：(a) 数据布局从 `[b,s,a,h]` 改为 `[s,b,a,h]` 避免 memory-bound transpose 并启用 strided batched GEMM；(b) PyTorch JIT 生成 fused kernel（bias+GeLU、bias+dropout+add）；(c) 自定义 scale+mask+softmax fused kernel（通用 mask 与 causal mask 两版本）。
- **效果**：175B 模型 throughput **+19%**（113→135 TF/s per GPU）；530B 模型 **+11%**（133→148 TF/s per GPU）（§5.8 原文数字）。定位为"让 operator graph compute-bound 而非 memory-bound"——§6 列为对比 DeepSpeed 的第一条优势。

### 5. Weak-scaling 跑满 1T 参数 / 3072 GPU
- **机制**：按 §3 启发式随模型增大同步上调 `B`、`n`、`(t,p,d)`；用 interleaved + scatter/gather + 融合 + activation recomputation（§5.1）。
- **效果（Table 1 弱扩展）**：从 1.7B/32 GPU（44% peak, 4.4 PF）到 1T/3072 GPU（**52% peak, 502 PF**）呈超线性扩展（更大 GEMM 提升单卡利用率，§5.1 原文 "GPU utilization improves as the models get larger ... without significant increase in the communication time"）。
- **LaTeX↔M3 双源校验（Table 1, Figure 11）**：弱扩展由三式支撑（formulas.json 权威源）：

$$P = 12lh^2\left(1 + \dfrac{13}{12h}+\dfrac{V+s}{12lh}\right). \tag{Eq. 2}$$

$$F=96Bslh^2\left(1 + \dfrac{s}{6h} + \dfrac{V}{16lh}\right). \tag{Eq. 3}$$

$$\text{End-to-end training time} \approx \dfrac{8TP}{nX}. \tag{Eq. 4}$$

  机制：Eq. 2 给参数量 P（embedding V 与 sequence s 作为修正项，主项 `12lh²` 为 transformer 主体）；Eq. 3 给每 iteration FLOP 数 F（含 activation recomputation 的 extra forward pass，§5.1 原文 "equation (3) assumes activation recomputation"）；Eq. 4 由 Eq.2/3 + 经验不等式 `6h≫s, 16lh≫(V+s), 12lh≫V`（§5.1）化简得训练时间估计。三者直接喂 Table 1：代入 P=175B、T=300B tokens、n=1024、X=140 TF/s 得 34 天；P=1T、T=450B、n=3072、X=163 TF/s 得 84 天（§5.1 原文）。Figure 11（p.9）M3 解读从单维度验证：weak-scaling pipeline 下 batch=128 曲线在 p=1→8 几乎平直 ~170–175 TF/s/GPU，而 batch=8 曲线从 ~165 跌到 ~85 TF/s/GPU——bubble fraction `1/v·(p−1)/m` 在小 batch 下随 p 线性恶化的直接观测。
- **FLOP 计算是 lower bound**：Eq. 3 仅计入 GEMM（§5.1 原文 "lower bound for the true FLOP count"），Eq. 4 依赖经验近似，84 天是估计而非实测端到端完成（§5.1 "we estimate"）。

### 6. Microbatch size 与 activation recomputation 的双轴调参
- **机制（§3.4, §3.5）**：microbatch b 同时影响 arithmetic intensity（大 b → kernel 更 compute-bound）与 pipeline bubble（大 b → m=B/(b·d) 变小 → bubble 变大）。formulas.json 给出 batch 计算时间（用于推导最优 b）：

$$\left(b' / b + p - 1\right) \cdot \left(t_f(b) + t_b(b)\right). \tag{Eq. 1}$$

  机制：`b' = B/d`，第一项 `b'/b` 是稳态每 microbatch 数的计算份额，`(p−1)` 是 warm-up/cool-down 的 bubble 周期数；大 b 让 `t_f(b)+t_b(b)` 更 compute-bound 但抬高 `(p−1)` 相对占比。Figure 8（§3.4）用 Eq. 1 估出 b=4 为两类 batch 的最优点。activation recomputation 的最优 checkpoint 数 c = √(l·A_intermediate/A_input)（§3.5 原文）。
- **LaTeX↔M3 双源校验（Figure 7/16/17）**：Figure 7（p.6）M3 解读——b=1→16 单卡吞吐从 ~70 升到 ~90 TF/s（≈1.3×），b≥4 后渐近饱和，与 §3.4 "increases by up to 1.3×" 及 b=4 最优点吻合。Figure 16（p.10）M3 解读——91B/(t,p)=(8,8) 下 best b=2（曲线 microbatch=1–8 几乎平直，batch=512 ~155、batch=128 ~155→120 TF/s）。Figure 17（p.11）M3 解读——145B/128 A100，小 batch 下 activation recomp 降 **33%** 吞吐（extra forward），但大 batch 下因 bubble 缩小反获最高 **2×** 吞吐（sequences/sec ~3.75@b=8 无 recomp → ~8@b=256 有 recomp）。"以算换存"在小 batch 是税、在大 batch 是杠杆。

## 表格（原文结构化）

### Table 1 — 弱扩展端到端吞吐（GPT, V=51200, s=2048, mixed precision, Selene A100）
| Params (B) | heads | hidden h | layers l | t | p | GPUs n | Batch B | TF/s per GPU | %peak | Aggregate PF/s |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.7 | 24 | 2304 | 24 | 1 | 1 | 32 | 512 | 137 | 44% | 4.4 |
| 3.6 | 32 | 3072 | 30 | 2 | 1 | 64 | 512 | 138 | 44% | 8.8 |
| 7.5 | 32 | 4096 | 36 | 4 | 1 | 128 | 512 | 142 | 46% | 18.2 |
| 18.4 | 48 | 6144 | 40 | 8 | 1 | 256 | 1024 | 135 | 43% | 34.6 |
| 39.1 | 64 | 8192 | 48 | 8 | 2 | 512 | 1536 | 138 | 44% | 70.8 |
| 76.1 | 80 | 10240 | 60 | 8 | 4 | 1024 | 1792 | 140 | 45% | 143.8 |
| 145.6 | 96 | 12288 | 80 | 8 | 8 | 1536 | 2304 | 148 | 47% | 227.1 |
| 310.1 | 128 | 16384 | 96 | 8 | 16 | 1920 | 2160 | 155 | 50% | 297.4 |
| 529.6 | 128 | 20480 | 105 | 8 | 35 | 2520 | 2520 | 163 | 52% | 410.2 |
| 1008.0 | 160 | 25600 | 128 | 8 | 64 | 3072 | 3072 | 163 | 52% | 502.0 |

注：超线性来自 GEMM 随模型变大而 compute-bound 化（§5.1）；t 始终 ≤8（单机 GPU 数），印证 Takeaway #1；p 随模型增大爬到 64。参数量由 Eq. 2 算得，FLOP 由 Eq. 3 算得。

### Table 2 — PTD-P vs ZeRO-3（无 model parallelism）
| Scheme | Params (B) | M=size | B | GPUs | micro-b | TF/s/GPU | 300B-token 训练天数 |
|---|---|---|---|---|---|---|---|
| ZeRO-3 | 174.6 | 1 | 1536 | 384 | 4 | 144 | 90 |
| ZeRO-3 | 174.6 | 2 | 1536 | 768 | 2 | 88 | 74 |
| ZeRO-3 | 174.6 | 1 | 1536 | 1536 | 1 | 44 | 74 |
| ZeRO-3 | 529.6 | 1 | 2560* | 640 | 4 | 138 | 169 |
| ZeRO-3 | 529.6 | 2 | 2240 | 1120 | 2 | 98 | 137 |
| ZeRO-3 | 529.6 | 1 | 2240 | 2240 | 1 | 48 | 140 |
| PTD-P | 174.6 | 96 | 1536 | 384 | 1 | 153 | 84 |
| PTD-P | 174.6 | 96 | 1536 | 768 | 1 | 149 | 43 |
| PTD-P | 174.6 | 96 | 1536 | 1536 | 1 | 141 | 23 |
| PTD-P | 529.6 | 280 | 2240 | 560 | 1 | 171 | 156 |
| PTD-P | 529.6 | 280 | 2240 | 1120 | 1 | 167 | 80 |
| PTD-P | 529.6 | 280 | 2240 | 2240 | 1 | 159 | 42 |

*530B 在 560 GPU + microbatch 4 下 ZeRO-3 装不下，被迫扩到 640 GPU / B=2560。Table 2 数字与 Figure 10（p.8）M3 解读一致：PTD-P 两条曲线（橙）在 768→1920 GPU 区间几乎平直 ~140–160 TF/s，ZeRO-3 两条曲线（蓝）从 ~140 跌到 ~40–50 TF/s，gap 随 GPU 数扩大。

### 配置启发式（§3 Takeaways 原文结构化）
| Takeaway | 维度 | 规则 | 出处 |
|---|---|---|---|
| #1 | t vs p | t ≤ g（单机 GPU 数），跨机用 p | §3.2 |
| #2 | M=t·p vs d | M 仅需刚够装下参数+metadata，其余用 d 扩展 | §3.3.2 |
| #3 | microbatch b | 问题相关，Eq. 1 估 upper-bound | §3.4 |

## 与同类对比

### vs ZeRO-3（§5.2, Table 2, Figure 10 p.8）—— 机制级
- **ZeRO-3 机制**：将 optimizer state / weights / gradients 全部分片到 data-parallel workers，计算前 all-gather 取回完整参数，**每层每 microbatch 都要 all-gather 权重**，跨节点放大严重。Figure 10（p.8）M3 解读：ZeRO-3 曲线随 GPU 数（768→1920）急剧下坠至 40–50 TF/s，正是 cross-node all-gather 随 d 线性恶化的视觉证据。
- **PTD-P 机制**：tensor 切分让权重在各 rank 上**永久驻留**（不每 microbatch 重建），pipeline 仅做点对点 activation 传递；通信频率本质不同。
- **量化差距**：少 GPU + microbatch=4 时 PTD-P 比 ZeRO-3 在 175B/530B 分别高 **6% / 24%**；GPU 数翻倍（同 batch）后 PTD-P **超 ZeRO-3 70%**（§5.2 原文 "outperforms ZeRO-3 by 70% for both models due to less cross-node communication"）。
- **作者承认的边界**：ZeRO-3 可叠加 tensor parallelism 改善 scaling，本文对比未做此组合（§5.2 末 "ZeRO-3 can be combined with model parallelism to potentially ..."）。

### vs DeepSpeed (1T 参数)（§6 Related Work）
- DeepSpeed 也跑过 1T 参数模型，但 throughput 仅 **36% peak**（vs 本文 52%）。原文归因四点：operator fusion 使计算图 compute-bound、更高效 pipeline schedule、A100 vs V100、更多 GPU（§6）。等量模型训练时间对比：DeepSpeed 聚合 ~37.6 PF/s 需 ~40 个月，本文 502 PF/s 需 ~3 个月（§6）——约 13× 量级差距。

### vs GPipe schedule（§2.2.1, Figure 3）
- GPipe：全 forward 再全 backward，stash 所有 m 个 microbatch 的 activation（或仅 input activation，用 recompute）。§2.2.1 给出 bubble：`t_pb = (p−1)·(t_f+t_b)`，fraction = `(p−1)/m`。
- 本文用 PipeDream-Flush（1F1B，Figure 4 top p.3）：in-flight microbatch 数 ≤ p，**stash 仅 p 个 microbatch**（vs m 个）。bubble time 相同，但 memory 占用从 O(m) 降到 O(p)，对 m≫p 关键（§2.2.1 原文）。Figure 4 的 M3 解读直接对照两图：top 与 bottom 的 flush 竖线位置不同，bottom 提前。

### vs PipeDream-2BW / PipeMare / 异步 pipeline（§2.2, §6）
- 这些方法靠放松 weight update 语义（1-stale 或 fully async）完全消除 flush，throughput 更高，但**可能损失收敛速度或最终精度**。本文明确保留 strict optimizer 语义，defer 异步方案到 future work（§2.2 末）——这是本文吞吐上限被语义锁住的根因。

## 跨论文关系（→ MOC 谱系）

- 前作与根：[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] —— Megatron 第一代，提出 tensor parallelism（column-parallel A / row-parallel B、attention head 切分、每层 2 个 f/g all-reduce）的 bedrock。本文 Figure 5（p.5）直接借用其切分图（M3 解读确认 "figures borrowed from Megatron [40]"），并在其上叠加 pipeline 维度、把 t 限制在单机内。Eq.（§2.3 两个矩阵式）即第一代 tensor 切分的数学基础。
- 后继 apex：[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] —— MegaScale 把 PTD-P 推到 10k+ GPU，在 interleaved schedule 基础上进一步引入通信-计算 overlap 与 stability 优化，可视为本文 PTD-P 范式在万卡尺度的延续。本文 §6 未量化通信-计算 overlap（只作工程细节），正是 MegaScale 的切入点。
- MoE 分支：[[scalable-training-of-mixture-of-experts-models-with-megatron-core]] —— Megatron-Core 在本文 PTD-P 之上加入 expert parallelism（all-to-all 路由），将并行维度从 3D 扩展到 4D（+ expert）。本文 §6 明确不涵盖 Switch Transformer / Mesh-TensorFlow 的 sparse 路线。
- DP 互补轴：[[zero-memory-optimizations-toward-training-trillion-parameter-models]] —— ZeRO 路线。本文明确与 ZeRO-3 对比（Table 2, Figure 10 p.8）并指出 "cross-node 通信过重" 是 ZeRO-3 劣势根因；后续工作常把 ZeRO 与 PTD-P 融合（如 ZeRO-1/2 over PTD-P 的 DP 维度）。
- 网络拓扑轴：[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] —— 本文强调拓扑敏感（fat-tree, NVLink vs IB 分层，§5.9 给出 892 GB/s pipeline bisection / 12.9 TB/s data-parallel bisection），但只给启发式不自动搜索；该工作从拓扑侧补齐自动寻优。
- 优化器轴：[[muon-is-scalable-for-llm-training]] —— 本文假设同步 SGD 类 optimizer step（pipeline flush 同步权重），未触及 optimizer 本身的并行性；Muon 等新优化器在 optimizer axis 上重新分配计算-通信比，与 PTD-P 正交。

谱系定位：本文处于 **Megatron-LM 谱系中"tensor → tensor+pipeline 三维组合 + interleaved schedule"的承上启下节点**——向上承接第一代 tensor parallelism（Figure 5 直接复用其切分图，Eq. §2.3 两矩阵式即其数学基础），向下为 MegaScale（10k GPU）、Megatron-Core（MoE）以及与 ZeRO 的混合范式提供基础范式。

## 局限与边界

1. **不做自动搜索**（§1, §3, §6）：明确放弃 FlexFlow / PipeDream / DAPPLE 那类 cost-model 自动 placement，只给 3 条启发式。非对称模型（非均匀 transformer 层）也不处理，defer 给上述工作（§2.2）。
2. **保留 strict optimizer 语义**：所有"消除 bubble"的红利都来自缩 v 与缩 `(p−1)/m`，**未触碰异步/1-stale** 方向（PipeMare, PipeDream-2BW）——理论上限被语义锁住。作者承认这些方法 throughput 更高但可能伤收敛（§2.2, §6）。
3. **Interleaved schedule 的硬约束**：m 必须是 p 的整数倍（§2.2.2）；v 增大虽缩 bubble 但通信量同步 ×v，**没有 scatter/gather 就在大 batch 下反输给 non-interleaved**（§5.3.2 末，Figure 18 p.11 M3 解读显示 scatter/gather 曲线全程高于 unoptimized）——依赖 t=8 + 8 IB 卡的硬件前提，迁移到 IB 卡更少或 t 更小的平台会失效。
4. **硬件耦合强**：A100 16-bit peak 312 TF/s、NVLink/NVSwitch 机内、8×200Gbps HDR IB 机间、fat-tree 850 switches、all-NVMe 共享 FS（§5）。§5.9 给出 1T 模型实测 bisection bandwidth：pipeline 892 GB/s、data-parallel 12.9 TB/s——**换 slower interconnect 或更通信密集的 partitioning 会直接破坏 scaling**（§1, §5.9）。checkpoint 13.8 TB，load 峰值 1 TB/s（撞 FS 读上限），save 仅 273 GB/s（40% peak write）——I/O 是真实瓶颈（§5.10）。
5. **activation recomputation 的吞吐税**：小 batch 下 activation recomputation 让 throughput 降 **33%**（extra forward pass）（§5.6, Figure 17 p.11）；M3 解读显示无 recomp 曲线在 b=8 即 plateau ~3.75 seq/s，而有 recomp 持续爬到 b=256 的 ~8 seq/s。它是"以算换存"的硬性 trade-off，仅在大 batch 才因更小 bubble 反超（最高 2×）。
6. **数据并行上界**：data parallelism 单独用受 batch size 限制（§5.4.3）——GPT-3 batch=1536 意味着 DP 最多 1536 GPU，但实际训练用了 ~10000 GPU，必须靠 model parallelism 把 DP 之外的部分填掉。
7. **FLOP 计算是 lower bound**：Eq. 3 仅计入 GEMM（attention 24Bsh²+4Bs²h per layer ×4 for recomp + logit 6BshV），Eq. 4 依赖经验近似（`6h≫s, 16lh≫(V+s), 12lh≫V` 等不等式，§5.1），训练时间估计 **~3 个月** 是估算而非实测端到端完成（§5.1 "we estimate"）。
8. **不涵盖 expert / sparse 模型**：1.6T 参数 Switch Transformer 用 Mesh-TensorFlow 路线（§6），本文 GEMM 切分针对 dense transformer；MoE 的 all-to-all 路由通信未在 PTD-P 框架内建模——由 [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] 后续补齐。
9. **未与异步/prefetch 重叠通信做对比**：通信-计算 overlap 在本文是工程实现细节（NCCL async），未作为算法贡献量化——这是 MegaScale 等后继工作超越本文的切入点。
