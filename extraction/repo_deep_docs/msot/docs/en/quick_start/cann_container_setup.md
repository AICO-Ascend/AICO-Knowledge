# Ascend CANN Installation Guide for Container Environment

> 仓 `msot` · 路径 `docs/en/quick_start/cann_container_setup.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msot/docs/en/quick_start/cann_container_setup.md

# msot 仓库 docs/en/quick_start/cann_container_setup.md 深度解读

---

## 【定位】

本篇文档面向 Ascend CANN（Compute Architecture for Neural Networks）AI 算子开发人员，描述如何在 Docker 容器环境中通过官方 CANN 镜像与官方启动脚本快速搭建起一套开箱即用的 Ascend AI 算子开发环境。

---

## 【技术要点】

1. **镜像来源与命名格式**：CANN 官方镜像托管在华为云镜像仓 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann`，完整路径形如 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:<image version>`，通过包含完整 registry 地址以实现免额外 Docker registry 配置。
2. **版本选择三元组**：选版需综合 CANN 版本（默认推荐最新稳定版）、芯片型号（以 `npu-smi info` 现场核实为准）、操作系统（openEuler/Ubuntu 皆可，推荐 openEuler）。示例版本 `8.5.1-910b-openeuler24.03-py3.11`，镜像 ID `6df0c5bbc16f`，体积 **17.1GB**。
3. **启动脚本机制**：通过 `curl -fLO --retry 3` 从 `https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py` 下载 `ctr_in.py` 启动脚本，并以 `python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>` 调用，自动挂载宿主 `$HOME` 目录用于数据共享。
4. **容器重入机制**：当 `ctr_in.py` 仅接收 **1 个参数**（容器名）时，进入"进入已存在容器"模式，并支持**容器名模糊匹配**；也可直接使用 Docker 原生命令 `docker exec -it <container> bash`。
5. **耗时预期**：完整流程通常 **<5 分钟**（依赖网络），本地已具备镜像时可在**秒级**完成；单次镜像 pull 约 **3–5 分钟**。

---

## 【关键机制与数据】

| 项目 | 内容 |
|---|---|
| 镜像仓完整地址 | `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann`（原文） |
| 启动脚本下载地址 | `https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py`（原文） |
| 脚本下载命令 | `cd ~ && curl -fLO --retry 3 ... && chmod +x ctr_in.py`（原文） |
| 启动命令模板 | `python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>`（原文） |
| 数据流/挂载机制 | 将宿主机的 `$HOME` 挂载进容器以共享数据（原文 "used to mount the $HOME directory for data sharing"） |
| 启动后登录态 | 直接以宿主机用户名进入容器终端，提示符形如 `[root@localhost alice]#`（原文） |
| 系统识别（示例输出） | `5.10.0-60.139.0.166.oe2203.aarch64`；显示时间 `Fri Mar 20 06:46:56 UTC 2026`；System load 8.95、Memory used 6.2%、Swap used 55.4%、Usage On 25%、Users online 0（原文预期输出） |

---

## 【表格解读】

### 表格 1 — 前置条件表（Prerequisites）

| Condition | Description | Verification Command |
| ------------- | --------------- | -------------- |
| Docker engine | Installed and the daemon is running | `docker info` |
| Network connectivity | Accessible to the Huawei Cloud image repository for pulling images and downloading scripts | `ping swr.cn-south-1.myhuaweicloud.com` |

**逐行解读**：
- **Docker engine 行**：要求本机已安装 Docker 引擎且守护进程正在运行，并通过 `docker info` 验证。该命令会输出 Docker 版本、镜像数量、存储驱动、容器运行数等综合状态信息，是确认 Docker daemon 健康的最常用一次性探针。
- **Network connectivity 行**：要求可访问华为云镜像仓（用于拉取镜像）及 `inst.obs.cn-north-4.myhuaweicloud.com`（用于下载 `ctr_in.py` 启动脚本）。通过 `ping swr.cn-south-1.myhuaweicloud.com` 这种基于 ICMP 的连通性验证仅作示例，文本未强制要求 `ping` 必须成功。

### 表格 2 — 镜像版本选择建议表

| Option          | Suggestion                                               |
| ----------- | ------------------------------------------------ |
| **CANN Version** | If no special requirements exist, it is recommended to select the latest stable version.                                |
| **Chip Model**    | Select based on the actual hardware (run `npu-smi info` to check). |
| **Operating System**    | Either openEuler or Ubuntu is acceptable; openEuler is recommended.               |

**逐行解读**：
- **CANN Version 行**：推荐无特殊需求时选取最新稳定版，与文档示例中 `8.5.1-910b-openeuler24.03-py3.11` 这种带具体次版本号的组合命名方式相一致。
- **Chip Model 行**：芯片型号必须与实际硬件匹配，并通过 `npu-smi info`（华为昇腾提供的 NPU 系统管理命令）确认；该示例中的 `910b` 即属于昇腾 NPU 系列代号。
- **Operating System 行**：底层 OS 两种均接受，但官方推荐 openEuler（与示例 `openeuler24.03` 一致，可能与华为生态兼容性最佳）。

### 表格 3 — 容器启动参数表

| Parameter | Description | Example |
| ---------------- | ------------------------------------ | --------------- |
| `CONTAINER_NAME` | Container name, which can be used to log in to the container later. Recommended format: `{Purpose}_{ID}` | `op_dev_alice` |
| `USER_NAME` | Username on the host machine, used to mount the `$HOME` directory for data sharing. | `alice` |
| `IMAGE` | Docker image ID or full name. | `6df0c5bbc16f` |

