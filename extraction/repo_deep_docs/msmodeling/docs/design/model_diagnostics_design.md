# Design Document: model_diagnostics 仿真结构诊断 / Simulation Structure Diagnostics

> 仓 `msmodeling` · 路径 `docs/design/model_diagnostics_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/model_diagnostics_design.md

# 一体化深度解读：model_diagnostics 仿真结构诊断设计文档

---

## 【定位】

本设计文档提出在 msmodeling 仓库 `tools/model_diagnostics/` 下新增一个**结构诊断子系统**，用于在 Roofline / 时延 / 寻优等下游结论之前，以**Theory（理论期望）↔ Runtime（仿真产物）** 成对校验的方式，对**算子语义完备性**与 **Tensor shape / dtype 元数据**做可机读、可回归的结构性判定；通过"一份 YAML 规格 + 来源中立 Source 端口"驱动单一诊断核心，并将 Runtime 的接触边界收敛到 `sources/runtime_capture.py` 一个文件中。

---

## 【技术要点】

1. **定位与归属**：工具放置在仓库根 `msmodeling/tools/model_diagnostics/`，**不作为顶层公共包、不入 wheel**、仅支持源码仓运行；与 `tensor_cast/`、`serving_cast/` 平级但保持单向依赖边界。

2. **唯一 Runtime 接触点**：`sources/runtime_capture.py` 是包内**唯一**允许接触 `ModelRunner`、PyTorch 与 TensorCast 内部对象的采集边界；它执行一次**非侵入采集**，只输出中立 `SimulationExecutionArtifact`。`sources/simulation_artifact.py` 及之后的 Source / organization / comparison / application **一律禁止 import Runtime**。

3. **单一份静态规格驱动一切**：`ModelDiagnosticsSpec → RegionSpec → LayerSpec/StageSpec` 同时驱动 Theory、Runtime 的组织与比较；改 YAML 即可调整期望，**比较核心无需改动**。

4. **成对（Pair）比较，不做三方**：一次校验恰好两个来源；按 `(region_id, optional layer_index, stage_id)` 配对，比较策略由 `Registry` 按**有序来源对**解析，**Source 实现由 composition root 直接注入**（YAML 不选择组织实现）。

5. **Region 内独立物理层号**：`language / mtp / vision / video` 等 region 各自维护从 0 开始的物理层号空间；请求显式给出 region 内层号（如 `{"language": (0, 1, 5), "mtp": (0, 1)}`），**不存在跨 region 全局层号隐式映射**；不识别 `first/middle/last` 名称。

6. **请求结构与最小公共值**：`DiagnosticsRequest` 由 `context: ModelRunContext` + `selected_layers: Mapping[region_id, tuple[int,...]]` + `selected_stage_regions: tuple[str,...]` 三部分组成，二者选可任一为空但**不能同时为空**；`ModelRunContext` 包含 `model_name / entrypoint / phase / batch_size / query_length / context_length / parallel / model_config / quantization_config`，并强调 **采集函数 / adapter / 测试包装器不得将自身函数名写入 `entrypoint`**；同一次诊断的 Theory、Runtime Artifact 与 Request 必须复用**完全相同**的 Context。

7. **并行上下文与执行阶段**：`ParallelContext` 字段固定为 `tensor_parallel_size / pipeline_parallel_size / data_parallel_size / expert_parallel_size`，均默认 1；`ExecutionPhase` 当前枚举仅 `PREFILL / DECODE`。`TensorShape = tuple[int,...]`，`DType = str`（规范化名称如 `float16 / bfloat16 / int8`）。

8. **来源中立 Source 端口**：首批只交付 `Theory Source` 与 `Runtime Artifact Source`；`runtime_capture.py` 之外的 Source 适配层**不实现 Profiling 采集、不输出 stage_id / 规则 id / PASS-FAIL 结论**，仅为未来扩展保留端口。

9. **不可写的反向边界**：推断出的 region / layer / stage **不写回** `OperatorCallRecord`；Organizer 直接返回本次请求的 `tuple[RegionExecutionRecord, ...]`，**不构造全模中间对象**。

---

## 【关键机制与数据】

### 诊断主流程（原文主流程文本）

```
DiagnosticsRequest
  -> resolve exactly one ModelDiagnosticsSpec
  -> load and type-check that Spec
  -> load two ModelExecutionRecord (Theory + Runtime)
  -> organize each into selected Region/Layer/Stage records
  -> pair by region_id + optional layer_index + stage_id
  -> resolve StageComparisonStrategy by ordered source pair
  -> aggregate Finding -> DiagnosticsResult
