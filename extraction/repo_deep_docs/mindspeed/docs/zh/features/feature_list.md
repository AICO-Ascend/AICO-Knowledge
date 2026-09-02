# 特性总览

> 仓 `mindspeed` · 路径 `docs/zh/features/feature_list.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/feature_list.md

# 深度解读：mindspeed 特性总览 (feature_list.md)

## 【定位】
本篇文档是 **MindSpeed Core 昇腾大模型加速库的特性索引/全景目录**，以分类表格的形式罗列了库中所有可用的并行策略、内存优化、通信优化、MoE、多模态等加速特性，并提供指向各特性详细文档的链接，作为用户查阅与功能选型的总入口。

---

## 【技术要点】

1. **九大特性分类体系**：原文将全部特性按"功能定位"划分为 9 大类 —— Megatron 特性（13 项）、并行策略特性（6 项）、内存优化特性（9 项）、亲和计算特性（1 项）、通信优化特性（2 项）、Mcore MoE 特性（8 项）、关键场景特性（1 项）、多模态特性（5 项）、其它特性（1 项），合计 **46 项特性**。
2. **Megatron 基础并行栈**：覆盖了数据并行、张量并行、流水并行（含虚拟流水线）、分布式优化器、序列并行、异步 DDP、权重更新通信隐藏、重计算、分布式权重、全分片并行（FSDP）、Transformer Engine、Multi-head Latent Attention（MLA）共 13 项基础能力。
3. **Ascend 增强的长序列并行**：在并行策略层提供了四条差异化路径 —— Ascend Ulysses、Ascend Ring Attention、Ascend Double Ring Attention、Ascend 混合长序列并行，外加 Ascend 自定义空操作层（noop-layers）与 Ascend DualPipeV。
4. **内存优化多元组合**：包含激活函数重计算、重计算流水线独立调度、Mask 归一、BF16 参数副本复用、swap_attention、Norm 重计算、Hccl Buffer 自适应、Swap Optimizer、Virtual Optimizer 共 9 项显存节省手段。
5. **MoE 专项优化族**：包括 Megatron MoE GMM、Allgather / Alltoall Dispatcher 性能优化、TP 拓展 EP、Allgather Dispatcher 分支通信隐藏、共享专家、1F1B Overlap、专家并行动态负载均衡（数参互寻）共 8 项。
6. **多模态与场景特性**：包含 Ascend PP 支持动态形状、PP 多参数传递、PP 多参数传递和动态形状、非对齐线性层、非对齐 Ulysses 长序列并行，以及 EOD Reset 训练场景、TFLOPS 计算等补充能力。

---

## 【关键机制与数据】

本文档为索引型文档，**原文未涉及具体工作原理、数据流或性能数据**。所有具体机制、性能收益、参数配置需跳转至各子特性文档查阅。文档本身的唯一"内容"是按类目组织的特性链接清单。

---

## 【表格解读】

原文核心为 **表 1 特性列表**，按"特征类型 / 特征名称"双列展示，用 `rowspan` 对同类别下多条特性进行合并。逐字还原并按类别解读如下：

| 特性类型 | 特性名称 | 类别解读 |
|---|---|---|
| **Megatron 特性**（13 项） | Megatron 数据并行 | 数据维度的并行基础 |
| | Megatron 张量并行 | 模型内层切分 |
| | Megatron 流水并行 | 模型按层切分到多卡 |
| | Megatron 虚拟流水线并行 | 流水并行的细粒度变体 |
| | Megatron 分布式优化器 | 优化器状态分片 |
| | Megatron 序列并行 | 与 TP 配套的序列维切分 |
| | Megatron 异步 DDP | 数据并行通信异步化 |
| | Megatron 权重更新通信隐藏 | 减少参数广播阻塞 |
| | Megatron 重计算 | 用计算换显存 |
| | Megatron 分布式权重 | dist_ckpt 权重分片 |
| | Megatron 全分片并行 | 自定义 FSDP 实现 |
| | Megatron Transformer Engine | 高性能 Transformer 算子栈 |
| | Megatron Multi-head Latent Attention | MLA 注意力实现 |
| **并行策略特性**（6 项） | Ascend Ulysses 长序列并行 | 序列维 all-to-all 切分 |
| | Ascend Ring Attention 长序列并行 | 环形通信长序列方案 |
| | Ascend Double Ring Attention 长序列并行 | 双环通信变体 |
| | Ascend 混合长序列并行 | 多种 CP 方案融合 |
| | Ascend 自定义空操作层 | noop-layers 占位层 |
| | Ascend DualPipeV | 改进型流水调度 |
| **内存优化特性**（9 项） | Ascend 激活函数重计算 | 选择性重算激活 |
| | Ascend 重计算流水线独立调度 | 重算与流水解耦 |
| | Ascend Mask 归一 | generate-mask 显存优化 |
| | Ascend BF16 参数副本复用 | 降低参数副本显存 |
| | Ascend swap_attention | 注意力显存换出 |
| | Ascend Norm 重计算 | Norm 层重算 |
| | Ascend Hccl Buffer 自适应 | 通信缓冲动态调整 |
| | Ascend Swap Optimizer | 优化器状态换出 |
| | Virtual Optimizer | 虚拟优化器 |
| **亲和计算特性**（1 项） | Ascend Flash Attention | 算子级 flash 注意力 |
| **通信优化特性**（2 项） | Ascend Gloo 存档落盘优化 | 替代 gloo 通信栈 |
| | Ascend 高维张量并行 | 2D TP 拓扑 |
| **Mcore MoE 特性**（8 项） | Ascend Megatron MoE GMM | MoE 通用矩阵乘 |
| | Ascend Megatron MoE Allgather Dispatcher 性能优化 | AG 派发加速 |
| | Ascend Megatron MoE Alltoall Dispatcher 性能优化 | A2A 派发加速 |
| | Ascend Megatron MoE TP 拓展 EP | TP 维度扩展专家并行 |
| | Megatron MoE Allgather Dispatcher 分支通信隐藏优化 | 通信与计算重叠 |
| | Ascend 共享专家 | 共享专家结构 |
| | 1F1B Overlap | 1F1B 流水计算通信重叠 |
| | 专家并行动态负载均衡（数参互寻） | balanced_moe 动态均衡 |
| **关键场景特性**（1 项） | Ascend EOD Reset 训练场景 | 长文 EOD 位置重置 |
| **多模态特性**（5 项） | Ascend PP 支持动态形状 | variable_seq_lengths |
| | Ascend PP 支持多参数传递 | multi_parameter_pipeline |
| | Ascend PP 支持多参数传递和动态形状 | 上述两者组合 |
| | Ascend 非对齐线性层 | unaligned_linear |
| | Ascend 非对齐 Ulysses 长序列并行 | 非对齐 CP 切分 |
| **其它特性**（1 项） | Ascend TFLOPS 计算 | 算力估算工具 |

> **表格结构说明**：原文使用 HTML 表格，每个 `rowspan` 单元格将多行特性"归口"到同一类目下，共形成 9 个 `rowspan` 分组（13 / 6 / 9 / 1 / 2 / 8 / 1 / 5 / 1），合计 46 个特性条目，每条均以超链接指向 `../features/...` 路径下的子文档。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档为 **目录型索引**，不展开任何特性的具体内容，但与仓库中以下结构存在强关联：

- **子文档网络**：表格中每条特性均链接到 `docs/zh/features/` 或 `docs/zh/features/megatron_moe/` 下的独立 markdown 文档（共 46 个目标文件），是整个特性文档体系的"根节点"。
- **功能正交与组合关系**（从类目划分可推断）：
  - *Megatron 基础并行*（13 项）是 *并行策略特性*（6 项）和 *通信优化特性*（2 项）的底层依赖；
  - *内存优化特性*（9 项）与 *并行策略*、*MoE 特性*常组合使用，以缓解大模型/长序列/MoE 带来的显存压力；
  - *Mcore MoE 特性*（8 项）依赖 *Megatron 张量并行*、*专家并行*、*序列并行* 等基础设施；
  - *多模态特性*（5 项）建立在 *PP 流水并行* 之上，扩展其对动态形状/多参数的承载能力；
  - *亲和计算特性*（Flash Attention）作为算子级加速，可被多种注意力实现（MLA、Ulysses CP、Ring CP）调用；
  - *关键场景特性*（EOD Reset）与 *其它特性*（TFLOPS 计算）作为辅助工具，独立于并行/内存体系。
- **仓库根目录关联**：本文档位于 `docs/zh/features/feature_list.md`，是中文特性手册的总入口；用户通常从此页跳转至具体特性详情。

---

## 【使用方法】

原文未涉及具体的启用方式、配置项或命令 —— 文档本身仅作特性清单的展示与导航入口。各项特性的实际启用方法、命令行参数、环境变量等需要打开对应的子特性文档（例如 `tensor-parallel.md`、`flash-attention.md`、`megatron-moe-gmm.md` 等）查阅。
