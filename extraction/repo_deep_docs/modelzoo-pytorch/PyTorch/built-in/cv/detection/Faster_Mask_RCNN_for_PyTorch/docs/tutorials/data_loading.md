# Use Dataloaders

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/data_loading.md

# 「Use Dataloaders」深度解读

## 【定位】
本篇文档系统讲解 Detectron2 内置数据加载流水线的工作原理、mapper 机制,以及如何在 `DefaultTrainer` 框架内替换或完全自定义 dataloader,解决"如何把原始数据集转换为模型可消费的 batch"这一核心问题。

---

## 【技术要点】

1. **两个核心入口函数**:`build_detection_train_loader` 与 `build_detection_test_loader`,根据给定的 config 创建默认 dataloader。
2. **四步处理流水线**:
   - ① 加载已注册的 dataset(名称形如 `"coco_2017_train"`),得到一个轻量化的 `list[dict]`,此时图片尚未读入内存,随机增强也未应用;
   - ② 通过 mapper 函数把每个 dict 转换为模型可消费的格式(默认 mapper 为 `DatasetMapper`);
   - ③ 将 mapper 输出直接 list 化 batch;
   - ④ 该 batch 即 dataloader 的输出,通常直接喂入 `model.forward()`。
3. **Mapper 是扩展点**:可通过 `build_detection_{train,test}_loader(mapper=)` 传入自定义 mapper;mapper 的输出格式只要被下游 model 接受即可,默认输出格式见 `Use Models` 文档。
4. **最小自定义 mapper 示例关键动作**:`utils.read_image` 读取图片 → `T.Resize((800, 800)).get_transform(image)` 获得 transform → `torch.from_numpy(... .transpose(2, 0, 1))` 转 Tensor → `utils.transform_instance_annotations` 同步变换标注 → `utils.annotations_to_instances` 转为 `Instances` 对象,最终输出 `{"image": ..., "instances": ...}`。
5. **使用默认 mapper 仅替换增强的写法**:通过 `DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))])` 即可注入增强。
6. **自定义 dataloader 的边界条件**:仅换 mapper 用 `build_detection_train_loader(mapper=)`;但若要改 sampling/batching 逻辑,需自写完整 dataloader——只要实现为产出 `[the format](./models.md)` 的 python iterator 即可,工具自选。

---

## 【关键机制与数据】

**工作原理/数据流**:
- 原文明确强调:dataset item 列表是**轻量化格式**,图片不入内存、随机增强未应用;mapper 负责把这种轻量化表示变换为模型可直接消费的张量化样本。
- 原文关于 batch 步骤的描述:**"The outputs of the mapper are batched (simply into a list)."** ——即 batch 就是朴素 list 化,未做特殊 padding/collate。
- mapper 至少承担的变换:读图、执行随机数据增强、转 torch Tensor;若需自定义变换,通常先考虑自定义 mapper。
- 自定义 mapper 范例中,文档显式把 `dataset_dict = copy.deepcopy(dataset_dict)` 写为第一步,提示后续代码会修改该 dict(避免污染原始数据)。
- 文档示例所给的 resize 目标尺寸:`(800, 800)`。
- 标注同步变换 API:`utils.transform_instance_annotations(annotation, [transform], image.shape[1:])`。
- 生成模型输入实例 API:`utils.annotations_to_instances(annos, image.shape[1:])`。

**性能数据**:原文未提供任何性能数字(吞吐量/加速比等),不做臆造。

---

## 【表格解读】
**原文无表格**。

---

## 【公式解读】
**原文无公式**。

---

## 【关联】

按文档内链/语义梳理的上下游关系:

| 关联对象 | 关系性质 | 在本文中的作用 |
|---|---|---|
| [datasets.md](datasets.md) / [./datasets.md](./datasets.md) | 数据源头 | dataloader 从已注册的 dataset 名(如 `"coco_2017_train"`)读取轻量化 dict 列表;数据集格式与注册详见该页 |
| [`detectron2.data.build_detection_train_loader`](../modules/data.html#detectron2.data.build_detection_train_loader) | API 入口 | 构造默认 train/test loader 的工厂函数,支持 `mapper=` 注入自定义 mapper |
| [`detectron2.data.DatasetMapper`](../modules/data.html#detectron2.data.DatasetMapper) | 默认 mapper | 把 dataset dict 变换为模型输入格式;支持 `is_train`、`augmentations` 等参数;示例中也是构造自定义 mapper 的参考实现 |
| [model-input format](./models.html#model-input-format) / [./models.md](./models.md) | 下游消费方 | mapper 输出(batch 后)需符合此格式才能被 `model.forward()` 接受 |
| [`detectron2.data`](../modules/data) | API 文档总览 | 文档末尾推荐查阅该模块 API 以了解更多函数用法 |
| [`DefaultTrainer`](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) | 训练框架 | 在该框架下,可通过覆写其 `build_{train,test}_loader` 方法接入自定义 dataloader |
| [DensePose train_net.py](../../projects/DensePose/train_net.py) | 实例参考 | 官方给出的自定义 dataloader 真实代码示例 |

---

## 【使用方法】

**启用方式/配置项/命令**(均直接取自原文):

1. **用默认 mapper 注入增强**:
   ```python
   import detectron2.data.transforms as T
   from detectron2.data import DatasetMapper
   dataloader = build_detection_train_loader(cfg,
      mapper=DatasetMapper(cfg, is_train=True, augmentations=[
         T.Resize((800, 800))
      ]))
   ```

2. **完全自定义 mapper**(最小实现示例):
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

3. **在 `DefaultTrainer` 中接入自定义 dataloader**:覆写其 `build_{train,test}_loader` 方法(参考 `projects/DensePose/train_net.py`)。

4. **自写训练循环时**:直接把自己的 dataloader iterator 接入即可。

5. **完全自写 dataloader**(改 sampling/batching 逻辑时):实现一个产出 `[the format](./models.md)` 的 python iterator 即可,使用任何工具均可。

> 原文未涉及 CLI 命令行开关、yaml 配置项键名等具体配置字段,故此处不补。
