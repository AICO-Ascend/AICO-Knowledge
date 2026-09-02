# 算子融合规则配置功能（optimization\_switch）

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/optimization_switch.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/optimization_switch.md

# 深度解读：算子融合规则配置功能（optimization_switch）

## 【定位】

本文档描述 TorchAir 在 GE 图模式下提供的「算子融合规则配置开关」（`optimization_switch`）能力——即在算子编译阶段允许用户按业务需要灵活地开启/关闭任意融合规则 Pass，从而降低网络推理时间、提升整网性能；同时它也是对既有 `fusion_switch_file` 能力的覆盖与替代入口。

---

## 【技术要点】

1. **能力本质**：通过 `config.ge_config.optimization_switch` 设置融合 Pass 的控制开关，编译时按用户声明决定每个 Pass 是执行还是跳过。
2. **取值格式**：严格的 key-value 字符串，形如 `"Passname1:on;Passname2:off"`，key 为 Pass 名称，value 仅可取 `on`（开）或 `off`（关），**不支持大小写模式匹配**，多条规则用**英文分号 `;`** 分隔。
3. **作用范围**：原文写明「适用于所有融合规则的指定」，不需要额外维护一份独立的 JSON 文件。
4. **优先级关系**：当 `optimization_switch` 与 `fusion_switch_file` 同时存在且配置了同一规则时，**以 `optimization_switch` 配置为准**；而 `config.fusion_config.fusion_switch_file` 仅能关闭图融合与 UB 融合规则。
5. **使用约束**：仅适用于 **GE 图模式场景**（非图模式/单算子直调场景不在本特性覆盖范围）。
6. **配置入口与编译入口**：配置写入 `torchair.CompilerConfig()` 的 `ge_config.optimization_switch` 字段，再通过 `torchair.get_npu_backend(compiler_config=config)` 取得 backend，最后经 `torch.compile(model, backend=npu_backend)` 触发整图编译。

---

## 【关键机制与数据】

**工作原理 / 数据流**（基于原文描述还原）：

1. 用户在 Python 侧构造 `CompilerConfig` 对象，并设置 `config.ge_config.optimization_switch` 字符串。
2. `get_npu_backend` 读取该 compiler_config 封装成 NPU 后端。
3. `torch.compile` 调用后端时，TorchAir 将 `optimization_switch` 透传给 GE（图引擎）编译流程。
4. GE 在执行每个图优化 Pass（融合规则）前，按 `Passname:on/off` 进行过滤：`on` 正常执行该融合，`off` 跳过该融合。
5. 因为该开关作用于 GE 图模式全过程，所以列表中给出的所有 Pass（涵盖算子融合、UB 融合、BatchNorm 融合、Conv 量化融合、DynamicRNN 系列、Transdata/Permute/YOLO 等算子族）都可单独控制。

**数据/性能说明**：
- 原文**未给出**任何具体的性能数字（如加速比、推理时延降低幅度、显存节省等），也**未给出**关于某个 Pass `on/off` 后行为差异的量化数据。
- 原文未提供公式、阈值或性能基准曲线；仅声明目标为「降低网络推理时间、提高整网性能」。

---

## 【表格解读】

原文包含一张参数说明表，逐字还原如下：

**表 1 参数说明**（原文为单一参数表）

| 参数名 | 说明 |
|--|--|
| `optimization_switch` | 算子编译时，融合规则的控制开关。取值格式为 key-value 键值对，形如 `"Passname1:on;Passname2:off"`，key 为 Pass 名称，value 为 `on`（表示开）或 `off`（表示关），**不支持大小写模式匹配**，多组配置使用**英文分号分隔**。可配置的融合规则请参见融合规则列表。 |

**逐行解读**：
- **参数名 `optimization_switch`**：是挂在 `config.ge_config` 命名空间下的属性，写入路径为 `config.ge_config.optimization_switch`。
- **key-value 键值对格式**：与一般环境变量或 KV 配置一致，便于解析与扩展；每个键值对形如 `<Pass名>:<on|off>`。
- **value 取值约束**：仅允许 `on`/`off`，二者必须小写，原文明确「不支持大小写模式匹配」，意味着写成 `On`、`OFF` 不会被识别为合法值。
- **分隔符**：多组规则之间用英文分号 `;` 分隔，而非逗号或换行；这对用户在脚本里拼接字符串时是一个容易出错的细节。
- **可配置范围**：文档后部给出了完整的「融合规则列表」，只要列表中出现的 Pass 名都可以作为 key；列表外的 Pass 名称按原文语义不会被该开关控制。

---

## 【公式解读】

原文无公式。性能、阈值、Pass 触发条件等均未以数学形式给出，故本节标注为 **原文无公式**。

---

## 【关联】

- **[`fusion_switch_file.md`](fusion_switch_file.md)**：姊妹篇 / 同类能力的旧入口。原文给出的关键差异是：
  - `fusion_switch_file` 只能关闭**图融合**与 **UB 融合**两类规则，且**必须配套 JSON 文件**；
  - `optimization_switch` 覆盖**所有**融合规则，**无需 JSON 文件**；
  - 两者同时配置且规则冲突时，`optimization_switch` 优先。
  因此本文档可视为 `fusion_switch_file` 的广义替代/补充。
- **[`../../api/torchair/get_npu_backend.md`](../../api/torchair/get_npu_backend.md)**：本文档中 `optimization_switch` 写入的 `CompilerConfig` 需要通过 `torchair.get_npu_backend(compiler_config=config)` 注入到 `torch.compile` 的 backend 中，因此该 API 是本特性的**编译入口与配置装载点**；其返回值类型、签名约定及与其他参数（如 `aicconfig` 系列）的组合方式在该链接的 API 文档中描述（本文未展开）。
- **CANN 图融合和 UB 融合规则参考**：原文提示「更多融合规则的介绍请参见《CANN 图融合和 UB 融合规则参考》」，说明 Pass 的具体语义定义归属于 CANN 文档体系，TorchAir 仅提供启用开关。
- **GE 图模式**：本特性只对 GE 图模式生效，意味着它与 TorchAir 中其他仅作用于单算子或 ACL 图执行路径的能力互不干扰；与 `torch.compile(dynamic=...)`、`config.aicconfig.*` 等其他 `CompilerConfig` 字段属于并列配置。

---

## 【使用方法】

**启用方式**（原文 Python 示例）：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 算子融合规则配置开关
config.ge_config.optimization_switch = "Passname1:on;Passname2:off"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**关键配置项与命令**：
- **配置项**：`config.ge_config.optimization_switch`
- **取值**：字符串，格式 `<PassName>:<on|off>`，多条用 `;` 分隔。
- **生效条件**：仅在 GE 图模式下生效（使用约束）。
- **典型开关语义**：
  - `<Pass>:on` —— 启用该融合规则（默认行为）。
  - `<Pass>:off` —— 关闭该融合规则，跳过对应图优化步骤。

**注意事项**（来自原文）：
- 原文明确「仅供参考不支持直接拷贝运行」，即示例仅展示调用骨架，实际 Pass 名称需替换为「融合规则列表」中的合法条目。
- 原文提醒「部分融合规则关闭后可能会对功能使用有影响，请谨慎操作」，意味着 `off` 会改变后续算子的 IR 形态，可能影响精度、内存占用或某些算子族的合法执行路径。
- 原文未给出 CLI/环境变量形式的开关命令，**仅提供 Python API 入口**；也未提供任何形式的「全量 `off`」或「全量 `on`」快捷语法，故关闭/启用必须按 Pass 名逐条显式声明。
