# ZeRO — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：ZeRO: Memory Optimizations Toward Training Trillion Parameter Models · arXiv:1910.02054v3 (13 May 2020)
> 作者：Samyam Rajbhandari, Jeff Rasley, Olatunji Ruwase, Yuxiong He (Microsoft)；DeepSpeed 开源库
> 深读定位：DP-axis 内存优化根节点（与 Megatron 的 MP-axis 分片正交、可组合）

## 核心问题

大型 DL 模型精度收益显著，但训练数十亿到万亿参数面临**设备内存墙**（§1, §3）。论文首先做了一次"内存去哪儿了"的拆解（§3），把单设备训练内存分成两大块：

1. **Model states（模型状态）** — 占大头。以 mixed-precision Adam 训练 Ψ 参数模型为例（§3.1）：fp16 参数 2Ψ + fp16 梯度 2Ψ + 优化器状态 KΨ，其中 mixed-precision Adam 的 K=12（fp32 参数副本 4Ψ + fp32 momentum 4Ψ + fp32 variance 4Ψ），合计 **16Ψ bytes**。1.5B 的 GPT-2 仅权重 fp16 占 3GB，但训练需 24GB，32GB GPU 单卡都训不动——这解释了为何 PyTorch DDP 在 1.4B 参数即 OOM（§1, §3.1）。
2. **Residual states（残余状态）** — 激活、临时 buffer、内存碎片（§3.2）。1.5B GPT-2 在 seq=1K、batch=32 下激活约 60GB；activation checkpointing 降到 ~8GB；100B 模型即便用 checkpointing 仍需 ~60GB（batch=32）。碎片化在大模型训练可导致 30%+ 内存仍空闲时 OOM。

现有方案的痛点（§1, §2）：
- **DP**：compute/communication 效率高（粒度大、通信量低），但**完整复制 model states 到每个 DP 进程**，内存冗余严重，>1.4B 即 OOM。
- **MP（Megatron-LM/Mesh-TF）**：垂直切分计算与参数，内存高效，但通信粒度过细、跨节点带宽掉崖（NVSwitch 300GB/s → InfiniBand EDR 12.5GB/s）。实测 40B 模型跨两节点 Megatron 仅 ~5 TFlops/V100（<5% 峰值，§1）。
- **PP（G-Pipe/PipeDream）**：水平切层+micro-batch，bubble 需大批量掩盖（影响收敛、激活内存大）或保留 stale 副本（PipeDream，非标准训练语义，§2.1）。
- **CPU Offload**：GPU-CPU-GPU 传输可占训练时间 50%（§2.2.2）。
- **Memory-efficient optimizer（Adafactor 等）**：改优化器统计粒度，可能影响收敛保证；ZeRO 与之正交（§2.2.3）。

核心矛盾：DP 内存差但效率高，MP 内存好但效率差，且二者都**静态保留全量 model states**，尽管并非时刻都需要。ZeRO 要同时拿到 DP 的效率 + MP 的内存效率。

## 关键创新点

1. **ZeRO-DP：沿 DP 轴分片 model states，消除复制冗余**（§4.1, §5）。基于三条 insight：(a) DP 比 MP 扩展性好（粒度大、通信低）；(b) DP 内存冗余源于复制，MP 分片高效；(c) DP/MP 都静态保留全量 states，但每层参数只在前后向经过该层时需要。ZeRO-DP 把 optimizer states / gradients / parameters 沿 DP 进程分区，并用**动态通信调度**利用时序性，保持通信量接近 baseline DP。三阶段可累积开启：

2. **Pos — Optimizer State Partitioning（§5.1）**：把 optimizer states 分成 Nd 等份，第 i 个 DP 进程只存/更新第 i 份，每步末 all-gather 同步全量参数。内存：`4Ψ + KΨ → 4Ψ + KΨ/Nd`。Nd 大时 ≈ 4Ψ，即 **4x 缩减**。7.5B 模型 Nd=64 从 120GB 降到 31.4GB。通信量与 baseline DP 相同（all-gather Ψ + reduce 等，见 §7.2.1 实际为 2Ψ）。

