# Parallel Scan on Ascend AI Accelerators — 技术点深读（DEEP 2026-08-18）
> 独立文件，extract_phase1 重跑不丢失。全要素深读 + 图表/公式/ablation 交织。
> 论文：Parallel Scan on Ascend AI Accelerators · arXiv:2505.15112v2 (2 Jan 2026)
> 平台：Huawei Ascend 910B4 · CANN 8.0.RC3.alpha002 · Ascend PyTorch adapter v2.1.0

## 核心问题

并行 scan（prefix sum）是基本并行原语，但通用 GPU 上的成熟 scan 策略（SSA / RSS / StreamScan / decoupled look-back，§2.1）都围绕 **SIMD + 全局内存 + 块级同步** 设计，并未利用今天主流加速器普遍内置的 **matrix multiplication engine（tensor core / cube unit）**。论文要回答三个层层递进的问题：

1. **能否用 Ascend DaVinci 架构里的 Cube 矩阵乘单元（AIC）来做 prefix scan，且比纯 vector（AIV）实现更快？** 单 Cube+单 Vector 内的 ScanU / ScanUL1 相对 vector-only CumSum 基线是否有收益（§1, §4.1）。这一问题之所以存在，是因为 910B 的 AI Core 是非对称的——**1 个 AI Cube (AIC) + 2 个 AI Vector (AIV)**（Figure 3.1, p.4，M3 解读：AIC 含 L1→L0A/L0B/BT/FP→L0C→FixPipe 的分层 scratchpad，两个 AIV 各带独立 Unified Buffer；Cube↔Vector 之间无本地通路，数据交换必须绕道 Global Memory / L2）。scan 之于 AIC 不是其天然工作负载，作者要把它"翻译"成矩阵乘。
2. **如何在 910B4 的非对称多核（20 AI Core = 20 AIC + 40 AIV，AIV:AIC = 2:1）上把 scan 扩展到极大一维数组？** 即同时打满 Cube 与 Vector、并逼近 HBM 带宽上限（§4.2 MCScan）。
3. **scan 作为 primitive 能否反哺 AI workload？** sorting / compress / top-k / top-p（nucleus）sampling / weighted sampling 这些 LLM 推理路径上的常客，能否由上述 scan kernel 组合得到加速（§5，Figure 5.1 p.7 的 DAG）。

scan 本质是 memory-bound（§2.1：SSA ≈4N、RSS ≈3N、StreamScan/decoupled look-back ≈2N 的全局内存读写），所以优化的真正指标不是峰值算力，而是 **打满 910B4 的 800 GB/s 理论 HBM 带宽（实测 memcpy 峰值约 560 GB/s，见 Figure 6.1, p.8）到多大百分比**（§6）。

## 关键创新点

1. **把 scan 表达成矩阵乘——单 Cube 内核 ScanU（Algorithm 4.1, §4.1）。**
   关键线性代数观察：若 `x` 的一个长度 `ℓ = s²` 的 tile 被 row-major reshape 成 `s×s` 矩阵 `A_s`，则 `A_s @ U_s`（`U_s` 为含主对角线的全 1 上三角方阵）一次性给出该 tile 内 **每行的局部 s-长前缀和**。Cube unit 做 `Mmad`，结果写回 Global Memory，再由单个 Vector core 在 UB 内对每行的最后一值做串行 `partial` 累加传播（Lines 9-14）。Cube↔Vector 之间靠 GM 传递 + AscendC 软件流水（pipeline）掩盖访存——这正呼应 Figure 3.1（p.4, M3）所示的"AIC 输出经 L0C/FixPipe 回 GM、AIV 从 GM 取到 UB"的非对称通路。矩阵乘次数 = `⌈n/s²⌉`，vector work = `O(n)`，span = `O(n/s)`（§4.1 Work/Span）。

