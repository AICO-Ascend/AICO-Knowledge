# Reasoning Outputs

> 仓 `vllm` · 路径 `docs/features/reasoning_outputs.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/reasoning_outputs.md

# 推理输出 (Reasoning Outputs) 文档深度解读

## 【定位】
本文档系统描述 vLLM 对"推理模型"(如 DeepSeek R1 这类会同时输出"思考过程"与"最终结论"的模型)的端到端支持能力——从输出字段约定、解析器选型、流式响应、到与工具调用的协同——为开发者提供将思考链路集成到 OpenAI 兼容 API 客户端的完整指南。

---

## 【技术要点】

1. **新增 `reasoning` 字段**: 推理模型在原有 `content` 之外多返回一个 `reasoning` 字段,承载推导步骤;此字段在其他普通模型的输出中**不存在**(原文: "This field is not present in the outputs of other models.")。
2. **字段重命名迁移**: 历史上 `reasoning` 曾叫 `reasoning_content`,迁移只需直接替换字符串,且需同步更新客户端代码,否则会出现"静默读到空 `reasoning_content` 但 `reasoning` 实际有值"的陷阱(原文 warning 段落)。
3. **`--reasoning-parser` 启动参数**: 通过 `vllm serve` 指定解析器,从模型原始输出中切分推理内容。例:`vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --reasoning-parser deepseek_r1`。
4. **多解析器适配多模型族**: 共支持 13 条模型系列,对应 `deepseek_r1` / `qwen3` / `granite` / `glm45` / `gemma4` 等不同 Parser Name;其中 QwQ-32B 复用 `deepseek_r1` 解析器。
5. **差异化开关 (chat_template_kwargs)**:
   - IBM Granite 3.2、DeepSeek-V3.1、Gemma 4 默认关闭推理 → 用 `thinking=True` / `enable_thinking=True` / 或 `reasoning_effort` 开启;
   - Qwen3 默认开启 → 用 `enable_thinking=False` 关闭;
   - Holo2 默认开启 → 用 `thinking=False` 关闭。
6. **工具调用与推理解耦**: 工具调用仅从 `content` 字段解析函数定义,**不解析** `reasoning` 字段(原文: "tool calling only parses functions from the `content` field, not from the `reasoning`.")。
7. **流式 chunk 中 `reasoning` 走 `delta`**: 与 OpenAI `chat.completion.chunk.choices[0].delta` 结构对齐;客户端需用 `getattr(chunk.choices[0].delta, "reasoning", None)` 安全访问,因为 OpenAI Python 客户端官方未支持该字段。

---

## 【关键机制与数据】

### 工作原理 (原文表述)
- **解析器机制**: `--reasoning-parser` 标志决定使用哪个解析器,**从模型输出中提取**推理内容,把模型的混合输出切分为 `reasoning`(推导步骤)与 `content`(最终结论)两部分再回传给客户端。
- **字段语义**: "`reasoning` field contains the reasoning steps that led to the final conclusion, while the `content` field contains the final conclusion."
- **数据流(流式)**:
  - 原始模型以流式增量产出 token → 解析器实时切分 → 封装进 OpenAI 兼容 chunk 的 `delta` 字段 → 客户端按顺序累积打印(代码中 `printed_reasoning` / `printed_content` 两个标志位确保只打一次前缀)。
- **跨版本兼容性陷阱**: 若客户端代码未同步迁移,可能"silently read an empty `reasoning_content`, even when `reasoning` is populated"——这是因为旧字段始终为空、新字段才有内容。
- **DeepSeek-V3.1 特殊行为**: 工具调用仅在 **non-thinking 模式**下支持(原文 note 第四条)。
- **性能数据**: 原文未提供任何性能基准数字(吞吐、延迟、首 token 时延等),故此处不臆造。

### 流式 chunk 字段位置
原文示例 JSON 显示: `choices[0].delta.reasoning` 携带增量推理文本(例值为 `"is"`),与 `role` 字段并列出现在 `delta` 对象中,`finish_reason` 此时为 `null`。

---

## 【表格解读】

**原文表格(逐字还原)**——Supported Models:

| Model Series | Parser Name | Structured Output Support | Tool Calling |
| ------------ | ----------- | ---------------- | ----------- |
| [Cohere Command A Reasoning](https://huggingface.co/CohereLabs/command-a-reasoning-08-2025) | `cohere_command3` | `json`, `regex` | ✅ |
| [DeepSeek R1 series](https://huggingface.co/collections/deepseek-ai/deepseek-r1-678e1e131c0169c0bc89728d) | `deepseek_r1` | `json`, `regex` | ❌ |
| [Gemma 4 series](https://huggingface.co/google/gemma-4-26B-A4B-it) | `gemma4` | `json`, `regex` | ✅ |
| [DeepSeek-V3.1](https://huggingface.co/collections/deepseek-ai/deepseek-v31-68a491bed32bd77e7fca048f) | `deepseek_v3` | `json`, `regex` | ❌ |
| [ERNIE-4.5-VL series](https://huggingface.co/baidu/ERNIE-4.5-VL-28B-A3B-PT) | `ernie45` | `json`, `regex` | ❌ |
| [ERNIE-4.5-21B-A3B-Thinking](https://huggingface.co/baidu/ERNIE-4.5-21B-A3B-Thinking) | `ernie45` | `json`, `regex` | ✅ |
| [GLM-4.5 series](https://huggingface.co/collections/zai-org/glm-45-687c621d34bda8c9e4bf503b) | `glm45` | `json`, `regex` | ✅ |
| [Holo2 series](https://huggingface.co/collections/Hcompany/holo2) | `holo2` | `json`, `regex` | ✅ |
| [Hunyuan A13B series](https://huggingface.co/collections/tencent/hunyuan-a13b-685ec38e5b46321e3ea7c4be) | `hunyuan_a13b` | `json`, `regex` | ✅ |
| [IBM Granite 3.2 language models](https://huggingface.co/collections/ibm-granite/granite-32-language-models-67b3bc8c13508f6d064cff9a) | `granite` | ❌ | ❌ |
| [MiniMax-M2](https://huggingface.co/MiniMaxAI/MiniMax-M2) | `minimax_m2_append_think` | `json`, `regex` | ✅ |
| [Qwen3 series](https://huggingface.co/collections/Qwen/qwen3-67dd247413f0e2e4f653967f) | `qwen3` | `json`, `regex` | ✅ |
| [QwQ-32B](https://huggingface.co/Qwen/QwQ-32B) | `deepseek_r1` | `json`, `regex` | ✅ |

**逐行解读**:

- **Cohere Command A Reasoning**: 使用专有解析器 `cohere_command3`,支持 JSON 与正则结构化输出,并兼容工具调用(✅)。
- **DeepSeek R1 series**: 解析器即本文档示例所用的 `deepseek_r1`,支持结构化输出,但**不支持**工具调用(❌)。
- **Gemma 4 series**: 解析器 `gemma4`,支持结构化输出与工具调用;默认关闭推理,需 `enable_thinking=True` 或 `reasoning_effort` 启用。
- **DeepSeek-V3.1**: 解析器 `deepseek_v3`,支持结构化输出但**不支持**工具调用(原文 note 注明:仅在 non-thinking 模式才支持工具调用,与表格 ❌ 看似冲突,需结合上下文理解——表格是基线状态,note 是配置补充)。
- **ERNIE-4.5-VL series**: 解析器 `ernie45`,支持结构化输出,不支持工具调用。
- **ERNIE-4.5-21B-A3B-Thinking**: 同样使用 `ernie45` 解析器,与 ERNIE-4.5-VL 共享解析器实现,但额外支持工具调用。
- **GLM-4.5 series**: 解析器 `glm45`,三项能力全部具备。
- **Holo2 series**: 解析器 `holo2`,全部支持;默认开启推理,可用 `thinking=False` 关闭。
- **Hunyuan A13B series**: 解析器 `hunyuan_a13b`,全部支持。
- **IBM Granite 3.2 language models**: 解析器 `granite`,**结构化输出与工具调用皆不支持**,且默认关闭推理,需 `thinking=True` 启用——是表格中最受限的一档。
- **MiniMax-M2**: 解析器 `minimax_m2_append_think`(命名暗示采用"追加 think 标记"策略),支持结构化输出与工具调用。
- **Qwen3 series**: 解析器 `qwen3`,全部支持;默认开启推理,可用 `enable_thinking=False` 关闭。
- **QwQ-32B**: 解析器复用 `deepseek_r1`,说明该模型输出格式与 DeepSeek R1 同源,工程上可走同一解析管线。

**共性观察**: 大多数模型同时支持 `json` 与 `regex` 两种结构化输出;真正不支持工具调用的只有 DeepSeek R1 series、DeepSeek-V3.1、ERNIE-4.5-VL series 与 IBM Granite 3.2 四款。

---

## 【公式解读】

原文无数学公式或伪代码公式。文档中出现的"代码公式"仅为启动命令与客户端调用片段,已在【使用方法】节中转写。

---

## 【关联】

- **上游 API 契约**: 与 OpenAI Chat Completions API 兼容(`chat.completions.create`、流式 chunk 结构、`delta` 字段命名),遵循 OpenAI 平台文档(链接: `https://platform.openai.com/docs/api-reference/chat/streaming`)。
- **下游解析器实现**: `vllm/reasoning/deepseek_r1_reasoning_parser.py`(内部链接重复两次,即此文件)实现 `deepseek_r1` 解析器;QwQ-32B 复用此解析器,意味着 QwQ 与 DeepSeek R1 共享同一段切分逻辑。
- **示例代码**: `examples/reasoning/openai_chat_completion_tool_calls_with_reasoning.py` 演示在工具调用场景下同时获取 `reasoning` 与 `content` 的写法(文末提到的 tool calling 章节对应此示例)。
- **流式示例**: `examples/reasoning/openai_chat_completion_with_reasoning_streaming.py`(GitHub 链接,文档内引用)展示流式消费 `delta.reasoning` 的模式。
- **配套特性**: 与"Tool Calling"模块强耦合——本文档单独用一节说明推理与工具调用同时启用时的字段边界(只解析 `content` 中的函数定义)。
- **结构化输出**: 表格第三列"Structured Output Support"与 vLLM 的结构化输出(guided JSON / guided regex)机制对齐,但本文档未展开其配置细节。

