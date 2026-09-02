# Ring Attention长序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/ring-attention-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/ring-attention-context-parallel.md

# Ring Attention长序列并行 — 深度解读

---

## 【定位】

本文档描述 **Ring Attention 长序列并行**能力：在昇腾大模型加速库 mindspeed 中，通过在**进程间构建 KV 块的环状通信结构**，沿序列维度切分 attention 与前馈计算，从而将长序列训练中以 O(S²) 增长的内存开销分摊到多个设备上，理论上支持"近无限"上下文长度。

---

## 【技术要点】

1. **问题驱动**：序列维度 S 增长时，attention 训练内存开销以 **O(S²)** 速度膨胀；现有数据/张量/流水线并行均**无法在序列维度切分**，需要专门的序列并行方案。
2. **核心机制 — 分块 Softmax + 环形 KV 传递**：借鉴 blockwise softmax 原理，使每个进程持有本地 QKV 块即可分块计算 attention，无需拼装整段 attention 矩阵。计算完本地 attention 后，**向后发送 / 向前获取** KV 块，沿设备环遍历，逐块完成 attention 与 FFN 计算。
3. **通信与计算互相掩盖**：本地的 attention 计算与 KV 块通信理想情况下可互相掩盖，**全程不需要数据拼接**，消除额外引入的通信开销。
4. **掩盖条件**：计算块序列长度 c 需满足 **c ≥ F/B**（F = 每 device FLOPS，B = 每 device 通信带宽），实践中需确保每个计算块分到的序列长度足够大才能较好掩盖。
5. **与 FlashAttention 兼容**：可兼容 FlashAttention 且 FlashAttention 默认开启，开启 Context Parallel 时必须同时开启 Flash Attention，否则特性不支持。
6. **Double Ring Attention 扩展**：通过 `--cp-window-size [int] > 1` 启用双层 Ring Attention（要求 cp_size 能被该参数整除），内层窗口越大通信/计算并发程度越高，但受片上内存带宽抢占影响，可能整体效率下降。
7. **相对其他方案的优势**：**不要求 head size 被 CP size 整除**（区别于 Ulysses 方案），具有更高灵活性；并提供 hybrid_cp_algo、ulysses_cp_algo、megatron_cp_algo（默认）三档长序列并行算法选项。
8. **典型触发场景**：使用 GPT 类模型训练、经 MoE 层后实际序列长度超过 8k 时启用。

---

## 【关键机制与数据】

### 工作原理 / 数据流

- **环状通信结构**：N 个进程排成环形，每个进程持有切分后的本地 QKV 块。
- **逐块计算流程**：每个进程先完成本地 attention → 向后一个进程发送 KV → 从前一个进程接收 KV → 用新 KV 继续计算本块 Q 的 attention → 重复 N-1 轮，覆盖所有 KV 块。
- **数据流特点**：attention 计算过程中**全程不需要数据拼接**，支持的序列长度理论上可以无限拓展。
- **算法层次**：默认使用 `megatron_cp_algo`（即本文所述 Ring Attention），也可切换至 `ulysses_cp_algo` 或 `hybrid_cp_algo`。
- **掩盖条件公式**：**c ≥ F/B**（c = 每个计算块的序列长度，F = 每 device FLOPS，B = 每 device 通信带宽），具体推导见 arxiv 原文。

### 性能数据（原文实测）

- **原文（实测案例）**：Llama2 裁剪模型，序列长度 32k，cp 为 16 且无其他并行切分时，实测 **内层窗口大小为 2 时性能最优**。
- **原文（经验阈值）**：序列长度 8k 时 cp 功能分割后的 send/recv 时间**长于**计算时间，造成性能下降；建议配置 **seq-length / context-parallel-size > 8k** 以获取最佳效果。
- **原文（整体效果）**：相比不开启序列并行，**单步耗时增加**，但**相比重计算，计算效率得到提升**。

### 引用文献

- Ring Attention with Blockwise Transformers for Near-Infinite Context（arxiv 2310.01889）：分块 Softmax 与 ring 通信结构的原始出处。

---

## 【表格解读】

原文给出**重要参数表**，逐字还原如下：

| 重要参数 | 参数说明 | 是否必选 | 默认值 |
|---|---|---|---|
| `--context-parallel-size [int]` | 开启CP对应的数量，根据用户需求配置。 | 否 | 1 |
| `--seq-length [int]` | 输入序列的长度。 | 是 | / |
| `--use-cp-send-recv-overlap` | 建议开启，开启后支持send receive overlap功能。 | 否 | True |
| `--attention-mask-type` | 设置Mask计算的类型，默认是causal（倒三角）Mask计算，设置general代表全量计算。 | 否 | causal |
| `--context-parallel-algo` | 长序列并行算法选项：<ul><li>ulysses_cp_algo：开启Ulysses长序列并行</li><li>hybrid_cp_algo：开启Hybrid长序列并行</li><li><b>megatron_cp_algo</b>：开启Ring Attention长序列并行</li></ul> | 否 | megatron_cp_algo |
| `--megatron-cp-in-bnsd` | 开启后，FA使用BNSD计算。 | 否 | True |
| `--cp-window-size [int]` | 控制双层Ring Attention的内层窗口大小。值为1时使用原始Ring Attention算法，值大于1时使用Double Ring Attention算法，优化原始性能。要求cp_size必须能被该参数整除。 | 否 | 1 |

**逐行解读：**

