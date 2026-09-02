# Introduction<a name="ZH-CN_TOPIC_0000001668092436"></a>

> 仓 `indexsdk` · 路径 `docs/en/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/indexsdk/docs/en/introduction.md

# Index SDK Introduction 深度解读

## 【定位】

这篇文档是 Index SDK（即基于华为昇腾 NPU + Faiss 构建的 **FeatureRetrieval** 异构检索加速框架）的总览性 Overview，介绍其**产品背景、定义、价值、软件架构、使用流程、硬件/OS 支持**，旨在让用户在动手部署之前快速理解该 SDK 能做什么、怎么用、跑在什么硬件上。

---

## 【技术要点】

1. **检索库规模分层**：分为小库（**30 万 ~ 100 万**条记录，走全量检索）与大库（**数千万甚至数亿**条记录，走近似检索），并由此对应不同的算法族。
2. **支持的算法**：小库包含 **Flat、SQ（又名 SQ8，8-bit 整数量化）、INT8（又名 int8flat，特征量化暴力检索）**；大库为 **IVFSQ**（基于 IVF 的近似检索思路：先聚类，再通过聚类中心缩小检索范围，以精度换性能）。
3. **特征维度范围**：**64 ~ 512 维**（依算法而定）。
4. **底层加速**：每个算法底层都使用 **TBE 算子**在昇腾平台上加速，覆盖距离计算算子、TopK 排序算子、属性过滤掩码算子三类。
5. **附加能力**：支持**属性过滤检索**（按时间/空间属性过滤底库向量）和**多索引批量检索**（多索引拆库 + 统一接口批量检索）。
6. **单卡能力上限**：单卡单索引（底库）容量受昇腾 AI 处理器设备侧内存制约；**建议索引数不超过 10,000**，超过后内存碎片显著，`add` 操作可用容量可能低于预期。

---

## 【关键机制与数据】

- **工作机制（原文）**：FeatureRetrieval 是基于 Faiss 为昇腾 NPU 构建的异构检索加速框架，使用 **C++（Faiss 风格）+ TBE 算子**，同时支持 **Arm 和 x86_64** 平台。
- **IVFSQ 与传统倒排索引的区别（原文）**：IVF 在此处的含义是 **"先聚类，再通过聚类中心缩小检索范围"**，属于近似检索（"This method trades accuracy for performance"）。
- **属性过滤检索（原文）**：在底库向量入库时可附带时间、空间属性，检索时按指定时空条件过滤底库数据。
- **多索引批量检索（原文）**：通过多索引拆库，经统一接口一次检索多个底库。
- **API 兼容性（原文）**：上层使用原生 **Faiss C++ 接口**完成特征入库、查询、删除、训练。
- **部署/调用细节（原文）**：FeatureRetrieval 通过 AscendCL 接口部署，**`aclInit` 已在内部调用**，用户无需重复调用。
- **价值定位（原文）**：与业界标准相比，**同算力卡上全量检索优于业界标准**；**批量检索优于串行场景**。
- **表 1 模块划分（原文）**：Index SDK 自上而下分为 **API 层 → 算法逻辑层 → 算子层**，每层职责明确。

> 注：性能数据原文仅以定性描述给出（"outperforms the industry standard"），未给出具体数字。

---

## 【表格解读】

### 表 1：Index SDK 模块介绍（原文逐字还原）

| Module | Description |
| --- | --- |
| Index SDK API layer | Provides Faiss-compatible C++ interfaces. Upper-layer applications can implement feature ingestion, query, deletion, and training functions. |
| Algorithm logic layer | Implements the logical flow of retrieval algorithms. The currently supported algorithms mainly include brute-force retrieval, approximate retrieval, and attribute-filtering algorithms. |
| Operator layer | Provides acceleration operators for retrieval algorithms on the Ascend platform, including distance computation operators, TopK sorting operators, and attribute-filtering mask operators. |

**逐行解读**：
- **API 层**：直接对用户暴露的是 **Faiss 兼容的 C++ 接口**，对应 FeatureRetrieval 上层应用可调用的入口；四大功能为 **ingest / query / delete / train**。
- **算法逻辑层**：编排具体算法的逻辑流程，目前覆盖三大算法族——**暴力检索（Flat/SQ/INT8）、近似检索（IVFSQ）、属性过滤算法**，对应小库 / 大库 / 过滤三类场景。
- **算子层**：落到昇腾硬件上的具体加速算子，按功能分为三类——**距离计算算子、TopK 排序算子、属性过滤掩码算子**，分别支撑算法层的距离打分、TopK 选取、时空过滤能力。

### 表 2：支持的硬件与操作系统（原文逐字还原，文档在 Atlas 300I Duo 处被截断）

| Product Series | Product Model | OSs (64-bit Only) |
| --- | --- | --- |
| Atlas inference products | Atlas 300I Pro inference card | ● CentOS 7.6<br>● openEuler 20.03<br>● openEuler 22.03<br>● openEuler 24.03<br>● Ubuntu 18.04<br>● Ubuntu 20.04<br>● EulerOS 2.12<br>● EulerOS 2.15<br>● KylinOS V10 SP3 2403<br>● KylinOS V11<br>● CTyunOS 23.01<br>● UOS V20 |
| Atlas inference products | Atlas 300V video analysis card | ● CentOS 7.6<br>● openEuler 20.03<br>● openEuler 22.03<br>● Ubuntu 18.04<br>● Ubuntu 20.04<br>● EulerOS 2.12<br>● UOS V20 |
| Atlas inference products | Atlas 300V Pro video analysis card | ● CentOS 7.6<br>● openEuler 20.03<br>● openEuler 22.03<br>● openEuler 24.03<br>● Ubuntu 18.04<br>● Ubuntu 20.04<br>● EulerOS 2.12<br>● CTyunOS 23.01<br>● UOS V20 |
| Atlas inference products | Atlas 300I Duo inference ca…（原文表格此处被截断） | …（原文未给出） |

**逐行解读**：
- **产品系列**：当前 Index SDK 仅在 **Atlas 推理类产品**上完成适配与发布，覆盖 Atlas 300I Pro、300V、300V Pro、300I Duo 等型号（原文表格最后一行在录入时被截断，后续型号与 OS 未在原文中给出）。
- **OS 共性**：所有列出的型号都仅支持 **64 位 OS**，且普遍覆盖 **CentOS 7.6、openEuler 20.03/22.03、Ubuntu 18.04/20.04、EulerOS 2.12、UOS V20** 等主流服务器发行版。
- **型号差异**：较新的 Atlas 300I Pro、300V Pro 额外支持 **openEuler 24.03、EulerOS 2.15、KylinOS V10 SP3 2403/KylinOS V11、CTyunOS 23.01**；而 Atlas 300V 不含这些扩展项，OS 列表相对更短。
- **运维含义**：从硬件/OS 表反推，部署前必须确认目标 Atlas 推理卡型号与所安装 OS 是否在支持矩阵内，否则不受文档及产品支持范围覆盖。

---

## 【公式解读】

**原文无公式**。

（文档中仅涉及"小库 30 万 ~ 100 万条"、"大库数千万至数亿条"、"特征维度 64 ~ 512"、"单索引建议 ≤ 10,000"等数值与容量阈值，无数学公式或伪代码。）

---

## 【关联】

- **部署上游（依赖与安装）**：通过 `./installation_guide.md#dependency-installation` 安装依赖；通过 `./installation_guide.md#index-sdk-package-download` 获取并校验软件包；通过 `./installation_guide.md#index-sdk-installation` 完成安装部署。
- **算法选型（横向）**：通过 `./user_guide.md#algorithm-introduction` 了解各检索类型（暴力 / 近似 / 属性过滤）下具体算法的适用场景、需要生成的算子以及样例说明。
- **算子准备（向下游依赖）**：通过 `./user_guide.md#generating-operators` 编译/生成算法所需的 TBE 算子（如 `int8flat_generate_model.py`、`sq8_generate_model.py` 脚本），是 API 调用前的必要步骤。
- **API 入口（最下游）**：通过 `./api/README.md` 查取 Faiss 兼容的 C++ API 用法，最终调用实现入库、查询、删除、训练。
- **产品对内/对外关系**：API 层兼容 Faiss（对上保持生态兼容）；底层依赖昇腾 AI Processor + AscendCL + TBE 算子（向下绑定昇腾生态）；架构上由 API 层 → 算法逻辑层 → 算子层三层串联，分别对应 Faiss 接口、检索算法编排、TBE 硬件加速。

