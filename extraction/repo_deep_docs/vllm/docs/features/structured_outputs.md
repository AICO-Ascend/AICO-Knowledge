# Structured Outputs

> 仓 `vllm` · 路径 `docs/features/structured_outputs.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/structured_outputs.md

# vLLM Structured Outputs 文档深度解读

## 【定位】
本文档系统介绍 vLLM 如何通过 [xgrammar](https://github.com/mlc-ai/xgrammar) 或 [guidance](https://github.com/guidance-ai/llguidance) 等后端,把大模型的生成输出约束为符合预定义结构(JSON Schema、正则、上下文无关文法、枚举选项等)的合规文本,服务于 OpenAI 兼容 API 场景下"模型输出即程序可消费数据"的需求。

---

## 【技术要点】

1. **后端选型**:文档明示支持 `xgrammar` 和 `guidance` 两类结构化生成后端;同时提及历史可用的 `outlines`、`lm-format-enforcer` 在正则语法上存在差异(Rust-style regex vs Python `re`)。
2. **六种结构化参数**:`choice`、`regex`、`json`、`grammar`、`structural_tag`、`whitespace_pattern`,均通过 `extra_body={"structured_outputs": {...}}` 或 `StructuredOutputsParams(...)` 传入。
3. **API 入口**:OpenAI 兼容 Server 默认启用结构化输出;可在 `vllm serve` 时通过 `--structured-outputs-config.backend` 指定后端,默认值为 `auto`。
4. **JSON 两种入口**:既可直接传 JSON Schema,也可由 Pydantic 模型经 `model_json_schema()` 派生;在 OpenAI Chat API 中通过 `response_format={"type":"json_schema", "json_schema":{...}}` 传入。
5. **推理模型集成**:与 reasoning 配合时,启动命令形如 `vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --reasoning-parser deepseek_r1`;`reasoning` 与 `content` 在返回消息中分离。
6. **Qwen3 Coder 特殊处理**(v0.11.2+):reasoning 开启时若 reasoning 内容未分离到独立字段,结构化输出可能被自动禁用,需显式加上 `--structured-outputs-config.enable_in_reasoning=True`。
7. **废弃字段映射**:v0.12.0 起移除 `guided_json`、`guided_regex`、`guided_choice`、`guided_grammar`、`guided_whitespace_pattern`、`structural_tag`、`guided_decoding_backend`,统一收敛到 `structured_outputs` 命名空间。

---

## 【关键机制与数据】

- **原文:** "Structured outputs are supported by default in the OpenAI-Compatible Server." —— 即不需要额外启用开关,默认即开。
- **原文:** 默认 backend 为 `auto`,会按请求细节自动挑选后端;也可手动指定并附加后端级选项(完整列表位于 `vllm serve --help`)。
- **原文:** regex 语法依后端而异 —— `xgrammar` / `guidance` / `outlines` 使用 Rust-style regex,`lm-format-enforcer` 使用 Python `re` 模块。
- **原文:** JSON 场景下"在 prompt 中显式给出 schema 与字段填写说明"通常能显著改善效果(非强制)。
- **原文:** "any provided structured outputs feature" 都可与 reasoning 共用,JSON Schema 与 reasoning 联用即给出 `People(name, age)` 样例。
- **原文:** Experimental Automatic Parsing 部分注明所用 OpenAI 客户端版本为 `openai==1.54.4`,并给出 OpenAI 官方代码行号定位 `openai-python@52357cff`(聊天 completions.py L100-L104)。
- **原文:** 实验性自动解析章节所用模型示例为 `meta-llama/Llama-3.1-8B-Instruct`。
- **性能/数据流细节**:原文未给出量化指标(如时延、吞吐、token 接受率等),仅描述接口形态与示例代码。

---

## 【表格解读】

**原文无表格。**

文档以代码片段与列表形式呈现参数与示例,未出现结构化的参数对照表或性能对比表。

---

## 【公式解读】

**原文无数学公式。**

文档中存在一段 EBNF 文法定义(非数学公式,此处仅作为"grammar 参数用法"的辅助说明):

```
root ::= select_statement
select_statement ::= "SELECT " column " from " table " where " condition
column ::= "col_1 " | "col_2 "
table ::= "table_1 " | "table_2 "
condition ::= column "= " number
number ::= "1 " | "2 "
```

含义解读(原文仅作为 `grammar` 参数的示例使用,文档未赋予其额外公式含义):
- `root` —— 文法起点,所有合法输出必须从 `root` 推导而出。
- `select_statement` —— 一条 SELECT 语句模板,字面量 `"SELECT "` / `" from "` / `" where "` 作为固定串,`column` / `table` / `condition` 为非终结符占位。
- `column` / `table` —— 限定列名(`col_1` / `col_2`)与表名(`table_1` / `table_2`)。
- `condition` —— 等值条件,`column "= " number` 即"列名 = 数字"。
- `number` —— 数字字面量,限定为 `"1 "` 或 `"2 "`(带尾随空格,贴合英文 token 习惯)。

---

## 【关联】

依据文中明确出现的内部链接,文档与以下模块/示例相互引用:

| 关联对象 | 关系性质 | 出处上下文 |
|---|---|---|
| [OpenAI-Compatible Server](../serving/online_serving/openai_compatible_server.md) | 上游能力定义页 —— 列出 `structured_outputs` 全部支持的 extra 参数 | "You can see the complete list of supported parameters on the [OpenAI-Compatible Server] page" |
| [full example](../../examples/features/structured_outputs/README.md) | 在线 serving 示例总入口 | "See also: [full example]" 出现两次(grammar 段落、reasoning 段落) |
| [Reasoning Outputs](reasoning_outputs.md) | 关联特性 —— 结构化输出可与推理输出协同工作 | "See also: [Reasoning Outputs] documentation" |
| [OpenAI Completions/Chat API](https://platform.openai.com/docs/api-reference) | 上游协议规范 | "using the OpenAI's Completions and Chat API" |
| [JSON Schema](https://json-schema.org/) | `json` 参数所遵循的规范 | "Using directly a JSON Schema" |
| [Pydantic](https://docs.pydantic.dev/latest/) | 把模型类转换为 JSON Schema 的辅助库 | "Defining a Pydantic model and then extracting the JSON Schema" |
| [xgrammar](https://github.com/mlc-ai/xgrammar) | 结构化生成后端实现 | 文档开篇 "using xgrammar ... as backends" |
| [guidance / llguidance](https://github.com/guidance-ai/llguidance) | 另一结构化生成后端实现 | 文档开篇 "or guidance ... as backends" |
| [OpenAI Python beta client](https://github.com/openai/openai-python/blob/52357cff50bee57ef442e94d78a0de38b4173fc2/src/openai/resources/beta/chat/completions.py#L100-L104) | "Experimental Automatic Parsing" 所封装的客户端层 | 章节"At the time of writing (openai==1.54.4)" |

另由文档外信息(原始提问上下文)可知还存在指向 [`../../examples/features/structured_outputs/structured_outputs_offline.py`](../../examples/features/structured_outputs/structured_outputs_offline.py) 的离线推理示例,但该链接未在所提供原文片段中显式出现,故此处不展开。

---

## 【使用方法】

### 1. 启动服务并选择后端(原文)

```bash
# 默认 auto 后端
vllm serve <model>

