# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/customize_dataset.md

# 一体化深度解读:Tutorial 2: Customize Datasets

> 注:本文档位于 `SSD_for_PyTorch/docs/en/`,但其正文内容引用 **MMDetection**(`open-mmlab/mmdetection`)的 API、`CustomDataset`/`CocoDataset`/`VOCDataset` 与配置体系(如 `cascade_mask_rcnn_r50_fpn_1x_coco.py`),与 SSD 自身实现无直接关系;此外原文在 MyDataset 示例处被截断(`'mot` 后缺失)。

---

## 【定位】

这篇文档解决"如何在 MMDetection 中接入一个全新的、自定义的数据集(新标注格式/新类别集合)"的问题,给出两种主路径——**离线转换为 COCO/PASCAL 等已有格式** 与 **转换为 middle format**(在线继承 `CustomDataset` 或离线导出 pickle/json)——并以一个 5 类自定义数据集驱动 Cascade Mask R-CNN R50-FPN 为例,展示 config 与标注的双向校验流程。

---

## 【技术要点】

1. **首选路径:离线转换为 COCO 格式**(原文:"we recommend to convert the data into COCO formats and do the conversion offline"),转换后仅需修改 config 的标注路径与类别。
2. **COCO JSON 三个必备键** — `images`(含 `file_name`/`height`/`width`/`id`)、`annotations`(实例标注)、`categories`(类别名与 ID)。
3. **config 修改两处**:`data.train/val/test` 显式添加 `classes` 字段;`model` 中把所有 `num_classes` 由 COCO 默认的 80 覆盖为实际类别数(示例 5)。
4. **Cascade 结构下,`roi_head.bbox_head` 是长度为 3 的列表**,每个元素都是 `Shared2FCBBoxHead`,**必须全部**显式覆盖 `num_classes=5`;此外 `mask_head.num_classes=5` 也需覆盖。
5. **类别一致性三校验**:①`categories` 长度 = `classes` 元组长度;②`classes` 与 `categories[*].name` 的元素和顺序相同;③`annotations.category_id` 必须属于 `categories[*].id`。
6. **Middle format 通用结构**:列表中每张图为一个 dict,含 `filename`/`width`/`height`,训练时多一个 `ann` 字段,`ann` 内含 `bboxes`(float32, (n,4))、`labels`(int64, (n,))、可选 `bboxes_ignore`/`labels_ignore`。
7. **两种自定义接入方式**:
   - **在线转换**:继承 `CustomDataset`,重写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`,参考 `CocoDataset`、`VOCDataset`。
   - **离线转换**:先把标注转成 middle format 并存为 pickle/json,再直接使用 `CustomDataset`,参考 `pascal_voc.py`。

---

## 【关键机制与数据】

- **类别映射机制(原文):**"MMDetection automatically maps the uncontinuous `id` in `categories` to the continuous label indices, so the string order of `name` in `categories` field affects the order of label indices."
  - 即 `categories` 中的 `id` 可以是不连续的(如示例中 `1, 3, 4, 16, 17`),但其**字符串顺序**决定最终 label 索引顺序;同样,config 中 `classes` 元组的顺序影响可视化时显示的类别文本。
- **示例配置数值(原文):**`samples_per_gpu=2`、`workers_per_gpu=2`、训练 Cascade Mask R-CNN 用 5 类。
- **bbox 标注示例数据(原文):**`bbox: [192.81, 224.8, 74.73, 33.43]`(`area: 1035.749`,`category_id: 16`)。
- **middle format 类型契约(原文):**`bboxes` 为 `<np.ndarray, float32> (n, 4)`;`labels` 为 `<np.ndarray, int64> (n, )`;`bboxes_ignore`/`labels_ignore` 可选,形状对应 (k, 4)/(k,)。
- **文本标注示例(原文被截断片段):** 每行格式 `x1 y1 x2 y2 class_id`(如 `10 20 40 60 1`),文件以 `#` 分组,首行为图像文件名,次行为 `width height`,第三行为该图目标数,之后为目标行。
- **实例分割限制(原文 Note 1):** "MMDetection only supports evaluating mask AP of dataset in COCO format for now" — 实例分割评估目前仅支持 COCO 格式。
- **数据流(综合原文):** 用户数据 → 离线转换为 COCO JSON 或 middle format pickle/json → `CustomDataset`(或其子类)在训练时读取 → DataLoader 按 `samples_per_gpu=2` 组 batch → 模型以 `num_classes=N` 输出预测。

