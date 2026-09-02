# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_losses.md

# 深度解读：MMDetection 自定义损失函数教程

---

## 【定位】

本文档系统讲解在 MMDetection 框架下如何自定义（customize）损失函数，涵盖损失计算的完整流水线、采样策略配置、超参数微调、归约方式切换、标量权重调整以及逐元素权重（element-wise weighting），以便用户针对不同数据集或模型调整损失行为。

---

## 【技术要点】

1. **损失计算五步流水线**（原文要点 1–5）：
   - Step 1：设定采样方法（sampling）
   - Step 2：通过损失核函数得到 **element-wise** 或 **sample-wise** 损失
   - Step 3：用 weight tensor 按元素加权
   - Step 4：将损失 tensor 归约为 **scalar**
   - Step 5：用 **scalar** 对损失再加权

2. **采样方法配置示例**（RPN head 配合 `CrossEntropyLoss`）：
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
   关键参数：`num=256`、`pos_fraction=0.5`、`neg_pos_ub=-1`、`add_gt_as_proposals=False`。

3. **带内建正负平衡机制的损失无需采样器**（原文）：Focal Loss、GHMC、QualityFocalLoss 自带平衡机制，sampler 不再必要。

4. **Focal Loss 默认构造参数**（原文）：
   - `use_sigmoid=True`
   - `gamma=2.0`
   - `alpha=0.25`
   - `reduction='mean'`
   - `loss_weight=1.0`

5. **Tweaking 包含四类修改**（原文 step 2/3/4/5 的可调点）：超参数、归约方式（mean→sum）、标量损失权重、逐元素权重；多数可通过 config 指定。

6. **两类的逐元素权重**（原文）：`label_weights`（用于分类损失）与 `bbox_weights`（用于 bbox 回归损失），定义在对应 head 的 `get_target` / `get_targets` 方法里。

---

## 【关键机制与数据】

**工作原理（原文所述流水线）**：

1. **输入**：预测（prediction）、目标（target）、权重（weights）。
2. **Step 1 — 采样**：选择正/负样本以缓解类别不平衡；并非所有损失都需要（如 FL/GHMC/QFL 自带机制）。
3. **Step 2 — 损失核函数计算**：得到 element-wise 或 sample-wise 的损失张量。
4. **Step 3 — 元素加权**：loss tensor 与同形 weight tensor 逐元素相乘，对 loss 中不同 entry 做差异化缩放。
5. **Step 4 — 归约（reduction）**：将张量归约为单个 scalar，可选 `'mean'` 或 `'sum'`。
6. **Step 5 — 标量加权**：最终 scalar 与一个标量权重相乘，控制在多任务（分类 loss + 回归 loss）中的相对重要性。

**Tweaking vs Weighting 分类**（原文）：
- **Tweaking**：与 step 2、4、5 相关，主要通过 config 完成（修改 hyper-parameter、reduction、loss_weight）。
- **Weighting**：与 step 3 相关（element-wise），需在 head 的 `get_targets` 方法里输出不同的 `label_weights` 与 `bbox_weights`。

**原文给出的具体数字/配置示例**：
- RandomSampler：`num=256, pos_fraction=0.5, neg_pos_ub=-1, add_gt_as_proposals=False`
- FL 默认：`gamma=2.0, alpha=0.25, reduction='mean', loss_weight=1.0`
- FL 自定义示例 1：`gamma=1.5, alpha=0.5, loss_weight=1.0`
- FL 自定义示例 2：`reduction='sum'`
- FL 自定义示例 3：`loss_weight=0.5`（分类 loss 权重降到 0.5）

> 注：原文未给出训练/推理性能数据（如 mAP、耗时等），仅为配置说明文档。

---

## 【表格解读】

**原文无表格**。

文档以代码片段与分步说明形式描述内容，未包含参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式**。

文档未显式写出 Focal Loss 的 LaTeX 数学形式或伪代码公式；仅以类构造签名（`__init__` 参数列表）和配置 dict 的形式呈现可调量。

---

## 【关联】

根据文末内部链接，文档关联到以下源码/模块：

1. **Focal Loss 实现**：`mmdet/models/losses/focal_loss.py` —— 作为 Tweaking 章节的示例损失，被 `@LOSSES.register_module()` 注册。
2. **ATSSHead**：`mmdet/models/dense_heads/atss_head.py`（锚点 `L530` 起）—— 作为 Weighting 章节的示例 head，其覆写了 `get_targets` 方法以产出自定义的 `label_weights` 与 `bbox_weights`。
3. **AnchorHead**（`mmdet/models/dense_heads/anchor_head.py`）—— ATSSHead 的父类，提供默认 `get_targets`。

**与其他教程/章节的逻辑关系**（基于文档标题与编号推断，非文档明文）：
- 属于"Tutorial 6"，属于 MMDetection 自定义系列教程（Tutorials 序列）的一部分，紧接其它自定义教程（如模型、数据、配置等）。
- 是"如何自定义 loss"这一上游配置/建模能力，与 head（ATSSHead/AnchorHead）和训练配置（`train_cfg`）耦合。

> 内部链接字段为"（无）"，以上链接均来自原文正文中给出的 GitHub URL。

---

## 【使用方法】

### 1) 修改采样方法（step 1）

在 `train_cfg` 中设置 `sampler`，以 `RandomSampler` 为例：

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

> 仅在所用损失本身**无**正负样本平衡机制（如 `CrossEntropyLoss`）时需要；若使用 Focal Loss / GHMC / QualityFocalLoss，可省略。

### 2) Tweaking 超参数（step 2）

```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=1.5,    # 原默认 2.0
    alpha=0.5,    # 原默认 0.25
    loss_weight=1.0)
```

### 3) Tweaking 归约方式（step 4）

```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=1.0,
    reduction='sum')   # 原默认 'mean'
```

### 4) Tweaking 标量损失权重（step 5）

```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=0.5)   # 原默认 1.0
```

### 5) Weighting（step 3，逐元素权重）

- 通过覆写 head 的 `get_targets` 方法，在返回值中提供与 loss tensor 同形的 `label_weights`、`bbox_weights`。
- 示例：在 `ATSSHead.get_targets`（继承自 `AnchorHead`）中定制权重张量。

> 启动命令、数据集/配置文件路径等在原文中未涉及。
