# NixlConnector Compatibility Matrix

> 仓 `vllm` · 路径 `docs/features/nixl_connector_compatibility.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/nixl_connector_compatibility.md

# vLLM NixlConnector 兼容性矩阵文档深度解读

---

## 【定位】

本文档是 vLLM **NixlConnector** 在**分离式 Prefill/Decode (PD 分离)** 推理场景下的**特性兼容性参考手册**,回答的核心问题是:"给定一种模型架构 + 一种 vLLM 能力(如 speculative decoding、异构 TP、跨层块、SWA、CPU host buffer 卸载、异构 block size),能否在 NIXL 传输层之上正确、稳定地完成 KV cache 的 P↔D 跨实例搬运?"

它本质是一张"架构 × 能力"的二维可行性表,并附带 P/D 实例之间的**握手兼容性规则**和**KV cache 布局/量化**约束。

---

## 【技术要点】

1. **PD 分离传输协议不兼容原则**:NIXL 的 push (WRITE) connector 与 pull (READ) connector 使用**互不兼容的传输协议**,绝对不能配对;此约束在握手 (handshake) 阶段通过 **compatibility hash** 校验强制执行。

2. **握手兼容性哈希 (compatibility hash) 默认开启**,P 与 D 实例必须在以下维度一致: **vLLM 版本、NIXL connector 版本、模型架构/dtype/KV heads 数/head size/隐藏层数、attention backend、cache_dtype、EAGLE/MTP 推测方法与 draft 模型配置、NIXL transfer mode**。可通过 `--kv-transfer-config '{"kv_connector_extra_config": {"enforce_handshake_compat": false}}'` 关闭(原文警告:"at your own risk")。

3. **默认 KV cache 布局为 `LBHNC`**(head-major,原文注 formerly `HND`),用于非 MLA 模型的最优传输性能。`LBNHC`(token-major, formerly `NHD`)也支持但**不支持异构 TP 的 head splitting**。跨布局 `LBHNC ↔ LBNHC` 的实验性 permute 通过 `--kv-transfer-config '{"enable_permute_local_kv": true}'` 启用,且**不兼容 HMA**。

4. **跨层块 (cross-layer blocks) 优化依赖 `BLHNC` 布局**,需通过环境变量 `VLLM_KV_CACHE_LAYOUT=BLHNC` 设置(见脚注 2)。

5. **异构 block size 仅支持 P block size < D block size,且仅在无需 HMA 的非 hybrid 模型上可用**;块 ID 自动重映射(block IDs are remapped automatically)。

6. **MLA 模型在异构 TP 下不进行 head splitting**:因为 MLA 的 KV cache 在各 TP worker 间**复制**(replicated),P TP > D TP 时只执行一次读操作(冗余 rank 被跳过);D TP > P TP 也支持(脚注 4)。

7. **混合 SSM/Mamba (Hybrid) 模型在异构 TP 上是 🚧 状态**(脚注 5),需**强制 homogeneous TP**(`P TP == D TP`),因为 Mamba 层尚未支持异构 TP;且因 HMA 需求,**不同 remote block size 不支持**(脚注 6)。

8. **量化 KV cache 的三类支持度**:
   - **Static quantization**(从 checkpoint 加载 scale):✅ 每实例独立从 checkpoint 加载
   - **Dynamic quantization**(运行时算 scale):❌ **不支持**,per-block scale 不会随 KV cache 一起传输
   - **Packed-layout scales**(scale 与权重内联存储):✅ 与 KV cache 块一起传输
   - 共同约束:**P/D 必须用相同 `cache_dtype`**,否则握手哈希校验失败。

---

## 【关键机制与数据】

### 工作原理:PD 分离 + NIXL 握手流程
- **Prefill 实例** 完成 prompt 的 prefill 计算 → 生成 KV cache → 通过 NIXL 写入到 Decode 实例 → **Decode 实例**接管后续 token 生成。
- 两者通过**握手 (handshake)** 建立连接,默认校验 compatibility hash;任何关键配置不一致都会**直接拒绝连接**。

### 普遍可用特性(原文:"universally supported features")
以下特性在**所有模型架构 + NixlConnector PD 分离**组合下都可用(原文用 `|` 分隔罗列):
- **Chunked Prefill**(`../configuration/optimization.md#chunked-prefill`)
- **APC / Prefix Caching**(`automatic_prefix_caching.md`)
- **Data Parallel**(`../serving/data_parallel_deployment.md`)
- **CUDA graph**
- **Logprobs**
- **Prompt Logprobs**
- **Prompt Embeds**(`prompt_embeds.md`)
- **Multiple NIXL backends (UCX, GDS, LIBFABRIC, etc.)**

