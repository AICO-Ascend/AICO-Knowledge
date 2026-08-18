# Kimi Linear — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Kimi Linear: An Expressive, Efficient Attention Architecture (Kimi Team 技术报告) · arXiv:2510.26692

## 核心问题

标准 softmax attention 有**二次时间复杂度 + 线性增长的 KV cache**，在长上下文、RL test-time scaling、agentic 解码密集场景下是吞吐/内存/上下文扩展的核心瓶颈。线性注意力降复杂度但**历史质量一直不如 softmax**（表达力受限，finite-state RNN 容量有限，长序列建模与 in-context retrieval 理论上受限）。混合架构（少量全注意力层 + 多数线性层）是质量/效率的实用折中，但既往工作**规模有限、缺跨场景全面评测**，且未能在公平对比下真正超越全注意力。

**解决思路**：提出 KDA（Kimi Delta Attention）——在 Gated DeltaNet 基础上加**更细粒度的 channel-wise 门控**，并配 DPLR 变体的定制 chunkwise 算法；与 MLA 全注意力按 3:1 混合，首次在公平对比下（同训练配方、1.4T tokens）于短/长/RL 三场景全面超越全注意力，同时 KV cache 砍 75%、1M 上下文解码吞吐 6×。

## 关键创新点

### 1. KDA = Gated DeltaNet + Channel-wise 门控（§1/§2）
- **机制**：GDN（与 Mamba2 类似）用**粗粒度的 head-wise forget gate**（每个头一个遗忘率）；KDA 改为 **channel-wise 变体**——每个特征维度独立遗忘率（类似 GLA），对 finite-state RNN memory 做更精细调控，释放线性注意力在混合架构里的潜力。
- **效果**：细粒度门控 → 更有效利用有限 RNN 记忆 → 长序列质量提升。

### 2. DPLR 变体 + 定制 chunkwise-parallel 算法（§1/§2）
- **机制**：KDA 用 **Diagonal-Plus-Low-Rank 转移矩阵的特化变体**参数化转移动力学，推导出专用 chunkwise-parallel 算法——相对一般 DPLR 公式**大幅减少计算**，同时保持与经典 delta rule 一致。
- **效果**：硬件高效（KDA kernel + vLLM 集成），兼顾表达力与算力效率。

### 3. 3:1 混合架构（KDA : 全局 MLA）
- **机制**：KDA 与周期性全注意力层按均匀 **3:1** 交织——多数快线性层省内存/算力，少量全注意力层保全局信息流。
- **效果**：长序列生成 KV cache 与内存降 **75%**，1M 上下文解码吞吐 **6×**，且全注意力层保住全局建模。

### 4. 公平规模验证 + 全开源
- 3B 激活 / 48B 总参，1.4T tokens 预训练。开源 KDA kernel、vLLM 实现、预训练/指令微调 checkpoint，drop-in 兼容现有全注意力管线（不改缓存/调度接口）。

## 表格（原文结果）

### 质量对比（1.4T 公平训练）
| 基准 | MLA(全注意力) | GDN-H | Kimi Linear |
|---|---|---|---|
| MMLU-Pro (4k) | 47.2 | 47.9 | **51.0** |
| RULER (128k) | 81.3 | 80.5 | **84.3** |

### 效率对比
| 指标 | MLA | Kimi Linear |
|---|---|---|
| 1M 上下文 TPOT | 11.48ms | **1.84ms**（6.3×） |
| 解码长度加速 | — | 4K→6.3×、128K→5.7×、256K→4.8× |
| KV cache 占用 | 基线 | −75% |

## 与同类对比
- **vs Gated DeltaNet (GDN) / Mamba2**：GDN/Mamba2 是 head-wise 粗门控；KDA 用 channel-wise 细门控，更精细管 RNN 记忆 → 质量更高。
- **vs GLA (Gated Linear Attention)**：KDA 的 channel-wise 门控思想借鉴 GLA，但结合 DPLR 变体 + chunkwise 算法做硬件优化。
- **vs 纯 softmax / MLA**：首次在公平规模下混合线性架构**全面超越**全注意力（既往混合架构要么规模小要么未超越）。

## 跨论文关系（→ MOC 谱系）
- **线性/混合注意力谱系**：Gated DeltaNet → KDA(本文,channel-wise 门控) → 与 MLA 混合(3:1)。延续 gated-delta 线（Mamba2/GLA/DeltaNet）。
- **与 [[gated-delta-networks-improving-mamba2-with-delta-rule]] 互补**：GDN 也是改进 Mamba2 的 delta rule；KDA 进一步在门控粒度上做文章，二者同属 delta-rule 线性注意力改进分支。
- **与 [[ascend-950-npu-architecture-whitepaper]]/[[parallel-scan-on-ascend-ai-accelerators]] 关联**：线性注意力的 chunkwise/scan 算子在 NPU 上的并行实现是落地关键（KDA kernel 可受益于并行 scan）。
- **应用层**：混合线性架构服务 agentic/RL test-time scaling 场景（长轨迹、工具调用），与 [[kimi-k3-open-frontier-intelligence]]、[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] 的长上下文需求同向。

## 局限与边界
- **3:1 比例是经验值**，最优混合比可能随规模/任务变（作者未给比例敏感性详析）。
- 仍依赖周期性全注意力层保全局信息——纯线性在长序列 in-context retrieval 上理论受限（作者承认 finite-state 容量瓶颈未根除，靠混合缓解）。
- 评测 1.4T tokens、3B 激活规模；更大规模（百B激活）下相对全注意力的优势是否保持，需后续验证。
- DPLR 变体的 chunkwise 算法实现复杂，依赖定制 kernel 才能拿到效率收益（非通用库开箱即用）。
