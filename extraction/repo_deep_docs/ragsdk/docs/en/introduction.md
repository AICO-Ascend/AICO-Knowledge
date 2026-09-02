# Introduction

> 仓 `ragsdk` · 路径 `docs/en/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ragsdk/docs/en/introduction.md

# ragsdk `docs/en/introduction.md` 一体化深度解读

---

## 【定位】

本篇是 **RAG SDK**（昇腾面向大语言模型的知识增强开发套件）的 Overview/介绍文档，旨在说明该套件针对大模型知识更新慢、垂直域问答弱等痛点所提供的快速搭建垂域 QA 系统的能力、整体软件架构、以及所支持的硬件/OS 运行环境。

---

## 【技术要点】

1. **目标定位**：原文指出 RAG SDK 是「Ascend-based knowledge-enhancement RAG SDK」，面向 QA 场景，提供模块化函数接口，**不包含**「user, permissions, or other function interfaces closely tied to business logic」。
2. **三大主功能**（原文原话）：① Quick setup（模块化接口 + 端到端工作流模板，"with very little code"）；② Multimodal parsing（支持 documents / tables / PDFs / images 等多模态文件解析）；③ High-performance inference（"Ascend-friendly model optimization and acceleration"）。
3. **向量化能力**：调用 embedding 与 reranker 两类模型，支持 **本地部署** 与 **服务化部署** 两种形态，服务化框架使用开源的 **text-embeddings-inference**。
4. **检索加速**：使用 **Ascend NPU 异构检索加速框架**，处理高维空间海量数据的高性能检索。
5. **缓存机制**：集成开源 **gptcache**，支持 **exact-match caching (memory cache)** 与 **semantic-similarity caching (similarity cache)** 两种缓存策略。
6. **目标受众**：原文明示 "Huawei technical support engineers" 与 "Channel partner technical support engineers"。

---

## 【关键机制与数据】

**工作原理/数据流（按原文对架构的描述复述）**：

- **RAG Python API** → 对上层应用暴露「模块化函数接口」，用户可灵活调用各 RAG 服务。
- **Knowledge management → Indexing → Vectorization → Retrieval** 形成端到端数据通路（原文）：
  - Knowledge management 负责知识库管理，支持多知识库创建、上传 documents/tables/images 等文件，提供加载、解析、分块及高效向量检索。
  - Indexing 通常包含「corpus collection → corpus parsing → corpus splitting → index construction (vectorization)」，索引基于 Knowledge management 模块内容生成。
  - Vectorization 提供 embedding/reranker 模型加载与第三方服务集成，**"The vectorization results form the basis of retrieval and ensure that queries match the knowledge base content."**
  - Retrieval 接收用户 query 后，调用 LLM 转换文本生成 query vector，再做搜索 + rerank，将结果返回 LLM。"Retrieval depends on vectorization results and uses vector comparison for efficient matching."
- **Caching**：原文："By caching queried results, it reduces repeated computation and improves retrieval speed."
- **Application acceleration operator layer**：对 vectorization / retrieval 等核心模块做 Ascend 友好优化，提升吞吐量与缩短响应时间。

**性能数据**：原文未给出具体的吞吐量、时延、召回率等数值（仅定性描述 "higher throughput and shorter response times"）。

---

## 【表格解读】

**Supported Hardware and Runtime Environments**（原文 markdown 表格逐字还原）：

| Product model | OS versions |
|---|---|
| Atlas 300I Duo inference card | <li>Ubuntu 20.04</li><li>Ubuntu 22.04</li><li>Ubuntu 24.04</li><li>KylinOS V10 SP3</li><li>BCLinux 21.10</li><li>EulerOS 2.13 for AArch64</li><li>EulerOS 2.15 for AArch64</li><li>Huawei Cloud EulerOS for x86_64</li><li>openEuler 24.03</li><li>openEuler 22.03 LTS SP4 for AArch64</li><li>CUlinux 3.0</li><li>CTyunOS 23.01</li><li>Kylin V10 SP3 2403</li><li>KylinOS V11</li> |
| Atlas 800I A2 inference server<br>Atlas 800I A3 SuperNode server | （同上 OS 列表，rowspan=2 共享） |

**逐行解读**：

- **第 1 行**：推理卡 **Atlas 300I Duo**，是单卡形态，对应边缘/小规模部署场景，配套 14 个 OS 发行版。
- **第 2 行**：推理服务器 **Atlas 800I A2** 与 **Atlas 800I A3 SuperNode server** 共用同一份 OS 列表；其中 **A3 SuperNode** 是面向超节点互联的大规模推理形态，适合高并发 QA 检索/生成。
- **OS 列表整体观察**：覆盖
  - **Ubuntu** LTS 系列（20.04 / 22.04 / 24.04）
  - **Kylin 系**：KylinOS V10 SP3、Kylin V10 SP3 2403、KylinOS V11（麒麟桌面/服务器 OS）
  - **openEuler 系**：openEuler 24.03、openEuler 22.03 LTS SP4 for AArch64（其中 AArch64 表明 ARM 架构支持）
  - **EulerOS 系**：2.13/2.15 for AArch64，以及 Huawei Cloud EulerOS for x86_64
  - **国产化云 OS**：BCLinux 21.10、CUlinux 3.0、CTyunOS 23.01
  - 覆盖 **x86_64 与 AArch64** 两种 CPU 架构，符合昇腾"一芯多用"以及信创生态兼容性需求。

---

## 【公式解读】

原文无公式（无 LaTeX、无伪代码形式的算法表达式）。

---

## 【关联】

由于本任务给定的"内部链接"清单标注为 **(无)**，可识别的文档内交叉引用只有一处：

- **Figure 1**（锚点 `#fig10342102918356`）：Software architecture diagram，对应图片资源 `figures/240909152924310.png`。该图与正文中六个模块的描述一一对应：
  - **RAG Python API**（顶层入口）
  - **Knowledge management**（上层，对应下游 Indexing / Vectorization 的数据来源）
  - **Indexing**（依赖 Knowledge management 的内容）
  - **Vectorization**（提供 embedding / reranker 服务，被 Retrieval 消费）
  - **Retrieval**（依赖 Vectorization 结果，对接 Ascend NPU 异构加速框架）
  - **Caching**（横切模块，集成 gptcache，作用于查询结果复用）
  - **Application acceleration operator layer**（贯穿底层，对 vectorization / retrieval 做 Ascend 友好加速）

