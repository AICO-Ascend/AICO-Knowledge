# 结构化输出（Structured Output）

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/structured_output.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/structured_output.md

# 结构化输出（Structured Output）文档深度解读

---

## 【定位】

这篇文档描述 MindIE LLM 提供的**约束解码（constrained decoding）特性**：在推理阶段对模型输出做 token 级格式约束，使其严格符合用户指定的 JSON / JSON Schema 形态，从而把模型输出直接变成下游系统可解析的结构化数据，解决"模型自由生成导致格式不可控、需后处理清洗"的问题。

---

## 【技术要点】

- **后端选型**：约束后端为 **xgrammar**——原文描述其为「基于 FSM 的高性能 token 约束库」，通过有限状态机在每一步解码时屏蔽不符合目标的 token。
- **三种输出模式**：`json_object`（通用 JSON 对象）、`json_schema`（用户指定 Schema）、`text`（不启用结构化输出，回退到自然语言）。
- **接入方式**：完全复用 OpenAI 兼容接口的 `response_format` 参数，无需在 `config.json` 中单独配置插件——只要请求里带 `response_format` 就自动启用。
- **接口端点**：支持 `POST /v1/chat/completions` 与 `POST /v1/completions` 两个 OpenAI 风格端点。
- **覆盖能力**：支持 **PD 混部、PD 分离**两种部署形态；可与 **splitFuse、prefix_caching** 叠加使用；**不可与 MTP、投机推理叠加**。
- **响应字段**：示例响应中 `usage` 包含 `prompt_tokens`、`completion_tokens`、`total_tokens`、`reasoning_tokens`、`cached_tokens` 等标准 OpenAI 计费字段，`finish_reason` 为 `stop`。

---

## 【关键机制与数据】

**工作原理（原文整合推断，不外添）：**

1. **触发**——客户端在请求体里塞入 `response_format` 字段，服务端识别后激活约束解码流水线。
2. **建图**——基于 `response_format.type`：
   - `text`：不激活，按自然语言路径生成。
   - `json_object`：构造"任意合法 JSON"对应的 token FSM。
   - `json_schema`：解析用户传入的 `json_schema.schema` 对象，编译为对应的 JSON Schema FSM。
3. **逐 token 约束**——推理阶段每一步采样前，FSM 根据当前已生成的 token 序列给出**合法 token 集合**，对 logits 做掩码后再采样，从而保证输出始终落在合法空间内。
4. **终止**——FSM 到达接受态（如完整闭合的 `}`）即正常结束，示例中 `finish_reason` 为 `stop`。

**请求/响应关键数据（原文示例）：**

- **json_object 模式示例请求**：`max_tokens=256`、`stream=false`、模型名 `dsv3_w8a8`、提示词要求抽取"张三，28岁，软件工程师，北京"为 JSON。
- **json_object 响应示例**：`completion_tokens=35`、`total_tokens=57`、`prompt_tokens=22`，输出内容为 `{"name": "Zhang San", "age": 30, "gender": "male", ...}`（注意：原文响应中输出字段含 `gender`、`workplace` 而 prompt 中并未提供——这印证了文档强调的"该模式仅保证输出为合法 JSON，不保证键名/类型受控"）。
- **json_schema 模式示例请求**：定义 `person_info` schema，必填字段为 `["name", "age", "occupation", "city", "phone"]`；响应严格按这 5 个键输出，且 `age=35`、`city="上海"` 与 prompt 中"李四，35岁，产品经理，上海"完全一致。

**性能/规模数据**：原文未给出吞吐量、延迟、显存占用等量化数据。

---

## 【表格解读】

### 表 1：功能特性总览

| 特性 | 说明 |
|------|------|
| 约束后端 | xgrammar（基于 FSM 的高性能 token 约束库） |
| 支持格式类型 | `json_object`（通用 JSON 对象）、`json_schema`（用户指定 Schema）、`text`（不启用结构化输出，以自然语言返回） |

**解读**：这是特性能力边界表。一行锁定后端技术栈（xgrammar/FSM），一行锁定用户可选的三种"严格度"——`text` 关闭特性、`json_object` 约束最弱、`json_schema` 约束最强。

### 表 2：`json_object` 类型 `response_format` 字段

| 字段 | 类型 | 是否必填 | 说明 |
|------|------|----------|------|
| `type` | string | 必填 | 固定值 `"json_object"` |