---

## 【使用方法】

**启用流程（按原文 Usage Process）**：

1. **部署（Deployment）**
   1. 确认硬件形态与 OS 在"Supported Hardware and OSs"列表中。
   2. 安装依赖 → 见 `./installation_guide.md#dependency-installation`。
   3. 获取并校验 Index SDK 安装包 → 见 `./installation_guide.md#index-sdk-package-download`。
   4. 安装并部署 Index SDK → 见 `./installation_guide.md#index-sdk-installation`。
2. **确定检索类型与算法**：根据业务需求选定小库 / 大库 / 属性过滤的具体算法及其使用场景、需生成的算子和样例 → 见 `./user_guide.md#algorithm-introduction`。
3. **生成算子**：编译生成算法所需的 TBE 算子 → 见 `./user_guide.md#generating-operators`（小库常用脚本：`int8flat_generate_model.py`、`sq8_generate_model.py`）。
4. **调用 API**：通过 Faiss 兼容 C++ 接口实现入库、查询、删除、训练 → 见 `./api/README.md`。

**关键配置项 / 容量建议（原文给出）**：

- **特征维度**：依据算法选择，**64 ~ 512 维**。
- **底库规模**：小库 **30 万 ~ 100 万**，大库 **数千万 ~ 数亿**。
- **索引数量**：**建议 < 10,000**，超过后内存碎片显著，`add` 操作可用容量可能下降。
- **运行时前置初始化**：**`aclInit` 已内部调用**，用户无需再调用。
- **兼容性边界**：仅在昇腾 AI 处理器 + 开源 Faiss 框架上验证，**不在其他硬件/异构平台兼容性范围内**。

