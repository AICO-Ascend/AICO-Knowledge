# 冗余算子消除功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/remove_noop_ops.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/remove_noop_ops.md

# TorchAir 冗余算子消除功能 一体化深度解读

---

## 【定位】

本文档描述 TorchAir 在图模式下集成的**冗余算子消除 (Remove Noop Ops) 优化能力**——自动识别并消除计算图中不影响程序逻辑或数据计算的冗余操作，从而减少不必要的计算开销、提升模型执行效率，并可与其它图优化策略配合通过对比选择最佳方案。

---

## 【技术要点】

1. **图模式自动优化机制**：TorchAir 在图模式下自动扫描计算图，识别出不影响程序逻辑或数据结果的冗余算子节点并消除，无需用户手动改图。

2. **依赖版本要求**：本功能**依赖 PyTorch 2.2.0 或更高版本**，不同 PyTorch 版本所支持的优化场景可能存在差异；文档以 PyTorch 2.5.1 为例列举了受支持算子。

3. **典型冗余操作分类**（原文列举）：
   - 无实际意义的张量视图操作，如 `b=tensor_a[:]`。
   - 参数无效的特殊算子，如重复次数为 1 的 `repeat` 操作。

4. **受支持算子清单**（基于 PyTorch 2.5.1，节选）：包括 `aten.slice`、`aten.slice_scatter`、`aten.repeat`、`aten.constant_pad_nd`、`torch.ops.prims.convert_element_type`、`torch.ops.prims.device_put`、`aten.ceil / floor / round / trunc`、`aten.pow`、`aten.cat`、`aten.view.default`、`aten.view.dtype`、`aten.copy`、`aten.alias`、`aten.clone` 等十余类，每类均给出触发冗余判定的具体场景示例。

5. **非冗余/不执行消除的边界条件**：当算子的输入/输出 Shape 不一致，或优化后在输入/输出之间引入新的别名关系时，**不会进行冗余消除**——确保正确性优先。

6. **默认开启，用户可关闭**：通过 `config.experimental_config.remove_noop_ops` 控制；默认值为 `True`（开启），设为 `False` 即可关闭。

---

## 【关键机制与数据】

- **优化位置与触发时机**（原文）：在图编译阶段（graph mode）进行，作用于 TorchAir 编译得到的 FX 计算图。
- **可观测手段**（原文）：设置成功后，配合 `python_log_print.md` 描述的方式开启 Debug 日志，可在日志中观察到形如下面的提示：

  ```txt
  [DEBUG] TORCHAIR(1675418,python3):2025-10-31 16:13:28.281.364 [npu_fx_compiler.py:297]1675418 After removing noop ops, graph is graph():
      %arg0_1 : [num_users=0] = placeholder[target=arg0_1]
      %arg1_1 : [num_users=1] = placeholder[target=arg1_1]
      %arg2_1 : [num_users=1] = placeholder[target=arg2_1]
      %add_3 : [num_users=1] = call_function[target=torch.ops.aten.add.Tensor](args = (%arg1_1, %arg2_1), kwargs = {})
      return (add_3,)
  ```

  该日志输出来自 `npu_fx_compiler.py:297` 的 `After removing noop ops` 阶段，表明冗余算子消除作为 FX 图流水线上的一独立阶段执行；从 dump 的图内容看，`%arg0_1` 已经没有下游使用者（`num_users=0`），说明原本可能存在的 noop 节点已被移除，只剩下 `add` 这一真正参与计算的算子。

- **默认配置值**（原文）：`remove_noop_ops` 默认为 `True`，即默认启用。

---

## 【表格解读】

**表 A：受支持算子及其冗余判定场景（PyTorch 2.5.1）**——原文逐字还原：

