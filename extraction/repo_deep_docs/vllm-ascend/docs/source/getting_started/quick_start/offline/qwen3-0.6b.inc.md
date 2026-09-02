# qwen3-0.6b.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/offline/qwen3-0.6b.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/offline/qwen3-0.6b.inc.md

# vllm-ascend 文档深度解读：Qwen3-0.6B 离线推理快速入门

## 【定位】
这篇文档是 vLLM-Ascend 在 **Ascend 平台上对 Qwen3-0.6B 模型进行离线推理**的最简可运行示例，目标是让用户在容器终端内通过少量 Python 代码即可验证 vLLM 已正确识别并激活 Ascend 平台插件，并产出可预期的生成结果。

---

## 【技术要点】

1. **使用 vLLM 的 `LLM` 类执行离线批量推理**——直接在 Python 进程内同步调用 `llm.generate(prompts, sampling_params)`，不依赖外部服务（与在线 serving 模式相对）。
2. **采样参数固定为贪心解码**：`temperature=0.0`，`max_tokens=32`，即以零温度取概率最高 token 并限制生成长度为 32 token（原文固定取值，原文未给出其他取值范围）。
3. **模型标识为 HuggingFace Hub 上的 `Qwen/Qwen3-0.6B`**——采用默认加载配置（"default model loading configuration"），未传入任何自定义参数。
4. **平台识别机制依赖 vLLM 插件组 `vllm.platform_plugins`**——日志显示已注册的 `ascend -> vllm_ascend:register` 插件被自动加载并激活（"Platform plugin ascend is activated"），可通过环境变量 `VLLM_PLUGINS` 控制加载范围。
5. **测试提示词包含两条**：原文给出 `prompts = ["Hello, my name is", "The future of AI is"]`，用于做最简单的 sanity check。
6. **断言式结果校验**：`assert len(outputs) == len(prompts)` 与 `assert generated_text.strip()` 双断言，确保推理成功且输出非空。

---

## 【关键机制与数据】

### 工作流程（原文信息整合）

1. **插件发现阶段**（原文日志）：vLLM 启动时扫描 `vllm.platform_plugins` 插件组，列出 `ascend -> vllm_ascend:register`，随后激活 `ascend` 平台插件——这是验证环境配置正确的关键标志。
2. **推理阶段**：`LLM(model="Qwen/Qwen3-0.6B")` 在引擎内完成模型加载后，`generate()` 在 EngineCore 进程中执行推理，阻塞至所有 prompt 产出 `max_tokens` 长度的输出。
3. **清理阶段**：离线推理结束后 EngineCore 主动发起 Shutdown（`timeout=0`），并完成 Shutdown；后续出现的 `EngineCore died unexpectedly, shutting down client` 与 `DeprecationWarning: builtin type swigvarlink has no __module__ attribute` **被原文明确归类为"不影响推理结果"的退出信息**。

### 原文给出的生成数据（原文逐字）

| Prompt | Generated text |
|---|---|
| `'Hello, my name is'` | `' Lucy and I am an 8 year old who loves to draw and write stories'` |
| `'The future of AI is'` | `' a topic that is being discussed in various contexts. In the business world, AI'` |

### 进程标识
原文日志中 EngineCore 的进程 PID（原文）：`EngineCore pid=970`——该数字仅在示例日志中出现，非通用配置参数。

---

## 【表格解读】

**原文无表格**（原文仅以代码块、日志块、文本段落形式组织信息，未出现任何 markdown 表格）。

---

## 【公式解读】

**原文无公式**（文档全部内容为示例代码、运行命令与日志文本，未包含任何 LaTeX 数学公式或伪代码形式的算法表达式）。

---

## 【关联】

原文**未提供任何文末内部链接**（题目中已注明"内部链接: (无)"），且文档自身也未指向其他章节、模块或特性。从内容定位推测，本文档位于 `docs/source/getting_started/quick_start/offline/` 路径下，应属于 vLLM-Ascend 离线推理快速入门系列的最基础示例，但原文未做显式关联说明。

---

## 【使用方法】

### 启用前提（原文）
- 已在 Ascend 容器终端环境中（"In the container terminal"）。
- 使用 **默认模型加载配置**（"default model loading configuration"，原文未列出具体字段含义）。

### 操作步骤（原文逐字）

1. **创建脚本文件**（原文命令）：
   ```bash
   # 在容器终端中创建 example.py
   ```
   文件内容即上方给出的完整 Python 代码（`from vllm import LLM, SamplingParams` 起，至 `print(f"...")` 止）。

2. **执行推理**（原文命令）：
   ```bash
   python3 example.py
   ```

3. **校验 Ascend 平台识别**（原文条件）：观测到日志中包含：
   ```
   Platform plugin ascend is activated
   ```

4. **校验生成结果**（原文条件）：通过 `assert` 检查或肉眼对比 "Generated text" 行——原文已给出两条参考输出供对照。

### 退出信息处理（原文说明）
`EngineCore died unexpectedly` 与 `DeprecationWarning: builtin type swigvarlink has no __module__ attribute` 被原文**明确标注**为 "do not affect the inference results"，属于正常的进程退出残留日志，可忽略。

### 未涉及内容（原文未涉及）
- 自定义 SamplingParams 列表（如 top_p、top_k、presence_penalty 等其他采样参数）。
- 多 GPU / 多 NPU 并行配置。
- `tensor_parallel_size` 等 `LLM()` 构造参数。
- 性能数据（吞吐、时延、tokens/s 等基准）。
- 模型路径的本地挂载方式（默认走 HuggingFace Hub 名 `Qwen/Qwen3-0.6B`）。
