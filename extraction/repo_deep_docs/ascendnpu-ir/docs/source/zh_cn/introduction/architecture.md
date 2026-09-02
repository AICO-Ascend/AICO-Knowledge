# 架构设计

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/introduction/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/introduction/architecture.md

# AscendNPU IR 架构设计文档深度解读

## 【定位】

本文档系统阐述了毕昇编译器 AscendNPU IR 的整体架构设计，包括其基于 MLIR 生态构建的分层抽象目标、自研方言体系（HFusion/HIVM/HACC/Annotation/Scope）的职责分工、代码组织结构，以及从高层 Tile 级 Op 到 NPU 底层二进制文件的编译流程。

---

## 【技术要点】

1. **分层抽象目标**：AscendNPU IR 自下而上对昇腾硬件底层指令、核内资源、核间资源、SOC 资源逐层进行抽象编译优化，多层抽象间分层解耦、开源开放，允许生态编程、三方框架按需权衡性能与易用性灵活对接。

2. **五大自研方言分工**：
   - **HFusion**：硬件相对无关的优化
   - **HIVM**：精细化感知 NPU 硬件细节，将 High level 编程语言转换为 NPU 底层指令
   - **HACC**：异构硬件抽象表达
   - **Annotation**：对特定 Operand/Operation 标记 compiler hint
   - **Scope**：与 Annotation 配合标记 compiler hint

3. **HFusion 三层能力**：转换层（与 Arith、Math、Torch 等方言 Operations 对接）→ 预处理（Tensor 表达式化简、`BF16`/`Bool` 数据类型合法化、复杂 Op 组合实现）→ 融合处理（自动融合生成 Device Kernel 算子及 Host Tiling 函数）。HFusion 处理的 operations 均为 `named operations`，以最大化保留高层语义。

4. **HIVM 三层编译优化**：
   - CV 核映射编译（含 CVPipeline pass、AutoSubTiling 实现 1:2 切分）
   - 核内片上内存映射（空间/数据格式推导、访存对齐、地址分配）
   - 核内处理单元映射（流水同步插入、基于策略的指令自动映射、使能 SIMD）

5. **Ascend 950PR/Ascend 950DT 新硬件特性支持**：RegBase（Register-based）编程模型、Warp Scheduler（SIMT 能力）、`ND-DMA` 新指令，以及 SIMD/SIMT 混合编译模式；HIVM 对接社区 TritonGPU 方言构建 Layout/共享内存/指令映射优化算法。

6. **代码组织与版本基线**：
   - 目录：`bishengir/`（实现）、`build-tools/`（构建脚本）、`third-party/`（第三方）
   - 维护分支：`llvm-project` 对应分支为 `Ascend/AscendNPU-IR/llvmorg-19.1.7`，`torch-mlir` 对应分支为 `Ascend/AscendNPU-IR/main-20250716`
   - 历史版本通过 `build-tools/patches` 目录 patch 应用的方式已废弃

---

## 【关键机制与数据】

**HFusion 方言定位与设计原则**（原文）：HFusion 是基于 MLIR 社区 Linalg 方言的扩展集，继承了 Linalg 方言的所有 operations 并扩展了 Linalg 社区还未支持的 operations；所有处理的 operations 均为 `named operations`，用于最大化保留高层语义。

**HFusion 转换层数据流**（原文）：当前支持与 Arith、Math、Torch 等方言关键 Operations 的 Conversion 对接，后续逐步完善生态对接能力。

**HIVM CV 核融合编译数据流**（原文）：
1. 感知 NPU CV 核分离硬件架构，对 Mix Kernel（既含 `cube` 操作又含 `vector` 操作的核函数）进行 CV 融合编译优化；
2. 分析 `cube` 与 `vector` 操作间的数据依赖关系，自动插入 `store` 和 `load` 进行 CV 核数据交互；
3. 计算中间交互所需的 workspace global memory 空间大小，并生成 Host 侧推导大小的函数；
4. 对有 CV 数据依赖处插入核间同步保证依赖顺序；
5. 自动拆分 MixKernel 为单独的 AIC 核函数和 AIV 核函数。

