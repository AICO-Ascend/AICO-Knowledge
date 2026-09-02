# Ring Attention for Long-Sequence Parallelism

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/ring-attention-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/ring-attention-context-parallel.md

# Ring Attention for Long-Sequence Parallelism — 深度解读

## 【定位】
本文档面向昇思 LLM 分布式训练框架 `mindspeed-llm`，介绍 **Ring Attention（环形注意力）** 这一长序列并行能力，用于解决序列维度 `S` 增长导致的 `O(S²)` 训练显存开销问题，突破现有数据/张量/流水线并行无法沿序列切分的限制。

---

## 【技术要点】

1. **核心思想 — Blockwise Softmax**：基于分块 softmax（blockwise softmax）原理，无需构造整段序列的完整注意力矩阵即可分块完成注意力计算。
2. **序列维切分**：将 self-attention 与 FFN 计算以 block 粒度执行，序列维度 `S` 分布在多个设备上；每进程持有本地分片的 QKV block。
3. **环形通信结构**：在进程/设备环上构建 ring 通信结构，本地完成 attention 后，KV block **沿环向后发送（send backward）、向前取回（fetch forward）**，逐 block 推进 attention 与 FFN。
4. **计算与通信重叠**：本地 attention 计算与 KV block 通信可重叠，消除额外通信开销；理论上需满足 `c >= F/B`（`c` 为每个 compute block 分配的序列长度，`F` 为每设备 FLOPS，`B` 为设备间带宽）。
5. **无数据拼接**：attention 计算过程中不进行任何数据拼接，理论上支持的序列长度可无限增长。
6. **与 FlashAttention 兼容**：默认启用 FlashAttention；与 Ulysses 方案相比 **不要求 `head_size` 能被 `cp_size` 整除**。
7. **触发场景**：GPT-like 模型一旦进入 MoE 层，实际序列长度即超过 8K；建议配置 `seq-length / context-parallel-size > 8K` 以获得最佳性能。

---

## 【关键机制与数据】

- **内存开销量级**（原文）：序列维度 `S` 增长时，训练显存开销按 $O(S^2)$ 增长，因此必须针对性优化。
- **重叠条件**（原文）：`c >= F/B`，其中 `c` 为每 compute block 分配的序列长度，`F` 为每设备 FLOPS，`B` 为设备间带宽；详见原论文推导。
- **最优配置约束**（原文）：`seq-length / context-parallel-size > 8K`，否则 8K 下 compute 时间较短，CP 切分后的 send/recv 时间会超过 compute 时间，性能反而下降。
- **量化准则**（原文）：`S/(T*alpha) >= 1/(W*beta)`，其中 `S = seq-length / context-parallel-size`，`T` 为芯片理论算力，`alpha` 为计算效率，`W` 为理论通信带宽，`beta` 为带宽利用率。
- **效果结论**（原文）：相比不开启序列并行，单步 latency 增大；但相比重计算（recomputation），计算效率提升。

---

## 【表格解读】

原文 Usage 章节参数表逐字还原：

| Key Parameter | Description |
| --- | --- |
| --context-parallel-size [int] | Sets the number of context-parallel ranks. The default is 1. Configure it based on your requirements. |
| --seq-length [int] | Input sequence length. |
| --use-cp-send-recv-overlap | Recommended. Enables send-receive overlap. |
| --attention-mask-type [general/causal] | Optional. Sets the mask computation type. The default is causal (triangular) mask computation. Setting `general` enables full computation. |
| --context-parallel-algo megatron_cp_algo | Long-sequence parallelism algorithm option. The default is `ulysses_cp_algo`. Set it to `megatron_cp_algo` to enable Ring Attention. |

逐行解读：

- `--context-parallel-size`：CP rank 数量，默认 1（即关闭），按需开启长序列并行；该参数决定序列被切多少份。
- `--seq-length`：输入序列长度，与 CP size 共同决定每份子序列长度 `S = seq-length / context-parallel-size`。
- `--use-cp-send-recv-overlap`：**推荐**开启，用于让 KV block 的 send/recv 与本地 attention 计算重叠，匹配文档所述"计算与通信可重叠"的核心机制。
- `--attention-mask-type`：可选 `general`（全量计算）或 `causal`（默认，三角/因果掩码）；GPT 类模型建议 `causal`。
- `--context-parallel-algo`：**关键开关**，默认 `ulysses_cp_algo`（Ulysses 方案），需显式设为 `megatron_cp_algo` 才启用 Ring Attention。

