# 快速入门

> 仓 `multimodalsdk` · 路径 `docs/zh/02_quickstart/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/multimodalsdk/docs/zh/02_quickstart/quickstart.md

# MultimodalSDK 快速入门文档深度解读

## 【定位】

本文档是 MultimodalSDK 的入门级实操指南，解决"如何在昇腾 Atlas 800I A2 推理服务器上，通过 Docker 快速拉起 MultimodalSDK 容器并跑通首个图像 resize 验证脚本"的问题，为后续深入使用图片/视频/音频处理、Qwen2VL/InternVL2 适配、vLLM 集成等能力奠定环境基础。

---

## 【技术要点】

1. **目标硬件限定**：仅支持 Atlas 800I A2 推理服务器，且仅支持 `aarch64` CPU 架构。
2. **环境加载机制**：使用环境变量 `MULTIMODAL_SDK_HOME`（默认 `/usr/local/multimodal`），通过 `source ${MULTIMODAL_SDK_HOME}/script/set_env.sh` 激活 SDK 环境。
3. **NPU 设备透传**：容器启动时需挂载 `--device /dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，以及驱动相关目录 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64`、`version.info`、`/etc/ascend_install.info`。
4. **镜像 Tag 命名规范**：`{version}-{cann}-{torch_npu}-910b-{os}-{python}-aarch64`，共 6 个语义段，含硬件代号 `910b`。
5. **Python API 验证示例**：使用 `Image.open(test_image, "cpu")` 解码图像，`Image.resize((500, 500), Interpolation.BICUBIC, DeviceMode.CPU)` 执行 resize，输出形状 `(500, 500, 3)`。
6. **测试图片内置**：镜像内已预置 `/data/test.jpg`（1920×1080 狗狗图），无需额外挂载；若缺失可从 gitcode 下载，权限需设为 `chmod 640`。

---

## 【关键机制与数据】

**工作流数据流（原文描述的 6 步流程）：**

```
拉取镜像 → 启动容器（挂载 NPU 设备与驱动目录）→ exec 进入容器 
→ source 环境脚本加载 SDK → 运行 Python 验证脚本 → exit + docker stop/rm 清理
```

**关键执行结果（原文）：**

- 验证脚本成功输出：`resize output shape: (500, 500, 3)`，即 500×500 像素、3 通道（RGB）的图像。
- 设备调用：`Image.open` 第二参数为解码设备字符串，当前仅支持 `"cpu"`；resize 等算子使用 `DeviceMode.CPU` 枚举。
- 权限控制：`chmod 640 "$TEST_IMAGE"`，避免文件权限报错。
- 驱动预检命令：`npu-smi info`，用于验证 NPU 驱动状态。
- 容器名统一为 `multimodal_container`，启动后用 `docker ps -a | grep multimodal_container` 校验。

**性能数据**：原文未涉及具体吞吐/时延/加速比等性能数字。

---

## 【表格解读】

### 表 1：镜像 Tag 变量含义表

| 变量 | 含义 | 示例值 |
|------|------|--------|
| `{version}` | Multimodal SDK 版本 | `26.1.0` |
| `{cann}` | cann 版本 | `9.1.0` |
| `{torch_npu}` | torch_npu 版本 | `2.6.0.rc1` |
| `{os}` | 基础操作系统 | `ubuntu22.04` / `openeuler24.03` |
| `{python}` | Python 版本 | `py3.12` |

**逐行解读：**

- **`{version}`**：SDK 自身的版本号，决定可用特性集合。示例 `26.1.0`。
- **`{cann}`**：华为 CANN（Compute Architecture for Neural Networks）版本，需与宿主机驱动版本匹配；不匹配会导致 NPU 不可用。
- **`{torch_npu}`**：PyTorch 适配昇腾 NPU 的专用包版本，示例 `2.6.0.rc1`；注意实际拉取示例里为 `2.6.0.post5`，存在小幅修订差异。
- **`{os}`**：基础操作系统镜像，支持 Ubuntu 22.04 与 openEuler 24.03 两种发行版。
- **`{python}`**：Python 解释器版本，示例 `py3.12`。
- 完整 Tag 还含固定段 `910b`（Ascend 910B 芯片代号）与 `aarch64`（CPU 架构），合计 6 个语义字段。

### 表 2：下一步目标导航表

| 目标 | 文档 |
| -- | -- |
| 图像 resize/crop 可视化样例 | [样例和指导 > 图片处理](../04_user_guide/user_guide.md#图片处理) |
| 视频帧解码 | [样例和指导 > 视频处理](../04_user_guide/user_guide.md#视频处理) |
| 音频加载 | [样例和指导 > 音频处理](../04_user_guide/user_guide.md#音频处理) |
| Qwen2VL / InternVL2 预处理加速 | [Adapter](../05_api/adapter.md) |
| vLLM 推理框架集成 | [patcher](../05_api/patcher.md) |
| API 完整参考 | [功能函数参考](../05_api/function_reference.md) |

**逐行解读：**

- 前三行引导用户进入按模态分类的样例文档（图片/视频/音频），覆盖 SDK 的三大预处理加速能力。
- 第四、五行指向模型/框架集成层：Adapter 用于多模态大模型预处理对接，patcher 用于 vLLM 推理框架的集成。
- 第六行指向 API 全量参考，是深入查阅函数签名的入口。

### 表 3：常见问题速查表

| 现象 | 处理方式 |
| -- | -- |
| 文件权限报错 | 确保图片权限不高于 640：`chmod 640 "$TEST_IMAGE"` |
| 容器内找不到测试图片 | 确认使用的镜像版本已内置 `/data/test.jpg`，且 `TEST_IMAGE` 使用容器内路径 `/data/test.jpg` |
| 容器无法访问 NPU | 检查 NPU 驱动挂载与 `--device /dev/davinci*` 设备号 |
| 导入 `mm` 失败 | 确认已执行 `source ${MULTIMODAL_SDK_HOME}/script/set_env.sh` |
| 更多问题 | [FAQ](../06_references/faq.md)、[附录](../06_references/appendix.md) |

**逐行解读：**

- **权限报错**：图片权限过高会触发读权限问题，统一收敛到 640（属主读写、组读、其他无权限）。
- **找不到测试图片**：强调路径必须是 `/data/test.jpg`（容器内路径），而非宿主机路径——这是容器化场景的常见误区。
- **NPU 不可用**：指向设备透传配置问题，需检查 `--device` 参数中的 `davinci*` 编号是否与宿主机实际 NPU 编号对应。
- **导入 `mm` 失败**：Python 包 `mm` 依赖环境脚本注入路径，未 source 则找不到 SDK 安装路径。
- **更多问题**：兜底指向 FAQ 与附录，覆盖未在速查表内的问题。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档处于 SDK 文档体系的"入门引导层"，与以下模块/文档形成上下游关系：

1. **[../03_installation_guide/installation_guide.md](../03_installation_guide/installation_guide.md)**：本文档显式说明"如需在宿主机原生安装，请参见安装部署"，即 Docker 路径之外的替代安装方式。
2. **[../01_introduction/01_introduction.md#支持的硬件和操作系统](../01_introduction/01_introduction.md#支持的硬件和操作系统)**：前置条件中"Atlas 800I A2 推理服务器"的来源依据，用于确认硬件/OS 兼容性。
3. **[../04_user_guide/user_guide.md#图片处理](../04_user_guide/user_guide.md#图片处理)**：本文档的 resize 验证示例是该章节的最小化前置演示，章节内提供完整的 resize/crop 可视化样例。
4. **[../04_user_guide/user_guide.md#视频处理](../04_user_guide/user_guide.md#视频处理)**：与图片处理并列的另一大模态能力（视频帧解码）。
5. **[../04_user_guide/user_guide.md#音频处理](../04_user_guide/user_guide.md#音频处理)**：与图片、视频并列的音频加载能力。
6. **[../05_api/adapter.md](../05_api/adapter.md)**：Qwen2VL、InternVL2 等多模态大模型的预处理加速适配层，属于"跑通基础 SDK 之后"的下一目标。
7. **[../05_api/patcher.md](../05_api/patcher.md)**：与 vLLM 推理框架的集成 patch 工具，属于框架适配层。
8. **[../05_api/function_reference.md](../05_api/function_reference.md)**：API 全量参考，本文档中使用的 `Image.open`、`Image.resize`、`Interpolation`、`DeviceMode` 等符号的完整签名在此查阅。
9. **[../06_references/faq.md](../06_references/faq.md)** 与 **[../06_references/appendix.md](../06_references/appendix.md)**：问题兜底文档，本文末尾 FAQ 表的"更多问题"链路指向这两份。

整体来看，本文档是连接"硬件/驱动环境" → "Docker 容器化基础" → "Python SDK 验证" → "按模态/框架的深度使用"的枢纽章节。

---

## 【使用方法】

### 1. 拉取镜像

```bash
TAG={version}-{cann}-{torch_npu}-910b-{os}-{python}-aarch64
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:${TAG}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:${TAG} \
    multimodalsdk:${TAG}
