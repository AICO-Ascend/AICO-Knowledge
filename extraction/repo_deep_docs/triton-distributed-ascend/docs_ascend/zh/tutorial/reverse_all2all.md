# Reverse All2All (EP MoE Distributed Kernel)

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/zh/tutorial/reverse_all2all.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/zh/tutorial/reverse_all2all.md

# 「Reverse All2All (EP MoE Distributed Kernel)」深度解读

## 【定位】

这篇文档解决 EP（Expert Parallel）MoE 模型中 All2All 通信"后半段"（Combine 阶段）的 Triton 内核编写问题——即 expert 计算完成后，如何把本地 expert 的输出送回 token 的原始 rank，并在 Ascend NPU 上以 Vector Core 粒度的 Producer-Consumer 流水线、基于 per-task 信号同步的方式实现高带宽的跨卡通信。文档同时覆盖一个针对 Ascend 950 UDMA 链路的优化版本。

---

## 【技术要点】

1. **两个实现版本**：
   - **MTE 版本**（通用）：Vector Core 级 Producer-Consumer 流水线，偶数 VC = Producer（跨卡远程 store），奇数 VC = Consumer（本地读取与输出写入）。
   - **UDMA 优化版本**（Ascend 950）：利用 950 新增的 UDMA 链路提高跨卡带宽，把"跨卡数据交换"与"本地数据重排"拆成两个阶段。

2. **核心算子语义**：
   - Input  shape：`(S * world_size, H, D)` per rank
   - Output shape：`(S, H * world_size, D)` per rank
   - 与 forward All2All 相比，`world_size` 因子从 H 维移到 S 维（跨 rank 通信模式的转置）。

3. **Vector Core 粒度 launch**：
   - `vec_num = NPUUtils().get_aivector_core_num()`（不是 AICore 数）
   - Launch grid：`kernel_hccl_reverse_a2a_pipelined[vec_num, 1, 1](...)`
   - `role = pid % 2`；`logical_core_id = pid // 2`；`n_role_cores = ncore // 2`。

4. **基于 per-task 信号的细粒度同步**（取代粗粒度 `barrier_all()` / `barrier_all_vec()`）：
   - Producer：`dl.wait(..., waitValue=0)` → `dl.consume_token` → `tl.store(remote_ptr + ...)` → `libshmem_device.fence()` → `dl.notify(signal_mem_ptr, target_rank)`
   - Consumer：`dl.wait(...)` → `dl.consume_token` → `tl.load(local_peer_ptr)` → `tl.store(output_ptr)` → `fence()` → `dl.notify(signal_mem_ptr, rank, 0)`（重置信号）
   - 跨卡远程 store 通过 `tl.store` + `dl.symm_at` 对称地址映射实现。

5. **信号内存布局**：
   - shape：`[H * world_size * buffer_num * 8]`（int64，每槽 8 字节）
   - Layout：`[buffer_id][num_blocks_d][H * rank_size][rank_factor]`
   - 索引公式：`remote_signal_ptr + buffer_id * num_blocks_d * H * rank_size * 8 + num_blocks_d * H * rank * 8 + task_idx * 8`
   - Producer/Consumer 端使用的 `rank_factor` 不同：Producer 用 `rank`，Consumer 用 `r`。

6. **双缓冲 + tile 大小参数**：
   - 外层循环遍历 S 维 block：`for global_id_s in range(0, num_blocks_s):` 中 `buffer_id = global_id_s % buffer_num`
   - Tile 常量 `COMM_BLOCK_S: tl.constexpr`（S 维）与 `COMM_BLOCK_D: tl.constexpr`（D 维）。

---

## 【关键机制与数据】

### 数据流（原文语义）

- **Forward All2All (Dispatch)**：`Input: (S, H, D) per rank → Output: (S/world_size, H * world_size, D) per rank` —— token 按目标 expert rank 分组被分发。
- **Expert Computation**：每个 rank 处理分配给其 expert 的 token。
- **Reverse All2All (Combine)**：`Input: (S * world_size, H, D) per rank → Output: (S, H * world_size, D) per rank` —— 结果返回原始 token rank。

> 原文："与 forward All2All 的关键区别在于维度交换：`world_size` 因子从 H 维移到 S 维（或反之），实质上是对跨 rank 通信模式做转置。"

### Producer 端（原文步骤）

