# FSDPTurbo Runtime Docker Overview

> 仓 `fsdpturbo` · 路径 `ci/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/fsdpturbo/ci/OVERVIEW.md

# FSDPTurbo 运行时 Docker 镜像概览 —— 深度解读

---

## 【定位】

这篇文档解决 **"如何在 NPU (昇腾) 环境下为 FSDPTurbo 准备一个可复用、可热更新源码的运行时容器"** 这一问题,描述了一个以 CANN 为底座、按 NPU/OS/Python 可参数化构建、并通过 `-v` 挂载源码实现"容器内依赖、主机上改码"的 FSDPTurbo 运行时 Docker 镜像 (image name `fsdpturbo-ci`) 的完整使用方法。

---

## 【技术要点】

1. **"依赖 vs 源码"分离架构**: 镜像内只预装 CANN + PyTorch + torch_npu + FSDPTurbo 的 Python 依赖 (transformers、datasets、pyyaml);FSDPTurbo **源码不进镜像**,通过 `docker run -v {path-to-fsdpturbo}:/workspace/FSDPTurbo` 在容器启动时由主机挂载进来,再以 `pip install -e` 可编辑安装,从而避免每次改代码都要重新 build 镜像。
2. **统一的 Dockerfile + 可配置 CANN 底包**: 通过 `docker/build.sh` 的多个参数 (`--npu-type`、`--os`、`--base-image-version`、`--base-image`、`--python-version`、`--torch-version`、`--torch-npu-version`) 在同一份 Dockerfile 内切换不同 NPU (a3 / 910b) 与不同 OS (openeuler24.03 / ubuntu22.04) 的 CANN 底包;`--base-image` 优先级高于 `--base-image-version` 且按原样透传。
3. **NPU 设备直通 (Device Passthrough) 清单**: `docker run` 显式挂载 `/dev/davinci0` … `/dev/davinci7` (8 张计算卡) + `/dev/davinci_manager` + `/dev/devmm_svm` + `/dev/hisi_hdc`,并把主机侧的 Ascend 驱动路径 `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info` 全部 bind 进容器,以保证容器内 NPU 工具链与驱动一致。
4. **面向 NPU/HCCS 的权限/命名空间调优**: 启动时加上 `--pid=host --network host --ipc=host --cgroupns host`、`--security-opt seccomp=unconfined`、`--cap-add=CAP_SYS_RESOURCE|CAP_SYS_ADMIN|CAP_MKNOD|CAP_SYS_PTRACE|CAP_IPC_LOCK`、`--security-opt label=disable`、`--shm-size=32G`、`-e ASCEND_VISIBLE_DEVICES=0-7`,把进程/网络/IPC/cgroup 命名空间与主机打通并放开大量特权能力,这是昇腾集体通信/共享内存/PCIe 操作所必需。
5. **镜像 Tag 命名规范**: 模板为 `{chip_info}-{os}-{python_tag}-{arch}`,例如 `910b-ubuntu22.04-py3.11-x86_64` 与 `a3-openeuler24.03-py3.11-aarch64`,Quick Start 中实际启动用的是 `fsdpturbo-ci:910b-openeuler24.03-py3.11-aarch64`。
6. **缺省环境锁定**: 默认底包为 CANN `9.0.0` + 910b + openEuler `24.03` + Python `3.11`,PyTorch `2.10`、TorchNPU `2.10`;镜像名 `fsdpturbo-ci`、Dockerfile 路径 `docker/Dockerfile`、默认工作目录 `/workspace` (源码挂在其下 `/workspace/FSDPTurbo`)。

---

## 【关键机制与数据】

- **数据/代码流向 (代码 → 镜像 → 容器 → Python 解释器)**:
  - 主机上的 FSDPTurbo 源码目录 → `docker run -v {path-to-fsdpturbo}:/workspace/FSDPTurbo` → 容器内 `/workspace/FSDPTurbo` → `pip install -e /workspace/FSDPTurbo` 注册为 editable site-package → `python -c "import fsdp_turbo"` 验证。
  - 主机 NPU 驱动 (`/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info`) → 同样以 `-v` bind 进容器,保证 `npu-smi` 等工具在容器内能识别物理设备。
  - NPU 计算设备 (`/dev/davinci0` … `/dev/davinci7`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`) 通过 `--device=` 直接透传给容器,`ASCEND_VISIBLE_DEVICES=0-7` 进一步以软件层白名单限制可见卡号。

