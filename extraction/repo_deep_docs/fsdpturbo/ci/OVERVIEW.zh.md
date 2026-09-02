# FSDPTurbo Runtime Docker 镜像概述

> 仓 `fsdpturbo` · 路径 `ci/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/fsdpturbo/ci/OVERVIEW.zh.md

# FSDPTurbo Runtime Docker 镜像概述 — 深度解读

## 【定位】

本篇文档解决"如何为 FSDPTurbo（提供 NPU 亲和的 FSDP 增强特性的代码仓）提供一个可复用、可配置、便于宿主机—容器协同开发的运行时 Docker 镜像"问题，描述的是位于 `docker/Dockerfile` 的 CI/运行镜像 `fsdpturbo-ci` 的设计、构建参数、启动方式与挂载工作流。

---

## 【技术要点】

- **镜像定位为运行时环境镜像**：原文明确"FSDPTurbo 源代码本身不在镜像中，而是通过 `-v` 挂载宿主机目录的方式引入"，从而实现"宿主机开发 → 容器内运行调试 → 无需每次改代码都重新构建镜像"。
- **默认基础镜像固定**：默认 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11`（即 CANN 9.0.0 / 910b / openEuler 24.03 / Python 3.11）。
- **Tag 模板规范**：推荐模板 `{芯片信息}-{操作系统}-{Python标签}-{架构类型}`，例：`910b-ubuntu22.04-py3.11-x86_64` 与 `a3-openeuler24.03-py3.11-aarch64`。
- **构建参数共 6 项**：`-t/--npu-type`（a3/910b，默认 `910b`）、`-o/--os`（openeuler24.03/ubuntu22.04，默认 `openeuler24.03`）、`--base-image-version`（默认 `9.0.0`）、`--base-image`（优先级高于 `--base-image-version`，原样传入，默认空）、`--python-version`（默认 `3.11`）、`--torch-version`（默认 `2.10`）、`--torch-npu-version`（默认 `2.10`）。
- **容器启动需透传 NPU 设备与驱动目录**：固定 8 张昇腾计算卡 `--device=/dev/davinci0` ~ `--device=/dev/davinci7`，外加 `--device=/dev/davinci_manager`、`--device=/dev/devmm_svm`、`--device=/dev/hisi_hdc`；并以 `-v` 挂载 `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info`。
- **共享内存与权限配置**：`--shm-size=32G`、`--ipc=host`、`--pid=host`、`--network host`、`--cgroupns host`、`--security-opt seccomp=unconfined`、`label=disable`，并显式 `--cap-add` 添加 `CAP_SYS_RESOURCE / CAP_SYS_ADMIN / CAP_MKNOD / CAP_SYS_PTRACE / CAP_IPC_LOCK`；`ASCEND_VISIBLE_DEVICES=0-7`。

---

## 【关键机制与数据】

- **工作原理（挂载式开发闭环）**（原文: "本镜像是一个**运行时环境镜像**，只提供 CANN、PyTorch、torch_npu 和 FSDPTurbo 的 Python 依赖。FSDPTurbo 源代码本身不在镜像中，而是通过 `-v` 挂载宿主机目录的方式引入"）——容器内 `/workspace/FSDPTurbo` 即宿主机源码路径，进入容器后执行 `pip install -e /workspace/FSDPTurbo` 完成 editable 模式安装，从而"改代码无需重装/重构建"。
- **默认版本组合**（原文: "默认基础镜像使用 CANN 9.0.0、910b、openEuler 24.03、Python 3.11"）——即构建参数 6 项默认值的合集。
- **设备/驱动可见性映射**（原文: `docker run` 命令片段）——`ASCEND_VISIBLE_DEVICES=0-7` 与 8 张 davinci 设备一一对应；`davinci_manager / devmm_svm / hisi_hdc` 为昇腾运行时所需的设备节点；4 个 `-v` 挂载分别承载驱动、DCMI、npu-smi 与安装信息文件。
- **预装依赖清单**（原文: "镜像预装 PyTorch、TorchNPU 以及 FSDPTurbo 的 Python 依赖（transformers、datasets、pyyaml）"）。
- **可选简化挂载**（原文: "也可以直接挂载整个用户目录 `-v /home/{user}:/home/{user}`，使容器内外路径完全一致"）。
- **镜像 Tag 与芯片/OS/Python/架构的强耦合**（原文 Tag 模板与示例）——决定了同一份 Dockerfile 可交叉产出 x86_64 与 aarch64、Ubuntu 与 openEuler 的不同镜像。

> 注：原文未给出任何性能数据（如吞吐、时延、显存占用等），亦未提供 FSDP 训练指标。

---

## 【表格解读】

### 表格 1：快速参考（原文逐字还原）

