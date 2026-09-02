# graph_mode

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/graph_mode.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/graph_mode.md

# Graph Mode 文档深度解读

## 【定位】

这篇文档描述 xLLM 引擎的 **Graph Mode（图模式）** 能力：通过预捕获（capture）计算图并在后续推理中重放（replay），减少 CPU 侧的调度与启动开销、压缩设备侧"气泡"（bubble），从而提升 LLM 推理性能；并说明该能力在不同硬件后端（ACLGraph / CudaGraph / MLUGraph）下的功能开关、模型支持矩阵与实测收益。

---

## 【技术要点】

1. **动态维度参数化**：把 `batch_size`、`kv_seq_lens`、`q_seq_lens`、`block_table_size` 等关键动态维度（**除 `num_tokens` 以外**）作为整图输入参数传入；内存分配与 kernel 配置阶段用这些参数算"实际所需值"，图启动阶段再把真实 stride 喂给 kernel，从而让一张图适配多种请求形状。

2. **Piecewise Graph（分段图）**：当个别算子不支持 graph 导致 *break graph*（整图捕获失败）时，对 break 点之后的各 piece **分段捕获** 多个子图，使原本无法整图捕获的场景（原文标注典型为 *prefill、chunked_prefill*）仍能拿到部分 graph mode 收益。

3. **多 shape 复用的显存池**：不同 shape 的 graph capture **不独占独立显存**，而是分配不同虚拟地址空间并共享同一组底层物理内存；输入 tensor 通过 **持久化 buffer + slice** 方式复用，从而在大量形状共存的 decode 场景中控制显存占用。

4. **调度优化目标**：在 CPU 侧一次性提交大任务，让设备侧内部流式执行小 kernel —— 主目标是 **降低启动延迟** 与 **压缩设备气泡**，而非改变算子语义。

5. **控制面（gflags）开关**：通过 `enable_graph` / `enable_prefill_piecewise_graph` / `enable_graph_mode_decode_no_padding` / `max_tokens_for_graph_mode` 等 flag 控制，**默认实现已嵌入引擎内部**，调用方通常无需手写捕获逻辑。

6. **硬件后端矩阵化覆盖**：同一套上层概念分别落到 ACLGraph / CudaGraph / MLUGraph 三种后端实现，模型×后端的可用性见下方表格。

---

## 【关键机制与数据】

**工作原理（原文语义复述）**：

- **捕获阶段**：在一次前向执行中"录制"整张计算图（含 kernel 启动顺序、输入/输出张量与 stride），把动态维度提炼为图参数。
- **分配阶段**：基于动态参数计算实际 buffer 形状，多个 shape 共享底层物理显存，仅用不同虚拟地址 / slice 区分。
- **启动阶段**：把运行时真实参数（`batch_size`、`kv_seq_lens`、`q_seq_lens`、`block_table_size` 等；`num_tokens` 不属于图参数）传入图入口，由图内部以正确 stride 访问持久化 buffer。
- **重放阶段**：CPU 不再逐 kernel 排队下发，而是触发一次图重放，由设备内部流式执行多个小 kernel，从而把"CPU 调度 + 设备排队"这段开销压缩成一次提交。

**性能数据（原文有据）**：

- **原文**：开启 Graph Mode 后，在 **Qwen3-0.6B** 和 **Qwen3-1.7B** 上，decode 阶段吞吐 **提升约 8%–10%**。
- 其它模型 / 阶段 / batch 量级 / 硬件后端的吞吐数字原文未给出（不臆造）。

**适用阶段与边界（原文有据）**：

- 完整整图 Graph Mode 主要面向 **decode** 阶段（`enable_graph` 注释明确为"decode 阶段的 Graph Mode 基础能力"）。
- **prefill / chunked_prefill** 场景因常有 break graph，使用 **Piecewise Graph**（`enable_prefill_piecewise_graph`）作为兜底收益手段。
- `max_tokens_for_graph_mode` 用于限定 Graph Mode 覆盖的最大 token 数，`0` 表示不限制；超限请求按非 graph 路径走。

---

## 【表格解读】

**逐字还原（原文表格）**：

| 模型 | ACLGraph | CudaGraph | MLUGraph |
|------|----------|-----------|----------|
| Qwen3/Qwen3-MoE | ✅ | ✅ | ✅ |
| DeepseekV3.2 | ✅ |  | ✅ |
| GLM4.5/4.6/4.7 | ✅ |  |  |
| Qwen2.5-VL |  |  | ✅ |
| Qwen3-VL/Qwen3-VL-MoE | ✅ |  |  |
| GLM4V | ✅ |  |  |
| GLM4V-MoE | ✅ |  |  |

> 注：原文表内"未支持"用空白表示，未列出其它模型。

**逐行解读**：

