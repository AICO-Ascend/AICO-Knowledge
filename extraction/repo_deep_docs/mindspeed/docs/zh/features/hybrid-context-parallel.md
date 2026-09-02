# 混合长序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/hybrid-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/hybrid-context-parallel.md

# 混合长序列并行 — 一体化深度解读

## 【定位】

本篇文档描述 mindspeed（昇腾大模型加速库）中"混合长序列并行"（Hybrid Context Parallel）能力：通过对 Ulysses 与 Ring Attention 两种序列并行方案做融合，取长补短，以突破单一方案在超长序列训练场景下的可扩展性上限与带宽利用率瓶颈。

---

## 【技术要点】

1. **要解决的根问题**：在序列维度 S 增长时，训练内存开销以 $O(S^2)$ 速度增长（注意力矩阵为 S×S），传统数据/张量/流水线并行都不沿序列维度切分，因此需要专门的序列并行方案。
2. **Ulysses 的局限**：要求 attention head 数能被序列并行维度整除；在 GQA、MQA 场景下，序列并行的可扩展大小受限，进而限制序列长度的扩展。
3. **Ring Attention 的局限**：并行维度不受 attention head 数限制，理论上序列长度可无限扩展；但通信与计算带宽利用率不及 Ulysses，序列块（chunk）较小时性能劣于 Ulysses。
4. **融合思路**：将序列并行维度拆分为「Ulysses 维度 × Ring Attention 维度」两层，融合两种方案以同时获得带宽利用率与可扩展性。理论依据来自文献 *USP: A Unified Sequence Parallelism Approach for Long Context Generative AI*。
5. **兼容性**：与 FlashAttention 兼容，默认开启 FlashAttention。
6. **附带能力**：混合长序列并行同时支持 Ring Attention 系的特性，包括 send/receive overlap 功能与 Mask 计算类型配置。

---

## 【关键机制与数据】

- **内存增长规律（原文）**：当序列维度 S 增长时，训练内存开销以 $O(S^2)$ 速度增长（来源：attention 计算与 S×S 注意力矩阵相关）。
- **可扩展性差异（原文）**：Ulysses 受 `num-attention-heads % sequence_parallel_size == 0` 约束，Ring Attention 在并行维度上无此约束，因此序列长度可"理论上无限拓展"。
- **性能取舍（原文）**：Ring Attention 在"序列块大小较低时性能劣于 Ulysses"——这是文档明确给出的性能定性结论，原文未提供具体数值。
- **使用效果（原文）**：
  - "利用多个计算设备对输入序列进行并行切分，降低单设备的内存消耗"——内存维度的收益。
  - "相比不开启序列并行单步耗时增加"——开启混合并行后单步时延会变高。
  - "相比重计算计算效率提升"——相对 activation/gradient checkpointing 重计算方案有更高计算效率。
- **FlashAttention（原文）**：目前已默认开启 FlashAttention。

> 原文未给出具体的数值基准（如吞吐提升百分比、显存节省 MB 等），故本节不杜撰任何具体性能数字。

---

## 【表格解读】

原文包含 1 张参数配置表，逐字还原如下：

| 重要参数 | 参数说明 | 是否必选 | 默认值 |
|---|---|---|---|
| `--context-parallel-size [int]` | 设置长序列并行大小，默认为 1，根据用户需求配置。 | 否 | 1 |
| `--ulysses-degree-in-cp [int]` | 该参数需大于 1，且 `--context-parallel-size` 可以被该参数整除。例如当设置 `--context-parallel-size` 为 8 时，可以设置 `--ulysses-degree-in-cp` 为 2 或 `--ulysses-degree-in-cp` 为 4。<br>同时需要确保 `--num-attention-heads` 可以被 `--ulysses-degree-in-cp * --tensor-model-parallel-size` 的乘积整除。 | / | / |
| `--context-parallel-algo` | 长序列并行算法选项：<br>• `ulysses_cp_algo`：开启 Ulysses 长序列并行<br>• **`hybrid_cp_algo`**：开启 Hybrid 长序列并行<br>• `megatron_cp_algo`：开启 Ring Attention 长序列并行 | 否 | `megatron_cp_algo` |

逐行解读：

- **`--context-parallel-size`**：序列并行的总大小（"CP size"），即所有参与序列并行的设备总数。默认 1 即关闭序列并行；设为 N 即把序列切分到 N 个设备上。它是混合方案的总并行度。
- **`--ulysses-degree-in-cp`**：在 CP 总维度中分给 Ulysses 的那一部分维度。约束有两层：
  1. 必须大于 1，即混合方案中 Ulysses 维度至少为 2（否则退化为纯 Ring Attention，与文档所称"混合"不符）；
  2. 必须能整除 `--context-parallel-size`，因为 CP 总维度 = Ulysses 维度 × Ring Attention 维度（环形维度 = CP size / ulysses_degree_in_cp），因此 ulysses_degree_in_cp 必须是 CP size 的因子。文档给出的示例：CP size = 8 时，ulysses_degree_in_cp 可取 2 或 4，对应的 Ring Attention 维度分别为 4 或 2。
  3. 第二个约束体现了 Ulysses 自身的 head 整除要求：`num-attention-heads` 必须能被 `ulysses-degree-in-cp × tensor-model-parallel-size` 整除——这是因为张量并行和 Ulysses 都对 attention head 做切分，两者的 head 切分乘积需整除总 head 数。
