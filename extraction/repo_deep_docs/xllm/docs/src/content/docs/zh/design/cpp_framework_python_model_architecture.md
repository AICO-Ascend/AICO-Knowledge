# cpp_framework_python_model_architecture

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/design/cpp_framework_python_model_architecture.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/design/cpp_framework_python_model_architecture.md

# 一体化深度解读：C++ Serving Framework + Python Model Execution 架构决策

---

## 【定位】

本文是一篇架构决策（Architecture Decision Record）类文档，回答两个核心问题：**为什么 xLLM 要在已有 C++ serving framework 中接入 Python model execution**，以及**为什么 Python 侧同时包含 Model 和 `ModelExecutor` 两层**。它只讨论架构选择本身，不涉及实现类、接口细节或迁移步骤。

---

## 【技术要点】

1. **C++ 与 Python 职责严格分层**：
   - C++ 侧保留 `Input/Output Processing`、`Continuous Batching Scheduler`、`KV Cache Manager`、`Distributed Runtime`、`Worker Runtime`、`Sampling`、`Speculative Decoding`、`Observability`。
   - Python 侧拆分为四块：`Model`（结构/权重/forward/logits）、`ModelExecutor/Runner`（persistent inputs/padding/graph 生命周期）、`AttentionBackend`（plan/workspace/backend state）、`Python Distributed`（仅 model 内 TP group 与 collective）。

2. **跨语言边界"窄且零拷贝"**：C++ 已经构造好的 Batch、page table、sequence length、slot mapping 等不能由 Python 重算；跨语言只传递一次 per step 的 **PyTorch tensor + metadata view**，tensor 保持零拷贝。

3. **graph 与 plan 的归属下沉到具体 backend**：
   - `common attention metadata` 仍由 C++ `InputBuilder` 构造并以 view 形式交由 Python `AttentionBackend` 消费。
   - "对于需要 plan 的 backend，同一 attention group 每个 step 只 plan 一次，所有 layer 复用该 plan"。
   - 公共 model/runner 接口**不规定** CUDA graph、ACL graph 或其他设备 graph 的类型；不同硬件可独立提供 runner，不共享同一 graph 继承结构。

4. **MTP 等 speculative decoding 的整体控制流仍在 C++**：Python 只执行其相关模型的 tensor 计算，不参与调度或 KV cache 决策。

5. **Python-first kernel 与调试能力**：AOT Triton/TileLang kernel 难以覆盖 model size、TP size、batch/sequence shape、dtype、量化格式与硬件型号的全部组合；改用 Python 路径后可直接调用 JIT kernel、Python-first 量化 loader、hook、tensor dump 与社区 profiler 与参考实现做数值对齐。

6. **进程与解释器边界约束**："每个 rank 保持独立进程和 Python 解释器。C++ serving 线程不进入 Python，只有 worker 的 model execution 路径跨越解释器边界"。

7. **七条硬约束（task 部分原文逐条列出）**：包括 model 不能复制 scheduler/KV cache/请求状态、padding/plan/graph state 不能散落在 model layer 中、跨语言 metadata contract 必须窄、Python eager 每步开销必须受 graph execution 覆盖等。

---

## 【关键机制与数据】

### 数据流（原文 ASCII 图所示的三层结构）

```
┌─────────────────────────────────────────────────────────────┐
│ C++ Serving Framework                                       │
│ Input/Output Processing · Continuous Batching Scheduler      │
│ KV Cache Manager · Distributed Runtime · Worker Runtime      │
│ Sampling · Speculative Decoding · Observability              │
└───────────────────────────┬─────────────────────────────────┘
                            │ PyTorch tensor + metadata view
                            │ once per step
┌───────────────────────────┴─────────────────────────────────┐
│ Python Model Execution                                      │
│ Model：model structure · weights · forward · logits          │
│ ModelExecutor/Runner：persistent inputs · padding · graph    │
│ AttentionBackend：plan · execute · backend state            │
│ Distributed：TP group · collective                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ torch.ops / backend API
┌───────────────────────────┴─────────────────────────────────┐
│ Device Kernels and Runtime                                  │
│ xllm_ops · Triton/TileLang · attention kernels · graph API   │
└─────────────────────────────────────────────────────────────┘
```

