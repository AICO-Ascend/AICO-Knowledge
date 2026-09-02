# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/training.md

## 【定位】

这篇文档解决如何从已有的自定义模型和数据加载器开始，在 detectron2 中选择并定制训练流程，同时说明训练指标如何集中记录并输出。

## 【技术要点】

1. **自定义训练循环**：模型和数据加载器准备好后，可以使用 PyTorch 自行编写训练逻辑；`tools/plain_train_net.py` 提供了一个示例，用户可以完整控制训练流程。

2. **Trainer 抽象**：文档提供带 hook 系统的标准化 `trainer` 抽象，用于简化标准训练行为，并包含两种实例化形式：

   - `SimpleTrainer`：仅提供单成本函数、单优化器、单数据源训练的最小训练循环。
   - `DefaultTrainer`：从配置初始化的 `SimpleTrainer`，由 `tools/train_net.py` 及许多脚本使用。

3. **`SimpleTrainer` 与 hook 的分工**：`SimpleTrainer` 本身不提供额外功能；检查点保存、日志记录等任务可以通过 `HookBase` hook 系统实现。

4. **`DefaultTrainer` 的默认行为**：它包含可选择的标准化默认配置，涵盖优化器、学习率调度、日志记录、评估和检查点保存等行为。

5. **训练定制方式**：
   - 简单定制：覆盖 `DefaultTrainer` 的方法，例如修改优化器、评估器、LR 调度器或数据加载器。
   - 复杂训练逻辑：先判断 hook 系统是否支持；不支持时，从 `tools/plain_train_net.py` 开始手动实现。

6. **指标集中记录**：模型和 trainer 将指标放入统一的 `EventStorage`；可以通过 `get_event_storage()` 获取存储对象，并使用 `storage.put_scalar("some_accuracy", value)` 写入标量指标，之后由 `EventWriter` 写入不同的输出目标。

## 【关键机制与数据】

### 1. 两种训练流程

原文给出两种训练风格：

- **Custom Training Loop**：用户自行组织训练逻辑，获得对训练过程和定制行为的完全控制。
- **Trainer Abstraction**：使用标准化的 trainer 抽象和 hook 系统，减少实现标准训练行为的负担。

### 2. 训练器层级关系

原文描述的调用与扩展关系为：

```text
SimpleTrainer
    ↓ initialized from a config
DefaultTrainer
    ↓ used by
tools/train_net.py and many scripts
```

`DefaultTrainer` 在 `SimpleTrainer` 的基础上增加默认的优化器、学习率调度、日志、评估和检查点等行为。

### 3. 指标数据流

原文中的指标流向为：

```text
model / trainer
    ↓ put metrics
EventStorage
    ↓
EventWriter
    ↓
various destinations
```

其中，模型侧可以按照原文代码在训练状态下计算指标值，并写入统一的指标存储：

```python
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
  value = # compute the value from inputs
  storage = get_event_storage()
  storage.put_scalar("some_accuracy", value)
```

### 4. 定制与升级路径

- 简单需求：通过覆盖 `DefaultTrainer` 方法完成定制。
- 超出标准 trainer 或 hook 支持范围的需求：使用 `tools/plain_train_net.py` 手动实现训练逻辑。

### 5. 性能与配置数据

原文：本文未提供训练结果、准确率、损失值、训练时间或性能对比等数据；仅说明了 `DefaultTrainer` 具备优化器、学习率调度、日志、评估和检查点等默认行为。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

1. **前序教程中的模型与数据加载器**  
   本文档以“已经拥有自定义模型和数据加载器”为前提，讨论训练流程的选择与定制。

2. **自定义循环与示例脚本**  
   自定义训练循环的自由实现方式与以下脚本直接关联：

   - [tools/plain_train_net.py](../../tools/plain_train_net.py)：提供一个自定义训练循环示例。
   - [SimpleTrainer](../modules/engine.html#detectron2.engine.SimpleTrainer)：提供最小训练循环。
   - [HookBase](../modules/engine.html#detectron2.engine.HookBase)：通过 hook 系统补充检查点保存、日志记录等非核心训练行为。

3. **`DefaultTrainer` 与训练入口**  
   [DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 是从配置初始化的 `SimpleTrainer`，并被 [tools/train_net.py](../../tools/train_net.py) 以及许多脚本使用。它集中提供优化器、学习率调度、日志记录、评估、检查点等默认行为。

4. **定制行为的两个层次**  
   - 简单定制通过覆盖 `DefaultTrainer` 方法完成。
   - 复杂训练逻辑先尝试 hook 系统；无法支持时，回到自定义训练循环。

5. **指标存储与输出**  
   训练模型或 trainer 将指标放入 [EventStorage](../modules/utils.html#detectron2.utils.events.EventStorage)，再由 [EventWriter](../modules/utils.html#module-detectron2.utils.events) 将指标写入不同目标。`DefaultTrainer` 默认启用若干个 `EventWriter`，并支持对这些输出行为进行定制。

## 【使用方法】

### 使用自定义训练循环

准备好模型和数据加载器后，按照 PyTorch 训练逻辑自行组织训练过程。原文提供的参考实现为：

- [tools/plain_train_net.py](../../tools/plain_train_net.py)

### 使用 `SimpleTrainer`

`SimpleTrainer` 用于单成本函数、单优化器、单数据源的最小训练循环：

- [SimpleTrainer](../modules/engine.html#detectron2.engine.SimpleTrainer)

检查点保存和日志记录等额外任务需要通过 hook 系统实现：

- [HookBase](../modules/engine.html#detectron2.engine.HookBase)

### 使用 `DefaultTrainer`

`DefaultTrainer` 从配置初始化，包含以下默认行为：

- 优化器
- 学习率调度
- 日志记录
- 评估
- 检查点保存

相关实现和使用入口：

- [DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer)
- [tools/train_net.py](../../tools/train_net.py)

### 定制 `DefaultTrainer`

对于简单定制，在 `DefaultTrainer` 子类中覆盖其方法，例如修改：

- 优化器
- 评估器
- LR 调度器
- 数据加载器

对于更复杂的训练任务，先检查 hook 系统是否支持；如果不支持，则从 [tools/plain_train_net.py](../../tools/plain_train_net.py) 开始手动实现训练逻辑。

### 记录训练指标

在模型内部使用以下代码将训练指标写入集中存储：

```python
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
  value = # compute the value from inputs
  storage = get_event_storage()
  storage.put_scalar("some_accuracy", value)
```

随后，`EventWriter` 会将指标写入各种输出目标。原文未提供具体的训练启动命令、配置文件片段或参数表。
