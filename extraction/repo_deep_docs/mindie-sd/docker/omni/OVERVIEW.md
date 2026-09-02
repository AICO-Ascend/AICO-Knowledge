# MindIE-SD

> 仓 `mindie-sd` · 路径 `docker/omni/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docker/omni/OVERVIEW.md

# mindiesd Docker 镜像 Overview 深度解读

## 【定位】
本文档是 `mindiesd` 容器镜像（v3.0.0 版）的 **Quick Reference / Overview**，解决"如何在昇腾 Atlas 800I A2 / A3 SuperPoD 两种 NPU 上把 vLLM-Omni（多模态 LLM 推理）与 MindIE-SD（Stable Diffusion 文生图）一起跑起来"的问题：给出镜像标签、软件栈版本、硬件依赖、容器拉取/运行/构建命令，以及二次开发入口。

---

## 【技术要点】

1. **镜像身份与两条产品线**（原文 Quick Reference 表）：
   - 镜像名：`mindiesd`
   - A2 变体：`v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64`
   - A3 变体：`v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64`

2. **基础软件栈**（原文）：Ubuntu 22.04 · Python 3.11 · CANN 8.5.1 · TorchNPU 2.9.0 · 架构 `linux/arm64` (aarch64) · 许可 Mulan PSL v2。

3. **基镜像层级**（原文）：两变体均基于 `quay.io/ascend/vllm-omni`（A2 用 `v0.20.0`，A3 用 `v0.20.0-a3`），基镜像已包含 CANN 8.5.1、torch、TorchNPU、vllm、vllm_ascend；`mindiesd` 镜像在其上叠加 Atlas 调测工具。

4. **附加工具集**（原文 Components 表）：
   - `mindiesd`（latest）—— MindIE Stable Diffusion 推理引擎
   - `msprobe` 0.1.4 —— 精度调试工具
   - `msmodelslim` 8.2.1 —— 模型压缩与量化工具
   - `msprof-analyze` 26.0.0 —— MindStudio Profiler 分析工具
   - `msprof` —— 随 CANN 一起打包，NPU profiling 工具

5. **NPU 设备映射与主机挂载**（原文 docker run 命令）：须透传 4 张计算卡 `/dev/davinci0–3`，加管理设备 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`；需挂载 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info`、`/root/.cache`；并使用 `--privileged` 与 `--shm-size=1g`。

6. **镜像标签命名约定**（原文 Tag Naming Convention）：
   `{version}-{cann version}-{torch_npu version}-{supported product}-{os}-{python version}-{architecture}-{others}`

---

## 【关键机制与数据】

本文档是镜像 README 类型，**不涉及运行时推理机制、数据流走向、延迟/吞吐性能数字**——原文通篇未出现任何 benchmark、性能数据或模型加载链路描述。

唯一与"机制"相关的陈述（原文 Image Overview 一节）为：
> "This image combines **vLLM-Omni** and **MindIE-SD** (Mind Inference Engine Stable Diffusion) into a single container, enabling both multi-modal LLM inference and Stable Diffusion image generation on Atlas NPUs."

机制层面的"参数"只有版本号、镜像分层与挂载点列表（已并入【技术要点】与【表格解读】）。

---

## 【表格解读】

原文共 5 个表格，逐字还原并逐行解读如下。

### 表 1 —— Quick Reference（快速参考总览）

| Item | Value |
|------|-------|
| **Image** | `mindiesd` |
| **Tags** | `v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64` |
|  | `v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64` |
| **Base Images** | Atlas 800I A2 inference server: `quay.io/ascend/vllm-omni:v0.20.0` |
|  | Atlas 800I A3 SuperPoD Server: `quay.io/ascend/vllm-omni:v0.20.0-a3` |
| **Architecture** | `linux/arm64` (aarch64) |
| **OS** | Ubuntu 22.04 |
| **Python** | 3.11 |
| **CANN** | 8.5.1 |
| **TorchNPU** | 2.9.0 |
| **License** | Mulan PSL v2 |

**逐行解读**：
- **Image / Tags**：镜像名固定为 `mindiesd`，并给出 2 个产品专用 tag；标签字段直接编码了 CANN、torch_npu、产品代号、OS、Python、arch。
- **Base Images**：两个变体分别 inherit 自不同基镜像 `quay.io/ascend/vllm-omni:v0.20.0`（A2）与 `…v0.20.0-a3`（A3），说明 A2/A3 在 vLLM-Omni 侧本身就有差异基线。
- **Architecture / OS / Python / CANN / TorchNPU**：均为静态版本约束，确认仅支持 arm64 + Ubuntu 22.04 + Py3.11 + CANN 8.5.1 + TorchNPU 2.9.0 这条组合。
- **License**：镜像以 Mulan PSL v2 开源。

### 表 2 —— Components（叠加在基镜像之上的 Atlas 工具）

| Component | Version | Description |
|-----------|---------|-------------|
| mindiesd | latest | MindIE Stable Diffusion inference engine |
| msprobe | 0.1.4 | Precision debugging tool |
| msmodelslim | 8.2.1 | Model compression and quantization tool |
| msprof-analyze | 26.0.0 | MindStudio Profiler analysis tool |
| msprof | *(bundled with CANN)* | NPU profiling tool |

**逐行解读**：
- `mindiesd`（latest）即本次发布的核心推理引擎，无具体版本号（"latest"）。
- `msprobe 0.1.4`：精度比对/调试工具，用于排查 NPU 上的算子数值偏差。
- `msmodelslim 8.2.1`：模型压缩与量化工具，可对 SD/LLM 模型做量化以加速推理。
- `msprof-analyze 26.0.0`：MindStudio Profiler 的离线分析组件，对 profiling 结果做后处理。
- `msprof`：（bundled with CANN）随 CANN 自带，不单独标版本号。

### 表 3 —— Series × Base Image（系列与基镜像对应关系）

| Series | Example Tag | Base Image |
|--------|-------------|------------|
| Atlas 800I A2 inference server | `v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64` | `quay.io/ascend/vllm-omni:v0.20.0` |
| Atlas 800I A3 SuperPoD Server | `v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64` | `quay.io/ascend/vllm-omni:v0.20.0-a3` |

**逐行解读**：明确"A2 ↔ tag 中带 `910b`、基镜像 `v0.20.0`"，"A3 ↔ tag 中带 `a3`、基镜像 `v0.20.0-a3`"的对应关系；这是用户挑选镜像的唯一判据。

### 表 4 —— Dockerfile Path（v3.0.0 Dockerfile 路径）

| Series | Example Tag | Dockerfile |
|--------|-------------|------------|
| Atlas 800I A2 inference server | `v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64` | [Dockerfile](https://gitcode.com/Ascend/MindIE-SD/blob/master/docker/omni/Dockerfile.a2.ubuntu) |
| Atlas 800I A3 SuperPoD Server | `v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64` | [Dockerfile](https://gitcode.com/Ascend/MindIE-SD/blob/master/docker/omni/Dockerfile.a3.ubuntu) |

**逐行解读**：A2 Dockerfile 名 `Dockerfile.a2.ubuntu`、A3 名 `Dockerfile.a3.ubuntu`，均归档在 MindIE-SD 仓库的 `docker/omni` 目录下（即本 overview 所在目录的同级）。

### 表 5 —— Hardware Support（硬件支持与主机必备挂载）

| Item | Requirement |
|------|-------------|
| **NPU** | Atlas 800I A2 inference server |
|  | Atlas 800I A3 SuperPoD Server |
| **Driver** | Atlas NPU driver must be installed on the host |
| **Host Mounts** | `/usr/local/dcmi`, `/usr/local/bin/npu-smi`, `/usr/local/Ascend/driver/lib64/`, `/usr/local/Ascend/driver/version.info`, `/etc/ascend_install.info`, `/root/.cache` |

**逐行解读**：
- **NPU**：明确仅支持 A2 inference server 与 A3 SuperPoD 两条产品线。
- **Driver**：宿主机必须先装好 Atlas NPU 驱动；容器内不自带驱动，靠挂载复用。
- **Host Mounts**：6 个挂载点是 NPU 设备发现 + DCMI 管理 + 模型缓存所必需的，缺一不可（与 `docker run` 命令中的 `-v` 一一对应）。

---

## 【公式解读】

**原文无数学公式**。

唯一接近"模板/伪代码"的标记是镜像标签命名约定（原文 Tag Naming Convention 节）：

```text
{version}-{cann version}-{torch_npu version}-{supported product}-{os}-{python version}-{architecture}-{others}
```

逐符号解读（按字段出现顺序）：
- `{version}` —— 镜像版本，此处对应 `v3.0.0`。
- `{cann version}` —— CANN 版本，此处为 `cann8.5.1`。
- `{torch_npu version}` —— TorchNPU 版本，此处为 `torch_npu2.9.0`。
- `{supported product}` —— 适配产品代号：`910b`（A2）或 `a3`（A3 SuperPoD）。
- `{os}` —— 操作系统版本：`ubuntu22.04`。
- `{python version}` —— Python 版本：`py3.11`。
- `{architecture}` —— CPU 架构：`aarch64`。
- `{others}` —— 预留扩展位（当前实际 tag 未使用）。

---

## 【关联】

原文未提供内部链接清单，但据文中提及可梳理如下关联：

- **基镜像**：`quay.io/ascend/vllm-omni`（v0.20.0 / v0.20.0-a3）—— `mindiesd` 镜像直接在它之上叠加 Atlas 调测工具与 mindiesd 推理引擎；这是 vLLM-Omni 多模态推理能力的来源。
- **同级 Dockerfile**：`docker/omni/Dockerfile.a2.ubuntu` 与 `docker/omni/Dockerfile.a3.ubuntu`，与本 OVERVIEW.md 同目录，是镜像的实际构建定义。
- **上游项目**：
  - MindIE 社区 / [MindIE image repository](https://www.hiascend.com/developer/ascendhub/detail/af85b724a7e5469ebd7ea13c3439d48f)
  - [MindIE-SD documentation](https://gitcode.com/Ascend/MindIE-SD/blob/master/docs/en/index.md)（兼容性变更指向这里）
- **辅助工具链**：msprobe / msmodelslim / msprof-analyze / msprof 是镜像内置的配套调测工具，可与 mindiesd / vLLM-Omni 协同做精度与性能分析。
- **支持入口**：[Atlas Developer Community](https://www.hiascend.com/developer) 与 [Issue feedback](https://gitcode.com/Ascend/MindIE-SD/issues)。

---

## 【使用方法】

### 1. 拉取基镜像（原文 Quick Start → Pull Base Image）

Atlas 800I A2 inference server：
```bash
docker pull quay.io/ascend/vllm-omni:v0.20.0
```

Atlas 800I A3 SuperPoD Server：
```bash
docker pull quay.io/ascend/vllm-omni:v0.20.0-a3
```

> 原文 Tip：`podman pull` 可替代 `docker pull`。

### 2. 运行容器（原文 Run the Container）

A2 完整启动命令（原文逐字保留关键 flag）：

```bash
docker run -it --rm --name=mindiesd \
    --privileged \
    --shm-size=1g \
    --device /dev/davinci0 \
    --device /dev/davinci1 \
    --device /dev/davinci2 \
    --device /dev/davinci3 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64 \
    bash
