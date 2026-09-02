# Use Dataloaders

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/data_loading.md

# 一体化深度解读:Detectron2 数据加载 (Dataloader) 指南

---

## 【定位】

这篇文档解决"Detectron2 数据加载机制如何使用与如何按需改造"的问题——说明 Detectron2 内置数据加载管线的工作原理,并演示从「指定一个轻量级 mapper」到「完全自定义 dataloader」三种粒度的定制方式,以及在 `DefaultTrainer` 中接入自定义 dataloader 的标准做法。

---

## 【技术要点】

1. **数据加载入口函数**:Detectron2 提供两个函数 `build_detection_{train,test}_loader`,从一个给定 config 创建默认 dataloader(分别对应训练/测试两种模式)。
2. **四步数据流**:
   - 步骤 1:根据已注册的数据集名称(如 `"coco_2017_train"`)加载为一个 `list[dict]`(轻量格式,此时图像未读入内存,未做随机增强);
   - 步骤 2:用「mapper 函数」把每个 dict 变换为模型可消费的格式(默认 mapper 是 `DatasetMapper`);
   - 步骤 3:把 mapper 输出简单列表化为一个 batch;
   - 步骤 4:该 batch 即 dataloader 输出,通常作为 `model.forward()` 的输入。
3. **默认 mapper 的能力**:读取图像、施加随机数据增强、转换为 torch Tensors,使得输出格式满足 `Use Models` 文档中描述的默认模型输入格式。
4. **轻量化定制(仅换 mapper)**:通过 `build_detection_{train,test}_loader(mapper=...)` 传入自定义 mapper,适合大多数自定义数据加载场景。原文示例:把所有训练图像 resize 到固定 `(800, 800)`,写法是 `DatasetMapper(cfg, is_train=True, augmentations=[T.Resize((800, 800))])`。
5. **完全自定义 mapper**:原文给出一个「最小 mapper」示例,关键调用包括 `utils.read_image(dataset_dict["file_name"], format="BGR")`、`T.Resize((800, 800)).get_transform(image)`、`transform.apply_image`、`torch.from_numpy(...transpose(2, 0, 1))`、`utils.transform_instance_annotations(annotation, [transform], image.shape[1:])` 以及 `utils.annotations_to_instances(annos, image.shape[1:])`,最终返回 `{"image": ..., "instances": ...}` 字典。
6. **彻底改写 dataloader**:如果还要改 sampling 或 batching 逻辑,`build_detection_train_loader` 就不再够用,需要写一个独立的 Python iterator,其产出格式须符合 `Use Models` 文档中模型接受的格式。
7. **与 `DefaultTrainer` 集成**:通过覆写 `DefaultTrainer` 的 `build_{train,test}_loader` 方法,即可在默认训练流程里使用自定义 dataloader;原文给出的参考实现是 `projects/DensePose/train_net.py`。若用户自己写训练循环,也可直接接入自己的 dataloader。

---

## 【关键机制与数据】

**(以下所有内容均严格来自原文,文档未给出任何具体性能数字或基准测试结果。)**

**工作原理(四步流水线,原文逐条列出)**:

原文:"Here is how `build_detection_{train,test}_loader` work:
1. It takes the name of a registered dataset (e.g., `"coco_2017_train"`) and loads a `list[dict]` representing the dataset items in a lightweight format. These dataset items are not yet ready to be used by the model (e.g., images are not loaded into memory, random augmentations have not been applied, etc.).
2. Each dict in this list is mapped by a function ('mapper'): ... The role of the mapper is to transform the lightweight representation of a dataset item into a format that is ready for the model to consume (including, e.g., read images, perform random data augmentation and convert to torch Tensors).
3. The outputs of the mapper are batched (simply into a list).
4. This batched data is the output of the data loader. Typically, it's also the input of `model.forward()`."

**关于 mapper 的设计哲学(原文)**:

原文:"The output format of the mapper can be arbitrary, as long as it is accepted by the consumer of this data loader (usually the model). The outputs of the default mapper, after batching, follow the default model input format documented in [Use Models]('./models.html#model-input-format')."

——这表明 mapper 输出的契约是「必须被下游消费者(通常是模型)接受」,默认 mapper 与「默认模型输入格式」是配套的。

**关于深度定制的边界(原文)**:

原文:"If you want to change not only the mapper (e.g., in order to implement different sampling or batching logic), `build_detection_train_loader` won't work and you will need to write a different data loader. The data loader is simply a python iterator that produces [the format]('./models.md') that the model accepts. You can implement it using any tools you like."

——即 dataloader 的本质契约是「一个产出模型接受格式的 Python iterator」,这一节没有给出性能/吞吐数据。

**性能/吞吐数据**:原文未涉及任何速度、显存、batch size 性能基准数据。

---

## 【表格解读】

**原文无表格。**

整篇文档仅包含文字段落与两段 Python 代码示例(分别对应「轻量改造」与「自定义 mapper」两种用法),没有以表格形式呈现的参数表、性能对比表或配置项清单。

---

## 【公式解读】

**原文无公式。**

文档内容为概念性说明与代码示例,没有出现数学公式或伪代码公式块。唯一的「代码公式」就是上述 `mapper` 函数示例——它通过 Python 代码而非公式形式描述了数据变换。

---

## 【关联】

文档明确指出了与以下模块/文档/项目之间的上下游关系(均来自文末内部链接清单):

