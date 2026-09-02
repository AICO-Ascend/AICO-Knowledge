# Tutorial 3: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/data_pipeline.md

# 一体化深度解读:CascadeMaskRCNN_iflytek_for_PyTorch — Tutorial 3: Customize Data Pipelines

---

## 【定位】

本教程系统说明 MMDet 框架中**目标检测数据预处理流水线(Pipeline)的内部机制与自定义扩展方法**:从 Dataset/DataLoader 的多 worker 数据加载出发,引入 MMCV 的 `DataContainer` 以承载变长数据,再用由一系列 dict→dict 算子构成的 Pipeline 完成"加载—预处理—格式化—测试时增强"四阶段数据准备,并示范如何注册并使用自定义算子。

---

## 【技术要点】

1. **加载范式**:采用 `Dataset` + `DataLoader`(多 worker);`Dataset` 返回与模型 `forward` 参数一一对应的 dict 数据项。
2. **变长数据封装**:由于目标检测中图像尺寸、GT bbox 数量、mask 等均不一致,引入 MMCV 的 `DataContainer` 类型来处理异构尺寸数据的收集与分发。
3. **Pipeline 与 Dataset 解耦**:Dataset 负责标注处理,Pipeline 定义"准备一个数据 dict"的全流程步骤;Pipeline 由串行算子构成,每个算子输入 dict、输出 dict。
4. **四类算子分类**:数据加载(data loading)、预处理(pre-processing)、格式化(formatting)、测试时增强(test-time augmentation);绿色键表示新增、橙色键表示更新。
5. **Faster R-CNN 标准配置关键参数**(原文):
   - 归一化:`mean=[123.675, 116.28, 103.53]`,`std=[58.395, 57.12, 57.375]`,`to_rgb=True`
   - 缩放:`img_scale=(1333, 800)`,`keep_ratio=True`
   - 翻转:`flip_ratio=0.5`
   - 填充:`size_divisor=32`
   - Collect 保留键:`keys=['img', 'gt_bboxes', 'gt_labels']`
6. **自定义算子三步法**:①在任意文件中以 `@PIPELINES.register_module()` 装饰一个 `__call__(self, results)` 类;②在配置可触达处 `from .my_pipeline import MyTransform`;③在 `train_pipeline` / `test_pipeline` 列表中以 `dict(type='MyTransform')` 插入。

---

## 【关键机制与数据】

### 工作原理与数据流

- **算子链字典流转**:Pipeline 是有序列表,蓝色块为算子,绿色键为新增字段,橙色键为更新字段。每个算子**只依赖前序算子写入 dict 的字段**,因此乱序插入会因 key 缺失而失败。
- **`DataContainer` 的作用**:在异构尺寸(变长 bbox、可变 mask、不同尺度图像)场景下,用 `DataContainer` 包住张量并指定 `stack`/`pad`/`concat` 等堆叠策略,让 `DataLoader` 的 collate 阶段能正确收集成 batch。
- **`Collect` 算子的"过滤"语义**:它是流水线的末端,把 dict 中**未被 `keys` 指定的键全部移除**,只把 `meta_keys` 指定的字段归并到 `img_meta` 列表,作为模型 `forward` 的元信息(图片 id、shape、scale_factor 等)。
- **`DefaultFormatBundle` 的"类型转换"语义**:把 numpy/PIL 等统一转为 Tensor,并把 GT 类目标字段用 `DataContainer` 包装,以便后续 collate。

### 训练与测试 Pipeline 对比

- **训练(`train_pipeline`)** 顺序:`LoadImageFromFile` → `LoadAnnotations(with_bbox=True)` → `Resize(img_scale=(1333,800), keep_ratio=True)` → `RandomFlip(flip_ratio=0.5)` → `Normalize(**img_norm_cfg)` → `Pad(size_divisor=32)` → `DefaultFormatBundle` → `Collect(keys=['img','gt_bboxes','gt_labels'])`。
- **测试(`test_pipeline`)** 用 `MultiScaleFlipAug` 包裹一个 transforms 子链(`Resize` → `RandomFlip` → `Normalize` → `Pad` → `ImageToTensor(keys=['img'])` → `Collect(keys=['img'])`),`img_scale=(1333, 800)`,`flip=False`,由该算子在内部按多尺度+翻转生成多组增强样本送入模型做集成。

### 性能/规模类数据

