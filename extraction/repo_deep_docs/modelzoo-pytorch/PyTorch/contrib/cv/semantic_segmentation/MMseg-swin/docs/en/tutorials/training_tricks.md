# Tutorial 5: Training Tricks

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/training_tricks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/tutorials/training_tricks.md

# 一体化深度解读:Tutorial 5: Training Tricks

---

## 【定位】

这篇文档解决的是 **MMSegmentation 框架开箱即用 (out of box) 的训练技巧配置问题**,描述了在语义分割模型训练过程中,通过配置项 (Python config) 即可启用的 5 类常用训练增强/调优手段——涵盖差异化学习率、难例挖掘、类别平衡损失、多损失联合训练与忽略标签。

---

## 【技术要点】

1. **骨干与头部的差异化学习率**:通过 `optimizer.paramwise_cfg.custom_keys` 让名称含 `'head'` 的参数组的学习率乘以 `lr_mult=10.`,即头部 LR 是骨干的 10 倍。
2. **在线难例挖掘 (OHEM)**:在 `decode_head` 中配置 `sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)`——置信度低于 0.7 的像素参与训练,至少保留 100000 像素;若不指定 `thresh`,则按 loss 取 top `min_kept`。
3. **类别平衡损失**:在 `CrossEntropyLoss` 中传入 `class_weight` 列表,作为 `weight` 参数生效(以 Cityscapes 19 类权重为例)。
4. **多损失联合训练**:在 `loss_decode` 中传入 list 形式的多个损失,以 `loss_name` + `loss_weight` 同时记录日志;UNet/DRIVE 示例为 `CrossEntropyLoss` (权重 1.0) + `DiceLoss` (权重 3.0) 的 1:3 加权,主头与辅助头并行使用。
5. **忽略指定标签**:`avg_non_ignore=True` 时损失只在非忽略标签像素上求平均;配合 `ignore_index=0` 可让背景(标签 0)不参与损失计算与平均。
6. **日志前缀约束 (隐含规则)**:`loss_name` 要进入反向传播图必须以 `loss_` 为前缀。

---

## 【关键机制与数据】

### 1. 差异化 LR 的工作原理
- 原文:`With this modification, the LR of any parameter group with 'head' in name will be multiplied by 10.`
- 机制:依赖 MMCV 的 `DefaultOptimizerConstructor`,按参数名 (子串 `'head'`) 匹配并施加 `lr_mult`,无需修改优化器源代码。

### 2. OHEM 像素采样器的工作原理
- 原文:`only pixels with confidence score under 0.7 are used to train. And we keep at least 100000 pixels during training. If thresh is not specified, pixels of top min_kept loss will be selected.`
- 实现位置:`mmseg/core/seg/sampler`(以 GitHub URL 形式给出)。
- 双模式:有 `thresh` → 置信度阈值筛选;无 `thresh` → top-`min_kept` loss 筛选。

### 3. Class Balanced Loss 的数据流
- 原文:`class_weight will be passed into CrossEntropyLoss as weight argument.`
- 数据 (原文):针对 Cityscapes 19 类,权重列表为
  `[0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754, 1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037, 1.0865, 1.0955, 1.0865, 1.1529, 1.0507]`,注释指出该权重为 DeepLab 在 Cityscapes 上使用的值。

### 4. 多损失并行机制
- 原文:`loss_weight and loss_name will be weight and name in training log of corresponding loss, respectively.`
- 原文:UNet/DRIVE 的具体比例为 `1:3` (CrossEntropyLoss : DiceLoss),主头 (`decode_head`) 与辅助头 (`auxiliary_head`) 同时配置相同的多损失结构。

### 5. 忽略标签机制
- 原文:`In default setting, avg_non_ignore=False which means each pixel counts for loss calculation although some of them belong to ignore-index labels.`
- 原文:`the average loss would only be calculated in non-ignored labels which may achieve better performance`
- 关联 PR (原文):`https://github.com/open-mmlab/mmsegmentation/pull/1409`

---

## 【表格解读】

**原文无表格**。

> 备注:文档中存在配置代码块 (见下"公式解读"节),但属于 Python 配置伪代码而非 markdown 表格。

---

## 【公式解读】

原文无 LaTeX 数学公式,但包含 **4 个 Python 配置伪代码片段**,逐字保留并解读如下:

### 伪代码 ①:差异化 LR

```python
optimizer=dict(
    paramwise_cfg = dict(
        custom_keys={
            'head': dict(lr_mult=10.)}))
```

- `optimizer`:外层字典,被 MMSegmentation 配置系统直接传给优化器构造器。
- `paramwise_cfg`:MMCV `DefaultOptimizerConstructor` 的"按参数分组"配置。
- `custom_keys`:以参数名字串为 key 的字典,声明匹配规则。
- `'head'`:子串匹配,只要参数名中出现 `'head'` 即可命中(骨干通常名为 `backbone`,因此不会被误匹配)。
- `lr_mult=10.`:学习率乘子,实际学习率 = `base_lr * lr_mult`。

### 伪代码 ②:OHEM 像素采样器

```python
_base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'
model=dict(
    decode_head=dict(
        sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)) )
```

- `_base_`:配置继承自 PSPNet/R50/D8/512×1024/40k iters 的 Cityscapes 基础配置。
- `model.decode_head.sampler`:为解码头注入像素级采样器。
- `type='OHEMPixelSampler'`:采样器类名。
- `thresh=0.7`:置信度阈值,低于此值的像素视为难例被采样。
- `min_kept=100000`:最小保留像素数下限,防止训练时有效像素过少。

### 伪代码 ③:类别平衡损失

