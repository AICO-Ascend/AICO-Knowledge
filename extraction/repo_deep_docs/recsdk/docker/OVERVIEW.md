# RecSDK Docker Image Build Overview

> 仓 `recsdk` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docker/OVERVIEW.md

# RecSDK Docker 镜像构建文档深度解读

## 【定位】

本文档是华为昇腾 RecSDK（推荐 SDK）仓库 `docker/` 目录下所有 Dockerfile 的总览说明，旨在帮助开发者快速理解镜像标签命名规则、查找到对应芯片/OS/框架的 Dockerfile，并通过**直接 `docker run`** 或**本地 `docker build`** 两种方式快速使用或二次开发 RecSDK 容器镜像——本质上是一篇"Docker 镜像使用手册"而非算法/性能文档。

---

## 【技术要点】

1. **镜像标签六段式命名约定**：`{RecSDK版本}-{CANN版本}-{芯片标识}-{OS版本}-{Python版本}-{框架标识}`，例如 `26.1.0-cann9.1.0-910-ubuntu20.04-py3.7-tf`；可通过 `--build-arg CORE_TYPE=a2/a3/a5` 切换芯片平台，并在标签中用 `910 / a3 / 950` 替换 `{chip}` 占位符。
2. **同一 Dockerfile 跨芯片复用**：通过 `CORE_TYPE` 构建参数将同一份 Dockerfile 同时产出 `Atlas 800T A2 (a2)`、`Atlas 800T A3 (a3)`、`Atlas 950 (a5)` 三种平台镜像，默认 `CORE_TYPE=a2`。
3. **多 OS / 多 Python / 多框架矩阵**：当前支持 `ubuntu20.04-py3.7-tf`、`ubuntu22.04-py3.11-pt`、`openEuler22.03-py3.7-tf`、`openEuler22.03-py3.11-pt` 共 4 类 Dockerfile 组合。
4. **主机硬件架构自适应**：Dockerfile 内置 `x86 / ARM` 双架构检测与处理逻辑，无需手动区分。
5. **多版本 Python 虚拟环境共存**：TF 容器内置 `tf1_env` (TF 1.15.0) 与 `tf2_env` (TF 2.6.5) 两套环境；PT 容器内置 `torch_v1_pt2.6.0 / torch_v1_pt2.7.1 / torch_v1_pt2.10.0` 及 `torch_v2_pt2.7.1 / torch_v2_pt2.10.0` 共 5 套环境，通过 `source /opt/buildtools/.../bin/activate` 切换，使用 `deactivate` 退出。
6. **驱动以只读卷方式注入**：容器通过 `-v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro` 与 `-v /etc/ascend_install.info:/etc/ascend_install.info` 将宿主机驱动与固件安装信息挂载进容器，避免重复安装。
7. **NPU 设备可见性控制**：通过环境变量 `ASCEND_VISIBLE_DEVICES=0-7`（原文示例，16 卡机器改为 `0-15`）显式指定容器可见的 NPU 卡范围。

---

## 【关键机制与数据】

- **RecSDK 三大能力定位（原文）**：
  1. 基础模型训练能力——支持单机单卡与多机多卡分布式训练；
  2. 推荐专属能力——基于稀疏表方案提供特征存取 / 准入 / 淘汰；
  3. 大规模稀疏表能力——支持加速器内存 / 主机内存 / 主机盘三级存储、多节点存储与动态扩容，**规模可超过 10 TB**（原文："Scale can exceed 10 TB"）。
- **数据流（基于 `docker run` 命令推断）**：宿主机 → 容器通过 `--net=host` 共享网络栈 → `ASCEND_VISIBLE_DEVICES` 限定 NPU → 只读卷注入 `/usr/local/Ascend/driver` 与 `/etc/ascend_install.info` → 用户业务目录通过 `{mount_dir}:{mount_dir}` 双向挂载 → 容器内 `/bin/bash` 启动。
- **资源配额（原文命令示例）**：容器内存上限 `-m 300g`（按实际使用调整）。
- **构建期依赖下载**：Dockerfile 内已包含软件包下载与安装逻辑（外网访问必需），无需用户预准备；可按需修改 CANN 包与 RecSDK 包版本。
- **磁盘需求（原文）**：构建至少需要 **60 GB** 可用空间。
- **硬件支持（原文，文档此节被截断）**：所有版本 Dockerfile 原生支持主机架构自动检测，覆盖 `x86` 与 `ARM` 硬件处理（原文节末尾被截断，更详细列表未给出）。

> 注：原文末尾 "Hardware Support Information" 一节在提供的截断文本中未完整呈现，仅有上述一条。

---

## 【表格解读】

