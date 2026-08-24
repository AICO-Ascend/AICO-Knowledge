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
> 【图文联合解读】**图文联合解读**

图1含两条子图：上图为**Speedup**、下图为**Accept length**，横轴均为训练数据相对ShareGPT的倍数（1/2/4/8×），评测任务为MT-bench，目标模型为LLaMA-3.1-8B-Instruct。红色EAGLE-2在两指标上几近饱和（speedup≈3.1→3.3，accept≈4.0→4.2），蓝色EAGLE-3则随数据量单调递增（speedup 3.7→4.4，accept length 5.2→6.1）。

论文据此论证：**EAGLE-3的新架构突破了EAGLE-2因特征预测受限导致的数据扩展瓶颈**，首次在投机解码中观察到持续可扩展的scaling curve，而此前工作从未出现。

作用上，该图作为开篇核心证据，定调全文研究动机——通过设计层面的创新解锁test-time training scaling能力，为后续方法细节、全模型/全任务加速比实验（Figure 2）以及与EAGLE、EAGLE-2的全面对比奠定前提。

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
> 【图文联合解读】**图3联合解读**

1) **核心对象**：三幅上下对照的draft流程图。上为原EAGLE：Training时以特征序列$f_1\cdots f_t$输入Draft模型，Step1输出$\hat f_{t+1}$（$l_{fea}$），Step2经LM head输出$\hat t_{t+2}$（$l_{token}$）。中为EAGLE+$l_{fea}$去除：改用无约束向量$\hat a_{t+1}$，Test时$\hat t_{t+3}\neq t_{t+3}$（红字标错）。下为EAGLE-3：Training/Test均执行Step1→Step2自回归，并以红色虚线"Training-time test"将Step1预测$\hat a_{t+1}$回灌为Step2输入。

2) **关键结论**：去掉特征预测会暴露train-test分布失配；将Step1纳入训练后，8×数据下α-α由~0.78升至~0.80、SP由~0.69升至~0.78，证明训练分布与测试对齐才能让数据规模转化为draft接受率增益。

3) **作用**：作为EAGLE-3的核心创新，支撑"scaling law"与相对EAGLE-2的1.4×延迟加速结论。

### Figure 4 (p.2) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig04.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]*
> [!quote] caption
> We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing training data become more pronounced. We name this technique as training-time test. EAGLE and speculative sampling methods such as Medusa (Cai et al., 2024) reuse the top-layer fea- tures of the target model, specifically the features immediately befor

> [!tip] 技术解读（多模态）
> 【图文联合解读】图4左侧给出EAGLE训练/测试两阶段流程（特征f_t预测f̂_{t+1}，再经LM head预测token）；右侧两折线图横轴为ShareGPT 1×–8×数据量下的接受率：EAGLE（红）较平稳；无特征预测版（黄）左图升至≈0.81但右图仅≈0.2–0.3；EAGLE-3（蓝）起点最低但随数据增速最快，8×时反超达≈0.80/0.78。原文据此论证：将测试时推理结构（Step1特征预测）纳入训练（training-time test）可显著放大数据扩展收益，是EAGLE-3关键改进。该图与Figure 3方法图互补，配合Table 4吞吐数据共同构成"训练时测试"有效性的完整证据链。

### Figure 5 (p.4) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig05.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]]*
> [!quote] caption
> Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level features of the target model, respectively. e denotes the embedding. 3 EAGLE-3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示EAGLE-3推理流水线的双塔结构：左侧为目标模型，自Embedding经多层Decoder依次输出低(l)、中(m)、高(h)三级特征及嵌入e；右侧为草稿模型的三步骤（①②③），每步通过FC层+Decoder层+LM Head自回归预测候选token（can/I/do/it），输入融合多级特征与token嵌入。

该图论证的关键结论：相较EAGLE/EAGLE-2仅复用顶层特征，EAGLE-3同时融合低、中、高三级特征与嵌入，使小容量草稿模型更精准逼近大模型分布，提高投机解码接受率。

在论文链路中，此图是方法部分的核心架构图，与Table 5的吞吐量加速实验相互印证，构成从"单层特征→多层特征+训练时测试"方法演进的关键可视化证据。

