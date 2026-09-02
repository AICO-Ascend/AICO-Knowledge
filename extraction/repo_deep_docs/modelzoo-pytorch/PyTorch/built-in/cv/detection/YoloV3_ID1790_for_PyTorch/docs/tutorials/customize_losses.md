# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/tutorials/customize_losses.md

# 一体化深度解读:YoloV3_ID1790_for_PyTorch 中 Customize Losses 教程

---

## 【定位】

本文档系统说明 MMDetection 框架中如何**自定义损失函数**,围绕"tweaking(微调)"与"weighting(加权)"两大修改类别,串联起从"loss kernel 计算 → 逐元素加权 → 归约 → 标量加权"的四步计算流水线,并以 Focal Loss 与 ATSSHead 为例给出可直接落地的 config 与代码修改方式。

---

## 【技术要点】

1. **损失计算的通用四步流水线**(原文定义):
   ① 通过 loss kernel 函数得到 **element-wise 或 sample-wise** 的 loss;
   ② 用与 loss 同形状的 **weight tensor 逐元素加权**;
   ③ 将 loss tensor **归约(reduction)为 scalar**;
   ④ 用 **scalar 再做一次加权**。

2. **修改类别二分法**:tweaking 主要涉及 step 1、3、4,绝大多数可在 **config 中指定**;weighting 对应 step 2,需在 head 的 `get_targets` 方法内调整 `label_weights` / `bbox_weights`。

3. **Focal Loss 构造器签名与默认值**(原文逐字给出):
   - `use_sigmoid=True`
   - `gamma=2.0`
   - `alpha=0.25`
   - `reduction='mean'`
   - `loss_weight=1.0`

4. **Tweaking 三种典型操作**(均以 `loss_cls=dict(...)` 形式给出):
   - 调超参: `gamma=1.5, alpha=0.5`;
   - 改 reduction: `'mean'` → `'sum'`;
   - 改 loss weight(标量加权): `loss_weight=1.0` → `loss_weight=0.5`。

5. **Weighting 的两类对象**:`label_weights`(分类损失)与 `bbox_weights`(bbox 回归损失),其来源为对应 head 的 `get_targets` 方法。

6. **ATSSHead 与 AnchorHead 的继承关系**:ATSSHead 继承自 AnchorHead,**重写(overwrite)了 `get_targets` 方法**,从而产生不同的 `label_weights` 与 `bbox_weights`,这正是 weighting 行为差异的源头。

---

## 【关键机制与数据】

- **工作原理**:loss 函数把"输入 prediction、target、weights"映射为最终的标量 loss,该映射被显式拆分为四步,使得每一步都可以独立定制。
- **Tweaking 机制**:通过修改 config 中 `loss_cls` 字典的字段,可一对一对应地控制 FL 的核函数超参(`gamma/alpha`)、归约方式(`reduction`)与标量权重(`loss_weight`),文档强调"config 与构造器参数一一对应"。
- **Weighting 机制**:在 step 2 中,以与 loss tensor 同形状的 weight tensor 逐元素相乘,**使 loss 中不同条目获得不同的缩放**,这种行为由 head 在 `get_targets` 阶段生成权重张量来决定。
- **多任务学习场景下的标量加权**(step 4):`loss_weight` 控制不同损失(如 cls loss 与 reg loss)的相对重要度,文档给出的示例是从 `1.0` 改到 `0.5`。
- **上下文相关性**(原文明确表述):"The loss weight varies across different models and highly context related",即具体数值需视模型与任务而定。
- **性能数据**:原文未涉及任何性能/精度数字。

---

## 【表格解读】

**原文无表格**。

(原文中所有结构化信息均以 config 代码块、构造器签名代码块、`get_targets` 方法签名代码块呈现,未出现 markdown 表格。)

---

## 【公式解读】

**原文无公式**。

(虽然本文档主题是损失函数,但原文并未显式列出 FL 的数学公式,也未给出任何 LaTeX/伪代码形式的公式;FL 的 `gamma`、`alpha`、`reduction`、`loss_weight` 均以代码参数形式给出。)

---

## 【关联】

- **与 ATSSHead 的关系**:本文档以 ATSSHead 为 weighting 的示例,**ATSSHead 继承自 AnchorHead**,并通过 **overwrite `get_targets` 方法**产出不同的 `label_weights` 与 `bbox_weights`,从而影响 step 2 的逐元素加权结果。
- **`get_targets` 方法的角色**:被明确指为 **两类 loss weights(`label_weights`、`bbox_weights`)的来源**,任何希望自定义 weighting 行为的修改都需聚焦在该方法上。
- **与 Config 系统的关系**:tweaking 全部通过修改 config 中的 `loss_cls=dict(...)` 完成,体现"config 与构造器一一对应"的设计约定。
- **与多任务学习的关系**:step 4 的 scalar 加权(`loss_weight`)用于**调节 cls loss 与 reg loss 等多任务项的相对权重**。
- **内部链接**:文末未给出内部链接清单(已确认 "(无)")。

---

## 【使用方法】

以下为**原文给出的、可直接复用**的启用/配置方式。

### 1. Tweaking 超参(FL step 1)

```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=1.5,
    alpha=0.5,
    loss_weight=1.0)
```

### 2. Tweaking 归约方式(FL step 3)

```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=1.0,
    reduction='sum')
```

### 3. Tweaking loss 标量权重(FL step 4,多任务相对权重)

```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=0.5)
```

### 4. Weighting(FL step 2)

原文**未给出可直接复用的 config 片段**,仅指出需要修改对应 head(如 ATSSHead)的 `get_targets` 方法以调整 `label_weights` 与 `bbox_weights`;其签名如下:

```
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

> 综上:tweaking 路径完全在 config 中完成;weighting 路径需要进入 head 源码修改 `get_targets`。其余命令行、CLI 开关、运行参数等**原文未涉及**。
