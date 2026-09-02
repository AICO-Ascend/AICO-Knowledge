# Architecture Design

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/introduction/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/introduction/architecture.md

# AscendNPU-IR Architecture Design 文档深度解读

---

## 【定位】

本文档是 AscendNPU IR（内部代号 bishengir）的**总体架构总览**，系统阐述其基于 MLIR 生态的分层抽象体系、方言（Dialect）划分、代码组织结构以及端到端编译流程，旨在为上层生态框架（PyTorch/Triton 等）提供面向昇腾 NPU 硬件的"统一编译入口 + 完整硬件表达与优化"能力。

---

## 【技术要点】

1. **五类自研方言（In-house Dialects）**：HFusion、HIVM、HACC、Annotation、Scope，分别承担"硬件无关优化 / 细粒度硬件感知 / 异构抽象 / 编译器提示标记"职责。
2. **HFusion = 社区 Linalg 的扩展集**：保留所有命名操作（named op）以保高层语义，分为 Conversion（生态对接 Arith/Math/Torch 等）、Preprocessing（tensor 简化、BF16/Bool legalization、复合 OP 分解）、Fusion（自动生成 Device Kernel + Host Tiling 函数）三层能力。
3. **HIVM = 昇腾硬件抽象 VM**：屏蔽低层指令参数，提供任意维度/大小的 Tensor/Memref tile 级操作；分层为 CV 核映射、片上存储映射、执行单元映射三层。
4. **CV 融合与 1:2 子分块**：CVPipeline pass 自动调度 Cube/Vector 顺序以启用核间流水线并行；AutoSubTiling 自动实现 CV **1:2 subtiling ratio**；Mix Kernel 会被拆分为独立 AIC 与 AIV 函数并自动插入核间同步、workspace 推导与 Host-side size-derivation 函数。
5. **A5 芯片新硬件特性支持**：继承 310B 的 RegBase（Register-based）编程模型；新增 Cube↔Vector 数据通路、Warp Scheduler（引入 SIMT）、ND-DMA 等新指令；HIVM 同步支持 Arith/Vector 的 compute 与 reduction OP，并在 SIMD 路径新增 VF fusion / vectorization / mask optimization / Combine optimization，并将社区 TritonGPU 下沉到 HIVM 支持 SIMT 编译，可输出纯 SIMD、纯 SIMT 或 SIMD/SIMT 混合编译产物。
6. **代码与构建架构**：以 bishengir 子仓承载自有实现，build-tools 提供 patch 与构建脚本，third-party 引入 llvm-project 与 torch-mlir；非侵入式增强放在 `bishengir/Dialect` 各方言目录，侵入式改动以独立 patch 文件（含独立 commit 信息）提交，便于回灌 MLIR 社区；命令链为 `bishengir-compile`（高层 tile → NPU-aware 低层 ops，IO 均为 MLIR）→ `hivmc`（低层 MLIR → LLVM IR → 算子二进制）。

---

## 【关键机制与数据】

**工作原理 / 数据流（原文抽取并标注）：**

- **逐层抽象与解耦**（原文: "performs abstraction, compilation, and optimization from bottom to top over Ascend low-level instructions, intra-core resources, inter-core resources, and SoC resources. The multiple abstraction layers are decoupled and open-source"）。
- **HFusion 命名操作保语义**（原文: "the operations handled by the HFusion dialect are all named operations, so that high-level semantics are preserved as much as possible for the compiler to process"）。
- **CV 融合自动拆分**（原文: "by analyzing data dependencies between cube and vector operations, it automatically inserts store and load for CV core data exchange, derives the workspace global memory size required for intermediate exchange and generates the Host-side size-derivation function, inserts inter-core synchronization at CV data dependencies to guarantee dependency order, and finally splits MixKernel into separate AIC and AIV kernel functions"）。
- **CV 子分块比例 1:2**（原文: "AutoSubTiling automatically implements the CV 1:2 subtiling ratio"）。
- **A5 相对 A2/A3 的硬件差异**（原文: "Compared with the Memory-based programming model of the A2 and A3 chips, it adds a register layer at the hardware level; a data path is added between the Cube and Vector cores"）。
- **A5 新增硬件组件**（原文: "components such as the Warp Scheduler are added to introduce SIMT capability; in addition, new hardware instructions such as ND-DMA are also introduced"）。
- **A5 编译模式三种**（原文: "AscendNPU IR for A5 supports not only pure SIMD and pure SIMT compilation, but also hybrid SIMD/SIMT compilation"）。
- **端到端编译路径**（原文: "The AscendNPU IR toolchain is bishengir-compile, which compiles high-level tile-level OPs into NPU-hardware–aware low-level ops; both input and output of this toolchain are MLIR. The hivmc tool is responsible for converting low-level MLIR into LLVM IR and for low-level instruction compilation and optimization on LLVM IR, finally producing the operator binary"）。

