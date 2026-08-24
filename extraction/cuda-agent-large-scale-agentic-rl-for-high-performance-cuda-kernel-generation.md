---
paper_num: "68"
title: "CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation"
authors: "CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation Weinan Dai1,2,3∗, Hanlin Wu1,2,3∗, Qiying Yu1,2,3, Huan-ang Gao1,2,3, Jiahao Li1, Chengquan Jiang1, Weiqiang Lou1, Yufan Song1, Hongli Yu1,2,"
date: "2026/2/27"
arxiv: "https://arxiv.org/abs/2602.24286"
pdf: "papers/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.pdf"
slug: "cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation"
tags: []
---

# CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation

> [!abstract] 摘要（原文）
> GPU kernel optimization is fundamental to modern deep learning but remains a highly specialized task requiring deep hardware expertise. Despite strong performance in general programming, large language models (LLMs) remain uncompetitive with compiler-based systems such as this http URL for CUDA kernel generation. Existing CUDA code generation approaches either rely on training-free refinement or fine-tune models within fixed multi-turn execution-feedback loops, but both paradigms fail to fundamentally improve the model's intrinsic CUDA optimization ability, resulting in limited performance gains. We present CUDA Agent, a large-scale agentic reinforcement learning system that develops CUDA kernel expertise through three components: a scalable data synthesis pipeline, a skill-augmented CUDA development environment with automated verification and profiling to provide reliable reward signals, and reinforcement learning algorithmic techniques enabling stable training. CUDA Agent achieves state-of-the-art results on KernelBench, delivering 100\%, 100\%, and 92\% faster rate over this http URL on KernelBench Level-1, Level-2, and Level-3 splits, outperforming the strongest proprietary models such as Claude Opus 4.5 and Gemini 3 Pro by about 40\% on the hardest Level-3 setting.

