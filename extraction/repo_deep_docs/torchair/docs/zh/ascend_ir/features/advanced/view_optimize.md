# View类算子优化功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/view_optimize.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/view_optimize.md

# 一体化深度解读: View类算子优化功能

## 【定位】
本文档描述 TorchAir 在图模式下对多个 View 类算子串接所产生的冗余计算进行自动消除的优化能力, 并给出在该特性与其他图特性共存时的失效约束与配置开关。

## 【技术要点】

1. **优化对象**: 图模式下连续出现的多个 View 类算子; 默认开启以减少冗余计算, 降低计算耗时。
2. **支持的 ATen IR 范围 (原文清单)**: `torch.permute`、`torch.t`、`torch.transpose`、`torch.Tensor.view`、`torch.reshape`; 范围外的 View 类算子不在本文档覆盖的优化范围内。
3. **模式约束**: 仅适用于 GE 图模式场景 (原文: "本功能仅适用于GE图模式场景。")。
4. **互斥约束**: 与以下四项图内特性同时启用时, View 类优化不生效:
   - 图内多流表达 (`multi_stream.md`)
   - 图内设置 AI Core 和 Vector Core 核数 (`limit_cores.md`)
   - 图内算子不超时配置功能 (`op_never_timeout.md`)
   - 指定算子 dump 范围 (`data_dump.md`)
5. **调优建议**: 进行算子调优, 尤其是精度比对时, 建议关闭此功能以避免其对调优结果造成干扰 (原文为 "建议关闭本功能避免影响调优效果")。
6. **配置入口**: 通过 `torchair.get_npu_backend` 的 `compiler_config` 中 `experimental_config.enable_view_optimize` 控制, 默认 `True`(开启)。

## 【关键机制与数据】

- **作用对象与原理 (原文)**: "以TorchAir图方式调用算子时，如果存在多个View类算子，会带来冗余计算，增加计算耗时。默认情况下，TorchAir会开启View类算子优化功能，以提升算子执行性能。"
- **覆盖算子清单 (原文)**: 5 个 ATen IR — `torch.permute`、`torch.t`、`torch.transpose`、`torch.Tensor.view`、`torch.reshape`。
- **失效场景 (原文)**: 仅适用于 GE 图模式; 与 4 项指定的图内特性 (`multi_stream` / `limit_cores` / `op_never_timeout` / `data_dump`) 同时使用时该特性不生效。
- **性能数据**: 原文未给出量化指标 (如加速比、耗时下降百分比、显存变化等), 因此本文档不臆造数字。

## 【表格解读】

**表 1 参数说明** (原文逐字还原):

| 参数名 | 说明 |
| -- | -- |
| enable_view_optimize | 图模式调用View算子时是否开启计算优化。<br>False：关闭优化。<br>True（默认值）：开启优化。 |

逐行解读:

- **参数名 `enable_view_optimize`**: 该参数位于 `experimental_config` 下 (`config.experimental_config.enable_view_optimize`), 是控制本文优化特性是否生效的唯一开关。
- **说明第一句** "图模式调用View算子时是否开启计算优化": 限定生效场景为"图模式调用 View 算子时", 与上文约束"仅适用于 GE 图模式场景"一致。
- **`False` 行**: 显式赋值为 `False` 时关闭优化, 对应"算子调优 / 精度比对场景下建议关闭"的使用建议。
- **`True (默认值)` 行**: 默认值即为开启状态, 表明该优化对最终用户透明, 无需额外配置即可享受收益; 仅在需要排除优化干扰时才需显式赋 `False`。

## 【公式解读】

原文无公式。

## 【关联】

本文档通过以下内部链接与 TorchAir 其他模块/特性形成显式关联:

- [`multi_stream.md`](../multi_stream.md): "图内多流表达"。文档明确指出在启用此特性时, View 类算子优化 **不生效**, 表示两者在图构建/调度层面存在互斥。
- [`limit_cores.md`](../limit_cores.md): "图内设置 AI Core 和 Vector Core 核数"。同上, 与本文特性 **不生效** 共存。
- [`op_never_timeout.md`](../op_never_timeout.md): "图内算子不超时配置功能"。同上, 与本文特性 **不生效** 共存。
- [`data_dump.md`](../data_dump.md): "指定算子 dump 范围"。同上, 与本文特性 **不生效** 共存。
- [`../../api/torchair/get_npu_backend.md`](../../api/torchair/get_npu_backend.md): "torchair.get_npu_backend"。该 API 的 `compiler_config` 是本文优化开关 `enable_view_optimize` 的承载对象, 即本文特性需要经过 `get_npu_backend` 包装后再配合 `torch.compile` 才能在图模式下生效。

可观察到的隐含关系: 本特性与其他 4 个图内特性构成"互斥族"——这 4 项均涉及对图 IR / 算子调度行为做特定改写 (多流、绑核、超时、dump), 改写动作可能与 View 算子的优化通路相互干扰, 因此 TorchAir 选择在同时启用时整体跳过本文优化, 而非尝试叠加。

## 【使用方法】

原文给出明确启用方式 (Python 配置示例):

```python
import torch_npu
import torchair
config = torchair.CompilerConfig()
# View类算子优化配置
config.experimental_config.enable_view_optimize = False
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

操作步骤可归纳为:

1. 构造 `torchair.CompilerConfig()`。
2. 在其 `experimental_config` 子对象上读写 `enable_view_optimize`:
   - `True`(默认): 开启优化, 通常无需显式赋值。
   - `False`: 关闭优化, 用于算子调优 / 精度比对等场景。
3. 将该 `config` 传入 `torchair.get_npu_backend(compiler_config=...)`, 再作为 `backend=` 交给 `torch.compile(model, ...)` 完成图编译。

原文同时声明该示例 "仅供参考不支持直接拷贝运行", 实际接入需结合上层业务模型调整传入的 `model` 等参数。
