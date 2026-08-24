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
> 【图文联合解读】**图1联合解读**

图1为甘特式调度图，对比两种架构：①**聚合（DP=4）**：4块GPU同时承载编码E与LLM预填充，4行依次为E¹→LLM¹、E²→LLM²、E³→LLM³、E⁴→LLM⁴→**E⁵→LLM⁵**，其中第4行LLM⁴占据GPU时间长，直接队头阻塞后续请求E⁵的编码启动。②**解耦（E=1, P=3）**：编码独占1块GPU流水处理E¹/E³/E⁴/E⁵，3块prefill GPU并行LLM¹-LLM⁵预填充，编码与LLM不再串行争用。

**技术结论**：直观论证EPD解耦可消除编码—预填充阶段间的资源争用与队头阻塞。

**论文作用**：与Table 1（EPD在所有视频长度下TTFT最低）互为印证，作为全文方法动机的核心可视化证据。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig02.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]]*
> [!quote] caption
> Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi- cantly increases capacity, enabling larger batches and higher- resolution inputs. This demonstrates the memory efficiency benefits of disaggregation. representations. This stage is computationally intensive, especially for high-resolution or complex

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心数据**：图示 MiniCPM-V 2.6 在不同每请求图像数（1/3/5/15/20/30/40）下，Disaggregated（蓝）与 Aggregated（绿）方案支持的最大批大小。1图时蓝≈48 vs 绿≈6；3图蓝≈17 vs 绿≈2；5图蓝≈7 vs 绿≈1；15图起绿方出现 OOM，蓝方仍可支持小批量。

2) **关键结论**：将 LLM 从编码端 GPU 摘除（EPD 解耦）后，显存释放使单请求图像数与批容量均显著提升；高并发/多图场景下 Aggregated 直接 OOM，解耦方案才可服务。

3) **论文作用**：作为论文 EPD Disaggregation 核心动机的实验依据，定量证明"编码—预填—解码"三阶段解耦相较聚合部署在显存效率上的优势，支撑后续 Table 2 跨模型对比与框架设计论证。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig03.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]]*
> [!quote] caption
> The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from prefill to de- code, respectively. We denote the input text prompt as ip, multimodal data as im, and the output text as o. The steps are as follows:

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示EPD Disaggregation的三阶段推理流水线结构：E GPUs（黄）负责Encoding Stage，经EP Migration迁移至P GPUs（橙）的Prefill Stage，再经PD Migration迁移至D GPUs（绿）的Decode Stage；每阶段含独立输入队列（Encoding/Prefill/Decode Queue），底部分别设EP Bridge Queue与PD Bridge Queue实现跨阶段数据缓冲。

**论证结论**：通过将多模态编码、文本预填、解码三类异构负载解耦到独立GPU池，并配合桥接队列迁移，可针对性解决"编码瓶颈"问题，使各阶段按需独立扩缩。

**论文作用**：作为核心架构图，奠定了Table 3对比E/P阶段最大批大小差异的实验基础，是全文方法论与评估链路的基石。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-fig04.png]]
*整页渲染: ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]]*
> [!quote] caption
> System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM weights for decoding tasks and use the KV cache.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图中为三阶段流水线：编码器 E 将图像 \(i_{m_t}\) 转为高维嵌入 \(v_t^e\)，经 EP 迁移至 Prefill(P)，结合文本提示 \(i_p\) 生成初始 KV 与首个 token \(o_1^P\)；再经 PD 迁移至 Decode(D)，以 \(kv_{t+1}^d\) 更新并循环至输出结束。E/P/D 独立部署、按 DP 并发请求，从而解耦资源、按阶段扩缩容；IRP 消融中，移除后 TTFT 最多恶化 2.9×。所给图片是公式段落，并非 Figure 4 架构图。

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

