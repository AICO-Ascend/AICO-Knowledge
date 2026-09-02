# async_schedule

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/async_schedule.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/async_schedule.md

# xLLM Async Schedule 文档深度解读

## 【定位】
本文档描述 xLLM 在框架层面提供的**异步调度（Async Schedule）**能力，通过让 CPU 端的调度与后处理操作与设备端计算重叠执行，消除 LLM 解码阶段中因串行依赖造成的设备空闲"气泡"，从而提升推理吞吐。

---

## 【技术要点】

1. **三阶段推理流水线**：CPU 端调度（准备模型输入）→ 设备端计算（GPU/TPU 执行）→ CPU 端后处理（输出处理），三个阶段在解码过程中被串行强制。
2. **解码依赖性**：step-i+1 的输入依赖 step-i 的输出，造成步骤间严格的串行执行，CPU 阶段（1 和 3）期间设备处于闲置气泡状态。
3. **Fake Token 预调度机制**：CPU 在发起 step-i 计算后不等待设备完成，而是为 step-i 请求构造 fake token，先用 fake token 执行 step-i+1 的调度（如 KV Cache 分配），待 step-i+1 真正启动计算时再替换为真 token，以保证正确性。
4. **多线程池 + 非阻塞 RPC**：CPU 端阶段 1 和阶段 3 由不同 thread pool 处理；RPC 函数调用采用非阻塞 C++ future / promise 机制，实现全异步运行时。
5. **启用开关**：gflags 参数 `enable_schedule_overlap`，默认 `false`，通过服务启动脚本设置为 `true` 启用。
6. **使用限制与代价**：该特性要求服务器额外多计算一步；针对输出 token 极少（如 few-token 生成）或单输出场景（如 embedding 模型）已在内部硬禁用；VLM 模型当前适配中、暂时禁用。

---

## 【关键机制与数据】

**工作机制（原文）**：
- 异步调度的核心做法是：CPU 在发起 step-i 计算后**不阻塞等待设备**，转而构造 fake token → 执行 step-i+1 的调度操作（如 KV Cache 分配）→ 当 step-i+1 计算启动前，用 step-i 产出的**真实 token 替换** fake token 以确保语义正确。
- 与此同时，CPU 在**单独的线程**中处理 step-i 的结果并返回给客户端。
- 整体架构中，CPU 侧的阶段 1 与阶段 3 由不同 thread pool 处理，RPC 使用非阻塞 C++ future / promise。

**性能数据（原文）**：
- 启用异步调度后，两个 step 之间的设备空闲时间约为 **200us**，与单次 kernel launch 时长相当。
- 在 **DeepSeek-R1-Distill-Qwen-1.5B** 模型上、TPOT 约束为 **50ms** 时，吞吐提升 **17%**。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **与模型类型的关联**：文档明确指出该特性对 **embedding 模型**（单输出场景）和 **few-token 生成**（输出 token 极少）不适用，并在内部硬禁用；**VLM 模型**当前适配中、暂时禁用。
- **与流水线阶段的关联**：异步调度将原本串行的 CPU 阶段 1、阶段 3 与设备阶段 2 重叠执行，并通过独立的 thread pool 与非阻塞 future/promise 实现全异步运行时。
- **架构图引用**：文档引用了 `figures/async_schedule_architecture.jpg` 作为整体架构示意（原文未提供该图内容）。
- **内部链接**：文末未提供任何内部链接（侧边栏顺序 order: 10，暗示属于 features 集合中的一篇，但未直接链接其他 feature）。

---

## 【使用方法】

原文给出的启用方式如下：

- **gflags 参数**：`enable_schedule_overlap`，**默认 `false`**。
- **启用命令**：在 xLLM 服务启动脚本中加入：

  ```shell
  --enable_schedule_overlap=true
  ```

- **注意事项（原文）**：
  - 不推荐用于输出 token 数量有限的场景（如 few-token 生成）或单输出场景（如 embedding 模型），否则可能导致服务端吞吐下降，已在内部硬禁用。
  - **VLM 模型**当前适配中，暂时禁用。
  - 该特性需服务器额外多算一步（one additional step），存在固有代价。

## 图文联合解读

- `async_schedule_architecture.jpg`: **图文联合解读**

**1) 图示内容**：上"before"时序为CPU单线程串行执行 Request/Schedule→NPU Forward→Output，三段之间出现红色"NPU Bubble"；下"after"时序中CPU线程A持续预Schedule，NPU Forward紧密衔接无空隙，线程B并行处理Output，仅末尾NPU sync+CPU sync一次同步。

**2) 技术结论**：通过调度与计算重叠+输出线程并行，NPU气泡被消除。

**3) 文档对应**：直接可视化文档论点——用fake token提前做step-i+1的KV Cache分配，CPU不等NPU即调度，线程B异步回传结果，消除bubbles。
