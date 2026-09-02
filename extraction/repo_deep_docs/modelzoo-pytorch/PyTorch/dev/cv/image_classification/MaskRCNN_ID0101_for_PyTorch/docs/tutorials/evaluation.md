# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/evaluation.md

# Evaluation 文档深度解读

## 【定位】

本文档描述 detectron2 中基于 `DatasetEvaluator` 接口的**模型评估通用框架**，说明如何对模型推理的 inputs/outputs 对进行聚合计算指标，并支持在自定义数据集上复用 COCO/SemSeg 评估能力。

---

## 【技术要点】

1. **核心接口 `DatasetEvaluator`**：定义了评估的统一抽象，包含 `reset()` / `process(inputs, outputs)` / `evaluate()` 三个方法（原文代码示例中明确给出这三个方法签名）。
2. **两种使用方式**：
   - 手动调用——按顺序执行 `evaluator.reset()` → 循环 `process()` → `evaluate()`。
   - 通过 `inference_on_dataset(model, data_loader, evaluator)` 一次性完成前向推理与评估。
3. **多评估器合并**：`DatasetEvaluators` 容器可将多个评估器（如 `COCOEvaluator(...)` + `Counter()`）组合，**一次前向推理**即可完成所有评估。
4. **自定义评估示例 `Counter`**：演示如何仅通过遍历 `output["instances"]` 计数，对验证集上检测到的实例数进行统计，最终返回 `{"count": self.count}`。
5. **数据集原生评估器**：detectron2 内置了面向 COCO、LVIS 等标准数据集 API 的评估器实现（原文未给出具体数量，仅以 "a few" 描述）。
6. **通用评估器**：仅 `COCOEvaluator` 与 `SemSegEvaluator` 两个评估器**不绑定具体数据集**，可对符合 detectron2 标准数据集格式的任意自定义数据集输出 AP（目标框检测、实例分割、关键点检测）与语义分割指标。

---

## 【关键机制与数据】

**工作原理（原文）：**

- 评估的本质是接收 "**inputs/outputs pairs**" 并对它们进行 **aggregate**（聚合）。可绕过评估框架，直接调用 `model` 并自行解析输出；也可使用 `DatasetEvaluator` 抽象。
- `inference_on_dataset` 的执行流程（原文）："This will execute `model` on all inputs from `data_loader`, and call evaluator to process them."——即遍历 `data_loader` 的每个 batch，调 `model(data)`，再把 `(inputs, outputs)` 交给 evaluator 的 `process` 方法。
- 数据流示意（综合原文）：
  - 手动模式：`get_all_inputs_outputs()` 是一个 `yield data, model(data)` 的生成器；外层依次 `reset → for ... process → evaluate`。
  - 自动模式：`inference_on_dataset` 内部完成生成器职责 + 评估器调度。

**性能数据：** 原文**未给出**任何具体数值（如 mAP、速度 benchmark 的实际数字），仅在描述 `inference_on_dataset` 时提到 "This function also provides accurate speed benchmarks for the given model and dataset"，作为该函数的副作用能力陈述。

**聚合后的指标形式：** 原文 `Counter` 示例的 `evaluate()` 返回值为字典 `{"count": self.count}`，表明评估结果以 dict 形式返回。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**（文档以伪代码/代码片段表达算法，未出现数学公式或 LaTeX 表达式。）

---

## 【关联】

依据文末给出的内部链接，文档处于 detectron2 评估体系的"入门引导"位置，向上下游衔接如下：

| 关联模块 | 关联角色 | 链接锚点 |
|---|---|---|
| `DatasetEvaluator` | **核心抽象接口**，本文档的主对象 | `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator` |
| `inference_on_dataset` | **高层调用入口**，封装模型推理 + 评估器调度 | `../modules/evaluation.html#detectron2.evaluation.inference_on_dataset` |
| `DatasetEvaluators` | **多评估器容器**，把多个 `DatasetEvaluator` 合并成单个调用 | `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators` |
| `COCOEvaluator` | 内置标准评估器，同时也是**通用 AP 评估器**（可用于自定义数据集） | `../modules/evaluation.html#detectron2.evaluation.COCOEvaluator` |
| `SemSegEvaluator` | 内置**通用语义分割评估器**（可用于自定义数据集） | `../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator` |
| `./models.md` | **上游**：直接使用模型解析输入输出的备选路径（与评估框架并列） | `./models.md` |
| `./datasets.md` | **数据契约**：`COCOEvaluator`/`SemSegEvaluator` 评估自定义数据集的前提——遵循 detectron2 标准数据集格式 | `./datasets.md` |

依赖链：**模型（models.md）→ 数据集格式（datasets.md）→ 评估器抽象（DatasetEvaluator）→ 容器/入口（DatasetEvaluators / inference_on_dataset）→ 具体评估器（COCOEvaluator、SemSegEvaluator）**。

---

## 【使用方法】

**1. 手动调用方式（原文示例代码）：**

```python
def get_all_inputs_outputs():
  for data in data_loader:
    yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
  evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

要点（原文）：需要自行提供 `data_loader` 与 `model`；评估器必须先 `reset()`，循环调用 `process(inputs, outputs)`，最后调一次 `evaluate()` 得到结果。

**2. 通过 `inference_on_dataset` 调用（原文示例代码）：**

```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```

要点（原文）：传入 `model`、`data_loader`、`DatasetEvaluators` 容器（容器内可放任意 `DatasetEvaluator` 实例，例如 `COCOEvaluator(...)` 与用户自定义的 `Counter()`）；函数会自动完成前向推理并聚合多个评估器的结果。

**3. 自定义评估器（原文示例代码）：**

```python
class Counter(DatasetEvaluator):
  def reset(self):
    self.count = 0
  def process(self, inputs, outputs):
    for output in outputs:
      self.count += len(output["instances"])
  def evaluate(self):
    return {"count": self.count}
```

要点（原文）：继承 `DatasetEvaluator`，实现三个方法——`reset` 清零状态，`process` 累积输入/输出对，`evaluate` 返回结果字典。原文未涉及具体配置项、环境变量或命令行参数。
