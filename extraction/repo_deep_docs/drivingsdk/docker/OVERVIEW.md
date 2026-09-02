# Add required software on top of a DrivingSDK image

> 仓 `drivingsdk` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/drivingsdk/docker/OVERVIEW.md

# 解读: docker/OVERVIEW.md (DrivingSDK Docker 镜像概览)

---

## 【定位】

本文档是 DrivingSDK 仓库的 Docker 镜像总览,用于解决「自动驾驶模型如何在昇腾 NPU 上快速获得开箱即用运行环境」的问题,集中说明支持的架构/操作系统/版本号、镜像 Tag 命名规则、最新 `26.1.0` 版本的可拉取镜像清单,以及如何 `docker run`、`docker buildx build` 和在已有镜像上二次开发。

---

## 【技术要点】

1. **栈定位**: DrivingSDK 提供基于 Ascend CANN + PyTorch + TorchNPU 的「NPU 加速算子 + 自动驾驶模型运行时」(原文:"DrivingSDK provides NPU-accelerated operators and runtime environments for autonomous-driving models based on Ascend CANN, PyTorch, and TorchNPU.")。

2. **平台覆盖**:
   - 架构: `x86_64` (AMD64)、`aarch64` (ARM64)
   - 操作系统: Ubuntu 22.04、openEuler 24.03
   - 昇腾芯片系列: `950`、`a3`、`910b`
   - Python 版本: `py3.8`、`py3.10`
   - 支持的 DrivingSDK 版本: `26.1.0`、`26.0.0`、`7.3.0`

3. **Tag 命名规范**(原文):
   ```
   <drivingsdk-version>-<cann-version>-torch_npu<torchnpu-version>-<chip-series>-<os>-py<python-version>
   ```
   - 例:`26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10`
   - 例外 1:`8.5.1-*` 与 `9.0.0-*` 目录属于「以 CANN 版本开头」的遗留 Tag。
   - 例外 2:`devel` 目录为源码构建的开发镜像(不含版本号字段)。

4. **运行容器必备的设备透传与目录挂载**(原文 `docker run` 命令):
   - 设备:`/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`
   - 目录:`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend`
   - **NPU 驱动由宿主机提供,Dockerfile 不安装**(原文:"The driver is provided by the host and is not installed by these Dockerfiles.")。

5. **构建与二次开发命令**(原文):
   ```bash
   docker buildx build \
       -t drivingsdk:26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10 \
       -f docker/26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10/Dockerfile .
   ```
   二次开发时基于已有镜像 `FROM drivingsdk:...` 再 `RUN apt-get install`;`devel` 镜像从仓库源码构建。

6. **免责声明**: 发布的 Ascend 镜像为社区版,**不用于商业问责**,仅作为生产实践参考(原文:"The released Ascend software images are community versions and are not intended for commercial accountability.")。

---

## 【关键机制与数据】