**性能数据**：原文未给出任何量化性能指标（吞吐、延迟、加速比等）。

---

## 【表格解读】

**原文无表格**（无参数表、性能对比表、配置项表）。文档中仅有 3 个 ASCII 目录结构代码块（仓库根目录、`bishengir` 子目录、构建产物目录）以及若干图片引用（`figures/architecture1.png`、`figures/architecture2.png`、`figures/architecture3.png`、`figures/architecture_A5.png`），均不属于狭义"表格"范畴。

---

## 【公式解读】

**原文无公式**（无 LaTeX、伪代码或数学表达式形式的公式）。

---

## 【关联】

虽然文末未提供内部交叉链接（用户标注"无"），但依据文中显式描述可梳理出以下模块/上下游关系：

1. **上游生态接入**（Conversion 层方向）：
   - HFusion ↔ Arith / Math / Torch（"Conversion layer… currently supports conversion with key operations of Arith, Math, Torch and other dialects"）。
   - 第三方 Torch 下沉通道：`TorchToHFusion`（"third-party ecosystem conversions (e.g. TorchToHFusion)"）。
   - TritonGPU 下沉到 HIVM（A5 路径）："lower the community TritonGPU dialect to HIVM"。

2. **内部方言互转**：
   - `HFusionToHIVM`：HFusion 经此转换进入硬件感知层（"internal AscendNPU IR dialect conversions (e.g. HFusionToHIVM)"）。
   - hivmc 进一步把 HIVM 输出转换为 LLVM IR（"hivmc tool is responsible for converting low-level MLIR into LLVM IR"）。

3. **方言间职责互补**：
   - HFusion（硬件无关优化）→ HIVM（硬件细节感知与指令下沉）→ HACC（异构硬件抽象）。
   - Annotation 与 Scope 不参与主计算图转化，仅作为 Operation/Operand 上的编译器提示标记（"Annotation and Scope are responsible for marking compiler hint information for specific Operands or Operations"）。

4. **代码组织与社区关系**：
   - 自研增强优先放在 `bishengir/Dialect/<Dialect名>/` 独立目录以避免侵入社区代码（"enhancements to MLIR upstream by AscendNPU IR are preferably placed under bishengir/Dialect in separate dialect directories… to avoid invasive changes to the community code"）。
   - 非隔离改动以 patch 形式提交到 `build-tools/patches/{llvm-project,torch-mlir}/`，每个 patch 携带独立 commit 信息以便未来回灌 MLIR 社区。

5. **芯片代际差异**：
   - A2/A3：Memory-based 编程模型，走 HIVM 标准路径。
   - A5（含 310B）：RegBase 编程模型，新增 register layer、Cube↔Vector 直连数据通路、Warp Scheduler、ND-DMA，HIVM 通过 SIMD/SIMT/Hybrid 三种编译模式覆盖。

---

## 【使用方法】

原文涉及但未展开细节的命令与脚本如下：

- **命令链（编译入口）**：
  - `bishengir-compile`：高层 tile-level OPs → NPU-hardware-aware 低层 ops，输入输出均为 MLIR；是 AscendNPU IR 编译器命令行驱动（"command-line driver of the AscendNPU IR compiler"）。
  - `bishengir-opt`：工具目录中定义的另一个编译工具（与 `bishengir-compile` 同列于 `tools` 下）。
  - `hivmc`：低层 MLIR → LLVM IR，并完成 LLVM IR 上的低层指令编译与优化，最终生成算子二进制。

