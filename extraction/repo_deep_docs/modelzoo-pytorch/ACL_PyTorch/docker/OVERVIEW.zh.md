# 镜像概述：昇腾 torch-onnx-inference 运行环境

> 仓 `modelzoo-pytorch` · 路径 `ACL_PyTorch/docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/ACL_PyTorch/docker/OVERVIEW.zh.md

# 一体化深度解读：torch-onnx-inference 镜像概述文档

---

## 【定位】

这篇文档是 ModelZoo-PyTorch 代码仓中 **torch-onnx-inference 容器镜像的概述（OVERVIEW）**，用于告知用户该镜像的能力边界、所支持的硬件 / 操作系统 / 软件栈组合、提供哪些 Tag 与对应 Dockerfile 路径、以及如何在昇腾 NPU 宿主机上拉起容器并完成端到端推理流程的快速验证。

---

## 【技术要点】

1. **目标硬件锁定为两款昇腾 NPU**：`Atlas 300I DUO` 与 `Atlas 800I A2`，算力架构与驱动配套需匹配昇腾原生栈。
2. **基础操作系统支持两种 AArch64 发行版**：`Ubuntu 22.04 LTS (AArch64)` 与 `openEuler 24.03 LTS (AArch64)`，并以此正交组合出 4 个镜像 Tag。
3. **CANN 版本固定为 `8.3.RC1`**，配套 `PyTorch 2.1.0` + `Python 3.11`，由 `Miniconda` 提供环境隔离；预装 `torch_npu`、`MindIE-SD`、`ais_bench`、`MSIT` 与 `onnxslim`，构成"框架 + 加速库 + 图优化 + 基准测试"全栈。
4. **驱动兼容底线**：宿主机驱动需 `不低于 24.1.RC3`，以保证向后兼容算子的正常编译与执行。
5. **容器运行设备透传**：必须挂载 `/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`、`/dev/davinci0`（均 rwm）以及只读的 `/usr/local/Ascend/driver`、`/usr/local/Ascend/firmware`、`/usr/local/sbin`，否则 NPU 无法被容器内部识别。
6. **容器入口自动化**：登录后自动切入 Conda `base` 环境（`Python 3.11`），并可通过 `python3 -c "import torch; import torch_npu; print(torch.npu.is_available())"` 一次性验证 PyTorch + 昇腾软件栈的连通性。
7. **镜像命名约定**：`torch-onnx-inference:cann8.3.rc1_torch2.1.0-<硬件>-<OS>-py3.11-aarch64`，Tag 中同时编码了 CANN 版本、PyTorch 版本、目标硬件、操作系统与架构五维信息。

---

## 【关键机制与数据】

- **核心工作链路（原文："本环境核心用于承载和运行 ModelZoo 仓内经典和主流算法模型的端到端推理流程"）**：在容器内一站式完成 **PyTorch 模型 → torch_npu 昇腾原生加速 → MindIE-SD 调度 → onnxslim 图优化 → ais_bench / MSIT 基准测试** 的推理闭环，避免在不同基础镜像间反复安装。
- **场景定位（原文："专为端侧场景定制的高性能深度学习推理部署与全栈开发运行环境"）**：强调"端侧"——即 Atlas 300I DUO / Atlas 800I A2 这类推理卡形态，而非训练集群。
- **预装组件数据流**：Python 3.11 提供运行时 → PyTorch 2.1.0 提供模型装载与前向 API → torch_npu 提供 NPU 后端算子适配 → MindIE-SD 提供服务化推理能力 → ais_bench 与 MSIT 提供 perf 维度评测数据 → onnxslim 提供 ONNX 模型精简与图融合。
- **宿主机前置健康检查（原文命令）**：`npu-smi info`，用于确认 NPU 驱动、固件、设备状态在拉起容器前已就绪。
- **性能 / 吞吐数字**：原文**未给出**任何具体时延、吞吐或精度数值。
- **共享内存配置（原文命令参数）**：`--shm-size=1g`，避免 PyTorch DataLoader 多 worker 因 `/dev/shm` 不足而崩溃。

---

## 【表格解读】

原文表格——**镜像 Tag 与 Dockerfile 归档路径对照**——逐字还原：

| 完整镜像路径 (`<仓库地址>/<镜像名>:<Tag>`) | 基础操作系统 | 目标硬件 | Dockerfile 归档路径 |
| :--- | :--- | :--- | :--- |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-300I-DUO-ubuntu22.04-py3.11-aarch64` | Ubuntu 22.04 | Atlas 300I DUO | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.300IDUO.ubuntu` |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-300I-DUO-openeuler24.03-py3.11-aarch64` | openEuler 24.03 | Atlas 300I DUO | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.300IDUO.openeuler` |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-800I-A2-ubuntu22.04-py3.11-aarch64` | Ubuntu 22.04 | Atlas 800I A2 | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.800I_A2.ubuntu` |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-800I-A2-openeuler24.03-py3.11-aarch64` | openEuler 24.03 | Atlas 800I A2 | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.800I_A2.openeuler` |

**逐行解读**：

- **第 1 行（300I DUO + Ubuntu 22.04）**：面向使用 Atlas 300I DUO 卡、且 OS 偏好 Ubuntu 的用户；Dockerfile 文件名后缀 `.ubuntu` 区分 OS 类型，所有 Ubuntu 镜像的构建脚本集中于 `Dockerfile.300IDUO.ubuntu`。
- **第 2 行（300I DUO + openEuler 24.03）**：同硬件不同 OS 的发行版——openEuler 镜像由 `Dockerfile.300IDUO.openeuler` 构建，适合已部署 openEuler 政企 / 边缘节点的客户。
- **第 3 行（800I A2 + Ubuntu 22.04）**：升级到 Atlas 800I A2（更高算力档位）配 Ubuntu 的组合；Dockerfile 命名为 `Dockerfile.800I_A2.ubuntu`，表明其构建参数 / 设备挂载策略与 300I DUO 不同。
- **第 4 行（800I A2 + openEuler 24.03）**：与第 3 行同硬件、同 OS 系列但不同大版本（openEuler 24.03），由 `Dockerfile.800I_A2.openeuler` 构建；这是文档示例中"快速开始"部分默认使用的 Tag。

**共同规律**：Tag 严格遵循 `cann{ver}_torch{ver}-{hardware}-{os}-{pyver}-aarch64` 模式，Dockerfile 与之一一对应；所有 Dockerfile 归档于同一父目录 `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/`，说明该镜像族的"基线版本"由 CANN 8.3.RC1 + PyTorch 2.1.0 共同确定，再以硬件 × OS 双因子派生。

---

## 【公式解读】

**原文无公式。**（文档性质为镜像概述，未涉及算法推导或数学表达式）

---

## 【关联】

依据文末内部链接与上下文，本镜像文档在整个 ModelZoo-PyTorch 仓中处于如下关联位置：

- **上游 / 维护方**：[ModelZoo 社区](https://gitcode.com/Ascend/ModelZoo-PyTorch)——镜像的发行与维护主体，本文档是该社区容器镜像体系的一员。
- **同级能力文档**：[ModelZoo 文档首页](https://gitcode.com/Ascend/ModelZoo-PyTorch/blob/master/ACL_PyTorch/README.md)——提供仓级 README，是该镜像的使用入口；本镜像位于 `ACL_PyTorch/docker/` 子树，因此归类于 ACL（Ascend Computing Language）PyTorch 推理路径。
- **下游使用指南**：[昇腾 ONNX 推理流程指南](https://gitcode.com/Ascend/ModelZoo-PyTorch/blob/master/ACL_PyTorch/docs/ONNX/README.md)——本镜像的核心能力即"端到端推理"，该指南给出具体的 ONNX 模型转换与推理步骤，是镜像能力的实际使用说明书。
- **问题反馈链路**：[Issues](https://gitcode.com/Ascend/ModelZoo-PyTorch/issues)——驱动兼容性、算子缺失、ONNX 转换失败等问题在此闭环。
- **横向工具集成关系**：镜像内集成的 `torch_npu`、`MindIE-SD`、`onnxslim`、`ais_bench`、`MSIT` 分别承担**算子后端适配**、**服务化推理调度**、**ONNX 图优化**、**性能基准采集**、**图分析与 dump** 的角色，互为上下游配合；任一环节缺位都会影响"端到端推理"这一对外承诺。

---

## 【使用方法】

**1. 宿主机前置检查**（原文命令）：

```bash
npu-smi info
```
确认驱动与固件已安装且 NPU 设备健康。

**2. 启动容器**（原文示例，以 Atlas 800I A2 + openEuler Tag 为例）：

```bash
docker run -it -d --net=host --shm-size=1g \
   --name <container-name> \
   --device=/dev/davinci_manager:rwm \
   --device=/dev/hisi_hdc:rwm \
   --device=/dev/devmm_svm:rwm \
   --device=/dev/davinci0:rwm \
   -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
   -v /usr/local/Ascend/firmware/:/usr/local/Ascend/firmware:ro \
   -v /usr/local/sbin:/usr/local/sbin:ro \
   -v /path-to-weights:/path-to-weights:ro \
   torch-onnx-inference:cann8.3.rc1_torch2.1.0-800I-A2-openeuler24.03-py3.11-aarch64 bash
