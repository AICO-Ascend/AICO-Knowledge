# MindSpeed LLM Docker 镜像概述

> 仓 `mindspeed-llm` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docker/OVERVIEW.zh.md

# MindSpeed LLM Docker 镜像 Overview 文档深度解读

## 【定位】

本篇文档解决"如何构建、识别、拉取和运行 MindSpeed LLM 在昇腾 NPU 上的 Docker 镜像"这一具体工程问题，给出一份涵盖镜像 Tag 命名规则、多架构(NPU/OS/Python/CANN)矩阵、本地构建脚本参数、容器启动方式及二次开发模板的端到端说明。

---

## 【技术要点】

1. **Tag 命名规范 (原文):** 所有镜像 Tag 遵循 `v{MindSpeed LLM版本}-cann{CANN版本}-torch_npu{TorchNPU版本}-{芯片信息}-{操作系统}-py{Python版本}`，且最新 Tag 是 `x86_64` 与 `aarch64` 二合一的多架构镜像，**不带** `-x86_64` / `-aarch64` 后缀；本地构建默认会生成带宿主机架构后缀的 Tag。
2. **多维度构建参数矩阵 (原文):** `image_build.sh` 支持 `--npu-type` (`910b`/`a3`/`950`)、`--os` (`openeuler24.03`/`ubuntu22.04`)、`--mindspeed-llm-branch`、`--mindspeed-branch`、`--megatron-branch`、`--python-version`、`--torch-version`、`--torch-npu-version`、`--triton-ascend-version`、`--fla-npu-branch`、`--base-image-version`、`--base-image`、`--cleanup-on-fail`、`--no-cache` 等参数；默认值与最新发布 Tag 保持一致（即 `910b` / `openeuler24.03` / `26.1.0` / `26.1.0_core_r0.12.1` / `core_v0.12.1` / `3.12` / `2.7.1` / `2.7.1.post8` / `3.2.2` / `v26.1.0` / `9.1.0`）。
3. **FLA NPU 算子编译 (原文):** 构建过程会在 clone `flash-linear-attention-npu` 后自动 source CANN 环境并编译 GDN 自定义算子 run 包与 `torch_custom/fla_npu` whl 包；算子列表集中在 `docker/image_build.sh` 的 `FLA_NPU_OPS` 数组中，新增算子只需追加即可，自动拼接为 `build.sh --ops` 逗号分隔参数。
4. **硬件→SOC 自动映射 (原文):** `--soc` 默认按机型映射：`910b → ascend910b`、`a3 → ascend910_93`、`950 → ascend950`；可通过 `--fla-npu-soc` 显式覆盖（例如 `bash image_build.sh --fla-npu-soc ascend910_93`）。
5. **容器运行设备清单 (原文):** 启动容器需挂载 `--device=/dev/davinci1`、`/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm` 四个设备，并 `-v` 挂载 `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/sbin/npu-smi`、`/etc/ascend_install.info` 等主机路径；常用卷挂载还包括 `/home/`、`/data`、`/mnt`。
6. **基础环境预装策略 (原文):** 镜像内仅预装 `PyTorch` 与 `TorchNPU` 基础依赖，针对特定模型需要手动安装依赖；`base` 环境默认工作目录为 `/workspace/MindSpeed-LLM`，并已包含 MindSpeed-LLM、MindSpeed、Megatron-LM、FSDPTurbo、Triton-Ascend。

---

## 【关键机制与数据】

### 镜像 Tag 机制 (原文)

最新发布版本 `26.1.0` 共发布 6 个 Tag，对应 `910b / a3 / 950 × openeuler24.03 / ubuntu22.04` 的笛卡尔积，每个 Tag 均为 `x86_64` + `aarch64` 双架构 manifest 合并镜像。Tag 中的 "芯片信息" 必须使用小写 (`910b`/`a3`/`950`)。

### 软件栈版本基线 (原文)

26.1.0 发布版本基线：CANN 9.1.0 / PyTorch 2.7.1 / Triton-Ascend 3.2.2 / MindSpeed `26.1.0_core_r0.12.1` / MindSpeed-LLM 26.1.0 / Megatron-LM `core_v0.12.1` / FSDPTurbo main。

