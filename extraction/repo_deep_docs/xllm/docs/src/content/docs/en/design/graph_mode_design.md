# graph_mode_design

> 仓 `xllm` · 路径 `docs/src/content/docs/en/design/graph_mode_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/design/graph_mode_design.md

# 深度解读：xLLM Graph Mode Design Document

## 【定位】

本文档系统性地描述了 xLLM 推理引擎中 Graph Mode 的统一抽象设计与三大核心机制（动态维度参数化、Piecewise Graph、多 Shape 可复用内存池），将 Host 驱动的细粒度 kernel 发射流改造为 capture-then-replay 执行流，以降低 Host 调度开销、消除 device 端气泡并提升吞吐与时延稳定性。

---

## 【技术要点】

1. **Capture / Replay 双阶段机制**：同一 shape bucket 首次出现时在专用 stream 上做 capture，记录 kernel 发射、内存操作与依赖；后续命中同一 bucket 的请求直接 replay 录制的图，避免逐 kernel 调度。同一条 capture path 上的控制流、launch shape 与依赖在 replay 期间不可切换到其他动态分支。
2. **三大 Graph Mode 前置条件**：(a) 稳定执行路径——capture 路径不能包含 stream 同步、由 host tensor 驱动的逻辑分支或隐式 host-device 交互；(b) 关键 tensor 的地址稳定——capture 时写入图的地址在 replay 时必须仍有效；(c) operator 行为与结果语义稳定——同一 shape 下必须选中相同的 kernel，不能混用 prefill / chunked prefill / decode 行为，`grid_dim`、`block_dim`、task count、workspace shape、tiling 内容均需稳定。
3. **统一 Graph Executor 抽象**：由 runtime 集中负责 bucketing、persistent buffer、graph cache 管理与 capture/replay 生命周期，把 Graph Mode 运行编排从 model 代码中抽出，避免分散在各 layer / operator 内。执行流可归纳为四步：(1) 按 `num_tokens` 或邻近 shape bucket 化请求；(2) 将 tokens、positions、seq_lens、block_tables 写入 persistent buffer 并更新 `attn_metadata` 与 `plan_info`；(3) 命中 bucket 直接 replay，未命中先 capture/cache 再走 replay；(4) 按场景执行 full graph 或 piecewise graph。
4. **动态维度参数化（Dynamic Dimension Parameterization）**：attention 的真实动态维度除 `num_tokens` 外还包括 `batch_size`、`q_seq_lens`、`kv_seq_lens`、`block_tables_size`；当这些维度影响 task 划分、workspace layout、`tiling_params` 或 kernel path 时，replay 只能复用 capture 时的旧配置，可能产生正确性问题——这是本章要解决的核心问题。
5. **Persistent Buffer 与图实例保活**：tokens、positions、seq_lens、block_tables 等动态输入不能在 replay 前被重新分配到任意新地址，必须先写入 persistent buffer 再原地更新内容；模型图构建过程中临时分配的 tensor 也要随 graph instance 一起保留，避免局部作用域结束时被回收；启用共享内存池时，不同 shape 的 capture 可共用同一份底层物理内存，但对图可见的虚拟地址保持稳定。
6. **Piecewise Graph 回退路径**：当整条路径不可捕获时（例如存在 host 侧分支决策），runtime 会在可捕获段用 full graph，对其余段切到 Piecewise Graph，在 capture / bucket 选择阶段自动降级。

---

## 【关键机制与数据】

**Capture/Reply 工作原理（原文 §1.1）：**
> Capture 时，在专用 stream 上跑一次 forward pass，把 kernel launches、memory operations 和依赖记录到图中；Replay 时，对命中相同 bucket 的请求重放录制好的图，不再由 Host 逐个发射 kernel。

**三种 capture 不安全操作的典型示例（原文 §1.3）：**
> 典型示例 1：ATB PA 与 MLA（在 Ascend CANN commercial 8.3 中）会根据 host 端 `kv_seq_lens` 与 `q_seq_lens` 选择不同的 task layout。
>
> 典型示例 2（原文代码）：
> ```cpp
> Tensor a;
> Tensor b = a * 0.5;  // scalar 被隐式传到 tensor 的 device，导致一次同步 H2D
>
> torch::Tensor max_of_seq = torch::max(input_params.kv_seq_lens);
> max_seq_len_ = std::max(max_of_seq.item<int>(), max_seq_len_);  // host 直接读 tensor 数据
> ```

**Runtime 端 4 个统一职责（原文 §1.2）：**①execution-path stability 周边——按 `num_tokens` / 邻近 shape 进行 bucket 化、对每个 bucket 维护 graph cache（命中直接 replay，未命中先 capture/cache）、可全捕获路径用 full graph、部分路径中断则切到 Piecewise Graph；②address stability 周边——动态输入写入 persistent buffer、图构建期临时 tensor 与 graph instance 同寿命保留、共享内存池下不同 shape 共享同一物理内存但虚拟地址稳定；③统一的 Graph Executor 抽象，集中处理 capture、cache、replay、graph-instance 管理与 backend abstraction；④执行 4 步流（bucket → prepare inputs → capture or replay → 执行 full graph 或 piecewise graph）。

**模型侧需要做的两层适配（原文 §1.3）：**①移除非 capture-safe 操作（流同步、host tensor 驱动分支、隐式 host-device 交互）；②operator 适配——同一输入 shape 下保证执行路径稳定，不混用 prefill / chunked prefill / decode 行为，并稳定 `grid_dim`、`block_dim`、task count、workspace shape、tiling content 等所有 launch 参数。

**动态维度的真问题（原文 §2.1，原文在此处被截断）：**attention 中真实动态因子除 `num_tokens` 外还包括 `batch_size`、`q_seq_lens`、`kv_seq_lens`、`block_tables_size`，一旦这些维度再影响 task 划分、workspace layout、`tiling_params` 或 kernel path，replay 便会因只能复用 capture 期配置而失效。

---

## 【表格解读】

**原文无表格**（文档当前阶段仅包含一个插图 `figures/graph_mode.png`、一段 C++/PyTorch 示意代码和若干 bullet-list 形式的清单，未出现参数表、性能对比表、配置项表等结构化表格）。

---

## 【公式解读】

**原文无公式**（文档未出现数学公式或伪代码算法。§1.3 中虽有一段 C++ 风格的代码块，但这是「典型示例」性质的语法片段，作用是列举非 capture-safe 操作模式，不构成可拆符号的公式。）其展示的句式语义如下以备查：

```cpp
Tensor a;
Tensor b = a * 0.5;  // 隐式 H2D 同步
torch::Tensor max_of_seq = torch::max(input_params.kv_seq_lens);
max_seq_len_ = std::max(max_of_seq.item<int>(), max_seq_len_);  // host 读 device tensor
```
其中：等号右边的 `a * 0.5` 表示 device 端的标量乘法，但 `0.5` 在 host 上必须先经一次 host-to-device 同步传输才能参与 device 计算；`torch::max(...)` 在 device 端产出 tensor，紧接着 `.item<int>()` 把单个元素同步拷回 host。这两处都属于文中强调的"capture 不安全操作"模式。

---

## 【关联】

文档在 Overview 末尾显式列出一个 internal link：

- **[Generative Recommendation Design Document](/en/design/generative_recommendation_design/)**——以推荐系统为案例的姊妹篇，专注于「固定调度（fixed scheduling）、多步执行（multi-step execution）、自定义算子（custom operators）」。本文对应把 Graph Mode 的通用抽象讲透，姊妹篇则把这些通用机制落到 generative recommendation 这种「shape 极固定、调度可重排」的工作负载上，给出真实业务侧的落地示例。

文档内部的章节耦合关系同样值得注意：
- §1.1 提出 Graph Mode 的三条前置条件（execution path / tensor address / operator semantics 稳定）；
- §1.2 与 §1.3 分别对应 runtime 端为前两条做的工程（Graph Executor、persistent buffer、memory pool、graph-instance 保活）与 model 端为第三条做的改造（去掉非 capture-safe 操作、收敛 operator 分支）；
- §2 进入 dynamic dimension parameterization，正式把 §1.1 中"execution path 稳定"这条约束在 attention 维度上的可变性缺口展开讨论（即"哪些动态信息可以随请求变化、哪些必须在 capture 期固化")，从而为后续 piecewise graph 与 multi-shape memory pool 提供问题陈述；
- 因此 §1 是机制总览，§2 起开始把总览中的"可被 shape 干扰的部分"逐一拆解，本文档在 §2 中被截断，后文应继续展开 Piecewise Graph 与 multi-shape memory pool 的具体设计。

---

## 【使用方法】

**原文未涉及** 具体的开启命令、flag 或配置项。该文档明确将自己定位为"面向开发者理解实现原理与关键设计选择"的内部 design doc，并在 Non-goals 中写明"不替代 flags 与使用示例的 feature 文档"。实际启用方式（例如怎样在 serving 配置中打开 Graph Mode、是否需要传 `--graph-mode`、persistent buffer 容量如何设定、bucket 划分数如何指定等）应查阅配套的 feature / usage 文档或姊妹篇 [Generative Recommendation Design Document](/en/design/generative_recommendation_design/)。

## 图文联合解读

- `graph_mode.png`: **1) 图示内容**：上下两条时间轴对比"Without Graph"与"With Graph"。上栏中Launch A–E依次串行触发Kernel A–E，kernel间存在明显的Launch overhead间隙；下栏先Build Graph（通过`cudaGraphExecKernelNodeSetParams`注入节点参数），再以单次Launch Graph驱动A–E紧邻连续执行，右侧标注Speed up表示总耗时缩短。

**2) 技术结论**：Graph模式用一次Launch替代多次Launch，消除了kernel间的调度空隙与设备端bubble；代价是引入一次性建图开销，但被后续每次replay分摊。

**3) 与文档论点关系**：直接佐证文档核心主张——将Host驱动的细粒度kernel流改造为capture-then-replay流程，从而降低Host调度开销、压缩device bubbles，提升吞吐与时延稳定性。
