# Quickstart tutorial to adding MLIR graph rewrite

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/QuickstartRewrites.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/QuickstartRewrites.md

# 「Quickstart tutorial to adding MLIR graph rewrite」一体化深度解读

---

## 【定位】

这篇文档是 MLIR 中**图重写(graph rewrite)机制的快速入门教程**,目标读者是初次为 MLIR 添加自定义转换/优化的开发者。它完整地走通了一条最小路径:在 TableGen 里定义一个 Operation(以 TensorFlow Lite 的 `LeakyRelu` 为示例)→ 用多种方式表达源 DAG 到目标 DAG 的重写 → 把生成代码接入到 pass 体系中使用。文中明确指出:patterns + rewrite engine 是**首选方式**,graph walker 仅为演示。

---

## 【技术要点】

1. **Operation 的 TableGen 定义结构**:一个 op 定义包含六部分 —— 操作名(含 dialect 前缀,如 `tfl.add`)、Traits(如 `NoMemoryEffect`、`SameValueType`)、Arguments(`(ins ...)` 内是 operand 和 attribute)、Results(`(outs ...)` 内可命名)、文档(`summary` + `description`)、Dialect 特有信息(如示例中 `let hasOptions = 1;`,仅供 flatbuffer 翻译时使用)。

2. **Operation 的可选 C++ 扩展点**:Operation 可自定义 parser、printer、builder、verifier、constant folder、canonicalizer。一旦声明某个 hook,就需要提供对应的 C++ 实现,例如声明 folder 后必须写出 `OpFoldResult SpecificOp::fold(ArrayRef<Attribute> constOperands)`。

3. **三种重写表达方式**(从轻到重):
   - **TableGen `Pat`**:用 `def : Pat<(src_op args), (dst_op args)>` 做 1:1 的 DAG-to-DAG 重写,简单同构映射可直接书写。
   - **TableGen `Pat` + NativeCodeCall 兜底**:对 framework 不能表达的目标,声明 `NativeCodeCall<"createTFLLeakyRelu(...)">` 调用 C++ 函数,可实现任意复杂 builder;**但 input pattern 端无法跨 operand/attribute 表达约束**。
   - **C++ `matchAndRewrite` 函数式**:对简单重写(如乘 2 的幂→左移)直接写函数,用 `PatternRewriter &rewriter` 重写并 `replaceOpWithNewOp<...>`。

4. **ODS 自带的函数式规范化接口**:在 op 定义里加 `let hasCanonicalizeMethod = 1;`,在 `.cpp` 里实现 `LogicalResult MyOp::canonicalize(MyOp op, PatternRewriter &rewriter)`。需要完整通用规范化时,改用任意 `RewritePattern` 列表。

5. **TableGen 文件的编译期接入**:CMake 中三行配置 —— `set(LLVM_TARGET_DEFINITIONS <td 文件>)`、`mlir_tablegen(<输出 inc 文件> -gen-rewriters)`、`add_public_tablegen_target(<cmake target>)`。生成的 C++ 文件对外暴露 `populateWithGenerated(RewritePatternSet &patterns)` 函数,把它放进任意 pass 的 pattern 集合即可。

6. **Trait vs. `let` 写法的等价性**:原 inputs 由 trait 推断,result 类型在 `let arguments = ...` 里显式声明;两种写法可以混用且可互换。

---

## 【关键机制与数据】

**工作原理与数据流(原文级解读):**

- **Op 定义 → 代码生成**:原文:"TableGen is a modeling tool to specify the ops and the C++ code to interact with these operations are generated from." —— 也就是说,TableGen 文件不是直接被运行时使用,而是在编译期被 `mlir-tblgen` 扫描并产出 C++ 类/方法。
- **Pattern 生成与注册**:原文:"The file containing the patterns need to be processed using `mlir-tblgen -gen-rewriters` during compilation time." → 生成 `populateWithGenerated(RewritePatternSet &patterns)`,由使用方在自己的 pass 里调用以"装填"patterns。
- **Pattern 的捕获语义**:原文:"The arguments in the source pattern is captured and can be used in the result pattern." 即源 DAG 中的形参(`$arg`、`$a`)会绑定到实参,可按位置或名字在目标 DAG 中复用。
- **常量折叠的失败语义**:原文示例 `return {};` 表示折叠不可行,这是 OpFoldResult 的"无结果"约定。
- **常量模式匹配 API**:原文示例使用 `matchPattern(inputs.back(), m_RConstant(value))` 配合 `value.isPowerOf2()`,完成"mul(x, c) where c=2^k"模式识别,进而 `value.exactLogBase2()` 取得指数。

**性能/定量数据**:原文**未给出**任何 benchmark、吞吐数字、加速比等性能数据(原文:"原文:无定量性能数据")。

---

## 【表格解读】

**原文无表格**。原文中所有参数、配置项、API 均以 TableGen 语法、C++ 代码块或散文形式表达,未出现 `<table>`/Markdown 表格结构。

可视为"伪表格"的 TableGen 关键定义(便于核对,内容逐字摘自原文):

| 字段 | 原文中对应的字面定义 | 说明 |
|---|---|---|
| Op 类名 | `TFL_LeakyReluOp` | TableGen def 名 |
| 基类模板 | `TFL_Op<TFL_Dialect, "leaky_relu", ...>` | 注入 dialect 前缀 `tfl.` |
| Traits | `[NoMemoryEffect, SameValueType]` | 无副作用 + 操作数与结果同类型 |
| Results | `(outs Tensor)` | 单结果 Tensor |
| Operand | `F32Tensor:$x` | 命名 operand `x` |
| Attribute | `F32Attr:$alpha` | 命名 attribute `alpha` |
| Summary | `"Leaky ReLU operator"` | 一行摘要 |
| Description | `[{ Element-wise Leaky ReLU operator x -> x >= 0 ? x : (alpha * x) }]` | 行为描述 |
| Dialect 私有 | `let hasOptions = 1;` | 仅用于 flatbuffer 输出生成 |

