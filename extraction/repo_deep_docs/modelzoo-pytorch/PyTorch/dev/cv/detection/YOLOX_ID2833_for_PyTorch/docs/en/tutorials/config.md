# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/config.md

【定位】
本篇文档面向「modelzoo-pytorch」(YOLOX_PyTorch)仓中检测方向,系统性地介绍了其**配置系统(Config)的模块化与继承式机制**,回答「如何查看、修改、命名、组织一份检测任务的配置文件」这一核心问题。

【技术要点】
1. **配置设计理念**:采用 *modular + inheritance* 设计,方便做多种实验对比。
2. **配置文件查看命令**:`python tools/misc/print_config.py /PATH/TO/CONFIG` 可打印完整合并后的 config。
3. **就地修改配置**:通过 `tools/train.py` 或 `tools/test.py` 配合 `--cfg-options` 参数,无需手动改文件即可覆盖原 config 字段。
4. **四类基础组件(`config/_base_`)**:dataset、model、schedule、default_runtime;Faster R-CNN / Mask R-CNN / Cascade R-CNN / RPN / SSD 等「primitive」配置均由这四类各取一份组合而成;**继承层级最多 3 层**。
5. **配置文件命名模板**: `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`(`{xxx}` 必填,`[yyy]` 可选)。
6. **train_cfg / test_cfg 已废弃**:必须从顶层独立字段下沉到 `model=dict(...)` 内部。

【关键机制与数据】
- 原文「Update config keys of dict chains」:链式 key 可被覆盖,例如 `--cfg-options model.backbone.norm_eval=False` 会把所有 backbone 内的 BN 模块切回训练模式。
- 原文「Update keys inside a list of configs」:`data.train.pipeline` 是一个 list(元素是 dict),可用 `--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam` 替换 list 中第 0 个元素的 type。
- 原文「Update values of list/tuples」:list/tuple 值整体替换,例如 `workflow=[('train', 1)]` 改为 `[('train',1),('val',1)]`,注意**引号内不允许出现空白**。
- 原文:schedule 数值——`1x` = 12 epochs、`2x` = 24 epochs、`20e` = 20 epochs(cascade 模型专用);LR 在 8/16 与 11/22 epoch 处衰减 10×(`1x`/`2x`);`20e` 在 16 与 19 epoch 处衰减 10×。
- 原文:默认 batch 设置 `[gpu x batch_per_gpu]` 中 `8x2` 为默认。
- 原文:继承层次「maximum of inheritance level is 3」,每个同目录配置族建议**只有一个 primitive**,其余全部继承它。
- 原文:Mask R-CNN config 示例中 `frozen_stages=1`、`nnum_outs=5`、`out_indices=(0,1,2,3)`、`depth=50`、`norm_eval=True`、`style='pytorch'`,FPN `in_channels=[256,512,1024,2048]`,`out_channels=256`。

【表格解读】
原文的 config 命名模板以伪代码形式给出,我把它**逐字保留**并按字段含义做表格化解读(原文本身没有 markdown 表格):

```
{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}
```

| 字段 | 是否必填 | 取值示例(原文) | 含义 |
|---|---|---|---|
| `{model}` | 必填 | `faster_rcnn`, `mask_rcnn` | 模型族名 |
| `[model setting]` | 可选 | `without_semantic`(htc)、`moment`(reppoints) | 某些方法的特定子设定 |
| `{backbone}` | 必填 | `r50`(ResNet-50)、`x101`(ResNeXt-101) | 主干网络 |
| `{neck}` | 必填 | `fpn`、`pafpn`、`nasfpn`、`c4` | neck 模块类型 |
| `[norm_setting]` | 可选 | `bn`(默认)、`gn`、`syncbn`、`gn-head`、`gn-neck`、`gn-all` | BN 默认,否则用 GN/SyncBN;`gn-head`/`gn-neck` 只在 head/neck 用 GN,`gn-all` 全模型都用 |
| `[misc]` | 可选 | `dconv`、`gcb`、`attention`、`albu`、`mstrain` | 杂项 plugin/设置 |
| `[gpu x batch_per_gpu]` | 可选 | `8x2`(默认) | GPU 数量 × 单卡 batch |
| `{schedule}` | 必填 | `1x`(12 ep)、`2x`(24 ep)、`20e`(20 ep,cascade) | 训练 schedule;`1x`/`2x` 在 8/16、11/22 ep 处 LR×0.1,`20e` 在 16、19 ep 处 LR×0.1 |
| `{dataset}` | 必填 | `coco`、`cityscapes`、`voc_0712`、`wider_face` | 数据集 |

