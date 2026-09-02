# CHANGELOG

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SOLOv1/docs/CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SOLOv1/docs/CHANGELOG.md

# 深度解读：mmdetection Changelog（路径 SOLOv1/docs/CHANGELOG.md）

> 说明：原文内容是 mmdetection 项目的整体 changelog，并非 SOLOv1 专属。下面严格基于原文做一体化解读。

---

## 【定位】

本篇文档是 **mmdetection 目标检测框架从 v0.5.1 (2018-10) 至 v1.0.0 (2020-01) 的完整版本演进记录**，系统罗列每个版本新增的模型/特性、关键 bug 修复、改进点与破坏性变更，为开发者追踪框架能力边界与升级影响提供时间线参考。

---

## 【技术要点】

1. **模型库持续扩张**：依次新增 ATSS、FoveaBox、RepPoints、FreeAnchor、HTC、Libra R-CNN、Guided Anchoring、Mask Scoring R-CNN、Grid R-CNN (Plus)、GHM、GCNet、FCOS、HRNet、SSD、RetinaNet、Cascade R-CNN、Deformable ConvNet v2 等检测模型与组件。
2. **可变形卷积（DCN）标准化接入**：v1.0.0 起 DCN 通过 `build_conv_layer` 与 `ConvModule` API 像普通卷积一样调用；v1.0rc1 中进一步封装为 ConvModule & Conv_layers（PR #1894），并修复 deformable_group>1 与非 cuda:0 设备下零输出等 bug。
3. **PyTorch 版本迁移链**：v0.5.7 为 PyTorch 0.4.1 末版 → v0.6rc0 迁移至 PyTorch 1.0 → v1.0rc1 兼容 PyTorch 1.2（含 int64_t 替代 long、`scalar_type()` 替代 `type()`、手动类型提升等兼容性补丁）。
4. **性能与精度工具链**：v0.6.0 相比 model zoo **提升最高 30% 速度**，并将 NMS / SigmoidFocalLoss 替换为 Pytorch CUDA 扩展；v1.0rc1 增加 FLOPs counter（PR #1127）与 `--with_ap` 选项（PR #1549），支持每类 AP 输出。
5. **数据增强与多数据集**：支持 WIDER FACE、Cityscapes、Albumentations 数据增强、灰度图像单通道加载、test-time augmentation、水平/垂直翻转、Expand/MinIoUCrop 概率参数。
6. **分布式训练与 CI 工程化**：支持多节点无共享存储测试（PR #1399）、分布式下不可用包回退（Windows 兼容，PR #1985）、Sphinx 文档站点（mmdetection.readthedocs.io）、pre-commit hook、travis CI 代码 lint、Dockerfile 瘦身。

---

## 【关键机制与数据】

- **速度提升（原文）**："Up to 30% speedup compared to the model zoo."（v0.6.0）
- **NMS / SigmoidFocalLoss 加速（原文）**："Replace NMS and SigmoidFocalLoss with Pytorch CUDA extensions."（v0.6.0）
- **mAP 多尺度统计回归（原文）**："There was a bug for computing COCO-style mAP w.r.t different scales (AP_s, AP_m, AP_l), introduced by #621."（v1.0rc1 Breaking Changes, #1679）
- **DCN API 形态（原文）**："DCN is now available with the api `build_conv_layer` and `ConvModule` like the normal conv layer."（v1.0.0）
- **Mask 测试时选项（原文）**："Add two test-time options `crop_mask` and `rle_mask_encode` for mask heads."（v1.0.0, #2013）
- **v1.0rc1 新增模型引用**：FoveaBox（arxiv 1904.03797）、RepPoints（arxiv 1904.11490）、FreeAnchor（arxiv 1909.02466）；v1.0.0 新增 ATSS（arxiv 1912.02424）。
- **PyTorch 1.2 inplace 兼容（原文）**："Fix inplace add in RoIExtractor which cause an error in PyTorch 1.2."（v1.0rc1, #1160）
- **Headless 数据流**：v1.0rc1 起 COCO mAP 计算支持 multiprocessing 与 logging（PR #1889）；可在 config 中通过 `img_prefix=None` 与 `gt_bboxes_ignore=None` 的容错路径处理空数据。
- **HTC/Cascade R-CNN 简化（原文）**："Remove the option `keep_all_stages` in HTC and Cascade R-CNN."（v1.0.0, #1806）

