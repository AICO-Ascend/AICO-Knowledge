# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/training.md

# 深度解读：detectron2 Training 教程

## 【定位】
本文档解决 detectron2 模型训练中的**训练循环组织方式选择**问题：介绍两种训练风格（自定义训练循环 vs. Trainer 抽象层），并说明如何通过继承 `DefaultTrainer`、注册 `HookBase` 子类或使用 `EventStorage` 来定制和观察训练过程。

---

## 【技术要点】

1. **两种训练风格并存**——detectron2 同时提供"Custom Training Loop"（用户自行用 PyTorch 写训练循环，模型与数据加载器之外的逻辑自行实现）和"Trainer Abstraction"（带 hook 系统的标准化抽象）两条路线，研究人员可按需取舍。
2. **`SimpleTrainer` 是极简训练循环**——定位为"single-cost single-optimizer single-data-source"，不内置 checkpointing、logging 等其它行为，全部委托给 hook 系统实现。
3. **`DefaultTrainer` 是 yacs 配置驱动的 `SimpleTrainer`**——由 `tools/train_net.py` 及大多数脚本使用，预置 optimizer、learning rate schedule、logging、evaluation、checkpointing 等默认行为。
4. **`DefaultTrainer` 定制三步法**——(a) 简单定制（换 optimizer、evaluator、LR scheduler、data loader）通过子类覆写其方法实现；(b) 额外任务通过 hook 系统；(c) 满足不了的极端场景回退到 `plain_train_net.py` 手写。
5. **`HookBase` 通过重写生命周期方法插入行为**——示例 `HelloHook.after_step` 在 `self.trainer.iter % 100 == 0` 时打印 "Hello at iteration {iter}!"，体现"按步插入"的标准模式。
6. **`EventStorage` 提供集中式指标读写**——模型内部通过 `get_event_storage()` 取得单例，调用 `storage.put_scalar("some_accuracy", value)` 上报指标；`EventWriter` 负责把指标写入多种目的地。

---

## 【关键机制与数据】

**训练循环的两条路径（原文："two styles"）**：
- **Custom Training Loop**：原句说明"everything else needed to write a training loop can be found in PyTorch, and you are free to write the training loop yourself"，对应的实现模板在 `tools/plain_train_net.py`；好处是 "manage the entire training logic more clearly and have full control"。
- **Trainer Abstraction**：原句给出 hook 系统的目标——"helps simplify the standard training behavior"，并刻意保持极简 "we intentionally keep the trainer & hook system minimal, rather than powerful"。

**`SimpleTrainer` 与 `DefaultTrainer` 的关系（原文："`DefaultTrainer` is a `SimpleTrainer` initialized from a yacs config"）**：
- `SimpleTrainer` 提供"minimal training loop"，外加能力全靠 hook 补齐。
- `DefaultTrainer` 在此基础上加入"default configurations for optimizer, learning rate schedule, logging, evaluation, checkpointing etc."。

**Hook 触发频率（原文代码）**：
```python
class HelloHook(HookBase):
  def after_step(self):
    if self.trainer.iter % 100 == 0:
      print(f"Hello at iteration {self.trainer.iter}!")
```
原文中"100"作为示例触发周期，由 `self.trainer.iter` 读取当前迭代计数并取模。

**指标流向（原文："a centralized EventStorage"）**：
1. 模型在 `self.training` 状态下计算指标 value；
2. `storage = get_event_storage()` 取得集中存储；
3. `storage.put_scalar("some_accuracy", value)` 写入；
4. `EventWriter`（默认随 `DefaultTrainer` 启用若干个）将指标落到具体目的地。

**定制边界（原文）**：原文明确"there will always be some non-standard behaviors that cannot be supported"，因此保留 `plain_train_net.py` 作为完全自定义的退路。

---

## 【表格解读】

**原文无表格**。文档以叙述与代码片段为主，未包含参数表、性能对比或配置矩阵。

---

## 【公式解读】

**原文无公式**。文档仅出现一段 Python 代码（Hook 子类）与一段 logging 用法代码，不含数学公式或伪代码算法。

---

## 【关联】

依据文末内部链接梳理的上下游依赖关系：

- **`tools/plain_train_net.py`**：自定义训练循环范式的参考实现；同时也是当 Trainer+Hook 无法覆盖需求时的"白板起点"（原文："it's easier to start from tools/plain_train_net.py to implement custom training logic manually"）。
- **`detectron2.engine.SimpleTrainer`**：`DefaultTrainer` 的基类，提供最简训练循环；任何额外行为需通过 `HookBase` 注入。
- **`detectron2.engine.HookBase`**：hook 系统的基类；`HelloHook.after_step` 即继承自它；`DefaultTrainer` 的 checkpoint、logging、evaluation 等默认行为均通过 hook 形式组装。
- **`detectron2.engine.defaults.DefaultTrainer`**：`SimpleTrainer` 的子类，初始化来自 yacs config；定制方式分两条：(a) 子类覆写方法（如 `train_net.py` 所示）；(b) 注册新 Hook。
- **`tools/train_net.py`**：使用 `DefaultTrainer` 的脚本示例，同时是 `DefaultTrainer` 子类覆写这一定制手法的范例。
- **`detectron2.utils.events.EventStorage`**：训练过程中所有指标的中枢存储；模型通过 `get_event_storage()` 读取并 `put_scalar(...)` 写入；下游由 `EventWriter` 写出。
- **`detectron2.utils.events.EventWriter`**（`../modules/utils.html#module-detectron2.utils.events`）：把 `EventStorage` 中的指标分发到不同目的地；`DefaultTrainer` 默认启用若干 `EventWriter`，与"Logging of Metrics"章节直接相关。

整体可视为：**`plain_train_net.py` ⇄（对照）⇄ `DefaultTrainer`（继承 `SimpleTrainer`，由 yacs 装配）+ `HookBase`（扩展点）⇄ `EventStorage`（指标中枢）⇄ `EventWriter`（落盘/可视化）**。

---

## 【使用方法】

原文给出的具体使用方法与命令如下：

1. **走自定义循环**：参考 [`tools/plain_train_net.py`](../../tools/plain_train_net.py) 的写法，在已具备模型和数据加载器后自行组织训练。
2. **走 Trainer 抽象**：
   - 直接使用 [`DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer)（yacs 配置驱动），或参照 [`tools/train_net.py`](../../tools/train_net.py) 继承覆写其方法以更换 optimizer / evaluator / LR scheduler / data loader 等。
   - 通过 [`HookBase`](../modules/engine.html#detectron2.engine.HookBase) 添加额外任务，例如：
     ```python
     class HelloHook(HookBase):
       def after_step(self):
         if self.trainer.iter % 100 == 0:
           print(f"Hello at iteration {self.trainer.iter}!")
     ```
   - 若 trainer + hook 仍无法满足需求，回退到 [`plain_train_net.py`](../../tools/plain_train_net.py) 手写训练逻辑。
3. **记录训练指标**：在模型内部（`self.training` 为真时）计算值后，写入 [`EventStorage`](../modules/utils.html#detectron2.utils.events.EventStorage)：
   ```python
   from detectron2.utils.events import get_event_storage

   # inside the model:
   if self.training:
     value = # compute the value from inputs
     storage = get_event_storage()
     storage.put_scalar("some_accuracy", value)
   ```
   指标落地由 `EventWriter` 完成；`DefaultTrainer` 默认启用若干 `EventWriter`，可在该文档上文所述的定制入口处调整。

原文未涉及具体的命令行调用、参数取值或配置文件项写法。
