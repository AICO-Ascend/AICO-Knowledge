# async_schedule

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/async_schedule.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/async_schedule.md

# 「异步调度」feature 文档深度解读

## 【定位】
本文描述 xLLM 框架层提供的「异步调度」能力：通过让 CPU 调度与 device 计算在相邻 step 之间并行执行,消除大模型自回归推理中因 CPU 串行调度导致的 device 空泡,从而提升端到端吞吐。

---

## 【技术要点】

1. **推理三阶段划分**: CPU 执行调度准备模型输入(阶段1) → device 计算(阶段2) → CPU 处理输出(阶段3);因 step-i+1 输入依赖 step-i 输出,三阶段必须串行,导致 device 在阶段1和阶段3时出现空泡。
2. **核心机制——fake token 提前调度**: CPU 发起 step-i 计算调用后不等待 device 完成,而是为该请求构造 fake token,使用 fake token 执行 step-i+1 的调度(分配 KV Cache 等);device 在启动 step-i+1 计算时,用 step-i 算出的 true token 替换 fake token,以保证计算正确性。
3. **全异步 runtime 架构**: CPU 侧阶段1和阶段3采用**不同线程池**;rpc 等函数调用使用 **C++ future/promise 非阻塞调用**。
4. **配置开关**: gflags 参数 `enable_schedule_overlap`,**默认 false**,启动脚本中设为 true 即可启用。
5. **性能数据**: 两个 step 之间的 device 空闲时间约 **200us**(基本等同于一个 kernel launch 的时间);在 **DeepSeek-R1-Distill-Qwen-1.5B** 模型、**TPOT 限制 50ms** 条件下,吞吐**提升 17%**。
6. **强制关闭场景**: 输出 token 数量较少、embedding 模型(只一次性输出)、VLM 模型(正在适配中)三种场景下会强制关闭。

---

## 【关键机制与数据】

**工作原理(原文数据流)**:
- step-i 计算发起 → CPU 不阻塞等待 → 为该请求构造 fake token → 用 fake token 跑 step-i+1 的调度(含 KV Cache 分配) → device 完成 step-i 后立即开始 step-i+1(用 true token 替换 fake token) → CPU 另起线程同步把 step-i 结果返回给 client。
- **原文**: "CPU在发起 step-i 计算调用后,不等待device计算完成,为 step-i 的请求构造fake token,使用fake token执行 step-i+1 的调度操作,分配KV Cache等;device在启动 step-i+1 的计算时,用 step-i 计算出来的true token替换fake token,保证计算的正确性。CPU在另外的线程中同步处理 step-i 的结果返回给client。"

**异步 runtime 拆分(原文)**:
- CPU 阶段1 与 阶段3 使用**不同线程池**;
- rpc 调用采用 **C++ future + promise 非阻塞**方式;
- 形成"全异步 runtime",架构图见 `figures/async_schedule_architecture.jpg`。

**性能数据(原文)**:
- 相邻 step 间的 device 空闲:**约 200us**,与一次 kernel launch 时间相当。
- 吞吐提升:**DeepSeek-R1-Distill-Qwen-1.5B 模型 + TPOT 50ms 限速条件下,吞吐 +17%**。

**代价(原文)**:
- 服务端会**额外计算一个 step**,因此对短输出 / embedding / VLM 场景得不偿失,这三种情况被强制关闭。

---

## 【表格解读】

**原文无表格。** 文档中仅含一张架构示意图(`figures/async_schedule_architecture.jpg`)与一段 shell 配置示例,未出现任何参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式。** 文档未给出任何 LaTeX 公式或伪代码表达式,核心机制完全通过文字 + fake/true token 替换流程描述。

---

## 【关联】

本文档未提供内部链接,但从内容可识别出与以下模块/特性的上下游关系:

| 关联对象 | 关系描述 |
|---|---|
| **CPU 调度阶段(阶段1)** | 异步调度需要把阶段1从串行路径中"前移"到上一 step 的 device 计算期间,因此依赖框架层调度器可重入且无强顺序假设。 |
| **Device 计算(阶段2)** | 是被"重叠"的对象,要求 kernel launch 本身足够快(原文给出 ~200us,与一次 kernel launch 同量级)。 |
| **CPU 输出处理(阶段3)** | 通过**单独线程池**与主调度线程解耦,从而让 fake token 调度能与输出处理并发。 |
| **KV Cache 管理** | 异步调度中需要为 step-i+1 **提前分配 KV Cache**(以 fake token 为占位),因此与 KV Cache 分配器紧耦合。 |
| **C++ future/promise** | rpc 等调用依赖此机制实现非阻塞,是构成"全异步 runtime"的底层工具。 |
| **TPOT(每 token 输出时间)** | 性能评估以 TPOT=50ms 为限速基线,异步调度在已有时延约束下转化为吞吐增益。 |
| **VLM 模型** | 原文标注"正在适配中",目前强制关闭,意味着该特性与 VLM 前处理管线存在尚未解决的兼容性。 |
| **Embedding 模型 / 短输出场景** | 同样强制关闭,因其一次性输出或极短输出无法让"额外计算一个 step"的代价被摊薄。 |

---

## 【使用方法】

**启用方式(原文)**:
通过 gflags 参数 `enable_schedule_overlap` 控制,默认 **false**;在 xLLM 服务启动脚本中加入如下参数即可开启:

```shell
--enable_schedule_overlap=true
```

**关闭/限制(原文未给出对应 gflags)**:
- 对输出 token 数量较少、embedding 模型、VLM 模型,框架**强制关闭**异步调度(原文未列出对应的关闭参数名,仅在 caution 中说明行为)。
- 文档未涉及其他相关配置项、命令行或 API。

## 图文联合解读

- `async_schedule_architecture.jpg`: **图示内容**：上下两条timeline对比。**before**横轴上CPU调度(NPU Forward前后)与计算串行，两段红色箭头标注"NPU Bubble"为空闲气泡；**after**中CPU thread A的Schedule与NPU Forward时间轴重叠（用NPU sync/CPU sync虚线标注同步点），CPU thread B另起线程异步处理Output，NPU Forward连续无间隙。

**技术结论**：以fake token提前调度、用双线程池分工执行，可使调度与计算流水化，消除device空泡。

**与文档关系**：直观佐证"空泡≈一个kernel launch（约200us）、吞吐提升17%"的性能结论，并体现"多线程池+futrue非阻塞"全异步runtime的设计。