```

### 架构节点颜色编码（原文 Mermaid 图注）

- **input 蓝**：诊断请求入口（如 `DiagnosticsRequest`）；
- **config 橙**：YAML 规格（`ModelDiagnosticsSpec YAML`）；
- **port 紫**：来源 / 规格端口（`Theory Source`、`Runtime Artifact Source`、`ModelDiagnosticsSpecResolver`、`ModelDiagnosticsSpecLoader`）；
- **strategy 绿**：可替换 Strategy（`Theory Organizer`、`Runtime Organizer`、`StageComparisonStrategy`），由 composition root 按 `SourceKind` 注入，**模型 YAML 不选择组织实现**；
- **domain 灰**：领域记录（`Pair by region/layer/stage`）；
- **output 红**：结论对象（`Finding[] / DiagnosticsResult`）。

### 数据流关键约束（原文）

- Theory、Runtime Artifact、`DiagnosticsRequest` **必须复用完全相同的 `ModelRunContext`**；
- 每个已声明 region 的层集合**不得为空**、拒绝负数 / 越界、随后**去重升序**；
- 对每个选中层，**声明的全部 stage 都必须比较**（"选中层全阶段"原则）；
- Theory 与 Runtime 在 `runtime_capture.py` 内**功能解耦**：该工具仅在 `sources/runtime_capture.py` 内接触 TensorCast 内部运行对象并生成中立 `SimulationExecutionArtifact`；Artifact 之后的 Source、domain、organization、comparison、application **不依赖 Runtime**，**也不输出由采集侧代写的 layer / stage / 规则结论**。

### 领域记录模型（原文 Python 定义摘录，原文无具体性能数字）

- `SourceKind`：`THEORY / RUNTIME`；
- `ModelExecutionRecord.source_kind / run_context / operator_calls`；
- `OperatorCallRecord.call_index / operator_name / original_operator_name / tensors / source_reference`；
- `StageExecutionRecord.stage_id / operator_calls`、`LayerExecutionRecord.layer_index / layer_kind / stages`、`RegionExecutionRecord.region_id / stages / layers`；
- `TensorDirection`：仅 `INPUT / OUTPUT / INOUT`；
- `TensorSlot`：含 `direction / index / name`，并通过 `_TensorSlots` 与模块级 `INPUT / OUTPUT` 句柄支持 `INPUT[i]`、`OUTPUT[j]` 写法（原文在此处被截断，仅给出片段）。

### 历史与规模（原文 Revision History，无具体性能数字）

| 维度 | 数值 / 描述 |
| --- | --- |
| 首次上库日期 | 2026-07-27，版本 1.0 |
| 当前版本 | 1.4，日期 2026-08-15 |
| 期间迭代版本数 | 1.0 → 1.1 → 1.2 → 1.3 → 1.4（共 5 版） |

> 原文未提供任何性能数据、吞吐数字或时延数据；本文档定位为结构诊断而非性能基准。

---

## 【表格解读】

### 表格 1：Revision History（**逐字保留**）

| Date (日期) | Version (修订版本) | Change Description (修改描述) | Author (作者) | RFC Document (RFC文档) |
| --- | --- | --- | --- | --- |
| 2026-07-27 | 1.0 | 首次上库版本：交付 Theory→Runtime 算子结构及 Tensor shape/dtype 诊断模块、Runtime Artifact 边界、YAML Theory Spec、Run Profile 样例、CLI 与回归测试 | ChenHuiwen | N/A |
| 2026-08-12 | 1.1 | 增加 DeepSeek V3 Dense-prefix/MoE 混合层、MLA/DSA/MoE Theory、W8A8/W4A8 与 MTP 纵向覆盖 | ChenHuiwen | N/A |
| 2026-08-14 | 1.2 | 分类 3 扩展为 DeepSeek V3/V3.2、GLM-5/5.1、Kimi K2/K2.5/K2.6 文本兼容矩阵，并增加代表性 TP/EP、DP/MDP 覆盖 | ChenHuiwen | N/A |
| 2026-08-15 | 1.3 | 分类 3 并行覆盖改为逐型号（每型号 TP=2/EP=2、DP=2/MDP=2 组合）；新增 `MOE_GATE_TOKENS` 契约并补充 sparse_attention 机械算子忽略 | ChenHuiwen | N/A |
| 2026-08-15 | 1.4 | 评审修复：lm_head TP 默认值单测、`explicit_moe_gate` 语义说明、config 一致性注释；E2E 按例行代表集 + nightly 全矩阵分层 | ChenHuiwen | N/A |

**逐行解读**：
- **1.0（2026-07-27）**：奠基版本，确立**模块边界**（Runtime Artifact）、**输入契约**（YAML Theory Spec、Run Profile）、**可执行面**（CLI、回归测试）。
- **1.1（2026-08-12）**：纵向上把 DeepSeek V3 的 **Dense-prefix / MoE 混合层**以及 **MLA / DSA / MoE Theory**、**W8A8 / W4A8**、**MTP** 纳入覆盖，体现"纵向覆盖"思路。
- **1.2（2026-08-14）**：把"分类 3"由单型号扩展为多型号文本兼容矩阵（DeepSeek V3/V3.2、GLM-5/5.1、Kimi K2/K2.5/K2.6），并补充 **TP/EP、DP/MDP** 代表性并行组合。
- **1.3（2026-08-15）**：将分类 3 并行覆盖**逐型号化**，每个型号固定 **TP=2 / EP=2** 与 **DP=2 / MDP=2** 两组组合；新增 **`MOE_GATE_TOKENS`** 契约字段，并补充 `sparse_attention` 机械算子**忽略**规则（说明比较器对 sparse attention 类机械算子选择跳过，而非期望它们进入成对比较）。
- **1.4（2026-08-15）**：评审修复，包括 **lm_head TP 默认值单测**、`explicit_moe_gate` 语义说明、config 一致性注释；E2E 测试策略明确为 **"例行代表集 + nightly 全矩阵"** 的分层节奏。

### 表格 2：Goals（**逐字保留**）

| Goal | Design Direction | Success Signal |
| --- | --- | --- |
| 尽早发现结构错误 | M1 校验算子完备性与 Tensor shape/dtype | 注入缺失/错误 shape 的 fixture 失败且可定位 |
| 单一语义源 | 一份静态 `ModelDiagnosticsSpec` 驱动 Theory、组织与比较 | 改 YAML 即可调整期望，无需改比较核心 |
| 可扩展来源 | 来源中立端口；当前只交付 Theory↔Runtime | 未来外部 Profiling 等可按同一契约接入 |
| 仓库内清晰归属 | 包放在仓库根目录，与 `tensor_cast` 平级 | 依赖边界测试证明 domain 不 import Runtime |

**逐行解读**：
- **Goal 1**（M1 校验）：将"结构正确性"聚焦到两个最小可机读属性——**算子完备性**与 **Tensor shape/dtype**；成功信号是 **fixture 失败 + 可定位**，意味着不仅测得到，还能定位到具体 shape 缺失 / 错误的注入点。
- **Goal 2**（单一语义源）：所有期望都集中到一份 YAML Spec；改期望 = 改 YAML，**比较核心代码保持不变**，这是该设计降低后续维护成本的关键。
- **Goal 3**（可扩展来源）：明确**当前不交付** Profiling 等其它来源，但通过端口协议**预留接入位**。
- **Goal 4**（清晰归属）：以"与 `tensor_cast` 平级"的方式表达治理边界——既不依赖也不被依赖；**依赖边界测试**作为硬约束：domain 层不得 import Runtime。

### 表格 3：Design Principles（**逐字保留**）

| Principle | Meaning |
| --- | --- |
| Context 已知 | `ModelRunContext` 由调用方提供，不从执行记录反推。 |
| 一份静态规格 | `ModelDiagnosticsSpec → RegionSpec → LayerSpec/StageSpec` 同时驱动 Theory、Runtime 组织与比较。 |
| Region 独立层号 | language / MTP / vision / video 等各自维护从 0 开始的物理层号空间；请求按 region 显式给出该 region 内的物理层号，不使用跨 region 的全局层号。 |
| 选中层全阶段 | 对每个选中层，声明的全部 stage 都必须比较。 |
| 成对比较 | 一次校验恰好两个来源；不做三方投票或聚合。 |
| Strategy 可替换 | 组织按 `SourceKind` 注入；比较按 `region_id + stage_id + 有序来源对` 解析策略。 |
| Artifact 解耦 | `runtime_capture.py` 是唯一 Runtime 接触点；诊断核心只消费稳定 artifact / 领域记录。 |

**逐行解读**：
- **Context 已知**：禁止"从执行记录反推"——杜绝 Runtime 侧把内部函数名塞回 `entrypoint` 的反模式。
- **一份静态规格**：与 Goals 表"单一语义源"互证；`RegionSpec / LayerSpec / StageSpec` 是规格的层级细化。
- **Region 独立层号**：与第 2.4.1 节"不存在全局连续层号到 region 层号的隐式映射"互证；消除 `language[1]` 与 `mtp[1]` 被混读的歧义。
- **选中层全阶段**：选择是**集合语义**，不能"选了一个层但跳过其中某个 stage"；这避免漏报。
- **成对比较**：把"比较"严格二元化，便于 Reasoning 与回归基线稳定。
- **Strategy 可替换**：组织与比较都被显式注册 / 解析，未来加新 Stage（如 MLA / DSA）只需新增 `StageComparisonStrategy`。
- **Artifact 解耦**：再次强调 `runtime_capture.py` 是边界，**核心诊断只吃稳定产物**。

---

## 【公式解读】

> 原文为设计文档，未给出数学公式；但包含若干**伪代码 / 接口契约**形式的关键声明，逐字保留并解读：

**契约 1：诊断主流程（伪代码）**

```text
DiagnosticsRequest
  -> resolve exactly one ModelDiagnosticsSpec
  -> load and type-check that Spec
  -> load two ModelExecutionRecord (Theory + Runtime)
  -> organize each into selected Region/Layer/Stage records
  -> pair by region_id + optional layer_index + stage_id
  -> resolve StageComparisonStrategy by ordered source pair
  -> aggregate Finding -> DiagnosticsResult
