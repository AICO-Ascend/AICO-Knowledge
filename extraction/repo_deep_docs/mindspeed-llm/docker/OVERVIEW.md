# MindSpeed LLM Docker Image Overview

> 仓 `mindspeed-llm` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docker/OVERVIEW.md

# docker/OVERVIEW.md 深度解读

## 【定位】

该文档是 MindSpeed-LLM（昇腾 LLM 分布式训练套件）官方 Docker 镜像仓库 `docker/` 的英文总览（OVERVIEW），用于解答"如何拉取、识别、命名以及在本地重建该框架容器镜像"的问题，定位为**镜像使用与构建的索引式参考手册**。

---

## 【技术要点】

1. **镜像命名规范**：所有 tag 严格遵循模板 `v{MindSpeed LLM Version}-cann{CANN Version}-torch_npu{TorchNPU Version}-{ChipType}-{OS}-py{Python Version}`，例如 `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.12`，版本号 `26.1.0` 同时充当 Git 分支名。
2. **多架构多芯组合**：发布态 tag 同时合并 `x86_64` 与 `aarch64` 两个架构，因此官方 tag 中不含 `-x86_64` / `-aarch64` 后缀；而本地构建脚本 `image_build.sh` 仍默认带宿主机架构后缀。
3. **三种 NPU 芯片支持**：覆盖 `910b`（Atlas A2 训练产品）、`a3`（Atlas A3 训练产品）、`950`（Ascend 950 系列），同时支持 `openeuler24.03` 与 `ubuntu22.04` 两个操作系统。
4. **核心软件栈版本组合（26.1.0 发布态）**：CANN 9.1.0 / PyTorch 2.7.1 / Triton-Ascend 3.2.2 / MindSpeed `26.1.0_core_r0.12.1` / MindSpeed-LLM 26.1.0 / Megatron-LM `core_v0.12.1` / FSDPTurbo `main`。
5. **构建脚本可覆盖参数**：`image_build.sh` 默认与最新发布 tag 对齐，提供 14 个可覆盖项，包括 NPU 类型、OS、各 Git 分支、CANN/PyTorch/TorchNPU/Triton-Ascend/FLA NPU 版本、基础镜像、`--no-cache`、`--cleanup-on-fail` 等。
6. **FLA NPU 算子构建**：构建过程中会在克隆 `flash-linear-attention-npu` 之后使能 CANN 环境，构建 GDN 自定义算子运行包与 `torch_custom/fla_npu` wheel；`--soc` 与 NPU 类型存在固定映射 (`910b→ascend910b`、`a3→ascend910_93`、`950→ascend950`)，可通过 `--fla-npu-soc` 覆盖。

---

## 【关键机制与数据】

- **镜像版本语义化绑定机制（原文）**：版本号 `26.1.0` 不仅作为镜像 tag 字段，同时也是 MindSpeed-LLM 在 gitcode 仓库的 Git 分支名（"MindSpeed LLM version label, also serves as Git branch name"）；同理 `MindSpeed → 26.1.0_core_r0.12.1`、`Megatron-LM → core_v0.12.1` 等亦同时作为分支名。
- **本地构建与发布 tag 差异（原文）**："The latest tags in the image registry are multi-architecture images combining `x86_64` and `aarch64`, so they do not include an `-x86_64` or `-aarch64` architecture suffix. When the image is built locally from the Dockerfile, the build script still generates a tag with the host architecture suffix by default." —— 即发布态为多架构合并 tag，本地构建态默认带宿主机架构后缀。
- **基础镜像自动拉取机制（原文）**：当 `--base-image` 指定但本地不存在时自动拉取；chip 字段与 CANN 镜像名必须小写（`910b`、`a3`、`950`）；当省略 `-t, --npu-type` 时，脚本从 base image tag 自动识别上述三种 NPU 类型。
- **FLA NPU 算子维护机制（原文）**："The FLA NPU operator list is maintained in the `FLA_NPU_OPS` array in `docker/image_build.sh`. Add new operator names to that array, and the script will convert it to the comma-separated value required by `build.sh --ops`." —— 算子列表由脚本中的数组变量集中维护。
- **性能/数据指标**：原文未提供任何训练吞吐、显存占用、MFU/加速比等性能数据。

