# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/config.md

# 一体化深度解读：`PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/config.md`

---

## 【定位】

本篇是 CascadeMaskRCNN_iflytek_for_PyTorch（基于 MMDetection 体系）配置系统（Config System）的入门 Tutorial 1，系统性讲解"如何理解、修改、组织和命名检测配置文件"，使读者能够基于 `_base_` 继承 + `cfg-options` 覆盖 + 命名约定三件套快速构建和裁剪检测实验配置。

---

## 【技术要点】

1. **配置继承与模块化设计**：配置采用"组合 + 继承"模式，`config/_base_` 下有 4 类基础组件——`dataset`、`model`、`schedule`、`default_runtime`，每种检测方法（Faster R-CNN / Mask R-CNN / Cascade R-CNN / RPN / SSD 等）均由一个 `_base_` 拼接而成，被称为 **primitive** 配置；同目录下建议仅保留 1 个 primitive，最大继承层级为 **3**。

2. **运行时配置覆盖机制**：提交 `tools/train.py` 或 `tools/test.py` 时可通过 `--cfg-options` 就地改写配置，三类典型用法：
   - **字典链覆写**：例如 `--cfg-options model.backbone.norm_eval=False` 将 backbone 中所有 BN 模块切换为 train 模式；
   - **列表元素覆写**：例如 `--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam`；
   - **列表/元组整体覆写**：例如 `--cfg-options workflow="[(train,1),(val,1)]"`，注意字符串外需包裹双引号且 **引号内不允许空白字符**。

3. **配置打印工具**：`python tools/misc/print_config.py /PATH/TO/CONFIG` 可打印完整配置用于检查。

4. **配置命名约定模板**：
   `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`
   - `{xxx}` 为必选字段，`[yyy]` 为可选字段；
   - 默认 batch 规模标记为 **`8x2`**（8 卡 × 每卡 2 个样本）；
   - backbone 简写：`r50` (ResNet-50)、`x101` (ResNeXt-101)；
   - neck 简写：`fpn`、`pafpn`、`nasfpn`、`c4`；
   - norm 简写：`bn`（默认）/ `gn`（Group Normalization）/ `syncbn`（SyncBN），并以 `gn-head` / `gn-neck` / `gn-all` 限定 GN 作用范围（head 仅、neck 仅、全模型）；
   - misc 标记：`dconv`、`gcb`、`attention`、`albu`、`mstrain` 等；
   - 数据集标记：`coco`、`cityscapes`、`voc_0712`、`wider_face`。

5. **学习率衰减方案（schedule）**：
   - `1x` = **12 epochs**，初始学习率在 **8 / 11** epoch 处 ×0.1 衰减；
   - `2x` = **24 epochs**，初始学习率在 **16 / 22** epoch 处 ×0.1 衰减；
   - `20e` = **20 epochs**（cascade 系模型采用），初始学习率在 **16 / 19** epoch 处 ×0.1 衰减。

6. **`train_cfg` / `test_cfg` 已弃用迁移**：原独立顶层 `train_cfg=dict(...)` / `test_cfg=dict(...)` 必须迁入 `model=dict(...)` 内部的 `train_cfg` / `test_cfg` 子键，以适配新版模型构造范式。

---

## 【关键机制与数据】

**工作原理 / 数据流**：

- **配置加载与覆盖原理**：MMDetection 启动训练时，递归合并 `_base_` 所列的 primitive 文件 → 当前配置文件顶层 override → 命令行 `--cfg-options` 字典/列表索引式覆盖。三者按优先级从低到高叠加，最终生成 `cfg` 全局字典喂入各 build 函数。
- **in-place 覆盖语义**：--cfg-options 并不修改磁盘上的 .py 文件，而是对内存中已加载的 cfg 做键路径定位式 patch，因此支持"原配置不动 + 一次实验一个 diff"。
- **list/tuple 改写必须整体替换**：由于 shell token 化限制，无法用 `--cfg-options` 对列表"局部插一项"，只能传整串字符串并让解析器再 `eval`（这正是引号内不允许空白的原因，防止切分错位）。

**Mask R-CNN 示例中的关键数据**（原文）：
- Backbone：`ResNet`，`depth=50`，`num_stages=4`，`out_indices=(0,1,2,3)`，`frozen_stages=1`，BN `norm_cfg` 的 `requires_grad=True`，`norm_eval=True`，style=`pytorch`；
- Neck：`FPN`，`in_channels=[256, 512, 1024, 2048]`，`out_channels=256`，`num_outs=5`；
- RPN head：`feat_channels=256`，`AnchorGenerator` 的 `scales=[8]`、`ratios=[0.5, 1.0, 2.0]`、`strides=[4, 8, 16, 32, 64]`；
- BBox coder：`DeltaXYWHBBoxCoder`，`target_means=[0.0, 0.0, 0.0, 0.0]`、`target_stds=[1.0, 1.0, 1.0, 1.0]`；
- 损失：分类用 `CrossEntropyLoss`（`use_sigmoid=True`，`loss_weight=1.0`），回归用 `L1Loss`；预训练权重 `pretrained='torchvision://resnet50'`。

> 注：原文示例代码在 `loss_bbox` 注释 "smooth_l1_loss.py#L56 for implementation." 处被截断，未暴露完整 Mask R-CNN 的 head/train_cfg 部分，本解读仅基于已展示字段。

---

