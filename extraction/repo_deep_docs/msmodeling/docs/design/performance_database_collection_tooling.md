# 特性设计：[算子性能数据采集能力建设]

> 仓 `msmodeling` · 路径 `docs/design/performance_database_collection_tooling.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/performance_database_collection_tooling.md

# 一体化深度解读：`docs/design/performance_database_collection_tooling.md`

> ⚠️ **原文完整性提示**: 本文档在 2.8 节"算子列表"表格中途截断（原文中表格的"量化"行尚未写完），下方解读仅基于已给出的原文内容，不补全未呈现的部分。

---

## 【定位】

**本文档定义了 msmodeling 中"基于 NPU 实测的算子/通信性能数据采集工具链"**：把原始 NPU profiling CSV → 按 kernel 拆分 → shape 矩阵扩展 → 逐算子 replay 跑 microbench → 写入带版本号的 profiling database，从而为仿真建模提供比 roofline 更精确的运行时性能查询数据资产。

---

## 【技术要点】

1. **四层分层架构（原文 §2.1）**：
   - **数据接入层** = `parse/`（parsers/parse_kernel_details.py）
   - **样本生成层** = `generate_shape_grid/`（含 grid_generator/ + memory_estimator.py）
   - **执行测量层** = `op_replay/`（25+ `_run.py`）+ `start_microbench.py` + `comm_bench/`
   - **数据资产层** = `profiling_database/data/`

2. **核心数据流管线（原文 §2.1 总架构图）**：
   `kernel_details.csv` → `parse_kernel_details.py` → `generate_shape_grid.py` → `op_replay/*_run.py` → `start_microbench.py`（msprof 编排）→ `profiling_database/data/{device}/vllm_ascend/{version}/`。
   通信分支：`comm_bench/generate_comm_microbench.py` → `profiling_database/data/{device}/hccl/{cann_version}/`。

3. **数据库版本目录命名约定（原文 §2.3）**：
   `{device}/vllm_ascend/{version_dir}/`，其中 `version_dir = vllm{vllm_version}_torch{torch_version}_cann{cann_version}`。
   原文给出 3 个示例：
   - `vllm0.13.0_torch2.8.0_cann8.3`
   - `vllm0.15.0_torch2.9.0_cann8.5`
   - `vllm0.18.0_torch2.9.0_cann8.5`

4. **shape 字段编码规则（原文 §2.4）**：分号分隔 tensor 槽位，逗号分隔维度，例如 `"136,7168;7168,3584"`；空槽位（如 FIA/自定义 kernel 中的可选输入/标量）必须保留；`FRACTAL_NZ` 是合法 format，runtime lookup 会做规范化。

5. **Parser 规范化映射（原文 §2.6）**：`split_qkv_rmsnorm_rope_kernel_0` → `split_qkv_rmsnorm_rope_kernel`，`muls_add_kernel_1` → `muls_add_kernel`；按 `(normalized Type, Input Shapes, Output Shapes)` 三元组聚合后写平均/median/标准差耗时列。

6. **Shape grid 过滤控制（原文 §2.7）**：`--target-models` 沿用 `text_generate` 的模型 ID 裁剪 GEMM `(N, K)` 候选；`--rows` 限制每 CSV 行数；`--seed` 保证可复现；`--max-hbm-gb` 经 `memory_estimator.py` 过滤超出 HBM 预算的行。

---

## 【关键机制与数据】

### 工作原理（端到端）

**计算算子数据采集**（原文 §2.1 流程图）：原始 NPU profiling 输出的 `kernel_details*.csv`（可能含 `operator_details.csv` 与 `trace_view.json` 用于 FIA bundle 校验）经 `parse_kernel_details.py` 按 `(normalized Type, Input Shapes, Output Shapes)` 聚合后拆分为每个 kernel 一份 `{KernelType}.csv`；`generate_shape_grid.py` 在不填性能值的前提下向 CSV 追加 theory shape 行；`op_replay/*_run.py`（25+ 脚本）按行逐 kernel 在 NPU 主机上重放并通过 `start_microbench.py` 用 msprof 编排采集、回写 `Average Duration(us)` 与 `MicroBench aicore_time(us)` / `aic_total_cycles` 列；最终持久化到 `{device}/vllm_ascend/{version_dir}/op_mapping.yaml + {KernelType}.csv`。

**通信数据采集**：原文 §2.5 给出标准文件名为 `hcom_allGather_.csv`、`hcom_allReduce_.csv`、`hcom_alltoallv_.csv`、`hcom_reduceScatter_.csv`（按原文逐字还原，文件名以"_"结尾），由 `generate_comm_microbench.py` + `run_comm_bench.sh` 生成，存到 `{device}/hccl/{cann_version}/`。

### 设计原则（原文明确表述）

- **Parser 保守性**（原文 §2.6）："不推断缺失 tensor 槽位，不改写 API 语义；保留 profiling 表示，把 shape/API 对齐留给 `op_mapping.yaml`、`generate_shape_grid.py` 和 replay 脚本。"
- **Grid 生成保守性**（原文 §2.7）："生成行继承源行中的稳定结构 metadata，不填充性能值（留空或置零）。只有经过 `start_microbench.py` 或后续 profiling 导入填充耗时后，才是可用的生产数据。"

### 核心价值（原文 §1 Background）

原文将该工具链的核心价值概括为三点：
1. 将"解析 profiling → 扩充 shape → replay → 数据库回填"串成可重复执行的数据生产链；
2. 解耦为职责清晰的子模块；
3. 提供结构化、可追溯的算子性能数据资产。

> 📌 **性能数据**：原文未提供具体的耗时数字/吞吐数字/基准数据等量化性能指标——本文档是设计文档而非测试报告。

---

## 【表格解读】

### 表 1：Revision History（原文逐字还原）

| Date (日期) | Version (修订版本) | Change Description (修改描述) | Author (作者) | RFC Document (RFC文档) |
| --------- | -------------- | ------------------------- | ----------- | -------------------- |
| 2026-6-1  | 1.0            | 初稿完成，算子性能数据采集能力设计文档       | -           | -                    |

**解读**：仅一行版本记录，为初稿（v1.0，2026-6-1），作者/RFC 文档栏为空，表示本特性尚处于设计起步阶段。

### 表 2：工具范围与职责（原文 §2.2 逐字还原）

| 范围              | 入口                                                                                                | 数据库职责                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 原始 profiling 解析 | `parsers/parse_kernel_details.py`                                                                 | 从 `kernel_details*.csv` 或 profiling 目录生成按 kernel 拆分的计算 CSV                       |
| Shape grid 扩展   | `generate_shape_grid.py` + `grid_generator/` + `memory_estimator.py`                              | 追加可 replay 的 theory shape 行，并按 HBM 预算过滤                                       |
| 计算算子 replay     | `op_replay/*_run.py` (25+ scripts) + `start_microbench.py`                                       | 在 NPU 主机上重放 CSV 行并回写 microbench 耗时                                              |
| HCCL 通信采集       | `comm_bench/generate_comm_microbench.py` + `run_comm_bench.sh`                                   | 生成 `hccl/{cann_version}/hcom_*.csv`                                          |

**逐行解读**：
- **原始 profiling 解析行**：`parse_kernel_details.py` 是唯一入口；输入既可以是单个 CSV 文件也可以是 profiling 目录（递归扫 `kernel_details*.csv`）；输出按 kernel 拆分。
- **Shape grid 扩展行**：由 3 个组件协同——顶层入口 `generate_shape_grid.py` + 包 `grid_generator/`（含 config/runner/theory_router/shape_grids/evaluator/model_configs/utils + generators/{base,fused_attention,moe}.py，原文 §2.7 树状图）+ 内存过滤 `memory_estimator.py`；目的是"扩展而非测量"。
- **计算算子 replay 行**：`op_replay/` 提供 25+ 脚本（原文用 "25+" 表示数量），`start_microbench.py` 是 msprof 编排与 CSV 回写枢纽。
- **HCCL 通信采集行**：`generate_comm_microbench.py` 生成脚本，`run_comm_bench.sh` 执行；产物落到 `hccl/` 子目录下以 `hcom_*.csv` 命名。

### 表 3：数据库目录契约（原文 §2.3 逐字还原）

| 数据类型    | 目录                                                                                            | 内容                                       | 版本范围                                |
| ------- | --------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------------- |
| 计算/算子数据 | `tensor_cast/performance_model/profiling_database/data/{device}/vllm_ascend/{version_dir}/`   | `op_mapping.yaml` 和 `{KernelType}.csv` | 设备 + vLLM-Ascend + PyTorch + CANN 栈 |
| 通信数据    | `tensor_cast/performance_model/profiling_database/data/{device}/hccl/{cann_version}/`         | `hcom_*.csv` benchmark 文件，可选拓扑/配置元数据     | 设备 + CANN/HCCL 栈                    |

**逐行解读**：
- **计算/算子数据行**：物理根路径是 `tensor_cast/performance_model/profiling_database/data/`，向上叠加 `{device}` 与 `vllm_ascend/{version_dir}` 两层；每个 `{version_dir}` 内放一份 `op_mapping.yaml`（shape/API 对齐元数据）加上若干 `{KernelType}.csv`；版本维度跨"硬件 + 推理框架 + 训练框架 + 芯片软件栈"四层栈版本。
- **通信数据行**：物理根路径同样位于 `tensor_cast/performance_model/profiling_database/data/`，但子目录结构是 `{device}/hccl/{cann_version}/`，版本维度只跨"硬件 + CANN/HCCL 栈"，不含 vLLM/PyTorch（因为通信算子主要受 HCCL 实现版本影响）；`hcom_*.csv` 是主文件，"可选拓扑/配置元数据"表示这部分元数据不是强制必有。

### 表 4：计算 CSV 基础必需列（原文 §2.4 逐字还原）

| 列组               | 列                                                                                                                                           | 生产者                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| Kernel 标识与 shape | `OP State`, `Accelerator Core`, `Input Shapes`, `Input Data Types`, `Input Formats`, `Output Shapes`, `Output Data Types`, `Output Formats` | 原始 profiling parser      |
| Profiling 耗时     | `Profiling Average Duration(us)`, `Profiling Median Duration(us)`, `Profiling Std Duration(us)`                                             | 原始 profiling parser      |
| Profiling 计数器    | `Profiling Average aicore_time(us)`, `Profiling Average aic_total_cycles`, `Profiling Average aic_mac_time(us)` 及 AIC/AIV 利用率列              | 原始 profiling parser      |
| Microbench 耗时    | `Average Duration(us)`                                                                                                                      | `start_microbench.py` 回写 |
| Microbench 计数器   | `MicroBench aicore_time(us)`, `MicroBench aic_total_cycles` 及对应 `MicroBench ...` 列                                                          | `start_microbench.py` 回写 |

**逐行解读**：
- **Kernel 标识与 shape 行**：标识 + 完整的 I/O 形状/类型/格式六元组（输入输出各 3 列），全部由原始 profiling parser 一次性写入；"格式"指 FRACTAL_NZ 等 layout。
- **Profiling 耗时行**：三列统计量（平均/中位/标准差），反映原始算子在 profiling 时的耗时分布。
- **Profiling 计数器行**：包含 aicore 时间、aic 总周期、aic MAC 时间以及"AIC/AIV 利用率列"（原文表述为"及 AIC/AIV 利用率列"，未列出每个利用率列的具体命名）。
- **Microbench 耗时行**：仅一列 `Average Duration(us)`，且**不带 "Profiling" 前缀**——与上面的 Profiling 耗时列区分；这是 replay 后回填的实际测量值。
- **Microbench 计数器行**：与 Profiling 计数器列对应但加 `MicroBench` 前缀；原文用"及对应 `MicroBench ...` 列"概括其余列（未逐一列出）。

### 表 5：通信 CSV Schema（原文 §2.5 逐字还原）

| 列                                                                          | 级别      | 类型     | 含义                                         |
| -------------------------------------------------------------------------- | ------- | ------ | ------------------------------------------ |
| `message_bytes`                                                            | 运行时必需   | int    | 每 rank 消息大小，用于查询和插值                        |
| `num_devices`                                                              | 运行时必需   | int    | 参与通信的 rank 数                               |
| `Average Duration(us)` / `Profiling Average Duration(us)` / `Duration(us)` | 运行时必需其一 | float  | 通信时延                                       |
| `topology_tier`                                                            | 条件匹配    | int    | 设备拓扑层级，0为inter_pod，1为intra_pod，2为die_level |
| `dtype`                                                                    | 采集标准    | string | 测量 dtype，如 `DT_BF16`                       |
| `bandwidth_gbps`                                                           | 采集标准    | float  | 派生带宽，用于审计和校验                               |

**逐行解读**：
- **`message_bytes`（运行时必需）**：每 rank 传输字节量，是运行时 lookup 的查询键与插值依据。
- **`num_devices`（运行时必需）**：参与该通信的 rank 数，同样作为查询键。
- **时延三选一（运行时必需其一）**：`Average Duration(us)` / `Profiling Average Duration(us)` / `Duration(us)` 三个名字任意一个出现即可被运行时识别——这是为兼容历史采集脚本的列名漂移。
- **`topology_tier`（条件匹配）**：拓扑层级编码，`0=inter_pod`、`1=intra_pod`、`2=die_level`；是否提供视采集场景而定，运行时做条件匹配。
- **`dtype`（采集标准）**：测量所用的数据类型，原文示例 `DT_BF16`。
- **`bandwidth_gbps`（采集标准）**：由 message_bytes/duration 派生的带宽值（原文标注为"用于审计和校验"），意味着它不参与查询决策，只作为数据正确性二次核验。

### 表 6：支持算子列表（原文 §2.8，逐字还原已有部分；原文未完成）

| 类别          | 算子脚本                                                                                       | 说明                 |
| ----------- | ------------------------------------------------------------------------------------------ | ------------------ |
| Matmul      | `MatMulV2_run.py`, `MatMulV3_run.py`, `MatMulCommon_run.py`                                | 标准矩阵乘法             |
| 量化          | `QuantBatchMatmulV3_run.py`, `AscendQuantV2_run.py`, `DynamicQuant_run.py`（原文此处被截断）  | （原文未给出"说明"列内容）     |

**逐行解读**：
- **Matmul 行**：列出 3 个 Matmul 变体脚本，覆盖 V2/V3/Common 三种实现；说明列直接标注为"标准矩阵乘法"。
- **量化行**：原文仅列出 3 个量化相关脚本名，本行"说明"列在原文中尚未写出即被截断——不做臆测补充。

---

## 【公式解读】

原文无公式。文档仅以 Python 伪代码风格的 ASCII 流程图（§2.1 总体架构）与目录树（§2.7 grid_generator/）展示结构，无 LaTeX 或数学公式表达式。

---

## 【关联】

> 📌 **原文内部链接信息**：文档文末标注 **(无)**，即没有显式的内部链接章节。

**但根据上下文可推断的上下游关联**（基于原文 §1、§2 内容描述，非新增信息）：

1. **上游依赖**：
   - **NPU Profiling 输出**（Ascend `kernel_details*.csv` / `operator_details.csv` / `trace_view.json`）—— Parser 直接消费对象。
   - **`text_generate` 模型 ID**（原文 §2.7："`--target-models` 使用与 `text_generate` 相同的模型 ID"）—— shape grid 的 GEMM `(N, K)` 候选裁剪共享此命名空间。
   - **`memory_estimator.py`**（位于 `generate_shape_grid/` 同包，原文 §2.2、§2.7）—— HBM 预算过滤依赖此模块。

2. **下游消费方**：
   - **性能模型查询**（`tensor_cast/performance_model/`，从 §2.3 路径可见）—— 这是工具链产物的运行时消费方，做算子性能 lookup。
   - **仿真建模**（文档背景 §1 指出"当前仿真建模主要基于 roofline 模型进行算子性能估算……需要建立一套基于实测性能数据的建模能力体系"）—— 本特性是仿真建模精度提升的输入数据来源。
   - **`op_mapping.yaml`**（§2.3、§2.6 反复提及）—— 是 shape/API 对齐的元数据桥接文件，连接 Parser 与 runtime lookup。

3. **同级模块协作**：
   - `parsers/` ↔ `generate_shape_grid/` ↔ `op_replay/` ↔ `start_microbench.py` 构成"解析→扩展→重放→测量"的串行依赖。
   - `comm_bench/` 是相对独立的旁支，仅产出 `hccl/` 子目录。

4. **vLLM-Ascend 栈版本**：`{version_dir}` 命名明确绑定 vLLM、PyTorch、CANN 三方版本，反映该工具链服务的推理栈组合。

---

## 【使用方法】

基于原文可提取的配置项/命令如下：

### 解析阶段（原文 §2.6）

- **入口脚本**：`parsers/parse_kernel_details.py`
- **关键参数**：
  - `--profiling-path`：接受单个 `kernel_details*.csv` 文件**或** profiling 目录（递归扫描文件名包含 `kernel_details` 的 CSV；同时发现 `operator_details.csv` 与 `trace_view.json` 用于 FIA bundle 校验）。

### Shape grid 扩展阶段（原文 §2.7）

- **入口脚本**：`generate_shape_grid.py`
- **关键参数**：
  - `--target-models`：与 `text_generate` 共享模型 ID，用于裁剪 GEMM `(N, K)` 候选。
  - `--rows`：限制每个 CSV 的行数。
  - `--seed`：保证抽样可复现。
  - `--max-hbm-gb`：通过 `memory_estimator.py` 过滤超出内存预算的行。
- **配置文件**：`grid_generator/config.yaml`（定义算子的 shape 结构和采样网格，用于生产理论性能测试的 shape 组合）。
- **Generator 扩展点**：`grid_generator/generators/`（含 `base.py` 基类、`fused_attention.py` FIA 复杂 generator、`moe.py` MoE 复杂 generator）。

### 计算算子 replay 阶段（原文 §2.8，原文截断）

- **入口脚本**：`op_replay/*_run.py`（25+ 脚本）。
- **编排脚本**：`start_microbench.py`（msprof 编排 + CSV 回写）。
- **已列出算子**：MatMul（`MatMulV2_run.py`/`MatMulV3_run.py`/`MatMulCommon_run.py`）、量化（`QuantBatchMatmulV3_run.py`/`AscendQuantV2_run.py`/`DynamicQuant_run.py`）；其余 22+ 算子原文未给出。

### 通信采集阶段（原文 §2.2、§2.5）

- **入口脚本**：`comm_bench/generate_comm_microbench.py`（生成脚本）+ `run_comm_bench.sh`（执行）。
- **产物路径**：`{device}/hccl/{cann_version}/` 下生成 `hcom_allGather_.csv` / `hcom_allReduce_.csv` / `hcom_alltoallv_.csv` / `hcom_reduceScatter_.csv`。

### 数据库版本号输入（原文 §2.3）

- **`{version_dir}` 模板**：`vllm{vllm_version}_torch{torch_version}_cann{cann_version}`
- **示例取值**：`vllm0.13.0_torch2.8.0_cann8.3`、`vllm0.15.0_torch2.9.0_cann8.5`、`vllm0.18.0_torch2.9.0_cann8.5`

> 📌 **关于"启用方式"**：原文未提供一键启用开关或顶层编排脚本（如 Makefile/CLI），整条数据生产链是按"四层分层"手动串联：parse → grid → replay → bench。如需完整端到端编排命令，原文未涉及。
