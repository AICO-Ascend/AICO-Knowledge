# 昇腾Ascend开源软件仓库

> 仓 `community` · 路径 `docs/org-introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/community/docs/org-introduction.md

# 昇腾 Ascend 开源软件仓库 Overview 文档深度解读

---

## 【定位】

本文档是昇腾（Ascend）开源软件仓库的总览/索引页，面向开发者系统性罗列昇腾 Ascend AI 处理器生态下"全栈开源软件"的组成与项目清单，承担「一张图看懂昇腾开源版图」的角色，并作为社区协作入口（会议、协作指南、FAQ、行为准则）的导航页。

---

## 【技术要点】

**核心覆盖方向（来自原文导言）：** 应用使能、训推加速、集群管理、工具链——四大全栈能力。

按文档表格分组的技术栈分布如下（共 7 大类、约 28 个子项目）：

1. **编译基础设施层**：AscendNPU IR —— 基于 MLIR 构建的、面向昇腾亲和算子编译时使用的中间表示。
2. **PyTorch 适配层**：TorchNPU（PyTorch 适配插件）、OpPlugin（算子适配插件）、TorchAir（图模式能力扩展库）。
3. **推理服务层（MindIE 系列）**：MindIE SD（视图生成推理模型套件）、MindIE LLM（大语言模型推理组件）、MindIE Motor（通用模型推理服务化框架）、MindIE Turbo（大语言模型推理引擎加速插件库）。
4. **训练加速层（MindSpeed 系列）**：MindSpeed Core（大模型训练加速库）、MindSpeed MM（大规模分布式多模态训练套件）、MindSpeed LLM（大语言模型分布式训练框架）、MindSpeed RL（强化学习加速框架）、MindSpeed-Core-MS（MindSpore + MindSpeed 连接组件）。
5. **AI 应用 SDK 层（MindSDK）**：Rec SDK、Index SDK、Driving SDK、Agent SDK、Vision SDK、Multimodal SDK、RAG SDK、Mind Inference Service 共 8 个。
6. **开发工具链层（MindStudio）**：msTT（训练工具集）、msIT（推理工具集）、msOT（算子工具集）三类。
7. **集群与基础设施层（MindCluster）**：MindCluster、MEF（端边云协同）、OMSDK（边缘硬件管理）、MemCache（分布式 KVCache）、MemFabric（内存池化与全局内存直访）、ascend-deployer（带内软件自动部署）。

> 说明：原文除「基于 MLIR」「基于 Faiss」等技术渊源表述外，**未给出任何性能数字、版本号、命令参数**。

---

## 【关键机制与数据】

原文为概览页，**没有出现具体的算法步骤、性能数据、带宽/时延/吞吐数值、benchmark 跑分或数据流图**。仅能摘录的机制性表述如下：

- **原文：** "基于 MLIR 构建的，面向昇腾亲和算子编译时使用的中间表示" → AscendNPU IR 的定位是 MLIR 框架下的 IR 层。
- **原文：** "基于 Faiss 开发的昇腾 NPU 异构检索加速框架" → Index SDK 衍生自 Faiss，并面向 NPU 异构化。
- **原文：** "为 LLM 推理、GR 推理场景设计的高性能分布式 KVCache 存储引擎" → MemCache 的应用域被锁定为 LLM 与 GR 两种推理场景。
- **原文：** "提供内存池化、高性能的全局内存直接访问的能力" → MemFabric 提供内存池化 + 全局内存直访（RDMA 类语义）。
- **原文：** "提供驱动、固件、CANN 等昇腾带内软件以及 OS 依赖软件，自动下载及安装部署参考" → ascend-deployer 覆盖范围含驱动、固件、CANN、OS 依赖。

除上述几条原文定性表述外，**无任何量化数据可摘录**。

---

## 【表格解读】

原文核心即一张项目清单表，原文使用 HTML `<table>` 形式呈现，单列结构（表头"项目简介"），按 7 个分组（行）罗列项目。**逐字还原**如下（去掉 HTML 标签、保留链接与分组语义）：

| 项目分类 | 子项目（链接仓库 / 简介原文） |
|---|---|
| （无分组标题的项目） | **[AscendNPU IR](https://gitcode.com/Ascend/AscendNPU-IR)** - 基于 MLIR 构建的，面向昇腾亲和算子编译时使用的中间表示 |
| Ascend for PyTorch | **[TorchNPU](https://gitcode.com/Ascend/pytorch)** - 基于昇腾NPU的PyTorch适配插件 |
| Ascend for PyTorch | **[OpPlugin](https://gitcode.com/Ascend/op-plugin)** - TorchNPU的算子适配插件 |
| Ascend for PyTorch | **[TorchAir](https://gitcode.com/Ascend/torchair)** - TorchNPU的图模式能力扩展库 |
| MindIE | **[MindIE SD](https://gitcode.com/Ascend/MindIE-SD)** - 视图生成推理模型套件 |
| MindIE | **[MindIE LLM](https://gitcode.com/Ascend/MindIE-LLM)** - 大语言模型推理组件 |
| MindIE | **[MindIE Motor](https://gitcode.com/Ascend/MindIE-Motor)** - 面向通用模型场景的推理服务化框架 |
| MindIE | **[MindIE Turbo](https://gitcode.com/Ascend/MindIE-Turbo)** - 大语言模型推理引擎加速插件库 |
| MindSpeed | **[MindSpeed Core](https://gitcode.com/Ascend/MindSpeed)** - 大模型训练加速库 |
| MindSpeed | **[MindSpeed MM](https://gitcode.com/Ascend/MindSpeed-MM)** - 大规模分布式训练的多模态大模型套件 |
| MindSpeed | **[MindSpeed LLM](https://gitcode.com/Ascend/MindSpeed-LLM)** - 大语言模型分布式训练框架 |
| MindSpeed | **[MindSpeed RL](https://gitcode.com/Ascend/MindSpeed-RL)** - 强化学习加速框架 |
| MindSpeed | **[MindSpeed-Core-MS](https://gitcode.com/Ascend/MindSpeed-Core-MS)** - MindSpore + MindSpeed 的连接组件 |
| MindSDK AI应用软件开发套件 | **[Rec SDK](https://gitcode.com/Ascend/RecSDK)** - 大规模推荐训推加速库，提供开箱即用的模型和昇腾亲和的加速模块 |
| MindSDK AI应用软件开发套件 | **[Index SDK](https://gitcode.com/Ascend/IndexSDK)** - 基于Faiss开发的昇腾NPU异构检索加速框架，提供高性能的检索 |
| MindSDK AI应用软件开发套件 | **[Driving SDK](https://gitcode.com/Ascend/DrivingSDK)** - 提供了适用于自动驾驶场景、VLA及世界模型的高性能的算子和模型加速接口 |
| MindSDK AI应用软件开发套件 | **[Agent SDK](https://gitcode.com/Ascend/AgentSDK)** - 智能体 Agentic RL 训推框架 |
| MindSDK AI应用软件开发套件 | **[Vision SDK](https://gitcode.com/Ascend/VisionSDK)** - 面向图片和视频视觉分析的SDK，提供了基本的视频、图像智能分析能力及编程框架 |
| MindSDK AI应用软件开发套件 | **[Multimodal SDK](https://gitcode.com/Ascend/MultimodalSDK)** - 提供高性能的昇腾设备亲和性接口，加速大模型推理预处理流程 |
| MindSDK AI应用软件开发套件 | **[RAG SDK](https://gitcode.com/Ascend/RAGSDK)** - 面向大语言模型的知识增强开发套件 |
| MindSDK AI应用软件开发套件 | **[Mind Inference Service](https://gitcode.com/Ascend/MindInferenceService)** - 提供了模型推理服务，无需复杂的依赖安装，即可快速完成部署 |
| MindStudio | **[MindStudio Training Tools(msTT)](https://gitcode.com/Ascend/mstt)** - 提供训练开发中常用的分析迁移工具、精度调试工具、性能调优等工具 |
| MindStudio | **[MindStudio Inference Tools(msIT)](https://gitcode.com/Ascend/msit)** - 提供推理开发中常用的模型压缩、模型调试调优等工具 |
| MindStudio | **[MindStudio Operator Tools(msOT)](https://gitcode.com/Ascend/msot)** - 提供算子开发中常用的异常检测、算子调试、性能调优等工具 |
| MindCluster | **[MindCluster](https://gitcode.com/Ascend/mind-cluster)** - 为训练和推理任务提供集群级解决方案 |
| MindCluster | **[MEF](https://gitcode.com/Ascend/MEF)** - 轻量化端边云协同框架，提供边缘节点管理、边缘推理应用生命周期管理等能力 |
| MindCluster | **[OMSDK](https://gitcode.com/Ascend/OMSDK)** - 提供快速搭建智能边缘硬件管理平台，自定义构建设备运维系统，简化设备运维部署能力 |
| MindCluster | **[MemCache](https://gitcode.com/Ascend/memcache)** - 为LLM推理、GR推理场景设计的高性能分布式KVCache存储引擎 |
| MindCluster | **[MemFabric](https://gitcode.com/Ascend/memfabric_hybrid)** - 提供内存池化、高性能的全局内存直接访问的能力 |
| MindCluster | **[ascend-deployer](https://gitcode.com/Ascend/ascend-deployer)** - 提供驱动、固件、CANN等昇腾带内软件以及OS依赖软件，自动下载及安装部署参考的功能 |

**逐组解读（按原文层级语义）：**

- **第 1 行（AscendNPU IR）**：昇腾栈底层的编译器基础设施。该项目独立成行、未归入任何上层分组，暗示它是"被所有上层项目共用"的底层依赖。
- **第 2–4 行（Ascend for PyTorch）**：聚焦 PyTorch 生态在昇腾上的迁移。TorchNPU 是入口插件；OpPlugin 是补齐 NPU 原生算子的"算子补丁"层；TorchAir 则把执行模式从 eager 升级到 graph（图中捕获/编译优化），三者是「插件→算子→图模式」的逐层递进关系。
- **第 5–8 行（MindIE）**：推理服务栈。SD 偏生成式视觉推理；LLM 与 Turbo 强绑定 LLM 推理（Turbo 是 LLM 引擎加速插件，对 LLM 形成加速关系）；Motor 抽象成面向任意模型的通用推理服务化框架，处于更高一层。
- **第 9–13 行（MindSpeed）**：训练加速栈，覆盖通用大模型训练（Core）、多模态分布式（MM）、LLM 专属分布式（LLM）、强化学习（RL）四类训练范式；Core-MS 是 MindSpore ↔ MindSpeed 的桥接器，定位为生态互联组件。
- **第 14–21 行（MindSDK）**：场景化应用 SDK 集合。Rec/Index 偏传统推荐与检索；Driving 对自动驾驶 / VLA / 世界模型；Agent 面向 Agentic RL；Vision 偏视觉分析；Multimodal 偏推理预处理；RAG 偏知识增强；Mind Inference Service 偏无依赖快速部署——共同特征是"开箱即用、面向具体业务域"。
- **第 22–24 行（MindStudio）**：开发期工具集合，三类分别对应训练 / 推理 / 算子三种开发场景（分析迁移、性能调优、异常检测），是研发提效工具而非运行时组件。
- **第 25–30 行（MindCluster）**：集群与硬件/部署层。MindCluster 是核心调度层；MEF/OMSDK 处理边缘侧节点与设备运维；MemCache/MemFabric 是分布式内存与 KVCache 基础设施；ascend-deployer 是带内软件（CANN/驱动/固件）自动化安装工具——这一层最贴近硬件与 OS。

整体上看，表格反映昇腾开源版图按"**底层编译 → 框架适配 → 训练加速 → 推理服务 → 场景 SDK → 研发工具 → 集群与部署**"自底向上组织的栈式分层。

---

## 【公式解读】

原文无任何公式（无 LaTeX、无伪代码、无数学表达式）。**原文无公式**。

---

## 【关联】

依据文末"参与贡献"与"相关链接"两节，可梳理出本文档作为索引页所链接的上下游节点：

- **./role-guidance.md**（开源协作指南）：本文档的"参与贡献"小节直接引用该相对路径文件，定位为贡献者角色与协作流程说明页，**是本文档的"如何参与"配套文档**。
- **./FAQ/infra-faq.md**（FAQ）：同列于"参与贡献"小节，定位为社区基础设施常见问题解答，**承接本文档项目清单中可能涉及的运维 / 仓库 / 权限类疑问**。
- **../docs/contributor/code-of-conduct.md**（Code of Conduct）：行为准则，**横跨整个 community 仓库**的贡献者行为规范。
- **https://meeting.osinfra.cn/ascend**（社区会议日历）：外部链接，提供定期社区会议时间。
- **https://gitcode.com/Ascend/infrastructure/.../robot使用指南.md**（机器人使用指南）：外部链接，指向 infrastructure 仓库下机器人（自动化 Bot）的使用文档，**与社区 PR / Issue 自动化流转相关**。
- **https://www.hiascend.com/**（昇腾社区）：昇腾官方对外门户站，**是本文档所有项目面向用户的最顶层入口**。

**横向项目级关联（来自表格中项目名共现）：**
- **AscendNPU IR** 作为编译底层，被上层（推断为 MindSpeed / MindStudio msOT 等算子/训练相关项目）共用。
- **OpPlugin → TorchNPU** 的从属关系（原文："TorchNPU 的算子适配插件"）。
- **TorchAir → TorchNPU** 的从属关系（原文："TorchNPU 的图模式能力扩展库"）。
- **MindSpeed-Core-MS** 桥接 MindSpore 与 MindSpeed，**跨生态互联组件**。
- **MemCache / MemFabric** 共同出现在 MindCluster 分组下，二者形成"**KVCache 存储 + 内存池化直访**"的分布式内存子系统，**为 LLM 推理（MindIE LLM / Turbo）和大规模分布式训练（MindSpeed LLM/MM）提供存储底座**。
- **ascend-deployer** 与 **CANN/驱动/固件** 强绑定，是 MindCluster 中"带内软件自动部署"的载体。
- **MindStudio 三件套（msTT/msIT/msOT）** 各自对接上层 MindSpeed / MindIE / 算子开发流程——表格中虽未显式连线，但分类语义（Training/Inference/Operator Tools）已隐含该对应关系。

---

## 【使用方法】

**原文未涉及**任何"启用方式 / 配置项 / 安装命令 / API 调用样例"。本页是导航/索引页，**仅指引用户前往各子项目仓库自行查看部署与使用方式**，入口即为表格中每行提供的 `https://gitcode.com/Ascend/<repo>` 链接。

如需了解参与流程，请按原文"参与贡献"小节进入 `./role-guidance.md`（开源协作指南）；如遇问题进入 `./FAQ/infra-faq.md`（FAQ）。
