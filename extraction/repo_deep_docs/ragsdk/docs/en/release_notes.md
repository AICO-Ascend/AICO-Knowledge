# Version Mapping

> 仓 `ragsdk` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ragsdk/docs/en/release_notes.md

# RAG SDK 26.0.0 Release Notes 深度解读

---

## 【定位】

本文档为昇腾 RAG SDK 26.0.0 的发布说明（Release Notes / Version Mapping），核心任务是明确该版本的版本归属、兼容的上下游软件版本矩阵、新增能力以及升级注意事项，为运维与开发人员提供版本升级决策依据。

---

## 【技术要点】

1. **版本归属与产品形态**：本文档描述的是 RAG SDK 26.0.0 **Release Version**（正式版本），产品名为 "RAG SDK"。
2. **版本兼容性矩阵**：以 RAG SDK 26.0.0 为基线，向前兼容 6 路 MindSDK 版本、5 路 CANN 版本以及 5 路 Ascend HDK 版本（详见下方表格逐字还原）。
3. **强约束前置条件**：升级到 26.0.0 后，使用 ascendfaiss 进行检索前，必须先安装 Index SDK 并生成算子（原文："you need to install Index SDK and generate operators before using ascendfaiss for retrieval"）。
4. **新增能力（New Feature）**：bge 系列 embedding 与 reranker 的加速，针对 `bge-reranker-v2-m3` 和 `bge-m3` 模型进行性能优化。
5. **适配硬件清单**：新增功能仅在 **Atlas 300I Duo Inference Card** 与 **Atlas 800I A2 Inference Server** 两款产品型号上支持。
6. **接口变更与缺陷**：服务接口无变更（No interface changes）、无关键功能变更、无已解决问题、无已知问题、无安全漏洞修复、无升级对系统的影响。

---

## 【关键机制与数据】

- **软件升级兼容语义（原文）**：
  > "Software version compatibility means that when the product software version is upgraded, other related software does not need to be upgraded or patched at the same time, and existing functions remain supported."

  即 RAG SDK 26.0.0 升级时，MindSDK/CANN/Ascend HDK 等相关软件不需要同步升级或打补丁，已有功能保持可用。

- **新特性加速对象（原文）**：
  - 模型：`bge-reranker-v2-m3`、`bge-m3`；
  - 加速范畴："bge series embedding and reranker acceleration. Performance optimization for the bge-reranker-v2-m3 and bge-m3 models."；
  - 硬件载体：Atlas 300I Duo Inference Card、Atlas 800I A2 Inference Server。

- **性能数据**：原文中**未给出**任何量化性能指标（如 QPS、Recall@K、加速比、latency 等），仅在描述层面提到 "Performance optimization"。

- **数据流 / 工作原理**：原文档为版本元数据类 changelog，**未涉及**具体的内部数据流、推理流水线或算子调度细节。

---

## 【表格解读】

### 表 A：Product Version（原文逐字还原）

| Product | RAG SDK |
| --- | --- |
| Product Version | 26.0.0 |
| Version Type | Release Version |

**解读**：明确本版本号 **26.0.0**，版本类型为 **正式版（Release Version）**，区别于 RC/Beta/补丁版本。

---

### 表 B：Related Product Versions（原文逐字还原）

| Product | Version |
| --- | --- |
| Ascend HDK | 26.0.RC1 |
| CANN | 9.0.0 |

**解读**：与 RAG SDK 26.0.0 同时期发布的相关产品版本。Ascend HDK 处于 RC 阶段，CANN 为 9.0.0 正式版，这是文档"基线对齐"的版本组合。

---

### 表 C：Table 1 Software Version Compatibility Description（原文逐字还原）

| MindSDK Software Version | MindSDK Version to Upgrade | CANN Version Compatibility | Ascend HDK Version Compatibility |
|--|--|--|--|
| RAG SDK 26.0.0 | <li>MindSDK 6.0.RC3 and patch versions</li><li>MindSDK 6.0.0 and patch versions</li><li>MindSDK 7.0.RC1 and patch versions</li><li>MindSDK 7.1.RC1 and patch versions</li><li>MindSDK 7.2.RC1 and patch versions</li><li>MindSDK 7.3.0 and patch versions</li> | <li>CANN 8.1.RC1 and patch versions</li><li>CANN 8.2.RC1 and patch versions</li><li>CANN 8.3.RC1 and patch versions</li><li>CANN 8.5.0 and patch versions</li><li>CANN 9.0.0 and patch versions</li> | <li>Ascend HDK 25.0.RC1 and patch versions</li><li>Ascend HDK 25.2.0 and patch versions</li><li>Ascend HDK 25.3.RC1 and patch versions</li><li>Ascend HDK 25.5.0 and patch versions</li><li>Ascend HDK 26.0.RC1 and patch versions</li> |

**逐行解读**：

