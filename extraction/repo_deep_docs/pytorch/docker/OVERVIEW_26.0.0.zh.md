# TorchNPU

> 仓 `pytorch` · 路径 `docker/OVERVIEW_26.0.0.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docker/OVERVIEW_26.0.0.zh.md

# TorchNPU Docker 镜像 Overview 文档深度解读

## 【定位】

本文档是 TorchNPU（昇腾为 PyTorch 框架打造的 NPU 适配插件）在 Docker 容器化部署场景下的总览文档，系统化说明了 **Tag 命名规范、Dockerfile 构建参数、镜像构建/运行命令以及支持的昇腾硬件型号**，解决"如何基于昇腾 NPU 硬件拉取、构建并运行与 PyTorch 框架对齐的 TorchNPU 容器镜像"这一部署问题。

---

## 【技术要点】

1. **Tag 五段式命名规范**（原文）`<TorchNPU版本号>-<CANN版本>-<硬件信息（芯片）>-<操作系统>-<Python版本>`，例如 `2.10.0-cann9.0.0-310p-ubuntu22.04-py3.11`，五段字段必须严格对应。

2. **Tag 多版本矩阵**：在 `26.0.0` 镜像仓库下并列提供 4 个 TorchNPU 版本（**2.10.0 / 2.9.0.post2 / 2.8.0.post4 / 2.7.1.post4**），每个版本再交叉 **3 种芯片（910b / 310p / a3）× 2 种 OS（ubuntu22.04 / openeuler24.03）**，合计 **24 个 Tag**。

3. **Dockerfile 参数化构建**：通过 11 个 `build-arg` 控制镜像内容，其中 9 个必填（CHIP_ARCH、OS、OS_VERSION、PY_VERSION、CANN_VERSION=**9.0.0**、ARCH、PY_TAG=**cp311**、TORCH_NPU_RELEASE_TAG=**v26.0.0-pytorch2.10.0**、TORCH_NPU_PATCH_TAG=**2.10.0**），2 个可选（MANYLINUX_VER=**manylinux_2_28**、PIP_MIRROR_URL 默认清华源）。

4. **Python 版本与 ABI 标签强一致**：`PY_VERSION=3.11` ↔ `PY_TAG=cp311` 必须严格匹配（原文："与 PY_VERSION 严格匹配"），否则 whl 包无法安装。

5. **宿主机设备直通机制**：运行容器时需 `--device` 透传 `/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 四个昇腾设备节点，并通过 `-v` 挂载 `/usr/local/dcmi`、`npu-smi`、`/usr/local/Ascend/driver/lib64/` 等驱动/管理目录。

6. **代理注入模式**（原文）：构建机需要代理时，必须通过 `--build-arg HTTP_PROXY / HTTPS_PROXY / NO_PROXY` 显式传入，不能仅靠环境变量。

---

## 【关键机制与数据】

### 工作原理

- **镜像生产链路**（原文推断链路）：CANN 基础镜像仓库（quay.io/ascend/cann）→ 注入 11 个 `build-arg` → 调用仓库根目录下的 `Dockerfile` → 生成 `ascend/pta:tag` 镜像。
- **版本号双标识机制**：发布时使用复合版本号 `v26.0.0-pytorch2.10.0`，其中 `26.0.0` 是 TorchNPU 自身发布版本，`2.10.0` 是其内嵌的 PyTorch 版本，通过 `download/` 与 `/torch_npu-` 之间的子串拆分（原文规则）。
- **Python 包 ABI 对齐机制**：`PY_TAG` 形如 `cp311`，对应 CPython 3.11 ABI，与 `PY_VERSION=3.11` 一一对应，确保 `torch_npu-2.10.0-cp310-cp310-manylinux_2_28_aarch64.whl` 这样的二进制 whl 能被 pip 正确解析安装。
- **设备发现/管理链路**：宿主机 `/dev/davinci_manager`（设备管理器）+ `/dev/hisi_hdc`（主机直连接口）+ `/dev/devmm_svm`（共享虚拟内存）+ `/dev/davinci1`（具体 NPU 设备）四件套，配合 `/etc/ascend_install.info` 安装元数据，使容器内进程能枚举并调用昇腾 NPU。

### 数据流（原文给出的 whl 路径示例）

```
https://gitcode.com/Ascend/pytorch/releases/download/
  v26.0.0-pytorch2.10.0/torch_npu-2.10.0-cp310-cp310-manylinux_2_28_aarch64.whl
        ↑                          ↑
  TORCH_NPU_RELEASE_VERSION    TORCH_NPU_PATCH_TAG
  = v26.0.0-pytorch2.10.0       = 2.10.0
```

### 性能/对比数据

原文未提供性能数据或基准测试结果（"原文: 无"）。

---

## 【表格解读】

### 表 1：Tag 规范字段表（原文逐字还原）

