# MindIE Docker

> 仓 `mindie-llm` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docker/OVERVIEW.md

# MindIE Docker Overview 深度解读

## 【定位】

本文档是 MindIE 推理引擎容器化交付体系的说明文档,聚焦于如何通过自动化构建脚本与多阶段 Dockerfile,把已编译的 MindIE LLM / SD / Motor 包、CANN 工具链、PyTorch + torch_npu (PTA) 及 Python 运行环境,统一打包成可在 Atlas 服务器上直接拉起推理服务的 Docker 镜像。

---

## 【技术要点】

1. **多阶段 Dockerfile(7 阶段)**:通过 `base-ubuntu` / `base-openeuler` 两条互斥的操作系统底座分支,汇入统一的 `base` 阶段,再依次叠加 `cann` → `pta` → `mindstudio` → `mindie` 四个层,实现"一次定义、双 OS 输出"。
2. **8 路并行下载加速**:`modules/download.sh` 对 PTA、Python 源码(仅 Ubuntu)、CANN Toolkit / NNAL / Kernels、MindIE-LLM / SD / Motor 共 8 类资源并发拉取。
3. **标签驱动的多维矩阵**:`<MindIE-version>-<product-series>-<python-version>-<os>-<arch>` 五段式镜像标签,把版本、芯片产品线、Python、操作系统、CPU 架构一次性固化在镜像名上。
4. **芯片参数 → 产品线映射**:通过 `modules/config.sh` 把 `--chip=310|910|A3` 翻译为 `300I-Duo` / `800I-A2` / `800I-A3` 三种 Atlas 产品系列。
5. **入口脚本分层职责**:`build.sh` 做参数解析与编排,`modules/config.sh` 做校验与元数据,`modules/download.sh` 做下载,`modules/build_image.sh` 做镜像标签计算、Docker build 与 `.tar.gz` 导出,职责清晰可独立替换。
6. **三类安装源镜像**:`swr.cn-north-4.myhuaweicloud.com/inference`(底座预拉镜像)、`ascend-repo.obs.cn-east-2.myhuaweicloud.com`(CANN)、`mirrors.huaweicloud.com/python` + 各 `gitcode.com` 仓库 Release 路径,构建过程无需直连外网专有源。

---

## 【关键机制与数据】

- **构建流水线四步**(原文):参数解析与校验 → 8 路并行下载 → Docker 多阶段构建 → 镜像导出为 `output/*.tar.gz`。
- **Dockerfile 7 阶段拓扑**(原文):`base-ubuntu ──┐` / `base-openeuler┘` 双分支汇入 `base → cann → pta → mindstudio → mindie`,共 7 个 stage(含 Stage 4.5 mindstudio 工具链层)。
- **Stage 1a / 1b 差异**(原文):Ubuntu 24.04 需要**源码编译 Python**;OpenEuler 24.03 使用**预装 Python**;因此 Python 源码 tarball 仅在 Ubuntu 分支下载。
- **运行时默认参数**(原文):`MINDIE_LLM_CONTINUOUS_BATCHING` 默认 `1`(开启 Continuous Batching),`ASCEND_GLOBAL_LOG_LEVEL` 默认 `3`。
- **环境前置条件**(原文):宿主机 Docker 版本 ≥ **24.x.x**,构建目录磁盘 ≥ **~50GB+**(含下载与构建缓存),需可访问 Atlas OBS 镜像与华为云 PyPI 镜像。
- **默认 Python 版本**(原文):未传 `--python` 时,使用 `3.11.10`;`--type` 未传时使用 `whl` 包类型。
- **MindIE 引擎能力**(原文):支持行业标准模型推理、多请求调度,内置 **Continuous Batching、PagedAttention、FlashDecoding** 三种性能特性。
- **性能/基准数字**:原文未提供任何 benchmark 数字。

---

## 【表格解读】

### 表 1 · File Overview

| File | Description |
|------|-------------|
| [build.sh](./build.sh) | Main entry point — argument parsing, validation, download orchestration, and build invocation |
| [Dockerfile](./Dockerfile) | Multi-stage Docker build file (7 stages) |
| [modules/config.sh](./modules/config.sh) | Central configuration: URL templates, logging, validation, arch detection, Chip/OS metadata |
| [modules/download.sh](./modules/download.sh) | Download layer: 8 parallel downloads for PTA / Python / CANN / MindIE-LLM / MindIE-SD / MindIE-Motor packages |
| [modules/build_image.sh](./modules/build_image.sh) | Build orchestration layer: image tag computation, Docker build, image export |