**HIVM 性能优化机制**（原文）：
- **CVPipeline pass**：自动调整 Cube 代码与 Vector 代码顺序，保证 CV 核流水并行；
- **AutoSubTiling**：自动实现 CV 配比 1:2 切分特性。

**HIVM 核内片上内存映射功能**（原文）：自动实现片上内存空间推导、片上内存数据格式推导、片上访存自动对齐、Op 临时空间申请以及片上内存地址分配。

**HIVM 核内处理单元映射功能**（原文）：感知 NPU 核内多级流水处理单元，自动插入流水同步操作保证不同流水线有序执行同时并行流水优化；感知 NPU 指令细节自动完成基于策略的指令自动映射，使能 NPU SIMD 高效指令。

**Ascend 950PR/950DT vs 既有芯片硬件差异**（原文）：
- 继承自 **310B 芯片的 RegBase（Register-based）编程模型**
- 相比 Atlas A2 / Atlas A3 系列产品的 **Memory-based 编程模型**，新增了寄存器层
- 在 Cube 与 Vector 核之间增加了数据通路，为 CV 融合提供更多优化空间
- 新增 Warp Scheduler 等组件引入 **SIMT 能力**
- 新增 `ND-DMA` 等新硬件指令

**AscendNPU IR 在 950PR/950DT 上的新增支持**（原文）：
- HIVM 方言中：Arith 与 Vector 方言支持计算与规约类 Op
- 纯 SIMD 编译：增加 VF 融合、向量化、掩码优化、Combine 优化
- 新增 SIMT 编译支持：将社区 TritonGPU 方言对接至 HIVM，构建昇腾亲和的 Layout 优化、共享内存分配、核心指令映射优化算法
- 支持模式：纯 SIMD、纯 SIMT、SIMD/SIMT 混合编译三种

**工具链角色**（原文）：`bishengir-compile` 把高抽象层级的 Tile 级 Op 编译成感知 NPU 硬件架构的 low level op（输入输出均为 MLIR）；`hivmc` 把 low level 的 MLIR 转成 LLVM IR 并基于 LLVM IR 进行底层指令编译优化，最终生成算子二进制。

---

## 【表格解读】

原文无传统参数/性能对比/配置项表格。但原文含两处 ASCII 目录树（`text` 代码块），属于结构性表格，按要求**逐字还原**如下：

### 表 1：AscendNPU IR 仓库顶层目录结构

```text
.
├── bishengir // AscendNPU IR 相关实现
├── build-tools // AscendNPU IR 构建脚本所在目录
│   └── build.sh
└── third-party
    ├── llvm-project // Ascend 维护分支：Ascend/AscendNPU-IR/llvmorg-19.1.7
    ├── shmem
    └── torch-mlir   // Ascend 维护分支：Ascend/AscendNPU-IR/main-20250716
```

**逐行解读**：
- `bishengir/`：AscendNPU IR（即"毕昇 IR"）自身的实现目录，是文档的核心讨论对象。
- `build-tools/`：构建脚本目录，包含 `build.sh` 入口脚本。原文明确指出：历史版本通过 `build-tools/patches` 目录下的 patch 文件在构建时应用的方式已废弃。
- `third-party/`：第三方依赖目录，包含三部分：
  - `llvm-project`：MLIR 原生社区代码作为第三方引入，对应 Ascend 维护分支 `Ascend/AscendNPU-IR/llvmorg-19.1.7`（基于 LLVM 19.1.7 版本）。
  - `shmem`：共享内存相关第三方依赖。
  - `torch-mlir`：Torch-MLIR 项目，对应 Ascend 维护分支 `Ascend/AscendNPU-IR/main-20250716`（基于 2025-07-16 主线）。

### 表 2：bishengir 子目录结构

```text
.
├── bishengir // AscendNPU IR 相关实现
│   ├── include
│   │   └── bishengir
│   │       ├── Conversion
│   │       └── Dialect
│   │           ├── 社区方言 // 对于社区方言的扩展增强
│   │           └── 自研方言 // 自定义的方言
├── lib
└── tools
    ├── bishengir-compile // AscendNPU IR 编译器命令行驱动程序
    └── bishengir-opt
```

