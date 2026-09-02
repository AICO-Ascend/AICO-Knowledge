# 非对齐Ulysses长序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/unaligned-ulysses-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/unaligned-ulysses-context-parallel.md

# 非对齐Ulysses长序列并行 — 深度解读

## 【定位】

这篇文档解决的是传统Ulysses长序列并行机制要求序列长度必须能被 Context Parallel (CP) size 整除的硬约束问题，描述了 mindspeed 通过引入可注入的 `GatherSizeCalculator` 抽象，使系统在处理动态、不规则（尤其是多模态）输入序列时仍能正常工作，从而扩展 Ulysses 长序列并行的适用场景。

---

## 【技术要点】

1. **根本约束**：传统 Ulysses 设计要求 `sequence length` 整除 `CP size`，在多模态等序列长度不可预测或经常变化的场景下被"卡住"。
2. **抽象接口**：定义抽象基类 `GatherSizeCalculator`，强制规定任何实现都必须提供 `calculate()` 方法，返回值类型为 `int` 或 `None`。
3. **两个预置策略**：
   - `DefaultGatherSizeCalculator`：默认返回 `None`，等价于"对齐 Ulysses"行为。
   - `DynamicGatherSizeCalculator`：根据"当前批次的注意力掩码序列长度"动态计算 gather size。
4. **可注入点**：`UlyssesContextAttention` 类允许通过构造函数参数注入 `gather_size_calculator` 实例，实现策略可插拔。
5. **Gather size 语义**：指经过 Ulysses 中 all-to-all 通信之后，输出张量在 `gather_idx` 维度上的大小。
6. **不兼容约束**：
   - 不支持与 `--use-legacy-models` 同时开启（即不在 legacy 分支使用）。
   - 与 `--context-parallel-kv-cache-policy` 设为 `full` 或 `half` 时互斥——若设置该参数，系统将自动回退到对齐 Ulysses。

---

## 【关键机制与数据】

**工作原理（原文描述还原）：**

- 传统 Ulysses 路径是"对齐"的：`sequence_length % cp_size == 0`，由此 gather size 是常量、可静态推导。
- "非对齐"路径下，CP size 不再是序列维度的硬分割因子，因此每次 all-to-all 后每张卡拿到的 `gather_idx` 维度大小会随实际批次而变。系统把这个变化量抽象为 **gather size**，并通过 `GatherSizeCalculator.calculate()` 在运行时计算。
- `DefaultGatherSizeCalculator` 返回 `None` 表示"沿用对齐逻辑"；`DynamicGatherSizeCalculator` 则读取当前批次 attention mask 的实际序列长度来动态得出 gather size。
- `UlyssesContextAttention` 在构造时接收 calculator 实例，运行时调用 `calculate()` 得到本次迭代所用的 gather size，进而决定 all-to-all 后张量的形状。

**数据流（原文语义）：**

输入批次 → 注意力掩码携带真实序列长度 → `DynamicGatherSizeCalculator.calculate()` 返回 int 类型的 gather size → 注入到 `UlyssesContextAttention` → 执行 all-to-all → 输出张量 `gather_idx` 维度大小等于该 gather size。

**性能/收益（原文仅有的定性陈述）：**

- 原文未给出任何量化性能数据（如吞吐、加速比、显存收益等），仅定性表述为"提升了系统对不同输入长度的适应能力"且"保持了良好的扩展能力"。
- 因此**性能数据这一项原文无任何数字指标**。

---

## 【表格解读】

**原文无表格。** 整篇文档未出现参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式。** 文档未出现 LaTeX 公式或伪代码形式的数学表达式。

（值得标注的是，文档中提到的 "Gather size" 是一个由代码语义定义的运行时常量，而非数学公式——它被定义为 all-to-all 后输出张量在 `gather_idx` 维度的大小。）

---

## 【关联】

文档本身没有提供文末的内部链接条目，但从正文约束条件可以梳理出与以下特性/模块的上下游关系：

| 关联项 | 关系 | 说明 |
|---|---|---|
| 传统（对齐）Ulysses 长序列并行 | **被替代/可回退** | `DefaultGatherSizeCalculator` 返回 `None` 时即恢复对齐行为 |
| `--context-parallel-algo ulysses_cp_algo` | **前置依赖** | 启用本特性的算法开关 |
| `--context-parallel-size` | **前置依赖** | 必须大于 1 才走 Ulysses 路径 |
| `--use-legacy-models` | **互斥** | 同时开启不被支持 |
| `--context-parallel-kv-cache-policy=full/half`（Ulysses KV 缓存优化） | **互斥** | 设置后系统自动回退到对齐 Ulysses |
| 多模态训练流程 | **应用驱动** | 序列长度不可整除 CP size 的典型来源 |
| `FlashSelfAttention` 等底层 attention 实现 | **组合点** | 作为 `core_attention` 被包装进 `UlyssesContextAttention` |

---

## 【使用方法】

启用方式（原文有明确步骤）：

1. **启动脚本配置**：
   ```
   --context-parallel-size [int]            # CP size 必须 > 1
   --context-parallel-algo ulysses_cp_algo  # 选择 Ulysses 算法
   ```
   且**不可**同时开启 `--use-legacy-models`，**不可**将 `--context-parallel-kv-cache-policy` 设为 `full` 或 `half`。

2. **自定义 Calculator（可选）**：继承 `GatherSizeCalculator`，实现 `calculate(*args, **kwargs)` 返回 int 或 `None`，在初始化 `UlyssesContextAttention` 时通过 `gather_size_calculator=` 注入。

3. **直接使用预置 `DynamicGatherSizeCalculator`**：无需自定义逻辑，会按当前批次 attention mask 序列长度自动算 gather size。

**原文代码示例（关键骨架）**：

```python
from mindspeed.core.context_parallel.ulysses_context_parallel.ulysses_context_parallel import (
    UlyssesContextAttention,
    GatherSizeCalculator,
    DynamicGatherSizeCalculator,
)
import megatron.core.parallel_state as ps
from your_library import FlashSelfAttention

class CustomGatherSizeCalculator(GatherSizeCalculator):
    def calculate(self, *args, **kwargs):
        return kwargs.get("gather_size", None)  # 示例逻辑

core_attention = FlashSelfAttention()
calculator = DynamicGatherSizeCalculator()       # 或 CustomGatherSizeCalculator()
ulysses_attention = UlyssesContextAttention(
    core_attention,
    ps.get_context_parallel_group(),
    gather_size_calculator=calculator,
)
```
