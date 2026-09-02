# FSDP2框架支持Agentic SFT

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/agentic_sft.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/agentic_sft.md

# 一体化深度解读：FSDP2框架支持Agentic SFT

## 【定位】

本文档描述 mindspeed-mm 在 FSDP2 分布式训练框架下，对具备工具调用能力的多模态模型进行"Agentic SFT（监督微调）"的支持方案——使模型学会理解用户意图、调用外部工具并基于工具返回结果进行多轮对话回复。

---

## 【技术要点】

1. **核心训练目标**：在多轮对话上下文中联合训练"用户意图理解 + 工具调用决策 + 工具结果处理"三项能力，让模型不仅能回答问题，还能主动发起外部函数调用并消化返回结果。
2. **数据格式契约**：采用 JSON 结构，每条样本以 `messages` 列表承载对话历史，并可选携带 `audios` / `images` / `videos` 多模态文件路径与 `tools`（工具 schema 列表）。
3. **角色顺序硬约束**：`tool_call` 与 `tool_response` 必须成对出现，且严格遵循 `user → tool_call → tool_response → assistant` 的交替顺序，未配对的工具调用会导致数据被跳过。
4. **工具定义注入机制**：`tools` 字段中的工具 schema 可被注入到系统提示中，使模型在训练/推理时获知当前可用的工具能力集；通过 `tool_prompt = StringFormatter(slots=[tools_slot])` 的模板注册方式扩展其它模板。
5. **格式转换器开关**：在数据配置中需将 `formatting` 设为 `multimodal_tool`，这是触发 Agentic SFT 数据处理路径的唯一入口。
6. **模板与模型矩阵**：当前官方推荐组合为 Qwen3.5（`qwen3_vl_nothink` 模板）与 Qwen3Omni（`qwen3_omni_nothink` 模板），均为已完整支持工具调用格式的 nothink 版本。

---

## 【关键机制与数据】

**工作原理（数据流视角）**：

1. 原始 JSON 样本进入 dataloader 后，由 `multimodal_tool` 格式转换器解析。
2. 转换器读取 `messages` 中的 `role`/`content`，对 `tool_call` 内容中的特殊标记（如示例中的 `<tool_call>{...}</tool_call>`）进行结构化解析，对 `tool_response` 的 JSON 字符串结果进行标准化。
3. 校验环节遍历 messages，若发现孤立的 `tool_call`（无后续 `tool_response` 匹配）或孤立 `tool_response`，整条样本被丢弃。
4. 若样本包含 `tools` 字段，则将其按 OpenAI function-calling 风格的 schema 注入到 system prompt 之前/之后（具体由模板中的 `tools_slot` 决定）。
5. 多模态字段（`audios`/`images`/`videos`）通过原 FSDP2 多模态管线加载，与对话文本在同一序列中拼接送入模型，完成"看/听 + 调用工具 + 回复"的端到端联合训练。

**原文数据示例（智能客服疫苗预约场景）**：

- 对话轮次：包含 8 轮 user-assistant 交替 + 1 组 tool_call/tool_response。
- 工具调用：`{"name": "register_vaccine_appointment", "arguments": {"appointment_time": "周三下午三点"}}`。
- 工具响应：`{"status": "success", "message": "预约成功"}`。
- 多模态字段：`audios = "/speeches/7_Katerina.wav"`（一条语音）。
- 工具 schema：`register_vaccine_appointment` 定义了字符串类型必填参数 `appointment_time`。

**性能数据**：原文未涉及性能基准、吞吐量、显存占用等数值。

---

## 【表格解读】

原文存在一张关键表格——`messages` 字段中各 `role` 取值含义表。逐字还原如下：

| role 值 | 含义 | 说明 |
|---------|------|------|
| `system` | 系统提示 | 定义助手的角色和行为规范，通常位于messages首位 |
| `user` | 用户输入 | 用户的提问或请求 |
| `assistant` | 助手回复 | 模型的回复内容 |
| `tool_call` | 工具调用 | 模型发起的工具调用请求，使用特殊格式 |
| `tool_response` | 工具响应 | 外部工具返回的结果 |

