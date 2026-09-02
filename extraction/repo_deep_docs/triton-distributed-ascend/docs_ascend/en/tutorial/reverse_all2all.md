# Reverse All2All (EP MoE Distributed Kernel)

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/en/tutorial/reverse_all2all.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/en/tutorial/reverse_all2all.md

```markdown
# 《Reverse All2All (EP MoE Distributed Kernel)》深度解读

> ⚠️ **原文截断说明**: 原文在 MTE Implementation 的 Triton kernel 代码段处被截断(`Outer loop: Iterate ove` 之后的内容缺失,后续的 MTE 细节、双 buffer 调度、UDMA 实现、性能对比等章节未出现在原文片段中)。以下解读严格基于现有原文,未出现的内容均明确标注。

---

## 【定位】

这篇文档描述并实现 EP(Expert Parallel)MoE 模型中 **All2All 通信模式的反向(Combine)阶段**——即在专家计算完成后,将位于专家所在 rank 上的输出**回传**到 token 原始所在 rank 的分布式 kernel,涵盖 MTE 通用版本和 Ascend 950 UDMA 优化版本两种实现。

---

## 【技术要点】

1. **通信语义为"维度互换"**: 与 Forward All2All 相比,Reverse All2All 将 `world_size` 因子从 H 维度"挪"到 S 维度,本质上是转置了跨 rank 通信模式。输入 `(S * world_size, H, D)` → 输出 `(S, H * world_size, D)`。

2. **Producer-Consumer Pipeline 以 Vector Core 粒度启动**: kernel 的 launch grid 是 `vec_num`(Vector Core 数量,而非 AICore 数量),通过 `kernel_hccl_reverse_a2a_pipelined[vec_num, 1, 1](...)` 启动,使得每个 VC 独立充当 Producer 或 Consumer。

3. **角色分配规则**: `role = pid % 2`(偶 = Producer,奇 = Consumer);**`logical_core_id = pid // 2`**,**`n_role_cores = ncore // 2`**,每个 Producer-Consumer 对共享一个 `logical_core_id`。

4. **同步机制从 barrier 切换到 per-task signal**: 用 `dl.wait(..., waitValue=0, "acquire")` + `dl.consume_token(...)` + `tl.store/tl.load` + `libshmem_device.fence()` + `dl.notify(...)` 替代 `barrier_all()` / `barrier_all_vec()`,Producer 等待目标 rank 的 signal slot 被清零(值为 0),Consumer 通过 `dl.notify(..., signal=0)` 复位 signal 释放下一轮迭代。

5. **Signal Memory 布局**:`signal_mem` shape 为 `[H * world_size * buffer_num * 8]`(int64,每槽 8 字节);索引布局为 `[buffer_id][num_blocks_d][H * rank_size][rank_factor]`,Producer 用 `rank`,Consumer 用 `r`(对方 rank)。

6. **UDMA 优化版本(Ascend 950)**: 利用 950 的新 UDMA 链路提升跨卡带宽,把"跨卡数据交换"和"本地数据重排"拆分为两个独立阶段分别处理(原文仅给出概述,具体实现未给出)。

---

## 【关键机制与数据】

### 工作原理(Producer 侧流程,原文:)

```
1. dl.wait(remote_signal_ptr, 1, "gpu", "acquire", waitValue=0)
   ↓ 等待目标 rank 的 signal slot 被清零(目标 Consumer 已读完上一 buffer)
2. dl.consume_token(remote_ptr, token)
   ↓ 强制依赖:remote writes 必须在 wait 完成后才进行
3. tl.store(remote_ptr + offset, data, mask=mask)
   ↓ 通过 dl.symm_at 映射的远程对称地址写入
4. libshmem_device.fence()
   ↓ 确保所有 remote writes 对 target 可见
5. dl.notify(signal_mem_ptr, target_rank)
   ↓ 通知 target rank 数据已就绪
```

### 工作原理(Consumer 侧流程,原文:)

```
1. dl.wait(signal_mem_ptr, 1, "gpu", "acquire")
   ↓ 等待 source rank 发来的数据就绪信号
2. dl.consume_token(local_peer_ptr, token)
   ↓ 强制依赖:local reads 必须在 wait 完成后才进行
3. tl.load(local_peer_ptr + offset, mask=mask)
   ↓ 从本地对称内存读取数据
4. tl.store(output_ptr + offset, data, mask=mask)
   ↓ 写入输出 tensor
5. libshmem_device.fence()
   ↓ 确保所有 reads 完成再复位信号
6. dl.notify(signal_mem_ptr, rank, 0)
   ↓ signal 复位为 0,释放下一轮 Producer
```

