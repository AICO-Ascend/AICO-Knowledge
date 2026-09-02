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

<!-- DEEP_NOTES:BEGIN -->

### 深读笔记索引（机械层 · 103 篇）

- [MindSpeed CI Docker Overview](../repo_deep_docs/mindspeed/ci/OVERVIEW.md) `overview`
- [MindSpeed CI Docker 镜像概述](../repo_deep_docs/mindspeed/ci/OVERVIEW.zh.md) `overview`
- [MindSpeed Core Docker Image Overview](../repo_deep_docs/mindspeed/docker/OVERVIEW.md) `overview`
- [MindSpeed Core Docker 镜像概述](../repo_deep_docs/mindspeed/docker/OVERVIEW.zh.md) `overview`
- [版本说明](../repo_deep_docs/mindspeed/docs/zh/_menu_releasenotes.md) `changelog`
- [MindSpeed 项目目录结构](../repo_deep_docs/mindspeed/docs/zh/dir_structure.md) `overview`
- [Automatic Parallelism](../repo_deep_docs/mindspeed/docs/zh/features/Automatic_Parallelism.md) `feature`
- [分层ZeRO](../repo_deep_docs/mindspeed/docs/zh/features/LayerZeRO.md) `feature`
- [激活函数重计算](../repo_deep_docs/mindspeed/docs/zh/features/activation-function-recompute.md) `feature`
- [AI QoS差异化调度特性说明](../repo_deep_docs/mindspeed/docs/zh/features/aiqos.md) `feature`
- [Alibi 位置编码](../repo_deep_docs/mindspeed/docs/zh/features/alibi.md) `feature`
- [Megatron权重更新通信隐藏](../repo_deep_docs/mindspeed/docs/zh/features/async-ddp-param-gather.md) `feature`
- [Megatron异步DDP](../repo_deep_docs/mindspeed/docs/zh/features/async-ddp.md) `feature`
- [异步日志全归约 (Async Log Allreduce)](../repo_deep_docs/mindspeed/docs/zh/features/async-log-allreduce.md) `feature`
- [开箱优化-大模型并行策略自动搜索 Auto settings 特性说明](../repo_deep_docs/mindspeed/docs/zh/features/auto_settings.md) `feature`
- [PP自动并行算法](../repo_deep_docs/mindspeed/docs/zh/features/automated-pipeline.md) `feature`
- [专家并行动态负载均衡（数参互寻）](../repo_deep_docs/mindspeed/docs/zh/features/balanced_moe.md) `feature`
- [计算通信并行 CoC (Communication Over Computation)](../repo_deep_docs/mindspeed/docs/zh/features/communication-over-computation.md) `feature`
- [compress-activation](../repo_deep_docs/mindspeed/docs/zh/features/compress-tensor.md) `feature`
- [Context Parallelism特性中的KV缓存优化](../repo_deep_docs/mindspeed/docs/zh/features/context_parallelism_kv_cache.md) `feature`
- [conv3d 序列并行](../repo_deep_docs/mindspeed/docs/zh/features/conv3d_sequence_paralle.md) `feature`
- [Megatron 全分片数据并行（Fully Sharded Data Parallel, FSDP）](../repo_deep_docs/mindspeed/docs/zh/features/custom_fsdp.md) `feature`
- [Megatron数据并行](../repo_deep_docs/mindspeed/docs/zh/features/data-parallel.md) `feature`
- [Megatron 分布式权重](../repo_deep_docs/mindspeed/docs/zh/features/dist_ckpt.md) `feature`
- [Megatron分布式优化器](../repo_deep_docs/mindspeed/docs/zh/features/distributed-optimizer.md) `feature`
- [Double Ring Attention长序列并行](../repo_deep_docs/mindspeed/docs/zh/features/double-ring.md) `feature`
- [DualPipeV](../repo_deep_docs/mindspeed/docs/zh/features/dualpipev.md) `feature`
- [支持EOD Reset训练场景](../repo_deep_docs/mindspeed/docs/zh/features/eod-reset.md) `feature`
- [特性总览](../repo_deep_docs/mindspeed/docs/zh/features/feature_list.md) `feature`
- [Flash Attention](../repo_deep_docs/mindspeed/docs/zh/features/flash-attention.md) `feature`
- [FSDP2](../repo_deep_docs/mindspeed/docs/zh/features/fsdp2.md) `feature`
- [fused_ema_adamw 优化器](../repo_deep_docs/mindspeed/docs/zh/features/fused_ema_adamw_optimizer.md) `feature`
- [fusion_attention_v2](../repo_deep_docs/mindspeed/docs/zh/features/fusion-attn-v2.md) `feature`
- [MindSpeed Mask归一实现阐述](../repo_deep_docs/mindspeed/docs/zh/features/generate-mask.md) `feature`
- [Hccl Group Buffer Set](../repo_deep_docs/mindspeed/docs/zh/features/hccl-group-buffer-set.md) `feature`
- [Gloo存档落盘优化](../repo_deep_docs/mindspeed/docs/zh/features/hccl-replace-gloo.md) `feature`
- [混合长序列并行](../repo_deep_docs/mindspeed/docs/zh/features/hybrid-context-parallel.md) `feature`
- [KVAllGather长序列并行](../repo_deep_docs/mindspeed/docs/zh/features/kvallgather-context-parallel.md) `feature`
- [低精度优化器](../repo_deep_docs/mindspeed/docs/zh/features/low-precision-optimizer.md) `feature`
- [Ascend MC2](../repo_deep_docs/mindspeed/docs/zh/features/mc2.md) `feature`
- [Allgather Dispatcher 分支优化](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-allgather-dispatcher.md) `feature`
- [Megatron MoE Allgather Dispatcher分支通信隐藏优化](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-allgather-overlap-comm.md) `feature`
- [Alltoall Dispatcher 分支优化](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-alltoall-dispatcher.md) `feature`
- [Megatron MoE alltoall dispatcher分支通信隐藏优化](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md) `feature`
- [MoE跨microbatch间AllToAll通信掩盖](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md) `feature`
- [Megatron MoE Grouped GEMM (GMM)](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-gmm.md) `feature`
- [Megatron MoE TP拓展EP](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-tp-extend-ep.md) `feature`
- [Megatron MoE alltoall dispatcher分支内存优化](../repo_deep_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-zero-memory.md) `feature`
- [MoE Token Permute and Unpermute 融合优化](../repo_deep_docs/mindspeed/docs/zh/features/moe-token-permute-and-unpermute.md) `feature`
- [MoE负载均衡-专家迁移](../repo_deep_docs/mindspeed/docs/zh/features/moe_expert_load_balance_placeemnt.md) `feature`
- [Multi-head Latent Attention多头潜注意力机制](../repo_deep_docs/mindspeed/docs/zh/features/multi-head-latent-attention.md) `feature`
- [PP支持多参数传递](../repo_deep_docs/mindspeed/docs/zh/features/multi_parameter_pipeline.md) `feature`
- [PP支持多参数传递和动态形状](../repo_deep_docs/mindspeed/docs/zh/features/multi_parameter_pipeline_and_variable_seq_lengths.md) `feature`
- [Muon 优化器](../repo_deep_docs/mindspeed/docs/zh/features/muon-optimizer.md) `feature`
- [MindSpeed FP8 零冗余权重 (Zero-Redundancy Weight) 架构设计](../repo_deep_docs/mindspeed/docs/zh/features/mxfp8/Zero_Redundancy_Weight.md) `feature`
- [Ascend自定义空操作层](../repo_deep_docs/mindspeed/docs/zh/features/noop-layers.md) `feature`
- [Norm重计算](../repo_deep_docs/mindspeed/docs/zh/features/norm-recompute.md) `feature`
- [Ascend MindStudio Training Tools 精度对照](../repo_deep_docs/mindspeed/docs/zh/features/npu_datadump.md) `feature`
- [Ascend 确定性计算](../repo_deep_docs/mindspeed/docs/zh/features/npu_deterministic.md) `feature`
- [matmul_add融合优化](../repo_deep_docs/mindspeed/docs/zh/features/npu_matmul_add.md) `feature`
- …

<!-- DEEP_NOTES:END -->
