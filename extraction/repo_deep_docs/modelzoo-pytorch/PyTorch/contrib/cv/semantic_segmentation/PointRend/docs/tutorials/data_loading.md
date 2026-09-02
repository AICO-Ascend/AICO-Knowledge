# Dataloader

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/data_loading.md

# 一体化深度解读:Dataloader 教程文档

## 【定位】

这篇文档解决 Detectron2 框架中**数据加载机制的理解与定制问题**——既解释内置 `build_detection_{train,test}_loader` 的工作原理,也说明当默认行为不满足需求时如何编写并接入自定义 dataloader/mapper,从而将原始数据集字典转换为模型可直接消费的输入。

---

## 【技术要点】

1. **核心入口函数**:Detectron2 提供 `build_detection_train_loader` 与 `build_detection_test_loader` 两个函数,接收一个 `cfg` 配置,从已注册的(registered)数据集构造一个默认 dataloader。
2. **数据集轻量表示**:函数第一步按名称(如 `"coco_2017_train"`)加载数据集,产出 `list[dict]`,其图像**尚未读入内存**、**尚未应用随机增强**——是"轻量格式"。
3. **Mapper 映射机制**:每个 dict 由一个 mapper 函数处理,默认 mapper 为 `DatasetMapper`;用户可通过 `mapper=` 参数传入自定义函数。Mapper 的职责是把"轻量表示"转化为"模型可消费格式"(读图、随机增强、转 torch Tensor)。
4. **批处理与输出**:Mapper 输出被简单地以 `list` 形式组批(batch),批数据即为 dataloader 的输出,通常直接送入 `model.forward()`。
5. **mapper 输出格式约定**:Mapper 输出格式可任意,但必须被下游消费者(通常是模型)接受;默认 mapper 批处理后的格式遵循 `Use Models` 教程中的"default model input format"。
6. **更深定制**:若不仅修改 mapper,还要改**采样或组批逻辑**,则 `build_detection_train_loader` 不再适用,需自行实现一个产出模型可接受格式的 python iterator。

---

## 【关键机制与数据】

**工作流(原文按 4 步描述)**:

1. 加载已注册数据集 → 得到 `list[dict]`(轻量格式,无图、无增强)。(原文:"It takes the name of a registered dataset (e.g., 'coco_2017_train') and loads a `list[dict]` representing the dataset items in a lightweight format.")
2. 每个 dict 经 mapper 映射:
   - 用户可通过 `mapper=` 参数自定义映射函数,默认是 `DatasetMapper`。
   - mapper 读图、做随机增强、转 Tensor。(原文:"The role of the mapper is to transform the lightweight representation of a dataset item into a format that is ready for the model to consume (including, e.g., read images, perform random data augmentation and convert to torch Tensors).")
3. mapper 输出被简单组批为 `list`。(原文:"The outputs of the mapper are batched (simply into a list).")
4. 批数据 = dataloader 输出,通常即 `model.forward()` 的输入。(原文:"This batched data is the output of the data loader. Typically, it's also the input of `model.forward()`.")

**性能数据**:原文未给出任何性能数字、基准或时延指标。

---

## 【表格解读】

**原文无表格**。原文通过编号列表(1–4)叙述流水线步骤,以及两段代码示例展示 mapper 配置与最小化 mapper 实现,无参数表、对比表或配置表。

---

## 【公式解读】

**原文无公式**。无 LaTeX、无伪代码算法公式;mapper 的实现以 Python 代码片段呈现(见下文【使用方法】)。

---

## 【关联】

文档通过内部链接织出以下依赖/上下游关系:

- **上游数据源**:`./datasets.md`(数据集格式与注册机制)—— dataloader 第一步从已注册数据集读取 `list[dict]`,因此本文是 datasets 教程的下游消费者。
- **核心 API**:
  - `../modules/data.html#detectron2.data.build_detection_train_loader` —— 本文反复调用的两个入口函数。
  - `../modules/data.html#detectron2.data.DatasetMapper` —— 默认 mapper,以及"最小化 mapper 示例"中显式 import 与替代的目标。
