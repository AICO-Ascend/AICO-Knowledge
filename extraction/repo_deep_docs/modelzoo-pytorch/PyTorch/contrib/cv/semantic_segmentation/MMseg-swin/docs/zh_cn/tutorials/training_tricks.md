# 教程 5: 训练技巧

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/training_tricks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/zh_cn/tutorials/training_tricks.md

# 一体化深度解读：MMseg-swin 训练技巧教程

## 【定位】
本教程系统性地介绍了 MMSegmentation 在语义分割训练阶段可启用的五类"训练技巧"（学习率分层、难样本挖掘、类别平衡损失、多损失加权、忽略指定类别），用于在标准配置无法满足需求时，通过修改配置文件中的特定字段来提升模型收敛速度、缓解类别不均衡或适配特定数据集的损失计算逻辑。

---

## 【技术要点】

1. **解码头与主干网络分层学习率**：通过 `optimizer.paramwise_cfg.custom_keys` 中的 `'head'` 字典将解码头参数的学习率乘以 `lr_mult=10.`，使得解码头学习率是主干网络的 10 倍；分组依据为参数名中包含 `'head'` 关键字的所有参数。
2. **在线难样本挖掘（OHEM）**：在 `decode_head` 中设置 `sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)`，仅保留置信度低于 0.7 的像素进行训练，并保证每次至少保留 100000 个像素；若 `thresh` 未指定，则按 `min_kept` 取损失最大的像素。
3. **类别平衡损失（Class Balanced Loss）**：在 `CrossEntropyLoss` 中传入 `class_weight` 列表，该列表作为 `weight` 参数参与损失计算，原文给出了 Cityscapes 数据集的 19 个类别权重示例。
4. **多损失加权融合**：将 `loss_decode` 设置为列表形式，每项含 `type`、`loss_name`、`loss_weight` 三个键，可同时启用 `CrossEntropyLoss` 与 `DiceLoss` 并按比例求和；原文示例采用 `1:3` 的 CE:Dice 权重比，且 `decode_head` 与 `auxiliary_head` 共享同一组损失配置。
5. **忽略指定 label 类别**：通过 `ignore_index` 标记需忽略的 label 值（如 Cityscapes 中的 label=0 背景），并配合 `loss_decode` 中的 `avg_non_ignore=True` 使损失均值仅在非忽略像素上计算；`avg_non_ignore` 默认 `False`。
6. **损失命名前缀约定**：`loss_name` 必须以 `loss_` 为前缀，否则不会被纳入反向传播图，导致该损失无法对参数更新产生贡献。

---

## 【关键机制与数据】

**工作原理总览**：

- **学习率分层机制**：MMCV 的 `DefaultOptimizerConstructor` 在构造 optimizer 时，会扫描所有可训练参数的名称，将名称匹配 `'head'` 子串的参数归入 `'head'` 组，对该组应用 `lr_mult=10.` 的乘子；其余参数（主要是主干 backbone）保持基础学习率不变。该机制本质上让优化器在每一步对解码头施加比主干大 10 倍的步长，从而更快地适配分割任务的解码头随机初始化权重。
- **OHEM 采样机制**：在 `decode_head` 前向计算后会得到每个像素的预测 logits 与对应的 loss 分布；`OHEMPixelSampler` 依据预测概率（即置信度）筛选像素。`thresh=0.7` 表示置信度低于 0.7 的像素被视为"难样本"被保留参与训练；若满足 `min_kept=100000` 的下界保证，则避免在极端情况下因难样本过少导致训练不稳定。该采样器实现在 `mmseg/core/seg/sampler` 中（原文链接指向该路径）。
- **类别平衡损失机制**：将 `CrossEntropyLoss` 的 `weight` 参数设为各类别权重向量后，损失函数对每个像素的负对数概率乘以其真实类别对应的权重再做平均；当某类样本稀少时，增大其权重可缓解模型对该类的欠拟合。原文给出的 19 个权重对应 Cityscapes 的 19 个训练类（验证集共 19 类，标签 0 通常为 ignore 类别）。
- **多损失求和机制**：在配置文件中将 `loss_decode` 改为列表后，`decode_head` 和 `auxiliary_head` 会分别把所有子损失按 `loss_weight` 加权求和得到总损失；`loss_name` 以 `loss_` 开头既是日志显示键，也是反向传播图节点注册名（保证梯度流通）。
- **忽略类别机制**：在像素级 loss 计算时，先将 `ignore_index` 对应的像素 loss 置零（不贡献梯度），若 `avg_non_ignore=False` 则分母为所有像素总数，若 `avg_non_ignore=True` 则分母仅统计非忽略像素，使损失值更聚焦于"真正需要学习"的部分。相关实现见原文给出的 PR #1409。

**原文数据**：
- Cityscapes 类别权重（19 个浮点数，按顺序）：`[0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754, 1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037, 1.0865, 1.0955, 1.0865, 1.1529, 1.0507]`
- OHEM 阈值 `thresh=0.7`，最小保留像素数 `min_kept=100000`
- 学习率倍数 `lr_mult=10.`
- CE:Dice 损失权重比 `1:3`（即 `loss_weight=1.0` 与 `loss_weight=3.0`）
- Cityscapes 中被忽略的 `ignore_index=0`

