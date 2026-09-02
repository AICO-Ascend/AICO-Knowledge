# Chapter 0: A Primer on “Structured” Linalg Operations

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/transform/Ch0.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/transform/Ch0.md

# 一体化深度解读: MLIR Structured Linalg Operations Primer (Ch0)

## 【定位】

本文档是 MLIR Transform dialect 教程的第 0 章, 旨在为读者铺垫 **"结构化操作" (Structured Operations)** 的概念基础——说明如何在 Linalg/Vector dialect 中通过保留高层计算结构 (如 elementwise、reduction、contraction、loop fusion) 来赋予编译器在代码生成时更大的优化自由度, 从而为后续 Transform dialect 章节中针对结构化操作的变换 (最成熟、最适合教学) 做准备。

> **重要说明**: 原文明确指出 "Transform dialect does not require Structured operations and vice versa", 二者只是历史共生关系; 本章重点是结构化抽象本身, 而非 Transform dialect 的 API。

---

## 【技术要点】

1. **Uniform Elementwise Extension** — 标量算术操作可"透明地"扩展到任意秩向量, 例如 `arith.addf` 从 `f32` 扩展到 `vector<8xf32>`, 再到 `vector<8x4xf32>`, 甚至 `vector<2x2x2x2x2x2x2xf32>`, 编译器可据此降级为低秩指令或融合 mul/add (避免上百次 mul 后接上百次 add 的指令风暴)。

2. **Vector Reduction** — `vector.reduction <add>, %v : vector<8xf32> into f32` 显式表达"向量内归约"; 当目标无对应指令时, 可降级为 `scf.for` 循环 (原文给出 `for %i = %c0 to %c8 step %c1` 的循环展开形式), 也可在有指令时强制使用循环以权衡指令延迟与寄存器压力 (unrolling)。

3. **Vector Contraction** — `vector.contract` 通过两个关键 attribute 描述:
   - `indexing_maps`: 一组 `affine_map`, 指定每个操作数如何被迭代变量索引;
   - `iterator_types`: 每维标记为 `"reduction"` 或 `"parallel"`。
   
   原文给出的 3D 例子 (8×10 × 10×16 → 8×16) 实质编码了 **矩阵乘** `init[i,j] += lhs[i,k] * rhs[k,j]`。

4. **linalg.generic on Memref** — `indexing_maps` 与 `iterator_types` **与 vector.contract 完全相同**; 操作数拆分为:
   - `ins`: 只读的输入 buffer;
   - `outs`: 读且更新的输出 buffer (向量是 SSA 只读的, 所以 vector 上不需要这一拆分)。
   
   region 内显式给出 mul + add 两条 IR 指令; region 按任意顺序遍历所有元素元组, 写入以整体方式在 op 末尾完成。

5. **Loop Fusion via Region** — `linalg.generic` 的 region 可串联任意多条 op, 从而表达隐式循环融合。例如 ReLU `max(0,x)` 可用一次 `linalg.generic` 完成 (compare-and-select), **不需要临时 buffer 存比较结果, 也不需要外层 op 重复执行**。

6. **Tensor 形式的 Generic Op** — (原文在此处被截断, 仅以"Let us take one"结尾, 未给出完整内容)。

---

## 【关键机制与数据】

> **原文工作机制 (数据流视角)**:

**Elementwise → 矢量化降秩**: 一条 `arith.addf %0, %1 : vector<2x2x2x2x2x2x2xf32>` 不必逐元素展开, 编译器可基于"uniform elementwise"这一结构信息, 把它降为低秩硬件指令 (例如 8×f32) 或识别 FMA 机会。

**Reduction → 循环/指令双解**: `vector.reduction` 提供一个语义锚点, 编译器据此决定: (a) 映射到专用归约指令; (b) 拆为 `vector.extractelement` + `arith.addf` 的 `scf.for` 循环 (含 unroll)。

**Contraction → 矩阵乘的 IR 抽象**: 通过 `indexing_maps` + `iterator_types`, 编译器得以**识别** GEMM/dot-product 类操作, 并可选地:
- 直接生成调用预生成 microkernel 的代码;
- 降级为外层 `scf.for` 三重循环;
- 拆分后调用 Vector dialect 原语。

**Memref 写入模型**: region 内的 block arguments 顺序对应 `ins` → `outs`; `linalg.yield` 的值是下一轮 region 执行的"`out` 元素输入", **执行顺序未指定**, 最终 `out` buffer 整体写入。

**Fusion 模型**: 多次原本需要 buffer 中间结果的 op, 在单个 `linalg.generic` region 内串联, 实现"无临时缓冲的隐式循环融合"。

> **性能/数字相关数据**: 原文未提供基准测试或性能数字, 仅给出示例类型尺寸: `vector<8xf32>`, `vector<8x4xf32>`, `vector<2x2x2x2x2x2x2xf32>`, `vector<8x10xf32>`, `vector<10x16xf32>`, `vector<8x16xf32>`, `memref<8x10xf32>` 等, **这些是示例 shape, 非性能数据**。

---

## 【表格解读】

**原文无表格**。文档中所有对比/参数信息均以 MLIR 代码片段或文字段落形式呈现, 例如 `iterator_types` 的取值列表 `"parallel"` / `"reduction"` 散布于各示例中, 未以表格形式汇总。

---

## 【公式解读】