- **构建参数 ↔ 产物对应关系** (原文: "Build Options" 表): 6 个参数分别决定底包的 NPU 类型、操作系统、CANN 版本/完整镜像名、Python tag、PyTorch 版本、TorchNPU 版本;其中 `--base-image` 与 `--base-image-version` 二选一,前者覆盖后者。

- **版本/路径常量化数据** (原文):
  - 镜像名: `fsdpturbo-ci`
  - 仓库: `https://gitcode.com/Ascend/FSDPTurbo`
  - Dockerfile: `docker/Dockerfile`
  - 默认 base image: `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11`
  - 默认工作目录: `/workspace`
  - 默认 CANN 版本: `9.0.0`
  - 默认 PyTorch / TorchNPU 版本: `2.10` / `2.10`
  - 默认 Python tag: `3.11`
  - 默认 OS: `openeuler24.03`
  - 默认 NPU type: `910b`
  - 容器名: `fsdpturbo-ci`
  - 共享内存: `--shm-size=32G`
  - 可见 NPU: `0-7` (即 8 卡)

- **运行时校验命令** (原文): 容器内 `python -c "import fsdp_turbo; print('FSDPTurbo OK')"`,用于确认 editable install 成功。

- **性能数据**: 原文未涉及。

---

## 【表格解读】

### 表格 1:Quick Reference (镜像基本信息)

