# Data Augmentation

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/augmentation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/augmentation.md

# 深度解读:Detectron2 数据增强 (Data Augmentation) Guide

## 【定位】

本篇文档系统性阐述 Detectron2 数据增强子系统的设计目标、核心抽象 (`T.Augmentation` / `T.AugInput` / `T.Transform` 三元组)、基本使用方法、自定义扩展路径以及面向研究场景的高级用法,解决"如何同时增强多种类型数据 (image/boxes/masks/sem_seg)、如何声明式组合增强、如何自定义新增强与新数据类型、如何反向/部分应用增强操作"这一组工程问题。

---

## 【技术要点】

1. **系统设计四大目标**(原文逐条):① 允许同时增强多种数据类型 (如图像与对应的 bounding boxes、masks);② 允许应用一组**静态声明**的增强序列;③ 允许新增自定义数据类型 (旋转框、视频片段等);④ 处理并操纵增强所施加的**操作 (operations)**。
2. **三类核心抽象**:`T.Augmentation`(策略层,定义 "如何改")、`T.Transform`(操作层,定义 "怎么改",含 `apply_image`、`apply_coords` 等)、`T.AugInput`(输入容器,保存被增强字段);其关系为 `Augmentation.__call__(AugInput) -> Transform`,且**就地修改输入**。
3. **基础调用骨架**(原文示例):
   - 序列声明:`T.AugmentationList([T.RandomBrightness(0.9, 1.1), T.RandomFlip(prob=0.5), T.RandomCrop("absolute", (640, 640))])`
   - 输入构造:`T.AugInput(image, boxes=boxes, sem_seg=sem_seg)`
   - 应用与读取:`transform = augs(input)`,然后通过 `input.image`、`input.sem_seg` 取结果,或用 `transform.apply_image(image2)`、`transform.apply_polygons(polygons)` 增强额外数据。
4. **自定义新增强**:子类化 `T.Augmentation` 并实现 `get_transform(self, image, ...)`,其返回具体的 `T.Transform`(如 `T.ColorTransform(lambda x: x * r[0] + r[1] * 10)`、`T.ResizeTransform(old_h, old_w, new_h, new_w)`);`get_transform` 的函数签名可直接声明对 `AugInput` 中其他字段的依赖,如 `get_transform(self, image, sem_seg)`。
5. **可逆变换 (inverse)**:通过 `transform.inverse()` 得到 `T.Transform` 的反向操作,再调用 `apply_segmentation(pred_mask)` 把预测映射回原图坐标系,用于推理前/后处理一致性。
6. **新数据类型注册**:使用 `@T.HFlipTransform.register_type("rotated_boxes")` 装饰器向 `T.Transform` 子类注册新类型的 `apply_*` 处理函数 (示例 `HFlipTransform(width=800)` 后 `t.apply_rotated_boxes(rotated_boxes)` 即被分发到该函数)。

---

## 【关键机制与数据】

**工作原理 / 数据流** (原文):

- **声明 → 应用 → 读取** 三阶段流程。声明阶段由用户构造 `AugmentationList`;应用阶段调用 `augs(input)`,Augmentation 内部采样随机性并返回一个或多个 `Transform`,同时**就地**改写 `AugInput` 中预置字段 (`image`、`sem_seg` 等);读取阶段可直接读 `input.image`/`input.sem_seg`,或用返回的 `transform` 对 `AugInput` 之外的数据 (`image2`、`polygons`) 调用对应的 `apply_*`。
- **策略与操作分离**:策略 (`Augmentation`) 只决定 "改什么",具体数值/几何操作 (`Transform`) 通过 `apply_image`/`apply_coords` 等多态方法作用到每种数据类型;因此同一个 `Transform` 可被复用于 image、boxes、polygons、semantic segmentation 等多种字段。
- **操作可观测**:返回的 `T.TransformList([transform]).transforms` 是一份**操作记录**;原文示例利用它统计 `HFlipTransform` 出现奇数次还是偶数次,以决定关键点语义 (左右眼) 是否需要 `flip_indices_mapping` 交换。
- **逐步骤可见性判定**:对 visibility 这种语义字段,可在 `for t in transform.transforms` 循环里逐次调用 `t.apply_coords(keypoints_xy)`,并即时 `visibility &= (keypoints_xy >= [0,0] & keypoints_xy <= [W,H]).all(axis=1)`,原文亦给出对照——默认 `transform_keypoint_annotations` 选择把 "暂时出框再被填回" 的关键点仍标为 visible。
- **几何可逆性**:推理时先用 `augs(input)` 预处理图像,得到 `pred_mask = make_prediction(input.image)`;再 `inv_transform = transform.inverse()` 并 `inv_transform.apply_segmentation(pred_mask)` 即可把语义分割结果还原到原图坐标系。

