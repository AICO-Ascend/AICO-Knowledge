# 激活函数重计算

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/activation_function_recompute.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/activation_function_recompute.md

# 一体化深度解读：激活函数重计算（Activation Function Recompute）

---

## 【定位】

这篇文档描述了一种**将重计算与反向传播解耦的"激活函数重计算"框架**，通过在前向阶段释放激活函数输出、在反向阶段之前即时重计算，使计算量小但显存占用大的激活函数（如 gelu）能够真正省下输出激活值的显存，是 mindspeed-rl 在显存优化方向上对传统紧耦合重计算机制的一次架构性改造。

---

## 【技术要点】

1. **机制创新点：重计算与反向传播解耦。** 传统框架将重计算绑定到被重计算模块自身的反向流程中，导致前向必须保留激活函数的输出；新框架将重计算"前置"到下游反向模块之前，从而允许前向阶段释放输出。
2. **核心作用对象：gelu 类激活函数。** 文档明确指出 gelu 激活函数具有"产生大量数据但计算量很小"的特点，是"以时间换空间"策略的最佳切入点。
3. **典型数据形状锚点。** 文档给出了 MLP 中 gelu 上下游张量的形状参考：**b 和 c 的 shape 为 (batch, seq, 4hidden_size)**——这是激活函数重计算收益最显著的中间张量尺寸。
4. **两条命令行开关。**
   - `--recompute-activation-function`：开启激活函数重计算功能。
   - `--recompute-activation-function-num-layers ${num}`：指定激活函数重计算的层数。
5. **执行优先级与组合约束。** 与全重计算同时开启时，必须满足 `--recompute-method 为 block`；执行顺序为"先全重计算层，后激活函数重计算层"；不开流水线并行时，**全重计算层数 + 激活函数重计算层数 = 总层数**（即不会有一层既做全重计算又做激活函数重计算）。
6. **可扩展机制：`CheckpointWithoutOutput` 类。** 提供通用接口，允许对任意自定义模块做"丢弃物理存储、保留逻辑视图、register_hook 触发恢复"的重计算包装。

---

## 【关键机制与数据】

### 工作原理（基于原文流程图描述）

文档通过两个图对比"传统紧耦合"和"新框架解耦"两种方案：

**图 1（重计算与反向绑定）：** 在 MLP 中，gelu 上游的中间张量 a、b、c、d 都需要被反向消费。其中 **b 和 c 的 shape 为 (batch, seq, 4hidden_size)**，是显存占用主力。gelu 本身计算量小，故**将 tensor c 释放掉**，反向时在 **4h→h 反向之前重新计算 c**。

**图 2（灵活插入重计算）：** 在前向 4h→h 计算完毕后，将 c 释放，仅保留逻辑视图；在 4h→h grad 计算之前需要把 c 算回来——**通过给 d 打 `tensor_hook` 的方式来插入重计算**。

### 数据流对比（原文摘录）

| 维度 | 传统方案 | 新框架 |
|---|---|---|
| 前向阶段 gelu 输出 | **必须保留**（因模块 A 反向需要） | **可释放**（因重计算被前置） |
| gelu 重计算触发时机 | 在 gelu 自身的反向流程中（紧耦合） | 在模块 A 反向之前（解耦） |
| 显存节省效果 | 有限，仍存大量中间激活 | 显著，因 gelu 输出不再被前向持有 |
| 性能开销 | — | **训练性能只会略微下降**（原文表述） |

### 性能数据

- **原文：** "启用激活函数重计算后，激活函数的输出激活值不用再保存，内存占用减少。同时由于激活函数计算量很小，训练性能只会略微下降。"
- **原文：** "根据模型配置不同，激活函数重计算收益也会发生改变。"
- 注：原文**未给出具体的数值收益（如百分比、显存 MB、吞吐 tokens/s 等）**，文档明确指出收益随模型配置而变。

### 核心机制文字描述（原文核心句）

> 原文："本方案设计了一种传入模块函数进行重计算的机制，在合适的时机，丢弃重计算模块输出的物理存储，保留逻辑视图。在反向时，在合适的时机，利用 register_hook 插入重计算流程。利用传入的函数重新进行计算，得到结果。"

这是整个技术方案的三段式骨架：**前向丢弃 → 逻辑保留 → 反向 hook 触发重算**。

---

## 【表格解读】

**原文无表格。** 文档未提供任何参数表、性能对比表或配置项矩阵。文档中的"图 1"、"图 2"为外部图片链接，不属于可逐字还原的表格结构。

---

## 【公式解读】

**原文无公式。** 文档未出现任何 LaTeX 或伪代码公式。文档中出现的仅是伪代码示例（见【使用方法】节中的 Python 代码片段），不构成数学公式。

---

## 【关联】

1. **与传统"全重计算"（full recompute）的关系**
   - 二者可同时开启。
   - 约束条件：必须 `--recompute-method 为 block`。
   - 执行优先级：先全重计算层，后激活函数重计算层。
   - 层数划分（无流水线并行时）：**全重计算层数 + 激活函数重计算层数 = 总层数**；一层不会同时承担两种重计算。

2. **与"自适应重计算"（adaptive recompute）的关系**
   - **暂不兼容**（原文明确指出："暂不兼容自适应重计算特性"）。

