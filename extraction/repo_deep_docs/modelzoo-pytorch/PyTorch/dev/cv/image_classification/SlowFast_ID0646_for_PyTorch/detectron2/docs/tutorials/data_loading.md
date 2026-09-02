# Dataloader

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/data_loading.md

# Detectron2 Dataloader 文档一体化深度解读

## 【定位】
本文档系统阐述 Detectron2 中**Dataloader（数据加载器）组件**的工作机制、自定义扩展方法及与训练框架的集成方式,定位为面向开发者的数据加载管线指南。

---

## 【技术要点】

核心机制分条如下:

1. **Dataloader 的本质**:为模型提供数据的组件,通常从 `datasets` 读取原始信息并加工为模型所需格式。
2. **两个核心构建函数**:Detectron2 提供 `build_detection_train_loader` 与 `build_detection_test_loader`,根据给定的 config 创建默认数据加载器。
3. **四步数据流管线**:`取注册数据集名 → 加载 list[dict]（轻量格式） → mapper 函数映射 → 简单 batch 为 list → 输出到 model.forward()`。
4. **默认 Mapper**:内置 `dataset_mapper` 为 [DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper);Mapper 负责读取图像、执行随机数据增强、转换为 torch Tensors。
5. **Mapper 可自定义**:通过 `build_detection_{train,test}_loader(mapper=...)` 注入自定义 mapper;原文档示例采用 **`T.Resize((800, 800))`** 将图像统一缩放到 800×800。
6. **完全自定义 DataLoader**:若需修改采样或 batch 逻辑,需自写一个**返回符合模型接受格式的 Python 迭代器**。

---

## 【关键机制与数据】

### 数据流（原文 "How the Existing Dataloader Works" 章节明确描述）

| 阶段 | 操作 | 输出 / 说明（原文表述） |
|------|------|------------------------|
| 1 | 接收**已注册数据集名**（如 `"coco_2017_train"`） | 加载为 `list[dict]`,**图像尚未读入内存,随机增强尚未应用** |
| 2 | Mapper 映射每条 dict | 读取图像、随机数据增强、转为 torch Tensors;输出格式可任意,但须被下游消费者（通常是模型）接受 |
| 3 | Batch 合并 | 简单合并为 `list` |
| 4 | 输出 | 即 `model.forward()` 的输入 |

### 自定义 Mapper 的关键 API（原文代码示例摘录）

原文给出了两种自定义 mapper 的写法:

**(a) 复用默认 `DatasetMapper`,仅修改增强:**

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper
dataloader = build_detection_train_loader(cfg,
   mapper=DatasetMapper(cfg, is_train=True, augmentations=[
      T.Resize((800, 800))   # 原文:resize to (800, 800)
   ]))
```

**(b) 手写最小化 mapper（原文逐字保留）:**

```python
from detectron2.data import detection_utils as utils
def mapper(dataset_dict):
    dataset_dict = copy.deepcopy(dataset_dict)
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

### 性能 / 数据相关数字

**原文未涉及性能数据、benchmark 数字或吞吐量指标**;唯一具体数值是 `T.Resize((800, 800))` 中的 **800×800**,这是示例中的图像目标尺寸,而非性能参数。

---

## 【表格解读】

**原文无表格。**

原文通过编号列表（1–4）和代码块描述机制,未提供任何对比表、参数表或配置表。

---

## 【公式解读】

**原文无公式。**

文档未涉及任何数学公式、LaTeX 表达式或伪代码算法;数据流通过自然语言编号列表描述。

---

## 【关联】

本文档在 Detectron2 体系中的上下游关系如下:

### 上游（数据来源）
- **`./datasets.md`**（×2 次链接）:解释数据集注册与 `list[dict]` 轻量格式,本文 Step 1 直接消费其输出。

### 中游（本文档自身）
- **`build_detection_train_loader` / `build_detection_test_loader`**（`../modules/data.html#detectron2.data.build_detection_train_loader`）:本文档核心解释对象。
- **`DatasetMapper`**（`../modules/data.html#detectron2.data.DatasetMapper`,×2 次链接）:默认 mapper;自定义 mapper 的对照基线。
- **`detectron2.data` API 文档**（`../modules/data`）:推荐进一步查阅 API 细节。

### 下游（消费方）
- **`./models.html#model-input-format`** 与 **`./models.md`**:定义 mapper 输出经 batch 后必须遵循的**模型输入格式**——本文档 Step 2 强调"只要被消费者接受即可"。
- **`../modules/engine.html#detectron2.engine.defaults.DefaultTrainer`**:`DefaultTrainer` 提供 `build_{train,test}_loader` 方法,可被覆盖以接入自定义 dataloader。

### 参考实现
- **`../../projects/DeepLab/train_net.py`**（DeepLab 项目的训练脚本）:官方给出的**自定义 dataloader 集成示例**,供用户参考 `DefaultTrainer` 子类化写法。

---

## 【使用方法】

### 方式一:复用默认 mapper,仅修改增强（原文:第一段代码块）
适用场景:**多数自定义需求**（如统一 resize、改 color jitter 等）。

```python
dataloader = build_detection_train_loader(
    cfg,
    mapper=DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))])
)
```

### 方式二:自定义 mapper 函数（原文:第二段代码块）
适用场景:**默认 `DatasetMapper` 参数无法满足需求时**。要求自定义函数读取图像、调用 `T.AugInput` + transform、`utils.transform_instance_annotations` 处理标注、用 `utils.annotations_to_instances` 构造 `instances` 字段,返回模型可消费的 dict;再通过 `build_detection_train_loader(cfg, mapper=mapper)` 注入。

### 方式三:完全自写 dataloader
适用场景:**采样或 batching 逻辑需彻底改动**。原文明确:`build_detection_train_loader won't work and you will need to write a different data loader`,其本质为**返回符合 `./models.md` 格式的 Python 迭代器**,可用任意工具实现。

### 方式四:接入 `DefaultTrainer`（原文:"Use a Custom Dataloader" 章节）
适用场景:使用 `DefaultTrainer` 时希望接入自定义 dataloader。
- 操作:**重写 `build_{train,test}_loader` 方法**;
- 参考实现:[`../../projects/DeepLab/train_net.py`](../../projects/DeepLab/train_net.py);
- 自写训练循环者:可直接将 dataloader 接入训练循环。

### 原文未涉及的内容
- **配置文件层面的配置项 / YAML 字段名**（本文档未列举 cfg 内部键值）。
- **命令行启用方式**（如 `python train_net.py --custom-dataloader ...`）。
- **性能调优参数**（如 `num_workers`、`batch_size` 等）—— 原文未涉及。
