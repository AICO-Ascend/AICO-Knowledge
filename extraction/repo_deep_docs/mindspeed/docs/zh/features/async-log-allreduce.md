# 异步日志全归约 (Async Log Allreduce)

> 仓 `mindspeed` · 路径 `docs/zh/features/async-log-allreduce.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/async-log-allreduce.md

# 异步日志全归约 (Async Log Allreduce) — 一体化深度解读

## 【定位】

这篇文档针对分布式训练中同步日志全归约会阻塞训练主流程、成为性能瓶颈的问题，介绍了 `mindspeed` 通过将日志相关 `all_reduce` 改为非阻塞方式 (`async_op=True`)、并与后续计算步骤重叠执行以提升整体吞吐量的能力。

## 【技术要点】

1. **核心机制**：使用 `torch.distributed.all_reduce(..., async_op=True)` 让日志归约不阻塞训练主流程，通信与后续计算 step 重叠。
2. **数据打包方式**：把 `torch.sum(losses * loss_mask)` 与 `total_tokens` 用 `torch.cat([..., ...]).view(1)` 拼成两元素 `loss` 张量，DP group 上做归约后同时承载 `lm loss` 统计。
3. **CP 路径独立归约**：当 `args.context_parallel_size > 1` 时，先在 `mpu.get_context_parallel_group()` 上做一次 `all_reduce`，确保 CP 维度已聚合并保留 `async_op` 仅用于日志路径。
4. **健全性校验链**：依赖 `rerun_state_machine` 在归约前对 `loss[0]` 做 NaN / Inf (`tolerance=0.0`, `fatal=True`) 以及 spike (`SPIKY_LOSS_FACTOR`, `fatal=False`) 三类校验，前向确定性结果不容忍误差。
5. **返回值改造**：将原日志同步等待改为返回 `({ 'lm loss': (reporting_loss[0], reporting_loss[1]) }, allreduce_handle)` 元组，把异步 handle 交由调度器稍后回收。
6. **显存/视图兼容处理**：注释指出 `loss[0]` 是 `loss` 的 view（存在 `_base`），会在 `deallocate_output_tensor` 触发 assert，因此对 `loss[0]` 与 `loss[1]` 都调用 `.clone().detach()`；`local_num_tokens` 还额外 `.to(torch.int)`。

## 【关键机制与数据】

- **工作原理**：日志同步路径从"算完→阻塞等所有 rank 通信→记录"变成"算完→发起非阻塞 `all_reduce`→把 handle 返回给上层→训练继续前进→真正写日志时再同步"。原文："使用非阻塞式(non-blocking)全归约操作，允许训练流程继续执行而不等待日志通信完成"。
- **数据流**：
  1. 在 micro-batch 内按 `loss_mask` 计算 `sum(losses * mask)` 与 `total_tokens`，`torch.cat` 拼成 `loss`。
  2. 若开启 CP，先在 CP group 上对 `loss` 做同步 `all_reduce`。
  3. 在 DP group 上对 `reporting_loss = loss.clone().detach()` 发起 `async_op=True` 的 `all_reduce`，返回 `allreduce_handle`。
  4. `loss_func` 把 `({ 'lm loss': (reporting_loss[0], reporting_loss[1]) }, allreduce_handle)` 一并返回。
  5. 调度器在真正记录 metrics 时再同步该 handle，从而把通信窗口隐藏在下一步前/反向计算之中。
- **性能数据**：原文未给出任何量化数字，仅以定性表述"训练吞吐量提升""资源利用率提高""开销变得显著"描述影响面。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式（损失聚合 `torch.sum(losses.view(-1) * loss_mask)` 是代码表达式而非独立公式段落，按原文不单列为公式进行解读）。

## 【关联】

- **上下文并行组 `mpu.get_context_parallel_group()`**：与文档涉及的 CP（context parallel）路径耦合；仅当 `args.context_parallel_size > 1` 时触发同步归约。
- **数据并行组 `mpu.get_data_parallel_group()`**：异步日志归约的目标集合，日志统计在 DP 范围内聚合。
- **重跑状态机 `get_rerun_state_machine()` / `SPIKY_LOSS_FACTOR`**：与 rerun / NaN-Inf / spiky-loss 校验特性共用，校验先于异步通信发起。
- **流水线调度 `core/pipeline_parallel/schedule.py::deallocate_output_tensor`**：注释中点名的下游调用点，因为 `loss[0]` 是 `loss` 的 view（`_base` 非 None）会在该处触发 assert，因此要求 `.clone()`；这表明特性与 pipeline parallel 调度器存在强耦合。
- **Megatron 训练入口 `pretrain_gpt.py`**：使用方式中明确要求替换该文件中的 `loss_func`。
- 原文内部链接块标注为"(无)"，故本节仅基于正文中出现的符号/模块名归纳。

## 【使用方法】

1. 在启动 bash 脚本中追加命令行参数 `--async-log-allreduce`。
2. 将 `pretrain_gpt.py` 中 `loss_func` 替换为原文给出的 `loss_func(loss_mask, output_tensor)` 实现，关键差异点：
   - `loss = torch.cat([torch.sum(losses.view(-1) * loss_mask).view(1), total_tokens.view(1)])`
   - CP 分支：`if args.context_parallel_size > 1: torch.distributed.all_reduce(loss, group=mpu.get_context_parallel_group())`
   - 日志归约分支：`reporting_loss = loss.clone().detach()` 后调用 `torch.distributed.all_reduce(reporting_loss, group=mpu.get_data_parallel_group(), async_op=True)`，拿到 `allreduce_handle`
   - 返回值：`(loss[0].clone(), local_num_tokens, ({'lm loss': (reporting_loss[0], reporting_loss[1])}, allreduce_handle))`，其中 `local_num_tokens = loss[1].clone().detach().to(torch.int)`
3. 适用条件（原文）：大规模分布式训练（数百至数千 NPU）、频繁记录训练指标、计算与通信需高度重叠、对训练吞吐量敏感的应用。
