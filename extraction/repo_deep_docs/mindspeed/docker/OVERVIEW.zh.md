# MindSpeed Core Docker 镜像概述

> 仓 `mindspeed` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docker/OVERVIEW.zh.md

# docker/OVERVIEW.zh.md 深度解读

## 【定位】

这篇文档是 MindSpeed Core（昇腾大模型加速库）官方 Docker 镜像的**总览/使用指南**，解决「用户如何在昇腾 NPU 环境下，以 Docker 镜像方式获取、构建、运行 MindSpeed Core + Megatron-LM 训练开发环境」的问题，描述了镜像命名规则、Tag 体系、构建参数矩阵、运行挂载方式与多架构支持的完整能力。

---

## 【技术要点】

1. **统一 Dockerfile + 构建脚本结构**：当前版本采用一份 `docker/Dockerfile` + `docker/build.sh` 入口，通过参数化实现不同 NPU/OS/架构/CANN 版本的镜像构建，避免多套 Dockerfile 维护。

2. **镜像 Tag 命名模板**：`{MindSpeed版本}-cann{CANN版本}-torch_npu{TorchNPU版本}-{NPU类型}-{操作系统}-py{Python版本}`，其中 NPU 类型字段（`a3` / `910b` / `950`）强制小写，且 `--base-image` 必须与已发布 CANN 镜像名完全一致（原文：会原样传入）。

3. **多架构镜像支持**：Tag 本身为 x86 + aarch64 二合一多架构镜像，构建完成后生成 `-aarch64` / `-x86_64` 后缀子 Tag；通过 `-a, --arch` 参数可显式选择 `aarch64` 或 `x86_64`，默认跟随当前宿主机架构。

4. **构建参数矩阵化**：脚本提供 11 个可配置参数（`--npu-type` / `--os` / `--arch` / `--base-image-version` / `--base-image` / `--python-version` / `--torch-version` / `--torch-npu-version` / `--numpy-version` / `--mindspeed-branch` / `--megatron-branch` / `--image-version`），其中 `--base-image` 优先级高于 `--base-image-version`。

5. **代理自动透传机制**：宿主机设置的 `http_proxy`、`https_proxy`、`HTTP_PROXY`、`HTTPS_PROXY`、`NO_PROXY`、`no_proxy` 环境变量会被脚本自动作为 Docker 构建参数转发，但**不会保留**在最终镜像中（保证镜像的纯净性）。

6. **容器运行时挂载点**：必须挂载 `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info` 四个驱动/管理面路径，以及用户自定义的 `{path-to-data}` → `/data`、`{path-to-weights}` → `/weights`，并需启用 `--privileged`、`--network host`、`--ipc=host`。

---

## 【关键机制与数据】

- **工作原理（数据流）**（原文）：构建脚本 `docker/build.sh` 接收参数 → 选定基础 CANN 镜像 → 在该镜像内安装 PyTorch（默认 `2.7.1`）、TorchNPU（默认 `2.7.1.post8`）、MindSpeed Core（默认 ref `v26.1.0_core_r0.12.1`）、Megatron-LM（默认 ref `core_v0.12.1`）以及 `requirements.txt` 中的 Python 依赖 → 恢复并校验 PyTorch/TorchNPU/NumPy（默认 `1.26.0`）版本 → 产出镜像。

- **目录布局**（原文）：MindSpeed 克隆到 `/MindSpeed`，Megatron-LM 克隆到 `/Megatron-LM`，默认工作目录为 `/MindSpeed`。

- **示例数据 Tag**（原文）：
  - `v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.11`
  - `v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11`

- **多架构后缀示例**（原文）：`v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11-aarch64`

- **最新支持的 6 种 Tag 组合**（原文）：覆盖 `a3` × {openeuler24.03, ubuntu22.04}、`910b` × {openeuler24.03, ubuntu22.04}、`950` × {openeuler24.03, ubuntu22.04} 共 6 个组合，统一 CANN 9.1.0 + TorchNPU 2.7.1.post8 + Python 3.11 + Content 为 `MindSpeed-Core/Megatron-LM`。

- **历史 Tag 查询入口**（原文）：参考 `docker/support_tags.md`。

---

## 【表格解读】

### 表格 1：快速参考

