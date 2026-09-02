# 图编译Debug信息保存功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/debug_save.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/debug_save.md

# 图编译Debug信息保存功能 深度解读

## 【定位】

这篇文档描述了 **TorchAir 中通过复用 PyTorch 原生环境变量 `TORCH_COMPILE_DEBUG=1`，一键自动开启图编译过程全部调试信息（日志 + 图结构 dump）收集** 的能力，目标是替代 GE 图模式下需手动分别配置日志与文件 dump 的繁琐操作，把定位过程的信息收集化繁为简。

---

## 【技术要点】

1. **统一开关**：复用 PyTorch 原生 `TORCH_COMPILE_DEBUG`，**设置为 `1`** 时即自动开启所有必要的日志打印与文件 dump，无需逐项手动配置。
2. **日志收集三类**：PyTorch 原生 Dynamo 日志、TorchAir Python 层日志、TorchAir C++ 层日志，分别落在 `torchdynamo/debug.log` 与 `torchair/debug.log`。
3. **图结构 dump 范围**：AOT **前**的 GraphModule、AOT **后**的 GraphModule、公共 Pass 图优化过程中每个 Pass 的输出 FX 图（`.txt`），以及 GE 图优化前后及不同 Pass 处理后的图结构信息（`.pbtxt`/`.txt`/`.py`）。
4. **图结构文件类型**：可通过 `config.debug.graph_dump.type` 设置为 `txt`、`pbtxt` 或 `py`，详见 [图结构 dump 功能](./graph_dump.md)。
5. **后端约束**：仅支持使用编译后端 `npu_backend`（见 [`get_npu_backend`](../../api/torchair/get_npu_backend.md)），**不支持自定义后端**。
6. **Dynamo 额外日志配合**：需在脚本中通过 `torch._logging.set_logs(dynamo=logging.DEBUG, aot=logging.DEBUG, output_code=True, graph_code=True)` 打开 Dynamo/AOT 详细日志；同时**必须**在 `import torchair` 与 `from torchair import logger` 之前设置环境变量，否则会因日志模块导入先于环境变量生效，导致 `torchair/debug.log` 文件缺失。

---

## 【关键机制与数据】

### 工作原理（原文梳理）

- **入口**：检测到 `TORCH_COMPILE_DEBUG=1` 后，TorchAir 自动接管后续所有 dump 流程，不再要求用户手动调用 `torch._logging.set_logs` 之外的图 dump 接口。
- **目录生成**：在当前脚本路径下创建 `torch_compile_debug/run_<时间>-pid_<进程号>/` 根目录；**分布式场景**下运行目录名追加 `-rank_<rank_id>`（原文：`torch_compile_debug/run_<时间>-pid_<进程号>-rank_<rank_id>`）。
- **子目录分工**：
  - `torchdynamo/debug.log` ← Torch 原生 Dynamo 日志。
  - `torchair/debug.log` ← TorchAir Python 层 + C++ 层日志。
  - `torchair/model__<模型ID>/` 下按 `forward` / `backward` 分类存储图 dump 文件。
- **图 dump 命名规则**（原文给出序号–阶段对应关系）：
  - `000_aot_<forward|backward>_graph.txt` — AOT 后的 GraphModule；
  - `001_…_after_${pass1_name}.txt` / `002_…_after_${pass2_name}.txt` — 公共 Pass 图优化每个 Pass 的输出 FX 图；
  - `003_aot_<forward|backward>_original_ge_graph.pbtxt` — **所有 GE 图优化处理前**的 GE 图；
  - `004_…_after_${pass3_name}.pbtxt` / `005_…_after_${pass4_name}.pbtxt` — GE 图优化中不同 Pass 处理后的 GE 图；
  - `006_aot_<forward|backward>_optimized_ge_graph.pbtxt` — **所有 GE 图优化处理后**的 GE 图；
  - `dynamo_out_graph.txt` — AOT 前的 GraphModule。
