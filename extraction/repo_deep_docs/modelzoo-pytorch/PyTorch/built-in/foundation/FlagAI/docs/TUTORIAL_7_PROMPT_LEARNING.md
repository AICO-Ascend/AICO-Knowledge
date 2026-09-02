# Introduction to Prompt Learning

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_7_PROMPT_LEARNING.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_7_PROMPT_LEARNING.md

# 《Introduction to Prompt Learning》一体化深度解读

## 【定位】
本文是 FlagAI 文档体系中的一篇**引导性教程**，面向自然语言处理场景下的**数据稀缺问题**，系统介绍 Prompt Learning（提示学习）这一范式的核心思想、两类主流提示工程方法（Cloze Prompts 与 Prefix Prompts）及其适用场景，作为后续实操的上游概念铺垫。

---

## 【技术要点】

1. **范式本质**：Prompt Learning 沿袭「预训练—微调」思路，但**不再为下游任务新增任务特定目标**，而是将每个原始任务**转换为特定的 prompting function**（该过程被称为 prompt engineering）。
2. **两大方法分支**：Prompt Engineering 主要包含 **cloze prompts**（完形填空式提示）与 **prefix prompts**（前缀提示）两类；前者更适用于**使用 masked LM 的下游任务**，后者一般用于**文本生成任务**。
3. **Cloze Prompts 构造流程**（两步）：
   - 步骤 1：**应用模板（template）**，包含输入槽（input slot）、答案槽（answer slot）以及用户自定义的自然语言文本；
   - 步骤 2：**应用 verbalizer**，将原始标签（label）映射到答案槽所用的具体答案词。
4. **Cloze 示例结构**：原始数据集含两条输入文本 *premise*（前提）与 *hypothesis*（假设），label 表示两者关系，对应三种可能的文本字符串——**entailment（蕴涵）、contradiction（矛盾）、neutral（中立）**；再围绕这一结构设计有意义的 cloze 模板。
5. **Prefix Prompts 机制**：**不再用真实自然语言**设计提示，而是**直接在嵌入空间中插入一段任务特定的向量序列**，同时**冻结 LM 参数**；其优势在于模板的嵌入表达**不再受限于预训练 LM 内部参数**所代表的语言表面形式。
6. **Prefix-tuning 与 fine-tuning 的对比视角**：在 Transformer 嵌入空间中，prefix tuning 期间 Transformer 的**灰色部分被冻结**，仅保留前缀向量参与更新，从而显著降低可训练参数量（原文以图示方式说明）。

---

## 【关键机制与数据】

- **数据形态（原文）：** Cloze 示例中每个样本包含两条输入文本 *premise* 与 *hypothesis*，以及一个取自三类（entailment / contradiction / neutral）的标签，最终由 template + verbalizer 重排为 cloze-style phrase。
- **Prefix Prompts 工作流（原文）：** 在 Transformer 的 embedding 空间中**插入任务特定的向量前缀** → **冻结 LM 主体参数** → 仅优化前缀向量；模板嵌入从此**摆脱预训练 LM 已有参数对自然语言表面形式的约束**。
- **性能数据**：原文未提供任何数值指标、训练曲线或对比基准，文中也未给出具体超参（如学习率、batch size、prefix length 等）。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文作为 Prompt Learning 的**概念入门篇**，与仓内其他 FlagAI 模块的耦合较弱；其外延主要依赖文末三篇 arXiv 参考文献提供学术溯源：

- **Liu, P. (2021)** "Pre-train, Prompt, and Predict: A Systematic Survey of Prompting"（arXiv:2107.13586）—— Prompt Learning 范式系统性综述，为本文整体思路的总源头。
- **Ding, N. (2021)** "OpenPrompt: An Open-source Framework for Prompt-learning"（arXiv:2111.01998）—— 开源 Prompt Learning 框架，与本文 cloze/prefix 方法的实际落地工具链紧密相关。
- **Schick, T. (2020)** "Exploiting Cloze Questions for Few Shot Text Classification and …"（arXiv:2001.07676）—— Cloze 完形填空提示用于小样本文本分类的方法学基础，对应本文 Cloze Prompts 一节。
- **Li, X. L. (2021)** "Prefix-Tuning: Optimizing Continuous Prompts for Generation"（arXiv:2101.00190）—— Prefix-Tuning 的原始论文，对应本文 Prefix Prompts 一节。

仓内未给出内部上下游模块的链接关系，故模块级依赖信息缺失。

---

## 【使用方法】

本文为教程性概念文档，**未涉及具体的启用命令、配置项或超参**；其作用是为 FlagAI 中可能涉及的 Prompt Learning 相关模块（如基于 FlagAI 大模型的下游任务适配）提供前置认知铺垫。如需进入实操，请进一步参考仓内具体模型/任务的训练与推理指南（原文档未涉及）。
