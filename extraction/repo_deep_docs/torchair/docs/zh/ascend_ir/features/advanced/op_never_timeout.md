# 图内算子不超时配置功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/op_never_timeout.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/op_never_timeout.md

# 图内算子不超时配置功能 —— 一体化深度解读

---

## 【定位】

本文档解决**昇腾 NPU 上图模式推理时统一超时阈值难以兼顾"易误判"与"故障响应慢"的问题**：TorchAir 通过 `torchair.scope.op_never_timeout` 接口对指定范围内的算子打上"**永不超时**"标签，使其跳过超时检测，从而在保留整体超时恢复机制的前提下，避免对大计算量算子产生误判、保障长尾推理的连续性。

---

## 【技术要点】

1. **核心机制——范围限定 + 属性注入**：通过 `with torchair.scope.op_never_timeout(enable=...)` 语句块圈定算子作用域；在语句块内，被编译到图中的算子会被自动附加 `_op_exec_never_timeout` 属性；该属性决定该算子是否参与超时检测。
2. **`enable` 形参语义**：`enable` 为 `bool` 类型；`enable=True` 时块内算子添加 `_op_exec_never_timeout=True`（不参与超时检测）；`enable=False` 时块内算子添加 `_op_exec_never_timeout=False`（参与超时检测）。
3. **作用域可嵌套**：内层 `with` 会覆盖外层 `enable` 的取值，每个算子按"最近一次生效的 `enable` 值"决定属性写入。
4. **使用约束——仅 GE 图模式生效**：本功能只适用于 GE 图模式场景。
5. **使用约束——融合算子不继承**：若子算子配置了本功能，其属性无法继承到融合后的新融合算子节点上。
6. **底层属性来源**：`_op_exec_never_timeout` 属性的详细定义与约束需查阅《CANN GE 图引擎 API》中"数据类型 > 属性名列表"章节（即该属性由 CANN GE 定义，TorchAir 只是上层注入入口）。

---

## 【关键机制与数据】

**工作原理（原文提炼）：**

1. **算子超时检测的取舍困境**
   - 推理中某些算子执行异常或耗时过长 → 任务长时间等待 → 整体阻塞或卡顿 → 需要超时恢复流程以快速恢复业务。
   - 统一阈值难以设定：
     - 部分算子计算量大、执行时间本身就长；
     - 阈值过短 → 误触发恢复；
     - 阈值过长 → 故障响应延迟。

2. **解决方案——"永不超时"标签**
   - 对部分算子设置"永不超时"标签，使其**不参与超时检测**，避免误判，保证推理流程的连续性。
   - 同时仍保留其他算子的超时检测，整体可靠性与恢复能力不丢失。

3. **TorchAir 注入路径**
   - 提供 `torchair.scope.op_never_timeout` 接口；
   - 通过对指定范围内的算子添加 `_op_exec_never_timeout` 属性，完成"不超时"语义注入。

4. **嵌套覆盖机制（原文示例佐证）**

   ```python
   def forward(self, x, y):
       x = x + 1                                   # Add（不在任何 op_never_timeout 块中）
       with torchair.scope.op_never_timeout(enable=True):       # 外层：True
           x = x * y                               # Mul    -> _op_exec_never_timeout=True
           with torchair.scope.op_never_timeout(enable=False):  # 内层：False（覆盖外层）
               y = y - 1                           # Sub    -> _op_exec_never_timeout=False
       return x + y
   ```

   开启 DEBUG 日志后可见两条属性写入记录：

   ```
   [DEBUG] TORCHAIR(993590,python):2025-10-30 17:42:58.380.700 [_scope_attr.py:38]993590 Set attribute _op_exec_never_timeout: True on op: Mul
   [DEBUG] TORCHAIR(993590,python):2025-10-30 17:42:58.388.864 [_scope_attr.py:38]993590 Set attribute _op_exec_never_timeout: False on op: Sub
   ```

   - `Add` 未出现在日志中，说明默认不写入 `_op_exec_never_timeout` 属性；
   - `Mul` 因外层 `enable=True` 被写入 `True`；
   - `Sub` 因内层 `enable=False` 被覆盖写入 `False`（即重新写一次，而非继承外层的 `True`）。

