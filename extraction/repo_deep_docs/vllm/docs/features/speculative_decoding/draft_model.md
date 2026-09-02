# Draft Models

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/draft_model.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/draft_model.md

# 「Draft Models」深度解读

---

## 【定位】

本篇文档描述 vLLM 中**使用 draft model 进行投机解码（speculative decoding）的配置与调用方法**，覆盖离线 `LLM` 与在线 `vllm serve` 两种部署模式，并扩展介绍了允许 draft 与 target 模型使用不同 tokenizer 的**异构词表（heterogeneous vocab）**机制——Token-Level Intersection (TLI) 算法。

---

## 【技术要点】

1. **核心机制**：用一个小型 draft 模型先连续预测若干 token，再由大模型（target）一次性并行验证，从而加速自回归生成。
2. **离线模式入口**：在 `LLM(...)` 构造时通过 `speculative_config={...}` 字典注入投机解码参数，必须显式声明 `"method": "draft_model"`。
3. **在线模式入口**：`vllm serve` 时通过 `--speculative-config '<json>'` 一次性传入整个 JSON 配置串（原文两个示例均使用 `num_speculative_tokens=5`）。
4. **统一配置 schema**：文档明确指出旧的 `--speculative-model` + `--num-speculative-tokens` 拆分写法已 **deprecated**，必须全部参数合并到 `--speculative-config` 中，并指向 `README.md#--speculative-config-schema` 作为完整键值参考。
5. **异构词表支持**：`use_heterogeneous_vocab: true` 启用 TLI（Token-Level Intersection）算法，使 draft 与 target 可来自不同模型族 / 不同 tokenizer；原文示例使用 `Qwen/Qwen3-8B` + `HuggingFaceTB/SmolLM2-135M-Instruct` 这种"大 Qwen + 小 SmolLM" 的跨家族组合。
6. **当前限制**：原文明确"Currently, `use_heterogeneous_vocab` requires `draft_sample_method='greedy'` (the default). Probabilistic draft sampling is not yet supported"——即异构词表下只能用 greedy 采样，不支持概率采样。

---

## 【关键机制与数据】

- **工作原理（原文语义）**：draft 模型每次**"speculating 5 tokens at a time"**（一次性猜 5 个 token），随后由 target 模型并行验证；命中率越高，target 模型的实际前向次数越少，从而获得加速。
- **数据流**（原文隐含）：
  1. `prompts` → `LLM.generate(prompts, sampling_params)`
  2. 内部按 `speculative_config` 加载 draft model + 设置 `num_speculative_tokens`
  3. 每一步：draft 顺序生成 K 个候选 token → target 并行 verify → 接受前缀 + 补 1 个新 token
- **性能/参数数据**（原文出现，仅做摘录标注）：
  - **原文**：`num_speculative_tokens=5`（离线 Qwen3-8B + Qwen3-0.6B 示例 & 在线 Qwen3-4B-Thinking-2507 + Qwen3-0.6B 示例）
  - **原文**：在线示例 `--max-model-len 2048`、`--gpu-memory-utilization 0.8`、`--seed 42`、`-tp 1`
  - **原文**：异构词表示例 `num_speculative_tokens=3`、`gpu_memory_utilization=0.5`
  - **原文**：SamplingParams `temperature=0.8, top_p=0.95`
  - 原文未提供实测加速比（speedup）/ 接受率（acceptance rate）等性能数字。

---

## 【表格解读】

**原文无表格**。

整篇文档以 Python 代码块、bash 命令块和散文段落为主，未包含任何 markdown 表格或结构化对比表。

---

## 【公式解读】

**原文无公式**。

文档描述的是配置式使用方法，未出现任何 LaTeX 数学公式或伪代码形式的推导表达式。投机解码本身的接受率/期望加速比公式也未在本页给出。

---

## 【关联】

- **配置 schema 上游**：`README.md#--speculative-config-schema`（原文链接目标）—— 该 schema 列出 `--speculative-config` 所有支持的键（如 `model`、`num_speculative_tokens`、`method`、`use_heterogeneous_vocab`、`draft_sample_method` 等），是本篇文档示例 JSON 的完整字段来源。
- **关联模块**：本文属于 `docs/features/speculative_decoding/` 子目录，与同目录下的其他 speculative decoding 方法（如 Medusa、EAGLE、n-gram 等）并列；本篇特化于 `method="draft_model"` 这一支。
- **下游调用**：在线模式下客户端代码**保持 OpenAI 兼容协议不变**（原文强调"The code used to request completions as a client remains unchanged"），即通过 `client.completions.create(model=...)` 即可——投机解码对客户端透明。
- **废弃路径**：旧命令行入口 `--speculative-model` + `--num-speculative-tokens` 被本文 deprecate，所有相关参数必须统一迁移到 `--speculative-config`。

---

## 【使用方法】

### 1. 离线模式（Python `LLM`）
```python
from vllm import LLM, SamplingParams

prompts = ["The future of AI is"]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(
    model="Qwen/Qwen3-8B",
    tensor_parallel_size=1,
    speculative_config={
        "model": "Qwen/Qwen3-0.6B",
        "num_speculative_tokens": 5,
        "method": "draft_model",
    },
)
outputs = llm.generate(prompts, sampling_params)
```

### 2. 在线模式（`vllm serve`）
```bash
vllm serve Qwen/Qwen3-4B-Thinking-2507 \
    --host 0.0.0.0 \
    --port 8000 \
    --seed 42 \
    -tp 1 \
    --max-model-len 2048 \
    --gpu-memory-utilization 0.8 \
    --speculative-config '{"model": "Qwen/Qwen3-0.6B", "num_speculative_tokens": 5, "method": "draft_model"}'
```

### 3. 异构词表（跨 tokenizer draft 模型）
在 `speculative_config` 中追加 `"use_heterogeneous_vocab": True` 即可启用 TLI 算法：
```python
llm = LLM(
    model="Qwen/Qwen3-8B",
    speculative_config={
        "method": "draft_model",
        "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
        "num_speculative_tokens": 3,
        "use_heterogeneous_vocab": True,
    },
    gpu_memory_utilization=0.5,
)
```

### 4. 配置项汇总（原文出现过的键）
| 键 | 含义 | 原文示例值 |
|---|---|---|
| `model` | draft 模型路径 | `Qwen/Qwen3-0.6B`、`HuggingFaceTB/SmolLM2-135M-Instruct` |
| `num_speculative_tokens` | 每轮 draft 猜测的 token 数 | `5`（默认示例）、`3`（异构示例） |
| `method` | 投机解码方法 | `"draft_model"` |
| `use_heterogeneous_vocab` | 是否启用 TLI 异构词表 | `True`（异构示例）/ 缺省（默认 false） |

> 完整字段定义（包括 `draft_sample_method` 等本文未示例的键）请参阅文末链接 `README.md#--speculative-config-schema`。