# 指定后端
vllm serve <model> --structured-outputs-config.backend xgrammar
# 或
vllm serve <model> --structured-outputs-config.backend guidance
```

可执行 `vllm serve --help` 查看 `--structured-outputs-config` 的完整子项。

### 2. 在线 API 调用 —— 六种参数(原文示例)

- **`choice`**:强制输出为给定枚举之一。
  ```python
  extra_body={"structured_outputs": {"choice": ["positive", "negative"]}}
  ```
- **`regex`**:匹配给定正则模板(语法依后端而异)。
  ```python
  extra_body={"structured_outputs": {"regex": r"\w+@\w+\.com\n"}, "stop": ["\n"]}
  ```
- **`json`**:JSON Schema 输出,两种用法 —— 直接传 schema,或用 Pydantic 模型 `model_json_schema()` 派生。
  ```python
  response_format={
      "type": "json_schema",
      "json_schema": {"name": "car-description",
                      "schema": CarDescription.model_json_schema()},
  }
  ```
- **`grammar`**:EBNF 文法输出(支持 SQL 等完整语言子集)。
  ```python
  extra_body={"structured_outputs": {"grammar": simplified_sql_grammar}}
  ```
- **`structural_tag`**:在指定标签内遵循 JSON schema。
- **`whitespace_pattern`**:控制 token 间空白匹配模式。

### 3. 推理模型 + 结构化输出(原文)

```bash
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --reasoning-parser deepseek_r1
```

返回消息中 `reasoning` 与 `content` 分字段,`reasoning` 可经 `completion.choices[0].message.reasoning` 读取。

### 4. Qwen3 Coder 兼容(原文 v0.11.2+)

```bash
vllm serve <qwen3-coder-model> \
  --reasoning-parser qwen3_coder \
  --structured-outputs-config.enable_in_reasoning=True
```

### 5. 实验性自动解析(原文所提,但文档此处在所提供片段中截断)

章节 "Experimental Automatic Parsing (OpenAI API)" 注明使用 OpenAI Python `beta` 客户端的 `client.chat.completions.create(...)` 包装,以获得对 Python 类型(Pydantic 模型等)的更丰富集成,所用示例模型为 `meta-llama/Llama-3.1-8B-Instruct`。该节在所提供原文片段中以 "Here is a simple example demonstrating how to get stru" 截断,故更详细调用代码**原文未涉及**(超出本片段范围)。

---

> **备注**:所提供原文在末尾处出现截断("Here is a simple example demonstrating how to get stru"),以及若干重复或非链接形态的内部参考条目(例如 `content='{"name":"Cameron","age":28}'...`、`parsed=Testing(...)`、`parsed=MathResponse(...)` 等)。这些片段在原始文档上下文中更可能是 **示例代码所打印出的消息响应内容**(即 `completion.choices[0].message` 的 `content`/`parsed` 字段示例),而非可点击的内部链接;因此本解读仅基于文档中可读的链接与代码片段进行归纳,未对截断部分进行臆测。
