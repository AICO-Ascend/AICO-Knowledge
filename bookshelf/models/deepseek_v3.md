> 来源：CalvinXKY/InfraTech · [models/deepseek_v3](https://github.com/CalvinXKY/InfraTech/tree/master/models/deepseek_v3)（总体模型结构解析，本库收纳拷贝；图片走原仓 raw 链接）

---

# DeepSeek V3模型简介

DeepSeek V3是一款采用MoE架构的大语言模型（LLM），核心注意力机制使用自研的MLA（Multi-head Latent Attention）。
模型总参数约671B，推理时每个token激活约37B参数，兼顾模型容量与在线推理效率。
相较于传统Transformer实现，DeepSeek V3通过MLA与MoE组合，在长上下文建模、推理效率和训练成本之间取得了更好的平衡。

效果：在通用能力、代码能力和数学推理等公开评测中，DeepSeek V3表现出较强竞争力，接近或超过同代高性能开源模型。

性能：通过注意力与专家计算路径优化，在保持模型能力的同时降低了推理开销，更适合大规模在线服务场景；支持长上下文输入，适用于复杂文档与多轮任务。

架构特点：
- 采用MoE架构，按需激活专家网络，提升参数利用率
- 注意力模块使用MLA，减少KV缓存占用并优化长序列推理
- 结合共享与路由专家机制，平衡模型表达能力与部署成本
- 训练阶段使用大规模高质量语料，累计训练token约14.8T
- 面向训练和推理做了系统级优化，增强吞吐与稳定性

## 整体架构

<p style="text-align: center;">
  <img src="https://raw.githubusercontent.com/CalvinXKY/InfraTech/master/models/deepseek_v3/deepseek_v3_architecture.jpg" alt="DeepSeek V3架构图" />
</p>

整体架构由Embedding、MLA注意力层、MoE前馈层和输出层构成。其关键设计在于将高效注意力计算与稀疏专家计算结合：前者侧重降低长上下文阶段的显存与计算压力，后者侧重在可控开销下提升模型容量与表达能力。
从工程视角看，DeepSeek V3的架构特点主要体现在三点：其一，MLA降低了KV缓存占用并改善长序列推理成本；其二，MoE按token路由激活少量专家，显著提升计算利用率；其三，训练与服务链路协同优化，支持大规模部署下的稳定吞吐。

## MLA模块

MLA模块有两种计算模式，MHA模式在prefill阶段使用，MQA模式在decode阶段使用。

### MHA模式

<p style="text-align: center;">
  <img src="https://raw.githubusercontent.com/CalvinXKY/InfraTech/master/models/deepseek_v3/MLA_MHA.jpg" alt="MLA_MHA架构图" />
</p>

### MQA模式

<p style="text-align: center;">
  <img src="https://raw.githubusercontent.com/CalvinXKY/InfraTech/master/models/deepseek_v3/MLA_MQA.jpg" alt="MLA_MQA架构图" />
</p>

两种模式的差异对比参考： **[《超细图解MLA计算流&吸收矩阵对比分析》](https://zhuanlan.zhihu.com/p/1948769945132470860)**

## 相关资料：
- [DeepSeek V3论文（技术报告）](https://arxiv.org/pdf/2412.19437)
- [整体介绍（官方仓库）](https://github.com/deepseek-ai/DeepSeek-V3)
- [模型配置文件](https://huggingface.co/deepseek-ai/DeepSeek-V3/blob/main/config.json)
- [Transformer模型定义](https://github.com/huggingface/transformers/tree/main/src/transformers/models/deepseek_v3)