> 原文：
> 1. `dl.wait(remote_signal_ptr, 1, "gpu", "acquire", waitValue=0)` —— 等待目标 rank 的信号槽被清零（值 == 0），表示目标 rank 的 consumer 已读完上一个 buffer
> 2. `dl.consume_token(remote_ptr, token)` —— 强制依赖生效，使远程写入仅在 wait 完成后发生
> 3. `tl.store(remote_ptr + offset, data, mask=mask)` —— 将数据写入远端对称内存
> 4. `libshmem_device.fence()` —— 确保所有远程写入在发送通知前可见
> 5. `dl.notify(signal_mem_ptr, target_rank)` —— 通知目标 rank 数据可用

### Consumer 端（原文步骤）

> 原文：
> 1. `dl.wait(signal_mem_ptr, 1, "gpu", "acquire")` —— 等待来自源 rank 的信号（数据可用）
> 2. `dl.consume_token(local_peer_ptr, token)` —— 强制依赖生效，使本地读取仅在 wait 完成后发生
> 3. `tl.load(local_peer_ptr + offset, mask=mask)` —— 从本地对称内存读取数据
> 4. `tl.store(output_ptr + offset, data, mask=mask)` —— 写入输出 tensor
> 5. `libshmem_device.fence()` —— 确保所有读取在重置信号前完成
> 6. `dl.notify(signal_mem_ptr, rank, 0)` —— 重置信号（值=0）以放行下一迭代的 producer

### 对称内存布局（原文）

```
symm memory layout: [buffer_num, S_block, H * rank_size, D]
stride_ps = H * rank_size * D
stride_ph = D
stride_pd = 1
```

### Producer 写远端的索引计算（原文）

```python
peer_h_write = rank * H + h_id
peer_offs_write = (
    buffer_id * (COMM_BLOCK_S * buffer_chunk_size)
    + tl.arange(0, COMM_BLOCK_S)[:, None] * stride_ps
    + peer_h_write * stride_ph
    + offs_d[None, :] * stride_pd
)
tl.store(remote_ptr_dummy + peer_offs_write, a_data, mask=mask)
```

### 跨 EP MoE 场景（原文）

> 原文："在典型 EP MoE 层（如 256 expert 的 DeepSeek-V3）中："
> 1. Forward All2All (Dispatch)：每 rank 输入 `(S, H, D)` → `(S/world_size, H * world_size, D)`
> 2. Expert GEMM：GroupedGEMM / Fused MoE
> 3. Reverse All2All (Combine)：每 rank 输入 `(S * world_size, H, D)` → `(S, H * world_size, D)`

> 原文性能定性描述："基于 per-task 信号同步的 Producer-Consumer 流水线实现了跨卡远程 store（Producer）与本地读取/输出写入（Consumer）的重叠，获得比基于 barrier 方式更高的带宽利用率。"  
> （文档**未给出**具体的 MB/s、延迟等量化性能数字。）

---

## 【表格解读】

**原文无表格**（无 markdown 表格、无形式化参数表/性能对比表）。

文档以代码块 + 文字方式给出了三组可视为"准表格"的语义信息，为完整性起见在此**逐字还原**：

### 表-1：Forward / Reverse All2All 语义对比（原文伪代码块）

| 阶段 | Input (per rank) | Output (per rank) |
|---|---|---|
| Forward All2All (dispatch) | `(S, H, D)` | `(S/world_size, H * world_size, D)` |
| Reverse All2All (combine) | `(S * world_size, H, D)` | `(S, H * world_size, D)` |

逐行解读：
- Forward 行：输入按目标 expert rank 分组的 token；输出是从所有 rank 收集后的展平形式（`world_size` 因子加到 H 维）。
- Reverse 行：输入是本地 expert 的输出（`world_size` 因子加到 S 维）；输出重组为完整 `(S, H * world_size, D)`。
- 关键对比：两行之间 `world_size` 因子在 S 维与 H 维之间互换，即"跨 rank 通信模式的转置"。

### 表-2：Producer / Consumer 行为对比（原文两段并列说明）

| 维度 | Producer（偶数 VC） | Consumer（奇数 VC） |
|---|---|---|
| 数据来源 | 本地输入 tensor `A` | 本地对称内存 `peer_mem` |
| 写目标 | 远端对称内存（`dl.symm_at`） | 输出 tensor `C` |
| 同步起点 | `dl.wait(remote_signal_ptr, ..., waitValue=0)` | `dl.wait(signal_mem_ptr, 1, "gpu", "acquire")` |
| 依赖强制 | `dl.consume_token(remote_ptr, token)` | `dl.consume_token(local_peer_ptr, token)` |
| 完成通知 | `dl.notify(signal_mem_ptr, target_rank)` | `dl.notify(signal_mem_ptr, rank, 0)`（重置） |
| 末尾 fence | `libshmem_device.fence()`（保证 notify 前写入可见） | `libshmem_device.fence()`（保证重置信号前读取完成） |