---

## 【表格解读】

### 表 1 · Quick Reference（镜像元信息）

> 原文表格逐字还原：

| Item | Description |
| ------ | ------ |
| **Image Name** | mindspeed-llm |
| **Maintainer** | MindSpeed LLM Team |
| **Source Repository** | [https://gitcode.com/Ascend/MindSpeed-LLM](https://gitcode.com/Ascend/MindSpeed-LLM) |
| **Dockerfile Path** | `docker/Dockerfile` |
| **License** | Apache-2.0 |
| **Where to get help** | [Issue Feedback](https://gitcode.com/Ascend/MindSpeed-LLM/issues) |

**逐行解读**：

- **Image Name / mindspeed-llm**：Docker 仓库内统一的镜像名称，所有 tag 都挂在此镜像名下。
- **Maintainer / MindSpeed LLM Team**：维护方即官方团队。
- **Source Repository**：源代码托管在 gitcode 的 `Ascend/MindSpeed-LLM` 仓库（非 GitHub）。
- **Dockerfile Path**：构建入口统一为 `docker/Dockerfile`，意味着所有 tag 共用一份 Dockerfile，靠构建参数差异化。
- **License / Apache-2.0**：项目许可证为 Apache-2.0。
- **Where to get help**：问题反馈入口为该仓库的 Issue 区。

---

### 表 2 · Tag 格式字段说明

> 原文表格逐字还原：

| Field | Example Value | Description |
| ------ | ------ | -------- |
| MindSpeed LLM Version | `26.1.0` | MindSpeed LLM version label, also serves as Git branch name |
| CANN Version | `9.1.0` | CANN base image version |
| TorchNPU Version | `2.7.1.post8` | TorchNPU package version |
| Chip Type | `910b`, `a3`, `950` | NPU chip type (lowercase) |
| OS | `openeuler24.03`, `ubuntu22.04` | Operating system version |
| Python Version | `3.12` | Python runtime version |

**逐行解读**：

- **MindSpeed LLM Version**：版本号字段同时是 Git 分支名，使用时可与代码分支一一对照。
- **CANN Version**：决定 `base image` 的 CANN 版本，是整个 AI 栈的根版本。
- **TorchNPU Version**：对 PyTorch 的 NPU 适配包版本，注入了 `.postN` 后缀（如 `2.7.1.post8`）。
- **Chip Type**：必须小写，三个合法取值为 `910b`、`a3`、`950`，与脚本 `--npu-type` 选项一一对应。
- **OS**：可选 `openeuler24.03` 或 `ubuntu22.04`。
- **Python Version**：当前默认 `3.12`，与 `--python-version` 默认值一致。

---

### 表 3 · Latest Version 26.1.0 镜像清单（6 个多架构 tag）

> 原文表格逐字还原（合并表格，仅列 Tag 与 Dockerfile 链接，Content 列统一相同）：

| Tag | Dockerfile | Content |
| --- | --- | --- |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-910b-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-a3-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-openeuler24.03-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |
| `v26.1.0-cann9.1.0-torch_npu2.7.1.post8-950-ubuntu22.04-py3.12` | [Dockerfile](https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.1.0/docker/Dockerfile) | CANN 9.1.0/PyTorch 2.7.1/Triton-Ascend 3.2.2/MindSpeed 26.1.0_core_r0.12.1/MindSpeed-LLM 26.1.0/Megatron-LM core_v0.12.1/FSDPTurbo main |

**逐行解读**：

- 同一 26.1.0 版本下，**三个 NPU（910b / a3 / 950）** × **两个 OS（openeuler24.03 / ubuntu22.04）** = **6 个发布 tag**，覆盖了所有支持的硬件/操作系统组合。
- 每个 tag 的 Content 列完全相同，说明 26.1.0 发布态通过**共享一份 Dockerfile + 构建参数差异**产出，NPU 差异主要体现在 base image、脚本 `--npu-type` 与 FLA NPU 的 `--soc` 映射。
- Dockerfile 链接全部指向 `26.1.0` 这个 Git 分支/tag，确保 Dockerfile 与对应版本严格绑定；历史 tag 列表需另见 `docker/supported_tags.md`。

---

### 表 4 · 目录结构（伪表格 / 代码块）

> 原文目录树逐字还原：

```text
docker/
├── Dockerfile                 # Universal Dockerfile for multi-NPU
├── image_build.sh             # Image build script
├── configure_yum_repo.sh      # YUM repository configuration script
├── configure_apt_repo.sh      # Apt repository configuration script
├── supported_tags.md          # Published and historical image tags
├── OVERVIEW.md                # English overview document
├── OVERVIEW.zh.md             # Chinese overview document
```

**逐行解读**：

- **Dockerfile**：通用 Dockerfile，对所有 NPU 共用一份，通过 ARG/build-arg 差异化。
- **image_build.sh**：核心构建驱动脚本，提供 14 个可覆盖参数；内含 `FLA_NPU_OPS` 数组。
- **configure_yum_repo.sh / configure_apt_repo.sh**：分别面向 openEuler（yum）与 Ubuntu（apt）两类 OS 的源配置脚本，与 OS 选项耦合。
- **supported_tags.md**：完整发布与历史 tag 清单，补充本 OVERVIEW 未列出的历史版本。
- **OVERVIEW.md / OVERVIEW.zh.md**：英中两版总览，本文档为英文版。

---

### 表 5 · `image_build.sh` 可覆盖参数

> 原文表格逐字还原：

| Parameter                 | Description                                  | Default Value |
|---------------------------|-------------------------------------| ------------ |
| `-t, --npu-type`          | NPU type: `910b`, `a3`, or `950`                | `910b` |
| `-o, --os`                | OS：`openeuler24.03`or`ubuntu22.04` | `openeuler24.03` |
| `--no-cache`              | Build without using Docker build cache                          | None |
| `--mindspeed-llm-branch`  |MindSpeed LLM version tag, also used as Git branch name    | `26.1.0` |
| `--mindspeed-branch`      | MindSpeed version tag, also used as Git branch name        | `26.1.0_core_r0.12.1` |
| `--megatron-branch`       | Megatron-LM version tag, also used as Git branch name      | `core_v0.12.1` |
| `--python-version`        | Python version                           | `3.12` |
| `--torch-version`         | PyTorch version                          | `2.7.1` |
| `--torch-npu-version`     | TorchNPU package version                   | `2.7.1.post8` |
| `--triton-ascend-version` | Triton-Ascend version                        | `3.2.2` |
|  `--fla-npu-branch`       | flash-linear-attention-npu version tag, also used as Git branch name       | `v26.1.0` |
| `--base-image-version`    | Base image CANN version                        | `9.1.0` |
| `--base-image`            | Full base image name, passed as-is to pull the image if not empty           | None |
| `--cleanup-on-fail`       | Clean up dangling images/containers when build fails           | None |

**逐行解读**：

- **NPU/OS 默认 `910b`+`openeuler24.03`**：默认值与最新发布态 tag 严格对齐，意味着"不传任何参数"即复现最新镜像。
- **三个 Git 分支参数**：`--mindspeed-llm-branch`、`--mindspeed-branch`、`--megatron-branch`、`--fla-npu-branch` 共同决定代码层版本，版本号与 Git 分支同构。
- **Python/Torch/TorchNPU/Triton-Ascend**：可独立覆盖，但默认组合已经经过验证；修改其中之一需注意互兼容性。
- **`--base-image-version`**：仅控制 CANN 版本号；若需自定义完整镜像名应使用 `--base-image`。
- **`--base-image`**：传入后**整体按原值使用**，因此要求 tag 必须与官方 CANN 镜像名**逐字符一致**。
- **`--no-cache` / `--cleanup-on-fail`**：流程控制开关，分别用于禁用 Docker 缓存和失败时清理悬挂镜像/容器。

---

### 表 6 · FLA NPU `--soc` 默认映射

> 原文表格逐字还原：

| NPU type | FLA NPU `--soc` |
| ------ | ------ |
| `910b` | `ascend910b` |
| `a3` | `ascend910_93` |
| `950` | `ascend950` |

**逐行解读**：

- **映射关系**：脚本根据 `-t/--npu-type` 自动推导 `build.sh --soc` 取值，避免用户重复指定。
- **910b → ascend910b**：Ascend 官方对 Atlas A2 (910B) 的 SoC 标识。
- **a3 → ascend910_93**：A3 训练产品对应 `ascend910_93`（注意下划线形式）。
- **950 → ascend950**：对应 Ascend 950 系列 SoC 标识。
- 当自动映射不满足需求时，可通过 `--fla-npu-soc`（脚本参数）手动覆盖。

---

## 【公式解读】

**原文无公式**（文档未涉及任何数学公式或伪代码形式表达式）。

---

## 【关联】

原文未提供任何文末内部链接（用户提供的元数据标注"内部链接: (无)"）。但根据文档自身可识别出以下模块/上下游关系：

- **`docker/Dockerfile`**：所有 tag 共享的唯一构建入口，`image_build.sh` 通过 build-arg 驱动其差异。
- **`docker/image_build.sh`**：构建驱动脚本；内部维护 `FLA_NPU_OPS` 算子数组，调用 FLA NPU 的 `build.sh --ops` 进行算子构建。
- **`docker/configure_yum_repo.sh` / `docker/configure_apt_repo.sh`**：分别与 `-o openeuler24.03` / `-o ubuntu22.04` 配套使用。
- **`docker/supported_tags.md`**：历史 tag 清单文档，与本文档互补，用于查询 26.1.0 之外的历史版本。
- **`docker/OVERVIEW.zh.md`**：中文版总览，与本文档互为镜像。
- **上游软件栈**：CANN → TorchNPU → PyTorch → Triton-Ascend → Megatron-LM → MindSpeed → MindSpeed-LLM → FSDPTurbo，构成镜像内的依赖层次。
- **底层 NPU 硬件**：华为 Atlas 生态下的 `910b`（Atlas A2）、`a3`（Atlas A3）、`950`（Ascend 950 系列）三类芯片。
- **外部仓库 `flash-linear-attention-npu`**：在 Dockerfile 中被克隆，用于编译 GDN 自定义算子与 `torch_custom/fla_npu` wheel。

文档正文在 "### Run a MindSpeed LLM Container" 处被截断（"**Important Note**: Due " 后内容缺失），因此容器运行阶段的具体依赖关系（与训练/推理入口脚本的衔接）原文未涉及。

---

## 【使用方法】

以下命令均来自原文，可在本地直接复用：

### 1. 基础构建（全默认 → 910b + openEuler24.03）

```bash
cd docker
bash image_build.sh
```

### 2. 切换 NPU 与操作系统（→ 950 + Ubuntu22.04）

```bash
bash image_build.sh -t 950 -o ubuntu22.04
```

### 3. 自定义 CANN / PyTorch / TorchNPU 版本

```bash
bash image_build.sh \
  --base-image-version 9.1.0 \
  --torch-version 2.7.1 \
  --torch-npu-version 2.7.1.post8
```

### 4. 切换源代码分支

```bash
bash image_build.sh \
  --mindspeed-llm-branch 26.1.0 \
  --mindspeed-branch 26.1.0_core_r0.12.1 \
  --megatron-branch core_v0.12.1
```

### 5. 自定义输出镜像名

```bash
bash image_build.sh -i myproject/mindspeed-llm:custom
```

### 6. 指定完整 base image 并自动检测 NPU 类型

```bash
cd docker
bash image_build.sh \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.12
```

### 7. 覆盖 FLA NPU `--soc` 映射

```bash
bash image_build.sh --fla-npu-soc ascend910_93
```

### 8. 扩展 FLA NPU 自定义算子

在 `docker/image_build.sh` 中的 `FLA_NPU_OPS` 数组里追加算子名，脚本会自动转换为 `build.sh --ops` 所需的逗号分隔字符串。

### 9. 其它开关

- `--no-cache`：禁用 Docker build cache，强制全量重建。
- `--cleanup-on-fail`：构建失败时清理 dangling 镜像/容器。

### 10. 运行容器

原文 "### Run a MindSpeed LLM Container" 一节在 **"Important Note**: Due" 处截断，**容器运行命令原文未完整给出**，故无法在此处列出对应 `docker run` / 启动脚本内容；该节内容待原文补全后再行引用。
