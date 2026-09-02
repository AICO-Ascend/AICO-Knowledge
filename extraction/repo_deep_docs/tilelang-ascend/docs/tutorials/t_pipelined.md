# T.Pipelined on TileLang-Ascend

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/t_pipelined.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/t_pipelined.md

# 一体化深度解读:`T.Pipelined on TileLang-Ascend`

---

## 【定位】

这篇文档系统介绍 TileLang-Ascend 中的高层抽象 `T.Pipelined`,用于在 Ascend AI 加速器上以**单核内(intra-core)流水线和跨核间(inter-core)流水线**两种模式表达并优化流水并行,实现计算与访存的细粒度重叠以及 Cube/Vector 核间的同步协作。

---

## 【技术要点】

1. **接口签名**(原文):
   `T.Pipelined(loop_iterations: int, num_stages: int, cross_interval: int = 1)`
   - `loop_iterations`:循环总迭代数(必填)
   - `num_stages`:双缓冲流水级数(必填)
   - `cross_interval`:跨核同步间隔,默认 `1`,仅在 inter-core 下生效

2. **Intra-core 双缓冲模式**(`num_stages=2`):在一核内将 `T.copy`(访存)和 `T.gemm_v0`(计算)通过 `T.barrier_all()` 切分成**预取阶段、主循环阶段、收尾阶段**。原文以 `loop_k=4` 为例,展示 6 个时间槽的执行排布。

3. **Inter-core 流水线(Cube ↔ Vector)**:通过 **workspace buffer** 实现两核间的生产者-消费者模型——Cube 侧 `T.gemm_v0` 写入 `workspace_1`,Vector 侧 `T.copy` 读取后用 `T.tile.add` 累加。原文以 `T.ceildiv(seq_len, block_N)=4`、`num_stages=2` 给出 5 个时间槽的时间线。

4. **跨核同步触发条件**:由 `cross_interval` 控制 `CrossCoreSetFlag`/`CrossCoreWaitFlag` 的触发周期。原文给出 `cross_interval=2, num_stages=4` 时的生成代码片段:`SetFlag` 在 `i % 2 == 1 || i == 3` 时执行,`WaitFlag` 在 `i % 2 == 0` 时执行。

5. **嵌套模式(Nested)被禁止**:`T.Pipelined` 中再嵌套 `T.Pipelined`(即同时启用 inter-core 与 intra-core)会导致未定义行为。文档明确标注 `❌ Not supported`。

6. **扁平模式(Flat,推荐)**:用 `T.Pipelined` 处理 inter-core 同步,用手动 `T.set_flag`/`T.wait_flag` + `T.serial(2)` 实现 intra-core 双缓冲。原文给出完整代码模板,包含初始化(`T.set_flag("MTE1","MTE2",SIG_K_L1)`)和销毁(`T.wait_flag` 消耗最后 token)两部分,强调双方向 set/wait 构成 `k_l1` 物理 buffer 的**所有权环**。

---

## 【关键机制与数据】

### 工作原理(分两层)

- **Intra-core 层**:利用 `num_stages` 级双缓冲,在同一核内把 `T.copy A/B → L1` 与 `T.gemm_v0` 串成"读-算-写"流水线。`T.barrier_all()` 强制把访存与计算物理隔开,使 GEMM 输入稳定后再启动。
- **Inter-core 层**:Cube 核作为生产者通过 `T.copy(acc_s_l0c, workspace_1[cid,...])` 把结果写到共享 workspace,Vector 核作为消费者从 `workspace_1` 读出并 `T.tile.add` 累加。`T.Pipelined` 自动插入跨核同步原语。

### 时间线数据(原文给出)

**Intra-core(`loop_k=4, num_stages=2`)** —— 6 个时间槽:

| Time | Copy A | Copy B | Compute |
|------|--------|--------|---------|
| t₀ | copy_A_0 | copy_B_0 | — |
| t₁ | copy_A_1 | copy_B_1 | — |
| t₂ | copy_A_2 | copy_B_2 | gemm_0 |
| t₃ | copy_A_3 | copy_B_3 | gemm_1 |
| t₄ | — | — | gemm_2 |
| t₅ | — | — | gemm_3 |

(注:文档原文此处 `t₀` 表中只有 `copy_A_0`,但紧接着正文同时提到 `copy_A_0 copy_A_1` 与 `copy_B_0 copy_B_1`,因此 t₀/t₁ 应分别承载两对拷贝,我按文档"主循环从第 k=2 才开始计算"的逻辑如实呈现。)

**Inter-core(`T.ceildiv(seq_len, block_N)=4, num_stages=2`)** —— 5 个时间槽:

| Time | Write Workspace | Read Workspace |
|------|-----------------|-----------------|
| t₀ | write_0 | — |
| t₁ | write_1 | read_0 |
| t₂ | write_2 | read_1 |
| t₃ | write_3 | read_2 |
| t₄ | — | read_3 |

