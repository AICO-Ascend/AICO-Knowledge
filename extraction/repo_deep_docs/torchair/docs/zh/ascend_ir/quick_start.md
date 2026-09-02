# GE图模式快速上手

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/quick_start.md

# GE图模式快速上手 — 一体化深度解读

---

## 【定位】

本文档是 TorchAir（基于 PyTorch + torch_npu 在昇腾 NPU 上使用图模式推理）的「GE 图模式」快速入门指南，描述**如何通过 `CompilerConfig` 开启默认 `mode="max-autotune"` 模式，将 FX 图转换为 Ascend IR 图，并通过 GE 图引擎完成图编译与执行**的全套最小化脚本骨架，并给出后续章节各功能项的总入口索引。

---

## 【技术要点】

1. **默认模式与开启方式**：GE 图模式通过 `torchair.CompilerConfig` 的 **`mode="max-autotune"`** 开启（系统默认模式）；FX 图 → Ascend IR 图的转换与 GE 图引擎的图编译/执行均在该模式下完成。
2. **导包顺序硬约束**：必须**先 import `torch_npu`，再 import `torchair`**；同时可选 `from torchair import patch_for_hcom; patch_for_hcom()` 以「Patch 方式」实现集合通信（hcom）入图。
3. **`.npu()` 设备迁移**：自定义 `Model` 必须调用 `.npu()` 将参数迁移到 NPU（如 `Model().npu()`），否则图执行前的 tensor 与模型不在同一后端。
4. **后端获取与绑定**：`npu_backend = torchair.get_npu_backend(compiler_config=config)` 是将 TorchAir 后端与 `CompilerConfig` 绑定的入口；再通过 `torch.compile(model, backend=npu_backend)` 完成 compile。
5. **`torch.compile` 原型签名（PyTorch 官方）**：`torch.compile(model=None, *, fullgraph=False, dynamic=None, backend='inductor', mode=None, options=None, disable=False)` —— 在 Ascend IR 模式下 `backend`、`mode`、`options` 的语义与原生语义存在差异（见【表格解读】表 1）。
6. **功能项分类总览**：`CompilerConfig` 下分为 `debug / export / dump_config / fusion_config / experimental_config / inference_config / ge_config` 七大类，每类下挂载若干子功能（见【表格解读】表 2）。

---

## 【关键机制与数据】

### 工作原理与数据流

原文给出的完整链路为：

> **FX 图** → （由 `torchair.get_npu_backend(compiler_config=config)` 接入） → **Ascend IR 图** → **GE 图引擎** 完成图编译与执行

### 启用入口（原文代码片段要点）

| 步骤 | 关键调用（原文） | 作用 |
|---|---|---|
| 1 | `import torch_npu` 再 `import torchair` | 导包顺序约束 |
| 2 | `patch_for_hcom()`（可选） | Patch 方式实现集合通信入图 |
| 3 | `Model().npu()` | 将自定义模型迁移到 NPU |
| 4 | `torchair.CompilerConfig()` | 创建编译配置（默认 `mode="max-autotune"`） |
| 5 | `torchair.get_npu_backend(compiler_config=config)` | 获取 TorchAir 自定义 backend |
| 6 | `torch.compile(model, backend=npu_backend)` | 基于 TorchAir backend 编译模型 |
| 7 | `opt_model(x, y)` 执行编译后 Model | 触发图编译与执行 |

### 性能/数量数据

- 原文**未提供**任何性能数字（无 ms、吞吐、加速比等）。
- 原文给出的可量化参数仅为：`torch.compile` 签名中各参数的缺省值（见【表格解读】表 1）。

---

## 【表格解读】

### 表 1：torch.compile 参数说明（Ascend IR 模式）

