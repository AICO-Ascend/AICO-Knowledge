# Cube与Vector循环切块

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/tile_cube_and_vector_loop.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/tile_cube_and_vector_loop.md

# Cube与Vector循环切块 — 一体化深度解读

## 【定位】

本文档描述 HIVM 中 **TileCubeVectorLoop Pass** 的功能、原理与使用约束，该 Pass 针对 CV（Cube-Vector）类 kernel 中已经完成软件流水的 Cube 与 Vector 循环做进一步的 Tiling 切分，以降低 AIC/AIV 核间同步频率、规避本地 buffer 溢出、提升访存与计算效率。

---

## 【技术要点】

1. **作用对象**：仅处理携带 `hivm.loop_core_type` 属性的 `scf.for` 循环，且属性值需为 `#hivm.tcore_type<CUBE>` 或 `#hivm.tcore_type<VECTOR>`，即只针对已经完成 CV 软件流水（CUBE 流水或 VECTOR 流水）的循环。
2. **锚点机制**：通过遍历 IR 寻找 Cube 和 Vector 循环对应的 `CopyOut` 操作进行切分，并以其为锚点（anchor point），将数据的 producer 依此切分，并融合至循环内。
3. **变换形态**：将原本一次迭代完成一整块计算的 `scf.for` 拆分为外层 `cube_loop` + 内层 `sub_tile` 两层嵌套结构，每层 `sub_tile` 处理更小的一块数据。
4. **编译开关**：
   - `tile-mix-cube-loop`，默认 `1`，为 `1` 时不 tiling
   - `tile-mix-vector-loop`，默认 `1`，为 `1` 时不 tiling
5. **硬件约束阈值**：
   - Vector 侧：若 Tiling 后切块大小 **小于 UB 对齐大小**，则不做 Tiling
   - Cube 侧：若 Tiling 前切块大小 **小于 L0C 总大小**，则不做 Tiling
6. **已知限制**：文档明确指出，当前尚未考虑 L1 空间大小约束，部分场景下可能会出现 L1 Memory Overflow 报错，后续将结合生命周期分析决定 Cube 侧的 Tiling。

---

## 【关键机制与数据】

- **硬件背景数据流**：当代昇腾 AI 加速芯片采用 **AIC（Cube 核）与 AIV（Vector 核）分离模式**，二者数据交互必须经过 **Global Memory**。当存在数据依赖时需要 **核间同步指令** 保证正确性，频繁同步会 **降低性能**。
- **设计目标**（原文双层目标）：
  1. 减少核间同步：每次迭代处理数据更小，更可能被限制在本地 buffer（L0C、UB 等）内，从而降低跨核同步开销。
  2. 增大切分粒度：在满足硬件约束前提下，有机会使用更大的 tile size。
- **Buffer 容量约束**（原文）：
  - Cube 侧：矩阵乘法结果存放在 **L0C Buffer**，若单次迭代数据总大小超过 L0C 容量则无法一次性放下。
  - Vector 侧：单次迭代过大可能导致 **UB（Unified Buffer）缓冲溢出**。
- **变换前 IR 结构**（原文 mlir 代码）：
  ```
  scf.for {
    hivm.load A
    hivm.load B
    hivm.hir.mmadL1
    hivm.hir.fixpipe
  } {cube_loop}
  ```
- **变换后 IR 结构**（原文 mlir 代码，外层 cube_loop 包裹内层 sub_tile 循环）：
  ```
  scf.for {
    for {
      hivm.load slice_A
      hivm.load slice_B
      hivm.hir.mmadL1
      hivm.hir.fixpipe
    } {sub_tile}
  } {cube_loop}
  ```
- **执行顺序**（原文）：寻找 `CopyOut` → 以其为锚点 → 对 producer 进行切分 → 融合至循环内。

> 原文未给出具体的性能对比数据（如加速比、耗时数字等），亦未给出 L0C 与 UB 的具体容量数值。

---

## 【表格解读】

原文包含一张「编译选项」配置表，逐字还原如下：

| 选项 | 默认值 | 含义 |
|------|--------|------|
| `tile-mix-cube-loop` | 1 | Cube循环目标trip count；为1时不tiling |
| `tile-mix-vector-loop` | 1 | Vector循环目标trip count；为1时不tiling |