> 原文未提供具体的安装命令、配置参数取值或 API 调用代码片段；这些信息分布在 `installation_guide.md`、`user_guide.md` 与 `api/README.md` 中（已在内部链接处指明）。

## 图文联合解读

- `software-architecture.png`: **图文联合分析**

图示呈现 Index SDK 的四层分层架构及数据流：顶层为检索与聚类应用，通过 Ingestion/Query/Delete/Train 四类接口调用 Faiss 兼容的 C++ API；中层为算法逻辑层（含全检索、近似检索、属性过滤）和算子层（含距离计算、Top-K 排序、过滤掩码算子）；底层通过 ACL 运行时库在 Host 端调度 NPU 的 AI Core、AICPU 计算资源与 Memory 存储资源。

该图论证了 **"软硬协同、算法-算子解耦"** 的技术设计：上层算法灵活支持小/大库检索模式，下层算子下沉至昇腾 NPU 实现硬件加速。

与文档呼应：图示直观印证了"基于 Faiss 风格、支持 Arm/x86_64、面向 Ascend NPU 构建异构检索加速框架"的产品定位。
- `index-sdk-usage-process.png`: **图文联合解读：**

图示为Index SDK使用流程图，呈线性单向数据流：安装部署→确定检索类型（小库/大库）→确定算法→生成算子（TBE）→调用SDK→获取检索结果，共六步闭环。

该图论证了FeatureRetrieval作为端到端检索加速框架的完整工程路径：从环境配置到结果输出，涵盖类型选择、算法确定、算子生成等核心环节，体现了"基于Faiss、面向Ascend NPU"的产品定位。

与文档呼应：图示将"产品定义"中支持的两种库类型和C++/TBE算子特性具体化为可执行步骤，印证了"在Faiss基础上构建高效向量检索引擎"的技术结论。
