# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/MMseg-swin/docs/en/changelog.md

# MMseg-swin Changelog 文档深度解读

## 【定位】

本篇 changelog 文档系统记录了 **OpenMMLab MMSegmentation 语义分割框架**在 V0.24.0 ~ V0.26.0 三个版本周期（约 2022 年 4 月底至 7 月初）内的功能新增、缺陷修复、改进点、文档更新与社区贡献情况，描述了该框架在此期间的演进能力与生态扩展。

---

## 【技术要点】

1. **新增 SegFormer 模型与 UPerNet-R18**
   - V0.26.0 在 ADE20K 数据集上更新 SegFormer 模型结果（PR [#1705](https://github.com/open-mmlab/mmsegmentation/pull/1705)）
   - V0.26.0 新增 UPerNet r18 结果（PR [#1669](https://github.com/open-mmlab/mmsegmentation/pull/1669)）

2. **专用 Wandb 集成 Hook**
   - V0.26.0 引入 `MMSegWandbHook`，专门服务于 MMSegmentation 的可视化与实验追踪（PR [#1603](https://github.com/open-mmlab/mmsegmentation/pull/1603)）

3. **新增骨干网络：MAE 与 ResNet-strikes-back**
   - V0.24.0 支持 **MAE (Masked Autoencoders Are Scalable Vision Learners)**（PR [#1307](https://github.com/open-mmlab/mmsegmentation/pull/1307)、[#1523](https://github.com/open-mmlab/mmsegmentation/pull/1523)）
   - V0.24.0 支持 **ResNet strikes back** 改进型 ResNet（PR [#1390](https://github.com/open-mmlab/mmsegmentation/pull/1390)）

4. **ONNX 部署友好性优化**
   - V0.26.0 保持 `cls_token_weight` 维度不变，便于 ONNX 导出（PR [#1642](https://github.com/open-mmlab/mmsegmentation/pull/1642)）

5. **推理能力扩展**
   - V0.26.0 支持 padding 模式下的推理（PR [#1607](https://github.com/open-mmlab/mmsegmentation/pull/1607)）
   - V0.25.0 支持 MLU 硬件上的 PyTorch 后端（PR [#1515](https://github.com/open-mmlab/mmsegmentation/pull/1515)）

6. **配置系统扩展**
   - V0.24.0 在配置文件中支持额外的 dataloader 设置（PR [#1435](https://github.com/open-mmlab/mmsegmentation/pull/1435)）
   - V0.24.0 合并 BEiT 与 ConvNeXt 的 LR decay optimizer constructor，并注册到 mmseg（PR [#1438](https://github.com/open-mmlab/mmsegmentation/pull/1438)、[#1456](https://github.com/open-mmlab/mmsegmentation/pull/1456)）

---

## 【关键机制与数据】

**原文：工作机制说明**
- `cls_token_weight` 的维度保持机制（V0.26.0）：通过不改变张量形状，使该参数在 ONNX 静态图导出时与训练推理路径一致，降低部署门槛。
- `MMSegWandbHook`（V0.26.0）：作为 Wandb 的专用 Hook 封装，专为 MMSegmentation 的日志字段定制。
- MAE 支持（V0.24.0）：将掩码自编码器预训练权重接入语义分割的下游任务训练流程，并通过 `build_pos_embed` 与 `build_layers` 函数（PR [#1517](https://github.com/open-mmlab/mmsegmentation/pull/1517)）复用 BEiT 的 ViT 结构。

**原文：缺陷修复相关数据**
- V0.25.0 修复了 batch size = 1 时的 BCE loss 计算错误（PR [#1629](https://github.com/open-mmlab/mmsegmentation/pull/1629)）。
- V0.25.0 修复了 `align_corners=True` 时 `resize` 函数的 bug（PR [#1592](https://github.com/open-mmlab/mmsegmentation/pull/1592)）。
- V0.24.0 修复了二进制交叉熵的 bug 并支持单通道预测（PR [#1527](https://github.com/open-mmlab/mmsegmentation/pull/1527)、[#1454](https://github.com/open-mmlab/mmsegmentation/pull/1454)）。
- V0.24.0 修复了 MAE 训练中 `LayerDecayOptimizerConstructor` 的问题（V0.24.1 PR [#1539](https://github.com/open-mmlab/mmsegmentation/pull/1539)、[#1540](https://github.com/open-mmlab/mmsegmentation/pull/1540)）。

**原文：性能/实验数据**
- 原文未提供 mIoU、参数量、推理速度等具体性能数字。

---

## 【表格解读】

**原文无表格**

（该 changelog 仅以条目列表形式记录 PR 链接与说明，未包含任何参数表、性能对比表或配置项表。）

---

## 【公式解读】

**原文无公式**

（changelog 文档未包含任何数学公式或伪代码表达式。）

---

## 【关联】

根据原文中提及的 PR 编号与组件名称，可梳理出以下内部关联：

- **MAE ↔ BEiT ↔ ViT backbone**：V0.24.0 中 PR [#1481](https://github.com/open-mmlab/mmsegmentation/pull/1481) 重构 ViT 与 BEiT backbone 的 Transformer 编码层；PR [#1517](https://github.com/open-mmlab/mmsegmentation/pull/1517) 为 BEiT 新增 `build_pos_embed` 和 `build_layers`；PR [#1438](https://github.com/open-mmlab/mmsegmentation/pull/1438) 合并 BEiT 与 ConvNeXt 的 LR decay optimizer constructor。三者共享底层 ViT 编码器实现。
- **MAE ↔ ResNet strikes back**：V0.24.0 同期引入两条新骨干线（PR [#1307](https://github.com/open-mmlab/mmsegmentation/pull/1307) 与 PR [#1390](https://github.com/open-mmlab/mmsegmentation/pull/1390)），扩充 backbone 池。
- **BEiT ↔ Azure Blob 存储**：V0.24.0 PR [#1503](https://github.com/open-mmlab/mmsegmentation/pull/1503) 将 BEiT 检查点迁移到 Azure Blob，影响预训练权重下载链路。
- **Swin Transformer ↔ 预训练权重**：V0.24.0 PR [#1389](https://github.com/open-mmlab/mmsegmentation/pull/1389) 提供 Swin Transformer 预训练模型 URL，是本文档所在路径 `MMseg-swin` 模块的上游依赖。
- **SegFormer ↔ ADE20K ↔ UPerNet**：V0.26.0 在 ADE20K 上同时发布 SegFormer 与 UPerNet-r18 结果（PR [#1705](https://github.com/open-mmlab/mmsegmentation/pull/1705)、[#1669](https://github.com/open-mmlab/mmsegmentation/pull/1669)），共享同一评测数据集与训练管线。
- **Wandb ↔ 实验追踪**：V0.26.0 `MMSegWandbHook`（PR [#1603](https://github.com/open-mmlab/mmsegmentation/pull/1603)）是对上游 Wandb 工具的 MMSegmentation 适配层。
- **Docker ↔ Python/PyTorch/MMCV 版本**：V0.24.0 PR [#1446](https://github.com/open-mmlab/mmsegmentation/pull/1446) 与 PR [#1534](https://github.com/open-mmlab/mmsegmentation/pull/1534) 共同维护容器环境的依赖栈。

---

## 【使用方法】

**原文未涉及具体启用命令或配置项。**

该 changelog 仅作为版本变更的叙述性记录，文档中未提供：
- 配置文件 YAML 片段
- CLI 启动命令
- API 调用示例
- 依赖安装指令

如需使用上述任一新特性（如 `MMSegWandbHook`、padding 推理、MLU 后端、MAE 骨干等）的具体配置方法，需参考原文中链接的对应 PR（如 PR [#1603](https://github.com/open-mmlab/mmsegmentation/pull/1603)、[#1515](https://github.com/open-mmlab/mmsegmentation/pull/1515)、[#1307](https://github.com/open-mmlab/mmsegmentation/pull/1307)）及 MMSegmentation 官方配置目录。

> **附注**：原文在 V0.24.0 的 Contributors 部分以 "made their first contribution i" 截断，本次解读严格遵守原文，未对截断部分进行臆测。
