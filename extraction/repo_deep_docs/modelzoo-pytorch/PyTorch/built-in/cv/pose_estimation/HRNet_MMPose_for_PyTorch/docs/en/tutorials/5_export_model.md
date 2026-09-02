# Tutorial 5: Exporting a model to ONNX

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/5_export_model.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/5_export_model.md

# 深度解读:Tutorial 5: Exporting a model to ONNX

---

## 【定位】

这篇文档解决的是如何将 MMPose 框架下基于 PyTorch 训练好的姿态估计/关键点检测模型导出为 ONNX 格式的问题,使模型脱离 PyTorch 运行时、进入开放的 ONNX 生态,便于跨平台部署与后续推理。

---

## 【技术要点】

1. **支持导出的模型范围**:仅限由 MMPose 训练出来的 PyTorch 模型,具体支持三类主干网络 —— **ResNet**、**HRNet**、**HigherHRNet**(原文无其他网络)。
2. **核心工具脚本**:`tools/deployment/pytorch2onnx.py`(正文给出运行命令路径),同时文中以链接形式引用 `/tools/pytorch2onnx.py`(原文链接文本与命令行路径存在轻微不一致,以原文为准同时呈现)。
3. **环境依赖(Prerequisite)**:导出后还需做可运行性与数值验证,因此必须安装 `onnx` 与 `onnxruntime`,命令为 `pip install onnx onnxruntime`。
4. **默认输入张量形状**:`--shape` 未指定时回退到 `1 3 256 192`(即 batch=1、通道=3、高=256、宽=192)。
5. **默认 ONNX Opset 版本**:`--opset-version` 未指定时为 `11`,且原文明确**推荐使用更高版本(如 11 及以上)**以保证兼容性。
6. **辅助开关**: `--verify` 默认 `False`(控制是否对导出模型做可运行性与数值校验)、`--show` 默认 `False`(控制是否打印导出模型的网络结构)、`--output-file` 默认 `tmp.onnx`(导出文件名)。

---

## 【关键机制与数据】

整篇文档的核心工作原理是一条线性流水线,**完全沿用原文表述**而未补充任何臆造数据:

- **数据流(原文)**: `${CONFIG_FILE}`(模型配置文件) + `${CHECKPOINT_FILE}`(训练好的权重) → 经 `tools/deployment/pytorch2onnx.py` → 生成 ONNX 模型 → 若开启 `--verify`,则调用 `onnxruntime` 对导出模型做**可运行性 + 数值一致性**校验。
- **可选可视化(原文)**:`--show` 用于打印导出后 ONNX 模型的架构。
- **配置覆盖机制(原文)**:所有可选参数都有"未指定 → 回退默认值"的设计,默认值见上一节【技术要点】。
- **质量反馈机制(原文)**:对于"导出存在精度损失或转换不完整"的 checkpoint,原文要求用户通过 fire an issue 反馈,即质量保障走社区 issue 渠道,而非文档内置检测。
- **性能/精度数据**:原文**未提供**任何导出前后的 mAP/PCK/速度/显存等数值。

---

## 【表格解读】

**原文无表格。**

(整篇文档以「命令模板 + 列表式可选参数说明」形式承载信息,未出现参数表、性能对比表或配置矩阵。)

---

## 【公式解读】

**原文无公式。**

(导出过程在本文档层面被抽象为单条 CLI 调用,不涉及损失、坐标解码、热力图等数学表达,故无 LaTeX 或伪代码公式。)

---

## 【关联】

依据文末/文中出现的内部与外部引用,本文档与下列模块/生态存在明确上下游关系:

- **核心关联脚本**:`/tools/pytorch2onnx.py`(原文链接形式给出) / `tools/deployment/pytorch2onnx.py`(原文命令行形式给出) —— 本教程的所有能力都封装在该脚本中,该脚本即本文档的"实现主体"。
- **上游**:MMPose 的 **config + checkpoint** 工作流(训练阶段产物)。文档明确说导出对象是「pytorch models trained with MMPose」,因此依赖 MMPose 训练生态的输出格式。
- **下游 / 跨生态对接**:[ONNX 官方](https://onnx.ai/) —— 一旦导出为 ONNX,即可对接支持 ONNX 的各类推理引擎(`onnxruntime` 仅是本文档提到的官方验证后端)。
- **横向同类教程**:文档定位为 "Tutorial 5",即该 `docs/en/tutorials/` 系列教程中的第 5 篇,与其他教程(按序号推测可能涵盖数据流、配置、训练、测试等)同属 MMPose 用户文档序列。
- **质量反馈通道**:仓库 issue 系统 —— 当导出失败或精度受损时的反馈回路(原文: "Please fire an issue …")。

---

## 【使用方法】

**1) 安装依赖(原文)**

```shell
pip install onnx onnxruntime
```

**2) 导出命令模板(原文)**

```shell
python tools/deployment/pytorch2onnx.py ${CONFIG_FILE} ${CHECKPOINT_FILE} [--shape ${SHAPE}] \
    [--verify] [--show] [--output-file ${OUTPUT_FILE}] [--opset-version ${VERSION}]
```

**3) 可选参数默认值一览(原文)**

| 参数 | 作用 | 未指定时的默认值 |
|---|---|---|
| `--shape` | 输入张量形状 | `1 3 256 192` |
| `--verify` | 是否验证导出模型(可运行 + 数值一致) | `False` |
| `--show` | 是否打印导出模型结构 | `False` |
| `--output-file` | 输出 ONNX 文件名 | `tmp.onnx` |
| `--opset-version` | ONNX Opset 版本,推荐 ≥ 11 | `11` |

**4) 异常/边界处理(原文)**

- 导出若出现精度损失或转换异常,**未提供内置修复**,原文要求通过 issue 反馈。

(以上命令、参数、默认值均直接出自原文,未做补充。)
