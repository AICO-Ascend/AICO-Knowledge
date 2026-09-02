# A2 x86

> 仓 `xllm` · 路径 `docs/src/content/docs/en/getting_started/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/getting_started/quick_start.md

# xllm 快速入门文档深度解读

## 【定位】
本文档解决「如何获取并启动 xllm 推理引擎开发/运行环境」的问题——为多硬件后端 (NPU、NVIDIA GPU、MLU、Hygon DCU、MetaX MACA、Mthreads MUSA) 分别给出 Docker 镜像拉取与容器启动命令,以及源码编译构建步骤,作为用户接触 xllm 的第一步操作手册。

## 【技术要点】

1. **镜像统一托管在 Quay 仓库** (除 DCU/MACA/MUSA 单独仓库外),地址为 `https://quay.io/repository/jd_xllm/xllm-ai?tab=tags`,默认以 `dev` 镜像作为示例。
2. **NPU 后端 (华为昇腾)** 提供三类预编译 dev 镜像:`a2-x86-cann9-20260605`、`a2-arm-cann9-20260605`、`a3-arm-cann9-20260605`,需挂载 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 等驱动设备,并把宿主机的 `/usr/local/Ascend/driver`、`/usr/local/Ascend/add-ons/`、`/usr/local/sbin/npu-smi`、日志目录 (`/var/log/npu/conf/slog`、`/var/log/npu/slog`、`/var/log/npu/profiling`、`/var/log/npu/dump`) 全部映射进容器。
3. **NVIDIA GPU 后端** 提供 `xllm-dev-cuda-x86` 镜像与官方 `Dockerfile.cuda`,容器启动使用 `--shm-size '128gb'`、`--pid=host`、`--net=host`、`--ipc=host`,并以 `sudo` 执行。
4. **MLU 后端** 原文明确「不能提供 MLU 镜像」,仅给出通用容器启动模板 (同样 `128gb` shm、privileged、host 网络/PID/IPC)。
5. **Hygon DCU 后端** 使用 `harbor.sourcefind.cn:5443/dcu/admin/base/custom:xllm-dev-dcu-x86-20260617`,容器挂载 `/dev/kfd`、`/dev/dri`、`/dev/mkfd` 及 `/opt/hyhal`,`--shm-size 256g`,并开启 `--security-opt seccomp=unconfined`、`--group-add video`。
6. **MetaX MACA 后端** 镜像为 `pub-registry1.metax-tech.com/dev-m01421/xllm-maca3.7.1.9:v1`,容器挂载 `/dev/mxcd`、`/dev/dri`、`/dev/infiniband`,`--shm-size 100gb`,同时设置 apparmor/seccomp unconfined、`--ulimit memlock=-1`、`-v /opt/maca:/opt/maca`。
7. **Mthreads MUSA 后端** 镜像为 `registry.mthreads.com/presale/devtech/xllm:0710`,容器挂载 `/dev/mtgpu0`、`/dev/dri`,`--shm-size=128g`,`--ulimit memlock=-1`,完整细节指向 `/en/hardware/musa/`。
8. **构建流程** 使用 `setup.py` 体系:`git submodule update --init --recursive` 拉取子模块 (含 vcpkg),`python setup.py build` 编译 C++ 二进制,`python setup.py bdist_wheel` 打 Python wheel,`python setup.py install` 编译并安装 wheel。首次编译耗时较长,因 vcpkg 需要编译所有依赖;后续编译会更快。
9. **Release 镜像** 内置预编译 xllm 二进制,可以直接调用 `xllm` 命令,无需走源码构建步骤。

## 【关键机制与数据】

