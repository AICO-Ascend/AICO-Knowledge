> 来源：CalvinXKY/InfraTech · [models/qwen3_vl](https://github.com/CalvinXKY/InfraTech/tree/master/models/qwen3_vl)（总体模型结构解析，本库收纳拷贝；图片走原仓 raw 链接）

---

# Qwen3-VL模型简介

Qwen3-VL是Qwen系列新一代视觉-语言模型，面向图文理解、视频理解、多模态推理与智能体交互等场景。  
官方形态同时覆盖Dense与MoE，并提供Instruct/Thinking等版本，支持从边缘端到云端的灵活部署。

整体特点：
- 架构侧更新：Interleaved-MRoPE、DeepStack、多级视觉特征融合与文本-时间戳对齐能力；
- 能力全面升级：文本理解与生成、视觉感知与推理、空间理解、视频时序建模与Agent交互能力同步增强；
- 长上下文与长视频理解：原生支持256K上下文，可扩展到1M，适配长文档与小时级视频分析；
- 视觉智能体能力：可识别GUI元素、理解界面功能，并结合工具调用完成复杂任务；
- OCR能力增强：支持更多语言，对低光、模糊、倾斜与复杂排版场景更稳健；
- 文本-视觉深度融合：在纯文本任务保持较强性能，同时具备统一的多模态理解能力。


## 整体架构

### Dense结构：Qwen3-VL-32B-Instruct

<p align="center">
  <img src="https://raw.githubusercontent.com/CalvinXKY/InfraTech/master/models/qwen3_vl/qwen_3_vl_32b_architecture.jpg" alt="Qwen3-VL-32B架构图" />
</p>

#### 模型结构描述：

- 类型：视觉-语言指令模型（Instruct）
- 架构：`Qwen3VLForConditionalGeneration`
- 模型类型：`qwen3_vl`
- 参数规模：32B（以模型命名为准）
- 文本上下文长度：262144
- 文本层数：64
- 文本隐藏维度：5120
- 文本FFN中间层维度：25600
- 文本注意力头数：Q=64，KV=8，head_dim=128
- 文本词表大小：151936
- RoPE参数：`rope_theta=5000000`，`mrope_section=[24,20,20]`
- 视觉编码器层数：27
- 视觉隐藏维度：1152
- 视觉头数：16
- 视觉FFN中间层维度：4304
- 图像Patch大小：16，时序Patch大小：2
- 视觉输出映射维度：5120（与文本隐藏维度对齐）

### MoE结构：Qwen3-VL-235B-A22B-Instruct

<p align="center">
  <img src="https://raw.githubusercontent.com/CalvinXKY/InfraTech/master/models/qwen3_vl/qwen_3_vl_235b_a22b_architecture.jpg" alt="Qwen3-VL-235B-A22B架构图" />
</p>

#### 模型结构描述：

- 类型：视觉-语言指令模型（Instruct）
- 架构：`Qwen3VLMoeForConditionalGeneration`
- 模型类型：`qwen3_vl_moe`
- 参数规模：235B，激活参数22B（以模型命名为准）
- 文本上下文长度：262144
- 文本层数：94
- 文本隐藏维度：4096
- 文本FFN中间层维度：12288
- 文本注意力头数：Q=64，KV=4，head_dim=128
- 文本词表大小：151936
- RoPE参数：`rope_theta=5000000`，`mrope_section=[24,20,20]`
- MoE配置：专家总数128，每token激活专家数8，`moe_intermediate_size=1536`
- 视觉编码器层数：27
- 视觉隐藏维度：1152
- 视觉头数：16
- 视觉FFN中间层维度：4304
- 图像Patch大小：16，时序Patch大小：2
- 视觉输出映射维度：4096（与文本隐藏维度对齐）


#### 相关资料：

- [Qwen3-VL-32B-Instruct配置文件](https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct/blob/main/config.json)
- [Qwen3-VL-235B-A22B-Instruct配置文件](https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Instruct/blob/main/config.json)
- [模型实现Dense](https://github.com/huggingface/transformers/blob/main/src/transformers/models/qwen3_vl/)
- [模型实现MoE](https://github.com/huggingface/transformers/tree/main/src/transformers/models/qwen3_vl_moe/)
- [Qwen3-VL Technical Report](https://arxiv.org/pdf/2511.21631)
- [DeepStack论文](https://arxiv.org/pdf/2406.04334)