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
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p03.png]]
> [!quote] caption
> Overview of the three-stage data collection pipeline. We first crawl seed operators from PyTorch

> [!tip] 技术解读（多模态）
> **Figure Description (Architecture / Components / Data Flow + Key Takeaway):**

The figure depicts a linear three-stage data collection pipeline, with arrows flowing left-to-right:

1. **Seed Problem Crawling (blue box):** Operators (matmul, relu, conv2d) are mined from PyTorch / Transformers libraries, building a primitive repository.
2. **Combinatorial Problem Synthesis (green box):** An LLM fuses those primitives (e.g., conv2d → relu → matmul) into multi-operator "fused op" tasks.
3. **Rubric-based Problem Filtering (white box):** A four-quadrant rubric applies checks — Executable ✅, Non-random ✅, Reasonable Workload ✅, Non-trivial ✅ — to retain only high-quality problems.

**Key technical takeaway:** Quality control is decoupled from generation — synthesis by an LLM is *post-hoc* gated by deterministic rubric filters, ensuring fused CUDA tasks remain executable, non-trivial, and benchmark-ready rather than purely synthetic.

---

**Caption (verbatim):**

> **Figure 1** Overview of the three-stage data collection pipeline. We first crawl seed operators from PyTorch and Transformer libraries to build a repository of fundamental computational primitives. Next, an LLM performs combinatorial synthesis to generate fused, multi-operator tasks. Finally, a rubric-based filtering stage retains only executable, deterministic, non-trivial problems with reasonable workloads to ensure data quality and reliable evaluation.

### Figure 2 (p.4) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p04.png]]
> [!quote] caption
> Overview of the agent loop.

> [!tip] 技术解读（多模态）
> **Architecture / Data Flow**
The diagram depicts a closed-loop CUDA optimization agent. On the left, a **SKILL.md** directive (expert prompt) plus a **Workdir** containing the original PyTorch model, utils, and verification scripts feeds into a **CUDA Agent** (center). The agent emits a **Generated** set of artifacts (`kernels/kernel.cu`, `kernel_binding.cpp`, `model_new.py`). These are dispatched to a **GPU Pool** for execution, which returns a **Performance** panel reporting a correctness check, generated kernel time, Torch eager time, and compile time—closing the feedback loop.

**Key technical takeaway**
A lightweight, file-based scaffolding (SKILL.md + workdir) lets an LLM agent iteratively emit fused CUDA kernels and benchmark them against a GPU pool, replacing hand-written reference kernels with agent-generated ones that beat the Torch eager baseline.

**Caption (verbatim)**
Figure 2 Overview of the agent loop.

### Figure 3 (p.5) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p05.png]]
> [!quote] caption
> Overview of training pipeline. Following a single-turn RL warm-up stage, the sampled trajectories are

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure depicts a three-stage training pipeline for building a CUDA agent, partitioned by dashed boxes:

1. **Single-Turn Warm-up** — A Base Model is fine-tuned via PPO into a Single-Turn Model.
2. **Agent Warm-up** — The Single-Turn Model generates sample trajectories by acting as an agent; these trajectories are then used to (a) initialize the **Actor Model** via RFT (rejection fine-tuning) and (b) pretrain the **Critic Model** via value pretraining.
3. **Agentic RL** — The actor–critic pair undergoes PPO to yield the final **CUDA Agent**.

**Key takeaway:** Sampled rollouts from the single-turn warm-up seed *both* actor and critic, mitigating cold-start issues before PPO-based agentic RL — a pragmatic bootstrapping trick for multi-turn code-generation agents.

**Caption (verbatim):**
"Figure 3 Overview of training pipeline. Following a single-turn RL warm-up stage, the sampled trajectories are used to initialize actor model and critic model before agentic RL stage."

### Figure 4 (p.10) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p10.png]]
> [!quote] caption
> Ablation: RFT. Removing RFT causes training reward to collapse. The concurrent increase in actor entropy

> [!tip] 技术解读（多模态）
> **Figure description (≤120 words):**

The page presents two ablation figures evaluating stability components of a PPO-based RL training pipeline for CUDA Agent. **Figure 4** plots Training Reward and Actor Entropy over ~30 steps, comparing PPO w/ RFT (orange, stable) vs. PPO w/o RFT (green, reward collapses near step 20 while entropy spikes sharply upward). **Figure 5** plots Explained Variation of the Value Function and Response-Length Clipped Ratio, comparing PPO w/ Value Pretrain (orange, flat near zero) vs. PPO w/o Value Pretrain (green, EV drops to ≈ −8 and response length explodes before termination). Both panels share x-axis = training step.