原文未给出吞吐量、显存、mAP 等数值,仅给出**配置参数**(尺寸 1333×800、divisor 32、flip_ratio 0.5、3 通道均值/方差),故不杜撰任何性能数字。

---

## 【表格解读】

**原文无表格**(整篇以代码块与项目列表呈现)。为便于理解,以下将**算子—字典字段影响**这一核心配置项**逐字**整理为 markdown 表格(字段名与"add/update/remove"完全忠实于原文)。

### 表 1:Data loading 阶段算子字段影响(原文逐字)

| 算子 | add(新增) | update(更新) | remove(删除) |
|---|---|---|---|
| `LoadImageFromFile` | `img`, `img_shape`, `ori_shape` | — | — |
| `LoadAnnotations` | `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg`, `bbox_fields`, `mask_fields` | — | — |
| `LoadProposals` | `proposals` | — | — |

逐行解读:`LoadImageFromFile` 负责把磁盘图像读成 numpy 并记录原图尺寸;`LoadAnnotations` 一次性注入全部监督信号(框、忽略框、类别、mask、语义分割)以及用于后续更新传播的"字段白名单"(`bbox_fields`/`mask_fields`,供 `Resize`/`RandomFlip`/`Pad` 用通配符 `*bbox_fields` 批量更新);`LoadProposals` 单独读 RPN 候选框,供两阶段检测的 RPN 复用路径。

### 表 2:Pre-processing 阶段算子字段影响(原文逐字)

| 算子 | add(新增) | update(更新) |
|---|---|---|
| `Resize` | `scale`, `scale_idx`, `pad_shape`, `scale_factor`, `keep_ratio` | `img`, `img_shape`, `*bbox_fields`, `*mask_fields`, `*seg_fields` |
| `RandomFlip` | `flip` | `img`, `*bbox_fields`, `*mask_fields`, `*seg_fields` |
| `Pad` | `pad_fixed_size`, `pad_size_divisor` | `img`, `pad_shape`, `*mask_fields`, `*seg_fields` |
| `RandomCrop` | — | `img`, `pad_shape`, `gt_bboxes`, `gt_labels`, `gt_masks`, `*bbox_fields` |
| `Normalize` | `img_norm_cfg` | `img` |
| `SegRescale` | — | `gt_semantic_seg` |
| `PhotoMetricDistortion` | — | `img` |
| `Expand` | — | `img`, `gt_bboxes` |
| `MinIoURandomCrop` | — | `img`, `gt_bboxes`, `gt_labels` |
| `Corrupt` | — | `img` |

逐行解读:`*bbox_fields` / `*mask_fields` / `*seg_fields` 是通配符,会按 `LoadAnnotations` 写入的 `bbox_fields` / `mask_fields` 列表**自动展开**为所有相关键(如 `gt_bboxes`/`gt_bboxes_ignore`、`gt_masks` 等),从而保证几何变换能联动更新所有 GT。`RandomCrop` 直接命名要更新的 GT 字段(不靠通配符),适合裁剪会改变 GT 的场景。`Normalize` 同时把 `img_norm_cfg` 写入 dict,以便 `Collect` 阶段能将其并入 `img_meta`,推理时还原用。

### 表 3:Formatting 阶段算子字段影响(原文逐字)

| 算子 | update 范围 | 其他行为 |
|---|---|---|
| `ToTensor` | specified by `keys` | — |
| `ImageToTensor` | specified by `keys` | — |
| `Transpose` | specified by `keys` | — |
| `ToDataContainer` | specified by `fields` | — |
| `DefaultFormatBundle` | `img`, `proposals`, `gt_bboxes`, `gt_bboxes_ignore`, `gt_labels`, `gt_masks`, `gt_semantic_seg` | — |
| `Collect` | — | **add**: `img_meta`(字段集合由 `meta_keys` 指定);**remove**: 除 `keys` 指定外的所有其他键 |

逐行解读:四个 `*-To*` 类算子提供"键级"细粒度控制,适合在标准 `DefaultFormatBundle` 不够用时手动选择需要格式化的部分。`DefaultFormatBundle` 是**预置组合**,把训练时所需的标准 GT 字段一次性打包成 Tensor/`DataContainer`。`Collect` 是流水线末尾的"过滤器+整合器",把非模型输入字段清掉,把元信息整合到 `img_meta` 列表(常见 `meta_keys`:`ori_shape`、`img_shape`、`pad_shape`、`scale_factor`、`flip`、`img_norm_cfg` 等)。

