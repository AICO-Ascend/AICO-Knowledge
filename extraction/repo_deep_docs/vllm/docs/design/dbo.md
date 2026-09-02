# Dual Batch Overlap

> 仓 `vllm` · 路径 `docs/design/dbo.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/dbo.md

# Dual Batch Overlap (DBO) 设计文档深度解读

---

## 【定位】

本文档描述 vLLM 中的 **Dual Batch Overlap (DBO)** 系统：通过对模型运行器中的 batch 进行拆分（microbatch），让两个 CPU worker 线程以"乒乓"方式交替执行，从而将 MoE 层稀疏 all-to-all 通信与相邻计算在时间轴上重叠起来——专门面向 **DP + EP（数据并行 + 专家并行）** 部署形态。

---

## 【技术要点】

1. **作用范围限定**：DBO 当前仅支持 DP+EP 部署，且需配合 DeepEP all-to-all 后端（`deepep_low_latency` 用于解码密集型，`deepep_high_throughput` 用于预填充密集型）。
2. **Batch 拆分与统一性约束**：`GPUModelRunner` 将 batch 拆为两个 microbatch；所有 DP rank 必须**一致地**决定是否启用 microbatch——只要任一 rank 无法 microbatch，则所有 rank 全部禁用；启用前还需将 token 数 padding 到所有 rank 中最大值，并保证 padding 后第二个 microbatch 非空，否则整体放弃。
3. **双线程 Ping-Pong**：两个 UBatch 线程并行启动，由 `UBatchContext` 协调；当任一线程在 `FusedMoEModularKernel.forward` 内的 `dbo_yield` 让出点暂停时，唤醒另一个线程继续运行，循环切换直到模型执行结束。
4. **CUDA Graph 约束**：CUDA graph 完全由 `UBatchWrapper` 管理，因此 DBO **只支持 Full CUDA graphs**；一旦 DBO CUDA graph 被捕获，即可重放而无需多线程/CPU 同步。
5. **接收回调机制**：`dbo_register_recv_hook` 注册的回调可由另一线程通过 `dbo_maybe_run_recv_hook` 触发，通常用于等待 all-to-all kernel 完成。
6. **启用门槛**：通过 `--enable-dbo` 启用；并依赖 `--data-parallel-size N`（N>1）、`--enable-expert-parallel`；同时受 `--dbo-decode-token-threshold`（纯解码 batch 启用 DBO 的最小 token 数）和 `--dbo-prefill-token-threshold`（含至少一段预填充的 batch 启用 DBO 的最小 token 数）两个阈值控制。

---

## 【关键机制与数据】

### 工作原理

1. **`GPUModelRunner` 中的两步拆分**
   - **第一步**：跨 DP rank 协调 microbatch 决策；进行 token 数 padding；校验 padding 后第二 microbatch 非空。
   - **第二步**：将 `CommonAttentionMetadata` 沿 batch 维度切成两半，形成**每 microbatch 一份**的 attention metadata。

2. **`UBatchWrapper` 双轮调用**
   - 内部对同一模型顺序调用两次（每个 microbatch 一次）；每次调用运行于独立的 UBatch 线程；线程间通过 `UBatchContext` 同步；每个线程持有半切片后的 attention metadata。
   - `forward` 通过判断 `forward_context` 中是否存在 `ubatch_slices` 来决定是否走 DBO 路径。

3. **Ping-Pong 同步原语**（位于 `FusedMoEModularKernel.forward` 内）
   - `dbo_yield`：当前线程休眠，唤醒对端 UBatch 线程。
   - `dbo_register_recv_hook` / `dbo_maybe_run_recv_hook`：跨线程触发回调，典型场景是等待 all-to-all kernel。
   - `make_ubatch_contexts`：独占式构造两个 `UBatchContext`，需传入两条 CUDA stream、原 `ForwardContext` 以及一个 CPU 线程屏障，并完成所有 event 初始化。

### 已实现的 overlap schedule（原文逐字给出）

```
# Schedule notation legend:
#    S = Shared expert
#    A0 = MLA qkv proj,
#    A1 = Core attn + out proj + MoE gate
#    D = Dispatch
#    C = Combine

