# Async Save Torch Dist

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/async_save_torch_dist.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/async_save_torch_dist.md

# 一体化深度解读: Async Save Torch Dist

## 【定位】

这篇文档描述了 MindSpeed LLM 在 Megatron 分布式检查点语义之上,为 `torch_dist` 格式检查点提供**异步落盘**的能力,用以解决大规模训练中同步保存检查点导致的训练暂停问题。

---

## 【技术要点】

1. **支持的保存格式**: 全文明确指出检查点仅支持 `torch` 与 `torch_dist` 两种格式;其中 **`torch_dist` 是唯一支持异步保存的格式**,`torch` 仅支持同步保存,`torch_dist` 同时支持同步与异步两种保存模式。

2. **启用开关**: 通过命令行参数 **`--async-save`** 启用异步保存。原文明示,启用后保存阶段通过 **`schedule_async_save`** 提交异步请求,checkpoint tracker 更新与 `one_logger` 成功事件运行在 **`finalize` 回调**中。

3. **训练结束兜底**: 训练结束时调用 **`maybe_finalize_async_save(blocking=True, terminate=True)`** 一次,以完成尚未结束的保存请求。

4. **格式兼容性约束**: `--async-save` **仅支持最终格式为 `torch_dist` 的检查点**;若格式为遗留的 `torch` 或其他分布式格式,将触发 unsupported-mode 检查(即报错)。

5. **使用场景约束**: 该特性**仅适用于预训练 (pretraining) 场景**;异步保存的 `torch_dist` 权重可直接用于推理,也可加载后继续预训练,但**不支持 LoRA、finetuning、SFT、DPO 等下游任务**。

6. **资源代价提示**: 原文明示"异步保存会增加 CPU 使用率",因此在 LLM 场景且保存频繁时,文档**反而建议使用同步保存**。这是一个值得注意的反直觉建议。

---

## 【关键机制与数据】

### 工作原理(基于原文提炼)

- **主流程与后台写盘解耦**: 主训练流程仅负责"构建并提交保存请求",真正的分片写入在后台异步进行,从而训练可继续推进,降低 checkpoint 相关的停顿。
- **两阶段收口**:
  - **保存阶段**: 调用 `schedule_async_save` 提交异步保存请求;
  - **收尾阶段**: 在 `finalize` 回调中执行 checkpoint tracker 更新与 `one_logger` 成功事件;
  - **训练终止**: 调用 `maybe_finalize_async_save(blocking=True, terminate=True)` 阻塞式收尾所有未完成请求。
- **同步与异步对比**(原文描述):
  - 异步保存: 主流程提交后立即返回,不阻塞训练;
  - 同步保存: 主流程必须等待保存完成后才能继续后续训练步骤。

### 性能数据

**原文未提供任何具体的性能数字、吞吐提升百分比或延迟节省数值。** 因此本节除机制说明外,无可量化的性能数据可引用。

### 资源权衡

- **CPU 代价**: 原文明示"异步保存会增加 CPU 使用率";
- **保存频率权衡**: 原文针对 LLM 与高频保存场景,**反而建议使用同步保存**,这是一个明确的反直觉推荐点。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

原文中显式提及的关联特性/模块如下:

- **底层语义**: 基于 **Megatron 的分布式检查点语义**(Megatron-LM 风格的 dist checkpoint)扩展而来,可见该特性在仓内与 Megatron-Core (mcore) 路径紧密相关,而非独立实现。
- **保存格式矩阵**: 与 **`torch` 格式保存**形成对比关系——`torch` 仅支持同步,`torch_dist` 同时支持同步与异步,二者并列构成 MindSpeed LLM 的检查点格式体系。
- **可加载的下游用途**: 异步保存的 `torch_dist` 权重
  - 可直接用于**推理**;
  - 可加载后**继续预训练**;
  - 但**不支持 LoRA / finetuning / SFT / DPO 等下游任务**(这些场景的 checkpoint 保存仍走其他路径)。
- **观测链路**: 通过 `one_logger` 在 `finalize` 回调中发出成功事件,与训练日志/可观测性模块存在联动。
- **tracker 机制**: 异步保存的 tracker 更新被推迟到 `finalize` 回调执行,与 checkpoint tracker 模块存在时序耦合。

> 备注: 文档未给出任何内部链接(原文标注"内部链接: (无)"),因此无法从文末链接直接反推上下游文档路径;以上关联均基于正文语义推断,仅涉及文中明确出现的模块名/特性名。

---

## 【使用方法】

根据原文,可直接还原的启用方式如下:

### 1. 启用异步保存

在启动训练的命令中加入参数:

```
--async-save
```

### 2. 隐含的前置条件(原文约束,非显式命令)

- 检查点的**最终格式必须为 `torch_dist`**(若仍使用遗留 `torch` 或其他分布式格式,会触发 unsupported-mode 检查并报错);
- 当前任务必须是**预训练 (pretraining)**,不能是 LoRA / finetuning / SFT / DPO 等下游任务。

### 3. 训练结束时的收尾

原文提示训练结束时框架会自动调用:

```
maybe_finalize_async_save(blocking=True, terminate=True)
```

以阻塞方式终止并完成所有未结束的保存请求。用户**无需手动调用**该函数,这是框架层面的兜底。

### 4. 选型建议(原文给定的反直觉提示)

- 若训练任务为 **LLM 且保存频率较高**,原文**反而建议关闭 `--async-save`、采用同步保存**,以避免 CPU 使用率被异步保存拉满带来的副作用。
- 反之,若保存不频繁且希望消除保存带来的训练停顿,才推荐启用异步保存。

> 原文未提供具体的配置文件路径、环境变量名或更细粒度的调参项(如线程数、队列深度等),本节未涉及这些未在原文中出现的内容。
