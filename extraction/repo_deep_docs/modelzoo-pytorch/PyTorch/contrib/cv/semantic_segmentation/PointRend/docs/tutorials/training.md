# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/training.md

# 深度解读：PointRend · Training 教程

---

## 【定位】

本文是 detectron2（PointRend 所依赖的底层训练框架）中"训练"环节的教程文档，定位为：**在用户已具备自定义模型与数据加载器之后，介绍两种启动训练的方式（自定义训练循环 vs Trainer 抽象），并讲解如何通过 Hook 与 EventStorage 机制进行定制与指标记录**。

---

## 【技术要点】

1. **两种训练风格并存**：文档明确将训练方式分为"Custom Training Loop（自定义训练循环）"与"Trainer Abstraction（Trainer 抽象）"两类，前者赋予研究者对训练逻辑的完全控制，后者以标准化的方式简化常规训练。
2. **SimpleTrainer 的最小化定位**：原文描述其为"single-cost single-optimizer single-data-source training, with nothing else"，即仅承担最朴素循环，其它能力（如 checkpointing、logging）通过 Hook 系统补齐。
3. **DefaultTrainer 的 yacs 配置驱动**：原文指出 DefaultTrainer 是"a `SimpleTrainer` initialized from a yacs config"，并由 `tools/train_net.py` 及多个脚本直接使用；默认包含 optimizer、learning rate schedule、logging、evaluation、checkpointing 等标准行为。
4. **Hook 系统的层级定位**：原文用一句关键判断——"we intentionally keep the trainer & hook system minimal, rather than powerful"——明确了该系统的设计哲学：当超出其能力范围时，更简单的做法是直接基于 `tools/plain_train_net.py` 手写训练逻辑。
5. **EventStorage 作为指标中枢**：训练中模型与 trainer 将指标放入集中的 `EventStorage`，可通过 `detectron2.utils.events.get_event_storage()` 获取实例，并调用 `storage.put_scalar("name", value)` 写入标量。
6. **EventWriter 负责指标分发**：原文指出"Metrics are then written to various destinations with `EventWriter`"，且 `DefaultTrainer` 默认启用若干 `EventWriter`；这一点确立了 EventStorage（写入端）→ EventWriter（写出端）的解耦结构。

---

## 【关键机制与数据】

### 工作原理与数据流

**1. 自定义训练循环路径**
- 输入：用户自定义的 model 与 data loader。
- 流程：用户在 PyTorch 层面自行编排训练循环，原文示例参考 `tools/plain_train_net.py`。
- 特性：可读性高、控制粒度最细；任何训练逻辑的定制都直接由用户掌握。

**2. Trainer 抽象路径**
- 输入：yacs 配置（仅 `DefaultTrainer` 需要）+ model + data loader。
- 流程：`DefaultTrainer` 内部组合 `SimpleTrainer` + 默认 Hook/Writer；可通过两种方式定制：
  - 子类化重写方法（用于简单定制：optimizer、evaluator、LR scheduler、data loader 等）；
  - 注册 Hook（用于训练过程中的额外任务）。
- 限制：原文明确指出该系统有意保持"minimal"，超出范围时建议回到 `plain_train_net.py`。

**3. Hook 机制的工作时机**（原文代码示例）
```python
class HelloHook(HookBase):
  def after_step(self):
    if self.trainer.iter % 100 == 0:
      print(f"Hello at iteration {self.trainer.iter}!")
```
- 时机：`after_step()` 在每个训练 step 后被调用。
- 触发频率判定：`self.trainer.iter % 100 == 0`，即每 100 个 iteration 触发一次。
- 原文（性能/数据点）：**原文未提供任何具体性能数字或基准数据**。

**4. 指标写入链路**
- 模型端：在 `self.training` 为真时计算指标 → `storage = get_event_storage()` → `storage.put_scalar("some_accuracy", value)`。
- 写出端：`EventWriter`（模块 `detectron2.utils.events`）将指标写入"various destinations"；`DefaultTrainer` 默认启用部分 `EventWriter`。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

以下关系完全基于原文文本与文末内部链接推断，未引入原文未明说的事实：

- **`tools/plain_train_net.py`**（`../../tools/plain_train_net.py`）：
  - 是"Custom Training Loop"风格的示例实现；
  - 也是当 trainer+hook 不足以承载自定义逻辑时，原文建议"从头开始实现自定义训练逻辑"的起点（"it's easier to start from tools/plain_train_net.py to implement custom training logic manually"）。

