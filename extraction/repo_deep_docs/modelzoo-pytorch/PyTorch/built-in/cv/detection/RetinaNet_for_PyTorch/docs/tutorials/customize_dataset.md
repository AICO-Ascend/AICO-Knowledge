# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/customize_dataset.md

【定位】
本文是 MMDetection 框架下 RetinaNet_for_PyTorch 模型仓中的 "Tutorial 2: Customize Datasets" 教程文档,解决的核心问题是: **当用户拥有非标准格式的自定义目标检测/实例分割数据集时,如何在不修改训练框架源码的前提下,通过离线/在线转换或自定义 Dataset 类的方式,使数据集适配现有检测器(如 Cascade Mask R-CNN、FPN、RetinaNet 等)进行训练与评估**。

【技术要点】

1. **三条主要路径支持新数据格式**:
   - 路径 A: 将数据转换为已存在格式 (COCO 或 PASCAL VOC) —— **原文推荐方案**,离线转换后只需修改 config 的 `ann_file` 与 `classes`。
   - 路径 B: 将数据转换为 MMDetection 定义的 **中间格式 (middle format)** —— 一个 list[dict] 结构,适合不想按 COCO/VOC 组织数据的用户。
   - 路径 C: 在线转换 —— 继承 `CustomDataset` 并重写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)` 两个方法(参考 `CocoDataset`/`VOCDataset`)。

2. **COCO 格式 JSON 的三必须键 (three necessary keys)**:
   - `images`: 列表,每项含 `file_name`、`height`、`width`、`id`。
   - `annotations`: 列表,每项含 `segmentation`(可选)、`area`、`iscrowd`、`image_id`、`bbox`(4 元素)、`category_id`、`id`。
   - `categories`: 列表,每项含 `id`、`name`。

4. **使用现有格式自定义数据集的两步配置流程**:
   - 步骤 1: 修改 config 的 `data` 字段,在 `data.train`、`data.val`、`data.test` 三个 dict 中显式添加 `classes` 元组,并设置 `dataset_type='CocoDataset'`、`ann_file`、`img_prefix`。
   - 步骤 2: 显式覆盖 `model.roi_head.bbox_head[*].num_classes` 与 `model.roi_head.mask_head.num_classes` (示例中由默认 80 → 自定义 5)。

5. **三类一致性校验规则 (Check the annotations)**:
   - 规则 ①:`annotations.categories` 的长度 = config 中 `classes` 元组长度(示例为 5)。
   - 规则 ②:config 中 `classes` 与 `categories[*].name` 元素及顺序一致;MMDetection 会自动将 `categories` 中**不连续**的 `id` 映射为**连续**的 label 索引,`name` 的字符串顺序影响 label 索引顺序,也影响可视化时边界框的 label 文本顺序。
   - 规则 ③:`annotations[*].category_id` 必须能在 `categories[*].id` 中找到(必须 valid)。

6. **中间格式数据结构**:每个样本对应一个 dict,公共字段为 `filename`(相对路径)、`width`、`height`;训练时额外带 `ann` dict,内含 `bboxes`(numpy float32, shape (n,4))、`labels`(numpy int64, shape (n,))、可选的 `bboxes_ignore`(float32, (k,4)) 与 `labels_ignore`(int64, (k,)),用于覆盖 crowd/difficult/ignored 标注。

7. **典型自定义文本格式示例**:每张图前以 `#` 分隔,首行为 ``、第二行为 `<width> <height>`、第三行为该图目标数量 `n`,后续 `n` 行每行格式为 `<x1> <y1> <x2> <y2> <category_id>`,如 `10 20 40 60 1`。通过在 `mmdet/datasets/my_dataset.py` 中创建继承 `CustomDataset` 的 `MyDataset` 类并用 `@DATASETS.register_module()` 注册来加载。

【关键机制与数据】

- **原文:类别映射机制**:MMDetection 自动将 `categories` 列表中**不连续**的 id(如示例中 `{1, 3, 4, 16, 17}`)按 `name` 出现的字符串顺序映射为**连续**的 label 索引 `0~4`,用户不必手动重排 id。
- **原文:Cascade Mask R-CNN R50 FPN 训练配置参数**:基础 config 为 `./cascade_mask_rcnn_r50_fpn_1x_coco.py`;`samples_per_gpu=2`、`workers_per_gpu=2`;三个 `Shared2FCBBoxHead` 的 `num_classes` 同时被覆盖为 5;`mask_head.num_classes=5`;示例类别元组为 `classes = ('a', 'b', 'c', 'd', 'e')`。
- **原文:COCO 标注样例数值**:`file_name='COCO_val2014_000000001268.jpg'`,`height=427`,`width=640`,`id=1268`;对应 annotation 的 `area=1035.749`、`iscrowd=0`、`image_id=1268`、`bbox=[192.81, 224.8, 74.73, 33.43]`、`category_id=16`、`id=42986`;categories 中 `{'id': 0, 'name': 'car'}`。
- **原文:中间格式示例数值**:`'filename': 'a.jpg'`,`width=1280`,`height=720`,内部 bboxes/labels 为 numpy 数组 (`bboxes` float32 形状 (n,4),`labels` int64 形状 (n,))。
- **原文:限制说明 (Note)**:**MMDetection 当前仅支持 COCO 格式数据集的 mask AP 评估**;强烈建议离线转换,以便复用 `CocoDataset`。

