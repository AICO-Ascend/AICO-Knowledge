# Tutorial 7: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/tutorials/finetune.md

# Tutorial 7: Finetuning Models 深度解读

## 【定位】

这篇文档是 MMDetection V2.0 体系下 (被 GFocalV2 收录的 contrib 教程) 的 "教程 7: 微调模型", 解决的核心问题是:**如何将基于 COCO 等大规模数据集预训练好的检测器 (Model Zoo) 迁移到新的下游数据集 (例如 CityScapes、KITTI) 上, 以获得更好的性能**。文档以 Cityscapes 数据集上的 Mask R-CNN 微调为例, 给出从 config 继承、head 改造、训练调度调整到加载预训练权重的完整步骤。

## 【技术要点】

1. **微调两大步骤 (原文)**:
   - 步骤一: 按照 [Tutorial 2: Customize Datasets](customize_dataset.md) 添加对新数据集的支持。
   - 步骤二: 修改 config (本文档详细讨论)。

2. **配置继承 (Inheritance)**: 利用 MMDetection V2.0 的多 config 继承机制, 新 config 通过 `_base_` 列表同时继承模型结构、数据集与运行时三个基础 config, 而无需重写全部内容。

3. **Head 改造的"减法"原则**: 仅修改 `num_classes` (从 COCO 的 80 改为新数据集的类别数, Cityscapes 实例分割示例中为 `num_classes=8`), 其余层 (backbone/fpn/共享 head) 沿用预训练权重, **最终预测层因维度不匹配需要重新训练**。

4. **训练调度的"小 lr + 短 epoch"原则**: 微调阶段使用比默认 schedule 更小的学习率和更少的训练轮数, 避免破坏预训练得到的特征。

5. **预训练权重的离线加载**: 通过 `load_from` 字段指向远端 `.pth` 文件, 建议**提前下载**而非训练时在线拉取, 避免下载时间影响训练。

6. **批大小对应的 lr 标定 (原文批注)**: 优化器中 `lr=0.01` 是针对 batch size=8 设置的, 用户在变更 batch size 时需按比例缩放。

## 【关键机制与数据】

- **工作原理**:
  - 模型参数分为两类: **可复用部分** (backbone、FPN、共享 box head/mask head 主体) 直接继承预训练权重; **必须重训部分** (最终的分类/回归/掩码预测层) 因输出维度与新数据集类别数 `num_classes=8` 不匹配, 通过 `pretrained=None` 关闭当前层的预训练加载, 随机初始化后从零学习。
  - 训练调度通过 `step=[7]` + `total_epochs=8` 的组合实现 "**8 轮 × 8 倍 = 实际 64 个 epoch**" 的等效长周期训练, 但在第 7 个 epoch 处 step decay 一次, 注释明确指出 "[7] yields higher performance than [6]"。

- **关键数据流**:
  1. 启动训练 → 加载 `_base_` 中的模型、数据集、运行时配置 →
  2. 覆盖 head 中 `num_classes=8` →
  3. 从 `load_from` URL 下载/读取 `mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth` →
  4. 按 key 匹配加载权重, 不匹配的层 (最终 head) 跳过 →
  5. 使用 `optimizer=dict(type='SGD', lr=0.01, ...)` 在 Cityscapes 上以 batch=8 微调 8 个 epoch →
  6. 第 7 个 epoch 后 step 衰减学习率。

- **性能/数据原话标注**:
  - 原文: "[7] yields higher performance than [6]" —— 表示学习率衰减节点取 7 比取 6 在该实验设置下效果更好。
  - 原文未提供具体的 mAP/AP 等数值结果。

## 【表格解读】

**原文无表格**。文中的 config 代码片段是 Python 字典字面量, 不构成表格语义; 参数值已分别在各小节中体现, 这里不强行重组为表格。

## 【公式解读】

**原文无公式** (无 LaTeX 公式或伪代码形式的数学表达式)。

可补充说明: 文中隐含的 "等效 epoch" 关系可表达为 `effective_epochs = total_epochs × scale_factor`, 其中原文以注释 `# actual epoch = 8 * 8 = 64` 给出, 即 `64 = 8 × 8`; 但这是文字注释中的算式, 不是文档正式公式。

