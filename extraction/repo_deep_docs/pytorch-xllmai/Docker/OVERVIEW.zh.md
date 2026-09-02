# Ascend PyTorch

> 仓 `pytorch-xllmai` · 路径 `Docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch-xllmai/Docker/OVERVIEW.zh.md

# Docker/OVERVIEW.zh.md 一体化深度解读

## 【定位】

本文档是「Ascend Extension for PyTorch（PTA）」容器镜像与 Dockerfile 的中文总览，目标是让用户/开发者能够在昇腾 NPU 上以 Docker 方式快速构建、运行和二次开发支持 PyTorch 框架的容器化环境，明确镜像 Tag 命名规范、构建参数、运行所需设备映射及硬件兼容矩阵。

---

## 【技术要点】

1. **PTA 镜像 Tag 命名格式**：`<PTA版本号>-<硬件信息（芯片）>-<操作系统>-<Python版本>`，示例字段包括 `v26.0.0-beta.1-torch2.10.0`（PTA 版本）、`910b / 310p / a3`（芯片）、`ubuntu / openeuler`（OS）、`py3.11`（Python）、`arm / x86`（架构）、`9.0.0-beta.2`（CANN 版本）。
2. **构建参数体系**：10 个核心 build-arg，其中 9 个为必填（CANN_VERSION、CHIP_ARCH、OS、OS_VERSION、PY_VERSION、ARCH、PY_TAG、TORCH_NPU_RELEASE_VERSION、TORCH_VERSION），可选参数包括 `MANYLINUX_VER`（如 `manylinux_2_28`）与 `PIP_MIRROR_URL`（默认清华源 `https://pypi.tuna.tsinghua.edu.cn/simple`）。
3. **TORCH_VERSION 提取规则**：从完整 whl 文件名 `torch_npu-2.10.0rc3-cp310-cp310-manylinux_2_28_aarch64.whl` 中取 `torch_npu-{}-cp310` 之间所有内容，即 `2.10.0rc3`；并要求 `PY_TAG`（如 `cp311`）与 `PY_VERSION`（如 `3.11`）严格匹配。
4. **容器设备与目录挂载要求**：必须挂载 4 个设备 `/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，以及 5 个目录卷 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info`。
5. **支持硬件矩阵**：覆盖三大昇腾芯片系列——昇腾 910B（Atlas 800T A2、Atlas 900 A2 PoD）、昇腾 A3（Atlas 800T A3）、昇腾 310P（Atlas 300I Pro、Atlas 300V Pro），均支持 ARM64 / x86_64 架构。
6. **PTA 维护与版本查询路径**：PTA 由 Ascend PyTorch community 维护；torch_npu 官方发布/补丁版本查询地址为 `https://gitcode.com/Ascend/pytorch/releases`，CANN 基础镜像查询地址为 `https://quay.io/repository/ascend/cann?tab=tags`。

---

## 【关键机制与数据】

- **镜像 Tag 与 CANN/PyTorch 版本强绑定**：Tag 中的 PTA 版本号字段（`v26.0.0-beta.1-torch2.10.0`）对应 `torch_npu` 官方发布 Tag 中的版本标识；构建时需通过 `CANN_VERSION=9.0.0-beta.2` 等参数与 CANN 基础镜像仓库标签精确对齐。
- **完整 whl 下载链示例（原文）**：`https://gitcode.com/Ascend/pytorch/releases/download/v26.0.0-beta.1-pytorch2.10.0/torch_npu-2.10.0rc3-cp310-cp310-manylinux_2_28_aarch64.whl`，文件名结构是 `TORCH_VERSION`/`PY_TAG`/`MANYLINUX_VER`/`ARCH` 四个 build-arg 共同决定的输出形式。
- **二次开发基镜像（原文）**：`FROM quay.io/ascend/ascend-pytorch:v26.0.0-beta.1-torch2.10.0-910b-ubuntu-py3.11`，原文注明"暂未发布，仅示例地址，仍需修改"。
- **数据流（Docker 侧）**：本地 Dockerfile 构建 → 调用 `docker buildx` 引入多架构支持 → 启动容器时通过 `--device` 透传昇腾 NPU 字符设备、通过 `-v` 透传驱动/固件/版本信息文件，使容器内可访问宿主机的 NPU 驱动栈。
- **性能数据**：原文无任何性能数据/benchmark 数字。

---

## 【表格解读】

### 表 1：Tag 规范字段说明（原文逐字还原）

