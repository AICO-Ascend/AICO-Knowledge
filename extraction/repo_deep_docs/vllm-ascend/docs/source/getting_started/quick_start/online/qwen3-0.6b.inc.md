# qwen3-0.6b.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/online/qwen3-0.6b.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/online/qwen3-0.6b.inc.md

# 文档深度解读：vllm-ascend Qwen3-0.6B 快速启动指南

---

## 【定位】

本文档是 vllm-ascend 镜像仓库中针对 Qwen3-0.6B 模型的一份**在线服务（online serving）快速启动操作手册**，解决"用户如何在最小配置下通过 `vllm serve` 一条命令拉起 OpenAI 兼容 API 服务、并完成查询模型列表、发起推理、优雅停机"这一端到端使用问题。

---

## 【技术要点】

1. **入口命令**：使用 `vllm serve Qwen/Qwen3-0.6B &`（以 `&` 放入后台）启动服务；文档明确指出该示例**使用默认模型加载配置（the default model loading configuration）** 完成验证。
2. **启动成功判据**：观察到 `Started server process`、`Application startup complete`、`Uvicorn running on http://0.0.0.0:8000` 三条日志即视为启动成功；服务监听地址为 `http://0.0.0.0:8000`，端口 **8000**。
3. **模型列表查询**：通过 `GET /v1/models`（OpenAI 兼容 endpoint）调用 `curl http://localhost:8000/v1/models | python3 -m json.tool` 获取并格式化输出。
4. **推理请求调用**：通过 `POST /v1/completions` 发送 prompt，关键参数为：`model="Qwen/Qwen3-0.6B"`、`prompt="Beijing is a"`、`max_completion_tokens=5`、`temperature=0`；响应同样经 `python3 -m json.tool` 格式化。
5. **优雅停机机制**：使用信号 `SIGINT`（即 `kill -2`）模拟前台进程 `Ctrl+C`；通过 `pgrep -f "vllm serve"` 获取 PID。
6. **环境隔离与退出容器**：停机后通过 `Ctrl+D` 退出容器；并以 `warning` 提示框特别提醒：`pgrep -f "vllm serve"` 可能在当前环境匹配到其他 `vllm serve` 进程，**停机前必须人工确认 `VLLM_PID` 归属**。

---

## 【关键机制与数据】

**工作原理 / 数据流**：

- 启动流程：用户执行 `vllm serve Qwen/Qwen3-0.6B &` → vLLM 框架加载默认配置 → 拉起 FastAPI/Uvicorn HTTP 服务（监听 `0.0.0.0:8000`）→ 应用启动完成（`Application startup complete`）。
- 推理调用流程：客户端构造符合 OpenAI 兼容协议的 JSON 请求 → 通过 HTTP `POST /v1/completions` 提交 → 服务端返回 `completion` 文本 → 客户端用 `python3 -m json.tool` 管道进行 JSON 美化输出。
- 停机流程：用户捕获 `$VLLM_PID` → 发送 `SIGINT`（信号 2）→ FastAPI 打印 `Shutting down FastAPI HTTP server` → 应用进入 `Waiting for application shutdown` → 最终 `Application shutdown complete`。

**原文数据**（原文中明确出现的可观测信号/参数）：

- 原文：启动进程示例 PID = `3594`
- 原文：服务监听端口 = `8000`，绑定地址 = `0.0.0.0`
- 原文：示例 prompt = `"Beijing is a"`，生成上限 = `max_completion_tokens=5`，采样温度 = `temperature=0`
- 原文：停机信号 = `kill -2`（对应 `SIGINT`）
- 原文：进程查找 = `pgrep -f "vllm serve"`
- 原文：容器退出 = `Ctrl+D`

---

## 【表格解读】

**原文无表格。**

（全文由 `bash`/`text` 代码块和一段 `warning` 提示框组成，未出现任何参数表、性能对比表或配置项表。）

---

## 【公式解读】

**原文无公式。**

（文档为操作性快速上手指南，未涉及 LaTeX 数学公式或伪代码公式推导。）

---

## 【关联】

**文档内部链接：原文标注为「(无)」**，即本文未通过文末 `内部链接` 段显式关联其他特性/模块。

从内容可观察到的隐含上下游关系（仅基于原文措辞推断，不臆造）：

- 依赖 **vLLM 主框架的 OpenAI 兼容 API 端点**：`/v1/models`、`/v1/completions`，这是文档能以标准 `curl` 调用的前提。
- 依赖 **vllm-ascend 适配层**：作为 vllm 镜像的衍生仓库，本文档默认假设 Ascend NPU 后端已完成与 vLLM 主体框架的对接（原文以"the default model loading configuration"隐含该适配已就绪）。
- 与**后台/前台进程控制**相关：使用 shell 的 `&`、`pgrep`、`kill` 等通用工具实现后台启动与优雅停机。
- 与**容器化运行**相关：末尾 `Ctrl+D` 退出容器，暗示整个示例预期在容器内执行（与仓库名 `vllm-ascend` 的镜像分发形式一致）。

---

## 【使用方法】

启用方式 / 配置项 / 命令（**严格逐字保留原文命令**）：

### 1. 启动服务（后台）
```bash
vllm serve Qwen/Qwen3-0.6B &
```

### 2. 验证启动成功（观察日志）
原文期望出现的关键日志字样：
```
INFO:     Started server process [3594]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. 查询模型列表
```bash
curl http://localhost:8000/v1/models | python3 -m json.tool
```

### 4. 向模型发送补全请求
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

### 5. 优雅停机（需先人工确认进程归属，原文已加 warning 强调）
```bash
VLLM_PID=$(pgrep -f "vllm serve")
kill -2 "$VLLM_PID"
```
停机过程期望输出：
```
INFO:     Shutting down FastAPI HTTP server.
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
```

### 6. 退出容器
```text
Ctrl+D
```

**关于自定义模型加载配置项**（如 dtype、device、tensor-parallel-size 等）：**原文未涉及**——文档明确写明本示例使用"the default model loading configuration"，未给出任何额外的配置开关或环境变量示例。
