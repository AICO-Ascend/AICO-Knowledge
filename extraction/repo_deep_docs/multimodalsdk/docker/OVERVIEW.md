# MultimodalSDK

> 仓 `multimodalsdk` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/multimodalsdk/docker/OVERVIEW.md

# MultimodalSDK Docker 镜像文档深度解读

---

## 【定位】

这篇文档是 `docker/OVERVIEW.md`,旨在为开发者提供 MultimodalSDK **容器镜像**的完整使用指南,涵盖镜像标签命名约定、镜像构建、容器运行、进入容器及二次开发等能力,使开发者能够在 Atlas NPU 环境下快速部署并使用 MultimodalSDK 的多模态预处理加速接口。

---

## 【技术要点】

1. **核心功能定位**:为多模态大模型推理流程中的预处理环节提供高性能 Ascend 亲和接口;预处理 API 当前运行在 CPU 模式 (`DeviceMode.CPU`),通常与 CANN/NPU 推理框架协同部署。

2. **支持的预处理操作**:覆盖图像与视频的加载、解码,以及 resize、crop 等典型处理步骤;支持开源数据结构与加速库数据结构之间的相互转换,便于应用与迁移。

3. **镜像标签命名规范**(原文 pattern):
   ```
   <multimodalsdk_version>-<vllm-ascend_version>-<torch-npu_version>-<chip_series>-<os>-<python_version>-aarch64
   ```
   字段说明表中以 `cann_version` 为准(`9.1.0`),但 pattern 占位符写的是 `<vllm-ascend_version>`——两者不一致,实际 tag 使用 `cann9.1.0`。

4. **当前已发布的两个镜像 Tag**:
   - `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-openeuler24.03-py3.12-aarch64`
   - `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64`

5. **构建命令**(原文):
   ```bash
   docker build -t {your_repo}/multimodal:latest -f Dockerfile.<chip_series>.<os> .
   ```

