# 环境变量列表

本手册描述开发者基于CANN构建AI应用和业务过程中可使用的环境变量。

![](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/public_sys-resources/caution_3.0-zh-cn.png) 

* 环境变量支持通过命令、接口、配置等方式实现，包括export命令、putenv/getenv/setenv/unsetenv/clearenv函数、os.environ、os.getenv等。建议用户在应用进程拉起前设置环境变量，否则可能引起环境变量访问冲突，导致程序异常。
* 本手册不包含Ascend Extension for PyTorch的环境变量，关于Ascend Extension for PyTorch环境变量的详细介绍请参见《[Ascend Extension for PyTorch 环境变量参考](https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/env_variable_list.md)》。

#### 安装配置相关

| 环境变量 | 简介 |
| --- | --- |
| [ASCEND\_CACHE\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0006.html) | 若开发者期望编译运行过程中产生的文件落盘到归一路径，可通过此环境变量设置**共享文件**的存储路径，各组件编译运行过程中产生的可共享文件会存储到此环境变量定义的路径中。 |
| [ASCEND\_WORK\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0007.html) | 若开发者期望编译运行过程中产生的文件落盘到归一路径，可通过此环境变量设置**单机独享文件**的存储路径，各组件编译运行过程中产生的单机独享文件会存储到此环境变量定义的路径中。 |
| [ASCEND\_CUSTOM\_OPP\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0147.html) | 用户自定义算子包安装路径。开发者编译生成的自定义算子包需要安装到指定路径下时，需要配置该路径。 |

#### 图编译

| 环境变量 | 简介 |
| --- | --- |
| [DUMP\_GE\_GRAPH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0011.html) | 把整个流程中各个阶段的图描述信息打印到文件中，此环境变量控制dump图的内容多少。 |
| [DUMP\_GRAPH\_LEVEL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0012.html) | 把整个图编译流程中各个阶段的图描述信息打印到文件中。 |
| [DUMP\_GRAPH\_FORMAT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0155.html) | 控制需要生成的dump文件类型。 |
| [DUMP\_GRAPH\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0013.html) | 指定DUMP图文件的保存路径，可配置为绝对路径或脚本执行目录的相对路径。 |
| [OP\_NO\_REUSE\_MEM](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0014.html) | 计算图在昇腾平台编译的过程中默认采用内存复用形式，在问题定位场景中，如果开发者怀疑是内存复用错误导致计算结果异常，可通过此环境变量指定为某算子单独分配内存。 |
| [ASCEND\_ENGINE\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0015.html) | 单算子JSON文件转换成离线模型场景，如果希望模型转换时只使用TBE算子（不查找AI CPU算子，找不到TBE算子则报错），则需要使用该环境变量。 |
| [MAX\_COMPILE\_CORE\_NUMBER](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0016.html) | 此环境变量用于指定图编译时可用的CPU核数。 |
| [MULTI\_THREAD\_COMPILE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0017.html) | 此环境变量用于控制模型转换时是否使用单线程编译。 |
| [ENABLE\_NETWORK\_ANALYSIS\_DEBUG](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0018.html) | TensorFlow训练场景下，计算图编译失败时默认会终止训练流程，不会继续向Device下发剩余的图。若开发者希望图编译失败时，不终止训练流程，允许TF Adapter持续向Device下发计算图，可通过设置该环境变量实现。 |

#### 算子编译

| 环境变量 | 简介 |
| --- | --- |
| [TE\_PARALLEL\_COMPILER](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0020.html) | 网络模型较大时，可通过配置此环境变量开启算子的并行编译功能。 |
| [ASCEND\_MAX\_OP\_CACHE\_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0021.html) | 启用算子编译缓存功能时，可通过此环境变量限制某个AI处理器下缓存文件夹的磁盘空间的大小。 |
| [ASCEND\_REMAIN\_CACHE\_SIZE\_RATIO](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0022.html) | 启用算子编译缓存功能时，当编译缓存空间大小达到ASCEND\_MAX\_OP\_CACHE\_SIZE而需要删除旧的kernel文件时，系统需要保留缓存的空间大小比例，默认为50，单位为百分比。 |
| [IGNORE\_INFER\_ERROR](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0142.html) | 算子入图时，跳过算子原型交付件校验的开关。交付件包括shape推导等算子入图适配函数的实现。 |

