# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/training.md

# CascadedMaskRCNN / docs/tutorials/training.md 深度解读

---

## 【定位】

本文档是 detectron2（被 CascadedMaskRCNN 作为基础框架使用）训练流程的入门引导文档，核心解决"用户拿到自定义模型和数据加载器之后，应当如何组织训练逻辑、如何在标准流程与完全自定义之间做取舍、如何记录训练指标"的问题。

---

## 【技术要点】

1. **两种训练风格并存**：文档明确把训练入口划分为"自定义训练循环（Custom Training Loop）"与"训练器抽象（Trainer Abstraction）"两类，用户可按需选择。
2. **SimpleTrainer 定位**：被定义为"minimal training loop for **single-cost single-optimizer single-data-source** training, with nothing else"，仅承载最基本的训练循环，其余能力（checkpointing、logging 等）由 hook 系统补齐。
3. **DefaultTrainer 定位**：是 SimpleTrainer 的"从 config 初始化"版本，被 `tools/train_net.py` 及多数脚本使用；默认包含 optimizer、learning rate schedule、logging、evaluation、checkpointing 等标准行为。
4. **DefaultTrainer 的两种定制路径**：
   - 路径 A：**简单定制**（如改 optimizer、evaluator、LR scheduler、data loader）—— 在子类中**覆写（overwrite）其方法**，参考 `tools/train_net.py`。
   - 路径 B：**复杂定制**—— 优先看 hook 系统能否支持，若不能则从 `tools/plain_train_net.py` 起步手动实现训练逻辑。
5. **Hook 系统的边界**：文档原文明示"there will always be some non-standard behaviors that cannot be supported, especially in research"，即 hook 不是万能的，研究型需求超出 hook 覆盖时应回到 plain 训练脚本。
6. **指标集中存储**：训练中模型和 trainer 把指标统一放入集中的 `EventStorage`；模型内部可通过 `storage.put_scalar("some_accuracy", value)` 写入标量。
7. **指标落盘**：通过 `EventWriter` 写到多个目的地（destinations），`DefaultTrainer` 默认启用若干 `EventWriter` 并提供默认配置。

---

## 【关键机制与数据】

> 说明：原文为引导性叙述，未给出任何性能数字、参数量或基准测试结果；本节只梳理机制性信息。

- **Custom Training Loop 的工作机制**（原文）：
  > "everything else needed to write a training loop can be found in PyTorch, and you are free to write the training loop yourself."
  - 即不依赖 detectron2 的 trainer，写法完全交给用户，参考实现见 [`tools/plain_train_net.py`](../../tools/plain_train_net.py)。
  - 优势：researcher 可"manage the entire training logic more clearly and have full control"，并能"easily controlled by the user"地定制任意训练逻辑。