- **镜像存储路径** (原文):「All images are stored [here](https://quay.io/repository/jd_xllm/xllm-ai?tab=tags). The docker startup command below uses the dev image as an example.」
- **首次编译耗时机制** (原文):「In a new image, the first compilation of xllm takes a long time because all dependencies in vcpkg need to be compiled, but subsequent compilations will be much faster.」——瓶颈在于 vcpkg 需现场编译 C++ 依赖。
- **Release vs Dev 镜像差异** (原文):「If you download a release image, i.e., an image with a version number in the tag, you can skip this step because the release image comes with a pre-compiled xllm binary, and call `xllm` directly.」——通过 tag 是否包含「版本号」区分 release 与 dev。
- **容器启动数据流**:各后端通过 `--device=...` 显式透传加速器字符设备、`-v` 透传驱动/固件目录与日志目录、`--ipc=host` / `--network=host` / `--pid=host` 共享宿主 IPC/网络/PID 命名空间,共同构成 xllm 直接访问底层加速器与共享内存的通道。
- **性能数据**:原文未给出任何吞吐/延迟/显存占用类数字。

## 【表格解读】

原文无表格 (各镜像 tag 与容器命令以代码块形式呈现,未以表格组织)。

## 【公式解读】

原文无公式。

## 【关联】

- **`/en/hardware/musa/`** (内部链接):Mthreads MUSA 小节末尾指向「Mthreads MUSE for full details」,说明 MUSA 完整配置/硬件说明在该页面,本文档仅给出最小启动模板。
- **`/en/getting_started/launch_xllm/`** (内部链接):文档末尾「## Launch xllm」整节只给出这一引用 `Please refer to [How to Launch xllm](/en/getting_started/launch_xllm/).`,说明「如何实际调用 xllm 二进制跑模型」的内容不在本文档范围,需跳转该页面获取 (推测涵盖服务启动参数、模型路径、API 端口等)。
- **上游/模块关系推断 (基于文档文字,非推断外延)**:
  - `vcpkg` 子模块 → 首次 `setup.py build` 的 C++ 依赖来源;
  - `pre-commit` → 代码提交规范 (在仓库初始化阶段安装);
  - git submodule → 与 `xllm` 主仓库并列的第三方依赖。
  - DCU 后端透传的 `/opt/hyhal`、MACA 后端透传的 `/opt/maca` 暗示各自 HAL (Hardware Abstraction Layer) 软件栈位于宿主机 `/opt` 下,是后续 `setup.py build` 能够链接到厂商库的桥梁。

## 【使用方法】

**1. 拉取镜像 (按后端选其一)**

```bash
# NPU - 华为昇腾 A2 x86
docker pull quay.io/jd_xllm/xllm-ai:xllm-dev-a2-x86-cann9-20260605
# NPU - A2 arm
docker pull quay.io/jd_xllm/xllm-ai:xllm-dev-a2-arm-cann9-20260605
# NPU - A3 arm
docker pull quay.io/jd_xllm/xllm-ai:xllm-dev-a3-arm-cann9-20260605

# NVIDIA GPU
docker pull quay.io/jd_xllm/xllm-ai:xllm-dev-cuda-x86

# Hygon DCU
docker pull harbor.sourcefind.cn:5443/dcu/admin/base/custom:xllm-dev-dcu-x86-20260617

# MetaX MACA
docker pull pub-registry1.metax-tech.com/dev-m01421/xllm-maca3.7.1.9:v1

# Mthreads MUSA
docker pull registry.mthreads.com/presale/devtech/xllm:0710

# MLU: 原文未涉及具体镜像 (仅给出启动命令)
```

**2. 启动容器 (按后端选其一,完整命令见原文)**

- **NPU**:必传 `--device=/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,并 `-v` 挂载 Ascend driver、add-ons、npu-smi、日志目录,`--network=host`。
- **NVIDIA GPU / MLU**:通用模板,`--privileged`、`--shm-size '128gb'`、`--net=host`、`--pid=host`、`--ipc=host`,NVIDIA 需 `sudo`。
- **DCU**:`--shm-size 256g`、透传 `/dev/kfd`、`/dev/dri`、`/dev/mkfd`、`-v /opt/hyhal:/opt/hyhal`、`--security-opt seccomp=unconfined`、`--group-add video`。
- **MACA**:`--shm-size 100gb`、透传 `/dev/mxcd`、`/dev/dri`、`/dev/infiniband`、`-v /opt/maca:/opt/maca`、apparmor/seccomp 均 unconfined、`--ulimit memlock=-1`。
- **MUSA**:`--shm-size=128g`、`/dev/mtgpu0`、`/dev/dri`、`--ulimit memlock=-1`、镜像直接作为命令末尾参数传入。

**3. 编译 xllm (仅 dev 镜像或源码用户)**

```bash
git clone https://github.com/xLLM-AI/xllm.git
cd xllm
pip install pre-commit
pre-commit install
git submodule update --init --recursive
python setup.py build          # 编译 C++ 二进制
python setup.py bdist_wheel    # 仅打 wheel
python setup.py install        # 打 wheel 并安装
```

**4. 跳过编译**:tag 含版本号的 release 镜像内置 `xllm` 二进制,容器内直接执行 `xllm` 即可,无需 `setup.py`。

**5. 启动 xllm 服务**:原文未涉及具体命令/参数,跳转 `/en/getting_started/launch_xllm/`。
