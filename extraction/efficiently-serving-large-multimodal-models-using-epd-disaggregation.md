---
paper_num: "44"
title: "Efficiently Serving Large Multimodal Models Using EPD Disaggregation"
authors: "Efficiently Serving Large Multimodal Models Using EPD Disaggregation Gursimran Singh 1 Xinglu Wang 2 Yifan Hu 1 Timothy Yu 1 Linzi Xing 1 Wei Jiang 3 Zhefeng Wang 3 Xiaolong Bai 3 Yi Li 3 Ying Xiong 1 Yong Zhang 1 Zhenan"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2501.05460"
pdf: "papers/efficiently-serving-large-multimodal-models-using-epd-disaggregation.pdf"
slug: "efficiently-serving-large-multimodal-models-using-epd-disaggregation"
tags: [multimodal, disaggregated-serving]
---

# Efficiently Serving Large Multimodal Models Using EPD Disaggregation

> [!abstract] 摘要（原文）
> 1\. 💡 本文提出了一种新颖的Encode-Prefill-Decode (EPD) Disaggregation框架，通过将LMM推理的编码、Prefill和解码阶段解耦到专用资源上，解决了现有LMM服务系统中的性能瓶颈。 2. 🚀 该框架引入了多媒体令牌缓存、Intra-Request Parallelization (IRP)、优化资源分配和动态角色切换等创新机制，以提高LMM的服务效率。 3. 📈 实验结果表明，与现有系统相比，EPD显著提升了内存效率（高达15倍）、批处理大小（高达22倍）、每请求图像数量以及SLO达成率，并大幅降低了Time to First Token (TTFT)。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Efficiently Serving Large Multimodal Models Using EPD Disaggregation Gursimran Singh 1 Xinglu Wang 2 Yifan Hu 1 Timothy Yu 1 Linzi Xing 1 Wei Jiang 3 Zhefeng Wang 3 Xiaolong Bai 3 Yi Li 3 Ying Xiong 1 Yong Zhang 1 Zhenan
- **arXiv**: https://arxiv.org/abs/2501.05460
- **本地 PDF**: `papers/efficiently-serving-large-multimodal-models-using-epd-disaggregation.pdf`
- **页数**: 17

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig01.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]]*
> [!quote] caption
> Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference be- tween encode and prefill stages (e.g., LLM-4 delays E5).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：图1对比两种LMM服务执行时间线。上半"Aggregated"（DP=4）E与LLM共享同GPU，4行流水线依次为E¹→LLM¹、E²→LLM²、E³→LLM³、E⁴→LLM⁴（挤占E⁵使其延迟）→LLM⁵；下半"Disaggregated"（P=3, E=1）E与LLM分置不同GPU，Encoder行集中处理E¹–E⁵，LLM三行并行执行LLM¹–LLM⁵。

**论证结论**：聚合架构下encoder与prefill共用GPU产生资源争用，如LLM⁴阻塞E⁵；解耦后两者独立调度，消除时序干扰。

**论文作用**：开篇动机图，揭示传统聚合部署的流水线瓶颈，为后文EPD解耦方案提供必要性依据。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig02.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]]*
> [!quote] caption
> Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi- cantly increases capacity, enabling larger batches and higher- resolution inputs. This demonstrates the memory efficiency benefits of disaggregation. representations. This stage is computationally intensive, especially for high-resolution or complex

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2联合解读**

1）**核心数据**：该柱状图对比了 MiniCPM-V 2.6 模型在 **Disaggregated（蓝色）** 与 **Aggregated（绿色）** 两种部署下的最大批处理大小（Max Batch Size），横轴为每请求图像数（1/3/5/15/20/30/40）。数据显示：1图时，解耦配置批大小约48 vs 聚合仅约6；3图时约17 vs 约2；5图时约8 vs 约1；15图及以上，聚合模式全部 OOM（显存不足），而解耦模式仍可支持 15图≈4、20图≈3、30–40图≈1 的批处理。

2）**论证结论**：将 LLM 从 GPU 卸载后，编码器独占显存，使批容量获得数倍乃至近一个数量级的提升，并解锁了更高分辨率/更多图像的请求输入，直观证明了**解耦架构的显存效率收益**。

