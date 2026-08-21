# Ascend 950 — 技术点深读（DEEP 2026-08-18，2026-08-21 织入 22 图 M3 解读）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：昇腾 950 NPU 架构白皮书 · arXiv:—（华为白皮书，2026/1/1）
> 图号说明：原文图号为中文「图3-1/图4-1」编码；MD 抽取层记作 Figure 301/401（章*100+节内序号）。本笔记统一用中文原图号。formulas.json 为空，公式与编码格式均以散文引用。

## 核心问题
面向下一代 LLM/AIGC/多模态/推荐场景，前代（910C，见 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）架构在三处触及瓶颈（§2 引言）：
1. **算力增速 < 需求增速**——LLM 推理算力需求增长远超硬件迭代，需低精度格式（FP8/MXFP4）提升有效算力；而 910C 不原生支持 FP8（CloudMatrix384 论文实测需 INT8 PTQ + SmoothQuant/GPTQ 补偿），是上一代硬伤。
2. **互联/内存墙**——LLM 预训练单次 All-to-All 通信达数十 MB、一次迭代数百 GB（百倍于小模型）；AI Agent 长上下文使 KV Cache 呈指数增长，单卡内存不敷使用。
3. **算存比失衡**——多模态生成 vs 理解算存比差异巨大，单一硬件类型无法最佳性价比覆盖全场景。

为此推出两款共架构衍生品：**950PR**（128GB/1.6TB/s，面向推荐+Prefill+多模态推理）与 **950DT**（144GB/4TB/s，面向全量训练+复杂推理/Decode）。两者均基于自研第三代 DaVinci 架构 + 灵衢（Unified Bus 2.0）互联，目标支撑**万亿+ 参数模型**与**超 128K 卡集群**（§2、§3）。

**整体架构（图3-1, p.12）**：芯片架构示意图确认了多 Die 合封的物理形态——两片镜像对称的 **AI Die** 居中，各含中央 AI Core 大阵列、两翼 Linx816 CPU、上下 L2 Cache 轨、外缘 DVPP 单元与 Memory Interface 控制器（对外接 Global Memory/HBM）；两片 **IO Die** 分居最左最右，承载 PCIe5.0 CTRL、Security Core、UB CTRL 与底部 Hilink I/O 端口。Die 间由内缘 D2D 链路 + STARS 桥接互连，对外经 PCIe5.0 与 Hilink 出片。这张图把后文所有创新点的物理位置一次讲清：2 AI-Die + 2 IO-Die chiplet 经高速 D2D 合成单一 UMA 域，是 CCU、Cube-Vector 融合与 8K 卡超节点全部故事的载体。

## 关键创新点

1. **第三代 DaVinci Core：低精度算力跃升（§3、§4.1）**
   - 原生新增 **HiF8 / MXFP8 / FP8 / MXFP4** 张量格式（910C 缺失的 FP8 在此补齐）。
   - 同频下：HiF8/MXFP8/FP8 提供 **2× FP16** 张量 TFLOPS；MXFP4 提供 **4× FP16**（§4.1.1）。
   - 顶配 950DT Cube+Vector 总算力：MXFP4 **2007 TFLOPS**、HiF8/MXFP8/FP8 **1034 TFLOPS**、BF16/FP16 **547 TFLOPS**、TF32 **273 TFLOPS**（表3-1）。
   - Vector Core FP32/FP16 单核算力较上代 **+100%**，消除 FlashAttention 等融合算子中非矩阵操作的瓶颈（§4.1.2）。
   - **AI Core 三列式结构（图4-1, p.17）**：顶层 Bus Interface 下，中列是控制与矩阵计算枢纽——Scalar 0 → L1 Buffer（512KB）→ 分流为 L0A（64KB）+ L0B（64KB）双输入缓冲 → Cube Core（16×16×16 FP16 矩阵乘）→ 结果写回 L0C（256KB）；左右两列各是一个 Vector Core（Scalar 2/1 控制，各 64×64 FP32 / 128×128 FP16 lane），各配 UB0/UB1（256KB）与独立 Register File。数据通路：Bus → L1 → L0A/L0B → Cube → L0C → 回流 UB 或 L1，Vector Core 在 UB 与寄存器堆间并行流水。矩阵密集负载（Cube + 分裂输入缓冲 + L0C 累加）与向量/element-wise 负载（双 Vector + 对称 UB）解耦并发，共享 L1 层级最大化吞吐与访存复用——这正是表2 Memory 层次（L1 512KB / L0A/L0B 各 64KB / L0C 256KB / UB 512KB）的电路图版本。
   - **Cube Core 微架构与精度谱（图4-2/图4-3, p.18）**：图4-2 给出乘加阵列结构——水平 x₀…x_{k-1} 与垂直 y₀…y_{k-1} 输入进入乘法器链，乘积汇入共享累加器，再馈入 4×4 PE 立方阵列，即脉动 MAC 流水线 + 可配置 PE 阵列。图4-3 以位布局图列出全部原生精度：32-bit（FP32 1/8/23、TF32 1/8/10）、16-bit（BF16 1/8/7、FP16 1/5/10）、8-bit（HiF8 动态位宽、FP8-E5M2 1/5/2、FP8-E4M3 1/4/3）、4-bit（FP4 1/2/1）——同一套硬件从 FP32 一路缩到 FP4，精度换吞吐/带宽的取舍完全留给用户。