**逐行解读**：

- **第一行 `tile-mix-cube-loop`**：控制 Cube 循环的目标 trip count（即 Tiling 后每个子循环块希望执行的迭代次数）。默认值为 `1`，含义是在默认配置下不做 Tiling（保持原始的"一次迭代一整块"行为）；用户需将该值调大才会触发 Cube 循环的切分。
- **第二行 `tile-mix-vector-loop`**：与上一项对称，控制 Vector 循环的目标 trip count。默认值同样为 `1`，即默认不触发 Vector 循环 Tiling；调大后才会将 Vector 循环再细分为多次更小迭代。

两个选项语义一致、独立生效，分别作用于 Cube 侧与 Vector 侧的循环粒度调整，trip count 越大则每次迭代处理的数据量越小。

---

## 【公式解读】

**原文无公式**。

文档中包含 MLIR 代码片段（变换前/变换后的 `scf.for` 嵌套结构），但未包含任何数学公式、伪代码公式或 LaTeX 表达。

---

## 【关联】

- **上游/前置阅读**：[CV Optimization](./cv_optimization.md)
  - 文档在开篇明确建议读者先阅读此文档以了解 CV 编译相关术语（如 CV Pipelining、MIX 算子等），属于本文的前置知识依赖。
- **所属 Pass**：TileCubeVectorLoop Pass，归属 **HIVM** 模块。
- **作用对象**：MIX 算子中已通过 **CV Pipelining** 完成软件流水的 Cube 与 Vector 循环，说明其上游流程为 CV 软件流水相关 Pass；下文 CopyOut 操作、mmadL1、fixpipe 等均为 HIVM/CV 流水线中的关键操作。
- **下游/后续**：文档明确提到当前尚未考虑 L1 空间大小约束，后续会结合 **生命周期分析（liveness analysis）** 决定 Cube 侧的 Tiling 策略。
- **配套图形**：原文配有 `figures/TileCubeAndVectorLoop.png`（Effect of using Tile Cube and Vector Loop）展示变换效果。

---

## 【使用方法】

**启用方式（基于原文「编译选项」章节）**：

- 默认状态下（`tile-mix-cube-loop=1`、`tile-mix-vector-loop=1`）**不生效**，Pass 不会对 Cube/Vector 循环做 Tiling。
- 若希望启用切分，需将对应选项调为 **大于 1** 的值：
  - 仅启用 Cube 循环 Tiling：调大 `tile-mix-cube-loop`
  - 仅启用 Vector 循环 Tiling：调大 `tile-mix-vector-loop`
  - 同时启用两侧：同时调大两个选项
- 该数值表示 Tiling 后子循环的目标 trip count（每次内层循环期望的迭代次数），数值越大单次迭代处理的数据越小。

**使用约束**（原文「使用约束」章节，原文内容如下要点）：

1. 仅处理携带 `hivm.loop_core_type` 属性的 `scf.for`，属性值需为 `#hivm.tcore_type<CUBE>` 或 `#hivm.tcore_type<VECTOR>`。
2. Vector 计算：Tiling 后切块大小 **小于 UB 对齐大小** 时不做 Tiling。
3. Cube 计算：Tiling 前切块大小 **小于 L0C 总大小** 时不做 Tiling。
4. 已知风险：当前未考虑 L1 空间大小约束，部分场景可能出现 **L1 Memory Overflow** 报错。

> 原文未提供具体的命令行调用示例、CMake 选项写法或运行时 API，启用方式以上述两个编译选项为唯一入口。

## 图文联合解读

- `TileCubeAndVectorLoop.png`: **图文解读：**

图左侧展示"CV Pipelining后"状态：4个GM workspace块，AIC与AIV各有频繁的写读箭头（红色实线与黑色虚线交错）。右侧展示"Tiling后"：每个workspace被切分为两块（0,0; 1,1; 2,2; 3,3），箭头密度减半，块大小翻倍。

**论证结论：** Cube tiling=2将单次迭代粒度增倍，使数据可容纳于L0C/UB本地缓冲，从而把AIC↔AIV核间同步通信频率减半。

**与文档对应：** 直接佐证"减少核间同步、增大切分粒度"两大设计目标，用最直观的箭头数量对比量化同步开销的下降。
