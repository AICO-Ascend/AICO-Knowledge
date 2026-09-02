# Autotuning Demo: UDMA Reverse All2All Optimization

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/en/tutorial/autotune_optimization_example.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/en/tutorial/autotune_optimization_example.md

# Autotuning Demo: UDMA Reverse All2All Optimization 深度解读

## 【定位】

这篇文档解决的核心问题是：**在不动 Triton Kernel 主体代码的前提下,如何以"增量"方式把 `triton_dist.tune.autotune` 函数级调优器接入已有的 Ascend UDMA Reverse All2All Host launcher**,从而自动搜索通信块大小、流水线缓冲数等参数的最优组合,并在多卡分布式场景下做全局选优与配置导出。

---

## 【技术要点】

1. **函数级 (function-level) autotune 而非 kernel 内 autotune**:`@triton_dist.tune.autotune(...)` 装饰在 Host wrapper 上,Kernel 主体保持不变;通过三个回调(`config_space` / `key_fn` / `prune_fn`)把候选配置、缓存键、剪枝策略注入。

2. **搜索空间规模固定为 40 个候选**:`TUNE_CONFIG_SPACE` 通过三层笛卡尔积生成 `5 × 2 × 4 = 40` 个配置,候选维度是 `COMM_BLOCK_S ∈ {32, 64, 128, 256, 512}`、`COMM_BLOCK_D ∈ {64, 128}`、`buffer_num ∈ {2, 3, 4, 8}`,字典键名与 Host launcher 形参名一一对应以便自动注入。

3. **缓存键 (cache key) 显式排除 rank 与张量地址**:`_autotune_key` 返回 `(TUNE_SPACE_VERSION, tuple(A.shape), tuple(C.shape), rank_size)`,理由是"不同 rank 需要选择相同的全局配置,地址不应影响缓存命中";`TUNE_SPACE_VERSION = "reverse-a2a-udma-autotune-v1"` 用于在搜索空间语义变化时隔离旧缓存。

4. **`_prune` 在计时前过滤明显无效候选**,剪枝条件共 5 条:缓冲冗余(`bn > num_blocks_s`)、白名单直通(`bs==128 and bd==128`)、块越界(`bs > S` 或 `bd > D`)、利用率不足(< 0.75,序列与特征维度各一条)、数据块过大(`bs * bd * A.element_size() > 128 * 1024` 字节)。

5. **资源上限按搜索空间最坏情况预留**:`signal_mem_size` 用 `min_bs`、`max_bn`、`max_num_blocks_d`、`max_num_blocks_s` 计算,保证最大候选也能跑起来,避免 tuning 中途因辅助内存不足失败。

6. **多 rank 分布式选优**:`autotune=True` + `autotune_pg=process_group`;每个候选在所有 rank 上同序执行,框架对计时做 `all_reduce(MAX)` 取最慢 rank 的耗时作为该候选的全局时间,再选全局最小耗时对应的配置;并通过 `_function_autotuned_hccl_reverse_a2a_udma.best_configs.get(key)` 读回当前 shape 的最优配置。

---

## 【关键机制与数据】

**整体工作流 (七步闭环)**:

1. **定义搜索空间**:`TUNE_CONFIG_SPACE` 列举 40 个 `(COMM_BLOCK_S, COMM_BLOCK_D, buffer_num)` 三元组,字典键与 launcher 形参同名,让 tuner 自动注入。
2. **定义缓存键**:`_autotune_key` 用 `(版本, 输入 shape, 输出 shape, rank_size)` 标识"同一种调优情境",保证相同情境可复用历史最优配置。
3. **定义剪枝**:`_prune` 在真正计时前剔除无效候选,降低首次搜索开销;返回 `True` 保留、`False` 剪掉。
4. **包装 Host launcher**:把原 launcher 的可调参数(`buffer_num`, `COMM_BLOCK_S`, `COMM_BLOCK_D`)提升为 wrapper 形参(带默认值),并在 wrapper 内每次候选测试前重置 `signal_mem.fill_(0)` 并 `dist.barrier()`,保证初始条件一致。
5. **资源按搜索空间最坏值预留**:`min_bs` 决定最多 sequence 块数,`max_bn` 决定最多缓冲数,共同决定 `signal_mem` 容量。
6. **发起分布式调优**:用 `dist.new_group` 建组,在所有 rank 上同步调用 `_function_autotuned_hccl_reverse_a2a_udma(..., autotune=True, autotune_pg=process_group)`,框架对每个候选执行 `all_reduce(MAX)` 取全局耗时最小者。
7. **使用并导出最优配置**:用 `best = ...best_configs.get(key)` 拿到当前 shape 的最优参数,送入稳态 launcher 计时;`rank == 0` 把 `(S, H, D, COMM_BLOCK_S, COMM_BLOCK_D, buffer_num)` 写入 JSON manifest。

**关键数据点 (原文)**:
- 候选数:原文明确 `5 × 2 × 4 = 40`。
- 利用率阈值:`< 0.75` 即剪枝 (序列维和特征维各判一次)。
- 单次原子数据块上限:`bs * bd * A.element_size() > 128 * 1024` 字节即剪枝。
- 版本字符串:`"reverse-a2a-udma-autotune-v1"`。
- 例子默认 dtype:固定 `torch.bfloat16`。
- 计时协议:`all_reduce(MAX)` (原文);当前最终归约使用默认 WORLD 组,故示例中新建的 `process_group` 与 WORLD 包含相同 ranks。

**与原 launcher 的差异 (原文)**:仅有"调优参数变成 wrapper 注入形参"和"信号重置 + 屏障移到 wrapper"两处改动,Kernel UDMA 通信逻辑保持不变。

---

## 【表格解读】

| Incremental Modification | Purpose |
| --- | --- |
| Introduce `triton_dist.tune` | Use function-level autotune interface |
| Add `TUNE_CONFIG_SPACE` | Define candidate parameters for Host launcher |
| Add `_autotune_key` | Reuse best configuration by shape and rank count |
| Add `_prune` | Filter invalid candidates before timing |
| Add autotune Host wrapper | Repeatedly run complete operator and inject candidate parameters |
| Pass `autotune_pg` when calling | Select configuration based on multi-rank maximum time |
| Read `best_configs` | Use and export best configuration for current shape |

逐行解读:

1. **Introduce `triton_dist.tune` / Use function-level autotune interface** — 引入项目自带的函数级调优子模块,这是与 Triton 原生 `triton.autotune` (Kernel 级) 的关键区别:本方案把调优装饰在 Host Python 函数上,Kernel 主体完全不动。
2. **Add `TUNE_CONFIG_SPACE` / Define candidate parameters for Host launcher** — 在常量区声明搜索空间,40 个字典条目,键名与 launcher 形参同名,保证 tuner 注入时能正确绑定。
3. **Add `_autotune_key` / Reuse best configuration by shape and rank count** — 用 shape + rank_size + 版本号生成缓存键,避免每次相同输入都重新搜索;同时故意排除 `rank` 与张量地址,使所有 rank 命中同一全局最优。
4. **Add `_prune` / Filter invalid candidates before timing** — 在计时前做剪枝(缓冲冗余、块越界、利用率、数据块大小),只返回 `True` 的配置进入计时阶段,缩短首调耗时。
5. **Add autotune Host wrapper / Repeatedly run complete operator and inject candidate parameters** — 新增 `_function_autotuned_hccl_reverse_a2a_udma`,内部完整复现原 launcher 流程,但每次先 `signal_mem.fill_(0)` + `dist.barrier()`,再以候选参数调用 kernel。
6. **Pass `autotune_pg` when calling / Select configuration based on multi-rank maximum time** — 调用时传 `autotune=True` 与 `autotune_pg=process_group`,启动跨 rank 同步计时,框架内部用 `all_reduce(MAX)` 取最慢 rank 耗时作为该候选全局表现。
7. **Read `best_configs` / Use and export best configuration for current shape** — 调优结束后用 `_autotune_key` 再次算 key,从 `.best_configs` 字典里读回当前 shape 的最优三元组,送稳态 launcher 并由 rank 0 写入 JSON manifest。