```

**原文示例（26.1.0 + Ubuntu 22.04 + Python 3.12）：**

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64 \
    multimodalsdk:26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64
```

### 2. 启动容器

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
    -itd multimodalsdk:26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64 bash

docker ps -a | grep multimodal_container
docker exec -it multimodal_container bash
```

> **注意**：`--device /dev/davinci0` 中的设备编号需按宿主机实际 NPU 编号调整（如 `davinci1`）。

### 3. 加载环境

```bash
export MULTIMODAL_SDK_HOME="/usr/local/multimodal"
source ${MULTIMODAL_SDK_HOME}/script/set_env.sh
```

### 4. 运行验证脚本

若镜像内未预置 `/data/test.jpg`，可下载：

```bash
mkdir -p /data
wget --tries=3 --timeout=30 --waitretry=5 -O /data/test.jpg https://raw.gitcode.com/Ascend/MultimodalSDK/blobs/f1f648b7a8b8a67c7509b3425a89f743bbf59563/dog_1920_1080.jpg
```

执行验证脚本：

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

期望输出：`resize output shape: (500, 500, 3)`

### 5. 清理环境

```bash
exit
docker stop multimodal_container
docker rm multimodal_container
```

### 6. 关键配置项说明（原文涉及）

- **环境变量 `MULTIMODAL_SDK_HOME`**：默认 `/usr/local/multimodal`，用于定位 SDK 安装根目录。
- **`Image.open(path, device)`**：第二参数为解码设备字符串，**当前仅支持 `"cpu"`**。
- **`DeviceMode.CPU`**：resize 等算子接口的运行模式枚举值。
- **`Interpolation.BICUBIC`**：resize 插值算法枚举值。
- **`chmod 640`**：测试图片权限上限。
- **`npu-smi info`**：宿主机 NPU 驱动状态预检命令。
