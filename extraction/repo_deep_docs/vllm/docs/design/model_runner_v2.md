# Model Runner V2 Design Document

> 仓 `vllm` · 路径 `docs/design/model_runner_v2.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/model_runner_v2.md

# Model Runner V2 (MRV2) Design Document 深度解读

## 【定位】

本文档描述 vLLM 中 **Model Runner V2 (MRV2)** 的设计——针对 V1 暴露出的设计缺陷与技术债，从零重写的模型执行器组件，目标是在 V1 之上做到 **更干净、更高效、更模块化**（原文："cleaner, more efficient, and more modular"）。

---

## 【技术要点】

1. **持久化批处理（Persistent Batch）解耦**：将"持久状态张量"与"每步输入张量"分离。预先分配固定大小张量（`max_num_reqs` 行，**默认 1024**），每个请求获得永久行号，抢占视作完成、恢复时重新加入。

2. **Async-First 设计**：核心模型执行循环假定为**无 CPU 同步点的 CUDA stream**，所有 CPU 入口点仅负责向 stream 提交工作，配合异步调度使 CPU 准备 N+1 步与 GPU 执行 N 步重叠。

3. **消除异步屏障（Async Barrier）**：通过"持久 CPU 状态 ≠ 被拷贝的张量"的物理分离消除竞争——CPU 写入非 pinned 状态，拷前才 `pin_memory()` 生成临时 pinned 副本，GPU 只读取副本，避免 race。

4. **StagedWriteTensor 增量写入**：5 步流程——base tensor 驻留 GPU、CPU 端累计 diff、pack 成连续 buffer、一次性拷到 GPU、单个 kernel apply。对 block table 等大张量尤其有效，原文示例为 `size=(1024, 1000), dtype=torch.int32, device="cuda"`。

5. **GPU 原生输入元数据准备**：用 Triton kernel 准备 `input_ids`、`positions`、`query_start_loc`、`seq_lens`，并用 UVA 让 GPU kernel 直接读 CPU 端的 `prefill_token_ids` 等大张量，无需复制到 GPU。

6. **Triton 原生采样器**：含 4 个子点——Gumbel-max 采样 kernel（无须显式 softmax 物化）；高效 top-k logprobs（**先从 logits 选 top-k，再仅对选中 token 计算 logprobs**，降低峰值显存）；更细粒度的 prompt logprobs 分块（含单个 prompt 内分块）；用 `idx_mapping` 间接寻址避免 per-logit 形状膨胀，兼容投机解码。

7. **模块化重构**：相比 V1 单一巨大 `gpu_model_runner.py`，MRV2 拆分为 `mrope_utils.py`、`penalties.py` 等专用文件，并把所有模型输入聚合到 `InputBatch` 类。

8. **`dummy_run` 职责瘦身**：`dummy_run` 不再承担初始 memory profiling / `torch.compile` / warmup / 空 DP forward 等多种职责，而是委托给 `execute_model`；CUDA graph capture 走**独立专用路径**。

---

## 【关键机制与数据】

### 工作原理（按文档章节顺序）

- **V1 持久批处理问题**（原文 §1）：V1 直接把持久状态张量作为 model/sampler 输入，对布局和顺序有强约束；请求加入/离开时常需要"张量整体重排"而非简单插拔行；同时必须维护冗余备份 `CachedRequestState`（原文："V1 also had to maintain `CachedRequestState`, a redundant backup copy of request state"）。

- **MRV2 持久状态机制**（原文 §1）：
  1. 预分配 `max_num_reqs` 行张量，**默认 1024（"on most platforms"）**；
  2. 每个请求在其活跃生命周期内拥有固定行号；
  3. 抢占 = 完成，恢复时按新请求重新加入状态。
  大状态张量主要驻 GPU，gather 与 GPU 计算并行，开销极低。

- **Async race 消除机制**（原文 §3）：
  - **不安全写法**：`self.states` 用 `pin_memory=True` 并直接用同一 buffer 做 H2D 拷贝，CPU 后续写入与 GPU 读取重叠 → race。
  - **MRV2 写法**：`self.states` **不 pinned**，写入后才调用 `.pin_memory()` 产生临时 `tmp_states`，H2D 拷贝 `tmp_states`，物理分离了"被读取对象"与"被修改对象"。

- **StagedWriteTensor 数据流**（原文 §4，5 步）：
  1. base tensor 在 GPU；
  2. CPU 端 diff staging（按 `state.stage_write(row=, start=, value=)`）；
  3. diffs 打包到连续 buffer；
  4. pack 一次性 H2D；
  5. launch one kernel apply。
  支持"参差不齐的更新（ragged updates）"，无 CPU-GPU 同步、kernel 启动极少。原文示例：`state.stage_write(row=2, start=3, value=[3, 1, 2])`、再 `state.stage_write(row=0, start=1, value=[-1, -2, -5])`。

- **采样器关键改动**（原文 §6）：
  - Gumbel kernel 内置 stateless RNG（种子作输入），**不显式物化 softmax**；
  - Top-k logprobs 顺序反转为"先选 top-k 再算 logprobs"——好处原文："reduces peak GPU memory usage"；
  - Prompt logprobs 允许**单个 prompt 内部做更细粒度分块**（"chunking inside a single prompt"），避免长 prompt 显存尖峰；
  - 投机解码用 `idx_mapping` 做间接寻址，省去 per-logit 的 per-request state 扩展。

- **`dummy_run` 重构**（原文 §8）：3 条规则——
  1. `execute_model` 可独立支撑 dummy run 而不污染状态；
  2. `dummy_run` 仅作为 profiling / warmup / 空 DP forward 的代理（delegate）入口；
  3. CUDA graph capture 走**专门独立路径**。
  原文："This reduces complexity and removes bugs caused by divergence between `execute_model` and `dummy_run` behavior."

### 性能/规模相关数据（原文）

- `max_num_reqs` 默认值：**1024 行**（原文："1024 by default on most platforms"）。
- `StagedWriteTensor` 示例 shape：`(1024, 1000)`，dtype `torch.int32`，device `"cuda"`。

> 原文未提供具体的延迟、吞吐、显存数字或与其他实现的 benchmark 对比；本文档以设计原因为主，不含性能基线。

---

## 【表格解读】

**原文无表格**。文中仅通过代码示例和图（`figures/persistent_batch_v1.png` / `persistent_batch_mrv2.png` / `async_sched.png` / `async_race_condition.png` / `async_no_race_condition.png`）来传达信息。

---

## 【公式解读】

**原文无公式**。代码示例虽含伪代码结构，但不含任何数学公式或 LaTeX 表达式。

---

## 【关联】

由文档结构与文末元数据（"内部链接: 无"）可知，本篇设计文档是**自包含**——未通过文内链接指向其他 design / spec / API 文档。但从内容本身，仍可识别出如下**模块关联**：

- **持久化批处理（§1）** 对接**注意力后端（attention backend）**：原文明确指出请求顺序"usually determined by the attention backend"，意味着 MRV2 把 input tensor 顺序决策权下放给后端，自己只负责 gather。
- **Async-First（§2）↔ Scheduler & Worker**："The scheduler and worker prepare inputs for step `N+1` while the GPU executes step `N`"，直接上下游是 **scheduler** 和 **worker**，两者需与之一起重新设计调度接口。
- **UVA（§5）↔ 推测解码（speculative decoding）**：原文点出 UVA 用于 `prefill_token_ids` 等大 CPU 张量直接被 GPU kernel 访问；§6 末尾的"speculative decoding 兼容性"也用 `idx_mapping` 解决 per-logit 形状膨胀——这表明 MRV2 把"GPU 已知而 CPU 尚不知"作为目标场景。
- **`InputBatch` 类（§7）↔ 各种特性模块**：模块化拆分后，`mrope_utils.py`、`penalties.py` 等都围绕 `InputBatch` 协作而非直接耦合 `gpu_model_runner.py`。
- **CUDA Graph（§8-§9）↔ `torch.compile` / DP+EP empty forward**：`dummy_run` 中淘汰掉的"Initial memory profiling and `torch.compile`"、"Empty DP forward passes for EP+DP"被独立路径取代，与图/编译子系统的耦合被切断。

---

## 【使用方法】

**原文未涉及**。
本文档是**设计说明**，没有给出：
- 启用 MRV2 的开关（CLI flag、环境变量、配置项）；
- 在 V1 与 MRV2 之间的选择方式；
- 任何构建/运行命令。

文档本身亦声明 MRV2 尚未特性完整："MRV2 is not yet feature-complete, not rigorously tested, and still has open design decisions"，因此**落地配置留待后续文档**。

## 图文联合解读

- `persistent_batch_v1.png`: 图示V1持久批次的块表时序：三张块表横向排列，展示Req C/A/B（带色行）随"D joins"在底部新增一行、"A finishes"移除A行的过程，剩余行槽就地复用，不重建整表。

论证：相邻步骤批次几乎相同时，固定槽位+就地增删可避免每步Python重新构建大张量（如block table、温度值）的开销。

对应文档：该图直观呈现了V1持久批次的核心理念，正是文档指出"输入准备CPU开销巨大"的来源，也是MRV2拟重新设计的痛点之一。
- `persistent_batch_mrv2.png`: **图解读：**

1. **画面内容**：左侧为"Block Table **State**"（块表状态），按 Req C / Req B / Req D 顺序排列在固定槽位中（含有空槽），每条请求对应独立行；右侧为"**Input** Block Table"（输入块表），仅包含活跃请求 Req B / Req C / Req D，按紧致连续布局。两者间有"Gather"箭头，并以 `req_order: ["B","C","D"]` 标注索引顺序。

2. **技术结论**：通过持久化状态表与 `req_order` 索引，仅做按行"收集"即可生成连续输入张量，避免每步从零构造完整张量，把 O(总槽位) 的 Python 构建开销降为 O(增量请求)。

3. **与文档关系**：呼应 §1 中关于 V1 持久批次"friction"的重构论点——用显式的 `req_order` + 预分配 State，使输入准备增量化、模块化，正是 MRV2"cleaner & more modular"原则的具体落地。
- `async_sched.png`: **1) 图示内容：** 三行时间线——Scheduler（调度）、CPU（Prepare）、Worker/GPU（Execute），按 N+1、N+2、N+3 三步依次推进。箭头显示：Schedule N+1 → Prepare N+1 → Execute N+1 串联，同时 Execute N+1 与 Schedule N+2、Prepare N+2 重叠执行。

**2) 技术结论：** Scheduler、CPU 准备、GPU 执行三阶段形成流水线，不同 step 的任务可并行，CPU 开销被 GPU 计算掩盖。

**3) 与文档关系：** 这是 §1 "Persistent Batch" 提出的核心动机——V1 每次临时构建输入张量，Python CPU 开销大且与 GPU 串行；MRV2 通过流水化设计，使持续批处理下 CPU 准备不再阻塞 GPU，验证"更清高效"的设计初衷。
- `async_race_condition.png`: **图示解读：**

1）**画面内容**：横向时间轴上，CPU 行依次有两个"Prepare step N/N+1 (modifies `self.states`)"块，GPU 行对应两个"Execute step N/N+1 (reads `self.states`)"块，箭头表示准备→执行的依赖；红框圈出"Prepare N+1"与"Execute N"在时间上重叠的区域，并标注"Race Condition!"。

2）**技术结论**：当 CPU 提前为下一步构造输入张量并就地修改共享 `self.states` 时，GPU 仍在执行上一步的读取，二者并发访问同一可变状态，引发数据竞争，GPU 可能读到被改写的中间值。

3）**与文档关系**：此图直接印证文档"Persistent Batch"小节对 V1 的批判——持久批复用张量带来严重的同步/竞态隐患，属于 MRV2 要从原理上重构的设计缺陷之一。
- `async_no_race_condition.png`: **图示解读**

1) **图形内容**：横向时间线划分为上下两泳道（CPU/GPU）。CPU 依次执行 "Prepare step N"、"Prepare step N+1"（均修改 `self.states`）；GPU 依次执行 "Execute step N"、"Execute step N+1"（均读取 `tmp_states`）。箭头表示 CPU 准备 → GPU 执行的前后依赖关系，标题为 "No Race Condition!"。

2) **技术结论**：CPU 端修改 `self.states` 与 GPU 端读取 `tmp_states` 操作的是**不同**状态容器，二者无数据争用，因此 CPU 准备下一步与 GPU 执行当前步可**流水线化重叠**。

3) **与文档论点关系**：直接支撑 MRV2 关于 Persistent Batch 的核心设计——通过分离读写状态缓冲区，消除 CPU/GPU 同步开销，使连续步之间可以异步流水，规避 V1 在每步重建 tensor 时的 CPU 瓶颈。