| 项目 | 说明 |
| ------ | ------ |
| 镜像名称 | `mindspeed-core` |
| 源码仓库 | https://gitcode.com/Ascend/MindSpeed |
| Dockerfile 路径 | `docker/Dockerfile` |
| 默认场景 | MindSpeed Core 训练与开发 |
| 基础镜像 | 可配置 CANN 镜像，默认 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.11` |
| 默认工作目录 | `/MindSpeed` |

**逐行解读**：
- **镜像名称** `mindspeed-core` —— 在 SWR 仓库中注册的产品镜像名，pull/run 命令均以此为前缀。
- **源码仓库** 指向 `gitcode.com/Ascend/MindSpeed`，即 MindSpeed 上游开源仓库。
- **Dockerfile 路径** `docker/Dockerfile` —— 仓库内构建脚本入口相对路径。
- **默认场景** 明确镜像定位为「训练 + 开发」双重用途，非纯推理。
- **基础镜像** 默认 `cann:9.1.0-910b-openeuler24.03-py3.11`，表示 CANN 9.1.0 + 910b NPU + openEuler 24.03 + Python 3.11 组合，可通过参数切换。
- **默认工作目录** `/MindSpeed` 对应 MindSpeed 源码克隆位置，便于直接执行训练脚本。

### 表格 2：CANN 9.1.0 最新版本镜像 Tag 列表（原文逐字还原）

| Tag | Dockerfile | Content |
| ------ | ------ | ------ |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-ubuntu22.04-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-950-openeuler24.03-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |
| v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-950-ubuntu22.04-py3.11 | [Dockerfile](https://gitcode.com/Ascend/MindSpeed/blob/master/docker/Dockerfile) | MindSpeed-Core/Megatron-LM |

**逐行解读**：
- 所有 6 行共用相同 CANN（9.1.0）、TorchNPU（2.7.1.post8）、Python（3.11）、Content（MindSpeed-Core/Megatron-LM），变化维度为 NPU 类型 × 操作系统。
- **第 1 行**：`a3` + `openeuler24.03` —— 面向昇腾 A3 系列（Atlas 900 A3 SuperPoD 集群） + openEuler 操作系统。
- **第 2 行**：`a3` + `ubuntu22.04` —— 同样 A3 硬件但 Ubuntu 22.04 操作系统。
- **第 3 行**：`910b` + `openeuler24.03` —— 910b（Atlas 800/900） + openEuler，**为默认组合**。
- **第 4 行**：`910b` + `ubuntu22.04` —— 910b + Ubuntu 替代组合。
- **第 5 行**：`950` + `openeuler24.03` —— 950 系列（新一代昇腾） + openEuler。
- **第 6 行**：`950` + `ubuntu22.04` —— 950 系列 + Ubuntu。
- **Dockerfile 列**：6 行均链接到 master 分支同一份 `docker/Dockerfile`，印证「统一 Dockerfile」设计。
- **Content 列**：6 行均为 `MindSpeed-Core/Megatron-LM`，说明镜像内同时打包了 MindSpeed Core 加速库与 Megatron-LM 训练框架。
- **补充说明**（原文）：上表 Tag 为多架构镜像（x86 + aarch64 二合一），实际构建后会追加 `-aarch64` / `-x86_64` 后缀；历史 Tag 见 `support_tags.md`。

### 表格 3：构建参数表（原文逐字还原）

| 参数 | 说明 | 默认值 |
| ------ | ------ | ------ |
| `-t, --npu-type` | NPU 类型：`a3`、`910b` 或 `950` | `910b` |
| `-o, --os` | 操作系统：`openeuler24.03` 或 `ubuntu22.04` | `openeuler24.03` |
| `-a, --arch` | 目标架构：`aarch64` 或 `x86_64` | 当前宿主机架构 |
| `--base-image-version` | CANN 基础镜像版本 | `9.1.0` |
| `--base-image` | 完整 CANN 基础镜像名，优先级高于 `--base-image-version`；会原样传入 | 空 |
| `--python-version` | CANN 基础镜像中的 Python 标签 | `3.11` |
| `--torch-version` | PyTorch 版本 | `2.7.1` |
| `--torch-npu-version` | torch_npu 版本 | `2.7.1.post8` |
| `--numpy-version` | 所有依赖安装完成后恢复的 NumPy 版本 | `1.26.0` |
| `--mindspeed-branch` | 克隆 MindSpeed 使用的分支、标签或 ref | `v26.1.0_core_r0.12.1` |
| `--megatron-branch` | checkout Megatron-LM 使用的分支、标签或 ref | `core_v0.12.1` |
| `--image-version` | 默认镜像 tag 中使用的 MindSpeed 版本字段 | `v26.1.0_core_r0.12.1` |

**逐行解读**：
- **`-t, --npu-type`**：决定 NPU 硬件适配目标，取值必须为 `a3` / `910b` / `950` 之一（与 Tag 中 NPU 字段约束一致，强制小写）。
- **`-o, --os`**：选择宿主操作系统发行版，影响基础镜像选择与系统包安装。
- **`-a, --arch`**：选择 CPU 架构，决定 manifest list 中实际构建/拉取的子 Tag。
- **`--base-image-version`**：单独指定 CANN 版本号；脚本会拼接出默认镜像名。
- **`--base-image`**：覆盖默认拼接逻辑，直接给出完整镜像名（含 tag），并**原样传入**给 Docker build —— 优先级最高，用于自定义 CANN 镜像源。
- **`--python-version`**：选择基础镜像中的 Python 解释器版本（必须与基础镜像实际提供的一致）。
- **`--torch-version`** / **`--torch-npu-version`**：分别控制 PyTorch 与 TorchNPU 包版本。
- **`--numpy-version`**：因依赖安装过程中可能被升级，最后强制恢复并校验 NumPy 到 `1.26.0`，保证 ABI 兼容。
- **`--mindspeed-branch`**：控制 MindSpeed Core 源码克隆来源（分支/tag/ref）。
- **`--megatron-branch`**：控制 Megatron-LM 切出的 ref。
- **`--image-version`**：写入默认镜像 Tag 的 MindSpeed 版本字段，便于自定义版本号。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游开源仓库**：[https://gitcode.com/Ascend/MindSpeed](https://gitcode.com/Ascend/MindSpeed) —— 本文档是仓库内 `docker/` 目录的概览，与同目录 `Dockerfile`（构建清单）、`build.sh`（构建脚本）、`support_tags.md`（历史 Tag 清单）共同构成完整的镜像交付物。
- **依赖的运行时库**：
  - **CANN**（昇腾异构计算架构，默认 9.1.0）—— 通过基础镜像引入。
  - **PyTorch**（默认 2.7.1）—— 深度学习框架。
  - **TorchNPU**（默认 2.7.1.post8）—— PyTorch 的昇腾 NPU 适配插件。
  - **NumPy**（默认 1.26.0）—— 数组计算基础库，构造结束后强制恢复版本以保证 ABI 兼容。
- **宿主侧依赖（运行时挂载）**：
  - `/usr/local/Ascend/driver`（昇腾设备驱动）
  - `/usr/local/dcmi`（设备控制与管理接口）
  - `/usr/local/bin/npu-smi`（NPU 系统管理命令）
  - `/etc/ascend_install.info`（昇腾安装元信息）
- **下游组件**：容器内 `/MindSpeed`（MindSpeed Core 主体）与 `/Megatron-LM`（Megatron-LM 训练框架）共同支撑大模型训练；用户数据/权重通过 `/data` 与 `/weights` 挂载点注入。
- **镜像注册中心**：`swr.cn-south-1.myhuaweicloud.com/ascendhub/` —— 华为云 SWR（软体仓库）华南区域，承载 `mindspeed-core` 与 `cann` 基础镜像。
- **许可证链路**：基于 Apache License 2.0 发布；镜像内可能包含 Bash 等基础发行版组件及其他依赖项的额外许可证约束，**镜像用户需自行确保使用合规**。

---

## 【使用方法】

### 1. 默认构建（原文）

```bash
cd docker
bash build.sh
```

等价于使用全部默认值：NPU=`910b`、OS=`openeuler24.03`、CANN=`9.1.0`、Python=`3.11`、PyTorch=`2.7.1`、TorchNPU=`2.7.1.post8`、NumPy=`1.26.0`、MindSpeed=`v26.1.0_core_r0.12.1`、Megatron-LM=`core_v0.12.1`。

### 2. 自定义 NPU + OS + 架构 + CANN 构建（原文）

```bash
cd docker
bash build.sh -t a3 -o openeuler24.03 -a aarch64
```

### 3. 使用完整基础镜像名构建（原文）

```bash
cd docker
bash build.sh \
  --arch aarch64 \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.11
