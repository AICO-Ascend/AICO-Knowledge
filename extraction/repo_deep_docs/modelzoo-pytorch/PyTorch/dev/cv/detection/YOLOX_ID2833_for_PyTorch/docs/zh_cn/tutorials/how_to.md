# 教程 11: How to xxx

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/how_to.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/how_to.md

# 一体化深度解读:「教程 11: How to xxx」

---

## 【定位】

这篇文档是一个**"How to" 问答式教程合集**,集中回答用户在 MMDetection 风格训练框架中遇到的高频"如何做"类问题,具体覆盖四个主题:**跨库复用骨干网络 (MMClassification / TIMM)**、**使用马赛克 (Mosaic) 数据增强**、**通过自定义 hook 冻结/解冻骨干网络**、**获取新骨干网络各阶段通道数**。

> ⚠️ 说明:原文正文实际标题与命名 (`Tutorial 11: How to xxx`) 保留占位文字,但内容已围绕上述四个具体 FAQ 展开,而非关于 "xxx" 本身。

---

## 【技术要点】

### 要点 1:跨库骨干网络复用 — 基于统一的注册器继承链
- MMDet、MMCls、MMSeg 的模型注册表**都继承自 MMCV 的根注册表**,因而可在不重写网络的情况下互相调用对方已注册模块。
- 在配置中通过 `custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)` 触发 mmcls 的 `register_module`。
- 依赖版本约束(原文标注):**`mmcls>=0.20.0`**。
- 骨干替换的写法核心:
  - `backbone=dict(_delete_=True, type='mmcls.MobileNetV3', ...)` — 删除 `_base_` 中原 backbone 字段后整体替换。
  - 预训练权重需去掉 mmcls 中的 `prefix='backbone.'`,通过 `init_cfg=dict(type='Pretrained', checkpoint=pretrained, prefix='backbone.')` 实现正确加载。
- 通过 mmcls 使用 timm 的配置:骨干类型写作 `type='mmcls.TIMMBackbone'`,关键参数 `model_name='efficientnet_b1'`、`features_only=True`、`pretrained=True`。

### 要点 2:Mosaic 数据增强 — 必须配套 MultiImageMixDataset
- 原文明确:"如果你想在训练中使用 `Mosaic`,那么请确保你同时使用 `MultiImageMixDataset`。"
- Mosaic + RandomAffine 的搭配原因(原文):**"图像经过马赛克处理后会放大 4 倍,所以我们使用仿射变换来恢复图像的大小"**。
- 关键参数:
  - `Mosaic` 的 `img_scale=(1333, 800)`、`pad_val=114.0`。
  - `RandomAffine` 的 `scaling_ratio_range=(0.1, 2)`、`border=(-img_scale[0] // 2, -img_scale[1] // 2)`。
  - 数据集包装:`type='MultiImageMixDataset'`,内部 `dataset` 仅做 `LoadImageFromFile` + `LoadAnnotations(with_bbox=True)` 的最小载入,`pipeline` 才挂载 Mosaic 等增强。

### 要点 3:基于 hook 的骨干网络延迟解冻
- 通过配置 `model=dict(backbone=dict(frozen_stages=1))` 实现初始冻结。
- 通过 `custom_hooks = [dict(type="UnfreezeBackboneEpochBasedHook", unfreeze_epoch=1)]` 注册解冻触发器。
- 用户需自行实现 `UnfreezeBackboneEpochBasedHook` 类(原文给出的完整代码见下一节),在 `before_train_epoch` 中根据 `runner.epoch == self.unfreeze_epoch` 触发。
- 原文注明该方法**"Only valid for resnet"**,因为代码逻辑依赖 ResNet 的 `deep_stem` / `norm1` / `conv1` / `layer{i}` 等命名。

### 要点 4:用伪造输入探测骨干网络各阶段通道数
- 标准做法:`self.eval()` + `inputs = torch.rand(1, 3, 32, 32)` + `level_outputs = self.forward(inputs)`,逐阶段打印 `tuple(level_out.shape)`。
- 以 `ResNet(depth=18)` 为例(原文输出):

| 阶段 | 形状 (原文) |
|---|---|
| 第 1 阶段 | `(1, 64, 8, 8)` |
| 第 2 阶段 | `(1, 128, 4, 4)` |
| 第 3 阶段 | `(1, 256, 2, 2)` |
| 第 4 阶段 | `(1, 512, 1, 1)` |

---

## 【关键机制与数据】

### 工作流 A:跨库骨干替换 (以 RetinaNet + MobileNetV3-small 为例)

数据流为:**`_base_` 加载 → `custom_imports` 触发 mmcls 注册 → `_delete_=True` 清空旧 backbone 字段 → 写入新 backbone → 同步修改 neck 的 `in_channels` 与 `start_level`**。

