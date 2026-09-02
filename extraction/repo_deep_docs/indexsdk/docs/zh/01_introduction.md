# 简介<a name="ZH-CN_TOPIC_0000001668092436"></a>

> 仓 `indexsdk` · 路径 `docs/zh/01_introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/indexsdk/docs/zh/01_introduction.md

# Index SDK 简介（docs/zh/01_introduction.md）一体化深度解读

## 【定位】

本文档是 Index SDK（基于华为昇腾 NPU 与 Faiss 框架的向量特征检索引擎）的总览性介绍文档，旨在系统说明其产品背景、检索类型与算法分类、软件架构、使用流程、关键使用约束及所支持的硬件/操作系统矩阵，为后续安装、算法选型、算子生成与接口调用提供导览。

---

## 【技术要点】

1. **核心能力定位**：FeatureRetrieval 是"基于 Faiss 开发的昇腾 NPU 异构检索加速框架"，采用与 Faiss 风格一致的 C++ 语言结合 TBE 算子开发，**同时支持 ARM 和 x86_64 平台**。
2. **两类检索能力**：分为**小库搜索（全量检索）**与**大库搜索（近似检索）**——小库规模通常 30万~100万条量级；大库规模可达到千万甚至亿级别；支持特征向量维度 **64 维到 512 维**。
3. **小库算法（暴力检索）**：当前实现 **Flat、SQ、INT8** 三类。INT8 在特征量化基础上做暴力检索，故别名 **int8flat**（算子生成脚本 `int8flat_generate_model.py`）；SQ 内部使用 8 位整型量化，故别名 **SQ8**（算子生成脚本 `sq8_generate_model.py`）。
4. **大库算法（近似检索）**：在 Ascend 平台基于 Faiss + IVF 思路实现 **IVFSQ**，其与传统"倒排索引"不同——先对特征做聚类，再通过聚类中心缩小检索范围，本质上是"用精度换性能"。
5. **附加能力**：① **属性过滤检索**（入库时挂载时间/空间等属性标签，检索时按条件过滤）；② **多 Index 批量检索**（支持分库后通过统一接口一次检索多个 Index 底库）。
6. **底层加速**：所有算法底层由 **Ascend 平台加速的 TBE 算子**实现。
7. **部署约束**：通过 **AscendCL** 接口部署，内部已调用 `aclInit`，用户无需重复调用；**单次 add 接口创建 Index 的数量建议小于 10000 个**，超过后内存碎片较多，可能导致 add 操作容量小于预期；单个 Index 最大库容取决于 Ascend AI 处理器 Device 侧内存大小。

---

## 【关键机制与数据】

**1. 检索数据流与模块分工（架构维度）**

- **API 层**：向上提供兼容 Faiss 的 C++ 接口，支持**入库（add）、查询、删除特征、训练**四类操作。
- **算法逻辑层**：编排检索算法的逻辑流程（暴力检索、近似检索、属性过滤算法等）。
- **算子层**：在昇腾平台上实现检索加速的关键算子，包括**距离计算算子、TopK 排序算子、过滤 Mask 属性算子**。
- **数据通路（原文）**：上层应用 → Index SDK API 层 → 算法逻辑层 → 算子层 → Ascend NPU 硬件加速。

**2. 算法工作机制（原文）**

- **IVFSQ 机制**：原文"对特征先做聚类，然后通过聚类中心缩小检索范围，是一种用精度换性能的方法"。
- **INT8 机制**：原文"在特征量化的基础上进行暴力检索"。
- **SQ8 机制**：原文"在内部进行量化，因使用 8 位整型进行量化"。
- **Flat 机制**：原文隐含为直接对全量向量做距离计算并按 TopK 排序的暴力检索。
- **属性过滤机制**：原文"在底库向量数据入库时添加时间、空间等属性标签，检索时通过指定属性条件，仅对符合条件的底库数据进行检索"。
- **多 Index 批量检索机制**：原文"使用多个 Index 进行分库并在执行检索时，通过统一的接口，一次检索多个 Index 底库"。

**3. 关键规模/约束数字（原文汇总）**

| 指标 | 数值 |
|---|---|
| 小库规模量级 | 30 万~100 万条 |
| 大库规模量级 | 千万~亿级 |
| 支持特征向量维度 | 64 ~ 512 维 |
| 单次 add 接口建议 Index 数 | < 10000 |
| 单 Index 最大库容 | 取决于 Ascend AI 处理器 Device 侧内存 |

> 注：原文未给出吞吐量/QPS/召回率等具体性能数字，仅给出"小库→全量、大库→近似"的容量范围与算法取舍定性描述。

---

## 【表格解读】

### 表 1：Index SDK 模块介绍（原文逐字还原）

| 模块 | 说明 |
|---|---|
| Index SDK API 层 | 提供兼容 Faiss 的 C++ 接口，上层应用可以实现入库、查询、删除特征以及训练功能。 |
| 算法逻辑层 | 实现检索算法的逻辑流程，当前支持的算法主要包括暴力检索、近似检索以及属性过滤算法等。 |
| 算子层 | 基于昇腾平台实现检索算法的加速算子，包括距离计算算子、TopK 排序算子以及过滤 Mask 属性算子等。 |

**逐行解读**：
- **Index SDK API 层**：面向开发者的最外层入口，强调"兼容 Faiss 的 C++ 接口"，意味着有 Faiss 使用经验的用户可平滑迁移；接口覆盖 add/query/delete/train 四大生命周期操作。
- **算法逻辑层**：将检索任务组织为可插拔的算法流程，原文明确列出的算法族为"暴力检索、近似检索、属性过滤算法"，这与前文"小库/大库/属性过滤"的三段能力一一对应。
- **算子层**：负责把算法逻辑映射到昇腾 NPU 的具体硬件操作，三类核心算子（距离计算、TopK 排序、过滤 Mask 属性）恰好对应三大检索路径（向量距离→TopK 排序→属性过滤）。

---

### 表 2：支持的硬件和操作系统（原文逐字还原，合并 rowspan 后按行展开）

| 产品系列 | 产品型号 | 操作系统版本（仅支持 64 位的操作系统） |
|---|---|---|
| Atlas 推理系列产品 | Atlas 300I Pro 推理卡 | CentOS 7.6；openEuler 20.03；openEuler 22.03；openEuler 24.03；Ubuntu 18.04；Ubuntu 20.04；EulerOS 2.12；EulerOS 2.15；KylinOS V10 SP3 2403；KylinOS V11；CTyunOS 23.01；UOS V20 |
| Atlas 推理系列产品 | Atlas 300V 视频解析卡 | CentOS 7.6；openEuler 20.03；openEuler 22.03；Ubuntu 18.04；Ubuntu 20.04；EulerOS 2.12；UOS V20 |
| Atlas 推理系列产品 | Atlas 300V Pro 视频解析卡 | CentOS 7.6；openEuler 20.03；openEuler 22.03；openEuler 24.03；Ubuntu 18.04；Ubuntu 20.04；EulerOS 2.12；CTyunOS 23.01；UOS V20 |
| Atlas 推理系列产品 | Atlas 300I Duo 推理卡 | CentOS 7.6；Ubuntu 18.04；Ubuntu 20.04；EulerOS 2.12；EulerOS 2.15；KylinOS V10 SP3 2403；KylinOS V11；openEuler 24.03；CTyunOS 23.01；UOS V20；UOS V25 |
| Atlas 推理系列产品 | Atlas 200I SoC A1 核心板 | CentOS 7.6；openEuler 20.03；EulerOS 2.12 |
| Atlas A2 推理系列产品（支持 AscendIndexFlat、AscendIndexInt8Flat、AscendIndexTS-FlatIP、AscendIndexTS-Int8Cos、AscendIndexIVFFlat、AscendIndexIVFRaBitQ 算法） | Atlas 800I A2 推理服务器 | CentOS 7.6；openEuler 20.03；openEuler 22.03；openEuler 24.03；Ubuntu 18.04；Ubuntu 20.04；Ubuntu 24.04；EulerOS 2.12；EulerOS 2.15；UOS V20；UOS V25；KylinOS V10 SP3；KylinOS V11；BC-Linux_21.10 U4 |
| Atlas A3 推理系列产品（支持 AscendIndexFlat、AscendIndexTS-FlatIP、AscendIndexTS-Int8Cos、AscendIndexIVFFlat、AscendIndexIVFRaBitQ 算法） | Atlas 800I A3 超节点服务器 | Ubuntu 18.04；CUlinux 3.0；KylinOS V10 SP3 2403；KylinOS V11；CTyunOS 4；UOS V25 |

**逐行解读**：
- **Atlas 300I Pro 推理卡**：覆盖面最广的 12 款操作系统，是入门推理场景的主力卡型，可作为兼容性最宽松的部署选项。
- **Atlas 300V 视频解析卡**：7 款 OS，重点是视频解析场景，OS 列表相对精简（缺 Ubuntu 24.04、openEuler 24.03、KylinOS 等更新版本）。
- **Atlas 300V Pro 视频解析卡**：10 款 OS，相比 300V 新增 openEuler 24.03、EulerOS 2.12 上的补强以及 CTyunOS 23.01。
- **Atlas 300I Duo 推理卡**：12 款 OS，且首次出现 **UOS V25**（与 A2 推理服务器相呼应），定位双芯推理。
- **Atlas 200I SoC A1 核心板**：仅 3 款 OS（CentOS 7.6、openEuler 20.03、EulerOS 2.12），属于边缘/嵌入式场景的最精简组合。
- **Atlas A2 推理系列产品（Atlas 800I A2 推理服务器）**：OS 覆盖最全（14 款，含 BC-Linux_21.10 U4），算法清单首次披露了 **AscendIndexTS-FlatIP、AscendIndexTS-Int8Cos、AscendIndexIVFRaBitQ** 等较新算子，表明 A2 系列是面向生产的旗舰推理平台。
- **Atlas A3 推理系列产品（Atlas 800I A3 超节点服务器）**：OS 收敛为 6 款（新增 CUlinux 3.0、CTyunOS 4），且**不支持 AscendIndexInt8Flat**（对比 A2 算法清单可见），说明 A3 当前的算法子集是 A2 的子集，体现"超节点"硬件形态尚处于算法逐步对齐阶段。

---

## 【公式解读】

**原文无公式**。本文档作为产品介绍与架构概览，未涉及任何数学公式、伪代码或量化误差表达式。

---

## 【关联】

文档在"使用流程"中明确给出了从入门到调用接口的链式指引，可串联到以下文档：

1. **[安装依赖说明（./04_installation_guide.md#安装依赖说明）】**——属于"使用流程"第 1 步"安装部署"中的第 2 小步（依赖前置），先决条件文档；只有依赖到位后才能继续离线安装。
2. **[离线安装（./04_installation_guide.md#离线安装）】**——属于"使用流程"第 1 步中的第 3 小步（Index SDK 本身的部署），依赖前一步的依赖安装结果。
3. **[算法介绍（./05_user_guide.md#算法介绍）】**——属于"使用流程"第 2 步"确定检索类型与算法"，是依据业务规模（小库/大库）与维度（64~512）选择 Flat/SQ/INT8/IVFSQ 等具体算法的依据。
4. **[生成算子（./05_user_guide.md#生成算子）】**——属于"使用流程"第 3 步，对应 `int8flat_generate_model.py`、`sq8_generate_model.py` 等算子生成脚本的实际使用说明，与本文档"算法分类"段落中提及的两个脚本名一一对应。
5. **[API 参考（./api/README.md）】**——属于"使用流程"第 4 步"调用接口实现算法"，对应 API 层"入库、查询、删除特征、训练"四类 C++ 接口的详细定义。

**模块上下游关系**：
- 上游（调用方）：上层应用 → 通过 Faiss 风格的 C++ API 调用。
- 下游（依赖）：AscendCL（已封装 aclInit）→ Ascend NPU + TBE 算子。
- 平行模块：算法逻辑层与算子层解耦，算子层封装具体的"距离计算、TopK 排序、属性 Mask 过滤"等原子能力，供算法逻辑层组合。

---

## 【使用方法】

**1. 入门学习（原文有）**
- 推荐学习课程：IndexSDK 特征检索入门课程（https://www.hiascend.com/edu/growth/details/310d161ab02c45958f9bc3d8fbbec51e）。

**2. 标准使用流程（原文"使用流程"小节给出的 4 步）**
1. **安装部署**：先确认产品硬件/操作系统支持（见"支持的硬件和操作系统"表），再完成依赖安装（→ `./04_installation_guide.md#安装依赖说明`），最后完成 Index SDK 自身安装（→ `./04_installation_guide.md#离线安装`）。
2. **确定检索类型与算法**：根据数据规模与维度选择小库（Flat / SQ8 / INT8-flat）或大库（IVFSQ），必要时叠加属性过滤或多 Index 批量检索（→ `./05_user_guide.md#算法介绍`）。
3. **生成算子**：通过对应生成脚本（如 `int8flat_generate_model.py`、`sq8_generate_model.py`）产出 TBE 算子（→ `./05_user_guide.md#生成算子`）。
4. **调用接口**：使用兼容 Faiss 的 C++ API 实现 add/query/delete/train，得到检索结果（→ `./api/README.md`）。

