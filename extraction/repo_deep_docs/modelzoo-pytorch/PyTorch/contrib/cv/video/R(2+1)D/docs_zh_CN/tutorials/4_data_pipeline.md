# 教程 4：如何设计数据处理流程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/4_data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/4_data_pipeline.md

# 一体化深度解读：MMAction2 数据处理流水线设计教程

## 【定位】

本教程系统阐述 MMAction2 中面向动作识别与时序动作检测的**数据前处理流水线（Data Pipeline）**设计方法：如何把「数据加载 → 数据预处理 → 数据格式化」拆解为一系列可组合、可扩展的字典变换操作，并支持 Lazy 算子加速与自定义流水线扩展。

---

## 【技术要点】

1. **字典式流水线（dict-in / dict-out）**：流水线的每一步都接收一个 `dict`，对其中的字段进行「新增/更新/删除」后输出下一个 `dict`，作为下一步输入——即「管线即数据字典变换序列」。
2. **三类操作分层**：
   - **数据加载**：`SampleFrames` / `DenseSampleFrames`（采样帧索引）+ `RawFrameDecode` / `PyAVDecode` / `DecordDecode` / `OpenCVDecode`（解码为图像张量）。
   - **数据预处理**：裁剪类（`RandomCrop`、`RandomResizedCrop`、`MultiScaleCrop`、`CenterCrop`、`ThreeCrop`、`TenCrop`、`MultiGroupCrop`）、几何变换（`Resize`、`Flip`）与像素归一化（`Normalize`）。
   - **数据格式化**：`ToTensor`、`ImageToTensor`、`Transpose`、`Collect`、`FormatShape`，负责把 dict 整理成模型可直接消费的 Tensor。
3. **可变尺寸数据用 `DataContainer`**：由于动作识别中帧、边界框尺寸不固定，MMAction2 复用 MMCV 的 `DataContainer` 收集并按需分配不同形状的数据。
4. **Lazy 算子 + Fuse 阶段加速**：Lazy 操作仅「记录」如何处理（例如 `Resize lazy=True` 只修改 bbox，不动像素），推迟到 `Fuse` 阶段一次性应用，避免对原始像素的多次读写。原文示例：`Resize`、`MultiScaleCrop`、`Resize`、`Flip` 全部 `lazy=True`，最后由 `Fuse` 统一处理。
5. **关键归一化参数（TSN 示例给出）**：`mean=[123.675, 116.28, 103.53]`、`std=[58.395, 57.12, 57.375]`、`to_bgr=False`，三通道顺序与 ImageNet 预训练保持一致。
6. **扩展机制**：通过 `@PIPELINES.register_module()` 注册自定义类，在 config 的 pipeline 列表中以 `type='MyTransform'` 字符串方式调用。

---

## 【关键机制与数据】

### 数据流与执行模型（原文）

> "按照惯例，MMAction2 使用 `Dataset` 和 `DataLoader` 实现多进程数据加载。`Dataset` 返回一个字典，作为模型的输入。"
>
> "由于动作识别和时序动作检测的数据大小不一定相同（图片大小，边界框大小等），MMAction2 使用 MMCV 中的 `DataContainer` 收集和分配不同大小的数据。"

- **数据流**：`Dataset` 构造 → 返回 dict → 依次经过每个流水线算子 → 最终 `Collect` + `ToTensor` → 模型输入。
- **并行机制**：通过 PyTorch `DataLoader` 多进程加载。
- **解耦原则**：原文："'数据前处理流水线' 和 '数据集构建' 是相互解耦的。通常，'数据集构建' 定义如何处理标注文件，'数据前处理流水线' 定义数据加载、预处理、格式化等功能。"

### Lazy 算子机制（原文）

> "Lazy 操作记录如何处理数据，但是它会推迟对原始数据的处理，直到进入 Fuse 阶段。"
>
> "lazy 操作符避免了对原始数据的频繁读取和修改操作，只在最后的 Fuse 阶段中对原始数据进行了一次处理，从而加快了数据预处理速度，因此，推荐用户使用本功能。"

**Lazy 流水线示例的差异化设计（与普通流水线对比，原文）**：