```

- **符号含义**：
  - `DiagnosticsRequest`：诊断请求（frozen dataclass）；
  - `ModelDiagnosticsSpec`：一份静态 YAML 规格；
  - `ModelExecutionRecord`：单来源执行记录（Theory 或 Runtime）；
  - `Region / Layer / Stage ExecutionRecord`：组织后的领域记录；
  - `StageComparisonStrategy`：按 `(region_id, optional layer_index, stage_id, ordered source pair)` 解析得到的比较策略；
  - `Finding`：单条比较结论；
  - `DiagnosticsResult`：汇总结果。
- **作用**：把"诊断一次调用"刻画为**严格有序的 7 步流水线**，每一步都对应架构图（§2.3）中的一个颜色分区——端口（resolve / load）、Source（two records）、Strategy（organize / pair / strategy）、Output（Finding → Result）。

**契约 2：请求与上下文**

```python
@dataclass(frozen=True)
class DiagnosticsRequest:
    context: ModelRunContext
    selected_layers: Mapping[str, tuple[int, ...]]  # region_id -> physical indices
    selected_stage_regions: tuple[str, ...] = ()    # request-level stages, including mixed stage/layer regions


@dataclass(frozen=True)
class ParallelContext:
    tensor_parallel_size: int = 1
    pipeline_parallel_size: int = 1
    data_parallel_size: int = 1
    expert_parallel_size: int = 1
