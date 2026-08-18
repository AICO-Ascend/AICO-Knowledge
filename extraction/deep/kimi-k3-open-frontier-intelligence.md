# Kimi K3 — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Kimi K3: Open Frontier Intelligence (Kimi Team 技术报告) · arXiv:2607.24653

## 核心问题

开源 LLM 在 **test-time scaling（第二轴）** 上进展迅速（RL/长推理/agent），但 **pre-training foundation（第一轴）** 长期停滞在 1T-class 参数区间，导致"开源之间趋同、与最强闭源（Claude Fable 5 / GPT-5.6 Sol）差距拉大"。同时，scaling 两轴同时推进到 3T-class + 1M 上下文 + 长程 agentic RL，撞上三重系统瓶颈：(i) 长序列注意力的 KV cache 与算力二次膨胀；(ii) 2.8T MoE 在 expert-parallel 训练下的负载不均、内存爆炸、视觉编码器抖动；(iii) million-token agentic rollout 的尾延迟、KV cache 留存、沙箱状态持久化。

**Kimi K3 的回答**：在三个维度同时 scale 信息流——序列长度（Hybrid KDA+MLA）、网络深度（Attention Residuals）、宽度（Stable LatentMoE，16/896 路由专家）——配合原生多模态训练与 multi-effort agentic RL，叠加全栈基础设施（KDA kernel/Context Parallelism、MoonEP 完美均衡 EP、co-located 长上下文 RL + microVM 沙箱、KDA-aware 前缀缓存）。结果：**2.8T 总参 / 104B 激活 / 1M 上下文**，相对 K2 scaling efficiency 提升 **~2.5×**；开源 frontier 模型，权重全放，整体仅次于 Claude Fable 5 与 GPT-5.6 Sol，但显著领先其它开源与闭源对照。

## 关键创新点

### 1. Hybrid Attention：3 KDA + 1 Gated MLA 的 3:1 block 结构（§2.1）
- **机制**：每个 block = 3 层 Kimi Delta Attention（线性、固定大小 recurrent state）+ 1 层 Gated MLA（全局 softmax，NoPE），block 末再补一层 Gated MLA 保证最终层是全局注意力。KDA 在 chunk 内并行、跨 chunk 递推；MLA 用 DeepSeek-V2 的 latent KV 压缩（缓存低维 `c_t` 而非每头 K/V），K3 进一步加 **input-dependent full-rank output gate** `y_t = W_o[Sigmoid(W_g x_t) ⊙ õ_t]`（Eq.7）。MLA 全部用 NoPE，位置信息由 KDA 的递推门控/衰减隐式编码——**外推到 1M 上下文无需任何 RoPE rescaling / YaRN 调参**（§3.4）。
- **效果**：长上下文 token mixing 成本大幅下降、KV cache 固定、位置编码外推免调；full-rank gate 让每 token 可通道级调制全局注意力读取。

### 2. KDA 的 Lower-bounded decay + Full-rank output gate（§2.1.1）
- **机制**：KDA = delta-rule recurrence + channel-wise forget gate（继承 [[kimi-linear-an-expressive-efficient-attention-architecture]]）。K3 改两处：(a) **log-decay 下界有界化**——Kimi Linear 用无界 `g = -e^A Softplus(z) ∈ (-∞,0)`，K3 改为 `g = g_min·Sigmoid(e^A z) ∈ (g_min, 0)`，`g_min = -5` 固定，使每步保留率 `α > e^-5 ≈ 6.7e-3`，16-token tile 累计 log-decay ∈ (−80,0)，倒数 rescale 因子 < e^80 仍在 BF16 动态范围内（Eq.5、Fig.3）。(b) **输出 gate 改 full-rank**：原低秩 → `y_t = W_o[Sigmoid(W_g x_t) ⊙ RMSNorm(õ_t)]`（Eq.6），数据相关 full-rank 门控。
- **效果**：对角 tile 也能走稠密 Tensor Core matmul（消掉 Kimi Linear 的 position-pair diagonal 路径），训练/推理 kernel 统一高效；full-rank gate 提升表达力。与有界递推门控的先前工作（HGRN2、Griffin、RWKV-7）思路相近。

### 3. Attention Residuals (AttnRes)：跨层选择性信息检索（§2.2）
- **机制**：把"Transformer 用 attention 取代 RNN 时序累积"的方法论搬到**深度维度**——每个 layer l 用可学习 pseudo-query `q_l = w_l`，对 embedding（i=0）+ 前序各层输出 `f_i(h_i)` 做 softmax 注意力（`ϕ(q,k)=exp(q^T RMSNorm(k))`，RMSNorm 防大层输出压制权重），加权求和得 `h_l`（Eq.8-9）。为控内存/通信开销，分 L 层为 N 块（K3 取 **N=8、每块 12 层**、含 embedding 共 9 块），块内求和成单一表示 `b_n`，跨块做 full AttnRes；块内用 online-softmax 合并 partial sum（Eq.10）。推理时块级状态有界，可 online softmax 合并。
- **效果**：突破标准残差把所有历史压缩进单一 `h_l` 的 RNN 式瓶颈；深度信息流可选择性检索；O(L²d) 算力可负担（L<100），Block 形式把内存/通信从 O(Ld) 降到 O(Nd)。