> 注：文档"软件栈"表格中将 `TorchNPU` 记为 `26.1.0`，而 Tag 与构建参数中 TorchNPU 安装包版本为 `2.7.1.post8`——此处**原文存在字段不一致**，按原文如实保留两套数值。

### 自动下载机制 (原文)

- 当 `--base-image` 被指定且本地不存在时自动拉取；其中"芯片信息"必须小写；
- 未指定 `--npu-type` 时脚本会从基础镜像 Tag 自动识别 `910b` / `a3` / `950` 三种 NPU 类型；
- 完整 `--base-image` 会原样传入拉取命令，因此其 tag 必须与已发布的 CANN 镜像名完全一致。

### 二次开发继承机制 (原文)

`FROM mindspeed-llm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.12` 作为父镜像，通过 `RUN pip install` 添加业务包 + `COPY` 注入代码 + `WORKDIR` 设定工作目录。

### 性能数据 (原文)

原文未提供任何 benchmark、吞吐量、显存占用或训练性能数字。

---

## 【表格解读】

### 表 1：快速参考表 (项目元数据)

| 项目 | 说明 |
| ------ | ------ |
| **镜像名称** | mindspeed-llm |
| **维护者** | MindSpeed LLM 团队 |
| **源码仓库** | https://gitcode.com/Ascend/MindSpeed-LLM |
| **Dockerfile 路径** | `docker/Dockerfile` |
| **许可证** | Apache-2.0 |
| **问题反馈** | Issue Feedback |

**逐行解读：**
- **镜像名称** `mindspeed-llm` 为 docker pull 与 docker run 的 `REPOSITORY` 部分。
- **Dockerfile 路径** 集中在仓库内的 `docker/Dockerfile`，即"统一 Dockerfile，支持多 NPU 类型"的归档位置。
- **许可证** Apache-2.0，意味着二次开发与商用均无附加限制。
- **问题反馈** 走 GitCode 的 Issue 入口而非 GitHub，与仓库托管位置一致。

### 表 2：Tag 格式字段表

| 字段 | 示例值 | 说明 |
| ------ | ------ | -------- |
| MindSpeed LLM版本 | `26.1.0` | MindSpeed LLM 版本标识，同时也是 Git 分支名称 |
| CANN版本 | `9.1.0` | CANN 基础镜像版本 |
| TorchNPU版本 | `2.7.1.post8` | TorchNPU 安装包版本 |
| 芯片信息 | `910b`, `a3`, `950` | NPU 芯片类型（小写） |
| 操作系统 | `openeuler24.03`, `ubuntu22.04` | 操作系统类型 |
| Python版本 | `3.12` | Python 版本 |

**逐行解读：**
- 该表是解析 Tag 字符串的反向字典，每个字段都对应构建参数 `--base-image-version` / `--torch-npu-version` / `--npu-type` / `--os` / `--python-version` / `--mindspeed-llm-branch`。
- "芯片信息"与 Git 分支名的双重身份（既是版本也是分支）保证了源码版本与运行时镜像的强一致——构建过程会按这些值直接 checkout 对应分支。

### 表 3：26.1.0 版本多架构 Tag 矩阵

| Tag | Dockerfile | Content |
| --- | --- | --- |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |

**逐行解读：**
- 6 个 Tag 都指向**同一个** `26.1.0` 标签下的 `docker/Dockerfile`——印证了"统一 Dockerfile + 构建脚本结构"的设计：差异完全由构建参数决定，而不是多份 Dockerfile。
- 行间差异只有第 4 段（芯片）与第 5 段（OS）：芯片 ∈ {`910b`, `a3`, `950`}，OS ∈ {`openeuler24.03`, `ubuntu22.04`}，呈现 3 × 2 笛卡尔积。
- Content 列完全相同，意味着无论选哪种芯片/OS，运行时关键软件栈一致：CANN 9.1.0 / PyTorch 2.7.1 / Triton-Ascend 3.2.2 / Megatron-LM `core_v0.12.1` / FSDPTurbo `main`。

### 表 4：image_build.sh 构建参数表