- **下游契约**:
  - `./models.html#model-input-format` 与 `./models.md` —— mapper 批处理后的输出格式必须符合此处定义的"default model input format";dataloader 最终产物须被模型接受,这是契约的强制点。
- **训练循环对接**:
  - `../modules/engine.html#detectron2.engine.defaults.DefaultTrainer` —— 若使用默认训练器,可重写其 `build_{train,test}_loader` 方法接入自定义 dataloader。
  - `../../projects/DeepLab/train_net.py` —— 作为 DeepLab 项目中**实际重写 dataloader 的示例**,供用户参考。
- **辅助参考**:`../modules/data`(detectron2.data 完整 API 文档)——用于了解可用函数。

整体而言,本文处于"数据接口适配层":上承 datasets(数据原始形态),下接 models(消费格式),旁通 engine(DefaultTrainer)与 projects/DeepLab(实际用例)。

---

## 【使用方法】

### 1. 仅修改 mapper(最常见定制方式)

将自定义 mapper 通过 `mapper=` 注入,适用于调整图像预处理等场景。原文示例:把所有训练图 resize 到固定 800×800。

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper   # the default mapper
dataloader = build_detection_train_loader(cfg,
   mapper=DatasetMapper(cfg, is_train=True, augmentations=[
      T.Resize((800, 800))
   ]))
# use this dataloader instead of the default
```

### 2. 完全自定义 mapper 函数

若 `DatasetMapper` 参数不够用,可自己写 mapper。原文给出"minimal mapper"模板(关键参数与调用):

```python
from detectron2.data import detection_utils as utils
 # Show how to implement a minimal mapper, similar to the default DatasetMapper
def mapper(dataset_dict):
    dataset_dict = copy.deepcopy(dataset_dict)  # it will be modified by code below
    # can use other ways to read image
    image = utils.read_image(dataset_dict["file_name"], format="BGR")
    # See "Data Augmentation" tutorial for details usage
    auginput = T.AugInput(image)
    transform = T.Resize((800, 800))(auginput)
    image = torch.from_numpy(auginput.image.transpose(2, 0, 1))
    annos = [
        utils.transform_instance_annotations(annotation, [transform], image.shape[1:])
        for annotation in dataset_dict.pop("annotations")
    ]
    return {
       # create the format that the model expects
       "image": image,
       "instances": utils.annotations_to_instances(annos, image.shape[1:])
    }
dataloader = build_detection_train_loader(cfg, mapper=mapper)
```

原文关键调用注释:
- `utils.read_image(file_name, format="BGR")`:读取图像文件。
- `T.AugInput(image)` + `T.Resize((800,800))(auginput)`:建立增强输入并施加 Resize 增强。
- `torch.from_numpy(auginput.image.transpose(2, 0, 1))`:HWC→CHW 并转 torch Tensor。
- `utils.transform_instance_annotations(annotation, [transform], image.shape[1:])`:同步变换实例标注。
- `utils.annotations_to_instances(annos, image.shape[1:])`:标注列表 → `Instances` 对象。
- 返回字典至少含 `"image"` 与 `"instances"` 两键,以匹配模型输入格式。

### 3. 彻底替换 dataloader(改采样/组批逻辑时)

若需自定义采样或 batching,`build_detection_train_loader` 不可用;只需实现一个 python iterator,其产出符合 `./models.md` 中模型接受格式的数据。原文未给出具体示例代码。

### 4. 在 DefaultTrainer 中接入

若使用 [`DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer),可**重写其 `build_{train,test}_loader` 方法**来使用自定义 dataloader。具体范例见 DeepLab 项目的 [`train_net.py`](../../projects/DeepLab/train_net.py)。

### 5. 自写训练循环

原文仅指出:"If you write your own training loop, you can plug in your data loader easily.",**未涉及具体配置项或命令**——属于一般性指引,无额外参数/CLI 开关。

### 配置项与命令行

原文未涉及任何具体 yaml 配置项(如 `cfg.DATALOADER.*`)或命令行参数;相关字段需查阅 `../modules/data.html#detectron2.data` 中 `build_detection_{train,test}_loader` 的 API 文档方可获得。
