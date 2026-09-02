# Paged Attention

> 仓 `vllm` · 路径 `docs/design/paged_attention.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/paged_attention.md

# vLLM `docs/design/paged_attention.md` 一体化深度解读

---

## 【定位】

这篇文档是对 vLLM 上游镜像中 Paged Attention 多头查询注意力 CUDA kernel 的**历史性设计说明**,基于 vLLM 原始论文 (arXiv:2309.06180),目的是**自顶向下解释 `csrc/attention/attention_kernels.cu` 中 paged KV cache 兼容的多头查询注意力 kernel 实现的关键概念、内存布局、线程分工与计算流程**,帮助读者把握高层逻辑后能更容易读懂实际代码;文档开头明确声明"**It no longer describes the code used in vLLM today**"(已不再描述 vLLM 当前的代码)。

---

## 【技术要点】

1. **专用 kernel + 分页 KV cache 布局**:vLLM 采用自研的多头查询注意力 kernel (`csrc/attention/attention_kernels.cu`),其 KV cache 按"block"分页存储,**注意此处 block 与 GPU thread block 不同**(文档后续以 "block" 指 vLLM 分页单元,以 "thread block" 指 GPU 线程块),kernel 必须兼容这种分页布局,通过精心设计的内存布局与访存模式来获取高性能。

2. **核心模板参数 (编译期确定)**:
   - `scalar_t`: 元素数据类型,例如 FP16。
   - `HEAD_SIZE`: 每个 head 的元素数。
   - `BLOCK_SIZE`: 每个 block 包含的 token 数。
   - `NUM_THREADS`: 每个 thread block 的线程数。
   - `PARTITION_SIZE`: 张量并行的 GPU 数 (为简化,文档假设为 0,即未启用张量并行)。

3. **四大核心指针 (运行期参数)**:
   - `out`: `[num_seqs, num_heads, max_num_partitions, head_size]` 指向输出全局内存。
   - `q`: `[num_seqs, num_heads, head_size]` 指向 query 全局内存。
   - `k_cache`: `[num_blocks, num_kv_heads, head_size/x, block_size, x]` 指向分页 key cache。
   - `v_cache`: `[num_blocks, num_kv_heads, head_size, block_size]` 指向分页 value cache。

4. **关键概念体系**:Sequence / Context / Vec / Thread group (`THREAD_GROUP_SIZE`) / Block (`BLOCK_SIZE`) / Warp (`WARP_SIZE=32`) / Thread block (`NUM_THREADS`、`NUM_WARPS`) / Grid,这些粒度共同决定了"每个线程/warp/thread block 在哪些数据上做点积"。

5. **Vec 尺寸的硬性约束**:对 query 与 key,Vec 大小 (`VEC_SIZE`) 是按"**每个 thread group 一次取并算 16 字节**"确定的;对 value,Vec 大小 (`V_VEC_SIZE`) 是按"**每个 thread 一次取并算 16 字节**"确定的。例如当 `scalar_t` 为 FP16 (2 字节) 且 `THREAD_GROUP_SIZE=2` 时,`VEC_SIZE=4`、`V_VEC_SIZE=8`。

6. **Grid 与工作分工**:Grid 形状为 `(num_heads, num_seqs, max_num_partitions)`,**每个 thread block 只处理一个 head × 一个 sequence × 一个 partition**;每个 warp 处理"一个 query token 与一个 block 内全部 key token"的点积 (可在多轮迭代中处理多个 block);**整 thread block 处理一个 query token 与整个 context 全部 key token 的计算**;kernel 为 single-query attention kernel,即**每个 sequence 在一次 kernel 内只对应一个 query token**,因此 `num_seqs` 等于该 batch 中正在处理的 token 总数。

---

## 【关键机制与数据】

### ① Query 侧机制 (内存布局与访存)
- 每个 thread group 一次取一个 query token 数据,每个 thread 仅处理该 token 的一部分。
- **每个 thread 独立计算 `q_ptr`**(原文代码):

  ```cpp
  const scalar_t* q_ptr = q + seq_idx * q_stride + head_idx * HEAD_SIZE;
  ```
- **每个 thread group 内的全部 thread 实际上取到同一 query token**,但会与该 warp 内分配的**不同 key token** 做点积;这一隐含语义在原文 "Within each warp, every thread group will fetch the same query token data, but will multiply it with different key token data." 中给出。

### ② Query 数据加载到共享内存
- 通过共享内存变量缓加载结果(原文代码):

  ```cpp
  __shared__ Q_vec q_vecs[THREAD_GROUP_SIZE][NUM_VECS_PER_THREAD];
  ```
- **每个 vec 被分到不同行**:原文明确"if `THREAD_GROUP_SIZE=2`, thread 0 负责第 0 行 vecs, thread 1 负责第 1 行 vecs";这种交错使相邻 thread 读相邻内存,**达成 memory coalescing 以提升性能**。
- 原文给出的实例:"if `VEC_SIZE=4` and `HEAD_SIZE=128`, `q_ptr` 指向 128 个元素的数据,这些元素被划分为 128/4 = **32 个 vecs**"。

### ③ Key 侧机制 (与 Query 的对比)
- 与 Query 不同,**每个 thread group 虽然一次只处理一个 query token,但会在多轮迭代中处理多个 key token**(原文:"each thread group only handle one query token one kernel run, it may handle multiple key tokens across multiple iterations")。
- 每个 warp 通过多轮迭代处理多个 block 的 key token,**确保经整个 kernel 跑完后 thread group 覆盖整个 context 的全部 token**。
- 原文给出 `k_ptr` 计算代码(在最后段落的开头,**文档原文在此处被截断**,仅保留了 `k_ptr` 的指针算式起始部分即戛然而止):

  ```cpp
  const scalar_t* k_ptr = k_cache + physical_block_number * kv_block_stride
                      + kv_head_idx * kv_head_stride
                      + physical_block_offset * x;
  ```
  后续"在每个 thread 中 `k_ptr` 会指向不同 key token ..."一句**原文档在此处中断**,未继续展开。

### ④ 工作分配实例 (Warp × Block)
- 原文给出 4 warps × 6 blocks 的具体分配示例 (1 个 context):
  - warp 0 → 第 0、第 4 block;
  - warp 1 → 第 1、第 5 block;
  - warp 2 → 第 2 block;
  - warp 3 → 第 3 block。
- 这展示了一种"**轮询分配 block 给 warp**"的循环调度范式(原文:"it may process multiple blocks in multiple iterations")。

### ⑤ Vec 与 Thread group 的相互计算例子
- 原文:"if the thread group contains 2 threads and the head size is 8, then thread 0 handles the query and key elements at index 0, 2, 4, 6, while thread 1 handles the elements at index 1, 3, 5, 7",即**同一 thread group 内的 thread 按 stride-2 交错拆分管线**。

### ⑥ Block 容量计算实例
- 原文:"if the block size is 16 and the head size is 128, then for one head, one block can store 16 * 128 = **2048 elements**"。

> 备注:原文在 "## Key" 章节末尾被截断,后续 Key 内存布局细节、Reduction、Softmax、Output 等章节在提供的文本中**不存在**,因此本节不再补写。

---

## 【表格解读】

**原文无表格**(原文全部以 prose、代码块、Markdown 图片引用呈现,没有任何 markdown 表格或表格化配置项)。

> 唯一类表格化的信息是 "Concepts" 一节中以 "**`THREAD_GROUP_SIZE` / `BLOCK_SIZE` / `WARP_SIZE=32` / `NUM_THREADS`" 等命名常量串成的概念清单,但这不是表格。下表为**便于解读**对原文**逐字保留**所列关键参数后做的"还原展示",并非原文表格:

| 概念 (原文术语) | 原文逐字定义 / 例子 |
|---|---|
| Sequence | "A sequence represents a client request. For example, the data pointed to by `q` has a shape of `[num_seqs, num_heads, head_size]`. … each sequence only has one query token." |
| Context | "The context consists of the generated tokens from the sequence. For instance, `["What", "is", "your"]` are the context tokens, and the input query token is `"name"`. The model might generate the token `"?"`." |
| Vec (Query/Key) | "the vec size (`VEC_SIZE`) is determined so that each thread group can fetch and calculate 16 bytes of data at a time" |
| Vec (Value) | "For value data, the vec size (`V_VEC_SIZE`) is determined so that each thread can fetch and calculate 16 bytes of data at a time" |
| Vec 数字示例 | "if the `scalar_t` is FP16 (2 bytes) and `THREAD_GROUP_SIZE` is 2, the `VEC_SIZE` will be 4, while the `V_VEC_SIZE` will be 8" |
| Thread group | "a small group of threads (`THREAD_GROUP_SIZE`) that fetches and calculates one query token and one key token at a time" |
| Thread group 拆分工 | "thread 0 handles the query and key elements at index 0, 2, 4, 6, while thread 1 handles the elements at index 1, 3, 5, 7" |
| Block | "stores data for a fixed number (`BLOCK_SIZE`) of tokens at one head" |
| Block 容量 | "if the block size is 16 and the head size is 128, then for one head, one block can store 16 * 128 = 2048 elements" |
| Warp | "a group of 32 threads (`WARP_SIZE`) that execute simultaneously on a stream multiprocessor (SM). In this kernel, each warp processes the calculation between one query token and key tokens of one entire block at a time" |
| Warp 调度示例 | "warp 0 handles the 0th, 4th blocks, warp 1 handles the 1st, 5th blocks, warp 2 handles the 2nd block and warp 3 handles the 3rd block" |
| Thread block | "a group of threads (`NUM_THREADS`) that can access the same shared memory. Each thread block contains multiple warps (`NUM_WARPS`)" |
| Thread block 工作 | "each thread block processes the calculation between one query token and key tokens of a whole context" |
| Grid | "the shape is `(num_heads, num_seqs, max_num_partitions)`. Therefore, each thread block only handles the calculation for one head, one sequence, and one partition" |

---

## 【公式解读】

原文未给出数学公式 (LaTeX 形式)。但作为"逐字保留"地把 kernel 中具有公式含义的代码片段完整列出并加以解读,这是本设计文档中唯一属于"公式"角色的内容:

### 公式 1:`paged_attention_kernel` 函数签名

原文逐字:

```cpp
template<typename scalar_t, int HEAD_SIZE, int BLOCK_SIZE, int NUM_THREADS, int PARTITION_SIZE = 0>
__device__ void paged_attention_kernel(
    ... // Other side args.
    const scalar_t* __restrict__ out,       // [num_seqs, num_heads, max_num_partitions, head_size]
    const scalar_t* __restrict__ q,         // [num_seqs, num_heads, head_size]
    const scalar_t* __restrict__ k_cache,   // [num_blocks, num_kv_heads, head_size/x, block_size, x]
    const scalar_t* __restrict__ v_cache,   // [num_blocks, num_kv_heads, head_size, block_size]
    ... // Other side args.
)
```

| 符号 | 含义 / 作用 |
|---|---|
| `scalar_t` | query/key/value 数据元素的运行时类型(如 FP16),编译期模板形参 |
| `HEAD_SIZE` | 每个 head 的元素数量 |
| `BLOCK_SIZE` | 每个 vLLM 分页 block 内的 token 数 |
| `NUM_THREADS` | 每个 GPU thread block 内的线程数 |
| `PARTITION_SIZE` | 张量并行的 GPU 数;`PARTITION_SIZE=0` 表示未启用张量并行 |
| `out` | 输出张量指针,逐 sequence/head/partition 写入 |
| `q` | 输入 query,总 token 数 = `num_seqs`(single-query attention) |
| `k_cache` | 分页 key cache,布局为 `[num_blocks, num_kv_heads, head_size/x, block_size, x]`,按 x 维分块以便 thread group 内 thread 拆分 |
| `v_cache` | 分页 value cache,布局为 `[num_blocks, num_kv_heads, head_size, block_size]`,与 key 的 layout 略有不同 |

### 公式 2:Query 指针 (每 thread 独立)

原文逐字:

```cpp
const scalar_t* q_ptr = q + seq_idx * q_stride + head_idx * HEAD_SIZE;
```

| 符号 | 含义 |
|---|---|
| `q` | query 起点指针 |
| `seq_idx` | 当前 thread block 所对应的 sequence 索引 |
| `q_stride` | sequence 维度的步长(即跨越一个 sequence 全部 head×head_size 元素) |
| `head_idx` | 当前 thread block 所对应的 head 索引 |
| `HEAD_SIZE` | 每个 head 元素数 |
| `q_ptr` | 落到当前 thread block 要处理的 query token 数据起点 |

### 公式 3:共享内存 query 向量缓存

原文逐字:

```cpp
__shared__ Q_vec q_vecs[THREAD_GROUP_SIZE][NUM_VECS_PER_THREAD];
```

| 符号 | 含义 |
|---|---|
| `Q_vec` | query 元素的 vec 类型(对应 vec 化加载单元) |
| `THREAD_GROUP_SIZE` | 一个 thread group 内的线程数;既控制数组行数,也对应"读 16 字节 / thread group"的 vec 大小约束 |
| `NUM_VECS_PER_THREAD` | 单个 thread 需要处理的 vec 数量 |
| `q_vecs` | 全 thread block 共享的 query 缓存,布局使 thread 0 占用第 0 行 vecs、thread 1 占用第 1 行 vecs 等,便于 coalesced load |

### 公式 4:Key 指针 (每 thread 因 iter 不同指向不同 token)

原文逐字:

```cpp
const scalar_t* k_ptr = k_cache + physical_block_number * kv_block_stride
                    + kv_head_idx * kv_head_stride
                    + physical_block_offset * x;
