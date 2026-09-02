# Thinking、Enable_reasoning、Function Call、Stream 特性叠加及开启方式

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/thinking_reasoning_function_stream.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/thinking_reasoning_function_stream.md

# 深度解读：Thinking / Enable_reasoning / Function Call / Stream 特性叠加

## 【定位】

本文档聚焦 MindIE 大模型推理引擎中 **Thinking（思考）、Enable_reasoning（思考解析）、Function Call（函数调用）、Stream（流式输出）四大特性的开启方式、优先级关系及叠加组合能力**，为开发者提供一份"按特性×按配置维度"可查可执行的统一参考，从而避免在请求体与服务端配置之间分散查找。

---

## 【技术要点】

1. **四特性 × 三维度的开启位点总览**（原文表 1）：Thinking 可在请求级与权重维度配置；Enable_reasoning 仅可在服务级配置；Function Call 由请求级触发、服务级决定解析方式；Stream 仅可在请求级配置。请求级均通过请求体字段控制，服务级均落在 `config.json` 中 `ModelConfig.models.{model_key}` 之下，权重维度落在 `tokenizer_config.json`。
2. **Thinking 优先级三段式**：原文明确 "请求级 > 权重维度 > 模型默认行为"。仅请求级配置 `enable_thinking` 时以其为准；未配置请求级则回退至权重维度；两者都未配置则取决于模型默认行为，原文给出的具体默认值为 "qwen3 默认开启思考，dsv3.1/dsv3.2 默认不开启思考"。
3. **Thinking 权重字段名因模型而异**（原文 1.3 节注意）：qwen3 系列用 `"enable_thinking": true/false`；deepseekv3.2 用 `"thinking": true/false`。
4. **Enable_reasoning 服务级专属 + 模型键名映射**：服务路径固定为 `/usr/local/lib/python3.11/site-packages/mindie_llm/conf/config.json`，默认值为 `false`，开启后输出会分离为 `reasoning_content`（思考过程）与 `content`（最终回答）。`models` 下的模型键名映射：Qwen3-30B-A3B 用 `"qwen3_moe"`；DeepSeek-R1 用 `"deepseek_v2"` 且需把权重文件 `model_type` 改为 `"deepseek_v3"`；DeepSeek-V3.2 用 `"deepseek_v32"`。
5. **Function Call 触发与解析分离**：请求体通过 `tools: [...]` 让模型自行决定是否触发；服务级在 `models.{model}.tool_call_options.tool_call_parser` 配置解析器；原文指出 Qwen 系列无需服务级开启，而 DeepSeek-V3.1 必须服务级开启（例如 `tool_call_parser: "deepseek_v31"`）。
6. **Stream 仅请求级**：字段为 `"stream": true/false`，原文明确默认值 `false`（非流式）。

---

## 【关键机制与数据】

### 工作原理（原文整合）

- **Thinking**：通过在 chat 模板中传入 `enable_thinking` 标志位控制模型是否输出思考过程。它不改变输出字段结构——思考过程仍混在模型输出文本中（典型形态如 `` 或 DeepSeek-V3.2 的 `</think>`），由下游消费方自行区分。
- **Enable_reasoning**：作用于"输出解析阶段"，把已生成文本中的思考片段从 `content` 中剥离，单独写入 `reasoning_content` 字段，是 Thinking 的"配套解析"开关。原文默认 `false`，仅服务级生效，无维度冲突。
- **Function Call**：双层机制——`tools` 决定"是否给模型工具能力并由模型自主决策是否调用"；`tool_call_parser` 决定"模型生成文本中的工具调用片段如何被解析为结构化字段"。原文 6.2 示例同时给出了 `tool_choice: "auto"`。
- **Stream**：以 SSE/分块形式逐段回传模型输出，对内容字段的处理取决于是否同时启用 Enable_reasoning。

### 数据流（原文 5.1 节的输出样式梳理）

