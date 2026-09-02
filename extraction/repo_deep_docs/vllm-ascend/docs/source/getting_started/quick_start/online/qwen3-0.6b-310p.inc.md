# qwen3-0.6b-310p.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/online/qwen3-0.6b-310p.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/online/qwen3-0.6b-310p.inc.md

# vllm-ascend Qwen3-0.6B (Atlas 300I DUO / Atlas 200I Pro) 部署文档深度解读

---

## 【定位】

本文档是 **vLLM Ascend 在 Atlas 300I DUO 与 Atlas 200I Pro 上启动 Qwen3-0.6B 推理服务**的快速上手指南，聚焦于受限硬件路径下的运行时必要配置及服务启停完整流程。

---

## 【技术要点】

1. **硬件适用范围**：该示例已在 **Atlas 300I DUO** 和 **Atlas 200I Pro** 上验证通过，属受限硬件路径（runtime requirements 显式标注）。
2. **精度约束**：必须使用 `float16` 数据类型（`--dtype float16`）。
3. **CUDA Graph 模式限制**：必须使用 `FULL_DECODE_ONLY` 模式，并将捕获大小限制为 `[1, 2, 4, 8]`。
4. **禁用 NPU Graph 扩展**：`enable_npugraph_ex` 不受支持，必须通过 `--additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":false}}'` 显式关闭。
5. **并发上限**：`--max-num-seqs 8`，限制同时处理的请求数为 8。
6. **服务启动方式**：以 `vllm serve Qwen/Qwen3-0.6B ... &` 后台进程方式运行，并提供优雅停止 `kill -2 $VLLM_PID` 与 PID 二次确认的注意事项。

---

## 【关键机制与数据】

**工作原理（原文描述层面）：**

- **原文**：vLLM Ascend 在 Atlas 300I DUO 与 Atlas 200I Pro 上运行时，因硬件驱动/编译器对算子编译与 CUDA Graph 的支持存在差异，需要将 `cudagraph_mode` 收敛到 `FULL_DECODE_ONLY`（即仅在解码阶段使用 CUDA Graph），并将捕获的形状集合裁剪到 `[1, 2, 4, 8]`，以避免超出 NPU 编译器在受限路径上的可支持范围。
- **原文**：`enable_npugraph_ex` 是 NPU 上额外引入的图捕获/执行扩展，在该硬件路径上不支持，因此通过 `--additional-config` 注入 `ascend_compilation_config.enable_npugraph_ex=false` 进行关闭，绕过对应特性。
- **数据流**：模型以 `float16` 加载 → 由 vLLM 编译器按 `FULL_DECODE_ONLY` + 限定 capture sizes 编译可执行图 → 通过 OpenAI 兼容 HTTP 端点（默认 `http://0.0.0.0:8000`）对外提供 `/v1/models` 模型列表查询与 `/v1/completions` 推理接口。

**性能/规模数据：**
- 原文未提供吞吐量、时延、显存占用等基准数据，仅明确示例规模（`max-num-seqs 8`，`cudagraph_capture_sizes=[1,2,4,8]`，最大生成长度示例 `max_completion_tokens=5`）。

---

## 【表格解读】

原文无表格。

> 文档以命令片段与日志片段形式提供信息，未包含任何参数表、对比表或配置项表，因此不做表格逐行还原。

---

## 【公式解读】

原文无公式。

> 文档未涉及任何数学公式、伪代码或参数化表达式，所有配置均以 JSON 字面量或 CLI 参数形式直接给出。

---

## 【关联】

原文**未提供内部链接**，文末「内部链接: (无)」已印证这一点。结合文档语境（属于 vllm-ascend 项目 `quick_start/online/` 路径下的 `qwen3-0.6b-310p.inc.md`），可推断的关联模块包括：

- **`ascend_compilation_config`**：vLLM 通用 `compilation-config` 之外的 Ascend 私有子配置，本文档通过 `--additional-config` 注入，用于在受限硬件路径上关闭 `enable_npugraph_ex`，属 Ascend 编译/算子适配层的开关。
- **`compilation-config`**（含 `cudagraph_mode`、`cudagraph_capture_sizes`）：vLLM 自身的 CUDA Graph 编译配置，此处被约束为 `FULL_DECODE_ONLY` + `[1,2,4,8]`，与 Ascend 后端的图引擎接入相关。
- **OpenAI 兼容 HTTP 服务**：`/v1/models` 与 `/v1/completions` 表明该示例输出与 vLLM 上游 OpenAI 兼容 API 协议层直接对齐。
- **同类快速上手**：文件命名 `qwen3-0.6b-310p.inc.md` 中 `inc.md` 后缀暗示其为 `qwen3-0.6b-310p.md` 的 include 片段，与 vllm-ascend 文档的模块化拼装结构相关（其他章节如其他模型/硬件路径的 quick start 可能共享该 include 机制，但本文未明示引用）。

---

## 【使用方法】

**1. 启动 vLLM 服务（原文命令，逐字保留）：**

```bash
vllm serve Qwen/Qwen3-0.6B \
    --dtype float16 \
    --max-num-seqs 8 \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY","cudagraph_capture_sizes":[1,2,4,8]}' \
    --additional-config '{"ascend_compilation_config":{"enable_npugraph_ex":false}}' &
```

**2. 成功启动的标志日志（原文）：**

```text
INFO:     Started server process [3594]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**3. 查询模型列表（原文）：**

```bash
curl http://localhost:8000/v1/models | python3 -m json.tool
```

**4. 发送推理请求（原文）：**

```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen3-0.6B",
        "prompt": "Beijing is a",
        "max_completion_tokens": 5,
        "temperature": 0
    }' | python3 -m json.tool
```

**5. 优雅停止服务（原文流程）：**

```bash
VLLM_PID=$(pgrep -f "vllm serve")
kill -2 "$VLLM_PID"
```

原文同时强调在执行 `kill` 前需**确认 `VLLM_PID` 与本示例所启动服务一致**（因 `pgrep -f "vllm serve"` 可能误中同一环境中其他 `vllm serve` 进程），停止后输出日志为：

```text
INFO:     Shutting down FastAPI HTTP server.
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
```

最后通过 `Ctrl+D` 退出容器，完成整个启停流程。
