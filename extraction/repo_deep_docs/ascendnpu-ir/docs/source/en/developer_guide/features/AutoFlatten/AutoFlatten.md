# Auto Flatten

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/AutoFlatten/AutoFlatten.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/AutoFlatten/AutoFlatten.md

# Auto Flatten 文档深度解读

## 【定位】

这篇文档描述了 **Auto Flatten 优化 Pass（`HIVMFlattenOps`）** 的工作机制——它能在保持算子语义正确性的前提下，将多维张量操作自动折叠（collapse）为低秩等价形式，以简化访存模式并提升昇腾加速器硬件利用率。

---

## 【技术要点】

1. **Pass 名称与核心作用**：自动折叠多维 tensor 操作到低秩等价形式，对应的 Pass 接口入口为 `mlir::hivm::createFlattenOpsPass()`。
2. **多阶段流水线算法**：分为三阶段——Stage 1 Unit Dimension Collapse、Stage 2 Uniform Reassociation Collapse、Stage 3 Compose Results；输入示例形态为 `[1, 64, 1, 128, 1, 256]`，最终坍缩为 `[64, 32768]`（rank 由 6 → 2）。
3. **维度三分类（Ternary Mask）**：每个维度被标记为 `U`（Unit，size=1）、`C`（Collapsible，可合并）或 `N`（NonCollapsible，屏障维度），三类在 mask 上有不同的折叠行为。
4. **屏障维度（Barrier Dimensions）**：reduce 维、broadcast 维、transpose 维三类不可合并；它们在 `strictBarrierWithUnit=true` 时即使本身是 unit 也被强制标记为 `N`。
5. **重关联映射（Reassociation Map）**：定义原始维度如何映射到折叠后维度，例如 `[[0,1,2], [3,4], [5]]` 表示 rank 5 → rank 3 的合并关系。
6. **可扩展接口（FlattenInterface）**：算子需实现 `getFlattened(FlattenOptions)` 与 `adjustTargetDimensions(...)` 两个虚方法才能参与自动折叠，并通过 `FlattenResult` 携带重关联、维度调整、barrier 追踪等信息。

---

## 【关键机制与数据】

### 数据流（原文示例）
- **输入**：shape `[1, 64, 1, 128, 256]` 的 5D elementwise 操作（原文："Consider a 5D elementwise operation on shape `[1, 64, 1, 128, 256]`"）。
- **中间过程**：
  - Stage 1 后：`Mask: [U, C, U, C, U, C]` → reassociation `[[0,1,2], [3,4], [5]]` → shape `[64, 128, 256]`
  - Stage 2 后：连续维度可继续合并 → `[[0], [1,2]]` → shape `[64, 32768]`
  - Stage 3 compose 后：最终 `[[0,1,2], [3,4,5]]` → shape `[64, 32768]`
- **输出**：插入 `memref.collapse_shape` 折叠每个 operand；clone 出新 op；调整 `reduce_dims`、`broadcast_dims` 等属性。

### 关键执行逻辑（原文 Mask Building Logic）
```
for each dimension i:
    if (strictBarrierWithUnit && isBarrier[i]):
        mask[i] = NonCollapsible
    else if (isUnit[i] && !isBarrier[i]):
        mask[i] = Unit
    else:
        mask[i] = Collapsible
```
即：**strict 模式下 barrier 强制隔离；unit 且非 barrier 被吸收；其余归为可合并组。**

### 性能动机（原文）
- 高 rank → 多维索引需要多次乘加（multiply-add），扁平化后线性寻址降低开销。
- 高 rank → 复杂 stride 阻碍内存合并访存；扁平后连续维度支持更好的 coalescing。
- 硬件 loop counter 数量有限，rank 降低意味着嵌套循环数减少。
- 多 stride 传输需多个 DMA descriptor；折叠后支持批量传输。
- 更多 index 变量占用 register，折叠后 bookkeeping 开销下降。

> 原文未提供具体性能数字（如加速比、cycle 数等），仅给出机理性说明。

---

## 【表格解读】

### 表格 1：Hardware Background 表格（原文逐字还原）

