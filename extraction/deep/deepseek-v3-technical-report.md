# DeepSeek-V3 — 技术点深读（DEEP 2026-08-18 重跑）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：DeepSeek-V3 Technical Report · arXiv:2412.19437v2 (18 Feb 2025)
> 公式权威源 = formulas.json LaTeX（`$$` 包裹，完全正确）；图上下文走 M3 caption 文本（subagent 禁图直读）。

## 核心问题

如何在 **单次预训练** 中把一个 671B 总参 / 37B 激活的 Mixture-of-Experts (MoE) 模型训到与 GPT-4o、Claude-3.5-Sonnet 相当的开源水平，同时把全流程成本压到 **2.788M H800 GPU 小时（$5.576M）**，并且训练全程无不可恢复 loss spike、无回滚（§1, Table 1）。这要求同时解决三重矛盾：(1) MoE 跨节点 all-to-all 通信导致 ~1:1 的算通比恶化；(2) 传统 auxiliary-loss 负载均衡与模型性能相冲突；(3) FP8 低精度训练在大规模语言模型预训练上受 outlier 与累加精度不足掣肘，此前极少在超大规模 LM 预训练中成功（§3.3 引言：Fishman et al. 2024 指出"relatively few studies demonstrating successful application of low-precision techniques in large-scale language model pre-training"）。DeepSeek-V3 给出的回答是用 **MLA + DeepSeekMoE + auxiliary-loss-free 负载均衡 + MTP + FP8 混合精度 + DualPipe** 的算法-框架-硬件协同设计，把上述瓶颈逐一消解。

## 关键创新点

1. **Multi-head Latent Attention (MLA) — KV cache 低秩联合压缩**（§2.1.1, Eq. 1-11）。核心是对 key/value 做 low-rank 联合压缩，把 KV cache 压到 latent 向量：

$$\mathbf{c}_{t}^{KV} = W^{DKV} \mathbf{h}_{t},$$

$$[\mathbf{k}_{t, 1}^{C};\mathbf{k}_{t, 2}^{C};...;\mathbf{k}_{t, n_{h}}^{C}] = \mathbf{k}_{t}^{C} = W^{UK} \mathbf{c}_{t}^{KV},$$

$$\mathbf{k}_{t}^{R} = \operatorname{RoPE}({W^{KR}} \mathbf{h}_{t}), \quad \mathbf{k}_{t, i} = [\mathbf{k}_{t, i}^{C}; \mathbf{k}_{t, i}^{R}],$$

$$[\mathbf{v}_{t, 1}^{C};\mathbf{v}_{t, 2}^{C};...;\mathbf{v}_{t, n_{h}}^{C}] = \mathbf{v}_{t}^{C} = W^{UV} \mathbf{c}_{t}^{KV}.$$

机制：`c_t^KV ∈ R^{d_c}`（d_c=512 ≪ d_h·n_h=128·128=16384）为压缩 latent；上投影 W^UK/W^UV 还原多头 K/V；RoPE 走**解耦共享 key** `k_t^R`（d_h^R=64），不经过压缩通道以保留位置信息（Eq. 3）。推理时只缓存 `c_t^KV` 与 `k_t^R` 两个蓝框向量，KV cache 大幅压缩而保持与 MHA 可比的性能（§2.1.1 末段）。Query 同样做压缩 `c_t^Q = W^DQ h_t`（d'_c=1536）以降低训练激活显存（Eq. 6-9）。注意力分母用 `sqrt(d_h + d_h^R)`：

$$\mathbf{o}_{t, i} = \sum_{j=1}^{t} \operatorname{Softmax}_j\left(\frac{\mathbf{q}_{t, i}^T \mathbf{k}_{j, i}}{\sqrt{d_{h} + d_{h}^{R}}}\right) \mathbf{v}_{j, i}^{C}, \quad \mathbf{u}_{t} = W^{O} [\mathbf{o}_{t, 1};\mathbf{o}_{t, 2};...;\mathbf{o}_{t, n_{h}}].$$

**图源校验**：Figure 2（架构图）M3 解读确认——MLA 部分只把 `Latent c_t^KV` 与 `k_t^R` 标为 "Cached During Inference"（蓝框），与 LaTeX Eq. 1-5 的"only the blue-boxed vectors need to be cached"完全一致；LaTeX↔M3 双源吻合。这是相对 GQA 更深的 KV 压缩后继者（→ [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]）。

