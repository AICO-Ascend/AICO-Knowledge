# KVAllGather长序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/kvallgather-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/kvallgather-context-parallel.md

# mindspeed 文档解读 · KVAllGather 长序列并行

## 【定位】

这篇文档面向长序列训练场景中"序列维度无法被数据/张量/流水线并行切分、且注意力显存随序列长度呈二次增长"的痛点，介绍 mindspeed 中通过在注意力计算前对分片 K/V 做 all-gather 来实现序列维度并行的 **KVAllGather 长序列并行** 特性，并给出启用该特性的参数、约束与适用场景。

## 【技术要点】

1. **问题本质**：现有数据并行、张量并行、流水线并行均无法在序列维度上切分；当序列维度 $S$ 增长时，训练显存开销按 $O(S^2)$ 速度上升（原文表述）。
2. **核心做法**：各计算设备在序列维度上各持一段样本；进入注意力计算前，对已分片的 key 和 value 执行 all-gather，使每个设备都拿到**完整**的 K/V 序列；随后每个设备用本地 query 与完整 K/V 做注意力计算。
3. **算法出处**：方案源自 Llama 3 论文第 3.3.2 节（`The Llama 3 Herd of Models`，arxiv 2407.21783）。
4. **通用性**：对各类 attention mask 约束较少；与 FlashAttention 完全兼容，且文档中标注**当前已默认启用 FlashAttention** 进行加速。
5. **特别受益场景**：GQA（Grouped-Query Attention）、MQA（Multi-Query Attention）下，对 K/V 做 all-gather 的通信耗时远小于整体注意力计算时间，因此收益更显著。
6. **强制依赖与约束**：必须同时设置 `--transformer-impl transformer_engine`；目前仅支持 `--attention-mask-type causal`；序列长度需满足特定整除关系（见使用方法节）。

## 【关键机制与数据】

**工作原理（数据流三步走，原文叙述）**：

- 步骤 1：各设备在序列维度上分别持有不同片段的输入样本。
- 步骤 2：进入注意力计算前，对已分片的 key 与 value 执行 all-gather 通信，使每个设备获得**完整**的 K/V 序列。
- 步骤 3：每个设备用本地 query 配合完整 K/V 完成注意力计算，得到对应输出。

**关键性能/开销数据（原文逐字引用）**：

- 原文：序列维度增长时，训练内存开销会以 $O(S^2)$ 的速度增长。
- 原文：相比不开启序列并行，**单步耗时增加**；相比重计算，**计算效率提升**。
- 原文定性结论：利用多设备并行切分输入序列，**降低单设备内存消耗**。
- 原文定性结论：GQA/MQA 场景下，K/V all-gather 通信时间"远少于"整体计算时间，因此方案收益更为显著。

> 说明：原文未给出具体的倍数、百分比、吞吐或显存数字，本节仅引用其定性结论，不臆造数据。

## 【表格解读】

原文在"使用方法"节给出一张参数配置表，下面**逐字还原**后再逐行解读：

| 重要参数 | 参数说明 |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `--context-parallel-size [int]` | 开启CP对应的数量，默认为1（不开启并行），需设置大于1才会开启并行，根据用户需求配置。 |
| `--context-parallel-algo kvallgather_cp_algo` | 长序列并行算法选项，设置为`kvallgather_cp_algo`，开启KVAllGather长序列并行。 |
| `--seq-length [int]` | 输入序列的长度。 |

**逐行解读**：

- `--context-parallel-size [int]`：上下文并行（CP）的进程/设备数。默认值为 1，即关闭序列并行；只有显式设置为大于 1 的整数时，特性才会真正生效，具体取值由用户按硬件规模与序列长度决定。
- `--context-parallel-algo kvallgather_cp_algo`：上下文并行算法选择器。要启用本文方案，需将该参数显式指定为 `kvallgather_cp_algo`；若使用其它算法选择，则不走 KVAllGather 路径。
- `--seq-length [int]`：输入序列总长度。它不是并行开关，而是与 CP 切分配合使用的输入尺寸信息，并参与下方"注意事项"中的整除约束判断。

## 【公式解读】

原文仅出现一处数学表达式，且为行内叙述形式（LaTeX 风格）：

$$O(S^2)$$

**逐符号解释**：

- $O(\cdot)$：大 O 记号，用于描述**渐进复杂度上界**。此处表示随输入规模增长，某项资源消耗的增长阶。
- $S$：**序列维度（sequence length）**的大小，来源于原文"当序列维度(S)增长时"的措辞。
- 整体含义：在注意力计算中，与序列相关的中间状态（如 attention matrix）通常与 $S$ 的平方成正比，因此当 $S$ 增大时显存开销以**平方级**增长，构成传统方案在长序列下不可扩展的根本原因，也正是 KVAllGather 要去缓解的问题。

> 文档未给出其它公式（如切分比例、通信量计算等），故仅保留此一处。

## 【关联】

文档正文未提供内部链接，但通过上下文可识别出本文与以下概念/模块存在强耦合关系：

- **Llama 3 论文 Section 3.3.2**：本文 KVAllGather 方案的理论出处（arxiv 2407.21783）。
- **FlashAttention**：被显式声明"完全兼容"且"目前已默认启用"，因此本特性的实际加速效果依赖 FlashAttention 内核。
- **GQA（Grouped-Query Attention）/ MQA（Multi-Query Attention）**：被点名为本方案收益最显著的场景，因为 K/V head 数量少使得 all-gather 通信量相对计算量更小。
- **transformer_engine（TE）**：通过"注意事项"中的强约束 `--transformer-impl transformer_engine` 体现——未启用 TE 时本特性不被支持，说明底层 attention 实现位于 TE 生态中。
- **attention-mask-type causal**：唯一被允许的 attention mask 类型，限定了本特性的适用范围。
- **EOD Reset 训练场景**：在"注意事项"中与"定长 padding 训练场景"并列出现，两种训练数据组织方式对应不同的序列切分策略与不同的整除约束。

## 【使用方法】

**启用命令（原文逐字列出）**：

- `--context-parallel-size [int]`：默认 1；需设置为大于 1 的整数以真正开启 CP。
- `--context-parallel-algo kvallgather_cp_algo`：显式赋值为 `kvallgather_cp_algo` 才会走 KVAllGather 路径。
- `--seq-length [int]`：输入序列长度。

**额外约束（来自"注意事项"，必须同时满足）**：

1. 必须同时设置 `--transformer-impl transformer_engine`，否则特性不支持。
2. 当前仅支持 `--attention-mask-type` 为 `causal`。
3. **定长 padding 训练场景**：采用**负载均衡的序列切分方式**；`--seq-length` 要求能被 `2 * context-parallel-size` 整除。
4. **EOD Reset 训练场景**：采用**常规序列切分方式**；`--seq-length` 要求能被 `context-parallel-size` 整除。

> 备注：文档原文未提供具体启动脚本示例、YAML/JSON 配置片段或环境变量，因此本节以"参数 + 约束"形式呈现，未额外补充任何原文中不存在的命令。
