# Chapter 3: High-level Language-Specific Analysis and Transformation

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/Toy/Ch-3.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/Toy/Ch-3.md

# mlir/docs/Tutorials/Toy/Ch-3.md 深度解读

## 【定位】

本篇文档是 MLIR Toy Dialect 教程的第三章,描述如何在 MLIR 中利用 Toy Dialect 的高层语义信息,通过**本地模式匹配与重写**(local pattern-match transformations)实现 LLVM 难以完成的优化(如冗余 `transpose`/冗余 `reshape` 的消除),涵盖**命令式 C++ 风格**与**声明式 DRR 风格**两种实现路径。

---

## 【技术要点】

1. **变换分类**: 编译器变换被划分为**局部 (local)** 与**全局 (global)** 两类;本章聚焦于前者,使用 MLIR 的 [Generic DAG Rewriter](../../PatternRewriter.md)。
2. **两种模式匹配实现方法**:
   - **Imperative**: C++ 中手写 `OpRewritePattern` 子类,匹配并重写 IR 树状模式。
   - **Declarative (DRR)**: 基于 [Declarative Rewrite Rules](../../DeclarativeRewrites.md),表驱动式规则定义;**前提是操作必须用 ODS 定义**(参见 [Ch-2](Ch-2.md))。
3. **C++ 风格模式**: `SimplifyRedundantTranspose : mlir::OpRewritePattern<TransposeOp>`,在构造时指定 `benefit=1`,实现 `transpose(transpose(x)) -> x`,通过 `rewriter.replaceOp(op, {transposeInputOp.getOperand()})` 完成重写,代码位于 `ToyCombine.cpp`。
4. **接入 Canonicalization**: 在 ODS 中设置 `hasCanonicalizer = 1`,并在 `TransposeOp::getCanonicalizationPatterns` 中 `results.add<SimplifyRedundantTranspose>(context)`,再在 `toyc.cpp` 通过 `PassManager` 添加 `mlir::createCanonicalizerPass()`。
5. **`Pure` trait 关键作用**: MLIR 默认假定操作可能有副作用,因此不会自动 DCE;为 `TransposeOp` 添加 `[Pure]` trait 后,Canonicalizer 才能将模式重写后留下的死 `transpose` 真正消除。
6. **DRR 三大原语**: `Pat<...>`(模式匹配 + 重写)、`Constraint<CPred<...>>`(参数条件约束)、`NativeCodeCall<"...">`(C++ 内联或辅助函数调用);生成的 C++ 位于 `tools/mlir/examples/toy/Ch3/ToyCombine.inc`。

---

## 【关键机制与数据】

### 工作原理(C++ 风格,以 transpose 为例)

- **原文**: 匹配阶段通过 `op.getOperand()` 取出当前 `TransposeOp` 的输入,再用 `transposeInput.getDefiningOp<TransposeOp>()` 判断输入是否由另一个 `TransposeOp` 定义;若否则 `return failure()`。
- **原文**: 命中后调用 `rewriter.replaceOp(op, {transposeInputOp.getOperand()})`,把外层 transpose 替换为内层 transpose 的输入。
- **原文**: 重写后留下的死 transpose 因 `TransposeOp` 无 `Pure` trait 而不会被 DCE;补充 `def TransposeOp : Toy_Op<"transpose", [Pure]>`(TableGen 片段)后再次运行,最终 IR 仅剩 `toy.return %arg0`。

### 数据流(DRR 风格,以 reshape 为例)

- **原文**: `ReshapeReshapeOptPattern` 将 `Reshape(Reshape(x))` 折叠为 `Reshape(x)`。
- **原文**: `RedundantReshapeOptPattern` 通过 `TypesAreIdentical : Constraint<CPred<"$0.getType() == $1.getType()">>` 约束,仅当输入输出类型相同时将 `ReshapeOp` 替换为其输入值 `($arg)`。
- **原文**: `FoldConstantReshapeOptPattern` 通过 `ReshapeConstant : NativeCodeCall<"$0.reshape(($1.getType()).cast<ShapedType>())">` 把对常量的 reshape 折叠进常量本身,生成新的 `ConstantOp`。

### 性能/对比数据

- **原文**: 文档未给出性能数字。但给出一个 C++ 对照示例:`double_transpose(int A[N][M])` 在 Clang 下"can't optimize away the temporary array",需要用 `#define N 100, M 100` 的二维循环 + 中间数组 `B[M][N]` 才能表达,作为 Toy IR 上做该优化的动机。

---

## 【表格解读】

原文 TableGen 片段逐字还原:

### 表 1 — `Pattern` 模板签名

