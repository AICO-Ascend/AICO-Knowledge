# Use Builtin Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/builtin_datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/builtin_datasets.md

# 「Use Builtin Datasets」深度解读

## 【定位】

本文档解决的是 detectron2 框架中「如何为内置数据集(builtin datasets)按约定目录结构摆放/生成数据,使其能被 `DatasetCatalog` 与 `MetadataCatalog` 这两个核心 API 正常加载」的问题,本质上是一份面向数据集接入侧的"目录约定 + 预处理脚本指南"。

---

## 【技术要点】

1. **环境变量定位数据集根目录**
   - 数据集必须位于环境变量 `DETECTRON2_DATASETS` 指向的目录下。
   - 设置方式:`export DETECTRON2_DATASETS=/path/to/datasets`。
   - 未设置时,默认为当前工作目录下的 `./datasets`(相对路径)。

2. **detectron2 期望识别的顶层子目录约定(原文中以 ASCII 树形结构展示)**
   - `$DETECTRON2_DATASETS/` 下寻找 `coco/`、`lvis/`、`cityscapes/`、`VOC20{07,12}/`(原文中的花括号为 shell 风格展开,即 `VOC2007` 与 `VOC2012` 两个目录并列)。

3. **COCO 实例/关键点检测的目录约定**
   - `coco/annotations/instances_{train,val}2017.json`
   - `coco/annotations/person_keypoints_{train,val}2017.json`
   - `coco/{train,val}2017/`(对应 json 中提到的图像文件)
   - 同时支持 2014 版本(原文:"You can use the 2014 version of the dataset as well.")。

4. **PanopticFPN(基于 COCO 全景注释)**
   - 需要 `coco/annotations/panoptic_{train,val}2017.json` 与 `coco/panoptic_{train,val}2017/`(png 注释)。
   - 另需运行 `python datasets/prepare_panoptic_fpn.py` 生成 `panoptic_stuff_{train,val}2017/`。
   - 依赖:`pip install git+https://github.com/cocodataset/panopticapi.git`。

5. **LVIS 实例分割**
   - 同时复用 `coco/{train,val,test}2017/` 图像目录;`lvis/` 下放 `lvis_v0.5_{train,val}.json`、`lvis_v0.5_image_info_test.json`、`lvis_v1_{train,val}.json`、`lvis_v1_image_info_test{,_challenge}.json`。
   - 依赖:`pip install git+https://github.com/lvis-dataset/lvis-api.git`。
   - 评估"在 COCO 上训练、在 LVIS 上评估"的模型时,运行 `python datasets/prepare_cocofied_lvis.py` 准备"cocofied" 注释。

6. **cityscapes 语义/实例/全景分割**
   - 同时需要 `gtFine/(train|val|test)/...` 与 `leftImg8bit/(train|val|test)/...`。
   - `gtFine/train/<city>/` 下需要 `color.png, instanceIds.png, labelIds.png, polygons.json, labelTrainIds.png`(原文同一目录内逗号分隔列出五个文件)。
   - 全景注释 `cityscapes_panoptic_{train,val,test}.json` 及对应目录由脚本生成。
   - 依赖:`pip install git+https://github.com/mcordts/cityscapesScripts.git`。
   - 生成 `labelTrainIds.png` 的命令:`CITYSCAPES_DATASET=/path/to/abovementioned/cityscapes python cityscapesscripts/preparation/createTrainIdLabelImgs.py`。
   - 生成 Cityscapes 全景数据命令:`CITYSCAPES_DATASET=/path/to/abovementioned/cityscapes python cityscapesscripts/preparation/createPanopticImgs.py`。
   - 原文两条 "These files are not needed for ..." 的注释:`labelTrainIds.png` 不被实例分割需要;全景注释文件不被语义/实例分割需要。

7. **Pascal VOC**
   - `VOC20{07,12}/` 下需要 `Annotations/`、`ImageSets/Main/`(含 `trainval.txt`、`test.txt`,并可选用 `train.txt` 或 `val.txt`)、`JPEGImages/`。

8. **ADE20k Scene Parsing**
   - `ADEChallengeData2016/` 下需要 `annotations/`、`images/`、`objectInfo150.txt`,以及运行 `python datasets/prepare_ade20k_sem_seg.py` 生成的 `annotations_detectron2/`。

---

## 【关键机制与数据】

**工作原理(原文层面)**:
- detectron2 内置数据集机制基于两个核心注册表 — `DatasetCatalog`(提供数据条目)与 `MetadataCatalog`(提供类名等元数据),文档开篇即点明这一分工。
- 数据集本身**不会自动下载**,框架只认**目录结构**与**约定文件名**。一旦满足这些结构,注册表即可正确索引到训练/评估所需的图像与注释。
- 部分数据集(如 COCO 2014 vs 2017、PanopticFPN 的 stuff 注释、Cityscapes 的 labelTrainIds 与 panoptic 注释、ADE20k 的 detectron2 注释、cocofied LVIS)需要额外的**预处理脚本或上游工具**来生成,detectron2 通过 `datasets/prepare_*.py` 这一组脚本将这些派生文件纳入约定路径。

