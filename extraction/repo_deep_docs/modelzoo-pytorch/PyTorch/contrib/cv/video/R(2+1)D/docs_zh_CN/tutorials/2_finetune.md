# 教程 2：如何微调模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/2_finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/2_finetune.md

# 一体化深度解读：R(2+1)D 微调教程文档

---

## 【定位】

本教程是 MMAction2 中 R(2+1)D（视频识别方向）模型迁移学习的操作指南，解决"如何在自有/新数据集（如 UCF101）上微调从 Kinetics-400 预训练得到的视频识别模型"这一核心问题，聚焦于配置文件中四个关键模块（Head、数据集、训练策略、预训练模型）的协同修改方法。

---

## 【技术要点】

- **两阶段微调流程**：新增数据集支持 + 修改配置文件。原文明确指出"对新数据集上的模型进行微调需要进行两个步骤：1. 增加对新数据集的支持……2. 修改配置文件"。
- **Head 修改核心**：仅需将 `cls_head` 中的 `num_classes` 从 Kinetics-400 的 **400** 改为目标数据集的类别数（如 UCF101 为 **101**）；除最后一层外的权重均可复用。
- **预训练权重加载的双路径机制**：
  - **Backbone 级别**：`pretrained='torchvision://resnet50'` 仅在主干网络上加载 ImageNet 预训练权重；
  - **整网级别**：`load_from` 用于加载整个网络的预训练权重（如 TSN 模型权重），可指向模型文件路径或 URL。
- **训练策略降配**：学习率从 `0.01` 降为 `0.005`，总 epoch 从 `100` 减为 `50`；`step=[20, 40]` 与 `total_epochs=50` 相适应。
- **优化器与梯度裁剪**：使用 SGD（`momentum=0.9`、`weight_decay=0.0001`），`grad_clip=dict(max_norm=40, norm_type=2)`。
- **数据集格式与读取**：MMAction2 提供 `RawframeDataset` 和 `VideoDataset` 等通用读取类，支持 UCF101、Kinetics-400、Moments in Time、Multi-Moments in Time、THUMOS14、Something-Something V1&V2、ActivityNet 等数据集。

---

## 【关键机制与数据】

### 工作原理：四模块联动

微调工作流沿"Head → 数据集 → 训练策略 → 预训练模型"四个环节顺序调整：

| 模块 | 改动前（Kinetics-400） | 改动后（UCF101 示例） | 原文依据 |
|------|------------------------|------------------------|----------|
| cls_head.num_classes | 400 | 101 | "UCF101 拥有 101 类行为，因此需要把 400 (Kinetics-400 的类别数) 改为 101" |
| 优化器 lr | 0.01 | 0.005 | 原文注释 "从 0.01 改为 0.005" |
| total_epochs | 100 | 50 | 原文注释 "从 100 改为 50" |
| 数据根目录 | k400 路径 | `data/ucf101/rawframes_train/` 等 | 原文代码块 |

### 数据流与配置继承

- **配置继承性**：`configs/_base_/default_runtime.py` 中将 `load_from=None` 设为默认，用户可直接在下游配置文件中设置 `load_from` 的值进行覆盖。
- **预训练权重范围**：`pretrained` 仅作用于 backbone（主干网络）；`load_from` 用于全网络权重加载。
- **checkpoint 配置**：`checkpoint_config = dict(interval=5)` 表示每 5 个 epoch 保存一次检查点。

### 性能预期（原文）

原文未提供具体的微调精度/性能数字，仅定性说明："通常情况下，设置较小的学习率，微调模型少量训练批次，即可取得较好效果"。

---

## 【表格解读】

**原文无表格**。

注：原文中出现的均为 Python 配置代码块（`model = dict(...)`、`dataset_type = ...`、`optimizer = dict(...)`、`load_from = ...`），属于配置片段而非结构化表格，未以 markdown 表格形式呈现。

---

## 【公式解读】

**原文无公式**。

文档未包含任何数学公式或伪代码形式的算法描述。

---

## 【关联】

依据文档中显式提及的内部链接以及内容上下文，本教程与以下文档/模块存在上下游依赖关系：