| 字段 | 原文 |
|---|---|
| `class Pattern` 定义 | `class Pattern<dag sourcePattern, list<dag> resultPatterns, list<dag> additionalConstraints = [], dag benefitsAdded = (addBenefit 0)>;` |

**逐行解读**:
- `dag sourcePattern`: 待匹配的操作 DAG 模式。
- `list<dag> resultPatterns`: 匹配成功后要生成的新操作 DAG 列表。
- `list<dag> additionalConstraints = []`: 可选的额外约束(如类型、属性条件),默认空。
- `dag benefitsAdded = (addBenefit 0)`: 该 pattern 在 greedy 应用时的优先级收益,默认 `addBenefit 0`。

### 表 2 — DRR 规则一览

| 规则名 | 原文 |
|---|---|
| `ReshapeReshapeOptPattern` | `def ReshapeReshapeOptPattern : Pat<(ReshapeOp(ReshapeOp $arg)), (ReshapeOp $arg)>;` |
| `TypesAreIdentical` | `def TypesAreIdentical : Constraint<CPred<"$0.getType() == $1.getType()">>;` |
| `RedundantReshapeOptPattern` | `def RedundantReshapeOptPattern : Pat<(ReshapeOp:$res $arg), (replaceWithValue $arg), [(TypesAreIdentical $res, $arg)]>;` |
| `ReshapeConstant` | `def ReshapeConstant : NativeCodeCall<"$0.reshape(($1.getType()).cast<ShapedType>())">;` |
| `FoldConstantReshapeOptPattern` | `def FoldConstantReshapeOptPattern : Pat<(ReshapeOp:$res (ConstantOp $arg)), (ConstantOp (ReshapeConstant $arg, $res))>;` |

**逐行解读**:
- `ReshapeReshapeOptPattern`: 匹配 `Reshape(Reshape($arg))`,重写为 `Reshape($arg)`,消除一层冗余 reshape。
- `TypesAreIdentical`: 约束谓词,要求 `$0.getType() == $1.getType()`,即两个 Value 的类型完全相同。
- `RedundantReshapeOptPattern`: 用 `:$res` 给外层 `ReshapeOp` 命名以便约束;`replaceWithValue $arg` 表示把整条 op 替换为其输入值;约束要求 `$res` 与 `$arg` 类型相同。
- `ReshapeConstant`: 调用 C++ 辅助,把 `$0` reshape 成 `$1` 所标注的目标 `ShapedType`,在模式内部直接求值。
- `FoldConstantReshapeOptPattern`: 匹配 `Reshape(Constant($arg))`,重写为先 reshape 常量、再用 `ConstantOp` 包起来;`$res` 提供目标 shape。

### 表 3 — TransposeOp 增强

| 原文 |
|---|
| `def TransposeOp : Toy_Op<"transpose", [Pure]>{...}` |

**解读**: 在 ODS 中给 `TransposeOp` 加上 `Pure` trait,告诉 MLIR 该 op 无副作用,以便 Canonicalizer 进行 DCE。

---

## 【公式解读】

### 公式 1 — 转置消除等价式

$$ \text{transpose}(\text{transpose}(X)) \to X $$

**符号含义**:
- `transpose`: Toy Dialect 的转置操作 `toy.transpose`。
- $X$: 被转置的张量输入(类型为 `tensor<*xf64>`)。
- 等式左侧:对 $X$ 做两次连续转置;右侧:直接返回 $X$。

### 公式 2 — DRR 模式:Reshape 折叠(Reshape(Reshape))

$$ \text{Reshape}(\text{Reshape}(x)) = \text{Reshape}(x) $$

**符号含义**:
- $x$: 内层 `ReshapeOp` 的输入 Value。
- 两侧都是 `ReshapeOp`,但左侧多了内层一次 reshape,可被简化为一次 reshape。

### 公式 3 — DRR 模式:同类型 Reshape 冗余消除

$$ \text{Reshape}(x) \;\xrightarrow{\;\text{type}(x_{\text{res}}) = \text{type}(x_{\text{arg}})\;}\; x_{\text{arg}} $$

**符号含义**:
- $x_{\text{res}}$: 命名后的外层 `ReshapeOp` 的结果。
- $x_{\text{arg}}$: 外层 `ReshapeOp` 的输入 Value。
- 当二者类型完全相同时,Reshape 是 no-op,直接用输入值替换。

### 公式 4 — DRR 模式:常量 Reshape 内联

$$ \text{Reshape}\big(\text{Constant}(c)\big) \;=\; \text{Constant}\big(\text{reshape}(c,\, \text{type}(x_{\text{res}}))\big) $$

