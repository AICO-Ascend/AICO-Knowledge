# Ascend PyTorch

> 仓 `pytorch-xllmai` · 路径 `Docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch-xllmai/Docker/OVERVIEW.md

# Docker/OVERVIEW.md 深度解读

## 【定位】

本文档是 **Ascend PyTorch (PTA)** Docker 镜像项目的总览说明,描述该插件如何为 Ascend NPU 提供 PyTorch 框架适配能力,并给出镜像标签规范、构建参数、容器运行方式以及所支持的硬件型号,作为用户构建、运行和二次开发 PTA 容器镜像的入口参考。

## 【技术要点】

- **PTA 插件定位**: 基于 Ascend 的 PyTorch 深度学习适配框架,让 Ascend NPU 支持 PyTorch,并将 Ascend AI 处理器的算力开放给 PyTorch 用户。
- **镜像标签格式**: `<PTA_version>-<chip>-<os>-<python_version>`,由 PTA 版本、芯片型号、操作系统、Python 版本等字段拼接构成(共 6 个字段)。
- **必需构建参数 (Required=Yes)**: `CANN_VERSION`、`CHIP_ARCH`、`OS`、`OS_VERSION`、`PY_VERSION`、`ARCH`、`PY_TAG`、`TORCH_NPU_RELEASE_VERSION`、`TORCH_VERSION` 共 9 项;可选参数为 `MANYLINUX_VER`、`PIP_MIRROR_URL`。
- **典型版本取值** (示例): `CANN_VERSION=9.0.0-beta.2`, `CHIP_ARCH=910b/310p/a3`, `PY_TAG=cp311`, `TORCH_NPU_RELEASE_VERSION=v26.0.0-beta.1-pytorch2.10.0`, `TORCH_VERSION=2.10.0rc3`, `PIP_MIRROR_URL=https://pypi.tuna.tsinghua.edu.cn/simple`。
- **容器运行挂载**: 必须透传 4 个 NPU 设备节点 (`/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`) 与 5 个主机目录 (含 `dcmi`、`npu-smi`、driver `lib64`、`version.info`、`ascend_install.info`)。
- **支持硬件**: Ascend 910B (Atlas 800T A2、Atlas 900 A2 PoD)、Ascend A3 (Atlas 800T A3)、Ascend 310P (Atlas 300I Pro、Atlas 300V Pro),统一支持 ARM64 / x86_64 架构。

## 【关键机制与数据】

- **工作原理**: 通过在基础 Docker 镜像中预装 Ascend CANN 工具包与 `torch_npu` wheel 包,把 PyTorch 模型中的张量/算子调用映射到 Ascend NPU 上执行,从而替代默认的 CUDA/CPU 后端。
- **数据流 (构建期)**: 用户在 `docker build` 时通过 `--build-arg` 注入 `CANN_VERSION`、`TORCH_NPU_RELEASE_TAG` 等参数,镜像内根据 `TORCH_VERSION` 字段(取 `torch_npu-<TORCH_VERSION>-cp...whl` 中 `torch_npu-` 与 `-cp310` 之间的字符串) 下载并安装对应的 `torch_npu` wheel 包。
- **数据流 (运行期)**: 容器启动时通过 `--device` 把 NPU 设备节点透传给容器进程,并通过 `-v` 把主机上的驱动、固件、CMDK 与版本信息目录挂入容器,使容器内应用可直接调用本地 NPU 算力。
- **示例 wheel 下载 URL** (原文):
  `https://gitcode.com/Ascend/pytorch/releases/download/v26.0.0-beta.1-pytorch2.10.0/torch_npu-2.10.0rc3-cp310-cp310-manylinux_2_28_aarch64.whl`
- **典型基础镜像示例** (原文,尚未发布,仅作示例): `quay.io/ascend/ascend-pytorch:v26.0.0-beta.1-torch2.10.0-910b-ubuntu-py3.11-arm`

## 【表格解读】

### 表格 ① 标签字段规范