**逐行解读:**
- `build.sh` 是面向用户的**唯一入口**,负责把 8 个 `--xxx` 参数解析后,串联调用 config → download → build_image 三个模块;它不直接做下载,只做"编排"。
- `Dockerfile` 以 7 个 stage 描述**最终镜像如何被分阶段烤出来**,不包含任何业务脚本逻辑。
- `modules/config.sh` 是**配置中心**:集中存放 URL 模板、日志、参数校验、架构探测以及"chip → OS/产品线"等元数据,改一处全链路生效。
- `modules/download.sh` 专责**8 路并发取包**,对 8 类资源统一调度,便于后续增加新依赖只需改本文件。
- `modules/build_image.sh` 负责**把前面下载到的制品组装成镜像**:包括镜像 tag 拼接、调用 `docker build`、最后导出 `.tar.gz` 落到 `output/`。

---

### 表 2 · Tag Specification

| Field | Example | Description |
|-------|---------|-------------|
| `MindIE-version` | `3.0.0` | MindIE version number (drives LLM / SD / Motor) |
| `product-series` | `800I-A2`, `800I-A3`, `300I-Duo` | Target Atlas product series |
| `python-version` | `py3.11` | Python version |
| `os` | `ubuntu24.04`, `openeuler` | Base operating system |
| `arch` | `x86_64`, `aarch64` | CPU architecture |

**逐行解读:**
- `MindIE-version` 字段一旦确定,**LLM / SD / Motor 三个子组件版本被同时驱动**,意味着 MindIE 三个仓库必须发版对齐。
- `product-series` 直接决定了后续 Dockerfile 中 CANN Kernels 包的选择(芯片相关算子包按产品线分发)。
- `python-version` 简写为 `py3.11` 而非完整 `3.11.10`,说明镜像标签只标**主次版本**,完整版本在 `--python` 内部参数中体现。
- `os` 仅两种:`ubuntu24.04` 与 `openeuler`,对应 Dockerfile Stage 1a / 1b 的两条入口分支。
- `arch` 决定底座基础镜像的 CPU 指令集,`aarch64` 主要面向 ARM 服务器的 Atlas 800I A2/A3。

---

### 表 3 · Product Series Mapping

| Chip Parameter | Product Series | Description |
|----------------|---------------|-------------|
| `310` | `300I-Duo` | Atlas 300I Duo |
| `910` | `800I-A2` | Atlas 800I A2 |
| `A3` | `800I-A3` | Atlas 800I A3 |

**逐行解读:**
- 用户在 CLI 上输入的是**芯片代号**(`310` / `910` / `A3`),由 `config.sh` 在内部翻译成**对外可见的产品系列名**(`300I-Duo` / `800I-A2` / `800I-A3`)。
- 这种"输入芯片,输出产品"的设计,把硬件细节与商业命名解耦,便于后续增加新芯片时只改映射表。
- Atlas 300I Duo 是面向推理的边缘卡,800I A2 / A3 是数据中心 AI 服务器,三者共用同一套 Dockerfile 框架。

---

### 表 4 · Build Parameters

| Parameter | Description | Required | Default | Example |
|-----------|-------------|----------|---------|---------|
| `--os` | Server operating system | Yes | — | ubuntu / openeuler |
| `--chip` | Atlas device model | Yes | — | 310 / 910 / A3 |
| `--arch` | System architecture | Yes | — | x86_64 / aarch64 |
| `--mindie` | MindIE version (drives LLM / SD / Motor) | Yes | — | 3.0.0 |
| `--cann` | CANN version | Yes | — | 9.0.0 |
| `--pta-tag` | PTA release tag | Yes | — | v26.0.0-pytorch2.9.0 |
| `--type` | Package type | No | `whl` | whl / run |
| `--python` | Python version | No | `3.11.10` | 3.11.6 |
| `--dry-run` | Validate and show config only | No | `false` | — |

