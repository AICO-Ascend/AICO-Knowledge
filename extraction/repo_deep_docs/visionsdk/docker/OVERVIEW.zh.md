# VisionSDK

> 仓 `visionsdk` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/visionsdk/docker/OVERVIEW.zh.md

# VisionSDK Docker 概述文档深度解读

## 【定位】

这篇文档描述了 **VisionSDK 容器镜像的发布规范与使用流程**：从镜像 Tag 命名规则、支持的产品型号、Dockerfile 构建方法、容器运行方式，到进入容器后的二次开发模板与示例代码入口，旨在帮助开发者快速获取并使用基于昇腾芯片的 VisionSDK 容器化视觉分析开发环境。

---

## 【技术要点】

1. **SDK 双开发范式**：VisionSDK 提供两种应用开发方式——**API 接口方式**（调用原生推理 API 与算子加速库）和**流程编排方式**（将功能单元封装为可串接的插件，模块化构建业务流程）。
2. **Tag 命名规范**：`版本-芯片系列-操作系统-python版本`，示例值为 `26.1.0-910b-openeuler24.03-py3.11`。
3. **构建命令**：使用 `docker build -t {your_repo}/vision:latest -f Dockerfile.<芯片系列>.<操作系统> .` 本地构建。
4. **容器运行需挂载的设备/目录**：需 `--device` 挂载 `/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并 `-v` 挂载 dcmi、npu-smi、Ascend driver lib64、version.info、ascend_install.info 等主机路径。
5. **进入容器验证方式**：`docker exec -it vision_container bash` 后执行 `pip show mindx`，看到 mindx 包信息即成功。
6. **二次开发基于官方基础镜像**：`FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/visionsdk:26.0.0-310p-ubuntu22.04-py3.11` 起扩展。
7. **硬件覆盖范围**：Atlas 推理系列、Atlas 800I A2，架构为 ARM64 / x86_64。

---

## 【关键机制与数据】

- **SDK 能力定位**（原文）：面向图片和视频视觉分析，提供基本的视频、图像智能分析能力及编程框架。
- **API 开发路径**（原文）：提供原生的推理 API 以及算子加速库，建议具有固定应用开发流程的用户采用，借用 VisionSDK 算法加速能力构建 CV 应用。
- **流程编排路径**（原文）：模块化设计，将业务流程功能单元封装为独立插件，支持插件串接、常用功能插件、流程编排能力、插件自定义开发。
- **驱动兼容性约束**（原文）：主机上必须安装与容器内 CANN 版本兼容的 NPU 驱动，驱动与 CANN 对应关系见 [CANN 兼容性矩阵](https://www.hiascend.com/document)。
- **镜像内预装核心包验证标志**（原文）：进入容器后通过 `pip show mindx` 查看到 mindx 包的具体信息即成功进入容器。
- **支持的镜像版本号**（原文）：示例版本为 `26.1.0`（支持的tags表）与二次开发模板中的 `26.0.0-310p-ubuntu22.04-py3.11`。
- **支持的基础操作系统**（原文）：`ubuntu22.04`、`openeuler24.03`。
- **支持的 Python 版本**（原文）：`py3.11`。
- **性能数据**：原文未涉及任何吞吐量、时延、加速比等性能指标。

---

## 【表格解读】

### 表格 1：Tag 字段说明（原文逐字还原）

| 字段            | 示例值                          | 说明             |
| --------------- | ------------------------------- | ---------------- |
| `VisionSDK版本` | `26.1.0`                        | VisionSDK 版本号 |
| `芯片系列`      | `910`                           | 目标芯片系列     |
| `操作系统`      | `ubuntu22.04`、`openeuler24.03` | 基础操作系统     |
| `python版本`    | `py3.11`                        | Python 版本      |

**逐行解读**：

- **`VisionSDK版本` 字段**：示例值 `26.1.0` 表示 VisionSDK 的版本号。该字段是 Tag 的版本锚点，开发者据此判断是否使用最新功能与修复。
- **`芯片系列` 字段**：示例值 `910` 表示目标芯片系列；结合下方「支持的tags及Dockerfile」表可知实际支持的系列为 `310p` 与 `910b`。
- **`操作系统` 字段**：示例给出两种基础操作系统 `ubuntu22.04` 与 `openeuler24.03`，代表镜像可适配主流 Linux 发行版与企业级服务器 OS。
- **`python版本` 字段**：示例值 `py3.11` 表示镜像内置 Python 3.11，AI/推理框架一般对 Python 版本敏感，统一版本可避免依赖冲突。

---

### 表格 2：支持的tags及Dockerfile（原文逐字还原）

| Tag                                 | Dockerfile |
| ----------------------------------- | ---------- |
| `26.1.0-310p-openeuler24.03-py3.11` | -          |
| `26.1.0-310p-ubuntu22.04-py3.11`    | -          |
| `26.1.0-910b-openeuler24.03-py3.11` | -          |
| `26.1.0-910b-ubuntu22.04-py3.11`    | -          |

**逐行解读**：

- **`26.1.0-310p-openeuler24.03-py3.11`**：面向 310p 芯片、openEuler 24.03 系统、Python 3.11 的 VisionSDK 26.1.0 镜像，Dockerfile 链接位以 `-` 占位（原文未提供）。
- **`26.1.0-310p-ubuntu22.04-py3.11`**：同版本下 310p 芯片对应的 Ubuntu 22.04 镜像变体，便于在主流 Ubuntu 环境下使用。
- **`26.1.0-910b-openeuler24.03-py3.11`**：面向算力更高的 910b 芯片、openEuler 24.03 镜像，适用于需要更强推理算力的场景。
- **`26.1.0-910b-ubuntu22.04-py3.11`**：910b 芯片对应的 Ubuntu 22.04 变体，完成对芯片系列 × 操作系统的笛卡尔积覆盖。

> **注**：原表中 Dockerfile 列全部为 `-`，未给出实际链接。

---

### 表格 3：支持的硬件（原文逐字还原）

| 产品型号      | 架构           |
| ------------- | -------------- |
| Atlas推理系列 | ARM64 / x86_64 |
| Atlas 800I A2 | ARM64 / x86_64 |

**逐行解读**：

- **Atlas 推理系列**：覆盖 ARM64 与 x86_64 两种主机架构，体现昇腾推理产品对多架构主机的适配能力。
- **Atlas 800I A2**：作为推理服务器产品，同样支持 ARM64 与 x86_64，说明 VisionSDK 容器镜像在不同 CPU 平台上具备一致的部署能力。

---

## 【公式解读】

原文给出的 Tag 命名格式（伪代码式）：

```
<VisionSDK版本>-<芯片系列>-<操作系统>-<python版本>
```

**符号含义与作用**：

- **`<VisionSDK版本>`**：VisionSDK 的语义化版本号，例如 `26.1.0`，用于标识 SDK 自身能力与 API 兼容性。
- **`<芯片系列>`**：目标芯片型号系列，例如 `310p`、`910b`，决定容器内 CANN 算子库与驱动适配的硬件目标。
- **`<操作系统>`**：宿主机/容器基础操作系统，例如 `ubuntu22.04` 或 `openeuler24.03`，影响镜像内系统库与运行时依赖。
- **`<python版本>`**：Python 运行时版本标识，例如 `py3.11`，统一 AI 框架（PyTorch/MindSpore 等）的解释器版本。
- **连字符 `-`**：作为字段分隔符，使 Tag 自描述且可被 CI/CD、镜像仓库索引解析。

除此 Tag 模板外，原文无其他数学/算法公式。

---

## 【关联】

- **语言版本关联**：本文件为中文版，英文版位于同目录的 `./OVERVIEW.md`（顶部语言切换条 `[English](./OVERVIEW.md) | 中文`）。
- **上游/帮助入口关联**：
  - [Issue 反馈](https://gitcode.com/Ascend/VisionSDK/issues) 与 [VisionSDK 代码仓](https://gitcode.com/Ascend/VisionSDK) 提供 bug 提交与源码获取通道。
  - [VisionSDK 文档入口](https://gitcode.com/Ascend/VisionSDK/blob/master/README.md) 与 [Ascend 社区](https://www.hiascend.com/) 提供更广泛的支持。
- **驱动/兼容性关联**：NPU 驱动与 CANN 版本需匹配，详见 [CANN 兼容性矩阵](https://www.hiascend.com/document)；镜像内集成 CANN 与 Mind 系列软件，其许可证见 [CANN 容器镜像 LICENSE](https://github.com/Ascend/cann-container-image/blob/main/LICENSE)。
- **示例代码关联**：使用说明指向 [VisionSDK 示例代码](https://gitcode.com/Ascend/VisionSDK/blob/master/docs/zh/03.quick_start.md)，可视为「快速开始」后的下游开发指引。
- **模块关系**：本文档是 docker 路径下的镜像发布/使用层说明，与 SDK 内的 API 开发方式（推理 API、算子加速库）和流程编排方式（功能插件、流程串接）形成「运行环境 ↔ 开发框架」的耦合。

---

## 【使用方法】

> 以下命令均按原文逐字保留。

### 1. 本地构建镜像

```bash
docker build -t {your_repo}/vision:latest -f Dockerfile.<芯片系列>.<操作系统> .
```

> 原文要求 `<芯片系列>`、`<操作系统>` 需替换为与「支持的tags」表中匹配的实参。

### 2. 运行 VisionSDK 容器

```bash
docker run \
    --name vision_container \
    --device /dev/davinci1 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -it ascend/vision:tag bash
```

### 3. 进入容器并验证

```bash
docker exec -it vision_container bash
pip show mindx
```

> 原文：查看到 mindx 包的具体信息即成功进入容器。

### 4. 二次开发 Dockerfile 模板

```dockerfile
FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/visionsdk:26.0.0-310p-ubuntu22.04-py3.11

RUN apt update -y && \
    apt install gcc ...

...
```

### 5. 前置条件（可选但推荐）

- **安装 NPU 驱动**（原文）：主机上必须安装与容器内 CANN 版本兼容的 NPU 驱动，对应关系见 [CANN 兼容性矩阵](https://www.hiascend.com/document)。Dockerfile 中是否安装驱动本身，原文未涉及。

### 6. 配置项说明

- 镜像 Tag 选择需匹配 **芯片系列**（310p / 910b）与 **操作系统**（ubuntu22.04 / openeuler24.03）。
- `--device` 与 `-v` 列表需按原文完整保留，缺一即无法使容器访问 NPU 设备与主机驱动库。
