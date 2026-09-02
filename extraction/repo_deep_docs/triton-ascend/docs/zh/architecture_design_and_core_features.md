# 架构设计与核心特性

> 仓 `triton-ascend` · 路径 `docs/zh/architecture_design_and_core_features.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-ascend/docs/zh/architecture_design_and_core_features.md

# Triton-Ascend 架构设计与核心特性 — 一体化深度解读

---

## 【定位】

本篇文档描述 Triton-Ascend 的整体逻辑架构（语言扩展 + 编译器 + 驱动三层结构）、代码目录组织原则、以及核心编译模块（语言扩展算子、NPU 编译选项、SIMD 编译器/TritonToStructured 转换）的设计与能力，旨在明确"如何在标准 Triton 之上适配华为 Ascend NPU"。

---

## 【技术要点】

1. **三层逻辑架构**：核心组件包括 `Ascend language extension`（语言扩展）、`compiler`（编译器）、`driver`（驱动），分别承担 DSL 语义扩展、MLIR 编译转换、设备可执行内核加载与对接 CANN 软件栈的职责。

2. **完整编译流水线（原文以伪代码呈现）**：`Triton IR → Linalg IR → AscendNPU IR → triton_xxx_kernel.o`，其中 Triton IR → Linalg IR 的转换由 triton-ascend 完成，Linalg IR → AscendNPU IR → `.o` 由 BiSheng Compiler 完成。

3. **代码分区原则**：target independent（与硬件无关）的修改保留在 Triton core；target affinitive（与 Ascend 强相关）的修改放在 Triton-Ascend，遵循"按硬件亲和度分层"的设计准则。

4. **语言扩展算子**（3 个）：`tl.insert_slice`、`tl.extract_slice`、`tl.get_element`，分别用于张量插入、切片提取、单元素读取。

5. **17 个 NPU 编译选项（NPUOptions）**：覆盖多缓冲（multibuffer）、ping-pong 流水线、CV-fused 内核调优、Barrier/Block 注入、workspace 多缓冲、ND2NZ 布局转换、AutoBlockify、stream 指定等多个自动调优维度。

6. **SIMD 编译器按 IR 转换分类**：分为 4 类 Pass —— triton-to-structured（ttir→ttir 线性化）、triton-to-unstructured（ttir→ttir 间接轴转循环）、triton-to-linalg（ttir→linalgir）、triton-to-other（ttir→hivm/hfusion/llvm）。

7. **TritonToStructured 转换器套件**（7 个 Converter）：处理 `tl.load`/`tl.store` 等操作中指针表达式与 mask 表达式里的整除/取余，通过升维消除 `//` 与 `%` 后重建 `AddPtrOp`/load/store；包含 `RewriteAddPtrOp`、`CreateAddpr`、`RewriteLoadOp`、`BuildMask`、`CreateLoad`、`RewriteStoreOp`、`CreateStore`、`RewriteAtomicRWMOp` 等。

---

## 【关键机制与数据】

### 工作原理

- **语言扩展层**：在标准 Triton 语言基础上引入 Ascend 特定的语法与语义扩展，不影响 Triton core 通用部分（依据代码分区原则）。
- **编译层**：triton-ascend 的 `compiler` 接收 Triton 编译器生成的 TTIR（Triton IR）文件，先将 TTIR 转换为 Linalg IR，再由 BiSheng Compiler 进一步降级到 AscendNPU IR，最终生成设备侧可执行文件 `triton_xxx_kernel.o`。**原文明确指出："Triton IR 转换为 Linalg IR，再经 BiSheng Compiler 生成面向 Ascend NPU 的可执行二进制文件 `triton_xxx_kernel.o`"。**
- **驱动层**：`driver` 提供 Triton runtime 与 CANN 软件栈之间的对接能力，加载 BiSheng Compiler 生成的 `triton_xxx_kernel.o`。

### 代码模块功能映射（原文）

