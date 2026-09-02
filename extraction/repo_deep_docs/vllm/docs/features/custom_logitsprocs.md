# Custom Logits Processors

> 仓 `vllm` · 路径 `docs/features/custom_logitsprocs.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/custom_logitsprocs.md

# 深度解读：vLLM Custom Logits Processors

## 【定位】
本文档阐述如何在**不修改或重新编译 vLLM 源码**的前提下，由用户编写、加载并使用自定义 logits 处理器（即在请求级 batch 粒度上调整模型下一 token 概率分布的组件），作为对 vLLM 内置 logits 处理器能力的扩展。

---

## 【技术要点】

1. **基类继承**：自定义 logits 处理器必须继承 `vllm.v1.sample.logits_processor.LogitsProcessor`，至少实现 5 个方法：`validate_params`、`__init__`、`apply`、`is_argmax_invariant`、`update_state`。
2. **batch 粒度运行**：输入张量形状固定为 `(num_requests) × (vocab_size)`；只处理启用了该 processor 的请求对应行，其余行保持原样，结果再传入 softmax。
3. **`is_argmax_invariant()` 启动期评估**：返回 `True` 时，vLLM 在所有请求均使用 greedy sampling 的步骤中会跳过该 processor，避免冗余计算。
4. **`update_state()` 处理顺序硬性规定**：必须按 `removes → adds → moves` 的顺序消费 `BatchUpdate`；其中 Add 操作的索引指 **添加发生时刻**的索引，发生在 Move 之前。
5. **BatchUpdate 的构造逻辑**：优先用新增请求替换已完成的请求（按被替换索引升序处理）；新增多于完成则扩展 batch（索引从 `current_max_batch_index + 1` 起始）；新增少于完成则先 Remove 再通过 Unidirectional Move "压缩 (Condense)" 连续化，最后更新 `batch_size`，并视注意力后端情况施加 Swap Move 重排。
6. **自定义参数接入**：通过 [custom arguments](./custom_arguments.md) 机制，从 `SamplingParams.extra_args` 等字段读取用户级配置（例如示例中的 `target_token`）。

---

## 【关键机制与数据】

| 工作流环节 | 原文描述 |
|---|---|
| **张量输入** | 原文: logits processor 消费一个 `(num_requests) × (vocab_size)` 的原始 logits 张量；该张量由模型在 engine step 中输出 |
| **行级作用域** | 原文: 只对启用了该 processor 的请求对应的行做转换，其他行保持不变；转换后整体送入 softmax |
| **in-place vs out-of-place** | 原文: `apply()` 中可对输入 logits 做 in-place 或 out-of-place 修改，in-place 更节省内存 |
| **argmax 不变量优化** | 原文: `is_argmax_invariant()` 在启动时评估一次；若返回 `True`，当所有请求都使用 greedy sampling 时 vLLM 将在该步骤跳过该 processor |
| **`BatchUpdate` 可空** | 原文: 若当前 step 无新增/完成请求且无 batch 重排，则传给 logits processor 的 batch update 为 `None`；但 processor 可基于自身保留的 `output_token_ids` 列表更新状态 |
| **Add 索引语义** | 原文: Add 操作的索引指 *Add 发生时刻* 的索引（即任何 Move 操作之前的索引）；示例中先 Add 到 index 5、后与 index 3 交换，则 `BatchUpdate.added` 记录的是 index 5 |
| **Move 应用顺序** | 原文: Move 操作按 `BatchUpdate.moved` 中出现的顺序依次应用 |
| **示例数值** | 原文: 示例 processor 把 `(num_requests) × (vocab_size)` 张量中除 `target_token` 外的所有 token 置为 `float(-inf)` |

**性能/优化数据**：原文未提供具体性能数字（如吞吐、延迟）。仅指出 in-place 比 out-of-place 更省内存，以及 argmax-invariant 处理器可在 greedy 全开时被跳过（隐含的零开销优化路径）。

---

## 【表格解读】
**原文无表格**。

---

## 【公式解读】

原文未出现 LaTeX 数学公式，但有一组**张量维度记法**，逐字保留如下并解读符号含义：

$$
\text{logits} \in \mathbb{R}^{(\text{num\_requests}) \times (\text{vocab\_size})}
$$

| 符号 | 含义 |
|---|---|
| `logits` | 当前 engine step 中由模型输出的原始 logits 张量，传给 `apply()` |
| `num_requests` | 当前 batch 中的请求数（即 logits 张量的行数） |
| `vocab_size` | 模型词表大小（即 logits 张量的列数） |
| 返回值 | `apply()` 输出的、形状相同的 `(num_requests) × (vocab_size)` 转换后 logits 张量，送入 softmax |

另外原文用伪代码/编号步骤描述了 `BatchUpdate` 的构建算法（步骤 1–5），本质上是一种"先替换、再扩展或压缩、最后重排"的 in-place 索引重写算法，符号含义：
- `current_max_batch_index`：当前 batch 中已有的最大索引；
- `Add(i)`：把一个新增请求放入索引 `i`；
- `Remove(i)`：移除索引 `i` 处的请求；
- `Unidirectional Move(src → dst)`：把 `src` 处的请求单向移到 `dst` 处；
- `Swap Move`：交换两个索引处的请求，用于注意力后端效率重排。

---

## 【关联】

依据文档末尾与正文中的内部链接，该特性与以下模块存在上下游/协作关系：

- **Custom Arguments 机制（`./custom_arguments.md`）**：自定义 logits processor 接收用户级配置的通道（如 `SamplingParams.extra_args`），本文档在 "Passing Custom Argument to a Custom Logits Processor" 一节明确引用此文档。原文链接：`[custom arguments](./custom_arguments.md)`。
- **`vllm.v1.sample.logits_processor` 模块**：基类 `LogitsProcessor`、数据结构 `BatchUpdate`、以及 `MoveDirectionality` 枚举的归属模块（示例代码 `from vllm.v1.sample.logits_processor import (BatchUpdate, LogitsProcessor, MoveDirectionality)` 印证）。
- **`vllm.config.VllmConfig`**：通过 `__init__` 注入引擎配置。
- **`vllm.sampling_params.SamplingParams`**：承载请求级参数与自定义额外参数（`extra_args`），`validate_params` 即对此做校验。
- **Engine Step / Batch Scheduler**：决定 `BatchUpdate` 内容（哪些请求完成、哪些新加入、是否重排）。
- **Attention Backend**：可能触发 Swap Move 重排以提升效率。
- **Softmax 阶段的下游**：转换后 logits 进入采样前的 softmax / 采样算子。

---

## 【使用方法】

> 注：原文文档在示例代码处被截断（`DummyLogitsProcessor.is_argmax_invariant` 之后未提供 `apply`/`update_state` 实现）。以下启用方式仅基于原文已给出的内容。

**启用/编写步骤（基于原文）：**

1. **继承基类**（原文代码片段）：
   ```python
   from vllm.v1.sample.logits_processor import (
       BatchUpdate, LogitsProcessor, MoveDirectionality)
   class DummyLogitsProcessor(LogitsProcessor):
       ...
   ```

2. **实现 5 个必需方法**（原文方法签名）：
   - `@classmethod validate_params(cls, params: SamplingParams)`：校验 `SamplingParams`（含自定义参数），非法则 `raise ValueError`。
   - `__init__(self, vllm_config: VllmConfig, device: torch.device, is_pin_memory: bool)`：保存硬件设备、pin memory 等上下文。
   - `apply(self, logits: torch.Tensor) -> torch.Tensor)`：在 `(num_requests) × (vocab_size)` 张量上做转换，可 in-place。
   - `is_argmax_invariant(self) -> bool`：返回是否影响 argmax（示例返回 `False`，注释为 "Never impacts greedy sampling"，但实际返回 `False`，原文一致）。
   - `update_state(self, batch_update: Optional["BatchUpdate"]) -> None`：按 removes → adds → moves 顺序处理 batch 变化。

3. **示例行为**（原文："The contrived example below implements a custom logits processor … masks out all tokens except for one (`target_token`) with `float(-inf)`"）：
   - 通过 `params.extra_args.get("target_token")` 读取请求级配置。
   - 未提供 `target_token` 的请求 → 该 processor 对其不生效。
   - `target_token` 非整数 → 在 `validate_params` 中抛 `ValueError`。

**命令/配置项**：原文未给出 CLI 启动命令、`engine_args` 配置项或 `--logits-processor` 之类的开关，仅说明 "loaded into vLLM at initialization without needing to modify or recompile the vLLM source code"。**具体加载/注册 API 原文未涉及**（文档本身在该部分被截断，且顶部明确提示 *"the API may change in the near future"*）。
