# Auto-Subtiling

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/AutoSubtiling/AutoSubtiling.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/AutoSubtiling/AutoSubtiling.md

# Auto-Subtiling 文档深度解读

## 【定位】

本文档描述了 HIVM（昇腾向量机中间表示）中的 **AutoBindSubBlock Pass**，该 Pass 通过 **Cube–Vector 1:2 subtiling**（子块切分）策略，自动优化 Cube-Vector (CV) 融合算子的计算效率与昇腾亲和性，解决用户手写算子与社区算子通常未实现 1:2 子块逻辑而导致的硬件算力浪费问题。

---

## 【技术要点】

1. **硬件背景**: 昇腾芯片架构中 AIC（Cube 核）与 AIV（Vector 核）以 **1:2** 的核数比分离部署，AIV 之间无直连数据通路，需要通过 subtile 在并行轴上拆分以保证各 tile 独立计算。

2. **整体算法 4 步走**: ① 用 extract-slice + for-loop 将 Store 数据**对半分**；② 通过 BubbleUpExtractSlice pattern **上浮** extract-slice；③ 将 for-loop **映射到 subblock**；④ subtiling 成功。若任一步失败，编译器**自动回退到 1:1** 以保证正确性。

3. **示例张量维度**: 输入张量 `tensor<64xf16>`，经过 1:2 切分后变为 `tensor<32xf16>`（即按所选轴切为长度 32 的两片）。

4. **Dimension Analyzer（维度分析器）**: 通过分析目标 kernel 中的全部算子，**选择一条并行轴**作为切分轴；选轴原则是**避免跨 tile 数据依赖**，使每个 tile 可在独立向量核上独立计算。

5. **BubbleUp Extract Slice 支持的算子类型**: `BroadcastOp`、`ReduceOp`、`ExpandOp`（特定 shape）、`CollapseOp`（特定 shape）、`ElementwiseOp`、`LoopOp`、`ExtractSliceOp`（特定情形）、`InsertSliceOp`（特定情形）；可通过新增 `matchAndRewrite` pattern 扩展更多算子。

6. **接口控制**: 通过命令行开关控制行为，默认值与语义为：
   - `--enable-auto-bind-sub-block=True`（默认）— 启用该 feature
   - `--enable-auto-bind-sub-block=False` — 禁用切分，但 Pass 仍运行，AIV 仅在 sub-block 0 上工作
   - `--skip-hivm-bind-sub-block-pass=True`（默认 False）— 完全跳过 `hivm-bind-sub-block` Pass

7. **回退条件**: ① 轴选择失败（无有效并行轴可切）；② BubbleUpExtractSlicePattern 遇到不支持的算子。

---

## 【关键机制与数据】

**1:2 切分的数据流（原文示例逐字保留）：**

- **原始（未切分）IR**：
  ```mlir
  %t0 = hivm.hir.vexp ins(%src: tensor<64xf16>)
                       outs(%init: tensor<64xf16>) -> tensor<64xf16>
  %t1 = hivm.hir.vabs ins(%t0: tensor<64xf16>)
                       outs(%init: tensor<64xf16>) -> tensor<64xf16>
  hivm.hir.store ins(%t1: tensor<64xf16>) outs(%output : memref<64xf16>)
  ```
  流程：`src → vexp → vabs → store → output`，全程在 `tensor<64xf16>` 上完成。

- **Auto 1:2 成功后的 IR**：
  ```mlir
  %0 = hivm.hir.get_sub_block_idx -> i64
  %slice_src = tensor.extract_slice %src[%0][32][1] : tensor<64xf16> to tensor<32xf16>
  %t0 = hivm.hir.vexp ins(%slice_src: tensor<32xf16>)
                       outs(%new_init: tensor<32xf16>) -> tensor<32xf16>
  %t1 = hivm.hir.vabs ins(%t0: tensor<32xf16>)
                       outs(%new_init: tensor<32xf16>) -> tensor<32xf16>
  %output_slice = memref.subview %output[%0][32][1] : memref<64xf16> to memref<32xf16>
  hivm.hir.store ins(%t1: tensor<32xf16>) outs(%output_slice : memref<32xf16>)
  ```
  **关键变化**（原文标注）：
  - 通过 `hivm.hir.get_sub_block_idx` 取出 sub-block 索引 `%0`；
  - 对输入张量做 `tensor.extract_slice %src[%0][32][1]`，**offset/stride 由 sub-block 索引决定**，长度恒为 32；
  - 对输出 memref 做 `memref.subview %output[%0][32][1]`，同样按 32 长度切半；
  - 算子链内部张量全部由 `64xf16` 降为 `32xf16`，实现两份 sub-block 上的并行计算。

- **回退到 1:1 的 IR**：
  ```mlir
  %0 = hivm.hir.get_sub_block_idx
  %1 = arith.cmpi eq %0, %c0_cst
  scf.if %1 {
    %t0 = hivm.hir.vexp ins(%src: tensor<64xf16>)
                         outs(%init: tensor<64xf16>) -> tensor<64xf16>
    %t1 = hivm.hir.vabs ins(%t0: tensor<64xf16>)
                         outs(%init: tensor<64xf16>) -> tensor<64xf16>
    hivm.hir.store ins(%t1: tensor<64xf16>) outs(%output : memref<64xf16>)
  }
  ```
  回退语义（原文）：**只有 core 0 工作**——通过 `arith.cmpi eq %0, %c0_cst` + `scf.if` 让仅 sub-block idx 等于 0 的核执行完整 kernel。

