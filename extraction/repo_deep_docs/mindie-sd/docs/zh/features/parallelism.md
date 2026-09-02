# 多卡并行

> 仓 `mindie-sd` · 路径 `docs/zh/features/parallelism.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/parallelism.md

# 多卡并行（Parallelism）深度解读

## 【定位】

本文档系统描述了 MindIE SD（昇腾亲和多模态加速套件）所提供的多种多卡并行策略（张量并行 TP、环状序列并行 RSP、Ulysses 序列并行 USP、CFG 并行），用于解决单卡显存不足与推理速度瓶颈问题，并给出各策略的原理、通信方式、适用场景及代码示例。

---

## 【技术要点】

1. **张量并行（TP）**：沿权重矩阵的行或列切分；示例中 `linear = torch.nn.Linear(4096, 4096)`，`x = torch.randn(1, 256, 4096)`，按列切分时每个 rank 持有 `W[:, h//world_size * rank : h//world_size * (rank+1)]`，前向后通过 all-reduce 合并结果。约束：**TP degree 不应超过单机 NPU 数量**，依赖高带宽卡间通信（如 HCCS），建议仅在单机多卡范围内使用。

2. **环状序列并行（RSP）**：沿序列维度切分 Q，采用 P2P 通信形成环状结构；示例使用 `batch=1, seqlen=4096, head=8, dim=128`，每轮通过 `dist.send_recv` 同时向 `rank+1` 发送、向 `rank-1` 接收 KV；约束：**通信开销在序列长度远大于 head_dim 时可被计算完全掩盖**，不适用于短序列场景。

3. **Ulysses 序列并行（USP）**：沿序列维度切分输入，在注意力头维度通过 `dist.all_to_all` 完成数据重组；示例 `batch=1, seqlen=4096, hiddensize=512, head=8`，先 `torch.chunk(x, world_size, dim=1)` 切分序列，再两次 all_to_all 完成前向与回收集合，最后 `dist.all_gather` 还原。约束：**Ulysses 的并行度需要能被 FA 的 head num 整除**。

4. **CFG 并行（CFG Parallel）**：将正样本（rank 1，conditioned）和负样本（rank 0，unconditioned）分发到不同设备；示例中 `guidance_scale = 7.5`，正负样本计算完全独立，通信量近似为零；约束：**至少拥有 2 卡富余设备**，设备越多加速越接近 2×。

5. **CFG 融合（CFG Fusion）**：与 CFG 并行不同，CFG 融合在单设备内将正负样本在 batch 维度拼接，一次前向产出两个结果，算子调用次数减半，**不消耗额外设备资源**，适合设备数有限但希望降低单次推理延迟的场景。

6. **FA_Power_Cap 技术**：可通过 `--comm_type 0/1/2` 在 baseline、插入通信、块级注意力三种路径之间切换，详细手动接入步骤参见 `./fa_power_cap.md`。

---

## 【关键机制与数据】

**TP 切分原理（原文）：**
输入 X 维度 = (b, s, h)，参数 W 维度 = (h, h')，其中 b 为 batch_size，s 为 sequence_length，h 为 hidden_size，h' 为参数 W 的 hidden_size。
- 按行切分（N=2）：将权重矩阵按行切分为两半，分别在不同 NPU 上完成矩阵乘，再通过卡间**加法**得到完整结果。
- 按列切分（N=2）：将权重矩阵按列切分为两半，分别在不同 NPU 上完成矩阵乘，再通过卡间**拼接**得到完整结果。
- 通信量与 hidden_size 成正比（原文），设备间带宽充足时通信开销占比随模型增大而降低。

**RSP 原理（原文）：**
将 Q 切分到各设备，计算时各设备计算完当前 KV 对后，将持有的 KV 对发送给下一设备，并继续接收前一设备的 KV 对，形成环状通信结构。**当卡间通信时间 ≤ 计算时间时，通信开销可被计算掩盖**。当设备数为 N 时，经过 N 轮通信后所有设备完成全部序列位置的注意力计算。

**USP 原理（原文）：**
把每个样本在序列维度上分割分配给不同设备；注意力计算前对 Q、K、V 进行 AlltoAll，使每个设备收到注意力头的非重叠子集并行计算；计算完成后再次通过 AlltoAll 按序列维度收集结果。原文引用 DeepSpeed Ulysses 论文分析：**当序列长度和设备数同比例增加时，单设备通信量保持恒定**。

**FA_Power_Cap（原文）：**
可通过 `--comm_type 0/1/2` 在 baseline、插入通信、块级注意力三种路径之间切换。

**CFG 并行原理（原文）：**
对于带噪声图像和文本提示词，模型原本需执行两次串行推理（正样本 + 负样本），每个去噪步骤都需两次前向传播；CFG 并行将两次串行计算合并为一次并行计算，**显著提升推理速度**。设备越多，加速越接近 2×。

**CFG 融合公式（原文代码）：**
```python
noise_pred = output_list[0] + guidance_scale * (output_list[1] - output_list[0])
```

---

## 【表格解读】

**原文无表格。**（原文通过图文（figures/*.png）和代码示例描述原理与流程，未提供参数表、性能对比表或配置项表格。）

---

## 【公式解读】

原文未出现 LaTeX 形式的正式数学公式，但包含若干伪代码与代码层面的算式，逐字保留并解释如下：

### 1. 矩阵乘法维度定义

$$X \in \mathbb{R}^{(b, s, h)}, \quad W \in \mathbb{R}^{(h, h')}$$

- **b**（batch_size）：批次大小
- **s**（sequence_length）：输入序列长度
- **h**（hidden_size）：每个 token 向量的维度
- **h'**：参数 W 的 hidden_size（输出维度）
- 作用：表示一次矩阵乘法的输入与参数维度，是 TP 切分（按行/按列）的基础。

### 2. 张量并行按列切分索引

```python
w_chunk = linear.weight.data.chunk(world_size, dim=0)[rank]
```

- `world_size`：分布式总 rank 数
- `rank`：当前设备编号
- 作用：将 W 沿 dim=0 切分为 `world_size` 份，每个 rank 持有 `W[:, h//world_size * rank : h//world_size * (rank+1)]` 的列分片。

### 3. RSP 局部注意力分数

```python
score = (q @ k.transpose(-2, -1)) / (dim ** 0.5)
return score.softmax(dim=-1) @ v
```

- `q, k, v`：分别为查询、键、值张量
- `dim`：head_dim，用于缩放（标准 Scaled Dot-Product Attention 形式）
- 作用：环状序列并行中每个设备对自身持有的 Q 与接收到的 K、V 片段做标准注意力计算。

### 4. RSP 环状通信收/发 rank 计算

```python
send_rank = (rank + 1) % world_size
recv_rank = (rank - 1 + world_size) % world_size
```

- 作用：实现环形拓扑，rank i 将 KV 发往 rank (i+1) % N，同时从 rank (i-1+N) % N 接收 KV。

### 5. USP AlltoAll 前后的维度含义

```python
in_list = [t.contiguous() for t in torch.tensor_split(x, world_size, 2)]
output_list = [torch.empty_like(in_list[0]) for _ in range(world_size)]
dist.all_to_all(output_list, in_list)
```

- `torch.tensor_split(x, world_size, 2)`：将张量沿第 2 维（head 维）切分为 world_size 份
- 第一次 AlltoAll：在 head 维度完成数据重组，使各设备获得不同的注意力头子集
- 第二次 AlltoAll（计算完成后）：在 head 维度反向重组，恢复为序列切分布局
- 末尾 `dist.all_gather`：在 seqlen 维度上把所有 rank 的结果拼回完整序列。

### 6. CFG 并行融合公式

```python
noise_pred = output_list[0] + guidance_scale * (output_list[1] - output_list[0])
```

- `output_list[0]`：负样本（unconditioned）预测结果
- `output_list[1]`：正样本（conditioned）预测结果
- `guidance_scale`：CFG 引导系数（示例中为 7.5）
- 作用：标准 Classifier-Free Guidance 公式，融合两路预测以控制条件生成强度。

---

## 【关联】

1. **[supported_matrix.md](supported_matrix.md)**：原文明确指出"各策略可以独立使用，也可以组合叠加，具体支持情况请参见 supported_matrix.md"，即该矩阵文档给出 TP / USP / RSP / CFG Parallel 在不同模型和框架（vLLM Omni、Diffusers+CacheDit、lightx2v）下的兼容性组合清单。

2. **[./fa_power_cap.md](./fa_power_cap.md)**：原文在"FA_Power_Cap 技术"小节中明确引用，详细描述 `--comm_type 0/1/2` 三个路径的手动接入步骤；该技术与 USP 协同工作——Ulysses 序列并行依赖 Flash Attention（FA），而 FA_Power_Cap 控制 FA 的通信/算子路径，二者在 USP 启用时构成上下游关系。

3. **各策略之间的组合关系**（原文推荐方案）：
   - **USP + RSP**：RSP 可配合 Ulysses 使用，补充 Ulysses 无法被 head num 整除的部分（即当 world_size 不能整除 head 数时，用 RSP 弥补剩余并行度）。
   - **TP 与 USP/RSP**：原文建议"不推荐优先使用 TP（通信开销较大）"，优先使用 USP；当模型 CFG > 1 时叠加 CFG 并行。
   - **CFG 融合 vs CFG 并行**：二者为同一优化目标的两种不同路径，CFG 融合在单设备内拼接 batch，CFG 并行在多设备间分摊正负样本。

---

## 【使用方法】

原文提供了详细的代码示例与配置开关，分策略汇总如下：

### 1. Tensor Parallel 启用

```python
dist.init_process_group(backend="hccl")
torch.npu.set_device(f"npu:{os.environ['LOCAL_RANK']}")
linear = torch.nn.Linear(4096, 4096).npu()
x = torch.randn(1, 256, 4096, device="npu")
world_size = dist.get_world_size()
rank = dist.get_rank()
with torch.no_grad():
    w_chunk = linear.weight.data.chunk(world_size, dim=0)[rank]
    local_out = x @ w_chunk.T
    dist.all_reduce(local_out)
```
- 关键配置：`backend="hccl"`、`LOCAL_RANK` 环境变量、`world_size` 即 TP 度数。
- 约束：**TP degree 不应超过单机 NPU 数量**。

### 2. Ring Sequence Parallel 启用

通过 `dist.send_recv` 实现环状 KV 传递，循环 `world_size` 轮完成全部序列位置注意力计算。
- 关键参数：`seqlen_chunk = seqlen // world_size`。
- 适用条件：序列长度远大于 head_dim。

### 3. Ulysses Sequence Parallel 启用

- 调用入口：`from mindiesd import attention_forward`
- 关键操作：序列切分 → `dist.all_to_all`（head 维重组）→ `attention_forward(..., opt_mode="manual", op_type="prompt_flash_attn", layout="BSND")` → `dist.all_to_all`（回收集合）→ `dist.all_gather`（还原序列）。
- 关键参数：`batch=1, seqlen=4096, hiddensize=512, head=8`。
- 约束：Ulysses 并行度需被 FA 的 head num 整除。

### 4. FA_Power_Cap 配置

- 命令行参数：`--comm_type 0/1/2`，分别对应 baseline、插入通信、块级注意力三种路径。
- 详细手动接入步骤参见 `./fa_power_cap.md`（原文未提供完整命令清单）。

### 5. CFG Parallel 启用

```python
guidance_scale = 7.5
if rank == 0:
    output = model(latent, timestep, uncond_embed)
elif rank == 1:
    output = model(latent, timestep, cond_embed)
output_list = [torch.empty_like(output) for _ in range(world_size)]
dist.all_gather(output_list, output)
noise_pred = output_list[0] + guidance_scale * (output_list[1] - output_list[0])
```
- 关键配置：`backend="hccl"`、`LOCAL_RANK` 环境变量。
- 约束：**guidance_scale > 1 且至少 2 卡**。

### 6. CFG Fusion 启用

原文仅给出原理与适用场景描述（单设备内 batch 维拼接正负样本），**未提供具体代码示例**，实际调用细节需结合 Diffusers+CacheDit 等下游框架代码进一步查看。

## 图文联合解读

- `tensor_parallel_image_1.png`: **图文联合解读：**

1) **图示内容**：展示单次矩阵乘法 X*W=Y。橙色方块 X 维度 [b,s,h]（batch、序列长度、隐藏维度），蓝色方块 W 维度 [h,h']，绿色方块 Y 维度 [b,s,h']，三者通过乘号与等号连接，呈现完整单卡运算流程。

2) **技术结论**：明确单卡矩阵乘的输入/输出张量维度定义，建立后续按行/按列切分的基准——切分后两设备分别计算部分结果，再通过通信（加法或拼接）合并。

3) **与文档关系**：作为张量并行原理章节的"原始态"示意图，与后续 image_2~5 的按行/按列切分图构成"整体→拆分→合并"的递进论证链，为读者理解 TP 如何降低单卡显存与计算负载提供可视化锚点。
- `tensor_parallel_image_2.png`: # 图文联合解读

**图示内容：**
展示一次矩阵乘法的基础设置：输入 X 沿第一维度被分为 X1|X2（形状 [b,s,h]），权重 W 沿行拆为 W1/W2（形状 [h,h']），输出为 Y（形状 [b,s,h']），三者分别对应两个 NPU 上的并行分片。

**技术结论：**
引出张量并行的核心思想——将单次大矩阵乘法 X×W=Y 拆分为两路子矩阵乘（在两个 NPU 上分别执行 X1×W1 与 X2×W2），通过卡间通信（all-reduce 或 all-gather）合并得到完整 Y，从而降低单卡显存与计算负载。

**与文档论点的关系：**
此图是「张量并行」章节的开篇示意图，为后续按行切分（image_2/3）和按列切分（image_4/5）的两种优化方式铺垫基础，强调 TP 通过拆分计算与参数来突破单卡显存瓶颈。
- `tensor_parallel_image_3.png`: **1) 图示内容：** 展示两路并行矩阵乘法 X1*W1=Y1 与 X2*W2=Y2，对应张量维度 [b,s,h/N]·[h/N,h']=[b,s,h']，两路结果通过箭头汇聚相加得到完整输出 Y，维度 [b,s,h']，体现按行切分 W 后各 NPU 卡独立计算再卡间通信归约的流程。

**2) 技术结论：** 张量并行按行切分将一次大矩阵乘法拆为 N 个并行子乘法，输出通过加法归约还原，分散了单卡显存与计算负载。

**3) 与文档关系：** 对应文档中 tensor_parallel_image_3，说明"按行切分"方案：切分后经卡间通信加法得到完整结果，论证张量并行可有效降低显存但通信开销较大的结论。
- `tensor_parallel_image_4.png`: **图文联合解读：**

1) **图示内容**：展示一次基础矩阵乘法 X × W = Y。橙色方块 X 维度 [b,s,h]，蓝色方块 W 被竖线分为 W1|W2（维度 [h,h']），绿色方块 Y 维度 [b,s,h']。矩阵 W 内部的分割线预示后续按行/列切分。

2) **技术结论**：该图为张量并行（TP）的基线示意——单一矩阵乘法可在权重维度上进行切分（如分为 W1、W2），分布到多卡并行计算，再通过通信（求和或拼接）合并结果，从而降低单卡显存与计算负载。

3) **与文档关系**：作为 TP 章节的引子，先定义输入 X、权重 W、输出 Y 的维度符号（b/s/h/h'），为下文"按行切分"与"按列切分"两种优化方法建立统一的数学符号基础。
- `tensor_parallel_image_5.png`: # 图文联合解读

**图示内容：** 输入X（橙色，[b,s,h]）完整复制，权重W按列切分为W1、W2（蓝色，各[h,h'/N]），分别计算得Y1、Y2（绿色，各[b,s,h'/N]），最终通过卡间通信**拼接**还原完整输出Y（[b,s,h']）。

**技术结论：** 这是张量并行的**按列切分**方案——单次矩阵乘法拆为N次并行子计算，各NPU独立运算后沿输出维度拼接，X需全卡复制。

**与文档关系：** 对应文档"按列切分"段落（tensor_parallel_image_5），论证了通过权重切分实现显存与计算负载在多卡间分摊，但输入X需广播复制（通信开销来源），呼应前文"TP通信开销较大，不推荐优先使用"的论点。
- `ring.png`: **图文联合解读：**

1) **图示内容**：四帧序列展示Q0/Q1/Q2/Q3四个Q块（沿序列维度N/P_d切分）保持位置不变，KV（kv0→kv1→kv2→kv3→kv0）以环形方式在设备间依次轮转传递，每步完成一次局部注意力计算。

2) **技术结论**：环状序列并行沿序列维度切分Q，通过环状通信使KV在P个设备上轮转P次后，每卡均可与全序列Q完成注意力计算，从而将序列维度显存均摊到多卡，并以计算掩盖通信开销。

3) **与文档论点对应**：直接论证"RSP可与USP互补使用"的策略——当Ulysses并行度无法被注意力头数整除时，剩余部分由RSP承担，通过环形切分序列维度实现扩展并行，二者叠加共同解决单卡显存不足问题。
- `ulysses.png`: **图文联合解读：**

1) **图示内容**：左侧 X(Wq/Wk/Wv) 沿序列维度切分为 Q/K/V（[N,d][local(N/P,d)]）；第一次 **alltoall** 将切分维度由序列转为注意力头，各卡并行计算 Qh·Kh^h→softmax→Sh·Vh→Oh；第二次 **alltoall** 将结果还原为序列切分输出 O。

2) **技术结论**：仅需两次 alltoall 即可在多头维度并行执行注意力计算，通信开销小，且输出保持原序列切分布局，与下游模块无缝衔接。

3) **与文档论点对应**：直观印证「Ulysses 序列并行」原理——沿序列切分输入、通过 AlltoAll 在注意力头维度重组、各卡并行计算不同头，正是文档推荐 USP 优先使用的核心依据。
- `cfg_parallel.png`: **图文联合解读：**

1）图示内容：同一 Input 分别送入 Device0（cond 条件分支）和 Device1（uncond 非条件分支），各自经 Block1–Block4 串行推理得 Output1/Output2，再经 AllGather 汇聚为最终 Output。

2）技术结论：CFG 并行将正负样本拆到两卡独立计算，仅末端通过 AllGather 通信汇总，通信开销极小。

3）与文档关系：直接对应"CFG 并行——将正负样本推理分发到不同设备并行执行"的论述，为"CFG>1 时推荐使用"的结论提供可视化依据。
- `cfg_fusion.png`: **图文联合解读：**

1) 图中左侧展示CFG并行结构：`prompt`与`neg_prompt`分别送入两个独立`DiT Block`，并行计算后汇聚到`pred`；右侧经转换箭头后，展示等效逻辑：将正负样本拼接（`Cat等`）后送入单个`DiT Block`输出`pred`。

2) 论证结论：CFG并行将正/负条件样本分发到不同设备并行推理，通信开销小，且与串行拼接执行数学等价，可显著加速推理。

3) 与文档论点呼应：直接对应"CFG并行"章节——"将正样本和负样本推理分发到不同设备并行执行，适合CFG>1的扩散模型，推荐使用"。
