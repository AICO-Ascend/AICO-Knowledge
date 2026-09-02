# Tile Cube and Vector Loop

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/CV/TileCubeAndVectorLoop.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/CV/TileCubeAndVectorLoop.md

## 【定位】

这篇文档说明 HIVM 中的 **TileCubeVectorLoop** pass，如何在 **CV Pipelining** 之后对 Mix kernels 内的 Cube、Vector 循环再次分片，以降低 AIC/AIV 核间同步开销并提升 L0C、UB 容量约束下的执行效率。

## 【技术要点】

- **作用阶段**：仅处理经过 **CV Pipelining** 后的 Mix kernel，对其中的 Cube loop 和 Vector loop 执行二次 tiling。
- **核心分片方式**：遍历 IR，以 Cube、Vector loop 中的 `hivm` **CopyOut op** 为锚点，切分其 producers，再把切分后的计算融合回对应循环。
- **硬件目标**：在硬件限制内使用尽可能大的 tile，使较小迭代更容易放入 L0C、UB，减少因 AIC/AIV 数据依赖而触发的核间同步。
- **编译选项**：
  - `tile-mix-cube-loop`：默认值为 `1`；表示 Cube loop trip count，`1` 表示不分片。
  - `tile-mix-vector-loop`：默认值为 `1`；表示 Vector loop trip count，`1` 表示不分片。
- **处理范围**：只处理带有 `hivm.loop_core_type` 属性的 `scf.for`，且该属性只能为 `#hivm.tcore_type<CUBE>` 或 `#hivm.tcore_type<VECTOR>`。
- **约束条件**：Vector 的分片块小于 UB alignment 时不分片；Cube 分片前块大小小于 L0C 总大小时也不分片，并且当前尚未将 L1 大小纳入 Cube tiling 决策。

## 【关键机制与数据】

- **原文（硬件背景）**：Ascend AI 加速器采用 AIC 与 AIV 解耦架构。两类核心之间通过 Global Memory 交换数据；存在数据依赖时，需要使用核间同步指令保证正确性，而频繁同步会造成性能下降，因此应尽量降低 AIC/AIV 之间的同步频率。

- **原文（Pass 工作流）**：该 pass 遍历 IR，找到 Cube loop 和 Vector loop 的 CopyOut op，将这些 op 作为锚点切分其 producers，并把切分结果融合回循环。整体数据流可以概括为：  
  `遍历 IR → 定位 CopyOut 锚点 → 切分其 producers → 将 split 融合进原 loop`。

- **原文（Cube 分片动机）**：Cube 的 Matmul 结果进入 L0C。如果一次迭代超过 L0C 容量，就无法一次性放入 L0C，因此需要在容量约束下切成更合适的迭代块，并在限制内争取更大的 tile，以改善访存和计算效率。

- **原文（Vector 分片动机）**：Vector 单次迭代过大可能导致 Unified Buffer（UB）溢出；切成更小的迭代后，迭代块更容易满足 UB 的容量和 alignment 条件。

- **原文（边界与风险）**：如果 Vector 分片块大小小于 UB alignment，或者 Cube 分片前块大小已经小于 L0C 总大小，则 pass 不执行 tiling。Cube tiling 目前还没有考虑 L1 容量，某些情况下可能发生 **L1 Memory Overflow**；后续计划通过 liveness analysis 改进。

- **原文（性能数据）**：文档没有给出绝对性能、同步次数、加速比、时延或具体 tile size 等实测数据，只给出了降低同步次数、避免 L0C/UB 溢出以及提高访存和计算效率的定性目标。

## 【表格解读】

原文中的参数表如下：

| Option| Default Value| Description|
|------|--------|------|
| `tile-mix-cube-loop` | 1 | Cube loop trip count; 1 means no tiling.|
| `tile-mix-vector-loop` | 1 | Vector loop trip count; 1 means no tiling.|

逐行解读：

| 原文配置项 | 作用与取值含义 |
|---|---|
| `tile-mix-cube-loop` | 控制 Cube loop 的 trip count；默认值为 `1`，此时不进行 tiling。该选项与 Cube Matmul 结果使用 L0C 缓存的硬件行为相关，但原文没有给出推荐的非 `1` 配置值。 |
| `tile-mix-vector-loop` | 控制 Vector loop 的 trip count；默认值为 `1`，此时不进行 tiling。分片结果还必须满足 UB alignment 和容量条件。 |

除上述两个参数外，原文没有性能对比表、测试配置表或进一步的可调参数表。

## 【公式解读】

原文无 LaTeX 公式，但提供了两段 MLIR 形式的前后伪代码。

**分片前：**

```mlir
scf.for {
  hivm.load A
  hivm.load B
  hivm.hir.mmadL1
  hivm.hir.fixpipe
} {cube_loop}
```

逐项解释：