**性能/效率数据**：原文未给出量化性能数字，仅以"提高计算效率与昇腾亲和性"作为定性结论（原文："To improve compute efficiency and Ascend affinity, the compiler needs automatic sub-block (subtiling) capability."）。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。文档中的"1:2"指的是 **AIC 核数 : AIV 核数 = 1 : 2** 的硬件比例，以及对应的 **数据切分比 1 : 2**（即 64 元素切为两份各 32 元素），这些是比例描述而非数学公式。算子中的 `[%0][32][1]` 是 MLIR 的 offset/size/stride 三元组（原文：`tensor.extract_slice %src[%0][32][1]`），不是公式。

---

## 【关联】

- **前置阅读**: 文档开头明确建议读者先阅读 **CV Optimization** 文档以理解相关术语（原文："Before reading this document, you are advised to read CV Optimization to understand its terms."）。
- **所属模块**: 本特性属于 **HIVM**（Heterogeneous Intermediate Representation for Vector Machine）中的 Pass 实现，与文档路径 `docs/source/en/developer_guide/features/AutoSubtiling/` 一致，位于「Developer Guide → Features」层级。
- **上下游 Pass 关系**:
  - 与 `hivm-bind-sub-block` Pass 直接耦合，可通过 `--skip-hivm-bind-sub-block-pass=True` 完全跳过该 Pass；
  - 该 Pass 在 `--enable-auto-bind-sub-block=False` 时仍会运行，但只让 sub-block 0 实际执行 AIV 工作。
- **依赖的 MLIR/HIVM 算子**:
  - 使用 `tensor.extract_slice`、`memref.subview` 完成数据切分；
  - 使用 `hivm.hir.get_sub_block_idx` 获取 sub-block 索引；
  - 使用 `scf.if` + `arith.cmpi` 实现回退时的"只让 core 0 工作"语义；
  - 上浮 pattern 作用于 `BroadcastOp`/`ReduceOp`/`ExpandOp`/`CollapseOp`/`ElementwiseOp`/`LoopOp`/`ExtractSliceOp`/`InsertSliceOp` 等异类算子。
- **内部链接**: 文末标注"（无）"，文档未给出其他内部链接。

---

## 【使用方法】

通过编译器命令行开关启用/禁用，原文给出三条命令（原文逐字保留）：

| 命令行开关 | 取值与默认值 | 作用（原文） |
|---|---|---|
| `--enable-auto-bind-sub-block=True` | 默认 `True` | 启用该 feature |
| `--enable-auto-bind-sub-block=False` | 显式 `False` | 禁用该 feature；Pass **仍会运行**，仅切分关闭，AIV 工作被限制在 sub-block 0 |
| `--skip-hivm-bind-sub-block-pass=True` | 默认 `False` | **完全省略** `hivm-bind-sub-block` Pass；仅在该 Pass 本身**不能运行**时使用 |

**回退机制**（原文）：无需用户额外配置——若 subtiling 失败或中间变换失败，编译器自动回退到 1:1（原文："If subtiling or an intermediate transformation fails, the compiler automatically falls back to 1:1 to preserve correctness."）。

## 图文联合解读

- `cvarch.png`: **1) 图示内容**：AICore 内部呈左右分区结构。左侧黄色为 AIC，含 Cube 单元、FixPipe、L0/L1 缓冲；右侧蓝色为 AIV，含 Vector 单元、UB 缓冲；底部为共享 HBM。箭头标注 Cube↔L0、FixPipe↔L0/L1↔HBM、Vector↔UB 的数据流向，二者无直接互连通路。

**2) 技术结论**：AIC 与 AIV 是两套独立的计算/存储子系统，仅通过 HBM 交互；Cube 走 L0/L1+FixPipe，Vector 走 UB，访存路径分离。

**3) 与文档论点的关系**：图直观支撑"AIC、AIV 以 1:2 比例分离"这一硬件事实，说明 CV 协同需跨核通信开销，因此自动 subtiling 将任务按 1:2 拆分以匹配架构、提升亲和性。
- `auto_subtiling2.png`: 图分三栏：User Input为Triton混合代码块；Split Cube-Vec按1:1拆为Cube+Vec，aic做matmul 64×64、aiv做vadd 64×64；Auto-Subtiling将Vec细分为Vec2双子块（1:2），aiv1与aiv2各处理32×64。论证自动子块切分使AIC:AIV匹配Ascend硬件1:2核比，提升算力利用率，与文档CV 1:2 tiling优化论点直接对应。
- `auto_subtiling3.png`: **图文联合解读**

图中并列展示两种CV配比：上为"CV 1:1"，1个Cube0搭配1个等宽Vec0；下为"CV 1:2"，1个Cube0搭配两个较小Vec0/Vec1。标注"Reduce synchronizations between CV"。

论证结论：1:2 subtiling将单Vec拆为双Vec子块，使Cube与Vector计算更细粒度并行，减少Cube-Vector间的同步等待。

与文档关系：直接呼应"AIC:AIV=1:2"的硬件架构及"CV 1:2 subtiling策略"，为AutoBindSubBlock Pass提供动机图。
- `auto_subtiling4.png`: 图示AutoBindSubBlock流程：输入内核依次经Tile And Slice Store→BubbleUpExtractSlice→Map Loop to Subblock三阶段完成CV 1:2 subtiling。若开关--enable-auto-bind-sub-block=False或在tile/bubble阶段失败，则沿右侧分支回退至"Back to 1:1"。该图论证了**级联判定+回退**机制：编译器逐步尝试自动分块，任一前置条件不满足即降级为1:1映射以保证正确性。与文档"Algorithm Principle"段直接对应，并呼应"Hardware Background"——非亲和算子无法手工实现1:2时，由编译器兜底回退。