- **`include/` 与 `lib/`**：包含针对 Ascend NPU 的 MLIR Passes、Dialects 及相关工具，用于在 MLIR 编译流程中表达与优化 Ascend 特定计算图。
- **`libdevice.py`**：适配 Ascend NPU 的 libdevice 接口，提供底层实现供 Triton 算子调用。
- **`backend/compiler.py`**：triton-ascend 编译器主入口，把 Triton 高层 DSL 代码编译为 Ascend NPU 可执行二进制（`.o`）。
- **`backend/driver.py`**：驱动模块，加载并启动已编译的可执行二进制。

### TritonToStructured 处理机制（原文）

处理指针表达式和 mask 表达式中的整除取余，通过升维的方法去除整除取余后重新生成 load/store 等 OP。例如对 `ptr + x // 1024 * 4096 + x % 1024 * 4 + y`，分析出 `x`、`y` 各轴贡献与关系并建模为 `PtrState` 对象；对 `mask = x // 1024 < 8 and x % 1024 < 1024 and y < 4`，分析出各维度独立约束并建模为 `MaskState` 对象。

### 性能数据

**原文未涉及**任何性能数字或基准测试数据。

---

## 【表格解读】

### 表 1：3.1.1 Language expansion — 语言扩展算子

| 序号 | 算子名称 | 描述 |
| :--- | :--- | :--- |
| 1 | `tl.insert_slice(full, src, offsets, sizes, strides)` | 按照指定的偏移量（offsets）、尺寸（sizes）和步幅（strides）参数，将一个张量插入到另一个张量中。<br>**返回值**：目标张量。<br>**full**：目标张量，源张量将被插入到此张量中。<br>**src**：源张量。<br>**offsets**：目标张量上的偏移量（整数元组）。<br>**sizes**：源张量上的尺寸（整数元组）。<br>**strides**：目标张量上的步幅（整数元组）。 |
| 2 | `tl.extract_slice(full, offsets, sizes, strides)` | 按照指定的偏移量（offsets）、尺寸（sizes）和步幅（strides）参数，从另一个张量中提取一个切片张量。<br>**返回值**：切片张量。<br>**full**：源张量，从此张量中提取切片。<br>**offsets**：源张量上的偏移量（整数元组）。<br>**sizes**：切片张量的尺寸（整数元组）。<br>**strides**：源张量上的步幅（整数元组）。 |
| 3 | `tl.get_element(source, offset)` | 读取一个具有维度的张量，并返回指定偏移量处的单个元素。<br>**source**：源张量。<br>**offset**：元素提取位置的偏移量（整数元组）。 |

**逐行解读**：
- **算子 1 insert_slice**：标准 Triton 缺失的张量插入原语；在 Ascend NPU 场景下用于将一个子张量（src）按 offsets/sizes/strides 写入到全张量（full）中，6 参接口与 MLIR 的 `tensor.insert_slice` 语义一致；strides 是目标张量维度的步幅（注意非源张量），这与一般 NumPy 风格切片语义有差异。
- **算子 2 extract_slice**：与 insert_slice 互补，用于按相同三参数（元组形式）从 full 中切出子张量；strides 是源张量维度上的步幅，与算子 1 的语义对齐但作用域相反。
- **算子 3 get_element**：单个元素提取；只需 source 与 offset（整数元组）两个参数，是最轻量级的张量子集访问算子。整体三个算子均为切片/点访问类语义扩展，对应 MLIR `tensor` dialect 的 `insert_slice`、`extract_slice`、`extract_element` 的 Triton 语言层封装。

---

### 表 2：3.2.1 Compiler Options — NPU 编译选项