- **Trainer Abstraction 的工作机制**（原文）：
  - 由 SimpleTrainer + Hook 系统组成。
  - SimpleTrainer 提供"最小可用循环"，其他任务（checkpointing、logging 等）通过 [HookBase](../modules/engine.html#detectron2.engine.HookBase) 实现。
  - DefaultTrainer 在 SimpleTrainer 基础上加载默认配置，是 [`tools/train_net.py`](../../tools/train_net.py) 与"many scripts"的实际依赖。

- **指标记录与落盘的数据流**（原文 + 代码示例）：
  1. 模型在 `self.training` 为 True 时计算指标；
  2. 通过 `get_event_storage()` 取得当前 EventStorage；
  3. 调用 `storage.put_scalar("some_accuracy", value)` 把标量写入；
  4. 默认的若干 `EventWriter` 将其分发到各目的地。

  原文中给出的代码片段逐字保留：

  ```
  from detectron2.utils.events import get_event_storage

  # inside the model:
  if self.training:
    value = # compute the value from inputs
    storage = get_event_storage()
    storage.put_scalar("some_accuracy", value)
  ```

- **性能数据**：原文未提供任何性能/精度/速度数据。

---

## 【表格解读】

**原文无表格。**

文档没有给出参数表、性能对比或配置项表格；其结构依赖段落 + 列表 + 代码片段呈现。

---

## 【公式解读】

**原文无公式。**

文档未出现任何 LaTeX 数学公式或伪代码形式的计算式。

---

## 【关联】

依据原文提到的链接与上下文，可梳理出如下依赖/调用关系：

| 原文提及的对象 | 角色 | 关联到的其他对象 |
|---|---|---|
| [`tools/plain_train_net.py`](../../tools/plain_train_net.py) | "Custom Training Loop" 风格的范例；也是"复杂定制"时手动实现的起点 | 与 [SimpleTrainer](../modules/engine.html#detectron2.engine.SimpleTrainer)、[DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 并列，是脱离 trainer 抽象的退路 |
| [`SimpleTrainer`](../modules/engine.html#detectron2.engine.SimpleTrainer) | 最小训练循环（单 cost / 单 optimizer / 单 data source） | 通过 [HookBase](../modules/engine.html#detectron2.engine.HookBase) 扩展 checkpointing、logging 等能力 |
| [`HookBase`](../modules/engine.html#detectron2.engine.HookBase) | 训练行为扩展点（事件钩子） | 既服务于 SimpleTrainer 的能力补足，也是 DefaultTrainer 复杂定制的首选途径 |
| [`DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) | 从 config 初始化的标准 trainer，含 optimizer/LR/log/eval/ckpt 默认行为 | 被 [`tools/train_net.py`](../../tools/train_net.py) 使用；可被子类覆写做"简单定制" |
| [`tools/train_net.py`](../../tools/train_net.py) | 默认训练入口脚本；同时也是"如何子类化 DefaultTrainer"的范例 | 与 [DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer)、[plain_train_net.py](../../tools/plain_train_net.py) 形成对比 |
| [`EventStorage`](../modules/utils.html#detectron2.utils.events.EventStorage) | 训练期指标的集中存储（通过 `get_event_storage()` 访问） | 数据来源是模型内部；数据去向是 EventWriter |
| `EventWriter`（[events 模块](../modules/utils.html#module-detectron2.utils.events)） | 把 EventStorage 中的指标分发到多个目的地 | 由 DefaultTrainer 默认启用并提供默认配置，可被自定义 |

---

## 【使用方法】

> 以下仅记录原文**明确写出**的启用/配置方式；未在原文中出现的内容按指令标注。

- **启用训练循环（Custom 风格）**：直接以 [`tools/plain_train_net.py`](../../tools/plain_train_net.py) 为模板自行编写。原文未给出具体命令行参数或环境变量。

- **启用训练循环（Trainer 风格 / SimpleTrainer）**：使用 [SimpleTrainer](../modules/engine.html#detectron2.engine.SimpleTrainer) 作为最小训练循环，并通过 [HookBase](../modules/engine.html#detectron2.engine.HookBase) 自行挂载 checkpointing、logging 等行为。原文未给出具体调用签名。

- **启用训练循环（Trainer 风格 / DefaultTrainer）**：使用 [`tools/train_net.py`](../../tools/train_net.py) 或等价脚本，默认配置涵盖 optimizer、learning rate schedule、logging、evaluation、checkpointing。

- **DefaultTrainer 简单定制**（改 optimizer / evaluator / LR scheduler / data loader 等）：
  > "overwrite its methods in a subclass, just like `tools/train_net.py`."
  即继承 DefaultTrainer 并覆写对应方法。原文未给出具体方法名列表。

- **DefaultTrainer 复杂定制**：
  1. 先尝试 [HookBase](../modules/engine.html#detectron2.engine.HookBase) 是否能承载；
  2. 若不行，从 [`tools/plain_train_net.py`](../../tools/plain_train_net.py) 起步手动实现训练逻辑。

- **在模型内记录指标**（原文给出代码模板）：

  ```python
  from detectron2.utils.events import get_event_storage

  # inside the model:
  if self.training:
      value = # compute the value from inputs
      storage = get_event_storage()
      storage.put_scalar("some_accuracy", value)
  ```

- **配置 EventWriter**：DefaultTrainer 默认启用若干 EventWriter；如需自定义需参考 events 模块文档（原文仅说"See above for how to customize them"，未给出具体配置项/键名）。