### 工作原理要点

- **每 step 一次调用**：C++ framework 在每个 step 调用一次 Python model execution；其余时间 C++ 独立运行 serving 流程。
- **Model 与 ModelExecutor 分层**：model 只负责权重和计算，`ModelExecutor`/runner 负责执行状态；这与 vLLM 和 SGLang 中 Model 与 ModelRunner/ModelExecutor 的基本职责分离一致。
- **Device 透明性**：通过 PyTorch dispatch 或具体 backend 选择硬件实现，model layer **不选择** CUDA、NPU 或其他设备实现（原文明确写出此约束）。
- **Kernel 路径**：关键 kernel 仍可由 C++、CUDA、AscendC 等 native 实现提供；"选择 Python model 不等于用 Python 重写 kernel"。

### 性能相关表述（原文直接给出的定性结论，非数值指标）

- 原文明确："本次引入 Python 不是因为 C++ model 无法达到性能要求"。
- 原文明确："Python eager 的每步开销必须受到控制。达到目标生产性能需要覆盖 decode、prefill 和 mixed batch 的 graph execution"。
- 原文对 AOT 的限制：kernel 需要适配不同 model size、TP size、batch/sequence shape、dtype、量化格式和硬件型号；"AOT 需要提前准备这些组合，也难以在实际部署硬件上根据运行时 shape 做 autotuning"——这是为何偏好 JIT/Python 路径的理由，而非性能数字。

---

## 【表格解读】

### 原文表格：四种解法对比

| 解法 | 能解决什么 | 主要限制 |
|---|---|---|
| 继续只使用 C++ libtorch model | 保持现有执行路径和运行时依赖 | 社区 Python 模型仍需重新实现，不能解决模型迁移和长期同步成本 |
| Python model 在 `forward()` 中直接使用 runner | 只增加一个 Python model 入口，接入简单 | model 同时持有权重、persistent input、padding、attention plan 和 graph state，难以保持社区 model 的职责和结构 |
| Python model + C++ model executor | 可以复用社区 model，并复用部分 C++ executor | persistent input、padding、attention plan 和 graph state 横跨 C++/Python；新增 Python attention backend 或硬件 graph 时仍需修改 C++ executor |
| Python model + Python `ModelExecutor` | model 和 execution state 都能复用 Python 生态；runner、attention backend 和 graph 可以在 Python 内协同演进 | 需要嵌入式 Python、跨语言 metadata contract 和 Python graph 能力 |

**逐行解读：**

- **第一行（继续只使用 C++ libtorch model）**：承认这是"已经验证的 native 路径"，仍适合现有模型和拒绝 Python runtime 的部署场景。但未触及本任务的首要问题——社区模型仍需重新实现，后续维护需同步两份代码。结论是"继续存在，但不能单独承担新模型扩展"。

- **第二行（Python model 在 `forward()` 中直接使用 runner）**：是最短的接入路径，但将变化频率不同的两类职责耦合在同一个对象中。model structure / weight / raw forward 应贴近社区实现；而 persistent buffer / padding / attention plan / graph 随 backend、batch shape 和硬件变化。耦合后移植社区 model 仍需理解 xLLM 完整 execution state，model 也无法脱离 runner 独立测试复用。

- **第三行（Python model + C++ model executor）**：保持 model/executor 分层，并让 C++ 准备 persistent input 和 graph。但 attention plan、workspace、padding metadata、graph capture 必须与 Python attention backend 保持一致——要么把 backend 私有状态暴露给 C++，要么 C++/Python 各维护一套状态转换。后续增加 Python backend 或硬件 graph 时修改仍跨语言。

- **第四行（Python model + Python `ModelExecutor`）**（**最终选择**）：让 model 保持接近社区 `nn.Module`，execution state 与 Python runner、attention backend、graph 实现在同一侧演进；C++ 只提供 Batch/tensor/metadata 并继续承担外围 serving runtime。代价是嵌入式 Python 与跨语言 contract——但成本边界明确、可独立验收。

**选型结论原文摘录：**"因此选择第四种解法。关键原因不是'Python 比 C++ 快'，而是它同时满足社区 model 迁移、model/executor 职责分离，以及 backend/graph 在 Python 内演进这三个任务要求。"

