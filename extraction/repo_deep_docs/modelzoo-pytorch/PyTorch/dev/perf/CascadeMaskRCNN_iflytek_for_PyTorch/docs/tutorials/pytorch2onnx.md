# Tutorial 8: Pytorch to ONNX (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/pytorch2onnx.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/pytorch2onnx.md

# 深度解读：Tutorial 8 — Pytorch to ONNX (Experimental)

---

## 【定位】

本文档是 MMDetection 项目中**面向"模型部署到 ONNX"全流程的实验性教程**，系统回答三个核心问题：① 如何将 MMDetection 中的 PyTorch 检测模型转换为 ONNX 格式；② 如何基于 ONNXRuntime / TensorRT 对导出的 ONNX 模型进行精度评测；③ 哪些模型已经验证支持 ONNX 导出与运行。它服务于需要把训练好的检测器落到生产推理环境（跨框架 / 跨硬件）的工程师。

---

## 【技术要点】

1. **导出入口脚本**：`tools/deployment/pytorch2onnx.py`，配套配置文件 `${CONFIG_FILE}` 与权重文件 `${CHECKPOINT_FILE}`，输出 `${OUTPUT_FILE}`（默认 `tmp.onnx`）。
2. **依赖项**：
   - 转换侧：`pip install onnx onnxruntime`
   - 评测侧（GPU 后端）：`pip install onnx onnxruntime-gpu`
3. **图像预处理默认值**（与 MMDetection 默认配置保持一致）：
   - 输入尺寸 `--shape` 默认 `800 1216`
   - 均值 `--mean` 默认 `123.675 116.28 103.53`
   - 标准差 `--std` 默认 `58.395 57.12 57.375`
4. **ONNX 算子集版本**：`--opset-version` 默认 `11`。
5. **关键开关**：
   - `--dynamic-export`：是否导出动态 shape 的 ONNX（默认 `False`）
   - `--verify`：是否校验导出模型的正确性（默认 `False`）
   - `--simplify`：是否对导出的 ONNX 做简化（默认 `False`）
   - `--show`：是否打印导出模型结构，并在 `--verify=True` 时可视化检测输出（默认 `False`）
6. **配置文件覆盖机制**：`--cfg-options` 支持以 `xxx=yyy` 形式覆盖配置文件中的任意项（如示例中的 `model.test_cfg.deploy_nms_pre=-1`）。
7. **独立评测脚本**：`tools/deployment/test.py`（注意原文中路径拼写为 `deplopyment`，疑似 typo），支持 `--backend onnxruntime|tensorrt` 切换推理后端。

---

## 【关键机制与数据】

### 工作流（数据流）

1. **导出阶段**：用户提供 config + checkpoint + 一张追踪图 `--input-img`（默认 `tests/data/color.jpg`），脚本按 `--shape` 构造 dummy input 调用 `torch.onnx.export` 流程，生成 `.onnx` 文件。
2. **校验阶段**（`--verify=True`）：使用 `--test-img`（默认回退到 `--input-img`）在 PyTorch 与 ONNX 后端各跑一次，对比输出。
3. **简化阶段**（`--simplify=True`）：通过 onnx-simplifier 等工具去除冗余算子。
4. **评测阶段**：使用 `tools/deployment/test.py`，把 config + 导出的 `.onnx` 喂入 ONNXRuntime / TensorRT，按 `--eval` 指定的指标（如 `bbox`、`segm`、`proposal` 对应 COCO；`mAP`、`recall` 对应 PASCAL VOC）计算精度。

### 性能数据（原文表格，详见下节）

- 绝大多数检测模型 PyTorch → ONNXRuntime → TensorRT 三者 Box AP 差异在 **0.1~0.4** 以内；
- **Mask R-CNN 的 Mask AP 出现 1% 跌幅**（PyTorch 34.7 → ONNXRuntime 33.7 → TensorRT 33.3），原文归因为：PyTorch 中预测 mask 直接插值回原图分辨率，而 ONNXRuntime/TensorRT 流程是先插值回预处理后的输入图，再二次映射回原图。
- **CornerNet 仅在 PyTorch 与 ONNXRuntime 两栏给出**（40.6 / 40.4），无 TensorRT 数据，原文解释：ONNX Runtime 当前仅支持单尺度评估，CornerNet 评测时关闭了 test-time flip。
- **评测条件**：所有 ONNX 模型均使用 dynamic shape，按原始 config 的预处理流程在 COCO 数据集上评测。

---

## 【表格解读】

### 表格 1：Results and Models（PyTorch / ONNX Runtime / TensorRT 精度对比）

