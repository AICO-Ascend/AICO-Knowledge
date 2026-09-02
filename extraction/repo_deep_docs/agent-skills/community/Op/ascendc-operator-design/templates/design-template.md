# [算子名称] 设计文档

> 仓 `agent-skills` · 路径 `community/Op/ascendc-operator-design/templates/design-template.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/community/Op/ascendc-operator-design/templates/design-template.md

# 一体化深度解读:AscendC 算子设计模板文档

## 【定位】

这篇文档是一份**AscendC 算子设计的标准化模板**,为昇腾(Ascend)社区中 AI Agent 辅助研发场景下,新建算子时的接口定义、计算逻辑拆解、两级 Tiling 策略、Workspace 规划、性能特性标注与代码实现检查提供统一的填空式骨架,使设计产物的结构、字段、约束可被 `ascendc-operator-code-gen` skill 直接消费并生成具体 C++ 代码。

---

## 【技术要点】

1. **算子接口规范**:采用 `at::Tensor [operator_name](const at::Tensor &input1, const at::Tensor &input2, ...)` 函数签名,显式列出 `input1`、`input2`、`output` 三个 Tensor,支持 `bfloat16/float16/float32` 三种 dtype,均要求 ND 格式(原文参数表第 1-3 行)。
2. **实现路径三选一**:AscendC Kernel(纯 vector / MatMul)、CATLASS 模板库(矩阵乘法类)、ACLNN 封装(CANN 内置算子),通过勾选框 + 选择理由说明决策。
3. **两级 Tiling 架构**:
   - **Block 级(核间切分)**:以 **Cache Line 512 字节对齐** 为基本单位,采用"整核 / 尾核(former/tail)"策略保证负载均衡,核数图中示例为 `Core 0 ... Core 39`(共 40 核)。
   - **UB 级(核内切分)**:**32 字节对齐**,由 Host 端根据 UB 分配表动态计算单 tile 长度 `tileLength`。
4. **精度处理硬约束**:**NPU 计算单元不支持 float16/bfloat16 的直接计算,必须升精度到 float32**,这意味着每个 fp16/bf16 输入/输出都额外占用一份 float32 临时 buffer,直接放大 UB 容量需求(原文 3.3 节"重要"提示)。
5. **Workspace 分类**:
   - elementwise 类算子:`SYSTEM_WORKSPACE_SIZE = 16 * 1024 * 1024`(即 **16MB**)。
   - 其他类算子:`sizeof([OperatorName]TilingData)`(即 TilingData 结构体自身大小)。
6. **核内执行三段式**:标准 AscendC `Process()` 主循环由 `CopyIn(GM→UB) → Compute(UB 上计算) → CopyOut(UB→GM)` 三阶段组成,需显式处理"整 tile 循环"与"尾 tile(tailTileLength)"两类分支。

---

## 【关键机制与数据】

### 3.1 数据流路径

**(原文)三级存储递降**:

```
GM (totalLength)
   └─→ 40 个 Core 并行切分 (Block 级,former/tail 策略)
        └─→ 各 Core 内部 UB 切分为多个 tileLength (UB 级)
             └─→ CopyIn → Compute(fp16/bf16 需升精度 fp32) → CopyOut
