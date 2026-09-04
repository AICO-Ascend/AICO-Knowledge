> 本页由 model-arch 技能从 HuggingFace `deepseek-ai/DeepSeek-R1` 的 config.json 实时解析生成（非人工绘制）；可交互版结构图：[deepseek_r1/deepseek_r1_arch.html](deepseek_r1/deepseek_r1_arch.html)（自包含单文件，浏览器打开）

---

# DeepSeek R1 架构简介

DeepSeek R1 架构分析（由 model-arch skill 从HuggingFace `deepseek-ai/DeepSeek-R1`实时抓取 `config.json` 与 modeling 代码自动生成）。模型族：**deepseek_v3**，model_type `deepseek_v3`。

## 整体架构

<p style="text-align: center;">
  <img src="deepseek_r1/deepseek_r1_arch.png" alt="DeepSeek R1架构图" />
</p>

## 模块说明

主要参数如下（来源：HuggingFace `deepseek-ai/DeepSeek-R1`的 `config.json` 与 modeling 代码）：

| 指标 | 值 |
|---|---|
| 架构族 | deepseek_v3 |
| model_type | deepseek_v3 |
| 总参数（估算） | ≈671B |
| 层数 | 61 |
| 隐藏维度 | 7168 |
| 注意力头数 | 128 |
| KV 头数 | 128 |
| head_dim | 56 |
| 词表大小 | 129280 |
| 上下文长度 | 163840 |
| 稠密 MLP 隐层 | 18432 |
| 归一化 | RMSNorm |
| RoPE θ | 10000 |
| tie embeddings | ✗ |
| 注意力机制 | MLA |
| MLA q_lora_rank | 1536 |
| MLA kv_lora_rank | 512 |
| qk_nope / rope / v head_dim | 128 / 64 / 128 |
| FFN/激活 | SiLU-GLU |
| MTP 层数 | 1 |
| MoE 专家数 | 256 |
| 每 token 激活专家 | 8 |
| 共享专家 | 1 |
| MoE 每专家隐层 | 2048 |
| 路由激活/归一 | None / True |
| 路由 topk 法 | noaux_tc |
| block 堆栈 | 3×MLA + 58×MLA-MoE |

### 语言模块

语言主干：**61 层**，block 堆栈 `3×MLA + 58×MLA-MoE`。注意力 MLA（q_lora=1536, kv_lora=512），FFN SiLU-GLU。MoE：256 专家 / 每 token 激活 8 / 1 共享专家。 MTP 1 层。

代码级佐证（modeling 文件中的实现类）：MoE_gate: MoEGate。

### 视觉模块

（本模型为纯文本模型，无视觉模块。）

## 相关资料

- [模型卡片与权重（Hugging Face）](https://huggingface.co/deepseek-ai/DeepSeek-R1)
- 本报告由 [model-arch skill](.) 自动生成，数值取自 `config.json` 真实字段，缺失项标「—」。
