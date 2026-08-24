---
paper_num: "3"
title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
authors: "Models via Training-Time Test Yuhui Li1,3, Fangyun Wei2, Chao Zhang1, Hongyang Zhang3,4 1Peking University 2Microsoft Research 3University of Waterloo 4Vector Institute yuhui.li@stu.pku.edu.cn, fawe@microsoft.com c.zhang"
date: "2025/3/3"
arxiv: "https://arxiv.org/abs/2503.01840"
pdf: "papers/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.pdf"
slug: "eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test"
tags: [speculative, training]
---

# EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test

> [!abstract] 摘要（原文）
> 1\. 🚀 EAGLE-3 通过放弃特征预测约束，直接进行 token 预测并引入 multi-layer feature fusion 技术，显著提升了 draft model 的表达能力与推理效率。 2. 📈 该研究提出了 training-time test 训练方法，使 draft model 能够有效利用规模化训练数据，从而在 LLaMA 等主流模型上实现了高达 6.5 倍的推理速度提升。 3. ⚙️ 实验表明，EAGLE-3 在 SGLang 等工业级推理框架中表现优异，在 batch size 为 64 时仍能保持 1.38 倍的吞吐量提升，优于现有的 speculative sampling 方法。

## 元信息
- **发表日期**: 2025/3/3
- **作者**: Models via Training-Time Test Yuhui Li1,3, Fangyun Wei2, Chao Zhang1, Hongyang Zhang3,4 1Peking University 2Microsoft Research 3University of Waterloo 4Vector Institute yuhui.li@stu.pku.edu.cn, fawe@microsoft.com c.zhang
- **arXiv**: https://arxiv.org/abs/2503.01840
- **本地 PDF**: `papers/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig01.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]]*
> [!quote] caption
> Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGPT.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图含上下两幅折线图，以LLaMA-3.1-8B-Instruct为target、在MT-bench上对比EAGLE-2（红）与EAGLE-3（蓝），x轴为1/2/4/8×ShareGPT。上图Speedup：EAGLE-3由~3.7单调升至~4.4，EAGLE-2在~3.2处趋于饱和；下图Accept length：EAGLE-3由~5.2升至~6.1，EAGLE-2始终贴近~4.1。图用以论证：EAGLE-3的新架构打破了前作随数据增大迅速饱和的瓶颈，首次呈现持续上升的scaling law。作为开篇Figure，它奠定全文核心动机——更多训练数据带来更大加速收益，为后续架构设计、训练策略与实验验证提供支撑。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig02.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]*
> [!quote] caption
> Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1, we present comparisons with additional methods, but this figure only showcases a subset. Chat model’s evaluation dataset is MT-bench, and the reasoning model’s evaluation dataset is GSM8K. DeepSeek R1 LLaMA 8B refers to DeepSeek-R1-Distill-LLaMA 8B

> [!tip] 技术解读（多模态）
> 【图文联合解读】图2展示7种方法在4个目标模型上的推理加速比（temperature=0）：Vicuna-13B（MT-bench）上EAGLE-3达5.6×，超过EAGLE-2（4.1×）、Medusa（2.1×）与投机采样（1.9×）；LLaMA-3.1-8B、LLaMA-3.3-70B、DeepSeek-R1-LLaMA-8B（GSM8K）上EAGLE-3分别达4.4×、4.1×、5.0×，均为各模型最优。该图作为性能总览，证明EAGLE-3在对话与推理任务、8B–70B不同规模上一致领先已有方法；配合Table 2消融（去特征约束+多级特征融合），共同支撑其两项关键改进的有效性，构成论文方法验证链路的收口证据。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig03.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]]*
> [!quote] caption
> Illustration of training-time test (the bottom part) and its comparison with other draft methods (the upper and middle parts). f denotes the feature, t denotes the token, and a represents the unconstrained vectors.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3 联合解读**

1) **核心结构**：图分三层对比。上层EAGLE：训练Step1用真实特征f_t预测f̂_{t+1}、t̂_{t+2}（含l_fea、l_token双损失），测试Step2串行自回归f̂→t̂；中层EAGLE+l_fea去除版：改输出无约束向量â，仅l_token，但测试时t̂_{t+3}≉ t_{t+3}（红错号）暴露训练-测试失配；底层EAGLE-3（training-time test）：训练时把Step1预测的â_{t+1}回灌为Step2输入（红虚线箭头"Training-time test"），使训练/测试一致，Step2输出t̂_{t+3}≈t_{t+3}。

2) **关键结论**：原文指出EAGLE训练用真特征、测试用预测特征，存在分布偏移；将Step1纳入训练循环后，模型学会在自身预测误差下仍保持稳定，使增加训练数据的收益更显著，验证了training-time test的必要性。

3) **论文作用**：作为EAGLE-3方法论核心图，奠定"训练模拟推理时自回归"原则，衔接后续消融与scaling实验，为EAGLE-3在更大数据/模型下的加速增益提供机制依据。

### Figure 4 (p.2) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig04.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]*
> [!quote] caption
> We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing training data become more pronounced. We name this technique as training-time test. EAGLE and speculative sampling methods such as Medusa (Cai et al., 2024) reuse the top-layer fea- tures of the target model, specifically the features immediately befor

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图4横轴为相对ShareGPT的训练数据规模（1/2/4/8倍），纵轴为接受率0-α，对比EAGLE、EAGLE-3及去掉特征预测的EAGLE三条曲线。EAGLE从约0.755升至0.784即饱和；EAGLE-3起点最低（≈0.722）但斜率最陡，于4倍处反超原EAGLE并达≈0.801；无特征预测版本始终居前（8倍≈0.812）。

该图印证原文关键结论：原EAGLE对数据扩展几乎无感，而采用"training-time test"将Step 1融入训练后，数据扩展收益被显著放大，使EAGLE-3在大数据规模下超越基线。此图作为支撑"训练-测试一致性"核心设计的可扩展性证据，串联起方法动机与后续加速比的实验链。

### Figure 5 (p.4) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig05.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]]*
> [!quote] caption
> Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level features of the target model, respectively. e denotes the embedding. 3 EAGLE-3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

1) **核心结构**：左为冻结的Target Model，经Embedding、两层Decoder Layer后输出低/中/高层特征 $l_{how}, m_{how}, l_{can}, m_{can}$（高层 $h$ 未在图中绘出）；右为Draft Model的三步流水线——① FC Layer融合目标特征 $g$ 与上下文embedding $e$；② Decoder Layer自回归展开序列；③ 仅LM Head扩展为多分支候选树（"can"/"I"/"do"）。

2) **关键论证**：EAGLE-3通过**训练时测试**让Draft Model直接消费Target Model的**多层特征（l/m/h）**而非仅末层hidden state，并以三层架构（FC→Decoder→LM Head）实现"特征融合→序列自回归→树状并行候选"解耦，使草稿生成既保留目标模型语义信息、又获得高吞吐候选。

3) **论文作用**：该图是EAGLE-3方法论的核心可视化，明确其相对EAGLE/EAGLE-2的**架构增量**（三层管线+多层级特征输入+训练时测试策略），为后续消融与加速比实验提供机制依据，是理解后续图6、图7 tree attention与训练流程的基础。

### Figure 6 (p.5) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig06.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]]*
> [!quote] caption
> All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in significant computational waste, so we can use vector dot products to calculate the attention score only for the corresponding positions. HASS (Zhang et al., 2024) and EAGLE-3 both make similar modifications to the attention mecha- nism to simulate t

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示展示训练时测试的三个注意力因果mask：①原生训练步（3×3，token 为 How/can/I）为全下三角，每 query 关注全部前置 key；②两个模拟步（依次 3×6、3×9）随 draft token（蓝/黄色，与原句"How can I are we do…"等灰色训练 token 区分）注入，mask 由稠密退化为严格对角——仅 query=key 处标✓，其余置零。

它论证：仅当 key 源自原始训练数据才需全下三角矩阵乘；模拟 draft 阶段用向量点积按位计算即可，避免对角化稀疏矩阵的算力浪费。该稀疏化改造与 HASS 类似，共同支撑 EAGLE-3 在训练—测试一致性模拟下训练 draft 模型，从而在推理时实现低开销的多 token 预测加速。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig07.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]]*
> [!quote] caption
> Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7联合解读：**

1）**核心对象与数据**：横轴为0-α至7-α（即在已接受前序token条件下，输入含n个估计特征后的接受率），纵轴为接受率。EAGLE（红）从0-α的≈0.71急剧衰减：1-α≈0.64、3-α≈0.57、6-α降至≈0.51，整体跌幅约20%；而EAGLE-3（蓝）始终稳定在0.78–0.81区间，几乎无衰减，6-α处反达峰值≈0.81。

2）**论证的关键结论**：随估计特征数n增加，传统EAGLE因仅依赖last-token特征而出现严重的接受率雪崩；EAGLE-3通过训练时即采用test-time多特征输入，使其在自投机多步生成中保持高且平稳的接受率，二者差距随n增大而显著扩大。

3）**作用**：为EAGLE-3"训练-测试一致性"设计提供了直接定量证据，是论证其推理加速效果优于EAGLE的核心实验之一。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab01.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ of different methods. V represents Vicuna, L31 represents LLaMA-Instruct 3.1, L33 represents LLaMA-Instruct 3.3, and DSL represents DeepSeek-R1-Distill-LLaMA. SpS denotes standard speculative sampling, with its draft model being Vicuna-68M. Methods lik

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读：**

表1在Temperature=0/1两种设置下，对V 13B、L31-8B、L33-70B、DSL-8B四类目标模型，在MT-bench、HumanEval、GSM8K、Alpaca、CNN/DM五个基准上对比SpS、PLD、Medusa、Lookahead、Hydra、EAGLE(-2/-3)各方法的**加速比**与**平均接受长度τ**。

**关键量化数据**：T=0（lossless）下，EAGLE-3在V 13B上均值加速达**5.51x**（τ=6.62），HumanEval上τ峰值**7.54**；L33-70B均值4.12x；DSL-8B在GSM8K上加速比最高（呼应正文"DeepSeek在数学推理集表现例外"的论述）。

**论证的技术结论**：EAGLE-3在lossless条件下全面领先所有基线（含EAGLE-2、Hydra），且τ峰值近7.5，表明其drafting机制质量显著优于前辈方法；并以Medusa（非lossless）作反衬，凸显本文方法的严谨性。

**在论文整体中的作用**：与Figure 1（MT-bench上的scaling law曲线）相互印证，构成"scaling曲线 + 多基准全模型量化对比"的实验双支柱，支撑"训练时数据扩展+多任务泛化"这一核心方法论的有效性主张。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab02.png]]
> [!quote] caption
> Ablation study results with LLaMA-Instruct 3.1 8B as the target model. “Remove fea con” refers to the first improvement of EAGLE-3, which removes the feature prediction constraint. “Fused features” refers to the second improvement of EAGLE-3, where low, middle, and high-level feature fusion replaces

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读：**

**1) 核心对象与数据：** 以 LLaMA-Instruct 3.1 8B 为目标模型，依次叠加两项改进——"+ remove fea con"（去除特征预测约束）和 "+ fused features"（低/中/高层特征融合）。MT-bench 上加速比由 EAGLE-2 的 **3.16×**（τ=4.05）逐步升至 **3.82×**→**4.40×**（τ=6.13）；GSM8K 上由 **3.39×**（τ=4.24）升至 **3.77×**→**4.48×**（τ=6.23）。每步均带来 ~0.6–0.7× 的加速增益。

**2) 关键结论：** 论证两项改进均有效——去除特征约束提高草稿接受率，多层特征融合进一步丰富表征信息，二者叠加使加速比相对 EAGLE-2 提升约 **39%（MT-bench）** 与 **32%（GSM8K）**。

**3) 在论文中的作用：** 作为消融实验，定量分离 EAGLE-3 相对 EAGLE-2 的两个核心改进各自的贡献，为"训练时测试"策略的有效性提供可分解的实证支撑。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab03.png]]
> [!quote] caption
> Throughput improvement under different batch sizes on H100 and LLaMA-Instruct 3.1 8B for the MT- Bench dataset, with SGLang without speculative sam- pling as the baseline (1.00x). The experiments were conducted by the SGLang team.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比EAGLE与EAGLE-3在H100、LLaMA-3.1-8B、MT-Bench上batch size 2–64的吞吐量加速比（基线SGLang=1.00×）。数据上，EAGLE在bs=2达1.40×，随bs增大迅速衰减至0.88–0.99×，大batch下甚至低于基线；而EAGLE-3在所有batch下均稳定领先，bs=4峰值1.82×，bs=64仍维持1.38×，较EAGLE同batch提升约0.34–0.50×。该结果有力佐证training-time test（TTT）技术使草稿模型在大batch高并发场景下保持高效加速，验证了论文"训练时测试"这一核心方法在真实服务负载下的实用价值与扩展性。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab04.png]]
> [!quote] caption
> Throughput at batch size = 1 on H100 when the target model is LLaMA-Instruct 3.1 8B and the testing dataset is MT-bench. The experiments were conducted by the SGLang team.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）表格内容**：Table 4 对比 EAGLE 与 EAGLE-3 在 LLaMA-Instruct 3.1 8B 模型、MT-bench 数据集、H100 上、batch size 从 2 到 64 的吞吐加速比。EAGLE-3 加速比稳定在 **1.32x–1.82x**（如 BS=2 时 1.81x，BS=64 时 1.38x）；而 EAGLE 加速比随 batch 增大急剧衰减（BS=2 时 1.40x，BS≥16 后跌至 **0.88x–0.99x**，反而慢于基线）。

**2）论证结论**：EAGLE-3 在高并发场景下仍能持续提供有效加速，而 EAGLE 在大 batch 时基本失效，验证了 training-time test 等改进使 EAGLE-3 的加速能力在高 batch 区间依然保持。

**3）论文作用**：此表补强了 EAGLE-3 的实验证据链，配合 Figure 4 所述训练时测试技术，证明该方法在单请求（batch=1，低延迟）与高吞吐（高 batch）两类部署场景下均优于 EAGLE，体现其工程实用性与全面性。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab05.png]]
> [!quote] caption
> Throughput improvement under different batch sizes on A100 and LLaMA-Instruct 3.1 8B for the MT- Bench dataset, with vLLM without speculative sampling as the baseline (1.00x).

> [!tip] 表格解读（多模态）
> 【图文联合解读】表5对比EAGLE与EAGLE-3在batch size 2-56下相对vLLM基线的吞吐加速比：EAGLE-3从bs=2的1.75x平稳降至bs=56的1.01x，全程≥1.00x；EAGLE仅在bs≤24有效，bs=32起跌破基线（0.93x→0.71x）。结合Figure 5所示机制——低/中/高层特征融合与三步树扩展草稿——印证了EAGLE-3草稿质量提升使其在高batch下仍维持正收益，构成论文证明方法可扩展性、走向实际部署的关键实验。

## 相关论文

- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM

## 技术点深读（DEEP）

![[deep/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.txt`（45552 字符）供引用检索。