2. **三矩阵乘的 ScanUL1（Algorithm 4.2, §4.1）——把单 tile 内 scan 完全用 cube 表达。**
   基于 [13, Alg.6] 的恒等式（Eq. 4.1）：`scan(z) = A_s @ U_s + L_s⁻ @ A_s @ 1_s`。三步矩阵乘序列 `C1 = A_s @ 1_s;  C2 = A_s @ U_s;  C2 = C2 + L_s⁻ @ C1`。两个收益点：(a) 前两步共享左操作数 `A_s`，`A_s` 只需载 L0A 一次；(b) 第三步利用 Cube 的 accumulation buffer（L0C）复用 `C2`。矩阵乘次数 = `3⌈n/s²⌉`，但 vector span 降到 `O(n/s²)`（vector length 为 `O(s²)`），相对 ScanU 有 `O(s)` depth 优势。实测 `s=128` 时 ScanUL1 ≈ 1.92× 快于 ScanU（§4.1 末，对照 Figure 4.2 的 log-log 曲线），与理论上界同量级。单核相对 vector-only CumSum 5×（ScanU）~ 9.6×（ScanUL1）（§1, §4.1）。

3. **MCScan 多核 scan 的"部分重算"策略（Algorithm 4.3, §4.2）——本文自称的新点。**
   形同 SSA（Scan-Scan-Add）两阶段，Phase I 与 Phase II 之间隔一道全局 `SyncAll`（Line 14）。但与以往所有 accelerator scan 不同的是：**Phase I 让 Cube 与 Vector 在同一 block 上同时做"同一份数据的不同任务"**——Cube 算每 `s`-tile 的局部前缀和写 GM，Vector 同时对该 block 做 `ReduceSum` 得到该 block 的 reduction `r[i]`（Line 11）。即 **block-level reduction 不是从 Cube 的 scan 输出里二次读出，而是 Vector 重新扫一遍原始输入算出来的（recomputation）**。这一设计直击 Figure 3.1（p.4, M3）揭示的硬件约束——Cube↔Vector 无本地 UB 通路，若让 Vector 从 Cube 输出二次读 reduction 会多一次 GM round-trip；重算反而省下这次访存。Phase II Vector 读 GM 中的 s-tile 局部 scan 与 `r` 数组，先在 UB 里对长度为 B 的 `r` 做小 scan，再用 `partial` 把跨块前缀 broadcast-add 到本块每个 s-tile（Lines 16-22）。矩阵乘数 `⌈n/s²⌉`，vector ops `O(n/s)`（reduce `O(n/s)` + add `O(n/s)`），span `O(n/(sB))`（§4.2 Work/Span）。

4. **MCScanUL1：把 Phase I 的单矩阵乘替换为 ScanUL1 的三矩阵乘序列（§6.1.1）。**
   仅替换 Phase I，Phase II 不变。实测相对 MCScan 提升 33%，down-sweep 阶段显著变短（Figure 6.4 break-down：up-sweep 略长但 down-sweep 大幅缩短，§6.1.1），**最终打到 memory-copy 带宽的 74.9%**（§1 abstract / §6.1.1）。这印证了 ScanUL1 的 `O(s)` depth 优势在多核 scale 下被放大。

5. **"L2 cache splitting" 优化（§6.1.1，Figure 6.3）。**
   把输入切成连续 chunk，使每 chunk 的输入与中间数组能塞进 L2，串行处理各 chunk 并把每 chunk 末值传到下一 chunk。给 MCScan 带来 25% 提升（§6.1.1）。

6. **int8 与 exclusive scan 扩展（§4.2 末 / Appendix B.2）。**
   AIC 支持 int8 输入、int32 累加。scan 是 memory-bound，用 int8 等价于"每字节多带一个元素"，提升 elements/s。exclusive scan 通过把 inclusive 结果整体后移一位、首位置 0（由第一个 block 执行）实现。

7. **Radix sort via MCScan（§5.3, §6.3, Figure 6.6）。**
   LSB radix sort 的 parallel split 直接复用 MCScan（mask = 当前 radix 位）。`SplitInd` operator 还并行维护输出索引以满足 `torch.sort()` API。支持 fp16（pre/post 处理用 AscendC bitwise 指令翻转 MSB 实现有符号→无符号映射，§5.3）。**N>525K 时 1.3×~3.3× 于 `torch_npu.sort()`**（§6.3）。作者特别点出一个反直觉发现：**多个小规模 dense 矩阵乘可以加速并行排序**（§1 末）——并抛出开放问题：能否进一步利用 cube 的 multiply-add 能力（radix sort 当前未利用）。

