# 教程 6: 自定义损失函数

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/customize_losses.md

# MMDetection 自定义损失函数文档深度解读

## 【定位】
本教程系统化地说明 MMDetection 目标检测框架中**损失函数的可定制机制**——既覆盖损失计算的完整五步流水线，也给出「微调（fine-tuning）」与「加权（weighting）」两种修改路径，并通过 Focal Loss 与 ATSSHead 两个具体实例展示如何在不同环节注入自定义逻辑，从而让用户在不修改源码主体的情况下适配新数据/新模型。

---

## 【技术要点】

1. **损失计算被抽象为五步流水线**：① 设置正负采样策略；② 通过损失核函数获得逐元素/逐样本的损失；③ 用权重张量（weight tensor）做逐元素加权；④ 将损失张量归约为标量（reduction）；⑤ 用一个标量（loss_weight）作为多任务学习中的整体权重。
2. **采样策略只在需要的损失上配置**：例如 RPN head 配合 `CrossEntropyLoss` 时需要在 `train_cfg` 中显式声明 `RandomSampler`；而 Focal Loss、GHMC、QualityFocalLoss 自带正负平衡机制，可省略采样步骤。
3. **Focal Loss 提供四个可调旋钮**：`use_sigmoid`（激活方式）、`gamma`（聚焦因子，默认 2.0）、`alpha`（类别平衡因子，默认 0.25）、`reduction`（'mean' 或 'sum'）、`loss_weight`（多任务权重，默认 1.0）。
4. **微调方式与五步流水线对应**：超参数修改对应「步骤 2」、reduction 修改对应「步骤 4」、loss_weight 修改对应「步骤 5」，全部可通过配置文件覆盖，无需改动源码。
5. **加权损失是逐元素（element-wise）操作**：通过与损失张量同形状的 `label_weights` / `bbox_weights` 实现正样本、难样本、忽略区域等差异化惩罚。
6. **`label_weights` 与 `bbox_weights` 由 head 的 `get_targets` 产生**：以 `ATSSHead` 为例，它继承 `AnchorHead` 并**重写** `get_targets` 方法以生成与上下文相符的权重张量。

---

## 【关键机制与数据】

### 工作原理：五步映射流水线

**原文：** *"给定输入（包括预测和目标，以及权重），损失函数会把输入的张量映射到最后的损失标量。"*

这条流水线把预测、目标、权重三类输入，按顺序经过采样 → 核函数 → 元素加权 → 归约 → 整体加权，最终输出单一标量 loss。下图（基于原文提炼）展示五个步骤的位置：

```
输入(预测+目标+权重) → [1]采样 → [2]核函数 → [3]逐元素权重 → [4]归约 → [5]整体权重 → loss标量
     ↑______________|                                  |____________|
      train_cfg.sampler                          loss_weight (标量)
                                            label_weights/bbox_weights (张量)
```

### 步骤 1 —— 采样（原文配置示例）

**原文：** RPN 中 `CrossEntropyLoss` 配套的 `RandomSampler` 配置：

```python
train_cfg=dict(
    rpn=dict(
        sampler=dict(
            type='RandomSampler',
            num=256,
            pos_fraction=0.5,
            neg_pos_ub=-1,
            add_gt_as_proposals=False))
```

数值含义（原文提及）：每轮采样 `num=256` 个候选，正样本占比 `pos_fraction=0.5`，负正比上限 `neg_pos_ub=-1`（不限制），并选择 `add_gt_as_proposals=False`（不把 GT 注入 proposal）。

### 步骤 2 —— 核函数超参数（原文 Focal Loss）

**原文：** `FocalLoss` 的构造签名与对应配置：

```python
@LOSSES.register_module()
class FocalLoss(nn.Module):
    def __init__(self,
                 use_sigmoid=True,
                 gamma=2.0,
                 alpha=0.25,
                 reduction='mean',
                 loss_weight=1.0):
```

```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=1.0)
```

原文将 **`gamma` 和 `beta`** 并列为 Focal Loss 的两个超参数（注：原文中 `beta` 与下文 `alpha` 不一致，此为原文原样表述，未予改动；后文示例只用到 `gamma` 与 `alpha`）。

### 步骤 3 —— 逐元素加权：ATSSHead 的 `get_targets`

**原文：** `ATSSHead.get_targets` 的方法签名：

```
class ATSSHead(AnchorHead):
    ...
    def get_targets(self,
                    anchor_list,
                    valid_flag_list,
                    gt_bboxes_list,
                    img_metas,
                    gt_bboxes_ignore_list=None,
                    gt_labels_list=None,
                    label_channels=1,
                    unmap_outputs=True):
```

ATSSHead 通过该方法得到 `label_weights`（分类逐元素权）与 `bbox_weights`（回归逐元素权），是「逐元素加权」机制的源头。

---

## 【表格解读】

**原文无表格。**

原文以代码配置块代替表格，关键等价「配置参数表」整理如下（仅为代码原文的紧凑复现，非原文表格）：