模块间的依赖关系（按原文描述归纳）：
- Knowledge management → Indexing → Vectorization → Retrieval 形成数据流主干；
- Caching 横切主干；
- Application acceleration operator layer 为底层算子支撑；
- RAG Python API 对外暴露能力。

---

## 【使用方法】

原文未涉及具体启用命令、配置文件路径、API 调用样例或参数表。仅在功能描述中提及以下可用性线索：

- **部署形态**：Vectorization 支持 "local deployment" 与 "service-based deployment"，服务化框架使用 `text-embeddings-inference`。
- **使用方式**："modular function interfaces and supports on-demand calls"；"built-in end-to-end workflow templates, users can quickly launch a QA service with very little code"。
- **受众限定**：文档自述 "mainly intended for ... Huawei technical support engineers" 与 "Channel partner technical support engineers"，因此该 introduction 面向技术支持/合作伙伴角色，而非终端开发者直接上手教程。

具体启动命令、Python SDK 安装步骤、配置文件项等内容需查阅本仓库其他文档（如用户手册、API 参考等），原文未给出。

## 图文联合解读

- `240909152924310.png`: **图文联合解读：**

1）图示为RAG SDK分层架构，自底向上为：Ascend硬件→CANN→算子层→推理框架（MindIE/vLLM）→LLM增强能力（Prompt压缩/RAG缓存）→SDK应用套件（RAG Python API，涵盖知识管理、索引、向量化、检索、缓存五大模块，支持文-文/文-图/图-图及混合检索）。

2）论证了SDK采用**全栈模块化设计**，硬件到应用层层解耦，覆盖检索增强全流程。

3）与文档呼应：图示直观呈现了"模块化功能接口"和"检索、知识管理"等核心论点，证明RAG SDK通过分层架构实现低成本领域化LLM构建。
