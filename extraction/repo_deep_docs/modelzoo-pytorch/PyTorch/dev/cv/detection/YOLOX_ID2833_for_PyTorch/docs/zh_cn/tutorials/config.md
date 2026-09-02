# 教程 1: 学习配置文件

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/config.md

# 一体化深度解读：MMDetection 配置文件学习教程

## 【定位】

本文系统讲解 MMDetection（YOLOX 等检测模型共用的检测框架）配置文件的**组织方式、继承机制、命令行覆写规范与命名约定**，帮助使用者从零理解一张配置 `xxx.py` 如何由 4 类 `_base_` 组件组合而成，以及如何在不修改源文件的前提下通过 `--cfg-options` 灵活调整训练/测试行为。

---

## 【技术要点】

1. **配置继承与 4 类基组件**：在 `config/_base_/` 下固定存在 4 类原始组件——`数据集(dataset)`、`模型(model)`、`训练策略(schedule)`、`运行时默认设置(default runtime)`。任何具体算法配置都是由这 4 类组件的"原始配置(primitive)"继承组合而成，并被推荐**同一目录下仅保留 1 个原始配置**，最大继承深度限制为 **3**。

2. **三种命令行覆写模式**（`tools/train.py` / `tools/test.py` 通用）：
   - **字典链覆写**：`--cfg-options model.backbone.norm_eval=False` —— 按原 dict 键顺序定位，可一次性影响子树（如主干所有 BN 模块进入 `train` 模式）。
   - **列表内字典覆写**：`--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam` —— 通过**下标**访问 pipeline 列表中的某一项。
   - **列表/元组整体替换**：`--cfg-options workflow="[(train,1),(val,1)]"` —— 引号必须包裹整个值，且**引号内不允许出现空格**。

3. **配置命名模板**：`{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`，其中 `{xxx}` 必填、`[yyy]` 可选，默认 batch 配置为 **8x2**。

4. **训练 schedule 数值约定**：`1x=12 epoch`、`2x=24 epoch`、`20e=20 epoch`（仅级联模型用）。学习率衰减策略：1x/2x 在第 **8/16 与 11/22 epoch** 处衰减 10 倍；20e 在第 **16 与 19 epoch** 处衰减 10 倍。

5. **`train_cfg` / `test_cfg` 已弃用**：必须将这两个字段从顶层迁移到 `model=dict(...)` 的内部，变为 `model=dict(type=..., train_cfg=dict(...), test_cfg=dict(...))` 的嵌套结构。

6. **配置检视工具**：`python tools/misc/print_config.py /PATH/TO/CONFIG` 用于把继承展开后的最终配置打印出来，避免手动追踪多级继承。

---

## 【关键机制与数据】

**配置合并工作原理（原文）**：用户在某一目录写一个 `xxx_rcnn_r50_fpn_1x_coco.py`，通过 `_base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` 实现继承，运行时注册器会按 `_base_` 字段递归合并所有被继承文件，最终得到一份完整的扁平配置。`print_config.py` 即是触发这一合并流程的可视化工具。

**Mask R-CNN 示例所揭示的完整模型骨架（原文参数逐项还原）**：

