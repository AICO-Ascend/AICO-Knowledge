# Pre-training distributed environment setup

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_8_ENVIRONMENT_SETUP.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/docs/TUTORIAL_8_ENVIRONMENT_SETUP.md

# 深度解读:Pre-training distributed environment setup

---

## 【定位】

本指南文档完整描述了在多机多卡环境上为 FlagAI/GLM 大模型预训练构建 Docker 化分布式训练环境的全过程——从宿主机层面的 Docker 安装与 NVIDIA 驱动配置,到定制 Dockerfile 中按顺序集成 CUDA/MPI/PyTorch/DeepSpeed 等组件,再到多节点容器互信(SSH)建立与最终的分布式启动测试,目标是产出一个可复现、可横向扩展的多节点预训练运行环境。

---

## 【技术要点】

1. **基础镜像与系统版本**:Dockerfile 基于 `nvidia/cuda:10.2-devel-ubuntu18.04` 构建,维护者署名为 `deepspeed <gqwang@baai.ac.cn>`,使用清华镜像 `mirrors.tuna.tsinghua.edu.cn` 替换 `archive.ubuntu.com` 与 `security.ubuntu.com`,并设置 `DEBIAN_FRONTEND="noninteractive"` 进行无交互式 apt 安装。

2. **核心组件栈按顺序**:文档以 16 个子步骤(a~p)顺序安装——GIT、Mellanox OFED、`nv_peer_mem`、OpenMPI(依赖 libevent)、Python、magma-cuda、若干 Python 包、`mpi4py`(需本地源码安装,避免 pip 版本兼容报错)、PyTorch(需本地安装,网络易中断可重试)、apex、DeepSpeed、NCCL(可选),最后配置 SSH 网络端口与公钥。

3. **NVIDIA 容器运行时接入**:`/etc/docker/daemon.json` 同时包含 `registry-mirrors`(使用方提供的阿里云镜像地址 `https://xxxx.mirror.aliyuncs.com`)与 `runtimes.nvidia`(`path=/usr/bin/nvidia-container-runtime`),使 Docker 守护进程可调用 NVIDIA 容器运行时。

4. **多节点互信机制**:在每个节点容器内生成公钥,将各节点 `id_rsa.pub` 互相写入 `authorized_keys`,实现 SSH 免密登录;`/etc/hosts` 或 hostfile 中需包含节点名(如 `V100-1`)与 IP 的对应关系,所有节点代码与数据路径必须一致(或使用云共享)。

5. **构建镜像两种方式**:Method 1 为直接 `docker pull` 镜像;Method 2 为根据 Dockerfile `docker build` 自定义镜像。Docker 镜像构建完后即可在每台机器上启动容器并执行分布式训练命令。

6. **分布式启动前置**:测试前需配置 `~/SSH/config` 与 hostfile(节点列表),配置 GLM 数据/代码目录(全节点路径一致),然后通过 MPI/DeepSpeed 启动命令发起多机多卡训练。

---

## 【关键机制与数据】

- **镜像构建流水线机制**:整个 Dockerfile 是一个**分层(layer-by-layer)的不可变环境构造流水线**——每一层 `RUN` 指令生成一个镜像层,后置层依赖前置层的文件系统状态。Mellanox OFED、`mpi4py`、PyTorch 等步骤均明确标注"需本地下载后再装",原因是 OFED 驱动包过大、PyTorch git clone 网络易中断、`mpi4py` 通过 pip 直接安装可能与系统 MPI 版本不兼容(原文:`"pip installation may report an error due to version compatibility"`)。  
  原文:`"Install the latest version of GIT (create an image clone installation package)"`——意味着 GIT 安装包通过克隆方式制作,而非直接 apt,以保证拿到最新源码版本。

- **NVIDIA 驱动故障恢复机制**:当 `nvidia-smi` 报 `NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver` 时,需安装 `dkms`(动态内核模块支持),通过 `ls /usr/src | grep nvidia` 查看驱动版本,再用 `dkms install -m nvidia -v [version]` 重新编译注册内核模块,最后**需要重启服务器**(原文:`"Note: you may need to restart the server after the installation is complete"`)。

- **apt 源替换机制(原文步骤 b)**:通过 `sed -i s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g /etc/apt/sources.list` 将 Ubuntu 官方源替换为清华源,提升中国大陆环境下 apt 下载速度与稳定性。

- **数据流路径(原文未给出具体吞吐/带宽数字)**:
  ```
  host_nvidia_driver ──▶ nvidia-container-runtime (daemon.json)
       │
       └─▶ docker container (nvidia/cuda:10.2-devel-ubuntu18.04)
              ├─ OpenMPI + libevent + nv_peer_mem + Mellanox OFED
              ├─ mpi4py ──▶ PyTorch ──▶ apex ──▶ DeepSpeed ──▶ NCCL(opt)
              └─ SSH 互信 ──▶ hostfile/GLM 数据 ──▶ 多机多卡分布式启动
  ```
  原文未提供具体的吞吐量、延迟或训练 step time 等性能数据。

- **GLM 数据/代码一致性要求(原文步骤 b,第四节)**:每个节点需配置相同的代码与数据路径(`"The path is required to be the same"`),也可使用云共享文件系统,避免各节点读取到不同内容导致集合通信错位。

---

## 【表格解读】

**原文无表格。**