```

> 脚本会尽量从镜像 tag 自动识别 CANN 版本、NPU 类型、操作系统和 Python 版本。

### 4. 下载已发布镜像（原文）

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/mindspeed-core:v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11
```

### 5. 运行镜像（原文）

```bash
docker run -it -d \
  --name mindspeed-core \
  --privileged \
  --network host \
  --ipc=host \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v {path-to-data}:/data \
  -v {path-to-weights}:/weights \
  swr.cn-south-1.myhuaweicloud.com/ascendhub/mindspeed-core:v26.1.0_core_r0.12.1-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11 \
  bin/bash
```

> ⚠️ 必须将 `{path-to-data}` 与 `{path-to-weights}` 替换为宿主机真实路径，否则容器内 `/data`、`/weights` 将无法挂载。

### 6. 进入已启动容器（原文）

```bash
docker exec -it mindspeed-core /bin/bash
```

### 7. 代理透传（原文）

宿主机设置了 `http_proxy`、`https_proxy`、`HTTP_PROXY`、`HTTPS_PROXY`、`NO_PROXY`、`no_proxy` 时，构建脚本会自动转发给 Docker 构建过程，**但不会保留在最终镜像中**。

### 8. 兼容性说明中的关键配置项（原文）

- 默认基础镜像组合：**CANN 9.1.0 + 910b + openEuler 24.03 + Python 3.11**
- 可通过 `docker/build.sh` 切换：操作系统、NPU 类型（`a3`/`910b`/`950`）、目标架构、CANN 基础镜像版本
- 镜像内源码位置：**MindSpeed → `/MindSpeed`，Megatron-LM → `/Megatron-LM`**
- 安装顺序：PyTorch → TorchNPU → MindSpeed Core → Megatron-LM → `requirements.txt` 中 Python 依赖 → 恢复并校验 PyTorch/TorchNPU/NumPy 版本
