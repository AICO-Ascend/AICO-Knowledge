# Cube与Vector优化

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/cv_optimization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/cv_optimization.md

# AscendNPU-IR「Cube与Vector优化」feature文档深度解读

---

## 【定位】

这篇文档系统描述了AscendNPU IR在HIVM（华为中间表示虚拟机）层针对Atlas A2/A3系列NPU硬件的Cube-Vector协同优化能力，介绍了从Matmul规范化、fixpipe内联、batch维度tiling、workspace分配与内存规划到AIC/AIV子内核拆分的一整套pass流水线，以提升混合内核（Mix Kernel）的执行效率。

---

## 【技术要点】

1. **面向硬件**：Atlas A2系列与Atlas A3系列产品NPU；处理对象为Cube（矩阵乘单元，如`mmadL1`、`batchMmadL1`）与Vector（向量运算单元，如`vadd`、`vcast`、`vreduce`）两类核心的协同。
2. **执行阶段**：CV相关pass多数在预bufferization阶段（`hivmPreBufferizationOptimizationPipeline`）运行，此时IR以tensor为主、含`scf.for`等控制流。
3. **核心变换序列**：Matmul规范化 → fixpipe内联 → batch维度tiling → CV交汇处插入load/store → 用workspace替换tensor.empty → 绑定workspace函数参数 → 内存规划（`GLOBAL_WORKSPACE_PLAN`）→ Mix内核拆分为AIC/AIV子函数。
4. **关键算子**：`hivm.hir.mmadL1`、`hivm.hir.batchMmadL1`、`hivm.hir.fixpipe`（含`pre_quant`、`pre_relu`属性）、`memref_ext.alloc_workspace`、`hivm.hir.pointer_cast`。
5. **匹配模式**：InsertWorkSpaceForMixCV识别CC（Cube→fixpipe→load→Cube）、CV（Cube→fixpipe→load→Vector）、VC（Vector→store→load→Cube）、VV（Vector→store→load→Vector）四类模式。
6. **调用约定**：Mix只能被Host调用（当前约定下device上的另一个kernel不能直接call一个mix函数）。

---

## 【关键机制与数据】

### 工作原理与数据流

- **Cube→Vector数据搬运通道**：fixpipe是Cube与Vector之间的数据搬运通道，对应硬件的L0C→UB数据通路。对于910系列，Cube计算完成后通过fixpipe将结果从L0C搬运到GM，供后续Vector运算使用；fixpipe可同时完成类型转换、量化等（由`pre_quant`、`pre_relu`等属性控制）。
- **Workspace复用机制**：多个中间buffer可在同一块workspace上按偏移分配；PlanMemory根据liveness判断两个buffer是否可能同时存活，若不重叠，可分配相同基址、不同偏移，从而复用一块大buffer、减少总占用；Inplace（操作的输出直接写在输入的存储位置上）由PlanMemory识别并做偏移分配。
- **Mix内核拆分**：后端按AIC/AIV分别调度到Cube/Vector核心，便于流水与同步；用`annotation.mark`标记跨核传递的tensor。

### 性能/硬件数据（原文已明确给出的）

- 原文：Cube典型规格为24个AI Core；Vector为48个AI Core。
- 原文：L0C为128KB，L0A/L0B各64KB，UB为256 KB，GM为外部DDR。

> 注：原文未给出具体的性能加速比或吞吐数据，仅有芯片架构规格。

---

## 【表格解读】

### 表格1：术语与背景知识

