# 调试模块DFX

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/dfx.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/dfx.md

# ascendnpu-ir 调试模块 DFX 文档深度解读

## 【定位】

本文档系统性描述了 AscendNPU-IR 中**调试模块 DFX（`device_print`）**的硬件背景、跨层（BiSheng 头文件 / Triton-Ascend / AscendNPU IR / 毕昇编译器）协同实现原理，以及在 AscendNPU IR 阶段所经历的多个 MLIR Pass 变换过程，目的是让开发者理解如何在昇腾 NPU 上把 Triton 的 `tl.device_print` 端到端落到底层硬件打印。

---

## 【技术要点】

1. **device_print 整体流程**（原文 Host 侧流程）：Host Launcher → ①传递打印缓冲区 → Kernel 执行 → ②Kernel 返回 → 读取缓冲区 → ③解析并打印 → 终端输出；代码实现侧由 BiSheng 头文件内置打印逻辑自动抽取，被 triton-ascend 集成后再被 Host Launcher 调用。

2. **关键硬件资源约束**（原文）：
   - 每个 aicore 固定分配 **16 KB** UB 打印缓冲区。
   - **同一个 aicore 内的所有打印操作共享这 16 KB 缓冲区**，写满后新数据提示 warning，大小超过缓冲区最大值后丢弃。
   - **每个 aicore 独立执行内核代码**，Host 侧呈现每个核的打印结果。

3. **三部分协同**（原文）：实现涉及 Triton Ascend、AscendNPU IR、毕昇编译器三部分配合，重点在 AscendNPU IR 阶段展开；Triton Ascend 在生成初始 `.ttadapter` IR 过程中会将 `tl.device_print` 转换成 `func.call @triton_print_*` 接口。

4. **AscendNPU IR 中的 Pass 链条**（原文按出现顺序）：
   - `AdaptTritonKernel`：把 `func.call @triton_print_*` 转换成 `hfusion.print`。
   - `HFusionToHIVM`（文中以 `ConvertHFusionToHIVM` 为例展示）：把 `hfusion.print` 转换成 `hivm.hir.debug`（属性含 `debugtype = "print"`、`hex = false`、`prefix`、`tcoretype = #hivm.tcore_type<CUBE_OR_VECTOR>`）。
   - `InlineFixpipe`：在 `hivm.mmadL1` 后插入 `hivm.fixpipe`，使 `hivm.print` 能打印 `mmad` 结果（`scf.for` 的 yield 值）。
   - `InsertNZ2NDForDebug`：`device_print` 仅支持 UB/GM 打印，对 L1 数据需通过 `hivm::DebugOp` 识别 `hivm::MmadL1Op` 的输入、申请 workspace、插入 `nz2nd` op 搬至 GM 再打印。
   - `SplitMixKernel`：`mix` 类用例中 `Debug` op 先做 `InferCoreType`（默认 `CUBE_OR_VECTOR`）精确推断为 VECTOR 或 CUBE，再将 `mix` 函数拆分为纯 cube 与纯 vector 函数，决定 `Debug` op 落在哪个核上。
   - `InsertInitAndFinishForDebug`：在每个函数开头插入 `hivm.hir.init_print`、每个 `hivm.hir.print` 后插入 `hivm.hir.finish_print`；`init_print` 用于打印前准备、`finish_print` 用于打印后收尾，目前为预留扩展接口。
   - `ConvertHIVMToStandard`（文档在该小节标题后被截断，未给出完整说明）。

5. **`hivm.hir.debug` 关键属性**（原文 IR 中反复出现）：
   - `debugtype = "print"`
   - `hex = false`（十六进制开关）
   - `prefix = " ... "`（打印前缀，如 `" x: "`、`" a_vals: "`、`" acc_11: "`）
   - `tcoretype = #hivm.tcore_type<CUBE_OR_VECTOR>`（被 `SplitMixKernel` 进一步精确化为 VECTOR/CUBE）

6. **打印支持的存储层级**（原文）：`device_print` 仅支持 **UB / GM** 上的数据打印；L1 数据必须经 `nz2nd` 搬到 GM 后再打印。