### 4. Stable LatentMoE：896 路由专家 / 16 激活 + 三件套稳定化（§2.3）
- **机制**：LatentMoE 思路——shared 专家保留 full-width 通路，routed 专家在紧凑 latent 空间（K3 取 latent dim 3584 = 0.5× hidden）操作，使 896 路由专家 / 16 激活 / sparsity 56 在通信上可承受。极端稀疏放大两个失败模式（routed 支路四连矩阵乘的病态条件 + 近 10³ 专家的负载均衡失控），用三件套应对：
  - **Normalized LatentMoE**（§2.3.1）：expert 聚合后、up-projection 前插 RMSNorm，降低 routed 支路对 scale 的敏感度，同时降验证损失。
  - **SiTU-GLU**（§2.3.2，Eq.12）：对 SwiGLU 的 gate 与 up 两支分别套 smooth cap `β·tanh(x/β)`（`β1=4, β2=25`），原点附近一阶等价 SwiGLU、大值有界 `|f|≤β1·β2=100`（Eq.18-19），保 SwiGLU 局部响应同时控溢出，优于 hard clamp（梯度在饱和边界外仍非零）。附录 B 给局部展开与极限恢复 SwiGLU。
  - **Quantile Balancing (QB)**（§2.3.3，Eq.13-14）：auxiliary-loss-free 路由——`s_i = Sigmoid(W_r x_i)`，`T_i = argtopk(s_i + b)`，混合权重 `p_{i,j}=s_{i,j}/Σ_{r∈T_i} s_{i,r}`（bias 不进权重、不改梯度）。原 sign 更新 `b_{j}^{t+1}=b_j^t + γ·sign(ℓ̄−ℓ_j^t)` 在 896 专家下慢且振荡；QB 从单次前向算：取 `Top-(k+1)` 的第 (k+1) 大为 cutoff `α_i^(t)`，再令 `b̂_j^{t+1} = -quantile_{1−k/n}(s_{:,j} − α^(t))` 后 mean-center，使每专家恰好收到目标负载 `q=mk/n`。附录 C 给从 bipartite b-matching LP 对偶推出的**精确坐标极小化解**（Eq.20-26），证明 QB 即 SignSGD 一步到对偶极小值的闭式跳；附录 D 给**直方图分位估计**：每专家维护 `r_{i,j}=α_i−s_{i,j}` 的 binned 直方图，单次 all-reduce 汇总 nB 计数即恢复全局分位（B=1000 时误差 ≤几×10⁻³，通信 <1% 原始 margins 交换成本，与 token 分片无关）。推理时 bias 冻结。
- **效果**：896 专家下稳定训练、负载完美均衡、无需手调 γ；稳定化使 2.8T 规模下 routed 支路不爆。

### 5. 原生多模态 + 从头训练 MoonViT-V2（§2.4）
- **机制**：单一共享 backbone 从训练伊始即联合优化 text+image+video（next-token prediction 统一目标），无事后 modality alignment 阶段。MoonViT-V2 = 27 层 ViT / ~0.4B 参数 / RMSNorm / 去所有 bias，**从头用 next-token prediction 训练**（非 SigLIP 对比预训练初始化）。理由：SigLIP-init 的 MoonViT-3D 联合优化时梯度范数持续偏高且频 spike（Fig.6），从头训的 V2 全程稳定；且 next-token 让表示直接由 LM 目标塑形而非对比损失的全局语义。视觉通路：图片/视频共享参数、intra-frame 空间 + inter-frame 时间 factorized attention + temporal pooling；pixel-shuffle 2×2 下采样使视觉 token 减 4×，支持 3584×3584 像素输入在 1M 上下文内可承担。
- **效果**：MoonViT-V2 在视觉评测上匹配 SigLIP-init 基线 → 证明对比预训练对大规模多模态 LM 并非必要初始化；vision-in-the-loop agentic 行为（写代码→截图/视频→迭代精修）有架构根基。

### 6. Per-Head Muon 优化器（§2.5）
- **机制**：继承 [[kimi-k2-open-agentic-intelligence]] 用 Muon（[[muon-is-scalable-for-llm-training]]）做矩阵参数优化器；对 Q/K/V 投影进一步做 per-head 变体——沿 head 维切分 momentum 矩阵、每头块独立 Newton–Schulz 正交化。直觉：全矩阵正交化把所有头当耦合块，大梯度/动量头主导共享更新方向、小头欠正交化；per-head 等价化各头更新尺度。
- **效果**：跨头学习动力学更均衡、大规模稳定性提升；per-head 块更瘦，Newton–Schulz 迭代比全矩阵更省。

### 7. Multi-effort RL + 多教师 on-policy 蒸馏（§4.1）
- **机制**：三段式 post-training——SFT 冷启 → 分域×分力度 RL 专家 → MOPD 合并。RL 跨三大域（general / general agents / coding agents），每域 × 三 effort {low, high, max} = **9 个专家**。关键算法：
  - **Partial rollout**（§4.1.2）：每迭代 N prompt × K 完成，维持 N×K 活跃轨迹；一旦 λ∈(0,1) 比例完成即触发策略优化，不等 straggler；暂停的 rollout 入队下迭代恢复（靠沙箱基础设施）。单条长程轨迹天然跨多迭代 → 引入 data staleness，靠 per-token 正则把策略更新限局部邻域容忍极 off-policy。
  - **Reasoning Effort RL**：每问题估初始 token 预算 `b_0(x)`（冷启模型估），超 `τ·b_0(x)` 的轨迹 reward 改为 −1；按 `τ` 阶段课程——先训 max-budget（大 τ 但封顶），再退火到 high/low。
  - **Agentic GRM**：非可验证任务用 tournament 二元比较的 generative reward；judge 强制四步协议（读产出→生成 rubric→按 rubric 打分→记 scorepad）；并用 `σ·ℓ_0` verbosity 控制反 reward hacking 到冗长。
  - **MOPD**（§4.1.3，Eq.15）：对域 d、effort e，由对应 9 专家 `π_teacher^(d,e)` 给 per-token OPD reward `r_opd = clip(sg(log π_teacher/π_θ), −R_max, R_max)`，dense reward 无缝集成进 partial rollout RL 框架。top-k distillation 未见明显优势。