| 算子名 | 冗余操作场景示例 |
|---|---|
| aten.slice | 对整个张量进行完整切片操作，如 tensor_a[:]。 |
| aten.slice_scatter | 对整个张量进行完整切片操作，如 tensor_a.slice_scatter(tensor_b)。 |
| aten.repeat | 张量在所有待重复维度上重复的次数为 1，如 tensor_a.repeat(1)。 |
| aten.constant_pad_nd | 张量在所有待扩充维度上扩充的数量为 0，如 torch.nn.functional.pad(tensor_a, pad=[0, 0, 0, 0], value=3.5)。 |
| torch.ops.prims.convert_element_type | 张量数据类型转换时，前后一致。 |
| torch.ops.prims.device_put | 张量设备类型转换时，前后一致。 |
| aten.ceil、aten.floor、aten.round、aten.trunc | 张量数据类型为整型。 |
| aten.pow | 张量指数运算时幂为 1。 |
| aten.cat | 张量拼接时，参与拼接的张量只有自身，如 torch.cat([tensor_a])。 |
| aten.view.default、aten.view.dtype | - |
| aten.copy、aten.alias、aten.clone | - |

逐行解读：
- **aten.slice / slice_scatter**：当切片范围覆盖整个张量（等价于 identity），整体切片结果与输入相同，可消除。
- **aten.repeat**：当 `repeat` 参数在每个维度上均为 1，结果与输入张量完全相同。
- **aten.constant_pad_nd**：所有待 pad 维度上的 pad 量为 0，输出与输入等价。
- **torch.ops.prims.convert_element_type / device_put**：源 dtype 与目标 dtype 一致、或源 device 与目标 device 一致时，类型/设备转换操作无效。
- **aten.ceil / floor / round / trunc**：针对整型张量，这些数值调整操作不会改变取值，整型是 noop 触发条件。
- **aten.pow**：指数为 1 时，任何底数的 1 次幂等于自身。
- **aten.cat**：拼接列表中只有一个张量，cat 退化为 identity。
- **aten.view.default / view.dtype / copy / alias / clone**：原文未给出具体冗余判定场景示例（用 "-" 占位），仅列入支持列表；这些算子通常在特定组合下（如 view 后 shape 未变化等）被识别为 noop，具体判定以 PyTorch 源码为准。

**表 B：参数说明（表 1）**——原文逐字还原：

| 参数名 | 说明 |
|---|---|
| remove_noop_ops | 图模式中是否开启冗余算子消除，布尔类型。False：关闭。True（默认值）：开启。 |

逐行解读：
- 仅一个开关项 `remove_noop_ops`，类型 `bool`；`True`（默认）即开启冗余算子消除，`False` 即关闭。位于 `experimental_config` 之下，表明该能力目前在实验性配置分组中。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游/调用入口**：[`torchair.get_npu_backend`](../../api/torchair/get_npu_backend.md)：本功能的开关参数最终通过 `get_npu_backend(compiler_config=config)` 传入并下发到 NPU 后端编译流水线，是启用该优化的必经入口。
- **调试可观测性**：[TorchAir Python 层日志打印](python_log_print.md)：开启 Debug 日志后才能看到 "After removing noop ops, graph is graph()" 这一阶段提示，从而验证优化是否生效及消除后的图结构。
- **配置层级**：开关位于 `config.experimental_config.remove_noop_ops` 之下，属于 `CompilerConfig` 的实验性配置分组，与其它图优化策略并列；文档明确指出"当与其它图优化策略结合使用时，可通过优化对比来选择最佳方案"，暗示其与 TorchAir 其它图优化（如算子融合、内存优化等）位于同一流水线的不同阶段。
- **PyTorch 版本耦合**：实际可消除的算子集合由底层 PyTorch FX Pass 提供，因此文档提醒"不同版本支持的优化场景可能存在差异"，与 PyTorch 2.2.0+ 的版本兼容策略相关。

---

## 【使用方法】

原文给出的启用方式（关键代码片段，逐字保留）：

```python
import torch_npu
import torchair
config = torchair.CompilerConfig()
# 冗余算子消除配置
config.experimental_config.remove_noop_ops = True
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

配置项：

| 参数 | 路径 | 取值 | 默认 |
|---|---|---|---|
| remove_noop_ops | `CompilerConfig.experimental_config.remove_noop_ops` | 布尔 | True（开启） |

启用后，配合 `python_log_print.md` 所述方式开启 Debug 日志，可在 `npu_fx_compiler.py` 的 "After removing noop ops" 阶段看到优化后的 FX 图 dump，用于确认优化是否生效。