| 字段 | 示例值 | 说明 |
|------|--------|------|
| PTA 版本号 | v26.0.0-beta.1-torch2.10.0 | 对应 torch_npu 官方发布 Tag 中的版本标识 |
| 硬件信息（芯片） | 910b / 310p / a3 | 昇腾芯片型号标识 |
| 操作系统 | ubuntu / openeuler | 基础镜像所使用的操作系统发行版 |
| Python 版本 | py3.11 | 镜像内置 Python 大版本号 |
| 系统架构 | arm / x86 | 宿主机及镜像运行的硬件架构 |
| CANN 版本 | 9.0.0-beta.2 | 昇腾 CANN 工具包版本号 |

**逐行解读**：
- **PTA 版本号**：作为镜像 Tag 的第一段，承载两层信息——PTA 框架自身版本（`v26.0.0-beta.1`）与所兼容的 PyTorch 大版本（`torch2.10.0`），是用户选择镜像时的首要匹配项。
- **硬件信息（芯片）**：决定镜像内 CANN 算子库与驱动绑定的芯片目标，`910b` 对应训练/推理主力，`310p` 对应边缘推理，`a3` 对应新一代训练卡。
- **操作系统**：基础镜像发行版，决定 apt/dnf 包管理与系统库版本。
- **Python 版本**：镜像内置 Python 大版本号，与后续 `PY_TAG`（cp311 等）共同决定 pip wheel ABI。
- **系统架构**：镜像编译目标架构，`arm` 多见于鲲鹏/A2 服务器，`x86` 多见于通用 x86 服务器。
- **CANN 版本**：昇腾计算架构工具包版本，决定算子兼容性，必须与宿主机驱动版本严格匹配。

### 表 2：构建参数表（原文逐字还原）

| 参数 | 说明 | 必填 | 参考来源 | 示例值 |
|------|------|------|----------|--------|
| CANN_VERSION | 昇腾 CANN 工具包版本 | 是 | CANN 基础镜像仓库 | 9.0.0-beta.2 |
| CHIP_ARCH | 昇腾芯片架构标识 | 是 | CANN 镜像标签规则 | 910b / 310p / a3 |
| OS | 基础镜像操作系统 | 是 | CANN 镜像标签规则 | ubuntu / openeuler |
| OS_VERSION | 操作系统版本 | 是 | CANN 镜像标签规则 | 22.04 / 24.03 |
| PY_VERSION | 基础镜像内置 Python 版本 | 是 | CANN 镜像标签规则 | 3.11 |
| ARCH | 宿主机硬件架构 | 是 | 环境硬件 | arm / x86 |
| PY_TAG | Python 包 ABI 标签（cp + 版本号） | 是 | 与 PY_VERSION 严格匹配 | cp311 (PY3.11) |
| TORCH_NPU_RELEASE_VERSION | torch_npu 官方发布 Tag（含 pytorch 版本） | 是 | PTA 仓库发行版 | v26.0.0-beta.1-pytorch2.10.0 |
| TORCH_VERSION | torch_npu 完整版本号 | 是 | PTA 仓库发行版 | 2.10.0rc3 |
| MANYLINUX_VER | PyPI 包兼容系统版本 | 否 | torch 官方 whl 规范 | manylinux_2_28 |
| PIP_MIRROR_URL | pip 安装源地址（默认清华源） | 否 | PyPI 镜像源 | https://pypi.tuna.tsinghua.edu.cn/simple |

**逐行解读**：
- **CANN_VERSION / CHIP_ARCH / OS / OS_VERSION / PY_VERSION**：这 5 个 build-arg 必须严格对齐 CANN 基础镜像仓库（如 `quay.io/ascend/cann`）的既有 Tag 规则，因为 Dockerfile 会基于这些值拉取特定上游镜像。
- **ARCH**：来自当前宿主机硬件探测，与 `OS_VERSION` 共同决定基础镜像的多架构选择。
- **PY_TAG**：必须与 `PY_VERSION` 数值严格匹配（如 PY3.11 → cp311），否则 pip 安装 whl 时会因 ABI 不一致而失败。
- **TORCH_NPU_RELEASE_VERSION / TORCH_VERSION**：前者是 PTA 仓库 release 页中的发行 Tag（含 pytorch 版本号），后者是该 release 对应的具体 torch_npu 包版本号，二者须来自同一 PTA 仓库发行版。
- **MANYLINUX_VER**：可选，默认遵循 torch 官方 whl 的 `manylinux_2_28` 规范；如目标系统 glibc 更旧则需下调。
- **PIP_MIRROR_URL**：可选，默认清华源，便于国内网络环境加速下载；可替换为内部 PyPI 镜像。

### 表 3：支持的硬件（原文逐字还原）

