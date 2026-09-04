# 通信域管理

通信域是集合通信算子执行的上下文，管理对应的通信对象（例如一个NPU就是一个通信对象）和通信所需的资源。通信域中的每个通信对象称为一个rank，每个rank都会分配一个介于0~n-1（n为NPU的数量）的唯一标识。

通信域创建根据用户场景的不同主要有以下几种方式：

* 多机集合通信场景
  + 如果有完整的描述集群信息的rank table文件，可通过HcclCommInitClusterInfo接口创建通信域，或者通过HcclCommInitClusterInfoConfig接口创建具有特定配置的通信域。
  + 如果无完整的rank table文件，可通过HcclGetRootInfo接口与HcclCommInitRootInfo/HcclCommInitRootInfoConfig接口配合使用，基于root节点信息创建通信域。
* 单机集合通信场景，可通过HcclCommInitAll接口在单机内批量创建通信域。
* 基于已有的通信域，可通过HcclCreateSubCommConfig接口切分具有特定配置的子通信域。

![](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/public_sys-resources/notice_3.0-zh-cn.png) 

* 多个通信域下的所有通信算子在每个Device上需要保证串行下发，不允许乱序、多线程并发下发，也不支持线程重入。
* 在同一Device上，同一通信域内的所有通信算子的下发线程需要使用相同的Context。
* 同一个通信域内不支持图模式通信和单算子通信混合执行。
* 同一个通信域内的算子需要由使用者确保串行执行。
* 同一个NPU上需要串行创建多个通信域。
* 针对Atlas A3 训练系列产品/Atlas A3 推理系列产品，通信域初始化时，如果组网中存在多个超节点，请将属于同一超节点内的AI Server信息配置在一起。假设有两个超节点，标识分别为“0”和“1”，请先配置“0”中的AI Server信息，再配置“1”中的AI Server信息，不支持“0”中的AI Server信息与“1”中的AI Server信息交叉配置。

#### 基于rank table创建通信域

多机集合通信、基于集群信息配置文件（rank table文件）创建通信域的场景，每张卡需要使用一个单独的进程参考如下流程创建通信域：

1. 构造rank table文件（rank table文件的配置可参见[集群信息配置](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000063.html)）。
2. 每张卡分别调用[HcclCommInitClusterInfo](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0003.html)接口创建通信域，或者调用[HcclCommInitClusterInfoConfig](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0004.html)接口创建具有特定配置的通信域。

一个简单的代码示例片段如下：

|  |  |
| --- | --- |
| ```  1  2  3  4  5  6  7  8  9 10 11 12 ``` | ```     int devId = 0;     // 配置rank table文件路径     char* rankTableFile = "/home/rank_table.json";     // 定义通信域句柄     HcclComm hcclComm;     // 初始化HCCL通信域     HcclCommInitClusterInfo(rankTableFile, devId, &hcclComm);         /*  集合通信操作   */      // 销毁HCCL通信域     HcclCommDestroy(hcclComm); ``` |

![](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/public_sys-resources/note_3.0-zh-cn.png) 

针对Atlas 350 加速卡，Atlas A3 训练系列产品/Atlas A3 推理系列产品，Atlas A2 训练系列产品/Atlas A2 推理系列产品，若业务为单卡多进程场景，建议在rank table配置文件中配置“device\_port”字段，并且不同的业务进程需要设置不同的端口号，否则业务可能会因为端口冲突运行失败。但需要注意，多进程会对资源开销、通信性能产生一定的影响。

#### 基于root节点信息创建通信域

多机集合通信场景，若无完整的集群信息配置文件（rank table文件），HCCL提供了基于root节点信息创建通信域的方式，**主要有如下两种典型使用场景**：

