# Communication Optimization

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/docs/en/performance_tuning/performance_tuning_methods/communication_basics_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/docs/en/performance_tuning/performance_tuning_methods/communication_basics_overview.md

# Communication Basics Overview 深度解读

---

## 【定位】

本文档是 HCCL（华为集合通信库）的**通信基础与优化概览**，聚焦昇腾 AI 处理器场景下分布式训练所依赖的硬件互联（PCIe / HCCS / RoCE）与软件栈架构，并给出 5 个面向性能调优的环境变量/配置项（HCCL_INTRA_ROCE_ENABLE、HCCL_RDMA_TC、HCCL_RDMA_SL、HCCL_BUFFSIZE、hccl_buffer_size），用于在特定硬件拓扑或资源受限场景中替换传输链路、调整 RDMA QoS 与通信域 buffer 大小。

---

## 【技术要点】

1. **HCCL 定位与链路**：基于昇腾 AI 处理器的高性能集合通信库，覆盖单节点多设备与多节点多设备场景，通过 PCIe、HCCS、RoCE 三类高速链路实现分布式训练；底层机制涉及 DMA / RDMA / Full Mesh 等。
2. **HCCL_INTRA_ROCE_ENABLE = 1**：在 Atlas 200T A2 Box16 部署单机 16-NPU 服务时，将两组 8-NPU 之间的 mesh 互连链路由 **SDMA 替换为 RDMA**；推荐用于设备虚拟化场景或 PCIe 带宽较低（**< 20 GB/s**）的场景。
3. **HCCL_RDMA_TC**：RDMA NIC 的流量类（traffic class），取值 **[0, 255]**，须为 **4 的整数倍**，默认值 **132**；对应 RoCE v2 IP 包头的 8-bit ToS 字段，其中 bit[0:1] 固定为 0，bit[2:7] 为 DSCP，关系为 **DSCP = HCCL_RDMA_TC / 4**（例：100 = 25×4 → DSCP=25）。
4. **HCCL_RDMA_SL**：RDMA NIC 的服务级别，取值 **[0, 7]**，默认 **4**；必须与 NIC 的 PFC 优先级一致，否则 RDMA 通信带宽下降。
5. **HCCL_BUFFSIZE**：控制两个 NPU 共享数据的 buffer 大小（MB），最小 1，默认 **200 MB**；每个 HCCL 通信域独占 **2 × HCCL_BUFFSIZE**（发送、接收各一份），用于多通信域并发时互不干扰，且内存专属于 HCCL、不可被其他服务复用。
6. **hccl_buffer_size**：相比 HCCL_BUFFSIZE（仅全局级别），可在每个通信域粒度单独设置 buffer 大小（MB，最小 1，无上限，默认 200 MB），通过 `torch.distributed.init_process_group` / `torch.distributed.new_group` 传入 `ProcessGroupHCCL.Options()`。

---

## 【关键机制与数据】

- **三层硬件互联**（原文术语）：
  - PCIe：CPU ↔ NPU 的串行扩展总线。
  - HCCS：NPU ↔ NPU 的高速总线，构成 8-NPU **Full Mesh** 全互联拓扑，任意两节点直连。
  - RoCE v2：基于以太网的 RDMA，跨节点通信。
- **DMA / RDMA 语义**：DMA 绕过 CPU 直接在外部设备与内存间高速搬运数据；RDMA 是可穿越网络的 DMA；RoCE 是承载于以太网的 RDMA。
- **Full Mesh 拓扑特征**：节点两两直连，常用于高可靠、高带宽场景（数据中心、HPC、金融交易）。
- **架构图三张**（原文提供图片引用，未含数值表）：
  - Figure 1 软件架构（`communication_basics_overview_fig_01.png`）
  - Figure 2 8-NPU 硬件架构（`communication_basics_overview_fig_02.png`）—— HCCS Full Mesh + PCIe 接 CPU。
  - Figure 3 16-NPU 硬件架构（`communication_basics_overview_fig_03.png`）—— 两组 8-NPU mesh 之间的互连可由 SDMA 切到 RDMA（HCCL_INTRA_ROCE_ENABLE 触发）。
