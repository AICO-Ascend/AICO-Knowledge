# TorchNPU

> 仓 `pytorch` · 路径 `docker/OVERVIEW_26.0.0.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docker/OVERVIEW_26.0.0.md

# TorchNPU Overview 26.0.0 深度解读

## 【定位】

这篇文档是 TorchNPU Docker 镜像（26.0.0 系列）的总览文档，核心解决"如何在昇腾 Atlas NPU 上以 Docker 镜像形式部署 PyTorch 框架"的问题——即通过规范化的镜像标签、构建参数与运行配置，使用户能够快速拉取、构建并运行适配昇腾 AI 处理器的 PyTorch 容器化开发环境。

---

## 【技术要点】

1. **插件定位**：TorchNPU 是基于 Atlas 的深度学习适配框架（plugin），使 Atlas NPU 支持 PyTorch 框架，从而为 PyTorch 用户提供 Atlas AI 处理器算力。
2. **镜像标签规范**：遵循 `<TorchNPU_version>-<CANN_version>-<chip>-<os>-<python_version>` 五段式命名格式。
3. **支持四类 TorchNPU 版本**：2.10.0、2.9.0.post2、2.8.0.post4、2.7.1.post4；CANN 统一为 9.0.0；Python 统一为 py3.11；OS 支持 ubuntu22.04 与 openeuler24.03；芯片覆盖 310p、910b、a3。
4. **Dockerfile 构建参数**：12 个参数（10 个必填 + 2 个可选），其中 `TORCH_VERSION=2.10.0`、`CANN_VERSION=9.0.0`、`PY_TAG=cp311`、`TORCH_NPU_RELEASE_TAG=v26.0.0-pytorch2.10.0`、`TORCH_NPU_PATCH_TAG=2.10.0`。
5. **容器运行设备挂载**：需挂载 `/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 设备文件，以及 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info` 主机目录/文件。
6. **支持的硬件产品**：Atlas 800T A2、Atlas 900 A2 PoD、Atlas 800T A3、Atlas 300I Pro、Atlas 300V Pro，统一架构为 ARM64 / x86_64。

---

## 【关键机制与数据】

### 工作原理（基于原文推断的工作流）

- **镜像标签机制**：通过五段式标签将 TorchNPU 版本、CANN 工具链版本、芯片型号、操作系统、Python 版本信息编码到镜像名称中，便于用户精准选择所需组合。
- **构建参数映射**：Dockerfile 构建参数 `TORCH_NPU_RELEASE_VERSION=v26.0.0-pytorch2.10.0` 与 `TORCH_NPU_PATCH_TAG=2.10.0` 共同从官方 wheel 包下载 URL 解析得到——前者取 `download/` 与 `/torch_npu-` 之间，后者取 `torch_npu-` 与 `-cp310` 之间。
- **二次开发机制**：通过 `FROM quay.io/ascend/torch-npu:2.10.0-cann9.0.0-910b-ubuntu22.04-py3.11` 作为基础镜像叠加用户自定义软件（如 `apt install gcc`）。

### 关键数据（原文标注）

- 原文：镜像标签示例共 **24 个**（4 个 TorchNPU 版本 × 3 种芯片 × 2 种 OS）。
- 原文：完整 wheel 包 URL 范例 `https://gitcode.com/Ascend/pytorch/releases/download/v26.0.0-pytorch2.10.0/torch_npu-2.10.0-cp310-cp310-manylinux_2_28_aarch64.whl`。
- 原文：默认 pip 镜像源为清华源 `https://pypi.tuna.tsinghua.edu.cn/simple`；manylinux 版本默认为 `manylinux_2_28`。

---

## 【表格解读】

### 表格 1：Tag Specification（标签字段说明）

| Field            | value                                                   | Description                                       |
|------------------|---------------------------------------------------------|---------------------------------------------------|
| TorchNPU Version | 2.10.0                                                  | For details, see the version notes in the readme. |
| CANN_version     | 9.0.0                                                   | For details, see the version notes in the readme. |
| Chip             | Specific example values can be found in the CANN mirror | chip model identifier                             |
| OS               | ubuntu22.04 / openeuler24.03                            | OS distribution used for the base image           |
| Python Version   | py3.11                                                  | Major Python version pre-installed in the image   |

**逐行解读**：
- TorchNPU Version=2.10.0：表示该文档主线版本是 TorchNPU 2.10.0，详细说明需查阅 readme。
- CANN_version=9.0.0：表示配套使用的 CANN（昇腾异构计算架构）工具链版本为 9.0.0。
- Chip：表示芯片型号标识符，具体可选值需在 CANN 镜像仓库中查询（310p/910b/a3 在后文标签中出现）。
- OS=ubuntu22.04/openeuler24.03：表示基础镜像的操作系统发行版，可选 Ubuntu 22.04 或 openEuler 24.03。
- Python Version=py3.11：表示镜像预装的主版本 Python 为 3.11。