- **backbone (ResNet-50)**：`depth=50`，`num_stages=4`，`out_indices=(0,1,2,3)`，`frozen_stages=1`，`norm_cfg=dict(type='BN', requires_grad=True)`，`norm_eval=True`，`style='pytorch'`（步长 2 的层为 3×3 卷积；'caffe' 则为 1×1），`init_cfg=dict(type='Pretrained', checkpoint='torchvision://resnet50')`。
- **neck (FPN)**：`in_channels=[256, 512, 1024, 2048]`（与 backbone 各级输出一致），`out_channels=256`，`num_outs=5`。
- **rpn_head**：`type='RPNHead'`，`feat_channels=256`；锚框 `scales=[8]`，`ratios=[0.5, 1.0, 2.0]`，`strides=[4, 8, 16, 32, 64]`（与 FPN 特征步幅一致，未设 `base_sizes` 时步幅值即被当作 `base_sizes`）；`bbox_coder=DeltaXYWHBBoxCoder`，`target_means=[0.0,0.0,0.0,0.0]`，`target_stds=[1.0,1.0,1.0,1.0]`；`loss_cls=CrossEntropyLoss(use_sigmoid=True, loss_weight=1.0)`；`loss_bbox=L1Loss(loss_weight=1.0)`。
- **roi_head.bbox_roi_extractor**：`SingleRoIExtractor`，`roi_layer=RoIAlign(output_size=7, sampling_ratio=0)`，`out_channels=256`，`featmap_strides=[4, 8, 16, 32]`。
- **roi_head.bbox_head**：`Shared2FCBBoxHead`，`in_channels=256`，`fc_out_channels=1024`，`roi_feat_size=7`，`num_classes=80`，`bbox_coder=DeltaXYWHBBoxCoder`，`target_means=[0.0,0.0,0.0,0.0]`，`target_stds=[0.1, 0.1, 0.2, 0.2]`（原文："因为框更准确，所以值更小，常规设置时 [0.1, 0.1, 0.2, 0.2]"），`reg_class_agnostic=False`，`loss_cls=CrossEntropyLoss(use_sigmoid=False, loss_weight=1.0)`，`loss_bbox=L1Loss(loss_weight=1.0)`。
- **roi_head.mask_roi_extractor**：`SingleRoIExtractor`，`RoIAlign(output_size=14, sampling_ratio=0)`，`out_channels=256`，`featmap_strides=[4, 8, 16, 32]`。
- **roi_head.mask_head**（原文在此处被截断，仅可见以下参数）：`type='FCNMaskHead'`，`num_convs=4`，`in_channels=256`，`conv_out_channels=256`，`num_classes=80`，`loss_mask=dict(type='CrossEntropyLoss', use_mask=True, ...)`。

**数据流（原文隐含）**：backbone 输出 4 个尺度 → FPN 融合为 5 个尺度 (`num_outs=5`) → RPN 在 5 个尺度上以 `strides=[4,8,16,32,64]` 产生候选框 → RoIAlign 将候选框按 `featmap_strides=[4,8,16,32]`（去掉 64）映射回特征图 → bbox 分支输出 7×7 特征用于分类/回归，mask 分支输出 14×14 特征用于分割。

---

## 【表格解读】

**原文无表格**。

（说明：原文中以代码字典形式罗列配置项，例如 `Mask R-CNN` 整段配置是嵌套 dict 而非 markdown 表格结构，故按"原文无表格"标注。）

---

## 【公式解读】

原文给出 1 处**伪代码形式的命名模板**（作为文件名生成规则）：

```text
{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
```

**符号含义**：

| 占位符 | 是否必填 | 含义 | 示例 |
|---|---|---|---|
| `{model}` | 必填 | 模型种类 | `faster_rcnn`、`mask_rcnn` |
| `[model setting]` | 可选 | 特定模型变体 | `without_semantic`（htc 中）、`moment`（reppoints 中） |
| `{backbone}` | 必填 | 主干网络 | `r50`（ResNet-50）、`x101`（ResNeXt-101） |
| `{neck}` | 必填 | Neck 类型 | `fpn`、`pafpn`、`nasfpn`、`c4` |
| `[norm_setting]` | 可选 | 归一化设置，默认 `bn` | `gn`、`syncbn`、`gn-head`、`gn-neck`、`gn-all` |
| `[misc]` | 可选 | 插件/数据增强等 | `dconv`、`gcb`、`attention`、`albu`、`mstrain` |
| `[gpu x batch_per_gpu]` | 可选 | GPU 数 × 每卡样本数，默认 `8x2` | `4x2`、`8x4` |
| `{schedule}` | 必填 | 训练方案 | `1x`（12 epoch）、`2x`（24 epoch）、`20e`（20 epoch，级联） |
| `{dataset}` | 必填 | 数据集 | `coco`、`cityscapes`、`voc_0712`、`wider_face` |

