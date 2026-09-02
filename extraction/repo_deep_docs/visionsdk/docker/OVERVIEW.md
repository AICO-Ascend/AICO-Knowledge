# VisionSDK

> 仓 `visionsdk` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/visionsdk/docker/OVERVIEW.md

# VisionSDK Docker OVERVIEW.md 深度解读

---

## 【定位】

本文档是 **VisionSDK**（面向图片和视频视觉分析的 SDK，提供视频与图像智能分析基础能力及编程框架）在 **Docker 容器化交付场景**下的入门说明，重点回答「如何构建镜像、如何运行容器、如何进入容器校验、以及 SDK 支持的硬件/OS/Python 组合版本」等问题，作为容器化部署与开发的快速上手指南。

---

## 【技术要点】

1. **两种开发范式**
   - **API 接口开发**：调用原生推理 API 与算子加速库，适用于"应用开发流程相对固定、希望直接复用算法加速能力"的用户。
   - **工作流编排开发**：采用模块化设计，将服务流程中的功能单元封装为独立 plugin（插件），通过编排插件链快速搭建服务，支持自定义插件开发。

2. **镜像 Tag 命名规范**（原文保留）
   ```
   <VisionSDK_version>-<chip_series>-<os>-<python_version>
   ```
   - `VisionSDK_version` 示例值：`26.1.0`
   - `chip_series` 示例值：`910`
   - `os` 示例值：`ubuntu22.04`、`openeuler24.03`
   - `python_version` 示例值：`py3.11`

3. **镜像构建命令**（原文保留）
   ```bash
   docker build -t {your_repo}/vision:latest -f Dockerfile.<chip_series>.<os> .
   ```

4. **容器运行命令**（原文保留，挂载多个设备与目录）
   ```bash
   docker run \
       --name vision_container \
       --device /dev/davinci1 \
       --device /dev/davinci_manager \
       --device /dev/devmm_svm \
       --device /dev/hisi_hdc \
       -v /usr/local/dcmi:/usr/local/dcmi \
       -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
       -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
       -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
       -v /etc/ascend_install.info:/etc/ascend_install.info \
       -it ascend/vision:tag bash
   ```

5. **容器内校验命令**（原文保留）
   ```bash
   docker exec -it vision_container bash
   pip show mindx
   ```
   - 判定标准：能够展示 `mindx` 包的详细信息即视为成功进入容器。

6. **基础镜像约定**（原文示例）
   ```bash
   FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/visionsdk:26.0.0-310p-ubuntu22.04-py3.11
   ```
   - 第三方开发者在扩展镜像时，可基于 `ascendhub` 提供的官方镜像进行 `apt` 等依赖安装。

---

## 【关键机制与数据】

