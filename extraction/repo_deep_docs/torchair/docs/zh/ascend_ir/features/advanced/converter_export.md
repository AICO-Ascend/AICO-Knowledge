# 算子Converter支持度导出功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/converter_export.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/converter_export.md

# 算子Converter支持度导出功能 — 一体化深度解读

---

## 【定位】

本文档描述的是 TorchAir 中一项面向 **GE 图模式** 的**诊断/可观测性能力**：通过 `config.debug.fx_summary` 配置项，把 FX 图中每一个 ATen（或 builtin）算子的 Converter 实现情况、调用次数、输入/输出 dtype 与 shape 等元数据，导出为一份带时间戳的 CSV 文件，供用户识别哪些算子尚未支持入图、从而有针对性地进行 Converter 补齐。

---

## 【技术要点】

1. **能力边界**：原文明确"本功能仅适用于 GE 图模式场景"——即与 Ascend IR 图编译（GE 后端）这条链路绑定，不覆盖纯 Eager 或其他图后端。
2. **导出开关**：`config.debug.fx_summary.type = "csv"` 决定是否启用；原文强调"当前仅支持 csv 格式"，且默认为 `None`（不导出）。
3. **编译旁路开关**：`config.debug.fx_summary.skip_compile`，bool 类型，**默认值 `True`**（即默认跳过 Ascend IR 图编译、以 FX 图 Eager 方式执行）；只有当模型本身可正常图执行又想顺手收集 FX 信息时，才设为 `False`。
4. **强制运行约束**：原文以 NOTE 形式给出强约束——正式跑图模式时必须**删除或注释** `config.debug.fx_summary.type = "csv"` 这行，否则图模式无法正确启用。
5. **产物形态**：`summary_${timestamp}.csv`，位置为"当前执行路径下"，列固定为「目标函数 / 函数类型 / 支持状态 / 调用次数 / 输入统计 / 输出统计」六列。
6. **支持状态三档分类**：未实现（Converter 未实现，不支持入图）、已支持（已实现 Converter，支持入图）、部分支持（仅部分场景支持入图）。

---

## 【关键机制与数据】

### 工作机制（原文逐句还原）

- **前置判断链**（原文）："PyTorch 模型启用图模式前，需要先识别 FX 图中 IR 是否有对应 Converter 实现。若有，表示算子支持接入 Ascend IR 计算图；否则不支持入图。"——即 Converter 支持度检查是**进入图编译的必经闸口**，本功能把这个闸口上的判定结果与调用统计一并落盘。
- **收集策略**（原文）：`skip_compile=True`（默认）时跳过 Ascend IR 图编译，"该场景下能收集完整的 FX 信息"——这是因为图编译失败会中断收集，跳过编译能拿到更完整的算子清单；反之 `skip_compile=False` 适用于"模型支持以图模式执行且想收集 FX 信息的场景"，此时 FX 收集与图编译并行进行。
- **数据流**：`torch.compile(model, backend=npu_backend)` → 内部走 `torchair.get_npu_backend(compiler_config=config)` 的 `compiler_config.debug.fx_summary` → 在 FX 图遍历阶段为每个 target function 统计 `调用次数 / 输入统计 / 输出统计` 并落 `summary_<timestamp>.csv`。

### 性能/规模数据（仅取自原文示例）

- 示例 CSV 中四行算子，调用次数分别为 **36 / 62 / 120 / 62**。
- 输入 dtype 全部为 `float16`，部分带 `float32`（如 layer_norm 输出、getitem 的 tuple 元素）。
- `s0` 出现在 shape 中，原文未解释，按 PyTorch FX 动态 shape 惯例视为符号维（原文未给出该符号的具体语义说明）。

---

## 【表格解读】

### 表 1：参数说明（逐字还原）

| 参数名 | 说明 |
| -- | -- |
| `fx_summary.type` | 指定导出的文件类型，字符串类型。默认为 None，不导出图中的 ATen 算子信息。<br>当前仅支持 csv 格式。 |
| `fx_summary.skip_compile` | 是否跳过 Ascend IR 图编译，以 FX 图 Eager 方式执行。bool 类型。<br>True（默认值）：跳过 Ascend IR 图编译，以 FX 图 Eager 方式执行。适用于模型 Converter 不全，图模式不能正常执行的场景，该场景下能收集完整的 FX 信息。<br>False：采用 Ascend IR 图编译。适用于模型支持以图模式执行且想收集 FX 信息的场景。 |

**逐行解读**：
- **`fx_summary.type`**：本功能的"总开关"。类型字符串、默认 None（即关闭）、当前仅落地 csv 一种格式——意味着想要拿到 json/其他格式需后续版本支持（原文未涉及）。
- **`fx_summary.skip_compile`**：决定 FX 收集阶段要不要真的去走 Ascend IR 图编译。默认 True 是为了让"Converter 不全、图模式跑不通"的模型也能完成导出，避免被编译失败截断；False 模式则要求模型本身可正常图执行，是"边跑图边记录"的用法。

---

### 表 2：`fx_summary` 信息（产物样例，逐字还原）