2. **DeepSeekMoE + Auxiliary-Loss-Free 负载均衡**（§2.1.2, Eq. 12-16）。FFN 输出为 shared + routed 求和：

$$\mathbf{h}_{t}^{\prime} = \mathbf{u}_{t} + \sum_{i=1}^{N_{s}} {\operatorname{FFN}^{(s)}_{i}\left( \mathbf{u}_{t} \right)} + \sum_{i=1}^{N_r} {g_{i,t} \operatorname{FFN}^{(r)}_{i}\left( \mathbf{u}_{t} \right)},$$

$$g_{i,t} = \frac{g^{\prime}_{i,t}}{\sum_{j=1}^{N_r} g^{\prime}_{j,t}}, \quad s_{i,t} = \operatorname{Sigmoid} \left( {\mathbf{u}_{t}}^{T} \mathbf{e}_{i} \right).$$

机制：N_s=1 shared、N_r=256 routed、K_r=8 激活、expert intermediate dim 2048；前 3 层保留 dense FFN，其余替换为 MoE。与 V2 的差异：gating 用 **sigmoid**（而非 softmax）算 affinity，再对 top-K 选中项做归一化得 gating value（Eq. 13-15）。**Aux-loss-free 机制**：为每个 expert 引入 bias b_i，仅参与 top-K 路由决策，而乘到 FFN 输出的 gating value 仍用原始 affinity s_i,t：

$$g^{\prime}_{i,t} = \begin{cases} s_{i,t}, & s_{i,t} + b_i \in \operatorname{Topk} (\{ s_{j, t} + b_j | 1 \leq j \leq N_r \}, K_{r}), \\ 0, & \text{otherwise}. \end{cases}$$

即"路由用带 bias 的、加权用不带 bias 的"，从而不污染前向信号（§2.1.2 "the bias term is only used for routing... still derived from the original affinity score"）。训练每步末按 expert 是否过载把 b_i 减/加 γ（bias update speed γ=0.001，前 14.3T tokens 用 0.001，最后 500B 降为 0.0）。再补一个极小的 sequence-wise balance loss（α=0.0001）防止单序列内极端失衡：

$$\mathcal{L}_{\mathrm{Bal}} = \alpha \sum_{i=1}^{N_r}{f_i P_i}, \quad f_i = \frac{N_r}{K_r T} \sum_{t=1}^{T} \mathds{1}\left( s_{i,t} \in \operatorname{Topk}(\cdot) \right), \quad P_i = \frac{1}{T} \sum_{t=1}^{T}{s^{\prime}_{i,t}}.$$

消融显示 aux-loss-free 在 Small/Large MoE 上多数 benchmark 持续优于纯 aux-loss-based（Table 5，如 Large MoE MATH 37.2→39.6、GSM8K 70.7→74.5），且 expert 专业化更强（§4.5.3, Figure 9）。**No token-dropping**：训练与推理都不丢 token（§2.1.2）。

3. **Multi-Token Prediction (MTP) 训练目标**（§2.2, Eq. 21-25）。用 D 个顺序 MTP 模块预测 D 个额外 token（DeepSeek-V3 取 **D=1**）。第 k 模块 = 共享 embedding + 共享 output head + 一个 Transformer block TRM_k + 投影矩阵 M_k∈R^{d×2d}；输入为：

$$\mathbf{h}_i^{\prime k} = M_k [\operatorname{RMSNorm}(\mathbf{h}_i^{k-1}) ; \operatorname{RMSNorm}(\operatorname{Emb}(t_{i+k}))],$$

$$\mathbf{h}_{1:T-k}^{k} = \operatorname{TRM}_k(\mathbf{h}_{1:T-k}^{\prime k}), \quad P_{i+k+1}^{k} = \operatorname{OutHead}(\mathbf{h}_{i}^{k}).$$

**与 Gloeckle et al. 2024 的关键差异**：顺序预测、保留完整因果链（"keep the complete causal chain at each prediction depth"），而非并行独立 head（§2.2）。MTP 损失：

$$\mathcal{L}_{\text{MTP}}^{k} = \operatorname{CrossEntropy}(P_{2 + k:T + 1}^{k}, t_{2 + k:T + 1}) = -\frac{1}{T} \sum_{i=2 + k}^{T + 1} \log P_i^k [t_i],$$