2. **HiF8：自研锥形精度 8-bit 浮点格式（§4.1.1）**
   - 目标：在 8-bit 开销下兼顾精度与动态范围，避免 MXFP8 需额外 8-bit MX 缩放因子的开销。
   - 机制：(a) 用变长前缀码 Dot 域显式指示阶码位宽与 Denormal 标志→锥形精度格式；(b) 阶码原码编码并隐藏 1 bit 固定值→不同位宽阶码范围不重复、无冗余；(c) Subnormal 设计将综合阶码范围从 [-15,15] 扩到 **[-22,15] 共 38 个 power-of-2**，接近 FP16 的 40 个；编码 4 个特殊值（表4-1：ZERO=00000000，NAN=10000000，+INF=01101111，-INF=11101111）。
   - **HiF8 位布局（图4-4, p.19）**：两张编码表把上述机制可视化。Normal 编码 X = (-1)^S × 2^E × 1.M：8-bit 字被划分为 1 个符号位 S + 变长 Dot 前缀（0–4）+ 剩余阶码位 E（含 1 个隐藏位，图中标红）+ 尾数位 M；Dot 每加 1，阶码范围翻倍（E=0, ±1, ±[2,3], ±[4,7], ±[8,15]），形成靠近 1 精度高、远离 1 渐变的锥形分布。Denormal 编码 X = (-1)^S × 2^(M−23) × 1.0，借 Subnormal 设计把范围下探到 E∈[−22,−16]。图例明确 Dot 域同时充当 Denormal 标志、阶码用原码且隐藏位不存储（红色标注）——无冗余编码与 38 档指数空间的来源一目了然。
   - 对比 FP8 E4M3 的 18 个指数表达，HiF8 动态范围成倍提升，且数值靠近 1 精度高、远离 1 渐变无跳变。

3. **新同构 SIMD/SIMT 混合编程（§4.1.3）**
   - 以 SIMD 为主、SIMT 为辅，在同一 Vector Core 上切换：基本函数块 Vector Function (VF) 可选 SIMD 或 SIMT 实现。
   - SIMD 走双发 ALU + 乱序执行（Out-of-Order），适配 element-wise 规则访存；SIMT 适配 gather/scatter、Hash Insert 等不规则/分支场景。
   - **Vector Core 双模前端（图4-5, p.21）**：架构图显示左半是共享前端（Scalar Unit、按执行类型打标 SIMD/SIMT/NULL 的 Async Function Queues、DMA Unit、Vector Cache/Buffer、Bus Interface），右半分裂为两条调度路径——SIMD 模式走 I Cache → Program Sequence → **QoO Dispatch**（乱序）→ Vector Cache/Uniform Buffer（N bank + Cache Controller + Coalescing Unit）→ Vector Load/Store → 寄存器堆（Lane 0…VL-1）→ Vector Execution Unit；SIMT 模式走 I Cache → Program Sequence → **Warp Scheduler** → In-order Dispatch → 同一 Vector Cache/Uniform Buffer → SIMT Load/Store → SIMT 寄存器堆（Lane 0…warp_size-1）→ 同一 Vector Execution Unit。两种模式复用同一套存储子系统与执行后端，只换前端调度逻辑（QoO vs Warp）与寄存器布局——"同构混合"的硬件含义即此：VF 粒度在编译/启动时选模式，零硅片冗余。
   - 效果：兼顾高带宽利用率与编程灵活性，便于算子融合、代码跨架构可移植。

