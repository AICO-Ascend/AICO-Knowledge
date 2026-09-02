# Catlass 算子设计文档模板

> 仓 `model-agent` · 路径 `skills/optimization/catlass-operator-design/references/design-document.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/optimization/catlass-operator-design/references/design-document.md

# Catlass 算子设计文档模板 — 深度解读

## 【定位】
这是一份面向昇腾 Catlass 算子开发的**设计文档撰写规范模板**,解决「Agent 自动代码生成(`catlass-operator-code-gen`)需要从何处获取选型决策依据」的问题——告诉文档作者如何用表格化、可实例化的方式记录「选了什么组件、为什么选、怎么组装」,使代码生成器能据此实例化模板参数、产出可编译代码。

---

## 【技术要点】

1. **三层组件选型表格化**: 用「概念表格」描述硬件架构(`Arch::AtlasA2`)、BlockMmad(分块策略 + L1/L0 分块 Shape + 数据类型)、BlockEpilogue(后处理流水线环节)、BlockScheduler(`GemmIdentityBlockSwizzle<3, 0>`,offset=3, direction=0)、Kernel 类型(`BasicMatmul` / `MatmulEpilogue` / `MatmulActivation`)五层组件的选型,完全不写代码。

2. **BlockMmad 核心参数**: DispatchPolicy 选 `MmadAtlasA2Pingpong`(流水调度);L1TileShape = `<128, 256, 256>`、L0TileShape = `<128, 256, 64>`(均为 M/N/K 顺序);输入 AType/BType 用 half RowMajor,**中间计算 CType 用 float 保精度**;并提示 code-gen 实例化为 `using BlockMmad = Gemm::Block::BlockMmad<DispatchPolicy, L1TileShape, L0TileShape, AType, BType, CType>;`。

3. **BlockEpilogue 流水线**: 矩阵乘无后处理时直接写 `BlockEpilogue = void`;有后处理时按「数据搬运入(TileCopy, GM→UB) → 计算(TileElemWiseGelu 等) → 数据搬运出(TileCopy, UB→GM)」顺序填入 `BlockEpilogue<EpilogueDispatchPolicy, CType, DType, ...Tile组件>`。自定义 Tile 必须单独写明名称、数学行为、DispatchPolicy(NoSource/OneSource/TwoSource)、computeLength 量级、与 TileCopy 组装顺序。

4. **Gemm 逻辑转置契约**: 由于 M/N/K 可取相同值,仅凭二维 shape 无法唯一确定 A/B 是否逻辑转置;InferShape/Tiling 不可见 aclTensor stride。推荐用 **OpDef 布尔属性**(`transpose_a`、`transpose_b`)声明逻辑转置,并用「属性 + 物理 shape → M、N、K」对照表固化契约,框架与 aclnn 调用方保证属性与数据布局一致。

5. **TilingKey 分支设计**: 每个 key 对应**一组模板实例化**(`TILING_KEY_IS` 分支内实例化 Kernel 模板)。例如 key=0 对应 dtype=half, transA=N, transB=N 走 `BasicMatmul + BlockMmad(Pingpong)`;key=1 对应 transB=T 走 BasicMatmul + BlockMmad(转置B)。Host 侧根据 dtype/转置/调度策略选择 TilingKey。

6. **Workspace 移植机制**: 大小直接从 `kernel/*.hpp` 的 `GetWorkspaceSize` 移植,用途为临时中间存储(如 SplitK 的 Reduce);aclnn 接口由框架自动生成 `aclnn<OpName>`;Host Tiling 负责计算 TilingKey、填充 Tiling 数据、SaveToBuffer;Kernel 入口固定为 `Params{problemShape, gmA, layoutA, ...}; kernel(params);`。

---

## 【关键机制与数据】

**工作原理(数据流与代码生成链)**:

- **设计文档产出的是「决策」,代码由 code-gen 完成**: 设计文档通过选型表格实例化为模板参数列表,Agent 按表格生成代码,示例映射链——`using DispatchPolicy = Gemm::MmadAtlasA2Pingpong<true>;` → `using BlockMmad = Gemm::Block::BlockMmad<DispatchPolicy, L1TileShape, L0TileShape, AType, BType, CType>;` → `using Kernel = Gemm::Kernel::BasicMatmul<BlockMmad, BlockEpilogue, BlockScheduler>;`。
- **Host/Kernel 分工**: Host 侧(op_host)负责 Tiling(解析 shape → 计算 TilingKey → SetTilingKey → SaveToBuffer)、InferShape(根据输入 shape 推导输出 shape)、OpDef(注册 Input/Output/DataType);Kernel 侧(op_kernel)负责 GET_TILING_DATA 取 tiling 数据、`TILING_KEY_IS` 分支内实例化 Kernel 模板、调用 `kernel(params)` 执行。
- **性能数据**: 原文未涉及具体性能数据或基准测试结果,仅在分块 Shape 上给出具体数值(L1TileShape `<128, 256, 256>`、L0TileShape `<128, 256, 64>`)。
- **示例参考**: 参考 `catlass/examples/00_basic_matmul`,模板类型选 Common 模板(M/N 方向分核);若无完全匹配,变通方案需说明(例:基于 00_basic_matmul 增加 `TileElemWiseGelu` 后处理,参考 03_matmul_add 的 Epilogue 组装方式)。

---

## 【表格解读】

### 表格 1: 概述(算子功能、数学公式、使用场景)

| 项 | 内容 |
|----|------|
| 算子功能 | 一句话描述(如:矩阵乘 + GELU 融合) |
| 数学公式 | $D = \text{GELU}(A \times B)$ |
| 使用场景 | 说明适用的模型或场景 |

**解读**: 此表为占位符结构,实际填写时需用一句话讲清算子功能;数学公式以 LaTeX 形式给出(示例为 GELU 融合);使用场景需关联到大模型/典型下游任务。

### 表格 2: 输入输出信息表

| 变量名 | 数据类型 | Shape | 布局 | 描述 |
|--------|---------|-------|------|------|
| A | half | (m, k) | RowMajor | 输入矩阵 A |
| B | half | (k, n) | RowMajor | 输入矩阵 B |
| D | half | (m, n) | RowMajor | 输出矩阵 D |

**解读**: 严格定义算子的输入输出契约——变量名(A/B/D)、数据类型(half)、Shape(A 为 m×k、B 为 k×n、D 为 m×n,体现矩阵乘维度关系)、布局(均 RowMajor)、描述。这是 InferShape 和 aclnn 接口注册的依据。

### 表格 3: Gemm 与逻辑转置

| 要点 | 说明 |
|------|------|
| 形状歧义 | 若 M、N、K 可取相同值,仅凭二维 shape **无法唯一**确定是否对 A/B 做了逻辑转置 |
| stride 与 Host | InferShape / Tiling **通常不可见** aclTensor stride,不应把「从 stride 推断布局」作为算子契约的一部分 |
| 推荐契约 | 用 **OpDef 布尔属性**(如 `transpose_a`、`transpose_b`)声明逻辑转置;设计文档给出 **属性 + 物理 shape → M、N、K** 的对照表;框架与 aclnn 调用方保证 **属性与数据布局一致** |

**解读**: 此表说明 Gemm 算子设计的关键陷阱——维度歧义性(M=N=K 时 shape 退化)与 stride 不可见性,共同决定了必须用显式 OpDef 布尔属性而不是隐式 stride 推断来声明转置契约。

### 表格 4: 内维对齐表(代码示例)

| transpose_a | transpose_b | A 物理形状 | B 物理形状 | K 约束 |
|-------------|-------------|------------|------------|--------|
| false | false | (M, K) | (K, N) | A 列维 == B 行维 |
| true | false | (K, M) | (K, N) | A 行维 == B 行维 |
| … | … | … | … | … |

**解读**: 用穷举表格固化「布尔属性 + 物理 shape」到「逻辑 M/N/K」的映射关系,消除歧义。code-gen 据此生成对应的 BlockMmad 实例化(如转置 B 时需用支持转置 B 的 BlockMmad 变体),K 约束确保矩阵乘合法性。

### 表格 5: 硬件与架构

| 组件 | 选型 | 说明 |
|------|------|------|
| 目标芯片 | AtlasA2 | 对应 `Arch::AtlasA2` |

**解读**: 单行表确定目标硬件平台,通过 `Arch::AtlasA2` 枚举值映射到昇腾 A2 系列产品。

### 表格 6: BlockMmad(块级矩阵乘)

| 组件 | 选型 | 说明 |
|------|------|------|
| DispatchPolicy | `MmadAtlasA2Pingpong` | 流水调度策略 |
| L1TileShape | `<128, 256, 256>` | L1 级分块 (M, N, K) |
| L0TileShape | `<128, 256, 64>` | L0 级分块 (M, N, K) |
| 输入类型 | AType: half, RowMajor | |
| 输入类型 | BType: half, RowMajor | |
| 输出类型 | CType: float, RowMajor | 中间计算用 float 保精度 |

**解读**: 这是算子最关键的性能决策表。DispatchPolicy 选 Pingpong(双缓冲流水调度);L1(128×256×256)与 L0(128×256×64)在 K 维上体现 4:1 的分块比,符合 Cube 单元到 L0A/L0B 的搬运层级;**精度策略上是输入 half、中间计算 float**,在吞吐量与精度间做平衡。

### 表格 7: BlockEpilogue(后处理流水线)

| 顺序 | 环节 | 组件 | 说明 |
|------|------|------|------|
| 1 | 数据搬运入 | `TileCopy` | GM → UB |
| 2 | 计算 | `TileElemWiseGelu` | GELU 激活 |
| 3 | 数据搬运出 | `TileCopy` | UB → GM |

**解读**: 严格的「搬运→计算→搬运」三阶段流水线。GM(Global Memory)→ UB(Union Buffer)负责数据进入计算单元,UB → GM 负责结果写回。`TileElemWiseGelu` 是 catlass 现成的逐元素 GELU 激活 Tile,符合"标准 epilogue 组件优先,自定义仅在无匹配时启用"的设计原则。

### 表格 8: BlockScheduler

| 组件 | 选型 | 说明 |
|------|------|------|
| 调度器 | `GemmIdentityBlockSwizzle<3, 0>` | offset=3, direction=0 |

**解读**: BlockSwizzle 决定多核间如何切分 M/N 方向的 Block;`offset=3, direction=0` 两个模板参数控制起始偏移与遍历方向(具体语义需参考 catlass 源码,模板中给出明确值)。

### 表格 9: Kernel 类型

| 组件 | 选型 | 说明 |
|------|------|------|
| Kernel 类型 | `Gemm::Kernel::BasicMatmul` | 纯矩阵乘 |
| | 或 `Gemm::Kernel::MatmulEpilogue` | 矩阵乘 + 后处理 |
| | 或 `Gemm::Kernel::MatmulActivation` | 矩阵乘 + 激活函数 |

**解读**: 三选一决策点——根据是否有后处理(Epilogue 流水线)和激活函数(Activation)分别选择。本模板示例是 GELU 融合,所以应选 `MatmulEpilogue` 而非 `MatmulActivation`(因为激活是放在 Epilogue 流水线里组装)。

### 表格 10: TilingKey 分支

| TilingKey 值 | 条件 | Kernel 分支内容 |
|--------------|------|----------------|
| 0 | dtype=half, transA=N, transB=N | BasicMatmul + BlockMmad(Pingpong) |
| 1 | dtype=half, transA=N, transB=T | BasicMatmul + BlockMmad(转置B) |

**解读**: 每个 TilingKey 是一个模板实例化分支的入口。Host 侧根据 dtype、转置属性决策 TilingKey 值,Kernel 侧在 `TILING_KEY_IS(key)` 宏内实例化对应的 Kernel 模板——这是昇腾算子编译期多态 + 运行时分发的标准做法。

### 表格 11: 参考 Example 与模板选型

| 项 | 内容 |
|----|------|
| 参考 example | `catlass/examples/00_basic_matmul` |
| 选型理由 | 功能最接近,可在其基础上增加 Epilogue |
| 模板类型 | Common 模板(M/N 方向分核) |

**解读**: 锚定最近的可复用代码示例,降低变通成本——若 00_basic_matmul 不够用,可参考 03_matmul_add 的 Epilogue 组装方式。

### 表格 12: Workspace

| 项 | 内容 |
|----|------|
| 大小计算 | 从 `kernel/*.hpp` 的 `GetWorkspaceSize` 移植 |
| 用途 | 临时中间存储(如 SplitK 的 Reduce) |

**解读**: Workspace 是算子执行时申请的一块 device 临时内存,典型用途是 SplitK 切分后的部分和 Reduce 操作;大小需从已编译 kernel 移植。

### 表格 13: 接口与使用

| 项 | 内容 |
|----|------|
| aclnn 接口 | 由框架自动生成 `aclnn<OpName>` |
| Host Tiling | 计算 TilingKey、填充 Tiling 数据、SaveToBuffer |
| Kernel 入口 | `Params{problemShape, gmA, layoutA, ...}; kernel(params);` |

**解读**: 算子对外暴露的标准三件套——框架自动生成的 aclnn 算子入口、Host 侧 Tiling 流程、Kernel 侧 Params + kernel 调用约定。

---

## 【公式解读】

**公式(原文)**:
$$D = \text{GELU}(A \times B)$$

**符号解读**:
- $A$、$B$: 输入矩阵,维度分别为 $(m, k)$ 与 $(k, n)$(由表格 2 给出)
- $A \times B$: 标准矩阵乘法,结果维度为 $(m, n)$
- $\text{GELU}(\cdot)$: Gaussian Error Linear Unit 激活函数,逐元素作用于矩阵乘结果
- $D$: 最终输出矩阵,维度 $(m, n)$,数据类型 half(由表格 2 给出)

**作用**: 这是表格 1 中"算子功能"的具体数学刻画,既定义了算子的语义(GEMM 后接 GELU 激活),也间接说明为何 BlockEpilogue 选 `TileElemWiseGelu`——公式层面的"数学行为"是选型决策的最上游依据。code-gen 据此组装 BlockEpilogue 流水线,无需在文档中写可编译代码。

---

## 【关联】

本文档作为 Catlass 算子设计的**总纲模板**,与以下上下游文档/模块存在明确引用关系:

1. **[epilogue-components.md](./epilogue-components.md)** — 标准 Tile Epilogue 组件清单。在 3.3.1 节明确指出:**当标准清单中无匹配组件时**,才允许进入自定义流程。这是「优先复用 → 自定义兜底」的依赖关系。

2. **[custom-epilogue.md](./custom-epilogue.md)** — 自定义 Tile Epilogue 的设计规范。在 3.3.1 节明确引用:自定义 Tile 需在该文档中独立写明名称、数学行为、DispatchPolicy、computeLength 量级、与 TileCopy 组装顺序;code-gen 据此在 `op_kernel/custom_epilogue/*.hpp` 实现该 Tile。本模板是上游入口,custom-epilogue.md 是下游补充。

3. **catlass-operator-code-gen**(隐含下游): 文中反复出现的"Agent 生成代码时按此表实例化模板参数""code-gen 时将上表实例化为……"等表述,说明本文档是 code-gen 工具的**事实上的输入契约**——表格中的每一个选型字段都对应一组模板参数实例化。

4. **catlass 源码 `catlass/include/catlass/epilogue/tile/`**(隐含): 自定义 Tile 的检索来源之一,与 epilogue-components.md 共同构成"是否走自定义流程"的判定依据。

---

## 【使用方法】

**启用方式**: 本文是**模板文档**而非可执行模块,不需启用命令。其使用方式是:在开发新 Catlass 算子时,复制本文档作为骨架,按以下流程填写:

1. **第 1 节概述**: 用一句话描述算子功能,填数学公式(LaTeX),说明适用模型/场景。
2. **第 2 节输入输出**: 严格列出所有输入/输出变量的数据类型、Shape、布局、描述;若涉及 A×B,**必须**写 2.1 节 Gemm 与逻辑转置,并给出「属性 + 物理 shape → M/N/K」对照表。
3. **第 3 节核心组件选型(必写)**: 按 3.1 ~ 3.5 依次填硬件、BlockMmad、BlockEpilogue、BlockScheduler、Kernel 的选型表格;无后处理时 BlockEpilogue 写 `void`;自定义 Tile 须按 [custom-epilogue.md](./custom-epilogue.md) 单独写明。
4. **第 4 节参考 Example**: 锚定 `catlass/examples/` 下最近的 example,说明选型理由与模板类型;无完全匹配时写明变通方案。
5. **第 5 节 TilingKey 分支**: 列出每个 key 的条件与对应 Kernel 分支内容。
6. **第 6 节 Workspace**: 填大小计算来源与用途。
7. **第 7 节接口与使用**: 说明 aclnn 接口来源、Host Tiling 流程、Kernel 入口。
8. **第 8 节扩展性**: 列出后续可替换的组件。
9. **第 9 节实现方案纲要**: 简要列出 Host 与 Kernel 各自职责,**只写纲要不写代码**。

**配置项/命令**: 原文未涉及任何运行时配置项或启用命令——本文档是设计阶段的写作规范,本身不需要配置或命令激活。code-gen 工具的具体调用方式(`catlass-operator-code-gen` 的命令行)原文未涉及。
