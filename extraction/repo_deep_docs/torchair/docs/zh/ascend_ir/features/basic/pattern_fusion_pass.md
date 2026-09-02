# FX图算子融合Pass配置功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/pattern_fusion_pass.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/pattern_fusion_pass.md

# FX图算子融合Pass配置功能 — 一体化深度解读

---

## 【定位】

本篇文档描述 TorchAir 在 PyTorch FX 图级别**基于 PyTorch 原生 Pattern 替换机制**将多个小算子替换为单一融合算子的能力，目的是减少图下发开销、提升模型在昇腾 NPU 上的执行效率，并同时提供了默认 Pass 表、自定义注册入口、关闭开关以及 dump 验证手段。

---

## 【技术要点】

1. **能力来源**：TorchAir 集成了 **PyTorch 原生 Pattern** 算子融合能力（即 `register_replacement` 接口所代表的能力），通过匹配特定算子组合并整体替换为融合算子。
2. **默认 Pass 覆盖范围（表 1 共 3 条规则）**：
   - `npu_add_rms_norm → npu_dynamic_quant（含 smooth_scales）` → 替换为 `npu_add_rms_norm_dynamic_quant`
   - `npu_add_rms_norm → flatten(0,1) → npu_dynamic_quant（不含 smooth_scales），输出 scaleOut 走 view(-1,1)` → 替换为 `npu_add_rms_norm_dynamic_quant`（自动处理 flatten 与 view）
   - `npu_add_rms_norm → 取最后一维尺寸 h → view(-1, h) → to(torch.float32)` → 替换为 `npu_add_rms_norm_cast`（自动处理 view）
3. **默认开启、可关闭**：通过 `compiler_config.experimental_config.pattern_fusion_pass` 控制，**默认 `True`（开启）**，置 `False` 即关闭。
4. **依赖版本**：必须 **PyTorch 2.6.0 或更高版本**。
5. **约束点（4 条硬约束）**：① 默认与自定义 Pass 均通过 `pattern_fusion_pass` 统一开关；② 表格中 `matmul` 输入**必须为三维**；③ `npu_transpose_batchmatmul` 与 `npu_add_rms_norm_quant` 在 **max-autotune 模式下不生效**；④ 融合算子输出必须被正常使用，融合后消失的中间结果不可被其他位置引用，否则无法完成融合。
6. **自定义扩展路径**：用户可通过 `register_replacement` 接口注册自定义算子融合 Pass，但需**自行实现自定义算子入图**并保证融合规则正确性。

---

## 【关键机制与数据】

**工作机制（基于原文重构）**：

- **匹配层**：TorchAir 在 FX 图上运行 Pattern 匹配，按表 1 三条规则扫描算子组合的拓扑结构（输入来源、shape 变化、数据类型转换、是否含 `smooth_scales`）。
- **替换层**：当某段子图满足匹配规则时，整段子图被替换为单个融合算子节点；替换过程中部分 shape 操作（`flatten(0,1)`、`view(-1,1)`、`view(-1,h)`）由融合算子**自动承载**（即由"显式节点"变为"算子内部行为"）。
- **开关层**：开关挂在 `CompilerConfig.experimental_config.pattern_fusion_pass`，属于 FX 图级 Pass，与图编译流水线串联；开关为 `False` 时跳过整个 Pattern 替换流程。
- **验证层**：通过 `graph_dump` 功能 dump FX 图结构，可观察到融合算子节点取代原多节点序列（例如 dump 输出中出现 `npu_add_rms_norm_dynamic_quant.default(...)` 单节点，并伴随必要的 `getitem` 与 reshape 节点）。

**dump 原文摘录（数据流示例，原文）**：