### 数据流与传输模式
- **NIXL transfer mode** 分为 **push (WRITE)** 与 **pull (READ)**,两者协议**互不兼容**(必须成对正确)。
- **KV cache 布局影响传输效率**:head-major (`LBHNC`) 是默认最优布局。
- **MLA 的传输特性**:KV cache 在 TP worker 间复制,异构 TP 下只有一次读操作(冗余 rank skipped)。

### 性能/参数相关原文事实
- 原文未提供具体数字(吞吐量、延迟、带宽),仅提供**支持/不支持/部分支持**的布尔矩阵和脚注说明。
- 兼容性状态随时变化,作者指引到 [NIXL connector roadmap issue #33702](https://github.com/vllm-project/vllm/issues/33702) 跟踪。

---

## 【表格解读】

### 原文表格:Model Architecture x Capability(逐字还原)

| Model type | Basic PD | Spec Decode | Hetero TP | Cross-layer blocks | SWA | Host buffer | Hetero block size |
|---|---|---|---|---|---|---|---|
| Dense Transformers | ✅ | ✅¹ | ✅ | ✅² | ✅ | ✅ | 🟠³ |
| MLA (e.g. DeepSeek-V2/V3) | ✅ | ✅¹ | 🟠⁴ | ✅² | ✅ | ✅ | 🟠³ |
| Sparse MLA (e.g. DeepSeek-V3.2) | ✅ | ✅¹ | 🟠⁴ | ✅² | ✅ | ✅ | 🟠³ |
| Hybrid SSM / Mamba | ✅ | ❔ | 🚧⁵ | ❌ | ✅ | ✅ | ❌⁶ |
| MoE | ✅ | ✅¹ | ✅ | ✅² | ✅ | ✅ | 🟠³ |
| Multimodal | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ |
| Encoder-Decoder | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**列定义**(原文 `<abbr>` 标题):
- **Basic PD**:基础 Prefill/Decode 分离
- **Spec Decode**:Speculative Decoding
- **Hetero TP**:异构 Tensor Parallelism(`P TP != D TP`)
- **Cross-layer blocks**:跨层块优化
- **SWA**:Sliding Window Attention
- **Host buffer**:CPU host buffer 卸载(如 TPU 场景)
- **Hetero block size**:P 与 D 使用不同 block size

**逐行解读**:

1. **Dense Transformers**:除 Hetero block size 外全部 ✅。这是兼容性最广的基线;唯一限制是异构 block size 仅"部分支持"且要求 P block size < D block size 且非 hybrid 模型。

2. **MLA (DeepSeek-V2/V3)**:Hetero TP 标记为 🟠——能工作但**无 head splitting**;Hetero block size 同上 🟠。

3. **Sparse MLA (DeepSeek-V3.2)**:与 MLA 行几乎完全一致,说明 vLLM 把两类 MLA 都按"KV cache 在 TP 间复制"的特性统一处理。

4. **Hybrid SSM / Mamba**:这是兼容性**最受限**的一行——Spec Decode ❔(未验证)、Hetero TP 🚧(进行中)、Cross-layer blocks ❌、Hetero block size ❌。原因是 Mamba 层不支持异构 TP,且需要 HMA(脚注 5、6)。Basic PD、SWA、Host buffer 三项 ✅。

5. **MoE**:与 Dense Transformers 几乎一致——所有主流能力 ✅,仅 Hetero block size 🟠。

6. **Multimodal**:几乎全 ❔,说明在 NIXL + PD 分离场景下**尚未充分验证**多模态模型。

7. **Encoder-Decoder**:**全 ❌**,即 PD 分离**根本不支持** encoder-decoder 架构(在 NIXL connector 上下文下)。

---

## 【公式解读】

**原文无公式**。

文档未包含 LaTeX 数学公式或伪代码形式的定量表达式。涉及的"配置项"均为命令行参数和 YAML/JSON 字段(如 `--kv-transfer-config '{"kv_connector_extra_config": {"enforce_handshake_compat": false}}'`、`VLLM_KV_CACHE_LAYOUT=BLHNC`、`--kv-transfer-config '{"enable_permute_local_kv": true}'`),这些已在"技术要点"中按原文保留。

---

## 【关联】

本文档是 vLLm PD 分离生态中的一个**专门描述"哪些组合能跑通"** 的参考页,处于以下关系网中:

### 上游(背景/概述)
- **[Disaggregated Prefilling](disagg_prefill.md)**:PD 分离的概念性介绍,本文是其能力兼容性细化。
- **[NixlConnector Usage Guide](nixl_connector_usage.md)**:通用使用说明,本文聚焦"哪些配置组合合法"。

### 同级被引用的特性(均在"universally supported"清单内)
- **[Chunked Prefill](../configuration/optimization.md#chunked-prefill)**:在 PD 分离下普适可用,意味着 prefill 阶段可分块处理而不破坏 NIXL 传输兼容性。
- **[APC / Prefix Caching](automatic_prefix_caching.md)**:PD 分离下仍能工作,跨实例共享前缀 KV cache。
- **[Data Parallel](../serving/data_parallel_deployment.md)**:数据并行部署与 PD 分离正交兼容。
- **[Prompt Embeds](prompt_embeds.md)**:支持以 embedding 形式传入 prompt 而非原始文本。
- **[Quantized KV cache](quantization/quantized_kvcache.md)**:本文最后一节展开说明其与 NIXL 的兼容约束(static/dynamic/packed-layout 三类)。

### 依赖的外部追踪
- **[NIXL connector roadmap (GitHub issue #33702)](https://github.com/vllm-project/vllm/issues/33702)**:🟠/❌ 标记的条目可能链接到具体跟踪 issue,本文持续跟进上游演进。

### 跨章节逻辑链
```
disagg_prefill.md (概念) 
   └── nixl_connector_compatibility.md (本文:哪些组合可行) 
          ├── nixl_connector_usage.md (如何使用) 
          ├── optimization.md#chunked-prefill (通用特性) 
          ├── automatic_prefix_caching.md (通用特性) 
          ├── data_parallel_deployment.md (部署模式) 
          ├── prompt_embeds.md (输入形态) 
          └── quantization/quantized_kvcache.md (量化约束)
```

---

## 【使用方法】

### 1. 查阅兼容性(无需配置)
直接阅读本文表格,确认目标"模型架构 × 能力"组合的 ✅/🟠/❌/❔/🚧 状态;🟠 与 ❌ 可点击进入对应 tracking issue。

### 2. 启用 cross-layer blocks(原文命令)
设置环境变量:
```bash
VLLM_KV_CACHE_LAYOUT=BLHNC
```

### 3. 启用实验性跨布局 permute(原文命令)
```bash
--kv-transfer-config '{"enable_permute_local_kv": true}'
```
(注意:**不支持 HMA**)

### 4. 关闭握手兼容性哈希校验(原文警告)
```bash
--kv-transfer-config '{"kv_connector_extra_config": {"enforce_handshake_compat": false}}'
```
⚠️ **at your own risk** —— 关闭后 P/D 实例可能因版本/配置不一致导致运行时崩溃或数据损坏。

### 5. 量化 KV cache 配置约束
- **Static quantization**:每实例独立加载 scale,无需额外配置,但 P/D **必须用相同的 `cache_dtype`**。
- **Dynamic quantization**:**不支持**,即使双方都开也会在握手哈希校验时被拒。
- **Packed-layout scales**:无需额外配置,scale 自动随 KV cache 块传输。

### 6. 通用 NIXL 后端选择
原文未给出具体启用命令,仅列出支持的 backend:**UCX、GDS、LIBFABRIC 等**,具体切换方式详见 [NixlConnector Usage Guide](nixl_connector_usage.md)。

### 7. 详细使用方式
原文明确指出通用使用说明请跳转 **[nixl_connector_usage.md](nixl_connector_usage.md)**,本文不重复部署/启动指令。
