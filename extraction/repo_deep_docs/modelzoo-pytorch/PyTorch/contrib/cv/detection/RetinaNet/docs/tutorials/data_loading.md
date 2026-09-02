# Use Dataloaders

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/data_loading.md

# 一体化深度解读:Detectron2 Dataloader 使用指南

---

## 【定位】

本文档系统描述了 Detectron2 中**数据加载器 (Dataloader) 的工作机制与定制方法**——它从已注册的 dataset 中读取轻量化的 `list[dict]`,经由 mapper 转换为模型可直接消费的格式,再分批送入 `model.forward()`,文档同时给出了**自定义 mapper** 和**完全自定义 dataloader** 的两层级扩展路径。

---

## 【技术要点】

1. **核心入口函数**:Detectron2 提供 `build_detection_{train,test}_loader` 两个函数,从给定 config 构建默认 dataloader。
2. **四步管线流程**:(a) 从已注册数据集名 (如 `"coco_2017_train"`) 加载 `list[dict]` 轻量化表示 → (b) 经 mapper 函数逐项映射 → (c) 简单 list 批量化 → (d) 输出即 `model.forward()` 的输入。
3. **默认 Mapper**:使用 `DatasetMapper`;其职责是将轻量 dict (图片未加载、未做增强) 转为模型可消费格式 (读图、随机增强、转 torch Tensor)。
4. **自定义 Mapper (轻量定制)**:通过 `build_detection_train_loader(cfg, mapper=...)` 替换 mapper;例如传入 `DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))])` 即可将所有图像 resize 到 800×800。
5. **完全自定义 Mapper 函数**:接受 `dataset_dict`,内部 `copy.deepcopy`、用 `utils.read_image(format="BGR")` 读图、用 `T.Resize` 的 `get_transform`/ `apply_image` 做几何变换、`transform_instance_annotations` 同步变换标注,最终返回含 `"image"` (转置为 CHW 的 torch tensor) 与 `"instances"` (由 `annotations_to_instances` 生成) 的 dict。
6. **完全自定义 Dataloader**:当需要修改采样或批处理逻辑时,`build_detection_train_loader` 失效;此时 dataloader 仅需实现为**产出模型接受格式的 python iterator**,可使用任意工具。

---

## 【关键机制与数据】

### 工作原理 (原文描述的四步管线)

1. **加载轻量化 dict 列表**:从已注册数据集名 (例如 `"coco_2017_train"`) 读取,此时图片**尚未读入内存**,随机增强**尚未应用**。格式细节见 datasets 文档。
2. **Mapper 映射**:用户可通过 `mapper=` 参数自定义;默认 `DatasetMapper` 的输出(批量化后)遵循 default model input format。mapper 负责把轻量表示转为模型可消费格式。
3. **批量化 (batching)**:原文明确为 "simply into a list"——仅简单聚合成 list,无其他复杂合并。
4. **输出即模型输入**:dataloader 输出可直接作为 `model.forward()` 的输入。

### 性能/量化数据

**原文未涉及**具体的吞吐、显存、时延数字。

### 数据流示例 (来自代码块)

```python
# 入口:dataset_dict (轻量 dict, 含 "file_name"、"annotations" 等)
# 出口:含 "image" (CHW torch tensor)、"instances" 的 dict
dataloader → model.forward()
```

---

## 【表格解读】

**原文无表格。** 文档以纯流程描述 + 两段代码示例代替表格。

---

## 【公式解读】

**原文无公式。** 但可把第二段代码示例视为"最小 mapper"的形式化模板,各符号含义如下:

| 符号/调用 | 含义与作用 |
|---|---|
| `dataset_dict` | 输入的单样本轻量 dict(来自已注册数据集) |
| `copy.deepcopy(dataset_dict)` | 拷贝以避免污染原始数据(原文: "it will be modified by code below") |
| `utils.read_image(file_name, format="BGR")` | 按 BGR 通道顺序读图 |
| `T.Resize((800, 800)).get_transform(image)` | 基于图像构造 resize 几何变换对象 |
| `transform.apply_image(image)` | 把变换应用到图像像素 |
| `.transpose(2, 0, 1)` + `torch.from_numpy` | HWC → CHW 并转 torch tensor |
| `utils.transform_instance_annotations(anno, [transform], image_shape)` | 同步变换标注框等实例信息 |
| `utils.annotations_to_instances(annos, image_shape)` | 将标注列表聚合为 `Instances` 对象 |
| `return {"image": image, "instances": ...}` | 构造模型期望的输出格式 |

---

## 【关联】

按照文档语义树,Dataloader 模块与以下上下游紧密耦合:

- **上游 — 数据集层**:依赖 [datasets.md](./datasets.md),dataloader 从已注册的数据集 (如 `"coco_2017_train"`) 读取 `list[dict]`;数据集的注册与格式由该文档定义。
- **下游 — 模型层**:mapper 的输出批量化后必须符合 [model input format](./models.html#model-input-format) (默认),或由用户自定义模型约定的格式;见 [./models.md](./models.md)。
- **API 实现层**:核心 API 见 [detectron2.data 模块文档](../modules/data),其中 [`build_detection_train_loader`](../modules/data.html#detectron2.data.build_detection_train_loader) 与 [`DatasetMapper`](../modules/data.html#detectron2.data.DatasetMapper) 是两个最常被引用与扩展的对象。
- **训练引擎层**:若使用 [`DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer),可通过覆写其 `build_{train,test}_loader` 方法注入自定义 dataloader;**典型范例**:[DensePose 项目的 train_net.py](../../projects/DensePose/train_net.py) 展示了一个真实的自定义 dataloader 实现。
- **横向并列**:与 [datasets.md](./datasets.md)、[./models.md](./models.md) 构成 Detectron2 的"数据—模型"双子教程;数据增强相关的 `detectron2.data.transforms` 模块 (代码中 `T.Resize`) 是 mapper 的常用工具集。

---

## 【使用方法】

### 1. 使用默认 Dataloader

```python
from detectron2.data import build_detection_train_loader
dataloader = build_detection_train_loader(cfg, mapper=DatasetMapper(cfg, is_train=True))
```

### 2. 仅修改增强策略(轻量定制)

通过 `augmentations` 参数传入增强列表:

```python
import detectron2.data.transforms as T
dataloader = build_detection_train_loader(cfg,
   mapper=DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))]))
```

### 3. 替换为自定义 Mapper 函数

实现一个签名类似 `def mapper(dataset_dict) -> dict` 的函数,然后传入 `mapper=` 参数(原文完整示例见上节"公式解读")。

### 4. 完全自定义 Dataloader

当需要**不同的采样或 batching 逻辑**时,绕过 `build_detection_train_loader`,自行实现一个产出模型可接受格式的 python iterator(可使用 PyTorch `DataLoader`、自定义生成器等任何工具)。

### 5. 在 `DefaultTrainer` 中挂载自定义 Dataloader

覆写 [`DefaultTrainer.build_{train,test}_loader`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 方法;参考 [DensePose train_net.py](../../projects/DensePose/train_net.py)。

### 6. 自定义训练循环

若不使用 `DefaultTrainer`,直接在自己写的训练循环中实例化并迭代 dataloader,原文未涉及具体接入代码(因属自由实现范畴)。
