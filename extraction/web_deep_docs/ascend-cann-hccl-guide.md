# 通信域管理

> 来源 https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html
> 抓取路由 hiascend-source · 2026-09-04 22:17 · 原文 8293 字符 · 4 图
> MiniMax-M3 七节深读 · ver=v1 · 原文: extraction/web_docs/ascend-cann-hccl-guide.md

# 一体化深度解读：HCCL 通信域管理（CANN 商用 900）

---

## 【定位】

本文档系统阐述 HCCL（Huawei Collective Communication Library，集合通信库）中"通信域（Communicator / `HcclComm`）"的概念与四种典型创建方式（基于 rank table、基于 root 节点信息、单机批量创建、基于已有通信域切分子通信域），以及销毁流程，为多机/单机集合通信算子下发提供执行上下文与资源管理依据。

---

## 【技术要点】

1. **通信域与 rank 定义**（原文）：通信域是集合通信算子执行的上下文，管理对应的通信对象（一个 NPU 就是一个通信对象）；每个 rank 分配介于 `0~n-1`（n 为 NPU 数量）的唯一标识。

2. **基于 rank table 的多机建域**：通过 `HcclCommInitClusterInfo(rankTableFile, devId, &hcclComm)` 或带配置的 `HcclCommInitClusterInfoConfig` 创建通信域；每张卡需使用单独的进程。

3. **基于 root 节点信息的多机建域**：root 节点调用 `HcclGetRootInfo` 生成 `rootInfo`（包含 device ip、device id），广播到所有 rank 后，各 rank 调用 `HcclCommInitRootInfo` 或 `HcclCommInitRootInfoConfig` 完成初始化。两种典型场景：①每 Device 一进程；②每 AI Server 一进程，多线程对应多 Device。

4. **Atlas 350 加速卡的前置检查**：需检查 `/etc/hccl_rootInfo.json` 文件是否存在（记录 NPU 间通信的 EID，即 Entity ID，通信中发起或接收对象的标识），环境部署完成后自动生成。

5. **Host 侧通信 IP/NIC 指定（可选）**：
   - `HCCL_IF_IP`：配置 Host 与 root 节点通信的 IP（IPv4 或 IPv6，仅支持配置一个）。
   - `HCCL_SOCKET_FAMILY`：`AF_INET`（IPv4）或 `AF_INET6`（IPv6）。
   - `HCCL_SOCKET_IFNAME`：网卡名，支持 `=` 精确匹配、`^=` 排除匹配、模糊匹配（`^` 前缀表示排除），多网卡用英文逗号分隔。
   - **优先级**：原文明确 `HCCL_IF_IP` 的优先级高于 `HCCL_SOCKET_IFNAME`；两者均不配置时，系统按"docker/lo 以外网卡（字典序升序）> docker 网卡 > lo 网卡"自动选择。

6. **多进程端口隔离**：单卡多进程场景下，建议通过 `HCCL_HOST_SOCKET_PORT_RANGE` 与 `HCCL_NPU_SOCKET_PORT_RANGE` 分别配置 Host 侧与 NPU 侧通信端口，示例 `export ...="auto"`，否则可能端口冲突。

7. **单机批量创建**：`HcclCommInitAll(ndev, devices, comms)`，按 Device 列表顺序建域，每个 Device 一个线程调用集合通信 API；多线程调用时，前后时间差需小于建链超时（`HCCL_CONNECT_TIMEOUT` 默认 120s）。

8. **子通信域切分**：`HcclCreateSubCommConfig(&globalHcclComm, rankCount, rankIds, ...)` 基于已有通信域切分，无需 socket 建链与 rank 信息交换，适用于业务故障下的快速建域；**不支持嵌套切分**。

9. **销毁通信域**：`HcclCommDestroy(hcclComm)`，并需调用运行时管理接口释放内存、Stream、Device 资源。

