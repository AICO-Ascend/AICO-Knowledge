# Parallel Draft Models

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/parallel_draft_model.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/parallel_draft_model.md

# 深度解读：Parallel Draft Models (PARD)

## 【定位】
这篇文档解决在 vLLM 中启用 **PARD (Parallel Draft Models) 投机解码** 的配置问题，给出**离线推理**与**在线服务**两种使用范式的可直接复制示例。

---

## 【技术要点】
- **投机解码方法选用**：使用 PARD（Parallel Draft Models，论文 arXiv:2504.18583）作为草案生成器，目标模型与草案模型并行工作以加速推理。
- **目标 / 草案模型组合**：离线示例中目标模型为 `Qwen/Qwen3-8B`，草案模型为 `amd/PARD-Qwen3-0.6B`；在线示例中目标模型为 `Qwen/Qwen3-4B`。
- **关键触发开关**：`speculative_config` 中需设置 `parallel_drafting: True`，并以 `"method": "draft_model"` 模式驱动草案模型生成提议。
- **每次推测步数**：`num_speculative_tokens = 12`，即每轮投机解码生成 12 个候选 token。
- **采样参数**：离线示例使用 `temperature=0.8, top_p=0.95`。
- **在线服务参数**：`vllm serve` 配合 `-tp 1`、`--max-model-len 2048`、`--gpu-memory-utilization 0.8`、`--seed 42` 等部署相关参数。

---

## 【关键机制与数据】
- **工作原理**：vLLM 在标准投机解码框架下，将 PARD 作为草案模型加载，由它在每一步**并行地**生成一组候选 token（而不是传统自回归草案模型顺序生成），从而减少草案阶段的串行开销。
- **数据流**：
  - 离线：`LLM(...)` 构造时把 `speculative_config` 字典传入 → `llm.generate(prompts, sampling_params)` 触发生成 → 逐 `output` 打印 `prompt` 与 `outputs[0].text`。
  - 在线：`vllm serve` 把同一 `speculative-config` JSON 字符串作为 CLI 参数注入，启动 OpenAI 兼容服务。
- **性能数据**：原文未提供任何吞吐量、加速比或接受率等量化指标。

---

## 【表格解读】
**原文无表格**

---

## 【公式解读】
**原文无公式**

---

## 【关联】
- **上游文档关联**：本文属于 `docs/features/speculative_decoding/` 路径下的子文档，与 vLLM 的 **Speculative Decoding（投机解码）特性** 同属一套加速方案，但本篇聚焦于 PARD 这一具体的并行草案实现。
- **下游关联**：
  - 依赖 HF 上的预训练权重集合 `amd/pard`（https://huggingface.co/collections/amd/pard），用户需从中选取与目标模型匹配的 PARD 草案模型。
  - 依赖 PARD 论文（https://arxiv.org/pdf/2504.18583）所描述的并行草案算法。
- **内部链接**：原文文末未提供任何站内部链接（标注为「(无)」）。

---

## 【使用方法】

### 1. 离线推理 (Python)
通过 `LLM` 构造时传入 `speculative_config` 字典，核心字段如下（原文代码逐字保留）：
```python
llm = LLM(
    model="Qwen/Qwen3-8B",
    tensor_parallel_size=1,
    speculative_config={
        "model": "amd/PARD-Qwen3-0.6B",
        "num_speculative_tokens": 12,
        "method": "draft_model",
        "parallel_drafting": True,
    },
)
```

### 2. 在线服务 (CLI)
通过 `vllm serve` 启动 HTTP 服务，将同一组投机解码配置以 JSON 字符串形式注入 `--speculative-config`：
```bash
vllm serve Qwen/Qwen3-4B \
    --host 0.0.0.0 \
    --port 8000 \
    --seed 42 \
    -tp 1 \
    --max-model-len 2048 \
    --gpu-memory-utilization 0.8 \
    --speculative-config '{"model": "amd/PARD-Qwen3-0.6B", "num_speculative_tokens": 12, "method": "draft_model", "parallel_drafting": true}'
```

### 3. 启用条件
- 需在 HuggingFace 集合 **amd/pard** 中存在与目标模型相匹配的 PARD 预训练权重。
- 必须显式打开 `parallel_drafting: True`，否则不会以 PARD 模式运行。
