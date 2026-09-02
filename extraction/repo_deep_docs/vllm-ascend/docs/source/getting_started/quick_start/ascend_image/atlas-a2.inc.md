# atlas-a2.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/ascend_image/atlas-a2.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-a2.inc.md

# vllm-ascend Atlas A2 镜像部署文档深度解读

## 【定位】

这篇文档解决的是"如何拉取并启动 vllm-ascend Docker 镜像以在 Atlas A2 硬件上运行"的问题——具体给出了 Atlas A2 在 **Ubuntu** 与 **openEuler** 两种宿主系统下，从镜像拉取到容器启动的完整命令序列，并说明了宿主机 NPU 设备、Ascend 驱动路径、模型缓存卷与对外服务端口的绑定方式。

---

## 【技术要点】

1. **镜像仓库与版本变量**：两个 OS 变体均从 `quay.io/ascend/vllm-ascend` 仓库拉取，版本号由 Jinja 模板变量 `{{ vllm_ascend_version }}` 注入；openEuler 变体在版本号后追加 `-openeuler` 后缀（即 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-openeuler`）。
2. **镜像源说明（包含文件）**：拉取镜像章节通过 `{% include "getting_started/quick_start/ascend_image/image_download_mirror.inc.md" %}` 嵌入了另一篇关于镜像下载/镜像源（mirror）配置的片段，说明该文档链上存在一个独立的镜像源配置子模块。
3. **NPU 设备挂载**：容器使用 `--device /dev/davinci0`（由 `export DEVICE=/dev/davinci0` 设置）作为计算设备，并额外挂载三个设备节点：
   - `/dev/davinci_manager` — 设备管理器
   - `/dev/devmm_svm` — 设备内存 / SVM
   - `/dev/hisi_hdc` — 昇腾主机侧通信通道
4. **驱动与工具挂载**：将宿主机的 5 个目录/文件以 `-v` 形式只读透传进容器：
   - `/usr/local/dcmi → /usr/local/dcmi`
   - `/usr/local/bin/npu-smi → /usr/local/bin/npu-smi`
   - `/usr/local/Ascend/driver/lib64/ → /usr/local/Ascend/driver/lib64/`
   - `/usr/local/Ascend/driver/version.info → /usr/local/Ascend/driver/version.info`
   - `/etc/ascend_install.info → /etc/ascend_install.info`
5. **共享内存与命名**：`--shm-size=1g` 提供 1 GiB `/dev/shm`，`--name vllm-ascend` 设置容器名，`--rm` 表示退出即清理。
6. **模型缓存与端口**：`${HOME}/.cache` 通过 `-v` 挂载到容器内 `/root/.cache`（默认 HuggingFace 模型缓存路径），`-p 8000:8000` 暴露 vLLM 默认 HTTP 服务端口。

---

## 【关键机制与数据】

**原文：文档描述的是一种"镜像 + 设备透传 + 卷挂载"的部署模式**，关键数据流/参数如下：

- **镜像获取通道**：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`（Ubuntu）/ `...-openeuler`（openEuler）。版本号不是文档里写死的字面量，而是由构建系统通过 Jinja 变量 `vllm_ascend_version` 注入；这意味着该文档每次构建时 `vllm_ascend_version` 会被替换为发布版本号。
- **NPU 设备命名约定**：原文示例使用 `/dev/davinci0`（编号为 0 的 Davinci 设备，即 NPU 0）；若宿主机有多张卡，用户应按需替换 `$DEVICE`（例如 `/dev/davinci1`、`/dev/davinci2` …）。
- **卷挂载语义**：`$MODEL_CACHE:/root/.cache` 的右侧路径 `/root/.cache` 是容器内 HuggingFace / vLLM 默认模型缓存根目录；左侧 `${HOME}/.cache` 是宿主机用户目录下的等价缓存。这样容器销毁后模型权重仍保留在宿主机，避免重复下载。
- **共享内存**：`--shm-size=1g` 提供 1 GiB `/dev/shm`，供 PyTorch 等框架的 DataLoader/张量共享使用。
- **驱动一致性保证**：通过透传 `/usr/local/Ascend/driver/lib64/`、`version.info`、`/etc/ascend_install.info` 与 `dcmi`/`npu-smi`，确保容器内的 CANN/驱动版本与宿主机完全一致，避免出现"容器内调用驱动版本 ≠ 宿主机驱动"的不兼容情况。
- **运行模式**：`docker run ... -it "$IMAGE" bash`——不是直接以服务形式拉起，而是进入交互式 bash shell，便于用户在容器内手动启动 vLLM 服务（如后续步骤中执行 `vllm serve ...`）。端口 `8000` 的 `-p 8000:8000` 只是预先暴露，并未在 `docker run` 阶段主动启动任何进程。
- **性能数据**：原文无任何 benchmark、吞吐、延迟、显存占用等量化数据。

