# Meta Registration Guide

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/meta-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/meta-guide.md

# Meta Registration Guide 深度解读

---

## 【定位】

本文档解决在昇腾 NPU 上为自定义算子（`npu_operator_name`）注册 Meta 推理函数（shape/dtype 推断）的问题，使算子能够在 `torch.compile`、`torch.export` 和 FakeTensor 模式下无需实际执行即可完成张量元信息推导，从而支持图编译与导出链路。

---

## 【技术要点】

1. **核心作用**：Meta Registration 不执行真实计算，只提供 shape/dtype 推断，适配 `torch.compile`、`torch.export`、FakeTensor 模式。
2. **注册位置**：所有 Meta 注册函数统一追加到 `op_plugin/python/meta/_meta_registrations.py` 文件中，使用装饰器 `@impl(m, "npu_operator_name")` 绑定到具体算子名。
3. **标准四步模板**：① 参数校验（`torch._check` + `ops_error(ErrCode.VALUE)`）；② 推断 `output_shape`（基于 `input.shape` 修改）；③ 推断 `output_dtype`（基于 `input.dtype` 修改）；④ 通过 `torch.empty(..., device='meta')` 返回 Meta Tensor。
4. **常见返回模式**：`torch.empty_like(input, device='meta')` 用于同 shape 输出；多输出场景通过元组返回多个 Meta Tensor；`dtype` 可显式指定（如 `torch.int8`、`torch.int64`）。
5. **量化算子 dtype 映射表**：`DTYPE_MAP` 将数值编码映射到 PyTorch dtype，关键映射为 `2→torch.int8`、`13→torch.quint4x2`、`30→torch.float8_e4m3fn`、`31→torch.float8_e5m2`。
6. **INT4 packed 特殊处理**：当 `dst_type == 13` 时，最后一维需整除 8（`output_shape[-1] // 8`），且输出 dtype 固定为 `torch.int32`。

---

## 【关键机制与数据】

- **Meta Tensor 的本质**：原文示例返回 `torch.empty(..., device='meta')`，表示在 `meta` device 上分配"虚拟张量"，仅承载 shape/dtype 元数据，不持有存储与数值。
- **数据流**：`@impl(m, "npu_operator_name")` → 装饰器把 `npu_operator_name` 算子与 Meta 函数绑定 → 当上层调用该算子时（在 `torch.compile`/`torch.export`/FakeTensor 上下文）→ Meta 函数被触发 → 返回的 Meta Tensor 提供 shape/dtype 给下游编译/导出流程。
- **INT4 packed 维度收缩规则**（原文）：`output_shape[-1] = output_shape[-1] // 8`，并以 `torch.int32` 作为承载 dtype（说明一个 int32 可装 8 个 INT4 元素）。
- **校验机制**（原文）：`torch._check(input.dim() >= 2, lambda: f"input must be at least 2D, but got {input.dim()}D" + ops_error(ErrCode.VALUE))`，使用 lambda 延迟构造错误信息以避免开销。
- **Troubleshooting 章节**：原文仅标注"Meta registration and FakeTensor issues. Accumulate from cases."，未列出具体排查条目（原文）。

---

## 【表格解读】

原文包含一个 dtype 映射字典，**逐字还原**如下：

| 数值编码 (key) | 映射 dtype (value) | 解读 |
|---|---|---|
| `2` | `torch.int8` | 8 位有符号整型，最常见的对称量化 dtype。 |
| `13` | `torch.quint4x2` | INT4 packed（4 位无符号，每 8 个打包）。特殊处理：`output_shape[-1] // 8`，输出 dtype 为 `torch.int32`。 |
| `30` | `torch.float8_e4m3fn` | FP8 E4M3 格式（4 位指数 + 3 位尾数），常用于推理加速。 |
| `31` | `torch.float8_e5m2` | FP8 E5M2 格式（5 位指数 + 2 位尾数），动态范围更大。 |

原文无其他对比表格或配置项表格。

---

## 【公式解读】

原文无独立数学公式（LaTeX 或伪代码形式）。代码中出现的算术表达式仅一处：

```python
output_shape[-1] = output_shape[-1] // 8
```

符号含义：
- `output_shape`：列表，表示 Meta 阶段推断的输出张量形状。
- `output_shape[-1]`：最后一维长度。
- `// 8`：整数除法，将最后一维收缩为原来的 1/8，对应 INT4 packed 打包语义（8 个 4-bit 元素合并到 1 个 32-bit 容器中，因此需要除以 8）。

---

## 【关联】

本文档所处的 Meta Registration 机制与以下特性/模块存在上下游依赖（原文提及）：

- **`torch.compile`**（上游消费者）：依赖 Meta 函数提供符号化 shape/dtype 以完成图编译。
- **`torch.export`**（上游消费者）：依赖 Meta 函数生成可导出的计算图。
- **FakeTensor 模式**（上游消费者）：依赖 Meta Tensor 作为虚拟载体，避免触发真实 NPU 计算。
- **`torch._check` + `ops_error(ErrCode.VALUE)`**：来自 `ops_error` / `ErrCode` 错误码体系（PyTorch 公共校验工具），用于构造带错误码的失败信息。
- **同目录现有 Meta 注册函数**：原文明确"For complete examples, refer to existing Meta registrations in the file"，建议参考 `_meta_registrations.py` 中已实现的算子作为模板。

内部链接：原文无内部链接。

---

## 【使用方法】

**启用方式（原文有）**：

1. 在文件 `op_plugin/python/meta/_meta_registrations.py` 中追加一个函数。
2. 使用装饰器 `@impl(m, "npu_operator_name")` 把函数绑定到目标 NPU 算子。
3. 函数签名形如：
   ```python
   def npu_operator_name_meta(input, *, optional_param=None, int_param=1):
   ```
4. 函数体按"四步模板"实现：参数校验 → shape 推断 → dtype 推断 → `return torch.empty(output_shape, dtype=output_dtype, device='meta')`。

**配置项/命令**：原文未涉及具体配置项或命令行开关。

**完整代码示例**：

```python
@impl(m, "npu_operator_name")
def npu_operator_name_meta(input, *, optional_param=None, int_param=1):
    # 1. Parameter validation (optional but recommended)
    torch._check(
        input.dim() >= 2,
        lambda: f"input must be at least 2D, but got {input.dim()}D" + ops_error(ErrCode.VALUE),
    )

    # 2. Infer output shape
    output_shape = list(input.shape)
    # Modify based on operator logic

    # 3. Infer output dtype
    output_dtype = input.dtype
    # Modify based on operator logic

    # 4. Return Meta Tensor
    return torch.empty(output_shape, dtype=output_dtype, device='meta')
```
