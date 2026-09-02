# Megatron序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/sequence-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/sequence-parallel.md

# Megatron序列并行 · 一体化深度解读

---

## 【定位】

这篇文档描述了 **Megatron 序列并行（Sequence Parallelism, SP）** 这一补充并行策略，核心解决的是**在张量并行基础上，进一步切分那些无法被张量并行分割的 LayerNorm / Dropout 类操作的输入序列维度**，从而降低激活值冗余内存、提升可训练模型规模。

---

## 【技术要点】

1. **互补定位**：序列并行并非替代张量并行，而是**依附于张量并行**的补充策略，专门处理张量并行"切不动"的操作（如 LayerNorm、Dropout）。
2. **切分对象**：将 LayerNorm / Dropout 这类**输入按序列维度（sequence dimension）**进行切分，使各设备仅负责序列上的一段。
3. **张量维度约定**：输入 $X$ 的大小约定为 $s \times b \times h$（即 sequence × batch × hidden 的标准排列）。
4. **切分表示**：沿序列维把 $X$ 切成 $X = [X_1^s, X_2^s]$，经过 LayerNorm 后得到 $Y = [Y_1^s, Y_2^s]$，**随后**才进入张量模型并行。
5. **内存收益来源**：LayerNorm/Dropout 等操作本身计算成本低，但**激活存储冗余显著**，序列并行把这部分冗余分摊到多设备。
6. **理论依据**：文档明确引用文献 *Reducing Activation Recomputation in Large Transformer Models*（arXiv:2205.05198）作为细节出处。

---

## 【关键机制与数据】

### 工作原理（数据流）

- **流程顺序**：原始输入 → 序列维度切分 → 各设备做**部分** LayerNorm / Dropout → 切分后的结果进入张量模型并行。
- **关键文字（原文）**：*"将LayerNorm以及Dropout等操作的输入按序列维度进行了切分，使得各个设备只需要做一部分的LayerNorm和Dropout等操作。"*
- **张量并行局限说明（原文）**：*"张量并行虽能有效降低内存占用并加快训练速度，但其要求将模型各层分割为独立块，这在处理如LayerNorm和Dropout等操作时存在局限。"*
- **图示说明（原文）**：文档配图 `sequence-parallel.png` 以两段为例展示 $X \rightarrow [X_1^s, X_2^s] \rightarrow [Y_1^s, Y_2^s] \rightarrow$ 张量模型并行的流向。

### 性能数据

- 原文未给出任何量化性能数据（如加速比、显存下降百分比等），仅做定性描述：*"进一步降低了内存占用，使得设备可以容纳更大参数的模型训练。"*
- 因此**不进行任何数字上的外推**。

---

## 【表格解读】

**原文无表格。** 文档以一段图示（PNG）+ 文字描述形式给出流程示意，未提供任何参数表、配置矩阵或性能对比表。

---

## 【公式解读】

原文中出现的数学/伪数学表达式只有输入张量形状的约定，**无运算公式**，按原文逐字保留如下：

### 输入张量形状约定

> 输入 $X$ 的大小为 $s \times b \times h$

- **$s$**：序列长度维度（sequence length），序列并行的**切分轴**。
- **$b$**：batch 维度（batch size），本文场景下**不切分**。
- **$h$**：隐藏层维度（hidden size），由后续张量并行负责切分。

### 序列维度切分表示

> 按照序列维度切分 $X = [X_1^s, X_2^s]$

- **$X_1^s, X_2^s$**：将 $X$ 在 $s$ 维上分成 2 段（原文示例取 2 段），各段形状约为 $\frac{s}{2} \times b \times h$。原文以"两设备"为示意，并非硬性约束。

### LayerNorm 后输出

> 经过 LayerNorm 操作后的结果为 $Y = [Y_1^s, Y_2^s]$

- **$Y_i^s$**：对应 $X_i^s$ 经过 LayerNorm 后的输出，**序列维仍保持切分状态**，与 $X_i^s$ 一一对应。

### 流程衔接（伪代码形式还原原文）

```
X : (s × b × h)
   ↓ 沿 s 维切分
[X_1^s, X_2^s]   # 各 ≈ (s/2 × b × h)
   ↓ 每设备独立 LayerNorm / Dropout
[Y_1^s, Y_2^s]
   ↓ 进入张量模型并行（沿 h 切分）
```

> 注：上述为对原文文字描述的等价还原，**未引入原文不存在的算子或变换**。

---

## 【关联】

依据文档自述及上下文逻辑，可归纳出如下关联关系（仅基于原文可推导的内容）：

1. **上游/依赖：Tensor Model Parallelism（张量并行）**
   - 原文：*"序列并行依赖张量并行"*。
   - 序列并行不是独立维度，必须在张量并行已开启的前提下生效。

2. **作用对象：LayerNorm、Dropout 等"非张量并行可切分"算子**
   - 这些算子在纯张量并行下无法切分、形成激活值冗余，序列并行正是为它们服务。

3. **文献引用：Reducing Activation Recomputation in Large Transformer Models（arXiv:2205.05198）**
   - 文档将"具体细节"指向该论文，是本特性的理论/工程实现出处。

4. **内部链接**：原文**未提供**任何内部链接（无章末"参见"、无交叉引用锚点），故不存在文末链接可解析。

5. **与仓库中其他加速特性的关系**：原文未点名提及 mindspeed 仓内其他特性（如多副本、流水线并行、零冗余优化器等），故**不做外推**。

---

## 【使用方法】

文档明确给出启用序列并行所需的训练脚本参数，原文逐字保留：

```bash
--tensor-model-parallel-size N  # 设置张量模型并行大小，N为单个并行组内的NPU数目
--sequence-parallel             # 开启序列并行
```

**关键约束（原文）**：
- **必须先配置 `--tensor-model-parallel-size N`**：因为序列并行"依赖张量并行"，不设张量并行大小则序列并行无法独立生效。
- **`--sequence-parallel`** 为布尔开关，用于开启序列并行策略。
- **`N` 的含义（原文）**：单个并行组内的 NPU 数目。
- 原文**未涉及**如何与流水线并行（`--pipeline-model-parallel-size`）、数据并行等其他并行维度组合的具体配置，也未给出推荐取值或环境变量脚本片段，**故不补充**。
