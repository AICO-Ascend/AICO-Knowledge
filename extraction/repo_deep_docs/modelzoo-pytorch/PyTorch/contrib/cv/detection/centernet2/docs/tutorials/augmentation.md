# Data Augmentation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/augmentation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/augmentation.md

## 【定位】

这篇文档介绍 Detectron2 数据增强系统如何在数据加载、训练与推理流程中统一组合图像、框、掩码、语义分割及自定义数据类型的变换，并支持扩展增强策略、可逆推理和特殊语义标注处理。

## 【技术要点】

1. **增强系统的设计目标**：支持多种数据类型联合增强、静态声明的增强序列、旋转框和视频片段等自定义数据类型，以及对实际执行操作的检查、复用与求逆；这些能力以一定 API 开销为代价。

2. **三类核心对象**：
   - `T.Augmentation` 定义“策略”，通过 `__call__(AugInput) -> Transform` 原位修改输入并返回实际变换。
   - `T.Transform` 描述“操作”，通过 `apply_image`、`apply_coords` 等方法定义各数据类型的变换方式。
   - `T.AugInput` 集中保存 `image`、`boxes`、`sem_seg` 等输入及其变换结果；未纳入它的数据仍可使用返回的 `transform` 同步处理。

3. **基础增强配置**：将多个增强组成 `T.AugmentationList`，例如：
   - `T.RandomBrightness(0.9, 1.1)`：亮度参数范围为 `0.9` 到 `1.1`。
   - `T.RandomFlip(prob=0.5)`：翻转概率为 `0.5`。
   - `T.RandomCrop("absolute", (640, 640))`：使用绝对尺寸模式裁剪为 `640 × 640`。
   - 之后通过 `augs(input)` 同时更新 `image` 和 `sem_seg` 等内置字段，并使用 `apply_image`、`apply_polygons` 同步处理额外数据。

4. **自定义增强策略**：通过继承 `T.Augmentation` 并实现 `get_transform` 返回具体 `T.Transform`。原文示例包括：
   - `T.ColorTransform(lambda x: x * r[0] + r[1] * 10)`，其中缩放系数取自 `np.random.rand(2)` 的第一个值，偏移为第二个值乘以 `10`。
   - `T.ResizeTransform(old_h, old_w, new_h, new_w)`，其中高度使用 `int(old_h * np.random.rand())`，宽度使用 `int(old_w * 1.5)`。
   - 自定义裁剪可在 `get_transform(self, image, sem_seg)` 中同时利用图像和语义分割决定 `T.CropTransform(...)`。

5. **自定义数据类型与可逆操作**：可继承 `T.Transform` 增加新操作，也可使用 `@T.HFlipTransform.register_type("rotated_boxes")` 为 `rotated_boxes` 注册处理函数；原文示例使用 `HFlipTransform(width=800)` 构造宽度为 `800` 的水平翻转。推理后可通过 `transform.inverse()` 将增强图像上的预测恢复到原始坐标系。

6. **语义相关的高级处理**：关键点不只改变坐标，还可能需要交换“left eye”和“right eye”的语义，因此系统统计 `T.HFlipTransform` 出现次数；奇数次水平翻转时使用 `flip_indices_mapping` 交换对应点。可见性还必须在每个变换步骤后依据 `[0, 0]` 与 `[W, H]` 边界重新检查，因为某一步移出边界的点可能被后续 padding 重新移回。

## 【关键机制与数据】

- **原文：** 整体数据流是“增强策略声明 → 将策略应用于 `AugInput` → 原位更新 `image`、`boxes`、`sem_seg` 等字段 → 返回可复用的 `Transform` → 对额外数据调用相应的 `apply_*` 方法”。因此，额外数据不需要重新猜测随机参数，也不必再次调用增强策略。

- **原文：** 基础示例中，`T.AugmentationList` 依次组合亮度扰动、随机翻转和 `640 × 640` 裁剪；`augs(input)` 返回操作对象，图像和语义分割从 `input.image`、`input.sem_seg` 读取，额外图像 `image2` 和多边形 `polygons` 则通过 `transform.apply_image` 与 `transform.apply_polygons` 同步转换。

- **原文：** 关键点示例先执行 `transform.apply_coords(keypoints_xy)`，再从 `T.TransformList([transform]).transforms` 获取全部操作。代码通过 `sum(isinstance(t, T.HFlipTransform) for t in transforms) % 2 == 1` 判断水平翻转总次数是否为奇数；只有奇数次时才交换左右关键点语义索引。

- **原文：** 关键点可见性采用逐步检查机制：每个 `t` 都立即执行 `t.apply_coords(keypoints_xy)`，随后执行 `visibility &= ...`，使用图像尺寸 `W`、`H` 判断坐标是否仍在边界内。原文特别指出，如果先裁剪掉关键点、后用 padding 把它移回边界，只在全部增强结束后检查会把本应标记为不可见的关键点错误保留为可见。