4. **CV 融合 + 随路量化（§4.1.1、§4.1.4）**
   - Cube L1 Buffer ↔ Vector Unified Buffer 直连通道，减少 L2 层交换；针对 FlashAttention 带宽瓶颈。
   - L0C→UB 回写阶段直接完成 **FP32→BF16/FP16/FP8 量化** + **NZ→ND/DN 排布转换**，降低核内缓冲占用与核间带宽消耗。
   - **融合拓扑（图4-6, p.22）**：示意图中两个 Vector Core（左 Vector Core 1 + UB1，右 Vector Core 0 + UB0）夹住中央 Cube Core，Cube 上接 L0A/L0B、下接 L0C、顶置 L1；双向箭头标明直连通路——UB1 ↔ L0A 与 L0B ↔ UB0 让 Vector 侧直接向 Cube 供操作数，L0C 计算结果经 UB0/UB1 回流 Vector，全程绕过 L2；上下 Bus Interface 只管对外流量。图中直连耦合正是"随路完成数据排布/精度转换"的物理基础。
   - FlashAttention 单核性能较上代提升 **1.5~2×**（§3、§4.1）。

5. **NDDMA 指令（§4.1.5）**
   - N-dimensional DMA，硬化地址生成，对全局内存数据做最多 **5 维重排**后写入 Vector UB，单指令同时完成搬运+排布转换/转置（如 NCHW↔NHWC）。
   - **指令语义（图4-7, p.23）**：图示两段式内存变换——左侧 Global Memory 32 行阵列中，数据元素（1–24）稀疏散布在非连续行（如行 0 存 {1,13}、行 2 存 {5,17}、行 21 仅存 {4}），按原始行组色标、呈列向跨步模式；中间一条 NDDMA 硬件级 DMA 箭头；右侧 Unified Buffer 中同样的值已按序致密排布（1,2,3,5,6,7,9,10,11,…），连续无跨步。搬运与重排/转置融合在单条指令内完成。
   - 内置缓存自动发掘局部性，将元素粒度读合并为 **128B 读**，提升访存效率，简化 Kernel 编程。

6. **BufferID 同步机制（§4.1.6）**
   - 类互斥锁语义：`get_buf()`/`rel_buf()` 直观表达流水线对 AI Core 内部存储的占用/释放，内聚性优于传统 `set_flag/wait_flag`，与其他流水线解耦。
   - **代码对比（图4-8, p.24）**：同页并排两段 100 次迭代流水线代码，箭头示意从新到旧——左侧旧机制每个迭代要 wait 上游 Vector 的 flag、执行 MTE2、set/clear 自身 flag、再等 MTE2 flag 才能跑 Vector()，最后发下一个生产者 flag，且需 `if i>0` 边界检查与 `if i<99` 尾部条件；右侧 BufferID 机制用 get_buf/rel_buf 在 MTE2 与 Vector 两级流水上锁步配对（申请 MTE2 缓冲→搬运→释放；申请 Vector 缓冲→计算→释放）。每级每迭代的 4 次 flag 操作压缩为 2 次 get/rel 配对，边界迭代 corner case 全消，且把流水线缓冲占用显式暴露给运行时以改进调度重叠。

