# Ring Attention长序列并行

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/ring-attention-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/ring-attention-context-parallel.md

# Ring Attention 长序列并行 — 一体化深度解读

## 【定位】

这篇文档针对**长序列训练场景下序列维度无法被现有并行策略（数据/张量/流水线）切分、导致注意力显存随序列长度 $O(S^2)$ 膨胀**的问题，介绍并启用 **Ring Attention（环状注意力）长序列并行方案**，使序列长度理论上可无限扩展，同时通过计算与 KV 通信的掩盖消除额外开销。

---

## 【技术要点】

1. **问题根源**：序列长度 $S$ 增加时，注意力矩阵显存按 $O(S^2)$ 增长；数据并行、张量并行、流水线并行均无法切分序列维度。
2. **核心方案**：Ring Attention 借鉴 **分块 Softmax** 原理，将 attention 与 FFN 以**分块方式**在多设备间分布，避免持有完整注意力矩阵。
3. **通信拓扑**：在进程间构建**环状 (Ring) 通信结构**，每个进程持有序列维度的本地 QKV 切块；本地 attention 计算完毕后，通过 **向后发送 + 向前获取 (send/recv)** KV 块沿环遍历，完成逐块注意力与 FFN。
4. **零拼接与可扩展**：attention 计算全程**不需数据拼接**，理论上支持的序列长度可无限拓展。
5. **计算/通信掩盖**：本地 attention 计算与 KV 块的通信理想情况下可互相掩盖，**消除额外引入的通信开销**。
6. **兼容性与默认行为**：当前已**默认开启 FlashAttention**；与 Ulysses 方案不同，**不需要 head_size 被 cp_size 整除**；使用条件为 GPT 类模型 + 数据进 MoE 层时实际序列长度 **8K 以上**。

---

## 【关键机制与数据】

**工作原理**：
- **分块 Softmax 分摊显存**：通过分块计算，使得每个设备不必持有完整 $S \times S$ 注意力矩阵，从根本上规避 $O(S^2)$ 显存增长。
- **Ring 流水线计算**：每个进程持本地 QKV 块 → 先做本地 attention → 沿环向后发本地 KV / 从前方收下一块 KV → 复用收到的 KV 继续算 attention → 循环一周回到自身完成所有块。
- **掩盖条件（原文）**：为让计算与通信互相掩盖，理论上需 **$c \geq F/B$**，其中 $c$ 为每个计算块分到的序列长度，$F$ 为每个 device 的 FLOPS，$B$ 为每个 device 间的带宽；原文强调"实践中需要确保每个计算块分到的序列长度足够大"。

**性能/效果数据（原文）**：
- 相比不开启序列并行：**单步耗时增加**。
- 相比**重计算（activation recompute/checkpointing）**：**计算效率提升**。
- 单设备**内存消耗降低**。
- **8K 序列长度下的退化现象**：原文明确指出，"在 8K 的序列长度情况下，由于计算的时间缩短，CP 功能分割之后的 send receive 的时间反而会长于计算时间，造成性能的下降"，因此建议 `seq-length / context-parallel-size > 8K` 以获取最佳效果。

**Mask 类型语义**：默认 **causal（倒三角）** Mask；设为 **general** 代表全量计算。

---

## 【表格解读】

下表为原文"使用方法"章节中关于**重要参数**的表格，**逐字还原**如下：

| 重要参数 | 参数说明 |
|---|---|
| --context-parallel-size [int] | 开启CP对应的数量，默认为1，根据用户需求配置。 |
| --seq-length [int] | 输入序列的长度。 |
| --use-cp-send-recv-overlap | 建议开启，开启后支持send receive overlap功能。 |
| --attention-mask-type [general/causal] | 可选，设置Mask计算类型，默认是causal（倒三角）Mask计算，设置general代表全量计算。 |
| --context-parallel-algo megatron_cp_algo | 长序列并行算法选项，默认项为`ulysses_cp_algo`，当设置为`megatron_cp_algo`时开启Ring Attention。 |

**逐行解读**：

- **`--context-parallel-size`**：CP 度数（cp_size），决定序列被切成几段同时跑多少路 Ring。默认 1 即不开启 CP，需按场景配置为 ≥2 才生效。
- **`--seq-length`**：总输入序列长度 $S$。结合上一项，Ring Attention 的实际每块序列长度 = `seq-length / context-parallel-size`。
- **`--use-cp-send-recv-overlap`**：开启 send/recv 与计算的 overlap，原文建议开启，与"$c \geq F/B$ 时计算通信可掩盖"的理论条件相对应。
- **`--attention-mask-type`**：控制注意力掩码形态。causal 适合 GPT 类自回归训练（原文注意事项中也专门建议 GPT 训练用 causal）；general 用于全量/双向注意力场景。
- **`--context-parallel-algo`**：在 `ulysses_cp_algo`（默认）与 `megatron_cp_algo`（Ring Attention 实现）之间二选一，**仅当设为 `megatron_cp_algo` 时才开启本文所述的 Ring Attention 长序列并行**。