---

## 【表格解读】

**原文无表格**。Changelog 以列表（Highlights / Bug Fixes / Improvements / New Features / Breaking Changes）+ PR 编号（#xxxx）形式组织版本信息，未出现任何参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式**。全文均为版本发布条目，不含数学公式或伪代码片段。

---

## 【关联】

原文本身在文末标注「(无)内部链接」，但从语义上可梳理如下模块/特性关联网络：

- **ATSS**（v1.0.0）↔ 框架内的 **AnchorHead / AssignResult**（v1.0rc1 PR #1995 增强）↔ **FCOS**（v1.0rc0）三者均为 anchor-free / adaptive sample 范式，ATSS 论文题目"Bridging the Gap Between Anchor-based and Anchor-free Detection"（PR #1872）即对应此关联。
- **DCN**（v0.5.7 → v1.0.0）↔ `build_conv_layer` / `ConvModule`（v1.0rc1 PR #1078 支持任意层顺序）↔ ResNe(X)t backbone（v0.5.5）。
- **HTC / Cascade R-CNN**（v1.0rc0 起，v1.0rc1 PR #1251 添加 TTA，v1.0.0 PR #1806 移除 `keep_all_stages`）共享 mask head 与 bbox head 抽象；其 mask head 复用了 v1.0.0 引入的 `crop_mask` / `rle_mask_encode`（#2013）。
- **Mixed Precision Training、GHM、GCNet、Mask Scoring R-CNN、Grid R-CNN (Plus)、Guided Anchoring、Libra R-CNN、Weight Standardization**（v1.0rc0）均挂载在统一 Refactoring 后的 loss API 与 Samplers/Assigners（v0.5.5 起，OHEM 同源）。
- **Sphinx 文档（PR #1859、#1864）** + **environment info collector（PR #1812）** 共同支撑 v1.0.0 上线的 mmdetection.readthedocs.io 站点。
- **HRNet**（v1.0rc0 起，PR #1284、#1182 更新结果）作为 backbone 与 FPN（PR #1240 新增 `no_norm_on_lateral`）配合。
- **数据集生态**：WIDER FACE（v1.0rc1 PR #1781 SSD300）、Cityscapes（v1.0rc0）、PASCAL VOC（v0.5.5）、COCO（贯穿全版本，含 PR #1376 仅两类时的 eval 修复）。
- **Albumentations**（v1.0rc1 PR #1354，可选依赖，v1.0.0 PR #1969）与 **imagecorruptions**（v1.0.0 PR #1969 改为可选）构成数据增强可选链。

---

## 【使用方法】

原文未涉及具体的启用命令、配置文件路径或运行指令，仅记录变更条目。如需获取使用方法，应参考同目录下其他文档（如 SOLOv1 的 README 或 mmdetection 官方文档站点 https://mmdetection.readthedocs.io，v1.0.0 上线）。具体到本 changelog 中可被操作者感知的开关/选项如下：

- **命令行**：`--with_ap`（v1.0rc1 PR #1549，输出每类 AP）；`--validate` 在非分布式训练下触发 warning（v1.0rc1 PR #1624）。
- **测试时 mask 选项**：`crop_mask`、`rle_mask_encode`（v1.0.0 #2013）。
- **Backbone 参数**：`in_channels`（v1.0rc1 PR #1475）。
- **FPN 参数**：`no_norm_on_lateral`（v1.0rc1 PR #1240）。
- **构建配置依赖**：albumentations、imagecorruptions 自 v1.0.0 起为可选依赖（PR #1969）。
