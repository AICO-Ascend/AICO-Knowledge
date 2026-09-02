# Double Ring Attention长序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/double-ring.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/double-ring.md

# 深度解读:Double Ring Attention 长序列并行

## 【定位】
本文档描述 mindspeed 中基于 Ring Attention 进一步演进的 **Double Ring Attention** 算法能力,旨在通过双环结构解决极长序列训练中头并行(Head Parallelism)可扩展性受限与上下文并行(Context Parallelism)P2P 通信效率低的双重瓶颈,为已开启 Ring Attention 的训练场景提供一种通过 `--cp-window-size` 参数即可开启的性能优化开关。

## 【技术要点】

1. **算法定位与学术来源**:Double Ring Attention 是对原始 Ring Attention 算法的加速延伸,算法细节参见原文论文 *LoongTrain: Efficient Training of Long-Sequence LLMs with Head-Context Parallelism* (arXiv 2406.18485)。
2. **双重瓶颈刻画**:头并行存在"并行度上限 = 注意力头数"的扩展性天花板;上下文并行采用 P2P 通信原语,导致节点内带宽利用率低、节点间网络资源利用率低,通信与计算难以重叠。
3. **继承的 Ring Attention 核心机制**:借鉴分块 Softmax 原理,跨设备分布序列维度;进程间构建环状通信结构(Ring),每个进程持有一个本地 QKV 块;通过"向后发送、向前获取"KV 块逐块遍历设备环;计算 attention 全程无需数据拼接,理论上支持无限扩展序列长度;本地计算与 KV 通信可掩盖。
4. **Double Ring 的核心思想**:在 Ring Attention 之上引入**分布式注意力 + 双环(Double Ring)结构**,在内层再组织一层环状通信以优化计算与内存使用,这就是 `--cp-window-size` 所控制的"内层窗口"。
5. **核心开关与约束**:`--cp-window-size` 控制内层窗口大小;取值为 1 时回退为原始 Ring Attention,大于 1 时启用 Double Ring Attention;要求 `--context-parallel-size` 必须能被 `--cp-window-size` 整除,且 `--cp-window-size < --context-parallel-size`。
6. **调优经验值(原文实测点)**:Llama2 裁剪模型、32k 序列长度、`--context-parallel-size=16` 且无其他并行切分时,**实测 `--cp-window-size=2` 时性能最优**;窗口继续增大时,通信与计算并发程度更高,但片上内存带宽存在抢占,整体效率可能下降。

## 【关键机制与数据】

**工作机制(原文叙述)**:

- **Ring Attention 基线**:采用分块 Softmax,无需拼回整段序列即可逐块完成 Attention 与 FFN;设备间按环组织,本地 QKV 块固定,KV 块沿环"后发前取"循环传递;理想情况下本地计算与 KV 通信互相掩盖,无额外通信开销;理论上支持无限长序列(无需全局拼接)。
- **Double Ring 演进**:在 Ring Attention 单环之外,**叠加一层内环(分布式注意力)**,使得在更大的上下文并行维度内仍能维持较高的通信-计算重叠度,缓解 P2P 通信中"节点内带宽"与"节点间网络资源"利用率低的问题。

**性能/经验数据(原文明确给出)**:

> 原文:Llama2 裁剪模型、序列长度 32k、`--context-parallel-size=16` 且无其他并行切分的场景下,实测内层窗口大小为 2 时性能最优;窗口继续增大,虽通信-计算并发程度更高,但片上内存带宽抢占会导致整体效率下降。

**趋势性结论(原文定性描述,无具体数字)**:

- 头并行的扩展上限受注意力头数约束;
- 上下文并行的 P2P 通信在扩展维度时难以与计算重叠;
- Double Ring 通过双环结构优化计算与内存使用,提升长序列训练效率。

## 【表格解读】

**原文表格逐字还原**:

| 重要参数 | 参数说明 | 是否必选 | 默认值 |
|---|---|---|---|
| `--cp-window-size [int]` | 控制双层 Ring Attention 的内层窗口大小。值为 1 时使用原始算法,值大于 1 时使用 Double Ring Attention 算法,优化原始 Ring Attention 性能。要求 `--context-parallel-size` 必须能被该参数整除。 | 否 | 1 |

**逐行解读**:

- **参数名 `--cp-window-size [int]`**:控制 Double Ring Attention 内层环窗口尺寸的整型参数。
- **参数说明**:精确刻画了"开关"语义——`=1` 即等价于不开启(退化为原始 Ring Attention);`>1` 即启用 Double Ring,以优化原始 Ring 性能。隐含的两个强约束:**整除性**(`--context-parallel-size` 必须能被本参数整除)与**边界性**(实际语境中还需 `<` `--context-parallel-size`,详见原文 NOTE)。
- **是否必选 = 否**:表示这是一个可选的性能调优开关,不开(=1)时仍可正常使用 Ring Attention。
- **默认值 = 1**:默认保持原始 Ring Attention 行为,需用户显式调大才会启用 Double Ring Attention。

## 【公式解读】

原文无公式。

## 【关联】

- **前置依赖特性 — Ring Attention 长序列并行**:文档明确"适用于已开启 Ring Attention 的训练场景,开启方式请参见 [Ring Attention长序列并行](ring-attention-context-parallel.md)"。Double Ring Attention 不是独立特性,而是 Ring Attention 之上的性能增强层;用户必须先具备 Ring Attention(上下文并行)能力,才能在此基础上开启 Double Ring。
- **参数耦合关系**:文档中的核心约束将 Double Ring 与上下文并行维度绑定——`--cp-window-size` 与 `--context-parallel-size` 之间存在整除关系与大小关系,这两项参数应作为一组协同调优。
- **学术来源**:本文档所描述算法取自 *LoongTrain: Efficient Training of Long-Sequence LLMs with Head-Context Parallelism* (arXiv 2406.18485),其同名方法主张"头并行 + 上下文并行"的混合思路,本文档中的 Double Ring 即是该思路在 mindspeed 中的落地形式。

## 【使用方法】

**启用前置**:需先开启 Ring Attention 长序列并行,参见内部链接 `ring-attention-context-parallel.md`。

**启用命令(原文)**:

- 在已开启 Ring Attention 的训练场景下,将 `--cp-window-size` 设置为**大于 1 的整数**,即可开启 Double Ring Attention 算法,优化原始 Ring Attention 性能。
- 取值为 `1` 时回退为原始 Ring Attention 算法(默认行为)。

**强约束(原文 NOTE)**:

1. 需要确保 `--context-parallel-size` 能被 `--cp-window-size` 整除;
2. 需要确保 `--cp-window-size` 小于 `--context-parallel-size`;
3. 内层窗口 `--cp-window-size` 增大时,通信与计算并发程度更高,但片上内存带宽抢占可能使整体效率下降,需结合实际场景调试;原文给出的参考经验值:**Llama2 裁剪模型 + 32k 序列长度 + `--context-parallel-size=16` + 无其他并行切分** 时,`--cp-window-size=2` 性能最优。