| 阶段 | 普通 TSN 流水线 | Lazy 流水线 |
|---|---|---|
| 帧采样 | `SampleFrames clip_len=1` | `SampleFrames clip_len=32, frame_interval=2`（更适合 SlowFast 等） |
| 解码后端 | `RawFrameDecode io_backend='disk'` | `RawFrameDecode decoding_backend='turbojpeg'` |
| Resize 链 | 直接对像素操作 | 三个 `Resize/MultiScaleCrop/Resize` 均 `lazy=True`，只动 bbox |
| Flip | 直接翻转像素 | `Flip lazy=True`，仅记录 flip 标志与方向 |
| 像素最终处理时机 | 在 `Normalize` 之前已多次改动像素 | 通过 `Fuse` 一次性应用，再交 `Normalize` |
| 张量布局 | `FormatShape input_format='NCHW'` | `FormatShape input_format='NCTHW'` |

**关键示例数值（原文逐字保留）**：
- 训练集采样：`clip_len=32, frame_interval=2, num_clips=1`
- 解码后端：`decoding_backend='turbojpeg'`
- 多尺度裁剪尺度：`scales=(1, 0.8)`，`max_wh_scale_gap=0`
- 翻转概率：`flip_ratio=0.5`
- 最终 Resize：`scale=(224, 224), keep_ratio=False`

---

## 【表格解读】

原文用「操作 → 新增/更新/删除」列表描述每个算子对 dict 的影响。下表逐字还原并标注关键变化：

### 表 1：数据加载类算子（原文逐字还原）

| 算子 (type) | 新增 (added) | 更新 (updated) |
|---|---|---|
| `SampleFrames` | `frame_inds`, `clip_len`, `frame_interval`, `num_clips`, `*total_frames` | — |
| `DenseSampleFrames` | `frame_inds`, `clip_len`, `frame_interval`, `num_clips`, `*total_frames` | — |
| `PyAVDecode` | `imgs`, `original_shape` | `*frame_inds` |
| `DecordDecode` | `imgs`, `original_shape` | `*frame_inds` |
| `OpenCVDecode` | `imgs`, `original_shape` | `*frame_inds` |
| `RawFrameDecode` | `imgs`, `original_shape` | `*frame_inds` |

**解读**：四个解码算子功能等价，仅底层解码库不同——`PyAV` 用 FFmpeg、`Decord` 用自家 libdecord、`OpenCV` 用 cv2、`RawFrameDecode` 用 turbojpeg/rawbytes。所有解码器都会消费上游 `SampleFrames` 产出的 `frame_inds` 来索引，并把读到的帧写入 `imgs` 字段，`*` 表示该字段不一定被影响。

### 表 2：数据预处理类算子（原文逐字还原）

| 算子 (type) | 新增 (added) | 更新 (updated) |
|---|---|---|
| `RandomCrop` | `crop_bbox`, `img_shape` | `imgs` |
| `RandomResizedCrop` | `crop_bbox`, `img_shape` | `imgs` |
| `MultiScaleCrop` | `crop_bbox`, `img_shape`, `scales` | `imgs` |
| `Resize` | `img_shape`, `keep_ratio`, `scale_factor` | `imgs` |
| `Flip` | `flip`, `flip_direction` | `imgs`, `label` |
| `Normalize` | `img_norm_cfg` | `imgs` |
| `CenterCrop` | `crop_bbox`, `img_shape` | `imgs` |
| `ThreeCrop` | `crop_bbox`, `img_shape` | `imgs` |
| `TenCrop` | `crop_bbox`, `img_shape` | `imgs` |
| `MultiGroupCrop` | `crop_bbox`, `img_shape` | `imgs` |

**解读**：所有裁剪类算子都同时记录 `crop_bbox`（便于可视化/复用）和最终 `img_shape`；`Resize` 还会保留 `keep_ratio` 与 `scale_factor` 以便回溯；`Flip` 是唯一会改动 `label` 的几何变换（label 翻转会破坏时序因果，因此需谨慎）；`Normalize` 把归一化参数本身写回 `img_norm_cfg`，方便后续可视化反归一化。

### 表 3：数据格式化类算子（原文逐字还原）

