# Tutorial 8: Pytorch to ONNX (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/pytorch2onnx.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/pytorch2onnx.md

# 一体化深度解读：PyTorch → ONNX 教程文档

---

## 【定位】

本教程文档（Tutorial 8: Pytorch to ONNX, Experimental）面向 MMDetection 用户，描述如何将 PyTorch 检测模型导出为 ONNX 格式，并使用 ONNX Runtime / TensorRT 后端对导出模型进行精度与性能评估的全流程能力，并在文首提示读者"试用更成熟的 MMDeploy"作为迁移方向。

---

## 【技术要点】

1. **导出入口**：`tools/deployment/pytorch2onnx.py`，需传入 `${CONFIG_FILE}` 与 `${CHECKPOINT_FILE}` 两个位置参数。
2. **输入输出控制**：`--input-img` 默认 `tests/data/color.jpg`；`--shape` 默认 `800 1216`；`--test-img` 默认 `None`（回退到 `--input-img`）；`--output-file` 默认 `tmp.onnx`。
3. **ONNX Opset**：`--opset-version` 默认 `11`。
4. **三类开关参数**（默认均为 `False`）：`--dynamic-export`（动态 shape 导出）、`--show`（打印导出模型结构并在 `--verify=True` 时可视化检测结果）、`--verify`（验证导出模型正确性）、`--simplify`（简化导出的 ONNX 模型）。
5. **配置覆盖**：`--cfg-options` 以 `xxx=yyy` 键值对合并进配置文件；实验性选项 `--skip-postprocess`（默认 `False`）仅对部分单阶段模型生效，导出后需用户自行实现后处理。
6. **评估入口**：`tools/deployment/test.py`，支持 `onnxruntime` 与 `tensorrt` 两种后端；`--backend` 指定后端；`--eval` 依数据集选择指标（COCO: `bbox`/`segm`/`proposal`；PASCAL VOC: `mAP`/`recall`）；`--show-score-thr` 默认 `0.3`；评估结果以 pickle 形式输出至 `--out`。
7. **环境依赖**：`pip install onnx onnxruntime==1.5.1`；GPU 环境需先卸载 CPU 版再安装 `onnxruntime-gpu`（与 CUDA/CUDNN 版本强相关）；TensorRT 后端需先 `export ONNX_BACKEND=MMCVTensorRT`，并在 `--dynamic-export` 与 `--simplify` 之间二选一。

---

## 【关键机制与数据】

**工作原理（原文机制串联）**：

1. **追踪（Tracing）路径**：在 `tools/deployment/pytorch2onnx.py` 中以一张 `--input-img` 指定的图像作为示例输入，将 PyTorch 模型沿前向计算图追踪为 ONNX 图，生成 ONNX 文件。
2. **可选精化路径**：`--simplify` 调用图简化工具，产出一个更精简的等价 ONNX；`--dynamic-export` 使输入输出张量具备动态 shape，便于部署到尺寸不固定的场景。
3. **正确性回环**：`--verify` 启用后，使用 `--test-img`（或回退到 `--input-img`）同时跑 PyTorch 模型与 ONNX 模型并对齐结果；`--show` 在此基础上可视化检测输出与打印模型结构。
4. **后处理剥离**：默认导出包含后处理；`--skip-postprocess=True` 仅导出模型本体（不带 NMS 等），由用户在推理端实现——原文明确标注"这是实验性选项，我们不保证正确性"。
5. **多后端推理**：`tools/deployment/test.py` 通过 `--backend` 切换 ONNX Runtime 或 TensorRT，对外暴露 `--eval`/`--format-only`/`--show-dir` 三种结果处理模式：前两者分别评估或仅格式化输出，第三者将检测结果绘制到目录中的图像。
6. **TensorRT 约束**：使用 `--dynamic-export` 时必须移除 `--simplify`，反之亦然——这是 MMCV TensorRT 插件对 ONNX 简化算子兼容性的硬性约束。

**性能数据（原文可见的 Results and Models 表已截断，目前可见 7 行，末行 Cascade R-CNN 不完整）**：原文以 Box AP 为统一指标，对比 PyTorch 原模型、ONNX Runtime、TensorRT 三者精度——下文表格逐字还原。

---

## 【表格解读】

原文给出 Results and Models 表，逐字还原如下（**原文在 Cascade R-CNN 行被截断**，仅 7 行可完整呈现）：

