# 代码仓卡片 · vllm

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/GitHub_Trending/vl/vllm.git |
| 分支 / HEAD | `main` @ `ec32f669bb55` (2026-09-01) |
| 最新 tag | `v0.28.1rc0` |
| 版本候选 |
  - git_tag: `v0.28.1rc0`
| 文件数 / md 文档 / 图片 | 6813 / 293 / 98 |
| 语言分布 | {"Python": 4401, "YAML": 321, "Rust": 312, "Markdown": 293, "Shell": 139, "CUDA": 97, "C++": 43, "C/C++ hdr": 41, "JavaScript": 7} |
| 备注 | vLLM 上游镜像 (GitHub_Trending) |

## 1. 定位 (LLM)

**vLLM = 业界事实标准的高吞吐 LLM 推理与服务引擎**（GitHub_Trending 镜像仓，上游 vllm-project/vllm）。
核心创新 PagedAttention（本库论文区 arXiv:2309.06180 有深读 + 深读2 页有其 Fig.2 原图：
KV 利用率 20.4%→96.3%）。在本知识库的生态位：vllm-ascend（昇腾插件）与 xLLM（国产推理框架）
共同的上游参照系 — glm53 人工汇报版「开源 vLLM 在 GLM-5.3 上精度未对齐、0day 未发布」
即指本仓。

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

- `vllm/`（python 主包：engine/scheduler/attention/model_executor）· `csrc/`（CUDA kernel）
- `rust/`（部分组件 Rust 化）· `benchmarks/` · `docs/`（293 篇：design 29 + feature 52）
- 硬件插件体系：vllm-ascend / vllm-xpu 等以 plugin 形式外挂（本仓只含上游主线）

| 顶层路径 | 文件数 |
|---|---|
| `AGENTS.md` | 文件 |
| `CLAUDE.md` | 文件 |
| `CMakeLists.txt` | 文件 |
| `CODE_OF_CONDUCT.md` | 文件 |
| `CONTRIBUTING.md` | 文件 |
| `DCO` | 文件 |
| `LICENSE` | 文件 |
| `MANIFEST.in` | 文件 |
| `README.md` | 文件 |
| `RELEASE.md` | 文件 |
| `SECURITY.md` | 文件 |
| `benchmarks/` | 134 |
| `build_rust.sh` | 文件 |
| `build_vllm_ppc64le.sh` | 文件 |
| `cmake` | 文件 |
| `codecov.yml` | 文件 |
| `csrc/` | 309 |
| `docker` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 52 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (核心) | 24 | Automatic Prefix Caching、Batch Invariance、Context Extension、Custom Arguments、Custom Logits Processors、Disaggregated Encoder、Disaggregated Prefilling (experimental)、IndexCache … |
| quantization | 16 | AutoAWQ、b12x Linear and MoE Backends、BitsAndBytes、FP8 ViT Encoder Attention、GGUF、GPTQModel、Intel Quantization Support、FP8 W8A8 … |
| speculative_decoding | 12 | Per-Request Acceptance Metrics、Adaptive Verification、Draft Models、Dynamic Speculative Decoding、EAGLE Draft Models、Hidden State Extraction、MLP Draft Models、MTP (Multi-Token Prediction) … |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

design 文档地图（docs/design/，29 篇，质量为推理框架文档标杆）：
- arch_overview.md（架构总览）· cuda_graphs.md + cuda_graphs_multimodal.md（图模式 —
  与 xllm aclgraph / glm53 图模式优化同一技术族）
- hybrid_kv_cache_manager.md（混合 KV cache — 与 KDA 定长状态 + DSA 稀疏 KV 的
  glm5.3-flash 混合架构直接相关）
- attention_backends.md（注意力后端矩阵）· fused_moe_modular_kernel.md（MoE 融合算子）
- dbo.md（Dual Batch Overlap）· huggingface_integration.md

## 5. 版本与演进