| Aspect | Impact of High Rank | Benefit of Flattening |
| --- | --- | --- |
| **Address Calculation** | Multi-dimensional indexing requires multiple multiply-add operations. | Simplified linear addressing reduces overhead. |
| **Memory Coalescing** | Complex stride patterns may hinder efficient memory access. | Contiguous flattened dimensions enable better coalescing. |
| **Hardware Loops** | The number of hardware loop counters is limited. | Fewer dimensions mean fewer loop nests required. |
| **DMA Efficiency** | Multi-stride transfers may require multiple DMA descriptors. | Collapsed dimensions enable bulk transfers. |
| **Register pressure** | More index variables consume registers. | Bookkeeping overheads are reduced. |

**逐行解读：**
- **Address Calculation（地址计算）**：高 rank tensor 多维索引 = 多个 stride 相乘相加，硬件上需多次 MAC；扁平化后变为线性寻址，少量加法即可完成 offset 计算。
- **Memory Coalescing（内存合并）**：复杂 stride 模式 → 相邻线程访问地址不连续 → coalescing 失败；扁平后维度连续 → 相邻线程访问相邻地址 → 提升带宽利用率。
- **Hardware Loops（硬件循环）**：硬件 loop counter 资源有限，rank 高时需多层嵌套循环；rank 降低后循环嵌套层数减少，循环展开/调度更灵活。
- **DMA Efficiency（DMA 效率）**：多 stride 传输需多份 DMA descriptor，占用 descriptor 资源且增加 setup 开销；折叠后单次 bulk transfer 即可完成。
- **Register pressure（寄存器压力）**：每多一个维度就需多一组 index/stride 寄存器；折叠后 bookkeeping 寄存器占用下降，可释放给计算使用。

---

### 表格 2：Dimension Classification（原文逐字还原）

| Category | Symbol | Description | Collapsing Behavior |
| --- | --- | --- | --- |
| **Unit** | `U` | Size-1 dimension | Absorbed into adjacent groups |
| Collapsible | `C` | Can be merged with neighbors | Forms groups, absorbs adjacent units |
| NonCollapsible | `N` | Barrier dimension | Isolated, blocks unit absorption |

**逐行解读：**
- **Unit（`U`）**：维度 size=1，本身不携带数据信息，可被合并进相邻的 `C` 组（或在 strict 模式下被 `N` 阻挡）。
- **Collapsible（`C`）**：可与相邻 `C` 合并成更大组，同时吸收两侧的 unit 维度；是合并的主体。
- **NonCollapsible（`N`）**：屏障维度，作为组边界隔断 unit 的吸收——即使两侧有 unit 也不会跨过 `N` 被合并。

---

## 【公式解读】

> 原文无 LaTeX 公式，但包含若干伪代码/示意图。下面**逐字保留原文代码块**并解释每个符号含义。

### 公式/伪代码 1：Reassociation Map 定义（原文）

```text
Original shape: [A, B, C, D, E] (rank 5)
Reassociation:  [[0, 1], [2], [3, 4]]
Result shape:   [A*B, C, D*E] (rank 3)
```

**符号说明：**
- `A, B, C, D, E`：原始 5 个维度的 size 变量。
- `[[0, 1], [2], [3, 4]]`：reassociation 索引列表，每个内层数组对应一个折叠后的维度。
- `[A*B, C, D*E]`：折叠后结果 shape——第 0 维 = A×B，第 1 维 = C，第 2 维 = D×E。
- 整体作用：将 rank 5 映射到 rank 3，保留乘积语义。

---

### 公式/伪代码 2：Mask Building Logic（原文）

```cpp
for each dimension i:
    if (strictBarrierWithUnit && isBarrier[i]):
        mask[i] = NonCollapsible // Strict mode: barriers isolated
    else if (isUnit[i] && !isBarrier[i]):
        mask[i] = Unit // Unit dims absorbed
    else:
        mask[i] = Collapsible // Can form groups
```

**符号说明：**
- `i`：维度索引（0-based）。
- `strictBarrierWithUnit`：`FlattenOptions` 字段，开启时 barrier 维度即使为 unit 也被强制设为 `NonCollapsible`。
- `isBarrier[i]`：当前维度是否为屏障（reduce/broadcast/transpose 维）。
- `isUnit[i]`：当前维度 size 是否为 1。
- `mask[i]`：输出分类，取值为 `Unit`/`Collapsible`/`NonCollapsible`。
- 优先级：strict barrier > unit & non-barrier > 其他（即默认 Collapsible）。