6. **运行容器所需的设备/目录挂载**(原文 docker run 命令):需挂载 4 个 NPU 相关设备 (`/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`)以及 5 个主机目录 (`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、驱动库、版本信息、安装信息)。

---

## 【关键机制与数据】

- **原文**:MultimodalSDK 通过提供"高性能 Ascend 亲和接口"来加速大模型推理的预处理工作流;预处理 API 当前运行在 CPU(`DeviceMode.CPU`),与 CANN/NPU 推理框架并行部署,不直接占用 NPU 算力。
- **原文**:数据流涵盖"图像/视频加载与解码 → resize/crop 等典型处理步骤 → 在开源数据结构与加速库数据结构之间转换",形成从原始数据到推理输入的预处理链路。
- **原文**:镜像与底层驱动的耦合——容器内 CANN 版本需要与宿主机已安装的 NPU 驱动兼容,文档明确指向 CANN Compatibility Matrix 查询对应关系。
- **原文**:镜像基线版本数据(无性能数据):`multimodalsdk 26.1.0`、`CANN 9.1.0`、`torch-npu 2.6.0.post5`、`Python 3.12`、芯片族 `910b`、OS `ubuntu22.04`/`openeuler24.03`、架构 `aarch64`。
- **原文**:文档未提供性能基准数据(如吞吐、加速比、时延),仅描述功能覆盖范围。

---

## 【表格解读】

### 表格 1: Tag 字段说明

| Field | Example Values | Description |
| --- | --- | --- |
| `multimodalsdk_version` | `26.1.0` | MultimodalSDK version |
| `cann_version` | `9.1.0` | cann version |
| `torch-npu_version` | `2.6.0.post5` | torch-npu version |
| `chip_series` | `910b` | Target Atlas chip family |
| `os` | `ubuntu22.04`, `openeuler24.03` | Base operating system |
| `python_version` | `py3.12` | Python version |

**逐行解读**:
- `multimodalsdk_version` —— SDK 自身版本号,示例 `26.1.0`,决定容器内预装的 MultimodalSDK 能力。
- `cann_version` —— 随镜像发布的 CANN 版本,示例 `9.1.0`;此字段决定了容器对算子、ACL 接口的支持集合,且必须与宿主机 NPU 驱动兼容。
- `torch-npu_version` —— PyTorch NPU 适配版本,示例 `2.6.0.post5`,影响上层 Python 模型代码的可用 API。
- `chip_series` —— 目标 Atlas 芯片族,当前示例为 `910b`,决定底层指令集与运行时。
- `os` —— 基础操作系统,可选 `ubuntu22.04` 或 `openeuler24.03`,影响系统库依赖。
- `python_version` —— Python 解释器版本,示例 `py3.12`,对应 Python 3.12。

> **注意**:原文档的 pattern 表达式中占位符写的是 `<vllm-ascend_version>`,而此处字段表使用 `cann_version`,实际 tag 字符串中也以 `cann9.1.0` 出现——pattern 占位符命名疑似错误,实际应理解为 CANN 版本。

### 表格 2: Tags 与 Dockerfile 对照

| Tag | Dockerfile |
| --- | --- |
| `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-openeuler24.03-py3.12-aarch64` | [Dockerfile.910b.openEuler](./Dockerfile.910b.openEuler) |
| `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64` | [Dockerfile.910b.ubuntu](./Dockerfile.910b.ubuntu) |

**逐行解读**:
- 第一行:openEuler 24.03 系统上的 Atlas 910b 镜像,栈版本固定为 SDK 26.1.0 / CANN 9.1.0 / torch-npu 2.6.0.post5 / Python 3.12,对应 `./Dockerfile.910b.openEuler`。
- 第二行:Ubuntu 22.04 系统上的 Atlas 910b 镜像,栈版本与第一行完全一致,仅更换 OS,对应 `./Dockerfile.910b.ubuntu`。

---

## 【公式解读】

原文无公式。

(文档仅含 docker build/run/exec 命令与镜像 tag pattern 表达式,pattern 已在「技术要点」中以字符串形式逐字保留;不涉及数学公式或伪代码算法。)

---

## 【关联】

根据文档末的内部链接列表,可梳理出以下关联关系:

1. **本地化版本关联** —— `./OVERVIEW.zh.md` 为本文档的中文翻译版,内容上与本 `OVERVIEW.md` 对应,适用于中文用户。
2. **openEuler 镜像构建关联** —— `./Dockerfile.910b.openEuler` 对应 tag `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-openeuler24.03-py3.12-aarch64`,是 openEuler 24.03 系统上 Atlas 910b 环境的实际构建脚本,与本文档的镜像构建/运行说明直接配套。
3. **Ubuntu 镜像构建关联** —— `./Dockerfile.910b.ubuntu` 对应 tag `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64`,是 Ubuntu 22.04 系统上 Atlas 910b 环境的实际构建脚本,与本文档的镜像构建/运行说明直接配套。
4. **与上游框架的部署关系** —— 文档明确指出 MultimodalSDK 预处理 API 与 CANN/NPU 推理框架"协同部署",指向 [CANN Compatibility Matrix](https://www.hiascend.com/document) 作为上游驱动的兼容依据,属于部署依赖链。
5. **示例代码关联** —— MultimodalSDK Samples(指向 gitcode 仓库 `docs/zh/02_quickstart/quickstart.md`)提供容器内 SDK 调用样例,镜像构建完成后通过样例验证能力。
6. **问题反馈与社区渠道** —— Issue Feedback、MultimodalSDK Code、Documentation、Community 四个 Quick Reference 链接构成文档的外部支撑链路,但不属于仓库内的代码或文件模块。

---

## 【使用方法】

### 1. 镜像构建(原文有)

```bash
docker build -t {your_repo}/multimodal:latest -f Dockerfile.<chip_series>.<os> .
```
其中 `<chip_series>` 当前为 `910b`,`<os>` 当前为 `openeuler24.03` 或 `ubuntu22.04`,与本仓库两个 Dockerfile 一一对应。

### 2. 容器运行(原文有)

```bash
docker run \
    --name multimodal_container \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -it ascend/multimodal:tag bash
```
要点:必须挂载 `davinci0`、`davinci_manager`、`devmm_svm`、`hisi_hdc` 4 个 NPU 设备,以及驱动、dcmi、npu-smi、版本与安装信息 5 个主机路径;镜像 tag 需替换为前述具体 tag 字符串。

### 3. 进入容器(原文有)

```bash
docker exec -it multimodal_container bash
```

### 4. 基于镜像做扩展构建(原文有 Development 示例片段)

```bash
FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64
RUN apt update -y && \
    ...
...
```
以官方 Ubuntu 22.04 镜像为基线,通过标准 Dockerfile `RUN` 指令叠加开发者自有依赖。

### 5. 前置条件(原文有 Prerequisites)

需要在宿主机安装与容器 CANN 版本兼容的 NPU 驱动;具体对应关系通过 [CANN Compatibility Matrix](https://www.hiascend.com/document) 查询。该项在原文中标记为 "(optional)",但实际是 NPU 场景下容器正常运行所必需。
