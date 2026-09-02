# 多机训练模型搭建环境

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_8_ENVIRONMENT_SETUP.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/doc_zh/TUTORIAL_8_ENVIRONMENT_SETUP.md

# 「多机训练模型搭建环境」文档深度解读

> ⚠️ 原始文档在 OpenMPI wrapper 创建部分被截断（以 `#Create a wrapper for OpenMPI to` 结尾），以下解读仅基于已提供的原文内容。

---

## 【定位】

这篇文档是 **FlagAI（基于 PyTorch + DeepSpeed + GLM 的多机分布式训练）搭建多节点 GPU 集群环境的完整工程手册**，系统性地给出从 Docker 基础环境、GPU 驱动与容器运行时、高速网络栈（Mellanox OFED / nv_peer_mem）、分布式通信库（OpenMPI），到 PyTorch / DeepSpeed / NCCL 安装与节点间 SSH 互信、最终启动分布式训练的全链路步骤。

---

## 【技术要点】

1. **Docker 安装与换源**：通过官方 GPG + apt 仓库安装 `docker-ce`，并在 `/etc/docker/daemon.json` 中配置 `registry-mirrors`（阿里云格式 `https://xxxx.mirror.aliyuncs.com`）实现镜像加速；切换后执行 `systemctl daemon-reload && systemctl restart docker`。
2. **NVIDIA 驱动与 nvidia-docker2 集成**：先查 `dpkg --list | grep nvidia-*` 或 `cat /proc/driver/nvidia/version`；不存在则用 `ubuntu-drivers devices` 查推荐版本后 `apt-get install nvidia-driver-<版本号>`；若驱动加载失败用 `dkms install -m nvidia -v <版本号>` 修复；通过 `nvidia-docker` 源安装 `nvidia-docker2`，将 `nvidia` runtime 写入 `daemon.json`（`path: /usr/bin/nvidia-container-runtime`）使容器内可用 GPU。
3. **基础镜像选择**：Dockerfile `FROM nvidia/cuda:10.2-devel-ubuntu18.04`，设置 `STAGE_DIR=/tmp` 作为临时构建目录，构建完后清理。
4. **Mellanox OFED 用户态安装**（版本 `5.1-2.5.8.0`，URL 明确为 `https://www.mellanox.com/downloads/ofed/MLNX_OFED-5.1-2.5.8.0/MLNX_OFED_LINUX-5.1-2.5.8.0-ubuntu18.04-x86_64.tgz`）：因网络问题建议本地下载后 `COPY` 进镜像；安装命令 `./mlnxofedinstall --user-space-only --without-fw-update --umad-dev-rw --all -q`，明确跳过固件升级。
6. **GPUDirect RDMA 支持（nv_peer_mem）**：克隆 `https://github.com/Mellanox/nv_peer_memory.git` 分支 `1.1-0`（`NV_PEER_MEM_VERSION=1.1`），`./build_module.sh` 后打包成 deb 安装，提供 GPU 与网卡之间的 peer-to-peer 直接内存访问，是多机 GPU 通信的关键。
7. **OpenMPI 4.0.5 + libevent 2.0.22-stable**：先 `./configure --prefix=/usr && make && make install` 安装 libevent，再装 OpenMPI 到 `/usr/local/openmpi-4.0.5`，软链 `/usr/local/mpi`，`-j"$(nproc)"` 并行编译，并通过 `ENV PATH=/usr/local/mpi/bin:${PATH}` 与 `LD_LIBRARY_PATH=/usr/local/lib:/usr/local/mpi/lib:/usr/local/mpi/lib64:${LD_LIBRARY_PATH}` 全局生效。

> 原文后续还规划了 Python 安装、magma-cuda、mpi4py、PyTorch、apex、DeepSpeed、NCCL、SSH 端口/公钥/SSH 配置，但因文档截断，命令细节未给出。

---

## 【关键机制与数据】

