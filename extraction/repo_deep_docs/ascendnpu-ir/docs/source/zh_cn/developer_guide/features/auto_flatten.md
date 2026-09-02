# 自动展平

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/developer_guide/features/auto_flatten.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/developer_guide/features/auto_flatten.md

【定位】
本篇文档描述 AscendNPU-IR 编译器中的 **Auto Flatten Pass（HIVMFlattenOps）** 能力——它将多维张量操作自动折叠为低维等价形式以降低 rank，从而简化内存访问模式、提升昇腾加速器上的硬件利用率与 DMA/寄存器效率。

【技术要点】
- **Pass 入口**：`mlir::hivm::createFlattenOpsPass()`，通过 `pm.addPass(...)` 接入 Pass 流水线。
- **三阶段流水线**：(1) 单元维度折叠（Unit Collapse）→ (2) 均匀重关联折叠（Uniform Reassociation Collapse）→ (3) 结果组合（Compose Results），最终插入 `memref.collapse_shape` 并克隆操作。
- **维度三值掩码**：每个维度标记为 `U`（Unit，size=1，被吸收）、`C`（Collapsible，可合并）、`N`（Non-collapsible，屏障维度），掩码构建由 `strictBarrierWithUnit` 等选项控制。
- **重关联映射（Reassociation Maps）**：以分组数组描述原维度到折叠后维度的映射，例如 `[[0,1], [2], [3,4]]` 把 rank 5 折叠为 rank 3。
- **FlattenInterface 接口**：操作需实现 `getFlattened(FlattenOptions)` 与 `adjustTargetDimensions(OpBuilder, FlattenResult)` 两个虚方法才能参与展平。
- **FlattenOptions 三项开关**：`strictBarrierWithUnit`（默认 false）、`checkMarkStride`（默认 false）、`checkInputConsistency`（默认 false，广播前验证输入一致性）。
- **支持的操作属性调整**：`VBrcOp`（`broadcast_dims`）、`VReduceOp`（`reduce_dims`）、`VTransposeOp`（`permutation`）、`VCumsumOp/VCumprodOp`（`cum_dims`）、`VPadOp`（`static_low`/`static_high`）、`VConcatOp`（`dim`）、`VFlipOp`（`flip_axis`）、逐元素操作（`iterator_types`）。
- **关键约束**：仅支持 `MemRefType`（需先 bufferize）、要求静态形状（需先跑符号方言/形状推断）、`VFlipOp` 必须 `strictBarrierWithUnit=true`、最后一个维度对部分操作不可 OTF 转置。

【关键机制与数据】
**工作原理**（原文）：
1. 算法对每个操作构造三值掩码 `mask[i] ∈ {Unit, Collapsible, NonCollapsible}`；判定规则在原文 `Mask building logic` 代码段中：`strictBarrierWithUnit && isBarrier[i]` → `NonCollapsible`；`isUnit[i] && !isBarrier[i]` → `Unit`；其余 → `Collapsible`。
2. 掩码按段处理生成 ReassociationMap，例如输入掩码 `[U, C, U, N, U, C, U]` 产出 `[[0,1,2], [3], [4,5,6]]`（原文示例）。
3. 转置 OTF 特殊路径：原文给出 6D 输入 `[A,B,C,D,E,F]`、置换 `[2,3,0,4,1,5]`、输出 `[C,D,A,E,B,F]`，步骤为：输入单元折叠 → 由逆置换推导置换块 → 分别为 input/init 生成重关联 → 在保持置换语义下组合。
4. **硬件收益定性对比**（原文表格）：地址计算（多次乘加→线性寻址）、内存合并（复杂步长→连续展平）、硬件循环（嵌套多→嵌套少）、DMA 效率（多描述符→批量）、寄存器压力（多索引变量→少）。
5. **示例场景数据**（原文）：5D 逐元素操作 shape `[1,64,1,128,256]`，展平前 5 层嵌套循环；展平后变为 `[64,128,256]` 或进一步为 `[64,32768]`。

【表格解读】

**表 1：高秩影响 vs 展平收益（原文表格，逐字还原）**

| 方面 | 高秩的影响 | 展平的收益 |
| ----------------------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| 地址计算 | 多维索引需要多次乘加运算 | 简化的线性寻址降低了开销 |
| 内存合并 | 复杂的步长模式可能阻碍高效内存访问 | 连续的展平维度实现更好的合并 |
| 硬件循环 | 硬件循环计数器数量有限 | 维度更少 = 所需循环嵌套更少 |
| DMA效率 | 多步长传输可能需要多个DMA描述符 | 折叠维度实现批量传输 |
| 寄存器压力 | 更多的索引变量占用寄存器 | 减少簿记开销 |

