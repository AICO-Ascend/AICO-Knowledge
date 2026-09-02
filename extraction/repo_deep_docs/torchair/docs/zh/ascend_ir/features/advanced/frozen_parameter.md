# 固定权重类输入地址功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/frozen_parameter.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/frozen_parameter.md

# 固定权重类输入地址功能 — 一体化深度解读

## 【定位】
这篇文档解决 TorchAir 在昇腾 NPU GE 图模式下，通过固定 Parameter 类型（权重类）图输入的内存地址不变性，缩短图下发时间、提升下发性能的问题，并给出 `frozen_parameter` 配置项的使用与典型陷阱规避方法。

## 【技术要点】
- **核心适用对象**：`torch.nn.parameter.Parameter` 类型（权重类）的图输入，其内存在推理场景中通常保持不变。
- **作用效果**：开启后缩短图下发时间，提升下发性能。
- **额外适用范围**：对于 PyTorch **v2.6.0 及以上**版本，通过 `torch._dynamo.mark_static_address` 接口标记的内存地址不变的图输入 Tensor（如 LLM 的 `kv_cache`）同样适用。
- **平台/场景约束**：仅适用于 **GE 图模式场景**。
- **典型适用模型**：ChatGPT、LLaMA 等开源大模型。
- **关键陷阱**（特殊场景）：PyTorch 的 `to` 算子转换时会丢失 Parameter 类型，必须先做 NPU 转换、再做 Parameter 包装，否则功能失效。

## 【关键机制与数据】
- **工作原理**（原文）：权重类输入内存地址在推理中保持不变 → 开启 `frozen_parameter` 后图执行复用同一地址 → 减少每次下发时的地址协商/拷贝开销 → 缩短下发时间、提升性能。
- **替代入口**（原文）：PyTorch v2.6.0+ 用户除直接靠 Parameter 类型外，还可通过 `torch._dynamo.mark_static_address` 显式标记静态地址的 Tensor（如 kv_cache）走同等优化路径。
- **失败模式**（原文）：当用户错误地先 `torch.nn.Parameter(...).npu()`（先包 Parameter 再迁设备）时，`to` 算子会丢掉 Parameter 类型标记，`in1` 不再是 Parameter，从而绕过该优化路径。
- **性能数据**：原文未涉及具体数字或对比数据。

## 【表格解读】

**表 1 参数说明**（原文逐字还原）：

|参数名|说明|
|--|--|
|frozen_parameter|图执行时是否固定权重类输入地址。False（默认值）：不固定权重类输入地址。True：固定权重类输入地址。|

逐行解读：
- **`frozen_parameter`**：布尔开关，挂在 `CompilerConfig.experimental_config` 下。取 `False`（默认）时不固定权重类输入地址，每次图下发按常规流程处理；取 `True` 时固定权重类输入地址，复用同一内存地址以压缩下发耗时。该参数与下文「使用方法」中 `config.experimental_config.frozen_parameter = True` 的赋值路径完全对应。

## 【公式解读】
原文无公式。

## 【关联】
- **上游/调用入口**：配置项最终通过 [`torchair.get_npu_backend`](../../api/torchair/get_npu_backend.md) 装配的 NPU backend 生效，使用形如 `torch.compile(model, backend=npu_backend)` 的入口接入 PyTorch 编译栈。
- **配套机制**：与 PyTorch 生态的 `torch.nn.parameter.Parameter` 类型判定、以及 PyTorch v2.6.0+ 的 `torch._dynamo.mark_static_address` 标记形成互补——前者靠类型识别，后者靠显式标记，共同覆盖静态地址 Tensor 的判定面。
- **算子层依赖**：依赖 PyTorch 的 `to` 算子语义（其会剥离 Parameter 类型信息），该约束直接产出了「特殊场景」一节的写法限制。
- **模型适用面**：明确点名 ChatGPT、LLaMA 等开源大模型，暗示该能力与 LLM 推理中大量静态权重 + kv_cache 复用的典型场景强相关。

## 【使用方法】

**基础启用方式**（原文）：
```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 固定权重类输入地址开关
config.experimental_config.frozen_parameter = True
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**关键配置项**：
- `config.experimental_config.frozen_parameter`：布尔值，`False`（默认）/ `True`。

**特殊场景的正确/错误写法**（原文逐字要点）：
- ✅ 正确：`in1 = torch.nn.Parameter(torch.randn(4, 1).float().npu())` —— 先 `.npu()` 转 NPU Tensor，再 `torch.nn.Parameter(...)` 包装，转换后仍是 Parameter。
- ❌ 错误：`in1 = torch.nn.Parameter(torch.randn(4, 1).float()).npu()` —— 先包 Parameter 再迁设备，`to` 算子使 `in1` 不再是 Parameter 类型。

**附加约束**（原文）：仅适用于 **GE 图模式场景**；示例代码注明「仅供参考，不支持直接拷贝运行」。
