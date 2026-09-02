# 代码仓卡片 · vllm-ascend

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/gh_mirrors/vl/vllm-ascend.git |
| 分支 / HEAD | `main` @ `f69831343a18` (2026-09-01) |
| 最新 tag | `v0.25.1rc1` |
| 版本候选 |
  - git_tag: `v0.25.1rc1`
| 文件数 / md 文档 / 图片 | 3646 / 261 / 39 |
| 语言分布 | {"Python": 1294, "C/C++ hdr": 791, "C++": 333, "YAML": 262, "Markdown": 261, "Shell": 55, "JavaScript": 2} |
| 备注 | vllm-ascend 镜像 (gh_mirrors) |

## 1. 定位 (LLM)

**vllm-ascend = vLLM 的昇腾 NPU 硬件插件**（gh_mirrors 镜像，上游 vllm-project/vllm-ascend）：
以 vLLM plugin 体系把调度/engine 复用、算子与后端替换为昇腾实现。glm53 上下文中的对照系：
人工汇报版指出「开源 vLLM 在 GLM-5.3 上精度未对齐、0day 未发布」— 本仓即该「开源路径」，
xLLM/uniinfer 路径是其替代（精度对齐 + SOTA 性能）。

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

- `vllm_ascend/`（python 插件包：platform/worker/attention/ops 注册）
- `csrc/`（昇腾自定义算子 — **含 csrc/attention/chunk_kda_fwd/（ChunkKdaFwd 算子 + docs/design.md
  设计文档）：KDA chunked 前向，与 xLLM 仓 chunk_kda 接口、glm5.3-flash KDA 层同一技术线**；
  sparse_attention_score 算子亦有独立设计文档）
- `docs/`（261 篇：guide 62 + feature 7 + tutorials）· `benchmarks/` · `examples/`

| 顶层路径 | 文件数 |
|---|---|
| `AGENTS.md` | 文件 |
| `CLAUDE.md` | 文件 |
| `CMakeLists.txt` | 文件 |
| `CODE_OF_CONDUCT.md` | 文件 |
| `CONTRIBUTING.md` | 文件 |
| `DCO` | 文件 |
| `Dockerfile` | 文件 |
| `Dockerfile.310p` | 文件 |
| `Dockerfile.310p.openEuler` | 文件 |
| `Dockerfile.a3` | 文件 |
| `Dockerfile.a3.openEuler` | 文件 |
| `Dockerfile.a5` | 文件 |
| `Dockerfile.a5.openEuler` | 文件 |
| `Dockerfile.openEuler` | 文件 |
| `LICENSE` | 文件 |
| `README.md` | 文件 |
| `README.zh.md` | 文件 |
| `benchmarks/` | 8 |

## 3. 功能逻辑 · 特性地图 (机械层: 7 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (核心) | 7 | Dynamic Chunked Pipeline Parallel (DeepSeek-V3.1)、Feature Tutorials、PD-Colocated with Mooncake Multi-Instance、Prefill-Decode Disaggregation (DeepSeek)、Prefill-Decode Disaggregation (Qwen2.5-VL)、Ray Distributed (Qwen3-235B-A22B)、Suffix Speculative Decoding |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

- **KDA 算子设计**：csrc/attention/chunk_kda_fwd/docs/design.md（ChunkKdaFwd 设计 —
  delta-rule chunked 前向的昇腾实现，glm5.3-flash 适配的核心算子之一）
- **PD 分离部署**：tutorials/features/pd_disaggregation_mooncake_{single,multi}_node.md
  （DeepSeek 系 / Qwen2.5 的 Mooncake PD 分离实战）
- **动态流水**：dynamic_chunked_pipeline_parallel.md（DCP 流水）
- **投机解码**：suffix_speculative_decoding.md · **AI QoS**：user_guide/feature_guide/Ai_QoS_introduction_en.md
- **Ray 分布式**：tutorials/features/ray.md（Qwen3-235B 实例）

## 5. 版本与演进