| 类别 | 关键参数/命令（原文） | 说明 |
|---|---|---|
| **基础镜像** | `nvidia/cuda:10.2-devel-ubuntu18.04` | CUDA 10.2 + Ubuntu 18.04 |
| **临时目录** | `ENV STAGE_DIR=/tmp` | 容器内一次性构建目录 |
| **APT 镜像** | 清华源 `mirrors.tuna.tsinghua.edu.cn`（archive.ubuntu.com 与 security.ubuntu.com） | 替换 `/etc/apt/sources.list` |
| **基础包** | `build-essential autotools-dev nfs-common pdsh cmake g++ gcc curl wget vim tmux emacs less unzip htop iftop iotop openssh-client openssh-server rsync iputils-ping net-tools sudo llvm-9-dev libsndfile-dev libcupti-dev libjpeg-dev libpng-dev screen jq psmisc dnsutils lsof musl-dev systemd` | 包含 `pdsh`（多机并行 shell）和 `nfs-common`（共享存储） |
| **Git** | `add-apt-repository ppa:git-core/ppa` | 装最新版用于克隆源码 |
| **Mellanox OFED** | `MLNX_OFED_VERSION=5.1-2.5.8.0`，`./mlnxofedinstall --user-space-only --without-fw-update --umad-dev-rw --all -q` | 用户态安装，跳过固件升级 |
| **nv_peer_mem** | `NV_PEER_MEM_VERSION=1.1`，`NV_PEER_MEM_TAG=1.1-0`，仓库 `Mellanox/nv_peer_memory` | GPUDirect RDMA 内核模块 |
| **OpenMPI** | `OPENMPI_VERSION=4.0.5`，`--prefix=/usr/local/openmpi-4.0.5`，软链 `/usr/local/mpi`，`make -j"$(nproc)" install` | 并行编译 |
| **libevent** | `libevent-2.0.22-stable`，`./configure --prefix=/usr` | OpenMPI 依赖 |
| **docker daemon.json** | `registry-mirrors` + `runtimes.nvidia.path=/usr/bin/nvidia-container-runtime` | 镜像加速 + GPU runtime |

> **数据流/性能数据**：原文未给出训练吞吐、节点数、延迟、加速比等性能指标，仅给出环境构建所需的版本号与命令清单。

---

## 【表格解读】

原文无 markdown 表格，但有一段**关键的 JSON 配置块**（daemon.json 最终内容），逐字还原如下：

| 配置字段 | 取值（原文） | 作用解读 |
|---|---|---|
| `registry-mirrors` | `["https://xxxx.mirror.aliyuncs.com"]` | Docker 镜像加速源，`<xxxx>` 需替换为个人阿里云账户子域 |
| `runtimes.nvidia.path` | `"/usr/bin/nvidia-container-runtime"` | 指定 NVIDIA 容器运行时二进制路径，使 `docker run --gpus` 与 `--runtime=nvidia` 可用 |
| `runtimes.nvidia.runtimeArgs` | `[]` | 无额外参数，透传给 nvidia-container-runtime |

**逐行解读**：
- 第一层 `registry-mirrors`：解决 Docker Hub 拉取慢问题，是国内环境刚需。
- 第二层 `runtimes.nvidia`：在 Docker 守护进程级别注册 `nvidia` runtime，是 GPU 容器化的前提；缺此字段时，`docker run --gpus all` 会失败。
- `runtimeArgs: []`：表示不传额外 flag，保持默认行为；如需 `--no-cgroups` 等参数可在此追加。

---

## 【公式解读】

**原文无公式**（无 LaTeX、无数学公式、无伪代码算法块）。仅有的"伪命令式"内容为 shell/Dockerfile 脚本，已在【技术要点】中保留原命令。

---

## 【关联】

本教程在 FlagAI 项目中的位置属于**基础设施层（Infrastructure Layer）**，与其他文档的逻辑关系如下（依据原文目录与截断处的规划推断）：

- **上游/前置**：
  - `PyTorch/built-in/foundation/FlagAI/doc_zh/` 下的**基础环境文档**（本文）→ 是后续所有模型训练、性能调优文档的前置条件。
  - 章节标题中已规划 `pip` 包、PyTorch、apex、DeepSpeed、NCCL 安装步骤，指向仓库内其他 tutorial（具体链接因文档截断未给出）。

