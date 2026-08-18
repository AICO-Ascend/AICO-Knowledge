# Ascend 950 — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：昇腾 950 NPU 架构白皮书 · arXiv:—（华为白皮书，2026/1/1）

## 核心问题
面向下一代 LLM/AIGC/多模态/推荐场景，前代（910C，见 [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）架构在三处触及瓶颈（§2 引言）：
1. **算力增速 < 需求增速**——LLM 推理算力需求增长远超硬件迭代，需低精度格式（FP8/MXFP4）提升有效算力；而 910C 不原生支持 FP8（CloudMatrix384 论文实测需 INT8 PTQ + SmoothQuant/GPTQ 补偿），是上一代硬伤。
2. **互联/内存墙**——LLM 预训练单次 All-to-All 通信达数十 MB、一次迭代数百 GB（百倍于小模型）；AI Agent 长上下文使 KV Cache 呈指数增长，单卡内存不敷使用。
3. **算存比失衡**——多模态生成 vs 理解算存比差异巨大，单一硬件类型无法最佳性价比覆盖全场景。

为此推出两款共架构衍生品：**950PR**（128GB/1.6TB/s，面向推荐+Prefill+多模态推理）与 **950DT**（144GB/4TB/s，面向全量训练+复杂推理/Decode）。两者均基于自研第三代 DaVinci 架构 + 灵衢（Unified Bus 2.0）互联，目标支撑**万亿+ 参数模型**与**超 128K 卡集群**（§2、§3）。

## 关键创新点

1. **第三代 DaVinci Core：低精度算力跃升（§3、§4.1）**
   - 原生新增 **HiF8 / MXFP8 / FP8 / MXFP4** 张量格式（910C 缺失的 FP8 在此补齐）。
   - 同频下：HiF8/MXFP8/FP8 提供 **2× FP16** 张量 TFLOPS；MXFP4 提供 **4× FP16**（§4.1.1）。
   - 顶配 950DT Cube+Vector 总算力：MXFP4 **2007 TFLOPS**、HiF8/MXFP8/FP8 **1034 TFLOPS**、BF16/FP16 **547 TFLOPS**、TF32 **273 TFLOPS**（表3-1）。
   - Vector Core FP32/FP16 单核算力较上代 **+100%**，消除 FlashAttention 等融合算子中非矩阵操作的瓶颈（§4.1.2）。

2. **HiF8：自研锥形精度 8-bit 浮点格式（§4.1.1）**
   - 目标：在 8-bit 开销下兼顾精度与动态范围，避免 MXFP8 需额外 8-bit MX 缩放因子的开销。
   - 机制：(a) 用变长前缀码 Dot 域显式指示阶码位宽与 Denormal 标志→锥形精度格式；(b) 阶码原码编码并隐藏 1 bit 固定值→不同位宽阶码范围不重复、无冗余；(c) Subnormal 设计将综合阶码范围从 [-15,15] 扩到 **[-22,15] 共 38 个 power-of-2**，接近 FP16 的 40 个；编码 4 个特殊值（表4-1：ZERO=00000000，NAN=10000000，+INF=01101111，-INF=11101111）。
   - 对比 FP8 E4M3 的 18 个指数表达，HiF8 动态范围成倍提升，且数值靠近 1 精度高、远离 1 渐变无跳变。

3. **新同构 SIMD/SIMT 混合编程（§4.1.3）**
   - 以 SIMD 为主、SIMT 为辅，在同一 Vector Core 上切换：基本函数块 Vector Function (VF) 可选 SIMD 或 SIMT 实现。
   - SIMD 走双发 ALU + 乱序执行（Out-of-Order），适配 element-wise 规则访存；SIMT 适配 gather/scatter、Hash Insert 等不规则/分支场景。
   - 效果：兼顾高带宽利用率与编程灵活性，便于算子融合、代码跨架构可移植。

4. **CV 融合 + 随路量化（§4.1.1、§4.1.4）**
   - Cube L1 Buffer ↔ Vector Unified Buffer 直连通道，减少 L2 层交换；针对 FlashAttention 带宽瓶颈。
   - L0C→UB 回写阶段直接完成 **FP32→BF16/FP16/FP8 量化** + **NZ→ND/DN 排布转换**，降低核内缓冲占用与核间带宽消耗。
   - FlashAttention 单核性能较上代提升 **1.5~2×**（§3、§4.1）。

5. **NDDMA 指令（§4.1.5）**
   - N-dimensional DMA，硬化地址生成，对全局内存数据做最多 **5 维重排**后写入 Vector UB，单指令同时完成搬运+排布转换/转置（如 NCHW↔NHWC）。
   - 内置缓存自动发掘局部性，将元素粒度读合并为 **128B 读**，提升访存效率，简化 Kernel 编程。

6. **BufferID 同步机制（§4.1.6）**
   - 类互斥锁语义：`get_buf()`/`rel_buf()` 直观表达流水线对 AI Core 内部存储的占用/释放，内聚性优于传统 `set_flag/wait_flag`，与其他流水线解耦。

7. **128MB L2 Cache + Sector/Hint/CMO（§3、§4.3.2）**
   - Chiplet 2-Die UMA 架构，硬件维护跨 Die 一致性，软件不感知；局部亲和性。
   - 微架构：多 Bank 分布式，**512B Cache Line**，新增 **128B Sector Cache**（支持 4×128B Sector），每 Bank 可同时读写；高位异或交织算法升级。
   - **L2 Hint**：程序员按数据流标注 non-allocate 等策略，避免短期不用数据驱逐热数据（图4-10）。
   - **CMO（Cache Maintenance Operation）** via SDMA：Prefetch / Writeback / Invalid / Flush，可配置时机与范围。
   - 同带宽下，离散小包+随机访存性能较上代 **>2×**（§3）。

8. **灵衢 Unified Bus 2.0 互联（§4.6）**
   - 72 Lane HiLink SerDes，18 个 x4 Port，每 Port 4×112Gbps，整芯片对外 IO 峰值 **2TB/s**；UB 双向带宽 **2016GB/s**（表3-1、§4.6）。
   - 双语义：**同步 UB Memory**（Load/Store/Atomic，最大 **128TB** Host-Device/Device-Device 内存共享）+ **异步 URMA**（Jetty 队列、Doorbell、UMMU 地址翻译）。
   - URMA 支持 Write/Write-Immediate/Write-Notify/Read/Send/Send-Immediate/Atomic FetchAdd/CompareAndSwap；两种传输层：**RTP**（可靠重传，4 Port 带宽，多 Transport Channel 多路径）与 **CTP**（轻量不可靠，9 Port 带宽，支持多路径）。
   - **UBoE**：UB over Ethernet，2×400Gbps，Port Bifurcation 1x400/200/100/50/25Gbps 或 2x200/100/50/25Gbps，与 UB Link 静态复用 SerDes。
   - **UB On Chip Switch**：单 IO Die 内 9 个 x4 Port 间转发，流量不经计算 Die、不占 DRAM 带宽，在 IO Die 上完成转发；支持注入+转发混合部署。
   - **PCIe 5.0**：1×16 Port（可降 x8/x4/x2），128GB/s 双向，RC/EP 双模静态选择，含 DMA/MCTP 加速器。

9. **CCU 集合通信卸载（§4.6.4）**
   - Collective Communication Unit 接收 STARS 下发任务，按软件预置算法自搬运、自同步、自计算（Reduce）。
   - 展开为并行小颗粒任务循环，支持 Broadcast / Reduce Scatter / All Gather / All Reduce / All2All / All2Allv。
   - 架构：CCUM（Mission 入口）+ CCUA（MemorySlice 存储 + Reduce Unit 计算）；URMA 搬运调用 URMA 引擎，Reduce 调用 CCUA 计算单元。
   - 效果：减少通信对系统总线带宽占用，释放 AI Core 算力，计算与通信深度并行，降低主存占用与 IO 调度延迟（§3 第 4 点）。

10. **超节点规模跃升（§4.7）**
    - 超节点从上代 **384 卡（CloudMatrix384）** 提升到 **8192 卡（8K）**，整体集群支持 **>128K 卡**（§3、§4.6）。
    - 基于 UB Switch 组 K 级超节点，支持 Full Mesh / Clos / nD-Mesh / 混合拓扑；UB Switch 或 UBoE+以太 Switch 扩展。
    - 超大内存池：Rack/Pod 计算芯片经 UB 端口直接访问 CPU 大内存池（高带宽低延时）；超大存储资源池：免存储协议转换开销直接访问。

11. **STARS2.0 硬件调度器（§4.4）**
    - Host 下沉 **2048 条任务流**到 Device 侧；专用 **HSCB（High Speed Control Bus）** 与 AIC/AIV 交互，调度开销 ns 级，支持广播调度。
    - 并发上限：16 AI CPU 任务 / 64 Host CPU 任务 / 64 UB jetty / 32 CCU 任务 / 32 SDMA 通道；同步标志 128K 单比特或 4096 个 32-bit 多比特。
    - Group 调度：AI Core 等资源分最多 **8 个 Group**，按 Die 亲和调度利用 L2 局部性。
    - 算力切分：AIC/AIV/SDMA 最多 16 个资源池，其他加速器最多 8 个池，绑定 VM 实现隔离。
    - 实时 TOP-DOWN Profiling（执行时间/算力开销/带宽/功耗）。

12. **多 Die 合封 + UMA + RAS（§3、§4.3.1）**
    - 整芯片合封 **2 AI Die + 2 IO Die + 8（950PR）/4（950DT）高速片上内存模块**，D2D Clink + Memory Interface 互连，构成 UMA 整体。
    - 高速片上内存 RAS：Online ECC、巡检回写/隔离、预留行动失效隔离（用户无感知）。

13. **DVPP 图片处理子系统（§4.5）**
    - 4×VPC + 4×JPEGE + 8×JPEGD，支持 STARS 直接硬件调度。
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

### 表2：Memory 层次容量（源自表4-2）
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

### 表3：HiF8 特殊值编码（源自表4-1）
| 特殊值 | 编码 |
|---|---|
| ZERO | 00000000 |
| NAN | 10000000 |
| +INF | 01101111 |
| -INF | 11101111 |

### 表4：UB 2.0 互联特性摘要（源自 §4.6）
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
- **vs 前代 910C（[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）**：910C 无 FP8 原生支持（CloudMatrix384 靠 INT8 PTQ + SmoothQuant/GPTQ 补偿），950 原生补齐 FP8/MXFP8/MXFP4/HiF8，MXFP4 张量算力 4×；超节点 384→8192 卡；新增 UB Memory 同步语义、URMA-CTP/RTP 双模、CCU 集合通信卸载、NDDMA、SIMD/SIMT 混合编程、BufferID 同步、L2 Hint/CMO/Sector Cache、STARS2.0（2048 任务流、8 Group）。
- **vs GPU-based serving（vLLM/Mooncake/SGLang）**：本质差异——NPU + UB shared-memory fabric + 内存语义（UB Memory/URMA）+ 硬件 CCU 集合通信卸载，而非 GPU + RDMA/NCCL verbs。GPU 体系靠 PagedAttention/KVCache-centric disaggregation 软件层补内存语义缺失；950 把内存共享（128TB）、集合通信、同步原语下沉到硅片。CCU 把 AllReduce/All2All 等卸载为硬件循环任务，对应 GPU 侧 NCCL 的软件栈。
- **vs NVIDIA NVLink/NVSwitch**：NVLink 面向 GPU 直连+统一内存空间（NVLink-C2C/Cache-Coherent），UB 2.0 类比——同为 scale-up 专用总线 + 超节点，但 UB 进一步融合 scale-out（UBoE 直接接以太）与同步/异步双语义；超节点 8K 卡规模为单协议栈领先指标。
- **低精度格式**：HiF8 是 950 的差异化格式，对标 OCP MX format（MXFP8/MXFP4 微缩放）与 NVIDIA FP8(E4M3/E5M2)。HiF8 以 38 个 power-of-2 动态范围接近 FP16，免去 MX 缩放因子开销——在 8-bit 极低开销下走精度/范围折衷路线。

## 跨论文关系（→ MOC 谱系）
- → [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]：**直接前代基线**。910C 是 950 的前代，CloudMatrix384 论文提供 910C 在 SuperPod serving 的实测行为（MTE2/MTE3 ping-pong、AIV/AIC 划分、NPU-Direct URMA、XCCL far-memory 原语、INT8 PTQ）。950 正是对这些痛点的硅片级回应：补齐 FP8（解 INT8 PTQ 精度损失）、CCU 硬件卸载集合通信（解 MTE2/MTE3/AIV 被通信占用问题）、UB Memory 同步语义 + 128TB 内存共享（解 host-centric 内存语义缺失）、超节点 384→8192（解规模上限）。
- → [[parallel-scan-on-ascend-ai-accelerators]]：**平台关系**。950 是该论文所述 NPU parallel scan 的承载平台；950 的 SIMD/SIMT 混合编程、NDDMA 5 维重排、L2 Cache Hint/Sector Cache、CCU 卸载为 parallel scan 类算法提供硬件基础。950 的 Vector Core FP32/FP16 算力 +100% 直接利好 scan/vector-bound 算子。
- → GPU-based serving 谱系（[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]、[[sglang-efficient-execution-of-structured-language-model-programs]]、[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]、[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]）：形成 **NPU-arch 路线 vs GPU-soft-stack 路线** 的对照。950 把 KV Cache 共享、集合通信、内存语义下沉到硅片（UB Memory 128TB、CCU、URMA），而 Mooncake/PagedAttention/SGLang 在 GPU+RDMA 上用软件层（KVCache-centric、PagedKV、RadixAttention）实现等价能力。950 的超大内存池/存储资源池组网（§4.7.2/4.7.3）直接对标 Mooncake 的 disaggregated KV pool 与 Prefill-as-a-Service 的 cross-datacenter KV。
- → 训练栈（[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]、[[zero-memory-optimizations-toward-trillion-parameter-models]]）：950 面向"万亿+参数"训练，CCU + UB 2.0 + 128K 卡集群是对 MegaScale/ZeRO 类分布式训练通信/内存优化的硬件替代路径。
- Ascend 950 作为 **NPU-architecture anchor** 置于 serving/NPU-cluster 主题，与 GPU-based（vLLM/Mooncake/SGLang）形成路线对照。

## 局限与边界
- **白皮书性质**：华为官方白皮书，规格数字为峰值/上限，无第三方实测；arXiv 无索引，方法论不可复现。表3-1 多个规格值（如 36/32/28）源于冗余设计衍生版本，对应实际产品形态需结合商业合同，文档明示"可能不在购买范围"。
- **缺精度对比数据**：HiF8 vs MXFP8/FP8 在真实 LLM 任务的端到端精度/吞吐 tradeoff 未给（仅给阶码范围/特殊值编码等机制描述）；MXFP4 "4× FP16" 是峰值算力，实际有效算力依赖量化质量。
- **950PR 带宽不对称**：950PR 仅 1.6TB/s（vs 950DT 4TB/s），虽面向 Prefill/推荐，但 Prefill 本身算力密集，带宽可能成瓶颈——文档未给 Prefill 场景下的 roofline 或实测。
- **超节点规模 vs 实际拓扑**：8192 卡超节点为"最大支持"，实际组网需 UB Switch 多级级联，文档未给不同拓扑下的集合通信 latency/throughput 实测；384→8192 跨度为 21×，物理布线、光模块成本、故障域未讨论。
- **UBoE 与 UB 端口争用**：400G 以太端口与 UB Link 静态复用 SerDes，启用 UBoE 即减少一个 400G UB 端口——scale-out 与 scale-up 带宽互斥，文档未给混合部署的带宽分配策略。
- **软件栈成熟度**：CANN 虽"全面开源开放"，但与 CUDA/NCCL 生态差距未讨论；STARS2.0 的 Group/算力切分在多租户场景的实际隔离强度（性能、安全）未给量化。
- **缺能效数据**：无 TOPS/W、TDP、液冷需求等功耗指标，950DT 顶配 144GB/4TB/s HBM 的功耗/散热边界未披露。
- **DVPP 上限**：JPEGD/JPEGE 最大 32K×32K，对标 libjpeg-turbo v2.0.2——对超高清/专业影像（如医疗 16-bit）支持未明示，仅 8-bit YUV。
- **无 FlashAttention 实测**：仅给"单核 1.5~2×"相对值，无绝对 tokens/s 或与 FlashAttention-2/3 的对比。
