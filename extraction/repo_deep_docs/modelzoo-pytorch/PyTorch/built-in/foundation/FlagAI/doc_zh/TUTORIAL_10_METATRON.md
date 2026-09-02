# 转化一个模型为Megatron-LM的模型并行版本

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_10_METATRON.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_10_METATRON.md

# 深度解读：FlagAI 教程 10 — 转化为 Megatron-LM 模型并行版本

---

## 【定位】

这篇文档解决的是**如何将一个普通 Transformer 模型（FlagAI 已支持 BERT、GLM、GPT2、T5）手动改写为 Megatron-LM 张量模型并行（Tensor Model Parallel）版本**的问题——具体落在 MLP、Self-Attention、Cross-Attention 三大组件里的 Linear 层如何替换为 `ColumnParallelLinear` / `RowParallelLinear` 这两类并行算子。

---

## 【技术要点】

1. **支持范围**：FlagAI 基于从 Megatron-LM 抽取的 `mpu` 模块，已实现 BERT、GLM、GPT2、T5 四类模型的张量并行；本文围绕这三个组件给出"先列后行（Column-then-Row）"拆分模式的标准范式。
2. **MLP 层切分**：将 `hidden_size → 4*hidden_size → hidden_size` 的两段式全连接，替换为 `ColumnParallelLinear(hidden_size, 4*hidden_size)` + `RowParallelLinear(4*hidden_size, hidden_size)`，前者在最后一次维度切分并保留分片（`gather_output=False`，原文注释"这里可以是 True"），后者要求输入已是并行形式（`input_is_parallel=True`）。
3. **Self-Attention 的 QKV 投影**：用一个 `ColumnParallelLinear(hidden_size, 3*hidden_size, stride=3, gather_output=False)` 一次性产生 q、k、v；输出 `dense` 用 `RowParallelLinear(hidden_size, hidden_size, input_is_parallel=True)`。若启用相对位置编码，再追加一个 `ColumnParallelLinear(hidden_size, hidden_size, gather_output=False)` 用于 `relative`。
4. **Cross-Attention 的 Q 与 KV 分离投影**：query 单独走 `ColumnParallelLinear(hidden_size, hidden_size)`；key 与 value 合用一个 `ColumnParallelLinear(hidden_size, 2*hidden_size, stride=2, gather_output=False)`；输出 `dense` 仍为 `RowParallelLinear(hidden_size, hidden_size, input_is_parallel=True)`。
5. **并行维度派生参数**：通过 `get_model_parallel_world_size()` 拿到 `world_size`，并据此计算 `hidden_size_per_partition = hidden_size / world_size`、`hidden_size_per_attention_head = hidden_size / num_attention_heads`、`num_attention_heads_per_partition = num_attention_heads / world_size`，三者即决定头维与隐层维如何按卡划分。
6. **代码落位**：MLP 切分逻辑位于 `flagai/model/layers/embeddings_mpu.py`；注意力（含 self / cross）切分逻辑位于 `flagai/model/layers/attentions_mpu.py`。

---

## 【关键机制与数据】

**工作原理（原文逻辑复述）**：文档遵循 Megatron-LM 的"先列后行"切分原则——

- **Column-parallel 阶段**：沿输出通道维度把权重矩阵按列切到各卡，每张卡只持有整体输出的一个分片；为避免在阶段末尾做一次 all-gather，`gather_output=False` 让输出保留分布式张量形式传递给下一算子。
- **Row-parallel 阶段**：沿输入通道维度把权重矩阵按行切到各卡，输入本身已是分布式张量（`input_is_parallel=True`），因此每张卡在自身局部完成矩阵乘后，只需做一次 `all-reduce` 求和即得完整输出，避免在阶段开头引入重复通信。

**数据流示意（按原文三段式还原）**：

- **MLP**：hidden_states →（Column：h→4h，列切）→ GELU →（Row：4h→h，行切）→ output。
- **Self-Attention**：hidden_states →（Column：h→3h，stride=3 列切）→ q,k,v → attention 计算（含可选 `relative` 列切）→ dropout →（Row：h→h，行切）→ output。
- **Cross-Attention**：hidden_states → query 走 Column（h→h），context 走 key_value 合并的 Column（h→2h, stride=2）→ attention → dropout → Row（h→h）→ output。

**性能数据**：原文未给出任何关于吞吐量、加速比、通信开销、显存收益或基准测量的数字；Dropout 层注释仅说明"不同并行分区上单次迭代输出会有差异，但平均上应不依赖分区"，这是一条语义说明，并非性能数据。

---

## 【表格解读】

