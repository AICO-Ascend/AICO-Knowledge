# Quick Start

> 仓 `multimodalsdk` · 路径 `docs/en/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/multimodalsdk/docs/en/quickstart.md

# MultimodalSDK `docs/en/quickstart.md` 深度解读

---

## 【定位】

这篇文档是 MultimodalSDK（多模态预处理加速 SDK）的**入门上手指南**，目标是让用户通过 Docker 镜像方式快速拉起 Atlas 800I A2 推理服务器上的运行环境，并以一个最小的图像 resize Python 示例验证 SDK 安装/链接/加速管线是否就绪。它本身不展开多模态 API 的能力细节，而是作为通向「图像/视频/音频处理、Qwen2VL/InternVL2 适配、vLLM 集成、完整 API 参考」的入口。

---

## 【技术要点】

1. **SDK 能力范围**：文档明确给出 MultimodalSDK 提供的四大类多模态预处理加速能力——**图像解码 (image decoding)、图像 resize/crop、视频帧解码 (video frame decoding)、音频加载 (audio loading)**——这也是本文示例中 `Image.resize` 调用所对应的核心算子类别。
2. **运行环境载体**：原生安装路径在外部链接（`./installation_guide.md`），本文档选择 **Docker 镜像** 方式作为快速通道，且明确测试图像 `/data/test.jpg` 由镜像自带，无需额外挂载测试数据目录。
3. **硬件前提**：Atlas 800I A2 推理服务器 + 配套 NPU 驱动/CANN；推荐使用 `npu-smi info` 做驱动预检，并比对镜像 CANN 版本与宿主机驱动版本的兼容性。
4. **镜像 Tag 命名规范**：格式 `{version}-{chip}-{os}-{python}-{arch}`，文档给出全部 5 个变量及其示例取值（`26.0.0` / `910b` / `ubuntu22.04` 或 `openeuler24.03` / `py3.11` / `aarch64` 或 `x86_64`），并要求用户区分 CPU 架构（x86_64 / aarch64）与 Ascend 芯片型号（Ascend 310 / 910 等）。
5. **容器设备透传**：启动容器必须显式挂载 NPU 相关设备与驱动文件，包括 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，以及 `/usr/local/dcmi`、`npu-smi`、`/usr/local/Ascend/driver/lib64`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info`；其中 `--device /dev/davinci0` 的设备号需根据宿主机实际 NPU 编号调整（如 `davinci1`）。
6. **环境变量加载**：进入容器后通过 `source ${MULTIMODAL_SDK_HOME}/script/set_env.sh` 完成 SDK 环境初始化；若漏执行会出现 `Failed to import mm` 的典型故障。
7. **验证脚本最小用例**：使用 `mm.Image.open(test_image, "cpu")` 加载、`img.resize((500, 500), Interpolation.BICUBIC, DeviceMode.CPU)` 完成 CPU 模式下的双三次插值缩放，最终以 `img_resize.numpy().shape` 输出 `(500, 500, 3)` 作为验证通过的标志。

---

## 【关键机制与数据】

**工作原理与数据流（基于原文梳理）**：

整个 Quick Start 的数据流是「硬件 → 驱动 → Docker 镜像 → 容器内 SDK 环境 → Python API 调用 → numpy 输出验证」，具体链路如下：