3. **Pg — Gradient Partitioning（§5.2）**：每个进程只需对应参数分区的 reduced gradient，反向传播中梯度就绪即做 **reduce-scatter**（而非 all-reduce）到负责该分区的进程，归约后立即释放。用 bucketization 策略（类 NVIDIA AMP 的 all-reduce bucketing，但用 reduce 而非 all-reduce）overlap 通信与计算。内存：`2Ψ → 2Ψ/Nd`。Pos+g 合计 `2Ψ + 14Ψ/Nd ≈ 2Ψ`，即 **8x 缩减**。7.5B Nd=64 降到 16.6GB。通信量仍 = baseline 2Ψ（§7.2.1：scatter-reduce Ψ + all-gather Ψ = 2Ψ）。

4. **Pp — Parameter Partitioning（§5.3, §7.2.2）**：每个进程只存自己分区的参数；前向/反向需要其他分区参数时通过 broadcast 接收，用完即弃，**沿前向/反向流水线化**避免内存堆积。前向 all-gather 一次（Ψ），反向再 all-gather 一次（Ψ），加梯度 reduce-scatter（Ψ），总通信量 **3Ψ = 1.5x baseline**，换来内存 **16Ψ → 16Ψ/Nd** 的线性缩减。7.5B Nd=64 降到 1.9GB。意义：ZeRO 让 DP 能拟合任意大小模型，只要设备数够。Nd=1024 时可拟合 1T 参数（16TB/1024=16GB/卡，§1）。

5. **ZeRO-R — 残余内存优化（§4.2, §6）**：
   - **Pa — Partitioned Activation Checkpointing（§6.1）**：MP 垂直切线性层时各 GPU 需复制完整激活（insight a）。ZeRO 把 activation checkpoint 分区存储，用到时 all-gather 重构单层。与 activation checkpointing 协同，激活内存按 MP 度缩减。100B 模型 batch=32、MP=16：从 33GB/GPU 降到 ~2GB/GPU；再 **Pa+cpu** 把分区 checkpoint offload 到 CPU，激活内存趋近于零（额外 ~2x CPU 数据搬运）。
   - **CB — Constant Size Buffers（§6.2）**：高性能库（Apex/Megatron）把参数 fuse 成单个大 buffer 提升集合通信带宽，但 buffer 随模型线性增长（3B 模型 fp32 fused buffer 需 12GB）。ZeRO 在模型过大时改用**定长 fused buffer**，解耦模型大小，仍够大以保持效率。
   - **MD — Memory Defragmentation（§6.3）**：forward 中 checkpoint 长存/重算激活短存，backward 中参数梯度长存/激活梯度短存——交错造成碎片。ZeRO 预分配连续内存块，将 activation checkpoint 和梯度即时拷入，既防 OOM 又减 allocator 搜索开销。

6. **ZeRO ⊗ MP 可组合，最大理论缩减 Nd × Nm（§1）**：ZeRO-DP 沿 DP 轴分片，Megatron-MP 沿 MP 轴分片，二者正交。1T 参数可在 1024 GPU 上用 16-way MP（单 DGX-2 节点内）+ 64-way DP（跨节点）拟合，且只用 modest batch size。这是后续 Megatron-DeepSpeed 组合范式的理论根基。

7. **通信量分析（§7, §8）**：定量证明 ZeRO 不是用通信换内存。Pos+g 通信量 = 2Ψ（与 baseline 同）；Pos+g+p = 3Ψ（1.5x）。Pa 增加的 all-gather 通信 < baseline MP 通信量的 10%（每 transformer block 一个 all-gather seq×hidden，对比 MP 的 12×seq×hidden）。更妙：Pa 让 batch 可放大 MP 度倍（最高 16x），DP 通信量反比于 batch，故 Pa 能让 DP 通信量降一个数量级——把 MP 通信 +10% 换 DP 通信 -10x，在 DP 通信是瓶颈时净收益巨大。Pa+cpu 仅在极小 batch、DP 通信瓶颈时启用。