3）**论文作用**：该图位于方法介绍后的实验验证环节，作为 EPD-Disaggregation 提出的**首个量化动机证据**，为后续吞吐/延迟实验提供容量前提说明。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig03.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]]*
> [!quote] caption
> The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from prefill to de- code, respectively. We denote the input text prompt as ip, multimodal data as im, and the output text as o. The steps are as follows:

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3图文联合解读：**

该图展示EPD分离推理流水线架构：三类GPU（E黄、P橙、D绿）各自配备独立的队列与处理阶段——Encoding Queue→Encoding Stage→EP Bridge Queue、P同构、D同构。数据经"EP Migration"由E传P，再经"PD Migration"由P传D，输入ip/im经三阶段生成输出o。

**论证结论：** 将多模态推理拆解为编码、预填充、解码三个异构阶段，因各阶段显存/算力特征差异显著（对应Table 3中E与P最大批处理规模相差数倍），独立部署可避免资源争用。

**论文作用：** 作为EPD方法的核心架构定义图，确立阶段划分与跨阶段迁移机制，为后续资源调度、批处理优化等实验奠定基础。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig04.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]]*
> [!quote] caption
> System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM weights for decoding tasks and use the KV cache.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示EPD分离推理架构：多模态请求经Scheduler(Load Balancer)分配至Encoding、Prefill、Decoding三类专精实例，分别承载Encoder Weights+MM Cache、LLM Weights+MM/KV Cache及纯解码任务。阶段间以5槽EP Bridge Queue经Async Transfer(§3.2.1)异步交接；阶段内用TP/PP并行，跨阶段用IRP(§3.2.2)通信。

它论证将异构负载解耦到独立实例可弹性扩缩、消除长尾阻塞，是论文EPD方法的核心系统蓝图，后续全部实验均基于此架构展开。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig05.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]]*
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 2 and 4 images per request. EPD consistently outperforms all baselines across configurations. question answering items that span diverse video lengths, topic

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5联合解读**

图示为3×2网格：上/下两行分别为每请求2/4张图像，列依次为MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B；纵轴SLO达成率(%)，横轴请求速率，三曲线对比EPD、DistServe、vLLM。**2图/请求时**，EPD峰值吞吐（虚线标示）约2.7/0.4/0.2 req/s且全程维持~100% SLO，而DistServe仅20–55%、vLLM常<10%（InternVL2两模型）；**4图/请求时**，EPD仍领先，峰值吞吐降至~1.5/0.1 req/s，基线几乎贴近0。

该图用于端到端SLO实验，量化证明EPD解耦在多模型、多图像规模下均稳定优于基线，是支撑"EPD Disaggregation"部署有效性结论的核心数据。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig06.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]*
> [!quote] caption
> Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b)

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图6含三幅箱线图，横轴为每请求图像数，纵轴为TTFT（秒），蓝色EPD与绿色DistServe对比：(a) MiniCPMv-2.6在2–16图范围内，16图时EPD≈3s、DistServe≈8.5s；(b) InternVL2-8B在2–8图范围，8图时EPD≈3.8s、DistServe≈5.5s；(c) InternVL2-26B在2–5图范围，5图时EPD≈5.2s、DistServe≈9.2s。

数据论证关键结论：随每请求图像数增加，TTFT单调增长，但**EPD增速远低于DistServe，差距随图像数扩大而显著放大**（如InternVL2-26B 5图时差距近2倍），证明EPD解耦对多图密集请求的延迟控制优势明显。

该图作为方法验证核心证据，在实验链中支撑"EPD解耦可有效降低多模态首token延迟"这一主张。

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig07.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]*
> [!quote] caption
> SLO attainment (↑) versus request rate on the

