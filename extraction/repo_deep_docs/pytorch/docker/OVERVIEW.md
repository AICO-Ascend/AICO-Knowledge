# TorchNPU

> 仓 `pytorch` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docker/OVERVIEW.md

# TorchNPU Docker 文档深度解读

## 【定位】
本文档是 TorchNPU 容器化镜像的官方入门手册,系统性描述 TorchNPU 在昇腾 Atlas NPU 上为 PyTorch 提供适配的镜像 Tag 规范、Dockerfile 构建参数来源及取值,以及镜像的构建、运行与二次开发完整流程,旨在为开发者提供「开箱即用」的容器化部署参考。

---

## 【技术要点】

1. **插件定位**:TorchNPU 是基于 Atlas 的深度学习适配框架,使 Atlas NPU 支持 PyTorch 框架,让 PyTorch 用户能够直接调用 Atlas AI 处理器的算力;由 Atlas PyTorch 社区维护。
2. **Tag 命名规范**:严格遵循 `<TorchNPU_version>-<CANN_version>-<chip>-<os>-<python_version>` 五段式结构,例如 `2.12.0-cann9.1.0-a3-ubuntu22.04-py3.12`。
3. **支持的版本矩阵**(26.1.0):TorchNPU 版本覆盖 **2.7.1.post8 / 2.9.0.post6 / 2.10.0.post4 / 2.11.0 / 2.12.0**,CANN 统一为 **9.1.0**,芯片支持 **310p / 910b / a3 / 950**,OS 支持 **ubuntu22.04 / openeuler24.03**,Python 统一 **py3.12**。
4. **Dockerfile 构建参数**:核心 9 个必填参数(`TORCH_VERSION`、`CHIP_ARCH`、`OS`、`OS_VERSION`、`PY_VERSION`、`CANN_VERSION`、`ARCH`、`PY_TAG`、`TORCH_NPU_RELEASE_VERSION/PATCH_TAG`)+ 2 个可选参数(`MANYLINUX_VER`、`PIP_MIRROR_URL`),每个参数都标注了来源(镜像仓、Release 列表、wheel 命名规则等)。
5. **运行容器需挂载的设备/目录**:`/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 四个昇腾设备节点,以及 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info` 五个驱动/管理工具路径。
6. **二次开发模式**:可直接 `FROM quay.io/ascend/torch-npu:2.12.0-cann9.0.0-910b-ubuntu22.04-py3.12` 作为基础镜像,在其上叠加业务软件(示例为 `apt install gcc ...`)。

---

## 【关键机制与数据】

### 工作原理
- **原文**:TorchNPU 是「deep learning adaptation framework based on Atlas, enabling Atlas NPUs to support the PyTorch framework」,本质是 PyTorch 框架与昇腾 Atlas AI 处理器之间的桥接层。
- **原文**:Tag 与 Dockerfile 构建参数存在严格映射关系——Tag 中的每一段都对应 Dockerfile 的一个 `BUILD_ARG`,构建时通过 `--build-arg` 注入。
- **原文**:wheel 包下载 URL(如 `https://gitcode.com/Ascend/pytorch/releases/download/v26.1.0-pytorch2.12.0/torch_npu-2.12.0-cp310-cp310-manylinux_2_28_aarch64.whl`)中,`/download/` 与 `/torch_npu-` 之间的部分即 `TORCH_NPU_RELEASE_VERSION`,`torch_npu-` 与 `-cp310` 之间的部分即 `TORCH_NPU_PATCH_TAG`——这是文档明文给出的字段解析规则。

### 关键数据
- **原文**:TorchNPU 当前最新文档版本为 **2.12.0**,CANN 版本为 **9.1.0**。
- **原文**:Tag(26.1.0)章节共列出 **40 个具体 Tag**(5 个 TorchNPU 版本 × 4 种芯片 × 2 种 OS)。
- **原文**:典型构建示例中 `ARCH=arm` 配合 `PY_TAG=cp311`,与 Tag 中的 `py3.12` 组合形成「基础镜像 py3.12 + 容器内安装 cp311 包」的搭配;Tag 与构建参数在 PY 大版本上存在 `3.12(镜像) vs 3.11(构建参数)` 的不一致,原文以两处并存形式呈现。

### 性能数据
- **原文未涉及**任何性能指标或基准测试数据。

---

## 【表格解读】

### 表 1:Tag Specification(镜像 Tag 字段说明)

