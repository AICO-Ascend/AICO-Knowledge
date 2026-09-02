# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_losses.md

# 深度解读:PyTorch/contrib/cv/detection/SSD/docs/tutorials/customize_losses.md

## 【定位】
本文档解决"在 MMDetection 框架下如何定制化损失函数"的问题——默认损失配置未必适配所有数据集或模型,文档给出**从损失计算管线解析到逐步骤修改**的完整指导,并区分"调整(tweaking)"与"加权(weighting)"两类操作。

> 注:文档虽归位于 SSD 路径下,但内容指向 **MMDetection 框架核心**,所引用代码全部位于 `mmdet/models/` 下的通用模块(`focal_loss.py`、`atss_head.py`、`anchor_head.py`),而非 SSD 私有实现。

---

## 【技术要点】

1. **四步损失计算管线**(原文明确给出):
   - Step 1:通过损失核函数得到 **element-wise / sample-wise** 损失;
   - Step 2:用与损失张量同形的 **weight tensor** 做 element-wise 加权;
   - Step 3:将损失张量 **reduce 为 scalar**;
   - Step 4:用 **scalar**(loss_weight)再做一次加权。

2. **Focal Loss 默认构造参数**(原文一一对应呈现):
   - `use_sigmoid=True`
   - `gamma=2.0`
   - `alpha=0.25`
   - `reduction='mean'`
   - `loss_weight=1.0`

3. **Tweaking 步骤 1——超参**:通过 config 修改 `gamma`(如 2.0 → 1.5)和 `alpha`(如 0.25 → 0.5)。

4. **Tweaking 步骤 3——reduction 方式**:通过 config 把 `reduction` 从 `'mean'` 改为 `'sum'`。

5. **Tweaking 步骤 4——loss_weight**:以 scalar 控制多任务学习中分类/回归损失的相对权重(如分类损失 `loss_weight=0.5`)。

6. **Weighting 步骤 2——element-wise 加权**:两种典型权重——`label_weights`(分类损失)与 `bbox_weights`(bbox 回归损失),由对应 head 的 `get_target`/`get_targets` 方法产生;**ATSSHead** 继承 **AnchorHead** 并**覆盖** `get_targets` 方法以产出不同的 `label_weights`/`bbox_weights`。

---

## 【关键机制与数据】

**工作原理(原文):**

- 整体映射:给定预测(prediction)、目标(target)与权重(weights),损失函数将输入张量映射到最终的 **loss scalar**。
- 步骤 1 的输出是**逐元素 / 逐样本**的张量;步骤 2 引入与该张量同形的 weight tensor 做**逐元素相乘**,从而实现"不同 loss entry 不同缩放";步骤 3 通过 `reduction` 把张量压成 scalar;步骤 4 再用 scalar `loss_weight` 做整体缩放,以协调多任务损失。
- **Tweaking vs Weighting 的边界**:文档把"调整(tweaking)"限定为步骤 1、3、4,**可通过 config 直接配置**;把"加权(weighting)"限定为步骤 2,**需修改 head 的 target 生成逻辑**。
- **loss_weight 的角色**(原文):"a scalar which controls the weight of different losses in multi-task learning, e.g. classification loss and regression loss."

**数据/参数(原文明确给出的数字):**

- 默认 FL 超参:`gamma=2.0`、`alpha=0.25`、`use_sigmoid=True`、`reduction='mean'`、`loss_weight=1.0`。
- Tweaking 超参示例:`gamma=1.5`、`alpha=0.5`(在 config 中替换原值)。
- Tweaking reduction 示例:在 config 中追加 `reduction='sum'`。
- Tweaking loss_weight 示例:`loss_weight=0.5`(用于分类损失,示例字段名为 `loss_cls`)。
- ATSSHead `get_targets` 方法签名(原文逐字给出):`anchor_list, valid_flag_list, gt_bboxes_list, img_metas, gt_bboxes_ignore_list=None, gt_labels_list=None, label_channels=1, unmap_outputs=True`。

**性能数据**:原文未提供任何性能/精度/速度数据。

---

## 【表格解读】

**原文无表格。** 原文以 Python 代码片段(逐字段对应)代替表格来展示类构造参数与 config 字段的一一对应关系,但并未以表格形式呈现。

---

## 【公式解读】

**原文无公式。** 全文未出现任何 LaTeX 或伪代码形式的数学公式,数值/超参仅以 Python 参数与 config 字段形式给出。

---

## 【关联】

文档与以下模块/特性存在直接引用关系(均为文末链接或代码引用):

- **Focal Loss 实现**:`mmdet/models/losses/focal_loss.py`(FL 作为 Step 1/3/4 调整的范例)。
- **Loss 注册机制**:`@LOSSES.register_module()` 装饰器(`FocalLoss` 类的构造处出现,说明所有损失类需经此装饰器注册方可被 config 通过 `type='FocalLoss'` 引用)。
- **ATSSHead**:`mmdet/models/dense_heads/atss_head.py`(原文注明 `get_targets` 方法位于第 530 行附近),作为 Step 2 element-wise 加权如何产出 `label_weights`/`bbox_weights` 的范例。
- **AnchorHead**:`mmdet/models/dense_heads/anchor_head.py`,ATSSHead 的父类,被 ATSSHead **继承**并**覆盖** `get_targets` 以产出**不同于**父类的权重。
- **Config 字段约定**:`loss_cls` 用于配置分类损失,与 `loss_bbox`(原文未直接出现但隐含)分别承担分类/回归两类任务损失的入口。
- **其他教程**:"Tutorial 6" 暗示存在前序教程(如 Tutorial 1–5),原文未给出具体链接或目录,但表明该篇是 MMDetection 教程系列的第 6 篇。

---

## 【使用方法】

**启用方式 / 配置项 / 命令**(原文已给出):

- **直接通过 config 修改即可启用所有 tweaking**,无需改动代码。以 Focal Loss 为例,config 字段 `loss_cls` 一一对应类构造参数:

  ```python
  # Step 1: 改超参
  loss_cls=dict(type='FocalLoss', use_sigmoid=True,
                gamma=1.5, alpha=0.5, loss_weight=1.0)

  # Step 3: 改 reduction 方式
  loss_cls=dict(type='FocalLoss', use_sigmoid=True,
                gamma=2.0, alpha=0.25, loss_weight=1.0,
                reduction='sum')

  # Step 4: 改 loss_weight
  loss_cls=dict(type='FocalLoss', use_sigmoid=True,
                gamma=2.0, alpha=0.25, loss_weight=0.5)
  ```

- **Step 2 element-wise 加权**:原文未给出可直接复制的 config 模板,仅说明需在对应 head 的 `get_target`/`get_targets` 方法中调整 `label_weights`(分类)与 `bbox_weights`(bbox 回归),并以 **ATSSHead 覆盖 AnchorHead 的 `get_targets`** 为例。
- **运行时命令**:原文未涉及任何 CLI/训练启动命令。
- **新增自定义损失类**:需继承 `nn.Module`,用 `@LOSSES.register_module()` 注册,并在 config 中通过 `type='YourLoss'` 引用(原文以 FL 的类定义为示意)。
