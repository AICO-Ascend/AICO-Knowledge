# TorchNPU

> 仓 `pytorch` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docker/OVERVIEW.zh.md

# TorchNPU Docker 镜像 Overview 文档深度解读

## 【定位】

本文档是 TorchNPU 项目中 `docker/OVERVIEW.zh.md` 的中文总览文件，目的是为昇腾 NPU + PyTorch 适配插件（TorchNPU）用户提供 Docker 镜像的**Tag 命名规范、Dockerfile 构建参数表、构建/运行命令样例、支持的硬件清单以及二次开发模板**，让用户能够据此在 AscendHub 渠道自行构建、运行或二次定制 TorchNPU 容器镜像。

---

## 【技术要点】

1. **镜像维护方**：由 Ascend for PyTorch 社区维护，镜像托管在 AscendHub，问题反馈在 gitcode 的 Ascend/pytorch 仓。
2. **Tag 命名规范（原文）**：
   ```
   <TorchNPU版本号>-<CANN版本>-<硬件信息（芯片）>-<操作系统>-<Python版本>
   ```
   - TorchNPU 版本号取值如 `2.12.0 / 2.11.0 / 2.10.0.post4 / 2.9.0.post6 / 2.7.1.post8`
   - CANN 版本统一为 `9.1.0`
   - 芯片型号：`910b / 310p / a3 / 950`
   - 操作系统：`ubuntu22.04 / openeuler24.03`
   - Python：`py3.12`
3. **当前文档覆盖的版本范围**（"Tag(26.1.0)" 段落）：TorchNPU 从 `2.7.1.post8` 到 `2.12.0` 共 5 个 TorchNPU 版本，每个版本都对应 8 个 Tag（4 种芯片 × 2 种 OS），合计 **40 个 Tag**；`26.0.0` 及更早版本的 Tag 见内部链接 `OVERVIEW_26.0.0.zh.md`。
4. **Dockerfile 构建参数表**（共 11 项参数，其中 9 项必填、2 项可选）：包含 `CHIP_ARCH / OS / OS_VERSION / PY_VERSION / CANN_VERSION / ARCH / PY_TAG / TORCH_NPU_RELEASE_VERSION / TORCH_NPU_PATCH_TAG`（必填），以及 `MANYLINUX_VER / PIP_MIRROR_URL`（可选）。
5. **构建命令模式**：通过 `docker build` 加 9 个 `--build-arg` 传参；如需代理，可追加 `HTTP_PROXY / HTTPS_PROXY / NO_PROXY` 三个 build-arg。
6. **运行容器必需挂载的设备与目录**：包括 `/dev/davinci1`（按设备号调整）、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 四个设备，以及 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info` 五个主机路径映射。

---

## 【关键机制与数据】

- **Tag 与 Dockerfile 参数一一对应**：原文表格中每一个 Tag 字段都有对应的 Dockerfile 参数。例如 Tag `2.12.0-cann9.1.0-310p-ubuntu22.04-py3.12` 翻译成 Dockerfile 参数为：`CHIP_ARCH=310p / OS=ubuntu / OS_VERSION=22.04 / PY_VERSION=3.11 / CANN_VERSION=9.1.0 / PY_TAG=cp311 / TORCH_NPU_PATCH_TAG=2.12.0`（原文备注：Tag 中写 `py3.12` 但 PY_VERSION 取 `3.11`，因为该字段描述镜像的 python 版本标识，PY_VERSION 则为构建时的 Python 解释器版本号）。
- **TORCH_NPU_RELEASE_VERSION 的取值规则**（原文）：从 whl 下载 URL `https://gitcode.com/Ascend/pytorch/releases/download/<X>/torch_npu-<Y>-cp310-cp310-manylinux_2_28_aarch64.whl` 中，取 `download/` 与 `/torch_npu-` 之间的部分作为 `TORCH_NPU_RELEASE_VERSION`（示例值 `v26.1.0-pytorch2.12.0`），取 `torch_npu-` 与 `-cp310` 之间的部分作为 `TORCH_NPU_PATCH_TAG`（示例值 `2.12.0`）。
- **可选参数的默认值（原文未直接给出但文档明确"默认清华源"）**：`PIP_MIRROR_URL` 默认 `https://pypi.tuna.tsinghua.edu.cn/simple`；`MANYLINUX_VER` 取自 torch 官方 whl 规范，例值 `manylinux_2_28`。
- **二次开发机制（原文）**：以 `quay.io/ascend/torch-npu:<tag>` 为基础镜像，再叠加用户层（如 `apt install gcc ...`）。
- **性能数据**：原文未涉及性能数据。
- **数据流/工作原理**：原文未描述运行时数据流，仅给出静态的构建/运行流程示意。

---

## 【表格解读】

### 表 1：Tag 字段规范表（原文逐字还原）

