# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/customize_losses.md

# 一体化深度解读:Tutorial 6 - Customize Losses

---

## 【定位】

这篇文档解决 **如何在 MMDetection(以及继承其设计思想的 GFocalV2)框架中按需定制损失函数** 的问题,系统描述了损失从「预测/目标张量 → 标量 loss」的完整计算流水线,并以 Focal Loss (FL) 为示例,给出通过配置文件(config)对损失进行 **微调(tweaking)** 与 **加权(weighting)** 的标准方法。

---

## 【技术要点】

1. **损失计算四步流水线**(原文核心抽象):
   - Step 1:由 loss kernel 函数得到 **element-wise 或 sample-wise** 的损失;
   - Step 2:用与损失张量 **同形状** 的 weight 张量做 **element-wise** 加权;
   - Step 3:将损失张量 **reduce 为 scalar**;
   - Step 4:用一个 **scalar** 再对损失做整体加权。

2. **Tweaking(微调)覆盖 Step 1/3/4**,绝大多数情况下 **无需改代码**,只需修改 config。以 FocalLoss 为例,config 与构造器字段一一对应:
   - 构造器签名:`use_sigmoid=True, gamma=2.0, alpha=0.25, reduction='mean', loss_weight=1.0`。
   - 对应 config 块 `loss_cls=dict(type='FocalLoss', use_sigmoid=True, gamma=2.0, alpha=0.25, loss_weight=1.0)`。

3. **三类微调操作及示例配置**:
   - 改 Step 1 超参:`gamma=2.0→1.5`,`alpha=0.25→0.5`(原文标题写 "gamma and beta",但随后只演示 `gamma` 与 `alpha`,与 FL 实际公式一致)。
   - 改 Step 3 reduction:由 `'mean'` 改为 `'sum'`,通过 `reduction='sum'` 实现。
   - 改 Step 4 loss weight:将分类损失整体权重 `loss_weight` 由 `1.0` 改为 `0.5`,用于多任务学习(classification 与 regression 之间)的平衡。

4. **Weighting(加权)专指 Step 2 的 element-wise 方式**:用一个与损失张量形状相同的 weight 张量 **逐元素相乘**,从而对不同位置的损失做差异化缩放。

5. **两类最常见的 element-wise 权重**:
   - `label_weights`:用于 **分类损失**;
   - `bbox_weights`:用于 **bbox 回归损失**;
   - 二者都在对应 head 的 `get_targets` 方法中产生。

6. **典型代码示例 ATSSHead**:继承自 `AnchorHead`,并 **覆写(overwrite)** 了 `get_targets` 方法,正是通过该覆写产生与 AnchorHead 不同的 `label_weights` 与 `bbox_weights`。其 `get_targets` 签名为:
   ```
   get_targets(self, anchor_list, valid_flag_list, gt_bboxes_list,
               img_metas, gt_bboxes_ignore_list=None,
               gt_labels_list=None, label_channels=1, unmap_outputs=True)
   ```

---

## 【关键机制与数据】

- **工作原理(数据流)**:
  输入 `prediction` 与 `target` → Step 1 由 `FocalLoss` 核函数得到逐元素损失 → Step 2 与 `label_weights`/`bbox_weights` 逐元素相乘 → Step 3 通过 `reduction`(`'mean'` / `'sum'`)聚合为 scalar → Step 4 乘以 scalar 形式的 `loss_weight` → 最终 loss。
- **关键参数默认值(原文):** `use_sigmoid=True`, `gamma=2.0`, `alpha=0.25`, `reduction='mean'`, `loss_weight=1.0`。
- **修改后的示例参数(原文):** `gamma=1.5, alpha=0.5`(超参微调);`reduction='sum'`(reduction 微调);`loss_weight=0.5`(标量权重重调)。
- **性能/基准数据**:原文未提供任何 benchmark 数字或训练指标,本文不臆造。

---

## 【表格解读】

**原文无表格**。原文中所有配置示例均以 Python config 代码块形式给出,而非表格。

---

## 【公式解读】

**原文无公式**。文档仅以「`gamma` 与 `alpha`(原文标题误写为 `beta`)是 Focal Loss 的两个超参」这种叙述方式间接提到 Focal Loss 的超参,**未写出 Focal Loss 的具体数学表达式**,因此本文不补写公式。

---

## 【关联】

- **FocalLoss 实现**:`mmdet/models/losses/focal_loss.py`(以 `@LOSSES.register_module()` 注册)。
- **ATSSHead**:`mmdet/models/dense_heads/atss_head.py`(第 L530 行附近,继承 `AnchorHead` 并覆写 `get_targets`)——是 element-wise 加权(`label_weights`/`bbox_weights`)的产生源头示例。
- **AnchorHead**:`mmdet/models/dense_heads/anchor_head.py`(`ATSSHead` 的父类,提供默认的 `get_targets`)。
- **上下游关系**:
  - 上游(被本教程引用):`FocalLoss` loss 类本身、`AnchorHead.get_targets` 默认实现。
  - 下游(本教程所影响):模型训练的 head 配置(分类/回归分支的 `loss_cls` / `loss_bbox` 字典)以及多任务学习中各 loss 间的相对比重。
- **在教程体系中的位置**:这是 Tutorial 6,属于 MMDetection(以及 GFocalV2 自带的 docs/tutorials 目录)中关于「自定义训练组件」系列教程的一环,前序教程通常涉及数据集、模型、数据增强等可定制对象。
- **本教程的两个主要修改维度**:Tweaking(改 Step 1/3/4,通过 config 直接覆盖)与 Weighting(改 Step 2,需深入 head 的 `get_targets` 才能定制)。

---

## 【使用方法】

- **启用方式**:无需额外命令,所有修改都在 **配置文件(config)** 的 `loss_cls=dict(...)` / `loss_bbox=dict(...)` 等字典中完成。
- **可配置项**(以 FocalLoss 为例,均与构造器字段一一对应):
  - `type='FocalLoss'`:选择 loss 类;
  - `use_sigmoid=True`:是否对预测做 sigmoid;
  - `gamma`:Step 1 超参,默认 `2.0`;
  - `alpha`:Step 1 超参,默认 `0.25`;
  - `reduction`:Step 3 聚合方式,默认 `'mean'`,可改为 `'sum'`;
  - `loss_weight`:Step 4 标量权重,默认 `1.0`,多任务中用于平衡分类与回归。
- **修改步骤(原文示例)**:
  1. 复制默认 config 块到自定义 config;
  2. 调整 `gamma`/`alpha` 调 Step 1;
  3. 设置 `reduction='sum'` 调 Step 3;
  4. 修改 `loss_weight` 调 Step 4;
  5. 如需 Step 2 的 element-wise 加权,则需修改对应 head(例如 `ATSSHead`)中 `get_targets` 的 `label_weights` / `bbox_weights` 生成逻辑——**这一步原文未给出可直接复制的 config 示例,需直接修改代码**。
- **原文未涉及**:命令行调用方式、具体训练启动命令、批量调参脚本、超参搜索流程等。