| Field          | Example Value              | Description                                              |
|----------------|----------------------------|----------------------------------------------------------|
| PTA Version    | v26.0.0-beta.1-torch2.10.0 | Version identifier in the official torch_npu release tag |
| Chip           | 910b / 310p / a3           | Ascend chip model identifier                             |
| OS             | ubuntu / openeuler         | OS distribution used for the base image                  |
| Python Version | py3.11                     | Major Python version pre-installed in the image          |
| System Arch    | arm / x86                  | Host and image runtime hardware architecture             |
| CANN Version   | 9.0.0-beta.2               | Ascend CANN toolkit version                              |

**逐行解读**:
- **PTA Version**:镜像 tag 中第一段,对应官方 `torch_npu` 发布版本标识 (示例 `v26.0.0-beta.1-torch2.10.0`),把 release 版本与 torch 版本绑在一起。
- **Chip**:指明镜像适配的 Ascend 芯片型号 (910b/310p/a3),决定后续驱动与 CANN 包的目标架构。
- **OS**:基础镜像操作系统 (ubuntu / openeuler),影响系统库的安装与依赖。
- **Python Version**:镜像预装的 Python 主版本 (示例 py3.11)。
- **System Arch**:主机与镜像运行的硬件架构 (arm / x86),与 CHIP_ARCH 配合决定 wheel 平台。
- **CANN Version**:配套的 Ascend CANN 工具包版本 (示例 `9.0.0-beta.2`),决定可用算子集合。

### 表格 ② 构建参数

| Argument                  | Description                                                | Required | Reference Source          | Example Value                            |
|---------------------------|------------------------------------------------------------|----------|---------------------------|------------------------------------------|
| CANN_VERSION              | Ascend CANN toolkit version                                | Yes      | CANN base image repo      | 9.0.0-beta.2                             |
| CHIP_ARCH                 | Ascend chip architecture identifier                        | Yes      | CANN image tag rules      | 910b / 310p / a3                         |
| OS                        | Base image operating system                                | Yes      | CANN image tag rules      | ubuntu / openeuler                       |
| OS_VERSION                | Operating system version                                   | Yes      | CANN image tag rules      | 22.04 / 24.03                            |
| PY_VERSION                | Python version pre-installed in base image                 | Yes      | CANN image tag rules      | 3.11                                     |
| ARCH                      | Host hardware architecture                                 | Yes      | Environment hardware      | arm / x86                                |
| PY_TAG                    | Python package ABI tag (cp + version number)               | Yes      | Strictly match PY_VERSION | cp311 (PY3.11)                           |
| TORCH_NPU_RELEASE_VERSION | Official torch_npu release tag (including PyTorch version) | Yes      | PTA repo releases         | v26.0.0-beta.1-pytorch2.10.0             |
| TORCH_VERSION             | Full torch_npu version number                              | Yes      | PTA repo releases         | 2.10.0rc3                                |
| MANYLINUX_VER             | PyPI package compatible system version                     | No       | torch official wheel spec | manylinux_2_28                           |
| PIP_MIRROR_URL            | pip installation source URL (Tsinghua mirror by default)   | No       | PyPI mirror sources       | https://pypi.tuna.tsinghua.edu.cn/simple |

**逐行解读**:
- **CANN_VERSION / CHIP_ARCH / OS / OS_VERSION / PY_VERSION**:均参考 CANN 基础镜像的 tag 规则,共同决定拉取哪一套 CANN 基础镜像。
- **ARCH**:由运行环境硬件决定 (arm / x86),与 `CHIP_ARCH` 共同决定最终镜像与 wheel 平台。
- **PY_TAG**:Python 包 ABI tag (`cp311` 对应 `PY3.11`),必须严格与 `PY_VERSION` 匹配,否则 `torch_npu` wheel 安装会失败。
- **TORCH_NPU_RELEASE_VERSION**:官方 `torch_npu` 发布 tag,示例 `v26.0.0-beta.1-pytorch2.10.0`,可直接用于 `wget`/`pip install` 路径拼接。
- **TORCH_VERSION**:`torch_npu` 完整版本号 (示例 `2.10.0rc3`),即从 wheel 文件名 `torch_npu-2.10.0rc3-cp310-...whl` 中提取 `torch_npu-` 与 `-cp310` 之间的部分。
- **MANYLINUX_VER**:PyPI 包兼容的系统版本标识 (示例 `manylinux_2_28`),可选,不指定时使用 torch 官方 wheel 默认值。
- **PIP_MIRROR_URL**:pip 安装源 URL (默认清华源),用于加速下载。

