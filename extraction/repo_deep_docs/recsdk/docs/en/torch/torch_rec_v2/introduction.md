# Introduction

> 仓 `recsdk` · 路径 `docs/en/torch/torch_rec_v2/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/torch/torch_rec_v2/introduction.md

# 一体化深度解读: docs/en/torch/torch_rec_v2/introduction.md

---

## 【定位】

这篇文档是 **Rec SDK Torch 模块的概览 (Introduction)**, 在 MindX 推荐 SDK (华为昇腾) 体系下, 用一页篇幅同时回答两个问题——**"Rec SDK Torch 能做什么"** (基础训练、推荐特有能力、大规模稀疏表三大类功能 + 四项关键特性) 与**"Rec SDK Torch 的内部架构如何分层"** (API 层 / 功能层 / 加速层 / 存储层 / TorchRec-NPU 适配层), 定位为读者进入 Rec SDK Torch 之前的功能地图与架构导读。

---

## 【技术要点】

1. **训练形态**: 支持单节点单卡训练, 以及单节点多卡分布式训练; 模型需基于 Torch 开发 (原文: "single-node, single-card training and single-node, multi-card distributed training" / "Models developed based on Torch are supported")。

2. **底层存储抽象**: 推荐特有能力全部构建在**动态稀疏表 (dynamic sparse table)** 解决方案之上, 并基于 **HKV (hierarchical key-value, 高性能键值存储加速库)** 实现 hash 映射、动态稀疏表扩展与动态稀疏表算子。

3. **大规模稀疏表**: 支持 **行级 (row-wise) 分布式稀疏表分片 (sharding)**。

4. **Hash 映射机制**: Torch 原生 `nn.Embedding` 用于稠密 ID 查找, 但推荐场景特征多为离散 ID, 直接查找不便; Rec SDK Torch 基于动态稀疏表提供 hash 映射, **实时**将离散特征键映射到存储地址, 无需预先把 ID 转为连续值。

5. **行级分片 (Row-wise sharding)**: 当 embedding 被分片到不同表时, Rec SDK Torch **按行**对 embedding 进行划分, 并使用**基于模数 (modulo-based) 的 bucketing 策略**——以 ID 的余数 (remainder) 决定 embedding 在表中的 bucket 位置。

6. **动态扩展与淘汰 (Dynamic expansion and eviction)**: 稀疏表支持**弹性扩展**, 新特征加入时系统自动分配空间; 当空间使用率达到阈值, 算子内置的淘汰策略 (eviction policy) 自动清理低频不活跃特征。

7. **动态稀疏表算子**: Rec SDK Torch 提供深度优化的高性能自定义算子扩展 `dynamic_emb_extensions`, 相对原生 Torch 实现**显著提升训练吞吐**。

---

## 【关键机制与数据】

> 本节只整理原文中以文字形式陈述的原理/数据流/性能结论; 凡未给出具体数字之处一律不补全。

- **(原文) Hash 映射触发条件与目的**: 触发条件 = 推荐场景中绝大多数原始特征 ID 是离散的 (原文: "most raw feature IDs are discrete"); 目的 = 把离散键实时映射为存储地址, 使调用方不必做 ID→连续值的预处理 (原文: "maps discrete feature keys to storage addresses in real time, so you do not need to convert IDs to contiguous values in advance")。

- **(原文) 行级分片的数据流**: embeddings 被分片到不同表 → 按行切分 → 用 ID 的余数决定 bucket 位置 (原文: "partitions embeddings by row and uses a modulo-based bucketing strategy to determine the bucket position of an embedding in the table from the remainder of its ID")。即"ID → modulo → bucket"三段式路由。

- **(原文) 动态扩展与淘汰的闭环**: 新特征进入 → 系统自动分配空间 (弹性扩展) → 当空间使用率触发阈值 → 内置淘汰策略自动清理低频不活跃特征 → 保持存储高效利用 (原文: "The system automatically allocates space when new features are added. When space usage reaches the threshold, the built-in eviction policy of the operator automatically clears low-frequency inactive features to ensure efficient use of storage resources")。

- **(原文) 自定义算子的性能结论 (定性、无具体数值)**: `dynamic_emb_extensions` 经深度优化, **"Compared with the native Torch implementation, it greatly improves training throughput"**——文档只给出"显著提升"这一定性表述, 未给出加速比、QPS、latency 等数字。

- **(原文) 架构定位**: Rec SDK Torch 构建于 TorchRec、主流推荐框架、CANN 以及多种硬件/网络架构之上, 面向搜索/推荐/广告 (SRA) 模型训练, 通过高性能、简化的 API 让昇腾 AI 处理器获得高效训练能力。

---

## 【表格解读】

**Table 1** Modules in the architecture diagram — 逐字还原:

| Rec SDK Torch Module | Description |
|---|---|
| Recommendation API layer | Provides easy-to-use APIs to simplify customer access and support service growth. |
| Recommended function layer | Provides core capabilities to meet customer requirements. |
| Recommendation acceleration layer | Provides core components to build performance competitiveness and offer superb performance for the entire system. |
| Recommendation storage layer | Supports distributed storage of sparse tables. |
| Torchrec-npu | Ascend adaptation layer for open-source TorchRec. |

**逐行解读**:

1. **Recommendation API layer (推荐 API 层)**——是面向客户的"门面", 通过易用 API 降低接入门槛, 并支撑业务横向扩展 (原文: "simplify customer access and support service growth")。
2. **Recommended function layer (推荐功能层)**——封装核心能力, 满足客户的功能性需求; 文中四类关键特性 (hash 映射、行级分片、动态扩展淘汰、动态稀疏表算子) 在逻辑上归属此层。
3. **Recommendation acceleration layer (推荐加速层)**——性能竞争力来源, 提供让"整个系统"获得卓越性能的核心组件; `dynamic_emb_extensions` 等自定义算子逻辑上归属此层。
4. **Recommendation storage layer (推荐存储层)**——承接稀疏表的分布式存储职责, 是 HKV / 动态稀疏表等能力的物理承载层, 与"large-scale sparse table functions / row-wise sharding"直接对应。
5. **Torchrec-npu (TorchRec 的昇腾适配层)**——把开源 TorchRec 移植到昇腾平台的适配层, 说明整个 Rec SDK Torch 在生态上**站在开源 TorchRec 之上**而非另起炉灶, 适配工作集中在这一层。

> 备注: 图 1 (Software architecture) 在 markdown 中以图片占位符形式引用 (`![](../../figures/torch_rec_v1/software-architecture.png ...)`), 文本未包含可读的图层结构, 故本解读完全基于 Table 1 的分层描述。

---

## 【公式解读】

**原文无公式** (文档中既无 LaTeX 表达式, 也无伪代码/数学式定义; 唯一可视为"准公式"的描述是分片策略的一句话——"remainder of its ID" 决定 bucket 位置, 已在上文【关键机制与数据】中按自然语言处理)。

---

## 【关联】

> 用户给出的本文件内部链接信息为 **"(无)"**——即本文档末尾没有指向其他文档页的相对链接; 因此本节仅基于正文叙述建立模块/上下游关系图。

- **上游 / 依赖栈** (原文: "Built upon TorchRec, mainstream recommendation frameworks, CANN, and diverse hardware and network architectures"):
  - **TorchRec** → 经由 `torchrec-npu` 适配层接入
  - **主流推荐框架** → 与 TorchRec 并列, 作为 Rec SDK Torch 的上层输入
  - **CANN (昇腾异构计算架构)** → 提供底层算子与硬件抽象
  - **多种硬件 / 网络架构** → 提供部署承载

- **下游 / 解决的目标场景**: 搜索、推荐、广告 (SRA) 模型的训练。

- **Rec SDK Torch 内部 5 层闭环** (Table 1 自上而下):
  API 层 ← 调用 → 功能层 ← 调用 → 加速层 + 存储层 (横支撑) ← 依赖 → `torchrec-npu` (横接入开源生态)。

- **与文中其他特性的相互引用**:
  - "hash mapping" 与 "dynamic sparse table" 互为依托 (hash 映射基于动态稀疏表实现);
  - "row-wise sharding" 与 "distributed storage" 通过 Recommendation storage 层耦合;
  - "dynamic expansion and eviction" 与 "built-in eviction policy of the operator" 同时落在算子层与存储层, 体现跨层协作;
  - `dynamic_emb_extensions` 作为加速层产物, 是 "Compared with the native Torch implementation, it greatly improves training throughput" 的承担者。

- **同仓库其他文档** (原文未给出具体链接, 此处仅指出本文档所处路径暗示的同级文档): 路径 `docs/en/torch/torch_rec_v2/` 表明存在与 v2 Rec SDK Torch 相关的其它专题文档 (如安装、API 参考、迁移指南等), 但本文未提供任何指向它们的链接, 不在此臆造具体文档名。

---

## 【使用方法】

**原文未涉及**。

本文档为概览/导读 (Introduction/Overview/Software Architecture), 通篇未出现任何启用指令、配置项、环境变量、命令行示例、API 调用代码或安装步骤; 仅在文字层面给出能力清单与架构分层。涉及启用方式 (如如何初始化动态稀疏表、如何启用 `dynamic_emb_extensions`、如何配置 HKV 等) 需要参考 Rec SDK Torch 同目录下其它专题文档, 但本文未提供这些文档的链接或入口。

## 图文联合解读

- `software-architecture.png`: **图示解读：**

图分两层结构。上层为 **Rec SDK Torch**，自顶向下分四级：接口层、功能层、加速层、存储层；下层为运行底座，依次为 Torchrec-npu → PyTorch（深度学习框架）→ CANN → NPU 驱动与固件（运行环境）。色块图例区分四类组件。

**技术结论：** Rec SDK Torch 采用"分层解耦"架构，将推荐特性封装于上层，把 Torchrec 与 PyTorch 作为中间件，依托 CANN/NPU 完成硬件加速。

**与文档关系：** 直观印证文档"基于 Torch 的推荐专属能力"论点，存储层对应动态稀疏表/HKV，加速层对应分布式与算子优化，接口/功能层对应哈希映射等关键特性。