```txt
npu_add_rms_norm_dynamic_quant_default = torch.ops.npu.npu_add_rms_norm_dynamic_quant.default(arg2_1, arg1_1, arg0_1, output_mask = [True, True]);
getitem_5: "i8[2, 3, 4]"  = npu_add_rms_norm_dynamic_quant_default[0]   # quant 输出
getitem_6: "f16[2, 3, 4]" = npu_add_rms_norm_dynamic_quant_default[2]   # norm 输出
getitem_7: "f32[2, 3]"    = npu_add_rms_norm_dynamic_quant_default[3]   # scaleOut
view_default:   "i8[6, 4]"  = torch.ops.aten.reshape.default(getitem_5, [6, 4])
view_default_1: "f32[6, 1]" = torch.ops.aten.reshape.default(getitem_7, [-1, 1])
return (view_default, view_default_1, getitem_6)
```

**原文数据/性能说明**：原文仅给出"可有效减少部分场景下不必要的下发开销、提高模型执行效率"以及"可通过优化对比来选择最佳方案"的定性表述，**未给出具体性能数字、吞吐或延迟百分比**，故本节不杜撰量化指标。

---

## 【表格解读】

### 表 1 — 已支持的算子融合 Pass

| 替换规则 | 对应的融合算子 |
|---|---|
| `npu_add_rms_norm` 输出直接作为 `npu_dynamic_quant`（含 `smooth_scales` 参数）输入 | `npu_add_rms_norm_dynamic_quant` |
| `npu_add_rms_norm` 输出经 `flatten(0,1)` 后作为 `npu_dynamic_quant`（不含 `smooth_scales` 参数）输入，且 `npu_dynamic_quant` 输出的 `scaleOut` 执行 `view(-1,1)` | `npu_add_rms_norm_dynamic_quant`（自动处理 flatten 与 view 操作） |
| `npu_add_rms_norm` 输出先获取最后一维尺寸 `h`，再经 `view(-1, h)` 变形及 `to(torch.float32)` 类型转换 | `npu_add_rms_norm_cast`（自动处理 view） |

**逐行解读**：

- **第 1 行（基础链路）**：仅当 `npu_dynamic_quant` 调用带 `smooth_scales` 参数时，触发融合为 `npu_add_rms_norm_dynamic_quant`；无额外 shape 变换，融合算子直接消费 `npu_add_rms_norm` 的输出。
- **第 2 行（带 shape 适配的链路）**：匹配条件更严格——前段必须有 `flatten(0,1)`，且 `npu_dynamic_quant` **不含** `smooth_scales`，`scaleOut` 还要继续被 `view(-1,1)`；融合后 `flatten` 与 `view` 由算子**隐式处理**（等价于：用户侧不再生成对应 ATen 节点）。
- **第 3 行（Cast 链路）**：目标不是量化，而是**类型转换**——沿最后一维 `h` 做 `view(-1,h)` 后再 `to(torch.float32)`；融合算子为 `npu_add_rms_norm_cast`，同样由算子自动处理 view。

### 表 2 — 参数说明

| 参数名 | 说明 |
|---|---|
| `pattern_fusion_pass` | FX 图是否开启算子融合 Pass 配置，布尔类型。`False`：关闭。`True`（默认值）：开启。 |

**逐行解读**：

- **字段位置**：`pattern_fusion_pass` 挂在 `config.experimental_config` 下，属于实验性配置项（`experimental_config` 前缀暗示 API 可能在后续版本调整）。
- **取值语义**：单一布尔值即可全局启用/停用 FX 图算子融合 Pass；**默认 `True`**，意味着开箱即用，无需用户手动开启。

---

## 【公式解读】

原文无公式（仅含 3 张图示 `figures/241127100846395-7/8/9.png` 表示融合规则示意图，文档中无可解析的 LaTeX/伪代码数学表达式）。**原文无公式**。

---

## 【关联】

| 关联对象 | 关系 | 链接 |
|---|---|---|
| `register_replacement` | **上游机制**：PyTorch 原生 Pattern 替换接口，是本功能自定义 Pass 的注册入口 | `../../api/torchair/register_replacement-0.md` |
| 自定义算子入图 | **配套要求**：自定义融合 Pass 注册后，必须让自定义融合算子能进入 FX 图，方可被替换匹配 | `../../../custom_op_graph/custom_op_graph.md` |
| `get_npu_backend` | **下游挂载点**：通过其 `compiler_config` 参数将 `pattern_fusion_pass` 注入编译流水线，最终作为 `torch.compile` 的 `backend` | `../../api/torchair/get_npu_backend.md` |
| 图结构 dump（`graph_dump.md`） | **验证手段**：开启 dump 后可在 FX 图中观察到融合算子节点（如 `npu_add_rms_norm_dynamic_quant.default`）取代原多节点链 | `graph_dump.md` |

