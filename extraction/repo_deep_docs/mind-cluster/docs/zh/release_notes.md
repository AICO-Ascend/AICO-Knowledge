# 版本说明

> 仓 `mind-cluster` · 路径 `docs/zh/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/zh/release_notes.md

# MindCluster 26.1.0 版本说明 深度解读

## 【定位】
本文档是 MindCluster 26.1.0 Release 版本的官方 release notes,集中声明该版本与 CANN、HDK、MindSpeed-LLM、TorchNPU、MindSpore 等上下游产品的版本配套矩阵,以及集群调度组件和 Ascend FaultDiag 组件的新增/变更/修复/遗留问题与升级影响,为运维和升级决策提供唯一权威依据。

## 【技术要点】
- **产品版本**:MindCluster 26.1.0,Release 版本;26.0 系列规划为 26.0.0 / 26.1.0 / 26.2.0 / 26.3.0 共 4 个迭代。
- **核心配套栈**:CANN 9.1.0、MindSpeed-LLM 26.1.0、TorchNPU 26.1.0、MindSpore 2.10.0;HDK 按硬件细分(Atlas 350 / Atlas 950 SuperPoD / Atlas 850E & 650E / 其他)分别为 25.7.RC1 / 25.1.RC1 / 25.6.RC1 / 26.1.0。
- **兼容性策略**:MindCluster 各组件必须同版本配套使用,严禁跨版本混用;历史版本(7.3.0、26.0.0)向下兼容的最低基线为 CANN/HDK/MindSpeed-LLM/TorchNPU 的前两代 X.Y 版本与 MindSpore 2.7.2。
- **驱动等待时长变更**:启动 Ascend Device Plugin、NPU Exporter、NodeD 时,若芯片数量不足,等待驱动上报完整芯片的最大时长参数 `-deviceResetTimeout` 默认值由 **60s** 修改为 **600s**。
- **Infer Operator 权限变更**:日志权限由普通权限更新为 **root** 权限;升级到 26.1.0 及之后版本需删除并重建日志目录为 root 权限,或修改既有日志目录及文件的属主为 root。
- **运行时环境变量**:Ascend Docker Runtime 支持默认配置 HDK 驱动的 `LD_LIBRARY_PATH` 环境变量,以保障 `npu-smi` 工具正常使用。
- **遗留问题**:进程级重调度在多次恢复后存在 PyTorch gloo 段错误,概率约 **0.00125**(issue 188266);Atlas A3 系列在算子重执行 + linkdown 下进程级重调度有概率失败,两者均建议以 Job/Pod 级重调度作为兜底。

## 【关键机制与数据】
- **版本配套数据流**(原文):本文档定义了 MindCluster 作为上层集群管理平台,与底层异构计算栈(异构计算架构 CANN、硬件驱动 HDK)、训练框架(MindSpeed-LLM、TorchNPU)、AI 框架(MindSpore)的版本对齐矩阵;所有兼容性结论以"Y"或"空白"显式给出,空白代表该组合未经过验证/不可配套。
- **故障诊断数据**(原文):Ascend FaultDiag 扩充了 Ascend 950 系列的故障模式库,新增支持基于 pyMotor+vLLM 的故障模式,并扩展了链路诊断工具报告内容,诊断面已支持 IPv6 场景;其中"性能劣化功能(资源抢占/网络拥塞)采集指标"对训练与推理业务存在性能影响,将在后续版本回滚(原文"日落")。
- **集群调度新增能力数据流**(原文):覆盖存储层(DTFS 故障支持)、网络层(IPv6,Atlas 950 SuperPoD 超节点参数面除外)、调度层(Volcano Pod 优先回原节点、多级调度亚健康热切、推理优先级调度/缩 P 保 D/实例级重调度)、可观测层(NPU Exporter 分组采集周期)、可靠性层(1825 网卡带内检测与 RDMA 设备插件、Ascend Device Plugin 故障处理插件化、新增卡死检测与恢复)、部署层(helm 一键化)、探针层(新增存活探针配置);并对 Atlas 850E 超节点 / Atlas 650E 服务器 / Atlas 950 SuperPoD 超节点三类硬件同步开启设备管理、亲和性调度、指标监控、故障检测、RankTable 生成,以及基础/全量断点续训和容器化能力。
- **修复问题数据**(原文):(1) Atlas 350 加速卡驱动部署后的软链接校验报错;(2) Ascend 950 系列 huawei.com/AscendReal 注解的 phyID 与 logicID 含义不一致导致的卡占用判断异常;(3) Ascend 950 系列 device-cm ManuallySeparateNPU 未将芯片名称适配为 NPU;(4) NPU Exporter 光模块 optical_index 在采集失效时内容存在但未上报。
- **概率数据**(原文):PyTorch gloo 段错误概率 ≈ 0.00125(见 PyTorch issue 188266)。

## 【表格解读】

### 表 0 产品版本信息
| 产品名称 | 产品版本 | 版本类型 |
|--|--|--|
| MindCluster | 26.1.0 | Release版本 |

**解读**:声明本次发布的具体版本号与发行类型,所有下文兼容性矩阵与功能描述均围绕 26.1.0 这一锚点展开;附录 NOTE 进一步提示 MindCluster 26.0 路线图为四个连续版本,26.1.0 是其中第二个迭代。

### 表 1 MindCluster 软件版本配套表
| MindCluster | CANN | HDK | MindSpeed-LLM | TorchNPU | MindSpore |
|--|--|--|--|--|--|
| 26.1.0 | 9.1.0 | Atlas 350 加速卡:25.7.RC1<br>Atlas 950 SuperPoD 超节点:25.1.RC1<br>Atlas 850E 超节点/Atlas 650E 服务器:25.6.RC1<br>其他产品:26.1.0 | 26.1.0 | 26.1.0 | 2.10.0 |

**解读**:这是 26.1.0 的"唯一推荐"配套组合,体现分层解耦的版本策略——HDK 因硬件形态差异被拆分为 4 档(超级节点、超节点+服务器、加速卡、通用),其余四类(CANN/MindSpeed-LLM/TorchNPU/MindSpore)则统一对齐到 26.1.0 / 9.1.0 / 2.10.0 主版本,确保端到端版本同代。

### 表 2 MindCluster 与 CANN 版本兼容
| MindCluster | CANN 8.5.X | CANN 9.0.X | CANN 9.1.X |
|--|--|--|--|
| 7.3.0 | Y |  |  |
| 26.0.0 | Y | Y |  |
| 26.1.0 | Y | Y | Y |

**解读**:呈现"向右下方扩张"的兼容矩阵——26.1.0 是当前唯一覆盖 CANN 三个大版本(8.5.X/9.0.X/9.1.X)的 MindCluster 版本,而 7.3.0 仅兼容 8.5.X;说明 MindCluster 26.x 较 7.x 在 CANN 兼容性上前向扩展了 2 个大版本。

### 表 3 MindCluster 与 HDK 版本兼容(拆分为两个子表)
**子表 3a Ascend 950 系列产品 HDK**
| MindCluster | HDK 25.1.RC1 / 25.6.RC1 / 25.7.RC1 |
|--|--|
| 26.0.0 | Y |
| 26.1.0 | Y |

**子表 3b 其他产品 HDK**
| MindCluster | HDK 25.5.X | HDK 26.0.X | HDK 26.1.X |
|--|--|--|--|
| 7.3.0 | Y |  |  |
| 26.0.0 | Y | Y |  |
| 26.1.0 | Y | Y | Y |

**解读**:HDK 兼容性按硬件族拆分——Ascend 950 系列因对应 RC 版本(25.1.RC1/25.6.RC1/25.7.RC1,分别对应 SuperPoD、850E/650E、350)而非通用 X.Y 版本号,因此独立成表,且只有 26.x 系列覆盖;其他产品 HDK 则保留了与表 2 类似的"向下兼容三代"模式,26.1.0 是首个覆盖到 26.1.X 的版本。

### 表 4 MindCluster 与 MindSpeed-LLM 版本兼容
| MindCluster | 2.3.X | 26.0.X | 26.1.X |
|--|--|--|--|
| 7.3.0 | Y |  |  |
| 26.0.0 | Y | Y |  |
| 26.1.0 | Y | Y | Y |

**解读**:MindSpeed-LLM 兼容性矩阵与 CANN、HDK 完全同构(都覆盖 3 代),说明 MindCluster 26.x 在训练链路各组件上保持一致的"前向兼容三代"策略;26.1.0 与 MindSpeed-LLM 26.1.0 同代对齐。

### 表 5 MindCluster 与 TorchNPU 版本兼容
| MindCluster | 7.3.X | 26.0.X | 26.1.X |
|--|--|--|--|
| 7.3.0 | Y |  |  |
| 26.0.0 | Y | Y |  |
| 26.1.0 | Y | Y | Y |

**解读**:TorchNPU 矩阵与表 4 完全镜像,说明 PyTorch 适配链路在版本策略上与 MindSpeed-LLM 等同处理;26.1.0 是首个可与 TorchNPU 26.1.X 配套的版本。

### 表 6 MindCluster 与 MindSpore 版本兼容
| MindCluster | 2.7.2 | 2.9.X | 2.10.X |
|--|--|--|--|
| 7.3.0 | Y |  |  |
| 26.0.0 | Y | Y |  |
| 26.1.0 | Y | Y | Y |

**解读**:MindSpore 矩阵的最低基线为 **2.7.2**(非 X.Y 通配符,与 CANN/HDK 的 X.5.X 不同),说明 MindSpore 主版本号变迁较快(2.7 → 2.9 → 2.10),MindCluster 26.1.0 是首个同时覆盖 2.7.2 / 2.9.X / 2.10.X 的版本。

### 表 7 新增特性清单
| 组件名称 | 特性描述 |
|--|--|
| MindCluster Ascend FaultDiag | (1) 在已有故障模式库中,针对 Ascend 950 系列产品补充故障模式,并新增支持基于 pyMotor+vLLM 的故障模式;(2) 优化链路诊断工具输出报告的内容;(3) 故障诊断支持 IPv6 场景。 |
| MindCluster 集群调度组件 | (1) 支持存储 DTFS 故障;(2) Atlas 950 SuperPoD 超节点支持 IPv6 场景(参数面除外);Atlas A2/A3 系列产品支持 IPv6;(3) Volcano 支持 Pod 优先调度回原运行节点;(4) Ascend Device Plugin 故障处理插件化;(5) 支持带内检测 1825 故障上报;(6) 提供 1825 网卡的 RDMA 设备插件;(7) 支持 helm 一键化部署易用性提升;(8) NPU Exporter 支持分组配置采集周期;(9) 多级调度场景支持亚健康热切;(10) 支持配置存活探针;(11) 新增卡死检测与恢复功能;(12) 支持 Atlas 850E 超节点、Atlas 650E 服务器和 Atlas 950 SuperPoD 超节点的设备管理、亲和性调度、指标监控、故障检测、RankTable 生成等基础能力;(13) 支持 Atlas 850E 超节点、Atlas 650E 服务器的基础断点续训能力;支持 Atlas 950 SuperPoD 超节点的全量断点续训能力;(14) 支持 Atlas 850E 超节点、Atlas 650E 服务器和 Atlas 950 SuperPoD 超节点的容器化能力;(15) 支持推理故障恢复能力,包括优先级调度、缩 P 保 D 和实例级重调度;(16) 支持推理场景基于负载的弹性扩缩容能力和容器快照能力。 |

**解读**:新增特性涵盖 FaultDiag 与集群调度两条产品线。FaultDiag 侧重"故障模式库扩展(950 系列 + pyMotor+vLLM)+ 报告优化 + IPv6";集群调度覆盖面更广,按层次可归类为:网络与存储可靠性(IPv6/DTFS/1825/RDMA)、调度策略(Volcano 回原节点、亚健康热切、推理优先级/缩 P 保 D/实例级重调度、负载弹性扩缩容)、可观测与运维(NPU Exporter 分组周期、卡死检测与恢复、helm 一键化、存活探针)、硬件平台覆盖(Atlas 850E / 650E / 950 SuperPoD 的设备/亲和性/监控/故障/RankTable/容器化/断点续训)。

### 表 8 业务接口变更
| 组件名称 | 接口变更 |
|--|--|
| MindCluster Ascend FaultDiag | (1) 链路诊断工具新增配置命令 `set_config_dir`,当前仅支持设置组网配置文件 LLD.xlsx 所在路径;(2) 性能劣化功能(资源抢占和网络拥塞)采集指标数据时对训练、推理业务性能有一定影响,该特性将在后续版本日落。 |
| MindCluster 集群调度组件 | 所有 K8s 部署的组件新增存活探针。 |

**解读**:接口层面变化有两类——FaultDiag 增加 `set_config_dir` 命令用于定位 LLD.xlsx(链路诊断关键组网输入),并明确告知"性能劣化采集"为临时能力、将被下线(文档用语"日落");集群调度统一对所有 K8s 组件开启存活探针,这是与"新增特性-支持配置存活探针"配套的实际落地。

### 表 9 版本配套文档
| 文档名称 | 内容简介 | 更新说明 |
|--|--|--|
| 《MindCluster 集群调度用户指南》(./scheduling/01_introduction/00_overview.md) | 提供集群调度组件说明、特性原理和使用参考,包括各组件的安装部署、集成适配示例和 API 参考,以及部分调度方案的原理介绍参考。 | 新增使用 helm 安装组件、开发者指南、容器快照部署及使用等,其他变更详见同链接。 |
| 《MindCluster 故障诊断用户指南》(./faultdiag/ascend-faultdiag/01_introduction/01_overview.md) | 提供日志采集、日志清洗与转储、故障诊断等功能的使用指导。 | 新增 Ascend 950 系列产品、基于 pyMotor+vLLM 的故障模式等,其他变更详见同链接。 |

**解读**:两份配套文档分别对应本文档变更的两条主线——集群调度侧新增 helm 安装、开发者指南、容器快照等;故障诊断侧新增 950 系列与 pyMotor+vLLM 故障模式,均为"特性发布 → 文档同步"的强一致性体现。

## 【公式解读】
原文无公式。

## 【关联】
- 与 **集群调度组件** 的关系:本文档列出的新增特性 16 条全部归入 MindCluster 集群调度组件,其中至少 6 条(IPv6、DTFS、1825/RDMA、Atlas 850E/650E/950 SuperPoD 基础能力、断点续训、容器化、推理故障恢复与弹性扩缩容)会涉及 RankTable 生成、亲和性调度、NodeD/Ascend Device Plugin 等子模块;用户可前往 [《MindCluster 集群调度用户指南》](./scheduling/01_introduction/00_overview.md) 查看安装部署、API 参考与方案原理。
- 与 **Ascend FaultDiag 组件** 的关系:本文档列出的 3 条 FaultDiag 新增特性(950 系列故障模式扩展、pyMotor+vLLM 模式、链路诊断报告优化)和 1 条接口变更(`set_config_dir` 命令)均依赖故障模式库与日志采集链路;用户可前往 [《MindCluster 故障诊断用户指南》](./faultdiag/ascend-faultdiag/01_introduction/01_overview.md) 查看日志采集、清洗与转储、故障诊断的使用指导。
- 与 **上下游生态** 的关系:CANN / HDK / MindSpeed-LLM / TorchNPU / MindSpore 通过表 2-6 形成强版本绑定;`npu-smi` 工具通过 Ascend Docker Runtime 的 `LD_LIBRARY_PATH` 默认化与 HDK 驱动解耦,使其在容器内可正常调用;Volcano 作为 K8s 调度器承接"Pod 优先回原节点"与"多级调度亚健康热切"等调度策略;Job/Pod 级重调度作为进程级重调度遗留问题(issue 188266、Atlas A3 linkdown)的兜底手段,与 K8s 生态深度耦合。

## 【使用方法】
- **升级方式**:MindCluster 26.1.0 升级过程中对现行系统无影响;升级后 Infer Operator 组件需将日志目录删除并以 root 权限重建,或修改日志目录及日志文件的属主为 root。
- **配置项/命令**(原文涉及):
  - `-deviceResetTimeout`:启动 Ascend Device Plugin、NPU Exporter、NodeD 时等待驱动上报完整芯片的最大时长,26.1.0 默认值由 60s 改为 **600s**。
  - `set_config_dir`:链路诊断工具新增配置命令,当前仅支持设置组网配置文件 `LLD.xlsx` 所在路径。
  - 存活探针:所有 K8s 部署的集群调度组件在 26.1.0 默认启用。
  - helm 一键化部署:集群调度组件在 26.1.0 支持 helm 一键化部署,详见配套《MindCluster 集群调度用户指南》。