### 表 1：RecSDK 26.1.0 Dockerfile 归档路径（原文逐字还原）

| Tag | Dockerfile |
|-----|------------|
| 26.1.0-cann9.1.0-{chip}-ubuntu20.04-py3.7-tf | [Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-ubuntu20.04-py3.7-tf) |
| 26.1.0-cann9.1.0-{chip}-ubuntu22.04-py3.11-pt | [Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-ubuntu22.04-py3.11-pt) |
| 26.1.0-cann9.1.0-{chip}-openEuler22.03-py3.7-tf | [Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-openEuler22.03-py3.7-tf) |
| 26.1.0-cann9.1.0-{chip}-openEuler22.03-py3.11-pt | [Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-openEuler22.03-py3.11-pt) |

**逐行解读**：
- 第 1 行：TensorFlow + Python 3.7 + Ubuntu 20.04 组合，CANN 9.1.0，RecSDK 26.1.0，芯片位占位 `{chip}`；
- 第 2 行：PyTorch + Python 3.11 + Ubuntu 22.04 组合，唯一使用 Python 3.11 + Ubuntu 22.04 的 PT 镜像；
- 第 3 行：TensorFlow + Python 3.7 + openEuler 22.03 组合，面向国产化 OS 部署；
- 第 4 行：PyTorch + Python 3.11 + openEuler 22.03 组合，面向国产化 OS + PyTorch 用户。
- 4 个 Dockerfile 共享同一个 `CORE_TYPE` 构建参数机制，因此同一份脚本可在 `a2 / a3 / a5` 三种芯片间复用。

---

### 表 2：前置条件（原文逐字还原）

| Item | Requirement |
|------|-------------|
| Docker Version | 20.10 or higher recommended; must support `--net=host` network mode |
| Host OS | Ubuntu 20.04 / 22.04 (x86_64 or ARM), openEuler 22.03 (x86_64 or ARM) |
| Atlas Driver & Firmware | Host must have Atlas NPU driver and firmware installed; default driver path is `/usr/local/Ascend/driver` |
| CANN Version | CANN 9.1.0 or higher recommended (Dockerfile can be configured with a download URL; defaults to version 9.1.0) |
| Disk Space | At least 60 GB of free space recommended for image builds |
| Network | External network access is required during the build process to download dependency packages |

**逐行解读**：
- Docker 版本：必须 ≥ **20.10**，且必须支持 `--net=host` 模式（用于容器与宿主机共享 NPU 网络栈）；
- Host OS：覆盖 3 种官方 OS × 2 种硬件架构（x86_64 与 ARM）；
- 驱动/固件：必须先在宿主机装好 Atlas 驱动，默认路径 `/usr/local/Ascend/driver`，容器以只读方式挂载；
- CANN 版本：≥ **9.1.0** 推荐，Dockerfile 默认下载 9.1.0，但 URL 可配置；
- 磁盘：**≥ 60 GB** 为推荐预留空间；
- 网络：构建期必须能访问外网以下载依赖。

---

### 表 3：`CORE_TYPE` 与芯片平台映射（原文逐字还原）

| CORE_TYPE | Applicable Platform | Tag Chip Identifier |
|-----------|---------------------|---------------------|
| `a2` | Atlas 800T A2 Training Server | `910` |
| `a3` | Atlas 800T A3 Super Node Server | `a3` |
| `a5` | Atlas 950 Generation | `950` |

**逐行解读**：
- `a2` → 标签中 `chip` 字段写 `910`，对应 Atlas 800T A2 训练服务器；
- `a3` → 标签中 `chip` 字段写 `a3`（与构建参数同名），对应 Atlas 800T A3 超节点服务器；
- `a5` → 标签中 `chip` 字段写 `950`，对应 Atlas 950 系列。
- 该映射是 `--build-arg CORE_TYPE=...` 与最终镜像 tag 命名之间的"翻译表"，用户必须在两处保持一致。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 RecSDK 主体的关系**：本目录镜像以 RecSDK 主体（`Ascend/RecSDK`）为内核，镜像内默认激活的虚拟环境（`tf1_env / tf2_env / torch_v1_* / torch_v2_*`）即对应 RecSDK 在不同 TF/PT 版本下的开发套件；
- **与 CANN 栈的关系**：镜像内置 CANN 包（默认 9.1.0），与宿主机 Atlas 驱动/固件协同——驱动由宿主机只读挂载注入，CANN 由镜像自带；
- **与多芯片平台的关系**：通过 `CORE_TYPE` 构建参数，使同一份 Dockerfile 适配 `a2 / a3 / a5` 三种 Atlas 平台，覆盖训练服务器、超节点服务器与新一代 Atlas 950；
- **与多 OS 生态的关系**：同时支持 Ubuntu 20.04/22.04 与 openEuler 22.03，覆盖开源与国产化操作系统生态；
- **与上游/下游文档**：
  - 上游：`RecSDK source code`（`https://gitcode.com/Ascend/RecSDK`）；
  - 上游：`RecSDK documentation`（`https://gitcode.com/Ascend/RecSDK/tree/develop/docs`）；
  - 上游：`Issue feedback`（`https://gitcode.com/Ascend/RecSDK/issues`）；
  - 平行：`OVERVIEW.zh.md`（同一文档的中文版本）；
  - 下游：4 个具体 Dockerfile 文件（见表 1）。
