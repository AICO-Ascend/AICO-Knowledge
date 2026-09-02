# Image Overview: Atlas torch-onnx-inference Environment

> 仓 `modelzoo-pytorch` · 路径 `ACL_PyTorch/docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/ACL_PyTorch/docker/OVERVIEW.md

# 「ACL_PyTorch/docker/OVERVIEW.md」一体化深度解读

## 【定位】
本文档是 ModelZoo-PyTorch 仓中 `torch-onnx-inference` 容器镜像的 Overview,系统性说明该镜像的运行栈构成、支持硬件/OS/CANN 版本矩阵、镜像标签与 Dockerfile 路径对应关系、容器启动与本地构建命令,以及 NPU 驱动兼容性要求,服务于在 Atlas NPU 上做 ONNX 推理部署的开发者快速上手。

---

## 【技术要点】

1. **镜像维护与归属**:该运行时环境由 ModelZoo Community 维护,目标是托管 ModelZoo 仓内经典/主流 AI 模型的端到端推理工作流。
2. **软件栈固化版本**:CANN **8.3.RC1** + PyTorch **2.1.0** + Python **3.11** + Miniconda;预装 `torch_npu`(原生加速)、`MindIE-SD`(服务化部署)、`ais_bench` 与 `MSIT`(性能基准/调试)、`onnxslim`(ONNX 图优化)。
3. **硬件/OS 矩阵(两轴交叉)**:
   - 硬件轴:Atlas **300I DUO** / Atlas **800I A2**(均为 NPU 架构)
   - OS 轴:Ubuntu **22.04 LTS**(AArch64) / openEuler **24.03 LTS**(AArch64)
   - 镜像标签命名严格形如:`cann8.3.rc1_torch2.1.0-<hardware>-<os>-py3.11-aarch64`。
4. **驱动/固件硬约束**:宿主机需安装 Atlas NPU 驱动和固件,且要求 Host Driver **24.1.RC3** 或更高版本,以保证反向算子执行的完整兼容性;启动前用 `npu-smi info` 确认 NPU 健康。
5. **容器设备透传机制**:启动时必须 `--device` 透传 `davinci_manager` / `hisi_hdc` / `devmm_svm` / `davinci0`(read-write)四类设备节点,并将宿主机的 `/usr/local/Ascend/driver`、`/usr/local/Ascend/firmware`、`/usr/local/sbin` 以只读方式挂入容器,以复用宿主机驱动栈。
6. **Conda 环境与 NPU 自检**:登录即自动激活 Python 3.11 的 Conda base 环境;通过 `python3 -c "import torch; import torch_npu; print(torch.npu.is_available())"` 一行命令验证 NPU 栈可用性。

---

## 【关键机制与数据】

- **栈定位(原文)**:原文称 `torch-onnx-inference` 是"a high-performance deep learning inference deployment and full-stack development runtime environment tailored specifically for edge and device-side scenarios",核心使命是"host and execute the end-to-end inference workflows for classic and mainstream AI models within the ModelZoo repository"。
- **栈整合机制(原文)**:PyTorch 框架 + `torch_npu` 原生加速库 + `MindIE-SD` + ONNX 图优化与基准工具集(`onnxslim`、`ais_bench`、`MSIT`)形成"端到端推理工作流"闭环。
- **驱动桥接机制(原文)**:宿主机驱动/固件目录被以 `:ro` 只读挂载到容器内同名路径,容器本身不内置驱动,而是通过设备透传+目录挂载"借力"宿主驱动栈。
- **环境激活机制(原文)**:"The Conda base environment (Python 3.11) is activated automatically upon login",即登录即激活。
- **性能/吞吐数据**:原文未给出任何具体吞吐量、时延或基准数字,本文不臆造。

---

## 【表格解读】

**镜像标签与 Dockerfile 路径对应表(逐字还原):**

| Full Image Path (`<Registry>/<ImageName>:<Tag>`) | Base OS | Target Hardware | Dockerfile Archive Path |
| :--- | :--- | :--- | :--- |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-300I-DUO-ubuntu22.04-py3.11-aarch64` | Ubuntu 22.04 | Atlas 300I DUO | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.300IDUO.ubuntu` |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-300I-DUO-openeuler24.03-py3.11-aarch64` | openEuler 24.03 | Atlas 300I DUO | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.300IDUO.openeuler` |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-800I-A2-ubuntu22.04-py3.11-aarch64` | Ubuntu 22.04 | Atlas 800I A2 | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.800I_A2.ubuntu` |
| `torch-onnx-inference:cann8.3.rc1_torch2.1.0-800I-A2-openeuler24.03-py3.11-aarch64` | openEuler 24.03 | Atlas 800I A2 | `ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.800I_A2.openeuler` |

**逐行解读:**

- **行 1 — 300I DUO + Ubuntu 22.04**:面向 Atlas 300I DUO 卡的 Ubuntu 22.04 镜像,Dockerfile 位于 `docker/cann8.3.rc1_torch2.1.0/Dockerfile.300IDUO.ubuntu`。这是"硬件/OS"二维矩阵的 Ubuntu 入门组合,适合主流桌面/服务器式部署。
- **行 2 — 300I DUO + openEuler 24.03**:同硬件的 openEuler 24.03 LTS 版,Dockerfile 为 `Dockerfile.300IDUO.openeuler`,面向国产化操作系统需求。
- **行 3 — 800I A2 + Ubuntu 22.04**:面向 Atlas 800I A2(训推一体推理卡)的 Ubuntu 版,Dockerfile 为 `Dockerfile.800I_A2.ubuntu`,适用于需要更强算力的边缘/中心侧推理场景。
- **行 4 — 800I A2 + openEuler 24.03**:矩阵的最右下角(800I A2 + openEuler),对应 Dockerfile `Dockerfile.800I_A2.openeuler`,同时满足"高性能推理硬件 + 国产 OS"两个维度的需求。

四条标签的命名结构一致:`cann{版本}_torch{版本}-{硬件代号}-{os 版本}-py{Python 版本}-aarch64`,可视为镜像自描述的"指纹串",在自建或推送时只需替换 `<Registry>/` 前缀。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游/社区归属**:镜像由 **ModelZoo Community**(Ascend/ModelZoo-PyTorch)维护,属于 `ACL_PyTorch` 子目录(Atlas Compute Library / PyTorch)下的运行时镜像族。
- **文档链路**:原文顶部给出三处求助/导航链接:
  - 仓库总入口:ModelZoo Documentation → `ACL_PyTorch/README.md`
  - 推理流程指南:Atlas ONNX Inference Workflow Guide → `ACL_PyTorch/docs/ONNX/README.md`(与本镜像同名,说明本镜像正是该工作流的"运行时载体")
  - 问题反馈:Issues & Feature Requests → 仓 issues 页
- **栈内依赖关系**:本镜像的"端到端推理工作流"以 ModelZoo 仓内"经典/主流 AI 模型"为执行对象,栈内各组件的关系是:`PyTorch` 提供模型表示 → `torch_npu` 提供 NPU 算子落地 → `onnxslim` 做 ONNX 图瘦身 → `MindIE-SD` 提供服务化部署能力 → `ais_bench` / `MSIT` 做性能与正确性基准。
- **底层硬件依赖**:宿主机的 **Atlas NPU Driver 24.1.RC3+** 与 **Firmware** 是镜像可用性的硬前置,本镜像自身不打包驱动,只通过设备透传+目录挂载消费。
- **法律关联**:镜像由 Huawei Technologies Co., Ltd. 于 2026 年发布,受 Huawei Container License Agreement 约束,并要求使用方同时遵守镜像内嵌的华为及第三方软件各自的许可协议。
- 内部链接:原文链接均为对外仓内 URL,文档显式声明 "(无)" 内部交叉链接;实际在文档外通过仓内 `ACL_PyTorch/README.md` 与 `ACL_PyTorch/docs/ONNX/README.md` 串联。

---

## 【使用方法】

### 1. 启动前检查(原文)
```bash
npu-smi info
```
确保宿主机 Atlas NPU 驱动/固件已正确安装,NPU 设备健康。

### 2. 启动容器(原文,以 800I A2 + openEuler 为例)
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
要点: `--net=host`、`--shm-size=1g`、四个 `--device` 设备透传(其中 `davinci0` 视实际卡序号调整)、三个 `:ro` 目录挂载(驱动/固件/sbin)、权重目录只读挂载;其他硬件/OS 组合只需替换镜像 Tag。

### 3. 进入容器做二次开发(原文)
```bash
docker exec -it torch-onnx-inference-800I-A2 bash
```
登录后 Conda base(Python 3.11)自动激活。

### 4. NPU 栈自检(原文)
```bash
python3 -c "import torch; import torch_npu; print(torch.npu.is_available())"
```

### 5. 本地重建镜像(原文,以 800I A2 + openEuler 为例)
```bash
docker build \
  -t <YOUR_IMAGE_REGISTRY>/torch-onnx-inference:cann8.3.rc1_torch2.1.0-800I-A2-openeuler24.03-py3.11-aarch64 \
  -f ModelZoo-PyTorch/ACL_PyTorch/docker/cann8.3.rc1_torch2.1.0/Dockerfile.800I_A2.openeuler .
```
其余三组(300I DUO + Ubuntu/openEuler、800I A2 + Ubuntu)仅需替换 `-f` 指向的 Dockerfile 与 `-t` 中的镜像 Tag。

### 6. 环境变量 / 配置项
原文未涉及具体环境变量或配置文件路径。