| 字段 | 值 | 说明 |
|------|----|------|
| TorchNPU 版本号 | 2.10.0 | 详见readme中版本说明部分 |
| CANN版本 | 9.0.0 | 详见readme中版本说明部分 |
| 硬件信息（芯片） | 910b / 310p / a3 | 昇腾芯片型号标识 |
| 操作系统 | ubuntu22.04 / openeuler24.03 | 基础镜像所使用的操作系统发行版 |
| Python 版本 | py3.11 | 镜像内置 Python 版本 |

**逐行解读**：
- **TorchNPU 版本号 = 2.10.0**：表示该 Tag 对应的 TorchNPU 插件主版本号为 2.10.0，详细变更需查阅仓库根目录的 `readme` 中"版本说明"部分。
- **CANN版本 = 9.0.0**：CANN（Compute Architecture for Neural Networks）是昇腾异构计算架构，9.0.0 为对应工具链版本，决定底层算子库与驱动兼容范围。
- **硬件信息（芯片）= 910b / 310p / a3**：分别对应昇腾训练芯片 Atlas 800T A2/A3 系列（910B、A3）和推理芯片 Atlas 300I/300V Pro（310P）。
- **操作系统 = ubuntu22.04 / openeuler24.03**：基础镜像只支持这两款 LTS 系发行版，其他 OS 暂未在 Tag 矩阵中提供。
- **Python 版本 = py3.11**：镜像内置 Python 3.11，对应 ABI 标签 `cp311`（见 Dockerfile 构建参数表）。

---

### 表 2：Dockerfile 构建参数表（原文逐字还原）

| 参数 | 说明 | 必填 | 参考来源 | 参数取值 |
|------|------|------|----------|----------|
| CHIP_ARCH | 昇腾芯片架构标识 | 是 | CANN 镜像标签规则 | 910b / 310p / a3 |
| OS | 基础镜像操作系统 | 是 | CANN 镜像标签规则 | ubuntu / openeuler |
| OS_VERSION | 操作系统版本 | 是 | CANN 镜像标签规则 | 22.04 / 24.03 |
| PY_VERSION | 基础镜像内置 Python 版本 | 是 | CANN 镜像标签规则 | 3.11 |
| CANN_VERSION | 昇腾 CANN 工具包版本 | 是 | CANN 基础镜像仓库 | 9.0.0 |
| ARCH | 宿主机硬件架构 | 是 | 环境硬件 | arm / x86 |
| PY_TAG | Python 包 ABI 标签（cp + 版本号） | 是 | 与 PY_VERSION 严格匹配 | cp311 |
| TORCH_NPU_RELEASE_VERSION | TorchNPU 官方发布 Tag（含 pytorch 版本） | 是 | TorchNPU 仓库发行版 | v26.0.0-pytorch2.10.0 |
| TORCH_NPU_PATCH_TAG | TorchNPU 官方发布包名里的版本号 | 是 | TorchNPU 仓库发行版 | 2.10.0 |
| MANYLINUX_VER | PyPI 包兼容系统版本 | 否 | torch 官方 whl 规范 | manylinux_2_28 |
| PIP_MIRROR_URL | pip 安装源地址（默认清华源） | 否 | PyPI 镜像源 | https://pypi.tuna.tsinghua.edu.cn/simple |

**逐行解读**：
- **CHIP_ARCH**：决定 Dockerfile 内部选用哪一组昇腾算子库与驱动，值集合严格继承自 CANN 镜像 tag 规则。
- **OS / OS_VERSION**：组合锁定基础镜像发行版；`ubuntu22.04` 与 `openeuler24.03` 是当前唯一支持的两个 OS 组合。
- **PY_VERSION = 3.11**：与下一行 `PY_TAG` 强耦合，原文明确"严格匹配"。
- **PY_TAG = cp311**：CPython 3.11 的 ABI 标识符，决定能否安装 `cp311` 标记的 torch_npu whl。
- **CANN_VERSION = 9.0.0**：对应 Tag 规范表中的 CANN 字段，确保驱动/算子/运行时版本一致。
- **ARCH = arm / x86**：宿主机 CPU 架构，决定下载 `aarch64` 还是 `x86_64` 的 whl 包。
- **TORCH_NPU_RELEASE_VERSION = v26.0.0-pytorch2.10.0**：TorchNPU 26.0.0 系列发布版，内含 PyTorch 2.10.0。
- **TORCH_NPU_PATCH_TAG = 2.10.0**：与上一参数中的 PyTorch 版本号对齐，但取自 whl 文件名 `torch_npu-2.10.0-cp310-...whl` 中 `torch_npu-` 与 `-cp310` 之间的子串。
- **MANYLINUX_VER = manylinux_2_28**（可选）：决定 whl 能否在 glibc ≥ 2.28 的系统上加载，是 PEP 600 规范要求。
- **PIP_MIRROR_URL = https://pypi.tuna.tsinghua.edu.cn/simple**（可选）：默认清华源，便于国内网络环境快速安装。