| 维度 | 原文信息 |
|------|----------|
| SDK 定位 | 提供"basic intelligent analysis capabilities for videos and images as well as a programming framework"（视频图像智能分析能力 + 编程框架） |
| 驱动依赖 | **驱动与 CANN 版本需兼容**（"An NPU driver compatible with the container's CANN version must be installed on the host"），具体映射需查阅 [CANN Compatibility Matrix](https://www.hiascend.com/document) |
| 设备透传 | 容器需透传 NPU 相关设备节点：`/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` |
| 驱动目录挂载 | `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info` 全部需要从 host 透传到容器内 |
| 包名校验 | 容器内通过 `pip show mindx` 校验是否成功启动 SDK |
| 官方样本路径 | 样本代码路径：[VisionSDK Samples](https://gitcode.com/Ascend/VisionSDK/blob/master/docs/zh/03.quick_start.md) |
| 许可证 | 遵循 [CANN/MindSeries 许可证](https://github.com/Ascend/cann-container-image/blob/main/LICENSE)；容器内预装的 Python 与系统库可能受各自许可约束 |

> 原文未给出性能数据（如吞吐、时延、FPS 等），本文不臆造。

---

## 【表格解读】

### 表格 1：Tag Naming Convention（Tag 命名约定）

| Field（原文）          | Example Values（原文）              | Description（原文）          |
| ---------------------- | ----------------------------------- | ---------------------------- |
| `VisionSDK_version`    | `26.1.0`                            | VisionSDK version            |
| `chip_series`          | `910`                              | Target Atlas chip family    |
| `os`                   | `ubuntu22.04`, `openeuler24.03`    | Base operating system       |
| `python_version`       | `py3.11`                           | Python version              |

**逐行解读**：

- **`VisionSDK_version`**：版本号字段，决定 SDK 自身的特性集；样例值 `26.1.0` 即目前（按原文）的发布版本。
- **`chip_series`**：目标 Atlas 芯片系列；样例值 `910` 代表一类 Ascend NPU 芯片族（如 Atlas 推理产品系列）。该字段决定了镜像底层驱动/固件的兼容性。
- **`os`**：基础操作系统；支持 Ubuntu 22.04 与 openEuler 24.03 两种发行版，是 Dockerfile 的 base image 选择依据。
- **`python_version`**：Python 版本；目前为 `py3.11`，与 mindx 等 Python 包绑定。

---

### 表格 2：Tags and Dockerfile（Tag 与 Dockerfile 对应关系）

| Tag（原文）                          | Dockerfile（原文链接）                                                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| `26.1.0-310p-openeuler24.03-py3.11`  | [Dockerfile](https://gitcode.com/Ascend/VisionSDK/blob/master/docker/Dockerfile.310p.openEuler) |
| `26.1.0-310p-ubuntu22.04-py3.11`     | [Dockerfile](https://gitcode.com/Ascend/VisionSDK/blob/master/docker/Dockerfile.310p.ubuntu)       |
| `26.1.0-910b-openeuler24.03-py3.11`  | [Dockerfile](https://gitcode.com/Ascend/VisionSDK/blob/master/docker/Dockerfile.910b.openEuler) |
| `26.1.0-910b-ubuntu22.04-py3.11`     | [Dockerfile](https://gitcode.com/Ascend/VisionSDK/blob/master/docker/Dockerfile.910b.ubuntu)       |

**逐行解读**：

- **`26.1.0-310p-openeuler24.03-py3.11`**：面向 **Atlas 310P** 芯片 + **openEuler 24.03** 系统的镜像，对应 `docker/Dockerfile.310p.openEuler`。
- **`26.1.0-310p-ubuntu22.04-py3.11`**：面向 **Atlas 310P** 芯片 + **Ubuntu 22.04** 系统，对应 `docker/Dockerfile.310p.ubuntu`。
- **`26.1.0-910b-openeuler24.03-py3.11`**：面向 **Atlas 910B** 芯片 + **openEuler 24.03** 系统，对应 `docker/Dockerfile.910b.openEuler`。
- **`26.1.0-910b-ubuntu22.04-py3.11`**：面向 **Atlas 910B** 芯片 + **Ubuntu 22.04** 系统，对应 `docker/Dockerfile.910b.ubuntu`。
- 规律：横轴 = 芯片系列（310p / 910b），纵轴 = OS（openeuler / ubuntu），形成 2×2 矩阵，4 个 Tag 完整覆盖两类硬件 × 两类 OS 的组合。

---

### 表格 3：Supported Hardware（支持的硬件）

| Product Examples（原文）    | Architecture（原文） |
| --------------------------- | -------------------- |
| Atlas Inference Product Series | ARM64 / x86_64       |
| Atlas 800I A2                  | ARM64 / x86_64       |

**逐行解读**：

- **Atlas Inference Product Series（Atlas 推理产品系列）**：支持 ARM64 与 x86_64 两种主机架构。
- **Atlas 800I A2**：同样支持 ARM64 与 x86_64。
- 文档列举的两类硬件只是「Product Examples」，并非穷举，意味着只要属于 Atlas 推理产品族且符合文档对应 Dockerfile 的硬件条件即可。

---

## 【公式解读】

**原文无公式**。

（文档中出现的所有命令、Tag 模式均以 bash 代码块或表格形式给出，没有 LaTeX 或伪代码形式的数学/算法公式。）

---

## 【关联】

文档涉及的内部链接与外部关联如下：

| 关联资源 | 关系说明 |
|----------|----------|
| `./OVERVIEW.zh.md`（文末链接） | **中文版**同一文档，用于中文用户阅读。 |
| [VisionSDK Code](https://gitcode.com/Ascend/VisionSDK) | 主代码仓地址，是镜像和 Dockerfile 的来源。 |
| [VisionSDK Documentation](https://gitcode.com/Ascend/VisionSDK/blob/master/README.md) | 主仓 README，作为 SDK 总入口。 |
| [Issue Feedback](https://gitcode.com/Ascend/VisionSDK/issues) | 问题反馈通道。 |
| [Community](https://www.hiascend.com/) | 昇腾社区入口，提供更广泛的交流渠道。 |
| [CANN Compatibility Matrix](https://www.hiascend.com/document) | 驱动 ↔ CANN 版本映射关系表，是「Prerequisites」一节的关键外部依赖。 |
| [VisionSDK Samples](https://gitcode.com/Ascend/VisionSDK/blob/master/docs/zh/03.quick_start.md) | SDK 使用样例代码，是「VisionSDK Usage」一节的入口。 |
| [License](https://github.com/Ascend/cann-container-image/blob/main/LICENSE) | 容器镜像（含 CANN、MindSeries）所遵循的开源许可证。 |
| 基础镜像 `swr.cn-south-1.myhuaweicloud.com/ascendhub/visionsdk:26.0.0-310p-ubuntu22.04-py3.11` | 「Development」一节示范如何在官方镜像基础上自定义扩展。 |

**上下游关系梳理**：

- 上游：Ascend 官方在 SWR 镜像仓库提供 `ascendhub/visionsdk` 基础镜像；用户在主机侧需安装与容器内 CANN 版本匹配的 NPU 驱动。
- 下游：用户基于本文档的 `docker build` 命令生成自定义镜像，并通过 `docker run` 挂载设备与驱动目录后启动容器；进入容器后通过 `mindx` 包使用 SDK，参考样例代码进行开发。

---

## 【使用方法】

### 1. 前置条件（原文："Prerequisites (optional)"）

- **驱动安装**：在主机上安装与容器内 CANN 版本兼容的 NPU 驱动；版本对照表参考 [CANN Compatibility Matrix](https://www.hiascend.com/document)。

### 2. 构建镜像（原文："How to build"）

```bash
docker build -t {your_repo}/vision:latest -f Dockerfile.<chip_series>.<os> .
```
- 需要将 `<chip_series>` 替换为 `310p` / `910b`，`<os>` 替换为 `ubuntu` / `openEuler`（参见「Tags and Dockerfile」表格中的 4 个 Dockerfile）。

### 3. 运行容器（原文："Running VisionSDK Container"）

使用上方「技术要点」第 4 条原样命令运行，挂载 NPU 设备节点与驱动目录：
- 设备：`/dev/davinci1`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`
- 目录：`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info`

### 4. 校验 SDK（原文："Enter the Container and check the Vision SDK"）

```bash
docker exec -it vision_container bash
pip show mindx
```
- 判定：能展示 `mindx` 详细信息 → 容器内 SDK 可用。

### 5. 自定义扩展（原文："Development"）

```dockerfile
FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/visionsdk:26.0.0-310p-ubuntu22.04-py3.11

RUN apt update -y && \
    apt install gcc ...
...
```
- 说明开发可基于 `ascendhub` 提供的官方镜像，安装自定义工具链后形成自有业务镜像。

### 6. 样例代码（原文："VisionSDK Usage"）

- 通过 [VisionSDK Samples](https://gitcode.com/Ascend/VisionSDK/blob/master/docs/zh/03.quick_start.md) 获取示例并快速上手。

### 7. 许可证确认（原文："License"）

- 容器内含 CANN、MindSeries 等组件，其许可证见 [CANN Container Image LICENSE](https://github.com/Ascend/cann-container-image/blob/main/LICENSE)；预装 Python 与系统库可能受各自许可约束。

---

> 注：文档为总览/快速上手型 OVERVIEW，未涉及模型训练、推理性能调优、插件开发细节、网络配置等更深层内容；如需了解，需结合仓库内 `docs/` 目录及其他文档。
