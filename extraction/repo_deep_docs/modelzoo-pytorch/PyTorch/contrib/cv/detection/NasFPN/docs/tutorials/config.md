# Tutorial 1: Learn about Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/config.md

# 深度解读: Tutorial 1: Learn about Configs

## 【定位】
这篇文档是 MMDetection 风格配置系统（基于 mmcv）的入门教程,系统性地阐述如何在继承式/模块化的 config 体系下查看、修改、继承与命名配置文件,从而让用户能够以最小代价复现/改造检测模型（Faster R-CNN、Mask R-CNN、Cascade R-CNN、RPN、SSD 以及本案所在路径提到的 NasFPN 等）的实验配置。

## 【技术要点】

1. **模块化 + 继承式 Config 设计**: 在 `config/_base_` 下有 4 类基础组件 —— `dataset`、`model`、`schedule`、`default_runtime`;多配置文件通过 `_base_` 字段引用组合而成 (称为 *primitive*),继承层数最多 **3 级**。

2. **运行时原地修改的三种 `--cfg-options` 用法**:
   - 修改 dict 链: `--cfg-options model.backbone.norm_eval=False` (让 backbone 中所有 BN 回到 train 模式)。
   - 修改列表内元素: `--cfg-options data.train.pipeline.0.type=LoadImageFromWebcam` (按索引 0 替换)。
   - 修改 list/tuple 值: `--cfg-options workflow="[(train,1),(val,1)]"`,要求双引号包裹、**值内不允许空白字符**。

3. **Config 命名规范 (强制/可选字段)**:
   `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`,默认 batch 配置为 **`8x2`**。

4. **训练 schedule 与学习率衰减策略**:
   - `1x` = 12 epoch,`2x` = 24 epoch;二者在第 **8/16 epoch** 与 **11/22 epoch** 处各衰减 10×。
   - `20e` = 20 epoch (级联模型使用),在第 **16 epoch** 与 **19 epoch** 处各衰减 10×。

5. **`train_cfg` / `test_cfg` 已弃用**: 必须内联进 `model = dict(...)` 之下作为子字段,而不再以顶层 key 出现 (避免与 `model` 同级造成歧义)。

6. **Mask R-CNN 示例的结构化参数**: Backbone 输出 `out_indices=(0,1,2,3)` 对应 `in_channels=[256,512,1024,2048]`;FPN `out_channels=256, num_outs=5`;anchor 步长 `[4,8,16,32,64]` 与 FPN 特征步长一一对应;box coder 用 `target_means=[0.0,0.0,0.0,0.0]`、`target_stds=[1.0,1.0,1.0,1.0]`;RPN 分类损失 `loss_weight=1.0`,RPN 二分类默认 `use_sigmoid=True`。

## 【关键机制与数据】

- **Config 检视机制**: 通过 `python tools/misc/print_config.py /PATH/TO/CONFIG` 把继承链全部展开后打印,这是诊断配置冲突/查看最终合并结果的核心命令。
- **数据流 (运行时修改)**: `--cfg-options` 经由 mmcv 的 Config 对象在内存中就地 patch,不写回源文件 —— 适合在 slurm/集群训练任务中临时切换超参,例如把 backbone 的 BN 切到 train (`norm_eval=False`) 或将数据管线第 0 步 `LoadImageFromFile` 换成 `LoadImageFromWebcam`。
- **Backbone 数据流 (Mask R-CNN 案例)**: ResNet-50 (`depth=50`, `num_stages=4`, `style='pytorch'` 即 stride-2 放在 3×3 conv 内;`style='caffe'` 则放在 1×1) → `frozen_stages=1` 冻结 stage 0 → 输出 4 个 feature map → FPN 融合为 5 层金字塔 → stride `[4,8,16,32,64]` 与金字塔各级严格对齐,供 `RPNHead` (256-channel) 接入。
- **性能/训练数据 (原文披露范围)**:
  - 原文:`1x` schedule = 12 epoch;`2x` = 24 epoch;`20e` = 20 epoch。
  - 原文:默认 batch 形态为 `8x2` (8 卡 × 每卡 2 sample)。
  - 原文:默认 backbone 为 `BN`;可选 `GN`/`SyncBN`,并可通过 `gn-head`/`gn-neck`/`gn-all` 限定归一化应用范围。
  - 原文:本文档未提供 mAP、FPS、显存等实测性能数字。

## 【表格解读】
**原文无表格** (无任何 markdown 表格;只有一段伪表格形态的命名模板和一段代码示例)。如需将命名模板转写为表,可参照下表 (此为对原文模板的纯形式化转写,**不构成原文表格**):