---

## 【公式解读】

**原文无公式**。文档仅以 ASCII 文本框图描述数据流与职责边界，未出现任何 LaTeX 数学公式或伪代码公式表达式。性能数据亦未以数学公式形式呈现。

---

## 【关联】

本节基于文档正文提及的模块/特性梳理上下游关系（原文链接为空 `(无)`，故仅以文中文字引用为线索）：

- **C++ 子系统被复用、不被替代**（来自 §1.1、§3、§Task 约束）：
  - `Input Processing`（tokenization / chat template / multimodal input processing）
  - `Continuous Batching Scheduler`（chunked prefill / prefill-decode scheduling / request priority / schedule overlap）
  - `Worker Runtime`（构造模型输入、管理设备资源与执行流程）
  - `KV Cache Manager`（KV block / prefix cache / 多级 KV cache）
  - `Distributed Runtime`（master/worker / 多 rank / 多节点 / **PD 分离** / **KV transfer**）
  - `Sampling` / `Speculative Decoding`（`MTP` / `Eagle` / `Suffix` 的 draft、verification、token acceptance）
  - `Observability`（profiling / metrics / device monitoring）
  - 上述模块继续负责 Batch、page table、sequence length、slot mapping 等"已经在 C++ 构造好的数据"。

- **Python 侧内部依赖**（来自 §3 职责划分）：
  - `Python Model` ← 调用 → `ModelExecutor/Runner`（持有 persistent inputs / padding / graph）
  - `ModelExecutor/Runner` ← 调用 → `AttentionBackend`（plan / execute / backend-specific state）
  - `AttentionBackend` ← 消费 → **C++ `InputBuilder` 产出的 `common attention metadata` view**（明确归属 C++，跨语言 ownership）
  - `Python Distributed` ← 协同 → `Model`（仅 model 内部 TP group / collective），但 worker/rank 管理、PD 分离、KV transfer 仍由 C++ `Distributed Runtime` 承担。

- **Device 层与上层解耦**（来自 §3）：
  - `xllm_ops` · `Triton/TileLang` · `attention kernels` · `graph API` 通过 `torch.ops / backend API` 提供。
  - model layer **不选择** CUDA、NPU 等设备实现。
  - 公共 model/runner 接口**不规定** CUDA graph、ACL graph 等设备 graph 类型（每个硬件可有独立 runner，不共享同一 graph 继承结构）。

- **与社区生态对齐点**（来自 §4.2）：
  - vLLM / SGLang 中 **Model 与 ModelRunner/ModelExecutor 的基本职责分离**——本文直接引用此约定作为 Python 侧分层依据。
  - Hugging Face / vLLM / SGLang / 模型厂商提供的 `nn.Module`、weight loader、layer API 作为参考实现来源。

- **被显式排除或弱化的路径**（来自 §4.1 与 §1.2 末尾）：
  - `torch.compile` / `Dynamo` / `FX` / `Inductor`：原文承认它们可直接处理 Python model 但**不能直接处理 C++ `torch::nn::Module` 定义的模型图**；同时明确其"优先级低于社区模型迁移、JIT kernel、量化和调试能力"。
  - AOT Triton/TileLang kernel：原文说明其需要覆盖 model size、TP size、shape、dtype、量化、硬件型号全部组合，且难做运行时 autotuning。

- **下游设计约束（来自 §Task 七条约束）**：
  - Python model **不得**复制 scheduler / KV cache manager / 请求状态。
  - persistent inputs / padding / attention plan / graph state **不得**散落到 model layer。
  - 跨语言 metadata contract 必须窄，tensor 零拷贝。
  - decode / prefill / mixed batch 都需 graph execution 覆盖。

---

## 【使用方法】

**原文未涉及**。本文为架构决策文档，frontmatter 仅声明 `sidebar.order: 3` 与版权信息（Apache License 2.0, Copyright 2026 The xLLM Authors），正文明确说明："**本文只讨论架构选择，不描述实现类、接口细节或迁移步骤**"。文档未提供任何启用开关、配置项、构建命令、部署参数或调用 API。文档内提供的两条 ASCII 文本框图（§1.1 的 C++ framework 流程、§3 的三层架构）属于职责说明，不属于可执行配置。
