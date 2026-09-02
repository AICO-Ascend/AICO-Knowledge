# Catlass 算子设计文档模板

> 仓 `agent-skills` · 路径 `community/Op/catlass-operator-design/references/design-document.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/community/Op/catlass-operator-design/references/design-document.md

# Catlass 算子设计文档模板 · 一体化深度解读

---

## 【定位】

本文是一份**标准化设计文档模板**，用于在「agent-skills / Catlass 算子」研发流程中，向下游 code-gen（`catlass-operator-code-gen`）客观传递**「选了什么组件、为什么选、怎么组装」**的设计决策，明确界定文档**不产出可编译代码**，代码细节全部交由 code-gen 完成。

---

## 【技术要点】

1. **职责分层**——设计文档仅做"选型 + 决策"（概念表格化），`catlass-operator-code-gen` 负责把表格实例化为模板参数；本文以一个 GEMM + GELU 融合算子为例，贯穿 BlockMmad / BlockEpilogue / BlockScheduler / Kernel 的完整组装链。
2. **目标硬件锁定 AtlasA2**——使用 `Arch::AtlasA2` 与 `MmadAtlasA2Pingpong`（`true` 表示开启 Pingpong 流水调度），L1TileShape `<128, 256, 256>`、L0TileShape `<128, 256, 64>`，块级分块三档尺寸与流水策略一并定标。
3. **算子契约解耦**——矩阵乘场景下，**禁止**依赖 InferShape / Tiling 中**通常不可见**的 `aclTensor stride` 推断是否做了逻辑转置；推荐用 **OpDef 布尔属性** `transpose_a` / `transpose_b` 声明，配合"属性 + 物理 shape → M、N、K"对照表与 aclnn 框架保证一致性。
4. **Kernel 三种形态**——根据是否带后处理选取：`Gemm::Kernel::BasicMatmul`（纯矩阵乘）/ `MatmulEpilogue`（矩阵乘 + 后处理）/ `MatmulActivation`（矩阵乘 + 激活）；统一组装为 `Kernel = Kernel类型<BlockMmad, BlockEpilogue, BlockScheduler>`。
5. **TilingKey 驱动特化**——Host 侧根据 dtype、transA、transB 等条件计算 TilingKey（如 0/1 两支），每个 key 对应一组**模板实例化**组合，Kernel 侧在 `TILING_KEY_IS` 分支内选择对应 `BlockMmad`（如 Pingpong 或 转置B）等特化版本。
6. **Epilogue 缺口的兜底链**——检索 [epilogue-components.md](./epilogue-components.md) 与 `catlass/include/catlass/epilogue/tile/` 后仍无匹配时，按 [custom-epilogue.md](./custom-epilogue.md) **单独**写明自定义 Tile 的名称、数学行为、`DispatchPolicy`（NoSource / OneSource / TwoSource）、`computeLength` 量级及与 `TileCopy` 的组装顺序，下游在 `op_kernel/custom_epilogue/*.hpp` 实现。

---

## 【关键机制与数据】

**工作原理 / 数据流（基于模板示例 GEMM + GELU 融合）**

原文工作机制描述按"组件表格 → 概念层组装 → Kernel 实例化"三段式：

- **数据流通道**：GM（Global Memory）→ 通过 `TileCopy` 搬入 UB → `TileElemWiseGelu` 计算 GELU → 再经 `TileCopy` 搬出 UB → GM。
- **分块粒度**：L1 级 `<128, 256, 256>` (M,N,K)，L0 级 `<128, 256, 64>` (M,N,K)；中间累加器 CType 用 `float` RowMajor 保精度。
- **调度**：`GemmIdentityBlockSwizzle<3, 0>`（offset=3, direction=0）。
- **Kernel 组装路径**：`using Kernel = Gemm::Kernel::BasicMatmul<BlockMmad, BlockEpilogue, BlockScheduler>;` 再由 `Kernel::Params{...}; Kernel kernel; kernel(params);` 调用。
- **Host Tiling 流程**：解析 shape → 计算 TilingKey → `SetTilingKey` → `SaveToBuffer`；`GET_TILING_DATA` 取 tiling 数据；`TILING_KEY_IS` 分支内实例化 Kernel。
- **Workspace**：临时中间存储（如 SplitK 的 Reduce），从 `kernel/*.hpp` 的 `GetWorkspaceSize` 移植大小计算。

**原文示例性能/数值数据**：原文未提供具体带宽、吞吐、时延或利用率数字，**无任何实测性能数据**。

---

## 【表格解读】

> 下列表格按原文**逐字还原**（模板示例列亦保留），每张表后给出逐行解读。

### 表 1 · 概述

| 项 | 内容 |
|----|------|
| 算子功能 | 一句话描述（如：矩阵乘 + GELU 融合） |
| 数学公式 | $D = \text{GELU}(A \times B)$ |
| 使用场景 | 说明适用的模型或场景 |

**解读**：模板的"封面页"。算子功能用一句话定位；数学公式列以 `$D = \text{GELU}(A \times B)$` 表达"先矩阵乘、再 GELU 激活"的两阶段语义；使用场景要求写明适用模型或推理/训练阶段。`如：矩阵乘 + GELU 融合` 是**示例占位文本**，正文需替换为该算子的真实描述。

### 表 2 · 输入输出信息表

| 变量名 | 数据类型 | Shape | 布局 | 描述 |
|--------|---------|-------|------|------|
| A | half | (m, k) | RowMajor | 输入矩阵 A |
| B | half | (k, n) | RowMajor | 输入矩阵 B |
| D | half | (m, n) | RowMajor | 输出矩阵 |

**解读**：标准 GEMM I/O 约定。A、B、D 同为 `half` RowMajor。A、B 在 K 维对齐（`k`），输出 D 形状 `(m, n)`。该表只表达**无逻辑转置**的一种情况；2.1 节专门处理转置歧义。

### 表 3 · 2.1 转置内维对齐对照表（模板示例）

| transpose_a | transpose_b | A 物理形状 | B 物理形状 | K 约束 |
|-------------|-------------|------------|------------|--------|
| false | false | (M, K) | (K, N) | A 列维 == B 行维 |
| true | false | (K, M) | (K, N) | A 行维 == B 行维 |
| … | … | … | … | … |

**解读**：这是为消除"A×B 形状歧义"准备的**契约表**。`(false, false)` 时 A 物理形状就是 `(M, K)`，`A 列维 == B 行维` 才能保证内维匹配；`(true, false)` 时 A 被物理存放为 `(K, M)`，转置后视作 `(M, K)`，此时 K 维来自 A 的**物理行维**，故约束改写为 `A 行维 == B 行维`。`…` 占位表示本算子应补齐其余组合。配合 `transpose_a` / `transpose_b` 布尔属性，可避免依赖 stride 推断。

### 表 4 · 3.1 硬件与架构

| 组件 | 选型 | 说明 |
|------|------|------|
| 目标芯片 | AtlasA2 | 对应 `Arch::AtlasA2` |

**解读**：唯一硬件目标，对应 C++ 命名空间 `Arch::AtlasA2`。这是后续 `MmadAtlasA2Pingpong` 等专用组件能实例化的前提。

### 表 5 · 3.2 BlockMmad 块级矩阵乘

| 组件 | 选型 | 说明 |
|------|------|------|
| DispatchPolicy | `MmadAtlasA2Pingpong` | 流水调度策略 |
| L1TileShape | `<128, 256, 256>` | L1 级分块 (M, N, K) |
| L0TileShape | `<128, 256, 64>` | L0 级分块 (M, N, K) |
| 输入类型 | AType: half, RowMajor | |
| 输入类型 | BType: half, RowMajor | |
| 输出类型 | CType: float, RowMajor | 中间计算用 float 保精度 |

**解读**：
- `MmadAtlasA2Pingpong` 流水策略应在 code-gen 中实例化为 `MmadAtlasA2Pingpong<true>`，`<true>` 表示开启 Pingpong 双缓冲。
- L1 `<128, 256, 256>`、L0 `<128, 256, 64>`——K 维在 L1 是 256、在 L0 是 64，反映 L0→L1→GM 的分块层级关系。
- A/B 输入 `half` RowMajor；累加器 CType 选用 `float` RowMajor 以保留中间精度。
- code-gen 实例化形式：`using BlockMmad = Gemm::Block::BlockMmad<DispatchPolicy, L1TileShape, L0TileShape, AType, BType, CType>;`。

### 表 6 · 3.3 BlockEpilogue 后处理流水线

| 顺序 | 环节 | 组件 | 说明 |
|------|------|------|------|
| 1 | 数据搬运入 | `TileCopy` | GM → UB |
| 2 | 计算 | `TileElemWiseGelu` | GELU 激活 |
| 3 | 数据搬运出 | `TileCopy` | UB → GM |

**解读**：模板示例是"三步 GELU Epilogue"——先 GM→UB，再做 GELU 元素级激活，再 UB→GM。code-gen 时将这三个组件按顺序填入 `BlockEpilogue<EpilogueDispatchPolicy, CType, DType, ...Tile组件>` 的模板参数列表；若算子无后处理，则 `using BlockEpilogue = void;`。

### 表 7 · 3.4 BlockScheduler

| 组件 | 选型 | 说明 |
|------|------|------|
| 调度器 | `GemmIdentityBlockSwizzle<3, 0>` | offset=3, direction=0 |

**解读**：`Swizzle` 调度器在多核切块时按 swizzle 模式重排 block 顺序；`offset=3` 与 `direction=0` 控制重排位移方向，是影响 L2 cache 命中率的关键参数。

### 表 8 · 3.5 Kernel

| 组件 | 选型 | 说明 |
|------|------|------|
| Kernel 类型 | `Gemm::Kernel::BasicMatmul` | 纯矩阵乘 |
| | 或 `Gemm::Kernel::MatmulEpilogue` | 矩阵乘 + 后处理 |
| | 或 `Gemm::Kernel::MatmulActivation` | 矩阵乘 + 激活函数 |

**解读**：三选一互斥。模板示例对应 `BasicMatmul`。组装为 `Kernel = Kernel类型<BlockMmad, BlockEpilogue, BlockScheduler>`；code-gen 中以 `using Kernel = Gemm::Kernel::BasicMatmul<BlockMmad, BlockEpilogue, BlockScheduler>;` 实例化，并通过 `Kernel::Params params{...}; Kernel kernel; kernel(params);` 调用。

### 表 9 · 4. 参考 Example 与模板选型

| 项 | 内容 |
|----|------|
| 参考 example | `catlass/examples/00_basic_matmul` |
| 选型理由 | 功能最接近，可在此基础上增加 Epilogue |
| 模板类型 | Common 模板（M/N 方向分核） |

**解读**：以 `00_basic_matmul` 为锚点（最近的纯 GEMM 起点），在此模板上**叠加** Epilogue（如 `TileElemWiseGelu`）；若无完全匹配，需写明**变通方案**（例：参照 `03_matmul_add` 的 Epilogue 组装方式）。模板类型标注 "Common 模板（M/N 方向分核）"。

### 表 10 · 5. TilingKey 分支设计

| TilingKey 值 | 条件 | Kernel 分支内容 |
|--------------|------|----------------|
| 0 | dtype=half, transA=N, transB=N | BasicMatmul + BlockMmad(Pingpong) |
| 1 | dtype=half, transA=N, transB=T | BasicMatmul + BlockMmad(转置B) |

**解读**：示例给出两条分支。TilingKey=0 对应 `BlockMmad(Pingpong)`；TilingKey=1 对应 `BlockMmad(转置B)`。每个 key **绑定**一组模板实例化（不同 dtype/转置/调度策略组合），由 Host 侧根据 dtype 与 transA/transB 选择，并由 Kernel 侧 `TILING_KEY_IS` 宏分支特化。

### 表 11 · 6. Workspace

| 项 | 内容 |
|----|------|
| 大小计算 | 从 `kernel/*.hpp` 的 `GetWorkspaceSize` 移植 |
| 用途 | 临时中间存储（如 SplitK 的 Reduce） |

**解读**：Workspace 用于算子内部需要跨 step 暂存数据的场景（如 SplitK 的 Reduce 工作区）。其大小与算子参数相关，需从已有 kernel 头移植 `GetWorkspaceSize`，原文未给出具体字节数。

### 表 12 · 7. 接口与使用

| 项 | 内容 |
|----|------|
| aclnn 接口 | 由框架自动生成 `aclnn<OpName>` |
| Host Tiling | 计算 TilingKey、填充 Tiling 数据、SaveToBuffer |
| Kernel 入口 | `Params{problemShape, gmA, layoutA, ...}; kernel(params);` |

**解读**：使用方流程——aclnn 接口名由框架自动生成；Host 端负责 Tiling 计算；Kernel 入口即 `Params{}` + `kernel(params)` 的两步调用，与表 8 的 code-gen 调用片段一致。

---

## 【公式解读】

**原文公式**：

$$D = \text{GELU}(A \times B)$$

- **A、B、D**：均为表 2 中规定的算子张量，A 为 `(m, k)` half RowMajor 输入矩阵；B 为 `(k, n)` half RowMajor 输入矩阵；D 为 `(m, n)` half RowMajor 输出矩阵。
- **A × B**：矩阵乘，对应 GEMM 核心计算，走 `BlockMmad` 流水（`MmadAtlasA2Pingpong<true>`，L1 `<128,256,256>`，L0 `<128,256,64>`，累加器 CType=float）。
- **GELU(·)**：GELU 激活函数，对应 `BlockEpilogue` 中的 `TileElemWiseGelu`，在 UB 上完成元素级激活后由 `TileCopy` 写回 GM。
- **D**：最终输出张量，DType 与形状 `(m, n)`。

文档全文**仅含此一条数学公式**，且为模板占位示例的展示，正式算子需用本算子的真实公式替换。

---

## 【关联】

- **[epilogue-components.md](./epilogue-components.md)**：原生 Epilogue 组件的检索清单。3.3.1 节规定**先查该文档 + `catlass/include/catlass/epilogue/tile/`**，无匹配才能进入 custom 流程。
- **[custom-epilogue.md](./custom-epilogue.md)**：自定义 Tile Epilogue 的标准化编写规范。3.3.1 节规定需在该规范下写明 Tile 名称、数学行为、`DispatchPolicy`（NoSource / OneSource / TwoSource）、`computeLength` 量级、与 `TileCopy` 的组装顺序，下游 code-gen 在 `op_kernel/custom_epilogue/*.hpp` 实现。
- **`catlass-operator-code-gen`**：本文明文指出的下游消费者——把表格实例化为模板参数与 `TILING_KEY_IS` 分支代码，不产出可编译代码到本设计文档中。
- **`catlass/examples/00_basic_matmul`** 与 **`03_matmul_add`**：参考 example，前者是纯 GEMM 的最近起点，后者是 Epilogue 组装样例。
- **`kernel/*.hpp` 的 `GetWorkspaceSize`**：Workspace 大小计算的源码来源。

---

## 【使用方法】

原文为设计文档模板，**未直接提供启用命令**。可识别的工程化要素如下：

- **目标芯片**：AtlasA2，对应 `Arch::AtlasA2`。
- **Kernel 实例化样例**（code-gen 侧使用）：

  ```cpp
  using DispatchPolicy = Gemm::MmadAtlasA2Pingpong<true>;
  using L1TileShape = Gemm::GemmTile<128, 256, 256>;
  using L0TileShape = Gemm::GemmTile<128, 256, 64>;
  using AType = half; using BType = half; using CType = float;
  using BlockMmad = Gemm::Block::BlockMmad<DispatchPolicy, L1TileShape, L0TileShape, AType, BType, CType>;
  using BlockEpilogue = void; // 无后处理时
  using BlockScheduler = Gemm::Block::GemmIdentityBlockSwizzle<3, 0>;
  using Kernel = Gemm::Kernel::BasicMatmul<BlockMmad, BlockEpilogue, BlockScheduler>;
  Kernel::Params params{...}; Kernel kernel; kernel(params);
  ```

- **Host Tiling 步骤**（原文概述）：解析 shape → 计算 TilingKey → `SetTilingKey` → `SaveToBuffer`；`InferShape` 推导输出 shape；`OpDef` 注册 Input/Output/DataType。
- **Kernel 入口模板**：`Params{problemShape, gmA, layoutA, ...}; kernel(params);`（原文 7 接口与使用 节）。

> 原文**未涉及** aclnn 接口的具体启用/调用命令、CI 命令、构建开关或环境变量配置，需结合 aclnn 框架与 `catlass-operator-code-gen` 实际产物使用。