* 每个Device对应一个业务进程的场景，实现流程如下所示：
  1. 针对Atlas 350 加速卡，检查rootinfo文件是否存在，其他产品跳过此步骤。

     基于root节点信息创建通信域前，请检查“/etc/hccl\_rootInfo.json”文件是否存在，此文件记录了NPU间通信的EID（Entity ID，通信中发起或接收对象的标识）信息，环境部署完成后自动生成。若无此文件，请单击[Link](https://www.hiascend.com/support)联系技术支持。
  2. 指定HCCL初始化时Host节点使用的通信IP地址或通信网卡（可选）。
     + 方式一：在每个Host节点通过环境变量[HCCL\_IF\_IP](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclenvref_07_0018.html)配置通信IP地址，该IP地址用于与root节点通信，可以是IPv4或IPv6格式，仅支持配置一个IP地址。配置示例如下：

       |  |  |
       | --- | --- |
       | ``` 1 ``` | ``` export HCCL_IF_IP=10.10.10.1 ``` |
     + 方式二：在每个Host节点通过环境变量[HCCL\_SOCKET\_IFNAME](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclenvref_07_0022.html)配置通信网卡名，通过[HCCL\_SOCKET\_FAMILY](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclenvref_07_0023.html)配置网卡使用的通信协议，HCCL将通过该网卡名获取Host IP，与root节点通信。配置示例如下：

       |  |  |
       | --- | --- |
       | ```  1  2  3  4  5  6  7  8  9 10 11 ``` | ``` # 配置HCCL初始化时通信网卡使用的IP协议版本，AF_INET：IPv4；AF_INET6：IPv6 export HCCL_SOCKET_FAMILY=AF_INET  # 支持以下格式的网卡名配置（4种规格自行选择1种即可，环境变量中可配置多个网卡，多个网卡间使用英文逗号分隔，取最先匹配到的网卡作为通信网卡） # 精确匹配网卡 export HCCL_SOCKET_IFNAME==eth0,enp0   # 使用指定的eth0或enp0网卡 export HCCL_SOCKET_IFNAME=^=eth0,enp0     # 不使用eth0与enp0网卡  # 模糊匹配网卡 export HCCL_SOCKET_IFNAME=eth,enp       # 使用所有以eth或enp为前缀的网卡 export HCCL_SOCKET_IFNAME=^eth,enp      # 不使用任何以eth或enp为前缀的网卡 ``` |

     环境变量HCCL\_IF\_IP的优先级高于HCCL\_SOCKET\_IFNAME。如果不配置HCCL\_IF\_IP或HCCL\_SOCKET\_IFNAME，系统将按照如下优先级自动选择网卡。若当前节点选择的网卡与root节点选择的网卡链路不通，将导致HCCL建链失败。

     ```
     docker/lo以外网卡(网卡名称的字典序升序) > docker 网卡 > lo网卡
     ```
  3. 在root节点调用[HcclGetRootInfo](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0005.html)接口，生成root节点rank标识信息“rootInfo”，包括device ip、device id等信息。
  4. 将root节点的rank信息广播至通信域中的所有rank。
  5. 在通信域中所有节点调用[HcclCommInitRootInfo](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0006.html)或者[HcclCommInitRootInfoConfig](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0007.html)接口（创建具有特定配置的通信域），基于接收到的“rootInfo”，以及本rank的rank id等信息，进行通信域初始化。
* 每个AI Server对应一个业务进程，每个线程对应一个Device，通过多线程的方式创建多个通信域的场景，实现流程如下所示：
  1. 针对Atlas 350 加速卡，检查rootinfo文件是否存在，其他产品跳过此步骤。

     基于root节点信息创建通信域前，请检查“/etc/hccl\_rootInfo.json”文件是否存在，此文件记录了NPU间通信的EID（Entity ID，通信中发起或接收对象的标识）信息，环境部署完成后自动生成。若无此文件，请单击[Link](https://www.hiascend.com/support)联系技术支持。
  2. 参见[2](#ZH-CN_TOPIC_0000002562460885__li33217719216)，指定HCCL初始化时Host节点使用的通信IP地址或通信网卡（可选）。
  3. 在主进程中循环执行“指定不同的Device + 调用HcclGetRootInfo接口”，获取多个“rootInfo”信息。
  4. 每个Device匹配一个线程，分别根据不同的“rootInfo”信息，并发调用[HcclCommInitRootInfo](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0006.html)或者[HcclCommInitRootInfoConfig](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0007.html)接口，进行通信域初始化。

![](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/public_sys-resources/note_3.0-zh-cn.png) 

针对Atlas 350 加速卡，Atlas A3 训练系列产品/Atlas A3 推理系列产品，Atlas A2 训练系列产品/Atlas A2 推理系列产品，若业务为单卡多进程场景，建议通过环境变量“[HCCL\_HOST\_SOCKET\_PORT\_RANGE](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclenvref_07_0020.html)”与“[HCCL\_NPU\_SOCKET\_PORT\_RANGE](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclenvref_07_0021.html)”分别配置HCCL在Host侧与NPU侧使用的通信端口，否则可能会导致端口冲突，配置示例如下所示。但需要注意，多进程会对资源开销、通信性能产生一定的影响。

```
export HCCL_HOST_SOCKET_PORT_RANGE="auto"
export HCCL_NPU_SOCKET_PORT_RANGE="auto"
```

#### 单机内批量创建通信域

单机通信场景中，开发者可通过一个进程统一创建多张卡的通信域，其中一张卡对应一个线程，创建流程如下：

1. 构造通信域中的Device列表，例如：{0, 1, 2, 3, 4, 5, 6, 7}，其中列表中的Device ID是逻辑ID（可通过**npu-smi info -m**命令查询），HCCL会按照列表中设置的顺序创建通信域。
2. 在进程中调用[HcclCommInitAll](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0009.html)接口创建通信域。

|  |  |
| --- | --- |
| ```  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 ``` | ```     uint32_t ndev = 8;     // 构造Device的逻辑ID列表     int32_t devices[8] = {0, 1, 2, 3, 4, 5, 6, 7};     // 定义通信域句柄     HcclComm comms[ndev];     // 初始化HCCL通信域     HcclCommInitAll(ndev, devices, comms);      // 启动线程执行集合通信操作     std::vector<std::unique_ptr<std::thread> > threads(ndev);     struct ThreadContext args[ndev];     for (uint32_t i = 0; i < ndev; i++) {         args[i].device = i;         args[i].comm = comms[i];        /*  集合通信操作   */           }      // 销毁HCCL通信域     for (uint32_t i = 0; i < ndev; i++) {         HcclCommDestroy(comms[i]);     } ``` |

需要注意，多线程调用集合通信操作API时（例如HcclAllReduce），需要确保不同线程中调用集合通信操作API的前后时间差不超过集合通信的建链超时等待时间（可通过环境变量[HCCL\_CONNECT\_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclenvref_07_0002.html)设置，默认120s），避免建链超时。

#### 基于已有通信域切分子通信域

HCCL提供了[HcclCreateSubCommConfig](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0019.html)接口，实现基于已有通信域切分具有特定配置的子通信域的功能。该子通信域创建方式无需进行socket建链与rank信息交换，可应用于业务故障下的快速通信域创建。

|  |  |
| --- | --- |
| ```  1  2  3  4  5  6  7  8  9 10 11 12 ``` | ``` // 初始化全局通信域 HcclComm globalHcclComm; HcclCommInitClusterInfo(rankTableFile, devId, &globalHcclComm); // 通信域配置 HcclCommConfig config; HcclCommConfigInit(&config); config.hcclBufferSize = 50; strcpy(config.hcclCommName, "comm_1"); // 初始化子通信域 HcclComm hcclComm; uint32_t rankIds[4] = {0, 1, 2, 3};  // 子通信域的 Rank 列表 HcclCreateSubCommConfig(&globalHcclComm, 4, rankIds, 1, devId, &config, &hcclComm); ``` |

![](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/public_sys-resources/notice_3.0-zh-cn.png) 

该接口不支持通信域的嵌套切分，即不支持在子通信域中进一步切分子通信域。

#### 销毁通信域

集合通信操作完成后，需要调用[HcclCommDestroy](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclcpp_07_0010.html)接口销毁指定的通信域，并调用运行时管理接口释放通信所用的内存、Stream、Device资源。

**父主题：** [使用通信库API实现通信功能](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000006.html)