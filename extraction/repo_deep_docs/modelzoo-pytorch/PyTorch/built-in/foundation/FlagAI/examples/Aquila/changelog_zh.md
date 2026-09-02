# changelog_zh

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/examples/Aquila/changelog_zh.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/examples/Aquila/changelog_zh.md

# Aquila 系列权重 changelog_zh 深度解读

---

## 【定位】

这篇文档是 FlagAI 仓库中 Aquila 系列（Aquila-7B / AquilaChat-7B / AquilaCode-*）权重文件的版本更新日志，按时间倒序记录自 2023/06/26 至 2023/07/24 共五个版本（v0.5 → v0.9）每次发布的模型清单及其权重文件的 MD5 校验值，用于追溯各版本权重的迭代轨迹与一致性核验。

---

## 【技术要点】

1. **发布节奏**：在不到一个月内（2023/06/26 – 2023/07/24）连续迭代五个版本（v0.5、v0.6、v0.7、v0.8、v0.9），平均约每 5.6 天一次更新，迭代密度较高。
2. **基座模型双线维护**：Aquila-7B 与 AquilaChat-7B 在 v0.5 → v0.8 期间持续变更权重，MD5 值每次发布都不同；在 v0.9 时其 MD5 与 v0.8 完全一致，表明 v0.9 未对该两条线再做改动。
3. **代码模型阶段性冻结**：AquilaCode-7B-NV（MD5: `91115e72a7fc7f780b410696eae6259c`）与 AquilaCode-7B-TS（MD5: `5dae2486bc5a885279be87c13872cd5c`）自 v0.5 起一直保持到 v0.8 MD5 不变；v0.9 进一步以「暂时不会有更新计划」明确标记其暂停维护。
4. **代码模型产品线扩展（v0.9 关键变更）**：v0.9 首次开源 `AquilaCode-multi`（MD5: `07cfce9440a0fa1ac2768b39d2cf4286`）与 `AquilaCode-py`（MD5: `3faa85fc03d8fda70a73064f48d02d85`），新增「多语言代码」与「Python 专用」两条新权重线。
5. **权重一致性核验**：每个发布条目都附带 MD5 校验码，用于用户校验下载到的权重文件与官方版本是否一致，是该日志最核心的可审计技术机制。
6. **命名约定**：`<基座名>-<参数规模>B[-<变体后缀>]`，其中 `NV` / `TS` / `multi` / `py` 为代码模型的功能变体标识。

---

## 【关键机制与数据】

本文档的「机制」即权重发布的工程流程，而非模型推理机制。可识别的数据流与机制如下：

- **原文**：MD5 哈希是本次 changelog 唯一承载的"数据"，作为版本指纹贯穿全文。具体演进：
  - `Aquila-7B` MD5 演进：`13d39993743e66081640c6245da3db48` (v0.5) → `395d01d9de3437e09aefd7d337a21aca` (v0.6) → `63819234d772435ed1b0b95a193c3d04` (v0.7) → `18eac56434db0198494b22b321633785` (v0.8) → 同 v0.8 (v0.9)
  - `AquilaChat-7B` MD5 演进：`d927752ebc543b2e6ae37217403814ef` (v0.5) → `f39e3eea73fddcce7845947f56a7717d` (v0.6) → `650924d045ba7c715c80f5be485dfe2e` (v0.7) → `465683009c8b536ef4cca85febb0227c` (v0.8) → 同 v0.8 (v0.9)
- **原文**：Aquila-7B 与 AquilaChat-7B 的 MD5 在 v0.5→v0.8 的四次变更说明每次发布都有权重层面的更新（可能是再训练、增量更新或重组发布）。
- **原文**：AquilaCode-7B-NV 与 AquilaCode-7B-TS 自 v0.5 起 MD5 完全未变（连续 4 个版本），说明该两条代码模型线在 2023/06/26 – 2023/07/24 期间保持冻结；v0.9 又以「暂时不会有更新计划」明确宣告其短期内不会再发新版。
- **原文**：Aquila-7B 与 AquilaChat-7B 在 v0.9 "权重无更新"，意味着 v0.9 仅作为代码模型产品线的发布载体，而非基座模型迭代。
- **性能数据**：原文未涉及任何推理速度、benchmark、训练 loss、参数量、tokenizer 配置等性能/技术指标。

---

## 【表格解读】

原文无表格。

为便于对照解读，将原文中分散在各版本条目下的 MD5 信息合并为下表（数据**全部来自原文**，仅做汇总与对齐，MD5 字符串逐字保留，未做任何修改）：

