# graph_mode

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/graph_mode.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/graph_mode.md

# xLLM Graph Mode Feature 文档深度解读

## 【定位】

本文档系统性介绍 xLLM 推理引擎中 **Graph Mode（图模式）** 的能力——通过**预先捕获计算图并复用回放**来削减 CPU 端调度开销、压缩设备气泡，从而提升推理吞吐，是 xLLM 在多硬件后端（ACL/CUDA/MLU）上的核心性能特性之一。

---

## 【技术要点】

1. **图捕获 + 流式内核回放（Streaming Kernel Replay）**：CPU 一次性提交大任务，设备上以流式方式执行众多小 kernel，从根本上**降低启动时延与设备 bubble**。
2. **动态形状参数化（Dynamic Shape Parameterization）**：除 `num_tokens` 之外的关键动态维度（`batch_size`、`kv_seq_lens`、`q_seq_lens`、`block_table_size` 等）作为整图输入参数传入；图启动时由**实际值**注入，kernel 据此采用正确 stride 访问数据，从而兼顾灵活性与图复用。
3. **分段图（Piecewise Graph）**：当部分算子不支持图捕获而**打断整图**时，按断点将后续每段分别捕获为独立图，仍最大化图模式收益，**典型应用是 prefill 与 chunked prefill**。
4. **多形状可扩展内存池（Multi-Shape Reusable Memory Pool）**：跨形状共享同一池基址，不同形状仅以**不同 offset** 偏移使用，避免为每种形状各自开辟 input/output/intermediate 缓冲区造成的浪费。
5. **gflags 驱动的细粒度开关**：核心 flag 为 `enable_graph`（decode 阶段基础开关）；配套 `enable_prefill_piecewise_graph`（prefill 分段图）、`enable_graph_mode_decode_no_padding`（decode 图用真实 `num_tokens` 而非 padding 形状）、`max_tokens_for_graph_mode`（覆盖 token 数上限，`0` 表示不限）。
6. **多硬件后端差异化实现**：在 ACLGraph / CudaGraph / MLUGraph 三种底层实现上各自具备模型支持矩阵，新增模型时必须保证所用 kernel 实现**动态维度参数化**，否则图会断裂。

---

## 【关键机制与数据】

### 工作原理（原文整合）

- **CPU 端调度优化路径**（原文）：「graph mode submits a large task from the CPU once and then executes small kernels in a streaming manner on the device, significantly reducing startup time and device bubbles.」
- **动态形状数据流**（原文）：捕获期将 `batch_size` / `kv_seq_lens` / `q_seq_lens` / `block_table_size` 等**整图输入参数**化 → 内存分配与 kernel 配置阶段据此规划 → 图启动（graph launch）时注入实际值 → kernel 以**正确 stride** 访问张量。
- **分段图触发条件**（原文）：「When some operators do not support graph capture and thus break the full graph, each segment (piece) after the break is captured as a separate graph.」典型用于 **prefill 与 chunked prefill**。
- **内存池机制**（原文）：跨形状共享池基址 → 不同形状使用**不同 offset** → 节省 input/output/intermediate tensor 缓冲占用。
- **新增模型的约束**（原文）：「Ensure that the kernels used in the computation implement dynamic dimension parameterization; otherwise the graph may break and kernels may need to be re-implemented.」

### 性能数据（原文）

> 原文："With Graph Mode enabled, decode-phase throughput **improves by about 8%–10%** on models such as Qwen3-0.6B and Qwen3-1.7B."

- **场景**：decode 阶段开启 Graph Mode。
- **收益**：吞吐提升 **约 8%–10%**。
- **测得该收益的模型**：**Qwen3-0.6B** 与 **Qwen3-1.7B**。
- **注意事项**：原文未给出 prefill 阶段或 chunked prefill 阶段的量化收益数字，亦未给出硬件后端（ACL/CUDA/MLU）间的对比数据。

---

## 【表格解读】

原文核心表格为「模型 × 后端」Graph 支持矩阵，原文表格逐字还原如下：

| Model | ACLGraph | CudaGraph | MLUGraph |
|------|----------|-----------|----------|
| Qwen3/Qwen3-MoE | ✅ | ✅ | ✅ |
| DeepseekV3.2 | ✅ |  | ✅ |
| GLM4.5/4.6/4.7 | ✅ |  |  |
| Qwen2.5-VL |  |  | ✅ |
| Qwen3-VL/Qwen3-VL-MoE | ✅ |  |  |
| GLM4V | ✅ |  |  |
| GLM4V-MoE | ✅ |  |  |

逐行解读：