原文未使用 LaTeX 数学公式, 但存在若干**类公式的伪代码 / MLIR affine_map 表达式**, 严格保留如下并解释:

### 公式 1 — Reduction 的循环等价 (原文 Section "Reduction")

```
for i in 0 to 8:
  partial = partial + v[i]
```

- 符号说明 (依据原文):
  - `i`: 循环归纳变量, 范围 `[0, 8)`;
  - `partial`: 累加器, 初值 `0.0` (来自 `%init = arith.constant 0.0 : f32`);
  - `v[i]`: 从 `%0 : vector<8xf32>` 通过 `vector.extractelement %0[%i]` 取出;
  - 该形式与 `vector.reduction <add>` 语义等价。

### 公式 2 — 1D Contraction 仿射索引 (原文 Section "Contraction")

```
indexing_maps = [affine_map<(i) -> (i)>,
                 affine_map<(i) -> (i)>,
                 affine_map<(i) -> ()>]
iterator_types = ["reduction"]
```

等价的伪代码:

```
for i in 0 to 8:
  init += p0[i] * ones[i]
```

- 符号说明:
  - `%0` (LHS 输入) 的 affine map `(i) -> (i)`: 归纳变量 `i` 直接索引向量第 `i` 元素;
  - `%ones` (值为 `1.0` 的稠密向量) 的 affine map `(i) -> (i)`: 同上;
  - `%init` (标量累加器) 的 affine map `(i) -> ()`: 不依赖 `i`, 即**单一标量值在整次 reduction 中被复用**;
  - `iterator_types = ["reduction"]`: 唯一维被归约。

### 公式 3 — 3D Matrix-Multiplication Contraction (原文 Section "Contraction")

```
indexing_maps = [affine_map<(i, j, k) -> (i, k)>,
                 affine_map<(i, j, k) -> (k, j)>,
                 affine_map<(i, j, k) -> (i, j)>]
iterator_types = ["parallel", "parallel", "reduction"]
```

等价的伪代码:

```
for i in 0 to 8:
  for j in 0 to 16:
    for k in 0 to 10:
      init[i, j] += lhs[i, k] * rhs[k, j]
```

- 符号说明:
  - 三个迭代维度 `(i, j, k)`, 范围分别 0..8, 0..16, 0..10;
  - `lhs` shape `vector<8x10xf32>` 被 `(i, k)` 索引 → 行 `i`, 列 `k`;
  - `rhs` shape `vector<10x16xf32>` 被 `(k, j)` 索引 → 行 `k`, 列 `j`;
  - `init` shape `vector<8x16xf32>` 被 `(i, j)` 索引 → 行 `i`, 列 `j`;
  - `iterator_types`: `i`、`j` 为 `"parallel"` (保留维), `k` 为 `"reduction"` (归约维)。

### 公式 4 — linalg.generic on Memref (原文 Section "Generic Operation on Memory")

```
indexing_maps = [affine_map<(i, j, k) -> (i, k)>,
                 affine_map<(i, j, k) -> (k, j)>,
                 affine_map<(i, j, k) -> (i, j)>]
iterator_types = ["parallel", "parallel", "reduction"]
```

- 符号说明: 与公式 3 **完全相同** (原文用 "exactly the same" 强调), 只是操作数类型从 `vector<...>` 替换为 `memref<8x10xf32>` / `memref<10x16xf32>` / `memref<8x16xf32>`, 区域 (region) 内显式给出 `%0 = arith.mulf` 与 `%1 = arith.addf`。

---

## 【关联】

原文提及的上下游 dialect / 模块关系如下 (因原文明确标注"无内部链接", 以下关系均来自正文叙述):

| 关联对象 | 关系描述 |
|---|---|
| **Transform dialect** | 后续教程 (Ch1+) 的主题; 与结构化操作共生演化, **不强制依赖**, 但结构化操作变换是最成熟、教学最合适的子集 (开头段) |
| **Vector dialect** | 提供 `vector.reduction`、`vector.contract`、`vector.extractelement` 等高层抽象, 是结构化操作的主要载体 (Reduction、Contraction 节) |
| **Linalg dialect** | 提供 `linalg.generic`、`linalg.yield`, 把 vector 抽象延伸到 memref / tensor, 引入 `ins/outs` 拆分与 region (Generic Operation on Memory 节) |
| **Arith dialect** | 提供 `arith.addf`、`arith.mulf`、`arith.cmpf`、`arith.select`、`arith.constant`, 是 region 内 scalar 算术的承载者 |
| **SCF dialect** | `scf.for` + `scf.yield` + `iter_args` 是 reduction 无专用指令时的循环等价的承载形式 (Reduction 节) |
| **机器学习层 (ReLU)** | 作为"Loop Fusion"机制的实例, 展示 fused `max(0,x)` 如何表达 |

> 注意: 本文档末尾的 "Generic Operation on Tensors" 节**在原文被截断**, 因此 tensor 与 vector/memref 形式的具体差异、可能的额外 attribute 等信息**原文未提供**, 不做推测。

---

## 【使用方法】

**原文未涉及**。本文档为概念性 primer, 仅展示 MLIR IR 片段用于说明结构化抽象, 未给出任何启用命令、CMake 选项、`mlir-opt` flag 或配置项。教程的实际操作步骤应位于被截断的 "Generic Operation on Tensors" 节或后续 Chapter 1+ 中。