7. **128MB L2 Cache + Sector/Hint/CMO（§3、§4.3.2）**
   - Chiplet 2-Die UMA 架构，硬件维护跨 Die 一致性，软件不感知；局部亲和性。
   - **内存层次全景（图4-9, p.25）**：双 Die（Die 0/Die 1）各自内含 AI Core（AIC 带 L1/L0A/L0B/L0C，AIV 带 UB）与 AI CPU（带 CPU L1/L2）；自底向上两条异构通路——AIC/AIV 各级缓冲汇入 **L2 Cache**，AI CPU 的 L1/L2 汇入 **L3 Cache**，两路再经 **Directory（目录式一致性）** 汇聚到 Global Memory。AI 加速与标量控制的访存路径解耦、由目录层统一维护跨 Die 一致性，是"软件不感知的 UMA"的实现方式。
   - 微架构：多 Bank 分布式，**512B Cache Line**，新增 **128B Sector Cache**（支持 4×128B Sector），每 Bank 可同时读写；高位异或交织算法升级。
   - **L2 Hint**：程序员按数据流标注 non-allocate 等策略，避免短期不用数据驱逐热数据（图4-10, p.27 给出 Non-allocate 典型应用场景示意，与 STARS2.0 架构图同页）。
   - **CMO（Cache Maintenance Operation）** via SDMA：Prefetch / Writeback / Invalid / Flush，可配置时机与范围。
   - 同带宽下，离散小包+随机访存性能较上代 **>2×**（§3）。

8. **灵衢 Unified Bus 2.0 互联（§4.6）**
   - 72 Lane HiLink SerDes，18 个 x4 Port，每 Port 4×112Gbps，整芯片对外 IO 峰值 **2TB/s**；UB 双向带宽 **2016GB/s**（表3-1、§4.6）。
   - 双语义：**同步 UB Memory**（Load/Store/Atomic，最大 **128TB** Host-Device/Device-Device 内存共享）+ **异步 URMA**（Jetty 队列、Doorbell、UMMU 地址翻译）。
   - **URMA 异步通路（图4-12, p.31）**：本端节点 Core 触发 Doorbell → URMA 引擎经本地 UMMU 从本地 Memory 取数 → 分发到多个 Port 并发跨节点传输；远端节点 Port 汇入远端 UMMU，完成地址翻译后写入远端 Memory。UMMU 在两端都处在关键路径上，提供 VA→PA 翻译与访问权限控制——跨节点内存访问的安全虚拟化与多端口并行由此而来。
   - **UB Memory 同步通路（图4-13, p.32）**：源芯片 Core 发起访问 → UB Mem Decoder 路由到出端口 → 跨片互连 → 目的芯片 Port 接收 → 目的端 UMMU 做地址翻译+权限检查 → 直接读写远端 Memory。同步语义（Write/Read + AtomicStore/AtomicLoad/AtomicSwap/AtomicCompareAndSwap）由硬件在目的端完成语义级地址翻译，源端零软件介入，一致性开销极低。
   - URMA 支持 Write/Write-Immediate/Write-Notify/Read/Send/Send-Immediate/Atomic FetchAdd/CompareAndSwap；两种传输层：**RTP**（可靠重传，4 Port 带宽，多 Transport Channel 多路径）与 **CTP**（轻量不可靠，9 Port 带宽，支持多路径）。
   - **UBoE**：UB over Ethernet，2×400Gbps，Port Bifurcation 1x400/200/100/50/25Gbps 或 2x200/100/50/25Gbps，与 UB Link 静态复用 SerDes。
   - **UB On Chip Switch（图4-15, p.34）**：单 IO Die 内嵌转发面——顶部 NoC、中部全端口共享 Routing Table、底部 9 个 x4 Port；入端口流量查路由表，若判定非本芯片流量则经 NoC 转发至出端口送出，全程不进计算 Die、不占 DRAM 带宽，IO Die 即成 Layer-2 级交换面，支持注入+转发混合部署，给 leaf-spine/环形/混合拓扑留出低成本组网空间。
   - **PCIe 5.0（图4-16, p.35）**：控制器经双向链路上接片上 System Bus，内部为四层协议栈——Application 层（内嵌 MCTP 与 DMA 加速器）→ Transaction → DataLink → x16 Physical，下接独立 Serdes 块出片；向后兼容 Gen4/3/2/1，链宽可配 x16/x8/x4/x2，EP/RC 双模静态选择，128GB/s 双向。