- **硬件层**：Atlas 800I A2 推理服务器提供 NPU 算力，宿主机已安装 Ascend 驱动与 `npu-smi` 工具，可通过 `npu-smi info` 查询驱动状态。
- **镜像层**：从 `swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk` 拉取与硬件型号匹配的镜像（本文示例具体值为 `26.0.0-910b-ubuntu22.04-py3.11-aarch64`），并 `docker tag` 为本地短名 `multimodalsdk:26.0.0-910b-ubuntu22.04-py3.11-aarch64`。
- **容器层**：`docker run` 启动容器 `multimodal_container`，通过 `--device` 透传 NPU 字符设备，通过 `-v` 挂载驱动库与版本信息文件，保证容器内进程能直接访问宿主机的 NPU 驱动栈。
- **SDK 环境层**：`source ${MULTIMODAL_SDK_HOME}/script/set_env.sh` 在容器 shell 中写入 `MULTIMODAL_SDK_HOME` 等环境变量，使 Python 能找到 `mm` 包及配套动态库。
- **数据流层**：测试图像 `/data/test.jpg` 由镜像内自带 → `Image.open(test_image, "cpu")` 在 CPU 侧解码 → `resize((500, 500), Interpolation.BICUBIC, DeviceMode.CPU)` 完成 500×500 的双三次插值缩放 → `.numpy()` 转为 NumPy 数组 → 打印 shape `(500, 500, 3)`（即 HWC 排列的 3 通道 RGB 数据）。

**性能/数据相关数字（原文逐字标注）**：
- 原文: 输出 shape = `(500, 500, 3)`，对应 resize 后的高度=500、宽度=500、通道数=3。
- 原文: 图像权限要求 `chmod 640`，权限不得高于 640。
- 原文: 镜像 Tag 5 个变量示例值分别为 `26.0.0` / `910b` / `ubuntu22.04` / `py3.11` / `aarch64`，并指出 `os` 还可取 `openeuler24.03`、`arch` 还可取 `x86_64`。
- 原文: 图像解码/缩放参数为 `(500, 500)`，插值方式 `BICUBIC`，运行模式 `DeviceMode.CPU`。

---

## 【表格解读】

### 表格 1：镜像 Tag 变量定义表（原文逐字还原）

| Variable | Description | Example |
|------|------|--------|
| `{version}` | Multimodal SDK version | `26.0.0` |
| `{chip}` | Ascend chip series | `910b` |
| `{os}` | Base operating system | `ubuntu22.04` / `openeuler24.03` |
| `{python}` | Python version | `py3.11` |
| `{arch}` | CPU architecture | `aarch64` / `x86_64` |

**逐行解读**：

- **`{version}` = Multimodal SDK version**：表示 SDK 自身的版本号，示例取 `26.0.0`，这是 MultimodalSDK 的语义化版本号，决定 API 与算子实现的兼容性边界。
- **`{chip}` = Ascend chip series**：指 Ascend NPU 芯片系列，示例取 `910b`，对应 Atlas 800I A2 推理服务器使用的昇腾 910B 芯片；该变量决定了镜像内预编译的 CANN toolkit/算子库的目标 ISA。
- **`{os}` = Base operating system**：表示镜像底层操作系统，可选 `ubuntu22.04` 或 `openeuler24.03`，影响 glibc、系统库版本与发行版包管理路径。
- **`{python}` = Python version**：示例为 `py3.11`，指镜像内置 Python 解释器主版本，决定 `mm` 包的 ABI 与 wheel 兼容性。
- **`{arch}` = CPU architecture**：CPU 架构，可选 `aarch64` 或 `x86_64`；Atlas 800I A2 默认 ARM 主机，因此示例使用 `aarch64`，而 x86 主机则需切到 `x86_64` 镜像。
- 整体而言，这张表定义了**一个 5 元组版本标签**，将 SDK 版本、芯片、OS、Python、CPU 架构五维信息编码进镜像 Tag，确保用户拉取的镜像与本地软硬件栈完全对齐。

### 表格 2：Next Steps 目标—文档对照表（原文逐字还原）