$$\mathcal{L}_{\text{MTP}} = \frac{\lambda}{D} \sum_{k=1}^{D} \mathcal{L}_{\text{MTP}}^{k}.$$

λ=0.3（前 10T tokens）→ 0.1（后 4.8T）。推理时可丢弃 MTP 模块独立运行，或转为 speculative decoding。消融（Table 4）：MTP 在 Small MoE (15.7B/1.33T) 与 Large MoE (228.7B/540B) 上多数 benchmark 持续涨点（如 Large MATH 38.6→39.8、GSM8K 72.3→74.0、HumanEval 44.5→53.7）。MTP 第二 token 接受率 85%-90%，配合 speculative decoding 达 **1.8× TPS**（§5.4.3）。

4. **DualPipe 双向流水线并行**（§3.2.1, Figure 4-5, Table 2）。把每个 chunk 切成 attention / all-to-all dispatch / MLP / all-to-all combine 四段，backward 进一步拆成 backward-for-input 与 backward-for-weights（类 ZeroBubble）；手动调整 SM 在通信/计算间的配比，使 all-to-all 与 PP 通信完全被计算掩盖。**双向**调度从流水线两端同时喂 micro-batch。

**图源校验（Figure 4，M3 caption）**：M3 解读确认其为"两行时间线"——上行 Computation 为 ATTN/MLP 的 Forward(F) / Backward-for-input(B) / Backward-for-weights(W) 子算子序列，"boundaries of the transformer blocks are not aligned"（边界故意错位）；下行 Communication 为 DISPATCH / COMBINE / 中央 PP 块。M3 要点："Both all-to-all and PP communication can be fully hidden"——与 LaTeX §3.2.1 文本"we can ensure that both all-to-all and PP communication can be fully hidden during execution"双源吻合。Bubble 公式（Table 2）：

| 方法 | Bubble | 参数 | 激活 |
|---|---|---|---|
| 1F1B | (PP−1)(F+B) | 1× | PP |
| ZB1P | (PP−1)(F+B−2W) | 1× | PP |
| **DualPipe** | **(PP/2−1)(F&B+B−3W)** | **2×** | **PP+1** |

F=forward chunk；B=full backward chunk；W=backward-for-weights chunk；F&B=互相重叠的 forward+backward chunk。DualPipe 在双向+重叠下显著减少 bubble；激活显存仅多 1/PP（需保留两份模型参数，但 EP 大时影响小）。与 Chimera 不同，只要求 PP stages 和 micro-batches 能被 2 整除即可；bubble 与激活不随 micro-batch 数增长（§3.2.1）。

5. **跨节点 all-to-all 通信 kernel**（§3.2.2）。集群：2048 H800，节点内 NVLink 160 GB/s（≈3.2× IB 的 50 GB/s），节点间 IB。策略：(a) 限制每 token 至多路由到 M=4 节点；(b) token 先经 IB 到目标节点的同 in-node index GPU，再经 NVLink 立即转发到持有目标 expert 的 GPU，IB 与 NVLink 完全重叠；(c) 每 token 平均 3.2 experts/节点，意味着虽实际激活 8 experts，可在不增加通信开销下扩到 4×3.2≈13 experts 上限。**只需 20 个 SM**（H800 共 132 SM）即可打满 IB+NVLink 带宽，用 warp specialization 切 10 个通信 channel，dispatch/combine 各 3 类 warp（IB send / IB→NVLink forward / NVLink recv 等），动态调 warp 数；用定制 PTX 指令 + 自动调 chunk size 降低 L2 占用与对其他 SM 的干扰。

6. **FP8 混合精度训练框架（首次在超大规模 LM 上验证）**（§3.3, Figure 6-7）。核心要点：

**图源校验（Figure 6，M3 caption）**：M3 解读确认该图为 Linear 算子的混合精度数据流——Fprop 中 BF16 Input cast 到 FP8 与 FP8 Weight 做 GEMM、FP32 累加出 BF16 Output；Dgrad 同理（FP8 输出梯度 × FP8 weight → FP32 累加 → BF16 输入梯度）；Wgrad 用缓存的前向 FP8 input × FP8 输出梯度、FP32 累加出 FP32 权重梯度，喂入 BF16 Optimizer States 更新 FP32 Master Weight 再 re-quantize 回 FP8。M3 要点："compute-heavy GEMMs (Fprop, Dgrad, Wgrad) run in FP8 with FP32 accumulation, while inputs/outputs, optimizer states, and master weights stay in higher precision"——与 §3.3.1 文本与 Figure 6 caption 双源吻合。