### 表格 2：Dockerfile build parameters（Dockerfile 构建参数）

| parameters                | Description                                               | Required | Reference Source          | Value                                                   |
|---------------------------|-----------------------------------------------------------|----------|---------------------------|---------------------------------------------------------|
| TORCH_VERSION             | Full TorchNPU version number                              | Yes      | TorchNPU repo releases    | 2.10.0                                                  |
| CHIP_ARCH                 | chip architecture identifier                              | Yes      | CANN image tag rules      | Specific example values can be found in the CANN mirror |
| OS                        | Base image operating system                               | Yes      | CANN image tag rules      | ubuntu / openeuler                                      |
| OS_VERSION                | Operating system version                                  | Yes      | CANN image tag rules      | 22.04 / 24.03                                           |
| PY_VERSION                | Python version pre-installed in base image                | Yes      | CANN image tag rules      | 3.11                                                    |
| CANN_VERSION              | CANN toolkit version                                      | Yes      | CANN base image repo      | 9.0.0                                                   |
| ARCH                      | Host hardware architecture                                | Yes      | Environment hardware      | arm / x86                                               |
| PY_TAG                    | Python package ABI tag (cp + version number)              | Yes      | Strictly match PY_VERSION | cp311                                                   |
| TORCH_NPU_RELEASE_VERSION | Official TorchNPU release tag (including PyTorch version) | Yes      | TorchNPU repo releases    | v26.0.0-pytorch2.10.0                                   |
| TORCH_NPU_PATCH_TAG       | TorchNPU version number in the release package name       | Yes      | TorchNPU repo releases    | 2.10.0                                                  |
| MANYLINUX_VER             | PyPI package compatible system version                    | No       | torch official wheel spec | manylinux_2_28                                          |
| PIP_MIRROR_URL            | pip installation source URL (Tsinghua mirror by default)  | No       | PyPI mirror sources       | https://pypi.tuna.tsinghua.edu.cn/simple                |

**逐行解读**：
- TORCH_VERSION=2.10.0（必填）：TorchNPU 完整版本号，来源于 TorchNPU 仓库 release。
- CHIP_ARCH（必填）：芯片架构标识，参考 CANN 镜像标签规则。
- OS=ubuntu/openeuler（必填）：基础镜像操作系统类型。
- OS_VERSION=22.04/24.03（必填）：操作系统版本号，与 OS 字段联动。
- PY_VERSION=3.11（必填）：预装 Python 版本，需与 PY_TAG 严格匹配。
- CANN_VERSION=9.0.0（必填）：CANN 工具链版本，来源于 CANN 基础镜像仓库。
- ARCH=arm/x86（必填）：宿主机硬件架构。
- PY_TAG=cp311（必填）：Python 包 ABI 标签（cp + Python 版本号），必须严格匹配 PY_VERSION。
- TORCH_NPU_RELEASE_VERSION=v26.0.0-pytorch2.10.0（必填）：官方 TorchNPU 发布 tag，包含 PyTorch 版本号。
- TORCH_NPU_PATCH_TAG=2.10.0（必填）：release 包名中的 TorchNPU 版本号。
- MANYLINUX_VER=manylinux_2_28（可选）：PyPI 包兼容的系统版本。
- PIP_MIRROR_URL=清华源（可选）：pip 安装源地址，默认使用清华镜像。

### 表格 3：Supported Hardware（支持的硬件）

| Product Examples                | Architecture   |
|---------------------------------|----------------|
| Atlas 800T A2, Atlas 900 A2 PoD | ARM64 / x86_64 |
| Atlas 800T A3                   | ARM64 / x86_64 |
| Atlas 300I Pro, Atlas 300V Pro  | ARM64 / x86_64 |

**逐行解读**：
- 第一行：Atlas 800T A2 与 Atlas 900 A2 PoD 是训练/推理型服务器级产品，宿主机可采用 ARM64 或 x86_64。
- 第二行：Atlas 800T A3 是新一代训练服务器，同样兼容两种架构。
- 第三行：Atlas 300I Pro、Atlas 300V Pro 是推理卡（边缘/数据中心推理场景），同样兼容两种架构。

---

## 【公式解读】

原文无数学公式，但存在一个**镜像标签命名格式规范**（类公式化定义）：

```text
<TorchNPU_version>-<CANN_version>-<chip>-<os>-<python_version>
```

