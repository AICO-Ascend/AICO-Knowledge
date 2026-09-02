# Release Notes

> 仓 `vllm-ascend` · 路径 `docs/source/user_guide/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/user_guide/release_notes.md

# vllm-ascend v0.23.0 Release Notes 深度解读

## 【定位】

本文档是 vLLM Ascend v0.23.0（2026.08.16）正式版的发布说明（Release Notes），汇总了自上一正式版 v0.18.0 以来、经过 v0.19.1rc1 → v0.20.2rc1 → v0.21.0rc1 → v0.22.1rc1 → v0.23.0rc1 共五个开发周期累积的所有用户面向变更，定位是为 Ascend NPU 用户提供该版本新能力、新模型/硬件支持、算子与性能优化的清单与启用说明。

---

## 【技术要点】

1. **Ascend 950 + DeepSeek V4 端到端支持**：首次在 Ascend 950 上落地 DeepSeek V4 全链路能力，集成 DSA attention、MTP（Multi-Token Prediction）、piecewise graph execution、分布式推理、sparse attention、CPU binding，以及 MXFP 量化和通信路径（PR #9757/#9935/#10236/#11014）。
2. **默认启用的图模式 `FULL_AND_PIECEWISE`**：新增的图执行模式作为默认配置，**无需任何手动配置**即生效；同期新增 DFlash `FULL_DECODE_ONLY`、zero-bubble async scheduling、P-Eagle、PARD，并扩展 MTP/Eagle3 支持（PR #7640/#8118/#9572/#10042/#10566）。
3. **长上下文与 P/D 分离部署的上下文并行**：SFA DCP 引入 replicated indexer、compact KV gather、C8 支持和 device-side metadata 路径，专门面向长上下文与 Prefill/Decode 分离部署场景（PR #9638/#9809/#11819/#11871/#11981）。
4. **KV-cache 全生命周期管理（AscendStore）**：在 AscendStore 中加入 hybrid/Mamba attention prefix caching，以及**覆盖所有后端**的 CPU 和 SSD offload（PR #8743/#9533/#9731/#10393）。
5. **模型与硬件矩阵大幅扩展**：覆盖 GLM-5.2、GLM-4.7-Flash、Qwen3.5/Qwen3.6、Qwen3-ASR、Qwen3-Omni、Bailing MoE、Gemma4、Step3、MiniMax 2.x 等模型；硬件覆盖 A2、A3、Ascend 950、Atlas 300I DUO；其中 **GLM-5.2 在 Atlas 800 A3 上支持最长 1M tokens 的长序列推理**。
6. **底层算子与 Python 3.12**：新增/优化 recurrent GDN、causal Conv1D、sparse-attention、LightningIndexer、compressor、fused quantization 算子；release 镜像迁移到 **Python 3.12**（PR #9558）。
7. **C8 INT8 KV cache 与 W8A8FP8/W4A16 MXFP 量化**：C8 INT8 KV cache 扩展到 sparse-attention 路径（含 packed layouts 和 DCP replicated indexer）；为 Ascend 950 新增 W8A8FP8 与 W4A16 MXFP 量化路径（PR #10236/#11014/#11846/#11871）。

---

## 【关键机制与数据】

### 工作原理 / 优化机制（原文逐条摘自 "Performance" 章节）

> Performance 章节原文明示："Unless stated otherwise, these optimizations are selected automatically for the targeted path and need no additional configuration."（除特别声明外，这些优化均针对目标路径自动选中，无需额外配置。）

| 优化项 | 工作机制 / 数据流 | 是否需手动配置 |
|---|---|---|
| A2/A3 attention 路径替换 `npu_fusion_attention` → `_npu_flash_attention_unpad` | 用更高效的 unpad flash attention 内核替换旧的融合 attention 内核 | 自动选中，无需配置（#8671） |
| MLA prefill + PCP 跳过尾部未用 KV token 的投影 | 在带 PCP 的 MLA prefill 阶段，省略对未使用 tail KV 的投影计算 | 需 `--prefill-context-parallel-size`（#8787） |
| 异步调度下减少调度器下发气泡（issuance bubbles） | 在异步调度下优化调度器发布节奏，减少等待气泡 | 需 `--async-scheduling`（#8766） |
| 异步投机解码的 zero-bubble 调度 | 在异步调度 + 投机解码组合下实现零气泡 | 需 `--async-scheduling` + 投机解码配置（#7640） |
| KV-cache CPU offload 使用 `aclrtMemcpyBatchAsync` 批量拷贝 | 利用 ACLRT 批量异步内存拷贝接口，把 KV cache 卸载到 CPU 的拷贝由多次同步合并为一次批量异步 | 在已配置 KV cache CPU offload 的路径内**自动生效**（#7819） |
| PCP/DCP KV-cache all-gather 流量削减 | 在通信之前先按需筛选所需 KV 块再发起 all-gather，降低通信量 | 需 `--prefill-context-parallel-size` 或 `--decode-context-parallel-size`（#8050） |
| `split_qkv_tp_rmsnorm_rope` 内核优化（量化模型路径） | 优化 QKV 切分 + TP RMSNorm + RoPE 的融合内核，针对量化模型路径 | 自动内核选择，无需配置（#8059/#9830） |
| 去除 Qwen3-Next 与 Qwen3.5 路径中的 prefill 主机-设备同步 | 在特定模型路径中省去 host-device sync 点，缩短 prefill 延迟 | 对这些模型**自动生效**（#7967） |
| SFA prefill 在 PCP/DCP 下减少 KV all-gather 通信 | 在上下文并行模式下对 SFA prefill 的 KV all-gather 做通信量优化 | 启用对应上下文并行模式后自动生效（#8043） |
| repetition/frequency/presence penalty 的 Triton penalty kernel | 用 Triton 内核实现惩罚项采样 | 当请求声明使用 penalty 时**自动选中**（#7569） |
| Model Runner V2 的 temperature / top-k / min-p / bad-word Triton 内核 | 用 Triton 内核加速 sampling 阶段相关算子 | 对 Model Runner V2 采样自动选中（#8083/#8243/#7767/#8030） |

> **性能数据**：原文 Performance 章节未给出任何量化的性能数字（如延迟百分比、吞吐数字等），所有项均为机制层面的描述。

### Feature 与 Highlight 中的关键数据流机制

- **HCCL weight transfer for RL workloads**：在强化学习工作负载下用 HCCL 进行权重传输（#9152）。
- **D2D NetLoader for speculative draft models**：device-to-device 网络加载支持投机解码 draft 模型（#9893）。
- **Model Runner V2**：扩展出初始的 MoE 与 Eagle 支持（#7885/#7922）。
- **EPLB（Expert Parallel Load Balancer）**：增加可观测性与动态负载均衡样例（#9536/#10627）。
- **多模态 DFlash、Qwen VL/MoE 的 FlashComm、PCP-aware 多模态推理**（#7486/#7897/#8038/#9340）。

---

## 【表格解读】

**原文无表格。** 原文所有信息以分级标题（Highlights / Features / Hardware and Operator Support / Performance）+ 项目符号列表 + 行末 PR 链接形式组织，未出现 markdown / HTML 表格。

---

## 【公式解读】

**原文无公式。** 全文未出现 LaTeX、伪代码或任何数学公式表述。

---

## 【关联】

### 版本演进脉络
- **上一正式版**：v0.18.0（本文档的基线对比起点）
- **本版对齐的上游 vLLM**：[v0.23.0](https://docs.vllm.ai/projects/ascend/en/v0.23.0/)
- **覆盖的开发周期**：
  - v0.19.1rc1
  - v0.20.2rc1
  - v0.21.0rc1
  - v0.22.1rc1
  - v0.23.0rc1
- **延迟合并（† 标记）**：标记 † 的 PR（如 #13262）在 v0.23.0rc1 之后才被合入 v0.23.0 release 分支。

### 模块 / 子系统内部关联
| 章节 | 与其他章节的联动点 |
|---|---|
| Highlights → Model and hardware coverage | 与 "Hardware and Operator Support" 中的 Atlas 300I DUO 扩展条目互为表里（同一硬件但侧重点不同） |
| Highlights → KV-cache lifecycle and offload | 与 Performance 中 "Batched KV-cache offload with `aclrtMemcpyBatchAsync`" (#7819) 直接对应；AscendStore 是 offload 的承载实体 |
| Highlights → Context parallelism and sparse attention | 与 Performance 中 PCP/DCP 相关的多项通信优化（#8050/#8043）形成 "特性 + 性能" 双层描述 |
| Highlights → Graph and speculative execution | 与 Performance 中 zero-bubble async scheduling (#7640)、Model Runner V2 各项 Triton 内核联动 |
| Features → C8 / MXFP 量化 | 与 Highlights 中 Ascend 950 + DeepSeek V4 的 MXFP 路径对应 |
| Hardware and Operator Support → Atlas 300I DUO | 与 Highlights 中 Atlas 300I DUO 模型矩阵对应 |

### 上下游关系
- **上游**：vLLM v0.23.0（官方文档 `https://docs.vllm.ai/projects/ascend/en/v0.23.0/`）
- **底层硬件**：Ascend A2 / A3 / Ascend 950 / Atlas 300I DUO / Atlas 800 A3
- **下游用户**：运行 DeepSeek V4、Qwen3.x 系列、GLM 系列、MiniMax 等模型 + Ascend NPU 的推理部署方

