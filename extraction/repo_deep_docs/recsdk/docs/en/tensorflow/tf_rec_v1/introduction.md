# Introduction

> 仓 `recsdk` · 路径 `docs/en/tensorflow/tf_rec_v1/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/tensorflow/tf_rec_v1/introduction.md

# 深度解读：Rec SDK TensorFlow Overview

## 【定位】

本文档是 Rec SDK TensorFlow（华为昇腾 MindX 推荐 SDK 中 TensorFlow 训练框架）的总览性介绍文档，向读者呈现该框架的核心能力、关键特性、软件架构分层以及所支持的硬件与操作系统版本，是了解整个 SDK 能力边界与功能入口的首页文档。

---

## 【技术要点】

1. **训练部署形态**：支持单机单卡、单机多卡、以及多机多卡分布式训练，并兼容原生 TensorFlow 模型开发模式。
2. **推荐专用能力**：基于稀疏表方案，提供特征存取（saving/loading）、特征准入（admission）、特征淘汰（eviction）、以及非亲和算子拆分（non-affinity operator splitting）等核心能力。
3. **大规模稀疏表存储**：采用"加速卡内存 + 主机内存 + 主机磁盘"多级存储，单表容量可超过 **10 TB**，并支持存储与动态伸缩（dynamic scaling）。
4. **关键特性清单**：动态扩容（Dynamic Expansion）、动态 Shape（Dynamic Shapes）、自动图修改（Automatic Graph Modification）、特征准入与淘汰（Feature Admission and Eviction）、Hot_Embedding、自定义 WarmStart（Customized WarmStart）。
5. **性能/精度工具链**：性能工具支持 Host 侧 profiling 数据采集、Host/Device profiling 数据融合、耗时排序与可视化；精度工具支持端到端算子级精度比对。
6. **约束与可用性**：
   - 自定义 WarmStart 仅在 **TensorFlow 1.15.0** 的 On-chip memory 与 DDR 模式下可用；
   - 增量模型保存与加载仅在 On-chip memory / DDR / SSD 三种存储模式 + Estimator 模式下可用，不支持 `train_and_evaluate`，且**不能与特征准入/淘汰同时启用**；
   - 准入功能可单独开启，或与淘汰同时开启，**不支持单独启用淘汰**；
   - 动态扩容启用时，需使用 SGDByAddr、LazyAdamByAddress、AdagradByAddress 等 ByAddress 系列优化器；
   - 自动图修改仅能在 TensorFlow 默认图中执行，不支持用户自定义 `tf.Graph`。

---

## 【关键机制与数据】

### 动态扩容机制
- 原文：原生 TensorFlow 通过固定 API 创建 variable，embedding 表大小一旦设定即不可增减，**会造成 NPU 内存浪费或空间不足**。
- 原文：On-chip memory 同时支持动态与静态扩容（**训练过程中 device 内存用量逐步增长**）；DDR/SSD 模式仅支持动态扩容（**host 内存/磁盘用量增长，device 内存保持恒定**）。
- 适用场景：推荐系统中多个稀疏表大小常不可预测。

### 动态 Shape
- 原文：Rec SDK TensorFlow 训练框架中，**算子的输入与输出均为动态 Shape**，Shape 依赖于 TensorFlow 的具体算子。

### 自动图修改（Automatic Graph Modification）
- 原文：通过修改 TensorFlow 计算图，**训练脚本无需创建 FeatureSpec，也无需显式调用嵌入读 key 算子**。
- 约束：仅能在 TF 默认图中使用。

### 特征准入与淘汰
- 原文：低频特征"对训练无帮助、造成内存浪费、易过拟合"，准入功能用于过滤此类特征；淘汰支持 **全局步数间隔（global step intervals）** 与 **时间间隔（time intervals）** 两类触发条件。
- 准入/淘汰可在 FeatureSpec 模式或自动图修改模式下启用。

### Hot_Embedding
- 原文：在 key 重复率较高的推荐场景中，缓存"频繁访问的 key"以加速表查找。

### 自定义 WarmStart（Customized WarmStart）
- 原文：在原生 Estimator WarmStart（仅从单一路径加载参数）基础上扩展为：**多路径 WarmStart**，可从多个模型路径加载局部或全量参数，用于多模型迁移学习。
- 原文：当前 **embedding 表的名字映射（name mapping）尚未支持**。

### 增量模型保存与加载
- 原文：用于流式训练场景（CTR 模型持续产生日志），按间隔保存全量或增量模型；仅保存稀疏参数的增量更新可"显著降低频繁 checkpoint 开销"，用最新全量 checkpoint + 一系列增量 checkpoint 即可恢复。

### PCIe through
- 原文：利用 PCIe-through 流水线式并行 swap（in/out）+ 共享内存进行数据交换，提升 host 与 device 之间的吞吐。

### 软件架构（4 层，原文 Table 1）
1. API 层：易用 API，简化客户接入；
2. 推荐功能层：核心能力；
3. 推荐加速层：构建性能竞争力的核心组件；
4. 稀疏存储层：支撑 **10 TB 以上** 大规模稀疏表存储。

### 硬件/系统覆盖（原文 Table 2）
- Atlas 800T A2 / Atlas 200T A2 Box16：Arm + x86_64，CentOS 7.6 / openEuler 22.03 / Ubuntu 20.04；
- Atlas 900 A3 SuperPoD：Arm，openEuler 22.03。

---

## 【表格解读】

### 表 1：软件架构分层（Modules in the architecture diagram）

| Rec SDK TensorFlow Module | Description |
|---|---|
| API layer | Provides easy-to-use APIs to simplify customer access and support service growth. |
| Recommended function layer | Provides core capabilities to meet customer requirements. |
| Recommendation acceleration layer | Provides core components to build performance competitiveness and offer superb performance for the entire system. |
| Sparse storage layer | Supports large-scale sparse table storage of more than 10 TB. |

**逐行解读**：
- **API layer（API 层）**：面向客户的接口入口层，强调"易用"与"服务扩展能力"，即业务开发者通过该层调用底层能力。
- **Recommended function layer（推荐功能层）**：承载前述所有特征级能力（特征存取、准入/淘汰、稀疏表查找、Hot_Embedding、动态 Shape 等），是业务逻辑直接对应的核心层。
- **Recommendation acceleration layer（推荐加速层）**：性能竞争力的来源，对应文档提到的 PCIe through、多级存储下的 swap in/out 流水线、自定义 WarmStart、稀疏表算子等性能优化组件。
- **Sparse storage layer（稀疏存储层）**：底层存储抽象，关键数字为 **>10 TB**，意味着该层同时覆盖加速卡内存（On-chip / DDR / SSD 多级）与单表可扩展能力。

### 表 2：支持产品（Supported products）

| Product | Architecture | OS Version |
|---|---|---|
| Atlas 800T A2 training server<br>Atlas 200T A2 Box16 heterogeneous subrack | Arm<br>x86_64 | CentOS 7.6<br>openEuler 22.03<br>Ubuntu 20.04 |
| Atlas 900 A3 SuperPoD | Arm | openEuler 22.03 |

**逐行解读**：
- **第 1 行（Atlas 800T A2 / Atlas 200T A2 Box16）**：同一硬件家族共享架构与 OS 矩阵；架构同时覆盖 **Arm 和 x86_64** 两套主流 CPU 指令集；操作系统同时覆盖 CentOS 7.6、openEuler 22.03、Ubuntu 20.04，是该 SDK 兼容性最广的硬件承载。
- **第 2 行（Atlas 900 A3 SuperPoD）**：仅支持 **Arm 架构 + openEuler 22.03**，反映 SuperPoD 这类超节点场景仅在昇腾自有 ARM + openEuler 组合下完成验证。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档作为总览页面，关键特性的实现细节通过文末 4 个内部链接指向 `appendix.md` 中的同名章节：

1. **`appendix.md#on-chip-memory-dynamic-expansion-mode`** ← 对应「Dynamic expansion」特性。该链接解释了当 On-chip memory 模式下启用动态扩容时的具体工作流程，与本节提到的"device 内存逐步增长"行为直接对应。
2. **`appendix.md#dynamic-shapes`** ← 对应「Dynamic shapes」特性。该链接给出 Rec SDK TensorFlow 训练框架中算子输入/输出均为动态 Shape 的具体实现说明。
3. **`appendix.md#automatic-graph-modification`** ← 对应「Automatic graph modification」特性。该链接解释如何在不显式调用 FeatureSpec / 读 key 算子的情况下完成训练，是与 FeatureSpec 模式并列的另一条上手路径。
4. **`appendix.md#feature-admission-and-eviction`** ← 对应「Feature admission and eviction」特性。该链接详细描述低频特征过滤与按 global step / 时间间隔触发的淘汰机制。