- **左列"MindSDK Software Version"**：本表基线软件是 RAG SDK 26.0.0。
- **第 2 列（升级目标 MindSDK）**：共 6 个可兼容的 MindSDK 版本族——6.0.RC3、6.0.0、7.0.RC1、7.1.RC1、7.2.RC1、7.3.0，每个版本均"and patch versions"（含其后补丁）。覆盖了 MindSDK 从 6.0 到 7.3 的完整跨大版本兼容矩阵。
- **第 3 列（CANN 兼容）**：5 个 CANN 版本——8.1.RC1、8.2.RC1、8.3.RC1、8.5.0、9.0.0，含 RC 与正式版混合，说明 RAG SDK 26.0.0 对 CANN 8.x 老链路与 9.0.0 新链路均保持兼容。
- **第 4 列（Ascend HDK 兼容）**：5 个 HDK 版本——25.0.RC1、25.2.0、25.3.RC1、25.5.0、26.0.RC1，跨度从 25.0 到 26.0.RC1，体现了"向前多版本兼容"的设计意图。
- **配套 NOTE 含义**：升级 RAG SDK 时 MindSDK/CANN/HDK **无需同步升级或打补丁**，旧功能保持可用——这意味着该列出的每一行组合都已通过兼容性验证。

---

### 表 D：New Features（原文逐字还原）

| Feature | Description | Supported Product Model |
|--|------------------------------------|--|
| RAG SDK | bge series embedding and reranker acceleration. Performance optimization for the bge-reranker-v2-m3 and bge-m3 models. | Atlas 300I Duo Inference Card<br>Atlas 800I A2 Inference Server |

**解读**：本版本唯一新增特性。加速对象为 **bge 系列**的 **embedding** 与 **reranker** 两类模型，具体点名 `bge-reranker-v2-m3` 与 `bge-m3`。承载硬件为 Atlas 300I Duo（推理卡）与 Atlas 800I A2（推理服务器）两款昇腾产品。

---

### 表 E：26.0.0 Documentation（原文逐字还原）

| Document | Description | Release Notes |
|--|--|--|
| *RAG SDK 26.0.0 User Guide* | Mainly includes RAG SDK installation and deployment process, application development process, API interface descriptions, and other common operations. | For changes, see *[RAG SDK 26.0.0 User Guide](./introduction.md)*. |

**解读**：配套用户手册主要覆盖安装部署、应用开发、API 接口描述等常用操作。变更说明通过内部链接 `./introduction.md` 关联到 RAG SDK 26.0.0 User Guide（即 introduction.md）。

---

## 【公式解读】

**原文无公式。**

本 release notes 文档为版本元数据说明性质，不涉及任何算法推导、性能模型或量化公式表达。

---

## 【关联】

- **./introduction.md**（内部链接，文中末尾"26.0.0 Documentation"小节中引用）：
  → 对应《RAG SDK 26.0.0 User Guide》入口页。文档描述该手册覆盖：RAG SDK 安装与部署流程、应用开发流程、API 接口描述及其他常用操作；变更内容须跳转该 introduction.md 查看——是本 release notes 唯一一条内部链接。

- **与 Ascend HDK 的关系**：依赖并兼容 Ascend HDK 25.0.RC1 ~ 26.0.RC1 共 5 个版本；当前关联基线为 26.0.RC1（见表 B、表 C）。

- **与 CANN 的关系**：兼容 CANN 8.1.RC1 ~ 9.0.0 共 5 个版本；当前关联基线为 CANN 9.0.0。

- **与 MindSDK 的关系**：兼容 MindSDK 6.0.RC3 ~ 7.3.0 共 6 个版本族，是本次升级"无需同步升 MindSDK"的关键依据。

- **与 Index SDK / ascendfaiss 的关系**：存在**强前置依赖**。原文指出，升级到 RAG SDK 26.0.0 后，使用 ascendfaiss 做检索必须先安装 Index SDK 并生成算子——这是文档中唯一带"必须"语义的操作约束。

- **与硬件产品的关系**：本次新特性（bge 加速）仅在 Atlas 300I Duo Inference Card 与 Atlas 800I A2 Inference Server 上声明支持；其他昇腾型号不在该特性支持列表内。

- **与 bge 模型生态的关系**：bge（BAAI General Embedding）系列下的 `bge-m3`（多语/多功能 embedding）与 `bge-reranker-v2-m3`（重排序器）是本次性能优化的明确目标模型。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令。文档仅在 **Version Compatibility** 章节中给出**一条使用前置条件**（非完整启用步骤）：

- **原文（关于 ascendfaiss）**：
  > "After upgrading to this version, you need to install Index SDK and generate operators before using ascendfaiss for retrieval."

  即：升级到 RAG SDK 26.0.0 后，若使用 ascendfaiss 做检索，需先完成 Index SDK 安装并完成算子生成。

除此之外，启用 bge 系列加速的具体 API 调用、配置项、环境变量、算子生成命令等，原文均未提供，需跳转至《RAG SDK 26.0.0 User Guide》（`./introduction.md`）查看完整启用与开发流程。