#### 资源配置

| 环境变量 | 简介 |
| --- | --- |
| [ASCEND\_DEVICE\_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0027.html) | 指定当前进程所用的AI处理器的逻辑ID。 |
| [ASCEND\_RT\_VISIBLE\_DEVICES](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0028.html) | 指定哪些Device对当前进程可见，支持一次指定一个或多个Device ID。通过该环境变量，可实现不修改应用程序即可调整所用Device的功能。 |
| [AUTO\_USE\_UC\_MEMORY](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0029.html) | 控制系统是否允许算子搬移数据不经过L2 Cache的功能。 |
| [RESOURCE\_CONFIG\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0133.html) | 用于设置配置异构资源描述信息文件的存储路径。 |

#### 算子执行

| 环境变量 | 简介 |
| --- | --- |
| [ACLNN\_CACHE\_LIMIT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0031.html) | 此环境变量用于配置aclnn API在Host侧缓存的算子信息条目个数。缓存的算子信息包含workspace大小、算子计算的执行器、Tiling信息等。 |

#### 图执行

| 环境变量 | 简介 |
| --- | --- |
| [ENABLE\_DYNAMIC\_SHAPE\_MULTI\_STREAM](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0033.html) | 计算图执行时，开启多流并发执行功能在一定场景下可提升网络性能。当前多流并发执行功能默认关闭，动态shape图模式场景下，若开发者想开启多流并发执行功能，可通过此环境变量开启。 |
| [MAX\_RUNTIME\_CORE\_NUMBER](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0034.html) | 训练与在线推理场景下，针对动态shape图模式执行的网络，可通过设置此环境变量开启图执行器（Host侧）的多线程任务调度。 |

#### TFAdapter

