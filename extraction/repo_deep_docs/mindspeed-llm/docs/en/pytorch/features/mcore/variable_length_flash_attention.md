# Variable-Length FlashAttention Training Scenarios

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/variable_length_flash_attention.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/variable_length_flash_attention.md

# 一体化深度解读：Variable-Length FlashAttention Training Scenarios

## 【定位】
本文档针对 mindspeed-llm（昇腾 LLM 分布式训练框架）中**同一 batch 内多文档拼接后跨文档边界发生自注意力串扰**的训练场景，介绍如何启用底层 FlashAttention 算子的 **variable-length（变长）模式**，使每个文档在保持拼接效率的同时实现注意力隔离。

---

## 【技术要点】

1. **核心触发场景**：一个 batch 内将多份文档（docs）拼接为单一长序列训练时，需在 EOD（end-of-document）位置重置注意力掩码和位置 ID，防止文档间互相 attend。
2. **底层支撑**：依赖底层 FlashAttention 算子的 **variable-length** 模式（非 full square mask），由 EOD 位置驱动生成变长序列长度。
3. **数据侧开关（`--append-eod`）**：在 `preprocess_data.py` 中添加 `--append-eod` 参数，为每篇文档末尾追加 EOD token；注释明确指出**这是启用 TND 的必要前提**。
4. **训练侧开关（`--reset-attention-mask`）**：在模型训练脚本中追加该参数后，系统会基于 EOD 位置动态生成 `actual_seq_len` 变量，用以表达拼接后的真实分段长度。
5. **注意力矩阵形态的转变**：启用前为 `2048*2048` 的压缩下三角因果掩码；启用后**不再实例化稠密掩码**，改由 `actual_seq_len` 描述每段实际计算长度。
6. **示例分段映射**：原文给出真实文本长度 `[2, 2, 0, 2, 2]` 对应 `actual_seq_len` = `[2, 4, 4, 6, 8]` 的累积映射关系，作为该机制最直观的演示。

---

## 【关键机制与数据】

### 启用前（Before Enablement）

- **掩码构造**：初始化 `attn_mask` 为 `2048×2048` 的压缩下三角因果矩阵（图示 `causal_mask.png`，文档标注宽度 261）。
- **行为特征**：多份文档被视作单一序列，**跨文档的自注意力不被屏蔽**，所有 token 全部参与计算——即"无段界"语义。

### 启用后（After Enablement）

- **掩码策略**：**不再初始化掩码矩阵**；改以 EOD 位置为锚点，生成 `actual_seq_len` 来精确刻画每段的真实长度。
- **实际算力**：计算量（compute cost）由 `actual_seq_len` 决定，而非固定的上三角方阵维度。
- **注意力矩阵可被想象为分块对角 + 上三角的段内因果结构**（图示 `varlen_mask.png`，文档标注宽度 414），原文显式指出："左下空白区域不参与计算"（The blank area in the lower left does not participate in the computation）。
- **映射示例（原文数据）**：
  - 真实文本段长度：`[2, 2, 0, 2, 2]`（注意第三段为长度 0，对应末尾或空文档）
  - 生成的 `actual_seq_len`：`[2, 4, 4, 6, 8]`（每个分段对应的累计 token 数）

### 内存与算力意义

变长模式下省去的不是总序列长度，而是对**跨文档无效注意力区域的计算与显存占用**；左下空白区域不参与计算，意味着 FlashAttention 内核只需在段内执行下三角因果注意力，从而兼顾**拼接吞吐**与**文档隔离**。

---

## 【表格解读】

**原文无表格。**

文档通过命令片段、参数列表和一对图片（`causal_mask.png` / `varlen_mask.png`）承载信息，未提供任何 markdown/HTML 数据表格。

---

## 【公式解读】

**原文无显式公式。**

但其数据流可抽象为一个**累积前缀和映射**（基于原文给出的 `[2, 2, 0, 2, 2]` → `[2, 4, 4, 6, 8]` 示例反推）：

$$
\text{actual\_seq\_len}[i] = \sum_{k=0}^{i} \text{seg\_len}[k]
$$

- $\text{seg\_len}[k]$：第 $k$ 段真实文本长度（单位：token）；原示例为 $[2, 2, 0, 2, 2]$。
- $\text{actual\_seq\_len}[i]$：第 $i$ 段**结束位置**对应的拼接后全局 token 数；原示例为 $[2, 4, 4, 6, 8]$。
- 作用：告知 FlashAttention 内核**各分段的实际跨度**，使算子只对段内有效 token 做下三角因果注意力，避免跨文档污染。

注意：以上公式是依据原文示例数据**反推出的等价表达**，原文本身未以 LaTeX 或伪代码形式给出。

---

## 【关联】

- **关联到的机制 / 模块**：
  - **FlashAttention 算子（variable-length 模式）**：本特性是其在昇腾 mindspeed-llm 中的训练侧落地；机制依赖算子端的变长 API，而非应用层显式构造 mask。
  - **TND / 变长 attention 路线**：原文在 `--append-eod` 旁注释 "To enable TND, you must add EOD"，暗示该特性是 **TND（Token-with-No-len / 变长 attention）训练模式**的前置条件之一。
  - **数据预处理管线 `preprocess_data.py`**：负责产出带 EOD 的二进制序列，是该特性启用的数据侧入口。
  - **位置 ID（position IDs）重置**：与 attention mask 一同在 EOD 处被重置，确保每个文档内部从 0 开始重新计位（原文以"must be reset"形式提到）。

- **内部链接**：原文（无内部链接引用）。

---

## 【使用方法】

### 步骤 1：数据准备（添加 EOD token）

调用预处理脚本并启用 `--append-eod`：

```shell
python ./preprocess_data.py \
   --input ./dataset/train-00000-of-00001-a09b74b3ef9c3b56.parquet \
   --tokenizer-name-or-path ./model_from_hf/Llama3-hf/ \
   --output-prefix ./dataset/enwiki \
   --workers 4 \
   --log-interval 1000  \
   --append-eod \ # To enable TND, you must add EOD.
   --tokenizer-type PretrainedFromHF
```

关键参数：
- `--append-eod`：每篇文档末尾追加 EOD token；
- `--workers 4`、`--log-interval 1000`：并行与日志参数（原文显式给出）；
- `--tokenizer-type PretrainedFromHF`：与示例 `--tokenizer-name-or-path` 指向的 HuggingFace `Llama3-hf` 模型配套使用。

### 步骤 2：训练参数设置

在模型训练脚本中追加 `--reset-attention-mask`。启用后：
- 系统**不再构造** `2048×2048` 压缩下三角注意力掩码；
- 系统**基于 EOD 位置**生成 `actual_seq_len`（形如 `[2, 4, 4, 6, 8]`），用于描述每段真实长度；
- 实际计算量由 `actual_seq_len` 决定，左下空白区域不参与计算。

> 原文未给出 `megatron` / `pretrain` 等具体训练入口命令，配置项以 `--reset-attention-mask` 一项为主。