- **效果**：长程 agentic（数百~数千工具调用、百万累积 token）训练稳定可扩；多力度统一进单模型；图 8 显示 RL FLOPs ↑ → tool-call steps ↑ → 各能力综合 ↑。

### 8. 部署感知 post-training：MXFP4 QAT + EAGLE-3 draft（§4.1.4）
- **机制**：MoE 专家权重 MXFP4、激活 MXFP8，非专家组件（attention 投影、latent MoE 投影、shared 专家、router）保高精度；**QAT 贯穿 SFT+RL**，rollout 与训练同量化方案消除 train-inference mismatch。MTP 层 fine-tune 成 EAGLE-3 风格 draft model（target frozen，仅更新 draft 层 + feature-fusion 投影）；draft 输入融合 AttnRes 第 1/4/末块的低/中/高层特征，`W_E3` 初始化 `[0 0 I]` 使初始等价高层特征；**直接优化 LK loss** `L_LK = −log Σ_x min(p(x),q(x))`（Eq.16，acceptance rate 负对数，温度=1，无辅助 CE 项），因 KL surrogate 不保证最大化 capacity-limited draft 的接受率。
- **效果**：部署内存/成本降 + 无损 speculative decoding；draft 在 QAT 配置下训练。

### 9. 任务合成与白盒 RL 环境（§4.2）
- **机制**：(i) **Unified White-Box RL Env** 把 agent harness 拆成可配置可组合模块（tool 接口、system prompt、context 管理、skills、memory、subagents），靠配置实例化 Kimi Code / Claude Code / Codex / OpenClaw / Hermes 等主流 harness，防过拟合单一 harness。(ii) **Knowledge-Graph-Guided Task Synthesis**（§4.2.2，Fig.9）：自演化分层 DAG 知识图，agent 递归扩展节点（web 搜索→查重→加边），按层级采样节点→派生关键词→检索真实材料→合成任务。(iii) **Verifiable agentic problems**：多步信息检索、专业工作流（投行/数据/法律）、多步可验证视觉推理（sandbox 内 Python 解释器，模型迭代写代码 crop/zoom/transform 验证）。(iv) **Kernel optimization tasks**（§4.2.4）：CUDA/Triton/CuTe DSL/Gluon/ThunderKittens/TileLang，BF16/FP8/FP4；reward = 正确性（超阈值零分）+ 性能（match expert 0.5，近 roofline 趋 1）；hacking 检测（CUDA graph replay、输入缓存、精度降低）。(v) **Personal assistant tasks**（§4.2.5）：Gmail/Notion/Slack/Canvas 的 mock 实现，跨多模拟日、数十互依事件、单 rollout 至数千工具调用百万 token。(vi) **AET (Autonomous Execution Tasks)**（§4.2.6）：给目标/约束/验证接口，无参考轨迹，agent 自主分解/选工具/规划/纠错/终止；reward 基于独立 verifier 对终态评估；black-box 系统复制（Fig.10 Camera Repair）、量化因子发现、税务审计；公私 verifier 配对防 hacking。(vii) **Web development tasks**（§4.2.7）：容器化沙箱、多 scaffold rollout、deterministic + model judge 双 reward。

### 10. KDA 算法-系统协同设计（§5.1）
- **机制**：(a) **FlashKDA**（§5.1.1）：CUTLASS-based chunkwise kernel，把 token-parallel stage 与 head-parallel recurrence 解耦独立调度，重叠 intra-chunk 计算与 cross-chunk state 传播，优于 Triton reference；服务于训练 + 推理 prefill。(b) **Intra-device Context Parallelism**：pure TP 下长 prefill 单 rank 仅持少头 → SM 闲置；观察到 segment 状态转移可独立算后精确复合，自动 SM-level CP planner 把序列切到单 rank 各 SM 上并行算 segment 转移再合并，无跨设备通信。(c) **KDA Context Parallelism (KCP)**（§5.1.2，Eq.17）：KDA 的 delta-rule 使 local segment 效果依赖入段 state（不能像普通线性注意力 S=0 直接求和）；KCP 把每段效果分解为 `Mt←1[i+1]`（作用于入段 state 的累积转移）+ `eSt[i+1]`（从零起 local 生成 state），二者皆可仅用 local token 算 → 各 rank 一次 all-gather 交换固定大小片段 → prefix scan 复合（结合律）恢复入段 state。**线性算力扩展 + 固定大小通信**，区别于 softmax attention 的 KV 块交换（size 随序列长增长）。

