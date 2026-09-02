# Chapter 6: Lowering to LLVM and CodeGeneration

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/Toy/Ch-6.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/Toy/Ch-6.md

# Chapter 6: Lowering to LLVM and CodeGeneration — 一体化深度解读

## 【定位】

本文档解决"如何将经 Ch-5 部分 lowering 后的 Toy IR 通过 dialect conversion 框架完整下沉到 LLVM dialect、导出 LLVM IR 并进入代码生成阶段"的问题，描述了从结构化 SCF/Affine 循环到 LLVM 分支形式、再到可执行 LLVM IR 的端到端 codegen 能力。

## 【技术要点】

- **继续使用 dialect conversion 框架做 FullConversion**：复用 Ch-5 的 4 大组件（ConversionTarget / TypeConverter / RewritePatternSet / `applyFullConversion`），但本轮把除 `toy.print` 之外的全部 `toy` 操作都已先下沉到 `affine/arith/std`，最后一并 lowering 到 `LLVMDialect`。
- **依赖传递性 lowering（transitive lowering）**：不需要直接生成 LLVM dialect op，而是先产生结构化 loop nest（`scf`/`affine`），由 `populateAffineToStdConversionPatterns`、`populateSCFToControlFlowConversionPatterns`、`populateArithToLLVMConversionPatterns`、`populateFuncToLLVMConversionPatterns`、`populateControlFlowToLLVMConversionPatterns` 等多阶段 pattern 链式合法化。
- **`toy.print` lowering 为非 affine 循环 + printf 调用**：通过 `getOrInsertPrintf` 在 module 中按需插入签名 `i32 (i8*, ...)` 的 `printf` 声明，返回 `FlatSymbolRefAttr` 供后续 `LLVM::CallOp` 引用；循环索引按 MemRef 布局 `{ double*, i64, [2 x i64], [2 x i64] }` 算 GEP，循环结束后对每一块 buffer 调用 `@free`。
- **MemRef → LLVM 类型转换使用 `LLVMTypeConverter`**：因涉及 block argument 转换，必须有 TypeConverter；原文 Toy 无自定义类型，因此使用默认转换即可。
- **导出 LLVM IR 与 JIT 执行**：通过 `mlir::translateModuleToLLVMIR(module)` 将纯 LLVM-dialect module 转为 `std::unique_ptr<llvm::Module>`；原文末尾（截断处）暗示后续会经 LLVM 优化 pass 后交给 JIT。

## 【关键机制与数据】

- **ConversionTarget 的最小合法集**：原文显式仅声明 `addLegalDialect<mlir::LLVMDialect>()` + `addLegalOp<mlir::ModuleOp>()`，其余一律非法，配合 FullConversion 强制彻底下沉。
- **Printf 声明的构造路径**：若模块已存在 `printf` 则直接返回 `SymbolRefAttr::get("printf", context)`；否则在 module body 起点 `setInsertionPointToStart` 插入 `LLVMFuncOp`，类型 `LLVMFunctionType::get(i32, i8*, /*isVarArg=*/true)`，参数 `llvmI32Ty = IntegerType::get(ctx, 32)`、`llvmI8PtrTy = LLVMPointerType::get(IntegerType::get(ctx, 8))`。
- **工作样例的形状（原文）**：输入 `toy.constant dense<[[1.0,2.0,3.0],[4.0,5.0,6.0]]> : tensor<2x3xf64>` → `toy.transpose` 到 `tensor<3x2xf64>` → `toy.mul %2, %2` → `toy.print`，所有值类型为 `f64`。
- **Lowering 后 IR 的关键观测**：循环内 `llvm.extractvalue` 取描述符第 0 域得到 `double*`，通过 `llvm.mul %214, 2`（stride=2）与 `llvm.mul %219, 1`（stride=1）计算 GEP 偏移；末尾基本块对每个分配内存调用 `llvm.call @free`，并 `bitcast double* → i8*` 适配 `@free(!llvm<"i8*">)` 签名。
- **导出后 LLVM IR 的关键观测**：printf 格式串经 `getelementptr inbounds ([4 x i8], [4 x i8]* @frmt_spec, i64 0, i64 0)` 取到（原文未给出 `@frmt_spec` 内容，按 `%f64` 推测为 `"%f\0"` 一类 4 字节串）；GEP 公式 `(%96 * 2) + (%100 * 1)` 与 MLIR 端 `llvm.mul ... 2/1` 一一对应；末尾连续 3 次 `extractvalue/bitcast/free` 释放 3 块中间 MemRef。
- **启用 LLVM 优化后的效果（原文片段）**：`tail call i32 (i8*, ...) @printf(i8* nonnull dereferenceable(1) ... double 1.000000e+00)` — 表明经优化后整个 2×3 矩阵常量与 3×2 转置乘法已被常量折叠/死代码消除压扁为直接的若干次 `printf` 调用，原文在展示到第二个 `printf` 实参 `1.000000e+00` 处被截断。

## 【表格解读】

**原文无表格**（文档全程以代码块、IR 片段和散文形式呈现 ConversionTarget/TypeConverter/Patterns 的配置，未提供任何参数表、对比表或配置项表）。