## 【表格解读】

**原文无表格。**

原文以**模板字符串**形式给出"配置命名风格"：

```
{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
```

并以**缩进的字段说明列表**替代表格，对每个占位符做解释。逐条解读如下（按原文顺序）：

| 字段语法 | 是否必选 | 含义与典型取值（原文摘录） |
|---|---|---|
| `{model}` | 必选 | 模型族，如 `faster_rcnn`、`mask_rcnn` 等 |
| `[model setting]` | 可选 | 模型特有设定，如 `htc` 的 `without_semantic`、`reppoints` 的 `moment` 等 |
| `{backbone}` | 必选 | 主干网络，如 `r50` (ResNet-50)、`x101` (ResNeXt-101) |
| `{neck}` | 必选 | 颈部结构，如 `fpn`、`pafpn`、`nasfpn`、`c4` |
| `[norm_setting]` | 可选 | 默认 `bn`；可选 `gn` / `syncbn`；作用域限定 `gn-head` / `gn-neck` / `gn-all` |
| `[misc]` | 可选 | 杂项插件/设定，如 `dconv`、`gcb`、`attention`、`albu`、`mstrain` |
| `[gpu x batch_per_gpu]` | 可选 | 训练规模，默认 `8x2` |
| `{schedule}` | 必选 | 训练计划：`1x`（12 ep）、`2x`（24 ep）、`20e`（20 ep，cascade 用） |
| `{dataset}` | 必选 | 数据集，如 `coco`、`cityscapes`、`voc_0712`、`wider_face` |

> 上表为"按原文字段列表重整"，内容完全来自原文，**未引入**额外取值或命名。

---

## 【公式解读】

**原文无 LaTeX/伪代码公式。**

可视为配置命名"模板"的占位符串已在上节以表格形式还原；学习率衰减规则以自然语言描述（`1x`/`2x` 在 8/16 与 11/22 epoch 衰减，`20e` 在 16 与 19 epoch 衰减，倍率均为 0.1），未以公式形式给出，因此本节不强行捏造表达式。

---

## 【关联】

基于文末内部链接信息（**原文未提供任何内部超链接**，仅在字段说明中指向 mmcv 与 mmdetection GitHub 上的若干源码 #L 号锚点，例如 `resnet.py#L288`、`fpn.py#L10`、`rpn_head.py#L12`、`anchor_generator.py#L10`、`delta_xywh_bbox_coder.py#L9`、`smooth_l1_loss.py#L56` 等），可关联出以下上下游模块：

- **上游基础设施**：`mmcv`（提供 Config 类、Registry、build_from_cfg 等，本文档末句提及 "Please refer to mmcv for detailed documentation."）；
- **同 repo 内配置目录**：`config/_base_/` 下的 `dataset` / `model` / `schedule` / `default_runtime` 四类基础组件文件，以及各模型族目录（如 `faster_rcnn/`、`mask_rcnn/`、`cascade_rcnn/`）下的 primitive 配置；
- **下游训练 / 测试入口**：`tools/train.py`、`tools/test.py`（消费 `--cfg-options`）；
- **打印 / 检查工具**：`tools/misc/print_config.py`（消费完整 config 路径）；
- **下游模型组件（示例 Mask R-CNN 中涉及）**：mmdetection 中的 `ResNet` 主干、`FPN` / `NASFPN` / `PAFPN` 颈部、`RPNHead` / `GARPNHead` 头部、`AnchorGenerator` / `SSDAnchorGenerator`、`DeltaXYWHBBoxCoder`、`CrossEntropyLoss` / `FocalLoss` / `L1Loss` / IoU 系损失等；
- **同期 Tutorial 系列**：本篇是 Tutorial 1，可推测后续 tutorial 会基于本文的配置约定继续展开（custom dataset、custom model、useful tools 等），但原文未给出链接。

---

## 【使用方法】

1. **查看完整配置（合并 `_base_` 之后）**：
   ```bash
   python tools/misc/print_config.py /PATH/TO/CONFIG
   ```

2. **启动训练 / 测试并就地覆盖配置键**：
   ```bash
   python tools/train.py ${CONFIG} --cfg-options model.backbone.norm_eval=False
   python tools/test.py  ${CONFIG} --cfg-options data.test.pipeline.0.type=LoadImageFromWebcam
   ```
   - 字典链：`--cfg-options a.b.c=value`；
   - 列表下标：`--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam`；
   - 列表/元组整体替换（**必须双引号 + 内不容许空白**）：
     `--cfg-options workflow="[(train,1),(val,1)]"`。

3. **构建新方法的目录约定**：若与现有方法的结构均不共享，应在 `configs/` 下新建一个 `xxx_rcnn/` 目录，内部放置从 `_base_` 继承而来的 primitive 配置，并控制最大继承深度为 3 层。

4. **迁移旧配置（`train_cfg` / `test_cfg` 弃用）**：将
   ```python
   # deprecated
   model = dict(type=..., ...)
   train_cfg = dict(...)
   test_cfg  = dict(...)
   ```
   改写为
   ```python
   # recommended
   model = dict(
       type=..., ...,
       train_cfg=dict(...),
       test_cfg=dict(...),
   )
   ```
   即把训练/测试相关超参数下沉到模型内部统一管理。

> 命令、键路径与命名模板均来自原文；本节未引入 `--cfg-options` 之外的额外 CLI 选项或新工具调用。