| 序号 | NPUOptions | 硬件平台 | 用途 |
| --- | --------------------------------------------- | ---------- | ----- |
| 1 | multibuffer | NPU | Autotune Option: Enable or disable ping-pong pipeline. |
| 2 | enable_auto_bind_sub_block | NPU | Autotune option (CV-fused kernels only): Enable or disable auto-binding of sub-blocks. |
| 3 | enable_hivm_auto_cv_balance | NPU | Autotune option (CV-fused kernels only): Enable or disable automatic CV balancing. |
| 4 | sync_solver | NPU | Autotune option (CV-fused kernels only): Enable or disable the synchronization solver. |
| 5 | unit_flag | NPU | Autotune Option: Enable or disable the sync unit flag. |
| 6 | inject_barrier_all | NPU | Autotune Option: Enable or disable automatic injection of barriers for all operations. |
| 7 | inject_block_all | NPU | Autotune Option: Enable or disable automatic injection of blocks for all operations. |
| 8 | limit_auto_multi_buffer_only_for_local_buffer | NPU | Autotune Option: Restrict automatic multi-buffering only to local buffers. |
| 9 | limit_auto_multi_buffer_of_local_buffer | NPU | Autotune Option: Enable or disable automatic multi-buffering for local buffers. |
| 10 | set_workspace_multibuffer | NPU | Autotune Option: Enable or disable multi-buffering for the workspace. |
| 11 | tile_mix_vector_loop | NPU | Autotune option (CV-fused kernels only): Enable or disable tiling for vector loops. |
| 12 | tile_mix_cube_loop | NPU | Autotune option (CV-fused kernels only): Enable or disable tiling for cube loops. |
| 13 | disable_auto_inject_block_sync | NPU | Autotune option (CV-fused kernels only): Enable or disable automatic injection of block synchronizations. |
| 14 | stream | NPU | Optional: Inform the compiler about the NPU stream to use. |
| 15 | enable_linearize | NPU | Autotune Option: Enable or disable the linearization pass. |
| 16 | enable_nd2nz_on_vector | NPU | Autotune option (CV-fused kernels only): Enable or disable the ND (n-dimensional) to NZ (non-zero) layout transformation. |
| 17 | auto_blockify_size | NPU | Autotune Option: Enable or disable AutoBlockify pass. It is ignored when TRITON_ALL_BLOCKS_PARALLEL is not set. |

**逐行解读**：
- **#1 multibuffer**：最常用的性能开关，控制 ping-pong 双缓冲流水线，影响访存与计算的重叠度。
- **#2–#4、#11–#13、#16** 标记为 "(CV-fused kernels only)"，仅在 Cube-Vector 融合的内核场景下生效，是 Ascend 硬件特有的融合优化维度（Cube 单元 + Vector 单元协同）。
- **#5 unit_flag**、**#6 inject_barrier_all**、**#7 inject_block_all**、**#8/#9 local buffer 多缓冲限制**、**#10 workspace 多缓冲**、**#15 linearize**：通用性能/同步控制选项，覆盖内存复用、同步粒度、线性化等。
- **#14 stream**：区别于其他选项，是 Optional（非 autotune）型，用于告知编译器目标 NPU stream，是驱动侧运行时信息的下沉通道。
- **#17 auto_blockify_size** 有一条隐含约束："It is ignored when `TRITON_ALL_BLOCKS_PARALLEL` is not set" —— 即只有当环境变量 `TRITON_ALL_BLOCKS_PARALLEL` 被设置时才会生效。
- **整体规律**：17 个选项中 16 个为 Autotune 维度，仅 stream 为运行时信息；其中 7 个仅对 CV-fused kernels 生效，反映出 Ascend NPU 上 Cube/Vector 融合优化是一个相对独立的调优子空间。

---

### 表 3：3.2.2 SIMD compiler Passes — SIMD 编译器 Pass 分类

| 序号 | Pass | 目的 | IR 转换 |
| ------ | ---------------------- |----------------------------------------------------------------------| ----------------------- |
| 1 | triton-to-structured | linearize | ttir->ttir |
| 2 | triton-to-unstructured | convert indirect axis to loop | ttir->ttir |
| 3 | triton-to-linalg | memory/reduction/view/creation/math/arith/linear algebra to linalgir | ttir->linalgir |
| 4 | triton-to-other | ttir->hivm/hfusion/llvm | ttir->hivm/hfusion/llvm |

