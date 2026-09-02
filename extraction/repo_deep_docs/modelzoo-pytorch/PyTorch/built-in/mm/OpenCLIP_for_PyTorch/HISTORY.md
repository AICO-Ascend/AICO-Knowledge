# HISTORY

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/mm/OpenCLIP_for_PyTorch/HISTORY.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/mm/OpenCLIP_for_PyTorch/HISTORY.md

【定位】
本文档是 OpenCLIP_for_PyTorch 项目（多模态视觉-语言预训练框架 OpenCLIP 的 PyTorch 实现/移植）的版本变更日志（changelog），按版本号升序倒序记录自 1.1.1 至今（2.17.2）的功能新增、模型权重发布、Bug 修复与重构内容，是项目演进轨迹的官方说明。

【技术要点】
1. **多语言与多文本塔扩展**：从 2.5.0 起引入 XLM-RoBERTa 系列文本塔，2.7.0 发布 multilingual H/14 xlm roberta large，2.3.0 起支持 HuggingFace 通用 Text Transformer（`Generalizable Text Transformer with HuggingFace Models`）。
2. **量化与精度支持**：2.17.0 新增 int8 支持；2.1.0 加入 bfloat16 选项；2.4.0 恢复了非 bf16/fp16 输入下的 LayerNorm 实现。
3. **新型骨干网络与权重发布**：2.10.0 新增 ViT-bigG-14，2.11.0 加入 CoCa 支持与权重及 ConvNeXt-Large，2.12.0 与 2.15.0 持续扩充 ConvNeXt 系列（xxlarge、320×320 微调权重），2.16.0 改进 g-14 权重。
4. **训练与数据管线增强**：2.8.0 支持梯度累积（gradient accumulation），2.13.0/2.14.0 引入带不同采样权重的数据集混合（dataset mixtures）并下移至 shard 层级，2.9.0 支持 `--resume latest` 自动续训。
6. **生态与依赖管理**：2.8.1/2.16.0 调整 protobuf 依赖，2.6.0 允许从 pypi 直接进行训练，2.10.1 增加 HuggingFace Hub `hf-hub:org/model_id` 加载方式，2.11.1/2.13.0 将 transformers 设为可选依赖。
7. **日志、可视化与可观测性**：2.10.0 引入 S3 同步日志/检查点与 LR scheduler（constant、constant with cooldown）选项，2.15.0 新增 samples per second per gpu 日志，2.9.3 修复 wandb 并行运行合并问题。