- **原文: 镜像内容组成**——每张镜像固定打包「PyTorch X.Y.Z + TorchNPU X.Y.Z.postN + DrivingSDK + model environments」四件套。
- **原文: 依赖关系链**——DrivingSDK 镜像内部署的加速算子依赖「CANN(算子编译/运行时) → TorchNPU(Pytorch 设备抽象) → PyTorch(上层框架)」三级栈,因此 Tag 中必须同时锁定 `cann-version` 与 `torchnpu-version`。
- **原文: 与宿主机的接口契约**——容器只挂载 `/dev/davinci*`、`/dev/devmm_svm`、`/dev/hisi_hdc` 设备节点,以及 `/usr/local/{dcmi,Ascend}` 和 `/usr/local/bin/npu-smi`,意味着镜像**假定宿主机已就位 NPU 驱动 + Ascend 工具链 + DCMI**,容器本身只携带 PyTorch 用户态栈。
- **原文: 跨平台适配**——同一组 `drivingsdk-version`/`cann-version`/`torchnpu-version` 组合会同时产出面向 `910b`、`a3`、`950` 三个芯片系列,以及 `ubuntu22.04` / `openeuler24.03` 两个 OS 的变体(原文 26.1.0 表中 10 条 Tag 即为此笛卡尔积的子集)。
- **原文: Python 与 TorchNPU 版本耦合**——`py3.8` 镜像绑定 `torch_npu2.1.0.post17`,`py3.10` 镜像绑定 `torch_npu2.7.1.post6`,二者不交叉(原文中 `26.1.0` 表没有出现 `py3.8 + 2.7.1` 或 `py3.10 + 2.1.0` 的组合)。
- **原文: 历史与最新分支**——`8.5.1-*`、`9.0.0-*` 为遗留 Tag 目录(以 CANN 版本打头),`26.1.0-*` 为当前 LATEST,`devel` 为源码构建分支。
- **原文: 帮助渠道**——DrivingSDK 团队维护,可通过 DrivingSDK 仓库(https://gitcode.com/Ascend/DrivingSDK)及其 Issue Tracker 获取支持。
- 性能数据 / 算子吞吐 / 训练 benchmark 等**原文未涉及**,本文档不包含此类信息。

---

## 【表格解读】

### 表 1: Tag 字段含义(逐字还原)

| Field | Example values | Description |
| --- | --- | --- |
| `drivingsdk-version` | `26.1.0`, `26.0.0`, `7.3.0` | DrivingSDK version number |
| `cann-version` | `9.1.0`, `9.0.0`, `8.5.1` | CANN version number |
| `torchnpu-version` | `2.1.0.post17`, `2.7.1.post6` | TorchNPU version number |
| `chip-series` | `950`, `a3`, `910b` | Target Atlas chip series |
| `os` | `ubuntu22.04`, `openeuler24.03` | Base operating system |
| `python-version` | `py3.8`, `py3.10` | Python version |
| `devel` | `devel` | Special tag representing a development image |

**逐行解读**:
- `drivingsdk-version`:本仓库自动驾驶加速库自身的语义化版本号,目前同时维护 `26.1.0`、`26.0.0`、`7.3.0` 三条线。
- `cann-version`:容器内预装的 CANN(Compute Architecture for Neural Networks)版本,与驱动/芯片兼容性直接相关。
- `torchnpu-version`:TorchNPU 是 PyTorch 对昇腾 NPU 的适配后端,版本号含 `postN` 后缀表示该版本的迭代补丁。
- `chip-series`:目标 Atlas 硬件系列,`910b` 为训练/推理主流卡,`a3` 与 `950` 为新代次芯片。
- `os`:基础 OS,Ubuntu 与 openEuler 双线并行以适配不同客户部署。
- `python-version`:容器内默认 Python 解释器版本,与 TorchNPU/PyTorch 版本强绑定。
- `devel`:特殊值,出现在 Tag 任意位置即表示该镜像是「从仓库源码构建的开发镜像」,跳过版本号字段。

---

### 表 2: LATEST DrivingSDK `26.1.0` 镜像清单(逐字还原)

| Tag | Dockerfile | Image contents |
| --- | --- | --- |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-910b-openeuler24.03-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-910b-openeuler24.03-py3.8/Dockerfile) | PyTorch 2.1.0, TorchNPU 2.1.0.post17, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-910b-ubuntu22.04-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-910b-ubuntu22.04-py3.8/Dockerfile) | PyTorch 2.1.0, TorchNPU 2.1.0.post17, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-a3-openeuler24.03-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-a3-openeuler24.03-py3.8/Dockerfile) | PyTorch 2.1.0, TorchNPU 2.1.0.post17, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-a3-ubuntu22.04-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-a3-ubuntu22.04-py3.8/Dockerfile) | PyTorch 2.1.0, TorchNPU 2.1.0.post17, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-910b-openeuler24.03-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-910b-openeuler24.03-py3.10/Dockerfile) | PyTorch 2.7.1, TorchNPU 2.7.1.post6, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10/Dockerfile) | PyTorch 2.7.1, TorchNPU 2.7.1.post6, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-950-openeuler24.03-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-950-openeuler24.03-py3.10/Dockerfile) | PyTorch 2.7.1, TorchNPU 2.7.1.post6, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-950-ubuntu22.04-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-950-ubuntu22.04-py3.10/Dockerfile) | PyTorch 2.7.1, TorchNPU 2.7.1.post6, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-a3-openeuler24.03-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-a3-openeuler24.03-py3.10/Dockerfile) | PyTorch 2.7.1, TorchNPU 2.7.1.post6, DrivingSDK, model environments |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-a3-ubuntu22.04-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-a3-ubuntu22.04-py3.10/Dockerfile) | PyTorch 2.7.1, TorchNPU 2.7.1.post6, DrivingSDK, model environments |

**逐行解读**:
- 第 1–4 行(`torch_npu2.1.0.post17` + `py3.8`):覆盖 `910b` × `a3` × `ubuntu22.04` × `openeuler24.03` 四种组合,沿用较老的 PyTorch 2.1.0 栈,**未提供 `950` 系列**——说明该 TorchNPU 版本尚未验证 `950`。
- 第 5–10 行(`torch_npu2.7.1.post6` + `py3.10`):覆盖 `910b`/`a3`/`950` 三种芯片 × 两种 OS 共 6 种组合,是当前**新代次芯片的官方推荐组合**。
- 整体规律:`drivingsdk-version`(26.1.0)与 `cann-version`(9.1.0)在所有镜像中保持一致,变化维度集中在「TorchNPU/PyTorch ↔ 芯片系列 ↔ 操作系统」三轴的笛卡尔积。
- Image contents 列内容全部相同(`PyTorch X.Y.Z, TorchNPU X.Y.Z.postN, DrivingSDK, model environments`),差异仅在具体版本号,说明每个 Tag 的 Dockerfile 仅调整版本字段,不增减软件包。
- 每个 Tag 都对应一个独立 Dockerfile 路径,体现「一 Tag 一 Dockerfile」的可复现构建策略。

