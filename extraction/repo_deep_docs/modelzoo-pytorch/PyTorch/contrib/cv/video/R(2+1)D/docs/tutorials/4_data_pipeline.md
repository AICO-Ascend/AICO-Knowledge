# Tutorial 4: Customize Data Pipelines

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/4_data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/4_data_pipeline.md

# R(2+1)D / MMAction 数据管线教程深度解读

## 【定位】

本教程（MMAction 框架 Tutorial 4）解决**动作识别/时序动作定位任务中"如何设计、扩展自定义数据预处理流水线"**的问题，描述在 MMAction 中通过一串"以 dict 为输入输出"的操作（pipeline operations）将原始视频/帧数据加工为模型 forward 所需样本的完整能力。

---

## 【技术要点】

1. **数据加载与处理分离**：使用 PyTorch 的 `Dataset`/`DataLoader` 多 worker 加载；`Dataset` 返回 dict，字段对齐模型 forward 参数；不同样本尺寸（图像、gt bbox 等）的差异通过 MMCV 的 `DataContainer` 收集分发。
2. **Pipeline = 操作序列**：每个操作接收 dict、输出 dict，可"新增 key（绿色）"或"更新已有 key（橙色）"；按职责划分为 **data loading / pre-processing / formatting** 三类。
3. **TSN 标准三套 pipeline**：train 用 `MultiScaleCrop` + `Flip` + `Normalize`；val 用 `CenterCrop`；test 用 `TenCrop`，分别取 `num_clips=3/3/25`，归一化参数固定 `mean=[123.675,116.28,103.53]`, `std=[58.395,57.12,57.375]`, `to_bgr=False`。
4. **Lazy operations + `Fuse` 加速机制**：lazy 操作只记录"如何处理"（如 `Resize`/`MultiScaleCrop`/`Resize`/`Flip`），不去反复读写原始数据，最终由 `Fuse` 一次性把修改落到原始数据上，从而加速预处理（典型配置 `clip_len=32, frame_interval=2, num_clips=1, scales=(1, 0.8), max_wh_scale_gap=0`）。
5. **操作对 dict 字段的精确影响声明**：每个操作都标注 add / update / remove 的字段及 `*`（可能不影响），`Collect` 阶段保留指定 `keys`、把其余塞入 `img_metas`，且第一个 key（通常 `imgs`）决定 batch size。
6. **自定义 pipeline 注册三步法**：写一个 `__call__(self, results)` 类、用 `@PIPELINES.register_module()` 注册、import 后即可在 config 中以 `dict(type='MyTransform')` 调用。

---

## 【关键机制与数据】

**Pipeline 数据流原理（原文）：** "a pipeline consists of a sequence of operations. Each operation takes a dict as input and also output a dict for the next operation." 蓝色块为操作、绿色为新增字段、橙色为更新字段。`*` 标记的 key 表示该操作"may not be affected"（即不一定被改）。

**Lazy op 工作原理（原文）：** "Lazy ops record how the data should be processed, but it will postpone the processing on the raw data until the raw data forward `Fuse` stage. Specifically, lazy ops avoid frequent reading and modification operation on the raw data, but process the raw data once in the final Fuse stage, thus accelerating data preprocessing." 例如 lazy `Resize`/`MultiScaleCrop`/`Flip` 只处理 bbox 与翻转标志位，等 `Fuse` 时一次性作用到原始帧。

**关键数值（原文）：**
- TSN 帧采样：`clip_len=1, frame_interval=1`，train/val 取 `num_clips=3`，test 取 `num_clips=25`。
- 尺度变换链：先 `Resize(scale=(-1, 256))` → 多尺度/中心/十裁剪到 `input_size/crop_size=224` → 再 `Resize(scale=(224,224), keep_ratio=False)`。
- 多尺度训练：`MultiScaleCrop` 使用 `scales=(1, 0.875, 0.75, 0.66), random_crop=False, max_wh_scale_gap=1`；lazy 版本简化为 `scales=(1, 0.8), max_wh_scale_gap=0`。
- 增强：`Flip(flip_ratio=0.5)`；归一化 `to_bgr=False`（自定义示例里改为 `to_rgb=True`）。
- Lazy 视频采样：`clip_len=32, frame_interval=2, num_clips=1`，并使用 `decoding_backend='turbojpeg'`。
- 自定义示例采样：`DenseSampleFrames(clip_len=8, frame_interval=8, num_clips=1)` + `RawFrameDecode(io_backend='disk')`。

