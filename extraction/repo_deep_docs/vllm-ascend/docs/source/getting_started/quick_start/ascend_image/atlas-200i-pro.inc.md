# atlas-200i-pro.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/ascend_image/atlas-200i-pro.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-200i-pro.inc.md

# 深度解读：Atlas 200I Pro 快速启动文档

## 【定位】

本文档是 vllm-ascend 项目针对 **Atlas 200I Pro**（基于 Ascend 310P 芯片）硬件平台的容器化快速启动指南，描述如何拉取预构建 Docker 镜像并在 Ubuntu/openEuler 主机上以特权模式启动容器，挂载 NPU 设备节点和驱动运行时依赖，以便运行 vLLM 推理服务。

---

## 【技术要点】

1. **镜像标签与变体**：镜像仓库为 `quay.io/ascend/vllm-ascend`，版本号通过 Jinja 变量 `{{ vllm_ascend_version }}` 注入（运行时由 Sphinx/MkDocs 模板替换），针对 Atlas 200I Pro 的两个 tag 分别为 `-310p`（Ubuntu 宿主）和 `-310p-openeuler`（openEuler 宿主）。

2. **镜像下载**：使用 `docker pull` 前通过 `export IMAGE=...` 设置环境变量，再 `"$IMAGE"` 引用；具体下载流程被内联到 `image_download_mirror.inc.md` 子文档（用于处理镜像加速/国内镜像源场景）。

3. **容器启动前置条件（警告）**：Atlas 200I Pro 相比标准 Atlas 800I A2（300I Duo）等需要**额外挂载** NPU 设备节点、驱动运行时库与宿主机配置文件；命令中所有 `-v` 挂载路径必须**预先存在于宿主机**，否则容器启动会失败。

4. **设备透传（`--device`）**：挂载 `/dev/davinci0`（昇腾 NPU 计算设备 0）、`/dev/davinci_manager`（设备管理器）、`/dev/ascend_manager`（昇腾资源管理器）、`/dev/user_config`（用户态配置）共 4 个设备节点，覆盖 310P 芯片的设备识别与管理通道。

5. **运行时卷挂载（Ubuntu 变体共 14 个 `-v`）**：包含 sys_version 版本信息、`mind_so.conf` 链接库配置、`hdcBasic.cfg` 主机设备连接配置、`dmp_daemon` 数据管理守护进程目录、`libmmpa.so`/`libcrypto.so.1.1`/`libyaml-0.so.2`（注意 Ubuntu 路径在 `/usr/lib/aarch64-linux-gnu/`）等昇腾栈运行时依赖；`/usr/local/Ascend/driver/lib64` 提供 CANN 驱动库；`/var/slogd` 与 `/etc/slog.conf` 提供日志守护。

6. **openEuler 差异点**：相比 Ubuntu 增加 `/usr/lib64/libsemanage.so.2` 挂载；`libyaml` 路径从 Ubuntu 的 `/usr/lib/aarch64-linux-gnu/libyaml-0.so.2` 改为 `/usr/lib64/libyaml-0.so.2.0.9`（即带 `.0.9` 版本号后缀的 openEuler 默认位置）。

7. **容器运行参数**：`--privileged`（特权模式，访问底层设备所需）、`--name vllm-ascend`、`--shm-size=10g`（10 GiB 共享内存，用于 PyTorch/vLLM 的张量并行通信）、端口映射 `8000:8000`（vLLM 默认 HTTP 服务端口）、`-it "$IMAGE" bash`（交互式 bash 启动）。

8. **模型缓存路径**：`MODEL_CACHE="${HOME}/.cache"`，挂载到容器内 `/root/.cache`，用于持久化 HuggingFace 模型下载，避免容器重建后重复下载。

---

## 【关键机制与数据】

**工作原理 / 数据流**：

1. **镜像获取阶段**：用户根据宿主系统选择 `310p` 或 `310p-openeuler` tag → Docker 从 quay.io 拉取包含预装 vLLM、Ascend CANN、torch_npu 等依赖的镜像（子文档 `image_download_mirror.inc.md` 处理加速逻辑）。

2. **设备资源透传**：通过 `--device` 将宿主机的 `/dev/davinci0` 等设备节点直接映射到容器，使容器内进程能通过昇腾驱动调用 NPU 硬件；`--privileged` 关闭 seccomp/apparmor 限制，允许容器进行设备 ioctl 与资源管理。

3. **运行时栈绑定**：通过 `-v` 绑定宿主机 `/usr/local/Ascend/driver/lib64` 等目录，使容器内昇腾运行时库（libascend、libdrv、libslog 等）与宿主机驱动版本保持一致，避免 ABI 不匹配。

4. **服务暴露**：容器内 vLLM 默认监听 8000 端口（OpenAI 兼容 API），通过 `-p 8000:8000` 暴露到宿主机，供外部客户端访问。

