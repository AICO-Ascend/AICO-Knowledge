# 通信优化

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/docs/zh/performance_tuning/performance_tuning_methods/communication_basics_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/docs/zh/performance_tuning/performance_tuning_methods/communication_basics_overview.md

# 通信基础概述 深度解读

## 【定位】

本篇文档描述昇腾 AI 处理器上 **HCCL（华为集合通信库）** 在分布式训练场景下的硬件互联基础与通信优化环境变量配置方法，覆盖 HCCS/PCIe/RoCE 等高速链路的拓扑特性，以及用于路由 QoS、缓冲区大小、SDMA/RDMA 切换等场景的五类调优开关，用于解决集群训练中的通信带宽与跨域缓存占用问题。

---

## 【技术要点】

1. **HCCL 的硬件互联链路**：NPU 与 NPU 之间通过 HCCS（Full Mesh 直连）互联；NPU 与 CPU 通过 PCIe 互联；多机多卡借助 RoCE（RoCE v2）跨越以太网实现 RDMA 通信。三种术语共同构成集合通信的底层传输通道（PCIe、HCCS、RoCE）。

2. **HCCL_INTRA_ROCE_ENABLE**：仅针对 **Atlas 200T A2 Box16** 异构子框的**单 server 16P** 业务。开启后（`=1`），两个 8P 之间用 RDMA 链路替代 SDMA 链路作为 mesh 互联。原文建议场景：设备虚拟化场景，或 PCIe 带宽不足 **20 GB/s** 时。

3. **HCCL_RDMA_TC**：用于配置 RDMA 网卡的 traffic class（对应 IP 头 ToS 域）。取值范围 **[0, 255]**，必须为 **4 的整数倍**，默认 **132**。其值除以 4 即等于 DSCP。原文示例：配为 `100`，对应 DSCP = 25。

4. **HCCL_RDMA_SL**：用于配置 RDMA 网卡的 service level，必须与网卡配置的 PFC 优先级保持一致，否则可能性能劣化。取值范围 **[0, 7]**，默认 **4**。原文示例：`=3`。

5. **HCCL_BUFFSIZE**：控制两个 NPU 之间共享数据缓存区大小。单位 MB，取值 ≥1，默认 **200 MB**。每个 HCCL 通信域占用 **2 × HCCL_BUFFSIZE** 的内存（发送 + 接收各一份），各通信域独占、不可复用。原文推荐配置公式：`向上取整( Micro Batch Size × Sequence Length × Hidden Size × Size of Data Type × 2 )`。

6. **hccl_buffer_size**：与 HCCL_BUFFSIZE 同样控制单通信域缓存大小，但粒度更细——可在每个通信域单独设置。最小值 1 MB，最大无上限，默认 **200 MB**。计算原则：纯 SDMA 按「较大通信数据量 / rank size」、含 RDMA 按「较大通信数据量」、SendRecv 按「实际收发数据量」、Alltoallv 按 `max(input[rank size], output[rank size])`（总通信量）。

---

## 【关键机制与数据】

**集合通信域的内存模型（原文）：**

> 每一个 HCCL 通信域都会占用 2 × HCCL_BUFFSIZE 大小的缓存区。若集群网络中存在较多的 HCCL 通信域，此缓存区占用量就会增多。此资源按通信域粒度管理，每个通信域独占一组 2 × HCCL_BUFFSIZE 大小的内存，保证多通信域并发算子互不影响。该环境变量申请的内存为 HCCL 独占，不可与其他业务内存复用。

**SDMA ↔ RDMA 切换（原文）：**

> Atlas 200T A2 Box16 异构子框进行单 server 16P 业务部署，开启 [HCCL_INTRA_ROCE_ENABLE] 后，两个 8P 之间使用 RDMA 链路代替 SDMA 链路作为 mesh 间互联链路。

**RoCE v2 ToS/DSCP 编码（原文）：**

> 在 RoCE V2 协议中，该值 [HCCL_RDMA_TC] 对应 IP 报文头中 ToS（Type of Service）域。共 8 个 bit，其中，bit[0,1] 固定为 0，bit[2,7] 为 DSCP，因此，该值除以 4 即为 DSCP 的值。

> Default：HCCL_RDMA_TC = 132 → DSCP = 132 / 4 = 33。

**PFC 优先级一致性（原文）：**

