# Batch Invariance

> 仓 `vllm` · 路径 `docs/features/batch_invariance.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/batch_invariance.md

# vLLM Batch Invariance 文档深度解读

## 【定位】
这篇文档描述 vLLM 中**批量不变性 (Batch Invariance)** 特性:确保模型推理输出在不同 batch size 或不同请求顺序下保持确定性与可复现性,处于 beta 阶段并由专门的 tracking issue 跟进进度。

---

## 【技术要点】

1. **启用机制 (核心开关)**:通过环境变量 `VLLM_BATCH_INVARIANT=1` 触发,无侵入式激活。
2. **硬件门槛**:仅支持 NVIDIA GPU 且 **compute capability ≥ 8.0** (即 Ampere 及之后架构,A100/H100 等符合)。
3. **确定性保证范围**:覆盖 batch size 维度与 batch 内请求顺序维度,保证同一 prompt + 同一采样参数永远产出相同输出。
4. **启用代价与权衡**:会主动禁用部分优化(如 **tensor parallel 模式下的 custom all-reduce**),以可复现性换取吞吐/延迟,这是有意的设计取舍。
5. **底层内核切换**:attention 等算子会改走**确定性 (deterministic) kernel 实现**,从而消除 batch 相关算子的浮点累加顺序差异。
6. **采样层要求示例**:文档示例中给出 `seed=42`、`temperature=0.7`、`top_p=0.95`、`max_tokens=100` 等可复现参数组合,seed 是配合 batch invariance 获得真正确定性输出的关键。

---

## 【关键机制与数据】

### 工作原理 (原文:"When batch invariance is enabled, vLLM:")
1. **使用确定性 kernel 实现** —— attention 等核心算子切到 deterministic 版本,消除 reduction 顺序带来的非确定性。
2. **跨 batch size 数值行为一致** —— 即便单请求 (b=1) 与批量 (b=N) 跑同一 prompt,逐 token 数值结果应一致。
3. **禁用部分非确定性优化** —— 显式点名 **tensor parallel 模式下的 custom all-reduce** 会被关闭,因为该类通信归约在跨 rank 时序与顺序会引入非确定偏差。

### 性能数据
- 原文未提供具体数字(无 throughput/latency 对比)。
- 原文定性表述:"Enabling batch invariance may impact performance compared to the default non-deterministic mode. This trade-off is intentional to guarantee reproducibility." —— 即**确定性 vs 性能**是有意为之的权衡。
- 原文:目前处于 beta,部分特性仍在积极开发,跟踪入口为 GitHub issue #27433。

### 数据流(在线/离线两种)
- **在线 (Server Mode)**:启动命令 `VLLM_BATCH_INVARIANT=1 vllm serve meta-llama/Llama-3.1-8B-Instruct` → OpenAI 兼容客户端 `/v1/...` 调用 → 同一 prompt 多次调用跨 batch/order 输出相同。
- **离线 (Offline)**:在 Python 进程内 `os.environ["VLLM_BATCH_INVARIANT"]="1"` → 构造 `LLM(model=..., tensor_parallel_size=1)` + `SamplingParams(temperature=0.7, top_p=0.95, max_tokens=100, seed=42)` → `llm.generate(prompts, sampling_params)` 一次性产出确定结果。

---

## 【表格解读】

**原文无表格**。

(文档以枚举列表形式给出「Tested Models」,而非结构化表格;详见下文【使用方法】中按原文逐字保留的模型清单。)

---

## 【公式解读】

**原文无公式**。

文档未涉及任何数学公式或伪代码,机制描述以自然语言 + 命令/代码片段形式呈现。

---

## 【关联】

文档中未提供任何内部 markdown 链接 (内部链接信息标注为"无")。但基于文中显式提及的模块/特性,可梳理如下关联关系:

- **`tensor_parallel_size=1` (TP)** ← 离线示例明确将张量并行度设为 1,因为 batch invariance 会**禁用 TP 模式下的 custom all-reduce**,TP 多 rank 通信本身会引入非确定因素,所以示例以 TP=1 来最严格地展示不变性。
- **Attention kernel 实现** ← 实现细节第一点提到 "deterministic kernel implementations for attention",即该特性与 vLLM 后端的 attention backend (FlashAttention/Triton 等) 的确定性分支紧密耦合。
- **`SamplingParams` 中的 `seed`** ← 采样层 seed 与 batch invariance 是**互补关系**:batch invariance 保证算子层确定性,seed 保证采样层确定性,二者缺一不可,文档示例中 `seed=42` 与该机制呼应。
- **OpenAI 兼容服务 (`vllm serve` + `/v1`)** ← 在线模式下 batch invariance 作用于 `vllm serve` 启动的 server,经 OpenAI-compatible HTTP API 暴露,与 OpenAI client SDK 直接对接。
- **tracking issue #27433** ← 文档把当前 beta 状态、规划改进(更多 GPU 架构、更多模型、性能优化)统一归口到此 issue,形成**特性-进度**关联。

---

## 【使用方法】

### 启用开关
```bash
export VLLM_BATCH_INVARIANT=1
```

### 在线推理 (Server 模式)
```bash
VLLM_BATCH_INVARIANT=1 vllm serve meta-llama/Llama-3.1-8B-Instruct
```
客户端示例参数:`model="meta-llama/Llama-3.1-8B-Instruct"`, `max_tokens=100`, `temperature=0.7`, `seed=42`。

### 离线推理
环境变量在 Python 内 `os.environ["VLLM_BATCH_INVARIANT"]="1"` 设置,`LLM` 构造 `tensor_parallel_size=1`,`SamplingParams` 参数 `temperature=0.7, top_p=0.95, max_tokens=100, seed=42`。

### 硬件要求
NVIDIA GPU,compute capability ≥ 8.0 (Ampere 及以上)。

### 已验证模型清单 (原文逐字保留,作为可用配置项参考)

| 类别 | 模型 |
|------|------|
| DeepSeek | `deepseek-ai/DeepSeek-V3`, `deepseek-ai/DeepSeek-V3-0324`, `deepseek-ai/DeepSeek-R1`, `deepseek-ai/DeepSeek-V3.1` |
| Qwen3 (Dense) | `Qwen/Qwen3-1.7B`, `Qwen/Qwen3-8B`, `Qwen/Qwen3-4B-AWQ`, `Qwen/Qwen3-8B-AWQ` |
| Qwen3-VL | `Qwen/Qwen3-VL-2B-Instruct`, `Qwen/Qwen3-VL-4B-Instruct` (单图与视频输入) |
| Qwen3 (MoE) | `Qwen/Qwen3-30B-A3B`, `Qwen/Qwen3-Next-80B-A3B-Instruct`, `Qwen/Qwen3-30B-A3B-Thinking-2507-FP8` |
| Qwen2.5 | `Qwen/Qwen2.5-0.5B-Instruct`, `Qwen/Qwen2.5-1.5B-Instruct`, `Qwen/Qwen2.5-3B-Instruct`, `Qwen/Qwen2.5-7B-Instruct`, `Qwen/Qwen2.5-14B-Instruct`, `Qwen/Qwen2.5-32B-Instruct` |
| Llama 3 | Llama3.1 与 3.2 系列(例:`meta-llama/Llama-3.2-3B-Instruct`) |
| GPT-OSS | `openai/gpt-oss-20b`, `openai/gpt-oss-120b` |
| Mistral | `mistralai/Mistral-7B-v0.3` |
| Phi | `microsoft/Phi-3.5-mini-instruct` |
| Granite 3.1 (MoE) | `ibm-granite/granite-3.1-1b-a400m-instruct`, `ibm-granite/granite-3.1-3b-a800m-instruct` |
| Granite 3.1 (Dense) | `ibm-granite/granite-3.1-2b-instruct`, `ibm-granite/granite-3.1-8b-instruct` |
| EXAONE 4.0 | `LGAI-EXAONE/EXAONE-4.0-1.2B`, `LGAI-EXAONE/EXAONE-4.0.1-32B`, `LGAI-EXAONE/EXAONE-4.0-32B` |

### 已知权衡 (原文有则写)
- 启用 batch invariance 会**降低性能**(对比默认非确定性模式),系为可复现性做出的**有意设计**取舍。
- TP 模式下的 **custom all-reduce** 会被禁用。

### 进度跟进
当前 beta,完整进度与未来改进(更多 GPU 架构、更多模型、性能优化、更多测试)集中在 tracking issue **<https://github.com/vllm-project/vllm/issues/27433>**;其他模型可能也可用,但未在上述清单中验证,若遇问题可到 [GitHub issue tracker](https://github.com/vllm-project/vllm/issues/new/choose) 反馈。