逐行解读：表格列出 5 个硬件维度，每行指出"高 rank 带来的负面效应"与"展平后获得的正面效应"。核心思想是：折叠维度能让地址计算线性化、内存访问连续化、循环嵌套减少、DMA 描述符合并、索引变量数降低——这些共同决定了展平 Pass 在昇腾硬件上的实际加速效果。

**表 2：维度分类三值掩码（原文表格，逐字还原）**

| 类别         | 符号 | 描述          | 折叠行为                   |
| ------------ | ---- | ------------- | -------------------------- |
| 单元维度     | `U`  | 大小为1的维度 | 被吸收到相邻组中           |
| 可折叠维度   | `C`  | 可与邻居合并  | 形成组，吸收相邻单元维度   |
| 不可折叠维度 | `N`  | 屏障维度      | 独立存在，阻止单元维度吸收 |

逐行解读：`U` 表示 size=1 的维度，可被吸收到相邻非屏障组；`C` 表示可与邻居合并的维度，能形成组并吸收相邻单元维度；`N` 是屏障维度，必须独立保留以维持归约/广播/置换语义。该三值分类是流水线阶段 1 单元折叠的判定基础。

**表 3：支持的操作调整（原文表格，逐字还原）**

| 操作 | 调整的属性 |
| -------------------------- | --------------------------------------------- |
| `VBrcOp` | `broadcast_dims` |
| `VReduceOp` | `reduce_dims` |
| `VTransposeOp` | `permutation` |
| `VCumsumOp` / `VCumprodOp` | `cum_dims` |
| `VPadOp` | `static_low`、`static_high` |
| `VConcatOp` | `dim` |
| `VFlipOp` | `flip_axis` |
| 逐元素操作 | `iterator_types`（broadcast/transpose数组） |

逐行解读：每种 HIVM 操作折叠后必须同步调整其语义属性，否则会产生错误 IR。例如 `VBrcOp` 折叠后原 `broadcast_dims` 索引会改变（原文示例展示 `[3] → [0]` 的重映射），需要通过 `adjustTargetDimensions` 重新计算索引。

**表 4：能力清单（原文表格，逐字还原）**

| 特性 | 描述 |
| ------------------------------- | ------------------------------------------------------------ |
| 单元维度折叠 | 自动移除大小为1的维度 |
| 连续性感知 | 遵守内存布局；非连续维度保持独立 |
| 操作特定处理 | 针对归约、广播、转置、填充等的自定义逻辑 |
| 流水线组合 | 多个折叠阶段可正确组合 |
| 均匀重关联 | 所有操作数折叠方式相同时的高效处理 |
| 非均匀重关联 | 支持不同的输入/init重关联（转置OTF） |
| 屏障保护 | 语义关键维度保持独立 |
| 跳过Host函数 | 自动跳过Host侧函数 |

逐行解读：列出 Pass 的 8 项能力；其中"均匀重关联"由 `OpTrait::UniformReassociationFlattenTrait` 标识，对应优化路径；"非均匀重关联"对应转置 OTF 特殊路径。

**表 5：限制与规避方案（原文表格，逐字还原）**

| 限制 | 描述 | 规避方案 |
| ---------------------------- | --------------------------------------------------------- | ------------------------------------------------------- |
| 仅支持MemRef类型 | 只折叠`MemRefType`操作数 | 张量必须先进行缓冲化（bufferize） |
| 需要静态形状 | 动态维度可能无法正确折叠 | 优先运行符号方言或形状推断Pass |
| 严格屏障模式 | `VFlipOp`需要`strictBarrierWithUnit=true` | 自动处理 |
| 转置后向维度 | 某些操作的最后一个维度不能进行OTF转置 | 算法保留最后一个维度不折叠 |
| 非HIVMStructuredOp | 未实现接口的操作返回恒等映射 | 实现`FlattenInterface` |

逐行解读：给出 5 条工程约束及对应缓解策略；最关键的工程要求是"先 bufferize 再展平"以及"先形状推断再展平"，否则 Pass 会因输入是 tensor 或动态维度而无法生效。

【公式解读】