- **HCCL_RDMA_TC 与 DSCP 映射关系**（原文图示 `HCCL_RDMA_TC_fig_01.png`）：8-bit ToS = `[DSCP(6 bit)][2 bit 固定 0]`，因此 4 倍关系成立。
- **hccl_buffer_size 分场景配置策略**（原文给出 4 条）：
  - 纯 SDMA 通信：按 `通信数据量 / rank size` 较大值配置。
  - RDMA 通信：按通信数据量配置。
  - SendRecv：按实际收发数据量配置。
  - Alltoallv：按总通信量 `max(input[rank size], output[rank size])` 配置。
- **性能数据**：原文未提供 benchmark 数字，仅给出"PCIe < 20 GB/s 时建议启用 RDMA"这类阈值提示。

---

## 【表格解读】

**原文无表格**（5 个优化项均以"Function Description / Configuration Example / Use Case"三段文字 + 代码片段形式呈现，未列出对照表或参数表）。

---

## 【公式解读】

**原文无 LaTeX 公式**，但存在两处需要解释的"准公式"：

### 1. HCCL_BUFFSIZE 推荐值公式（原文以图片形式 `HCCL_BUFFSIZE_fig_01.png` 给出，未展开 LaTeX）

> 原文：The recommended value is calculated as follows, which should be rounded up.
> 变量解释（原文给出）：
> - **Micro Batch Size**：每设备上的 batch size
> - **Sequence Length**：序列长度
> - **Hidden Size**：模型隐藏层维度
> - **Size of Data Type**：当前模型数据类型占用的内存大小
>
> 作用：根据模型数据量上取整计算 HCCL_BUFFSIZE 推荐值，避免配置过小导致通信性能下降。

### 2. DSCP 与 HCCL_RDMA_TC 的换算（原文给出）

```
DSCP = HCCL_RDMA_TC / 4
```

- **HCCL_RDMA_TC**：RDMA NIC 流量类，整数倍 4，∈ [0, 255]
- **DSCP**（Differentiated Services Code Point）：IP 包头 ToS 字段高 6 位（bit[2:7]）
- 作用：环境变量实际写入 ToS 字段，但交换路由 QoS 通常按 DSCP 解读，因此需要此换算（例：`HCCL_RDMA_TC=100` → DSCP=25）。

---

## 【关联】

文档自身交叉引用与外延：

- **HCCL_BUFFSIZE → hccl_buffer_size**：原文明确"`HCCL_BUFFSIZE` can only configure the global HCCL communication domain buffer size. For related content, see [HCCL_BUFFSIZE](#hccl_buffsize)"——前者全局、后者单域，构成"全局默认 + 单域覆盖"的层级关系。
- **hccl_buffer_size → torch.distributed**：通过 `torch.distributed.init_process_group` 和 `torch.distributed.new_group` 两个入口传入，绑定到 `ProcessGroupHCCL.Options` 的 `hccl_config` 字典。
- **C 接口集成**：HCCL_BUFFSIZE 的典型场景之一是"开发者调用 HCCL 的 C 语言接口进行框架集成"，对应外链 **HCCL Collective Communication Library Guide → API Reference**（https://www.hiascend.com/document/detail/en/CANNCommunityEdition/910/commlib/hcclug/docs/en/api_ref/hccl_header_and_lib.md）。
- **上下游**：本文档位于 `PyTorch/docs/en/performance_tuning/performance_tuning_methods/` 性能调优方法目录下，属于 PyTorch + HCCL 集合通信性能优化的基础章节，其上游依赖 Ascend NPU 硬件（Atlas 200T A2 Box16 等具体机型）与 CANN 软件栈；本目录其它性能调优方法（推理、算子融合等）可视为下游平行章节。
- **硬件前置**：HCCL_INTRA_ROCE_ENABLE 仅适用于 Atlas 200T A2 Box16 的 16-NPU 拓扑；HCCS Full Mesh 描述对应 8-NPU 单机组——这意味着各优化项的启用条件**与硬件拓扑强绑定**，不可脱离机型泛用。

---

## 【使用方法】

### HCCL_INTRA_ROCE_ENABLE
```shell
export HCCL_INTRA_ROCE_ENABLE=1
```
启用条件：Atlas 200T A2 Box16 单机 16-NPU；建议场景：设备虚拟化，或 PCIe 带宽 < 20 GB/s。

