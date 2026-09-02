# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/evaluation.md

# 一体化深度解读:RetinaNet/docs/tutorials/evaluation.md

## 【定位】

本文档系统描述了 detectron2 中**评估(Evaluation)能力**的设计与使用方法,核心围绕 `DatasetEvaluator` 抽象接口展开,讲解如何将模型的输入/输出对聚合成评测指标,以及如何通过 `inference_on_dataset` 配合多种 Evaluator 完成对自定义数据集的标准指标计算。

---

## 【技术要点】

1. **核心抽象接口 `DatasetEvaluator`**:detectron2 把评估建模为"接收若干 (inputs, outputs) 对并聚合指标"的接口,任何自定义评估器只需实现 `reset()` / `process(inputs, outputs)` / `evaluate()` 三方法。
2. **手写计数器示例 `Counter`**:通过对 `output["instances"]` 取 `len` 进行实例计数,展示了 `process` 中按 batch 累加、`evaluate` 返回 `{"count": self.count}` 字典的最小可用模式。
3. **`inference_on_dataset` 一站式推理+评估**:接受 `model`、`data_loader`、`DatasetEvaluators([...])`,一次性完成全数据集前向传播并把多个 Evaluator 合并执行。
4. **`DatasetEvaluators` 组合多个评估器**:可通过列表方式把例如 `COCOEvaluator(...)` 与 `Counter()` 同时挂载,避免对数据集做多次 forward pass。
5. **自定义数据集支持的两种通用 Evaluator**:`COCOEvaluator`(可对任意自定义数据集计算 AP,支持 box detection / instance segmentation / keypoint detection)与 `SemSegEvaluator`(可对任意自定义数据集计算语义分割指标)。
6. **配套数据集格式要求**:通用 Evaluator 依赖 detectron2 的标准数据集格式,引用 `./datasets.md` 作为前提条件。

---

## 【关键机制与数据】

- **工作原理(原文):** 评估过程被建模为一个 `DatasetEvaluator` 接口,接收若干 inputs/outputs 对并聚合;内部通过 `reset()` 初始化状态、`process(inputs, outputs)` 逐 batch 累积、`evaluate()` 输出最终字典结果。
- **数据流(原文):** `data_loader` 产出 `data` → `model(data)` 产出 `outputs` → 形成 `(inputs, outputs)` 对 → `evaluator.process(...)` 逐对处理 → `evaluator.evaluate()` 产出 `eval_results`(字典)。
- **性能数据(原文):** 文档未给出任何具体的数值型性能数据(如 FPS、AP、时延等);仅定性说明 `inference_on_dataset` "provides accurate speed benchmarks for the given model and dataset",即它能给出准确的速度基准,但未列出具体数字。

---

## 【表格解读】

**原文无表格。** 本文档没有包含任何参数表、性能对比表或配置项表格,所有信息均通过文字描述与代码片段给出。

---

## 【公式解读】

**原文无公式。** 本文档没有出现 LaTeX 数学公式或伪代码形式的算法表达式;其"逻辑结构"以 Python 代码片段呈现(例如 `Counter` 类的 `reset/process/evaluate` 三方法定义,以及 `for inputs, outputs in get_all_inputs_outputs(): evaluator.process(...)` 的循环)。这些代码片段应视为伪代码/调用模板,而非数学公式。

---

## 【关联】

本文档处于 detectron2 tutorials 体系中,与以下内容形成上下游/并列关系(基于文末内部链接):

- **./models.md**:作为"可直接用模型手动解析输入/输出做评估"的替代路径,与 `DatasetEvaluator` 抽象路径并列;若不想引入 Evaluator 抽象,可参照 `./models.md` 自己解析。
- **./datasets.md**:**前提条件**——通用 Evaluator(`COCOEvaluator`、`SemSegEvaluator`)能够作用于自定义数据集的前提是数据集遵循 detectron2 的标准数据集格式,该格式在 `./datasets.md` 中定义。
- **../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator**:**核心抽象**接口定义所在,本文所有 Evaluator 都实现该接口。
- **../modules/evaluation.html#detectron2.evaluation.inference_on_dataset**:**一键推理+评估**入口函数,接受 `model`、`data_loader`、`DatasetEvaluators([...])`。
- **../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators**:**Evaluator 组合容器**,允许把多个 `DatasetEvaluator` 合并,在一次 forward pass 中并行计算多项指标。
- **../modules/evaluation.html#detectron2.evaluation.COCOEvaluator**:**内置 Evaluator 之一**,可对任何遵循标准数据集格式的数据集计算 AP(box detection / instance segmentation / keypoint detection)。
- **../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator**:**内置 Evaluator 之一**,可对任何遵循标准数据集格式的数据集计算语义分割指标。

整体来看,本文档位于"**数据 → 模型 → 评测**"流水线的评测环节:上游依赖 `./datasets.md` 定义的数据格式与 `./models.md` 暴露的模型接口,下游通过 `DatasetEvaluator` 抽象族(`COCOEvaluator` / `SemSegEvaluator` / 自定义 Evaluator)输出结构化指标,并由 `DatasetEvaluators` 与 `inference_on_dataset` 提供组合与执行能力。

---

## 【使用方法】

1. **手动方式(原文):** 自己写生成器产生 `(data, model(data))`,循环调用 `evaluator.reset()` → `evaluator.process(inputs, outputs)` → `evaluator.evaluate()`,示例代码:
   ```
   def get_all_inputs_outputs():
     for data in data_loader:
       yield data, model(data)

   evaluator.reset()
   for inputs, outputs in get_all_inputs_outputs():
     evaluator.process(inputs, outputs)
   eval_results = evaluator.evaluate()
   ```

2. **推荐方式(原文):** 使用 `inference_on_dataset`,把 `model`、`data_loader` 与一组 `DatasetEvaluator`(通过 `DatasetEvaluators([...])` 合并)传入即可,示例:
   ```python
   eval_results = inference_on_dataset(
       model,
       data_loader,
       DatasetEvaluators([COCOEvaluator(...), Counter()]))
   ```

3. **自定义数据集评估(原文):** 注册/准备一个遵循 detectron2 标准数据集格式(`./datasets.md`)的数据集后,直接选用 `COCOEvaluator` 或 `SemSegEvaluator` 作为 Evaluator 即可对自定义数据集计算标准 AP / 语义分割指标,无需自行实现 API 适配。

4. **自定义评估逻辑(原文):** 继承 `DatasetEvaluator` 并实现 `reset` / `process(inputs, outputs)` / `evaluate` 三方法;`process` 中可访问 `output["instances"]` 等模型输出字段,`evaluate` 返回一个 `dict`(如 `{"count": self.count}`)作为指标结果。

> 原文未涉及:具体的命令行/Shell 启动方式、YAML 配置文件项、关键超参数(学习率、batch size 等)、性能数字、硬件/环境要求等——这些信息不在本文档范围内。