8. **ZeRO-100B 实现 = Pos+g + ZeRO-R（§10）**：实现的是子集（未含 Pp），400 V100（25 DGX-2 节点，800Gbps 互联）上：(a) 模型规模——配合 MP 训练 170B（>8x SOTA，Megatron 跨节点难超 40B）；(b) 速度——100B 上 15 PetaFlops 聚合（>30% 峰值），最高 10x 加速；(c) 超线性扩展——60B 模型 64→400 GPU，GPU 数翻倍性能 >翻倍（Pos+g 随 Nd 降内存→更大 batch→更高算术强度）；(d) 民主化——无 MP/PP 即可训 13B（>T5 11B），128 GPU 上 >40 TFlops/GPU，且无需 NVLink/NVSwitch 高端互联；(e) 驱动 Turing-NLG 17B，Webtext-103 perplexity 10.21 SOTA，41.4 TFlops/GPU。

9. **可插拔接口（§10.1）**：兼容任意 `torch.nn.module`，用户只需 wrap 模型即可像经典 DP 一样用，**无需改模型代码**——对比 MP/PP 需模型重构、分布式算子改造、Megatron 仅支持有限算子。这是 ZeRO 易用性的关键。

## 表格（原文结构化）

**Table 1 — ZeRO-DP 各阶段单设备 model-state 内存（GB），随 DP 度 Nd 变化（§5）**。粗体=可装入 32GB V100 集群。

| Nd | 7.5B: DP | Pos | Pos+g | Pos+g+p | 128B: Pos | Pos+g | Pos+g+p | 1T: Pos | Pos+g | Pos+g+p |
|----|---------|-----|-------|---------|-----------|-------|---------|---------|-------|---------|
| 1  | 120     | 120 | 120   | 120     | 2048      | 2048  | 2048    | 16000   | 16000 | 16000   |
| 4  | —       | 52.5| 41.3  | **30**  | 896       | 704   | **512**| 7000    | 5500  | **4000**|
| 16 | —       | 35.6| 21.6 | **7.5** | 608       | 368   | **128**| 4750    | 2875  | **1000**|
| 64 | —       | 31.4| 16.6 | **1.88**| 536       | 284   | **32** | 4187    | 2218  | **250** |
| 256| —       | 30.4| 15.4 | **0.47**| 518       | 263   | **8**  | 4046    | 2054  | **62.5**|
| 1024|—       | 30.1| 15.1 | **0.12**| 513       | 257   | **2**  | 4011    | 2013  | **15.6**|

解读（§5.4）：Nd=64 时 Pos/Pos+g/Pos+g+p 可训 7.5B/14B/128B；Nd=1024 时 Pos+g+p 可训 **1T**。无 ZeRO 时 DP 单卡 <1.5B。

**Table 2 — 最大可训模型规模（理论 vs 实测，§6.3 后）**：

| MP | GPUs | 理论 Max: Baseline | Pos | Pos+g | Pos+g+p | 实测(ZeRO-OS/Pos) |
|----|------|-------------------|-----|-------|---------|-------------------|
| 1  | 64   | 2B                | 7.6B| 14.4B | 128B    | 1.3B → 6.2B       |
| 2  | 128  | 4B                | 15.2B|28.8B| 256B    | 2.5B → 12.5B      |
| 4  | 256  | 8B                | 30.4B|57.6B| 0.5T    | 5B → 25B          |
| 8  | 512  | 16B               | 60.8B|115.2B| 1T     | 10B → 50B         |
| 16 | 1024 | 32B               | 121.6B|230.4B| 2T    | 20B → 100B        |