- **示例运行行为**（原文示例）：
  - 第一次构造 `torch.randn(10, 10, requires_grad=True, device=device)` → 触发前向 + 反向编译，生成 `forward/` 与 `backward/` 子目录；
  - 第二次构造 `torch.randn(20, 20, requires_grad=False, device=device)` → 仅前向推理，对应 `forward/`；
  - 不同 shape 触发重新编译，因此示例中可见 `model__0`（首次编译产物）与 `model__1`（第二次推理编译产物）两个模型 ID 目录。
- **性能数据**：原文未涉及。

### 数据流概览

```
用户脚本 → torch.compile(backend=npu_backend)
        → 检测 TORCH_COMPILE_DEBUG=1
        → 自动落盘：
            ├── torchdynamo/debug.log         (Dynamo 日志)
            └── torchair/
                 ├── debug.log                 (Python + C++ 日志)
                 └── model__<id>/
                      ├── dynamo_out_graph.txt                (AOT 前 GraphModule)
                      ├── forward/000_aot_forward_graph.txt   (AOT 后 GraphModule)
                      ├── forward/001...002...txt              (公共 Pass FX 图)
                      ├── forward/003_aot_forward_original_ge_graph.pbtxt
                      ├── forward/004...005...pbtxt           (GE 各 Pass 后)
                      └── forward/006_aot_forward_optimized_ge_graph.pbtxt
```

---

## 【表格解读】

**表 1 信息收集表** （原文逐字还原）

| 信息类型 | 说明 |
|---|---|
| 日志信息 | PyTorch 原生 Dynamo 日志<br>TorchAir Python 层日志<br>TorchAir C++ 层日志 |
| Debug信息 | AOT 前的 GraphModule<br>AOT 后的 GraphModule<br>公共 Pass 图优化过程中每个 Pass 的输出 FX 图（txt 文件）<br>GE 图优化前后及不同 Pass 处理后的图结构信息：该图结构信息可通过 config.debug.graph_dump.type 设置 txt、pbtxt、py 文件类型，可参考[图结构 dump 功能](./graph_dump.md)。 |

**逐行解读**：

- **日志信息**行：列举了三类并行落盘的日志——`torchdynamo/debug.log`（Dynamo）、`torchair/debug.log` 中的 Python 层条目（框架/前端代码 trace）、以及同一 `debug.log` 中的 C++ 层条目（底层算子/图编译 trace）。
- **Debug 信息**行拆 4 个子项：
  1. *AOT 前的 GraphModule* — 即 `dynamo_out_graph.txt`，对应 Dynamo trace 后、AOT 编译前的 FX 图；
  2. *AOT 后的 GraphModule* — 即 `000_aot_<fwd|bwd>_graph.txt`，对应 AOTAutograd 阶段产物；
  3. *公共 Pass 图优化每个 Pass 的 FX 图（txt）* — 即 `001_…_after_${pass1_name}.txt` / `002_…_after_${pass2_name}.txt` 等，反映 TorchAir 公共 Pass 链逐步优化后的中间状态；
  4. *GE 图优化前后及不同 Pass 处理后的图结构信息* — 即 `003_aot_…_original_ge_graph.pbtxt` → `004/005_…_after_${pass3/4_name}.pbtxt` → `006_…_optimized_ge_graph.pbtxt`；文件类型由 `config.debug.graph_dump.type` 决定，支持 `txt` / `pbtxt` / `py`，并通过链接指引到 [图结构 dump 功能](./graph_dump.md)。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游 / 触发**：依赖 **PyTorch 原生 `TORCH_COMPILE_DEBUG` 环境变量**以及 `torch._logging.set_logs`（Dynamo/AOT 日志开关）。未设置环境变量或设置时序错误均会导致产物缺失（具体见"使用方法"中的 NOTE）。