**解读**：极简结构——只需声明 `type="json_object"` 即可启用，**没有任何额外参数**。这意味着用户无法在请求里直接指定 schema，约束粒度仅为"输出是合法 JSON 对象"。

### 表 3：`json_schema` 类型 `response_format` 字段

| 字段 | 类型 | 是否必填 | 说明 |
|------|------|----------|------|
| `type` | string | 必填 | 固定值 `"json_schema"` |
| `json_schema` | object | 必填 | Schema 描述对象 |
| `json_schema.name` | string | 必填 | Schema 名称（非空字符串，用于标识） |
| `json_schema.schema` | object | 可选 | 标准 JSON Schema 对象；不填时默认约束为通用 JSON 对象 |

**解读**：典型的"信封 + 信封内层"双层结构。`name` 是标识符（非空字符串，作用类似日志/调试时的句柄）；`schema` 不填则退化为 `json_object` 的行为，这给了用户"想约束就传 schema，不想约束就只传 type"的渐进式用法。

### 表 4：`json_schema.schema` 支持的 JSON Schema 关键字

| 关键字 | 说明 |
|--------|------|
| `type` | 数据类型：`object`、`array`、`string`、`integer`、`number`、`boolean`、`null` |
| `properties` | 对象属性定义（`type: object` 时使用） |
| `required` | 必填属性列表 |
| `items` | 数组元素类型定义（`type: array` 时使用） |
| `enum` | 枚举值列表 |
| `description` | 属性描述（不影响约束，仅用于说明） |
| `additionalProperties` | 是否允许额外属性，默认 `false` |

**解读**：覆盖了 JSON Schema 规范的一个**常用子集**而非全集。约束类关键字（`type` / `properties` / `required` / `items` / `enum` / `additionalProperties`）真正参与 FSM 构建；而 `description` 明确标注为"不影响约束"——这与 json_schema 模式下 `description` 字段填中文（"人员姓名"）的示例一致，提示词中可读、约束时不参与。`additionalProperties` 默认 `false` 是关键安全默认：默认拒绝未声明字段，避免模型"自由发挥"出未定义键。

---

## 【公式解读】

原文无公式。

（约束解码的数学本质是"在每一步把词表 V 投影到 FSM 接受态可达集 A(s) ⊆ V 上，并对 logits 做 mask：logits'[v] = logits[v] if v ∈ A(s) else -∞"，但该式未在原文中出现，故不补写。）

---

## 【关联】

文档在「限制与注意事项」一节明确划定了结构化输出与其他特性的**相容矩阵**：

- **可叠加（正向依赖）**：
  - **splitFuse**：将长 prompt 切分到 prefill / decode 阶段的调度策略，与结构化输出在解码侧的 token 掩码不冲突。
  - **prefix_caching**：KV cache 复用以加速 prompt，与结构化输出的 FSM 状态机在每步独立运行不冲突。
  - **PD 混部 / PD 分离**：Prefill-Decode 同卡或分卡的部署形态，结构化输出在 decode 阶段生效，两者解耦。
- **不可叠加（互斥）**：
  - **MTP（Multi-Token Prediction）**：一次预测多 token 的机制，与"逐 token FSM 约束"的粒度冲突。
  - **投机推理（speculative inference）**：先草拟多 token 再验证，同样会破坏逐 token 约束的合法性。

文档还提示参数详细说明位于《MindIE Motor开发指南》中的「服务化接口 \> EndPoint业务面RESTful接口 \> 兼容OpenAI接口 \> 推理接口」章节，说明该特性是 MindIE Motor 服务化层 OpenAI 兼容能力的一部分。

---

## 【使用方法】

### 启用方式

无需在 `config.json` 中为本特性单独配置插件——**只要请求中携带 `response_format` 参数，结构化输出即自动启用**。

### 启动服务

```bash
cd {MindIE安装目录}/latest/mindie-service/
./bin/mindieservice_daemon
```

### 发送请求

- 端点：`POST http://{ip}:{port}/v1/chat/completions` 或 `POST http://{ip}:{port}/v1/completions`
- Content-Type：`application/json`
- `response_format` 用法：
  - **`json_object`**：`{"type": "json_object"}`——只保证合法 JSON。
  - **`json_schema`**：`{"type": "json_schema", "json_schema": {"name": "<标识>", "schema": {<标准 JSON Schema 对象>}}}`——按 schema 约束字段、类型、枚举、必填项。

### 配置项

原文未涉及独立配置项（开关完全由请求体 `response_format` 字段决定；后端固定为 xgrammar，文档未提及替换或调参方式）。