**作用**：通过下划线分段，使任意一个配置文件都能从文件名一眼读出"模型/主干/Neck/归一化/插件/算力/schedule/数据"七要素，便于大规模实验管理。

---

## 【关联】

- **上下游模块**：
  - 注册与合并机制依赖外部库 **MMCV** 的 `Config` 类，原文明确建议参考 [MMCV 配置文档](https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html) 获取更多继承/合并语义。
  - 本文是教程系列的"教程 1"，后续教程（原文提到但本文未展开）通常涵盖自定义数据集、模型、数据增强、训练 Pipeline 等。

- **被频繁引用的 mmdetection 源码**（用于追溯具体实现类）：
  - `mmdet/models/backbones/resnet.py`（ResNet backbone）
  - `mmdet/models/necks/fpn.py`（FPN neck）
  - `mmdet/models/dense_heads/rpn_head.py`（RPNHead）
  - `mmdet/core/anchor/anchor_generator.py`（AnchorGenerator）
  - `mmdet/core/bbox/coder/delta_xywh_bbox_coder.py`（DeltaXYWHBBoxCoder）
  - `mmdet/models/losses/smooth_l1_loss.py`（Smooth L1 Loss）
  - `mmdet/models/roi_heads/standard_roi_head.py`、`bbox_heads/convfc_bbox_head.py`、`mask_heads/fcn_mask_head.py`、`roi_extractors/single_level.py`
  - `mmdet/ops/roi_align/roi_align.py`（RoIAlign，含 DeformRoIPoolingPack、ModulatedDeformRoIPoolingPack）

- **训练/测试入口脚本**：`tools/train.py`、`tools/test.py`（共享 `--cfg-options` 覆写接口），辅助工具 `tools/misc/print_config.py`。

- **可构建的方法**：原文列出可被该配置体系"很容易地构建"的方法——`Faster R-CNN`、`Mask R-CNN`、`Cascade R-CNN`、`RPN`、`SSD`。

- **与 train_cfg/test_cfg 迁移相关的接口**：将 `train_cfg`、`test_cfg` 由顶层键迁移进 `model` 字典后，模型类需具备相应字段读取能力（即新版 mmdet 模型注册器约定），这是与代码层强耦合的一处约定。

---

## 【使用方法】

**原文已涉及**：

1. **打印最终合并后的配置**：
   ```bash
   python tools/misc/print_config.py /PATH/TO/CONFIG
   ```

2. **训练时覆写主干 BN 模式**：
   ```bash
   python tools/train.py --cfg-options model.backbone.norm_eval=False
   ```

3. **训练时替换 pipeline 中的数据加载器**：
   ```bash
   python tools/train.py --cfg-options data.train.pipeline.0.type=LoadImageFromWebcam
   ```

4. **修改 workflow 为 train/val 交替**（注意引号内**无空格**）：
   ```bash
   python tools/train.py --cfg-options workflow="[(train,1),(val,1)]"
   ```

5. **继承式构造新配置**：在已有方法基础上修改时，设置 `_base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` 然后覆写需要变动的字段；构建全新结构时，在 `configs/` 下新建 `xxx_rcnn/` 目录并撰写 4 类 `_base_` 组件配置。

6. **train_cfg/test_cfg 迁移**：将原顶层 `train_cfg=dict(...)`、`test_cfg=dict(...)` 整体移入 `model=dict(...)` 内，作为其子字段，触发检测器在构造时统一从 `model.train_cfg` / `model.test_cfg` 读取。

> 原文未涉及：YOLOX 专属配置字段、命令行分布式启动细节（如 `--launcher`）、自动学习率缩放规则（线性缩放）、AMP / 梯度累积等开关在配置文件中的写法——这些需要在 `configs/yolox/` 下对应的具体配置或后续教程中查阅。
