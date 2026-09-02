# Data Augmentation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/augmentation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/augmentation.md

# 深度解读:Detectron2 数据增强(Data Augmentation)

## 【定位】

Detectron2 数据增强系统的使用与扩展指南——阐述如何在编写新数据加载器时使用增强,以及如何编写自定义增强/变换,以同时支持图像、边界框、掩码等多类型数据的协同增强,并暴露底层"操作"供高级用法利用。

---

## 【技术要点】

1. **AugmentationList 串接多步增强**:通过 `T.AugmentationList([...])` 静态声明一个增强序列(策略),包含 `RandomBrightness(0.9, 1.1)`、`RandomFlip(prob=0.5)`、`RandomCrop("absolute", (640, 640))` 等具体策略。
2. **AugInput 作为统一输入容器**:`T.AugInput(image, boxes=boxes, sem_seg=sem_seg)` 一次性传入多种数据类型,`augs(input)` 在原地(in-place)修改输入,并返回 `T.Transform` 对象用于额外数据。
3. **Augmentation 与 Transform 的解耦**:`T.Augmentation` 定义"策略",`__call__(AugInput) -> Transform` 同时完成增强并返回操作对象;`T.Transform` 定义"操作",提供 `apply_image`、`apply_coords`、`apply_polygons`、`apply_segmentation` 等方法。
4. **自定义增强通过子类化**:继承 `T.Augmentation` 并实现 `get_transform(self, image, ...)`;函数签名中出现的属性名(如 `image`, `sem_seg`)即从 `AugInput` 读取。
5. **支持反向变换**:`transform.inverse()` 可将增强后图像上的预测(如分割掩码)映射回原图坐标。
6. **可注册新数据类型**:通过 `@T.HFlipTransform.register_type("rotated_boxes")` 把旋转框等扩展类型挂接到现有变换器上,自动获得 `apply_rotated_boxes(...)` 接口。

---

## 【关键机制与数据】

**三大基本概念**(原文):

- **`T.Augmentation`**——"policy",定义如何修改输入;`__call__(AugInput) -> Transform` 在原地增强并返回操作对象。
- **`T.Transform`**——"operations",实现具体变换;拥有 `apply_image`、`apply_coords` 等方法定义每种数据类型的变换方式。
- **`T.AugInput`**——存储 `Augmentation` 所需的输入及变换方式;常见用例直接使用即可,`AugInput` 之外的额外数据可通过返回的 `transform` 进行增强。

**基础数据流**(原文代码):
```
AugInput(image, boxes=boxes, sem_seg=sem_seg)
    │
    ▼
augs(input)  ──►  transform : T.Transform
    │
    ├─► input.image          (新图像)
    ├─► input.sem_seg        (新语义分割)
    ├─► transform.apply_image(image2)
    └─► transform.apply_polygons(polygons)
```

**关键点自定义策略**(原文):图像水平翻转后,需交换"左眼"与"右眼"等语义性 keypoints。检测方法:
```python
do_hflip = sum(isinstance(t, T.HFlipTransform) for t in transforms) % 2 == 1
```
翻转奇数次时,按 `flip_indices_mapping` 索引重排 keypoints 数组。

**关键点可见性逐步检查**(原文):增强链可能把可见点先移出边界(如裁剪),后又被拉回(如 padding)。若需标为"invisible",则每步变换后都需检测:
```python
for t in transform.transforms:
    keypoints_xy = t.apply_coords(keypoints_xy)
    visibility &= (keypoints_xy >= [0, 0] & keypoints_xy <= [W, H]).all(axis=1)
```

**推理阶段反变换**(原文):
```python
transform = augs(input)
pred_mask = make_prediction(input.image)              # 在增强图像上预测
inv_transform = transform.inverse()                   # 反向
pred_mask_orig = inv_transform.apply_segmentation(pred_mask)
```

**AugInput 的能力扩展**(原文):通过重写 `AugInput.transform()` 方法,可让不同字段之间相互依赖(如基于增强后的掩码后处理边界框)。

> 性能/数值数据:原文未提供。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式(文档中出现的均为代码片段,如 `visibility &= (keypoints_xy >= [0, 0] & keypoints_xy <= [W, H]).all(axis=1)` 系 Python 布尔表达式而非数学公式)。