> [!tip] 技术解读（多模态）
> 【图文联合解读】图7展示MiniCPM-V 2.6在NextQA数据集上的SLO达成率(%)与请求速率(req/s)关系。三条曲线对比：EPD(蓝)在约1.2 req/s前稳定保持近100%达成率后骤降，垂直虚线标示其最大承载点；DistServe(绿)从约57%持续衰减；vLLM(红)仅约35%且迅速归零。该图论证EPD通过编码器-预填充-解码器分离设计显著提升多模态模型的在线服务SLO性能，是论文核心端到端实验的关键证据，与Table 7(音频基准)共同支撑"分离式架构优于DP/3P1D等方案"的方法结论。

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig08.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]*
> [!quote] caption
> As seen, EPD consistently outperforms vLLM and Dist-

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

1) **核心数据**：横轴为请求速率(0.5–3.0 req/s)，纵轴为SLO达成率(%)。EPD(蓝)在0.5–1.5 req/s区间维持近100%，至约1.85 req/s(蓝色虚线)仍达90%阈值，2.0 req/s降为~70%，3.0 req/s仅~10%；DistServe(绿)与vLLM(红)在0.5 req/s仅约70%，随负载上升持续衰减，3.0 req/s时降至5–10%。

2) **关键结论**：EPD在全部请求速率下均显著优于vLLM和DistServe，其维持90% SLO的最大可承载请求率约为后两者的近4倍，验证了编码-预填充-解码分离架构在多模态视频推理场景下的优越性。

3) **论文作用**：作为EPD方法的核心实验证据之一，与Figure 7、Table 8共同支撑"分离式架构显著提升大模型多模态服务效率"的整体论证。

### Figure 9 (p.9) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig09.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]]*
> [!quote] caption
> As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low request rates.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图9对比三种方案在InternVL2-8B模型、NPU上的SLO达成率（请求率0.007–0.035 req/s）：EPD由~95%单调降至~25%，仅在≤0.008 req/s内仍高于90%阈值线（红虚线）；DistServe与vLLM全程贴近0%，完全未达标。原文据此论证：EPD是唯一满足严格TTFT SLO的方案，基线即使在低负载下也整体失败。该图作为关键定量证据，支撑论文"Encode–Prefill–Decode解耦"核心架构的主张。

### Figure 10 (p.13) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig10.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]*
> [!quote] caption
> Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill workers. The DistServe method uses a fixed 7P configuration, assigning 7 workers to handle both encoding and prefill steps. Middle: Effect of the number of images per request on end-to-end throughput. Right: Sensitivity to encoding and prefill batch sizes

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图含三子图，均以EPD（橙实线）对比DistServe基线7P（绿虚线，约97 req/s）。**左图**：吞吐量随编/预填工人数配比变化——1E6P仅~45、5E2P峰值~155、6E1P降至~85 req/s，表明编/预填资源均衡（5:2）至关重要。**中图**：每请求图像数1→5时EPD由~155降至~50 req/s，但全程持续领先DistServe。**右图**：批大小32–64时EPD达~175 req/s峰值，对批大小不敏感。**作用**：作为敏感性/消融实验，定量论证EPD解耦在资源配置、图像规模、批大小三维度上均稳定优于DistServe，支撑全文"EPD解耦可大幅提升LMM服务吞吐"的核心主张。

### Figure 11 (p.13) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig11.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]*
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases.. content of this image?”),

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示为2×3子图网格：纵轴SLO达成率(0–100%)、横轴请求速率(req/s)；上下行分别对应每请求6/8张图像，(a)(b)(c)列对应MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B；蓝/绿/红曲线分别代表EPD、DistServe、vLLM。

数据观察：(a) MiniCPM-V 2.6中EPD在≤1.0 req/s保持100% SLO，6/8图对应最大可持续速率≈1.4/1.9 req/s；DistServe峰值仅~45%，vLLM全程<20%。(b)(c) EPD仅在≈0.1 req/s时近100%，随负载上升急剧下滑；两基线全程≈0%。

论证结论：图像数由6增至8时EPD承载速率不降反升(1.4→1.9)，印证"随图像数增加仍保持稳健"；三模型EPD均大幅领先基线，且在InternVL2-26B等大模型上差距更悬殊。

整体作用：作为EPD解耦方案端到端主实验，以"负载×SLO"量化其在多模态大模型在线服务中跨模型与图像规模的实用性与鲁棒性。

