# 支持variable length flash attention训练场景

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/variable_length_flash_attention.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/variable_length_flash_attention.md

# 一体化深度解读：variable length flash attention 训练场景

---

## 【定位】

这篇文档解决"同一 batch 中多个文档拼接时需要在 EOD 位置重置 attention mask 与 position ids，使各文档之间互相不参与 self attention"的问题，方法是通过调用底层 FlashAttention 算子的可变长模式（variable length / TND）来支持该训练场景。

---

## 【技术要点】

1. **问题边界**：默认情况下，多个文档被拼接视为同一序列，文档间 self attention 不做 mask；而在文档独立场景下，必须在每个文档结束位置（EOD）重置 attention mask 和 position ids。
2. **核心方案**：调用底层 FlashAttention 算子的可变长模式，通过 `--reset-attention-mask` 参数使能。
3. **数据前置要求**：每个文档末尾必须追加 EOD Token；预处理阶段通过 `--append-eod` 参数完成。
4. **核心数据结构**：使能后不再初始化固定 mask，而是依据 EOD 位置生成 `actual_seq_len`（累计长度数组），实际计算量由 `actual_seq_len` 决定。
5. **关键累计规则**：当一个序列中真实文本长度分别为 `[2,2,0,2,2]` 时，`actual_seq_len` 为 `[2,4,4,6,8]`（前缀和，空文档长度保持不变即 0）。
6. **mask 形状**：使能前为 2048×2048 的压缩下三角矩阵；使能后类似"块对角下三角"，左下角空白位置不参与计算（仅逻辑上表示，实际计算时不生成）。

---

## 【关键机制与数据】

### 工作原理（按原文分两态对比）

- **使能前**（原文）：
  - 初始化 `attn_mask` 为 **压缩下三角矩阵（2048×2048）**；
  - 多个文档被视为同一序列，互相间的 self attention **没有掩盖**，所有 token 均参与计算；
  - 示意：完整下三角因果掩码（见 `causal_mask.png`）。

- **使能后**（原文）：
  - **不初始化 mask**，根据 EOD 位置生成 `actual_seq_len`；
  - 给定单序列文档真实长度 `[2,2,0,2,2]` → `actual_seq_len` 为 `[2,4,4,6,8]`；
  - **实际计算量由 `actual_seq_len` 决定**；
  - 实际计算时 **不生成 attn_mask**，其等效可视化效果见 `varlen_mask.png`（类似块对角下三角，左下角空白处不参与计算）。

### 数据流

1. 原始数据（parquet）→ `preprocess_data.py` 预处理（追加 EOD）→ 训练脚本。
2. 训练脚本传入 `--reset-attention-mask` → 框架依据 EOD 切分文档 → 生成 `actual_seq_len` → 传给 FlashAttention 算子的可变长模式 → 文档间不再相互 attention。

### 性能数据

- **原文未涉及**任何量化性能/吞吐/加速比数据。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式（无 LaTeX / 无伪代码）**。

但原文给出了一个**算法式数据变换关系**，可理解为"前缀和"形式的描述：

> 单个序列中文本真实长度分别为 `[2,2,0,2,2]`，则 `actual_seq_len` 为 `[2,4,4,6,8]`。

逐位解释：
- `[2,2,0,2,2]`：该序列由 5 个文档拼接而成，各文档有效 token 数依次为 2、2、0、2、2；第 3 个文档为空（长度为 0）。
- `[2,4,4,6,8]`：对应位置为前缀和——`2`、`2+2`、`2+2+0`、`2+2+0+2`、`2+2+0+2+2`，标识**到第 i 个文档为止（含）的累计实际序列长度**。
- 作用：FlashAttention 可变长模式据此切分"块对角下三角"区域，使每个文档的 attention 仅在其自身累计长度范围内计算，从而天然实现文档间相互隔离。

---

## 【关联】

原文内部链接标注为 "(无)"，故无法直接给出文中提及的其他特性/模块的内部跳转链接。

依据文档自身内容，可梳理出以下**功能链路**关联（均为原文描述范围内可推断）：

- **数据预处理模块**：`preprocess_data.py`（需配合 `--append-eod` 与 `--tokenizer-type PretrainedFromHF`）→ 输出含 EOD 的训练语料。
- **训练脚本入口**：通过新增的 `--reset-attention-mask` 参数开关该能力。
- **底层算子**：FlashAttention 的 **可变长模式（variable length / TND）**——这是算子层的能力，框架层通过 `actual_seq_len` 暴露给上层使用。
- **mask 与 position_ids 配套**：原文强调"attention mask **和** position ids 需要在每个文档结束的位置（EOD）被重新设置"，说明该特性同时影响 mask 与 position_ids 两套机制（但具体 position_ids 的生成细节原文未展开）。

---

## 【使用方法】

### 数据准备

每个文档末尾追加 EOD Token，使用 `preprocess_data.py` 时必须增加 `--append-eod`：

```shell
python ./preprocess_data.py \
   --input ./dataset/train-00000-of-00001-a09b74b3ef9c3b56.parquet \
   --tokenizer-name-or-path ./model_from_hf/Llama3-hf/ \
   --output-prefix ./dataset/enwiki \
   --workers 4 \
   --log-interval 1000  \
   --append-eod \
   --tokenizer-type PretrainedFromHF
```

### 训练参数

在模型训练脚本中新增 `--reset-attention-mask`：

- 使能后，框架根据 EOD 位置生成变量 `actual_seq_len`，标识多个文档（doc）拼接的**实际长度**；
- 实际计算时不生成 attn_mask，**实际计算量由 `actual_seq_len` 决定**。

### 依赖关系（原文给出的前置约束）

- 必须使用 TND（variable length）模式时，**必须先确保** EOD Token 已正确追加（"使能TND必须增加eod: `--append-eod`"）；
- 文档互不 attention 的隔离边界完全由 EOD 位置决定，因此 EOD 的正确性是本特性生效的前提。