```

### 3.2 Block 级切分计算

**(原文)Cache Line 对齐 + 整核/尾核策略**:
- `totalLengthCore`:`(totalLength + CORE_NUM - 1) / CORE_NUM` → 每核理论平均长度(向上取整)
- `totalLengthCoreAlign`:`(totalLengthCore + 512 - 1) / 512 * 512` → 512 字节对齐后的核长度
- `usedCoreNum`:`(totalLength + totalLengthCoreAlign - 1) / totalLengthCoreAlign` → 实际占用核数
- `formerNum = usedCoreNum - 1`(整核数),`tailNum = 1`(尾核固定为 1)
- 验证式:`formerNum * formerLength + tailNum * tailLength == totalLength`

### 3.3 UB 级切分与精度 buffer

**(原文)**:`tileLength` 受 UB 容量与 buffer 系数共同约束:

```
maxTileElements   = UB_SIZE_LIMIT / bufferCoefficient
alignElements     = 32 / dtypeSize
tileLength        = (maxTileElements / alignElements) * alignElements
```

- `UB_SIZE_LIMIT` 在编码时通过接口获取,文档示例值 **192KB**(原文 3.3 节"UB 限制"行)。
- fp16/bf16 输入额外引入 `tileLength * 4` 字节的 float32 临时 buffer(数量 1)。

### 3.4 性能特性待标注项

**(原文)**:模板预留三类标签供填写者勾选/填空:计算模式(memory-bound / compute-bound / balance)、访存模式(顺序 / 随机 / 跨轴)、并行性(高 / 中 / 低)——本模板未给默认值,属于设计阶段定性输入。

### 3.5 文件结构契约

**(原文)** 7.1 节列出 5 个固定交付物路径:`csrc/ops/<operator_name>/CMakeLists.txt`、`op_host/<operator_name>.cpp`、`op_kernel/<operator_name>.cpp`,以及 `csrc/ops.h` 声明、`csrc/register.cpp` 注册。

---

## 【表格解读】

### 表 1:算子参数说明(原文 §1.2)

| 参数名 | 类型 | 输入/输出 | 支持的数据类型 | 描述 | 约束条件 |
|--------|------|-------|-------|--------|------|
| input1 | at::Tensor | 输入 | bfloat16/float16/float32 | 输入tensor1 | 支持ND |
| input2 | at::Tensor | 输入 | bfloat16/float16/float32 | 输入tensor2 | 支持ND |
| output | at::Tensor | 输出 | bfloat16/float16/float32 | 输出tensor | 支持ND |

**解读**:输入 2 个、输出 1 个,数据类型三选一并通过 ND 格式约束;input/output 三列结构完全对称,意味着 Host 端 dtype 检查逻辑可参数化复用。

### 表 2:Block 级 Tiling 参数计算(原文 §3.2)

| 参数 | 计算公式 | 值 |
|------|----------|-----|
| totalLengthCore | (totalLength + CORE_NUM - 1) / CORE_NUM | [值] |
| totalLengthCoreAlign | (totalLengthCore + 512 - 1) / 512 * 512 | [值] |
| usedCoreNum | (totalLength + totalLengthCoreAlign - 1) / totalLengthCoreAlign | [值] |
| formerNum | usedCoreNum - 1 | [值] |
| tailNum | 1 | [值] |
| formerLength | totalLengthCoreAlign | [值] |
| tailLength | totalLength - (usedCoreNum - 1) * formerLength | [值] |

**解读**:六步链式派生——先求理论均分 → 512B 对齐 → 反算实际核数 → 拆出整核/尾核两组参数。所有公式均含 `-1` 实现向上取整除法;`formerLength ≥ tailLength` 为内嵌的负载均衡不变量。

### 表 3:精度处理与 UB 影响(原文 §3.3 精度处理)

| 输入数据类型 | 处理方式 | 计算精度 | UB 影响 |
|------------|---------|---------|--------|
| float16 | **升精度到 float32** | float32 | 需要额外 float32 buffer |
| bfloat16 | **升精度到 float32** | float32 | 需要额外 float32 buffer |
| float32 | 直接计算 | float32 | 无额外开销 |

**解读**:仅 float32 输入走"直通"路径,其余两类必须引入 dtypeSize=4 的临时 buffer,使得 buffer 系数 `bufferCoefficient` 在 fp16/bf16 路径下显著膨胀,直接挤压 `tileLength` 上界。

### 表 4:UB 分配表(原文 §3.3 UB 分配表)

| Buffer名称 | 大小(字节) | 用途 | 数量 | 总大小 |
|-----------|-----------|------|------|--------|
| inQueueX | tileLength * dtypeSize | 输入数据缓冲 | BUFFER_NUM | [计算值] |
| inQueueY | tileLength * dtypeSize | 输入数据缓冲 | BUFFER_NUM | [计算值] |
| outQueueZ | tileLength * dtypeSize | 输出数据缓冲 | BUFFER_NUM | [计算值] |
| tempBuffer (fp16/bf16时) | tileLength * 4 | float32计算缓冲 | 1 | [计算值] |
| **总计** | - | - | - | **[总UB使用]** |

**解读**:在 fp32 路径下 `bufferCoefficient ≈ 3 * dtypeSize * BUFFER_NUM`;一旦开启升精度,需再加 `4 * 1`,且 `dtypeSize=2`(fp16/bf16)与 `tileLength*4`(fp32 temp)在数值上量纲一致,合并后 `bufferCoefficient` 可按本表直接累加。

### 表 5:tileLength 计算(原文 §3.3 tileLength 计算)

| 参数 | 计算公式 | 值 |
|------|----------|-----|
| bufferCoefficient | 根据UB分配表确定 | [值] |
| maxTileElements | UB_SIZE_LIMIT / bufferCoefficient(UB_SIZE_LIMIT 实际编码时通过接口获取) | [值] |
| alignElements | 32 / dtypeSize | [值] |
| tileLength | (maxTileElements / alignElements) * alignElements | [值] |

**解读**:`alignElements` 体现"按元素粒度对齐"——dtypeSize=2 时为 16,=4 时为 8;`tileLength` 末端乘以 `alignElements` 即完成向下对齐到 32 字节边界。

### 表 6:Workspace 大小计算(原文 §4.1)

| 算子类别 | workspace size | 说明 |
|----------|---------------|------|
| elementwise 类 | SYSTEM_WORKSPACE_SIZE | 通常为 16MB |
| 其他类算子 | sizeof([OperatorName]TilingData) | tiling data 大小 |

**解读**:二选一策略——elementwise 算子无 tiling 中间态,直接申请 16MB 系统 workspace;其他类(如 reduction、matmul)只需把 TilingData 结构体自身大小作为 workspace,用于跨核同步传递参数。

---

## 【公式解读】

### 公式 ① — 每核理论均分长度

$$ \text{totalLengthCore} = \left\lfloor \frac{\text{totalLength} + \text{CORE\_NUM} - 1}{\text{CORE\_NUM}} \right\rfloor $$

- `totalLength`:待处理元素总数(原始未对齐值)。
- `CORE_NUM`:硬件可用核数,模板未给死值,由运行时/芯片型号决定。
- `+ CORE_NUM - 1` 实现向上取整除法,保证每个核至少分配到完整工作量。

### 公式 ② — 512 字节对齐后的核长度

$$ \text{totalLengthCoreAlign} = \left\lfloor \frac{\text{totalLengthCore} + 511}{512} \right\rfloor \times 512 $$

- `512`:Cache Line 大小,确保一次 GM 事务跨完整 cache line。
- 该对齐是 GM 带宽最优与硬件访存效率的折中约束。

### 公式 ③ — 实际占用核数

$$ \text{usedCoreNum} = \left\lfloor \frac{\text{totalLength} + \text{totalLengthCoreAlign} - 1}{\text{totalLengthCoreAlign}} \right\rfloor $$

- 含义:数据总量除以单核对齐后长度,得到真正需要的核数。
- 当 totalLength 较小时,usedCoreNum < CORE_NUM,实现自动核数收缩。

### 公式 ④ — 尾核长度(剩余不足对齐单元的部分)

$$ \text{tailLength} = \text{totalLength} - (\text{usedCoreNum} - 1) \times \text{formerLength} $$

- 表示最后一个核需要处理的"剩余"元素数,可能小于 formerLength,体现 former/tail 策略对尾部不均衡的吸收。

### 公式 ⑤ — 32 字节对齐元素数

$$ \text{alignElements} = \frac{32}{\text{dtypeSize}} $$

- `dtypeSize` ∈ {2, 4} 对应 fp16/bf16、fp32。
- 含义:32 字节是 UB 内部数据搬运的最小对齐粒度。

### 公式 ⑥ — 单 tile 处理长度(向下对齐)

$$ \text{tileLength} = \left\lfloor \frac{\text{maxTileElements}}{\text{alignElements}} \right\rfloor \times \text{alignElements} $$

- `maxTileElements` 已由 buffer 系数反推得到,此处再做一次"按 32 字节向下对齐"以满足 UB 约束。

### 伪代码(原文 §2.2)— 单 tile 处理流程

```
for each tile in input:
    load tile to local memory      # CopyIn: GM → UB
    compute on tile                # Compute:  fp16/bf16 升精度后运算
    store result to global memory  # CopyOut: UB → GM