| Model | Config | Metric | PyTorch | ONNX Runtime | TensorRT |
|---|---|---|---|---|---|
| FCOS | `configs/fcos/fcos_r50_caffe_fpn_gn-head_4x4_1x_coco.py` | Box AP | 36.6 | 36.5 | 36.3 |
| FSAF | `configs/fsaf/fsaf_r50_fpn_1x_coco.py` | Box AP | 36.0 | 36.0 | 35.9 |
| RetinaNet | `configs/retinanet/retinanet_r50_fpn_1x_coco.py` | Box AP | 36.5 | 36.4 | 36.3 |
| SSD | `configs/ssd/ssd300_coco.py` | Box AP | 25.6 | 25.6 | 25.6 |
| YOLOv3 | `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py` | Box AP | 33.5 | 33.5 | 33.5 |
| Faster R-CNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` | Box AP | 37.4 | 37.4 | 37.0 |
| Mask R-CNN | `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py` | Box AP | 38.2 | 38.1 | 37.7 |
| Mask R-CNN | `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py` | Mask AP | 34.7 | 33.7 | 33.3 |
| CornerNet | `configs/cornernet/cornernet_hourglass104_mstest_10x5_210e_coco.py` | Box AP | 40.6 | 40.4 | （空） |

**逐行解读**：
- **FCOS / FSAF / RetinaNet**：单阶段 anchor-based / anchor-free 检测器的代表，三个后端的 Box AP 差距均在 0.1~0.2，验证 ONNX 导出的高保真度。
- **SSD**：三端 Box AP 完全一致（25.6），说明 SSD300 这种较为静态的网络在 ONNX 转换中损失为零。
- **YOLOv3**：三端 Box AP 完全一致（33.5），进一步证明 backbone-neck-head 结构在该工具链下转换无损。
- **Faster R-CNN**：PyTorch 与 ONNXRuntime 完全一致（37.4），TensorRT 出现 0.4 跌幅（37.0），可能源自 TensorRT 对部分算子的近似优化。
- **Mask R-CNN**（跨两行的合并单元格）：Box AP 在三端差距较小（≤0.5），但 Mask AP 从 34.7 一路跌到 33.3（合计 1.4 个点）。原文已在 Notes 中给出根因：mask 插值的中间分辨率选择不同。
- **CornerNet**：仅两栏数据，且与 PyTorch 差距 0.2。原文指出原因——ONNX Runtime 目前不支持 test-time flip，且只能单尺度评估，因此精度略低。

### 表格 2：List of supported models exportable to ONNX

**原文无表格**（原文在 `List of supported models exportable to ONNX` 一节开头写出了表头 `| Model | Config |` 与 `---` 分隔符，但表格正文在所提供的片段中已被截断，未见任何数据行，故按"原文无表格"处理）。

---

## 【公式解读】

**原文无公式**（整篇文档不涉及 LaTeX 或伪代码形式的数学公式，仅以命令行参数和参数说明列表呈现）。

---

## 【关联】

1. **`../get_started.md`**：Prerequisite 一节明确指引读者先按 `get_started.md` 完成 MMCV 与 MMDetection 的安装，是本文档的前置依赖入口。
2. **`tools/deployment/pytorch2onnx.py`**：本文档主脚本，承载 PyTorch → ONNX 的导出。
3. **`tools/deployment/test.py`**（原文路径写作 `deplopyment`，疑似 typo）：用于评估 ONNX 模型的评测脚本，与导出脚本形成"导出—评测"闭环。
4. **`onnx` / `onnxruntime(-gpu)`**：跨框架推理运行时，是评测与导出的运行时支撑。
5. **TensorRT 后端**：通过 `onnxruntime` 或独立 TensorRT 引擎执行导出的 ONNX 模型，是生产部署的常见目标。
6. **被引用的配置文件**（在示例与结果表中出现）：
   - `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`
   - `configs/fcos/fcos_r50_caffe_fpn_gn-head_4x4_1x_coco.py`
   - `configs/fsaf/fsaf_r50_fpn_1x_coco.py`
   - `configs/retinanet/retinanet_r50_fpn_1x_coco.py`
   - `configs/ssd/ssd300_coco.py`
   - `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`
   - `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py`
   - `configs/cornernet/cornernet_hourglass104_mstest_10x5_210e_coco.py`
   
   这些 config 与上游 `configs/` 体系直接挂钩，评测时通过 `--cfg-options` 还能覆盖 `model.test_cfg.deploy_nms_pre` 等与部署相关的子项，连接训练侧与部署侧。
7. **后文小节（文档截断处）**：原 TOC 显示还有 *The Parameters of Non-Maximum Suppression in ONNX Export*、*Reminders*、*FAQs* 三节，**但所提供的原文片段在 "List of supported models exportable to ONNX" 表头之后即截止**，因此后续 NMS 参数、注意事项、FAQ 内容**原文未涉及**，不予臆造。

---

## 【使用方法】

### 1. 导出 ONNX 模型

```bash
python tools/deployment/pytorch2onnx.py \
    ${CONFIG_FILE} \
    ${CHECKPOINT_FILE} \
    --output-file ${OUTPUT_FILE} \
    --input-img ${INPUT_IMAGE_PATH} \
    --shape ${IMAGE_SHAPE} \
    --mean ${IMAGE_MEAN} \
    --std ${IMAGE_STD} \
    --dataset ${DATASET_NAME} \
    --test-img ${TEST_IMAGE_PATH} \
    --opset-version ${OPSET_VERSION} \
    --cfg-options ${CFG_OPTIONS} \
    --dynamic-export \
    --show \
    --verify \
    --simplify