### EP MoE 场景数据流(原文: DeepSeek-V3 with 256 experts)

| 阶段 | 输入 shape(每 rank) | 输出 shape(每 rank) |
|---|---|---|
| Forward All2All (Dispatch) | `(S, H, D)` | `(S/world_size, H * world_size, D)` |
| Expert GEMM | (本地专家 GEMM) | — |
| **Reverse All2All (Combine)** | `(S * world_size, H, D)` | `(S, H * world_size, D)` |

### 性能特性(原文:)

- "A Producer-Consumer pipeline based on per-task signal synchronization achieves overlap between remote cross-card stores (Producer) and local reads/output writes (Consumer), obtaining **higher bandwidth utilization than barrier-based approaches**." —— 性能优势来自**细粒度 per-task 信号同步**,而非全局 barrier。

---

## 【表格解读】

**原文无传统意义上的 Markdown 表格**,但原文给出了几个**布局定义/参数清单**,逐字还原并以表格形式呈现如下:

### 表 1: Kernel 签名参数清单(原文:kernel 形参列表)

| 参数 | 类型/语义 | 角色 |
|---|---|---|
| `a_ptr` | Input tensor: shape `(S_total, H, D)` | 输入 |
| `c_ptr` | Output tensor: shape `(S, H * world_size, D)` | 输出 |
| `peer_mem_ptr` | Symmetric memory pointer | 远程/本地对称地址映射 |
| `signal_mem_ptr` | Signal memory pointer (int64) | 同步信号槽 |
| `rank` | Current rank ID (host side) | 当前 rank |
| `rank_size` | Total number of ranks (host side) | 全局 rank 数 |
| `buffer_num` | Number of double buffers | 双缓冲数量 |
| `S, H, D` | Tensor dimensions(`S = S_total / rank_size`) | 张量维度 |
| `stride_as, stride_ah, stride_ad` | Input strides | A 的三轴 stride |
| `stride_cs, stride_ch, stride_cd` | Output strides | C 的三轴 stride |
| `COMM_BLOCK_S` | `tl.constexpr`,Tile size in S dimension | S 轴 tile 大小 |
| `COMM_BLOCK_D` | `tl.constexpr`,Tile size in D dimension | D 轴 tile 大小 |

**逐行解读**:
- `a_ptr` / `c_ptr`: Reverse All2All 的输入来自 forward All2All 后再经 Expert GEMM 计算的输出,形状为 `(S_total, H, D)`,`S_total = S * rank_size`;最终输出回到原始 token 分布形状 `(S, H * rank_size, D)`。
- `peer_mem_ptr`: 用于 `dl.symm_at` 将本地地址映射到远程 rank 的对称地址,Producer 通过它写入远程,Consumer 通过它读取本地副本。
- `signal_mem_ptr`: 跨 rank 的同步信号数组,Producer-Consumer 间握手。
- `rank` / `rank_size` / `buffer_num`: 全部为 host 端标量参数,在编译期即可确定布局。
- `COMM_BLOCK_S` / `COMM_BLOCK_D`: 编译期 tile 大小,原文未给出具体默认值(原文截断)。

### 表 2: Signal Memory 布局(原文:`signal_mem shape: [H * world_size * buffer_num * 8]`)

| 层级 | 字段 | 含义 | 公式/取值 |
|---|---|---|---|
| 顶层 | shape | 总字节数 | `[H * world_size * buffer_num * 8]` (int64,每槽 8 字节) |
| 一级索引 | `buffer_id` | 双缓冲槽编号 | `0..buffer_num-1` |
| 二级索引 | `num_blocks_d * H * rank_size` | 每 buffer iteration 的总任务数 | `num_blocks_d * H * rank_size` |
| 三级索引 | `rank_factor` | Producer-Consumer 对标识 | Producer 用 `rank`,Consumer 用 `r` |
| Producer 地址 | `remote_signal_ptr` 偏移 | `buffer_id * num_blocks_d * H * rank_size * 8 + num_blocks_d * H * rank * 8 + task_idx * 8` | |
| Consumer 地址 | `signal_mem_ptr` 偏移 | `buffer_id * num_blocks_d * H * rank_size * 8 + num_blocks_d * H * r * 8 + task_idx * 8` | |

**逐行解读**:
- 信号槽按 `[buffer_id][num_blocks_d * H * rank_size][rank_factor]` 三维布局,前两个维度共同构成 `(buffer_num, num_blocks_d * H * rank_size)` 个 8 字节槽,第三层用于区分 Producer 和 Consumer 视角。
- **Producer 与 Consumer 的 `rank_factor` 不同**:Producer 使用自己的 `rank`,Consumer 使用对端的 `r`。这意味着两端读写的是 signal 数组中**不同的槽位**,实现了"发信号槽"与"收信号槽"的解耦——Producer 等的是"对端 Consumer 是否已读完上一 buffer",Consumer 等的是"对端 Producer 是否已写完当前 buffer"。

