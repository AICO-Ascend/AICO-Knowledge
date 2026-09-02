# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FCOS/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FCOS/docs/changelog.md

# 一体化深度解读:PyTorch/contrib/cv/detection/FCOS/docs/changelog.md

## 【定位】

本篇文档是 MMDetection 目标检测框架 **v2.3.0 → v2.6.0 四个版本(2020-05 至 2021-01)的版本变更日志(Changelog)**,系统记录每个版本的 **Highlights / 向后不兼容变更 / 新特性 / Bug Fixes / Improvements**,帮助用户理解版本演进、迁移注意事项与可用新能力。尽管物理路径位于 FCOS 文档目录下,内容实质为上游 mmdet 通用框架的 changelog(非 FCOS 模型专属)。

---

## 【技术要点】

1. **新算法支持**:v2.3.0–v2.6.0 依次引入 **CornerNet、DIoU/CIoU Loss、LVIS V1、SABL、YOLOv3、PAA Assign、YOLACT、CentripetalNet、VarifocalNet** 九项新方法,均带 arXiv 链接可追溯。
2. **架构迁移**:v2.3.0 起 **CUDA/C++ 算子从 `mmdet.ops` 迁出至 `mmcv.ops`**(`mmdet.ops` 保留为薄包装以兼容);v2.5.0 起 **FP16 相关工具(`force_fp32`、`auto_fp16`、`wrap_fp16_model`、`Fp16OptimizerHook`)从 `mmdet.core.fp16` 迁移至 `mmcv.runner`**,V2.8.0 将彻底移除旧导入路径。
3. **标签语义统一(关键 Breaking Change)**:v2.5.0 起 **RPN 与其他 head 一致采用 `[0, N-1]` 表示前景、`N` 表示背景**,删除 `dense_heads` 中的 `self.background_labels`,统一改用 `self.num_classes`;会影响使用 softmax RPN 的两阶段检测器类别顺序,但对 v2.x 已发布模型权重无影响。
4. **Batch Inference(重大能力)**:v2.4.0 起支持 **单 GPU 多图像批推理**,影响所有测试 API;通过 `replace_ImageToTensor`(#3686)在数据集初始化时转换遗留 test pipeline 辅助迁移。
5. **数据增强扩展**:v2.4.0 起支持 **RandomFlip 水平/垂直/对角方向**;v2.2.4.0 起增加 **Cutout 增强**;v2.5.0 新增 `Shear`、`Rotate`、`Translate` 几何增强和 `Constrast`、`Equalize`、`Color`、`Brightness` 图像增强。
6. **数据集与依赖**:v2.4.0 弃用原生 `lvis`/`pycocotools`,改用 **mmlvis + mmpycocotools**(API 完全兼容);v2.3.0 起通过 PyPI 发布 `mmdet` 包;v2.4.0 起模型权重托管切换至 `download.openmmlab.com`。
7. **性能优化**:v2.6.0 中 PAA head 训练加速(#3985);CPU 推理改用 MMCV 内置 `RoIAlign`(#3930);v2.5.0 起支持 **batch_size > 1 的验证**(#3966)。

---

## 【关键机制与数据】

- **GIoU 计算重构(v2.6.0)**:在 `BboxOverlaps2D` 中原生支持 GIoU 计算,并基于 `bbox_overlaps` 重写 `giou_loss`(PR #3936)。
- **CPU 模式 RoI 采样**:v2.6.0 在 CPU 模式下启用 RoIAlign(由 MMCV 提供,#3930),并支持 CPU 模式随机采样(#3948)。
- **数据集过滤语义(v2.5.0)**:重写 `get_subset_by_classes`(#3695),仅当 `test_mode=True` **且** `self.filter_empty_gt=True` 时调用;若 `filter_empty_gt=False` 则无论是否指定类别都使用全部图像——这改变了 v2.5.0 之前的行为。
- **PAA num_pos=0 防护**:v2.6.0 修复 PAA head 在 `num_pos=0` 时的除零问题(#3938);v2.5.0 修复 Focal Loss 在 `num_pos=0` 的同类 bug(#3702)。
- **多节点测试目录修复**:v2.6.0 修复多节点测试时的临时目录错误(#4034, #4017)。
- **ONNX 导出重构(v2.6.0)**:将 `pytorch2onnx` 重构进 `mmdet.core.export`,并使用 `generate_inputs_and_wrap_model`(#3857, #3912)。
- **环境信息采集**:v2.5.0 改用 `mmcv.utils.collect_env`(#3779)消除重复代码。
- **NMS 在 PyTorch 1.6.0 修复**:v2.5.0 修复 `nonzero` 在新版 PyTorch 的行为变化(#3867)。
- **Docker 与 CUDA 修复**:v2.5.0 修复 Dockerfile 中 ligGL.so.1 导致的 cv2 导入错误(#3891);v2.5.0 起支持 PyTorch 1.6 docker(#3905)。
- **OHEM 与 PAA 兼容性**:v2.4.0 修复 `OHEMSampler` bug(#3677)与 `fuse_conv_bn` import 问题(#3529, #3606)。
- **数据流说明**:原文为 changelog,**未提供端到端数据流图或性能 benchmark 数据(如 mAP/时延/吞吐)**;无定量性能数字。

---

## 【表格解读】

原文无表格。

(注:虽然本 changelog 中包含大量 PR 编号列表、版本号、日期,但均为平铺文本,未使用 markdown 表格形式。)

---

## 【公式解读】

原文无公式。

(注:changelog 中虽提及 DIoU/CIoU Loss、GIoU Loss、PAA Assign、SABL、YOLACT 等损失/方法,但**仅给出方法名与 arXiv 链接,未包含任何 LaTeX 公式或伪代码**,故按指示标注"原文无公式"。)

---

## 【关联】

- **与 model_zoo.md 的关联**:changelog 中多次提到 model zoo 变更(v2.4.0 起 **切换模型权重托管到 `download.openmmlab.com`**(#3665)、添加 **ATSS ResNet-101 模型**(#3639)、更新 RPN upgrade scripts 至 v2.5.0 兼容(#3986));这些变更直接对应 `model_zoo.md#comparison-with-detectron2` 章节中的模型对比与权重下载链接。
- **与 compatibility.md 的关联**:changelog 详细记录了 **向后不兼容变更(Backwards Incompatible Changes)**——背景标签语义统一(影响带 softmax RPN 的两阶段检测器)、FP16 工具迁移、Batch Inference 引入、RandomFlip 三方向扩展——这些均直接关联到 `compatibility.md#training-hyperparameters` 中关于训练超参数/标签编码约定的兼容性说明。
- **与 FCOS 的上下游关系**:本文档物理路径虽在 FCOS 文档下,但 **内容属于上游 mmdet 框架**;FCOS 作为 mmdet 支持的一阶段 anchor-free 检测器,**直接受益于** Batch Inference、CPU RoIAlign、GIoU/DIoU/CIoU Loss、`replace_ImageToTensor` 兼容层等基础能力,这些能力均体现在本文档列出的 PR 中(例如 #3966 batch_size>1 验证、#3564/#3686/#3705 Batch Inference、#3936 GIoU in `BboxOverlaps2D`)。
- **依赖模块迁移链**:`mmdet.ops` → `mmcv.ops`(算子)、`mmdet.core.fp16` → `mmcv.runner`(FP16 utils)、`lvis`/`pycocotools` → `mmlvis`/`mmpycocotools`(数据集),体现了 mmdet → mmcv 的依赖收敛趋势。

---

## 【使用方法】

原文未涉及具体启用方式/配置项/命令。

(说明:本 changelog 描述的是"做了什么",而非"怎么用"。每个新特性/方法虽配有 PR 编号与 arXiv 链接,但**未在本文档中给出对应的配置文件、命令行参数或 API 调用示例**。如需启用 VarifocalNet、YOLACT、CentripetalNet、SABL、YOLOv3、PAA、CornerNet 等方法,需查阅对应 `configs/` 目录下的 config 文件;启用 Batch Inference 需使用 v2.4.0+;启用 CPU RoIAlign 需使用 v2.6.0+ 且安装适配版 MMCV。)

---

**总结**:本 changelog 是一份 **"what changed" 性质的工程变更记录**,其价值在于:
1. 帮助用户判断升级风险(尤其是 v2.4.0 Batch Inference 与 v2.5.0 标签语义统一两项 Breaking Change);
2. 提供 PR/issue 编号作为深入溯源线索;
3. 与同仓库 `model_zoo.md` 和 `compatibility.md` 配套阅读,构成完整的迁移/兼容性知识三角。