9. **CCU 集合通信卸载（§4.6.4）**
   - Collective Communication Unit 接收 STARS 下发任务，按软件预置算法自搬运、自同步、自计算（Reduce）。
   - 展开为并行小颗粒任务循环，支持 Broadcast / Reduce Scatter / All Gather / All Reduce / All2All / All2Allv。
   - **CCU 三层架构（图4-14, p.33）**：顶层 **CCUM（Management）**——Mission Call Interface 进 Mission Commander，经指令解析单元分流到 Reduce Call Interface 或 URMA Call Interface；中层多个 **CCUA（Agent）** 各集成 MemorySlice（存储）+ Reduce Unit（计算）；底层 **URMA** 模块桥接 URMA Call Interface 到 Port 阵列做远端搬运。硬件分发把本地归约与远端 RDMA 式搬运干净分离，CCUA 充当计算+存储一体端点；任务完成后经 Mission 编程接口上报状态。
   - 效果：减少通信对系统总线带宽占用，释放 AI Core 算力，计算与通信深度并行，降低主存占用与 IO 调度延迟（§3 第 4 点）。

10. **超节点规模跃升（§4.7）**
    - 超节点从上代 **384 卡（CloudMatrix384）** 提升到 **8192 卡（8K）**，整体集群支持 **>128K 卡**（§3、§4.6）。
    - **超节点拓扑（图4-17, p.36）**：三级结构——顶层一排 UB Switch（Spine，可扩展）、中层两组 Leaf Switch 各服务一个 pod/rack、底层每组多片昇腾950 全互连（Full Mesh），整体构成两级胖树/类 Clos：片内组全网格 → Leaf → Spine → 对端 Leaf → 对端组。任一昇腾950 经至多两跳交换即达任意对等芯片，超节点表现为单一逻辑计算域；拓扑支持 Full Mesh / Clos / 混合，同一硅片可重部署到不同集群形态。
    - 超大内存池（图4-18, p.36，与超节点图同页）：Rack/Pod 计算芯片经 UB 端口直接访问 CPU 大内存池（高带宽低延时）；超大存储资源池（图4-19, p.37）——胖树式拓扑中中央 Switch 扇出到两个 Rack：左 Rack 是 CPU+昇腾950 计算 pod，右 Rack 是 5×4 Storage 节点存储 pod，计算芯片经原生 UB 端口免协议转换直达整个存储池。
    - **与以太世界互通的两条路径**：图4-20（p.38）走 UB Switch 转换——超节点边界内两台 UB Switch 各暴露 ETH 上行口与 UB 下行口，交叉冗余上接外部以太交换机，下接全网格 UB 互连的昇腾950 阵列，UB↔以太翻译由 UB Switch 原生完成、无需额外网关；图4-21（p.39）走 UBoE 直连——昇腾950 自带 ETH 端口全网格上接服务器内两台以太交换机（再交叉上联外部交换机），芯片间仍以 UB 环/总线互连，直接插标准商用以太交换机，与以太生态无缝互通。
    - 基于 UB Switch 组 K 级超节点，支持 Full Mesh / Clos / nD-Mesh / 混合拓扑；UB Switch 或 UBoE+以太 Switch 扩展。

11. **STARS2.0 硬件调度器（§4.4）**
    - Host 下沉 **2048 条任务流**到 Device 侧；专用 **HSCB（High Speed Control Bus）** 与 AIC/AIV 交互，调度开销 ns 级，支持广播调度。
    - **调度架构（图4-11, p.27）**：STARS 容器持有 Task 槽阵列与四个伴生特性——Notify Sync、Conds、Profiling、Fusion；下方 Sched 调度条把任务扇出到两张互连面：**HSCB → AIV/AIC**（计算引擎）与 **NoC → UB DMA/SDMA/CCU/CPU/DVPP**（搬数与通用引擎）。Notify Sync/Conds 编排依赖，Profiling/Fusion 采集运行时遥测——全芯片异构引擎统一在单一调度器下做软硬件协同调度。
    - 并发上限：16 AI CPU 任务 / 64 Host CPU 任务 / 64 UB jetty / 32 CCU 任务 / 32 SDMA 通道；同步标志 128K 单比特或 4096 个 32-bit 多比特。
    - Group 调度：AI Core 等资源分最多 **8 个 Group**，按 Die 亲和调度利用 L2 局部性。
    - 算力切分：AIC/AIV/SDMA 最多 16 个资源池，其他加速器最多 8 个池，绑定 VM 实现隔离。
    - 实时 TOP-DOWN Profiling（执行时间/算力开销/带宽/功耗）。