- **`tools/train_net.py`**（`../../tools/train_net.py`）：
  - 是 `DefaultTrainer` 的典型使用者（"used by tools/train_net.py and many scripts"）；
  - 同时也是"`DefaultTrainer` 简单定制——子类化重写方法"的示例参考。

- **`detectron2.engine.SimpleTrainer`**（`../modules/engine.html#detectron2.engine.SimpleTrainer`）：
  - 提供"single-cost single-optimizer single-data-source"的最小训练循环；
  - 是 `DefaultTrainer` 的直接父类（"a `SimpleTrainer` initialized from a yacs config"）。

- **`detectron2.engine.defaults.DefaultTrainer`**（`../modules/engine.html#detectron2.engine.defaults.DefaultTrainer`）：
  - 是用户面向的主入口，包含 optimizer/LR schedule/logging/evaluation/checkpointing 等默认行为；
  - 与 `SimpleTrainer`、`tools/train_net.py`、`EventStorage`/`EventWriter` 都有上下游依赖。

- **`detectron2.engine.HookBase`**（`../modules/engine.html#detectron2.engine.HookBase`）：
  - 提供 hook 系统基类（`HelloHook(HookBase)` 示例所继承）；
  - 被 `SimpleTrainer` 与 `DefaultTrainer` 用于在训练过程中插入额外任务（checkpointing、logging 等"other tasks"即通过它实现）。

- **`detectron2.utils.events.EventStorage`**（`../modules/utils.html#detectron2.utils.events.EventStorage`）：
  - 是训练期间指标的中枢存储；
  - 通过 `get_event_storage()` 访问，通过 `put_scalar("name", value)` 写入；
  - 由 model 和 trainer 共同写入。

- **`detectron2.utils.events` 模块（含 `EventWriter`）**（`../modules/utils.html#module-detectron2.utils.events`）：
  - 负责把 `EventStorage` 中的指标"written to various destinations"；
  - `DefaultTrainer` 启用了若干带默认配置的 `EventWriter`，可通过子类化方式定制。

总体关系图（按原文措辞）：

```
plain_train_net.py  ──示例──▶  Custom Training Loop（用户自管）
                                          ▲
                                          │  "无法支持时退回"
                                          │
DefaultTrainer ───继承───▶ SimpleTrainer（最小循环）
       │                       ▲
       │使用                    │扩展
       ▼                       │
train_net.py ─────────▶  HookBase（after_step 等钩子）
       │
       ▼
EventStorage（指标中枢） ──分发──▶ EventWriter（写向各类目的地）
```

---

## 【使用方法】

### A. 启用"自定义训练循环"
- 直接编写自己的训练循环，参考 `tools/plain_train_net.py`；不依赖 `DefaultTrainer` 或 Hook。

### B. 启用"Trainer 抽象"
- 使用 `DefaultTrainer` 时：传入 yacs 配置即可；脚本可参考 `tools/train_net.py`。

### C. 定制 `DefaultTrainer` 的三种路径（原文逐条编号）
1. **简单定制**（如改 optimizer、evaluator、LR scheduler、data loader）：在子类中**重写其方法**，方式与 `tools/train_net.py` 一致。
2. **训练中插入额外任务**：检查 `HookBase` 是否已支持；若否，自定义 Hook 类并注册。
3. **当 trainer+hook 不够用时**：原文建议"start from `tools/plain_train_net.py` to implement custom training logic manually"。

### D. 自定义 Hook 示例（原文逐字保留）
```python
class HelloHook(HookBase):
  def after_step(self):
    if self.trainer.iter % 100 == 0:
      print(f"Hello at iteration {self.trainer.iter}!")
```
- 触发点：每 100 个 iteration（`self.trainer.iter % 100 == 0`）。
- 访问当前训练状态：通过 `self.trainer.iter`。

### E. 写入指标到 `EventStorage`（原文逐字保留）
```python
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
  value = # compute the value from inputs
  storage = get_event_storage()
  storage.put_scalar("some_accuracy", value)
```
- 约束：仅在 `self.training` 为真时写入（避免评估阶段污染训练指标）。
- 写入方式：`put_scalar(name, value)`，示例键名为 `"some_accuracy"`。

### F. 定制 `EventWriter`
- 原文未给出具体代码；
- 原文仅说明："`DefaultTrainer` enables a few `EventWriter` with default configurations. See above for how to customize them."——即定制方式与上文 `DefaultTrainer` 的子类化路径一致。

### G. 命令行/CLI 参数
- **原文未涉及**具体的 CLI 命令、参数名或 shell 用法。
