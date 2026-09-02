# MindSpeed-Bridge Docker 镜像概述

> 仓 `mindspeed-bridge` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-bridge/docker/OVERVIEW.zh.md

# MindSpeed-Bridge Docker 镜像文档 一体化解读

---

## 【定位】

这篇文档是 `mindspeed-bridge` 仓库存放 Ascend NPU 训练镜像构建产物的 `docker/` 目录说明——告诉使用者**镜像内默认装了什么软件栈、用什么命令构建、如何按芯片/OS/Python 版本定制，以及容器如何挂载设备并启动训练**，是 MindSpeed-Bridge 在昇腾上落地的"构建 + 运行"操作手册。

---

## 【技术要点】

1. **基础镜像选型**：默认以 AscendHub 的 CANN `9.1.0` 镜像为基座（典型形态 `9.1.0-910b-openeuler24.03-py3.12`），复用其内置 Python `3.12`，**不额外安装 Conda**，避免多环境冲突。
2. **替代 MindSpeed 的 NPU 适配方案**：镜像不再安装 MindSpeed，而是改为在 Megatron-LM 之上叠加两个昇腾 NPU 适配组件：
   - `MegatronAdaptor` (`core_r0.18.0`)，以 `pip install -e . --no-build-isolation --no-deps` 可编辑安装；
   - `TransformerEngineNPU` (`main` 分支)，以 `pip install -e . --no-build-isolation` 可编辑安装。
