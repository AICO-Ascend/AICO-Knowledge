# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/tutorials/config.md

# 一体化深度解读:Tutorial 1: Learn about Configs

## 【定位】

这篇文档是 DeepLabV3_for_Pytorch(基于 mmseg 框架)配置系统的入门指南,核心解决"如何组织、命名、继承语义分割实验配置"的问题,并通过一份完整注释过的 PSPNet+ResNet50V1c 配置示例,帮助使用者快速建立对现代语义分割系统各模块的具象认知。

---

## 【技术要点】

1. **配置检视命令**:可执行 `python tools/print_config.py /PATH/TO/CONFIG` 查看完整配置;追加 `--options xxx.yyy=zzz` 可看到临时覆盖后的更新配置。
2. **4 类基础组件**:在 `config/_base_` 下,共有四类基本组件——**dataset、model、schedule、default_runtime**;每类各取一份即可组合成一个完整方法(原文称这种组合后的 config 为 _primitive_)。
3. **继承层级约束**:同一文件夹下推荐**只保留一份 _primitive_ 配置**,其他配置都应继承自它;最大继承层级为 **3**。
4. **新方法继承路径**:若改动基于已有方法(如 DeepLabV3),通过 `_base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py` 引入骨架后,再覆写必要字段;若是全新方法则需在 `configs` 下新建 `xxxnet` 文件夹。
5. **配置文件命名规范**:`{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{schedule}_{dataset}`,其中 `{xxx}` 为必填、`[yyy]` 为可选;默认 `8x2`(GPU 数 × 每 GPU batch);`{schedule}` 中 `20ki` 代表 20k iterations。
6. **测试模式选项**:`test_cfg = dict(mode='whole')`,可选 `'whole'`(整图全卷积测试)或 `'sliding'`(滑窗裁剪);原文未给出 sliding 的具体窗口参数。

---

## 【关键机制与数据】

### 工作原理与数据流(原文逐条梳理)

- **模块化 + 继承式设计**:配置由 dataset / model / schedule / default_runtime 四类组件拼装而成,各组件可被继承、覆写,从而在不动基础结构的前提下快速开展实验。
- **Primitive 配置原则**:每个目录下仅保留一份 _primitive_ 配置,其他配置全部继承自它,继承深度上限 **3 层**;这保证目录结构清晰且不易出现循环覆盖。
- **骨干网络载入**(原文:`pretrained='open-mmlab://resnet50_v1c'`):从 open-mmlab 模型库拉取 ImageNet 预训练权重;骨干名为 `ResNetV1c`,depth=50,num_stages=4,out_indices=(0,1,2,3),dilations=(1,1,2,4),strides=(1,2,1,1),style='pytorch'(stride=2 用 3×3 conv,对应 caffe 风格则用 1×1 conv),contract_dilation=True。
- **解码头与辅助头**(PSPNet 范例):
  - decode_head 类型 `PSPHead`,in_channels=2048,in_index=3,channels=512,**pool_scales=(1, 2, 3, 6)**,dropout_ratio=0.1,num_classes=19,align_corners=False,loss_decode 为 `CrossEntropyLoss`(use_sigmoid=False,loss_weight=1.0)。
  - auxiliary_head 类型 `FCNHead`,in_channels=1024,in_index=2,channels=256,num_convs=1,concat_input=False,dropout_ratio=0.1,num_classes=19,loss_weight=**0.4**(原文:"usually 0.4 of decode head")。
- **归一化策略**:语义分割通常用 SyncBN,`norm_cfg=dict(type='SyncBN', requires_grad=True)`,norm_eval=False(不冻结 BN 统计量);骨干和解码头/辅助头均保持一致。
- **数据流(train_pipeline 顺序,原文)**:
  1. `LoadImageFromFile` → 2. `LoadAnnotations` → 3. `Resize`(img_scale=(2048, 1024),ratio_range=(0.5, 2.0)) → 4. `RandomCrop`(crop_size=(512,1024),cat_max_ratio=0.75) → 5. `RandomFlip`(flip_ratio=0.5) → 6. `PhotoMetricDistortion` → 7. `Normalize`(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True) → 8. `Pad`(size=(512,1024), pad_val=0, seg_pad_val=255) → 9. `DefaultFormatBundle` → 10. `Collect`(keys=['img','gt_semantic_seg'])。