- **下游/后续**：
  - **第三章「互信机制设置」**：依赖 Dockerfile 中 `openssh-client openssh-server` 与"配置网络端口、公钥和 ssh"步骤（原文截断但已列在目录）。
  - **第四章「分布式训练测试」**：依赖 hostfile（与 `~/.ssh/config` 中主机别名 `V100-1` 对应）、各节点 GLM 代码与数据路径一致、`cmd` 启动命令（原文截断但已列在目录）。
  - **GLM 分布式训练**：`b. 配置 glm 文件` 表明本教程最终服务于 FlagAI 中 GLM 大模型的分布式启动。

- **技术组件之间的依赖链**：
  ```
  nvidia-docker2  →  GPU 容器化
       ↓
  Mellanox OFED + nv_peer_mem  →  RDMA / GPUDirect（网络层加速）
       ↓
  OpenMPI 4.0.5  →  多节点集合通信
       ↓
  PyTorch + DeepSpeed + NCCL  →  分布式训练框架
       ↓
  SSH 互信 + hostfile  →  跨节点编排
  ```

---

## 【使用方法】

> 以下命令均**逐字保留原文**，可直接复制使用。

**1. 安装 Docker（原文 1.安装docker）**
```shell
apt-get remove docker docker-engine docker-ce docker.io
apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce
```

**2. Docker 换源（原文 2.Docker 换源，需将 `xxxx` 替换为个人阿里云 ID）**
```shell
mkdir -p /etc/docker
tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://xxxx.mirror.aliyuncs.com"]
}
EOF
systemctl daemon-reload
systemctl restart docker
```

**3. 安装显卡驱动（原文 3.安装显卡驱动）**
```shell
dpkg --list | grep nvidia-*
# 或 cat /proc/driver/nvidia/version
ubuntu-drivers devices
apt-get install nvidia-driver-<版本号>
nvidia-smi
# 若失败：apt install dkms && dkms install -m nvidia -v <版本号>
```

**4. 配置 nvidia-docker（原文 4.配置nvidia-docker源）**
```shell
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update
apt-get install -y nvidia-docker2
```
随后将 `"runtimes": { "nvidia": { "path": "/usr/bin/nvidia-container-runtime", "runtimeArgs": [] } }` 加入 `/etc/docker/daemon.json`，再 `systemctl daemon-reload && systemctl restart docker`。

**5. 构建 Docker 镜像（原文 5.制作dockerfile → 6.构建docker 镜像）**
- **方式一**：直接 `pull` 预制镜像（原文未给出镜像仓库地址，命令被截断）。
- **方式二**：按上文 Dockerfile 逐段拼装（a 拉取 nvidia 基础镜像 → b 配置 apt 清华源并安装基础包 → c 装 git → d 装 Mellanox OFED 5.1-2.5.8.0 → e 装 nv_peer_mem 1.1 → f 装 libevent 2.0.22-stable + OpenMPI 4.0.5 → 后续步骤文档截断）。

**6. 在每个机器节点构建容器（原文 二.）**：原文仅列标题，命令细节未给出（文档截断）。

**7. 互信机制设置（原文 三.）**：
- 默认 docker 镜像创建时已生成公钥，若不存在则在 shell 端执行 `ssh-keygen`（原文未给出完整命令）。
- 将各节点容器生成的公钥文件互相追加到对方 `~/.ssh/authorized_keys`。
- 免密登录：`ssh <节点别名>`（如 `V100-1`）。
- 测试：原文未给出测试命令。

**8. 分布式训练测试（原文 四.）**：
- 配置 hostfile：`V100-1` 等条目需与 `~/.ssh/config` 中的主机别名对应（原文未给出 hostfile 示例内容）。
- 各节点 GLM 代码与数据路径需保持一致，或共同访问云端共享文件。
- 启动命令 `cmd`：原文未给出（文档截断）。

> **整体建议**：本文档属于"操作清单 + 注意事项"风格，命令逐字可用；但**第四章分布式训练启动的关键 cmd 命令与 hostfile 示例因原文截断而缺失**，需结合仓库内其他 tutorial 或 DeepSpeed 官方文档补充。