### 阶段切分(原文摘录)

- 预取(Prefetch):`copy_A_0 copy_A_1`、`copy_B_0 copy_B_1`
- 主循环(Main body):`copy_A_2 copy_B_2 gemm_0`、`copy_A_3 copy_B_3 gemm_1`
- 收尾(Epilogue):`gemm_2`、`gemm_3`

### 生成代码(原文:`cross_interval=2, num_stages=4`)

```c
if (((i % 2) == 1) || (i == 3)) {
    AscendC::CrossCoreSetFlag<2, PIPE_FIX>(0);
}
if ((i % 2) == 0) {
    AscendC::CrossCoreWaitFlag(2);
}
```

**性能/数据含义**(原文有的才写):文档未给出实测 perf 数字;原文通过时间槽表说明:intra-core 通过 `num_stages=2` 双缓冲把 4 次访存与 4 次计算在 6 步内完成,inter-core 通过 workspace 实现 read/write 重叠以隐藏访存延迟。

---

## 【表格解读】

### 表 1:`T.Pipelined` 接口参数表(原文逐字还原)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `loop_iterations` | int | Required | Total number of loop iterations |
| `num_stages` | int | Required | Number of pipeline stages for double buffering |
| `cross_interval` | int | 1 | Interval for cross-core synchronization (only effective in inter-core pipeline) |

**逐行解读**:
- `loop_iterations`(int,必填):决定流水线覆盖的循环总步数,直接对应 Intra-core 示例中的 `loop_k=4` 和 Inter-core 示例中的 `T.ceildiv(seq_len, block_N)=4`。
- `num_stages`(int,必填):双缓冲级数。`num_stages=2` 是 Intra-core 示例默认;`num_stages=4` 在 Inter-core `cross_interval` 示例中出现,表明同一参数在两种模式下表达"分几级错位"。
- `cross_interval`(int,默认 1):跨核同步步距,只在 Inter-core 生效。默认 `1` 表示每轮迭代都同步(`CrossCoreSetFlag` 每轮触发),值越大同步开销越低,但要求 buffer 足够大以容纳更多 in-flight 块。

### 表 2:Intra-core 时间线(原文逐字还原)

| Time | Copy A | Copy B | Compute |
|------|--------|--------|---------|
| t₀ | **copy_A_0** | **copy_B_0** | |
| t₁ | **copy_A_1** | **copy_B_1** | |
| t₂ | **copy_A_2** | **copy_B_2** | **gemm_0** |
| t₃ | **copy_A_3** | **copy_B_3** | **gemm_1** |
| t₄ | | | **gemm_2** |
| t₅ | | | **gemm_3** |

**逐行解读**:
- t₀–t₁:预取 2 级数据(`copy_A_0/B_0`、`copy_A_1/B_1`),此时 GEMM 无输入未启动。
- t₂–t₃:预取下一轮 + 启动第一级计算,访存与计算同槽重叠(`num_stages=2` 双缓冲生效)。
- t₄–t₅:所有访存已完成,只剩余最后两级 `gemm_2`、`gemm_3` 的收尾。
- 整体把 `4(访存)+4(计算)` 的串行 8 步压缩到 6 步,体现双缓冲的延迟隐藏收益。

### 表 3:Inter-core 时间线(原文逐字还原)

| Time | Write Workspace | Read Workspace |
|------|-----------------|-----------------|
| t₀ | **write_0** | |
| t₁ | **write_1** | **read_0** |
| t₂ | **write_2** | **read_1** |
| t₃ | **write_3** | **read_2** |
| t₄ | | **read_3** |

**逐行解读**:
- t₀:Cube 完成第一块 `write_0`,Vector 尚未读到任何数据。
- t₁–t₃:Cube 写第 N 块时,Vector 同步读第 N-1 块,实现生产者-消费者流水线。
- t₄:Cube 写完所有 4 块,Vector 收尾 `read_3`。
- 关键是 `num_stages=2` 让 reader 比 writer 落后 1 槽,保证 workspace 槽位不会"未写先读"。

### 表 4:`cross_interval` 使用场景(原文逐字还原)

| cross_interval | Sync Frequency | Use Case |
|----------------|----------------|----------|
| 1 | Every iteration | Default, highest parallelism |
| N | Every N iterations | Reduced sync overhead, multi-KV cache |

**逐行解读**:
- `cross_interval=1`:每轮都同步,默认配置,实现最高并行的跨核流水线。
- `cross_interval=N`:每 N 轮才同步一次,降低 `CrossCoreSetFlag/WaitFlag` 的调度开销,适用于 multi-KV cache 等需要更大 in-flight 窗口的场景。

---

