# Ascend MindStudio Training Tools 精度对照

> 仓 `mindspeed` · 路径 `docs/zh/features/npu_datadump.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/npu_datadump.md

# Ascend MindStudio Training Tools 精度对照 — 深度解读

## 【定位】
本文档介绍 MindSpeed 集成的「精度对照」功能：通过简化 msprobe 工具的使用，为大模型在跨平台（GPU→NPU）训练场景下提供一键式整网精度数据 dump 与比对能力，解决跨平台精度对齐时手动改代码、调 config 的繁重工作。

## 【技术要点】

1. **核心能力来源**：底层依赖 msprobe 工具，配合 Ascend 芯片的「确定性计算」机制，完成整网训练数据的采集与精度比对。
2. **MindSpeed 集成定位**：将 msprobe 进行了"集成与简化"，对用户屏蔽了"手动修改代码 + 调节 config"的步骤，用户只需通过参数启用即可。
3. **启用方式**：在训练脚本中加入 `--npu-datadump` 即可开启本功能。
4. **默认采集范围**：默认仅采集 `RANK0`（只采集 0 号卡）、`STEP0`（只采集第 0 步）的 `statistics` 精度（统计量级精度数据类型）。
5. **配置文件双文件机制**：
   - `mindspeed/functional/npu_datadump/config.json` —— 控制整网 dump 的各选项；
   - `mindspeed/functional/npu_datadump/compare.json` —— 控制利用 msprobe 进行 dump 数据精度对照的策略。
6. **已知约束/默认行为**：
   - 暂不支持 Lite 后端；
   - dump 数据默认保存在 Megatron-LM 目录下；
   - 使用前需先修改 config.json。

## 【关键机制与数据】

工作原理（按原文推断的链路）：

- **原文**：msprobe 在使用上"需要手动修改代码，并设置调节 config"——这是其在 MindSpeed 中使能不便的根因。
- **原文**：MindSpeed 的解决思路是"集成并简化了 msprobe 工具的使用，允许用户通过设置参数，快速进行整网的精度数据 dump 及比对"。
- **原文**：默认的 dump 维度为"采集 RANK0（仅采集 0 号卡）、STEP0（仅采集第 0 步）下的 statistics 精度"，即统计量级精度数据类型——这表明精度对照的对象并非 tensor 原始 bit 级数据，而是统计量级（如均值、方差等统计量），目的是发现量级上的偏差。
- **原文**：dump 数据"默认保存在 Megatron-LM 目录下"——输出路径与 Megatron-LM 工程结构绑定。

性能/效果数据：
- 原文未提供具体的性能数字、采集耗时、内存占用等量化数据；仅定性表述"可快速确认整网运行过程中的精度误差"。

## 【表格解读】

**原文无表格**。文档中未出现任何参数表、性能对比表或配置项表，相关配置（默认 RANK0/STEP0/statistics）以正文文字形式给出。

## 【公式解读】

**原文无公式**。文档中未涉及任何数学公式或伪代码。

## 【关联】

1. **上游/底层依赖**：msprobe 工具（Ascend MindStudio Training Tools 系列工具之一），原文给出官方使用教程链接 `https://gitcode.com/Ascend/msprobe/blob/master/docs/zh/user_guide/dump/config_json_introduct.md`，作为 config 设置细节的参考来源。
2. **被集成的对象**：msprobe 在原始形态下"需要手动修改代码，并设置调节 config"——这是 MindSpeed 在本特性中需要屏蔽的复杂度来源。
3. **工程耦合点**：
   - 配置入口位于 `mindspeed/functional/npu_datadump/config.json`（dump 行为）；
   - 配置入口位于 `mindspeed/functional/npu_datadump/compare.json`（比对行为）；
   - 数据落地于 Megatron-LM 工程目录；
   - 与 Lite 后端**不兼容**（"暂不支持 Lite 后端"）。
4. **应用场景关联**：与"跨平台精度对齐（GPU→NPU）"、"特定场景复现"两类使用场景强绑定，依赖 Ascend 的确定性计算前提。
5. **内部链接**：原文未提供仓库内其他文档的内部链接。

## 【使用方法】

按原文整理，启用本功能的步骤为：

1. **修改配置文件**（使用前必做）：
   - 编辑 `mindspeed/functional/npu_datadump/config.json` —— 调整整网 dump 的各选项；
   - 编辑 `mindspeed/functional/npu_datadump/compare.json` —— 调整 msprobe 进行 dump 数据精度对照的策略。
   - config 设置更多细节请参考 msprobe 官方使用教程（原文给出链接）。

2. **启用功能**：在训练启动脚本中加入参数 `--npu-datadump`。

3. **默认行为**（如不修改 config）：仅采集 `RANK0`（0 号卡）、`STEP0`（第 0 步）的 `statistics`（统计量级精度）数据。

4. **输出位置**：dump 数据默认保存在 Megatron-LM 目录下。

5. **后端限制**：暂不支持 Lite 后端（原文未涉及 Lite 模式的启用方式或替代方案）。