| 术语 | 含义 | 补充说明 |
|------|------|----------|
| **HIVM** | Huawei Intermediate Virtual Machine，华为中间表示虚拟机 | AscendNPU IR中的一种dialect，承载面向NPU的算子（如mmadL1、fixpipe、vadd）与控制流。 |
| **IR** | Intermediate Representation，中间表示 | 编译器在源码与机器码之间的抽象表示。本仓库使用MLIR（Multi-Level IR），IR以SSA形式组织。 |
| **Bufferization** | 将tensor抽象转换为具体内存（memref）的过程 | 在「预bufferization」阶段，IR仍以tensor为主（逻辑多维数组）；bufferization之后会引入memref（带地址/布局的内存引用）。CV中多数pass在预bufferization阶段运行。 |
| **tensor vs memref** | tensor：逻辑多维数组，无显式地址；memref：有基址、步长、形状的内存区域 | fixpipe的「输出」常先以tensor表示，后续通过workspace（memref）或bufferization落到具体内存。 |
| **Workspace** | 运行时在GM上分配的一块连续内存，作为kernel参数传入 | 用于存放Cube-Vector之间的中间结果（如fixpipe输出）。多个中间buffer可在同一块workspace上按偏移分配，由PlanMemory计算偏移。 |
| **Liveness** | 某个buffer从「被定义/首次使用」到「最后一次使用」的生命周期 | PlanMemory根据liveness判断两个buffer是否可能同时存活；若不重叠，可分配相同基址、不同偏移。 |
| **Inplace** | 操作的输出直接写在输入的存储位置上，复用同一块buffer | 例如vcast从f16转到i16（等宽），输出可覆盖输入，减少alloc。 |
| **AIC / AIV** | AIC：以Cube为主的子内核；AIV：以Vector为主的子内核 | Mix内核拆分后，AIC主要在Cube核心执行，AIV主要在Vector核心执行；二者通过fixpipe、DMA等传递数据，由Host或调度器协调调用顺序。 |
| **Host / Device** | Host：在CPU上运行<br>Device：在NPU上运行 | Mix内核属于device侧；当前约定下device上的另一个kernel不能直接call一个mix函数。 |
| **CC / CV / VC / VV** | 两个字母分别表示「前一段计算单元」和「后一段计算单元」：C=Cube，V=Vector | 例如CV表示Cube算完经fixpipe/load后接Vector运算；CC表示两段Cube之间通过fixpipe+load衔接。用于描述InsertWorkSpaceForMixCV的匹配模式。 |

**逐行解读**：
- 第1-2行定义HIVM和IR两个最基础的dialect与中间表示概念，确立文档语境（MLIR/SSA）。
- 第3-4行强调tensor到memref的转换时机——预bufferization阶段以tensor为主，这与后续所有pass运行阶段直接相关。
- 第5-7行（Workspace / Liveness / Inplace）共同构成PlanMemoryPass的内存规划基础：liveness决定是否冲突，inplace决定能否覆盖输入。
- 第8行解释AIC/AIV拆分后的硬件归属，呼应后续SplitMixKernelPass。
- 第9行强调调用约定边界（Host发起Mix调用）。
- 第10行的四类匹配模式直接对应InsertWorkSpaceForMixCVPass的具体插入规则。

### 表格2：芯片架构组件

| 组件 | 说明 | 典型规格（举例） |
|------|------|-------------------|
| **Cube** | 矩阵乘单元，执行`mmadL1`、`batchMmadL1`等矩阵运算 | 24个AI Core |
| **Vector** | 向量运算单元，执行`vadd`、`vcast`、`vreduce`等向量运算 | 48个AI Core |
| **L0C** | Cube输出缓冲，存放矩阵乘结果 | 128KB |
| **L0A/L0B** | Cube输入缓冲 | 64KB |
| **UB** | 统一缓冲，Vector运算主存 | 256 KB |
| **GM** | 全局内存 | 外部DDR |

**逐行解读**：
- Cube与Vector分别是矩阵乘与向量运算两类核心，文档后续所有pass的核心目的就是让这两类核心协同高效。
- L0C是fixpipe的来源端（Cube→Vector），L0A/L0B是Cube输入缓冲；UB是Vector的运算主存。
- GM（外部DDR）是workspace所在层——意味着多个中间buffer复用同一块workspace能显著减少DDR占用。
- Vector核心数（48）多于Cube（24），与AIV拆分后的并行调度能力相关。

---

## 【公式解读】

原文无公式（仅有MLIR代码片段示例，如`mmadL1`、`fixpipe`等的变换前/后对照，这些是MLIR伪代码形式而非数学公式）。各pass章节通过变换前/后的MLIR代码块展示IR形态变化，已在【关键机制与数据】与各pass描述中体现。

---

## 【关联】

> 内部链接：(无)

根据文档内容，可以推断出以下关联关系（基于原文显式提及，未做臆造）：