**Collect 机制（原文）：** "Collect - add: img_metas (the keys of img_metas is specified by `meta_keys`); remove: all other keys except for those specified by `keys`"，且"the first key, commonly `imgs`, will be used as the main key to calculate the batch size"。

---

## 【表格解读】

> **原文无表格。** 原文以"操作名 + 列表"形式列出了每个 pipeline 操作对 dict 字段的 add / update / remove 影响（`*` 表示可能不影响）。下面将原文三类操作列表逐字还原为 markdown 表格以便阅读。

### 表 1：Data loading 类操作对 dict 的影响（原文逐字还原）

| Operation | add | update |
|---|---|---|
| `SampleFrames` | `frame_inds, clip_len, frame_interval, num_clips` | `*total_frames` |
| `DenseSampleFrames` | `frame_inds, clip_len, frame_interval, num_clips` | `*total_frames` |
| `PyAVDecode` | `imgs, original_shape` | `*frame_inds` |
| `DecordDecode` | `imgs, original_shape` | `*frame_inds` |
| `OpenCVDecode` | `imgs, original_shape` | `*frame_inds` |
| `RawFrameDecode` | `imgs, original_shape` | `*frame_inds` |

**解读：** 采样类（`SampleFrames`/`DenseSampleFrames`）只产出索引和元信息，不读帧；解码类四种后端（PyAV / Decord / OpenCV / RawFrame）行为一致：新增 `imgs`（解码后的帧）和 `original_shape`，并视情况更新 `frame_inds`。其中 `RawFrameDecode` 配合 `io_backend='disk'` 用于"原始帧已抽好"场景，`PyAVDecode` 等用于"原始视频"场景。

### 表 2：Pre-processing 类操作对 dict 的影响（原文逐字还原）

| Operation | add | update |
|---|---|---|
| `RandomCrop` | `crop_bbox, img_shape` | `imgs` |
| `RandomResizedCrop` | `crop_bbox, img_shape` | `imgs` |
| `MultiScaleCrop` | `crop_bbox, img_shape, scales` | `imgs` |
| `Resize` | `img_shape, keep_ratio, scale_factor` | `imgs` |
| `Flip` | `flip, flip_direction` | `imgs, label` |
| `Normalize` | `img_norm_cfg` | `imgs` |
| `CenterCrop` | `crop_bbox, img_shape` | `imgs` |
| `ThreeCrop` | `crop_bbox, img_shape` | `imgs` |
| `TenCrop` | `crop_bbox, img_shape` | `imgs` |
| `MultiGroupCrop` | `crop_bbox, img_shape` | `imgs` |

**解读：** 所有 crop 类（`RandomCrop`/`RandomResizedCrop`/`MultiScaleCrop`/`CenterCrop`/`ThreeCrop`/`TenCrop`/`MultiGroupCrop`）统一以 `crop_bbox` + `img_shape` 描述裁剪；`MultiScaleCrop` 还会把自身使用过的 `scales` 写入 dict；`Resize` 不写 `crop_bbox` 而是写 `keep_ratio` 与 `scale_factor`；`Flip` 是唯一会更新 `label` 的预处理（因为动作识别中左右翻转会改标签）；`Normalize` 把归一化配置 `img_norm_cfg` 一并写入以便后处理回查。

### 表 3：Formatting 类操作对 dict 的影响（原文逐字还原）

| Operation | add | update | remove |
|---|---|---|---|
| `ToTensor` | — | specified by `keys` | — |
| `ImageToTensor` | — | specified by `keys` | — |
| `Transpose` | — | specified by `keys` | — |
| `Collect` | `img_metas`（由 `meta_keys` 指定其子键） | — | all other keys except for those specified by `keys` |
| `FormatShape` | `input_shape` | `imgs` | — |

**解读：** 三类张量化操作（`ToTensor`/`ImageToTensor`/`Transpose`）作用范围完全由 `keys` 参数决定；`Collect` 是"分拣"操作——白名单 `keys`（典型为 `imgs, label`）留在主 dict，其余打包成 `img_metas` 子字典，原文强调"第一个 key（通常 `imgs`）将作为计算 batch size 的主键"；`FormatShape` 仅记录 `input_shape` 信息（实际维度变换在 `FormatShape`/`Transpose`/`ToTensor` 协作中完成），并刷新 `imgs` 的元数据。

