# MindSpeed-Bridge Docker Image Overview

> 仓 `mindspeed-bridge` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-bridge/docker/OVERVIEW.md

# mindspeed-bridge · docker/OVERVIEW.md 深度解读

## 【定位】
本篇文档是 MindSpeed-Bridge 在昇腾 NPU 上的**可配置 Docker 镜像构建入口说明**，定义默认软件栈版本、组件安装方式及镜像构建选项，用于为 Ascend 平台复现/定制 Bridge 模型的运行环境。

---

## 【技术要点】

1. **基于 CANN 基础镜像复用 Python 环境**：镜像不安装 Conda，直接使用 AscendHub CANN 基础镜像 `9.1.0` 自带的 Python（`3.12`），降低环境复杂度。
2. **"Megatron-LM + 昇腾适配层"替代 MindSpeed**：不再安装 MindSpeed，改为在 Megatron-LM（`core_v0.18.0`）之上以 `pip install -e . --no-build-isolation [--no-deps]` 可编辑源码方式安装 MegatronAdaptor（`core_r0.18.0`）和 TransformerEngineNPU（`main`）；MindSpeed-Ops 仅作为 Qwen3.5-VL GDN kernels 的依赖被保留（因 `mindspeed_ops` 仍被导入）。
3. **FLA NPU 自定义算子构建流程**：在镜像构建时先 clone `flash-linear-attention-npu`（`v26.1.0`），再 source CANN 环境，编译 GDN 自定义算子 run 包与 `torch_custom/fla_npu` wheel；NPU 类型到 `--soc` 参数存在固定映射（`910b`→`ascend910b`、`a3`→`ascend910_93`、`950`→`ascend950`），可由 `--fla-npu-soc` 覆盖；待编译算子列表维护在 `docker/image_build.sh` 的 `FLA_NPU_OPS` 数组中，脚本会转换为 `build.sh --ops` 所需的逗号分隔字符串。
4. **支持三类 NPU 平台**：`910b`、`a3`、`950`，通过 `-t/--npu-type` 切换并联动 FLA NPU 的 `--soc` 映射。
5. **torch_npu 与 PyTorch 安装来源可覆盖**：默认从 `https://gitcode.com/Ascend/pytorch/releases/download/v26.1.0-pytorch2.9.0/torch_npu-2.9.0.post6-cp312-cp312-manylinux_2_28_aarch64.whl` 拉取 wheel；可通过 `--torch-npu-whl-url ""` 回退到默认 pip 源按 `TORCH_NPU_VERSION`（`2.9.0`）安装；PyTorch 既可按版本安装也可由 `--torch-whl-url` 指定 wheel。
6. **构建网络与代理透传**：`image_build.sh` 默认使用 `--network=host`；当 `http_proxy/https_proxy/HTTP_PROXY/HTTPS_PROXY/no_proxy/NO_PROXY` 任一被设置时，会被自动作为 build arg 转发给 Docker build；构建失败时 `--cleanup-on-fail` 会清理悬空镜像与相关容器。

---

## 【关键机制与数据】

### 工作原理（基于原文）
- **整体流水线（原文）**：进入 `docker/` 目录 → 执行 `bash image_build.sh` → 脚本根据 `image_build.sh --help` 暴露的参数解析 NPU 类型、基础镜像、组件版本与分支 → 生成完整 `FROM` 基础镜像名（默认来自 AscendHub 命名规则，亦可由 `--base-image` 直接覆盖）→ 在 Dockerfile 中：source CANN 环境 → clone 各组件仓库到指定分支/tag → `pip install -e . --no-build-isolation [--no-deps]` 安装 MegatronAdaptor 与 TransformerEngineNPU → 安装 MindSpeed-Ops、flash-linear-attention-npu 及其自编译的 GDN run 包与 `torch_custom/fla_npu` wheel → 安装 `triton-ascend==3.2.1`（默认源 `https://triton-ascend.osinfra.cn/pypi/simple`）→ 输出镜像。
- **组件安装方式（原文）**：
  - MegatronAdaptor: `pip install -e . --no-build-isolation --no-deps`
  - TransformerEngineNPU: `pip install -e . --no-build-isolation`
- **MindSpeed-Ops 保留原因（原文）**："MindSpeed-Ops is still installed because the Qwen3.5-VL GDN kernels in MindSpeed-Bridge import `mindspeed_ops`."
- **FLA NPU 算子列表机制（原文）**："The FLA NPU operator list is maintained in the `FLA_NPU_OPS` array in `docker/image_build.sh`. Add new operator names to that array, and the script will convert it to the comma-separated value required by `build.sh --ops`."
- **回退安装语义（原文）**："To install `torch_npu` from the configured pip source instead, pass an empty wheel URL. The fallback pip package version follows `TORCH_NPU_VERSION`."

