# 教程 5: 训练技巧

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/training_tricks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/training_tricks.md

# 一体化深度解读:教程 5 — 训练技巧

## 【定位】

这篇文档是 MMSegmentation(此处挂载于 `DeeplabV3_for_Pytorch` 仓库)的训练技巧教程,系统介绍三种提升语义分割训练效果/收敛速度的常用策略:**主干/解码头差异化学习率、在线难样本挖掘 (OHEM)、类别平衡损失**,并给出可直接复制粘贴的配置片段。

---

## 【技术要点】

1. **解码头学习率倍增** — 通过 `optimizer.paramwise_cfg.custom_keys` 将分组键 `'head'` 的参数 `lr_mult` 设为 `10.`,实现主干网络与解码头组件使用不同学习率(解码头为骨干的 10 倍),无需改动其他字段。
2. **OHEM 像素采样** — 在 `decode_head` 中设置 `sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)`,只保留置信度低于 0.7 的难样本像素,且每张图至少保留 100 000 个像素点;未指定 `thresh` 时退化为按损失取前 `min_kept` 个像素。
3. **类别平衡损失权重** — 将 `loss_decode.type='CrossEntropyLoss'` 并设置 `class_weight=[…]`,作为 `weight` 参数注入 `CrossEntropyLoss`,对 cityscapes 这类长尾/类别不均衡数据集按类加权。
4. **继承式配置写法** — 三个例子均通过 `_base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'` 继承 PSPNet R50-D8 512×1024 40k 迭代的 cityscapes 配置,只覆写(override)目标字段,保持其余训练 pipeline 不变。
5. **依赖说明** — OHEM 依赖 `mmseg/core/seg/sampler` 的像素采样器;`paramwise_cfg` 的完整字段需参考 MMCV 的 `DefaultOptimizerConstructor`;`class_weight` 注入方式遵循 PyTorch `torch.nn.CrossEntropyLoss`。

---

## 【关键机制与数据】

- **工作原理(原文:主干与解码头差异化 LR)**:`custom_keys={'head': dict(lr_mult=10.)}` 会让任何被分组到 `'head'` key 的参数的学习率在基础学习率上乘以 10。原文明确指出此机制"在语义分割里,一些方法会让解码头组件的学习率大于主干网络的学习率,这样可以获得更好的表现或更快的收敛"。
- **工作原理(原文:OHEM)**:`sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)`,其中 `thresh=0.7` 表示"置信分数在 0.7 以下的像素值点会被拿来训练";`min_kept=100000` 表示"训练时我们至少要保留 100000 个像素值点";若 `thresh` 未指定,则退化为"前 `min_kept` 个损失的像素值点才会被选择"。
- **工作原理(原文:类别平衡)**:`class_weight=[0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754, 1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037, 1.0865, 1.0955, 1.0865, 1.1529, 1.0507]`(共 19 个权重,匹配 cityscapes 19 类),作为 `weight` 参数传入 `CrossEntropyLoss`,原注释说明"DeepLab 对 cityscapes 使用这种权重"。
- **数据流/数据规模(原文):OHEM 训练中至少保留 `100000` 个像素点(原文: "至少要保留100000个像素值点");类别权重数组长度=19,对应 cityscapes 19 个语义类别。
- **性能数据**:原文未提供任何性能数字(如 mIoU 提升、收敛 epoch 减少等),本节不臆造。

---

## 【表格解读】

**原文无表格。** 文中仅以代码片段、列表项和注释形式给出配置,没有 markdown/html 表格。但原文第三段(类别平衡损失)中包含一个长度 19 的 `class_weight` 数组,可视为"cityscapes 19 类权重表",此处**逐字还原**以便参考(原文数据):

| 类别索引 (按 cityscapes 顺序) | class_weight (原文) |
|---|---|
| 1 | 0.8373 |
| 2 | 0.9180 |
| 3 | 0.8660 |
| 4 | 1.0345 |
| 5 | 1.0166 |
| 6 | 0.9969 |
| 7 | 0.9754 |
| 8 | 1.0489 |
| 9 | 0.8786 |
| 10 | 1.0023 |
| 11 | 0.9539 |
| 12 | 0.9843 |
| 13 | 1.1116 |
| 14 | 0.9037 |
| 15 | 1.0865 |
| 16 | 1.0955 |
| 17 | 1.0865 |
| 18 | 1.1529 |
| 19 | 1.0507 |

