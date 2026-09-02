# MindIE-Motor

> 仓 `mindie-motor` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docker/OVERVIEW.zh.md

# MindIE-Motor Docker Overview 文档深度解读

## 【定位】

本文档是 MindIE-Motor（昇腾自研推理集群管理框架）官方 Docker 镜像的概览说明，解决的是"如何在 AscendHub 上识别、选用与本地构建对应 MindIE-Motor 容器镜像"的问题，同时给出能力定义、Tag 规范、3.1.0 版本镜像矩阵、本地构建命令及许可证信息，是镜像层的入口说明。

## 【技术要点】

1. **核心能力定位（一键式 PD 分离部署）**：提供一键式 PD（Prefill-Decode）分离部署；基于云原生插件化架构灵活适配多种推理引擎（vLLM、SGLang）；结合高性能调度与负载均衡能力，构建高可用、可扩展的大规模推理服务。
2. **镜像多架构**：官方发布镜像名称为 `mindie-motor`，每个 Tag 均为多架构镜像（`arm64` / `x86_64`）。
3. **Tag 命名规范**：` <Motor版本>-<推理引擎版本>-<芯片系列>-<操作系统>-<python版本>`，例：`3.1.0-vllm_ascend0.23.0-a2-ubuntu22.04-py3.12`。3.0.x 历史 Tag 使用另一套命名，需参见 `supported_tags.md`。
4. **3.1.0 当前发布矩阵**（2026/08/18）：覆盖 a2 / a3 / a5 三种芯片系列、ubuntu22.04 / openeuler24.03 两种 OS、vllm-ascend 0.23.0 一种引擎、py3.12 一种 Python 版本，组合出 6 个 Tag，每个 Tag 同时支持 arm64 / x86_64。
5. **本地构建机制**：每个 Dockerfile 构建时会自动 clone 指定分支与 commit 的源码，并在镜像内执行 `build.sh` 安装 `motor` / `ccae_reporter`，无需本地源码或构建上下文；通过环境变量 `TAG` + `docker build --network=host --platform=linux/arm64 -f` 完成镜像构建。
6. **前置依赖**：宿主机需安装好固件与驱动、Docker 与 k8s（标注"可选"，但配合 `docker build` 与后续部署必备）。

## 【关键机制与数据】

- **原文：镜像命名公式（伪 Tag 模板）**：`<Motor版本>-<推理引擎版本>-<芯片系列>-<操作系统>-<python版本>`，五段以 `-` 串联，作为镜像 Tag 的强约束形式，可用于反查 Dockerfile 路径。
- **原文：3.1.0 发布时间**：2026/08/18，发布于 AscendHub。
- **原文：版本三要素**：`Motor版本` 形如 `3.1.0`、`3.1.0b1`；`引擎版本` 形如 `0.23.0`、`0.23.0rc1`（配套 vllm-ascend）；`芯片系列` 取值 `a2` / `a3` / `a5`。
- **原文：本地构建数据流**：执行 `docker build` → Dockerfile 头部声明 → 自动 clone 源码 → 镜像内 `build.sh` 安装 `motor` / `ccae_reporter` → 产出 `mindie-motor:${TAG}` 镜像。原文未给出任何性能/吞吐/QPS 数据。
- **原文：构建上下文**：标注"无需本地源码或构建上下文"，意味着 Dockerfile 自身具备从远端仓库拉源码并构建的能力。

## 【表格解读】

### 表 1：Tag 字段规范表（原文逐字还原）

| 字段 | 示例值 | 说明 |
|---|---|---|
| `Motor版本` | `3.1.0`、`3.1.0b1` | MindIE-Motor 版本号 |
| `引擎版本` | `0.23.0`、`0.23.0rc1` | 配套 vllm-ascend 版本 |
| `芯片系列` | `a2`、`a3`、`a5` | 目标昇腾芯片系列 |
| `操作系统` | `ubuntu22.04`、`openeuler24.03` | 基础操作系统 |
| `python版本` | `py3.12` | Python 版本 |

