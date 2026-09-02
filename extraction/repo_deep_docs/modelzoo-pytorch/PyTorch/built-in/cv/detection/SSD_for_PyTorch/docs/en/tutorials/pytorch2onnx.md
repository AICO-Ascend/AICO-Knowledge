# Tutorial 8: Pytorch to ONNX (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/pytorch2onnx.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/pytorch2onnx.md

# 《Tutorial 8: Pytorch to ONNX (Experimental)》深度解读

---

## 【定位】

这篇文档解决"如何将 PyTorch (MMDetection 风格) 训练好的检测模型导出为 ONNX,并在 ONNX Runtime / TensorRT 后端上进行精度评估"的问题,同时提醒该流程为 **实验性**,推荐改用更新的 MMDeploy 工具链。

---

## 【技术要点】

1. **两条工具链路**:导出端 `tools/deployment/pytorch2onnx.py`、评估端 `tools/deployment/test.py`(原文:"We prepare a tool `tools/deplopyment/test.py` to evaluate ONNX models with ONNXRuntime and TensorRT")。
2. **导出默认参数集合**:`--shape` 默认 `800 1216`、`--opset-version` 默认 `11`、`--input-img` 默认 `tests/data/color.jpg`、`--output-file` 默认 `tmp.onnx`、`--dynamic-export / --show / --verify / --simplify` 默认均为 `False`(原文:"If not specified, it will be set to …")。
3. **实验性后处理开关**:`--skip-postprocess` 默认 `False`,原文明确指出"This is an experimental option. Only work for some single stage models. Users need to implement the post-process by themselves. We do not guarantee the correctness of the exported model."
4. **评估环境差异约束**:CPU 版 `pip install onnx onnxruntime==1.5.1`;GPU 版需先 `pip uninstall onnxruntime` 再 `pip install onnxruntime-gpu`;TensorRT 后端需先 `export ONNX_BACKEND=MMCVTensorRT`。
5. **TensorRT 与 dynamic-export 的互斥约束**:原文"If you want to use the `--dynamic-export` parameter in the TensorRT backend to export ONNX, please remove the `--simplify` parameter, and vice versa."
6. **NMS 参数可注入**:通过 `--cfg-options` 以 `model.test_cfg.deploy_nms_pre=-1` 的形式覆盖 config 中的 NMS 预过滤项(原文示例命令)。

---

## 【关键机制与数据】

- **工作原理(导出)**:输入 `CONFIG_FILE + CHECKPOINT_FILE` → 用 `--input-img` 的真实图像做 torch tracing → 输出 `.onnx` 文件;可叠加 `--verify` 复用 `--test-img` 校验一致性,可叠加 `--show` 打印导出模型结构与检测结果。
- **工作原理(评估)**:将导出的 `.onnx` 模型作为 `MODEL_FILE` 喂给 `test.py`,通过 `--backend onnxruntime|tensorrt` 切换推理后端,按 `--eval` 指定的指标(如 `bbox`、`segm`、`proposal`、`mAP`、`recall`)进行评测。
- **数据流(可视化阈值)**:`--show-score-thr` 默认 `0.3`,低于该分数的检测框不会画到 `--show-dir` 目录中的图片上(原文:"Score threshold. Default is set to `0.3`.")。
- **配置覆盖**:`--cfg-options` 与 `--eval-options` 都接受 `xxx=yyy` 形式的键值对,前者合并到 config,后者作为 `dataset.evaluate()` 的 kwargs(原文)。
- **精度数据(原文表格,见下一节逐行还原)**:所列 6 个模型中 SSD / YOLOv3 / Faster R-CNN(部分)在 PyTorch → ONNX Runtime → TensorRT 三后端的 Box AP 几乎一致;Faster R-CNN 在 TensorRT 上从 37.4 降至 37.0;FCOS / RetinaNet 在三后端呈 0.1 量级下降。
- **后处理跳过机制**:`--skip-postprocess=True` 时导出的模型不包含 NMS 等后处理,需用户自行实现(原文限定"Only work for some single stage models")。

---

## 【表格解读】

原文给出了一张 "Results and Models" 表(文档末尾被截断,最后一行 Cascade R-CNN 未给出数值)。逐字还原如下:

| Model | Config | Metric | PyTorch | ONNX Runtime | TensorRT |
|---|---|---|---|---|---|
| FCOS | `configs/fcos/fcos_r50_caffe_fpn_gn-head_4x4_1x_coco.py` | Box AP | 36.6 | 36.5 | 36.3 |
| FSAF | `configs/fsaf/fsaf_r50_fpn_1x_coco.py` | Box AP | 36.0 | 36.0 | 35.9 |
| RetinaNet | `configs/retinanet/retinanet_r50_fpn_1x_coco.py` | Box AP | 36.5 | 36.4 | 36.3 |
| SSD | `configs/ssd/ssd300_coco.py` | Box AP | 25.6 | 25.6 | 25.6 |
| YOLOv3 | `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py` | Box AP | 33.5 | 33.5 | 33.5 |
| Faster R-CNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` | Box AP | 37.4 | 37.4 | 37.0 |
| Cascade R-CNN | `configs/...(原文被截断,未给出 Config 路径及后端数值)` | — | — | — | — |

**逐行解读**

- **FCOS(anchor-free 单阶段)**:PyTorch 36.6 → ONNX Runtime 36.5(−0.1)→ TensorRT 36.3(相对 PyTorch −0.3);说明 FCOS 在量化/图优化路径下有小幅度精度损失。
- **FSAF(anchor-free 单阶段)**:36.0 → 36.0 → 35.9;ONNX Runtime 与 PyTorch 完全持平,TensorRT 损失 0.1。
- **RetinaNet(anchor-based 单阶段)**:36.5 → 36.4 → 36.3;从 PyTorch 到 TensorRT 累计损失 0.2。
- **SSD**:25.6 → 25.6 → 25.6;三后端完全一致,可作为 ONNX/TensorRT 转换无损的代表。
- **YOLOv3**:33.5 → 33.5 → 33.5;与 SSD 一样,转换链路对该模型无精度影响。
- **Faster R-CNN(two-stage,RPN+RoI)**:37.4 → 37.4 → 37.0;ONNX Runtime 端无损,但 TensorRT 端出现 0.4 的下降,说明 RoI/后处理算子在 TensorRT 路径下需要额外校对。
- **Cascade R-CNN**:原文行未完成,无可读数据。

总体观察(基于原文可读部分):单阶段 anchor-free 模型在三后端普遍存在 ≤0.3 的精度漂移;单阶段 anchor-based 简单模型(SSD、YOLOv3)无损;两阶段模型在 TensorRT 上最易出现精度回退。

---

## 【公式解读】

原文无公式。

(整个 tutorial 涉及的"数值"均为命令行参数与 Box AP,无数学表达式;参数解释通过 `--xxx` 形式给出,而非 LaTeX/伪代码公式。)

---

## 【关联】

- **上游依赖 — 运行环境与 MMDetection 安装**:文末内部链接 `../get_started.md`(出现两次,分别对应"Prepare environment"前置步骤和"Install MMdetection"的 step 2-3)指向入门文档,说明本 tutorial 假设环境、MMCV、MMDetection 已就绪。
- **外部依赖 — MMCV 自定义算子**:导出与评估两个章节都要求按 MMCV 文档 [How to build custom operators for ONNX Runtime](https://github.com/open-mmlab/mmcv/blob/master/docs/en/deployment/onnxruntime_op.md/) 构建自定义算子;TensorRT 评估还依赖 [How to build TensorRT plugins in MMCV](https://mmcv.readthedocs.io/en/latest/deployment/tensorrt_plugin.html)。
- **替代方案 — MMDeploy**:文档开头的提示框 `> ## [Try the new MMDeploy to deploy your model](https://mmdeploy.readthedocs.io/)` 明确宣告 ONNX 导出已被新方案取代,本教程仅作遗留参考。
- **下游 — 评估指标体系**:`--eval` 列举的 `bbox / segm / proposal`(COCO)与 `mAP / recall`(PASCAL VOC)与 MMDetection 数据集评测约定一致,意味着导出的 ONNX 模型在评测语义上仍遵循原框架标准。
- **同级 — NMS 参数覆盖**:通过 `--cfg-options model.test_cfg.deploy_nms_pre=-1` 直接覆盖 config 中的部署期 NMS 行为,体现了"训练 config ↔ 部署 config"的桥接关系(原文示例命令中可见到)。

