# Online Data Rearrange

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/online_data_rearrange.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/online_data_rearrange.md

# Online Data Rearrange 文档深度解读

---

## 【定位】

本篇文档针对多模态大模型训练中因不同模态（文本/图片/音频）token数量差异巨大且动态变化所导致的 **intra-microbatch（DP间）与 inter-microbatch（DP内）负载不均衡** 问题，描述了基于 packing + 在线数据重排 的负载均衡方案与使能方式。

---

## 【技术要点】

1. **不均衡来源**：不同模态样本的 token 数量差异大且动态变化（动态分辨率），导致不同编码器、骨干网络计算量差异。不均衡分为两类：`intra-microbatch`（DP 间）与 `inter-microbatch`（DP 内）。

2. **方案目标**：实现 **LLM DP 间计算量均衡**，其中计算量定义为 **sub_seq² 的和**。

3. **packing 条件**：以 **最大序列长度 max_seq_len** 为条件进行序列 packing 拼接。

4. **重排机制核心**：通过 `all_to_all` 通信两次（一次为 encoder 负载均衡，一次恢复原索引以保证 LLM 负载均衡），配合数据索引重排，使数据按对应计算单元的负载分布。

5. **当前支持范围**：仅支持 **ViT 负载均衡**。

6. **触发开关**：启动脚本添加参数 `--use-data-balance` 以开启在线数据负载均衡。

---

## 【关键机制与数据】

**工作原理（6 步实现流程，原文）：**

1. 数据集按照**条件**（max_seq_len）和**目标**（sub_seq² 的和均衡）进行数据组装；
2. **dataloader** 数据读取后，按照 **encoder 间 DP 负载均衡**进行**数据索引重排**；
3. 根据索引位置使用 **`all_to_all` 通信**对数据进行重排；
4. encoder 执行**负载均衡计算**；
5. 按照**原始索引**再次执行 **`all_to_all` 通信**，使 embed 数据按照 LLM 负载均衡；
6. LLM 执行**负载均衡计算**。

**数据流关键节点（原文）：**
- 起点：dataloader 数据读取 → 索引重排 → all_to_all 重排 → encoder → all_to_all 复原索引 → LLM。
- 关键观察：两次 `all_to_all` 通信方向相反，第一次按 encoder 均衡打散数据，第二次按 LLM 均衡（恢复到与 LLM 计算顺序一致）拉回数据。

**性能数据：**
- 原文未涉及具体性能数字 / benchmark 指标。

---

## 【表格解读】

**原文无表格。**

（本节文档仅以文本列表形式给出方案介绍与流程，未含任何参数表、性能对比表或配置项表。）

---

## 【公式解读】

文档中出现一处非标准数学表达：

> **计算量定义为 sub_seq² 的和**

由于原文以纯文本形式书写，未使用 LaTeX / 伪代码，可逐字还原为：

$$
\text{ComputeCost} = \sum_{i} (\text{sub\_seq}_i)^2
$$

**符号含义与作用：**

| 符号 | 含义 | 作用 |
|---|---|---|
| $\text{sub\_seq}_i$ | 第 $i$ 个子序列（packing 后产生的序列片段）的长度（token 数） | 作为负载度量的基础单元 |
| $(\cdot)^2$ | 二次方 | 反映 attention 等计算量与序列长度的平方关系 |
| $\sum_i$ | 求和 | 将一个样本内所有 packing 子片段的计算量累计，得到该样本的总计算量 |
| $\text{ComputeCost}$ | 单样本总计算量 | 用于在 packing 组装 / 数据重排阶段衡量各 DP rank 上的负载是否均衡 |

文档后续以此为**目标均衡量**进行数据组装与重排——即通过对 sub_seq 序列长度的调度，使各 DP rank 上 $\sum (\text{sub\_seq}_i)^2$ 尽可能相等。原文未给出更多展开公式。

---

## 【关联】

**原文无内部链接信息（文末关联：标注为"无"）。**

但从内容可观察到的功能模块关系（原文叙述）：

- 与 **数据集（dataset）组装** 强相关：是 packing 阶段的输入与约束来源。
- 与 **dataloader** 耦合：在线重排在 dataloader 读取之后立即触发。
- 与 **encoder（具体为 ViT）**：第一次 `all_to_all` 的直接受益方，当前唯一支持的目标模块。
- 与 **LLM 主干网络**：第二次 `all_to_all` 的直接受益方，需要其配合按"原始索引"对应的均衡分布接收 embed。
- 与 **packing 方案**：二者同时启用，packing 提供 max_seq_len 约束下的拼接，重排在拼接基础上做 DP 间均衡。
- 与 **DP（数据并行）拓扑**：intra- / inter-microbatch 两类不均衡是问题前提，本方案主要解决其中一类（文本明确目标为"LLM DP 间"计算量均衡）。

---

## 【使用方法】

**启用方式（原文）：**

在训练启动脚本的 `GPT_ARGS` 中添加 `--use-data-balance` 参数：

```shell
GPT_ARGS="
    ...
    --use-data-balance \
"
```

**约束（原文）：**

- 当前**仅支持 ViT 负载均衡**。
- packing 阶段以 `max_seq_len` 为条件进行序列拼接；该参数及具体阈值在原文中**未给出**默认 / 推荐值，属于"原文未涉及"。
