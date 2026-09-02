# moe_params

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/moe_params.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/moe_params.md

# xllm「EP并行」feature文档深度解读

---

## 【定位】

本文档描述了 xllm 在部署 DeepSeek-R1 671B 等大规模 MoE（Mixture of Experts）模型时，通过 **Expert Parallelism（EP 专家并行）** 解决传统分布式部署中显存利用率低、通信开销大、硬件成本高等瓶颈问题的并行方案，包含 `dp_size`、`ep_size`、`expert_parallel_degree` 三个核心参数及两种 EP 级别（level1/level2）的执行流程。

---

## 【技术要点】

1. **三种并行维度协同配置**：通过 `dp_size`（Attention 部分 DP 规模，默认 1，2 的指数倍）、`ep_size`（MoE 部分 EP 规模，默认 1，2 的指数倍）、`expert_parallel_degree`（EP 等级开关，0/1/2）三个参数联合控制并行拓扑；当 `dp_size` 或 `ep_size` 不等于卡数时，dp 组内自动退化为 **tp 并行**。

2. **EP level1（默认开启）**：Attention 与 MoE 两阶段计算完成后，通过 **All Gather** 全卡广播方式将数据发送至下一阶段；attn 与 moe 通信量为全卡广播级别。

3. **EP level2（仅当 ep_size 等于卡数时开启）**：将 `expert_parallel_degree` 设为 2，attn 与 moe 部分之间通讯变为 **All-to-All**，只向需要的卡发送目标 token/Expert 数据，**降低通讯量与通讯开销**。

4. **MLA 自动启用机制**：支持 MLA（Multi-head Latent Attention）的模型**自动开启 MLA**，无需手动配置。

5. **显存放大原理**（基于等资源条件）：单卡 Expert 数越少 → 可分配给 KV Cache 的显存越多 → 可缓存 token 数越多；TP Size 越小 → MLA 下冗余 KV Cache 越少 → 可缓存 token 数越多。

6. **计算集中化收益**：大规模 EP 并行可将**同一个 Expert 的 token 计算集中到同一设备**，提高硬件利用率。

---

## 【关键机制与数据】

- **原文**：DeepSeek-R1 671B 参数规模模型部署时，传统分布式部署面临"显存利用率低、通信开销大、硬件成本高昂"等核心瓶颈。
- **原文**：EP 并行带来三方面收益——Expert 减少→KV Cache 显存增多；TP Size 减小→MLA 冗余 KV Cache 减少；Expert 计算集中化→硬件利用率提升。
- **EP level1 通讯模式**：All Gather，全卡广播（attn 部分 dp32tp2、moe 部分 ep32tp2 的 64 卡部署示例，原文以架构图 `figures/moe_eplevel1.jpg` 说明）。
- **EP level2 通讯模式**：All-to-All，点对点按需发送（64 卡部署示例，原文以架构图 `figures/moe_eplevel2.jpg` 说明）。
- **参数约束**：`dp_size`、`ep_size` 必须为 2 的指数倍；`expert_parallel_degree=2` 的前置条件是 `ep_size == 卡数`。
- **关键数据点（原文）**：64 卡部署时 attn 部分采用 dp32tp2、moe 部分采用 ep32tp2。

---

## 【表格解读】

**原文无表格**。原文以三个并列要点的形式说明 EP 并行背景，三个加号开头的段落说明参数定义，两段文字加架构图说明 level1/level2 流程，未以表格形式呈现对比。

---

## 【公式解读】

**原文无公式**。文档中涉及的所有参数语义与流程均以文字 + 架构图（`moe_eplevel1.jpg`、`moe_eplevel2.jpg`）方式描述，未给出任何数学公式或伪代码表达式。

---

## 【关联】

原文内部链接信息为"无"，但根据文档语义可关联如下：

