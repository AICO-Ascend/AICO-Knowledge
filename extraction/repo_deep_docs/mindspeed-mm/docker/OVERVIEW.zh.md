# MindSpeed MM Docker 镜像概述

> 仓 `mindspeed-mm` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docker/OVERVIEW.zh.md

# MindSpeed MM Docker 镜像概述 — 深度解读

## 【定位】

本篇文档是 `mindspeed-mm` 容器镜像的官方使用与维护说明，目的是让用户**理解镜像 Tag 命名规则、拉取/运行容器、在本地基于 Dockerfile 与 build.sh 自定义构建**，从而为昇腾芯片上的大规模多模态大模型训练提供一致的运行环境。

---

## 【技术要点】

1. **基础环境支持矩阵**：镜像基于 **Ubuntu 22.04** 与 **openEuler 24.03** 两种操作系统，支持 **x86_64** 与 **aarch64（ARM64）** 两种 CPU 架构，多架构（x86 + aarch64）以"二合一"形式分发。
2. **预装软件栈**：仅预装**基础依赖**——**PyTorch + TorchNPU**（深度学习框架）、**decord 0.6.0**（高效视频解码库）、**CANN**（华为昇腾 AI 处理器基础软件栈）。模型专属依赖**不在镜像内**，需进入容器后在 `base` 环境手动安装。
3. **Tag 命名模板**：`{版本号}-{CANN版本}-{TorchNPU版本}-{适用产品信息}-{操作系统}-{Python版本}`，共 6 字段，**全部必选、顺序不可调整、连接符固定为 `-`**。
4. **NPU 产品线覆盖**：通过 Tag 中的"适用产品信息"字段支持 **910b、a3、950** 三类昇腾 NPU 芯片（小写）。
5. **Tag 中架构后缀规则**：镜像仓库中的官方 Tag **不包含** `x86_64` / `aarch64` 后缀；只有通过 Dockerfile 本地构建才会生成带架构后缀的 Tag（如 `...-aarch64`、`...-x86_64`）。
6. **当前最新版本组合**：`v26.1.0` + `cann9.1.0` + `torch_npu2.7.1.post8`，覆盖 **910B/A3/950** 三种 NPU × **openeuler24.03/ubuntu22.04** 两种 OS = 共 6 个 Tag。
7. **构建系统分层**：`Dockerfile`（统一 dev 镜像，通过构建参数支持所有 NPU/OS） + `Dockerfile.ci`（在 dev 基础上叠加多版本 conda，通过 `--build-ci` 启用） + `build.sh`（参数化构建脚本）。
8. **容器运行必备设备映射**：NPU 设备 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`（950 系列额外需 `/dev/ummu`、`/dev/uburma`）以及 `/usr/local/dcmi`、`npu-smi`、Ascend driver 路径挂载。

---

## 【关键机制与数据】

### 镜像 Tag 模板机制（原文模板）

```
{版本号}-{CANN版本}-{TorchNPU版本}-{适用产品信息}-{操作系统}-{Python版本}
```

- **版本号**：`v` + 数字（v 表示 version，数字代表 Git 分支），如 `v26.1.0`（分支名 `26.1.0`）。
- **CANN 版本**：`cann` + 版本号，如 `cann9.1.0`。
- **TorchNPU 版本**：`torch_npu` + 版本号，如 `torch_npu2.7.1.post8`。
- **适用产品信息**：NPU 芯片类型小写，如 `910b`、`a3`、`950`。
- **操作系统**：`openeuler24.03` 或 `ubuntu22.04`。
- **Python 版本**：`py` + 版本号，如 `py3.11`。

### 构建脚本参数解析机制

- **CANN 版本、NPU 类型（910b/a3/950）、操作系统** —— **只能** 通过解析 `--base-image` 的 tag 自动获取，**不支持手动指定**。
- **Python 版本** —— 默认从 base 镜像 tag 自动识别，可通过 `--python-version` 覆盖。
- **TorchNPU 版本** —— 通过 `--torch-npu-version` 参数指定（默认值 `2.7.1.post8`）。
- **版本号（Git 分支）** —— 通过 `-v / --version` 指定，默认 `26.1.0`，同时作为 `git clone` 的分支名。

### 容器启动设备/路径挂载（原文示例）

- NPU 设备：`/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`
- 系统路径：`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info`
- 950 系列 aarch64 额外挂载：`/dev/davinci0`、`/dev/ummu`、`/dev/uburma`

---

## 【表格解读】

### 表 1：快速参考（原文逐字）

| 项目 | 说明 |
| ------ | ------ |
| **镜像名称** | mindspeed-mm |
| **维护者** | MindSpeed MM 团队 |
| **源码仓库** | [https://gitcode.com/Ascend/MindSpeed-MM](https://gitcode.com/Ascend/MindSpeed-MM) |
| **Dockerfile 路径** | `docker/` |
| **许可证** | Apache-2.0 |

**解读**：这是镜像的元信息索引表。其中 **Apache-2.0** 表明开源协议非常宽松，允许商用与修改；源码仓库与 Dockerfile 路径都指向了项目自身的 `docker/` 目录，暗示所有构建相关的脚本与说明都集中在该目录中维护。

---

### 表 2：镜像 Tag 字段描述（原文逐字）

| 字段 | 必选 | 说明 | 示例值 |
| ------ | ------ | ------ | -------- |
| 版本号 | 是 | MindSpeed MM 版本标识(v表示version，数字代表分支) | v26.0.0, v26.1.0 |
| CANN版本 | 是 | `cann` + 版本号 | cann9.1.0 |
| TorchNPU版本 | 是 | `torch_npu` + 版本号 | torch_npu2.7.1.post8 |
| 适用产品信息 | 是 | NPU 芯片类型（小写） | 910b, a3, 950 |
| 操作系统 | 是 | 操作系统 | openeuler24.03, ubuntu22.04 |
| Python版本 | 是 | `py` + 版本号 | py3.11 |

**解读**：每个字段都通过固定前缀（`cann`、`torch_npu`、`py`）或纯字符串（版本号、NPU 类型、OS）拼装，因此用户**仅凭 Tag 字符串即可解析出完整的运行时环境组合**，无需查表。"必选"列强调 6 字段缺一不可，意味着任何省略都会让镜像失去自描述能力。

---

### 表 3：示例 Tag（原文逐字）

| Tag | 版本号 | CANN | TorchNPU | NPU | 操作系统 | Python |
| ----- | ----- | ----- | ----- | ----- | --------- | -------- |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11` | v26.1.0 | 9.1.0 | 2.7.1.post8 | A3 | openEuler 24.03 | 3.11 |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11` | v26.1.0 | 9.1.0 | 2.7.1.post8 | 910B | openEuler 24.03 | 3.11 |

**解读**：两个示例展示同一版本（v26.1.0）、同一 CANN（9.1.0）、同一 TorchNPU（2.7.1.post8）、同一 OS（openEuler 24.03）、同一 Python（3.11）下，通过**NPU 类型字段切换**得到 A3 与 910B 两个不同 Tag。这验证了模板在"适用产品信息"维度上的可组合性——同一软件栈可针对不同昇腾硬件分发独立镜像。

---

### 表 4：Tag 含义说明（以 `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11` 为例，原文逐字）

| 字段 | 值 | 含义 |
| ------ | ------ | ------ |
| 版本号 | `v26.1.0` | MindSpeed MM Git tag（分支名：26.1.0） |
| CANN版本 | `cann9.1.0` | 基于 CANN 9.1.0 |
| TorchNPU版本 | `torch_npu2.7.1.post8` | TorchNPU 2.7.1.post8 |
| 适用产品信息 | `a3` | 适用于昇腾 A3 服务器 |
| 操作系统 | `openeuler24.03` | 基于 openEuler 24.03 |
| Python版本 | `py3.11` | Python 3.11 |

**解读**：该表进一步说明 Tag 中每个字段不只是字符串，而是**与 Git 分支、CANN 主版本号、TorchNPU 发布版、NPU 产品系列、Linux 发行版、Python 解释器一一映射的"语义标识"**。一旦发布就能让运维人员直接判断该镜像是否与目标服务器硬件兼容。

---

### 表 5：v26.1.0 所有 Tag（原文逐字）

| Tag | Dockerfile | 说明 |
| --- | --- | --- |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 910B + openEuler 24.03，x86_64/aarch64 二合一 |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 910B + Ubuntu 22.04，x86_64/aarch64 二合一 |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | A3 + openEuler 24.03，x86_64/aarch64 二合一 |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-ubuntu22.04-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | A3 + Ubuntu 22.04，x86_64/aarch64 二合一 |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 950 + openEuler 24.03，x86_64/aarch64 二合一 |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-ubuntu22.04-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 950 + Ubuntu 22.04，x86_64/aarch64 二合一 |

**解读**：本表是表 2 模板的**完整笛卡尔积实例化**——3 种 NPU（910b/a3/950）× 2 种 OS（openeuler24.03/ubuntu22.04）= 6 个 Tag。所有 Tag 都共用同一个 [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile)（指向 `26.1.0` 分支的 `docker/Dockerfile`），通过构建参数在同源文件上生成不同最终镜像，从而降低镜像维护成本。

---

### 表 6：内置环境（原文逐字）

| 环境 | 说明 | 工作目录 |
| ------ | ------ | --------- |
| base | 基础环境，包含 PyTorch、TorchNPU、decord、MindSpeed MM | /workspace/MindSpeed-MM |

**解读**：容器中只有一个 `base` conda 环境，预装 PyTorch + TorchNPU + decord + MindSpeed MM，工作目录固定为 `/workspace/MindSpeed-MM`。其他模型专属依赖需要用户进入该 base 环境后手动 pip/conda 安装，这体现了"基础环境 + 模型差异化扩展"的设计哲学。

---

### 表 7：构建脚本参数说明（原文逐字）

| 参数 | 说明 | 默认值 |
| ------ | ------ | ------------ |
| `--base-image` | **必选。** 完整基础镜像名称，CANN 版本、NPU 类型（910b/a3/950）、操作系统和 Python 版本均从镜像 tag 自动识别 | 无（必需） |
| `--python-version` | conda base 环境的 Python 版本（如 3.11/3.10/3.12）。用于选择对应的 Miniconda 安装器，最终决定 conda base 环境的 Python 版本 | 从 base 镜像 tag 自动识别 |
| `-v, --version` | MindSpeed MM 版本标识，同时作为 Git 分支名称 | 26.1.0 |
| `--tag` | 自定义镜像 tag（覆盖默认 tag；CI 构建自动追加 `-ci`） | 自动生成 |
| `-n, --no-cache` | 构建时不使用缓存 | 无 |
| `--torch-version` | PyTorch 版本（在线安装） | 2.7.1 |
| `--torch-npu-version` | TorchNPU 版本（在线安装） | 2.7.1.post8 |
| `--build-ci` | 在 dev 镜像基础上构建 CI 镜像（多版本 conda 环境），输出 tag 追加 `-ci` | 无 |
| `--cleanup-on-fail` | 构建失败时清理悬空镜像/容器 | 无 |

**解读**：`build.sh` 的设计核心是**"以 base 镜像为唯一可信源"**——CANN、NPU、OS、Python 都从 `--base-image` tag 解析，避免人为输入错配。TorchNPU 与 PyTorch 版本通过独立参数显式指定（默认值 `2.7.1` / `2.7.1.post8`）。`--build-ci` 是 dev→ci 的开关，决定是否在基础镜像上叠加多版本 conda。`--cleanup-on-fail` 提升构建容错性，自动清理失败构建残留。

---

## 【公式解读】

原文无数学公式，但含有一处**镜像 Tag 命名模板**（更接近字符串模式）：

```
{版本号}-{CANN版本}-{TorchNPU版本}-{适用产品信息}-{操作系统}-{Python版本}
```

**符号含义：**

| 占位符 | 含义 | 取值约束 |
| --- | --- | --- |
| `{版本号}` | MindSpeed MM 版本标识 | 以 `v` 开头，后跟数字（对应 Git 分支名） |
| `{CANN版本}` | 华为昇腾 AI 处理器基础软件栈版本 | 固定前缀 `cann` + 主版本号（如 `cann9.1.0`） |
| `{TorchNPU版本}` | TorchNPU 适配层版本 | 固定前缀 `torch_npu` + 版本号（含 post 修订号，如 `2.7.1.post8`） |
| `{适用产品信息}` | NPU 芯片系列 | 小写枚举值 `910b` / `a3` / `950` |
| `{操作系统}` | 宿主机操作系统 | `openeuler24.03` 或 `ubuntu22.04` |
| `{Python版本}` | Python 解释器版本 | 固定前缀 `py` + 主.次版本号（如 `py3.11`） |

**作用**：该模板既是**发布规范**（决定镜像仓库中 Tag 的合法性），也是**消费契约**（用户可依据 Tag 推断兼容矩阵）。同时也是 `build.sh` 自动生成 Tag 的算法依据。

---

## 【关联】

### 上游（依赖/支撑）

- **[CANN 版本配套网站](https://www.hiascend.com/developer/download/compatibility)** —— 用于查询宿主机 NPU 驱动与容器内 CANN 版本的兼容关系，是部署前置条件。
- **[镜像中心 / ascendhub](https://www.hiascend.com/developer/ascendhub)** —— 镜像分发仓库，用户通过搜索 `mindspeed-mm` 获取 `docker pull` 命令。
- **[mindspeed-mm 镜像中心详情页](https://www.hiascend.com/developer/ascendhub/detail/6857f6fc2cfa4a678710a7075426ee5e)** —— 当前 v26.1.0 系列镜像的拉取入口。
- **昇腾芯片主页 [hiAscend](https://www.hiAscend.com/)** —— 介绍 MindSpeed MM 所运行的硬件平台。

### 同级（同级模块/产物）

- **[Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile)** —— 统一的 dev 镜像构建文件，是所有 v26.1.0 Tag 的共同构建源。
- **[Dockerfile.ci](https://gitcode.com/Ascend/MindSpeed-MM)** —— CI 镜像构建文件（在 dev 上叠加多版本 conda）。
- **[Supported Tags](https://gitcode.com/Ascend/MindSpeed-MM/blob/master/docker/supported_tags.md)** —— 历史版本 Tag 完整列表。
- **[Ascend/MindSpeed-MM 源码仓库](https://gitcode.com/Ascend/MindSpeed-MM)** —— MindSpeed MM 主仓库，`docker/` 目录是本文档与所有构建产物的归属地。

### 下游（被使用/消费者）

- MindSpeed MM 各模型训练 README —— 用户进入容器后，**根据目标模型 README 在 base 环境中手动安装模型专属依赖**（原文反复强调）。
- `docker/build.sh` 脚本 —— 通过 `-v` 参数指定的版本号（默认 `26.1.0`）作为 `git clone MindSpeed-MM` 的分支名，从而把上游源码仓库与具体镜像构建流程串接起来。

---

## 【使用方法】

### 1. 拉取镜像（原文）

访问 ascendhub 搜索 `mindspeed-mm`，获取对应的 `docker pull` 命令。例：

```bash
docker pull mindspeed-mm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11
```

### 2. 通用运行命令（原文示例，910b/A3 系列）

```bash
docker run -it \
    --name mm_container \
    --device=/dev/davinci1 \
    --device=/dev/davinci_manager \
    --device=/dev/devmm_svm \
    --device=/dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /path/to/data:/data \
    -v /path/to/weights:/weights \
    mindspeed-mm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11 bash
