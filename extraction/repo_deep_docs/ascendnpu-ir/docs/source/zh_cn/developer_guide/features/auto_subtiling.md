# 自动子块切分

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/auto_subtiling.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/auto_subtiling.md

# AutoBindSubBlock（自动子块切分）深度解读

---

## 【定位】

这篇文档描述了 HIVM（HIVM 是 AscendNPU-IR 中面向昇腾亲和算子编译的子模块）中的 **AutoBindSubBlock Pass**——一种针对 CV（Cube-Vector）类 kernel 自动应用 **Cube-Vector 1:2 分核**策略的能力，用于在用户/社区算子未显式编写分核逻辑时，由编译器自动插入数据切分以提升昇腾亲和性与计算效率。

---

## 【技术要点】

1. **硬件架构前提**：昇腾 AI 加速芯片中 **AIC 与 AIV 分离**，**核数比为 1:2**——即每 1 个 Cube 核搭配 2 个 Vector 核；Vector 核之间**不存在直接数据通路**。
2. **核心机制：Cube-Vector 1:2 自动切分**：对 Vector 类算子（如 `vexp`、`vabs`）的输入与输出沿"平行轴（Parallel Axis）"对半切分（`64xf16` → `32xf16` × 2），使两份子片可被独立分配到两个 Vector 核上并行处理。
3. **四步实现思路**：
   ① 通过 `extract-slice` 和 `for-loop` 对 Store 数据**对半切分**；
   ② 通过 `BubbleUpExtractSlice` Pattern 把 extract slice 沿数据流**向上冒泡**；
   ③ 将 `for-loop` **映射到 subblock**；
   ④ 切分成功即收尾；**切分失败则回退到 1:1**（仅 0 核工作），保证功能正确性。
4. **选轴算法（Dimension Analyzer）**：综合分析 Kernel 内**所有 Operator**，识别并选定一个**平行轴**作为数据切分维度——其依据是 Vector 核之间无直连数据通路，故所选维度必须**严格避免引入跨分片数据依赖**。
5. **冒泡策略（BubbleUp Extract Slice）支持的 Op 类型**：`BroadcastOp`、`ReduceOp`、`ExpandOp`（特定 Shape）、`CollapseOp`（特定 Shape）、`ElementwiseOp`、`LoopOp`、`ExtractSliceOp`（特定场景）、`InsertSliceOp`（特定场景），并支持通过新增 `matchAndRewritePattern` 扩展更多 Op 类型。
6. **关键 IR 原语**：`hivm.hir.get_sub_block_idx`（获取当前 sub block 索引 i64）、`tensor.extract_slice`（沿选轴切出 `32` 长度的子张量）、`memref.subview`（对输出 memref 做对应切分），以及回退路径上的 `arith.cmpi eq %0, %c0_cst` + `scf.if` 包裹。

---

## 【关键机制与数据】

### 整体数据流（自动 1:2 成功路径）

- **原文**：原始 IR 中，64 长度的 `vexp`、`vabs` 串联后通过单个 `hivm.hir.store` 写回 `memref<64xf16>`。
- **原文**：自动切分后，先通过 `%0 = hivm.hir.get_sub_block_idx -> i64` 拿到 sub block 索引；再以索引 `%0` 作为 `offset`、`32` 作为 `length`、`1` 作为 `stride`，对源张量 `tensor.extract_slice` 出 `tensor<32xf16>`，对输出 memref 用 `memref.subview` 切出 `memref<32xf16>`；中间 `vexp`、`vabs` 的 `ins`/`outs` 都改为 32 长度类型。
- **原文**：由此两份子片分别落在 sub block 0、sub block 1 上独立运算、互不通信。

### 回退数据流（1:1 路径）

- **原文**：当 `hivm.bind_sub_block` 进入 `if` 判断分支时，使用 `%0 = hivm.hir.get_sub_block_idx` 与 `%c0_cst` 做 `arith.cmpi eq` 比较，仅当等于 0 时进入 `scf.if` 体执行原始 64 长度计算——即**仅 0 核工作**，保证切分失败时功能等价于原始代码。

### 性能/效果来源（原文未给量化数据）

- 原文仅以文字 + 示意图描述"带来的效果"（即两份独立子片并行），未提供具体加速比、吞吐、时延等数字，故此处**不臆造**。

---

## 【表格解读】

**原文无表格**。原文以 MLIR 代码块和示意图（`cvarch.png`、`auto_subtiling2.png`、`auto_subtiling3.png`、`auto_subtiling4.png`）呈现输入/输出样例与流程，无参数表或性能对比表。

---

## 【公式解读】

**原文无公式**（无 LaTeX 表达式或伪代码形式的公式定义）。涉及到的"切分尺寸 `32`"、`stride=1` 等数值均以 MLIR 操作数形式出现在代码块中（如 `%slice_src = tensor.extract_slice %src[%0][32][1] : tensor<64xf16> to tensor<32xf16>`），并非形式化公式。

---

## 【关联】