| 文档/模块 | 关联角色 | 链接锚点 |
|---|---|---|
| `datasets.md` | 上游数据源——dataloader 通常从已注册的 dataset 中取原始数据 | `./datasets.md`, `datasets.md` |
| `build_detection_{train,test}_loader` | 入口函数——本指南的主角,所有定制都从这里出发 | `../modules/data.html#detectron2.data.build_detection_train_loader` |
| `DatasetMapper` | 默认 mapper——改造数据加载最常见的切入点 | `../modules/data.html#detectron2.data.DatasetMapper`(在文中出现两次,分别对应「用其作默认 mapper」「用其包一层做轻量改造」) |
| `Use Models` (`./models.md` / `./models.html#model-input-format`) | 下游契约——决定 mapper 输出格式与 dataloader 产出格式 | `./models.html#model-input-format`, `./models.md` |
| `detectron2.data` API 总览 | 工具箱——实现任何定制时都建议查阅 | `../modules/data` |
| `DefaultTrainer` | 训练容器——通过覆写其 `build_{train,test}_loader` 接入自定义 dataloader | `../modules/engine.html#detectron2.engine.defaults.DefaultTrainer` |
| `projects/DensePose/train_net.py` | 参考样例——示范如何在 `DefaultTrainer` 派生类里覆写 dataloader | `../../projects/DensePose/train_net.py` |

**关系总结(原文视角)**:
- **上游**:dataloader 消费 `datasets.md` 描述的 dataset 字典表示;
- **核心**:`build_detection_{train,test}_loader` + `DatasetMapper` 共同构成默认管线;
- **下游**:产出格式必须符合 `./models.md` / `model-input-format` 的要求,才能送入 `model.forward()`;
- **训练侧集成**:通过 `DefaultTrainer.build_{train,test}_loader` 覆写或自定义训练循环两条路径接入;
- **API 参考**:`../modules/data` 是任何改造都应该回查的工具集合;
- **实战参考**:`projects/DensePose/train_net.py` 给出了一个真实改造范例。

---

## 【使用方法】

以下全部摘自原文,文档没有引入新的配置文件项或环境变量,而是给出一组 Python API 调用模式。

**1. 用默认 dataloader(原文未给出完整调用,但暗示通过 `build_detection_{train,test}_loader(cfg)` 即可获得)**

原文:"Detectron2 provides two functions `build_detection_{train,test}_loader` that create a default data loader from a given config."

**2. 轻量改造——固定 resize**(原文示例,逐字保留):

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper   # the default mapper
dataloader = build_detection_train_loader(cfg,
   mapper=DatasetMapper(cfg, is_train=True, augmentations=[
      T.Resize((800, 800))
   ]))
# use this dataloader instead of the default
```

要点:
- 在 `DatasetMapper` 构造时传入 `is_train=True`;
- `augmentations` 参数接收一个 `T.Resize((800, 800))` 的列表,固定把图像缩放到 `800×800`。
- 注释 `# use this dataloader instead of the default` 提示:这是替换默认 dataloader 的标准位置。

**3. 写自定义 mapper 函数**(原文示例,逐字保留):

```python
from detectron2.data import detection_utils as utils
 # Show how to implement a minimal mapper, similar to the default DatasetMapper
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
       # create the format that the model expects
       "image": image,
       "instances": utils.annotations_to_instances(annos, image.shape[1:])
    }
dataloader = build_detection_train_loader(cfg, mapper=mapper)
```

要点:
- 必须 `copy.deepcopy(dataset_dict)` 以避免污染原始数据;
- 图像读取采用 `utils.read_image(..., format="BGR")`(注释提示也可以用其他方式);
- 图像维度变换使用 `transpose(2, 0, 1)`(从 H×W×C 到 C×H×W);
- 标注变换 `transform_instance_annotations` 接受一个变换列表(此处为单元素 `[transform]`);
- 最终返回 `{"image", "instances"}` 字典,符合 `Use Models` 文档规定的输入格式。
- 然后通过 `build_detection_train_loader(cfg, mapper=mapper)` 注入。

**4. 完全自写 dataloader**(原文描述,无代码):

原文:"If you want to change not only the mapper (e.g., in order to implement different sampling or batching logic), `build_detection_train_loader` won't work and you will need to write a different data loader. The data loader is simply a python iterator that produces [the format]('./models.md') that the model accepts. You can implement it using any tools you like."

要点:实现一个 Python iterator,逐个产出符合 `models.md` 所规定格式的数据即可,不强制使用 PyTorch `DataLoader`。

**5. 在 `DefaultTrainer` 中接入自定义 dataloader**(原文描述,无代码):

原文:"If you use `DefaultTrainer`, you can overwrite its `build_{train,test}_loader` method to use your own dataloader. See the `densepose dataloader` for an example."

要点:
- 继承 `DefaultTrainer`;
- 覆写 `build_train_loader` / `build_test_loader` 方法,在其中返回自定义 dataloader;
- 参考样例 `projects/DensePose/train_net.py`(本仓内项目代码)。

**6. 自写训练循环接入**(原文描述,无代码):

原文:"If you write your own training loop, you can plug in your data loader easily."

要点:由于 dataloader 仅是产出模型输入格式的 iterator,任何训练循环均可直接消费,无框架耦合限制。

**推荐的后续查阅项(原文建议,非配置)**:

原文:"No matter what to implement, it's recommended to check out [API documentation of detectron2.data] to learn more about the APIs of these functions."

——即在做任何定制之前/之后,均建议查阅 `detectron2.data` 模块的 API 文档以确认可用工具。
