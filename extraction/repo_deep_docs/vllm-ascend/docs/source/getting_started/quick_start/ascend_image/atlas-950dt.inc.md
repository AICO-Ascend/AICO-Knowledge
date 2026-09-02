# atlas-950dt.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/ascend_image/atlas-950dt.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-950dt.inc.md

# vllm-ascend Atlas 950DT 快速开始文档深度解读

## 【定位】
本文档解决在 **Atlas 950DT** 硬件平台上使用 vllm-ascend 容器镜像进行快速部署的问题，描述了针对该平台拉取预构建 Docker 镜像并启动容器（同时覆盖 Ubuntu 与 openEuler 两种操作系统变体）的完整流程。

---

## 【技术要点】

1. **双操作系统支持**：提供两套镜像变体 —— Ubuntu 版镜像标签为 `{{ vllm_ascend_version }}-a5`，openEuler 版镜像标签为 `{{ vllm_ascend_version }}-a5-openeuler`，两者均通过 `quay.io/ascend/vllm-ascend` 仓库分发。

2. **镜像拉取方式**：通过 `export IMAGE=...` 设置环境变量后再调用 `docker pull "$IMAGE"`，版本号使用 Jinja 模板变量 `{{ vllm_ascend_version }}` 在构建时替换。

3. **容器命名与清理**：使用 `--name vllm-ascend` 命名容器，并加 `--rm` 参数使容器退出后自动删除。

4. **网络与共享内存配置**：使用 `--net=host` 共享主机网络栈，`--shm-size=1g` 为容器分配 1 GB 共享内存（用于 PyTorch DataLoader 等多进程通信）。

5. **NPU 设备透传**：通过 4 个 `--device` 参数将 Ascend NPU 相关设备节点透传到容器内 —— `/dev/davinci0`（昇腾计算设备 0）、`/dev/davinci_manager`（设备管理器）、`dev/devmm_svm`（共享虚拟内存）、`/dev/hisi_hdc`（主机-设备通信通道）。

6. **驱动与工具目录挂载**：通过 `-v` 将宿主机的 8 个关键路径挂载到容器，覆盖 DCMI（`/usr/local/dcmi`）、hccn_tool 网卡工具、NPU smi 工具、驱动库目录 `lib64/`、驱动版本文件以及安装信息文件 `ascend_install.info`。

---

## 【关键机制与数据】

**工作原理与数据流**（原文标注）：

- **镜像层（原文）**：文档顶部通过 `{% include "getting_started/quick_start/ascend_image/image_download_mirror.inc.md" %}` 片段引入镜像下载镜像源配置（即在拉取前切换/配置 Docker Registry mirror），随后通过环境变量 + `docker pull` 完成镜像拉取。
- **缓存层（原文）**：定义 `MODEL_CACHE="${HOME}/.cache"`，用 `mkdir -p` 创建后挂载到容器内 `/root/.cache`，用于持久化 HuggingFace 等模型权重，避免容器销毁后重新下载。
- **设备层（原文）**：将宿主机的 4 类昇腾设备节点直接透传（device passthrough）给容器，使容器内的 CANN 驱动栈可直接操作物理 NPU，而驱动库、工具二进制、版本/安装信息则通过 bind mount 方式复用宿主机已安装的昇腾驱动，无需在容器内重复安装。
- **入口（原文）**：容器以 `-it "$IMAGE" bash` 启动交互式 shell。

> 原文未提供性能数据、TPS、时延等指标。

---

## 【表格解读】

**原文无表格**。

原文为结构化 markdown，包含 4 个代码块（2 个 `docker pull` 命令、2 个 `docker run` 命令）以及若干锚点（`#quick-start-atlas-950dt-ubuntu`、`#quick-start-atlas-950dt-openeuler`、`#quick-start-atlas-950dt-container`），但未包含 markdown 表格。下面对两个 OS 变体的差异点做对照说明：

| 维度 | Ubuntu | openEuler |
|---|---|---|
| 镜像 tag（原文） | `{{ vllm_ascend_version }}-a5` | `{{ vllm_ascend_version }}-a5-openeuler` |
| `docker run` 命令（原文） | 完全相同（设备、挂载、网络参数均一致） | 完全相同（设备、挂载、网络参数均一致） |

两个变体**仅在镜像 tag 上不同**，容器启动命令完全一致，说明容器内运行时已能跨这两种 OS 复用宿主机的昇腾驱动栈。

---

## 【公式解读】

**原文无公式**。

文档为操作型 guide，未涉及任何数学公式或伪代码表达。

---

## 【关联】

- **镜像源配置模块（原文）**：通过 `{% include "getting_started/quick_start/ascend_image/image_download_mirror.inc.md" %}` 引入"镜像下载镜像源配置"片段，说明 Atlas 950DT 与其他 Atlas 平台（如 Atlas 800I A2、Atlas 300I Duo 等）共享同一份 Docker Registry mirror 配置逻辑。
- **同目录其他 Atlas 平台文档**：本文档位于 `docs/source/getting_started/quick_start/ascend_image/atlas-950dt.inc.md`，命名规则表明该目录采用 `<平台型号>.inc.md` 的片段化组织，便于被上层 quick_start 页面通过 `include` 拼装。本文档是该系列中专门针对 **950DT** 的片段。
- **版本变量（原文）**：镜像 tag 中使用的 `{{ vllm_ascend_version }}` 是文档站构建期由 MkDocs 注入的全局版本号变量，与 `vllm-ascend` 软件包版本号保持一致。
- **父页面关联**：锚点 `quick-start-atlas-950dt-ubuntu`、`quick-start-atlas-950dt-openeuler`、`quick-start-atlas-950dt-container` 均采用 `quick-start-atlas-950dt-*` 命名空间，供父页面（quick_start 入口）做页内跳转。
- 用户提供的**内部链接清单为 "无"**，本文档在仓库内未显式通过 markdown 链接指向其他文档，但通过 `include` 与锚点机制与其他 Atlas 文档保持结构耦合。

---

## 【使用方法】

**镜像拉取（原文）**：

```bash
# Ubuntu
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a5
docker pull "$IMAGE"

# openEuler
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a5-openeuler
docker pull "$IMAGE"
```

**容器启动（原文）**：

```bash
export MODEL_CACHE="${HOME}/.cache"
mkdir -p "$MODEL_CACHE"

docker run --rm \
    --name vllm-ascend \
    --net=host \
    --shm-size=1g \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v "$MODEL_CACHE:/root/.cache" \
    -it "$IMAGE" bash
```

**关键配置项（原文汇总）**：

| 配置项 | 取值 | 作用 |
|---|---|---|
| `--shm-size` | `1g` | 容器共享内存大小 |
| `--device` | `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` | 透传 4 类昇腾 NPU 设备节点 |
| `-v MODEL_CACHE` | `${HOME}/.cache → /root/.cache` | 持久化模型/权重缓存 |
| `-v` 驱动目录 | `/usr/local/dcmi`、`Ascend/driver/tools/hccn_tool`、`bin/npu-smi`、`Ascend/driver/lib64/` | 复用宿主机昇腾驱动/工具 |
| `-v` 版本/信息文件 | `Ascend/driver/version.info`、`/etc/ascend_install.info` | 注入驱动版本与安装信息 |
| 网络模式 | `--net=host` | 共享主机网络 |

> 原文未提供后续 vllm 服务启动命令或推理调用示例；本文档止步于容器启动并进入 `bash` shell 的阶段。
