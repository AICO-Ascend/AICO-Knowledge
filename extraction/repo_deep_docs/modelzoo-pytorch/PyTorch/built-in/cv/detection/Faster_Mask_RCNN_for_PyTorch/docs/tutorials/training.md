# Training

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/training.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/training.md

# 一体化深度解读: Faster_Mask_RCNN_for_PyTorch — `docs/tutorials/training.md`

---

## 【定位】

这篇文档面向已具备自定义模型与数据加载器的 detectron2 用户, 介绍**两种训练范式** (自定义训练循环 / Trainer 抽象) 以及**训练过程中的指标记录机制**, 帮助用户根据研究/工程需求选择合适的训练组织方式并完成定制。

---

## 【技术要点】

1. **两种训练风格**: ① 自定义训练循环 (Custom Training Loop), 由用户完全控制训练逻辑, 示例见 `tools/plain_train_net.py`; ② Trainer 抽象, 通过标准化的 Trainer + Hook 系统简化标准训练行为。
2. **SimpleTrainer**: 一个**最小化训练循环**, 仅支持 "single-cost single-optimizer single-data-source" 的训练, 不含 checkpoint、logging 等额外任务 (需通过 Hook 系统补齐)。
3. **DefaultTrainer**: 从 config 初始化的 `SimpleTrainer`, 被 `tools/train_net.py` 及众多脚本调用, 内置 optimizer、学习率调度、logging、evaluation、checkpointing 等**默认行为**。
4. **DefaultTrainer 的定制路径**: 
   - **轻量定制** (改 optimizer / evaluator / LR scheduler / data loader 等): 在子类中**重写其方法**, 参考 `tools/train_net.py`。
   - **复杂定制**: 优先检查 Hook 系统是否支持; 不支持则从 `tools/plain_train_net.py` 出发手动实现训练逻辑。
5. **指标集中存储**: 训练过程中模型与 Trainer 把指标写入**中心化的 `EventStorage`**, 通过 `get_event_storage()` 获取并 `put_scalar("name", value)` 记录标量指标。
6. **指标分发**: 指标通过 `EventWriter` 写入多种目的地, `DefaultTrainer` 默认启用若干 `EventWriter` (配置可定制)。

---

## 【关键机制与数据】

### 工作原理与数据流 (原文梳理)

- **Custom Training Loop 数据流**: 模型 + 数据加载器已就绪 → 用户直接基于 PyTorch 编写训练循环 → 完全控制所有训练逻辑; 示例实现位于 `tools/plain_train_net.py`。
- **Trainer 抽象数据流**: 模型 + 数据加载器 + config → 交给 `DefaultTrainer` → 内部封装 optimizer / LR schedule / logging / evaluation / checkpointing 等默认组件 → 通过 **Hook 系统** 在标准训练流程的关键节点插入用户自定义行为。
- **Hook 系统作用**: 在 `SimpleTrainer` 仅保留最小循环时, 把 checkpoint、logging 等"非核心但通用"的逻辑**外置**为 Hook, 既不污染最小循环, 又允许用户按需扩展。
- **指标记录数据流**: 模型前向 / 后向计算得到指标 → `get_event_storage()` 取到全局 `EventStorage` → `storage.put_scalar("name", value)` 写入 → `EventWriter` 写向各目的地。

### 性能/数字数据
原文未提供任何具体的性能数字、batch size、学习率、epoch 数等量化指标 (无表格、无公式、无数据条目)。**原文无量化性能数据**。

---

## 【表格解读】

**原文无表格**。文档未出现参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 或伪代码形式的公式。

---

## 【关联】

依据文末内部链接, 本文档与以下模块/脚本存在上下游/互补关系:

| 关联对象 | 类型 | 与本文档的关系 |
|---|---|---|
| `../../tools/plain_train_net.py` | 脚本 | **Custom Training Loop 风格的示例**, 同时也是当 Hook 系统无法满足需求时手动实现训练逻辑的起点 |
| `../modules/engine.html#detectron2.engine.SimpleTrainer` | 模块 | **最小化 Trainer**, 是 `DefaultTrainer` 的基类; 仅做单 cost / 单 optimizer / 单 data source |
| `../modules/engine.html#detectron2.engine.HookBase` | 模块 | **Hook 系统的基类**, 负责把 checkpoint、logging 等非核心逻辑以 Hook 形式挂到训练流程中; 用于补齐 `SimpleTrainer` 的扩展能力 |
| `../modules/engine.html#detectron2.engine.defaults.DefaultTrainer` | 模块 | **配置驱动的标准 Trainer**, 内部组合了 `SimpleTrainer` + 若干 Hook (optimizer/LR schedule/logging/evaluation/checkpointing 等), 是 `tools/train_net.py` 等众多脚本的运行入口 |
| `../../tools/train_net.py` | 脚本 | 调用 `DefaultTrainer` 的标准脚本, 同时也是 "在子类中重写 `DefaultTrainer` 方法做轻量定制" 的参考样例 |
| `../modules/utils.html#detectron2.utils.events.EventStorage` | 模块 | **集中式指标存储**, 是训练过程中 `put_scalar` / 后续 `EventWriter` 读取指标的中介 |

逻辑链路可概括为: **`plain_train_net.py` ↔ 自定义循环风格**; **`train_net.py` → `DefaultTrainer` → `SimpleTrainer` + `HookBase` → `EventStorage` → `EventWriter`**, 构成完整 Trainer 抽象的标准数据/控制流。

---

## 【使用方法】

### 1. 选择训练风格
- 想要**完全掌控训练逻辑 / 研究目的** → 写自己的训练循环 (参考 `tools/plain_train_net.py`)。
- 想要**快速使用标准训练管线 / 只想做局部定制** → 使用 `DefaultTrainer` (参考 `tools/train_net.py`)。

### 2. 定制 `DefaultTrainer` (原文给出两种方式)
- **简单定制**: 在子类中**重写** `DefaultTrainer` 的方法 (optimizer / evaluator / LR scheduler / data loader 等), 仿照 `tools/train_net.py` 的写法。
- **复杂定制**: 先看 Hook 系统是否能支持; 若不能, 以 `tools/plain_train_net.py` 为模板手动实现训练逻辑。

### 3. 在训练中记录指标 (原文代码逐字保留)

```python
from detectron2.utils.events import get_event_storage

# inside the model:
if self.training:
  value = # compute the value from inputs
  storage = get_event_storage()
  storage.put_scalar("some_accuracy", value)
```

要点: 仅在 `self.training` 为真时记录; 通过 `get_event_storage()` 获取**进程级中心化存储**; 调用 `put_scalar(name, value)` 写入标量, 之后由 `EventWriter` 写出到各目的地 (DefaultTrainer 默认启用若干 `EventWriter`, 需自定义时可参考上文定制方式)。

### 4. 启用 / 配置项
原文未给出具体的 CLI 启动命令、配置文件 yaml 字段或 flag 列表 (这些内容属于 `tools/train_net.py` / `DefaultTrainer` 文档, 不在本文档范围内)。**原文未涉及具体的启动命令与配置项**。