3. **MindSpeed-Ops 保留原因**：仅因 MindSpeed-Bridge 的 **Qwen3.5-VL GDN 算子**依赖 `mindspeed_ops`，故镜像仍安装 MindSpeed-Ops (`master`) 源码。
4. **flash-linear-attention-npu 算子自动编译**：镜像构建时会在 clone 之后**自动 source CANN 环境**，编译安装 GDN 相关自定义算子 run 包与 `torch_custom/fla_npu` whl 包；`--soc` 默认为 `910b→ascend910b`、`a3→ascend910_93`、`950→ascend950`，可由 `--fla-npu-soc` 覆盖。算子名单统一维护在 `image_build.sh` 的 `FLA_NPU_OPS` 数组里，新增只需追加。
5. **torch_npu 安装双通道**：默认从 GitCode release 下载 `torch_npu-2.9.0.post6-cp312-cp312-manylinux_2_28_aarch64.whl` 经 `--torch-npu-whl-url` 安装；置空 `--torch-npu-whl-url ""` 时退化为 `pip install torch-npu==${TORCH_NPU_VERSION}`。`triton-ascend==3.2.1` 从 `https://triton-ascend.osinfra.cn/pypi/simple` 拉取。
6. **容器化与设备直通**：运行容器使用 `--privileged --network host --ipc=host` 并挂载 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm` 四个 NPU 设备节点，以及 `Ascend driver`、`dcmi`、`npu-smi`、`ascend_install.info` 等主机文件；裸机 Docker 版本**不低于 26.X**，否则多线程构建会失败。

---

## 【关键机制与数据】

### 镜像构建/安装工作机制

- **工作目录布局**（原文）：
  - `/workspace/Megatron-Bridge`（默认工作目录）
  - `/workspace/MindSpeed-Bridge`（MindSpeed-Bridge 源码）
  - `/workspace/MindSpeed-Ops`（MindSpeed-Ops 源码）
  - `/workspace/MegatronAdaptor`（MegatronAdaptor 源码）
  - `/workspace/TransformerEngineNPU`（TransformerEngineNPU 源码）
  - `/workspace/flash-linear-attention-npu`（flash-linear-attention-npu 源码）
- **FLA NPU 算子编译机制**（原文）：镜像构建流程会在 `flash-linear-attention-npu` clone 后**自动 source CANN 环境**，并编译安装 GDN 自定义算子 run 包及 `torch_custom/fla_npu` whl 包；`--soc` 经 `FLA_NPU_OPS` 数组自动拼接成 `build.sh --ops` 的逗号分隔参数。
- **代理透传机制**（原文）：`image_build.sh` 默认使用 `--network=host`；若 shell 设了 `http_proxy/https_proxy/HTTP_PROXY/HTTPS_PROXY/no_proxy/NO_PROXY`，脚本会**自动**通过 `--build-arg` 透传到 Docker build。
- **失败清理机制**（原文）：`--cleanup-on-fail` 在构建失败时清理无标签镜像及相关容器。

### 训练入口数据流（原文）

- 容器内建议从 `/workspace/Megatron-Bridge` 目录启动训练脚本；
- 训练命令形态：
  - `bash /workspace/MindSpeed-Bridge/mindspeed_bridge/examples/models/vlm/qwen35_vl/qwen35_vl_35b_sft.sh`（脚本入口）；
  - `torchrun ... --module mindspeed_bridge.scripts.training.run_recipe ...`（Python 模块入口）。

> 文档本身未提供任何基准性能数据（FPS、吞吐、显存占用等），故不在此臆造。

---

## 【表格解读】

### 1) 快速参考表（镜像基本元信息）

| 项目 | 说明 |
| ------ | ------ |
| 镜像名称 | `mindspeed-bridge` |
| Dockerfile 路径 | `docker/Dockerfile` |
| 默认基础镜像 | AscendHub CANN `9.1.0` |
| 默认 TorchNPU | `2.9.0` |
| 默认 Python | `3.12` |
| 支持机型 | `910b`、`a3`、`950` |

**逐行解读：**
- "镜像名称 `mindspeed-bridge`"：最终 docker 镜像 tag 名（在运行命令里展示为 `mindspeed-bridge:master-910b-openeuler24.03-cann9.1.0-torchnpu2.9.0-py3.12-aarch64` 这种拼接形态）。
- "Dockerfile 路径 `docker/Dockerfile`"：构建入口脚本所在目录。
- "默认基础镜像 AscendHub CANN `9.1.0`"：决定 NNAL/CANN 算子库版本，整套上层 PyTorch / torch_npu 兼容性以此为基础。
- "默认 TorchNPU `2.9.0`"：与 PyTorch `2.9.0` 严格对齐，二者版本必须一致。
- "默认 Python `3.12`"：决定所有 wheel 的 `cp312` 标识，也影响基础镜像 OS 拼接形态。
- "支持机型 `910b`、`a3`、`950`"：三档 NPU 覆盖训练芯片与推理芯片，`--npu-type` 必须从这三者中选。

### 2) 默认软件栈版本表

| 组件 | 默认版本 |
| ------ | ------ |
| CANN 基础镜像 | `9.1.0` |
| TorchNPU | `2.9.0` |
| PyTorch | `2.9.0` |
| torch_npu | `2.9.0`，默认通过 `torch_npu-2.9.0.post6-cp312-cp312-manylinux_2_28_aarch64.whl` 安装 |
| triton-ascend | `3.2.1` |
| MegatronAdaptor | `core_r0.18.0` |
| TransformerEngineNPU | `main` |
| MindSpeed-Ops | `master` |
| flash-linear-attention-npu | `v26.1.0` |
| Megatron-LM | `core_v0.18.0` |
| Megatron-Bridge | `v0.5.0` |
| MindSpeed-Bridge | `master` |

**逐行解读：**
- "CANN 基础镜像 `9.1.0`"：算子编译时 source 的 CANN 环境，决定 `ascend910b/ascend910_93/ascend950` 的使能能力。
- "TorchNPU / PyTorch `2.9.0`"：训练框架主干，二者版本必须一致（`--torch-version` 与 `--torch-npu-version` 联动）。
- "`torch_npu` ... manylinux_2_28_aarch64"：aarch64 + manylinux_2_28 决定基础镜像需为 OpenEuler/Ubuntu 高版本，否则 wheel 无法安装。
- "`triton-ascend` `3.2.1`"：昇腾版 Triton，用于算子融合与图编译。
- "`MegatronAdaptor` `core_r0.18.0`"：取代 MindSpeed，提供 Megatron-LM 与昇腾 NPU 的桥接（含张量并行、流水并行等）。
- "`TransformerEngineNPU` `main`"：昇腾 FP8/Transformer 加速模块，挂在 Megatron-LM 之上。
- "`MindSpeed-Ops` `master`"：仅为 Qwen3.5-VL GDN 算子依赖而保留。
- "`flash-linear-attention-npu` `v26.1.0`"：本镜像在构建期会额外编译其中的 GDN 自定义算子。
- "`Megatron-LM` `core_v0.18.0`"：底层训练框架，决定 MegatronAdaptor/Megatron-Bridge 的兼容边界。
- "`Megatron-Bridge` `v0.5.0`"：Megatron-LM 的新训练入口（`run_recipe` 等模块在这里）。
- "`MindSpeed-Bridge` `master`"：本仓库代码，是 Megatron-Bridge 在昇腾上的扩展。

### 3) FLA NPU `--soc` 默认映射表

| 机型 | FLA NPU `--soc` |
| ------ | ------ |
| `910b` | `ascend910b` |
| `a3` | `ascend910_93` |
| `950` | `ascend950` |

**逐行解读：**
- "`910b → ascend910b`"：训练主力芯片，对应 Atlas 800T/900 等。
- "`a3 → ascend910_93`"：A3 训练服务器（Ascend 910C/93 系列），命名带下划线 + 数字后缀。
- "`950 → ascend950`"：推理/训练新一代芯片；表格映射固定，写死脚本。
- 任何一行被覆盖时只需 `--fla-npu-soc ascend910_93` 等即可。

### 4) `image_build.sh` 构建参数表

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-t, --npu-type TYPE` | `910b` | 指定 NPU 类型，支持 `910b`、`a3` 和 `950`。 |
| `-i, --image-name NAME` | 自动生成 | 指定输出镜像的完整名称和标签。未指定时按照默认镜像标签规则自动生成。 |
| `-o, --os OS` | `openeuler24.03` | 指定基础镜像操作系统，支持 `openeuler24.03` 和 `ubuntu22.04`。 |
| `-n, --no-cache` | 关闭 | 构建镜像时不使用 Docker 缓存。 |
| `--base-image IMAGE` | 自动拼接 | 指定完整的 CANN 基础镜像名称。指定后直接传递给 Dockerfile 的 `FROM`。 |
| `--base-image-version VER` | `9.1.0` | 指定自动拼接基础镜像时使用的 CANN 版本。 |
| `--python-version VER` | `3.12` | 指定 Python 版本。 |
| `--torch-version VER` | `2.9.0` | 指定 PyTorch 版本。 |
| `--torch-npu-version VER` | `2.9.0` | 指定 `torch_npu` 版本。 |
| `--torch-whl-url URL` | 空 | 从指定 wheel URL 安装 PyTorch。未指定时按版本号安装。 |
| `--torch-npu-whl-url URL` | 配套远端 wheel | 从指定 wheel URL 安装 `torch_npu`。传入空字符串时按版本号从 pip 源安装。 |
| `--triton-ascend-version VER` | `3.2.1` | 指定 Triton-Ascend 版本。 |
| `--mindspeed-bridge-branch VER` | `master` | 指定 MindSpeed-Bridge 的分支、标签或版本。 |
| `--mindspeed-ops-branch VER` | `master` | 指定 MindSpeed-Ops 的分支、标签或版本。 |
| `--megatron-branch VER` | `core_v0.18.0` | 指定 Megatron-LM 的分支或标签。 |
| `--megatron-bridge-branch VER` | `v0.5.0` | 指定 Megatron-Bridge 的分支或标签。 |
| `--megatron-adaptor-branch VER` | `core_r0.18.0` | 指定 MegatronAdaptor 的分支或标签。 |
| `--transformer-engine-npu-branch VER` | `main` | 指定 TransformerEngineNPU 的分支或标签。 |
| `--fla-npu-branch VER` | `v26.1.0` | 指定 flash-linear-attention-npu 的分支或标签。 |
| `--fla-npu-soc SOC` | 按 NPU 类型映射 | 指定 flash-linear-attention-npu 的目标芯片型号。默认映射为：`910b → ascend910b`、`a3 → ascend910_93`、`950 → ascend950`。 |
| `--cleanup-on-fail` | 关闭 | 构建失败时清理无标签的镜像及相关容器。 |
| `-h, --help` | - | 显示帮助信息并退出。 |