---

## 【关联】

**与其他特性的关系**(基于原文):

- **Dataloader 教程** (`data_loading`):默认 data loader 已支持接收用户提供的增强列表——本文档侧重"如何写新数据加载器"与"如何写新增强",与默认 loader 的关系是"默认 loader 是上层封装,本文是底层机制"。
- **与 albumentations 的对比**(原文):本文档列出的"目标 1(多数据类型协同增强)"与"目标 2(静态声明序列)"是 albumentations 也具备的功能;目标 3(可扩展数据类型,如旋转框、视频片段)与目标 4(操作的可处理/可查询)是 detectron2 独有的扩展能力——这是该 API 引入额外开销的来源。

**内部链接对应模块**(原文提及):

| 链接 | 角色 | 关键能力 |
|---|---|---|
| `../modules/data_transforms.html#detectron2.data.transforms.Augmentation` | 策略类 | `__call__(AugInput) -> Transform`、子类的 `get_transform` |
| `../modules/data_transforms.html#detectron2.data.transforms.Transform` | 操作类 | `apply_image`/`apply_coords`/`inverse()`;支持 `register_type(...)` 注册新数据类型 |
| `../modules/data_transforms.html#detectron2.data.transforms.Transform.inverse` | 反变换方法 | 把增强空间结果映射回原图 |
| `../modules/data_transforms.html#detectron2.data.transforms.AugInput` | 输入容器基类 | 存储增强所需输入及如何变换 |
| `../modules/data_transforms.html#detectron2.data.transforms.StandardAugInput` | 标准 AugInput 实现 | 内置 `image`/`boxes`/`sem_seg` 字段,覆盖常见增强策略 |

**上下文位置**:本文位于 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/augmentation.md`,是 detectron2 教程体系中数据流水线方向的核心文档,与 `data_loading.md` 共同构成"加载—增强"链路。

---

## 【使用方法】

**基础用法**(原文代码):
```python
from detectron2.data import transforms as T

augs = T.AugmentationList([
    T.RandomBrightness(0.9, 1.1),
    T.RandomFlip(prob=0.5),
    T.RandomCrop("absolute", (640, 640))
])  # type: T.Augmentation

input = T.AugInput(image, boxes=boxes, sem_seg=sem_seg)
transform = augs(input)  # type: T.Transform

image_transformed = input.image
sem_seg_transformed = input.sem_seg
image2_transformed = transform.apply_image(image2)
polygons_transformed = transform.apply_polygons(polygons)
```

**编写自定义增强**(原文代码):
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

class MyCustomCrop(T.Augmentation):
    def get_transform(self, image, sem_seg):
        return T.CropTransform(...)   # 同时利用 image 与 sem_seg 决定裁剪

augs = MyCustomResize()
transform = augs(input)
```

**注册新数据类型**(原文代码):
```python
@T.HFlipTransform.register_type("rotated_boxes")
def func(flip_transform: T.HFlipTransform, rotated_boxes: Any):
    return flipped_rotated_boxes

t = HFlipTransform(width=800)
transformed_rotated_boxes = t.apply_rotated_boxes(rotated_boxes)
```

**推理期反变换**(原文代码):
```python
transform = augs(input)
pred_mask = make_prediction(input.image)
inv_transform = transform.inverse()
pred_mask_orig = inv_transform.apply_segmentation(pred_mask)
```

**关键点自定义标注**(原文代码):
```python
transform = augs(input)
keypoints_xy = transform.apply_coords(keypoints_xy)

transforms = T.TransformList([transform]).transforms
do_hflip = sum(isinstance(t, T.HFlipTransform) for t in transforms) % 2 == 1
if do_hflip:
    keypoints_xy = keypoints_xy[flip_indices_mapping]

# 逐步可见性检查
assert isinstance(transform, T.TransformList)
for t in transform.transforms:
    keypoints_xy = t.apply_coords(keypoints_xy)
    visibility &= (keypoints_xy >= [0, 0] & keypoints_xy <= [W, H]).all(axis=1)
```

**默认数据加载器接入**(原文说明):若使用 detectron2 默认 data loader,可通过用户提供的增强列表直接传入,详见 [Dataloader 教程](data_loading)。