| 环境变量 | 简介 |
| --- | --- |
| [JOB\_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0036.html) | TensorFlow训练与在线推理场景下，可通过此环境变量自定义任务ID。 |
| [ENABLE\_FORCE\_V2\_CONTROL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0037.html) | TensorFlow 1.15训练场景下，如果输入是动态shape，由于tf.case/tf.cond/tf.while\_loop这些API对应TensorFlow V1版本的控制流算子（例如Switch、Merge、Enter、LoopCond、NextIteration、Exit、ControlTrigger等）不支持动态shape，仅TensorFlow V2版本的控制流算子（例如If、Case、While、For、PartitionedCall等）支持动态shape，因此，如果用户的训练脚本中使用了这些API，需要将V1版本的控制流算子转换为V2版本，用于支持动态shape功能。另外，如果网络中的分支结构较多，采用V1版本的控制流算子可能导致流数超限，此时也需要将V1版本的控制流算子转换成V2版本算子解决。 |
| [ENABLE\_HF32\_EXECUTION](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0038.html) | 针对TensorFlow 1.15网络，是否启用HF32自动代替FP32数据类型的功能，当前版本此环境变量仅针对Conv类算子与Matmul类算子生效。 |
| [NPU\_DEBUG](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0039.html) | TensorFlow 2.6.5训练与在线推理场景下，用于开启TF Adapter的Debug级别执行日志。 |
| [NPU\_DUMP\_GRAPH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0040.html) | TensorFlow 2.6.5训练与在线推理场景下，用于开启TF Adapter图Dump功能。 |
| [NPU\_ENABLE\_PERF](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0041.html) | TensorFlow 2.6.5训练与在线推理场景下，用于开启TF Adapter图耗时打印功能。 |
| [NPU\_LOOP\_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0042.html) | TensorFlow 2.6.5训练与在线推理场景下，用于设置NPU上循环下沉的次数。 |
| [STEP\_NOW](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0043.html) | TensorFlow 1.15训练场景下，若通过“experimental\_accelerate\_train\_mode”参数或者“accelerate\_train\_mode”参数触发了训练加速功能，可通过此环境变量设置NPU上当前的执行步数。 |
| [TOTAL\_STEP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0044.html) | TensorFlow 1.15训练场景下，若通过“experimental\_accelerate\_train\_mode”参数或者“accelerate\_train\_mode”参数触发了训练加速功能，可通过此环境变量设置NPU上总训练步数。 |
| [LOSS\_NOW](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0045.html) | TensorFlow 1.15训练场景下，若通过“experimental\_accelerate\_train\_mode”参数或者“accelerate\_train\_mode”参数触发了训练加速功能，可通过此环境变量设置NPU上当前迭代的loss值。 |
| [TARGET\_LOSS](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0046.html) | TensorFlow 1.15训练场景下，若通过“experimental\_accelerate\_train\_mode”参数或者“accelerate\_train\_mode”参数触发了训练加速功能，可通过此环境变量设置NPU上的目标训练loss值。 |
| [RANK\_TABLE\_FILE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0047.html) | TensorFlow分布式训练或推理场景下，通过此环境变量指定参与集合通信的AI处理器的rank table资源配置文件，包含rank table文件路径和文件名。 |
| [RANK\_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0048.html) | TensorFlow分布式训练或推理场景下，通过此环境变量指定当前进程在集合通信进程组中对应的rank标识。 |
| [RANK\_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0049.html) | TensorFlow分布式训练或推理场景下，通过此环境变量指定当前训练进程对应的Device数量。 |
| [CM\_CHIEF\_IP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0050.html) | TensorFlow分布式训练场景下，用户可以选择不使用rank table文件，通过组合使用环境变量的方式自动生成资源信息，完成集合通信初始化。  本环境变量用于配置Master节点的监听Host IP。 |
| [CM\_CHIEF\_PORT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0051.html) | 本环境变量用于配置Master节点的监听端口。 |
| [CM\_CHIEF\_DEVICE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0052.html) | 本环境变量用于指定Master节点中统计Server端集群信息的Device逻辑ID。 |
| [CM\_WORKER\_SIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0053.html) | 本环境变量用于配置本次业务通信域Device的数量。 |
| [CM\_WORKER\_IP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0054.html) | 本环境变量用于配置当前Device和Master节点进行信息交换时所用的网卡IP。 |

#### 集合通信

