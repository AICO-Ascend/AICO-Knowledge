# MindIE-SD

> 仓 `mindie-sd` · 路径 `docker/omni/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docker/omni/OVERVIEW.zh.md

# MindIE-SD `docker/omni/OVERVIEW.zh.md` 一体化深度解读

---

## 【定位】

本文档是 MindIE-SD 仓库中 `docker/omni` 镜像（即 `mindiesd`）的官方中文概览，描述如何通过单一容器在昇腾 NPU 上**同时**进行多模态大语言模型推理（vLLM-Omni）与 Stable Diffusion 图像生成（MindIE-SD），并给出 Tag 命名、硬件适配、运行/构建/二次开发等使用指引。

---

## 【技术要点】

1. **集成能力**：将 **vLLM-Omni** 与 **MindIE-SD** 集成到同一容器，实现「多模态 LLM 推理 + Stable Diffusion 文生图」双栈共存。原文表述："本镜像将 vLLM-Omni 与 MindIE-SD（Mind Inference Engine Stable Diffusion）集成在单一容器中，支持在昇腾 NPU 上同时进行多模态大语言模型推理和 Stable Diffusion 图像生成。"

2. **两套 NPU 适配**：分为 Atlas 800I A2 推理服务器与 Atlas 800I A3 超节点服务器两条产品线，对应两条 Tag 与两份 Dockerfile。
   - A2：`v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64`
   - A3：`v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64`

3. **基础镜像分层**：以 `quay.io/ascend/vllm-omni:v0.20.0`（A2）与 `quay.io/ascend/vllm-omni:v0.20.0-a3`（A3）为底，已含 CANN 8.5.1、torch、TorchNPU、vllm、vllm_ascend；再叠加 5 个昇腾侧工具链（详见表格）。

4. **运行环境栈版本固定**：CANN `8.5.1`、TorchNPU `2.9.0`、Python `3.11`、Ubuntu `22.04`、架构 `linux/arm64`（aarch64）。

5. **Tag 命名规则**：`{版本号}-{CANN版本}-{torch_npu版本}-{适用产品信息}-{操作系统}-{Python版本}-{架构类型}-{其他字段}`。

6. **容器运行硬性约束**：必须 `--privileged`、必须挂载 NPU 设备 `/dev/davinci0..3`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并以 `-v` 方式注入宿主机驱动与 DCMI 路径（详见硬件支持表）。原文表述："`--privileged` 和设备映射是访问 NPU 的必要条件。"

---

## 【关键机制与数据】

原文未提供工作流图、量化指标、吞吐/延迟等性能数据，亦无数据流细节。文档以「容器使用指南」为主，仅在以下几处给出可核验的事实性数据，原文如下：

- **集成范围（原文）**："本镜像将 vLLM-Omni 与 MindIE-SD（Mind Inference Engine Stable Diffusion）集成在单一容器中，支持在昇腾 NPU 上同时进行多模态大语言模型推理和 Stable Diffusion 图像生成。"
- **基础镜像内容（原文）**："镜像基于 `quay.io/ascend/vllm-omni` 基础镜像构建（已包含 CANN 8.5.1、torch、TorchNPU、vllm 及 vllm_ascend）"
- **运行时长驻进程路径（原文）**：容器启动后进入 `bash`，未启动任何服务进程（无 entrypoint 服务化）。
- **许可证（原文）**：木兰宽松许可证 第2版（Mulan PSL v2）。
- **维护方（原文）**：本镜像由 [MindIE community](https://www.hiascend.com/cn/developer/software/mindie) 维护。

性能/吞吐/精度等量化指标在原文中**未涉及**，按要求不臆造。

---

## 【表格解读】

### 表格 1：快速参考表（原文逐字还原）

| 项目 | 值 |
|------|-----|
| **镜像** | `mindiesd` |
| **Tags** | `v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64` |
| | `v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64` |
| **基础镜像** | Atlas 800I A2 推理服务器：`quay.io/ascend/vllm-omni:v0.20.0` |
| | Atlas 800I A3 超节点服务器：`quay.io/ascend/vllm-omni:v0.20.0-a3` |
| **架构** | `linux/arm64`（aarch64） |
| **操作系统** | Ubuntu 22.04 |
| **Python** | 3.11 |
| **CANN** | 8.5.1 |
| **TorchNPU** | 2.9.0 |
| **许可证** | 木兰宽松许可证 第2版（Mulan PSL v2） |

**逐行解读**：
- **镜像 / Tags**：镜像名固定为 `mindiesd`，Tag 由版本号、CANN、torch_npu、产品代号、OS、Python、架构拼接，与下文命名规则表一致。
- **基础镜像**：A2/A3 各对应不同上游镜像，是产品适配差异的源头。
- **架构**：限定 `aarch64`，意味着不能在 x86 主机上原生运行（与昇腾 ARM 主机匹配）。
- **Python/CANN/TorchNPU**：固定版本栈，体现镜像的可复现性，避免依赖漂移。
- **许可证**：木兰宽松许可证 第2版，宽松开源许可。

### 表格 2：镜像内组件版本表（原文逐字还原）

| 组件 | 版本 | 说明 |
|------|------|------|
| mindiesd | 最新版 | MindIE Stable Diffusion 推理引擎 |
| msprobe | 0.1.4 | 精度调试工具 |
| msmodelslim | 8.2.1 | 模型压缩/量化工具 |
| msprof-analyze | 26.0.0 | MindStudio Profiler 分析工具 |
| msprof | *（随 CANN 捆绑）* | NPU 性能Profiling工具 |

**逐行解读**：
- **mindiesd**：核心新增组件，提供 SD 推理能力，"最新版"未钉死版本号。
- **msprobe 0.1.4**：用于精度比对/调试（如 FP16 vs BF16 vs INT8 一致性验证）。
- **msmodelslim 8.2.1**：用于 SD/LLM 模型的量化（如 W8A8、W4A16）压缩。
- **msprof-analyze 26.0.0**：采集后的 profiling 数据离线分析器；版本号 `26.0.0` 与 MindStudio Profiler 主版本对齐。
- **msprof**：NPU 性能 Profiling 工具，由 CANN 自带，不单独声明版本。

### 表格 3：Tag 命名规则示例对照表（原文逐字还原）

| 系列 | 示例 Tag | 基础镜像 |
|------|----------|----------|
| Atlas 800I A2 推理服务器 | `v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64` | `quay.io/ascend/vllm-omni:v0.20.0` |
| Atlas 800I A3 超节点服务器 | `v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64` | `quay.io/ascend/vllm-omni:v0.20.0-a3` |

**逐行解读**：
- **A2 行**：产品代号字段为 `910b`（Ascend 910B），对应 A2 推理服务器。
- **A3 行**：产品代号字段为 `a3`（Ascend 910C/超节点形态），对应 A3 超节点。
- 两条 Tag 中仅"产品信息"段不同，反映产品适配是唯一变量。

### 表格 4：Dockerfile 归档路径表（原文逐字还原，共出现两次，结构一致）

| 系列 | 示例 Tag | Dockerfile |
|------|----------|------------|
| Atlas 800I A2 推理服务器 | `v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64` | [Dockerfile](https://gitcode.com/Ascend/MindIE-SD/blob/master/docker/omni/Dockerfile.a2.ubuntu) |
| Atlas 800I A3 超节点服务器 | `v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64` | [Dockerfile](https://gitcode.com/Ascend/MindIE-SD/blob/master/docker/omni/Dockerfile.a3.ubuntu) |

**逐行解读**：
- **A2 行 Dockerfile**：`docker/omni/Dockerfile.a2.ubuntu` 路径下，可在 gitcode 仓库直接查阅构建指令。
- **A3 行 Dockerfile**：`docker/omni/Dockerfile.a3.ubuntu` 路径下，与 A2 文件差异应在 `FROM` 行和 NPU 适配层。

### 表格 5：硬件支持表（原文逐字还原）

| 项目 | 要求 |
|------|------|
| **NPU** | Atlas 800I A2 推理服务器 |
| | Atlas 800I A3 超节点服务器 |
| **驱动** | 宿主机需安装昇腾 NPU 驱动 |
| **宿主机挂载** | `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info`、`/root/.cache` |

**逐行解读**：
- **NPU 行**：明示只支持 A2 / A3 两类 Atlas 推理服务器，其他型号未在原文中声明支持。
- **驱动行**：驱动在宿主机侧安装，容器内不打包驱动。
- **宿主机挂载**：6 个路径分别承担 DCMI 设备管理接口、`npu-smi` 命令、驱动动态库、驱动版本、昇腾安装信息、HF/缓存目录——其中 `/root/.cache` 通常用于 HuggingFace 模型缓存，是 LLM/SD 模型权重落盘路径。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文末信息（含外部链接与上下文），本镜像与以下模块/上游存在依赖或并列关系：

- **上游基础镜像**：`quay.io/ascend/vllm-omni:v0.20.0` / `:v0.20.0-a3`（包含 CANN 8.5.1、torch、TorchNPU、vllm、vllm_ascend）。`mindiesd` 镜像是在其之上的「叠加层」，并非替代关系。
- **底层软件栈**：
  - **CANN 8.5.1** —— NPU 异构计算架构；
  - **TorchNPU 2.9.0** —— PyTorch 的 NPU 适配层；
  - **vllm + vllm_ascend** —— LLM 推理引擎及其昇腾后端（来自基础镜像）；
  - **mindiesd** —— Stable Diffusion 推理引擎（本镜像新增）。
- **同仓工具/模块**（通过文末链接指明）：
  - MindIE-SD 文档索引：[`docs/zh/index.md`](https://gitcode.com/Ascend/MindIE-SD/blob/master/docs/zh/index.md)；
  - LICENSE：[`LICENSE.md`](https://gitcode.com/Ascend/MindIE-SD/blob/master/LICENSE.md)；
  - 问题反馈区：[`gitcode.com/Ascend/MindIE-SD/issues`](https://gitcode.com/Ascend/MindIE-SD/issues)；
  - 镜像索引页：[AscendHub af85b724…](https://www.hiascend.com/developer/ascendhub/detail/af85b724a7e5469ebd7ea13c3439d48f)。
- **配套昇腾工具链**：msprobe（精度调试）、msmodelslim（量化）、msprof-analyze + msprof（Profiling）——均非 vLLM-Omni 原生组件，而是本镜像为昇腾开发者补充的可观测/调优工具集。
- **并列产品线**（仓库级关联）：根据仓库 README，MindIE-SD 同时支持 vLLM Omni、Diffusers+CacheDit、lightx2v 等框架；本 README 所属的 `docker/omni` 仅是 vLLM-Omni 这一容器线的说明，其余框架的 Docker 镜像位于仓库其他目录（如 `docker/diffusers`、`docker/lightx2v` 等，原文未给出具体路径，但同仓存在并列模块可由此推断）。
- **社区归属**：由 [MindIE community](https://www.hiascend.com/cn/developer/software/mindie) 维护，并接入昇腾开发者社区 [hisascend.com/developer](https://www.hiascend.com/developer)。

---

## 【使用方法】

下列命令均**原文给出**，可直接复用。

### 1. 拉取基础镜像

A2：
```bash
docker pull quay.io/ascend/vllm-omni:v0.20.0
```
A3：
```bash
docker pull quay.io/ascend/vllm-omni:v0.20.0-a3
```
> 原文提示：使用 Podman 时把 `docker pull` 替换为 `podman pull`。

### 2. 运行容器（两套命令除镜像 Tag 不同外完全一致）

A2：
```bash
docker run -it --rm --name=mindiesd \
    --privileged \
    --shm-size=1g \
    --device /dev/davinci0 \
    --device /dev/davinci1 \
    --device /dev/davinci2 \
    --device /dev/davinci3 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64 \
    bash