- **三类 GEMM 全 FP8**：Linear 的 Fprop / Dgrad / Wgrad 都 FP8 输入、BF16/FP32 输出，理论 2× BF16 速度；Wgrad 用 FP8 反而允许激活以 FP8 缓存（省显存）。保持原始高精度的组件：embedding、output head、MoE gating、norm、attention；master weight / weight grad / optimizer states 保 FP32/BF16。
- **细粒度量化**（Figure 7a）：activation 用 1×128 tile（per token per 128 channels），weight 用 128×128 block；per-group scaling factor 沿 GEMM 内维 K。与 microscaling formats（Rouhani 2023b）思路一致，先于 Blackwell 原生支持。
- **提升累加精度**（Figure 7b）：H800 Tensor Core 的 FP8 GEMM 累加仅保留约 14 bit（K=4096 时最大相对误差近 2%）。采用 promotion to CUDA Cores（Thakkar 2023），每 N_C=128 个 FP8×FP8 乘积复制到 CUDA Core 的 FP32 register 做全精度累加，并把 per-group scaling factor 在 CUDA Core 上做反量化。两 WGMMA 并发（一个 promote、一个 MMA）维持利用率。
- **Mantissa over Exponents**：所有张量统一用 E4M3（而非前作的 Fprop E4M3 / Dgrad+Wgrad E5M2 混合），靠细粒度分组共享指数位弥补动态范围。
- **Online quantization**：在线算每 1×128 / 128×128 的 max abs 推导 scale，取代依赖历史 max 的 delayed quantization。
- **低精度存储/通信**：optimizer 的 AdamW 一阶/二阶矩用 BF16（master weight 与 grad 仍 FP32）；attention 后 Linear 输入用定制 E5M6 格式（sensitive），scale 取 2 的整数次幂；SwiGLU 输入 FP8 缓存并重算输出；MoE up-projection 前激活量化为 FP8 再 dispatch；forward/backward combine 保留 BF16。
- **验证**：在 V2-Lite 与 V2 量级上训 ~1T tokens，相对 BF16 的 loss 误差 **持续 <0.25%**（§3.3, Appendix B.1, Figure 10）。Appendix B.2 警告：对 Dgrad 的 activation gradient 做块级 128×128 量化会导致 16B MoE 训练发散（token-correlated outliers 无法被 block-wise 管理）。

7. **推理部署：prefilling 与 decoding 分离 + redundant experts**（§3.4）。Prefilling 最小单元 4 节点 32 GPU：attention 用 TP4+SP+DP8，MoE 用 EP32，shallow dense MLP 用 TP1 省 TP 通信；设 **32 个 redundant experts**（每 GPU 原 8 experts + 1 redundant，每 10 分钟按在线负载统计调整）；同时处理两个相近负载 micro-batch 互相掩盖 attention 与 MoE。Decoding 最小单元 40 节点 320 GPU：把 shared expert 当 routed 处理 → 每 token 选 9 experts（shared 视为必选高载 expert）；attention TP4+SP+DP80，MoE EP320（每 GPU 仅 1 expert，64 GPU 负责 redundant+shared）；all-to-all 走 IB 点对点低延迟，用 IBGDA 进一步降延迟；decoding batch/expert ≤256 token，瓶颈是访存不是算力，只给 dispatch+MoE+combine 分配少量 SM。端到端生成速度 >2× DeepSeek-V2（§6）。

8. **Post-Training：从 DeepSeek-R1 蒸馏推理能力**（§5.1, §5.4.1）。SFT 数据 1.5M 实例。**推理数据用内部 DeepSeek-R1 生成**，但 R1 输出存在 overthinking/格式差/过长问题。方法论：先训一个领域 expert 模型（SFT+RL pipeline），生成两种样本 `<problem, original response>` 与 `<system prompt, problem, R1 response>`，system prompt 引导 reflection/verification；RL 阶段高温采样让中间 RL 模型在无显式 system prompt 时也融入 R1 模式；数百 RL 步后用 rejection sampling 产出简洁有效的 SFT 数据。蒸馏显著提升但会推长输出（Table 9：V2.5+R1 Distill 在 MATH-500 74.6→83.2，长度 769→1510；LiveCodeBench-CoT 31.1→37.4, 718→783），需在精度与长度间权衡。RL 用 GRPO（去 critic，用 group score 估 baseline）：

