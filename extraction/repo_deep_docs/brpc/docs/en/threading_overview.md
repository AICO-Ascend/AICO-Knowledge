# Common threading models

> 仓 `brpc` · 路径 `docs/en/threading_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/brpc/docs/en/threading_overview.md

【定位】
本文档系统梳理了构建高并发在线服务时常见的几种线程模型(独占线程/进程模型、单线程 reactor、N:1 协程库、多线程 reactor、M:N 线程库),分析各自的适用场景、性能瓶颈与多核扩展性问题,为 brpc 后续讨论其自有执行模型做铺垫。

【技术要点】
- 独占线程/进程模型:每个连接独占一个线程或进程,受 C10K 问题困扰,资源占用与上下文切换成本随连接数膨胀,如今已很少见。
- 单线程 reactor:由事件分发器"原地(in-place)"串行调用回调,只有一个系统线程参与核心计算,等价于 IO-bound 或每个回调短小且时长确定的场景;事件回调不并发执行,回调间竞态简单,部分场景可不用锁。
- N:1 协程库(Fiber):N 个用户线程映射到 1 个系统线程,合作式切换(只在阻塞原语处切换),能力等价于单线程 reactor,但回调换成上下文(栈、寄存器、信号);移除信号掩码支持后上下文切换可达 100~200ns。
- 多线程 reactor:一个或多个线程运行事件分发器,事件回调入队交给工作线程执行,天然支持多核;事件回调不要求全非阻塞(除非所有工作线程都被阻塞),适合多数 RPC 框架同步等待下游的真实负载。
- M:N 线程库:M 个用户线程映射到 N 个系统线程,可调度代码的运行位置与时长;brpc 讨论的特化版本不做完整抢占与优先级;新语言可在用户态实现(GHC thread、goroutine),老语言常需修改 OS 内核(Windows UMS、google SwitchTo,后者为 1:1)。
- 多核扩展性问题:全异步理想但实践中难;任务被推入被全局 mutex+condition 保护的队列,争用激烈;改进方向是"每系统线程一个 runqueue + 调度器分发",更利于 NUMA 与扩展性;事件分发器与 worker 跨核跳转会触发 cacheline 同步,理想是让 worker 直接跑在分发器所在核上。

【关键机制与数据】
- C10K 问题:由连接数增加导致线程/进程资源与上下文切换开销不可承受,在早期 web server 普遍,如今少见。(原文: "When number of connections increases, resources occupied by threads/processes and costs of context switches becomes more and more overwhelming" / "C10K problem")
- 单线程 reactor:事件分发器"原地"调用回调 → 处理完毕 → 再次等待,形成 loop;多个 handler 的代码被交错到同一系统线程执行。(原文: "calling the corresponding event handler in-place when an event occurs" / "multiplexes(interleaves) code written in different handlers into a system thread")
- 单线程 reactor 扩展方式:增加进程数 (multi-process)。(原文: "These programs are often scaled by deploying more processes")
- N:1 协程库性能数据:上下文切换 100~200ns(前提是不支持信号掩码)。(原文: "context switches between user threads can be done very fast(100 ~ 200ns)")
- 多线程 reactor 对比数据:在 24 核机器上实现不当的多线程 reactor 甚至比精心调优的单线程 reactor 还慢。(原文: "a badly implemented multi-threaded reactor running on 24 cores is even slower than a well-tuned single-threaded reactor")
- 多线程 reactor 与多进程单线程 reactor 对比:前者因共享内存地址,worker 间负载均衡更频繁且更廉价;后者基本依赖前端服务器分发流量。(原文: "sharing memory addresses makes interactions between threads much cheaper ... multiple single-threaded reactors basically depend on the front-end servers to distribute traffic")
- 多线程 reactor 与单线程 reactor 的关系:可由单线程 reactor 直觉扩展而来;支持多核。(原文: "This model is extensible from single-threaded reactor intuitively and able to make use of multiple CPU cores")
- M:N 与多线程 reactor 对比:在调度"何时何地运行、运行到何时"上更灵活。(原文: "able to decide when and where to run a piece of code and when to end the execution, which is more flexible at scheduling")
- M:N 与 N:1 对比:使用方式更接近系统线程,需锁或消息传递保障线程安全。(原文: "usages of M:N threading libraries are more similar to system threads, which need locks or message passings to ensure thread safety")
- cacheline 同步:worker 跨核跳转会等待 cacheline 同步,代价不低。(原文: "wait for synchronizations of relevant cachelines, which is not very fast")
- 多核扩展建议:每系统线程一个 runqueue + 一到多个调度器分发,优于全局 mutex+condition 队列;利于 NUMA。(原文: "each system thread has its own runqueue, and one or more schedulers dispatch user threads to different runqueues ... easier to support NUMA")
- CPU 亲和性建议:worker 最好直接运行在事件分发器所在核上;被 RPC 阻塞的用户线程最好在收到响应的同一核上唤醒。(原文: "better to wake up the user thread blocking on RPC on the same CPU core where the response is received")
- 异步编程痛点:任何挂起(休眠、等待)都需显式保存/恢复状态;一旦挂起发生在条件、循环或子函数中,几乎写不出可维护的状态机;多事件唤醒(fd 可读或超时)易引入竞态;lambda 等语法糖只减少编码麻烦,不降低难度。(原文: "Syntactic sugars(such as lambda) just make coding less troublesome rather than reducing difficulty")

【表格解读】
原文无表格。

【公式解读】
原文无公式。

【关联】
- 与中文版同主题文档的关联:文档顶部链向 `../cn/threading_overview.md`,提供中文版本,内容结构对应。
- 与原子指令/cacheline 的关联:正文在讨论多线程 reactor 多核扩展性时显式链向 `atomic_instructions.md#cacheline` 中的 cacheline 章节,用于解释为什么多线程 reactor 难以随 CPU 核数线性扩展,以及 worker 跨核切换的代价来源(cacheline 同步)。
- 上游/旁系引用:文档以链接方式提及若干外部模型参考,用于定位每种线程模型的典型实现 — 单线程 reactor 引用 libevent、libev;N:1 协程库引用 GNU Pth、StateThreads;多线程 reactor 引用 boost::asio;M:N 线程库引用 GHC thread、goroutine、Windows UMS、google SwitchTo。这些用于在 brpc 自身的执行模型讨论之前,建立通用术语与对比基准。