| 算子 (type) | 新增 (added) | 更新 (updated) | 删除 (removed) |
|---|---|---|---|
| `ToTensor` | — | specified by `keys` | — |
| `ImageToTensor` | — | specified by `keys` | — |
| `Transpose` | — | specified by `keys` | — |
| `Collect` | `img_metas`（整合所有需要的元数据到 `meta_keys` 键值中） | — | 所有未在 `keys` 中指定的字段 |

**解读**：
- `Collect` 是流水线的「汇聚闸」：把多个元数据字段整合为统一的 `img_metas`，并清理掉 `keys` 之外的所有字段（防止无关数据进入训练循环）。
- 原文特别强调："**值得注意的是**，第一个键，通常是 `imgs`，会作为主键用来计算批大小。" ——这决定了 `Collect keys=[...]` 的第一个元素必须是被 `DataLoader` 用于 batch 维度对齐的张量。
- `FormatShape`（表外补充）新增 `input_shape`、更新 `imgs`，作用是把 `imgs` 整理成指定维度（如 NCHW/NCTHW）以匹配模型期望。

### 表 4：TSN 三套流水线配置对照（原文逐字还原）

| 配置键 | `train_pipeline` | `val_pipeline` | `test_pipeline` |
|---|---|---|---|
| `SampleFrames` | `clip_len=1, frame_interval=1, num_clips=3` | `clip_len=1, frame_interval=1, num_clips=3, test_mode=True` | `clip_len=1, frame_interval=1, num_clips=25, test_mode=True` |
| `RawFrameDecode` | `io_backend='disk'` | `io_backend='disk'` | `io_backend='disk'` |
| 裁剪/几何 | `Resize(-1,256)` → `MultiScaleCrop(input_size=224, scales=(1,0.875,0.75,0.66), random_crop=False, max_wh_scale_gap=1)` → `Resize((224,224), keep_ratio=False)` → `Flip(flip_ratio=0.5)` | `Resize(-1,256)` → `CenterCrop(224)` | `Resize(-1,256)` → `TenCrop(224)` |
| `Normalize` | `**img_norm_cfg`（`mean=[123.675, 116.28, 103.53]`, `std=[58.395, 57.12, 57.375]`, `to_bgr=False`） | 同上 | 同上 |
| `FormatShape` | `input_format='NCHW'` | `input_format='NCHW'` | `input_format='NCHW'` |
| `Collect` | `keys=['imgs','label'], meta_keys=[]` | 同上 | 同上 |
| `ToTensor` | `keys=['imgs','label']` | `keys=['imgs']` | `keys=['imgs']` |

**解读**：
- 训练时使用 `MultiScaleCrop` 多尺度抖动 + `Flip` 随机翻转实现数据增强；验证用 `CenterCrop` 确定性裁剪；测试用 `TenCrop`（中心+四角的 10-crop 集成）提升稳健性。
- `num_clips` 在训练/验证为 3，测试扩到 25，是为了覆盖更长视频的时间维度并做 clip 级集成。
- 训练阶段 `ToTensor` 同时转 `label`，是因为训练时需要计算分类损失；验证/测试时通常 `label` 不必转 Tensor。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

1. **MMCV 依赖**：流水线的可变尺寸数据容器来自 MMCV 的 `DataContainer`（原文链接指向 `mmcv/parallel/data_container.py`）；同时 `PIPELINES.register_module()` 注册机制亦来自 MMCV 的 Registry 体系。
2. **`Dataset` 与 `DataLoader`**：流水线挂在 `Dataset` 的 `prepare_train_data` / `prepare_test_data` 中，由 `DataLoader` 多进程调度——本教程聚焦「字典变换」，不涉及上层数据加载调度。
3. **上游「数据集构建」**：教程明确把"标注文件解析"剥离到 `Dataset` 类中，与本流水线解耦。
4. **模型侧的张量期望**：`FormatShape input_format` 取值需与模型 forward 期望一致——TSN 一类 2D CNN backbone 用 `'NCHW'`，SlowFast/CSN/TSM 等 3D 网络用 `'NCTHW'`（原文 Lazy 示例）。
6. **R(2+1)D 仓库上下文**：本文档位于 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/` 下，是 MMAction2 数据流水线教程的中文版本，可作为该 R(2+1)D 视频识别模型训练配置文件中 pipeline 字段的参考。
7. **自定义扩展**：`Collect` 的 `meta_keys` 字段决定了哪些元数据被保留——下游模型若需要额外元信息（如人体检测框、光流），需在自定义 pipeline 中注入并在 `Collect` 时声明。

---

## 【使用方法】

### 1. 标准（非 Lazy）流水线（原文 TSN 示例）

```python
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_bgr=False)