---

## 【公式解读】

原文无公式。

---

## 【关联】

> 提示:本文档的内部链接信息标注为「(无)」,因此下面给出的是文档**文本中明确提到的、与其它特性/模块/外部文档的关系**,而非仓内交叉链接。

- **与 CANN 的关系**:DrivingSDK 镜像的内核加速依赖 Ascend CANN(`cann-version` 字段必须出现在 Tag 中),文档明确「需安装与 Dockerfile 中 CANN 版本兼容的 Ascend NPU 驱动」(原文:"Install an Ascend NPU driver compatible with the CANN version used by the selected Dockerfile.")。版本兼容性通过 Tag 锁定。
- **与 PyTorch / TorchNPU 的关系**:镜像打包 PyTorch + TorchNPU,共同提供「上层框架 ↔ NPU 设备」的桥接;镜像是否可用取决于这三者版本矩阵能否相互匹配(详见表 2 中 `py3.8 ↔ 2.1.0.post17`、`py3.10 ↔ 2.7.1.post6` 的绑定关系)。
- **与宿主机驱动的关系**:镜像不自带驱动,**通过 `/dev/davinci*` 等设备节点 + `/usr/local/Ascend` 挂载**与宿主机驱动协同工作,Driver 与 Docker 镜像为「各自独立、运行时拼接」的部署契约。
- **与历史版本的关系**:`8.5.1-*` 与 `9.0.0-*` 目录为遗留 Tag,与当前 `26.1.0-*` Tag 命名规则不同(以 CANN 版本打头),存在两条历史平行分支。
- **与源码开发的关系**:`devel` 目录代表源码构建路径,适合需要修改 DrivingSDK 本体的开发者;普通用户应直接拉取 `26.1.0-*` 镜像。
- **与外部文档的关系**:文档提及了(均为 gitcode 上的同仓库外链,非仓内相对链接):
  - 中文版 OVERVIEW:`docker/OVERVIEW.zh.md`
  - 历史 Tag 列表:`docker/supported_tags.md`
  - DrivingSDK 仓库主页与 Issue Tracker
  - 每个 Tag 对应的独立 Dockerfile 路径

---

## 【使用方法】

### 1. 启动容器(原文给出完整示例)

```bash
docker run \
    --name drivingsdk_container \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend:/usr/local/Ascend \
    -it drivingsdk:26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10 bash
```

关键配置项说明(均为可调项):
- `--device /dev/davinci0`(可扩展到 davinci1/.../davinciN):每张 NPU 卡的字符设备。
- `--device /dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`:昇腾设备管理、共享虚拟内存、HDC 通道,均为容器内算子运行所必需。
- `-v /usr/local/dcmi`、`-v /usr/local/bin/npu-smi`、`-v /usr/local/Ascend`:挂载宿主机的 DCMI(设备管理接口)、`npu-smi` 命令、Ascend 工具链目录。
- 镜像 Tag 必须按命名规范选定,且**宿主机已装好匹配 CANN 版本的 NPU 驱动**(原文明确)。

### 2. 构建镜像(原文给出完整示例)

```bash
docker buildx build \
    -t drivingsdk:26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10 \
    -f docker/26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10/Dockerfile .
```

源码构建版本:

```bash
docker buildx build -t drivingsdk:devel -f docker/devel/Dockerfile .
```

### 3. 在已有镜像上二次开发(原文示例)

```dockerfile
FROM drivingsdk:26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10

RUN apt-get update && apt-get install -y <package>
```

### 4. 选取镜像的决策路径(基于原文)

1. 先确认 DrivingSDK 版本需求(`26.1.0` / `26.0.0` / `7.3.0`)。
2. 确认目标芯片(`910b` / `a3` / `950`)与宿主机 OS(Ubuntu 22.04 / openEuler 24.03)。
3. 按 Python + TorchNPU 版本绑定关系选择 `py3.8 + 2.1.0.post17` 或 `py3.10 + 2.7.1.post6`。
4. 拉取对应 Tag 或自行 `docker buildx build`。
5. 确保宿主机驱动与所选 Tag 中 `cann-version` 兼容后再 `docker run`。

> 注:环境变量、调参开关、性能调优参数等**原文未涉及**,本文档仅作为镜像清单与基础启动指南。
