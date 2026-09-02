# Tutorial 2: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/2_finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/2_finetune.md

# 一体化深度解读:PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/2_finetune.md

## 【定位】

这篇文档是 MMAction2 框架下的**模型微调 (Finetuning) 教程**,指导用户如何将基于 Kinetics-400 等数据集预训练的识别模型 (以 TSN/R(2+1)D 体系下的 2D 识别器为例)迁移到新的下游数据集 (如 UCF101) 上,以获得更好的性能。教程聚焦于"修改配置文件"这一核心动作,串联起 backbone 复用、分类头替换、数据集适配、优化策略调整与预训练权重加载五个环节。

---

## 【技术要点】

1. **两阶段微调流程**:先按 [Tutorial 3: Adding New Dataset](3_new_dataset.md) 增加新数据集支持,再修改 config 文件(本文档重点)。
2. **分类头 (cls_head) 类别数替换**:`num_classes` 由 Kinetics-400 的 `400` 改为 UCF101 的 `101`,其余预训练权重全部复用;in_channels 保持 `2048`,空间池化类型 `spatial_type='avg'`,dropout_ratio `0.4`,init_std `0.01`。
3. **Backbone 初始化与任务权重的解耦**:`pretrained='torchvision://resnet50'` 仅用于 ImageNet 初始化 backbone,与微调任务无关;真正载入预训练识别模型靠 `load_from`。
4. **数据集配置项**:dataset_type 选用 `'RawframeDataset'`,data_root、data_root_val、ann_file_train、ann_file_val、ann_file_test 五个路径/标注文件路径需正确指向 UCF101 的 rawframes 目录与 train/val 列表文件。
5. **训练 schedule 调小**:SGD 优化器 `lr` 由 `0.01` 降至 `0.005`,momentum `0.9`,weight_decay `0.0001`;梯度裁剪 `max_norm=40, norm_type=2`;step 学习率衰减节点 `[20, 40]`;total_epochs 由 `100` 减为 `50`;checkpoint 保存间隔 `interval=5`。
6. **预训练权重载入机制**:默认在 `configs/_base_/default_runtime.py` 中 `load_from=None`,依赖配置继承机制,用户可在自有 config 中覆盖 `load_from`,指向 OpenMMLab S3 上的 Kinetics-400 TSN-R50 预训练权重 URL。

---

## 【关键机制与数据】

**工作原理 / 数据流**

- 文档以 `Recognizer2D + ResNet(depth=50) + TSNHead` 作为典型 backbone-head 组合,展示微调配置改写路径。
- 数据流层面,沿用 MMAction2 标准五元组配置:`dataset_type` + `data_root` (train) + `data_root_val` (val) + `ann_file_train` + `ann_file_val`,test 阶段复用 `ann_file_val` 作为示例。
- 权重加载层面,继承自 `_base_/default_runtime.py` 的 `load_from=None` 通过配置继承 (inheritance design) 被用户自定义 config 覆盖,实现"只改一项即可加载预训练模型"。
- 微调的核心思想:**只替换与类别数强相关的最后一层 (cls_head),保留 backbone 及大部分 head 的预训练权重**;同时降低学习率、缩短训练 epoch,避免灾难性遗忘。

**性能 / 数值数据 (原文)**

- 类别数变化:`400 → 101` (Kinetics-400 → UCF101)。
- 学习率变化:`0.01 → 0.005`。
- 总 epoch 变化:`100 → 50`。
- 其余固定超参:in_channels=`2048`、dropout_ratio=`0.4`、init_std=`0.01`、momentum=`0.9`、weight_decay=`0.0001`、grad_clip max_norm=`40`、norm_type=`2`、step=`[20, 40]`、checkpoint interval=`5`。

> 原文未提供具体的精度/mAP 等性能数字或耗时数据。

---

## 【表格解读】

**原文无表格。** 教程中所有信息均以 Python 配置字典 (config) 的形式给出,而非表格结构。

---

## 【公式解读】

**原文无公式。** 全文未出现 LaTeX 或伪代码形式的数学表达式;所有数值参数都以 config 字段形式呈现 (如 `lr=0.005`、`max_norm=40`、`step=[20, 40]`),无显式公式。

---

## 【关联】

- **上游链接**:[Tutorial 3: Adding New Dataset](3_new_dataset.md) — 微调流程的前置条件,负责在框架内注册新的数据集包装类与标注解析方式。
- **同级链接**:[1_config.md](/docs/tutorials/1_config.md) 与文档中内嵌的 [here](1_config.md) 锚点 — 解释 config 的整体结构 (backbone / cls_head / train_cfg / test_cfg / dataset / optimizer / lr_config / total_epochs / checkpoint_config / load_from 等),是本文四处修改动作 (Modify Head / Dataset / Training Schedule / Use Pre-Trained Model) 的语义基础。
- **配置继承链**:`/docs/tutorials/1_config.md` 中阐述的 inheritance design 决定了 `load_from` 只需在用户 config 中显式赋值即可覆盖 `_base_/default_runtime.py` 中的默认值 `None`,这是"使用预训练模型"一节的底层机制。
- **下游生态**:文中指向 OpenMMLab S3 的 TSN-R50 Kinetics-400 预训练权重 URL (`tsn_r50_1x1x3_100e_kinetics400_rgb_...pth`),与 model zoo 联动;用户在 R(2+1)D 模型库中也可类比使用对应的预训练 checkpoint 链接。

---

## 【使用方法】

启用微调需要完成的全部配置改动 (以 Kinetics-400 → UCF101 为例):

**1) 修改 cls_head (`num_classes`)**
```python
cls_head=dict(
    type='TSNHead',
    num_classes=101,   # 原 400,改为新数据集类别数
    in_channels=2048,
    spatial_type='avg',
    consensus=dict(type='AvgConsensus', dim=1),
    dropout_ratio=0.4,
    init_std=0.01)
```

**2) 修改 dataset 配置**
```python
dataset_type = 'RawframeDataset'
data_root = 'data/ucf101/rawframes_train/'
data_root_val = 'data/ucf101/rawframes_val/'
ann_file_train = 'data/ucf101/ucf101_train_list.txt'
ann_file_val = 'data/ucf101/ucf101_val_list.txt'
ann_file_test = 'data/ucf101/ucf101_val_list.txt'
```

**3) 修改训练 schedule**
```python
optimizer = dict(type='SGD', lr=0.005, momentum=0.9, weight_decay=0.0001)  # lr 由 0.01 降至 0.005
optimizer_config = dict(grad_clip=dict(max_norm=40, norm_type=2))
lr_config = dict(policy='step', step=[20, 40])
total_epochs = 50  # 由 100 减为 50
checkpoint_config = dict(interval=5)
```

**4) 指定预训练权重 (`load_from`)**
```python
load_from = 'https://open-mmlab.s3.ap-northeast-2.amazonaws.com/mmaction/mmaction-v1/recognition/tsn_r50_1x1x3_100e_kinetics400_rgb/tsn_r50_1x1x3_100e_kinetics400_rgb_20200614-e508be42.pth'
```

> 原文未涉及具体的启动训练命令行 (如 `tools/train.py` 调用形式)、分布式/单卡启动方式、是否需要冻结 backbone 层、warmup 配置等细节;这些需结合 [1_config.md](/docs/tutorials/1_config.md) 与仓库根目录的使用文档进一步查阅。
