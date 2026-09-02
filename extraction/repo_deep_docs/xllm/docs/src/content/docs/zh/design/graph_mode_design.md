# graph_mode_design

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/design/graph_mode_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/design/graph_mode_design.md

# xLLM Graph Mode 设计文档 深度解读

---

## 【定位】

本篇文档定义 xLLM 推理引擎中 **Graph Mode** 的统一抽象与三项关键设计（动态维度参数化、Piecewise Graph、多 Shape 显存池），目的是在推理服务场景中，将 Host 频繁下发的小粒度 kernel 启动转为"先捕获、后重放"的图执行流程，从而降低 Host 调度开销、减少设备气泡、提升吞吐与时延稳定性。

---

## 【技术要点】

1. **Graph Capture / Replay 两阶段机制**：第一次遇到某 shape bucket 时，在专用 stream 上执行一次 forward 并把 kernel 启动、内存操作和依赖关系记录成图；后续相同 bucket 的请求直接重放该图（详见 1.1）。
2. **Graph Mode 三项前提**：执行路径稳定、关键 Tensor 地址稳定、算子与结果语义稳定——前两项由运行时负责，第三项由模型/算子适配负责（详见 1.1、1.2、1.3）。
3. **运行时统一 Graph Executor**：负责请求分桶（按 `num_tokens` 或相近 shape）、持久化 buffer 维护、graph cache、capture/replay 生命周期管理与后端屏蔽；模型侧不再承担图组织逻辑（详见 1.2）。
4. **动态维度参数化的边界划分**：会改变 `grid_dim`、`block_dim`、task 数量、workspace 布局、tiling key 的维度属于"决定图形态的维度"，只能走分桶或重建图；不改变执行形态的维度（如 `batch_size`、`q_seq_lens`、`kv_seq_lens`、`block_tables`、`new_cache_slots`、`plan_info`）才可作为参数化对象（详见 2.2.1、2.2.2）。
5. **Piecewise Graph**：将一条 forward 拆成"可图化 piece"（捕获为子图）与"非图化 piece"（保留 eager），replay 时按 capture 顺序串接，专门用于 chunked prefill 等 attention 路径无法整图捕获的场景（详见 3.1、3.2）。
6. **分桶粒度会随场景扩张**：decode 通常只按 `num_tokens` 建桶；chunked prefill 必须把 `num_tokens × batch_size` 乃至 `seq_lens` 组合纳入分桶键，否则 attention 在 replay 时会沿用错误的批次划分（详见 3.2.1）。

---

## 【关键机制与数据】

### 3.1 Graph Mode 运行时流程（原文: 1.2 节）

xLLM Graph Executor 在运行时按以下四步执行：

1. **请求分桶**：按 `num_tokens` 或相近 shape 归类到 bucket。
2. **输入准备**：将 `tokens`、`positions`、`seq_lens`、`block_tables` 等动态输入写入持久化 buffer，并更新 `attn_metadata`、`plan_info` 等动态元数据。
3. **capture / replay 决策**：bucket 命中 → 直接 replay；未命中 → 先 capture、缓存图，再进入 replay。
4. **执行图**：按场景执行完整图或 Piecewise Graph。

### 3.2 三项关键 Tensor 持久化要求（原文: 1.2 节）

- **动态输入**：`tokens`、`positions`、`seq_lens`、`block_tables` 必须在 replay 前写入持久化 buffer，不能在 replay 前重新分配到任意新地址。
- **过程临时 Tensor**：模型计算图过程中临时分配的 Tensor 都需要持久化保存到对应的 graph instance 中，不能随作用域结束触发 Tensor 回收。
- **共享内存池**：启用后，不同 shape 的 capture 可复用同一组底层物理内存，但 graph 看到的虚拟地址仍需保持稳定。

### 3.3 模型适配的两类典型破坏 capture 的操作（原文: 1.3 节）