原文给出的关键参数流(MobileNetV3-small):
- 骨干输出阶段索引:`out_indices=(3, 8, 11)`。
- Neck 适配输入:`neck=dict(in_channels=[24, 48, 96], start_level=0)` — 这三个通道数必须与 MobileNetV3-small 在 `out_indices=(3, 8, 11)` 处的输出通道对齐。
- 预训练权重 URL(原文):`https://download.openmmlab.com/mmclassification/v0/mobilenet_v3/convert/mobilenet_v3_small-8427ecf0.pth`。

### 工作流 B:跨库骨干替换 (以 RetinaNet + TIMM EfficientNet-B1 为例)

原文配置链接:`https://github.com/open-mmlab/mmdetection/blob/master/configs/timm_example/retinanet_timm_efficientnet_b1_fpn_1x_coco.py`。

关键参数:
- 骨干:`type='mmcls.TIMMBackbone'`、`model_name='efficientnet_b1'`、`features_only=True`、`pretrained=True`、`out_indices=(1, 2, 3, 4)`。
- Neck:`neck=dict(in_channels=[24, 40, 112, 320])` — 四个值必须与 EfficientNet-B1 在 `(1, 2, 3, 4)` 处的特征通道对齐。
- 优化器(原文给出):`type='SGD'`,`lr=0.01`,`momentum=0.9`,`weight_decay=0.0001`。

### 工作流 C:Mosaic 数据增强 (以 Faster R-CNN 为例)

数据流为:**`MultiImageMixDataset` 包裹 `CocoDataset` → 内层 dataset 只做载入 → 外层 pipeline 跑 Mosaic+RandomAffine+RandomFlip+Normalize+Pad+DefaultFormatBundle+Collect**。

具体 pipeline 顺序(原文,逐条):
1. `Mosaic(img_scale=(1333, 800), pad_val=114.0)`
2. `RandomAffine(scaling_ratio_range=(0.1, 2), border=(-img_scale[0] // 2, -img_scale[1] // 2))`
3. `RandomFlip(flip_ratio=0.5)`
4. `Normalize(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)`
5. `Pad(size_divisor=32)`
6. `DefaultFormatBundle`
7. `Collect(keys=['img', 'gt_bboxes', 'gt_labels'])`

数据集字段(原文):
- `data_root = 'data/coco/'`
- `ann_file = data_root + 'annotations/instances_train2017.json'`
- `img_prefix = data_root + 'train2017/'`
- `filter_empty_gt=False`
- `train_dataset._delete_ = True`(删除 `_base_` 中不必要的训练集设置)

### 工作流 D:延迟解冻 hook 的运行机制

触发链路:`runner.epoch == unfreeze_epoch` → 取出 `backbone` → 视 `frozen_stages >= 0` 解冻 stem → 循环 `for i in range(1, backbone.frozen_stages + 1)` 解冻 `layer{i}`。

原文 hook 类完整骨架(关键字段释义,逐字段保留):
- `@HOOKS.register_module()` 注册到 MMCV 钩子体系。
- `__init__(self, unfreeze_epoch=1)`:保存解冻 epoch。
- `before_train_epoch(self, runner)`:每个 epoch 开始前检查。
- `is_module_wrapper(model)`:处理分布式包装(`MMDistributedDataParallel`)。
- `backbone.deep_stem` 分支:解冻 `backbone.stem`;非 deep_stem 分支:解冻 `backbone.conv1` 与 `backbone.norm1`。
- 阶段层解冻:`m = getattr(backbone, f'layer{i}')`,对 `m.train()` 并置 `param.requires_grad = True`。

### 性能/运行数据(原文有)

- ResNet-18 在 `torch.rand(1, 3, 32, 32)` 输入下的四阶段输出形状(原文逐字):
  - `(1, 64, 8, 8)`、`(1, 128, 4, 4)`、`(1, 256, 2, 2)`、`(1, 512, 1, 1)`。
- 注:原文未给出任何精度/mAP/FPS 等训练性能数据。

---

## 【表格解读】

**原文无表格。**

> 说明:本文档以代码片段 + 散文说明为主,未出现 markdown/HTML 表格结构。所有"参数表/性能对比/配置项"均以 Python 配置字典或代码块形式给出,详见【技术要点】与【关键机制与数据】中按字段逐条列出。

---

## 【公式解读】

**原文无公式。**

> 说明:全文未出现任何 LaTeX 公式或伪代码形式数学表达式。文档涉及的所有"变换关系"均以配置参数(如 `scaling_ratio_range`、`border`、`out_indices`、`in_channels`)和代码逻辑(如 `requires_grad`、`frozen_stages` 计数)呈现。

---

## 【关联】

> 内部链接:原文提供 (无)。
> 外部链接(原文中显式提及):
> - MMCV 注册器/层级结构文档:`https://github.com/open-mmlab/mmcv/blob/master/docs/zh_cn/understand_mmcv/registry.md#...`
> - MMClassification 配置文档:`https://github.com/open-mmlab/mmclassification/blob/master/docs/zh_CN/tutorials/config.md`
> - TIMM EfficientNet-B1 完整配置示例:`https://github.com/open-mmlab/mmdetection/blob/master/configs/timm_example/retinanet_timm_efficientnet_b1_fpn_1x_coco.py`