```

- **符号含义**：
  - `selected_layers`：region → region 内层号元组；例：`{"language": (0, 1, 5), "mtp": (0, 1)}`；
  - `selected_stage_regions`：请求级 stages（包含混合 stage/layer 的 region）；
  - `ParallelContext.t/p/d/e_x_size`：4 个并行维度，全部默认 1；
  - 不可变性（`frozen=True`）保证 Theory / Runtime / Request 三处 Context 复用时的**强一致性**。
- **作用**：定义"诊断什么"的最小可机读契约；通过 region 显式层号，避免任何"全局层号反推"路径。

**契约 3：执行记录与组织记录**

```python
class SourceKind(Enum):
    THEORY = "theory"
    RUNTIME = "runtime"


@dataclass(frozen=True)
class RegionExecutionRecord:
    region_id: str
    stages: tuple[StageExecutionRecord, ...] = ()
    layers: tuple[LayerExecutionRecord, ...] = ()
```

- **符号含义**：`SourceKind` 严格二元；`RegionExecutionRecord` 既可只装 stages（如 `language` 的 prefill 共享 stage）、也可只装 layers（典型 LLM 主干），还可两者皆有（**mixed stage/layer region**）。
- **作用**：把"组织结果"建模为**只装本次请求相关的子集**，并强制 Organizer 不去构造"全模"中间对象。

**契约 4：Tensor 方向与句柄**

```python
class TensorDirection(Enum):
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"