---

## 【公式解读】

原文共有两条公式/不等式，逐字保留并解释：

**公式 1（重叠理论条件，原文 Notes 引用）：**

$$c \geq F / B$$

- `c`：每个 compute block 所分到的序列长度（per-device compute block sequence length）。
- `F`：每设备的 FLOPS（计算能力）。
- `B`：设备之间的通信带宽（inter-device bandwidth）。
- **作用**：保证本地 attention 计算耗时能够"覆盖"一次 KV block 通信耗时，从而实现计算与通信完全重叠；`c` 越大重叠越充分。详细推导见原文引用的 arXiv 2310.01889。

**公式 2（8K 性能拐点的量化判据，原文 Notes 第 3 条）：**

$$S / (T \cdot \alpha) \geq 1 / (W \cdot \beta)$$

其中 `S = seq-length / context-parallel-size`：

- `S`：每个 CP rank 实际承载的子序列长度。
- `T`：芯片的理论计算能力（theoretical compute capability of the chip）。
- `alpha`：`T` 的实际计算效率折扣系数（computation efficiency）。
- `W`：理论通信带宽（theoretical communication bandwidth）。
- `beta`：带宽利用率（bandwidth utilization）。
- **作用**：左侧 `S / (T·alpha)` 近似"每个 CP rank 真实计算时间"，右侧 `1 / (W·beta)` 近似"一次通信时间"。不等式成立意味着单次计算足以掩盖单次通信，是能否获得性能收益的临界条件。原文据此给出经验阈值：`seq-length / context-parallel-size > 8K`。

---

## 【关联】

- **Megatron Core（mcore）特性集合**：本文档路径为 `docs/en/pytorch/features/mcore/ring-attention-context-parallel.md`，属于 mcore 特性家族，与同仓其他 mcore 特性（如 TP/PP/CP 的组合）共享 `--context-parallel-size` 等基础参数。
- **Context Parallel (CP) 算法切换**：通过 `--context-parallel-algo` 在 `ulysses_cp_algo`（Ulysses）与 `megatron_cp_algo`（本文 Ring Attention）之间二选一；二者是同一上下文并行框架下的两种算法实现。
- **FlashAttention**：Ring Attention **必须**与 FlashAttention 协同使用（原文 Notes 第 1 条："When Context Parallel is enabled, you must also enable FlashAttention"），由后者提供底层高效 attention 内核。
- **MoE 训练**：Use Cases 章节指出 GPT 类模型一旦进入 MoE 层，序列长度即超 8K，是本特性的典型触发场景；与 MoE 特性形成上下游依赖（上游长序列 → 下游进入 MoE → 进一步放大对 CP 的需求）。
- **重计算（recomputation）**：原文 Effects 中将 Ring Attention 与 recomputation 比较计算效率，表明其可作为重计算的替代/补充来降低显存。
- **外部依赖（论文）**：引用 Liu et al., *Ring Attention with Blockwise Transformers for Near-Infinite Context*, arXiv:2310.01889，本文是该论文思想在 mindspeed-llm 中的工程落地说明。

---

## 【使用方法】

依据原文 Usage 表格与 Notes 章节，启用 Ring Attention 的最小步骤：

1. **启用 FlashAttention**（强制项，原文 Notes 第 1 条）。
2. 设置序列相关参数：
   - `--seq-length <int>`：根据目标长序列长度设置。
   - `--context-parallel-size <int>`：默认 1，按需设为大于 1 的值；建议满足 `seq-length / context-parallel-size > 8K`。
3. **切换 CP 算法**为 Ring Attention：
   - `--context-parallel-algo megatron_cp_algo`（默认是 `ulysses_cp_algo`，不指定不会启用本特性）。
4. （推荐）开启通信重叠：
   - `--use-cp-send-recv-overlap`（用于让 KV block send/recv 与本地 attention 重叠）。
5. （可选）选择 mask 类型：
   - `--attention-mask-type causal`（默认，GPT 类模型建议使用）或 `general`。
6. GPT 类模型训练时，原文 Notes 第 2 条建议将 `--attention-mask-type` 显式设为 `causal`。

> 原文未提供完整启动命令样例或 yaml 配置片段，仅以参数表 + Notes 形式给出约束。