### 11. 3T-class 预训练基础设施（§5.2）
- **MoonEP**（§5.2.1，附录 E 证明）：perfectly balanced expert-parallel scheme，每 rank 恰收 `S×K` token。证明 **每 rank 至多 E/R 个 redundant expert 即可保证均衡方案存在且该界 essentially tight**（`⌈E(R−1)/R²⌉ ≈ E/R`）。在线 planning kernel 近最优且零开销（ILP 离线求参考解），forward prefetch、backward 本地 reduce buffer；**zero-copy 通信**（planner 预算每 token 目的地，直接送至远程 expert-grouped 位置，无中间拷贝；最坏失衡下 DeepEP 需 `S×K×R` buffer，MoonEP 仅固定 `S×K`）；**static shapes 去 per-layer host-device sync**（每 rank 恒收 S×K → 计算形状静态已知 → 去 host-side kernel launch stall）；**workload-aware expert-GEMM scheduling**（per-expert token count 仍偏斜 → 自适应调度参数 + offline autotune 校准硬件系数；shared experts 派到独立 stream 重叠）。
- **Memory-efficient training**（§5.2.2）：统一 activation manager（recompute/quant/offload/remote-offload 皆 tensor 粒度可组合存储策略，函数粒度 recompute 支跨层；block-wise FP8 + offload）；memory-efficient MoE（参考 SonicMoE 把 permuted probs 的梯度改写为仅依赖 `act_output + d_output`，省前向输出依赖 + group GEMM 前向只存 dispatch 输入、反向重算 dispatch 并与 group-GEMM 反向重叠）；Block AttnRes 优化（块表示生成一次驻 GPU、整 AttnRes 包 checkpointing、cache-based pipeline 仅传新块达到理论下界）；跨 PP rank 激活均衡（1F1B warmup 致 PP 高 rank 激活少 → Mooncake Transfer Engine 远程 offload 到其它 PP rank）；Pipeline ZeRO-2 梯度分片+CPU offload（shard 存 CPU，double grad buffer 留 GPU，DP reduce 后累积进 CPU shard）；**P2P Muon 正交化**（不去 all-gather 全参数 buffer，每 rank 仅 P2P 拉本 rank 拥有的 shard，消除全参数 buffer + 减少 memory/通信，模型 chunk 粒度流水隐藏通信）。
- **Multimodal encoder 优化**（§5.2.3）：动态 CP 切大图/长视频 patch 到多设备 gather-KV + sub-CP group 负载均衡；ViT 计算塞进 PP bubbles（首微批次同步前置、余下进 bubble、backward 类似）——继承 K2.5 DEP 思路进一步分解 ViT，几乎消除视觉编码器有效开销。

### 12. 1M Agentic RL 基础设施 + AgentENV microVM 沙箱（§5.3）
- **机制**：(a) **Co-located RL**（§5.3.1）：每 1M-上下文 RL 实验压在几百 GPU 内 + partial rollout 降尾延迟。**External KV cache pool**：1M 多步 rollout 的 prefix KV miss 极贵，partial rollout 每迭代初大量未完长 prefill 同时到、speculative decoding 加速周转致 prefix-block churn → 触发抢占降命中率。解法：write-back 设计——active decode 块留 GPU KV，可复用 idle prefix 仅在被驱逐时写回 CPU DRAM 外部池，下次复用前 prefetch 回；KDA state 与对应 MLA KV 块同生命周期 offload/prefetch；训练迭代后把训练状态（权重+优化器）offload 到 NVMe 腾 DRAM 给池。**Rollout auto-throttling**：基于 active/queued 请求数 + KV cache 利用率动态控并发，早期高利用、后期降并发防抢占。**Gradient-buffer reuse**：非策略模型（如 reference model）权重存 CPU、用时 materialize 到策略模型的 FP32 gradient buffer（real gradient 算时才覆写，安全复用），ZeRO-2 下每 GPU 仅留两 VPP chunk 的 grad buffer，stream 参考权重 chunk by chunk + 另一槽 prefetch。
- **AgentENV**（§5.3.2）：与合作伙伴开发的 microVM 沙箱，Firecracker 隔离（容器级曾出 kernel panic/deadlock）。三目标：(i) 高保真隔离（agent 可挂盘/跑容器/起 VM）；(ii) 灵活生命周期——增量 checkpoint/resume（仅存脏页，**checkpoint 133ms / resume 49ms**），Pause-Resume（等待模型推理时暂停沙箱零耗 CPU/mem，占沙箱寿命 98%）、Fork（同状态 fork 出新沙箱做无副作用 reward judging）、Snapshot 定期快照错误恢复；(iii) 高密度高效——OverlayBD 图像 + 自研 ublk 驱动 + 存储层共享 + P2P 传输，亚秒级大规模启动；copy-on-write 内存 + page-cache 优化，**memory overcommit 比 6.5×**。整个训练+评测期共创建 **51,219,741 沙箱跨 1,505,678 镜像**。