**性能数据**：原文未提供任何性能对比或实验指标，仅给出配置示例。

---

## 【表格解读】

**原文无表格**。原文档全程以 Python 配置代码块的形式呈现参数与示例，未出现 markdown 表格或结构化对照表。

---

## 【公式解读】

**原文无公式**。原文档未使用 LaTeX 或伪代码形式给出任何公式，仅以配置项的方式间接表达了损失加权（如 `loss_weight=1.0` 与 `loss_weight=3.0` 的比例对应多损失加权和中的权重系数）。如需将原文语义形式化为公式，CE+Dice 多损失加权可写作：

$$
\mathcal{L}_{\text{total}} \;=\; w_{\text{ce}}\cdot \mathcal{L}_{\text{CE}} \;+\; w_{\text{dice}}\cdot \mathcal{L}_{\text{Dice}}
$$

其中 $w_{\text{ce}}=1.0$、$w_{\text{dice}}=3.0$，但请注意 **此式并非原文出现**，仅为对原文配置项的语义还原，不应视为原文内容。

---

## 【关联】

- **与 MMCV 的关系**：学习率分层机制依赖 `mmcv.runner.DefaultOptimizerConstructor` 的 `paramwise_cfg.custom_keys` 接口，原文明确指向 [MMCV 文档](https://mmcv.readthedocs.io/en/latest/api.html#mmcv.runner.DefaultOptimizerConstructor) 作为深入参考。
- **与 PyTorch 的关系**：类别平衡损失最终调用 `torch.nn.CrossEntropyLoss` 的 `weight` 参数，原文链接至 [PyTorch CrossEntropyLoss 文档](https://pytorch.org/docs/stable/nn.html?highlight=crossentropy#torch.nn.CrossEntropyLoss)。
- **与 MMSegmentation 内部模块的关系**：OHEM 采样器由 `mmseg/core/seg/sampler` 模块提供，挂在 `decode_head.sampler` 字段上使用。
- **与上游配置文件的关系**：每一节技巧示例均通过 `_base_` 继承自一个完整的训练配置（如 `pspnet_r50-d8_512x1024_40k_cityscapes.py`、`fcn_unet_s5-d16_64x64_40k_drive.py`、`fcn_unet_s5-d16_4x4_512x1024_160k_cityscapes.py`），说明这些技巧是叠加在标准训练配置之上的增量修改，而非独立训练流程。
- **与特定数据集的关系**：类别平衡示例与忽略类别示例都基于 Cityscapes，多损失加权示例基于 DRIVE 医疗影像数据集，说明这些技巧常用于类别分布不均或标签语义特殊的场景。
- **与上游 PR 的关系**：忽略 label 类别的特性由 PR #1409 引入（原文给出链接）。

---

## 【使用方法】

启用方式统一为：新建（或修改）一个继承自 `_base_` 的配置文件，将对应字段写入模型配置块即可，无需修改训练脚本。

**① 分层学习率**——在 `optimizer` 字典中添加：
```python
optimizer=dict(
    paramwise_cfg = dict(
        custom_keys={
            'head': dict(lr_mult=10.)}))
```

**② OHEM**——在 `decode_head` 中加入 `sampler`：
```python
model=dict(
    decode_head=dict(
        sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)))
```

**③ 类别平衡损失**——在 `decode_head.loss_decode` 中指定 `type='CrossEntropyLoss'` 并填写 `class_weight`：
```python
model=dict(
    decode_head=dict(
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0,
            class_weight=[0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754,
                        1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037,
                        1.0865, 1.0955, 1.0865, 1.1529, 1.0507])))
```

**④ 多损失加权**——将 `loss_decode` 改为列表，每个元素含 `type`、`loss_name`、`loss_weight`，并同步配置 `auxiliary_head`：
```python
model = dict(
    decode_head=dict(loss_decode=[
        dict(type='CrossEntropyLoss', loss_name='loss_ce', loss_weight=1.0),
        dict(type='DiceLoss', loss_name='loss_dice', loss_weight=3.0)]),
    auxiliary_head=dict(loss_decode=[
        dict(type='CrossEntropyLoss', loss_name='loss_ce', loss_weight=1.0),
        dict(type='DiceLoss', loss_name='loss_dice', loss_weight=3.0)]),
)
```
注意：`loss_name` 必须以 `loss_` 为前缀。

**⑤ 忽略指定 label**——在 `decode_head` 与 `auxiliary_head` 上同时设置 `ignore_index`，并在 `loss_decode` 中设置 `avg_non_ignore=True`：
```python
model = dict(
    decode_head=dict(
        ignore_index=0,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0, avg_non_ignore=True)),
    auxiliary_head=dict(
        ignore_index=0,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0, avg_non_ignore=True)),
)
```
