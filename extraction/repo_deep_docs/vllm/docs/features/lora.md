# LoRA Adapters

> 仓 `vllm` · 路径 `docs/features/lora.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/lora.md

# vLLM LoRA Adapters 文档深度解读

## 【定位】

这篇文档解决"如何在 vLLM 上以 LoRA Adapter 形式对基础模型做轻量化、按需、可动态扩展的服务"这一类问题，覆盖离线推理、在线服务、以及运行时动态加载/卸载/插件解析四种使用场景。

---

## 【技术要点】

1. **接口前提**：LoRA 适配器可用于任何实现了 `vllm.model_executor.models.interfaces.SupportsLoRA` 的 vLLM 模型。
2. **离线启用三步法**：
   - 用 `huggingface_hub.snapshot_download(repo_id="...")` 把 adapter 下载到本地（如 `jeeejeee/llama32-3b-text2sql-spider`）。
   - 实例化 `LLM(model="meta-llama/Llama-3.2-3B-Instruct", enable_lora=True)`。
   - 用 `LoRARequest("sql_adapter", 1, sql_lora_path)` 作为 `llm.generate(..., lora_request=...)` 参数提交请求；`LoRARequest` 三个参数依次为：人类可读名、全局唯一 ID、adapter 路径。
3. **服务端启动**：通过 `vllm serve` 加两个开关：
   - `--enable-lora`
   - `--lora-modules {name}={path}`（可重复多个，如 `sql-lora=jeeejeee/llama32-3b-text2sql-spider`）。
   - 服务端还接受 `max_loras`、`max_lora_rank`、`max_cpu_loras` 等全局配置，作用于后续所有请求。
4. **运行时动态加载/卸载**：必须先 `export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True`（文档明确警告：除非隔离可信环境，否则不应在生产使用）。
   - 加载：`POST /v1/load_lora_adapter`，body 含 `lora_name` + `lora_path`。
   - 卸载：`POST /v1/unload_lora_adapter`，body 含 `lora_name`。
   - 成功均返回 `200 OK`，body 形如 `Success: LoRA adapter 'sql_adapter' added successfully` / `removed successfully`。
5. **插件化解析（LoRAResolver）**：在请求遇到尚未加载的模型名时自动加载；可同时配多个 resolver，vLLM 取第一个命中的。文档给出的两个内置 resolver：
   - `lora_filesystem_resolver` —— 配合 `VLLM_LORA_RESOLVER_CACHE_DIR`，从本地目录加载子目录形式的 adapter。
   - `lora_hf_hub_resolver` —— 配合 `VLLM_LORA_RESOLVER_HF_REPO_LIST`（逗号分隔 HF 仓库 ID 列表），从 HF Hub 按 `my/repo/subpath` 形式下载并构建请求。
   - 启用任一 resolver 同样需要 `VLLM_ALLOW_RUNTIME_LORA_UPDATING=True`。
6. **采样与请求参数示例**：`temperature=0`、`max_tokens=256`、`stop=["[/assistant]"]`；curl 客户端示例用 `model: "sql-lora"`、`max_tokens: 7`、`temperature: 0`。

---

## 【关键机制与数据】

- **per-request 服务**：原文："Adapters can be efficiently served on a per-request basis with minimal overhead." 即 LoRA 可按请求粒度低开销切换。
- **请求处理关系**：原文："The requests will be processed according to the server-wide LoRA configuration (i.e. in parallel with base model requests, and potentially other LoRA adapter requests if they were provided and `max_loras` is set high enough)." —— LoRA 请求与基础模型请求并行，并能与其他 LoRA 请求并行，前提是 `max_loras` 足够大。
- **`/models` 端点暴露**：原文示例响应中，`/v1/models` 列表里会同时出现基础模型 `meta-llama/Llama-3.2-3B-Instruct` 与 LoRA 别名 `sql-lora`，客户端可像普通模型一样通过 `model` 字段指定。
- **Resolver 命中与缓存**：原文：HF resolver 在收到请求 `my/repo/subpath` 时，会下载 `my/repo` 的 `subpath` 目录（须含 `adapter_config.json`），之后构建到缓存目录的请求，"similar to the `lora_filesystem_resolver`"。
- **多 resolver 优先级**：原文："vLLM will load the first LoRA adapter that it finds." 多个 resolver 时取第一个命中。
- **离线→在线身份一致性**：离线的 `LoRARequest("sql_adapter", 1, sql_lora_path)` 与在线 `--lora-modules sql-lora=...` / 动态接口的 `lora_name: "sql_adapter"` 是同一类标识抽象，可视为同一逻辑名。
- **多 adapter / 异步引擎**：原文把这部分指向了 `examples/features/lora/multilora_offline.py`，本文未给出具体数字/性能指标。
- **安全边界**：原文对动态加载/远程 HF 解析器均给出 "not intended for use in production environments" 与 "comes with security risks" 的警示，未给出具体风险量化指标。

---

## 【表格解读】

**原文无表格**（文档以代码片段与命令行示例为主，未提供参数表或性能对比表）。

---

## 【公式解读】

**原文无公式**（文档不涉及数学表达式或伪代码算法，仅给出参数化示例代码与 API 调用形式）。

---

## 【关联】

- **`../../examples/features/lora/multilora_offline.py`**（文末直接链接）：异步引擎 + 高级配置（如多 adapter 并发、更复杂的 `LoRARequest` 用法）的可运行示例；本文多次提到的"更多配置"即指向该文件。
- **`SupportsLoRA` 接口**（`vllm.model_executor.models.interfaces.SupportsLoRA`）：定义"哪些模型类支持 LoRA"，是离线/在线/动态三条路径能否启用 LoRA 的判定前提。
- **`vllm.lora.request.LoRARequest`**（代码 `from vllm.lora.request import LoRARequest`）：离线推理与 plugin（自定义 S3 resolver）共用的请求载体，承载 name / id / path 三元组。
- **`vllm.lora.resolver.LoRAResolver`**（`from vllm.lora.resolver import LoRAResolver`）：插件机制入口，文档给出 S3 自定义实现的 `async def resolve_lora(self, base_model_name, lora_name)` 签名，作为扩展点。
- **`../design/plugin_system.md`**（内部链接清单给出的关联文档）：vLLM 的插件系统总览；本文的 `VLLM_PLUGINS`、resolver 注册、enable/disable 流程都建立在该插件框架之上，是 LoRA 动态能力的基础设施层。
- **OpenAI 兼容 API**：`/v1/models`、`/v1/completions`、`/v1/load_lora_adapter`、`/v1/unload_lora_adapter` 都沿用 OpenAI 风格，把 LoRA 视作与基础模型同质的一等公民。

---

## 【使用方法】

### 1. 离线（Offline）推理

- 启用 flag：`LLM(..., enable_lora=True)`。
- 加载 adapter：`snapshot_download(repo_id=...)`。
- 调用：`llm.generate(prompts, sampling_params, lora_request=LoRARequest(name, id, path))`。
- 异步 / 多 adapter / 高级配置见 `examples/features/lora/multilora_offline.py`。

### 2. 在线服务（Server）

- 启动命令示例：
  ```bash
  vllm serve meta-llama/Llama-3.2-3B-Instruct \
      --enable-lora \
      --lora-modules sql-lora=jeeejeee/llama32-3b-text2sql-spider
  ```
- 配套配置项（原文提到的）：`max_loras`、`max_lora_rank`、`max_cpu_loras`（"etc." 表示原文并未穷举）。
- 查询可用模型：`curl localhost:8000/v1/models`，可看到基础模型 + LoRA 别名。
- 客户端调用时把 `model` 字段写为 LoRA 别名即可（如 `"model": "sql-lora"`）。

### 3. 运行时动态加载/卸载

- 先开启开关：
  ```bash
  export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
  ```
- 加载：
  ```bash
  curl -X POST http://localhost:8000/v1/load_lora_adapter \
  -H "Content-Type: application/json" \
  -d '{"lora_name": "sql_adapter", "lora_path": "/path/to/sql-lora-adapter"}'
  ```
- 卸载：
  ```bash
  curl -X POST http://localhost:8000/v1/unload_lora_adapter \
  -H "Content-Type: application/json" \
  -d '{"lora_name": "sql_adapter"}'
  ```

### 4. 插件化解析（LoRAResolver）

- 启用内置 resolver 同样需先 `export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True`。
- 本地目录 resolver：
  - 设置 `VLLM_PLUGINS` 含 `lora_filesystem_resolver`。
  - 设置 `VLLM_LORA_RESOLVER_CACHE_DIR` 指向本地目录。
  - 收到请求 `foobar` 时，会在该目录下找 `foobar/` 子目录并作为 adapter 加载。
- Hugging Face Hub resolver：
  - 设置 `VLLM_PLUGINS` 含 `lora_hf_hub_resolver`。
  - 设置 `VLLM_LORA_RESOLVER_HF_REPO_LIST` 为逗号分隔的仓库 ID 列表。
  - 收到 `my/repo/subpath` 请求时，会下载 `my/repo` 的 `subpath`（须含 `adapter_config.json`），缓存到本地后再走 filesystem resolver 流程。
  - 原文明确警示："enabling remote downloads is insecure and not intended for use in production environments"。
- 自定义 plugin：实现 `vllm.lora.resolver.LoRAResolver`，覆写 `async def resolve_lora(self, base_model_name, lora_name)`，示例中给出基于 `s3fs` 的 S3 resolver 模板（具体 `S3_PATH_TEMPLATE` / `LOCAL_PATH_TEMPLATE` 等环境变量由实现者自行约定，文档未给出默认值）。