- **文档内部无页内跳转链接**（提供的文末标注"内部链接: (无)"）。

---

## 【使用方法】

### 1. 直接运行已存在的镜像（原文命令逐字保留）

```bash
docker run -it \
    --name {container_name} \
    --net=host \
    -m 300g \
    -e ASCEND_VISIBLE_DEVICES=0-7 \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v {mount_dir}:{mount_dir} \
    {image_name}:{image_tag} \
    /bin/bash
```

参数要点：`ASCEND_VISIBLE_DEVICES` 按实机卡数调整（如 16 卡写 `0-15`）；`-m 300g` 按需调整；驱动/固件信息两个 `-v` 必须挂载，否则容器内 NPU 不可见。

### 2. 本地构建 PyTorch 镜像（ubuntu22.04 示例，原文命令逐字保留）

```bash
docker build --build-arg CORE_TYPE=a2 \
  -t recsdk_pt:26.1.0-cann9.1.0-910-ubuntu22.04-py3.11-pt \
  -f docker/Dockerfile.26.1.0-cann9.1.0-ubuntu22.04-py3.11-pt .
```

### 3. 本地构建 TensorFlow 镜像（ubuntu20.04 示例，原文命令逐字保留）

```bash
docker build --build-arg CORE_TYPE=a2 \
  -t recsdk_tf:26.1.0-cann9.1.0-910-ubuntu20.04-py3.7-tf \
  -f docker/Dockerfile.26.1.0-cann9.1.0-ubuntu20.04-py3.7-tf .
```

> `CORE_TYPE` 可取 `a2 / a3 / a5`；切换芯片时同步把 tag 中的 `910` 改为 `a3` 或 `950`。

### 4. openEuler 镜像构建

原文仅说明"构建流程与 Ubuntu 示例相同"，未给出具体命令，请参照上述 PyTorch/TF 示例替换 Dockerfile 路径。

### 5. 二次开发（基于已有镜像叠加业务层，原文片段逐字保留）

```dockerfile
FROM recsdk_tf:26.1.0-cann9.1.0-910-ubuntu20.04-py3.7-tf
RUN apt update -y && \
    apt install ...
```

### 6. 切换 Python 虚拟环境（TensorFlow 容器，原文命令逐字保留）

```bash
source /opt/buildtools/tf1_env/bin/activate   # TF 1.15.0
source /opt/buildtools/tf2_env/bin/activate   # TF 2.6.5
```

### 7. 切换 Python 虚拟环境（PyTorch 容器，原文命令逐字保留）

```bash
source /opt/buildtools/torch_v1_pt2.6.0/bin/activate
source /opt/buildtools/torch_v1_pt2.7.1/bin/activate
source /opt/buildtools/torch_v1_pt2.10.0/bin/activate
source /opt/buildtools/torch_v2_pt2.7.1/bin/activate
source /opt/buildtools/torch_v2_pt2.10.0/bin/activate
```

退出虚拟环境：`deactivate`。

### 8. 关键配置项汇总（原文摘录）

| 配置项 | 取值/默认值 | 含义 |
|---|---|---|
| `CORE_TYPE` | `a2`（默认）/`a3`/`a5` | 构建参数，指定目标芯片平台 |
| `--net=host` | 必选 | 容器共享宿主机网络栈 |
| `-m` | `300g`（示例） | 容器内存上限 |
| `ASCEND_VISIBLE_DEVICES` | `0-7`（示例） | 容器可见 NPU 卡范围 |
| `/usr/local/Ascend/driver` | 只读挂载 | 宿主机驱动注入路径 |
| `/etc/ascend_install.info` | 只读挂载 | 驱动/固件安装信息 |
| CANN 版本 | 默认 `9.1.0`（Dockerfile 可配 URL） | 镜像内置 CANN 包版本 |
| 磁盘预留 | ≥ 60 GB | 构建所需磁盘空间 |
| Docker 版本 | ≥ 20.10 | 需支持 `--net=host` |
