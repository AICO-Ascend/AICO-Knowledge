# 代码仓卡片 · mindspeed

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/Ascend/MindSpeed.git |
| 分支 / HEAD | `master` @ `4fb7dc00614a` (2026-08-31) |
| 最新 tag | `v26.1.0_core_r0.12.1` |
| 版本候选 |
  - git_tag: `v26.1.0_core_r0.12.1`
| 文件数 / md 文档 / 图片 | 1516 / 149 / 78 |
| 语言分布 | {"Python": 1126, "Markdown": 149, "Shell": 82, "C++": 34, "C/C++ hdr": 14, "YAML": 9, "C": 1} |
| 备注 | 昇腾大模型加速库 |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
| `CONTRIBUTING.md` | 文件 |
| `LICENSE` | 文件 |
| `OWNERS` | 文件 |
| `README.md` | 文件 |
| `Third_Party_Open_Source_Software_Notice` | 文件 |
| `ci/` | 11 |
| `docker/` | 7 |
| `docs/` | 209 |
| `mindspeed/` | 1031 |
| `pre-commit` | 文件 |
| `requirements.txt` | 文件 |
| `setup.py` | 文件 |
| `tests_extend/` | 236 |
| `tools` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 86 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (核心) | 77 | Automatic Parallelism、分层ZeRO、激活函数重计算、AI QoS差异化调度特性说明、Alibi 位置编码、Megatron权重更新通信隐藏、Megatron异步DDP、异步日志全归约 (Async Log Allreduce) … |
| megatron_moe | 8 | Allgather Dispatcher 分支优化、Megatron MoE Allgather Dispatcher分支通信隐藏优化、Alltoall Dispatcher 分支优化、Megatron MoE alltoall dispatcher分支通信隐藏优化、MoE跨microbatch间AllToAll通信掩盖、Megatron MoE Grouped GEMM (GMM)、Megatron MoE TP拓展EP、Megatron MoE alltoall dispatcher分支内存优化 |
| mxfp8 | 1 | MindSpeed FP8 零冗余权重 (Zero-Redundancy Weight) 架构设计 |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

  - 版本说明

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| feature | 86 |
| doc | 30 |
| readme | 14 |
| guide | 8 |
| overview | 7 |
| changelog | 2 |
| faq | 1 |
| api | 1 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/mindspeed/ (149 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