|参数名|PyTorch 原生参数说明|Ascend IR 模式下参数说明|
|---|---|---|
|model|**必选参数**。入图部分的模型或者函数。|与原生含义一致。|
|fullgraph|可选参数，bool 类型。是否捕获整图进行优化。<br>False（缺省值）：非整图优化。<br>True：捕获整图优化。|与原生含义一致。|
|dynamic|可选参数，bool 类型或 None。是否启用动态 Shape 追踪。<br>None（缺省值）：自动检测是否启用动态 Shape 追踪。<br>False：不启用动态 Shape 追踪。<br>True：启用动态 Shape 追踪。|与原生含义一致。|
|backend|**必选参数**，后端选择，缺省值为 "inductor"。|如需使用 TorchAir 提供的后端，需通过 `torchair.get_npu_backend` 获取并显式传入。通过 **compiler_config 参数**配置图模式功能，支持的功能项参见表 2。|
|mode|开销模式，内存开销模式选择，缺省值为 None。|昇腾 NPU **暂不支持**。|
|options|优化选项，缺省值为 None。|昇腾 NPU **暂不支持**。|
|disable|可选参数，bool 类型。是否关闭 torch.compile 能力。<br>False（缺省值）：开启 torch.compile 能力。<br>True：关闭 torch.compile 能力，采用单算子模式。|与原生含义一致。|

**逐行解读**：
- **model / fullgraph / dynamic / disable**：在 Ascend IR 模式下含义与 PyTorch 原生完全一致，开发者可按 PyTorch 官方语义使用，无须特殊适配。
- **backend**：是 Ascend IR 模式下唯一**必须显式配置**的参数 —— 原生缺省值 `"inductor"` 在昇腾 NPU 上不能直接使用，必须用 `torchair.get_npu_backend(compiler_config=config)` 显式替换；该参数也是 `CompilerConfig` 各功能项（表 2）的承载入口。
- **mode 与 options**：Ascend IR 模式下**暂不支持**，即调用 `torch.compile(..., mode=...)` 或 `options=...` 在昇腾 NPU 上不会生效，需用 `CompilerConfig` 内部对应功能项替代（参见表 2）。
- **disable=True**：退化为单算子模式（即 Eager 模式），是图模式无法使用时的降级开关。

---

### 表 2：CompilerConfig 功能项

|分类|说明|功能项|
|---|---|---|
|debug|配置 debug 调试类功能，配置形式为 `config.debug.xxx`。|[图结构 dump 功能](./features/basic/graph_dump.md)<br>[算子 data-dump 功能（Eager 模式）](./features/basic/data_dump_eager.md)<br>[run-eagerly 功能](./features/basic/run_eagerly.md)<br>[算子 Converter 支持度导出功能](./features/advanced/converter_export.md)<br>[多流并发死锁检测功能](./features/basic/deadlock_check.md)|
|export|配置离线导图相关功能，配置形式为 `config.export.xxx`。|[Dynamo 导图功能](./features/advanced/dynamo_export.md)|
|dump_config|配置图模式下 dump 功能，配置形式为 `config.dump_config.xxx`。|[算子 data-dump 功能（Ascend-IR）](./features/advanced/data_dump.md)|
|fusion_config|配置图融合相关功能，配置形式为 `config.fusion_config.xxx`。|[算子融合规则配置功能（fusion_switch_file）](./features/advanced/fusion_switch_file.md)|
|experimental_config|配置各种试验功能，配置形式为 `config.experimental_config.xxx`。|[冗余算子消除功能（Ascend-IR）](./features/basic/remove_noop_ops.md)<br>[FX 图算子融合 Pass 配置功能 Ascend-IR](./features/basic/pattern_fusion_pass.md)<br>[固定权重类输入地址功能（Ascend-IR）](./features/advanced/frozen_parameter.md)<br>[图模式编译节点遍历选项](./features/advanced/topology_sorting_strategy.md)<br>[计算与通信并行功能](./features/advanced/cc_parallel.md)<br>[算子在线编译选项](./features/advanced/jit_compile.md)<br>[RefData 类型转换功能](./features/advanced/ref_data.md)<br>[Tiling 调度优化功能](./features/advanced/tiling_schedule_optimize.md)<br>[View 类算子优化功能](./features/advanced/view_optimize.md)<br>[动静子图拆分场景性能优化](./features/advanced/static_model_ops_lower_limit.md)|
|inference_config|配置推理相关功能，配置形式为 `config.inference_config.xxx`。|[动态 shape 图分档执行功能](./features/advanced/dynamic_gears_merge_policy.md)|
|ge_config|配置 GE 图引擎提供的功能，配置形式为 `config.ge_config.xxx`。|[图编译统计信息导出功能](./features/advanced/export_compile_stat.md)<br>[单流执行功能](./features/advanced/single_stream.md)<br>[图编译多级优化选项](./features/advanced/oo_level.md)<br>[算子融合规则配置功能（optimization_switch）](./features/advanced/optimization_switch.md)<br>[AI-Core 和 Vector-Core 限核功能（Ascend-IR）](./features/advanced/limit_cores.md)<br>[多流并行模式配置功能](./features/advanced/multistream_parallel_mode.md)|