---

## 【公式解读】

原文无显式 LaTeX 公式,但给出若干可形式化的关键表达式,逐条逐符号还原与解释:

**(a) 候选总数**

$$N_{\text{cand}} = |BS| \times |BD| \times |BN| = 5 \times 2 \times 4 = 40$$

- $BS = \{32, 64, 128, 256, 512\}$,序列维通信块大小 `COMM_BLOCK_S`。
- $BD = \{64, 128\}$,特征维数据块大小 `COMM_BLOCK_D`。
- $BN = \{2, 3, 4, 8\}$,流水线缓冲数 `buffer_num`。

**(b) 序列维块数**

$$\text{num\_blocks\_s} = \lceil S / bs \rceil$$

- $S = A.\text{shape}[0] / \text{rank\_size}$ (per-rank 序列长度)。
- $bs$ = 当前候选的 `COMM_BLOCK_S`。

**(c) 剪枝条件集合** (任一成立即返回 `False`)

$$
\text{prune}(c) =
\begin{cases}
\text{True}, & bn > \text{num\_blocks\_s} \\
\text{True}, & bs = 128 \land bd = 128 \quad \text{(白名单直通)} \\
\text{False}, & bs > S \lor bd > D \\
\text{False}, & \dfrac{S}{\text{num\_blocks\_s} \cdot bs} < 0.75 \\
\text{False}, & \dfrac{D}{\lceil D/bd \rceil \cdot bd} < 0.75 \\
\text{False}, & bs \cdot bd \cdot \text{element\_size}(A) > 128 \times 1024 \\
\text{True}, & \text{otherwise}
\end{cases}
$$

符号含义:
- $bn$:当前候选的 `buffer_num`。
- $D = A.\text{shape}[2]$:特征维长度。
- $S / (\text{num\_blocks\_s} \cdot bs)$:序列维有效利用率(尾部填充后实际占用比例)。
- $D / (\lceil D/bd \rceil \cdot bd)$:特征维有效利用率。
- $\text{element\_size}(A)$:输入张量单元素字节数 (示例中 `bfloat16` 为 2 字节)。
- $128 \times 1024$:单次搬运数据块字节上限 (原文为 128 KiB)。

**(d) 全局耗时归约**

$$T_{\text{global}}(c) = \max_{r \in \text{pg}} T_r(c) = \text{all\_reduce}_{\text{MAX}}\bigl(T_r(c)\bigr)$$

- $T_r(c)$:rank $r$ 在配置 $c$ 上的计时。
- 最优配置 $c^* = \arg\min_{c \in \text{survivors}} T_{\text{global}}(c)$。

**(e) 资源容量最坏值**

$$
\begin{aligned}
\min bs &= \min_{c \in \mathcal{C}} c[\text{COMM\_BLOCK\_S}] \\
\max bn &= \max_{c \in \mathcal{C}} c[\text{buffer\_num}] \\
\max \text{blocks}_d &= \max_{c \in \mathcal{C}} \text{triton.cdiv}(D,\, c[\text{COMM\_BLOCK\_D}]) \\
\max \text{blocks}_s &= \text{triton.cdiv}(S,\, \min bs)
\end{aligned}
$$

这些值用于计算 `signal_mem_size`,保证搜索空间中"最大缓冲数 + 最细块划分"的最坏组合也有足够信号内存。

---

## 【关联】

从文末内部链接可梳理出本文所处的位置与上下游:

- **API 层** (`../api/autotune_api.md`):本文是 `triton_dist.tune.autotune` API 的具体使用样例,所展示的 `config_space` / `key_fn` / `prune_fn` 三个参数、`best_configs` 字典、`autotune=True` / `autotune_pg` 调用约定都对应 API 文档。
- **开发者调优指南** (`../developer-guide/kernel-performance/operator_performance_testing_and_tuning_autotune_guide.md`):本文是"Operator Performance Testing and Tuning Autotune Guide"在 Reverse All2All UDMA 这一具体算子上的落地演示,共享缓存键、剪枝、分布式选优等设计原则。
- **被调优的原型算子**:`tutorials/ascend/04-ascend-reverse-all2all/04-ascend-reverse-all2all.py`,作为基线;本文示例 `06-ascend-reverse-all2all-udma-autotune.py` (实际链接为 `06-ascend-reverse-all2all-udma-bare.py`) 在它之上做增量改动。
- **Kernel 侧符号**(链接锚点引用):
  - `A` — 输入张量 (`S_total, H, D`)。
  - `C` — 输出张量。
  - `peer_mem` / `signal_mem` — UDMA 跨卡对端内存与同步信号内存。
  - `rank` / `rank_size` — 当前进程号与总进程数。
  - `buffer_num` — 流水线缓冲数 (调优注入参数)。
  - `S`, `H`, `D` — per-rank 序列长、头数、特征维。
  - `A.stride(0, ...)` — 输入张量各维步长,作为 kernel 形参传入。

---

## 【使用方法】

**环境前置**:完成 Ascend、CANN、HCCL、SHMEM 配置 (原文未给出具体步骤)。

**环境变量** (原文给出 4 个):
```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh

export REV_PROFILE_WARMUP=5
export REV_PROFILE_ITERS=50
export REVERSE_A2A_MANIFEST=reverse_a2a_udma_autotune_manifest.json
export REVERSE_A2A_CSV=reverse_a2a_udma_autotune_perf.csv
```

- `REV_PROFILE_WARMUP=5`:稳态计时的 warmup 迭代数。
- `REV_PROFILE_ITERS=50`:稳态计时的有效迭代数。
- `REVERSE_A2A_MANIFEST`:rank 0 写出的最优配置 JSON 文件名。
- `REVERSE_A2A_CSV`:稳态性能结果 CSV 文件名。

**启动命令** (原文末尾被截断,可还原的部分):
```bash
torchrun --nproc-per-node=<rank_num> \
  06-as...
```
原文此处命令不完整,具体脚本名应参考仓库 `tutorials/ascend/04-ascend-reverse-all2all/06-ascend-reverse-all2all-udma-autotune-bare.py`(链接中的 `-bare.py` 文件)。

**调优使能三要素** (调用处必须同时给出):
```python
_function_autotuned_hccl_reverse_a2a_udma(
    A_local, C_local, peer_mem, signal_mem, rank, rank_size,
    autotune=True,              # 启用搜索 / 缓存查询
    autotune_pg=process_group,  # 多 rank 同步与选优
)
```
- `autotune=False` (或省略):不进入调优,直接使用 wrapper 默认值。
- `autotune=True` 但缺 `autotune_pg`:仅单进程本地选优,不进行跨 rank `all_reduce(MAX)`。

**回读最优配置**:
```python
key = _autotune_key(A_local, C_local, peer_mem, signal_mem, rank, rank_size)
best = _function_autotuned_hccl_reverse_a2a_udma.best_configs.get(key)
```
`best` 是与 `TUNE_CONFIG_SPACE` 字典结构相同的子集,含 `COMM_BLOCK_S` / `COMM_BLOCK_D` / `buffer_num` 三个字段。

**版本隔离**:当搜索空间语义发生变化(增删候选、改剪枝规则、改资源计算公式)时,务必更新 `TUNE_SPACE_VERSION` 字符串,否则会沿用旧缓存导致错配。
