# autotune 样例：UDMA Reverse All2All 增量优化实践

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/zh/tutorial/autotune_optimization_example.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/zh/tutorial/autotune_optimization_example.md

# 一体化深度解读：autotune 样例：UDMA Reverse All2All 增量优化实践

---

## 【定位】

这篇文档解决的是 **"如何在不改动 Triton Kernel 本体的前提下，为已存在的 Ascend UDMA Reverse All2All Host launcher 增量接入 `triton_dist.tune.autotune` 函数级自动调优"** 这一具体工程问题，提供从配置空间定义、缓存键、剪枝、Host 包装、分布式选优到导出最佳配置与运行的完整增量改造方案。

---

## 【技术要点】

1. **函数级（Host 端）调优而非 Kernel 内调优**：使用 `triton_dist.tune.autotune` 装饰器包住普通 Python Host 包装函数，**不**在 Triton Kernel 内加 `@triton.autotune`，因此 Kernel UDMA 通信逻辑保持不变。

2. **配置空间 = 笛卡尔积 5 × 2 × 4 = 40 组候选**：
   - `COMM_BLOCK_S ∈ [32, 64, 128, 256, 512]`（序列维通信分块）
   - `COMM_BLOCK_D ∈ [64, 128]`（特征维数据分块）
   - `buffer_num ∈ [2, 3, 4, 8]`（流水缓冲区数量）
   - 配置字典字段名与 Host launcher 同名参数对应，**调优器自动注入**。

3. **缓存键 = `(TUNE_SPACE_VERSION, tuple(A.shape), tuple(C.shape), rank_size)`**：
   - `TUNE_SPACE_VERSION = "reverse-a2a-udma-autotune-v1"`，搜索空间语义变化时需更新以隔离旧缓存；
   - 故意**不**放入 `rank` 和 Tensor 地址——多 rank 须选同一全局配置，且地址不应影响命中；
   - 样例固定 `torch.bfloat16`，扩展 dtype / 运行模式时须把相应信息加入 key。

4. **`_prune` 六条过滤规则**（原文）：缓冲区冗余（`bn > num_blocks_s`）、`bs==128 and bd==128` 直接保留、分块越界（`bs > S` 或 `bd > D`）、S 利用率 `< 0.75`、D 利用率 `< 0.75`、数据块过大（`bs * bd * element_size > 128 * 1024`）。`_prune` 只裁过滤，**最佳仍由实测耗时决定**。

5. **分布式选优机制**：调用时传 `autotune=True` 与 `autotune_pg=process_group`；框架对每个候选耗时在多 rank 上做 `all_reduce(MAX)`，以最慢 rank 耗时为全局结果，选全局耗时最小者；当前归约使用默认 **WORLD group**（与新创建 `process_group` 含相同 rank）。

6. **资源容量按"覆盖所有候选"准备**：用 `min_bs`、`max_bn` 以及各候选 `triton.cdiv(D, COMM_BLOCK_D)` 最大值计算 `signal_mem_size`，避免大候选因辅助内存不足而调优失败。环境变量 `REV_PROFILE_WARMUP=5`、`REV_PROFILE_ITERS=50` 仅控制**选出后的稳态计时**；函数级调优器内部固定 **5 次预热、10 次计时**。

7. **缓存与强制重调**：`~/.triton_dist/autotune/` 为磁盘缓存目录；`TRITON_DIST_AUTOTUNE_ALWAYS_TUNE=1` 强制忽略已有结果重新搜索。

---

## 【关键机制与数据】

### 1) 增量改造的工作原理（数据流视角）

```
常量区新增 TUNE_CONFIG_SPACE / TUNE_SPACE_VERSION
        ↓
_key_fn(_autotune_key) 基于 (version, A.shape, C.shape, rank_size) 生成缓存键
        ↓
调用 Host 包装器（_function_autotuned_hccl_reverse_a2a_udma）
        ├─ 首次：_prune 过滤 40 组候选 → 重复执行完整算子（reset signal_mem + dist.barrier） → 各 rank all_reduce(MAX) 选优 → 写入 ~/.triton_dist/autotune/
        └─ 命中：best_configs.get(key) 直接取缓存配置
        ↓
稳态阶段：_prepare_reverse_launch(...) 用最佳配置运行 → rank 0 写 manifest；全员写 CSV
```

