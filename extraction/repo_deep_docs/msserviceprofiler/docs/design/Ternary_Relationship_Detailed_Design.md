# 三元关系详设

> 仓 `msserviceprofiler` · 路径 `docs/design/Ternary_Relationship_Detailed_Design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/design/Ternary_Relationship_Detailed_Design.md

# 三元关系详设 —— 一体化深度解读

---

## 【定位】

本文档描述在服务化自动寻优工具 `msserviceprofiler` 中引入「三元参数关系推导」能力，使 `tp * pp * dp = world_size` 这类需要**两个源字段共同决定一个派生字段**的复杂并行配置可通过统一的 `OptimizerConfigField` 模型表达，并通过优先级感知的约束修复策略避免 PSO 粒子位置与真实评估参数不一致；同期新增 `-c/--config` 命令行参数以解决多配置文件路径切换痛点。

---

## 【技术要点】

1. **两类三元派生字段**：在 `OptimizerConfigField` 中新增 `dtype="ternary_factories"`（值 = `product / (field_a * field_b)`）和 `dtype="ternary_times"`（值 = `product * field_a * field_b`），由 `map_param_with_value` 在已有二元派生处理之后进行三元分支解码。

2. **自洽性修复触发条件**：当三元除法结果「非整除」、「低于 `min_value`」、「高于 `max_value`」三类异常同时统一视为需要修复场景；不可修复时按明确策略降级。

3. **两阶段约束修复**（`_repair_ternary_factories_with_priority`）：
   - 阶段一：固定高优先级字段 `keep`，在低优先级字段 `adjust` 候选集中搜索最近合法值；
   - 阶段二：两个字段候选集按与当前值距离排序后联合搜索，取第一组合法组合。

4. **优先级策略双模式**：
   - `fixed`：按 `dtype_param.priority` 显式列表保留高优先级字段，缺失或非法时退化为 `target_names` 顺序；
   - `balanced`：PSO 前半粒子使用 `target_names` 正序，后半粒子使用反序，**奇数迭代轮次整体翻转方向**，无 `DecodeContext` 时退化为 `target_names` 顺序。

5. **PSO 粒子位置一致性回写**：通过新增 `DecodeContext`（含 `particle_index`、`n_particles`、`iteration`）在 `PSOOptimizer.op_func` 中预解码并把修复后真实参数通过 `field_to_param` 反写到 `x[i]`，使 `personal_best`/`global_best` 基于实际评估参数。

6. **`-c/--config` 命令行参数**：支持绝对路径、含目录分隔符的相对路径、纯文件名三种形式，TOML 验证后追加到配置加载列表**末尾（最高优先级）**，不指定时行为与历史版本完全一致；与旧环境变量 `MODEL_EVAL_STATE_CONFIG_PATH` 共存但优先级更低；不支持同时传入多个配置文件。

---

## 【关键机制与数据】

### 三元关系在参数配置解码层的集成路径

原文：`ms_serviceparam_optimizer/ms_serviceparam_optimizer/config/config.py` 中扩展 `OptimizerConfigField` 字段模型，`update_optimizer_value` 在已有二元派生处理后增加 `ternary_factories` 和 `ternary_times` 分支。三元关系集中在参数配置解码层，**服务框架和测试工具只接收最终参数，不需要感知三元推导细节**。

### PSO 评估一致性保证

原文：`PSOOptimizer.op_func` 为每个粒子构造 `DecodeContext`，调用 `map_param_with_value` 预解码并通过 `field_to_param` 把修复后的真实参数反写到 `x[i]`；随后 `Scheduler.run_with_request_rate` 使用**同一个 `DecodeContext`** 运行评估，避免 PSO 认为评估的是原始非法位置。

### 性能影响边界（原文）

> 修复过程可能枚举两个源字段候选集。`enum` 使用候选列表，`int` 仅在范围长度不超过 256 时枚举，范围过大时返回不可修复并降级，避免搜索开销失控。

### 可靠性边界（原文）

> 非法 `target_names`、0 值依赖、NaN、非整除且不可修复等场景都会记录 warning 并保持可控降级，不直接中断寻优流程。

### 降级机制（原文）

> 若修复失败，三元除法会根据上下界降级截断；对于 `int` 非整除且无法修复、无法安全截断的场景，会抛出 `ValueError` 向上传播，最终由 `op_func` 捕获并置 `fitness=inf`，使 PSO 自动淘汰该不自洽粒子。

### 安全边界（原文）

> 本特性不新增外部输入入口、不新增文件写入和网络访问；主要风险来自配置错误，已通过字段名校验、候选集限制和 warning 暴露。

---

## 【表格解读】

### 表 1：修订记录（原文逐字还原）

| 日期 | 修订版本 | 修改描述 | 作者 | RFC文档 |
| -- | -- | -- | -- | -- |
| 2026-05-16 | 1.0 | 初稿完成 | 待确认 | 待确认 |
| 2026-04-27 | 1.1 | 新增 `-c/--config` 命令行参数，支持用户在启动时显式指定配置文件路径 | 待确认 | 待确认 |

**逐行解读**：注意原文中两个日期的时间顺序——`2026-05-16` 为初稿（版本 1.0），`2026-04-27` 为补丁（版本 1.1）。这意味着 1.1 版本的 `-c/--config` 实际上是比 1.0 初稿**更早**合并进来的改动，作者与 RFC 文档均为「待确认」状态。

### 表 2：优先级策略（原文逐字还原）

| 策略 | 配置 | 行为 |
| -- | -- | -- |
| `fixed` | `priority_policy="fixed"`，可选 `priority=["tp","pp"]` | 按显式 `priority` 保留高优先级字段；配置缺失或非法时退化为 `target_names` 顺序 |
| `balanced` | `priority_policy="balanced"` 或缺省 | PSO 前半粒子使用 `target_names` 正序，后半粒子使用反序；奇数迭代轮次整体翻转方向；无上下文时退化为 `target_names` 顺序 |

**逐行解读**：
- `fixed` 策略：用户必须显式声明 `priority` 列表，工具严格按列表顺序决定哪个字段被 `keep`、哪个被 `adjust`；当 `priority` 配置缺失或非法（例如只列了一个名字）时回退到 `target_names` 的声明顺序，体现"显式优先、退化兜底"的设计哲学。
- `balanced` 策略：在 PSO 种群维度（前/后半粒子）和迭代维度（奇/偶数轮）**双重翻转**优先级方向，目的是消除 PSO 搜索中对某一类源字段的结构性偏置（structural bias）；但在非 PSO 调用路径（无 `DecodeContext`）下无法做到粒子级区分，故退化为 `target_names` 顺序。

### 表 3：数据模型定义（原文逐字还原）

| 字段 | 类型 | 说明 |
| -- | -- | -- |
| `OptimizerConfigField.dtype="ternary_factories"` | 字符串枚举 | 三元除法派生字段，值由两个源字段共同决定 |
| `OptimizerConfigField.dtype="ternary_times"` | 字符串枚举 | 三元乘法派生字段，值由两个源字段共同决定 |
| `dtype_param.target_names` | `list[str]` | 两个依赖字段名称，必须能匹配同一 `target_field` 中的字段名 |
| `dtype_param.product` | `int`/`float` | 乘积系数；缺省为 `1` |
| `dtype_param.dtype` | `str` | 派生结果类型，支持复用 `dtype_func` 中的转换函数 |
| `dtype_param.min_value` | `int`/`float` | `ternary_factories` 结果下界；`int` 类型缺省为 `1` |
| `dtype_param.max_value` | `int`/`float` | `ternary_factories` 结果上界；缺省不限制 |
| `dtype_param.priority_policy` | `fixed`/`balanced` | 三元除法修复优先级策略；缺省为 `balanced` |
| `dtype_param.priority` | `list[str]` | `fixed` 策略下的显式优先级顺序 |
| `DecodeContext.particle_index` | `int` | 当前 PSO 粒子索引，0-based |
| `DecodeContext.n_particles` | `int` | 当前 PSO 种群大小 |
| `DecodeContext.iteration` | `int` | 当前 PSO 迭代轮次，0-based；`balanced` 策略在奇数迭代轮次翻转优先级方向，避免同一粒子在整个优化过程中长期固定偏向同一修复顺序 |

**逐行解读**：
- 前两行扩展了 `OptimizerConfigField.dtype` 的取值集合，使配置模型支持三元派生。
- 中间七行 `dtype_param.*` 是三元字段在 `dtype_param` 子表中的参数集合：其中 `target_names` 是**必选**核心参数，`product`/`dtype`/`min_value`/`max_value`/`priority_policy`/`priority` 均为可选。
- 后三行是新增 `DecodeContext` 上下文对象，承载 PSO 维度的状态信息（粒子索引、种群大小、迭代轮次），是 `balanced` 策略实现"按粒子分半切换"和"按迭代翻转方向"语义的基础。

### 表 4：`-c/--config` 参数说明（原文逐字还原）

| 参数 | 可选/必选 | 默认值 | 说明 |
| -- | -- | -- | -- |
| `-c` 或 `--config` | 可选 | `None` | 自定义配置文件路径（TOML 格式）。支持绝对路径、含目录分隔符的相对路径、纯文件名（在当前工作目录下查找）三种形式。指定文件具有最高配置优先级。不指定时工具按默认路径顺序自动搜索配置文件。 |

**逐行解读**：参数默认值为 `None`，表示"不指定"，此时走原有默认路径搜索逻辑；指定后文件被追加到配置加载列表**末尾**（即最高优先级），意味着它能覆盖默认配置和旧的环境变量 `MODEL_EVAL_STATE_CONFIG_PATH`。三种路径形式的覆盖度体现了从「完全控制」到「轻量引用」的灵活性。

### 表 5：配置参数说明（原文逐字还原）

| 参数 | 可选/必选 | 默认值 | 说明 |
| -- | -- | -- | -- |
| `dtype` | 必选 | 无 | 取 `ternary_factories` 或 `ternary_times` |
| `target_names` | 必选 | 无 | 两个依赖字段名，必须与同一 `target_field` 中的 `name` 一致 |
| `product` | 可选 | `1` | 乘积系数；三元除法中作为被除数，三元乘法中作为乘数 |
| `dtype_param.dtype` | 可选 | `int` | 派生结果类型，复用 `int`、`float` 等转换 |
| `min_value` | 可选 | `int` 类型为 `1`，其他类型为无限制 | 三元除法结果下界 |
| `max_value` | 可选 | 无限制 | 三元除法结果上界 |
| `priority_policy` | 可选 | `balanced` | `fixed` 使用显式优先级；`balanced` 按 PSO 粒子分半切换优先级 |
| `priority` | 可选 | `target_names` | `fixed` 策略下的优先级顺序，必须包含两个 `target_names` |

**逐行解读**：前两个为必选，其余六个均有缺省行为。值得注意的是 `priority` 的默认值是 `target_names`——这是**配置层面的缺省值**，与代码运行时的"无 DecodeContext 退化"是不同层面的语义；`priority_policy` 缺省为 `balanced` 表明设计者默认认为「平衡搜索覆盖」比「固定优先级」更适合作为通用策略。

---

## 【公式解读】

### 公式 1：三元除法派生（原文）

$$value = \frac{product}{field\_a \times field\_b}$$

**符号含义**：
- `value`：派生字段（如 `dp`）的目标值。
- `product`：配置参数中的乘积系数（如 `world_size`），缺省为 `1`。
- `field_a`、`field_b`：两个源字段（如 `tp`、`pp`），通过 `dtype_param.target_names = ["tp", "pp"]` 指定。

**作用**：表达 `tp * pp * dp = world_size` 这类三参数乘积约束，使框架可通过两个源字段反推派生字段。

### 公式 2：三元乘法派生（原文）

$$value = product \times field\_a \times field\_b$$

**符号含义**：与公式 1 同名符号含义一致；此处 `product` 作为乘数参与（缺省为 `1`）。

**作用**：适用于 `total_tokens = seq_len * batch * 1` 这类由两个因子直接相乘得到派生量的场景（与 `times` 二元派生语义一致，但显式接收两个源字段）。

### 公式 3：整除约束（原文伪代码）

$$product \bmod (field\_a \times field\_b) == 0$$

**符号含义**：所有符号同公式 1；`%` 为取模运算。

**作用**：`int` 类型下保证 `product / (field_a * field_b)` 整除，避免 `int()` 截断破坏乘积自洽性。这是触发约束修复的核心条件之一。

### 公式 4：合法组合三约束（原文隐式）

合法组合必须同时满足：
1. 两个源字段均非 0（`field_a != 0 ∧ field_b != 0`）
2. `int` 类型下 `product % (field_a * field_b) == 0`
3. `min_value ≤ value ≤ max_value`

**作用**：构成两阶段修复搜索的"过滤器"，任何不满足三条中任一条件的组合都视为非法候选。

---

## 【关联】

文档明确指出以下模块/特性的耦合与扩展关系：

### 上游依赖（已有特性）
- **`OptimizerConfigField`**（`config/config.py`）：参数字段模型是本特性的扩展基础，`update_constant` 机制用于将派生字段（`min=max=0`）标记为常量从而**不占用粒子维度**。
- **`map_param_with_value`**（解码流程）：本特性在其二元派生处理之后**追加三元分支**，不破坏原有流水线。
- **`PSOOptimizer.op_func`** 与 **`Scheduler.run_with_request_rate`**：被扩展为接收 `DecodeContext` 并将修复后参数回写到粒子数组 `x[i]`。
- **`factories` / `times` 二元派生**（语义不变）：本特性**不改变**已有二元派生语义，只在其上层叠加三元能力。

### 同源同期特性
- **健康检查、多模型配置**等扩展功能（被文中提及为 `config.toml` 配置项膨胀的原因之一），是 `-c/--config` 参数引入的动机。
- **环境变量 `MODEL_EVAL_STATE_CONFIG_PATH`**：旧版绕行方案，与 `-c/--config` 共存但优先级更低。

### 下游覆盖
- **服务化框架**（vllm、mindie 等）：仅作为最终参数接收方，**不需要感知三元推导细节**。
- **测试工具**（`test/ut/python/test_optimizer/config/test_config_config.py`）：覆盖三元关系、优先级解析、两阶段修复、上下文集成，以及 `-c/--config` 的路径解析、文件验证、优先级合并。

### 上下游关系图（按原文系统架构描述）

> 服务框架 / 测试工具 ← 最终参数 ← 参数配置解码层（三元关系集中处）← `OptimizerConfigField` / `map_param_with_value`

---

## 【使用方法】

### 启用方式（三元关系）

通过 TOML 配置文件中 `[[mindie.target_field]]` 的 `dtype` 字段启用，原文给出两个标准示例：

**`ternary_factories` 示例**（原文）：

```toml
[[mindie.target_field]]
name = "dp"
config_position = "BackendConfig.ModelDeployConfig.ModelConfig.0.dp"
min = 0
max = 0
dtype = "ternary_factories"
dtype_param = { target_names = ["tp", "pp"], product = 32, dtype = "int", min_value = 1, max_value = 32, priority_policy = "balanced" }
```

**`ternary_times` 示例**（原文）：

```toml
[[mindie.target_field]]
name = "total_tokens"
config_position = "Example.totalTokens"
min = 0
max = 0
dtype = "ternary_times"
dtype_param = { target_names = ["seq_len", "batch"], product = 1, dtype = "int" }
```

**派生字段约定**：派生字段通常配置为 `min = max = 0`，由 `OptimizerConfigField.update_constant` 标记为常量，**不占用粒子维度**。

### 启用方式（命令行入口，原文）

```bash
# 三元关系功能通过配置文件生效
msserviceprofiler optimizer -e mindie -b ais_bench