### 13. 推理与服务：KDA-aware 混合前缀缓存 + 专用 kernel + fleet 调度（§5.4）
- **KDA-aware prefix cache**（§5.4.1）：KDA recurrent state（固定大小、每序列一份）与 MLA KV cache（随序列长分页）size/lifetime 不同但必须同边界恢复才有用 → 统一到同 paged pool（同 byte size 共享分配/引用计数/eviction；页内各 head 连续存储为最小跨节点传输单元；prefill/decode 解耦不同 TP 度时传输路径 re-layout 零 GPU 重排）。**解耦粒度**：MLA prefix hashing 走 512-token hash block，物理块仍 6144-token；KDA checkpoint 仅存于（稀疏子集的）hash 边界——只有 lookup 能引用的位置。两阶段 lookup（Fig.12）：MLA 阶段物理块链式 hash 匹配 + 缺块时回退到块内 hash 端点；KDA 阶段要求候选边界在每个 KDA cache group 有 checkpoint（每 group 独立 recurrent state）。hit = 同时满足两阶段的最长边界（必为 512 倍数、不必为 6144 倍数）。一致性：共享 free list + 跨 group pin hit 块防互驱；私有拷贝在 forward 前立即上 GPU、当步新分配/注册块排除出匹配；checkpoint 任 group 驱逐则原子失效兄弟 group。
- **专用 kernel**（§5.4.2）：KDA 解码——MTP speculative decoding 下拒答子集 token 时 state 已前推无法简单回滚；缓存每 draft 位置的 state snapshot 会乘大 batch state traffic；解法：**只缓存 draft token 的 projected input**（远小于 state），on-chip 重建接受 token 的 state，写回 verified + bonus token 的 state（concurrent ReplaySSM 同思路）；短卷积/归一化/门控/递推/输出归一化全融进单 kernel，验证延迟亚线性增长。Block AttnRes——prefill 用 sequence parallelism 把 TP all-reduce 拆 reduce-scatter + all-gather，intra-block kernel 插中间只在单 rank 物化块表示；decode 在 side stream 跑 inter-block kernel 与主 stream 重叠，intra-block 与 RMSNorm 融进前序 TP all-reduce。Stable LatentMoE——latent down-proj 与 router 融单 GEMM、latent 权重矩阵分片且输出 all-gather 融进 GEMM epilogue（multimem store）、通信与 shared-expert 计算重叠；routed 专家小 batch 下用 token-centric **WarpDecode**（每 warp 负责一输出 neuron 直接 stream 权重），warp 内再细分 lane team 各处理不相交专家子集 + warp-wide reduction，权重离线 permute 降运行时 dequant 开销。
- **Fleet 调度**（§5.4.3）：**Cache-aware affinity scheduling**——典型 coding 输入 400K 前缀 + 4K prefill，hit 避免重 prefill 数量级成本差，故每 session 路由到持其前缀缓存的集群；consistent hashing pin 每 session 到主+预指派备两集群，主失败备接管重 prefill（分担到多集群非集中）；**Budget-based admission control**——请求成本跨 3 数量级（2K→1M），按请求类分资源预算，bursty 长上下文不至拖垮短请求 SLO/TTFT。

### 14. XTML chat template（§F，Fig.16）
- **机制**：XML-like 但用三个保留 special token `[open]/[sep]/[close]` + `[end_of_msg]` 替代尖括号——每结构边界是显式 special token，消除边界 tokenize 歧义、简化 constrained decoding。消息分 input messages（system/user/assistant/tool）与 option messages（global：tool-declare + thinking-effort 放所有 input 之前；one-shot：tool_choice/response_format 放之后以保 KV cache 不被 per-request 改动失效；input option：会话中动态加载 tool 用，不重建前文）。assistant body 分 think/response/tools 三 channel（灵感 OpenAI Harmony）。tool call 带 tool+index 属性，结果按 call 顺序回传、参数有类型（string 原始文本、其它 JSON 紧凑序列化；纯 JSON fallback 块仅输入侧、训练时 loss mask）。reasoning effort 以自然语言 global option message 注入（非改 prefix 或暴露 token 预算），pre-trained 模型已能跟从 → 新选项可零/微训练引入（"low alignment tax"）。

## 表格（原文结构化）

### Table 1：Kimi K2 vs Kimi K3 架构对比
| 项 | Kimi K2 | Kimi K3 | Δ |
|---|---|---|---|
| Architecture | MoE | MoE | – |
| #Layers | 61 | 93 | ↑52% |
| Total Parameters | 1.04T | 2.78T | ↑167% |
| Activated Parameters | 32.6B | 104.2B | ↑220% |
| Hidden Dimension | 7,168 | 7,168 | = |
| Latent MoE Dimension | – | 3,584 (0.5×) | – |
| MoE Hidden Dim / Expert | 2,048 | 3,072 | ↑50% |
| Routed Experts | 384 | 896 | ↑133% |
| Experts Active / Token | 8 | 16 | ↑100% |
| Shared Experts | 1 | 2 | ↑100% |
| Attention Heads | 64 | 96 | ↑50% |
| Number of Dense Layers | 1 | 1 | = |
| Vocabulary Size | 160K | 160K | = |
| Training Context Length | 128K | 1M | 8× |
| Attention Mechanism | MLA | Hybrid KDA–MLA | – |
| Activation Function | SwiGLU | SiTU-GLU | – |
| Attention-Layer Composition | 61 MLA | 69 KDA + 24 MLA | – |
| #MTP Layers | 1 | 1 | = |
| Total Params of ViT | – | 401M | – |
| #ViT Layers | – | 27 | – |
| Patch Size of ViT | – | 14 | – |
| #Attention Heads of ViT | – | 12 | – |

