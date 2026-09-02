# 使用encoder/decoder/encoder-decoder模型进行文本生成

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_9_SEQ2SEQ_METHOD.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_9_SEQ2SEQ_METHOD.md

# 一体化深度解读：FlagAI seq2seq 三种模型文本生成指南

---

## 【定位】
本文档介绍 FlagAI 框架中实现序列到序列（seq2seq）文本生成任务的三种主流范式——**仅 Encoder、仅 Decoder、Encoder-Decoder 架构**——并为每种范式各给出对应的代表模型（RoBERTa/GLM、GPT-2、T5）与可运行的示例链接，指导用户按场景选取合适的生成方案。

---

## 【技术要点】

1. **三种 seq2seq 范式**：文档明确把 seq2seq 拆分为 (1) 仅 Encoder（带特殊 attention mask）、(2) 仅 Decoder（自回归生成）、(3) Encoder-Decoder（编码一次、循环解码）三种实现路线。
2. **Encoder 范式代表模型**：Bert、RoBERTa、GLM 等双向编码器；通过在训练时加入**特殊 attention mask**（参考微软 UniLM 思路）使模型具备 seq2seq 能力。
3. **Encoder 输入格式**：双句拼接 `[cls] 句子1[sep] 句子2[sep]`；其中**句子 1 不使用 mask**（双向可见），**句子 2 使用自回归 mask**（单向/三角可见）。
4. **Decoder 范式代表模型**：GPT-2；典型用法是给定起始文本后**自回归续写**。
5. **Encoder-Decoder 范式代表模型**：T5；encoder 一次性编码得到特征，decoder 端在自回归生成时**同时依赖自身历史与 encoder 特征**。
6. **配套示例入口**：文档给出 4 个可运行 demo 链接，覆盖 RoBERTa 标题生成、GLM 标题生成、GPT-2 中文续写、T5 标题生成。

---

## 【关键机制与数据】

**1. Encoder-only 路线的工作机制（原文）**

> "在训练过程中，我们在编码器模型中添加了一个特殊的 attention mask。"
> 来源：https://github.com/microsoft/unilm

> "该模型的输入是两个句子：[cls]句子1[sep]句子2[sep]。其中，句子_1不使用mask，而句子_2使用自回归mask。"

机制解读：原生双向 Encoder（如 BERT、RoBERTa、GLM）通过把**自回归三角 mask** 注入 attention 矩阵，使同一套参数既能像双向模型那样编码源端（句子 1），又能像自回归模型那样逐 token 生成目标端（句子 2），从而"借用"双向编码器完成 seq2seq 任务，无需显式 Decoder。

**2. Decoder-only 路线的工作机制（原文）**

> "给出一个起始文本，这个模型可以很好地延续文本。"

机制解读：GPT-2 类 Decoder 天然采用**下三角 causal mask**，文本生成等价于条件概率采样 $p(x_t | x_{<t})$。起始文本作为 prompt，模型据此续写整篇文章。

**3. Encoder-Decoder 路线的工作机制（原文）**

> "encoder只需编码一次即可获得特征编码，decoder根据自身和特征编码继续生成。"

机制解读：T5 这类典型 encoder-decoder 中，encoder 对源序列一次性计算得到全局表示 $\mathbf{K}_{\text{enc}}, \mathbf{V}_{\text{enc}}$，decoder 在每一步自回归生成时通过 cross-attention 读取该特征，同时通过 self-attention 读取已生成的目标 token。**编码只需一次**，解码需多步迭代。

**4. 性能数据**：原文未提供任何吞吐量、训练步数、收敛指标等定量数据。

---

## 【表格解读】

**原文无表格。** 文档未给出任何参数表、性能对比表或配置项表；模型信息仅以列表+图片形式呈现。

---

## 【公式解读】

**原文无公式。** 文档未出现 LaTeX 公式或伪代码公式；mask 的具体形态仅以图片（`encoder_mask.png`、`decoder_mask.png`、`encoder_decoder_mask.png`）形式给出，未在文本中以矩阵或表达式描述。

---

## 【关联】

文档内部链接仅有外链形式（指向 GitHub 示例仓库与微软 UniLM 论文），**文末未提供仓库内部的其他 tutorial 内部链接**。其与同目录下其他文档的关联可从内容推断：

- 与 **TUTORIAL 系列**的关系：本篇是第 9 篇，专讲 seq2seq；上游应有模型加载/基础训练相关教程（如基础分类、预训练），下游通常对应推理部署、微调最佳实践等教程（原文未显式给出链接）。
- 与 **`examples/` 目录**的关系：文档把 RoBERTa/GLM/T5 的标题生成示例都指向 `examples/<model>_title_generation`，把 GPT-2 中文续写指向 `quickstart/writing_ch.py`，是用户从文档跳转到可运行代码的入口。
- 与 **UniLM 的关系**：encoder 范式所依赖的"特殊 attention mask"思想直接引用自微软 UniLM（https://github.com/microsoft/unilm），可视为该方法的理论依据。
- 与 **FlagAI 模型库**的关系：所列 Bert、RoBERTa、GLM、GPT-2、T5 均为 FlagAI 内置/支持的基础模型族。

---

## 【使用方法】

**原文未涉及**具体的启用命令、配置项参数或脚本调用方式。文档仅以**外链示例**形式引导用户上手：

| 范式 | 代表模型 | 推荐示例（原文链接） |
|---|---|---|
| Encoder-only | RoBERTa | https://github.com/FlagAI-Open/FlagAI/tree/master/examples/roberta_title_generation |
| Encoder-only | GLM | https://github.com/FlagAI-Open/FlagAI/tree/master/examples/glm_title_generation |
| Decoder-only | GPT-2（中文） | https://github.com/FlagAI-Open/FlagAI/blob/master/quickstart/writing_ch.py |
| Encoder-Decoder | T5 | https://github.com/FlagAI-Open/FlagAI/tree/master/examples/t5_title_generation |

具体的训练启动命令、超参、数据格式、checkpoint 配置等细节，文档要求读者跳转至上述示例仓库自行查阅，原文未做展开。