**逐行解读**：
- `Motor版本`：定义 MindIE-Motor 框架自身版本，区分正式版（`3.1.0`）与 beta 版（`3.1.0b1`）。
- `引擎版本`：声明该镜像预装/适配的推理引擎版本，示例中的 `vllm-ascend` 与 Tag 中的 `vllm_ascend` 前缀对应；支持 rc 预发布版（如 `0.23.0rc1`）。
- `芯片系列`：覆盖 a2 / a3 / a5 三档昇腾芯片，决定底层算子与运行时差异。
- `操作系统`：两种主流基础 OS，`ubuntu22.04` 与 `openeuler24.03`（openEuler LTS 衍生版）。
- `python版本`：当前统一为 `py3.12`，表明 3.1.0 已不再兼容更老 Python。

### 表 2：MindIE-Motor 3.1.0 镜像发布矩阵（原文逐字还原）

| Tag | Dockerfile | 架构 | 镜像内容 |
|---|---|---|---|
| `3.1.0-vllm_ascend0.23.0-a2-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindIE-Motor/blob/master/docker/mindie-motor-vllm/3.1.0-vllm_ascend0.23.0-a2-ubuntu22.04-py3.12/Dockerfile) | arm64 / x86_64 | motor / vllm-ascend 0.23.0 |
| `3.1.0-vllm_ascend0.23.0-a2-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindIE-Motor/blob/master/docker/mindie-motor-vllm/3.1.0-vllm_ascend0.23.0-a2-openeuler24.03-py3.12/Dockerfile) | arm64 / x86_64 | motor / vllm-ascend 0.23.0 |
| `3.1.0-vllm_ascend0.23.0-a3-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindIE-Motor/blob/master/docker/mindie-motor-vllm/3.1.0-vllm_ascend0.23.0-a3-ubuntu22.04-py3.12/Dockerfile) | arm64 / x86_64 | motor / vllm-ascend 0.23.0 |
| `3.1.0-vllm_ascend0.23.0-a3-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindIE-Motor/blob/master/docker/mindie-motor-vllm/3.1.0-vllm_ascend0.23.0-a3-openeuler24.03-py3.12/Dockerfile) | arm64 / x86_64 | motor / vllm-ascend 0.23.0 |
| `3.1.0-vllm_ascend0.23.0-a5-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindIE-Motor/blob/master/docker/mindie-motor-vllm/3.1.0-vllm_ascend0.23.0-a5-ubuntu22.04-py3.12/Dockerfile) | arm64 / x86_64 | motor / vllm-ascend 0.23.0 |
| `3.1.0-vllm_ascend0.23.0-a5-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindIE-Motor/blob/master/docker/mindie-motor-vllm/3.1.0-vllm_ascend0.23.0-a5-openeuler24.03-py3.12/Dockerfile) | arm64 / x86_64 | motor / vllm-ascend 0.23.0 |

**逐行解读**：
- 整张表是表 1 字段规范的实例化产物，共 6 行 = `3 芯片 × 2 OS × 1 引擎 × 1 Python × 1 Motor版本` 的笛卡尔展开。
- **第 1、2 行**：目标芯片 a2，分别基于 ubuntu22.04 / openeuler24.03，Dockerfile 路径随 Tag 字面拼接。
- **第 3、4 行**：目标芯片 a3，OS 组合同上；a3 区别于 a2 在于芯片代次不同，对应不同的固件/驱动与算子库。
- **第 5、6 行**：目标芯片 a5，OS 组合同上；a5 为 3.1.0 新增覆盖的芯片系列。
- **第 1 列**：Tag 中 `vllm_ascend` 前缀连接符为 `_`（与 Tag 模板中的 `-` 不同，模板里"引擎版本"段自身内部用 `_`），表明 3.1.0 仅配套 vllm-ascend，未在 3.1.0 中出现 SGLang 镜像。
- **第 2 列**：每个 Tag 对应独立 Dockerfile 路径，符合"每镜像一 Dockerfile"的工程实践。
- **第 3 列**：6 个 Tag 全部声明 `arm64 / x86_64`，镜像为多架构清单（multi-arch manifest）形态。
- **第 4 列**：镜像内容统一标注 `motor / vllm-ascend 0.23.0`，3.1.0 当前未声明 SGLang 引擎版本（即便简介中提到支持 SGLang）。