### Table 2（节选核心，公开基准，max effort；HLE/MMMU-Pro/CharXiv/Math-Vision/ZeroBench 为 w/o tool / w/ tool）
| Benchmark | Kimi K3 | Fable 5 | GPT-5.6 Sol | Opus 4.8 | GPT-5.5 | GLM-5.2 |
|---|---|---|---|---|---|---|
| GPQA Diamond | 93.5 | 92.6 | 94.1 | 91.0 | 93.5 | 91.2 |
| CritPt | 23.4 | 28.6 | 32.3 | 20.9 | 27.1 | 20.9 |
| AA-LCR | 74.7 | 70.0 | 73.7 | 67.7 | 74.3 | 71.3 |
| HLE-Full | 43.5/56.0 | 53.3/63.0 | 44.5/58.0 | 49.8/57.9 | 41.4/52.2 | – |
| DeepSWE | 67.5 | 70.0 | 73.0 | 59.0 | 67.0 | 46.2 |
| ProgramBench | 77.8 | 76.8 | 77.6 | 71.9 | 70.8 | 63.7 |
| Terminal-Bench 2.1 | 88.3 | 88.0 | 88.8 | 84.6 | 83.4 | 82.7 |
| FrontierSWE | 81.2 | 86.6 | 71.3 | 66.7 | 64.9 | 67.3 |
| SWE-Marathon | 42.0 | 35.0 | 39.0 | 40.0 | 14.0 | 13.0 |
| BrowseComp | 91.2 | 88.0 | 90.4 | 84.3 | 84.4 | – |
| GDPval-AA v2 (Elo) | 1686 | 1747 | 1736 | 1593 | 1491 | 1510 |
| MCPMark-Verified | 94.5 | 87.4 | 92.9 | 76.4 | 92.9 | – |
| AutomationBench | 30.8 | 29.1 | 29.7 | 27.2 | 22.7 | 12.9 |
| JobBench | 54.3 | 57.4 | 45.4 | 48.4 | 38.3 | 43.4 |
| AA-Briefcase (Elo) | 1548 | 1583 | 1495 | 1354 | 1158 | 1260 |
| Agents' Last Exam | 28.3 | 25.7† | 29.6 | 27.0 | 26.6 | 20.4 |
| OSWorld-Verified | 84.8 | 85.0 | 83.0 | 83.4 | 79.0 | – |
| OSWorld 2.0 | 58.3 | 66.1 | 62.6 | 55.7 | 49.5 | – |
| τ 3-Banking | 33.4 | 26.8 | 33.0 | 27.6 | 31.3 | 26.8 |
| Harvey Lab-AA | 94.6 | 93.6 | 87.2 | 91.1 | 86.3 | 91.0 |
| WorldVQA ForceAnswer | 51.0 | 56.7 | 41.8 | 39.1 | 38.5 | – |
| OmniDocBench | 91.1 | 89.8 | 85.8 | 87.9 | 89.4 | – |
| Math-Vision | 94.3/97.8 | 94.8/98.6 | 95.8/97.8 | 86.7/97.1 | 92.2/96.8 | – |
| ZeroBench-main (pass@5) | 23.0/41.0 | 23.0/46.0 | 17.0/35.0 | 17.0/34.0 | 22.0/41.0 | – |

### Table 4：Kimi Webdev Bench vs Claude Opus 4.8（盲评专家）
| Domain | Win | Tie | Lose | Win−Lose |
|---|---|---|---|---|
| Games | 55.6% | 3.7% | 40.7% | +14.9% |
| 3D / WebGL / Shader | 72.7% | 13.7% | 13.6% | +59.1% |
| Website / UI Clone | 52.6% | 21.1% | 26.3% | +26.3% |
| Overall | 58.6% | 13.8% | 27.6% | +31.0% |

