# Tool Calling

> 仓 `vllm` · 路径 `docs/features/tool_calling.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/tool_calling.md

## 【定位】

这篇文档说明 vLLM 在 Chat Completion API 中如何配置、约束、解析和执行命名函数调用，以及 `auto`、`required`、`none` 三种工具选择模式。

## 【技术要点】

1. **支持范围与版本**
   - 默认支持命名函数调用。
   - 支持 `tool_choice` 的 `auto`、`none`；`required` 从 `vllm>=0.8.3` 起可用。
   - 命名函数调用只保证函数调用结果**能够被合法解析**，不保证模型生成的工具选择或参数具有高质量。

2. **基础服务配置**
   ```bash
   vllm serve meta-llama/Llama-3.1-8B-Instruct \
       --enable-auto-tool-choice \
       --tool-call-parser llama3_json \
       --chat-template examples/tool_chat_template_llama3.1_json.jinja
   ```
   其中：
   - `--enable-auto-tool-choice` 是启用 auto 工具选择的必选参数。
   - `--tool-call-parser llama3_json` 指定 Llama 3 JSON 工具解析器。
   - `--chat-template` 指定能够处理工具角色及包含历史工具调用的 assistant 消息的聊天模板。

3. **命名函数调用与结构化输出**
   - 在 `tools` 中定义函数及其 JSON Schema，再通过 `tool_choice` 指定函数名：
     ```python
     tool_choice={"type": "function", "function": {"name": "get_weather"}}
     ```
   - vLLM 使用 structured outputs，使参数符合工具定义的 JSON Schema。
   - 文档建议同时在提示词中说明预期输出格式，使模型意图与被强制生成的 Schema 对齐。

4. **`required` 与 `none`**
   - `tool_choice='required'` 保证模型生成一个或多个工具调用，调用数量取决于用户查询，参数严格遵循 `tools` 中的 Schema。
   - `tool_choice='none'` 禁止生成工具调用，只返回普通文本；即使请求中定义了工具也会如此。
   - 默认情况下，即使选择 `none`，工具定义仍会进入提示词；可使用 `--exclude-tools-when-tool-choice-none` 排除。

5. **`auto` 与 strict 模式**
   - `tool_choice="auto"` 下，只有至少一个工具设置 `strict: true` 时，structural-tag 解析器才约束工具参数。
   - 没有工具设置 `strict: true` 时，模型自由生成，vLLM 从原始文本中提取工具调用。
   - 命名函数或 `required` 始终应用结构化约束，不受 per-tool `strict` 字段控制。
   - 可通过 `VLLM_ENFORCE_STRICT_TOOL_CALLING` 全局控制 structural tags；其默认值为 `true`。

6. **自定义解析器与聊天模板**
   - `--tool-call-parser` 选择工具解析器。
   - `--tool-parser-plugin` 可注册用户自定义解析器，注册后的解析器名称仍通过 `--tool-call-parser` 指定。
   - `--chat-template` 用于指定自定义工具调用模板；如果模型的 `tokenizer_config.json` 已配置专用模板，该参数也可设为 `tool_use`。

## 【关键机制与数据】

- **原文:** 请求中的 `tools` 同时承担“函数目录”和“参数 Schema”两种作用：函数名供调用方匹配实际实现，嵌套的 `parameters` 则描述可接受参数及必填项。示例中 `location` 和 `unit` 都是必填参数，`unit` 的枚举值为 `celsius`、`fahrenheit`。

- **原文:** 工具调用完成后，响应中的函数名必须与调用方注册的实现对应。原文通过 `tool_functions[tool_call.name]` 按名称取得函数，再使用：
  ```python
  **json.loads(tool_call.arguments)
  ```
  将模型返回的 JSON 参数字符串转换为关键字参数并执行函数。

- **原文:** 完整示例的数据流为：
  1. 通过 `client.models.list().data[0].id` 选择服务端模型。
  2. 发送用户问题、工具定义和 `tool_choice="auto"`。
  3. 读取 `response.choices[0].message.tool_calls[0].function`。
  4. 取得函数名和参数字符串。
  5. 解析参数、匹配本地函数并输出结果。

- **原文:** 示例输出为：
  ```text
  Function called: get_weather
  Arguments: {"location": "San Francisco, CA", "unit": "fahrenheit"}
  Result: Getting the weather for San Francisco, CA in fahrenheit...
  ```

- **原文:** `auto` 模式存在两条不同的解析路径：开启 `strict` 时使用 structural-tag 解析并约束参数；未开启时自由生成，再从原始文本提取调用。因此，auto 模式并不像命名函数或 `required` 那样默认保证结构化参数 Schema。

- **原文:** 调用方仍需负责三件事：
  1. 在请求中定义合适的工具。
  2. 在聊天消息中提供相关上下文。
  3. 在应用逻辑中处理并执行工具调用。

- **原文:** 性能方面，命名函数调用第一次使用 structured outputs backend 时，需要首次编译 FSM，之后编译结果会被缓存；原文描述首次可能出现“several seconds of latency (or more)”。原文没有给出精确耗时、吞吐量或缓存大小。

## 【表格解读】

| `tool_choice` value | Schema-constrained decoding | Behavior |
| --- | --- | --- |
| Named function | Yes (via structured outputs backend) | Arguments are guaranteed to be valid JSON conforming to the function's parameter schema. |
| `"required"` | Yes (via structured outputs backend) | Same as named function. The model must produce at least one tool call. |
| `"auto"` | Only when `strict: true` is set on at least one tool | Structural-tag parsers constrain tool-call arguments when a tool opts in with `strict: true`. Without it, the model generates freely and tool calls are extracted from raw text. |
| `"none"` | N/A | No tool calls are produced. |

逐行解读：

- **Named function：** 指定具体函数时，始终通过 structured outputs backend 约束解码；参数保证为符合函数参数 Schema 的合法 JSON。
- **`"required"`：** 同样始终使用 structured outputs；除参数 Schema 约束外，模型还必须产生至少一个工具调用。
- **`"auto"`：** 是否启用 Schema 约束取决于是否至少有一个工具设置 `strict: true`。开启时使用 structural-tag 解析器；未开启时，模型自由生成并从原始文本提取工具调用。
- **`"none"`：** 不应用工具调用 Schema 约束，也不生成任何工具调用。

## 【公式解读】

原文无公式。

## 【关联】

- **Structured outputs：** 命名函数和 `required` 的核心依赖。它根据 `tools[].function.parameters` 约束生成内容，确保参数是符合 JSON Schema 的合法 JSON。
- **工具解析器：** `auto` 模式通过 `--tool-call-parser` 选择不同模型对应的解析器；strict 模式还依赖 structural-tag 解析。
- **`../usage/v1_guide.md#features`：** 对应 `docs/usage/v1_guide.md#features`。原文说明 V1 引擎对 alternative decoding backends 的支持仍在 roadmap 中。
- **`../../examples/tool_chat_template_llama3.1_json.jinja`：** 快速开始中显式使用。它负责把工具定义、用户消息以及包含历史工具调用的消息组织成模型所需格式。
- **`../../examples/tool_chat_template_mistral.jinja` 与 `../../examples/tool_chat_template_mistral_parallel.jinja`：** 文档链接提供的 Mistral 工具聊天模板，其中一个名称明确对应 parallel tool calls。
- **`../../examples/tool_chat_template_llama3.2_json.jinja`、`../../examples/tool_chat_template_llama4_pythonic.jinja`：** 分别提供 Llama 3.2 JSON 和 Llama 4 Pythonic 风格的工具聊天模板候选。
- **`../../examples/tool_chat_template_granite.jinja`、`../../examples/tool_chat_template_granite_20b_fc.jinja`：** 提供 Granite 系列的通用及函数调用模板候选。
- **`../../examples/tool_chat_template_deepseekv3.jinja`：** 提供 DeepSeek V3 的工具聊天模板候选。
- **`json.loads(tool_call.arguments)`：** 位于模型生成结果与应用执行逻辑之间的边界：模型返回 JSON 字符串，Python 应用负责反序列化、验证函数名并调用本地实现。