8. **Top-p (nucleus) sampling 是 scan-intensive（§5.5）——一个据作者所知的新观察。**
   用 radix sort 实现 top-p 时，fp16 一次 top-p batch 要跑 **17 次 scan**：16 次（每 radix 位一次）+ 1 次 sort 后的概率累加 scan（§5.5）。这让 scan kernel 的优化直接放大到 LLM 采样路径。Llama3 的 `sample_top_p` 实现就是 sort → cumsum 开头（§5.5 引 [39]）。Figure 5.1（p.7, M3 DAG）把这一依赖链可视化：Parallel Scan → Split → Compress/Radixsort → Top-K/Top-P，单个 MCScan primitive 自底向上组合出 LLM 推理的关键算子。

9. **Compress / masked_select（§5.2, §6.2, Figure 6.5）。**
   compress = split 只取 true 段。基于 exclusive MCScan on int8 mask。实测达 160 GB/s = **peak 带宽的 20%**；而 baseline `torch.masked_select` 在 Ascend 上**根本没用 vector/cube unit**（是纯 host 退化路径，§6.2），这恰好解释了 baseline 慢的根因。

10. **Batched scan 的 2:1 调度（Appendix B.1, Figure B.1）。**
    针对 910B 的 vector:cube = 2:1（Figure 3.1, p.4, M3 强调的关键设计点），每个 cube 一次处理两个 batch 的 `ℓ`-tile，两个 AIV 分别完成两个 batch 的 partial 传播（Figure B.1）。ScanU 在 `batch>18 且 len<4K` 时更优；ScanUL1 在 `batch<18 且 len>4K` 时更优（§B.1，Figure B.2 热力图），二者互补。

## 表格（原文结构化）

### 表1. 单核 vs 多核 scan 算法 work/span 汇总（综合 §4.1 / §4.2）

| 算法 | 矩阵乘次数（size s） | Vector work | Span | 关键性质 |
|---|---|---|---|---|
| ScanU (Alg. 4.1) | `⌈n/s²⌉` | `O(n)` | `O(n/s)` | 单 `A_s@U_s` 算 s 个并行 s-tile 局部 scan |
| ScanUL1 (Alg. 4.2) | `3⌈n/s²⌉` | `O(n)` | `O(n/s²)`（vector length `O(s²)`） | Eq.4.1 三矩阵乘 + L0C 累积 buffer 复用；`O(s)` depth 优于 ScanU |
| MCScan (Alg. 4.3) | `⌈n/s²⌉` | `O(n/s)` reduce + `O(n/s)` add | `O(n/(sB))` | Cube/Vector Phase I **并行重算** block-level reduction；B=block 数 |

### 表2. 主要性能数据（§6 全部实测，910B4，800 GB/s 理论 / ~560 GB/s 实测 memcpy 峰值）

| 指标 | 数值 | 出处 |
|---|---|---|
| ScanU vs vector-only CumSum 单核 speedup | 5× | §1, §4.1, Fig 4.2 |
| ScanUL1 vs vector-only CumSum 单核 speedup | 9.6× | §1, §4.1, Fig 4.2 |
| ScanUL1 vs ScanU（s=128 实测） | ≈1.92× | §4.1 末 |
| MCScan vs ScanU（20 AI cores） | 15.2× | §1, Fig 6.1（p.8） |
| MCScan 达 peak 带宽比例（s=128） | 37.5%（≈300 GB/s） | §6.1；Fig 6.1 M3：s=128 饱和约 300 GB/s |
| MCScan + L2 cache splitting 提升 | +25% | §6.1.1, Fig 6.3 |
| MCScanUL1 vs MCScan 提升 | +33% | §6.1.1, Fig 6.2 |
| MCScanUL1 达 memory-copy 带宽比例 | 74.9% | §1 abstract / §6.1.1 |
| Compress kernel 带宽 | 160 GB/s = 20% peak | §6.2, Fig 6.5 |
| Radix sort vs `torch_npu.sort()`（fp16，N>525K） | 1.3×–3.3× | §6.3, Fig 6.6 |
| Batched scan 峰值带宽（s=64/128） | 400 GB/s | §6.4, Fig 6.7 |
| Radix sort 低精度（8bit / 4bit）预估额外加速 | ≈1.5× / ≈3× | §B.5, Fig B.4 |

### 表3. Ascend 910B4 平台参数（§3.1, §6 + Figure 3.1 M3）

