# 快速入门

> 仓 `pytorch` · 路径 `docs/zh/user_guide/torch_compile/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docs/zh/user_guide/torch_compile/quick_start.md

# 「torch.compile 快速入门」一体化深度解读

---

## 【定位】

本文档是「Ascend for PyTorch」/`TorchNPU` 中 `torch.compile` 用户指南的入门篇，用三段递进的代码示例（逐点算子 → ResNet-50 → BERT/ResNeXt 预训练模型）演示如何在 NPU 上启用 `torch.compile` 与 `inductor` 后端，并通过环境变量查看自动生成的 Triton kernel，直观理解算子融合与 NPU Graph 带来的性能收益。

---

## 【技术要点】

1. **基本调用范式**：`torch.compile(fn, backend="inductor")` 返回一个包装后的可调用对象；示例中使用 `new_fn(input_tensor)` 触发即时编译与执行。硬件默认绑定 `device="npu:0"`，无 NPU 时可去掉 `.to(device="npu:0")` 退化到 CPU。
2. **逐点算子的融合收益**（原文核心数字）：对 `torch.cos → torch.sin` 链路，融合把 **2 次读（`x`、`a`）+ 2 次写（`a`、`b`）** 缩减为 **1 次读（`x`）+ 1 次写（`b`）**；该优化在以**内存带宽**为瓶颈的较新 NPU 上尤为关键。
3. **Inductor 的 NPU Graph 自动支持**：在编译过程中自动启用 NPU Graph，消除 Python 端逐 kernel 启动开销，同样针对较新 NPU 设计。
4. **调试入口**：`TORCH_COMPILE_DEBUG=1 python example.py` 会在终端输出 `DEBUG` 消息，并在日志末尾给出包含 `torchinductor_<your_username>` 文件夹的目录路径；其中 `output_code.py` 即为生成的 Triton kernel 源。
5. **后端枚举**：在 REPL 中运行 `torch.compiler.list_backends()` 可列出全部可用后端；文中点名 `inductor` 与 `npugraphs` 两种可试。
6. **Triton kernel 形状参数**（原文示例内）：生成的 `@pointwise` 装饰器携带 `size_hints=[16384]`、`triton_meta.signature` 中的 `in_ptr0/ out_ptr0` 均为 `*fp32`，`xnumel` 为 `i32`，`divisible_by_16=(0, 1, 2)`，并在 kernel 内显式 `xnumel = 10000`，对应原始输入张量长度。

---

## 【关键机制与数据】

- **数据流（cos→sin 示例）**：Python 函数 `fn(x)` 经 `torch.compile(..., backend="inductor")` 包装后，由 **TorchDynamo** 做图捕获，由 **TorchInductor** 把捕获到的 FX 图 lower 成单个 Triton `@pointwise` JIT kernel；kernel 内 `tl.load(in_ptr0 + x0)` → `tl.cos` → `tl.sin` → `tl.store(out_ptr0 + x0, ...)`，`cos` 中间结果 `tmp1` 仅驻留在寄存器，不再写回全局内存——这是融合落地的直接证据。原文：`"cos和sin操作位于同一个Triton kernel中，并且临时变量保存在访问速度极快的寄存器中"`。
- **融合前/后 I/O 计数**（原文）：读 `2→1`，写 `2→1`；张量长度示例为 `10000`。
- **后端链路**：TorchDynamo 负责捕获、TorchInductor 负责生成 Triton kernel；Inductor 同时自动注入 NPU Graph 支持。
- **预训练模型链路**：Hugging Face `BertTokenizer` + `BertModel('bert-base-uncased')`、TIMM `timm.create_model('resnext101_32x8d', ...)`，均只需在加载后追加一行 `model = torch.compile(model, backend="inductor")`；去掉 `.to(device="npu:0")` 后 Triton 会回退为可在 CPU 上运行的 C++ kernel（原文）。
- **可调度的可用后端**：通过 `torch.compiler.list_backends()` 查询；文中建议尝试 `npugraphs`。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无独立数学公式。但文档内含一段 **Triton kernel 伪代码**，逐字保留如下并逐元素解释：

```python
@pointwise(size_hints=[16384], filename=__file__, triton_meta={'signature': {'in_ptr0': '*fp32', 'out_ptr0': '*fp32', 'xnumel': 'i32'}, 'device': 0, 'constants': {}, 'mutated_arg_names': [], 'configs': [AttrsDescriptor(divisible_by_16=(0, 1, 2), equal_to_1=())]})
@triton.jit
def triton_(in_ptr0, out_ptr0, xnumel, XBLOCK : tl.constexpr):
   xnumel = 10000
   xoffset = tl.program_id(0) * XBLOCK
   xindex = xoffset + tl.arange(0, XBLOCK)[:]
   xmask = xindex < xnumel
   x0 = xindex
   tmp0 = tl.load(in_ptr0 + (x0), xmask, other=0.0)
   tmp1 = tl.cos(tmp0)
   tmp2 = tl.sin(tmp1)
   tl.store(out_ptr0 + (x0 + tl.zeros([XBLOCK], tl.int32)), tmp2, xmask)