### Figure 6 (p.5) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig06.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]]*
> [!quote] caption
> All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in significant computational waste, so we can use vector dot products to calculate the attention score only for the corresponding positions. HASS (Zhang et al., 2024) and EAGLE-3 both make similar modifications to the attention mecha- nism to simulate t

> [!tip] 技术解读（多模态）
> 【图文联合解读】## Figure 6 图文联合解读

**1) 核心对象与结构：**
图示三个下三角（causal）掩码矩阵，对应训练时测试的三个步骤：
- **第一步**（左上，3×3）：原始训练步，Query/Key 均为真实 token "How/can/I"（灰色），构成标准下三角掩码；
- **第二步**（右上，3×6）：模拟步 1，新增蓝色预测 token "are/we/do" 作为 Query，Key 扩展至 6 个；
- **第三步**（右下，3×9）：模拟步 2，再追加黄色预测 token "you/help/it"，Key 扩展至 9 个；
- 左侧两棵 token 树（蓝、黄分支）对应采样得到的扩展树状结构，红勾标记有效注意力位置。

**2) 关键技术结论：**
所有掩码均保持下三角因果性；当 Query 为训练数据（灰色）时，注意力分数仅分布在原 token 位置，故可用 **向量点积**替代完整矩阵乘法以避免计算浪费；模拟 token 呈**对角线**稀疏模式，实现并行多 token 草稿训练。

**3) 论文链路作用：**
该图是 EAGLE-3 "训练时测试" 策略的可视化基石，阐明如何在一次前向中同时监督多个采样分支的注意力计算，使 head 模型能在一轮训练内学习多 token 预测，为后续 tree attention 推理加速（Fig 7）与加速比实验提供机制支撑。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig07.png]]
*整页渲染: ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]]*
> [!quote] caption
> Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 7）**

图7展示EAGLE（红）与EAGLE-3（蓝）在MT-bench上、目标模型LLaMA 3.1 8B下的token接受率，横轴0-α到7-α表示输入0–7个估计特征且前序token全被接受。量化对比：EAGLE-3全程稳定于0.78–0.81；EAGLE则由0-α的0.71骤降至6-α的0.51，呈明显衰减。

原文借此论证关键结论：**多层级（低/中/高层）特征输入不损害EAGLE-3的接受率**，而EAGLE因额外特征带来性能下降。该图直接支撑三层管线+多特征融合的架构设计，承上启下，衔接方法论与后续图8加速比/吞吐评测，是EAGLE-3核心增量的关键实验证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab01.png]]
> [!quote] caption
> Speedup ratios and average acceptance lengths τ of different methods. V represents Vicuna, L31 represents LLaMA-Instruct 3.1, L33 represents LLaMA-Instruct 3.3, and DSL represents DeepSeek-R1-Distill-LLaMA. SpS denotes standard speculative sampling, with its draft model being Vicuna-68M. Methods lik

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1在温度0/1下比较V13B、L31-8B、L33-70B、DSL-8B在MT-bench、HumanEval、GSM8K、Alpaca、CNN/DM上的加速比与平均接受长度τ。温度0时，EAGLE-3在V13B均值5.51×、τ6.62，EAGLE-2为4.22×、4.83；其在L31/L33/DSL均值4.44/4.12/4.16×，τ6.23/5.88/5.84。温度1仍领先，说明长接受序列带来稳定加速。该表衔接Fig.1数据扩展与Fig.2部署评测，验证跨模型优势。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab02.png]]
> [!quote] caption
> Ablation study results with LLaMA-Instruct 3.1 8B as the target model. “Remove fea con” refers to the first improvement of EAGLE-3, which removes the feature prediction constraint. “Fused features” refers to the second improvement of EAGLE-3, where low, middle, and high-level feature fusion replaces

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心数据**：以 LLaMA-3.1-8B-Instruct 为目标模型，三行渐进消融对比——EAGLE-2 基线在 MT-bench/GSM8K 上加速比为 3.16x/3.39x（接受长度 τ=4.05/4.24）；加入"移除特征约束"后升至 3.82x/3.77x（τ=5.37/5.22）；再加"多层级特征融合"（即完整 EAGLE-3）达 4.40x/4.48x（τ=6.13/6.23）。