**逐行解读**：
- `include/bishengir/Conversion`：声明不同方言间转换的能力（对应 `.h`、`.hpp`、`.td` 文件）。
- `include/bishengir/Dialect`：声明方言定义与实现；下分两个子目录：
  - `社区方言/`：存放对 MLIR 社区已有方言的扩展增强。
  - `自研方言/`：存放自定义方言（即 HFusion、HIVM、HACC、Annotation、Scope 等）。
- `lib/`：实现代码（`.cpp`），目录结构与 `include/` 基本保持一致。原文另注：构建目录 `build/include` 中包含 TableGen 自动生成的文件（`.h.inc`、`.cpp.inc`）。
- `tools/`：编译工具链目录，包含：
  - `bishengir-compile`：AscendNPU IR 编译器的命令行驱动程序（核心入口）。
  - `bishengir-opt`：优化器工具（MLIR 方言通用 opt 工具）。

### 表 3：IR 三大组成部分（原文文字总结，非代码块）

| 组成部分 | 职责 | 原文示例 |
|---|---|---|
| `Conversion` | 承载不同方言间转换的能力 | 三方生态对接转换（`TorchToHFusion`）；AscendNPU IR 内部方言间转换（如 `HFusionToHIVM`） |
| `Dialect` | 不同方言的定义和实现 | 既包括自研方言，也包括社区方言 |
| `tools` | 定义编译工具链 | `bishengir-compile` 是 AscendNPU IR 编译器的命令行驱动程序 |

---

## 【公式解读】

原文无 LaTeX 数学公式或伪代码公式。

原文中的可视为"过程式表达"的内容（如 HIVM CV 核融合编译的步骤）已在【关键机制与数据】中按工作流形式逐条保留并解读，未引入原文中未出现的符号或公式编号。

---

## 【关联】

**上游输入（生态对接层）**：
- HFusion 转换层对接 **Arith、Math、Torch** 等上游方言 Operations，原文明确"TorchToHFusion"是三方生态对接转换的代表路径。
- 在 Ascend 950PR/Ascend 950DT 上，**社区 TritonGPU 方言**对接至 HIVM，用于 SIMT 编译支持。

**内部方言间转换（IR 内部）**：
- **HFusion → HIVM**：HFusionToHIVM 是 AscendNPU IR 内部方言间转换的代表路径；HFusion 输出高抽象层级的 Tile 级 Op，由 HIVM 精细化感知 NPU 硬件细节并生成底层指令。

**与 MLIR 社区的扩展关系**：
- HFusion 基于 MLIR 社区 **Linalg 方言**扩展，继承了 Linalg 的所有 operations 并扩展了 Linalg 社区还未支持的 operations。
- HIVM 复用社区 **Arith、Vector** 方言的计算与规约类 Op（在 950PR/950DT 上显式支持）。

**下游输出（编译工具链）**：
- `bishengir-compile`（输入输出均为 MLIR）→ `hishengir-opt`（优化）→ `hivmc` → **LLVM IR** → 算子二进制。
- 文档末尾图 `figures/architecture3_zh.png` 即描绘该编译流程。

**硬件代际关联**：
- Ascend 950PR/Ascend 950DT 继承自 **310B 芯片的 RegBase 编程模型**，相比 Atlas A2/A3 系列的 Memory-based 编程模型新增寄存器层与 Cube↔Vector 数据通路。

**代码组织对社区的关系**：
- MLIR 原生社区代码作为第三方引入；AscendNPU IR 增强**优先**在 `include/bishengir/Dialect` 独立目录下创建对应方言目录以避免侵入式修改；无法隔离的修改则提交到 `third-party/` 下对应 Ascend 维护分支，每个修改有单独 `commit` 信息，便于后续回合 MLIR 社区。

---

## 【使用方法】

原文涉及的工具与启用方式如下：

- **核心编译器驱动**：`bishengir-compile`
  - 职责：将高抽象层级的 Tile 级 Op 编译成感知 NPU 硬件架构的 low level op
  - 输入/输出格式：均为 MLIR