---

### 表 3：支持的硬件表（原文逐字还原）

| 芯片系列 | 产品示例 | 架构 |
|---------|---------|------|
| 昇腾 910B | Atlas 800T A2、Atlas 900 A2 PoD | ARM64 / x86_64 |
| 昇腾 A3 | Atlas 800T A3 | ARM64 / x86_64 |
| 昇腾 310P | Atlas 300I Pro、Atlas 300V Pro | ARM64 / x86_64 |

**逐行解读**：
- **昇腾 910B**：训练主力，对应 `Tag` 中的 `910b`，产品形态为 8 卡及以上的训练服务器（PoD 形态），支持 ARM64 与 x86_64 两种宿主 CPU。
- **昇腾 A3**：新一代训练芯片，对应 Tag 中的 `a3`，落地产品为 Atlas 800T A3。
- **昇腾 310P**：推理主力，对应 Tag 中的 `310p`，落地为 Atlas 300I Pro / 300V Pro 边缘或推理卡。
- 三个芯片系列均同时兼容 ARM64 与 x86_64 主机，因此 `ARCH` 参数需根据实际宿主选择。

---

## 【公式解读】

**原文无公式**。

文档内容以 Tag 命名、构建参数表、命令行示例为主，未出现任何数学公式、性能公式或 LaTeX 表达式。

---

## 【关联】

本文档位于 `docker/` 目录下，作为 TorchNPU 容器化交付的入口说明，与以下文档/模块存在上下游关系：

1. **英文版 Overview（内部链接，文末）**：`./OVERVIEW_26.0.0.md` —— 与本文件为同一份文档的中英双语版本，提供国际化镜像说明。
2. **根目录 `Dockerfile`**：`https://gitcode.com/Ascend/pytorch/blob/master/docker/Dockerfile` —— 本文档所有 `docker build` 命令的目标文件，所有 11 个 `build-arg` 的实际消费端。
3. **仓库根目录 `README`**：原文 "详见 readme 中版本说明部分" 提示 Tag 规范表中的 `TorchNPU 版本号`、`CANN 版本` 的详细变更说明位于根 README。
4. **CANN 基础镜像仓库**：`https://quay.io/repository/ascend/cann?tab=tags` —— Tag 中 OS、OS_VERSION、CANN_VERSION 等字段的"上游真值源"。
5. **TorchNPU 官方 Release**：`https://gitcode.com/Ascend/pytorch/releases` —— 提供 `TORCH_NPU_RELEASE_VERSION` 与 `TORCH_NPU_PATCH_TAG` 的取值，并托管 whl 包下载。
6. **`LICENSE`**：`https://gitcode.com/Ascend/pytorch/blob/master/LICENSE` —— 镜像内 TorchNPU 组件的许可证信息。
7. **社区支持矩阵**：昇腾开发者社区、TorchNPU 文档（`https://www.hiascend.com/document/detail/zh/Pytorch/730/index/index.html`）、问题反馈（`https://gitcode.com/Ascend/pytorch/issues`）—— 文档"快速参考"一节列出的用户支持路径。
8. **Ascend for PyTorch 社区主页**：`https://www.hiascend.com/developer/software/ai-frameworks/pytorch` —— TorchNPU 的维护方声明。

---

## 【使用方法】

### 1. 拉取预构建镜像（直接使用 Tag）

直接以 24 个 Tag 之一拉取，例如：
```text
2.10.0-cann9.0.0-910b-ubuntu22.04-py3.11
```
无需本地构建（原文给出 Tag 列表供 `docker pull` 使用）。

### 2. 自定义构建镜像（原文给出的完整示例）

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

代理环境追加（原文）：
```bash
  --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
  --build-arg NO_PROXY=localhost,127.0.0.1
```

### 3. 启动容器（原文给出的运行命令）

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

### 4. 二次开发（基于已构建镜像叠加用户软件，原文 Dockerfile 片段）

```dockerfile
FROM quay.io/ascend/torch-npu:2.10.0-cann9.0.0-910b-ubuntu22.04-py3.11
RUN apt update -y && apt install gcc ...
```

### 5. 关键约束（原文明确）

- `PY_VERSION` 与 `PY_TAG` 必须严格匹配（cp311 ↔ 3.11）。
- `TORCH_NPU_RELEASE_VERSION` 与 `TORCH_NPU_PATCH_TAG` 取值需与 [官方 releases](https://gitcode.com/Ascend/pytorch/releases) 中实际发布的 Tag 一致。
- 容器运行需保证宿主机已正确安装昇腾驱动（由挂载的 `/usr/local/Ascend/driver/...` 与 `/etc/ascend_install.info` 验证）。
- `PIP_MIRROR_URL` 默认清华源，可按需覆盖。