@dataclass(frozen=True)
class TensorSlot:
    direction: TensorDirection
    index: int
    name: str | None = None


class _TensorSlots:
    def __init__(self, direction: TensorDirection): ...
    def __getitem__(self, index: int) -> TensorSlot: ...


INPUT = _TensorSlots(TensorDirection.INPUT)
OUTPUT = _TensorSlots(TensorDirection.OUTPUT)
```

- **符号含义**：
  - `TensorDirection` 仅三态：`INPUT / OUTPUT / INOUT`；
  - `TensorSlot` = `(direction, index, name?)`：以**方向 + 位置索引**唯一定位一个 tensor 槽位；
  - `_TensorSlots` 通过 `__getitem__(index)` 暴露轻量句柄语法 `INPUT[i]`、`OUTPUT[j]`；
  - 模块级 `INPUT / OUTPUT` 是该句柄的**共享单例**。
- **作用**：把"算子的输入/输出 tensor"统一抽象为**按方向 + 索引寻址的 slot**，并为后续 `TensorInfo`（原文在末尾被截断）保留机读接口。

> **注**：原文在 `TensorInf` 处被截断，因此 `TensorInfo` / `OperatorCallRecord` 完整字段、`Finding` / `DiagnosticsResult` 形态、CLI 子命令、YAML Theory Spec 示例、Run Profile 样例、E2E 分层策略等均**未在本文片段中给出**。

---

## 【关联】

- **下游消费对象 / 报告产物**：`rendering/` 子包提供 **Console** 与 **self-contained HTML reports** 两种渲染，是 `Finding[] / DiagnosticsResult`（架构图 output 红色节点）的最终用户面。
- **CI / 测试集成**：`integrations/pytest_assertions.py` 是结构诊断与回归测试体系的桥接点，把 `Finding → DiagnosticsResult` 转译为 pytest 断言（与 §1.1 Goals 的"fixture 失败且可定位"成功信号互证）。
- **测试镜像**：`tests/model_diagnostics/` 与工具内部结构**镜像对齐**，意味着测试既覆盖 domain，也覆盖 sources / organization / comparison / application 五层。
- **依赖边界测试**：通过**依赖边界测试**证明 `domain` 不 import Runtime，是 §2.1 "Artifact 解耦"原则的硬性验收。
- **并行 / 量化覆盖（来自 Revision History）**：覆盖矩阵由 1.1 的单型号（DeepSeek V3 Dense-prefix/MoE）→ 1.2 的多型号（V3/V3.2、GLM-5/5.1、Kimi K2/K2.5/K2.6）→ 1.3 的逐型号并行组合（**TP=2 / EP=2** 与 **DP=2 / MDP=2**）+ 新增 `MOE_GATE_TOKENS` 契约 + `sparse_attention` 机械算子忽略 → 1.4 的 `lm_head` TP 默认值 / `explicit_moe_gate` 语义 / config 一致性 + E2E 分层（**例行代表集 + nightly 全矩阵**）逐步成型。
- **包放置与上下游**：工具位于 `msmodeling/tools/model_diagnostics/`，与 `tensor_cast/`、`serving_cast/` 平级；上游是 `tensor_cast` 的 Runtime（仅通过 `runtime_capture.py` 单向接触），下游是 msmodeling 自身的 Roofline / 时延 / 寻优等结论（文档 §1 明确指出"语义算子完备性、Tensor shape / dtype 出错 → 后续 Roofline、时延与寻优结论失真"）。
- **内部链接（来自文末）**：`../../tools/model_diagnostics/README.md`——仓库内 README 应当描述该工具的快速上手 / CLI 入口 / Run Profile 样例 / 内置 builtin specs 的清单与索引；本 design 文档与之形成"接口契约 ↔ 使用说明"的左右栏关系。

---

## 【使用方法】

> 原文为 design 文档，正文未直接给出 CLI 命令、配置项或启用开关的逐字说明；可从文中拼出的**启用方式与配置契约**如下：

- **包放置与运行方式**：工具位于仓库根 `msmodeling/tools/model_diagnostics/`，**不作为顶层公共包、不入 wheel**，仅支持源码仓运行（`tools/` 下源码 import 路径）。
- **启用入口**：`application/ModelDiagnosticsRunner` 是构造根之上的应用入口（架构图未细化其内部），由 `builtin.py`（composition root）装配。
- **诊断请求契约**（需在调用侧构造）：
  - `context: ModelRunContext`——至少填 `model_name / entrypoint / phase / batch_size / query_length / context_length / parallel / model_config / quantization_config`；
  - `selected_layers: Mapping[region_id, tuple[int,...]]`（如 `{"language": (0, 1, 5), "mtp": (0, 1)}`），region 内层号从 0 起、必须去重升序、不可为负、不可越界、不可为空；
  - `selected_stage_regions: tuple[str,...]`（含混合 stage/layer region）；
  - 两者可任一为空，**但不能同时为空**；**不允许** `first/middle/last` 名称检索。
- **规格输入**：以 `ModelDiagnosticsSpec YAML` 形式提供（`specification/` 提供 YAML loader + schema + builtin specs）；同一份 Spec 驱动 Theory、Runtime 的组织与比较，**模型 YAML 不选择组织实现**（组织由 composition root 按 `SourceKind` 注入）。
- **来源接入**：首批只交付 `Theory Source` 与 `Runtime Artifact Source`；**当前工作流不实现 Profiling 采集**、Source、组织、映射或集成。
- **比较策略**：由 `Registry` 按 `(region_id, stage_id, ordered source pair)` 解析 `StageComparisonStrategy`；**不做三方投票或聚合**，仅成对比较。
- **结果消费**：`rendering/` 提供 **Console** 与 **self-contained HTML** 报告；`integrations/pytest_assertions.py` 提供 pytest 断言桥接，用于 CI 回归。
- **测试运行**：测试树 `tests/model_diagnostics/` 与包结构镜像；E2E 采用**例行代表集 + nightly 全矩阵**分层（来自 Revision History v1.4）。
- **运行时硬约束**：同一次诊断中，Theory / Runtime Artifact / `DiagnosticsRequest` 必须复用**完全相同**的 `ModelRunContext`；`runtime_capture.py` 是唯一允许接触 Runtime / PyTorch / `ModelRunner` 的边界。

> 原文未涉及的具体启用项（如具体 CLI 子命令名、YAML Theory Spec 字段表、Run Profile 样例内容、TensorInfo 完整字段定义、Finding / DiagnosticsResult 结构、稀疏算子忽略的精确表达式）需参考文末内部链接 `../../tools/model_diagnostics/README.md` 与仓库内 `tools/model_diagnostics/specification/`、`builtin.py` 等模块源码。
