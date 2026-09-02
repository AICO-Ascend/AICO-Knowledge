# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/config.md

# config.md 深度解读

## 【定位】
本文档系统介绍了 MMDetection 风格目标检测框架中**配置系统（Config System）的模块化与继承式设计**，以及如何通过命令行参数、命名约定、结构组织来高效管理检测模型实验配置。

---

## 【技术要点】

1. **模块化 + 继承式配置**：config 系统采用模块化与继承设计，便于进行多种实验对比。
2. **配置查看命令**：`python tools/misc/print_config.py /PATH/TO/CONFIG` 用于打印完整配置。
3. **`--cfg-options` 命令行覆盖机制**：
   - 按 dict 链顺序修改：`--cfg-options model.backbone.norm_eval=False`（将 backbone 中所有 BN 模块切换为 train 模式）；
   - 修改列表中元素：`--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam`；
   - 修改 list/tuple 值：`--cfg-options workflow="[(train,1),(val,1)]"`（**必须**使用双引号，引号内**不允许**空白字符）。
4. **四种基础组件类型**（位于 `config/_base_`）：`dataset`、`model`、`schedule`、`default_runtime`；由这四类组件组合而成的 config 称为 _primitive_（原语配置）。
5. **继承层级最多为 3 层**，同一文件夹下推荐只保留**一个** _primitive_ 配置，其余均继承自它。
6. **废弃字段迁移**：原配置文件根级别的 `train_cfg` / `test_cfg` 已废弃，需迁移到 `model=dict(..., train_cfg=dict(...), test_cfg=dict(...))` 中。

---

## 【关键机制与数据】

原文信息整理如下：

- **继承层级上限**：最大继承深度为 3（原文："the maximum of inheritance level is 3"）。
- **调度（schedule）策略**：
  - `1x` = 12 epochs；
  - `2x` = 24 epochs；
  - `20e` = 20 epochs（Cascade 系列模型采用）；
  - 初始学习率衰减规则：对于 `1x`/`2x`，学习率分别在第 8/16 epoch 与第 11/22 epoch 处衰减 10×；对于 `20e`，学习率分别在第 16 epoch 与第 19 epoch 处衰减 10×（原文："decays by a factor of 10 at the 8/16th and 11/22th epochs" / "at the 16th and 19th epochs"）。
- **默认 GPU×batch**：`8x2`（即 8 卡 × 每卡 2 个样本）为默认设置。
- **BN 冻结开关**：`--cfg-options model.backbone.norm_eval=False` 会把 backbone 中**所有** BN 模块切换为 train 模式（即不冻结 BN 统计量）。
- **配置文件命名风格**：详见下方表格解读。
- **文档截断**：原文最末给的 Mask R-CNN 代码示例以 `loss_bbox=` 处截断（仅注释到 L1Loss 之前），并未给出完整配置。

---

## 【表格解读】

原文并未以表格形式呈现数据，但其配置命名模板是一段结构化规则，可视为"配置项表"逐字段解读如下：

| 字段 | 是否必填 | 取值/示例 | 原文含义 |
|---|---|---|---|
| `{model}` | 必填 | `faster_rcnn`、`mask_rcnn` 等 | 模型类型 |
| `[model setting]` | 可选 | `without_semantic`（用于 `htc`）、`moment`（用于 `reppoints`） | 特定模型设置 |
| `{backbone}` | 必填 | `r50`（ResNet-50）、`x101`（ResNeXt-101） | 主干网络类型 |
| `{neck}` | 必填 | `fpn`、`pafpn`、`nasfpn`、`c4` | neck 类型 |
| `[norm_setting]` | 可选 | `bn`（默认）/`gn`/`syncbn`/`gn-head`/`gn-neck`/`gn-all` | BN 为默认归一化；`gn-head`/`gn-neck` 表示 GN 仅应用于 head/neck；`gn-all` 表示整个模型（含 backbone、neck、head）均使用 GN |
| `[misc]` | 可选 | `dconv`、`gcb`、`attention`、`albu`、`mstrain` | 模型杂项 / 插件 |
| `[gpu x batch_per_gpu]` | 可选 | `8x2`（默认） | GPU 数量 × 每 GPU 样本数 |
| `{schedule}` | 必填 | `1x` / `2x` / `20e` 等 | 训练调度：`1x`=12 epochs、`2x`=24 epochs、`20e`=20 epochs（Cascade 模型采用） |
| `{dataset}` | 必填 | `coco`、`cityscapes`、`voc_0712`、`wider_face` | 训练数据集 |