- **典型示例 1**（算子内部依赖 host 决策）：Ascend CANN 商发 8.3 的 ATB [PA](https://www.hiascend.com/document/detail/zh/canncommercial/83RC1/API/ascendtbapi/ascendtb_01_0197.html) 和 [MLA](https://www.hiascend.com/document/detail/zh/canncommercial/83RC1/API/ascendtbapi/ascendtb_01_0314.html) 算子，会根据 host 侧 `kv_seq_lens` 和 `q_seq_lens` 选不同任务排列——这条 host 分支决策在 capture 后会固化，无法在 replay 时切换。
- **典型示例 2**（host 标量参与 Tensor 计算、host 直接读取 Tensor）：如 `Tensor b = a * 0.5;` 会隐式触发 h2d 同步；`torch::max(...).item<int>()` 让 host 读取 tensor 数据。

### 3.4 decode 与 chunked prefill 在 attention 上的本质差异（原文: 3.2.1 节）

| 场景 | `num_tokens` 与 `batch_size` 关系 | attention 路径选择 |
|---|---|---|
| **decode** | 单步通常"每个序列生成一个 token"，`num_tokens` 与 `batch_size` 基本一一对应；`q_seq_lens` 模式相对稳定 | 可随 full graph 一起捕获 |
| **chunked prefill** | `num_tokens` 与 `batch_size` 不绑定，相同 `num_tokens` 可对应完全不同请求组合 | attention 留在图外，其他稳定部分进入 Piecewise Graph |

文档中给出的同一 `num_tokens = 128` 的三种组合（原文 3.2.1）：

- `num_tokens = 128, batch_size = 2, q_seq_lens = [64, 64]`
- `num_tokens = 128, batch_size = 4, q_seq_lens = [32, 32, 32, 32]`
- `num_tokens = 128, batch_size = 8, q_seq_lens = [16, 16, 16, 16, 16, 16, 16, 16]`

> 原文：这些请求虽然 `num_tokens` 相同，但并不是同一种 shape；attention 的任务数量划分、本地索引、`q_seq_lens` / `kv_seq_lens` 长度以及 `plan_info` 都和 `batch_size` 直接相关。

### 3.5 通信相关场景的桶键扩张（原文: 2.3 节末尾）

> 原文：通信相关场景就是典型例子，例如 Attention DP + MoE EP 下，通信规模可能取决于最大 DP Data Size，而不完全等于单卡本地的 `num_tokens`。

---

## 【表格解读】

**原文无表格**。文档没有给出任何 markdown/HTML 表格；上述 3.4 节中的对比是基于原文散文叙述重构的，并非文档原文表格。

---

## 【公式解读】

文档中并未给出标准 LaTeX 公式，而是给出三段 C++ 伪代码片段，可视为 launch 参数化与算子 launch 形态的形式化描述，逐字保留并解释如下：

### 公式 ①：简化 norm kernel——launch params 一旦进图即固化

```cpp
int grid_dim = num_tokens;
NormKernel<<<grid_dim, block_dim>>>(x, y, ...);
```

**符号含义：**

- `grid_dim`：CUDA/HIP/Ascend 等执行模型中的 grid 维度，等于 `num_tokens`，表示按 token 数并行划分任务。
- `block_dim`：每个 grid 内 block（或 thread block）的尺寸。
- `num_tokens`：当前请求的 token 总数。
- `x, y, ...`：norm 算子的输入/输出 tensor。

**作用**：原文用此式说明"凡参与 launch 配置的 `num_tokens`，属于图形态的一部分"。一旦 capture 完成，replay 不能在同一张图里把 `grid_dim = 128` 改成 `grid_dim = 256`——这是判断一个动态维度能否参数化的判据。

---

### 公式 ②：改造前——host 侧 planning 决定 launch 和 workspace

```cpp
// Host side
auto plan_info = PlanAttention(q_seq_lens_host, kv_seq_lens_host, ...);
WritePlanToWorkspace(attention_workspace, plan_info);

AttentionKernel<<<grid_dim, block_dim>>>(
    q, k, v, out,
    attention_workspace,
    tiling_params);
```

**符号含义：**

- `PlanAttention(...)`：host 端依据 `q_seq_lens_host`、`kv_seq_lens_host` 计算 attention 的任务划分方案，返回 `plan_info`。
- `q_seq_lens_host`、`kv_seq_lens_host`：保存在 host 内存的 query / kv 序列长度数组。
- `WritePlanToWorkspace(attention_workspace, plan_info)`：把 planning 结果写入 device 端 workspace。
- `attention_workspace`：attention 算子使用的 workspace 内存。
- `tiling_params`：tiling 相关参数，控制 kernel 内部切分策略。
- `grid_dim, block_dim`：launch 参数。
- `q, k, v, out`：attention 的输入/输出 tensor。

**作用**：原文用此式展示改造前 NPU attention 的常见实现路径——`plan_info` 由 host 生成，replay 时图不会自动重做 planning，因此只能重复 capture 时那次 launch 和那次 workspace 布局。

---

### 公式 ③：改造后——`kv_seq_lens` 等动态信息外置到 device 端持久化 buffer

```cpp
struct AttentionLaunchArgs {
  void* q;
  void* k;
  void* v;
  void* out;
  int32_t batch_size;
  int32_t* kv_seq_lens;   // device buffer
  void* attention_workspace;
  void* tiling_params;
};

LaunchAttentionKernel(args);
```

**符号含义：**

- `q, k, v, out`：attention 的输入/输出 tensor 指针。
- `batch_size`：动态 batch 大小，作为参数传入 launch args。
- `kv_seq_lens`：指向 **device 端持久化 buffer** 的指针（原文明确注释 `// device buffer`），kernel 在执行时直接读取；这是参数化的核心——launch 形态保持固定，但每次 replay 读到的 `kv_seq_lens` 内容可以更新。
- `attention_workspace`：workspace 指针（保持固定地址）。
- `tiling_params`：tiling 参数指针（保持固定地址）。
- `LaunchAttentionKernel(args)`：用结构化 launch args 发射 attention kernel。

**作用**：原文用此式说明参数化的目标形态——在固定 launch 形态下，把 `q_seq_lens`、`kv_seq_lens`、`block_tables_size`、`plan_info` 等写入设备侧持久化 buffer，再由 kernel 在执行时读取，从而让同一个 bucket 在不重 capture 的前提下承载多种真实动态请求。

---

## 【关联】

### 6.1 文档内部引用的上下游设计文档

- **[生成式推荐设计文档](/zh/design/generative_recommendation_design/)**：原文中两处明确关联——
  - 文档开头："若希望看一个更偏业务推理场景、并且聚焦固定调度、多步执行和定制算子的案例，可参考：[生成式推荐设计文档](/zh/design/generative_recommendation_design/)"
  - 这是文档正文中唯一指向其他设计文档的内部链接，说明 Graph Mode 是 xLLM 中多个推理场景共享的底层能力，生成式推荐场景是其重要落地场景之一。

### 6.2 文档中提到的外部技术依赖

- **Ascend CANN 商发 8.3** 的 ATB 算子：
  - [PA](https://www.hiascend.com/document/detail/zh/canncommercial/83RC1/API/ascendtbapi/ascendtb_01_0197.html) —— host 侧根据 `kv_seq_lens`/`q_seq_lens` 决定任务排列。
  - [MLA](https://www.hiascend.com/document/detail/zh/canncommercial/83RC1/API/ascendtbapi/ascendtb_01_0314.html) —— 同上。
  - 文档指出 ATB PA 还会根据序列长度与 batch size 实时决定是否启用 flash-decoding 长序列模式，tiling key 与 `kernel_name` 都会变，进入 Graph Mode 前需要先收敛。

### 6.3 三大关键设计之间的关系（文档内部隐含关系）

- **动态维度参数化（§2）** 解决"bucket 选定后，replay 如何承载剩余动态信息"；
- **Piecewise Graph（§3）** 解决"无法整图捕获时，如何最大化图执行收益"；
- **多 Shape 复用的显存池**（概述中提及，本文未展开）解决"不同 shape capture 的虚拟地址稳定性与物理内存复用"——三者共同支撑 Graph Executor 的统一封装。

### 6.4 文档中明确指出的非目标边界

- 不覆盖所有算子或所有模型的适配细节；
- 不替代功能文档中的参数说明与使用示例；
- 不展开不同图执行后端之间的差异（统一抽象设计层面）。

---

## 【使用方法】

**原文未涉及**。本文档为设计文档（Design Document），通篇聚焦原理、机制与关键设计选择，原文未给出：

- 启用 Graph Mode 的配置项 / 环境变量 / 启动开关；
- bucket 维度、`bucket_num_tokens` 的具体配置接口；
- 多 Shape 显存池的容量、复用策略的配置参数；
- capture / replay 的具体命令或 API 调用示例。

如需了解具体启用方式与配置参数，原文提示需参考 **功能文档中的参数说明与使用示例**（见原文"非目标"段落），即应查阅 xLLM 的功能文档而非本设计文档。

## 图文联合解读

- `graph_mode.png`: **图文联合解读：**

**1) 图中内容：** 上半部分「Without Graph」展示传统 eager 模式——Host 端连续发起 Launch A~E 五个调度块，每个调度都有开销，对应设备端 A~E 五个 kernel 之间存在间隙。下半部分「With Graph」展示经过 Build Graph 阶段后，单次 Launch Graph 即可驱动 A~E 紧凑执行，并辅以 `cudaGraphExecKernelNodeSetParams` 进行参数更新；右侧标注「Speed up」。

**2) 技术结论：** Graph Mode 通过将多次小粒度 kernel 启动合并为一次图重放，显著压缩 Host 调度开销与设备气泡，使 kernel 紧密背靠背执行。

**3) 与文档关系：** 直观印证文档 1.1 节关于"将 Host 频繁的小 kernel 启动转化为先捕获、后重放，降低调度开销、减少执行气泡、提升吞吐与时延稳定性"的核心论点。
