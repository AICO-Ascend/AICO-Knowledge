# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/evaluation.md

# 一体化深度解读:Detectron2 Evaluation 指南

---

## 【定位】

这篇文档描述 Detectron2 中评估（Evaluation）能力的统一抽象与使用方式,即如何通过 `DatasetEvaluator` 接口把模型对 (输入, 输出) 数据对的处理结果按数据集官方 API 聚合为指标,并提供手动调用与基于 `inference_on_dataset` 的两种典型执行路径。

---

## 【技术要点】

1. **统一抽象接口 `DatasetEvaluator`**:Detectron2 把评估抽象成 `DatasetEvaluator` 接口,任何评估器都通过 `reset()`、`process(inputs, outputs)`、`evaluate()` 三个方法完成一轮完整评估;内置评估器针对 COCO、LVIS 等数据集的标准 API 计算 AP 等指标;也允许用户继承该接口实现自定义评估器(如文中的 `Counter` 示例)。
2. **手动执行模式**:`reset()` → 循环 `process(inputs, outputs)` → `evaluate()` 三段式,以生成器形式逐批对齐 `data_loader` 与 `model(data)` 的输出。
3. **`inference_on_dataset` 一次性合并执行**:将 `model`、`data_loader` 与 `DatasetEvaluators([evaluator1, evaluator2, ...])` 组合,可对数据集只做一次前向传播就完成多种评估;在性能上"provides accurate speed benchmarks for the given model and dataset"。
4. **自定义数据集可用评估器**:符合 detectron2 [standard dataset format](./datasets.md) 的自定义数据集,可使用 `COCOEvaluator`(框检测/实例分割/关键点 AP)与 `SemSegEvaluator`(语义分割指标)两种通用评估器。
5. **可直接调用模型自行解析**:`You can always [use the model](./models.md) directly and just parse its inputs/outputs manually to perform evaluation`, 即评估并非强制依赖 `DatasetEvaluator` 体系。
6. **多评估器合并机制**:`DatasetEvaluators` 容器可以把多个评估器合并起来,通过一次遍历数据得到所有评估结果。

---

## 【关键机制与数据】

**工作原理 (原文阐述)**:

- 评估过程"takes a number of inputs/outputs pairs and aggregate them";本质是对 `(inputs, outputs)` 列表做聚合。
- 标准接口 `DatasetEvaluator` 描述了一次评估生命周期:
  - **`reset()`**——清空/初始化评估器内部状态(如 `Counter.count = 0`)。
  - **`process(inputs, outputs)`**——每批 `(inputs, outputs)` 调用一次,把每条 `output` 中的预测结果纳入计数(原文示例:`self.count += len(output["instances"])`)。
  - **`evaluate()`**——遍历结束后,导出/返回指标字典(原文示例:`return {"count": self.count}`)。
- **手动模式数据流 (原文)**:
  ```
  def get_all_inputs_outputs():
    for data in data_loader:
      yield data, model(data)

  evaluator.reset()
  for inputs, outputs in get_all_inputs_outputs():
    evaluator.process(inputs, outputs)
  eval_results = evaluator.evaluate()
  ```
  即**生成器产生 `(data, model(data))` 对 → 重置评估器 → 逐批 process → 汇总 evaluate**。
- **`inference_on_dataset` 数据流 (原文)**:
  ```python
  eval_results = inference_on_dataset(
      model,
      data_loader,
      DatasetEvaluators([COCOEvaluator(...), Counter()]))
  ```
  原文描述:"This will execute `model` on all inputs from `data_loader`, and call evaluator to process them.", 即对数据集中每个输入执行一次 `model`,再交给 `DatasetEvaluators` 中每个评估器处理;相比手写循环的优势是 "evaluators can be merged together using `DatasetEvaluators`, and all the evaluation can finish in one forward pass over the dataset"。
- **自定义数据集评估 (原文)**:`COCOEvaluator` 能够对任意符合标准格式的数据集"evaluate AP (Average Precision) for box detection, instance segmentation, keypoint detection";`SemSegEvaluator` 能够"evaluate semantic segmentation metrics on any custom dataset";前提是数据集遵循 detectron2 的 standard dataset format。
- **性能数据 (原文)**:"This function also provides accurate speed benchmarks for the given model and dataset." —— 即 `inference_on_dataset` 会输出给定模型与数据集下的准确速度基准。无具体数字。