**逐行解读**：

- **`system` 行**：是整段对话的"角色宣告 + 行为规范"承载位，原文示例中通过"你是专业、高效的AI智能客服。当前对话的时间为..."明确身份与时间锚点；表格提示它"通常位于messages首位"，但并未禁止在其他位置出现。
- **`user` 行**：表示来自真实用户的输入，支持纯文本，也可承载多模态引用（如示例中的 `<audio>` 占位符，对应 `audios` 字段）。
- **`assistant` 行**：表示模型自身的回复；该角色在示例中频繁出现，承担"无工具调用时的直接回答"与"接收到 tool_response 后的二次总结"两种职能（后者对应示例最后一段"好的，已经为您登记了周三下午三点的接种时间……"）。
- **`tool_call` 行**：是模型"主动发起外部调用"的标识位；"使用特殊格式"指示例中 `<tool_call>{...}</tool_call>` 这类带定界符的 JSON 序列化方式，便于格式转换器解析函数名与参数。
- **`tool_response` 行**：承接外部工具的真实输出，原文示例中以 `{"status": "success", "message": "预约成功"}` 形式呈现；该值会被模型在下一轮 `assistant` 回复中作为事实依据引用。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未提供内部链接（无超链接指向其他特性或模块文档）。从内容可推断的上下游/横纵关系如下：

- **上游（数据侧）**：依赖 FSDP2 框架原有的多模态数据集加载管线（`audios` / `images` / `videos` 文件加载逻辑），本特性在其上叠加 `multimodal_tool` 格式转换器与 `tools` schema 注入。
- **下游（模型侧）**：消费方为 Qwen3.5（VL 多模态）与 Qwen3Omni（音视频全模态）模型系列；二者分别通过 `qwen3_vl_nothink` 与 `qwen3_omni_nothink` 模板承载工具调用格式。
- **横向（与其它 Agentic 能力的关系）**：本特性专注于"训练阶段"的工具调用监督微调，与推理阶段的工具调度、Agent 编排等能力属于上下游分离关系——文档未做交叉引用。

---

## 【使用方法】

**数据配置（YAML）**：

```yaml
data:
  dataset_param:
    attr:
      formatting: multimodal_tool  # 使用 multimodal_tool 格式转换器

    basic_parameters:
      template: qwen3_vl_nothink  # 推荐使用 qwen3_vl_nothink 或 qwen3_omni_nothink 模板
      # 如需使用其他模板，可参照 qwen3_vl_nothink 的模板注册代码进行传参 tool_prompt = StringFormatter(slots=[tools_slot])
```

**模型与模板对照**：

| 模型 | 推荐模板 |
|------|----------|
| Qwen3.5 | `qwen3_vl_nothink` |
| Qwen3Omni | `qwen3_omni_nothink` |

**启用步骤（基于原文整理）**：

1. 按上述 JSON Schema 准备训练数据，确保 `messages` 中 `tool_call` 与 `tool_response` 成对出现，并按 `user → tool_call → tool_response → assistant` 顺序排列。
2. 若需将工具能力告知模型，按 OpenAI function-calling 规范填写 `tools` 字段（参考示例中的 `register_vaccine_appointment`）。
3. 在训练配置中将 `data.dataset_param.attr.formatting` 设置为 `multimodal_tool`。
4. 在 `data.dataset_param.basic_parameters.template` 中选择 `qwen3_vl_nothink`（Qwen3.5）或 `qwen3_omni_nothink`（Qwen3Omni）。
5. 若要扩展其它模板，按注释提示传入 `tool_prompt = StringFormatter(slots=[tools_slot])`。
6. 直接复用现有 FSDP2 训练启动命令启动训练，无需额外开关——原文明确"兼容现有FSDP2训练流程，无需额外配置即可启用"。

**原文未涉及**：具体启动命令（如 `torchrun`/`mm_run` 等）、超参与优化器配置、分布式并行度设置、checkpoint 与日志配置。
