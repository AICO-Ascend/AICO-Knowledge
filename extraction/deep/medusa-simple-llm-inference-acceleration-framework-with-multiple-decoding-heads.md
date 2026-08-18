# MEDUSA — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads · arXiv:2401.10774 (ICML 2024)

## 核心问题

LLM 自回归解码是**内存带宽受限**（memory-bandwidth-bound）：每步都要把全模型参数从 HBM 搬到加速器缓存，却只产 1 个 token，算力严重浪费。推测解码（speculative decoding）用小 draft 模型先生成候选再由大模型校验，但**获取/维护独立 draft 模型困难、难以集成进分布式系统**。

**解决思路**：不用外部 draft 模型，而是在主干 LLM 的最后隐状态上加**多个并行解码头（MEDUSA heads）**，每个头预测后续第 i 个位置的 token；多候选 continuation 用 tree attention 一次性校验。无需 draft 模型、即插即用、分布式友好。

## 关键创新点

### 1. 多解码头并行预测（§2.1）
- **机制**：主干 LLM 原样不动，在最后一层隐状态上接 K 个轻量 MEDUSA 头（每个头预测 +1…+K 位置的 token）。一次 forward 同时得到主干 token + K 个未来位置的 top-k 候选。把这些候选拼成树状候选 continuation。
- **效果**：单步生成多个候选 token，把"每步 1 token"扩到"每步 1+K 候选树"。

### 2. Tree-based attention 一次校验多候选（§2.1.2）
- **机制**：多个候选 continuation 共享公共前缀，只调 attention mask（树形掩码）即可在**一次 forward** 里并行校验所有候选，无需多次前向。
- **效果**：候选校验几乎零额外延迟（复用了主干前向的算力），是加速的关键之一。

### 3. MEDUSA-1 vs MEDUSA-2 两种微调（§2.2）
- **MEDUSA-1**：冻结主干，只训 MEDUSA 头（参数高效，可配 QLoRA 量化）。**无损加速**（主干不变，输出分布不变）。
- **MEDUSA-2**：主干 + MEDUSA 头联合训练，预测更准、加速更高，但需特殊训练配方（`L = L_LM + λ₀ L_MEDUSA-1`，加 LM loss 约束）防止主干能力退化。
- **效果**：MEDUSA-1 >2.2× 无损；MEDUSA-2 达 **2.3–2.8×**。

### 4. Typical Acceptance（§2.3.1）——替代拒绝采样
- **机制**：标准推测解码用拒绝采样保证与原模型同分布，但**不能再提升加速率**。MEDUSA 提出 typical acceptance：用 temperature 阈值从 MEDUSA 头输出里选"合理"候选（温度调控偏离原模型的程度），温度>0 时接受更多候选→更快；温度=0 退化为贪心。
- **效果**：比拒绝采样进一步加速，同时生成质量近似。

### 5. Self-distillation（§2.3.2）
- **机制**：当训练数据不可得（私有数据/RLHF 模型）时，用原模型自蒸馏生成 MEDUSA 头的训练数据。
- **效果**：解决"无数据"场景，RLHF 对齐模型也能加 MEDUSA。

## 表格（原文结果）

### 加速效果（§3）
| 配置 | 加速倍数 | 质量 |
|---|---|---|
| MEDUSA-1（冻结主干） | >2.2× | 无损（主干分布不变） |
| MEDUSA-2（联合训练） | 2.3–2.8× | 近似无损（训练配方保能力） |

实验：Vicuna-7B/13B（公开数据）、Vicuna-33B（私有数据）、Zephyr-7B（SFT+对齐）；batch=1（本地部署场景）。

## 与同类对比
- **vs Speculative Decoding（Leviathan/Chen 2023）**：speculative 需独立 draft 模型（获取/集成难）；MEDUSA 用主干自己的多头，无 draft 模型、即插即用、分布式友好。
- **vs Blockwise Parallel Decoding（Stern 2018）**：MEDUSA 改进并有效应用了"多头预测后续 token"的旧思路，加 tree attention + typical acceptance 让它真正可用。
- **演进关系**：MEDUSA 是推测解码谱系中"**多头自推测**"分支的奠基（无需 draft 模型）；后续 EAGLE 系列在此基础上用单层特征预测 + 训练时测试进一步提升。

## 跨论文关系（→ MOC 谱系）
- **推测解码谱系奠基之一**（多头分支）：MEDUSA(#2) → EAGLE(#4,特征不确定性) → EAGLE-2(#5,动态 draft 树) → EAGLE-3(#3,训练时测试)。
- **与 Block Diffusion 分支互补**：MEDUSA 走"多头预测+树校验"；Block Diffusion(#6)/DFlash(#7)/DSpark(#8) 走"块级半自回归"。
- **正交于 SGLang**：MEDUSA 是单模型解码加速，SGLang(#43) 是多调用间 KV 复用——可叠加（SGLang runtime 可托管 MEDUSA 头）。

## 局限与边界
- **batch=1 场景为主**（本地部署），大 batch 下内存带宽瓶颈减弱、加速收益下降（作者明确）。
- **typical acceptance 引入轻微分布偏差**（温度>0 接受更多候选），质量近似而非严格无损。
- MEDUSA-2 联合训练有主干能力退化风险，靠 LM loss 约束 + 训练配方缓解（复杂度高于 MEDUSA-1）。
- 头数选择需权衡（§2.2.3/2.3.3），头太多预测质量降、校验开销增。