**Key takeaway:** Reward Filtering (RFT) and Value Pretraining are non-removable stability anchors—ablation triggers correlated failure modes (reward collapse � entropy blow-up; EV collapse ↔ trajectory explosion).

**Caption transcription (verbatim):**

**Figure 4** Ablation: RFT. Removing RFT causes training reward to collapse. The concurrent increase in actor entropy suggests that the policy becomes increasingly diffuse and poorly structured.

**Figure 5** Ablation: Value Pretraining. Without Value Pretraining, the critic fails to learn a meaningful value function, as reflected by low explained variance. This leads to inefficient exploration, manifested as excessively long interaction trajectories.

### Figure 5 (p.10) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p10.png]]
> [!quote] caption
> Ablation: Value Pretraining. Without Value Pretraining, the critic fails to learn a meaningful value

> [!tip] 技术解读（多模态）
> **Figure description (≤120 words):**

The page presents two ablation figures evaluating stability components of a PPO-based RL training pipeline for CUDA Agent. **Figure 4** plots Training Reward and Actor Entropy over ~30 steps, comparing PPO w/ RFT (orange, stable) vs. PPO w/o RFT (green, reward collapses near step 20 while entropy spikes sharply upward). **Figure 5** plots Explained Variation of the Value Function and Response-Length Clipped Ratio, comparing PPO w/ Value Pretrain (orange, flat near zero) vs. PPO w/o Value Pretrain (green, EV drops to ≈ −8 and response length explodes before termination). Both panels share x-axis = training step.

**Key takeaway:** Reward Filtering (RFT) and Value Pretraining are non-removable stability anchors—ablation triggers correlated failure modes (reward collapse � entropy blow-up; EV collapse ↔ trajectory explosion).

**Caption transcription (verbatim):**

**Figure 4** Ablation: RFT. Removing RFT causes training reward to collapse. The concurrent increase in actor entropy suggests that the policy becomes increasingly diffuse and poorly structured.

**Figure 5** Ablation: Value Pretraining. Without Value Pretraining, the critic fails to learn a meaningful value function, as reflected by low explained variance. This leads to inefficient exploration, manifested as excessively long interaction trajectories.

### Figure 6 (p.13) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p13.png]]
> [!quote] caption
> Examples of operator classes in our training data.

> [!tip] 技术解读（多模态）
> **Figure 7 — Histogram of Max AST Similarity**

*Architecture/components:* A single-panel histogram on a white background. X-axis is "Max similarity to any test sample" (0.0–1.0). Y-axis is "Proportion (%)" (0–12%). Gray bars show the empirical distribution; a yellow dashed vertical line marks threshold = 0.9.

*Data flow:* Each training sample is compared against every evaluation sample, and its maximum AST (Abstract Syntax Tree) similarity score is recorded and binned into the histogram.

*Key technical takeaway:* The distribution is concentrated near 0.25–0.35 with peak proportion ≈12%, and almost no samples exceed the 0.9 threshold, demonstrating that the training and evaluation sets are essentially disjoint — i.e., minimal risk of data leakage/contamination in the benchmark.

**Caption (verbatim):**
"Figure 7: Distribution of the maximum AST similarity between each training sample and all evaluation samples."

### Figure 7 (p.13) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p13.png]]
> [!quote] caption
> Distribution of the maximum AST similarity between each training sample and all evaluation samples.

> [!tip] 技术解读（多模态）
> **Figure 7 — Histogram of Max AST Similarity**

*Architecture/components:* A single-panel histogram on a white background. X-axis is "Max similarity to any test sample" (0.0–1.0). Y-axis is "Proportion (%)" (0–12%). Gray bars show the empirical distribution; a yellow dashed vertical line marks threshold = 0.9.

*Data flow:* Each training sample is compared against every evaluation sample, and its maximum AST (Abstract Syntax Tree) similarity score is recorded and binned into the histogram.

*Key technical takeaway:* The distribution is concentrated near 0.25–0.35 with peak proportion ≈12%, and almost no samples exceed the 0.9 threshold, demonstrating that the training and evaluation sets are essentially disjoint — i.e., minimal risk of data leakage/contamination in the benchmark.

