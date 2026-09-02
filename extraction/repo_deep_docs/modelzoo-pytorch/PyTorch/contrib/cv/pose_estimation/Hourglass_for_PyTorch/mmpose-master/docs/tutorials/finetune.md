# Tutorial 1: Finetuning Models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/tutorials/finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/tutorials/finetune.md

# 一体化深度解读: Tutorial 1: Finetuning Models

## 【定位】
本教程解决「如何将在 COCO 数据集上预训练的人体姿态估计模型,迁移 (finetune) 到其他自定义数据集 (例如 PoseTrack) 上以获得更好性能」的问题,提供从数据集接入到配置文件修改的全套操作指引。

---

## 【技术要点】

1. **微调前置条件**: 模型需已在 COCO 上预训练完成 (来自 [Model Zoo](../top_down_models.md)),作为下游数据集的初始化权重。
2. **微调整体流程 (两步法)**:
   - 第一步: 按 [Tutorial 2: Adding New Dataset](new_dataset.md) 增加新数据集支持。
   - 第二步: 按本教程修改配置文件 (config),共需改动四个部分。
3. **模型配置改动**: 仅需修改 `keypoint_head` 下的 `out_channels` 参数以匹配新数据集的关键点数 (原文示例中保留为 `17`,即 COCO 的 17 个关键点)。
4. **训练调度改动**: 相比默认调度,微调通常采用**更小的学习率**与**更少的训练轮次**。原文给出示例: `lr=1e-4`、`total_epochs=20`、`step=[10, 15]` (即在第 10、15 轮衰减学习率)。
5. **预训练权重加载**: 通过在 config 中设置 `load_from` 字段指向本地预训练权重文件路径 (如 `resnet50_coco.pth`),建议**预先下载**到本地以避免训练过程中下载造成的延迟。
6. **支持的数据集现状**: MMPose 已原生支持 COCO 与 MPII-TRB 数据集,其他数据集需要用户自行添加。

---

## 【关键机制与数据】

**工作原理**: 微调的本质是迁移学习 (transfer learning) — 利用大规模数据集 (COCO) 上学习到的视觉特征作为初始化,在小规模/特定场景数据集 (如 PoseTrack) 上以更小学习率与更少迭代轮次微调,使模型适配新数据的关键点定义与分布。

**配置修改的数据流 (按执行顺序)**:

1. **Modify Model** → 修改 `keypoint_head.out_channels`,使网络输出维度匹配新数据集的关键点数。
2. **Modify Dataset** → 准备数据集与对应 config (MMPose 原生支持 COCO 与 MPII-TRB)。
3. **Modify Training Schedule** → 改用 Adam 优化器,`lr=1e-4`,启用 `linear` warmup (500 iter, ratio=0.001),`step` 学习率衰减在 `[10, 15]` 轮,共训练 `20` 个 epoch。
4. **Use Pre-trained Model** → 在 config 设置 `load_from = 'resnet50_coco.pth'`,指向本地预训练权重。

**原文性能数据**: 原文未给出具体性能指标 (如 mAP、AP50/70、误差数值等),仅强调「可以取得 better performance」,无定量数字。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游/来源**:
  - [Model Zoo](../top_down_models.md) — 提供在 COCO 上预训练好的姿态估计模型权重,是微调的起点。
  - `resnet50_coco.pth` (在 `load_from` 中引用) — 即来自 Model Zoo 的具体预训练权重文件。
- **平行教程**:
  - [Tutorial 2: Adding New Dataset](new_dataset.md) — 微调流程的前置步骤,负责把数据集接入 MMPose 框架。
- **模块依赖**:
  - 本教程中的 `TopDown` 模型类型、`ResNet` backbone、`TopDownSimpleHead` head — 均属于 MMPose 顶向下 (top-down) 姿态估计体系,具体细节与可选 backbone / head 列表应参考 [top_down_models.md](../top_down_models.md)。

---

## 【使用方法】

原文涉及的具体配置项与命令如下 (均为 Python config 写法,非命令行):

| 配置项 | 原文值 | 含义 |
|---|---|---|
| `model.type` | `'TopDown'` | 顶向下姿态估计模型类型 |
| `model.pretrained` | `None` | 不再自动下载 backbone 预训练,改由 `load_from` 控制 |
| `model.backbone` | `dict(type='ResNet', depth=18)` | 使用 ResNet-18 作为骨干网络 |
| `model.keypoint_head.in_channels` | `512` | 头部输入通道数 |
| `model.keypoint_head.out_channels` | `17` | **微调时需改**为新数据集关键点数 |
| `model.test_cfg.flip_test` | `True` | 启用水平翻转测试增强 |
| `model.test_cfg.modulate_kernel` | `11` | 解码核大小 |
| `model.loss_pose` | `JointsMSELoss, use_target_weight=False` | 损失函数 |
| `optimizer` | `Adam, lr=1e-4` | **微调采用更小学习率** |
| `lr_config.policy` | `'step'` | step 学习率策略 |
| `lr_config.warmup` | `'linear'`, `warmup_iters=500`, `warmup_ratio=0.001` | 线性 warmup |
| `lr_config.step` | `[10, 15]` | 第 10、15 epoch 衰减 |
| `total_epochs` | `20` | **比默认更少的训练轮次** |
| `load_from` | `'resnet50_coco.pth'` | **预训练权重路径,需提前下载** |

> 原文未涉及具体命令行启动方式 (如 `tools/train.py` 的调用),所有操作均通过修改 config 文件完成。