```

**可调参数清单**（默认值见【技术要点】第 3、4、5 条）：

| 参数 | 类型 | 默认值 | 作用 |
|---|---|---|---|
| `config` | 位置参数 | — | 模型 config 路径 |
| `checkpoint` | 位置参数 | — | checkpoint 路径 |
| `--output-file` | str | `tmp.onnx` | ONNX 输出路径 |
| `--input-img` | str | `tests/data/color.jpg` | 追踪用输入图 |
| `--shape` | int×2 | `800 1216` | 输入 H、W |
| `--mean` | float×3 | `123.675 116.28 103.53` | 输入均值 |
| `--std` | float×3 | `58.395 57.12 57.375` | 输入标准差 |
| `--dataset` | str | `coco` | 数据集名 |
| `--test-img` | str | `None`（回退到 `--input-img`） | 验证用图 |
| `--opset-version` | int | `11` | ONNX opset 版本 |
| `--dynamic-export` | flag | `False` | 动态 shape 导出 |
| `--show` | flag | `False` | 打印结构/可视化检测输出 |
| `--verify` | flag | `False` | 校验 ONNX 模型 |
| `--simplify` | flag | `False` | 简化 ONNX |
| `--cfg-options` | kv | — | `xxx=yyy` 覆盖 config 项 |

### 2. 完整示例（YOLOv3）

```bash
python tools/deployment/pytorch2onnx.py \
    configs/yolo/yolov3_d53_mstrain-608_273e_coco.py \
    checkpoints/yolo/yolov3_d53_mstrain-608_273e_coco.pth \
    --output-file checkpoints/yolo/yolov3_d53_mstrain-608_273e_coco.onnx \
    --input-img demo/demo.jpg \
    --test-img tests/data/color.jpg \
    --shape 608 608 \
    --mean 0 0 0 \
    --std 255 255 255 \
    --show \
    --verify \
    --dynamic-export \
    --cfg-options \
      model.test_cfg.deploy_nms_pre=-1
```

### 3. 评测 ONNX 模型

```bash
python tools/deployment/test.py \
    ${CONFIG_FILE} \
    ${MODEL_FILE} \
    --out ${OUTPUT_FILE} \
    --backend ${BACKEND} \
    --format-only ${FORMAT_ONLY} \
    --eval ${EVALUATION_METRICS} \
    --show-dir ${SHOW_DIRECTORY} \
    ----show-score-thr ${SHOW_SCORE_THRESHOLD} \
    ----cfg-options ${CFG_OPTIONS} \
    ----eval-options ${EVALUATION_OPTIONS}
```

> 注：原文 `test.py` 命令块中存在 `----show-score-thr / ----cfg-options / ----eval-options` 共 **四个连字符** 的写法，与同一命令块中的 `--out / --backend / --eval`（两个连字符）不一致，疑似 markdown 笔误，**保留原文写法以避免臆改**，实际使用时请以仓库最新版本为准。

**`test.py` 参数**：

| 参数 | 默认 / 取值 | 说明 |
|---|---|---|
| `config` | — | config 路径 |
| `model` | — | 输入模型路径 |
| `--out` | — | pickle 格式结果输出 |
| `--backend` | `onnxruntime` / `tensorrt` | 推理后端 |
| `--format-only` | `False` | 仅格式化输出，不做评测 |
| `--eval` | `bbox`/`segm`/`proposal`（COCO）；`mAP`/`recall`（VOC） | 评测指标 |
| `--show-dir` | — | 可视化结果保存目录 |
| `--show-score-thr` | `0.3` | 可视化阈值 |
| `--cfg-options` | — | 覆盖 config 项（kv 形式） |
| `--eval-options` | — | 透传给 `dataset.evaluate()` 的 kwargs |

---

**说明**：文档原 TOC 显示 *The Parameters of Non-Maximum Suppression in ONNX Export*、*Reminders*、*FAQs*、以及 *List of supported models* 的表格正文均位于所提供片段之外，**原文未涉及**对应细节，本解读未做推断性补全。