```
A3 唯一区别：末行 Tag 改为
```
mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64
```

### 3. 本地构建（从源码）

A2：
```bash
git clone https://gitcode.com/Ascend/MindIE-SD.git
cd MindIE-SD/docker/omni
docker build -t mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64 \
    -f Dockerfile.a2.ubuntu .
```
A3：
```bash
git clone https://gitcode.com/Ascend/MindIE-SD.git
cd MindIE-SD/docker/omni
docker build -t mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-a3-ubuntu22.04-py3.11-aarch64 \
    -f Dockerfile.a3.ubuntu .
```

### 4. 二次开发（在 mindiesd 之上加层）

```dockerfile
FROM mindiesd:v3.0.0-cann8.5.1-torch_npu2.9.0-910b-ubuntu22.04-py3.11-aarch64

# 安装自定义依赖包
RUN pip install --no-cache-dir your-package

# 拷贝应用代码
COPY ./your-app /workspace/your-app
WORKDIR /workspace/your-app
```

### 5. 关键配置项 / 注意事项（原文）
- `--privileged` **必需**（访问 NPU）。
- `--shm-size=1g` 增大共享内存（PyTorch DataLoader 多 worker 场景常需）。
- 必须挂载 4 个 NPU 设备文件（`davinci0..3`）以及 `davinci_manager`、`devmm_svm`、`hisi_hdc`。
- 6 个宿主机路径必须 `-v` 注入（见硬件支持表）。
- 宿主机需**预先**安装昇腾 NPU 驱动。
- 容器启动后**不**自带后台服务（最后参数是 `bash`），需用户自行执行 vLLM-Omni / mindiesd 的启动命令；具体启动命令未在原文给出，属于未涉及内容。
