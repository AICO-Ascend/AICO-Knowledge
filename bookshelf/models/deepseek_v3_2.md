> 来源：InfraTech 开源项目 models/deepseek_v3_2 模型结构解析 · 本库本地化收纳（文本+图片）

---

# DeepSeek V3.2模型介绍

DeepSeek V3.2是一款大语言模型，其关键特点是：V3.2-Exp在V3.1-Terminus的基础上引入了DeepSeek Sparse Attention（DSA），显著降低了计算复杂度。
该系列首先推出了V3.2Exp（实验版本），随后推出了正式版本V3.2和V3.2-Speciale。

效果：DeepSeek-V3.2-Speciale超越了GPT-5，并表现出与Gemini-3.0-Pro相当的推理能力。

性能：在保持几乎相同的模型输出质量的同时，大幅提高了长上下文训练和推理效率。

架构特点：
- Attention 模块：
  - DSA：在MLA的基础上增加了Indexer模块，用于控制KV值中参与计算的tokens数量。
  - Decode阶段，tokens数量限定在2k以内，因此MLA的计算量与context长度无关。
  - 支持上下文长度：128K。


## 整体架构

<p style="text-align: center;">
  <img src="deepseek_v3_2/deepseek_v3_2_architecture.jpg" alt="DeepSeek V3.2架构图" />
</p>

## DSA模块介绍

DSA基于MLA(Multi-Head Latent Attention)的改进，让Q(query)的每个token与最相关的K/V(key/value)值进行注意力机制运算，
其目的是降低原MLA的计算量，同时保证模型效果接近。

稀疏计算的实现模块：
- **Lightning Indexer** : 计算出每个Q值与历史的所有K/V值的关联关系(相关性)，得到一个分数排序；
- **Top-k Selector**: 选出分数最高的k个K/V进行注意力计算，实现稀疏Attention。

DSA详细介绍：
[DSA原理解析（https://zhuanlan.zhihu.com/p/1962162900111172920)
[超细图解DSA计算流&性能对比与优化分析（https://zhuanlan.zhihu.com/p/1963371483985319543)

### MQA模式
<p style="text-align: center;">
  <img src="deepseek_v3_2/DSA_MQA.jpg" alt="DeepSeek V3.2（MQA）架构图" />
</p>

### MHA模式
<p style="text-align: center;">
  <img src="deepseek_v3_2/DSA_MHA.jpg" alt="DeepSeek V3.2（MHA）架构图" />
</p>

## 相关资料：
- [整体介绍（官方博客）（https://github.com/deepseek-ai/DeepSeek-V3.2-Exp/blob/main/DeepSeek_V3_2.pdf)
- [模型配置文件（https://huggingface.co/deepseek-ai/DeepSeek-V3.2/blob/main/config.json)
- [模型定义示例（https://huggingface.co/deepseek-ai/DeepSeek-V3.2/tree/main/inference)