- `scf.for`：表示外层结构化循环；原图用它表示 Cube 计算所在的 `scf.for`。
- `hivm.load`：HIVM 的加载操作。
- `A`、`B`：被加载数据的示意名称，原文没有给出其张量形状、类型或地址。
- `hivm.hir.mmadL1`：加载 A、B 之后执行的 Matrix Multiply-Add 类操作，是伪代码中 Cube 计算阶段的一部分。
- `hivm.hir.fixpipe`：紧接 `hivm.hir.mmadL1` 执行的后续操作。
- `{cube_loop}`：示意性地标识外层循环。
- 整个结构表达的是：在一个较大的 Cube 循环体内依次加载 A、B，执行 `hivm.hir.mmadL1` 和 `hivm.hir.fixpipe`。

**分片后：**

```mlir
scf.for {
  for {
    hivm.load slice_A
    hivm.load slice_B
    hivm.hir.mmadL1
    hivm.hir.fixpipe
  } {sub_tile}
} {cube_loop}
```

逐项解释：

- 第一个 `scf.for { ... } {cube_loop}` 保持外层 `cube_loop` 的循环结构。
- 内层 `for` 表示新拆出的较小迭代块；原文按示意写法使用 `for`，没有把它改写为 `scf.for`。
- `{sub_tile}` 示意性地标识内层子分片循环。
- `hivm.load slice_A` 和 `hivm.load slice_B` 表示每个子迭代只加载 A、B 的一部分切片。
- 每次内层迭代仍包含 `hivm.hir.mmadL1` 和 `hivm.hir.fixpipe`，说明切分发生在 producer 加载及计算迭代层面，而不是简单把计算结果拆到循环外。
- 缩进表示 `sub_tile` 嵌套在 `cube_loop` 中；原来一次较大的迭代被组织成多个较小的子迭代。
- 伪代码没有给出迭代范围、分片尺寸、分片公式或 CopyOut 的具体写法，因此不能从该示例推导具体 tile 数值。

## 【关联】

- **[CV Optimization](./CVOptimization.md)**：文档明确建议在阅读前先了解该文档，以统一 AIC、AIV、Mix kernel、Cube、Vector 等 CV 术语背景。
- **CV Pipelining**：TileCubeVectorLoop 位于 CV Pipelining 之后。CV Pipelining 先完成流水线化处理，该 pass 再针对 Cube 和 Vector loop 做二次 tiling。
- **HIVM 循环与核心类型**：该 pass 以 `scf.for` 为处理对象，并通过 `hivm.loop_core_type` 将循环限定为 Cube 或 Vector 类型。
- **CopyOp 与 CopyOut**：pass 通过 `hivm.load` 展示切分后的数据加载效果，并以 CopyOut op 作为生产者切分锚点。
- **AIC/AIV 与 Global Memory**：AIC/AIV 的解耦执行带来 Global Memory 数据交换；只有存在核间数据依赖时才需要同步，而 tiling 旨在减少这种同步。
- **L0C、UB 与 L1**：L0C 约束 Cube 迭代容量，UB 约束 Vector 迭代容量；当前 Cube 决策尚未考虑 L1，后续计划加入 liveness analysis。
- **Mix kernels**：该 pass 面向 Mix kernels 内的 Cube、Vector 循环，并非所有任意形式的 `scf.for` 都会被处理。

## 【使用方法】

原文未提供具体的命令行、编译命令或 pass 启用命令，仅给出以下 API 编译选项：

```text
tile-mix-cube-loop
```

- 默认值：`1`
- 含义：Cube loop trip count。
- `1` 的特殊语义：不执行 tiling。
- 原文未给出具体的非 `1` 推荐值。

```text
tile-mix-vector-loop
```

- 默认值：`1`
- 含义：Vector loop trip count。
- `1` 的特殊语义：不执行 tiling。
- 原文未给出具体的非 `1` 推荐值。

启用实际 tiling 时，循环还必须满足：

- 是带 `hivm.loop_core_type` 属性的 `scf.for`；
- 属性值为 `#hivm.tcore_type<CUBE>` 或 `#hivm.tcore_type<VECTOR>`；
- Vector 分片块不小于 UB alignment；
- Cube 分片前块大小不小于 L0C 总大小。

需要注意：Cube 分片目前只检查 L0C，尚未考虑 L1 容量，某些情况下可能发生 L1 Memory Overflow。

## 图文联合解读

- `TileCubeAndVectorLoop.png`: **图示解读：**

1) **结构**：左图为CV Pipelining后状态，含4个GM工作块(0-3)，AIC/AIV各通过实线（写入）与虚线（读取）箭头与GM多次交互；右图为Tile Cube and Vector Loop后，GM块两两合并为4对(0,0/1,1/2,2/3,3)，AIC/AIV与GM的连线减半。

2) **结论**：Cube tiling=2使每块容量翻倍、块数减半，**同步次数减半**，通信开销降低；更大的tile更易装入L0C/UB，提升访存与计算效率。

3) **与文档呼应**：直观印证"减少AIC-AIV核间同步"与"在硬件容量上限内增大tile"两大优化目标。