实测 Pos 规模与理论上限吻合，验证内存分析的真实性。

**Table 3 — ZeRO 配置 C1-C5（§10.5）**：

| Config | ZeRO-DP | ZeRO-R |
|--------|---------|--------|
| C1 | Pos | CB+MD |
| C2 | Pos | CB+MD+Pa |
| C3 | Pos+g | CB+MD |
| C4 | Pos+g | CB+MD+Pa |
| C5 | Pos+g | CB+MD+Pa+cpu |

C1→C2：加 Pa，激活内存 ×1/MP 度，模型 40B→60B；C2→C4：Pos→Pos+g，model states 减半，60B→140B；C4→C5：Pa+cpu，激活再降，140B→150B（170B 必须 C5 才能跑，§10.5）。

**Table 4 — 实验模型配置（§10.1）**：

| 模型规模 | Layers | Hidden Dim |
|----------|--------|-----------|
| 1.5B | 48 | 1600 |
| 8B | 72 | 3072 |
| 40B-60B | 88, 132 | 4096 |
| 80B-170B | 100, 125, 150 | 8192 |

**关键公式** — mixed-precision Adam 单设备 model-state 内存（§3.1）：

$$2\Psi + 2\Psi + K\Psi = 16\Psi \text{ bytes}, \quad K=12$$

ZeRO-DP 三阶段后：`Pos→4Ψ+KΨ/Nd`, `Pos+g→2Ψ+14Ψ/Nd`, `Pos+g+p→16Ψ/Nd`。

## 与同类对比

| 维度 | ZeRO-DP | Megatron MP | G-Pipe PP | CPU Offload | Adafactor |
|------|---------|-------------|-----------|-------------|-----------|
| 分片轴 | DP 轴 | MP 轴（垂直切层内）| 层间（水平）| CPU-GPU | 优化器统计粒度 |
| 内存效率 | 16Ψ/Nd（线性）| 高但受层均分约束 | 中（激活大）| 高 | 中（K↓）|
| 通信量 vs baseline | 1x（Pos+g）/ 1.5x（+p）| 高，跨节点掉崖 | bubble 开销 | 50% 训练时间在搬运 | 无 |
| 计算粒度 | 大（DP 级）| 细 | 中 | 大 | 大 |
| 收敛影响 | 无（语义等价）| 无 | 大 batch 影响收敛 | 无 | 可能影响 |
| 易用性 | wrap 即用，无需改模型 | 需模型重构+分布式算子 | 难（tied weight/bn）| 中 | 改优化器 |
| 跨节点扩展 | 强（超线性）| 弱（<5% 峰值 @40B 跨节点）| 中 | 弱 | 强 |

ZeRO 的根本性差异：**沿 DP 轴分片而非 MP 轴**，因此保留了 DP 的大计算粒度与低通信量，同时消除复制冗余——把"DP 效率高但内存差"与"MP 内存好但效率差"的二元对立打破。

## 跨论文关系（→ MOC 谱系）