$$\mathcal{J}_{GRPO}(\theta) = \mathbb{E}\left[\frac{1}{G}\sum_{i=1}^G \left( \min \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)} A_i, \text{clip} \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)}, 1 - \epsilon, 1 + \epsilon \right) A_i \right) - \beta \mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right)\right)\right],$$

$$\mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right) = \frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)}- \log\frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)} - 1, \quad A_i = \frac{r_i - {\operatorname{mean}(\{r_1, \cdots, r_G\})}}{{\operatorname{std}(\{r_1, \cdots, r_G\})}}.$$

reward 分 rule-based（数学/LeetCode 可验证）与 model-based RM（V3 SFT checkpoint 训，含 CoT 防 reward hacking）。Self-rewarding 用 constitutional AI + V3 自身投票（§5.4.2）。

9. **硬件设计建议**（§3.5）。通信侧：希望未来芯片把 IB↔NVLink 转发、RDMA buffer 搬运、all-to-all combine reduce、细粒度内存布局管理从 SM 卸载到专用协处理器（类 SHARP），并统一 IB(scale-out) 与 NVLink(scale-up) 接口。计算侧：(a) Tensor Core 原生支持更高 FP8 GEMM 累加精度（Hopper 仅 14 bit 是缺陷）；(b) 原生支持 tile/block-wise 量化（接收 per-group scaling factor 并在 Tensor Core 内完成 MMA+反量化）；(c) 原生支持 online quantization（FP8 cast 与 TMA 访问融合，或近 HBM 计算）；(d) 支持转置 GEMM 读（forward 1×128 tile 存后 backward 需 128×1，目前要 dequant/transpose/requant）。

## 表格（原文结构化）

### Table 1 — 训练成本（§1）
| 阶段 | H800 GPU 小时 | USD（@$2/GPU·h）|
|---|---|---|
| Pre-Training | 2,664K | $5.328M |
| Context Extension | 119K | $0.238M |
| Post-Training | 5K | $0.010M |
| **Total** | **2,788K** | **$5.576M** |
注：每万亿 token 仅 180K H800 小时；2048 H800 集群约 3.7 天/万亿 token；不含研究/消融成本。

### 模型超参（§4.2）
| 项 | 值 |
|---|---|
| Transformer 层数 L | 61 |
| Hidden dim d | 7168 |
| 初始化 std | 0.006 |
| 注意力头数 n_h | 128 |
| 每头 dim d_h | 128 |
| KV 压缩 dim d_c | 512 |
| Query 压缩 dim d'_c | 1536 |
| 解耦 RoPE 每头 dim d_h^R | 64 |
| Shared experts N_s | 1 |
| Routed experts N_r | 256 |
| 每 token 激活 routed K_r | 8 |
| Expert intermediate dim | 2048 |
| Node-limited routing M | 4 节点 |
| MTP 深度 D | 1 |
| **Total params** | **671B** |
| **Activated params/token** | **37B** |

### 训练超参（§4.2）
| 项 | 值 |
|---|---|
| Optimizer | AdamW (β1=0.9, β2=0.95, weight_decay=0.1) |
| Max seq len（预训练） | 4K |
| 训练 tokens | 14.8T |
| LR warmup | 0→2.2e-4 over 2K steps |
| LR 常数 | 2.2e-4 到 10T tokens |
| LR cosine decay | 2.2e-4 → 2.2e-5 over 4.3T tokens |
| 末段 LR | 2.2e-5 (333B) → 7.3e-6 (167B) |
| Grad clip | 1.0 |
| Batch size schedule | 3072 → 15360（前 469B），后保持 15360 |
| Bias update speed γ | 0.001（前 14.3T）→ 0.0（后 500B） |
| Balance loss α | 0.0001 |
| MTP loss weight λ | 0.3（前 10T）→ 0.1（后 4.8T） |
| 并行策略 | 16-way PP + 64-way EP（跨 8 节点）+ ZeRO-1 DP |
| Tokenizer | Byte-level BPE, vocab 128K; FIM rate 0.1 (PSM) |