### Table 2 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab02.png]]
> [!quote] caption
> Comparison of the maximum number of images supported per request for various image resolutions across different models. Higher values are better; best values in each row are italicized.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比 DistServ 与 EPD 在 MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B 三种模型、三种分辨率（313,234/787,444/4032,3024）下每请求支持的最大图像数。EPD 在 MiniCPM-V 2.6 上由 77/26/7 跃升至 490/165/49（约 6–7 倍）；InternVL2-26B 由 1/11/1 提升至 10/45/10；InternVL2-8B 则恒为 19。原文借此论证：分离 LLM 显著释放显存，使每请求可容纳更多图像，验证 EPD 架构的显存效率优势；该表与 Figure 2 共同构成支撑方法有效性的关键实验证据。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab03.png]]
> [!quote] caption
> Comparison of the maximum supported batch sizes for E and P stages across different models and image reso- lutions. Higher values are better; italicized values indicate the best in each row. OOM denotes cases where the model ran out of memory.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## 表3 联合解读

**核心对象与数据**：对比DistServe与EPD在MiniCPMv2.6、InternVL2-8B、InternVL2-26B三个模型、三种图像分辨率（313×234 / 787×444 / 4032×3024）下E、P阶段最大支持batch size。EPD对E阶段扩批效果显著：MiniCPMv2.6在313×234下E由7→49、P由7→86；InternVL2-8B在787×444下E由9→67。高分辨率4032×3024场景下DistServe多次OOM（如MiniCPMv2.6、InternVL2-26B三档全OOM），而EPD仍可运行（MiniCPMv2.6: E=4, P=9）。

**关键技术结论**：E与P解耦后，编码阶段可独立扩批，突破DistServe将E/P绑定在同一实例上的显存瓶颈，对大模型+高分辨率场景尤为有效。

