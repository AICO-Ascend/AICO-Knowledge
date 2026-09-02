# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_losses.md

# 深度解读:MMDetection 自定义损失函数 (Tutorial 6: Customize Losses)

## 【定位】

这篇文档是 MMDetection 的官方教程 (Tutorial 6),解决「如何根据不同数据集/模型的需求,定制/调整检测框架中的损失函数」的问题,系统化地阐述损失计算的完整流程并提供「微调 (Tweaking)」与「加权 (Weighting)」两大类修改方法。

---

## 【技术要点】

1. **损失计算五步流水线** (原文核心框架):① 采样正负样本 → ② 通过损失核函数得到 element-wise/sample-wise loss → ③ 用 weight tensor **逐元素**加权 → ④ 将 loss tensor 归约为 **scalar** → ⑤ 用 **scalar** 再次加权。
2. **采样策略示例**:RPN head 使用 `CrossEntropyLoss` 时,在 `train_cfg` 中配置 `RandomSampler`,关键参数为 `num=256, pos_fraction=0.5, neg_pos_ub=-1, add_gt_as_proposals=False`。
3. **自带正负平衡的损失**:Focal Loss、GHMC、QualityFocalLoss 内部已含正负样本平衡机制,因此**不再需要外部 sampler**。
4. **Tweaking 维度**:针对步骤 ②/④/⑤ 可在 config 中修改超参数 (γ、α)、reduction 方式 (`mean`/`sum`)、`loss_weight` 标量。
5. **Weighting 维度**:针对步骤 ③ 涉及 element-wise 加权,典型为 `label_weights` (分类) 与 `bbox_weights` (bbox 回归),由对应 head 的 `get_targets` 方法产生。
6. **继承与覆写模式**:以 `ATSSHead` 为例,继承 `AnchorHead` 后**覆写 `get_targets` 方法**即可产生不同的 `label_weights` 与 `bbox_weights`。

---

## 【关键机制与数据】

- **Focal Loss 构造默认超参数** (原文):`use_sigmoid=True, gamma=2.0, alpha=0.25, reduction='mean', loss_weight=1.0`,且 class 实现中明确写为「`__init__(self, use_sigmoid=True, gamma=2.0, alpha=0.25, reduction='mean', loss_weight=1.0)`」。
- **Reduction 默认值** (原文):Focal Loss 默认 reduction 为 `mean`,文中给出改为 `sum` 的 config 写法。
- **多任务学习中 loss_weight 的作用** (原文):`loss_weight` 是一个 **scalar**,用于在多任务学习 (如分类 loss 与回归 loss) 之间控制各损失的权重。
- **两类权重张量** (原文):`label_weights` 用于分类 loss,`bbox_weights` 用于 bbox 回归 loss;它们由对应 head 的 `get_targets` 方法产生。
- **RPN RandomSampler 数值参数** (原文):`num=256`(每张图采样 256 个 anchor),`pos_fraction=0.5`(正样本占比 50%)。
- **覆写接口** (原文):`ATSSHead.get_targets(self, anchor_list, valid_flag_list, gt_bboxes_list, img_metas, gt_bboxes_ignore_list=None, gt_labels_list=None, label_channels=1, unmap_outputs=True)`。

---

## 【表格解读】

**原文无表格**。文中所有配置信息均以 Python 代码块形式给出,未提供任何参数表/性能对比表/配置项表格。

---

## 【公式解读】

**原文无显式公式** (无 LaTeX 或伪代码形式的公式)。文档未给出损失函数的数学表达式,仅以代码与文字描述 Focal Loss 的超参数 (`gamma`、`alpha`)、reduction 方式 (`mean`/`sum`) 和 `loss_weight` 标量的语义。

---

## 【关联】

- **上游/调用方**:RPN head 在使用 `CrossEntropyLoss` 时需要 sampler,体现了「损失核函数 ↔ 采样策略」的耦合关系。
- **同模块其他损失**:Focal Loss、GHMC、QualityFocalLoss 同属「自带正负样本平衡」的损失族,可替代需外置 sampler 的方案。
- **Head 层耦合**:Weighting (element-wise) 逻辑由 head 的 `get_targets` 方法产出 `label_weights`/`bbox_weights`;`ATSSHead` 通过继承 `AnchorHead` 并**覆写 `get_targets`** 来产出与 AnchorHead 不同的权重张量,体现了「Head 子类化 → 权重差异 → 损失差异」的扩展点。
- **MMDetection 组件依赖**:本文档引用了 `mmdet/models/losses/focal_loss.py`、`mmdet/models/dense_heads/atss_head.py`、`mmdet/models/dense_heads/anchor_head.py` 等具体源文件,说明自定义损失最终落到 models 子模块的 losses 与 dense_heads 两个目录中。
- **本教程在教程系列中的位置**:作为 Tutorial 6,聚焦于「损失函数」这一训练环节的可定制点,与模型结构、数据增强、推理等教程形成上下游配合 (但文末未给出内部链接,文档本身也未标注与其他 Tutorial 的交叉引用)。

---

## 【使用方法】

**1. Tweaking 损失超参数 (步骤 ②)**——修改 Focal Loss 的 `gamma` 为 1.5,`alpha` 为 0.5:
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=1.5,
    alpha=0.5,
    loss_weight=1.0)
```

**2. Tweaking reduction 方式 (步骤 ④)**——Focal Loss 由 `mean` 改为 `sum`:
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=1.0,
    reduction='sum')
```

**3. Tweaking loss_weight 标量 (步骤 ⑤)**——分类 loss 权重改为 0.5:
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=0.5)
```

**4. 设置采样策略 (步骤 ①)**——RPN head + CrossEntropyLoss 时在 `train_cfg` 中配置 `RandomSampler`:
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

**5. Weighting 损失 (步骤 ③,element-wise)**——通过**自定义 head 并覆写 `get_targets` 方法**(以 `ATSSHead` 继承 `AnchorHead` 为模板)产出与默认不同的 `label_weights` 与 `bbox_weights`;具体实现可参考 `mmdet/models/dense_heads/atss_head.py` 中 `get_targets` 的签名。

**6. 选用内置平衡损失替代采样器**——若使用 Focal Loss、GHMC、QualityFocalLoss 等已内置正负平衡机制的损失函数,则无需再配置 sampler。
