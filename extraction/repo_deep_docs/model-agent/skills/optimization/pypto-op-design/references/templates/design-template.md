# {operator_name} 算子设计文档

> 仓 `model-agent` · 路径 `skills/optimization/pypto-op-design/references/templates/design-template.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/optimization/pypto-op-design/references/templates/design-template.md

# 「pypto-op-design」算子设计文档模板 深度解读

---

## 【定位】

这是一份 **PyPTO 算子设计文档的标准化模板**，为「昇腾模型 Agent」中每个自定义算子（custom operator）的实现提供一套从需求 → 数学公式 → API 映射 → 数据规格 → Tiling/Loop 策略 → 验证 → 性能 → 风险管控的 **全流程结构化设计框架**，其内容由该 skill（pypto-op-design）基于上游生成的 SPEC.md 自动填充。

---

## 【技术要点】

1. **九节式设计骨架**：模板固定覆盖 概述 → API 映射 → 数据规格 → Tiling → Loop → 验证 → 性能 → 风险 → 交付件 共九大章节，每节皆有占位符（如 `{operator_name}`、`{formula}`、`{tiling_api_call}`），由 skill 解析 SPEC.md 后逐项替换。
2. **公式 → API 分解机制**：第 2 节要求把数学公式 `${formula}$` 拆解为 `步骤 / 数学表达 / 说明` 三列，再映射到 `PyPTO API / 参数 / 文档路径`，形成"数学→算子 API"的可追溯链路。
3. **数据规格双 dataclass**：第 3 节用 `@dataclass` 定义 `{OperatorName}Input` 与 `{OperatorName}Output`，对每个 Tensor 显式标注 `shape / dtype / 格式（ND 或 NZ）`；第 3.6 节挂载 `@pypto.frontend.jit(runtime_options=...)` 装饰器用于编译期优化。
4. **Tiling 分型策略**：第 4 节先判定算子类型（Cube / Vector / 混合），再调用 `tiling_api_call` 设初值，并给出"判断依据 / 适用条件 / 不适用场景"三段式说明。
5. **Loop 结构场景化判定**：第 5 节采用二分模板——「场景 A：不需要 Loop（所有轴编译期已知）」与「场景 B：需要 Loop（动态轴 / 大范围）」，后者进一步细化静态 vs 动态轴处理、Loop 合并、尾块策略与 `loop_unroll` 配置。
6. **Golden 对照与精度阈值**：第 6 节要求实现 `{operator_name}_golden` 参考函数，并以表格列出每个 dtype 对应的 `atol / rtol` 精度标准；第 7 节给出「预期 kernel 耗时」性能目标。

---

## 【关键机制与数据】

### 工作原理

模板的生成链路为：**SPEC.md → DESIGN.md → golden → impl → test**，对应 skill 调用顺序即原文第 9.4 节所示：

```
SPEC.md → DESIGN.md → {op}_golden.py → {op}_impl.py → test_{op}.py
```

### 数据流

- **输入来源**：模板第 1.4 节注明数据流图 `{ASCII数据流图}` 从 `SPEC.md §3` 直接复制；第 2.4 节 API 选择依据同样来自 `spec / api_report / docs / example`。
- **内部流向**：数学公式 `${formula}$` → 子公式分解（第 2.1 节）→ PyPTO API 映射（第 2.2 节）→ 计算步骤伪代码（第 2.3 节）→ Tiling / Loop 编排（第 4-5 节）→ Golden 函数（第 6.1 节）→ 测试用例（第 6.2 节）。

### 性能数据

**原文未涉及具体性能数值**（所有耗时、Shape 数字均为占位符）。原文仅以 `{expected_time}` 占位说明"基于 SPEC.md 典型配置（性能类）的预期 kernel 耗时"。

---

## 【表格解读】

原文无具实填值的成品表格（**整篇为模板**），但定义了大量占位表格结构。以下**逐字还原**原文中的代表性关键表格并逐行解读：

### 表 1：数学公式分解（第 2.1 节）

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | `{sub_formula_1}` | `{step_desc_1}` |
| 2 | `{sub_formula_2}` | `{step_desc_2}` |

**解读**：将总公式 `${formula}$` 拆为 2 步子表达式（实际填写时可任意扩展 N 行），左列为序号、中列为 LaTeX/伪代码子式、右列为自然语言解释，便于后续 API 映射追溯。

### 表 2：PyPTO API 映射表（第 2.2 节）

| 步骤 | 数学表达 | PyPTO API | 参数 | 文档路径 |
|------|----------|-----------|------|----------|
| 1 | `{sub_formula_1}` | `{pypto_api_1}` | `{params_1}` | `{doc_path_1}` |
| 2 | `{sub_formula_2}` | `{pypto_api_2}` | `{params_2}` | `{doc_path_2}` |

**解读**：在公式分解基础上增加"PyPTO API / 参数 / 文档路径"三列，每行构成"数学子式 → 框架 API → 参数配置 → 官方文档引用"的完整映射单元。

### 表 3：中间 Tensor 定义（第 3.3 节）

| 名称 | Shape | Dtype | 说明 |
|------|-------|-------|------|
| `{intermediate_name}` | `{intermediate_shape}` | `{intermediate_dtype}` | `{intermediate_desc}` |

**解读**：显式枚举算子执行过程中产生的非输入非输出中间张量，避免后续实现中随意命名/Shape 不一致。

### 表 4：数据格式选择（第 3.4 节）

| Tensor | 格式 | 说明 |
|--------|------|------|
| `{tensor_name}` | ND / NZ | `{format_reason}` |

**解读**：在昇腾硬件上必须显式选择 ND（默认）或 NZ（Cube 优化布局），并填写选择理由。

### 表 5：动态轴定义（第 3.5 节）

| 轴名称 | 含义 | 取值范围 |
|--------|------|----------|
| `{axis_name}` | `{axis_meaning}` | `{axis_range}` |

**解读**：标记编译期未知、运行期可变的维度，是判定 Loop 结构是否需要的依据。

### 表 6：静态轴 vs 动态轴处理（第 5.2 节）

| 轴 | 类型 | 处理方式 |
|----|------|----------|
| `{axis}` | 静态 / 动态 | Python for / pypto.loop |

**解读**：逐轴选择遍历机制——静态轴用 Python `for`，动态轴用 `pypto.loop` 或 `pypto.loop_unroll`。

### 表 7：测试用例配置（第 6.2 节，基于 SPEC.md）

| 配置名称 | 类型 | 优先级 | 参数 | 输入 Shape | 输出 Shape | 说明 |
|----------|------|--------|------|------------|------------|------|
| `{config_name}` | `{type}` | `{priority}` | `{params}` | `{input_shapes}` | `{output_shapes}` | `{config_desc}` |

**解读**：穷举 SPEC.md 中所有典型配置（含功能类 / 性能类），按优先级排定测试顺序。

### 表 8：边界情况测试（第 6.2 节，可选）

| 场景 | 参数 | 说明 |
|------|------|------|
| `{boundary_scenario}` | `{boundary_params}` | `{boundary_desc}` |

**解读**：覆盖极小 Shape、极端 dtype、零维张量等 corner case，可选填。

### 表 9：精度验证标准（第 6.3 节）

| Dtype | atol | rtol |
|-------|------|------|
| `{dtype}` | `{atol}` | `{rtol}` |

**解读**：按浮点精度档位（fp16 / bf16 / fp32）分别给出绝对误差与相对误差阈值，供测试断言使用。

### 表 10：性能目标（第 7.1 节）

| 配置名称 | 类型 | 优先级 | 参数 | 输入 Shape | 输出 Shape | 预期 kernel 耗时 |
|----------|------|--------|------|------------|------------|------------------|
| `{perf_config_name}` | 性能 | `{priority}` | `{params}` | `{input_shapes}` | `{output_shapes}` | `{expected_time}` |

**解读**：仅取"性能类"配置，以"预期 kernel 耗时"列作为后续 benchmark 的目标基线。

### 表 11：常见错误规避（第 8.2 节）

| 风险 / 错误 | 触发场景 | 影响 / 原因 | 规避方法 |
|-------------|----------|-------------|----------|
| `{error_1}` | `{trigger_1}` | `{reason_1}` | `{solution_1}` |

**解读**：以"风险 → 触发场景 → 影响 → 规避"四列串联，便于工程师速查排雷。

### 表 12：实现建议（第 8.4 节）

| 建议项 | 说明 |
|--------|------|
| `{impl_hint_1}` | `{hint_desc_1}` |

**解读**：留给作者沉淀跨算子的 PyPTO 实现经验，沉淀到 DESIGN 中供后续算子复用。

### 表 13：文件清单（第 9.2 节）

| 文件 | 类型 | 说明 | 生成方式 |
|------|------|------|----------|
| SPEC.md | 需求 | 算子需求规范 | pypto-intent-understand |
| DESIGN.md | 设计 | 算子设计文档 | pypto-op-design（本 skill） |
| `{operator_name}_golden.py` | 代码 | Golden 参考实现 | pypto-golden-generate |
| `{operator_name}_impl.py` | 代码 | 算子核心实现 | 后续实现 |
| `test_{operator_name}.py` | 代码 | 测试用例 | 后续实现 |

**解读**：明确每个交付件的来源 skill / 阶段，是流水线编排的依据。

### 表 14：命名规范（第 9.3 节）

| 项目 | 规范 | 示例 |
|------|------|------|
| 算子名称 | 小写字母 + 下划线 | `fast_gelu` |
| 目录名 | 与算子名称一致 | `custom/fast_gelu/` |
| Golden 文件 | `{op}_golden.py` | `fast_gelu_golden.py` |
| 实现文件 | `{op}_impl.py` | `fast_gelu_impl.py` |
| 测试文件 | `test_{op}.py` | `test_fast_gelu.py` |

**解读**：以 `fast_gelu` 为唯一示例，强制统一 5 项命名，避免仓库内出现 `FastGelu` / `fastgelu` / `fast_gelu_v2` 等散乱命名。

---

## 【公式解读】

原文无具体公式实体（所有公式均为占位符），仅以 **Jinja 风格占位符** 表达：

$$ {formula} \quad\text{（在 §1.2 节，表示算子的核心数学公式）} $$

$$ \{sub\_formula\_1\},\ \{sub\_formula\_2\} \quad\text{（在 §2.1 节，表示公式分解后的子步骤）} $$

**符号说明**（基于占位符命名约定推断）：

- `{formula}`：待填写的完整数学公式（如 $y = \text{GELU}(x) = x \cdot \Phi(x)$ 等），由 SPEC.md 自动注入。
- `{sub_formula_i}`：第 i 个子表达式，对应 PyPTO API 的一次基本操作。
- 所有 `{}` 内文字均为 **skill 渲染时替换的变量**，并非真实符号；模板本身不携带任何数值或算式。

**作用**：作为"数学语义"层与"PyPTO 代码"层之间的桥梁，确保实现 `impl.py` 时可双向追溯到原始公式。

---

## 【关联】

- **上游输入**：`SPEC.md`（由 `pypto-intent-understand` skill 生成）——本模板第 1.4 节明确数据流图需"从 SPEC.md §3 复制"，第 6.2 节测试用例需"基于 SPEC.md 所有典型配置"。
- **同流程工具**：
  - `pypto-golden-generate` —— 生成 `{operator_name}_golden.py`（第 9.2 节）。
  - `pypto-op-design` —— 即本 skill，生成 DESIGN.md。
- **下游消费**：模板第 9.4 节给出生成顺序 `SPEC.md → DESIGN.md → golden → impl → test`，因此本 DESIGN.md 是 `impl.py` 与 `test_*.py` 编写的直接依据。
- **内部参考文档**：第 5 节注释提到"根据 `quick_ref.md §2.1` 判据表的结论选择对应模板（场景 A / B）"，说明 `quick_ref.md` 提供了 Loop 选型判据表，与本模板形成配套。
- **PyPTO API 文档**：第 2.2 节每个映射行都要求填写 `{doc_path}`，指向 PyPTO 官方 API 文档，构建"公式→API→文档"三段链接。
- **JIT/编译层**：第 3.6 节 `@pypto.frontend.jit(runtime_options=...)` 与第 7.4 节 `runtime_options_config` 配置直接挂钩 PyPTO 前端 JIT 编译通道。

---

## 【使用方法】

> 原文未直接给出"如何启用此 skill"的命令（无 CLI 入口或配置项展示），但可从模板结构推断使用方式如下：

1. **触发方式**：作为 `pypto-op-design` skill 的输出模板被自动渲染，无需用户手动启用。**原文未涉及**具体 CLI 调用。
2. **前置依赖**：必须先有上游 `pypto-intent-understand` 生成的 `SPEC.md`（置于 `custom/{operator_name}/SPEC.md`），模板第 1 节标注「基于: SPEC.md」。
3. **配置项 / 占位符清单**（来自模板 `{}` 占位符）：
   - 顶层元数据：`{operator_name}`、`{category}`、`{timestamp}`。
   - 第 1 节：`{description}`、`{formula}`、`{algorithm_name}`、算法伪代码块、数据流图。
   - 第 2 节：`{sub_formula_i}`、`{pypto_api_i}`、`{params_i}`、`{doc_path_i}`。
   - 第 3 节：`{OperatorName}Input/Output` dataclass 字段、`{intermediate_*}`、`{tensor_name}` 格式（ND/NZ）、`{axis_name}`、`{runtime_option_key/value}`。
   - 第 4 节：`{tiling_api_call}`、`{tiling_rationale}`、`{tiling_note_*}`。
   - 第 5 节：`{loop_reason}`、`{loop_type}`、`{loop_unroll_config}` 等。
   - 第 6-7 节：`{golden_params/return_type/impl}`、`{config_*}`、`{boundary_*}`、`{dtype/atol/rtol}`、`{expected_time}`、`{tiling_config}`、`{pass_options_config}`、`{runtime_options_config}`。
   - 第 8 节：`{constraint_*}`、`{error_* / trigger_* / reason_* / solution_*}`、`{special_scenario_handling}`、`{impl_hint_*}`。
4. **输出位置**：模板第 9.1 节给出固定目录结构 `custom/{operator_name}/`，DESIGN.md 写入该目录下，命名约定如表 14 所列。
5. **后续衔接**：渲染完成后，按 `SPEC.md → DESIGN.md → {op}_golden.py → {op}_impl.py → test_{op}.py` 顺序推进（第 9.4 节）。
