# Op Mapping 教程 v2

> 仓 `msmodeling` · 路径 `docs/perf_database/tutorial/OP_PLUGIN_MAPPING_TUTORIAL.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/perf_database/tutorial/OP_PLUGIN_MAPPING_TUTORIAL.md

# Op Mapping 教程 v2 — 一体化深度解读

---

## 【定位】

本文档系统性解决「如何让 TensorCast (TC) 虚拟算子语义对齐到真实 NPU profiling 内核类型」这一核心问题——即通过维护 `op_mapping.yaml` 这一桥接文件，使 `EmpiricalPerformanceModel` 能够以真实 profiling 延迟替代解析估算，从而打通 *PyTorch 算子 → OpPlugin → aclnn → CANN L0 OPTYPE → NPU kernel* 全链路的可追溯映射，并为 8 种常见 shape 差异、CANN 版本演化、5 类查询分发提供诊断与维护规范。

---

## 【技术要点】

1. **映射文件三态互斥分类**：每个条目必须恰好属于 `kernel_type` (compute)、`composite: true` (分解为 `sub_kernels`)、`zero_cost: true` (latency=0) 三者之一——这是条目存在性的硬约束，避免查询路径二义性。

2. **5 路查询分发**：基于条目类型 + 类别字段，`ProfilingDataSource` 在 `_lookup_composite` / `_lookup_comm` / `_lookup_attention` / `zero_cost=0` / `_lookup_compute` 之间做单选路由；额外触发条件为 `category: communication`、`query_mode: attention_special`、`query_mode: elementwise` 三种修饰字段。

3. **核心关键标识符**：`kernel_details.csv` 中的 `Type` 列 ≡ CANN OPTYPE ≡ `op_mapping.yaml` 中的 `kernel_type`——三者完全等价，是跨模块联接的"主键"。

4. **Name 列三段式结构**：`aclnnAPI_DispatchFunc_L0OpType`，第 3 段 `=` Type 列；这是从 profiling 数据反查 aclnn 注册路径的直接线索。

5. **元素算子特殊查询模式**：`query_mode: elementwise` 用输出形状匹配 + dtype 松弛缩放（FP32 → BF16 × 2.0 字节比），无需 `tc_input_count`；典型受众为 `aten.add.Tensor / aten.mul.Tensor / aten.div.Tensor` 等内存带宽受限算子。

6. **CANN 版本兼容策略**：使用 `alternate_kernel_types: [Type1, Type2]` 兜底主类型未命中的情况；版本号命名规范支持 `v0.13.0` 或 `vllm0.13.0_torch2.8.0_cann8.3` 两种粒度。

---

## 【关键机制与数据】

### 工作原理（5 层流水线）

映射不是"配置文件本身"，而是**对一条已经发生的代码调用链做结构化标注**。原文给出从高层到低层贯通的 5 层栈：

```text
PyTorch aten 算子 (如 aten.mm)
  → OpPlugin 分发 (op_plugin_functions.yaml)
    → C++ 实现 (opapi/*.cpp)
      → EXEC_NPU_CMD(aclnn*) 调用
        → CANN aclnn Host API
          → L0 OpType 注册 (CMakeLists.txt)
            → NPU 内核执行
              → Profiling kernel_details.csv
```

### 三条映射路径（互不重叠的算子来源象限）

- **路径 A**（最常见，aten → OpPlugin → aclnn）：面向标准 PyTorch 算子。原文示例：`aten.mm.default → MatMulV2`，链路为 `op_plugin_functions.yaml → MmKernelNpuOpApi.cpp → EXEC_NPU_CMD(aclnnMm) → cann-ops-nn/matmul/mat_mul_v2/ → OP_TYPE_REGISTER(MatMulV2)`。
- **路径 B**（`torch_npu.npu_*` → op-plugin → aclnn）：面向 vLLM-ascend 专用算子。原文示例：`npu_grouped_matmul_swiglu_quant → GroupedMatmulSwigluQuant`，落到 `cann-ops-transformer/gmm/OP_TYPE_REGISTER(GroupedMatmulSwigluQuant)`。
- **路径 C**（vLLM-ascend 自定义 / Triton / ATB）：不在 OpPlugin 中，函数名通常 `=` profiling Type。原文示例：`torch_npu.atb.npu_ring_mla() → RINGMLAPrefillBF16Kernel`。
- **通信旁路**：完全绕过 OpPlugin；HCCL 的 `hcom_allReduce_` 类型查询走 `message_bytes + num_devices` 而非 shape 匹配。

### 分步追踪实证（原文 `tensor_cast.swiglu.default` 案例）

- **Step 1**：`grep -r "def swiglu" tensor_cast/ops/` → `tensor_cast/ops/activation.py: SwiGlu`
- **Step 2**：vLLM-ascend 调用 `torch_npu.npu_swiglu(...)`
- **Step 3**：`op_plugin_functions.yaml` 第 5742 行：`npu_swiglu`
- **Step 4**：`SwigluKernelNpuOpApi.cpp: EXEC_NPU_CMD(aclnnSwiglu, ...)`
- **Step 5**：`set(OPTYPE "SwiGlu")` 于 `cann-ops-transformer/CMakeLists.txt`
- **Step 6**：原文披露实测数据点：**DSv3 profiling 中 SwiGlu 出现 390 次，Qwen3 中出现 670 次**。

### 查询模式自动分流（5 类）

```text
是复合算子？   → _lookup_composite(sub_kernels)
是通信算子？   → _lookup_comm(message_bytes, num_devices)
是特殊注意力？ → _lookup_attention(batch, seq, heads, head_dim)
是零开销？     → QueryResult(latency=0)
默认          → _lookup_compute(kernel_type, alternate_kernel_types)
```

### Shape 差异自动处理（8 种）

`profiling_data_source.py` 自动处理 8 种差异：批次维前导 batch=1 剥离、block-padding 向上对齐 16/32、`fractal_nz_to_nd()` 还原、MatMul 权重转置检查、SwiGlu 在最后维拼接、RoPE 维度转置与重排、RoPE 多内核用 `alternate_kernel_types`、融合算子用 `sub_kernels` 分解。

### 性能数据 / Profiling 验证

解析工具链：`tools.perf_data_collection.parse_kernel_details`（输入 `kernel_details.csv`、输出按内核拆分 CSV）+ `tools.perf_data_collection.validate`（验证生成的 profiling database）；均使用 `python3.10` 运行。

---

## 【表格解读】

### 表 1：条目类型（互斥）

| 类型 | 字段 | 含义 | 示例 |
|------|------|------|------|
| **计算** | `kernel_type: X` | 通过 Type=X 直接查询 CSV | MatMulV2, SwiGlu |
| **复合** | `composite: true` | 分解为 `sub_kernels`，分别查询 | matmul_all_reduce → [MatMulV2, hcom_allReduce_] |
| **零开销** | `zero_cost: true` | 返回 latency=0（纯元数据算子） | view, permute, split |

**逐行解读**：
- *计算* 行：是最常见的"一对一"映射；`kernel_type` 字段直接成为 profiling CSV 的查询键。
- *复合* 行：通过 `sub_kernels` 数组允许把单个 TC 算子拆成多个 NPU 内核查表后聚合——隐含了"latency 累加"的语义。
- *零开销* 行：是性能建模中的特殊豁免机制，针对的是无 NPU 计算的元数据算子；例子里 `view/permute/split` 都是 Python/C++ 端就能完成的 reshape，不需要落进 AI Core。
- 表格标题"互斥"是关键设计：避免映射产生查询路径歧义，使得 5 路分发可确定地工作。

### 表 2：8 种 Shape 差异

| # | 差异类型 | TC Shape | NPU Profiling Shape | 处理方式 |
|---|---------|----------|---------------------|----------|
| 1 | 批次维度 | `(1,S,D)` | `(S,D)` | 移除两边的前导 batch=1 |
| 2 | 序列填充 | `S=144` | `S=136` | block-padding 容差（向上取整到 16/32） |
| 3 | FRACTAL_NZ | `(K,N)` ND 格式 | `[H,W,bh,bw]` 分块格式 | `fractal_nz_to_nd()` 还原 |
| 4 | ND 转置 | `(K,N)` | `(N,K)` | MatMul 权重转置检查 |
| 5 | SwiGlu 拼接 | 2×`(S,D/2)` | 1×`(S,D)` | 在最后维度上拼接输入 |
| 6 | RoPE 布局 | `(B,H,S,D)` Q,K | `(B,S,H,D)` K,Q | 转置维度 + 重排输入 |
| 7 | RoPE 内核 | 单个 TC 算子 | 多个 NPU 内核 | `alternate_kernel_types` |
| 8 | 复合算子 | 融合的 TC 算子 | 分离的 NPU 内核 | `sub_kernels` 分解 |

**逐行解读**：
- #1-#4：纯几何/格式差异，本质是同一计算在不同表示层下的表达，**全部可由 `profiling_data_source.py` 自动归一化**。
- #1 批维剥离：常因 eager/batch=1 推理产生；上下两侧都允许前置 1。
- #2 块大小对齐：16/32 是 CANN 的常见 block size 边界；136 → 144 是向上取整示例。
- #3 NZ 格式：Ascend 硬件专有的分块布局，需 `fractal_nz_to_nd()` 反向解码。
- #4 ND 转置：常见于权重预转置场景，MatMul 是受影响最大的算子。
- #5-#8：TC 算子语义与 NPU 内核语义不完全等价时的"再拼装"操作；这类差异**不能完全自动处理**，需在配置文件中显式声明。
- #6 RoPE Q/K 布局差异需要同时做维度转置与输入重排，复杂度较高。
- #7-#8：体现出 `alternate_kernel_types` / `sub_kernels` 两种机制的价值——前者用于"一查多命中"，后者用于"一对多分解"。

### 表 3：kernel_details.csv 列说明

| 列名 | 含义 | 用途 |
|------|------|------|
| **Type** | CANN OPTYPE = 我们的 `kernel_type` | 聚合的主键 |
| **Name** | `aclnn_Dispatch_L0OpType` 三段式 | 追溯到 aclnn API |
| **Input Shapes** | tensor shape 字符串 | CSV 中的 shape 匹配 |
| **Duration(us)** | 内核执行时间 | 性能数据 |
| **Accelerator Core** | AI Core 或 AI Vector Core | 硬件利用率 |

**逐行解读**：
- *Type* 列是核心 hub，所有上层映射表都以它为 join key；这是 §3 "关键标识符"原则的具体落点。
- *Name* 列的三段式允许工程师仅靠 profiling 即可反查 aclnn API 调用点（第 3 段固定为 Type）；这是反向 debug 工具。
- *Input Shapes* 是 compute 类查询的主匹配字段，**而 communication 类查询不使用它**（用 `message_bytes + num_devices` 替代）。
- *Duration(us)* 单位为微秒，是最终 EmpiricalPerformanceModel 替换解析估算的数据源。
- *Accelerator Core* 提供硬件亲和性信息，可用于区分类 AI Core 类（如 MatMul）与 AI Vector Core 类（如 elementwise）内核。

### 表 4：查询分发类别

| 类别 | 查询方式 | 匹配依据 |
|------|---------|---------|
| `compute` | CSV shape 查找 | 输入/输出 tensor shape |
| `communication` | 消息字节数 | `tensor_nbytes * dtype_size` |
| `attention_special` | 注意力维度 | `(batch, seq_len, num_heads, head_dim)` |
| `composite` | 分解 + 求和 | 每个 sub_kernel 独立查询 |
| `zero_cost` | 返回 0 | 无需查找 |

**逐行解读**：
- *compute* 是默认模式，未命中任何修饰字段则走此分支；TC 大部分稠密算子（MatMul/Linear/Conv 等）属于此类。
- *communication* 跳过 shape，改用 `tensor_nbytes * dtype_size` 作为"带宽和时延"代理，反映集体通信的字节传输本质。
- *attention_special* 用四元组，匹配 FlashAttention 系算子的 query_mode 协议——`(batch, seq, heads, head_dim)` 足以唯一刻画 attention GEMM 的命中条件。
- *composite* 隐含"延迟求和"语义：每个 sub_kernel 独立查表后累加，是模拟 fused-op 在 NPU 端展开性能的最简方式。
- *zero_cost* 是性能等价于 0 的短路返回；与 `zero_cost: true` 条目是配置与查询两端的呼应。

### 表 5：CANN 版本变更模式

| 变更类型 | 示例 | 处理方式 |
|---------|------|---------|
| **重命名** | `ScatterElements` → `ScatterElementsV2` | 更新 `kernel_type`，用 `alternate_kernel_types` 兼容 |
| **融合** | 独立的 matmul+activation → 单个融合内核 | 更新 `kernel_type`（不仅仅是 `alternate_kernel_types`） |
| **拆分** | 一个内核 → 两个独立内核 | 可能需要 `composite: true` + `sub_kernels` |
| **移除** | Triton 内核被 CANN 原生融合替代 | 删除条目或更新为新内核类型 |
| **新增内核** | 新的 ATB/CANN 融合内核 | 添加新条目，通过 5 层流水线追踪 |

**逐行解读**：
- *重命名*：最温和的破坏性变更；用 `alternate_kernel_types` 维持向后兼容即可。
- *融合*：原文特别强调"更新 `kernel_type`（不仅仅是 `alternate_kernel_types`）"——因为若仅作备选，主查询仍会按旧类型落空，融合带来的加速带无法被建模。这是映射维护中**最易踩的坑**。
- *拆分*：与融合相反方向；可能需要从单一 `kernel_type` 升级为 composite 分解，结构性变更。
- *移除*：典型场景是自定义 Triton 实现被 CANN 上游融合取代；需要在版本切换时显式删除或更新条目，否则会留下指向已不存在内核的死引用。
- *新增内核*：视为新增条目而非变更现有条目；需要走完整 5 层流水线重新建立证据链。

---

## 【公式解读】

**原文无公式。**

文档涉及的所有量化关系均以命令、配置字段、profiling CSV 列值等工程形式表达，未出现 LaTeX 数学公式或伪代码公式段落。仅有的隐含"关系式"在表格中以「Type ≡ CANN OPTYPE ≡ kernel_type」「Name = `aclnn_Dispatch_L0OpType`」「FP32 → BF16 × 2.0 字节比缩放」等文本化等式呈现，故按"原文无公式"处理。

---

## 【关联】

文档明示依赖**内部链接** `../../../.agents/skills/op-mapping/SKILL.md`（指向 `op-mapping` skill 的 SKILL 描述）——这是与"AI Agent 驱动 op_mapping 维护"工作流的官方锚点，表明本教程既可人读，也可被编程 Agent 通过该 skill 自动执行。

文档自身不显式给出 GitHub 内的其他交叉链接，但所引用的代码路径表明其覆盖范围横跨以下**上下游模块**：

- **`tensor_cast/`** —— TC 虚拟算子源头（如 `tensor_cast/ops/activation.py: SwiGlu`）。
- **`tensor_cast/performance_model/`** —— `EmpiricalPerformanceModel`、`ProfilingDataSource`、`profiling_data_source.py`（自动 shape 归一化 + 5 路分发）。
- **`tensor_cast/performance_model/profiling_database/data/{device}/vllm_ascend/{version}/op_mapping.yaml`** —— 本文核心配置文件位置。
- **`op_plugin/`** —— 华为 Ascend OpPlugin，包含 `op_plugin/config/op_plugin_functions.yaml`、`op_plugin/ops/opapi/MmKernelNpuOpApi.cpp` / `SwigluKernelNpuOpApi.cpp` 等。
- **CANN 仓库（`cann-ops-nn/`、`cann-ops-transformer/`）** —— aclnn 实现与 `OP_TYPE_REGISTER` 注册源。
- **vLLM-ascend** —— 算子使用方与 vLLM-ascend 自定义算子来源（如 `vllm_ascend/ops/activation.py`、`vllm_ascend/ops/attention.py`、`vllm_ascend/ops/mla_v1.py`）。
- **`tools/perf_data_collection/`** —— `parse_kernel_details`、`validate` 两个 profiling 数据库构建/校验工具。

可推断的**模块协同关系**：`op_mapping.yaml` 位于 *配置层*，向上承接 TC 算子语义、向下承接 NPU kernel 物理实现，两端都通过"OP_TYPE_REGISTER"和"Type 列"这两个等价主键串联。

---

## 【使用方法】

### 启用方式

无需启用——它是一个**静态映射文件**，存在即可被 `EmpiricalPerformanceModel` 自动加载。但路径必须遵循命名规范：

```
tensor_cast/performance_model/profiling_database/data/{device}/vllm_ascend/{version}/op_mapping.yaml
```

其中 `{version}` 形如 `v0.13.0` 或 `vllm0.13.0_torch2.8.0_cann8.3`，承载了 profiling 时的软件栈版本信息。

### 关键命令集合

**1. 查找并验证单个算子映射**（6 步法，以 `tensor_cast.swiglu.default` 为例原文逐字给出）：

```bash
# Step 1: 理解 TC 算子
grep -r "def swiglu" tensor_cast/ops/

# Step 2: 找到 aten/TorchNPU 路径
grep -r "swiglu\|silu_and_mul" /path/to/vllm-ascend/

# Step 3: 查找 OpPlugin 条目
grep "npu_swiglu" /path/to/op-plugin/op_plugin/config/op_plugin_functions.yaml

# Step 4: 查找 EXEC_NPU_CMD
grep -r "npu_swiglu" /path/to/op-plugin/op_plugin/ops/

# Step 5: 查找 OPTYPE
grep -r "SwiGlu\|SWIGLU" /path/to/cann-ops-transformer/ --include="CMakeLists.txt"

# Step 6: 在 profiling 中验证
grep "SwiGlu" kernel_details.csv | head -3
```

**2. 跨 CANN 版本对比 profiling 类型**：

```bash
awk -F',' 'NR>1 {print $2}' old_kernel_details.csv | sort -u > old_types.txt
awk -F',' 'NR>1 {print $2}' new_kernel_details.csv | sort -u > new_types.txt
diff old_types.txt new_types.txt
```

**3. 由原始 profiling 数据生成结构化性能数据库**：

```bash
python3.10 -m tools.perf_data_collection.parse_kernel_details \
  --device ATLAS_800_A3_752T_752T_128G_DIE \
  --vllm-ascend-version <version_string> \
  --kernel-details-path /path/to/kernel_details.csv

python3.10 -m tools.perf_data_collection.validate \
  --database tensor_cast/performance_model/profiling_database/data/{device}/vllm_ascend/{version}/
```

**注**：原文在第 3 命令中给出的 device 标识为 `ATLAS_800_A3_752T_128G_DIE`（原文如此）。

**4. 快速统计 profiling 中各内核类型出现频次**：

```python
import csv
from collections import Counter
with open('kernel_details.csv') as f:
    types = Counter(row['Type'] for row in csv.DictReader(f))
for t, c in types.most_common():
    print(f"{c:6d}  {t}")
```

> **原文截断提示**：文档第 8 章在说明「使用 `alternate_kernel_types`：当新旧名称可……」处中断，未给出完整规则。维护此类兼容性需结合 §3 关键要点（`alternate_kernel_types` 作为兜底）与 §8 已列出的 5 种变更模式共同判断。
