# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/GFocalV2/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/GFocalV2/docs/changelog.md

# 一体化深度解读：GFocalV2/docs/changelog.md

---

## 【定位】

本文档并非 GFocalV2 算法本身的技术说明，而是 **MMDetection v2.3.0 → v2.6.0 的官方发布历史（Changelog）**，记录该检测框架在 2020-08 至 2020-11 期间四个版本的 **新算法引入、向后不兼容变更、缺陷修复与文档/工程改进**。其中 v2.6.0 引入的 VarifocalNet 与仓库中 "GFocalV2" 路径存在直接算法渊源（VarifocalNet 即 GFocal 的前作），可视为该模型进入 modelzoo 的版本依据。

---

## 【技术要点】

1. **新增 VarifocalNet 检测方法（v2.6.0）**：对应论文 arXiv:2008.13367，PR #3666 与 #4024；这是 GFocalV2 系列的核心前置工作。
2. **BboxOverlaps2D 支持 GIoU 计算**（v2.6.0，#3936）：在 overlap 接口中新增 GIoU 选项，并使用 `bbox_overlaps` 重写 `giou_loss`。
3. **后台标签语义统一**（v2.5.0，#3221）：全模型统一为 `[0, N-1]` 表示前景类别，`N` 表示背景；删除 `dense_heads` 中的 `self.background_labels`，改用 `self.num_classes` 指代背景索引。
4. **FP16 工具迁移**（v2.5.0，#3766/#3822）：`force_fp32`、`auto_fp16`、`wrap_fp16_model`、`Fp16OptimizerHook` 从 `mmdet.core.fp16` 迁移至 `mmcv.runner`，v2.8.0 前保留 deprecation warning。
5. **`get_subset_by_classes` 触发条件收紧**（v2.5.0，#3695）：仅当 `test_mode=True` 且 `filter_empty_gt=True` 时才生效，避免训练阶段被隐式过滤。
6. **Batch Inference 能力上线**（v2.4.0，#3564/#3686/#3705）：单 GPU 可一次推理多张图片，并引入 `replace_ImageToTensor`（#3686）兼容旧数据流水线。
7. **数据增强扩展**：新增 `Shear/Rotate/Translate`（#3656/#3619/#3687）、`Contrast/Equalize/Color/Brightness` 图像级变换（#3643）、`RandomFlip` 支持水平/垂直/对角方向（v2.4.0，#3608）、Cutout（v2.4.0，#3521）。
8. **新增检测方法**：YOLACT（arXiv:1904.02689，#3456）、CentripetalNet（arXiv:2003.09119，#3390）、SABL（arXiv:1912.04260，#3603）、YOLOv3（arXiv:1804.02767，#3083）、PAA Assign（arXiv:2007.08103，#3547）、CornerNet（arXiv:1808.01244）。
9. **新增损失/算子**：DIoU（arXiv:1911.08287）/CIoU（arXiv:2005.03572）Loss（v2.3.0）。
10. **新增数据集**：LVIS V1（arXiv:1908.03195，v2.3.0），通过 `mmlvis`+`mmpycocotools`（v2.4.0，#3727）替换原 `lvis`/`pycocotools`。
11. **模型权重托管域名切换**：从 GitHub release 切换至 `download.openmmlab.com`（v2.4.0 起，#3665/#3840 等）。
12. **包发布通道**：自 v2.3.0 起，`mmdet` 通过 GitHub Action（#3510）发布到 PyPI。

---

## 【关键机制与数据】

### 工作原理 / 数据流相关（仅原文明确说明者）

- **GIoU 路径**（原文 v2.6.0，#3936）：`BboxOverlaps2D` 增加 GIoU 选项 → `giou_loss` 改用 `bbox_overlaps` 计算 → 可在配置层按 IoU 类型调用统一接口。
- **背景标签一致化**（原文 v2.5.0，#3221）：RPN 与其他 head 共享 `num_classes` 作为背景索引。原文明确：*"This change has no effect on the pre-trained models in the v2.x model zoo, but will affect the training of all models with RPN heads. Two-stage detectors whose RPN head uses softmax will be affected because the order of categories is changed."*
- **`get_subset_by_classes` 触发矩阵**（原文 v2.5.0，#3695）：
  - `filter_empty_gt=False` → 不论是否指定 classes，使用全部图片；
  - `filter_empty_gt=True` 且 `test_mode=True` → 调用 `get_subset_by_classes` 过滤无 GT 图片；
  - `filter_empty_gt=True` 且 `test_mode=False` → 不再隐式过滤，由用户自行负责测试集清洗。
