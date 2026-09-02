# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SSD/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SSD/docs/tutorials/finetune.md

# 一体化深度解读: Tutorial 7 — Finetuning Models

---

## 【定位】

本教程解决 **"如何将 COCO 预训练的目标检测模型迁移到新数据集(如 Cityscapes、KITTI)以获得更好性能"** 的问题,给出了在 MMDetection V2.0 配置体系下,通过继承+覆写的 config 改写方式,将预训练 Mask R-CNN 微调至 Cityscapes 等新数据集的标准流程。

---

## 【技术要点】

1. **两步微调流程**: ① 按 [Tutorial 2: Customize Datasets](customize_dataset.md) 为新数据集添加支持;② 按本教程修改 config(共五个部分)。

2. **配置继承机制 (`_base_`)**: 新 config 通过 `_base_` 列表从 `_base_/models/mask_rcnn_r50_fpn.py`(模型结构)、`_base_/datasets/cityscapes_instance.py`(数据集)、`_base_/default_runtime.py`(运行时设置)三个已有 config 继承,减少重复编写并降低出错概率;也可选择不继承、直接全量编写。

3. **改 head(只改 `num_classes`即可迁移预训练权重)**: 仅修改 `roi_head` 内的 `bbox_head.num_classes` 与 `mask_head.num_classes`,预训练权重除最终预测头外其余部分可继续复用。

4. **改训练 schedule**: 微调需用更小的学习率和更少的 epoch;示例给出 lr=0.01、step=[7]、total_epochs=8(因 batch_size=8,实际 epoch = 8×8 = 64)、warmup_iters=500、warmup_ratio=0.001 的 step 策略。

5. **载入预训练权重**: 在 config 中通过 `load_from` 指定预训练 checkpoint 的下载 URL,建议训练前先下载以避免训练中下载耗时。

6. **支持的数据集范围**: 原文明示 MMDetection V2.0 已支持 VOC、WIDER FACE、COCO、Cityscapes 四类数据集。

---

## 【关键机制与数据】

### 工作原理 / 数据流

- **继承机制**: `_base_` 列表式多重继承 — 新 config 仅需声明差异部分,基类 config 负责提供完整骨架(模型、数据集、运行设置),机制类似 Python 类继承。
- **Head 替换原理**: 预训练权重 = 特征提取 backbone + FPN + 大部分 head 参数;由于最终分类层输出维度由类别数决定(COCO=80 → Cityscapes=8),仅 `num_classes` 维度变化会导致 shape 不匹配,故只重新初始化最终预测层,其余权重可直接载入。
- **训练 schedule 调整**: 因微调时模型已在 COCO 上充分收敛,故使用更小 lr(0.01)+ 短 step(7 epoch)+ linear warmup(500 iters),避免破坏已学特征。
- **预训练模型加载**: `load_from` 字段载入 `mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth`(Mask R-CNN R50-FPN,2x schedule 训练产物)。

### 性能数据
- 原文未给出具体 mAP/AP 等数值结果。
- 原文仅给出一句关于训练 schedule 的注释: `# [7] yields higher performance than [6]` — 即 step=[7] 比 step=[6] 性能更好(具体提升幅度未给出)。

---

## 【表格解读】

**原文无表格。** 本教程全部配置以 Python 代码块形式呈现,未包含 markdown 表格。

---

## 【公式解读】

**原文无公式。** 文档不含任何 LaTeX 数学公式或伪代码公式;性能表达仅以代码中的列表(如 `step=[7]`、`total_epochs = 8  # actual epoch = 8 * 8 = 64`)和注释形式出现,其中隐含的乘法关系为:

```
actual_epoch = total_epochs × batch_size
              = 8 × 8
              = 64
```

含义: 配置中 `total_epochs=8` 是按 batch_size=8 折算的 epoch 数,实际训练样本遍历次数为 64 epoch。

---

## 【关联】

- **上游 / 前置教程**:
  - [Tutorial 2: Customize Datasets](customize_dataset.md): 微调流程的**第 1 步**就是先按本教程为新数据集添加支持;不先做数据集定制,本教程的"Modify dataset"步骤就无从谈起。
  - [Model Zoo](../model_zoo.md): 本教程明确说明 `load_from` 所引用的预训练权重来自 Model Zoo,该文档是预训练 checkpoint 的来源索引。

