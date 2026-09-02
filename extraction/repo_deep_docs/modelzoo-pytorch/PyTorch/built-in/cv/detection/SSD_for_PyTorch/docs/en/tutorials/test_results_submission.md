# Tutorial 12: Test Results Submission

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/test_results_submission.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/test_results_submission.md

# 深度解读：Test Results Submission (Panoptic Segmentation)

## 【定位】

本教程解决"如何将 panoptic segmentation 模型在 COCO test-dev 集上的预测结果生成符合 COCO 官方评估服务器要求的提交包"这一完整流程问题，涵盖数据准备、推理执行、结果重命名与打包的全链路操作。

---

## 【技术要点】

1. **数据集三元下载**：必须同时下载 COCO test2017 图像包 (`test2017.zip`)、测试图像元信息 (`image_info_test2017.zip`) 与 panoptic train/val 标注 (`panoptic_annotations_trainval2017.zip`)，统一解压至 `data/coco/` 与 `data/coco/annotations/`。

2. **类别信息补全脚本**：通过 `python tools/misc/gen_coco_panoptic_test_info.py data/coco/annotations` 将 `panoptic_val2017.json` 中的 `isthing` 属性回填到 `image_info_test-dev2017.json` 中——原文明确指出该属性在原始 test-dev 元信息中是**缺失**的。

3. **三种推理执行模式**：
   - 单卡：`CUDA_VISIBLE_DEVICES=0 python tools/test.py`
   - 四卡：`bash tools/dist_test.sh` 并显式传 `4`
   - Slurm：`GPUS=8 tools/slurm_test.sh`（设 `GPUS=8`）

4. **关键推理参数**：`--format-only` 关闭评估计算、仅输出结果文件；`data.test.ann_file` 与 `data.test.img_prefix` 通过 `--cfg-options` 注入测试集路径；`--eval-options jsonfile_prefix=${WORK_DIR}/results` 指定输出前缀。

5. **结果命名规范**：将 `panoptic` 目录与 `results.panoptic.json` 重命名为 `panoptic_test-dev2017_[algorithm_name]_results{,.json}` 形式，并通过 `zip -ur` 打包；要求 zip 包**直接**包含这两个文件，而非嵌套目录。

6. **示例基线模型**：使用 `maskformer_r50_mstrain_16x1_75e_coco.py` 配置 + `maskformer_r50_mstrain_16x1_75e_coco_20220221_141956-bc2699cb.pth` 权重作为可复现样例。

---

## 【关键机制与数据】

- **工作原理（原文）**：由于 `image_info_test-dev2017.json` 中的类别信息**缺少** `isthing` 字段，而 panoptic 推理需要区分 "thing"（可数目标如人、车）与 "stuff"（背景如天空、草地）类别，故必须用 `panoptic_val2017.json` 的类别信息进行补全。
- **数据流（原文）**：`COCO test2017 图像` → `tools/test.py` 加载模型 + 注入测试集路径 → 在 `${WORK_DIR}` 输出 `panoptic/`（mask 目录）+ `results.panoptic.json`（结果 JSON）→ 按命名规范 `mv` 重命名 → `zip` 打包 → 上传 COCO 评估服务器。
- **性能数据**：原文未涉及任何性能指标（如 PQ、mIoU、推理耗时等）。

---

## 【表格解读】

原文中的唯一"表格"是文本形式的目录结构示意图（严格意义上是树状目录），用 markdown 表格逐字还原如下：

| 路径层级 | 文件/目录名 |
|---|---|
| `data/` | (目录) |
| `data/coco/` | (目录) |
| `data/coco/annotations/` | (目录) |
| `data/coco/annotations/image_info_test-dev2017.json` | 由 `gen_coco_panoptic_test_info.py` 生成的文件 |
| `data/coco/annotations/image_info_test2017.json` | 原始下载的测试图像元信息 |
| `data/coco/annotations/panoptic_image_info_test-dev2017.json` | 由 `gen_coco_panoptic_test_info.py` 生成的 panoptic 版测试元信息 |
| `data/coco/annotations/panoptic_train2017.json` | panoptic 训练集标注 JSON |
| `data/coco/annotations/panoptic_train2017.zip` | panoptic 训练集标注压缩包 |
| `data/coco/annotations/panoptic_val2017.json` | panoptic 验证集标注 JSON |
| `data/coco/annotations/panoptic_val2017.zip` | panoptic 验证集标注压缩包 |
| `data/coco/test2017/` | 测试图像目录 |