**上下游关系**：
- 上游：文档开篇提及"Built upon mainstream recommendation frameworks, CANN, and diverse hardware and network architectures"，即 Rec SDK TensorFlow 构建于主流推荐框架 + CANN（昇腾异构计算架构） + 多样硬件与网络拓扑之上。
- 横向：四个特性之间存在组合约束关系——**特征准入/淘汰 与 增量模型保存/加载 互斥**；**动态扩容 与 ByAddress 系列优化器绑定**。
- 下游：API layer（Table 1 第 1 层）面向业务开发者，封装下层推荐功能/加速/稀疏存储三大底层模块；同时上文"Overview"中提到"single-server multi-card / multi-server multi-card" 训练能力，进一步与 CANN 中的 HCCL 集合通信层对接。

---

## 【使用方法】

原文未涉及具体的启用命令、配置项或 API 调用代码。本文档为 Overview 章节，仅描述"是什么"以及关键特性的存在性，不展示"如何开启"。

具体的开启方式、配置项及代码示例需查阅以下章节：
- [Dynamic Expansion Mode on On-chip Memory](appendix.md#on-chip-memory-dynamic-expansion-mode)
- [Dynamic Shapes](appendix.md#dynamic-shapes)
- [Automatic Graph Modification](appendix.md#automatic-graph-modification)
- [Feature Admission and Eviction](appendix.md#feature-admission-and-eviction)

以及位于 `https://gitcode.com/Ascend/RecSDK/tree/develop/cust_op/ascendc_op/ai_core_op/cust_op_by_addr/v220` 的 **稀疏表算子样例与 README**（与动态扩容特性的 ByAddress 系列算子配套使用）。

## 图文联合解读

- `4-mxRec-architecture.png`: **图示解读**

1) **结构**：自上而下分层架构——Rec SDK（接口层、推荐功能层、推荐加速层、稀疏存储层）→ TensorFlow/MindSpore → CANN → Ascend 硬件。颜色区分三类：Rec SDK、深度学习框架、基础运行环境。

2) **技术结论**：Rec SDK 作为适配层，依托 TF/MindSpore 框架与 CANN 异构计算栈，完整覆盖推荐场景接口、算法、加速与稀疏存储。

3) **与文档关系**：图示对应文中"基于 TensorFlow 的模型开发、稀疏表方案、多级存储、推荐专属功能"四大能力，揭示其分层封装、向下调用 Ascend 算力的整体设计。