### 表 3: Producer / Consumer 角色对比(原文:角色定义段落)

| 维度 | Producer(pid % 2 == 0) | Consumer(pid % 2 == 1) |
|---|---|---|
| 数据流方向 | 本地 → 远程对称内存 | 本地对称内存 → 输出 tensor |
| 主要操作 | `tl.store(remote_ptr + offset, data, mask=mask)` | `tl.load(local_peer_ptr + offset, mask=mask)` + `tl.store(output_ptr + offset, data, mask=mask)` |
| wait 语义 | 等目标 rank 的 signal slot 被清零(`waitValue=0`) | 等 source rank 发来的数据就绪信号 |
| consume_token 目标 | `remote_ptr`(确保 wait → remote write) | `local_peer_ptr`(确保 wait → local read) |
| notify 目标 | `target_rank` | `rank`(自复位,`signal=0`) |
| fence() 时机 | 所有 remote writes 后 | 所有 reads 后 |

**逐行解读**:
- Producer 的 `waitValue=0` 至关重要:它表达"对端的 Consumer 已经读完上一 buffer,这个槽位可复用",这是**双 buffer pipeline**的核心信号语义。
- Consumer 的 notify 是 `dl.notify(signal_mem_ptr, rank, 0)`(自复位),而 Producer 的 notify 是 `dl.notify(signal_mem_ptr, target_rank)`(通知对方),两者**操作对象和值都不同**,但地址偏移公式沿用同一个 layout。

---

## 【公式解读】

> 原文无标准数学公式,以下"公式"为原文出现的**布局/偏移/索引表达式**,按原式逐字保留并逐符号解释。

### 公式 1:Signal Memory 总大小(伪公式)

```
signal_mem shape = [H * world_size * buffer_num * 8]
```

- `H`: 隐藏维度大小(head dim 或 hidden size 派生量)
- `world_size`: 全局 rank 数(等于 `rank_size`)
- `buffer_num`: 双 buffer 数量
- `8`: int64 每个 8 字节
- **作用**:信号槽总字节数,等于"每 rank 的 H 维任务数 × rank 数 × buffer 数 × 8 字节"。

### 公式 2:Producer Signal 地址(伪公式)

```
remote_signal_ptr + buffer_id * num_blocks_d * H * rank_size * 8
                 + num_blocks_d * H * rank * 8
                 + task_idx * 8
```

- `buffer_id`: 当前双 buffer 索引(`0..buffer_num-1`)
- `num_blocks_d * H * rank_size`: 每 buffer iteration 的总任务数(乘 8 字节得到字节偏移)
- `H * rank`: 第 `rank` 个 rank 的 H 维任务起点
- `task_idx`: 当前 task 在该 rank 内的序号
- **作用**:定位 Producer 要等待的目标信号槽。

### 公式 3:Consumer Signal 地址(伪公式)

```
signal_mem_ptr + buffer_id * num_blocks_d * H * rank_size * 8
               + num_blocks_d * H * r * 8
               + task_idx * 8
```

- 整体结构同公式 2,只是把 `rank` 换成了 `r`(对端 rank 标识)
- **作用**:Consumer 等待的是来自 source rank 的信号槽,所以索引用源 rank `r`。

### 公式 4:对称内存布局 stride(原文代码内表达式)

```
buffer_chunk_size = (H * rank_size) * D
stride_ps = H * rank_size * D
stride_ph = D
stride_pd = 1
```

- 原文注释:`# Symmetric memory layout: [buffer_num, S_block, H * rank_size, D]`
- `buffer_chunk_size`: 单 buffer 在 S 维度上一个 chunk 的大小(元素数)
- `stride_ps` / `stride_ph` / `stride_pd`: 对称内存 `peer_mem_ptr` 在 S、H、D 三个轴上的 stride
- **作用**:在 Producer 端计算 `tl.store(remote_ptr + offset, data, mask=mask)` 中的 offset。

### 公式 5:角色与逻辑核标识(原文代码内表达式)

```
role = pid % 2
logical_core_id = pid // 2
n_role_cores = ncore // 2
```

- `pid = tl.program_id(axis=0)`: 当前 Vector Core 的程序 ID(范围 `0..vec_num-1`)
- `role`: 0 = Producer,1 = Consumer
- `logical_core_id`: 同一对 Producer-Consumer 共享同一 `logical_core_id`
- `n_role_cores`: 每个角色可用的逻辑核数
- **作用**:在以 Vector Core 粒度启动的 grid 内,把任务分成两半,前一半写、后一半读。