### Long Context Extension（§4.3）
| 阶段 | seq len | batch | steps | LR |
|---|---|---|---|---|
| Phase 1 | 32K | 1920 | 1000 | 7.3e-6 |
| Phase 2 | 128K | 480 | 1000 | 7.3e-6 |
YaRN：scale s=40, α=1, β=32, √t = 0.1·ln(s)+1，仅作用于解耦共享 key k_t^R。NIAH 128K 全长度表现稳健（Figure 8）。

### Table 3 — Base 模型对比（§4.4.2，节选）
| Benchmark | DeepSeek-V2-Base | Qwen2.5-72B-Base | LLaMA-3.1-405B-Base | **DeepSeek-V3-Base** |
|---|---|---|---|---|
| Pile-test (BPB) | 0.606 | 0.638 | 0.542 | **0.548** |
| BBH (EM) | 78.8 | 79.8 | 82.9 | **87.5** |
| MMLU (EM) | 78.4 | 85.0 | 84.4 | **87.1** |
| MMLU-Pro (EM) | 51.4 | 58.3 | 52.8 | **64.4** |
| HumanEval (Pass@1) | 43.3 | 53.0 | 54.9 | **65.2** |
| LiveCodeBench-Base (Pass@1) | 11.6 | 12.9 | 15.5 | **19.4** |
| MATH (EM) | 43.4 | 54.4 | 49.0 | **61.6** |
| C-Eval (EM) | 81.4 | 89.2 | 72.5 | **90.1** |
| MMMLU-non-English (EM) | 64.0 | 74.8 | 73.8 | **79.4** |

### Table 4 — MTP 消融（§4.5.1）
| Benchmark | Small Baseline | Small +MTP | Large Baseline | Large +MTP |
|---|---|---|---|---|
| # Total Params | 15.7B | 15.7B | 228.7B | 228.7B |
| # Training Tokens | 1.33T | 1.33T | 540B | 540B |
| BBH (EM) | 39.0 | 41.4 | 70.0 | 70.7 |
| HumanEval (Pass@1) | 20.7 | 26.8 | 44.5 | 53.7 |
| GSM8K (EM) | 25.4 | 31.4 | 72.3 | 74.0 |
| MATH (EM) | 10.7 | 12.6 | 38.6 | 39.8 |

### Table 5 — Aux-Loss-Free 消融（§4.5.2）
| Benchmark | Small Aux-Loss-Based | Small Aux-Loss-Free | Large Aux-Loss-Based | Large Aux-Loss-Free |
|---|---|---|---|---|
| # Training Tokens | 1.33T | 1.33T | 578B | 578B |
| BBH (EM) | 37.3 | 39.3 | 66.7 | 67.9 |
| HumanEval (Pass@1) | 22.0 | 22.6 | 40.2 | 46.3 |
| GSM8K (EM) | 27.1 | 29.6 | 70.7 | 74.5 |
| MATH (EM) | 10.9 | 11.1 | 37.2 | 39.6 |

### Table 6 — Chat 模型对比（§5.3.2，节选）
| Benchmark | DeepSeek-V2.5-0905 | Qwen2.5-72B-Inst | LLaMA-3.1-405B-Inst | Claude-3.5-Sonnet-1022 | GPT-4o-0513 | **DeepSeek-V3** |
|---|---|---|---|---|---|---|
| MMLU (EM) | 80.6 | 85.3 | 88.6 | 88.3 | 87.2 | **88.5** |
| MMLU-Pro (EM) | 66.2 | 71.6 | 73.3 | 78.0 | 72.6 | 75.9 |
| GPQA-Diamond (Pass@1) | 41.3 | 49.0 | 51.1 | 65.0 | 49.9 | 59.1 |
| DROP (3-shot F1) | 87.8 | 76.7 | 88.7 | 88.3 | 83.7 | **91.6** |
| SimpleQA (Correct) | 10.2 | 9.1 | 17.1 | 28.4 | 38.2 | 24.9 |
| LongBench v2 (Acc.) | 35.4 | 39.4 | 36.1 | 41.0 | 48.1 | **48.7** |
| LiveCodeBench (Pass@1-CoT) | 29.2 | 31.1 | 28.4 | 36.3 | 33.4 | **40.5** |
| Codeforces (Percentile) | 35.6 | 24.8 | 25.3 | 20.3 | 23.6 | **51.6** |
| SWE Verified (Resolved) | 22.6 | 23.8 | 24.5 | 50.8 | 38.8 | 42.0 |
| Aider-Polyglot (Acc.) | 18.2 | 7.6 | 5.8 | 45.3 | 16.0 | **49.6** |
| AIME 2024 (Pass@1) | 16.7 | 23.3 | 23.3 | 16.0 | 9.3 | **39.2** |
| MATH-500 (EM) | 74.7 | 80.0 | 73.8 | 78.3 | 74.6 | **90.2** |
| CNMO 2024 (Pass@1) | 10.8 | 15.9 | 6.8 | 13.1 | 10.8 | **43.2** |
| C-SimpleQA (Correct) | 54.1 | 48.4 | 50.4 | 51.3 | 59.3 | **64.8** |

