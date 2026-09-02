# Context Extension

> 仓 `vllm` · 路径 `docs/features/context_extension.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/context_extension.md

# 上下文扩展 (Context Extension) 文档深度解读

## 【定位】
本篇文档回答「如何在 vLLM 中将预训练模型的上下文窗口从原始长度外推到更长长度（如把 32K 扩展到 128K）」这一问题，给出基于 RoPE 参数重写（YARN 等插值/外推方法）的离线推理示例与 OpenAI 兼容在线服务两种使用路径，并明确旧版 `--rope-scaling` 参数已弃用的迁移方案。

---

## 【技术要点】

1. **旧参数弃用与迁移路径**：原先用于上下文扩展的 `--rope-scaling` 参数在新版 vLLM 中**已不再支持**，必须改用 `--hf-overrides` 配合 `rope_parameters` JSON 字段来声明 RoPE 配置。
2. **离线推理示例脚本**：仓库提供 `examples/features/context_extension/context_extension_offline.py`，使用 **YARN** 方法对 **Qwen 系列模型**（示例为 Qwen3-0.6B）做上下文扩展并跑一段简单 chat。
3. **在线服务调用方式**：通过 `vllm serve` 命令加载扩展后的模型，外部用 OpenAI Python SDK（兼容 OpenAI API 协议）以 `base_url=http://localhost:8000/v1` 发起 `chat.completions.create` 请求；其中 `api_key="token-abc123"` 为占位 dummy key（满足客户端必填校验，并非真实鉴权）。
4. **核心 RoPE 参数四件套**：示例命令同时给出 `factor=4.0`、`original_max_position_embeddings=32768`、`rope_theta=1000000`、`rope_type="yarn"`，将基座模型的 32K 上下文按 4 倍比例外推到 131072。
5. **`max_model_len` 的语义**：设为扩展后的新上限 `131072`（即 32768 × 4），**同时承担 KV cache 预分配容量**与**服务期单请求长度上限**两个职责。
6. **`rope_type` 多样性**：除 YARN 外，原文指出还支持 `linear`、`dynamic` 等 RoPE 实现类型，具体可用参数需参考 Hugging Face Transformers 的 `RopeParameters` 文档。

---

## 【关键机制与数据】

**工作原理（按原文可还原的链路）**：
1. 启动 vLLM 时通过 `--hf-overrides` 把 JSON 形式的 `rope_parameters` 注入到 HuggingFace 模型配置层，等价于把 HF `RopeParameters` 直接喂给模型；
2. vLLM 根据 `rope_type=yarn` 选择 YARN 位置编码插值算法，并在内部用 `factor` 把 `original_max_position_embeddings`（32768）线性放大到目标长度；
3. `--max-model-len 131072` 决定 KV cache 一次性按 131072 个 token 预分配，并作为 serving 阶段单请求的最大序列长度硬约束；
4. 离线模式直接由 Python 脚本加载模型并推理；在线模式则通过 `vllm serve` 起 HTTP 服务，外部使用 OpenAI Python SDK 走 `/v1` 兼容接口。

**原文中的关键数字**：
- `factor = 4.0`（外推倍数）
- `original_max_position_embeddings = 32768`（模型原始上下文）
- `rope_theta = 1000000`（YARN 的 RoPE 基频参数）
- `max_model_len = 131072`（即 32768 × 4，新上限）
- `max_tokens = 128`（示例客户端单次生成上限）
- `temperature = 0.8`、`top_p = 0.95`（示例采样参数）
- `api_key = "token-abc123"`（dummy 鉴权占位）

**性能数据**：原文未提供任何吞吐量、延迟、显存占用或精度对比数据，因此本节不臆造。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式（无 LaTeX 公式，也未给出伪代码表达式）。

> 备注：尽管上下文扩展本质涉及 RoPE 位置编码的数学插值/外推（例如 `factor = new_max / original_max`），但**原文并未显式写出该公式**，因此严格按"原文有则写"原则，本节不补写。

---

## 【关联】

- **示例代码**：文档中链接到的 `examples/features/context_extension/context_extension_offline.py` 是离线模式下使用 YARN 扩展 Qwen 模型上下文并跑 chat 的可执行样例，是本特性最直接的代码参考。
- **RoPE 参数体系上游**：详细参数语义需跳转至 Hugging Face Transformers 的 [RopeParameters 文档](https://huggingface.co/docs/transformers/main/en/internal/rope_utils#transformers.RopeParameters) —— vLLM 这里 `rope_parameters` 的字段命名与取值直接对齐 HF，是 vLLM 与 HF 模型生态兼容的关键承接点。
- **OpenAI 兼容服务层**：在线方式借用了 vLLM 自带的 OpenAI 兼容 HTTP 服务（`/v1/chat/completions` 端点，默认监听 8000），属于 vLLM 在线推理服务生态的一部分。
- **替代关系**：旧版 `--rope-scaling` → 新版 `--hf-overrides rope_parameters`，这是一处显式的弃用/替换关系，迁移时需注意命令行参数形态改变。

---

## 【使用方法】

**离线模式（执行示例脚本）**：
```bash
python examples/features/context_extension/context_extension_offline.py
```
（脚本内部使用 YARN 方法扩展 Qwen 模型上下文并跑 chat；具体模型与参数需查看脚本实现，原文未在此处展开）

**在线模式（启动 vLLM 服务）**：
```bash
vllm serve Qwen/Qwen3-0.6B \
  --hf-overrides '{"rope_parameters": {"factor": 4.0, "original_max_position_embeddings": 32768, "rope_theta": 1000000, "rope_type": "yarn"}}' \
  --max-model-len 131072
```

**客户端调用示例（OpenAI Python SDK）**：
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-abc123"  # Dummy API key, required by the client
)

response = client.chat.completions.create(
    model="Qwen/Qwen3-0.6B",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}
    ],
    max_tokens=128,
    temperature=0.8,
    top_p=0.95
)

print(response.choices[0].message.content)
```

**关键配置项速查（原文覆盖范围）**：
- `--hf-overrides` 中 `rope_parameters` 的字段：`rope_type`（"yarn" / "linear" / "dynamic" 等）、`factor`、`original_max_position_embeddings`，YARN 还用到 `rope_theta`；完整字段以 HF Transformers RoPE 文档为准。
- `--max-model-len`：扩展后 KV cache 预分配与服务期请求长度上限，等价于 `original_max_position_embeddings × factor`。