# 如需指定自定义配置文件，可使用 -c 参数
msserviceprofiler optimizer -e vllm -b vllm_benchmark -c /data/configs/my_config.toml
```

### `-c/--config` 多场景示例（原文）

```bash
# 针对 GLM-5.1 的寻优，使用项目配置目录下的配置
msserviceprofiler optimizer -e vllm -b vllm_benchmark -c /data/configs/glm_config.toml

# 切换到另一个模型的配置，无需修改环境变量
msserviceprofiler optimizer -e vllm -b vllm_benchmark -c /data/configs/qwen_config.toml
```

### 使用约束（原文逐条）

- `ternary_factories` 和 `ternary_times` 第一版**仅支持两个依赖字段**。
- `target_names` 必须指向已定义字段；字段名大小写必须一致。
- `ternary_factories` 的依赖字段值不能为 0，否则跳过计算并保留原值。
- `ternary_times` 的依赖字段值不能为 `None` 或 `NaN`，否则跳过计算并保留原值。
- 约束修复只对可枚举候选集生效：`enum` 字段使用 `dtype_param`，`int` 字段仅在范围长度**不超过 256** 时枚举。
- 若修复失败，三元除法会根据上下界降级截断；对于 `int` 非整除且无法修复、无法安全截断的场景，会抛出 `ValueError`，最终由 `op_func` 捕获并置 `fitness=inf`。
- `balanced` 策略只有在 PSO 路径传入 `DecodeContext` 时才能按粒子分半切换；其他调用路径退化为 `target_names` 顺序。
- `-c/--config` **不支持同时传入多个配置文件**；如需合并多份配置，请先手动合并后指定。
- `-c/--config` 指定的文件必须为合法 TOML 格式，格式错误时抛出 `ValueError` 并输出详细错误位置。

### 兼容与迁移（原文）

- 既有配置**不需要迁移**；已有 `factories` 和 `times` 字段继续按原语义执行。
- 插件如需表达 `tp * pp * dp = product` 这类关系，可将派生字段从自定义处理迁移为 `ternary_factories`，并把派生字段配置为 `min = max = 0`。
- `-c/--config` 对旧版本**完全向前兼容**：不指定时行为与历史版本完全一致；已有环境变量 `MODEL_EVAL_STATE_CONFIG_PATH` 仍然有效，但优先级低于 `-c`。
- 回滚方式（原文末尾被截断）：将三元派生字段恢复为旧的二元（处理方式，原文于此处中断）。

## 图文联合解读

- `image.png`: **1）图示内容**：三大包结构——「自动寻优」（`PSOoptimizer.op_func`→`Scheduler.run_with_request_rate`）、「参数配置解码」（`map_param_with_value`→`update_optimizer_value`→`resolve_priority`/`_repair_ternary_factories_with_priority`/`field_to_param`）、「运行对象」（Simulator/Benchmark）。标注关键数据流：预解码粒子→运行前再次解码→排查派生字段→非整除或越界时修复→修复后位置回写→使用修复后粒子评估。

**2）技术结论**：三元派生字段的解码、优先级修复与PSO位置回写形成闭环，保证评估参数与粒子位置一致。

**3）与文档关系**：图示对应文档"目标"——支持`ternary_factories`、优先级感知修复（`fixed`/`balanced`）及位置回写机制。
- `image.png`: **1）图示内容**：三大包结构——「自动寻优」（`PSOoptimizer.op_func`→`Scheduler.run_with_request_rate`）、「参数配置解码」（`map_param_with_value`→`update_optimizer_value`→`resolve_priority`/`_repair_ternary_factories_with_priority`/`field_to_param`）、「运行对象」（Simulator/Benchmark）。标注关键数据流：预解码粒子→运行前再次解码→排查派生字段→非整除或越界时修复→修复后位置回写→使用修复后粒子评估。

**2）技术结论**：三元派生字段的解码、优先级修复与PSO位置回写形成闭环，保证评估参数与粒子位置一致。

**3）与文档关系**：图示对应文档"目标"——支持`ternary_factories`、优先级感知修复（`fixed`/`balanced`）及位置回写机制。
- `image.png`: **1）图示内容**：三大包结构——「自动寻优」（`PSOoptimizer.op_func`→`Scheduler.run_with_request_rate`）、「参数配置解码」（`map_param_with_value`→`update_optimizer_value`→`resolve_priority`/`_repair_ternary_factories_with_priority`/`field_to_param`）、「运行对象」（Simulator/Benchmark）。标注关键数据流：预解码粒子→运行前再次解码→排查派生字段→非整除或越界时修复→修复后位置回写→使用修复后粒子评估。

**2）技术结论**：三元派生字段的解码、优先级修复与PSO位置回写形成闭环，保证评估参数与粒子位置一致。

**3）与文档关系**：图示对应文档"目标"——支持`ternary_factories`、优先级感知修复（`fixed`/`balanced`）及位置回写机制。
