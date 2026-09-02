# 快速入门

> 仓 `mindie-motor-cpp` · 路径 `docs/zh/user_guide/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor-cpp/docs/zh/user_guide/quick_start.md

# mindie-motor-cpp 快速入门文档 深度解读

## 【定位】

本篇文档面向首次接触 MindIE（昇腾自研推理集群管理框架）Server 的用户，提供从环境就绪到服务拉起、再到通过 vLLM 兼容的 OpenAI 风格 RESTful 接口发起流式推理请求的端到端最小可用路径，并提示关键的目录权限、HTTPS 安全、共享内存清理等工程陷阱。

---

## 【技术要点】

1. **服务启动入口**：以 `mindieservice_daemon` 二进制为核心，原文给出两种启动方式——方式一（推荐）使用 `source set_env.sh && nohup ./bin/mindieservice_daemon > output.log 2>&1 &` 后台进程模式，关闭窗口进程仍存活；方式二直接前台执行 `./bin/mindieservice_daemon`。两种方式成功回显均为 `Daemon start success!`。

2. **启动目录硬性约束**：原文明确指出 `bin` 目录权限为 **550（无写权限）**，但算子运行需在当前目录生成 `kernel_meta` 文件夹，且 `Ascend-cann-toolkit` 会生成 `kernel_meta_temp_*xxxx*` 目录保存算子 cce 文件，因此禁止直接在 `bin` 下启动，必须在用户可写目录（如 `Ascend-mindie-server_{version}_linux-{arch}` 自身或其下自建临时目录）执行。

3. **切换用户时的共享内存清理**：切换用户后须执行 `rm -f /dev/shm/*`，删除前用户遗留的共享文件，避免新用户因无读写权限导致推理失败。

4. **默认监听与可配置项**：Server 默认监听 `https://127.0.0.1:1025`，可通过 `config.json` 中的 `"ipAddress"` 和 `"port"` 参数修改。

5. **HTTPS 安全默认与告警**：原文以 WARNING 级别提示 HTTP 缺乏安全机制（数据泄露、篡改、中间人攻击风险），建议优先使用 HTTPS。客户端 curl 命令固定使用 `--cacert ca.pem --cert client.pem --key client.key.pem` 三件套做双向证书校验。

6. **兼容多框架接口**：Server 可部署兼容 Triton / OpenAI / TGI / vLLM 第三方框架的服务接口；本文给出 `v1/chat/completions` 与 `v1/completions` 两个 OpenAI 兼容的流式推理接口示例，请求体支持 `presence_penalty / frequency_penalty / repetition_penalty / temperature / top_p / top_k / seed / max_tokens / n / best_of` 等参数。

7. **超大模型加载特殊性**：原文示例 1300B 超大模型加载时间很长，需参考 FAQ 章节缩短加载时间。

---

## 【关键机制与数据】

**工作原理/数据流（基于原文）：**

- **服务能力栈**：Server 提供三类能力——服务状态查询、模型信息查询、文本/流式推理（原文:"Server可实现服务状态查询，模型信息查询，文本/流式推理等功能"）。
- **流式响应机制**：从 `v1/chat` 返回示例可见，响应为一系列 `data: {...}` 的 Server-Sent Events（SSE）片段，每条 chunk 中 `choices[].delta.content` 携带增量 token；最后一条携带 `finish_reason:"length"` 表示达到 `max_tokens` 限制，并以 `data: [DONE]` 结束流。
- **性能统计字段（原文）**：流式响应末段附带 `usage` 字段，含 `prompt_tokens=24, completion_tokens=5, total_tokens=29`，并暴露 `batch_size:[1,1,1,1,1]` 与 `queue_wait_time:[5318,117,82,196]` 等运行时统计指标（注意原文末段 `queue_wait_time` 数组列出的具体数字为示例值，原文示例中末段只显示了 4 个数字，但格式为按批次粒度的队列等待时间，单位为 ms，原文未显式标注单位）。

**性能/规模数据（原文有标注的）：**

- 原文（关于超大模型）："如果您使用的模型为超大模型（比如1300B的超大模型），其模型加载时间将会很长"。
- 默认端口：`1025`，默认协议：`HTTPS`，默认 IP：`127.0.0.1`。
- `bin` 目录权限数值：`550`（无写权限）。

---

## 【表格解读】

### 表 1：v1/chat 流式推理接口（原文逐字还原）

| 字段 | 值 |
|---|---|
| 接口名 | v1/chat流式推理接口 |
| URL | **https://**{服务IP地址}:{端口号}**/v1/chat/completions** |
| 请求类型 | POST |
| 请求示例 | `curl -H "Accept: application/json" -H "Content-type: application/json" --cacert ca.pem --cert client.pem  --key client.key.pem -X POST -d '{ "model": "Qwen", "messages": [ { "role": "user", "content": "You are a helpful assistant." } ], "stream": true, "presence_penalty": 1.03, "frequency_penalty": 1.0, "repetition_penalty": 1.0, "temperature": 0.5, "top_p": 0.95, "top_k": 1, "seed": 1, "max_tokens": 5, "n": 2, "best_of": 2 }' https://127.0.0.1:1025/v1/chat/completions` |
| 返回示例 | `data: {"id":"endpoint_common_10","object":"chat.completion.chunk","created":1744038509,"model":"llama","choices":[{"index":0,"delta":{"role":"assistant","content":"You"},"logprobs":null,"finish_reason":null}]}` ……（多个 chunk 依次输出 `"You"`, `" are"`, `" a"`, `" helpful"`, `" assistant"`）…… `data: {"id":"endpoint_common_10","object":"chat.completion.chunk","created":1744038509,"model":"llama","usage":{"prompt_tokens":24,"prompt_tokens_details": {"cached_tokens": 0},"completion_tokens":5,"total_tokens":29,"batch_size":[1,1,1,1,1],"queue_wait_time":[5318,117,82,72,196]},"choices":[{"index":0,"delta":{"role":"assistant","content":" assistant"},"logprobs":null,"finish_reason":"length"}]}` `data: [DONE]` |