## 【公式解读】

原文给出的核心公式/接口签名(逐字保留):

```python
for var in T.Pipelined(loop_iterations: int, num_stages: int, cross_interval: int = 1):
```

**符号含义**:
- `var`:迭代变量,在循环体中即当前迭代索引 `k`(原文 Intra-core 示例)或 `k`(原文 Inter-core 示例)。
- `loop_iterations`:整型,必填参数,表示流水迭代总次数。Intra-core 示例中传入 `loop_k=4`,Inter-core 示例中传入 `T.ceildiv(seq_len, block_N)=4`。
- `num_stages`:整型,必填参数,表示双缓冲流水级数。Intra-core 示例取 `2`,Inter-core `cross_interval` 示例取 `4`。
- `cross_interval`:整型,可选参数,默认 `1`,只在 inter-core 模式下生效,决定 `CrossCoreSetFlag`/`CrossCoreWaitFlag` 触发的步距。

**作用**:该接口将原本需要手写 `set_flag`/`wait_flag` 与双 buffer 索引切换的样板代码封装为高层 for 循环,由编译器/运行时插入同步原语并展开双缓冲逻辑;`num_stages` 直接控制生成的错位级数,`cross_interval` 控制跨核同步原语的触发密度。

> 注:原文无 LaTeX 数学公式,以上为唯一的"伪代码/接口式公式"。

---

## 【关联】

文档在特性、模块、上下游关系上与以下概念紧密耦合(均来自原文):

- **AscendC 底层原语**:`AscendC::CrossCoreSetFlag<2, PIPE_FIX>` 与 `AscendC::CrossCoreWaitFlag` —— `T.Pipelined` 在 inter-core 模式下会被翻译为这些原语,文档直接给出生成代码示例。
- **TileLang 算子原语**:`T.copy`(GM→L1、GM→workspace、workspace→UB)、`T.gemm_v0`(支持 `transpose_B=True` 与 `init=True/False` 控制累加语义)、`T.barrier_all`(intra-core 阶段切分)、`T.tile.add`(Vector 核累加)、`T.serial`(顺序迭代,用于 flat 模式中的 `side ∈ {0,1}` 双 buffer)。
- **Flag 管理体系**:Flat 模式涉及 `SIG_K_L1`、`SIG_L0AB + side`、`SIG_L0C + side` 等信号 ID,以及 `MTE1/MTE2`、`M`、`FIX` 等硬件流水线标签,说明 `T.Pipelined` 与底层 `T.set_flag`/`T.wait_flag` 的同步空间共享同一套资源池。
- **Pass 配置开关**:`tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_COMBINE` 与 `TL_ASCEND_AUTO_CV_SYNC`,文档明确写出二者必须为 `True` 才能启用 inter-core pipeline(否则 `cross_interval` 不生效)。
- **对比特性**:`T.Pipelined` 与"手写双 buffer + 手写同步"形成对照——文档通过 flat 模式同时使用两者,演示了**高层抽象与底层控制**在同一程序内的混合使用边界。

> 注:原文未提供内部 markdown 链接(文末"内部链接: (无)")。

---

## 【使用方法】

### 启用 Inter-core pipeline 所需的 Pass 配置(原文逐字保留):

```python
pass_configs = {
    tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_COMBINE: True,
    tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_SYNC: True,
}
```

### 使用步骤(基于原文):

1. **选择模式**:若只需单核内访存/计算重叠,使用 Intra-core(`cross_interval` 参数被忽略);若需要 Cube 与 Vector 核流水,使用 Inter-core 并按上文设置 Pass。
2. **调用接口**:按 `for var in T.Pipelined(loop_iterations, num_stages, cross_interval=1):` 包裹循环体。
3. **循环体编排**:Intra-core 在 `T.copy` 与 `T.gemm_v0` 间插入 `T.barrier_all()`,首轮用 `init=True`;Inter-core 中 Cube 写入 workspace、Vector 从 workspace 读取并累加。
4. **嵌套约束**:不可在 `T.Pipelined` 内再嵌套 `T.Pipelined`;若需 intra-core 双缓冲,改用 flat 模式,以 `T.serial(2)` + `T.set_flag`/`T.wait_flag` 手动实现,并在循环前后加上初始化与销毁的 flag 操作(`T.set_flag("MTE1","MTE2",SIG_K_L1)` 与最终 `T.wait_flag` 消耗返回 token)。
5. **调优 `cross_interval`**:默认 `1` 最大化并行;当同步开销成为瓶颈(如 multi-KV cache 场景)时增大该值,并通过生成代码(`CrossCoreSetFlag`/`CrossCoreWaitFlag` 的 `i % N` 条件)验证触发密度符合预期。

> 注:原文未涉及命令行或环境变量层面的启用方式,以上均来自文档原文。