train_pipeline = [
    dict(type='SampleFrames', clip_len=1, frame_interval=1, num_clips=3),
    dict(type='RawFrameDecode', io_backend='disk'),
    dict(type='Resize', scale=(-1, 256)),
    dict(type='MultiScaleCrop',
         input_size=224, scales=(1, 0.875, 0.75, 0.66),
         random_crop=False, max_wh_scale_gap=1),
    dict(type='Resize', scale=(224, 224), keep_ratio=False),
    dict(type='Flip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCHW'),
    dict(type='Collect', keys=['imgs', 'label'], meta_keys=[]),
    dict(type='ToTensor', keys=['imgs', 'label'])
]
```

**关键配置项说明（原文）**：
- `clip_len` / `frame_interval` / `num_clips`：采样参数，控制每段视频被切分成多少 clip、每个 clip 抽几帧、帧间隔。
- `io_backend='disk'`：解码器后端，原文 Lazy 流水线示例改用 `decoding_backend='turbojpeg'` 提速。
- `scales=(1, 0.875, 0.75, 0.66)`：多尺度裁剪尺度候选集合。
- `input_format`：模型张量布局，原文 TSN 用 `'NCHW'`，3D 网络用 `'NCTHW'`。
- `meta_keys=[]`：被 `Collect` 收拢的元数据键列表；空列表表示不额外保留元数据。

### 2. Lazy 加速流水线（原文 SlowFast 风格示例）

```python
train_pipeline = [
    dict(type='SampleFrames', clip_len=32, frame_interval=2, num_clips=1),
    dict(type='RawFrameDecode', decoding_backend='turbojpeg'),
    dict(type='Resize', scale=(-1, 256), lazy=True),
    dict(type='MultiScaleCrop',
         input_size=224, scales=(1, 0.8),
         random_crop=False, max_wh_scale_gap=0, lazy=True),
    dict(type='Resize', scale=(224, 224), keep_ratio=False, lazy=True),
    dict(type='Flip', flip_ratio=0.5, lazy=True),
    dict(type='Fuse'),          # 一次性应用前面 lazy 记录的几何变换
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='Collect', keys=['imgs', 'label'], meta_keys=[]),
    dict(type='ToTensor', keys=['imgs', 'label'])
]
```

**启用要点（原文）**：
- 在所有"对图像几何敏感但只记录 bbox/标志位即可"的算子上加 `lazy=True`。
- 必须在所有 lazy 算子之后、`Normalize`（会真正读像素）之前插入 `Fuse`，否则像素始终未被处理。
- 原文原话："推荐用户使用本功能"。

### 3. 自定义流水线（原文扩展步骤）

```python
# Step 1: my_pipeline.py
from mmaction.datasets import PIPELINES

@PIPELINES.register_module()
class MyTransform:
    def __call__(self, results):
        results['key'] = value
        return results

# Step 2: 在 __init__.py 中导入
from .my_pipeline import MyTransform

# Step 3: 在 config 中使用
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='DenseSampleFrames', clip_len=8, frame_interval=8, num_clips=1),
    dict(type='RawFrameDecode', io_backend='disk'),
    dict(type='MyTransform'),      # 自定义算子以字符串 type 调用
    dict(type='Normalize', **img_norm_cfg),
    dict(type='FormatShape', input_format='NCTHW'),
    dict(type='Collect', keys=['imgs', 'label'], meta_keys=[]),
    dict(type='ToTensor', keys=['imgs', 'label'])
]
```

**配置/启用要点（原文）**：
- 自定义类必须用 `@PIPELINES.register_module()` 装饰（来自 mmaction.datasets），否则无法通过 `type='MyTransform'` 字符串查找。
- 类只需实现 `__call__(self, results) -> dict`，输入输出均为字典，遵循流水线 dict-in/dict-out 约定。
- `to_rgb=True` 是自定义示例中给出的另一个合法 `img_norm_cfg` 取值，与 TSN 默认的 `to_bgr=False` 不同，可按 backbone 预训练权重通道顺序选择。