> [HCCL_RDMA_SL] 该值需要和网卡配置的 PFC 优先级保持一致，若配置不一致可能导致性能劣化。

**Full Mesh 拓扑语义（原文）：**

> Full Mesh 是指在一个网络拓扑中，每个节点都直接连接到其他节点，形成一个完全互联的网络结构。任何两个节点之间都可以直接通信，通常用于需要高度可靠性和高带宽的应用场景。

> 原文未给出实测带宽、时延或加速比等量化性能数据；所有图示（软件架构图、硬件架构图 8p / 16p）以及 HCCL_BUFFSIZE 推荐配置图均为示意图，未提供具体数值。

---

## 【表格解读】

**原文无表格**。

原文仅含三张示意图（软件架构图 / 硬件架构图 8p / 硬件架构图 16p）以及 HCCL_RDMA_TC、HCCL_BUFFSIZE 的两张说明性配图，均未以表格形式逐行列出参数对照或性能对比，故按要求标注 "原文无表格"。

---

## 【公式解读】

**原文无完整公式（LaTeX/伪代码形式）**，但给出两处计算式，逐字保留并说明如下：

### 1) HCCL_BUFFSIZE 推荐配置（原文图片内文字 + 文字描述）

> 向上取整（ Micro Batch Size × Sequence Length × Hidden Size × Size of Data Type × 2 ）

| 符号 | 含义（原文释义） |
| --- | --- |
| Micro Batch Size | 每张卡上的 batch size |
| Sequence Length | 序列长度 |
| Hidden Size | 模型隐藏层的维度 |
| Size of Data Type | 当前模型数据类型所占的内存大小 |
| 乘以 2 | 原文约定，表示按发送 + 接收两侧总量估算 |
| 向上取整 | 取整方式 |

**作用：** 估算单个 HCCL 通信域所需的缓存区大小，作为 HCCL_BUFFSIZE 配置值的下限参考；不足此值会导致通信性能下降。

### 2) hccl_buffer_size 计算方法（原文文字描述）

| 通信类型 | 计算方式（原文） |
| --- | --- |
| 纯 SDMA 通信 | 按照「较大通信数据量 / rank size」配置 |
| 带有 RDMA 通信 | 按照「较大通信数据量」配置 |
| SendRecv | 按照「实际收发数据量」配置 |
| Alltoallv | 按照总通信量配置 `max(input[rank size], output[rank size])` |

**作用：** 为每类集合通信原语分别给出缓存区大小的计算口径，避免全局统一配置造成的内存浪费或通信拥塞。

---

## 【关联】

根据原文上下文可梳理出的内部关联如下：

1. **hccl_buffer_size 与 HCCL_BUFFSIZE 的作用域关系**：
   > 原文："HCCL_BUFFSIZE 环境变量只能配置全局 HCCL 通信域缓存区大小……hccl_buffer_size 配置可用于分别设置每个通信域的 hccl_buffer_size 大小。"
   
   二者控制相同的物理量（单通信域共享缓存大小，单位 MB，默认均 200），但 hccl_buffer_size 粒度更细，可针对单个通信域覆盖全局默认值。

2. **HCCL_RDMA_TC / HCCL_RDMA_SL 与网络 QoS 的耦合**：
   > 原文："昇腾网卡与交换机 QoS（Quality of Service，服务质量）不匹配导致 RDMA 通信带宽下降时，需要进行配置。"
   
   TC 对应 RoCE v2 IP 头 DSCP，SL 对应 PFC 优先级——两者均需与交换机侧 QoS 策略保持一致。

3. **HCCL_INTRA_ROCE_ENABLE 与 HCCS / SDMA / RDMA 链路的依赖**：
   > 该开关仅在 Atlas 200T A2 Box16 + 单 server 16P 拓扑中生效，把 8P↔8P 的 mesh 互联由 SDMA 改为 RDMA，是 HCCS 高速总线之外的第二条跨 8P 互联路径。

4. **与 HCCL C 语言接口的关联**（原文外链）：
   > 原文指向《HCCL 集合通信库指南》"[API 参考](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910/commlib/hcclug/docs/zh/api_ref/hccl_header_and_lib.md)"章节，说明 HCCL_BUFFSIZE 也可用于框架对接的 C 接口调用场景。