## 元信息
- **发表日期**: 2026/2/27
- **作者**: CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation Weinan Dai1,2,3∗, Hanlin Wu1,2,3∗, Qiying Yu1,2,3, Huan-ang Gao1,2,3, Jiahao Li1, Chengquan Jiang1, Weiqiang Lou1, Yufan Song1, Hongli Yu1,2,
- **arXiv**: https://arxiv.org/abs/2602.24286
- **本地 PDF**: `papers/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig01.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p03.png]]*
> [!quote] caption
> Overview of the three-stage data collection pipeline. We first crawl seed operators from PyTorch

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以三栏流水线形式展示数据采集全流程：

1. **第一栏（蓝色）**：从 torch/transformers 库中爬取种子算子，产出 matmul、relu、conv2d 三类基础算子，构建"计算原语库"。

2. **第二栏（绿色）**：以 LLM 为"组合器"，将 conv2d、relu、matmul 等单一算子自动合成融合任务（fused op：conv2d → relu → matmul）。

3. **第三栏（白色）**：基于四项 rubric 过滤——可执行（Executable ✓）、确定性（Non-random ✓）、合理负载（Reasonable Workload ✓）、非平凡（Non-trivial ✓），并约束数据类型一致（如 fp16）。

**论证结论**：原文借此说明其训练数据并非随机拼凑，而是通过"原始算子→LLM 合成→rubric 筛选"的链式质控，保证题目可编译、可复现且具训练价值。

**在论文中的作用**：作为整体方法链路的"数据底座"，直接服务于后续 Agentic RL 的 CUDA kernel 生成与高效评测，是论文区别于现有工作（如 KernelBench）的关键数据工程创新。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig02.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p04.png]]*
> [!quote] caption
> Overview of the agent loop.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2展示CUDA Agent的闭环工作流：(1) 输入侧含 `SKILL.md` 系统提示（PyTorch+CUDA专家角色）与 `Workdir`（kernels/、model.py、binding.cpp、utils/含verify与profile脚本）；(2) 中间CUDA Agent生成 `kernel.cu`、`kernel_binding.cpp`、`model_new.py`；(3) GPU Pool执行并反馈四类指标——Correctness、Generated Time 1.26ms、Torch Eager Time 2.30ms、Compile Time 1.80ms。该图定义了训练/评估闭环，将生成→编译→正确性验证→性能基准串成单步RL轨迹。Table 2消融实验据此验证"agent loop"为关键组件，移除后性能显著下降，印证其作为方法链基础设施的必要性。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig03.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p05.png]]*
> [!quote] caption
> Overview of training pipeline. Following a single-turn RL warm-up stage, the sampled trajectories are

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示Agentic RL阶段的核心架构：Actor Model（绿）与Critic Model（蓝）均由RL预热后采样的轨迹分别初始化；Critic Model额外经Value Training训练，二者通过PPO算法连接并最终生成CUDA Agent。原文以此论证：(1)采用"单轮RL预热→轨迹采样→初始化actor-critic"的两阶段训练策略，保证agentic RL的稳定冷启动；(2)以PPO为框架的actor-critic结构是大规模CUDA内核生成agentic RL的关键设计。该图是论文整体方法链路的核心枢纽，串联起轨迹生成、奖励调度与最终高性能CUDA智能体训练的全流程。

### Figure 4 (p.10) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig04.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p10.png]]*
> [!quote] caption
> Ablation: RFT. Removing RFT causes training reward to collapse. The concurrent increase in actor entropy

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a) Training Reward与(b) Actor Entropy对比PPO w/ RFT（橙）与w/o RFT（绿）在约30步训练中的表现。定量看：含RFT时奖励稳步升至1.9–2.0，熵平稳于~0.07；去除RFT时奖励在步16达峰~1.75后骤降至0，熵由~0.07飙升至~0.13后训练崩溃。该图论证RFT是防止策略弥散、维持训练稳定的关键模块——无RFT时策略变得弥散且结构不良。它与Figure 5（Value Pretrain消融）共同构成稳定性消融实验，验证CUDA Agent PPO训练框架中两项必要设计，支撑整体RL管线可靠性的论证。

### Figure 5 (p.10) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig05.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p10.png]]*
> [!quote] caption
> Ablation: Value Pretraining. Without Value Pretraining, the critic fails to learn a meaningful value

> [!tip] 技术解读（多模态）
> 【图文联合解读】图5双子图横轴均为训练步数（0–30）。(a) 价值函数解释方差EV：PPO w/ Value Pretrain（橙）全程平稳≈0；w/o（绿）剧烈波动，最低≈-8，约10步即崩溃终止。(b) 响应长度截断比：带预训练者恒为0；不带者约10步内飙升至0.25后训练中断。

技术结论：Value Pretraining使critic学到有意义的价值函数（高EV），为策略提供稳定梯度信号；缺失时价值估计失效，探索失控，交互轨迹过长触发截断，训练发散。

论文作用：在CUDA Agent的PPO-RL训练链路中，与Fig.4（RFT消融）互补，共同论证"价值预训练"与"拒绝采样微调"是大规模RL稳定收敛的必要前提。

### Figure 6 (p.13) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig06.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p13.png]]*
> [!quote] caption
> Examples of operator classes in our training data.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(b)展示训练数据中的"组合型Torch算子类"`Model`：在`forward`中依次执行`Softmax(dim=1)`→`ConvTranspose2d`(3→16通道，k=3，s=2，p=1)→可学习`bias`相加；输入张量形状为`[512, 3, 32, 32]`。它表明训练算子并非单原子操作，而是由softmax+转置卷积+偏置融合而成的复合算子类，由此扩展了可优化算子空间的组合深度与多样性，为agent生成长程、融合式CUDA kernel提供更贴近真实工作负载的训练目标，支撑大规模RL对复杂算子的端到端优化能力验证。

### Figure 7 (p.13) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig07.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p13.png]]*
> [!quote] caption
> Distribution of the maximum AST similarity between each training sample and all evaluation samples.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象**：直方图展示训练样本与全部评估样本间的最大AST相似度分布。横轴范围0–0.45，纵轴占比0%–12%；峰值约12%出现在相似度≈0.30处，整体集中于0.15–0.45区间，极低相似度(<0.10)样本几乎为零；右上角虚线"t"标记约0.42的阈值位置。

2) **关键结论**：训练集与评估集存在中等程度的代码结构重叠，既非高度雷同（避免数据泄露/记忆式刷分），也非完全无关（保证任务可迁移），由此佐证评估结果的有效性与公平性。

3) **链路作用**：作为前置数据审计环节，用于在RL训练前排除与评测题高度相似的训练样本，防止策略过拟合到已知解，确保后续KernelBench等基准上的性能提升来自真正的泛化能力。

### Figure 8 (p.22) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig08.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p22.png]]*
> [!quote] caption
> Reference operator for diagonal matmul (Case D.2).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图8展示的是 PyTorch 风格的参考算子代码（Case D.2）。核心对象为 `Model` 类，其 `forward(self, A, B)` 执行 `torch.diag(A) @ B`：将 1D 向量 A（N=4096）构造为对角矩阵，与 2D 矩阵 B（4096×4096）做矩阵乘，得到 (N, M) 结果。`get_inputs()` 用 `torch.rand` 生成 A、B 作为测试输入，`get_init_inputs()` 为空。

该代码作为**真值参考算子（reference operator）**，用于在 CUDA 内核生成流水线中：(1) 让 agent 生成的 CUDA kernel 与 `torch.diag(A)@B` 逐元素对比以验证正确性；(2) 提供真实计算语义供 RL 奖励/性能基准对照。它在论文方法链路中扮演 ground-truth 角色，确保 agent 在 KernelBench 类基准上学习"对角矩阵×稠密矩阵"这一特定算子的最优 CUDA 实现。

### Figure 9 (p.23) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig09.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p23.png]]*
> [!quote] caption
> Diagonal matmul kernel implementation (Case D.2).

> [!tip] 技术解读（多模态）
> 【图文联合解读】图9为Case D.2对角矩阵乘的CUDA实现。Kernel采用1D grid-stride循环，每个线程由`row=idx/4096`得行号后执行`output[idx]=A[row]*B[idx]`，覆盖4096×4096=16M元素；launcher启动1024 blocks×128 threads。

关键论证：代码未物化稠密对角矩阵，而是将A作为1D向量(N=4096)按行复用索引，直接产出完整N×M输出——证明RL agent能识别对角稀疏结构并做针对性优化，而非套用通用matmul模板。

论文作用：作为定性案例之一，与其他case共同支撑"agent生成的kernel具备问题感知优化"的核心论点，区别于通用PyTorch基线，验证agentic RL在大规模kernel生成中的实际价值。

### Figure 10 (p.23) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig10.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p23.png]]*
> [!quote] caption
> Custom operator for diagonal matmul (Case D.2).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 10，Case D.2）：**

1）图中展示 `ModelNew` 的 Python 封装：继承 `nn.Module`，仅含 `__init__` 与 `forward(A, B)`，`A` 为 1D 向量 `shape (N,)`，`B` 为 2D 张量 `(N, M)`，逻辑即 `C[i,j] = A[i] * B[i,j]`；前向直接转发至 `cuda_extension.diagonal_multiply_forward(A, B)`，返回 `(N, M)` 结果，自身不含任何计算或对角矩阵构造。

2）原文借此论证"结构化算子"无需物化稠密对角阵：CUDA 端以 **1024 blocks × 128 threads** 启动，线程在 `output` 上做 grid-stride 循环，由 `row = idx / 4096` 反推行号，复用 `A[row]` 一次性广播至该行全部 M 列，仅一次访存完成行级标量–向量乘。

3）在论文链路中，它是 CUDA-Agent 生成的"自定义算子 wrapper + 高性能 kernel"协同范式的代表样例，用以证明 agent 能将高层 PyTorch 算子等价改写为稀疏/结构化语义的高效 GPU 实现，是端到端编译–执行评估 (Case D.2) 的关键验证。

### Figure 11 (p.25) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig11.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p25.png]]*
> [!quote] caption
> Reference operator for matrix multiplication, division, summation, and scaling (Case D.3).

> [!tip] 技术解读（多模态）
> 【图文联合解读】图11展示Case D.3的PyTorch参考算子（共31行代码）：输入x形状(batch_size,input_size)=(1024,8192)，可学习权重矩阵(hidden_size,input_size)=(8192,8192)；forward依次执行torch.matmul转置乘法（GEMM）→x/2（Divide）→torch.sum(dim=1,keepdim=True)（Sum）→×scaling_factor=1.5（Scaling），输出(batch_size,1)=(1024,1)。

该图作为正确性基准真值，用以论证CUDA-Agent能将包含**GEMM矩阵乘、elementwise除、reduction求和、标量缩放**四类异构算子复合的PyTorch模型，自动转译为结果正确且高性能的自定义CUDA kernel。它构成附录D案例集中的关键实证，体现agentic RL方法对多类算子融合调度的综合能力，是论文"参考算子→生成CUDA内核→正确性+性能评测"实验链路中标准答案的角色。

### Figure 12 (p.26) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p26.png]]
> [!quote] caption
> Fused sum-then-dot-product kernel implementation (Case D.3).

> [!tip] 技术解读（多模态）
> **Architecture / Components / Data Flow**

The figure shows a two-stage fused CUDA implementation (`fused_sum_dot_launcher`) for an input_size × hidden_size matrix operation (8192 × 8192):

1. **Stage 1 — `sum_weight_kernel`**: 1 thread per input column; loops over the hidden dimension, accumulating column sums of the `weight` matrix into `sum_weight[8192]`. Launched with ⌈8192/128⌉ blocks × 128 threads.
2. **Stage 2 — `dot_product_kernel`**: 1024 blocks × 128 threads, each thread performs a **float4-vectorized** dot product of `x` against `sum_weight` (4 multiply-adds per load), writes to shared memory, then performs a **log₂(128) tree reduction** in `smem`. Thread 0 emits `output[block] = smem[0] · (scaling_factor / 2.0f)`.

**Key Technical Takeaway** — The fusion reduces the O(8192²) matrix–vector work to O(8192·1024) by pre-summing the weight columns on-GPU; combined with `float4` coalesced loads and in-block shared-memory reduction, this minimizes global-memory traffic and eliminates an intermediate host-visible reduction step.

**Caption (verbatim):**
Figure 12: Fused sum-then-dot-product kernel implementation (Case D.3).

### Figure 13 (p.27) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig13.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p27.png]]*
> [!quote] caption
> Custom operator for matrix multiplication, division, summation, and scaling (Case D.3).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图13展示`ModelNew`自定义算子类（22行代码），将原本独立的**矩阵乘法、除法、求和与缩放**四类操作融合，通过单次`cuda_extension.fused_sum_dot`调用替代多条PyTorch逐op链。`__init__`声明weight参数与scaling_factor，`forward`仅返回融合输出，体现**算子融合 + 自定义CUDA扩展**的端到端可集成形态。

论文借此论证：在D.3案例中，Agent能够生成超越torch原生接口的**fused custom operator**，将多类element-wise/reduction操作合一，直接通过PyTorch `nn.Module`对外暴露，验证了agentic RL在生成可编译、可调用的高性能CUDA算子方面的泛化能力，为"算子级优化取代逐op调度"提供落地证据。

### Figure 14 (p.28) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p28.png]]
> [!quote] caption
> Reference operator for Resnet BasicBlock (Case D.4).

> [!tip] 技术解读（多模态）
> **Description:**

The figure presents a PyTorch implementation of a ResNet BasicBlock reference operator. The `Model` class (with `expansion=1`) is initialized with `in_channels`, `out_channels`, and `stride=1`. Its architecture comprises two sequential 3×3 convolutions (`conv1`, `conv2`) each followed by BatchNorm2d (`bn1`, `bn2`), with a ReLU activation after the first BN. A `downsample` Sequential (1×1 conv + BN) adjusts dimensions when stride ≠ 1. **Data flow:** input → conv1→bn1→ReLU → conv2→bn2 → add identity shortcut (downsampled if needed) → ReLU → output. Test code uses `in_channels=3, out_channels=64, stride=1, batch_size=10` on 224×224 tensors.

**Key takeaway:** The skip connection enables gradient flow by adding the (optionally downsampled) input to the convolved output before the final ReLU — the defining feature of residual learning.

**Caption (verbatim):**

Figure 14 Reference operator for Resnet BasicBlock (Case D.4).

### Figure 17 (p.30) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-fig17.png]]
*整页渲染: ![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p30.png]]*
> [!quote] caption
> Fused add-relu kernel implementation (Case D.4).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示为 Case D.4 的 CUDA 融合 add-ReLU 内核源码（共 33 行）。核心结构：`block_size=256`，`grid_size` 上限 4096，采用**网格步进循环（grid-stride loop）**；主体通过 `reinterpret_cast<float4*>` 做 **向量化 4 元素批量访存**，每元素执行 `fmax(v1+v2, 0.0f)`，尾部用标量循环补齐非 4 对齐元素。

论文用它论证的关键结论：经过 RL 训练的 agent 能自主产出**融合访存（向量化 float4）+ 激活融合**的高质量优化内核，体现"显存带宽受限算子 → 单次访存完成 add+ReLU"的优化能力，是验证 agent 在 end-to-end 编译、SIMD 化与尾部处理等工程细节上达到人类专家水平的关键案例。

### Figure 18 (p.31) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p31.png]]
> [!quote] caption
> Custom operator for Resnet BasicBlock (Case D.4).

> [!tip] 技术解读（多模态）
> ## Description

**Architecture / Components**
The figure shows a `ModelNew` (PyTorch `nn.Module`) implementing a fused ResNet BasicBlock for inference:
- Two 3×3 conv layers (`conv1`, `conv2`) plus an optional 1×1 `downsample` conv
- Three matching BatchNorm2d modules (`bn1`, `bn2`, `downsample[1]`)
- A custom CUDA extension providing `conv_forwardd` (conv + optional ReLU) and `fused_add_relu_forward` (add + ReLU)

**Data flow (`forward`)**
1. Enable TF32 for matmul/conv
2. Save `identity = x` (skip branch)
3. Fold `bn1` into `conv1` weights/bias → call custom conv (stride, padding, dilation, ReLU=True)
4. Fold `bn2` into `conv2` → call custom conv (ReLU=False)
5. If downsample ≠ None, fold its BN and apply to `identity`
6. `fused_add_relu_forward(out, identity)`
7. Disable TF32; return `out`

**Key technical takeaway (≤120 words):**
The block performs inference-time **BN-folding**, absorbing each BatchNorm's γ/β/mean/var into the preceding Conv's weight and bias (`γ·W/√(var+ε)`, `β − μ·γ/√(var+ε)`). This lets the entire residual block — conv, BN, skip-add, and ReLU — collapse into just **two custom CUDA calls** (`conv_forwardd`, `fused_add_relu_forward`) per branch. The result is a single fused kernel that eliminates intermediate tensor materialization, cuts kernel-launch overhead, and keeps TF32 precision scoped only to the convolutions themselves. (~90 words)

**Caption (verbatim):**
Figure 18. Custom operator for Resnet BasicBlock (Case D.4).

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.7) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-tab01.png]]
> [!quote] caption
> Main Results on KernelBench. We report Pass Rate, Faster Rate (percentage of kernels faster than baseline), and Geometric Mean Speed-up. Metrics are reported relative to both PyTorch Eager and PyTorch Compile baselines. Overall metrics are weighted by the number of problems in each level (Level 1: 1

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表格对象与结构**：Table 1 对比 6 个模型（基座 Seed1.6、GLM 4.6、Kimi K2、Gemini 3 Pro、Claude Opus 4.5 及本文 CUDA Agent）在 KernelBench 三级共 250 题（100/100/50）上的三项指标：Pass Rate、相对 PyTorch Eager/Compile 的 Faster Rate 与 Geomean 加速比，Overall 按题数加权。

**关键技术结论**：CUDA Agent 在所有层级全面最优。Overall 达 Pass Rate 98.8%、加速比 2.60×/2.11×；Level 2 实现 100% 通过与 3.27×/2.80× 加速，显著领先 Claude Opus 4.5（95.2%、1.99×）与 Gemini 3 Pro（91.2%、1.92×）；Level 3 高难度下仍保持 94% 与 1.80×/1.52×，难度越高领先幅度越大；而 Seed1.6 基座 Overall 仅 74%、加速 0.95×（反慢于 baseline）。

**论文作用**：作为 headline 主表，定量验证"三阶段合成数据 + 大规模 agentic RL"全链路在自动 CUDA kernel 生成上同时超越基座与商用 SOTA，是闭环证明方法有效性的关键实验落点。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-tab02.png]]
> [!quote] caption
> Ablation Study. Comparison between the full model and leave-one-out variants under agent loop evaluation . We analyze the contributions of (1) the agent loop, (2) robust reward design, (3) RFT, and (4) Value Pretraining. For variants without RFT or Value Pretraining, we report results from the final

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表2 联合解读**

该表以Overall子集为基准，对完整模型进行四项消融，报告Pass Rate、相对Eager/Compile的Faster Rate与几何平均加速比。

关键数据：完整模型Pass 98.8%、vs Eager 98.4%更快、加速2.60×；去掉Agent Loop后各项骤降至77.1%/43.5%/0.89×，甚至慢于Eager；去掉RFT后Pass 95.6%但vs Compile仅49.8%、1.05×；去掉Robust Reward与Value Pretraining均明显退化。

结论：四项组件均不可或缺，其中Agent Loop贡献最大（无它即失效），RFT次之。

作用：以定量消实验验证了"Agent Loop + 鲁棒奖励 + RFT + Value Pretraining"四项设计的必要性，支撑论文方法完整性的核心论据。

### Table 3 (p.14) ⭐深度解读
![[assets/crops/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-tab03.png]]
> [!quote] caption
> Composition of the final training dataset

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

**核心数据：** 该表按"算子融合度"（单 CUDA kernel 融合的 torch 算子数量 ×N）划分训练集分布：×2 占绝对主导（83.77%），×3（7.62%）、×1（3.40%）、×4（2.80%）、×5（1.23%）依次递减，transformers 类算子仅 1.18%。

**论证结论：** 数据分布严重偏向"两算子融合"，反映真实 PyTorch 推理中算子合并是最高频的优化场景；高阶融合（×4、×5）与 transformer 专属算子样本稀缺，是后续评估泛化能力的难点。

**链路作用：** 作为 Figure 3 训练流水线的"数据基座"，该分布直接决定了 actor/critic 在单轮 RL 预热与多轮 agentic RL 阶段所见的奖励信号密度——模型主要学习 ×2 融合策略，少量样本支撑复杂场景的探索。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
r = \begin{cases} -1 & \text{if correctness check fails} \\ 3 & \text{if } b(t, t_{\text{eager}}) \land b(t, t_{\text{compile}}) \\ 2 & \text{if } b(t, t_{\text{eager}}) \\ 1 & \text{otherwise} \end{cases}
$$

$$
\mathcal{L}_{\text{RFT}}(\theta) = -\mathbb{E}_{\tau \sim \mathcal{D'}} \left[ \sum_{t=1}^{T} \log \pi_\theta(a_t \mid s_t, a_{<t}) \right],
$$

$$
V_t^{\text{targ}} = V_\phi(s_t) + \hat{A}_t, \quad \text{where} \quad \hat{A}_t = \sum_{l=0}^{T-1-t} (\gamma\lambda)^l \delta_{t+l},
$$

$$
\mathcal{L}_{\text{VP}}(\phi) = \frac{1}{2} \mathbb{E}_{\tau \sim \mathcal{D}} \left[ \frac{1}{T} \sum_{t=0}^{T-1} \left( V_\phi(s_t) - V_t^{\text{targ}} \right)^2 \right],
$$

$$
\begin{aligned} \mathcal{L}^{\text{CLIP}}(\theta) = \mathbb{E}_{\tau \sim \mathcal{D}} &\bigg[ \frac{1}{T} \sum_{t=0}^{T-1} \min \big( \rho_t(\theta)\hat{A}_t, \\ & \text{clip}(\rho_t(\theta), 1-\epsilon_{\text{lower}}, 1+\epsilon_{\text{higher}})\hat{A}_t \big) \bigg] \end{aligned}
$$

$$
\sum_j \frac{x_i \cdot w_j^T}{2} = x_i \cdot \left(\sum_j w_j^T\right) / 2,
$$

## 技术点深读（DEEP）

![[deep/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.txt`（74680 字符）供引用检索。