**逐行解读**：
- `image_info_test-dev2017.json` 与 `panoptic_image_info_test-dev2017.json` 是 `gen_coco_panoptic_test_info.py` 脚本运行后的**生成产物**，其中后者是 panoptic 推理实际加载的标注文件（见推理命令中的 `data.test.ann_file`）。
- 训练集 (`panoptic_train2017`) 与验证集 (`panoptic_val2017`) 标注虽然下载，但**主要用途**是为补全 `isthing` 字段提供权威类别来源，并非训练用途——这反映出 test-dev 推理流程对 val 标注的依赖。
- 测试图像 `test2017` 与 `annotations` 平级存放，符合 mmdet/mmdetection 标准数据布局约定。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游/数据源**：
  - [COCO 官方下载](http://images.cocodataset.org/zips/test2017.zip) — 原始测试图像
  - [COCO 评估服务器](https://competitions.codalab.org/competitions/19507) — 最终提交目标
  - [COCO 命名规范页](https://cocodataset.org/#upload) — 决定 `mv` 重命名规则

- **同仓工具脚本**：
  - `tools/misc/gen_coco_panoptic_test_info.py` — 类别信息补全
  - `tools/test.py` — 单卡/单进程推理入口
  - `tools/dist_test.sh` — 多卡分布式推理包装
  - `tools/slurm_test.sh` — 集群调度推理入口

- **模型配置示例**：引用了 MaskFormer 系列的 `maskformer_r50_mstrain_16x1_75e_coco.py` 与对应权重 `.pth`，提示该流程主要服务于 MaskFormer 这类 mask classification 范式的 panoptic 模型，而非 box-based 检测器。

- **下游**：本教程不涉及提交后的评分解析，提交后流程由 COCO 评估服务器侧处理。

---

## 【使用方法】

**Step 1 — 数据下载与解压（原文命令）**：
```shell
mkdir -pv data/coco/
wget -P data/coco/ http://images.cocodataset.org/zips/test2017.zip
wget -P data/coco/ http://images.cocodataset.org/annotations/image_info_test2017.zip
wget -P data/coco/ http://images.cocodataset.org/annotations/panoptic_annotations_trainval2017.zip
unzip data/coco/test2017.zip -d data/coco/
unzip data/coco/image_info_test2017.zip -d data/coco/
unzip data/coco/panoptic_annotations_trainval2017.zip -d data/coco/
rm -rf data/coco/test2017.zip data/coco/image_info_test2017.zip data/coco/panoptic_annotations_trainval2017.zip
```

**Step 2 — 类别信息补全（原文命令）**：
```shell
python tools/misc/gen_coco_panoptic_test_info.py data/coco/annotations
```

**Step 3 — 单卡推理（原文命令）**：
```shell
CUDA_VISIBLE_DEVICES=0 python tools/test.py \
    ${CONFIG_FILE} \
    ${CHECKPOINT_FILE} \
    --format-only \
    --cfg-options data.test.ann_file=data/coco/annotations/panoptic_image_info_test-dev2017.json data.test.img_prefix=data/coco/test2017 \
    --eval-options jsonfile_prefix=${WORK_DIR}/results
```

**Step 4 — 四卡分布式推理（原文命令）**：
```shell
CUDA_VISIBLE_DEVICES=0,1,3,4 bash tools/dist_test.sh \
    ${CONFIG_FILE} \
    ${CHECKPOINT_FILE} \
    4 \
    --format-only \
    --cfg-options data.test.ann_file=data/coco/annotations/panoptic_image_info_test-dev2017.json data.test.img_prefix=data/coco/test2017 \
    --eval-options jsonfile_prefix=${WORK_DIR}/results
```

**Step 5 — Slurm 集群推理（原文命令）**：
```shell
GPUS=8 tools/slurm_test.sh \
    ${Partition} \
    ${JOB_NAME} \
    ${CONFIG_FILE} \
    ${CHECKPOINT_FILE} \
    --format-only \
    --cfg-options data.test.ann_file=data/coco/annotations/panoptic_image_info_test-dev2017.json data.test.img_prefix=data/coco/test2017 \
    --eval-options jsonfile_prefix=${WORK_DIR}/results
```

**Step 6 — 文件重命名与打包（原文命令）**：
```shell
cd ${WORK_DIR}
mv ./panoptic ./panoptic_test-dev2017_[algorithm_name]_results
mv ./results.panoptic.json ./panoptic_test-dev2017_[algorithm_name]_results.json
zip panoptic_test-dev2017_[algorithm_name]_results.zip -ur panoptic_test-dev2017_[algorithm_name]_results panoptic_test-dev2017_[algorithm_name]_results.json
```

**关键配置项速查**：
| 配置项 / 参数 | 作用 |
|---|---|
| `--format-only` | 仅格式化输出结果，跳过评估指标计算 |
| `--cfg-options data.test.ann_file=...` | 覆盖配置文件中测试集标注路径 |
| `--cfg-options data.test.img_prefix=...` | 覆盖配置文件中测试图像根目录 |
| `--eval-options jsonfile_prefix=...` | 指定 panoptic 结果 JSON 与 mask 目录的输出前缀 |
| `CUDA_VISIBLE_DEVICES` | 指定可见 GPU 编号 |
| `GPUS=8`（slurm_test.sh 环境变量） | 指定 Slurm 任务使用的 GPU 数量 |
| `${CONFIG_FILE}` | 模型配置文件路径（如 `configs/maskformer/maskformer_r50_mstrain_16x1_75e_coco.py`） |
| `${CHECKPOINT_FILE}` | 模型权重文件路径（如 `checkpoints/maskformer_r50_mstrain_16x1_75e_coco_20220221_141956-bc2699cb.pth`） |
| `${WORK_DIR}` | 工作目录，存放输出结果 |
| `[algorithm_name]` | 用户自定义算法名称占位符，需替换为实际算法名 |

**注意事项（原文约束）**：
- `isthing` 字段缺失是 test-dev 元信息的固有问题，**不可跳过** Step 2。
- 生成的 zip 包必须**直接**包含 `panoptic_test-dev2017_[algorithm_name]_results/` 目录与同名 `.json` 文件，不得存在多余嵌套层。
