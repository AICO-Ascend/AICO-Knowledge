# TorchAir Python层日志打印

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/python_log_print.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/python_log_print.md

# TorchAir Python层日志打印 — 一体化深度解读

## 【定位】

本文档解决 TorchAir 用户在 NPU 上做图模式推理时**Python 层（图编译过程）日志无法查看、级别无法配置、关键流程耗时难以统计**的问题，描述 TorchAir 在 Python 侧通过 `logger.setLevel` 与 `torch._logging.set_logs` 提供的两级（Ascend IR 编译 / Dynamo 编译）调试日志能力。

## 【技术要点】

- **日志主入口**：`torchair.logger`，通过 `logger.setLevel(...)` 切换 Python 层日志级别，用于"图编译过程"信息打印与问题定位。
- **支持的 5 个级别**：`logging.DEBUG`、`logging.INFO`、`logging.WARNING`、`logging.ERROR`，以及 TorchAir 自定义的 `EVENT_LEVEL`。
- **默认级别**：`logger.setLevel` 的默认值是 `logging.ERROR`（原文写为 "logging.ERROR"，对应日志级别 ERROR）。
- **EVENT_LEVEL 自定义行为**：TorchAir 自定义的 EVENT 级别，开启后**只输出 ERROR 与 EVENT 日志**，用于统计 TorchAir 关键流程耗时。
- **Ascend IR 图编译日志开启**：
  ```python
  from torchair import logger
  logger.setLevel(logging.DEBUG)
  # 或启用 EVENT_LEVEL：
  # from torchair.core.utils import EVENT_LEVEL
  # logger.setLevel(EVENT_LEVEL)
  ```
- **Dynamo 原生编译日志开启**：
  ```python
  torch._logging.set_logs(dynamo=logging.DEBUG, aot=logging.DEBUG,
                          output_code=True, graph_code=True)
  ```
- **日志格式（TorchAir 侧）**：`[DEBUG] TORCHAIR(<pid>,python):<timestamp> [:<lineno>]<pid> <message>`，例如 `[npu_fx_compiler.py:242]`。
- **日志格式（Dynamo 侧）**：`[<timestamp>] [<rank>] <logger_name>: [DEBUG] <message>`，例如 `[0/0] torch._dynamo.output_graph.__graph_code: [DEBUG] ...`。

## 【关键机制与数据】

### 工作原理

TorchAir 的图编译日志分两层：

1. **Ascend IR 编译层**（`torchair.logger`）：针对 `npu_fx_compiler.py` 等 TorchAir 内部编译器流程，会在关键节点（如 `before sym input optimization` / `after sym input optimization`）打印当前 FX Graph 的 IR 文本，并逐个节点 dump `target`、`input` 张量的 meta / npu 信息（如 `dtype=torch.float32, size=[1,1,2,8]`），便于用户在图编译失败或精度异常时定位变换前后的差异。
2. **Dynamo 编译层**（`torch._logging`）：针对 PyTorch 原生 `torch._dynamo`，开启 `output_code=True` 与 `graph_code=True` 后会打印 `TRACED GRAPH`、`TRACED GRAPH TENSOR SIZES` 等，呈现 GraphModule 的 Python 源码形式以及每个中间张量的形状，例如 `l_var_: (1, 1, 2, 8)` → `scatter_update: (1, 1, 2, 8)`。

### 原文日志样例中的关键数据流（原文 Ascend IR DEBUG 样例）

| 阶段（原文日志行） | 节点 / target | 输入 | 输出 |
|---|---|---|---|
| `before sym input optimization` | `%scatter_update = call_function[target=torch.ops.npu.scatter_update.default]` | `(%arg0_1, %arg1_1, %arg2_1, -2)` | `(scatter_update,)` |
| `after sym input optimization` | 同上（IR 未发生结构变化） | 同上 | 同上 |
| 节点 dump：`target: arg0_1` | arg0_1 | — | `FakeTensor(dtype=torch.float32, size=[1, 1, 2, 8])` 对应 `npu:Tensor(arg0_1:0, DT_FLOAT, [1, 1, 2, 8])` |
| 节点 dump：`target: arg1_1` | arg1_1 | — | `FakeTensor(dtype=torch.int64, size=[1])` 对应 `npu:Tensor(arg1_1:0, DT_INT64, [1])` |
| 节点 dump：`target: arg2_1` | arg2_1 | — | `FakeTensor(dtype=torch.float32, size=[1, 1, 1, 8])` 对应 `npu:Tensor(arg2_1:0, DT_FLOAT, [1, 1, 1, 8])` |
| 节点 dump：`target: npu.scatter_update.default` | scatter_update | input0=`[1,1,2,8] float32`、input1=`[1] int64`、input2=`[1,1,1,8] float32`、input3=`-2` | `npu:Tensor(Scatter:0, DT_FLOAT, [1, 1, 2, 8])` |

