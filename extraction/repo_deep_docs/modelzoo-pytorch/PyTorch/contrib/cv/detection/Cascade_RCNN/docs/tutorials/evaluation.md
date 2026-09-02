# Evaluation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/evaluation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/evaluation.md

# 一体化深度解读: Cascade_RCNN/docs/tutorials/evaluation.md

## 【定位】
本文档描述 detectron2 中"评估(Evaluation)"的统一接口与使用范式: 如何对一个数据集上的模型输出做聚合、统计与指标计算, 并通过 `DatasetEvaluator` / `inference_on_dataset` 等原语把评估流程标准化。

---

## 【技术要点】

1. **评估的本质**: 评估是一段"接受若干 `(inputs, outputs)` 对并做聚合"的流程; 用户既可直接调用模型并自行解析输出, 也可以借助 detectron2 提供的 `DatasetEvaluator` 接口。
2. **三类内置标准评估器**: detectron2 内置若干基于标准数据集官方 API 的 `DatasetEvaluator`(如 COCO、LVIS); 同时提供可在"任意符合 detectron2 标准数据集格式"的自定义数据集上工作的两类通用评估器:
   - **`COCOEvaluator`** —— 可对自定义数据集计算 **box detection、instance segmentation、keypoint detection 的 AP(Average Precision)**;
   - **`SemSegEvaluator`** —— 可对自定义数据集计算**语义分割(semantic segmentation)指标**。
3. **`DatasetEvaluator` 三段式接口**: 每个评估器都暴露 `reset()` → `process(inputs, outputs)` → `evaluate()` 三个方法, 用户也可继承 `DatasetEvaluator` 实现自定义评估(例如统计验证集上检测到的实例总数 `Counter`)。
4. **手动评估与自动评估**: 既可手动循环 `reset / process / evaluate`, 也可直接调用 `inference_on_dataset(model, data_loader, evaluator)`; 后者会代为执行模型前向并喂给评估器。
5. **多评估器合并**: 通过 `DatasetEvaluators([evaluator1, evaluator2, ...])` 把多个评估器组合起来, `inference_on_dataset` 会**在一次完整的数据集 forward pass 内同时完成所有评估**, 避免重复推理。
6. **附带速度基准**: `inference_on_dataset` 还会在评估过程中给出"对指定模型与数据集的精确速度基准"(accurate speed benchmarks)。

---

## 【关键机制与数据】

### 工作原理 / 数据流

1. **核心抽象**:`DatasetEvaluator` 把评估抽象成"输入/输出流"——
   - `reset()`: 初始化/清零内部状态(例如 `self.count = 0`);
   - `process(inputs, outputs)`: 每来一个 batch 推完模型后被调用一次, 消费一组 `(inputs, outputs)`, 累计信息;
   - `evaluate()`: 遍历结束后被调用, 输出最终结果(例如返回 `{"count": self.count}`)。
2. **手动执行流程**(原文示例模式):
   ```
   get_all_inputs_outputs()  →  对 data_loader 中每个 data 跑 model(data), yield (data, model_output)
   evaluator.reset()
   for (inputs, outputs) in get_all_inputs_outputs():
       evaluator.process(inputs, outputs)
   eval_results = evaluator.evaluate()
   ```
3. **自动执行流程**(推荐写法):
   ```
   eval_results = inference_on_dataset(
       model, data_loader,
       DatasetEvaluators([COCOEvaluator(...), Counter()]))
   ```
   `inference_on_dataset` 内部会: 对 `data_loader` 中每个 batch 调用 `model`, 拿到 `outputs`, 然后分发给传入的评估器(们), 最后调用 `evaluate()` 汇总。
4. **自定义评估器示例**:`Counter` 通过累加 `outputs[i]["instances"]` 长度统计"验证集上总共检测出多少个实例", 最后用 `evaluate()` 返回 dict; 文档未给出具体数值, 仅展示接口形状。
5. **性能/速度收益**: 原文明确点出 `inference_on_dataset` 的两个收益——
   - **合并多评估器**: `DatasetEvaluators` 把多个评估器串成一个, **一次前向完成所有评估**;
   - **精确速度基准**: 同时输出给定 `model` + `dataset` 组合下的 timing。

### 性能数据
**原文未给出具体的数值、AP、吞吐或时延指标**, 仅在概念层面描述了"评估可在一次前向内完成"以及"附带准确的速度基准"。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档在评估流程上串联了下述组件, 构成完整的"推理 → 评估"链路:

- **[`./models.md`](./models.md)**: 文档开篇即提到 "你可以总是直接[使用模型](./models.md)", 即评估既可绕过框架自行 `model(inputs)` 后手工解析输出, 也可以走本文介绍的 `DatasetEvaluator` 路径——`./models.md` 是"直接用模型"那一支的入口。
- **[`./datasets.md`](./datasets.md)**: 通用评估器(`COCOEvaluator`、`SemSegEvaluator`)能在"任意符合 detectron2 标准数据集格式"的自定义数据集上工作, `datasets.md` 即定义这一标准数据集格式的文档, 是使用这两个评估器的前提。
- **[`detectron2.evaluation.DatasetEvaluator`](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluator)**: 评估器接口的基类, 文档中的 `reset / process / evaluate` 三段式以及 `Counter` 示例都基于此。
- **[`detectron2.evaluation.inference_on_dataset`](../modules/evaluation.html#detectron2.evaluation.inference_on_dataset)**: 推荐的"一行式"评估入口函数, 内部串联 model + data_loader + evaluator; 也是获取"精确速度基准"的入口。
- **[`detectron2.evaluation.DatasetEvaluators`](../modules/evaluation.html#detectron2.evaluation.DatasetEvaluators)**: 多评估器合并容器, `inference_on_dataset` 接受它之后可在一次前向内跑完所有评估。
- **[`detectron2.evaluation.COCOEvaluator`](../modules/evaluation.html#detectron2.evaluation.COCOEvaluator)**: 计算 box detection / instance segmentation / keypoint detection AP 的标准评估器, 既支持 COCO 类官方数据集, 也支持自定义数据集。
- **[`detectron2.evaluation.SemSegEvaluator`](../modules/evaluation.html#detectron2.evaluation.SemSegEvaluator)**: 计算语义分割指标的评估器, 同样支持自定义数据集。

上下游关系可以概括为:**`datasets.md`(数据格式) → `models.md`(模型前向) → `DatasetEvaluator` 体系(`COCOEvaluator` / `SemSegEvaluator` / 自定义子类) → 由 `DatasetEvaluators` 合并 → 经 `inference_on_dataset` 一次性调度 → 输出 eval 结果 + 速度基准**。

---

## 【使用方法】

### 启用方式 1 — 手动调用评估器三段式
适用于需要把模型推理与评估解耦、自己控制循环的场景:

```
def get_all_inputs_outputs():
    for data in data_loader:
        yield data, model(data)

evaluator.reset()
for inputs, outputs in get_all_inputs_outputs():
    evaluator.process(inputs, outputs)
eval_results = evaluator.evaluate()
```
关键步骤(来自原文):
1. 提供一个生成 `(data, model(data))` 的迭代器 `get_all_inputs_outputs()`;
2. 先 `evaluator.reset()` 清零;
3. 对每对 `(inputs, outputs)` 调 `evaluator.process(...)`;
4. 数据集跑完后调 `evaluator.evaluate()` 拿到 `eval_results`。

### 启用方式 2 — `inference_on_dataset`(推荐)
把模型、数据加载器、评估器一起交给函数:

```python
eval_results = inference_on_dataset(
    model,
    data_loader,
    DatasetEvaluators([COCOEvaluator(...), Counter()]))
```
关键配置项:
- `model`: 任意 detectron2 模型(或行为兼容的对象), 需支持 `model(data)`;
- `data_loader`: 提供验证/测试数据迭代;
- 第三个参数接受单个 `DatasetEvaluator`, 也可传 `DatasetEvaluators([...])` 合并多个评估器(例如原文示例同时传入 `COCOEvaluator` 与自定义 `Counter`)。
返回值: `eval_results` 字典(来自 `evaluator.evaluate()`), 同时附带速度基准信息。

### 自定义评估器
继承 `DatasetEvaluator` 实现三个方法: `reset()`、`process(inputs, outputs)`、`evaluate()`, 例如原文中的 `Counter` 累加 `len(output["instances"])` 并返回 `{"count": self.count}`; 可与 `inference_on_dataset` 配合使用。

### 适用场景速查
- **任意自定义数据集的检测/实例分割/关键点 AP**: 用 `COCOEvaluator`;
- **任意自定义数据集的语义分割指标**: 用 `SemSegEvaluator`;
- **同时跑多指标**: 用 `DatasetEvaluators([...])` 包裹后传给 `inference_on_dataset`, 一次前向完成。
