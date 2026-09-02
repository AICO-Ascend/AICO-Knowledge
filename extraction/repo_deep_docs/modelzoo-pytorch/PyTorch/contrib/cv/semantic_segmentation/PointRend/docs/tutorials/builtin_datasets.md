# Use Builtin Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/builtin_datasets.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/builtin_datasets.md

# 「PointRend · Use Builtin Datasets」一体化深度解读

---

## 【定位】
本篇文档解决 **Detectron2 内置数据集（COCO / LVIS / Cityscapes / Pascal VOC / ADE20k / PanopticFPN）的目录布局与环境变量配置问题**，使它们能被 PointRend 等模型通过统一的 `DatasetCatalog` / `MetadataCatalog` API 访问。

---

## 【技术要点】

1. **统一访问入口**：数据集通过 `DatasetCatalog` 取数据、`MetadataCatalog` 取元信息（类别名等），所有内置数据集必须按本文规定的目录结构摆放才能被这两个 Catalog 识别。
2. **环境变量控制路径**：`DETECTRON2_DATASETS` 指定数据集根目录，可通过 `export DETECTRON2_DATASETS=/path/to/datasets` 设置；缺省值为当前工作目录下的 `./datasets`。
3. **期望的根目录结构**：detectron2 在 `DETECTRON2_DATASETS` 下按以下四个子目录查找：
   ```
   $DETECTRON2_DATASETS/
     coco/
     lvis/
     cityscapes/
     VOC20{07,12}/
   ```
4. **多数据集类型复用 `coco/` 目录**：COCO instance/keypoint、PanopticFPN、LVIS 三个任务的数据都放在同一个 `coco/` 子目录下，但要求不同的子文件（annotations 子集、`panoptic_*` png、`lvis_*.json` 等）。
5. **若干数据集需要预处理脚本**：PanopticFPN 需 `python datasets/prepare_panoptic_fpn.py`、LVIS 需 `python datasets/prepare_cocofied_lvis.py`、ADE20k 需 `python datasets/prepare_ade20k_sem_seg.py`，cityscapes 的 panoptic / trainId 标注也需由 `cityscapesscripts` 生成。
6. **外部依赖需手动安装**：`panopticapi`、`lvis-api`、`cityscapesScripts` 三个 Git 仓库需通过 `pip install git+https://...` 安装；测试时还有 `./datasets/prepare_for_tests.sh` 下载 COCO 微型版。

---

## 【关键机制与数据】

**工作机制（原文信息整合）**：

- **数据流**：用户把数据集按指定目录结构放在 `DETECTRON2_DATASETS` 路径下 → detectron2 启动时通过 `DatasetCatalog` 读取文件路径列表 → 通过 `MetadataCatalog` 读取类别名等元数据 → PointRend 等模型据此训练/评测。
- **默认行为**：若未设置 `DETECTRON2_DATASETS`，则以当前工作目录的 `./datasets` 作为根（即默认认为数据集与代码同级）。
- **COCO 版本兼容**：原文明确"You can use the 2014 version of the dataset as well"，即 `instances_{train,val}2014.json`、`person_keypoints_{train,val}2014.json`、`{train,val}2014/` 也可被识别。
- **PanopticFPN 双步准备**：第一步安装 `panopticapi`；第二步运行 `python datasets/prepare_panoptic_fpn.py`，将 panoptic 注释拆出语义部分，生成 `panoptic_stuff_{train,val}2017/`。
- **Cityscapes 三类标注**：
  - 实例分割：`gtFine/` 下的 `instanceIds.png` + `leftImg8bit/` 原图；
  - 语义分割：需先生成 `labelTrainIds.png`（运行 `createTrainIdLabelImgs.py`）；
  - 全景分割：需生成 `cityscapes_panoptic_{train,val,test}.json` 和对应 png 目录（运行 `createPanopticImgs.py`）。
  - 原文注释明确："These files are not needed for instance segmentation"（语义/全景标注对纯实例任务非必需）。
- **LVIS 评估复用 COCO**：通过 `python datasets/prepare_cocofied_lvis.py` 产生"cocofied" LVIS 标注，可在 COCO 训练的模型上用 LVIS 注释评测。
- **测试用微型数据集**：`dev/run_*_tests.sh` 调用 `./datasets/prepare_for_tests.sh` 下载迷你版 COCO，用于单元测试。