### 2) 关键设计原则（原文摘录 / 标注）

- **可复位性要求**（原文）："被调优 Host 函数会重复执行，输入、通信缓冲区和同步状态必须可复位"——包装器内部以 `signal_mem.fill_(0)` + `dist.barrier()` 保证每次候选起跑条件一致。
- **一致性要求**（原文）："所有 rank 的 key、配置空间和裁剪结果必须一致"，否则 all_reduce(MAX) 选优将失效。
- **首项必须可执行**（原文）："搜索空间第一项应保证可执行，供 `autotune=False` 时直接使用"。
- **统计分离原则**（原文）："首次调优耗时与最佳配置的稳态性能应分开统计"——分别通过 manifest 调优耗时与 CSV 稳态耗时体现。
- **范围安全（128 KiB 上限，原文）**：`bs * bd * A.element_size() > 128 * 1024` 直接裁掉——这是 UDMA 单次搬运块大小的硬性经验阈值。
- **分布式同步细节（原文）**："当前最终耗时归约使用默认 WORLD group，因此样例创建的 `process_group` 与 WORLD 包含相同 rank"——这意味着此版本虽提供 `autotune_pg`，但归约阶段实际仍走 WORLD。

### 3) 性能/容量数据（原文）

- 总候选数：40（原文：`5 × 2 × 4 = 40`）。
- 数据块过滤阈值：128 KiB（原文：`bs * bd * A.element_size() > 128 * 1024`）。
- 利用率阈值：0.75（原文：S、D 两维利用率过滤均使用该值）。
- 稳态环境变量：预热 5、迭代 50（原文：`REV_PROFILE_WARMUP=5`、`REV_PROFILE_ITERS=50`）。
- 函数级调优器内部固定值：预热 5、计时 10（原文：明确说明不随 `REV_PROFILE_*` 改变）。

---

## 【表格解读】

### 原文表 1（修改概览）

| 增量修改 | 作用 |
| --- | --- |
| 引入 `triton_dist.tune` | 使用函数级 autotune 接口 |
| 增加 `TUNE_CONFIG_SPACE` | 定义 Host launcher 的候选参数 |
| 增加 `_autotune_key` | 按 shape 和 rank 数复用最佳配置 |
| 增加 `_prune` | 在计时前过滤无效候选 |
| 增加 autotune Host 包装器 | 重复运行完整算子并注入候选参数 |
| 调用时传入 `autotune_pg` | 按多 rank 最大耗时选择配置 |
| 读取 `best_configs` | 使用并导出当前 shape 的最佳配置 |

**逐行解读：**
- **引入 `triton_dist.tune`**：由 Kernel 内 `@triton.autotune` 改为 Host 函数级 `triton_dist.tune.autotune` 装饰器，作用域上移到 Python 层，可承载分布式 rank 协同。
- **TUNE_CONFIG_SPACE**：纯 Python dict list，调优器在每次候选测试时把键名当作 kwargs 注入被包装函数，因此必须与 launcher 形参严格同名（`COMM_BLOCK_S / COMM_BLOCK_D / buffer_num`）。
- **`_autotune_key`**：去掉了 `rank` 与地址，仅保留语义信息，使多 rank 共享同一最优配置；版本号隔离配置空间变化。
- **`_prune`**：在计时前淘汰已知无效候选，缩短首调耗时；只过滤不排序。
- **autotune Host 包装器**：唯一"重复执行"算子的入口；同时承担状态复位（`signal_mem.fill_(0)` + `dist.barrier()`），保证候选间起跑条件一致。
- **`autotune_pg`**：开启多 rank 同步与"最慢 rank 耗时为全局耗时"的归约语义，是分布式选优开关。
- **`best_configs`**：字典式结果，`key = _autotune_key(...)`，稳态阶段与 manifest 导出都基于它。

---

## 【公式解读】

### F1. 序列块数（原文，`_prune` 内）

$$\text{num\_blocks\_s} = \lceil S / bs \rceil$$

- 符号：`S = A.shape[0] // rank_size`（每 rank 上的序列长度），`bs` = `COMM_BLOCK_S`。
- 作用：作为 "流水线缓冲区是否冗余" 与 "S 维利用率" 的分母。

### F2. 缓冲区冗余裁剪（原文）

$$bn > \lceil S / bs \rceil \;\Longrightarrow\; \text{裁掉}$$