| 参数 | 说明 | 默认值 |
| ------ |-------------------------------------| ------------ |
| `-t, --npu-type` | NPU 类型：`910b`、`a3` 或 `950` | `910b` |
| `-o, --os` | 操作系统：`openeuler24.03`或`ubuntu22.04` | `openeuler24.03` |
| `--no-cache` | 构建时不使用 Docker 构建缓存 | 无 |
| `--mindspeed-llm-branch` | MindSpeed LLM 版本标识，同时作为 Git 分支名称 | `26.1.0` |
| `--mindspeed-branch` | MindSpeed 版本标识，同时作为 Git 分支名称 | `26.1.0_core_r0.12.1` |
| `--megatron-branch` | Megatron-LM 版本标识，同时作为 Git 分支名称 | `core_v0.12.1` |
| `--python-version` | Python 版本 | `3.12` |
| `--torch-version` | PyTorch 版本 | `2.7.1` |
| `--torch-npu-version` | TorchNPU 安装包版本 | `2.7.1.post8` |
| `--triton-ascend-version` | Triton-Ascend 版本 | `3.2.2` |
| `--fla-npu-branch` | flash-linear-attention-npu 分支 | `v26.1.0` |
| `--base-image-version` | 基础镜像 CANN 版本 | `9.1.0` |
| `--base-image` | 完整基础镜像名称，当设置不为空时会原样传入拉取镜像 | 无 |
| `--cleanup-on-fail` | 构建失败时清理悬空的镜像和容器 | 无 |

**逐行解读：**
- 该参数表是表 2 的"反向工程"：每个 Tag 字段对应一个 CLI 参数；默认值与 26.1.0 Tag 完全一致，保证 `bash image_build.sh` 在干净环境直接得到等价镜像。
- `--base-image` 是"完全覆盖型"参数：设置后整个基础镜像名被原样传给 docker pull，因此其内部 tag 必须与华为云已发布的 CANN 镜像名（例如 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.12`）逐字一致。
- `--cleanup-on-fail` 与 `--no-cache` 是"行为开关"型参数，无默认值即意味着"不做"；前者用于失败清理，后者用于确保缓存不污染。

### 表 5：FLA NPU --soc 默认映射

| 机型 | FLA NPU `--soc` |
| ------ | ------ |
| `910b` | `ascend910b` |
| `a3` | `ascend910_93` |
| `950` | `ascend950` |

**逐行解读：**
- 该映射决定了 `build.sh`（FLA NPU 仓库的算子编译脚本）在编译自定义算子时使用的 SoC 目标；同名 SoC 字符串是 CANN 编译工具链的合法 target 名。
- 用户可通过 `--fla-npu-soc` 覆盖默认映射，相当于绕过表格的隐式约定改成显式指定。

### 表 6：内置环境表

| 环境 | 说明 | 工作目录 |
| ------ | ------ | --------- |
| base | 基础环境，包含`PyTorch`，`TorchNPU`，`MindSpeed LLM`，`MindSpeed`，`Megatron-LM`，`FSDPTurbo`，`Triton-Ascend` | `/workspace/MindSpeed-LLM` |

**逐行解读：**
- 镜像只显式声明一个 conda/venv 环境 `base`，所有前述组件均安装到此环境，即前文"仅预安装了 PyTorch、TorchNPU 基础依赖包"与此处"包含…7 个组件"看起来有出入——按原文两段均在文档中出现，反映了不同段落描述的不同粒度（基础软件 vs. 完整运行时）。
- 工作目录硬编码为 `/workspace/MindSpeed-LLM`，意味着容器启动后默认 git 工作区指向仓库根；二次开发时通常直接在此目录或其子目录操作。

### 表 7：软件栈表 (原文)

| 组件 | 版本 |
| ------ |----------|
| CANN | 9.1.0 |
| Python | 3.12 |
| PyTorch | 2.7.1 |
| TorchNPU | 26.1.0 |
| Triton-Ascend | 3.2.2 |
| MindSpeed LLM | 26.1.0 |

**逐行解读：**
- 此表是"最终运行时"语义层面的依赖快照；与表 3 的 Content 列相比，缺了 MindSpeed / Megatron-LM / FSDPTurbo 三项。
- TorchNPU 行写 `26.1.0`，与上文出现过的 `2.7.1.post8` 不一致——保留原文如实呈现，提示读者此处可能为字段笔误或与发布 Tag 中 TorchNPU 安装包版本的命名口径不同。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 docker/ 目录其他文件的关系：** 文档中给出的目录树显示 `Dockerfile`、`image_build.sh`、`configure_yum_repo.sh`、`configure_apt_repo.sh`、`supported_tags.md`、`OVERVIEW.md`、`OVERVIEW.zh.md` 共 7 个文件，本文是 `OVERVIEW.zh.md`，作为中文版的总览入口。其余文件分别承担：构建入口 (`image_build.sh`)、历史 Tag 索引 (`supported_tags.md`)、两类 OS 软件源适配 (`configure_yum_repo.sh`/`configure_apt_repo.sh`)，最终都通过 `Dockerfile` 组合生成镜像。
- **与上游基础镜像的关系：** 通过 `--base-image` / `--base-image-version` 参数注入 CANN 基础镜像（默认取自 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann` 仓库、`9.1.0` 版本），是镜像栈最底层的依存；CANN 决定硬件抽象层行为。
- **与下游算法仓库的关系：** 三个 Git 分支参数 (`--mindspeed-llm-branch`、`--mindspeed-branch`、`--megatron-branch`) 直接 checkout MindSpeed-LLM、MindSpeed、Megatron-LM 三处源码；意味着 `26.1.0` 镜像基线锁定了这三个仓库在 26.1.0 时刻的可复现状态。
- **与并行计算栈的关系：** 镜像同时预装 `FSDPTurbo`（`main` 分支）与 `MindSpeed`，两者配合 MindSpeed-LLM 形成分布式训练能力，与文档开头"分布式预训练、分布式指令微调"的套件定位一致。
- **与算子扩展仓库的关系：** `flash-linear-attention-npu`（`--fla-npu-branch` / `--fla-npu-soc`）提供 GDN 等自定义算子，在构建阶段 source CANN 环境后被自动编译进镜像，运行阶段即可使用。
- **内部链接说明：** 文档提示"内部链接: (无)"——本文档不包含同仓库内的相对路径引用跳转，所有外部 GitCode 链接均已在上述原始 markdown 中完整列出。