```

A3 SuperPoD 命令结构完全相同，仅把镜像名替换为 `mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64`。

> 原文 Note：`--privileged` 与 device 映射为 NPU 访问必需；宿主机必须挂载驱动库、driver version info、DCMI、`npu-smi`、Atlas install info。

### 3. 本地构建（原文 Build Locally）

A2：
```bash
git clone https://gitcode.com/Ascend/MindIE-SD.git
cd MindIE-SD/docker/omni

docker build -t mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64 \
    -f Dockerfile.a2.ubuntu .
```

A3：把 tag 与 `-f Dockerfile.a3.ubuntu` 对应替换即可。

### 4. 二次开发 / 自定义（原文 Customize）

```dockerfile
FROM mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64

# Add your custom packages
RUN pip install --no-cache-dir your-package

# Copy your application
COPY ./your-app /workspace/your-app
WORKDIR /workspace/your-app
```

### 5. 兼容性变更
原文未在本文列出具体变更条目，仅指向 [MindIE-SD documentation](https://gitcode.com/Ascend/MindIE-SD/blob/master/docs/en/index.md) 获取 release notes 与兼容性信息。

### 6. 许可
- 镜像许可：**Mulan Permissive Software License, Version 2 (Mulan PSL v2)**（完整文本见仓库 [LICENSE.md](https://gitcode.com/Ascend/MindIE-SD/blob/master/LICENSE.md)）。
- 容器使用须遵守 **Huawei Container License Agreement**（https://www.hiascend.com/en/legal/ascendhub-download ）；镜像内含的华为或第三方软件须各自遵守其协议。
