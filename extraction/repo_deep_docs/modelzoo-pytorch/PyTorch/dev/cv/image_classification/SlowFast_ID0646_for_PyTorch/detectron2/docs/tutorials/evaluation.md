# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/evaluation.md

# 深度解读:detectron2 Evaluation 文档

## 【定位】
本文档系统阐述 detectron2 中**模型评估(Evaluation)的统一接口与使用方法**,核心围绕 `DatasetEvaluator` 抽象接口,描述如何对模型在数据集上的推理结果进行聚合计算指标,以及如何借助 `inference_on_dataset` 将推理与评估一体化执行。

---

## 【技术要点】

1. **评估的本质**:评估是一个"接收若干 (输入, 输出) 对并将其聚合"的过程,可手动解析模型输出,也可通过 `DatasetEvaluator` 接口规范化执行。
2. **`DatasetEvaluator` 接口的三段式协议**(原文示例代码 `Counter` 类):
   - `reset()` — 重置内部状态(如 `self.count = 0`)
   - `process(inputs, outputs)` — 处理每一批 (输入, 输出) 对(原文中为累加 `len(output["instances"])`)
   - `evaluate()` — 汇总结果并返回(原文中返回 `{"count": self.count}` 字典)
3. **内置与自定义并存**:detectron2 内置基于标准数据集官方 API(COCO、LVIS 等)的评估器,同时允许用户继承 `DatasetEvaluator` 实现自定义评估逻辑(如示例中统计验证集上检测到的实例数)。
4. **手动评估模式**:通过 `get_all_inputs_outputs()` 生成器逐批喂入数据,显式调用 `evaluator.reset() → process(...) → evaluate()`,调用方完全控制推理循环。
5. **一体化模式 `inference_on_dataset`**:将模型、数据加载器、评估器三者绑定,内部完成全部前向推理并触发评估器;支持通过 `DatasetEvaluators([...])` **合并多个评估器**在同一次数据集前向传播中完成所有评估,并提供精确的速度基准(speed benchmarks)。
6. **通用数据集评估器**:除专用评估器外,有两个评估器可对任意遵循 detectron2 标准数据集格式的数据集生效——`COCOEvaluator`(支持 box detection / instance segmentation / keypoint detection 的 AP 指标)与 `SemSegEvaluator`(语义分割指标)。

---

## 【关键机制与数据】

### 工作原理

- **接口抽象**:`DatasetEvaluator` 是评估的契约。任何实现 `reset / process / evaluate` 三个方法的对象都可作为评估器接入。
- **数据流(手动模式)**:文档原文给出的循环结构为:
  ```
  evaluator.reset()
  for inputs, outputs in get_all_inputs_outputs():
      evaluator.process(inputs, outputs)
  eval_results = evaluator.evaluate()
  ```
  即"初始化 → 逐批累加 → 汇总返回"的经典三阶段。
- **数据流(一体化模式)**:`inference_on_dataset(model, data_loader, evaluator)` 内部对 `data_loader` 中所有输入执行 `model(data)`,把 `(inputs, outputs)` 喂给评估器。其相较于手动调用模型的**两个核心收益**(原文表述):
  1. 可用 `DatasetEvaluators` 将多个评估器合并,实现"一次前向传播,多种指标";
  2. 提供给定模型与数据集上的"accurate speed benchmarks"。
- **自定义数据集的兼容性**:`COCOEvaluator` 与 `SemSegEvaluator` 不局限于原始 COCO/cityscapes 数据集,凡是遵循 detectron2 [standard dataset format](./datasets.md) 的数据集均可直接复用——这是这两个评估器能"evaluate any custom dataset"的前提(原文明确写出)。

### 性能数据
原文未提供具体的数值、延迟、AP 数字或命令参数;仅在概念层面提及"accurate speed benchmarks",未给出实际基准结果。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **./models.md**:文档开头即提示读者可以"always [use the model](./models.md) directly and just parse its inputs/outputs manually to perform evaluation",说明 evaluation 模块与 model 模块在能力上是**正交且互补**的——评估既可以脱离框架手工实现,也可借助评估器自动化。
- **./datasets.md**:`COCOEvaluator` 与 `SemSegEvaluator` 能评估"any custom dataset"的**前置条件**是该数据集遵循 detectron2 [standard dataset format](./datasets.md),因此本文与数据集格式规范构成上下游依赖。
- **../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator**:核心抽象接口,自定义评估器(如原文 `Counter` 示例)需继承此类。
- **../modules/evaluation.html#detectron2.evaluation.inference_on_dataset**:将"模型推理 + 评估器调度"封装为单次调用的关键 API。
- **../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators**:用于把多个 `DatasetEvaluator` 实例聚合成一个,使得 `inference_on_dataset` 只需接受一个评估器参数即可同时跑多项指标。
- **../modules/evaluation.html#detectron2.evaluation.COCOEvaluator**:支持 box detection、instance segmentation、keypoint detection 三类任务的 AP 计算,可作用于自定义数据集。
- **../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator**:提供语义分割指标评估,同样支持自定义数据集。

整体模块拓扑:**Models**(产出 outputs)→ **Datasets**(提供 inputs)→ **Evaluators**(消费 inputs/outputs),由 **inference_on_dataset** 作为粘合层完成端到端评估闭环。

---

## 【使用方法】

**1. 定义自定义评估器**(原文示例,实现 `reset / process / evaluate`):
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

**2. 手动调用评估器**(原文示例):
```python
def get_all_inputs_outputs():
    for data in data_loader:
        yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
    evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

**3. 一体化调用(推荐用法,原文示例)**:
```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```
其中 `COCOEvaluator(...)` 与 `Counter()` 的具体构造参数(如数据集名、配置)在原文中以 `...` 占位,**未给出**;需查阅对应模块 API 文档。原文亦未涉及 CLI 命令、配置文件项或训练脚本中的注册方式。