**论文链路作用**：作为对比实验，为Figure 3所述EPD分离推理流水线提供量化证据，支撑"解耦提升吞吐与可扩展性"的核心主张。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab04.png]]
> [!quote] caption
> Effect of ablating IRP feature from the proposed system on TTFT (s). Disabling IRP negatively affects the TTFT (up to 2.9x worse ) for various multiple images/ re- quest (#I/R). Results are averaged over 100 requests.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4 对比 EPD 启用/禁用 IRP 在 #I/R=2/4/6/8 四档负载下的 TTFT（100 请求均值）：启用时为 0.92 / 1.02 / 1.14 / 1.74 s；禁用后升至 1.46 / 2.47 / 3.37 / 4.27 s，分别劣化 1.6×、2.4×、2.9×、2.5×。原文据此论证 IRP 是降低首 token 延迟的关键调度组件，在 #I/R=6 中等负载时收益最大（2.9×）。该表属 4.4 消融研究，与 Figure 4 架构图呼应，通过逐项剔除核心模块，证明 EPD 解聚推理设计的完整性与各组件不可替代性。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab05.png]]
> [!quote] caption
> Ablating the offline optimizer reduces goodput by 2.2× on average when configurations are selected randomly. ↓ indicates lower is better; ↑ indicates higher is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读：**

该表为消融实验，对比 EPD 完整方案与"去掉离线优化器（w/o Opt.）"在随机配置下的三项指标：Goodput 由 1.25 r/s 降至 0.56（劣化 2.2×），TTFT 由 2.12s 升至 4.48s（劣化 2.1×），TPOT 略优（0.025s vs 0.031s，因并发降低所致）。

**技术结论**：离线优化器在随机配置场景下是 EPD 取得高吞吐与低首 token 时延的关键组件，缺失后 goodput 平均下降 2.2×，证明其不可替代性。

**论文作用**：作为方法链路中的消融验证环节，定量支撑 EPD 系统中"搜索最优编码/解码资源配比"这一设计点的必要性与有效性。

### Table 6 (p.9) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab06.png]]
> [!quote] caption
> Ablating dynamic role-switching from EPD de- grades TPOT by 2.4× and increases end-to-end latency by 2.2×. Results are averaged over 100 requests with one 4K image each. ↓ indicates lower is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 联合解读**

Table 6 为 EPD 消融实验：对比完整 EPD（Latency 28.01s、TTFT 1.42s、TPOT 0.05s）与去掉动态角色切换（61.10s、1.33s、0.12s）。负载为 100 个含 4K 图像请求，前 10 个生成 50 token、后 90 个生成 500 token，到达率 3 req/s。**去除切换使 TPOT 劣化 2.4×、端到端延迟增加 2.2×，而 TTFT 几乎不变（0.9×）**。

论文借此论证：动态角色切换是 EPD 解聚合框架不可或缺的核心机制而非可选项——当请求输出长度从短到长跨阶段跃迁时，若 EPD 实例不能动态重分配 Encode/Prefill/Decode 角色，长输出阶段将产生严重排队，TPOT 与端到端延迟显著劣化。该表是论文实验链路中的关键一节，验证了 EPD 方法在动态工作负载下的鲁棒性。

### Table 7 (p.12) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab07.png]]
> [!quote] caption
> SLO attainment results ( ↑ ) for online audio bench- marking with ultravox-v0 3 (24 audio files per re- quest). All baselines use 4 GPUs: vLLM operates in data- parallel (DP) mode, DistServe uses a 3P1D configuration, and EPD adopts a 2E1P1D setup. EPD achieves consis- tently high SLO attainment and

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 联合解读**

Table 7 在4 GPU、ultravox-v0_3音频（24文件/请求）条件下，对比vLLM-DP、DistServe-3P1D、EPD-2E1P1D在0.10–1.15 r/s六档请求率下的SLO达标率与goodput。EPD全程≥0.93，DistServe自0.50 r/s起下滑至高负载0.68，vLLM居中为0.87–0.91；goodput分别为1.16、0.45、1.01 r/s。论文借此论证EPD解耦方案在多模态在线音频服务兼顾SLO达标与最高吞吐，验证方法在视觉之外的跨模态可扩展性，是实验链路上"从图像到音频"的泛化关键证据。

### Table 8 (p.12) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab08.png]]
> [!quote] caption
> Comparison of maximum supported KV cache size (in terms of percentage of free memory) on prefill node for various #images/ request. Image resolution fixed to 4K. Higher ( italicized ) is better.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 联合解读：**

**1）核心对象与数据：** 对比两种方案（EPD vs 基线，斜体为优）在 prefill 节点可支持的最大 KV cache 占空闲内存比，图像固定 4K。InternVL2-8B：5 张图 94% vs 95%、10 张图 89% vs 91%、20 张图均 OOCL；InternVL2-26B：5 张图 67% vs 89%、10 张图 36% vs 80%、20 张图 OOM vs 63%、40 张图 OOM vs OOCL。

**2）关键结论：** EPD 将视觉编码解耦后，prefill 节点不再背负图像 embedding 显存压力，可用 KV cache 余量大幅提升；优势随模型规模与图像数放大——26B 在 10 张图时差距达 44 个百分点，20 张图时基线 OOM 而 EPD 仍可分配 63%。

**3）论文作用：** 为"EPD 解耦提升显存效率与并发吞吐"的核心主张提供量化佐证，与吞吐/时延实验互补。

### Table 9 (p.16) ⭐深度解读
![[assets/crops/efficiently-serving-large-multimodal-models-using-epd-disaggregation-tab09.png]]
> [!quote] caption
> TTFT and TPOT values (in seconds) used as SLO thresholds for different models and image counts per request (#I/R). Respective values are shown for MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 联合解读**

1. **核心对象与数据**：表给出 MiniCPM-V 2.6、InternVL2-8B、InternVL2-26B 三模型在每请求图像数 #I/R=2/4/6/8 下的 TTFT 与 TPOT（秒）SLO 阈值。例如 InternVL2-26B 的 TTFT 从 3.50 (#I/R=2) 升至 15.00 (#I/R=8)，远高于另两模型；TPOT 多在 0.04–0.18s 区间，仅 #I/R=6 时 26B 达 0.95s。

2. **关键结论**：作为实验基准的 SLO 上限，为 Figure 9 中"EPD 是唯一在低请求率下仍满足全部 SLO、而其他基线全部失效"的判断提供量化依据；图像越多 TTFT 阈值越松，反映多模态推理本身的高延迟。

3. **链路作用**：服务于 EPD 解聚方案评估——先设定分模型/分图像规模的时延门槛，再以此衡量端到端调度是否能达标，是论文实验部分"门槛—测量—结论"链条的核心输入。

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