- 含义：当流水线缓冲数多于序列块数时，多余 buffer 无事可做，直接裁剪。

### F3. S 维利用率裁剪（原文）

$$\frac{S}{\lceil S / bs \rceil \cdot bs} < 0.75 \;\Longrightarrow\; \text{裁掉}$$

- 含义：分块后实际承载比例不足 75% 即认为浪费严重。

### F4. D 维利用率裁剪（原文）

$$\frac{D}{\lceil D / bd \rceil \cdot bd} < 0.75 \;\Longrightarrow\; \text{裁掉}$$

- 含义：特征维分块利用率不足 75% 视为浪费。

### F5. 数据块上限（原文）

$$bs \cdot bd \cdot \text{element\_size} > 128 \times 1024 \;\Longrightarrow\; \text{裁掉}$$

- 含义：单次搬运字节数超过 128 KiB 直接淘汰——这是 UDMA 通道对单块大小的硬性经验上限。

### F6. 资源容量覆盖（原文 §5）

$$
\begin{aligned}
\min\_bs &= \min_{c \in \text{TUNE\_CONFIG\_SPACE}}\, c[\text{COMM\_BLOCK\_S}] \\
\max\_bn &= \max_{c \in \text{TUNE\_CONFIG\_SPACE}}\, c[\text{buffer\_num}] \\
\max\_\text{num\_blocks\_d} &= \max_{c}\, \big\lceil D / c[\text{COMM\_BLOCK\_D}] \big\rceil \\
\max\_\text{num\_blocks\_s} &= \big\lceil S / \min\_bs \big\rceil \\
\text{signal\_mem\_size} &= \text{\_signal\_mem\_size}(S, H, D, \text{rank\_size}, \max\_bn, \max\_\text{num\_blocks\_s}, \max\_\text{num\_blocks\_d})
\end{aligned}
$$

- 含义：辅助内存按"最坏情况候选"分配，避免调优过程中大候选因资源不足失败。**注意：原文未提供 `_signal_mem_size` 的具体实现，需结合仓库代码确认。**

### F7. 全局耗时归约语义（原文）

$$T_{\text{global}}(c) = \text{all\_reduce}_{\max}\big(T_{\text{rank}}(c)\big), \quad \forall c \in \text{候选集}$$

- 含义：每个候选以最慢 rank 耗时为全局耗时，再在候选间取最小者。原文特别注明当前归约走 **WORLD group**，而非传入的 `process_group`。

---

## 【关联】

### 内部文档关联

1. **[`../api/autotune_api.md`](../api/autotune_api.md)**——分布式通用 Host 接口：autotune
   - 文中使用的 `triton_dist.tune.autotune(config_space=..., key_fn=..., prune_fn=...)`、`autotune=True`、`autotune_pg=...`、`best_configs.get(key)` 等接口的**正式签名与字段说明**均出自该 API 文档；本文是该 API 在 Reverse All2All 上的"调用样例"。
   - 关联原因：本文未给出 `autotune` 装饰器本身的参数清单，全文末尾直接导向该文档获取接口参数。

2. **[`../developer-guide/kernel-performance/operator_performance_testing_and_tuning_autotune_guide.md`](../developer-guide/kernel-performance/operator_performance_testing_and_tuning_autotune_guide.md)**——算子性能测试与调优：autotune 特性使用介绍
   - 本文是上述"特性使用介绍"在 Reverse All2All 算子上的**具体实践**——前者讲通用原则（配置空间、缓存、剪枝、导出），本文展示从原始 launcher 到 autotune launcher 的**增量 diff 视角**。
   - 关联原因：本文末尾明确指引读者查阅该文档以了解整体流程。

### 与仓库代码的关联