| 版本 | 发布日期 | Aquila-7B MD5 | AquilaChat-7B MD5 | AquilaCode-7B-NV MD5 | AquilaCode-7B-TS MD5 | AquilaCode-multi MD5 | AquilaCode-py MD5 |
|---|---|---|---|---|---|---|---|
| v0.9 | 2023/07/24 | 18eac56434db0198494b22b321633785 | 465683009c8b536ef4cca85febb0227c | — | — | 07cfce9440a0fa1ac2768b39d2cf4286 | 3faa85fc03d8fda70a73064f48d02d85 |
| v0.8 | 2023/07/13 | 18eac56434db0198494b22b321633785 | 465683009c8b536ef4cca85febb0227c | 91115e72a7fc7f780b410696eae6259c | 5dae2486bc5a885279be87c13872cd5c | — | — |
| v0.7 | 2023/07/07 | 63819234d772435ed1b0b95a193c3d04 | 650924d045ba7c715c80f5be485dfe2e | 91115e72a7fc7f780b410696eae6259c | 5dae2486bc5a885279be87c13872cd5c | — | — |
| v0.6 | 2023/06/27 | 395d01d9de3437e09aefd7d337a21aca | f39e3eea73fddcce7845947f56a7717d | 91115e72a7fc7f780b410696eae6259c | 5dae2486bc5a885279be87c13872cd5c | — | — |
| v0.5 | 2023/06/26 | 13d39993743e66081640c6245da3db48 | d927752ebc543b2e6ae37217403814ef | 91115e72a7fc7f780b410696eae6259c | 5dae2486bc5a885279be87c13872cd5c | — | — |

**逐行解读**：
- **v0.5（2023/06/26）**：首个被本 changelog 收录的版本。基座模型 Aquila-7B、AquilaChat-7B 与代码模型 AquilaCode-7B-NV、AquilaCode-7B-TS 四条权重线齐发。
- **v0.6（2023/06/27）**：距 v0.5 仅 1 天，属于最频繁更新；两个基座模型 MD5 均发生变更，但两条代码模型线 MD5 完全保持不变。
- **v0.7（2023/07/07）**：相比 v0.6 间隔约 10 天，两个基座模型 MD5 再次变更；代码模型线仍冻结。
- **v0.8（2023/07/13）**：两个基座模型 MD5 又一次变更（已变为与 v0.9 相同的终值）；代码模型线依旧冻结（最后一个带 NV/TS MD5 的版本）。
- **v0.9（2023/07/24）**：基座模型权重相对 v0.8 "无更新"（MD5 完全一致）；同时宣布两条旧代码模型线（NV/TS）"暂时不会有更新计划"；首次引入两个新代码模型线 `AquilaCode-multi` 与 `AquilaCode-py`，完成代码模型产品矩阵的扩展。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据 changelog 体现出的产品矩阵关系，可梳理出以下内部关联（无内部链接，仅基于原文行文推断）：

- **基座 ↔ 对话**：Aquila-7B 为基座（base），AquilaChat-7B 为其对话微调版本。两者在 changelog 中始终成对出现，MD5 演进也呈现同步节奏（每次版本变更两者同时改），暗示两者在同一次训练/对齐流程中产出。
- **基座 ↔ 代码**：AquilaCode-7B-* 家族从 Aquila-7B 基座派生（命名上沿用 7B 规格），按功能进一步分化：
  - `AquilaCode-7B-NV`（v0.5 – v0.8）→ 冻结 → v0.9 宣告暂停维护
  - `AquilaCode-7B-TS`（v0.5 – v0.8）→ 冻结 → v0.9 宣告暂停维护
  - `AquilaCode-multi`（v0.9 首次出现，多语言代码场景）
  - `AquilaCode-py`（v0.9 首次出现，Python 专项代码场景）
- **版本主线 ↔ 旁支**：v0.5–v0.8 是基座模型与 NV/TS 两条旧代码线的并轨迭代；v0.9 是产品矩阵分叉点——基座线停止迭代、NV/TS 转入暂停、新代码线 multi/py 上线。
- **与本仓库其他模块的关系**（基于路径 `PyTorch/built-in/foundation/FlagAI/examples/Aquila/` 推断）：该 changelog 隶属于 FlagAI 框架下 Aquila 的 example 目录，对应的训练/推理脚本、配置文件应同目录存放；但原文档未给出任何脚本或配置文件名作为内链，因此不存在可枚举的内部链接。

---

## 【使用方法】

原文未涉及。

该文档作为 changelog 仅承担"版本说明 + MD5 校验"功能，原文中未出现任何启动命令、配置文件路径、推理脚本调用方式、部署环境要求等使用方法信息。如需启用具体版本的 Aquila 模型，应参考同目录下其他文件（如 README、推理脚本等），本 changelog 自身不提供使用入口。
