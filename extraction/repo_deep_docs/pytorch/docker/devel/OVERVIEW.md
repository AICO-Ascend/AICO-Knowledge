# TorchNPU devel

> 仓 `pytorch` · 路径 `docker/devel/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docker/devel/OVERVIEW.md

# TorchNPU devel 文档一体化深度解读

## 【定位】

本篇文档是 `torch-npu-devel` 镜像的官方 OVERVIEW,描述一个**面向 TorchNPU 源码编译的开发镜像**——它在 builder 基础镜像之上集成 CANN 工具链,使用户能在容器内直接编译 TorchNPU wheel 并运行在 NPU 上,同时明确了镜像的标签规范、构建参数、产品映射与多架构构建流程。

---

## 【技术要点】

1. **镜像分层定位**: `torch-npu-devel` 是构建在 `builder` 镜像( manylinux + Python + gcc-toolset + cmake + PyTorch CPU 依赖 )之上的**开发镜像**,集成 CANN toolkit( Toolkit + Ops,NNAL 为可选 );用户可在容器内**编译出 TorchNPU wheel 并直接运行在 NPU 上**。
2. **驱动与镜像解耦**: **Driver 不包含在镜像中**,必须**提前在宿主机安装**;这是容器化交付昇腾生态的标准边界。
4. **标签格式与版本固定**: Tag 格式为 `<PyTorch_version>-<CANN_version>-<chip>-<os>`;预装 PyTorch `2.13.0`、CANN `9.1.0`、OS 为 `manylinux_2_28`,支持的芯片枚举为 `310p / 910 / 910b / a3 / 950`。
5. **Python 通过 build arg 而非 tag 控制**: 默认 `3.10`,由 `PY_VERSION` 指定;Python 版本**不进入 tag 命名**。
6. **CANN release train 必须显式声明**: 由于 OBS 目录名( 如 `CANN%209.1.T1`、`CANN%209.1.0` )**无法从版本号推导**,当 `CANN_VERSION` 偏离默认 `9.1.0` 时必须**同时**指定 `CANN_RELEASE_TRAIN`,否则构建失败。
7. **多架构构建模式**: x86 与 ARM 需**分别构建再合并**( `--push` )到同一镜像仓库。

---

## 【关键机制与数据】

- **工作原理(原文)**: "It is built on top of the `builder` image (manylinux + Python + gcc-toolset + cmake + PyTorch CPU dependencies) and integrates the CANN toolkit (Toolkit + Ops, NNAL optional). Users can compile the TorchNPU wheel inside the container and run it directly on NPU."
- **驱动隔离(原文)**: "Driver is not included in the image and must be installed on the host in advance."
- **CANN 目录命名非派生(原文)**: "The directory name cannot be derived from the version number, so when `CANN_VERSION` differs from the default `9.1.0`, you must specify `CANN_RELEASE_TRAIN` at the same time, otherwise the build will fail."
- **代理传递(原文)**: 镜像构建若需代理,通过 `--build-arg HTTP_PROXY=...` / `HTTPS_PROXY=...` / `NO_PROXY=...` 三个变量注入( `localhost,127.0.0.1` 需放行 )。
- **运行时挂载(原文)**: dev 镜像启动需**透传 NPU 驱动、设备节点与 npu-smi 工具**(对应 `-v /dev:/dev` 、 `-v /usr/local/Ascend/driver:/usr/local/Ascend/driver` 等挂载项;原文末段被截断)。
- 性能数据:**原文未涉及**。

---

## 【表格解读】

### 表 1 — Tag Specification(标签规范)

| Field            | value                              | Description                                       |
|------------------|------------------------------------|---------------------------------------------------|
| PyTorch Version | 2.13.0                             | Pre-installed PyTorch version |
| CANN_version     | 9.1.0                              | Pre-installed CANN version |
| Chip             | 310p / 910 / 910b / a3 / 950       | The Ascend chip models supported by the image     |
| OS               | manylinux_2_28                     | Base image OS distribution used                   |

> The Python version (default `3.10`) is specified via the `PY_VERSION` build arg and is not part of the tag.

**逐行解读**:
- **PyTorch Version = 2.13.0**: 镜像预装的 PyTorch 主版本号,直接固化到 tag 中。
- **CANN_version = 9.1.0**: 镜像预装的 CANN 工具链版本,固化到 tag 中。
- **Chip = 310p/910/910b/a3/950**: 列出 5 个支持的昇腾芯片型号枚举值,与 CANN_PRODUCT 形成映射。
- **OS = manylinux_2_28**: 基础操作系统发行版(manylinux 标准的 glibc 2.28 基线,如 AlmaLinux 8 / RHEL 8 / Rocky 8 等)。
- **脚注**: 解释 Python 不在 tag 中,通过 `PY_VERSION` 构建参数控制(默认 3.10)。

### 表 2 — Tag(Pre-installed PyTorch 2.13.0)

| Tag                                                    |
|--------------------------------------------------------|
| `2.13.0-cann9.1.0-310p-manylinux_2_28`                 |
| `2.13.0-cann9.1.0-910-manylinux_2_28`                  |
| `2.13.0-cann9.1.0-910b-manylinux_2_28`                 |
| `2.13.0-cann9.1.0-a3-manylinux_2_28`                   |
| `2.13.0-cann9.1.0-950-manylinux_2_28`                  |

**逐行解读**: 按 Tag 规范格式枚举出 5 种芯片各自的完整镜像标签,用于直接拉取或复现构建。

### 表 3 — Dockerfile build parameters

| parameters         | Description                                                                                   | Required | Reference Source        | Value                       |
|--------------------|--------------------------------------------------------------------------------------------|----------|-------------------------|-----------------------------|
| PY_VERSION         | Python version, only dependencies for the corresponding version are installed                | Yes      | manylinux image         | 3.10                        |
| TORCH_VERSION      | PyTorch version, format `x.x.x` (e.g. `2.13.0`) or dev version (e.g. `2.13.0.dev20260610`)   | Yes      | TorchNPU repo releases  | 2.13.0                      |
| DEVTOOLSET_VERSION | GCC toolset version                                                                          | No       | Dockerfile default      | 13                          |
| CANN_VERSION       | CANN toolkit version                                                                        | Yes      | CANN base image repo    | 9.1.0                       |
| CANN_PRODUCT       | CANN ops package product type                                                                | Yes      | CANN product mapping     | 910b                        |
| INSTALL_NNAL       | Whether to install NNAL neural network acceleration library                                  | No       | Dockerfile default      | 0                           |
| CANN_RELEASE_TRAIN | CANN release train; must be specified manually when `CANN_VERSION` differs from the default   | No       | CANN download directory  | CANN%209.1.0                |

**逐行解读**:
- **PY_VERSION(必选)**: 控制 Python 解释器及对应 pip 依赖;默认 3.10。
- **TORCH_VERSION(必选)**: 控制预装的 PyTorch 版本,支持 `x.x.x` 与 `x.x.x.devYYYYMMDD` 两种格式;示例 `2.13.0` 与 `2.13.0.dev20260610`。
- **DEVTOOLSET_VERSION(可选)**: GCC 工具集主版本号;默认 13(Dockerfile 内置默认值)。
- **CANN_VERSION(必选)**: 拉取的 CANN toolkit 基础镜像版本号;默认 9.1.0。
- **CANN_PRODUCT(必选)**: CANN ops 包产品类型,对应表 4 映射;示例值 910b。
- **INSTALL_NNAL(可选)**: 是否额外安装 NNAL 神经网络加速库;默认 0(不安装)。
- **CANN_RELEASE_TRAIN(可选)**: CANN 在 OBS 上的 release train 目录名;默认 `CANN%209.1.0`;仅在 `CANN_VERSION` 偏离默认时**必须**手动指定,否则构建失败。

### 表 4 — CANN Product Mapping

| Product Code | Corresponding Product     |
|--------------|---------------------------|
| `910b`       | Atlas A2 series           |
| `910`        | Atlas training series     |
| `310p`       | Atlas inference series    |
| `A3`         | Atlas A3 series           |
| `950`        | Atlas 350 accelerator card |

**逐行解读**: 将表 3 中 `CANN_PRODUCT` 的产品代码映射到实际的昇腾产品系列——910b→Atlas A2 系列、910→Atlas 训练系列、310p→Atlas 推理系列、A3→Atlas A3 系列、950→Atlas 350 加速卡。

### 表 5 — 5 种标签对应的构建命令

| Image Tag                                         | Build Command                                                                                                                                                                                                                                                                                                                                                                            |
|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `2.13.0-cann9.1.0-310p-manylinux_2_28`            | `docker build --target dev --build-arg PY_VERSION=3.10 --build-arg TORCH_VERSION=2.13.0 --build-arg CANN_VERSION=9.1.0 --build-arg CANN_PRODUCT=310p --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" -t *your-registry*/torch-npu-devel:2.13.0-cann9.1.0-310p-manylinux_2_28 --push .`                                                                |
| `2.13.0-cann9.1.0-910-manylinux_2_28`             | `docker build --target dev --build-arg PY_VERSION=3.10 --build-arg TORCH_VERSION=2.13.0 --build-arg CANN_VERSION=9.1.0 --build-arg CANN_PRODUCT=910 --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" -t *your-registry*/torch-npu-devel:2.13.0-cann9.1.0-910-manylinux_2_28 --push .`                                                                |
| `2.13.0-cann9.1.0-910b-manylinux_2_28`            | `docker build --target dev --build-arg PY_VERSION=3.10 --build-arg TORCH_VERSION=2.13.0 --build-arg CANN_VERSION=9.1.0 --build-arg CANN_PRODUCT=910b --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" -t *your-registry*/torch-npu-devel:2.13.0-cann9.1.0-910b-manylinux_2_28 --push .`                                                                |
| `2.13.0-cann9.1.0-a3-manylinux_2_28`              | `docker build --target dev --build-arg PY_VERSION=3.10 --build-arg TORCH_VERSION=2.13.0 --build-arg CANN_VERSION=9.1.0 --build-arg CANN_PRODUCT=A3 --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" -t *your-registry*/torch-npu-devel:2.13.0-cann9.1.0-a3-manylinux_2_28 --push .`                                                                  |
| `2.13.0-cann9.1.0-950-manylinux_2_28`             | `docker build --target dev --build-arg PY_VERSION=3.10 --build-arg TORCH_VERSION=2.13.0 --build-arg CANN_VERSION=9.1.0 --build-arg CANN_PRODUCT=950 --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" -t *your-registry*/torch-npu-devel:2.13.0-cann9.1.0-950-manylinux_2_28 --push .`                                                                |