**逐行解读：**
- **接口名/URL/请求类型**：表明这是 OpenAI 兼容的 Chat Completions 流式端点，使用 HTTPS POST，路径拼接为 `/v1/chat/completions`。
- **请求示例关键参数**：`stream=true` 开启流式；`max_tokens=5` 解释了返回示例中恰好产出 5 个增量片段；`n=2` 解释了为什么每个 chunk 都同时携带 `index:0` 与 `index:1` 两条候选；`best_of=2` 与 `n` 配合，决定服务端从 `best_of` 个候选中返回 `n` 个；`temperature=0.5, top_p=0.95, top_k=1` 共同约束采样；`presence_penalty=1.03 / frequency_penalty=1.0 / repetition_penalty=1.0` 为可重复性控制项。
- **返回示例关键观察**：`id` 固定为 `endpoint_common_10`，标识本次会话；`created` 为 Unix 秒级时间戳；`object` 为 `chat.completion.chunk`；`logprobs:null` 表示未开启对数概率回传；末段 `usage` 给出 token 用量统计，并附带 `batch_size` 与 `queue_wait_time` 运行时元数据（前者为批大小，后者按推理步骤给出排队等待时间示例值）；`finish_reason:"length"` 说明因 `max_tokens=5` 而非自然结尾停止；流结束于 `data: [DONE]`。

### 表 2：v1/completions 流式推理接口（原文表格被截断，逐字还原可见部分）

| 字段 | 值 |
|---|---|
| 接口名 | v1/completions流式推理接口 |
| URL | **https://**{服务IP地址}:{端口号}**/v1/completions**（原文在"端口号}*"处截断，未给出完整路径后缀，但章节标题已明确为 `/v1/completions`，请求体与返回示例未在原文中给出） |

**逐行解读：**
- 该表在原文档中表格主体未完整给出（被截断），仅能看到表头与 URL 起始部分。文档其它表格（接口名/URL/请求类型/请求示例/返回示例）结构与表 1 保持一致，定位为 OpenAI 兼容的 Completions 端点。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本篇作为"快速入门"层，与以下文档/模块形成上下游或并列关系（基于原文链接 + 用户提供的内部链接信息）：