| 字段 | 是否必选 | 取值示例 (原文出现) | 含义 (原文) |
|---|---|---|---|
| `{model}` | 必选 | `faster_rcnn`, `mask_rcnn`, ... | 模型类型 |
| `[model setting]` | 可选 | `without_semantic` (htc), `moment` (reppoints) | 某些模型的特定设定 |
| `{backbone}` | 必选 | `r50` (ResNet-50), `x101` (ResNeXt-101) | 主干网络类型 |
| `{neck}` | 必选 | `fpn`, `pafpn`, `nasfpn`, `c4` | 颈部网络类型 |
| `[norm_setting]` | 可选 | `bn` (默认), `gn`, `syncbn`, `gn-head`, `gn-neck`, `gn-all` | 归一化层类型及作用范围 |
| `[misc]` | 可选 | `dconv`, `gcb`, `attention`, `albu`, `mstrain` | 杂项插件/设定 |
| `[gpu x batch_per_gpu]` | 可选 | `8x2` (默认) | GPU 数 × 每卡 batch |
| `{schedule}` | 必选 | `1x`, `2x`, `20e` | 训练 schedule |
| `{dataset}` | 必选 | `coco`, `cityscapes`, `voc_0712`, `wider_face` | 数据集 |

## 【公式解读】
**原文无公式** (全文未出现 LaTeX/伪代码形式的数学公式;仅有的"准公式"是命名模板 `{model}_[model setting]_{backbone}_{neck}_[norm setting]_[misc]_[gpu x batch_per_gpu]_{schedule}_{dataset}`,其中 `{}` 表示必选、`[]` 表示可选,这是字符串拼接约定而非数学表达式)。

## 【关联】

- **与 NasFPN 的关联**: 本文档位于 `NasFPN/docs/tutorials/config.md`,但内容是通用 MMDetection-style config 教程;在 `neck=dict(type='FPN', ...)` 的注释里明确指出 "We also support 'NASFPN', 'PAFPN', etc.",即 **NasFPN 是该 config 体系中可选的 `neck` 取值之一**,可直接替换 `type='FPN'` 启用,其余 `in_channels=[256,512,1024,2048]`、`out_channels=256`、`num_outs=5` 等参数语义保持一致。
- **上下游模块 (通过外链指明)**:
  - `mmcv` config 工具基类 → [mmcv utils.html#config](https://mmcv.readthedocs.io/en/latest/utils.html#config) 提供 Config 合并/继承/序列化的底层实现。
  - `mmdet/models/backbones/resnet.py#L288` → ResNet 实现入口,被 `backbone=dict(type='ResNet', ...)` 引用。
  - `mmdet/models/necks/fpn.py#L10` → FPN/NASFPN/PAFPN 实现入口,被 `neck=dict(type='FPN', ...)` 引用。
  - `mmdet/models/dense_heads/rpn_head.py#L12` → RPNHead/GARPNHead 实现入口。
  - `mmdet/core/anchor/anchor_generator.py#L10` → AnchorGenerator (注意:SSD 用 `SSDAnchorGenerator`)。
  - `mmdet/core/bbox/coder/delta_xywh_bbox_coder.py#L9` → `DeltaXYWHBBoxCoder` (大多数方法默认)。
- **检测任务关联**: 同一套 config 体系被文中列举的 *primitive* 方法共用 —— Faster R-CNN、Mask R-CNN、Cascade R-CNN、RPN、SSD —— 表示 NasFPN 可作为 neck 直接嫁接到这些模型上,只需替换 `neck` 字段而保留 `model`、`dataset`、`schedule`、`default_runtime` 四件套。

## 【使用方法】

- **检视完整配置** (合并所有继承): `python tools/misc/print_config.py /PATH/TO/CONFIG`。
- **提交训练/测试任务时覆盖配置**:
  - `python tools/train.py ... --cfg-options model.backbone.norm_eval=False`
  - `python tools/test.py ... --cfg-options data.train.pipeline.0.type=LoadImageFromWebcam`
  - `python tools/train.py ... --cfg-options workflow="[(train,1),(val,1)]"` (注意双引号包裹、值内无空白)。
- **构建新方法的推荐流程**: 若与现有方法同结构,在 `configs` 下新建文件并设置 `_base_ = ../faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` 后只覆差不同字段;若与现有方法均不共享结构,新建 `xxx_rcnn` 文件夹。
- **原始的 `train_cfg` / `test_cfg` 迁移方式**: 把这两个 dict 内联到 `model = dict(...)` 之下作为 `model.train_cfg` / `model.test_cfg` (原文 "recommended" 写法)。
- **启用 NasFPN 的具体写法 (原文未给出完整示例,仅在 neck 注释里说 "We also support 'NASFPN'")** —— 原文未涉及完整 NasFPN config 字段;按命名规范应产出形如 `mask_rcnn_r50_nasfpn_1x_coco.py` 的文件名,把 `neck=dict(type='NASFPN', ...)` 替换 `type='FPN'` 即可 (具体 NasFPN 参数需参考 mmdet necks 实现,原文未提供)。
