# 代码仓卡片 · mindspeed-llm

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/Ascend/MindSpeed-LLM.git |
| 分支 / HEAD | `master` @ `06d905186879` (2026-09-01) |
| 最新 tag | `v26.1.0` |
| 版本候选 |
  - git_tag: `v26.1.0`
| 文件数 / md 文档 / 图片 | 2156 / 198 / 140 |
| 语言分布 | {"Python": 1007, "Shell": 624, "Markdown": 198, "YAML": 38, "C++": 2} |
| 备注 | 昇腾LLM分布式训练框架 |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
| `3rdparty` | 文件 |
| `CONTRIBUTING.md` | 文件 |
| `LICENSE` | 文件 |
| `MANIFEST.in` | 文件 |
| `OWNERS` | 文件 |
| `README.md` | 文件 |
| `README_en.md` | 文件 |
| `Third_Party_Open_Source_Software_Notice` | 文件 |
| `ci` | 文件 |
| `configs` | 文件 |
| `convert_ckpt_v2.py` | 文件 |
| `docker/` | 7 |
| `docs/` | 309 |
| `evaluation.py` | 文件 |
| `examples/` | 415 |
| `inference.py` | 文件 |
| `inference_deepseek4.py` | 文件 |
| `inference_fsdp2.py` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 52 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| mcore | 44 | Async Activation Offload、Async Save Torch Dist、CCLoRA、Checkpoint-based Resumable Training、ChunkLoss、Communication over Computation for Computation-Communication Parallelism、Model Script Environment Variables、Long-Sequence Fine-Tuning … |
| fsdp2 | 6 | Full Parameter Reference、Introduction to PyTorch FSDP2 Backend Features、MindSpeed LLM FSDP2 Back-End Low-Precision Training Guide、全量参数说明、PyTorch FSDP2 后端特性介绍、MindSpeed LLM FSDP2后端低精度训练指南 |
| (核心) | 2 | Checkpoint-based Resumable Training、断点续训功能使用介绍 |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

  - Release Notes
  - Version Mapping
  - Product Version Information
  - Related Product Version Mapping
  - Version Compatibility Information
  - Version Usage Notes
  - Update Notes
  - New Features
  - Removed Features
  - API Changes
  - Resolved Issues
  - Known Issues

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| doc | 107 |
| feature | 52 |
| readme | 27 |
| overview | 4 |
| guide | 4 |
| faq | 2 |
| changelog | 2 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/mindspeed-llm/ (198 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