**符号含义**:
- $c$: 常量操作的 Value(`$arg`)。
- $x_{\text{res}}$: 外层 `ReshapeOp` 的结果,提供目标 shape(通过 `($1.getType()).cast<ShapedType>()`)。
- `reshape(...)`: 通过 `NativeCodeCall` 调用的 C++ 助手,生成形状为 `type($res)` 的新常量,再包回 `ConstantOp`,消除 `ReshapeOp`。

### 公式 5 — DRR `Pattern` 模板签名(伪代码)

$$ \text{Pattern}(\text{sourcePattern},\; \text{resultPatterns},\; \text{additionalConstraints}=[],\; \text{benefitsAdded}=(\text{addBenefit } 0)) $$

**符号含义**:
- `sourcePattern`: 待匹配的 DAG。
- `resultPatterns`: 生成序列。
- `additionalConstraints`: 谓词/约束。
- `benefitsAdded`: 用于 greedy 排序的收益值。

---

## 【关联】

依据文末内部链接梳理上下游与横向依赖:

- **[PatternRewriter.md](../../PatternRewriter.md)** — 本章 C++ 风格所用的 Generic DAG Rewriter 的总览文档;`mlir::PatternRewriter`、`OpRewritePattern` 等 API 来源。
- **[DeclarativeRewrites.md](../../DeclarativeRewrites.md)** — 本章 DRR 风格所用的声明式重写规则的权威参考;`Pat`、`Constraint`、`NativeCodeCall` 的完整语义。
- **[Ch-2.md](Ch-2.md)** — Toy 操作必须以 ODS 定义,DRR 才能使用;本章依赖 Ch-2 的 ODS 基础。
- **[Canonicalization.md](../../Canonicalization.md)** — 介绍 MLIR 的 Canonicalization Pass 如何以 greedy、iterative 方式应用注册的 `RewritePattern`;本章 C++ 风格的 pattern 正是挂入该 Pass。
- **[DefiningDialects/Operations.md/#hascanonicalizer](../../DefiningDialects/Operations.md/#hascanonicalizer)** — ODS 中为操作启用 `hasCanonicalizer = 1` 的开关,让 Canonicalizer 框架发现该 op 的 `getCanonicalizationPatterns`。
- **[DeclarativeRewrites.md](../../DeclarativeRewrites.md)** — 第二次出现,作为"Further details on the declarative rewrite method can be found at Table-driven Dec…"的引导(原文末尾链接被截断)。
- **[Ch-4.md](Ch-4.md)** — 下一篇章节,文档末尾通过"In the next section, we use DRR…"过渡(实际上 Ch-4 应是后续 Toy 教程章节,原文链接在末尾行被截断)。

---

## 【使用方法】

### 编译与运行命令(原文有)

```bash
# transpose 优化(初次运行,会留下一个死 transpose)
toyc-ch3 test/Examples/Toy/Ch3/transpose_transpose.toy -emit=mlir -opt

# 添加 Pure trait 后再运行(消除所有 transpose)
toyc-ch3 test/transpose_transpose.toy -emit=mlir -opt

# reshape 优化(DRR 风格)
toyc-ch3 test/Examples/Toy/Ch3/trivial_reshape.toy -emit=mlir -opt
```

### 关键配置项与代码片段(原文有)

1. **ODS 中启用 canonicalizer**(TableGen):
   ```tablegen
   def TransposeOp : Toy_Op<"transpose", [Pure]> {...}
   ```
   - `[Pure]` trait 让 MLIR 允许 DCE 该 op。
   - `hasCanonicalizer = 1`(原文链接到 [Operations.md/#hascanonicalizer](../../DefiningDialects/Operations.md/#hascanonicalizer))让 Canonicalizer 框架发现 `getCanonicalizationPatterns`。

2. **注册模式到 Canonicalization**(C++):
   ```c++
   void TransposeOp::getCanonicalizationPatterns(
       RewritePatternSet &results, MLIRContext *context) {
     results.add<SimplifyRedundantTranspose>(context);
   }
   ```

3. **PassManager 中加入 Canonicalizer Pass**(C++,位于 `toyc.cpp`):
   ```c++
   mlir::PassManager pm(module->getName());
   pm.addNestedPass<mlir::toy::FuncOp>(mlir::createCanonicalizerPass());
   ```

4. **DRR 规则自动生成**: 每个 DRR `Pat` 在构建时被转为 C++,输出到
   ```
   path/to/BUILD/tools/mlir/examples/toy/Ch3/ToyCombine.inc
   ```
   (原文如此,无需用户额外编译指令)

### 原文未涉及

- 任何**全局优化**、跨函数优化、循环变换的具体方法。
- 性能基准数据(benchmark numbers)。
- 多线程/并行应用 pattern 的配置项。
- 自定义 GreedyPatternRewriteDriver 的 `benefit` 调优指南(除 `benefit=1` 默认值外未给出推荐范围)。