**逐行解读（节选要点）：**
- 顶层三件套（机型/OS/Python）由 `-t/-o/--python-version` 决定，决定基础镜像拼接形态。
- `--base-image` 与 `--base-image-version` 是"二选一覆盖"关系——前者优先级最高，可让 Dockerfile 跳过自动拼接。
- `--torch-version` 与 `--torch-npu-version` 必须配套（同版本号），否则 ABI 不兼容。
- `--torch-whl-url` / `--torch-npu-whl-url` 提供 wheel 走法；后者**传空串**即降级为 pip 源安装（这是文档明确写的两种安装模式切换）。
- 五个 `--*-branch` 参数（MindSpeed-Bridge/Ops、Megatron-LM、Megatron-Bridge、MegatronAdaptor、TransformerEngineNPU、flash-linear-attention-npu）允许在不改 Dockerfile 的情况下切换到任意 fork 的某个 tag。
- `--fla-npu-soc` 是上面 SOC 映射表的人工覆盖入口。
- `--cleanup-on-fail` 仅做"无标签镜像 + 容器"清理，是 CI 友好选项。

---

## 【公式解读】

原文无公式（仅有版本号、shell 命令、目录路径与表格），无 LaTeX 或伪代码形式的算式需要解读，故略。

---

## 【关联】

文档内部未给出"内部链接"索引（用户提供"内部链接: (无)"），但其叙述本身揭示出 MindSpeed-Bridge 与以下模块/仓库存在强耦合：

- **下游/被替代关系**：`docker/` 文档明确写到镜像"不再安装 MindSpeed，改为在 Megatron-LM 之上安装昇腾 NPU 适配组件"。这意味着：
  - `MindSpeed`（旧）→ 被 `MegatronAdaptor + TransformerEngineNPU`（新）替代；
  - 迁移后的栈顶是 `MindSpeed-Bridge`，下方依次挂 `Megatron-Bridge` → `Megatron-LM` → `MegatronAdaptor`/`TransformerEngineNPU`。
