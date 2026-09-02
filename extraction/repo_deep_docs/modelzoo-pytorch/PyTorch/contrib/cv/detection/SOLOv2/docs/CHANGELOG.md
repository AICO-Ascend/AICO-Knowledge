# CHANGELOG

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SOLOv2/docs/CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SOLOv2/docs/CHANGELOG.md

# SOLOv2 文档之 CHANGELOG.md 深度解读

---

## 【定位】

**一句话定位**：本文档是 mmdetection 目标检测框架（SOLOv2 算法所依赖的底层平台）的版本演进日志，记录从 2018-10 至 2020-01 期间 10 余个版本中新增算法模型、缺陷修复、性能改进与工程设施完善情况，为 SOLOv2 复现所需的依赖框架（mmdetection v1.0.0 系列）的能力边界与历史脉络提供依据。

---

## 【技术要点】

核心机制分条（按版本演进顺序，保留原文关键数字/参数/命令）：

1. **DCN（可变形卷积）接口统一**（v1.0.0）：通过 `build_conv_layer` 与 `ConvModule` 两条 API 实现可变形卷积的常规调用，关键 PR #1894 将 DCN 封装入 `ConvModule` 与 `Conv_layers`，使 DCN 在 ResNe(X)t 中的使用与普通卷积无异。
2. **多尺度 mAP 回归缺陷**（v1.0rc1 破坏性变更）：Issue #1679 修复了 #621 引入的 COCO 风格 mAP 在 AP_s / AP_m / AP_l 多尺度统计中的计算错误。
3. **ATSS 算法引入**（v1.0.0）：实现论文 "Bridging the Gap Between Anchor-based and Anchor-free Detection via Adaptive Training Sample Selection"（PR #1872，论文 arXiv:1912.02424）。
4. **三大检测新模型**（v1.0rc1）：FoveaBox（arXiv:1904.03797）、RepPoints（arXiv:1904.11490）、FreeAnchor（arXiv:1909.02466），同时 PR #1251 为 HTC 与 Cascade R-CNN 引入测试时增强（TTA）。
5. **推理性能提升**（v0.6.0）：相对前代 model zoo 实现高达 **30% 速度提升**，并将 NMS 与 SigmoidFocalLoss 替换为 PyTorch CUDA 扩展。
6. **里程碑式功能矩阵**（v1.0rc0）：一次性集成混合精度训练（Mixed Precision Training）、HTC、Libra R-CNN、Guided Anchoring、Empirical Attention、Mask Scoring R-CNN、Grid R-CNN（Plus）、GHM、GCNet、FCOS、HRNet、Weight Standardization 等算法，并新增 WIDER FACE 与 Cityscapes 两个数据集支持。

---

## 【关键机制与数据】

**【算法/模型引入机制】**

- **原文**：v1.0.0 新增 ATSS（PR #1872），并通过 PR #1995 强化 `AssignResult` 与 `SamplingResult`，PR #1982 为 Registry 增加覆盖已存在模块的能力。
- **作用机理**：Registry 模块允许动态注册与覆写模型组件，配合 `build_conv_layer` / `ConvModule` 的统一调用接口，把"算法即插即用"的能力落地到框架层，为后续 SOLOv2 等新算法接入预留入口。

**【数据增强与标注机制】**

- **原文**：v1.0.0 PR #1880 给 `RandomCrop` 增加分割图裁剪；PR #1975 支持加载灰度图为单通道；v1.0rc1 PR #1354 引入 Albumentations 数据增强库，PR #1273/#1115 支持水平与垂直翻转。
- **作用机理**：mask 与 bbox 在数据增强中需同步变换，分割图裁剪（PR #1880）以及 Expand/MinIoUCrop 处理 mask 与语义分割（v1.0rc1 PR #1550/#1361）确保 SOLOv2 这类实例分割算法在数据流上 mask 不发生越界或错位。

**【分布式训练与容错机制】**

- **原文**：v1.0.0 PR #1985 修复 Windows 等无 `distributed` 包环境下的兼容性问题；v1.0rc1 PR #1851 将 `init_dist()` 迁入 MMCV；PR #1399 支持无共享存储下的多节点分布式测试。
- **作用机理**：通过把分布式初始化统一下沉到 MMCV，框架层不再耦合具体的 torch.distributed 导入路径，从而在 Windows、单机多卡、多节点无 NFS 等场景下均能跑通 SOLOv2 训练。

**【推理与后处理机制】**

- **原文**：v1.0.0 新增两个测试时选项 `crop_mask` 与 `rle_mask_encode` 用于 mask head（PR #2013）；PR #1889 重构 mAP 评估并支持多进程与日志。
- **作用机理**：掩膜按 RLE 编码可显著压缩 mask 体积、加速 NMS 与 AP 计算，SOLOv2 在实例分割后处理中可直接复用该机制。

**【缺陷修复相关数据/版本号】**

- **原文**：与 numpy/pycocotools 最新版不兼容（#2024）；`refine_bboxes()` 维度问题（#1962）；`ga_shape_target_single()` 返回值修复（#1853）；DeformableConv 当 `deformable_group>1` 的 bug（#1359）；FCOS 在无正样本时崩溃（#1136）。
- **作用机理**：这些修复对 SOLOv2 复现尤为关键——其 backbone 中常使用 DCN，#1359/#1326 修复直接关系到前向正确性。

**【量化性能数据】**

- **原文**："v0.6.0 (14/04/2019) Up to **30%** speedup compared to the model zoo."
- **原文**："v0.5.6 (17/01/2019) Unify RPNHead and single stage heads (RetinaHead, SSDHead) with AnchorHead."

---

## 【表格解读】

