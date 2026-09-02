# A2 x86

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/getting_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/getting_started/quick_start.md

# xllm 快速开始 深度解读

## 【定位】

本文档是 xllm 高性能 LLM 推理引擎的"快速开始"指南，针对六种异构 AI 加速硬件平台（NPU、NVIDIA GPU、MLU、海光 DCU、沐曦 MACA、摩尔线程 MUSA）分别给出**开发镜像拉取 → 容器启动 → 源码编译 → 启动引擎**的端到端环境准备流程，是用户从零搭建 xllm 开发与运行环境的入口文档。

---

## 【技术要点】

1. **六类硬件平台镜像策略**：NPU 提供三个变体（A2 x86、A2 arm、A3 arm，tag 日期 20260605，CANN 9 版本）；NVIDIA GPU 提供官方 Dockerfile 与预构建 `xllm-dev-cuda-x86` 镜像；MLU 不提供官方镜像，需用户自备；海光 DCU 提供 `xllm-dev-dcu-x86-20260617`；沐曦 MACA 提供 `xllm-maca3.7.1.9:v1`；摩尔线程 MUSA 提供 `xllm:0710`。
2. **设备透传与驱动挂载**：NPU 需挂载 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 及 `/usr/local/Ascend/driver`；DCU 需 `--device=/dev/kfd --device=/dev/dri --device=/dev/mkfd` 并挂载 `/opt/hyhal`；MACA 需 `/dev/mxcd`、`/dev/dri`、`/dev/infiniband` 并挂载 `/opt/maca`；MUSA 需 `/dev/mtgpu0`、`/dev/dri`。
3. **共享内存差异化配置**：`--shm-size` 在不同平台分别为 NVIDIA GPU/MLU 的 `128gb`、海光 DCU 的 `256g`、沐曦 MACA 的 `100gb`、MUSA 的 `128g`，匹配各硬件 IPC 需求。
4. **安全与权限策略**：所有平台均使用 `--privileged`（MACA 为 `--privileged=true`），DCU/MACA 额外使用 `--security-opt seccomp=unconfined`，MACA 还附加 `--security-opt apparmor=unconfined`，DCU/MUSA/MACA 均使用 `--group-add video`，MACA/MUSA 使用 `--ulimit memlock=-1`。
5. **三级编译流程**：`python setup.py build` 仅编译 C++ 二进制；`python setup.py bdist_wheel` 生成 wheel；`python setup.py install` 生成并安装 wheel。原文指出"第一次编译耗时较长，因为需要编译 vcpkg 中的所有依赖，但是后续编译会很快"。
6. **前置依赖初始化**：克隆主仓库后需依次执行 `pip install pre-commit` → `pre-commit install` → `git submodule update --init --recursive`，用于提交规范与子模块同步；带版本号的 release 镜像自带编译产物，可跳过编译直接调用 `xllm`。

---

## 【关键机制与数据】

- **镜像集中托管**：原文（"所有的镜像都存放在[这里](https://quay.io/repository/jd_xllm/xllm-ai?tab=tags)"）说明统一从 quay.io 拉取，DCU 例外使用 `harbor.sourcefind.cn:5443`，MACA 使用 `pub-registry1.metax-tech.com`，MUSA 使用 `registry.mthreads.com`。
- **NPU 容器挂载驱动路径**（原文）：NPU 容器除挂载 `/usr/local/Ascend/driver`、`/usr/local/Ascend/add-ons/`、`/usr/local/sbin/npu-smi` 外，还把宿主机 SLOG 配置目录 `/var/log/npu/conf/slog/slog.conf`、`/var/log/npu/slog/`、`/var/log/npu/profiling/`、`/var/log/npu/dump/` 全部映射进容器，用于日志与 profiling 采集。
- **首次编译性能特征**（原文）："在新镜像中，第一次编译 xllm 耗时较长，因为需要编译 vcpkg 中的所有依赖，但是后续编译会很快。"——首次开销主要来源于 vcpkg 依赖编译，后续增量编译快速。
- **MLU 限制声明**（原文）："我们无法提供 MLU 镜像，如果您已经拥有了相应的开发镜像，那么可以根据下面的命令启动容器"——MLU 是唯一无官方镜像的平台，仅提供容器启动模板。
- **网络与进程命名空间**：NVIDIA GPU 与 MLU 均使用 `--net=host --pid=host`，而 NPU/DCU/MACA/MUSA 仅使用 `--network=host`，不共享 PID 命名空间。

