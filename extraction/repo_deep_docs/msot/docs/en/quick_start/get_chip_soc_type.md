# Method for Obtaining the SoC Model of Ascend Chips

> 仓 `msot` · 路径 `docs/en/quick_start/get_chip_soc_type.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/en/quick_start/get_chip_soc_type.md

# 一体化深度解读:Ascend 芯片 SoC Model 获取指南

---

## 【定位】

本文档提供了一套**从命令行查询 Ascend A2/A3 系列昇腾芯片 SoC 模型的标准方法**,通过 `npu-smi` 工具分三步(NPU ID/Chip ID → Chip Name → 拼接 SoC Model)获取唯一标识芯片的字符串(如 `Ascend910B4`、`Ascend910_9392`),供上层工具基于芯片型号做差异化处理。

---

## 【技术要点】

1. **芯片代际区分**:A2(基于 Atlas A2 训练/推理产品)与 A3(基于 Atlas A3 训练/推理产品)是产品代际,SoC 模型格式存在差异,A2 拼接为 `{Chip Type}{Chip Name}`,A3 拼接为 `{Chip Name}_{NPU Name}`。
2. **第一步命令**:`npu-smi info -m` 用于获取 NPU ID、Chip ID、Chip Logic ID、Chip Name 的对应关系,默认假设服务器上所有芯片类型一致,故取**第一行数据**(本例 NPU ID=0, Chip ID=0)。
3. **第二步命令**:`npu-smi info -t board -i <NPU ID> -c <Chip ID>`,其中 `-i` 取 NPU ID、`-c` 取 Chip ID;该命令会输出 Chip Type、Chip Name(A2 环境),或 NPU Name、Chip Name(A3 环境)。
4. **A2/A3 字段差异**:
   - 两者都有 **Chip Name**;
   - **A3 有 NPU Name,A2 没有 NPU Name**;
   - **A2 有 Chip Type,A3 没有 Chip Type**。
5. **SoC Model 拼接规则**:将第二步取得的字段按代际规则字符串拼接,得到最终 SoC 模型标识。
6. **下游用途**:获取到的 SoC Model 需**记录下来**,供后续步骤使用(原文明确指出 "will be needed in subsequent steps")。

---

## 【关键机制与数据】

### 工作原理

整个获取流程是一个**两阶段标识符解析 → 字符串拼接**的过程:

1. **物理/逻辑 ID 解析阶段**:`npu-smi info -m` 枚举所有 NPU 设备并按四列对齐输出(NPU ID、Chip ID、Chip Logic ID、Chip Name)。其中 Chip Logic ID 对非 Mcu 芯片有效(值为 `0` 或 `1`),对 Mcu 协处理器显示为 `-`。
2. **详细板卡信息查询阶段**:`npu-smi info -t board -i 0 -c 0` 在选定 (NPU ID, Chip ID) 后进一步查询板卡详细信息;输出的字段集合因芯片代际(A2/A3)而不同。
3. **拼接阶段**:根据代际使用不同的模板将字段拼接成最终 SoC 字符串。

### 原文数据

- 原文示例输出中 NPU ID=0 与 NPU ID=1 各有两条记录(Chip ID 0 和 1),其中 Chip ID=1 的 Chip Name 为 `Mcu`(表示管理控制单元,非主计算芯片,故 Chip Logic ID 显示为 `-`)。
- 第一行可用的 SoC 原始组件:NPU ID=0、Chip ID=0、Chip Logic ID=0、Chip Name=`Ascend 910B4`。
- A2 示例拼接结果:`Chip Type: Ascend` + `Chip Name: 910B4` → `Ascend910B4`。
- A3 示例拼接结果:`Chip Name: Ascend910` + `NPU Name: 9392` → `Ascend910_9392`。

### 数据流

```
npu-smi info -m          →  NPU ID + Chip ID
npu-smi info -t board    →  Chip Type / Chip Name / NPU Name
模板拼接                  →  SoC Model (用于后续步骤)
```

---

## 【表格解读】

原文无标准 markdown 表格,但包含两组关键的命令输出(对齐列格式),逐字还原如下并逐行解读:

### 表 1:`npu-smi info -m` 输出(NPU ID/Chip ID 枚举)

| NPU ID | Chip ID | Chip Logic ID | Chip Name   |
|--------|---------|---------------|-------------|
| 0      | 0       | 0             | Ascend 910B4|
| 0      | 1       | -             | Mcu         |
| 1      | 0       | 1             | Ascend 910B4|
| 1      | 1       | -             | Mcu         |

**逐行解读**:
- 第 1 行 (0,0,0,Ascend 910B4):NPU 0 上的主计算芯片,Chip Logic ID=0,这是**默认取用的目标行**。
- 第 2 行 (0,1,-,Mcu):NPU 0 上的协处理器(Mcu,Management Control Unit),Chip Logic ID 显示 `-` 表示无逻辑编号。
- 第 3 行 (1,0,1,Ascend 910B4):NPU 1 上的主计算芯片,Chip Logic ID=1(与 NPU 0 的主芯片不同编号)。
- 第 4 行 (1,1,-,Mcu):NPU 1 上的协处理器。
- **规律——每块 NPU 对应 1 个主芯片 + 1 个 Mcu**;Chip Logic ID 仅对主芯片有效。

### 表 2:A2 环境 `npu-smi info -t board -i 0 -c 0` 输出

| 字段        | 取值     |
|-------------|----------|
| NPU ID      | 0        |
| Chip ID     | 0        |
| Chip Type   | Ascend   |
| Chip Name   | 910B4    |

**逐行解读**:
- NPU ID / Chip ID:回显定位参数。
- Chip Type = `Ascend`:作为 SoC 拼接的前缀。
- Chip Name = `910B4`:作为 SoC 拼接的后缀,与 Chip Type 拼接为 `Ascend910B4`。

### 表 3:A3 环境 `npu-smi info -t board -i 0 -c 0` 输出

| 字段        | 取值        |
|-------------|-------------|
| NPU ID      | 0           |
| NPU Name    | 9392        |
| Chip ID     | 0           |
| Chip Name   | Ascend910   |

**逐行解读**:
- NPU Name = `9392`:A3 专属字段(用于 SoC 后缀)。
- Chip Name = `Ascend910`:A3 的 Chip Name 已含 "Ascend" 前缀,与 NPU Name 用 `_` 拼接为 `Ascend910_9392`。

---

## 【公式解读】

原文无 LaTeX 公式,但给出两套**字符串拼接模板**(可视为伪代码公式),逐字保留并解释:

### 公式 1(A2 芯片 SoC Model)

```
SoC_Model = {Chip Type}{Chip Name}
```

**符号说明**:
- `{Chip Type}`:占位符,对应 A2 环境下 `npu-smi info -t board` 输出的 `Chip Type` 字段值(A2 示例为 `Ascend`)。
- `{Chip Name}`:占位符,对应同命令输出的 `Chip Name` 字段值(A2 示例为 `910B4`)。
- 两者直接**首尾相接,无分隔符**。
- 实际产出:`Ascend` + `910B4` = `Ascend910B4`。

### 公式 2(A3 芯片 SoC Model)

```
SoC_Model = {Chip Name}_{NPU Name}
```

**符号说明**:
- `{Chip Name}`:占位符,对应 A3 环境下 `npu-smi info -t board` 输出的 `Chip Name` 字段值(A3 示例为 `Ascend910`)。
- `_`:字面量下划线,作为分隔符(A3 模板独有)。
- `{NPU Name}`:占位符,对应 A3 环境下同命令输出的 `NPU Name` 字段值(A3 示例为 `9392`),A2 不含此字段。
- 实际产出:`Ascend910` + `_` + `9392` = `Ascend910_9392`。

---

## 【关联】

文档本身为**前导步骤**(标题含 "quick_start"),其作用是为后续步骤提供输入,关系如下:

- **上游**:**无**(本文档即起点,依赖的仅有 `npu-smi` 工具与本地硬件)。
- **下游**(原文明确指出):获取到的 SoC Model 字符串 **"will be needed in subsequent steps"**(后续步骤需要),但本文未给出具体下游模块名称。
- **横向上下游**:
  - 与 **Atlas A2 训练/推理产品** 关联(对应 A2 SoC 格式);
  - 与 **Atlas A3 训练/推理产品** 关联(对应 A3 SoC 格式);
  - 与 **上层工具的差异化处理机制** 关联(上层工具按 SoC 模型做分支处理,如 `Ascend910B4`)。
- **文档目录定位**:处于 `docs/en/quick_start/` 路径下,属于**快速开始系列**文档之一,推测与 `msot` 仓的部署/调优前置准备流程绑定。

> 注:原文未提供内部链接(用户已确认"无"),故无更多锚点关系可解析。

---

## 【使用方法】

### 启用方式

仅依赖 `npu-smi` 系统命令(随昇腾驱动/固件安装),无需额外启用。

### 完整步骤与配置项

1. **枚举所有 NPU/Chip**:
   ```shell
   npu-smi info -m
   ```
   读取第一行(或自行指定)的 NPU ID 与 Chip ID。

2. **查询板卡详细信息**:
   ```shell
   npu-smi info -t board -i <NPU ID> -c <Chip ID>
   ```
   参数说明:
   - `-i`:NPU ID(取自步骤 1);
   - `-c`:Chip ID(取自步骤 1);
   - `-t board`:查询类型为 board(板卡信息)。

3. **按代际拼接 SoC Model**:
   - A2 → `Chip Type` + `Chip Name`(例:`Ascend910B4`);
   - A3 → `Chip Name` + `_` + `NPU Name`(例:`Ascend910_9392`)。

4. **记录结果**:原文明确要求 "please record it, as it will be needed in subsequent steps"。

### 配置项

原文未涉及任何配置文件项(如 ini/json/yaml),所有操作均通过命令行参数完成。
