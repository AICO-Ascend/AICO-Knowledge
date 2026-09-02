# Cube-Vector Optimization Overview

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/CV/CVOptimization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/CV/CVOptimization.md

# AscendNPU-IR Cube-Vector 优化文档深度解读

---

## 【定位】

这篇文档面向 AscendNPU IR（基于 MLIR 的昇腾亲和编译器中间层），系统描述了 **Cube–Vector (CV) 优化流水线** 在 HIVM（Huawei Intermediate Virtual Machine）Dialect 中的整体能力：如何通过一系列 IR 变换把 Cube（矩阵）和 Vector（向量）两类子核高效协同，使 Atlas A2/A3 等 NPU 上的 Mix kernel 性能可被显式调控。

---

## 【技术要点】

1. **CV 优化运行在 pre-bufferization 阶段**
   - 大多数 CV pass 属于 `hivmPreBufferizationOptimizationPipeline`，此时 IR 仍是 `tensor` 中心化（带 `scf.for` 等控制流）；只有 bufferization 之后才会落地 `memref.alloc` 等 post-bufferization 优化（如另一次 PlanMemory）。
   - 关键术语在原文中严格区分：tensor 是逻辑多维数组无地址，memref 有 base/stride/shape。

2. **HIVM 是承载 NPU 算子的方言**
   - 包含 `mmadL1`、`batchMmadL1`、`fixpipe`、`vadd`、`vcast`、`vrelu` 等与硬件直接对应的算子，并承载控制流。

3. **数据流通过 fixpipe 跨越 Cube–Vector**
   - 910 系列上 Cube 完成计算后，fixpipe 把结果从 L0C 搬到 GM；IR 上对应 `hivm.hir.fixpipe`，硬件对应 L0C→UB 通路，可执行 `pre_quant`/`pre_relu` 等量化与激活。

4. **核心 CV 优化 Pass 链（六步）**
   - `createNormalizeMatmulPass`：归一化 mmadL1/batchMmadL1 的 M/K/N、init 条件、per-channel add 形态。
   - `createInlineFixpipePass`：在 mmadL1→store 链上插入 `fixpipe`，并尝试把 `vcast`/`vrelu`/`store` 折叠为 fixpipe 的 quant/activation 选项（如 `pre_quant=F322F16`）。
   - `createTileBatchMMIntoLoopPass`：把 `batchMmadL1` 沿 batch 维度展开为 `scf.for` 循环，使 load/fixpipe/store 可以按 batch 索引到 workspace 并支持流水线。
   - `createInsertLoadStoreForMixCVPass`：在 Cube–Vector 边界插入 load/store，使 tensor 与 workspace 数据流正确（典型 CV 模式）。
   - `createInsertWorkSpaceForMixCVPass`：在 CC/CV/VC/VV 边界把 `tensor.empty` 替换为 `memref_ext.alloc_workspace`，为跨迭代/跨核共享分配全局 workspace。
   - `createBindWorkSpaceArgPass`：把函数内 `alloc_workspace` 绑定到函数参数 `hacc.arg_type<workspace>`，让运行时把 workspace 指针作为实参传入，实现多 kernel 共享同一 workspace。

5. **CC/CV/VC/VV 四种结构模式**
   - 双字母中前字母是「前序计算单元」，后字母是「后续计算单元」（C=Cube，V=Vector）。
   - 用于描述 `InsertWorkSpaceForMixCV` 的插入点：例如 CV = Cube→fixpipe/load→Vector；CC = 两段 Cube 之间靠 fixpipe+load 相连。

6. **Mix kernel 调用规约**
   - Mix kernel 跑在 device 端，但「只能由 host 调用」：mix 入口必须由 host 启动的 kernel call 触发；当前规约下 device 上其它 kernel 不能直接调用 mix 函数（原文标注 current convention）。

---

## 【关键机制与数据】

### 硬件数据通路

- **Cube（矩阵单元）**：执行 `mmadL1`、`batchMmadL1` 等；**典型规格 24 个 AI Core**（原文：Atlas A2/A3 描述，规格数字以原文为准）。
- **Vector（向量单元）**：执行 `vadd`、`vcast`、`vreduce` 等；**典型规格 48 个 AI Core**。
- **L0C**：Cube 输出缓冲，**128 KB**。
- **L0A/L0B**：Cube 输入缓冲，**64 KB**。
- **UB**：向量算子统一缓冲，**256 KB**。
- **GM**：全局内存，外部 DDR。
- **fixpipe**：Cube→Vector 的数据通路；910 系列上 Cube 完成后由 fixpipe 把 L0C 结果搬到 GM，供后续 Vector 使用；硬件上对应 L0C→UB 通路，可做类型转换、量化等（受 `pre_quant`、`pre_relu` 等属性控制）。