- **与HIVM dialect的关系**：CV优化完全建立在HIVM之上，所有变换围绕`hivm.hir.mmadL1`、`hivm.hir.batchMmadL1`、`hivm.hir.fixpipe`、`hivm.hir.vadd`、`hivm.hir.vcast`、`hivm.hir.vrelu`、`hivm.hir.store`、`hivm.func_core_type<MIX/AIC/AIV>`等HIVM算子/属性展开。
- **与MLIR基础设施的关系**：依赖MLIR的SSA形式、`scf.for`控制流、`tensor.empty`、`func.func`、`bufferization.to_tensor`等通用MLIR概念；本仓库使用MLIR（Multi-Level IR）。
- **与`memref_ext`扩展的关系**：`memref_ext.alloc_workspace`与`memref.alloc`是PlanMemoryPass的两个输入目标（前者在预bufferization阶段，后者在后bufferization阶段）。
- **与`hacc`扩展的关系**：函数参数上的`hacc.arg_type = #hacc.arg_type<workspace>`、`#hacc.arg_type<ffts_base_address>`用于BindWorkSpaceArgPass绑定workspace参数。
- **上下游pass顺序**：文档显式说明「先做CV结构变换，再做内存具体化」——CV相关pass多数在预bufferization阶段（`hivmPreBufferizationOptimizationPipeline`）执行；bufferization之后还有后bufferization阶段的优化（如另一轮PlanMemory针对`memref.alloc`）。
- **与Atlas A2/A3系列硬件的关系**：面向Atlas A2系列、Atlas A3系列产品的NPU硬件，以910系列为例给出V220架构示意（`figures/cvarch.png`）。
- **TCB mark/hoist**：文档末尾命令注释提到「TCB mark/hoist 仅 Ascend950」，表明存在芯片版本差异的pass分支（原文未给出具体特性链接）。
- **其他文档**：原文未显式提供其他文档链接，但根据上下文，本文档属于AscendNPU IR developer_guide/features系列下的「CV优化」专题，与HIVM dialect本身的算子参考、各pass的独立专题文档构成互补关系（原文未给出这些链接）。

---

## 【使用方法】

### 单个Pass调试命令（原文给出）

```bash
# Matmul规范化
bishengir-opt -hivm-normalize-matmul input.mlir -o output.mlir

# fixpipe内联
bishengir-opt -hivm-inline-fixpipe input.mlir -o output.mlir

# batch维度tiling为循环
bishengir-opt --hivm-tile-batchmm-into-loop input.mlir -o output.mlir

# Mix CV交汇处插入workspace
bishengir-opt -insert-workspace-for-mix-cv input.mlir -o output.mlir

# 绑定workspace函数参数
bishengir-opt --hivm-bind-workspace-arg input.mlir -o output.mlir

# 全局workspace内存规划（带mem-plan-mode选项）
bishengir-opt -hivm-plan-memory -mem-plan-mode=global-work-space-plan input.mlir -o output.mlir

# Mix拆分（需先独立split-mixed-if；TCB mark/hoist仅Ascend950）
bishengir-opt -hivm-split-mixed-if-conditionals -hivm-mark-tightly-coupled-buffer \
  -hivm-hoist-tightly-coupled-alloc -hivm-split-mix-kernel input.mlir -o output.mlir
```

### 关键配置项（原文给出）

- `-mem-plan-mode=global-work-space-plan`：PlanMemoryPass在`GLOBAL_WORKSPACE_PLAN`模式下进行内存规划（将`memref_ext.alloc_workspace`替换为`hivm.hir.pointer_cast` + 偏移）。
- `hivm.func_core_type = #hivm.func_core_type<MIX/AIC/AIV>`：函数级属性，标识函数归属的核类型（由SplitMixKernelPass拆分后赋予）。

### 测试用例查找方式（原文给出）

原文：目前库上所有的测试用例所在的路径都在`path-to-ascendnpuir/bishengir/test`下，需要运行某个pass，搜索对应的编译命令即可找到对应的测试文件，例如搜索`hivm-normalize-matmul`（原文此处被截断，但提示了按pass名搜索的方式）。

### 典型变换的MLIR伪代码（原文给出）

文档为每个pass都提供了「变换前/变换后」的MLIR代码块示例（NormalizeMatmul、InlineFixpipe、TileBatchMMIntoLoop、InsertLoadStoreForMixCV、InsertWorkSpaceForMixCV、BindWorkSpaceArg、PlanMemory、SplitMixKernel八个pass），可作为启用各pass后预期IR形态的对照参考。

## 图文联合解读

- `cvarch.png`: **图示内容**：AICore内分AIC（黄色，左）和AIV（蓝色，右）两子核。AIC含Cube、L0/L1缓冲及FixPipe；AIV含Vector与UB。Cube↔L0/FixPipe双向箭头、FixPipe↔HBM、AIV↔HBM均标注数据通路。

**技术结论**：Cube与Vector物理分离，必须通过HBM中转（FixPipe落盘→AIV读回）才能协同，片上带宽与延迟是性能关键。

**与文档关系**：为"CV优化为何需PlanMemory、workspace复用、inplace"提供硬件依据——子核分离导致中间buffer经GM往返，是Mix Kernel效率瓶颈的根源。
