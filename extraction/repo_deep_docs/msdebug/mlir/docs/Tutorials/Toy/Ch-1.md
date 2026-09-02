# Chapter 1: Toy Language and AST

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/Toy/Ch-1.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/Toy/Ch-1.md

# mlir/docs/Tutorials/Toy/Ch-1.md 深度解读

## 【定位】
本文是 MLIR Toy 编译器教程的第一章，定义了一个名为 "Toy" 的玩具张量语言并展示其源代码到 AST 的表示，作为后续将 AST 转换为 MLIR IR（Ch-2）的前置铺垫。

---

## 【技术要点】

1. **语言基本性质**：Toy 是基于张量（tensor-based）的语言，codegen 限制为 **rank ≤ 2** 的张量；唯一数据类型为 **64-bit 浮点（double）**，所有值隐式双精度。

2. **值语义**：所有 `Values` 不可变（immutable），每个操作返回一个新分配的值，释放由系统自动管理。

3. **类型系统**：通过 **类型推断（type inference）** 进行静态类型检查；仅在需要指定张量形状时才要求类型声明（如 `var b<2, 3>`），否则可省略（如 `var a` / `var c`）。

4. **函数泛型与特化**：函数参数是 unranked 的（即只知是张量、不知维度）；在每个调用点根据实际参数签名进行 **特化（specialize）**，并推断出返回类型；不同签名的调用会触发新的特化版本。

5. **形状推断失败示例**：`multiply_transpose(a, c)`（`<2,3>` 与 `<3,2>` 不兼容）会触发 shape inference error。

6. **仅有的两个内置函数**：`transpose()` 与 `print()`；其他均为用户自定义。支持 element-wise 乘法 (`*`)。

---

## 【关键机制与数据】

### 隐式 reshape 机制
原文：定义新变量是 reshape 张量的方式，元素数量必须匹配。示例中 `var a = [[1, 2, 3], [4, 5, 6]]`（2×3）与 `var b<2, 3> = [1, 2, 3, 4, 5, 6]`（6 元素一维字面量）元素数同为 6，可隐式 reshape。

### 泛型函数按调用签名特化的数据流（原文示例）：
- 调用 1：`multiply_transpose(a, b)` → `<2,3>` + `<2,3>` → 返回 `<3,2>`，存于 `c`
- 调用 2：`multiply_transpose(b, a)` → `<2,3>` + `<2,3>` → 复用上一次的特化版本，返回 `<3,2>`，存于 `d`
- 调用 3：`multiply_transpose(c, d)` → `<3,2>` + `<3,2>` → 触发新特化，返回 `<2,3>`，存于 `e`
- 调用 4：`multiply_transpose(a, c)` → `<2,3>` + `<3,2>` → 触发 shape inference error

### AST 结构层次
原文：AST dump 显示节点层级为 `Module → Function { Proto, Params, Block { Return / VarDecl { Literal | Call | BinOp } } }`。每个 AST 节点携带完整源位置（`file:line:column`），例如：
- `Function Proto 'multiply_transpose' @test/Examples/Toy/Ch1/ast.toy:4:1`
- `Literal: <2, 3>[ <3>[ 1.000000e+00, 2.000000e+00, 3.000000e+00], <3>[ 4.000000e+00, 5.000000e+00, 6.000000e+00]]`

### 字面量浮点格式
原文：AST 中字面量统一以科学计数法表示，例如 `1.000000e+00`、`2.000000e+00` 等，符合双精度浮点格式。

---

## 【表格解读】

**原文无表格**（原文仅以代码块、AST dump 文本与散文描述呈现，无 markdown/HTML 表格）。

---

## 【公式解读】

**原文无公式**（未出现任何 LaTeX 数学式或伪代码算法式；张量形状仅以 `<m, n>` 形式作为类型标注语法呈现）。

---

## 【关联】

### 与 Ch-2 的衔接
原文最末段：*"The [next chapter](Ch-2.md) will demonstrate how to convert this AST into MLIR."* 即本文建立的 Toy AST 是 Ch-2 中 MLIR Dialect 转换的输入源。

### 与 LLVM Kaleidoscope 教程的类比
原文：*"If you are not familiar with such a Lexer/Parser, these are very similar to the LLVM Kaleidoscope equivalent that are detailed in the first two chapters of the Kaleidoscope Tutorial"* — Toy 的 Lexer/Parser 设计与 LLVM 经典 Kaleidoscope 教程（LangImpl02）前两章实现方式相似，可作为前置阅读。

### 模块/文件上下游
- Lexer 实现：`examples/toy/Ch1/include/toy/Lexer.h`（**单头文件**实现）
- Parser 实现：`examples/toy/Ch1/include/toy/Parser.h`（**递归下降 parser**）
- 可执行入口：`path/to/BUILD/bin/toyc-ch1`
- 测试用例：`test/Examples/Toy/Ch1/ast.toy`
- 完整示例目录：`examples/toy/Ch1/`

### AST 节点类型（构成 IR 节点的"字典"）
Module / Function / Proto / Params / Block / Return / VarDecl / Literal / Call / BinOp（其中 BinOp 为二元运算符节点，原文中仅出现 `*`）。

---

## 【使用方法】

原文给出的复现命令：
```bash
path/to/BUILD/bin/toyc-ch1 test/Examples/Toy/Ch1/ast.toy -emit=ast
```
- `-emit=ast`：指定输出 AST dump（文本形式即文中所示结构）。

源码位置指引：
- Lexer：`examples/toy/Ch1/include/toy/Lexer.h`
- Parser：`examples/toy/Ch1/include/toy/Parser.h`（递归下降实现）
- 示例 toy 源：`test/Examples/Toy/Ch1/ast.toy`
- 工程目录：`examples/toy/Ch1/`

语言特性启用/限制（原文有提及）：
- 张量 rank 限制 ≤ 2（codegen 层面限制）
- 类型声明仅在需要指定形状时强制要求（如 `var b<2, 3>`），其余可省略
- 函数参数始终 unranked，由调用点特化
- 内置仅 `transpose` 与 `print`
