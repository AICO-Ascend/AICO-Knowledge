# CSV 正例、反例与格式详解

> 仓 `agent-skills` · 路径 `official/Common/ascend-transformer-boost/skills/atb-csv-testcase-generator/references/csv-design-and-columns.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/Common/ascend-transformer-boost/skills/atb-csv-testcase-generator/references/csv-design-and-columns.md

# 一体化深度解读：CSV 正例、反例与格式详解

---

## 【定位】

本文是 `atb-csv-testcase-generator` 的延伸阅读文档，系统化阐述 ATB（Ascend Transformer Boost）算子 CSV 测试用例的设计原则与格式规范——覆盖正例（功能正确性）、反例（错误校验）、性能测试（Performance）、CSV 列定义、数据类型映射、ExpectedError 体系，以及 Ascend910B 与 Ascend950 双设备覆盖规则，是为算子测试人员提供从"用例结构"到"多设备适配"的完整设计手册。

---

## 【技术要点】

1. **典型 Shape 选型基准**：Llama 取 hidden_size=3584，常用 shape 512/7168；GPT 取 hidden_size=6144，常用 shape 256/12288；Mini batch 覆盖 1–16 tokens，Large batch 覆盖 1024–2048 tokens。
2. **边界条件三类**：UB 上限（hidden_size=31424）、非对齐 hidden_size（130、65）、最小 shape（1、64）。
3. **ExpectedError 三级阶段前缀**：`C:` 表示 Create 阶段、`I:` 表示 InferShape 阶段、`S:` 表示后续阶段；正例完整流程用 `NO_ERROR`、仅校验 InferShape 用 `I:NO_ERROR`、仅校验参数用 `C:ERROR_INVALID_PARAM`。
4. **正例 vs Golden 强绑定**：CSV 中正例使用 `NO_ERROR` 时，必须在 `data_generation.py` 中实现对应的 `golden()` 参考计算；仅做维度推断（`I:NO_ERROR`）则无需 golden。
5. **多设备 SocVersion 表达**：单设备直接写 `Ascend910B` 或 `Ascend950`；双设备一致场景合并写为 `Ascend910B;Ascend950`（分号分隔）；任何差异（dtype/format/参数约束/维度上限/ExpectedError/性能基准）必须拆分为两条独立用例，分别命名为 `{OpName}{场景}910B` / `{OpName}{场景}950`。
6. **CSV 列结构 21 列定长**：从 `CaseNum` 到 `ExpectedError`，输入/输出张量均以 `分号` 分隔多 tensor；数据类型在 CSV 中有别名（如 `float16`/`half`、`bf16`/`bfloat16`、`int8`/`char`、`int64`/`long`），对应 `data_generation.py` 支持的类型名。

---

## 【关键机制与数据】

### 工作原理：CSV 用例驱动的算子测试流水线
- CSV 每行即一条用例，测试框架按行解析后调度算子执行流水线三步骤——`Create → Execute → Golden Compare`（原文："完整流程：Create→Execute→Golden Compare"）。
- `ExpectedError` 通过阶段前缀（`C:`/`I:`/`S:`）精确控制流程在哪一步预期失败：例如 `I:ERROR_INVALID_TENSOR_DIM_NUM` 表示 InferShape 阶段就应报错，框架不会继续执行算子。
- `DataGenType=customize` 触发 `data_generation.py` 中的 `golden()` 参考计算，正例中 OutShape/OutDType 与算子实际输出对齐。

### 关键数据（原文中明确给出的）
- **Llama 主流 shape**：512、7168（hidden_size=3584，原文）
- **GPT 主流 shape**：256、12288（hidden_size=6144，原文）
- **UB 上限边界**：hidden_size=31424（原文）
- **非对齐 hidden_size 示例**：130、65（原文）
- **最小 shape 示例**：1、64（原文）
- **Performance 大/中/小 shape**：`2048,16384` / `512,8192` / `64,256`（原文）
- **Performance bf16 shape**：`1024,8192`（原文）
- **Performance 边界 shape**：`256,8192`（原文，hidden_size 边界）
- **910B 与 950 维度上限差异**：910B hidden_size≤31424；950 hidden_size≤32768（原文）

### 多设备运行约束
- **原文："实际运行测试时仅执行 Ascend910B 用例（当前测试环境限制）。Ascend950 用例由用户在 950 设备上手动验证。"**
- 这意味着 950 用例在 CI 环境不会自动跑，只作为设计交付物供用户在 950 设备上回放。

---

## 【表格解读】

### 表 1：ExpectedError 选择指南（正例）

| 测试目标 | ExpectedError | 需要 Golden | 典型场景 |
|---------|--------------|------------|---------|
| 仅验证参数校验 | `C:ERROR_INVALID_PARAM` | 否 | 反例 |
| 仅验证维度推断 | `I:NO_ERROR` | 否 | 简单正例 |
| 完整执行+精度验证 | `NO_ERROR` | **是** | 完整正例 |

**逐行解读**：
- 第 1 行：`C:ERROR_INVALID_PARAM` 表示算子构造（Create）阶段即应参数校验失败——无需 golden，因为根本不会进入 Execute 与精度比对；用于反例构造中的参数非法校验。
- 第 2 行：`I:NO_ERROR` 表示 InferShape 阶段成功即可终止——无需 golden，因为不进入实际执行；用于只关心形状推导路径正确性的快速用例。
- 第 3 行：`NO_ERROR` 表示全流程必须通过，且必须配套 `data_generation.py::golden()` 实现——用于功能正例的完整精度比对。

### 表 2：反例覆盖检查表

| 校验类型 | ExpectedError | 覆盖场景 |
|----------|--------------|---------|
| 数据类型 | `I:ERROR_INVALID_TENSOR_INI_MATCH` | int64, int32, float32, bool |
| 数据格式 | `I:ERROR_INVALID_TENSOR_INI_MATCH` | fractal_z, ncdhw 等 |
| 维度数量 | `I:ERROR_INVALID_TENSOR_DIM_NUM` | 1D, 3D, 4D |
| 维度值 | `I:ERROR_INVALID_TENSOR_DIM` | 0, 奇数, 超限 |
| 参数校验 | `C:ERROR_INVALID_PARAM` | 非法参数值 |
| 输出 Shape | `S:ERROR_INVALID_TENSOR_DIM` | shape 不匹配 |
| UB 边界 | `I:ERROR_INVALID_TENSOR_DIM` | hidden_size 过大 |

**逐行解读**：
- 数据类型行：用 `I:ERROR_INVALID_TENSOR_INI_MATCH` 覆盖算子不支持的输入类型（int64/int32/float32/bool），错误发生在 InferShape 阶段的张量初始化校验。
- 数据格式行：与上一行共用同一错误码，针对 fractal_z/ncdhw 等不被支持的输入 format。
- 维度数量行：1D/3D/4D 触发 `I:ERROR_INVALID_TENSOR_DIM_NUM`，针对 dimNum 不符的输入。
- 维度值行：维度为 0、奇数、超限触发 `I:ERROR_INVALID_TENSOR_DIM`，针对具体维度数值的合法性。
- 参数校验行：唯一带 `C:` 前缀的反例，错误发生在 Create 阶段——参数非法直接拦下。
- 输出 Shape 行：唯一带 `S:` 前缀的反例，针对运行后期输出维度不匹配的语义错误。
- UB 边界行：与维度值行共用同一错误码，但专门针对 hidden_size 超过 UB 上限（31424）的场景。

### 表 3：CSV 列说明

| 列号 | 名称 | 说明 |
|------|------|------|
| 1 | CaseNum | 用例编号 |
| 2 | CaseName | 用例名称 |
| 3 | OpName | 算子名称（如 `SwigluQuantOperation`） |
| 4 | OpParam | JSON 格式参数字符串 |
| 5 | InNum | 输入张量数量 |
| 6 | InDType | 输入数据类型（分号分隔） |
| 7 | InFormat | 输入数据格式（分号分隔） |
| 8 | InShape | 输入形状（分号分隔） |
| 9 | OutNum | 输出张量数量 |
| 10 | OutDType | 输出数据类型 |
| 11 | OutFormat | 输出数据格式 |
| 12 | OutShape | 输出形状 |
| 13 | DataGenType | 数据生成类型（通常为 `customize`） |
| 14 | DataGenRange | 数据生成范围 |
| 15 | InTensorFile | 输入张量文件（空） |
| 16 | OutTensorFile | 输出张量文件（空） |
| 17 | TestType | 测试类型（空或 `Performance`） |
| 18 | TestLevel | 测试级别（空） |
| 19 | FromModel | 来源模型（空） |
| 20 | SocVersion | 目标 SoC（如 `Ascend910B`、`Ascend950`。多个设备用 `;` 分隔：`Ascend910B;Ascend950`） |
| 21 | ExpectedError | 期望错误（`NO_ERROR` 或错误类型） |

**逐行解读**：
- 列 1–4 为用例元信息（编号、名称、算子、操作符 JSON 参数）。
- 列 5–8 为输入张量定义；列 5 标数量，列 6/7/8 用 `;` 平行分隔每个 tensor 的 dtype/format/shape。
- 列 9–12 为输出张量定义，结构与输入对称。
- 列 13–14 控制数据生成方式（`customize` 触发 `data_generation.py`，`DataGenRange` 给出生成区间如 `-100,100`）。
- 列 15–16 为张量文件占位（空），由框架在运行时填充。
- 列 17 为性能标识（填 `Performance` 即进入性能基准测试，否则为空）。
- 列 18–19 为测试级别与来源模型（空字段，预留扩展位）。
- 列 20 关键：单设备直接写名字，多设备用 `;` 分隔，但仅在 910B/950 完全一致时才合并。
- 列 21 决定测试预期（正例、反例、性能、阶段前缀）。

### 表 4：数据类型映射

| 实际类型 | CSV 中使用 |
|----------|-----------|
| float32 | `float` |
| float16 | `float16` 或 `half` |
| bfloat16 | `bf16` 或 `bfloat16` |
| int8 | `int8` 或 `char` |
| int32 | `int32` 或 `int` |
| int64 | `int64` 或 `long` |

**逐行解读**：每种数值类型都提供两种 CSV 别名，便于与上下游脚本（如 PyTorch/TensorFlow 导出）对接——例如历史用例可能用 `half`、新用例倾向 `float16`；`bf16`/`bfloat16` 同理；`int8`/`char` 兼容 C/C++ 习惯写法。

### 表 5：常用 ExpectedError 类型

| 错误类型 | 说明 | 触发场景 |
|----------|------|----------|
| `NO_ERROR` | 无错误，正例预期（完整流程：Create→Execute→Golden Compare） | 正常执行，需要 golden 参考实现 |
| `I:NO_ERROR` | InferShape 无错误（仅验证到 InferShape 阶段） | 不需要 golden，仅验证维度推断 |
| `C:NO_ERROR` | Create 无错误（仅验证到 Create 阶段） | 仅验证参数校验通过 |
| `I:ERROR_INVALID_TENSOR_INI_MATCH` | 张量初始化不匹配 | dtype/format 错误 |
| `I:ERROR_INVALID_TENSOR_DIM_NUM` | 维度数量错误 | dimNum 不符合预期 |
| `I:ERROR_INVALID_TENSOR_DIM` | 维度值错误 | 维度值超限/无效 |
| `C:ERROR_INVALID_PARAM` | 参数错误 | 非法参数值 |
| `S:ERROR_INVALID_TENSOR_DIM` | 输出 Shape 错误 | 输出 tensor shape 不匹配 |

**逐行解读**：
- 前三行定义"流程终止点"：`NO_ERROR` 走完整个链路，`I:NO_ERROR` 在 InferShape 后停，`C:NO_ERROR` 在 Create 后停——便于快速正例快速验证。
- 后五行定义错误码及其对应触发点：`I:` 前缀都在张量推断阶段捕获（dtype/format/dimNum/dim），`C:` 在参数构造阶段拦截，`S:` 在执行后期形状不匹配时报出。

### 表 6：合并 vs 分离规则

| 情况 | SocVersion | 说明 |
|------|-----------|------|
| 910B 和 950 **完全一致**（场景/约束/dtype/format 均相同） | `Ascend910B;Ascend950` | 合并为一条用例 |
| 910B 和 950 **存在任何差异** | 分两条，各写各自 SocVersion | **必须分离** |

**逐行解读**：合并的充要条件是 910B 与 950 在"场景/约束/dtype/format"四个维度上完全对齐；只要有一项不同，必须拆分为两条用例并在命名上区分 910B/950。

### 表 7：必须分离的场景

| 差异类型 | 示例 | 处理方式 |
|---------|------|---------|
| **dtype 支持不同** | 910B 支持 bf16，950 不支持 | 分两条：910B bf16 / 950 用其他 dtype |
| **format 支持不同** | 910B 支持 ND，950 仅支持 ND_TRANSPOSE | 分两条，各自指定合法 format |
| **参数约束不同** | 910B quantType=0,1；950 quantType=0 | 分两条，各自合法/非法参数 |
| **维度限制不同** | 910B hidden_size≤31424；950 hidden_size≤32768 | 正向/边界分别设计 |
| **ExpectedError 不同** | 同一非法输入，910B 报 ERROR_A，950 报 ERROR_B | 分两条，各自 ExpectedError |
| **性能基准不同** | 910B 和 950 性能预期不同 | 分两条，各自 Performance |

**逐行解读**：
- dtype 行：bf16 仅在 910B 上可用，950 端必须切换为别的 dtype（如 float16）单独成例。
- format 行：format 维度上的支持差异，950 只能 ND_TRANSPOSE 时不能复用 910B 的 ND 用例。
- 参数约束行：`quantType` 在 910B 上接受 0/1、在 950 上只接受 0，因此合法/非法集本身就不同，必须分写。
- 维度限制行：原文给出明确数字——910B 上限 31424、950 上限 32768；意味着 950 多 1264 的裕量区间，边界用例要分别在两设备上单独设计。
- ExpectedError 行：同一输入可能命中不同错误码（如不同算子实现路径），必须各自标注。
- 性能基准行：硬件性能曲线不同，必须各自给出 Performance 用例。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游 Skill：`atb-csv-testcase-generator`**：本文是该 skill 的延伸阅读（`references/` 目录），专门展开 CSV 设计的细颗粒度规范；CSV 用例生成时必须遵循本文档的列结构、ExpectedError 体系、多设备规则。
- **跨 Skill 引用：`../../atb-golden-developer/SKILL.md`**：本文明确指出"正例使用 `NO_ERROR` 时，需要在 `data_generation.py` 中实现 `golden()` 参考计算。详见 ATB Golden Developer"——`atb-golden-developer` 是为算子编写 `golden()` 参考计算实现的另一 skill，二者构成"用例生成 + 参考实现"的协作闭环：CSV 设计 → 触发 `data_generation.py` 中 `golden()` 调用 → 算子输出与 golden 对比完成精度验证。
- **下游对象：Ascend910B / Ascend950 设备**：本文档的所有多设备规则都指向这两个 SoC 平台；用例命名约定（`{OpName}{场景}910B` / `{OpName}{场景}950`）直接服务于跨设备可追溯性。

---

## 【使用方法】

**CSV 用例设计流程（原文给出的 4 步法）**：

1. **先分析接口文档**：对比 910B 和 950 的 ACLNN 接口规格，标记所有差异点。
2. **先写共同用例**：无差异的场景用 `Ascend910B;Ascend950` 合并为一条。
3. **再写差异用例**：每个差异点，为 910B 和 950 各写一条独立用例。
4. **差异用例命名**：`{OpName}{场景}910B` / `{OpName}{场景}950` 便于区分。

**启用方式 / 配置项**：
- **SocVersion 字段**：单设备写 `Ascend910B` 或 `Ascend950`；双设备一致场景写 `Ascend910B;Ascend950`；任何差异必须拆条。
- **ExpectedError 字段**：正例完整流程写 `NO_ERROR`；仅校验 InferShape 写 `I:NO_ERROR`；仅校验参数写 `C:NO_ERROR`；反例按校验类型选 `C:ERROR_INVALID_PARAM` / `I:ERROR_INVALID_TENSOR_INI_MATCH` / `I:ERROR_INVALID_TENSOR_DIM_NUM` / `I:ERROR_INVALID_TENSOR_DIM` / `S:ERROR_INVALID_TENSOR_DIM`。
- **DataGenType 字段**：通常填 `customize`，并在 `data_generation.py` 中实现 `golden()`。
- **TestType 字段**：性能用例填 `Performance`（空值则为功能用例）。

**运行约束（原文提示）**：
- **当前测试环境仅执行 Ascend910B 用例**——Ascend950 用例由用户在 950 设备上手动执行，不在 CI 中自动跑。
- 反例场景下 `SwigluQuant` 系列示例明确标识：dtype 只支持 `float16`/`bf16`、`dimNum` 必须为 2、`hidden_size` 必须能被 2 整除、`quantType` 只能为 0；违反任一项即可构造对应反例。
