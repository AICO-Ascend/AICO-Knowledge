# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/training.md

# 一体化深度解读: PyTorch/contrib/cv/detection/centernet2/docs/tutorials/training.md

---

## 【定位】

这篇文档解决**"在 detectron2 框架下,用户应当如何组织目标检测模型的训练流程"**的问题——明确给出了两种并列的训练组织风格(自定义训练循环 vs. Trainer 抽象),并指明在何种场景下应选择哪种风格、如何以最小成本定制 `DefaultTrainer`、如何利用 hook 机制注入额外行为、以及如何把训练指标写入框架的集中式事件存储系统。

---

## 【技术要点】

1. **两种互斥但互补的训练风格**
   - 自定义训练循环 (Custom Training Loop): 基于已有的 `model` 与 `data loader`,直接用 PyTorch 写循环,示例见 `tools/plain_train_net.py`。
   - Trainer 抽象 (Trainer Abstraction): 框架提供 `SimpleTrainer` 与 `DefaultTrainer`,叠加 hook 系统,简化标准训练行为。

2. **`SimpleTrainer` 的最小化定位**
   - 原文: "provides a minimal training loop for single-cost single-optimizer single-data-source training, with nothing else"。
   - 其他任务(checkpointing、logging 等)需通过 hook 系统实现。

3. **`DefaultTrainer` 的"开箱即用"配置范围**
   - 原文明确列出: optimizer、learning rate schedule、logging、evaluation、checkpointing 五类默认配置。
   - 由 config 初始化,被 `tools/train_net.py` 及多数脚本采用。

4. **`DefaultTrainer` 的三级定制策略(按侵入度递增)**
   - 简单定制(改 optimizer / evaluator / LR scheduler / data loader): 在子类中**覆盖方法**,模式见 `tools/train_net.py`。
   - 训练中插入额外任务: 查 hook 系统是否已支持。
   - 上述两条都不够: 转去 `tools/plain_train_net.py` 手写。

5. **Hook 注入示例代码 (`HelloHook`)**
   - 钩子点 `after_step()`,触发条件 `self.trainer.iter % 100 == 0`,输出 `Hello at iteration {self.trainer.iter}!`。
   - 由此可看出 hook 框架定义了若干标准时机,`iter` 字段是当前迭代计数。

6. **指标写入选集中的 `EventStorage`**
   - 调用 `get_event_storage()` 取得存储句柄,模型侧以 `storage.put_scalar("some_accuracy", value)` 写入。
   - 写入的前提是 `self.training` 为真。
   - 写出到各类目的地由 `EventWriter` 完成;`DefaultTrainer` 已默认启用若干 `EventWriter`,可按"上文"所述流程进行定制。

---

## 【关键机制与数据】

**工作原理(分层结构):**

- **底层:** PyTorch 原生训练循环——用户拿到 `model` 与 `data loader` 之后,loss 反传、optimizer.step() 全部由 PyTorch 提供,detectron2 不在此层做额外约束(原文: "everything else needed to write a training loop can be found in PyTorch")。

- **中间层 (`SimpleTrainer`):** detectron2 引擎(`detectron2.engine`)中的最小训练循环,被显式约束为 "single-cost / single-optimizer / single-data-source",即不支持多任务、多优化器、多数据源混训。

- **上层 (`DefaultTrainer`):** 一个**由 config 初始化的 `SimpleTrainer`**。它叠加了五类工程化默认项,这些默认项在研究场景下经常成为阻碍,因此文档强调"trainer & hook system 故意保持 minimal,而非 powerful"(原文: "we intentionally keep the trainer & hook system minimal, rather than powerful")。

- **横切层 (Hook 系统):** 通过继承 `HookBase` 在训练的固定时机(`after_step` 等)插入代码,示例中以"每 100 iter 打印一次"展示。

- **指标通道 (`EventStorage` ↔ `EventWriter`):**
  - **生产端:** 模型代码中 `if self.training` 守卫,使用 `get_event_storage().put_scalar(...)` 提交标量。
  - **消费端:** `EventWriter` 把已提交的指标写出到各种目的地(如 TensorBoard、JSON 等,具体由 `DefaultTrainer` 默认配置)。
  - 原文: "Metrics are then written to various destinations with `EventWriter`";`EventWriter` 与 `EventStorage` 角色分离,`DefaultTrainer` 启用其中若干。

**性能数据:** 原文未给出任何数值、benchmark、epoch/iter 数或吞吐数据(原文无相关数字)。

---

## 【表格解读】

**原文无表格。** 该教程为说明性散文结构,所有信息以层级标题、列表与代码块组织,未包含参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式。** 文档未出现 LaTeX 数学公式或伪代码形式的算法表达式。仅出现两段 Python 代码示例:

