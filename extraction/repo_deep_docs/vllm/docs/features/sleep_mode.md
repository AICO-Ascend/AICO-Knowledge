# Sleep Mode

> 仓 `vllm` · 路径 `docs/features/sleep_mode.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/sleep_mode.md

# vLLM Sleep Mode 文档深度解读

## 【定位】
这篇文档描述 vLLM 的 **Sleep Mode（休眠模式）** 能力：在不停止 server、不卸载 Docker 容器的前提下，临时释放模型占用的 GPU 显存（模型权重 + KV cache），以便在同一份 GPU 资源上交错进行推理与训练（如 RLHF、colocated trainer），并可快速唤醒恢复推理。

---

## 【技术要点】

1. **两级休眠机制（Sleep Levels）**
   - **Level 1**：将模型权重卸载到 CPU RAM（备份），丢弃 KV cache；KV 内容遗忘，权重可恢复。需保证 CPU 内存足够。
   - **Level 2**：同时丢弃模型权重和 KV cache（仅保留部分元数据如 rope scaling 等 buffer 在 CPU）；两者内容均遗忘；适用场景为切换/更新模型、CPU 内存不足的 RLHF colocation；唤醒后需通过 `collective_rpc("reload_weights")` 重新加载权重。

2. **细粒度唤醒（fine-grained wake_up）**
   - `wake_up()` 支持 `tags` 参数，可分步唤醒：`tags=["weights"]` 仅恢复权重、`tags=["kv_cache"]` 仅恢复 KV cache；目的为避免 RLHF 权重更新期间同时分配 KV cache 导致 OOM。
   - 注意：`is_sleeping` 在所有组件全部唤醒完毕前都会返回 `true`。

3. **离线推理启用**
   - 通过 `LLM("model", enable_sleep_mode=True)` 启用。
   - 配套调用：`llm.sleep(level=1|2)`、`llm.wake_up()`、`llm.wake_up(tags=[...])`、`llm.collective_rpc("reload_weights")`。

4. **在线 Serving 启用（HTTP API）**
   - 启动前置条件：环境变量 `VLLM_SERVER_DEV_MODE=1`（开启 dev endpoints，**不应暴露给用户**） + 启动参数 `--enable-sleep-mode`。
   - 启动命令：`VLLM_SERVER_DEV_MODE=1 vllm serve Qwen/Qwen3-0.6B --enable-sleep-mode --port 8000`。
   - HTTP endpoints：`POST /sleep?level=N`、`POST /wake_up`（可带 `?tags=weights` 或 `?tags=kv_cache`）、`POST /collective_rpc`、`GET /is_sleeping`。

5. **平台支持与分布式**
   - 支持 **CUDA 和 ROCm** 平台。
   - 支持 **tensor parallelism / pipeline parallelism** 等分布式工作负载。

6. **ROCm 平台限制**
   - ROCm 上虚拟内存分配以 **chunked memory allocation** 方式执行；可通过环境变量 `VLLM_ROCM_SLEEP_MEM_CHUNK_SIZE`（单位 MB）控制 chunk 大小；**默认值 256MB**。
   - 块越大速度越快，但过大可能引发 OOM；建议取 **2 的幂**，遇 OOM 时调小。

---

## 【关键机制与数据】

- **显存释放比例（原文）**：原文声明可释放 **"up to 90%+ of GPU memory"** 用于其他任务——这是通过把模型权重 offload 到 CPU RAM 并丢弃 KV cache 实现的。
- **数据流（Level 1）**：GPU 权重 → CPU RAM 备份；KV cache → 丢弃；唤醒时权重由 CPU 回迁 GPU，KV cache 重建。
- **数据流（Level 2）**：GPU 权重 → 丢弃；KV cache → 丢弃；CPU 仅保留少量 model buffer（如 rope scaling tensors）；唤醒时通过 `collective_rpc("reload_weights")` 重新加载权重。
- **RLHF 权重更新推荐时序**（原文示例）：
  1. `llm.sleep(level=2)`
  2. 获取新权重
  3. `llm.wake_up(tags=["weights"])` —— 仅分配权重显存，避免 OOM
  4. 更新权重
  5. `llm.wake_up(tags=["kv_cache"])` —— 更新后再分配 KV cache
- **ROCm chunked allocation（原文）**：默认 256MB；块越大速度越快；过大会 OOM；建议 2 的幂。
- **典型性能/恢复速度（原文）**：原文仅定性描述 "Fast resume" 与 "Quickly wake up the engine and resume inference without full model reload"，**未给出具体的数字（毫秒、token/s 等）**，故不引用具体数值。

---

## 【表格解读】
**原文无表格。**

原文所有信息以「Key benefits 列表」「Sleep levels 段落」「HTTP endpoints 列表」「代码块」「注释」形式呈现，未提供 markdown/html 表格。

---

## 【公式解读】
**原文无公式。**

文档全文未包含任何 LaTeX 公式、伪代码公式或数学表达式。

---

## 【关联】

文档中显式提及/隐含的关联如下：

- **RLHF 训练流程**：Sleep Level 2 + `tags=["weights"]` + `collective_rpc("reload_weights")` 的组合，是文档重点推荐的 colocated RLHF 权重更新模式；与上游 trainer 的 offload 行为互不冲突。
- **Distributed execution**：支持 tensor parallelism、pipeline parallelism——意味着 Sleep Mode 与 vLLM 的分布式执行器（distributed executor / `collective_rpc`）共享同一控制面，唤醒动作通过 collective RPC 下发。
- **Online Serving / dev endpoints**：HTTP 入口 `/sleep`、`/wake_up`、`/collective_rpc`、`/is_sleeping` 都挂载在 dev mode 下（`VLLM_SERVER_DEV_MODE=1`）——属于 OpenAI-compatible 之外的 dev-only 路由，不应在生产对外暴露。
- **ROCm 虚拟内存分配器**：Sleep Mode 在 ROCm 上依赖 chunked VMM，是与平台后端（AMD ROCm）紧耦合的实现细节；通过 `VLLM_ROCM_SLEEP_MEM_CHUNK_SIZE` 暴露调参。
- **内部链接**：原文未提供任何其他文档/章节的内部链接，仅引用了一篇外部博客 https://blog.vllm.ai/2025/10/26/sleep-mode.html 作为补充材料。

---

## 【使用方法】

### 离线（Offline inference）
```python
from vllm import LLM
llm = LLM("Qwen/Qwen3-0.6B", enable_sleep_mode=True)