| Goal | Document |
| -- | -- |
| Image resize/crop visualization examples | [Examples and Guidance - Image Processing](./user_guide.md#image-processing) |
| Video frame decoding | [Examples and Guidance - Video Processing](./user_guide.md#video-processing) |
| Audio loading | [Examples and Guidance - Audio Processing](./user_guide.md#audio-processing) |
| Qwen2VL / InternVL2 preprocessing acceleration | [Adapter](./api/adapter.md) |
| vLLM inference framework integration | [patcher](./api/patcher.md) |
| Complete API reference | [Function Reference](./api/function_reference.md) |

**逐行解读**：

- **Image resize/crop visualization examples**：把 Quick Start 中的最小 resize 示例扩展为可视化案例，对应 `user_guide.md#image-processing`，覆盖图像处理全流程。
- **Video frame decoding**：跳转至 `user_guide.md#video-processing`，对应文档开头列出的「视频帧解码」能力。
- **Audio loading**：跳转至 `user_guide.md#audio-processing`，对应文档开头列出的「音频加载」能力。
- **Qwen2VL / InternVL2 preprocessing acceleration**：通过 `api/adapter.md` 接入主流多模态大模型的预处理加速，是 SDK 与上层模型之间的适配层。
- **vLLM inference framework integration**：通过 `api/patcher.md` 提供 vLLM 推理框架的 patch 集成方式，凸显 SDK 在大模型推理链路中的预处理角色。
- **Complete API reference**：完整 API 索引见 `api/function_reference.md`，作为所有调用方式的权威参考。

### 表格 3：Quick Troubleshooting 症状—解决方案对照表（原文逐字还原）

| Symptom | Solution |
| -- | -- |
| File permission error | Ensure image permissions are no higher than 640: `chmod 640 "$TEST_IMAGE"` |
| Test image not found in container | Confirm that the image version includes `/data/test.jpg`, and `TEST_IMAGE` uses the container path `/data/test.jpg` |
| Container cannot access NPU | Check NPU driver mounting and `--device /dev/davinci*` device number |
| Failed to import `mm` | Confirm `source ${MULTIMODAL_SDK_HOME}/script/set_env.sh` was executed |
| More issues | [FAQ](./faq.md), [Appendix](./appendix.md) |

**逐行解读**：

- **File permission error**：当测试图像权限高于 640 时 `Image.open` 可能因安全策略失败，解决方案是用 `chmod 640` 收紧权限（不超过 640）。
- **Test image not found in container**：测试图像未找到时，需确认两点——镜像内确实带有 `/data/test.jpg`（无需外挂载），且环境变量 `TEST_IMAGE` 必须使用容器内路径 `/data/test.jpg` 而非宿主机路径。
- **Container cannot access NPU**：容器看不到 NPU 时，问题多出在驱动挂载或 `--device /dev/davinci*` 的设备号与宿主机实际 NPU 编号不匹配。
- **Failed to import `mm`**：Python 找不到 `mm` 模块，通常是因为漏执行 `source ${MULTIMODAL_SDK_HOME}/script/set_env.sh`，环境变量未生效。
- **More issues**：超出以上四类典型问题的，进一步参考 `faq.md` 与 `appendix.md`。

---

## 【公式解读】

**原文无公式**。

文档中未出现任何数学公式或伪代码形式的算子定义；唯一的「类公式表达」是镜像 Tag 的字符串模板 `TAG={version}-{chip}-{os}-{python}-{arch}`，这是一条命名规范（见表格 1），不构成数学公式，本文不强行将其升级为公式解读。

---

## 【关联】

本文档作为 Quick Start，处于文档树的**入口枢纽位置**，向上承接环境与硬件文档，向下分发到 API 与各模态用户指南，具体上下游关系如下：

- **上游 — 环境与硬件依赖**：
  - `./installation_guide.md`：当用户不走 Docker、需要在宿主机原生安装时跳转至此，是 Quick Start 的替代路径。
  - `./introduction.md#supported-hardware-and-oss`：Atlas 800I A2 等硬件以及配套 OSS 信息的权威出处，Quick Start 的「Prerequisites」直接引用之。
- **下游 — 各模态用户指南**：
  - `./user_guide.md#image-processing`：图像 resize/crop 可视化示例的扩展。
  - `./user_guide.md#video-processing`：视频帧解码详细用法。
  - `./user_guide.md#audio-processing`：音频加载详细用法。
- **下游 — 框架/模型集成**：
  - `./api/adapter.md`：Qwen2VL / InternVL2 等多模态大模型预处理加速适配器。
  - `./api/patcher.md`：vLLM 推理框架集成 patch。
- **下游 — 权威参考与故障排查**：
  - `./api/function_reference.md`：完整 API 函数参考。
  - `./faq.md` 与 `./appendix.md`：在 Quick Troubleshooting 表中作为「More issues」出口，覆盖文档级常见问题与附录信息。

整体看，Quick Start 的角色是「用一次最小 Python 调用（Image.open + resize）确认链路通畅」，随后通过 Next Steps 表与 Troubleshooting 表把用户精准路由到具体的模态用户指南、模型/框架集成层以及排障参考。

---

## 【使用方法】

**启用方式**（原文按 4 步给出）：

1. **Step 1 — 拉取镜像**：先用 `npu-smi info` 预检 NPU 驱动，再根据硬件型号在 Ascend Community 镜像仓库选定版本，按 `TAG={version}-{chip}-{os}-{python}-{arch}` 模板拼出完整 Tag；本文给出 `26.0.0-910b-ubuntu22.04-py3.11-aarch64` 的具体示例：
   ```bash
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:26.0.0-910b-ubuntu22.04-py3.11-aarch64
   docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:26.0.0-910b-ubuntu22.04-py3.11-aarch64 \
       multimodalsdk:26.0.0-910b-ubuntu22.04-py3.11-aarch64
   ```
2. **Step 2 — 启动容器**：使用 `docker run` 透传 NPU 设备与驱动挂载，容器名 `multimodal_container`，注意 `--device /dev/davinci0` 需根据实际 NPU 编号调整：
   ```bash
   docker run \
       --name multimodal_container \
       --device /dev/davinci0 \
       --device /dev/davinci_manager \
       --device /dev/devmm_svm \
       --device /dev/hisi_hdc \
       -v /usr/local/dcmi:/usr/local/dcmi \
       -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
       -v /usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64 \
       -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
       -v /etc/ascend_install.info:/etc/ascend_install.info \
       -itd multimodalsdk:26.0.0-910b-ubuntu22.04-py3.11-aarch64 bash
   ```
3. **Step 3 — 进入容器并加载环境**：
   ```bash
   docker exec -it multimodal_container bash
   source ${MULTIMODAL_SDK_HOME}/script/set_env.sh
   ```
4. **Step 4 — 运行验证脚本**：
   ```bash
   export TEST_IMAGE="/data/test.jpg"
   chmod 640 "$TEST_IMAGE"
   python3 - <<'EOF'
   import os
   from mm import Image, DeviceMode, Interpolation

   test_image = os.environ["TEST_IMAGE"]
   img = Image.open(test_image, "cpu")
   img_resize = img.resize((500, 500), Interpolation.BICUBIC, DeviceMode.CPU)
   print(f"resize output shape: {img_resize.numpy().shape}")
   EOF
   ```

**配置项 / 关键参数（原文已出现）**：

- `TEST_IMAGE`：测试图像路径，**必须**使用容器内路径 `/data/test.jpg`，权限不超过 640（`chmod 640`）。
- `mm.Image.open(test_image, "cpu")`：第一参数为图像路径，第二参数为解码后端（CPU）。
- `img.resize((500, 500), Interpolation.BICUBIC, DeviceMode.CPU)`：三参数分别为目标 (H, W) = `(500, 500)`、插值方式 `Interpolation.BICUBIC`、运行模式 `DeviceMode.CPU`。
- 容器启动参数：`--device` 透传 4 个 NPU 相关字符设备，`-v` 挂载 5 个驱动/版本/安装信息文件路径。

**验证成功的判定标准（原文）**：

- 输出 `resize output shape: (500, 500, 3)`，即表示 SDK 已就绪。