```python
_base_ = './pspnet_r50-d8_512x1024_40k_cityscapes.py'
model=dict(
    decode_head=dict(
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0,
            # DeepLab used this class weight for cityscapes
            class_weight=[0.8373, 0.9180, 0.8660, 1.0345, 1.0166, 0.9969, 0.9754,
                        1.0489, 0.8786, 1.0023, 0.9539, 0.9843, 1.1116, 0.9037,
                        1.0865, 1.0955, 1.0865, 1.1529, 1.0507])))
```

- `type='CrossEntropyLoss'`:损失类型。
- `use_sigmoid=False`:语义分割多为多类,不经 sigmoid 直接做 CE。
- `loss_weight=1.0`:该损失在整体目标中的权重系数。
- `class_weight=[...19 个数...]`:逐类权重,与 Cityscapes 的 19 个类别一一对应,直接透传至 `CrossEntropyLoss(weight=...)`。

### 伪代码 ④:多损失联合 (UNet/DRIVE, 1:3)

```python
_base_ = './fcn_unet_s5-d16_64x64_40k_drive.py'
model = dict(
    decode_head=dict(loss_decode=[dict(type='CrossEntropyLoss', loss_name='loss_ce', loss_weight=1.0),
            dict(type='DiceLoss', loss_name='loss_dice', loss_weight=3.0)]),
    auxiliary_head=dict(loss_decode=[dict(type='CrossEntropyLoss', loss_name='loss_ce',loss_weight=1.0),
            dict(type='DiceLoss', loss_name='loss_dice', loss_weight=3.0)]),
    )
```

- `loss_decode=[...]`:由"单一损失 dict"升级为"损失 dict 列表",触发多损失并行计算。
- `loss_name='loss_ce'` / `'loss_dice'`:日志中显示的损失名;**同时**也是参与反向传播的键名,必须以 `loss_` 为前缀(原文 Note 约束)。
- `loss_weight=1.0` 与 `loss_weight=3.0`:两个损失按 1:3 加权求和。
- `decode_head` 与 `auxiliary_head` 同时设置相同的多损失结构,体现"主头+辅助头"联合监督的范式。

### 伪代码 ⑤:忽略指定标签 (UNet/Cityscapes, 忽略 label 0)

```python
_base_ = './fcn_unet_s5-d16_4x4_512x1024_160k_cityscapes.py'
model = dict(
    decode_head=dict(
        ignore_index=0,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0, avg_non_ignore=True),
    auxiliary_head=dict(
        ignore_index=0,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0, avg_non_ignore=True)),
    ))
```

- `ignore_index=0`:将真实标签为 0 的像素标记为"忽略"。
- `avg_non_ignore=True`:平均损失时只对非忽略像素求平均(即分母排除忽略像素)。
- 主头/辅助头均同步设置,确保两路监督行为一致。

---

## 【关联】

文末内部链接字段标注为 **"无"**。然而原文正文嵌入了若干**外部参考链接**,可视为本文档与上下游模块的关联关系:

- **`mmcv.runner.DefaultOptimizerConstructor`**(MMCV 文档):差异化 LR 机制(`paramwise_cfg.custom_keys`)的实际承载者,文档中所有"按参数名分组施加 LR 倍率"的能力均来自 MMCV,而非 MMSegmentation 自研。
- **`mmseg/core/seg/sampler`**(MMSegmentation 代码库路径):OHEM 像素采样器的实现位置,说明该训练技巧由 MMSegmentation 自身提供,而非依赖外部库。
- **PyTorch `torch.nn.CrossEntropyLoss`**(PyTorch 文档):`class_weight` 的最终落地对象,说明类别平衡损失仅是 PyTorch 原生 `weight` 参数的封装,未引入新数学。
- **PR #1409**(MMSegmentation 仓库):`avg_non_ignore` 与 `ignore_index` 联合机制的引入 PR,表明该特性是后续增量添加,而非最初版本所具备。
- **基础配置基线**(`_base_` 字段):文档中所有示例均通过 `_base_` 继承自具体模型配置文件,如 `pspnet_r50-d8_512x1024_40k_cityscapes.py`、`fcn_unet_s5-d16_64x64_40k_drive.py`、`fcn_unet_s5-d16_4x4_512x1024_160k_cityscapes.py`,说明训练技巧是与"具体模型 + 数据集 + 调度"配置解耦的横向模块。

---

## 【使用方法】

原文均为**配置式启用**,无独立 CLI 命令,核心启用方式如下:

1. **差异化 LR**:在自定义 config 的 `optimizer` 块中加入 `paramwise_cfg.custom_keys={'head': dict(lr_mult=10.)}`,然后用 `tools/train.py ${CONFIG_FILE}` 启动训练(原文未给出 train 命令,按 MMSegmentation 通用做法推断)。
2. **OHEM**:在 `model.decode_head` 下新增 `sampler=dict(type='OHEMPixelSampler', thresh=0.7, min_kept=100000)`(可省略 `thresh` 切换为 top-loss 模式)。
3. **类别平衡损失**:在 `model.decode_head.loss_decode` 中把 `type` 设为 `CrossEntropyLoss` 并提供与类别数等长的 `class_weight` 列表。
4. **多损失联合**:将 `loss_decode` 由单一 dict 改为 dict 列表,每个元素含 `type` / `loss_name`(必须以 `loss_` 为前缀)/ `loss_weight`,主头与辅助头需分别配置。
6. **忽略标签**:在 `decode_head` 与 `auxiliary_head` 同时设置 `ignore_index=<待忽略标签值>` 与 `loss_decode=dict(..., avg_non_ignore=True)`,默认 `avg_non_ignore=False`。

> **命令行/启动脚本**:`原文未涉及` 具体的 `tools/train.py` 启动命令或 shell 片段,所有示例均以 Python config 形式呈现。