| 组合形态 | 关键输出字段（原文摘录） |
|---|---|
| Thinking + Enable_reasoning | `reasoning_content` + `content` 两个字段分离 |
| Thinking + Function Call | `content` 含 `` + 说明文字；触发时含 `tool_calls` |
| Thinking + Stream | 流式 `content`，先 `` 再回答 |
| Enable_reasoning + Function Call | `content`（说明文字）+ `tool_calls` |
| Enable_reasoning + Stream | 流式 `content`（回答内容） |
| Function Call + Stream | 流式 `content` + `tool_calls` |
| 三/四组合（带 Enable_reasoning） | `reasoning_content`（思考）+ `content`（说明）+ `tool_calls` |

### 性能/数值数据

- 原文 6.1 示例：`Qwen3-32B` 使用 `worldSize: 1`、`backendType: "atb"`、`trustRemoteCode: false`。
- 原文 6.2 示例：`max_tokens: 1024`。
- 原文 3.3 示例：`dsv31` 使用 `worldSize: 16`、`tool_call_parser: "deepseek_v31"`。
- 原文未提供吞吐量、时延、首 token 时间等性能指标数据。

---

## 【表格解读】

### 表 1：四大特性开启方式汇总（原文逐字还原）

| 维度 | 开启位置 | 是否开启思考 (Thinking) | 是否开启思考解析 (Enable_reasoning) | 是否开启 Function Call | 是否开启 Stream |
|------|------|------------------------|-----------------------------------|----------------------|----------------|
| **请求级** | 发送的请求体中 | 添加 `"chat_template_kwargs": {"enable_thinking": true/false}` | NA | 传入 `"tools": [...]` 参数，且模型决定触发工具调用 | `"stream": true/false`（默认 false） |
| **服务级** | 服务化配置文件：`/usr/local/lib/python3.11/site-packages/mindie_llm/conf/config.json` | NA | `models` 下配置 `"enable_reasoning": true/false` | NA | NA |
| **权重维度** | 模型权重目录下的 tokenizer_config.json 文件 | 添加 `"enable_thinking": true/false`（不同模型字段名称不一样，详见下文） | NA | NA | NA |

逐行解读：
- **第一行（请求级）**：四个特性中 Thinking、Function Call、Stream 都把请求体作为唯一的或可用的开启位点；Enable_reasoning 在该维度为 `NA`，即请求体无法控制解析开关。
- **第二行（服务级）**：只有 Enable_reasoning 在该维度生效，路径是 MindIE Python 包内固定的 `conf/config.json`，配置点下沉到 `models` 子对象下；Thinking/Function Call/Stream 在该维度为 `NA`。
- **第三行（权重维度）**：仅 Thinking 可在此层配置，且原文明确字段名因模型而异（详见后文 qwen3 vs deepseekv3.2 的差异）。

### 表：Thinking 优先级场景（原文逐字还原）

| 场景 | 行为说明 |
|------|---------|
| 请求级配置了 `enable_thinking` | 以请求级配置为准 |
| 请求级未配置，权重维度配置了 `enable_thinking` | 以权重维度配置为准 |
| 均未配置 | 取决于模型默认行为（如 qwen3 默认开启思考，dsv3.1/dsv3.2 默认不开启思考） |

逐行解读：
- **场景 1**：请求体显式声明具有最高优先级，权重配置被覆盖。
- **场景 2**：权重维度相当于"部署默认值"，在没有请求级覆盖时被采纳。
- **场景 3**：原文给出三个具体模型家族（qwen3 / dsv3.1 / dsv3.2）的默认行为，对部署者而言是该文档中最关键的"落地默认事实"之一。

### 表：Thinking 请求级配置说明（原文逐字还原）

| 字段配置 | 说明 |
|---------|------|
| `"enable_thinking": true` | 开启思考功能 |
| `"enable_thinking": false` | 关闭思考功能 |
| 不添加该字段 | 参考权重维度配置；如权重维度也未配置，则取决于模型默认行为 |

逐行解读：清晰对应"显式开 / 显式关 / 不显式（回退到下层）"三种状态——与上表优先级一致，强调请求级字段是用户侧主开关。

### 表：Thinking 权重维度配置说明（原文逐字还原）

| 字段配置 | 说明 |
|---------|------|
| `"enable_thinking": true` | 开启思考功能 |
| `"enable_thinking": false` | 关闭思考功能 |
| 不添加该字段 | 是否思考取决于模型默认行为 |

逐行解读：与请求级表结构相同，但只影响"请求级未配置"时的回退结果。

