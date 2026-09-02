# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FCOS/docs/tutorials/customize_losses.md

# 一体化深度解读:MMDetection 损失函数定制指南

## 【定位】

这篇文档解决 MMDetection 框架中**损失函数 (Loss) 定制化**的问题——在默认配置无法适配新数据集或新模型时,如何在不修改源代码的前提下,通过 config 调整或代码层面的权重分配,实现损失函数计算流程中各步骤的个性化定制,文档将定制分为"微调 (Tweaking)"和"加权 (Weighting)"两大类。

---

## 【技术要点】

1. **损失计算的 4 步流水线**:给定输入预测、目标以及权重,损失函数将输入 tensor 映射为最终的 loss 标量,流水线分为 ① 元素级/样本级损失核函数计算 → ② 与权重 tensor **逐元素**相乘 → ③ 归约为**标量** → ④ 用**标量**加权。
2. **微调 (Tweaking) 对应步骤 1/3/4**:通过 config 即可完成,绝大多数修改无需改动源码,以 Focal Loss (FL) 为示例对象。
3. **核心可调超参数**:`use_sigmoid=True`、`gamma=2.0`、`alpha=0.25`、`reduction='mean'`、`loss_weight=1.0`;文档示例中演示了 `gamma` 从 2.0→1.5,`alpha` 从 0.25→0.5,`reduction` 从 `mean`→`sum`,`loss_weight` 从 1.0→0.5 的修改方法。
4. **加权 (Weighting) 对应步骤 2**:通过与 loss tensor 同形状的 weight tensor 做**逐元素乘法**,实现 loss 各条目的差异化缩放。
5. **两种典型逐元素权重**:`label_weights`(用于分类 loss)与 `bbox_weights`(用于 bbox 回归 loss),二者在不同模型 head 的 `get_target`/`get_targets` 方法中产生。
6. **Head 模块的权重来源**:以 `ATSSHead` 为例,它继承 `AnchorHead` 并重写 `get_targets` 方法,从而产出与其他 AnchorHead 不同的 `label_weights` 和 `bbox_weights`。

---

## 【关键机制与数据】

**工作原理(原文阐述)**:

- **Step 1 (Element-wise or sample-wise loss)**:由 loss 核函数给出,例如 Focal Loss 的 `__init__` 接受 `use_sigmoid`、`gamma`、`alpha`、`reduction`、`loss_weight` 五个参数(原文中 `__init__` 签名逐字列出)。
- **Step 2 (Element-wise weighting)**:将 loss tensor 与等形状权重 tensor 相乘,使不同位置/样本的 loss 被差异化缩放。
- **Step 3 (Reduction)**:把 loss tensor 归约为标量,默认方式 `mean`,也可改为 `sum` 等。
- **Step 4 (Scalar weighting)**:用一个**标量**对整个 loss 加权,以平衡多任务学习(如分类 loss 与回归 loss)的相对贡献。

**配置与代码的对应关系(原文)**:

文档明确指出"Focal Loss 的构造方法代码片段与 config **一一对应**",即 `loss_cls=dict(type='FocalLoss', use_sigmoid=True, gamma=2.0, alpha=0.25, loss_weight=1.0)` 中的每个键都直接对应 `FocalLoss.__init__` 的同名参数。

**权重生成位置(原文)**:

`label_weights` 和 `bbox_weights` 可以在对应 head 的 `get_target`/`get_targets` 方法中找到;`ATSSHead.get_targets` 的方法签名(原文逐字列出)包含 9 个参数:`anchor_list, valid_flag_list, gt_bboxes_list, img_metas, gt_bboxes_ignore_list=None, gt_labels_list=None, label_channels=1, unmap_outputs=True`。

**性能数据**:原文未涉及(无 benchmark、无 mAP、无速度数字)。

---

## 【表格解读】

**原文无表格**。

文档中所有信息均以 Python 代码块和散文叙述呈现,未出现任何 markdown 表格形式的参数表、性能对比表或配置项表。可调参数以 `__init__` 函数签名和 config dict 两种形式并列展示。