---

## 【关键机制与数据】

**工作原理 / 数据流（整合自原文）**：

- **跨层接口下沉路径**：`tl.device_print` → `func.call @triton_print_*`（`.ttadapter` IR 中）→ `hfusion.print`（`AdaptTritonKernel`）→ `hivm.hir.debug`（`HFusionToHIVM`）→ 最终被 `ConvertHIVMToStandard` 等下游 Pass 进一步 lowering。
- **mmad 结果打印链路**：`scf.for` 中 `mmad` → `InlineFixpipe` 插入 `hivm.fixpipe` → `hivm.print` 打印 yield 值；若该值位于 L1，则 `InsertNZ2NDForDebug` 申请 workspace 并插入 `hivm.hir.nz2nd` 把数据从 L1 搬到 GM 后再由 `hivm.hir.debug` 打印。
- **核分工机制**：`SplitMixKernel` 通过 `InferCoreType` 把 `tcoretype` 由默认 `CUBE_OR_VECTOR` 精确为 `VECTOR` 或 `CUBE`，并把混合函数拆成纯 cube / 纯 vector 两个函数，使 `Debug` op 落到对应核。
- **生命周期包裹**：`InsertInitAndFinishForDebug` 在每个函数开头插入 `hivm.hir.init_debug`（原文 IR 中出现的语法形式为 `init_print`），在每个 `hivm.hir.debug`（含 `finishInserted = 0 : i32` 标记）之后插入 `hivm.hir.finish_debug`，作为打印前后钩子。

**性能 / 容量数据（原文有标注）**：

| 数据 | 原文 |
|---|---|
| UB 打印缓冲区大小 | 原文：**16 KB / aicore** |
| 缓冲区共享范围 | 原文：同一 aicore 内的所有打印操作**共享**这 16 KB |
| 缓冲区写满行为 | 原文：写满后新数据提示 warning，大小超过缓冲区最大值后**丢弃** |
| 并发粒度 | 原文：每个 aicore 独立执行内核代码，Host 侧呈现每个核的打印结果 |
| 打印支持的存储位置 | 原文：仅支持 **UB / GM**，L1 需经 `nz2nd` 搬到 GM |
| 示例张量形状（来自 IR 片段） | `tensor<8xi64>`、`tensor<1x4xf32>`、`tensor<4x1xf32>`、`tensor<1x1xf32>`、`memref<1x1xf32, #hivm.address_space<gm>>` |
| 标量常数（来自 IR 片段） | `%c1`、`%c4`（index）、`%c0_i64`、`%c-1_i64`、`%c1_i64` |
| `InlineFixpipe` 中 affine map | 原文：`affine.apply affine_map<()[s0] -> (s0 * 4)>()[%16]`（步长为 4，对应 `f32` 字节数） |
| `Sync` 同步参数个数 | 原文：`sync_related_args(%c1_i64, %c0_i64, %c-1_i64, %c-1_i64, %c-1_i64, %c-1_i64, %c-1_i64)` 共 **7 个 i64** |

---

## 【表格解读】

**原文无表格**（原文以 MLIR 代码块、mermaid 流程图、列表呈现，未提供参数表/性能对比表/配置项表格）。

---

## 【公式解读】

**原文无数学公式**（原文出现的仅是 MLIR 操作/属性语法片段，例如 `affine.apply affine_map<()[s0] -> (s0 * 4)>()[%16]` 是 MLIR 的 affine map 表达式，并非独立数学公式；`memref.reinterpret_cast` 的 offset/sizes/strides 也属于地址计算描述而非公式）。下文逐字保留并解释其中最值得注意的地址计算片段：

- **原文逐字保留**：`%17 = affine.apply affine_map<()[s0] -> (s0 * 4)>()[%16]`
  - 含义：依据输入符号 `%16`（被 `arith.index_cast %2 : i64 to index` 产生），按映射 `s0 -> s0 * 4` 计算偏移。
  - 作用：用于将元素索引转换为以 **4 字节为步长** 的字节偏移，对应 `f32`（32 位 = 4 字节）的元素跨度，从而在 `memref.view` 中切出 `memref<1x1xf32, #hivm.address_space<gm>>` 视图。

