# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/semantic_segmentation/BiseNetV1_for_PyTorch/docs/en/changelog.md

# BiseNetV1_for_PyTorch Changelog 文档深度解读

---

## 【定位】

本篇文档为 `mmsegmentation` 仓库（被 BiseNetV1_for_PyTorch 引用为上游依赖）的版本变更日志，覆盖 **V0.24.0 (2022/4/29) 至 V0.28.0 (2022/9/8)** 共 5 个版本的演进轨迹，旨在记录语义分割框架在 **新特性/模型/支持的后端、Bug 修复、文档改进、贡献者致谢** 四个维度的所有变更，便于使用者追踪能力边界与已知问题。

---

## 【技术要点】

按版本归纳的核心变更点（保留原文 PR 编号作为索引）：

1. **V0.28.0 (9/8/2022)** — 引入 **Tversky Loss** 损失函数（PR #1986，原文写为 `#1896` 但链接指向 `mmsegmentation/pull/1986`），并修复二值分割、配置文件、`confusion_matrix` 计算、`decode_head` 的 `forward_train` 错误。
2. **V0.27.0 (7/28/2022)** — 新增 **Swin-L Transformer** 模型（PR #1471），更新 **ERFNet** 结果（PR #1744），并修复 SegFormer checkpoint URL、colab tutorial。
3. **V0.26.0 (7/1/2022)** — **更新 ADE20K 上的 SegFormer 新模型**（PR #1705），新增 **专用 `MMSegWandbHook`**（PR #1603），**UPerNet r18** 结果新增（PR #1669）；`cls_token_weight` 保留维度以利于 **ONNX 部署**（PR #1642），支持 **padding 推理**（PR #1607）。
4. **V0.25.0 (6/2/2022)** — **MLU 后端支持 PyTorch**（PR #1515），修复 BCE loss 在 batch_size=1 时的错误（PR #1629），修复 `align_corners=True` 下的 `resize` 函数（PR #1592）。
5. **V0.24.0 (4/29/2022)** — **支持 MAE（Masked Autoencoders Are Scalable Vision Learners）**（PR #1307、#1523），**支持 ResNet strikes back**（PR #1390），**支持 config 中额外 dataloader 设置**（PR #1435），修复 `LayerDecayOptimizerConstructor`（PR #1539/#1540）。

---

## 【关键机制与数据】

> **原文:** 本 changelog 以"事件清单 + PR 链接"形式组织，**未提供**任何性能/精度数值、训练曲线、超参表、推理时延数据，也未给出数据流示意。所列机制均以行为描述而非工程指标呈现，仅可作为变更事实的索引。

可从原文直接还原的工作机制描述：

- **Loss 扩展机制（V0.28.0）**：将 Tversky Loss 作为新的损失选项加入损失函数体系，用于解决类别不平衡场景（原文未给出 α/β 权重等具体参数）。
- **数据可视化机制（V0.26.0）**：通过 `MMSegWandbHook` 将 MMSegmentation 训练过程的指标上传至 Weights & Biases 平台（原文未给出默认上传的指标清单）。
- **推理部署机制（V0.26.0）**：
  - `cls_token_weight` 维度保留，使 SegFormer 类模型可通过 `keep_dim=True` 导出 ONNX；
  - 推理阶段支持对输入进行 padding，便于任意尺寸输入。
- **多后端机制（V0.25.0）**：PyTorch 训练流水线在 **MLU（Cambricon 寒武纪）** 设备上得到支持，使 MMSegmentation 不仅能在 GPU/NPU 上运行，也能在 MLU 上运行。
- **自监督预训练机制（V0.24.0）**：MAE（He et al.）被加入作为骨干网络/预训练选项，可通过 `LayerDecayOptimizerConstructor` 为 MAE 微调定制分层学习率衰减。
- **二值/多类分割机制（V0.28.0 / V0.24.0）**：修复 `binary_cross_entropy` 在 `batch_size=1` 时的行为，并支持 BCE Loss 的单通道预测（PR #1454）；修复了评估时 `label_map` 对 label id 的二次转换问题（PR #1417）。

---

## 【表格解读】

**原文无表格**。

原文仅以分类列表（Highlights / New Features / Enhancement / Bug Fixes / Documentation / Contributors）+ Markdown 项目符号呈现变更条目，未包含任何参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式**。

原文作为版本变更说明，不含任何损失函数定义、IoU 计算式或训练目标等 LaTeX/伪代码公式。涉及到的 Tversky Loss、BCE Loss 等均为名称引用，未给出数学形式。

---

## 【关联】

文档本身标注「(无) 内部链接」，但从原文可读出的关联关系如下：

- **上下游关系**：
  - `BiseNetV1_for_PyTorch` 文档目录下引用本 changelog，表明其 **功能/配置/API 演进** 与上游 `mmsegmentation` 严格同步；
  - 涉及的依赖性能力（如 `MMSegWandbHook`、`SegFormer`、`Swin-L`、`MAE`、`ResNet strikes back`、`UPerNet r18`、`ERFNet`、`Tversky Loss`）均通过 `mmsegmentation` 的 registry/config 体系被 BiseNetV1 的配置文件间接调用。
- **跨版本关联**：
  - V0.28.0 中修复的 `decode_head forward_train` 错误涉及 cascade/多阶段解码头逻辑，与 V0.24.0 中"修复 last `cascade_decode_head` 接收前序结果"（PR #1450）形成连贯修复链；
  - V0.25.0 修复的 BCE loss `batch_size=1` 错误（PR #1629）与 V0.24.0 新增"BCE Loss 单通道预测支持"（PR #1454）构成 BCE 相关问题的两次迭代；
  - V0.26.0 引入 `MMSegWandbHook`（PR #1603）与 V0.25.0 的文档重构（包括 myst-parser 与 mdformat 替换）共同提升可观测性与文档可维护性；
  - V0.24.0 引入的 MAE 支持与 V0.24.1 紧接修复 `LayerDecayOptimizerConstructor` 表明 MAE 在 V0.24 系列中作为重点新特性落地。
- **贡献者关联**：V0.25.0 ~ V0.28.0 共记录 **15+ 位首次贡献者**（@suchot、@TimoK93、@DataSttructure、@AkideLiu、@mawanda-jun、@Yan-Daojiang、@RunningLeon、@zhouzaida、@tkhe、@rotorliu、@EvelynWang-0423、@ZhaoYi1222、@Sanster、@ayulockin、@atinfinity、@DoubleChuang、@alpha-baymax、@274869388），覆盖 loss、可视化 hook、文档、推理路径、后端适配等多个方向。

---

## 【使用方法】

**原文未涉及**。Changelog 文档本身仅记录变更事实，不包含：

- 启用 Tversky Loss 的 config 写法；
- `MMSegWandbHook` 的注册/调用方式；
- MLU 后端的安装/启动命令；
- ONNX 导出的具体步骤；
- MAE/ResNet strikes back 的 config 模板名；
- `padding` 推理的开关参数。

上述使用细节需查阅对应 PR 链接、config 模板或 `mmsegmentation` 官方文档以获取。
