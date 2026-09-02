# Function Call

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/function_call.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/function_call.md

【定位】
本文档系统介绍昇腾自研大模型推理引擎 MindIE LLM 中 **Function Call（函数调用 / 工具调用 tool use）** 特性——即大模型识别何时需要调用外部工具、如何选工具与填参、并在拿到工具结果后整合生成最终答案的全流程能力，并说明其在哪些硬件/模型上受支持、如何配置 server 端参数、以及如何发起一次完整的 OpenAI 兼容请求。

【技术要点】

1. **能力定义与术语统一**：Function Call ＝ 让大模型在不能直接回答时，从应用给定的工具集合中挑选一个或多个函数、返回工具名 + 参数，由上层应用执行后再回灌结果生成最终答案；本文档后续统一以“**工具调用（tool use）**”叙述。

2. **5 步闭环流程**（图 1 流程）：① 应用下发 system prompt + 用户输入 + 可用工具集合 → ② 模型决定直答还是选工具，并返回工具名/参数 → ③ 应用解析响应、执行函数得到工具结果 → ④ 应用以工具结果重组成 prompt 再次送回模型 → ⑤ 模型基于工具结果总结生成最终答案。

3. **硬件 & 模型支持范围**：
   - 硬件：仅 **Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器、Atlas 300I Duo 推理卡**。
   - 模型：**ChatGLM3-6B、Qwen3-32B、Qwen3-235B-A22B、Qwen3-30B-A3B、DeepSeek-R1-0528、Qwen2.5-Instruct、DeepSeek-V3.1** 系列。
   - 接口：**仅支持 OpenAI chat 接口**。

4. **能力叠加与互斥**：
   - **可叠加**：量化、长序列、多机推理、PD 分离、MoE、Multi-LoRA、SplitFuse、并行解码、专家并行、MTP、Prefix Cache、思考解析、张量并行、MLA。
   - **互斥/限制**：DeepSeek-V3.1 不能同时开启 Function Call + 思考解析；**SplitFuse、并行解码、MTP 在流式推理下不可叠加 Function Call**。
   - **不支持的后处理参数**：`include_stop_str_in_output`、`stop`、`best_of`、`n`、`use_beam_search`、`logprobs`；`temperature` 过高（采样随机性高）会影响触发稳定性。

5. **流式 vs 非流式**：默认所有支持模型均可做**非流式**推理；**流式推理**仅 **Qwen3-32B、Qwen3-235B-A22B、Qwen3-30B-A3B、DeepSeek-R1-0528** 支持。

6. **请求体 JSON 嵌套层次上限为 10 层**（含 Function Call 报文的请求）。

【关键机制与数据】

1. **双模型角色回复机制**：要让模型最终回答，必须把 assistant 角色的 `tool_calls`（含每个调用的 `id` 与 `function.name/arguments`）原样回传，再用 `tool` 角色把工具执行结果对应到同一个 `id` 上再次请求，否则上下文无法闭合。（原文步骤 4 + 请求样例注释）

2. **工具解析器（ToolsCallProcessor）必须与模型族严格匹配**——例如 DeepSeek-V3.1 强制 `tool_call_parser="deepseek_v31"`，若保留默认 `""` 或误配为 `deepseek_v3` 会因格式不匹配导致解析失败。`chat_template`（`.jinja` 文件路径）用于替换 `tokenizer_config.json` 中的默认模板：DeepSeek 系列（V3.1 / R1-0528 / V3-0324）权重自带模板**不**支持 Function Call，必须显式传入；chat_template 的**空格/换行**会影响数据集与 Function Call 评分。

3. **触发稳定性受采样超参影响**：高 `temperature` 会导致模型随机选择工具/参数，降低 Function Call 触发稳定性（原文作为约束列出，非性能数字）。

4. **响应中的计时字段**（原文响应样例展示）：`prefill_time`（prefill 阶段耗时，单位原文未指定，样例值 200）、`decode_time_arr`（per-token decode 耗时数组，样例值从 25 到 56 不等），可用于工具调用场景下的延迟分解。

5. **Decode token 拆解示例**（原文响应样例中 `decode_time_arr` 数组举例）：`[56, 28, 28, 28, 28, ..., 28, 32, 28, 28, 41, 28, 25, 28]`——首 token 因含工具描述生成耗时较高（56），多数常规 token 稳定在 ~28 ms，部分 token 因特殊输出略高/略低。

【表格解读】

