# Tutorial 6: Customize Losses

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_losses.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_losses.md

# 一体化深度解读:MMDetection 教程 6 —— 自定义损失(Customize Losses)

## 【定位】

本文档是 MMDetection 系列教程的第 6 篇,系统阐述如何在使用 MMDetection 时根据不同数据集或模型的需求**修改损失函数(loss function)**:既涵盖损失从原始预测/目标到最终标量(scalar)的四步计算流水线,也把可定制维度归纳为两大类——**微调(Tweaking)**与**加权(Weighting)**——从而让用户在不重写训练框架的前提下,通过 config 或少量代码即可适配自定义场景。

## 【技术要点】

1. **损失计算的"四步流水线"**(原文):
   - Step 1:由损失核函数(loss kernel)得到 element-wise 或 sample-wise 的损失张量;
   - Step 2:用**形状相同**的 weight tensor 对损失张量做 element-wise 加权;
   - Step 3:将损失张量 reduce(reduction)成一个 scalar;
   - Step 4:用一个 scalar(loss_weight)再对最终损失做一次加权。

2. **两类自定义维度**:
   - **Tweaking(微调)**:覆盖步骤 1、3、4,绝大多数情况下可在 config 中直接指定;
   - **Weighting(加权)**:针对步骤 2,属于 element-wise 维度,通常需要修改 head 的 `get_targets` 方法。

3. **以 Focal Loss(FL)为示例的可调参数**(原文构造签名):
   ```python
   FocalLoss(use_sigmoid=True, gamma=2.0, alpha=0.25,
             reduction='mean', loss_weight=1.0)
   ```
   关键默认值:`use_sigmoid=True`,`gamma=2.0`,`alpha=0.25`,`reduction='mean'`,`loss_weight=1.0`。

4. **Tweaking 的三种具体操作**(原文):
   - 改 step 1 的超参:例 `gamma=1.5`、`alpha=0.5`;
   - 改 step 3 的 reduction 方式:例从 `'mean'` 改为 `'sum'`;
   - 改 step 4 的 loss_weight:例把分类损失权重设为 `0.5`(与回归损失等多任务间加权)。

5. **Weighting 的两种张量**(原文):
   - `label_weights`:用于分类损失;
   - `bbox_weights`:用于 bbox 回归损失;
   - 二者均可在对应 head 的 `get_target` 方法里找到。

6. **代码层面的扩展点**(原文):
   - ATSSHead 继承自 AnchorHead,但**重写了 `get_targets`** 方法,从而产出不同的 `label_weights` 与 `bbox_weights`;
   - 构造签名:`get_targets(self, anchor_list, valid_flag_list, gt_bboxes_list, img_metas, gt_bboxes_ignore_list=None, gt_labels_list=None, label_channels=1, unmap_outputs=True)`。

## 【关键机制与数据】

- **工作原理(原文)**:"Given the input prediction and target, as well as the weights, a loss function maps the input tensor to the final loss scalar."——损失函数是把预测/目标/权重映射为最终标量的过程,被分解为四步。
- **Tweaking 与 Weighting 的区分**(原文):Tweaking 是 scalar 维度的、与模型/数据集**最相关**的微调,绝大多数可在 config 完成;Weighting 则是 element-wise 维度,需要用与损失张量同形的 weight tensor **逐元素相乘**,从而让损失的不同条目被差异化缩放。
- **上下文相关性**(原文):"The loss weight varies across different models and highly context related"——loss_weight 的具体取值高度依赖模型与任务上下文(例如分类损失 vs 回归损失之间的多任务平衡)。
- **性能/基准数据**:原文未给出任何性能数字、收敛曲线或对比指标;文中所有出现的具体数值(`gamma=2.0/1.5`、`alpha=0.25/0.5`、`loss_weight=1.0/0.5`)均为示例超参,而非性能数据。

## 【表格解读】

原文无表格。

(原文全部以代码块 + 文字说明呈现,未出现任何 markdown 表格或参数对照表。)

## 【公式解读】

原文无公式。

(原文未给出任何 LaTeX 数学公式或伪代码公式;所涉及的"四步流水线"仅以文字 + 编号列表形式描述,且没有写出 $L = ...$ 形式的显式表达式。)

## 【关联】

原文提及的关键模块/类及其上下游关系(以下信息均来自原文引用或文中代码片段,**未自行扩展**):

- **Focal Loss(FL)**:作为 Tweaking 的示例损失,被 `@LOSSES.register_module()` 注册为可被 config 通过 `type='FocalLoss'` 选用的 loss;
- **ATSSHead ↔ AnchorHead**:ATSSHead 继承 AnchorHead,但**重写 `get_targets` 方法**,以产出与父类不同的 `label_weights` 与 `bbox_weights`,正是 Weighting 步骤的代表性实现路径;
- **config 与 loss_cls 字典**:Tweaking 维度的所有示例均通过修改 `loss_cls=dict(...)` 字典完成,表明 config 中的 loss 配置与损失类的构造签名一一对应("they are actually one to one correspondence");
- **多任务学习平衡**:Step 4 的 `loss_weight` 显式用于在分类损失与回归损失之间进行加权,这是损失层与下游 head / 多任务优化器的关联点。

内部链接信息:原文提供的均为 GitHub 指向(mmdetection 仓库内 focal_loss.py、atss_head.py、anchor_head.py),**文档未给出内部 anchor 链接**,本节按原文所述的引用关系归纳。

## 【使用方法】

下列启用方式/配置项均直接取自原文示例,未自行补充:

1. **在 config 中修改 Focal Loss 超参(Step 1)**——原文示例:
   ```python
   loss_cls=dict(
       type='FocalLoss',
       use_sigmoid=True,
       gamma=1.5,
       alpha=0.5,
       loss_weight=1.0)
   ```

2. **在 config 中修改 reduction 方式(Step 3)**——原文示例:
   ```python
   loss_cls=dict(
       type='FocalLoss',
       use_sigmoid=True,
       gamma=2.0,
       alpha=0.25,
       loss_weight=1.0,
       reduction='sum')
   ```

3. **在 config 中修改 loss_weight(Step 4)**——原文示例(将分类损失权重设为 0.5):
   ```python
   loss_cls=dict(
       type='FocalLoss',
       use_sigmoid=True,
       gamma=2.0,
       alpha=0.25,
       loss_weight=0.5)
   ```

4. **修改 element-wise 加权(Step 2)**:在对应 head(以 ATSSHead 为例)的 `get_targets` 方法中产出自定义的 `label_weights` 与 `bbox_weights`;原文给出的方法签名为:
   ```python
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
   原文未给出该方法的具体修改片段或运行命令(例如 CLI/脚本启动方式)——此部分内容**原文未涉及**。