| 目标函数 | 函数类型 | 支持状态 | 调用次数 | 输入统计 | 输出统计 |
| -- | -- | -- | -- | -- | -- |
| `aten.as_strided.default` | aten | 未实现 | 36 | 24次：(`float16(12, 1, 512, 64)`, `[12, 1, 512, 64]`, `[64, 196608, 768, 1]`) 12次：(`float16(12, 1024, 64)`, `[12, 2, 768, 64]`, `[65536, 16384, 64, 1]`) | 24次：`float16(12, 1, 512, 64)` 12次：`float16(12, 2, 768, 64)` |
| `aten.native_layer_norm.default` | aten | 部分支持 | 62 | 62次：(`float16(1, s0, 4096)`, `[4096]`, `float16(4096,)`, `float16(4096,)`, `1e-05`) | 62次：(`float16(1, s0, 4096)`, `float32(1, s0, 1)`, `float32(1, s0, 1)`) |
| `aten.add.Tensor` | aten | 已支持 | 120 | 60次：(`float16(1, s0, 4096)`, `float16(1, s0, 4096)`) 30次：(`float16(1, s0, 16384)`, `1`) 30次：(`float16(1, s0, 16384)`, `1.0`) | 60次：`float16(1, s0, 4096)` 60次：`float16(1, s0, 16384)` |
| `built-in function getitem` | builtin | 已支持 | 62 | 62次：((`float16(1, s0, 4096)`, `float32(1, s0, 1)`, `float32(1, s0, 1)`), `0`) | 62次：`float16(1, s0, 4096)` |

**逐行解读**：

1. **`aten.as_strided.default` / aten / 未实现 / 36**
   - 这是典型的"Converter 未实现"案例：算子在模型里被调用 36 次，分两种 shape pattern（24+12）。一旦模型整体进入图模式，这 36 次调用都会失败，**这条记录直接给出"该算子需进行 Converter 补齐"的清单项**。
   - 输入/输出统计呈现了 shape 不规整的 stride 参数（`[64, 196608, 768, 1]`、`[65536, 16384, 64, 1]`），便于补齐 Converter 时核对 stride 一致性。

2. **`aten.native_layer_norm.default` / aten / 部分支持 / 62**
   - "部分支持"档位：算子 62 次调用全部命中某一种 input pattern（`float16(1, s0, 4096)` + 权重/偏置 + `1e-05` eps），但 Converter 仅在部分场景落地。
   - 输出侧 `float32(1, s0, 1)` 出现两次，对应 mean/rstd——这部分信息是判断"该 pattern 是否落入了已支持分支"的关键线索。

3. **`aten.add.Tensor` / aten / 已支持 / 120**
   - 已支持档位的典型形态：120 次调用拆成 3 种 input pattern（60/30/30），覆盖 add- tensor 与 add- scalar 两种语义（第二参数分别是 `1` 与 `1.0`）。说明 Converter 已能处理这些 shape 与混合 dtype 的组合。
   - 输出侧 `float16(1, s0, 4096)` 与 `float16(1, s0, 16384)` 各 60 次，与输入侧的 60+60 分布一一对应。

4. **`built-in function getitem` / builtin / 已支持 / 62**
   - 注意**函数类型为 builtin 而非 aten**——这是 Python 内置的 `__getitem__`，多用于拆解 layer_norm 的 tuple 输出（输入里能看到完整的 layer_norm 输出 tuple 加索引 `0`）。说明 CSV 并不只统计 ATen 算子，FX 图上所有 target function 都会被纳入，**用户排查"非 ATen 算子是否阻塞入图"时同样依赖此表**。

---

## 【公式解读】

原文无公式（既无 LaTeX 表达式，也无伪代码/数学符号推导）。

---

## 【关联】

1. **与「Converter 补齐」的上下游关系**：文档功能简介段落明确指出——若导出结果中出现「未实现」或「部分支持」的算子，需进行 Converter 补齐，并链接到 `../../../../../CONTRIBUTING.md#converter补齐`。即本功能是 Converter 补齐工作的**前置诊断手段**：先用 fx_summary 把缺口列出来，再去补齐。
2. **与 `torchair.get_npu_backend` 的关系**：所有配置入口都挂在 `get_npu_backend(compiler_config=config)` 的 `compiler_config.debug.fx_summary` 下，链接 `../../api/torchair/get_npu_backend.md`——也就是说，本功能的 API 形态是「`CompilerConfig` 的 debug 子字段」+「`get_npu_backend` 注入到 `torch.compile` 的 backend」，并不独立暴露新接口。
3. **与 Ascend IR 图编译的关系**：`skip_compile` 字段同时指向 Ascend IR 图编译——`True` 即跳过该编译（走 FX Eager）、`False` 即走图编译。两者是「采集 FX 元数据」与「真正生成 Ascend IR 图」的二选一/并行关系，原文限定本功能仅在 GE 图模式场景下生效。
4. **与图模式启用的强约束**：NOTE 段落把 `config.debug.fx_summary.type = "csv"` 与「图模式能否正确启用」直接绑定，提示该调试字段是**临时性诊断开关**，不属于正常生产配置。

---

## 【使用方法】

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 导出图中ATen算子信息和相关配置
config.debug.fx_summary.type = "csv"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

启用要点（原文有）：

- 启用开关：`config.debug.fx_summary.type = "csv"`。
- 编译策略：`config.debug.fx_summary.skip_compile`（bool，默认 `True`）；Converter 不全的模型保持默认即可拿到完整 FX 信息。
- 产物路径：当前执行路径下生成 `summary_${timestamp}.csv`。
- 运行结束后的清理动作：原文 NOTE 强制要求**删除或注释** `config.debug.fx_summary.type = "csv"` 这一行，再正式跑图模式。
- 适用范围：原文限定「仅适用于 GE 图模式场景」。

原文未涉及：CLI 命令行触发方式、其他导出格式（如 json）、与 `torch.compile` 之外的 backend 组合用法、定时/增量导出机制。
