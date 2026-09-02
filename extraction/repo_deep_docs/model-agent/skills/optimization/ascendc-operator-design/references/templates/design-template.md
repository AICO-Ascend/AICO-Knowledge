# [算子名称] 设计文档

> 仓 `model-agent` · 路径 `skills/optimization/ascendc-operator-design/references/templates/design-template.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/optimization/ascendc-operator-design/references/templates/design-template.md

# 「AscendC 算子设计模板」深度解读

## 【定位】

这是一份**AscendC 算子开发的设计文档模板**，为在昇腾 NPU 上落地自定义算子的开发者提供一套标准化的设计框架：规定算子接口、数据类型、计算逻辑、Tiling 切分、Workspace 分配、Kernel 循环结构、文件结构与检查清单的填写范式，使任意算子（elementwise / reduction / 矩阵类等）都能按统一模板输出可被 `ascendc-operator-code-gen` skill 消费的设计规范，从而自动生成 Host/Kernel 双端代码。

---

## 【技术要点】

1. **算子接口与多精度支持**：函数签名为 `at::Tensor [operator_name](const at::Tensor &input1, const at::Tensor &input2, /* 其他参数 */)`，输入输出 Tensor 支持 `bfloat16 / float16 / float32` 三种精度，均支持 ND 格式。

2. **实现路径三选一**：AscendC Kernel（纯 vector）、CATLASS 模板库（矩阵乘法类）、ACLNN 封装（CANN 内置算子），需在文档中勾选并填写理由。

3. **两级 Tiling 策略**：Block 级（核间切分）+ UB 级（核内切分）。Block 级保证负载均衡并做 512 字节 Cache Line 对齐；UB 级根据 buffer 系数和 32 字节对齐约束计算单次循环处理量。

4. **整核/尾核负载均衡**：通过 `formerNum / formerLength / tailNum / tailLength` 四元组描述核间数据分配，验证公式为 `formerNum * formerLength + tailNum * tailLength == totalLength`。

5. **精度强制升精度**：NPU 计算单元不支持 fp16/bf16 直接计算，必须升精度到 fp32；因此输入为 fp16/bf16 时需额外分配 `tileLength * 4` 字节的 float32 tempBuffer。

6. **Workspace 分类**：elementwise 类算子固定申请 `SYSTEM_WORKSPACE_SIZE = 16 * 1024 * 1024`（16MB）；其他类算子申请 `sizeof([OperatorName]TilingData)` 大小。

---

## 【关键机制与数据】

### 工作原理

算子执行遵循 **"GM → UB → 计算 → UB → GM"** 的经典 AscendC 流程：

1. **Host 端**：根据 `totalLength` 计算 Block 级 Tiling 参数（Cache Line 对齐、整核/尾核分配）和 UB 级 Tiling 参数（`tileLength`），打包为 `[OperatorName]TilingData` 结构体下发给 Kernel。
2. **Kernel 端**：`Process()` 主循环通过 `AscendC::GetBlockIdx()` 判定当前核是整核还是尾核，得到 `coreLength`；再以 `tileLength` 为步长在核内迭代。
3. **每个 tile**：依次执行 `CopyIn`（GM→UB）→ `Compute`（核心计算，fp16/bf16 时升精度到 fp32）→ `CopyOut`（UB→GM）。
4. **尾块处理**：循环中前 `tileNum-1` 次按 `tileLength` 处理，最后一次按 `tailTileLength = blockLength - (tileNum - 1) * tileLength` 处理。

### 关键数据（原文占位符标注）

- 原文：UB_SIZE_LIMIT 示例值 **192KB**（实际编码时通过接口获取）。
- 原文：Cache Line 对齐粒度 **512 字节**；UB 内部对齐 **32 字节**。
- 原文：示例架构图中核数量为 **Core 0 ~ Core 39**（40 个核的示意，非硬性参数）。
- 原文：Workspace 示例值 **16MB**。
- 原文：fp16/bf16 升精度所需额外 buffer 大小为 `tileLength * 4` 字节。

### 性能/访存特性（原文为待填写项）

模板要求填写三项算子特性：**计算模式**（memory-bound / compute-bound / balance）、**访存模式**（顺序 / 随机 / 跨轴）、**并行性**（高 / 中 / 低）。具体值由实际算子决定，原文未给出。

---

## 【表格解读】

### 表 1：参数说明（§1.2）

| 参数名 | 类型 | 输入/输出 | 支持的数据类型 | 描述 | 约束条件 |
|--------|------|-------|--------|------|------|
| input1 | at::Tensor | 输入 | bfloat16/float16/float32 | 输入tensor1 | 支持ND |
| input2 | at::Tensor | 输入 | bfloat16/float16/float32 | 输入tensor2 | 支持ND |
| output | at::Tensor | 输出 | bfloat16/float16/float32 | 输出tensor | 支持ND |

**逐行解读**：
- **input1 / input2**：模板展示两个对称输入张量的标准描述方式，dtype 三选一（bf16/fp16/fp32），形态约束统一为"支持ND"——即非维度限制，输入任意 rank。
- **output**：输出张量与输入保持同样三种精度可选；模板暗示输出 dtype 由调用方指定，而非由算子内部强制——需 Host 端在调用 kernel 前保证 output 已分配并传入。

---

### 表 2：Block 级 Tiling 参数计算（§3.2）

| 参数 | 计算公式 | 值 |
|------|----------|-----|
| totalLengthCore | (totalLength + CORE_NUM - 1) / CORE_NUM | [值] |
| totalLengthCoreAlign | (totalLengthCore + 512 - 1) / 512 * 512 | [值] |
| usedCoreNum | (totalLength + totalLengthCoreAlign - 1) / totalLengthCoreAlign | [值] |
| formerNum | usedCoreNum - 1 | [值] |
| tailNum | 1 | [值] |
| formerLength | totalLengthCoreAlign | [值] |
| tailLength | totalLength - (usedCoreNum - 1) * formerLength | [值] |

**逐行解读**：
- **totalLengthCore**：总长度向上取整均分到 `CORE_NUM` 个核，得到的"平均每核数据量"——是后续对齐的基准。
- **totalLengthCoreAlign**：将 `totalLengthCore` 向上取整到 512 字节倍数，保证每个核处理的数据块 **Cache Line 对齐**，避免跨 Cache Line 访问造成性能损失（512B 是 NPU Cache Line 大小）。
- **usedCoreNum**：用对齐后的块大小反推实际需要的核数——`usedCoreNum ≤ CORE_NUM`，未用到的核不参与计算。
- **formerNum / tailNum**：采用**整核 + 1 个尾核**的简化模型。`formerNum = usedCoreNum - 1` 表示跑"整块大小"的核数；`tailNum = 1` 表示最多一个尾核处理剩余数据。
- **formerLength = totalLengthCoreAlign**：整核统一处理对齐后长度。
- **tailLength**：总长减去所有整核承担的数据，剩余交给尾核。

下方"负载均衡验证"明确给出两条不变量：`formerLength >= tailLength`（整核 ≥ 尾核数据量，保证整核不会更轻），以及 `formerNum * formerLength + tailNum * tailLength == totalLength`（数据完整切分，无遗漏）。

---

### 表 3：精度处理说明（§3.3）

| 输入数据类型 | 处理方式 | 计算精度 | UB 影响 |
|------------|---------|---------|--------|
| float16 | **升精度到 float32** | float32 | 需要额外 float32 buffer |
| bfloat16 | **升精度到 float32** | float32 | 需要额外 float32 buffer |
| float32 | 直接计算 | float32 | 无额外开销 |

**逐行解读**：
- **fp16 行**：硬件限制下，fp16 不能直接进入 Vector 计算单元，必须在 UB 上转成 fp32 再算。代价是占用额外 fp32 buffer（输入/输出各一份）。
- **bf16 行**：与 fp16 同理，虽然 bf16 动态范围更大，但 NPU 计算单元同样不直接支持。
- **fp32 行**：无需精度转换，buffer 开销与 dtype 一致，是最经济的情况。

该表与下方"UB 分配表"中的 `tempBuffer (fp16/bf16时)` 行直接对应——`tileLength * 4` 字节的 tempBuffer 就是为升精度预留的。

---

### 表 4：UB 分配表（§3.3）

| Buffer名称 | 大小(字节) | 用途 | 数量 | 总大小 |
|-----------|-----------|------|------|--------|
| inQueueX | tileLength * dtypeSize | 输入数据缓冲 | BUFFER_NUM | [计算值] |
| inQueueY | tileLength * dtypeSize | 输入数据缓冲 | BUFFER_NUM | [计算值] |
| outQueueZ | tileLength * dtypeSize | 输出数据缓冲 | BUFFER_NUM | [计算值] |
| tempBuffer (fp16/bf16时) | tileLength * 4 | float32计算缓冲 | 1 | [计算值] |
| **总计** | - | - | - | **[总UB使用]** |

**逐行解读**：
- **inQueueX / inQueueY**：两个输入的 UB 队列（典型 elementwise 二元算子），单 buffer 大小 = `tileLength × dtypeSize`，数量 `BUFFER_NUM` 一般为 2（双缓冲 double buffer 用）。
- **outQueueZ**：输出队列，结构同上。
- **tempBuffer**：仅在 fp16/bf16 输入时存在，大小 `tileLength * 4`（fp32 占 4 字节），用于在 Compute 阶段承载升精度后的中间数据。
- **总计行**：所有 buffer 大小求和，模板要求填入"总UB使用"具体值，配合 UB 约束验证（与 §3.3 末"UB 使用 / UB 限制 / 是否满足约束 / 32字节对齐"四行配合使用）。

---

### 表 5：tileLength 计算（§3.3）

| 参数 | 计算公式 | 值 |
|------|----------|-----|
| bufferCoefficient | 根据UB分配表确定 | [值] |
| maxTileElements | UB_SIZE_LIMIT / bufferCoefficient（UB_SIZE_LIMIT 实际编码时通过接口获取） | [值] |
| alignElements | 32 / dtypeSize | [值] |
| tileLength | (maxTileElements / alignElements) * alignElements | [值] |

**逐行解读**：
- **bufferCoefficient**：从 UB 分配表反推出的"每元素占用字节数"，典型值为 `2 * BUFFER_NUM * dtypeSize`（输入缓冲）+ `2 * BUFFER_NUM * dtypeSize`（输出缓冲），fp16/bf16 时再 + 4（tempBuffer）。
- **maxTileElements**：用 `UB_SIZE_LIMIT`（硬件接口查询，示例 192KB）除以系数，得到单 tile 可容纳的最大元素数。
- **alignElements**：32 字节对齐粒度换算到元素数（fp16→16元素，fp32→8元素，bf16→16元素）。
- **tileLength**：将 `maxTileElements` 向下取整到 `alignElements` 的倍数——保证 tile 边界 32 字节对齐，避免 UB 内部出现非对齐访存。

---

### 表 6：Workspace 需求（§4.1）

| 算子类别 | workspace size | 说明 |
|----------|---------------|------|
| elementwise 类 | SYSTEM_WORKSPACE_SIZE | 通常为 16MB |
| 其他类算子 | sizeof([OperatorName]TilingData) | tiling data 大小 |

**逐行解读**：
- **elementwise 行**：固定申请 16MB，因为 elementwise 无需 tiling data 持久化（kernel 直接读 GM），且可能需要 scratch buffer。
- **其他类算子**：申请仅够放下 TilingData 的空间（通常几百字节到几 KB），因为这部分数据要在 Host 与 Kernel 间传递。

---

## 【公式解读】

文档中所有 Block 级 Tiling 公式构成一组完整的"对齐-切分-反推"链路：

$$
\text{totalLengthCore} = \left\lceil \frac{\text{totalLength}}{\text{CORE\_NUM}} \right\rceil = \frac{\text{totalLength} + \text{CORE\_NUM} - 1}{\text{CORE\_NUM}}
$$

- $\text{totalLength}$：待处理总元素数；$\text{CORE\_NUM}$：物理核数（图中示例为 40）。
- 作用：算出"理想平均每核负载"，作为对齐基数。

$$
\text{totalLengthCoreAlign} = \left\lceil \frac{\text{totalLengthCore}}{512\ \text{bytes}} \right\rceil \times 512\ \text{bytes} = \frac{\text{totalLengthCore} + 512 - 1}{512} \times 512
$$

- 作用：把每核数据量对齐到 **Cache Line（512B）** 边界，避免 GM 访问跨 Cache Line。代码中实际按"元素数"使用公式——若 dtypeSize=4，则 `alignElements = 512/4 = 128`。

$$
\text{usedCoreNum} = \left\lceil \frac{\text{totalLength}}{\text{totalLengthCoreAlign}} \right\rceil
$$

- 作用：用对齐后的块大小反推实际需要的核数。未使用的核保持空闲，避免小数据浪费并行度。

$$
\text{formerNum} = \text{usedCoreNum} - 1, \quad \text{tailNum} = 1
$$

- 作用：建立"整核 + 尾核"二元模型。整核跑满 `formerLength`，尾核处理余数。

$$
\text{formerLength} = \text{totalLengthCoreAlign}
$$

$$
\text{tailLength} = \text{totalLength} - (\text{usedCoreNum} - 1) \times \text{formerLength}
$$

- 作用：定义两类核各自承担的数据长度。不变量 $\text{formerNum} \times \text{formerLength} + \text{tailNum} \times \text{tailLength} = \text{totalLength}$ 必须成立。

UB 级 Tiling 公式：

$$
\text{maxTileElements} = \frac{\text{UB\_SIZE\_LIMIT}}{\text{bufferCoefficient}}
$$

- $\text{UB\_SIZE\_LIMIT}$：UB 总容量上限（接口获取，示例 192KB）。
- $\text{bufferCoefficient}$：单个 tile 元素平均占用的字节数（由 UB 分配表所有 buffer 之和 / tileLength 推得）。
- 作用：算出"单次循环最多能处理多少元素"。

$$
\text{alignElements} = \frac{32}{\text{dtypeSize}}
$$

- $\text{dtypeSize}$：单元素字节数（fp16/bf16=2，fp32=4）。
- 作用：UB 内部 32 字节对齐约束换算到元素粒度。

$$
\text{tileLength} = \left\lfloor \frac{\text{maxTileElements}}{\text{alignElements}} \right\rfloor \times \text{alignElements}
$$

- 作用：将 maxTileElements 向下取整到 alignElements 倍数，确保 tile 边界 32B 对齐。

核内循环公式（在 §6.1 代码注释中体现）：

$$
\text{tileNum} = \left\lceil \frac{\text{blockLength}}{\text{tileLength}} \right\rceil
$$

$$
\text{tailTileLength} = \text{blockLength} - (\text{tileNum} - 1) \times \text{tileLength}
$$

- $\text{blockLength}$：当前核承担的数据长度（`formerLength` 或 `tailLength`）。
- 作用：循环前 `tileNum - 1` 次按完整 `tileLength` 处理，最后一次按 `tailTileLength` 处理，处理尾块边界。

---

## 【关联】

文档通过引用与外部 skill 形成完整的"设计 → 编码"链路：

- **`references/hardware-architecture.md`**（硬件说明）：解释 Cache Line（512B）、UB 大小、对齐约束等硬件级参数的由来——`tileLength` 计算、`totalLengthCoreAlign` 都依赖此处的硬件事实。

- **`references/elementwise-tiling.md`**（逐元素操作 Tiling）：本文档 UB 分配表默认两个输入 + 一个输出的结构（inQueueX/inQueueY/outQueueZ）正是 elementwise 算子的典型形态，Workspace 章节也将"elementwise 类"单列为 16MB 标准。

- **`references/reduction-tiling.md`**（归约操作 Tiling）：与 elementwise 并列的另一大类算子；reduction 涉及跨轴访存，文档"算子特性"中"访存模式"字段（顺序 / 随机 / 跨轴访问）即对应 reduction 的跨轴归约场景。

- **`references/general-tiling-principles.md`**（通用 Tiling 原则）：提供整核/尾核策略、负载均衡等不依赖具体算子类型的通用规则，文档 §3.2 整核/尾核模型的理论基础来源。

- **`ascendc-operator-code-gen` skill**（文档末尾"使用说明"）：模板填写完成后，下游消费方——通过此 skill 将设计文档自动转成 `csrc/ops/<operator_name>/` 下的 Host + Kernel 双端 C++ 代码，对应 §7.1 文件结构清单（CMakeLists.txt、op_host/*.cpp、op_kernel/*.cpp、ops.h、register.cpp）。

- **`csrc/ops.h` 与 `csrc/register.cpp`**（§7.1）：分别承担算子声明注册职责——`ops.h` 提供对外 C++ 入口声明，`register.cpp` 将算子注册到 PyTorch / TorchScript 调用表，使 ATen 形式的 `at::Tensor [operator_name](...)` 可被 Python 前端调用。

---

## 【使用方法】

**模板填充步骤**（原文"使用说明"章节直接给出）：

1. **替换占位符**：将所有 `[placeholder]`（如 `[operator_name]`、`[OperatorName]`、`[值]`、`[优化点1]` 等）替换为实际内容。
2. **勾选复选框**：§1.3 数据类型、§2.3 实现路径、§3.3 float16/bfloat16 额外 UB 分配项——按算子实际支持情况勾选。
3. **填写表格数值**：§3.2 Block 级 Tiling 的 `[值]` 列、§3.3 UB 分配的 `[计算值]` 列、§3.3 tileLength 的 `[值]` 列、§5.1 关键优化点 1~4。
4. **调整代码块**：根据实际算子调整函数签名、参数名、类型（如非二元 elementwise 则修改 inQueue 数量）。
5. **删除不适用节**：若某节不适用于当前算子（如 reduction 算子无 tempBuffer 升精度逻辑），可整节删除。

**启用命令**（原文末尾明确）：设计文档填写完成后，调用 `ascendc-operator-code-gen` skill，即可自动生成 `csrc/ops/<operator_name>/` 下的具体代码实现，包括：

- Host 端：`op_host/<operator_name>.cpp`（TilingData 定义 + Block/UB 级参数计算 + workspace 分配 + kernel 入口调用）。
- Kernel 端：`op_kernel/<operator_name>.cpp`（Init、CopyIn、Compute、CopyOut、Process 主循环）。
- 配套文件：`CMakeLists.txt`（编译规则）、`ops.h`（声明）、`register.cpp`（注册）。

**配套配置项**：原文以**模板占位符**形式呈现，未给出具体的运行时配置开关或命令行参数；具体配置项需在使用方按算子语义填入 §3 Tiling 参数、§4 Workspace size、§5 优化项后由 code-gen skill 固化到代码中。