**逐行解读**：
- **Pass 1 triton-to-structured**：完成"线性化"，仍在 ttir 层面工作；这与下文 3.2.2.1 TritonToStructured 转换器直接对应，是同一概念在 Pass 与 Converter 两个粒度的描述。
- **Pass 2 triton-to-unstructured**：将间接访问轴（indirect axis）转换为显式 loop；同样保留在 ttir 域，是对间接索引模式（典型如 scatter/gather 类）的规范化。
- **Pass 3 triton-to-linalg**：把 ttir 中的 memory/reduction/view/creation/math/arith/linear algebra 等多种 op 类别统一下沉到 Linalg IR，是 Triton→硬件 IR 的主桥梁。
- **Pass 4 triton-to-other**：把尚未被 Linalg 覆盖的 ttir 算子直接翻译到 hivm（Ascend 向量计算中间表示）、hfusion（融合 IR）、llvm 等目标方言/IR，是兜底通道。
- **整体规律**：4 个 Pass 形成一个"先结构化、再去结构化、再统一降级、最后兜底"的降级管线，前两步保持 ttir 自洽，后两步切换到目标硬件的 IR。

---

### 表 4：3.2.2.1 TritonToStructured Converter 矩阵

| Converter | 功能 | 局限性 |
| ------------------------ | -------------------------- | ------------------------- |
| RewriteAddPtrOp | 分析 `tl.load`、`tl.store` 等操作中的指针表达式（`AddPtrOp`）。将原始的指针偏移计算分解并建模为包含各维度（轴）具体偏移信息的 `PtrState` 对象。例如，对 `ptr + x // 1024 * 4096 + x % 1024 * 4 + y`，分析出 `x` 和 `y` 轴的贡献与关系。 | 1. 所涉及的原始迭代轴（如 `x`）必须能被分裂轴（如 `1024`）整除。<br>2. 外部的 `XBLOCK` 大小必须是分裂轴 `divisor` 的整数倍或其约数。 |
| CreateAddpr | 根据分析得到的 `PtrState` 对象，重新构造一个新的 `AddPtrOp` 指针计算操作。新生成的指针表达式将消除原表达式中的整数除法（`//`）和取模（`%`）操作。 | 依赖于 `RewriteAddPtrOp` 成功生成的、合法的 `PtrState`。 |
| RewriteLoadOp | 分析 `tl.load` 操作中的掩码（mask）表达式，将包含整除/取余的复杂掩码条件分解并建模为 `MaskState` 对象。例如，对 `mask = x // 1024 < 8 and x % 1024 < 1024 and y < 4`，分析出各维度的独立约束条件。 | 1. 所涉及的原始迭代轴（如 `x`）必须能被分裂轴（如 `1024`）整除。<br>2. 外部的 `XBLOCK` 大小必须是分裂轴 `divisor` 的整数倍或其约数。 |
| BuildMask | 根据 `MaskState` 重新构造一个新的 mask 表达式，消除原表达式中的 `//` 和 `%`。 | 仅处理由 `RewriteLoadOp` 或 `RewriteStoreOp` 生成的 `MaskState`，无法处理任意复杂的、非规范化的 mask。 |
| CreateLoad | 使用由 `CreateAddpr` 生成的新指针表达式和 `BuildMask` 生成的新 mask 表达式，重新创建（替换）原始的 `tl.load`，完成指令重写。 | 依赖于 `RewriteAddPtrOp`、`CreateAddpr`、`RewriteLoadOp`、`BuildMask` 等前置步骤均成功执行。 |
| RewriteStoreOp | 分析 `tl.store` 操作中的 mask 表达式，功能与 `RewriteLoadOp` 类似，将包含整除/取余的复杂 mask 条件分解并建模为 `MaskState`。 | 与 `RewriteLoadOp` 相同。 |
| CreateStore | 使用由 `CreateAddpr` 生成的新指针表达式和 `BuildMask` 生成的新 mask 表达式，重新创建（替换）原始的 `tl.store`，完成指令重写。 | 依赖于 `RewriteAddPtrOp`、`CreateAddpr`、`RewriteStoreOp`、`BuildMask` 等前置步骤均成功执行。 |
| RewriteAtomicRWMOp | 处理原子读写修改操作（如 `atomic.add`、`atomic.max` 等）中的指针问题。 | （原文表格中此 Converter 的"局限性"列在文档末尾被截断） |