10. **通用约束**（原文注意事项）：
    - 多个通信域在每个 Device 上必须**串行下发**，禁止乱序、多线程并发、线程重入；
    - 同一 Device 同一通信域的所有通信算子下发线程需使用**相同的 Context**；
    - 同一通信域内**不支持图模式与单算子通信混合执行**；
    - 同一 NPU 上**需串行创建**多个通信域；
    - 针对 Atlas A3 训练/推理系列产品，通信域初始化时若存在多个超节点，属于同一超节点内的 AI Server 信息必须配置在一起（例如"0"超节点排完再排"1"超节点），**不支持交叉配置**。

---

## 【关键机制与数据】

- **通信域作用**：为集合通信算子提供执行上下文，管理通信对象（NPU）与所需资源（原文）。
- **rank 标识范围**：`0~n-1`，n 为 NPU 数量（原文）。
- **建链超时默认值**：原文 `HCCL_CONNECT_TIMEOUT` 默认 `120s`（链接到环境变量参考）。
- **网卡自动选择优先级**（原文原文逐字）：
  ```
  docker/lo以外网卡(网卡名称的字典序升序) > docker 网卡 > lo网卡
  ```
- **超节点配置顺序约束**（原文，针对 Atlas A3 系列）：同超节点的 AI Server 信息需连续配置，不允许跨超节点交叉。
- **`/etc/hccl_rootInfo.json` 含义**：记录 NPU 间通信的 EID（Entity ID）信息，环境部署完成后自动生成（原文）。
- **子通信域切分语义**：无需 socket 建链与 rank 信息交换，仅做已有域的子集切分（原文）；不支持在子通信域中进一步切分子通信域（嵌套切分）。
- **多进程端口方案原文表述**：针对 Atlas 350 加速卡、Atlas A3 训练/推理系列产品、Atlas A2 训练/推理系列产品，单卡多进程场景建议配置 `device_port` 字段（rank table）或上述端口范围环境变量；原文明确指出"多进程会对资源开销、通信性能产生一定的影响"。

---

## 【表格解读】

**原文无传统意义上的参数表/环境变量表/硬件支持表**。原文中所有 `| --- | --- |` 包裹的区域均为**代码示例展示框**（非数据表格），其中包含的 shell 命令与 C/C++ 代码片段已在前文【技术要点】与【使用方法】中逐条引用，故此处不重复渲染。

---

## 【公式解读】

原文无数学公式或伪代码公式。涉及"优先级排序"的描述（网卡选择顺序）以纯文字+分隔符 `>` 表达，已在【关键机制与数据】中按原文逐字保留。

---

## 【关联】

原文页面内链（均位于站点 `www.hiascend.com`，URL 版本线索 900）：

| 原文锚文本 | 链接 | 关联内容 |
| --- | --- | --- |
| 集群信息配置 | `hcclug_000063.html` | rank table 文件的配置方法（基于 rank table 建域的前置） |
| `HcclCommInitClusterInfo` | `hcclcpp_07_0003.html` | 基于 rank table 建域的核心接口 |
| `HcclCommInitClusterInfoConfig` | `hcclcpp_07_0004.html` | 带配置的 rank table 建域接口 |
| `HCCL_IF_IP` | `hcclenvref_07_0018.html` | Host 侧通信 IP 环境变量 |
| `HCCL_SOCKET_IFNAME` | `hcclenvref_07_0022.html` | 通信网卡名环境变量 |
| `HCCL_SOCKET_FAMILY` | `hcclenvref_07_0023.html` | 网卡协议族环境变量（AF_INET/AF_INET6） |
| `HcclGetRootInfo` | `hcclcpp_07_0005.html` | root 节点生成 rootInfo 接口 |
| `HcclCommInitRootInfo` | `hcclcpp_07_0006.html` | 基于 rootInfo 建域接口 |
| `HcclCommInitRootInfoConfig` | `hcclcpp_07_0007.html` | 基于 rootInfo 带配置建域接口 |
| `HCCL_HOST_SOCKET_PORT_RANGE` | `hcclenvref_07_0020.html` | Host 侧端口范围环境变量 |
| `HCCL_NPU_SOCKET_PORT_RANGE` | `hcclenvref_07_0021.html` | NPU 侧端口范围环境变量 |
| `HCCL_CONNECT_TIMEOUT` | `hcclenvref_07_0002.html` | 建链超时等待时间，默认 120s |
| `HcclCommInitAll` | `hcclcpp_07_0009.html` | 单机批量建域接口 |
| `HcclCreateSubCommConfig` | `hcclcpp_07_0019.html` | 子通信域切分接口 |
| `HcclCommDestroy` | `hcclcpp_07_0010.html` | 销毁通信域接口 |
| 父主题：使用通信库 API 实现通信功能 | `hcclug_000006.html` | 本页所属上级章节 |

