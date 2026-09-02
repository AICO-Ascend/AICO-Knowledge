# 概述

> 仓 `torchair` · 路径 `docs/zh/custom_op_graph/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/custom_op_graph/overview.md

# 「torchair 自定义算子入图概述」深度解读

---

## 【定位】

本篇文档是 TorchAir 中「自定义 PyTorch 算子接入图模式」整章的总览，阐明自定义 PyTorch 算子如何与 TorchAir 图模式（`torch.compile`）配合工作，介绍完整入图流程涉及的交付件、各步骤的依赖关系，以及不同入图场景（从零开发 vs 仅做图模式适配）和算子类型（非 In-place vs In-place）所需完成的具体步骤，并交代环境准备与源码获取方式。

---

## 【技术要点】

1. **TorchAir 两种工作模式**：
   - `npugraph_ex` 后端（aclgraph）模式：提供**模型下沉调度、多 Stream 并行、图间内存复用**能力，所需交付件与 Torch 原生图模式完全一致。
   - GE 图模式（`mode=max-autotune`，又称 **Ascend IR 模式**）：在 aclgraph 能力基础上额外提供 **SuperKernel 等 JIT 编译能力**，进一步提升执行性能，需额外实现 **Ascend Converter** 交付件以完成 PyTorch 算子 → Ascend IR 的转换。

2. **完整入图最多包含 6 个步骤**（以 In-place 算子为例）：
   - 步骤 1：PyTorch Eager 模式调用交付件——确定目标算子原型并完成 Schema 定义。
   - 步骤 2：PyTorch Eager 模式调用交付件——基于 **Ascend C** 完成 NPU 实现。
   - 步骤 3：PyTorch Eager 模式调用交付件——基于 **OpPlugin** 完成 Ascend C 算子的 Eager 模式适配。
   - 步骤 4：PyTorch 原生入图——完成 **Meta 符号化推导**，使算子可被 `npugraph_ex`（aclgraph）和 `aot_eager` 等原生图后端使用，并获得 aclgraph 下沉调度收益。
   - 步骤 5：（可选）**仅 In-place 算子**才需要执行，完成函数化转换。
   - 步骤 6：（可选）希望使用 **SuperKernel**、**分核执行**等 `max-autotune` 模式提供的高阶能力时，需额外完成 Ascend IR 入图操作。

3. **关键术语要点**：
   - **In-place 算子**：计算时会修改输入的算子（如 `torch.ops.aten.add_`），又称原地算子 / Ref 类算子。
   - **非 In-place 算子**：`add_` 对应的 `torch.ops.aten.add`，结果写入输出而非直接修改输入。
   - **函数化（Functionalization）**：将 In-place 算子替换为非 In-place 算子的过程（如 `add_` → `add`），是 In-place 算子与 PyTorch 图模式配合工作的前提。
   - **Meta 函数（符号化推导）**：描述算子输出与输入 shape、dtype 以及内存关系，是 PyTorch 入图的**前提条件**，所有能与 `torch.compile` 配合工作的算子都必须实现。

4. **交付件差异**：
   - **非 In-place 算子**本身是函数化的，无需实现函数化转换。
   - **In-place 算子**需要实现函数化；TorchAir 已支持 PyTorch 社区的**自动化函数化**能力。

5. **两种入图场景**：
   - 场景 1（从零开发 Eager + 图模式）：需完成步骤 1–6，参考 `op_adapt_torchair.md`。
   - 场景 2（已具备 Eager 模式，仅补图模式适配）：需完成步骤 4–6，采用「插件化适配」方式，**无需编译、安装 TorchNPU**，**全 Python 实现**，可在任意 `.py` 文件中实现交付件并在模型执行前加载，便于调试或作为插件分发。

6. **环境与版本要求**：
   - PyTorch：建议 **2.6.0** 版本。
   - 需安装：PyTorch、TorchNPU、CANN 软件、固件/驱动，并严格注意**软件版本配套关系**。
   - 基于 TorchNPU 自定义算子接入流程开发时，需与 **TorchNPU 源码一起编译打包**便于共享。

---

## 【关键机制与数据】

### 工作机制（原文）

- **aclgraph 模式数据流**：用户模型 → `torch.compile` → npugraph_ex 后端 → 在 NPU 上以图方式执行；交付件与 Torch 原生图模式完全一致，因此复用 PyTorch 自身生态即可。
- **GE 图模式（Ascend IR）数据流**：在 aclgraph 之上，通过 **Ascend Converter** 把 PyTorch 算子转成 Ascend IR，再借助 SuperKernel 等 JIT 编译能力融合/优化，最终在 NPU 上执行。
- **Meta 推导机制**（原文："Meta函数表示了PyTorch算子输出与输入shape、dtype以及内存的关系，它是PyTorch入图的前提条件"）：这是 `torch.compile` 在 FX Graph 中预先分配内存、推导输出形状的依据；没有 Meta 函数的算子无法进入图模式。
- **函数化机制**（原文："PyTorch图模式基于函数化后的FX图工作"）：FX 图阶段只接受纯函数式算子，因此 In-place 算子必须先转成非 In-place 形式才能入图；TorchAir 支持 PyTorch 社区的自动化函数化。
- **插件化适配机制**（原文："无需编译、安装TorchNPU，并且采用全Python实现……在模型执行前加载即可"）：交付件以纯 Python 形式存在，可作为插件注入，降低开发与调试门槛。

### 性能收益（原文已表述的能力，文档未给出具体数字）

- aclgraph 模式提供：**模型下沉调度收益**、多 Stream 并行、图间内存复用。
- GE 图模式（max-autotune）在 aclgraph 基础上，**通过 SuperKernel 等 JIT 编译能力进一步提升执行性能**。

> 原文未提供具体的延迟、吞吐等量化性能数据。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

| 关联文档 | 关系 |
|---|---|
| `../ascend_ir/features/advanced/super_kernel_scope.md` | 步骤 6 中提到的 Ascend IR 高阶能力之一：SuperKernel，在 GE 图模式（max-autotune）下启用 |
| `../ascend_ir/features/advanced/limit_cores.md` | 步骤 6 中提到的 Ascend IR 高阶能力之一：分核执行（limit cores），同样属于 max-autotune 模式 |
| `../overview.md#常用概念` | 上游概念手册，文中 Eager 模式、算子 Schema、Ascend C、OpPlugin、In-place 算子等术语需先查阅此节 |
| `op_adapt_torchair.md` | 场景 1（从零开发 Eager + 图模式算子）对应的详细操作指南 |
| `op_plugin_adapt_torchair.md` | 场景 2（Eager 已就绪、仅做图模式适配）对应的详细操作指南——即「插件化适配」 |
| `non_in_place_op_cases.md` | 场景 1 + 非 In-place 算子的开发与入图样例 |
| `in_place_op_cases.md` | 场景 1 + In-place 算子的开发与入图样例 |
| `./op_plugin_adapt_torchair.md`（出现两次） | 场景 2 中非 In-place 与 In-place 算子的「插件化入图样例」入口（原文将两类算子的样例都链接到了同一路径） |