1. **上游/前置教程**：[`3_new_dataset.md`](3_new_dataset.md)——"教程 3：如何增加新数据集"。
   - 关系：微调流程的第一步（"增加对新数据集的支持"）即依赖该教程；本教程是教程 3 的下游，即假设用户已完成数据集注册，仅需在配置文件层面修改。

2. **并行参考教程**：[`1_config.md`](1_config.md)——配置文件说明。
   - 关系：教程 1 提供配置文件（Head、数据集、训练策略、预训练模型）四个部分的语义规范；本教程展示这些部分在 UCF101 微调场景下的具体取值变化。

3. **依赖的代码基类：`RawframeDataset` / `VideoDataset`**
   - 来源：MMAction2 框架；用于将自建数据集转换为已有格式。

4. **框架级常量位置：`configs/_base_/default_runtime.py`**
   - 作用：定义 `load_from=None` 默认值，是配置继承链的根。

5. **模型来源：model zoo**
   - 原文提到的预训练权重 URL 指向 `mmaction-v1/recognition/tsn_r50_1x1x3_100e_kinetics400_rgb/`，表明该 TSN 模型权重可作为微调起点。

---

## 【使用方法】

### 启用方式（步骤化）

1. **替换 Head 的类别数**（在配置文件的 `cls_head` 段）：
   ```python
   cls_head=dict(type='TSNHead', num_classes=101, ...)
   ```
   - 注意：`pretrained='torchvision://resnet50'` 仅用于 backbone 的 ImageNet 初始化，并非微调预训练权重。

2. **切换数据集配置**：
   ```python
   dataset_type = 'RawframeDataset'
   data_root = 'data/ucf101/rawframes_train/'
   data_root_val = 'data/ucf101/rawframes_val/'
   ann_file_train = 'data/ucf101/ucf101_train_list.txt'
   ann_file_val = 'data/ucf101/ucf101_val_list.txt'
   ann_file_test = 'data/ucf101/ucf101_val_list.txt'
   ```

3. **调整训练策略**（降配微调）：
   ```python
   optimizer = dict(type='SGD', lr=0.005, momentum=0.9, weight_decay=0.0001)
   optimizer_config = dict(grad_clip=dict(max_norm=40, norm_type=2))
   lr_config = dict(policy='step', step=[20, 40])
   total_epochs = 50
   checkpoint_config = dict(interval=5)
   ```

4. **加载预训练权重**（在配置文件中设置）：
   ```python
   load_from = 'https://open-mmlab.s3.ap-northeast-2.amazonaws.com/mmaction/mmaction-v1/recognition/tsn_r50_1x1x3_100e_kinetics400_rgb/tsn_r50_1x1x3_100e_kinetics400_rgb_20200614-e508be42.pth'
   ```
   - 原文："模型路径可以在 model zoo 中找到"。

### 关键参数/命令对照

| 项 | 默认/原值 | 微调推荐值 | 说明 |
|----|-----------|-----------|------|
| num_classes | 400 | 101（UCF101） | 需与新数据集类别数一致 |
| lr | 0.01 | 0.005 | 微调用更小学习率 |
| total_epochs | 100 | 50 | 减少训练轮次 |
| step | — | [20, 40] | 学习率衰减节点（与 50 epoch 相适应） |
| max_norm | — | 40 | 梯度裁剪上限 |
| norm_type | — | 2 | L2 范数 |
| momentum | — | 0.9 | SGD 动量 |
| weight_decay | — | 0.0001 | 权重衰减 |
| checkpoint interval | — | 5 | 每 5 epoch 保存 |
| dropout_ratio | — | 0.4 | Head dropout |
| init_std | — | 0.01 | 权重初始化标准差 |
| in_channels (Head) | — | 2048 | ResNet-50 输出通道 |
| spatial_type | — | 'avg' | Head 空间池化类型 |
| consensus | — | AvgConsensus(dim=1) | TSN 时序融合方式 |
| norm_eval | — | False | backbone BN 训练模式 |
| average_clips (test_cfg) | — | None | 测试时 clip 聚合策略 |

### 启动命令

原文未涉及具体的训练启动命令（如 `python tools/train.py ...`），仅展示配置文件层的修改方法。
