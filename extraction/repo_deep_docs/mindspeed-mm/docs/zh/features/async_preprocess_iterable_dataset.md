# AsyncPreprocessIterableDataset

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/async_preprocess_iterable_dataset.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/async_preprocess_iterable_dataset.md

# AsyncPreprocessIterableDataset 文档深度解读

## 【定位】
这篇文档描述了 `AsyncPreprocessIterableDataset` —— 一种面向 HuggingFace `streaming=True` 流式数据场景的异步预处理包装器，通过"单线程顺序读取上游数据 + 多 worker 并发预处理 + 按序重排输出"的设计，将单条样本的预处理工作从训练主线程中解耦出来,在保持样本逻辑顺序不变的前提下由多个后台 worker 并发执行。

---

## 【技术要点】

1. **双路径集成**:能力同时部署在 Megatron 与 FSDP2 两条训练链路 —— Megatron 路径实现位于 `mindspeed_mm/data/datasets/qwen2vl_dataset.py`,FSDP2 路径实现位于 `mindspeed_mm/fsdp/data/datasets/huggingface/qwen2vl_dataset.py`。

2. **两个核心配置开关**:`async_preprocess`(是否启用流式异步预处理,主要在 `streaming: true` 时生效)与 `async_preprocess_buffer_size`(异步预处理的缓冲深度,按单条原始样本生效,而不是按批次生效)。

3. **配置归一化默认值**:二者都未配置时默认 `buffer_size=8`,`num_workers` 取 `min(buffer_size, cpu_count)`;只配置 `preprocessing_num_workers` 时 `buffer_size` 回落为同样大小;只配置 `async_preprocess_buffer_size` 时 worker 数会自动补齐为不超过 CPU 数量的合理值。

4. **必须先分片后预处理**:DP 分片(`DistributedIterableDataset`)必须先于 `AsyncPreprocessIterableDataset` 执行,否则会导致重复预处理、CPU/线程/队列开销浪费,以及因样本过滤或一对多展开导致分片边界漂移。

5. **三类消息类型**:worker 通过 `result_queue` 传递 `(message_type, payload, extra)`,主要包含 `result`(某个 `sequence_idx` 对应的样本预处理完成)、`done`(worker 处理完所有任务并退出)、`error`(producer 或 worker 内部抛出异常,需终止整个迭代链路)三种消息。

6. **单条样本批量化适配**:由于 `preprocess_fn` 以 batch 字典为输入,异步路径会把单条样本临时封装成长度为 1 的 batch 再调用 `preprocess_fn`,因此开启 `async_preprocess` 后 `preprocessing_batch_size` 不用于控制 worker 的处理粒度。

---

## 【关键机制与数据】

### 数据流链路(原文)
```text
load_dataset(..., streaming=True)
    -> align_dataset(...)
    -> DistributedIterableDataset
    -> AsyncPreprocessIterableDataset
    -> DataLoader / StatefulDataLoader
    -> DataCollator
    -> 模型前向与训练循环
```

### 工作原理(原文)
- **Producer 线程**:由 `__iter__()` 内部启动,只做两件事 —— 通过 `enumerate(self.dataset)` 顺序遍历当前 rank 的子流,为每条样本分配单调递增的 `sequence_idx`,并将 `(sequence_idx, item)` 放入 `task_queue`。`sequence_idx` 只由上游子流的迭代顺序决定,不由 worker 的完成时序决定。
- **Worker 线程**:从 `task_queue` 取出任务执行 `_preprocess_item()`,处理完成后将结果以 `(message_type, payload, extra)` 写入 `result_queue`,不直接访问上游 dataset。
- **按序重排**:主迭代器使用 `pending_results[sequence_idx]` 缓存已到达但未到输出顺序的结果,只有当 `pending_results` 中已存在 `next_sequence_idx` 时才真正 `yield` 对应结果。
- **派生结果整体输出**:`_preprocess_item()` 可能返回 `processed_items` 列表(一对多展开),命中某个 `sequence_idx` 后会先完整输出这一组 `processed_items`,再推进到下一个 `sequence_idx`。

### 两 rank 分片示例(原文)
原始样本流 `s0, s1, s2, s3, s4, s5`,DP size 为 2:
- rank 0 分片后看到 `s0, s2, s4`,本 rank 内重新编号为 `sequence_idx = 0, 1, 2`
- rank 1 分片后看到 `s1, s3, s5`,本 rank 内同样重新编号为 `sequence_idx = 0, 1, 2`

若 rank 0 上处理 `s2` 的 worker 比处理 `s0` 的 worker 更快,`result_queue` 可能先收到 `sequence_idx = 1`,但主迭代器会先把它放入 `pending_results` 而不输出;只有等编号 0 到达后才会按 `0 -> 1 -> 2` 顺序产出。

