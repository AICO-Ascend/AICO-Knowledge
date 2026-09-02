# IndexCache

> 仓 `vllm` · 路径 `docs/features/index_cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/index_cache.md

# IndexCache 文档深度解读

## 【定位】
这篇文档介绍 vLLM 中的 **IndexCache** 能力——通过在 DeepSeek-V3.2 (DSA) 模型的多层之间缓存并复用 top-k token 索引, 削减稀疏注意力中逐层重复计算 top-k 所带来的冗余开销。

---

## 【技术要点】

1. **问题域**: DeepSeek-V3.2 采用 **DeepSeek Sparse Attention (DSA)** 机制, 每一层都需要独立完成 top-k token 选择, 在层数很多的深层模型中, 这部分计算代价昂贵。
2. **核心思想**: IndexCache 让若干层跳过 top-k 计算, 直接复用上一层得到的 top-k 索引, 从而把"每层必算"降级为"按需计算 + 层间共享"。
3. **主开关 `use_index_cache`** (bool, 默认 `false`): 必须显式设为 `true` 才启用; 仅靠 `index_topk_freq` 默认值无法启用功能。
4. **频率模式 `index_topk_freq`** (int, 默认 `1`): 按层间隔触发完整 top-k 计算。`1` 表示每层都算 (即功能"禁用"等效态), `4` 表示每 4 层算一次 (即大约 1/4 的层参与计算)。
5. **显式模式 `index_topk_pattern`** (str, 默认 `null`): 逐层自定义的 `F/S` 字符序列, 每个字符对应一个 DSA 层; 一旦设置, **优先级高于 `index_topk_freq`**。
6. **F/S 语义**: `F` = Full (本层独立计算并存储 top-k 索引), `S` = Shared (本层接收并复用上一层缓存的索引, 不重新计算)。

---

## 【关键机制与数据】

原文 "How It Works" 节描述的工作流程如下 (三步):

> **原文:**
> 1. When IndexCache is enabled, layers marked with `"F"` (Full) calculate and store top-k indices
> 2. Subsequent layers marked with `"S"` (Shared) receive the cached indices from the previous layer instead of recomputing
> 3. The cached indices are passed through the layer stack, reducing total computation

可概括为: **F 层产出 → 索引沿层栈向后传递 → S 层直接消费, 不重算**。 整个机制是沿 transformer 层栈单向流动的 (从低层向高层), 缓存的索引只被下游的 S 层读取。

性能数据方面, **原文未提供**任何具体的加速比、显存节省、吞吐量提升等量化指标; 仅在概念层面指出"reducing total computation"。

---

## 【表格解读】

原文含一张配置参考表, 逐字还原如下:

| Parameter            | Type | Default | Description                                                                                                                                      |
|----------------------|------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_index_cache`    | bool | false   | Enable IndexCache. Must be set to true to use this feature                                                                                       |
| `index_topk_freq`    | int  | 1       | Frequency (in layers) at which top-k is computed. 1 = compute on every layer (disabled), 4 = compute on 1/4 of layers                            |
| `index_topk_pattern` | str  | null    | Per-layer F/S pattern. Overrides index_topk_freq if set. Each character maps to one DSA layer: F = Full, S = Shared                              |

逐行解读:

- **`use_index_cache` / bool / `false`**: 总开关。默认关闭, 不开启则其余两个参数即便设置也不会生效 (见 "Requirements" 节要求 `use_index_cache: true`)。
- **`index_topk_freq` / int / `1`**: 计算频率, 单位为层。`1` 是"每层都算"的语义, 等价于把缓存机制关闭; 调大到 `4` 等数值才会出现真正的跳过与复用, 即大约 1/4 层执行计算、其余 3/4 层复用。
- **`index_topk_pattern` / str / `null`**: 显式逐层控制开关。字符串中**每个字符对应一个 DSA 层**, `F` 触发计算, `S` 触发复用。文档明确该参数"**overrides `index_topk_freq` if set**", 即它一旦非空, 频率参数就被忽略。

---

## 【公式解读】

**原文无公式** (无 LaTeX 表达、无伪代码算法式; 仅以编号列表和一段 F/S 模式字符串描述机制)。

---

## 【关联】

- **模型/架构依赖**: DeepSeek-V3.2, 以及所有兼容的 **DeepSeek Sparse Attention (DSA)** 模型; IndexCache 不是通用 transformer 优化, 而是 DSA 专属。
- **上游机制**: DeepSeek Sparse Attention 的 **per-layer top-k token selection**——IndexCache 直接插入到该选择步骤, 改变其是否在每一层都执行。
- **外部论文**: 引用 [IndexCache Paper](https://arxiv.org/abs/2603.12201) 作为方法出处。
- **配置通道**: 借助 HuggingFace 兼容的 `--hf-overrides` 机制把配置写进模型 config; 因此运行时需保留 HF overrides 链路, 不能用普通 CLI flag 替代。
- **文档内无内部链接** (文档底部未列其他 vllm 特性页)。

---

## 【使用方法】

**(a) CLI 启用——频率模式** (原文):

```bash
vllm serve deepseek-ai/DeepSeek-V3.2 \
    --hf-overrides '{"use_index_cache": true, "index_topk_freq": 4}' ...
```

**(b) CLI 启用——显式逐层模式** (原文, 原文标注 "custom pattern for 61 layers: F = compute, S = reuse"):

```bash
vllm serve deepseek-ai/DeepSeek-V3.2 \
    --hf-overrides '{"use_index_cache": true, "index_topk_pattern": "FFSFSSSFSSFFFSSSFFFSFSSSSSSFFSFFSFFSSFFFFFFSFFFFFSFFSSSSSSFSF"}'
```

(说明: 原文称该模式针对 61 层, 但所给字符串实际字符数与该标注不完全一致——此处按原文忠实呈现, 不作改写。)

**(c) 配置项要点 (对应上表)**:

- `use_index_cache` 必须设为 `true`。
- `index_topk_freq` 与 `index_topk_pattern` 二选一; 设置 `index_topk_pattern` 时 `index_topk_freq` 被覆盖。
- 模式字符仅 `F` / `S` 两种取值。

**(d) 前提条件 (原文 Requirements 节)**:

- 模型必须是 **DeepSeek-V3.2 或兼容的 DSA 模型**。
- 必须通过 `--hf-overrides` 传入 `use_index_cache: true`。

**(e) 原文未涉及**: API 端点调用方式、Python SDK 用法、动态切换/热更新配置、与 prefix caching / chunked prefill 等其他 vllm 特性的组合示例——这些均**未在原文中出现**。
