# Chapter 5: Partial Lowering to Lower-Level Dialects for Optimization

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/Toy/Ch-5.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/Toy/Ch-5.md

# mlir/docs/Tutorials/Toy/Ch-5.md 深度解读

## 【定位】

本文是 MLIR Toy 语言教程第 5 章,描述如何通过 `DialectConversion` 框架将 Toy 方言的计算密集型操作**部分降级**到 `Affine`、`Arith`、`Func`、`MemRef` 等低层方言以复用既有优化,同时把 `toy.print` 暂时保留为合法操作为下一章直接降级到 `LLVM IR` 方言做准备——核心解决"同一函数内多种方言共存时的渐进式降级与跨方言类型(TensorType→MemRefType)转换"问题。

## 【技术要点】

1. **DialectConversion 框架三件套**:使用该框架需提供 (a) `ConversionTarget`(合法/非法操作规格)、(b) 一组 `Rewrite Patterns`(把非法操作改写成合法操作)、(c) **可选** `Type Converter`(转换块参数类型,本文未使用)。

2. **合法方言集合**:本 Pass 目标方言为 `affine::AffineDialect, arith::ArithDialect, func::FuncDialect, memref::MemRefDialect`(通过 `target.addLegalDialect<...>()` 一次声明)。

3. **Toy 方言全量非法 + `toy.print` 动态合法**:`target.addIllegalDialect<ToyDialect>()`;再用 `target.addDynamicallyLegalOp<toy::PrintOp>([](toy::PrintOp op){ return llvm::none_of(op->getOperandTypes(), [](Type t){ return t.isa<TensorType>(); }); });`——即"操作数中**没有任何** TensorType 时"才合法。原文明确指出:"个体操作总是优先于(更通用的)方言定义,因此顺序无关"(可查阅 `ConversionTarget::getOpInfo`)。

4. **ConversionPattern 与 RewritePattern 的差别**:原文强调"ConversionPattern 与传统 RewritePattern 不同在于多了一个 `operands` 参数,该参数持有已被 remapped/replaced 的操作数";该特性正是 TensorType→MemRefType 类型转换所依赖的不变量。示例 `TransposeOpLowering` 继承 `mlir::ConversionPattern`,在构造时传入 `TransposeOp::getOperationName(), 1, ctx`——**pattern benefit = 1**。

5. **`lowerOpToLoops` 辅助 + ODS Adaptor**:模式内调用 `lowerOpToLoops(op, operands, rewriter, [loc](...) {...})`,在 lambda 内通过 ODS 自动生成的 `TransposeOpAdaptor(memRefOperands)` 取得已 remap 的 `input()`(已是 memref),再以 `llvm::reverse(loopIvs)` 的逆序下标构造 `mlir::AffineLoadOp`,完成转置语义。

6. **部分降级入口**:`mlir::applyPartialConversion(getOperation(), target, patterns)`,失败时 `signalPassFailure()`;此模式允许合法操作(如 `toy.print`)留在 IR 中,与降级后操作共存于同一函数体。

## 【关键机制与数据】

- **类型抽象语义差异**(原文):"Tensors represent an abstract value-typed sequence of data, meaning that they don't live in any memory. MemRefs, on the other hand, represent lower level buffer access, as they are concrete references to a region of memory."——这决定了为何必须引入 Type Converter 才能让同函数内 Tensor 与 MemRef 共存过渡。

- **数据流 / 降级路径**(原文):
  1. `toy.transpose(TensorType)` → 通过 `TransposeOpLowering` 匹配;
  2. 操作数被框架 remap 为 `MemRefType` 后传入 `operands`;
  3. `TransposeOpAdaptor` 暴露 `input()`(MemRef);
  4. lambda 借助逆序 IV 生成 `AffineLoadOp`,完成循环嵌套+仿射加载表达。

- **合法性检查谓词**(原文):`llvm::none_of(op->getOperandTypes(), [](Type t){ return t.isa<TensorType>(); })`——只有当**所有**操作数都已非 TensorType 时,`PrintOp` 才视为合法。这等价于:"先把 Tensor 全部降为 MemRef,然后 print 自动变得合法",从而天然衔接降级流程。

- **失败语义**(原文):"The conversion will signal failure if any of our *illegal* operations were not converted successfully."——即 `applyPartialConversion` 返回 failure 时需调用 `signalPassFailure()`。

