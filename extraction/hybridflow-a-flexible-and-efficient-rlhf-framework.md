---
paper_num: "30"
title: "HybridFlow: A Flexible and Efficient RLHF Framework"
authors: "Guangming Sheng The University of Hong Kong gmsheng@connect.hku.hk Chi Zhang ByteDance zhangchi.usc1992@bytedance.com Zilingfeng Ye ByteDance yezilingfeng@bytedance.com Xibin Wu ByteDance wuxibin@bytedance.com Wang Zhang"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2409.19256"
pdf: "papers/hybridflow-a-flexible-and-efficient-rlhf-framework.pdf"
slug: "hybridflow-a-flexible-and-efficient-rlhf-framework"
tags: [rl]
---

# HybridFlow: A Flexible and Efficient RLHF Framework

> [!abstract] 摘要（原文）
> 1\. 🤔 HybridFlow 提出了一种混合编程模型，巧妙地结合了单控制器（用于节点间数据流协调）和多控制器（用于高效执行节点内分布式 LLM 计算）范式，旨在解决 RLHF 在 LLM 对齐中面临的复杂性和效率挑战。 2. ⚙️ 该框架设计了分层 API 以实现灵活的 RLHF 算法表达和高效操作编排，并引入了 3D-HybridEngine 用于 Actor 模型在训练和生成阶段之间的高效参数重分片，实现了零内存冗余和显著降低的通信开销。 3. 🚀 实验结果表明，HybridFlow 在运行各种 RLHF 算法时，吞吐量比现有最先进的基线系统（如 DeepSpeed-Chat、OpenRLHF 和 NeMo-Aligner）提高了 1.53 倍至 20.57 倍，验证了其灵活性和高效率。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Guangming Sheng The University of Hong Kong gmsheng@connect.hku.hk Chi Zhang ByteDance zhangchi.usc1992@bytedance.com Zilingfeng Ye ByteDance yezilingfeng@bytedance.com Xibin Wu ByteDance wuxibin@bytedance.com Wang Zhang
- **arXiv**: https://arxiv.org/abs/2409.19256
- **本地 PDF**: `papers/hybridflow-a-flexible-and-efficient-rlhf-framework.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.3)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]
> [!quote] caption
> Dataflow graph of 3 RLHF algorithms [19, 43, 55].

### Figure 2 (p.3)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]
> [!quote] caption
> Programming model used in RLHF systems. (a)

### Figure 3 (p.4)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p04.png]]
> [!quote] caption
> Dataflow execution given a model placement plan.

### Figure 4 (p.6)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]
> [!quote] caption
> Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybrid programming model includes a set of hierarchical APIs to enable flexible expression of the RLHF dataflow and effi- cient computation of models in the dataflow (§4). The 3D-

### Figure 5 (p.6)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]
> [!quote] caption
> An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, resource allocation, and 3DParallelWorker initialization. (b) Asynchronous data re- sharding between two models with collect and distribute functions in 3D_PROTO. devices, it facilitates distributed model weight initialization and establishes 3D parallel groups for each model. A parallel group includes a set of GPUs to

### Figure 6 (p.7)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p07.png]]
> [!quote] caption
> Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to different RLHF algorithms by simply adding or deleting a few lines of code. our programming model, HybridFlow is flexible in support- ing diverse distributed execution patterns without any code change of the RLHF algorithm (Figure 6).

### Figure 7 (p.8)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]
> [!quote] caption
> 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor training and generation. 1-2-2 (𝑝-𝑡-𝑑) parallel groups are used in training and 1-1-2-2 (𝑝𝑔- 𝑡𝑔-𝑑𝑔-𝑑) parallel groups are used in generation. 5 3D-HybridEngine

### Figure 8 (p.8)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]
> [!quote] caption
> Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation. model parameters updated in iteration 𝑖(step 1○in Figure 7), for generation within each micro DP group. Then, the batch of prompts are loaded to each model replica (step 2○), which generates responses (Generation stage of RLHF). Following this, 3D-HybridEngine performs an all-gather operation on the g

### Figure 9 (p.11)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!quote] caption
> PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines. 8 16 32 64 128 # of GPUs 0 1 2 3

### Figure 10 (p.11)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!quote] caption
> ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines 8 16 32 64 128 # of GPUs 0 1 2 3

### Figure 11 (p.11)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
> [!quote] caption
> Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines reward models. Each model is a Llama [73] model with sizes ranging from 7B to 70B. Safe-RLHF has an additional cost model whose architecture and size are the same as the re- ward model and ReMax eliminates the critic model. We use mixed precision for actor and critic training, i.e., BF16 for model 

### Figure 12 (p.12)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]
> [!quote] caption
> Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs

### Figure 13 (p.12)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]
> [!quote] caption
> Placement comparison under 13B actor and reference policy & 70B critic and reward model.

### Figure 14 (p.13)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]
> [!quote] caption
> Transition time between actor training and generation.

### Figure 15 (p.13)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]
> [!quote] caption
> Time breakdown on different generation parallel sizes of the actor model on 16 GPUs. various model scales, which is the time to reshard model weights from training to generation, under the same settings in §8.2. OpenRLHF’s transition time includes weight syn- chronization time between two copies of the actor model on different devices. HybridFlow reduces the transition time by 55.2% (11.7s) on ave

### Figure 16 (p.13)
![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]
> [!quote] caption
> Runtime of device mapping algorithm. The model size and # of GPUs are simultaneously scaled.

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.7 `critic_metrics = critic.update_critic(batch, loss_func=algo_type)`
- p.7 `pretrain_loss = actor.compute_loss(pretrain_batch)`
- p.7 `batch[“pretrain_loss”] = pretrain_loss`
- p.7 `actor_metrics = actor.update_actor(batch, loss_func=algo_type)`
- p.8 `𝑁𝑎=𝑝×𝑡×𝑑=𝑝𝑔×𝑡𝑔×𝑑𝑔×𝑑such that 𝑑𝑔=`

## 相关论文

- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM REINFORCEMENT LEARNING
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning

## 全文文本
全文已存 `extraction/fulltext/hybridflow-a-flexible-and-efficient-rlhf-framework.txt`（109820 字符）供引用检索。