5. **模型加载路径**：宿主机 `~/.cache` → 容器 `/root/.cache`，vLLM 启动时会从该路径读取预下载的 HuggingFace 模型权重。

**原文未涉及**：性能数据（吞吐、延迟、算力利用率）、内存/显存占用、量化配置等具体数值。

---

## 【表格解读】

原文无表格。

但为便于对比，可整理出 **Ubuntu 与 openEuler 挂载差异表**（基于原文逐字提取，非原文表格）：

| 差异项 | Ubuntu | openEuler |
|---|---|---|
| 镜像 tag 后缀 | `-310p` | `-310p-openeuler` |
| `libsemanage.so.2` | 未挂载 | `/usr/lib64/libsemanage.so.2:/usr/lib64/libsemanage.so.2` |
| `libyaml-0.so.2` 源路径 | `/usr/lib/aarch64-linux-gnu/libyaml-0.so.2` | `/usr/lib64/libyaml-0.so.2.0.9` |
| 总 `-v` 挂载数量 | 14 个 | 15 个（多 1 个 libsemanage） |

**逐行解读**：
- **镜像 tag 差异**：体现两套基础镜像分别构建在 Ubuntu 与 openEuler 用户态库之上，不能混用。
- **libsemanage.so.2**：SELinux 语义管理库，是 openEuler（默认启用 SELinux 安全策略）上部分昇腾组件的运行时依赖。
- **libyaml 路径**：Ubuntu 走 Debian 系多架构布局 `/usr/lib/aarch64-linux-gnu/`，openEuler 走集中式 `/usr/lib64/`；版本号 `.2.0.9` 体现 openEuler 包管理器固定版本号的习惯。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档**未在文末提供内部链接**（文档头注明"内部链接: (无)"）。

基于文档自身结构推断的关联点（基于原文出现位置的提及）：

- **子文档引用**：包含 `{% include "getting_started/quick_start/ascend_image/image_download_mirror.inc.md" %}` —— 指向同目录下的「镜像下载镜像源」共享片段，处理国内/特殊网络环境下 quay.io 的拉取加速。
- **同一镜像指南族**：文档路径 `atlas-200i-pro.inc.md` 与同名目录的其他 `inc.md`（推测存在 `atlas-800i-a2.inc.md` 等）平行，覆盖 vllm-ascend 支持的不同 Atlas 硬件型号；本文是其中针对 310P 芯片 Atlas 200I Pro 的分支。
- **上游依赖**：镜像内含 vLLM 主线推理引擎 + Ascend CANN + torch-npu，本指南不涉及这些组件的版本细节，但容器能否运行取决于宿主机 CANN 驱动与镜像内 CANN 运行时版本一致。

---

## 【使用方法】

**启用方式 / 命令（原文逐字摘录）**：

**步骤 1：拉取镜像**

```bash
# Ubuntu 宿主
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p
docker pull "$IMAGE"

# openEuler 宿主
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p-openeuler
docker pull "$IMAGE"
```

**步骤 2：创建模型缓存目录并启动容器**

```bash
export MODEL_CACHE="${HOME}/.cache"
mkdir -p "$MODEL_CACHE"

docker run --rm \
    --privileged \
    --name vllm-ascend \
    --shm-size=10g \
    --device=/dev/davinci0:/dev/davinci0 \
    --device=/dev/davinci_manager \
    --device=/dev/ascend_manager \
    --device=/dev/user_config \
    [其余 -v 挂载见原文 Ubuntu/openEuler 各自块] \
    -v "$MODEL_CACHE:/root/.cache" \
    -p 8000:8000 \
    -it "$IMAGE" bash
```

**关键配置项说明（基于原文出现）**：

| 参数 | 取值 | 作用 |
|---|---|---|
| `--shm-size` | `10g` | 容器共享内存大小，张量并行 IPC 通信所需 |
| `-p` | `8000:8000` | vLLM HTTP API 端口映射 |
| `--name` | `vllm-ascend` | 容器名称 |
| `--device` ×4 | davinci0 / davinci_manager / ascend_manager / user_config | NPU 设备透传 |
| 镜像 tag | `-310p` 或 `-310p-openeuler` | 区分 Ubuntu / openEuler 宿主 |

**前置依赖（原文警告项）**：启动容器前必须确保宿主机以下路径/文件存在：`/etc/sys_version.conf`、`/etc/ld.so.conf.d/mind_so.conf`、`/etc/hdcBasic.cfg`、`/var/dmp_daemon`、`/usr/local/sbin/npu-smi`、`/etc/slog.conf`、`/var/slogd`、`/usr/local/Ascend/driver/lib64`、Ubuntu 上的 `/usr/lib/aarch64-linux-gnu/libyaml-0.so.2` 或 openEuler 上的 `/usr/lib64/libyaml-0.so.2.0.9` 等。

**镜像内后续操作**：容器启动后进入 bash，需进一步执行 `vllm serve <model>` 等命令启动推理服务（**原文未涉及**，属于 vLLM 主线用法）。