| 项 | 值 |
|---|---|
| 每 AI Core 构成 | 1 AI Cube (AIC) + 2 AI Vector (AIV)（Fig 3.1, p.4） |
| 910B4 AI Core 数 | 20（→ 20 Cube + 40 Vector，AIV:AIC = 2:1） |
| 理论 HBM 带宽 | 800 GB/s（实测 memcpy 峰值 ≈560 GB/s，Fig 6.1） |
| Cube 支持精度 | float16→float32, int8→int32 |
| AIC 内 scratchpad 层级 | L1, L0A, L0B, L0C, BT, FP buffer；FixPipe |
| AIV scratchpad | Unified Buffer (UB)，每 AIV 独立 |
| Core 间数据交换路径 | 仅 GM / L2（**无 AIC→AIV UB 本地通路**，Fig 3.1 M3 要点） |
| 同步原语 | AscendC 的 `SyncAll`（跨 block barrier） |
| 软件 | CANN 8.0.RC3.alpha002，AscendC，PyTorch adapter v2.1.0，op-plugin |

### 表4. Scan-based AI workload 一览（§5 依赖关系，Figure 5.1 p.7 DAG）

| Operator | 用到的 scan primitive | 备注 |
|---|---|---|
| Split | exclusive scan on int8 mask + `GatherMask` | `SplitInd` 同时返回输出索引 |
| Compress | split 的 only-true 段 | 等价 `torch.masked_select` |
| Radix sort | 每 radix 位一次 split (= 一次 MCScan) | LSB；fp16 需 pre/post bitwise 翻转 |
| Top-k | split 内的 partial quicksort/select | k≤4096 时未能超过 baseline（§5.4） |
| Top-p sampling | sort(radix) + cumsum = **17 scan/batch（fp16）** | scan-intensive 的新观察 |
| Weighted sampling | scan(w) + SplitInd + 阈值谓词 | 支持任意 support size（baseline 仅 224） |

### 表5. GPU scan 策略对比（§2.1）

| 策略 | 全局内存读写量 | 同步 | 备注 |
|---|---|---|---|
| Scan-Scan-Add (SSA) | ≈4N | 块级 | 多次读写 GM，scan-bound 时不利 |
| Reduce-Scan-Scan (RSS) | ≈3N | 块级 | 少于 SSA |
| StreamScan | ≈2N | 相邻块同步 | 单遍，串行块依赖 |
| Decoupled look-back (NVIDIA [38]) | ≈2N | 相邻块 + 冗余 work | SOTA on GPU |

## 与同类对比

