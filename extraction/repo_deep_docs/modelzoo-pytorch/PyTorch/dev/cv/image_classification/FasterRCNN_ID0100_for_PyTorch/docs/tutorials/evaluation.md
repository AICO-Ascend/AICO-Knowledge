# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/evaluation.md

# Evaluation 文档深度解读

---

## 【定位】

这篇文档描述 detectron2 框架中的**模型评估机制**：如何通过 `DatasetEvaluator` 接口对模型在数据集上的输入/输出对进行聚合计算，并介绍了内置评估器、自定义评估器的实现方式以及 `inference_on_dataset` 这一便捷工具函数。

---

## 【技术要点】

1. **DatasetEvaluator 接口**：detectron2 中所有评估器的统一抽象接口，包含三个核心方法：`reset()`、`process(inputs, outputs)`、`evaluate()`。
2. **三种方法分工**：`reset()` 初始化内部状态；`process()` 逐批次接收模型推理的输入/输出对并累积；`evaluate()` 返回最终的指标字典（如 `{"count": self.count}`）。
3. **手动评估模式**：通过生成器 `get_all_inputs_outputs()` 逐 batch 取出 `(data, model(data))`，配合 `evaluator.reset() → process() 循环 → evaluate()` 完成评估。
4. **inference_on_dataset 工具函数**：一次性对 `data_loader` 中所有输入执行模型推理，并把结果分发给组合评估器 `DatasetEvaluators([...])`，避免对同一数据集做多次前向传播。
5. **DatasetEvaluators 组合能力**：可将多个 `DatasetEvaluator`（如 `COCOEvaluator` 与自定义 `Counter`）合并使用，所有评估在**单次前向遍历**数据集内完成，并提供**准确的速度基准**（speed benchmarks）。
6. **通用评估器**：`COCOEvaluator` 可对任意自定义数据集计算**AP（Average Precision）**，覆盖 box detection、instance segmentation、keypoint detection 三类任务；`SemSegEvaluator` 可对任意自定义数据集计算语义分割指标。两者均依赖 detectron2 的 standard dataset format。

---

## 【关键机制与数据】

**工作原理与数据流（按原文描述还原）：**

- 原文："Evaluation is a process that takes a number of inputs/outputs pairs and aggregate them." → 评估本质是把若干 `(input, output)` 对累积聚合。
- 原文数据流（手动方式）：
  1. `evaluator.reset()` → 清零内部计数器/缓存；
  2. 循环：`for inputs, outputs in get_all_inputs_outputs(): evaluator.process(inputs, outputs)` → 由 `data_loader` 逐 batch 取数据，并由 `model(data)` 同步产出预测；
  3. `eval_results = evaluator.evaluate()` → 汇总并返回指标字典。
- 原文数据流（`inference_on_dataset` 方式）：模型对 `data_loader` 中**所有**输入执行推理 → 调用组合评估器处理 → 一次性产出评估结果；原文明确该函数相比手动方式的优势是"all the evaluation can finish in one forward pass over the dataset"。
- 原文性能描述：`inference_on_dataset` 还"provides accurate speed benchmarks for the given model and dataset"，即除了评估指标外还可给出该模型在该数据集上的速度基准（原文未给出具体数字）。

**Counter 自定义评估器原文示例机制：**
- `reset()`：把 `self.count` 置 0；
- `process(inputs, outputs)`：遍历 `outputs`，对每个 `output["instances"]` 累加实例数；
- `evaluate()`：返回 `{"count": self.count}`。

---

## 【表格解读】

**原文无表格**

---

## 【公式解读】

**原文无公式**

---

## 【关联】

本文档是 detectron2 评估体系的入口指南，与以下模块/特性存在上下游关系：

- **`./models.md`**：原文指出"You can always use the model directly and just parse its inputs/outputs manually to perform evaluation"，表明本文档与模型使用文档是并列/替代关系——本文档提供了更高层的封装。
- **`./datasets.md`**：原文提到 `COCOEvaluator` 与 `SemSegEvaluator` 可评估"any generic dataset that follows detectron2's standard dataset format"，因此依赖 datasets 文档定义的 standard dataset format。
- **`detectron2.evaluation.DatasetEvaluator`**：核心接口定义所在，本文所有评估器都实现该接口。
- **`detectron2.evaluation.inference_on_dataset`**：本文档重点推荐的工具函数，封装了"模型推理 + 评估器分发"全过程。
- **`detectron2.evaluation.DatasetEvaluators`**：组合多个 `DatasetEvaluator` 的容器类，使 `inference_on_dataset` 能在单次前向遍历中完成多项评估。
- **`detectron2.evaluation.COCOEvaluator`**：内置的具体评估器，用于 box detection / instance segmentation / keypoint detection 的 AP 计算，可用于自定义数据集。
- **`detectron2.evaluation.SemSegEvaluator`**：内置的具体评估器，用于任意自定义数据集的语义分割指标计算。

整体关系：**`DatasetEvaluator`** 是接口基类 → **`COCOEvaluator` / `SemSegEvaluator` / 用户自定义评估器（如 `Counter`）** 是其具体实现 → **`DatasetEvaluators`** 是多评估器组合容器 → **`inference_on_dataset`** 串联**模型** + **DataLoader** + **评估器** 三者完成端到端评估。**`./models.md`** 与 **`./datasets.md`** 分别是上游（如何得到 outputs）和数据格式约束。

---

## 【使用方法】

**1. 实现自定义评估器（原文 Counter 完整示例）：**

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

**2. 手动调用评估器（原文代码）：**

```python
def get_all_inputs_outputs():
  for data in data_loader:
    yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
  evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

**3. 使用 `inference_on_dataset`（原文代码）：**

```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```

**4. 通用评估器的启用（原文描述）：**
- **COCOEvaluator**：可直接对遵循 detectron2 standard dataset format 的自定义数据集计算 box detection / instance segmentation / keypoint detection 的 AP。
- **SemSegEvaluator**：可直接对遵循同格式的自定义数据集计算语义分割指标。

> 注：原文未涉及具体的命令行启动方式、配置文件项或超参数设置；上述方法均为 Python API 级别的使用说明。