知识脉络：本文档作为 HCCL 通信域管理的总览入口，向下细分为三类子页（`hcclcpp_07_xxx` 系列接口详情）、环境变量参考（`hcclenvref_07_xxx`）与配置文件参考（`hcclug_000063` 集群信息配置），形成"接口—环境变量—配置文件"三足互链的知识结构。

---

## 【使用方法】

### 1. 基于 rank table 建域（C/C++ 代码片段，原文）

```c
int devId = 0;
char* rankTableFile = "/home/rank_table.json";
HcclComm hcclComm;
HcclCommInitClusterInfo(rankTableFile, devId, &hcclComm);
/*  集合通信操作   */
HcclCommDestroy(hcclComm);
```

> 注意（原文）：单卡多进程场景下，应在 rank table 配置文件中配置 `device_port` 字段，并为不同业务进程设置不同端口号（适用于 Atlas 350 / Atlas A3 / Atlas A2 系列）。

### 2. 基于 root 节点信息建域：Host 侧通信 IP 指定（原文 shell）

```bash
export HCCL_IF_IP=10.10.10.1
```

### 3. 基于 root 节点信息建域：网卡名 + 协议族指定（原文 shell）

```bash
# IPv4
export HCCL_SOCKET_FAMILY=AF_INET

# 精确匹配：使用 eth0 或 enp0
export HCCL_SOCKET_IFNAME==eth0,enp0
# 排除匹配：不使用 eth0 与 enp0
export HCCL_SOCKET_IFNAME=^=eth0,enp0

# 模糊匹配：使用所有以 eth 或 enp 为前缀的网卡
export HCCL_SOCKET_IFNAME=eth,enp
# 排除匹配：不使用任何以 eth 或 enp 为前缀的网卡
export HCCL_SOCKET_IFNAME=^eth,enp
```

### 4. 单卡多进程端口范围配置（原文 shell）

```bash
export HCCL_HOST_SOCKET_PORT_RANGE="auto"
export HCCL_NPU_SOCKET_PORT_RANGE="auto"
```

### 5. 单机批量建域 + 多线程集合通信（C/C++ 代码片段，原文）

```c
uint32_t ndev = 8;
int32_t devices[8] = {0, 1, 2, 3, 4, 5, 6, 7};
HcclComm comms[ndev];
HcclCommInitAll(ndev, devices, comms);

std::vector<std::unique_ptr<std::thread>> threads(ndev);
struct ThreadContext args[ndev];
for (uint32_t i = 0; i < ndev; i++) {
    args[i].device = i;
    args[i].comm = comms[i];
    /*  集合通信操作   */
}
for (uint32_t i = 0; i < ndev; i++) {
    HcclCommDestroy(comms[i]);
}
```

> Device ID 是逻辑 ID，可通过 `npu-smi info -m` 查询（原文）；建链超时通过 `HCCL_CONNECT_TIMEOUT` 调整，默认 120s。

### 6. 子通信域切分（C/C++ 代码片段，原文）

```c
HcclComm globalHcclComm;
HcclCommInitClusterInfo(rankTableFile, devId, &globalHcclComm);

HcclCommConfig config;
HcclCommConfigInit(&config);
config.hcclBufferSize = 50;
strcpy(config.hcclCommName, "comm_1");

HcclComm hcclComm;
uint32_t rankIds[4] = {0, 1, 2, 3};   // 子通信域的 Rank 列表
HcclCreateSubCommConfig(&globalHcclComm, 4, rankIds, 1, devId, &config, &hcclComm);
```

> 不支持嵌套切分（原文）。

### 7. Device 列表查询（原文命令）

```bash
npu-smi info -m
```