【使用方法】
原文未涉及 (本文为 overview/概念性文档,没有列出可启用的配置项、命令行参数或启用步骤)。

## 图文联合解读

- `threading_overview_1.png`: **图文联合解读：**

**1) 图示内容：** 单线程 reactor 事件循环时序栈，自上而下依次为 epoll_wait → callback1 → epoll_ctl → callback2 → epoll_ctl → callback3 → epoll_ctl，底部箭头返回 epoll_wait 形成循环；红色括号标注 callback2/3 的"延迟（Delay）"区间。

**2) 技术结论：** 所有回调串行运行在同一线程，任一回调耗时都将阻塞后续所有事件处理，延迟相互叠加且不可控，除非服务专有、可保证回调短而确定。

**3) 与文档关系：** 图示直观印证文档论点——单线程 reactor 仅适合 IO-bound 或回调时长短且确定的场景（如 http 服务器），否则一个慢回调会阻塞整个程序、引发高延迟。
- `threading_overview_2.png`: **图示解读：**

1. **结构**：左侧Polling Thread通过epoll_wait循环检测，将事件放入queueing队列，由顶部Dispatcher分发给Thread1/2/3，各线程内含callback和epoll_ctl。

2. **技术结论**：标注三处缺陷——Dispatcher"高度争用"成为瓶颈；epoll_ctl操作"O(log N)、不可由ET边缘触发移除"开销大；底部"Cache bouncing"显示Polling Thread与各线程间因共享状态引发缓存行抖动。

3. **与文档关系**：图示揭露单reactor模型的扩展性痛点（争用+缓存抖动），论证为何需引入新的线程模型，引出后续brpc的改进方案。
