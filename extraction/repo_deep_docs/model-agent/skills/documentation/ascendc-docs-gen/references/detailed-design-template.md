# {算子名称} 设计文档

> 仓 `model-agent` · 路径 `skills/documentation/ascendc-docs-gen/references/detailed-design-template.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/documentation/ascendc-docs-gen/references/detailed-design-template.md

# 深度解读：AscendC 算子详细设计文档模板

## 【定位】

本文档是一份**昇腾 AscendC 自定义算子详细设计文档的编写模板**，用于指导开发者按统一结构填写算子的基本信息、架构视图、模板划分、TilingData 设计、API 映射、内存管理、性能优化与风险评估等章节，从而产出可落地、可评审、可交付的设计材料。

---

## 【技术要点】

1. **四层模块架构**：算子按 `op_api`（ACLNN 接口层）→ `op_host`（Host 侧 Tiling/Shape 推导）→ `op_kernel`（NPU Kernel 实现）→ `op_graph`（图模式适配）的层级组织，每层职责与对应核心文件路径在 §2.1 明确定义。

2. **双架构兼容**：模板显式区分 `arch22`（DAV_2201，对应 Ascend910B / Ascend910_93）与 `arch35`（DAV_3510，对应 Ascend950DT / Ascend910PR），Tiling 与 Kernel 代码均按这两个目录分文件维护。

3. **TilingKey 多模板机制**：通过模板参数 `D_T_X ∈ {half, float}`、`TILE_NUM ∈ {1, 4, 8}`、`IS_SPLIT ∈ {false, true}` 的笛卡尔积组合出多个编译期模板实例，由 Host 侧 `ASCENDC_TPL_SEL_PARAM` 选择触发。

4. **TilingData 结构体**：Kernel 侧通过 `REGISTER_TILING_DEFAULT` + `GET_TILING_DATA_WITH_STRUCT` 拿到由 Host 侧 `GetTilingData<T>()` 填充的结构体，承载 `totalLength` / `tileLength` 等切分参数。

5. **UB 容量硬约束**：所有 Buffer 大小之和必须 ≤ 实际可用 UB 空间，DAV_2201 验证公式 `sum(buffers) ≤ 184 * 1024`、DAV_3510 验证公式 `sum(buffers) ≤ 248 * 1024`；查询方式为编译时常量 `GetUBSizeInBytes()`、运行时值 `GetRuntimeUBSize()`。

6. **API 验证强制流程**：每个 Ascend C API 必须用通配符 `ls asc-devkit/docs/api/context/ | grep -i "^{APIName}"` 检索官方文档并填写"API 验证记录表"，并通过 6 项检查清单确认对齐、类型、签名、平台可用性。

---

## 【关键机制与数据】

### 工作原理（运行视图，原文 §2.3）

算子调用流程如下，**原文**：

```
aclnn${OpName}GetWorkspaceSize()
     │
     ├──▶ op_host/_def.cpp: 获取算子定义
     ├──▶ op_host/_tiling.cpp: 计算 Tiling 参数 → 生成 TilingData
     │
     ▼
aclnn${OpName}()
     │
     ├──▶ 加载 Kernel 二进制
     ├──▶ 传递 TilingData 到 Device
     │
     ▼
NPU Device 执行
     ├──▶ 读取 TilingData
     ├──▶ GM → UB 数据搬运
     ├──▶ 执行计算逻辑
     └──▶ UB → GM 结果写回
```

**数据流**（原文）：

```
GM (Global Memory)
  │
  │ DataCopy (GM → UB)
  ▼
UB (Unified Buffer)
  │
  │ 计算 (ALU/Vector/Cube)
  ▼
UB (Unified Buffer)
  │
  │ DataCopy (UB → GM)
  ▼
