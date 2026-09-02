# 教程 6：如何导出模型为 onnx 格式

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/6_export_model.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/6_export_model.md

【定位】
本文档解决"MMAction2 训练得到的 PyTorch 模型如何导出为 ONNX 格式以便跨框架部署"的问题，描述了将 MMAction2 训练产物（涵盖行为识别器与时序动作检测器）转换为 ONNX 表示的能力，并给出统一的导出脚本与各模型类型的输入形状约定。

【技术要点】
- **生态基础**：ONNX（Open Neural Network Exchange）作为开放的神经网络交换格式，使 AI 开发者能随项目演进选择合适的推理工具；导出流程依赖 `onnx` 与 `onnxruntime` 两个 Python 包，前者负责序列化，后者负责导出后的运行/数值验证（"需要安装 `onnx` 和 `onnxruntime` 包以进行导出后的验证"）。
- **统一导出入口**：`tools/deployment/pytorch2onnx.py`（内部链接指向 `/tools/deployment/pytorch2onnx.py`），通过 `${CONFIG_FILE}` 与 `${CHECKPOINT_FILE}` 两个位置参数加载训练配置与权重，再由若干可选开关控制导出行为。
- **支持的模型范围**：行为识别类 `I3D / TSN / TIN / TSM / R(2+1)D / SLOWFAST / SLOWONLY`；时序动作检测类 `BMN / BSN(tem, pem)`。两类下游分别对应识别与定位（localizer）两种使用模式。
- **输入张量形状约定**：2D 模型（如 `TSN`）输入形状为 `$batch $clip $channel $height $width`，例 `1 1 3 224 224`；3D 模型（如 `I3D`）为 `$batch $clip $channel $time $height $width`，例 `1 1 3 32 224 224`；时序检测器（如 `BSN`）的各模块形状不一致，需查阅对应 `forward` 函数确定。
- **可选参数语义**：`--shape` 指定输入形状（未指定 → `1 1 3 224 224`）；`--verify` 决定是否进行可运行/数值正确性验证（默认 `False`）；`--show` 决定是否打印导出模型结构（默认 `False`）；`--output-file` 决定输出文件名（默认 `tmp.onnx`）；`--is-localizer` 决定是否按时序检测器导出（默认 `False`）；`--opset-version` 决定 ONNX opset 版本（默认 `11`，推荐使用如 `11` 的高版本以保证稳定性）；`--softmax` 决定是否在识别器尾部追加 Softmax（默认 `False`，仅支持行为识别器）。
- **错误反馈路径**：若权重文件无法成功导出或出现精度损失，原文指引用户在本 repo 提交 issue。

【关键机制与数据】
- **工作流（原文）**：① 安装依赖 `pip install onnx onnxruntime`；② 选择待导出模型所属类别（行为识别器或时序动作检测器）；③ 调用 `python tools/deployment/pytorch2onnx.py ${CONFIG_FILE} ${CHECKPOINT_FILE} [--shape ...] [--verify] [--show] [--output-file ...] [--is-localizer] [--opset-version ...]`；④（可选）通过 `--verify` 借助 `onnxruntime` 进行端到端运行与数值一致性核验；⑤（可选）通过 `--show` 打印 ONNX 图结构以辅助调试。
- **数据流（原文）**：PyTorch checkpoint → 按 config 构建识别器/检测器并切换至导出分支 → 按 `--shape` 组织输入张量 → 追踪得到 ONNX 计算图 → 以 `--output-file` 指定路径写出（默认 `tmp.onnx`）。识别器路径下还可经 `--softmax` 在网络末端追加 Softmax 节点；时序检测器路径则通过 `--is-localizer` 切换导出分支。
- **数值与默认参数（原文）**：默认 `shape = 1 1 3 224 224`；默认 `opset-version = 11`；默认 `output-file = tmp.onnx`；`verify / show / is-localizer / softmax` 缺省均为 `False`。
- **性能/精度数据**：原文未涉及具体数值指标或吞吐量数据。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
- **导出脚本锚点**：本文档与内部链接 `/tools/deployment/pytorch2onnx.py` 紧耦合——文档所述所有参数（`--shape / --verify / --show / --output-file / --is-localizer / --opset-version / --softmax`）与该脚本的行为一一对应，因此该脚本是本文档能力的实际承载体。
- **上游训练产物**：`${CONFIG_FILE}` 与 `${CHECKPOINT_FILE}` 表示上游 MMAction2 训练阶段产出的配置文件与权重，是导出流程的输入依赖。
- **下游模型家族**：本文档列出的 9 个模型（`I3D / TSN / TIN / TSM / R(2+1)D / SLOWFAST / SLOWONLY / BMN / BSN(tem, pem)`）分别对应仓库内不同的算法模块；其中 2D/3D 区分驱动 `--shape` 的五维/六维张量布局；`BSN(tem, pem)` 与 `BMN` 共同构成时序动作检测链路，并由 `--is-localizer` 触发对应的导出分支。
- **外部生态**：链接 `https://onnx.ai/` 表示 ONNX 作为本文档所导出模型的运行环境与互操作目标；`onnxruntime` 是文档指定的运行时验证工具。
- **当前路径上下文**：文档位于 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/6_export_model.md`，说明这是 R(2+1)D 算法子仓中关于导出模型的教程第 6 篇，但其描述范围覆盖整个 MMAction2 体系下的多模型导出能力，因此对上文列出的其他算法同样适用。

【使用方法】
- **环境准备（原文）**：`pip install onnx onnxruntime`。
- **通用命令模板（原文）**：
  ```
  python tools/deployment/pytorch2onnx.py ${CONFIG_FILE} ${CHECKPOINT_FILE} [--shape ${SHAPE}] \
      [--verify] [--show] [--output-file ${OUTPUT_FILE}] [--is-localizer] [--opset-version ${VERSION}]
  ```
- **行为识别器导出（原文）**：
  ```
  python tools/deployment/pytorch2onnx.py $CONFIG_PATH $CHECKPOINT_PATH --shape $SHAPE --verify
  ```
- **时序动作检测器导出（原文）**：
  ```
  python tools/deployment/pytorch2onnx.py $CONFIG_PATH $CHECKPOINT_PATH --is-localizer --shape $SHAPE --verify
  ```
- **关键配置项摘要**：2D 模型 shape 例 `1 1 3 224 224`；3D 模型 shape 例 `1 1 3 32 224 224`；opset 建议 ≥ 11；行为识别器可叠加 `--softmax`；仅行为识别器支持 `--softmax`；反馈通道为仓库 issue。
