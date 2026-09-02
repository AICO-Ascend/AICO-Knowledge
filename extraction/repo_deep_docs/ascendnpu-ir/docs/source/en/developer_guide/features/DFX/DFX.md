# Debugging Module (DFX)

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/DFX/DFX.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/DFX/DFX.md

【定位】
本文档介绍了 AscendNPU IR 调试模块（DFX, Debugging Module）中的 `device_print` 子特性——一种在昇腾 NPU 上基于 Triton 框架实现的设备侧调试打印能力，用于在算子 kernel 执行过程中直接打印标量/向量信息，并通过 AscendNPU IR 阶段的多趟 Pass 转换打通从 Triton 高级 API 到硬件可执行指令的完整链路。

【技术要点】
- **硬件资源上限**：每个 AI core 固定分配 **16 KB** 的 UB（Unified Buffer）打印缓冲区，同一 aicore 内所有 print 操作共用此 16 KB 空间，缓冲满后将丢弃新数据并发出"数据超出最大缓冲容量"警告。
- **多核并发**：各 AI core 独立执行 kernel 代码，最终将各自打印结果汇总到 host 端输出。
- **三级协作架构**：`device_print` 由 Triton Ascend、AscendNPU IR、毕昇（Bisheng）编译器三方协作实现；文档聚焦 AscendNPU IR 部分。
- **API 转换链路**：Triton 侧 `tl.device_print` → `.ttadapter` IR 中的 `func.call @triton_print_*` → AscendNPU IR 中经两趟 Pass 转换为 `hfusion.print`，再转换为 `hivm.hir.debug`，最终落到硬件指令。
- **专用 Pass 集合**（按执行顺序）：`AdaptTritonKernel` → `HFusionToHIVM` → `InlineFixpipe` → `InsertNZ2NDForDebug` → `SplitMixKernel` → `InsertInitAndFinishForDebug`。
- **数据位置限制**：`device_print` 仅支持打印 UB/GM 上的数据；当打印 L1 数据时需经 `InsertNZ2NDForDebug` Pass 插入 `nz2nd` 操作将数据搬至 GM。

【关键机制与数据】

**整体数据流（原文 mermaid 图）**：
Host Launcher 在 kernel 启动前 (1) 传递 print buffer → 执行 kernel → kernel 返回后 (2) 读 buffer → (3) 解析并打印到终端。代码实现侧由 BiSheng 头文件中的 Builtin print 逻辑通过 `triton-ascend` 集成自动提取，最终回调 Host Launcher。

**Pass 转换机制**（逐趟说明，按原文保留关键属性）：

1. **AdaptTritonKernel**：把 `func.call @triton_print_*` 重写为 `hfusion.print`。原文示例属性：`{hex = false}`，字符串前缀如 `" x: "`，被打印的张量类型如 `tensor<8xi64>`。

2. **HFusionToHIVM**：把 `hfusion.print` 降级为 `hivm.hir.debug`。原文示例属性：`debugtype = "print"`、`hex = false`、`prefix = " x: "`、`tcoretype = #hivm.tcore_type<CUBE_OR_VECTOR>`。

3. **InlineFixpipe**：当被打印的值是从 `scf.for` yield 出来的 `hivm.mmadL1` 结果时，在 `hivm.print` 之前插入 `hivm.fixpipe`，保证打印结果是已搬出的数据。

4. **InsertNZ2NDForDebug**：检测 `hivm::MmadL1Op` 的输入是否被 `hivm::DebugOp` 使用；若是，则通过 `memref_ext.alloc_workspace()` 分配工作区，插入 `hivm.hir.nz2nd` 把 L1 上 NZ 格式的中间结果搬到 GM 再打印。原文示例中输入 `tensor<1x4xf32>` 经 NZ2ND 后输出到工作区张量 `%14`，随后 `hivm.hir.debug` 的操作数由 `%12` 改为 `%15`。

5. **SplitMixKernel**：对 mix kernel 先用 `InferCoreType` 推断 Debug op 的精确 core 类型（VECTOR/CUBE），默认 `CUBE_OR_VECTOR`；再将 mix 函数拆分为纯 Cube 与纯 Vector 两部分，以决定 Debug op 最终跑在 Cube 核还是 Vector 核。

6. **InsertInitAndFinishForDebug**：检测到任意 Debug op 时，在函数入口插入 `hivm.hir.init_print`，在每个 `hivm.hir.print` 后插入 `hivm.hir.finish_print`。原文明确说明二者目前尚无具体作用（"no specific effect"），是为后续 `device_print` 扩展预留接口。

**打印缓冲区约束**：原文明确"所有 print 操作在同一 aicore 内共享 16 KB 缓冲"，未给出单条打印的最大字节数或最多次数等具体数字，因此本解读不做任何额外推算。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
文档在 Pass 命名与操作类型上点出了与 AscendNPU IR 其他子模块的明确依赖关系，但文档未提供文末内部链接：
- **`hivm` 层 IR**：所有底层 Pass（`InlineFixpipe`、`InsertNZ2NDForDebug`、`SplitMixKernel`、`InsertInitAndFinishForDebug`）都围绕 `hivm.hir.debug`、`hivm.hir.print`、`hivm.hir.mmadL1`、`hivm.hir.fixpipe`、`hivm.hir.nz2nd`、`hivm.hir.load` 等操作展开，说明 DFX 能力与 AscendNPU IR 的 HIVM（CUBE/VECTOR 指令层）模块深度耦合。
- **`hfusion` 层 IR**：作为 `func.call @triton_print_*`（Triton 高层 API）到 `hivm.hir.debug`（HIVM 指令层）之间的中间表达，对应 `HFusionToHIVM` 这类跨方言转换 Pass。
- **Triton Ascend / BiSheng**：文档明确说明 `device_print` 由三方协作完成，本文档仅覆盖 AscendNPU IR 阶段，前后端的语义保留与代码生成由 Triton Ascend 与 BiSheng 编译器承担。
- **AI 硬件抽象**：UB 打印缓冲、多核并发、Cube/Vector 核拆分等机制均直接对应昇腾 NPU 硬件特性，说明 DFX 必须与硬件内存层次（Cbuf/UB/GM/L1 等 AddressSpace）协同。

【使用方法】
原文未给出具体的用户侧启用开关、环境变量、CLI 命令或配置文件项；文档聚焦于 IR 转换机制本身，相关打印 API 由 Triton 侧的 `tl.device_print` 触发，开发者通过在算子代码中调用该 API 即可走通本路径。文档最后一段代码示例（`InsertInitAndFinishForDebug`）在原文中被截断，故该 Pass 的完整"Before/After"对照未能呈现。
