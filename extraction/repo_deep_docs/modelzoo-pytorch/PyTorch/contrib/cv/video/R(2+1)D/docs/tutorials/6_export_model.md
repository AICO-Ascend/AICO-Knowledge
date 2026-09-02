# Tutorial 6: Exporting a model to ONNX

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/6_export_model.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/6_export_model.md

# 一体化深度解读:Tutorial 6 — Exporting a model to ONNX

---

## 【定位】

本文档解决 **如何将 MMAction2 训练好的 PyTorch 视频理解模型(包括识别器 Recognizer 与时序定位器 Localizer)导出为 ONNX 格式以便跨框架部署** 的问题,提供了支持模型清单、依赖环境、一键导出脚本调用方式及所有可选参数的语义与默认值。

---

## 【技术要点】

1. **支持模型清单(9 类)**:识别器侧涵盖 I3D、TSN、TIN、TSM、R(2+1)D、SLOWFAST、SLOWONLY;定位器侧涵盖 BMN、BSN(含 tem 与 pem 两个子模块)。
2. **导出入口脚本**:`tools/deployment/pytorch2onnx.py`,接受 `${CONFIG_FILE}` 与 `${CHECKPOINT_FILE}` 两个位置参数,以及若干可选 flag。
3. **依赖安装**:`pip install onnx onnxruntime` —— ONNX 用于序列化模型,ONNX Runtime 用于导出后的可运行性与数值校验。
4. **输入张量 shape 分两类**:
   - 2D 识别器(以 TSN 为例):`$batch $clip $channel $height $width`,示例 `1 1 3 224 224`;
   - 3D 识别器(以 I3D 为例):`$batch $clip $channel $time $height $width`,示例 `1 1 3 32 224 224`;
   - 定位器(如 BSN)各模块 input 不同,需自行查阅 `forward` 函数。
5. **核心可选参数与默认值**:`--shape` 默认 `1 1 3 224 224`;`--verify` 默认 `False`;`--show` 默认 `False`;`--output-file` 默认 `tmp.onnx`;`--is-localizer` 默认 `False`;`--opset-version` 默认 `11`(建议用更高版本以保兼容性);`--softmax` 默认 `False`(仅识别器生效,定位器尚不支持)。
6. **两类调用模板**:识别器走标准命令并加 `--verify`;定位器需额外加 `--is-localizer` flag,以切换脚本内部的模型构建分支。

---

## 【关键机制与数据】

工作原理如下:

1. **位置参数加载模型**:`pytorch2onnx.py` 接收 `${CONFIG_FILE}`(MMAction2 配置)与 `${CHECKPOINT_FILE}`(训练权重),依据配置重建 PyTorch 模型并加载权重。
2. **`--shape` 控制 dummy input**:脚本据此构造符合识别器 / 定位器规范的 dummy tensor,作为 `torch.onnx.export` 的示例输入驱动 tracing,得到计算图。
3. **`--opset-version` 控制 ONNX 算子集版本**:默认 `11`,数值越大支持的算子越新,跨运行时兼容性通常更好。
4. **`--softmax` 在 recognizer 末端追加 Softmax**:使输出即概率分布,便于部署时直接使用;定位器目前不开放此选项。
5. **`--verify` 触发双校验**:导出后用 ONNX Runtime 加载生成的 `.onnx` 文件,与原始 PyTorch 模型在同一输入上做 forward,核对运行性与数值一致性。
6. **`--show` 打印导出模型结构**:便于调试模型图与算子映射。
7. **`--output-file` 指定产物文件名**:默认 `tmp.onnx`。
8. **`--is-localizer` 切换构建分支**:告知脚本当前导出对象是时序定位器(BMN / BSN),其内部网络结构与 forward 调用方式与识别器不同。

性能 / 精度数据:原文未给出导出后推理时延、吞吐或精度损失数值,仅以 "fire an issue if you discover any checkpoints that are not perfectly exported or suffer some loss in accuracy" 暗示存在导出异常需上报。

---

## 【表格解读】

原文无表格。

(原文所有结构化信息均以 Markdown 列表与命令块形式给出,未提供参数表、性能对比表或配置项表。)

---

## 【公式解读】

原文无公式。

(文档为工程使用指南,未出现任何数学公式或伪代码块,所有"形状 / 参数 / 默认值"信息均以自然语言或命令行参数形式呈现。)

---

## 【关联】

1. **与导出脚本 `tools/deployment/pytorch2onnx.py` 的关系**(原文内链:`/tools/deployment/pytorch2onnx.py`):本文档是该脚本的"用户面"说明,所有命令行示例均直接调用此脚本,文档未展开脚本内部实现细节(如 `decode_heads` 的构造、动态 shape 处理、`do_constant_folding` 等 `torch.onnx.export` 参数),这些需查阅脚本源码。
2. **与 MMAction2 训练流程的关系**:本文档承接已完成训练、产出 `${CONFIG_FILE}` + `${CHECKPOINT_FILE}` 的前置流程,是模型从训练态走向部署态的桥梁。
3. **与下游 ONNX Runtime / 推理引擎的关系**:导出后的 `.onnx` 文件依赖 ONNX Runtime(`onnxruntime` 包)做可运行性与数值校验,亦可被其他支持 ONNX 的推理后端(TensorRT、OpenVINO 等)消费。
4. **与同类教程(Tutorial 1–5)的关系**:作为 Tutorial 6,处于部署链路的导出环节,与上文未在本文档出现的量化 / 推理服务化 / 精度对齐等教程存在上下游衔接关系(本文档未提供这些链接)。
5. **与外部 ONNX 生态的关系**:文档开头给出 ONNX 官方链接 `https://onnx.ai/`,声明其"open ecosystem that empowers AI developers to choose the right tools" 的定位,表明本文档产出物遵循该开放标准。

---

## 【使用方法】

### 1. 环境准备

```shell
pip install onnx onnxruntime
```

### 2. 通用命令模板

```shell
python tools/deployment/pytorch2onnx.py ${CONFIG_FILE} ${CHECKPOINT_FILE} [--shape ${SHAPE}] \
    [--verify] [--show] [--output-file ${OUTPUT_FILE}]  [--is-localizer] [--opset-version ${VERSION}]
```

### 3. 识别器导出(示例)

```shell
python tools/deployment/pytorch2onnx.py $CONFIG_PATH $CHECKPOINT_PATH --shape $SHAPE --verify
```

### 4. 定位器导出(示例)

```shell
python tools/deployment/pytorch2onnx.py $CONFIG_PATH $CHECKPOINT_PATH --is-localizer --shape $SHAPE --verify
```

### 5. 关键配置项

| 参数 | 作用 | 默认值 |
|---|---|---|
| `--shape` | dummy input 形状 | `1 1 3 224 224` |
| `--verify` | 是否做可运行性 + 数值校验 | `False` |
| `--show` | 是否打印导出模型结构 | `False` |
| `--output-file` | 输出 `.onnx` 文件名 | `tmp.onnx` |
| `--is-localizer` | 是否为定位器分支 | `False` |
| `--opset-version` | ONNX 算子集版本(建议 ≥11) | `11` |
| `--softmax` | 识别器末端是否追加 Softmax(定位器不支持) | `False` |

(上表为根据原文逐条整理,便于查阅;**原文本身未以表格形式呈现**,此处为读者友好化重排,内容严格来自原文。)