## 【公式解读】

**原文无独立公式块**（LaTeX 或伪代码形式的纯数学公式未出现）。唯一接近"公式"的是 GEP 偏移计算的两段伪算术表达式，列出如下供对照理解：

- 原文 LLVM-dialect 形式（循环体内）：
  ```
  %225 = llvm.add %222, %224   // %224 = llvm.mul %214, %223=2
  %228 = llvm.add %225, %227   // %227 = llvm.mul %219, %226=1
  ```
  符号含义：`%222`=基址偏移 0；`%214`=外层索引；`%223=2`=外层 stride（行号 ×2）；`%219`=内层索引；`%226=1`=内层 stride；最终 `offset = 0 + i_outer*2 + i_inner*1`。

- 原文导出后 LLVM IR 形式：
  ```
  %103 = extractvalue { double*, i64, [2 x i64], [2 x i64] } %8, 0
  %104 = mul i64 %96, 2
  %105 = add i64 0, %104
  %106 = mul i64 %100, 1
  %107 = add i64 %105, %106
  %108 = getelementptr double, double* %103, i64 %107
  ```
  符号含义：`%103`=底层 `double*` 数据指针；`%96`/`%100`=外/内层循环变量；常数 `2`、`1` 分别为两个维度的 stride；`%107` 即 `(i_outer * 2 + i_inner * 1)`，作为 GEP 的 element 索引计算 `*(base + offset)`。

## 【关联】

- **承上（Ch-5.md）**：Ch-5 已用 dialect conversion 将大部分 `toy` op 下沉到 `affine` loop nest；Ch-6 在其产物之上叠加本轮 FullConversion，并复用 Ch-5 的 4 大组件配置范式。
- **框架底座（../../DialectConversion.md）**：ConversionTarget / TypeConverter / RewritePatternSet / `applyFullConversion` 的语义与 `FullConversion` 严格性规则。
- **目标方言（../../Dialects/LLVM.md）**：定义 `llvm.func`、`llvm.call`、`llvm.extractvalue`、`llvm.getelementptr`、`llvm.load`、`llvm.bitcast`、`llvm.br`、`llvm.return`、`llvm.mlir.constant` 等本轮产出的全部 op。
- **概念（../../../getting_started/Glossary.md/#transitive-lowering）**：解释为何可以先生成结构化 SCF/Affine 循环，再由多阶段 pattern 链式合法化到 LLVM；同一概念在 Ch-5 已被引用一次。
- **LLVM IR 目标详解（../../TargetLLVMIR.md）**：Ch-6 文末指引"more in-depth details on lowering to the LLVM dialect"指向此处，承接底层 lowering 行为描述。
- **Pass 管理 / IR 打印（../../PassManagement.md/#ir-printing）**：在文末内部链接列表中被引用，应在后续章节（如 Ch-7 的 Pipeline 讲解）配合 pass manager 与 `-mlir-print-ir-after-all` 等能力使用。
- **下游（Ch-7.md）**：本章节"code generation / getting out of MLIR"环节被截断于优化后 LLVM IR 展示处，明确指向 Ch-7 继续讲 JITEngine 装配与运行模型。

## 【使用方法】

原文涉及的使用方式/配置项：

- **ConversionTarget 配置**：`addLegalDialect<mlir::LLVMDialect>()` + `addLegalOp<mlir::ModuleOp>()`。
- **TypeConverter 配置**：`LLVMTypeConverter typeConverter(&getContext());`（使用默认转换规则，覆盖 MemRef → LLVM 结构体映射以支持 block argument 重写）。
- **Pattern 装配顺序**（在同一个 `RewritePatternSet` 上依次 `populate`）：`populateAffineToStdConversionPatterns` → `populateSCFToControlFlowConversionPatterns` → `populateArithToLLVMConversionPatterns(typeConverter, patterns)` → `populateFuncToLLVMConversionPatterns(typeConverter, patterns)` → `populateControlFlowToLLVMConversionPatterns`，最后 `patterns.add<PrintOpLowering>(&getContext())` 处理 `toy.print`。
- **执行入口**：`mlir::applyFullConversion(module, target, patterns)`，失败则 `signalPassFailure()`。
- **Printf 声明按需插入**：通过 `getOrInsertPrintf(rewriter, module, llvmDialect)` 在 module 顶部插入/复用 `LLVM::LLVMFuncOp("printf", i32(i8*, ...))`。
- **LLVM IR 导出**：`mlir::translateModuleToLLVMIR(module)` 返回 `std::unique_ptr<llvm::Module>`；失败时返回空指针，调用方需自行处理错误。
- **可选 LLVM 优化**：原文示例在导出 LLVM IR 后启用 LLVM 优化（具体命令行/Pass 配置未在截断片段中给出），可将常量折叠 + 死代码消除后的精简 main 体作为示例。
- **JIT 执行**：原文在 "CodeGen: Getting Out of MLIR" 标题下预告"export to LLVM IR and setup a JIT to run it"，但具体 JITEngine 构造、`mlir::ExecutionEngine` API 与 `lookup` 调用示例因原文截断未给出，应在 Ch-7 查阅。