### Table 7 — 开放对话评测（§5.3.3）
| Model | Arena-Hard | AlpacaEval 2.0 (LC win rate) |
|---|---|---|
| DeepSeek-V2.5-0905 | 76.2 | 50.5 |
| Qwen2.5-72B-Instruct | 81.2 | 49.1 |
| LLaMA-3.1 405B | 69.3 | 40.5 |
| GPT-4o-0513 | 80.4 | 51.1 |
| Claude-Sonnet-3.5-1022 | 85.2 | 52.0 |
| **DeepSeek-V3** | **85.5** | **70.0** |

### Table 8 — RewardBench（§5.3.4）
| Model | Chat | Chat-Hard | Safety | Reasoning | Avg |
|---|---|---|---|---|---|
| GPT-4o-0806 | 96.1 | 76.1 | 88.1 | 86.6 | 86.7 |
| Claude-3.5-sonnet-1022 | 96.4 | 79.7 | 91.1 | 87.6 | 88.7 |
| DeepSeek-V3 | 96.9 | 79.8 | 87.0 | 84.3 | 87.0 |
| DeepSeek-V3 (maj@6) | 96.9 | 82.6 | 89.5 | 89.2 | **89.6** |

### Table 9 — R1 蒸馏贡献（§5.4.1）
| Model | LiveCodeBench-CoT Pass@1 | Length | MATH-500 Pass@1 | Length |
|---|---|---|---|---|
| DeepSeek-V2.5 Baseline | 31.1 | 718 | 74.6 | 769 |
| DeepSeek-V2.5 +R1 Distill | 37.4 | 783 | 83.2 | 1510 |

### FP8 vs BF16 训练消融（§3.3, Appendix B.1）
- Small: ~16B total / 1.33T tokens；Large: ~230B total / ~0.9T tokens
- 相对 loss 误差 **<0.25%**（Figure 10 EMA 曲线，EMA 系数 0.9）

### Batch-wise vs Sequence-wise Balance（§4.5.3, 1B/3B MoE）
| MoE 规模 | sequence-wise aux loss | aux-loss-free | batch-wise aux loss |
|---|---|---|---|
| 1B val loss | 2.258 | 2.253 | 2.253 |
| 3B val loss | 2.085 | 2.080 | 2.080 |
结论：batch-wise 与 aux-loss-free 性能相当，均优于 sequence-wise；关键在平衡作用域（batch vs sequence）而非具体实现。

## 与同类对比

- **vs GPT-4o / Claude-3.5-Sonnet**：在 MMLU/MMLU-Pro/GPQA 上接近或略低，但在 math（MATH-500 90.2 > GPT-4o 74.6 / Claude 78.3；AIME 39.2 > Qwen 23.3 / Claude 16.0）、code competition（Codeforces 51.6 percentile，远超所有对手）、Chinese factual（C-SimpleQA 64.8 > GPT-4o 59.3 / Claude 51.3）上反超。工程类 coding（SWE-Verified 42.0 < Claude 50.8）略低于 Claude-3.5-Sonnet，但 Aider-Polyglot V3 49.6 反超 Claude 45.3。开放对话 Arena-Hard 85.5（首个超 85% 的开源模型）、AlpacaEval 2.0 70.0 显著领先。
- **vs Qwen2.5-72B-Inst（最强中文开源 dense）**：仅一半激活参数（37B vs 72B），英文/多语/code/math 全面领先；中文除 CMMLU 外多数领先；C-SimpleQA 领先 16.4 分（且 Qwen 用了 18T tokens，比 V3 的 14.8T 多 20%）。
- **vs LLaMA-3.1-405B-Inst（最大开源 dense）**：激活参数仅 1/11，multilingual/code/math 全面更好，英文/中文多数持平或更好。
- **vs DeepSeek-V2.5**：训练 V3 用 14.8T tokens（V2 系列量级更大但激活更小 21B），V3 在几乎所有 benchmark 大幅领先；端到端生成速度 >2× V2。

