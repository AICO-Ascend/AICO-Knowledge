# MindSpeed MM Docker Image Overview

> 仓 `mindspeed-mm` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docker/OVERVIEW.md

# MindSpeed MM Docker Image Overview — 一体化深度解读

## 【定位】

本篇文档定位为 **MindSpeed MM 多模态大模型套件官方 Docker 镜像的"门面说明"（Overview）**，解决的是用户拿到一个 `mindspeed-mm` 镜像后"它是什么、能装在哪、tag 该怎么读、镜像怎么拉/怎么用、目录结构如何组织"的问题,相当于 docker 子仓的总入口 README,并链接到 Dockerfile、build.sh、supported_tags.md 等具体实现细节。

---

## 【技术要点】

1. **套件定位**:MindSpeed MM 是面向华为 Atlas 芯片的多模态大模型套件,提供端到端多模态训练方案,涵盖预置主流模型、数据工程、分布式训练与加速、预训练、微调、后训练、在线推理。
2. **基础镜像环境**:同时基于 Ubuntu 22.04 与 openEuler 24.03 双 OS,支持 x86_64 与 aarch64(ARM64)两种 CPU 架构。
3. **预装基础依赖**(仅这三项基础依赖,其它依赖需按模型 README 自行安装):
   - PyTorch + TorchNPU(深度学习框架)
   - **decord 0.6.0**(高性能视频解码库)
   - CANN(华为 Atlas AI 处理器基础软件栈)
4. **镜像 Tag 命名模板**:**`{version}-{CANN version}-{TorchNPU version}-{product info}-{OS}-{Python version}`**——所有字段必填、顺序固定、分隔符统一为 `-`。
5. **Tag 字段细则**:版本号形如 `v26.0.0`/`v26.1.0`(v 表示版本,数字代表分支);CANN 版本格式 `cann9.1.0`;TorchNPU 版本格式 `torch_npu2.7.1.post8`;product info 为 NPU 芯片类型(小写:`910b`/`a3`/`950`);OS 形如 `openeuler24.03`/`ubuntu22.04`;Python 形如 `py3.11`。
6. **多架构与本地构建差异**:仓库 tag 为 x86+aarch64 合包,**不带** `x86_64`/`aarch64` 后缀;只有本地通过 Dockerfile 构建时,才会生成带 `-x86_64`/`-aarch64` 后缀的 tag。
7. **Dockerfile 双层结构**:`Dockerfile` 是统一 dev 镜像构建文件,通过 build arg 支持全部 NPU 类型(910b/a3/950)与 OS;`Dockerfile.ci` 是 CI 镜像,在 dev 镜像之上叠加多版本 conda 环境,通过 `--build-ci` 启用。
8. **构建脚本默认版本**:`docker/build.sh` 使用 `-v` 参数指定的版本号(**默认:26.1.0**)作为 git clone MindSpeed-MM 的分支。
9. **构建参数机制**:CANN 版本、NPU 类型(910b/a3/950)、OS、Python 版本默认由基础镜像 tag 派生;Python 版本可被 `--python-version` 覆盖;TorchNPU 版本由 `--torch-npu-version` 参数指定。
10. **驱动路径说明**:默认 NPU 驱动路径为 `/usr/local/Ascend/driver`;若不在默认路径,运行 docker 命令时需通过环境变量或参数补充路径(原文以 `/usr/local/npu/driver` 为例,后文被截断)。

---

## 【关键机制与数据】