【关键机制与数据】
- **梯度累积**：原文 2.8.0「add support for gradient accumulation」；2.14.0「Fix CoCa accum-grad training」并修复相关累积梯度训练问题。
- **混合精度**：原文 2.1.0「bfloat16 option」；2.4.0「Bring back LayerNorm impl that casts to input for non bf16/fp16」。
- **低精度量化**：原文 2.17.0「Add int8 support」（具体量化方案/校准方式原文未涉及）。
- **自动续训**：原文 2.9.0「auto-resume from the latest checkpoint on restart via `--resume latest`」；2.10.0「Fix wandb autoresuming when resume is not set」。
- **学习率调度器**：原文 2.10.0「New options for LR schedulers, constant and constant with cooldown」。
- **吞吐日志**：原文 2.15.0「Add samples per second per gpu logging」。
- **Checkpoint 同步**：原文 2.10.0「Added an option to sync logs and checkpoints to S3 during training」。
- **Hub 模型推送**：原文 2.17.2「Update push_to_hf_hub」；2.10.1「`hf-hub:org/model_id` support for loading models w/ config and weights in Hugging Face Hub」。
- **patch dropout**：原文 2.8.0「add support for patch dropout」；2.8.1「override the default patch dropout value in 'vision_cfg'」；2.8.2「wrapped patchdropout in a torch.nn.Module」。
- **ConvNeXt 训练策略融合**：原文 2.10.0「`timm` augmentation + regularization (dropout / drop-path) supported」，同时移除配置前缀「`timm-` model prefix removed from configs」。
- **梯度检查点（gradient checkpointing）**：原文 1.1.1「Add grad checkpointing support」；2.3.1「Implement grad checkpointing for hf model」。
- **数据集混合权重**：原文 2.13.0「Add support for dataset mixtures with different sampling weights」；2.14.0「Move dataset mixtures logic to shard level」。
- **零样本分类重构**：原文 2.17.0「Refactor zero-shot classification code」；2.4.0「zero_shot.py: set correct tokenizer based on args」。
- **CoCa 生成/蒸馏**：原文 2.11.0「coca support and weights」；2.12.0「Clean and improve CoCa generation」与「Support model distillation」；2.11.1「Add MSCOCO CoCa finetunes to pretrained models」。
- **输入归一化选项**：原文 2.12.0「Added input_patchnorm option」。
- **数据加载稳定性**：原文 1.1.1「more robust data loader」；2.9.2「Fix braceexpand memory explosion for complex webdataset urls」；2.9.0「Allow webp in webdataset」。

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
- **模型权重/架构串联**：CoCa（2.11.0 → 2.11.1 预训练微调 → 2.12.0 生成改进与蒸馏支持 → 2.14.0 accum-grad 训练修复）；ConvNeXt（2.8.0 配置 → 2.10.0 base/base_w 预训练 → 2.11.0 Large 权重 → 2.12.0 配置一致性 + 320×320 微调权重 → 2.15.0 xxlarge 权重）；ViT-bigG-14/g-14（2.10.0 → 2.16.0 改进 g-14）。
- **HuggingFace 生态整合**：HuggingFace 文本塔（2.3.0 引入 → 2.3.1 梯度检查点 + 自定义开关 → 2.4.0 参数清理 → 2.4.1 补全 `hf_tokenizer_name` → 2.5.0 首例基于 HF 文本编码器的 CLIP 权重 → 2.10.1 Hub 加载 → 2.11.1/2.13.0 设为可选依赖 → 2.16.1 加入 PubMed CLIP 的 HF BERT 配置 → 2.17.2 更新 `push_to_hf_hub`）。
- **训练基础设施演进**：梯度检查点（1.1.1 → 2.3.1 HF 版）→ 梯度累积（2.8.0 → 2.14.0 修复）→ 自动续训（2.9.0 → 2.10.0 wandb 联动）→ 混合精度（2.1.0 → 2.4.0 LayerNorm 修正）→ 量化（2.17.0 int8）。
- **数据集与采样**：Webdataset 数据源（2.9.0 webp 支持 → 2.9.2 braceexpand 修复）→ 数据集混合（2.13.0 加权 → 2.14.0 shard 化）→ 训练样本数控制（2.16.1 修复 `--train-num-samples`）。
- **下游接口**：零样本分类（`zero_shot.py`，2.4.0 修正 tokenizer → 2.17.0 重构）与上游特征（`get_labels` 2.14.0 重构、`context_length`/`vocab_size` 在 2.16.1/2.16.2 反复修正）形成前后呼应。
- **日志与调度**：S3 同步（2.10.0）+ LR scheduler constant/cooldown（2.10.0）+ 每 GPU 吞吐日志（2.15.0）+ wandb 修复（2.9.3、2.10.0）共同构成训练可观测性体系。

【使用方法】
- 启用 int8 量化：原文 2.17.0「Add int8 support」（具体启用方式原文未涉及）。
- 自动续训：原文 2.9.0 启动训练时传 `原文: --resume latest`。
- 模型蒸馏：原文 2.12.0「Support model distillation」（具体配置项原文未涉及）。
- 加载 HuggingFace Hub 模型：原文 2.10.1 使用 `原文: hf-hub:org/model_id` 形式路径进行模型加载。
- 上传模型至 HuggingFace Hub：原文 2.17.2 更新 `push_to_hf_hub`（具体调用命令原文未涉及）。
- LR scheduler 选择：原文 2.10.0「constant and constant with cooldown」选项（具体参数名原文未涉及）。
- S3 同步日志/检查点：原文 2.10.0 提供相关选项（具体开关原文未涉及）。
- 数据集混合权重：原文 2.13.0 支持在数据集配置中设定不同采样权重（具体字段名原文未涉及）。
- patch dropout 设置：原文 2.8.0/2.8.1 在 `vision_cfg` 中覆盖默认值（具体键名原文未涉及）。
- 输入 PatchNorm 开关：原文 2.12.0「Added input_patchnorm option」（具体键名原文未涉及）。