---

## 【表格解读】

**原文无表格**。

（文档以代码块形式列举各平台的 `docker pull` 与 `docker run` 命令，未出现结构化表格。）

---

## 【公式解读】

**原文无公式**。

（文档为操作性指南，不涉及任何数学公式或伪代码推导。）

---

## 【关联】

文档通过文末的内部链接指向两个下游章节，构成"环境准备 → 引擎启动"的串联关系：

| 内部链接 | 关联模块 | 关系说明 |
|---|---|---|
| `/zh/hardware/musa/` | 摩尔线程 MUSA 硬件适配详情 | 本文 MUSA 章节末尾指引用户跳转至该页，获取 MUSA 平台更深入的硬件配置细节（本文仅提供基础容器启动模板） |
| `/zh/getting_started/launch_xllm/` | xllm 启动方式 | 本文"启动 xllm"章节明确指引用户参考该页，了解编译后如何调用 xllm 二进制（本文只到编译结束为止） |

此外，文档通过 `Dockerfile.cuda` 的 GitHub 链接间接关联 `docker/Dockerfile.cuda` 构建脚本，为 NVIDIA GPU 用户提供自定义镜像构建能力。

---

## 【使用方法】

### 一、镜像拉取与容器启动（六平台）

| 平台 | 拉取命令 | 关键启动参数 |
|---|---|---|
| NPU (A2 x86) | `docker pull quay.io/jd_xllm/xllm-ai:xllm-dev-a2-x86-cann9-20260605` | `--device=/dev/davinci0`、`-v /usr/local/Ascend/driver:...` |
| NPU (A2 arm) | `...xllm-dev-a2-arm-cann9-20260605` | 同上 |
| NPU (A3 arm) | `...xllm-dev-a3-arm-cann9-20260605` | 同上 |
| NVIDIA GPU | `docker pull quay.io/jd_xllm/xllm-ai:xllm-dev-cuda-x86` | `--shm-size '128gb' --net=host --pid=host` |
| MLU | （无官方镜像） | `--shm-size '128gb' --net=host --pid=host` |
| 海光 DCU | `docker pull harbor.sourcefind.cn:5443/dcu/admin/base/custom:xllm-dev-dcu-x86-20260617` | `--shm-size 256g`、`--device=/dev/kfd --device=/dev/dri --device=/dev/mkfd`、`-v /opt/hyhal:...` |
| 沐曦 MACA | `docker pull pub-registry1.metax-tech.com/dev-m01421/xllm-maca3.7.1.9:v1` | `--shm-size 100gb`、`--device=/dev/mxcd --device=/dev/dri --device=/dev/infiniband`、`-v /opt/maca:...` |
| 摩尔线程 MUSA | `docker pull registry.mthreads.com/presale/devtech/xllm:0710` | `--shm-size=128g`、`--device=/dev/mtgpu0 --device=/dev/dri` |

所有容器统一使用 `-v $HOME:$HOME -w $HOME` 将用户家目录映射进容器并设为工作目录。

### 二、源码编译流程

```bash
git clone https://github.com/xLLM-AI/xllm.git
cd xllm
pip install pre-commit
pre-commit install
git submodule update --init --recursive

python setup.py build        # 仅编译 C++ 二进制
python setup.py bdist_wheel  # 生成 python wheel
python setup.py install      # 生成并安装 python wheel
```

### 三、跳过编译的判定条件

原文："如果下载的是 release 镜像，即 tag 中带有版本号的镜像，可以跳过此步，因为 release 镜像自带编译好的 xllm 二进制文件，可以直接调用 `xllm`。"

### 四、启动引擎

原文仅给出指引链接："请参考 [xllm 启动方式](/zh/getting_started/launch_xllm/)"，具体命令行参数与配置项**原文未涉及**，需跳转至该页查阅。
