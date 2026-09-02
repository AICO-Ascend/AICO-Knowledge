# Chapter H: Reproducing Halide Schedule

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/transform/ChH.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/transform/ChH.md

# 一体化深度解读:Chapter H — Reproducing Halide Schedule

---

## 【定位】

本文档解决"如何用 MLIR 的 Transform dialect + Linalg structured ops 来复现 Halide DSL 的调度(schedule)"这一示范性问题,以 2D 通道卷积为例,把 Halide 的 `split / reorder / vectorize / unroll / parallel / compute_at` 等"分离式(schedule 与 compute 分离)"调度原语映射到 MLIR 的变换算子上。

---

## 【技术要点】

1. **两种映射路径**:Halide → Transform dialect 可走两条路 — (a) 新建一个对应 Halide DSL 计算部分的方言,并围绕它包装 Transform dialect 变换;或 (b) 将 Halide 抽象映射到既有 MLIR 抽象(计算部分 → Linalg,调度部分 → Transform)。文档选用后者,因 Linalg 的结构化操作与 Halide 的"数学函数"概念更贴近。
2. **示例问题规模(原文 C++ 尺寸常量)**:`N = 5, CI = 128, CO = 128, W = 100, H = 80`;输入张量 `input[CI][W+2][H+2][N]`(Halide 维度顺序相对 C++ 是反转的),卷积核 `filter[CO][3][3][CI]`,偏置 `bias[CO]`。
3. **Halide ↔ Linalg 循环结构差异**:Halide 把 `conv` 的初始化 + 累加 + `relu` 放在共享的迭代变量 `x,y,c,n` 下 → 等价于"全融合(fully-fused)"循环嵌套;Linalg 则把初始化、卷积更新、ReLU 表示为三个独立操作 → "全分布(fully-distributed)"循环嵌套。这直接影响后续 schedule 的构造方式。
4. **`split` ↔ `transform.structured.tile_using_forall`**:`split` 在 Halide 中把一个循环维度拆成两个紧邻嵌套循环(内层迭代数 ≤ 给定值),等价于 Linalg 中的 strip-mining / 单维退化 tile。文档选用 `tile_using_forall` 是因其对 bufferization 支持最好,并可在后续转 parallel loop;注意它不像 Halide 那样增加新维度,而是围绕操作生成外层循环并把操作改写为对原数据子集进行运算。
5. **`reorder`** 在 Linalg 中调度策略不同:Linalg 循环是隐式的,在面向 microkernel 时应尽量保持隐式;只有当真正需要在外层调度时,才借助 `transform` 把隐式循环转为显式 `scf.for`/`forall` 后再 reorder。
6. **`compute_at`** 在 Halide 中把某个 Func(此处为 `conv`)的计算下移到消费者(此处 `relu`)的某个循环变量(此处 `xo`)内部,从而复用中间张量并避免物化;这是 Linalg 的 fusion 类变换(`fuse_into_containing_op` 等)的对应物。

---

## 【关键机制与数据】

### 1. 工作原理(Halide compute 表示)

```text
conv(c, x, y, n)  = bias(c);
conv(c, x, y, n) += filter(c, r.y, r.z, r.x) * input(r.x, x + r.y, y + r.z, n);
relu(c, x, y, n)  = max(0, conv(c, x, y, n));
```

归约域 `RDom r(0, CI, 0, 3, 0, 3)`,三个归约维度后文称为 `r.x, r.y, r.z`。

### 2. 数据流(从 Halide 到 Linalg)

- **Bias 初始化**:用命名 op `linalg.broadcast`,沿维度 `[0, 1, 2]` 把 1D `bias` 广播成 4D 张量。
- **卷积主体**:由于 Halide 例子的 filter 维度顺序与 Linalg 现成的 2D 卷积命名 op 不兼容(且把 filter 当作第一个参数),故用 `linalg.generic` 通用形式忠实复现;`arith.mulf` 与 `arith.addf` 都带 `{fastmath = #arith.fastmath<fast>}` 属性,以便后续重组为 `math.fma` 并允许重排归约。
- **ReLU**:用 `linalg.generic` 做 `max(0, x)`,内部用 `llvm.intr.maxnum` 实现 IEEE 754 maxnum。

### 3. 性能/结构相关数据(原文)

