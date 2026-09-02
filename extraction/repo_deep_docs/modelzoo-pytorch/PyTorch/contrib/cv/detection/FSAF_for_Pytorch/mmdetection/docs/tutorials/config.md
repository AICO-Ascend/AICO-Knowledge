# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/config.md

# 一体化深度解读：mmdetection 配置文件教程 (Tutorial 1: Learn about Configs)

## 【定位】

本教程系统化地讲解了 mmdetection 配置系统的设计哲学与使用规范，解决"如何通过模块化与继承式配置文件来组织、管理和定制目标检测实验"这一核心问题，并配套介绍配置文件的结构、命名约定、运行时修改方式以及各组成模块的语义。

---

## 【技术要点】

1. **模块化 + 继承式配置系统**：将检测流程拆解为独立组件，通过 `_base_` 引用进行组合复用，最大继承层级为 **3 层**。

2. **四种基础组件类型**（位于 `config/_base_`）：
   - `dataset`
   - `model`
   - `schedule`
   - `default_runtime`

3. **运行时配置覆写机制**：
   - 打印完整配置命令：`python tools/misc/print_config.py /PATH/TO/CONFIG`
   - 覆写命令：`--cfg-options`（搭配 `tools/train.py` 或 `tools/test.py`）
   - 字典链覆写示例：`--cfg-options model.backbone.norm_eval=False`
   - 列表中字典覆写示例：`--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam`
   - 列表/元组整体覆写示例：`--cfg-options workflow="[(train,1),(val,1)]"`

4. **配置文件命名约定**（模板）：
   ```
   {model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
   ```
   - `{xxx}` 为必填字段，`[yyy]` 为可选字段。
   - 默认 GPU 数量×每 GPU 样本数为 `8x2`。

5. **训练调度 (schedule) 约定**：
   - `1x` = **12 epochs**，学习率在第 **8、11** epoch 衰减 10 倍。
   - `2x` = **24 epochs**，学习率在第 **16、22** epoch 衰减 10 倍。
   - `20e` = **20 epochs**（cascade 模型使用），学习率在第 **16、19** epoch 衰减 10 倍。

6. **配置迁移（已弃用模式 → 推荐模式）**：
   - 旧模式：顶层独立声明 `model = dict(...)`、`train_cfg=dict(...)`、`test_cfg=dict(...)`。
   - 新模式：将 `train_cfg`、`test_cfg` 内嵌到 `model = dict(...)` 中，作为模型配置的子字段。

---

## 【关键机制与数据】

### 配置修改的三种典型路径（原文）

- **字典链修改**：通过点号分隔的字典键路径定位字段，例如 `model.backbone.norm_eval=False` 可将骨干网络中所有 BN 模块切换为 `train` 模式（即关闭 BN 统计量冻结）。
- **列表内字典修改**：当目标位于列表内字典时，通过下标访问，例如 `data.train.pipeline.0.type=LoadImageFromWebcam` 将训练流水线第 0 步从加载文件改为从摄像头读取。
- **列表/元组整体修改**：例如将 `workflow=[('train', 1)]` 改为 `workflow="[(train,1),(val,1)]"`，**必须使用双引号**且**引号内不允许任何空白字符**。

### 文件结构与继承策略（原文）

- 一份「primitive config」由 4 类基础组件各取一份组合而成（适用于 Faster R-CNN、Mask R-CNN、Cascade R-CNN、RPN、SSD 等）。
- 同一目录下应只有 **一份** primitive config，其余配置应基于它继承。
- 贡献者建议继承已有方法，例如修改 Faster R-CNN 时先指定：
  ```
  _base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py
  ```
  再覆盖必要字段。
- 完全创新方法可新建 `xxx_rcnn` 文件夹于 `configs` 下。
- 详细配置语义参考 mmcv 文档：<https://mmcv.readthedocs.io/en/latest/utils.html#config>

### 命名风格中各字段语义（原文）

| 字段 | 含义 |
|---|---|
| `{model}` | 模型类型，如 `faster_rcnn`、`mask_rcnn` |
| `[model setting]` | 模型特殊设置，如 `without_semantic`（htc）、`moment`（reppoints）|
| `{backbone}` | 骨干网络类型，如 `r50`（ResNet-50）、`x101`（ResNeXt-101）|
| `{neck}` | 颈部网络，如 `fpn`、`pafzn`、`nasfpn`、`c4` |
| `[norm_setting]` | 归一化设置：`bn`（默认）/ `gn` / `syncbn`；`gn-head` 仅 head 用 GN，`gn-neck` 仅 neck 用 GN，`gn-all` 整个模型用 GN |
| `[misc]` | 其他杂项/插件，如 `dconv`、`gcb`、`attention`、`albu`、`mstrain` |
| `[gpu x batch_per_gpu]` | GPU 数量×每 GPU 样本，默认 `8x2` |
| `{schedule}` | 训练调度：`1x`、`2x`、`20e` 等 |
| `{dataset}` | 数据集，如 `coco`、`cityscapes`、`voc_0712`、`wider_face` |

### Mask R-CNN 配置示例中的关键数值（原文）