```

符号与作用：

| 符号 | 含义 |
|---|---|
| `@pointwise(size_hints=[16384], …)` | Inductor 的逐点算子装饰器；`size_hints` 给编译器提示向量化规模 |
| `triton_meta.signature` | kernel 签名：`in_ptr0`/`out_ptr0` 为 `fp32` 指针，`xnumel` 为 `i32` |
| `device: 0` | 目标设备编号（对应 `npu:0`） |
| `divisible_by_16=(0,1,2)` | 提示 Inductor 形参 0/1/2 均可被 16 整除，可触发向量化访存 |
| `@triton.jit` | Triton 即时编译入口 |
| `XBLOCK : tl.constexpr` | 编译期块大小常量 |
| `xnumel = 10000` | 与 Python 侧 `torch.randn(10000)` 对齐的元素总数 |
| `tl.program_id(0)` | 当前 program（grid）在第 0 维的索引 |
| `tl.arange(0, XBLOCK)[:]` | 生成块内偏移向量 |
| `xmask = xindex < xnumel` | 边界掩码，屏蔽越界元素 |
| `tl.load(..., xmask, other=0.0)` | 条件加载，越界位读 0.0 |
| `tmp1 = tl.cos(tmp0)` / `tmp2 = tl.sin(tmp1)` | 融合算子链，`tmp1` 仅在寄存器 |
| `tl.store(out_ptr0 + (x0 + tl.zeros([XBLOCK], tl.int32)), tmp2, xmask)` | 按索引回写结果并保持 `xmask` 边界 |

---

## 【关联】

- **上游入口**：文档开头要求先阅读 [torch.compiler](./_menu_torch_compile.md)（即 `docs/zh/user_guide/torch_compile/_menu_torch_compile.md`），作为本指南的菜单/索引页。
- **下游延伸**（文末「后续步骤」指向）：
  - [用于训练的 torch.compile 教程](https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html)
  - [torch.compiler API 参考](https://docs.pytorch.org/docs/2.13/torch.compiler_api.html)
  - [用于细粒度追踪的 TorchDynamo API](https://docs.pytorch.org/docs/2.13/user_guide/torch_compiler/torch.compiler_fine_grain_apis.html)
- **横向模块依赖**：TorchDynamo（图捕获）→ TorchInductor（生成 Triton kernel）→ NPU Graph（自动注入）；后端枚举由 `torch.compiler.list_backends()` 提供；`npugraphs` 作为另一可选后端在文中被点名。
- **预训练模型生态**：Hugging Face Transformers（`BertTokenizer`/`BertModel`）、TIMM（`timm.create_model`）、`torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)` 均被列为开箱即用目标。

---

## 【使用方法】

- **启用编译**（推理场景）：
  ```python
  opt_model = torch.compile(model, backend="inductor")
  ```
  也可直接作用于函数：`torch.compile(fn, backend="inductor")`。
- **设备绑定**（NPU）：
  ```python
  torch.randn(10000).to(device="npu:0")
  # 或对模型
  BertModel.from_pretrained("bert-base-uncased").to(device="npu:0")
  ```
  无 NPU 时去掉 `.to(device="npu:0")`，可退化到 CPU 运行（Triton 将生成 C++ kernel）。
- **查看生成代码**：
  ```bash
  TORCH_COMPILE_DEBUG=1 python example.py
  ```
  在终端 `DEBUG` 日志末尾定位 `torchinductor_<your_username>` 目录，打开其中的 `output_code.py` 查看 Triton kernel。
- **查询可用后端**（REPL）：
  ```python
  torch.compiler.list_backends()
  ```
  文中建议在 `inductor` 之外尝试 `npugraphs`。
- **预训练模型调用**：
  - ResNet-50：`torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)` → `torch.compile(..., backend="inductor")` → 输入 `torch.randn(1,3,64,64)`。
  - BERT：`BertTokenizer.from_pretrained('bert-base-uncased')` + `BertModel.from_pretrained("bert-base-uncased").to(device="npu:0")` → `torch.compile(..., backend="inductor")`。
  - ResNeXt：`timm.create_model('resnext101_32x8d', pretrained=True, num_classes=2)` → `torch.compile(..., backend="inductor")` → 输入 `torch.randn(64,3,7,7)`。