逐行解读：
- 数据流方向相反：Producer 写远端、Consumer 写本地输出。
- 同步语义相反：Producer 等"目标已读完上一个 buffer"（`waitValue=0`），Consumer 等"源已写完当前 buffer"（到达即放行）。
- 通知语义相反：Producer 通知"我已写完"，Consumer 通知"我已读完请清零"。

### 表-3：信号内存 Layout（原文代码块）

```
signal_mem shape: [H * world_size * buffer_num * 8]  (int64, 每槽 8 字节)

Layout: [buffer_id][num_blocks_d][H * rank_size][rank_factor]
```

| 字段 | 含义 |
|---|---|
| `buffer_id` | 双缓冲槽索引 |
| `num_blocks_d * H * rank_size` | 每个 buffer 迭代的总 task 数 |
| `rank_factor` | Producer 用 `rank`，Consumer 用 `r`（标识 producer/consumer 对） |

逐行解读：
- 总字节数 = `H * world_size * buffer_num * 8`，每个槽位 8 字节（int64）。
- 三层索引中：最外层是 buffer（双缓冲切换），中层是 task（按 `num_blocks_d * H * rank_size` 展平），最内层是 rank 因子。
- `rank_factor` 在 Producer/Consumer 端的取值不同，是为了让 Producer 写入到目标 rank 的"自己专属槽位"，让 Consumer 读取时定位到"自己消费的那个槽位"。

---

## 【公式解读】

**原文无标准 LaTeX 公式**。文档以 Triton/伪代码方式给出了若干索引与步长表达式，**逐字保留**并解释如下：

### 公式 F1：role / logical_core_id / n_role_cores 分配

```
role = pid % 2
logical_core_id = pid // 2
n_role_cores = ncore // 2
```

符号含义：
- `pid`：`tl.program_id(axis=0)`，当前 Vector Core 的程序 ID（kernel 以 VC 总数 launch）。
- `role`：0 = Producer，1 = Consumer。
- `logical_core_id`：每个 Producer-Consumer 对共享同一个 logical_core_id（`pid // 2`）。
- `n_role_cores`：分配给每个角色（Producer/Consumer）的 core 数。

作用：把一维的 VC 序列拆成 P/C 对，实现 Vector Core 级的角色分配。

### 公式 F2：任务索引分解（Producer task 索引 → 三维坐标）

```
tmp = task_idx
rank_loop_id = tmp % rank_size
tmp //= rank_size
h_id = tmp % H
block_id_d = tmp // H
```

符号含义：
- `task_idx`：从 `logical_core_id` 出发按 `n_role_cores` 步进得到的一维 task 索引（范围 `0 ~ num_blocks_d * H * rank_size`）。
- `rank_loop_id`：当前 task 要送往的目标 rank 在"rank 偏移环"中的位置。
- `h_id`：当前处理的 H 维下标。
- `block_id_d`：当前处理的 D 维 block 下标。

### 公式 F3：目标 rank 计算

```
target_rank = (rank + rank_loop_id) % rank_size
```

符号含义：
- `rank`：当前 rank ID（host 侧常量）。
- `rank_loop_id`：见 F2。
- `rank_size`：rank 总数（host 侧常量）。
- `target_rank`：本次 task 要写入的远端 rank。

作用：在 rank 集合上做环形偏移，覆盖所有目标 rank。

### 公式 F4：Producer 信号等待地址

```
remote_signal_ptr = dl.symm_at(signal_mem_ptr, target_rank)

remote_signal_ptr
+ buffer_id * num_blocks_d * H * rank_size * 8
+ num_blocks_d * H * rank * 8
+ tmp * 8
```

符号含义：
- `dl.symm_at(signal_mem_ptr, target_rank)`：把本地的 `signal_mem_ptr` 映射到 `target_rank` 上的对称地址（跨 rank 访问）。
- `buffer_id * num_blocks_d * H * rank_size * 8`：跳到当前双缓冲槽。
- `num_blocks_d * H * rank * 8`：跳到"用 `rank` 作为 rank_factor"的子层（Producer 端固定用 `rank`，所以同一 producer rank 内的所有 task 落在同一子层）。
- `tmp * 8`：跳到当前 task 槽位（每槽 8 字节）。

作用：精确寻址 Producer 需要等待的"目标 rank 上、与本 rank 配对的那一个 task 信号槽"。