- 最新 tag `v0.25.1rc1`；HEAD 2026-09-01（活跃日更）
- 版本线跟随 vLLM 上游 minor 版本（插件兼容性以 vllm 版本为锚）

  - Release Notes
  - v0.23.0 - 2026.08.16
  - Highlights
  - Features
  - Hardware and Operator Support
  - Performance
  - Stability and Bug Fixes
  - Dependencies
  - Deprecation and Configuration Changes
  - Ready to Deprecate
  - Documentation
  - Known Issues

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| doc | 155 |
| guide | 62 |
| readme | 29 |
| feature | 7 |
| api | 2 |
| design | 2 |
| overview | 2 |
| faq | 1 |
| changelog | 1 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/vllm-ascend/ (261 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json

<!-- DEEP_NOTES:BEGIN -->

### 深读笔记索引（机械层 · 72 篇）

- [ChunkKdaFwd 设计](../repo_deep_docs/vllm-ascend/csrc/attention/chunk_kda_fwd/docs/design.md) `design`
- [SparseAttentionScore Operator Design](../repo_deep_docs/vllm-ascend/csrc/attention/sparse_attention_score/docs/sparse_attention_score_design.md) `design`
- [Getting Started](../repo_deep_docs/vllm-ascend/docs/source/getting_started/overview.md) `overview`
- [atlas-200i-pro.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-200i-pro.inc.md) `guide`
- [atlas-300i-duo.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-300i-duo.inc.md) `guide`
- [atlas-950dt.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-950dt.inc.md) `guide`
- [atlas-a2.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-a2.inc.md) `guide`
- [atlas-a3.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-a3.inc.md) `guide`
- [image_download_mirror.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/image_download_mirror.inc.md) `guide`
- [verify_container.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/verify_container.inc.md) `guide`
- [qwen3-0.6b-310p.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/offline/qwen3-0.6b-310p.inc.md) `guide`
- [qwen3-0.6b.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/offline/qwen3-0.6b.inc.md) `guide`
- [qwen3-0.6b-310p.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/online/qwen3-0.6b-310p.inc.md) `guide`
- [qwen3-0.6b.inc](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start/online/qwen3-0.6b.inc.md) `guide`
- [Quick Start](../repo_deep_docs/vllm-ascend/docs/source/getting_started/quick_start.md) `guide`
- [Dynamic Chunked Pipeline Parallel (DeepSeek-V3.1)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/features/dynamic_chunked_pipeline_parallel.md) `feature`
- [PD-Colocated with Mooncake Multi-Instance](../repo_deep_docs/vllm-ascend/docs/source/tutorials/features/pd_colocated_mooncake_multi_instance.md) `feature`
- [Prefill-Decode Disaggregation (DeepSeek)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md) `feature`
- [Prefill-Decode Disaggregation (Qwen2.5-VL)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/features/pd_disaggregation_mooncake_single_node.md) `feature`
- [Ray Distributed (Qwen3-235B-A22B)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/features/ray.md) `feature`
- [Suffix Speculative Decoding](../repo_deep_docs/vllm-ascend/docs/source/tutorials/features/suffix_speculative_decoding.md) `feature`
- [Cohere Transcribe](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Cohere-Transcribe.md) `guide`
- [DeepSeek-R1](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-R1.md) `guide`
- [DeepSeek-V3 & 3.1](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V3.1.md) `guide`
- [DeepSeek-V3.2](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V3.2.md) `guide`
- [DeepSeek-V4-Flash](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V4-Flash.md) `guide`
- [DeepSeek-V4-Pro](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V4-Pro.md) `guide`
- [DeepSeek-OCR-2](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/DeepSeekOCR2.md) `guide`
- [Dots3 Note](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Dots3-Note.md) `guide`
- [GLM-4.5/4.6/4.7](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/GLM4.x.md) `guide`
- [GLM-5.2](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/GLM5.2.md) `guide`
- [GLM-5.3 (Experimental)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/GLM5.3.md) `guide`
- [GLM-5 & GLM-5.1](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/GLM5.md) `guide`
- [Gemma4](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Gemma4.md) `guide`
- [Hunyuan-A13B-Instruct](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Hunyuan-A13B-Instruct.md) `guide`
- [Hy3-preview](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Hy3-preview.md) `guide`
- [Hy4-preview (Experimental)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Hy4-preview.md) `guide`
- [InternVL3.5(38B/241B-A28B)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/InternVL3.5.md) `guide`
- [Kimi-K2-Thinking](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K2-Thinking.md) `guide`
- [Kimi-K2.5](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K2.5.md) `guide`
- [Kimi-K2.6](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K2.6.md) `guide`
- [Kimi-K3](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K3.md) `guide`
- [LLaVA-OneVision-Qwen2-0.5B-OV](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/LLaVA-OneVision-Qwen2-0.5B-OV.md) `guide`
- [MiniMax-M2](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/MiniMax-M2.md) `guide`
- [MiniMax-M3](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/MiniMax-M3.md) `guide`
- [Minitron-8B-Base](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Minitron-8B-Base.md) `guide`
- [Mixtral-8x7B-Instruct-v0.1](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Mixtral-8x7B-Instruct-v0.1.md) `guide`
- [PaddleOCR-VL](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/PaddleOCR-VL.md) `guide`
- [Qwen-VL-Dense(Qwen3-VL-8B/32B)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen-VL-Dense.md) `guide`
- [Qwen2.5-Math-RM-72B](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen2.5-Math-RM-72B.md) `guide`
- [Qwen3-235B-A22B](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-235B-A22B.md) `guide`
- [Qwen3-30B-A3B](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-30B-A3B.md) `guide`
- [Qwen3-ASR-1.7B](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-ASR-1.7B.md) `guide`
- [Qwen3-Coder-30B-A3B](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Coder-30B-A3B.md) `guide`
- [Qwen3-Dense (Qwen3-0.6B/1.7B/4B/8B/14B/32B)](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Dense.md) `guide`
- [Qwen3-Embedding](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Embedding.md) `guide`
- [Qwen3-Next](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Next.md) `guide`
- [Qwen3-Omni-30B-A3B-Thinking](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Omni-30B-A3B-Thinking.md) `guide`
- [Qwen3-Reranker](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Reranker.md) `guide`
- [Qwen3-VL-235B-A22B-Instruct](../repo_deep_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-VL-235B-A22B-Instruct.md) `guide`
- …

<!-- DEEP_NOTES:END -->