---

## 【使用方法】

### A. 导出 PyTorch → ONNX

```bash
python tools/deployment/pytorch2onnx.py \
    ${CONFIG_FILE} \
    ${CHECKPOINT_FILE} \
    --output-file ${OUTPUT_FILE} \
    --input-img ${INPUT_IMAGE_PATH} \
    --shape ${IMAGE_SHAPE} \
    --test-img ${TEST_IMAGE_PATH} \
    --opset-version ${OPSET_VERSION} \
    --cfg-options ${CFG_OPTIONS} \
    --dynamic-export \
    --show \
    --verify \
    --simplify
```

**关键参数(原文给出)**
| 参数 | 默认值 / 说明 |
|---|---|
| `config` | 模型 config 路径(必填位置参数) |
| `checkpoint` | checkpoint 路径(必填位置参数) |
| `--output-file` | 默认 `tmp.onnx` |
| `--input-img` | 默认 `tests/data/color.jpg` |
| `--shape` | 默认 `800 1216`(H W) |
| `--test-img` | 默认 `None`,即复用 `--input-img` |
| `--opset-version` | 默认 `11` |
| `--dynamic-export` / `--show` / `--verify` / `--simplify` | 默认 `False` |
| `--cfg-options` | `xxx=yyy` 合并到 config |
| `--skip-postprocess` | 默认 `False`,实验性,仅部分单阶段模型有效 |

**原文示例(以 YOLOv3 为例)**

```bash
python tools/deployment/pytorch2onnx.py \
    configs/yolo/yolov3_d53_mstrain-608_273e_coco.py \
    checkpoints/yolo/yolov3_d53_mstrain-608_273e_coco.pth \
    --output-file checkpoints/yolo/yolov3_d53_mstrain-608_273e_coco.onnx \
    --input-img demo/demo.jpg \
    --test-img tests/data/color.jpg \
    --shape 608 608 \
    --show \
    --verify \
    --dynamic-export \
    --cfg-options \
      model.test_cfg.deploy_nms_pre=-1 \
```

### B. 评估导出的 ONNX 模型

**前置安装**

```shell
pip install onnx onnxruntime==1.5.1
# GPU 版
pip uninstall onnxruntime
pip install onnxruntime-gpu
# TensorRT (可选):按 MMCV 文档构建 TensorRT 插件
```

**运行**

```bash
python tools/deployment/test.py \
    ${CONFIG_FILE} \
    ${MODEL_FILE} \
    --out ${OUTPUT_FILE} \
    --backend ${BACKEND} \
    --format-only ${FORMAT_ONLY} \
    --eval ${EVALUATION_METRICS} \
    --show-dir ${SHOW_DIRECTORY} \
    --show-score-thr ${SHOW_SCORE_THRESHOLD} \
    --cfg-options ${CFG_OPTIONS} \
    --eval-options ${EVALUATION_OPTIONS} \
```

**关键参数(原文给出)**
| 参数 | 说明 |
|---|---|
| `config` / `model` | config 与模型文件路径(位置参数) |
| `--out` | 输出结果文件(pickle 格式) |
| `--backend` | `onnxruntime` 或 `tensorrt` |
| `--format-only` | 仅格式化结果,不评估;默认 `False` |
| `--eval` | `bbox / segm / proposal`(COCO)或 `mAP / recall`(PASCAL VOC) |
| `--show-dir` | 绘制结果图片保存目录 |
| `--show-score-thr` | 默认 `0.3` |
| `--cfg-options` | 合并到 config |
| `--eval-options` | 作为 `dataset.evaluate()` 的 kwargs |

**TensorRT 后端额外要求**

```bash
export ONNX_BACKEND=MMCVTensorRT
```
且若使用 `--dynamic-export`,需去掉 `--simplify`(反之亦然,原文 Notes 段)。

> 注:原文未涉及"如何在 ONNX 模型中关闭/开启 NMS 各算子"的具体 NMS 参数表(章节"The Parameters of Non-Maximum Suppression in ONNX Export"与"Reminders"、"FAQs"在用户提供的原文片段中未出现正文,故此部分不展开)。
