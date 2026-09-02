# 思考预算

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/thinking_budget.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/thinking_budget.md

# 思考预算（thinking_budget）文档深度解读

## 【定位】

这篇文档描述了 MindIE LLM 推理引擎的"思考预算"特性，用于控制具备思维链（CoT）输出能力的大模型的思考深度——当模型生成的思考内容超过用户设定的 `thinking_budget` 时，系统通过注入结束提示词强制截断思考过程，从而在响应速度与答案质量之间实现灵活权衡。

---

## 【技术要点】

1. **支持硬件（3 类）**：Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器、Atlas 300I Duo 推理卡。
2. **支持模型（3 个）**：Qwen3-32B、Qwen3-235B-A22B、Qwen3-30B-A3B。
3. **接口范围**：当前仅支持 OpenAI 推理接口。
4. **请求侧参数**：在请求中传入 `"chat_template_kwargs": {"thinking_budget": <uint32_t>}`，取值范围为 `[1, MAX_UINT32_T]`。
5. **服务侧配置**：在 Server 的 `config.json` 的 `ModelConfig.models` 中配置 `early_stopping_text` 字段，类型为 string，长度范围 `[1, 1024]`，用于在思考超出预算时截断思考过程。
6. **互斥约束**：该特性暂不支持与 `use_beam_search` 等多序列推理相关的后处理参数同时开启。

---

## 【关键机制与数据】

**工作原理（原文）：** "当思考内容超过设定的 thinking\_budget 时，系统会使用提示词对思考过程进行截断，促使模型提前结束思考。"

**关键数据流（原文）：**
- 请求阶段：客户端在 OpenAI 接口的请求体中通过 `chat_template_kwargs.thinking_budget` 声明思考长度上限。
- 服务阶段：服务端通过 `config.json` 中 `ModelConfig.models.<model_key>.early_stopping_text` 预设截断提示词原文。
- 截断阶段：模型输出思考 token 累计达到 `thinking_budget` 时，推理引擎将该提示词注入生成上下文，引导模型输出 `` 等结束标记，跳过剩余思考直接产出最终答案。

**已观察的副作用（原文）：** "在 thinking\_budget 设置过低的情况下，推理结果有概率切换到与提示词相同的语言。"——即低预算截断可能引入与提示词语言对齐的偏置。

**性能数据**：原文未给出 token 数、时延、吞吐量等量化指标。

---

## 【表格解读】

**表 1  思考预算特性补充参数：ModelConfig 中的 models 参数**

| 配置项 | 取值类型 | 长度范围 | 配置说明 |
|---|---|---|---|
| `early_stopping_text` | string | [1, 1024] | 结束思考提示词。<br>开启 `thinking_budget` 后，当模型思考输出超过预算后使用该提示词进行截断。<br>不同模型提示词不同，qwen 系列模型提示词参考下面的参数配置示例。 |

**逐行解读：**
- **配置项 `early_stopping_text`**：截断提示词的字面文本，是该特性在服务端唯一的可配置项，决定了模型被截断后看到的"终止指令"内容。
- **取值类型 string**：纯文本字符串，而非枚举或数值，原因是提示词内容需与目标模型训练时所用的截断模式对齐。
- **长度范围 [1, 1024]**：最少 1 字符（最少需含 `` 之类闭合标记），上限 1024 字符，避免过长提示词挤占推理上下文。
- **配置说明三要点**：
  1. 触发条件：仅在 `thinking_budget` 开启且思考输出超限时生效；
  2. 作用机制：以注入提示词方式截断思考过程（见前文工作机制）；
  3. 模型差异：`qwen` 系列各模型的最佳提示词不同，文档以下方的 Qwen3-32B 示例为准；Qwen3-30B-A3B 因 MoE 结构差异，配置时将 `models` 键名由 `qwen3` 改为 `qwen3_moe`。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **`../user_manual/service_parameter_configuration.md`**（内部链接，文档正文引用）：服务化参数的完整说明章节，`early_stopping_text` 作为新增的 `ModelConfig.models` 字段，其取值范围、配置位置及生效方式在该章节中有体系化的对照说明。
- **上游接口对接**：《MindIE LLM 开发指南》中"服务化接口使用指导"章节负责说明 `chat_template_kwargs.thinking_budget` 在 OpenAI 请求体中的传参方式。
- **服务启动流程**：PD 混部与 PD 分离两种部署模式分别在《MindIE Motor 开发指南》的"快速入门 > 启动服务"与"集群服务部署 > PD 分离服务部署"章节中给出，文档将其作为启用该特性的前置步骤。
- **互斥特性**：`use_beam_search` 等多序列推理相关后处理参数与该特性冲突，二者不能在同一请求中同时启用。

---

## 【使用方法】

1. **编辑 Server 配置**（whl 包方式）：
   ```bash
   cd {MindIE安装目录}/mindie_llm/
   vi conf/config.json
   ```
   （run 包方式：`cd {MindIE安装目录}/latest/mindie-service` 后编辑同路径配置文件）

2. **添加 `early_stopping_text` 字段**（以 Qwen3-32B 为例）：
   ```json
   "models": {
       "qwen3": {"early_stopping_text": "\n\nConsidering the limited time by the user, I have to give the solution based on the thinking directly now.\n\n\n"}
   }
   ```
   - Qwen3-30B-A3B 模型需将键名 `"qwen3"` 改为 `"qwen3_moe"`；
   - 配置位置为 `ModelConfig.models` 之下，需配合 `modelName`、`modelWeightPath` 等其它模型部署参数共同设置。

3. **启动服务**：根据部署模式参考《MindIE Motor 开发指南》中 PD 混部或 PD 分离章节。

4. **发起推理请求**：在 OpenAI 兼容请求中携带 `chat_template_kwargs.thinking_budget` 字段，值域 `[1, MAX_UINT32_T]`；请求格式详见《MindIE LLM 开发指南》"服务化接口使用指导"章节。
