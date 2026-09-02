# **MindStudio-Ops-Profiler特性设计说明书**

> 仓 `msot` · 路径 `docs/design/26.0.0/调优工具功能设计文档/MindStudio-Ops-Profiler特性设计说明书.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/design/26.0.0/调优工具功能设计文档/MindStudio-Ops-Profiler特性设计说明书.md

# MindStudio-Ops-Profiler 特性设计说明书 — 一体化深度解读

---

## 【定位】

本文描述的是 MindStudio 调优工具链中的 **Ops Profiler 特性**,面向昇腾 A2/A3/A5/310P 系列芯片,为开发者自定义算子提供**硬件上板运行**与**仿真运行**的性能数据采集与报告能力,用于识别算子性能瓶颈、指导代码优化,其核心实现围绕"kernel 重放 + 多通道数据汇聚"展开。

---

## 【技术要点】

1. **三类上板数据采集**(原文 4.1):①芯片通过驱动通道上报的数据;②基于软件实现的 Kernel 运行时数据 dump(包含 AscendC 打点、动态插桩数据收集);③通过 Profiling/Mstx 接口收集的各外部组件上报数据。

2. **Kernel 重放机制**(原文 4.1/4.3):因芯片单次通过 PMU 采集数据有限,引入重放。原文给出三种友商方案:基于 kernel 的重放、基于 application 的重放、基于接口自定义范围的重放;因 "反复拉起 Application 方式并不能解决 warm-up",本特性**优先实现 kernel 重放**,思路为"对所有用户内存数据做 backup,调度 kernel 时进行 restore"。

3. **PMU 采集约束**(原文 4.3):PMU 一次性**最多只能采集 8 个 event**,因此需将用户配置的采集项对应的 Event ID 拆解成 AIV/AIC 两个队列,每次重放从两队顺序取 **8 个 Event ID**,最终合并二进制落盘并按队列顺序重组。

4. **运行时接口打桩表**(原文 4.3):通过预加载 `prof-injection`,对 `rtMalloc`(记录大小/地址、建副本)、`rtFree`(释放副本)、`rtKernelLaunch`、`rtKernelLaunchWithHandle`(ACLNN 动态算子)、`rtKernelLaunchWithFlag`(ACLNN 静态算子)等接口做劫持;副本内存拷贝使用 `rtMemcpyAsync`(SDMA)+ `rtSynchronizeStream`,并明确指出"rtMemcpy 走 CPU 路线,会出现 Cache 异常",故不可用。

5. **驱动 Profiling 上报接口集**(原文 4.3):通过 `dlopen` 加载驱动侧 `libascend_hal.so`,调用四个接口 —— `prof_drv_start`(开启通道,需与待调优应用同进程)、`prof_stop`、`prof_channel_read`(非阻塞,buffer 最大 `1024*1024*2`)、`prof_channel_poll`(阻塞,每次最多 polling 6 个有数据上报通道)。

6. **LD_PRELOAD 挂接 Device/Context**(原文 4.3):工具拉起调优程序时,以 `LD_PRELOAD` 方式劫持 `rtSetDevice` / `rtSetDeviceEx` / `rtCtxCreate`,在劫持函数内获取 `device_id` 并开启通道;通道逻辑设计为**可重入**,以便用户多次调用接口时能"关闭旧通道、停止旧线程、重开新通道与线程";主线程用 `thread_local` 变量 + 析构函数通知子线程退出。动态插桩特性则在重放过程中由编译器新增最后一个入参,算子执行结束后拷贝回 Host 侧。

7. **重放采集执行顺序**(原文 4.3):第 1 次采集"不做任何工作,用于解决 warm-up";第 2 ~ n 次采集按用户配置进行数据收集。原文给出实验依据"六组数据中,第一次 task_time 比第二组高出 50+ us,第二次之后数据趋于稳定"。

8. **Profiling/Mstx 数据通过劫持方式采集**(原文 4.1):为不强依赖 `libprofapi.so`,采取两条劫持路线 —— ①劫持 Profiling 开关回调接口,按 `moduleId` 配置开关;②劫持 host 数据上报接口以获取数据。

9. **内存硬约束**(原文 4.2):kernel 重放过程中,硬件上申请的内存空间**不能超过总空间的一半**,否则没有足够资源进行内存备份。

---

## 【关键机制与数据】

- **工作原理总览**(原文 3.2 + 4.1 总体方案/重放思路):特性先通过 LD_PRELOAD 注入 `prof-injection` 与劫持 Profiling 通道接口,在用户进程内同时驱动三路采集(芯片通道/软件 dump/外部组件),针对 PMU 8-event 上限采用 kernel 重放策略(同一 Application 内反复调度,避免 application 级重放无法消除 warm-up),重放期间对每次 `rtKernelLaunch` 进行"原内存→副本内存"拷贝与必要的 `rtMemcpyAsync`+`rtSynchronizeStream` 同步,保证每次采集到的数据完整且内存状态可还原;采集完成后多路数据合并成二进制落盘,工具侧按 AIV/AIC 队列顺序重组并按用户采集项还原分析。

- **Profiling 数据上报流程**(原文 4.3 流程图 + 接口说明):驱动侧 `libascend_hal.so` 暴露 `prof_drv_start` → `prof_channel_poll`(阻塞等通道到达,单次最多 6 路)→ `prof_channel_read`(非阻塞读,buffer 上限 `1024*1024*2`)→ `prof_stop` 的闭环,工具侧将该闭环挂到用户进程的 `thread_local` 主线程上下文中,通过析构函数与全局标志位协同通知子线程退出。

- **warm-up 实验观测**(原文 4.1):第一次运行 task_time 比第二次高出 `50+ us`,第二次及之后数据趋于稳定;本特性因此要求"先做一次空重放"。

---

## 【表格解读】

### 表 1:特性元数据

| 字段 | 值 |
|---|---|
| 所属 SIG 组 | msot |
| 落入版本 | MindStudio 26.0.0 |
| 设计人员 | 陈泽仁 |
| 日期 | 2026.1.23 |

**解读**:本表为标准的特性登记表,标识本特性的归属社区 SIG、下落版本、设计者及版本日期;无解读异常。

---

### 表 2:改版记录

| 日期 | 修订版本 | 修订描述 | 作者 | 审核 |
|---|---|---|---|---|
| 2026.1.23 | 初版 | 开源仓首次修订的新版本,针对 26.0.0 | 陈泽仁 | 陈泽仁 |

**解读**:表明本文是 26.0.0 版本的开源仓初版修订,作者与审核均为同一人,意味着该版本基线尚未经过多人评审。

---

### 表 3:Kernel 重放运行时接口打桩表(原文 4.3)

| runtime 接口 | 接口作用 | 插桩内容 |
|---|---|---|
| `rtMalloc` | Device 侧 GM 内存申请 | 记录申请的大小、地址,创建副本内存 |
| `rtFree` | Device 侧 GM 内存释放 | 释放副本内存 |
| `rtKernelLaunch` | `<<<>>>` 拉起算子 | 第一次跑的时候将原内存更新至副本内存;后续重放时从副本内存获取值;需要针对每一次的重放逻辑增加同步,确保每次采集到的数据是完整的 |
| `rtKernelLaunchWithHandle` | ACLNN 拉起动态算子 | 同上 |
| `rtKernelLaunchWithFlag` | ACLNN 拉起静态算子 | 同上 |

**逐行解读**:

- **`rtMalloc` 插桩**:作为内存生命周期入口,必须在此处记录 size/addr 并创建副本,否则后续重放时无法回放用户上下文。
- **`rtFree` 插桩**:与 `rtMalloc` 对称,负责释放对应副本,避免因内存泄漏导致"硬件内存 > 总空间一半"的硬约束被触发。
- **`rtKernelLaunch` 插桩**:这是重放热路径 —— 第一次执行时把当前 GM 内容同步到副本(建立 baseline),后续每次 launch 都从副本 restore,保证 N 次运行都跑在相同输入上;每次 launch 后强制同步是为了让 PMU 事件采集落定。
- **`rtKernelLaunchWithHandle` 与 `rtKernelLaunchWithFlag` 插桩**:覆盖 ACLNN 两条算子拉起路径(动态算子/静态算子),插桩策略与裸 `<<<>>>` 拉起完全一致,确保 ACLNN 生态下的算子也能纳入重放分析。

---

### 表 4:系统外部接口 — `--replay-mode`(原文 4.7)

| 接口 | 说明 | 参数样例 |
|---|---|---|
| `--replay-mode` | 指令重放模式<br>kernel: kernel 级重放<br>application: 应用级重放<br>range: 范围级重放 | `--replay-mode=kernel` |

**逐行解读**:

- **`--replay-mode=kernel`**:本特性优先实现的模式,适合大多数自定义算子的细粒度性能分析,通过在同一进程内反复调度 kernel 解决 warm-up。
- **`--replay-mode=application`**:友商支持、本特性目前未实现,因实验已证明该方式不能解决 warm-up,只能作为后续扩展。
- **`--replay-mode=range`**:友商支持、本特性目前未实现,提供接口自定义范围的重放,适合需要只对部分代码段做打点的场景。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与运行时的依赖**:本文打桩对象为 `rtMalloc / rtFree / rtKernelLaunch / rtKernelLaunchWithHandle / rtKernelLaunchWithFlag / rtSetDevice / rtSetDeviceEx / rtCtxCreate / rtMemcpyAsync / rtSynchronizeStream`,均属于昇腾 CANN ACL/Runtime 层的对外 C 接口,任何 ACLNN 算子或自定义算子的运行链路都通过该层落地。
- **与驱动的依赖**:通过 `dlopen` 调用驱动 `libascend_hal.so` 的 `prof_drv_start / prof_stop / prof_channel_read / prof_channel_poll` 四个接口,形成"芯片 → 驱动 → 工具"的硬件 Profiling 通道。
- **与编译器/算子实现的依赖**:动态插桩特性的数据回传依赖编译器在重放过程中"在 kernel 最后新增一个入参"——这是 AscendC 算子编译侧需要配套的能力。
- **与 Profiling 子系统的依赖**:原文明确为避免强依赖 `libprofapi.so`,选择"劫持接口"方案来获取外部组件(通算融合 host 侧组件)上报数据,意味着 Profiler 在设计上对 Profiling 标准库是非侵入式的。
- **特性需求关联(原文 1.2)**:A2/A3 上需支持"Scalar 细粒度性能数据分析"与"算子自定义打点性能数据展示"两条能力 —— 前者由 `rtKernelLaunch` 路径下的 PMU 重放落地,后者由 AscendC 打点 + 动态插桩的两条软件路径落地。
- **与硬件约束的关联(原文 2.3.1 / 4.2)**:范围限定昇腾 A2/A3/A5/310P 系列芯片,同时受"内存使用不超过总空间一半"约束,直接决定单进程能分析的算子规模上限。
- **文末内部链接**:原文未提供任何内部链接(标注为"无"),无上下游模块链接引用。

---

## 【使用方法】

原文明确提供的启用/配置方式如下:

- **命令行参数**:`--replay-mode`,可选值 `kernel`(已实现)/ `application`(待扩展)/ `range`(待扩展),示例 `--replay-mode=kernel`。
- **运行时通道开启**:通过 `prof_drv_start(device_id, channel_id, prof_start_para)` 在待调优应用同一进程中开启 profiling 通道;`prof_stop(device_id, channel_id)` 关闭。
- **运行时数据读取**:用阻塞 `prof_channel_poll(poll_info, count, timeout)`(单次最多 polling 6 个有数据上报通道)配合非阻塞 `prof_channel_read(device_id, channel_id, buffer, size)`(buffer 最大 `1024*1024*2`)轮询读取。
- **采集项配置**:用户输入的采集项拆解为 AIV/AIC 两个 Event ID 队列,每次重放取最多 8 个 Event ID(PMU 上限),按队列顺序重组分析。
- **进程挂接方式**:工具拉起调优程序时,通过 **`LD_PRELOAD`** 注入 `prof-injection`,劫持 Device/Context 接口(`rtSetDevice` / `rtSetDeviceEx` / `rtCtxCreate`)以完成 `device_id` 获取与通道/线程挂接。
- **重放执行顺序**:第 1 次为空跑(解 warm-up),第 2~n 次按用户配置采集。
- **内存约束**:硬件上申请的内存空间不得超过总空间的一半,以保证有足够空间做 memory backup。
- **副本搬运**:必须使用 `rtMemcpyAsync`(SDMA)+ `rtSynchronizeStream`,不要使用 `rtMemcpy`(CPU 路线,会出现 Cache 异常)。

A5/310P 的具体启用/配置流程、Use Case 二的启用方式、性能/可靠性/安全设计细节,原文标注为 `NA` 或留空,尚未涉及。

## 图文联合解读

- `image-1.png`: 图为三层链路：Insight含Timeline、负载和指令密度；AscendC、MsTX、DFX、DWARF经msprof op采集指令流、Trace、统计与Roofline；Runtime Injection连接runtime与CAModel。数据贯通源码至芯片，实现上板采集与自定义算子瓶颈分析。
- `image-3.png`: 图是按 task_id 排列的性能数据表（非流程图，无数据流），标注 task_time、total_cycles、MAC/MTE2比率与周期及 L2Cache命中率。各任务耗时约229–295 μs，MAC周期固定1,499,840，MTE2约81–85万，L2命中率约32.5%–32.9%，指标较稳定，可用于横向比较和瓶颈定位，支撑性能采集及算子优化。
- `image-2.png`: 图示为一次 Kernel 执行周期的内存保存/恢复流程：Setup 后，Kernel 将 Memory 状态保存到 Backup；Kernel 暂停时先 Restore 上次备份，再保存新状态，后续 Kernel 重复此过程。灰色双箭头表示未执行或调度切换。论证了通过 Memory 与 Backup 的周期性 Save/Restore 保留算子中间状态，为上板性能分析提供连续、可回溯的数据，支撑文档“上板数据采集”与“自定义算子性能分析”方案。
- `image-4.png`: 图中三步展示：Host侧申请Device内存，将a、a′映射为连续块；第一次KernelLaunch按地址和大小定位并建立缓存，第二次复用该块；覆盖数据时自动invalid cache。结论是缓存可按块复用并保持一致性，减少重复分配，保障多次上板性能采集，为算子瓶颈分析提供数据基础。
- `image-5.png`: 1）时序图展示用户程序、prof-injection、runtime间的内存申请、Kernel下发与完成、数据备份/恢复及释放；loop重放时先恢复数据。  
2）注入层透明管理算子生命周期，借记录表保障循环重放和数据正确。  
3）支撑文档所述自定义算子上板性能数据采集，为瓶颈分析提供依据。
- `image-6.png`: 图以 Prof Tool、Driver、T5、OMPI 为时序线，虚框标出“执行”：工具取 channel_list、启动并分配 data_buff；设备写缓冲，Tool 通过 read、同步读写指针取数，最后 flush、stop 返回。说明驱动与硬件协同完成可控的板上性能采集。它是文档“利用硬件/仿真数据定位算子瓶颈”总体方案的流程证明。
- `image-7.png`: 流程从检查是否显式指定Device开始：是则调用aclrtSetDevice，再按需创建Context和Stream（aclrtCreateContext/Stream）；否则跳过。随后可选调用aclrtGetRunMode获取软件栈运行模式。蓝色为必选、绿色为可选，说明Profiler在上板采集前完成运行环境初始化，兼容显式与自动配置，对应文档“自定义算子性能分析、数据采集与瓶颈优化”的总体方案。
- `image-8.png`: 图为上板采集时序：用户预加载libmsprof_stub.so，主线程调用prof_drv_start开通道并启动读取线程；线程循环轮询、读取驱动数据，结果经主线程返回用户。算子结束后线程有序停止并关通道。说明采集与算子运行解耦，对应Use Case一，为后续瓶颈分析供数。
