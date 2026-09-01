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

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

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

## 5. 版本与演进

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
