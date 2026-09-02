# Python Multiprocessing

> 仓 `vllm` · 路径 `docs/design/multiprocessing.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/multiprocessing.md

# vLLM Python Multiprocessing 设计文档深度解读

## 【定位】

本文档阐述 vLLM 在使用 Python `multiprocessing` 模块时所面临的"库模式约束"与"依赖兼容性"双重挑战，描述 v0/v1 引擎对 `spawn`/`fork`/`forkserver` 三种启动方式的选择策略、已知失败场景与未来工作方向。

## 【技术要点】

- **三种启动方式语义与默认值**：`spawn` 是 Windows/macOS 默认；`fork` 是 Linux Python 3.14 之前的默认；`forkserver` 是 Linux Python 3.14 及之后默认。
- **v0 状态**：环境变量 `VLLM_WORKER_MULTIPROC_METHOD` 控制启动方式，默认 `fork`；通过 `vllm` 命令调用时使用 `spawn`；`multiproc_xpu_executor` 强制使用 `spawn`；`all_reduce_utils.py` 与 `api_server.py` 中也硬编码了 `spawn`。
- **v1 状态**：曾存在 `VLLM_ENABLE_V1_MULTIPROCESSING`（默认 off）控制 v1 engine core 是否多进程；开启时 `LLMEngine` 会创建新进程运行 engine core。
- **v1 "best effort" 决策策略**：(1) 默认 `fork`；(2) 当 vLLM 掌控主进程时使用 `spawn`；(3) 若检测到 `cuda` 已被初始化，强制 `spawn` 并发出 WARNING 日志。
- **已知失败场景**：用户代码在调用 vLLM 之前已初始化 `cuda`，且没有 `__main__` 守卫，此时会同时触发 vLLM 的 WARNING 与 Python 的 `RuntimeError`。
- **替代方案**：探索 `forkserver`-like 自定义 `vllm-manager` 子进程、或类似 `loky` 的第三方库。

## 【关键机制与数据】

- **工作原理**（原文：v0 与 v1 的多进程选择机制）：
  - vLLM 作为库被调用时，无法保证用户主模块含有 `if __name__ == "__main__":` 守卫，使用 `spawn`/`forkserver` 时新进程会重新执行主模块代码，可能导致无限递归等问题。
  - `fork` 在 Linux 上速度最快，但不兼容依赖线程的库；在 macOS 上可能崩溃。
  - 多依赖（PyTorch CUDA / 共享 CUDA tensor / Habana Gaudi dataloader）声明偏好或要求 `spawn`，且在这些依赖初始化后再使用 `fork` 会触发已知问题。

- **数据流**（原文：v1 engine core 启动路径）：`LLMEngine` → 创建新进程 → 在子进程中运行 `engine core`（基于 `core_client.py` 的客户端）。

- **日志原文（vLLM WARNING）**：
  > `WARNING 12-11 14:50:37 multiproc_worker_utils.py:281] CUDA was previously initialized. We must use the spawn` multiprocessing start method. Setting `VLLM_WORKER_MULTIPROC_METHOD` to 'spawn'.`

- **Python 异常原文**：`RuntimeError: An attempt has been made to start a new process before the current process has finished its bootstrapping phase.`，提示用户参考 `multiprocessing.html` 中 "Safe importing of main module" 一节。

- **性能数据**：原文未涉及。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **调试与已知问题** → 通过文首与文末双重指引链接到 `docs/usage/troubleshooting.md#python-multiprocessing`，作为本文档处理失败场景时的官方解决方案出处。
- **环境变量层** → `VLLM_WORKER_MULTIPROCESSING`（v1，已废弃/默认 off）与 `VLLM_WORKER_MULTIPROC_METHOD`（v0/v1 通用）在 `vllm/envs.py` 中定义。
- **执行器层** → `multiproc_xpu_executor.py` 强制 `spawn`；`all_reduce_utils.py`（集合通信路径）、`api_server.py`（OpenAI 入口）也硬编码 `spawn`。
- **引擎核心层** → v1 中 `v1/engine/llm_engine.py` 与 `v1/engine/core_client.py` 共同实现 engine core 子进程化。
- **脚本入口层** → `vllm/scripts.py` 在 CLI 路径下选择 `spawn`，与"掌控主进程则用 spawn"的策略一致。
- **上游依赖** → PyTorch `notes/multiprocessing.html#cuda-in-multiprocessing`、`sharing-cuda-tensors` 文档、Habana Gaudi `torch-multiprocessing-for-dataloaders` 文档共同构成 `spawn` 偏好/要求的来源。
- **历史/Issue 关联** → GitHub PR `#8823` 被引用，作为相关变更的追踪入口。
- **未来方向** → 提及 `joblib/loky` 作为潜在替代实现，属于 vLLM worker 管理层面的横向探索。

## 【使用方法】

- **指定启动方式（v0 与 v1 共用）**：设置环境变量 `VLLM_WORKER_MULTIPROC_METHOD`，可选值 `spawn` / `fork` / `forkserver`（原文：v0 默认 `fork`，通过 `vllm` CLI 时为 `spawn`）。
- **禁用 v1 engine core 多进程**：设置 `VLLM_ENABLE_V1_MULTIPROCESSING`（原文：默认 off；v1 中已属历史状态，文档未明示是否仍在主线维护）。
- **强制 spawn 的场景**（无需用户配置）：
  - 通过 `vllm` 命令行启动（`vllm/scripts.py`）。
  - XPU 执行器路径（`multiproc_xpu_executor.py`）。
  - `all_reduce_utils.py` 与 `api_server.py` 中的特定调用点。
- **修复已知失败**：当看到 vLLM 的 "CUDA was previously initialized" WARNING 或 Python 的 `RuntimeError` 时，按提示添加 `if __name__ == "__main__":` 守卫，或关闭多进程；详细方案见 `docs/usage/troubleshooting.md#python-multiprocessing`。
- **辅助命令/参数**：原文未涉及。
