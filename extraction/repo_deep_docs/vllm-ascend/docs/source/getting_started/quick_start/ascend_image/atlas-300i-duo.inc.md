# atlas-300i-duo.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/ascend_image/atlas-300i-duo.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/atlas-300i-duo.inc.md

# 「Atlas 300I DUO 快速启动」文档深度解读

---

## 【定位】

这篇文档是 vllm-ascend 在 **Atlas 300I DUO**（基于 Ascend 310P 芯片）硬件平台上的容器化快速部署指南，告诉用户如何拉取对应镜像并启动一个可访问 310P NPU 设备、加载模型缓存的 Docker 容器，以便后续运行 vLLM-Ascend 推理服务。

---

## 【技术要点】

1. **镜像标签区分操作系统变体**：Ubuntu 与 openEuler 两个 OS 对应两条独立镜像 tag，**后缀 `-310p`** 标识 Atlas 300I DUO（Ascend 310P）硬件架构，而 `-310p-openeuler` 则是同硬件在 openEuler 系统下的变体。
2. **镜像仓库与版本占位符**：统一使用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p[-openeuler]`，`{{ vllm_ascend_version }}` 为文档构建时的 Jinja 模板变量，最终渲染为具体版本号。
3. **容器命名与生命周期管理**：`--rm --name vllm-ascend` 表示退出即删除且固定容器名为 `vllm-ascend`；`--shm-size=1g` 显式分配 **1 GB 共享内存**（PyTorch DataLoader 等多进程场景必需）。
4. **四类 NPU 设备透传**：必须挂载 `/dev/davinci0`（即 `$DEVICE` 可配置的计算设备节点）、`/dev/davinci_manager`（设备管理器）、`/dev/devmm_svm`（共享虚拟内存）、`/dev/hisi_hdc`（主机-设备通信通道），缺一不可。
5. **驱动与固件只读挂载**：通过 `-v` 将宿主机侧的 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`version.info`、`/etc/ascend_install.info` 注入容器，使容器复用宿主机已安装的 Ascend 驱动栈（避免容器内重复安装/版本错位）。
6. **模型缓存与端口暴露**：模型缓存目录通过 `MODEL_CACHE` 环境变量（默认 `${HOME}/.cache`）映射至容器内 `/root/.cache`；服务端口固定为 **`-p 8000:8000`**，符合 OpenAI 兼容 API 默认端口；交互入口为 `-it "$IMAGE" bash`。

---

## 【关键机制与数据】

> **原文无性能数据、无数据流图。** 以下为从原文命令中可直接读出的机制要点：

- **设备节点命名约定**：`/dev/davinci0` 中的数字 `0` 表示第 0 张 NPU 卡，因此 `DEVICE` 环境变量可改为 `/dev/davinci1`、`/dev/davinci2` 等以切换卡号；多卡推理需相应追加 `--device` 行（原文仅示范单卡）。
- **只读驱动共享机制**：容器不自带 Ascend CANN 驱动，而是依赖宿主机驱动挂载——这意味着宿主机必须预先安装与镜像兼容的 Ascend 驱动版本，否则容器内 `npu-smi` 等工具无法识别设备。
- **共享内存（SHM）机制**：`--shm-size=1g` 覆盖 Docker 默认 64MB 限制，避免 PyTorch DataLoader 多 worker 通信或 vLLM 内部 IPC 时报 `RuntimeError: DataLoader worker (pid xxx) is killed by signal: Bus error`。
- **镜像变体隔离**：Ubuntu 与 openEuler 的 `docker run` 命令块**完全一致**（设备、卷、端口、SHM 参数无任何差异），说明 vllm-ascend 已将 OS 差异消化在镜像层，上层运维命令统一。

---

## 【表格解读】

**原文无表格。** 文档仅由两个操作系统分支（Ubuntu / openEuler）下的代码块组成，无参数对比表、无性能对照表、无配置矩阵。

---

## 【公式解读】

**原文无公式。** 全文仅包含 Bash 命令与 Jinja 模板占位符 `{{ vllm_ascend_version }}`，未出现任何数学表达式或伪代码。

---

## 【关联】

- **`image_download_mirror.inc.md`（include 片段）**：本文通过 `{% include %}` 引入该片段，位于 `getting_started/quick_start/ascend_image/` 目录下，负责提供镜像下载的镜像源（mirror）说明——这是所有 Atlas / 800I / A2 等硬件快速启动文档共享的公共片段，本文复用之。
- **同目录兄弟文档（隐含关系）**：文档锚点 `#quick-start-atlas-300i-duo-ubuntu`、`#quick-start-atlas-300i-duo-openeuler`、`#quick-start-atlas-300i-duo-container` 的命名遵循 `quick-start-<硬件>-<OS>/<阶段>` 规范，与同目录其他硬件（如 Atlas 800I A2、Atlas 900 等）保持一致结构，说明这是 vllm-ascend **按硬件分卷**的快速启动系列中的一篇。
- **上游 vLLM 与 CANN 驱动栈**：`/usr/local/dcmi`、`npu-smi`、`Ascend/driver/lib64` 的挂载依赖宿主机已安装的 Ascend CANN 工具链；`8000` 端口对应 vLLM 默认的 OpenAI 兼容 HTTP 服务端口——意味着本容器准备好后直接 `vllm serve …` 即可对外暴露 API。
- **模板变量 `{{ vllm_ascend_version }}`**：该占位符由文档站构建系统（Sphinx + MyST）渲染，引用项目统一发布的版本号，确保文档与发布版本同步。

> 原文 metadata 中标注 **(无)** 内部链接，但文档内嵌的三个 HTML `id`/`span id`（`#quick-start-atlas-300i-duo-ubuntu`、`#quick-start-atlas-300i-duo-openeuler`、`#quick-start-atlas-300i-duo-container`）本身可作为锚点供同文档其他章节或目录交叉引用。

---

## 【使用方法】

**步骤一：拉取镜像**

```bash
# Ubuntu 环境
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p
docker pull "$IMAGE"

# openEuler 环境
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p-openeuler
docker pull "$IMAGE"
```

**步骤二：准备模型缓存目录**

```bash
export MODEL_CACHE="${HOME}/.cache"
mkdir -p "$MODEL_CACHE"
```

**步骤三：启动容器**（Ubuntu / openEuler 命令相同）

```bash
export DEVICE=/dev/davinci0
docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --device "$DEVICE" \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v "$MODEL_CACHE:/root/.cache" \
    -p 8000:8000 \
    -it "$IMAGE" bash
```

**关键配置项速查：**

| 配置项 | 取值 | 作用 |
|---|---|---|
| `--shm-size` | `1g` | 扩展容器共享内存 |
| `--device` | `$DEVICE` + 3 个管理节点 | 透传 NPU 设备与驱动通道 |
| `-v` 驱动挂载 | 5 条宿主 → 容器路径 | 复用宿主机 Ascend CANN 驱动 |
| `-v` 模型缓存 | `$MODEL_CACHE` → `/root/.cache` | 持久化 HF/ModelScope 模型权重 |
| `-p` | `8000:8000` | 暴露 vLLM OpenAI 兼容 API |
| `-it … bash` | — | 进入交互式 shell，便于手动启动推理服务 |

> **前置条件（原文未明列但隐含要求）**：宿主机需已正确安装 Ascend 310P 对应版本的 CANN 驱动，并确认 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 节点存在；否则容器启动后 `npu-smi info` 将无法识别设备。
