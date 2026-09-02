# Multi-Card Parallelism

> 仓 `mindie-sd` · 路径 `docs/en/features/parallelism.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/parallelism.md

```markdown
# Multi-Card Parallelism —— 深度解读

## 【定位】

本文档系统阐述 MindIE SD 在多卡部署场景下提供的四类并行策略（TP、RSP、USP、CFG Parallel），用于解决单卡显存不足与推理吞吐瓶颈问题，并给出各策略的原理、通信方式、适用场景与代码示例。

## 【技术要点】

1. **Tensor Parallel (TP)**：沿权重矩阵 W 的行或列切分；列切分后通过 **all-reduce** 归约，行切分后通过 **all-gather** 拼接。通信量与 `hidden_size` 成正比；建议仅在单机多卡内使用，TP 度不超过单机 NPU 数。
2. **Ring Sequence Parallel (RSP)**：沿序列维度切分 Q，KV 在设备间以环状 P2P 方式传递；当通信时间 ≤ 计算时间时，可被计算掩盖。需 N 轮通信完成全序列注意力。
3. **Ulysses Sequence Parallel (USP)**：沿序列维度切分输入，attention 前对 Q/K/V 做 **AlltoAll** 重组到 head 维度，各卡并行计算不同 head，attention 后再做一次 AlltoAll 还原序列。约束：**USP 并行度必须能被 FA 的 head num 整除**。
4. **CFG Parallel**：将 positive / negative 两条样本分配到不同设备并行执行，适用于 `CFG > 1` 的扩散模型，通信开销低。
5. **策略组合**：RSP 可与 USP 组合使用，补齐 USP 在 head 数无法整除时的剩余并行度；TP 不推荐作为首选（通信开销大）。
7. **后端与硬件**：分布式后端为 **hccl**；TP 依赖高带宽互联（如 HCCS），建议限制在单机多卡。

## 【关键机制与数据】

