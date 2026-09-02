# 常见线程模型

> 仓 `brpc` · 路径 `docs/cn/threading_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/brpc/docs/cn/threading_overview.md

# brpc `docs/cn/threading_overview.md` 深度解读

---

## 【定位】

本文档系统梳理了服务器端网络编程中常见的五种线程模型（连接独占、单线程 reactor、N:1 线程库、多线程 reactor、M:N 线程库），并指出多核扩展性与异步编程两大核心痛点，为读者理解 brpc 后续线程/调度相关设计（如 bthread、但本文不涉及具体 bthread）奠定背景。

---

## 【技术要点】

1. **连接独占线程/进程模型**：线程/进程处理绑定连接的消息直至连接断开；当连接数增多时，资源占用与上下文切换成本激增，是 [C10K 问题](http://en.wikipedia.org/wiki/C10k_problem) 的来源。早期 web server 常见，现已少用。
2. **单线程 reactor**：以 libevent、libev 为代表。"loop" 含义为：event dispatcher 等待事件 → **原地**调用 event handler → 全部跑完后再等下一批。**单 loop 只能用一个核**，适合 IO-bound 或 handler 运行时间确定的场景（如 http server）；多开发者协作易因阻塞回调拖慢全局；handler 不并发运行 → race condition 少 → 一些代码可不加锁；扩展靠多进程。
3. **N:1 线程库（Fiber）**：以 GNU Pth、StateThreads 为代表，把 N 个用户线程映射到 1 个系统线程。能力上**等价于单线程 reactor**，差别在于把"事件回调"换成了"上下文切换（栈、寄存器、signals）"。单线程对 CPU cache 友好，且若舍弃 signal mask 支持，用户线程上下文切换可至 **100~200 ns**。扩展性同样主要靠多进程。
4. **多线程 reactor**：以 `boost::asio` 为典型，由一个或多个线程跑 event dispatcher，事件发生后把 handler **交给 worker 线程执行**。是多线程 reactor 的天然多核扩展。可缓解单线程 reactor 的回调阻塞问题，**大部分 RPC 框架采用了此模型**，回调中常含同步阻塞（如同步等待下游 RPC 返回）。
5. **M:N 线程库**：M 个用户线程映射到 N 个系统线程，调度灵活度高于多线程 reactor，但实现困难。文中给出的方向包括用户态（GHC threads、goroutine，可围绕库设计新关键字并拦截相关 API）与内核改造（Windows UMS、Google SwitchTo，后者本身是 1:1，但可借其实现 M:N 效果）。使用上更接近系统线程，需锁或消息传递保证线程安全。
6. **两大问题**：
   - **多核扩展性**：回调中常发起同步操作使 worker 被阻塞 → 用户需开**几百个线程**维持吞吐 → 调度开销高、TLS 代码效率低。任务分发采用全局 mutex + condition 保护的队列 → 全局竞争激烈。建议方向：每系统线程独立 runqueue + scheduler 分发用户线程到不同 runqueue（更容易支持 NUMA）；event dispatcher 最好把任务递给**自身核心**的 worker；response 唤醒也尽量在当前核进行以避免 cacheline 同步等待。
   - **异步编程**：任一挂起点都需显式保存状态并在回调中恢复；异步代码被迫写成状态机；当挂起发生在条件判断、循环、子函数中时几乎无法维护；多触发源（fd 可读 vs 超时）的唤醒易引入 race condition。Lambda 语法糖只能降低"麻烦"，无法降低难度。共享指针泛滥导致内存 ownership 不清（泄漏 / 段错误难定位）。**缺乏上下文使 RAII 无法充分发挥**，常见 "callback 外 lock / callback 内 unlock" 的反模式。

---

## 【关键机制与数据】

| 论点 | 原文关键事实 | 关联 |
|---|---|---|
| 单线程 reactor 局限性 | "一个 event-loop 只能使用一个核" → 仅适合 IO-bound 或 handler 运行时间确定的程序 | 解释了为什么纯异步框架不适合 CPU-bound 业务 |
| N:1 上下文切换速度 | "舍弃对 signal mask 的支持的话，用户线程间的上下文切换可以很快（100~200ns）" | 给出可量化的优化收益来源 |
| 多线程 reactor 性能非线性 | "在特定的场景中，粗糙的多线程reactor实现跑在24核上甚至没有精致的单线程reactor实现跑在1个核上快" | 印证 cache 一致性瓶颈，由 `atomic_instructions.md#cacheline` 进一步解释 |
| RPC 框架通行做法 | "事实上，大部分RPC框架都使用了这个[多线程 reactor]模型，且回调中常有阻塞部分，比如同步等待访问下游的RPC返回" | 说明 brpc 并非个例，阻塞回调是行业级现实 |
| 阻塞回调造成的线程膨胀 | "线程把大量时间花在了等待下游请求上，用户得开几百个线程以维持足够的吞吐" | 是 bthread / work_stealing_queue 的现实动机之一（原文未明示，但上下文指向） |
| 全局队列竞争 | "任务的分发大都是使用全局mutex + condition保护的队列，当所有线程都在争抢时，效率显然好不到哪去" | 给出 runqueue-per-thread 改进方向的依据 |
| NUMA 友好度 | "每个系统线程有独立的runqueue …… 这种结构也更容易支持NUMA" | 暗示 brpc 在 NUMA 机器上的调度考量 |
| 缓存局部性优化 | "如果worker的逻辑能直接运行于event dispatcher所在的核心上就好了" + "收到response后最好在当前核心唤醒正在同步等待RPC的线程" | 是 worker locality 与 avoid-thread-migration 的设计动机 |
| RAII 失效模式 | "没有上下文会使得RAII无法充分发挥作用, 有时需要在callback之外lock，callback之内unlock，实践中很容易出错" | 异步代码中的典型资源管理反模式 |
| 共享指针副作用 | "大量使用引用计数的用户代码很难控制代码质量" | 异步编程中 ownership 难题 |