# Comp: |-A0₀-A1₀-||-MLP₁-||-S₁-MLP₀-||-S₀-A0₁-A1₁-|
# Comm: |----D₁---||--D₀--||----C₁---||-----C₀-----|
# Order: D₁ send, A0₀, A1₀, D₁ recv, D₀ send, MLP₁, D₀ recv,
#        C₁ send, S₁, MLP₀, C₁ recv, C₀ send, S₀, A0₁, A1₁, C₀ recv.
# MLP_SHARED_OVERLAP = "mlp_shared_overlap"
```

**原文解读**：compute 与 communication 在 4 个时段交错进行——dispatch（D）发送后立刻跑第 0 个 microbatch 的 MLA 投影（A0₀/A1₀），再回来收 D₁，同时并行发出 D₀；以此类推将 MLP、Shared expert (S)、第二次 MLA 与 combine (C) 错位排开。`MLP_SHARED_OVERLAP = "mlp_shared_overlap"` 是对应的 schedule 配置常量。

### 性能/数据相关说明（原文）

原文未给出吞吐量、延迟或加速比的量化性能数据；其性能结论性描述仅一处——**DBO CUDA graph 捕获后可无多线程/CPU 同步开销地重放**。

---

## 【表格解读】

原文**无参数表/性能对比表/配置项表**。仅含一个 ASCII 形式的 schedule 时间线注释块（已在"关键机制与数据"小节按原样呈现并解读）。可视为"伪表格"的内容仅有一项常量：

| 名称 | 取值 |
|---|---|
| `MLP_SHARED_OVERLAP` | `"mlp_shared_overlap"` |

含义：标识"将 MLP 与 shared expert 重叠排布"这一 DBO schedule 模式的常量名。

---

## 【公式解读】

原文**无 LaTeX 公式或伪代码形式公式**。唯一接近"算式/序列"的表述是上一节引用的 overlap schedule 文本（计算时段 vs 通信时段的并列注释），已在"关键机制与数据"按原样保留并解读。

---

## 【关联】

| 上游/模块 | 关系 |
|---|---|
| `GpuModelRunner` | DBO 在其中发起 batch 拆分与跨 DP rank 协调；其修改是 DBO 三大组件之一 |
| `ModularKernel`（`FusedMoEModularKernel` / `FusedMoEPrepareAndFinalizeModular`） | 承载 DBO 的 `dbo_yield` 与 `dbo_maybe_run_recv_hook` 调用点；`FusedMoEPrepareAndFinalizeModular` 通过返回的回调注册到对端 UBatchContext |
| `UBatchWrapper` | 模型包装层，管理线程、UBatchContext 与 CUDA graph；对 GPU Model Runner 透明 |
| `UBatchContext` | `ForwardContext` 包装类；负责两个 UBatch 线程的同步与跨线程 recv hook 触发 |
| `ForwardContext` | 由 `make_ubatch_contexts` 封装，被 DBO 复用为基础同步载体 |
| DeepEP（`deepep_low_latency` / `deepep_high_throughput`） | 当前 DBO **唯一**支持的后端；提供稀疏 all-to-all 内核，由 `dbo_maybe_run_recv_hook` 触发的回调所等待 |
| DP+EP 部署形态 | DBO 生效的前提，需 `--data-parallel-size N`（N>1）+ `--enable-expert-parallel` |
| Full CUDA graphs | 强制约束；DBO 的 CUDA graph 由 `UBatchWrapper` 独占管理，捕获后可独立重放 |

> 原文文末无内部链接可进一步展开（标记为"无"），以上关联来自文档正文中的明确提及。

---

## 【使用方法】

### 启动参数（原文给出）

- `--enable-dbo`：开启 DBO。
- `--data-parallel-size N`：`N > 1`，且与 `--enable-expert-parallel` 联合使用。
- `--enable-expert-parallel`：启用专家并行。
- `--all2all-backend deepep_low_latency`：当负载以解码（decode）请求为主时设置。
- `--all2all-backend deepep_high_throughput`：当负载以预填充（prefill）请求为主时设置。
- 硬件约束：`CUDA_VISIBLE_DEVICES` 中**至少可见两块 GPU**。

### 两个 DBO 阈值配置项（原文给出）

- `--dbo-decode-token-threshold`：纯解码 batch 启用 DBO 所需的最小 token 数。
- `--dbo-prefill-token-threshold`：至少包含一段预填充的 batch 启用 DBO 所需的最小 token 数。

### 完整示例命令（原文逐字给出）

```
vllm serve deepseek-ai/DeepSeek-V2-Lite --trust-remote-code --data-parallel-size 2 --enable-expert-parallel --enable-dbo --all2all-backend deepep_low_latency
```

### 编程/内部 API 启用方式（原文给出）

- `UBatchWrapper.__init__(model, vllm_config, cuda_graph_mode, device)`。
- `UBatchWrapper.forward(...)`：仅根据 `forward_context` 中是否含 `ubatch_slices` 自动决定是否走 DBO 路径。
- `make_ubatch_contexts(cuda_stream_a, cuda_stream_b, forward_contexts, cpu_thread_barrier)`：**唯一**的 `UBatchContext` 构造入口，负责 event 初始化。
- `UBatchContext.dbo_register_recv_hook(...)` / `UBatchContext.dbo_maybe_run_recv_hook()` / `UBatchContext.dbo_yield()`：用于跨线程同步与 all-to-all 等待。

原文**未涉及**具体的吞吐量调优指引、与非 DBO 模式的逐项性能对比数据，亦未给出安装/编译层面的额外说明。
