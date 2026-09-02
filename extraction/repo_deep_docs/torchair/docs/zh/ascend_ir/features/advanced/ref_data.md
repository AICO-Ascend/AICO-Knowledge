# RefData类型转换功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/ref_data.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/ref_data.md

# RefData类型转换功能 — 一体化深度解读

## 【定位】

这篇文档描述的是 TorchAir 在 GE 图模式下，通过将输入张量从普通 `Data` 类型转换为 `RefData` 引用类型，使 Ref 类算子（Assign、ScatterUpdate 等就地修改类算子）可直接改写输入内存，从而避免重复数据拷贝、提升推理图执行效率的能力与启用方式。

---

## 【技术要点】

1. **作用对象**：Ref 类算子，原文列举为 `Assign`、`ScatterUpdate`，并明确指出"类似于 PyTorch 中的 in-place 类算子"，其特征是会直接改写输入 tensor 的内存内容。
2. **核心机制**：在构图（graph construction）过程中将用户输入的 `Data` 类型转换为 `RefData` 类型，使 Ref 算子能够以引用方式读写输入缓冲区，避免下游再次拷贝。
3. **适用前提**：原文"使用约束"一节明确"本功能仅适用于 GE 图模式场景"。
4. **离线推理场景**：使用 Dynamo 导图功能导出离线图时，RefData 数据类型转换功能"默认已开启"，无需额外配置。
5. **在线推理场景**：通过 `torchair.get_npu_backend` 的 `compiler_config` 进行配置，关键开关为 `config.experimental_config.enable_ref_data = True`，与 `torch.compile(model, backend=npu_backend)` 配合使用。
6. **可观测性**：开启 RefData 转换并启用 Python 层日志后，可通过 `TORCHAIR Replace ... RefData with ... Data in graph ...` 这类 `DEBUG` 级日志确认替换动作已生效。

---

## 【关键机制与数据】

**工作原理（原文还原）**：

- 在大模型推理场景下，当图中存在 Ref 类算子（Assign、ScatterUpdate 等类 in-place 算子）需要改写输入内存时，构图流程会识别输入张量的用途，对"被 Ref 算子以引用方式读写"的输入张量执行一次类型提升：由普通 `Data` 类型提升为 `RefData` 类型。
- 提升为 `RefData` 后，Ref 算子可直接对输入内存进行就地修改（in-place），无需把结果再额外拷贝回输入张量，从而"减少重复数据拷贝，提高模型执行效率"。
- 在线推理流程为：`torch.compile` 触发图编译 → 编译阶段读取 `compiler_config.experimental_config.enable_ref_data` → 若为 `True`，构图过程中执行上述 `Data → RefData` 转换；若为 `False`（默认），不执行该转换。

**数据流示例（原文日志）**：

原文给出的 DEBUG 日志原文：
```
[DEBUG] TORCHAIR 20240607 02:06:15 Replace RefData_5_3_20_20_1200_400_20_1_0_140251860631280:RefData with arg0_1:Data in graph graph_1
```
该日志表明：在 `graph_1` 中，符号 `arg0_1:Data`（普通 Data 类型输入）被替换为 `RefData_5_3_20_20_1200_400_20_1_0_140251860631280:RefData`（带唯一 ID 的 RefData 类型），对应使用示例中 `forward(self, x)` 的输入 `x`。

**性能数据**：原文未提供具体性能数字（如加速比、内存节省量），仅以定性描述"减少重复数据拷贝，提高模型执行效率"说明收益。

---

## 【表格解读】

原文唯一表格为"表 1 参数说明"，逐字还原如下：

| 参数名 | 说明 |
|--|--|
| enable_ref_data | 构图过程中是否将输入数据类型转换为 RefData 类型。<br>False（默认值）：不转换为 RefData 类型。<br>True：转换为 RefData 类型。 |

逐行解读：

