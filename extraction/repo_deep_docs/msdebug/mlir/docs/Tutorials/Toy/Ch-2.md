# Chapter 2: Emitting Basic MLIR

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/Toy/Ch-2.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/Toy/Ch-2.md

# 深度解读: MLIR Toy 教程 Chapter 2 — Emitting Basic MLIR

---

## 【定位】

本文档是 MLIR Toy 教程系列的第二章, 解决"如何将 Toy 语言的 AST 发射 (emit) 为 MLIR 文本形式"这一入门问题, 同时系统介绍 MLIR 的核心抽象 (Operation / Attribute / Type / Dialect / Location) 与 Toy Dialect 的 C++ 及 TableGen 两种定义方式, 为后续章节注册算子、接入 Verifier、构建 Pass 打基础。

---

## 【技术要点】

1. **MLIR 的扩展性设计原则** — 原文: "there are few pre-defined instructions (*operations* in MLIR terminology) or types", MLIR 旨在通过 Dialect 机制避免每个前端重复实现分析与变换基础设施。

2. **Operation 的七要素 (general form)** — 原文逐字列举:
   - 一个 operation 名称 (例如 `"toy.transpose"`)
   - 一组 SSA 操作数 (operands)
   - 一组 [attributes](../../LangRef.md/#attributes) (常量元数据)
   - 一组 [types](../../LangRef.md/#type-system) (结果类型)
   - 一个 [source location](../../Diagnostics.md/#source-locations) (调试用)
   - 一组后继 [blocks](../../LangRef.md/#blocks) (主要用于分支)
   - 一组 [regions](../../LangRef.md/#regions) (用于函数等结构化操作)

3. **Toy transpose 操作示例** — 原文给出完整 MLIR 文本形式:
   ```
   %t_tensor = "toy.transpose"(%tensor) {inplace = true} : (tensor<2x3xf64>) -> tensor<3x2xf64> loc("example/file/path":12:1)
   ```
   其中: `%t_tensor` 是带 sigil 前缀的结果名; `{inplace = true}` 是布尔属性; `loc(...)` 是源码位置 (`file:line:col` 三段式 `12:1` 即第 12 行第 1 列)。

4. **强制 source location** — 原文: "every operation has a mandatory source location associated with it. Contrary to LLVM, where debug info locations are metadata and can be dropped, in MLIR, the location is a core requirement, and APIs depend on and manipulate it." 即 Location 是 Operation 的一等成员, 删除必须显式选择。

5. **Opaque API / 未注册算子的回环 (round-trip)** — 原文: 任何 Operation/Attribute/Type 即使所属 Dialect 未注册, MLIR 仍能解析、表示并 [round-trip](../../../getting_started/Glossary.md/#round-trip); 此时 MLIR 仅强制结构性约束 (如 dominance), 不做类型/算子语义验证。原文给出可"骗过" verifier 的 invalid IR:
   ```
   func.func @main() {
     %0 = "toy.print"() : () -> tensor<2x3xf64>
   }
   ```

6. **ToyDialect 两种实现** —
   - **C++ 命令式**: 继承 `mlir::Dialect`, 显式实现 `initialize()` 并通过 `static llvm::StringRef getDialectNamespace() { return "toy"; }` 提供命名空间。
   - **TableGen 声明式 (ODS)**: 通过 `def Toy_Dialect : Dialect { let name = "toy"; let summary = "..."; let description = [{...}]; }` 定义, 自动生成文档与样板代码。

7. **mlir-opt 调试输出开关** — 原文: "the `-mlir-print-debuginfo` flag specifies to include locations"; mlir-opt 默认不在输出中包含 location 信息。

---

## 【关键机制与数据】

- **Operation = SSA 核心单元**: 原文把 Operation 比作 LLVM instructions, 但强调 Operation 能表达 LLVM IR 的全部核心结构 (instructions、globals/functions、modules 等), 而非仅底层 RISC 类指令。

- **Dialect 命名空间机制**: 原文: "Dialects provide a grouping mechanism for abstraction under a unique `namespace`", 算子名采用 `"<namespace>.<opname>"` 双段式 (例如 `toy.transpose`、`toy.print`) 以避免冲突。

- **Round-trip 工作流**: 原文描述将 Toy 操作写进 `.mlir` 文件 → 经 mlir-opt → 输出等价 IR, 整个过程无需注册 Toy Dialect; 但代价是 "Unregistered operations must be treated conservatively by transformations and analyses, and they are much harder to construct and manipulate."

- **属性 (Attribute) 与操作数 (Operand) 区分**: 原文: "A dictionary of zero or more attributes, which are special operands that are always constant." 即 Attribute 是常量形式的特殊操作数。

- **结果名的非持久性**: 原文: "The name is used during parsing but is not persistent (e.g., it is not tracked in the in-memory representation of the SSA value)." 即 `%t_tensor` 仅文本解析时使用, 内存表示中 SSA value 不记录该名。

- **位置替换的强制性**: 原文: "If a transformation replaces an operation by another, that new operation must still have a location attached." 这条规则保证变换不会"无意"丢失来源信息。

(原文未提供具体性能数字或基准数据)

---

## 【表格解读】

**原文无表格。** 文中 Operation 的结构以带项目符号的列表 + 一段 MLIR 示例代码呈现, 未使用任何 markdown/data 表格。

---

## 【公式解读】

**原文无公式。** 文中示例均为 MLIR 文本片段 (例如 `%t_tensor = "toy.transpose"(%tensor) {inplace = true} : (tensor<2x3xf64>) -> tensor<3x2xf64> loc(...)`) 及 C++ / TableGen 代码块, 不含 LaTeX 数学公式或伪代码公式。

---

## 【关联】

本文处于 Toy 教程的承上启下位置, 与以下上下游模块/章节通过文末链接形成关系网:

| 内部链接 | 关系定位 |
|---|---|
| [../../LangRef.md](../../LangRef.md) | 总入口: MLIR 语言参考手册, 是 Operation/Dialect/Attribute/Type 等概念的权威定义来源 |
| [../../LangRef.md/#dialects](../../LangRef.md/#dialects) | 上游定义: Dialect 的形式化语义, 本文 ToyDialect 即据此设计 `namespace = "toy"` |
| [../../LangRef.md/#operations](../../LangRef.md/#operations) | 上游定义: Operation 的完整语法/语义, 本文示例 MLIR 操作均遵循其规范 |
| [../../LangRef.md/#identifiers-and-keywords](../../LangRef.md/#identifiers-and-keywords) | 上游定义: 解释 `%t_tensor` 等 SSA 值的 sigil 前缀规则 |
| [../../LangRef.md/#attributes](../../LangRef.md/#attributes) | 上游定义: Attribute (例如 `{inplace = true}`) 的常量元数据机制 |
| [../../LangRef.md/#type-system](../../LangRef.md/#type-system) | 上游定义: `tensor<2x3xf64>` 等张量类型的语法与语义 |
| [../../Diagnostics.md/#source-locations](../../Diagnostics.md/#source-locations) | 横向关联: Location 是 Operation 强制成员, 由 Diagnostics 文档体系定义 |
| [../../LangRef.md/#blocks](../../LangRef.md/#blocks) | 上游定义: Operation 的 successor blocks 概念 (本文 Toy 暂未使用, 为后续控制流章节铺垫) |
| [../../LangRef.md/#regions](../../LangRef.md/#regions) | 上游定义: Operation 的 regions 概念 (为后续函数体结构化操作铺垫) |
| [../../../getting_started/Glossary.md/#round-trip](../../../getting_started/Glossary.md/#round-trip) | 横向关联: "Round-trip" 术语定义, 是 Opaque API 一节验证机制的基础 |

文档末尾 (原文被截断于 `let description = [{` 之后) 暗示后续将进入"注册 Toy Dialect 与算子"的章节, 本章为其做概念铺垫。

---

## 【使用方法】

1. **查看带 Location 的 MLIR 输出**
   ```bash
   mlir-opt --help           # 查看所有可用选项
   mlir-opt -mlir-print-debuginfo input.mlir   # 在输出中包含 loc(...) 位置信息
   ```
   原文: "the `-mlir-print-debuginfo` flag specifies to include locations".

2. **未注册 Dialect 的 round-trip 验证** — 原文示例: 将含 `"toy.transpose"`、`"toy.print"` 等未注册算子的 `.mlir` 文件直接喂给 `mlir-opt`, 即使算子语义错误, IR 仍可"骗过" verifier 完成回环; 仅在注册 Dialect 与算子后, verifier 才会捕获真正的语义违规。

3. **C++ 方式注册 Toy Dialect** — 原文给出类骨架: 继承 `mlir::Dialect`, 在 `initialize()` 中调用各算子/属性/类型的 `addOperations<>()`/`addAttributes<>()`/`addTypes<>()`。

4. **TableGen 声明式注册 Toy Dialect** — 原文给出 ODS 写法:
   ```tablegen
   def Toy_Dialect : Dialect {
     let name = "toy";
     let summary = "A high-level dialect for analyzing and optimizing the Toy language";
     let description = [{ ... }];
   }
   ```
   此方式 (原文: "Using the declarative specification is much cleaner as it removes the need for a large portion of the boilerplate") 适合大规模 Dialect, 并自动生成文档。

5. **Toy transpose 的 MLIR 文本发射** — 从 Toy AST 节点 `TransposeOp` 生成原文示例 MLIR 字符串, 这是本章要解决的核心问题; 后续章节将进一步处理 AST 各节点 (PrintOp、ConstantOp、GenericOp 等) 的发射。

(原文未涉及具体的 CMake 构建命令、编译开关或 Pass pipeline 配置; 这些将在后续章节展开。)