5. **硬件架构层（PCIe / HCCS / RoCE）的支撑**：
   > 全文背景为分布式训练，所有集合通信原语均建立在 PCIe、HCCS、RoCE 三类高速链路之上，本篇中各环境变量是对这些链路参数（traffic class、service level、buffer）层面的软件调优手段。

> 备注：原文文末内部链接信息为 "(无)"，上述关联均基于文档内正文交叉引用与外链整理。

---

## 【使用方法】

下列环境变量 / 配置项均按原文给出启用方式：

### 1) HCCL_INTRA_ROCE_ENABLE（shell 环境变量）
```shell
export HCCL_INTRA_ROCE_ENABLE=1
```
启用条件：Atlas 200T A2 Box16 异构子框 + 单 server 16P。

### 2) HCCL_RDMA_TC（shell 环境变量）
```shell
# DSCP = 25 → HCCL_RDMA_TC = 25 * 4 = 100
export HCCL_RDMA_TC=100
```
范围 [0, 255]，4 的整数倍，默认 132。

### 3) HCCL_RDMA_SL（shell 环境变量）
```shell
export HCCL_RDMA_SL=3
```
范围 [0, 7]，默认 4；需与网卡 PFC 优先级保持一致。

### 4) HCCL_BUFFSIZE（shell 环境变量）
```shell
export HCCL_BUFFSIZE=200
```
单位 MB，≥1，默认 200；按 `Micro Batch Size × Sequence Length × Hidden Size × Size of Data Type × 2` 向上取整配置。

### 5) hccl_buffer_size（Python 接口入参，支持 init_process_group / new_group）
```python
options = torch_npu._C._distributed_c10d.ProcessGroupHCCL.Options()
options.hccl_config = {"hccl_buffer_size":200}
torch.distributed.init_process_group(backend='hccl', pg_options=options)
```
```python
options = torch_npu._C._distributed_c10d.ProcessGroupHCCL.Options()
options.hccl_config = {"hccl_buffer_size":200}
torch.distributed.new_group(backend="hccl", pg_options=options)
```
最小 1 MB，默认 200 MB；按通信类型（纯 SDMA / 含 RDMA / SendRecv / Alltoallv）选择对应计算口径。

## 图文联合解读

- `communication_basics_overview_fig_02.png`: **图文解读：**

1）图中绘制了8个NPU（NPU1–NPU8）通过蓝色HCCS总线两两直连，形成Full Mesh全互联拓扑；同时通过绿色PCIe链路分别接入4个CPU（CPU1–CPU4），CPU间亦互连。

2）论证了NPU间通过HCCS实现任意两点直接通信，NPU–CPU间通过PCIe连接的两级分层架构。

3）对应文档"图2 硬件架构图（8p）"，印证"Full Mesh实现NPU两两互联、NPU与CPU通过PCIe连接"的硬件事实，为HCCL通信优化提供物理拓扑基础。
- `communication_basics_overview_fig_03.png`: **图文联合解读：**

图示16卡硬件拓扑：顶部两CPU经PCIe-SW下连两组8 NPU，每组内NPU以HCCS构成Full Mesh（蓝色），NPU与PCIe-SW/CPU间走PCIe（绿色）。

论证了**单server 16P部署的双8P Mesh架构**：组内靠HCCS高速互联，组间经PCIe链路打通。

对应文档「图3 硬件架构图（16p）」，为HCCL_INTRA_ROCE_ENABLE参数（双8P间以RDMA替代SDMA作为mesh互联）的应用场景提供拓扑依据。
- `HCCL_BUFFSIZE_fig_01.png`: **图文联合解读：**

**1）图示内容：** 公式分母为 `1024*1024`（即 MB 换算），分子为 `Micro Batch Size * Sequence Length * Hidden Size * Size of Data Type`，表示单 micro-batch 的数据体积（字节 → MB）。

**2）技术含义：** 该式用于估算分布式训练中单次前向/反向通信需传输的张量数据量（MB），是评估 HCCL 通信带宽、选择 RDMA TC / 链路方式（HCCS vs RoCE）的输入依据。

**3）与文档关系：** 图所在 `HCCL_RDMA_TC` 章节强调按流量类型配置 ToS/DSCP，其前提是先量化通信负载；该公式即为"通信基础"向"优化方法"过渡的量化桥梁，呼应"通信优化"主题。