1. **环境准备 → 安装部署**：跳转至 `./install/environment_preparation.md`（原文锚文本："[安装指南]"，作为启动服务的前置条件）。
2. **配置参数说明（服务化）**：外部链接 `https://gitcode.com/Ascend/MindIE-LLM/blob/dev/docs/zh/user_guide/user_manual/service_parameter_configuration.md`——用于配置 `config.json` 中包括 `"ipAddress"`、`"port"` 在内的各项参数。
3. **单机部署 + HTTPS 通信配置**：外部链接 `https://gitcode.com/Ascend/MindIE-LLM/blob/dev/docs/zh/user_guide/user_manual/prefill_decode_mixed_deployment.md`——用于获取服务端证书、私钥等 HTTPS 所需文件（`ca.pem` / `client.pem` / `client.key.pem`）。
4. **预检工具**：原文提示拉起服务前可用 MindStudio 的 `msprechecker`（外部链接 `https://gitcode.com/Ascend/msit/tree/master/msprechecker`）对配置文件字段做合法性校验。
5. **大模型加载耗时长 FAQ**：外部链接 `https://gitcode.com/Ascend/MindIE-LLM/blob/master/docs/zh/faq/faq.md#%E5%8A%A0%E8%BD%BD%E5%A4%A7%E6%A8%A1%E5%9E%8B%E6%97%B6%E8%80%97%E6%97%B6%E8%BF%87%E9%95%BF`——用于 1300B 等超大模型加载时间优化。
6. **性能/精度测试工具（用户提供的内部链接，但原文未引用）**：`./service_oriented_optimization_tool/performance_accuracy_test_tool.md#table_ptrm002`——该链接在用户提供的"内部链接"清单中存在，但**原文正文并未直接引用**，可能属于姊妹文档或后续章节锚点，用于服务化部署后的精度/性能基准评测（PTRM002 锚点暗示存在性能测试结果对照表 `table_ptrm002`）。
7. **EndPoint 业务面 RESTful 接口全集**：外部链接 `https://www.hiascend.com/document/detail/zh/mindie/230/mindiellm/llmdev/mindie_service0065.html`——本文仅示例 `v1/chat` 与 `v1/completions`，其余接口（如 embeddings、rerank 等）需查阅该全集。

---

## 【使用方法】

**1. 查看安装路径（启动前置）**
```bash
pip show mindie_llm | grep Location
```

**2. 后台进程方式启动（推荐）**
```bash
cd {MindIE安装目录}
source set_env.sh
nohup ./bin/mindieservice_daemon > output.log 2>&1 &
```
成功标志：日志中打印 `Daemon start success!`。

**3. 前台直接启动**
```bash
./bin/mindieservice_daemon
```
成功标志：`Daemon start success!`。

**4. 配置监听地址/端口**
修改 `config.json` 中的 `"ipAddress"` 与 `"port"` 参数。

**5. HTTPS 客户端请求示例（列出模型列表）**
```bash
curl -H "Accept: application/json" -H "Content-type: application/json" \
     --cacert ca.pem --cert client.pem --key client.key.pem \
     -X GET https://127.0.0.1:1025/v1/models
```

**6. 流式 Chat 推理请求示例**
使用表 1 中的 curl 命令，URL 为 `https://127.0.0.1:1025/v1/chat/completions`，请求体 JSON 字段参见表 1 解读。

**7. 切换用户后必做清理**
```bash
rm -f /dev/shm/*
```

**8. 自定义日志路径**
`output.log` 文件名与路径均可自定义（`nohup ./bin/mindieservice_daemon > {自定义路径}/output.log 2>&1 &`）。

> 原文未涉及：除上述 curl 命令之外的其它客户端（Python SDK / Java SDK 等）的调用方式、性能调优开关的具体数值、鉴权 Token 用法等均未在本文给出，需查阅上文【关联】中各外部链接文档。