### 关键机制

- **Workspace 复用机制**：多个缓冲可在同一 workspace 内分配不同 **offset**，由 PlanMemory 根据 **Liveness**（从 defined/first use 到 last use 的生命周期）决定哪些缓冲可共享基址。
- **Inplace 机制**：当 op 输出可覆盖输入存储时（例如 `vcast f16→i16` 同宽度转换），PlanMemory 识别 inplace 并复用同一段存储以减少 alloc。
- **AIC/AIV 拆分**：Mix kernel 拆分后，AIC（Cube 主导）跑在 Cube、AIV（Vector 主导）跑在 Vector，二者通过 fixpipe、DMA 交换数据，host/scheduler 协调调用顺序。
- **pre- vs post-bufferization 的流水线顺序原则**：CV 结构先建（tensor 阶段），再 materialization（memref/bufferization 阶段），便于理解 pass 排序。

### 典型 IR 变换（原文 Before / After）

- **createInlineFixpipePass** 把 `mmadL1 -> store` 改写为 `mmadL1 -> fixpipe`，并尝试把 `hivm.vcast`、`hivm.vrelu`、`hivm.store` inline 进新插入的 fixpipe。
- **createTileBatchMMIntoLoopPass** 把 `batchmmadL1 a:[batch,m,k], b:[batch,k,n]` + `fixpipe workspace:[batch,m,n]` 展开为 `for batch_idx in range(batch): mmadL1(extract_slice(a), extract_slice(b)); fixpipe(extract_slice(workspace))`。
- **createInsertWorkSpaceForMixCVPass** 把 `mmadL1; tensor.empty(); fixpipe; load; vadd` 中的 `tensor.empty()` 替换为 `memref_ext.alloc_workspace()` 并通过 `bufferization.to_tensor` 回填为 tensor 输出。
- **createBindWorkSpaceArgPass** 把函数内的 `memref_ext.alloc_workspace() : memref<100xi32>` 绑定到函数参数 `%arg1: memref<?xi8> {hacc.arg_type = #hacc.arg_type<workspace>}`，形成单一 workspace 源。

> 注：原文 `createBindWorkSpaceArgPass` 的 After 代码块在提供文本中被截断（停在 `func.func @bind_workspace_arg(\n              %arg0: i64 {hacc.arg_type = #hacc`），下文不臆造其完整形态。

---

## 【表格解读】

### 表 1：术语与背景（原文逐字还原）

| Term | Description | Remarks |
|------|------|----------|
| **HIVM** | Huawei Intermediate Virtual Machine | A dialect in AscendNPU IR that carries NPU-oriented ops (e.g. mmadL1, fixpipe, vadd) and control flow. |
| **IR** | Intermediate Representation | The compiler's abstraction between source and machine code. This project uses Multi-Level IR (MLIR); IR is in SSA form. |
| **Bufferization** | Converting the tensor abstraction into concrete memory (memref) | In the "pre-bufferization" phase, IR is still **tensor**-centric (logical multi-dim arrays). After bufferization, **memref** (memory with address/layout) is introduced. Most CV passes run in pre-bufferization, so you will see `tensor.empty`, `tensor slice`, etc. |
| **tensor vs memref** | tensor: logical multi-dim array, without explicit address; memref: memory region with base, stride, and shape | In the CV process, "output" is often first represented as a tensor, then materialized via workspace (memref) or bufferization. |
| **Workspace** | A contiguous region of memory in GM, passed as a kernel argument at runtime | Used for intermediate data between Cube and Vector (e.g. fixpipe output). Multiple buffers can be allocated at different **offsets** in the same workspace; PlanMemory computes offsets for reuse. |
| **Liveness** | The lifetime of a buffer from "defined/first use" to "last use" | PlanMemory uses liveness to decide whether two buffers can overlap; if not, they can share the same base address with different offsets. |
| **Inplace** | The op's output is written over the input's storage, reusing the same buffer | For example, vcast f16→i16 (same width); output can overwrite input, reducing alloc. PlanMemory identifies inplace ops and assigns offsets accordingly. |
| **AIC / AIV** | AIC: sub-kernel dominated by Cube; AIV: sub-kernel dominated by Vector | After splitting a Mix kernel, AIC runs mainly on Cube and AIV on Vector; they exchange data via fixpipe, DMA, etc., and the host/scheduler coordinates the call order. |
| **Host / Device** | Host: runs on CPU; Device: runs on NPU | Mix kernels are on the device side. "Mix can only be called from host" means the mix entry is called from a host-launched kernel call; another device kernel cannot directly call a mix function (current convention). |
| **CC / CV / VC / VV** | Two letters: "previous compute unit" and "next compute unit" (C=Cube, V=Vector) | For example, CV = Cube then fixpipe/load then Vector; CC = two Cube segments connected by fixpipe+load. It is used to describe InsertWorkSpaceForMixCV patterns. |

