# Use Dataloaders

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/data_loading.md

# 《Use Dataloaders》一篇深度解读

## 【定位】
这篇文档是 Detectron2 数据加载子系统的官方使用教程,核心回答两个问题:**Detectron2 默认的 Dataloader 是如何把"原始数据集条目"转成"模型可消费输入"的**,以及**用户如何在不改训练循环的前提下,替换 mapper 或完全自定义 Dataloader 以适配自定义变换、采样或批处理逻辑**。

---

## 【技术要点】

1. **两个核心入口函数**:Detectron2 提供 `build_detection_train_loader` 与 `build_detection_test_loader`,通过传入已注册的 dataset 名称(如 `"coco_2017_train"`)配合 config,自动构建默认数据加载器。

2. **四步默认管线**(原文编号):
   - 步骤 1:加载 `list[dict]` 形式的"轻量级数据集条目"(图像未读入内存、未做随机增强);
   - 步骤 2:由"mapper"函数把每个 dict 转换为模型可消费格式(默认 mapper 为 `DatasetMapper`,负责读图、做随机增强、转 torch Tensor);
   - 步骤 3:对 mapper 输出做简单 batching(直接列表化);
   - 步骤 4:批数据即为 Dataloader 输出,通常直接送入 `model.forward()`。

3. **Mapper 的可替换性**:用户可通过 `build_detection_{train,test}_loader(mapper=...)` 参数注入自定义 mapper;mapper 的输出格式"只要被下游消费者(通常是模型)接受即可,可以是任意格式"。

4. **典型自定义方式一——仅替换 augmentations**:利用默认 `DatasetMapper` 加 `augmentations` 列表,例如把训练图像统一缩放到 `(800, 800)`。

5. **典型自定义方式二——完全自写 mapper 函数**:手动 `copy.deepcopy(dataset_dict)` → `utils.read_image(...)` → 构造 transform → `transform.apply_image` + numpy→torch 转换(HWC→CHW via `transpose(2, 0, 1)`)→ `utils.transform_instance_annotations` 处理标注 → `utils.annotations_to_instances` 生成 `instances` 字段,产出 `{"image": ..., "instances": ...}`。

6. **更深度自定义——自写 Dataloader**:若要改采样/批处理逻辑,`build_detection_train_loader` 不够用,需自写一个 Python 迭代器,产出符合 [model 输入格式](./models.md) 的数据;并通过覆写 `DefaultTrainer` 的 `build_{train,test}_loader` 方法接入训练循环(参考 DensePose 的 `train_net.py`)。

---

## 【关键机制与数据】

### 工作原理/数据流(基于原文描述,逐条标注)

> 原文:"It takes the name of a registered dataset (e.g., 'coco_2017_train') and loads a `list[dict]` representing the dataset items in a lightweight format."

- **数据形态起点**:`list[dict]`,每项是"轻量级数据集条目"。注意原文明确指出此时"images are not loaded into memory, random augmentations have not been applied"(图像未读入内存、随机增强尚未施加)。

> 原文:"The role of the mapper is to transform the lightweight representation of a dataset item into a format that is ready for the model to consume (including, e.g., read images, perform random data augmentation and convert to torch Tensors)."

- **Mapper 的核心职责三件套**(原文列举):读图、执行随机数据增强、转换为 torch Tensor。

> 原文:"The outputs of the mapper are batched (simply into a list)."

- **Batching 策略**(原文):无复杂 collate_fn,mapper 输出被简单地"装进 list"组成 batch。

> 原文:"This batched data is the output of the data loader. Typically, it's also the input of `model.forward()`."

- **数据出口**:Dataloader 产出 = `model.forward()` 的输入(典型场景)。

### 性能数据
**原文未涉及任何性能/吞吐数字。**

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

(原文 mapper 示例中出现的 `transpose(2, 0, 1)` 是 NumPy/PyTorch 的轴置换操作符,属于代码语法而非数学公式;故不计入公式解读。)

---

## 【关联】

本教程在 Detectron2 整体文档体系中处于"训练链路的数据上游"位置,关联如下(均以原文内链为据):