- **`--context-parallel-algo`**：算法选择器，三选一：
  - `ulysses_cp_algo`：纯 Ulysses；
  - `hybrid_cp_algo`：**本文核心**，混合方案；
  - `megatron_cp_algo`：即 Megatron 原生的 Ring Attention 实现，作为混合方案中的底层 Ring Attention 分量，文档将其同时作为默认算法与 Ring Attention 的等价入口。
  - 默认值为 `megatron_cp_algo`，意味着若想启用混合并行，必须显式将 `--context-parallel-algo` 改为 `hybrid_cp_algo`。
- "是否必选"列中，前两行为"否"或"/"，仅靠默认参数无法开启混合并行；第三行 `context-parallel-algo` 标注"否"但默认 `megatron_cp_algo`，即默认**不**开启混合——这与文档强调"开启混合需显式指定 algo"相一致。

---

## 【公式解读】

原文仅给出 1 处复杂度表述（无 LaTeX 包裹，本节按原文保留写法并解释）：

- 原文表述：`$O$($S^2$)`
- 符号含义：
  - $O(\cdot)$：渐近复杂度（大 O 记号）。
  - $S$：序列维度长度（sequence length）。
  - $S^2$：表示与序列长度的平方成正比。
- 物理含义：在标准 attention 计算中，注意力矩阵形状为 $S \times S$（每个 query 要与所有 key 计算），其显存与算力开销随 $S$ 平方增长，因此当序列很长时（例如万到数十万 token）内存会成为训练瓶颈，这正是需要序列并行的根本动机。

> 文档中没有给出具体的数学公式（如环形通信 schedule、Ulysses all-to-all 切分表达式等），故仅保留上式并解读。

---

## 【关联】

本节基于文档正文提及的能力/模块进行梳理（文档未提供内部链接列表，故以正文引用为准）：

- **FlashAttention**：混合长序列并行兼容 FlashAttention，并默认开启——属于上游/兼容特性。
- **Ulysses 序列并行（`ulysses_cp_algo`）**：混合方案的"一半"，对应 `--ulysses-degree-in-cp` 维度，受 attention head 整除约束。
- **Ring Attention（`megatron_cp_algo`，即 Megatron CP）**：混合方案的"另一半"，提供 send/receive overlap、Mask 计算类型配置等特性——文档明确指出混合方案继承了 Ring Attention 的相关特性。
- **张量并行（`--tensor-model-parallel-size`）**：head 整除约束会与 ulysses 维度耦合（`num-attention-heads % (ulysses-degree-in-cp × tensor-model-parallel-size) == 0`），属于平行并行的依赖。
- **重计算（activation recomputation）**：文档将"重计算"作为对比基线，混合并行的计算效率相对重计算更高——这意味着两者可在更大训练配置中互为备选/补充。
- **学术文献**：USP: A Unified Sequence Parallelism Approach for Long Context Generative AI（arxiv:2405.07719），是该实现融合思路的理论来源。
- **典型应用场景**：会话式 AI、长文档摘要（章节/书籍级，数万到数十万字）、视频生成等长上下文推理/训练任务（背景章节提及）。

---

## 【使用方法】

启用混合长序列并行的最小配置组合（综合"使用场景"与参数表）：

1. 设置序列并行总大小：
   ```bash
   --context-parallel-size 8        # 例：8 路序列并行，原文示例取值
   ```
2. 设置 Ulysses 在 CP 中的维度（需 >1 且能整除 CP size）：
   ```bash
   --ulysses-degree-in-cp 2         # 或 4（当 CP size=8 时，二者合法）
   ```
   - 同时确保 `--num-attention-heads` 能被 `--ulysses-degree-in-cp × --tensor-model-parallel-size` 整除。
   - 剩余的 Ring Attention 维度 = `context-parallel-size / ulysses-degree-in-cp`，例 8/2=4 或 8/4=2。
3. 选择混合算法（**关键**：默认是 `megatron_cp_algo`，必须显式覆盖）：
   ```bash
   --context-parallel-algo hybrid_cp_algo
   ```
4. FlashAttention 默认已开启，无需额外配置（原文说明）。
5. 可选：利用混合方案继承自 Ring Attention 的特性 —— send/receive overlap 功能、Mask 计算类型配置（原文提及，但未给出具体开关/参数名，属于"原文未涉及具体配置项"的部分）。

> 原文未提供完整的命令行模板、yaml 配置片段或多节点启动脚本，故本节不杜撰。