**符号逐位解读**：
- `<TorchNPU_version>`：TorchNPU 插件版本号，例如 `2.10.0`、`2.9.0.post2`。
- `<CANN_version>`：CANN 工具链版本号，例如 `9.0.0`。
- `<chip>`：芯片型号标识符，例如 `310p`、`910b`、`a3`。
- `<os>`：操作系统发行版与版本，例如 `ubuntu22.04`、`openeuler24.03`。
- `<python_version>`：Python 主版本标识，例如 `py3.11`。
- 连字符 `-`：作为字段分隔符，不可省略。

完整示例：`2.10.0-cann9.0.0-a3-ubuntu22.04-py3.11` 表示 TorchNPU 2.10.0 + CANN 9.0.0 + a3 芯片 + Ubuntu 22.04 + Python 3.11 的组合。

---

## 【关联】

文末内部链接 `./OVERVIEW_26.0.0.zh.md`（中文版概述文档）与本英文文档互为镜像翻译版本，提供同一份内容的中文呈现，便于不同语言使用者查阅同一版本镜像信息。

文档通过外部链接与其他昇腾生态模块产生关联：
- **Atlas PyTorch 社区**（https://www.hiascend.com/developer/software/ai-frameworks/pytorch）：TorchNPU 的维护主体，决定版本演进节奏。
- **Image Repository / AscendHub**（https://www.hiascend.com/developer/ascendhub）：镜像托管来源，与 `quay.io/ascend/torch-npu:*` 标签体系互补。
- **TorchNPU 官方文档**（https://www.hiascend.com/document/detail/zh/Pytorch/730/index/index.html）：API 与算子映射详细手册。
- **CANN 基础镜像仓库**（https://quay.io/repository/ascend/cann?tab=tags）：提供 chip、OS、Python 等参数的实际可选值，是 `CHIP_ARCH`、`OS`、`OS_VERSION`、`PY_VERSION`、`CANN_VERSION` 的取数源头。
- **TorchNPU Release 仓库**（https://gitcode.com/Ascend/pytorch/releases）：提供 `TORCH_VERSION`、`TORCH_NPU_RELEASE_VERSION`、`TORCH_NPU_PATCH_TAG` 的取值，并托管 wheel 包（例：`torch_npu-2.10.0-cp310-cp310-manylinux_2_28_aarch64.whl`）。
- **Dockerfile 源码**（https://gitcode.com/Ascend/pytorch/blob/master/docker/Dockerfile）：本文档的构建参数定义源头。
- **Issue Feedback**（https://gitcode.com/Ascend/pytorch/issues）：社区问题反馈渠道。
- **LICENSE**（https://gitcode.com/Ascend/pytorch/blob/master/LICENSE）：镜像中 TorchNPU 组件的许可证。

上游依赖关系：CANN 工具链（9.0.0）→ TorchNPU 插件（2.10.0）→ PyTorch 框架 → 用户的 AI 模型；下游用户为基于 Atlas NPU 的 PyTorch 开发者与研究者。

---

## 【使用方法】

### 1. 构建镜像（原文 Quick Start）

以构建 `2.10.0-a3-ubuntu22.04-py3.11` 镜像为例：

```bash
docker build \
  --build-arg CHIP_ARCH=a3 \
  --build-arg OS=ubuntu \
  --build-arg OS_VERSION=22.04 \
  --build-arg PY_VERSION=3.11 \
  --build-arg CANN_VERSION=9.0.0 \
  --build-arg ARCH=arm \
  --build-arg PY_TAG=cp311 \
  --build-arg TORCH_NPU_RELEASE_TAG=v26.0.0-pytorch2.10.0 \
  --build-arg TORCH_NPU_PATCH_TAG=2.10.0 \
  -t image_name:tag \
  -f Dockerfile .
```

代理环境补充：

```bash
docker build \
  --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
  --build-arg NO_PROXY=localhost,127.0.0.1 \
  ... \
  -f Dockerfile .
```

### 2. 运行容器（原文 Run TorchNPU Container）

```bash
docker run \
    --name pta_container \
    --device /dev/davinci1 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -it ascend/pta:tag bash
```

### 3. 二次开发（原文 Secondary Development）

```bash
# Use TorchNPU image as base image and add user software
FROM quay.io/ascend/torch-npu:2.10.0-cann9.0.0-910b-ubuntu22.04-py3.11 

RUN apt update -y && \
    apt install gcc ...

...
```

### 4. 镜像拉取参考

以 `quay.io/ascend/torch-npu:2.10.0-cann9.0.0-910b-ubuntu22.04-py3.11` 标签作为二次开发基础镜像，或直接使用 24 个官方 tag 之一（如 `2.10.0-cann9.0.0-310p-openeuler24.03-py3.11`）拉取现成镜像。
