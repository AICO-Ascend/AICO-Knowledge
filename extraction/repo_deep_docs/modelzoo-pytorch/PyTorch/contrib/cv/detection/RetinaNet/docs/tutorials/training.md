# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/training.md

# 一体化深度解读：RetinaNet 训练教程文档

---

## 【定位】

这篇文档解决的是 detectron2 框架下 RetinaNet 模型「如何启动并管理模型训练」的问题，向用户介绍两种训练范式（自定义训练循环 与 Trainer 抽象层）的取舍，并说明如何对训练过程进行自定义扩展以及如何对训练指标进行记录与写出的能力。

---

## 【技术要点】

1. **两种训练范式并列**：文档显式给出两种风格——"Custom Training Loop"（自写训练循环）和 "Trainer Abstraction"（标准化的 trainer + hook 系统），让用户按需选择。
2. **SimpleTrainer 的定位**：`SimpleTrainer` 提供"单损失 / 单优化器 / 单数据源"的最小训练循环，其他能力（checkpointing、logging 等）通过 `HookBase` 系统实现。
3. **DefaultTrainer 的定位**：`DefaultTrainer` 是基于 config 初始化的 `SimpleTrainer`，被 `tools/train_net.py` 与许多脚本采用，内置 optimizer、学习率策略、日志、评估、checkpoint 等默认行为。
4. **DefaultTrainer 自定义的两条路径**：
   - 简单自定义（换 optimizer、evaluator、LR scheduler、数据加载器等）：通过子类重写 `DefaultTrainer` 的方法实现，参考 `tools/train_net.py`。
   - 复杂自定义：先看 `HookBase` 是否支持；不支持则从 `tools/plain_train_net.py` 出发手写训练逻辑。
5. **指标日志统一出口**：`EventStorage` 是 detectron2 模型与 trainer 集中存放训练指标的场所，模型可通过 `get_event_storage()` 获取并调用 `put_scalar()` 写入。
6. **指标的多目标写出**：`EventWriter` 负责把 `EventStorage` 中的指标写到多个目标，`DefaultTrainer` 默认启用了一组 `EventWriter`，并支持自定义。

---

## 【关键机制与数据】

- **自定义训练循环的数据流**（原文："With a model and a data loader ready, everything else needed to write a training loop can be found in PyTorch"）：用户拿到 model 与 data loader 之后，剩下的训练循环代码直接用 PyTorch 即可，"This style allows researchers to manage the entire training logic more clearly and have full control." 原文示例入口为 `tools/plain_train_net.py`。
- **Trainer 抽象层的工作原理**（原文："We also provide a standarized 'trainer' abstraction with a hook system that helps simplify the standard training behavior."）：detectron2 提供带 hook 系统的标准 trainer 抽象，用于简化标准训练行为。其两种具体实现为 `SimpleTrainer`（最小循环）和 `DefaultTrainer`（基于 config、含更多默认行为）。
- **Hook 系统的设计意图**（原文："Other tasks (checkpointing, logging, etc) can be implemented using the hook system."）：通过 `HookBase`，把 checkpointing、logging 等"非训练核心"任务以 hook 形式插入训练流程。
- **指标日志的数据流**（原文："During training, detectron2 models and trainer put metrics to a centralized EventStorage. You can use the following code to access it and log metrics to it"）：训练过程中，模型与 trainer 把指标集中放入 `EventStorage`；指标最终由 `EventWriter` 写到"various destinations"（原文："Metrics are then written to various destinations with EventWriter"），`DefaultTrainer` 默认启用了一组 `EventWriter`。

> 注：原文档未给出任何性能数字（如 mAP、训练时长、batch size、显存占用等）。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末链接梳理模块间的上下游与平行关系：

- **入口脚本 ↔ Trainer 类**：
  - `tools/plain_train_net.py` ↔ `SimpleTrainer`：作为"自写训练循环"范式的示例入口，演示不依赖标准 trainer 的最小实现。
  - `tools/train_net.py` ↔ `DefaultTrainer`：`train_net.py` 使用基于 config 的 `DefaultTrainer`，是"Trainer 抽象"范式的默认入口。
- **Trainer ↔ Hook 系统**：
  - `SimpleTrainer` ↔ `HookBase`：当 `SimpleTrainer` 只提供最小循环时，checkpointing、logging 等能力通过 `HookBase` 系统扩展。
  - `DefaultTrainer` ↔ `HookBase`：在 `DefaultTrainer` 仍不能覆盖的复杂定制场景下，先尝试 `HookBase`，失败再退回手写（`plain_train_net.py`）。
- **Trainer ↔ 日志体系**：
  - `DefaultTrainer` ↔ `EventStorage`：训练过程中模型和 trainer 将指标 put 到 `EventStorage`。
  - `EventStorage` ↔ `EventWriter`：指标从 `EventStorage` 经 `EventWriter` 写出到多个目标；`DefaultTrainer` 默认启用一组 `EventWriter`。
- **模型 ↔ 日志体系**：
  - 用户模型（通过 `get_event_storage()`）↔ `EventStorage`：模型可在 `self.training` 分支内调用 `storage.put_scalar("some_accuracy", value)` 写入标量指标，构成"模型侧"的指标产出端。
- **自定义层次（由浅到深）**：子类重写 `DefaultTrainer` 方法 → 在 `DefaultTrainer` 上启用 hook → 基于 `plain_train_net.py` 全手写，构成文档给出的三档"自定义深度"。

---

## 【使用方法】

文档原文涉及的方法与配置项如下（均为代码片段、命令或语义层面的提示，未给出具体超参数值）：

1. **走"自定义训练循环"路线**：参考并仿照 `tools/plain_train_net.py` 自己实现训练循环（"One such example is provided in tools/plain_train_net.py"）。
2. **走"Trainer 抽象"路线（最小化）**：使用 `SimpleTrainer`（"a minimal training loop for single-cost single-optimizer single-data-source training, with nothing else"），并按需叠加 `HookBase` 实现 checkpointing、logging 等。
3. **走"Trainer 抽象"路线（默认）**：使用 `DefaultTrainer`，由 config 初始化，配套脚本为 `tools/train_net.py`；默认已包含 optimizer、学习率策略、logging、evaluation、checkpointing 等行为。
4. **简单自定义 DefaultTrainer**（原文："For simple customizations (e.g. change optimizer, evaluator, LR scheduler, data loader, etc.), overwrite its methods in a subclass, just like tools/train_net.py."）：通过子类化并重写对应方法，换掉 optimizer / evaluator / LR scheduler / data loader 等。
5. **复杂自定义时的回退路径**（原文："For more complicated tasks during training, see if the hook system can support it, or start from tools/plain_train_net.py to implement the training logic manually."）：先看 hook 系统能否支持；不行就从 `plain_train_net.py` 出发手写。
6. **在模型中记录指标**（原文代码片段）：

```python
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
  value = # compute the value from inputs
  storage = get_event_storage()
  storage.put_scalar("some_accuracy", value)
```

即在 `self.training` 条件下计算值，通过 `get_event_storage()` 取得 `EventStorage`，再用 `put_scalar(name, value)` 写入标量指标。

7. **自定义指标写出目标**（原文："DefaultTrainer enables a few EventWriter with default configurations. See above for how to customize them."）：默认 `DefaultTrainer` 已启用若干 `EventWriter`，可通过上文提到的"子类重写"路径进行自定义；具体如何改写 EventWriter 的配置，原文未涉及。