---

## 【表格解读】

**原文无表格**。原文仅包含两段 Python 代码示例(`Counter` 自定义评估器与 `inference_on_dataset` 调用),未出现任何结构化参数表、对比表或配置表。

---

## 【公式解读】

**原文无公式**。文中给出的均为可执行 Python 代码片段,无 LaTeX 数学公式或形式化算法表达。两段代码逐字保留如下以便核查:

1. 自定义评估器示例:
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
   其中 `output["instances"]` 表示 Detectron2 模型对单张图输出的 `Instances` 预测对象,`len()` 取其检测到的实例数。
2. `inference_on_dataset` 调用示例:
   ```python
   eval_results = inference_on_dataset(
       model,
       data_loader,
       DatasetEvaluators([COCOEvaluator(...), Counter()]))
   ```

---

## 【关联】

依据文中文末出现过的内部链接对象,可梳理出如下上下游关系:

- **`./models.md`** — 文档开篇即指出"可以直接使用模型并手动解析输入输出完成评估",把 `models.md` 作为不依赖评估体系的备用路径。两者在文档结构上构成并列:**自定义手写评估** vs **`DatasetEvaluator` 体系评估**。
- **`../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator`** — 是整篇文档的核心抽象接口,所有内置与自定义评估器都继承自它;属于被反复引用的"基类"角色。
- **`../modules/evaluation.html#detectron2.evaluation.inference_on_dataset`** — 与 `DatasetEvaluator`、`DatasetEvaluators` 协同的官方便利函数,定位"评估调度器/编排器":在一次前向中调用多个评估器。
- **`../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators`** — 多评估器合并容器;与 `inference_on_dataset` 紧密耦合,为后者一次遍历产生多种结果提供机制。
- **`./datasets.md`** — 是"自定义数据集评估"一节的前置依赖;只有符合 `datasets.md` 所定义的 standard dataset format,`COCOEvaluator`、`SemSegEvaluator` 才能在自定义数据上工作。
- **`../modules/evaluation.html#detectron2.evaluation.COCOEvaluator`** — 内置评估器,适用场景:任意数据集(满足标准格式)的框检测 / 实例分割 / 关键点 AP 评估;面向通用自定义数据集。
- **`../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator`** — 内置评估器,适用场景:任意数据集(满足标准格式)的语义分割指标;面向通用自定义数据集。

整体关系可视为:**`models.md`(模型)→ `DatasetEvaluator`(接口)→ `COCOEvaluator` / `SemSegEvaluator` / 用户子类(具体实现)→ 通过 `DatasetEvaluators` 合并 → 由 `inference_on_dataset` 驱动执行,目标数据须遵循 `datasets.md` 的标准格式**。

---

## 【使用方法】

依据原文信息,启用方式分为三层:

**1. 直接手动评估(无需评估器,原文已给示例)**
```python
def get_all_inputs_outputs():
  for data in data_loader:
    yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
  evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```

**2. 使用内置评估器对标准数据集/自定义数据集评估(原文示例)**
```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```
其中 `COCOEvaluator(...)` 需要传入符合 detectron2 标准数据集格式的数据集/标注参数(具体参数细节在 [模块页](../modules/evaluation.html#detectron2.evaluation.COCOEvaluator),原文未细化)。

**3. 自定义评估器(原文示例,继承 `DatasetEvaluator`)**
实现 `reset` / `process(inputs, outputs)` / `evaluate` 三个方法;`process` 接收一个 batch 的 `(inputs, outputs)` 列表,`evaluate` 返回指标字典;之后即可像内置评估器一样被 `DatasetEvaluators` 包裹并由 `inference_on_dataset` 调用。

**关于配置项 / 命令行开关**:原文未涉及任何配置文件项或 CLI 命令(无 cfg、launch、train_net 等关键词),仅 API 调用式使用。
