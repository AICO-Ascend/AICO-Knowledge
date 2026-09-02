# Interleaved Thinking

> 仓 `vllm` · 路径 `docs/features/interleaved_thinking.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/interleaved_thinking.md

# vllm `docs/features/interleaved_thinking.md` 深度解读

## 【定位】
本篇文档描述 vLLM 中**交错思考（Interleaved Thinking）** 能力,即让模型在多次工具调用之间插入推理步骤,从而基于工具返回的中间结果进行更细致的决策——并明确该特性会**增加 token 消耗与响应延迟**,需要在预算与性能之间权衡。

---

## 【技术要点】

1. **核心能力定位**:交错思考让模型在"工具调用 → 收到结果 → 再次调用工具"的循环中,每一步都能基于上一次工具结果进行推理,而不是一次性把所有工具调用串好再发起。
2. **启用入口(命令行)**:通过 `vllm serve` 启动服务时,需同时指定 `--tool-call-parser`、`--reasoning-parser`、`--enable-auto-tool-choice` 三个参数,文档示例中 `--tensor-parallel-size 4`。
3. **模型支持范围**:目前仅两类模型支持——`moonshotai/Kimi-K2-Thinking`(reasoning parser 名为 `kimi_k2`)与 `MiniMaxAI/MiniMax-M2`(reasoning parser 名为 `minimax_m2`)。
4. **重要约束(原文警告)**:原文明确指出 "Interleaved thinking increases token usage and response latency"——启用前需评估预算与性能要求。
5. **客户端调用方式**:通过 OpenAI 兼容的 `chat.completions.create` 接口,在请求中传入 `tools`、`tool_choice="auto"`,并在多轮对话中将 `reasoning` 字段随 `assistant` 消息一起回传(见示例代码中 `reasoning: response.choices[0].message.reasoning`)。
6. **典型应用形态**:文档示例演示了"天气查询"场景——一次工具调用 → 拿到 celsius 结果 → 模型基于推理判断需再以 Fahrenheit 形式返回或调整后续行为。

---

## 【关键机制与数据】

### 工作原理(原文机制描述)
原文以列举形式给出模型在交错思考模式下能做到的四件事(均为原文措辞,逐条忠实还原):

- **Reason about the results of a tool call before deciding what to do next**——在收到工具返回后,先推理再决定下一步。
- **Chain multiple tool calls with reasoning steps in between**——把多个工具调用串联起来,中间插入推理步骤。
- **Make more nuanced decisions based on intermediate results**——基于中间结果做更细致的决策。
- **Provide transparent reasoning for its tool selection process**——为工具选择过程提供可读的推理。

### 数据流(原文示例代码体现的交互流程)
1. 客户端发起第一次 `chat.completions.create`,携带 `tools` 与 `tool_choice="auto"`。
2. 服务端返回包含 `tool_calls` 的 `assistant` 消息,以及 `reasoning` 字段(原文代码注释:`# append reasoning`)。
3. 客户端将该 `assistant` 消息追加到 `messages`,保留 `reasoning` 字段。
4. 客户端在本地执行工具函数(示例中是 `get_current_weather`),将结果以 `role="tool"` 追加到 `messages`,同时附带 `tool_call_id` 与 `name`。
5. 客户端发起第二次 `chat.completions.create`(原文:`response_2 = client.chat.completions.create(...)`),模型在拿到工具结果后再次推理并生成最终 `content`。

### 性能数据
**原文未提供具体的 token 增量、延迟数字、基准测试结果**——只在 Introduction 处做了定性警告(会增加 token 与延迟),未给出量化指标。

---

## 【表格解读】

原文中的关键表格为「Supported Models」,逐字还原如下:

| Model Series | Reasoning Parser Name |
| ------------ | --------------------- |
| moonshotai/Kimi-K2-Thinking | kimi_k2 |
| MiniMaxAI/MiniMax-M2 | minimax_m2 |