- 骨干网络：`type='ResNet'`，`depth=50`，`num_stages=4`，`out_indices=(0, 1, 2, 3)`，`frozen_stages=1`，`style='pytorch'`。
- 归一化配置：`type='BN'`，`requires_grad=True`，`norm_eval=True`。
- 颈部 FPN：`in_channels=[256, 512, 1024, 2048]`，`out_channels=256`，`num_outs=5`。
- RPN Head：`in_channels=256`，`feat_channels=256`，锚生成器 `scales=[8]`，`ratios=[0.5, 1.0, 2.0]`，`strides=[4, 8, 16, 32, 64]`。
- BBox Coder：`type='DeltaXYWHBBoxCoder'`，`target_means=[0.0, 0.0, 0.0, 0.0]`，`target_stds=[1.0, 1.0, 1.0, 1.0]`。
- 分类损失：`CrossEntropyLoss`，`use_sigmoid=True`，`loss_weight=1.0`。
- 回归损失：`L1Loss`（注：原文此处在示例末尾被截断，仅给出开始片段）。

> 原文说明：Mask R-CNN 示例在 `loss_bbox` 注释行中途被截断（`# Refer to https://github.com/open-mmlab/mmdet...`），后续字段（如 `loss_weight` 等）未在原文中给出，故本解读不予臆造。

---

## 【表格解读】

**原文无表格**。文档中存在多段代码块（Python 配置示例、模板字符串、迁移示例），但并未以 Markdown 表格形式呈现参数对比或性能数据。本节按要求标记为「原文无表格」。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 或伪代码形式的数学公式，故本节标记为「原文无公式」。

---

## 【关联】

- **mmcv 配置工具**：文档显式指向 mmcv 配置系统的官方文档 <https://mmcv.readthedocs.io/en/latest/utils.html#config>，说明 mmdetection 的配置解析与覆写机制直接构建在 mmcv 的 Config 工具之上，是其下游消费者。

- **各子模块的代码定位链接**（Mask R-CNN 示例中给出的源码锚点）：
  - 骨干网络 ResNet：<https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/backbones/resnet.py#L288>
  - 颈部 FPN：<https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/necks/fpn.py#L10>
  - RPN Head：<https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/dense_heads/rpn_head.py#L12>
  - Anchor Generator：<https://github.com/open-mmlab/mmdetection/blob/master/mmdet/core/anchor/anchor_generator.py#L10>
  - BBox Coder (`DeltaXYWHBBoxCoder`)：<https://github.com/open-mmlab/mmdetection/blob/master/mmdet/core/bbox/coder/delta_xywh_bbox_coder.py#L9>
  - IoU / Smooth L1 Loss 系列（在 `loss_bbox` 处链接被截断，引用模式延续自上述锚点形式）

- **上下游关系**：
  - **上游**：基础配置目录 `config/_base_`（dataset / model / schedule / default_runtime）。
  - **下游**：实验配置位于 `configs/<method>/`，通过 `_base_` 指向 `_base_` 组件或兄弟 primitive config。
  - **配套工具**：`tools/misc/print_config.py`（可视化）、`tools/train.py` / `tools/test.py`（通过 `--cfg-options` 覆写）。
  - **API 文档**：教程明确指出「更详细用法及每个模块对应的替代方案请参考 API 文档」，表明本文与 mmdetection API reference 之间是教程 → 详细参考的引导关系。

---

## 【使用方法】

### 启用方式（原文）

1. **查看完整配置**：
   ```bash
   python tools/misc/print_config.py /PATH/TO/CONFIG
   ```

2. **运行时覆写配置**：在调用训练/测试脚本时附加 `--cfg-options`：
   ```bash
   # 覆写字典链
   python tools/train.py /PATH/TO/CONFIG --cfg-options model.backbone.norm_eval=False

   # 覆写列表内字典
   python tools/train.py /PATH/TO/CONFIG --cfg-options data.train.pipeline.0.type=LoadImageFromWebcam

   # 覆写列表/元组（必须用双引号且引号内无空白）
   python tools/train.py /PATH/TO/CONFIG --cfg-options workflow="[(train,1),(val,1)]"
   ```

3. **新建配置文件**：
   - 优先基于已有方法继承，例如：
     ```python
     _base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py
     # 然后覆写需要修改的字段
     ```
   - 全新方法可在 `configs/` 下新建 `xxx_rcnn/` 文件夹，并在其中放置 primitive config（继承 `_base_` 中的四类组件）。

4. **迁移旧版配置**：将顶层 `train_cfg`、`test_cfg` 合并至 `model = dict(...)` 的内部字段中（参考「Deprecated train_cfg/test_cfg」一节的 before/after 示例）。

### 配置项

- **命名字段**：见【技术要点】第 4 条命名约定。
- **调度字段**：见【技术要点】第 5 条训练调度约定。
- **归一化字段**：`bn`（默认）、`gn`、`syncbn`、`gn-head`、`gn-neck`、`gn-all`。
- **杂项 (misc) 字段**：`dconv`、`gcb`、`attention`、`albu`、`mstrain` 等。

> 原文未涉及具体的「开关式」命令行参数说明（如 `--gpu-ids`、`--seed` 等），亦未涉及 `tools/` 下其它脚本的调用方式，故本节不补充臆造内容。
