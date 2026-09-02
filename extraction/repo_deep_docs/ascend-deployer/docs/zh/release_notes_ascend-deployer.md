# 版本说明

> 仓 `ascend-deployer` · 路径 `docs/zh/release_notes_ascend-deployer.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascend-deployer/docs/zh/release_notes_ascend-deployer.md

# 一体化深度解读：MindCluster Ascend Deployer 26.1.0 版本说明

---

## 【定位】

本篇文档作为「ascend-deployer」代码仓的版本变更记录（changelog），核心目的是**对外公告 MindCluster Ascend Deployer 26.1.0 Release 版本的版本配套关系、兼容性矩阵、下载源迁移策略、本版本新增/变更特性，以及配套文档指引**，帮助用户在升级或新部署前明确版本边界与组件依赖。

---

## 【技术要点】

1. **下载源迁移**：MindCluster 7.3.0 与 26.0.0 中已在 GitCode 官方 Release 发布的集群调度组件，以及 TorchNPU 中已在 GitCode 官方 Release 发布的 **15 个版本共 104 个 wheel**，默认下载源由华为云 OBS 迁移至 GitCode。软件包名称、SHA256 校验值、离线部署目录保持不变。
2. **网络放行要求**：用户环境若通过防火墙或白名单限制外网访问，下载 MindCluster 或 TorchNPU 软件包前需放行域名 `gitcode.com` 与 `file-cdn.gitcode.com`。
3. **保留原下载源的范围**：PyTorch 上游 wheel 以及 GitCode 无对应发行制品的 TorchNPU 版本继续使用原下载源（即仍走原通道）。
4. **版本规划与命名**：产品进入 26.0 系列，MindCluster 26.0 版本规划为 26.0.0、26.1.0、26.2.0、26.3.0 四个连续发布；本版本为 26.1.0，Release 类型。
5. **新增硬件适配**：支持 Atlas 850E 超节点、Atlas 650E 服务器、Atlas 950 SuperPoD 超节点；适配 openEuler 24.03 SP4 aarch64。
6. **新增组件与命令**：支持部署 Infer Operator 组件；下载器新增 `--show-releases` 命令行参数，安装后收集报告展示 error messages，并支持展示软件包的配套版本。

---

## 【关键机制与数据】

- **下载源切换的"平替"语义**（原文）：本次切换仅改变默认下载源端点（OBS → GitCode），不改变软件包身份与产物形态——`软件包名称、SHA256校验值、离线部署目录保持不变`。这意味着已构建的离线包/校验脚本无需重做，只需更新下载地址白名单。
- **下载源覆盖范围**（原文）：
  - 迁移至 GitCode：MindCluster 7.3.0/26.0.0 的集群调度组件；TorchNPU 已发布 15 个版本共 104 个 wheel。
  - 保留原源：PyTorch 上游 wheel；GitCode 无对应发行制品的 TorchNPU 版本。
- **域名白名单**（原文）：GitCode 主站 `gitcode.com` + 内容分发 `file-cdn.gitcode.com`，二者缺一不可，否则会出现解析失败或下载中断。
- **错误可观测性增强**（原文）：安装昇腾软件后的收集报告中展示 `error messages`，以及下载昇腾软件时支持展示软件包的配套版本——属于"可观测性/自助排错"层面的改动，不涉及安装主流程变更。
- **版本节奏暗示**（原文）：26.0 系列按 4 个小版本滚动发布，说明 26.1.0 处于持续维护节奏中；性能/资源数据原文未提供。

---

## 【表格解读】

### 原文表 0：产品版本信息（基本信息表）

| 产品名称 | 产品版本 | 版本类型 |
|---|---|---|
| MindCluster Ascend Deployer | 26.1.0 | Release版本 |

逐行解读：
- 第 1 行三列共同界定本次 release 的主体：自研的昇腾软件一键式安装部署工具 MindCluster Ascend Deployer。
- 产品版本 `26.1.0` 与本文档"26.0 系列规划"中的第二个迭代吻合。
- 版本类型为正式 Release（区别于 RC/Beta），意味着可生产使用。

---

### 原文表 1：MindCluster Ascend Deployer 软件版本配套表

| MindCluster Ascend Deployer | CANN | HDK | MindCluster（集群调度/故障诊断/ToolBox）| MindSpore |
|---|---|---|---|---|
| 26.1.0 | 9.1.0 | <ul><li>Atlas 350 加速卡：25.7.RC1</li><li>Atlas 950 SuperPoD 超节点：25.1.RC1</li><li>Atlas 850E 超节点/Atlas 650E 服务器：25.6.RC1</li><li>其他产品：26.1.0</li></ul> | 26.1.0 | 2.10.0 |

逐行解读：
- 仅一行有效数据，对应本版本（26.1.0）的"锁定配套组合"：与 CANN 9.1.0、MindCluster 26.1.0、MindSpore 2.10.0 三大件主版本号对齐。
- HDK 列做了**按产品分通道**的拆解：Atlas 350 用 25.7.RC1、Atlas 950 SuperPoD 用 25.1.RC1、Atlas 850E/650E 用 25.6.RC1，其余产品用 26.1.0。这体现了"硬件型号差异 → HDK RC 版本差异"的多分支配套策略。
- 横向看，HDK 引入了 25.7.RC1 / 25.6.RC1 / 25.1.RC1 三个 RC 版本与 26.1.0 正式版并存，提示这部分硬件仍处于预发布节奏。

---

### 原文表 2：MindCluster Ascend Deployer 与 CANN 版本兼容

| MindCluster Ascend Deployer | 8.5.X | 9.0.X | 9.1.X |
|---|---|---|---|
| 7.3.0 | Y | N | N |
| 26.0.0 | Y | Y | N |
| 26.1.0 | Y | Y | Y |

逐行解读：
- 矩阵纵轴为 Deployer 三个版本，横轴为 CANN 三个系列；"Y/N" 表示是否可配套。
- Deployer **7.3.0** 只兼容 CANN 8.5.X，是历史版本边界。
- Deployer **26.0.0** 与 8.5.X、9.0.X 兼容，但与 9.1.X 不兼容——意味着从 26.0.0 升 26.1.0 时若想用 CANN 9.1.X，必须同步升级 Deployer。
- Deployer **26.1.0** 是当前唯一同时兼容 CANN 8.5.X / 9.0.X / 9.1.X 的版本，是 CANN 跨版本兼容最广的 Deployer。

---

### 原文表 3：MindCluster Ascend Deployer 与 HDK 版本兼容（拆分为两张子表）

#### 表 3a：Ascend 950 系列产品 HDK

| MindCluster Ascend Deployer | 25.1.RC1 / 25.6.RC1 / 25.7.RC1 |
|---|---|
| 26.0.0 | Y |
| 26.1.0 | Y |

逐行解读：
- 该子表将三个 RC 版本合并为一列，表明三者对 Deployer 26.0.0/26.1.0 均兼容，简化呈现。
- 7.3.0 不在此表，说明 7.3.0 时代 Ascend 950 系列产品尚未纳入配套范围（或兼容关系未列出）。

#### 表 3b：其他产品 HDK

| MindCluster Ascend Deployer | 25.5.X | 26.0.X | 26.1.X |
|---|---|---|---|
| 7.3.0 | Y | N | N |
| 26.0.0 | Y | Y | N |
| 26.1.0 | Y | Y | Y |

逐行解读：
- 与 CANN 兼容表（表 2）结构高度一致：Deployer 7.3.0 仅匹配旧版 25.5.X；26.0.0 新增支持 26.0.X；26.1.0 再扩展至 26.1.X。
- Deployer 26.1.0 是当前唯一一个横跨 25.5.X / 26.0.X / 26.1.X 三个 HDK 系列的版本，回溯兼容性最强。

---

### 原文表 4：MindCluster Ascend Deployer 与 MindCluster（集群调度/故障诊断/ToolBox）版本兼容

| MindCluster Ascend Deployer | 7.3.X | 26.0.X | 26.1.X |
|---|---|---|---|
| 7.3.0 | Y | N | N |
| 26.0.0 | Y | Y | N |
| 26.1.0 | Y | Y | Y |

逐行解读：
- 纵轴 Deployer 与横轴 MindCluster 版本号命名节奏相同（7.3.0/26.0.0/26.1.0），所以本表呈现"对角线 + 上三角兼容"的规律——即同主版本号或更高小版本号之间互可配套，但 Deployer 不能与比自己更新的 MindCluster 组件组合。
- Deployer 26.1.0 同时支持 MindCluster 7.3.X、26.0.X、26.1.X，可平滑承接旧集群部署。

---

### 原文表 5：MindCluster Ascend Deployer 与 MindSpore 版本兼容

| MindCluster Ascend Deployer | 2.7.2 | 2.9.X | 2.10.X |
|---|---|---|---|
| 7.3.0 | Y | N | N |
| 26.0.0 | Y | Y | N |
| 26.1.0 | Y | Y | Y |

逐行解读：
- 与前述兼容表遵循相同"逐版扩展"模式：每个新 Deployer 版本增加一个新 MindSpore 主版本的支持，但保留对老版本的兼容。
- Deployer 26.1.0 是首个支持 MindSpore 2.10.X 的 Deployer 版本，结合表 1 中"26.1.0 配 MindSpore 2.10.0"的硬配套关系，可推断这是为最新 AI 框架而推出的对应能力。

---

### 原文表 6：版本配套文档

| 文档名称 | 内容简介 | 更新说明 |
|---|---|---|
| 《MindCluster Ascend Deployer 用户指南》（链接 `./01_introduction/01_introduction.md`） | 提供 OS 依赖和 Docker 的自动下载以及一键式安装的功能，并支持驱动、固件、CANN、MindCluster 组件（性能测试，故障诊断，集群调度）、AI 框架（TensorFlow、MindSpore 或 PyTorch）、MindIE 镜像等软件包在线&离线下载、安装及升级。 | 新增支持 Atlas 850E 超节点、Atlas 650E 服务器、Atlas 950 SuperPoD 超节点，支持 Infer Operator 组件安装部署等，其他变更详见用户指南。 |

逐行解读：
- 这是文末的"文档地图"表，唯一一条记录指向《MindCluster Ascend Deployer 用户指南》，详细功能描述与本文档"新增特性"小节互为印证——即 Atlas 850E/650E/950 SuperPoD 硬件适配、Infer Operator 组件部署等具体使用方法需进入该用户指南查阅。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档中显式提供的内部链接仅指向 `./01_introduction/01_introduction.md`（即《MindCluster Ascend Deployer 用户指南》），在文中出现两次：
- 第一次位于文末"版本配套文档"表中的文档名称列；
- 第二次位于同一表的"更新说明"列末尾，用于跳转到详细变更说明。

基于文档语义可建立的上下游/横向关联如下：
- **上游组件**：本文档声明的兼容矩阵（CANN 9.1.0、HDK 多版本、MindCluster 26.1.0、MindSpore 2.10.0）决定了 Deployer 26.1.0 可调用的最大版本边界，是用户评估"升哪个版本"的入口。
- **下游使用方**：Atlas 350 加速卡、Atlas 850E 超节点、Atlas 650E 服务器、Atlas 950 SuperPoD 超节点四类硬件，以及 openEuler 24.03 SP4 aarch64 操作系统均在本次适配范围；这些是新硬件用户选型的关键依据。
- **下载链路下游**：默认下载源迁移至 GitCode 后，依赖 `gitcode.com` 与 `file-cdn.gitcode.com` 域名可达性，影响企业内网/防火墙策略。
- **同仓库参考**：本文档位于 `docs/zh/release_notes_ascend-deployer.md`，与代码仓 README、用户指南（`01_introduction/01_introduction.md`）属于同一文档体系，使用方法、命令细节应回到用户指南查阅。

---

## 【使用方法】

- **新增命令参数**：
  - `--show-releases`：下载器新增命令行参数，执行后展示当前支持的昇腾软件版本配套兼容性表格，便于用户查询各组件间的版本配套关系。
  - `infer-operator`：新增安装部署组件参数，用于部署集群调度 Infer Operator 组件。
- **部署能力入口**：
  - 一键式安装支持驱动、固件、CANN、MindCluster 组件（性能测试、故障诊断、集群调度）、AI 框架（TensorFlow、MindSpore 或 PyTorch）、MindIE 镜像等软件包在线/离线下载、安装及升级。
  - 支持 Atlas 850E 超节点、Atlas 650E 服务器、Atlas 950 SuperPoD 超节点等新型硬件。
  - 适配 openEuler 24.03 SP4 aarch64 操作系统。
  - 部署 Infer Operator 组件；安装后收集报告展示 error messages；下载时展示软件包配套版本。
- **网络/防火墙配置**：
  - 若环境限制外网访问，在从 GitCode 下载 MindCluster 或 TorchNPU 软件包前，需放行 `gitcode.com` 与 `file-cdn.gitcode.com`。
- **版本选型约束**：
  - MindCluster Ascend Deployer 组件需要配套使用，**请勿跨版本混用各组件**（原文）。
  - 详细的启用方式、配置项、命令格式以及完整版本配套关系表，原文未直接给出使用方法步骤，建议参考配套的《MindCluster Ascend Deployer 用户指南》（`./01_introduction/01_introduction.md`）。