### Figure 12 (p.16) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig12.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]]*
> [!quote] caption
> Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light green denotes encode latency and light blue indicates prefill latency. NPUs demonstrate distinct latency characteristics compared to GPUs as input size increases. E.3. SLO Criteria

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图12以堆叠柱状图展示InternVL2-8B模型在每请求图像数(#I/R)由1增至8时，encode（绿）与prefill（蓝）阶段的延迟占比，分(a)GPU与(b)NPU两组。GPU上encode占比由约65%(#I/R=1)降至约25%(#I/R=8)，prefill升至约75%；NPU上encode由约72%降至约39%，prefill升至约61%。

原文借此论证：随图像量增加，encode与prefill占比发生明显翻转，且NPU的encode占比始终比GPU高约10–20%，两类阶段呈现显著不同的资源与时延特征——encode并行度高、可独立批处理，prefill则计算密集。该差异为论文核心贡献**EPD解耦**（Encode/Prefill/Decode分离部署）提供了直接实验依据，支撑将二者分配到不同硬件单元以提升多模态推理的整体吞吐与SLO达标率。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab01.png]]
> [!quote] caption
> Mean TTFT latency (in seconds) ( ↓ ) for varying video lengths at a fixed request rate of 1 request/sec. Results are averaged over 100 Video-MME samples. EPD achieves the lowest latency across all video lengths.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比vLLM、DistServe与EPD在1 req/s下8/16/32/64帧视频的TTFT延迟。EPD各帧数均最低：8帧0.24s（vs 0.42s）、16帧0.30s（vs 0.81/0.82s）、32帧0.49s（vs 1.54/1.59s）、64帧1.00s（vs 3.08/3.11s），64帧时相对vLLM降约68%。原文借此论证E-P-D三级解耦有效消除了聚合架构中编码与预fill争抢GPU的干扰（如Figure 1中LLM-4延误E5）。在论文中，该实验是从Figure 1架构动机到第四章方法落地的关键性能证据，量化印证解耦在长视频多模态场景的端到端时延优势。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab02.png]]
> [!quote] caption
> Comparison of the maximum number of images supported per request for various image resolutions across different models. Higher values are better; best values in each row are italicized.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

**核心数据：** 表中对比 MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B 三款模型，在 313,234 / 787,444 / 4032,3024 三档分辨率下，DistServe 与 EPD 两种方案单请求可承载的最大图像数。

**关键结论：** EPD 在所有行均**优于或持平** DistServe——MiniCPM-V 2.6 高分辨率档（4032×3024）由 7 跃升至 49（约 7×）；InternVL2-26B 由 1/11/1 提升至 10/45/10（4–10×）；仅 InternVL2-8B 三档同列均为 19，无增益。

**论文作用：** 该表与 Figure 2 互为佐证，定量证明 EPD 通过将 LLM 从视觉编码端解耦，腾出大量 GPU 显存，使单请求能容纳更高分辨率、更多图像，是支撑"EPD 解耦提升多模态服务容量"核心论点的关键实验证据。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab03.png]]
> [!quote] caption
> Comparison of the maximum supported batch sizes for E and P stages across different models and image reso- lutions. Higher values are better; italicized values indicate the best in each row. OOM denotes cases where the model ran out of memory.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化对比MiniCPMv 2.6、InternVL2-8B、InternVL2-26B三模型在313×234、787×444、4032×3024三种分辨率下，DistServe与EPD方案E/P阶段最大批处理容量。数据显示EPD全面碾压：InternVL2-8B@787×444的E从9飙至67；MiniCPMv 2.6@4032×3024下DistServe OOM，EPD仍可服务E=4/P=9，多个高分辨率场景实现DistServe崩溃而EPD可运行的逆转。