- **`--context-parallel-size`**：CP 并行度（参与序列并行的进程数）。非必选，默认 1 表示不开启；按需配置即可。
- **`--seq-length`**：唯一必选参数，定义输入序列长度；无默认值，是计算 seq-length / context-parallel-size 比值（决定是否能有效掩盖通信）的前置输入。
- **`--use-cp-send-recv-overlap`**：是否启用 send/recv 与计算的 overlap。文档明确"建议开启"，默认 True，与本文强调的"通信与计算互相掩盖"机制直接对应。
- **`--attention-mask-type`**：决定 attention 掩码形状。GPT 类训练建议设为 `causal`（倒三角）；`general` 表示全量双向 attention。该参数与 FlashAttention 的 mask 模式耦合。
- **`--context-parallel-algo`**：三选一长序列并行算法——`ulysses_cp_algo`（Ulysses 方案，要求 head size 被 CP size 整除）、`hybrid_cp_algo`（混合方案）、`megatron_cp_algo`（**默认即本文 Ring Attention**）。
- **`--megatron-cp-in-bnsd`**：控制 FA 计算时的张量布局是否为 BNSD。默认 True，便于与 FlashAttention 的张量排布对齐。
- **`--cp-window-size`**：Double Ring Attention 内层窗口大小。=1 即退化为原始 Ring Attention；>1 启用 Double Ring Attention 并对原始性能做优化，但要求 **cp_size 能被该参数整除**；文档给出实测结论——32k 序列、cp=16、Llama2 裁剪模型下窗口=2 最优，并非越大越好。

---

## 【公式解读】

### 1. 内存增长复杂度

$$O(S^2)$$

- **S**：序列维度（sequence length）。
- **作用**：说明 vanilla attention 训练内存随序列长度二次增长，是 Ring Attention 要解决的核心瓶颈。

### 2. 通信掩盖的最低条件

$$c \geq F/B$$

- **c**：每个计算块分到的序列长度（单进程本轮 attention 计算覆盖的 token 数）。
- **F**：每 device 的 FLOPS（计算吞吐）。
- **B**：每 device 间的带宽（通信吞吐）。
- **作用**：通信与计算能否互相掩盖的临界条件——只有当单块计算量所需的 FLOPs 时间 ≥ KV 块传输时间，才能让通信被计算完全覆盖。该条件等价于原文 NOTE 中给出的判据的简化形式。

### 3. 推荐配置的经验判据

$$S/(T \cdot \alpha) \geq 1/(W \cdot \beta)$$

- **S**：seq-length / context-parallel-size（**每个 CP rank 分到的序列长度**，对应公式 2 中的 c）。
- **T**：芯片理论算力。
- **α**：计算效率（实际 FLOPS 利用率）。
- **W**：理论通信带宽。
- **β**：带宽利用率。
- **作用**：与公式 2 同一物理意义的另一表达形式，用于判断在给定 seq-length / cp 比值、芯片算力与带宽下，通信能否被计算掩盖；文档明确建议 **seq-length / context-parallel-size > 8k** 作为经验阈值。

---

## 【关联】

- **上游算法/论文**：Ring Attention with Blockwise Transformers for Near-Infinite Context（<https://arxiv.org/pdf/2310.01889>）——blockwise softmax 与 ring 通信结构的原始出处，本特性即基于此文实现。
- **兄弟特性 — Ulysses 长序列并行**：`--context-parallel-algo ulysses_cp_algo`，需要 head size 被 CP size 整除，灵活性不如本文方案；可由 `hybrid_cp_algo` 与 Ring Attention 混合使用。
- **依赖特性 — FlashAttention**：开启 Context Parallel 时**必须同时开启 Flash Attention**，否则特性不支持；可通过 `--megatron-cp-in-bnsd` 切换 FA 的张量布局为 BNSD。
- **关联场景 — MoE 长序列**：在 GPT 类模型中输入数据经过 MoE 层、实际序列长度超过 8k 时，Ring Attention 为典型解决方案。
- **扩展机制 — Double Ring Attention**：`--cp-window-size > 1` 时启用双层 Ring Attention，是对本文方案的进一步性能优化（受片上内存带宽影响，需实测调参）。
- **互补特性 — 重计算（recomputation）**：原文将 Ring Attention 与重计算做效率对比，意在说明对超长序列场景，Ring Attention 的计算效率优于重计算。

---

## 【使用方法】

**核心启用命令**（基于文档参数表与使用场景说明）：

```bash
# 最小启用示例：开启 Ring Attention（megatron_cp_algo 为默认）
--context-parallel-algo megatron_cp_algo \
--context-parallel-size <N> \
--seq-length <S> \
--use-cp-send-recv-overlap \
--attention-mask-type causal \
--megatron-cp-send-recv-overlap  # 若存在该开关

# Double Ring Attention 启用（要求 cp_size 能被 cp-window-size 整除）
--cp-window-size 2

# 配合 Flash Attention（必选，否则特性不支持）
# 通过仓库其他特性开关启用 FlashAttention
```

**关键注意事项**（原文 NOTE）：

1. 开启 Context Parallel 时需**同时开启 Flash Attention**，否则特性不支持。
2. GPT 类模型训练场景下，建议 `--attention-mask-type` 设为 `causal`。
3. 经验配置：**seq-length / context-parallel-size > 8k** 才能有效掩盖通信，否则 8k 附近 send/recv 时间会超过计算时间造成性能下降。
4. Double Ring Attention 的 `--cp-window-size` 需结合实际场景调试，并非越大越好；文档实测 32k 序列 + cp=16 + Llama2 裁剪模型下，窗口=2 性能最优。
