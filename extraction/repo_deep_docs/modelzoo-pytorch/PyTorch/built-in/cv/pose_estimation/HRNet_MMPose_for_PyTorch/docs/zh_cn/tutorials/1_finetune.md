# 教程 1：如何微调模型

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/1_finetune.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/1_finetune.md

# 教程 1：如何微调模型 —— 一体化深度解读

## 【定位】

本文是 MMPose 0.x 系列教程的第 1 篇，针对"如何在 COCO 等数据集上预训练后再到自定义数据集（含 COCO-WholeBody 等）上微调 Top-Down 关键点估计模型"这一工程问题，给出配置文件层面的标准化修改模板，覆盖 **网络头 / 数据集 / 训练策略 / 预训练权重载入** 四个修改面。

---

## 【技术要点】

1. **微调总流程**：支持新数据集 + 修改配置文件。具体需改四个部分 —— 网络头（keypoint_head）、数据集（data）、训练策略（optimizer / lr_config）、预训练模型（load_from）。
2. **网络头修改的最小集**：仅需修改 `keypoint_head.out_channels` 与 `channel_cfg` 中的关键点个数相关字段；最后一层预训练参数不会被加载，其余层正常加载。例如 COCO(17) → COCO-WholeBody(133)。
3. **主干与网络头职责分离**：
   - `pretrained` 字段 **只** 初始化 backbone（不会初始化 head）；
   - `load_from` 字段 **载入整个网络**（含 head）的预训练权重，是微调场景的推荐用法。
4. **数据集接入方式**：用户将自定义数据转为已有数据集格式（COCO/MPII/MPII-TRB 等十余种），并替换 `data` 字典中的 `type`、`ann_file`、`img_prefix` 三个字段。
5. **微调训练策略要点**：使用 **Adam 优化器**，学习率 `lr=5e-4`（可适当减小）；`lr_config` 使用 `step` policy + `linear` warmup，`warmup_iters=500`，`warmup_ratio=0.001`，`step=[170, 200]`，`total_epochs=210`（epoch 数可适当减小）。
6. **参考配置**：以 HRNet-W48 为例，backbone 采用 4 阶段结构，`keypoint_head=TopdownHeatmapSimpleHead`，`in_channels=48`，`num_deconv_layers=0`，`final_conv_kernel=1`，损失函数 `JointsMSELoss(use_target_weight=True)`；推理时 `flip_test=True, post_process='unbiased', shift_heatmap=True, modulate_kernel=17`。

---

## 【关键机制与数据】

- **微调 vs. 从头训练的选择依据**（原文）："在新数据集上的模型微调需要两个步骤：1. 支持新数据集；2. 修改配置文件。" 因为预训练模型已具备良好的特征提取能力，故只需要小学习率、短轮次即可获得性能提升。
- **Head 输出层不加载的机制**（原文）：当 `num_output_channels` 改变时，预训练权重与新维度不匹配，最后一层被自动跳过，其余层正常载入；这保证了 backbone 的迁移学习仍然有效。
- **数据流（原文配置中可见）**：单卡 `samples_per_gpu=32`，`workers_per_gpu=2`，训练/验证/测试 pipeline 分别绑定到 `train2017/` 与 `val2017/` 图像目录与对应的 `coco_wholebody_*_v1.0.json` 标注文件。
- **预训练权重来源（原文给出的两条 URL）**：
  - ImageNet 预训练 backbone：`https://download.openmmlab.com/mmpose/pretrain_models/hrnet_w48-8ef0771d.pth`（用于 `pretrained` 字段）
  - COCO 预训练整网：`https://download.openmmlab.com/mmpose/top_down/hrnet/hrnet_w48_coco_384x288_dark-741844ba_20200812.pth`（用于 `load_from` 字段）
- **性能数据**：原文未给出 AP/AR 等具体数值。

---

## 【表格解读】

**原文无表格。**

（文中的若干 Python 配置块以代码形式呈现参数表，但并非 markdown 表格，因此按"原文无表格"处理。下文《公式解读》同。）

---

## 【公式解读】

**原文无公式。**

（仅含 Python 配置片段与文件/网络 URL，未出现任何 LaTeX 数学式或伪代码算法表达式。）

---

## 【关联】

- **与 [2_new_dataset.md](2_new_dataset.md) 的关系**：本文将"支持新数据集"作为微调的前置步骤并以链接方式委托给该教程；自身聚焦"数据集名 + ann_file + img_prefix 三字段替换"层面的快速接入，不展开数据集格式细节。
- **与 [0_config.md](0_config.md) 的关系**：本文中所有修改（head、data、optimizer、lr_config、pretrained、load_from）都发生在配置文件内部，因此本文实质上是配置文档的一个"微调场景示例"，需配合配置文档理解字段语义。
- **与模型库（model zoo）的关系**：原文引用 `https://mmpose.readthedocs.io/en/0.x/modelzoo.html` 与 `hrnet_w48_coco_384x288_dark-...pth`，说明 `load_from` 的合法取值来源于模型库已发布的预训练模型清单。
- **上下游流水线关系**：微调本身并不重新设计 backbone，本文示例以 HRNet 为载体（4 阶段、并行多分支结构），因此若需更换 backbone（如 ResNet、HRNet-W32 等），backbone 字典需整体替换，但 head/dataset/strategy 三块修改规则不变。

---

## 【使用方法】

1. **新增数据集**：按 [2_new_dataset.md](2_new_dataset.md) 完成数据集类接入后，把自定义数据放进 `data_root = 'data/coco'`（或对应路径），并修改 `data` 字典中的 `type`、`ann_file`、`img_prefix`。
2. **修改网络头**：在 `channel_cfg` 中将 `num_output_channels`、`dataset_joints`、`dataset_channel`、`inference_channel` 由 17 改为新数据集关键点数（示例 133）；同时确认 `keypoint_head.out_channels` 与 `channel_cfg['num_output_channels']` 一致。
3. **调整训练策略**（示例值均为原文给出的可调起点）：
   - `optimizer=dict(type='Adam', lr=5e-4)`
   - `optimizer_config=dict(grad_clip=None)`
   - `lr_config=dict(policy='step', warmup='linear', warmup_iters=500, warmup_ratio=0.001, step=[170, 200])`
   - `total_epochs = 210`（原文建议"适当减小"）
4. **载入预训练模型**（两种方式，按需二选一/组合）：
   - 仅初始化 backbone：在 `model.pretrained` 写 `hrnet_w48-8ef0771d.pth`（ImageNet 权重）。
   - 加载整网预训练：在配置文件顶层写 `load_from = 'https://download.openmmlab.com/mmpose/top_down/hrnet/hrnet_w48_coco_384x288_dark-741844ba_20200812.pth'`（CCO 384×288 dark 权重）。
5. **运行入口**：原文未涉及具体启动命令（如何调用 `tools/train.py`、传 `config` 与 `work-dir` 等参数未在本文给出），如需执行请参照 MMPose 主仓 train/test 文档。