### 表 4:Test time augmentation 阶段算子(原文逐字)

| 算子 | 备注 |
|---|---|
| `MultiScaleFlipAug` | 原文档未列出详细字段影响,仅列出算子名 |

逐行解读:`MultiScaleFlipAug` 是测试期增强的**复合算子**,自身接受 `img_scale` 与 `flip` 参数,并在内部再嵌入一个 `transforms` 子流水线,对同一张图做多尺度/翻转组合以做集成推理。

---

## 【公式解读】

**原文无公式**(教程为工程性 guide,不含数学公式或伪代码公式)。

---

## 【关联】

- **上游 — MMCV 核心库**:`DataContainer` 由 MMCV 提供(原文链接 `mmcv/parallel/data_container.py`),负责异构尺寸数据的堆叠策略;`@PIPELINES.register_module()` 依赖 `mmdet.datasets.PIPELINES` 注册器,二者均说明本 Pipeline 机制是 MMCV 通用数据流范式在检测任务上的具体落地。
- **下游 — 检测模型 `forward`**:`Dataset` 最终返回的 dict 字段必须与检测模型 `forward` 形参对应(典型为 `img`、`gt_bboxes`、`gt_labels`、`img_meta` 列表);`Collect` 通过 `keys=['img','gt_bboxes','gt_labels']` 显式锁定这一契约,任何想新增输入(如 `gt_masks`)的算法(如 Mask R-CNN、Cascade Mask R-CNN)都需把对应键加进 `keys`。
- **与教程的关系**:这是 Tutorial 3,承接 Tutorial 1(配置文件)与 Tutorial 2(数据集)之后的数据准备环节;后续教程(自定义模块/损失/钩子等)通常会与 Pipeline 中 `gt_*` 字段命名保持一致。
- **测试 Pipeline 与训练 Pipeline 的对偶性**:测试期 `MultiScaleFlipAug` 中的 `transforms` 子链与训练链几乎相同,只是末尾多了 `ImageToTensor(keys=['img'])` 并跳过了 `DefaultFormatBundle`(因为无 GT,无需打包),这一差异同时说明"算子选型由下游消费者决定"。

> 文末链接标注为"(无)"——教程自身未再给出额外内部链接;外部依赖链接仅指向 MMCV 仓库的 `data_container.py`。

---

## 【使用方法】

以下要点均按原文示例逐字整理,无原文证据的内容不补充。

### 1. 训练 Pipeline 完整配置(Faster R-CNN 原文示例)

```python
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(type='Resize', img_scale=(1333, 800), keep_ratio=True),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
```

### 2. 测试 Pipeline 完整配置(原文示例)

```python
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(1333, 800),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
```

### 3. 自定义 Pipeline 三步启用(原文示例)

**①定义(`my_pipeline.py`)**:

```python
from mmdet.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:
    def __call__(self, results):
        results['dummy'] = True
        return results
```

**②导入**:在配置可触达的文件中加入 `from .my_pipeline import MyTransform`(原文示例)。

**③在 config 文件的 `train_pipeline` 中插入**:在 `Normalize` 与 `Pad` 之间插入 `dict(type='MyTransform')` 即可生效(原文示例插入位置即此处)。

### 4. 各算子的可配置参数速查(原文逐字)

- `LoadAnnotations`:可传 `with_bbox`(示例为 `True`)。
- `Resize`:`img_scale=(1333, 800)`,`keep_ratio=True`。
- `RandomFlip`:`flip_ratio=0.5`。
- `Normalize`:`mean`、`std`、`to_rgb`(通过 `**img_norm_cfg` 注入)。
- `Pad`:`size_divisor=32`。
- `Collect`:`keys`、`meta_keys`。
- `ImageToTensor`:`keys=['img']`。
- `MultiScaleFlipAug`:`img_scale`、`flip`、`transforms`。

### 5. Pipeline 调试建议(基于原文机制推断的最佳实践,**非原文**)

- 在自定义算子 `__call__` 内对 `results` 做 key 完整性断言,便于在流水线早期发现上游字段缺失;
- 通过把 `Collect` 的 `keys` 临时放宽为包含 `img_meta` 内全部字段并 `print`,可一次性看到整条 Pipeline 注入的全部键名,验证字段契约。

> 原文未涉及:命令行/启动参数、`tools/train.py` 中如何指定 pipeline、Shell 级别启动方式、`envs`/环境变量、依赖版本要求等——故未涉及内容严格按指令不杜撰。