---

## 【表格解读】

原文无表格。所有信息均以 bash 命令、env 变量和挂载列表形式呈现。

---

## 【公式解读】

原文无公式。文档全部内容为命令与挂载参数，不涉及数学表达式或伪代码。

---

## 【关联】

虽然文档文末未列出内部链接（题目标注"内部链接: (无)"），但从文档自身内容仍可推断出以下关联关系：

- **子文档包含（Include）**：拉取镜像章节通过 `{% include "getting_started/quick_start/ascend_image/image_download_mirror.inc.md" %}` 嵌入了「镜像下载/镜像源」子文档（`image_download_mirror.inc.md`）。该子文档负责说明 Docker 镜像源/加速器（mirror）的配置方式，本文档则专注 Atlas A2 设备侧的拉取与启动。两者共同构成完整镜像获取链路。
- **跨硬件家族**：本文件是 `atlas-a2.inc.md`，路径前缀 `atlas_image/` 与同级其他 `*.inc.md` 文件（如 Atlas 800I A2 的姊妹变体、Atlas 9000 等）平行存在，说明整个 `vllm-ascend` 文档为不同 Atlas 硬件型号维护了各自的镜像部署片段，并复用 `image_download_mirror.inc.md` 这一共享子模块。
- **跨 OS 变体**：同一文档内 Ubuntu 与 openEuler 两个 tab 共用相同的 `docker run` 命令模板，差异仅在于镜像 tag；说明 vLLM Ascend 在两种宿主 OS 上的运行命令语义一致。
- **与上层 quick_start 编排的关系**：本片段位于 `getting_started/quick_start/ascend_image/` 路径下，是上层「Quick Start」编排文档的"Atlas A2"分支；上层文档会负责在容器启动后执行 `vllm serve` 等服务拉起命令（本文档未涉及，故写在【使用方法】中需注意）。

---

## 【使用方法】

以下步骤逐字摘录自原文，按"先拉镜像，再启容器"的顺序展开。两个 OS 变体命令并列，原文亦按 tab 形式呈现。

### 1. 拉取镜像（Pull the image）

**Ubuntu**（原文锚点：`quick-start-atlas-a2-ubuntu`）：
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
docker pull "$IMAGE"
```

**openEuler**（原文锚点：`quick-start-atlas-a2-openeuler`）：
```bash
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-openeuler
docker pull "$IMAGE"
```

> 说明：`{{ vllm_ascend_version }}` 为构建期 Jinja 变量，最终渲染为具体的版本号字符串。

### 2. 启动容器（Start the container，原文锚点：`quick-start-atlas-a2-container`）

两个 OS 变体的 `docker run` 命令完全一致：

```bash
export DEVICE=/dev/davinci0
export MODEL_CACHE="${HOME}/.cache"

mkdir -p "$MODEL_CACHE"

docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --device "$DEVICE" \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v "$MODEL_CACHE:/root/.cache" \
    -p 8000:8000 \
    -it "$IMAGE" bash
```

### 配置项语义速览（按原文出现顺序）

| 配置项 | 取值 | 作用（原文语义） |
|---|---|---|
| `DEVICE` | `/dev/davinci0` | 容器内访问的 NPU 设备节点；可按需改成 `/dev/davinci1` 等 |
| `MODEL_CACHE` | `${HOME}/.cache` | 宿主机模型缓存根目录 |
| `--rm` | — | 容器退出时自动删除 |
| `--name` | `vllm-ascend` | 容器名 |
| `--shm-size` | `1g` | 分配 1 GiB `/dev/shm` |
| `--device` × 4 | davinci0、davinci_manager、devmm_svm、hisi_hdc | 透传 NPU 计算设备与管理/通信节点 |
| `-v` × 6 | dcmi、npu-smi、Ascend driver lib64/version.info、ascend_install.info、模型缓存 | 透传驱动、工具与模型权重 |
| `-p` | `8000:8000` | 暴露 vLLM HTTP 服务端口 |
| `-it "$IMAGE" bash` | — | 启动后进入交互式 bash |

### 文档未涉及的事项

- **如何拉起 vLLM 服务**：原文只启动 bash shell，未给出 `vllm serve` 等命令——这部分由上层 Quick Start 编排文档负责。
- **多卡配置**：`--device` 仅示范了 `$DEVICE` 单卡透传；多卡（如 `--device /dev/davinci0 --device /dev/davinci1`）原文未直接列出。
- **离线/无网环境下的 `docker load` 流程**：仅依赖 `docker pull`，未涉及。
- **环境变量与运行时配置**（如 `ASCEND_VISIBLE_DEVICES`、`VLLM_*`）：原文未涉及。
- **健康检查、端口冲突处理**：原文未涉及。