5. **数据流概览**
   `Python 用户代码` → `torchair.scope.op_never_timeout(enable=…)` with 块 → `torch.compile + npu_backend` 编译期捕获作用域 → 在图构建时遍历落入块内的算子 → 调用底层 API 写入 `_op_exec_never_timeout` 属性 → 生成的 GE 图算子节点携带该属性 → CANN GE 运行时按属性决定是否跳过超时检测。

---

## 【表格解读】

**原文无表格。** 文档中没有以表格形式呈现的参数表、对比表或配置表；属性说明、约束条件均以列表/正文形式给出。

---

## 【公式解读】

**原文无公式。** 全文未出现 LaTeX 数学公式或伪代码公式；作用域嵌套的行为通过 Python `with` 语句直接表达，没有代数化建模。

---

## 【关联】

1. **与 `torchair.scope.op_never_timeout` API 文档（[`../../api/scope/op_never_timeout.md`](../../api/scope/op_never_timeout.md)）的关系**
   - 本文是该 API 的 **feature 介绍**；
   - API 文档提供该 `with` 上下文管理器的接口签名、参数与返回值的精确说明。
   - 链接出现在"使用方法"章节第 2 步。

2. **与 TorchAir Python 层日志打印（[`../basic/python_log_print.md`](../basic/python_log_print.md)）的关系**
   - 本 feature 设置成功与否的判断依据是 **Debug 日志中的属性写入条目**；
   - 文档引用 Python 日志打印功能作为**验证手段**，提示用户"开启 Debug 日志，可以看到类似的提示信息"。
   - 链接出现在"使用示例"末尾。

3. **与下游 CANN GE 的关系**
   - `_op_exec_never_timeout` 属不属于 TorchAir 自定义，而是 CANN GE 图引擎的属性；
   - 详细定义与约束需查阅《CANN GE 图引擎 API》中"数据类型 > 属性名列表"章节。
   - 因此本 feature 是 TorchAir 对 CANN GE 属性的**Python 层便捷注入封装**，受到 CANN GE 图引擎自身语义约束（即"本功能仅适用于 GE 图模式场景"）。

4. **与 `torch.compile` + GE 图模式的关系**
   - 算子融合发生在 GE 图阶段；融合后生成的新算子节点**不会**继承子算子上的 `_op_exec_never_timeout` 标签——这是本文档明确点出的融合场景约束。

---

## 【使用方法】

**一、配置 `CompilerConfig` 与后端**

```python
import torch
import torch_npu, torchair
import logging
from torchair import logger

logger.setLevel(logging.DEBUG)                        # 可选：开启 Debug 日志用于验证
config = torchair.CompilerConfig()
config.mode = "max-autotune"                          # GE 图模式场景
npu_backend = torchair.get_npu_backend(compiler_config=config)
```

**二、在 `forward` 中按算子作用域使用 `with` 语句块**

```python
with torchair.scope.op_never_timeout(enable=True):
    # 块内落入图中的算子将被自动添加 _op_exec_never_timeout 属性
    ...
```

- `enable`：`bool`；
  - `True` → 块内算子不参与超时检测；
  - `False` → 块内算子参与超时检测（可在外层 `True` 块中嵌套 `False` 块来局部取消）。

**三、编译并执行**

```python
model = Model()
model = torch.compile(model, backend=npu_backend, dynamic=False)
x = torch.randn(2, 2)
y = torch.randn(2, 2)
model(x, y)
```

**四、验证生效**

按 [`../basic/python_log_print.md`](../basic/python_log_print.md) 开启 Debug 日志后，应观察到形如下文（原文给出的样例）的输出：

```
[DEBUG] TORCHAIR(...):... [_scope_attr.py:38]... Set attribute _op_exec_never_timeout: True on op: Mul
[DEBUG] TORCHAIR(...):... [_scope_attr.py:38]... Set attribute _op_exec_never_timeout: False on op: Sub
```

**五、约束与限制（原文明确列出）**

| 约束项 | 原文描述 |
|---|---|
| 适用范围 | 本功能仅适用于 GE 图模式场景。 |
| 算子融合 | 若子算子配置了本功能，其无法继承到新的融合算子节点上。 |
| 属性来源 | `_op_exec_never_timeout` 属性的详细介绍和约束参见《CANN GE 图引擎 API》中"数据类型 > 属性名列表"章节（原文未涉及更多细节）。 |
