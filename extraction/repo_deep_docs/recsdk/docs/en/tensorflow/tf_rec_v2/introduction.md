# Introduction

> 仓 `recsdk` · 路径 `docs/en/tensorflow/tf_rec_v2/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/tensorflow/tf_rec_v2/introduction.md

# Rec SDK TensorFlow Introduction 文档深度解读

## 【定位】
这篇文档是 Rec SDK TensorFlow 的总览(Overview)性介绍,旨在描述其在华为昇腾(Ascend)AI 处理器上,为搜索/推荐/广告模型训练所提供的"基础训练能力 + 推荐专用稀疏表能力"的整体功能边界、软件架构层次以及所支持的硬件与操作系统。

---

## 【技术要点】

1. **双层能力定位**:Rec SDK TensorFlow 提供两类能力——基础训练能力(单服务器单卡训练、单服务器多卡训练,基于 TensorFlow 的模型开发),以及推荐专用能力(基于稀疏表方案的特征存取/准入/淘汰)。
2. **四大关键特性(Key Features)**:
   - **稀疏表创建**(Sparse table creation)——通过 [`get_embedding_table`](api/model_apis.md#get_embedding_table) API
   - **稀疏表查询**(Sparse table query)——通过 [`embedding_lookup`](api/model_apis.md#embedding_lookup) API
   - **保存与加载**(Saving and loading)——通过 [`embeddingtablesaver`](api/model_apis.md#embeddingtablesaver) API
   - **特征准入与淘汰**(Feature admission and eviction)——通过 `get_embedding_table` API 中的 `min_used_times` 与 `max_cold_secs` 两个参数实现
3. **四层软件架构**:自上而下分为 API 层、推荐功能层(Recommended function layer)、推荐加速层(Recommendation acceleration layer)、稀疏存储层(Sparse storage layer)。
4. **支撑底座**:构建于主流推荐框架、CANN 之上,适配多种硬件与网络架构,目标是让 Ascend AI Processor 在搜索/推荐/广告模型训练上达到高效性能。
5. **支持的训练规模**:原文明确给出稀疏存储层可支持 **"more than 10 TB"** 的大规模稀疏表存储(原文表 1)。
6. **硬件/OS 矩阵**:覆盖 Atlas 800T A2、Atlas 200T A2 Box16、Atlas 900 A3 SuperPoD 三类整机产品,涉及 CentOS 7.6 / openEuler 22.03 / Ubuntu 20.04 三种 OS(原文表 2)。

---

## 【关键机制与数据】

- **特征准入/淘汰的设计动机**:原文指出"低频特征往往对训练无帮助,造成内存浪费与过拟合",因此引入特征准入功能来过滤低频特征;对训练无益的特征需被剔除,以避免影响训练效果并节约内存。
- **保存与加载的内涵**:原文定义"持久化存储已训练模型参数,并在需要时恢复"——保存通常包含**模型结构、权重、优化器状态**;加载则将模型恢复到可用状态,可用于训练中断后继续或推理部署。
- **性能/规模数据(原文)**:
  - 稀疏存储层:"Supports large-scale sparse table storage of **more than 10 TB**."(原文表 1:Sparse storage layer)
- **数据流/工作原理(原文)**:原文未给出具体的数据流图或工作原理伪代码,仅以四层架构图(`figures/4-mxRec-architecture.png`)做高层抽象;详细流程需结合各 API 文档查阅。
- **其他量化指标**:原文未涉及训练吞吐、embedding 维度、batch size 等量化指标。

---

## 【表格解读】

### 表 1(原文逐字还原):架构图中的模块

|Rec SDK TensorFlow Module|Description|
|--|--|
|API layer|Provides easy-to-use APIs to simplify customer access and support service growth.|
|Recommended function layer|Provides core capabilities to meet customer requirements.|
|Recommendation acceleration layer|Provides core components to build performance competitiveness and offer superb performance for the entire system.|
|Sparse storage layer|Supports large-scale sparse table storage of more than 10 TB.|

**逐行解读**:
- **API layer**:最上层面向用户的接口层,目标是"简化客户接入、支持业务增长",对应文档中四大特性的入口 API(`get_embedding_table`、`embedding_lookup`、`embeddingtablesaver` 等)。
- **Recommended function layer**:业务功能层,承载"满足客户需求的核心能力",与 Overview 中提到的特征存取/准入/淘汰等推荐专用能力对应。
- **Recommendation acceleration layer**:性能加速层,提供"构建性能竞争力的核心组件",是 Rec SDK 在 Ascend 上实现高效训练的关键加速模块。
- **Sparse storage layer**:底层存储层,唯一给出量化指标的一层——支持 **>10 TB 级别**的大规模稀疏表存储,是推荐场景中大规模 embedding 表的物理基础。

### 表 2(原文逐字还原):支持的产品

|Product|Architecture|OS Version|
|--|--|--|
|Atlas 800T A2 training server<br>Atlas 200T A2 Box16 heterogeneous subrack|<li>Arm</li><li>x86_64</li>|<li>CentOS 7.6</li><li>openEuler 22.03</li><li>Ubuntu 20.04</li>|
|Atlas 900 A3 SuperPoD|Arm|openEuler 22.03|

**逐行解读**:
- **Atlas 800T A2 训练服务器 / Atlas 200T A2 Box16 异构子框**:同属 A2 系列,二者共享架构与 OS 选项——支持 Arm 与 x86_64 两种 CPU 架构,OS 可选 CentOS 7.6、openEuler 22.03、Ubuntu 20.04,适配面较广。
- **Atlas 900 A3 SuperPoD**:仅 Arm 架构,且仅支持 openEuler 22.03——这是面向更大规模训练场景(超节点/PoD 形态)的更高端型号,选型更收敛。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本 Introduction 作为总览性章节,与文档内以下 API/特性存在显式的上下游引用关系:

- **稀疏表创建** → 链接到 `api/model_apis.md#get_embedding_table`(文中出现 2 次:1 次用于"创建",1 次用于"特征准入与淘汰"),说明该 API 既承担创建也承担准入/淘汰控制(`min_used_times`、`max_cold_secs`)。
- **稀疏表查询** → 链接到 `api/model_apis.md#embedding_lookup`,是读取/查询稀疏表中已有特征向量的入口。
- **保存与加载** → 链接到 `api/model_apis.md#embeddingtablesaver`,与"保存包含模型结构、权重、优化器状态"的能力描述一一对应,负责稀疏表的持久化。
- **架构层次关联**:API 层封装上述 API → 调用 Recommended function 层核心能力 → 经 Recommendation acceleration 层在 Ascend 上获得加速 → 落到 Sparse storage 层做大规模存储;四层之间是"接口 → 业务 → 加速 → 存储"的层层下沉关系。
- **硬件/OS 关联**:底层依赖 Ascend AI Processor + CANN + 多样硬件/网络架构,与表 2 所列 Atlas 系列训练服务器/超节点形成"软件栈 ↔ 硬件载体"的对应。