> 原文：从"before"到"after sym input optimization"的两次 dump 中算子结构未变化，说明此处符号输入优化未改写 IR；`input 3: -2` 即 `scatter_update` 的 `dim` 参数。

### 原文 Dynamo 样例关键数据流

| 图节点 | 形状 |
|---|---|
| `l_var_` | `(1, 1, 2, 8)` |
| `l_indices_` | `(1,)` |
| `l_updates_` | `(1, 1, 1, 8)` |
| `scatter_update` | `(1, 1, 2, 8)` |

> 原文：Dynamo 触发原因 `GraphCompileReason(reason='return_value', user_stack=[<FrameSummary ... test_scatter_update.py line 17 in forward>], graph_break=False)`，并伴随 `Tabulate module missing, please install tabulate to log the graph in tabular format, logging code instead:` 提示信息。

## 【表格解读】

原文无独立结构化表格。但文档以代码块+日志样例形式给出了两张可类比"配置/输出对照"的表，已在上节「关键机制与数据」中按原文逐行还原：

- **Ascend IR DEBUG 日志**：按"编译阶段 → 节点 → 输入 → 输出"组织，原文逐字保留 `target=torch.ops.npu.scatter_update.default`、`args = (%arg0_1, %arg1_1, %arg2_1, -2)`、`dtype=DT_FLOAT/DT_INT64`、`size=[1,1,2,8]/[1]/[1,1,1,8]` 等关键字段。
- **Dynamo 原生日志**：按"TRACED GRAPH + 张量尺寸"组织，原文逐字保留 `l_var_: (1, 1, 2, 8)`、`l_indices_: (1,)`、`l_updates_: (1, 1, 1, 8)`、`scatter_update: (1, 1, 2, 8)` 等形状。

## 【公式解读】

原文无公式（无 LaTeX、无伪代码形式公式）。文档中出现的 `args = (%arg0_1, %arg1_1, %arg2_1, -2)` 是 FX Graph 节点的参数列表 IR 片段（非数学公式），其中 `-2` 是 `scatter_update` 的 `dim` 参数值。

## 【关联】

- 与 **Ascend IR 图编译**流程上下游的关系：通过 `torchair.logger` 输出的 DEBUG 日志主要来自 `npu_fx_compiler.py`（如 `:112 / :113 / :115 / :119 / :238 / :242`），覆盖"sym input optimization"前后 FX Graph 对照以及逐节点 `input/output` meta 打印，构成 TorchAir Python 层的图编译可观测性链路。
- 与 **Dynamo 编译**的关系：`torch._logging.set_logs` 控制 PyTorch 原生 Dynamo 链路（`torch._dynamo.output_graph`、`__graph_code`、`__graph`、`__graph_sizes`），与 TorchAir 的 Ascend IR 编译日志**并列互补**：前者面向 `torch.compile` 捕获阶段，后者面向 TorchAir 自有 FX → Ascend IR 转换阶段。
- 与 **`logging` 标准库**的关系：除 `EVENT_LEVEL` 为 TorchAir 自定义外，其余四个级别与 Python 原生 `logging` 用法一致，可参考 Python 官网 `logging` 模块（原文给出 `https://docs.python.org/3.8/library/logging.html`）。
- 与 **`EVENT_LEVEL` 自定义机制**的关系：`EVENT_LEVEL` 只输出 ERROR 与 EVENT 两类日志，专用于"关键流程耗时"统计，是与 Python `logging` 体系的差异点。

## 【使用方法】

**Ascend IR 图编译（TorchAir Python 层）**：

```python
import logging
import torch_npu
from torchair import logger

# 设置 Debug 日志级别
logger.setLevel(logging.DEBUG)

# 设置 EVENT 日志级别（TorchAir 自定义）
# from torchair.core.utils import EVENT_LEVEL
# logger.setLevel(EVENT_LEVEL)
```

- 默认级别：`logging.ERROR`（即不显式调用 `setLevel` 时只输出 ERROR 及以上）。

**Dynamo 编译（PyTorch 原生日志）**：

```python
import logging
torch._logging.set_logs(dynamo=logging.DEBUG,
                         aot=logging.DEBUG,
                         output_code=True,
                         graph_code=True)
```

- `dynamo` / `aot`：分别控制 Dynamo 前端与 AOT 后端的日志级别。
- `output_code=True`：打印捕获到的 GraphModule Python 源码形式（`TRACED GRAPH`）。
- `graph_code=True`：打印图代码（与 `__graph_code` 日志项对应）；若环境中未安装 `tabulate`，原文日志会提示 `Tabulate module missing, please install tabulate to log the graph in tabular format, logging code instead:`，回退为代码形式输出。