### 公式 F5：Consumer 信号地址（Consumer 端）

```
signal_mem_ptr
+ buffer_id * num_blocks_d * H * rank_size * 8
+ num_blocks_d * H * r * 8
+ task_idx * 8
```

符号含义：
- 与 F4 结构相同，但 `rank_factor` 取 `r`（Consumer 端的 rank 因子，原文称 "consumer 用 r"）。
- 其它三层与 Producer 完全一致。

作用：让 Consumer 寻址到"自己应该读取的那个 task 信号槽"（与 Producer 写入的槽位匹配）。

### 公式 F6：对称内存步长与 chunk size

```
stride_ps = H * rank_size * D
stride_ph = D
stride_pd = 1
buffer_chunk_size = (H * rank_size) * D
```

符号含义：
- `stride_ps`：S 维相邻元素之间的元素数。
- `stride_ph`：H 维相邻元素之间的元素数。
- `stride_pd`：D 维相邻元素之间的元素数。
- `buffer_chunk_size`：单个 S block 在对称内存中所占的元素数（`H * rank_size * D`）。

作用：定位对称内存中每个 (buffer, s_block, h, d) 单元的偏移；layout 为 `[buffer_num, S_block, H * rank_size, D]`。

### 公式 F7：Producer 写远端的偏移

```
peer_h_write = rank * H + h_id

peer_offs_write = (
    buffer_id * (COMM_BLOCK_S * buffer_chunk_size)
    + tl.arange(0, COMM_BLOCK_S)[:, None] * stride_ps
    + peer_h_write * stride_ph
    + offs_d[None, :] * stride_pd
)
tl.store(remote_ptr_dummy + peer_offs_write, a_data, mask=mask)
```

符号含义：
- `peer_h_write = rank * H + h_id`：在 `H * rank_size` 维上，把"自己的 rank"作为块前缀，再叠加上 h_id，确保不同 producer 的数据落在不同的 H 切片里（消费者按 rank 切片读回）。
- `buffer_id * (COMM_BLOCK_S * buffer_chunk_size)`：跳到当前双缓冲槽的起始。
- `tl.arange(0, COMM_BLOCK_S)[:, None] * stride_ps`：S 维 tile 内各行的偏移。
- `peer_h_write * stride_ph`：H 维偏移。
- `offs_d[None, :] * stride_pd`：D 维 tile 内各列的偏移。
- `mask`：非对齐 S 与 D 维的边界 mask。

作用：把从本地 A tensor 读取的 tile，按 `(buffer_id, s_block, h_id=peer_h_write, d_block)` 的形式写入远端对称内存。

---

## 【关联】

文档中涉及的核心模块/原语与上下游关系（基于原文及内部链接词汇）：

| 词汇/原语 | 在文中的作用 | 上下游关系 |
|---|---|---|
| `A`（输入 tensor） | shape `(S_total, H, D)`，Producer 读取来源 | 来自 expert GEMM 输出的本地结果 |
| `C`（输出 tensor） | shape `(S, H * world_size, D)`，Consumer 写入目标 | 流向 EP MoE 层的下游（如后续 Linear/Reduce） |
| `peer_mem` | 对称内存指针，用于跨 rank 数据落地 | 由 host 侧 `libshmem_device` 分配，与 `dl.symm_at` 配对使用 |
| `signal_mem` | 信号内存指针（int64），用于 Producer/Consumer 同步 | 与 `peer_mem` 一一对应，按 `[H * world_size * buffer_num * 8]` 布局 |
| `rank` / `rank_size` | 当前 rank ID 与总 rank 数（host 侧常量） | 控制 `target_rank = (rank + rank_loop_id) % rank_size` 的环形偏移 |
| `buffer_num` | 双缓冲槽数 | 通过 `buffer_id = global_id_s % buffer_num` 切换 |
| `S` / `H` / `D` | tensor 维度（`S = S_total / rank_size`） | 决定 tile 数 `num_blocks_s = ceil(S/COMM_BLOCK_S)`、`num_blocks_d = ceil(D/COMM_BLOCK_D)` |
| `tl.store(remote_ptr_dummy + ...)` | 跨卡远程 store 实现 | 与 `dl.symm_at` 共同实现对称地址远程写 |
| `dl.wait / dl.notify / dl.consume_token` | per-task 信号同步原语 | 替代 `barrier_all()` / `barrier_all_vec()`，实现更细粒度 Producer/Consumer 重叠 |
| `libshmem_device.fence()` | 跨卡写入可见性 fence | 在 notify 前保证远程 store 已被对端可见 |
| `NPUUtils().get_aivector_core_num()` | 取 Vector Core 数（非 AICore 数） | 决定 launch grid：`kernel_hccl_reverse_a2a_pipelined[vec_num, 1, 1](...)` |

