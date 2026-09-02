# kvallgather 长序列并行

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/kvallgather-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/kvallgather-context-parallel.md

# kvallgather 长序列并行 — 深度解读

## 【定位】
本文档介绍在昇腾 LLM 分布式训练框架（mindspeed-llm）中，针对 **sparse flash attention / lightning indexer / lightning indexer loss** 三类算子的 **KV AllGather 长序列并行（context-parallel）算法**，即在 attention 计算前对已被 CP 切分的 K/V 做一次 allgather 通信以恢复完整 K/V，从而支持定长 padding 下的长序列训练。

---

## 【技术要点】

1. **核心思想**：在进入 sparse flash attention、lightning indexer、lightning indexer loss 计算之前，先对已经按 context-parallel 维度切分的 key 和 value 执行 allgather 通信，把每个 rank 上分散持有的 K/V 片段重新汇聚成完整的 K/V，再交给注意力算子使用。
2. **算法名称**：长序列并行算法选项 `--context-parallel-algo` 需设置为 `kvallgather_cp_algo`，用以开启本特性。
3. **CP 维度的启用**：通过 `--context-parallel-size [int]` 启用 CP 并行；该参数默认为 `1`，需按用户实际需求配置。
4. **序列长度约束**：必须显式指定 `--seq-length [int]`，且该值要求能被 `2 * context-parallel-size` 整除。
5. **序列切分方式**：仅支持**定长 padding 训练场景**，并且采用**负载均衡的序列切分方式**。
6. **算子/掩码覆盖范围**：当前仅适配 sparse flash attention、lightning indexer 融合算子、lightning indexer loss 融合算子三类算子；同时仅支持 `--attention-mask-type=causal`。

---

## 【关键机制与数据】

- **工作原理（原文）**：针对 sparse flash attention、lightning indexer、lightning indexer loss 这三类算子，在计算前对已切分的 key 和 value 执行 allgather 通信操作，从而获得完整的 key 和 value，再喂给后续 attention / indexer 计算。
- **数据流（原文）**：
  1. K/V 已被 context-parallel 切成多片，分布在 `context-parallel-size` 个 rank 上。
  2. 在指定的三个算子计算之前，先做一次 **allgather**，将各 rank 的 K/V 片段收齐成完整 K/V。
  3. 用完整的 K/V 进入 sparse flash attention / lightning indexer / lightning indexer loss 的计算。
- **性能数据**：原文未提供具体的性能数字、吞吐/加速比或带宽占用等指标，仅给出机制说明与配置约束。

---

## 【表格解读】

下表为原文"使用方法"章节的关键参数表，按原文逐字还原：

| 重要参数 | 参数说明 |
|---|---|
| `--context-parallel-size [int]` | 设置 CP 对应的数量，默认为 1，根据用户需求配置。 |
| `--context-parallel-algo <b>kvallgather_cp_algo</b>` | 长序列并行算法选项，设置为 `kvallgather_cp_algo`，开启 KVAllGather 长序列并行。 |
| `--seq-length [int]` | 输入序列的长度。 |

逐行解读：

- **`--context-parallel-size [int]`**：context-parallel 的并行度（即切分 K/V 的 rank 数量）。默认值为 `1`，即不启用 CP 切分；启用本特性时需按需调大。它直接决定了 allgather 通信的参与 rank 数与切分粒度，并且会与下文 `--seq-length` 形成 `seq-length % (2 * CP-size) == 0` 的约束。
- **`--context-parallel-algo <b>kvallgather_cp_algo</b>`**：选择 context-parallel 的具体算法实现。本特性要求把该参数显式设置为 `kvallgather_cp_algo`，作为开启"先 allgather K/V 再做 attention"这一流程的总开关。
- **`--seq-length [int]`**：训练样本的输入序列长度。文档给出约束：`seq-length` 须能被 `2 * context-parallel-size` 整除；并且训练需采用定长 padding 场景 + 负载均衡的序列切分方式。

---

## 【公式解读】

原文无公式（既无 LaTeX 公式也无伪代码形式的算式）。

可由原文约束隐含写出的一个整数整除关系（仅作约束转述，非原文公式）：

$$
\text{seq-length} \;\bmod\; (2 \times \text{context-parallel-size}) \;=\; 0
$$

- `seq-length`：输入序列长度（对应 `--seq-length`）。
- `context-parallel-size`：CP 并行度（对应 `--context-parallel-size`）。
- 作用：保证在使用负载均衡的定长 padding 序列切分时，序列能被 `2 * CP-size` 整除，从而每段切分大小一致、allgather 拼接完整。

---

## 【关联】

- **算法定义与详细文档**：本文档指向更详细的算法说明页面 **`kvallgather_cp_algo`**，链接为 `https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/kvallgather-context-parallel.md`（原文已给出）。该链接位于本仓库外的 `MindSpeed` 主仓 "docs/zh/features/" 目录下，提供本特性的完整背景与机制说明。
- **特征路径**：本文档位于 `docs/zh/pytorch/features/mcore/` 目录下，对应 "mcore" 特性集合，意味着该 kvallgather 长序列并行能力是在 mcore（Megatron-Core）模型栈下、针对 PyTorch 训练流程的扩展。
- **关联算子**：本特性的能力边界明确绑定三类融合算子 —— **sparse flash attention**、**lightning indexer**、**lightning indexer loss**；其余 attention 路径未在本文档的适配范围内。
- **上游特性**：与 context-parallel（CP）整体能力同源，因此与同框架下其他 CP 算法（如常见的 ring/ulysses 等，原文未列具体名）共享 `--context-parallel-size` 与 `--context-parallel-algo` 这两个开关。

---

## 【使用方法】

启用本特性需同时设置以下三个参数（按原文"使用方法"表格与"注意事项"原文）：

1. 设置 CP 并行度：`--context-parallel-size <int>`，按需配置（默认 `1`，启用本特性时需大于 1）。
2. 选择 CP 算法：`--context-parallel-algo kvallgather_cp_algo`。
3. 设置序列长度：`--seq-length <int>`，且必须满足 `seq-length % (2 * context-parallel-size) == 0`。

额外的训练侧前提（原文"注意事项"原文）：

- 训练采用 **定长 padding**，并使用 **负载均衡的序列切分** 方式。
- `--attention-mask-type` 需设为 **`causal`**。
- 当前仅在 **sparse flash attention / lightning indexer / lightning indexer loss** 这三类融合算子上验证，其余算子不在本文档所述适配范围内。
