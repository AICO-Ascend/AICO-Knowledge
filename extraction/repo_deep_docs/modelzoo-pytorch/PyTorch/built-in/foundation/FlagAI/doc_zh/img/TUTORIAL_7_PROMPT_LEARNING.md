# Introduction to Prompt Learning

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/img/TUTORIAL_7_PROMPT_LEARNING.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/img/TUTORIAL_7_PROMPT_LEARNING.md

# 深度解读：Introduction to Prompt Learning

## 【定位】
本文档系统介绍了 NLP 领域中提示学习（Prompt Learning）范式的基本概念与核心方法（完形填空提示与前缀提示），解决"在数据有限场景下，如何通过提示工程将下游任务转化为预训练语言模型擅长的形式，避免传统微调对人工模板设计的过度依赖"这一核心问题。

---

## 【技术要点】

1. **范式定位**：提示学习遵循"预训练-微调"思想，但区别于传统微调——它通过**提示工程**将下游任务转化为特定模板，使预训练好的语言模型直接适配多种任务。

2. **两大提示工程方法**：
   - **完形填空提示（Cloze Prompts）**：更适合**遮挡类语言模型（Masked LM）**的下游任务；
   - **前缀提示（Prefix Prompts）**：通常用于**文本生成任务**。

3. **完形填空提示的两步构建流程**：
   - 步骤一：构建由"输入部分 + 答案部分 + 自然语言"组成的模板；
   - 步骤二：构建从**原始标签到可填选项的对应关系（即 Verbalizer）**。

4. **Verbalizer 的实现形式**：本质上是标签到选项的映射关系，使用 Python 字典定义，示例代码中定义了三个标签的映射（contradiction→false、entailment→true、neutral→neither）。

5. **前缀提示的核心思想**：**不依赖真实自然语言模板**，而是通过在 Transformer 中**插入可训练的前缀向量**并**冻结语言模型其余参数**，将离散 token 转化为连续向量，从而规避人工模板质量对模型性能的影响。

6. **数据-标签组合示例**：以 NLI 任务为例，原始数据集包含两个输入文本（前提 premise + 假设 hypothesis），标签为三种字符串（entailment、contradiction、neutral），通过模板与 Verbalizer 转换为完形填空形式。

---

## 【关键机制与数据】

**原文：完形填空提示模板结构**

模板由四段依次拼接组成：
```
[example.text_a] + " question: is it true, false or neither that" + [example.text_b] + " answer:" + [mask token]
```
即"前提 + 自然语言提问 + 假设 + 自然语言引导词 + 空格待填"，最终 `[mask]` 位置由语言模型从 Verbalizer 提供的三个候选词中选择填充。

**原文：Verbalizer 字典定义**

```python
VERBALIZER = {
    "contradiction": [" false"],
    "entailment": [" true"],
    "neutral": [" neither"]
}
```
- 键（key）：原始任务标签（布尔/整数/字符串等多种类型，NLI 任务中为字符串）；
- 值（value）：完形填空空格处可填入的候选词列表；
- 调用方式：`verbalize(label) → VERBALIZER[label]`，返回对应候选词列表。

**原文：前缀提示的工作原理**

- **插入位置**：在 Transformer 中插入前缀向量（prefix vectors）；
- **参数策略**：**冻结语言模型的其余参数**，仅前缀向量参与训练/适配；
- **核心优势**：从离散的 token 转为连续的嵌入空间向量，避免人工设计模板的质量好坏对模型性能影响过大。

---

## 【表格解读】

**原文无表格**

（文档中所有信息均以文字描述、示意图引用和 Python 代码片段形式呈现，未包含任何 markdown 表格。）

---

## 【公式解读】

**原文无公式**

（文档属于概念性介绍，涉及的"模板拼接"和"字典映射"逻辑均通过 Python 代码而非数学公式表达，未出现 LaTeX 或伪代码形式的公式定义。）

---

## 【关联】

**原文无内部链接**（文档文末标注"(无)"）。

不过从文档描述可推断的模块/上下游关联如下：

- **上游范式**：传统"预训练-微调（pre-train + fine-tuning）"范式，提示学习是其变体；
- **适配模型类型**：
  - 完形填空提示 → 对接**遮挡类语言模型（Masked LM）**的下游任务；
  - 前缀提示 → 对接**文本生成（text generation）**类任务；
- **相关工具/框架**：文中参考论文指向 **OpenPrompt**（开源 Prompt-learning 框架），可作为本文档方法论的工程化实现参考；
- **关联下游任务示例**：文档以 NLI（自然语言推理）任务为典型案例，涉及前提-假设-关系标签三元组结构，可拓展到文本分类等同类完形填空任务。

---

## 【使用方法】

**原文未涉及**

（本文档定位为概念介绍与原理讲解，未提供具体的命令行启用方式、配置文件示例或可执行参数说明。所有"实现"层面的内容仅通过简化版 Python 函数片段（`get_parts` 与 `verbalize`）示意方法论，未涉及 FlagAI 仓库中 prompt learning 模块的实际调用命令、环境变量、训练超参或模型路径配置。）
