# Allgather Dispatcher 分支优化

> 仓 `mindspeed` · 路径 `docs/zh/features/megatron_moe/megatron-moe-allgather-dispatcher.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-allgather-dispatcher.md

# mindspeed — Allgather Dispatcher 分支优化 · 一体化深度解读

---

## 【定位】

本文档聚焦 Megatron MoE 中 Allgather dispatcher 分支的两个性能瓶颈（gather/scatter 随机访存、permute 开头三次串行 allgather 通信），分别通过"逐元素→逐行等价替换"与"异步通信重排"两个手段进行优化，端到端提升 MoE 模型训练吞吐。

---

## 【技术要点】

1. **算子替换背景**：Megatron MoE 的 Allgather 分支原本用 `torch.gather` / `scatter` 沿 dim 轴做"按索引逐元素取值/赋值"，因索引扩展后产生大量随机地址，对性能造成显著影响。
2. **逐元素→逐行等价替换**：利用 `expand(-1, hidden_states.shape[-1])` 后每一行内容一致的特性，把 `gather`/`scatter` 替换为对行操作的 `index` / `indexput` 算子，避免随机访存。
3. **异步通信重排**：`permute` 函数开头会对 `hidden_states`、`max_ind`、`max_prob` 三个张量分别做 allgather，原文指出"这些操作为串行操作，但各计算任务之间并非串行依赖关系"，因此可通过 `async=True` 异步下发实现通信与计算并行。
4. **使用场景约束**：仅当部署 Mcore MoE（Mixture of Experts）架构并启用 `--moe-token-dispatcher-type allgather` 时生效。
5. **启用参数**：通过 `--moe-permutation-async-comm` 开关开启。
6. **性能收益**：原文给出"类 DeepSeek-V2 的 MoE 模型，端到端训练吞吐提升约 **10%**"。

---

## 【关键机制与数据】

- **gather/scatter 性能损耗机理**（原文）：索引经 `expand` 后"每一行中的内容都是一致"，逐元素随机取值/赋值产生大量随机地址访存，因此可安全地降维到"按行"粒度。
- **等价替换形式**（原文伪代码）：
  ```python
  self.global_local_map = global_local_map.view(-1, 1).expand(-1, hidden_states.shape[-1])
  local_hidden_states = torch.gather(global_hidden_states, 0, self.global_local_map)
  ```
  原方案为逐元素；优化后改为 `index` / `indexput` 逐行操作，对 `gather`/`scatter` 作等价替换（原文未给出替换后的具体调用写法，故不臆造）。
- **通信并行化机制**（原文）：在 `permute` 入口对 `hidden_states`、`max_ind`、`max_prob` 三段 allgather 进行任务重排序，并附 `async=True` 参数异步下发，使通信与计算流水并行。
- **数据流概览**（基于原文信息整合）：
  - 输入：`global_hidden_states`、`global_local_map` → 通过索引映射得到 `local_hidden_states`；
  - 通信侧：`hidden_states`/`max_ind`/`max_prob` 三段 allgather 经异步化后可与后续计算交叠。
- **性能数据**（原文）：类 DeepSeek-V2 MoE 模型，"采用上述优化措施后，端到端训练吞吐提升约 10%，相同训练步数下的墙钟时间相应缩短。" 原文未提供具体训练步数、batch size 或硬件配置等数字。

---

## 【表格解读】

**原文无表格。**

（文档未包含任何参数表、性能对比表或配置表，所有信息以叙述方式给出。）

---

## 【公式解读】

原文给出的是一段 Python 等价调用伪代码，而非数学公式，但其形式上可视为"原 gather 写法的形式化表达"，逐字保留并解读如下：

```python
self.global_local_map = global_local_map.view(-1, 1).expand(-1, hidden_states.shape[-1])
local_hidden_states = torch.gather(global_hidden_states, 0, self.global_local_map)
```

符号/语句含义：

- `global_local_map`：全局到本地的映射索引（形状 `(N,)`），`view(-1, 1)` 将其变为列向量以适配后续广播；
- `.expand(-1, hidden_states.shape[-1])`：在最后一维扩展为与 `hidden_states` 等宽，使同一行索引可被广播到该行所有列；
- `torch.gather(global_hidden_states, 0, self.global_local_map)`：沿 dim=0（行维度）按 `global_local_map` 选取行，构成 `local_hidden_states`；
- 关键性质：扩展后的 `global_local_map` "每一行内容一致"，因此可由"逐元素 gather"等价降级为"逐行 index"，这是算子替换可行性的形式化根据。

原文未涉及数学公式（LaTeX），故数学公式层面写为"原文无公式"。

---

## 【关联】

- **所属模块**：Megatron MoE 中的 **Allgather dispatcher 分支**（与 alltoall dispatcher 形成对比，但本文未展开 all-toall 路径）。
- **触发条件**：与 `--moe-token-dispatcher-type allgather` 配套；该开关决定了 token dispatch 的通信拓扑，从而决定是否走 Allgather 分支。
- **作用函数**：在 `permute` 函数开头进行通信重排，影响 `hidden_states`、`max_prob`、`max_ind` 三类张量的 allgather 调度。
- **架构前置**：仅对部署 **Mcore MoE（Mixture of Experts）** 架构的深度学习模型生效。
- **对比/同类**：文末"内部链接: (无)"，未给出文档间跳转关系；仅在背景中提及 `gather`/`scatter` 与 `expand`/`index`/`indexput` 等算子层面的对照。

---

## 【使用方法】

- **触发场景**：部署 Mcore MoE 架构 + 启用 `--moe-token-dispatcher-type allgather`。
- **启用开关**：在训练命令中加入参数 **`--moe-permutation-async-comm`**。
- **其他配置项**：原文未涉及额外环境变量、配置项或示例启动命令。