补充:原文还提到一种「伪表格」式的 deprecated vs recommended 代码块,见下一节。

【公式解读】
原文无 LaTeX 公式。仅给出了一段 Python 代码形式的**配置迁移模板**,我将其视为「伪代码公式」逐字保留:

```python
# deprecated
model = dict(
    type=...,
    ...
)
train_cfg=dict(...)
test_cfg=dict(...)
```

符号含义:
- `model`:`dict`,detector 主配置,`type` 字段指明检测器类名(如 `MaskRCNN`)。
- `train_cfg` / `test_cfg`:训练/测试阶段的额外配置,顶层独立字段,**已废弃**。

```python
# recommended
model = dict(
    type=...,
    ...
    train_cfg=dict(...),
    test_cfg=dict(...),
)
```

符号含义:把 `train_cfg`、`test_cfg` 嵌入到 `model=dict(...)` 内部,使其成为模型自身的一部分;这样模型本身自包含训练/测试策略,更利于复用与继承。

【关联】
- 原文末尾给出官方参考链:`mmcv` 的 config 文档 — 详解 Python 风格 config 的合并与继承底层实现(`https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html`)。
- Mask R-CNN 示例中引用的 mmdetection 源码链接(均为**外链** GitHub):
  - ResNet backbone 实现(`models/backbones/resnet.py`)
  - FPN neck 实现(`models/necks/fpn.py`)
  - RPN head(`models/dense_heads/rpn_head.py`)
  - AnchorGenerator(`core/anchor/anchor_generator.py`)
  - DeltaXYWHBBoxCoder(`core/bbox/coder/delta_xywh_bbox_coder.py`)
- 上下文中提到的相关组件(均在 `_base_` 中):
  - `dataset configs`:coco / cityscapes / voc_0712 / wider_face
  - `schedule configs`:`1x`、`2x`、`20e`
  - `default_runtime`:与训练/测试 pipeline、日志、hook 相关的默认运行时配置
- 文档最后被截断于 `loss_bbox` 的 L1Loss 配置注释(原文以 `Refer to https://github.com/` 结束),但已经在同一 Mask R-CNN 示例中给出了**完整的 RPN head 链路**:anchor_generator → bbox_coder → loss_cls → loss_bbox。

【使用方法】
- **查看完整配置**:`python tools/misc/print_config.py /PATH/TO/CONFIG`
- **就地修改并训练/测试**:`python tools/train.py /PATH/TO/CONFIG --cfg-options key.subkey=value`(`tools/test.py` 同理);支持:
  - 链式 dict key 覆盖:`--cfg-options model.backbone.norm_eval=False`
  - list 内元素覆盖:`--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam`
  - list/tuple 整体覆盖:`--cfg-options workflow="[(train,1),(val,1)]"`(**引号内不允许空白**)
- **新建配置族**:在 `configs/` 下创建 `xxx_rcnn` 文件夹,先 `_base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`,再覆写差异字段;继承层数 ≤ 3。
- **norm 设置切换**:默认 BN;可通过 `gn` / `syncbn` / `gn-head` / `gn-neck` / `gn-all` 等命名后缀区分作用范围(作用于 backbone/head/neck 的 BN ↔ GN)。
- **检测器 backbone 切换**:在 `init_cfg` 中指定 `checkpoint='torchvision://resnet50'` 等预训练权重路径;`norm_eval=True` 冻结 BN 统计量。
- 原文未涉及:具体 hook 配置、可视化开关、distributed launcher(如 `dist_train.sh`)等细节。
