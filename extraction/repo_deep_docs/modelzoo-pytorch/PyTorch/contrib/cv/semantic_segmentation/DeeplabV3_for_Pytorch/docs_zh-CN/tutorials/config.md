# 教程 1: 学习配置文件

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs_zh-CN/tutorials/config.md

```markdown
# 一体化深度解读：DeeplabV3_for_Pytorch 配置体系文档

## 【定位】
本文档是面向 DeepLabV3 (含 PSPNet 等同类语义分割模型) 在 PyTorch 框架下使用的 **教程 1：学习配置文件**，通过约定继承与模块组合，教会使用者如何阅读、查看与复用 `_base_` 配置文件，以最小代价派生并修改新的训练/测试配置。

---

## 【技术要点】
1. **配置查看入口**：执行 `python tools/print_config.py /PATH/TO/CONFIG` 可打印完整解析后的配置；可通过 `--options xxx.yyy=zzz` 在打印前就地覆写任意层级键值，便于做差异对比。
2. **四大基础组件**：位于 `config/_base_`，分别对应 **数据集 (dataset)、模型 (model)、训练策略 (schedule)、运行时默认设置 (default runtime)**；任何具体配置都通过组合这四类组件得到。
3. **继承深度上限为 3**：每一目录下推荐**唯一一份原始配置 (primitive)**，其余配置必须继承自该 primitive，避免超深继承带来的可维护性塌陷。
4. **命名约定 (强制项)**：
   `{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{schedule}_{dataset}`
   - `{model}` 例：`psp`、`deeplabv3`
   - `{backbone}` 例：`r50` (ResNet-50)、`x101` (ResNeXt-101)
   - `[misc]` 例：`dconv`、`gcb`、`attention`、`mstrain`
   - `[gpu x batch_per_gpu]` 默认 `8x2`
   - `{schedule}` 例：`20ki` 表示 20k iterations
   - `{dataset}` 例：`cityscapes`、`voc12aug`、`ade`
5. **跨方法继承范式**：若改 DeepLabV3，先写 `_base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py`，再覆写差异字段；全新模型需在 `configs/` 下建独立子目录 `xxxnet`。
6. **PSPNet + ResNet50V1c 完整字段示例**：涵盖 backbone (ResNetV1c, depth=50, 4 stages, dilations=(1,1,2,4), strides=(1,2,1,1))、decode_head (PSPHead, channels=512, pool_scales=(1,2,3,6), num_classes=19) 与 auxiliary_head (FCNHead, num_convs=1, channels=256, loss_weight=0.4)，并显式给出数据集 (Cityscapes)、归一化常数 (mean=[123.675,116.28,103.53], std=[58.395,57.12,57.375])、train/test pipeline 全字段说明。

---

## 【关键机制与数据】
> 标注说明：以下所有数字/参数均来自原文，未额外揣测。

**工作机制（配置组合）：**
- 原始配置 (primitive) 由来自 `_base_` 的 4 类组件拼接而成，DeepLabV3、PSPNet 等都能借此快速组装。
- 同一目录推荐**仅 1 份 primitive**，其余配置只是它的子节点；最大继承深度为 3。
- 推荐社区贡献者**优先继承已有方法**而非从零开始。

**PSPNet 关键参数流 (原文数据)：**
- backbone：`ResNetV1c`, `depth=50`, `num_stages=4`, `out_indices=(0,1,2,3)`, `dilations=(1,1,2,4)`, `strides=(1,2,1,1)`, `style='pytorch'`, `contract_dilation=True`
- decode_head (PSPHead)：`in_channels=2048`, `in_index=3`, `channels=512`, `pool_scales=(1,2,3,6)`, `dropout_ratio=0.1`, `num_classes=19`, `loss_weight=1.0`
- auxiliary_head (FCNHead)：`in_channels=1024`, `in_index=2`, `channels=256`, `num_convs=1`, `concat_input=False`, `dropout_ratio=0.1`, `num_classes=19`, `loss_weight=0.4`
- 公共 norm：`SyncBN, requires_grad=True`, `norm_eval=False`
- 训练：`samples_per_gpu=2`, `workers_per_gpu=2`, `crop_size=(512,1024)`
- 数据增广组合：Resize 比例 `(0.5, 2.0)`、RandomCrop `cat_max_ratio=0.75`、RandomFlip `flip_ratio=0.5`、PhotoMetricDistortion、Pad `pad_val=0`, `seg_pad_val=255`
- 测试：`test_cfg = dict(mode='whole')`，支持 `'whole'`（全卷积整图）与 `'sliding'`（滑窗裁剪）两种模式；MultiScaleFlipAug 内部以 `keep_ratio=True` 进行 Resize

**类别映射约定 (原文)：** cityscapes=19 类，VOC=21 类，ADE20k=150 类。

**性能数据**：原文未提供任何 benchmark 数字/精度对比/速度。

---

## 【表格解读】
**原文无表格**。

注：原文以伪代码/列表形式给出 **配置命名模板** `{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{schedule}_{dataset}`，并以项目符号列举每个占位符的取值示例，但并未以 markdown 表格形式呈现，因此不构成可"逐字还原"的表格。

---

## 【公式解读】
**原文无公式**（无 LaTeX 公式、无伪代码形式的公式定义）。

---

## 【关联】
**内部链接**：原文未在文末给出内部链接，标注 `(无)`。

**外部 / 隐含关联**：
- 详细继承/插值语法指向外部 `mmcv` 文档：`https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html`
- backbone 可选项指向 `mmseg/backbone/resnet.py`。
- decode_head / auxiliary_head 可选项指向 `mmseg/models/decode_heads`。
- dataset 可选项指向 `mmseg/datasets/`。
- 预训练权重加载源 `pretrained='open-mmlab://resnet50_v1c'` 关联到 open-mmlab 权重体系。
- 与同方法族配置的关系：通过 `_base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py` 进行跨方法继承，文档暗示同一仓库下还存放 PSPNet、DeepLabV3 的同族配置以供复用。
- 与"教程系列"上下游关系：本篇为 Tutorial 1，预计后续教程将进一步涉及调度器、数据集自定义、模型自定义等模块，构成多教程的学习链路（原文未列链接，仅在标题"教程 1"中体现顺序）。

---

## 【使用方法】
1. **查看 / 打印配置**  
   ```bash
   python tools/print_config.py /PATH/TO/CONFIG
   python tools/print_config.py /PATH/TO/CONFIG --options xxx.yyy=zzz
   ```
2. **继承已有配置（推荐起步方式）**  
   在新配置文件首行声明：
   ```python
   _base_ = '../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py'
   ```
3. **建立全新模型配置**  
   在 `configs/` 下新增独立子目录 `xxxnet/`，并在该目录中放 1 份 primitive 配置，其余通过 `_base_` 继承。
4. **典型键位置（来自 PSPNet 示例，便于定位修改点）**  
   - 模型：`model.type`、`model.backbone.*`、`model.decode_head.*`、`model.auxiliary_head.*`
   - 数据：`data.samples_per_gpu`、`data.workers_per_gpu`、`data.train.pipeline`、`data.val.pipeline`、`data.test.pipeline`
   - 归一化：`img_norm_cfg.mean / std / to_rgb`
   - 训练：`train_cfg`（当前仅占位符）、`test_cfg.mode`（`'whole'` 或 `'sliding'`）
5. **未涉及**（原文未给出）：具体训练启动命令、resume/checkpoint 路径字段、optimizer/lr_config 配置写法（这些 `_base_/schedule_*` 组件未在本文示例中展开）。
```

> 备注：用户提供的原文末尾在 `test=dict(` 处被截断（缺右括号与尾部若干字段），因此以上解读严格限定在已给出的字段范围内，未对截断之后的内容做臆测补全。
