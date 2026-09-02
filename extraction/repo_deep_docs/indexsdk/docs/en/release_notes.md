# Version Mapping<a name="ZH-CN_TOPIC_0000002524441743"></a>

> 仓 `indexsdk` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/indexsdk/docs/en/release_notes.md

# Index SDK 26.0.0 Release Notes 深度解读

---

## 【定位】

本文档是 **Index SDK 26.0.0 (Release Version) 的发布说明 (Release Notes)**,集中描述该版本的版本配套关系、版本兼容性、新增特性、接口变更、升级影响以及配套文档入口,服务于基于华为昇腾平台 Index SDK 进行向量特征检索引擎开发的用户,帮助其评估升级可行性与功能收益。

---

## 【技术要点】

1. **版本配套**:Index SDK 26.0.0 配套 Ascend HDK 26.0.RC1、CANN 9.0.0;病毒扫描通过;升级后需**重新编译基于 Index SDK 开发的应用,并重新生成相关算子**。

2. **向下兼容性范围**:兼容 MindSDK 6.0.RC3/6.0.0/7.0.RC1/7.1.RC1/7.2.RC1/7.3.0,CANN 8.1.RC1/8.2.RC1/8.3.RC1/8.5.0/9.0.0,Ascend HDK 25.0.RC1/25.2.0/25.3.RC1/25.5.0/26.0.RC1 及其 patch 版本;按原文档说明,兼容性意味着升级本产品时其他相关软件**无需同步升级或打补丁**,既有功能仍受支持。

3. **ILFlat 标准态性能优化**:在基库 500 万条 (5,000,000)、维度 256 的条件下,使用 GetFeature 随机检索 40,000 条数据耗时降低至 **25 ms 以内**。

4. **时空库异构内存扩展**:时空库新增支持 **TSInt8FlatCos** 类型,在 1024 维度下,可于异构内存场景为该类型**添加额外属性 (additional attributes)**,检索可按额外属性正确过滤。

5. **服务接口变更**:Index SDK **未涉及接口变更** (No interface changes are involved)。

6. **其他变更**:关键特性变更、已解决问题、已知问题、升级期间与升级后对系统的影响、修复漏洞 — 均**无** (None / No known issues)。

7. **支持的产品型号**:Atlas 300I Pro Inference Card、Atlas 300V Video Analysis Card、Atlas 300V Pro Video Analysis Card、Atlas 300I Duo Inference Card、Atlas 200I SoC A1 Core Board、Atlas 300I Inference Card (Model 3000)、Atlas 300I Inference Card (Model 3010)、Atlas 800I A2 Inference Server。

---

## 【关键机制与数据】

- **ILFlat 性能优化(原文)**:针对 ILFlat 标准态,基库规模 5,000,000 条、维度 256,GetFeature 随机检索 40,000 条耗时降至 ≤ 25 ms。该数据揭示的机制是 ILFlat 索引在标准态下的随机访问吞吐被进一步压低,可作为高并发检索场景的延迟基线。

- **时空库异构内存机制(原文)**:时空库的 TSInt8FlatCos 类型在 1024 维度下,支持在异构内存场景添加额外属性;检索时可正确按额外属性过滤。这意味着属性过滤与向量检索的耦合能力在该类型上得到补齐,但其它类型是否同步支持原文档未明确说明。

- **版本兼容语义(原文 NOTE)**:兼容性意味着产品软件版本升级时,其他相关软件无需同步升级或打补丁,既有功能仍受支持。

- **升级硬约束(原文)**:升级到本版本后,基于 Index SDK 开发的应用程序需**重新编译**,相关算子需**重新生成**。

- **病毒扫描(原文)**:Virus scan passed。

---

## 【表格解读】

### 表 1 — Software Version Compatibility Description (原文逐字还原)

| MindSDK Software Version | MindSDK Version to Upgrade | CANN Version Compatibility | Ascend HDK Version Compatibility |
|---|---|---|---|
| Index SDK 26.0.0 | ● MindSDK 6.0.RC3 and patch versions<br>● MindSDK 6.0.0 and patch versions<br>● MindSDK 7.0.RC1 and patch versions<br>● MindSDK 7.1.RC1 and patch versions<br>● MindSDK 7.2.RC1 and patch versions<br>● MindSDK 7.3.0 and patch versions | ● CANN 8.1.RC1 and patch versions<br>● CANN 8.2.RC1 and patch versions<br>● CANN 8.3.RC1 and patch versions<br>● CANN 8.5.0 and patch versions<br>● CANN 9.0.0 and patch versions | ● Ascend HDK 25.0.RC1 and patch versions<br>● Ascend HDK 25.2.0 and patch versions<br>● Ascend HDK 25.3.RC1 and patch versions<br>● Ascend HDK 25.5.0 and patch versions<br>● Ascend HDK 26.0.RC1 and patch versions |