## 跨论文关系（→ MOC 谱系）

- **[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]**：R1 是 V3 的"老师"。V3 在 post-training 阶段通过 expert 模型 + RL pipeline 蒸馏 R1 的 long-CoT verification/reflection 模式（§5.4.1），在 math/code 上获得大幅提升（AIME、MATH-500、CNMO 2024 均显著超越同量级对手）。R1 系列 → V3 的蒸馏链路是 V3 报告的核心 post-training 贡献。
- **[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]**：MLA 是 GQA 思路的更深一步——不止共享 K/V head，而是用 low-rank 联合压缩把 KV cache 压到 latent 向量 c_t^KV（d_c=512 ≪ 16384），在保持 MHA 性能的同时把 KV cache 降到比 GQA 更低。两者同属"KV 压缩家族"，MLA 是后继演进。
- **[[muon-is-scalable-for-llm-training]]**：Moonlight 是基于 DeepSeek-V3-Small 架构（MoE + MLA）的模型；V3 提供了 MoE+MLA 的生产级架构范式与超参基线（256 routed + 1 shared, MLA d_c=512 等），Moonlight 等后续工作在此之上做优化器（Muon）层面的扩展。
- **[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]**：CloudMatrix 在生产环境 serve DeepSeek-V3 / R1。V3 报告自身的 H800 集群部署策略（prefilling EP32 + 32 redundant experts / decoding EP320 + shared-as-routed）为 CloudMatrix 这类超算服务提供了推理拓扑参考；CloudMatrix 进一步在 MLA 上做 INT8 量化、MoE dispatch 优化以适配 V3/R1 的大规模服务化。
- **DeepSeek-V2（前作，引用 DeepSeek-AI 2024c）**：V3 沿用 V2 的 MLA + DeepSeekMoE 双架构，但在 gating（sigmoid+topK norm 替代 softmax）、负载均衡（aux-loss-free 替代 aux-loss）、训练精度（FP8）、流水线（DualPipe）、训练目标（MTP）、规模（671B vs 236B, 14.8T tokens）上全面升级。
- **架构 (MLA) + 训练 (FP8/MTP) + 服务 (CloudMatrix) 三角锚点**：V3 是把这三条线收口的生产级模型——MLA 解决推理 KV 压力、FP8+DualPipe 解决训练成本、CloudMatrix 解决服务化部署，共同构成"开源 671B MoE 可经济训练与部署"的完整证据链。

## 局限与边界

- **部署单元大**：prefilling 最小 4 节点 32 GPU、decoding 最小 40 节点 320 GPU，对小团队是负担（§6）。
- **生成速度仍有空间**：虽 >2× V2，作者认为仍可进一步优化，寄望下一代硬件（§6）。
- **英文事实知识落后**：SimpleQA 24.9 落后 GPT-4o (38.2) 与 Claude (28.4)，因训练 token 向中文知识倾斜（§5.3.2）。
- **工程 coding 略弱**：SWE-Verified (42.0) 等工程任务略低于 Claude-3.5-Sonnet (50.8)（§5.3.2）。
- **FP8 训练脆弱性**：块级 128×128 量化对 Dgrad 的 activation gradient 会导致 16B MoE 训练发散（Appendix B.2，~300B tokens 处发散），需维持 1×128/128×1 不同分组的 tile-wise 量化，工程实现复杂。
- **DualPipe 双份参数**：需保留两份模型参数（靠大 EP 缓解），并非零成本。
- **MTP 仅 D=1**：未探索更深 MTP 链；推理时默认丢弃 MTP 模块，speculative decoding 是可选增益而非默认。
- **bias 调参敏感**：aux-loss-free 的 bias update speed γ 在末段需手动降为 0，表明该机制仍需人工调度而非完全自适应。
- **评测框架自研**：base 模型评测用内部 HAI-LLM 框架，与社区标准存在差异；作者注明 V2-Base 分数因框架更新而略有变化（§4.4.2）。
- **成本口径**：$5.576M 仅含官方训练，不含架构/算法/数据的 prior 研究与消融（§1）。
