# MultimodalSDK

> 仓 `multimodalsdk` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/multimodalsdk/docker/OVERVIEW.zh.md

# MultimodalSDK Docker 镜像文档深度解读

## 【定位】

本篇文档是 **MultimodalSDK**（多模态大模型推理预处理加速库）在 **昇腾（Ascend）910b 芯片 + 容器化场景**下的镜像部署与使用指南，定位为「镜像 Tag 规范说明 + 本地构建 + 容器运行 + 二次开发」的快速参考手册，配套两个具体 Dockerfile（openEuler / Ubuntu）共同构成完整的容器交付物入口。

---

## 【技术要点】

1. **SDK 定位**：提供昇腾设备亲和的高性能接口，加速多模态大模型的**推理预处理**流程；当前预处理接口**在 CPU 上执行**（`DeviceMode.CPU`），需与 **CANN/NPU 推理框架配合部署**。
2. **功能范围**：包含 **图像/视频加载与解码**，以及 **resize、crop** 等常用预处理操作；同时支持**多种开源数据结构 ↔ 加速库数据结构**的相互转换，便于移植与快速接入。
3. **Tag 命名格式**（共 7 段）原文给出：
   `<MultimodalSDK版本>-<cann版本>-<torch-npu版本>-<芯片系列>-<操作系统>-<python版本>-aarch64`
4. **当前支持的镜像 Tag**（原文两行）锁定组合：`MultimodalSDK 26.1.0 + CANN 9.1.0 + torch-npu 2.6.0.post5 + 910b + ubuntu22.04/openeuler24.03 + py3.12 + aarch64`。
5. **本地构建命令**：
   `docker build -t {your_repo}/multimodal:latest -f Dockerfile.<芯片系列>.<操作系统> .`
6. **容器运行需挂载的设备与目录**：4 个 device（`/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`）+ 4 个 volume（dcmi、npu-smi、driver lib64、driver version.info、ascend_install.info）。
7. **二次开发基镜像**：以 `swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64` 为基础（原文只给出一个具体的 base image 示例，即 ubuntu 变体）。

---

## 【关键机制与数据】

- **运行模式**：原文明确「预处理接口当前在 CPU 上执行（`DeviceMode.CPU`）」——这意味着 SDK 的瓶颈/收益主要在数据准备阶段（解码、resize、crop、格式转换），而非矩阵运算；NPU 仅承担后续推理，因此镜像需要 CANN 而不是只需要纯 CPU 环境。
- **数据流（基于原文可推导）**：原始图像/视频 → CPU 端解码 + resize/crop + 数据结构转换 → 送入 CANN/NPU 推理框架（原文未给出具体内存拷贝路径与 tensor shape 描述，此处不做臆造）。
- **依赖约束**：原文要求「主机上必须安装与容器内 CANN 版本兼容的 NPU 驱动」，并指向 CANN 兼容性矩阵（https://www.hiascend.com/document）——这是容器与宿主机之间的版本对齐约束。
- **架构约束**：Tag 末尾固定 `aarch64`，意味着**仅支持 ARM64 架构**的 910b 服务器（原文未给出 x86/鲲鹏以外的架构说明）。
- 原文未提供任何性能数据（如 QPS、latency、加速比），故不展开。

---

## 【表格解读】

### 表 1：Tag 字段说明表（逐字还原）

| 字段         | 示例值                          | 说明             |
| ------------ | ------------------------------- | ---------------- |
| `MultimodalSDK版本`   | `26.1.0`              | MultimodalSDK 版本号      |
| `cann版本`   | `9.1.0`              | cann 版本号      |
| `torch-npu版本`   | `2.6.0.post5`              | torch-npu 版本号      |
| `芯片系列`   | `910b`          | 目标芯片系列 |
| `操作系统`   | `ubuntu22.04`、`openeuler24.03` | 基础操作系统     |
| `python版本` | `py3.12`    | Python 版本      |

**逐行解读**：
- `MultimodalSDK版本 = 26.1.0`：SDK 自身版本，与 Tag 第一段对应，是用户评估 API 兼容性的关键锚点。
- `cann版本 = 9.1.0`：容器内置的 CANN 工具链版本，必须与**宿主机 NPU 驱动版本**对齐（原文「前置要求」明确）。
- `torch-npu版本 = 2.6.0.post5`：PyTorch + 昇腾适配版本，决定上层能否直接以 `torch` API 调用 NPU。
- `芯片系列 = 910b`：当前唯一受支持的昇腾芯片系列；意味着镜像内的 CANN 算子库是按 910b 指令集编译的，不可移植到其他系列。
- `操作系统 = ubuntu22.04 / openeuler24.03`：基础 OS 二选一，对应文末给出的两个不同 Dockerfile。
- `python版本 = py3.12`：Python 解释器版本，决定能否使用较新语法特性及第三方包兼容性。

注意：原表头只有 6 个字段，但 Tag 格式公式中含 7 段（多了一个尾部的 `aarch64` 架构字段，且**未在说明表中单列**，仅在 Tag 格式模板中显式出现）。

---

### 表 2：支持的 tags 及 Dockerfile（逐字还原）

| Tag                                | Dockerfile                                                   |
| ---------------------------------- | ------------------------------------------------------------ |
| `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-openeuler24.03-py3.12-aarch64`   | [Dockerfile.910b.openEuler](./Dockerfile.910b.openEuler) |
| `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64`    | [Dockerfile.910b.ubuntu](./Dockerfile.910b.ubuntu)      |