| 字段           | 值                            | 说明              |
|--------------|------------------------------|-----------------|
| TorchNPU 版本号 | 2.12.0                       | 详见readme中版本说明部分 |
| CANN版本       | 9.1.0                        | 详见readme中版本说明部分 |
| 硬件信息（芯片）     | 910b / 310p / a3 / 950       | 昇腾芯片型号标识        |
| 操作系统         | ubuntu22.04 / openeuler24.03 | 基础镜像所使用的操作系统发行版 |
| Python 版本    | py3.12                       | 镜像内置 Python 版本  |

**逐行解读**：
- "TorchNPU 版本号" 一行示例值 `2.12.0`，说明这是当前最新 TorchNPU 插件版本号，详尽说明指向 readme；该字段直接对应 Dockerfile 参数 `TORCH_NPU_PATCH_TAG`。
- "CANN 版本" 一行示例值 `9.1.0`，CANN 是昇腾异构计算架构（CANN, Compute Architecture for Neural Networks），对应 Dockerfile 参数 `CANN_VERSION`。
- "硬件信息（芯片）" 一行枚举 `910b / 310p / a3 / 950`，对应 Dockerfile 参数 `CHIP_ARCH`，覆盖训练卡 910B、A3 与推理卡 310P、950 四个系列。
- "操作系统" 一行枚举 `ubuntu22.04 / openeuler24.03`，由 `OS` 与 `OS_VERSION` 组合而成（如 `ubuntu` + `22.04`）。
- "Python 版本" 一行示例值 `py3.12`，是镜像 Tag 中的标识串，与 Dockerfile 内 `PY_VERSION=3.11 / PY_TAG=cp311` 的实际构建时解释器版本并不一一对应——文档约定镜像 Tag 用 3.12 标识，但基础解释器仍为 3.11。

### 表 2：Dockerfile 构建参数表（原文逐字还原）

| 参数                        | 说明                              | 必填 | 参考来源              | 参数取值                                     |
|---------------------------|---------------------------------|----|-------------------|------------------------------------------|
| CHIP_ARCH                 | 昇腾芯片架构标识                        | 是  | CANN 镜像标签规则       | 910b / 310p / a3 / 950                   |
| OS                        | 基础镜像操作系统                        | 是  | CANN 镜像标签规则       | ubuntu / openeuler                       |
| OS_VERSION                | 操作系统版本                          | 是  | CANN 镜像标签规则       | 22.04 / 24.03                            |
| PY_VERSION                | 基础镜像内置 Python 版本                | 是  | CANN 镜像标签规则       | 3.11                                     |
| CANN_VERSION              | 昇腾 CANN 工具包版本                   | 是  | CANN 基础镜像仓库       | 9.1.0                                    |
| ARCH                      | 宿主机硬件架构                         | 是  | 环境硬件              | arm / x86                                |
| PY_TAG                    | Python 包 ABI 标签（cp + 版本号）       | 是  | 与 PY_VERSION 严格匹配 | cp311                                    |
| TORCH_NPU_RELEASE_VERSION | TorchNPU 官方发布 Tag（含 pytorch 版本） | 是  | TorchNPU 仓库发行版    | v26.1.0-pytorch2.12.0                    |
| TORCH_NPU_PATCH_TAG       | TorchNPU 官方发布包名里的版本号            | 是  | TorchNPU 仓库发行版    | 2.12.0                                   |
| MANYLINUX_VER             | PyPI 包兼容系统版本                    | 否  | torch 官方 whl 规范   | manylinux_2_28                           |
| PIP_MIRROR_URL            | pip 安装源地址（默认清华源）                | 否  | PyPI 镜像源          | https://pypi.tuna.tsinghua.edu.cn/simple |

**逐行解读**：
- `CHIP_ARCH` 是构建参数中决定底层芯片支持的关键；其取值必须与 CANN 镜像标签规则匹配，否则基础镜像会缺失对应的驱动/算子库。
- `OS` 与 `OS_VERSION` 需搭配使用，如 `ubuntu` + `22.04`，对应基础镜像发行版。
- `PY_VERSION=3.11` 与 Tag 中展示的 `py3.12` 不一致，文档表内明确构建时使用 3.11，可能与 CANN 镜像仓库所托管的 Python 解释器版本绑定。
- `CANN_VERSION=9.1.0` 是文档范围内所有 Tag 统一使用的版本号。
- `ARCH` 取 `arm / x86`，由宿主机硬件决定；910B、A3、310P 镜像在 ARM64/x86_64 主机上皆可运行。
- `PY_TAG=cp311` 是 `cp` + Python 版本号格式的 ABI 标签，必须与 `PY_VERSION` 严格匹配，否则 pip 装的 wheel 会因 ABI 不匹配而加载失败。
- `TORCH_NPU_RELEASE_VERSION=v26.1.0-pytorch2.12.0`：26.1.0 是 Ascend for PyTorch 主版本号（含 PyTorch 与 TorchNPU 联合打包），2.12.0 是其中 TorchNPU 的小版本号。
- `TORCH_NPU_PATCH_TAG=2.12.0`：仅取 TorchNPU 子版本号，用于定位具体 wheel 文件名。
- `MANYLINUX_VER=manylinux_2_28`：默认不填走 torch 官方规范，决定 wheel 的 glibc 兼容下界。
- `PIP_MIRROR_URL`：默认清华源，方便国内用户加速；如需其他源（如华为云、阿里云）可覆盖。