**关系链总览**：`register_replacement` 提供 Pattern 替换底层能力 → `custom_op_graph` 让自定义融合算子可入图 → `get_npu_backend.compiler_config.experimental_config.pattern_fusion_pass` 控制是否启用 → `graph_dump` 用于 dump 后验证融合是否生效。

---

## 【使用方法】

**启用方式（原文）**：

- 本功能**默认开启**（`pattern_fusion_pass = True`），无需用户额外配置即可生效。
- 关闭示例（原文代码片段，标注"仅供参考，不支持直接拷贝运行"）：

```python
import torch_npu
import torchair

config = torchair.CompilerConfig()
# FX图中算子融合Pass配置
config.experimental_config.pattern_fusion_pass = False
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**配置项**：

- `pattern_fusion_pass`（布尔，`True`/`False`，**默认 `True`**），位于 `config.experimental_config` 命名空间下。

**验证命令/步骤（原文）**：

1. 启用 `pattern_fusion_pass` 后，参考 `graph_dump.md` 开启 FX 图 dump。
2. 检查 dump 输出中是否出现融合算子节点（如 `npu_add_rms_norm_dynamic_quant.default(...)` 单节点及其 `getitem`/reshape 节点），以确认替换生效。

**自定义扩展命令（原文）**：

- 通过 `register_replacement` 接口注册自定义融合规则；具体调用示例详见 `../../api/torchair/register_replacement-0.md`。

**原文未涉及**：未给出 CLI 命令行开关、未给出环境变量、未给出性能基准测试脚本或对比数据。

## 图文联合解读

- `241127100846395-7.png`: **图解：** 左图"融合前"展示`npu_add_rms_norm`（输入x1/x2/gamma，输出y/smooth_scale/xOut）与`npu_dynamic_quant`（输入y/smooth_scale，输出yOut/scale1Out）两个独立算子；右图"融合后"两者合并为单一`npu_add_rms_norm_dynamic_quant`算子，外部`smooth_scale`直接作为输入，省去中间y的传递。

**结论：** 通过Pattern匹配将多算子替换为融合算子，减少下发与中间张量开销，对应文档表1第一行规则及"减少不必要的下发开销"论点。
- `241127100846395-8.png`: **图文联合解读：**

图示对比了算子融合前后的FX图结构：融合前，`npu_add_rms_norm` 与 `npu_dynamic_quant` 为两个独立算子，中间夹带 `flatten(0,1)` 和 `view(-1,1)`；融合后合并为单一算子 `npu_add_rms_norm_dynamic_quant`，自动内嵌这些维度变换操作。

该图直观论证了**算子融合Pass可消除下发与中间调度开销**这一技术结论，对应文档表1第二行所述的融合规则（`flatten(0,1)` 后的 `npu_add_rms_norm` 输出作为 `npu_dynamic_quant` 输入，scaleOut 经 `view(-1,1)`），验证了融合功能对调用透明且能简化计算图。
- `241127100846395-9.png`: 1) **图示内容**：左侧"融合前"展示x1、x2、gamma输入经`npu_add_rms_norm`后，输出y经`size(-1)`取维度h、再经`view(-1,h)`和`npu_dtype_cast`转float32的流程；右侧"融合后"将多步合并为单一算子`npu_add_rms_norm_cast`，自动处理view，输出y、y_cast、xOut。

2) **技术结论**：证明FX算子融合Pass能将"add_rms_norm + 取尺寸 + view + 类型转换"的多节点链路折叠为单个融合算子，减少算子下发与中间张量。

3) **文档呼应**：直观对应表1第三行的替换规则，论证算子融合可降低下发开销、提升执行效率。
