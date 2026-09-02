# 教程 6: 自定义损失函数

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/customize_losses.md

# 一体化深度解读：MMDetection 自定义损失函数教程

## 【定位】
这篇文档是 MMDetection「教程 6：自定义损失函数」的官方指南，解决的核心问题是：**当 MMDetection 默认损失函数配置无法适配特定数据或模型时，如何系统地理解并修改损失函数的每一个计算环节**。它将一次损失计算解构为可独立调控的 5 个步骤，使用户能够通过配置文件而不是修改源码的方式完成"微调"和"加权"两类常见的损失定制需求。

## 【技术要点】
1. **损失计算的 5 步流程**：原文将"预测 + 目标 + 权重"到"标量损失"的映射拆解为 ①采样→②核函数得到元素/样本损失→③逐元素加权→④归约为标量→⑤任务级损失权重。
2. **采样策略仅在需要时配置**：以 RPN head 中 `CrossEntropyLoss` 为例，需在 `train_cfg.rpn.sampler` 中配置 `RandomSampler`，关键参数为 `num=256`、`pos_fraction=0.5`、`neg_pos_ub=-1`、`add_gt_as_proposals=False`；而 Focal Loss / GHMC / QualityFocalLoss 因内置正负平衡机制，无需额外采样。
3. **微调损失聚焦步骤 ②④⑤**：超参数（如 `gamma=1.5, alpha=0.5`）、归约方式（`reduction='sum'`）、任务级权重（`loss_weight=0.5`）均可**通过配置文件覆盖**，无需触碰 `FocalLoss` 类的 `__init__`。
4. **加权损失对应步骤 ③**：通过与损失张量同形状的权重张量实现逐元素加权，主要以分类头的 `label_weights` 和回归的 `bbox_weights` 为载体。
5. **`get_targets` 是权重生成的核心**：以 `ATSSHead` 为例，其继承 `AnchorHead` 并**重写 `get_targets`** 方法来产出与上下文相关的 `label_weights` / `bbox_weights`，这正是"权重与上下文相关"的实现入口。
6. **代码—配置一一对应原则**：原文以 `FocalLoss` 的 `@LOSSES.register_module()` 类与同名 `loss_cls=dict(...)` 配置块并列展示，明确每个字段（`use_sigmoid`、`gamma`、`alpha`、`reduction`、`loss_weight`）的位置意义。

## 【关键机制与数据】

**工作原理（原文中可提取的）**：
- 原文将整条计算链描述为"输入张量 → 五步映射 → 标量损失"，每一步独立可改，使得修改粒度可细到单步。
- 步骤 ①采用负采样来缓解类别失衡（以 RPN 中 `RandomSampler` 的 256 候选、50% 正样本比例为典型数值）。
- 步骤 ②核函数既可输出"元素级"损失也可输出"样本级"损失，决定了后续加权与归约的粒度。
- 步骤 ③的逐元素加权通过"与损失同形的权重张量"实现，使每个 anchor、每个类别可被差异化赋权。
- 步骤 ④使用 `reduction` 参数（默认 `mean`）将张量归约为标量，原文演示了从 `mean` 切到 `sum` 的配置方法。
- 步骤 ⑤以 `loss_weight` 标量进行多任务平衡，原文示例将分类损失由 1.0 调为 0.5。

**性能数据**：原文未提供任何性能、精度或速度数值，仅给出方法论与配置示例。

**关键参数一览（原文出现）**：
| 字段 | 默认值 | 原文示例修改值 |
|---|---|---|
| `gamma` | 2.0 | 1.5 |
| `alpha` | 0.25 | 0.5 |
| `reduction` | `'mean'` | `'sum'` |
| `loss_weight` | 1.0 | 0.5 |
| `sampler.num` | 256 | （未改）|
| `sampler.pos_fraction` | 0.5 | （未改）|

## 【表格解读】
**原文无表格**。原文中仅以代码块与配置字典形式罗列参数，未以 markdown/HTML 表格形式呈现，因此本节不做逐字表格还原。

## 【公式解读】
**原文无公式**。文档全程以自然语言 + Python 代码块描述损失计算流程与配置方法，未出现任何 LaTeX 数学表达式或伪代码形式的公式，因此本节不做符号解读。

## 【关联】
- **上下游模块关联**：原文在多个位置将本教程与具体代码锚点绑定：
  - **Focal Loss 实现**：`mmdet/models/losses/focal_loss.py`（作为"微调"主案例的源代码）。
  - **ATSSHead 的 `get_targets` 重写位置**：`mmdet/models/dense_heads/atss_head.py`，其继承自 `AnchorHead`（`mmdet/models/dense_heads/anchor_head.py`）。
- **与其他教程的可能关系**：原文开篇"教程 6"暗示其属于 MMDetection 系列教程的一部分，与"配置系统"、"自定义模型"、"自定义数据"等教程共享同一套"配置文件驱动修改"的方法论，但原文档本身未给出交叉链接。
- **与其他损失族的关联**：原文明确 Focal Loss / GHMC / QualityFocalLoss 与 RPN `CrossEntropyLoss` 在"是否需要采样"这一维度上互斥，为后续选择损失函数提供决策依据。
- **内部链接**：原文未提供内部链接（无），文末标注"(无)"与原文一致。

## 【使用方法】

**启用方式（原文给出的）**：
- **采样器配置（RPN 场景）**：在 `train_cfg` 中通过以下字典启用采样——
  ```
  train_cfg=dict(
      rpn=dict(
          sampler=dict(
              type='RandomSampler',
              num=256,
              pos_fraction=0.5,
              neg_pos_ub=-1,
              add_gt_as_proposals=False)))
  ```
- **微调 Focal Loss 超参数**（步骤 ②）：在 `loss_cls` 中将 `gamma` 改为 1.5、`alpha` 改为 0.5。
- **微调归纳方式**（步骤 ④）：在 `loss_cls` 中将 `reduction` 从默认 `'mean'` 改为 `'sum'`。
- **微调任务级损失权重**（步骤 ⑤）：在 `loss_cls` 中将 `loss_weight` 从 1.0 改为 0.5。
- **加权损失（步骤 ③）的使用入口**：通过自定义或继承 Head（如 `ATSSHead` 继承自 `AnchorHead`）并**重写 `get_targets` 方法**，在签名层面需提供 `anchor_list`、`valid_flag_list`、`gt_bboxes_list`、`img_metas`、`gt_bboxes_ignore_list=None`、`gt_labels_list=None`、`label_channels=1`、`unmap_outputs=True` 等参数以产出新的 `label_weights` / `bbox_weights`。

**原文未涉及**：命令行启用方式、配置文件全局开关、不同模型/数据集下的具体推荐值、性能收益数据。