---

## 【表格解读】

**原文无表格**。文档以 Python 代码块、JSON 片段与配置文件形式承载结构化信息,未出现 markdown 表格。

---

## 【公式解读】

**原文无公式**(无 LaTeX 公式、无伪代码形式的算法式)。仅有的"准结构化"标注格式以 JSON 字段或 Python 字典表示,见上文【关键机制与数据】。

---

## 【关联】

虽然本任务说明中标注"内部链接:(无)",原文对外指向了 MMDetection 生态中的多个模块与脚本,可作为上下游/参考实现关联:

- **基线配置**:`cascade_mask_rcnn_r50_fpn_1x_coco.py` — 自定义 config 通过 `_base_` 继承。
- **数据集类基座**:`CustomDataset`(用户继承起点);参考实现 `CocoDataset`、`VOCDataset`。
- **离线转换脚本**:
  - `tools/dataset_converters/cityscapes.py` — CityScapes 转 COCO 的示例(原文:"We use this way to support CityScapes dataset")。
  - `tools/dataset_converters/pascal_voc.py` — PASCAL VOC 转 middle format 的示例。
- **微调配置入口**:`configs/cityscapes/` 目录(CityScapes 的 finetuning 配置)。
- **MMDetection 限制依赖**:实例分割 mask AP 评估能力绑定于 COCO 格式。
- **本仓库上下文**:路径位于 `modelzoo-pytorch/SSD_for_PyTorch/docs/`,但教程内容实质是 MMDetection 通用教程,若 SSD 训练需遵循该流程,实际仍需在 SSD_for_PyTorch 自身配置中替换为 SSD 检测器(原文示例用 Cascade Mask R-CNN,不直接适用 SSD)。

---

## 【使用方法】

**1. 离线转 COCO 后的接入(原文流程)**

- 步骤 1 — 修改 config(`configs/my_custom_config.py`):
  - 设置 `dataset_type = 'CocoDataset'`、`classes = ('a', 'b', 'c', 'd', 'e')`。
  - 在 `data.train/val/test` 中分别填写 `type=dataset_type`、`classes=classes`、`ann_file='path/to/your/{train,val,test}/annotation_data'`、`img_prefix='path/to/your/{train,val,test}/image_data'`。
  - 在 `model.roi_head.bbox_head`(列表 3 项,均为 `Shared2FCBBoxHead`)逐项覆盖 `num_classes=5`,并覆盖 `model.roi_head.mask_head.num_classes=5`。
- 步骤 2 — 校验标注:满足上文"类别一致性三校验"。
- 启动:按 MMDetection 常规训练命令(`python tools/train.py configs/my_custom_config.py`),原文未给出具体启动命令,需参考 MMDetection 通用教程。

**2. Middle format 接入(原文流程)**

- 离线:用脚本(如 `pascal_voc.py` 的方式)将自定义标注导出为 middle format 的 pickle/json。
- 在线:新建 `mmdet/datasets/my_dataset.py`,用 `@DATASETS.register_module()` 注册 `MyDataset(CustomDataset)`,设置 `CLASSES = (...)`,并重写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`(原文示例在 `'mot` 处被截断,`get_ann_info` 的具体实现未给出)。

**3. 实例分割评估**

- 原文 Note 1 明确:**仅 COCO 格式支持 mask AP 评估**,因此若需 mask 指标,数据必须先转 COCO。

**4. 命令行/超参**

- 原文未涉及具体启动命令、学习率、batch size 等训练超参(仅给出 `samples_per_gpu=2, workers_per_gpu=2` 作为 config 片段示例),其余需参考 MMDetection 主教程与所继承的基线 config(`cascade_mask_rcnn_r50_fpn_1x_coco.py`)。
