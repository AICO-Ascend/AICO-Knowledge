# Symbolic 符号化特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/dynamicshape/symbolic.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/dynamicshape/symbolic.md

# Symbolic 符号化特性深度解读

## 【定位】

这篇文档系统介绍了 PyTorch Ascend 扩展（即 `torch_npu`）Inductor 后端中 **Symbolic（符号化）特性**——即通过 `SymInt`/`SymFloat` 符号变量表示编译时未知的张量维度，从而支持"一次编译、多形状复用"的动态形状编译优化能力，解决运行时输入形状动态变化场景下的重复编译开销与 kernel 自适应问题。

---

## 【技术要点】

1. **核心抽象：SymInt/SymFloat 符号变量**——以符号变量表示编译时未知的维度，使编译器在无具体数值的情况下也能进行图分析与优化。
2. **三种编译模式通过 `dynamic` 参数切换**：`dynamic=False`（静态编译）、`dynamic=True`（符号化编译）、`dynamic=None`（由框架自动判断）。
3. **"一次编译、多种形状复用"机制**：原文示例展示 `(32, 128)` 与 `(64, 256)` 两种不同形状输入可共享同一编译结果，无需重新编译。
4. **与 PyTorch Dynamo 深度集成**：通过 `torch.compile(backend='inductor', dynamic=True)` 透明调用，并支持 `torch._dynamo.export` 导出计算图进行调试。
5. **与 ShapeHandling 形成互补的两种动态形状策略**：Symbolic 走"符号化抽象"路线，ShapeHandling 走"分档映射 + padding/splitting"路线。
6. **典型适用场景**：LLM 推理（BatchSize/SequenceLength 经常变化）、多模态模型（图像分辨率/文本长度变化）、动态批处理与通用推理服务。

---

## 【关键机制与数据】

- **符号变量机制（原文）**：在编译期用 SymInt/SymFloat 代替具体整数维度，运行时根据实际输入形状动态适配 kernel 实现。
- **三模式工作原理（原文）**：
  - `dynamic=False`：编译时确定所有张量形状 → 适用固定形状极致性能场景。
  - `dynamic=True`：使用符号变量表示未知维度 → 允许运行时根据实际形状动态适配。
  - `dynamic=None`：框架自动分析计算图与依赖关系，"对形状敏感的算子自动启用符号化，对形状固定的算子保持静态编译，以平衡灵活性与性能"。
- **形状复用示例（原文测试数据）**：测试形状列表 `[(16, 128), (32, 128), (64, 256), (128, 512)]` 与 `[(16, 32), (32, 32), (64, 32), (128, 32), (256, 32)]` 演示同一 `compiled_fn` 接收多形状输入的复用行为。
- **ShapeHandling 档位配置（原文示例参数）**：`type="BATCHSIZE"`、`dimensions=0`、`min_size=1`、`max_size=256`、`policy="TIMES"`。
- **性能权衡提示（原文）**：符号化编译提高灵活性，但"可能带来一定的运行时开销"；部分复杂模型"可能在符号化编译时遇到问题"。
- **调试入口（原文）**：`torch.compile(..., dynamic=True)` 运行 + `torch._dynamo.export(model_fn)(A, B)` 导出 `graph_module` 并 `print(graph_module.code)` 查看生成图。

---

## 【表格解读】

### 表格 1：动态编译模式对照表（原文逐字还原）

| 模式 | 参数设置 | 特点 | 适用场景 |
|------|----------|------|----------|
| 静态编译 | `dynamic=False` | 编译时确定所有形状 | 形状固定的场景 |
| 符号化编译 | `dynamic=True` | 使用符号变量处理未知形状 | 形状动态变化的场景 |
| 自动模式 | `dynamic=None` | 由框架自动判断 | 不确定形状变化规律的通用场景 |

**逐行解读**：
- **静态编译行**：`dynamic=False` 是 PyTorch `torch.compile` 的默认形式，编译期所有维度已固化，因此能产出最特化的 kernel，但遇到新形状必须重新编译，适用 batch、序列长度、图像分辨率完全不变的推理场景。
- **符号化编译行**：`dynamic=True` 启用 SymInt/SymFloat 抽象，编译产物对维度值不敏感，可被多形状复用，是本文档主角，适用形状真动态、无法枚举全部可能值的场景。
- **自动模式行**：`dynamic=None` 把决策权交给框架，框架会按算子级别混合策略——形状敏感算子符号化、固定算子保持静态，是兼顾灵活性与性能的折中入口，适用迁移、调试、通用服务阶段。

### 表格 2：Symbolic vs ShapeHandling 设计理念对照表（原文逐字还原）

| 特性 | 设计理念 | 核心方法 |
|------|----------|----------|
| **Symbolic** | 符号化抽象 | 使用符号变量表示未知维度，保持编译灵活性 |
| **ShapeHandling** | 分档处理 | 将动态形状映射到固定档位，减少编译开销 |

