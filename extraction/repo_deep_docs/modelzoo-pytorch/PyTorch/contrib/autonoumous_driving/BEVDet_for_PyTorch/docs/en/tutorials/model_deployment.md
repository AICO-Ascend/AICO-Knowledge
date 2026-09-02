# Tutorial 8: MMDetection3D model deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/model_deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/model_deployment.md

# BEVDet_for_PyTorch — 模型部署文档深度解读

## 【定位】

这篇文档是 MMDetection3D (在 BEVDet_for_PyTorch 仓的 contrib/autonoumous_driving 路径下) 的"Tutorial 8: MMDetection3D model deployment",解决的核心问题是:**如何将训练好的 3D 检测模型从 PyTorch 原生格式,通过 OpenMMLab 的 MMDeploy 框架导出到 ONNX 等推理后端,完成实际部署的端到端流程**,覆盖安装、模型导出、推理调用、可选评估及当前支持的模型清单。

---

## 【技术要点】

1. **部署框架依赖**:使用 OpenMMLab 的 [MMDeploy](https://github.com/open-mmlab/mmdeploy) 作为统一部署入口,需要先 `git clone -b master` 并执行 `git submodule update --init --recursive` 完成子模块初始化。

2. **支持的后端 (backend)**:目前 MMDetection3D 已支持三种推理后端 — OnnxRuntime、TensorRT、OpenVINO(每个后端对应一篇独立文档链接)。TorchScript / NCNN / PPLNN 等后端对 3D 模型未给出"全部支持"。

3. **模型导出主命令**:通过 `tools/deploy.py` 一条命令即可将 MMDetection3D 的 PyTorch 模型转成 ONNX 及后端所需的模型文件,关键可选参数包括 `--test-img`、`--work-dir`、`--calib-dataset-cfg`(int8 模式专属)、`--device`、`--log-level`、`--show`、`--dump-info`。

4. **即用推理 API**:通过 `mmdeploy.apis.inference_model(model_cfg, deploy_cfg, backend_files, img=img, device=device)` 一行调用即可,MMDeploy 内部创建 wrapper 模块,且返回值格式与原始 OpenMMLab repo 保持一致(便于无缝替换)。

5. **可选精度/速度评估**:通过 `tools/test.py` 加载已导出的后端模型文件,使用 `--metrics`、`--show`、`--show-score-thr` 等参数在推理后端直接评估(等价于在原 repo 跑 test)。

6. **支持的模型有限**:表格中明确列出仅 PointPillars 与 CenterPoint (pillar) 两种 3D 检测器已被官方支持,且 CenterPoint **仅支持 pillar 版本**;MMDeploy 版本要求 **>= 0.4.0**。

---

## 【关键机制与数据】

**部署工作流** (原文 Pipeline):

```
① 安装 MMDeploy (master 分支 + 子模块)
        ↓
② 安装 inference backend + 构建 custom ops
        ↓
③ 准备 deploy_cfg / model_cfg / checkpoint / 输入数据
        ↓
④ tools/deploy.py: PyTorch → ONNX → backend model files
        ↓
⑤ inference_model(...) 或 tools/test.py 验证/评估
```

**导出时数据流** (按原文 deploy.py 参数推演):
- **输入侧**:`img` 是用于触发导出的单个点云 (.bin) 或图像文件;`--test-img` 额外提供一个推理测试图(若不指定为 None);`--calib-dataset-cfg` 仅在 int8 量化模式下生效,不指定时使用 model config 中的 "val" 数据集做校准。
- **输出侧**:产物落到 `--work-dir`,并可通过 `--show` 直接可视化检测输出,通过 `--dump-info` 输出供 SDK 使用的额外元信息。
- **设备**:`--device` 默认 cpu,可设为 cuda:0 等 GPU 设备。

**性能/精度评估流程** (原文 test.py 参数):
- 通过 `--model ${BACKEND_MODEL_FILES}` 指定已转换好的后端模型,可选 `--out` 输出 PKL 结果、`--format-only` 仅做格式转换、`--metric-options` 传递评测超参、`--log2file` 把日志落到 `work_dirs/output.txt`。

**版本/限制数据** (原文):
- 原文:MMDploy version >= 0.4.0
- 原文:Currently, CenterPoint has only supported the pillar version

---

## 【表格解读】

**原文"Supported models"表(逐字还原)**:

| Model                | TorchScript | OnnxRuntime | TensorRT | NCNN | PPLNN | OpenVINO | Model config                                                                           |
| -------------------- | :---------: | :---------: | :------: | :--: | :---: | :------: | -------------------------------------------------------------------------------------- |
| PointPillars         |      ?      |      Y      |    Y     |  N   |   N   |    Y     | [config](https://github.com/open-mmlab/mmdetection3d/blob/master/configs/pointpillars) |
| CenterPoint (pillar) |      ?      |      Y      |    Y     |  N   |   N   |    Y     | [config](https://github.com/open-mmlab/mmdetection3d/blob/master/configs/centerpoint)  |

**逐行解读**:

- **表头**:横轴列举了 7 种推理后端(TorchScript / OnnxRuntime / TensorRT / NCNN / PPLNN / OpenVINO)+ 1 列 Model config 链接,纵轴是 2 个模型。
- **PointPillars 行**:TorchScript 标 "?"(原文如此,未给出确切结论);OnnxRuntime、TensorRT、OpenVINO 三个后端标 "Y"(支持);NCNN、PPLNN 标 "N"(不支持);对应配置文件入口是 mmdetection3d master 分支的 `configs/pointpillars`。
- **CenterPoint (pillar) 行**:支持矩阵与 PointPillars 完全一致(TorchScript=?;OnnxRuntime/TensorRT/OpenVINO=Y;NCNN/PPLNN=N);配置入口为 mmdetection3d 的 `configs/centerpoint`。结合文末 Note 强调"CenterPoint has only supported the pillar version",此处仅指 pillar 系 CenterPoint,而非 voxel 系。
- **整体结论**:3D 检测器目前在 MMDeploy 中可用的"确定支持"后端为 OnnxRuntime / TensorRT / OpenVINO 三件套,TorchScript 状态存疑("?"),NCNN 与 PPLNN 明确未支持。

---

## 【公式解读】

**原文无公式**。文档为流程型部署 guide,所有数值化内容以命令行参数形式呈现(如日志级别字符串枚举 `'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'`),未涉及任何数学表达式或算法公式。

---

## 【关联】

文档本身没有文末"内部链接"清单(原文提供的"内部链接:(无)"),其模块间关系主要通过**外部链接**体现:

1. **MMDeploy 主框架**:整篇文档是 MMDeploy 在 MMDetection3D 上的子文档,核心命令 `tools/deploy.py` 与 `tools/test.py` 都运行在 clone 下来的 mmdeploy 仓内(`cd mmdeploy`)。
2. **MMDetection3D (上游)**:model_cfg 与 checkpoint 均来自上游 `${MMDET3D_DIR}`,文档示例使用 PointPillars (KITTI 3D-3class) 与 CenterPoint (nuScenes) 两种配置,验证了与 mmdetection3d configs 的耦合。
3. **后端子文档**:OnnxRuntime / TensorRT / OpenVINO 三篇后端安装指南(链接到 mmdeploy.readthedocs.io)是本文"Prerequisite → Install backend and build custom ops"的直接下游。
4. **MMDeploy 通用教程**:导出阶段引用 `how_to_convert_model.html`、评估阶段引用 `how_to_measure_performance_of_models.html`,二者均为本文档所在仓之外、MMDeploy 仓内的上层 tutorial,作为"想深入时的下一步阅读"。
5. **SDK 集成**:`--dump-info` 参数表明导出会同时产出供下游 SDK 调用的元信息,隐含了与 MMDeploy SDK 的接口约定(但本文未展开 SDK 用法)。

---

## 【使用方法】

### 1. 准备环境(原文 §Prerequisite)

```bash
git clone -b master git@github.com:open-mmlab/mmdeploy.git
cd mmdeploy
git submodule update --init --recursive
```
随后按需安装 OnnxRuntime / TensorRT / OpenVINO 后端并 build custom ops(对应链接在 MMDeploy 官方文档)。

### 2. 导出模型(原文 §Export model)

通用命令模板:

```bash
python ./tools/deploy.py \
    ${DEPLOY_CFG_PATH} \
    ${MODEL_CFG_PATH} \
    ${MODEL_CHECKPOINT_PATH} \
    ${INPUT_IMG} \
    --test-img ${TEST_IMG} \
    --work-dir ${WORK_DIR} \
    --calib-dataset-cfg ${CALIB_DATA_CFG} \
    --device ${DEVICE} \
    --log-level INFO \
    --show \
    --dump-info
```

**关键参数(原文逐条)**:
- `deploy_cfg`:MMDeploy 仓内的 deploy 配置文件路径
- `model_cfg`:OpenMMLab 仓内的模型配置路径
- `checkpoint`:checkpoint 路径
- `img`:用于触发导出的点云/图像文件路径
- `--test-img`:测试用图像(默认 None)
- `--work-dir`:日志与模型保存目录
- `--calib-dataset-cfg`:仅 int8 模式有效;不指定则用 model config 中的 "val" 数据集做校准(默认 None)
- `--device`:转换设备(默认 cpu)
- `--log-level`:`'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'` 之一(默认 INFO)
- `--show`:是否可视化检测输出
- `--dump-info`:是否为 SDK 输出元信息

**示例**(PointPillars + TensorRT + KITTI):

```bash
cd mmdeploy
python tools/deploy.py \
    configs/mmdet3d/voxel-detection/voxel-detection_tensorrt_dynamic-kitti.py \
    ${MMDET3D_DIR}/configs/pointpillars/hv_pointpillars_secfpn_6x8_160e_kitti-3d-3class.py \
    ${MMDET3D_DIR}/checkpoints/hv_pointpillars_secfpn_6x8_160e_kitti-3d-3class_20200620_230421-aa0f3adb.pth \
    ${MMDET3D_DIR}/demo/data/kitti/kitti_000008.bin \
    --work-dir work-dir \
    --device cuda:0 \
    --show
```

### 3. 即时推理(原文 §Inference Model)

```python
from mmdeploy.apis import inference_model

result = inference_model(model_cfg, deploy_cfg, backend_files, img=img, device=device)
```
返回值格式与原 OpenMMLab repo 保持一致。

### 4. 精度/速度评估(原文 §Evaluate model,可选)

```bash
python tools/test.py \
    ${DEPLOY_CFG} \
    ${MODEL_CFG} \
    --model ${BACKEND_MODEL_FILES} \
    [--out ${OUTPUT_PKL_FILE}] \
    [--format-only] \
    [--metrics ${METRICS}] \
    [--show] \
    [--show-dir ${OUTPUT_IMAGE_DIR}] \
    [--show-score-thr ${SHOW_SCORE_THR}] \
    --device ${DEVICE} \
    [--cfg-options ${CFG_OPTIONS}] \
    [--metric-options ${METRIC_OPTIONS}] \
    [--log2file work_dirs/output.txt]
```

**示例**(CenterPoint + OnnxRuntime + CPU):

```bash
cd mmdeploy
python tools/test.py \
    configs/mmdet3d/voxel-detection/voxel-detection_onnxruntime_dynamic.py \
    ${MMDET3D_DIR}/configs/centerpoint/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus.py \
    --model work-dir/end2end.onnx \
    --metrics bbox \
    --device cpu
```

### 5. 版本与限制(原文 §Note)

- MMDeploy 版本 **>= 0.4.0**。
- CenterPoint **仅支持 pillar 版本**;如需 voxel 版 CenterPoint 部署,本文档未给出步骤,需参考 MMDeploy 后续更新。