---

### 公式/伪代码 3：Reassociation Generation from Mask（原文）

```text
Input Mask: [U, C, U, N, U, C, U]

Processing:
  Segment 1: [U, C, U] → Group units with collapsible → [[0, 1, 2]]
  Segment 2: [N]       → Isolated non-collapsible    → [[3]]
  Segment 3: [U, C, U] → Group units with collapsible → [[4, 5, 6]]

Result: [[0, 1, 2], [3], [4, 5, 6]]
```

**符号说明：**
- `[U, C, U, N, U, C, U]`：7 个维度的 mask 序列。
- `Segment`：按 `N` 屏障切分的连续段；`N` 自身构成独立段。
- 在 `[U, C, U]` 这类段中：首尾的 `U` 被中间 `C` 吸收，整段合并为一个折叠组。
- `Segment 2 [N]`：屏障维度独成一组，索引 `[3]`。
- 最终 `[[0,1,2], [3], [4,5,6]]`：rank 7 → rank 3。

---

## 【关联】

> 文档内部链接：原文未提供内部链接（标注"内部链接: (无)"）。

文档中提到的上下游/相关模块（基于原文语义，非外推）：

- **`memref.collapse_shape` 操作**：Stage 3 输出阶段会为每个 operand 插入该 op 作为折叠实现机制（原文："Insert memref.collapse_shape for each operand"）。
- **`hivm` dialect**：Pass 注册于 `mlir::hivm::createFlattenOpsPass()`，说明该 Pass 属于 `hivm` 方言的算子优化管线。
- **MLIR Pass Pipeline**：通过 `pm.addPass(...)` 接入通用 MLIR pass manager，与其他优化 Pass 串联。
- **`FlattenInterface` 算子 trait 系统**：所有希望参与自动折叠的 op 需实现该 interface；与 `FlattenOptions`（配置）和 `FlattenResult`（结果）三者构成完整的可扩展机制。
- **目标加速器（target accelerator）**：原文 Overview 提到"improves hardware utilization on the target accelerator"，指向 Ascend NPU 的硬件约束特性。

---

## 【使用方法】

### Pass 注册（原文 API 节）

```cpp
// 创建 flatten pass
std::unique_ptr<Pass> mlir::hivm::createFlattenOpsPass();

// 接入 pass pipeline
pm.addPass(mlir::hivm::createFlattenOpsPass());
```

### 算子接入方式（原文）

- 算子需实现 `FlattenInterface`，提供两个虚函数：
  - `FailureOr<FlattenResult> getFlattened(FlattenOptions options)`：根据配置计算本 op 的折叠结果。
  - `void adjustTargetDimensions(OpBuilder &builder, const FlattenResult &result)`：在折叠后调整 op 的目标维度属性。

### 关键配置项 `FlattenOptions`（原文）

| 字段 | 类型 | 默认值 | 作用 |
| --- | --- | --- | --- |
| `strictBarrierWithUnit` | `bool` | `false` | 为 true 时，barrier 维度即使 size=1 也被强制标为 NonCollapsible，阻止 unit 跨越 barrier 被吸收 |
| `checkMarkStride` | `bool` | `false` | 检查 stride annotation 以满足对齐要求 |
| `checkInputConsistency` | `bool` | `false` | 折叠前校验输入 shape 一致性（用于 broadcast 场景） |

### 结果查询 `FlattenResult`（原文）

提供的方法：`isIdentityCollapse()`、`getRankAfterFlatten()`、`getOperandTypes(DpsKind)`、`getInputReassociation()`、`getInitReassociation()`、`uniformReassociation()`，分别用于判断是否为恒等折叠、获取折叠后 rank、查询 operand 类型、获取输入/init 重关联、检查输入与 init 是否使用同一重关联。

### 命令行启用

> 原文未提供命令行 flag / 配置项 / 启用命令。

---

## 备注

原文在 **Operation Traits** 小节处被截断（以 `// Indicates operation uses same re` 结束），因此 `FlattenResult` 之后关于 operation trait 的进一步说明（如哪些 op 标记为 `uniform` 重关联等）**原文未提供完整内容**，本解读未做推断。