| 环境变量 | 简介 |
| --- | --- |
| **功能相关** | |
| [HCCL\_CONNECT\_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0077.html) | 分布式训练或推理场景下，用于限制不同设备之间socket建链过程的超时等待时间。不同设备进程在集合通信初始化之前由于其他因素会导致执行不同步。该环境变量控制设备间的建链超时等待时间，在该配置时间内各设备进程等待其他设备建链同步。 |
| [HCCL\_EXEC\_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0078.html) | 不同设备进程在分布式训练或推理过程中存在卡间执行任务不一致的场景（如仅特定进程会保存checkpoint数据），通过该环境变量可控制设备间执行时同步等待的时间，在该配置时间内各设备进程等待其他设备执行通信同步。 |
| [HCCL\_ALGO](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0079.html) | 此环境变量用于配置集合通信Server间通信算法以及超节点间通信算法，支持全局配置算法类型与按算子配置算法类型两种配置方式。 |
| [HCCL\_BUFFSIZE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0080.html) | 此环境变量用于控制通信域所使用的共享数据缓存区大小。需要配置为整数，取值大于等于1，默认值为200，单位MB。 |
| [HCCL\_INTRA\_PCIE\_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0081.html) | 用于配置Server内是否使用PCIe链路进行通信。 |
| [HCCL\_INTRA\_ROCE\_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0082.html) | 用于配置Server内或超节点内是否使用RoCE链路进行通信。 |
| [HCCL\_INTER\_HCCS\_DISABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0083.html) | 此环境变量用于配置超节点模式组网中超节点内的通信链路类型，支持如下取值： |
| [HCCL\_OP\_EXPANSION\_MODE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0096.html) | 该环境变量用于配置通信算子的展开模式。 |
| [HCCL\_DETERMINISTIC](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0099.html) | 此环境变量用于配置是否开启归约类通信算子的确定性计算或保序功能，其中归约类通信算子包括AllReduce、ReduceScatter、ReduceScatterV、Reduce，归约保序是指严格的确定性计算，在确定性的基础上保证归约顺序一致。 |
| [HCCL\_LOGIC\_SUPERPOD\_ID](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0100.html) | 针对 Atlas A3 训练系列产品 / Atlas A3 推理系列产品 的超节点模式组网，若不使用rank table文件配置集群资源信息，可通过此环境变量指定当前节点运行进程所属的超节点ID，实现将一个物理超节点划分为多个逻辑超节点的功能。 |
| **性能相关** | |
| [HCCL\_RDMA\_PCIE\_DIRECT\_POST\_NOSTRICT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0093.html) | 多机通信且Host操作系统小页内存页表大小非4KB的场景，当通信算子下发性能Host Bound时，开发者可设置此环境变量，通过PCIe Direct的方式提交RDMA任务，提升通信算子下发性能。 |
| [HCCL\_RDMA\_QPS\_PER\_CONNECTION](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0094.html) | 两个rank之间RDMA通信时会默认创建1个QP（Queue Pair）进行数据传输，若开发者想让两个rank之间的RDMA通信使用多个QP，可通过此环境变量实现。 |
| [HCCL\_RDMA\_QP\_PORT\_CONFIG\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0141.html) | 两个rank之间RDMA通信时会默认创建1个QP（Queue Pair）进行数据传输，若开发者想让两个rank之间的RDMA通信使用多个QP，并指定多QP通信时使用的源端口号，可通过此环境变量实现。 |
| [HCCL\_MULTI\_QP\_THRESHOLD](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0095.html) | rank间RDMA通信使用多QP通信的场景下，开发者可通过本环境变量设置每个QP分担数据量的最小阈值。 |
| **网络相关** | |
| [HCCL\_IF\_IP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0073.html) | 当通信域的创建方式为“[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)”时，可通过此环境变量配置HCCL初始化时Host使用的通信IP地址。此IP地址用于与root节点通信，以完成通信域的创建**。** |
| [HCCL\_IF\_BASE\_PORT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0074.html) | 当通信域的创建方式为“[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)”时，可以通过该环境变量指定Host网卡起始端口号，配置后系统默认占用以该端口起始的32个端口进行集群信息收集。 |
| [HCCL\_HOST\_SOCKET\_PORT\_RANGE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0143.html) | 当通信域的创建方式为“[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)”时，开发者可通过此环境变量配置HCCL在Host侧使用的通信端口。 |
| [HCCL\_NPU\_SOCKET\_PORT\_RANGE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0144.html) | 当通信域的创建方式为“[基于root节点信息创建](https://www.hiascend.com/document/detail/zh/canncommercial/900/API/hcclug/hcclug_000008.html#ZH-CN_TOPIC_0000002562460885__section1539155710538)”时，开发者可通过此环境变量配置HCCL在NPU侧使用的通信端口。 |
| [HCCL\_SOCKET\_IFNAME](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0075.html) | 配置HCCL初始化时Host使用的通信网卡名，HCCL将通过该网卡名获取Host IP，与root节点通信，以完成通信域的创建**。** |
| [HCCL\_SOCKET\_FAMILY](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0076.html) | 该环境变量指定通信网卡使用的IP协议。 |
| [HCCL\_RDMA\_TC](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0089.html) | 用于配置RDMA网卡的traffic class。 |
| [HCCL\_RDMA\_SL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0090.html) | 用于配置RDMA网卡的service level，该值需要和网卡配置的PFC优先级保持一致，若配置不一致可能导致性能劣化。 |
| [HCCL\_RDMA\_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0091.html) | 用于配置RDMA网卡重传超时时间的系数timeout。 |
| [HCCL\_RDMA\_RETRY\_CNT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0092.html) | 用于配置RDMA网卡的重传次数，需要配置为整数，取值范围为[1,7]，默认值为7。 |
| **调试相关** | |
| [HCCL\_DIAGNOSE\_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0087.html) | 此环境变量用于配置集合通信是否缓存部分任务的详细信息，以便任务执行失败时，打印详细日志，用于问题定位。 |
| [HCCL\_ENTRY\_LOG\_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0088.html) | 此环境变量用于控制是否实时打印通信算子的调用行为日志。 |
| [HCCL\_DEBUG\_CONFIG](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0145.html) | 启用此环境变量后，运行日志（即“$HOME/ascend/log/run”目录下的日志）将包含HCCL特定子模块的详细运行信息。目前支持ALG或alg（算法编排模块）、TASK或task（任务编排模块）、RESOURCE或resource（资源管理模块，包括资源的申请和释放操作）几个配置项。 |
| [HCCL\_DFS\_CONFIG](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0162.html) | 该环境变量支持以下配置项： |
| **可靠性相关** | |
| [HCCL\_OP\_RETRY\_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0085.html) | 此环境变量用于配置是否开启HCCL算子的重执行特性。HCCL算子重执行以**通信域**为粒度，当通信算子执行报 SDMA 或者RDMA CQE类型的错误时，HCCL会尝试重新执行此通信算子。 |
| [HCCL\_OP\_RETRY\_PARAMS](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0086.html) | 此环境变量用于配置是否开启HCCL算子的重执行特性。HCCL算子重执行以**通信域**为粒度，当通信算子执行报 SDMA 或者RDMA CQE类型的错误时，HCCL会尝试重新执行此通信算子。 |
| **安全相关** | |
| [HCCL\_WHITELIST\_DISABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0156.html) | 配置在使用HCCL时是否开启通信白名单。 |
| [HCCL\_WHITELIST\_FILE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0157.html) | 当通过HCCL\_WHITELIST\_DISABLE开启了通信白名单校验功能时，需要通过此环境变量配置指向HCCL通信白名单配置文件的路径，只有在通信白名单中的IP地址才允许进行集合通信。 |

#### AOE调优

| 环境变量 | 简介 |
| --- | --- |
| [TUNE\_BANK\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0104.html) | 可通过此环境变量指定调优后自定义知识库的存储路径。 |
| [REPEAT\_TUNE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0105.html) | 是否重新发起调优，此环境变量在开启子图调优或算子调优的场景下生效。 |
| [AOE\_MODE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0106.html) | 在线推理与训练场景下，可通过此环境变量指定AOE调优模式。 |

#### AMCT模型压缩

| 环境变量 | 简介 |
| --- | --- |
| [AMCT\_LOG\_FILE\_LEVEL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0109.html) | 控制日志文件（PyTorch框架：amct\_pytorch.log；Caffe框架：amct\_caffe.log；ONNX：amct\_onnx.log）的信息级别以及生成精度仿真模型时，对应量化层生成的日志文件信息级别。 |
| [AMCT\_LOG\_LEVEL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0110.html) | 控制屏幕输出的信息级别。该环境变量仅适用于PyTorch框架、Caffe框架、ONNX网络模型的量化。 |
| [DUMP\_AMCT\_RECORD](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0111.html) | 控制是否生成权重和数据的量化因子。该环境变量仅适用于MindSpore框架的模型压缩。 |
| [AMCT\_LOG\_DUMP](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0112.html) | 控制训练后量化过程中日志落盘等信息的环境变量。该环境变量仅适用于调用aclgrphCalibration接口进行的量化。 |

#### 性能数据采集

| 环境变量 | 简介 |
| --- | --- |
| [PROFILING\_MODE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0115.html) | 该环境变量用于控制是否开启Profiling功能。 |
| [PROFILING\_OPTIONS](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0116.html) | 训练或在线推理场景下，开发者可通过PROFILING\_OPTIONS环境变量配置Profiling配置选项。 |

#### 日志

| 环境变量 | 简介 |
| --- | --- |
| [ASCEND\_PROCESS\_LOG\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0120.html) | 设置日志落盘路径。 |
| [ASCEND\_SLOG\_PRINT\_TO\_STDOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0121.html) | 是否开启日志打印。开启后，日志将不会保存在log文件中，而是将产生的日志直接打印显示。 |
| [ASCEND\_GLOBAL\_LOG\_LEVEL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0122.html) | 设置应用类日志的日志级别及各模块日志级别，仅支持调试日志。 |
| [ASCEND\_MODULE\_LOG\_LEVEL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0123.html) | 设置应用类日志的各模块日志级别，仅支持调试日志。 |
| [ASCEND\_GLOBAL\_EVENT\_ENABLE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0124.html) | 设置应用类日志是否开启Event日志。 |
| [ASCEND\_LOG\_DEVICE\_FLUSH\_TIMEOUT](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0125.html) | 指定Device侧应用类日志回传到Host侧的延时时间。 |
| [ASCEND\_HOST\_LOG\_FILE\_NUM](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0126.html) | Ascend EP 场景下，设置应用类日志目录（plog和device-*id*）下存储每个进程日志文件的数量。 |
| [ASCEND\_COREDUMP\_SIGNAL](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0127.html) | 设置trace处理的core dump信号量。 |
| [ASCEND\_LOG\_SYNC\_SAVE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0128.html) | 指定日志拥塞处理方式。 |
| [ASCEND\_TRACE\_RECORD\_NUM](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0140.html) | 设置trace日志文件的老化规格，取值范围[10, 1000]。 |

#### 故障信息收集

| 环境变量 | 简介 |
| --- | --- |
| [NPU\_COLLECT\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0163.html) | 在复现问题场景下，使用该环境变量指定故障信息（包括dump图、AI Core算子异常数据、算子编译信息等）的保存路径，可配置为绝对路径或相对路径（此处是相对执行程序或命令的路径），执行用户需对该路径具有读、写、可执行权限，若路径不存在，系统会自动创建该路径中的目录。 |
| [ASCEND\_DUMP\_SCENE](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0164.html) | 在复现问题场景时，使用该环境变量开启异常算子Dump，导出异常算子的输入输出数据、workspace信息和Tiling信息。 |
| [ASCEND\_DUMP\_PATH](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0130.html) | 指定异常算子Dump信息的存储路径，可配置为绝对路径或执行程序的相对路径。指定的路径支持大小写字母（a-z，A-Z）、数字（0-9）、下划线（\_）、中划线（-）、句点（.）、中文字符，执行用户需具有读、写、执行权限，若路径不存在，系统会自动创建该路径中的目录。不指定路径时，异常算子Dump信息默认存放在应用程序的当前执行目录。 |

#### 后续版本废弃环境变量

| 环境变量 | 简介 |
| --- | --- |
| [GE\_USE\_STATIC\_MEMORY](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0138.html) | 此环境变量用于配置网络运行时使用的内存分配方式。 |
| [ENABLE\_ACLNN](https://www.hiascend.com/document/detail/zh/canncommercial/900/maintenref/envvar/envref_07_0139.html) | 图编译时，通过设置该环境变量，可以决定在图执行时是否调用算子注册的host执行函数来实现host执行逻辑及kernel下发。 |