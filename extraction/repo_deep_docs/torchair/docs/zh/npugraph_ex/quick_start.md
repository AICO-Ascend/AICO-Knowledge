# npugraph\_ex快速上手

> 仓 `torchair` · 路径 `docs/zh/npugraph_ex/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/npugraph_ex/quick_start.md

# TorchAir `npugraph_ex` 快速上手 深度解读

## 【定位】

本文是 TorchAir 中 `npugraph_ex` 后端的入门指南，告诉用户如何用一行 `torch.compile(model, backend="npugraph_ex", fullgraph=True, dynamic=False)` 把 PyTorch 模型切换到基于 aclgraph 的整图捕获加速模式，并概览其功能清单与异常定界方法。

## 【技术要点】

1. **后端身份**：`npugraph_ex` 是 `torch.compile` 的一个 backend 选项，提供基于 aclgraph（即"捕获模式"）的整图加速方案，其底层实现可参考《CANN应用开发》"ACL Graph > 任务更新"章节。
2. **使用约束**：主要面向在线推理场景，**不支持反向流程 capture 成图，也不支持随机数算子 capture**；与 `torch.cuda.CUDAGraph` 约束一致，因此**不支持 stream sync、动态控制流**等。
3. **调用方式**：通过 `torch.compile(model, backend="npugraph_ex", fullgraph=True, dynamic=False)` 启用；`backend` 必须显式传入 `"npugraph_ex"`，`mode` 参数昇腾 NPU **暂不支持**。
4. **功能分层**：通过 `options` 参数配置基础功能（12 项），进阶功能（6 项）与 DFX 功能（3 项）通过其它接口/环境变量启用。
5. **三层问题定界**：先用 `backend="aot_eager"` 排查用户脚本，再开 `force_eager` 排查是否 aclgraph 自身问题，再开 `force_recapture` 区分是图捕获阶段问题还是输入/输出内存处理阶段问题。
6. **扩展机制**：通过 `torch.npu.npugraph_ex.compile_fx` 配合 `aot_module_simplified` 自定义 `fw_compiler`，可在内置 Pass 之外注入自定义 FX 图优化。

## 【关键机制与数据】

- **整图捕获要求**（原文）：`fullgraph=True` 时"要求将整个函数或模型捕获到一个单一的计算图中。如果编译器遇到无法追踪到该单一图中的代码时（即'图中断'），则会引发错误"。
- **disable 行为**（原文）：`disable=True` 时"采用单算子模式"，等价于关闭 `torch.compile` 能力。
- **force_eager 用途**（原文）：用于定界 aclgraph 问题——"如果用户脚本使用 force_eager 运行异常，则可能是 npugraph_ex 存在问题，否则可能是 aclgraph 的 Runtime 底层问题"。
- **force_recapture 用途**（原文）："启用 force_recapture 后，每次执行都会重新捕获 aclgraph。通过对比重捕获前后执行效果，如果 force_recapture 后存在问题，说明问题是出在图捕获执行阶段。如果 force_recapture 后功能正常，说明问题是出在对输入输出内存处理阶段。"
- **aot_eager 角色**（原文）："backend='aot_eager' 是 PyTorch 社区为用户自定义后端做一个简单使用 Eager 模式直接运行 fx.graph 的方式"。
- **功能层级**（原文）："基础功能通过 torch.compile 的 options 参数进行配置"；进阶与 DFX 功能通过其它方式（详见表 3、表 4）。
- **集合通信默认行为**（原文）："调用 torch.compile 时**默认已支持**集合通信算子入图"。
- **本文档未给出任何量化性能数据**（如延迟/吞吐提升百分比、显存节省量等均无），只描述功能定位。

## 【表格解读】

### 表 1　torch.compile 参数说明（aclgraph 模式）

| 参数名 | PyTorch 原生参数说明 | aclgraph 模式下参数说明 |
|---|---|---|
| model | **必选参数**。入图部分的模型或者函数。 | 与原生含义一致。 |
| fullgraph | 可选参数，bool 类型。是否捕获整图进行优化。<br>False（缺省值）：非整图优化。<br>True：捕获整图优化。 | 建议设置为 True，要求将整个函数或模型捕获到一个单一的计算图中。如果编译器遇到无法追踪到该单一图中的代码时（即"图中断"），则会引发错误。 |
| dynamic | 可选参数，bool 类型或 None。是否启用动态 Shape 追踪。<br>None（缺省值）：自动检测是否启用动态 Shape 追踪。<br>False：不启用动态 Shape 追踪。<br>True：启用动态 Shape 追踪。 | 与原生含义一致。 |
| backend | **必选参数**，后端选择，缺省值为"inductor"。 | 需显式传入 backend="npugraph_ex"。 |
| mode | 开销模式，内存开销模式选择，缺省值为 None。 | 昇腾 NPU**暂不支持**。 |
| options | 优化选项，缺省值为 None。 | 提供多种基础功能配置，具体参见[基础功能](#fig2)。 |
| disable | 可选参数，bool 类型。是否关闭 torch.compile 能力。<br>False（缺省值）：开启 torch.compile 能力。<br>True：关闭 torch.compile 能力，采用单算子模式。 | 与原生含义一致。 |

**逐行解读**：
- **model**：调用入口，最常用的就是传入 `nn.Module`，aclgraph 下含义不变。
- **fullgraph**：这是 aclgraph 模式下**最关键的开关**，原文建议设为 `True`，因为非整图优化会破坏 aclgraph 的捕获完整性，遇到图中断会直接报错，比 silent fallback 更易排查。
- **dynamic**：aclgraph 当前对动态 Shape 没有特殊说明，即沿用 PyTorch 自身行为，原文未给出 aclgraph 模式下对动态 Shape 的明确支持矩阵。
- **backend**：**唯一必须修改**的参数；PyTorch 默认的 "inductor" 后端在昇腾上不可用，必须显式写 `"npugraph_ex"`。
- **mode**：是 PyTorch 用于切换"默认/最大自动调优/减少开销"等模式的参数，原文直接标注 NPU 暂不支持。
- **options**：aclgraph 的核心配置入口，承载"基础功能"表中的 12 项能力。
- **disable**：是关闭整套 `torch.compile` 的总开关，开启后回退到单算子执行，相当于关闭 aclgraph。

---

### 表 2　npugraph_ex 基础功能

| 功能 | 功能说明 |
|---|---|
| [force_eager 功能](./basic/force_eager.md) | 图执行前是否使用 Eager 模式运行。 |
| [force_recapture 功能](./basic/force_recapture.md) | 是否强制每次执行时重新捕获 aclgraph。 |
| [FX 图优化 Pass 配置功能](./basic/inplace_pass.md) | 是否开启 FX 图优化能力。以减少计算过程中的内存搬运，从而提升性能。 |
| [FX 图算子融合 Pass 配置功能](./basic/pattern_fusion_pass.md) | 是否开启 FX 图算子融合 Pass。该 Pass 基于已有 Aten IR 进行融合，从而提升性能。 |
| [aclgraph 间内存复用功能](./basic/memory_reuse.md) | aclgraph 间内存复用功能，支持多种模式。 |
| [静态 Kernel 编译功能](./basic/static_kernel_compile.md) | 是否开启静态 Kernel 编译。 |
| [冗余算子消除功能](./basic/remove_noop_ops.md) | 是否对冗余 Kernel 进行优化处理。 |
| [固定权重类输入地址功能](./basic/frozen_parameter.md) | 图执行时是否固定权重类输入地址。 |
| [重捕获次数限制功能](./basic/capture_limit.md) | 设置重捕获次数。 |
| [集合通信入图](./basic/communication_graph.md) | 实现集合通信算子 Ascend Converter，调用 torch.compile 时默认已支持集合通信算子入图。 |
| [Cat 算子消除功能](./basic/remove_cat_ops.md) | 是否开启 Cat 算子消除优化以减少内存拷贝和临时张量分配，提升执行性能。 |
| [图捕获安全策略配置](./basic/capture_error_mode.md) | 控制图捕获过程中，对某些可能不安全操作（如分配 device 内存）的处理策略。 |

**逐行解读**：基础功能全部通过 `options={...}` 字典传入。`force_eager` 与 `force_recapture` 是**问题定界**专用开关（后文会用到）；`inplace_pass`、`pattern_fusion_pass` 都是面向 FX 层 IR 的优化 Pass，作用分别是减少内存搬运和做算子融合；`memory_reuse` 是 aclgraph 特有的图间内存复用（支持多种模式）；`static_kernel_compile` 走静态 Kernel 编译路径；`remove_noop_ops` 删冗余算子；`frozen_parameter` 在多次执行间固定权重输入地址（典型于推理场景）；`capture_limit` 限制重新捕获次数以避免反复 capture 带来的开销；`communication_graph` 是集合通信算子的入图支持且**默认开启**；`remove_cat_ops` 减少 Cat 产生的临时张量；`capture_error_mode` 处理 capture 过程中可能不安全（如直接分配 device 内存）的操作。

---

### 表 3　npugraph_ex 进阶功能

| 功能 | 功能说明 |
|---|---|
| [模型编译缓存功能](./advanced/compile_cache.md) | 在推理服务和弹性扩容等业务场景中，使用编译缓存可有效缩短服务启动后的首次推理时延。 |
| [多流表达功能](./advanced/multi_stream.md) | 大模型推理场景下，对于一些可并行的场景，可划分多个 stream 提升执行效率。 |
| [AI-Core 和 Vector-Core 限核功能](./advanced/limit_cores.md) | 提供 Stream 级核数配置，可调整最大 AI Core 数和 Vector Core 数，避免算子执行并行度降低。 |
| [算子级确定性计算配置功能](./advanced/deterministic.md) | 为指定范围内的算子配置确定性、强一致性或 Batch 一致性级别。 |
| [自定义 FX 图优化 Pass 功能](./advanced/post_grad_custom_pass.md) | 传入自定义 FX Pass 函数，该配置可控制自定义 Pass 在框架内置 Pass 执行前/后生效。 |
| [SuperKernel 功能](./advanced/superkernel.md) | 将连续的可融合 Task 合并为一个 SuperKernel Task，减少任务调度开销，提升执行性能。 |

**逐行解读**：进阶功能面向生产级推理服务的进一步调优——`compile_cache` 缩短冷启动时延；`multi_stream` 解决大模型可并行子图的并发执行；`limit_cores` 控制算子占用核数避免并行度下降；`deterministic` 提供算子级一致性保障；`post_grad_custom_pass` 允许在 `npugraph_ex` 内置 Pass 之前/之后注入用户自定义 FX Pass（与"功能拓展"章节呼应）；`superkernel` 做任务级合并以减少调度开销。

---

### 表 4　npugraph_ex DFX 功能

| 功能 | 功能说明 |
|---|---|
| [图编译 Debug 信息保存功能](./dfx/debug_save.md) | 通过复用原生 DEBUG 环境变量 TORCH_COMPILE_DEBUG 开启日志打印和文件 Dump。 |
| [算子 Data-Dump 功能](./dfx/data_dump.md) | 是否开启数据 dump 功能。 |
| [多流并发死锁检测功能](./dfx/deadlock_check.md) | 是否开启多流并发死锁检测功能。 |

**逐行解读**：DFX（Design For X）即辅助调试/可观测性能力——`debug_save` 复用 `TORCH_COMPILE_DEBUG` 环境变量；`data_dump` 在算子级做张量数据落盘以便回溯；`deadlock_check` 与"多流表达功能"配合，专门检测多 stream 并发场景的死锁。

## 【公式解读】

原文无公式。

## 【关联】

本文档位于 `npugraph_ex` 文档树的入口位置，向上承接 `torch.compile` 原生接口（PyTorch 上游），向下分发到三类子文档：

- **基础功能（`./basic/`）**：本文给出的"功能列表"中基础功能指向的 12 个子文档。文末的"问题定界"章节特别引用了 `force_eager.md`（步骤 2）与 `force_recapture.md`（步骤 3）作为定界工具；而 ACL graph 的总机制则被链接到外部《CANN应用开发》的"ACL Graph > 任务更新"章节。
- **进阶功能（`./advanced/`）**：本文指向 6 个子文档，包含与本文"功能拓展"章节直接呼应的 `post_grad_custom_pass.md`（自定义 FX Pass 注入时机）以及大模型推理常用能力 `multi_stream.md` / `superkernel.md` / `compile_cache.md` / `limit_cores.md` / `deterministic.md`。
- **DFX 功能（`./dfx/`）**：本文指向 3 个子文档（`debug_save.md` / `data_dump.md` / `deadlock_check.md`），其中 `deadlock_check.md` 与进阶的 `multi_stream.md` 互补。
- **API（`./api/`）**：本文"功能拓展"章节给出 `torch.npu.npugraph_ex.compile_fx` 的接口示例，指向 `./api/npugraph_ex/compile_fx.md`。
- **上游约束**：使用约束章节明确 `npugraph_ex` 与 `torch.cuda.CUDAGraph` 保持一致（stream sync / 动态控制流限制），这是其上游 PyTorch CUDAGraph 的语义透传。

> 说明：用户提供的内部链接清单（`./basic/*.md` 共 10 条）覆盖了表 2 中的前 10 项基础功能，但**未包含**表 2 中的 `remove_cat_ops.md`、`capture_error_mode.md` 两个基础功能链接，也**未覆盖**进阶功能与 DFX 功能以及 `./api/npugraph_ex/compile_fx.md`，这些均出现在原文中。

## 【使用方法】

### 1. 基础启用（原文）

```python
import torch
import torch_npu

# 自定义 Model
class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
    def forward(self, x, y):
        return torch.add(x, y)

model = Model().npu()
# 基于 npugraph_ex backend 进行 compile
opt_model = torch.compile(model, backend="npugraph_ex", fullgraph=True, dynamic=False)

# 执行编译后的 Model
x = torch.randn(2, 2).npu()
y = torch.randn(2, 2).npu()
opt_model(x, y)
```

### 2. torch.compile 接口原型（原文）

```python
torch.compile(model=None, *, fullgraph=False, dynamic=None,
              backend='inductor', mode=None, options=None, disable=False)
```

其中 `backend` 必须显式传 `"npugraph_ex"`；`fullgraph` 建议 `True`；`mode` NPU 暂不支持。

### 3. 基础功能配置（原文：通过 `options` 字典）

```python
torch.compile(model, backend="npugraph_ex", fullgraph=True,
              options={"force_eager": True})        # 示意：打开某项基础功能
```

具体键名与每项功能的语义参见表 2（共 12 项基础功能）。

### 4. 三步问题定界命令（原文）

```python
# 步骤 1：定界用户脚本问题（必须先通过这一步）
torch.compile(model, backend="aot_eager", fullgraph=True)

# 步骤 2：定界 aclgraph 自身问题
torch.compile(model, backend="npugraph_ex", fullgraph=True,
              options={"force_eager": True})

# 步骤 3：定界是图捕获阶段还是输入/输出内存处理阶段
torch.compile(model, backend="npugraph_ex", fullgraph=True,
              options={"force_recapture": True})
```

### 5. 自定义扩展（原文：功能拓展章节）

```python
import torch
from torch._functorch.aot_autograd import aot_module_simplified
import torch_npu

class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
    def forward(self, x, y):
        x = x + y
        return x

# 构建自定义的 compiler
def custom_compiler(gm: torch.fx.GraphModule, example_inputs):
    test_options = {"clone_input": False}
    compiled_graph = torch.npu.npugraph_ex.compile_fx(gm, example_inputs, test_options)
    return compiled_graph

# 构建自定义的 backend
def custom_backend(gm: torch.fx.GraphModule, example_inputs):
    return aot_module_simplified(gm, example_inputs, fw_compiler=custom_compiler)

x = torch.ones([2, 2], dtype=torch.int32).npu()
y = torch.ones([2, 2], dtype=torch.int32).npu()
model = torch.compile(Model().npu(), backend=custom_backend,
                      fullgraph=True, dynamic=False)
ret = model(x, y)
```

### 6. 集合通信入图（原文）

调用 `torch.compile` 时**默认已支持**集合通信算子入图，无需额外 options；如需了解实现细节参见 `./basic/communication_graph.md`。