- **Halide 循环结构(原文 `HL_DEBUG_CODEGEN=1` dump 改编)**:n → y → x → c 四层并行外循环,内嵌 `rz → ry → rx` 三层归约;`conv` 初始化与累加在同一个 `c` 循环体内,`relu` 紧跟其后。
- **Linalg 循环结构(原文由 `mlir-opt --linalg-generalize-named-ops --empty-tensor-to-alloc-tensor --one-shot-bufferize --convert-linalg-to-loops` 获得)**:三个独立循环嵌套块 — bias init、convolution update、relu — 各自拥有完整的 `n→y→x→c` 外层,内部只有各自的归约或无归约。
- 文档明确说明:**为避免 Halide 与 MLIR 并行运行时差异,本文只考虑不含 `parallel` 的调度**,即只看循环变换、unroll、vectorize。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

### 公式 1:Halide 卷积定义

原文(原文保留字面):

```
conv(c, x, y, n)  = bias(c);
conv(c, x, y, n) += filter(c, r.y, r.z, r.x) * input(r.x, x + r.y, y + r.z, n);
relu(c, x, y, n)  = max(0, conv(c, x, y, n));
```

符号含义:

| 符号 | 含义 |
|---|---|
| `conv`, `relu` | Halide `Func`,数学意义上的"函数/张量" |
| `c, x, y, n` | 顶层迭代器:通道、宽(x)、高(y)、批次 |
| `r` | 归约域 `RDom r(0, CI, 0, 3, 0, 3)`;三维度后文称 `r.x, r.y, r.z` |
| `filter(c, r.y, r.z, r.x)` | 卷积核项;维度顺序为 `[输出通道, ry, rz, 输入通道]` |
| `input(r.x, x + r.y, y + r.z, n)` | 输入项;`x+r.y`、`y+r.z` 是显式的窗口偏移 |
| `bias(c)` | 输出通道 c 的偏置标量(在 Halide 中以广播方式参与累加) |
| `max(0, ·)` | ReLU 修正线性单元 |

### 公式 2:Linalg 卷积 `indexing_maps`

原文(原文保留字面):

```text
iterator_types = ["parallel", "parallel", "parallel", "parallel",
                  "reduction", "reduction", "reduction"],
indexing_maps = [
  affine_map<(n, y, x, c, rz, ry, rx) -> (rx, rz, ry, c)>,
  affine_map<(n, y, x, c, rz, ry, rx) -> (n, y+rz, x+ry, rx)>,
  affine_map<(n, y, x, c, rz, ry, rx) -> (n, y, x, c)>
]
```

符号含义:

| 符号 | 含义 |
|---|---|
| `n, y, x, c` | 四个 parallel 维度(对应 Halide 的迭代变量,注意顺序在 Halide 中 `n` 是最外层/变化最慢) |
| `rz, ry, rx` | 三个 reduction 维度(归约窗口的 z、y、x 三轴) |
| `affine_map<...> -> (rx, rz, ry, c)` | 第一输入(filter)的访问模式:按归约顺序取,filter 维度为 `[输入通道, ry, rz, 输出通道]`——这是原文特意强调的"非标准顺序" |
| `affine_map<...> -> (n, y+rz, x+ry, rx)` | 第二输入(input)的访问模式:`y+rz`、`x+ry` 还原窗口偏移 |
| `affine_map<...> -> (n, y, x, c)` | 输出(累加器)的访问模式:无归约维度 |
| `iterator_types` 7 个 | 4 parallel + 3 reduction,决定此 generic op 的循环类型 |

### 公式 3:Linalg ReLU `indexing_maps`

原文(原文保留字面):

```text
iterator_types = ["parallel", "parallel", "parallel", "parallel"],
indexing_maps = [
  affine_map<(d0, d1, d2, d3) -> ()>,
  affine_map<(d0, d1, d2, d3) -> (d0, d1, d2, d3)>,
  affine_map<(d0, d1, d2, d3) -> (d0, d1, d2, d3)>
]
```

符号含义:

| 符号 | 含义 |
|---|---|
| 第一个 `affine_map<...> -> ()` | 标量 `0.0`(常数 `c0`)的零秩访问 |
| 第二/三个 `affine_map<...> -> (d0,d1,d2,d3)` | 卷积结果和最终输出,均为同一 4D shape 的恒等访问 |

### 公式 4:Halide schedule 表达式链

原文(原文保留字面):

```
relu.split(c, co, ci, vec * tile_w)
  .split(x, xo, xi, tile_h)
  .reorder(ci, xi, xo, y, n, co)
  .vectorize(ci, vec)
  .unroll(ci)
  .unroll(xi)
  .parallel(y)
  .parallel(n)
  .parallel(co);

conv.compute_at(relu, xo)
  .vectorize(c, vec)
  .unroll(c)
  .unroll(x)
  .unroll(y)
  .update()
  .reorder(c, x, y, r.x, r.y, r.z, n)
  .vectorize(c, vec)
  .unroll(c)
  .unroll(x)
  .unroll(y)
  .unroll(r.x, 2);
```

