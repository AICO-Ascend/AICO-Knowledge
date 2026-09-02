# Use Dataloaders

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/data_loading.md

# 深度解读:Detectron2 数据加载器 (Use Dataloaders)

## 【定位】

本篇文档解决的是 **Detectron2 中数据从数据集(dataset)送入模型(model) 的整个加载、转换、批量化流程的认知与定制问题**——既要说明内置 `build_detection_{train,test}_loader` 的四步工作机制,又要指导用户如何在不重写一切的前提下定制 mapper、以及在更极端情况下如何彻底替换 dataloader。

---

## 【技术要点】

1. **核心入口函数**: Detectron2 内置 `build_detection_train_loader` 与 `build_detection_test_loader` 两个函数,从给定 `cfg` 创建默认数据加载器。

2. **数据集输入形式**: 函数接受已注册的 dataset 名字(如示例 `"coco_2017_train"`),内部读出 `list[dict]` 这种**轻量级**数据项——此时图像尚未读入内存,数据增强也未应用。

3. **Mapper 机制**: 每条 dict 都由一个 mapper 函数映射;可通过 `mapper=` 参数替换;**默认 mapper 为 `DatasetMapper`**;mapper 的职责是把轻量级 dict 转成模型可消费的格式(读图、做随机增强、转 torch Tensor);输出格式任意,只要消费者(模型)接受即可。

4. **批量化与最终交付**: mapper 输出**仅以 list 形式简单 batch** 后即作为 dataloader 的输出,通常直接作为 `model.forward()` 的输入。

5. **轻量级自定义(改 mapper)**: 通过 `DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))])` 这种传参方式就能给训练集统一 resize 到 (800, 800);若还不够,可自定义 mapper 函数(原文给出最小 mapper 模板)。

6. **重度自定义(改 sampler/batcher)**: 当不仅想换 mapper,而是想换采样或 batch 逻辑时,`build_detection_train_loader` 不再够用,**用户需自写一个产出模型所接受格式的 python iterator**;若用 `DefaultTrainer`,可覆盖其 `build_{train,test}_loader` 方法,参考 `projects/DensePose/train_net.py`。

---

## 【关键机制与数据】

### 工作原理(四步流水线,原文描述)

1. **加载 dataset dict**:`build_detection_{train,test}_loader` 接收注册名(如 `"coco_2017_train"`)→ 加载一个 `list[dict]`(轻量级,不含图像张量、未做增强)。dataset 格式与注册机制见 [datasets.md](./datasets.md)。

2. **Mapper 映射**:
   - 通过 `mapper=` 参数可自定义;默认 mapper 为 `DatasetMapper`(原文: `../modules/data.html#detectron2.data.DatasetMapper`)。
   - mapper 输出格式任意,只要消费者(模型)接受;**默认 mapper 输出的 batch 形式遵循 "default model input format"**(原文: `./models.html#model-input-format`)。
   - mapper 的本质动作:**读图、执行随机增强、转 torch Tensor**,把轻量 dict → 模型可直接消费的形式。

3. **批量化 (batching)**: mapper 输出"simply into a list"地拼成 batch。

4. **交付模型**: batch 即 dataloader 的输出,典型用法即 `model.forward()` 的输入。

### 自定义 mapper 的关键数据流(原文代码展示)

- **读图**: `utils.read_image(dataset_dict["file_name"], format="BGR")`(注意 format 是 `"BGR"`)。
- **几何变换**: `transform = T.Resize((800, 800)).get_transform(image)`(目标尺寸 `(800, 800)`)。
- **图转 Tensor**: `torch.from_numpy(transform.apply_image(image).transpose(2, 0, 1]))`——`transpose(2, 0, 1)` 即 HWC → CHW 的轴重排。
- **标注同步变换**: 用 `utils.transform_instance_annotations(annotation, [transform], image.shape[1:])` 对每条 annotation 应用同一 transform,`image.shape[1:]` 传入 (H, W) 作为图像新尺寸。
- **标注 → Instances**: `utils.annotations_to_instances(annos, image.shape[1:])`。
- **输出 dict 键**: `"image"` + `"instances"`(需符合模型所期望的格式)。

> 原文: "If the arguments of the default `DatasetMapper` does not provide what you need, you may write a custom mapper function and use it instead"

### 默认 + 极简增强用法(原文代码)

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper
dataloader = build_detection_train_loader(cfg,
   mapper=DatasetMapper(cfg, is_train=True, augmentations=[
      T.Resize((800, 800))
   ]))