- **vs GPU decoupled look-back (Merrill & Garland, [38])**：两者都以"打满 2N 数据移动 + 局部重算换流水"为核心思想，但 MCScan 的局部重算发生在 **Cube 和 Vector 两个不同计算单元之间**（Cube 算局部 scan，Vector 重算 block reduction），而不是 GPU 上的"邻居块状态传递"。Ascend 缺少 AIC→AIV 的本地通路（Figure 3.1, p.4, M3 明确），这是被迫也是被利用的特性。MCScan 不走 decoupled look-back 路线，而走 SSA 谱系但用 recomputation 把 Phase I 的 Cube/Vector 并行起来。
- **vs [13] (Dakkak et al., GPU tensor-core scan, ICS'19)**：ScanUL1 是 [13, Alg.6] 的 Ascend 改写（Eq. 4.1 即源自 [13]），但作者强调他们还做了多核扩展（MCScan）和"matrix-vector recomputation in up-sweep"，这是 [13] 没有的。
- **vs [53] (Zouzias & McColl, TCU 模型 logarithmic-depth scan)**：[53] 理论 depth 更好但"poor memory access patterns limit practical performance"（§1），本文选择走更简单、访存更友好的 [13] 谱系而非 [53]。
- **vs AscendC `CumSum` baseline**：作者把它视作 vector-only 的公平对照（CumSumInfo 设 128/128，s=128 与 cube 版对齐，§4.1 末）。baseline 不使用 Cube——这是 5×–9.6× 的解释，也是 masked_select / multinomial 等"baseline 在 Ascend 上根本没用 cube/vector"现象的同源问题（§6.2 代码审查佐证）。
- **跨硬件**：作者明确**不与 GPU/TPU 直接比绝对带宽**（§6 开头），因为那会变成比硬件规格；结果以 GB/s 或 GElems/s 给出便于读者自比。Figure 6.1（p.8, M3）中 memcpy 参考线（≈560 GB/s）即作为本硬件上的带宽上界。

## 跨论文关系（→ MOC 谱系, wikilinks [[slug]]）

- **[[gated-delta-networks-improving-mamba2-with-delta-rule]]**：GDN 的 chunkwise scan kernel 正是本文优化的 scan workload 类型——线性注意力/SSM 的 chunkwise parallel scan 都依赖前缀和（GDN 的 chunkwise scan / state propagation 是同一类 prefix-sum 内核）。本文提供 NPU 侧的 Cube-based 实现，GDN 提供 workload 与算法侧动机。
- **[[kimi-linear-an-expressive-efficient-attention-architecture]]**：KDA 的 chunkwise-parallel algorithm 与 Mamba2 的 associative scan 同属 SSM/线性注意力 scan kernel 家族。本文是把这一家族 kernel 落到 Ascend NPU 的工程参考，构成"算法（KDA/GDN）↔ NPU kernel（本文）"的桥接层。
- **[[ascend-950-npu-architecture-whitepaper]]**：910B4 是本文实测平台（§3.1, §6 + Figure 3.1 p.4），950 是其后续代际。本文描述的 DaVinci 非对称 Cube/Vector 划分、L0A/L0B/L0C/UB/FixPipe 层级、CANN/AscendC 编程模型，是 950 白皮书的直接前置——950 的 cube/vector 演进、更高带宽 HBM 都沿此架构路径。
- **[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]**：Ascend 910B/950 是 CloudMatrix 超算 pod 的核心 AI 加速器。本文的 scan / radix sort / top-p kernel 是该 serving 栈底层的算子优化——top-p sampling 直接处于 LLM serving 推理路径上（Figure 5.1 p.7 DAG 顶端），本文为其提供 Ascend-native 高带宽实现。
- **MOC 谱系定位**：本文是 **linear-attention / SSM genealogy 的 "NPU-kernel-implementation" 分支**——上游是算法侧（GDN chunkwise scan、KDA chunkwise-parallel、Mamba2 associative scan），下游是硬件/serving 栈（Ascend 910B/950、CloudMatrix）。它把"算法需要的 associative scan"翻译为"DaVinci Cube/Vector 非对称多核上的 MCScan/MCScanUL1"，是算法↔硬件之间的实现桥。

## 局限与边界

1. **span 仍线性于 n（单核）**：ScanU/ScanUL1 的 critical path 是 `O(n/s)` 或 `O(n/s²)`，§4.1 明确指出这些 kernel 仅适合"short input"——大数组必须走 MCScan。
2. **MCScan 有全局 barrier**：Phase I/II 之间的 `SyncAll`（Line 14）是 SSA 谱系固有的，对极小或极不均匀的输入不利；论文未给出与 decoupled look-back 在 Ascend 上的直接对比。
3. **cube↔vector 通信必走 GM/L2**（Figure 3.1 p.4, M3），这是 910B 的硬件约束——MCScan 的"重算"策略恰恰是为绕开这个瓶颈而设计的；若未来 Ascend 给出 AIC→AIV UB 的本地路径，本设计的相对优势会变化。
4. **Top-k 失败**：作者坦承 k≤4096 时未能超过 baseline top-k（§5.4），radix/split 路线对 top-k 不普遍适用。
5. **Batched scan 对小 s 退化**：s=16/32 时性能差，甚至与 baseline 持平（§6.4, Figure 6.7），说明 cube tile size 必须够大（s=64/128）才能填满 L0A/L0B。
6. **int8 收益有限**：当前实现 int8 相对 fp16 仅在较小长度上有小幅提升（§B.4, Figure B.3），作者归因于"current implementation"未充分利用 cube 的 128×256 / 256×128 int8 单指令能力——是一个未兑现的工程空间。
7. **radix sort 仅在 N>525K 才赢**（§6.3, Figure 6.6），小 N 时 baseline 更优；同时 radix sort **未利用 cube 的 multiply-add**（§1 末），作者将其列为开放问题。
8. **平台局限**：所有数值仅在 910B4 上测得，未在 910A/910B 其他子型号或 950 上验证；与 GPU/TPU 不做绝对带宽对比（§6 开头）。
9. **weighted sampling 收益不显著**：单采样场景相对 baseline 无明显加速，主要价值在功能（支持 >224 support size，§B.3）。
