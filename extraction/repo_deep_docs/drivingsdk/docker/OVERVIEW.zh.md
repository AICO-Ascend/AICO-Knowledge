# 在 DrivingSDK 镜像上叠加用户软件

> 仓 `drivingsdk` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/drivingsdk/docker/OVERVIEW.zh.md

# 昇腾 DrivingSDK Docker 镜像 文档深度解读

---

## 【定位】

本文档是 DrivingSDK（华为昇腾面向自动驾驶模型的 NPU 加速库）的 **Docker 镜像总览**，系统说明镜像的 Tag 命名规范、支持的芯片/OS/版本组合、容器启动与本地构建方式，作为用户快速获取并部署自动驾驶模型运行环境的入口指南。

---

## 【技术要点】

1. **依赖栈定位**：DrivingSDK 镜像基于「昇腾 CANN + PyTorch + TorchNPU」三层栈构建，向上为自动驾驶模型提供 NPU 加速算子与运行时，向下通过宿主机驱动调用昇腾 NPU 设备。
2. **Tag 命名六段式格式**：`<drivingsdk版本>-<cann版本>-torch_npu<TorchNPU版本>-<芯片系列>-<操作系统>-py<python版本>`，将版本、芯片、OS、Python 全部编码进镜像 Tag；历史 `8.5.1-*` 与 `9.0.0-*` 以 CANN 版本起头，`devel` 为源码构建专用标记。
3. **硬件/OS 覆盖范围**：架构 `x86_64` 与 `aarch64`；OS 为 `ubuntu22.04` 与 `openeuler24.03`；芯片系列覆盖 `910b`、`a3`、`950`。
4. **支持的版本组合**：DrivingSDK 版本 `26.1.0 / 26.0.0 / 7.3.0`；CANN 版本 `9.1.0 / 9.0.0 / 8.5.1`；TorchNPU 版本 `2.1.0.post17` 与 `2.7.1.post6`；Python `py3.8 / py3.10`。
5. **设备透传与目录挂载**：运行容器时需将 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 透传至容器，并挂载 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend`；驱动由宿主机提供，Dockerfile 不安装驱动。
6. **构建与二次开发路径**：支持 `docker buildx` 本地构建（路径以 `docker/<Tag>/Dockerfile` 为准），并可在基础镜像上 `FROM` 叠加用户软件；`devel` 镜像从仓库源码构建 DrivingSDK。

---

## 【关键机制与数据】

- **镜像内容组成（原文：镜像内容列）**：每个 Tag 镜像包含「PyTorch 对应版本 + TorchNPU 对应版本 + DrivingSDK + 模型环境」四类内容。例如 `26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10` 内容为「PyTorch 2.7.1、TorchNPU 2.7.1.post6、DrivingSDK、模型环境」。
- **驱动与容器边界（原文：前置要求）**：NPU 驱动由宿主机承担并与 Dockerfile 中 CANN 版本兼容；镜像内部不安装驱动，容器运行时通过设备透传复用宿主驱动。
- **历史 Tag 兼容说明（原文：Tag 规范段）**：`8.5.1-*` 与 `9.0.0-*` 历史 Tag 的命名规则为「以 CANN 版本开头」，与现行「以 DrivingSDK 版本开头」的命名规则不同，使用历史镜像时需注意区分。
- **`devel` 镜像机制（原文：如何二次开发段）**：`devel` 镜像通过 `docker buildx build -t drivingsdk:devel -f docker/devel/Dockerfile .` 从仓库源码构建，区别于发布版直接使用预编译产物。
- **版本矩阵规模（原文：26.1.0 表）**：最新版本 `26.1.0` 共发布 10 个 Tag，矩阵覆盖 2 个 TorchNPU 版本 × 3 个芯片系列 × 2 个 OS 的笛卡尔积（去掉 910b 不支持 `2.7.1.post6` 与某些组合后剩余 10 项，其中 910b 仅与 `torch_npu2.1.0.post17` 与 `torch_npu2.7.1.post6` 各自搭配 2 个 OS 共 4 项，`950` 仅与 `torch_npu2.7.1.post6` 搭配 2 个 OS 共 2 项，`a3` 与两类 TorchNPU × 2 个 OS 共 4 项）。
- **原文未提供**：性能数据、训练吞吐、推理时延、显存占用等基准数据本文均未涉及。

---

## 【表格解读】

### 表格 1：Tag 规范字段说明

| 字段 | 示例值 | 说明 |
| --- | --- | --- |
| `drivingsdk版本` | `26.1.0`、`26.0.0`、`7.3.0` | DrivingSDK 版本号 |
| `cann版本` | `9.1.0`、`9.0.0`、`8.5.1` | CANN 版本号 |
| `TorchNPU版本` | `2.1.0.post17`、`2.7.1.post6` | TorchNPU 版本号 |
| `芯片系列` | `950`、`a3`、`910b` | 目标昇腾芯片系列 |
| `操作系统` | `ubuntu22.04`、`openeuler24.03` | 基础操作系统 |
| `python版本` | `py3.8`、`py3.10` | Python 版本 |
| `devel` | `devel` | 开发态镜像所具有的特殊标记 |

**逐行解读**：

- **`drivingsdk版本`**：DrivingSDK 自身的语义化版本号，是 Tag 的第一段，决定上层 API 与算子能力。
- **`cann版本`**：底层 CANN（昇腾计算架构）版本，决定算子库与运行时兼容性，需与宿主机驱动配套。
- **`TorchNPU版本`**：PyTorch 适配昇腾 NPU 的桥接包版本，格式中以 `torch_npu` 前缀拼接。
- **`芯片系列`**：目标硬件平台，`910b` 为训练/推理常用款，`a3` 与 `950` 为更新代次的昇腾芯片。
- **`操作系统`**：基础镜像 OS，与宿主机或用户偏好相关。
- **`python版本`**：容器内默认 Python 解释器版本，`py3.8` 通常与 `torch_npu2.1.0.post17` 配套，`py3.10` 与 `torch_npu2.7.1.post6` 配套。
- **`devel`**：特殊后缀，标识该镜像为源码构建的开发态镜像，与发布版 Tag 在语义上不同。

### 表格 2：DrivingSDK 26.1.0 镜像 Tag 清单

| Tag | Dockerfile | 镜像内容 |
| --- | --- | --- |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-910b-openeuler24.03-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-910b-openeuler24.03-py3.8/Dockerfile) | PyTorch 2.1.0、TorchNPU 2.1.0.post17、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-910b-ubuntu22.04-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-910b-ubuntu22.04-py3.8/Dockerfile) | PyTorch 2.1.0、TorchNPU 2.1.0.post17、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-a3-openeuler24.03-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-a3-openeuler24.03-py3.8/Dockerfile) | PyTorch 2.1.0、TorchNPU 2.1.0.post17、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.1.0.post17-a3-ubuntu22.04-py3.8` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.1.0.post17-a3-ubuntu22.04-py3.8/Dockerfile) | PyTorch 2.1.0、TorchNPU 2.1.0.post17、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-910b-openeuler24.03-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-910b-openeuler24.03-py3.10/Dockerfile) | PyTorch 2.7.1、TorchNPU 2.7.1.post6、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10/Dockerfile) | PyTorch 2.7.1、TorchNPU 2.7.1.post6、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-950-openeuler24.03-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-950-openeuler24.03-py3.10/Dockerfile) | PyTorch 2.7.1、TorchNPU 2.7.1.post6、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-950-ubuntu22.04-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-950-ubuntu22.04-py3.10/Dockerfile) | PyTorch 2.7.1、TorchNPU 2.7.1.post6、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-a3-openeuler24.03-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-a3-openeuler24.03-py3.10/Dockerfile) | PyTorch 2.7.1、TorchNPU 2.7.1.post6、DrivingSDK、模型环境 |
| `26.1.0-9.1.0-torch_npu2.7.1.post6-a3-ubuntu22.04-py3.10` | [Dockerfile](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/26.1.0-9.1.0-torch_npu2.7.1.post6-a3-ubuntu22.04-py3.10/Dockerfile) | PyTorch 2.7.1、TorchNPU 2.7.1.post6、DrivingSDK、模型环境 |

