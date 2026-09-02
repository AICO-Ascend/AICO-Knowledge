# MindStudio Insight 版本发布说明

> 仓 `msinsight` · 路径 `docs/zh/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/release_notes/release_notes.md

# MindStudio Insight 版本发布说明 — 一体化深度解读

---

## 【定位】

这篇文档是 MindStudio Insight（针对昇腾大模型训练/推理场景的可视化调优工具）的**版本发布总览 changelog**，用于向用户集中说明当前及历史各版本的核心特性、新增能力、配套 CANN 版本关系和下载渠道，以便用户按需选型与升级。

---

## 【技术要点】

1. **多版本配套 CANN 的兼容性矩阵**：明确四个 MindStudio Insight 版本（26.1.0 / 26.0.0 / 26.0.0-alpha.1 / 8.3.0）分别对应 CANN 9.1.0 及以前、9.0.0 及以前、8.5.0 及以前、8.0.RC2 及以前，决定升级路径。
2. **ftrace 采集与分析能力的双向扩展**：既新增 tracefs/debugfs 模式 ftrace 采集（脱离 trace-cmd 依赖）、ftrace DB 格式输出与上下文切换/Running-Sleeping-Runnable/IRQ 耗时统计的 Excel 报告输出；又通过 `trace_convert` 支持按 CPU 范围过滤转换，降低大规模 trace 转换开销。
3. **Profiling × ftrace 联合导入与 System View 分页签呈现**：设备侧 Profiling 数据与 Host 侧 ftrace 调度数据可导入同一工程，并在 System View 中按数据类型自动归类展示。
4. **内存快照分析三件套**：① memsnapshot 新增潜在泄漏 Tensor 查询（区间内申请未释放的内存块，含总/最大/最小大小）；② 内存池 segment 详情独立展示（segment size、allocated size、gap size、block count、gap count、max gap size）；③ reservedSize 折线观测 + 解析进度加载提示。
5. **容器化与 Web 访问部署模式**：新增 Dockerfile、streamer 容器启停脚本，支持 HTTP/HTTPS+mTLS、数据目录/证书目录挂载、指定端口与动态端口；前端/后端/底座/ JupyterLab 插件均适配 IPv6。
6. **Timeline 交互与多卡可读性优化**：多硬件指标泳道合并层级、悬浮工具栏、同名泳道置顶泛化、右键时间对齐、通信算子一键对齐、查找窗口二级筛选；Python 调用栈独立泳道展示；COMMUNICATION_OP 表新增 deviceId 列以适配多 device。

---

## 【关键机制与数据】

- **ftrace 主动分析机制（原文）**：支持 tracefs/debugfs 模式采集 → 在无法安装或使用 trace-cmd 的环境仍可采集 ftrace；输出新增 ftrace DB 格式并适配 Timeline 展示；统计维度包含上下文切换、Running/Sleeping/Runnable 时间、IRQ 耗时和次数，最终生成含多工作表和图表的 Excel 分析报告。
- **ftrace 与 Profiling 联合导入机制（原文）**：导入同一工程后，System View 根据数据类型展示对应分析页签，便于在同一工程中联合分析设备侧 Profiling 与 Host 侧调度数据。
- **trace_convert 过滤转换机制（原文）**：可按 CPU 范围过滤，仅转换指定 CPU 的 CPU Scheduling、IRQ/SoftIRQ 和 Process Scheduling 事件，目标为"减少大规模 trace 数据的转换耗时和输出体积"。
- **潜在泄漏 Tensor 识别机制（原文）**：以"区间内申请但未在区间内释放的内存块"为判定条件，展示总大小、最大大小、最小大小三个聚合指标。
- **内存池 segment 详情机制（原文）**：在来源 alloc/map 事件存在时同步展示事件上下文；事件缺失时仍可查看 segment 级统计（segment size / allocated size / gap size / block count / gap count / max gap size）。
- **PyTorch Snapshot 分析规模（原文）**：能够处理更大（数十 GB 级）的 snapshot 文件，针对强化学习场景的内存问题定位。
- **Host-Device 内存拷贝专项分析（原文）**：按流按类型统计；同一流按类型查询详细算子信息；算子点击可跳转 timeline 位置。
- **ACLGraph JSONPrint 约束（原文）**：保证 Record 与 Wait 事件能同时结束，且 Wait 事件的起始时间应小于 Record 事件的起始时间，以展现 Record → Wait 的唤醒信息。
- **容器化部署能力（原文）**：streamer 容器启停脚本支持 HTTP、HTTPS + mTLS、数据目录挂载、证书目录挂载、指定端口和动态端口等场景。
- **网络与通信数据展示（原文）**：支持展示 NIC 表和 ROCE 表中的网络相关数据，统一优化 Byte、Packet 等单位展示；COMMUNICATION_OP 表适配 deviceId 列。
- **26.0.0 集成方式（原文）**：用 Python 解释器 + 集群分析工具三方库 + 集群分析 Python 脚本，代替 PyInstaller。

> 原文未给出任何性能数字（如加速比、内存节省百分比、转换耗时具体数值等），以上均为机制层面的原文描述。

---

## 【表格解读】

### 表 1：版本对比（原文逐字还原）

| 版本           | 类型   | 发布日期   | 主要特性                                                                                  |
| -------------- | ------ | ---------- | ----------------------------------------------------------------------------------------- |
| 26.1.0         | 稳定版 | 2026-07-25 | ftrace 主动分析、内存快照分析增强、容器化与 Web 访问、Timeline 交互增强、场景化资料完善   |
| 26.0.0         | 稳定版 | 2026-04-29 | ftrace 联合分析、PyTorch Snapshot 分析、Triton 片上内存可视化、Host-Device 内存拷贝分析   |
| 26.0.0-alpha.1 | 预览版 | 2026-02-04 | Host Bound 定位、强化学习性能分析、Timeline 增强                                         |
| 8.3.0          | 稳定版 | 2026-02-03 | 集群性能分析、算子性能分析、内存分析、服务化分析                                          |

**逐行解读**：
- 26.1.0（最新稳定版）：发布时间 2026-07-25，特性聚焦"主动分析（ftrace）+ 内存分析增强 + 容器化 + Timeline 易用性 + 资料完备"，是当前主推版本。
- 26.0.0（前一个稳定版）：2026-04-29 发布，能力重心在 ftrace 联合分析、PyTorch/Triton 框架级内存分析、Host-Device 内存拷贝分析，已包含本版本大部分底层能力。
- 26.0.0-alpha.1（预览版）：2026-02-04 发布，预演了 Host Bound 定位与强化学习场景分析能力，介于稳定版之间。
- 8.3.0（基线稳定版）：2026-02-03 发布，定位为四大基础分析域（集群/算子/内存/服务化），代表 MindStudio Insight 早期通用能力。

### 表 2：版本配套关系（原文逐字还原）

| MindStudio Insight 版本 | CANN 版本      | 说明                                                     |
| ----------------------- | -------------- | -------------------------------------------------------- |
| 26.1.0                  | 9.1.0 及以前   | [CANN 9.1.0 下载](https://www.hiascend.com/cann/download)   |
| 26.0.0                  | 9.0.0 及以前   | [CANN 9.0.0 下载](https://www.hiascend.com/cann/download)   |
| 26.0.0-alpha.1          | 8.5.0 及以前   | [CANN 8.5.0 下载](https://www.hiascend.com/cann/download)   |
| 8.3.0                   | 8.0.RC2 及以前 | [CANN 8.0.RC2 下载](https://www.hiascend.com/cann/download) |

**逐行解读**：
- 26.1.0 ↔ CANN 9.1.0 及以前：最新版配套最新 CANN，向下兼容。
- 26.0.0 ↔ CANN 9.0.0 及以前：若使用 CANN 9.0.x 训练栈应使用 26.0.0。
- 26.0.0-alpha.1 ↔ CANN 8.5.0 及以前：作为过渡预览版覆盖更老的 CANN 8.5.x。
- 8.3.0 ↔ CANN 8.0.RC2 及以前：最早的稳定版，支持 CANN 8.0 系列。
- 表中"说明"列全部指向 https://www.hiascend.com/cann/download，是统一 CANN 下载入口。

### 表 3：26.1.0 下载地址（原文逐字还原）

| 平台                     | 下载链接 |
| ------------------------ | -------- |
| Windows                  | [MindStudio-Insight_26.1.0_win.exe](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_26.1.0_win.exe)   |
| Linux x86_64 | [MindStudio-Insight_26.1.0_linux_x86_64.zip](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_26.1.0_linux_x86_64.zip) |
| Linux aarch64 | [MindStudio-Insight_26.1.0_linux_aarch64.zip](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_26.1.0_linux_aarch64.zip) |
| macOS x86_64 | [MindStudio-Insight_26.1.0_macos_x86_64.dmg](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_26.1.0_macos_x86_64.dmg) |
| macOS aarch64 | [MindStudio-Insight_26.1.0_macos_aarch64.dmg](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_26.1.0_macos_aarch64.dmg) |
| JupyterLab Linux x86_64 | [mindstudio_insight_jupyterlab-26.1.0-py3-none-linux_x86_64.whl](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/mindstudio_insight_jupyterlab-26.1.0-py3-none-linux_x86_64.whl) |
| JupyterLab Linux aarch64 | [mindstudio_insight_jupyterlab-26.1.0-py3-none-linux_aarch64.whl](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/mindstudio_insight_jupyterlab-26.1.0-py3-none-linux_aarch64.whl) |
| Docker镜像 Ubuntu 22.04 x86_64 | [MindStudio-Insight_docker_image_26.1.0-ubuntu22.04_py3.10_x86_64.tar](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_docker_image_26.1.0-ubuntu22.04_py3.10_x86_64.tar) |
| Docker镜像 Ubuntu 22.04 aarch64 | [MindStudio-Insight_docker_image_26.1.0-ubuntu22.04_py3.10_aarch64.tar](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_docker_image_26.1.0-ubuntu22.04_py3.10_aarch64.tar) |
| Docker镜像 openEuler 24.03 x86_64 | [MindStudio-Insight_docker_image_26.1.0-openeuler24.03_py3.11_x86_64.tar](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_docker_image_26.1.0-openeuler24.03_py3.11_x86_64.tar) |
| Docker镜像 openEuler 24.03 aarch64 | [MindStudio-Insight_docker_image_26.1.0-openeuler24.03_py3.11_aarch64.tar](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.1.0.B100_002/MindStudio-Insight_docker_image_26.1.0-openeuler24.03_py3.11_aarch64.tar) |

**逐行解读**：
- Windows / Linux(x86_64+aarch64) / macOS(x86_64+aarch64)：覆盖桌面端全平台，桌面端产物形态为 .exe / .zip / .dmg。
- JupyterLab Linux x86_64 / aarch64：两套 .whl 包，对应 Jupyter 插件安装形态，与 26.1.0 容器化/Web 访问能力配合。
- Docker 镜像四套：基系统分别为 Ubuntu 22.04（Python 3.10）与 openEuler 24.03（Python 3.11），各覆盖 x86_64 与 aarch64 两种架构，对应"容器化部署与 Web 访问"新能力。
- 所有下载 URL 锚点统一指向 tag `tag_MindStudio_26.1.0.B100_002`，是 26.1.0 版本的唯一发布源。

### 表 4：26.0.0 下载地址（原文逐字还原）

| 平台 | 下载链接 |
|------|---------|
| Windows | [MindStudio-Insight_26.0.0_win.exe](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.0.0.B120_0012/MindStudio-Insight_26.0.0_win.exe) |
| Linux x86_64 | [MindStudio-Insight_26.0.0_linux_x86_64.zip](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.0.0.B120_0012/MindStudio-Insight_26.0.0_linux_x86_64.zip) |
| Linux aarch64 | [MindStudio-Insight_26.0.0_linux_aarch64.zip](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.0.0.B120_0012/MindStudio-Insight_26.0.0_linux_aarch64.zip) |
| macOS x86_64 | [MindStudio-Insight_26.0.0_macos_x86_64.dmg](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.0.0.B120_0012/MindStudio-Insight_26.0.0_macos_x86_64.dmg) |
| macOS aarch64 | [MindStudio-Insight_26.0.0_macos_aarch64.dmg](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.0.0.B120_0012/MindStudio-Insight_26.0.0_macos_aarch64.dmg) |
| JupyterLab Linux x86_64 | [mindstudio_insight_jupyterlab-26.0.0-py3-none-linux_x86_64.whl](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.0.0.B120_0012/mindstudio_insight_jupyterlab-26.0.0-py3-none-linux_x86_64.whl) |
| JupyterLab Linux aarch64 | [mindstudio_insight_jupyterlab-26.0.0-py3-none-linux_aarch64.whl](https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_26.0.0.B120_0012/mindstudio_insight_jupyterlab-26.0.0-py3-none-linux_aarch64.whl) |

**逐行解读**：26.0.0 仅提供 Windows / Linux(x86_64+aarch64) / macOS(x86_64+aarch64) 桌面端与 JupyterLab .whl，**未提供 Docker 镜像包**——Docker 镜像是 26.1.0 才开始引入的新交付形态。下载锚点 tag 为 `tag_MindStudio_26.0.0.B120_0012`。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **安装指引（内部链接）**：`../install_guide/mindstudio_insight_install_guide.md` —— 本 changelog 仅给出下载链接与系统平台清单，具体安装步骤、环境要求、容器启动参数等依赖该安装指南。
- **CANN 配套**：版本配套表直接链向 `https://www.hiascend.com/cann/download`，各 MindStudio Insight 版本的能力（如 ftrace、内存快照、ACLGraph、Stream 合并、Triton 片上内存分析）均依赖对应 CANN 版本提供底层数据。
- **上游采集/解析工具**：
  - 26.1.0 的 `trace_convert` 工具、tracefs/debugfs 模式 ftrace 采集 → 支撑 System View 中 Profiling 与 ftrace 的联合导入。
  - 26.0.0 的 trace-cmd 采集控制工具 → 26.1.0 在此基础上扩展为主动分析与结构化统计。
