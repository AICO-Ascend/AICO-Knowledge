# [3.1.0](https://github.com/dreamquark-ai/tabnet/compare/v3.0.0...v3.1.0) (2021-01-12)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/TabNet_ID2862_for_PyTorch/CHANGELOG.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/TabNet_ID2862_for_PyTorch/CHANGELOG.md

# TabNet 项目 CHANGELOG 深度解读

## 【定位】
本篇文档是 dreamquark-ai/tabnet（PyTorch 实现的表格数据深度学习模型 TabNet）从 **v1.0.0（2019-12-03）至 v3.1.1（2021-02-02）** 的版本演进日志，记录了约 14 个月内 12 个版本号的 Bug 修复与功能新增，重点呈现该库从"基础可用的单任务分类器"逐步演化为"支持多任务、自监督预训练、稀疏特征选择、可解释性的工业级表格学习框架"的能力成长曲线。

## 【技术要点】

1. **自监督预训练 (Self-supervised Pretraining)**：v3.0.0 引入，配套 v3.1.1 修复 `preds_mapper to pretraining`，让 TabNet 能够在无标签数据上学习表征，再迁移到下游有标签任务。
2. **多任务分类器 TabNetMultiTaskClassifier**：v2.0.0 引入，将单一分类头扩展为可同时预测多个相关任务的共享骨干结构。
3. **掩码相关损失 (mask-dependent loss)**：v3.0.0 引入，将特征选择 mask 的稀疏性约束与主任务损失耦合训练。
4. **训练稳定性保障**：v2.0.0 加入 `check nan and inf` 检测；v3.0.0 修复 `checknan allow string as targets` 使目标列支持字符串型；v2.0.0.1 限定 `pin memory` 仅在训练阶段生效，CPU 设备下自动关闭 `pin_memory`。
5. **稀疏化与可解释性**：v1.0.5 切换至 **sparse matrix trick** 提升 mask 计算效率；v1.2.0 将 **entmax** 作为可配置参数（区别于默认 sparsemax，提供更平滑/更稀疏的注意力分布）。
6. **模型持久化与跨设备兼容**：v1.2.0 实现 `save and load tabnet models`；v3.1.0 单独增加 `save and load preds_mapper`；v3.0.0/v2.0.0.1 多次修复 CPU↔GPU 加载兼容（`map_location`、`load from cpu when saved on gpu`、`torch.load map_location in Py36 fallback`）。
7. **训练控制面增强**：v2.0.0 加入 **callbacks and metrics** 系统与 **easy schedulers**；v1.1.0 暴露 `num_workers` 与 `drop_last` 至 `fit` 接口；v1.2.0 允许自定义其他 optimizer 参数与回归任务的样本权重采样 (`weights sample for regression`)。

## 【关键机制与数据】

- **版本节奏**（原文）：1.0.0 (2019-12-03) → 1.0.x 系列小修 → 1.1.0 (2020-06-02) → 1.2.0 (2020-07-01) → 2.0.0 (2020-10-13) → 2.0.1 (2020-10-15) → 3.0.0 (2020-12-15) → 3.1.0 (2021-01-12) → 3.1.1 (2021-02-02)。其中 2.0.0 与 3.0.0 间隔约 2 个月，且各自后立即有一个 0.0.1 修补版本，说明两个主版本都伴随跨设备/跨依赖兼容问题需要即时打补丁。
- **v3.0.0 三大新特性（原文）**：`add new default metrics`、`enable self supervised pretraining`、`mask-dependent loss`，标志着 TabNet 从纯监督范式迈向"预训练 + 微调"范式。
- **v2.0.0 重构（原文）**：`refacto models with metrics and callbacks` + `adding callbacks and metrics` + `add easy schedulers` 三连提交，将训练循环从硬编码改造为可插拔架构，是 API 层面最大的一次重构。
- **依赖版本约束（原文）**：v1.0.0 阶段将 numpy 锁定到 v1.17.3→v1.17.4、torch 锁定到 v1.3.1，表明该库早期与 PyTorch 1.x、NumPy 1.17 系列深度耦合。

## 【表格解读】
**原文无表格**。原 CHANGELOG 全部以 Keep-a-Changelog 风格的 Markdown 标题层级 + Bullet 列表组织，仅在每行条目末尾附带 GitHub commit 哈希链接（如 `76f2c85`、`d4af838`）作为可追溯标识，不含任何参数表、性能对比表或配置矩阵。

## 【公式解读】
**原文无公式**。整个文档未出现任何数学公式、伪代码或 LaTeX 表达式，所有变更均通过自然语言 commit message 描述（如 "switch to sparse matrix trick"、"mask-dependent loss"），具体数学细节需查阅对应 commit 源码。

## 【关联】

由于文末标注"内部链接: (无)"，本篇 changelog 没有显式的内部锚点跳转。但从提交间逻辑可梳理出以下隐式关联链：

- **预训练 ↔ 预测映射**：`enable self supervised pretraining` (v3.0.0) → `save and load preds_mapper` (v3.1.0) → `add preds_mapper to pretraining` (v3.1.1)，构成"预训练产出 → 映射持久化 → 映射复用"的闭环。
- **稀疏 mask 机制**：v1.0.5 `switch to sparse matrix trick` → v1.2.0 `add entmax as parameter` → v1.1.0 `remove mask computations from forward` → v3.0.0 `mask-dependent loss`，四步构成 mask 计算从"前向计算 → 稀疏加速 → 灵活稀疏化函数 → 损失耦合"的递进。
- **持久化兼容层**：v1.2.0 `save and load tabnet models` + `save params and easy loading` → v2.0.1 `torch.load map_location in Py36 fallback` → v3.0.0 `load from cpu when saved on gpu` → v3.1.0 `save and load preds_mapper`，形成从模型权重 → 训练参数 → 跨设备加载 → 标签映射器持久化的递进。
- **训练控制面**：v1.0.1 `**regression:** fix scheduler` → v2.0.0 `add easy schedulers` + `adding callbacks and metrics` → v3.0.0 `add new default metrics`，将回归分支的调度器修复扩展为通用调度器框架，再加入指标系统。
- **多任务扩展**：v1.1.0 `add multi output regression` → v2.0.0 `TabNetMultiTaskClassifier`，从回归多输出演进到分类多任务，统一为"共享骨干 + 多任务头"范式。

## 【使用方法】

**原文未涉及**。CHANGELOG 本身仅记录"改了什么"，不包含启用方式、配置项或命令行说明。以下为基于 changelog 中提及的特性推断出的常见入口（仅作背景说明，非原文内容）：

- 使用 **自监督预训练**：调用 v3.0.0 引入的预训练接口（v3.1.1 修复了 `preds_mapper` 联动）。
- 配置 **entmax 稀疏化**：在 `TabNetClassifier` / `TabNetRegressor` 构造时通过 v1.2.0 暴露的 `entmax` 参数切换稀疏函数。
- 启用 **NaN/Inf 检测**：v2.0.0 引入的 `check_nan` 行为由 v3.0.0 进一步支持字符串型 targets。
- 保存与加载：通过 v1.2.0 的 `save_model` / `load_model`，搭配 v3.1.0 的 `preds_mapper` 持久化，跨设备加载需依赖 v3.0.0 的 `map_location` 修复。
- 多任务训练：实例化 v2.0.0 新增的 `TabNetMultiTaskClassifier`。
- 回调与指标：v2.0.0 起可通过 callbacks/metrics 接口自定义训练循环，v3.0.0 起使用新增的默认指标集合。

> 实际启用参数、命令行示例、配置文件示例需查阅仓库 README 或对应 commit 源码（本 changelog 未提供）。