**逐行解读**:
- **第 1 行**(表头):表格以"模型系列"与"推理解析器名称"两列组织,前者表示 HF 上的模型仓库名,后者表示在 vLLM 中 `--reasoning-parser` 应填入的字符串值。
- **第 2 行 `moonshotai/Kimi-K2-Thinking` ↔ `kimi_k2`**:Kimi 系列的"思考"变体对应的解析器标识;启用该模型时 `--reasoning-parser kimi_k2`、`--tool-call-parser` 也应同源(原文示例对 `MiniMaxAI/MiniMax-M2` 给出了 `minimax_m2` 同名配对的写法,可推断此处的 `kimi_k2` 同样要求解析器与 parser 名称同源)。
- **第 3 行 `MiniMaxAI/MiniMax-M2` ↔ `minimax_m2`**:MiniMax 系列的 M2 模型,原文示例完整命令即为这一行所对应的配置:`--tool-call-parser minimax_m2 --reasoning-parser minimax_m2 --enable-auto-tool-choice`。
- **整体含义**:该表揭示 vLLM 中"交错思考"是一种**模型级(而非引擎级通用)能力**——只有原生支持思考块与工具调用交错格式的模型,才有专属的 reasoning parser;未列入此表的模型,即便启用了 `--enable-auto-tool-choice`,也无法产生交错推理效果。

---

## 【公式解读】

原文无公式(无 LaTeX、无伪代码算法式)。仅在示例代码中有一段普通的 Python 函数 `get_current_weather(location: str, unit: "str")` 用条件分支返回摄氏度或华氏度的字符串,属于业务示例而非数学/算法公式。

**原文无公式**。

---

## 【关联】

由于文末标注「内部链接: (无)」,原文并未显式给出超链接到其他文档的位置。但从文档语义可识别出以下**特性/模块级关联**(均为原文术语推断,不臆造新关系):

- **Tool Calling(工具调用)能力**:交错思考是其上层增强,文档明确以 `tools`/`tool_choice="auto"`/`tool_calls` 字段为前提。
- **`--enable-auto-tool-choice` 开关**:原文示例命令依赖此开关,它是 vLLM 中让模型自主选择工具的开关;未启用则交错思考无法发挥作用。
- **`--reasoning-parser` 与 `--tool-call-parser`**:在文档示例中两个参数使用同一个值(`minimax_m2`),暗示交错思考要求**推理解析与工具调用解析同源**——这两个解析器通常在 vLLM 中是独立模块,本文是该特性的耦合点。
- **`chat.completions.create` 中的 `reasoning` 字段**:示例代码将其与 `tool_calls` 一同存放在 `assistant` 消息中,这意味着 vLLM 在响应体里把推理内容作为独立字段暴露给客户端——与 vLLM 标准的 `reasoning_content` / `reasoning` 字段体系一致。
- **下游影响**:由于会"增加 token 使用与响应延迟",该特性与 vLLM 的 **KV cache 调度、吞吐(throughput)、首 token 时间(TTFT)** 等性能指标存在隐含的负相关关系(原文仅做定性警告,未给出具体量化)。

---

## 【使用方法】

### 服务端启动命令(原文示例,逐字还原)

```bash
vllm serve MiniMaxAI/MiniMax-M2 \
  --tensor-parallel-size 4 \
  --tool-call-parser minimax_m2 \
  --reasoning-parser minimax_m2 \
  --enable-auto-tool-choice
```

### 关键配置项说明(原文有据)

| 配置项 | 原文中的取值 | 作用 |
| --- | --- | --- |
| `MODEL`(`vllm serve` 后的位置参数) | `MiniMaxAI/MiniMax-M2`(示例)/ `moonshotai/Kimi-K2-Thinking`(表格) | 选择支持交错思考的模型 |
| `--tensor-parallel-size` | `4`(示例) | 张量并行度 |
| `--tool-call-parser` | `minimax_m2`(示例) | 工具调用解析器 |
| `--reasoning-parser` | `minimax_m2`(示例) | 推理块解析器 |
| `--enable-auto-tool-choice` | 无值(标志位) | 开启模型自动选择工具的能力 |

### 客户端调用要点(原文代码中体现)

1. 通过 OpenAI 客户端连 `http://localhost:8000/v1`。
2. 在 `messages` 中以 `tools`/`tool_choice="auto"` 发起首次请求。
3. 在追加 `assistant` 消息时,**必须同时保留 `reasoning` 字段**(`reasoning: response.choices[0].message.reasoning`),否则模型下一轮将丢失中间推理。
4. 工具结果以 `role="tool"` 追加,并带 `tool_call_id` 与 `name`。
5. 发起第二次 `chat.completions.create` 后,模型在 tool 结果之上再次推理并产出最终 `content`。

原文未提供其他启用方式(如环境变量、配置文件、HTTP API flag 等);也未给出 K8s/Ansible 等部署形态的配置示例。