---

## 【使用方法】

### 本地构建（原文命令）

```bash
cd docker

# 使用全部默认值构建（910b + openEuler24.03）
bash image_build.sh

# 自定义 NPU 类型和操作系统
bash image_build.sh -t 950 -o ubuntu22.04

# 自定义 CANN、PyTorch 和 TorchNPU 软件包版本
bash image_build.sh \
  --base-image-version 9.1.0 \
  --torch-version 2.7.1 \
  --torch-npu-version 2.7.1.post8

# 修改源码分支
bash image_build.sh \
  --mindspeed-llm-branch 26.1.0 \
  --mindspeed-branch 26.1.0_core_r0.12.1 \
  --megatron-branch core_v0.12.1

# 修改输出镜像名称
bash image_build.sh -i myproject/mindspeed-llm:custom
```

```bash
# 指定 910b 基础镜像，脚本会自动识别 NPU 类型
cd docker
bash image_build.sh \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.12
```

```bash
bash image_build.sh --fla-npu-soc ascend910_93
```

### 运行容器（原文命令）

```bash
# 基本运行
docker run -it --rm \
  mindspeed-llm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.12 bash

# 使用 NPU 设备运行（示例：设备 /dev/davinci1）
docker run -it --rm \
  --name mindspeed-llm \
  --privileged \
  --network host \
  --ipc=host \
  --device=/dev/davinci1 \
  --device=/dev/davinci_manager \
  --device=/dev/hisi_hdc \
  --device=/dev/devmm_svm \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /home/:/home/ \
  -v /data:/data \
  -v /mnt:/mnt \
  mindspeed-llm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.12 \
  /bin/bash

# 进入已启动容器
docker exec -it mindspeed-llm /bin/bash
```

### 二次开发（原文 Dockerfile 模板）

```dockerfile
FROM mindspeed-llm:v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.12

RUN pip install your-package==1.0.0

COPY . /workspace/your-project

WORKDIR /workspace/your-project
```

```bash
docker build -t my-mindspeed-app:latest .
docker run -it --rm \
  --device=/dev/davinci1 \
  --device=/dev/davinci_manager \
  --device=/dev/devmm_svm \
  --device=/dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  my-mindspeed-app:latest bash
```

> 模型级依赖安装、训练启动方式等下游用法，原文明确**未涉及**，仅声明"需根据目标模型的 README 文件，在 base 环境中手动安装该模型所需的依赖环境"。