```

关键参数说明（基于原文）：
- `--net=host`：使用宿主机网络，便于推理服务直接对外暴露。
- `--shm-size=1g`：提升 `/dev/shm` 容量，规避 PyTorch DataLoader 多进程崩溃。
- `--device=...rwm`：将 NPU 管理面与设备节点以读写权限透传。
- `-v ...:ro`：驱动、固件、系统工具以只读方式挂载，避免容器篡改宿主机环境。
- `-v /path-to-weights:/path-to-weights:ro`：将模型权重目录以只读方式挂入容器。

**3. 进入已运行容器进行二次开发**（原文命令）：

```bash
docker exec -it torch-onnx-inference-800I-A2 bash
```

**4. 验证昇腾软件栈连通性**（原文命令）：

```bash
python3 -c "import torch; import torch_npu; print(torch.npu.is_available())"
```
预期输出为 `True`，表示 PyTorch 已成功注册 NPU 后端。

**5. 本地构建**（原文示例，以 Atlas 800I A2 openEuler 镜像为例）：

```bash
docker build \
  -t <YOUR_IMAGE_REGISTRY>/torch-onnx-inference:cann8.3.rc1_torch2.1.0-800I-A2-openeuler24.03-py3.11-aarch64 \
  -f ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.800I_A2.openeuler .
```
需在 `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/` 同级目录执行。

**6. 宿主驱动配套要求**（原文："宿主机驱动版本需不低于 24.1.RC3"）：低于该版本的驱动可能导致算子编译失败或推理异常。

**7. 环境激活**：登录容器后自动进入 Conda `base` 环境（`Python 3.11`），无需手动 `conda activate`——原文未涉及具体 Conda 命令切换。