**性能数据**：原文未涉及任何训练/推理耗时、mAP、IoU 等性能数字。

---

## 【表格解读】

**原文无表格**。

（补充说明：原文以**代码块**形式罗列了各数据集的目录树结构，例如 `coco/annotations/instances_{train,val}2017.json` 等。这些属于目录布局约定，不是 markdown 表格，未在原文以表格形式出现，故不作逐字还原。）

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

根据原文内容，与之相关的模块/特性/上下游如下（均无内部链接可跳转，按提示标注）：

| 关联对象 | 关系性质 | 上下文 |
|---|---|---|
| `DatasetCatalog` / `MetadataCatalog` | 上游 API | 数据集被注册后供 PointRend 等模型调用 |
| `MODEL_ZOO.md`（model zoo） | 平行资源 | 包含使用本篇所述内置数据集的 configs 与预训练模型 |
| `tutorials/datasets.html`（Use Custom Datasets） | 平行教程 | 讲解 `DatasetCatalog` / `MetadataCatalog` 的深度用法及如何新增自定义数据集 |
| `dev/run_*_tests.sh` + `datasets/prepare_for_tests.sh` | 下游测试链路 | 单元测试依赖本篇定义的目录结构，使用微型 COCO |
| `datasets/prepare_panoptic_fpn.py` | 配套脚本 | 为 PanopticFPN 生成 `panoptic_stuff_*` 目录 |
| `datasets/prepare_cocofied_lvis.py` | 配套脚本 | 为 COCO→LVIS 评测生成 cocofied 标注 |
| `datasets/prepare_ade20k_sem_seg.py` | 配套脚本 | 生成 `annotations_detectron2/` |
| `cityscapesscripts/preparation/createTrainIdLabelImgs.py` | 外部脚本 | 生成 `labelTrainIds.png`（语义分割用） |
| `cityscapesscripts/preparation/createPanopticImgs.py` | 外部脚本 | 生成 Cityscapes 全景标注 |
| `panopticapi`、`lvis-api`、`cityscapesScripts` | 外部 Python 包 | 三个数据集的工具库，需 `pip install git+...` 安装 |

---

## 【使用方法】

### 1. 设置数据集根目录（原文）
```bash
export DETECTRON2_DATASETS=/path/to/datasets
```
未设置时，默认值为 `./datasets`（相对于当前工作目录）。

### 2. 准备各数据集的依赖与预处理脚本（原文逐字命令）

**PanopticFPN**
```bash
pip install git+https://github.com/cocodataset/panopticapi.git
python datasets/prepare_panoptic_fpn.py
```

**LVIS**
```bash
pip install git+https://github.com/lvis-dataset/lvis-api.git
# 可选：用于 COCO→LVIS 评测
python datasets/prepare_cocofied_lvis.py
```

**Cityscapes**
```bash
pip install git+https://github.com/mcordts/cityscapesScripts.git
# 语义分割需要：
CITYSCAPES_DATASET=/path/to/abovementioned/cityscapes \
  python cityscapesscripts/preparation/createTrainIdLabelImgs.py
# 全景分割需要：
CITYSCAPES_DATASET=/path/to/abovementioned/cityscapes \
  python cityscapesscripts/preparation/createPanopticImgs.py
```

**测试用微型 COCO**
```bash
./datasets/prepare_for_tests.sh
```

### 3. 各数据集目录结构关键配置项（按原文）
- **COCO instance/keypoint**：`coco/annotations/instances_{train,val}2017.json`、`person_keypoints_{train,val}2017.json`，图片目录 `{train,val}2017/`。
- **PanopticFPN**：`coco/annotations/panoptic_{train,val}2017.json`、`panoptic_{train,val}2017/`、`panoptic_stuff_{train,val}2017/`（最后一个由脚本生成）。
- **LVIS**：`coco/{train,val,test}2017/` + `lvis/lvis_v0.5_{train,val}.json`、`lvis_v1_{train,val}.json` 等。
- **Cityscapes**：`cityscapes/gtFine/{train,val,test}/` + `cityscapes/leftImg8bit/{train,val,test}/`。
- **Pascal VOC**：`VOC20{07,12}/Annotations/`、`ImageSets/Main/{trainval,test}.txt`、`JPEGImages/`。
- **ADE20k**：`ADEChallengeData2016/annotations/`、`annotations_detectron2/`（由脚本生成）、`images/`、`objectInfo150.txt`。