上下游链路（基于原文"EP MoE 场景"一节）：
1. **Forward All2All (Dispatch)** → `A` 来源（expert GEMM 输入）；
2. **Expert GEMM** → 本步 kernel 的输入 `A`；
3. **本 kernel（Reverse All2All / Combine）** → 输出 `C`；
4. `C` → 后续 EP MoE 层下游。

UDMA 优化版本（Ascend 950）把"跨卡数据交换"与"本地数据重排"拆成两阶段处理，是 MTE 版本在 950 UDMA 链路上的替代实现，文档以小节标题提示（"UDMA 优化实现"），但**原文未给出该版本的详细代码与参数**（用户提供的原文在 Producer 末尾 notify 段落被截断，未含 UDMA 章节正文）。

---

## 【使用方法】

以下均按原文给出（**未出现于原文的启用方式/配置项不做臆造**）：

### 1. kernel 函数定义（原文逐字保留）

```python
import triton
import triton.language as tl
import triton_dist.language as dl
from triton_dist.language.extra import libshmem_device
from triton.backends.ascend.driver import NPUUtils

@triton.jit
def kernel_hccl_reverse_a2a_pipelined(
    a_ptr,                           # 输入 tensor: shape (S_total, H, D)
    c_ptr,                           # 输出 tensor: shape (S, H * world_size, D)
    peer_mem_ptr,                    # 对称内存指针
    signal_mem_ptr,                  # 信号内存指针 (int64)
    rank,                            # 当前 rank ID（host 侧）
    rank_size,                       # rank 总数（host 侧）
    buffer_num,                      # 双缓冲数量
    S, H, D,                         # tensor 维度 (S = S_total / rank_size)
    stride_as, stride_ah, stride_ad, # 输入 strides
    stride_cs, stride_ch, stride_cd, # 输出 strides
    COMM_BLOCK_S: tl.constexpr,      # S 维 tile 大小
    COMM_BLOCK_D: tl.constexpr,      # D 维 tile 大小
):
    ...
```

### 2. Launch 方式（原文逐字保留）

```python
from triton.backends.ascend.driver import NPUUtils

vec_num = NPUUtils().get_aivector_core_num()  # Vector Core 数（非 AICore 数）
kernel_hccl_reverse_a2a_pipelined[vec_num, 1, 1](...)
```

> 原文："kernel 以 **Vector Core 总数** 而非 AICore 数 launch。"

### 3. Tile 大小配置项（原文）

| 参数 | 类型 | 作用 |
|---|---|---|
| `COMM_BLOCK_S` | `tl.constexpr` | S 维 tile 大小（`num_blocks_s = tl.cdiv(S, COMM_BLOCK_S)`） |
| `COMM_BLOCK_D` | `tl.constexpr` | D 维 tile 大小（`num_blocks_d = tl.cdiv(D, COMM_BLOCK_D)`） |
| `buffer_num` | runtime arg | 双缓冲槽数（按 `buffer_id = global_id_s % buffer_num` 切换） |

### 4. 关键原语调用示例（原文）

- 跨卡地址映射：`remote_ptr = dl.symm_at(peer_mem_ptr, target_rank)`
- Producer 等待信号：`dl.wait(remote_signal_ptr + offset, 1, "gpu", "acquire", waitValue=0)`
- Producer 写远端：`tl.store(remote_ptr_dummy + peer_offs_write, a_data, mask=mask)`
- 跨卡 fence：`libshmem_device.fence()`
- Producer 通知对端：`dl.notify(signal_mem_ptr + offset, target_rank)`
- Consumer 通知自身（重置）：`dl.notify(signal_mem_ptr + offset, rank, 0)`

### 5. 边界 mask（原文）

```python
offs_s = global_id_s * COMM_BLOCK_S + tl.arange(0, COMM_BLOCK_S)
offs_d = block_id_d * COMM_BLOCK_D + tl.arange(0, COMM_BLOCK_D)
mask = (offs_s < S)[:, None] & (offs_d < D)[None, :]
```

作用：处理非对齐 S 与 D 维的尾部 tile。

---

**附注**：用户提供的原文在 Producer 末尾 notify 段落被截断（"...`+ tmp * 8, target_"），"UDMA 优化实现"小节的正文未包含在提供的片段中；因此上述解读中所有数据、参数、布局均严格来源于用户给出的原文片段，未做任何外推。
