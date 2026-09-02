# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_losses.md

# 一体化深度解读：MMDetection 自定义损失函数教程

## 【定位】
本教程面向需要为新数据集或新模型**修改/定制检测损失函数**的用户，系统说明 MMDetection 损失的四步计算流水线，并以 Focal Loss 与 ATSSHead 为例，演示如何在不重写代码的前提下通过 config 完成超参、reduction 方式与标量权重的微调，以及如何理解与定位 element-wise 加权（label_weights / bbox_weights）的来源。

---

## 【技术要点】

1. **损失计算的标准化四步流水线**（原文逐字）
   1. Get **element-wise** or sample-wise loss by the loss kernel function.
   2. Weighting the loss with a weight tensor **element-wisely**.
   3. Reduce the loss tensor to a **scalar**.
   4. Weighting the loss with a **scalar**.

2. **两类定制范畴**（原文用语）：
   - **Tweaking loss** —— 涉及步骤 1、3、4，通常只需修改 config 即可，对应 step 1（核函数超参）、step 3（reduction）、step 4（标量 loss_weight）。
   - **Weighting loss** —— 涉及步骤 2，需要根据模型上下文构造与 loss tensor 同形的 weight tensor。

3. **Focal Loss 的标准超参默认取值**（原文）：
   - `use_sigmoid=True`、`gamma=2.0`、`alpha=0.25`、`reduction='mean'`、`loss_weight=1.0`

4. **Tweaking 的三类可调参示例**（原文逐字）：
   - step 1 调超参：`gamma=1.5, alpha=0.5`（原文）。
   - step 3 改 reduction：`reduction='sum'`（原文）。
   - step 4 改标量权重：`loss_weight=0.5`（原文，对分类损失）。

5. **Weighting 的两种来源**（原文逐字）：
   - 分类损失：`label_weights`
   - bbox 回归损失：`bbox_weights`
   - 二者由对应 head 的 `get_target(s)` 方法产生。

6. **代表模型与代码位置**（原文链接）：
   - `FocalLoss` 注册实现：`mmdet/models/losses/focal_loss.py`（以 `@LOSSES.register_module()` 装饰）。
   - 权重生成示例：`ATSSHead.get_targets`（`mmdet/models/dense_heads/atss_head.py`），继承并重写 `AnchorHead` 的同名方法。

---

## 【关键机制与数据】

**损失映射机制（原文）**：给定输入预测、target 以及 weights，损失函数将输入 tensor 映射到一个最终的 loss 标量，整体映射被划分为四步：
1. 由 **核函数**产生 element-wise 或 sample-wise loss。
2. 与形状相同的 weight tensor **逐元素**相乘（element-wise）。
3. 把 loss tensor **reduce 成标量**（reduction：默认 `mean`，也可设为 `sum`）。
4. 乘以一个**标量**作为最终权重（loss_weight）。

**Step 1 机制（原文）**：以 FL 为例，核函数由 `use_sigmoid`（默认 `True`）、`gamma=2.0`、`alpha=0.25` 共同决定。原文给出的修改方式：在 config 中改 `gamma=1.5, alpha=0.5` 即可生效，无需改源码。

**Step 3 机制（原文）**：reduction 控制"标量化"方式，默认 `mean`；通过在 config 中追加 `reduction='sum'` 即可切换为求和，原文明确该改动仅需一行配置。

**Step 4 机制（原文）**：标量 `loss_weight` 用于**多任务学习**中平衡不同损失（如 classification loss vs. regression loss），原文示例将 `loss_cls` 的 `loss_weight` 改为 `0.5`。

**Step 2 机制（原文）**：element-wise 加权通过与 loss tensor 同形的 weight tensor 逐元素相乘实现，使 loss 中不同 entry 可被差异化缩放。`label_weights` 与 `bbox_weights` 均在 head 的 `get_target` / `get_targets` 中产生，并因 head 而异（context related），原文以 `ATSSHead` 继承并重写 `AnchorHead.get_targets` 为例说明 `label_weights`、`bbox_weights` 的差异来源。

**性能数据**：原文**未给出任何数值/benchmark**。

---

## 【表格解读】

原文无表格。

（文档仅以代码片段的形式给出 Focal Loss 构造方法与对应 config 的"一一对应"关系，未提供任何参数表或性能对比表。）

---

## 【公式解读】

原文无公式。

（文中 FL 的 `gamma`、`alpha` 等仅以代码参数形式出现，并未写出 FL 的数学定义式；因此本节按要求标注"原文无公式"。）

---

## 【关联】

依据原文文末/正文中的内部链接信息，本教程与以下组件存在直接耦合关系：

- **`FocalLoss`**：`mmdet/models/losses/focal_loss.py`（以 `@LOSSES.register_module()` 注册的 `nn.Module`，是 step 1/3/4 改动的示例对象）。
- **`ATSSHead`**：`mmdet/models/dense_heads/atss_head.py`（line 530 起的 `get_targets` 方法）—— step 2 `label_weights` / `bbox_weights` 的示例来源。
- **`AnchorHead`**：`mmdet/models/dense_heads/anchor_head.py`（`ATSSHead` 的父类；其 `get_targets` 被 `ATSSHead` 重写，从而产出**与父类不同**的 `label_weights` 与 `bbox_weights`）。
- **模块注册机制**：所有 loss 通过 `@LOSSES.register_module()` 注册到 registry，因此 step 1/3/4 的修改只需在 config 中指定 `type='FocalLoss'` 等字符串即可切换/复用 loss 类。
- **多任务权重链路**：step 4 的 `loss_weight` 体现为顶层 config 中 `loss_cls` / `loss_bbox` 等条目，最终汇入 detector 的总 loss。

> 原文未提供额外的内部链接或版本引用信息，故以上仅基于正文给出的源码链接与 `AnchorHead` ↔ `ATSSHead` 继承关系进行关联梳理。

---

## 【使用方法】

**Step 1（核函数超参 tweaking）—— 原文示例**：
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=1.5,      # 原文：相较默认 2.0 改为 1.5
    alpha=0.5,      # 原文：相较默认 0.25 改为 0.5
    loss_weight=1.0)
```

**Step 3（reduction 方式 tweaking）—— 原文示例**：
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=1.0,
    reduction='sum')   # 原文：默认 'mean'，此处改为 'sum'
```

**Step 4（标量 loss_weight tweaking）—— 原文示例**：
```python
loss_cls=dict(
    type='FocalLoss',
    use_sigmoid=True,
    gamma=2.0,
    alpha=0.25,
    loss_weight=0.5)   # 原文：将分类损失标量权重改为 0.5
```

**Step 2（element-wise weighting）—— 原文指引**：
- 在目标 head 的 `get_target` / `get_targets` 方法中构造 `label_weights`（分类）与 `bbox_weights`（bbox 回归）。
- 原文指向 `ATSSHead.get_targets`（继承自 `AnchorHead`）作为查看/参考位置；未给出可直接在 config 中启用或覆盖的具体字段名或命令行开关。
- 因此 **step 2 的具体启用方式（如何为非 ATSS 模型新增/替换 weight tensor）原文未涉及**。

**注册与注册器**：通过 `@LOSSES.register_module()` 注册 loss 类，并在 config 中以 `type='...'` 指定即可使用——这一约定贯穿 step 1/3/4 的所有改动方式。
