# 单流执行功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/single_stream.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/single_stream.md

# 深度解读：「单流执行功能」

## 【定位】

本篇文档描述 TorchAir 在静态 Shape 场景下支持用户在图执行过程中开启「单 Stream 执行」的优化能力，主要用于解决多 Stream 模型因流间切换带来额外计算耗时、导致图执行性能下降的问题。

## 【技术要点】

- **适用前提**：仅适用于 **静态 Shape 场景**，且仅适用于 **GE 图模式**（原文："本功能仅适用于GE图模式场景"）。
- **默认行为**：默认 **不开启** 单流模式（默认 `enable_single_stream=False`）。
- **核心机制**：图执行过程中通过 `compiler_config` 中的 `ge_config.enable_single_stream` 控制是否将图执行收敛到单一 Stream 上，借此避免流间切换开销。
- **互斥约束一**：`enable_single_stream=True` 与 `torch_npu.npu_prefetch` 接口 **不能同时使用**（"不支持同时开启本功能，否则影响算子正常执行"）。
- **互斥约束二**：当通信算法的编排展开位置在 Device 侧 **AI Vector Core** 计算单元时（通过 `export HCCL_OP_EXPANSION_MODE="AIV"` 配置）， **不能同时开启** 本功能。
- **触发场景定位**：对于 "没有实际并发效果" 且采用多 Stream 执行的模型，开启单 Stream 可提升图执行性能。

## 【关键机制与数据】

- **Stream 的作用**（原文）："Stream一般用于维护一些异步操作的执行顺序，确保按照应用程序中的代码调用顺序在Device上执行。" 即 Stream 是 Device 上异步操作的有序执行通道。
- **性能影响的根因**（原文）："由于流间切换导致额外的计算耗时，影响性能" — 即多 Stream 模型若没有真实并发收益，则 Stream 切换本身成为纯开销。
- **AI Vector Core 通信展开的环境变量**（原文）：
  ```bash
  export HCCL_OP_EXPANSION_MODE="AIV"
  ```
  当通信算子以 AIV 模式展开在 Device 侧的 AI Vector Core 上时，与单流模式存在不兼容性。
- 原文未提供具体的性能数字（如加速比、benchmark 数据等），性能收益以定性描述方式给出（"提高图执行性能"）。

## 【表格解读】

原文包含 **1 个表格**：「表 1 参数说明」，逐字还原如下：

|参数名|说明|
|--|--|
|enable_single_stream|图执行时是否开启单流模式。False（默认值）：不开启单流模式。True：开启单流模式。|

**逐行解读**：

- **参数名 `enable_single_stream`**：该参数挂在 `config.ge_config` 之下（详见代码示例），用于控制图执行是否采用单 Stream 模式。
- **取值 `False`（默认值）**：维持原有多 Stream 执行模式，不启优化。
- **取值 `True`**：开启单 Stream 模式，按需减少流间切换开销，但需注意与 `npu_prefetch`、`HCCL_OP_EXPANSION_MODE=AIV` 的互斥关系。

## 【公式解读】

原文无公式。

## 【关联】

- **配置入口依赖**：`enable_single_stream` 通过 [`torchair.get_npu_backend`](../../api/torchair/get_npu_backend.md) 提供的 `compiler_config` 传入，说明该特性是 `CompilerConfig` / `ge_config` 配置体系的一部分，与 TorchAir 的图编译/后端绑定流程紧密耦合。
- **运行环境依赖**：
  - 与 **GE 图模式** 强绑定（仅 GE 图模式可用）。
  - 与 **静态 Shape** 场景绑定（动态 Shape 下未提及支持）。
- **互斥特性**：
  - 与 `torch_npu.npu_prefetch`（自定义 API）互斥。
  - 与 HCCL AIV 通信展开模式（`HCCL_OP_EXPANSION_MODE="AIV"`）互斥。
- 内部链接指向：`../../api/torchair/get_npu_backend.md`（即 `torchair.get_npu_backend` API 参考）。

## 【使用方法】

启用方式（原文给出示例代码）：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 开启图单流执行功能
config.ge_config.enable_single_stream = True
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**配置项**：`config.ge_config.enable_single_stream`，布尔值，**默认 `False`**，置为 `True` 即开启单流执行模式。

**前置条件 / 启用限制**：

- 仅适用于 **GE 图模式** 场景。
- 仅适用于 **静态 Shape** 场景。
- 不能与 `torch_npu.npu_prefetch` 同时使用。
- 不能与 `HCCL_OP_EXPANSION_MODE="AIV"` 的通信编排方式同时使用。

> 注：原文示例明确标注 "**仅供参考不支持直接拷贝运行**"，正式使用时需结合实际模型与上层 `torch.compile` 调用流程。