- **enable_ref_data**：这是控制 RefData 类型转换功能是否启用的唯一开关。
  - 该参数位于 `CompilerConfig` 之下的 `experimental_config` 子命名空间，即 `config.experimental_config.enable_ref_data`，属于实验性配置项。
  - 默认值为 `False`：保持输入张量为普通 `Data` 类型，Ref 算子按常规方式处理（即可能产生额外的数据拷贝）。
  - 设为 `True` 时：构图过程会主动将相关输入张量标记为 `RefData` 类型，使 Ref 算子能够以引用方式就地修改输入，节省一次拷贝开销。
  - 离线场景下该参数被忽略（因为 Dynamo 导图流程默认开启 RefData 转换）；在线场景下该参数实际生效。

---

## 【公式解读】

原文无公式（既无 LaTeX 公式也无伪代码形式的数学表达式）。

---

## 【关联】

依据文末三个内部链接，可梳理出 RefData 类型转换功能在 TorchAir 体系中的上下游关系：

1. **上游 — Dynamo 导图功能（`dynamo_export.md`）**
   - 适用于**离线推理**场景。
   - 在该流程中 RefData 转换**默认开启**，无需配置 `enable_ref_data`，因此 Dynamo 导图链路可视为 RefData 功能的隐式入口。

2. **上游 — `torchair.get_npu_backend` API（`../../api/torchair/get_npu_backend.md`）**
   - 适用于**在线推理**场景，是 `torch.compile` 接入 NPU 后端的核心接口。
   - RefData 转换开关通过其 `compiler_config` 参数（即 `CompilerConfig`）传入；链接指向该 API 的参数说明，可补充了解 `compiler_config` 的其它可选字段。

3. **配套 — TorchAir Python 层日志打印（`../basic/python_log_print.md`）**
   - 用于在**在线推理**场景中验证 RefData 替换是否实际发生。
   - 原文示例代码中即通过该日志功能打印出 `Replace RefData ... with arg0_1:Data in graph graph_1`，让"是否启用成功"具备可观测性。

---

## 【使用方法】

依据原文整理如下：

**离线推理场景**

- 流程：使用 [Dynamo 导图功能](dynamo_export.md) 导出离线图，再进行后续 AI 应用开发。
- 配置：默认已开启 RefData 数据类型转换功能，无需额外设置 `enable_ref_data`。

**在线推理场景**

- 流程：使用 `torch.compile` 进行图编译，再进行图执行；通过 `torchair.get_npu_backend` 注入 NPU 后端与编译配置。
- 关键配置项（原文"表 1"）：
  - `config.experimental_config.enable_ref_data`：`False`（默认）不转换，`True` 启用 RefData 类型转换。
- 最小化配置示例（原文代码片段，标注"仅供参考不支持直接拷贝运行"）：
  ```python
  import torch_npu
  import torchair
  config = torchair.CompilerConfig()
  # 启用RefData类型的开关
  config.experimental_config.enable_ref_data = True
  npu_backend = torchair.get_npu_backend(compiler_config=config)
  opt_model = torch.compile(model, backend=npu_backend)
  ```
- 可运行示例（原文"使用示例"小节，含 in-place 算子 `x.add_(1)`、设备 `npu:0`、并启用 `fullgraph=True, dynamic=True`）：
  ```python
  import torch
  import torch_npu
  import torchair
  from torch import nn
  from torchair.configs.compiler_config import CompilerConfig

  class Network(nn.Module):
      def __init__(self):
          super(Network, self).__init__()
      def forward(self, x):
          return x.add_(1)

  device = torch.device("npu:0")
  config = CompilerConfig()
  config.experimental_config.enable_ref_data = True
  input0 = torch.ones((3,3), dtype=torch.float32)
  input0 = input0.to(device)
  model = Network()
  npu_backend = torchair.get_npu_backend(compiler_config=config)
  model = torch.compile(model, fullgraph=True, backend=npu_backend, dynamic=True)
  ```
- 验证手段：开启 Python 层日志打印（链接见 `../basic/python_log_print.md`），观察是否出现 `Replace ... RefData with ... Data in graph ...` 的 DEBUG 日志。