| Field            | value                                                   | Description                                       |
|------------------|---------------------------------------------------------|---------------------------------------------------|
| TorchNPU Version | 2.12.0                                                  | For details, see the version notes in the readme. |
| CANN_version     | 9.1.0                                                   | For details, see the version notes in the readme. |
| Chip             | Specific example values can be found in the CANN mirror | chip model identifier                             |
| OS               | ubuntu22.04 / openeuler24.03                            | OS distribution used for the base image           |
| Python Version   | py3.12                                                  | Major Python version pre-installed in the image   |

**逐行解读**:
- **TorchNPU Version = 2.12.0**:表示当前文档锚定的 TorchNPU 主版本号,具体变更需查阅 readme 中的版本说明。
- **CANN_version = 9.1.0**:CANN(昇腾异构计算架构)工具链版本,与 TorchNPU 严格配套,版本细节见 readme。
- **Chip**:芯片型号标识符,具体可选值需要在 CANN 镜像仓的 tag 中查找——文档未直接列出全部值,而是通过 26.1.0 tag 列表给出了具体示例(310p / 910b / a3 / 950)。
- **OS = ubuntu22.04 / openeuler24.03**:基础镜像使用的 OS 发行版,覆盖 Ubuntu 与 openEuler 两大主流分支。
- **Python Version = py3.12**:镜像内预装的 Python 主版本号,与 Dockerfile 中的 `PY_VERSION` 字段相关。

---

### 表 2:Dockerfile build parameters(构建参数说明)

| parameters                | Description                                               | Required | Reference Source          | Value                                                   |
|---------------------------|-----------------------------------------------------------|----------|---------------------------|---------------------------------------------------------|
| TORCH_VERSION             | Full TorchNPU version number                              | Yes      | TorchNPU repo releases    | 2.12.0                                                  |
| CHIP_ARCH                 | chip architecture identifier                              | Yes      | CANN image tag rules      | Specific example values can be found in the CANN mirror |
| OS                        | Base image operating system                               | Yes      | CANN image tag rules      | ubuntu / openeuler                                      |
| OS_VERSION                | Operating system version                                  | Yes      | CANN image tag rules      | 22.04 / 24.03                                           |
| PY_VERSION                | Python version pre-installed in base image                | Yes      | CANN image tag rules      | 3.11                                                    |
| CANN_VERSION              | CANN toolkit version                                      | Yes      | CANN base image repo      | 9.1.0                                                   |
| ARCH                      | Host hardware architecture                                | Yes      | Environment hardware      | arm / x86                                               |
| PY_TAG                    | Python package ABI tag (cp + version number)              | Yes      | Strictly match PY_VERSION | cp311                                                   |
| TORCH_NPU_RELEASE_VERSION | Official TorchNPU release tag (including PyTorch version) | Yes      | TorchNPU repo releases    | v26.1.0-pytorch2.12.0                                   |
| TORCH_NPU_PATCH_TAG       | TorchNPU version number in the release package name       | Yes      | TorchNPU repo releases    | 2.12.0                                                  |
| MANYLINUX_VER             | PyPI package compatible system version                    | No       | torch official wheel spec | manylinux_2_28                                          |
| PIP_MIRROR_URL            | pip installation source URL (Tsinghua mirror by default)  | No       | PyPI mirror sources       | https://pypi.tuna.tsinghua.edu.cn/simple                |

**逐行解读**:
- **TORCH_VERSION = 2.12.0(必填)**:完整 TorchNPU 版本号,来源 TorchNPU 仓库 releases。
- **CHIP_ARCH(必填)**:芯片架构标识符,需从 CANN 镜像 tag 中查询具体取值。
- **OS = ubuntu / openeuler(必填)**:基础镜像操作系统,直接对应 Tag 中的 `ubuntu22.04` 或 `openeuler24.03` 段。
- **OS_VERSION = 22.04 / 24.03(必填)**:具体 OS 版本,与 `OS` 组合确定基础镜像。
- **PY_VERSION = 3.11(必填)**:Dockerfile 实际使用的 Python 版本(注意此处为 3.11,与 Tag 中 `py3.12` 不同,构建流程会用该版本安装 TorchNPU 的 wheel 包)。
- **CANN_VERSION = 9.1.0(必填)**:CANN 工具链版本,需与 base image tag 严格匹配。
- **ARCH = arm / x86(必填)**:宿主机硬件架构,决定拉取 aarch64 还是 x86_64 版本的 wheel。
- **PY_TAG = cp311(必填)**:Python 包 ABI 标签,严格匹配 `PY_VERSION`(3.11 → cp311)。
- **TORCH_NPU_RELEASE_VERSION = v26.1.0-pytorch2.12.0(必填)**:官方 release 完整 tag,包含 PyTorch 版本信息。
- **TORCH_NPU_PATCH_TAG = 2.12.0(必填)**:wheel 包名中的 TorchNPU 版本段,字段解析规则已在文档「Parameter Sources」中明确给出。
- **MANYLINUX_VER = manylinux_2_28(可选)**:PyPI 包兼容的系统版本,默认遵循 torch 官方 wheel 规范。
- **PIP_MIRROR_URL = https://pypi.tuna.tsinghua.edu.cn/simple(可选)**:pip 安装源,默认使用清华镜像。