GM (Global Memory)
```

### 性能/容量数据（原文明确给出的硬数字）

- **DAV_2201 平台**：总 UB 192 KB、向量可用 184 KB、系统保留 8 KB → 验证公式 `sum(buffers) ≤ 184 * 1024`（原文 §3.3.8）。
- **DAV_3510 平台**：总 UB 248 KB、向量可用 248 KB、系统保留 0 KB → 验证公式 `sum(buffers) ≤ 248 * 1024`（原文 §3.3.8）。
- **DataCopy 约束**：GM→UB 时 `stride=bytes`、32B 对齐；UB→GM 无 padding 参数（原文 §3.3.4）。
- **模板参数取值范围**：`TILE_NUM ∈ {1, 4, 8}`、`IS_SPLIT ∈ {false, true}`（原文 §3.1）。
- **内存示例大小**：输入 UB / 输出 UB 各为 `tileLength * sizeof(T)`（原文 §3.3.7）。

---

## 【表格解读】

### 表 1：算子基本信息（原文 §1.1）

| 项目 | 内容 |
|-----|------|
| 算子名称 | {算子名称} |
| 算子类别 | {Reduction / Elementwise / Broadcast / Conversion / MatMul / ...} |
| 支持数据类型 | {fp16 / fp32 / bf16 / ...} |
| **目标芯片** | {Ascend910B / Ascend910_93 / Ascend950DT / Ascend910PR} |
| **目标架构** | {arch22 / arch35} |

**逐行解读**：模板要求填写算子的元数据。"目标芯片"与"目标架构"加粗，意味着是评审关注的强约束项：芯片型号与架构标识（arch22 ↔ DAV_2201；arch35 ↔ DAV_3510）必须严格匹配，否则后续 Tiling 与 Kernel 文件的目录归属（`op_host/arch22/`、`op_kernel/arch35/` 等）无法对齐。

---

### 表 2：模块职责（原文 §2.1）

| 模块 | 职责 | 核心文件 |
|------|------|---------|
| **op_api** | ACLNN 接口层：对外暴露算子调用接口，处理输入校验、类型转换、内存管理 | `aclnn_${op}.h`, `aclnn_${op}.cpp`, `${op}.h`, `${op}.cpp` |
| **op_host** | Host 侧逻辑：算子定义、Tiling 切分、Shape 推导 | `_def.cpp`, `_tiling.cpp`, `_tiling.h`, `_infershape.cpp` |
| **op_kernel** | Kernel 侧 NPU 计算逻辑 | `.cpp`, `.h`, `_tiling_key.h`, `_tiling_data.h` |
| **op_graph** | 图模式适配，定义算子 IR 原型和类型推导 | `_proto.h`, `_graph_infer.cpp` |

**逐行解读**：定义四层模块边界。`op_api` 是用户接触面，封装 ACLNN 调用入口；`op_host` 在 CPU 侧完成 Tiling 决策；`op_kernel` 是 NPU 上的实际计算实现，含 TilingKey/TilingData 的结构定义；`op_graph` 是图引擎接入的可选模块。模块依赖关系见原文 ASCII 图：`aclnn${Op}GetWorkspaceSize() → op_host`，`aclnn${Op}() → op_kernel`。

---

### 表 3：模板参数定义（原文 §3.1）

| 参数 | 类型 | 取值范围 | 说明 |
|-----|------|---------|------|
| D_T_X | DataType | {half, float} | 输入X数据类型 |
| TILE_NUM | UINT | {1, 4, 8} | 切分数量 |
| IS_SPLIT | BOOL | {false, true} | 是否切分 |

**逐行解读**：这三个参数共同决定 Kernel 模板实例。`D_T_X` 决定浮点精度路径；`TILE_NUM` 控制单次循环的切分粒度（最大 8）；`IS_SPLIT` 是布尔开关，触发不同 Process 路径（模板一示例中 `IS_SPLIT=0` 走 `Process1`，`IS_SPLIT=1` 走 `Process2`）。

---

### 表 4：模板划分表（原文 §3.1）

| 模板 | 触发条件 | 模板参数 | 适用场景 |
|-----|---------|---------|---------|
| 模板一 | {条件描述，如: float + small_shape} | `D_T_X=float, TILE_NUM=1, IS_SPLIT=false` | 基础计算路径 |
| 模板二 | {条件描述，如: half + large_shape} | `D_T_X=half, TILE_NUM=8, IS_SPLIT=true` | 优化计算路径 |
| 模板三 | {条件描述} | {...} | 特殊场景A |
| ... | ... | ... | ... |

**逐行解读**：模板一行示例展示了"小 shape + float → 不切分"路径；模板二示例展示了"大 shape + half → 切 8 份"路径。模板三起为占位扩展行，开发者按需追加。`...` 行说明模板数量不固定，按算子复杂度自适应。

---

### 表 5：API 映射（原文 §3.3.4）

| 计算步骤 | Ascend C API | 参数签名 | 平台验证 | 约束说明 | 替代方案 |
|---------|-------------|---------|---------|---------|---------|
| 数据搬入 | DataCopyPad\<T\> | (dst, src, DataCopyExtParams, DataCopyPadExtParams) | ✅ {DAV_2201/DAV_3510} | GM→UB: stride=bytes; 32B对齐 | - |
| {计算步骤} | {API\<T, Template\>} | (完整参数列表) | ✅/❌ {DAV_2201/DAV_3510} | {对齐/类型/尺寸约束} | {不可用时的替代} |
| 数据搬出 | DataCopyPad\<T\> | (dst, src, DataCopyExtParams) | ✅ {DAV_2201/DAV_3510} | UB→GM 无 padding 参数 | - |

**逐行解读**：示例行给出搬入/搬出用 `DataCopyPad<T>`，搬入带 `DataCopyPadExtParams`（处理非 32B 对齐尾部），搬出不带 padding 参数。`平台验证`列用 ✅/❌ 标注在 DAV_2201 / DAV_3510 上的可用性，这是关键回归点。

---

### 表 6：API 验证记录（原文 §3.3.5）

| API 名称 | 官方文档路径 | 通配符搜索结果 | 验证状态 | 备注 |
|---------|-------------|---------------|---------|------|
| {API名称} | docs/api/context/{API}.md | {文件列表} | ✅ 已验证 / ❌ 不可用 / ⚠️ 有条件 | {说明} |

**逐行解读**：该表强制要求每个 API 留下"可追溯证据"——通过 `ls asc-devkit/docs/api/context/ | grep -i "^{APIName}"` 通配符搜索结果作为证据留存，避免凭记忆编码。

---

### 表 7：内存管理（原文 §3.3.7）

| 内存区域 | 大小计算 | 说明 |
|---------|---------|------|
| **输入 UB** | `tileLength * sizeof(T)` | 单次搬入数据块 |
| **输出 UB** | `tileLength * sizeof(T)` | 单次计算结果块 |
| **临时缓冲区** | {大小} | {用途说明} |
| **Workspace** | {大小} | Global Memory 工作区 |

**逐行解读**：每个 Buffer 都需显式给出"大小 + 用途"。输入与输出 UB 大小计算式一致，均依赖 `tileLength` 与类型尺寸 `sizeof(T)`，这是 Tiling 阶段确定的硬性物理占用。

---

### 表 8：UB 容量验证（原文 §3.3.8）

| 平台 | 总 UB | 向量可用 | 系统保留 | 验证公式 |
|------|-------|---------|---------|---------|
| DAV_2201 (Ascend910B/Ascend910_93) | 192 KB | 184 KB | 8 KB | `sum(buffers) ≤ 184 * 1024` |
| DAV_3510 (Ascend950DT/Ascend910PR) | 248 KB | 248 KB | 0 KB | `sum(buffers) ≤ 248 * 1024` |

**逐行解读**：两条验证公式是模板强制项。DAV_2201 上系统保留了 8 KB，实际可用比总容量少 8 KB；DAV_3510 上没有系统保留，可用 = 总容量。所有 InitBuffer 调用的总和必须落在这两个公式之内，否则 Kernel 会在 UB 分配阶段失败。

---

### 表 9：用户调用方式（原文 §2.4）

| 调用方式 | 说明 |
|---------|------|
| **ACLNN 调用** | 通过 aclnn 接口直接调用 |
| **图模式调用** | 通过 GE 图引擎调用 |

**逐行解读**：算子对外暴露两条入口——ACLNN（算子直调）和图模式（GE 图引擎）。ACLNN 调用流程为 `GetWorkspaceSize → 分配 workspace → 执行`；图模式流程为 `定义 IR 图 → 编译优化 → 执行计算图`。

---

### 表 10：迭代规划（原文 §7）

| 迭代 | 目标 | 代码开发 | UT开发 | ST用例 |
|------|------|---------|--------|-------|
| 迭代一 | 骨架搭建 | 单TilingKey + 预埋骨架 + 单dtype | 核心路径用例 | L0标准用例（基础shape + 单dtype） |
| 迭代二 | 策略完善 | 多TilingK...（原文截断） | | |

**逐行解读**：迭代一聚焦"骨架 + 单一路径验证"，仅支持一种 TilingKey 与一种 dtype，跑通基础 shape。迭代二原文中表格被截断（原文以"多TilingK"结尾），仅可看到"策略完善"目标与"多 TilingKey"代码方向。

---

## 【公式解读】

**原文无实际数学公式**。文档中第 1.3 节标题为"数学公式"，内容仅为占位符 `{数学公式定义}`，要求开发者根据算子功能自行填入；其他章节也未给出 LaTeX 或伪代码形式的公式。

可识别的**等价表达式**（实为代码 / 验证公式，非数学公式）：

- `tileLength * sizeof(T)`（§3.3.7）— 各 Buffer 大小计算式，其中 `tileLength` 为单次处理长度（来自 TilingData），`T` 为数据类型，`sizeof(T)` 取该类型的字节大小。
- `sum(buffers) ≤ 184 * 1024`（§3.3.8，DAV_2201）— 所有 Buffer 字节总和须 ≤ 184 × 1024 = 188416 字节。
- `sum(buffers) ≤ 248 * 1024`（§3.3.8，DAV_3510）— 所有 Buffer 字节总和须 ≤ 248 × 1024 = 253952 字节。

---

## 【关联】

原文未提供文末内部链接列表（已标注"无"），但文档内部存在以下**显式交叉引用**：

1. **§3.1 TilingKey 机制**明确指向外部技能文档：
   > 参考 `ascendc-custom-op-enhance` 技能的 `advanced-guide.md` 第 47-103 行
   这是模板对多模板参数机制最权威的解释来源，TilingKey 的设计语义应回查该文件。

2. **§3.3.5 API 验证记录**指向本地 devkit 文档路径：
   > 使用通配符搜索 `ls asc-devkit/docs/api/context/ | grep -i "^{APIName}"`
   表明 API 是否可用、签名细节、对齐约束都必须以 `asc-devkit/docs/api/context/` 下的官方文档为准，而非凭经验判断。

3. **§3.3.8 UB 容量**指引运行时查询接口：
   - 编译期常量：`GetUBSizeInBytes()`
   - 运行时值：`GetRuntimeUBSize()`
   这两个 API 是 UB 容量验证的运行时补充手段。

4. **四层模块依赖图**（§2.1）建立了 `op_api ↔ op_host ↔ op_kernel ↔ op_graph` 的调用链；`op_graph` 在 §6 交付件清单中标注为"可选（图模式需要）"，表明该模块仅在启用 GE 图引擎时为必需项。

---

## 【使用方法】

原文未提供"启用 / 启动命令"类的使用说明——本文档是**模板**而非可执行工具，使用方式即"按模板填写"，涉及的关键填写规范如下：

1. **占位符替换**：将所有 `${op_name}` / `${Op}` / `{算子名称}` / `{条件描述}` 等占位符替换为实际算子名（如 `AddCustom`）与真实条件。
2. **架构目录归属**：根据 §1.1 选择的 `arch22` / `arch35`，将 §2.2 中的目录树按 `op_host/arch22/` 或 `op_host/arch35/` 分文件落地。
3. **TilingKey 注册**：
   - Host 侧：`ASCENDC_TPL_SEL_PARAM(context, D_T_X, TILE_NUM, IS_SPLIT);`
   - Kernel 侧：`REGISTER_TILING_DEFAULT(${op_name}TilingData);`
4. **TilingData 传递**：
   - Host 侧：`auto tiling = context->GetTilingData<${op_name}TilingData>();`
   - Kernel 侧：`GET_TILING_DATA_WITH_STRUCT(${op_name}TilingData, tilingData, tiling);`
5. **UB 容量校验流程**（§3.3.8 验证检查清单原文）：
   - [ ] 已用通配符搜索 API 所有变体文件
   - [ ] 已确认 API 在目标芯片架构（{arch}）上可用
   - [ ] 已确认 API 支持所需的数据类型（{dtypes}）
   - [ ] 已确认参数签名与官方文档一致
   - [ ] 已确认 tmpBuffer/对齐等约束条件
   - [ ] 如 API 不可用，已确定替代方案
6. **构建入口**：仓库根的 `CMakeLists.txt`（§2.2 目录树中标注为"# 构建配置"），与 `op_host/`、`op_kernel/`、`tests/` 一并列入 §6"必需"交付件；`op_graph/` 为可选。
