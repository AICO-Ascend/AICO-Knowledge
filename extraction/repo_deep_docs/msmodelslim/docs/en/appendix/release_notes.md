# Release Notes

> 仓 `msmodelslim` · 路径 `docs/en/appendix/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodelslim/docs/en/appendix/release_notes.md

# 深度解读：msModelSlim Release Notes

---

## 【定位】

本文档是 **msModelSlim** 模型量化压缩工具的版本发布说明（changelog），系统性记录了三个版本（26.0.0.alpha02、26.0.0.alpha01、8.3.0）的版本映射、配套依赖兼容性、wheel 包下载信息以及各版本特性更新，用于帮助开发者确认版本适配关系并了解新增/改进能力。

---

## 【技术要点】

1. **三层版本体系**：文档覆盖一个 Official version（8.3.0）和两个 Internal test version（26.0.0.alpha01、26.0.0.alpha02），形成「正式版 + 内测版」双轨发布模式。
2. **配套依赖矩阵**：所有版本均要求 Python 3.10 和 3.11；PyTorch、torch_npu、Transformers 版本均「Depends on the specific model」（依赖具体模型）；仅 8.3.0 显式要求 CANN ≥ 8.2.RC1，两个 alpha 版本则「No specific version requirement」。
3. **插件化 model_adapter 雏形**：26.0.0.alpha02 引入「Supports custom `practice` directories through an entry point」，为基于插件机制的 `model_adapter` 能力奠定基础。
4. **基于精度反馈的自动调优**：26.0.0.alpha01 与 26.0.0.alpha02 均涉及「automatic tuning」能力，alpha01 明确定义为基于 **quantization-accuracy feedback** 自动搜索最优量化配置。
5. **多卡分布式逐层量化**：26.0.0.alpha01 的「Quick quantization」支持 multi-card quantization 与 distributed layer-by-layer quantization，用于提升大模型量化效率。
6. **多场景量化方案**：覆盖 W4A8、W8A8、W8A8C8 三种主流 weight/activation 量化组合（其中 C8 指 8-bit 校准/缓存量化）。
7. **硬件门槛**：DeepSeek-V3.2 系列（W8A8 与 W4A8）均需「single card with **64 GB of accelerator memory** and **100 GB of system memory**」，即单卡即可运行大模型量化。

---

## 【关键机制与数据】

**原文工作机制（按版本演进）：**

- **8.3.0（Official）**：作为基线版本，提供 W8A8C8 / W8A8 / W4A8C8 量化能力，覆盖 DeepSeek-V3.2-Exp、DeepSeek-V3.1、Qwen3-32B、Qwen3-Next-80B、DeepSeek-R1-0528 等模型。
- **26.0.0.alpha01**：在 8.3.0 基础上引入**精度反馈自动调优**、**多模态模型自管理量化与集成**、**多卡/分布式逐层量化**；首次披露 DeepSeek-V3.2 在「**64 GB 加速器内存 + 100 GB 系统内存**」单卡环境下运行 W8A8 / W4A8 量化；新增 Qwen3-VL-32B-Instruct、Qwen3-VL-235B-A22B 的 W8A8 支持。
- **26.0.0.alpha02**：在前一 alpha 基础上开放 **practice 目录 entry point 注册机制**，为插件化 model_adapter 铺路；自动调优能力继续增强；新增 Qwen3-Coder-480B（W4A8）、Qwen3.5 MoE（W8A8）、GLM-4.7（W8A8）、GLM-5（W4A8）、Qwen2.5-Omni-7B 与 Qwen3-Omni-30B-A3B（W8A8）等多模态/MoE 模型支持。

**原文性能/数据要点（逐条复述）：**
- 26.0.0.alpha02 / 26.0.0.alpha01：Python 3.10 和 3.11。
- 8.3.0：CANN 8.2.RC1 or later，Python 3.10 和 3.11。
- DeepSeek-V3.2（W8A8）：single card，64 GB accelerator memory + 100 GB system memory。
- DeepSeek-V3.2-Exp（W4A8）：single card，64 GB accelerator memory + 100 GB system memory。

**wheel 包校验和（原文）：**
- `msmodelslim-26.0.0a2-py3-none-any.whl` → SHA256: `4711edb30c4354fcb99fb69a2e0351561b013bb1298d6f54a0ee409bf979a264`
- `msmodelslim-26.0.0a1-py3-none-any.whl` → SHA256: `60383c42bf103cf2f78304b3b974e2dac0190f0f20706a5ef347e55855048f42`

---

## 【表格解读】

### 表 1：Product Versions（产品版本）

| Product       | Version          | Version Type           |
|---------------|------------------|------------------------|
| msModelSlim   | 26.0.0.alpha02   | Internal test version  |
| msModelSlim   | 26.0.0.alpha01   | Internal test version  |
| msModelSlim   | 8.3.0            | Official version       |

**逐行解读：**
- 第 1 行：26.0.0.alpha02 为最新内测版（迭代最快的特性验证通道）。
- 第 2 行：26.0.0.alpha01 为前一内测版（首次引入自动调优反馈、多卡量化等大特性）。
- 第 3 行：8.3.0 为正式版本（基线稳定版，要求 CANN ≥ 8.2.RC1，是正式生产推荐版本）。

---

### 表 2：Related Product Versions（相关产品版本配套矩阵）

| msModelSlim Version | CANN Version                  | PyTorch Version                                                  | torch_npu Version                                                  | Python Version     | Transformers Version                                                                                          |
|---------------------|-------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------|--------------------|--------------------------------------------------------------------------------------------------------------|
| 26.0.0.alpha02      | No specific version requirement| Depends on the specific model. See the corresponding model documentation. | Depends on the specific model. See the corresponding model documentation. | Python 3.10 and 3.11 | Depends on the specific model. See the corresponding case description in the [example](https://gitcode.com/Ascend/msmodelslim/tree/master/example) directory. |
| 26.0.0.alpha01      | No specific version requirement| Depends on the specific model. See the corresponding model documentation. | Depends on the specific model. See the corresponding model documentation. | Python 3.10 and 3.11 | Depends on the specific model. See the corresponding case description in the [example](https://gitcode.com/Ascend/msmodelslim/tree/master/example) directory. |
| 8.3.0               | 8.2.RC1 or later              | Depends on the specific model. See the corresponding model documentation. | Depends on the specific model. See the corresponding model documentation. | Python 3.10 and 3.11 | Depends on the specific model. See the corresponding case description in the [example](https://gitcode.com/Ascend/msmodelslim/tree/master/example) directory. |

**逐行解读：**
- 第 1 行（26.0.0.alpha02）：CANN 无强制版本（内测期放宽依赖），Python 仍锁定 3.10/3.11，PyTorch/torch_npu/Transformers 三项均随模型变化，需查阅对应模型文档与 example 目录案例。
- 第 2 行（26.0.0.alpha01）：同 alpha02 一致的宽松依赖策略，Python 限制保持不变。
- 第 3 行（8.3.0）：唯一对 **CANN 版本有硬性要求** 的版本——必须 8.2.RC1 或更高；其余三项同样依赖具体模型，需查阅 example 目录案例。

---

### 表 3：Wheel Package Downloads（wheel 包下载）

| Version       | Download Link                                                                                                                                                                                              | Checksum                                                            |
|:-------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------:|
| 26.0.0-alpha.2 | [msmodelslim-26.0.0a2-py3-none-any.whl](https://gitcode.com/Ascend/msmodelslim/releases/download/tag_mindstudio_26.0.0.alpha02/msmodelslim-26.0.0a2-py3-none-any.whl)                                       | 4711edb30c4354fcb99fb69a2e0351561b013bb1298d6f54a0ee409bf979a264    |
| 26.0.0-alpha.1 | [msmodelslim-26.0.0a1-py3-none-any.whl](https://gitcode.com/Ascend/msmodelslim/releases/download/tag_MindStudio_26.0.0-alpha.1/msmodelslim-26.0.0a1-py3-none-any.whl)                                       | 60383c42bf103cf2f78304b3b974e2dac0190f0f20706a5ef347e55855048f42    |

**逐行解读：**
- 第 1 行：alpha02 的 wheel 包命名遵循 PEP 440 规范化为 `26.0.0a2`，下载 tag 为 `tag_mindstudio_26.0.0.alpha02`，提供 SHA256 校验值用于完整性验证。
- 第 2 行：alpha01 的 wheel 包名为 `26.0.0a1`，下载 tag 为 `tag_MindStudio_26.0.0-alpha.1`，校验和同样为 SHA256。
- 注意：8.3.0 正式版未在此表提供 wheel 下载链接（详见原文档「For more details」段落指引至 releases 页面）。

---

## 【公式解读】

原文无公式。

（文档为版本说明性质，仅包含版本号、量化方案命名如 W4A8/W8A8/W8A8C8、内存容量等离散参数，未给出任何数学公式或伪代码。）

---

## 【关联】

文档自身明确指向的上下游/外部资源：

- **example 目录**：在「Related Product Versions」表的 Transformers Version 列中三次引用，链接为 `https://gitcode.com/Ascend/msmodelslim/tree/master/example`，作为具体模型配套 Transformers 版本的参考案例库。
- **releases 页面**：在「Wheel Package Downloads」段落末尾指向 `https://gitcode.com/Ascend/msmodelslim/releases?presetConfig={...}`，用于获取更多历史版本的下载信息。
- **具体模型文档**：在兼容性矩阵的 PyTorch、torch_npu、Transformers 三列中均提示「See the corresponding model documentation」，表明模型级适配细节不在本 changelog 范围内，需配合各模型子文档查阅。
- **插件生态上游**：26.0.0.alpha02 的 practice 目录 entry point 机制是 **plugin-based model_adapter 能力** 的前置条件，意味着后续版本将开放第三方/自定义模型适配器接入点。
- **CANN 工具链**：8.3.0 显式约束 CANN ≥ 8.2.RC1，表明 msModelSlim 与昇腾 CANN 工具链强耦合，CANN 是其运行时底座。

---

## 【使用方法】

原文未涉及具体的命令行/API 启用方式，仅提供以下分发信息：

1. **wheel 包安装（内测版）**：通过上表给出的 gitcode 直链下载 `msmodelslim-26.0.0a2-py3-none-any.whl` 或 `msmodelslim-26.0.0a1-py3-none-any.whl`，下载后可使用标准 `pip install <wheel 文件>` 安装；安装前需比对文档给出的 SHA256 Checksum 验证完整性。
2. **正式版获取**：原文中 8.3.0 正式版的 wheel 链接未在本文档直接给出，需跳转至 `https://gitcode.com/Ascend/msmodelslim/releases` 页面查找。
3. **环境依赖**：所有版本均需 Python 3.10 或 3.11；8.3.0 额外要求 CANN 8.2.RC1 or later；具体模型的 PyTorch / torch_npu / Transformers 版本需结合 example 目录案例确认。
4. **插件注册（26.0.0.alpha02 新增）**：可通过 entry point 注册自定义 `practice` 目录，原文未给出具体的 entry point 名称或注册语法，需结合插件化 model_adapter 后续文档。

原文未涉及的项：未给出 CLI 入口、API 调用示例、`pip` 完整命令、配置文件 schema、调优参数默认值等。
