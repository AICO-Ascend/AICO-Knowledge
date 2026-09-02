# Logits Processors

> 仓 `vllm` · 路径 `docs/design/logits_processors.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/logits_processors.md

# Logits Processors 设计文档解读

## 【定位】
本文档定义了 vLLM 引擎与"logits 处理器（logits processor）"之间的交互契约以及实现 logits 处理器的编程模型，核心回答："logits 处理器如何在 vLLM 的持久化批处理（persistent batch）架构下以**批粒度**、**有状态**的方式接入 model runner → sampler 流水线，并兼顾 greedy sampling 的算力节约。"

## 【技术要点】

1. **批粒度张量处理**：单个 logits 处理器消费形状为 `(num_requests) x (vocab_size)` 的整批原始 logits 张量，仅对启用该处理器的请求所在行做变换，其他行保持原样，随后整张量送入 softmax。
2. **每引擎步两阶段调用**：每个 engine step 中，引擎依次执行 (1) 调用每个 logits 处理器的 `update_state(batch_update)` 让其内部状态与新的 persistent batch 状态对齐；(2) 在 sampler 中调用各处理器的 `apply(logits)`（可原地修改，也可返回新张量；原地更省内存）。
3. **三类批变更事件**：`BatchUpdate`（frozen dataclass）封装了 `batch_size` 与三段序列——`removed: Sequence[RemovedRequest]`（被移除请求在批内的索引，整数）、`added: Sequence[AddedRequest]`（形如 `(index, SamplingParams, prompt_tok_ids, output_tok_ids)` 的元组）、`moved: Sequence[MovedRequest]`（形如 `(index1, index2, MoveDirectionality)` 的元组），用于精确描述 persistent batch 的增删与重排。
4. **两类移动语义**：通过 `enum.Enum` 的 `MoveDirectionality` 区分 `UNIDIRECTIONAL`（单向 i1→i2 移动）与 `SWAP`（双向 i1↔i2 交换）。
5. **argmax-invariant 优化路径**：sampler 在采样前判定全批是否均为 greedy；若是，则跳过 `sampling_metadata.logitsprocs.argmax_invariant` 中的所有处理器；非 argmax-invariant 处理器 (`non_argmax_invariant`) 则在采样更早阶段、路径中"logits = processor.apply(logits)"循环里执行，**永远不能被跳过**。
6. **状态同步入口**：模型运行器在 `execute_model` → `_update_states` → `InputBatch.refresh_metadata()` 内调用 `batch_update_builder.get_and_reset(self.num_reqs)` 后，逐个调用 `logit_proc.update_state(batch_update)`；此后再做模型推理与采样。

## 【关键机制与数据】

- **工作原理（数据流）**：
  - scheduler 输出 → `GPUModelRunner.execute_model` 调度新请求/结束请求/请求重排 → `_update_states` → `InputBatch.refresh_metadata` → 构造 `BatchUpdate(batch_size, removed, added, moved)` → 对 `self.logitsprocs.all` 中每个处理器逐个调用 `update_state(batch_update)`。
  - 模型推理产出 `(num_requests) x (vocab_size)` logits → 构造 `SamplingMetadata`（其中的 `logitsprocs` 引用来自持久化批数据结构）→ `Sampler.forward` 中按 `non_argmax_invariant` → `sample` → `argmax_invariant` 三段顺序套用 `apply(logits)`，最终采样并返回 `sampler_output`。
- **性能/优化数据**（原文）：当且仅当"全批均为 greedy 采样"时，sampler "saves compute by skipping argmax-invariant logits processors"；原文给出的唯一量化提示是"原地 `apply()` 比非原地内存更高效"（"in-place is more memory-efficient"），未提供具体加速比、吞吐或时延数字。
- **关键抽象/数据结构**：原文通过伪代码明确给出 `GPUModelRunner`、`InputBatch.refresh_metadata`、`Sampler.forward/sample`、`BatchUpdate`、`MoveDirectionality`、`AddedRequest/MovedRequest/RemovedRequest` 类型别名以及 `LogitsProcessor`（ABC 抽象基类，但文档因截断未给出 `apply`/`update_state` 的完整签名）。

> 原文未给出任何 benchmark 数字或性能表格。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无数学公式。原文给出的"公式性"表达均为结构性伪代码，例如：

$$
\text{applied\_logits} = f_{\text{LP}}(\text{logits}), \quad \text{shape} = (\text{num\_requests}) \times (\text{vocab\_size})
$$

其中符号含义（按原文语义还原）：
- $f_{\text{LP}}$：单个 logits 处理器的 `apply` 方法。
- `logits`：模型推理输出的原始 logits 张量，行 = 各请求、列 = 词表维度。
- `num_requests`、`vocab_size`：分别为批内请求数与词表大小。

以及流程式伪式：

$$
\text{Sampler}(\text{logits}, \mathbb{M}) = \text{sample}\Big(\prod_{p \in \text{non\_argmax\_invariant}} p.\text{apply}(\text{logits}),\ \mathbb{M}\Big)
$$

其符号含义：
- $\mathbb{M}$：`SamplingMetadata`，含 `logitsprocs` 引用。
- $\prod_{p \in \text{non\_argmax\_invariant}} p.\text{apply}(\text{logits})$：顺序对每个非 argmax 不变量 logits 处理器施加 `apply`（链式、可在 `Sampler.forward` 中以"左折叠"形式形成新张量或原地改写）。
- $\text{sample}(\cdot, \mathbb{M})$：当全批 greedy 时可省去后续 argmax-invariant 处理器乘积。

## 【关联】
- **下游用户指引**：文末明确给出内部链接 `../features/custom_logitsprocs.md`，指向"自定义 logits 处理器"特性文档，承接本文给出的 `LogitsProcessor` 抽象与 `BatchUpdate` 模型，供读者按教程编写自己的处理器。
- **上游模块**：
  - `GPUModelRunner.execute_model` / `_update_states`：负责把 scheduler 输出转成 `BatchUpdate` 并驱动处理器 `update_state`。
  - `InputBatch` / `gpu_input_batch.py`：持有 `self.logitsprocs.all` 与 `batch_update_builder`，是处理器状态的"权威源"。
  - `Sampler.forward/sample`（`sampler.py`）：通过 `sampling_metadata.logitsprocs.{non_argmax_invariant, argmax_invariant}` 调用 `apply`。
  - `SamplingMetadata`：传递处理器引用的桥梁，由引擎构造时从 persistent batch 注入。
  - `SamplingParams`、`VllmConfig`：`AddedRequest` 类型签名中直接消费 `SamplingParams`；`LogitsProcessor` 基类通过 `TYPE_CHECKING` 引用 `VllmConfig`。
- **跨概念依赖**：argmax / argmax-invariant / non-argmax-invariant 三者的判定直接决定了 sampling 的跳过路径，进而耦合到 greedy decoding 行为。

## 【使用方法】
原文未给出对外 CLI、参数或 YAML 配置项；启用方式仅在内部编程模型层面给出契约性方法：

- **抽象基类需要实现的钩子**（原文出现于正文及截断的伪代码）：`update_state(batch_update: BatchUpdate)` 与 `apply(logits)`（可原地修改以省内存，亦可返回新张量）；以及（被前文援引但因原文截断未完整呈现）`LogitsProcessor` 基类签名。
- **注册位置**：处理器被放入 `InputBatch` 上的 `self.logitsprocs.all`，并按是否改变 argmax 分别归入 `non_argmax_invariant` / `argmax_invariant` 两个分组（具体注册 API 在本文档内未列示）。
- **使用位置**：在 `SamplingMetadata` 构造时被绑定；调用方为 `Sampler.forward` / `Sampler.sample`。
- **示例处理器**：正文仅举例 "Min-P"（作为 argmax-invariant 的代表）以及"在某步后强制仅保留 EOS"（作为 non-argmax-invariant 的代表），未给出可执行命令或配置文件片段。

> 文档开篇即声明："Some logits processors design changes are still in progress and the API may change in the near future"，故具体启用细节以 `../features/custom_logitsprocs.md` 为准。