**逐行解读**:
- **行 (Index SDK 26.0.0)**:仅含一行,描述当本产品升级至 26.0.0 时,可同时共存、不需同步升级的 MindSDK / CANN / Ascend HDK 版本范围。
- **MindSDK 列**:列出 6 个起点版本 (6.0.RC3、6.0.0、7.0.RC1、7.1.RC1、7.2.RC1、7.3.0) 及其 patch,覆盖 6.0.x、7.x 两条主线 RC/GA。
- **CANN 列**:列出 5 个起点版本 (8.1.RC1、8.2.RC1、8.3.RC1、8.5.0、9.0.0) 及其 patch,跨度从 8.1 到 9.0。
- **Ascend HDK 列**:列出 5 个起点版本 (25.0.RC1、25.2.0、25.3.RC1、25.5.0、26.0.RC1) 及其 patch,跨度从 25.0 到 26.0。

### 配套产品版本表 (原文逐字还原)

| Product | Version |
|---|---|
| Ascend HDK | 26.0.RC1 |
| CANN | 9.0.0 |

**逐行解读**:Ascend HDK 26.0.RC1 与 CANN 9.0.0 是 Index SDK 26.0.0 在本发布中的直接依赖基线。

### 新特性表 (原文逐字还原)

| Feature | Description | Supported Product Model |
|---|---|---|
| Index SDK | ● ILFlat standard-state performance optimization: For a base library with 5 million entries and 256 dimensions, the time required to randomly retrieve 40,000 entries from the base library with GetFeature is reduced to within 25 ms.<br>● Heterogeneous memory support for additional attributes in the spatiotemporal library: The feature supports TSInt8FlatCos in the spatiotemporal library. At 1024 dimensions, you can add additional attributes in heterogeneous memory scenarios, and retrieval can correctly filter by additional attributes. | Atlas 300I Pro Inference Card<br>Atlas 300V Video Analysis Card<br>Atlas 300V Pro Video Analysis Card<br>Atlas 300I Duo Inference Card<br>Atlas 200I SoC A1 Core Board<br>Atlas 300I Inference Card (Model 3000)<br>Atlas 300I Inference Card (Model 3010)<br>Atlas 800I A2 Inference Server |

**逐行解读**:
- **Feature 列**:仅一行,Feature = Index SDK。
- **Description 列**:包含 2 个并列的新增项。**第 1 项**给出明确数字三元组 — 基库 5,000,000 条 / 维度 256 / GetFeature 随机检索 40,000 条 / 耗时 ≤ 25 ms;**第 2 项**限定到 TSInt8FlatCos 类型、1024 维度、异构内存、可添加额外属性且可按属性正确过滤。
- **Supported Product Model 列**:列出 8 个昇腾产品型号,涵盖推理卡、视频分析卡、SoC 核心板、推理服务器四类。

### 文档入口表 (原文逐字还原)

| Document | Description | Release Notes |
|---|---|---|
| *Index SDK 26.0.0 User Guide* | Mainly includes the usage process of Index SDK, algorithm introduction, operator generation instructions, API interface descriptions, and other common operations. | For changes, see *Index SDK 26.0.0 User Guide* (link to introduction.md#software-architecture). |

**逐行解读**:本版本提供 1 份配套用户指南,内容覆盖使用流程、算法介绍、算子生成说明、API 接口描述等;变更详情需跳转至 introduction.md#software-architecture 查看。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **配套文档 (原文 §26.0.0 Documentation)**:本文档本身是 release notes,详细使用流程、算法介绍、算子生成、API 接口描述均在《Index SDK 26.0.0 User Guide》(introduction.md#software-architecture) 中给出;两份文档需配合使用。

- **上下游依赖 (原文 §Related Product Versions / §Version Compatibility)**:Index SDK 26.0.0 是 MindSDK 产品线中的一员,其运行依赖 Ascend HDK 与 CANN 提供的底层算力与运行时;MindSDK、CANN、Ascend HDK 三者在表 1 中以并列形式给出兼容矩阵,体现"产品–驱动–芯片栈"的三层耦合。

- **新特性涉及的能力扩展 (原文 §New Features)**:ILFlat 标准态性能优化作用于 Index SDK 内部索引 (ILFlat) 的随机检索通路;时空库的 TSInt8FlatCos + 异构内存 + 额外属性过滤,作用于时空索引 (spatiotemporal library) 的属性筛选通路 — 二者对应 Index SDK 的两个内部能力域。

- **支持的昇腾硬件族 (原文 Supported Product Model 列)**:覆盖 Atlas 300I / 300V / 200I / 800I 等多个产品线,说明本次新特性并非限定单一型号,而是在多款昇腾硬件上同步可用。

> 说明:文末内部链接字段为「(无)」,原文也未给出额外的交叉引用链接,故以上关联完全基于原文中明确出现的模块/产品/版本名。

---

## 【使用方法】

- **升级操作 (原文 §Version Compatibility)**:
  - 将 Index SDK 升级至 26.0.0 后,基于旧版本 Index SDK 开发的应用必须**重新编译**。
  - 相关算子必须**重新生成**。
  - 在表 1 列出的 MindSDK / CANN / Ascend HDK 兼容版本范围内,**无需同步升级或打补丁**即可保持既有功能可用。

- **特性启用方式 (原文 §New Features)**:原文仅说明 ILFlat 标准态性能优化与 TSInt8FlatCos 在 1024 维度下异构内存附加属性的能力,**未给出具体的 API 调用、命令行、配置项或参数开关**。具体使用方法需参考《Index SDK 26.0.0 User Guide》(introduction.md#software-architecture)。

- **配置项 / 命令**:原文未涉及。