**性能数据**:原文未给出任何 benchmark / 数值性能数据,仅在功能层面描述。

---

## 【表格解读】

**原文无表格。** 文档以示例代码 + 概念解释为主,未出现任何参数表/性能对比表/配置项表。

---

## 【公式解读】

**原文无显式数学公式** (无 LaTeX 行间/行内公式)。

但文档中含若干**伪代码/代码片段形式的关键表达式**,逐字保留并解释如下:

- `T.RandomBrightness(0.9, 1.1)`:参数 `0.9` 为亮度下限倍率,`1.1` 为上限倍率,表示在 `[0.9, 1.1]` 之间随机缩放像素亮度。
- `T.RandomFlip(prob=0.5)`:参数 `prob=0.5` 为执行翻转的概率。
- `T.RandomCrop("absolute", (640, 640))`:`"absolute"` 表示按**绝对像素值**裁剪到 `(640, 640)` 的尺寸。
- `T.AugInput(image, boxes=boxes, sem_seg=sem_seg)`:分别传入原图、bounding boxes、语义分割图;只有 `image` 为必填,`boxes`/`sem_seg` 可选。
- `T.ColorTransform(lambda x: x * r[0] + r[1] * 10)`:其中 `r = np.random.rand(2)`,即 `r[0]` 为乘性亮度系数、`r[1]*10` 为加性偏移,共同构成 `y = r0·x + 10·r1` 的逐像素仿射变换。
- `T.ResizeTransform(old_h, old_w, new_h, new_w)` 中,`new_h = int(old_h * np.random.rand())`,`new_w = int(old_w * 1.5)`——宽度方向固定放大 1.5 倍,高度方向按 `Uniform(0,1)` 随机缩放。
- `transform.apply_coords(keypoints_xy)`:对 `(x, y)` 关键点集合施加几何变换。
- `do_hflip = sum(isinstance(t, T.HFlipTransform) for t in transforms) % 2 == 1`:统计 `HFlipTransform` 出现次数的奇偶性,以判断整体是否被水平翻转 (翻转奇数次等效翻转一次)。
- `visibility &= (keypoints_xy >= [0, 0] & keypoints_xy <= [W, H]).all(axis=1)`:对每个关键点的两个坐标分量做边界判断,只有落在 `[0, W] × [0, H]` 内才视为可见,`&=` 表示按位与累积更新 visibility。
- `@T.HFlipTransform.register_type("rotated_boxes")`:装饰器把字符串 `"rotated_boxes"` 关联到一个签名为 `func(flip_transform, rotated_boxes) -> flipped_rotated_boxes` 的函数,使得 `t.apply_rotated_boxes(rotated_boxes)` 调用被分派到该函数。
- `HFlipTransform(width=800)`:构造一个关于宽度 `800` 的水平翻转变换,该宽度用于把 `x` 坐标映射为 `width - 1 - x`。

---

## 【关联】

