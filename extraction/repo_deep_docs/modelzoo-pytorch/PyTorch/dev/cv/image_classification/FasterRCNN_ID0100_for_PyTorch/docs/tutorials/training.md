# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/training.md

# 深度解读:`Training` 教程文档

## 【定位】
本教程文档面向已完成自定义模型与数据加载器的用户,系统性地介绍 detectron2 中两种组织训练循环的风格(完全自写循环 vs. Trainer 抽象层 + 钩子机制),并给出指标日志的接入方式,解决"训练逻辑如何编排与扩展"的问题。

---

## 【技术要点】

1. **两种训练范式并存**:detectron2 同时支持(a)用户基于 PyTorch 自由编写训练循环,以及(b)内置的 Trainer 抽象层(含 hook 系统),二者面向不同的可控性/便捷性权衡。
2. **Custom Training Loop 示例入口**:参考实现位于 `tools/plain_train_net.py`,任何训练逻辑定制都可由用户直接掌控。
3. **SimpleTrainer 定位**:仅提供"单损失函数 + 单优化器 + 单数据源"的最小训练循环,其余(checkpointing、logging 等)需通过 hook 系统补齐。
4. **DefaultTrainer 定位**:`SimpleTrainer` 的子类,由 config 初始化,是 `tools/train_net.py` 及多数脚本的实际驱动者,默认集成 optimizer、学习率调度、日志、评估、断点续训等"开箱即用"行为。
5. **DefaultTrainer 的两类定制路径**:简单定制(换 optimizer / evaluator / LR scheduler / data loader)通过子类覆写方法实现;复杂定制先看 `HookBase` 是否支持,否则回到 `plain_train_net.py` 手写训练逻辑。
6. **指标日志机制**:训练期间模型/Trainer 将指标写入中心化的 `EventStorage`,通过 `get_event_storage()` + `storage.put_scalar("name", value)` 写入;再由 `EventWriter` 把数据分发到各落地目标(Sink)。

---

## 【关键机制与数据】

- **原文:** SimpleTrainer 是"single-cost single-optimizer single-data-source"的最小训练循环,"with nothing else"——它不内置 checkpointing、logging 等横切关注点。
- **原文:** SimpleTrainer 的扩展点是通过 hook 系统(`HookBase`)实现的"other tasks (checkpointing, logging, etc)"。
- **原文:** DefaultTrainer 是"a `SimpleTrainer` initialized from a config",由 `tools/train_net.py` 启动,其默认行为包括 "default configurations for optimizer, learning rate schedule, logging, evaluation, checkpointing etc"。
- **数据流(原文):** 模型/Trainer → `EventStorage`(集中存放指标)→ `EventWriter`(将指标分发到各种 destinations,如 stdout、TensorBoard、文件等)。
- **原文指标 API 示例:**
  ```python
  from detectron2.utils.events import get_event_storage

  # inside the model:
  if self.training:
    value = # compute the value from inputs
    storage = get_event_storage()
    storage.put_scalar("some_accuracy", value)
  ```
  - 该示例展示了**仅在 `self.training` 为真时**才写指标的训练期判别;存储介质为单例 `EventStorage`,通过字符串键(`"some_accuracy"`)登记标量。
- **原文:** "DefaultTrainer enables a few `EventWriter` with default configurations",即 DefaultTrainer 已默认启用若干 `EventWriter`,定制方式需"see above"。

> 原文未给出任何性能/精度/速度等量化指标,以上为文档实际出现的内容。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

本教程位于训练编排层,与 detectron2 其他模块的关系(均来自文末链接):

- **`tools/plain_train_net.py`** —— Custom Training Loop 范式的参考实现;也是当 `DefaultTrainer` + hook 仍无法满足复杂定制需求时的"回退起点"。
- **`detectron2.engine.SimpleTrainer`** —— Trainer 抽象层的最小核心:`DefaultTrainer` 的父类,被 `tools/train_net.py` 间接驱动。
- **`detectron2.engine.HookBase`** —— 在 Trainer 范式中,负责将 checkpointing、logging 等横切行为以 hook 方式挂入 `SimpleTrainer`;也是 `DefaultTrainer` 复杂定制的扩展点。
- **`detectron2.engine.defaults.DefaultTrainer`** —— `SimpleTrainer` 的 config 化封装,与 `tools/train_net.py` 紧耦合,是教程中"先用 DefaultTrainer 子类覆写、再考虑 hook/回到 plain 训练脚本"的中央枢纽。
- **`tools/train_net.py`** —— 实际调用 `DefaultTrainer` 的脚本入口,既是 DefaultTrainer 的使用样例,也是教程建议作为简单定制起点的参考实现。
- **`detectron2.utils.events.EventStorage`** —— 训练期指标中心仓库;教程给出的 `get_event_storage()` + `put_scalar` API 即对接此处。
- **`detectron2.utils.events.EventWriter`(模块 `module-detectron2.utils.events`)** —— `EventStorage` 的下游消费者,把指标分发到不同目的地;DefaultTrainer 默认启用若干实例。

整体可视为:训练入口(`train_net.py` / `plain_train_net.py`)→ 训练循环(`SimpleTrainer` / `DefaultTrainer`)→ 扩展机制(`HookBase`)→ 指标管线(`EventStorage` → `EventWriter`),其中本文档是连接"循环层"与"指标层"的指南。

---

## 【使用方法】

**A. 选择训练风格**
- 想完全掌控训练细节 → 自写循环,参考 [`plain_train_net.py`](../../tools/plain_train_net.py)。
- 想要标准行为(optimizer/LR/log/eval/checkpoint)开箱即用 → 使用 [`DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer),最便捷的方式是直接跑 [`train_net.py`](../../tools/train_net.py)。

**B. 定制 DefaultTrainer(原文给出的步骤)**
1. **简单定制**:在子类中覆写其方法(如 optimizer、evaluator、LR scheduler、data loader 等),实现方式参考 [`train_net.py`](../../tools/train_net.py)。
2. **复杂定制**:先评估 [`HookBase`](../modules/engine.html#detectron2.engine.HookBase) 是否能承载需求;若仍不足,放弃 Trainer 抽象,从 [`plain_train_net.py`](../../tools/plain_train_net.py) 起手手写训练逻辑。

**C. 在模型中记录指标(原文给出的代码)**
```python
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
  value = # compute the value from inputs
  storage = get_event_storage()
  storage.put_scalar("some_accuracy", value)
```
- 调用时机需在 `self.training == True` 时。
- 通过 `get_event_storage()` 获取单例 `EventStorage`,以字符串名为键、`put_scalar` 写标量。

**D. 自定义指标的落地方式(原文未给出具体命令/参数)**
- 文档仅指明 "DefaultTrainer enables a few `EventWriter` with default configurations",并提示 "See above for how to customize them";具体配置项/命令属其他章节,本文未涉及。

> 原文未提供具体的命令行启动方式(如 `python train_net.py ...` 的具体 flag)、超参与配置键名,均需结合仓库内 `train_net.py` 与 config 系统查阅。