---

## 【关联】

### 与文中提及的其他特性的关系

1. **Forward All2All (Dispatch)**: 文档明确指出 Reverse All2All 是其**反向**,二者通过维度 swap 互补。Forward 输入 `(S, H, D)` → `(S/world_size, H * world_size, D)`,Reverse 走相反方向。

2. **Expert GEMM (GroupedGEMM / Fused MoE)**: Reverse All2All 的输入 `a_ptr` 即来自本地专家 GEMM 的输出,形状 `(S_total, H, D)`,所以 Reverse All2All 与 `GroupedGEMM` / `Fused MoE` 在数据流上是**上下游串联关系**。

3. **`dl.symm_at`**: Producer 远程写入依赖该原语提供的**对称地址映射**,这是 libshmem_device 提供的底层能力(原文 `from triton_dist.language.extra import libshmem_device`)。

4. **`dl.consume_token`**: 用于**强制 Producer/Consumer 内部 wait → store/load 的依赖顺序**,避免编译期乱序。

5. **`barrier_all()` / `barrier_all_vec()`**(前代实现): 被 per-task signal 取代,意味着这是从"粗粒度全局 barrier"到"细粒度 per-task signal"的演进。

6. **UDMA link(Ascend 950)**:UDMA 优化版本是 MTE 版本在新硬件上的**带宽增强替代**,但文中未给具体带宽数字或对比数据。

7. **`sub_vec_id()` 子块模型**(前代): 被 `pid // 2 / pid % 2` 的 Vector Core PID 模型取代,文档明文"This differs from the previous `sub_vec_id()` sub-block model"。

### 内部链接信息(原文链接列表解析)

原文给出的链接上下文片段:`..., A, C, peer_mem, signal_mem, rank, rank_size, buffer_num, S, H, D, A.stride(0, A, C, peer_mem, rank, rank_size, buffer_num, S, H, D, A.stride(0`

- `A` / `C`:对应 kernel 形参中的 `a_ptr`(输入)和 `c_ptr`(输出),均为**文档超链接锚点**(`A`/`C` 是常见 tensor 命名)。
- `peer_mem` / `signal_mem`:对应 `peer_mem_ptr` / `signal_mem_ptr`,**Symmetric Memory 概念**的文档链接。
- `rank` / `rank_size` / `buffer_num`:分布式概念,与 ProcessGroup/Rank 文档关联。
- `S, H, D`:张量维度命名,链接到 shape 规范。
- `A.stride(0)`:Triton tensor stride API,链接到 Triton 语言参考。

> **说明**: 原文链接列表本身是被截断的元数据片段,实际链接到的目标页面文档未在原文提供。

---

## 【使用方法】

### 启用方式(原文:)

```python
from triton.backends.ascend.driver import NPUUtils

vec_num = NPUUtils().get_aivector_core_num()  # Vector Core count (not AICore count)
kernel_hccl_reverse_a2a_pipelined[vec_num, 1, 1](...)
```

### 配置项 / 编译期参数(原文:)

| 参数 | 来源 | 取值约束 |
|---|---|---|
| Launch grid | `vec_num` | 必须等于 Vector Core 数,**不是** AICore 数 |
| `COMM_BLOCK_S` | `tl.constexpr` | S 维 tile 大小(原文未给具体默认值,因截断) |
| `COMM_BLOCK_D` | `tl.constexpr` | D 维 tile 大小(原文未给具体默认值,因截断) |
| `buffer_num` | host 端参数 | 双 buffer 数量,影响 signal memory 大小 |

### Kernel 导入(原文:)

```python
import triton
import triton.language as tl
import triton_dist.language as dl
from triton_dist.language.extra import libshmem_device
from triton.backends.ascend.driver import NPUUtils
```

### UDMA 优化版本(原文:)

原文仅在开头概述中提及 "UDMA Optimized Version (Ascend 950)",**详细配置、命令、性能数据原文未涉及**(原文截断)。

### ⚠️ 原文未涉及的内容

- 具体性能数字(MTE vs UDMA 的带宽对比、延迟数字): **原文未给出**(原文截断)。
- 在真实 EP MoE 模型中端到端调用 Reverse All2All 的 Python wrapper 示例: **原文未给出**(原文截断)。
- `buffer_num` 的推荐取值: **原文未给出**。
- `COMM_BLOCK_S` / `COMM_BLOCK_D` 的推荐取值: **原文未给出**。
- 错误处理、超时策略、重试机制: **原文未涉及**。
```
