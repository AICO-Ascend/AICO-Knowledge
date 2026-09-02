# 算子级确定性计算配置功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/deterministic.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/deterministic.md

# 「算子级确定性计算配置功能」一体化深度解读

---

## 【定位】

这篇文档描述了 TorchAir 在 GE 图模式下为**指定作用域内的算子**配置确定性级别的能力——通过 `torchair.scope.deterministic` 这一 with 语句上下文管理器，将 `_deterministic`/`_deterministic_level` 两个属性挂载到目标算子上，从而在局部范围（而非全图）控制算子是否启用确定性计算及其强度，解决"模型推理中部分算子因并行归约顺序、算法选择等因素在相同输入下产生不一致结果"的工程问题。

---

## 【技术要点】

1. **核心接口**：`torchair.scope.deterministic(level: int)`，以 with 语句块形式限定作用域，仅对块内 GE 算子生效。
2. **属性注入机制**：进入 scope 后,块内算子被自动附加 `_deterministic` 与 `_deterministic_level` 两个属性；退出 scope 后（块外算子）不再附加这两个属性，继续沿用整图默认的确定性配置。
3. **四级确定性级别**：原文明确定义了 4 档——
   - `level=0`：关闭确定性计算
   - `level=1`：确定性计算
   - `level=2`：强一致性
   - `level=3`：Batch 一致性
4. **属性编码规则**（关键数字）：
   - `_deterministic` 字段：`level=0` 时为字符串 `"0"`；`level=1、2、3` 时一律为字符串 `"1"`（即"是否启用"二值化）
   - `_deterministic_level` 字段：保存完整的级别数值（与 level 入参一致）
   - 两者均以**字符串形式**写入算子属性
5. **作用域语义**：with 语句块支持**嵌套**，进入内层 scope 使用内层 level，退出内层 scope 后恢复外层 level；block 内**不支持断图**。
6. **生效约束**：确定性级别能否真正生效取决于**算子本身**与**配套 CANN 版本**是否支持对应级别；仅适用于 GE 图模式场景。

---

## 【关键机制与数据】

### 数据流 / 工作原理

```
用户代码
  │
  ├── 进入 torchair.scope.deterministic(level=k)
  │     │
  │     └── 上下文管理器将 block 内的 GE 算子
  │           写入属性：_deterministic="0/1"
  │                    _deterministic_level="k"
  │
  ├── block 内算子 ──→ 下沉到 GE 图时带属性 ──→ CANN 按属性调度确定性路径
  │
  ├── 退出 scope
  │     └── block 外算子 ──→ 不带这两个属性 ──→ 使用整图默认确定性配置
  │
  └── 整图默认确定性配置（scope 外算子）
        └── 通过 torch.compile 之前调用 torch_npu.npu.set_deterministic_level(level) 设置
```

### 关键映射关系（原文）

| 字段 | 来源 | 取值映射 |
|---|---|---|
| `_deterministic`（是否启用） | level | level=0 → `"0"`；level∈{1,2,3} → `"1"` |
| `_deterministic_level`（级别） | level | 直接保存 level 值（字符串形式） |

### 性能数据

原文未涉及任何性能数据/基准/时延/吞吐数字。

---

## 【表格解读】

### 确定性级别含义表（原文唯一表格，逐字还原）

| level | 含义 |
|---|---|
| 0 | 关闭确定性计算。 |
| 1 | 确定性计算。 |
| 2 | 强一致性。 |
| 3 | Batch 一致性。 |

**逐行解读：**

