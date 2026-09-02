# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_losses.md

# 深度解读:Tutorial 6: Customize Losses

## 【定位】
这篇文档解决"MMDetection 默认损失函数配置在特定数据集或模型上不适用时,如何按步骤修改损失"的问题,系统描述了损失从预测/目标张量到最终标量的计算流水线,以及在配置层面进行 tweaking(微调)与 weighting(加权)两类自定义操作的完整方法。

## 【技术要点】

1. **损失计算流水线分四步**(原文显式列出):① 由损失核函数得到 element-wise / sample-wise 损失;② 用 weight tensor 做 element-wise 加权;③ 将损失张量 reduce 为 scalar;④ 用 scalar 做整体加权。
2. **Tweaking 与 Weighting 的二分法**:tweaking 对应步骤 1、3、4(超参数、reduction、loss_weight),主要通过 config 修改;weighting 对应步骤 2(element-wise 加权),依赖 head 的 `get_targets` 产生的 `label_weights` 与 `bbox_weights`。
3. **以 Focal Loss 为示例的 config 一一映射关系**:Python 构造器 `__init__` 的参数与 config 字典中的键名一一对应(`use_sigmoid / gamma / alpha / reduction / loss_weight`)。
4. **可调超参数(步骤 1)**:Focal Loss 的 `gamma`(原文示例默认值 2.0,修改示例改为 1.5)与 `alpha`(原文默认值 0.25,修改示例改为 0.5)。
5. **可调 reduction 方式(步骤 3)**:Focal Loss 默认 `reduction='mean'`,可改为 `'sum'`。
6. **可调 loss weight(步骤 4)**:多任务学习中控制分类/回归损失的 scalar 权重,原文示例将 `loss_weight` 由 1.0 改为 0.5。

## 【关键机制与数据】

### 工作原理(原文:"The mapping can be divided into four steps")

**原文:** 损失计算管线分为 4 步:
1. Get **element-wise** or sample-wise loss by the loss kernel function.
2. Weighting the loss with a weight tensor **element-wisely**.
3. Reduce the loss tensor to a **scalar**.
4. Weighting the loss with a **scalar**.

**数据流(原文:"Given the input prediction and target, as well as the weights, a loss function maps the input tensor to the final loss scalar.")** 即:prediction + target + weights → (kernel) → element-wise loss → (× weight tensor) → weighted loss → (reduction) → scalar → (× scalar loss_weight) → final loss scalar。

### 性能数据
原文未涉及任何性能数据(无 mAP、无推理时延、无训练 epoch/iteration 数等指标)。

### Tweaking — 修改前后配置对比(原文配置块,关键数值保留):

| 修改项 | 默认配置(原文) | 修改后配置(原文) | 生效步骤 |
|---|---|---|---|
| `gamma` | `2.0` | `1.5` | 步骤 1(超参数) |
| `alpha` | `0.25` | `0.5` | 步骤 1(超参数) |
| `reduction` | `'mean'` | `'sum'` | 步骤 3(reduction) |
| `loss_weight` | `1.0` | `0.5` | 步骤 4(scalar 加权) |

### Weighting 的两类权重张量(原文:"overall there are two kinds of loss weights")
- **`label_weights`** —— 用于分类损失
- **`bbox_weights`** —— 用于 bbox 回归损失
- 来源:`get_target` / `get_targets` 方法(原文以 `ATSSHead.get_targets` 为例,继承自 `AnchorHead` 并被覆写以产出不同的 `label_weights` 与 `bbox_weights`)。

## 【表格解读】
**原文无表格。** 原文以多个并列的 Python config 代码块(`dict(type='FocalLoss', ...)`)形式展示参数,而非表格。

## 【公式解读】
**原文无公式。** 原文未给出 LaTeX 或伪代码形式的损失表达式,虽然提到了 Focal Loss 涉及 `gamma`、`alpha`、`use_sigmoid`,但未写出 FL 的标准数学形式(如 $-\alpha_t (1-p_t)^\gamma \log p_t$),亦未列出 loss 管线各步的数学表达式。

## 【关联】

### 文档自身的引用关系
- **Focal Loss 实现**:原文链接到 `mmdet/models/losses/focal_loss.py`,作为 tweaking 的演示载体。
- **ATSSHead**:原文链接到 `mmdet/models/dense_heads/atss_head.py` 的 `get_targets` 方法(标注行号 L530),作为 weighting 的演示载体。
- **AnchorHead**:原文指出 `ATSSHead` 继承自 `mmdet/models/dense_heads/anchor_head.py`,但覆写了 `get_targets`,因此产生不同的 `label_weights`/`bbox_weights`。

### 在流水线中的上下游关系
- 上游:`loss_kernel` → element-wise 损失(对应模型 head 的输出 prediction 与 dataset 产生的 target/gt);
- 中游:`head.get_targets()` 产出 `label_weights` / `bbox_weights`(步骤 2 的输入);
- 下游:`loss_cls` / `loss_bbox` 的 scalar 之和(或加权组合)进入 total loss,反向传播更新模型参数。

### 与文中其他特性的耦合
- **多任务学习**:步骤 4 的 `loss_weight` 是控制 `loss_cls` 与 `loss_bbox` 之间相对权重的 scalar,直接决定多任务梯度平衡。
- **不同 reduction 策略**:步骤 3 的 `mean` vs `sum` 会同时影响 loss 量级与梯度尺度,需要与步骤 4 的 `loss_weight` 协同考虑。

## 【使用方法】

### 启用方式
原文未涉及"如何注册/启用一个新损失"的完整流程(例如 `@LOSSES.register_module()` 仅作为代码片段出现于 `FocalLoss` 类定义旁,未展开 registry 机制说明)。可观察到的是:凡在 `loss_cls` / `loss_bbox` config 中指定 `type='FocalLoss'`,即按 `LOSSES.register_module` 注册路径查找并实例化。

### 配置项(原文显式给出的 config 修改范式)

**1) 修改超参数(步骤 1)**——原文示例:
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=1.5,
    alpha=0.5,
    loss_weight=1.0)
```

**2) 修改 reduction(步骤 3)**——原文示例:
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=1.0,
    reduction='sum')
```

**3) 修改 loss_weight(步骤 4)**——原文示例:
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=0.5)
```

### 命令
原文未涉及任何命令行(无 `python tools/train.py`、`mmdet` CLI、shell 命令等)。所有修改均通过修改 config 文件中的 Python 字典完成。

### Weighting(步骤 2)的修改入口
原文未给出 config 层的直接修改方法,而是指向 head 的代码侧:查看/修改对应 head 的 `get_targets`(或 `get_target`)方法中产生 `label_weights` 与 `bbox_weights` 的逻辑(以 `ATSSHead.get_targets` 为参考样例)。