| 字段 | 原文默认值 | 原文示例 | 含义 |
|---|---|---|---|
| `type` | — | `'FocalLoss'` | 损失类名（注册器 key） |
| `use_sigmoid` | `True` | `True` | 是否对 logits 用 sigmoid |
| `gamma` | `2.0` | `1.5`（微调示例） | 聚焦因子 |
| `alpha` | `0.25` | `0.5`（微调示例） | 类别平衡因子 |
| `reduction` | `'mean'` | `'sum'`（微调示例） | 归约方式 |
| `loss_weight` | `1.0` | `0.5`（微调示例） | 多任务整体权重 |
| `sampler.num` | — | `256` | 采样总数 |
| `sampler.pos_fraction` | — | `0.5` | 正样本比例 |
| `sampler.neg_pos_ub` | — | `-1` | 负正样本比上限（-1 表示不限） |
| `sampler.add_gt_as_proposals` | — | `False` | 是否把 GT 作为 proposal |

---

## 【公式解读】

**原文无 LaTeX 公式。** 但原文对修改效果可用以下等价表达式刻画（仅为对原文参数机制的"忠实复述"，未引入原文未给出的算子）：

* **归约（步骤 4）**：`loss_scalar = reduction(loss_tensor)`，其中 `reduction ∈ {'mean', 'sum'}`，二选一后被映射为单一标量。
* **整体加权（步骤 5）**：`loss_final = loss_weight × loss_scalar`，`loss_weight` 为原文中明确给出的标量超参（如 `0.5`、`1.0`）。
* **逐元素加权（步骤 3）**：`loss_weighted[i,j,...] = label_weights[i,j,...] × loss_per_element[i,j,...]`，权重张量与元素损失形状一致，来自 head 的 `get_targets`。

> 说明：上述三条非原文中以数学公式显式给出，而是从代码配置（`reduction`、`loss_weight`、`get_targets`）与文字描述（「用权重张量来给损失逐元素权重」「用一个张量给当前损失一个权重」）直接对应而来。

---

## 【关联】

文档通过两条内部链接锚定到 MMDetection 源码（位于 `mmdet/models/` 目录下），构成清晰的依赖链：

* **Focal Loss 实现** → `mmdet/models/losses/focal_loss.py`（步骤 2/4/5 微调的承载类）。
* **ATSSHead** → `mmdet/models/dense_heads/atss_head.py`（`get_targets` 方法所在，约第 530 行；用于步骤 3 逐元素加权实例）。
* **AnchorHead** → `mmdet/models/dense_heads/anchor_head.py`（ATSSHead 的父类，原始 `get_targets` 的来源，ATSSHead 通过继承并**重写**得到自定义的 `label_weights` / `bbox_weights`）。

依赖关系可概括：

```
AnchorHead (基类)
   └─ ATSSHead (重写 get_targets → 自定义 label_weights/bbox_weights)
                 ↓
              loss_cls/loss_bbox ← FocalLoss (alpha/gamma/reduction/loss_weight)
                 ↑
          RPN 用 RandomSampler; FL/GHMC/QualityFocalLoss 自带正负平衡
```

因此本教程向上衔接「损失注册机制（`@LOSSES.register_module()`）」与「采样配置（`train_cfg.rpn.sampler`）」，向下衔接「各类 dense_heads 中的 `get_targets` 协议」与「`loss_xxx` 配置字典」。

---

## 【使用方法】

原文提供以下启用方式，均通过**配置文件（dict 风格）**完成，无需改源码：

1. **替换采样器**（步骤 1）—— 在对应 head 的 `train_cfg` 中设置 `sampler` 子字段，例如 RPN 的 `RandomSampler`：

   ```python
   train_cfg=dict(
       rpn=dict(
           sampler=dict(
               type='RandomSampler',
               num=256,
               pos_fraction=0.5,
               neg_pos_ub=-1,
               add_gt_as_proposals=False))
   ```

2. **微调超参数**（步骤 2）—— 修改 `gamma`、`alpha`（以 Focal Loss 为例）：

   ```python
   loss_cls=dict(
       type='FocalLoss',
       use_sigmoid=True,
       gamma=1.5,
       alpha=0.5,
       loss_weight=1.0)
   ```

3. **微调归约方式**（步骤 4）—— 添加 `reduction` 字段：

   ```python
   loss_cls=dict(
       type='FocalLoss', use_sigmoid=True,
       gamma=2.0, alpha=0.25,
       loss_weight=1.0, reduction='sum')
   ```

4. **微调损失整体权重**（步骤 5）—— 修改 `loss_weight`：

   ```python
   loss_cls=dict(
       type='FocalLoss', use_sigmoid=True,
       gamma=2.0, alpha=0.25,
       loss_weight=0.5)
   ```

5. **自定义逐元素加权**（步骤 3）—— 在自定义 head（如继承 `AnchorHead`）中重写 `get_targets`，使其返回与上下文相符的 `label_weights` / `bbox_weights`。

> 原文未涉及的项：CLI 启动命令、调参搜索范围、性能基准、特定数据集推荐值等，本文档均未提及。