**逐行解读**：
- **HIVM**：定位为承载 NPU 算子与控制流的 dialect，是整个 CV 优化运行的容器方言。
- **IR**：强调本项目使用 MLIR 的多级 IR，并以 SSA 形式表示，区别于线性 IR。
- **Bufferization**：把 tensor 抽象转为带地址/布局的 memref；CV pass 大多发生在 bufferization 之前，因此读者会频繁见到 `tensor.empty`、`tensor.slice`。
- **tensor vs memref**：明确两种抽象的差别——tensor 不带显式地址，memref 有 base/stride/shape；并提示 CV 流程中"输出"常常先以 tensor 表示、再经 workspace(memref) 或 bufferization 落地。
- **Workspace**：GM 上连续内存区域，作为 kernel 实参传入；通过不同 offset 实现多个缓冲复用，并由 PlanMemory 决策。
- **Liveness**：从首次定义/使用到最后一次使用的生命周期，是 PlanMemory 决定"两个 buffer 能否共享基址"的关键依据。
- **Inplace**：算子输出直接覆盖输入存储（同宽度 `vcast f16→i16` 是典型例子），PlanMemory 借此减少 alloc。
- **AIC / AIV**：拆分子核后的命名约定——AIC 偏 Cube、AIV 偏 Vector，二者通过 fixpipe/DMA 交换数据，由 host/scheduler 协调。
- **Host / Device**：明确 Mix kernel 在 device 端，但调用入口须由 host 启动；当前不允许 device 上其它 kernel 直接调 mix（current convention 提示这是当下规约，未来可能变化）。
- **CC / CV / VC / VV**：描述 Cube/Vector 邻接段的双字母编码，是 `InsertWorkSpaceForMixCVPass` 模式识别的基本词汇。

### 表 2：昇腾 NPU 异构芯片架构（原文逐字还原，保留原文笔误）