**逐行解读:**
- 6 个必传参数构成了"硬件 + 操作系统 + 软件栈版本"的最小闭环:任何一项缺失,镜像就失去可复现性。
- `--mindie` 一个版本号同时拉齐 LLM/SD/Motor,印证了表 2 中 `MindIE-version` 是"总开关"的设定。
- `--cann` 必须与 `--pta-tag` 严格对齐(PTA 自身内含与特定 CANN 的耦合关系),否则可能踩到算子不兼容。
- `--type` 默认 `whl`,若选择 `run`,将下载并安装 `.run` 整包,通常对应一体化部署包而非 pip 包。
- `--python` 默认 `3.11.10`,与 tag 中 `py3.11` 是"粗粒度标签 + 细粒度内部参数"的两层表达。
- `--dry-run` 提供"只校验不构建"的逃生通道,适合 CI 中做 smoke test,避免一次错误参数跑完整条 8 路下载 + 7 阶段烤镜像。

---

### 表 5 · Download Sources

| Component | Source |
|-----------|--------|
| MindIE-LLM | `https://gitcode.com/Ascend/MindIE-LLM/releases/download` |
| MindIE-SD | `https://gitcode.com/Ascend/MindIE-SD/releases/download` |
| MindIE-Motor | `https://gitcode.com/Ascend/MindIE-Motor/releases/download` |
| PTA (torch_npu) | `https://gitcode.com/Ascend/pytorch/releases/download` |
| CANN | `https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN` |
| Python Source | `https://mirrors.huaweicloud.com/python` |

**逐行解读:**
- 三个 MindIE 子组件与 PTA 都从 `gitcode.com` 的 Release 通道拉取,与外部社区仓库对齐,**保证用户拉到的就是社区可见的开源版本**。
- CANN 单独走华为云 OBS(`ascend-repo.obs.cn-east-2`),说明 CANN 包未开源在 gitcode,需凭华为云账号/镜像可达。
- Python 源码走 `mirrors.huaweicloud.com`(华为云 PyPI/源码镜像),只有 Ubuntu 分支会真正下载(因为 openEuler 自带 Python)。

---

### 表 6 · Supported Hardware

| Chip Series | Product Examples | Architecture |
|-------------|-----------------|--------------|
| Atlas 910 | Atlas 800I A2 | ARM64 |
| Atlas A3 | Atlas 800I A3 | ARM64 |
| Atlas 310 | Atlas 300I Duo | ARM64 / x86_64 |

**逐行解读:**
- Atlas 910 / A3 仅支持 **ARM64**,意味着这两条产品线的镜像**没有 `--arch=x86_64` 的构建路径**,即使强行传入也会被校验拒绝。
- Atlas 310 同时支持 ARM64 与 x86_64,说明其**底座镜像有两种 arch 变体**,构建时 `--arch` 真正起作用。
- 三款芯片中,910 与 A3 同属高端训练/推理服务器,310 属于边缘推理卡,文档以同一表格统一展示,说明 Docker 体系是**横跨训练卡与推理卡**的统一交付。

---

### 表 7 · Container Environment Variables

| Variable | Description |
|----------|-------------|
| `ASCEND_TOOLKIT_HOME` | CANN toolchain installation path |
| `MINDIE_LLM_HOME_PATH` | MindIE-LLM service installation path |
| `MIES_INSTALL_PATH` | MindIE-Motor (mindie-service) installation path |
| `ATB_SPEED_HOME_PATH` | ATB-LLM acceleration library path |
| `MINDIE_LLM_CONTINUOUS_BATCHING` | Continuous batching toggle (default 1) |
| `ASCEND_GLOBAL_LOG_LEVEL` | Global log level (default 3) |

**逐行解读:**
- 前四个变量是**路径类**(`*_HOME_PATH` / `*_INSTALL_PATH`),给容器内的可执行文件、动态库、模型权重提供固定查找根,降低业务脚本硬编码成本。
- `MIES_INSTALL_PATH` 中的 "MIES" 即 **MindIE-Service**(编排服务 Motor)的缩写,文档用括号补全,避免读者误读。
- `ATB_SPEED_HOME_PATH` 指向 **ATB-LLM 加速库**,这是 MindIE-LLM 推理性能的核心算子后端。
- `MINDIE_LLM_CONTINUOUS_BATCHING=1` 默认开启,与文档开头宣传的"Continuous Batching 特性"对齐——**镜像里直接默认打开,而非让用户自行启用**。
- `ASCEND_GLOBAL_LOG_LEVEL=3` 是 CANN 全局日志级别,3 通常对应"WARNING",说明默认**只记录告警及以上**,避免推理时刷屏。

---

## 【公式解读】

原文无公式。

文档中出现的两类"准公式"仅作说明:

- **镜像标签格式**(原文,以伪模板形式给出):
  ```text
  mindie:<MindIE-version>-<product-series>-<python-version>-<os>-<arch>
  ```
  其中 `<...>` 是占位符,具体取值见上方表 2;该式不是数学公式,而是镜像命名约定。
- **Stage 拓扑图**(原文):
  ```text
  base-ubuntu ──┐
                ├──> base ──> cann ──> pta ──> mindstudio ──> mindie
  base-openeuler┘
  ```
  箭头 `──>` 表示**构建阶段依赖顺序**(前一层是后一层的 FROM);两侧分支表"二选一汇合"。

---

## 【关联】

- **`build.sh`** ↔ `Dockerfile`:前者计算好镜像 tag 与 build 参数后,调用 `docker build` 触发后者;二者通过 `--build-arg` / 上下文目录耦合。
- **`modules/config.sh`** 是**所有模块的真值源**:它输出的 URL 模板、芯片 → 产品线映射、合法 OS/Arch 集合,被 `download.sh`(决定去哪下)与 `build_image.sh`(决定 tag 怎么拼)共同消费;修改一处即影响全链路。
- **`modules/download.sh`** ↔ `modules/build_image.sh`:下载产物落到本地缓存目录,`build_image.sh` 在 `docker build` 时通过 `COPY` 把这些包送入 Dockerfile 各 Stage。
- **MindIE 子组件三件套**:文档反复强调 LLM / SD / Motor 三者**共享同一 `--mindie` 版本号**,意味着下游仓库 Ascend/MindIE-LLM、Ascend/MindIE-SD、Ascend/MindIE-Motor 的 Release 必须保持版本对齐;构建脚本会在一次构建中并发拉取三者。
- **上游社区**:PTA 取自 Ascend/pytorch 仓库,CANN 取自 Atlas Community 下载页(原文以脚注形式给出链接),MindIE 镜像底座来自 `swr.cn-north-4.myhuaweicloud.com/inference` 镜像仓——本仓库相当于把这些上游制品**重新装配**为带 CANN + PTA + MindIE 的"全家桶"镜像。
- **许可证**:最终镜像中的 Python、系统库等预装软件**各自保留原许可**,与顶层 [../LICENSE.md](../LICENSE.md) 中的 MindIE 许可叠加生效。

---

## 【使用方法】

**原文已给出完整 Quick Start,核心命令归纳如下:**

**1. 典型构建(whl 包 + 默认 Python 3.11.10):**
```bash
bash build.sh \
    --os=ubuntu \
    --chip=910 \
    --arch=x86_64 \
    --mindie=3.0.0 \
    --cann=9.0.0 \
    --pta-tag=v26.0.0-pytorch2.9.0
```

**2. run 包 + 自定义 Python 版本(OpenEuler + ARM 边缘卡):**
```bash
bash build.sh \
    --os=openeuler \
    --chip=310 \
    --arch=aarch64 \
    --mindie=3.0.0 \
    --cann=9.0.0 \
    --pta-tag=v26.0.0-pytorch2.9.0 \
    --type=run \
    --python=3.11.6
```

**3. 仅校验(不真正构建,适合 CI):**
```bash
bash build.sh \
    --os=ubuntu --chip=910 --arch=x86_64 \
    --mindie=3.0.0 --cann=9.0.0 \
    --pta-tag=v26.0.0-pytorch2.9.0 \
    --dry-run
```

**4. 前置依赖(原文 Prerequisites):**
- 宿主机 Docker ≥ **24.x.x**
- 构建目录磁盘 ≥ **~50GB+**
- 可访问 Atlas OBS 镜像 + 华为云 PyPI 镜像

**5. 产出物位置:** 镜像以 `.tar.gz` 形式导出到 `output/` 目录(原文 Build Pipeline 第 4 步)。

**6. 拉起推理服务后关键环境变量(由镜像内置,无需手动 export):**
- `MINDIE_LLM_CONTINUOUS_BATCHING=1`(Continuous Batching 默认开启)
- `ASCEND_GLOBAL_LOG_LEVEL=3`(CANN 日志默认级别)
- 其余路径类变量见表 7。

**7. 镜像预拉(可选):** 若需复用官方基础层,可从 `swr.cn-north-4.myhuaweicloud.com/inference` 镜像仓预拉底座镜像(原文 Image Registry 一节)。
