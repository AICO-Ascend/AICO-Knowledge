# Tutorial 12: Test Results Submission

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/test_results_submission.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/test_results_submission.md

# 深度解读:Tutorial 12 — Test Results Submission

---

## 【定位】

本文档描述了如何基于已训练好的全景分割(panoptic segmentation)模型,在 COCO test-dev 集上产出推理结果,并按照 COCO 评估服务器要求的命名与打包规范提交预测结果,以便在官方服务器上获取 test-dev 上的量化分数。

---

## 【技术要点】

1. **数据准备三件套**:需下载三份 COCO 资源 — `test2017.zip`(测试图像)、`image_info_test2017.zip`(测试图元信息)、`panoptic_annotations_trainval2017.zip`(全景分割 train/val 标注),统一解压到 `data/coco/` 下,最终 `data/coco/annotations/` 中应包含 `image_info_test-dev2017.json`、`panoptic_val2017.json`、`panoptic_train2017/zip`、`panoptic_image_info_test-dev2017.json` 等。

2. **类别信息补全**:由于 `image_info_test-dev2017.json` 的类别信息中缺少 `isthing` 属性,必须调用 `python tools/misc/gen_coco_panoptic_test_info.py data/coco/annotations` 用 `panoptic_val2017.json` 的类别信息对其做补丁。

3. **三种推理入口**:分别支持 单 GPU(`CUDA_VISIBLE_DEVICES=0 python tools/test.py ...`)、四 GPU(`tools/dist_test.sh ... 4`)、SLURM(`GPUS=8 tools/slurm_test.sh ...`)。三种方式都需附加 `--format-only`,并通过 `--cfg-options` 重定向 `data.test.ann_file` 到 `panoptic_image_info_test-dev2017.json`、`data.test.img_prefix` 到 `data/coco/test2017`,并通过 `--eval-options jsonfile_prefix=${WORK_DIR}/results` 指定输出前缀。

4. **示例模型**:以 MaskFormer + ResNet-50(`configs/maskformer/maskformer_r50_mstrain_16x1_75e_coco.py` + 对应 `checkpoints/...20220221_141956-bc2699cb.pth`)为典型示例,展示了单卡调用形态。

