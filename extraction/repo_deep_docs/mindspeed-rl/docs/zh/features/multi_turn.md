# 多轮迭代

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/multi_turn.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/multi_turn.md

# mindspeed-rl 多轮迭代（Multi Turn）特性文档深度解读

## 【定位】

本文档系统阐述了 mindspeed-rl 强化学习加速库中**多轮迭代（Multi Turn）能力**的两种实现方案 —— **ReTool（代码解释器）**与 **Search Tool（搜索引擎）**，解决"在固定参数量下，通过让 LLM 在 rollout 阶段交错调用外部工具并基于多轮反馈学习工具使用策略"这一核心问题，从而提升 LLM 在复杂推理任务上的表现。

---

## 【技术要点】

1. **两种多轮工具方案**：① ReTool —— 基于字节 seed 团队 [ReTool](https://github.com/ReTool-RL/ReTool) 框架，LLM 推理与代码执行交错执行，通过最终结果反馈学习工具调用策略；② Search Tool —— 检索增强式工具调用，基于检索服务返回结果指导模型学习。

2. **多轮迭代通用配置（rl_config 段）**：
   - `verifier_function: ["retool_reward"]` —— 规则奖励函数
   - `multi_turn_enable: true` —— 开启多轮迭代
   - `tool_config_path` —— 工具配置路径（ReTool 用 `retool_config.yaml`，Search Tool 用 `search_tool_config.yaml`）
   - `max_tool_calls: 1` / `max_parallel_calls: 1` —— 累积/并发调用工具上限
   - `max_total_response_length: 2048` / `max_tool_response_length: 256` —— 拼接总长度与单次工具返回长度上限
   - `tool_response_truncate_side: 'middle'` —— 截断方式（支持 left/right/middle）
   - `tool_parser_format: 'hermes'` —— 工具调用内容提取方式（目前仅支持 hermes）
   - `async_engine: true` —— **异步引擎开启**是多轮迭代可用的前提条件

3. **ReTool 沙箱配置关键参数**：线程池并发度 `num_workers: 128`、限流 `rate_limit: 128`、代码运行超时 `default_timeout: 30`、语言 `default_language: "python"`、内存上限 `memory_limit_mb: 1024`、沙箱地址 `sandbox_fusion_url: "http://localhost:8080/run_code"`。

4. **Search Tool 配置关键参数**：检索服务地址 `retrieval_service_url: "http://localhost:8080/retrieve"`、并发度 `num_workers: 120`、限流 `rate_limit: 120`、超时 `timeout: 30`、返回结果数 `topk: 3`。

5. **数据预处理模板**：ReTool 使用 `qwen_retool`，Search Tool 使用 `qwen_search_tool`，通过数据集 yaml 中 `prompt_type` 字段切换。

6. **OpenAI Function Calling Schema**：工具描述遵循 `OpenAIFunctionToolSchema` 格式（含 `type`/`name`/`description`/`parameters`/`strict` 等字段），当前 `type` 仅支持 `native`（function call 方式）。

---

## 【关键机制与数据】

**工作原理（原文）：** "在 rollout 的过程中，LLM 推理与代码执行交错执行，多轮迭代之后，根据最终输出的结果反馈指导模型学习何时以及如何调用工具。"

**数据流（ReTool 路径）：**
1. LLM 在推理生成 response 时按 `hermes` 格式提取工具调用内容；
2. 工具调用经 `retool_config.yaml` 路由至 `mindspeed_rl.tools.retool.ReTool` 类；
3. ReTool 类通过 HTTP 转发至部署于 `http://localhost:8080/run_code` 的 SandboxFusion 代码沙箱；
4. 沙箱执行结果返回后，若长度 > 256 token，则按 `middle` 方式截断；
5. 工具结果与 LLM response 拼接，累计总长不超过 2048 token，达到 `max_tool_calls: 1` 后终止；
6. 最终输出经 `retool_reward` 规则奖励函数评估，反馈至训练过程。

**数据流（Search Tool 路径）：** 与 ReTool 流程一致，但终端服务为本地或集成搜索引擎，检索请求携带 `query_list`，返回 top-3 结果。

**性能/上限数据（原文）：**
- `max_total_response_length`: **2048**
- `max_tool_response_length`: **256**
- `max_tool_calls` / `max_parallel_calls`: **1 / 1**
- ReTool 线程池并发: **128 worker / 128 rate_limit**
- Search Tool 线程池并发: **120 worker / 120 rate_limit**
- 代码沙箱超时: **30s**；内存上限: **1024 MB**
- 搜索超时: **30s**；topk: **3**

---

## 【表格解读】

### 表 1：多轮迭代通用 rl_config 配置项

| 配置项 | 原文取值 | 含义 |
|---|---|---|
| `verifier_function` | `["retool_reward"]` | 使用的规则奖励函数，默认 retool_reward |
| `multi_turn_enable` | `true` | 是否使能多轮迭代 |
| `tool_config_path` | `./configs/tools/retool_config.yaml` / `./configs/tools/search_tool_config.yaml` | 工具相关配置路径 |
| `max_tool_calls` | `1` | 多轮迭代过程中累积最多调用工具次数 |
| `max_parallel_calls` | `1` | 每次调用工具过程中最多同时调用次数 |
| `max_total_response_length` | `2048` | 推理 response + 工具结果拼接后完整 response 长度上限 |
| `max_tool_response_length` | `256` | 单次工具执行结果长度上限，超出则截断 |
| `tool_response_truncate_side` | `'middle'` | 工具结果过长时的截断方式，支持 left/right/middle |
| `tool_parser_format` | `'hermes'` | 从推理 response 中提取工具调用内容的方式，目前仅支持 hermes |
| `async_engine` | `true` | 是否使能异步引擎，多轮迭代仅在异步引擎开启时可用 |

### 表 2：ReTool 工具配置（`retool_config.yaml`）

| 字段 | 原文取值 | 含义 |
|---|---|---|
| `class_name` | `mindspeed_rl.tools.retool.ReTool` | 使用的工具子类 |
| `sandbox_fusion_url` | `http://localhost:8080/run_code` | 部署好的代码沙箱 URL |
| `num_workers` | `128` | 线程池默认并发度 |
| `enable_global_rate_limit` | `true` | 是否初始化对应线程池 worker |
| `rate_limit` | `128` | 线程池同时获取资源的线程数量 |
| `default_timeout` | `30` | 调用代码沙箱默认的代码运行/编译超时（秒） |
| `default_language` | `python` | 调用代码沙箱默认传入的代码语言 |
| `memory_limit_mb` | `1024` | 调用代码沙箱默认能使用的最大内存量 |
| `type` | `native` | 是否通过 function call 方式调用，目前仅支持 native |
| `tool_schema.function.name` | `code_interpreter` | 工具函数名 |
| `tool_schema.function.parameters.required` | `["code"]` | 函数必填参数 |

### 表 3：Search Tool 配置（`search_tool_config.yaml`）

| 字段 | 原文取值 | 含义 |
|---|---|---|
| `class_name` | `mindspeed_rl.tools.search_tool.SearchTool` | 使用的工具子类 |
| `retrieval_service_url` | `http://localhost:8080/retrieve` | 部署好的搜索工具 URL |
| `num_workers` | `120` | 线程池默认并发度 |
| `enable_global_rate_limit` | `true` | 是否初始化对应线程池 worker |
| `rate_limit` | `120` | 线程池同时获取资源的线程数量 |
| `timeout` | `30` | 调用搜索工具默认请求超时（秒） |
| `topk` | `3` | 调用搜索工具返回结果的最大数量 |
| `type` | `native` | 是否通过 function call 方式调用，目前仅支持 native |
| `tool_schema.function.name` | `search` | 工具函数名 |
| `tool_schema.function.parameters.required` | `["query_list"]` | 函数必填参数 |

### 表 4：OpenAI Function Calling Schema 通用字段

| 字段 | 含义 |
|---|---|
| `type` | 一般设置为 `function` |
| `name` | 函数名 |
| `description` | 描述函数功能，模型据此决定调用方式 |
| `parameters` | Json Schema 对象，定义函数接受的参数；无需参数时省略 |
| `strict` | 是否强制匹配当前 schema 格式 |

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **训练入口脚本**：两种工具方案共用 [`dapo_trainer_qwen25_7b_multi_turn.sh`](../../../examples/multi_turn/dapo_trainer_qwen25_7b_multi_turn.sh) 作为启动入口，并通过同一训练配置 [`dapo_qwen25_7b_A2_multi_turn.yaml`](../../../configs/dapo_qwen25_7b_A2_multi_turn.yaml) 引用；唯一差异在 `tool_config_path` 指向的工具配置不同（ReTool → `retool_config.yaml`，Search Tool → `search_tool_config.yaml`）。
- **奖励函数扩展点**：用户可通过 [`rule_verifier.py`](../../../mindspeed_rl/models/rule_verifier.py) 增加自定义奖励函数，并在 `rule_verifier_function` 变量中注册映射，再将训练配置中的 `retool_reward` 替换为自定义函数名即可生效。
- **工具实现层**：ReTool 对应 `mindspeed_rl.tools.retool.ReTool` 类，Search Tool 对应 `mindspeed_rl.tools.search_tool.SearchTool` 类，两者均以 `class_name` 字段在 yaml 中注入。
- **工具部署依赖**：ReTool 的代码沙箱依赖字节开源的 [SandboxFusion](https://github.com/bytedance/SandboxFusion)（conda 环境 python=3.12，`make run-online` 启动）；Search Tool 的检索后端既可自建，也可参考 [Search-R1](https://github.com/PeterGriffinJin/Search-R1/blob/main/docs/retriever.md) 集成方案。
- **数据预处理联动**：数据集 yaml 中 `prompt_type` 字段需在 `qwen_retool`（ReTool）与 `qwen_search_tool`（Search Tool）之间切换，可按需自定义修改。

---

## 【使用方法】

### 1. 启用 ReTool 多轮迭代

```yaml
# configs/dapo_qwen25_7b_A2_multi_turn.yaml (rl_config 段)
rl_config:
  verifier_function: ["retool_reward"]
    
  multi_turn_enable: true
  tool_config_path: ./configs/tools/retool_config.yaml
  max_tool_calls: 1
  max_parallel_calls: 1
  max_total_response_length: 2048
  max_tool_response_length: 256
  tool_response_truncate_side: 'middle'
  tool_parser_format: 'hermes'

  async_engine: true
```

数据集 yaml 中设置 `prompt_type: qwen_retool`。

### 2. 启用 Search Tool 多轮迭代

将 `tool_config_path` 改为 `./configs/tools/search_tool_config.yaml`，数据集 yaml 中设置 `prompt_type: qwen_search_tool`。

### 3. 自定义奖励函数

编辑 `mindspeed_rl/models/rule_verifier.py`，在 `rule_verifier_function` 变量中注册新映射；将训练配置 `verifier_function` 由 `["retool_reward"]` 改为自定义函数名。

### 4. 部署 ReTool 代码沙箱

```shell
conda create -n sandbox -y python=3.12
conda activate sandbox
pip install poetry
poetry install
pip install -r runtime/python/requirements.txt --ignore-requires-python
mkdir -p docs/build
make run-online
```

### 5. 部署 Search Tool 检索后端

参考 [Search-R1 retriever 文档](https://github.com/PeterGriffinJin/Search-R1/blob/main/docs/retriever.md) 进行本地搭建或集成。