- **镜像仓库**:Quay.io 上的 `ascend/mindspeed-mm`(`原文:`[Quay.io](https://quay.io/repository/ascend/mindspeed-mm?tab=tags)),用户在此获取 `docker pull` 命令。
- **源代码仓库**:[https://gitcode.com/Ascend/MindSpeed-MM](https://gitcode.com/Ascend/MindSpeed-MM),License 为 Apache-2.0。
- **当前最新版本系列**:`v26.1.0`,搭配 `cann9.1.0` + `torch_npu2.7.1.post8`(`原文:`Latest Version v26.1.0)。
- **组合矩阵(原文共 6 条最新 tag)**:覆盖 NPU(910B/A3/950)× OS(openEuler 24.03 / Ubuntu 22.04)的 6 种组合,均为 x86_64/aarch64 合包。
- **多架构分发机制**:`原文:`"The tags in the image repository are multi-architecture images combining x86 and aarch64, and **do not** include the `x86_64`/`aarch64` architecture suffix." 即官方 tag 同一字符串覆盖两架构,只在本地 build 时才拆出 `-x86_64` / `-aarch64` 后缀。
- **构建派生规则**:`原文:`"The CANN version, NPU type (910b/a3/950), OS, and Python version are derived from the base image tag by default; the Python version can be overridden with `--python-version`. The TorchNPU version comes from the `--torch-npu-version` parameter."——表明 base image tag 决定四个字段,TorchNPU 独立于 base tag 来自 `--torch-npu-version`。
- **依赖按模型后装机制**:`原文:`"Due to differences in dependencies between models, only the above basic dependencies are pre-installed in the image." 这是镜像"瘦身"的明确说明,模型级依赖不在镜像内,迁移到用户进入容器后手动安装。

> **说明**:原文"1. Image Usage Guide" 一节中给出的 `docker run` 样例在 `LD_LIBRARY_PATH="/usr/loca` 处被截断,因此**实际完整 run 命令、`-v` 挂载、NPU 设备透传等具体参数在本文可见范围内未给出**。

---

## 【表格解读】

### 表 1:Quick Reference(快速参考)

| Item | Description |
| ------ | ------ |
| **Image Name** | mindspeed-mm |
| **Maintainer** | MindSpeed MM Team |
| **Source Repository** | [https://gitcode.com/Ascend/MindSpeed-MM](https://gitcode.com/Ascend/MindSpeed-MM) |
| **Dockerfile Path** | `docker/` |
| **License** | Apache-2.0 |

**逐行解读**:
- **Image Name = mindspeed-mm**:这是 Quay.io 上的镜像名,即 `docker pull` 时使用的 repo。
- **Maintainer = MindSpeed MM Team**:维护方是项目自有团队,意味着 tag 演进与 MindSpeed-MM 主仓分支强耦合(后文 tag 中 `v26.1.0` 即对应 `26.1.0` 分支)。
- **Source Repository = gitcode.com/Ascend/MindSpeed-MM**:源代码托管位置,Dockerfile、build.sh 等都在其中 `docker/` 目录下。
- **Dockerfile Path = docker/**:构建上下文为仓库根下的 `docker/` 子目录。
- **License = Apache-2.0**:Apache-2.0 开源许可,意味着使用与再分发均需遵循 Apache-2.0 条款。

### 表 2:Image Tag Key Fields(Tag 字段说明)

| Field | Mandatory | Description | Example Values |
| ------ | ------ | ------ | -------- |
| version | Yes | MindSpeed MM version identifier (v indicates version; the number represents the branch) | v26.0.0, v26.1.0 |
| CANN version | Yes | `cann` + version number | cann9.1.0 |
| TorchNPU version | Yes | `torch_npu` + version number | torch_npu2.7.1.post8 |
| product info | Yes | NPU chip type (lowercase) | 910b, a3, 950 |
| OS | Yes | Operating system | openeuler24.03, ubuntu22.04 |
| Python version | Yes | `py` + version number | py3.11 |

**逐行解读**:
- **version**:必填,语义双层——`v` 前缀标识这是版本 tag,数字部分同时是 git 分支号(如 `v26.1.0` 对应分支 `26.1.0`),所以 `build.sh` 的 `-v` 与 git 分支天然对齐。
- **CANN version**:必填,前缀 `cann` 是固定字面量,后跟纯版本号(例 `9.1.0`),用于匹配华为 CANN 软件栈版本。
- **TorchNPU version**:必填,前缀 `torch_npu` 固定,版本号允许带 `postN` 后缀(例 `2.7.1.post8`),表明这是 post-release 修订版。
- **product info**:必填,小写 NPU 型号,目前支持 **910b、A3、950** 三类,决定了镜像内 CANN 配套芯片相关组件的目标硬件。
- **OS**:必填,目前两种取值 `openeuler24.03` / `ubuntu22.04`,分别对应 openEuler 24.03 与 Ubuntu 22.04。
- **Python version**:必填,前缀 `py` 固定,当前取值 `py3.11`,原文示例中仅给出 3.11,但文档注明可被 `--python-version` 覆盖,意味着其它 Python 版本理论上也可派生。

### 表 3:Example Tags(Tag 拆解示例)

| Tag | version | CANN | TorchNPU | NPU | OS | Python |
| ----- | ----- | ----- | ----- | ----- | --------- | -------- |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11` | v26.1.0 | 9.1.0 | 2.7.1.post8 | A3 | openEuler 24.03 | 3.11 |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11` | v26.1.0 | 9.1.0 | 2.7.1.post8 | 910B | openEuler 24.03 | 3.11 |

**逐行解读**:
- 第一行:`v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11` —— MindSpeed-MM 分支 26.1.0、CANN 9.1.0、TorchNPU 2.7.1.post8、目标 Atlas **A3** 服务器、openEuler 24.03、Python 3.11。
- 第二行:仅 `a3` 改为 `910b`,语义切换为 Atlas **910B**;其余五字段完全一致,直观展示 product info 是 tag 唯一变化位,体现 chip type 的正交切换能力。
- 两行同时说明:在最新 v26.1.0 系列下,CANN/TorchNPU/OS/Python 是**冻结**的组合,变体只发生在 NPU 型号上。

### 表 4:Tag Meaning Explanation(逐字段释义)

| Field | Value | Meaning |
| ------ | ------ | ------ |
| version | `v26.1.0` | MindSpeed MM Git tag (branch: 26.1.0) |
| CANN version | `cann9.1.0` | Based on CANN 9.1.0 |
| TorchNPU version | `torch_npu2.7.1.post8` | TorchNPU 2.7.1.post8 |
| product info | `a3` | For Atlas A3 servers |
| OS | `openeuler24.03` | Based on openEuler 24.03 |
| Python version | `py3.11` | Python 3.11 |

**逐行解读**:
- **version=v26.1.0**:对应 MindSpeed-MM 的 **Git tag**,且与同名的 git **branch** 一一对应,便于脚本(`-v`)直接 checkout。
- **CANN version=cann9.1.0**:镜像基座所基于的 CANN 主版本为 **9.1.0**。
- **TorchNPU version=torch_npu2.7.1.post8**:对应的 TorchNPU 为 **2.7.1.post8** 版本。
- **product info=a3**:明确目标硬件为 **Atlas A3 服务器**。
- **OS=openeuler24.03**:基于 **openEuler 24.03** 操作系统。
- **Python version=py3.11**:Python **3.11**。

### 表 5:Supported Tags and Dockerfile Links(v26.1.0 全量 tag)

| Tag | Dockerfile | Description |
| --- | --- | --- |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 910B + openEuler 24.03, x86_64/aarch64 combined |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 910B + Ubuntu 22.04, x86_64/aarch64 combined |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | A3 + openEuler 24.03, x86_64/aarch64 combined |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-ubuntu22.04-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | A3 + Ubuntu 22.04, x86_64/aarch64 combined |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 950 + openEuler 24.03, x86_64/aarch64 combined |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-ubuntu22.04-py3.11` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile) | 950 + Ubuntu 22.04, x86_64/aarch64 combined |

**逐行解读**:
- 6 行 tag 共用同一份 Dockerfile 链接(均指向 `26.1.0` 分支的 `docker/Dockerfile`),说明**一份 Dockerfile + build arg** 即覆盖所有组合。
- 矩阵 = **3 NPU(910b / a3 / 950)× 2 OS(openeuler24.03 / ubuntu22.04)** = 6 tag,正交穷尽。
- 每行 Description 显式标注 "x86_64/aarch64 combined",强调此为官方多架构合包镜像,无需用户按 CPU 架构挑选 tag。

### 表 6:Project Directory Structure(目录结构树)

文档以 `text` 代码块给出(此处转写为树形):

```
docker/
├── Dockerfile                 # Unified dev image Dockerfile, supporting multiple NPU types and OS versions
├── Dockerfile.ci              # CI image Dockerfile (stacked on top of the dev image)
├── build.sh                   # Image build script, supporting various parameter configurations
├── OVERVIEW.md                # English documentation
├── OVERVIEW.zh.md             # Chinese documentation
├── supported_tags.md          # Historical tag list
└── scripts/                   # Script directory
    └── ci/                    # CI build scripts and version configuration
```

**逐行解读**:
- `Dockerfile`:dev 镜像统一构建入口,支持多 NPU 类型与多 OS,通过 build arg 区分。
- `Dockerfile.ci`:CI 镜像,层级在 dev 镜像之上叠加多版本 conda 环境,需用 `--build-ci` 启用。
- `build.sh`:统一构建脚本,提供参数化与自动检测能力。
- `OVERVIEW.md` / `OVERVIEW.zh.md`:本篇文档的中英双语版(当前解析的为英文版)。
- `supported_tags.md`:历史 tag 总表,链接于"Supported Tags"小节末尾,供查阅历史版本镜像。
- `scripts/`:按功能组织脚本,`ci/` 子目录专门存放 CI 构建脚本与版本配置。

---

## 【公式解读】

原文无公式(`原文无公式`)。

唯一出现的"模板表达式"为 tag 命名模板:

```
{version}-{CANN version}-{TorchNPU version}-{product info}-{OS}-{Python version}
```

它**不是数学公式**而是**字面字符串模板**,6 个占位符的含义已在【表格解读】表 2 中逐项说明,此处不重复展开。

---

## 【关联】

本 OVERVIEW 作为 docker 子仓的总入口,与下列模块/特性存在显式或隐式关联:

- **`docker/Dockerfile`**(唯一构建入口):v26.1.0 全部 6 条 tag 均链接到 `26.1.0` 分支同一 Dockerfile;通过 build arg(隐式)切 NPU/OS 组合,文档链接 `https://gitcode.com/Ascend/MindSpeed-MM/blob/26.1.0/docker/Dockerfile`。
- **`docker/Dockerfile.ci`**:CI 镜像层,通过 `--build-ci` 在 dev 镜像之上叠加多版本 conda 环境,与 `scripts/ci/` 配套使用。
- **`docker/build.sh`**:构建脚本入口;`-v` 默认 `26.1.0` 对应 git 分支;`--python-version` 覆盖 Python 版本;`--torch-npu-version` 覆盖 TorchNPU 版本。
- **`docker/supported_tags.md`**:历史版本 tag 集合,文档末尾注明 "For all tags of historical versions, please refer to Supported Tags",URL 为 `https://gitcode.com/Ascend/MindSpeed-MM/blob/master/docker/supported_tags.md`。
- **`docker/scripts/ci/`**:CI 构建脚本与版本配置目录,服务于 CI 镜像流水线。
- **`docker/OVERVIEW.zh.md`**:本篇中文翻译版,与本文件同源、互译。
- **上游 MindSpeed-MM 主仓**:镜像 tag 中的 `version` 字段直接对应 MindSpeed-MM 的 Git branch(如 `26.1.0`),因此镜像与主仓代码版本天然对齐。
- **外部镜像源 Quay.io**:分发渠道 `ascend/mindspeed-mm`,提供 `docker pull` 命令。
- **下游模型 README**:文档明确"用户需按目标模型 README 在基础环境中手动安装额外依赖",意味着 docker 镜像只提供基础栈,模型专属依赖由各自 README 指引,这是与各模型模块的松耦合接口。

---

## 【使用方法】

> **重要提示**:原文"1. Image Usage Guide" 一节的 `docker run` 样例在 `LD_LIBRARY_PATH="/usr/loca` 处被截断,**完整 run 命令、挂载、设备透传、环境变量在原文可见范围内未给出**。因此下文仅基于原文已明确出现的部分说明使用方法。

- **拉取镜像**:`原文:`"Image download: Please visit Quay.io to get the corresponding `docker pull` command."——具体 `docker pull` 命令需去 Quay.io 的 `ascend/mindspeed-mm` tags 页面获取(原文未贴出具体命令字符串)。
- **手动安装模型依赖**:`原文:`"After pulling the image and starting a container, users need to manually install the additional dependencies required by the target model in the base environment according to the target model's README file."——进入容器后,按各模型 README 安装额外依赖。
- **NPU 驱动路径覆盖**:`原文:`"If the NPU driver is not installed in the default path (/usr/local/Ascend/driver), you need to add the path information in the command when running the following docker commands. Taking the path '/usr/local/npu/driver' as an example:"——若驱动不在 `/usr/local/Ascend/driver`,需在 docker run 命令中补充路径(原文示例路径 `/usr/local/npu/driver`),具体命令片段在原文截断处之后。
- **本地构建(dev 镜像)**:`原文:`通过 `docker/Dockerfile`,由 `docker/build.sh` 驱动,使用 `-v` 指定分支(默认 `26.1.0`);NPU 类型/OS 由 base image tag 派生;`--python-version` 与 `--torch-npu-version` 可覆盖 Python 与 TorchNPU 字段;本地构建产物 tag 会带 `-x86_64` / `-aarch64` 后缀。
- **本地构建(CI 镜像)**:`原文:`启用 `Dockerfile.ci` 需加 `--build-ci` 参数,会在 dev 镜像之上叠加多版本 conda 环境。
- **运行启动命令(原文已截断部分)**:`原文未涉及`完整 `docker run` 命令(仅显示到 `LD_LIBRARY_PATH="/usr/loca` 即中断)。