逐行解读:该表 19 个权重分布在约 `[0.84, 1.15]` 区间(原文数据),数值围绕 1.0 浮动,体现"按类别频次反比加权"的思路——原文中注释为 "DeepLab 对 cityscapes 使用这种权重",由 DeepLab 系列论文给出;最大权重 1.1529 出现在第 18 类,最小权重 0.8373 出现在第 1 类,说明训练样本越少的类别被赋予越高损失权重,从而抑制类别不平衡。该表是配置片段中的字面值,**并非可由训练过程自动学习**。

---

## 【公式解读】

**原文无公式。** 文中未出现 LaTeX、伪代码或符号化公式,只通过代码配置(`lr_mult`、`thresh`、`min_kept`、`class_weight`)隐含了参数关系:
- 实际 LR = 基础 LR × `lr_mult`(对 `'head'` key);
- 参与训练的像素子集 = `{像素 | 置信度 < thresh}`,且大小 ≥ `min_kept`;
- `CrossEntropyLoss` 内部将各样本损失乘以对应类别的 `class_weight[i]` 再求均值(PyTorch 原生语义)。

---

## 【关联】

- **上游依赖(原文链接)**:
  - MMCV 的优化器构造器 `mmcv.runner.DefaultOptimizerConstructor` — 用于解释 `paramwise_cfg.custom_keys.lr_mult` 的完整字段语义(原文:"参照 MMCV 文档获取更详细的信息")。
  - `mmseg/core/seg/sampler` — 像素采样器实现位置,OHEM 的 `OHEMPixelSampler` 在此注册(原文:"对于训练时采样,我们在 那里 做了像素采样器")。
  - PyTorch `torch.nn.CrossEntropyLoss` — `class_weight` 通过 `weight` 参数传入(原文链接到 PyTorch 官方文档)。
- **下游/配套示例(原文)**:
  - 三段示例均基于 `pspnet_r50-d8_512x1024_40k_cityscapes.py` 继承扩展,说明这些技巧可与 PSPNet(DeeplabV3 同属语义分割全卷积网络族)训练流程叠加使用;其中第三例注释 "DeepLab 对 cityscapes 使用这种权重" 明确点出该权重源自 DeepLab 系列工作,与本仓库 `DeeplabV3_for_Pytorch` 主题一致。
- **内部链接**:原文无仓库内部链接;文末给出的 `(无)` 与正文一致。

---

## 【使用方法】

三种技巧均通过**配置字典覆写**启用,无需改训练入口代码:

1. **差异化学习率** — 在配置 `optimizer` 字段内追加:
   ```python
   optimizer=dict(
       paramwise_cfg=dict(
           custom_keys={'head': dict(lr_mult=10.)}))
   ```
2. **OHEM 像素采样** — 在 `model.decode_head` 中追加 `sampler`:
   ```python
   model=dict(
       decode_head=dict(
           sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)))
   ```
   - 调整 `thresh`(0~1,值越大越"只挑难的");调整 `min_kept` 控制每张图最少保留像素数;不传 `thresh` 则按损失 top-`min_kept` 选取。
3. **类别平衡损失** — 替换 `model.decode_head.loss_decode`:
   ```python
   model=dict(
       decode_head=dict(
           loss_decode=dict(
               type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0,
               class_weight=[0.8373, 0.9180, 0.8660, 1.0345, 1.0166,
                             0.9969, 0.9754, 1.0489, 0.8786, 1.0023,
                             0.9539, 0.9843, 1.1116, 0.9037, 1.0865,
                             1.0955, 1.0865, 1.1529, 1.0507])))
   ```
   - `use_sigmoid=False` 与多类交叉熵语义一致(原文给出该值);`loss_weight=1.0` 控制该损失在总损失中的缩放;`class_weight` 长度需与数据集类别数一致(此处 19 = cityscapes)。
4. **组合使用**:三段示例均以 `_base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'` 起手,可按需将 `optimizer`、`model.decode_head.sampler`、`model.decode_head.loss_decode` 在同一配置中合并覆写。命令/CLI 启动方式原文未涉及,需结合仓库的训练入口脚本使用。
