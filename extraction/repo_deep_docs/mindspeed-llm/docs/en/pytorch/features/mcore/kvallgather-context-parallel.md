# KVAllGather Long-Sequence Parallelism

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/kvallgather-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/kvallgather-context-parallel.md

# 深度解读: KVAllGather Long-Sequence Parallelism

---

## 【定位】

本文档介绍 Mindspeed-LLM 中一种**长序列上下文并行 (CP) 算法 `kvallgather_cp_algo`**, 通过在计算前对按序列维度切分的 K/V 张量执行 **All-Gather 通信**, 解决稀疏 Flash Attention、Lightning Indexer 等融合算子在超长序列训练时因 K/V 分片而无法直接使用的问题。

---

## 【技术要点】

1. **核心操作 — K/V All-Gather**: 在执行稀疏 Flash Attention、Lightning Indexer、Lightning Indexer Loss 这三类融合算子之前, 先对已被 CP 切分 (partitioned) 的 key、value 张量做一次 All-Gather, 在目标 rank 上重建出**完整的 K/V 张量**再进行 attention 计算。
2. **依赖的上下文并行规模**: 必须设置 `--context-parallel-size` 大于 1 才有效, 默认值为 **1** (即不启用 CP)。
3. **算法选择开关**: 通过 `--context-parallel-algo` 指定为 `kvallgather_cp_algo`, 即触发该长序列并行算法。
4. **序列长度约束**: `--seq-length` (输入序列长度) **必须能被 `2 * context-parallel-size` 整除**, 这是该算法使用**负载均衡序列切分 (load-balanced sequence partitioning)** 的硬性前提。
5. **算子适用范围限制**: 当前**仅支持**三个融合算子 —— sparse flash attention 融合算子、lightning indexer 融合算子、lightning indexer loss 融合算子。
6. **注意力掩码限制**: 当前**仅支持** `--attention-mask-type` 设置为 `causal` (因果掩码)。

---

## 【关键机制与数据】

**工作原理 (原文):**
- 在 CP > 1 时, 序列会被切分到不同的 rank 上, 每个 rank 仅持有 K/V 张量的一部分 (partitioned key and value tensors)。
- 该算法的做法是: **在计算前对 K/V 做一次 All-Gather**, 让参与计算的 rank 拿到**完整的 K/V** (the complete key and value tensors), 然后再交给稀疏 Flash Attention / Lightning Indexer 等融合算子执行后续计算。
- 其切分方式为**固定长度填充 + 负载均衡序列切分** (fixed-length padding + load-balanced sequence partitioning), 因此序列长度与 CP 规模的乘除关系是约束条件。
- 内部链接指向中文版详细算法说明: `kvallgather_cp_algo` (原文链接: https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/kvallgather-context-parallel.md)。

**数据流概览 (基于原文推导):**
输入序列 → 按 `--seq-length` 与 `2*CP` 关系切分到各 rank → 每 rank 持有局部 K/V → 算子调用前触发 **All-Gather** → 各 rank 获得完整 K/V → 送入 sparse flash attention / lightning indexer / lightning indexer loss 融合算子 → 输出结果。

> 原文未提供性能数据 (无吞吐量、时延、通信量数字), 故此处不臆造。

---

## 【表格解读】

原文逐字还原 (Usage 参数表):

| Key Parameter | Description |
| --- | --- |
| `--context-parallel-size [int]` | Number of context-parallel ranks to enable. The default is 1. Configure it based on your requirements. |
| `--context-parallel-algo` **kvallgather_cp_algo** | Long-sequence parallelism algorithm option. Set it to `kvallgather_cp_algo` to enable KVAllGather long-sequence parallelism. |
| `--seq-length [int]` | Input sequence length. |

**逐行解读:**

| 参数 | 类型/取值 | 作用 | 关键约束/默认 |
| --- | --- | --- | --- |
| `--context-parallel-size` | `[int]` | 启用 CP 的 rank 数量, 是上下文并行的规模开关 | 默认 **1**; 必须配合 `--context-parallel-algo=kvallgather_cp_algo` 且需 ≥2 才有意义 |
| `--context-parallel-algo` | 取值 `kvallgather_cp_algo` | 选择长序列并行算法实现 | 必须显式设为 `kvallgather_cp_algo` 才会启用本文所述的 K/V All-Gather 策略 |
| `--seq-length` | `[int]` | 训练输入序列长度 | Notes 中进一步约束: **必须能被 `2 * context-parallel-size` 整除** |

---

## 【公式解读】

**原文无公式。** 文档仅给出参数表与文字描述, 未包含任何 LaTeX 公式或伪代码形式推导。可量化的关系仅以自然语言形式出现于 Notes 第 3 条: "`--seq-length` 必须能被 `2 * context-parallel-size` 整除"。

---

## 【关联】

- **上游算法说明**: 文档正文显式链向仓库内**中文版详细文档** `kvallgather_cp_algo` (路径 `docs/zh/features/kvallgather-context-parallel.md`, 链接: `https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/kvallgather-context-parallel.md`), 提供该长序列并行算法的具体实现细节。
- **下游/被加速对象**: 三类融合算子 —— `sparse flash attention`、`lightning indexer`、`lightning indexer loss`, 它们需要**完整的 K/V 张量**才能工作, 因此依赖本特性提供的 All-Gather 步骤。
- **依赖的注意力掩码机制**: 限定 `--attention-mask-type=causal`, 与上层 attention 调度逻辑紧耦合。
- **文末内部链接**: (无) — 原文未给出额外的内部交叉链接。

---

## 【使用方法】

**启用步骤 (基于原文 Usage 与 Notes 整合):**

1. 设置 `--context-parallel-size [int]` 为大于 1 的整数 (默认 1, 按需配置)。
2. 设置 `--context-parallel-algo kvallgather_cp_algo`, 显式指定长序列并行算法。
3. 设置 `--seq-length [int]`, **该值必须能被 `2 * context-parallel-size` 整除**。
4. 同时确保 `--attention-mask-type` 设置为 `causal`。
5. 仅在以下三类融合算子场景下使用: **sparse flash attention 融合算子、lightning indexer 融合算子、lightning indexer loss 融合算子**; 且当前仅支持**固定长度填充 (fixed-length padding)** 训练场景。

原文未给出具体的命令行示例、训练脚本片段或配置文件 YAML 模板, 故仅按上述参数清单归纳。