### 默认数据（原文：均为字面列出）
- AscendHub CANN 基础镜像版本：`9.1.0`；TorchNPU/PyTorch/torch_npu 版本：`2.9.0`；triton-ascend：`3.2.1`；MegatronAdaptor：`core_r0.18.0`；TransformerEngineNPU：`main`；MindSpeed-Ops：`master`；flash-linear-attention-npu：`v26.1.0`；Megatron-LM：`core_v0.18.0`；Megatron-Bridge：`v0.5.0`；Python：`3.12`；默认 NPU 类型：`910b`；默认 OS：`openeuler24.03`。
- torch_npu 默认 wheel 文件名：`torch_npu-2.9.0.post6-cp312-cp312-manylinux_2_28_aarch64.whl`。

### 性能数据
原文未涉及任何性能数据。

---

## 【表格解读】

### 表 1：FLA NPU `--soc` 映射（原文表格逐字还原）

| NPU type | FLA NPU `--soc` |
| ------ | ------ |
| `910b` | `ascend910b` |
| `a3` | `ascend910_93` |
| `950` | `ascend950` |

**逐行解读**：
- **`910b` → `ascend910b`**：原文将训练卡 910B 系列对应的 FLA NPU 编译 SoC 目标设为 `ascend910b`。
- **`a3` → `ascend910_93`**：`a3` 平台（A3 训练服务器，对应 Ascend 910C/910_93 SoC）映射到 `ascend910_93`，与官方 `build.sh --soc` 参数命名一致。
- **`950` → `ascend950`**：`950` 系列映射到 `ascend950`；该映射可通过 `bash image_build.sh --fla-npu-soc ascend910_93` 等命令整体覆盖。
- **整体语义**：NPU 类型是面向用户的高层概念，`--soc` 是 FLA NPU 构建工具链底层参数；脚本默认按此表做"高层→底层"自动翻译，减少手工错误。

---

### 表 2：`image_build.sh` 构建选项（原文表格逐字还原）

| Option | Default | Description |
| ------ | ------ | ------ |
| `-t, --npu-type TYPE` | `910b` | NPU type. Supported values are `910b`, `a3`, and `950`. |
| `-i, --image-name NAME` | Auto-generated | Full output image name and tag. The script generates one from the configured stack when omitted. |
| `-o, --os OS` | `openeuler24.03` | Base image operating system. Supported values are `openeuler24.03` and `ubuntu22.04`. |
| `-n, --no-cache` | Disabled | Build without the Docker cache. |
| `--base-image IMAGE` | Auto-generated | Full CANN base image name. When set, it is passed to the Dockerfile `FROM` instruction as-is. |
| `--base-image-version VER` | `9.1.0` | CANN version used when generating the default base image name. |
| `--python-version VER` | `3.12` | Python version. |
| `--torch-version VER` | `2.9.0` | PyTorch version. |
| `--torch-npu-version VER` | `2.9.0` | `torch_npu` version. |
| `--torch-whl-url URL` | Empty | Install PyTorch from a specific wheel URL. When omitted, PyTorch is installed by version. |
| `--torch-npu-whl-url URL` | Compatible remote wheel | Install `torch_npu` from a specific wheel URL. Pass an empty string to install it from the configured pip source by version. |
| `--triton-ascend-version VER` | `3.2.1` | Triton-Ascend version. |
| `--mindspeed-bridge-branch VER` | `master` | MindSpeed-Bridge branch, tag, or version. |
| `--mindspeed-ops-branch VER` | `master` | MindSpeed-Ops branch, tag, or version. |
| `--megatron-branch VER` | `core_v0.18.0` | Megatron-LM branch or tag. |
| `--megatron-bridge-branch VER` | `v0.5.0` | Megatron-Bridge branch or tag. |
| `--megatron-adaptor-branch VER` | `core_r0.18.0` | MegatronAdaptor branch or tag. |
| `--transformer-engine-npu-branch VER` | `main` | TransformerEngineNPU branch or tag. |
| `--fla-npu-branch VER` | `v26.1.0` | flash-linear-attention-npu branch or tag. |
| `--fla-npu-soc SOC` | Mapped from the NPU type | Target SoC for flash-linear-attention-npu. Defaults to `ascend910b` for `910b`, `ascend910_93` for `a3`, and `ascend950` for `950`. |
| `--cleanup-on-fail` | Disabled | Remove dangling images and their related containers after a failed build. |
| `-h, --help` | - | Display help and exit. |

**逐行解读（按职能分组）**：

- **NPU 平台与 OS 选择**
  - `-t, --npu-type`：决定 `--fla-npu-soc` 默认映射，并影响自动生成的基础镜像名（与 AscendHub 命名规则相关）。
  - `-o, --os`：原文枚举两个可用值 `openeuler24.03`（默认）与 `ubuntu22.04`。
- **镜像命名与构建行为**
  - `-i, --image-name`：未提供时，脚本根据"配置好的软件栈"自动生成镜像名/标签，保证每次构建都有可追踪的 tag。
  - `--base-image`：当 AscendHub 发布的镜像 tag 与默认命名规则不一致时，传入完整名称并原样作为 Dockerfile `FROM`。
  - `--base-image-version`：仅在自动生成基础镜像名时参与计算，默认 `9.1.0`。
  - `-n, --no-cache`：跳过 Docker 缓存层，常用于排除缓存导致的陈旧依赖问题。
  - `--cleanup-on-fail`：构建失败时清理悬空镜像与容器，节省磁盘并避免污染本地镜像表。
