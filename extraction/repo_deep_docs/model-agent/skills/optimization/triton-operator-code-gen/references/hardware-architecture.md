# 昇腾 NPU 硬件架构

> 仓 `model-agent` · 路径 `skills/optimization/triton-operator-code-gen/references/hardware-architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/optimization/triton-operator-code-gen/references/hardware-architecture.md

# 昇腾 NPU 硬件架构 —— 一体化深度解读

---

## 【定位】

这篇文档面向 Triton-Operator 代码生成场景，系统性描述**昇腾 NPU（A2/A3 芯片）的硬件架构基座**：AI Core 组成与核心类型选择、三级存储层次（GM / L1 / UB）、Cube-Vector 协同数据通路、内存对齐约束、Grid 分核策略以及常见编译/运行问题（如 UB 溢出、coreDim 超限、INT64 退化、FP16 精度损失），为后续算子编写、性能调优与排错提供**硬件级的判断依据**。

---

## 【技术要点】

1. **AI Core 数量与组成**：A2/A3 芯片每张卡通常含 **24 个 AI Core**；每个 AI Core 内置 **1 个 Cube Core + 2 个 Vector Core**，分别绑定 L1 Buffer（1MB，矩阵专用）与 UB（192KB，向量专用）。
2. **核心类型选择 API**：纯向量算子用 `get_npu_vectorcore_num()` 拿 Vector Core 数；矩阵乘法（`tl.dot`）与 CV 混合算子用 `get_npu_aicore_num()` 拿 AI Core 数，原文给出 Python 实现示例（`driver.active.utils.get_device_properties(device)["num_aicore"/"num_vectorcore"]`）。
3. **三级存储与数据搬运**：GM（GB 级 DDR）→ MTE2/MTE3 搬运 → 片上 L1（Cube 专用）/UB（Vector 专用）；Cube→UB 之间的中间结果迁移是 CV 算子（如 Attention QK^T→Softmax→SV）的关键路径。
4. **内存对齐硬性约束**：VV/UB/单值缓冲要求 **32 字节对齐**；CV（Cube-Vector 混合）要求 **512 字节对齐**。
5. **Grid 分核优化环境变量**：当逻辑核数 > 物理核数时，设 `TRITON_ALL_BLOCKS_PARALLEL=1` 自动优化（原文出现在「合并 Grid 分核」一节）。
6. **数据类型陷阱**：Vector Core 的 ADD/CMP 不支持 **INT64/INT32**（会退化为标量运算），应改用 **FP32 比较**；FP16 输入做归约易丢精度，需在 FP32 下完成累加后再降精度输出。

---

## 【关键机制与数据】

### 一、AI Core 与核心选择机制（原文）

- **原文**："昇腾 NPU 的计算核心是 AI Core，A2/A3 芯片通常有 **24 个 AI Core**。"
- **原文**：每个 AI Core 含 Cube Core × 1（矩阵乘）+ Vector Core × 2（向量/归约），分别绑定 L1 Buffer（1MB）与 UB（192KB）。
- **机制**：算子类型决定调度路径——`tl.dot` 走 Cube/Core，元素级/归约走 Vector Core，CV 类（Attention、LayerNorm+MatMul 等）需要 Cube 与 Vector 协同，并通过 workspace 在 L1↔UB 之间传递中间结果。

### 二、三级存储数据流（原文）

```
GM ──(MTE2)──► L1 ──► Cube Core ──► L1 ──(MTE3)──► GM   （矩阵路径）
GM ──(MTE2)──► UB  ──► Vector Core ──► UB ──(MTE3)──► GM  （向量路径）
GM ──► L1 ──► Cube ──► L1/UB ──► Vector ──► UB ──► GM   （CV 协同：QK^T→Softmax→SV）
```

- **原文**：GM 为 GB 级 DDR，容量大但延迟高；L1 与 UB 为片上高速缓存。
- **原文**："Cube 计算结果需要从 L1 转移到 UB，Vector Core 处理 Softmax 等向量操作，使用 workspace 缓存中间结果。"

### 三、Grid 与核数映射（原文）

- **机制**：当逻辑 block 数超过物理 AI Core 数（通常 24）时，单 block 对单物理核已无法一一对应，需启用自动并行化策略。
- **原文**："当逻辑核数大于物理核数时，使用 `TRITON_ALL_BLOCKS_PARALLEL=1` 自动优化"。

### 四、性能与报错阈值（原文给出的具体数据）

- **原文**：UB 溢出错误信息形如 `ub overflow, requires xxxx bits while 1572684 bits available!`（即上限 **1,576,284 bits ≈ 192.2 KB**，与 UB 标称 192KB 一致）。
- **原文**：coreDim 上限为 `UINT16_MAX = 65535`，即单个 launch 的 grid 不得超过 **65535**。
- **原文**：Vector ADD 不支持 INT64，Vector CMP 不支持 INT64/INT32，会退化为标量。
- **原文**：L1 Buffer 通常 **1MB**，UB 通常 **192KB**（A2/A3）。

> 注：以上数字均直接出自原文，未做推导或外推。

---

## 【表格解读】

### 表格 1：AI Core 组成（原文逐字还原）

| 组件 | 数量 | 功能 | 专用缓存 |
|------|------|------|----------|
| **Cube Core** | 1 | 矩阵乘法计算 | L1 Buffer (1MB) |
| **Vector Core** | 2 | 向量计算（逐元素、归约等） | UB (192KB) |

**逐行解读：**

- **Cube Core / 1 / 矩阵乘法计算 / L1 Buffer (1MB)**：单个 AI Core 仅配备 1 个 Cube 单元，承担 `tl.dot` 一类的矩阵乘；其私有缓存为片上 L1，容量 1MB，决定了单次可驻留的矩阵分块大小上限。
- **Vector Core / 2 / 向量计算（逐元素、归约等）/ UB (192KB)**：Vector 数量是 Cube 的 2 倍，说明昇腾 NPU 在设计上倾向同时支撑更多并行向量任务；UB 192KB 是 Vector 侧访存带宽的"瓶颈容量"，BLOCK_SIZE/UB 占用预算要按此约束。

---

### 表格 2：核心类型选择（原文逐字还原）

| 算子类型 | 使用核心 | 获取核数方法 |
|----------|----------|--------------|
| 纯向量计算（逐元素、归约） | Vector Core | `get_npu_vectorcore_num()` |
| 矩阵乘法（tl.dot） | AI Core | `get_npu_aicore_num()` |
| CV 混合算子 | AI Core + Vector Core | `get_npu_aicore_num()` |

**逐行解读：**

- **纯向量计算 → Vector Core / `get_npu_vectorcore_num()`**：元素级 op、归约 op 不消耗 Cube 资源，调度目标是 2× AI Core 数（每 AI Core 内 2 个 Vector）。
- **矩阵乘法 → AI Core / `get_npu_aicore_num()`**：`tl.dot` 必须落到 Cube，因此调度目标是 1× AI Core 数。
- **CV 混合 → AI Core + Vector Core / `get_npu_aicore_num()`**：Cube 与 Vector 协同时，瓶颈仍由 Cube 决定（因为 Cube 数量更少），故调度目标按 AI Core 数取，并需预留 L1↔UB 通路与 workspace。

---

### 表格 3：内存对齐规则（原文逐字还原）

| 场景 | 对齐要求 | 说明 |
|------|----------|------|
| VV（Vector-Vector） | 32 字节 | 纯向量计算 |
| CV（Cube-Vector） | 512 字节 | 矩阵+向量混合计算 |
| UB 缓冲区 | 32 字节 | 所有 UB 分配 |
| 单值缓冲区 | 32 字节 | 均值、方差等归约结果 |

**逐行解读：**

- **VV / 32 字节**：纯向量访存以 32 字节为基本对齐粒度，对应 Vector Core 的高效访存事务。
- **CV / 512 字节**：矩阵+向量混合路径要求更严（512 字节 = 32 字节 × 16），未对齐会触发额外搬运开销，文档在「UB 溢出」一节将"非对齐访存导致额外开销"列为成因之一。
- **UB 缓冲区 / 32 字节**：所有 UB 分配都需按 32 字节对齐，否则可能踩到 UB 容量边界。
- **单值缓冲区 / 32 字节**：均值、方差等归约标量结果虽小，但同样需 32 字节对齐以保证访存效率。

---

### 表格 4：Vector Core 不支持的数据类型（原文逐字还原）

| 操作 | 不支持的数据类型 |
|------|------------------|
| Vector ADD | int64 |
| Vector CMP | int64/int32 |

**逐行解读：**

- **Vector ADD / int64**：长整型加法会被降级为标量执行，性能与吞吐会显著劣化。
- **Vector CMP / int64/int32**：整型比较在 32 位以下与 64 位均不被原生支持，需改用 FP32 做比较运算（原文代码示例将 `cols` 转 `tl.float32` 再与 `N` 比较）。

---

## 【公式解读】

**原文无公式。**

文档中出现的仅为 ASCII 数据通路图与 Python/Triton 代码片段，未给出任何数学公式（如 MAC 数、带宽利用率、Roofline 等），故不作 LaTeX 还原。

---

## 【关联】

文档开头标注："(无)" 内部链接。但从内容自洽性出发，可梳理出如下**文档内部的特性/模块上下游关系**（皆为同一文件内的章节引用，不臆造外部链接）：

- **AI Core 组成（Cube/Vector/L1/UB）↔ 存储层次（GM/L1/UB）**：硬件资源表定义了 L1 与 UB 的归属（Cube vs Vector），存储层次章节则展开其容量、用途，构成"硬件组件 → 存储资源"的下行细化。
- **存储层次 ↔ 数据通路**：三级存储是数据通路的载体；向量通路、矩阵通路、CV 通路分别对应 L1 / UB 路径上的搬运顺序。
- **核心类型选择 ↔ 数据通路 ↔ Grid 分核策略**：算子类型决定走 Cube 还是 Vector，对应不同的数据通路，进一步影响逻辑 block 数是否超过 24 个 AI Core 的物理上限，进而触发 `TRITON_ALL_BLOCKS_PARALLEL=1`。
- **内存对齐 ↔ UB 溢出 / coreDim 超限**：对齐不达标会作为「UB 溢出」的成因之一；coreDim 超限则与 Grid 分核优化互为同义问题域。
- **数据类型优化（INT64/FP16）↔ 精度损失 / Vector ADD-CMP 退化**：数据类型章节既是性能优化项，又是「常见问题」中精度损失与算子退化的根因解释。
- **常见问题章节 ↔ 上述所有章节**：UB 溢出回链到「存储层次/UB」；coreDim 超限回链到「Grid 分核策略」；精度损失回链到「数据类型优化」，构成"问题 → 根因 → 调优手段"的闭环。

---

## 【使用方法】

以下命令与配置项均直接取自原文：

1. **读取物理核心数（Python）**
   ```python
   import torch
   import triton.runtime.driver as driver

   def get_npu_aicore_num():
       device = torch.npu.current_device()
       return driver.active.utils.get_device_properties(device)["num_aicore"]

   def get_npu_vectorcore_num():
       device = torch.npu.current_device()
       return driver.active.utils.get_device_properties(device)["num_vectorcore"]
   ```
   用途：构造 Grid、选择调度目标。

2. **启用合并 Grid 自动并行化（环境变量）**
   ```bash
   export TRITON_ALL_BLOCKS_PARALLEL=1
   ```
   用途：逻辑核数 > 物理核数（> 24）时自动优化；也是 coreDim 超限（> 65535）时的解决方案之一。

3. **数据类型改写（FP32 比较替代 INT64/INT32）**
   ```python
   # 优化前：int64 比较，退化为标量
   cols = tl.arange(0, BLOCK_N)
   xbar = tl.where(cols < N, x - mean, 0.0)

   # 优化后：转为 FP32 比较
   cols_cmp = cols.to(tl.float32)
   xbar = tl.where(cols_cmp < N, x - mean, 0.0)
   ```

4. **常见问题处置（原文给出的工程动作）**
   - UB 溢出（`requires xxxx bits while 1572684 bits available!`）：① 减小 BLOCK_SIZE；② 使用核内循环切分；③ 确保访存对齐。
   - coreDim 超限（`coreDim=xxxx can't be greater than UINT16_MAX`）：① 增大 BLOCK_SIZE；② 设置 `TRITON_ALL_BLOCKS_PARALLEL=1`；③ 使用核内循环减少 grid 数量。
   - 精度损失（FP16 输入不准确）：① 归约前升精度到 FP32；② 在 FP32 下完成所有计算；③ 最后降精度到输出类型。