- **核心 API**：[`get_npu_backend`](../../api/torchair/get_npu_backend.md) — 本功能要求使用 `torchair.get_npu_backend(compiler_config=config)` 构造后端，并注入 `CompilerConfig` 以便进一步配置 `config.debug.graph_dump.type`。
- **相关特性**：[图结构 dump 功能](./graph_dump.md) — 本文档中 GE 图 dump 的文件类型选择（`txt`/`pbtxt`/`py`）即由此特性提供，文档明确将其作为"可参考"对象。
- **图编译链路组件**：
  - **Dynamo**（Torch 原生）→ 输出 `torchdynamo/debug.log` 与 AOT 前的 GraphModule；
  - **AOT（FX Graph / AOTAutograd）** → 输出 AOT 后 GraphModule 与 AOT 阶段 FX Pass 序列；
  - **TorchAir 公共 Pass**（C++ 层）→ 输出 `001_…/002_…` 等中间 FX 图与 `debug.log`；
  - **GE 图优化**（昇腾 GE）→ 输出 `003_…_original` 至 `006_…_optimized` 的 `.pbtxt` 序列。
- **产物物理路径**：以 `torch_compile_debug/` 为根目录，分布式场景下追加 `-rank_<rank_id>` 后缀。

---

## 【使用方法】

### 启用方式

- **方法一（终端环境变量）**：
  ```bash
  export TORCH_COMPILE_DEBUG=1
  python main.py
  ```

- **方法二（Python 脚本开头设置）**：
  ```python
  import os
  # 配置环境变量
  os.environ["TORCH_COMPILE_DEBUG"] = "1"
  import torch
  import torch.nn as nn
  import torchair
  from torchair import logger
  ```
  > **NOTE（原文约束）**：若在 `import torchair` 及 `from torchair import logger` **之后**才设置环境变量，会因环境变量未在日志模块导入前生效，导致目录下缺失 `torchair/debug.log` 文件。

### 配置项

- `config.debug.graph_dump.type`：取值为 `"txt"` / `"pbtxt"` / `"py"` 之一，控制 GE 图 dump 文件类型。
- 需配合 `torch._logging.set_logs(dynamo=logging.DEBUG, aot=logging.DEBUG, output_code=True, graph_code=True)` 打开 Dynamo/AOT 详细日志。
- 编译后端必须为 [`get_npu_backend`](../../api/torchair/get_npu_backend.md) 返回的 `npu_backend`，**不支持自定义后端**。

### 完整示例（原文摘录要点）

```python
import os
os.environ["TORCH_COMPILE_DEBUG"] = "1"
import torch
import torch_npu
import torchair
import logging
torch._logging.set_logs(dynamo=logging.DEBUG, aot=logging.DEBUG,
                        output_code=True, graph_code=True)

config = torchair.CompilerConfig()
config.debug.graph_dump.type = "pbtxt"
npu_backend = torchair.get_npu_backend(compiler_config=config)
device = "npu:0"

class Model(torch.nn.Module):
    def forward(self, x):
        return 2 * x

model = Model().to(device)
model = torch.compile(model, backend=npu_backend, dynamic=False)

# 第一次：requires_grad=True，触发前向 + 反向编译
x = torch.randn(10, 10, requires_grad=True, device=device)
out = model(x)
loss = torch.nn.MSELoss()(out, torch.randn(10, 10, device=device))
loss.backward()

# 第二次：requires_grad=False，仅前向推理
x = torch.randn(20, 20, requires_grad=False, device=device)
out = model(x)
```

### 产物目录默认位置

```
torch_compile_debug/run_<时间>-pid_<进程号>/        # 单机
torch_compile_debug/run_<时间>-pid_<进程号>-rank_<rank_id>/  # 分布式
```

具体子目录、文件名规则详见前文【关键机制与数据】。

## 图文联合解读

- `graph_compile_6.png`: **图文联合解读：**

图中展示了图编译的四阶段流程——GraphModule→AOT_AutoGrad→JointGraph→前反向切图→公共Pass优化→GE图→GE图优化，并以四个蓝色标注框标记Debug信息保存点（①AOT前/②AOT后GraphModule、③每个公共Pass后的FX图、④GE图优化前后及Pass处理后的图结构）。

该图直观论证了`TORCH_COMPILE_DEBUG=1`可自动覆盖**前向切图、Pass优化、GE编译全链路**的调试信息收集，与文档"简化定位、自动开启所有日志与dump"的论点形成对应，为表1中Debug信息类型提供可视化流程依据。