**数据流(原文层面)**:
- 用户设置 `DETECTRON2_DATASETS` → detectron2 在其下按约定目录扫描 → 用户保证 JSON 注释、PNG 注释、原始图像三类文件就位 → 通过 `DatasetCatalog` 暴露给上层训练/评估代码。

**性能数据**:
- 原文未涉及任何性能/基准数字。

---

## 【表格解读】

原文无表格。

(原文仅以 ASCII 目录树的方式罗列每个数据集期望的子目录与文件名,不属于参数表、性能对比或配置项表格;按要求不臆造。)

---

## 【公式解读】

原文无公式。

(原文中没有数学公式或伪代码算法片段;所有"命令式"内容(`pip install`、`export`、`python datasets/...`、`CITYSCAPES_DATASET=... python ...`)均为 shell 命令,而非数学式。)

---

## 【关联】

本文档明确给出的上下游/跨模块引用如下:

- **`DatasetCatalog` / `MetadataCatalog`**(detectron2.data 模块)
  - 链接:https://detectron2.readthedocs.io/modules/data.html#detectron2.data.DatasetCatalog 与 `...#detectron2.data.MetadataCatalog`
  - 关系:本文档说明"如何摆放数据才能被这两个 API 正常使用";它们是 detectron2 数据层的"上层 API"。

- **`Use Custom Datasets` 教程**(detectron2 自定义数据集教程)
  - 链接:https://detectron2.readthedocs.io/tutorials/datasets.html
  - 关系:原文描述其为"a deeper dive on how to use `DatasetCatalog` and `MetadataCatalog`, and how to add new datasets to them",即本文档定位为"内置数据集速查",该教程为"自定义数据集深入指南",二者形成内置 vs 自定义的并列关系。

- **MODEL_ZOO(模型动物园)**
  - 链接:https://github.com/facebookresearch/detectron2/blob/master/MODEL_ZOO.md
  - 关系:模型动物园中的 configs 与 models 假设这些内置数据集已按本文档的目录结构就位。

- **数据集下载来源**(原文将其作为"上游数据源"提及)
  - COCO 官方下载页:https://cocodataset.org/#download
  - LVIS 数据集:https://www.lvisdataset.org/dataset
  - Cityscapes:https://www.cityscapes-dataset.com/downloads/
  - Pascal VOC:http://host.robots.ox.ac.uk/pascal/VOC/index.html
  - ADE20k Scene Parsing:http://sceneparsing.csail.mit.edu/

- **上游/配套第三方包**(原文明确以 `pip install` 方式给出)
  - panopticapi(cocodataset 组织下的全景注释工具)
  - lvis-api(lvis-dataset 组织下的 LVIS 接口)
  - cityscapesScripts(mcordts 个人仓库下的 cityscapes 预处理脚本)

- **`dev/run_*_tests.sh` 内置测试脚本**
  - 关系:原文提到部分内置测试使用了"a tiny version of the COCO dataset",通过 `./datasets/prepare_for_tests.sh` 下载;这是文档中唯一一处提到 detectron2 自家测试套件与本文档的衔接点。

- **`datasets/prepare_*.py` 预处理脚本族**
  - 本文反复引用的同仓库脚本:`prepare_for_tests.sh`、`prepare_panoptic_fpn.py`、`prepare_cocofied_lvis.py`、`prepare_ade20k_sem_seg.py`。它们不与单一数据集一一对应,而是作为"配套派生文件生成器"嵌于各数据集小节中。

---

## 【使用方法】

以下命令/配置项均直接出自原文。

1. **设定数据集根目录**
   - `export DETECTRON2_DATASETS=/path/to/datasets`
   - 不设置则默认为 `./datasets`(当前工作目录的相对路径)。

2. **让内置测试运行起来(最小化 COCO 子集)**
   - `./datasets/prepare_for_tests.sh`

3. **PanopticFPN**
   - 安装:`pip install git+https://github.com/cocodataset/panopticapi.git`
   - 生成 stuff 注释:`python datasets/prepare_panoptic_fpn.py`

4. **LVIS**
   - 安装:`pip install git+https://github.com/lvis-dataset/lvis-api.git`
   - 准备 cocofied LVIS 注释(用于在 COCO 上训练、LVIS 上评估的模型):`python datasets/prepare_cocofied_lvis.py`

5. **Cityscapes**
   - 安装:`pip install git+https://github.com/mcordts/cityscapesScripts.git`
   - 生成训练 ID 标签图(语义分割需要):`CITYSCAPES_DATASET=/path/to/abovementioned/cityscapes python cityscapesscripts/preparation/createTrainIdLabelImgs.py`
   - 生成 Cityscapes 全景数据(全景分割需要):`CITYSCAPES_DATASET=/path/to/abovementioned/cityscapes python cityscapesscripts/preparation/createPanopticImgs.py`

6. **ADE20k Scene Parsing**
   - 生成 detectron2 友好的注释目录:`python datasets/prepare_ade20k_sem_seg.py`

7. **Pascal VOC / COCO / LVIS / ADE20k 数据本体**
   - 需自行从上文【关联】一节列出的官方下载页获取,并按原文中所示目录树摆放;detectron2 不提供自动下载脚本(原文未涉及一键下载入口,仅 COCO 提供了用于测试的 `prepare_for_tests.sh` 极小子集)。