| 关联模块 | 关系性质 | 原文描述锚点 |
|---|---|---|
| [datasets.md](./datasets.md) / [datasets](datasets.md) | **上游——数据来源** | mapper 接收的"lightweight representation"由 registered dataset 产生;原文:"Details about the dataset format and dataset registration can be found in [datasets](./datasets.md)." |
| [build_detection_{train,test}_loader](../modules/data.html#detectron2.data.build_detection_train_loader) | **核心 API** | 原文:"Detectron2 provides two functions ... that create a default data loader from a given config." |
| [DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper) | **默认 mapper 实现** | 原文:"The default mapper is DatasetMapper." 自定义 mapper 例子中 `from detectron2.data import DatasetMapper` |
| [./models.html#model-input-format](./models.html#model-input-format) 与 [./models.md](./models.md) | **下游——消费格式约定** | 原文:"The outputs of the default mapper, after batching, follow the default model input format documented in [Use Models](./models.html#model-input-format)." 自写 dataloader 也需遵循 `./models.md` 格式 |
| [../modules/data](../modules/data) | **API 参考索引** | 原文:"check out [API documentation of detectron2.data](../modules/data) to learn more about the APIs" |
| [DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) | **训练循环承载点** | 原文:"If you use DefaultTrainer, you can overwrite its `build_{train,test}_loader` method to use your own dataloader." |
| [../../projects/DensePose/train_net.py](../../projects/DensePose/train_net.py) | **工程范例** | 原文:"See the [densepose dataloader] ... for an example." 展示如何注入自定义 dataloader 到 DefaultTrainer |

**整体数据流链(按文档语义顺序)**:`Registered Dataset Name → list[dict] (轻量条目) → Mapper (读图+增强+转 Tensor) → list (batch) → model.forward()`。

---

## 【使用方法】

### 1. 使用默认 Dataloader(原文未给出完整调用语句,但描述了接口)

```python
# 原文隐含用法:传入 cfg,自动构建
dataloader = build_detection_train_loader(cfg)
dataloader = build_detection_test_loader(cfg)
```

### 2. 仅替换 augmentations(原文直接给出)

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper   # the default mapper

dataloader = build_detection_train_loader(
    cfg,
    mapper=DatasetMapper(cfg, is_train=True, augmentations=[
        T.Resize((800, 800))
    ])
)
```
**关键参数**(原文):
- `is_train=True`:启用训练分支(随机增强);
- `augmentations=[T.Resize((800, 800))]`:增广列表,本例把图统一缩放到 800×800。

### 3. 完全自写 mapper(原文直接给出)

```python
from detectron2.data import detection_utils as utils
import copy
import torch
import detectron2.data.transforms as T

def mapper(dataset_dict):
    dataset_dict = copy.deepcopy(dataset_dict)  # it will be modified by code below
    # can use other ways to read image
    image = utils.read_image(dataset_dict["file_name"], format="BGR")
    # can use other augmentations
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
**实现要点**(逐条对应原文注释):
- `copy.deepcopy`:避免污染原始 dict(原文:"it will be modified by code below");
- `utils.read_image(..., format="BGR")`:OpenCV 风格读图;
- `transform.apply_image(...).transpose(2, 0, 1)`:把 HWC 图像转成 CHW Tensor;
- `utils.transform_instance_annotations`:把标注框同步做几何变换;
- `utils.annotations_to_instances`:把标注列表转成 Detectron2 的 `Instances` 对象。

### 4. 接入自定义 Dataloader 到训练流程

- **使用 `DefaultTrainer` 的场景**(原文):"overwrite its `build_{train,test}_loader` method to use your own dataloader",参考 [`../../projects/DensePose/train_net.py`](../../projects/DensePose/train_net.py)。
- **自写训练循环的场景**(原文):"you can plug in your data loader easily",无特定接口约束。

### 5. 工具扩展建议(原文)
"it's recommended to check out [API documentation of detectron2.data](../modules/data) to learn more about the APIs of these functions."