```

> 原文未提供任何性能数据(吞吐、时延、显存等),本文不臆造。

---

## 【表格解读】

**原文无表格。** 本文档为纯叙述 + 代码片段形态,未出现参数表、对比表、配置项表等结构化表格。

---

## 【公式解读】

**原文无公式。** 文档中仅含 Python 代码片段(`T.Resize((800, 800))`、`transpose(2, 0, 1)` 等数值常量)以及四步文字描述,**未出现 LaTeX 数学公式或伪代码公式块**。

---

## 【关联】

依据原文与文末链接,可梳理上下游模块依赖图:

- **上游 — 数据来源**: [datasets.md](./datasets.md)
  - 文档明确说明"轻量级 dict 来自 datasets 流程",所以 dataloader 强依赖 dataset 注册机制。

- **并行 — 数据格式契约**: [./models.md](./models.md)、[./models.html#model-input-format](./models.html#model-input-format)
  - mapper 的输出"as long as it is accepted by the consumer of this data loader (usually the model)";dataloader 自写时也要求产出"the format that the model accepts"——**mapper 输出格式 ↔ 模型输入格式 是一对契约**,两边约定在 models 文档中描述。

- **核心 API**:
  - [../modules/data.html#detectron2.data.build_detection_train_loader](../modules/data.html#detectron2.data.build_detection_train_loader)——本篇主讲的入口函数。
  - [../modules/data.html#detectron2.data.DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper)——默认 mapper,也是用户最常见的定制入口。
  - [../modules/data](../modules/data)——推荐的 API 参考总入口,文档结尾建议用户查阅以了解更详细接口。

- **下游 — 训练循环接入**: [../modules/engine.html#detectron2.engine.defaults.DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer)
  - 若用 `DefaultTrainer`,可通过覆盖其 `build_{train,test}_loader` 方法插入自定义 dataloader。

- **示例工程 (典型实践)**: [../../projects/DensePose/train_net.py](../../projects/DensePose/train_net.py)
  - 文档显式把它列为"覆盖 dataloader 的参考实现",它本身就是 DensePose 项目在自己训练循环里重写 dataloader 的范本。

**关系一句话**: datasets(数据源) → dataloader(本页) → 模型(models.md 规定的输入格式);训练侧由 `DefaultTrainer` 调用,定制时通过覆盖其 `build_{train,test}_loader` 接入,典型范例即 DensePose 项目。

---

## 【使用方法】

> 以下均来自原文,可直接照搬使用。

### ① 最小代价:用现有函数 + 自定义 mapper 增强

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper
dataloader = build_detection_train_loader(cfg,
   mapper=DatasetMapper(cfg, is_train=True, augmentations=[
      T.Resize((800, 800))
   ]))
```
> 原文: "if you want to resize all images to a fixed size for training, use"

### ② 中级:写一个最小自定义 mapper

```python
from detectron2.data import detection_utils as utils

def mapper(dataset_dict):
    dataset_dict = copy.deepcopy(dataset_dict)
    image = utils.read_image(dataset_dict["file_name"], format="BGR")
    transform = T.Resize((800, 800)).get_transform(image)
    image = torch.from_numpy(transform.apply_image(image).transpose(2, 0, 1))
    annos = [
        utils.transform_instance_annotations(annotation, [transform], image.shape[1:])
        for annotation in dataset_dict.pop("annotations")
    ]
    return {
       "image": image,
       "instances": utils.annotations_to_instances(annos, image.shape[1:])
    }

dataloader = build_detection_train_loader(cfg, mapper=mapper)
```
关键参数说明(原文):
- `format="BGR"` —— 读图色彩格式。
- `T.Resize((800, 800))` —— 几何增强目标尺寸。
- `transpose(2, 0, 1)` —— HWC → CHW 轴序,转 torch Tensor 前所需。
- `image.shape[1:]` —— (H, W),作为变换后图像尺寸传给 `transform_instance_annotations` / `annotations_to_instances`。
- 输出键 `"image"`、`"instances"` —— 需与模型期望对齐。

### ③ 重度自定义:换采样/批量化逻辑

> 原文: "If you want to change not only the mapper (e.g., in order to implement different sampling or batching logic), `build_detection_train_loader` won't work and you will need to write a different data loader. The data loader is simply a python iterator that produces [the format](./models.md) that the model accepts. You can implement it using any tools you like."

要点:
- **放弃** `build_detection_train_loader`。
- 自己写一个 python iterator,**输出严格遵循 `./models.md` 中规定的模型可接受格式**(原文链接 `./models.md`)。
- 实现工具不限。

### ④ 接入 DefaultTrainer

> 原文: "If you use `DefaultTrainer`, you can overwrite its `build_{train,test}_loader` method to use your own dataloader. See the [densepose dataloader](../../projects/DensePose/train_net.py) for an example."

- 覆盖对象:`DefaultTrainer` 上的 `build_train_loader` / `build_test_loader`。
- 参考实现:`projects/DensePose/train_net.py`。

### ⑤ 接入自定义训练循环

> 原文: "If you write your own training loop, you can plug in your data loader easily."

无特殊配置——只需保证 dataloader 输出的 batch 是模型 forward 接受的格式即可。

### 推荐查阅的 API 文档

> 原文: "it's recommended to check out [API documentation of detectron2.data](../modules/data) to learn more about the APIs of these functions."

- 入口:`../modules/data`。
- 重点关注:`build_detection_train_loader` 与 `DatasetMapper` 的接口签名、可选参数(原文未展开列表,需自行查阅 API 文档)。