**逐行解读**：
- **RewriteAddPtrOp 与 RewriteLoadOp/RewriteStoreOp** 共享同一条结构性限制："迭代轴必须能被分裂轴整除" 且 "XBLOCK 必须是 divisor 的整数倍或约数"。这意味着 TritonToStructured 是针对"按固定步长切分迭代空间"的规范化模式，并不具备对任意非线性索引的通用处理能力。
- **CreateAddpr → CreateLoad / CreateStore** 形成 "分析 → 重建 → 应用" 的三阶段流水线：分析类（Rewrite*）建模状态对象，重建类（CreateAddpr/BuildMask）生成新的 IR 节点，应用类（CreateLoad/CreateStore）完成 op 替换。任何一个前置步骤失败都会阻断后续步骤。
- **RewriteAtomicRWMOp** 是把原子操作也纳入该升维转换体系，与 load/store 形成对称；但原文未给出该 Converter 的具体例子与局限性描述（被截断）。
- **整体设计目标**：通过升维把 `//`、`%` 从热路径中移除，让生成的 IR 更利于下游硬件 Pass（特别是 ND2NZ、Cube/Vector 分块）做高效映射。

---

## 【公式解读】

**原文无严格数学公式**，但有一处**伪代码形式的编译流水线表达式**：

```
Triton IR → Linalg IR → AscendNPU IR → triton_xxx_kernel.o
```

**逐符号/逐阶段解释**：

| 符号 / 阶段 | 含义与作用 |
| --- | --- |
| `Triton IR`（即 TTIR，Triton 中间表示） | 由上层 Triton compiler 生成，作为 triton-ascend 编译器的输入 IR；承载 Triton DSL 的高级语义。 |
| `→`（第一次转换） | 在 triton-ascend 的 `compiler` 中完成，目标是把 TTIR 转换为 Linalg IR，过程中会执行 SIMD 编译器的若干 Pass（含 triton-to-structured/unstructured/linalg 等）。 |
| `Linalg IR` | MLIR 的 Linalg dialect 中间表示，便于表达结构化的 memory/reduction/view/creation/math/arith/linear algebra 等运算。 |
| `→`（第二次转换） | 由 BiSheng Compiler 完成，从 Linalg IR 降级到 AscendNPU IR。 |
| `AscendNPU IR` | 面向 Ascend NPU 的目标 IR，承载 BiSheng 的优化与硬件映射。 |
| `→`（第三次转换） | 由 BiSheng Compiler 完成，从 AscendNPU IR 生成可执行二进制。 |
| `triton_xxx_kernel.o` | 设备侧可执行内核二进制，`xxx` 代表具体 kernel 名占位；由 `driver` 在运行时加载并启动。 |

**辅助示例表达式**（来自 3.2.2.1，原文为伪代码形式）：

- `ptr + x // 1024 * 4096 + x % 1024 * 4 + y` —— 指针表达式示例；含 `//`（整除）与 `%`（取模），TritonToStructured 把它分解为 `PtrState` 后再消除除法/取模。
- `mask = x // 1024 < 8 and x % 1024 < 1024 and y < 4` —— 掩码表达式示例；同样的"分析 → 升维消除"流程。

---

## 【关联】

**原文无内部链接（文末未提供任何指向其他文档/章节的链接或交叉引用）。**

可基于文档本身内容推断的隐式关联：