| 项目 | 说明 |
| ------ | ------ |
| 镜像名称 | `fsdpturbo-ci` |
| 源码仓库 | [https://gitcode.com/Ascend/FSDPTurbo](https://gitcode.com/Ascend/FSDPTurbo) |
| Dockerfile 路径 | `docker/Dockerfile` |
| 默认场景 | FSDPTurbo 运行时环境（CANN + PyTorch + torch_npu） |
| 基础镜像 | 可配置 CANN 镜像，默认 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.0-910b-openeuler24.03-py3.11` |
| 默认工作目录 | `/workspace` |

**逐行解读**：
- *镜像名称 `fsdpturbo-ci`*：与 `docker run` 命令末尾的镜像 tag 前缀一致，是该 CI/运行镜像的统一标识。
- *源码仓库*：指向 FSDPTurbo 主仓，配套 `LICENSE` 等文件均位于此仓库下。
- *Dockerfile 路径 `docker/Dockerfile`*：表明构建入口位于仓库 `docker/` 子目录，`build.sh` 也在该目录下（见"构建镜像"小节）。
- *默认场景：CANN + PyTorch + torch_npu*：明确镜像内三层软件栈，源码不在其中。
- *基础镜像*：默认走华为云 SWR 上的官方 CANN 9.0.0/910b/openEuler 24.03/Python 3.11 镜像；并标注"可配置"，对应下文构建参数。
- *默认工作目录 `/workspace`*：与容器启动时 `-v {path-to-fsdpturbo}:/workspace/FSDPTurbo` 的挂载点呼应。

### 表格 2：构建参数（原文逐字还原）

| 参数 | 说明 | 默认值 |
| ------ | ------ | ------ |
| `-t, --npu-type` | NPU 类型：`a3` 或 `910b` | `910b` |
| `-o, --os` | 操作系统：`openeuler24.03` 或 `ubuntu22.04` | `openeuler24.03` |
| `--base-image-version` | CANN 基础镜像版本 | `9.0.0` |
| `--base-image` | 完整 CANN 基础镜像名，优先级高于 `--base-image-version`；会原样传入 | 空 |
| `--python-version` | CANN 基础镜像中的 Python 标签 | `3.11` |
| `--torch-version` | PyTorch 版本 | `2.10` |
| `--torch-npu-version` | TorchNPU 版本 | `2.10` |

**逐行解读**：
- *`-t/--npu-type`*：取值 `a3` 或 `910b`，覆盖昇腾不同代次芯片；与 Tag 中的"芯片信息"段对应。
- *`-o/--os`*：在 `openeuler24.03` 与 `ubuntu22.04` 之间切换，决定基础镜像发行版。
- *`--base-image-version`*：在默认情况下控制 CANN 版本号 `9.0.0`，会拼入默认基础镜像 tag。
- *`--base-image`*：提供"完整基础镜像名"作为高级覆盖项，优先级高于 `--base-image-version`，原样透传——便于使用内部/自建 CANN 镜像。
- *`--python-version`*：仅作为 Python 标签段（`py3.11`）参与 tag 拼接；与基础镜像内 Python 解耦控制。
- *`--torch-version` 与 `--torch-npu-version`*：默认均为 `2.10`，是 torch 与 torch_npu 的版本绑定点；调整时应同步。

---

## 【公式解读】

原文无公式。文档中仅出现 Tag 模板的字符串拼接说明：

`{芯片信息}-{操作系统}-{Python标签}-{架构类型}`

该模板属于命名约定而非数学/算法公式，故归入技术要点与表格解读部分呈现。

---

## 【关联】

- **与源码仓库的关系**（原文: 快速参考中"源码仓库 https://gitcode.com/Ascend/FSDPTurbo"）——文档本身位于仓库 `ci/OVERVIEW.zh.md`，与主仓共享同一许可证（Apache License 2.0）。
- **与 `docker/Dockerfile` 及 `docker/build.sh` 的关系**（原文: "Dockerfile 路径 `docker/Dockerfile`"；"构建镜像 `cd docker && bash build.sh`"）——文档是该 Dockerfile 与构建脚本的使用说明，所有构建参数对应 `build.sh` 入参。
- **与 FSDPTurbo 源码包的关系**（原文: "FSDPTurbo 源码需从宿主机挂载，容器内 `pip install -e` 安装后可随时修改代码"）——挂载点 `/workspace/FSDPTurbo` 与 editable 安装构成"宿主机改、容器跑"链路。
- **与昇腾驱动/固件的依赖**（原文: `docker run` 中挂载 `/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info`）——镜像不自带驱动，依赖宿主机已有的昇腾 runtime。
- **与 Apache 2.0 许可证**（原文: "FSDPTurbo 基于 Apache License 2.0 许可证发布。详见 LICENSE 文件"）——镜像内可能包含 Bash 等其他许可证组件。
- **与同仓其他文档的关系**：文末内部链接字段标注 "(无)"，因此本 overview 在文内未显式互链其他特性/模块。

---

## 【使用方法】

### 1. 构建镜像（原文有）

```bash
cd docker
bash build.sh
```

可通过 `build.sh` 的入参切换 NPU 类型、操作系统、CANN 版本、Python 版本、PyTorch 与 TorchNPU 版本（参数清单见"构建参数"表格）。

### 2. 启动容器（原文有）

```bash
docker run -it -d \
  --name fsdpturbo-ci \
  --pid=host --network host --ipc=host --cgroupns host \
  --security-opt seccomp=unconfined --security-opt label=disable \
  --cap-add=CAP_SYS_RESOURCE --cap-add=CAP_SYS_ADMIN \
  --cap-add=CAP_MKNOD --cap-add=CAP_SYS_PTRACE --cap-add=CAP_IPC_LOCK \
  -e ASCEND_VISIBLE_DEVICES=0-7 \
  --device=/dev/davinci0 ... --device=/dev/davinci7 \
  --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc \
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

> `{path-to-fsdpturbo}` / `{path-to-data}` / `{path-to-weights}` 需替换为宿主机真实路径；也可直接 `-v /home/{user}:/home/{user}` 简化。

### 3. 容器内安装 FSDPTurbo 并验证（原文有）

```bash
docker exec -it fsdpturbo-ci /bin/bash

pip install -e /workspace/FSDPTurbo
python -c "import fsdp_turbo; print('FSDPTurbo OK')"
```

### 4. 切换基础镜像（原文有）

可通过 `docker/build.sh` 切换至 Ubuntu 22.04、a3 或其他 CANN 基础镜像版本；若需使用自建基础镜像，通过 `--base-image` 原样传入完整镜像名（优先级高于 `--base-image-version`）。
