# Async Save Torch Dist

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/async_save_torch_dist.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/async_save_torch_dist.md

【定位】
本文档描述 MindSpeed-LLM 基于 Megatron 分布式 checkpoint 语义所提供的 `torch_dist` 格式 checkpoint 异步保存能力，旨在解决大规模训练中同步保存 checkpoint 导致训练主流程阻塞、吞吐下降的问题。

【技术要点】
- checkpoint 仅支持 `torch` 与 `torch_dist` 两种格式；只有 `torch_dist` 格式才支持异步保存，`torch` 格式只支持同步保存，且会阻塞训练主流程。
- `torch_dist` 格式同时支持两种保存模式：异步保存（主流程仅构建并提交保存请求、不阻塞训练）和同步保存（保存完成后才继续后续训练步骤）。
- 异步保存通过开启 `--async-save` 启用；保存阶段通过 `schedule_async_save` 提交异步请求。
- checkpoint tracker 更新与 one_logger 成功事件统一放在 finalize 回调执行。
- 训练结束统一调用 `maybe_finalize_async_save(blocking=True, terminate=True)` 收敛未完成请求。
- 异步保存会额外增加 CPU 占用；大规模模型或频繁保存场景建议改用同步保存。
- 仅适用于预训练场景；保存后的权重可直接用于推理，也可加载后继续预训练。

【关键机制与数据】
- 数据流：主训练流程仅负责「构建并提交保存请求」→ 后台执行分片写盘 → 训练主流程可继续推进，从而减少 checkpoint 引发的训练停顿。
- 资源代价（原文）：异步保存会增加 CPU 占用；因此在大规模模型和频繁保存场景下，文档建议走同步保存以避免 CPU 资源争抢。
- 终结收敛（原文）：训练结束时通过 `maybe_finalize_async_save(blocking=True, terminate=True)` 对未完成的异步写盘请求做最终收敛。
- 兼容性约束（原文）：若处于 legacy `torch` 或其他分布式格式，开启异步保存将触发「不支持的模式检查」。

【表格解读】
原文无表格

【公式解读】
原文无公式

【关联】
文末给出的内部链接标注为「无」。文档内容自身涉及到的关联点（仅基于原文描述）如下：
- 上游依赖：依赖 Megatron 的分布式 checkpoint（Distributed Checkpoint）语义，由 MindSpeed-LLM 在其上叠加异步保存能力。
- checkpoint 格式维度：与 `torch` 格式（仅同步保存）形成互斥/补充关系；`torch_dist` 格式本身仍保留同步保存模式。
- tracker / one_logger：异步保存将 tracker 更新与 one_logger 成功事件下沉到 finalize 回调，与 checkpoint 主流程的写入解耦。
- 下游使用：保存后的 `torch_dist` checkpoint 可直接用于推理，或加载后继续预训练；当前不支持 LoRA、微调、SFT、DPO 等下游任务。

【使用方法】
- 启动异步保存：在训练命令中开启 `--async-save`。
- checkpoint 格式要求：必须使用 `torch_dist` 格式作为最终 checkpoint 格式；若处于 legacy `torch` 或其他分布式格式，将触发不支持的模式检查。
- 收尾收敛（原文）：训练结束阶段需统一调用 `maybe_finalize_async_save(blocking=True, terminate=True)`，以阻塞方式终结并收敛未完成的保存请求。
- 场景选择（原文）：大规模模型或频繁保存场景建议改用同步保存，以规避异步保存带来的 CPU 占用上升；下游任务（LoRA / 微调 / SFT / DPO）暂不支持。