# Level 1
llm.sleep(level=1)
llm.wake_up()

# Level 2 + 重新加载权重
llm.sleep(level=2)
llm.wake_up(tags=["weights"])
llm.collective_rpc("reload_weights")
llm.wake_up(tags=["kv_cache"])
```

### 在线 Serving（Online Serving）
- 启动：
  ```bash
  VLLM_SERVER_DEV_MODE=1 vllm serve Qwen/Qwen3-0.6B \
    --enable-sleep-mode \
    --port 8000
  ```
- 控制命令：
  ```bash
  # Level 1
  curl -X POST 'http://localhost:8000/sleep?level=1'
  curl -X POST 'http://localhost:8000/wake_up'

  # Level 2
  curl -X POST 'http://localhost:8000/sleep?level=2'
  curl -X POST 'http://localhost:8000/wake_up?tags=weights'
  curl -X POST 'http://localhost:8000/collective_rpc' \
       -H 'Content-Type: application/json' \
       -d '{"method":"reload_weights"}'
  curl -X POST 'http://localhost:8000/wake_up?tags=kv_cache'
  ```

### 配置项 / 环境变量
- `enable_sleep_mode=True` —— `LLM` 构造参数，离线启用。
- `--enable-sleep-mode` —— vLLM serve 启动参数。
- `VLLM_SERVER_DEV_MODE=1` —— 启用 dev-only HTTP endpoints（`/sleep`、`/wake_up`、`/collective_rpc`、`/is_sleeping`）。
- `VLLM_ROCM_SLEEP_MEM_CHUNK_SIZE` —— **ROCm 专用**，单位 MB，**默认 256**，建议取 2 的幂；ROCm 遇 OOM 时调小以提速/省显存之间的权衡。

### 常用 HTTP 端点（仅 dev mode 下可用）
- `POST /sleep?level=1|2`
- `POST /wake_up`（支持 `?tags=weights` / `?tags=kv_cache`）
- `POST /collective_rpc`
- `GET /is_sleeping`