---

## 【使用方法】

以下为原文中**显式给出**的启用方式 / 配置项 / 命令：

| 启用项 | 命令 / 配置 | 出处 PR |
|---|---|---|
| Prefill Context Parallelism (PCP) | `--prefill-context-parallel-size` | #8787, #8050, #8043 |
| Decode Context Parallelism (DCP) | `--decode-context-parallel-size` | #8050, #8043 |
| 异步调度（async scheduling） | `--async-scheduling` | #8766 |
| 异步投机解码的 zero-bubble 调度 | `--async-scheduling` + 投机解码配置 | #7640 |
| KV cache CPU offload | 按官方文档配置 KV cache CPU offload（在路径内自动启用 `aclrtMemcpyBatchAsync` 批量拷贝） | #7819 |
| `FULL_AND_PIECEWISE` 图模式 | **默认启用**，无需手动配置 | Highlights |
| 其他大部分性能优化（`_npu_flash_attention_unpad`、Triton penalty kernel、Model Runner V2 各类采样内核等） | **自动选中**，无需手动配置 | 各项 |

> 其余功能（HCCL 权重传输、D2D NetLoader、Atlas 300I DUO 上的新模型支持、Python 3.12 镜像等）的具体配置 / 命令，**原文未涉及**，需参考官方文档 `https://docs.vllm.ai/projects/ascend/en/v0.23.0/` 或对应 PR 链接。