| Item | Description |
| ------ | ------ |
| Image Name | `fsdpturbo-ci` |
| Repository | [https://gitcode.com/Ascend/FSDPTurbo](https://gitcode.com/Ascend/FSDPTurbo) |
| Dockerfile Path | `docker/Dockerfile` |
| Default Scenario | FSDPTurbo runtime environment (CANN + PyTorch + torch_npu) |
| Base Image | Configurable CANN image, default `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11` |
| Default Working Directory | `/workspace` |

**逐行解读**:
- **Image Name = `fsdpturbo-ci`**: 该镜像在本地 `docker images` 中的 tag 名前缀;Quick Start 里实际启动的 tag 是 `fsdpturbo-ci:910b-openeuler24.03-py3.11-aarch64`。
- **Repository**: 指向 FSDPTurbo 在 gitcode 上的源码仓,这是 `-v` 挂载的来源地。
- **Dockerfile Path**: `docker/Dockerfile`,与 `bash docker/build.sh` 在同一目录,二者协同完成"一份 Dockerfile + 可配置脚本"的构建模式。
- **Default Scenario**: 表明本镜像定位是"运行时环境",而非含源码的开发镜像 —— 配套 `pip install -e` 才形成完整 FSDPTurbo 可运行环境。
- **Base Image**: 底包选型是**可配置**的,默认值即下文 "Compatibility Notes" 中给出的组合 (CANN `9.0.0` + 910b + openEuler `24.03` + Python `3.11`),来源是华为云 SWR 镜像仓库 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann`。
- **Default Working Directory**: `/workspace`,正是容器内挂载 FSDPTurbo 源码 (`/workspace/FSDPTurbo`) 与用户数据 (`/data`、`/weights`) 的根位置。

### 表格 2:Build Options (构建参数)

| Option | Description | Default |
| ------ | ------ | ------ |
| `-t, --npu-type` | NPU type: `a3` or `910b` | `910b` |
| `-o, --os` | Operating system: `openeuler24.03` or `ubuntu22.04` | `openeuler24.03` |
| `--base-image-version` | CANN base image version | `9.0.0` |
| `--base-image` | Full CANN base image name, higher priority than `--base-image-version`; passed through unchanged | empty |
| `--python-version` | Python tag in the CANN base image | `3.11` |
| `--torch-version` | PyTorch version | `2.10` |
| `--torch-npu-version` | TorchNPU version | `2.10` |

**逐行解读**:
- **`-t, --npu-type` (默认 `910b`)**: 在 a3 与 910b 两种昇腾芯片家族之间二选一,直接影响底包选择与最终 tag 中的 `{chip_info}` 字段。
- **`-o, --os` (默认 `openeuler24.03`)**: 在 openEuler `24.03` 与 Ubuntu `22.04` 之间二选一,影响底包 OS 层与 tag 中 `{os}` 字段。
- **`--base-image-version` (默认 `9.0.0`)**: 仅传 CANN 版本号,实际完整底包名由脚本根据 `--npu-type` / `--os` / `--python-version` 自动拼接为 `…/cann:{ver}-{chip}-{os}-{py_tag}` 形式。
- **`--base-image` (默认 empty)**: 允许用户直接给定一个完整的 CANN 镜像名,优先级高于 `--base-image-version`,并**原样透传** (不做拼接/裁剪),用于自定义/私有镜像源。
- **`--python-version` (默认 `3.11`)**: 仅影响 tag 中 `{python_tag}` 与底包拼接,不直接等同于容器内 Python 解释器的精确次版本号。
- **`--torch-version` (默认 `2.10`)** / **`--torch-npu-version` (默认 `2.10`)**: 控制 FSDPTurbo 在镜像内预装/锁定的 PyTorch 与 torch_npu 版本,二者默认相同,需保持配套兼容。

---

## 【公式解读】

**原文无公式。**

(文档性质为运维/使用说明,未出现任何数学公式、性能公式或伪代码表达式;tag 模板 `{chip_info}-{os}-{python_tag}-{arch}` 与容器启动命令行是字符串模板/CLI 参数,不属于数学公式,故此节留空。)

---

## 【关联】

文末未给出内部链接,以下关系来自文中显式提及的对象 (原文):

- **与 FSDPTurbo 源码仓的关系**: 文档把 FSDPTurbo 仓库 `https://gitcode.com/Ascend/FSDPTurbo` 视为外部数据源,通过 `-v` 把主机路径 `{path-to-fsdpturbo}` 映射为容器内 `/workspace/FSDPTurbo`,再以 `pip install -e /workspace/FSDPTurbo` 形成 editable 安装 —— 因此本镜像严格依赖源码仓存在,但与具体源码版本解耦。
- **与昇腾 CANN 软件栈的关系**: 默认底包 `…/cann:9.0.0-…` 表明镜像上层 (PyTorch + torch_npu) 全部基于 CANN 9.0.0;运行时依赖的主机侧 CANN 组件以 `-v` 方式提供 (`/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info`)。
- **与 NPU 驱动/设备层的关系**: 通过 `--device=/dev/davinci0` … `davinci7` + `davinci_manager` + `devmm_svm` + `hisi_hdc` 把昇腾设备节点透传给容器;`ASCEND_VISIBLE_DEVICES=0-7` 在用户态再过滤一次可见卡。
- **与 NPU 集体通信/HCCLS 的关系**: `--pid=host --network host --ipc=host --cgroupns host` 与 `--shm-size=32G` 为跨进程通信 (HCCL/RDMA) 提供共享内存与命名空间前提,`CAP_SYS_PTRACE`/`CAP_IPC_LOCK`/`CAP_SYS_RESOURCE` 等 capability 配合 `seccomp=unconfined` 放宽安全沙箱。
- **与 FSDPTurbo Python 依赖的关系**: 镜像预装 `transformers`、`datasets`、`pyyaml` (原文: "the image pre-installs PyTorch, TorchNPU, and FSDPTurbo's Python dependencies (transformers, datasets, pyyaml)"),这些是 FSDPTurbo 上层训练脚本 (典型 HuggingFace 生态) 的运行时前置。
- **与 LICENSE 的关系**: 镜像本身随附 Apache License 2.0 (与 FSDPTurbo 源码许可一致),并提示底包/系统组件 (Bash 等) 可能另带其他许可,见 [LICENSE](https://gitcode.com/Ascend/FSDPTurbo/blob/master/LICENSE)。
- **与 `docker/build.sh` 的关系**: 文档显式引用 `bash docker/build.sh` 与 `docker/build.sh` 参数为切换 NPU/OS/CANN 版本的唯一入口,是连接本文档与 `ci/Dockerfile`/`docker/build.sh` 的关键桥梁。

---

## 【使用方法】

> 原文未把"启用方式"作为单独小节,但给出了完整可执行命令,以下**逐字保留并标注**。

### 1) 构建镜像 (原文)

```bash
cd docker
bash build.sh
```

可选参数与默认值见上文"Build Options"表格;示例等价命令:`bash build.sh --npu-type 910b --os openeuler24.03 --base-image-version 9.0.0 --python-version 3.11 --torch-version 2.10 --torch-npu-version 2.10` (原文未给出该示例,仅说明可经 `docker/build.sh` 切换)。

### 2) 启动容器 (原文 Quick Start)

把 `{path-to-fsdpturbo}` 换成 FSDPTurbo 源码在主机上的绝对路径,`{path-to-data}` / `{path-to-weights}` 换成真实数据/权重路径;亦可改用 `-v /home/{user}:/home/{user}` 整体挂载 home,使主机与容器路径完全一致。

```bash
docker run -it -d \
  --name fsdpturbo-ci \
  --pid=host \
  --network host \
  --ipc=host \
  --cgroupns host \
  --security-opt seccomp=unconfined \
  --cap-add=CAP_SYS_RESOURCE \
  --cap-add=CAP_SYS_ADMIN \
  --cap-add=CAP_MKNOD \
  --cap-add=CAP_SYS_PTRACE \
  --cap-add=CAP_IPC_LOCK \
  -e ASCEND_VISIBLE_DEVICES=0-7 \
  --device=/dev/davinci0 \
  --device=/dev/davinci1 \
  --device=/dev/davinci2 \
  --device=/dev/davinci3 \
  --device=/dev/davinci4 \
  --device=/dev/davinci5 \
  --device=/dev/davinci6 \
  --device=/dev/davinci7 \
  --device=/dev/davinci_manager \
  --device=/dev/devmm_svm \
  --device=/dev/hisi_hdc \
  --security-opt label=disable \
  --shm-size=32G \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v {path-to-fsdpturbo}:/workspace/FSDPTurbo \
  -v {path-to-data}:/data \
  -v {path-to-weights}:/weights \
  fsdpturbo-ci:910b-openeuler24.03-py3.11-aarch64 \
  /bin/bash
```

### 3) 进入容器并以 editable 模式安装 FSDPTurbo (原文)

```bash
docker exec -it fsdpturbo-ci /bin/bash

# Inside container: install FSDPTurbo in editable mode (code changes take effect immediately)
pip install -e /workspace/FSDPTurbo

# Verify
python -c "import fsdp_turbo; print('FSDPTurbo OK')"
```

### 4) 已生效的镜像预装内容 (原文 "Compatibility Notes")

- 镜像**已预装**: PyTorch、TorchNPU、FSDPTurbo 的 Python 依赖 (`transformers`、`datasets`、`pyyaml`)。
- 镜像**未预装**: FSDPTurbo 源码 —— 必须由主机挂载并 `pip install -e` 引入。
- **可配置项**: CANN 版本 (默认 `9.0.0`)、NPU 型号 (`a3`/`910b`,默认 `910b`)、OS (`openeuler24.03`/`ubuntu22.04`,默认 `openeuler24.03`)、Python tag (默认 `3.11`),通过 `docker/build.sh` 切换。