- 最新 tag `v0.28.1rc0`（rc 版本线）；HEAD 2026-09-01（日更活跃）
- 镜像仓与上游同步节奏以 tag 为准（GitHub_Trending 镜像）

  - (无 changelog)

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| doc | 145 |
| readme | 65 |
| feature | 52 |
| design | 29 |
| guide | 1 |
| faq | 1 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/vllm/ (293 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json

<!-- DEEP_NOTES:BEGIN -->

### 深读笔记索引（机械层 · 82 篇）

- [Architecture Overview](../repo_deep_docs/vllm/docs/design/arch_overview.md) `design`
- [Attention Backend Feature Support](../repo_deep_docs/vllm/docs/design/attention_backends.md) `design`
- [CUDA Graphs](../repo_deep_docs/vllm/docs/design/cuda_graphs.md) `design`
- [Vision Encoder (ViT) CUDA Graphs](../repo_deep_docs/vllm/docs/design/cuda_graphs_multimodal.md) `design`
- [CustomOp](../repo_deep_docs/vllm/docs/design/custom_op.md) `design`
- [Dual Batch Overlap](../repo_deep_docs/vllm/docs/design/dbo.md) `design`
- [How to debug the vLLM-torch.compile integration](../repo_deep_docs/vllm/docs/design/debug_vllm_compile.md) `design`
- [Endpoint Plugins](../repo_deep_docs/vllm/docs/design/endpoint_plugins.md) `design`
- [Fused MoE Modular Kernel](../repo_deep_docs/vllm/docs/design/fused_moe_modular_kernel.md) `design`
- [Fusion torch.compile passes](../repo_deep_docs/vllm/docs/design/fusions.md) `design`
- [Integration with Hugging Face](../repo_deep_docs/vllm/docs/design/huggingface_integration.md) `design`
- [Hybrid KV Cache Manager](../repo_deep_docs/vllm/docs/design/hybrid_kv_cache_manager.md) `design`
- [IO Processor Plugins](../repo_deep_docs/vllm/docs/design/io_processor_plugins.md) `design`
- [Logits Processors](../repo_deep_docs/vllm/docs/design/logits_processors.md) `design`
- [LoRA Resolver Plugins](../repo_deep_docs/vllm/docs/design/lora_resolver_plugins.md) `design`
- [Metrics](../repo_deep_docs/vllm/docs/design/metrics.md) `design`
- [Multi-Modal Data Processing](../repo_deep_docs/vllm/docs/design/mm_processing.md) `design`
- [Model Runner V2 Design Document](../repo_deep_docs/vllm/docs/design/model_runner_v2.md) `design`
- [Fused MoE Kernel Features](../repo_deep_docs/vllm/docs/design/moe_kernel_features.md) `design`
- [Python Multiprocessing](../repo_deep_docs/vllm/docs/design/multiprocessing.md) `design`
- [NIXL KV Cache Lease Renewal](../repo_deep_docs/vllm/docs/design/nixl_kv_cache_lease.md) `design`
- [NIXL push-mode KV transfer](../repo_deep_docs/vllm/docs/design/nixl_kv_push_connector.md) `design`
- [Optimization Levels](../repo_deep_docs/vllm/docs/design/optimization_levels.md) `design`
- [Paged Attention](../repo_deep_docs/vllm/docs/design/paged_attention.md) `design`
- [Plugin System](../repo_deep_docs/vllm/docs/design/plugin_system.md) `design`
- [Automatic Prefix Caching](../repo_deep_docs/vllm/docs/design/prefix_caching.md) `design`
- [`torch.compile` integration](../repo_deep_docs/vllm/docs/design/torch_compile.md) `design`
- [torch.compile with Multimodal Encoders](../repo_deep_docs/vllm/docs/design/torch_compile_multimodal.md) `design`
- [vLLM IR: Functional Intermediate Representation](../repo_deep_docs/vllm/docs/design/vllm_ir.md) `design`
- [Automatic Prefix Caching](../repo_deep_docs/vllm/docs/features/automatic_prefix_caching.md) `feature`
- [Batch Invariance](../repo_deep_docs/vllm/docs/features/batch_invariance.md) `feature`
- [Context Extension](../repo_deep_docs/vllm/docs/features/context_extension.md) `feature`
- [Custom Arguments](../repo_deep_docs/vllm/docs/features/custom_arguments.md) `feature`
- [Custom Logits Processors](../repo_deep_docs/vllm/docs/features/custom_logitsprocs.md) `feature`
- [Disaggregated Encoder](../repo_deep_docs/vllm/docs/features/disagg_encoder.md) `feature`
- [Disaggregated Prefilling (experimental)](../repo_deep_docs/vllm/docs/features/disagg_prefill.md) `feature`
- [IndexCache](../repo_deep_docs/vllm/docs/features/index_cache.md) `feature`
- [Interleaved Thinking](../repo_deep_docs/vllm/docs/features/interleaved_thinking.md) `feature`
- [KV Offloading Usage Guide](../repo_deep_docs/vllm/docs/features/kv_offloading_usage.md) `feature`
- [LoRA Adapters](../repo_deep_docs/vllm/docs/features/lora.md) `feature`
- [MooncakeConnector Usage Guide](../repo_deep_docs/vllm/docs/features/mooncake_connector_usage.md) `feature`
- [MooncakeStoreConnector Usage Guide](../repo_deep_docs/vllm/docs/features/mooncake_store_connector_usage.md) `feature`
- [MoRIIOConnector Usage Guide](../repo_deep_docs/vllm/docs/features/moriio_connector_usage.md) `feature`
- [Multimodal Inputs](../repo_deep_docs/vllm/docs/features/multimodal_inputs.md) `feature`
- [NixlConnector Compatibility Matrix](../repo_deep_docs/vllm/docs/features/nixl_connector_compatibility.md) `feature`
- [NixlConnector Usage Guide](../repo_deep_docs/vllm/docs/features/nixl_connector_usage.md) `feature`
- [Per-Request Metrics](../repo_deep_docs/vllm/docs/features/per_request_metrics.md) `feature`
- [Prompt Embedding Inputs](../repo_deep_docs/vllm/docs/features/prompt_embeds.md) `feature`
- [AutoAWQ](../repo_deep_docs/vllm/docs/features/quantization/auto_awq.md) `feature`
- [b12x Linear and MoE Backends](../repo_deep_docs/vllm/docs/features/quantization/b12x.md) `feature`
- [BitsAndBytes](../repo_deep_docs/vllm/docs/features/quantization/bnb.md) `feature`
- [FP8 ViT Encoder Attention](../repo_deep_docs/vllm/docs/features/quantization/fp8_vit_attn.md) `feature`
- [GGUF](../repo_deep_docs/vllm/docs/features/quantization/gguf.md) `feature`
- [GPTQModel](../repo_deep_docs/vllm/docs/features/quantization/gptqmodel.md) `feature`
- [Intel Quantization Support](../repo_deep_docs/vllm/docs/features/quantization/inc.md) `feature`
- [FP8 W8A8](../repo_deep_docs/vllm/docs/features/quantization/llm_compressor/fp8.md) `feature`
- [INT4 W4A16](../repo_deep_docs/vllm/docs/features/quantization/llm_compressor/int4.md) `feature`
- [INT8 W4A8](../repo_deep_docs/vllm/docs/features/quantization/llm_compressor/int8_w4a8.md) `feature`
- [INT8 W8A8](../repo_deep_docs/vllm/docs/features/quantization/llm_compressor/int8_w8a8.md) `feature`
- [NVIDIA Model Optimizer](../repo_deep_docs/vllm/docs/features/quantization/modelopt.md) `feature`
- …

<!-- DEEP_NOTES:END -->