---

## 【公式解读】

**原文无公式。**（教程未出现 LaTeX 数学式或伪代码公式；"pipeline = dict-in / dict-out 操作序列"以文字 + 流程图形式描述。）

---

## 【关联】

- **MMCV 基础设施**：使用 `mmcv.parallel.data_container.DataContainer` 处理样本尺寸不一致问题；文档显式指向 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`。
- **PyTorch 数据加载**：`Dataset` + `DataLoader` 多 worker 范式，pipeline 中 `Collect`/`ToTensor` 输出直接喂入模型 forward。
- **MMAction 注册器**：自定义 pipeline 通过 `mmaction.datasets.PIPELINES.register_module` 注册；该注册器在所有内置 `SampleFrames`/`RawFrameDecode`/`Resize`/`Flip`/`Normalize`/`Collect`/`ToTensor` 等组件之上工作，是用户扩展的统一入口。
- **TSN 模型语义**：示例 pipeline 直接对应 TSN 的训练/验证/测试约定（多 clip、TenCrop 推理），下游被各 TSN config（如 `configs/recognition/tsn/` 系列）消费。
- **R(2+1)D 模型语义**：本教程路径位于 `PyTorch/contrib/cv/video/R(2+1)D/docs/`，表明 R(2+1)D 在该仓库中复用同一 MMAction 数据栈；`FormatShape` 中 `input_format='NCTHW'` 即为 3D 卷积网络（(2+1)D / I3D / SlowFast 等）所要求的五维张量布局，与上游 `SampleFrames(clip_len=32)`、`Collect(keys=['imgs','label'])` 配套。
- **Lazy 优化链路**：lazy `Resize/MultiScaleCrop/Resize/Flip` → `Fuse` → `Normalize` → `FormatShape(input_format='NCTHW')` → `Collect` → `ToTensor`，专为 3D 网络（如 R(2+1)D）减少密集解码后帧的反复 IO。
- **教程体系**：标题 "Tutorial 4" 暗示该项目还有其他 Tutorial（如 Tutorial 1/2/3，可能为 config、数据集、模型构建等），但本文件内未提供内部链接，文末链接信息为"无"。

---

## 【使用方法】

**1. 直接使用内置 pipeline：** 在 config 中按 `train_pipeline`/`val_pipeline`/`test_pipeline` 列表形式组合各 `dict(type='...')`。示例（原文 TSN）：

```python
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_bgr=False)
train_pipeline = [
    dict(type='SampleFrames', clip_len=1, frame_interval=1, num_clips=3),
    dict(type='RawFrameDecode', io_backend='disk'),
    dict(type='Resize', scale=(-1, 256)),
    dict(type='MultiScaleCrop', input_size=224,
         scales=(1, 0.875, 0.75, 0.66),
         random_crop=False, max_wh_scale_gap=1),
    dict(type='Resize', scale=(224, 224), keep_ratio=False),
    dict(type='Flip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs', 'label'], meta_keys=[]),
    dict(type='ToTensor', keys=['imgs', 'label'])
]
```

**2. 启用 Lazy 加速（原文示例）：** 把 `Resize`/`MultiScaleCrop`/`Resize`/`Flip` 全部加上 `lazy=True`，并在序列中插入 `dict(type='Fuse')`，`FormatShape` 使用 `input_format='NCTHW'` 以适配 3D 网络。

**3. 编写自定义 pipeline（原文三步法）：**

```python
# my_pipeline.py
from mmaction.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:
    def __call__(self, results):
        results['key'] = value
        return results
```

```python
# 在数据集 __init__ 或 registry 文件中
from .my_pipeline import MyTransform
```

```python
# 在 config 中使用
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='DenseSampleFrames', clip_len=8, frame_interval=8, num_clips=1),
    dict(type='RawFrameDecode', io_backend='disk'),
    dict(type='MyTransform'),               # use a custom pipeline
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='Collect', keys=['imgs', 'label'], meta_keys=[]),
    dict(type='ToTensor', keys=['imgs', 'label'])
]
```

> 自定义类只需实现 `__call__(self, results): dict -> dict`，使其可被插入到任意两个内置操作之间；不要求继承特定基类（原文示例中 `MyTransform` 即为裸类）。