- **设计权衡**(原文开篇已述,但条目被截断):在"从值类型 TensorType 转到分配型 MemRefType"而又"不降级 `toy.print`"的过渡期,需要在两套世界之间架桥;原文列出 *Generate `load` operations from the buffer* 作为可选方案之一,但列表在 `---` 处被截断,后续条目原文未给出。

> 注:**原文本身在此处断尾(以 `---` 结束)**,后续关于 "bridge Tensor 与 MemRef" 的若干 trade-off 列表并未完整呈现,故不补全。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

根据文末内部链接,可梳理上下游与并列模块关系如下:

| 链接锚点 | 与本文关系 | 作用 |
|---|---|---|
| [Ch-6.md](Ch-6.md) | 紧接本文的下一章 | 直接降级 `print` 到 `LLVM IR` 方言——本文保留 `toy.print` 合法正是为此章铺垫 |
| [Builtin.md/#rankedtensortype](../../Dialects/Builtin.md/#rankedtensortype) | 上游类型 | Toy 操作当前操作的 `TensorType` 定义 |
| [Builtin.md/#memreftype](../../Dialects/Builtin.md/#memreftype) | 下游类型 | 降级目标 `MemRefType`(仿射循环嵌套索引的内存视图)定义 |
| [Glossary.md/#conversion](../../../getting_started/Glossary.md/#conversion) | 术语 | "conversion"概念解释 |
| [DialectConversion.md/#conversion-target](../../DialectConversion.md/#conversion-target) | 框架核心 | `ConversionTarget` 详细规范(合法/非法声明、动态合法谓词、`getOpInfo` 细节) |
| [Glossary.md/#legalization](../../../getting_started/Glossary.md/#legalization) | 术语 | "legalization"概念解释 |
| [DialectConversion.md/#rewrite-pattern-specification](../../DialectConversion.md/#rewrite-pattern-specification) | 框架核心 | 转换用 `RewritePattern`(含 `ConversionPattern`)的规范 |
| [QuickstartRewrites.md](../QuickstartRewrites.md) | 前置 | 第 3 章引入的 `RewritePattern` 写法基础 |
| [DialectConversion.md/#type-conversion](../../DialectConversion.md/#type-conversion) | 框架核心(本文未启用) | `Type Converter` 规范,用于块参数类型转换 |
| [Ch-3.md](Ch-3.md) | 回顾 | 前一章的 canonicalization + RewritePattern 基础 |

整体定位:**Ch-3(规范化)** → **Ch-5(本文:用 DialectConversion 做向低层方言的部分降级)** → **Ch-6(继续把剩余操作向 LLVM IR 降级生成代码)**;`DialectConversion.md` 与 `Builtin.md` 提供底层机制与类型定义支撑。

## 【使用方法】

原文给出的可启用/配置项与命令汇总:

- **声明合法方言**:`target.addLegalDialect<affine::AffineDialect, arith::ArithDialect, func::FuncDialect, memref::MemRefDialect>();`
- **声明非法方言**:`target.addIllegalDialect<ToyDialect>();`
- **声明动态合法操作**:`target.addDynamicallyLegalOp<toy::PrintOp>([](toy::PrintOp op){ return llvm::none_of(op->getOperandTypes(), [](Type type){ return type.isa<TensorType>(); }); });`
- **构建模式集合**:`mlir::RewritePatternSet patterns(&getContext()); patterns.add<..., TransposeOpLowering>(&getContext());`(注意 `TransposeOpLowering` 构造时传入 benefit = `1`)。
- **执行部分降级**:`mlir::applyPartialConversion(getOperation(), target, patterns)`,失败则 `signalPassFailure()`。
- **辅助函数 `lowerOpToLoops`** 在示例中用于把当前操作降到仿射循环嵌套,并向调用者回调最内层循环体的生成逻辑。
- **合法性优先级细节**:个体操作覆盖方言定义,顺序无关,见 `ConversionTarget::getOpInfo`。

> 备注:原文未涉及 CLI flag、配置文件、环境变量或 `mlir-opt` 命令行调用方式的具体写法;关于"如何桥接 Tensor 与 MemRef"的设计选项列表在原文 `---` 处中断,故该处具体条目不臆造。
