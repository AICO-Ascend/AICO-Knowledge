# Use Dataloaders

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/data_loading.md

# 一体化深度解读:Use Dataloaders

## 【定位】
本文档是 detectron2 中关于**数据加载器（Dataloader）**的使用指南,系统性地说明内置数据加载管线的工作原理、如何通过自定义 mapper 实现定制化数据处理、以及如何将自定义数据加载器接入训练流程,从而将原始数据集条目转换为模型可直接消费的张量格式。

---

## 【技术要点】

1. **两个核心入口函数**:Detectron2 提供 `build_detection_train_loader` 与 `build_detection_test_loader`,作为从给定 config 创建默认数据加载器的标准接口;二者都接受 `mapper` 参数以注入自定义映射逻辑。
2. **Mapper 是可定制的关键钩子**:默认 mapper 是 `DatasetMapper`,其职责是把"轻量级"的 `list[dict]` 数据条目(图像尚未读入内存、未做数据增强)转换为模型可直接消费的格式(读取图像、施加随机增强、转 torch Tensor);自定义只需传入 `mapper=` 参数即可。
3. **典型自定义方式——修改 augmentations**:通过 `DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))])` 即可将所有图像缩放到固定尺寸 (800, 800),无需重写整个 mapper。
4. **典型自定义方式——完全重写 mapper**:当默认 mapper 参数不够用时,可自定义函数签名 `def mapper(dataset_dict)`,流程为:`utils.read_image(format="BGR")` → `T.Resize((800, 800)).get_transform(image)` → `transform.apply_image()` → `torch.from_numpy(...transpose(2, 0, 1))` → `utils.transform_instance_annotations(annotation, [transform], image.shape[1:])` → `utils.annotations_to_instances(annos, image.shape[1:])`,最终输出包含 `"image"` 与 `"instances"` 两个键。
5. **超越 mapper 的改造边界**:若需修改采样(sampling)或批处理(batching)逻辑,`build_detection_train_loader` 不再适用,需要写一个完全自定义的、产出"模型可接受格式"的 Python 迭代器。
6. **接入训练循环的标准做法**:若使用 `DefaultTrainer`,覆盖其 `build_{train,test}_loader` 方法即可替换数据加载器;若自写训练循环,直接接入自定义 loader 即可。

---

## 【关键机制与数据】

**内置数据加载管线的工作流程(原文分四步)**:

1. **轻量级数据加载**:函数接受已注册的 dataset 名(如 `"coco_2017_train"`),加载出 `list[dict]`,代表数据条目;此时**图像尚未读入内存,随机增强尚未施加**(原文:"images are not loaded into memory, random augmentations have not been applied, etc.")。
2. **Mapper 映射**:对每条 dict 调用 mapper;输出格式可任意,只要与数据加载器的消费者(通常是模型)所接受的格式一致;默认 mapper 批量化(batch)后的输出遵循默认模型输入格式(原文:"The outputs of the default mapper, after batching, follow the default model input format documented in [Use Models]")。
3. **批量化**:Mapper 的输出被简单地 batch 成 list。
4. **交付给模型**:该 batch 数据即为 `model.forward()` 的输入。

**自定义 mapper 的数据流(原文代码)**:

- **读取**:`utils.read_image(dataset_dict["file_name"], format="BGR")` 读入原始图像。
- **几何变换**:`T.Resize((800, 800)).get_transform(image)` 生成 transform 对象,然后 `transform.apply_image(image)` 对图像应用几何变换。
- **通道轴换位**:`.transpose(2, 0, 1)` 将 HWC 转为 CHW,再用 `torch.from_numpy` 转为 Tensor。
- **标注同步变换**:`utils.transform_instance_annotations(annotation, [transform], image.shape[1:])` 对每条 annotation 做与图像同步的几何变换,`image.shape[1:]` 提供 `(H, W)` 形状信息。
- **实例对象化**:`utils.annotations_to_instances(annos, image.shape[1:])` 将变换后的标注列表转为 `Instances` 对象。
- **深拷贝**:`dataset_dict = copy.deepcopy(dataset_dict)` 避免对原始数据条目的副作用(原文注释:"it will be modified by code below")。

**性能数据**:原文未提供任何性能数字(吞吐量/延迟/显存占用等)。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

(全文仅包含 Python 代码片段与流程性叙述,未出现 LaTeX 公式或伪代码形式的数学表达式。)

---

## 【关联】

本文档处于 detectron2 数据流管线的"中段",围绕 mapper 与 dataloader 的扩展点,与上下游多个模块紧密耦合:

- **上游 — 数据集定义**:[datasets.md](./datasets.md) 描述数据集条目 `list[dict]` 的格式与注册机制;mapper 消费的正是这种"轻量级"格式,图像文件通过 `file_name` 字段按需读取。
- **下游 — 模型输入契约**:[./models.html#model-input-format](./models.html#model-input-format) 定义 mapper 输出经批量化后必须遵循的"默认模型输入格式";自定义 mapper 的返回 dict(如示例中的 `{"image": ..., "instances": ...}`)必须与该契约一致。
- **横切 — API 参考**:[../modules/data](../modules/data) 是 `detectron2.data` 的 API 总目录,涵盖 `build_detection_train_loader`、`DatasetMapper`、`read_image`、`transform_instance_annotations`、`annotations_to_instances` 等所有相关接口。
- **训练集成**:[../modules/engine.html#detectron2.engine.defaults.DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 提供了 `build_{train,test}_loader` 可被覆盖的标准训练器,本文档指明的"用自定义 loader 替换默认 loader"的入口就在此处。
- **实战示例**:[../../projects/DensePose/train_net.py](../../projects/DensePose/train_net.py) 给出了一个完整示例,展示如何在 `DefaultTrainer` 子类中覆盖 `build_{train,test}_loader` 来接入项目专属的数据加载逻辑。
- **并行参考**:[./models.md](./models.md) 与 [../modules/data.html#detectron2.data.DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper) 也在文末反复链接出现,用于回查 mapper 输出格式与默认 mapper 实现细节。

整体数据流可概括为:**原始数据集条目 (`list[dict]`,见 datasets.md) → mapper (默认 `DatasetMapper` 或自定义) → 批量化 list → `model.forward()` 输入 (见 models.md) → `DefaultTrainer` 调用入口**。

---

## 【使用方法】

**1. 使用默认数据加载器(无侵入)**:
调用 `build_detection_train_loader(cfg)` 或 `build_detection_test_loader(cfg)`,cfg 中需指定已注册的 dataset 名(如 `"coco_2017_train"`)。

**2. 仅替换增强策略(推荐轻量定制)**:
```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper
dataloader = build_detection_train_loader(
    cfg,
    mapper=DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))])
)
```
**3. 完全自定义 mapper(中等定制)**:
实现 `def mapper(dataset_dict)` 函数(参见原文代码),内部使用 `detectron2.data.detection_utils` 与 `detectron2.data.transforms` 完成读图、增强、格式转换;通过 `build_detection_train_loader(cfg, mapper=mapper)` 注入。**注意**:函数内必须 `copy.deepcopy(dataset_dict)` 以避免修改上游数据。

**4. 完全自定义数据加载器(深度定制)**:
当需要不同采样或 batching 策略时,`build_detection_train_loader` 不再适用,需实现一个产出"模型可接受格式"的 Python 迭代器;若使用 `DefaultTrainer`,覆盖其 `build_{train,test}_loader` 方法;若自写训练循环,直接 plug in 即可。

**配置项/命令行参数**:本文档未涉及具体 YAML config 字段或 CLI 命令的写法,均为 Python API 层级的使用说明(原文未涉及)。