1. **Qwen3 / Qwen3-MoE**：三列全 ✅，是**唯一在三种硬件后端均完整支持 Graph Mode** 的模型族，可作为跨平台 Graph Mode 的基准验证目标。
2. **DeepseekV3.2**：ACLGraph ✅、MLUGraph ✅、**CudaGraph 空白**——表明该 MoE 大模型在 CUDA 后端暂未启用图模式，可能与动态维度实现或算子覆盖度有关（原文未给出原因）。
3. **GLM4.5 / 4.6 / 4.7**：仅 ACLGraph ✅，CUDA 与 MLU 列空白，**仅在 ACL 后端落地**。
4. **Qwen2.5-VL**：仅 MLUGraph ✅，ACLGraph 与 CudaGraph 均为空白，**该多模态模型目前只在 MLU 后端打通图模式**。
5. **Qwen3-VL / Qwen3-VL-MoE**：仅 ACLGraph ✅，CUDA 与 MLU 暂未覆盖。
6. **GLM4V**：仅 ACLGraph ✅，其余两列空白。
7. **GLM4V-MoE**：仅 ACLGraph ✅，其余两列空白。

**矩阵共性观察**（基于表格事实）：ACLGraph 覆盖**最广**（6/7 行 ✅），MLUGraph 次之（3/7 行 ✅），**CudaGraph 仅覆盖 Qwen3/Qwen3-MoE**；视觉-语言（VL/V）类模型目前主要走 ACLGraph 与 MLUGraph，未见 CudaGraph 支持。

---

## 【公式解读】

**原文无公式**。文档描述的是工程开关与机制，未出现任何 LaTeX 表达式、伪代码公式或带数学符号的量化模型；性能数据以区间百分比（8%–10%）自然语言形式给出。

---

## 【关联】

根据文末「Related Documentation」与文中交叉引用，可梳理如下关联链路：

1. **CLI Reference（[/en/cli_reference/](/en/cli_reference/)）**：本文档 `Usage` 段末尾明确跳转——所有 `enable_graph`、`enable_prefill_piecewise_graph`、`enable_graph_mode_decode_no_padding`、`max_tokens_for_graph_mode` 等 gflags 的**完整说明**应查阅该参考页；本文档定位为「使用指南速查」，CLI Reference 提供权威参数清单。
2. **Graph Mode Design Document（[/en/design/graph_mode_design/](/en/design/graph_mode_design/)）**：文末直接链接，作为本文档的**设计层深化文档**。文档自身预告该设计文档涵盖：ACL Graph / CUDA Graph 基础、动态维度参数化（Dynamic Dimension Parameterization）、分段图（Piecewise Graph）、多形状内存复用（Multi-Shape Memory Reuse）——即本文档三大 Feature 子节的**理论与实现细节展开**。
3. **上游能力依赖**：本文档明确指出 Graph Mode 的可用性受制于 **kernel 是否实现动态维度参数化**（caution 段），因此与算子库实现深度耦合；新增模型时若 kernel 不支持动态维度，需**重新实现 kernel**，否则图会断裂。
4. **下游性能受益对象**：decode 阶段（Qwen3-0.6B、Qwen3-1.7B 已有 8%–10% 量化收益）、prefill / chunked prefill 阶段（通过 `enable_prefill_piecewise_graph` 启用分段图受益）。
5. **多硬件后端并行关系**：ACLGraph / CudaGraph / MLUGraph 三套实现彼此独立，但通过同一组 gflags 接口暴露，构成「统一开关 + 差异化实现」的产品矩阵。

---

## 【使用方法】

### 最小启用（仅 decode 阶段开图模式）

```shell
--enable_graph=true
```

### 完整启用（decode 图 + prefill 分段图，并限制覆盖 token 数）

```shell
--enable_graph=true \
--enable_prefill_piecewise_graph=true \
--max_tokens_for_graph_mode=2048
```

### decode 图捕获去除 padding（使用真实 `num_tokens`）

```shell
--enable_graph=true \
--enable_graph_mode_decode_no_padding=true
```

### gflags 含义一览（原文条目）

| Flag | 作用（原文） |
|------|--------------|
| `enable_graph` | enables the base Graph Mode capability for the decode phase（开启 decode 阶段基础图模式能力） |
| `enable_prefill_piecewise_graph` | enables Piecewise Graph for the prefill phase（为 prefill 阶段启用分段图） |
| `enable_graph_mode_decode_no_padding` | builds decode graphs with the actual `num_tokens` instead of the padded shape（用真实 token 数而非 padding 形状构建 decode 图） |
| `max_tokens_for_graph_mode` | limits the maximum number of tokens covered by Graph Mode; `0` means no limit（限制图模式覆盖的最大 token 数；`0` 表示不限制） |

### 平台/模型启用注意事项（原文 caution）

> 「Ensure that the kernels used in the computation implement dynamic dimension parameterization; otherwise the graph may break and kernels may need to be re-implemented.」

—— 即在为新模型开启 Graph Mode 前，须确认所用 kernel 已实现**动态维度参数化**，否则图会断裂，必要时需重写 kernel。具体到模型 × 后端是否可用，请查阅上文「Model Support」表格。

### 完整参数说明的获取途径

原文：「For a more complete description of the flags, see [CLI Reference](/en/cli_reference/).」——更详细的 flag 说明请跳转 CLI Reference 页面；本文档不再赘述。
