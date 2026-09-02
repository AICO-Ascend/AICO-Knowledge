# History

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/others/DCN_for_PyTorch/docs/source/History.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/others/DCN_for_PyTorch/docs/source/History.md

【定位】
本篇是 DeepCTR-Torch（基于 PyTorch 的点击率/特征交互模型库）在 modelzoo-pytorch 仓 DCN_for_PyTorch 样例目录下的版本变更日志，按时间倒序记录 2019-09-22 至 2021-04-04 间共 11 个版本（v0.1.0 → v0.2.6）所引入的新模型、API 重构、训练辅助机制、bug 修复与工程化能力。

【技术要点】
1. **模型引入主线**（按版本顺序）：v0.1.1 新增 [CCPM](./Features.html#ccpm-convolutional-click-prediction-model) → v0.2.1 新增 [DIN](./Features.html#din-deep-interest-network) 与 [DIEN](./Features.html#dien-deep-interest-evolution-network) → v0.2.3 新增 **DCN-M & DCN-Mix** → v0.2.6 新增 **IFM 与 DIFM**。
2. **输入与特征列重构**：v0.1.2 新增 sequence (multi-value) 输入支持；v0.1.3 简化输入逻辑；v0.2.0 **重构 [feature columns](./Features.html#feature-columns)**，是特征列接口的定型节点。
3. **训练回调体系**：v0.2.3 引入 **EarlyStopping + ModelCheckpoint**；v0.2.4 引入 **History** 回调；三者共同构成「训练历史记录 / 早停 / 检查点」完整回调链。
4. **数值与训练工程**：v0.2.0 在指标计算中 **支持双精度 (double precision)**；v0.2.6 引入 **多 GPU 运行 (multi-gpus running) 并附 example**。
5. **可靠性迭代**：v0.2.2 改进 **reproducibility** 并修若干 bug；v0.2.4 提升兼容性并修 issue；v0.2.5 修复 **DCN-M** 中的 bug。
6. **分发起点**：v0.1.0 作为首发版本发布至 [PyPi](https://pypi.org/project/deepctr-torch/)。

【关键机制与数据】
原文为版本变更日志，**未给出任何性能指标、训练曲线、数据流或计算公式**，可识别的「机制」信息均以条目形式记录：

- 原文（v0.2.6）："Add add IFM and DIFM; Support multi-gpus running(example)." —— 引入 IFM/DIFM 两个交互类模型，并支持多卡训练，提供 example。
- 原文（v0.2.5）："Fix bug in DCN-M." —— 修复 DCN-M 的 bug。
- 原文（v0.2.4）："Imporve compatibility & fix issues. Add History callback." —— 提升兼容性 + 引入 History 回调（[example 链](https://deepctr-torch.readthedocs.io/en/latest/FAQ.html#set-learning-rate-and-use-earlystopping)）。
- 原文（v0.2.3）："Add DCN-M&DCN-Mix. Add EarlyStopping and ModelCheckpoint callbacks." —— 引入 DCN 系列两变体 + 早停与模型检查点回调。
- 原文（v0.2.2）："Improve the reproducibility & fix some bugs." —— 复现性增强与修 bug。
- 原文（v0.2.1）："Add DIN and DIEN." —— 兴趣网络与兴趣演化网络落地。
- 原文（v0.2.0）："Refactor feature columns. Support to use double precision in metric calculation." —— 特征列重构 + 指标计算支持双精度。
- 原文（v0.1.3）："Simplify the input logic." —— 简化输入逻辑。
- 原文（v0.1.2）："Add sequence(multi-value) input support." —— 多值/序列输入支持。
- 原文（v0.1.1）："Add CCPM." —— 卷积点击预测模型。
- 原文（v0.1.0）："first version v0.1.0 is released on PyPi." —— 上 PyPi 作为首发分发。

【表格解读】原文无表格。

【公式解读】原文无公式。

【关联】
- **特性详情页链接（文末内部链接）**：
  - `./Features.html#din-deep-interest-network` ↔ v0.2.1 引入 DIN。
  - `./Features.html#dien-deep-interest-evolution-network` ↔ v0.2.1 引入 DIEN。
  - `./Features.html#feature-columns` ↔ v0.2.0 重构特征列（接口定型）。
  - `./Features.html#ccpm-convolutional-click-prediction-model` ↔ v0.1.1 引入 CCPM。
- **外部文档交叉点**：`https://deepctr-torch.readthedocs.io/en/latest/FAQ.html#set-learning-rate-and-use-earlystopping` 与 v0.2.3（EarlyStopping / ModelCheckpoint）、v0.2.4（History）回调条目同时被引用，对应"学习率设置 + 早停"的 example。
- **GitHub release 链接**：每个版本号链向 `https://github.com/shenweichen/DeepCTR-Torch/releases/tag/vX.Y.Z`，构成与上游 DeepCTR-Torch 主仓的版本锚点。
- **模型家族演化关系**：CCPM（卷积点击预测）→ DIN / DIEN（兴趣演化）→ DCN-M / DCN-Mix（深度交叉）→ IFM / DIFM（特征交互机），构成「卷积 → 序列兴趣 → 交叉网络 → 交互机器」的能力扩充主线；仓路径名 `DCN_for_PyTorch` 与 v0.2.3/v0.2.5 的 DCN-M 条目直接对应，暗示该仓样例以 DCN 家族为示范对象。
- **多 GPU 工程**：v0.2.6 的 "multi-gpus running(example)" 与 README/子目录示例代码关联，但原文未给出具体脚本路径。

【使用方法】
原文未给出具体的配置项或调用命令。可定位的使用入口如下：
- **安装入口**：原文 "DeepCTR-Torch first version v0.1.0 is released on [PyPi](https://pypi.org/project/deepctr-torch/)"，可从 PyPi 安装 `deepctr-torch`。
- **回调使用 example**：v0.2.3（EarlyStopping、ModelCheckpoint）与 v0.2.4（History）通过 `https://deepctr-torch.readthedocs.io/en/latest/FAQ.html#set-learning-rate-and-use-earlystopping` 给出 example。
- **多 GPU 运行 example**：v0.2.6 标注 "(example)"，但原文未给出具体命令或脚本路径。
- **版本 release notes**：每个版本号链向对应 GitHub releases 页面，可查阅每个版本的完整说明。
