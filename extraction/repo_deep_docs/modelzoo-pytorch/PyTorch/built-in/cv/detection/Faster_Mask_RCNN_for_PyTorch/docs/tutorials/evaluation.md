# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/evaluation.md

# 深度解读: detectron2 Evaluation 指南

## 【定位】

本文档系统介绍了 detectron2 框架中**模型评估 (Evaluation) 的统一接口与使用方法**, 围绕 `DatasetEvaluator` 抽象、批量推理函数 `inference_on_dataset` 以及面向自定义数据集的内置评估器展开, 为 Faster/Mask R-CNN 等检测模型的验证流程提供标准化、可扩展的评测能力。

---

## 【技术要点】

1. **评估本质**: 评估是接收若干「输入/输出对」并对其进行聚合的过程; 既可直接用模型解析 IO, 也可通过 `DatasetEvaluator` 接口统一处理。
2. **核心抽象类**: `DatasetEvaluator` —— 任何评估器需实现 `reset() / process(inputs, outputs) / evaluate()` 三方法, 分别负责清零、逐 batch 累计、产出最终指标。
3. **内置评估器**: detectron2 自带基于 COCO、LVIS 等标准数据集 API 的评估器, 可直接产出标准 AP 指标。
4. **批量评估函数**: `inference_on_dataset(model, data_loader, evaluator)` —— 用一次前向遍历完成全数据集推理与评估, 同时提供精确的速度基准 (speed benchmark)。
5. **多评估器合并**: `DatasetEvaluators([...])` 可将多个评估器 (如 `COCOEvaluator` + `Counter`) 合并, 共享同一次推理结果, 避免重复计算。
6. **面向自定义数据集的通用评估器**: `COCOEvaluator` 可对任意自定义数据集评估 box 检测、实例分割、关键点检测的 AP; `SemSegEvaluator` 可对任意自定义数据集评估语义分割指标 (前提: 数据遵循 detectron2 [标准数据集格式](./datasets.md))。

---

## 【关键机制与数据】

### 1. 评估的工作流程 (数据流)

评估流程本质是一条流水线:

```
data_loader  ──►  model(data)  ──►  (inputs, outputs) pairs
                                            │
                                            ▼
                                  evaluator.process(inputs, outputs)
                                            │
                                            ▼
                                  evaluator.evaluate()  ──►  eval_results (dict)
```

- **原文**: "Evaluation is a process that takes a number of inputs/outputs pairs and aggregate them."
- **原文**: "Evaluators can also be used with `inference_on_dataset`."
- **原文**: "the benefit of this function is that evaluators can be merged together using `DatasetEvaluators`, and all the evaluation can finish in **one forward pass** over the dataset. This function also provides **accurate speed benchmarks** for the given model and dataset."

### 2. `DatasetEvaluator` 三方法契约 (原文代码逐字保留)

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

| 方法 | 触发时机 | 职责 |
|---|---|---|
| `reset()` | 评估开始前 | 清零内部状态 (此处设 `self.count = 0`) |
| `process(inputs, outputs)` | 每个 batch 后 | 消费一次推理的输入输出, 累计中间统计量 |
| `evaluate()` | 全部 batch 处理完 | 返回最终评估字典 `{"count": ...}` |

> `Counter` 是文档给出的最小可用自定义评估器示例, 用 `len(output["instances"])` 统计检测到的实例总数。

### 3. 手动使用 vs `inference_on_dataset` 的差异