- **关键数值(原文逐字保留)**:
  - 类别数约定:**cityscapes=19、VOC=21、ADE20k=150**。
  - 图像归一化 mean=[123.675, 116.28, 103.53],std=[58.395, 57.12, 57.375],to_rgb=True(与 ImageNet 预训练骨干保持一致)。
  - 训练 crop_size=(512, 1024);缩放 img_scale=(2048, 1024);随机缩放比 ratio_range=(0.5, 2.0);随机翻转 flip_ratio=0.5;随机裁剪 cat_max_ratio=0.75;Pad 填充 image 用 0、gt_semantic_seg 用 255。
- **测试增强封装**:`MultiScaleFlipAug`,img_scale=(2048, 1024) 作为测试最大尺度(原文末尾截断于 "used fo",后续内容未给出)。

### 原文未给出的内容

- 训练 schedule(optimizer、lr、迭代次数等)的具体字段在示例代码中**未展示**,原文仅以 PSPNet 的"现代分割系统"作为模块结构示例,schedule 部分需参考 API 文档。
- 性能数据(mIoU、fps 等)**原文未涉及**。

---

## 【表格解读】

**原文无表格。** 全文由 Markdown 文本、Python 配置代码块和命令片段组成,未出现任何 markdown 表格;参数对照信息以代码注释形式给出(如 backbone 字段、`pool_scales=(1,2,3,6)` 等)。

---

## 【公式解读】

**原文无公式。** 文档未给出任何 LaTeX 数学表达式或伪代码公式;仅以配置字段赋值(如 `norm_cfg`、`loss_decode`)展示语义分割系统的组件结构。

---

## 【关联】

- **上游依赖 — mmcv 配置系统**:文末明确指向 [mmcv 配置文件说明](https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html),作为"详细文档"的权威参考,说明本配置体系继承自 mmcv 的 modular + inheritance 范式。
- **同目录兄弟方法**:文档多次以 DeepLabV3、PSPNet 为例,并提到 DeepLabV3 的 `_base_` 路径(`../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py`),暗示与 `configs/deeplabv3/`、`configs/pspnet/` 等目录中的配置同属 _primitive_/继承 体系。
- **下游可改写模块**:PSPNet 范例中以注释形式指向多个子目录作为"备选项",包括:
  - 骨干实现:`mmseg/backbone/resnet.py`(`ResNetV1c` 详情)。
  - 解码头/辅助头类型清单:`mmseg/models/decode_heads`(用于查阅 `PSPHead`、`FCNHead` 等可用类型)。
- **数据集映射**:通过 `dataset_type = 'CityscapesDataset'`、`data_root = 'data/cityscapes/'` 与 `{dataset}` 命名字段(`cityscapes`、`voc12aug`、`ade`)建立与 `_base_/datasets/` 的对应关系(原文未直接给出 `_base_` 数据集路径,但通过命名约定隐式关联)。
- **API 文档**:文末提示"For more detailed usage and the corresponding alternative for each modules, please refer to the API documentation",作为教程 1 的下游阅读路径。

---

## 【使用方法】

1. **查看完整配置**:
   ```
   python tools/print_config.py /PATH/TO/CONFIG
   ```
2. **临时覆盖并查看更新配置**:
   ```
   python tools/print_config.py /PATH/TO/CONFIG --options xxx.yyy=zzz
   ```
3. **继承已有 _primitive_**(以 DeepLabV3 为基础做修改时,在配置文件首行写):
   ```python
   _base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py
   ```
   然后在本地覆写需要变动的字段即可。
4. **新建方法**:在 `configs/` 下创建 `xxxnet/` 文件夹,并放置 _primitive_ 配置(无 `_base_` 指向),其下所有配置继承该 _primitive_;继承深度不超过 **3 层**。
5. **命名新配置**:遵循 `{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{schedule}_{dataset}`,例如 `deeplabv3_r50_dconv_8x2_512x1024_40ki_cityscapes`(示意,原文未给出该完整示例)。
6. **配置示例中可直接复用的关键值(原文)**:
   - `norm_cfg = dict(type='SyncBN', requires_grad=True)`(语义分割通用)。
   - 图像归一化:`mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]`、`to_rgb=True`。
   - `test_cfg = dict(mode='whole')` 或 `'sliding'`(原文仅给出 whole 用法)。
   - `dataset_type`/`data_root` 与 `{dataset}` 命名保持一致(原文用 `CityscapesDataset` + `data/cityscapes/`)。
7. **原文未涉及的启用项**:具体启动训练/测试命令、schedule(optimizer/lr/iter)字段、滑动测试窗口尺寸等,原文均未给出,需查阅 mmcv 文档与 API 文档补齐。