**Caption (verbatim):**
"Figure 7: Distribution of the maximum AST similarity between each training sample and all evaluation samples."

### Figure 8 (p.22) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p22.png]]
> [!quote] caption
> Reference operator for diagonal matmul (Case D.2).

> [!tip] 技术解读（多模态）
> **Figure Description**

The figure displays a PyTorch reference operator implementation (~35 lines) for diagonal-matrix-times-dense-matrix multiplication (Case D.2).

**Components:**
- **Imports** (lines 1–2): `torch` and `torch.nn as nn`
- **`Model(nn.Module)` class** with three methods:
  - `__init__`: trivial superclass init
  - `forward(self, A, B)`: computes `torch.diag(A) @ B`, where A is a 1D diagonal tensor `(N,)` and B is a 2D matrix `(N, M)`, returning `(N, M)`
  - `get_inputs()`: produces random `A` and `B` tensors
  - `get_init_inputs()`: returns `[]` (no learnable params)
- **Constants**: `M = N = 4096`, defining the workload shape

**Data flow:** 1D diagonal → materialized 2D diagonal matrix → matmul with dense matrix → output.

**Key takeaway:** Diagonal matmul is O(N·M), not O(N²·M) like dense matmul, so an optimized kernel can skip redundant zero-multiplies by exploiting the diagonal structure of A.

**Caption (verbatim):**
**Figure 8** Reference operator for diagonal matmul (Case D.2).

### Figure 9 (p.23) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p23.png]]
> [!quote] caption
> Diagonal matmul kernel implementation (Case D.2).

> [!tip] 技术解读（多模态）
> **Architecture / Data flow.** `ModelNew` (Figure 10) is a thin PyTorch `nn.Module` wrapper that forwards inputs `A (N,)` and `B (N, M)` to a compiled CUDA extension. The launcher (Figure 9) launches 1024 blocks × 128 threads; each thread strides through `output` with a grid-stride loop, derives `row = idx / 4096`, and writes `output[idx] = A[row] * B[idx]`. No diagonal matrix is materialized — only the 1-D diagonal `A` is indexed, and the full N×M result is produced by reusing `A[row]` across all columns `j` of row `row`.

**Key takeaway.** Computing `C[i,j] = A[i] * B[i,j]` row-wise in a grid-stride loop avoids the O(N²) diagonal construction and exploits the broadcast reuse of `A[row]` across the 4096 columns — yielding an N×M output from just O(N+M) input storage and a single fused multiply.

**Captions (verbatim):**
- *Figure 9* Diagonal matmul kernel implementation (Case D.2).
- *Figure 10* Custom operator for diagonal matmul (Case D.2).

### Figure 10 (p.23) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p23.png]]
> [!quote] caption
> Custom operator for diagonal matmul (Case D.2).

> [!tip] 技术解读（多模态）
> **Architecture / Data flow.** `ModelNew` (Figure 10) is a thin PyTorch `nn.Module` wrapper that forwards inputs `A (N,)` and `B (N, M)` to a compiled CUDA extension. The launcher (Figure 9) launches 1024 blocks × 128 threads; each thread strides through `output` with a grid-stride loop, derives `row = idx / 4096`, and writes `output[idx] = A[row] * B[idx]`. No diagonal matrix is materialized — only the 1-D diagonal `A` is indexed, and the full N×M result is produced by reusing `A[row]` across all columns `j` of row `row`.

**Key takeaway.** Computing `C[i,j] = A[i] * B[i,j]` row-wise in a grid-stride loop avoids the O(N²) diagonal construction and exploits the broadcast reuse of `A[row]` across the 4096 columns — yielding an N×M output from just O(N+M) input storage and a single fused multiply.

**Captions (verbatim):**
- *Figure 9* Diagonal matmul kernel implementation (Case D.2).
- *Figure 10* Custom operator for diagonal matmul (Case D.2).

### Figure 11 (p.25) ⭐深度解读
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p25.png]]
> [!quote] caption
> Reference operator for matrix multiplication, division, summation, and scaling (Case D.3).

> [!tip] 技术解读（多模态）
> **Description (architecture/components/data flow + key takeaway):**

