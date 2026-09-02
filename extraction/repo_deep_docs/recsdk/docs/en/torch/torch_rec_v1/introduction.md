# Introduction

> 仓 `recsdk` · 路径 `docs/en/torch/torch_rec_v1/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/torch/torch_rec_v1/introduction.md

# docs/en/torch/torch_rec_v1/introduction.md 一体化深度解读

---

## 【定位】

这篇文档是华为昇腾 Rec SDK 中 **Rec SDK Torch 模块的总体概览 (Overview)**：在简要介绍其面向搜索/推荐/广告 (SRA) 模型训练所需的基础训练能力、推荐专用能力与大规模稀疏表能力的基础上，分项阐述五大关键特性 (hash mapping / EBC lookup / row-wise sharding / pipeline lookup / lookup fusion operator)、软件架构的分层组成，以及所支持的硬件与操作系统版本。它解决的是"Rec SDK Torch 能做什么、由哪些模块构成、跑在什么硬件上"的总览认知问题。

---

## 【技术要点】

1. **训练能力范围 (Basic Model Training)**
   - 原文: "Rec SDK supports single-node, single-card training and single-node, multi-card distributed training."
   - 原文: "Models developed based on Torch are supported."
   - 即训练拓扑限定为 **单节点单卡** 与 **单节点多卡分布式**，模型侧需基于 Torch 开发。

2. **推荐专用能力 (Recommendation-specific functions)**
   - 原文: "Based on the sparse table solution, Rec SDK Torch provides the essential functions required for recommendation, such as non-affine operator offloading and hash mapping."
   - 核心是建立在 **稀疏表 (sparse table) 解决方案** 之上的 **非仿算子卸载 (non-affine operator offloading)** 与 **hash mapping**。

3. **大规模稀疏表 (Large-scale Sparse Table)**
   - 原文: "Rec SDK Torch supports row-wise distributed sparse table sharding."
   - 采用 **按行 (row-wise) 分布式稀疏表分片**。

4. **Hash Mapping 机制**
   - 原文: "Torch provides `nn.Embedding` for dense ID lookup."
   - 原文: "Rec SDK Torch provides hash mapping to map discrete IDs to embedding table row indexes without requiring users to convert IDs in advance."
   - 替代 `nn.Embedding` 的"密集 ID 直查"模式，将 **离散原始特征 ID** 直接映射到 **embedding 表的行索引**，省去用户预转换。

5. **EBC Lookup**
   - 原文: "This corresponds to the native Torch `nn.EmbeddingBag` function."
   - 原文: "For multiple specified IDs, Rec SDK Torch performs pooling by summing or averaging during lookup."
   - 对应原生 `nn.EmbeddingBag`，在查表过程中对多个 ID 进行 **sum 池化** 或 **average 池化**。

6. **Row-wise Sharding**
   - 原文: "Rec SDK Torch partitions embeddings by row and uses a modulo-based bucketing strategy to determine the bucket position of an embedding in the table from the remainder of its ID."
   - 分片策略为 **按行切分 embedding**，并用 **基于模运算 (modulo) 的 bucketing 策略**，以 **ID 的余数** 决定该 embedding 在表中的桶位置。

7. **Pipeline Lookup**
   - 原文: "A Rec SDK Torch lookup task consists of multiple subtasks, including communication, CPU computation, and NPU computation."
   - 原文: "Rec SDK Torch provides a pipeline lookup method so that these subtasks can run in parallel and fully use hardware computing power."
   - 将一次 lookup 拆分为 **communication / CPU computation / NPU computation** 三类子任务，并 **并行执行** 以榨取硬件算力。

8. **Lookup Fusion Operator**
   - 原文: "Rec SDK Torch provides lookup operators with fused gradient calculation and optimizer logic to improve lookup performance."
   - 将 **梯度计算** 与 **优化器逻辑** 融合进 lookup 算子本身，以提升查表性能。

9. **软件架构构建栈**
   - 原文: "Built upon TorchRec, mainstream recommendation frameworks, CANN, and diverse hardware and network architectures..."
   - 下层依赖 **TorchRec + 主流推荐框架 + CANN + 多样化硬件/网络**；上层提供 **high-performance, streamlined APIs**。

---

## 【关键机制与数据】

### 工作原理 (原文:)

1. **Hash Mapping 工作原理**
   - 原文: "In recommendation scenarios, most raw feature IDs are discrete, which makes direct lookup inconvenient."
   - 原文: "A common practice is to convert discrete IDs to table row indexes."
   - 原文: "Rec SDK Torch provides hash mapping to map discrete IDs to embedding table row indexes without requiring users to convert IDs in advance."
   - 即在 Rec SDK Torch 内部完成 **"离散 ID → 行索引"** 的映射，用户无需预处理。

2. **EBC Lookup 工作原理**
   - 原文: "This corresponds to the native Torch `nn.EmbeddingBag` function. For multiple specified IDs, Rec SDK Torch performs pooling by summing or averaging during lookup."
   - 与 `nn.EmbeddingBag` 语义一致，对 **多个指定 ID** 在 lookup 阶段直接产出 **sum/average** 池化结果。

3. **Row-wise Sharding 工作原理**
   - 原文: "...partitions embeddings by row and uses a modulo-based bucketing strategy to determine the bucket position of an embedding in the table from the remainder of its ID."
   - 物理上按行切分；路由上以 **ID % bucket_count** 的余数决定 embedding 落入哪个桶/分片。

4. **Pipeline Lookup 工作原理**
   - 原文: "...subtasks, including communication, CPU computation, and NPU computation."
   - 原文: "...these subtasks can run in parallel..."
   - 单一 lookup 任务被分解为 **communication / CPU computation / NPU computation** 三个子任务，三者 **并行** 运行以复用硬件资源。

5. **Lookup Fusion 工作原理**
   - 原文: "...fused gradient calculation and optimizer logic to improve lookup performance."
   - 在 lookup 算子内集成 **梯度计算 + 优化器逻辑**，避免多次往返/中间态。

6. **软件架构运行原理**
   - 原文: "...enabling Ascend AI Processors to achieve highly efficient training for search, recommendation, and advertising models."
   - Rec SDK Torch 在 **昇腾 AI 处理器** 上实现对 SRA 模型的高效训练。

### 性能数据

- **原文未提供任何量化性能数据 (如 QPS、加速比、时延、吞吐等)。** 文档仅以定性表述提及 "improve lookup performance"、"highly efficient training"、"superb performance"，未给出具体数字。

---

## 【表格解读】

### 表 1 (Table 1): Modules in the architecture diagram

| Rec SDK Torch Module | Description |
|---|---|
| Recommendation API layer | Provides easy-to-use APIs to simplify customer access and support service growth. |
| Recommended function layer | Provides core capabilities to meet customer requirements. |
| Recommendation acceleration layer | Provides core components to build performance competitiveness and offer superb performance for the entire system. |
| Recommendation storage layer | Supports distributed storage of sparse tables. |
| Torchrec-npu | Ascend adaptation layer for open-source TorchRec. |

**逐行解读：**

- **Recommendation API layer** — 最靠近用户的一层，定位是"易用 API"，目标是 **降低客户接入门槛、支持业务增长**。
- **Recommended function layer** — 提供面向客户需求的核心能力（如 hash mapping、EBC lookup 等关键特性应归于此层）。
- **Recommendation acceleration layer** — 提供 **核心性能组件**，为整个系统提供 **性能竞争力** 与 **卓越性能 (superb performance)**，对应 lookup fusion、pipeline lookup 等加速机制。
- **Recommendation storage layer** — 负责 **稀疏表的分布式存储**，对应 row-wise sharding 等大规模稀疏表能力。
- **Torchrec-npu** — **开源 TorchRec 的昇腾 (Ascend) 适配层**，是把 TorchRec 生态接到昇腾/CANN 上的桥梁；与架构图标题"Built upon TorchRec"对应。

> 五层自上而下构成 **"对外 API → 业务功能 → 性能加速 → 存储 → 昇腾适配"** 的栈式结构。

---

### 表 2 (Table 2): Supported products (原文 HTML 含 rowspan，逐字还原如下)

<table border="1">
  <tr>
    <th>Product</th>
    <th>Architecture</th>
    <th>OS Version</th>
  </tr>
  <tr>
    <td rowspan="2"><p>Atlas 800T A2 training server</p><p>Atlas 200T A2 Box16 heterogeneous subrack</p></td>
    <td>x86_64</td>
    <td>Debian version: 12<br>CentOS version: 7.6</td>
  </tr>
  <tr>
    <td>Arm</td>
    <td>openEuler version: 22.03</td>
  </tr>
</table>

**逐行解读：**

- **产品列 (Product)**：通过 `rowspan="2"` 跨两行，明确两款产品 **共享同一组支持矩阵**，它们是：
  - **Atlas 800T A2 训练服务器**
  - **Atlas 200T A2 Box16 异构子框**
- **第一行 (Architecture = x86_64)**：
  - **Debian version: 12**
  - **CentOS version: 7.6**
  - 即在 x86_64 架构下支持 Debian 12 与 CentOS 7.6 两种 OS。
- **第二行 (Architecture = Arm)**：
  - **openEuler version: 22.03**
  - 在 Arm 架构下仅支持 openEuler 22.03。
- **覆盖矩阵总结**：
  - x86_64 × {Debian 12, CentOS 7.6} 共 2 种组合；
  - Arm × {openEuler 22.03} 共 1 种组合；
  - 同一产品型号 (如 Atlas 800T A2) 在 x86_64 与 Arm 两种架构下均可运行，但 **OS 选项因架构而异**。

---

## 【公式解读】

**原文无公式。** 文档正文未出现任何数学公式、伪代码公式或 LaTeX 表达式；其技术机制 (modulo bucketing、sum/average pooling、fusion 等) 全部以自然语言描述，未给出形式化表达式。

---

## 【关联】

文末内部链接一栏标注为 **(无)**，因此本文未提供跳转链接。但文档内部已通过以下语义关联指向其他特性/模块，可作为理解上下游关系的依据：

- **关键特性 ↔ 软件架构层映射**：
  - *Hash mapping / EBC lookup* 归位于 **Recommended function layer (Table 1)**；
  - *Pipeline lookup / Lookup fusion operator* 归位于 **Recommendation acceleration layer**；
  - *Row-wise sharding* 归位于 **Recommendation storage layer**；
  - *Torchrec-npu* 与 *torch.nn.Embedding / torch.nn.EmbeddingBag* 直接对应，是其昇腾适配入口。
- **能力栈依赖**：Rec SDK Torch → Built upon → **TorchRec + 主流推荐框架 + CANN + 多样硬件/网络**，最终在 **昇腾 AI 处理器** 上交付 SRA 训练。
- **功能定位上下文**：上层是 *Recommendation API layer* (面向用户)，下层是 *Torchrec-npu* (面向开源 TorchRec 的适配)；中间三层依次封装 **业务功能 → 性能加速 → 存储**。
- **运行平台上下文**：Table 2 列出的 **Atlas 800T A2 训练服务器 / Atlas 200T A2 Box16 异构子框** 即为 Rec SDK Torch 可运行的硬件载体；与 "diverse hardware and network architectures" 文案呼应。

> 注：原文未提供文档内部的进一步交叉链接 (如跳转至 hash mapping / pipeline lookup 等子文档的具体 URL)。

---

## 【使用方法】

**原文未涉及具体的启用命令、配置文件路径、环境变量或启动参数。** 本篇为 overview 性质，未列出：

- 任何安装/启动命令 (无 `pip install` / `bash` / 配置文件路径)；
- 任何 API 调用样例或代码片段；
- 任何环境变量、模型配置项或超参默认值；
- 任何与 Table 2 硬件/OS 配套的部署步骤。

上述具体使用方法需查阅同目录下的其他专题文档 (如各特性的单独说明页) 才能获取，本 overview 文档本身不予覆盖。

## 图文联合解读

- `software-architecture.png`: **图文联合解读：**

图示呈现Rec SDK Torch的分层架构：上层为四层蓝色模块（接口层/功能层/加速层/存储层），下层依次为Torchrec-npu、PyTorch、CANN及NPU驱动与固件。

**与文档关系**：该图论证了Rec SDK Torch基于Torchrec-npu与PyTorch向上封装推荐专用能力、向底层CANN/NPU异构栈下沉的端到端架构，印证了文档所述"基于稀疏表方案提供hash映射、行级切分、EBC lookup、流水线lookup及融合算子"等关键特性的层次化承载关系。