### 表：Enable_reasoning 服务级配置说明（原文逐字还原）

| 配置项 | 取值 | 说明 |
|--------|---------|------|
| `enable_reasoning`  | `true`  | 开启模型思考解析，将输出分别解析为 `reasoning_content` 和 `content` 两个字段。默认值：`false` |
| `enable_reasoning`  | `false`（默认值） | 不开启模型思考解析，将输出 `content` 字段。 |

逐行解读：这是一对"是否做输出后处理"的开关，开启会增加一个 `reasoning_content` 字段；默认关闭意味着原生输出只走单一 `content` 通道。

### 表：Function Call 请求级配置说明（原文逐字还原）

| 字段 | 说明 |
|------|------|
| `tools` | 工具列表，包含可用的函数定义 |

逐行解读：单一字段即可触发能力；函数定义遵循 OpenAI 兼容的 JSON Schema 风格（含 `type`/`function`/`parameters`/`required`）。

### 表：Stream 请求级配置说明（原文逐字还原）

| 字段配置 | 说明 |
|---------|------|
| `"stream": true` | 开启流式输出 |
| `"stream": false` | 关闭流式输出（非流式） |
| 不添加该字段 | 默认值为 `false`，即非流式输出 |

逐行解读：三种状态给出明确默认值，便于集成方对默认行为做兜底判断。

### 表：5.1 支持的特性叠加组合（原文逐字还原）

| 特性组合 | 支持情况 | 输出样式说明 |
|---------|---------|-------------|
| **两两组合** |||
| Thinking + Enable_reasoning | ✅ 支持 | 输出分离为两个字段：<br>• `reasoning_content`: 思考过程<br>• `content`: 最终回答 |
| Thinking + Function Call | ✅ 支持 | 输出包含：<br>• `content`: 包含 `` 包裹的思考过程 + 说明文字<br>• `tool_calls`: 工具调用信息（如需调用工具） |
| Thinking + Stream | ✅ 支持 | 流式输出 `content`，先输出思考过程 ``，再输出回答 |
| Enable_reasoning + Function Call | ✅ 支持 | 输出包含：<br>• `content`: 说明文字<br>• `tool_calls`: 工具调用信息 |
| Enable_reasoning + Stream | ✅ 支持 | 流式输出：<br>• `content`: 回答内容 |
| Function Call + Stream | ⚠️ 部分支持 | 流式输出：<br>• `content`: 说明文字<br>• `tool_calls`: 工具调用信息 |
| **三三组合** |||
| Thinking + Enable_reasoning + Function Call | ⚠️ 部分支持 | 输出包含：<br>• `reasoning_content`: 思考过程<br>• `content`: 说明文字<br>• `tool_calls`: 工具调用信息 |
| Thinking + Enable_reasoning + Stream | ✅ 支持 | 流式输出：<br>• `reasoning_content`: 思考过程<br>• `content`: 回答内容 |
| Thinking + Function Call + Stream | ⚠️ 部分支持 | 流式输出：<br>• `content`: 包含思考过程 + 说明文字<br>• `tool_calls`: 工具调用信息 |
| Enable_reasoning + Function Call + Stream | ⚠️ 部分支持 | 流式输出：<br>• `content`: 说明文字<br>• `tool_calls`: 工具调用信息 |
| **四者组合** |||
| Thinking + Enable_reasoning + Function Call + Stream | ⚠️ 部分支持 | 流式输出：<br>• `reasoning_content`: 思考过程<br>• `content`: 说明文字<br>• `tool_calls`: 工具调用信息 |

逐行解读（按维度归纳）：
- **完全支持（✅）的组合**：集中在"两两"层且多为 Thinking/Enable_reasoning/Stream 三者之间的两两叠加；三三组合中仅 Thinking + Enable_reasoning + Stream 完全支持。
- **部分支持（⚠️）的组合**：所有涉及 Function Call 的多组合均落在"部分支持"，提示 Function Call 与 Thinking、Stream 同时叠加时存在行为差异，需结合具体模型再做兼容性确认。
- **输出形态规律**：是否引入 `reasoning_content` 由 Enable_reasoning 决定；是否引入 `tool_calls` 由 Function Call 决定；流式只改变推送粒度，不改变字段集合。
- 原文附注进一步提醒：Thinking 输出在 `content` 中的"包裹标签"因模型而异——Qwen3 系列用 ``，DeepSeek-V3.2 用 `</think>`，需参考模型部署指导。

