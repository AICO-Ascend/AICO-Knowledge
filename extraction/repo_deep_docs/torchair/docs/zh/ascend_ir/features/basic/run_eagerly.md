# run-eagerly功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/run_eagerly.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/run_eagerly.md

# 深度解读: docs/zh/ascend_ir/features/basic/run_eagerly.md

## 【定位】

这篇文档介绍 TorchAir 中的 **run-eagerly 调试能力** —— 当模型在 GE 图模式下出现执行异常、无法判断问题源（是 TorchAir 的图变换环节还是图执行器）时，提供一种"在 GE 图模式执行之前先用 Eager 模式执行 FX graph"的旁路手段，用于辅助问题定界。

---

## 【技术要点】

1. **问题定界场景定位**：当模型执行出现问题、且无法确定根因来自 TorchAir 图变换操作（IR converter、Cache compile 等）还是图执行器时，可开启 run-eagerly 进行对比定位。
2. **执行模式插桩**：在 GE 图模式执行之前，插入 Eager 模式执行 FX graph 的能力；通过对比"前后执行效果"判断异常来源。
3. **配置开关**：通过 `torchair.get_npu_backend` 的 `compiler_config` 中的 `config.debug.run_eagerly = True` 开启。
4. **互斥约束**：开启后，**GE 图模式相关的功能配置均不生效**（这是关键副作用，必须注意）。
5. **类型与默认值**：参数为布尔类型，默认 `False`（不启用 Eager 模式，以图模式运行）；置 `True` 则启动 Eager 模式运行。
6. **集成路径**：与 `torch.compile(model, backend=npu_backend)` 配合使用，`npu_backend` 由 `torchair.get_npu_backend(compiler_config=config)` 返回。

---

## 【关键机制与数据】

原文提供的工作原理描述：

- **原理定位**（原文）："其可以在 GE 图模式执行之前提供 Eager 模式执行 FX graph 的能力，通过对比模型前后执行效果，辅助问题定界。"
- **数据流方向**：模型 → `torch.compile` → `npu_backend`（携带 `compiler_config.debug.run_eagerly` 配置）→ 先以 Eager 模式跑 FX graph → 再以 GE 图模式执行（若 run_eagerly 关闭时）。
- **约束带来的副作用**（原文）："开启该功能后，GE 图模式相关的功能配置均不生效。"
- **性能数据**：原文未提供任何量化性能数据（如延迟、吞吐对比等）。原文无表格以外的具体数字。

---

## 【表格解读】

原文中有 **表 1 参数说明**，逐字还原如下：

| 参数名 | 参数说明 |
|--|--|
| run_eagerly | 图执行前是否使用Eager模式运行，布尔类型。<br>False（默认值）：不启动Eager模式，以图模式运行。<br>True：启动Eager模式运行。 |

**逐行解读**：

- **参数名（`run_eagerly`）**：这是 debug 命名空间下的一个布尔开关（文档示例中以 `config.debug.run_eagerly` 形式赋值）。
- **参数说明第一句**："图执行前是否使用 Eager 模式运行" —— 明确了它的语义位置：在 GE 图执行之前是否插入一次 Eager 模式运行。
- **类型信息**："布尔类型"，排除字符串/整数等传入方式。
- **`False` 默认值说明**：不启动 Eager 模式，保持图模式运行（即正常路径，不增加调试开销）。
- **`True` 说明**：启动 Eager 模式运行，进入调试/定界模式。
- **隐含语义**：表格未列出的额外提示是文档开头指出的"开启后 GE 图模式相关功能配置均不生效"——这条约束虽不在表内，但属于使用该参数时必须连带考虑的前提。

原文无其他表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文档末尾及正文给出的内部链接，存在以下上下游关系：

1. **API 入口**：[`../../api/torchair/get_npu_backend.md`](../../api/torchair/get_npu_backend.md)
   - run-eagerly 必须通过 `torchair.get_npu_backend` 的 `compiler_config` 注入，因此该 API 文档是参数通道、签名、默认行为的权威说明。
   - 这是 run-eagerly 能力的"配置入口上游"。

2. **示例与场景参考**：[`../../../appendix/cases/performance_cases.md#性能分析案例`](../../../appendix/cases/performance_cases.md#性能分析案例)
   - 文档明确写"完整示例可参考性能分析案例"，意味着该案例文档承载了 run-eagerly 的端到端可运行/可参考写法。
   - 这是 run-eagerly 能力在"性能问题排查"场景下的下游范例。

3. **被互斥影响的模块**（原文文字隐含，未给出独立链接）：
   - **GE 图模式相关功能配置**：开启 run-eagerly 后该类配置全部失效。这说明 run-eagerly 与 GE 图执行链路是"互斥或前置阻断"的关系，而非叠加关系。
   - **图变换链路（IR converter、Cache compile 等）**：被列为 run-eagerly 试图区分的"问题源之一"，因此文档语义上把 run-eagerly 与图变换链路放在对比/定界的两极。

4. **集成调用栈**：
   `torch.compile(model, backend=npu_backend)` ← `npu_backend = torchair.get_npu_backend(compiler_config=config)` ← `config.debug.run_eagerly = True`
   即 run-eagerly 通过 `CompilerConfig` → `get_npu_backend` → `torch.compile` 三级链路生效。

---

## 【使用方法】

原文给出的启用方式（**仅供参考、不支持直接拷贝运行**）：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
config.debug.run_eagerly = True
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

配置项与命令要点：

- **类与命名空间**：`torchair.CompilerConfig()` 实例化 → 写入 `config.debug.run_eagerly`（即 `debug` 子命名空间下的 `run_eagerly` 字段）。
- **取值**：`True` / `False`（布尔），默认 `False`。
- **注入点**：作为 `compiler_config` 参数传入 `torchair.get_npu_backend`。
- **最终生效**：将返回的 `npu_backend` 作为 `torch.compile` 的 `backend` 参数使用。
- **附加约束**：开启后，GE 图模式相关功能配置全部失效，需评估是否影响其他能力的同时启用。
- **完整示例入口**：见 [`性能分析案例`](../../../appendix/cases/performance_cases.md#性能分析案例)。
- **未涉及**：原文中未给出环境变量方式、未给出 CLI 方式、未给出关闭/回滚的显式命令（关闭方式即把 `run_eagerly` 重新置为 `False` 或不设置，走默认值路径）。