| 芯片系列 | 产品示例 | 架构 |
|----------|----------|------|
| 昇腾 910B | Atlas 800T A2、Atlas 900 A2 PoD | ARM64 / x86_64 |
| 昇腾 A3 | Atlas 800T A3 | ARM64 / x86_64 |
| 昇腾 310P | Atlas 300I Pro、Atlas 300V Pro | ARM64 / x86_64 |

**逐行解读**：
- **昇腾 910B**：覆盖训练主力产品 Atlas 800T A2 与超节点 Atlas 900 A2 PoD，宿主机既可以是 ARM64（鲲鹏）也可以是 x86_64。
- **昇腾 A3**：对应 Atlas 800T A3 单一系列（原文未列出多产品），同样双架构支持。
- **昇腾 310P**：边缘/推理产品线，覆盖 Atlas 300I Pro 与 Atlas 300V Pro 推理卡。

---

## 【公式解读】

**原文无数学公式。** 原文仅有一个 Tag 命名模板：

```
<PTA版本号>-<硬件信息（芯片）>-<操作系统>-<Python版本>
```

这属于字符串模板而非数学公式，符号说明：
- `<PTA版本号>`：占位 PTA 框架版本字符串。
- `<硬件信息（芯片）>`：占位芯片型号字符串。
- `<操作系统>`：占位 OS 发行版字符串。
- `<Python版本>`：占位 Python 大版本字符串。

实际拼装时还需在结尾追加（来自表格）`<系统架构>` 与 `<CANN 版本>` 两段字段，组成完整 Tag，例如 `v26.0.0-beta.1-torch2.10.0-910b-ubuntu-py3.11-arm-9.0.0-beta.2`（基于原文字段组合推断，原文未给出合并后的完整示例字符串）。

---

## 【关联】

- **与 PTA 上游框架的关系**：本文档镜像内承载的核心软件是 `torch_npu`（Ascend Extension for PyTorch 插件），其发行 Tag 由 `https://gitcode.com/Ascend/pytorch/releases` 给出，是镜像 Tag 第一段（`TORCH_NPU_RELEASE_VERSION`）的取值来源。
- **与 CANN 工具链的关系**：CANN（Compute Architecture for Neural Networks）是底层算子/驱动栈，镜像 Tag 与构建参数中的 `CANN_VERSION`、`CHIP_ARCH`、`OS`、`OS_VERSION`、`PY_VERSION` 必须对齐 `https://quay.io/repository/ascend/cann?tab=tags` 中的既有镜像标签，CANN 版本决定了 NPU 上算子的可用集合。
- **与硬件产品的关系**：硬件矩阵（昇腾 910B / A3 / 310P）直接对应 `CHIP_ARCH` 参数的可选值，并决定了容器 `--device /dev/davinci*` 与 `/dev/hisi_hdc` 等设备节点的可用性。
- **与英文版本的关系**：文末内部链接 `./OVERVIEW.md` 为同一文档的英文版本，结构与字段一一对应，可作为中文版的官方对照。
- **与许可证的关系**：镜像内 PTA 软件遵循 `https://gitcode.com/Ascend/pytorch/blob/master/LICENSE` 中的开源许可证；其他预装包（Python、系统库）受各自许可证约束。

---

## 【使用方法】

### 1. 构建 PTA 镜像（原文 `docker build`）

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
  -t 镜像名:标签 \
  -f Dockerfile .
```

> 原文注：参数 `TORCH_NPU_RELEASE_TAG` / `TORCH_NPU_PATCH_TAG` 在构建参数表中未单独列出，但出现在 `docker build` 命令行中，属于补充的 release/patch 区分字段。

### 2. 运行 PTA 容器（原文 `docker run`）

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

设备挂载说明（原文）：4 个 `--device` 用于透传 NPU 字符设备，5 个 `-v` 用于透传 dcmi 管理工具、`npu-smi` 命令、驱动库目录、驱动版本文件、安装信息文件。

### 3. 本地构建（原文 `docker buildx`）

```bash
docker buildx build -t {your_repo}/pta:latest -f Dockerfile .
```

### 5. 二次开发（原文 `FROM` 片段）

```dockerfile
FROM quay.io/ascend/ascend-pytorch:v26.0.0-beta.1-torch2.10.0-910b-ubuntu-py3.11 # 暂未发布，仅示例地址，仍需修改。

RUN apt update -y && \
    apt install gcc ...

...
```

### 6. 获取帮助（原文"快速参考"部分）

- AscendHub 镜像仓库：`https://www.hiascend.com/developer/ascendhub`
- PTA 文档：`https://www.hiascend.com/document/detail/zh/Pytorch/730/index/index.html`
- 昇腾开发者社区：`https://www.hiascend.com/developer`
- 问题反馈：`https://gitcode.com/Ascend/pytorch/issues`
