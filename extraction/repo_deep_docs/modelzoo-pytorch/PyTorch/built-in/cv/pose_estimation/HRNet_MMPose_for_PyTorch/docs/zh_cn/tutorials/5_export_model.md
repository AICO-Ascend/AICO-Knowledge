# 教程 5：如何导出模型为 onnx 格式

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/5_export_model.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/5_export_model.md

# 一体化深度解读:教程 5 —— 如何导出模型为 ONNX 格式

## 【定位】

本文档是 MMPose 模型部署流水线的入口指南,系统性描述如何将 MMPose 训练得到的 PyTorch 关键点检测模型(以 2D 姿态估计为代表)转换为 [ONNX](https://onnx.ai/) 通用交换格式,以便跨框架部署与跨硬件推理。

## 【技术要点】

1. **导出格式目标**:ONNX(Open Neural Network Exchange)作为框架中立的模型交换标准,使 MMPose 训练产物可脱离原生 PyTorch 运行时被其他推理框架消费。
2. **支持模型范围**(原文列举,非穷举):ResNet、HRNet、HigherHRNet 三类骨干/检测架构,涵盖 MMPose 主流 2D 关键点检测路线。
3. **导出脚本入口**:`tools/deployment/pytorch2onnx.py`,由 MMPose 官方维护,封装了 PyTorch → ONNX 的转换流程。
4. **运行依赖**:`onnx` 与 `onnxruntime` 两个 Python 包,通过 `pip install onnx onnxruntime` 一次性安装。
5. **核心命令行模板**:
   ```shell
   python tools/deployment/pytorch2onnx.py ${CONFIG_FILE} ${CHECKPOINT_FILE} \
       [--shape ${SHAPE}] [--verify] [--show] [--output-file ${OUTPUT_FILE}] \
       [--is-localizer] [--opset-version ${VERSION}]
   ```
   其中 `${CONFIG_FILE}` 与 `${CHECKPOINT_FILE}` 为位置参数(必传),其余为可选标志。
6. **关键默认策略**:`--verify`、`--show` 默认 `False`,`--output-file` 默认 `tmp.onnx`,`--opset-version` 默认 `11`(文档推荐使用更高版本以保稳定性,示例中提及 11)。

## 【关键机制与数据】

**工作原理(基于原文可推得的导出闭环)**:
- 文档给出的脚本调用流程将 **配置文件 + 权重文件** 作为输入,二者必须匹配(MMPose 的标准做法);脚本依据配置构建 PyTorch 模型骨架并加载 checkpoint 权重,随后调用 PyTorch 的 ONNX 导出能力(依赖 `onnx` 包本身)将动态图固化为静态 ONNX 图。
- 验证机制(`--verify`):文档明示"验证项包括是否可运行,数值是否正确等",即导出后用 `onnxruntime` 加载产物并对同一输入前向,与 PyTorch 输出的数值对齐,以确认导出无损或量化精度损失幅度。
- 结构可视化(`--show`):打印导出模型的层级结构,便于开发者核对 ONNX 算子图是否符合预期(尤其在自定义算子/插桩场景)。
- Opset 版本选择(`--opset-version`):决定 ONNX 算子集版本,直接影响新算子支持度与不同推理后端(如 TensorRT、onnxruntime)的兼容性;文档明确建议高版本(举例 11)以确保稳定性。

**输入张量形状约定**(原文):2D 关键点检测模型(以 HRNet 为代表)采用四元组 `$batch $channel $height $width`,示例取 `1 3 256 192`。

**性能数据**:原文未提供导出耗时、ONNX 与 PyTorch 数值误差、显存占用、模型体积等任何量化指标。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **上游依赖(训练侧产出)**:本教程消费 MMPose 训练流程产生的 `CONFIG_FILE` 与 `CHECKPOINT_FILE` 两类产物,二者通常由 MMPose 的 configs/train 流程生成,文档未在此展开训练细节,属于典型的"训练 → 导出 → 部署"链路中的导出节点。
- **下游对接**:导出的 ONNX 文件可在支持 ONNX 的推理引擎(如 onnxruntime、TensorRT、OpenVINO 等)上加载;`onnxruntime` 同时也是导出验证阶段的执行器(因 `pip install` 中同时安装了 onnxruntime)。
- **仓库内关联脚本**:核心脚本 `/tools/deployment/pytorch2onnx.py` 是本教程唯一指明的内部工具,该脚本与 MMPose 的模型注册表(支持 ResNet/HRNet/HigherHRNet 等)耦合,以决定哪些模型可被导出。
- **跨教程关系**:作为教程 5,该文档处于"模型导出与部署"主题块;文档未列出本仓其他教程链接,但其支持的模型(ResNet、HRNet、HigherHRNet)与 MMPose 配置库中同名的 model configs 形成隐式映射。
- **问题反馈回路**:文档末段给出"如导出失败或精度下降可在 repo 提 issue"的反馈通道,表明该导出流程存在已知边界情况(如自定义算子回退、动态 shape 处理等)需用户协同维护。

## 【使用方法】

**启用方式**:在已安装 MMPose 及其依赖的环境中,执行官方提供的导出脚本 `python tools/deployment/pytorch2onnx.py`。

**配置项/命令行参数(原文枚举)**:

| 参数 | 是否必填 | 默认值 | 含义与示例(原文) |
|---|---|---|---|
| `${CONFIG_FILE}` | 必填(位置参数) | — | MMPose 模型配置文件 |
| `${CHECKPOINT_FILE}` | 必填(位置参数) | — | 训练得到的 PyTorch 权重文件 |
| `--shape` | 可选 | 未指定 | 模型输入张量形状;2D 关键点检测模型(如 HRNet)使用 `$batch $channel $height $width`,示例 `1 3 256 192` |
| `--verify` | 可选(flag) | `False` | 是否对导出模型进行验证(含可运行性与数值正确性检查) |
| `--show` | 可选(flag) | `False` | 是否打印导出模型的结构 |
| `--output-file` | 可选 | `tmp.onnx` | 导出的 onnx 模型文件名 |
| `--is-localizer` | 可选(flag) | 原文未给默认值 | 用于本地化(关键点定位)类模型的导出(原文仅列出该标志存在,未描述具体行为) |
| `--opset-version` | 可选 | `11` | ONNX 算子集版本;MMPose 推荐使用高版本(如 11)以确保稳定性 |

**最小可用示例(原文组合)**:
```shell
pip install onnx onnxruntime
python tools/deployment/pytorch2onnx.py ${CONFIG_FILE} ${CHECKPOINT_FILE}
# 默认产物:当前工作目录下的 tmp.onnx
```

**完整示例(原文组合,含可选参数)**:
```shell
python tools/deployment/pytorch2onnx.py ${CONFIG_FILE} ${CHECKPOINT_FILE} \
    --shape 1 3 256 192 --verify --show --output-file hrnet.onnx --opset-version 11
```

**问题处理路径**:导出失败或精度异常时,在本仓库 issue 区反馈(原文措辞:"在本 repo 下提出问题")。