**逐行解读**：
- **debug 类**：定位为「调试类功能集合」，覆盖图结构可视化、Eager 模式下算子 data-dump、run-eagerly（跳过图编译逐算子运行，便于调试）、Converter 算子支持度导出、多流并发死锁检测 —— 主要服务于开发期问题定位。
- **export 类**：仅一项 `Dynamo 导图功能`，用于离线导出 GE 图（不立即执行），适合做模型交付物或预编译产物。
- **dump_config 类**：与 `debug` 下 Eager 模式的 data-dump 对偶，本类专门服务于 Ascend-IR 图模式下的算子 data-dump。
- **fusion_config 类**：通过 `fusion_switch_file` 自定义算子融合规则，是图编译期算子融合策略的开关。
- **experimental_config 类**：功能项最多（共 10 项），覆盖冗余算子消除、FX 图算子融合 Pass、固定权重地址、编译节点遍历、计算通信并行、JIT 在线编译、RefData 转换、Tiling 调度、View 优化、动静子图拆分 —— 多数为试验性或深度调优选项。
- **inference_config 类**：仅有「动态 shape 图分档执行」一项，针对动态 shape 场景做图分档执行（gear）。
- **ge_config 类**：直连 GE 图引擎原生能力，包含编译统计导出、单流执行、多级优化（OO）、optimization_switch 融合规则、AI-Core/Vector-Core 限核、多流并行模式 —— 是与底层 GE 引擎交互的最深一层配置。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档是 TorchAir「GE 图模式」的**入口与索引页**，与文中其他特性的关联分为四层：

### 1. 图执行主链路（核心闭环）
- 文档定义的最小脚本骨架本身即「图模式总入口」，所有后续章节功能（如 dump、fusion、调试）都通过 `CompilerConfig` 的不同分类挂载其上。
- **`backend=npu_backend`** 决定了后续所有 `config.*` 子项（表 2）的生效位置。

### 2. 调试与可观测性（debug / dump_config 类）
- [图结构 dump](./features/basic/graph_dump.md)：可视化整图结构
- [算子 data-dump（Eager）](./features/basic/data_dump_eager.md) 与 [算子 data-dump（Ascend-IR）](./features/advanced/data_dump.md)：分别覆盖 Eager 与图模式下的算子输入/输出数据导出
- [run-eagerly](./features/basic/run_eagerly.md)：跳过图编译逐算子运行，定位算子级错误
- [多流并发死锁检测](./features/basic/deadlock_check.md)：覆盖多流场景死锁排查

### 3. 导图与离线产物（export / fusion 类）
- [Dynamo 导图](./features/advanced/dynamo_export.md)：离线导出图模型
- [Converter 支持度导出](./features/advanced/converter_export.md)：导出当前算子 Converter 支持矩阵
- [fusion_switch_file](./features/advanced/fusion_switch_file.md) 与 [optimization_switch](./features/advanced/optimization_switch.md)：两套算子融合规则配置入口（前者位于 `fusion_config` 下，后者位于 `ge_config` 下）

### 4. 深度调优（experimental / ge / inference 类）
- [冗余算子消除](./features/basic/remove_noop_ops.md) / [FX 图算子融合 Pass](./features/basic/pattern_fusion_pass.md)：图编译期图优化
- [固定权重类输入地址](./features/advanced/frozen_parameter.md) / [RefData 类型转换](./features/advanced/ref_data.md) / [View 算子优化](./features/advanced/view_optimize.md)：地址与中间表示层优化
- [计算与通信并行](./features/advanced/cc_parallel.md) / [多流并行模式](./features/advanced/multistream_parallel_mode.md) / [单流执行](./features/advanced/single_stream.md)：并行执行策略三件套
- [图编译多级优化选项（OO）](./features/advanced/oo_level.md) / [算子在线编译（JIT）](./features/advanced/jit_compile.md)：编译期策略
- [AI-Core 和 Vector-Core 限核](./features/advanced/limit_cores.md) / [Tiling 调度优化](./features/advanced/tiling_schedule_optimize.md) / [动静子图拆分性能优化](./features/advanced/static_model_ops_lower_limit.md)：硬件亲和优化
- [图模式编译节点遍历](./features/advanced/topology_sorting_strategy.md) / [图编译统计信息导出](./features/advanced/export_compile_stat.md)：编译过程控制与可观测性
- [动态 shape 图分档执行](./features/advanced/dynamic_gears_merge_policy.md)：与 `torch.compile(dynamic=...)` 配套使用的动态 shape 策略