【表格解读】

**原文无表格**。原文中所有结构化信息均以代码块、字典、列表或元组形式给出,未出现 markdown/HTML 表格。可结构化的代码示例见上节"关键机制与数据"。

【公式解读】

**原文无公式**。本文是工程配置教程,未涉及数学公式或伪代码算法。所有数值(如 `area=1035.749`、`bbox=[192.81, 224.8, 74.73, 33.43]`)均为示例标注值,非公式。

【关联】

- **`../../mmdet/datasets/dataset_wrappers.py`**(文末内部链接):属于 MMDetection 数据集封装层,通常提供 `ClassBalancedDataset`、`RepeatDataset`、`MultiImageMixDataset` 等包装器,用于在已注册的自定义 `Dataset`(如本文中基于 `CustomDataset` 的 `MyDataset`、或经 COCO 转换后的 `CocoDataset`)之外再加一层采样/增强/Mix 策略包装,与本文的"自定义数据集 → 训练流程"环节直接耦合。
- **上游关联**:
  - `CocoDataset`(https://github.com/open-mmlab/mmdetection/blob/master/mmdet/datasets/coco.py)—— 在线自定义 Dataset 的参考实现。
  - `VOCDataset`(https://github.com/open-mmlab/mmdetection/blob/master/mmdet/datasets/voc.py)—— 同上,作为 PASCAL VOC 路径的参照。
  - `CustomDataset`(被 `MyDataset` 继承的基类)—— 中间格式入口。
  - `tools/dataset_converters/cityscapes.py` 与 `configs/cityscapes` —— 离线转换的 CityScapes 示例,印证"推荐离线转 COCO"的方法论。
  - `tools/dataset_converters/pascal_voc.py` —— 离线转换的 PASCAL VOC 示例。
- **下游关联**:
  - `configs/cascade_mask_rcnn_r50_fpn_1x_coco.py` —— 文档示例中被继承的 base config,验证了"只需修改 data/model 字段即可换数据集"的最小侵入性原则,RetinaNet、MaskRCNN、FasterRCNN 等模型仓的 config 同样可按本教程的 `data`/`model` 覆盖范式迁移到自定义数据集。

【使用方法】

1. **离线转 COCO 格式 (原文推荐)**
   - 准备 `images` / `annotations` / `categories` 三键完整的 JSON 标注文件。
   - 新建 `configs/my_custom_config.py`,以 base config(如 `cascade_mask_rcnn_r50_fpn_1x_coco.py`)为基础:
     - 设置 `dataset_type='CocoDataset'`。
     - 在 `data.train / data.val / data.test` 三个子 dict 中填入 `classes=classes`、`ann_file`、`img_prefix`。
     - 在 `model.roi_head.bbox_head[*].num_classes`(以及 `mask_head.num_classes`)处显式覆盖为自定义类别数。
   - 校验:`categories` 长度 == `classes` 长度;`categories[*].name` 与 `classes` 元素及顺序一致;`annotations[*].category_id` 全部命中 `categories[*].id`。

2. **离线转 middle 格式 (原文备选)**
   - 用 `pascal_voc.py` 等脚本将原始标注转换为 list[dict](含 `filename`/`width`/`height`/`ann.{bboxes,labels,...}`),保存为 pickle/json。
   - 直接使用 `CustomDataset` 并在 config 中指定 `ann_file` 为转换结果文件即可,无需继承类。

3. **在线自定义 (原文备选)**
   - 在 `mmdet/datasets/my_dataset.py` 中创建继承 `CustomDataset` 的类,使用 `@DATASETS.register_module()` 注册。
   - 重写 `load_annotations(self, ann_file)`(解析原始文件为 self.data_infos 列表)与 `get_ann_info(self, idx)`(返回当前样本的 bboxes/labels 等)。
   - 设置类属性 `CLASSES = ('person', 'bicycle', 'car', ...)`,与 config 中 `model` 的 `num_classes` 保持一致。
   - 在 config 中将 `dataset_type` 设为 `'MyDataset'`,`ann_file`/`img_prefix` 指向原始数据路径。

4. **典型命令行 (原文未涉及具体训练命令)** —— 原文未给出,需结合 modelzoo 的启动脚本(在 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch` 仓内另行查找)使用 `tools/train.py` + 自定义 config 进行训练与 `tools/test.py` 进行评估。