此表是论文核心论点——"EP解耦让编码阶段获得独立显存/并行资源"——的硬证据，量化印证了高分辨率多模态推理下EPD相较DistServe传统EP合并策略的批容量与抗OOM优势，构成后续吞吐/延迟实验的理论与实证基石。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab04.png]]
> [!quote] caption
> Effect of ablating IRP feature from the proposed system on TTFT (s). Disabling IRP negatively affects the TTFT (up to 2.9x worse ) for various multiple images/ re- quest (#I/R). Results are averaged over 100 requests.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表4针对EPD系统，在图像数/请求数 #I/R=2/4/6/8 四档下，对比开启IRP与禁用IRP的TTFT(秒)：完整EPD分别为 0.92/1.02/1.14/1.74 s；w/o IRP 劣化至 1.46/2.47/3.37/4.27 s，恶化倍数依次 1.6×、2.4×、2.9×、2.5×（100请求均值）。

**技术结论：** 禁用IRP使TTFT恶化最高达2.9×，证明Image Request Prediction是降低多图首token时延的核心组件，尤其在中高并发场景收益显著。

**实验链路作用：** 该表作为4.4节消融研究的关键证据，量化拆解各模块贡献；与Figure 4所描绘的EPD解耦推理架构形成"设计↔验证"闭环，论证完整"EPD+IRP"方案的必要性与最优性。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab05.png]]
> [!quote] caption
> Ablating the offline optimizer reduces goodput by 2.2× on average when configurations are selected randomly. ↓ indicates lower is better; ↑ indicates higher is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

1) **核心数据**：在随机选取配置的设定下，对比完整 EDP 与去掉离线优化器（w/o Opt.）的版本。完整 EPD 的 Goodput 为 1.25 r/s、TTFT 为 2.12 s、TPOT 为 0.031 s；去掉优化器后，Goodput 降至 0.56 r/s（退化 2.2×），TTFT 升至 4.48 s（退化 2.1×），仅 TPOT 略优（0.025 s，0.8×）。

2) **关键结论**：离线优化器对吞吐与首 token 时延贡献显著——没有它，即便保留 EPD 的 encoder/decoder/prefill 拆分与请求路由机制，系统平均 goodput 仍掉一半，说明仅靠架构设计无法替代为异构 LMM 工作负载搜索最优 batch/cache/并行配置的作用。

3) **实验链路作用**：该表作为消融实验，剥离"架构 vs. 配置搜索"两个独立贡献，验证 EPD 系统的收益同时来源于分离式服务架构与离线优化器；这一结论支撑了论文后续在 SLO attainment 等端到端指标中 EPD 全面优于基线的主张。

### Table 6 (p.9) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab06.png]]
> [!quote] caption
> Ablating dynamic role-switching from EPD de- grades TPOT by 2.4× and increases end-to-end latency by 2.2×. Results are averaged over 100 requests with one 4K image each. ↓ indicates lower is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**1) 核心对象与数据**：Table 6 为消融实验，对比 EPD 完整方案与去除动态角色切换（w/o Switch）在三项指标的表现——Latency 28.01→61.10s（劣化 2.2×）、TPOT 0.05→0.12s（劣化 2.4×）、TTFT 1.42→1.33s（0.9×）。实验模拟负载突变：100 请求、到达率 3 req/s、前 10 个请求生成 50 token、剩余 90 个生成 500 token，每请求配 1 张 4K 图像。

**2) 关键结论**：动态角色切换是 EPD 架构的核心设计；移除后 TPOT 与端到端延迟显著恶化，而 TTFT 反而略优（0.9×），说明无切换时系统被预 fill 阻塞、拖累解码，证实动态切换对负载自适应的必要性。

**3) 在论文中的作用**：作为关键消融，与 Figure 6 的 TTFT 分布图等共同支撑"EPD 解耦 + 动态角色"提升多模态大模型服务效率的核心论点。

### Table 7 (p.12) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab07.png]]
> [!quote] caption
> SLO attainment results ( ↑ ) for online audio bench- marking with ultravox-v0 3 (24 audio files per re- quest). All baselines use 4 GPUs: vLLM operates in data- parallel (DP) mode, DistServe uses a 3P1D configuration, and EPD adopts a 2E1P1D setup. EPD achieves consis- tently high SLO attainment and

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读：**