```

### 伪代码(原文 §6.1)— 核内 Process 主循环

```cpp
coreLength = (GetBlockIdx() == usedCoreNum - 1) ? tailLength : formerLength
tileNum    = ceil(blockLength / tileLength)
tailTileLength = blockLength - (tileNum - 1) * tileLength
for i in [0, tileNum - 1):     CopyIn/Compute/CopyOut(i, tileLength)
最后一块:                       CopyIn/Compute/CopyOut(tileNum - 1, tailTileLength)
```

---

## 【关联】

**(原文)§3 "参考文档"小节列出 7 个 references 子文档**,构成本模板的横向引用图谱:

| 引用路径 | 关联内容 |
|---------|---------|
| `references/hardware-architecture.md` | 硬件层(Core/UB/GM/Cache Line)基础说明 |
| `references/elementwise-tiling.md` | elementwise 算子 tiling 专属指导 |
| `references/reduction-tiling.md` | 归约类算子 tiling 策略 |
| `references/index-tiling.md` | 索引类算子 tiling |
| `references/sort-tiling.md` | 排序类算子 tiling |
| `references/matmul-tiling.md` | 矩阵乘法类(对应 CATLASS 路径)tiling |
| `references/general-tiling-principles.md` | 跨类别的通用 tiling 原则 |

**纵向协同**:
- 本模板为 **`ascendc-operator-design` skill 的输入契约**,其产出再被 **`ascendc-operator-code-gen` skill** 消费(原文末"使用说明"第 5 条);
- §7.1 文件结构(5 个固定路径)与代码生成 skill 的产物布局一一对应,构成上下游衔接;
- §2.3 实现路径选择(AscendC / CATLASS / ACLNN)与 `matmul-tiling.md`、CANN 内置算子文档形成矩阵式引用。

**关于用户提供的"内部链接"**:
```cpp
const at::Tensor &input1,
const at::Tensor &input2,
/* 其他参数 */
```
该片段是模板 §1.1 函数签名中的形参占位代码,非可点击的内部链接,在仓库中通常直接由 `ascendc-operator-code-gen` 解析并替换为具体参数。

---

## 【使用方法】

**(原文)模板使用流程**:

1. **替换占位符**:将全文 `[placeholder]`(如 `[operator_name]`、`[OperatorName]TilingData`)替换为实际算子名。
2. **勾选复选框**:`§1.3 数据类型`、`§2.3 实现路径`、`§3.3 额外 UB 分配`、`§7.1-7.4 检查清单` 中所有 `[ ]` 按实际情况勾选。
3. **填表数值**:`§3.2 Block 级`、`§3.3 tileLength 计算`、`§4.1 Workspace` 三张参数表的"值"列填入实测或计算结果。
4. **代码块参数化**:`§3.1 TilingData` 结构体与 `§6.1 Process()` 循环中的参数名、类型按实际算子调整。
5. **删除不适用节**:若某节不适用(如非 elementwise 算子无 Workspace 16MB 需求)可整节删除。
6. **下游衔接**:设计文档定稿后,调用 `ascendc-operator-code-gen` skill 生成具体 C++ 代码实现(原文末段最后一行)。

**配置项/命令行**:
- 原文未涉及具体 CLI 命令或配置开关。
- 涉及的关键运行时常量:`SYSTEM_WORKSPACE_SIZE = 16 * 1024 * 1024`(常量定义示例见原文 §4.2 代码块)、`UB_SIZE_LIMIT`(通过 AscendC 接口在编码时获取,示例值 192KB)、对齐常量 `512`(Cache Line)、`32`(UB 内部)。