原文模板（逐字保留）：

```
{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
```

`{xxx}` 表示必填字段，`[yyy]` 表示可选字段。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游工具脚本**：本文档反复依赖 `tools/misc/print_config.py`（配置查看）、`tools/train.py` 与 `tools/test.py`（训练/测试入口），它们是配置系统唯一对外的运行入口。
- **配置基础设施**：配置继承、合并、命令行覆盖等底层机制依赖 mmcv 的 Config 实现，详细文档指向外部链接 *https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html*。
- **检测器代码定位**：Mask R-CNN 示例中的多个字段给出了指向 mmdetection 仓库具体源文件的注释链接，例如：
  - backbone (`resnet.py`)：*https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/backbones/resnet.py#L308*
  - neck (`fpn.py`)：*https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/necks/fpn.py#L10*
  - rpn_head (`rpn_head.py`)：*https://github.com/open-mmlab/mmdetection/blob/master/mmdet/models/dense_heads/rpn_head.py#L12*
  - anchor_generator (`anchor_generator.py`)：*https://github.com/open-mmlab/mmdetection/blob/master/mmdet/core/anchor/anchor_generator.py#L10*
  - bbox_coder (`delta_xywh_bbox_coder.py`)：*https://github.com/open-mmlab/mmdetection/blob/master/mmdet/core/bbox/coder/delta_xywh_bbox_coder.py#L9*
  - 因原文示例在 `loss_bbox` 注释段被截断，未能给出后续组件（如 `roi_head`、损失函数后续）的对应链接。
- **继承式方法扩展**：以 Faster R-CNN 为基线进行修改时，可在配置中通过 `_base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` 继承其结构，再覆写特定字段；这是与 _primitive_ 配置、3 层继承上限直接挂钩的实践方式。
- **内部链接**：用户提示"内部链接: (无)"，即本页未提供内部交叉链接。

---

## 【使用方法】

1. **查看完整配置**：
   ```bash
   python tools/misc/print_config.py /PATH/TO/CONFIG
   ```

2. **通过 `--cfg-options` 覆盖配置键**（以 `tools/train.py` 与 `tools/test.py` 为入口）：
   - 修改 dict 链：
     ```bash
     --cfg-options model.backbone.norm_eval=False
     ```
   - 修改列表中第 `0` 项的 `type`：
     ```bash
     --cfg-options data.train.pipeline.0.type=LoadImageFromWebcam
     ```
   - 修改 list/tuple（必须双引号、内不容许空白）：
     ```bash
     --cfg-options workflow="[(train,1),(val,1)]"
     ```

3. **配置文件命名**遵循模板：
   ```
   {model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
   ```
   举例语义（原文未给出具体字面示例，但根据命名规范可理解的字段组合：`faster_rcnn_r50_fpn_1x_coco.py`）。

4. **从已有方法继承示例**（Faster R-CNN 改造）：
   ```python
   _base_ = '../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'
   # then override necessary fields
   ```

5. **train_cfg/test_cfg 迁移**：将原先与 `model` 平级的 `train_cfg=dict(...)` / `test_cfg=dict(...)` 移入 `model=dict(...)` 内部的两个同名字段中（原文已给出 deprecated 与 recommended 两种写法）。

6. **全新方法**：若新方法结构与现有方法均不共享，需在 `configs` 下新建 `xxx_rcnn` 文件夹（原文未涉及更多配置生成细节）。