- **上游/同类特性**：与 **TP（Tensor Parallel，张量并行）**、`dp_size` 配套使用，当 `dp_size`/`ep_size` 不等于卡数时组内自动退化为 TP 并行，属于并行拓扑的协同配置。
- **依赖特性**：与 **MLA（Multi-head Latent Attention）** 强耦合——MLA 模型自动启用 MLA 优化，且 MLA 的 KV Cache 冗余特性是 EP 收益的关键来源之一。
- **应用场景**：专门针对 **DeepSeek-R1 671B** 等超大规模 MoE 模型的部署场景设计，是该类模型在多卡环境下的推荐并行策略。
- **关联模块**：本文档位于 `docs/src/content/docs/zh/features/moe_params.md`，从路径与命名可推断属于"MoE 参数配置"特性簇，与 xllm 中 MoE 推理引擎、Attention 计算模块、通信层（All Gather / All-to-All）紧密相关。
- **架构图引用**：依赖 `figures/moe_eplevel1.jpg` 与 `figures/moe_eplevel2.jpg` 两张流程图辅助说明 level1/level2 的执行流。

---

## 【使用方法】

**参数配置方式**（原文直接给出）：

| 参数 | 取值规则 | 说明 |
|------|---------|------|
| `dp_size` | 2 的指数倍，默认 1 | Attention 部分的 DP 规模；当不等于卡数时 dp 组内为 tp 并行 |
| `ep_size` | 2 的指数倍，默认 1 | MoE 部分的 EP 规模；当不等于卡数时 dp 组内为 tp 并行 |
| `expert_parallel_degree` | 0/1/2 | 0 = 不开启 EP；1 = 开启 EP（默认），即 ep level1；2 = 开启 ep level2，**前提是 ep_size 等于卡数** |

**MLA 启用**：支持 MLA 的模型**自动开启 MLA**，无需手动配置。

**典型配置示例**（原文给出）：64 卡部署时采用 attn 部分 dp32tp2、moe 部分 ep32tp2。

**关于启用命令/启动脚本/API 调用方式**：原文未涉及具体的启动命令、环境变量或代码调用方式，仅给出参数语义。

## 图文联合解读

- `moe_eplevel1.jpg`: **图文联合解读：**

**1）图像内容**：展示EP level1下64卡（DP Rank #0与#31为例）执行流程。顶层Schedule受KVCache Block Manager调度；每卡依次为EMB→MLA(TP2)→MLP(TP2)（3X共享专家层）→MLA(TP2)（Attention阶段，DP32+TP2），再经All Gather全卡通信后进入8+1+1 MoE层（EP32+TP2，58X路由专家），MoE后再一次All Gather。

**2）技术结论**：EP level1在Attn与MoE之间及MoE之后均使用All Gather，将数据同步到全部64卡，通信量与卡数成正比，开销较大。

**3）与文档关系**：图示佐证文档论点——level1默认采用All Gather作为attn→moe衔接；正因全量广播开销大，才需引入level2的All2All向文档所述"只向需要的卡发送数据，降低通讯量与通讯开销"。
- `moe_eplevel2.jpg`: **图文联合解读：**

1）**图示内容**：展示64卡NPU（#0/#1/#62/#63为代表）的EP并行架构。顶部Schedule模块受KVCache Block Manager调度；每卡依次执行EMB→ATTN层（DP64,TP1，含MLA+MLP，重复3次）→ALL2LL通信→58层MLA+MoE（EP64,TP1，每卡承载4+1+1个专家）→ALL2LL通信。

2）**技术结论**：当ep_size等于卡数（64）时开启EP level2，ATTN与MoE之间采用ALL2ALL通信，仅向目标专家所在卡发送token，避免全卡广播，显著降低通信量与开销。

3）**与文档关系**：图示正是文档"方案设计"中ep level2方案的实例化，印证"ep_size=卡数时通信由All Gather升级为ALL2ALL"的论点，支撑"大规模EP并行提升硬件利用率、降低通信成本"的核心动机。