---

## 【公式解读】

**原文无公式**。

（文档为配置驱动型指南，所有"逻辑表达式"以 JSON 示例和优先级表格呈现，无 LaTeX 数学公式或伪代码公式。）

---

## 【关联】

- **enable_reasoning.md（限制与约束）**：本文 5.2 限制与约束节将该链接作为 Enable_reasoning 的能力边界补充（如适用模型范围、解析字段约束等）。
- **function_call.md（参数说明）**：本文 3.3 节将其作为 `tool_call_parser` 取值与详细语法的权威参考。
- **function_call.md（限制与约束）**：本文 5.2 节将其作为 Function Call 的能力边界补充。
- **../model_support_list.md（模型清单）**：本文 5.2 节将其作为"哪些模型支持上述特性"的总入口，并指向各模型独立的部署指导。
- **上游/下游关系梳理**：
  - Thinking 与 Enable_reasoning 在叠加图中形成"生成 ↔ 解析"的上下游：Thinking 是"是否生成思考"的开关，Enable_reasoning 是"如何拆分思考与回答"的解析器。
  - Function Call 在所有叠加组合中始终作为独立维度存在，并依赖 `tool_call_parser` 进行结构化抽取；它与 Thinking 的输出形式存在交集（均涉及特殊标签），因此文档专门提示"标签形态因模型而异"。
  - Stream 是横切特性，不改变字段语义，只改变推送节奏；它与 Enable_reasoning 配合时输出形态最规整（三三组合中唯一"完全支持"项）。

---

## 【使用方法】

### Thinking 开启
- **请求级**（原文 1.2）：在请求体 `chat_template_kwargs.enable_thinking` 字段中传 `true/false`。
- **权重维度**（原文 1.3）：在 `tokenizer_config.json` 中按模型家族设置：
  - qwen3：`"enable_thinking": true/false`
  - deepseekv3.2：`"thinking": true/false`

### Enable_reasoning 开启（原文 2.2）
- 服务化配置文件路径：`/usr/local/lib/python3.11/site-packages/mindie_llm/conf/config.json`
- 在 `ModelConfig -> models` 下按模型设置（默认 `false`）：
  - Qwen3-32B / 通用 Qwen3：`"qwen3": {"enable_reasoning": true}`
  - Qwen3-30B-A3B：将键名替换为 `"qwen3_moe"`
  - DeepSeek-R1：将键名替换为 `"deepseek_v2"`，并把权重文件 `model_type` 改为 `"deepseek_v3"`
  - DeepSeek-V3.2：将键名替换为 `"deepseek_v32"`

### Function Call 开启
- **请求级**（原文 3.2）：请求体传入 `tools: [...]`（含 `type`/`function.name`/`function.description`/`function.parameters`）。
- **服务级**（原文 3.3）：在 `models.{model_key}.tool_call_options.tool_call_parser` 配置解析器；Qwen 系列无需服务级配置，DeepSeek-V3.1 需服务级配置（如 `"deepseek_v31"`）。

### Stream 开启（原文 4.2）
- 请求体中设置 `"stream": true/false`；默认 `false`（非流式）。

### 全特性叠加请求示例（原文 6.2，原文有即写）
请求体同时包含：
- `"chat_template_kwargs": {"enable_thinking": true}`
- `"tools": [...]`（含 `get_weather` 函数定义）
- `"tool_choice": "auto"`
- `"stream": true`
- `"max_tokens": 1024`

### 全特性叠加服务端示例（原文 6.1，原文有即写）
`config.json` 在 `ModelConfig.models.qwen3` 下设置 `"enable_reasoning": true`，并配合 `worldSize: 1`、`backendType: "atb"`、`trustRemoteCode: false`。

### 启用前置条件（原文限制与约束）
- 硬件范围：Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器和 Atlas 300I Duo 推理卡。
- 模型支持范围：详见 `../model_support_list.md` 中各模型的部署指导链接。