---

## 【公式解读】

**原文无公式**。

文档未以 LaTeX 或伪代码形式显式写出 Focal Loss 的数学表达式,仅以代码签名 (`gamma`, `alpha`, `use_sigmoid`) 和概念描述("element-wise loss by the loss kernel function")呈现,没有出现如 $-\alpha_t (1-p_t)^\gamma \log(p_t)$ 这类符号化公式。

---

## 【关联】

文档涉及以下模块/类/方法,它们之间构成上下游关系:

- **`mmdet/models/losses/focal_loss.py` 中的 `FocalLoss` 类**:作为"Tweaking"小节的示例损失,定义了 `__init__` 的 5 个可调参数(`use_sigmoid`, `gamma`, `alpha`, `reduction`, `loss_weight`)。
- **`@LOSSES.register_module()` 装饰器**:将 `FocalLoss` 注册到 MMDetection 的损失注册表中,使 config 中可通过 `type='FocalLoss'` 字符串调用。
- **`mmdet/models/dense_heads/anchor_head.py` 中的 `AnchorHead`**:作为父类,定义原始的 `get_targets` 方法。
- **`mmdet/models/dense_heads/atss_head.py` 中的 `ATSSHead`**:`AnchorHead` 的子类,重写 `get_targets`,从而产出**特定**于 ATSS 的 `label_weights` 与 `bbox_weights`,这是"Weighting loss (step 2)"小节的范例。
- **配置 dict `loss_cls`**:作为 config 文件中分类损失的统一入口,既承载步骤 1/3/4 的 tweak,又间接反映步骤 2 的逐元素权重策略(由 head 的 `get_targets` 决定)。
- **多任务学习中的回归损失 `loss_bbox`**:文档在"Tweaking loss weight (step 4)"小节中以"classification loss 和 regression loss"举例,说明 `loss_weight` 用于在二者间做平衡,但未给出 `loss_bbox` 的具体配置示例。

**内部链接**:文末注明 "(无)"——文档本身未提供站内锚链接,但通过裸 GitHub URL 引用了 `focal_loss.py`、`atss_head.py`、`anchor_head.py` 三个文件,以及 ATSSHead `get_targets` 方法的行号锚点 (`#L530`)。

---

## 【使用方法】

以下所有配置均通过修改 config 文件中的 `loss_cls` dict 完成,**无需改动源码**:

**1. 修改 Focal Loss 超参数(对应步骤 1)**
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=1.5,    # 原默认 2.0,此处改为 1.5
    alpha=0.5,    # 原默认 0.25,此处改为 0.5
    loss_weight=1.0)
```

**2. 修改归约方式(对应步骤 3)**
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=1.0,
    reduction='sum')   # 原默认 'mean',此处改为 'sum'
```

**3. 修改标量损失权重(对应步骤 4)**
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=0.5)   # 原默认 1.0,此处改为 0.5
```

**4. 修改逐元素权重(对应步骤 2)**:原文未给出可直接抄录的 config 范例,而是指向 head 内部 `get_targets` 方法中的 `label_weights` 与 `bbox_weights` 生成处,即要修改此类权重需进入 head 的代码层(而非单纯改 config)。原文表述为"You can find them in the `get_target` method of the corresponding head",并以 `ATSSHead.get_targets` 的方法签名作为定位指引。

**5. 启用命令**:原文未涉及任何命令行调用方式(如 `--loss_cls` 覆盖、训练脚本启动方式等),所有修改均通过 config 文件静态指定。

---

### 附:文档内部一处表述需注意

原文 Tweaking hyper-parameters 小节首句写为"`gamma` and `beta` are two hyper-parameters in the Focal Loss",但 `FocalLoss.__init__` 实际签名为 `gamma` 与 **`alpha`**(而非 `beta`),且后续示例代码使用的也是 `alpha=0.5`。此处"beta"应为原文笔误,实际可调参数是 `alpha`,本文解读按代码真实签名还原。
