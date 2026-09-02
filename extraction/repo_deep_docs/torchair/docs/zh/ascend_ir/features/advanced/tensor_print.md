# 图内Tensor打印功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/tensor_print.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/tensor_print.md

# 图内Tensor打印功能 — 一体化深度解读

## 【定位】

本文档描述 TorchAir 在昇腾 NPU 图模式下提供的"不触发断图的 Tensor 打印能力"——通过 `torchair.ops.npu_print` 接口，使用户能够在 GE 图执行过程中观察 Tensor 的 value、shape、dtype 等信息，从而辅助图模式下的调试与问题定位。

---

## 【技术要点】

1. **核心接口：`torchair.ops.npu_print`**——专为图模式设计的打印算子，等价语义于 Python 原生 `print`，但不会触发 graph break。
2. **适用范围约束**：仅适用于 **GE 图模式**场景，非 GE 图场景（如即时执行模式或带断图的图模式）不在该特性的覆盖范围内。
3. **异步打印机制**：打印为异步行为，输出顺序仅与图中算子执行顺序一致，与图外的 Python `print` 等其他输出顺序无关；因此图内打印可能出现在外部 Python `print` 之后。
4. **Device 侧资源代价**：作为异步算子，打印会**额外占用 Device 内存**并**耗费 Device 侧执行时间**；官方建议单次打印的数据量控制在 **KB 级别以下**，否则可能因内存不足或执行超时而失败。
5. **数据类型支持矩阵**（`torch.Tensor` 输入）：`torch.int8 / uint8 / int16 / int32 / int64 / uint16 / uint32 / uint64 / float16 / float32 / float64 / bool / bfloat16`。
6. **版本约束**：`torch.uint16 / uint32 / uint64` 三种类型的打印要求 **PyTorch ≥ 2.3.0**（此为 PyTorch 原生约束，非 TorchAir 约束）。`Complex` 类型 Tensor **不支持**打印对应 value 值。

---

## 【关键机制与数据】

- **断图问题（原文）**：在图模式下，Python 原生 `print` 会触发"graph break"，导致无法在图执行过程中观察 Tensor 的 value、shape、dtype。TorchAir 通过 `npu_print` 算子规避此问题，使打印节点作为图内算子参与编译与执行。
- **异步语义（原文）**：`torchair.ops.npu_print` 是异步接口，其输出**严格遵循图内算子调度顺序**，与图外 Python `print` 的输出顺序解耦。
  - **原文示例场景**：图执行完成后，用户在 Python 脚本中再调用 `print`，有可能出现"图内打印内容出现在 Python `print` 之后"的情况。
- **资源消耗（原文）**：异步打印 → 占用 Device 内存 + 占用 Device 侧执行时间 → 数据量过大会触发 OOM 或执行超时。
- **类型边界（原文）**：
  - 打印 **value 值**：`Complex` 类型 ❌；上述 13 种 dtype ✅。
  - **`torch.uint16 / uint32 / uint64` 需 PyTorch ≥ 2.3.0**（PyTorch 原生约束）。
- **数据流（基于代码示例）**：

```
Python 脚本  ──torch.compile(backend="npu", fullgraph=True)──►  GE 图编译
   │                                                                    │
   ▼                                                                    ▼
torch.arange(10).npu()  ────►  npu_print("hello, tensor:", x)  ──►  Device 异步打印
                                                                     │
                                                                     ▼
                                                          "hello, tensor: [0 1 2 ... 7 8 9]"
```

当传入 `tensor_detail=True` 时，输出额外携带 `shape` 与 `dtype`：

```
"hello, tensor_detail: tensor([0 1 2 ... 7 8 9], shape=[10], dtype=torch.int64)"
```

---

## 【表格解读】

**原文无表格**。原文中"支持的 torch.Tensor dtype"以列表形式罗列，而非以表格形式呈现，因此未进行表格逐字还原。可参见【技术要点】第 5 条。

---

## 【公式解读】

**原文无公式**。文档未包含 LaTeX 或伪代码形式公式。

---

## 【关联】

- **下游 API 文档**：[`npu_print`](../../api/ops/npu_print.md) ——本文档第 3 节明确将 `torchair.ops.npu_print` 的接口说明（参数列表、返回值等）指向此页。该页是本文档的"接口级定义"补充，定位为 ops 算子的 API 参考。
- **上游调用框架**：文档示例中使用了 `@torch.compile(backend="npu", fullgraph=True)` 与 `torch_npu`，说明 `npu_print` 的使用前提是**已通过 TorchAir 的 `npu` 后端进行全图编译**——它是 TorchAir 在 GE 图内注册的自定义算子，仅在 `fullgraph=True` 不触发断图的前提下才能生效。
- **横向能力对比**：本文档是 TorchAir"Advanced 特性"分类下的一个调试辅助特性，与图模式本身（GE 图）共生；它的存在是为弥补 Python 原生 `print` 在图模式下的不可用问题，而非替代 `print`。

---

## 【使用方法】

**启用方式（原文示例）**：

```python
import torch
import torch_npu, torchair

@torch.compile(backend="npu", fullgraph=True)
def hello_tensor(x):
    torchair.ops.npu_print("hello, tensor:", x)

@torch.compile(backend="npu", fullgraph=True)
def hello_tensor_detail(x):
    torchair.ops.npu_print("hello, tensor_detail:", x, tensor_detail=True)

v = torch.arange(10).npu()
hello_tensor(v)
# 打印结果为"hello, tensor: [0 1 2 ... 7 8 9]"

hello_tensor_detail(v)
# 打印结果为"hello, tensor_detail: tensor([0 1 2 ... 7 8 9], shape=[10], dtype=torch.int64)"
```

**关键调用要点（原文）**：

| 项 | 说明 |
|---|---|
| 接口名 | `torchair.ops.npu_print` |
| 第一个参数 | 字符串前缀（如 `"hello, tensor:"`） |
| 后续参数 | 待打印的 Tensor |
| 可选参数 `tensor_detail` | 设为 `True` 时额外输出 `shape` 与 `dtype`（见 `hello_tensor_detail` 示例） |
| 装饰器 | `@torch.compile(backend="npu", fullgraph=True)` |
| Tensor 需提前搬至 NPU | 通过 `.npu()` 完成 |

**配置项 / 命令**：原文未涉及独立的开关、配置文件或 CLI 命令；启用与否完全取决于用户是否在图编译后的函数内调用 `npu_print` 算子。其余约束（如打印数据量建议、dtype 范围）已在上文【技术要点】与【关键机制与数据】中列出。