3. **与流水线并行（pipeline parallel）的关系**
   - 文档仅给出约束："在流水线并行未开启的情况下，全重计算层数和激活函数重计算层数之和应该等于总层数"——暗含开启流水线并行时该等式约束不强制。

4. **与混合精度训练的隐性关联**
   - 文档"背景介绍"段铺垫了"权重与状态权重生命周期不重叠可共享内存"的话题，暗示本方案处于 mindspeed-rl 的整体显存优化体系内。

5. **上下文中提到的模块依赖**
   - gelu（激活函数模块）→ 后续模块 A（4h→h 线性层）。
   - 触发链：**d 注册 tensor_hook → 4h→h grad 计算前 → 调用传入函数 → 重新计算 c**。

6. **可扩展接口的内部依赖**
   - `CheckpointWithoutOutput` 类来自 `mindspeed.core.tensor_parallel.random` 路径（原文 import 语句），表明该能力建立在 mindspeed 的随机状态管理/张量并行基础设施之上。
   - 使用该 API 的前提："如要使用 register_hook，需要确保张量有梯度"。

> 注：本篇文档文末**未提供任何内部交叉链接**（"内部链接: (无)"），上述关联均依据文中正文提及的相关特性归纳。

---

## 【使用方法】

### 命令行启用方式

| 配置项 | 取值/含义 | 备注 |
|---|---|---|
| `--recompute-activation-function` | 开关型 flag | 启用激活函数重计算 |
| `--recompute-activation-function-num-layers ${num}` | 整数 `${num}` | 指定参与激活函数重计算的层数 |
| `--recompute-method` | 必须为 `block` | 仅在与全重计算同时开启时强制 |

### 组合使用约束（原文"说明"节要点）

- **可与全重计算同时开启**，但 `--recompute-method` 必须为 `block`。
- 执行优先级：**先计算全重计算层，后计算激活函数重计算层**。
- **层数约束（不开流水线并行时）：** 全重计算层数 + 激活函数重计算层数 = 总层数；不会有一层既做全重计算又做激活函数重计算。
- **不兼容自适应重计算特性**。

### 适用场景（原文）

> 原文："主要用于训练场景，用户内存不足或要节省内存时，可以开启激活函数重计算，节省激活函数的输出激活值。"

### 扩展使用：`CheckpointWithoutOutput` 自定义重计算

文档给出了完整的 Python 伪代码示例，可对**任何自定义模块**做"丢弃输出 + 反向 hook 重算"的灵活包装：

```python
from mindspeed.core.tensor_parallel.random import CheckpointWithoutOutput


class Custom_module(torch.nn.Module):
    def __init__(self):
        ......

    def forward(self, input):
        self.activation_checkpoint_manager = CheckpointWithoutOutput()
        function_output = self.activation_checkpoint_manager.checkpoint(
            self.custom_function, False, function_input1, function_input2, ...)
        ...(after used output)
        self.activation_checkpoint_manager.discard_output()
        if module_output.requires_grad:
            module_output.register_hook(self.activation_checkpoint_manager.recompute)

        return module_output
```

**示例代码逐块解读（基于原文）：**

1. `CheckpointWithoutOutput()` 实例化一个重计算管理器。
2. `.checkpoint(self.custom_function, False, ...)` 以前向方式运行自定义函数，第二个参数 `False` 控制是否保留原计算语义（原文未进一步解释此布尔位含义，按字面保留）。
3. **下游消费完 `function_output` 后**调用 `.discard_output()` 释放其物理存储，仅保留逻辑视图——这是节省显存的关键步骤。
4. **仅当 `module_output.requires_grad` 为真**时才注册 `register_hook`——这是原文特别强调的边界条件（"如要使用 register_hook，需要确保张量有梯度"）。
5. 最终返回 `module_output` 完成一次"前向丢弃、反向恢复"的可重计算模块封装。

## 图文联合解读

- `img-transfer.gitcode.com`: **图文联合解读：**

图示MLP前向流（h→4h→gelu→4h→h，标注a/b/c/d）与对应反向梯度流（h-4h grad、gelu grad、4h→h grad），展示激活值沿箭头从左向右传递。

**论证结论**：传统框架将重计算与反向紧耦合，反向时模块A（h-4h grad需b、4h→h grad需c）的梯度计算先于gelu重计算触发，因此前向必须保留gelu输出b，显存无法真正节省。

**与文档关系**：作为"传统方案"基线，对照凸显新框架将gelu重计算前置到A反向之前、无需保存b的核心优势。
- `img-transfer.gitcode.com`: **图文联合解读：**

图示MLP前向流（h→4h→gelu→4h→h，标注a/b/c/d）与对应反向梯度流（h-4h grad、gelu grad、4h→h grad），展示激活值沿箭头从左向右传递。

**论证结论**：传统框架将重计算与反向紧耦合，反向时模块A（h-4h grad需b、4h→h grad需c）的梯度计算先于gelu重计算触发，因此前向必须保留gelu输出b，显存无法真正节省。

**与文档关系**：作为"传统方案"基线，对照凸显新框架将gelu重计算前置到A反向之前、无需保存b的核心优势。
