# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/evaluation.md

# 一体化深度解读:Evaluation 文档

## 【定位】

这篇文档解决的是 detectron2 中**模型评估(evaluation)的标准化问题**——描述如何通过 `DatasetEvaluator` 接口对一批模型的 inputs/outputs 配对样本进行聚合计算,从而得到标准指标或自定义指标,使评估流程可复用、可扩展、可与不同数据集对接。

## 【技术要点】

1. **核心抽象接口 `DatasetEvaluator`**:具有三个生命周期方法 —— `reset()`(初始化计数等状态)、`process(inputs, outputs)`(对每批推理结果逐条累加)、`evaluate()`(返回最终的指标字典,如 `{"count": self.count}`)。
2. **手动评估模式**:自定义生成器 `get_all_inputs_outputs()` 逐个从 `data_loader` 取数据并调用 `model(data)`,然后循环执行 `evaluator.reset()` → `evaluator.process()` → `evaluator.evaluate()`。
3. **`inference_on_dataset()` 一站式函数**:把 `model`、`data_loader` 和一个(可合并的)evaluator 一并传入,在**一次前向遍历**中完成推理与评估,并提供该模型在该数据集上的准确速度基准。
4. **评估器合并器 `DatasetEvaluators`**:可将多个 evaluator(如 `COCOEvaluator(...)` 与自定义 `Counter()`)合并到一个列表里统一调用。
5. **通用数据集评估能力**:两个 evaluator 可作用于任何遵循 detectron2 [标准数据集格式](./datasets.md)的自定义数据集 —— `COCOEvaluator`(支持 box detection、instance segmentation、keypoint detection 的 AP)和 `SemSegEvaluator`(语义分割指标)。
6. **官方数据集原生 API 路径**:其他 evaluator 使用各自数据集的官方 API(原文提及 "e.g., COCO, LVIS")计算指标。

## 【关键机制与数据】

**工作原理/数据流**(原文有的才写):

- **整体数据流**:`data_loader` 产出 `inputs` → `model(inputs)` 产出 `outputs` → evaluator 对 (inputs, outputs) 反复调用 `process` → 最终 `evaluate()` 返回 `eval_results` 字典。
- **效率机制**:原文:"Compared to running the evaluation manually using the model, the benefit of this function is that evaluators can be merged together using `DatasetEvaluators`, and all the evaluation can finish in **one forward pass over the dataset**." 即合并评估可在**一次完整前向遍历**内完成所有指标计算,避免重复推理。
- **基准测试能力**:原文:"This function also provides accurate speed benchmarks for the given model and dataset." 即 `inference_on_dataset` 同时给出准确的运行速度指标。
- **自定义 evaluator 的最小实现示例**:`Counter` 通过 `process` 中 `self.count += len(output["instances"])` 累计验证集上检测到的实例总数,`evaluate()` 返回 `{"count": self.count}`。

原文未出现具体的性能数字、AP 数值或速度基准的量化值,仅给出了方法论层面的描述。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

本节解析原文文末或正文中显式给出的所有内部链接,以及它们与本 evaluation 文档的关系:

| 链接锚点 | 指向对象 | 与本文的关系 |
|---|---|---|
| `./models.md` | models guide | 上游:说明可直接使用 `model` 自行解析 inputs/outputs 进行评估,作为本接口方式之外的另一种可选路径 |
| `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator` | `DatasetEvaluator` 类 API 文档 | 核心:本文所描述的评估器接口的完整方法签名 |
| `../modules/evaluation.html#detectron2.evaluation.inference_on_dataset` | `inference_on_dataset` 函数 API | 核心:本文重点介绍的一站式评估函数 |
| `../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators` | `DatasetEvaluators` 类 API | 核心:用于将多个 evaluator 合并成一次遍历的合并器 |
| `./datasets.md` | datasets guide | 配套:解释 detectron2 的标准数据集格式,`COCOEvaluator` / `SemSegEvaluator` 在自定义数据集上工作的前提 |
| `../modules/evaluation.html#detectron2.evaluation.COCOEvaluator` | `COCOEvaluator` 类 API | 下游:通用型 evaluator,可对自定义数据集计算 box/instance/keypoint AP |
| `../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator` | `SemSegEvaluator` 类 API | 下游:通用型 evaluator,可对自定义数据集计算语义分割指标 |

逻辑链路:用户通过 `./models.md` 获得模型 → 通过 `./datasets.md` 获得数据 → 用 `DatasetEvaluator` 子类(`COCOEvaluator` / `SemSegEvaluator` / 自定义 evaluator)封装指标 → 用 `DatasetEvaluators` 合并 → 用 `inference_on_dataset` 在**一次前向**中完成全部评估。

## 【使用方法】

原文涉及以下启用方式/命令/配置项:

**方式 A — 完全手动评估**(原文代码):
```python
def get_all_inputs_outputs():
  for data in data_loader:
    yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
  evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

**方式 B — 通过 `inference_on_dataset` 一站式评估**(原文代码):
```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```
此方式会在 `data_loader` 上对所有输入执行 `model`,并调用 evaluator 进行处理;自动合并多个 evaluator,只做**一次前向遍历**,并产出准确的速度基准。

**自定义 evaluator 的最小注册模式**(原文示例):
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

**可选 evaluator**(用于自定义数据集):
- `COCOEvaluator(...)`:计算 box detection、instance segmentation、keypoint detection 的 AP。
- `SemSegEvaluator(...)`:计算语义分割指标。

原文未涉及任何 CLI 命令行启动方式、环境变量或配置文件路径,以上仅为其 API 调用层的使用说明。
