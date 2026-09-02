# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/evaluation.md

# 深度解读: PointRend / Detectron2 Evaluation 指南

---

## 【定位】

这篇文档描述 **detectron2 中的模型评估能力**——基于统一的 `DatasetEvaluator` 接口, 将模型在数据集上的输入/输出对 (inputs/outputs pairs) 聚合为评测指标, 并提供手动调用与一键批处理两种使用方式。

---

## 【技术要点】

1. **统一接口 `DatasetEvaluator`**: 所有评估器均实现 `reset() / process(inputs, outputs) / evaluate()` 三个方法, 形成 "重置 → 逐样本处理 → 汇总" 的标准流程。
2. **内置数据集专用评估器**: detectron2 内置基于官方 API 计算指标的评估器, 例如 **COCO、LVIS**。
3. **自定义评估器示例 `Counter`**: 通过继承 `DatasetEvaluator`, 在 `process` 中累加 `output["instances"]` 长度, 即可在验证集上统计 "检测到的实例总数" 这类自定义指标。
4. **手动调用三步式**: 先构造 `get_all_inputs_outputs()` 生成器 (对每个 batch 调用 `model(data)`), 然后 `evaluator.reset()` → 循环 `evaluator.process(inputs, outputs)` → `eval_results = evaluator.evaluate()`。
5. **批处理入口 `inference_on_dataset`**: 一行代码完成 "在 `data_loader` 上跑模型 + 调用评估器"; 支持用 `DatasetEvaluators([...])` 把多个评估器合并, **所有评估在一次前向传播 (one forward pass) 内完成**, 还能给出 **给定模型与数据集下的精确速度基准 (accurate speed benchmarks)**。
6. **通用自定义数据集评估器**: detectron2 提供两类可对任意符合 [standard dataset format](./datasets.md) 的自定义数据集生效的评估器——`COCOEvaluator` (框检测/实例分割/关键点的 AP) 与 `SemSegEvaluator` (语义分割指标)。

---

## 【关键机制与数据】

**工作原理 (原文):**

- 评估本质是 "接收若干 inputs/outputs pairs, 然后聚合" 的过程 (`Evaluation is a process that takes a number of inputs/outputs pairs and aggregate them`)。
- 用户可绕开评估器, 直接调用 [model](./models.md) 并手动解析输入输出做评估; 也可以使用基于 `DatasetEvaluator` 接口的实现。
- `DatasetEvaluator` 抽象三类操作:
  - `reset()`: 清零内部状态 (如 `Counter` 中 `self.count = 0`)
  - `process(inputs, outputs)`: 处理单批样本 (如 `Counter` 中累加 `len(output["instances"])`)
  - `evaluate()`: 汇总输出 (如 `Counter` 返回 `{"count": self.count}`)
- `inference_on_dataset` 的执行流程 (原文): 遍历 `data_loader` 中所有输入, 执行 `model` 前向推理, 然后调用评估器进行 `process`/`evaluate`。

**性能/数据相关说明 (原文):**

- 原文未给出任何具体数字 (如 mAP、时延、吞吐)。
- 唯一与 "性能" 相关的描述是: `inference_on_dataset` "provides **accurate speed benchmarks** for the given model and dataset"——即它能给出给定模型+数据集组合下的精确速度基准。

---

## 【表格解读】

**原文无表格。** 全文为说明性文字与 Python 代码片段, 不含任何参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式。** 全文没有数学公式或伪代码形式表达式 (代码示例为 Python 调用/类定义, 不属于公式)。

---

## 【关联】

依据文末与正文中的内部链接信息, 本文档与以下特性/模块形成上下游关系:

| 关联对象 | 关系类型 | 说明 |
|---|---|---|
| [models.md](./models.md) | 上游/并列 | 提供直接调用模型并手动解析输出做评估的替代路径 |
| [datasets.md](./datasets.md) | 依赖 | 通用评估器 (`COCOEvaluator`/`SemSegEvaluator`) 仅对遵循 detectron2 **standard dataset format** 的数据集生效 |
| `detectron2.evaluation.DatasetEvaluator` | 核心抽象 | 所有评估器 (内置、自定义、`COCOEvaluator`、`SemSegEvaluator`) 的基类 |
| `detectron2.evaluation.inference_on_dataset` | 上层封装 | 一次性完成 "模型前向 + 评估器调用 + 速度基准测量" 的便捷入口 |
| `detectron2.evaluation.DatasetEvaluators` | 组合容器 | 将多个 `DatasetEvaluator` 合并为单一对象, 在一次前向传播中并行完成所有评估 |
| `detectron2.evaluation.COCOEvaluator` | 具体实现 | 用于自定义数据集上的框检测 / 实例分割 / 关键点 AP 评估 |
| `detectron2.evaluation.SemSegEvaluator` | 具体实现 | 用于自定义数据集上的语义分割指标评估 |

**关系图谱 (按文中流程):**
```
model (models.md) ──┐
                    │ 输入/输出对
data_loader ────────┼──► inference_on_dataset ──► DatasetEvaluators ──► {DatasetEvaluator, COCOEvaluator, SemSegEvaluator, Counter, ...}
                    │                                                            ↑
                    └──► 也可由用户手动: reset() → process() → evaluate()       │
                                                                                 │
                                                                       依赖 datasets.md 的标准格式
```

---

## 【使用方法】

### 方式一: 手动调用评估器 (原文代码)
```python
def get_all_inputs_outputs():
  for data in data_loader:
    yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
  evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

### 方式二: 使用 `inference_on_dataset` (推荐, 原文代码)
```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```
此方式会自动:
1. 遍历 `data_loader` 执行 `model`
2. 合并多个评估器 (`DatasetEvaluators`)
3. 在 **一次前向传播** 内完成所有评估
4. 输出 **精确速度基准** (accurate speed benchmarks)

### 方式三: 自定义评估器 (原文 Counter 示例)
```python
class Counter(DatasetEvaluator):
  def reset(self):
    self.count = 0
  def process(self, inputs, outputs):
    for output in outputs:
      self.count += len(output["instances"])
  def evaluate(self):
    # save self.count somewhere, or print it, or return it.
    return {"count": self.count}
```

### 选择评估器的决策树 (原文)
- 数据集是 **COCO / LVIS** 等有官方 API 的标准数据集 → 使用 detectron2 内置的对应数据集专用评估器。
- 数据集是 **自定义数据集**, 需做:
  - 框检测 / 实例分割 / 关键点评估 → [`COCOEvaluator`](../modules/evaluation.html#detectron2.evaluation.COCOEvaluator) (评估 AP)
  - 语义分割评估 → [`SemSegEvaluator`](../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator)
- 需统计其他自定义指标 → 实现自己的 `DatasetEvaluator` 子类 (三方法: `reset`/`process`/`evaluate`)。

> 注: 原文未涉及任何命令行参数、配置文件 (config) 字段或超参数; 评估器均通过 Python API 构造与调用。