1. `HelloHook` 子类(纯结构示意,无算式):
   ```python
   class HelloHook(HookBase):
     def after_step(self):
       if self.trainer.iter % 100 == 0:
         print(f"Hello at iteration {self.trainer.iter}!")
   ```
   符号:`HookBase` (基类名)、`self.trainer.iter` (当前训练迭代计数)、`% 100 == 0` (每 100 步触发条件)。作用:演示 hook 框架的标准插入点 `after_step()`。

2. `EventStorage` 写入示例:
   ```
   if self.training:
     value = # compute the value from inputs
     storage = get_event_storage()
     storage.put_scalar("some_accuracy", value)
   ```
   符号:`self.training` (模式守卫)、`value` (待记录指标,具体计算方式由用户给出,原文留空)、`get_event_storage()` (获取全局存储)、`put_scalar("some_accuracy", value)` (键值对写入)。作用:把模型侧计算的标量指标放入集中式事件存储。

---

## 【关联】

文档以"两种风格"为骨架,把 detectron2 引擎中所有训练相关组件织成一张依赖网:

| 关系方向 | 组件 | 关系描述(原文依据) |
|---|---|---|
| 自定义风格示例入口 | [`tools/plain_train_net.py`](../../tools/plain_train_net.py) | 原文称其是"One such example",即自定义循环的样例实现;同时也是"无法用 trainer+hook 完成时"的回退起点。 |
| 抽象最小核心 | [`detectron2.engine.SimpleTrainer`](../modules/engine.html#detectron2.engine.SimpleTrainer) | 提供"single-cost single-optimizer single-data-source"的最小循环,其余皆为额外职责。 |
| 抽象扩展实例 | [`detectron2.engine.defaults.DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) | "a `SimpleTrainer` initialized from a config",叠加五类默认行为;同时也是定制行为(subclass override)的入口。 |
| 抽象扩展驱动 | [`tools/train_net.py`](../../tools/train_net.py) | 原文: "used by `tools/train_net.py` and many scripts",即命令行训练脚本与多数脚本的默认底座。 |
| 横切点 | [`detectron2.engine.HookBase`](../modules/engine.html#detectron2.engine.HookBase) | 与 `SimpleTrainer`、`DefaultTrainer` 并列提及的扩展机制;用于 checkpointing、logging 等非 trainer 本体的任务。 |
| 指标中枢 | [`detectron2.utils.events.EventStorage`](../modules/utils.html#detectron2.utils.events.EventStorage) | 文档末尾指明它是"centralized"事件存储,模型侧通过 `get_event_storage()` 访问。 |
| 指标写出 | [`detectron2.utils.events` (`EventWriter`)](../modules/utils.html#module-detectron2.utils.events) | 原文称 "Metrics are then written to various destinations with `EventWriter`",由 `DefaultTrainer` 默认启用若干 writer。 |

**总体调用链:** 用户脚本 → `tools/train_net.py` → `DefaultTrainer`(由 config 初始化) → 内部委托 `SimpleTrainer` 跑最小循环 → `HookBase` 衍生 hook 在固定时机执行 → 模型侧 `get_event_storage().put_scalar(...)` 提交指标 → `EventWriter` 写出到目的地。当这一链路不够用时,文档建议回退到 `tools/plain_train_net.py` 自写循环。

---

## 【使用方法】

**1. 选择训练风格的判据(原文):**
- 想要"manage the entire training logic more clearly and have full control" → 自定义训练循环,参考 [`plain_train_net.py`](../../tools/plain_train_net.py)。
- 想要"simplify the standard training behavior" → Trainer 抽象,使用 `SimpleTrainer` 或 `DefaultTrainer`。

**2. 定制 `DefaultTrainer` 的三级方式(原文):**
- **Level 1 — 子类覆盖方法:** 用于换 optimizer、evaluator、LR scheduler、data loader 等,模式见 [`tools/train_net.py`](../../tools/train_net.py)。
- **Level 2 — 借助 hook:** 训练中插入额外任务,先查 [`HookBase`](../modules/engine.html#detectron2.engine.HookBase) 是否已支持;示例 `HelloHook` 见上文【公式解读】节。
- **Level 3 — 回退到 `plain_train_net.py`:** 当 trainer+hook 系统"intentionally ... cannot be supported"(原文),从 [`plain_train_net.py`](../../tools/plain_train_net.py) 起步手写。

**3. 写入训练指标(原文命令):**
```
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
  value = # compute the value from inputs
  storage = get_event_storage()
  storage.put_scalar("some_accuracy", value)
```
要点:`self.training` 守卫、键名用字符串(如 `"some_accuracy"`)、值需为标量。

**4. 自定义 `EventWriter` 出站目的地(原文):**
原文仅指引 "See above for how to customize them",即回到前文 `DefaultTrainer` 定制流程;**原文未涉及具体的 writer 配置项、命令行参数或环境变量**。

**5. 启动命令与具体配置项:** 原文未涉及 CLI 启动命令、yaml config 字段名、epoch/batch size 等数值参数;欲获取需参考 [`train_net.py`](../../tools/train_net.py) 与 [`DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 文档。
