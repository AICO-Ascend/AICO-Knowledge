# 教程 8: MMDet3D 模型部署

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/model_deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/model_deployment.md

【定位】
本文档是「MMDet3D 模型部署」教程（教程 8），解决如何将 OpenMMLab MMDetection3D 训练好的 PyTorch 模型通过 MMDeploy 框架导出并部署到各种推理后端（如 ONNX Runtime、TensorRT、OpenVINO 等）以满足实际部署速度需求的问题。

【技术要点】
1. **部署框架**：使用 MMDeploy（OpenMMLab 系列算法库的部署框架）将训练好的 MMDet3D 模型部署到推理后端；MMDeploy 版本要求 ≥ 0.4.0。
2. **支持的推理后端**（MMDet3D 模型当前支持）：OnnxRuntime、TensorRT、OpenVINO。
3. **模型导出**：通过 `tools/deploy.py` 将 PyTorch 模型转换为 ONNX 模型文件与后端所需模型文件；命令行使用 `${DEPLOY_CFG_PATH} ${MODEL_CFG_PATH} ${MODEL_CHECKPOINT_PATH} ${INPUT_IMG}` 等参数。
4. **模型推理**：通过 `mmdeploy.apis.inference_model` 调用后端 API 进行推理，结果与 OpenMMLab 原始代码库格式一致。
5. **模型测试（可选）**：通过 `tools/test.py` 评估部署后模型的精度与速度，可指定 `--metrics bbox` 等。
7. **模型支持范围**：仅 PointPillars 与 CenterPoint（pillar 版本）受支持，且仅列出 OnnxRuntime/TensorRT/OpenVINO 三项为 Y，其余 TorchScript 显示为 ?，NCNN、PPLNN 为 N。

【关键机制与数据】
**工作原理 / 数据流**：
- 整体流程：安装 MMDeploy（clone + submodule update）→ 安装推理后端并编译自定义算子 → 通过 `deploy.py` 把 MMDet3D PyTorch 模型 + 模型配置 + checkpoint + 校准数据一起转成 ONNX 与后端模型 → 通过 `inference_model` 或后端原生 API 做推理 → 可选用 `test.py` 测量精度与速度。
- `--calib-dataset-cfg`：原文："此参数只在 int8 模式下生效，用于校准数据集配置文件。如果没有指定，将被设置成 `None`，并使用模型配置文件中的 'val' 数据集进行校准。"
- `--device`：原文："用于模型转换的设备。如果没有指定，将被设置成 cpu。"
- `--log-level`：原文选项 `'CRITICAL'，'FATAL'，'ERROR'，'WARN'，'WARNING'，'INFO'，'DEBUG'，'NOTSET'`，缺省 INFO。
- `inference_model`：原文："将创建一个推理后端的模块并为你进行推理。推理结果与模型的 OpenMMLab 代码库具有相同的格式。"

**性能数据**（原文）：未提供任何具体性能数字/吞吐量/延迟等量化指标；仅示例命令以 `cuda:0` / `cpu` 指定运行设备。

【表格解读】
原文表格「支持模型列表」逐字还原：

| Model                | TorchScript | OnnxRuntime | TensorRT | NCNN | PPLNN | OpenVINO | Model config                                                                           |
| -------------------- | :---------: | :---------: | :------: | :--: | :---: | :------: | -------------------------------------------------------------------------------------- |
| PointPillars         |      ?      |      Y      |    Y     |  N   |   N   |    Y     | [config](https://github.com/open-mmlab/mmdetection3d/blob/master/configs/pointpillars) |
| CenterPoint (pillar) |      ?      |      Y      |    Y     |  N   |   N   |    Y     | [config](https://github.com/open-mmlab/mmdetection3d/blob/master/configs/centerpoint)  |

**逐行解读**：
- **PointPillars 行**：TorchScript 状态标 `?`（原文未明确给出结论），OnnxRuntime / TensorRT / OpenVINO 均为 Y（支持），NCNN / PPLNN 为 N（不支持）；Model config 指向 `mmdetection3d/configs/pointpillars`。
- **CenterPoint (pillar) 行**：状态分布与 PointPillars 一致——OnnxRuntime / TensorRT / OpenVINO 为 Y，NCNN / PPLNN 为 N，TorchScript 仍为 `?`；Model config 指向 `mmdetection3d/configs/centerpoint`。注意文档「注意」小节明确："目前 CenterPoint 仅支持了 pillar 版本的。"

【公式解读】
原文无公式。

【关联】
本文档内部链接信息标注为「（无）」。文档中涉及的外部关联项均为参考链接：
- MMDeploy 主仓库及子模块（用于 clone 部署框架）
- 推理后端文档：OnnxRuntime、TensorRT、OpenVINO 三个独立页面
- 模型导出文档：`how_to_convert_model.md`
- 性能测试文档：`how to measure performance of models`
- 模型配置：指向 `mmdetection3d` 仓库的 `configs/pointpillars` 与 `configs/centerpoint` 路径

关系上：本文档是「MMDet3D 模型部署」位于 BEVDet 仓库的教程文档，其上下游是 MMDetection3D（提供待部署模型与配置）与 MMDeploy（提供转换与后端运行时）之间的桥接说明。

【使用方法】
原文给出了完整可执行命令，分为「准备」「模型导出」「模型推理」「测试模型」四个阶段：

- **安装**：
  ```bash
  git clone -b master git@github.com:open-mmlab/mmdeploy.git
  cd mmdeploy
  git submodule update --init --recursive
  ```

- **模型导出（PointPillars + TensorRT 示例）**：
  ```bash
  cd mmdeploy
  python tools/deploy.py \
      configs/mmdet3d/voxel-detection/voxel-detection_tensorrt_dynamic-kitti.py \
      ${$MMDET3D_DIR}/configs/pointpillars/hv_pointpillars_secfpn_6x8_160e_kitti-3d-3class.py \
      ${$MMDET3D_DIR}/checkpoints/hv_pointpillars_secfpn_6x8_160e_kitti-3d-3class_20200620_230421-aa0f3adb.pth \
      ${$MMDET3D_DIR}/demo/data/kitti/kitti_000008.bin \
      --work-dir work-dir \
      --device cuda:0 \
      --show
  ```

- **模型推理（Python API）**：
  ```python
  from mmdeploy.apis import inference_model
  result = inference_model(model_cfg, deploy_cfg, backend_files, img=img, device=device)
  ```

- **测试模型（CenterPoint + OnnxRuntime 示例）**：
  ```bash
  cd mmdeploy
  python tools/test.py \
      configs/mmdet3d/voxel-detection/voxel-detection_onnxruntime_dynamic.py \
      ${MMDET3D_DIR}/configs/centerpoint/centerpoint_02pillar_second_secfpn_circlenms_4x8_cyclic_20e_nus.py \
      --model work-dir/end2end.onnx \
      --metrics bbox \
      --device cpu
  ```

配置项已在「参数描述」段逐项列出，包括 `deploy_cfg`、`model_cfg`、`checkpoint`、`img`、`--test-img`、`--work-dir`、`--calib-dataset-cfg`（仅 int8 生效）、`--device`（缺省 cpu）、`--log-level`（缺省 INFO）、`--show`、`--dump-info`；测试阶段额外可指定 `--out`、`--format-only`、`--metrics`、`--show-dir`、`--show-score-thr`、`--cfg-options`、`--metric-options`、`--log2file`。