**逐行解读**：
- **Symbolic 行**：以"符号变量"作为一等公民，编译产物形态与具体数值解耦，优势是复用率上限高、padding/splitting 损耗低，劣势是符号化可能引入运行时 dispatch 开销。
- **ShapeHandling 行**：以"档位（bucket）"为单位做离散化，把动态形状折叠到最近的档位上并辅以 padding/splitting，优势是编译产物数量可控、kernel 特化程度高，劣势是会引入 padding 浪费或精度敏感算子的限制。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档中明确提及的关联模块与上下游关系如下：

- **`torch_npu`（Ascend for PyTorch 适配插件）**：本文档所属的整个能力栈的载体，所有示例都依赖 `import torch_npu`，且张量需放在 `device="npu"` 上执行。
- **PyTorch Dynamo（`torch._dynamo`）**：原文称 Symbolic 与 Dynamo"深度集成，提供透明的编译优化"；调试环节通过 `torch._dynamo.export(model_fn)(A, B)` 导出 `graph_module`，是其直接接口。
- **`torch.compile` 入口**：核心调用形式为 `torch.compile(model_fn, backend='inductor', dynamic=...)`，`backend='inductor'` 显式指定走 Inductor 后端。
- **Inductor 后端**：本文档处于 `torch_npu/_inductor/docs/feature/dynamicshape/symbolic.md` 路径下，是 Ascend Inductor 中动态形状特性族的成员。
- **ShapeHandling 特性**（位于同一路径下：`torch_npu/_inductor/docs/feature/dynamicshape/` 目录）：与 Symbolic 并列的另一种动态形状策略，原文通过"设计理念对照表 + 性能对比代码段"详细说明两者差异与组合用法，并演示了 `enable_shape_handling=True` + `shape_handling_configs` 的混合配置（场景 2 的 `dynamic=True` + ShapeHandling 同时启用）。
- **`options` 参数透传**：`torch.compile(..., options={"enable_shape_handling": True, "shape_handling_configs": [...]})` 显示 Inductor 的编译选项（如 ShapeHandling）是通过 `options` 字典下发的，Symbolic 与 ShapeHandling 通过该字典共存于同一编译过程。
- **典型应用领域**：原文多次提及 LLM 推理（BatchSize/SequenceLength）、多模态模型、动态批处理、通用推理服务，体现其在 Ascend 推理生态中的定位。

---

## 【使用方法】

1. **启用符号化编译（核心入口）**：
   ```python
   import torch
   import torch_npu

   def model_fn(A, B):
       return torch.matmul(A, B)

   compiled_fn = torch.compile(model_fn, backend='inductor', dynamic=True)
   A = torch.randn(32, 64, device="npu")
   B = torch.randn(64, 128, device="npu")
   out = compiled_fn(A, B)
   ```
   关键参数：`backend='inductor'` + `dynamic=True`。

2. **三种模式按场景选择（原文逐字摘录）**：
   - **静态编译**：`torch.compile(model_fn, backend='inductor', dynamic=False)`——适用于"模型推理时输入形状完全固定"、"对性能有极致要求，形状变化不频繁"、"部署环境资源有限，需要最小化运行时开销"、"生产环境的批量推理任务"。
   - **符号化编译**：`torch.compile(model_fn, backend='inductor', dynamic=True)`——适用于"输入形状在运行时动态变化，无法预知所有可能值"、"需要支持真正的运行时形状变化"、"大语言模型推理"、"多模态模型"、"API 服务或在线推理系统"。
   - **自动模式**：`torch.compile(model_fn, backend='inductor', dynamic=None)`——适用于"不确定形状变化规律，希望框架自动处理"、"混合使用场景"、"快速原型开发和实验阶段"、"通用推理服务"、"迁移 PyTorch 模型到 Ascend NPU，希望开箱即用"。

3. **Symbolic 与 ShapeHandling 混合配置（场景 2）**：
   ```python
   model_dynamic_controlled = torch.compile(
       model, backend='inductor', dynamic=True,
       options={
           "enable_shape_handling": True,
           "shape_handling_configs": [{
               "type": "BATCHSIZE",
               "dimensions": 0,
               "min_size": 1,
               "max_size": 256,
               "policy": "TIMES"
           }]
       }
   )
   ```

4. **调试符号化问题（原文示例步骤）**：
   - 步骤 1：定义 `model_fn`（如 `torch.matmul`）。
   - 步骤 2：在 NPU 上准备测试数据 `A = torch.randn((16, 128), device="npu")`、`B = torch.randn((128, 16), device="npu")`。
   - 步骤 3：`compiled_fn = torch.compile(model_fn, backend='inductor', dynamic=True)` 运行并打印 `out.shape`。
   - 步骤 4：`graph_module, _ = torch._dynamo.export(model_fn)(A, B)`，再 `print(graph_module.code)` 查看生成的图代码。

5. **使用建议（原文）**：
   - 开发调试阶段使用 `dynamic=None` 自动模式。
   - 生产环境根据实际形状特征选择合适的固定模式（`True`/`False`）。
   - 可根据模型不同模块的特点混合使用不同编译模式。
   - 需注意"符号化编译虽然提高了灵活性，但可能带来一定的运行时开销"，"部分复杂模型可能在符号化编译时遇到问题，建议进行充分测试"。