- **Batch Inference 兼容链路**（原文 v2.4.0，#3564/#3686/#3705）：通过 `replace_ImageToTensor` 在 dataset 初始化阶段将旧 test pipeline 转换为新格式，影响所有测试 API 及下游代码库。
- **数据增强联动**（原文 v2.4.0，#3608）：`RandomFlip` 增加 vertical/diagonal 方向后，bounding box、mask、image 变换以及回映射逻辑同步更新。
- **PAA / ATSS 训练健壮性**（原文）：v2.5.0 #3702 修复"无 GT 框时 ATSS/Focal Loss 训练崩溃"；v2.6.0 #3938 修复 `num_pos=0` 时 PAA head 的除零问题；v2.5.0 #3713 修复 Mask R-CNN 在无 positive RoI 时的卡死。
- **测试稳健性**（原文 v2.6.0 #4000）：更新 test robustness；v2.5.0 #3966 支持 validation 中 `batch_size > 1`；v2.6.0 #3930 在 CPU 推理时改用 MMCV 实现的 RoIAlign。

### 性能/版本元数据

- 文档覆盖版本与日期：v2.6.0 = 1/11/2020；v2.5.0 = 5/10/2020；v2.4.0 = 5/9/2020；v2.3.0 = 5/8/2020（原文明确给出）。
- 兼容性终点：FP16 旧导入路径将在 v2.8.0 完全移除（原文 v2.5.0，#3766/#3822）。
- PR 编号均为原文罗列，未做改写。

---

## 【表格解读】

**原文无表格**。该 changelog 采用纯列表（条目 + PR 编号 + 简要说明）组织，无任何 markdown 表格或对比矩阵。

---

## 【公式解读】

**原文无公式**。该 changelog 仅描述功能开关与 PR 改动，不含数学表达式、LaTeX 或伪代码推导。

---

## 【关联】

> 用户提示中存在三条内部链接：`model_zoo.md#comparison-with-detectron2`、`compatibility.md#training-hyperparameters`、`compatibility.md`。**这三条链接在当前提供的 changelog 全文中均未实际出现**（changelog 仅通过 PR/Issue 编号和论文 arXiv 链接引用外部资源），因此无法基于原文展开上下游锚点描述。

可基于 changelog 内容推断的关联线索（仅原文支撑部分）：

- **GFocalV2 ↔ VarifocalNet**：v2.6.0 引入 VarifocalNet（arXiv:2008.13367），是 GFocalV2（Generalized Focal Loss V2）所基于的 Varifocal Loss/Net 路线，因此本 changelog 是该仓库存在的版本前提。
- **GIoU / DIoU / CIoU 链路**：v2.6.0 扩展 GIoU；v2.3.0 已支持 DIoU/CIoU Loss，三者在 `bbox_overlaps`/`BboxOverlaps2D` 体系中前后衔接。
- **MMCV 依赖演进**：v2.5.0 将 FP16 工具迁入 `mmcv.runner`（`mmcv.runner`），v2.5.0 起改用 `mmcv.utils.collect_env` 收集环境信息（#3779），Docker 中支持 PyTorch 1.6（#3905）；说明 mmdet 与 mmcv 的耦合关系在持续调整。
- **模型权重分发**：自 v2.4.0 切换到 `download.openmmlab.com`，与 `model_zoo.md` 文档应配套更新。

---

## 【使用方法】

该文档本身是发布历史记录，**不直接提供启用配置或命令**。可从原文提炼出的与"启用/使用"相关的关键项（均来自 changelog 条目本身）：

- **启用 GIoU**：通过 `BboxOverlaps2D` 配置并使用 `bbox_overlaps` 实现（原文 v2.6.0，#3936）；具体配置 key 原文未给出。
- **使用新模型**：将 detector 配置切换为 VarifocalNet / YOLACT / CentripetalNet / SABL / YOLOv3 / PAA / CornerNet（PR 编号见【技术要点】），并从 `download.openmmlab.com` 下载对应权重（v2.4.0 起切换域名）。
- **Batch Inference**：自 v2.4.0 起可直接在单 GPU 多图推理，旧 test pipeline 由 `replace_ImageToTensor` 自动转换（#3686）。
- **FP16 迁移**：自 v2.5.0 起 `force_fp32 / auto_fp16 / wrap_fp16_model / Fp16OptimizerHook` 应从 `mmcv.runner` 导入，旧路径产生 deprecation warning 并将于 v2.8.0 移除。
- **PyPI 安装：原文未涉及**具体安装命令，仅说明"v2.3.0 起开始发布到 PyPI（#3510）"。
- **训练超参与 Detectron2 对比、训练超参兼容细节：原文未涉及**——上述内容应查阅 `model_zoo.md#comparison-with-detectron2` 与 `compatibility.md#training-hyperparameters`，但这些页面在本 changelog 中未引用具体细节。