> **补充**：表 2 中部分链接（`frozen_parameter.md`、`topology_sorting_strategy.md`、`cc_parallel.md`、`jit_compile.md`、`ref_data.md`、`tiling_schedule_optimize.md`、`view_optimize.md`、`static_model_ops_lower_limit.md`、`dynamic_gears_merge_policy.md`、`export_compile_stat.md`、`single_stream.md`、`oo_level.md`、`optimization_switch.md`、`limit_cores.md`、`multistream_parallel_mode.md`）未出现在题目提供的「内部链接」清单中，但原文表格中确有指向 —— 本文据实保留。

---

## 【使用方法】

### 最小化脚本骨架（原文示例，逐字保留）

```python
# 导包（必须先导 torch_npu 再导 torchair）
import torch
import torch_npu
import torchair

# Patch 方式实现集合通信入图（可选）
from torchair import patch_for_hcom
patch_for_hcom()

# 自定义 Model
class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x, y):
        return torch.add(x, y)

model = Model().npu()
# 图执行模式默认为 max-autotune
config = torchair.CompilerConfig()
npu_backend = torchair.get_npu_backend(compiler_config=config)

# 基于 TorchAir backend 进行 compile
opt_model = torch.compile(model, backend=npu_backend)

# 执行编译后的 Model
x = torch.randn(2, 2).npu()
y = torch.randn(2, 2).npu()
opt_model(x, y)
```

### 关键配置项（汇总自表 1 与表 2）

- **默认模式开关**：`torchair.CompilerConfig()` 即默认 `mode="max-autotune"`，无须额外参数即开启 GE 图模式。
- **`backend` 绑定**：`torch.compile(model, backend=torchair.get_npu_backend(compiler_config=config))` —— 必选且缺省值 "inductor" 在昇腾 NPU 上不适用。
- **`fullgraph`**：可选 bool，决定是否捕获整图优化（缺省 `False`）。
- **`dynamic`**：可选 bool / `None`，决定是否启用动态 Shape 追踪（缺省 `None` 自动检测）。
- **`disable`**：可选 bool，`True` 时关闭图模式退化为单算子（Eager）模式。
- **`config.debug.xxx`**：调试类（graph_dump、data_dump_eager、run_eagerly、converter_export、deadlock_check）。
- **`config.export.xxx`**：离线导图类（dynamo_export）。
- **`config.dump_config.xxx`**：Ascend-IR 图模式 data-dump（data_dump）。
- **`config.fusion_config.xxx`**：算子融合规则（fusion_switch_file）。
- **`config.experimental_config.xxx`**：试验性调优（remove_noop_ops、pattern_fusion_pass、frozen_parameter、topology_sorting_strategy、cc_parallel、jit_compile、ref_data、tiling_schedule_optimize、view_optimize、static_model_ops_lower_limit）。
- **`config.inference_config.xxx`**：推理相关（dynamic_gears_merge_policy）。
- **`config.ge_config.xxx`**：GE 引擎原生能力（export_compile_stat、single_stream、oo_level、optimization_switch、limit_cores、multistream_parallel_mode）。

### 不支持的参数
- `torch.compile` 的 **`mode`** 与 **`options`** 参数在昇腾 NPU 上**暂不支持**（原文表述）。

### 注意事项
- 文档明确声明「本章将提供 GE 图模式功能配置的快速上手示例，**仅供参考**。请根据实际情况自行修改脚本」，即示例不是生产级模板，使用时需自行替换 `Model` 定义与输入规模。