- **原始算子**：[`04-ascend-reverse-all2all.py`](https://gitcode.com/Ascend/Triton-distributed-ascend/blob/master/tutorials/ascend/04-ascend-reverse-all2all/04-ascend-reverse-all2all.py)
- **autotune 样例**：[`06-ascend-reverse-all2all-udma-autotune-bare.py`](https://gitcode.com/Ascend/Triton-distributed-ascend/blob/master/tutorials/ascend/04-ascend-reverse-all2all/06-ascend-reverse-all2all-udma-autotune-bare.py)
- 关系：本文仅说明**两文件之间的增量**（配置空间、key、prune、Host 包装、分布式选优、导出）；Kernel 的 UDMA 通信逻辑保持不变——这构成"增量接入"的核心语义。

### 与上下游模块的关联

- **分布式通信层**：依赖 `dist.new_group(...)` 创建 `process_group`，并使用默认 WORLD group 进行 `all_reduce(MAX)`；rank 间通过 `dist.barrier()` 在每次候选前同步。
- **NPU 工具层**：调用 `NPUUtils().get_aivector_core_num()` 取 vec_num，作为 kernel grid 第一维——表明该改造保留了与 NPU 硬件特性相关的并行粒度。
- **SHMEM 通道**：依赖 `peer_mem`、`signal_mem`（UDMA 的对端内存与同步信号）；`_signal_mem_size` 函数承担资源预算，**原文未涉及**其内部公式（需查仓库代码）。
- **CSV / manifest 持久化**：rank 0 写 `REVERSE_A2A_MANIFEST`、所有 rank 写 `REVERSE_A2A_CSV`（CSV 由原 benchmark 流程承担，autotune 不直接产出）。

---

## 【使用方法】

### 1) 环境准备

- 配置 Ascend、CANN、HCCL、SHMEM 环境变量：
  ```bash
  source /usr/local/Ascend/ascend-toolkit/set_env.sh
  ```

### 2) 稳态计时参数（仅影响最佳配置选出**之后**的稳态测量）

| 变量 | 默认/推荐值 | 作用 |
| --- | --- | --- |
| `REV_PROFILE_WARMUP` | `5` | 稳态阶段预热次数 |
| `REV_PROFILE_ITERS` | `50` | 稳态阶段计时迭代次数 |

> 注：函数级调优器内部固定 5 次预热、10 次计时，不受上述变量影响。

### 3) 输出文件配置

| 变量 | 推荐值 | 作用 |
| --- | --- | --- |
| `REVERSE_A2A_MANIFEST` | `reverse_a2a_udma_autotune_manifest.json` | rank 0 写入每个 shape 的最佳配置（`S / H / D / COMM_BLOCK_S / COMM_BLOCK_D / buffer_num`） |
| `REVERSE_A2A_CSV` | `reverse_a2a_udma_autotune_perf.csv` | 稳态性能 CSV |

### 4) 缓存与强制重调

- 缓存位置：`~/.triton_dist/autotune/`
- 强制重新搜索：`export TRITON_DIST_AUTOTUNE_ALWAYS_TUNE=1`

### 5) 启动命令（仓库根目录下执行）

```bash
export REV_PROFILE_WARMUP=5
export REV_PROFILE_ITERS=50
export REVERSE_A2A_MANIFEST=reverse_a2a_udma_autotune_manifest.json
export REVERSE_A2A_CSV=reverse_a2a_udma_autotune_perf.csv

torchrun --nproc-per-node=<rank_num> \
  06-ascend-reverse-all2all-udma-autotune.py
```

其中 `rank_num` 应与参与运行的 NPU 数量一致。

### 6) 关键调用形态（原文）

```python
process_group = dist.new_group(ranks=list(range(rank_size)))

_function_autotuned_hccl_reverse_a2a_udma(
    A_local, C_local,
    peer_mem, signal_mem,
    rank, rank_size,
    autotune=True,              # 启用搜索或缓存查询
    autotune_pg=process_group,  # 启用多 rank 同步与选优
)

key = _autotune_key(A_local, C_local, peer_mem, signal_mem, rank, rank_size)
best = _function_autotuned_hccl_reverse_a2a_udma.best_configs.get(key)
```

### 7) 配置空间变更协议

修改 `TUNE_CONFIG_SPACE` 的语义时必须同步升级 `TUNE_SPACE_VERSION`（如 `"reverse-a2a-udma-autotune-v1"` → `"...-v2"`），以通过缓存 key 隔离旧结果，避免命中语义不一致的旧配置。

### 原文未涉及的事项

- `_signal_mem_size` 的内部公式与实现细节。
- `triton_dist.tune.autotune` 装饰器的完整参数清单、默认值与异常语义——需查阅 [`../api/autotune_api.md`](../api/autotune_api.md)。
- `best_configs` 的数据结构与跨进程共享机制——同上。
- 候选注入机制（如何把 dict 字段映射为函数 kwarg）的实现位置——同上。