---

## 【使用方法】

原文未涉及具体的启用步骤、配置命令或部署流程(无 CLI 命令、无环境变量、无安装/启动指令)。

唯一可作为"配置项"线索的参数为特征准入与淘汰相关的两个字段(原文):

- **`min_used_times`**(参数,出自 `get_embedding_table` API)——用于特征准入控制
- **`max_cold_secs`**(参数,出自 `get_embedding_table` API)——用于特征淘汰控制

但其具体取值/语义需进一步查阅 `api/model_apis.md#get_embedding_table` 章节,本文档未给出更多说明。

## 图文联合解读

- `4-mxRec-architecture.png`: **图示解读**

1) **结构内容**：图为Rec SDK的分层架构图，自顶向下四层堆叠——接口层、推荐功能层、推荐加速层、稀疏存储层构成Rec SDK主体；其下依次为深度学习框架（TensorFlow/MindSpore）、异构计算架构（CANN）以及Ascend硬件底层。图例以蓝、青、灰三色区分SDK、框架与基础环境。

2) **技术结论**：Rec SDK通过模块化分层（功能/加速/存储解耦）实现"推荐能力+训练框架+硬件加速"的端到端协同；稀疏存储层为底层，加速层对接CANN完成硬件加速，性能由Ascend保障。

3) **与文档关系**：呼应文档"基于TensorFlow的基础训练+稀疏表方案支撑特征存取/准入/淘汰"的核心论点，将文中的关键特性（稀疏表创建、查询、保存加载、入退特征）映射到图中具体层级，佐证Rec SDK既可独立嵌入自研模型，也具备完整技术栈能力。