```

| 符号 | 含义 |
|---|---|
| `k_cache` | 分页 key cache 起点 |
| `physical_block_number` | 当前 thread 迭代到的物理 block 号 (vLLM 通过 block table 将逻辑 block 映射到物理 block) |
| `kv_block_stride` | 跨越一个 block 内全部数据的步长 |
| `kv_head_idx` | KV head 索引 |
| `kv_head_stride` | 跨越一个 KV head 全部数据的步长 |
| `physical_block_offset` | block 内 token 偏移 |
| `x` | 一个 thread group 一次能处理的总元素数 (`= THREAD_GROUP_SIZE × (vec size per thread)`) |
| `k_ptr` | 当前 thread 在本轮迭代中要处理的 key token 数据起点 |

> 注:该公式对应的"具体计算细节"上下文在原文档此处被截断,后续 `k_ptr` 的迭代更新与 reduction 流程**原文未给出**。

---

## 【关联】

1. **核心实现入口**:文档明确将实现位置指明在 `csrc/attention/attention_kernels.cu`,这是文档与代码仓的直接关联。

2. **上层理论来源**:文档以 ⚠️ 框开头引用了 [vLLM 原始论文 (arXiv:2309.06180)](https://arxiv.org/abs/2309.06180),说明该文档的 Paged Attention kernel 设计逻辑源自该论文,论文中的 PagedAttention 算法(paged KV cache、block table 逻辑到物理块映射)是该 kernel 的理论基础。

3. **配套模块**:文档明确指出 vLLM 的 KV cache 是分页的 ("vLLM's paged KV caches"),**因此本 kernel 与 vLLM 的 block manager / KV cache manager 紧密耦合**——`physical_block_number` 等指针算式暗示调用方需持有 block table 才能将逻辑块号翻译成物理块号;该 block manager 不在本篇文档讨论范围内,但属于该 kernel 的隐含上游依赖。

4. **GPU 并行模型**:文档与 CUDA 概念 (Warp `WARP_SIZE=32`、Thread block、Grid、Shared memory) 紧密相关,与 CUDA Programming Guide 所述概念一一对应,可将本文视为"vLLM PagedAttention kernel 的 CUDA 实现笔记"。

5. **其他 vLLM 机制**:文档未提到 chunked prefill、continuous batching、speculative decoding 等其他 vLLM 特性,但这些特性在调度时同样会调用该 attention kernel,因此该 kernel 是 vLLM 推理栈**多个调度/特性共享的下层基础**;本文档未列出具体内部链接或目录条目。

6. **状态时效性**:文档自我声明 "It no longer describes the code used in vLLM today",意味着读者应把该文档视为**对早期 kernel 实现的历史性文档**,而非当前 vLLM (`main` 分支) attention kernel 的描述——这一时间维度的关联(旧版 vs 当代)对维护者尤为重要。

---

## 【使用方法】

原文未涉及。该文档是**设计/教学型**说明,而非操作指南,文中没有给出任何启用、配置项、CLI 命令、环境变量或 Python API 调用样例。要使用 vLLM 的 Paged Attention,**请查阅 vLLM 当前的官方推理使用文档**,而非本文档(原文已声明"no longer describes the code used in vLLM today")。

如需在源码层面验证本文档所述概念,可参考原文给出的入口文件 `csrc/attention/attention_kernels.cu`。

---

**总结提示**:本文档只覆盖到 Query / Key 的内存布局与指针算式,**原文档在 "## Key" 小节末尾截断**,因此对 Key 的迭代更新、Attention Score 计算、Softmax、Value 加载、Output 归约等后续阶段,**原文未提供任何信息,本文不做臆造补完**。

## 图文联合解读

- `query.png`: **图解读：**

1）图中显示一个 Query（单 Token、单 Head）的水平条带，被等分为 32 个向量片段（vec0–vec31），中间段标记为 `q_ptr`，总长度为 HEAD_SIZE / VEC_SIZE。

2）论证：单个 head_size 的查询向量按 VEC_SIZE 分块向量化（如 32 个向量），便于 CUDA kernel 以向量为单位做连续内存加载，提高带宽利用率。

3）与文档关系：对应文档所述"特设的内存布局与访问方式"——kernel 以向量粒度从 global memory 读 Query 数据，是实现 Paged KV Cache 高性能 attention kernel 的基础步骤。
- `q_vecs.png`: **图示解读：**

1) **结构**：二维网格展示 q_vecs 在线程间的分配。两行（thread0/thread1）标记为 THREAD_GROUP_SIZE，多列（vec0、vec2…vec30 / vec1、vec3…vec31）标记为 NUM_VEC_PER_THREAD，索引交替排列（偶数给 thread0，奇数给 thread1）。

2) **技术结论**：相邻 query 向量被交错映射到不同线程，形成跨线程的交错访问模式，便于从全局内存合并读取到共享内存，提高带宽利用率。

3) **与文档关系**：对应文中"专门设计的内存布局与访问方式"——即核函数将 q 向量按交错方式切分给线程组，是实现 Paged Attention 高性能访存的布局细节之一。
- `key.png`: **图文联合解读：**

图示为单个Context、单个Head的Key cache内存布局：多个block（block0–block4）按token顺序排列，每block由warp并行处理（warp1→block1，依此类推）。聚焦框内展示单block内部二维组织——横轴`THREAD_GROUP_SIZE`为线程组维度，纵轴`HEAD_SIZE/x`为head维切片，内含vec0–vec31共32个向量单元，对应"Warp0 Block0 Token0"。`inner loop`纵向遍历block内token，`outer loop`横向遍历跨block的序列。

**技术结论：** 该图论证了GPU线程（warp/thread）到vLLM paged KV block的映射方案——通过二维分块+内外循环分解，实现从全局内存到共享内存的合并高效访问。

**与文档关系：** 直观对应文中"特制的内存布局与访问方式"及"vLLM paged KV caches with separate blocks"的核心论点，是`csrc/attention/attention_kernels.cu`中数据排布的高层视图。
- `k_vecs.png`: 1) 图示单个线程（thread0）的向量分配：以横向条形划分等长槽位，左侧vec0/vec2…右侧vec28/vec30，中部粗体k_vecs代表该线程负责的key向量段，总量由NUM_VEC_PER_THREAD限定。

2) 论证每个线程通过均匀分摊固定数量的向量槽（k_vecs为关注重点）实现并行访存，便于从全局内存按规则加载到共享内存。

3) 与文档呼应：正是"为高性能而设计的内存布局与访问方式"——线程级向量划分是paged KV cache分块读取的基础，使attention kernel高效运行。
- `value.png`: **1) 图示内容**：展示V cache在paged布局下的内存排布。纵轴"inner loop HEAD_SIZE"遍历head内维度，横轴"outer loop"遍历各block。每个Block（如Block0）归属一个Warp（Warp0），块内thd0/thd1两线程分别加载v_vec0/1…v_vec224/225；后续Warp1-3依次对应Block1-3。

**2) 技术结论**：采用"一Warp一Block、线程沿HEAD_SIZE分片"的内存排布，实现跨warp并行、跨线程向量化加载，利于全局内存到共享内存的合并访存。

**3) 与文档论点关系**：直观印证文档所述"专为paged KV cache设计的内存布局与访存方式"，是kernel高效并行读取数据流的可视化说明。
- `logits_vec.png`: **图文联合解读：**

图示为一个`logits_vec`向量，两端以虚线小框标出首末token（tk0、tk1 与 tk6、tk7），中间主体为`logits_vec`内容区。

**技术含义**：在vLLM Paged Attention kernel中，向量首末少数token为边界/上下文关键token，需单独特殊处理（如拼接prefix/suffix），中间大量token则可批量按统一block访存并行计算。

**与文档关系**：印证"特殊设计的内存布局与访问方式"——kernel将首末边界token与中间常规token分离处理，减少冗余计算，提升GPU shared memory访存效率，支撑Paged Attention高吞吐推理。
- `v_vec.png`: **图文联合解读：**

1）图中描绘了 vLLM 注意力 kernel 中单个 thread0 的 V 向量访存布局：纵轴按 head 偏移（0、16、…、112）划分 8 个迭代轮次（iter0–iter7），横轴每行承载 NUM_ROWS_PER_THREAD 个 token 槽位（tk0–tk7），整体高度为 V_VEC_SIZE。

2）该图论证了 kernel 的数据划分策略：每个线程按 head 步长交错迭代、固定每轮处理 NUM_ROWS_PER_THREAD 行，使全局内存读取可合并，从而在 paged KV cache 布局下实现高效的 global→shared memory 加载。

3）呼应文档论点：图示正是文档所强调的"为兼容分页 KV cache 而设计的特殊内存布局与访存方式"，直观展示 vLLM 自研 attention kernel 的线程—head—迭代三级映射，是高吞吐实现的内存基础。