- **TP 数据切分维度**：原文给出输入 X=(b, s, h)、权重 W=(h, h')，以 N=2 为示例展示 row-wise 与 column-wise 两种切法，将一次 matmul 转化为两次独立的卡上 matmul，再通过卡间通信（add 或 concat）合并为完整结果。
- **TP 代码示例关键参数（原文）**：`Linear(4096, 4096)`，输入 `x = torch.randn(1, 256, 4096)`，每个 rank 持有 `W[:, h//world_size * rank : h//world_size * (rank+1)]`；列切分后用 `dist.all_reduce(local_out)` 合并。
- **RSP 原理**：Q 分片驻留各卡，attention 计算后第 i 个 device 将 KV 发往 i+1，同时接收 i-1 的 KV，循环 N 轮覆盖所有序列位置。
- **RSP 代码示例关键参数（原文）**：`batch, seqlen, head, dim = 1, 4096, 8, 128`；`seqlen_chunk = seqlen // world_size`；每轮通过 `dist.send_recv` 进行 KV 交换并叠加注意力结果。
- **USP 通信特征（原文）**：核心为 **AlltoAll** 集合通信；当序列长度与设备数同比例放大时，单设备通信量保持恒定（原文注明理论分析见 DeepSpeed Ulysses 论文）。
- **适用偏好（原文）**：USP 与 CFG Parallel 被标注为「推荐首选/低通信开销」；TP 与 RSP 在不同带宽/序列长度条件下表现各异，RSP 适合长序列（seqlen ≫ head_dim），USP 适合 head 多且 AlltoAll 带宽充足的场景。
- **注**：原文末尾关于 USP 与 RSP 的对比被截断（"Compared to RSP, Ulysses is more efficie…"），CFG Parallel 仅在概述章节出现，未提供独立小节、示例或参数。

## 【表格解读】

**原文无表格**。文档仅以图片（`figures/tensor_parallel_image_*.png`、`figures/ring.png`、`figures/ulysses.png`）示意切分与通信结构，未提供任何 markdown 形式的参数表、性能对比表或配置项表。

## 【公式解读】

原文未以标准 LaTeX 形式给出公式，但包含若干可视为公式/伪代码的关键表达式，逐字保留并解释：

1. **维度定义**：`X = (b, s, h)`，`W = (h, h')`
   - 符号含义：`b = batch_size`（批大小），`s = sequence_length`（输入序列长度），`h = hidden_size`（token 向量维度），`h' = W` 的输出隐藏维度。
   - 作用：刻画一次矩阵乘法 `Y = X @ W` 的张量形状，是后续 row/column 切分的输入条件。

2. **TP 列切分后权重索引**：`W[:, h//world_size * rank : h//world_size * (rank+1)]`
   - 符号含义：`world_size` 为参与并行的设备总数，`rank` 为当前设备编号。
   - 作用：定义每个 rank 持有的权重列切片范围，实现 column-wise 切分。

3. **注意力缩放点积**：`score = (q @ k.transpose(-2, -1)) / (dim ** 0.5)`
   - 符号含义：`dim` 即 head_dim，`q`、`k` 为 RSP 示例中的本地 Q/K 分片。
   - 作用：RSP 示例中 `local_attn` 的标准 scaled dot-product attention 计算式。

4. **RSP 通信轮次**：经过 N 轮环式 KV 传递后，所有设备完成全序列位置注意力计算（原文用"N rounds of communication"表述）。
   - 符号含义：N 等于参与并行的设备数（即 `world_size`）。
   - 作用：表明 RSP 的通信轮次与并行度线性相关，通信开销与计算时间可形成掩盖关系。

## 【关联】

- **[supported_matrix.md](supported_matrix.md)**：原文多次指引读者查阅该文件以确认各并行策略在具体模型/硬件上的支持矩阵，是本文档的事实依据与配套索引。
- **[./fa_power_cap.md](../fa_power_cap.md)（目录推断为 `docs/en/features/fa_power_cap.md`）**：与 FlashAttention（FA）相关；USP 段落明确指出 "USP parallelism degree must be divisible by FA's head num"，因此 FA 的 head 数约束直接决定了 USP 的合法并行度选择，二者在 head 维度切分上强耦合。

## 【使用方法】

**TP 使用方式（原文代码示例）**：
1. `dist.init_process_group(backend="hccl")` 初始化分布式环境；
2. `torch.npu.set_device(f"npu:{os.environ['LOCAL_RANK']}")` 绑定本地 NPU；
3. 对 `nn.Linear` 权重沿 dim=0 做 `chunk(world_size)[rank]` 获取本地切片；
4. 本地 `x @ w_chunk.T` 计算后用 `dist.all_reduce(local_out)` 合并（对应列切分场景）。

**RSP 使用方式（原文代码示例）**：
1. 按 `seqlen // world_size` 切分 Q/K/V 到各卡；
2. 首轮本地 `local_attn(q_chunk, k_chunk, v_chunk)`；
3. 后续 `world_size-1` 轮通过 `dist.send_recv(k_chunk, k_recv, send=(rank+1)%world_size, recv=(rank-1+world_size)%world_size)`（K、V 各做一次）交换 KV 并累加注意力结果。

**USP / CFG Parallel / RSP+USP 组合**：原文未给出具体启用命令、配置项或 API 参数；仅在原理与适用场景章节做了机制描述，相关启用细节需结合 [supported_matrix.md](supported_matrix.md) 及对应框架（vLLM Omni、Diffusers+CacheDit、lightx2v）的并行配置文档确认（原文未涉及）。
```

## 图文联合解读

- `tensor_parallel_image_1.png`: **图文联合解读：**

图中展示了基础矩阵乘法 **X * W = Y** 的张量形状关系：输入 X[b,s,h]、权重 W[h,h']、输出 Y[b,s,h']，橙色/蓝色/绿色三色块对应不同角色，h 为收缩维度。

**技术结论：** 该图揭示了权重矩阵沿 h 与 h' 两个可分维度的切分结构，恰好对应 TP 沿"行或列"切分权重矩阵的两种方式：通过切分 h'（列切分）将输出维度分散到多卡，或切分 h（行切分配合后续通信）分散输入维度，从而实现矩阵计算的分布式拆分。

**与文档关系：** 作为多卡并行文档的视觉锚点，该图为后续介绍 TP（沿权重切分）、USP（沿 s 切分并重排注意力头）等策略提供形状参照——所有并行策略本质上都是对该 XW=Y 表达式中某一维度的重组。
- `tensor_parallel_image_2.png`: 图示将输入X沿h维度切分为X1|X2，权重W对应切分为W1|W2，执行矩阵乘法得到输出γ。论证了Tensor Parallel按权重矩阵行/列切分、多卡分摊矩阵运算的机理，对应文档中"TP沿权重矩阵行列切分、分散矩阵计算"的论点，并呼应其"TP通信开销大、不推荐作为首选"的建议。
- `tensor_parallel_image_3.png`: **图文联合解读：**

图示展示了**张量并行（TP）**的计算流程：将输入 X 沿隐藏维 h 切分到 N 张卡（每卡持有 [b,s,h/N]），权重 W 同步切分为 [h/N,h']，各卡独立完成 X_i × W_i 得到局部结果 Y_i，再合并为完整输出 Y [b,s,h']。

该图论证了 TP 的核心机制——**从权重矩阵维度拆分计算与显存**，单卡仅存储 1/N 的权重，从而缓解显存瓶颈；但合并 Y1↔Y2 的箭头也直观暴露了其固有缺陷：每层都需 AllReduce/Sum 通信，对应文档"通信开销显著，不推荐作为首选"的结论。

整体作为 TP 策略的配图，与 U SP/RSP 形成对比——后者通过切分序列维并隐藏通信，更适合作为首选并行方案。
- `tensor_parallel_image_4.png`: **图解：** 橙色输入张量 X[b,s,h] 与蓝色权重矩阵 W[h,h']（沿列方向经虚线切分为 W1|W2）相乘，输出绿色张量 Y[b,s,h']。每张卡持有部分权重（W1 或 W2），独立计算后再拼接得到完整 Y。

**技术结论：** 该图刻画了**张量并行（TP）的列切分**方案——权重按输出维度拆分到多卡，各卡计算局部结果后拼接，无需跨卡归约即可合并。

**与文档关系：** 直观对应首条 TP 说明（"沿权重矩阵行/列拆分"），同时也呼应"TP 通信开销显著，非首选"的建议：列切分虽然切分直观，但在更大规模场景下仍需结合 USP/RSP 等低开销策略使用。
- `tensor_parallel_image_5.png`: # 图文联合解读

**1) 图示内容：** 展示矩阵乘法X×W=Y的张量并行拆分。橙色X[b,s,h]与蓝色权重W1、W2（各[h,h'/N]）相乘，得到绿色分片结果Y1、Y2 [b,s,h'/N]，最后经拼接箭头合并为完整Y[b,s,h']。

**2) 技术结论：** 演示**列切分**（column-wise split）策略——将权重矩阵沿输出维度h'切为N份，各卡算局部输出后拼接，无需额外通信即可还原完整结果，体现"算后即合"的低开销思路。

**3) 与文档关系：** 对应文档"TP：沿权重矩阵行列切分，分摊矩阵计算"的定义，是该策略的最小计算单元示例；说明TP虽能省显存，但隐含的拼接与分布式计算也是文档中"建议优先选USP"权衡的参照依据。
- `ring.png`: ## 图文联合解读

**图示内容**：四个时间步组成的环形通信示意图。Q0–Q3 四个处理器排列成环，每个节点保存自身 KV 切片（Q_i: N/Pd），并通过环形邻居交换 kv0→kv1→kv2→kv3，使每张卡在不同时步依次持有不同 KV 切片，与本地 Q 完成注意力计算。

**技术结论**：RSP 沿序列维度切分 Q，各卡仅持有 1/P 的 KV，沿环形交换即可让每张卡逐步拼齐全部 KV 完成注意力；通信与计算流水重叠，隐藏开销。

**与文档关系**：对应 "Ring Sequence Parallel" 条目，以可视图佐证其 "KV 环形传递、隐藏通信开销" 的核心机制。
- `ulysses.png`: **图文联合解读：**

**1) 图内容：** 展示 Ulysses Sequence Parallel（USP）的数据流。输入 X[N,d] 与权重 Wq/Wk/Wv 相乘得到局部 Q、K′、V，经首次 AlltoAll 沿 head 维度重排后分发至 P 卡，每卡独立完成 Qh·Khᵀ→softmax→·Vh 的 attention 计算，最终通过第二次 AlltoAll 还原输出 O。

**2) 技术结论：** 论证 USP 通过两次 AlltoAll 完成"序列切分→注意力头切分→还原"的重映射，使各卡仅计算局部 attention 头，通信仅两次集合通信，远低于 TP 的频繁 allreduce。

**3) 与文档关系：** 直观支撑"USP 推荐作为首选"的论点，验证其"低通信开销"特性，并体现"USP 并行度须整除 head num"的约束——即 P 卡各持 d/P 维 head 特征。
- `cfg_parallel.png`: ## 图文联合解读

**1) 图示内容：** 图中展示双卡（Device 0 / Device 1）的CFG Parallel数据流。Device 0走**有条件分支**（cond，带提示词图标），Device 1走**无条件分支**（uncond，空图标），两者并行独立经过Block1–4，各自输出Output1、Output2后，通过**AllGather**汇聚为最终Output。

**2) 技术结论：** CFG Parallel将正/负样本推理拆分到不同设备同步执行，避免单卡串行两倍推理开销；AllGather在末端整合两份潜空间表征，确保CFG融合计算无损。

**3) 与文档关系：** 直观印证文档"Distributes positive and negative sample inference to different devices for parallel execution"论点，凸显其适用于扩散模型的并行加速场景。
- `cfg_fusion.png`: **图文解读：**

**1) 图示内容：** 左侧为CFG并行的两条独立推理路径——`prompt`与`neg_prompt`分别经由各自的DiT Block，再各自输出`pred`；流程中存在红色双向反馈环。右侧通过"Cat等"（拼接/合并）操作将两条分支合并为单一`prompt`→DiT Block→`pred`通路，保留同样的反馈循环结构。

**2) 技术结论：** 图示论证了CFG Parallel并非简单并行——正负样本需在分支末端进行结果合并（Cat），以实现Classifier-Free Guidance的对比引导；合并后可等价压缩为单通路，节省一条DiT Block的显存开销。

**3) 与文档论点关系：** 对应文档中"CFG Parallel将正负样本分发到不同设备并行执行"的策略说明，通过可视化的拆分—合并结构，解释了负向分支存在的必要性（用于生成引导信号）及与正向分支的汇合机制，支撑了多卡并行策略可独立或组合使用的设计思想。