**3. 关键使用约束/配置项（原文"使用须知"小节）**
- **硬件范围**：仅在昇腾 AI 处理器 + 开源 Faiss 上开发适配，**不支持**其他硬件或异构计算平台。
- **AscendCL 初始化**：部署层已内部调用 `aclInit`，**用户无需再次调用**。
- **单次 add 上限**：建议单次调用 add 接口创建的 Index 数量 **< 10000 个**；超过会产生较多内存碎片，导致 add 实际容量低于预期。
- **单 Index 容量上限**：受限于 Ascend AI 处理器 Device 侧内存大小；业务侧需根据实际需求规划 Index 个数，避免内存超限。

**4. 命令/脚本名（原文有）**
- `int8flat_generate_model.py`（INT8 暴力检索算子生成脚本，对应 INT8 = int8flat）。
- `sq8_generate_model.py`（SQ 量化检索算子生成脚本，对应 SQ = SQ8，8 位整型量化）。

## 图文联合解读

- `软件架构.png`: **图示内容**：自上而下四层架构——应用层（检索服务，入库/查询/删除/训练）→ Index SDK（含API层、算法逻辑层、算子层）→ ACL运行时库（Host：X86/ARM）→ Device（AI Core/AI CPU/MEM），算子下发与内存管理贯穿Host-Device。

