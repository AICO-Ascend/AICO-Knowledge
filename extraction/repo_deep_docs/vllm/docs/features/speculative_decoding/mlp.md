# MLP Draft Models

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/mlp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/mlp.md

# 深度解读: vLLM MLP Draft Models (MLP 投机解码草案模型)

---

## 【定位】

这篇文档描述 vLLM 中如何启用基于 MLP 的**草案模型 (MLP Drafter) 进行投机解码 (speculative decoding)**,其特点是草案预测同时以**上下文向量 (context vectors)** 和**已采样 token (sampled tokens)** 为条件,从而加速 LLM 推理。

---

## 【技术要点】

1. **方法标识**:通过 `speculative_config` 中的 `method="mlp_speculator"` 显式启用 MLP 投机器,与其它自回归式 draft 模型(如 n-gram、Medusa、 Eagle)区别开。
2. **草案-主模型配对**:主模型使用 `meta-llama/Meta-Llama-3.1-8B-Instruct`,草案模型使用 `ibm-ai-platform/llama3-8b-accelerator`,体现"同族 LLM + IBM 训练的小型 MLP 加速器"的成对组合模式。
3. **张量并行参数分离**:主模型 `tensor_parallel_size=1` 与草案模型 `draft_tensor_parallel_size=1` 是两个独立字段,允许二者采用不同的并行策略。
4. **双条件预测机制**:草案模型既依赖**上下文向量**(来自主模型 hidden states 的中间表示)又依赖**已采样 token**,这一点有别于仅依赖 token 的传统 n-gram 或仅依赖 hidden states 的 Medusa。
5. **采样参数示例**:原文示例采用 `temperature=0.8, top_p=0.95`,说明该方法支持随机采样场景下的投机解码(而非仅贪心)。
6. **已知缺陷**:`ibm-ai-platform/llama3-70b-accelerator` 在 vLLM 中会抛出 `AttributeError: 'MLPSpeculatorConfig' object has no attribute 'num_attention_heads'`,跟踪于 issue #34106 与 PR #34163。

---

## 【关键机制与数据】

**工作原理 (原文综合表述)**:
- vLLM 在推理时加载主 LLM(例如 `Meta-Llama-3.1-8B-Instruct`)作为验证模型;
- 同时加载一个轻量 MLP 草案模型(例如 `llama3-8b-accelerator`),后者接收主模型前向过程中的**上下文向量**与**先前已采样 token**,快速预测若干候选 token;
- 主模型一次性验证草案模型的多个预测 token,接受其中与主模型分布一致的子序列,从而减少自回归步数。

**性能数据**:原文**未给出**任何吞吐量、加速比、acceptance rate 等量化指标,仅提供代码示例与模型列表。

**外部参考**:
- PyTorch 博客 "The Hitchhiker's Guide to Speculative Decoding"(原文链接)
- IBM Research 技术报告 `arXiv:2404.19124`(原文链接)

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文末给出的内部链接信息为**无 (无)**。根据文档上下文,可推断的关联关系如下(均为文档**外部**指向,非 vllm 仓库内部链接):

- **同类特性对比**:vLLM 投机解码家族中其它草案方法(如 `n-gram`、`medusa`、`eagle` 等)通过不同 `method` 字段区分;MLP drafter 属于"非自回归式、需训练的小型神经网络草案模型"这一类。
- **依赖主模型隐状态**:因 MLP drafter 需要 context vectors,它在 vLLM 推理引擎中依赖主模型的 hidden state 暴露接口(具体实现未在本文展开)。
- **下游生态**:IBM 在 HuggingFace Hub 上发布了**9 个预训练 MLP 草案模型**,覆盖 Llama-2/3、Codellama、Granite 等多个系列,作为可直接搭配使用的"加速器"配对方案。
- **Bug 跟踪**:与上游 issue `#34106` 和 PR `#34163` 直接关联,涉及 `MLPSpeculatorConfig` 字段缺失问题。

---

## 【使用方法】

启用方式 (原文示例逐字摘录):

```python
from vllm import LLM, SamplingParams

prompts = ["The future of AI is"]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    tensor_parallel_size=1,
    speculative_config={
        "model": "ibm-ai-platform/llama3-8b-accelerator",
        "draft_tensor_parallel_size": 1,
        "method": "mlp_speculator",
    },
)
outputs = llm.generate(prompts, sampling_params)
```

关键配置项 (原文出现):

| 字段 | 值 | 含义 |
|---|---|---|
| `model` (LLM) | `meta-llama/Meta-Llama-3.1-8B-Instruct` | 主验证模型 |
| `tensor_parallel_size` | `1` | 主模型张量并行度 |
| `speculative_config.model` | `ibm-ai-platform/llama3-8b-accelerator` | 草案模型名称 |
| `speculative_config.draft_tensor_parallel_size` | `1` | 草案模型张量并行度 |
| `speculative_config.method` | `"mlp_speculator"` | 投机解码方法标识 |

**预训练 MLP 草案模型清单 (原文逐字)**:

- `ibm-ai-platform/llama-13b-accelerator`
- `ibm-ai-platform/llama3-8b-accelerator`
- `ibm-ai-platform/codellama-34b-accelerator`
- `ibm-ai-platform/llama2-70b-accelerator`
- `ibm-ai-platform/llama3-70b-accelerator` ⚠️ 已知缺陷
- `ibm-granite/granite-3b-code-instruct-accelerator`
- `ibm-granite/granite-8b-code-instruct-accelerator`
- `ibm-granite/granite-7b-instruct-accelerator`
- `ibm-granite/granite-20b-code-instruct-accelerator`

命令 / CLI 用法 / 其它配置项:**原文未涉及**。