12. **多 Die 合封 + UMA + RAS（§3、§4.3.1）**
    - 整芯片合封 **2 AI Die + 2 IO Die + 8（950PR）/4（950DT）高速片上内存模块**，D2D Clink + Memory Interface 互连，构成 UMA 整体（物理布局见图3-1, p.12；内存层次见图4-9, p.25）。
    - 高速片上内存 RAS：Online ECC、巡检回写/隔离、预留行动失效隔离（用户无感知）。

13. **DVPP 图片处理子系统（§4.5）**
    - 4×VPC + 4×JPEGE + 8×JPEGD，支持 STARS 直接硬件调度（在图4-11 的 NoC 调度面上与 UB DMA/SDMA/CCU 并列）；DVPP 单元在芯片版图上的位置见（图3-1, p.12）AI Die 外缘。
    - VPC 算子覆盖对标 OpenCV/TensorFlow/TorchVision/Pillow/DALI（Resize/Crop/Padding/上下采样/CSC/HSV/Affine/Perspective/PixAug）。
    - JPEGD/JPEGE 最大分辨率 32768×32768，JPEGD 对标 libjpeg-turbo v2.0.2，支持区域解码。

## 表格（原文结构化）

### 表1：950PR vs 950DT 核心规格（源自表3-1，挑选关键项）
| 规格项 | 昇腾950PR | 昇腾950DT |
|---|---|---|
| Cube Core 数量 | 32/28 | 36/32/28 |
| Vector Core 数量 | 64/56 | 72/64/56 |
| Cube+Vector MXFP4 (TFLOPS) | 1784/1561 | 2007/1784/1561 |
| Cube+Vector HiF8/MXFP8/FP8 (TFLOPS) | 919/804 | 1034/919/804 |
| Cube+Vector INT8 (TOPS) | 919/804 | 1034/919/804 |
| Cube+Vector BF16/FP16 (TFLOPS) | 486/425 | 547/486/425 |
| Cube+Vector TF32 (TFLOPS) | 243/212 | 273/243/212 |
| Cube MXFP4 (TFLOPS) | 1730/1513 | 1946/1730/1513 |
| Cube HiF8/MXFP8/FP8 (TFLOPS) | 865/756 | 973/865/756 |
| Vector FP16/BF16 (TFLOPS) | 54/47 | 60/54/47 |
| Vector FP32 (TFLOPS) | 27/23 | 30/27/23 |
| Memory 容量 (GB) | 128/112 | 144/96 |
| Memory 带宽 (TB/s) | 1.6/1.4 | 4 |
| AI CPU Subsys | Linx816 8C16T/6C12T/4C8T, NEON | Linx816 8C16T/6C12T, NEON |
| DVPP VPC | 4/2 Core, 5760/2880 FPS@1080P | 4/2 Core, 5760/2880 FPS@1080P |
| Image Decoder | 8 JPEGD, 4096 FPS@1080P, max 32K×32K | 同左 |
| Image Encoder | 4/2 JPEGE, 1024/512 FPS@1080P, max 32K×32K | 同左 |
| L2 Cache 容量 (MB) | 128/112 | 128 |
| L2 Cache 配置 | 512B Line, 4×128B Sector, Hint, CMO | 同左 |
| 互联协议 | URMA-CTP/URMA-TP/UB Memory/PCIe 5.0/UBoE | 同左 |
| UB 带宽 | 18 Port×112Gbps, 2016GB/s 双向 | 同左 |
| UBoE | 2×400Gbps（与 UB 共用 2 端口） | 同左 |
| PCIe | 5.0 x16, 128GB/s 双向（与 UB 共用 4 端口） | 同左 |

> 说明：表中斜杠分隔多个规格值，对应冗余设计衍生的不同版本（§3 末段）。

### 表2：Memory 层次容量（源自表4-2；层次拓扑见图4-9, p.25，核内缓冲位置见图4-1, p.17）
| Memory | Size |
|---|---|
| L1 Buffer | 512KB per AI Core |
| L0A Buffer | 64KB per AI Core |
| L0B Buffer | 64KB per AI Core |
| L0C Buffer | 256KB per AI Core |
| Unified Buffer (UB) | 512KB per AI Core |
| CPU L1 Cache | 64KB per CPU Core |
| CPU L2 Cache | 1MB per CPU Core |
| L3 Cache | 4MB per CPU Cluster |
| L2 Cache | Up to 128MB |
| 950PR 片上内存 | Up to 128GB |
| 950DT 片上内存 | Up to 96/144GB |