**公式 1（掩码构建逻辑，原文伪代码）**：
```cpp
for each dimension i:
    if (strictBarrierWithUnit && isBarrier[i]):
        mask[i] = NonCollapsible    // 严格模式：屏障维度独立
    else if (isUnit[i] && !isBarrier[i]):
        mask[i] = Unit              // 单元维度被吸收
    else:
        mask[i] = Collapsible       // 可形成组
```
符号说明：
- `i`：维度下标，遍历所有维度；
- `strictBarrierWithUnit`：布尔选项，`FlattenOptions` 字段；为 true 时即使是单元维度旁的屏障也强制保留；
- `isBarrier[i]`：判定该维度是否属于屏障（归约/广播/置换关键维度）；
- `isUnit[i]`：判定该维度大小是否为 1；
- `mask[i]`：输出三值之一 `Unit`/`Collapsible`/`NonCollapsible`。

**公式 2（Reassociation 重关联示例，原文）**：
```text
Original shape: [A, B, C, D, E] (rank 5)
Reassociation:  [[0, 1], [2], [3, 4]]
Result shape:   [A*B, C, D*E] (rank 3)
```
符号说明：
- `A, B, C, D, E`：原维度大小（符号占位）；
- `Reassociation`：分组数组，每个子数组对应折叠后一个新维度，子数组内是原维度下标的集合；
- `Result shape`：`A*B, C, D*E` 表示第 0 维由原 0、1 维相乘得到，第 1 维保留原 2 维，第 2 维由原 3、4 维相乘得到；rank 由 5 降至 3。

**公式 3（转置 OTF，原文）**：
```text
Input shape:   [A, B, C, D, E, F]
Permutation:   [2, 3, 0, 4, 1, 5]
Output shape:  [C, D, A, E, B, F]
```
符号说明：
- `A~F`：6 个输入维度；
- `Permutation`：置换向量，含义为输出第 `i` 维对应输入第 `Permutation[i]` 维；
- `Output shape`：经置换后的输出维度顺序；
- 文中"Step 1~4" 表明：在 OTF 场景下算法先对 input 折叠，再由 `inverse(Permutation)` 推导置换块，最后分别为 input 与 init 生成独立的重关联图，并在组合阶段维持置换语义。

【关联】
- 文中提及 `memref.collapse_shape` 作为折叠产物的插入操作——它属于 MLIR MemRef 方言的标准折叠原语，是展平 Pass 在 IR 层落地折叠结果的载体。
- 文中提及 `DpsKind`（出现在 `FlattenResult::getOperandTypes(DpsKind kind)` 中），暗示其与 HIVM 的"Destination-Passing Style"语义建模相关，与归约/逐元素等操作数分类有关。
- 文中提及 `OpTrait::UniformReassociationFlattenTrait` 与 `OpTrait::CollapsibleConsecutiveTargetDimsTrait` 两个操作 Trait，它们通过 Operation 特质机制声明哪些操作支持均匀折叠、哪些可折叠连续目标维度，是 Pass 在 op 粒度上识别可折叠候选的依据。
- 文中提及 "优先运行符号方言或形状推断 Pass" 作为动态形状问题的规避方案，说明该 Pass 通常与符号执行 / shape inference 类 Pass 形成流水线前置依赖。
- 文中提及 "张量必须先进行缓冲化（bufferize）"，表明本 Pass 处于 bufferize 之后的下游。
- 文中提及 `LDBG` 调试宏，可追踪每阶段重关联、掩码分类、调整后的目标维度及组合结果。
- 内部链接：原文未提供任何内部链接信息。

【使用方法】
启用方式与配置项（原文有）：
1. **Pass 注册与使用**：
```cpp
std::unique_ptr<Pass> mlir::hivm::createFlattenOpsPass();
pm.addPass(mlir::hivm::createFlattenOpsPass());
```
2. **`FlattenOptions` 三项开关**（均默认 `false`，可按需打开）：
   - `strictBarrierWithUnit`：`VFlipOp` 必须置 `true`；
   - `checkMarkStride`：启用步长注释对齐检查；
   - `checkInputConsistency`：用于广播场景的输入形状一致性验证。
3. **调试**：使用 `LDBG` 宏启用调试日志，可查看每个阶段的重关联映射、掩码分类、调整后的目标维度与组合结果。
4. **前置 Pass 要求**：bufferize（保证 MemRefType）+ 形状推断/符号方言（保证静态形状），否则 Pass 会因输入不满足前提而无法生效。
5. **跳过条件**：`isIdentityCollapse()` 返回 true 时报告 `matchFailure`；未实现 `FlattenInterface` 的非 HIVMStructuredOp 自动跳过（返回恒等映射）。
