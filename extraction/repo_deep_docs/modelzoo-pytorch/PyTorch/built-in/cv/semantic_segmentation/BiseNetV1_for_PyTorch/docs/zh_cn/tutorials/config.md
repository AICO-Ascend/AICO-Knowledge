# 教程 1: 学习配置文件

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/config.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/zh_cn/tutorials/config.md

```markdown
# 一体化深度解读:教程 1 — 学习配置文件

---

## 【定位】
本文档面向使用 mmseg 风格语义分割框架(对应本仓库 BiseNetV1_for_PyTorch 等模型)的使用者/社区贡献者,系统讲解**配置文件的结构组织、命名规范、继承机制**,并以 ResNet50V1c+PSPNet 为完整范例逐字段注释,使读者能够看懂、复用、修改和派生配置文件。

---

## 【技术要点】

1. **配置即 Python 文件,可通过打印工具查看**:执行 `python tools/print_config.py /PATH/TO/CONFIG` 输出完整配置;追加 `--cfg-options xxx.yyy=zzz` 可在打印时验证覆写效果。
2. **四类基础组件构成 `_base_`**:在 `config/_base_/` 下包含 *数据集 (dataset)、模型 (model)、训练策略 (schedule)、运行时默认设置 (default runtime)* 四种组件,通过组合即可派生 DeepLabV3、PSPNet 等模型;由 `_base_` 组件构成的配置称为**原始配置 (primitive)**。
3. **继承深度上限为 3,推荐单一原始配置**:同一文件夹下推荐**仅有一个原始配置**,其他配置继承自它;社区贡献者应继承已有方法(如通过 `_base_ = ../deeplabv3/deeplabv3_r50_512x1024_40ki_cityscapes.py`)再做局部修改;完全新模型需在 `configs/` 下新建 `xxxnet` 文件夹。
4. **命名模板强制规范**:`{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}`,`{xxx}` 必选,`[yyy]` 可选;默认批大小记作 `8x2`;迭代数示例 `160k`。
5. **分割头默认使用 SyncBN + CrossEntropyLoss**:PSPNet 全注释示例明确 `norm_cfg = dict(type='SyncBN', requires_grad=True)`;解码头与辅助头损失皆为 `CrossEntropyLoss`,`use_sigmoid=False`,解码头 `loss_weight=1.0`、辅助头 `loss_weight=0.4`。
6. **数据增广流程 (train_pipeline) 顺序固定**:LoadImageFromFile → LoadAnnotations → Resize(img_scale=(2048,1024), ratio_range=(0.5,2.0)) → RandomCrop(crop_size=(512,1024), cat_max_ratio=0.75) → RandomFlip(0.5) → PhotoMetricDistortion → Normalize → Pad(pad_val=0, seg_pad_val=255) → DefaultFormatBundle → Collect(keys=['img','gt_semantic_seg'])。

---

## 【关键机制与数据】

- **配置即模块化继承**:基于 Python `_base_` 字段实现多文件组合,这是把数据集/模型/调度/运行时解耦的关键设计,使得修改某一维度(如换 backbone 或数据集)时不需要重写其余配置。
- **数据流 (Data flow,以 PSPNet 训练为例)**:
  1. `data['train']['pipeline']` 调用 `train_pipeline`,从文件加载图像 (`LoadImageFromFile`) 与标注 (`LoadAnnotations`);
  2. 通过 `Resize`(最大边 2048×1024, 比例 0.5–2.0)、`RandomCrop`(512×1024, 单类填充上限 0.75)、`RandomFlip`(概率 0.5)、`PhotoMetricDistortion` 做空间与光度增强;
  3. 用 ImageNet 预训练均值 `mean=[123.675, 116.28, 103.53]` 与标准差 `std=[58.395, 57.12, 57.375]` 做归一化 (`to_rgb=True`);
  4. `Pad` 到 `(512, 1024)`,图像填 `0`、语义标注填 `255`(ignore 索引);`DefaultFormatBundle` + `Collect` 只把 `img` 与 `gt_semantic_seg` 喂入分割器。
- **批大小与并行度**:`samples_per_gpu=2`,`workers_per_gpu=2`;命名中默认 `8x2` 即 8 卡 × 每卡 2 样本。
- **测试模式**:`test_cfg = dict(mode='whole')`,可选 `'whole'`(全卷积整图推理)与 `'sliding'`(滑窗裁剪);`MultiScaleFlipAug` 封装多尺度+翻转测试增强,本例 `flip=False`、`keep_ratio=True`。
- **数据集路径**:`data_root='data/cityscapes/'`,`img_dir='leftImg8bit/{train,val}'`,`ann_dir='gtFine/{train,val}'`;验证与测试使用同一 val 划分。
- **类别数对照 (原文给出)**:`cityscapes`=19,`VOC`=21,`ADE20k`=150。
- **性能数据**:原文未提供任何吞吐/精度数字,故无性能基准可引用。
- **关于公式与性能指标**:原文无任何训练曲线、mIoU、fps 数值。

---

## 【表格解读】

**原文无表格**。原文中唯一形似表格的内容是命名模板,以代码块形式给出:

```
{model}_{backbone}_[misc]_[gpu x batch_per_gpu]_{resolution}_{iterations}_{dataset}
```

为便于阅读,按原文条目**逐字还原**如下:

| 字段 | 是否必选 | 含义 | 原文示例 |
|---|---|---|---|
| `{model}` | 必选 | 模型种类 | `psp`, `deeplabv3` |
| `{backbone}` | 必选 | 主干网络种类 | `r50`(ResNet-50), `x101`(ResNeXt-101) |
| `[misc]` | 可选 | 各种设置/插件 | `dconv`, `gcb`, `attention`, `mstrain` |
| `[gpu x batch_per_gpu]` | 可选 | GPU 数 × 每 GPU 样本数 | 默认 `8x2` |
| `{resolution}` | 必选 | 训练分辨率 | `(512, 1024)` |
| `{iterations}` | 必选 | 训练迭代轮数 | `160k`, 文中另出现 `40ki`(deeplabv3 路径示例) |
| `{dataset}` | 必选 | 数据集名称 | `cityscapes`, `voc12aug`, `ade` |

> 注:原文中 `40ki` 出现于 `_base_` 路径示例 `deeplabv3_r50_512x1024_40ki_cityscapes.py`,以"ki"后缀表达 40k 迭代;此表中"原文示例"列已逐字摘录。

---

## 【公式解读】

**原文无公式**。文档中出现的仅是 Python 字面量(dilations、strides、pool_scales、crop_size 等**元组**配置),而非数学公式。若需将 PSPHead 配置中的池化尺度视为参数,可读为 `pool_scales=(1, 2, 3, 6)`,表示 PSP 模块四个分支的**平均池化窗口大小**(对应原文注释"PSPHead 平均池化(avg pooling)的规模(scales)")。ResNet 主干中 `dilations=(1, 1, 2, 4)` 与 `strides=(1, 2, 1, 1)` 描述四个 stage 的膨胀率与步长,**这些是配置常量,无数学运算表达式**。

---

## 【关联】

- **上游/工具链**:`tools/print_config.py`(配置查看入口)、`--cfg-options xxx.yyy=zzz`(运行时覆写);二者皆依赖 mmcv 的配置系统,文档明确将更深入的实现细节指向 [mmcv config 文档](https://mmcv.readthedocs.io/en/latest/understand_mmcv/config.html)。
- **同级模块(以 PSPNet 配置为例)**:
  - `mmseg/models/backbones/resnet.py` — 提供 `ResNetV1c` 主干类。
  - `mmseg/models/decode_heads` — 提供 `PSPHead` 与 `FCNHead`(`auxiliary_head`)。
  - `mmseg/datasets/` — 提供 `CityscapesDataset`。
- **兄弟模型/派生关系**:文档以 DeepLabV3 与 PSPNet 为代表,说明通过 `_base_` 组合可生成大量分割模型;对于 BiseNetV1,本文档属于该生态通用约定,**与本文路径 `BiseNetV1_for_PyTorch` 同属 mmseg 配置体系**,实际 BiseNetV1 配置应使用其 `decode_head=BiSeNetV1Head` 等替换 PSPHead 字段,其余 `_base_` 继承结构保持一致。
- **预训练权重**:`pretrained='open-mmlab://resnet50_v1c'` 指向 open-mmlab 维护的 ResNet-50 v1c 预训练,归一化参数 `mean/std` 与 `to_rgb` 必须与之对齐,否则骨干特征分布失配。

---

## 【使用方法】

1. **查看完整配置**:
   ```bash
   python tools/print_config.py /PATH/TO/CONFIG
   ```
   追加 `--cfg-options xxx.yyy=zzz` 可即时打印覆写后的最终配置。

2. **继承已有配置(派生写法)**:
   ```python
   _base_ = ['../_base_/models/pspnet_r50.py',
             '../_base_/datasets/cityscapes.py',
             '../_base_/default_runtime.py',
             '../_base_/schedules/schedule_40ki.py']
   # 再覆写自己想改的字段
   ```

3. **关键可配置项 (取自 PSPNet 示例)**:
   - 主干:`type='ResNetV1c'`、`depth=50`、`num_stages=4`、`out_indices=(0,1,2,3)`、`dilations=(1,1,2,4)`、`strides=(1,2,1,1)`、`contract_dilation=True`、`style='pytorch'`。
   - 解码头:`type='PSPHead'`、`in_channels=2048`、`in_index=3`、`channels=512`、`pool_scales=(1,2,3,6)`、`dropout_ratio=0.1`、`num_classes=19`、`align_corners=False`。
   - 辅助头:`type='FCNHead'`、`in_channels=1024`、`in_index=2`、`channels=256`、`num_convs=1`、`loss_weight=0.4`(默认)。
   - 归一化:`mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]`、`to_rgb=True`。
   - 训练:`crop_size=(512, 1024)`、`samples_per_gpu=2`、`workers_per_gpu=2`。
   - 测试:`test_cfg=dict(mode='whole')`,可选 `'sliding'`。

4. **使用约定**(原文涉及):新模型无任何已有方法可继承时,在 `configs/` 下新建 `xxxnet` 目录并放入**唯一一份原始配置**,其余配置基于 `_base_` 继承;继承深度不超过 3 层。

> 备注:原文末尾的 `test=dict(...)` 代码块被截断,故 `test` 字段完整内容**原文未给出**,此处不臆补。
```