### Table 5：第三方评测（as of July 23, 2026）
| Benchmark | Kimi K3 | Fable 5 | GPT-5.6 Sol | Opus 4.8 | GPT-5.5 | GLM-5.2 |
|---|---|---|---|---|---|---|
| Artificial Analysis Intelligence Index v4.1 | 57.1 (#4/580) | 59.9 | 58.9 | 55.7 | 55.0 | 51.1 |
| Vals AI Vals Index | 74.7 (#2/39) | 75.1 | 73.1 | 70.4 | 68.0 | 65.0 |
| WebDev Arena (Elo) | 1,678 (#1/99) | 1,634 | 1,630 | 1,565 | 1,507 | 1,592 |
| Text Arena (Elo) | 1,486 (#8/200) | 1,507 | 1,485 | 1,484 | 1,482 | 1,469 |
| Agent Arena | 9.1 (#4/37) | 12.7 | 10.1 | 9.8 | 8.8 | 6.5 |

### 关键效率数字（§6.4，Fig.13）
- Kimi Code Bench 2.0：落后 Fable 5 4.0 分，成本仅其 38%；高 effort 即匹配 Opus 4.8 max 分、约其 1/3 成本。
- BrowseComp：91.2%（最高）@ $2.03/task —— GPT-5.6 Sol（90.4%）一半成本，比 Claude max effort 模型便宜约一个数量级。
- GDPval-AA v2：差 GPT-5.6 Sol 不到 50 Elo、成本低 13%；比 Fable 5 便宜 2.6×。
- AA-Briefcase：第二，约 Fable 5 一半成本。

### 案例研究（§7）核心数字
- GPU kernel 优化：AttnRes 283.6ms→114.4ms，DSA −55.1%，KDA −73.6%，MLA 超 peak TFLOPS 一半；match Fable 5(with fallback)，超 Opus 4.8/GPT-5.6 Sol/GPT-5.5。
- MiniTriton 编译器：matmul 近 cuBLAS 约 90% machine roof；DSL-level KDA prefill kernel 超 Triton reference；GPT 训练 loss 紧贴 PyTorch reference，全模型梯度 vs torch autograd 差 ≤ fp32 rounding 10⁻⁴（fp64 参考）。
- 芯片设计：48h 自主跑，nano 模型推理芯片原型（同 hybrid KDA+NoPE-MLA、Block AttnRes block size 2、sigmoid MoE routing、1 shared expert、group-wise INT4 w128），4mm² 内 100MHz 闭时序、RTL 仿真 decode >8,700 tokens/s、1.46M cells、0.277 MiB SRAM、INT4 MAC 融合反量化。
- Cyber（§6.2.2）：Tier 1 漏洞挖掘 ~70% 经人确认为真（含 6 项目 16 个未知漏洞）；Linux kernel 远程堆越界写 + RDMA Dirty-COW-class 本地提权。Tier 2 exploit 36 task 解 14（38.9%）vs GLM-5.2 8（22.2%），10/14 来自 user-space track。UK AISI+CAISI 评估：K3 超 GLM-5.2（ExploitBench 32% vs 24%、32 步企业网 17 vs 11 步），但 0/41 任务完成 arbitrary code execution。

## 与同类对比

- **vs [[kimi-k2-open-agentic-intelligence]]（直接前代）**：K2 是 1.04T/32.6B 激活/128K 上下文/全 MLA/SwiGLU/384 路由专家 8 激活/1 shared。K3 在所有维度加码（2.78T/104.2B/1M/Hybrid KDA-MLA/SiTU-GLU/896 路由 16 激活/2 shared），加 AttnRes 跨层、Stable LatentMoE 稳定化、QB 路由均衡、MoonEP 完美均衡、MoonViT-V2 从头训、microVM 沙箱、KDA-aware 前缀缓存。scaling efficiency ~2.5×。
- **vs [[kimi-k2-5-visual-agentic-intelligence]]（K2.5）**：K2.5 引入视觉 agentic + Agent Swarm；K3 继承 K2.5 视觉通路设计但**视觉编码器从头训**（K2.5 用 SigLIP-init 的 MoonViT-3D），骨干换 hybrid attention，扩展到 3T。test-time scaling 由 K2.5 的并行 agent swarm 推进到 K3 的多力度 RL + MOPD 统一。
- **vs [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] / [[deepseek-v3-technical-report]]（DeepSeek frontier 线）**：DeepSeek 系是 MLA 的起源（V2 引入，V3/V4 采用并扩到 MoE）。K3 保留 MLA 作为周期性全局注意力层，但主体换成 KDA 线性注意力 + AttnRes 跨层混合——是 DeepSeek 路径之外的一种"长上下文靠线性注意力 + 少量全局层"的替代架构选择。K3 的 LatentMoE（compact latent 空间路由）+ auxiliary-loss-free QB 也与 DeepSeek 的 MoE 路由思路形成对照（DeepSeek 用辅助损失/auxiliary-loss-free 变体）。K3 强调"开源 3T-class 首例"，DeepSeek-V4 强调"高效 million-token 上下文智能"，二者在长上下文 + MoE 上方向同向但架构解不同。
- **vs [[kimi-linear-an-expressive-efficient-attention-architecture]]（Kimi Linear）**：Kimi Linear 是 KDA 的提出者，3:1 KDA:MLA 混合的来源（3B 激活/48B 总参/1.4T tokens 公平对比验证超越全注意力）。K3 把 Kimi Linear 的架构思路**首次推到 2.8T 生产规模**，并改 decay 参数化（下界有界）、output gate（full-rank）、加 AttnRes + Stable LatentMoE 配套，落地 1M 上下文 + agentic RL。
- **vs [[muon-is-scalable-for-llm-training]]（Muon）**：K3 直接用 Muon，并细化为 per-head 变体（Q/K/V 投影沿 head 维切分独立正交化）；分布式上用 P2P 取代 all-gather 全参数 buffer——是对 Muon scalability 工作的工程延续。
- **vs [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]（GEPA，prompt evolution vs RL）**：K3 走的是大尺度 RL + MOPD 路线（9 专家 × 3 effort），主张"scaling RL FLOPs → 工具调用步数 ↑ → 能力综合 ↑"（Fig.8）；与 GEPA"prompt evolution 可超 RL"的论点形成方法学张力，但 K3 也在 task synthesis / GRM 用了 prompt/LLM-judge 协议（rubric 四步、knowledge-graph-guided synthesis）——RL 与 prompt evolution 在工程中常互补。
- **vs [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]（EAGLE-3）**：K3 把预训练 MTP 层直接 fine-tune 成 EAGLE-3 draft 模型，并直接优化 LK loss（非 KL surrogate），是 EAGLE-3 范式在 2.8T MoE + hybrid attention 上的落地；同时用 AttnRes 第 1/4/末块特征作 draft 融合输入。
- **vs 闭源 frontier（Claude Fable 5 / GPT-5.6 Sol / Opus 4.8 / GPT-5.5）**：整体仅次于 Fable 5 与 GPT-5.6 Sol，在 SWE-Marathon（42.0，超 Fable 5 7 分）、ProgramBench（77.8 第一）、BrowseComp（91.2 第一）、Swarm Bench/Deep Research Bench（in-house 第一）、WebDev Arena（1,678 第一开源登顶）等多个套件领先；但 HLE/CritPt（研究级推理）、Elo 类知识工作（GDPval-AA v2/AA-Briefcase）、OSWorld 2.0/SaaS-Bench、Agent Behavior Bench 仍落后 Fable 5。

## 跨论文关系（→ MOC 谱系）

- **Moonshot Kimi 系列主线**：Kimi K1.5（RL scaling）→ [[kimi-k2-open-agentic-intelligence]]（agentic foundation, 1T MoE）→ [[kimi-k2-5-visual-agentic-intelligence]]（视觉 agentic + agent swarm）→ **[[kimi-k3-open-frontier-intelligence]]（3T open frontier，本文）**。K3 同时是 K2 的规模/架构继任者与 K2.5 的视觉/agentic 延续。
- **架构组件谱系**：
  - 线性/混合注意力：[[gated-delta-networks-improving-mamba2-with-delta-rule]] → [[kimi-linear-an-expressive-efficient-attention-architecture]]（KDA 提出）→ K3（KDA 落地 3T + 下界有界 decay + full-rank gate）。
  - 跨层信息流：标准残差 → Attention Residuals（K3 引入），与 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] 的深度堆叠思想同向（深度维度信息访问）。
  - MoE 路由均衡：DeepSeek-V3 auxiliary-loss-free → K3 Quantile Balancing（精确对偶极小闭式跳）+ MoonEP（完美均衡 + E/R redundant 上界证明）。
  - 优化器：[[muon-is-scalable-for-llm-training]] → K3 Per-Head Muon + P2P 分布式正交化。
  - 多模态：[[kimi-vl-technical-report]]（Moonshot VLM）→ K2.5（MoonViT-3D，SigLIP-init）→ K3（MoonViT-V2，从头 next-token 训练）。
  - Speculative decoding：[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] → K3（MTP→EAGLE-3 draft + LK loss 直接优化）。
- **DeepSeek frontier 对照谱系**：[[deepseek-v3-technical-report]] → [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] 与 K3 同属"长上下文 + MoE frontier 模型"，但 K3 走 hybrid 线性注意力 + AttnRes 路线、DeepSeek 走 MLA-only 路线，是两种 frontier 架构解。
- **test-time scaling 谱系**：Kimi K1.5 / DeepSeek-R1（RL reasoning）→ K2.5 Agent Swarm（并行 agent）→ K3（多力度 RL + MOPD 统一 + million-token agentic trajectory）。与 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] 形成"RL vs prompt evolution"方法学对照。
- **基础设施谱系**：FlashKDA（CUTLASS chunkwise kernel）+ KDA Context Parallelism（prefix scan 复合）→ 与 [[flash-linear-attention]]/fla-org 生态共建（PR #691）；MoonEP 与 DeepEP/UltraEP/ECHO 在 expert-parallel 负载均衡上对照（K3 证明 E/R 上界且 tight）；AgentENV（Firecracker microVM）与 [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] 的异步 RL 系统在长程 agentic RL 基础设施上互补。

## 局限与边界

- **整体仍落后最强闭源**：作者明确 K3 整体仍 trail Claude Fable 5 与 GPT-5.6 Sol。研究级推理短板明显——HLE-Full（43.5/56.0）显著落后 Fable 5（53.3/63.0）与 GPT-5.6 Sol（44.5/58.0），CritPt（23.4）落后三者。Elo 类知识工作（GDPval-AA v2、AA-Briefcase）、computer-use（OSWorld 2.0、SaaS-Bench）、Agent Behavior Bench、MIRA Bench、24/7 ClawBench 2.0、Agentic Vision Bench、KWV Bench 均非领先。
- **Fable 5 评测带 fallback、GPT-5.6 Sol 带 cyberguards**（Fig.1 注、Table 2 注）——对照并非"裸"模型，K3 是无 fallback 对照，比较不完全对等（K3 在某些套件领先部分源于此）。
- **cyber 能力是 lower bound**：作者自述评估为能力下限，conditioned on 当前模型版本与评测覆盖；end-to-end exploit completion 是瓶颈，hardened target 多数 expert-solvable 任务未解；UK AISI+CAISI 独立评估显示 K3 在 41 任务上 0 个 arbitrary code execution——距离 frontier cyber-capable 模型仍有差距。
- **架构经验值**：3:1 KDA:MLA 比例、N=8/12-layer AttnRes 块划分、`g_min=−5`、`β1=4/β2=25`、latent dim 0.5× hidden 均为经验/ablation 选定，未给大规模敏感性系统分析；最优随规模/任务可能漂移。
- **KDA 线性注意力的 finite-state 容量理论上限未根除**：靠周期性全局 MLA 层 + AttnRes 缓解，但纯线性层在极长 in-context retrieval 上理论受限（继承 Kimi Linear 的边界）。
- **从头训 MoonViT-V2 匹配 SigLIP-init**：作者称"对比预训练对大规模多模态 LM 并非必要初始化"——但仅在 K3 规模/配方下验证，小规模或不同 LM 目标下是否成立未论。
- **基础设施强耦合定制**：FlashKDA、MoonEP、AgentENV、KDA-aware 前缀缓存等均为高度定制 kernel/系统，复现门槛高（虽部分开源 MoonEP/AgentENV/MiniTriton/nano-kpu/FlashKDA）；2.8T 训练的 ROI 与可复现性对一般团队不现实。
- **scaling efficiency 2.5× 的可比性**：曲线拟合在 OOD 验证集上比较 K2 vs K3（Fig.7），但 K3 的数据配方、训练课程也同步精炼，2.5× 是"架构+数据+训练recipe 合力"，非纯架构贡献可分离归因。
- **9 专家 × 3 effort 的 MOPD 合并**：top-k distillation 未见明显优势被采纳为 dense per-token OPD reward；但 9 专家训练成本高、effort 课程 `τ` 退火靠 human-in-the-loop 指导，自动化程度有限。
- **长上下文"真正"能力依赖合成数据**：1M 上下文自然长文档/视频稀缺，靠排列拼接多模态文档与子任务合成训练 attention 机制——合成任务的分布与真实长程任务分布的 gap 未量化。
