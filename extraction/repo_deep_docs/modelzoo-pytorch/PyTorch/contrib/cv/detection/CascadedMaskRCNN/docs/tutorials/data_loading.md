# Use Dataloaders

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/data_loading.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/data_loading.md

```markdown
# 文档一体化深度解读:Use Dataloaders

## 【定位】

这篇文档解决 Detectron2 中"如何在训练/测试时为模型提供数据"的核心问题,系统性地说明内置数据加载管线(`build_detection_{train,test}_loader` + `DatasetMapper`)的工作原理,并提供自定义 dataloader / mapper 的范式与示例,以适配各种数据集、采样和批处理需求。

---

## 【技术要点】

1. **两套入口函数**:Detectron2 提供 `build_detection_train_loader` 与 `build_detection_test_loader` 两个函数,从给定 config 创建默认 dataloader(见 [API 文档](../modules/data.html#detectron2.data.build_detection_train_loader))。
2. **数据集轻量表示**:加载的是已注册数据集名(如 `"coco_2017_train"`)对应的 `list[dict]`,每条 dict 是**轻量**的——图像未读入内存、未做随机增广;格式与注册细节见 [datasets](./datasets.md)。
3. **可定制的 mapper 层**:每条 dict 由一个 mapper 函数处理,默认 mapper 为 `DatasetMapper`,可由 `build_detection_{train,test}_loader(mapper=)` 替换;mapper 负责把轻量表示变为模型可直接消费的张量(读图、增广、转 torch Tensor)。
4. **mapper 输出的 batch 化**:mapper 输出经简单 list 化打包成 batch,该 batch 即 dataloader 的产出,通常直接送入 `model.forward()`。
5. **官方增广接入范式**:在 `DatasetMapper` 中通过 `augmentations=[T.Resize((800, 800))]` 传入增广变换列表,实现"把训练图全部 resize 到固定尺寸"。
6. **完全自实现路径**:若需改的不是 mapper 而是**采样/批处理逻辑**,官方建议丢掉 `build_detection_train_loader`,自行实现一个"产出符合 [model 输入格式](./models.md) 的 python 迭代器"。

---

## 【关键机制与数据】

### 工作原理(四步管线)
原文明确给出 `build_detection_{train,test}_loader` 内部流程(原文 1–4 步):

1. 拿注册名 → 取回 `list[dict]`(轻量、未加载图像、未增广)。
2. 每条 dict 经 mapper 处理:
   - 自定义方式:`build_detection_{train,test}_loader(mapper=...)` 显式传入;
   - 默认实现:`DatasetMapper`;
   - 职责:读图、做随机增广、转 torch Tensor;
   - 输出格式任意,只要下游(通常是模型)能消费,默认 mapper 批量化后的输出遵循 [Use Models - model input format](./models.html#model-input-format)。
3. mapper 输出被**简单 list 化**为 batch。
4. 该 batch 是 dataloader 的产出,典型用法即 `model.forward()` 的输入。

### 数据流(自定义 mapper 的最小实现)
原文给出一个最小 mapper 示例(代码块第二段),关键链路:

- `copy.deepcopy(dataset_dict)`:就地修改前先复制,避免污染上游;
- `utils.read_image(dataset_dict["file_name"], format="BGR")`:替代默认读图;
- `T.Resize((800, 800)).get_transform(image)` → `transform.apply_image(image)` → `.transpose(2, 0, 1)` → `torch.from_numpy(...)`:增广 + HWC→CHW + 张量化;
- `utils.transform_instance_annotations(annotation, [transform], image.shape[1:])`:对每条 annotation 同步施加同一几何变换;
- 最终返回 `{"image": image, "instances": utils.annotations_to_instances(annos, image.shape[1:])}`:对得上 model 期望的输入键 `image`、`instances`。

### 性能/统计数字
原文:**无**性能 benchmark、时延、吞吐、参数量等数据;文中出现的"数字"只有示例中的图像尺寸 `(800, 800)` 与图像维度描述 `HWC→CHW`,属于示意而非基准。

---

## 【表格解读】

**原文无表格。** 全文通过 4 步文字描述 + 2 段代码示例解释机制,未呈现任何参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式。** 文中不含 LaTeX、伪代码公式或数学表达式;数据处理以代码(调用 `T.Resize(...).get_transform(image)`、`transform.apply_image(...)`、`annotations_to_instances(...)`)描述,无符号化公式。

---

## 【关联】

依据文末给出的内部链接,文档与以下模块/项目构成上下游或互补关系:

- **数据集侧(上游)**:
  - [datasets.md](./datasets.md)、[datasets](datasets.md):解释 `list[dict]` 格式如何被注册与取出,是 dataloader 第 1 步的直接输入。
  - [../modules/data](../modules/data):dataloader / mapper 相关 API 总索引,文中明确"无论如何实现,建议查阅该 API 文档"。

- **模型侧(下游)**:
  - [./models.html#model-input-format](./models.html#model-input-format)、[./models.md](./models.md):规定 mapper 输出 + batch 后送入模型的字段格式;自定义 mapper 第二个代码块中返回的 `{"image", "instances"}` 即对应此约定。
  - [../modules/data.html#detectron2.data.DatasetMapper](../modules/data.html#detectron2.data.DatasetMapper):默认 mapper 的具体 API,文档中两处反复指回,作为"覆盖默认行为"的参考。

- **训练引擎侧(集成点)**:
  - [../modules/engine.html#detectron2.engine.defaults.DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer):用户使用 `DefaultTrainer` 时,通过覆写其 `build_{train,test}_loader` 方法接入自定义 dataloader。
  - [../../projects/DensePose/train_net.py](../../projects/DensePose/train_net.py):官方 DensePose 项目中接入自定义 dataloader 的完整示例,可作为"如何挂载"的最权威参考。

- **构建函数(本文主角)**:
  - [../modules/data.html#detectron2.data.build_detection_train_loader](../modules/data.html#detectron2.data.build_detection_train_loader):`build_detection_train_loader` 与 `build_detection_test_loader` 的 API 文档,本文 4 步流程的源码对应点。

整体形成"**注册数据集 → dataloader 拉取 + mapper 转换 → 模型/DefaultTrainer 消费**"的链路,本文聚焦在中间那一段。

---

## 【使用方法】

### 1. 用默认 dataloader
原文未给出独立命令(由 `DefaultTrainer` 隐式调用),典型流程即在 config 中指定注册数据集名后由 [../modules/engine.html#detectron2.engine.defaults.DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 调用 `build_detection_{train,test}_loader(cfg)`。

### 2. 用自定义增广(沿用默认 mapper)
原文示例,直接把训练图 resize 到 800×800:

```python
import detectron2.data.transforms as T
from detectron2.data import DatasetMapper
dataloader = build_detection_train_loader(
    cfg,
    mapper=DatasetMapper(cfg, is_train=True, augmentations=[
        T.Resize((800, 800))
    ])
)
# 替换默认 dataloader
```

### 3. 用自定义 mapper 函数
原文给出一个最小 mapper(读图 → Resize → 转 Tensor → 同步变换 annotation → 返回 `{image, instances}`),并通过 `build_detection_train_loader(cfg, mapper=mapper)` 接入;关键 API:`utils.read_image`、`T.Resize(...).get_transform(...)`、`transform.apply_image(...)`、`utils.transform_instance_annotations(...)`、`utils.annotations_to_instances(...)`。

### 4. 在 `DefaultTrainer` 中覆写
原文明确:使用 [DefaultTrainer](../modules/engine.html#detectron2.engine.defaults.DefaultTrainer) 时,重写其 `build_{train,test}_loader` 方法即可插入自定义 dataloader;完整范例见 [densepose train_net.py](../../projects/DensePose/train_net.py)。

### 5. 完全自实现(改采样/批处理)
原文说明:若改的不是 mapper 而是采样或批处理逻辑,`build_detection_train_loader` 不再适用,需自行实现一个"产出符合 [model 输入格式](./models.md) 的 python 迭代器",可自由选用任何 python 工具实现。

### 6. 排查/扩展前必读
原文建议:无论实现何种自定义,先查 [API 文档 of detectron2.data](../modules/data) 摸清可复用函数接口,再决定走"只换 mapper"还是"全自实现"。
```