- **原文：** 推理时，模型接收 `input.image` 并在增强坐标系中产生 `pred_mask`；随后 `inv_transform = transform.inverse()`，再通过 `inv_transform.apply_segmentation(pred_mask)` 得到原始图像上的 `pred_mask_orig`。

- **原文：** 原文给出了这些配置性数字：`0.9`、`1.1`、`0.5`、`640 × 640`、`1.5` 和水平翻转示例宽度 `800`。但没有给出准确率、损失、吞吐、显存占用或增强前后性能对比等基准数据。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **数据加载上游**：文档说明，使用 Detectron2 默认数据加载器时，用户提供的自定义增强列表已经受支持；具体接入方式参见 [Dataloader tutorial](data_loading)。默认加载器还包含根据水平翻转交换左右关键点语义的自定义策略。

- **增强策略层**：[`T.Augmentation`](../modules/data_transforms.html#detectron2.data.transforms.Augmentation) 决定如何从当前输入产生实际变换，是随机参数和裁剪位置等策略的载体。

- **操作层**：[`T.Transform`](../modules/data_transforms.html#detectron2.data.transforms.Transform) 负责把同一操作一致地施加到图像、坐标、框、掩码和多边形等不同类型；它还可以注册 `rotated_boxes` 等新数据类型。

- **输入封装层**：[`T.AugInput`](../modules/data_transforms.html#detectron2.data.transforms.AugInput) 提供 `image`、`boxes` 和 `sem_seg`；相关 API 入口还指向 [`StandardAugInput`](../modules/data_transforms.html#detectron2.data.transforms.AugInput.StandardAugInput)。若标准字段不足以表达依赖关系，可重新实现 `transform()`，例如基于增强后的掩码后处理边界框。

- **关键点与模型输出下游**：增强操作会先影响关键点坐标、语义标签和可见性，模型再在增强后的输入上预测；分割等结果通过 [`Transform.inverse()`](../modules/data_transforms.html#detectron2.data.transforms.Transform.inverse) 返回原始图像坐标系。`Transform` 的重复链接分别指向类定义、基础接口和 `inverse` 方法。

- **扩展方向**：除常见 2D 数据外，系统允许增加旋转边界框、视频片段或用户自定义字段；对于后处理，扩展 `AugInput` 或注册新的 `apply_*` 变换类型均属于下游扩展点。

## 【使用方法】

基础联合增强方式如下：

```python
from detectron2.data import transforms as T

# Define a sequence of augmentations:
augs = T.AugmentationList([
    T.RandomBrightness(0.9, 1.1),
    T.RandomFlip(prob=0.5),
    T.RandomCrop("absolute", (640, 640))
])  # type: T.Augmentation

# Define the augmentation input ("image" required, others optional):
input = T.AugInput(image, boxes=boxes, sem_seg=sem_seg)

# Apply the augmentation:
transform = augs(input)  # type: T.Transform
image_transformed = input.image  # new image
sem_seg_transformed = input.sem_seg  # new semantic segmentation

# For any extra data that needs to be augmented together, use transform, e.g.:
image2_transformed = transform.apply_image(image2)
polygons_transformed = transform.apply_polygons(polygons)
```

新增策略时继承 `T.Augmentation` 并实现 `get_transform`：

```python
class MyColorAugmentation(T.Augmentation):
    def get_transform(self, image):
        r = np.random.rand(2)
        return T.ColorTransform(lambda x: x * r[0] + r[1] * 10)

class MyCustomResize(T.Augmentation):
    def get_transform(self, image):
        old_h, old_w = image.shape[:2]
        new_h, new_w = int(old_h * np.random.rand()), int(old_w * 1.5)
        return T.ResizeTransform(old_h, old_w, new_h, new_w)

augs = MyCustomResize()
transform = augs(input)
```

自定义裁剪可把 `sem_seg` 加入函数签名，并确认输入对象包含所需字段：

```python
class MyCustomCrop(T.Augmentation):
    def get_transform(self, image, sem_seg):
        # decide where to crop using both image and sem_seg
        return T.CropTransform(...)

augs = MyCustomCrop()
assert hasattr(input, "image") and hasattr(input, "sem_seg")
transform = augs(input)
```

注册新的数据类型：

```python
@T.HFlipTransform.register_type("rotated_boxes")
def func(flip_transform: T.HFlipTransform, rotated_boxes: Any):
    # do the work
    return flipped_rotated_boxes

t = HFlipTransform(width=800)
transformed_rotated_boxes = t.apply_rotated_boxes(rotated_boxes)  # func will be called
```

原文此处装饰器使用 `T.HFlipTransform`，而构造语句写作 `HFlipTransform(width=800)`；原文未进一步解释两者是否为简写关系。

恢复推理结果到原始图像：

```python
transform = augs(input)
pred_mask = make_prediction(input.image)
inv_transform = transform.inverse()
pred_mask_orig = inv_transform.apply_segmentation(pred_mask)
```

默认数据加载器的具体配置入口、命令行参数和配置文件键：原文未涉及。
