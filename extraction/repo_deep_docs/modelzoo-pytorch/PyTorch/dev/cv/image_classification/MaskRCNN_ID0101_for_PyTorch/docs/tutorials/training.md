# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/training.md

# 《Training》文档深度解读

---

## 【定位】

这篇文档解决的是 **detectron2 框架下"如何开展模型训练"的问题**——即在前置教程（自定义模型与数据加载器）已经就绪的前提下，向用户介绍两种互补的训练组织方式（自定义训练循环 vs. Trainer 抽象层），并给出指标日志记录的标准做法。

---

## 【技术要点】

1. **两种训练范式并存**：提供 "Custom Training Loop"（研究者写完整训练逻辑）和 "Trainer Abstraction"（框架提供标准化训练器）两条路线，定位是"由用户自由选择"。
2. **最小化训练器 `SimpleTrainer`**：定位是"minimal training loop for single-cost single-optimizer single-data-source training, with nothing else"（最小化、单代价/单优化器/单数据源、无额外功能）。
3. **默认训练器 `DefaultTrainer`**：基于 `SimpleTrainer`，从 config 初始化；默认集成 optimizer、learning rate schedule、logging、evaluation、checkpointing 等标准行为，被 `tools/train_net.py` 及多数脚本使用。
4. **Hook 系统作为扩展点**：SimpleTrainer 之外的 checkpointing、logging 等行为通过 [HookBase](../modules/engine.html#detectron2.engine.HookBase) 实现；复杂定制优先考虑 hook 是否能承载，否则回退到 `plain_train_net.py` 手动实现。
5. **`DefaultTrainer` 的两类定制路径**：①简单定制（改 optimizer / evaluator / LR scheduler / data loader 等）——在子类中覆写方法；②复杂定制——评估 hook 支持度，否则手动写训练逻辑。
6. **集中化指标日志 `EventStorage`**：训练中模型与 trainer 通过 `get_event_storage()` 获取存储对象，使用 `storage.put_scalar("some_accuracy", value)` 写入指标；最终由 `EventWriter` 写往各目的地，DefaultTrainer 已启用若干默认 `EventWriter`。

---

## 【关键机制与数据】

### 工作原理（数据流）

- **训练循环基础（plain_train_net.py 路线）**：用户自己用 PyTorch 组合 model + data loader + 训练循环，完全掌控训练逻辑。
- **Trainer 抽象层（默认路线）**：
  - `SimpleTrainer` 是基础骨架，仅承担"前向 → 计算 loss → 反向 → step"的最小循环；
  - `DefaultTrainer` 在 `SimpleTrainer` 之上加载 config，并默认挂接 optimizer、LR schedule、logging、evaluation、checkpointing 等组件；
  - 额外能力（checkpointing、logging 等）由 **Hook 系统** 在主循环钩子点插入执行；
  - 训练过程中产生的指标写入 **`EventStorage`**（集中存储），再由若干 **`EventWriter`** 落盘/打印到不同目的地。
- **指标日志的代码入口**（原文代码块，原文:）：
  ```
  from detectron2.utils.events import get_event_storage

  # inside the model:
  if self.training:
    value = # compute the value from inputs
    storage = get_event_storage()
    storage.put_scalar("some_accuracy", value)
  ```

### 性能/配置数据

原文未给出任何性能数字、batch size、epoch 数等量化指标；也未涉及具体超参数数值。**所有数字/参数/性能数据均为"原文未涉及"**，本文不臆造。

---

## 【表格解读】

**原文无表格**。原文中所有信息以小节标题、列表项、段落和一段代码块形式呈现，未包含任何参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式**。文中未出现任何 LaTeX 公式或伪代码公式表达式；唯一的"代码块"是 Python 调用片段（见上文"关键机制与数据"中按字保留的代码），不属于公式。

---

## 【关联】

依据文末的内部链接信息，可梳理出本文描述的模块/工具之间的上下游关系：

1. **`plain_train_net.py`（路径：../../tools/plain_train_net.py）**
   - 自定义训练循环路线的**示例实现**（"One such example is provided in tools/plain_train_net.py"）；
   - 同时也是**复杂定制回退方案**的起点——若 hook 无法支持则"start from tools/plain_train_net.py to implement the training logic manually"。

2. **`train_net.py`（路径：../../tools/train_net.py）**
   - **`DefaultTrainer` 的实际使用方**：被 `DefaultTrainer` 初始化并被"many scripts"采用；
   - 同时也是 **简单定制 `DefaultTrainer` 的参考**——"overwrite its methods in a subclass, just like tools/train_net.py"。

3. **`SimpleTrainer`（../modules/engine.html#detectron2.engine.SimpleTrainer）**
   - 训练器抽象层的**最小基类**，提供"single-cost single-optimizer single-data-source"的最小循环；
   - 是 `DefaultTrainer` 的**父类**（"`DefaultTrainer` is a `SimpleTrainer` initialized from a config"）。

4. **`HookBase`（../modules/engine.html#detectron2.engine.HookBase）**
   - Trainer 抽象层的**扩展机制**（"hook system"）；
   - 用于承载 `SimpleTrainer` 之外的 checkpointing、logging 等行为；
   - 也是评估"能否避免从 `plain_train_net.py` 手动实现"的判定工具（"see if the hook system can support it"）。

5. **`DefaultTrainer`（../modules/engine.html#detectron2.engine.defaults.DefaultTrainer）**
   - 文中**重复引用两次**（先介绍其功能，再介绍其定制方法），是 trainer 抽象层的**主推实例**；
   - 内置 optimizer、LR schedule、logging、evaluation、checkpointing 等默认配置；
   - 默认启用若干 `EventWriter`。

6. **`EventStorage`（../modules/utils.html#detectron2.utils.events.EventStorage）**
   - 训练过程中**指标的中转存储**——"put metrics to a centralized EventStorage"；
   - 与 `EventWriter` 配对使用：EventStorage 收指标 → EventWriter 写往各目的地。

整体依赖链（自下而上）：
> `EventStorage` / `EventWriter`（指标读写）
> → `HookBase`（扩展点）
> → `SimpleTrainer`（最小训练循环）
> → `DefaultTrainer`（默认完整训练器，从 config 初始化）
> → `train_net.py`（使用 DefaultTrainer 的脚本 / 简单定制范例）
> 平行分支：`plain_train_net.py`（自定义训练循环的范例 & 复杂定制的回退起点）

---

## 【使用方法】

### A. 自定义训练循环（Custom Training Loop 路线）

- 准备 model 与 data loader；
- 参考 [`tools/plain_train_net.py`](../../tools/plain_train_net.py) 实现完整训练循环；
- 所有训练逻辑由用户掌控，适合需要"full control"的研究场景。

### B. Trainer Abstraction 路线

- **最简用法**：直接使用 `DefaultTrainer`（由 config 初始化），已被 `tools/train_net.py` 及多数脚本采用；
- **简单定制 `DefaultTrainer`**（改 optimizer / evaluator / LR scheduler / data loader 等）：
  1. 继承 `DefaultTrainer`；
  2. 覆写其对应方法（"overwrite its methods in a subclass, just like tools/train_net.py"）；
- **复杂定制**：
  1. 优先判断 [`HookBase`](../modules/engine.html#detectron2.engine.HookBase) 是否能承载；
  2. 若不能，则回退到 [`tools/plain_train_net.py`](../../tools/plain_train_net.py) 手动实现训练逻辑。

### C. 指标日志记录（Logging of Metrics）

原文给出的标准做法（按字保留）：
```python
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
    value = # compute the value from inputs
    storage = get_event_storage()
    storage.put_scalar("some_accuracy", value)
```

- 在模型 `self.training` 为 True 时计算指标；
- 通过 `get_event_storage()` 获取当前上下文中的 `EventStorage`；
- 用 `put_scalar(name, value)` 写入标量指标；
- 后续由 `EventWriter` 写到各目的地，DefaultTrainer 默认已启用若干 EventWriter；
- 更多细节**原文未涉及**——需要时参考 `EventStorage` 文档与 `EventWriter` 模块。