上下游逻辑：本 overview 是整章入口，向下细分为「从零开发」与「插件化适配」两条路径，分别对应章节 `op_adapt_torchair.md` 与 `op_plugin_adapt_torchair.md`；步骤 6 涉及的能力则向上回流到 Ascend IR 章节的 `super_kernel_scope.md` 与 `limit_cores.md`。

---

## 【使用方法】

### 软件安装清单（原文）

- **PyTorch**：建议 **2.6.0** 版本
- **TorchNPU**：注意与 CANN 等软件配套关系
- **CANN 软件**：注意与 TorchNPU 等软件配套关系
- **固件/驱动**：注意与 CANN、TorchNPU 等软件配套关系

> 原文指出：安装指导参考《TorchNPU 框架特性》中的「基于 OpPlugin 算子适配开发」章节，需保证可正常编译、安装及执行 TorchNPU。

### TorchNPU 源码下载命令（原文）

```bash
git clone https://gitcode.com/Ascend/pytorch.git -b v2.6.0 --recursive
cd pytorch
```

### 启用方式 / 加载方式（原文）

- 插件化适配场景下，交付件**采用全 Python 实现**，**可在任意 `.py` 文件中实现交付件，并在模型执行前加载**——便于算子调试或将自定义算子模块作为插件使用。

### 图模式后端启用（基于文档语义，原文未给出完整命令）

- `npugraph_ex`（aclgraph）后端：完成 Meta 推导（步骤 4）后即可使用，并可在 `aot_eager` 等原生图模式后端运行。
- `mode=max-autotune`（Ascend IR / GE 图）后端：需额外完成 Ascend Converter（步骤 6）以解锁 SuperKernel、分核执行等高阶能力。

> 原文未涉及具体的 `torch.compile(..., backend="npugraph_ex")` 或 `mode="max-autotune"` 等调用命令字面写法，也未涉及配置项 / 环境变量列表。

## 图文联合解读

- `op_in_graph_flowchart.png`: **图示解读**

图分三层纵向展示算子接入TorchAir的6步流程：Eager层（步骤1-3必选，依次为Schema定义、Ascend C实现、OpPlugin注册）；PyTorch原生图模式层（步骤4必选Meta推导、步骤5可选函数化转换）；Ascend IR层（步骤6可选Converter实现）。每步右侧"为什么需要"注解分别论证：Meta推导是torch.compile入图前提，函数化消除In-place隐患便于图优化，Converter则将算子转为Ascend IR以解锁max-autotune模式下的SuperKernel、在图内存刷新等极致性能。

**图文关系**：图与文档"两种工作模式（npugraph_ex/Ascend IR）+ 六步交付件"论点一一对应，可视化了"必选/可选"分层，并以侧边栏将交付件分别归入"获取调度收益"与"探索极致性能"两层增益，帮助读者按需选择实施范围。