### 表3：HiF8 特殊值编码（源自表4-1；位布局机制见图4-4, p.19）
| 特殊值 | 编码 |
|---|---|
| ZERO | 00000000 |
| NAN | 10000000 |
| +INF | 01101111 |
| -INF | 11101111 |

### 表4：UB 2.0 互联特性摘要（源自 §4.6；同步/异步通路见图4-12/图4-13，片上转发见图4-15）
| 特征 | 规格 |
|---|---|
| UB 协议版本 | Unified Bus 2.0 |
| UB IO 带宽 | UB 2016GB/s 双向；UBoE 200GB/s 双向（与 UB 复用 SerDes） |
| UB 端口模式 | UB 18 个 x4 Port（可降 x2/x1）；UBoE 2 个 x4 或 4 个 x2（可降 x2/x1） |
| UB 编程接口 | 同步 UB Memory；异步 URMA；CCU 集合通信加速 |
| UB 互联规模 | 最大 8192 卡超节点 |
| UB 可靠性 | 链路层重传 + 端到端可靠性重传 |
| UB 拓扑 | Clos / Full Mesh+Clos / nD-Mesh |
| UB On Chip 转发 | 支持 |
| UB 组网扩展 | UB Switch 或 UBoE+以太 Switch |
| PCIe | 5.0，128GB/s 双向，1×16（可降 x8/x4/x2），RC/EP 静态双模 |