5. **结果重命名规范**:推理产物为 `${WORK_DIR}/panoptic/` 目录(存放各图 mask)与 `${WORK_DIR}/results.panoptic.json`,需重命名为 `panoptic_test-dev2017_[algorithm_name]_results/` 与 `panoptic_test-dev2017_[algorithm_name]_results.json`,命名遵循 [cocodataset.org/#upload](https://cocodataset.org/#upload) 的约定。

6. **打包约束**:用 `zip ... -ur` 将上述两文件打成 `panoptic_test-dev2017_[algorithm_name]_results.zip`,且 zip 内部必须 **直接** 包含这两个条目,而非再嵌一层目录,然后上传至 [COCO 评估服务器](https://competitions.codalab.org/competitions/19507)。

---

## 【关键机制与数据】

**工作原理 / 数据流**(以原文为限):

- **数据准备阶段**(原文:"Download COCO test dataset images, testing image info, and panoptic train/val annotations... put 'test2017' to `data/coco/`, put json files and annotation files to `data/coco/annotations/`"):从 cocodataset.org 下载 3 份 zip → 解压到 `data/coco/` → 准备 6 个标注/元信息 json(含 panoptic 训练/验证)与 `test2017/` 图像目录。

- **类别信息补丁**(原文:"Since the attribute `isthing` is missing in category information of 'image_info_test-dev2017.json', we need to update it with the category information in 'panoptic_val2017.json'"):由于官方 test-dev 图像信息 JSON 不含 `isthing` 字段,该字段是全景分割判定"thing 类 vs stuff 类"的依据,因此脚本以 panoptic val 标注为源做覆盖更新,生成 `panoptic_image_info_test-dev2017.json` 作为后续测试集标注。

- **推理阶段**(原文:"The commands to perform inference on test2017 are as below"):通过 `tools/test.py` 或分布式 `tools/dist_test.sh` / `tools/slurm_test.sh` 以 `--format-only` 模式输出 JSON 格式的预测结果,而非在本地计算指标(`--eval` 被省略,只保留 `--format-only`),由 `--eval-options jsonfile_prefix=${WORK_DIR}/results` 控制结果文件名。

- **产物重命名与打包**(原文:"the panoptic segmentation results (a json file and a directory where the masks are stored) will be in `WORK_DIR`. We should rename them according to the naming convention described on COCO's Website... Note that the zip file should **directly** contains the above two files"):`WORK_DIR/panoptic/` + `WORK_DIR/results.panoptic.json` → 重命名为 `panoptic_test-dev2017_[algorithm_name]_results/` 与 `..._results.json` → `zip` 命令将两文件压缩,且 zip 内部 **不** 允许再多一层同名父目录。

**性能数据**:原文未涉及任何 mAP/PQ/RQ 等具体数值。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未提供文末内部链接,但提到了以下外部/工具关联,可作为上下游参考:

- **COCO 评估服务器**:[competitions.codalab.org/competitions/19507](https://competitions.codalab.org/competitions/19507),即最终提交预测 zip 的入口,本教程的输出物(`panoptic_test-dev2017_[algorithm_name]_results.zip`)即提交给该服务器。

- **COCO 命名规范页面**:[cocodataset.org/#upload](https://cocodataset.org/#upload),提供 `[algorithm_name]` 占位对应的命名规则与提交说明。

- **数据源(三处 cocodataset.org 下载链接)**:分别对应测试图(`/zips/test2017.zip`)、测试图元信息(`/annotations/image_info_test2017.zip`)、全景 train/val 标注(`/annotations/panoptic_annotations_trainval2017.zip`)。

- **下游工具/脚本**:
  - `tools/misc/gen_coco_panoptic_test_info.py` —— 负责把 `isthing` 属性从 `panoptic_val2017.json` 复制到 test-dev 图像信息中。
  - `tools/test.py` / `tools/dist_test.sh` / `tools/slurm_test.sh` —— 同一推理逻辑的三种调度入口(单卡 / 多机多卡 / SLURM 集群)。

- **示例配置**:与 `configs/maskformer/maskformer_r50_mstrain_16x1_75e_coco.py` 这一配置文件及其 `checkpoints/maskformer_r50_mstrain_16x1_75e_coco_20220221_141956-bc2699cb.pth` 权重配套,演示端到端流程。

---

## 【使用方法】

(原文给出的启用方式与命令按阶段列举,均逐字保留)

**1) 数据下载与目录布局**

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

(原文目录结构)

```text
data
`-- coco
    |-- annotations
    |   |-- image_info_test-dev2017.json
    |   |-- image_info_test2017.json
    |   |-- panoptic_image_info_test-dev2017.json
    |   |-- panoptic_train2017.json
    |   |-- panoptic_train2017.zip
    |   |-- panoptic_val2017.json
    |   `-- panoptic_val2017.zip
    `-- test2017
```

**2) 补全 `isthing` 字段**

```shell
python tools/misc/gen_coco_panoptic_test_info.py data/coco/annotations
```

**3) 在 test-dev 上推理**(以 MaskFormer R50 为例)

```shell
# 单卡
CUDA_VISIBLE_DEVICES=0 python tools/test.py \
    configs/maskformer/maskformer_r50_mstrain_16x1_75e_coco.py \
    checkpoints/maskformer_r50_mstrain_16x1_75e_coco_20220221_141956-bc2699cb.pth \
    --format-only \
    --cfg-options data.test.ann_file=data/coco/annotations/panoptic_image_info_test-dev2017.json data.test.img_prefix=data/coco/test2017 \
    --eval-options jsonfile_prefix=work_dirs/maskformer/results
```

多卡与 SLURM 形式(原文):

```shell
# 四卡
CUDA_VISIBLE_DEVICES=0,1,3,4 bash tools/dist_test.sh \
    ${CONFIG_FILE} ${CHECKPOINT_FILE} 4 \
    --format-only \
    --cfg-options data.test.ann_file=data/coco/annotations/panoptic_image_info_test-dev2017.json data.test.img_prefix=data/coco/test2017 \
    --eval-options jsonfile_prefix=${WORK_DIR}/results

# SLURM(原文 GPUS=8)
GPUS=8 tools/slurm_test.sh ${Partition} ${JOB_NAME} ${CONFIG_FILE} ${CHECKPOINT_FILE} \
    --format-only \
    --cfg-options data.test.ann_file=data/coco/annotations/panoptic_image_info_test-dev2017.json data.test.img_prefix=data/coco/test2017 \
    --eval-options jsonfile_prefix=${WORK_DIR}/results
```

**4) 重命名 + 打包**

```shell
cd ${WORK_DIR}
mv ./panoptic ./panoptic_test-dev2017_[algorithm_name]_results
mv ./results.panoptic.json ./panoptic_test-dev2017_[algorithm_name]_results.json
zip panoptic_test-dev2017_[algorithm_name]_results.zip -ur \
    panoptic_test-dev2017_[algorithm_name]_results \
    panoptic_test-dev2017_[algorithm_name]_results.json
```

随后将生成的 `panoptic_test-dev2017_[algorithm_name]_results.zip` 上传至 [COCO 评估服务器](https://competitions.codalab.org/competitions/19507) 即可在 test-dev 上得到官方评测指标。