| Model | Config | Metric | PyTorch | ONNX Runtime | TensorRT |
|---|---|---|---|---|---|
| FCOS | `configs/fcos/fcos_r50_caffe_fpn_gn-head_4x4_1x_coco.py` | Box AP | 36.6 | 36.5 | 36.3 |
| FSAF | `configs/fsaf/fsaf_r50_fpn_1x_coco.py` | Box AP | 36.0 | 36.0 | 35.9 |
| RetinaNet | `configs/retinanet/retinanet_r50_fpn_1x_coco.py` | Box AP | 36.5 | 36.4 | 36.3 |
| SSD | `configs/ssd/ssd300_coco.py` | Box AP | 25.6 | 25.6 | 25.6 |
| YOLOv3 | `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py` | Box AP | 33.5 | 33.5 | 33.5 |
| Faster R-CNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` | Box AP | 37.4 | 37.4 | 37.0 |
| Cascade R-CNN | （原文截断） | （原文截断） | （原文截断） | （原文截断） | （原文截断） |

**逐行解读**：

- **FCOS**（anchor-free 单阶段）：PyTorch 36.6 → ONNX Runtime 36.5（−0.1）→ TensorRT 36.3（−0.3），两段折损。
- **FSAF**（anchor-free 单阶段）：PyTorch 36.0 → ONNX Runtime 36.0（无折损）→ TensorRT 35.9（−0.1），精度几乎无损。
- **RetinaNet**（anchor-based 单阶段）：36.5 → 36.4 → 36.3，单调下降 0.1。
- **SSD**：三后端完全一致 25.6，原文体现该模型迁移稳健性最佳。
- **YOLOv3**：三后端完全一致 33.5，同样无精度折损。
- **Faster R-CNN**（两阶段）：37.4 → 37.4 → 37.0，ONNX Runtime 阶段无损，TensorRT 阶段 −0.4，是表中可见最大单步折损。
- **Cascade R-CNN**：原文截断不可见。

**整体观察（基于上述 6 个完整行）**：单阶段模型（SSD、YOLOv3）跨后端几乎无损；anchor-free/anchor-based 单阶段检测器（FCOS、FSAF、RetinaNet）有 ≤0.3 量级的微折损；两阶段 Faster R-CNN 在 TensorRT 上折损最大（−0.4）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

1. **与 `get_started.md` 的上下游关系**：本教程在两个 Prerequisite 节点分别引用 `../get_started.md`——第一次指向 "Prepare environment" 段，依赖其完成的 Python/CUDA/PyTorch 等环境作为前置；第二次指向 "Install MMdetection" 段（步骤 2-3），需在其之上完成 MMCV/ONNX 自定义算子构建后再安装 MMdetection。换言之，本教程以 `get_started.md` 为前置门槛，而非平行模块。
2. **与 MMCV 自定义算子的依赖**：导出与评估两段均强制要求先构建 MMCV 的 ONNX Runtime 自定义算子（外链至 `mmcv/docs/en/deployment/onnxruntime_op.md`），TensorRT 评估则要求构建 MMCV TensorRT 插件（外链至 `mmcv/deployment/tensorrt_plugin.html`）——即本教程的"导出—评估"闭环全部依赖 MMCV 层的算子/插件供应。
3. **与 MMDeploy 的替代关系**：原文首句以醒目提示将读者引导至更成熟方案 MMDeploy（`https://mmdeploy.readthedocs.io/`），这表明本教程在仓库内被定位为"过渡性实验文档"——它保留作为教程参考，但官方推荐新工作迁移到 MMDeploy。
4. **与 `--cfg-options` 的配置链路**：导出与评估两段同时支持 `--cfg-options xxx=yyy` 覆盖配置文件，与 MMDetection 训练流程中的 `cfg-options` 语义一致；导出示例中出现的 `model.test_cfg.deploy_nms_pre=-1` 暗示部署侧 cfg 字段（如 `deploy_nms_pre`）专属于测试/部署分支，是与训练 cfg 解耦的"部署子配置"机制。
5. **与 NMS 参数段的预留链接**：TOC 中已列出 "The Parameters of Non-Maximum Suppression in ONNX Export"，但**原文正文中此节内容缺失**（文档于 Results and Models 表中截断），下游若读此节需结合 MMCV NMSOp 的 `deploy_nms_pre`/`deploy_nms_post` 等字段。

---

## 【使用方法】

**启用方式（原文有，给出逐条命令骨架）**：

**Step 1 — 导出 PyTorch → ONNX（典型命令骨架）**：

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

**Step 2 — 评估导出模型（典型命令骨架）**：

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

**TensorRT 后端附加配置**：先 `export ONNX_BACKEND=MMCVTensorRT`；在 `--dynamic-export` 与 `--simplify` 之间只可启用其一。

**依赖安装命令（原文逐字保留）**：

```shell
pip install onnx onnxruntime==1.5.1
pip uninstall onnxruntime   # 仅 GPU 环境先卸载 CPU 版
pip install onnxruntime-gpu # GPU 环境
```

> 备注：文档原文中"List of supported models exportable to ONNX"、"The Parameters of Non-Maximum Suppression in ONNX Export"、"Reminders"、"FAQs" 四个小节在 TOC 中列出，但**正文于 Results and Models 表格 Cascade R-CNN 行处被截断**，故未涉及；如需启用 `--skip-postprocess`、调整 NMS 部署参数、查阅完整支持的模型清单与 FAQ，需参阅仓库原文后续段落或迁移到 MMDeploy。