**逐行解读**：

- **行 1–2（910b + torch_npu2.1.0.post17）**：910b 芯片 × 旧版 TorchNPU 组合，分别面向 openEuler 24.03 与 Ubuntu 22.04，Python 锁定 py3.8。
- **行 3–4（a3 + torch_npu2.1.0.post17）**：a3 芯片 × 旧版 TorchNPU 组合，覆盖两种 OS。
- **行 5–6（910b + torch_npu2.7.1.post6）**：910b 芯片 × 新版 TorchNPU 组合，升级至 py3.10，体现 PyTorch 2.7.1 的能力。
- **行 7–8（950 + torch_npu2.7.1.post6）**：新增 950 芯片支持，仅在新版 TorchNPU + py3.10 组合中出现。
- **行 9–10（a3 + torch_npu2.7.1.post6）**：a3 芯片同时支持两代 TorchNPU，新版组合使用 py3.10。

整体规律：**TorchNPU 2.1.0.post17 ⇄ py3.8**，**TorchNPU 2.7.1.post6 ⇄ py3.10**；`950` 芯片仅在新版组合中提供；910b 与 a3 跨两代 TorchNPU 兼容。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上下游仓库**：镜像由 [DrivingSDK 团队](https://gitcode.com/Ascend/DrivingSDK) 维护，文档内所有 Tag 与 Dockerfile 路径均指向 `Ascend/DrivingSDK` 仓库根目录的 `docker/` 子目录。
- **历史版本与多版本索引**：本文仅详细列出 `26.1.0` 最新版本镜像；`26.0.0` 与 `7.3.0` 仅在「支持的 DrivingSDK 版本」中点名，历史 Tag 完整清单需跳转至 [Supported Tags](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/supported_tags.md)。
- **英文文档对位**：文档头部明确指向英文版 [English OVERVIEW.md](https://gitcode.com/Ascend/DrivingSDK/blob/master/docker/OVERVIEW.md)，与本中文版为同一文档双语言对照。
- **依赖组件授权链**：许可证段落指出镜像内预装的 CANN、PyTorch、TorchNPU、Python 及系统软件包各有自身许可证，需与 DrivingSDK 仓库许可证共同遵循。
- **与 `devel` 镜像的耦合**：`devel` 通过 `docker/devel/Dockerfile` 从源码构建，与发布版的 `docker/<Tag>/Dockerfile` 平级，是开发态入口。
- **内部链接**：原文未提供除上述已列之外的额外内部链接。

---

## 【使用方法】

### 1. 安装前置驱动（可选，但运行容器必需）

在宿主机安装与所选 Dockerfile 中 CANN 版本兼容的昇腾 NPU 驱动（原文：驱动由宿主机提供，Dockerfile 不负责安装驱动）。

### 2. 运行 DrivingSDK 容器

```bash
docker run \
    --name drivingsdk_container \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend:/usr/local/Ascend \
    -it drivingsdk:26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10 bash
```

设备与挂载含义：
- `--device /dev/davinci0`：透传 NPU 计算设备 0。
- `--device /dev/davinci_manager`：透传设备管理器。
- `--device /dev/devmm_svm`：透传设备内存管理接口。
- `--device /dev/hisi_hdc`：透传主机-设备通信通道。
- `-v /usr/local/dcmi:/usr/local/dcmi`：挂载 DCMI（设备管理接口）。
- `-v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi`：挂载 NPU 状态查询工具。
- `-v /usr/local/Ascend:/usr/local/Ascend`：挂载昇腾运行时目录。

### 3. 本地构建镜像

```bash
docker buildx build \
    -t drivingsdk:26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10 \
    -f docker/26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10/Dockerfile .
```

### 4. 二次开发（在基础镜像上叠加用户软件）

```dockerfile
FROM drivingsdk:26.1.0-9.1.0-torch_npu2.7.1.post6-910b-ubuntu22.04-py3.10

RUN apt-get update && apt-get install -y <package>
```

### 5. 源码构建（`devel` 镜像）

```bash
docker buildx build -t drivingsdk:devel -f docker/devel/Dockerfile .
```

### 6. 镜像选择建议（依据原文矩阵）

- **910b 训练/推理**：可选 py3.8（TorchNPU 2.1.0）或 py3.10（TorchNPU 2.7.1）。
- **a3 新平台**：同样支持两代 TorchNPU。
- **950 新平台**：仅提供 py3.10 + TorchNPU 2.7.1 组合。
- **OS 选择**：Ubuntu 22.04 与 openEuler 24.03 二选一，按宿主机/集群环境匹配。

### 7. 合规与免责

镜像使用需遵循仓库许可证以及镜像内预装组件各自许可证；该镜像为社区版本，不对商业负责，仅作为生产实践参考（原文：免责声明）。