- **同 config 体系的引用关系**:
  - `_base_/models/mask_rcnn_r50_fpn.py` — 提供 Mask R-CNN R50-FPN 的完整结构定义。
  - `_base_/datasets/cityscapes_instance.py` — 提供 Cityscapes 实例分割数据集的加载/预处理配置。
  - `_base_/default_runtime.py` — 提供日志、检查点、分布式等通用运行时设置。

- **下游影响**: 经本教程微调得到的模型,可在目标数据集(原文示例为 Cityscapes)上得到优于"从头训练"的收敛速度与最终性能(原文未给出具体数值证据)。

---

## 【使用方法】

### 启用方式(以 Cityscapes + Mask R-CNN R50-FPN 为例)

**Step 1 — 继承基础 config**:

```python
_base_ = [
    '../_base_/models/mask_rcnn_r50_fpn.py',
    '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
]
```

**Step 2 — 修改 head(类别数改为 Cityscapes 的 8 类)**:

```python
model = dict(
    pretrained=None,
    roi_head=dict(
        bbox_head=dict(
            type='Shared2FCBBoxHead',
            in_channels=256,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=8,
            bbox_coder=dict(
                type='DeltaXYWHBBoxCoder',
                target_means=[0., 0., 0., 0.],
                target_stds=[0.1, 0.1, 0.2, 0.2]),
            reg_class_agnostic=False,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
            loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
        mask_head=dict(
            type='FCNMaskHead',
            num_convs=4,
            in_channels=256,
            conv_out_channels=256,
            num_classes=8,
            loss_mask=dict(
                type='CrossEntropyLoss', use_mask=True, loss_weight=1.0))))
```

**Step 3 — 修改数据集配置**: 依据 [Tutorial 2: Customize Datasets](customize_dataset.md) 为新数据集编写 config;MMDetection V2.0 内置支持 VOC / WIDER FACE / COCO / Cityscapes。

**Step 4 — 修改训练 schedule**:

```python
# optimizer
# lr is set for a batch size of 8
optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    # [7] yields higher performance than [6]
    step=[7])
total_epochs = 8  # actual epoch = 8 * 8 = 64
log_config = dict(interval=100)
```

**Step 5 — 指定预训练权重来源(建议训练前手动下载)**:

```python
load_from = 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/mmdetection/models/mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth'  # noqa
```

### 配置项速查表(原文出现的关键参数)

| 参数 / 字段 | 原文中取值 | 作用 |
|---|---|---|
| `_base_` 列表 | 3 个 base config | 多重继承,避免重写 |
| `bbox_head.num_classes` | 8 | Cityscapes 类别数 |
| `bbox_head.in_channels` | 256 | 与 FPN 输出对齐 |
| `bbox_head.fc_out_channels` | 1024 | Shared2FC 头部 FC 维度 |
| `bbox_head.roi_feat_size` | 7 | RoI Pooling 输出空间尺寸 |
| `bbox_coder.target_means` | `[0., 0., 0., 0.]` | Δxywh 编码均值 |
| `bbox_coder.target_stds` | `[0.1, 0.1, 0.2, 0.2]` | Δxywh 编码方差(wh 权重 2 倍) |
| `reg_class_agnostic` | `False` | 每类独立回归 |
| `loss_cls.use_sigmoid` | `False` | 使用 Softmax+CE |
| `loss_bbox.beta` | `1.0` | Smooth L1 阈值 |
| `mask_head.num_convs` | 4 | FCNMaskHead 卷积层数 |
| `mask_head.conv_out_channels` | 256 | mask 预测 conv 输出通道 |
| `optimizer.lr` | 0.01(bs=8) | 微调学习率 |
| `optimizer.momentum` | 0.9 | SGD 动量 |
| `optimizer.weight_decay` | 0.0001 | 权重衰减 |
| `lr_config.warmup_iters` | 500 | linear warmup 迭代数 |
| `lr_config.warmup_ratio` | 0.001 | 起始 lr/基础 lr 比例 |
| `lr_config.step` | `[7]` | step 策略里程碑 |
| `total_epochs` | 8(实际 64) | bs=8 折算 epoch |
| `log_config.interval` | 100 | 日志打印间隔 |
| `load_from` | `mask_rcnn_r50_fpn_2x_20181010-...pth` | COCO 预训练权重 URL |

> 注: 上述速查表为**对原文中代码块的字段整理**,所有数值与命令均直接摘自原文,未做外推。