**原文无表格**（全文为带版本号的层级化 Bullet List 与少量 PR 编号引用，未出现任何 markdown 表、CSV 或对齐数据表）。

---

## 【公式解读】

**原文无公式**（未出现任何 LaTeX 行内/行间数学表达式、伪代码或算法流程公式）。

---

## 【关联】

本文档位于 `PyTorch/contrib/cv/detection/SOLOv2/docs/CHANGELOG.md`，实际描述的是底层 **mmdetection** 框架（SOLOv2 的依赖）的变更，对 SOLOv2 的影响与上下游关联如下：

- **上游依赖**：
  - **PyTorch 版本**：v0.6rc0 起迁移到 PyTorch 1.0（#1131 把 CUDA 内核中 `long` 改为 `int64_t`、PR #1114 手动补齐类型提升以兼容 PyTorch 1.2、PR #1160 修复 RoIExtractor 中 inplace add 触发 PyTorch 1.2 错误），SOLOv2 复现时需锁定 PyTorch ≥ 1.2 且建议 1.x 稳定版。
  - **MMCV**：v1.0.0 PR #1851 把 `init_dist()` 下沉到 MMCV，表明 SOLOv2 在更高版本 mmdetection 中实际间接依赖 MMCV 提供的分布式能力。
  - **CUDA 扩展**：v0.6.0 起 NMS 与 SigmoidFocalLoss 由 PyTorch CUDA 扩展提供（替代原版实现），与 SOLOv2 中实例分割的 mask NMS 流程相关。

- **同模块内的相互引用**（按算法类别串联）：
  - **两阶段/级联类**：v0.5.3 Cascade R-CNN + Cascade Mask R-CNN → v1.0.0 移除 `keep_all_stages` 选项（#1806）→ v1.0rc1 增加 TTA（#1251）→ v1.0.0 修复 HTC 内 `nms_cfg` 关键字参数错误（#1573）。
  - **单阶段/无锚框类**：v0.5.4 SingleStageDetector/RetinaNet → v0.5.6 锚框头统一到 AnchorHead → v1.0rc0 引入 FCOS → v1.0rc1 修复 FCOS 无正样本崩溃（#1136） → v1.0.0 引入 ATSS（#1872）→ SSD 的 CPU/GHM Loss 修复（#1578）。
  - **特征提取 backbone**：v0.5.5 引入 ResNeXt → v0.5.6 引入 GN（Group Normalization）→ v0.5.7 引入 DCN v2 → v1.0rc0 引入 HRNet（更新结果 #1284、#1182）与 Weight Standardization → v1.0.0 把 DCN 封装为 `ConvModule`（#1894）。
  - **注意力模块**：v1.0rc0 同时引入 Empirical Attention 与 GCNet。
  - **采样/分配**：v0.5.1 BBoxAssigner/BBoxSampler → v0.5.5 增加 OHEM → v1.0rc1 修复 Libra R-CNN 采样间隔 bug（#1800） → v1.0.0 强化 AssignResult/SamplingResult（#1995）。
  - **后处理/评估**：v0.5.3 支持 Soft-NMS → v1.0rc1 重构 mAP 与多进程评估（#1889）→ v1.0.0 修复多尺度 AP 计算（#1679）。
  - **数据集/增强**：v0.5.2 自定义数据集 + VOC 注释转换脚本 → v0.5.5 新增 VOC 数据集与评估脚本 → v1.0rc0 新增 WIDER FACE 与 Cityscapes → v1.0rc1 增加 Albumentations 支持（#1354） → v1.0.0 PR #1880 把分割图裁剪加入 RandomCrop。
  - **工程与文档**：v1.0rc1 增加 Dockerfile（#1168）、webcam demo（#1155/#1150）、jupyter notebook demo（#1158）、CI 代码风格与单元测试；v1.0.0 上线 mmdetection.readthedocs.io 文档站、增加 sphinx 文档（#1859、#1864）、增加 FLOPs 计数器（v1.0rc1 #1127、v1.0.0 #1850 支持 GN 下的 FLOPs）。

- **下游影响（对 SOLOv2 的具体赋能）**：
  - SOLOv2 属于"按位置分割"类单阶段实例分割算法，其 backbone 可受益于 ResNeXt（v0.5.5）+ DCN（v0.5.7/v1.0.0 封装）+ Weight Standardization（v1.0rc0）。
  - 实例分割结果后处理依赖 mask crop 与 RLE 编码（v1.0.0 PR #2013）。
  - 数据流可叠加 Albumentations 增强（v1.0rc1 #1354）与 RandomCrop 中 mask 同步（v1.0.0 #1880）。
  - 评估对齐 mAP 多进程计算（v1.0rc1 #1889）。

- **社区/贡献者**：文档内 @Erotemic 提交了批量 docstring/单元测试（v1.0rc1 #1603/#1517/#1506/#1505/#1491/#1479/#1477/#1475/#1474），@chengdazhi 参与 DCN v2 集成（v0.5.7）。

---

## 【使用方法】

**原文未涉及** SOLOv2 的具体启用命令、超参数配置或启动脚本；本文档为 changelog 性质，仅记录 mmdetection 框架自身的变更条目，未给出：
- 训练启动命令（如 `tools/train.py` 的调用方式）
- 配置文件路径或字段
- 推理脚本调用方式
- 权重下载链接

如需在 SOLOv2 复现中启用上述变更（例如 DCN v2 backbone、Albumentations 数据增强、FLOPs 计数、mask 测试时 RLE 编码、混合精度训练等），需结合 mmdetection 官方配置文档与 SOLOv2 自身 README（不在本 changelog 中）进行配置组合。