---

## 【表格解读】

原文无表格（全文为叙述性文字 + 两张运行示意图 `figures/threading_overview_1.png`、`figures/threading_overview_2.png`，无参数表/性能对比表）。

---

## 【公式解读】

原文无公式（无 LaTeX 表达式、无伪代码形式的调度/性能公式；唯一出现的数字 "100~200ns" 与 "24核 / 1个核" 是叙述性论据，未以公式形式给出）。

---

## 【关联】

- **../en/threading_overview.md**：本文的英文版本，提供同一概述的英文表述。
- **atomic_instructions.md#cacheline**：在讨论"多线程 reactor 受 cache 一致性限制"时引用，承接原文"粗糙的多线程 reactor 跑在 24 核上甚至没有精致单线程 reactor 跑在 1 个核上快"的论断。该链接指向 brpc 文档中关于 cacheline 与原子指令的章节，用于解释为什么跨核 worker 调度存在 cacheline 同步开销，是理解"worker 留在 dispatcher 所在核心"这一建议的底层原理。
- **文档自身的逻辑串联**：本文先铺五种线程模型的形态与典型实现（libevent/libev → GNU Pth/StateThreads → boost::asio → GHC/goroutine/UMS），再以"多核扩展性"和"异步编程"两个问题章节收束，**实质是为后文 brpc 自研线程方案的动机说明做铺垫**（虽然本文未直接出现 bthread/work_stealing_queue 等字样，但 "runqueue-per-thread"、"NUMA 友好"、"避免 cacheline 同步" 等论点正是其设计方向）。
- **外部知识关联**：C10K、Reactor pattern、Fiber、Windows UMS、Google SwitchTo、GHC threads、goroutine、RAII 均为背景知识链接，帮助读者核实术语。

---

## 【使用方法】

原文未涉及任何具体启用方式、配置项或命令（本文为概念性 overview，不包含 API 调用、参数表或构建/启动指令）。如需相关配置方法，应参考 brpc 中其他关于 bthread、ExecutionQueue、任务的章节（本文未列出对应链接）。

## 图文联合解读

- `threading_overview_1.png`: **图示解读：**

1）**画面内容**：单一线程的纵向执行时间轴，依次为 epoll_wait→callback1→epoll_ctl→callback2(高大红色块)→epoll_ctl→callback3→epoll_ctl，蓝色箭头回到顶部形成循环。标注 callback1 区段为"Delay for callback2"，callback2 区段为"Delay for callback3"，红字批注"不可控！除非是专有服务"。

2）**技术结论**：单个耗时漫长的 callback2 独占线程，导致后续 callback3 的派发及所有 epoll_ctl 注册被无限延迟，体现单线程 reactor 一旦回调阻塞则整个事件循环失序且无法干预。

3）**与文档关系**：直接可视化文档论点——"一个耗时漫长的回调就会卡住整个程序，产生高延时"，说明该模型仅适合 IO-bound 或短回调场景，佐证后续引出多线程 reactor 的必要性。
- `threading_overview_2.png`: **图示解读：**

图绘多线程reactor架构：单Polling Thread（epoll_wait+多queueing）经Dispatcher分派事件至Thread1/2/3，各线程含callback与epoll_ctl。

**技术结论：** 揭示三大缺陷——Dispatcher多生产者争用（Highly contended）、epoll_ctl为O(log N)红黑树操作（Not fast）、跨核cache bouncing。

**文档呼应：** 以图佐证单线程reactor扩展局限及多线程reactor的共享开销，为后续brpc自有bthread模型做铺垫。