---

## 【公式解读】

**公式 1（问题规模）：序列维显存复杂度**

$$O(S^2)$$

- $O(\cdot)$：渐进复杂度记号。
- $S$：序列长度（对应 `--seq-length`）。
- **作用**：刻画注意力矩阵随序列长度的二次方增长，这是 Ring Attention 要解决的根本瓶颈。

**公式 2（掩盖条件）：计算块粒度的下界**

$$c \geq F / B$$

- $c$：每个计算块分到的序列长度。
- $F$：每个 device 的 FLOPS（理论算力）。
- $B$：每个 device 间的带宽。
- **作用**：要使 KV 通信与本地 attention 计算在时间上重叠，**单个计算块所含序列长度必须不小于"算力 / 带宽"之比**。实践中要求 $c$ 足够大以保证掩盖效果较好。

**公式 3（最佳性能准则）：计算/通信时间比例**

$$\frac{S}{T \cdot \alpha} \geq \frac{1}{W \cdot \beta}$$

- $S$：即 `seq-length / context-parallel-size`（原文："S = seq-length / context-parallel-size"）。
- $T$：芯片的理论算力。
- $\alpha$：计算效率（实际算力 / 理论算力）。
- $W$：理论通信带宽。
- $\beta$：带宽利用率。
- **作用**：原文作为**配置 `seq-length / context-parallel-size > 8K` 的数学依据**——左侧代表每块的有效"算力时间"，右侧代表通信时间；只有左侧 ≥ 右侧时才能形成掩盖而不退化，这与公式 2 在量纲上一致（$S / T\alpha \geq 1 / W\beta \Leftrightarrow S \geq T\alpha / (W\beta)$，即每设备序列长度须超过"算力带宽比"）。

---

## 【关联】

- **与 Ulysses 长序列并行的关系**：原文在"使用场景"中明确将本方案与 **Ulysses 方案** 作对比——Ring Attention **不需要 head_size 被 cp_size 整除**（这是 Ulysses 的硬约束），同时在 `使用方法` 表中通过 `--context-parallel-algo` 实现二者切换（默认 `ulysses_cp_algo`，设为 `megatron_cp_algo` 启用 Ring Attention）。两者可视为同一 CP 接口下的两种算法实现。
- **与 FlashAttention 的依赖与协同**：
  - "使用场景"标注"**可兼容 FlashAttention，目前已默认开启**"。
  - "注意事项"第 1 条："**开启 Context Parallel 时需要同时开启 Flash Attention 特性，否则特性不支持**"——这是强依赖。
- **与 MoE / GPT 类模型的协同**："使用场景"说明启用条件为 **GPT 类模型 + 数据进 MoE 层时实际序列长度 8K 以上**；注意事项也建议 GPT 训练中将 `attention-mask-type` 设为 `causal`。
- **与重计算的关系**：原文"使用效果"将 Ring Attention 与**重计算（activation checkpointing）** 作直接对比——相比重计算计算效率提升，作为长序列场景下替代/补充显存优化手段的定位。
- **学术上游**：解决方案一节引用了原始论文 *Ring Attention with Blockwise Transformers for Near-Infinite Context*（arXiv:2310.01889）作为方法细节来源。

---

## 【使用方法】

启用本文 Ring Attention 长序列并行需至少配置（原文"使用方法"表 + 注意事项）：

1. **指定 CP 算法为 Ring Attention**：

   ```
   --context-parallel-algo megatron_cp_algo
   ```
   （默认 `ulysses_cp_algo`，不改则不会启用本文方案。）

2. **设置 CP 度数**：

   ```
   --context-parallel-size <int>     # 默认 1，需按需配置为 ≥2
   ```

3. **设置输入序列长度**：

   ```
   --seq-length <int>
   ```

4. **开启计算/通信 overlap（建议开启）**：

   ```
   --use-cp-send-recv-overlap
   ```

5. **根据模型类型选择 Mask（建议 GPT 训练用 causal）**：

   ```
   --attention-mask-type causal    # 默认；双向/全量场景改为 general
   ```

6. **强制依赖：同时开启 Flash Attention**，否则 CP 特性不支持（原文注意事项第 1 条）。

7. **配置准则**：为避免 8K 量级时 send/recv 反而压过计算造成性能下降，**建议 `seq-length / context-parallel-size > 8K`**，数学准则见公式 3 `S/(T·α) ≥ 1/(W·β)`。