**逐行解读**: 5 条命令模板共享相同结构,仅 `CANN_PRODUCT` 与最终 tag 不同——它们共同执行 ① 指定 build stage `dev`、② 注入 Python/PyTorch/CANN 版本与产品类型、③ 通过 `CANN_RELEASE_TRAIN="CANN%209.1.0"` 锁定 OBS 目录、④ 用 `-t your-registry/torch-npu-devel:<tag>` 打标签、⑤ 用 `--push .` 推送到多架构仓库( x86/ARM 需各跑一次再合并 )。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **横向语言版本**: `./OVERVIEW.zh.md` — 本文档对应的中文翻译版本。
- **构建细节**: `./README.md` — 提供 Dockerfile 与构建脚本的细节说明(本文档仅给出构建参数概览,具体实现细节需跳转)。
- **上游维护方**: Atlas PyTorch 社区( https://www.hiascend.com/developer/software/ai-frameworks/pytorch )— TorchNPU 的维护组织。
- **依赖上游镜像**: `builder` 镜像( manylinux + Python + gcc-toolset + cmake + PyTorch CPU 依赖 )— devel 镜像的构建底座,提供 C++/Python 编译环境。
- **集成上游**: CANN 工具链( Toolkit + Ops,可叠加 NNAL )— 昇腾异构计算架构,提供 NPU 算子与运行时;`CANN_VERSION` 与 `CANN_PRODUCT`/`CANN_RELEASE_TRAIN` 共同决定拉取的 CANN 包内容。
- **外部资源**: Image Repository(AscendHub 镜像仓)、TorchNPU 官方文档、Developer Community 开发者社区、Issue Feedback 反馈入口( gitcode Ascend/pytorch )——分别对应镜像拉取、文档查阅、问题交流、Bug 上报四条支持通道。
- **下游使用**: 编译产物 TorchNPU wheel 在 NPU 上运行,需宿主机的 NPU 驱动、设备节点( `/dev` )与 `npu-smi` 工具支撑。

---

## 【使用方法】

### 启用方式:构建开发镜像(原文完整示例,以 910b 为例)

```bash
docker build \
  --target dev \
  --build-arg PY_VERSION=3.10 \
  --build-arg TORCH_VERSION=2.13.0 \
  --build-arg CANN_VERSION=9.1.0 \
  --build-arg CANN_PRODUCT=910b \
  --build-arg CANN_RELEASE_TRAIN="CANN%209.1.0" \
  -t image_name:tag \
  -f Dockerfile .
```

### 启用方式:启动开发容器(原文,段落尾部被截断)

```bash
docker run -d --rm \
    --name torch-npu-devel \
    --privileged \
    -v /dev:/dev \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/Ascend/a...
```

> 容器启动需 `--privileged` 特权模式,并挂载宿主机的 `/dev`(设备节点)、 `/usr/local/Ascend/driver`(驱动目录)及 `npu-smi` 工具所在路径(原文末段被截断,完整挂载点列表请参考 ./README.md )。

### 配置项

- **Python 版本**: 通过 `--build-arg PY_VERSION=3.10` 控制。
- **PyTorch 版本**: 通过 `--build-arg TORCH_VERSION=2.13.0` 控制,支持 `2.13.0` 与 `2.13.0.dev20260610` 格式。
- **GCC 工具集**: 通过 `--build-arg DEVTOOLSET_VERSION=13` 覆盖默认值 13。
- **CANN 版本**: 通过 `--build-arg CANN_VERSION=9.1.0` 控制。
- **CANN 产品类型**: 通过 `--build-arg CANN_PRODUCT=910b`( 取值 910b / 910 / 310p / A3 / 950 )控制。
- **NNAL 安装开关**: 通过 `--build-arg INSTALL_NNAL=0`( 0 关闭 / 1 开启 )控制。
- **CANN release train**: 通过 `--build-arg CANN_RELEASE_TRAIN="CANN%209.1.0"` 控制;**当 `CANN_VERSION` 偏离默认 9.1.0 时必须显式指定**。
- **代理**: 通过 `--build-arg HTTP_PROXY=...` / `HTTPS_PROXY=...` / `NO_PROXY=localhost,127.0.0.1` 注入代理环境变量。
- **多架构构建**: x86 与 ARM 架构需**分别构建后合并**( 如 manifest 工具合并同一 tag 下不同架构的镜像层 )。
- **构建 stage**: 通过 `--target dev` 指定使用 Dockerfile 中的 `dev` 阶段。