## 【使用方法】

1. **启动启用工具调用的服务**

   ```bash
   vllm serve meta-llama/Llama-3.1-8B-Instruct \
       --enable-auto-tool-choice \
       --tool-call-parser llama3_json \
       --chat-template examples/tool_chat_template_llama3.1_json.jinja
   ```

2. **发送 auto 工具选择请求**

   ```python
   from openai import OpenAI
   import json

   client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")

   def get_weather(location: str, unit: str):
       return f"Getting the weather for {location} in {unit}..."

   tool_functions = {"get_weather": get_weather}

   tools = [
       {
           "type": "function",
           "function": {
               "name": "get_weather",
               "description": "Get the current weather in a given location",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "location": {
                           "type": "string",
                           "description": "City and state, e.g., 'San Francisco, CA'"
                       },
                       "unit": {
                           "type": "string",
                           "enum": ["celsius", "fahrenheit"]
                       }
                   },
                   "required": ["location", "unit"],
               },
           },
       },
   ]

   response = client.chat.completions.create(
       model=client.models.list().data[0].id,
       messages=[
           {"role": "user", "content": "What's the weather like in San Francisco?"}
       ],
       tools=tools,
       tool_choice="auto",
   )

   tool_call = response.choices[0].message.tool_calls[0].function
   print(f"Function called: {tool_call.name}")
   print(f"Arguments: {tool_call.arguments}")
   print(
       f"Result: "
       f"{tool_functions[tool_call.name](**json.loads(tool_call.arguments))}"
   )
   ```

3. **强制至少生成一个工具调用**

   ```python
   tool_choice="required"
   ```

4. **禁止工具调用**

   ```python
   tool_choice="none"
   ```

   如不希望工具定义继续进入提示词：

   ```bash
   --exclude-tools-when-tool-choice-none
   ```

5. **配置 auto 模式相关参数**

   ```text
   --enable-auto-tool-choice
   --tool-call-parser llama3_json
   --chat-template examples/tool_chat_template_llama3.1_json.jinja
   ```

   可选的自定义解析器配置：

   ```text
   --tool-parser-plugin
   --tool-call-parser
   ```

6. **按 OpenAI strict-schema 风格定义参数**
   - 每个 `parameters` 对象设置 `"additionalProperties": "false"`。
   - 将 `properties` 中的所有字段标记为必填。
   - 可选字段通过允许 `null` 表示，例如：
     ```json
     {"type": ["string", "null"]}
     ```

7. **全局关闭 structural tags**

   ```bash
   VLLM_ENFORCE_STRICT_TOOL_CALLING=false vllm serve ...
   ```

   该操作不改变命名函数调用或 `tool_choice="required"` 所使用的 schema-derived structured outputs。

所给原文在“If your favorite tool-calling model”处截断，因此完整的模型解析器列表、parallel tool calls 的详细配置、Responses API 和 Anthropic Messages API 的具体启用命令，以及插件注册代码，原文未涉及。