文档中出现的结构化内容为两份 JSON 配置文件(`/etc/docker/daemon.json`)与一份 Dockerfile 代码块,均为命令/配置片段而非参数对比表。逐字还原其中最关键的最终 `daemon.json` 配置如下,以便理解其字段含义:

| 字段 | 取值(原文逐字) | 作用解读 |
|---|---|---|
| `registry-mirrors` | `["https://xxxx.mirror.aliyuncs.com"]` | Docker 镜像加速地址,需替换为用户自己的阿里云镜像源,`xxxx` 为占位符 |
| `runtimes.nvidia.path` | `"/usr/bin/nvidia-container-runtime"` | 指定 NVIDIA 容器运行时可执行文件路径,使 Docker 在启动容器时可挂载 GPU |
| `runtimes.nvidia.runtimeArgs` | `[]` | 运行时附加参数,此处留空 |

---

## 【公式解读】

**原文无公式。**

文档为操作型指南,全文不包含任何数学公式、损失函数或训练算法表达式。

---

## 【关联】

文档以"预训练分布式环境搭建"为主题,与以下概念/模块存在隐含的上下游依赖关系(均**在原文标题/步骤中被提及**,但未提供可点击的内部链接):

- **Docker**(第一节)→ 是 NVIDIA 容器运行时、SSH、DeepSpeed 启动的**宿主载体**;Dockerfile 中的每一层都是后续步骤的依赖底座。
- **NVIDIA 驱动 + nvidia-docker2**(第 3、4 节)→ **GPU 透传的前置条件**;没有 nvidia-docker2 则容器内无法识别 GPU。
- **Mellanox OFED + nv_peer_mem + OpenMPI + mpi4py + NCCL**(Dockerfile d、e、f、k、o 步)→ 共同构成**高性能集合通信栈**,是分布式训练节点间梯度同步的底层通路。
- **apex + DeepSpeed + PyTorch**(Dockerfile l、m、n 步)→ 是**训练框架栈**,其中 DeepSpeed 支持 ZeRO 优化,apex 提供混合精度(AMP)支持——这些是 GLM 大模型预训练能否在多卡上跑通的核心依赖。
- **SSH 互信机制(第三节)与 hostfile/GLM 配置(第四节)**→ 是**分布式启动命令**(第四节 c)的运行时前置条件:DeepSpeed/MPI 启动器通过 SSH 远程拉起各节点 worker 进程。

文末给出的"内部链接"提示为"(无)",表明本 Markdown 文档**未内嵌指向其他文档的跳转链接**,所有相关模块都需在同一仓内其他路径(如 PyTorch/built-in/foundation/FlagAI/ 下其他 md 文件)自行查找。

---

## 【使用方法】

**(以下命令均按原文逐字保留)**

**1. 宿主机端 Docker 与 NVIDIA 配置(第一节)**
```shell
apt-get remove docker docker-engine docker-ce docker.io
apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce
```
镜像源替换(将 `https://xxxx.mirror.aliyuncs.com` 替换为自己的镜像):
```shell
mkdir -p /etc/docker
tee /etc/docker/daemon.json <<-'EOF'
{ "registry-mirrors": ["https://xxxx.mirror.aliyuncs.com"] }
EOF
systemctl daemon-reload && systemctl restart docker
```
NVIDIA 驱动安装与 dkms 修复:
```shell
ubuntu-drivers devices
apt-get install nvidia-driver-[recommended version]
nvidia-smi
# 若失败:
apt install dkms
dkms install -m nvidia -v [version]
```
nvidia-docker2 安装与配置 `/etc/docker/daemon.json`(参见上节表格),配置后 `systemctl daemon-reload && systemctl restart docker`。

**2. 构建自定义镜像(第二节第 6 步)**
```shell
# Method 1: docker pull <image>
# Method 2: 在 Dockerfile 所在目录执行
docker build -t <your_image_tag> .
```
> 原文明确 PyTorch、mpi4py、Mellanox OFED 需先下载到本地再在 Dockerfile 中安装,网络中断可重试。

**3. 多节点容器启动(第二节)**
在各机器节点上以相同的镜像、相同的代码/数据挂载路径启动容器。

**4. 容器内互信建立(第三节)**
```shell
# 若容器未生成公钥,执行:
ssh-keygen -t rsa   # 原文标题所述"enter flow on the shell"

# 各节点将自己的 id_rsa.pub 内容追加到所有节点(包括自己)的
# ~/.ssh/authorized_keys 中
# 然后测试:
ssh <other_node>    # 应免密登录
```

**5. 分布式训练启动(第四节)**
- 编辑 `~/SSH/config` 与 hostfile(原文 a),`hostfile` 中需列出 `V100-1` 等节点主机名与 IP 的对应关系;
- 配置 GLM 代码与数据路径(原文 b),**所有节点路径必须一致**或挂载同一云共享;
- 执行原文 c 节的启动命令(原文 c 节标题为 `cmd`,**具体命令在原文中被截断**,本指南未涉及该命令的逐字内容)。

> **提示**:文档在 Dockerfile 步骤 c(`Install the latest version of GIT`)后被截断,因此步骤 d~p 的具体 `RUN` 命令、第二节"Build containers at each machine node"以及第四节 c 节的 `cmd` 启动命令的**完整原文内容均未在本文件中给出**,如需使用,请补全原始文档后查阅。