- **保留依赖**：`MindSpeed-Ops` 仅为 **Qwen3.5-VL GDN 算子**依赖而保留——即 MindSpeed-Bridge 的 VLM/Qwen3.5-VL 路径仍间接依赖 `mindspeed_ops`，不替代不掉。
- **算子侧独立编译**：flash-linear-attention-npu 自带算子构建链（`build.sh --ops`，从 `FLA_NPU_OPS` 数组出参），与主 CANN 算子分开构建，但要求构建期 `source CANN` 环境。
- **运行链路**：训练入口脚本在 `/workspace/MindSpeed-Bridge/mindspeed_bridge/examples/...` 下，但**默认工作目录是 `/workspace/Megatron-Bridge`**——即 MindSpeed-Bridge 把 shell 训练样例与 Megatron-Bridge 的 `run_recipe` Python 入口并联提供，MindSpeed-Bridge 自身只贡献 `mindspeed_bridge` Python 包与模型适配。
- **模型层依赖**：文档末尾"训练入口"示例直接给出 `qwen35_vl_35b_sft.sh`，暗示 MindSpeed-Bridge 在该镜像里首要保证的是 Qwen3.5-VL（含 GDN 算子）能在昇腾上跑通——这是为何同时保留 MindSpeed-Ops + 编译 flash-linear-attention-npu 的根因。
- **上游镜像来源**：AscendHub（华为云 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-*`）；`triton-ascend` 来自 `https://triton-ascend.osinfra.cn/pypi/simple`；`torch_npu` 走 GitCode release 站点。

---

## 【使用方法】

> 以下命令均**逐字取自原文**，未做任何臆测。

### 1) 构建镜像（默认配置）
```bash
cd docker
bash image_build.sh
```
等价于：CANN `9.1.0` + TorchNPU `2.9.0` + Python `3.12` + NPU `910b` + OS `openeuler24.03`。

### 2) 指定完整基础镜像
```bash
bash image_build.sh \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.12
```

### 3) 覆盖 `torch_npu` 安装源（默认远端 wheel）
```bash
bash image_build.sh \
  --torch-npu-whl-url https://gitcode.com/Ascend/pytorch/releases/download/v26.1.0-pytorch2.9.0/torch_npu-2.9.0.post6-cp312-cp312-manylinux_2_28_aarch64.whl
```

### 4) 改用 pip 源安装 `torch_npu`
```bash
bash image_build.sh --torch-npu-whl-url ""
```

### 5) 调整 `triton-ascend` 版本
```bash
bash image_build.sh --triton-ascend-version 3.2.1
```

### 6) 覆盖 FLA NPU SOC 默认映射
```bash
bash image_build.sh --fla-npu-soc ascend910_93
```

### 7) 切换其他组件版本/分支（典型示例）
```bash
bash image_build.sh \
  --mindspeed-bridge-branch master \
  --mindspeed-ops-branch master \
  --megatron-branch core_v0.18.0 \
  --megatron-bridge-branch v0.5.0 \
  --megatron-adaptor-branch core_r0.18.0 \
  --transformer-engine-npu-branch main \
  --fla-npu-branch v26.1.0
```

### 8) 查看全部构建参数
```bash
bash image_build.sh --help
```

### 9) 运行镜像（含 NPU 设备直通）
```bash
docker run -it --rm \
  --name mindspeed-bridge \
  --privileged \
  --network host \
  --ipc=host \
  --device=/dev/davinci0 \
  --device=/dev/davinci_manager \
  --device=/dev/hisi_hdc \
  --device=/dev/devmm_svm \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /home:/home \
  -v /data:/data \
  mindspeed-bridge:master-910b-openeuler24.03-cann9.1.0-torchnpu2.9.0-py3.12-aarch64 \
  bash
```

### 10) 容器内启动训练（脚本入口）
```bash
cd /workspace/Megatron-Bridge
bash /workspace/MindSpeed-Bridge/mindspeed_bridge/examples/models/vlm/qwen35_vl/qwen35_vl_35b_sft.sh
```

### 11) 容器内启动训练（Python 模块入口）
```bash
torchrun ... --module mindspeed_bridge.scripts.training.run_recipe ...
```

### 12) 注意事项（原文摘要）
- 镜像名按 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:{CANN版本}-{芯片}-{OS}-py{Python版本}` 拼接；若 AscendHub 实际镜像名不同请用 `--base-image`。
- `torch_npu` wheel 默认来自 `v26.1.0-pytorch2.9.0` release。
- 不同模型可能仍需额外依赖或数据准备，请参考对应模型 README。
- 裸机 Docker 版本**不低于 26.X**，否则多线程构建会失败。