**技术结论**：Index SDK采用分层解耦设计，Faiss风格C++ API统一对外，算子层将距离计算、TopK排序、过滤Mask等任务下沉至昇腾NPU加速，主机端负责调度与内存管理，形成CPU+NPU异构加速闭环。

**与文档关系**：图示印证"Faiss风格C++接口+基于昇腾NPU异构加速"的产品定义，并直观呈现全量/近似/属性过滤三类算法的统一算子化实现路径。
- `zh-cn_image_0000002148233552.png`: # 图文联合解读

**1) 图中内容**：线性流程图，6个蓝色圆角矩形按箭头串联——`安装部署` → `确定检索类型` → `确定算法` → `生成算子` → `调用SDK` → `得到检索结果`，呈现端到端的使用步骤。

**2) 技术结论**：论证Index SDK具备**标准化、可落地的工程闭环**，用户无需深入底层，只需按"环境→类型→算法→算子→接口→结果"的固定链路即可完成向量检索全流程。

**3) 与文档关系**：文档介绍Index SDK是小库/大库特征检索引擎，图中"确定检索类型/算法"对应文档中的Flat、SQ8、IVFSQ等算法选择，"生成算子"对应TBE算子加速机制，整体流程图作为**使用指引**补充了产品定义中的技术细节。