### 表格 ③ 支持硬件

| Chip Series | Product Examples                | Architecture   |
|-------------|---------------------------------|----------------|
| Ascend 910B | Atlas 800T A2, Atlas 900 A2 PoD | ARM64 / x86_64 |
| Ascend A3   | Atlas 800T A3                   | ARM64 / x86_64 |
| Ascend 310P | Atlas 300I Pro, Atlas 300V Pro  | ARM64 / x86_64 |

**逐行解读**:
- **Ascend 910B 系列**:对应训练/推理主力产品 `Atlas 800T A2` 与 `Atlas 900 A2 PoD`,支持 ARM64 与 x86_64 两种主机架构。
- **Ascend A3 系列**:对应产品 `Atlas 800T A3`,同样支持 ARM64 与 x86_64。
- **Ascend 310P 系列**:对应边缘/推理产品 `Atlas 300I Pro` 与 `Atlas 300V Pro`,支持 ARM64 与 x86_64。

## 【公式解读】

原文无公式。

## 【关联】

- **多语言版本**:与 `./OVERVIEW.zh.md` (中文版 OVERVIEW) 互为翻译对应。
- **社区与文档上游**:
  - [Ascend PyTorch community](https://www.hiascend.com/developer/software/ai-frameworks/pytorch):PTA 项目维护方。
  - [PTA Documentation](https://www.hiascend.com/document/detail/zh/Pytorch/730/index/index.html):详细使用文档。
  - [AscendHub Image Repository](https://www.hiascend.com/developer/ascendhub):镜像托管平台。
  - [Ascend Developer Community](https://www.hiascend.com/developer):开发者交流入口。
  - [Issue Feedback](https://gitcode.com/Ascend/pytorch/issues):问题反馈。
- **构建依赖来源**:
  - [torch_npu official releases](https://gitcode.com/Ascend/pytorch/releases):提供 `TORCH_NPU_RELEASE_VERSION`、`TORCH_VERSION` 取值。
  - [CANN base image repository](https://quay.io/repository/ascend/cann?tab=tags):提供 `CANN_VERSION / CHIP_ARCH / OS / OS_VERSION / PY_VERSION` 取值规则。
- **许可**:镜像中预装的 PTA 遵循 [LICENSE](https://gitcode.com/Ascend/pytorch/blob/master/LICENSE);Python 与系统库等预装软件遵循各自许可。
- **二次开发**:文档明确给出 `FROM quay.io/ascend/ascend-pytorch:v26.0.0-beta.1-torch2.10.0-910b-ubuntu-py3.11-arm` 的方式,说明下游用户可直接把 PTA 镜像作为基础镜像继续叠加自定义软件。

## 【使用方法】

**1. 构建 PTA 镜像** (原文 `docker build` 命令):

```bash
docker build \
  --build-arg CANN_VERSION=xxx \
  --build-arg CHIP_ARCH=xxx \
  --build-arg OS=xxx \
  --build-arg OS_VERSION=xxx \
  --build-arg PY_VERSION=xxx \
  --build-arg TORCH_VERSION=xxx \
  --build-arg ARCH=xxx \
  --build-arg PY_TAG=xxx \
  --build-arg TORCH_NPU_RELEASE_TAG=xxx \
  --build-arg TORCH_NPU_PATCH_TAG=xxx \
  -t image_name:tag \
  -f Dockerfile .
```

**2. 本地快速构建** (原文 `docker buildx` 命令):

```bash
docker buildx build -t {your_repo}/pta:latest -f Dockerfile .
```

**3. 运行 PTA 容器** (原文 `docker run` 命令):

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

**4. 二次开发** (原文 Dockerfile 片段):

```dockerfile
FROM quay.io/ascend/ascend-pytorch:v26.0.0-beta.1-torch2.10.0-910b-ubuntu-py3.11-arm # Not yet published, example only, subject to change.

RUN apt update -y && \
    apt install gcc ...

...
```