### 模块/上下游关系图谱

| 本教程涉及模块 | 上游依赖 | 下游被用于 |
|---|---|---|
| 骨干网络 backbone | MMCV 注册器 (根) ← MMDet/Seg/Cls | 检测头、FPN/neck |
| mmcls.MobileNetV3 / mmcls.TIMMBackbone | MMClassification ≥0.20.0 → timm | RetinaNet backbone 字段 |
| Mosaic + MultiImageMixDataset | MMDetection 数据管线 | 任意检测器训练 |
| UnfreezeBackboneEpochBasedHook | MMCV `HOOKS` + `Hook.before_train_epoch` | ResNet-based 检测器 |
| 通道探测脚本 (torch.rand) | torch.no_grad 等价的 `eval()` 模式 | 新骨干的 neck `in_channels` 配置 |

### 隐含依赖关系
- **要点 1 与要点 4 联动**:要点 4 探测到的输出通道数,正是要点 1 中 `neck.in_channels` 必须填入的数值。
- **要点 2 与训练稳定性**:Mosaic 放大 4 倍 → 必须配合 `RandomAffine` 进行反向缩放,否则输入到检测头的 feature map 尺寸会偏离 anchor 设计范围。
- **要点 3 与训练策略**:`UnfreezeBackboneEpochBasedHook` 与 `schedule_1x.py`(12 epoch 周期)是常见搭配 —— `unfreeze_epoch=1` 意味着第 2 个 epoch 起骨干解冻,适合 warm-up 后全参数微调。

---

## 【使用方法】

### 1. 启用跨库骨干网络(配置层操作)

a) 使用 mmcls 骨干:
```python
custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)
model = dict(
    backbone=dict(
        _delete_=True,
        type='mmcls.MobileNetV3',
        arch='small',
        out_indices=(3, 8, 11),
        init_cfg=dict(type='Pretrained', checkpoint=pretrained, prefix='backbone.')),
    neck=dict(in_channels=[24, 48, 96], start_level=0))
```

b) 通过 mmcls 使用 timm 骨干:
```python
custom_imports = dict(imports=['mmcls.models'], allow_failed_imports=False)
model = dict(
    backbone=dict(
        _delete_=True,
        type='mmcls.TIMMBackbone',
        model_name='efficientnet_b1',
        features_only=True,
        pretrained=True,
        out_indices=(1, 2, 3, 4)),
    neck=dict(in_channels=[24, 40, 112, 320]))
```

启用前提(原文):安装 **`mmcls>=0.20.0`**。

### 2. 启用 Mosaic 数据增强

原文做法:在 `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` 基础上**增添字段**(非 `_base_` 修改),重写 `train_dataset` 与 `data = dict(train=train_dataset)`。最小载入管线(`LoadImageFromFile` + `LoadAnnotations`)放在内层 `dataset`,完整增强管线 `train_pipeline` 放在 `MultiImageMixDataset.pipeline`。

### 3. 启用延迟解冻骨干网络

a) 配置文件:
```python
_base_ = ['../_base_/models/faster_rcnn_r50_fpn.py',
          '../_base_/datasets/coco_detection.py',
          '../_base_/schedules/schedule_1x.py',
          '../_base_/default_runtime.py']
model = dict(backbone=dict(frozen_stages=1))
custom_hooks = [dict(type="UnfreezeBackboneEpochBasedHook", unfreeze_epoch=1)]
```

b) 实现 hook 类(原文):在 `mmdet/core/hook/unfreeze_backbone_epoch_based_hook.py` 中按原文给出的完整代码书写 `UnfreezeBackboneEpochBasedHook` 类。

### 4. 获取新骨干网络通道数(原文逐字)

```python
from mmdet.models import ResNet
import torch
self = ResNet(depth=18)
self.eval()
inputs = torch.rand(1, 3, 32, 32)
level_outputs = self.forward(inputs)
for level_out in level_outputs:
    print(tuple(level_out.shape))
```

用户可替换 `ResNet(depth=18)` 为自定义骨干以得到 `level_outputs` 的逐阶段形状,据此填写 `neck.in_channels`。

---

> **使用范围提示(原文标注):**
> - timm 骨干路径要求 **`mmcls>=0.20.0`**。
> - `UnfreezeBackboneEpochBasedHook` 原作者标注 **"Only valid for resnet"**,若用于非 ResNet 骨干需自行修改 stem / stage 命名分支逻辑。
> - 探测通道数时使用 `self.eval()`,原文未提及需配合 `torch.no_grad()` 关闭梯度,如在大骨干/大输入下需自行补充以节省显存。