- **Qwen3 / Qwen3-MoE**：唯一在三种后端（ACLGraph / CudaGraph / MLUGraph）全部支持的模型，也是性能章节中 8%–10% decode 提升的实测对象，定位为 Graph Mode 的 **旗舰参考路径**。
- **DeepseekV3.2**：仅支持 ACLGraph 与 MLUGraph，**不支持 CudaGraph**；暗示在该模型上，NVIDIA GPU 后端走的是非 graph 路径或使用其它优化手段。
- **GLM4.5 / 4.6 / 4.7**：仅支持 ACLGraph，CudaGraph 与 MLUGraph 留空；属于 ACL 后端生态的覆盖范围。
- **Qwen2.5-VL**：仅支持 **MLUGraph**，是表中唯一仅在 MLUGraph 上可用的模型，区别于同家族的 Qwen3-VL。
- **Qwen3-VL / Qwen3-VL-MoE**：仅支持 ACLGraph，与纯文本 Qwen3 的"三端齐全"形成对比，说明多模态模型在 CudaGraph / MLUGraph 上尚未具备条件。
- **GLM4V**：仅 ACLGraph 支持。
- **GLM4V-MoE**：仅 ACLGraph 支持，与 GLM4V 一致。

**横向归纳**：

- **列维度（后端）**：ACLGraph 覆盖最广（6/7 行打勾），CudaGraph 仅覆盖 Qwen3 系列（1 行），MLUGraph 覆盖 Qwen3 系列 + DeepseekV3.2 + Qwen2.5-VL（3 行）。
- **行维度（模型族）**：Qwen3 文本系列成熟度最高；MoE 类（Qwen3-MoE、GLM4V-MoE）至少可在 ACLGraph 上获得 Graph Mode 收益；多模态 VL 系列整体覆盖较稀疏。

---

## 【公式解读】

**原文无公式**（无 LaTeX 表达式、无伪代码算法；动态维度参数化、Piecewise 切分、显存池共享等机制均以自然语言描述）。

---

## 【关联】

依据文末"相关文档"与正文引用，本文档在仓库中处于以下关系网中：

- **上游 / 设计原理**：*[Graph Mode 设计文档](/zh/design/graph_mode_design/)* — 文末"相关文档"明示，ACL Graph / CUDA Graph 基本原理、动态维度参数化、Piecewise Graph、多 shape 复用内存方案的 *详细设计* 在该文档中展开；本文是其"功能侧 + 使用侧"的精简视图。
- **横向 / 参数索引**：*[CLI 参数说明](/zh/cli_reference/)* — 正文"使用方式"末尾指向该链接，承接本文列出的 `enable_graph`、`enable_prefill_piecewise_graph`、`enable_graph_mode_decode_no_padding`、`max_tokens_for_graph_mode` 等 gflags 的 *完整定义*（取值范围、默认值、冲突策略等）。
- **承载引擎**：xLLM 推理引擎本体 — Graph Mode 不是独立模块，而是嵌入引擎内部的优化能力；因此它与解码调度、prefill 流水线、KV cache block table 分配等模块耦合（如 `block_table_size` 被显式列为图参数）。
- **硬件后端**：ACLGraph ↔ 昇腾 ACL 后端、CudaGraph ↔ NVIDIA CUDA 后端、MLUGraph ↔ 寒武纪 MLU 后端 — 文档通过"模型支持表"显式列出三者的覆盖差异。

---

## 【使用方法】

> 以下开关均为 gflags / 命令行参数，在启动 xLLM 引擎时传入；原文未给出默认值，仅给出示例组合。

**最小配置（仅开启 decode Graph Mode）**：

```shell
--enable_graph=true
```

**典型组合（decode Graph + prefill Piecewise Graph，并限定 token 上限为 2048）**：

```shell
--enable_graph=true \
--enable_prefill_piecewise_graph=true \
--max_tokens_for_graph_mode=2048
```

**decode 阶段按真实 `num_tokens` 建图（不做 padding shape）**：

```shell
--enable_graph=true \
--enable_graph_mode_decode_no_padding=true
```

**开关语义对照表（原文有据）**：

| 参数 | 作用（原文） |
|------|--------------|
| `enable_graph` | 开启 decode 阶段的 Graph Mode 基础能力 |
| `enable_prefill_piecewise_graph` | 开启 prefill 阶段的 Piecewise Graph |
| `enable_graph_mode_decode_no_padding` | decode 阶段按实际 `num_tokens` 建图，而非按 padding 后的 shape |
| `max_tokens_for_graph_mode` | 限制 Graph Mode 覆盖的最大 token 数；`0` 表示不限制 |

更完整说明（含默认值、类型、范围）见原文指向的 [CLI 参数说明](/zh/cli_reference/)。