---

## 【使用方法】

### 服务端启动(原文 Quickstart)
```bash
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
    --reasoning-parser deepseek_r1
```
`--reasoning-parser` 取值需与表格中的 Parser Name 一致(`deepseek_r1` / `qwen3` / `granite` / `glm45` / `gemma4` / `deepseek_v3` / `ernie45` / `holo2` / `hunyuan_a13b` / `minimax_m2_append_think` / `cohere_command3`)。

### 非流式调用
通过 `client.chat.completions.create(...)` 发起请求,访问路径:
```python
response.choices[0].message.reasoning   # 推导步骤
response.choices[0].message.content    # 最终结论
```

### 流式调用
在请求参数中加入 `stream=True`,在每个 chunk 中通过 `getattr(chunk.choices[0].delta, "reasoning", None)` 安全读取,需先判断是否非空再打印(原文代码示例展示了 `printed_reasoning` / `printed_content` 标志位模式)。

### 按模型族启用/关闭推理(原文 note)
- **Granite / DeepSeek-V3.1 / Holo2**: `extra_body={"chat_template_kwargs": {"thinking": True/False}}`
- **Qwen3**: `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` (默认开启,此参数关闭)
- **Gemma 4**: `extra_body={"chat_template_kwargs": {"enable_thinking": True}}` 或设置 `reasoning_effort`(自动启用)

### 工具调用叠加(原文 Tool Calling 节)
在 `chat.completions.create` 中传入 `tools=[...]` 参数;注意函数定义只能从 `content` 字段被识别,`reasoning` 字段中的工具调用信号会被忽略。完整示例见 `examples/reasoning/openai_chat_completion_tool_calls_with_reasoning.py`。

### 迁移提示
若从早期 vLLM 版本升级,需把客户端代码中的 `reasoning_content` 全局替换为 `reasoning`,否则会出现"静默读到空值"的兼容问题。