## 与同类对比
- **vs 前代 910C（[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）**：910C 无 FP8 原生支持（CloudMatrix384 靠 INT8 PTQ + SmoothQuant/GPTQ 补偿），950 原生补齐 FP8/MXFP8/MXFP4/HiF8（精度谱见图4-3），MXFP4 张量算力 4×；超节点 384→8192 卡（图4-17）；新增 UB Memory 同步语义（图4-13）、URMA-CTP/RTP 双模（图4-12）、CCU 集合通信卸载（图4-14）、NDDMA（图4-7）、SIMD/SIMT 混合编程（图4-5）、BufferID 同步（图4-8）、L2 Hint/CMO/Sector Cache（图4-9/图4-10）、STARS2.0（图4-11：2048 任务流、8 Group）。
- **vs GPU-based serving（vLLM/Mooncake/SGLang）**：本质差异——NPU + UB shared-memory fabric + 内存语义（UB Memory/URMA）+ 硬件 CCU 集合通信卸载，而非 GPU + RDMA/NCCL verbs。GPU 体系靠 PagedAttention/KVCache-centric disaggregation 软件层补内存语义缺失；950 把内存共享（128TB）、集合通信、同步原语下沉到硅片。CCU 把 AllReduce/All2All 等卸载为硬件循环任务，对应 GPU 侧 NCCL 的软件栈。
- **vs NVIDIA NVLink/NVSwitch**：NVLink 面向 GPU 直连+统一内存空间（NVLink-C2C/Cache-Coherent），UB 2.0 类比——同为 scale-up 专用总线 + 超节点，但 UB 进一步融合 scale-out（UBoE 直接接以太，图4-20/图4-21 两条互通路径）与同步/异步双语义；超节点 8K 卡规模为单协议栈领先指标。
- **低精度格式**：HiF8 是 950 的差异化格式，对标 OCP MX format（MXFP8/MXFP4 微缩放）与 NVIDIA FP8(E4M3/E5M2)。HiF8 以 38 个 power-of-2 动态范围接近 FP16（图4-4 的 Normal/Denormal 双编码表），免去 MX 缩放因子开销——在 8-bit 极低开销下走精度/范围折衷路线。

## 跨论文关系（→ MOC 谱系）
- → [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]：**直接前代基线**。910C 是 950 的前代，CloudMatrix384 论文提供 910C 在 SuperPod serving 的实测行为（MTE2/MTE3 ping-pong、AIV/AIC 划分、NPU-Direct URMA、XCCL far-memory 原语、INT8 PTQ）。950 正是对这些痛点的硅片级回应：补齐 FP8（解 INT8 PTQ 精度损失）、CCU 硬件卸载集合通信（解 MTE2/MTE3/AIV 被通信占用问题）、UB Memory 同步语义 + 128TB 内存共享（解 host-centric 内存语义缺失）、超节点 384→8192（解规模上限）。
- → [[parallel-scan-on-ascend-ai-accelerators]]：**平台关系**。950 是该论文所述 NPU parallel scan 的承载平台；950 的 SIMD/SIMT 混合编程（图4-5 双模前端）、NDDMA 5 维重排（图4-7）、L2 Cache Hint/Sector Cache、CCU 卸载为 parallel scan 类算法提供硬件基础。950 的 Vector Core FP32/FP16 算力 +100% 直接利好 scan/vector-bound 算子。
- → GPU-based serving 谱系（[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]、[[sglang-efficient-execution-of-structured-language-model-programs]]、[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]、[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]）：形成 **NPU-arch 路线 vs GPU-soft-stack 路线** 的对照。950 把 KV Cache 共享、集合通信、内存语义下沉到硅片（UB Memory 128TB、CCU、URMA），而 Mooncake/PagedAttention/SGLang 在 GPU+RDMA 上用软件层（KVCache-centric、PagedKV、RadixAttention）实现等价能力。950 的超大内存池/存储资源池组网（§4.7.2/4.7.3，图4-18/图4-19）直接对标 Mooncake 的 disaggregated KV pool 与 Prefill-as-a-Service 的 cross-datacenter KV。
- → 训练栈（[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]、[[zero-memory-optimizations-toward-trillion-parameter-models]]）：950 面向"万亿+参数"训练，CCU + UB 2.0 + 128K 卡集群是对 MegaScale/ZeRO 类分布式训练通信/内存优化的硬件替代路径。
- Ascend 950 作为 **NPU-architecture anchor** 置于 serving/NPU-cluster 主题，与 GPU-based（vLLM/Mooncake/SGLang）形成路线对照。

## 局限与边界
- **白皮书性质**：华为官方白皮书，规格数字为峰值/上限，无第三方实测；arXiv 无索引，方法论不可复现。表3-1 多个规格值（如 36/32/28）源于冗余设计衍生版本，对应实际产品形态需结合商业合同，文档明示"可能不在购买范围"。
- **缺精度对比数据**：HiF8 vs MXFP8/FP8 在真实 LLM 任务的端到端精度/吞吐 tradeoff 未给（图4-4 仅给编码机制与阶码范围，无精度实验曲线）；MXFP4 "4× FP16" 是峰值算力，实际有效算力依赖量化质量。
- **950PR 带宽不对称**：950PR 仅 1.6TB/s（vs 950DT 4TB/s），虽面向 Prefill/推荐，但 Prefill 本身算力密集，带宽可能成瓶颈——文档未给 Prefill 场景下的 roofline 或实测。
- **超节点规模 vs 实际拓扑**：8192 卡超节点为"最大支持"，实际组网需 UB Switch 多级级联（图4-17 仅示一级 Spine/Leaf 示意），文档未给不同拓扑下的集合通信 latency/throughput 实测；384→8192 跨度为 21×，物理布线、光模块成本、故障域未讨论。
- **UBoE 与 UB 端口争用**：400G 以太端口与 UB Link 静态复用 SerDes，启用 UBoE 即减少一个 400G UB 端口——scale-out 与 scale-up 带宽互斥，文档未给混合部署的带宽分配策略（图4-20/图4-21 两条互通路径的选型准则亦未量化）。
- **软件栈成熟度**：CANN 虽"全面开源开放"，但与 CUDA/NCCL 生态差距未讨论；STARS2.0 的 Group/算力切分在多租户场景的实际隔离强度（性能、安全）未给量化。
- **缺能效数据**：无 TOPS/W、TDP、液冷需求等功耗指标，950DT 顶配 144GB/4TB/s HBM 的功耗/散热边界未披露。
- **DVPP 上限**：JPEGD/JPEGE 最大 32K×32K，对标 libjpeg-turbo v2.0.2——对超高清/专业影像（如医疗 16-bit）支持未明示，仅 8-bit YUV。
- **无 FlashAttention 实测**：仅给"单核 1.5~2×"相对值（机制侧见图4-6 融合通路），无绝对 tokens/s 或与 FlashAttention-2/3 的对比。