**表 1 Function Call 特性补充参数——`ModelConfig` 中的 `models` 参数**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| `chat_template` | string | `.jinja` 格式的文件路径 `""` | 传入自定义对话模板，替换模型默认对话模板；默认 `""`；DeepSeek 系列 `tokenizer_config.json` 中的默认 `chat_template` 不支持工具调用，可用此参数传入支持工具调用的版本；DeepSeek 系列、Qwen 系列（大语言模型）、ChatGLM 系列、LLaMA 系列模型支持使用该参数传入自定义模板。 |
| `tool_call_options` | — | — | （原表未填取值类型与取值范围，仅作为占位外层 key，内含 `tool_call_parser`） |
| `tool_call_parser` | string | [表 2 已注册 ToolsCallProcessor](#table2) 中的「可选注册名称」或 `""` | 使能 Function Call 时选择工具的解析方式；默认 `""`；未配置或配置错误时使用当前模型所对应的默认工具解析方式；**DeepSeek-V3.1 模型使用 Function Call 时必须配置为 `"deepseek_v31"`**，其余模型使用默认值；与 `chat_template` 配合使用，根据 `chat_template` 中指定的 Function Call 调用格式选择相应的 ToolsCallProcessor。 |

**逐行解读**：
- `chat_template` 是**模型侧**字段，给的是 `.jinja` 文件绝对路径；其作用是告诉推理引擎按何种 prompt 模板拼接 system/user/tool 消息。默认值 `""` 表示沿用权重自带模板；只有当自带模板不支持工具（如 DeepSeek 全系）时**才必须**传入新模板。
- `tool_call_options` 是外层容器键，用来包裹真正的解析选项；具体语义放在子项 `tool_call_parser` 中。
- `tool_call_parser` 是**解析侧**字段，决定模型吐出的工具调用文本用什么解析器切出 name/arguments。它的取值表绑定了下表（表 2）中的一组别名（如 `qwen3`、`hermes`、`deepseek_v31` 等）；若用户填空或填错，则引擎自动回退到「该模型默认」解析器——但 DeepSeek-V3.1 例外，必须显式 `deepseek_v31`，否则会落到 `deepseek_v3` 而格式错配。

**表 2 已注册 ToolsCallProcessor**

| 工具解析模块 | 可选注册名称 | 说明 |
|---|---|---|
| `ToolsCallProcessorChatglmV2` | `chatglm2_6b`，`chatglm_v2_6b`，`chatglm_v2`，`chatglm2` | 不进行工具解析，直接返回 `content`。 |
| `ToolsCallProcessorChatglmV3` | `chatglm3_6b`，`chatglm_v3_6b`，`chatglm_v3`，`chatglm3` | 适用于 ChatGLM3-6B 的工具解析模块。 |
| `ToolsCallProcessorChatglmV4` | `chatglm4_9b`，`chatglm_v4_9b`，`glm_4`，`glm_4_9b` | 适用于 GLM4-9B 的工具解析模块。 |
| `ToolsCallProcessorDeepseekv3` | `deepseek_v2`，`deepseek_v3`，`deepseekv2`，`deepseekv3` | 适用于 DeepSeek-R1-0528 与 DeepSeek-V3-0324 的工具解析模块。 |
| `ToolsCallProcessorDeepseekv31` | `deepseek_v31`，`deepseekv31` | 适用于 DeepSeek-V3.1 的工具解析模块。 |
| `ToolsCallProcessorLlama` | `llama`，`llama3`，`llama3_1` | 适用于 LLaMA3 的工具解析模块。 |
| `ToolsCallProcessorQwen1_5_or_2` | `qwen1_5`，`qwen_1_5`，`qwen2`，`qwen_2`，`qwen1_5_or_2`，`qwen_1_5_or_2` | 适用于 Qwen1.5 与 Qwen2 的工具解析模块。 |
| `ToolsCallProcessorQwen2_5` | `qwen2_5`，`qwen_2_5` | 适用于 Qwen2.5 的工具解析模块。 |
| `ToolsCallProcessorQwen3` | `qwen3`，`qwen3_moe`，`hermes` | Hermes 工具解析方式，适用于 Qwen3 与 Qwen3-moe 系列。 |

**逐行解读**：
- 该表本质上是一个**模型族 → 文本切片规则**的注册表；每个解析器类（左侧）内部固化了如何从模型输出文本里正则抽取 `function name + JSON arguments`。
- **别名重定向**：同一类解析器接受多个等效别名，目的是兼容用户使用不同 checkpoint 命名（例如 `qwen2_5` 与 `qwen_2_5` 等价）。
- **特殊行为**：`ToolsCallProcessorChatglmV2` 是个**空操作**解析器——仅放行 content，不解析工具。这说明 ChatGLM2-6B 不在 Function Call 支持范围（虽然表 1 中只有 ChatGLM3-6B 在受支持模型清单里）。
- **`ToolsCallProcessorQwen3` 复用 Hermes 格式**：`hermes` 别名表明 Qwen3 系列的工具调用文本遵循 Hermes XML/JSON 风格。
- **DeepSeek 分两支**：v2/v3（包括 R1-0528 与 V3-0324）共用一个解析器，但 **V3.1 必须单独走 `deepseek_v31`**，因 V3.1 引入了独立 tool-call token 序列，必须新解析器才能正确切分。

【公式解读】

原文无公式。

【关联】

- **服务化参数配置章节**：`../user_manual/service_parameter_configuration.md`——本文档「执行推理」步骤 2 中明确要求用户在 `Server` 的 `config.json` 里新增 `tool_call_parser` 与 `chat_template` 字段，**更完整的服务化参数语义**需在该配置手册中查阅（本文档为引用方）。
- **MindIE Motor 服务化 RESTful 接口**：本文档步骤 4 把完整请求样例（含 OpenAI 兼容 schema、`tools[].function.parameters` JSON-Schema、`tool_choice`、`stream` 字段）指向《MindIE Motor 开发指南》的“服务化接口 > EndPoint 业务面 RESTful 接口 > 兼容 OpenAI 接口 > 推理接口”章节——这是 Function Call 走线的 HTTP 入口，与 `service_parameter_configuration.md` 共同构成「参数面」与「请求面」两个上下游。
- **可叠加特性（前置条件）**：Function Call 与量化、长序列、多机推理、PD 分离、MoE、Multi-LoRA、SplitFuse、并行解码、专家并行、MTP、Prefix Cache、思考解析（DeepSeek-V3.1 除外）、张量并行、MLA 等特性的叠加关系意味着：部署 Function Call 时还需参考这些特性各自的部署/限制文档（本文档未列具体章节路径，但约束维度已穷举）。
- **互斥特性**：与 `include_stop_str_in_output / stop / best_of / n / use_beam_search / logprobs` 后处理参数互斥，意味着如要做 Function Call，这些后处理开关必须关闭；同时 `SplitFuse / 并行解码 / MTP` 三者在**流式**模式下与 Function Call 互斥，非流式则可叠加。
- **思考解析**：DeepSeek-V3.1 上思考解析与 Function Call **互斥**（一条请求只能选其一）。

【使用方法】

1. **确认硬件/模型在白名单内**（Atlas 800I A2 / 800I A3 / 300I Duo；模型需在 ChatGLM3-6B、Qwen3-32B、Qwen3-235B-A22B、Qwen3-30B-A3B、DeepSeek-R1-0528、Qwen2.5-Instruct、DeepSeek-V3.1 列表中）。

2. **编辑 server 配置**：
   - whl 包：`vi {MindIE安装目录}/mindie_llm/conf/config.json`
   - run 包：`vi {MindIE安装目录}/latest/mindie-service/conf/config.json`
   - 在 `ModelConfig[*].models` 下新增对应 `model_type` 键（DeepSeek-V3.1 写 `deepseekv2`），内含 `tool_call_options.tool_call_parser` 与 `chat_template`（DeepSeek 系列必须写；其余模型可选）：

     ```json
     "models": {
         "deepseekv2": {
             "tool_call_options": { "tool_call_parser": "deepseek_v31" },
             "chat_template": "/path/to/tool_chat_template_deepseekv31.jinja"
         }
     }
     ```

3. **启动服务**：
   - whl：`mindie_llm_server`
   - run：`./bin/mindieservice_daemon`

4. **发起请求**：以 OpenAI chat 接口（`POST https://{ip}:{port}/v1/chat/completions`）形式发送，`messages` 中带 `system`/`user`，`tools` 描述可用函数（含 `parameters` JSON-Schema），`tool_choice` 可设为 `auto`，`stream` 决定是否启用流式（仅 Qwen3-32B / Qwen3-235B-A22B / Qwen3-30B-A3B / DeepSeek-R1-0528 支持流式 Function Call）。拿到模型返回的 `tool_calls`（含 `id` 与 `function.name/arguments`）后，由应用侧**实际执行**外部函数；再以 `tool` 角色消息关联该 `id` 把工具执行结果回灌请求，让模型生成最终答案。

5. **避坑提示**：
   - DeepSeek-V3.1 必须显式 `tool_call_parser="deepseek_v31"`，且必须传 `chat_template`，否则要么用错解析器要么用不支持 tool 的默认模板。
   - `temperature` 调低以保证触发稳定性。
   - JSON 嵌套 ≤ 10 层。
   - 流式模式下不要叠 `SplitFuse` / 并行解码 / `MTP`；DeepSeek-V3.1 流式下不要开思考解析。

## 图文联合解读

- `function_call_flowchart.png`: ## 图文联合解读

**1) 图的内容**：序列图，左侧为"应用"，右侧为"推理引擎（以MindIE为例）"，共5条交互消息。流程为：①应用调用Rest API传入prompt/functions/question；②引擎决策直接回答或选取工具；③引擎返回工具名称及参数；④应用解析响应并执行函数；⑤应用将工具结果封装入message再次请求；⑥引擎综合messages生成最终答案并返回。

**2) 技术结论**：工具调用是**双轮请求机制**——模型仅负责"选择与参数化"，实际执行由应用侧完成，体现了推理引擎与应用的责任解耦边界。

**3) 与文档关系**：图中交互顺序与文档"流程步骤"1-5一一对应，补充了"OpenAI chat接口、MindIE Rest API"等具体实现细节，强化了"模型不能直接执行工具，仅返回结构化指令"的论点。