---

## 【公式解读】

**原文无公式。**

文档中未出现任何数学公式、伪代码或形式化表达式;Tag 命名规则以 `text` 代码块给出,可视为一种结构化字符串模板,但不属于公式范畴。

---

## 【关联】

### 与其他文档/模块的关联
- **OVERVIEW.zh.md**(`./OVERVIEW.zh.md`):本文档的中文翻译版,内容应与英文版完全对应。
- **OVERVIEW_26.0.0.md**(`OVERVIEW_26.0.0.md`):**历史版本镜像 Tag 信息归档**——原文明确写有 `[Tag information for version 26.0.0]` 链接,说明当前文档主版本为 26.1.0,而 26.0.0 的 tag 列表已迁移到独立文件。

### 上下游生态
- **上游**:**PyTorch 框架**(被适配方)——TorchNPU 的存在意义即为 PyTorch 在昇腾 NPU 上运行提供支持。
- **下游/依赖**:
  - **CANN(Compute Architecture for Neural Networks)**:昇腾异构计算架构,版本号直接出现在 Tag 与构建参数中,基础镜像来自 `quay.io/repository/ascend/cann`。
  - **Atlas AI 处理器**:实际执行计算的硬件,Tag 中 `chip` 字段(310p / 910b / a3 / 950)即对应不同型号。
  - **昇腾驱动与工具**:容器运行时挂载的 `/usr/local/dcmi`、`npu-smi`、driver lib64、`version.info`、`ascend_install.info` 等,均为昇腾驱动栈的运行时依赖。
- **外部资源生态**:
  - **Atlas PyTorch 社区**:TorchNPU 的官方维护方,提供 Issue 反馈、镜像仓库、文档站点。
  - **昇腾镜像仓**(`quay.io/ascend/torch-npu`):二次开发示例中作为 `FROM` 基础镜像出现。
  - **GitCode Releases**(`Ascend/pytorch/releases`):wheel 包下载源,提供 `TORCH_NPU_RELEASE_VERSION` 与 `TORCH_NPU_PATCH_TAG` 的真实取值依据。

---

## 【使用方法】

### 构建 TorchNPU 镜像
以构建 `2.12.0-a3-ubuntu22.04-py3.12` 为例,执行以下命令:

```bash
docker build \
  --build-arg CHIP_ARCH=a3 \
  --build-arg OS=ubuntu \
  --build-arg OS_VERSION=22.04 \
  --build-arg PY_VERSION=3.11 \
  --build-arg CANN_VERSION=9.1.0 \
  --build-arg ARCH=arm \
  --build-arg PY_TAG=cp311 \
  --build-arg TORCH_NPU_RELEASE_TAG=v26.1.0-pytorch2.12.0 \
  --build-arg TORCH_NPU_PATCH_TAG=2.12.0 \
  -t image_name:tag \
  -f Dockerfile .
```

**代理环境**:通过额外 `--build-arg` 传入:
```bash
  --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
  --build-arg NO_PROXY=localhost,127.0.0.1
```

### 运行 TorchNPU 容器

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

### 二次开发(以官方镜像为基础)

```dockerfile
FROM quay.io/ascend/torch-npu:2.12.0-cann9.0.0-910b-ubuntu22.04-py3.12 

RUN apt update -y && \
    apt install gcc ...

...
```

### 配置项与参数对照
- 全部可配置项已在「表 2 Dockerfile build parameters」中以「参数名 / 描述 / 是否必填 / 参考来源 / 取值」五列完整给出,构建时按需以 `--build-arg KEY=VALUE` 形式传入。
- 镜像 Tag 的完整可选矩阵见「Tag(26.1.0)」章节(40 个具体 tag),或查阅旧版本归档 `OVERVIEW_26.0.0.md`。