2) **关键技术结论**：两项改进均带来单调提升，特征融合收益最大，使 MT-bench 加速比相对 EAGLE-2 提升约 39%、τ 提升 ~51%，证明去除约束与多层级融合均不可或缺。

3) **论文作用**：作为核心消融实验，定量验证 EAGLE-3 两大设计选择的有效性，与 Figure 2 的端到端对比互补，构成方法合理性的关键证据链。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab03.png]]
> [!quote] caption
> Throughput improvement under different batch sizes on H100 and LLaMA-Instruct 3.1 8B for the MT- Bench dataset, with SGLang without speculative sam- pling as the baseline (1.00x). The experiments were conducted by the SGLang team.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 表3对比 EAGLE 与 EAGLE-3 在 H100、LLaMA-3.1-8B、MT-Bench 上，批量为 2–64 时的吞吐量加速比（基线 SGLang=1.00×）。EAGLE 仅在小批量（2–4）保持 1.38–1.40× 增益，批量≥16 后普遍降至 0.88–1.02×；EAGLE-3 全批量均显著领先，最低仍达 1.32×（batch=32），峰值 1.82×（batch=4）。

**2）关键技术结论：** 证明 EAGLE-3（结合训练时测试）相对 EAGLE 在高并发场景下优势扩大——传统推测解码在大批量下易失效，EAGLE-3 的训练时测试机制有效突破此瓶颈。

**3）实验链路作用：** 与 Figure 3 的方法示意图呼应，验证训练时测试在实际部署（大批量推理）中的工程价值，为论文核心方法提供端到端部署证据。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab04.png]]
> [!quote] caption
> Throughput at batch size = 1 on H100 when the target model is LLaMA-Instruct 3.1 8B and the testing dataset is MT-bench. The experiments were conducted by the SGLang team.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）该表展示 EAGLE 与 EAGLE-3 在 H100 上对 LLaMA-Instruct 3.1 8B 跑 MT-bench 的吞吐加速比（batch size=2…64）。EAGLE 由 1.40x 单调下滑至 0.99x，batch≥24 时跌破 1x；EAGLE-3 始终保持 1.32x–1.82x 加速，全区间领先 0.4–0.5x 左右。

2）关键结论：随着 batch 增大、EAGLE 的 top-layer feature 复用策略因分布偏移而失效，加速比归零；而 EAGLE-3 借助 training-time test 把测试阶段纳入训练，缓解该问题，使其在高并发下仍稳定提速 1.3x 以上。

3）实验链路作用：与 acceptance length、loss 曲线互证，将"训练-测试一致性"从离线质量指标延伸至 SGLang 在线服务性能，闭合算法→系统的证据链。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-tab05.png]]
> [!quote] caption
> Throughput improvement under different batch sizes on A100 and LLaMA-Instruct 3.1 8B for the MT- Bench dataset, with vLLM without speculative sampling as the baseline (1.00x).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读：**

**① 核心数据**：在 A100 + LLaMA-3.1-8B + MT-Bench 上，以 vLLM 无投机采样为基线（1.00x），对比 EAGLE 与 EAGLE-3 在 batch size 2/4/8/16/24/32/48/56 下的吞吐加速比。EAGLE-3 依次为 1.75x/1.68x/1.58x/1.49x/1.42x/1.36x/1.21x/1.01x；EAGLE 为 1.30x/1.25x/1.21x/1.10x/1.03x/0.93x/0.82x/0.71x。

**② 关键结论**：批越大加速越小，但 EAGLE-3 始终优于 EAGLE；EAGLE 在 batch≥32 即跌破 1.0x（变慢），而 EAGLE-3 在 batch=56 仍保持 1.01x，证明其训练期测试（training-time test）融合多层级特征带来更强的批大小鲁棒性。

**③ 论文作用**：作为方法有效性的吞吐维度实证，对应 Figure 5 流程，支撑 EAGLE-3 在高并发服务场景的部署优势。

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