```

### 3. 自定义驱动路径运行（原文示例）

若 NPU 驱动安装在非默认路径（如 `/usr/local/npu/driver`），需在 `docker run` 时追加：

```bash
docker run -it --rm \
    -e LD_LIBRARY_PATH="/usr/local/npu/driver/lib64/driver:/usr/local/npu/driver/lib64/common:$LD_LIBRARY_PATH" \
    mindspeed-mm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11 bash
```

### 4. 950 系列 aarch64 运行（原文示例）

```bash
docker run \
    --name mm_container \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/hisi_hdc \
    --device /dev/ummu \
    --device /dev/uburma \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -it mindspeed-mm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11 bash
```

### 5. 本地自定义构建（原文示例片段）

```bash
cd docker
# 构建 A3 + openEuler 镜像
bash build.sh --base-image sw...
```

> 文档原文此处命令被截断；可参照表 7 中所有 `build.sh` 参数完成完整构建调用，例如：
>
> ```bash
> bash build.sh \
>     --base-image ascendhub.huawei.com/.../cann9.1.0-a3-openeuler24.03-py3.11 \
>     --torch-version 2.7.1 \
>     --torch-npu-version 2.7.1.post8 \
>     -v 26.1.0
> ```

### 6. 容器内安装模型依赖（原文）

```bash
# 进入 base 环境后，根据目标模型 README 手动安装
pip install <model-specific-packages>
```

### 7. CI 镜像构建开关

```bash
bash build.sh --base-image <image> --build-ci
```

> 启用后会在 dev 镜像基础上叠加多版本 conda 环境，最终 tag 自动追加 `-ci` 后缀。

---

*注：原文 `bash build.sh --base-image sw...` 命令末尾在源文档中即被截断，本文在使用方法第 5 节中给出说明并参照表 7 参数补全示意，未引入未在原文出现的具体镜像地址。*