| Component | Description | Typical Specifications (Example) |
|------|------|-------------------|
| **Cube** | Matrix unit; runs `mmadL1`. `batchMmadL1`,, etc. | (24 AI Cores |
| **Vector** | Vector unit; runs `vadd`, `vcast`, `vreduce`, etc. | 48 AI Cores |
| **L0C** | Cube output buffer for matmul results | 128 KB |
| **L0A/L0B** | Cube input buffer | 64 KB |
| **UB** | Unified buffer for vector ops | 256 KB |
| **GM** | Global Memory | External DDR |

**逐行解读**：
- **Cube**：矩阵单元，跑 `mmadL1`、`batchMmadL1` 等；典型规格 24 AI Core（原文括号未闭合，可能是排版瑕疵，按原文如实保留）。
- **Vector**：向量单元，跑 `vadd`、`vcast`、`vreduce` 等；典型规格 48 AI Core，数量约为 Cube 的 2 倍。
- **L0C**：Cube 的输出缓冲，专门承接 `mmad` 结果，容量 128 KB；fixpipe 从 L0C 出发把数据搬到 GM/UB。
- **L0A/L0B**：Cube 输入缓冲，各 64 KB，承载矩阵乘的左右操作数。
- **UB**：向量算子统一缓冲 256 KB，Vector 计算与 fixpipe 落地（按 910 系列的 L0C→UB 路径）的临时空间。
- **GM**：外部 DDR，作为 kernel 间数据（包括 workspace）的中转与落地区。

---

## 【公式解读】

**原文无公式**。文档仅包含 MLIR IR 伪代码示例（Before/After 片段），未出现任何 LaTeX/伪代码形式的数学公式。

---

## 【关联】

> 原始任务提示中给出的「内部链接」为 (无)。因此本节依据文档自身提及的概念与模块，做合理的结构性关联梳理：

- **上游：HIVM Dialect 层**
  - 本文档描述的所有 pass 都运行在 HIVM 方言之上，HIVM 提供 `mmadL1`、`batchMmadL1`、`fixpipe`、`vadd`、`vcast`、`vrelu`、`vbrc`、`store`、`load` 等 NPU 算子，以及控制流承载能力。

- **横向：Pass 流水线**
  - 6 个 CV pass 构成一条线性优化链：`NormalizeMatmul → InlineFixpipe → TileBatchMMIntoLoop → InsertLoadStoreForMixCV → InsertWorkSpaceForMixCV → BindWorkSpaceArg`。读者可将其视为 CV 结构从「IR 归一化」→「显式化 fixpipe 边界」→「批维循环展开→load/store 边界→workspace 分配→参数绑定」的逐步构造过程。

- **下游：Bufferization 与 PlanMemory**
  - 在 pre-bufferization 阶段（`hivmPreBufferizationOptimizationPipeline`）完成后，由 bufferization 把 tensor 转为 memref；post-bufferization 阶段会再次调用 PlanMemory 在 `memref.alloc` 上做内存规划（offset/liveness/inplace 决策）。这与本文档中描述的 Workspace/Liveness/Inplace 概念直接对应。

- **运行时：Host/Scheduler 与 Workspace 实参传递**
  - `BindWorkSpaceArgPass` 输出的 `hacc.arg_type<workspace>` 函数参数，是 host/scheduler 在启动 kernel 时传入 workspace 指针的依据；Mix kernel 由 host 启动（device 上其它 kernel 当前不能直接调 mix）。

- **CC/CV/VC/VV 与 `InsertWorkSpaceForMixCV` 模式识别**
  - 双字母命名是 `InsertWorkSpaceForMixCV` 内部识别模式的核心词汇，对应 `tensor.empty → memref_ext.alloc_workspace` 的替换点。

- **跨文档引用（文档级别）**
  - 文末提供的「内部链接」字段为 (无)；但文档本体在 `Terms and Background` 段落使用了「Read First」措辞，暗示该章节是后续单 pass 详细文档的前置阅读材料，与系列其他 CV pass 详解文档存在前置依赖关系。

---

## 【使用方法】

**原文未涉及**具体的启用命令、开关参数或编译选项（如 `-mllvm-pass`、`--enable-cv-*` 等）。

原文仅以「算法原理」形式描述每个 pass 的 Role / Goal / Typical transforms / Typical scenario，并给出 MLIR Before/After 片段作为概念示例；没有给出：
- 任何 CLI 命令或编译参数；
- 任何 CMake/Python 配置开关；
- 任何 `PassPipeline` 拼接示例；
- 任何运行验证脚本或端到端测试命令。

如需在 AscendNPU IR 中实际启用本文档所述的 CV 优化链，需要结合同仓其它文档（如 `hivmPreBufferizationOptimizationPipeline` 的 Pass 注册说明、`PlanMemory` 的 post-bufferization 说明等）自行拼装，本篇文档不提供具体的启用方式。

## 图文联合解读

- `cvarch.png`: ## 图文联合解读

**1) 图中内容**
外框为 **AICore**，内部并列两个子单元：左侧黄色 **AIC** 含 Cube（矩阵运算）、FixPipe、L0/L1 三级缓冲；右侧蓝色 **AIV** 含 Vector 单元与 UB（统一缓冲）；底部为外部 **HBM**。箭头显示：Cube 与 L0/L1 双向读写；FixPipe 在 L0/L1 与 HBM 之间搬运结果；Vector 与 UB 双向交互。AIC 与 AIV 之间**无直连箭头**。

**2) 技术结论**
Cube 负责矩阵计算并通过 FixPipe 落盘 HBM；Vector 在片内 UB 上做向量化操作；二者必须经 HBM/L 缓冲间接协作，**片上数据通路不直通**。

**3) 与文档论点呼应**
对应"Hardware Background"所述 HIVM 上 `mmadL1`、`fixpipe`、`vadd` 等算子，以及 Mix kernel 执行需 Cube/Vector 高效协同——CV 优化的本质正是通过 IR 变换编排跨单元的数据搬运与时序对齐，弥补硬件无直连的代价。