- **依赖前置阅读**：文档开篇明确建议"在阅读本文之前，建议先阅读 [CV Optimization](./cv_optimization.md)，了解 CV 编译相关术语"。该特性建立在 CV 编译流水线的术语与抽象之上（`Leaf`/`StoreOp`/`ElementwiseOp` 等概念属 CV 域）。
- **所属模块**：本文特性位于 **HIVM**（属于 AscendNPU-IR / MLIR 体系），具体 Pass 名为 `AutoBindSubBlock`（文档亦提到 `hivm-bind-sub-block` Pass），作用于 HIVM 的 HIR（HIVM Intermediate Representation）。
- **上游 / 下游关系**：
  - 上游为产生原始 `vexp`/`vabs` 等 Vector 算子的前端/算子生成阶段；
  - 下游衔接 Cube-Vector 协同调度与昇腾亲和代码生成（与 AIC:AIV 1:2 拓扑对齐）；
  - 失败时回退到 1:1 等价于"不切分、仅 0 核运行"的串行语义，作为安全网嵌入到 Pass 内部。

---

## 【使用方法】

文档明确给出以下三个 CLI 选项：

| 选项 | 取值 | 行为（原文表述） |
|---|---|---|
| `--enable-auto-bind-sub-block` | `True`（**默认**） | 启用 1:2 自动切分特性 |
| `--enable-auto-bind-sub-block` | `False` | 关闭切分；**Pass 仍会运行**，并将 AIV 工作**限制在子块 0 上** |
| `--skip-hivm-bind-sub-block-pass` | `True`（默认 `False`） | **完全跳过** `hivm-bind-sub-block` Pass；仅在该 Pass 本身不应运行时使用 |

**回退保证**：若选轴分析失败（无可切分平行轴）或 `BubbleUpExtractSlicePattern` 遇到不支持的 Op，会自动回退到 1:1 以保证功能正确性，**无须用户额外配置**。

## 图文联合解读

- `cvarch.png`: 1) **图示内容**：描绘AICore内部硬件结构，分为黄色AIC区（含Cube计算单元、FixPipe及L0/L1缓存）和蓝色AIV区（含Vector单元与UB），二者并列于AI Core内，并通过FixPipe与下方共享HBM进行数据交互。

2) **技术结论**：AIC与AIV在物理上分离、各自拥有独立存储层级与运算单元，二者核数呈1:2比例关系，需通过显式切分才能实现并行利用。

3) **与文档关联**：该图直接支撑"AIC与AIV分离、核数1:2"的硬件背景论点，是AutoBindSubBlock Pass对CV类kernel自动按1:2策略切分子块、避免用户手工分核的硬件依据。
- `auto_subtiling2.png`: **图文联合解读：**

1) **图示内容**：横向三栏对比。上方"示意图"展示三种处理形态——User Input为单一灰色混合块；Split Cube-Vec拆分为黄色Cube（顶部）与蓝色Vec（底部），标注1:1；Auto-Subtiling则在Cube下方显示两个蓝色Vec2块（1:1但Vec被切两半）。下方"伪代码"对应：Triton原`matmul_add_kernel`（load→dot→add→store）→手工拆分后`aic`做64×64 matmul、`aiv`做64×64 vadd → Auto-Subtiling后`aic`仍64×64 matmul，`aiv1`与`aiv2`各做32×64 vadd，红框标注数据维度减半。

2) **技术结论**：编译器可自动将单一Vector任务沿数据维度对半拆分到两个Vector核执行，而Cube核负载保持不变，实现Cube-Vector 1:1基础配比下Vector侧的"1拆2"并行。

3) **与文档关系**：对应"算法原理"中Cube-Vector 1:2分核策略及"输入输出样例"的`extract_slice`对64→32维切分思想，论证AutoBindSubBlock Pass无需手工切分即可获得双Vector核并行收益。
- `auto_subtiling3.png`: **1) 图中内容：** 对比两种CV核分配。上图"CV 1:1"：1个Cube0（黄）与1个Vec0（蓝）等宽并排；下图"CV 1:2"：1个Cube0（黄，缩小）与Vec0、Vec1（两个蓝块上下堆叠）。标注"Reduce synchronizations between CV"。

**2) 技术结论：** 将单一Vector核拆分为两个子块（1:2），可在同量Cube资源下并发更多Vector任务，减少Cube-Vector间的同步等待。

**3) 与文档关系：** 图示印证了"算法原理"中AutoBindSubBlock Pass的核心收益——通过自动1:2切分使CV类算子亲和昇腾AIC:AIV=1:2硬件架构，降低同步开销。
- `auto_subtiling4.png`: 图示：左侧为主流程，Input Kernel经Tile And Slice Store→BubblUpExtractSlice→Map Loop to Subblock→Succeed 1:2四步串行执行；右侧带"--enable-auto-bind-sub-block=False"标注的箭头从Input Kernel直连Back to 1:1，并在前两步标注"fail for tile"和"fail for bubble up"两条回退路径。论证：AutoBindSubBlock按四步流水线决策，任意一步失败或开关关闭即回退至1:1原始绑定。与文档论点对应：实现思路中的四个步骤一一映射，且佐证"切分失败返回1:1"的回退机制。