- **构建脚本**（位于 `build-tools/`）：
  - `apply_patches.sh`：应用对第三方项目的侵入式补丁。
  - `build.sh`：构建 AscendNPU IR 自身。

- **补丁组织**：
  - `build-tools/patches/{llvm-project,torch-mlir}/0001-[Huawei][MLIR]-xxx.patch`：每个 patch 含独立 commit 信息，便于未来与 MLIR 社区合并。

原文**未给出** `bishengir-compile` / `hivmc` / `bishengir-opt` 的具体命令行参数、Pass 开关、配置选项或环境变量；亦未给出具体调用示例，需结合其他文档（如 Getting Started / User Guide 类）查阅。

## 图文联合解读

- `architecture1.png`: **图文联合解读**

1）**画面内容**：图分三层堆叠。最上层是AI框架（MindSpore、PyTorch、TensorFlow…）；中层是生态语言（Triton、Tilelang、FlagTree/TLE、DLCompiler…），以箭头统一汇入下方编译器；下层BiSheng编译器嵌套AscendNPU IR（内含HFusion与HIVM两个子Dialect）、"AscendNPU IR 2 LLVM IR"转换层、以及LLVM IR。

2）**技术结论**：论证"多前端—统一中间表示—底层多目标"的解耦编译栈范式，多种AI框架与生态语言共用同一IR入口与转换通道。

3）**与文档论点关系**：呼应"分层解耦、生态灵活接入"主张，体现HFusion承担硬件无关优化、HIVM承担硬件细节感知与指令转换，再下沉至LLVM IR完成统一硬件表达与优化。
- `architecture2.png`: **图文联合解读：**

**图示内容：** 图分两大模块。上方HFusion（多维融合抽象）以"Linalg"为底座，自上而下分三层：转换层（arith/math/torch→hfusion）、预处理（bool/BF16合法化、算子简化分解）、融合层（Reshape传播、Flatten、自动调度、Host Tiling）。下方HIVM（Ascend硬件高层抽象）分三层映射：核映射编译（核间通信、同步、并行、Workspace、Auto-Subtiling）、片上存储映射（空间/格式/地址推导）、处理单元映射（流水线同步、矢量化）。

**技术结论：** HFusion沿Linalg做硬件无关的逐层算子融合与规范化；HIVM则自上而下完成Core→存储→PU的硬件细节落地，体现MLIR"渐进式lower"的分层设计思想。

**与文档关系：** 印证HFusion基于Linalg扩展、负责"硬件相对无关优化"，HIVM负责"细粒度感知NPU硬件并转译低层指令"的论点，呈现二者解耦、各司其职的架构分工。
- `architecture_A5.png`: **1) 图中内容**：分层架构图——顶层 AscendNPU IR (A5) 上承 HFusion 与 TritonGPU 两个高层方言；中层 HIVM 通过 CV Core Mapping Compilation 统一调度，并行展开 HIVM-SIMD（VF Fusion、Vectorization、Other Optimization）与 HIVM-SIMT（Layout Optimization、Shared Memory Allocation、Other Optimization）双后端路径；底层统一落到 LLVM IR。

**2) 技术结论**：HIVM 采用 SIMD 与 SIMT 双后端并行架构，分别承担向量融合优化与线程级并行优化，二者协同覆盖 Ascend 不同执行单元的硬件特征。

**3) 与文档关系**：图示印证文档"多抽象层解耦、生态开放"的核心论点——上层 HFusion/TritonGPU 灵活对接第三方框架，HIVM 承上启下完成硬件感知与指令生成，呼应"分层抽象、统一编译入口"的设计理念。
- `architecture3.png`: 图示：左侧IR层（蓝）含HFusion/HIVM方言及AscendNPU IR→LLVM IR转换；右侧工具链（黄）为bishengir-compile与hivmc。箭头表明bishengir-compile处理MLIR级AscendNPU IR，hivmc承接LLVM IR后端编译。呼应文档"基于MLIR生态、自顶向下多层抽象、统一编译入口"的论点。