## 【公式解读】

原文无公式（无 LaTeX 公式、无伪代码公式）。仅有一个 Tag 命名模板，可视为字符串模板：

```
<Motor版本>-<推理引擎版本>-<芯片系列>-<操作系统>-<python版本>
```

- `<Motor版本>`：MindIE-Motor 主版本，形如 `3.1.0` / `3.1.0b1`。
- `<推理引擎版本>`：配套的推理引擎版本，写作时以 `vllm_ascend<版本>` 形式嵌入。
- `<芯片系列>`：目标昇腾芯片系列，`a2` / `a3` / `a5`。
- `<操作系统>`：基础操作系统，`ubuntu22.04` / `openeuler24.03`。
- `<python版本>`：Python 版本，当前统一 `py3.12`。

## 【关联】

- **`./OVERVIEW.md`**（英文版）：与本文同义的中文镜像概览，提供英文检索路径，二者内容应保持镜像 Tag 矩阵一致。
- **`../docs/zh/user_guide/quick_start.md`**（用户指南 - 快速入门）：本文"使用 Motor"小节直接指引用户前往该文档，说明该文档负责"镜像拉取后如何启动 / 部署 MindIE-Motor 集群"等运行时步骤，与本文的"如何选镜像 / 如何本地构建"形成上下游：本文负责镜像层入口，快入门负责运行时入口。
- **`Supported Tags`（`docker/supported_tags.md`）**：覆盖 3.0.x 历史 Tag，本文明确告知历史命名"使用另一套命名"，需跳转查阅，构成版本演进的历史回溯关联。
- **AscendHub 仓库**：所有 Tag 镜像的实际托管位置，与本文 Tag 表一一对应，是镜像下载来源。
- **MindIE 社区与昇腾开发者社区**：能力归属与帮助/问题反馈渠道，构成外部生态关联。
- **`build.sh`**：在本地构建时被调用，负责安装 `motor` / `ccae_reporter`，是构建流程中的下游安装步骤（原文未给出 `build.sh` 内部细节）。
- **`ccae_reporter`**：与 `motor` 一同被打入镜像，定位为附属组件（原文未展开其职责）。

## 【使用方法】

**前置准备**（原文标注"可选"但实际为本地构建/运行的前置）：
- 宿主机已安装固件与驱动（参考昇腾官方"安装驱动和固件"文档）。
- 宿主机已安装 Docker 与 k8s。

**直接使用官方镜像**：
- 镜像名：`mindie-motor`，仓库为 AscendHub 上的 `mindie-motor` 仓库。
- 选取符合本地环境的 Tag（按 芯片系列/OS/架构 选），拉取后启动容器即可，具体运行步骤需参考 [快速入门](../docs/zh/user_guide/quick_start.md)。

**本地构建**（原文给出的完整命令，需在项目根目录执行，将 `<tag>` 替换为目标组合）：

```bash
TAG="3.1.0-vllm_ascend0.23.0-a2-ubuntu22.04-py3.12"

docker build --network=host \
    --platform=linux/arm64 \
    -t "mindie-motor:${TAG}" \
    -f "docker/mindie-motor-vllm/${TAG}/Dockerfile" \
    .
```

- `--network=host`：使用宿主机网络（原文示例值，便于拉取依赖）。
- `--platform=linux/arm64`：示例为 arm64，需按宿主实际架构替换为 `linux/amd64` 或保持 `linux/arm64`；各 Dockerfile 头部注释中已写明对应的 `--platform`、源码仓库信息与完整 `docker build` 命令，可直接复制使用。
- `-t "mindie-motor:${TAG}"`：构建产物镜像名。
- `-f "docker/mindie-motor-vllm/${TAG}/Dockerfile"`：Dockerfile 路径与 Tag 字面拼接一致。
- 构建上下文为当前目录（`.`），但因 Dockerfile 内部自动 clone 源码，原文说明"无需本地源码或构建上下文"。

**配置项 / 环境变量**：原文未涉及镜像内运行时配置项（如 service 端口、调度参数等），这些属于 [快速入门](../docs/zh/user_guide/quick_start.md) 范围。