## 【关联】

文档定位为教程链条中的一环, 其内部链接与上下游关系如下:

| 关联对象 | 关系 | 链接指向 |
|---|---|---|
| Model Zoo | **上游数据源**: 提供可下载的预训练检测器 (例如 `mask_rcnn_r50_fpn_2x_...`), 通过 `load_from` 字段消费 | [../model_zoo.md](../model_zoo.md) |
| Tutorial 2: Customize Datasets | **前置步骤**: 微调第一步 "添加对新数据集的支持" 依赖此教程, 涉及数据集类注册、`dataset_type`、`classes` 元信息等 | [customize_dataset.md](customize_dataset.md) |
| `_base_/models/mask_rcnn_r50_fpn.py` | **继承的模型结构配置**: 定义 backbone + FPN + RoI Head 的整体骨架 | (configs 目录内) |
| `_base_/datasets/cityscapes_instance.py` | **继承的数据集配置**: 定义 Cityscapes 实例分割数据 pipeline | (configs 目录内) |
| `_base_/default_runtime.py` | **继承的运行时配置**: 定义默认的 logger、checkpoint、timestamper 等 | (configs 目录内) |

文档同时与 GFocalV2 项目的整体教程链 (Tutorial 1~6) 形成纵向衔接: 前置教程 (如 Tutorial 2) 处理 "如何支持新数据", 本教程处理 "如何在新数据上微调", 后续可衔接模型评估/部署 (Tutorial 8+)。

## 【使用方法】

以 Cityscapes + Mask R-CNN R50-FPN 微调为例, 完整流程 (原文摘录并按原文顺序整理):

1. **新建 config 文件**, 在文件顶部以 `_base_` 列表继承三个基础 config:
   ```python
   _base_ = [
       '../_base_/models/mask_rcnn_r50_fpn.py',
       '../_base_/datasets/cityscapes_instance.py', '../_base_/default_runtime.py'
   ]
   ```

2. **修改 head** —— 关键是把 `num_classes` 改为新数据集的类别数 (Cityscapes 实例分割示例为 8):
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
               loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
               loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
           mask_head=dict(
               type='FCNMaskHead',
               num_convs=4,
               in_channels=256,
               conv_out_channels=256,
               num_classes=8,
               loss_mask=dict(type='CrossEntropyLoss', use_mask=True, loss_weight=1.0))))
   ```

3. **修改训练调度** —— 较默认 schedule 降低 lr、缩短 epoch:
   ```python
   # optimizer (lr 对应 batch size=8)
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

4. **加载预训练权重** —— 建议提前下载后再训练:
   ```python
   load_from = 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/mmdetection/models/mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth'
   ```

5. **配置项速查表** (基于原文出现过的关键字段):

   | 字段 | 作用 | 原文中给出的取值 |
   |---|---|---|
   | `model.pretrained` | 是否加载 backbone 预训练 | `None` (从 `load_from` 统一控制) |
   | `model.roi_head.bbox_head.num_classes` | 分类头类别数 | `8` |
   | `model.roi_head.mask_head.num_classes` | 掩码头类别数 | `8` |
   | `optimizer.lr` | 初始学习率 | `0.01` (batch size=8) |
   | `optimizer.momentum` | SGD 动量 | `0.9` |
   | `optimizer.weight_decay` | 权重衰减 | `0.0001` |
   | `lr_config.policy` | lr 策略 | `'step'` |
   | `lr_config.warmup` | 预热方式 | `'linear'` |
   | `lr_config.warmup_iters` | 预热迭代数 | `500` |
   | `lr_config.warmup_ratio` | 起始 lr 比例 | `0.001` |
   | `lr_config.step` | step 衰减节点 | `[7]` |
   | `total_epochs` | 训练总 epoch | `8` |
   | `log_config.interval` | 日志间隔 | `100` |
   | `load_from` | 预训练权重 URL/路径 | `mask_rcnn_r50_fpn_2x_20181010-41d35c05.pth` |

**注**: 启动训练所用的命令行 (例如 `tools/train.py <config>`)、N 卡多机分布式启动方式、超参搜索脚本等内容 **原文未涉及**, 未做推断。