- **[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]** — MP-axis 分片根节点（垂直切线性层，all-reduce 2 次/forward+backward）。ZeRO 是其正交对偶：DP-axis 分片。二者可组合（ZeRO ⊗ Megatron = Nd×Nm 理论缩减），论文用 Megatron-LM(Sept 2019) 作 baseline 与组合对象（§1, §10.1）。**组合范式 → Megatron-DeepSpeed**。
- **[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]** — MegaScale 的 DP 通信 overlap 基于 ZeRO-2 的核心拆解：把 all-reduce 拆成 reduce-scatter + all-gather。ZeRO-2 正是利用 reduce-scatter（梯度只归约到对应分区进程）实现"通信量不变、内存 8x 缩减"（§5.2, §7.2.1）。MegaScale 把这一拆分用于通信-计算 overlap 的极致调度。
- **[[muon-is-scalable-for-llm-training]]** — 优化器内存视角对比。ZeRO-1 对 Adam 的 K=12 做沿 DP 轴分片（4x 缩减）。Muon 只需 1 个 momentum buffer，额外内存是 ZeRO-1 AdamW 的一半——从优化器结构本身降低 K，与 ZeRO-1 的"分片 K"是正交的另一条降内存路径，可叠加。
- **[[scalable-training-of-mixture-of-experts-models-with-megatron-core]]** — MoE 训练规模化的内存组合，ZeRO 与 EP/MP 协同的下游范式。
- **[[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]** — ZeRO 作为 DP-axis 内存优化的代表入选综述。
- 谱系定位：**ZeRO = DP-axis memory-optimization root**。MP-axis root = Megatron-LM；Pipeline-axis = G-Pipe/PipeDream；CPU-offload axis = vDNN；optimizer-stat axis = Adafactor/Muon。ZeRO 的独特贡献是证明"DP 轴分片可同时保效率与省内存"，成为后续 FSDP（PyTorch 原生 ZeRO-3）的理论原型。

## 局限与边界

1. **算力缺口未解（§9）**：ZeRO 能"拟合"1T 模型，但训练时间仍不可行。1T 模型单样本计算量是 Bert-Large 的 3000x；Bert-Large 在 1024 V100 DGX-2H 上需 67 分钟，1T 同硬件同效率需 ~140 天，实际 seq/data 也增大则 >1 年。需 exa-flop 级系统。ZeRO 解决的是"装得下"，不是"训得完"。
2. **ZeRO-100B 未实现 Pp（§10）**：论文实测仅 Pos+g+ZeRO-R（C1-C5），Pp（参数分片）当时未发布，计划 2020 年 5 月后扩展。1T 的 Pp 结论是理论分析（Table 1/2），非实测。1.5x 通信开销仅在 Pp 启用时产生。
3. **Pa+cpu 性能权衡（§10.5）**：C4→C5 在 60B 上性能反降——CPU 激活搬运开销超过 batch 放大收益。仅在模型极大（如 170B）或 batch 极小、DP 通信瓶颈时才净收益。论文承认"绝大多数情况下 Pa+cpu 更差"。
4. **超大 batch 收敛边界（§1 脚注1, §10.3 脚注5）**：ZeRO 靠省内存放大 batch 提速，但 batch 过大会损害收敛（critical-batch-size）。论文声明在 1K GPU 量级 batch 仍在安全区，但不保证更大规模。
5. **MP 仍未完全替代（§1）**：ZeRO 削弱了 MP "仅为拟合模型"的必要性，但两类场景仍需 MP：(a) 超大模型激活内存仍超限时配合 ZeRO-R；(b) DP 单独聚合 batch 过大影响收敛时用 MP 控制 batch。ZeRO 与 MP 是协同而非取代。
6. **通信量分析假设带宽受限区（§7.1）**：通信量比较基于"大模型 all-reduce 完全带宽受限"假设，只算总数据量 2Ψ/3Ψ；小模型或 latency 受限区结论可能不同。reduce-scatter/all-gather 的 pipelined 实现假设 Ψ 元素的数据移动量，依赖具体集合通信原语实现。
7. **MP 度受硬件拓扑约束**：组合方案推荐 16-way MP 限在单 DGX-2 节点内（NVSwitch 高带宽），跨节点仍走 DP——仍依赖高端互联，对低端集群（无 NVLink）仅"无 MP 训 13B"场景适用。
8. **未评估收敛精度等价性实测**：论文声称"不改变优化方法、不影响收敛"，但未给出 ZeRO vs baseline 的最终精度对照实验（Turing-NLG 仅报 perplexity，无 ZeRO-off 对照）。语义上等价但工程实现（如 bucket 化 reduce 顺序、fp32/fp16 转换点）可能引入数值差异——这一点未严格论证。