- **架构 → 代码**：逻辑架构中的 `compiler` 对应 `backend/compiler.py`，`driver` 对应 `backend/driver.py`，语言扩展层对应 `include/` 与 `lib/` 中的 MLIR Dialects/Passes，以及 `libdevice.py`。
- **编译器 → BiSheng Compiler**：triton-ascend 自身只完成到 Linalg IR 的转换，Linalg IR → AscendNPU IR → `.o` 由 BiSheng Compiler 完成，二者形成上下游协同关系。
- **3.1 Triton core Enhancement 与 3.2 Triton-Ascend**：分别对应"标准 Triton 的语言增强"和"triton-ascend 侧编译选项/Pass 设计"，前者通常在 Triton core 提交以保持通用性，后者在 Triton-Ascend 仓内维护。
- **3.2.2 SIMD compiler（4 个 Pass） → 3.2.2.1 TritonToStructured（7+ 个 Converter）**：前者是 Pass 粒度的总体管线，后者是其中 `triton-to-structured` 这一 Pass 在 TritonToStructured 模块下的 Converter 级展开，二者是同一概念在不同抽象层的体现。
- **仓库迁移说明**：用户上下文指出 triton-ascend 已迁移至 https://github.com/triton-lang/triton-ascend，本文档是该迁移前仓的设计说明。

---

## 【使用方法】

**原文未涉及**具体的启用命令、配置语法或代码调用示例。

可从原文明确得到的"配置/选项维度"信息（仅有名称与作用，不含调用方式）：

- 17 个 `NPUOptions`（multibuffer、enable_auto_bind_sub_block、enable_hivm_auto_cv_balance、sync_solver、unit_flag、inject_barrier_all、inject_block_all、limit_auto_multi_buffer_only_for_local_buffer、limit_auto_multi_buffer_of_local_buffer、set_workspace_multibuffer、tile_mix_vector_loop、tile_mix_cube_loop、disable_auto_inject_block_sync、stream、enable_linearize、enable_nd2nz_on_vector、auto_blockify_size）—— 原文仅列出选项名称与用途，未提供如何在 Triton 程序或 `compile()` 接口中传递这些键值的方式。
- 环境变量 `TRITON_ALL_BLOCKS_PARALLEL`：原文在 `auto_blockify_size` 项中提到该选项 "is ignored when TRITON_ALL_BLOCKS_PARALLEL is not set"，但未给出该环境变量的取值规范与作用域。
- 入口文件 `backend/compiler.py` 与 `backend/driver.py`：原文指出它们分别是"编译器主入口"与"驱动模块"，但未给出 API 调用示例或环境搭建步骤。

如需具体调用方式（如何在 Python 侧将 NPUOptions 传入 triton.compile、如何加载 triton-ascend 驱动、BiSheng Compiler 的安装/路径对接等），需要参考其他章节或迁移后仓库（https://github.com/triton-lang/triton-ascend）中的开发者指南，本文档**未提供**。

## 图文联合解读

- `architectural_diagram.png`: **图文联合解读：**

1) **图示内容**：自上而下三层架构——上层"**Triton**"（含 compiler/language/runtime）；中层"**Triton Ascend**"含 Ascend 语言扩展、compiler（Triton IR→Linalg IR）、driver、libdevice；下层"**BiSheng Compiler**"含 AscendNPU IR（HFusion/HIVM Dialect）→LLVM IR→后端代码生成。棕色箭头标示上下层依赖与 IR 下沉流向。

2) **技术结论**：Triton-Ascend 采用"上游 Triton + 适配层 + 下游 BiSheng"的分层解耦设计，以 MLIR 多级 IR 渐进式降低（TTIR→Linalg IR→AscendNPU IR→LLVM IR）实现从通用 Triton DSL 到 Ascend NPU 可执行码的端到端编译。

3) **与文档关系**：图像与文档"逻辑架构"章节严格一一对应——三块核心组件（语言扩展/编译器/驱动）及其 IR 转换公式 `Triton IR → Linalg IR → AscendNPU IR → .o` 被完整可视化，印证"目标硬件相关修改下沉至 Triton-Ascend 与 BiSheng"的代码分层原则。