- **原文逐字保留**：`memref.reinterpret_cast %arg2 to offset: [0], sizes: [8], strides: [1] : memref<?xi64> to memref<8xi64, strided<[1]>>`
  - 含义：把动态形状 `memref<?xi64>` 重解释为静态形状 `memref<8xi64>`，偏移 0、维度大小 8、步长 1。
  - 作用：为 `device_print` 提供长度为 8 的 `i64` 张量作为待打印数据。

- **原文逐字保留**：`memref.reinterpret_cast %arg4 to offset: [%14], sizes: [4, 1], strides: [%13, 1] : memref<?xf32> to memref<4x1xf32, strided<[?, 1], offset: ?>`
  - 含义：以 `%13`（行步长）和 `%14`（起始偏移）构造一个 4×1 的 `f32` 视图，行步长动态（记为 `?`），列步长 1。
  - 作用：在 `hivm.hir.load` 中按动态行步长把 `f32` 数据加载到 `memref<4x1xf32>` 暂存。

---

## 【关联】

原文未提供文末内部链接，但从文档正文可识别出与本特性紧密耦合的上下游模块 / 组件：

- **上游**：Triton 端的 `tl.device_print` 原语 → 由 Triton Ascend 在生成 `.ttadapter` IR 时下沉为 `func.call @triton_print_*`。
- **本层（AscendNPU IR）多 Pass 协作**：
  - `AdaptTritonKernel`（`triton_print_*` → `hfusion.print`）
  - `HFusionToHIVM`（`hfusion.print` → `hivm.hir.debug`）
  - `InlineFixpipe`（为打印 `mmad` 结果补 `fixpipe`）
  - `InsertNZ2NDForDebug`（L1 → GM 的 `nz2nd` 搬运）
  - `SplitMixKernel`（`mix` 函数按 `InferCoreType` 拆分 cube/vector）
  - `InsertInitAndFinishForDebug`（插入 `init_print` / `finish_print` 包裹）
  - `ConvertHIVMToStandard`（文档在该标题后被截断，未给出完成描述，但属于下游继续 lowering 的一环）
- **下游**：毕昇编译器（BiSheng 头文件内置打印逻辑，自动抽取并集成进 triton-ascend）→ Host Launcher → Kernel 执行 → Host 读取 16 KB UB 打印缓冲区 → 解析并打印到终端。
- **硬件耦合**：昇腾 NPU 的 **aicore**（每个核 16 KB UB 打印缓冲，cube / vector 两类核由 `SplitMixKernel` 决定 Debug op 落点）。

---

## 【使用方法】

原文未涉及启用方式 / 配置项 / 命令行的具体说明（文档定位为算法原理与 IR 变换说明，未给出开关、环境变量、CLI 参数或示例调用脚本）。

原文仅可推断出以下隐含的「使用方法相关事实」（不作扩展）：

- 调用入口为 Triton 侧的 `tl.device_print`（通过 `BiSheng 头文件` 内置打印逻辑自动抽取并由 `triton-ascend` 集成）。
- 打印字符串前缀由 `hfusion.print` 的 `" ..."` 字面量决定（原文中出现 `" x: "`、`" a_vals: "`、`" acc_11: "`），并最终落入 `hivm.hir.debug` 的 `prefix` 属性。
- 是否按十六进制打印由 `hfusion.print {hex = false}`（对应 `hivm.hir.debug {hex = false}`）控制。
- 打印张量示例形状：`tensor<8xi64>`、`tensor<1x4xf32>`、`tensor<4x1xf32>`、`tensor<1x1xf32>`。
- 打印数据位置限制：仅支持 **UB / GM**（L1 必须经 `InsertNZ2NDForDebug` 搬到 GM 后才能打印）。

> 注：原文 `ConvertHIVMToStandard` 小节在被截断处停止，因此该 Pass 及更下游的启用细节无法从原文确认。