- **下游可视化模块**：Timeline（包含 Python 调用栈泳道、通信算子、NIC/ROCE、COMMUNICATION_OP deviceId）、内存池状态图（含 segment 详情、潜在泄漏 Tensor）、System View（按数据类型自动归类页签）、算子调优（Top Wall Reason、stall top reason）、Kernel E2E（后端表格与整体耗时）—— 这些视图都通过 changelog 列出的新数据通道（ftrace DB 格式、reservedSize 折线、memsnapshot 增强、IPv6 等）被驱动。
- **集群分析工具**：26.0.0 起改用 Python 集成（替代 PyInstaller），26.1.0 增加其标准输出/标准错误日志落盘，便于上游 MindStudio Insight 调用时定位问题。
- **JupyterLab 插件**：作为独立 .whl 产物，与桌面端并列分发；在 26.1.0 中已适配 IPv6 场景。

---

## 【使用方法】

原文为 changelog 文档，**未直接给出具体的启用命令、配置项或 API 调用**。可参考的"使用前置信息"包括：

- **选择版本**：依据配套表（表 2）按 CANN 版本选择对应的 MindStudio Insight 版本下载与升级。
- **获取安装包**：依据平台（Windows / Linux x86_64+aarch64 / macOS x86_64+aarch64 / JupyterLab / Docker）从表 3 / 表 4 中下载对应产物；26.1.0 起首次提供 Docker 镜像（Ubuntu 22.04、openEuler 24.03 各架构）。
- **详细安装步骤**：跳转内部链接 `../install_guide/mindstudio_insight_install_guide.md` 获取。

具体的安装命令、配置文件路径、streamer 启动参数、trace_convert 调用语法、Dockerfile 构建方式、JupyterLab 插件注册方式等，原文均未展开，需结合安装指南与对应功能专题文档使用。
