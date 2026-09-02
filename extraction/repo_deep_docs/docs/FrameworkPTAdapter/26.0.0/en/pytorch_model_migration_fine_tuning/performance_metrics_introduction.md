# Introduction to Performance Metrics

> 仓 `docs` · 路径 `FrameworkPTAdapter/26.0.0/en/pytorch_model_migration_fine_tuning/performance_metrics_introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/docs/FrameworkPTAdapter/26.0.0/en/pytorch_model_migration_fine_tuning/performance_metrics_introduction.md

# 一体化深度解读：Introduction to Performance Metrics

## 【定位】

这篇文档为 PyTorch 模型迁移/微调（fine-tuning）场景下的**性能指标（Performance Metrics）评测体系**确立优先级与单位规范，作为后续章节将逐一深入介绍各项关键指标的**总览（overview）入口**。

## 【技术要点】

1. **指标优先级硬性排序（原文钦定）**：吞吐量（throughput）> 单步迭代时长（single-step iteration time）> 扩展效率（scaling efficiency）> 内存使用率（memory usage）> 带宽利用率（bandwidth utilization）> 训练效率（training efficiency）> 每秒浮点运算次数（floating-point operations per second）> 计算资源利用率（compute utilization）。该顺序即"调优时先看哪一项"的决策依据。
2. **指标单位统一规范（Table 1）**：吞吐以 `samples/s` 或 `tokens/s` 计；单步迭代时间以秒（s）计；扩展效率以无量纲数值（values）计；内存使用率、计算资源利用率、通信性能、流水线并行效率均以百分比（%）计；训练效率以 `tokens/day` 计；算力以 `TFLOPS/s` 计。
3. **指标集合范围（Table 1 共 9 项）**：在优先级正文提及的 8 项之外，Table 1 额外纳入了**通信性能（Communication performance, %）** 与**流水线并行效率（Pipeline parallelism efficiency, %）** 两项并行类指标。
4. **正文与表格的覆盖差异**：优先级序列中提到的"带宽利用率（bandwidth utilization）"**未**出现在 Table 1 中；而 Table 1 中的"通信性能"与"流水线并行效率"**未**进入优先级排序，需注意二者口径并不完全重合。
5. **章节定位**：原文末尾明确"以下章节仅介绍关键性能指标（key performance metrics）"，暗示 Table 1 中的若干项可能仅作列举、不全部展开详细定义。

## 【关键机制与数据】

- **性能评测的优先级决策树（原文）**：当多指标需要权衡时，按 `throughput → single-step iteration time → scaling efficiency → memory usage → bandwidth utilization → training efficiency → FLOPs/s → compute utilization` 顺序取舍，前者优先级**高于**后者。
- **指标—单位对照（原文 Table 1）**：见下方"表格解读"逐字还原。
- **单位类型分布（由 Table 1 统计可得）**：
  - 速率类：3 项（throughput、training efficiency、FLOPs/s）
  - 时间类：1 项（single-step iteration time）
  - 比例/百分比类：4 项（memory usage、compute utilization、communication performance、pipeline parallelism efficiency）
  - 无量纲类：1 项（scaling efficiency）
- 原文**未提供**任何具体数值、阈值、公式或实验数据，仅给出方法论层面的优先级与单位约定。

## 【表格解读】

**Table 1 Parameters**（原文无表格标题之外的其他列，逐字还原）：

| Metric | Unit |
|---|---|
| Throughput | samples/s, tokens/s |
| Single-step iteration time | s |
| Scaling efficiency | values |
| Memory usage | % |
| Training efficiency | tokens/day |
| Floating-point operations per second | TFLOPS/s |
| Compute utilization | % |
| Communication performance | % |
| Pipeline parallelism efficiency | % |

**逐行解读**：
- **Throughput / samples/s, tokens/s**：模型吞吐量的双单位约定——既支持以样本数计（CV/NLP 通用），也支持以 token 数计（LLM 场景），由任务类型决定取哪一个。
- **Single-step iteration time / s**：一次迭代（step）的耗时，是端到端时延的细粒度版本，常与 throughput 互为倒数视角。
- **Scaling efficiency / values**：扩展效率为无量纲比值（通常 0–1 或 0%–100%），描述多卡/多节点扩展相对于线性加速的接近程度。
- **Memory usage / %**：显存（或内存）占用百分比，反映资源压力与 OOM 风险。
- **Training efficiency / tokens/day**：以"天"为时间窗口、token 为产出单位的训练效率，是 LLM 训练产能的标准口径。
- **Floating-point operations per second / TFLOPS/s**：算力峰值指标，`T` 为 10¹² 量级，用于衡量硬件理论算力被实际任务调用的程度。
- **Compute utilization / %**：计算资源利用率，与 FLOPs/s 互补——前者看比例，后者看绝对值。
- **Communication performance / %**：通信开销占比或通信完成度，分布式训练专用指标，**仅出现于 Table 1、未出现在优先级排序中**。
- **Pipeline parallelism efficiency / %**：流水线并行的有效利用率，分布式训练专用指标，**仅出现于 Table 1、未出现在优先级排序中**。

> 注：原文未给出"带宽利用率（bandwidth utilization）"的独立条目，但其意涵可能部分被 Table 1 中"Communication performance"覆盖，需结合上下文判断，**本文不臆断**。

## 【公式解读】

原文无公式。

## 【关联】

- **本文档在文档仓中的位置**：路径 `FrameworkPTAdapter/26.0.0/en/pytorch_model_migration_fine_tuning/performance_metrics_introduction.md`，归属于 PyTorch 模型迁移/微调（fine-tuning）专题下的"性能指标"子专题。
- **承上关系**：作为 overview 文档，它**承接**模型迁移/微调主流程——完成迁移后进入性能评估阶段时，本篇定义"测什么、按什么顺序看"。
- **启下关系**：原文末尾"以下章节仅介绍关键性能指标（The following section introduces only the key performance metrics.）"明示本文是后续各单项指标详解（如 throughput、scaling efficiency、memory usage 等各自独立章节）的**索引与统一口径页**。
- **横向并列**：Table 1 中"Communication performance"与"Pipeline parallelism efficiency"指向分布式并行训练模块；"Training efficiency / tokens/day"指向 LLM 训练产能口径。
- **内部链接**：原文未提供任何内部链接（文末标注"内部链接: (无)"）。

## 【使用方法】

原文未涉及具体的启用方式、配置项或命令。本文仅作为概念与单位层面的入门说明，**任何具体调用方式、采集工具、采样周期或阈值告警规则均未在原文中给出**。