---

## 【公式解读】

原文中的"公式"均为**伪代码/语义表达式**,无 LaTeX 数学式。逐字保留并解释:

### 公式 1:Leaky ReLU 行为定义

```text
x -> x >= 0 ? x : (alpha * x)
```

- `x`: 输入张量/标量(逐元素)。
- `alpha`: 编译期常量属性,负区间的斜率。
- 语义:对每个元素,若 `x >= 0` 则输出 `x`,否则输出 `alpha * x`。

### 公式 2:Mul→Shl 规范化规则(CIRCT 示例)

```text
mul(x, c) -> shl(x, log2(c)), where c is a power of two
```

- `mul(x, c)`:两个操作数的乘法 op。
- `c`:必须为 2 的幂(由 `value.isPowerOf2()` 保证)。
- `shl`:左移 op。
- `log2(c)`:即 `value.exactLogBase2()`,把常量 c 转换为移位位数。
- 作用:把"乘以 2 的幂"这种运行时乘指令降级为位运算,在硬件后端通常更便宜。

### 公式 3:OpFoldResult 失败约定

```text
return {};     // 表示 fold 失败
```

- `{}`:空 `OpFoldResult`,表示当前 op 在此情形下无法被常量折叠,应继续由其他规则/canonicalize 处理。

---

## 【关联】

文档虽短,但把 MLIR 重写生态的几个关键模块串成一条链,与文末/文中给出的内部链接对应关系如下:

| 链接目标 | 与本文的关系 |
|---|---|
| [`../LangRef.md`](../LangRef.md) | 上游基础:本文所有 op、attribute、trait 概念都假定读者已熟悉 MLIR IR 结构与 operation 语义。文档开头即指向它做背景阅读。 |
| [`../DefiningDialects/Operations.md`](../DefiningDialects/Operations.md) | **本文的"权威参考"**:文章里的 TableGen op 定义(`def TFL_LeakyReluOp: TFL_Op<...>`)、`(ins/outs)` 语法、`let summary/description/hasOptions` 等字段的完整规范都在该文档中。 |
| [`../DeclarativeRewrites.md`](../DeclarativeRewrites.md) | **本文的"重写机制详解"**:`Pat`、`NativeCodeCall`、多 op 源模式、约束表达能力的边界都来自该文档;本文只给出 quickstart 示例。 |
| [`../PassManagement.md`](../PassManagement.md) | 下游使用:本文生成的 `populateWithGenerated(RewritePatternSet &)` 最终要被某个 pass 调用以驱动重写;pass 的注册、管理、与 `mlir-opt` 集成的细节在该文档中。 |

**模块上下游串联**:LangRef(IR 语义) → DefiningDialects/Operations(op 定义) → DeclarativeRewrites(规则定义) → 本文(把上面三者串成最小工作流) → PassManagement(把生成的 patterns 装载进 pass 运行)。Graph walker 部分在本文只作演示,实际生产代码不推荐使用。

---

## 【使用方法】

**启用方式与配置项(原文逐条):**

### A. 让 `mlir-tblgen` 处理 patterns 文件

在 CMakeLists.txt 中加入(原文逐字):

```cmake
set(LLVM_TARGET_DEFINITIONS <name-of-the-td-file>)
mlir_tablegen(<name-of-the-generated-inc-file> -gen-rewriters)
add_public_tablegen_target(<name-of-the-cmake-target>)
```

- `<name-of-the-td-file>`:包含 `def : Pat<...>` 的 TableGen 文件。
- `<name-of-the-generated-inc-file>`:由 `mlir-tblgen -gen-rewriters` 生成的 `.inc` / `.h` 文件名。
- `<name-of-the-cmake-target>`:公共 tablegen 目标名,**使用方 library 必须 link 到这个 target**,否则 `#include` 找不到生成文件。

### B. 在 pass 中装载生成的 patterns

原文 API:`populateWithGenerated(RewritePatternSet &patterns)` —— 把生成的规则集合并进传入的 `RewritePatternSet`,再交给目标 pass。

### C. 给 op 启用函数式 canonicalize

在 op 的 TableGen 定义里加:

```tablegen
let hasCanonicalizeMethod = 1;
```

然后在对应 `.cpp` 里实现:

```c++
LogicalResult MyOp::canonicalize(MyOp op, PatternRewriter &rewriter) { ... }
```

### D. C++ `RewritePattern` 全量方式

若 `matchAndRewrite` 风格仍不够,文档开头即提示"可以指定任意 `RewritePattern` 列表"(原文:"you can specify an arbitrary list of `RewritePattern`s"),具体骨架在文档尾部但被截断(原文档以 `---` 结束,未给出完整示例代码,故**更细的命令/参数需参照 `../DeclarativeRewrites.md` 与 `../PassManagement.md`**)。

### E. 命令行工具

- `mlir-tblgen -gen-rewriters`:编译期驱动,无运行时 CLI 参数。
- 运行时由 `mlir-opt` 等 driver 加载使用这些 patterns 的 pass;原文未涉及具体 `mlir-opt` 调用命令。