该表以 Ultravox-v0.3 音频在线基准（每请求24音频文件）、4 GPU 为统一条件，横向对比 vLLM（DP）、DistServe（3P1D）与 EPD（2E1P1D）在 0.10–1.15 r/s 六档请求率下的 SLO Attainment 及 Goodput。数据上，低负载（≤0.25 r/s）三者均≥0.94 接近饱和；高负载下差距凸显，1.15 r/s 时 EPD=0.93、vLLM=0.87、DistServe=0.68；Goodput 方面 EPD=1.16 r/s，约为 DistServe（0.45）的 2.6 倍。

原文借此论证：**EPD 在音频多模态场景下具备持续高 SLO 达成率与最高有效吞吐**。

在全篇中，该表与文本/图像基准互为补充，作为 EPD disaggregation 框架在**音频模态**上的端到端验证，支撑其相对 vLLM、DistServe 的全面优势结论。

### Table 8 (p.12) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab08.png]]
> [!quote] caption
> Comparison of maximum supported KV cache size (in terms of percentage of free memory) on prefill node for various #images/ request. Image resolution fixed to 4K. Higher ( italicized ) is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

1) **对象与数据**：表比较两种方案（vLLM vs EPD，斜体为更优）在 4K 分辨率下，prefill 节点上 KV 缓存可占空闲显存的最大百分比。InternVL2-8B：5/10 张图分别为 94%→*95%*、89%→*91%*，20 张时两者均 OOCL；InternVL2-26B：5 张 67%→*89%*、10 张 36%→*80%*、20 张 vLLM OOM 而 EPD 达 *63%*、40 张 EPD OOCL。

2) **关键结论**：随每请求图像数增多，EPD 优势显著放大——EPD 通过将视觉编码外置，使 prefill 节点获得更大 KV 缓存预算，从而避免 vLLM 早出现的 OOM/OOCL。

3) **论文作用**：作为消解论证（与 Figure 8 互证），证明 EPD 解耦架构在多图像高并发场景下能维持更大批处理与更高吞吐，支撑"更高效服务大模型多模态推理"的核心主张。

### Table 9 (p.16) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab09.png]]
> [!quote] caption
> TTFT and TPOT values (in seconds) used as SLO thresholds for different models and image counts per request (#I/R). Respective values are shown for MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读**

Table 9 给出 MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B 三模型在每请求图像数 #I/R∈{2,4,6,8} 下的 TTFT 与 TPOT 阈值（秒）。TTFT 随图像数近似线性增长：8B 模型从 1.20s 升至 5.00s，26B 模型从 3.50s 跃至 15.00s；TPOT 多维持在 0.04–0.18s，仅 26B 在 #I/R=6 出现 0.95s 异常尖峰。该表为 Figure 9 的 SLO attainment 评估提供基准阈值，与正文相互印证：EPD 解耦方案是唯一在严格 TTFT 约束下仍能满足 SLO 的配置，PD/TD 等基线在高请求率下完全无法达标。该表在论文实验链路中承担"评价标尺"作用，支撑 EPD disaggregation 在严苛 SLO 场景下的核心有效性主张。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\max_{(\mathbf{p},\mathbf{b},\mathbf{s}) \in \mathcal{X}} f(\mathbf{p},\mathbf{b},\mathbf{s}) - \beta cost(\mathbf{p})
$$

$$
\max_{(\mathbf{p}, \mathbf{b}, \mathbf{s}) \in \mathcal{X}} f(\mathbf{p}, \mathbf{b}, \mathbf{s}) - \beta \cdot \text{cost}(\mathbf{p})
$$

$$
v_t^e = E(i_m)
$$

$$
v_t^p = \psi_{EP}(v_t^e)
$$

$$
kv_1^p, o_1^p = P(v_t, i_p)
$$

$$
kv_1^d, o_1^d = \psi_{PD}(kv_1^p, o_1^p)
$$

$$
kv_{t+1}^d, o_{t+1}^d = D(kv_t^d, o_t^d)
$$

## 相关论文

- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

## 技术点深读（DEEP）

![[deep/efficiently-serving-large-multimodal-models-using-epd-disaggregation]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficiently-serving-large-multimodal-models-using-epd-disaggregation.txt`（69151 字符）供引用检索。