符号含义(原文未给出 `vec / tile_w / tile_h / co / ci / xo / xi` 的具体数值,文档把它们当作给定调度参数):

| 符号 | 含义 |
|---|---|
| `split(c, co, ci, vec * tile_w)` | 将 `c` 拆为外 `co`、内 `ci`,内层至多 `vec * tile_w` 次迭代 |
| `split(x, xo, xi, tile_h)` | 将 `x` 拆为外 `xo`、内 `xi`,内层至多 `tile_h` 次 |
| `reorder(ci, xi, xo, y, n, co)` | 重排循环顺序(最内→最外) |
| `vectorize(ci, vec)` / `unroll(ci)` / `unroll(xi)` | 向量化与展开 |
| `parallel(y/n/co)` | 并行化(本文档有意忽略) |
| `conv.compute_at(relu, xo)` | 把 `conv` 的计算嵌入到 `relu` 在 `xo` 循环的迭代中,实现算子融合 |
| `.update()` | 选中 `conv` 的累加更新语句(区别于初始化) |
| `.unroll(r.x, 2)` | 对归约维 `r.x` 因子为 2 的展开 |

---

## 【关联】

文档处于 MLIR 的 Tutorials → Transform 章节链中(Chapter H 标识符暗示前序章节 A–G),其与下列特性/模块的关系如下(全部源于原文):

- **Transform dialect**:本文档的"调度承载体";文档开头明确定义其作用为"实现变换指令式 DSL 的基底",并允许通过新增 op 或新方言来支撑特定调度模型。
- **Linalg dialect(结构化操作)**:本文档计算部分的"承接者"。Halide 的 `Func` 数学函数抽象几乎一一对应 Linalg 的 structured op(broadcast、generic);但 Linalg 不支持 Halide 那种"初始化 + 原地累加合一"的对象模型,而是把初始化与 update 表达为两个独立 op。
- **Halide DSL**:被复现的对象;链接到 http://halide-lang.org,以及具体示例 apps/conv_layer(commit `294f80c49bf3bb8582446613c25fcce03b82bcd8`)。
- **`linalg.tile_` transform ops / `transform.structured.tile_using_forall`**:用于实现 `split` 与(单维退化)tile;`tile_using_forall` 还能为后续并行化提供基础。
- **fastmath / `math.fma`**:Linalg generic 体内带 `{fastmath = #arith.fastmath<fast>}` 的 `mulf`+`addf`,后端可重组为 `math.fma`,并允许归约重排。
- **MLIR 命令行工具链**(原文出现):`mlir-opt --linalg-generalize-named-ops --empty-tensor-to-alloc-tensor --one-shot-bufferize --convert-linalg-to-loops`,用于查看 Linalg 的循环结构,作为与 Halide `HL_DEBUG_CODEGEN=1` dump 的对比手段。
- **代码与教程源**:https://github.com/llvm/llvm-project/tree/main/mlir/test/Examples/transform/ChH — 原文多次声明"以此源码为权威",因本文档伪代码可能与当前语法脱节。

---

## 【使用方法】

- **示例源码位置**(原文):`mlir/test/Examples/transform/ChH`(在 llvm-project 仓库下,URL 见原文)。
- **查看 Halide 端循环结构的方法**(原文):设置环境变量 `HL_DEBUG_CODEGEN=1` 后跑 Halide 程序以 dump codegen。
- **查看 Linalg 端循环结构的方法**(原文给出的 `mlir-opt` 流水线):
  ```
  mlir-opt --linalg-generalize-named-ops --empty-tensor-to-alloc-tensor \
           --one-shot-bufferize --convert-linalg-to-loops
  ```
- **复现策略(原文说明)**:为避开 Halide 与 MLIR 各自并行运行时差异,本文只讨论不含 `parallel` 的 schedule;实际把 `split / reorder / vectorize / unroll / compute_at` 映射为 `transform.structured.*` 算子(例:`tile_using_forall`)并作用于 Linalg structured op 上。
- **配置项/命令开关**(原文):上文 `mlir-opt` 流水线的各 `--` 开关即为典型配置;`vec / tile_w / tile_h` 等调度参数在原文示例中以变量形式出现,本文档未给出具体数值。
- 文档末尾(从 "The order of implicit loops in a `linal" 起)出现截断,关于 `reorder` 与剩余调度原语到 Linalg 变换的逐项映射、以及完整 Transform dialect 序列本文档未给出,需以仓库内 ChH 源码为准。