**逐行解读**：
- 第一行：基于 openEuler 24.03 的镜像，对应 `./Dockerfile.910b.openEuler`——面向国产化操作系统场景。
- 第二行：基于 Ubuntu 22.04 的镜像，对应 `./Dockerfile.910b.ubuntu`——面向主流 Linux 生态场景。
- 两行除了 OS 段外其余字段完全一致，体现「同一 SDK + 同一 CANN + 同一芯片，仅 OS 层差异」的镜像矩阵设计。

---

## 【公式解读】

原文无公式（仅包含一段 Tag 命名的伪模板字符串，并非数学/算法公式）。

**Tag 格式伪模板（原文逐字保留）**：

```
<MultimodalSDK版本>-<cann版本>-<torch-npu版本>-<芯片系列>-<操作系统>-<python版本>-aarch64
```

各占位符含义（与表 1 一致）：
- `<MultimodalSDK版本>`：SDK 版本号，例 `26.1.0`
- `<cann版本>`：CANN 工具链版本，例 `9.1.0`
- `<torch-npu版本>`：PyTorch-NPU 适配版本，例 `2.6.0.post5`
- `<芯片系列>`：目标昇腾芯片，例 `910b`
- `<操作系统>`：基础 OS，例 `ubuntu22.04` 或 `openeuler24.03`
- `<python版本>`：Python 解释器，例 `py3.12`
- `aarch64`：**字面量而非占位符**，表明镜像仅发布 ARM64 架构。

---

## 【关联】

文档位于仓库 `docker/` 目录下，依赖/引用关系梳理：

- **同目录文档**：
  - `./OVERVIEW.md` —— 英文版同一文档（顶部语言切换链接）。
  - `./Dockerfile.910b.openEuler` —— openEuler 24.03 变体的构建脚本（表 2 第 1 行）。
  - `./Dockerfile.910b.ubuntu` —— Ubuntu 22.04 变体的构建脚本（表 2 第 2 行）。
- **上游软件栈**：
  - **CANN**（Compute Architecture for Neural Networks，昇腾计算架构）—— 容器内预装，提供 NPU 算子与运行时。
  - **Mind 系列软件** —— 与 CANN 同源，许可证与镜像一并继承（见文末「许可证」）。
  - **torch-npu** —— PyTorch 的昇腾适配层，使上层模型可直接以 `torch` 风格调用 NPU。
- **宿主机依赖**：
  - **NPU 驱动** —— 必须与容器内 CANN 版本兼容，参见外部链接 [CANN 兼容性矩阵](https://www.hiascend.com/document)。
- **代码与示例**：
  - 仓库主入口：[MultimodalSDK 代码](https://gitcode.com/Ascend/MultimodalSDK)、[文档入口](https://gitcode.com/Ascend/MultimodalSDK/blob/master/README.md)、[示例代码](https://gitcode.com/Ascend/MultimodalSDK/blob/master/docs/zh/02_quickstart/quickstart.md)。
  - 问题反馈：[issue 反馈](https://gitcode.com/Ascend/MultimodalSDK/issues)。
  - 社区入口：[hiascend.com](https://www.hiascend.com/)。
- **镜像注册表**（二次开发基镜像）：
  - `swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:...` —— 华为云 SWR 西南-广州区域，ascendhub 命名空间下的 multimodal SDK 仓库。

---

## 【使用方法】

### 1. 构建镜像（原文逐字保留）

```bash
docker build -t {your_repo}/multimodal:latest -f Dockerfile.<芯片系列>.<操作系统> .
```

- `<芯片系列>`：当前为 `910b`
- `<操作系统>`：当前为 `openeuler24.03` 或 `ubuntu22.04`
- 替换 `{your_repo}` 为用户自己的镜像仓库前缀。

### 2. 运行容器（原文逐字保留）

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

要点：
- `tag` 需替换为具体的 Tag（如 `26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64`）。
- 4 个 `--device` 把 NPU 字符设备透传到容器，否则容器内无法访问加速器。
- 4 个 `-v` 把宿主机的 dcmi、npu-smi 工具、driver 库与版本信息、ascend 安装信息挂入容器（这是 NPU 在容器内可被识别的关键）。

### 3. 进入已运行的容器（原文逐字保留）

```bash
docker exec -it multimodal_container bash
```

### 4. 二次开发——基于已发布镜像扩展（原文逐字保留）

```dockerfile
FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/multimodalsdk:26.1.0-cann9.1.0-torch_npu2.6.0.post5-910b-ubuntu22.04-py3.12-aarch64

RUN apt update -y && \
    ...

...
```

要点：以官方 ubuntu 变体为基础镜像，自行添加依赖与应用层。

### 5. 前置要求（原文逐字保留）

主机上**必须**安装与容器内 CANN 版本兼容的 NPU 驱动。版本对应关系参见 [CANN 兼容性矩阵](https://www.hiascend.com/document)。

### 6. 运行时配置项说明

原文未涉及具体环境变量、SDK 调用参数、batch size、线程数等运行时配置——这些信息在文档外部的「[MultimodalSDK 示例代码](https://gitcode.com/Ascend/MultimodalSDK/blob/master/docs/zh/02_quickstart/quickstart.md)」链接中（原文未展开）。