### 表 3：支持的硬件清单（原文逐字还原）

| 芯片系列    | 产品示例                           | 架构             |
|---------|--------------------------------|----------------|
| 昇腾 910B | Atlas 800T A2、Atlas 900 A2 PoD | ARM64 / x86_64 |
| 昇腾 A3   | Atlas 800T A3                  | ARM64 / x86_64 |
| 昇腾 310P | Atlas 300I Pro、Atlas 300V Pro  | ARM64 / x86_64 |

**逐行解读**：
- "昇腾 910B" 对应训练/推理主力芯片，Atlas 800T A2 与 Atlas 900 A2 PoD 是其服务器/PoD 产品形态；同时支持 ARM64 与 x86_64 主机。
- "昇腾 A3" 是 Atlas 800T A3 一款产品，对应 `a3` 芯片型号 Tag；同样跨 ARM64 与 x86_64。
- "昇腾 310P" 对应边缘/推理产品，Atlas 300I Pro 与 Atlas 300V Pro 是其典型卡型；Tag 中对应 `310p`。
- 文档支持表未单列 `950` 芯片（但在 Tag 与构建参数表中出现），说明该芯片可能为更新或小众型号，未在本硬件清单中给出对应产品示例。

---

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的数学表达式）。

---

## 【关联】

- **./OVERVIEW.md**：本文档的英文版本，提供同样的 Tag、构建参数与命令清单，是中英文双语对照入口（页面顶部 `English | 中文` 跳转）。
- **OVERVIEW_26.0.0.zh.md**：26.0.0 版本及更早的 Tag 信息归档页；当前文档（覆盖 26.1.0 系列 Tag）通过 `[26.0.0 版本相关标签信息](OVERVIEW_26.0.0.zh.md)` 链接将用户引导至此文件，以便查阅历史版本 Tag。
- **下游资源链接**（原文出现）：
  - AscendHub 镜像仓库：用于拉取预构建的 TorchNPU 镜像。
  - TorchNPU 官方文档站：详尽的插件使用文档。
  - 昇腾开发者社区：技术交流与答疑渠道。
  - gitcode Issue 页面：用于问题反馈与 Bug 提交。
  - CANN 基础镜像仓库（quay.io/ascend/cann）：Dockerfile 参数 `CHIP_ARCH / OS / OS_VERSION / PY_VERSION / CANN_VERSION` 的取值来源。
  - TorchNPU 官方 release 页面：`TORCH_NPU_RELEASE_VERSION / TORCH_NPU_PATCH_TAG` 的取值来源。
- **上游链路**：`Dockerfile`（仓库内 `docker/Dockerfile`）是 `docker build` 命令的依赖，所有 `build-arg` 都由该 Dockerfile 消费；二次开发示例中 `quay.io/ascend/torch-npu:<tag>` 是直接来源镜像。
- **License 文件**：与 `LICENSE`（仓内）相对应，约束所分发 TorchNPU 镜像的使用条款。

---

## 【使用方法】

### 一、构建 TorchNPU 镜像（原文命令）

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

**注意（原文）**：构建环境需要代理时，通过 `--build-arg` 追加 `HTTP_PROXY / HTTPS_PROXY / NO_PROXY` 三个变量，例如：
```bash
docker build \
  --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
  --build-arg NO_PROXY=localhost,127.0.0.1 \
  ... \
  -f Dockerfile .
```

### 二、运行 TorchNPU 容器（原文命令）

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

**说明**：4 个 `--device` 是昇腾 NPU 设备的字符设备节点，`5` 个 `-v` 是主机侧驱动/管理工具路径的 bind mount；`/dev/davinci1` 表示使用第 1 号 NPU 设备，多卡场景下需相应调整设备号。

### 三、二次开发（原文 Dockerfile 模板）

```dockerfile
FROM quay.io/ascend/torch-npu:2.12.0-cann9.1.0-910b-ubuntu22.04-py3.12

RUN apt update -y && \
    apt install gcc ...

...
```

### 四、可选配置项（原文有则写）
- `MANYLINUX_VER`：默认依 torch 官方 whl 规范（如 `manylinux_2_28`），决定安装的 torch wheel 兼容性。
- `PIP_MIRROR_URL`：默认 `https://pypi.tuna.tsinghua.edu.cn/simple`（清华源），可按需替换为其他 PyPI 镜像源。
- `ARCH`：依宿主机硬件选 `arm` 或 `x86`。

### 五、原文未涉及的内容
- 容器启动后如何在 Python 中 `import torch_npu`、如何切换后端 device 名称、具体算子/模型运行示例：原文未涉及。
- 镜像大小、镜像层数、安装路径等元信息：原文未涉及。
- 镜像安全扫描、签名验证流程：原文未涉及。
- 多卡分布式训练启动命令（如 `torchrun` / `deepspeed`）：原文未涉及。