**逐行解读**：
- **`CONTAINER_NAME` 行**：容器名既是 Docker 内部标识，也是后续重入/管理入口；推荐 `{Purpose}_{ID}` 形式（如 `op_dev_alice` 表示「算子开发_用户 alice」），便于多用户多用途的容器隔离。
- **`USER_NAME` 行**：宿主上的用户名，`ctr_in.py` 据此将宿主 `$HOME` 路径挂载进容器，实现主机与容器间的数据持久化共享；同名主机用户也用于确保文件权限一致。
- **`IMAGE` 行**：既可填写镜像 ID（如 `6df0c5bbc16f`——对应示例中所列 CANN 镜像短哈希），也可填写完整镜像名（如 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11`），二者效果等价。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游能力依赖**：本文档为算子开发铺路，故其能力交付物位于"基于 Ascend NPU 的算子开发环境"的下游；它本身依赖两项上游：(a) Docker 引擎（前置条件中的 Docker engine），(b) 华为云镜像仓可达性（前置条件中的 Network connectivity）以及 `inst.obs.cn-north-4.myhuaweicloud.com` 上的 `ctr_in.py` 提供方。
- **同仓特性关联**：第 1.1 节在文本中明确给出"若有合适的本地镜像可直接跳到 **Section 2: Starting the Container**"的内部跳转，说明本指南与"启动容器"子流程构成先后关系；本指南不与仓库中其他独立模块建立链接，文档末尾标注的"内部链接"也确认**无**（`(无)`）。
- **横向对应**：与"Huawei Cloud image repository `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann`"——即 `ascendhub` 上的 CANN Image Repository 页面（含 Image Versions 标签页）——形成内容与索引的对应；Hiascend 站点 `https://www.hiascend.com/developer/ascendhub/detail/17da20d1c2b6493cb38765adeba85884` 是镜像清单入口。
- **风险边界**：免责声明指明本文仅供学习参考，不保证生产稳定性与安全性，意味着它属于"开发/试用"层级的文档，与任何生产级 CI/CD 或集群调度流程无明确上下游耦合。

---

## 【使用方法】

### 启用方式总览（原文操作步骤）

1. **确认前置条件**：执行 `docker info` 确认 Docker daemon 健康；执行 `ping swr.cn-south-1.myhuaweicloud.com` 确认镜像仓可达。
2. **查询本地镜像（可选）**：执行 `docker images | grep cann`，若结果中已有合适 CANN 镜像（如 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11`），可跳到第 2 步。
3. **拉取镜像**：访问 CANN Image Repository → 切到 **Image Versions** 标签页 → 选定（CANN 版本 / 芯片型号 / 操作系统）三元组 → 复制完整版本号 → 执行：
   ```bash
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:<image version>
   # 示例（耗时约 3–5 分钟）：
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11
   ```
4. **下载启动脚本**：
   ```shell
   cd ~ && curl -fLO --retry 3 https://inst.obs.cn-north-4.myhuaweicloud.com/env/ctr_in.py && chmod +x ctr_in.py
   ```
5. **启动容器**（进入 `python3 ~/ctr_in.py <CONTAINER_NAME> <USER_NAME> <IMAGE>` 形态，参数详见上文表格 3）：
   ```shell
   # 用镜像 ID：
   python3 ~/ctr_in.py op_dev_alice alice 6df0c5bbc16f
   # 用镜像全名：
   python3 ~/ctr_in.py op_dev_alice alice swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:8.5.1-910b-openeuler24.03-py3.11
   ```
   启动成功后直接进入容器终端，等待命令输入。
6. **退出后再进入容器**：
   - 方案 A：`python3 ~/ctr_in.py op_dev_alice`（仅传容器名，进入已存在容器并支持模糊匹配）。
   - 方案 B：`docker exec -it op_dev_alice bash`（Docker 原生命令）。

### 关键配置项与可调点（原文出现）

- **`CONTAINER_NAME`**：推荐命名格式 `{Purpose}_{ID}`。
- **`USER_NAME`**：宿主用户名，决定 `$HOME` 挂载路径。
- **`IMAGE`**：镜像短 ID 或完整名称二选一。
- **操作系统偏好**：openEuler > Ubuntu。
- **CANN 版本偏好**：无特殊需求选最新稳定版。
- **镜像大小示例**：`17.1GB`。

### 性能/时间基线（原文出现）

- 镜像拉取耗时：约 **3–5 分钟**。
- 完整环境搭建耗时：**< 5 分钟**。
- 本地已有镜像时：秒级完成。

> 注：原文未涉及任何 GPU/NPU 共享模式、卷挂载细节（如 `-v` 参数）、端口映射、`--privileged`、`--device` 等 Docker 容器运行参数；这些"原文未涉及"的内容由 `ctr_in.py` 内部封装，本文未给出。

## 图文联合解读

- `image.png`: ## 图文联合解读

**1) 图中内容**：展示了华为云镜像仓库的 `cann` 镜像版本选择页面。顶部标注仓库元信息（公开、最新版本 8.5.0-910b-ubuntu22.04-py3.11、大小 8 GB、发布者 Ascend）；红色箭头指向"镜像版本"标签页；下方版本表格列出四种芯片平台对应的 Tag（910b/310p/a3/910），红框高亮强调 `8.5.0` 版本号，并支持 x86_64 与 arm64 双架构。

**2) 技术结论**：用户应根据自身 NPU 芯片型号（910/910b/310p/a3）选择对应 Tag，版本号与 Ubuntu 22.04 + Python 3.11 需对齐。

**3) 与文档关系**：对应"1. Preparing the Image"章节——指导用户从华为云镜像仓库定位 CANN 镜像版本，为后续 `docker pull` 提供选型依据。