- **第 1 行（level=0）**：关闭档，作为"对照基准"，相当于不施加任何确定性约束，算子按 CANN 常规路径执行；对应 `_deterministic="0"`。
- **第 2 行（level=1）**：基础确定性计算档，针对单算子内部的并行归约顺序、算法选择等不确定因素做约束，使相同输入总能复现相同结果；对应 `_deterministic="1"`、`_deterministic_level="1"`。
- **第 3 行（level=2）**：在 level=1 基础上进一步约束"强一致性"，通常覆盖更广的算子集合和更严格的执行路径；对应 `_deterministic="1"`、`_determinetric_level="2"`（注：原文此行仅给出语义标签，无量化指标，适用边界取决于算子与 CANN 版本）。
- **第 4 行（level=3）**：Batch 一致性档，要求同一 batch 内不同样本的运算次序、归约路径对结果的影响一致；适用示例正好是文档示例代码中的 `torch.mm` 场景（输入 `x` 为 `(2, 2)` 形状，模拟 batch 内两条样本），`_deterministic="1"`、`_deterministic_level="3"`。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末给出的内部链接以及文档上下文，可建立的关联如下：

- **与 [图结构 dump 功能（`../basic/graph_dump.md`）](#)** 的关系：文档末尾明确建议"参考图结构 dump 功能导出 GE 图，检查目标算子的 `_deterministic` 和 `_deterministic_level` 属性是否符合预期"。即 graph_dump 是本特性的**验证/观测手段**——scope 接口负责"写入属性"，graph_dump 负责"读取并核对属性"，二者构成"写入 → 校验"闭环。
- **与 `torch_npu.npu.set_deterministic_level` 的关系**：文档明确指出，本 scope 接口用于**局部**确定性配置；而 `torch_npu.npu.set_deterministic_level` 用于**全局**（整图默认）确定性配置，必须在调用 `torch.compile` 之前设置；二者是"局部 vs 全局"的互补关系，文档也明确禁止"在模型 `forward` 中直接调用 `torch_npu.npu.set_deterministic_level` 来实现局部配置"。
- **与 GE 图模式的依赖关系**：本特性仅适用于 GE 图模式场景，block 内不允许断图，scope 外的算子继续使用整图默认配置——意味着本特性的能力边界由 GE 图编译/下发链路决定。
- **与 CANN 算子实现的依赖关系**：文档"使用约束"中点明，确定性级别能否生效取决于**算子和配套 CANN 版本**是否支持对应级别，表明本特性是"上层接口 + 下层 CANN 能力"的耦合，级别越高（2、3）越可能受限于特定算子/版本组合。

---

## 【使用方法】

### 接口调用形式（原文给出）

```python
with torchair.scope.deterministic(level: int):
```

- `level` 仅支持整数 `0`、`1`、`2`、`3`，传入其他值会抛出 `ValueError`。

### 嵌套规则

- with 语句块支持嵌套；进入内层 scope 后使用内层 level，退出内层 scope 后恢复外层 level。

### 整图默认确定性级别（scope 外算子）

在调用 `torch.compile` 之前设置：

```python
torch_npu.npu.set_deterministic_level(level)
```

### 适用与不适用

- **适用**：仅限 GE 图模式场景。
- **不适用/禁止**：在模型 `forward` 中直接调用 `torch_npu.npu.set_deterministic_level` 来实现局部配置；scope 内不允许断图。

### 完整示例（原文给出，原样保留）

```python
import torch
import torchair


class Model(torch.nn.Module):
    def forward(self, x, weight1, weight2):
        with torchair.scope.deterministic(3):
            batch_consistent_out = torch.mm(x, weight1)

        default_out = torch.mm(x, weight2)
        return batch_consistent_out + default_out


config = torchair.CompilerConfig()
npu_backend = torchair.get_npu_backend(compiler_config=config)
model = torch.compile(Model(), backend=npu_backend, fullgraph=True, dynamic=False)

x = torch.randn(2, 2)
weight1 = torch.randn(2, 2)
weight2 = torch.randn(2, 2)
result = model(x, weight1, weight2)
```

示例行为（原文已明确说明）：
- 第一个 `torch.mm`（block 内）将携带 `_deterministic="1"` 与 `_deterministic_level="3"` 属性。
- 第二个 `torch.mm`（block 外）不携带这两个属性，沿用整图默认配置。

### 验证手段

通过图结构 dump 功能（`../basic/graph_dump.md`）导出 GE 图，检查目标算子的 `_deterministic` 与 `_deterministic_level` 属性是否符合预期。
