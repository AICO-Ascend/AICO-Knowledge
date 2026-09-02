# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/evaluation.md

# 深度解读:CascadedMaskRCNN Evaluation 教程文档

---

## 【定位】

这篇文档描述 detectron2 评估(Evaluation)框架的能力——通过 `DatasetEvaluator` 接口对模型在验证集上的预测结果做统一的输入/输出对聚合与指标计算,从而无需用户手动解析模型输出即可完成检测、分割等任务的离线评测。

---

## 【技术要点】

1. **核心抽象接口**:评估功能由 `DatasetEvaluator` 接口实现,文档同时提供手动循环(`reset → process → evaluate`)与 `inference_on_dataset` 高级接口两种使用方式。
2. **三段式 API 协议**:任何自定义 evaluator 需实现 `reset()`(清零状态)、`process(inputs, outputs)`(逐 batch 累积)、`evaluate()`(返回结果字典,如 `{"count": self.count}`)三个方法。
4. **多 evaluator 合并机制**:多个 evaluator 可通过 `DatasetEvaluators([...])` 包装类合并,在**一次**模型前向传播中并行处理,避免重复推理。
5. **内置通用 evaluator**:`COCOEvaluator` 支持**任意自定义数据集**(只要遵循 detectron2 标准数据集格式)的 box detection、instance segmentation、keypoint detection 的 AP 指标;`SemSegEvaluator` 支持**任意自定义数据集**的语义分割指标。
6. **额外收益**:`inference_on_dataset` 还会给出给定模型与数据集的精确速度基准(speed benchmark)。

---

## 【关键机制与数据】

**原文工作原理与数据流**(基于原文描述):

- **数据流**:`data_loader` 提供输入 → `model(data)` 产生输出 → 每对 `(inputs, outputs)` 被送入 evaluator 的 `process()` 方法 → 最后调用 `evaluate()` 得到聚合指标。
- **手动模式 vs 高阶模式**:
  - 手动模式由用户自己驱动 `for inputs, outputs in get_all_inputs_outputs(): evaluator.process(...)`。
  - 高阶模式直接调用 `inference_on_dataset(model, data_loader, DatasetEvaluators([...]))`,该函数内部执行整个前向传播并把每个 batch 派发给 evaluator。
- **合并执行的关键优势**(原文):"all the evaluation can finish in **one forward pass** over the dataset"——即多个 evaluator 共享同一次推理结果,而不是每个 evaluator 都重新跑一遍模型。
- **性能基准**:原文仅定性提到"accurate speed benchmarks for the given model and dataset",**未给出具体数字**。
- **指标范围**:原文列出的指标包括 AP(Average Precision,用于 box detection / instance segmentation / keypoint detection)与语义分割指标(semantic segmentation metrics),但**未列出具体数值或阈值**。

---

## 【表格解读】

**原文无表格。**

整篇教程通过代码片段与文字描述传达内容,未出现任何 markdown 或文本形式的表格(无参数表、无性能对比表、无配置项表)。

---

## 【公式解读】

**原文无公式。**

文档中既无 LaTeX 数学公式,也无伪代码形式的算式表达。仅有的"代码块"为 Python 类定义与函数调用片段,属【使用方法】范畴。

---

## 【关联】

依据文末内部链接,本教程与以下特性/模块存在上下游关系:

- **上游/数据来源**:
  - [./datasets.md](./datasets.md)——`COCOEvaluator` 与 `SemSegEvaluator` 能评测"任意自定义数据集"的前提是遵循 detectron2 的**标准数据集格式**(standard dataset format),该格式在 `./datasets.md` 中定义。
- **下游/模型侧**:
  - [./models.md](./models.md)——文档首句即提示"You can always use the model directly"指向此链接,意味着评估逻辑建立在 [./models.md](./models.md) 给出的模型接口之上。
- **核心 API 模块**(均位于 `../modules/evaluation.html`):
  - [DatasetEvaluator](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator)——评估器抽象基类,本教程所有自定义 evaluator 都继承它。
  - [inference_on_dataset](../modules/evaluation.html#detectron2.evaluation.inference_on_dataset)——一键执行"前向传播 + evaluator 派发"的高阶函数。
  - [DatasetEvaluators](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators)——多 evaluator 合并容器,使多个评估共享一次推理。
  - [COCOEvaluator](../modules/evaluation.html#detectron2.evaluation.COCOEvaluator)——内置 COCO 风格 AP 评估器,可作用于自定义数据集。
  - [SemSegEvaluator](../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator)——内置语义分割评估器,可作用于自定义数据集。

整体来看,该教程处于 **模型 → 评估** 流水线的末端,以 `./datasets.md` 定义的数据格式为输入契约,以 `./models.md` 给出的模型对象为被测对象,通过 `DatasetEvaluator` 抽象族完成指标计算。

---

## 【使用方法】

**启用方式与配置项**(原文给出):

- **手动模式启用**:
  ```python
  def get_all_inputs_outputs():
      for data in data_loader:
          yield data, model(data)

  evaluator.reset()
  for inputs, outputs in get_all_inputs_outputs():
      evaluator.process(inputs, outputs)
  eval_results = evaluator.evaluate()
  ```

- **高阶模式启用**(推荐,合并多个 evaluator):
  ```python
  eval_results = inference_on_dataset(
      model,
      data_loader,
      DatasetEvaluators([COCOEvaluator(...), Counter()]))
  ```

- **自定义 evaluator 模板**(原文 `Counter` 示例):
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
  关键点:继承 `DatasetEvaluator`、实现三方法、`evaluate()` 返回 dict。

- **依赖前置条件**:若要使用 `COCOEvaluator` 或 `SemSegEvaluator` 评测自定义数据集,数据集必须遵循 `./datasets.md` 中定义的 detectron2 **标准数据集格式**(原文明确点出此前提)。

- **可选替代方案**:原文明确指出可绕过整套 evaluator 框架,直接 [use the model](./models.md) 并手动 parse 其 inputs/outputs 来评估,但未给出该手动解析路径的代码细节。

**原文未涉及**的部分:具体命令行启动方式(CLI)、配置文件 YAML 字段、性能数字、阈值参数等均未在本教程中出现。