原文无表格。所有参数都嵌在代码块中以构造函数入参的形式给出（详见下一节【公式解读】中对每一段代码的逐字保留）。

---

## 【公式解读】

原文无独立公式块。文档以 **Python 代码 + 构造函数签名** 的形式承载公式含义，下面**逐字保留原式**并解读每个参数的语义（在原文中以代码形式出现，故按代码算式逐项还原）：

**(a) MLP forward（原文：先列后行拆分）**

```python
intermediate_parallel = self.dense_h_to_4h(hidden_states)
intermediate_parallel = gelu(intermediate_parallel)
output = self.dense_4h_to_h(intermediate_parallel)
```

- `self.dense_h_to_4h`：Column 投影，把 `hidden_size` 维映射到 `4 * hidden_size` 维，按输出通道切分到各卡。
- `gelu`：非线性激活，原文未指定实现，按 FlagAI 默认即可。
- `self.dense_4h_to_h`：Row 投影，把 `4 * hidden_size` 维映射回 `hidden_size` 维，按输入通道切分。

**(b) `dense_h_to_4h` 构造（原式）**

```python
self.dense_h_to_4h = ColumnParallelLinear(hidden_size,
                                          4 * hidden_size,
                                          gather_output=False,
                                          init_method=init_method)
```

- `hidden_size`：输入维度；`4 * hidden_size`：输出维度（Transformer MLP 中间层典型 4 倍扩展）。
- `gather_output=False`：保持输出为各卡的列分片，避免列并行末尾做 all-gather。
- `init_method`：权重初始化方法。

**(c) `dense_4h_to_h` 构造（原式）**

```python
self.dense_4h_to_h = RowParallelLinear(
    4 * hidden_size,
    hidden_size,
    input_is_parallel=True,
    init_method=output_layer_init_method)
```

- `4 * hidden_size → hidden_size`：将 MLP 中间表示复原到隐藏层尺寸。
- `input_is_parallel=True`：声明其输入已是 Column 阶段输出的列分片（与 `dense_h_to_4h.gather_output=False` 配套，原文原话）。
- `init_method=output_layer_init_method`：使用输出层专用初始化。

**(d) 关键派生参数（原式）**

```python
world_size = get_model_parallel_world_size()
self.hidden_size_per_partition = divide(hidden_size, world_size)
self.hidden_size_per_attention_head = divide(hidden_size,
                                             num_attention_heads)
self.num_attention_heads_per_partition = divide(
    num_attention_heads, world_size)
```

- `world_size`：张量并行进程数（来自 `mpu`）。
- `hidden_size_per_partition`：每张卡持有的隐层维度大小，等于 `hidden_size / world_size`。
- `hidden_size_per_attention_head`：单个注意力头对应的隐层维度，等于 `hidden_size / num_attention_heads`。
- `num_attention_heads_per_partition`：每张卡上分配的注意力头数，等于 `num_attention_heads / world_size`。

**(e) Self-Attention QKV + 相对位置 + 输出（原式）**

```python
self.query_key_value = ColumnParallelLinear(hidden_size,
                                            3 * hidden_size,
                                            stride=3,
                                            gather_output=False,
                                            init_method=init_method)
if relative_encoding:
    self.relative = ColumnParallelLinear(hidden_size,
                                         hidden_size,
                                         gather_output=False,
                                         init_method=init_method)
self.attention_dropout = torch.nn.Dropout(attention_dropout_prob)
self.dense = RowParallelLinear(hidden_size,
                               hidden_size,
                               input_is_parallel=True,
                               init_method=output_layer_init_method)
```

- `query_key_value`：单层 `ColumnParallelLinear(hidden_size, 3*hidden_size, stride=3, gather_output=False)` 一次性投影出 q/k/v 三组，`stride=3` 揭示每张卡分得三组（q,k,v）连续块中各一份。
- `self.relative`：可选的相对位置编码投影，同样为 Column 切分。
- `attention_dropout`：标准 Dropout（原文注释明确"单次迭代在不同分区上输出不同，但平均上不依赖分区"）。
- `self.dense`：Self-Attention 的输出投影，Row 切分，输入已是并行形式。

**(f) Cross-Attention query、key_value、output（原式）**

```python
self.query = ColumnParallelLinear(hidden_size,
                                  hidden_size,
                                  gather_output=False,
                                  init_method=init_method)
self.key_value = ColumnParallelLinear(hidden_size,
                                      2 * hidden_size,
                                      stride=2,
                                      gather_output=False,
                                      init_method=init_method)
self.attention_dropout = torch.nn.Dropout(attention_dropout_prob)
self.dense = RowParallelLinear(hidden_size,
                               hidden_size,
                               input_is_parallel=True,
                               init_method=output_layer_init_method)
```