The figure shows a single-layer PyTorch `Model` (subclass of `nn.Module`) implementing a fused linear reduction. **Components:** a learnable weight matrix `W` of shape `(hidden_size, input_size)`, plus a scalar `scaling_factor`. **Data flow** on input `x ∈ ℝ^{batch × input}`:
1. `Gemm`: `y = x · Wᵀ` → `(batch × hidden)`
2. `Divide`: `y = y / 2`
3. `Sum`: collapse dim-1 with `keepdim=True`
4. `Scaling`: `y *= scaling_factor` (1.5)

**Config:** batch=1024, input=hidden=8192. **Key takeaway:** despite four annotated ops, the sum-after-matmul reduces the output to a `(batch × 1)` vector, so the dominant cost is the 8192×8192 GEMM; the post-ops are memory-bound and fuse cheaply into the GEMM epilogue.

**Caption (verbatim):**

**Figure 11** Reference operator for matrix multiplication, division, summation, and scaling (Case D.3).

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
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p27.png]]
> [!quote] caption
> Custom operator for matrix multiplication, division, summation, and scaling (Case D.3).

> [!tip] 技术解读（多模态）
> **Description of Main Figure (Figure 13):**

The figure displays a Python code listing defining a `ModelNew` PyTorch module that wraps a single fused custom CUDA kernel. **Components/architecture:**
- **Imports:** `torch`, `torch.nn as nn`, and `cuda_extension` (the custom binding).
- **`ModelNew(nn.Module)` class** holding a learnable `weight` parameter of shape `(hidden_size, input_size)` and a `scaling_factor` hyperparameter.
- **`forward(x)` method:** instead of chaining separate ops, it invokes `cuda_extension.fused_sum_dot_forward(x, weight, scaling_factor)`, which returns a tensor of shape `(batch_size, hidden_size)`.

**Data flow:** input tensor → single fused CUDA kernel (combined sum + dot product + scaling) → output tensor, with no intermediate Python-level operations.

**Key Technical Takeaway (≤120 words):** The figure exemplifies kernel-fusion optimization — collapsing what would normally be separate CUDA launches for summation, matrix multiplication, division, and scaling into a single custom `fused_sum_dot_forward` operator. By exposing the fused kernel through a thin Python/C++ binding (`cuda_extension`), PyTorch's autograd-compatible `nn.Module` interface is preserved while eliminating kernel-launch overhead and intermediate memory traffic. This achieves substantial speedups over naïve operator-by-operator execution by reducing global memory round-trips and letting the GPU execute the entire linear-style transformation in one pass.

**Caption (verbatim):**
> Figure 13  Custom operator for matrix multiplication, division, summation, and scaling (Case D.3).

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
![[assets/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation-p30.png]]
> [!quote] caption
> Fused add-relu kernel implementation (Case D.4).

> [!tip] 技术解读（多模态）
> **Figure 17 — Fused Add-ReLU Kernel (CUDA)**

**Architecture / Components / Data Flow:**
- `fused_add_relu_kernel`: a CUDA device function where each thread processes a strided segment of `total_elements`.
- Inputs (`input1`, `input2`) are loaded as `float4` vectors (4 lanes at once), summed via `__fadd_rn`, then passed through `fmaxf(..., 0.0f)` to fuse ReLU in-register.
- A second pass handles the tail (remainder) elements scalar-wise.
- `fused_add_relu_launcher` computes `grid_size` from `total_elements` (capped at 4096 blocks) and launches with 256 threads/block.

**Key Technical Takeaway:** Operator fusion (add + ReLU) plus `float4` vectorization eliminates intermediate memory writes and quadruples per-thread throughput, while a tail loop preserves correctness for non-multiple-of-4 sizes.

**Caption (verbatim):**
*Figure 17* Fused add-relu kernel implementation (Case D.4).

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

## 关键公式（启发式抽取，引用前请核对原文页码）

- p.6 `LRFT(θ) = −Eτ∼D′`
- p.6 `where τ = (s0, s1, . . . , sT −1) denotes a filtered CUDA agent trajectory, πθ is the policy parameterized by θ,`
- p.7 `and δt = rt + γVϕ(st+1) −Vϕ(st) is the temporal difference error with Vϕ(sT ) = 0. We set γ = 1 and λ = 0.95`
- p.7 `LCLIP(θ) = Eτ∼D`
- p.7 `where ρt(θ) =`

## 技术点深读（DEEP）

![[deep/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.txt`（74680 字符）供引用检索。