- **Python/PyTorch/torch_npu 安装源**
  - `--python-version`、`--torch-version`、`--torch-npu-version`：按版本号安装时的版本控制开关。
  - `--torch-whl-url`：指定 PyTorch 的 wheel URL；为空时回退到按 `--torch-version` 安装。
  - `--torch-npu-whl-url`：指定 torch_npu 的 wheel URL；传 `""`（空字符串）时回退到默认 pip 源并按 `--torch-npu-version` 安装（其版本遵循变量 `TORCH_NPU_VERSION`）。
- **上游/适配层组件分支**
  - `--mindspeed-bridge-branch`、`--mindspeed-ops-branch`、`--megatron-branch`、`--megatron-bridge-branch`、`--megatron-adaptor-branch`、`--transformer-engine-npu-branch`、`--fla-npu-branch`：均为"branch/tag/version"形式的 git 引用，决定构建时 clone 的代码位置；默认分别为 `master`、`master`、`core_v0.18.0`、`v0.5.0`、`core_r0.18.0`、`main`、`v26.1.0`。
- **Triton-Ascend**
  - `--triton-ascend-version`：默认 `3.2.1`，从 `https://triton-ascend.osinfra.cn/pypi/simple` 安装。
- **FLA NPU SoC 覆盖**
  - `--fla-npu-soc`：默认由 NPU 类型映射（见上表），用于覆盖映射以适配非默认编译目标。
- **帮助**
  - `-h, --help`：列出全部构建选项。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **MegatronAdaptor / TransformerEngineNPU**：作为"Megatron-LM 之上的昇腾适配层"取代原 MindSpeed 角色，与 Megatron-LM（`core_v0.18.0`）形成"Megatron-LM + 适配层"的新基线；其中 TransformerEngineNPU 默认跟随 `main` 分支。
- **MindSpeed-Ops**：尽管 MindSpeed 自身已不安装，但 MindSpeed-Ops 仍被保留，原因是 MindSpeed-Bridge 中的 Qwen3.5-VL GDN kernels 仍 `import mindspeed_ops`，形成"GDN kernels → mindspeed_ops → MindSpeed-Ops"的导入依赖链。
- **flash-linear-attention-npu**：构建过程需在 clone 后 source CANN 环境，然后产出 GDN 自定义算子 run 包和 `torch_custom/fla_npu` wheel；其 `--soc` 与镜像的 NPU 类型联动，算子白名单维护在 `docker/image_build.sh` 的 `FLA_NPU_OPS` 数组。
- **Megatron-Bridge**：作为本仓库命名来源（`mindspeed-bridge`），与 MindSpeed-Bridge 分支（`--mindspeed-bridge-branch`，默认 `master`）并列，构成 Bridge 模型的上层框架支撑。
- **triton-ascend**：Triton 在昇腾上的实现，从独立索引源 `https://triton-ascend.osinfra.cn/pypi/simple` 安装，版本可被 `--triton-ascend-version` 控制。
- **CANN 基础镜像**：作为整个镜像的根，Python 环境直接复用而非通过 Conda 重建；CANN 版本与 NPU 类型、OS 共同决定默认 `FROM` 行的镜像名。

> 注：原文未提供内部链接，外部链接包括 MegatronAdaptor 与 TransformerEngineNPU 的 gitcode 仓库地址，以及 triton-ascend 的 pip 索引源。

---

## 【使用方法】

### 启动构建（原文）
```bash
cd docker
bash image_build.sh
```

### 指定完整基础镜像名（原文）
当 AscendHub 镜像 tag 与默认命名规则不一致时使用：
```bash
bash image_build.sh \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.1.0-910b-openeuler24.03-py3.12
```

### 覆盖 torch_npu wheel URL（原文）
默认 wheel URL 由脚本配置；需要其他 wheel 时：
```bash
bash image_build.sh \
  --torch-npu-whl-url https://gitcode.com/Ascend/pytorch/releases/download/v26.1.0-pytorch2.9.0/torch_npu-2.9.0.post6-cp312-cp312-manylinux_2_28_aarch64.whl
```

### 回退到 pip 源按版本安装 torch_npu（原文）
```bash
bash image_build.sh --torch-npu-whl-url ""
```

### 覆盖 FLA NPU `--soc` 映射（原文）
```bash
bash image_build.sh --fla-npu-soc ascend910_93
```

### 覆盖 triton-ascend 版本（原文）
```bash
bash image_build.sh --triton-ascend-version 3.2.1
```

### 查看全部构建选项（原文）
```bash
bash image_build.sh --help
```

### 网络与代理（原文摘录）
构建默认使用 `--network=host`；当设置了 `http_proxy/https_proxy/HTTP_PROXY/HTTPS_PROXY/no_proxy/NO_PROXY` 任一环境变量，脚本会自动将其作为 build argument 透传给 Docker build。

### 中文版本详细说明
原文指向 `OVERVIEW.zh.md`（`See OVERVIEW.zh.md for detailed Chinese instructions`）。