- **与默认数据加载器的关系**:文档开篇明确指出,使用 Detectron2 默认数据加载器时,可直接通过[用户提供的自定义增强列表](data_loading.md) 启用本系统——即本教程主要面向**自写 data loader** 的场景。
- **与上游抽象层的关系**:`T.Augmentation`(策略) → `T.Transform`(操作) → `T.AugInput`(输入) 是三层耦合;其中 `T.AugInput` 在标准实现下对应 [T.StandardAugInput](../modules/data_transforms.html#detectron2.data.transforms.StandardAugInput),提供 `image`/`boxes`/`sem_seg` 默认字段,扩展需子类化并重写 `transform()`。
- **Transform 反向 API 的下游消费者**:`transform.inverse()` 输出的反向 `Transform` 通过 `apply_segmentation` 把分割预测还原到原图,服务于"带增强的推理 + 结果回投" 这一闭环。
- **与多类型数据增强生态的对照**:原文将特性 ① 和 ② 与 [albumentations](https://medium.com/pytorch/multi-target-in-albumentations-16a777e9006e) 做了对标,定位 Detectron2 系统因支持 ③/④ 而增加的额外开销。
- **特性组合关系**:可观测操作记录 (`TransformList`) 与几何可逆 (`inverse()`) 是 "Custom transform strategy" 与 "Geometrically invert the transform" 两节共同依赖的底层能力;`register_type` 与扩展 `AugInput` 共同构成 "Add new data types" 与 "Extend T.AugInput" 两条自定义路径。
- **关键点语义增强的内置参考**:文档指出 `transform_keypoint_annotations` 是 Detectron2 默认 loader 中实现关键点增强的内置函数,其对 "出框再回框" 的关键点选择保留 visible 标记。

---

## 【使用方法】

**启用方式 / 配置 / 命令** (原文所给):

- **使用内置增强组合**:
  ```python
  from detectron2.data import transforms as T
  augs = T.AugmentationList([
      T.RandomBrightness(0.9, 1.1),
      T.RandomFlip(prob=0.5),
      T.RandomCrop("absolute", (640, 640)),
  ])
  ```
- **应用到输入并取出结果**:
  ```python
  input = T.AugInput(image, boxes=boxes, sem_seg=sem_seg)
  transform = augs(input)
  image_transformed = input.image
  sem_seg_transformed = input.sem_seg
  image2_transformed = transform.apply_image(image2)
  polygons_transformed = transform.apply_polygons(polygons)
  ```
- **注册新数据类型** (以旋转框 + 水平翻转为例):
  ```python
  @T.HFlipTransform.register_type("rotated_boxes")
  def func(flip_transform: T.HFlipTransform, rotated_boxes: Any):
      return flipped_rotated_boxes
  t = HFlipTransform(width=800)
  transformed_rotated_boxes = t.apply_rotated_boxes(rotated_boxes)
  ```
- **推理时几何回投**:
  ```python
  transform = augs(input)
  pred_mask = make_prediction(input.image)
  inv_transform = transform.inverse()
  pred_mask_orig = inv_transform.apply_segmentation(pred_mask)
  ```
- **关键点自定义语义**(基于返回的 `transform` 自行决定左右眼映射):
  ```python
  transform = augs(input)
  keypoints_xy = transform.apply_coords(keypoints_xy)
  transforms = T.TransformList([transform]).transforms
  do_hflip = sum(isinstance(t, T.HFlipTransform) for t in transforms) % 2 == 1
  if do_hflip:
      keypoints_xy = keypoints_xy[flip_indices_mapping]
  ```
- **逐步骤关键点 visibility 更新**:
  ```python
  for t in transform.transforms:
      keypoints_xy = t.apply_coords(keypoints_xy)
      visibility &= (keypoints_xy >= [0, 0] & keypoints_xy <= [W, H]).all(axis=1)
  ```
- **通过默认 DataLoader 间接启用**:参见 [data_loading](data_loading.md) 教程中的"用户自定义增强列表"用法 (具体命令行/参数在原文未涉及)。