**手动模式 (原文代码)**:
```python
def get_all_inputs_outputs():
  for data in data_loader:
    yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
  evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

**便捷模式 (原文代码)**:
```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```

**关键区别** (原文表述):
- 手动模式只能跑单一 evaluator;
- `inference_on_dataset` 借助 `DatasetEvaluators` 把多个 evaluator 合并, **仅做一次前向推理**, 即可同时得到多份评估结果;
- `inference_on_dataset` 同时给出**模型在指定数据集上的精确速度基准**。

### 4. 自定义数据集评估能力清单 (原文)

- `COCOEvaluator` → 可在**任意自定义数据集**上评估:
  - box detection AP
  - instance segmentation AP
  - keypoint detection AP
- `SemSegEvaluator` → 可在**任意自定义数据集**上评估:
  - semantic segmentation 指标

前提 (原文): 数据需遵循 detectron2 的 [标准数据集格式](./datasets.md)。

---

## 【表格解读】

**原文无表格**。

(文档主要以代码块和列表形式呈现, 未出现参数表、性能对比表或配置项表格。)

---

## 【公式解读】

**原文无公式**。

(文档不涉及任何 LaTeX 或伪代码形式的数学公式, 评估过程以 API 调用与数据流描述呈现。)

---

## 【关联】

本文档在 detectron2 生态中的位置与上下游关系:

| 关联对象 | 关系性质 | 出处链接 |
|---|---|---|
| **[models](./models.md)** | 上游 —— 评估可直接基于 `model` 的 IO 自行解析, 也可借助本文的 evaluator | `./models.md` |
| **`DatasetEvaluator`** | 核心抽象 —— 本文的主线接口, 所有内置/自定义评估器都实现它 | `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator` |
| **`inference_on_dataset`** | 核心函数 —— 提供「一次前向 + 多 evaluator 合并 + 速度基准」能力 | `../modules/evaluation.html#detectron2.evaluation.inference_on_dataset` |
| **`DatasetEvaluators`** | 容器类 —— 将多个 `DatasetEvaluator` 合并, 配合 `inference_on_dataset` 使用 | `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators` |
| **[datasets](./datasets.md)** | 数据格式规范 —— `COCOEvaluator`/`SemSegEvaluator` 用于自定义数据集时必须遵循 | `./datasets.md` |
| **`COCOEvaluator`** | 内置评估器 —— box / instance seg / keypoint AP | `../modules/evaluation.html#detectron2.evaluation.COCOEvaluator` |
| **`SemSegEvaluator`** | 内置评估器 —— 语义分割指标 | `../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator` |

**关系网结构**:

```
models.md (上游: 模型定义)
    │
    ▼
evaluation.md (本文: 评估接口与流程)
    │
    ├──► DatasetEvaluator (接口)
    │       │
    │       ├──► COCOEvaluator ──► 依赖 datasets.md (标准格式)
    │       ├──► SemSegEvaluator ──► 依赖 datasets.md (标准格式)
    │       └──► 用户自定义 Counter 等
    │
    ├──► DatasetEvaluators (合并容器)
    │
    └──► inference_on_dataset (整合: 模型 + dataloader + evaluators)
```

---

## 【使用方法】

### 1. 直接用模型 + 解析 IO (无 evaluator)

**原文**:
> "You can always use the model directly and just parse its inputs/outputs manually to perform evaluation."

—— 调用 `model(data)`, 自行遍历 `outputs` 解析预测结果。

### 2. 手动驱动单个 evaluator (原文代码)

```python
def get_all_inputs_outputs():
  for data in data_loader:
    yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
  evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

要点: 先 `reset()`, 再循环 `process()`, 最后 `evaluate()` 拿到 dict。

### 3. 用 `inference_on_dataset` 合并多个 evaluator (原文代码)

```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```

要点:
- `model`: 训练好的 detectron2 模型;
- `data_loader`: 验证集迭代器;
- 第三个参数传入 `DatasetEvaluators` 列表, 内部 evaluator 共享一次前向;
- 返回 `eval_results` dict, 同时附带速度基准信息。

### 4. 自定义评估器 (原文代码)

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

要点: 继承 `DatasetEvaluator`, 实现三方法; `process` 中读取 `output["instances"]` (detectron2 标准 Instances 字段) 等结构化输出。

### 5. 自定义数据集评估配置 (原文要点)

- **box / instance seg / keypoint AP**: 使用 `COCOEvaluator(dataset_name, cfg, distributed, output_dir)`;
- **语义分割**: 使用 `SemSegEvaluator(dataset_name, distributed, output_dir)`;
- 数据集必须先注册为 detectron2 标准数据集格式 (详见 `datasets.md`)。

> **注**: 文档未给出具体的命令行启动方式或 YAML 配置项; 评估入口以 Python API 调用为主, 这一点与 detectron2 整体设计风格一致。
