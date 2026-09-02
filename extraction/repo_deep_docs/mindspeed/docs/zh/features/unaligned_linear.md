# unaligned linear 非对齐线性层

> 仓 `mindspeed` · 路径 `docs/zh/features/unaligned_linear.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/unaligned_linear.md

【定位】
本文档描述 mindspeed 中"非对齐线性层（unaligned linear）"特性——在类 Megatron-LM 框架的 Tensor Parallelism（TP）场景下，解决"序列长度"和"注意力头数"无法被 TP 整除时报错的问题，使原本因整除校验失败而无法启动的训练任务得以运行。

【技术要点】
- 序列切分策略：当 `seq_len % tp_size ≠ 0` 时，采用非 pad 的分配方案，索引小于 `(seq_len % tp_size)` 的 TP 卡分到 `(seq_len // tp_size + 1)` 长度，其余分到 `(seq_len // tp_size)` 长度。
- 头数切分策略（针对 MHA）：当 `num_attention_heads % tp_size ≠ 0` 时，索引小于 `(num_attention_heads % tp_size)` 的 TP 卡分到 `(num_attention_heads // tp_size + 1)` 个头，其余分到 `(num_attention_heads // tp_size)` 个头。
- GQA 适配：对于 GQA 结构模型，权重切分与注意力头切分按 `num_query_groups` 比例分配（原文未给出具体公式）。
- 权重形状联动：注意力相关权重（qkv_weight、dense_weight）按照各 TP 卡实际分配到的头数/序列长度进行切分，不再是均匀切分。
- 启用方式：在训练脚本中追加 `--unaligned-linear` 参数；不支持与 `--use-legacy-models` 同时开启。
- 功能边界：不支持 mc2、2D 张量并行、CP 特性（要求 `TP*CP` 能被注意力头数整除）；结构上仅适配 MHA、GQA，暂不支持 MOE、MLA。

【关键机制与数据】
- 工作原理（原文）：通过自定义的序列/头分配策略代替原来的"pad 到 TP 整数倍"和"强制整除"两种做法；权重按各 TP 卡实际拿到的头/序列数做不等分切分，使各卡权重形状不同但总和与原始张量等价。
- 数据流（原文）：
  1. seq_len=1026、tp_size=4 → tp0、tp1 各分配 257 条序列；tp2、tp3 各分配 256 条。
  2. num_attention_heads=25、tp_size=4（MHA） → tp0 分配 7 个头；tp1、tp2、tp3 各分配 6 个头。
  3. 对应权重：hidden_size=3200 时，qkv_weight 原形状 (9600, 3200)、dense_weight 原形状 (3200, 3200)；tp0 的 qkv=(2688, 3200)、dense=(3200, 896)；tp1/tp2/tp3 的 qkv=(2304, 3200)、dense=(3200, 768)。
- 性能数据（原文）：原文未提供 benchmark 数字，仅定性指出"各 TP 处理的注意力头数、序列长度不一致，会带来负载不均衡"，建议在模型结构设计与超参优化时考虑该影响。

【表格解读】
原文无表格。

（说明：原文以正文举例的方式给出了 seq_len=1026/tp=4 的序列分配、以及 num_attention_heads=25/tp=4、hidden_size=3200 的权重切分尺寸，这些是叙述性举例而非表格，故按要求标注"原文无表格"。）

【公式解读】
原文中给出的不是严格意义上的数学公式，而是 Python 风格的整数运算表达式，逐字保留如下：

1. 序列分配条件与长度
   - 条件索引：`idx < (seq_len % tp_size)`
   - 较长段长度：`L_long = seq_len // tp_size + 1`
   - 较短段长度：`L_short = seq_len // tp_size`
   符号含义：`seq_len` 为总序列长度；`tp_size` 为张量并行度；`//` 为整除；`%` 为取模；`idx` 为当前 TP 卡的 rank 索引。作用：让余数个卡多拿 1 条序列，从而不借助 pad 也能精确覆盖全部序列。

2. 注意力头分配（MHA）
   - 条件索引：`idx < (num_attention_heads % tp_size)`
   - 较多头数：`H_long = num_attention_heads // tp_size + 1`
   - 较少头数：`H_short = num_attention_heads // tp_size`
   符号含义：`num_attention_heads` 为注意力头总数；其余同上。作用：按头数余数把多余的头分给前面几张卡。

3. 权重形状（以 num_attention_heads=25、tp_size=4、hidden_size=3200 为例）
   - 头维度：`head_dim = hidden_size / num_attention_heads = 3200 / 25 = 128`
   - tp0（7 头）qkv 输出维度：`3 * 7 * 128 = 2688`，故 qkv_weight 形状 `(2688, 3200)`
   - tp0 dense 输出维度：`7 * 128 = 896`，故 dense_weight 形状 `(3200, 896)`
   - tp1/tp2/tp3（6 头）qkv 输出维度：`3 * 6 * 128 = 2304`，故 qkv_weight 形状 `(2304, 3200)`
   - tp1/tp2/tp3 dense 输出维度：`6 * 128 = 768`，故 dense_weight 形状 `(3200, 768)`
   符号含义：`hidden_size` 为隐藏层维度；`qkv_weight` 形状 `(out, in)`，`out = 3 * 头数 * head_dim`，`in = hidden_size`；`dense_weight` 形状 `(out, in)`，`out = 头数 * head_dim`，`in = hidden_size`。作用：把权重按各卡实际持有的头数做不等分切分。

4. GQA 权重切分（原文）
   - 原文表述："对于 GQA 结构模型，权重切分和注意力头切分按 `num_query_groups` 比例分配"。
   符号含义：`num_query_groups` 为查询组（即 KV 头）数量。作用：将 q 与 k/v 的切分按 KV 组与 Q 头的对应比例进行，保证 GQA 共享 KV 的约束不被破坏。

【关联】
- 与 Megatron-LM TP 范式的关系：该特性是对标准 TP "seq_len 必须整除 TP、num_attention_heads 必须整除 TP"约束的补充，与 pad 方案并列存在（本文方案不走 pad）。
- 与 CP（Context Parallel）的关系：原文明确不支持与 CP 同时开启，并给出约束 `TP*CP` 需被注意力头数整除；这意味着 CP 仍依赖原 Megatron 风格的整除校验，二者不能叠加。
- 与 2D 张量并行、mc2 的关系：原文列出两者均不兼容。
- 与 `--use-legacy-models` 的关系：原文明确不能在 legacy 分支使用（非对齐线性层不支持 legacy 模型路径）。
- 与模型结构的适配关系：当前已覆盖 MHA、GQA（含 `num_query_groups` 切分规则），尚未覆盖 MOE、MLA——意味着 MOE/MLA 模型若出现非整除情况，仍需走原 TP 校验，无法用此特性绕过。

【使用方法】
- 启用命令（原文）：在训练脚本的命令行参数中加入 `--unaligned-linear`，示例原文逐字如下：
  ```bash
  # 开启非对齐线性层
  --unaligned-linear
  ```
- 约束（原文）：仅添加该参数即可启用，但需遵守以下限制——非对齐会引发各 TP 负载不均衡；不支持 mc2、2D 张量并行、CP；已适配 MHA、GQA，暂不支持 MOE、MLA；不能与 `--use-legacy-models` 同时开启。
- 其他配置项（原文未涉及除 `--unaligned-linear` 之外的额外开关、环境变量或配置文件项）。
