# Dataloader

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/data_loading.md

# CenterNet2 数据加载 (Dataloader) 教程深度解读

## 【定位】

这篇文档是 detectron2 / CenterNet2 的"数据加载 (Dataloader)"教程,系统性地解释**默认数据加载管线的工作原理**、**如何通过自定义 mapper 来定制数据加载行为**,以及**如何将自己实现的 dataloader 接入训练流程**,目标是在用户需要修改数据加载逻辑时,提供从理解原理到落地的完整路径。

---

## 【技术要点】

1. **数据加载器本质**:Dataloader 是为模型提供数据的组件,通常(但非必须)从 [datasets](./datasets.md) 读取原始信息,并将其处理为模型所需的格式。

2. **入口函数**:Detectron2 提供两个函数 `build_detection_{train,test}_loader` (详见 [detectron2.data.build_detection_train_loader](../modules/data.html#detectron2.data.build_detection_train_loader)),可从给定 config 创建默认 dataloader。

3. **四步工作流**:
   - 步骤 1:接收已注册的数据集名(如 `"coco_2017_train"`),加载为轻量级 `list[dict]`(此时图像尚未读入内存,随机增强尚未应用)。
   - 步骤 2:通过一个 mapper 函数对每个 dict 进行转换(默认 mapper 为 [DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper)),输出格式只要被模型接受即可;批量后符合 [Use Models](./models.html#model-input-format) 描述的默认输入格式。
   - 步骤 3:mapper 输出被简单组装为一个 list 作为 batch。
   - 步骤 4:该 batch 即 dataloader 输出,通常直接送入 `model.forward()`。

4. **自定义 mapper 的两种方式**:
   - **方式 A(参数化)**:在 `build_detection_{train,test}_loader(mapper=)` 中替换 mapper。典型用法是把 `DatasetMapper` 的 `augmentations` 换成自定义增强列表(原文示例 `T.Resize((800, 800))`)。
   - **方式 B(完全自定义)**:若默认 [DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper) 的参数不够用,可自行写一个 `mapper(dataset_dict)` 函数(原文给出一个最小示例,使用 `utils.read_image`、`T.AugInput`、`T.Resize`、`utils.transform_instance_annotations`、`utils.annotations_to_instances` 等 API)。

5. **重写整个 dataloader 的边界条件**:若不仅想改 mapper(例如想换 sampling 或 batching 逻辑),`build_detection_train_loader` 不再适用,需要自行实现一个"产生模型所接受格式的 python iterator",可使用任意工具实现。

6. **接入训练流程的两种方式**:
   - 使用 [DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 时,重写其 `build_{train,test}_loader` 方法(参考 [deeplab dataloader](../../projects/DeepLab/train_net.py))。
   - 自写训练循环时,直接插入自己的 dataloader 即可。

---

## 【关键机制与数据】

### 数据流(原文描述的逐阶段语义)

- **轻量 dict 阶段**:每个数据项只是元信息(file_name、annotations 等),**没有加载图像**,**没有应用随机增强**。
- **mapper 阶段**:承担"读图 + 随机增强 + 转换为 torch Tensor + (可选) 转换标注"的工作。原文明确写出 mapper 的职责包括:"read images, perform random data augmentation and convert to torch Tensors"。
- **batch 阶段**:仅"simply into a list",即不做额外 collation,只把 mapper 输出聚合成 list。
- **消费阶段**:通常直接作为 `model.forward()` 输入。

### 性能 / 资源特征(原文所述)

- 原文:`list[dict]` 是"lightweight format",不占内存,直到 mapper 阶段才真正读取图像。这意味着内存峰值由 mapper 内部处理决定,而非加载阶段。
- 原文未提供任何数值化的性能数据(吞吐、延迟、显存占用等),故以下数据项**原文未涉及**:每张图像 resize 后尺寸的批量上限、worker 数量、内存预算、IO 瓶颈数字等。

### mapper 最小示例的关键 API 语义(原文代码)

- `utils.read_image(dataset_dict["file_name"], format="BGR")`:按 BGR 顺序读取图像。
- `T.AugInput(image)` + `T.Resize((800, 800))(auginput)`:标准 AugInput 范式,得到 transform 与变换后图像。
- `image = torch.from_numpy(auginput.image.transpose(2, 0, 1))`:从 HWC 转 CHW 的 torch Tensor。
- `utils.transform_instance_annotations(annotation, [transform], image.shape[1:])`:同步变换实例标注。
- `utils.annotations_to_instances(annos, image.shape[1:])`:将标注列表汇总为 Instances 对象。
- 返回字典必须包含 `"image"` 与 `"instances"` 键,匹配模型所要求的输入格式。

---

## 【表格解读】

**原文无表格**。整篇文档以步骤描述 + 代码示例为主,未出现任何参数表、配置表或性能对比表。

---

## 【公式解读】

**原文无公式**。文档未给出任何数学公式或伪代码形式的数据变换表达式,所有逻辑均以自然语言步骤和 Python 代码呈现。

---

## 【关联】

依据文末提供的内部链接,可梳理出本教程在 detectron2 / CenterNet2 知识体系中的位置:

- **上游 / 数据源**:
  - [./datasets.md](./datasets.md):被多次引用,负责解释"已注册数据集的数据格式"以及注册机制,是 dataloader 步骤 1(`list[dict]` 形态)的来源。
- **下游 / 消费方**:
  - [./models.html#model-input-format](./models.html#model-input-format):被引用以说明 mapper 批量输出应当匹配"默认模型输入格式"。
  - [../modules/data.html#detectron2.data.build_detection_train_loader](../modules/data.html#detectron2.data.build_detection_train_loader):入口函数的 API 文档。
  - [../modules/data.html#detectron2.data.DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper):默认 mapper 的 API 文档,在文中共出现两次,分别是步骤 2 的"默认 mapper 是什么"与"如何用参数化方式自定义"。
- **横向辅助模块**:
  - [../modules/data](../modules/data):作者建议在完成自定义实现前,先查阅该模块的 API 文档以了解可用工具。
  - [../modules/engine.html#detectron2.engine.defaults.DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer):训练流程入口,本节说明如何通过重写 `build_{train,test}_loader` 接入自定义 dataloader。
- **跨项目示例**:
  - [../../projects/DeepLab/train_net.py](../../projects/DeepLab/train_net.py):作为"在 DefaultTrainer 中覆写 `build_{train,test}_loader` 来使用自定义 dataloader"的具体范例被引用。
- **未直接出现但语义相关**:
  - `./models.md`:指向"模型所接受的格式说明",在"完全重写 dataloader"小节中被再次引用,提示自定义 dataloader 的产出必须与此处描述的格式对齐。

---

## 【使用方法】

### 1. 使用默认 dataloader(原文未给出直接命令)

原文未给出"一行命令即可启动默认 dataloader"的写法;默认用法需通过 `DefaultTrainer` 在其内部调用 `build_detection_{train,test}_loader(cfg)`。**原文未涉及**具体启动命令或配置项字段名(如 `cfg.DATALOADER.NUM_WORKERS` 等均未在本文出现)。

### 2. 替换 augmentations 的最简自定义(原文示例)

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper   # the default mapper
dataloader = build_detection_train_loader(cfg,
   mapper=DatasetMapper(cfg, is_train=True, augmentations=[
      T.Resize((800, 800))
   ]))
# use this dataloader instead of the default
```

要点:`is_train=True` 决定是否启用训练相关的随机增强;`augmentations` 列表替换原 mapper 的增强流水线。

### 3. 完全自定义 mapper(原文示例)

```python
def mapper(dataset_dict):
    dataset_dict = copy.deepcopy(dataset_dict)        # 避免就地修改原 dict
    image = utils.read_image(dataset_dict["file_name"], format="BGR")
    auginput = T.AugInput(image)
    transform = T.Resize((800, 800))(auginput)
    image = torch.from_numpy(auginput.image.transpose(2, 0, 1))
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

关键约束:
- 必须 `deepcopy`,否则会污染上游 dataset dict。
- 返回字典至少包含 `"image"` 与 `"instances"` 两键,且语义需对齐 `./models.md` 的模型输入格式。
- `annotations` 通过 `pop` 消费掉,避免在 batch 中残留。

### 4. 替换整个 dataloader(原文描述)

当要修改 sampling 或 batching 逻辑时,需自己实现一个 python iterator,其产出格式匹配 `./models.md`。**原文未涉及**具体实现模板或性能调优配置项。

### 5. 接入训练流程(原文描述)

- 在 [DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 中,覆写其 `build_{train,test}_loader` 方法,使其返回自己的 dataloader。参考示例:[../../projects/DeepLab/train_net.py](../../projects/DeepLab/train_net.py)。
- 若自行实现训练循环,只需把自定义 dataloader 直接作为数据源使用,无需任何适配层。**原文未涉及**具体训练循环代码或 config 字段写法。