### 调参经验(原文)
- 预处理明显慢于训练:优先增加 `preprocessing_num_workers`,再将 `buffer_size` 设为不小于 `num_workers` 的值
- 两者接近:`buffer_size` 调到 `num_workers` 到 `2 * num_workers` 区间
- 训练明显慢于预处理:`buffer_size` 保持在 `num_workers` 附近即可

### 流式数据加载模式(原文)
当前仓库支持 `base` 和 `sampler` 两种模式:`base` 模式按 dataset 自身的迭代顺序读取,兼容 `IterableDataset`,但不支持 shuffle;`sampler` 模式依赖 `len(dataset)` 生成全局索引,不适用于流式读取。当前异步预处理能力仅基于 `base` 模式实现。

---

## 【表格解读】

**原文无表格**。文档中并未提供参数表、性能对比表或配置项表等结构化表格;关键参数(`async_preprocess`、`async_preprocess_buffer_size`、`preprocessing_num_workers`、`preprocessing_batch_size` 等)以正文段落和 JSON 示例代码片段形式给出。

---

## 【公式解读】

**原文无公式**。文档未包含 LaTeX 数学公式或伪代码形式的算法表达式;关键算法通过自然语言文字(如"先分片后异步预处理"、"按 `sequence_idx` 做重排"、"消息类型分类")与一段链路图(`load_dataset -> ... -> 模型前向与训练循环`)进行描述。

---

## 【关联】

### 上游模块
- **`DistributedIterableDataset`**:负责按 DP rank 切分原始样本流,必须先于 `AsyncPreprocessIterableDataset` 执行。Megatron 路径按 `idx % num_dp == dp_rank` 取样,FSDP2 路径按同样的模运算规则切分。
- **`align_dataset(...)`**:在数据流链路中位于 `load_dataset` 之后、`DistributedIterableDataset` 之前,用于数据对齐。
- **Megatron 侧的 `mpu` 模块**:FSDP2 侧的并行状态查询 —— 用于计算本 rank 应消费的子序列。

### 配置定义
- Megatron 配置定义位于 `mindspeed_mm/data/data_utils/func_utils/convert.py`
- FSDP2 配置定义位于 `mindspeed_mm/fsdp/data/data_utils/func_utils/convert.py`

### 实现路径
- Megatron: `mindspeed_mm/data/datasets/qwen2vl_dataset.py`,调用入口为 `get_qwen2vl_dataset()`
- FSDP2: `mindspeed_mm/fsdp/data/datasets/huggingface/qwen2vl_dataset.py`

### 下游消费者
- `DataLoader / StatefulDataLoader`(异步预处理结果的消费者,支持断点续训)
- `DataCollator`(后续的样本组装)
- 模型前向与训练循环

### 相关功能/概念
- **`dataset.map(..., batched=True)` 路径**:关闭 `async_preprocess` 时走的非流式预处理路径,作为对照说明。
- **`preprocessing_batch_size`**:与 `async_preprocess_buffer_size` 概念不同 —— 前者控制 `dataset.map` 路径每次送入 `preprocess_fn` 的样本数,后者控制异步路径可缓存多少条"等待处理或等待按序输出"的样本。
- **窗口/缓冲区内局部 shuffle**:文档指出后续若需要引入乱序能力,更合适的方向是在窗口或缓冲区内做局部 shuffle,因 `sampler` 模式的全局 shuffle 不适用于流式场景。

---

## 【使用方法】

### Megatron 路径(Qwen2.5Omni)
- 训练入口脚本:`examples/qwen2.5omni/finetune_qwen2_5_omni_7b.sh`
- 训练程序入口:`pretrain_vlm.py`
- 默认数据配置文件:`examples/qwen2.5omni/data_7b.json`

### 关键配置(原文 JSON 示例片段)
在数据配置中至少增加以下字段:

```json
{
    "dataset_param": {
        "dataset_type": "huggingface",
        "preprocess_parameters": {
            "model_name_or_path": "./ckpt/hf_path/Qwen2.5-Omni-7B",
            "use_fast_tokenizer": true,
            "split_special_tokens": false,
            "image_max_pixels": 262144,
            "image_min_pixels": 0,
            "video_max_pixels": 16384,
            "video_min_pixels": 0,
            "video_fps": 2.0,
            "video_maxlen": 128
        },
        "basic_parameters": {
            "template": "qwen2_omni",
            "dataset_dir": "./data",
            "dataset": "./data/mllm_format_llava_instruct_data.json",
            "cache_dir": "./data/cache_dir",
            "train_on_prompt": false,
            "mask_history": false,
            "preprocessing_batch_size": 1000,
            "preprocessing_num_workers": 16,
            "max_samples": null,
            "tool_format": null,
            "streaming": true,
            "async_preprocess": true,
            "async_preprocess_buffer_size": 16
```
*(注:原文此处被截断,`}` 闭合括号未完整呈现。)*

### 启用条件
当 `streaming: true` 与 `async_preprocess: true` 同时设置时,数据集构建流程就会进入 `AsyncPreprocessIterableDataset` 异步路径。