### HCCL_RDMA_TC
```shell
# 配置为 25*4 = 100，DSCP 值为 25
export HCCL_RDMA_TC=100
```
约束：值 ∈ [0,255]，必须为 4 的整数倍，默认 132；启用条件：Ascend NIC 与交换机 QoS 不匹配导致 RDMA 通信带宽下降。

### HCCL_RDMA_SL
```shell
export HCCL_RDMA_SL=3
```
约束：值 ∈ [0,7]，默认 4；启用条件：同 HCCL_RDMA_TC，且必须与 NIC 上的 PFC 优先级一致。

### HCCL_BUFFSIZE（全局）
```shell
export HCCL_BUFFSIZE=200
```
约束：单位 MB，≥ 1，默认 200；推荐值由 Micro Batch Size、Sequence Length、Hidden Size、Data Type 大小计算后向上取整；启用条件：
- 动态 shape 网络
- C 接口框架集成（详见 *HCCL Collective Communication Library Guide* 的 API Reference 章节）
- 部署内存不足时下调；模型数据小而通信数据大时上调；配置低于推荐值则通信性能下降。

### hccl_buffer_size（单通信域）
```python
options = torch_npu._C._distributed_c10d.ProcessGroupHCCL.Options()
options.hccl_config = {"hccl_buffer_size": 200}
torch.distributed.init_process_group(backend='hccl', pg_options=options)
```
```python
options = torch_npu._C._distributed_c10d.ProcessGroupHCCL.Options()
options.hccl_config = {"hccl_buffer_size": 200}
torch.distributed.new_group(backend="hccl", pg_options=options)
```
约束：单位 MB，最小 1，无上限，默认 200；分场景策略见上文【关键机制与数据】；启用条件：需要对单个通信域细粒度调 buffer、且部署内存不足或通信数据量分布不均时。

## 图文联合解读

- `communication_basics_overview_fig_02.png`: **图文解读：**

8个NPU（NPU1-8）通过HCCS（蓝线）两两直连，构成Full Mesh全互连拓扑，实现片间高带宽集合通信；4个CPU（CPU1-4）间互连，并通过PCIe（绿线）分别挂接各NPU，作为控制与数据通路。

**论证结论：** HCCS提供NPU间低延迟高带宽互联，PCIe负责CPU-NPU通信，二者协同支撑HCCL的分布式训练通信原语。

**与文档关系：** 即文档所述"Figure 2 Hardware architecture (8-NPU)"，印证"Full Mesh interconnection achieved via HCCS"的论述。
- `communication_basics_overview_fig_03.png`: **图文解读：**

1）图示双CPU（CPU1/CPU2）经4个PCIe-SW，以绿色PCIe链路连接两组8-NPU集群；每组内部8个NPU（NPU1-8）经蓝色HCCS总线构成Full Mesh全连接拓扑。

2）论证了HCCL硬件层由两级互连构成：NPU间通过HCCS高带宽全互联实现高速对等通信，NPU↔CPU通过PCIe-SW扩展接入主机。

3）支撑文档论点——HCCL基于PCIe与HCCS高速链路提供单节点多设备集合通信原语，是分布式训练的通信底座。
- `HCCL_BUFFSIZE_fig_01.png`: # 图文联合解读

**1) 图中内容**
图中呈现一个分数公式：分子为 *Micro Batch Size × Sequence Length × Hidden Size × Size of Data Type*；分母为 *1024 × 1024*。

**2) 技术结论**
该公式用于估算分布式训练中的**单卡激活/梯度显存占用（MB）**：将微批次内每个 token 的隐藏层数据按四维度相乘得到总字节数，再除以 1MB（1024²），从而量化单设备在一次前向/反向中需存储的张量体积。

**3) 与文档关系**
虽归入"Communication Optimization"，但该图实际服务于**通信开销分析**：通信量与张量体积直接挂钩——显存数据越大，All-Reduce/AllGather 等集合通信传输的字节数越多，越能凸显 HCCL 在 HCCS/RoCE 高速互联上做通信优化的必要性。
