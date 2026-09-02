# Alibi 位置编码

> 仓 `mindspeed` · 路径 `docs/zh/features/alibi.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/alibi.md

# Alibi 位置编码 — 一体化深度解读

## 【定位】

本文档描述 mindspeed 昇腾大模型加速库中 **Alibi 位置编码（ALiBi, Attention with Linear Biases）特性**的启用方式与使用约束，旨在解决大模型在训练/预测输入长度不一致时**外推能力不足**的痛点，从而提升长文本、多轮对话场景下的效果。

---

## 【技术要点】

1. **核心手段**：在 attention score 上叠加一个**预设的线性偏置矩阵**，而非直接对 token embedding 注入位置信息。
2. **效果定位**：相比正弦位置编码（外推能力弱）和 RoPE（外推能力有所提高但仍有限），Alibi 通过将位置差异**直接作用于 attention score** 来突出位置差异性，从而获得较强的外推能力。
3. **强依赖**：Alibi 特性**仅在开启 Flash Attention v2 时支持**，必须设置 `--use-fusion-attn-v2`。
4. **必选配置**：`--position-embedding-type alibi` + `--alibi-fusion-attn-type 2`（当前可用取值为 0 或 2）。
5. **可选行为**：通过 `alibi_diagonal_opposite` 控制 Alibi 矩阵的对角线对称取反行为；不设置时（默认）与 `--alibi-fusion-attn-type=2` 核内生成方式一致。
6. **长序列约束**：在 `--alibi-fusion-attn-type` 为 2 的**压缩模式**下，支持 **ring-attention 长序列并行**，仅适用 **causal mask** 场景；不支持 Ulysses 与混合长序列并行。

---

## 【关键机制与数据】

### 1. 解决思路（工作机制）

- **作用对象**：attention score（而非 token embedding）。
- **作用方式**：给 attention score 添加一个**预设的线性偏置矩阵**。
- **原理依据**：原文链接指向论文 <https://arxiv.org/pdf/2108.12409>（即 Press et al., 2021 的 ALiBi 论文），矩阵形态仅以图示 `alibi.png` 形式呈现，原文未给出具体公式。
- **能力来源**：位置信息直接落在 attention score 上 → 突出位置差异性 → 模型学习到的是**相对位置关系**，而非绝对位置索引 → 因此对超出训练长度的序列仍能保持稳定表现。

### 2. 数据流概览（基于原文参数推断）

- 用户侧：开启 FA v2 → 设置 `position-embedding-type alibi` → 选择 `alibi-fusion-attn-type`（0：CPU 端预生成 Alibi 矩阵后传入；2：FA v2 内核内生成）。
- 可选开关：`alibi_diagonal_opposite` 决定矩阵对角线是否对称取反。
- 模型侧：Alibi 偏置 → 注入 attention score → 影响 softmax 前的权重 → 强化相对位置编码信号。

### 3. 性能数据

原文：原文**未提供**任何基准性能数据、外推长度对比或加速比。仅以一句"模型外推能力提高"作为效果说明。

---

## 【表格解读】

原文无表格。全文仅包含一段说明文字、一张 `alibi.png` 示意图及一个论文外链，**未出现任何参数表 / 性能对比表 / 配置项表**。

---

## 【公式解读】

原文无公式。

文档中提及的"预设的线性偏置矩阵"仅以图片 `../figures/alibi.png`（400×180）可视化展示，文中**未给出任何 LaTeX 表达式或伪代码**来定义 Alibi 偏置的数值构造（如按 head 维度的斜率 `m`、head index 关系等）。如需算法细节需查阅原论文 <https://arxiv.org/pdf/2108.12409>。

---

## 【关联】

文档内部出现的依赖与互斥关系如下：

- **上游依赖（前置特性）**：
  - **Flash Attention v2**（`--use-fusion-attn-v2`）——Alibi 的**唯一支持路径**，未开启该特性则无法使用 Alibi。
- **同位/互斥特性**：
  - **Dropout**——开启 FA v2 + 长序列并行时，与 Alibi 互斥（不支持同时开启）。
  - **Ulysses 长序列并行** 与 **混合长序列并行** ——在 Alibi + `alibi-fusion-attn-type=2` 压缩模式下**不支持**；仅 **ring-attention** 长序列并行可用。
- **位置编码对比**：
  - **正弦位置编码**（外推能力弱）、**RoPE**（外推能力提高但有限），二者作为 Alibi 的能力参照对象被提及。
- **外部依赖**：
  - ALiBi 原始论文 <https://arxiv.org/pdf/2108.12409>——算法出处。
- 文档文末内部链接：**无**（mindspeed docs/zh/features 中未给出相关交叉链接）。

---

## 【使用方法】

以下配置均**取自原文**：

### 基础启用步骤

1. **开启 Flash Attention v2（强制前置）**
   ```
   --use-fusion-attn-v2
   ```

2. **启用 Alibi 位置编码（两参数必选）**
   ```
   --position-embedding-type alibi
   --alibi-fusion-attn-type 2
   ```
   - `--alibi-fusion-attn-type` 当前**仅支持 0 或 2**
     - `0`：生成 Alibi 后再传入（CPU 端预生成）
     - `1`：**暂不开放**
     - `2`：**核内生成**（推荐，与默认行为一致）

3. **可选：对角线对称取反**
   - 设置 `alibi_diagonal_opposite`：Alibi 矩阵对角线对称取反。
   - **不设置**（默认）：与 `--alibi-fusion-attn-type=2` 核内生成方式一致。

### 兼容性约束（原文明确指出）

- **Ring-attention 长序列并行**：支持，但当前**仅支持 causal mask 场景**，且 `--alibi-fusion-attn-type` 必须为 **2 的压缩模式**。
- **Ulysses 长序列并行 / 混合长序列并行**：原文标注**暂不支持**。
- **Dropout**：开启 `--use-fusion-attn-v2` 且启用长序列并行时，**Alibi 不支持开启 dropout**。

> 注：原文为图文型 feature 文档，未提供完整端到端训练命令脚本；上述用法需结合 mindspeed 的整体启动方式（如 `torchrun` + `pretrain.py` 等通用脚本，未在本文档中展开）。