- **底层指令编译器**：`hivmc`
  - 职责：把 low level 的 MLIR 转成 LLVM IR，并基于 LLVM IR 进行底层指令编译优化，最终生成算子二进制

- **优化工具**：`bishengir-opt`
  - 职责：AscendNPU IR 的 opt 工具，配合 `bishengir-compile` 使用

- **构建脚本**：`build-tools/build.sh`
  - 备注：历史通过 `build-tools/patches` 目录 patch 文件在构建时应用的方式已废弃

**关键 Pass/自动机制**（原文提及，可通过工具链触发）：
- `CVPipeline pass`：自动调整 Cube/Vector 代码顺序
- `AutoSubTiling`：自动实现 CV 配比 1:2 切分

**Ascend 950PR/Ascend 950DT 启用模式**（原文提及）：支持纯 SIMD、纯 SIMT、SIMD/SIMT 混合编译三种模式选择。

原文未给出具体命令行参数、配置项清单或开关列表；具体 `bishengir-compile` 的 flag 用法、环境变量、CI 入口等未在本篇文档中展开。

## 图文联合解读

- `architecture1_zh.png`: **1) 图中内容**：自顶向下三层结构——AI框架层(MindSpore/PyTorch/TensorFlow等)、生态编程语言层(Triton/Tilelang/FlagTree-TLE/DLCompiler等)、毕昇编译器层(绿色大框含蓝色AscendNPU IR子框，框内并列HFusion与HIVM两方言，下接AscendNPU IR→LLVM IR的Conversion模块与LLVM IR)。箭头从编程语言层汇入AscendNPU IR。

**2) 技术结论**：AscendNPU IR作为统一编译接入层,向上吸收多框架、多编程语言,内部通过HFusion/HIVM方言分层解耦完成"硬件无关优化→硬件细节感知"职责,最终降低为LLVM IR。

**3) 与文档关系**：直观印证"面向生态的统一编译接入层"以及"HFusion负责硬件无关优化、HIVM负责精细化感知NPU硬件"的分层论点。
- `architecture2_zh.png`: 图分两层：上层HFusion基于Linalg扩展，依次为转换层（arith/math/torch方言对接）、预处理（bool/BF16合法化、OP简化分解）、融合层（reshape传播、自动调度、host tiling）；下层HIVM面向昇腾硬件，含核映射编译（核间通信/同步/并行、auto-sub-tiling）、片上内存映射（空间/格式/地址推导）、处理单元映射（流水同步、向量化）。论证"分层解耦"设计：HFusion承担硬件无关优化，HIVM承担硬件细节抽象，两层职责清晰。与文档"硬件无关与硬件感知分层解耦、开源开放"论点一一对应，是其可视化诠释。
- `architecture_A5_zh.png`: **图文联合解读：**

1）**图中结构**：自顶向下分层——AscendNPU IR (A5) 顶层并列 HFusion 与 TritonGPU 两入口；中间层 HIVM 含「CV核映射编译」顶层，下设两条虚线框支路：HIVM-SIMD（VF融合、向量化…）与 HIVM-SIMT（Layout优化、共享内存分配…）；底层落到 LLVM IR。

2）**论证结论**：HIVM 通过 SIMD/SIMT 双路径分别承接 Vector 与 Cube 核的编译优化，CV核映射编译统一调度二者，体现面向昇腾CV分离架构的层次化解耦与异构协同。

3）**与文档关系**：直观印证「HFusion负责硬件无关优化、HIVM精细化感知NPU并提供CV融合编译能力」的核心论点。
- `architecture3_zh.png`: 图示分左右两栏：左栏"中间表达"自上而下排列AscendNPU IR（含HFusion、HIVM方言）、AscendNPU IR到LLVM IR的转换、LLVM IR三层；右栏"工具链"对应bishengir-compile与hivmc；箭头将IR层级与工具逐一映射。论证了IR与编译工具按层一一对应、分层解耦的架构关系，呼应文档"自下而上逐层抽象、分层解耦开源"的目标定位及方言职责划分。