- `self.query`：来自解码端 hidden_states 的查询投影，Column 切分 `hidden_size → hidden_size`。
- `self.key_value`：合并 key 与 value，单层 `ColumnParallelLinear(hidden_size, 2*hidden_size, stride=2)`，`stride=2` 与 qkv 三合一时的 `stride=3` 同构。
- `self.dense`：Cross-Attention 输出投影，Row 切分。
- `attention_dropout`：同(e)，原文复读了"在不同分区上输出不同，但平均上应不依赖分区"这一注释。

---

## 【关联】

文档自述其改写范式"主要操作都是从 Megatron-LM 中拿出来的，放在了 mpu 模块中"，因此本教程与以下上下游构成关系链：

- **上游 / 算子来源**：`mpu` 模块（即 Megatron-LM 移植进 FlagAI 的张量并行层），提供 `ColumnParallelLinear`、`RowParallelLinear`、`get_model_parallel_world_size()` 等 API。
- **下游 / 应用模型**：本文明确点名的四个模型——BERT、GLM、GPT2、T5——其张量并行版本均依赖本文所示的"MLP / Self-Attention / Cross-Attention 三段式"改造范式。
- **代码协同**：`flagai/model/layers/embeddings_mpu.py`（MLP 切分，Section 1 锚点）与 `flagai/model/layers/attentions_mpu.py`（自注意力 + 交叉注意力切分，Section 2、3 锚点）共同实现了文档所述改造。
- **目录上下文**：作为 `TUTORIAL_10`（编号来自本文 Markdown 锚点列），它属于 FlagAI 教程序列中的一篇，与同目录下的其他 TUTORIAL 形成"模型并行如何实现"这一独立模块；本篇不直接调用其他教程，但凡是希望把新模型接入 FlagAI 张量并行的用户，都需要并行参考此篇。

> 文末内部链接标注为"无"——本文档未显式给出任何内部超链接，仅依赖 Markdown 锚点定位自身三个章节。

---

## 【使用方法】

原文未提供完整的"启用命令、启动脚本或 yaml 配置"，但给出了**实现侧**的接入方法，按原文逐条整理如下：

1. **确定改造目标组件**：在你的模型实现里定位 MLP、Self-Attention、可选的 Cross-Attention 三处的 `Linear` 层（按 Section 1/2/3 顺序处理）。
2. **导入并行算子**：从 FlagAI 移植自 Megatron-LM 的 `mpu` 模块导入 `ColumnParallelLinear`、`RowParallelLinear` 以及 `get_model_parallel_world_size()`。
3. **按 Section 1 改造 MLP**：
   - 将第一层 `nn.Linear(hidden_size, 4*hidden_size)` 替换为 `ColumnParallelLinear(hidden_size, 4*hidden_size, gather_output=False, init_method=init_method)`。
   - 将第二层 `nn.Linear(4*hidden_size, hidden_size)` 替换为 `RowParallelLinear(4*hidden_size, hidden_size, input_is_parallel=True, init_method=output_layer_init_method)`（输入并行性要与上一层 `gather_output=False` 配套）。
   - 在 `__init__` 中按原式计算 `hidden_size_per_partition`、`hidden_size_per_attention_head`、`num_attention_heads_per_partition`。
4. **按 Section 2 改造 Self-Attention**：
   - 将 Q、K、V 三个 `Linear` 合并或保留为单个 `ColumnParallelLinear(hidden_size, 3*hidden_size, stride=3, gather_output=False, ...)`。
   - 若启用相对位置编码，追加 `ColumnParallelLinear(hidden_size, hidden_size, gather_output=False, ...)`。
   - 输出 `dense` 替换为 `RowParallelLinear(hidden_size, hidden_size, input_is_parallel=True, init_method=output_layer_init_method)`。
5. **按 Section 3 改造 Cross-Attention**：
   - `query` 替换为 `ColumnParallelLinear(hidden_size, hidden_size, gather_output=False, ...)`。
   - `key` 与 `value` 合用 `ColumnParallelLinear(hidden_size, 2*hidden_size, stride=2, gather_output=False, ...)`。
   - 输出 `dense` 同样替换为 `RowParallelLinear(hidden_size, hidden_size, input_is_parallel=True, ...)`。
6. **运行/分布式启动命令**：原文未涉及分布式启动命令、并行度设置开关、环境变量或训练入口脚本，需要结合 FlagAI 同目录下其他教程与 `mpu` 模块自身的初始化约定使用。
