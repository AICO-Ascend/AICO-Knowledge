# Seq2seq Method

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_9_SEQ2SEQ_METHOD.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_9_SEQ2SEQ_METHOD.md

```markdown
# Seq2seq Method 文档深度解读

## 【定位】
这篇文档概述 FlagAI 框架在序列到序列 (seq2seq) 文本生成任务上所支持的 **三种模型范式**：仅编码器、仅解码器、编码器-解码器，并以示例链接和注意力掩码示意图说明各自的工作机制。

---

## 【技术要点】

1. **三种范式并行支持**（原文 1-3 项列举）：encoder-only / decoder-only / encoder-decoder 三类 seq2seq 生成方案。
2. **Encoder-only 范式**：以 Bert、RoBERTa、GLM 等为代表；在训练时引入 **special attention mask**（参考微软 UniLM 思路），输入格式为 `[cls] sentence_1 [sep] sentence_2 [sep]`，其中 sentence_1 不加掩码、sentence_2 使用 autoregressive mask。
3. **Decoder-only 范式**：以 GPT-2 为代表；典型场景为给定 start text 后做文本续写 (continuation)。
4. **Encoder-Decoder 范式**：以 T5 为代表；encoder 仅编码一次得到特征，decoder 结合 self-attention 与 encoder 特征继续生成。
5. **对应示例入口**（外部链接，原文给出）：
   - RoBERTa 标题生成：`examples/roberta_title_generation`
   - GLM 标题生成：`examples/glm_title_generation`
   - GPT-2 文本生成：`quickstart/writing_ch.py`
   - T5 标题生成：`examples/t5_title_generation`
6. **三种注意力掩码可视化**：`./img/encoder_mask.png`、`./img/decoder_mask.png`、`./img/encoder_decoder_mask.png` 分别对应三种范式。

---

## 【关键机制与数据】

**原文工作原理 / 数据流：**

- **Encoder 模型数据流**：输入为两段拼接句子 → 形式为 `[cls] sentence_1 [sep] sentence_2 [sep]` → sentence_1 **不使用 mask**（即全可见，对应双向上下文编码）→ sentence_2 使用 **autoregressive mask**（即下三角掩码，保证当前位置只能看到自身及左侧 token）→ 这种非对称 mask 让一个 encoder 同时具备双向理解 (sentence_1) 和单向生成 (sentence_2) 的能力，对应微软 **UniLM**（原文链接 `https://github.com/microsoft/unilm`）的设计思路。
- **Decoder 模型数据流**：以 start text 作为 prompt 输入 → 解码器自回归生成续写内容 → 配套掩码示意图 `./img/decoder_mask.png`，体现标准 causal mask。
- **Encoder-Decoder 模型数据流**：encoder 对输入一次性编码得到特征 → decoder 依据自身自回归输入 + encoder 提供的特征 持续生成 → 配套掩码示意图 `./img/encoder_decoder_mask.png`，体现 cross-attention 与 self-attention 的联合结构。

**原文无性能数据、benchmark 数字或训练超参。**

---

## 【表格解读】

**原文无表格。**（文档以项目符号列表 + 示意图为主，未出现任何 markdown 或纯文本表格。）

---

## 【公式解读】

**原文无公式。**（文档描述层面的工作原理均为自然语言说明，未给出 LaTeX 数学公式或伪代码表达式。）

---

## 【关联】

- **上游方法参考**：encoder-only 范式 special attention mask 的实现思路来自 **`https://github.com/microsoft/unilm`**（原文显式链接），即 UniLM 系列将 mask 矩阵改造后使单一 encoder 模型可同时服务于 NLU 与 NLG 的做法。
- **下游示例模块**（均跳转至 FlagAI 仓库）：
  - `examples/roberta_title_generation` —— 对应 Encoder 模型 + 标题生成场景。
  - `examples/glm_title_generation` —— 对应 GLM 的 Encoder/Decoder 风格 + 标题生成场景。
  - `quickstart/writing_ch.py` —— 对应 Decoder 模型 + 中文文本续写场景。
  - `examples/t5_title_generation` —— 对应 Encoder-Decoder 模型 + 标题生成场景。
- **资源文件**：图片资源位于同级 `docs/img/` 目录 (`encoder_mask.png`、`decoder_mask.png`、`encoder_decoder_mask.png`)，与正文三种范式一一对应。
- **内部链接**：本文末尾为 `(无)`，所有 URL 均指向 FlagAI 主仓库或外部 UniLM 仓库，未携带文档内交叉引用。

---

## 【使用方法】

**原文未给出直接的配置项/命令行**，仅提供示例入口：

- 运行 RoBERTa 标题生成：参考 `https://github.com/FlagAI-Open/FlagAI/tree/master/examples/roberta_title_generation`
- 运行 GLM 标题生成：参考 `https://github.com/FlagAI-Open/FlagAI/tree/master/examples/glm_title_generation`
- 运行 GPT-2 中文写作：`https://github.com/FlagAI-Open/FlagAI/blob/master/quickstart/writing_ch.py`
- 运行 T5 标题生成：参考 `https://github.com/FlagAI-Open/FlagAI/tree/master/examples/t5_title_generation`

具体的训练启动命令、超参数与配置文件，需进入上述示例目录查看（本文档未涉及）。
```
