# MindSpeed CI Docker Overview

> 仓 `mindspeed` · 路径 `ci/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/ci/OVERVIEW.md

# MindSpeed CI Docker Overview 深度解读

## 【定位】

这篇文档是 MindSpeed（昇腾大模型加速库）CI 集成测试 Docker 镜像的构建与使用说明，定义了 `mindspeed-ci` 镜像的默认组件、版本、标签规范、构建参数以及运行配置，目的是为 MindSpeed Core 及上下游组件（MindSpeed-LLM、vLLM、vLLM-ascend、verl、Megatron-LM）提供一套统一、可复现的 ST（系统测试）环境。

## 【技术要点】

- **镜像标识与基础镜像**：镜像名固定为 `mindspeed-ci`，基础镜像默认 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.1-910b-openeuler24.03-py3.12`，CANN 安装于 `/usr/local/Ascend`，可通过 `--base-image` 或 `--base-image-version` 切换。
- **标签模板**：`{version}-{chip_info}-{os}-{python_tag}-{arch}`，其中 `chip_info` 必须小写（如 `a3`、`910b`），示例 `master-910b-openeuler24.03-py3.12-aarch64`。
- **统一构建入口**：`ci/build.sh` 支持 NPU 类型（`a3`/`910b`）、OS（`openeuler24.03`/`ubuntu22.04`）、Python（`3.12`）、CANN 版本（`9.0.1`）、PyTorch/torch_npu（`2.9.0`）、Megatron-LM（`core_v0.12.1`）、vLLM（`v0.18.0`）、vLLM-ascend（`releases/v0.18.0`）、verl（`v0.7.0`）等组件版本可配。
- **关键运行时补丁**：verl v0.7.0 与 vLLM v0.18.0 存在 API 不兼容，Dockerfile 在构建时对 `WorkerWrapperBase` 构造签名与 `execute_method` 方法打补丁；并把 `requirements-npu.txt` 中的 `triton-ascend==3.2.0rc4` 改写为 `triton-ascend==3.2.1`。
- **依赖顺序与版本钉死**：mbridge 在 verl 之后安装以规避依赖冲突；transformers 在最终 `RUN` 步骤钉死为 `4.57.1`，防止被中间步骤升级；MindSpeed 通过 `requirements_basic.py` 注册 `flash_attn.flash_attn_interface.flash_attn_unpadded_func` 与 `flash_attn.ops.triton.rotary.apply_rotary` 等 dummy namespace 包，避免与 vLLM 的 `find_spec` 检测冲突。
- **非特权运行模式**：CI 环境不允许特权容器，文档给出 `--device` + `--cap-add`（`CAP_SYS_RESOURCE`、`CAP_SYS_ADMIN`、`CAP_MKNOD`、`CAP_SYS_PTRACE`、`CAP_IPC_LOCK`）替代 `--privileged` 的运行模板，并挂载 `/dev/davinci0–7`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 与 `/usr/local/Ascend/{driver,firmware}`，以及 `--shm-size=32G`。

## 【关键机制与数据】

- **组件与路径数据（原文）**：CANN 9.0.1 位于 `/usr/local/Ascend`；Megatron-LM `core_v0.12.1` 位于 `/mindspeed_ci_deps/Megatron-LM`；MindSpeed/MindSpeed-LLM `master` 位于 `/mindspeed_ci_deps/MindSpeed`、`/mindspeed_ci_deps/MindSpeed-LLM`；vLLM `v0.18.0` 位于 `/mindspeed_ci_deps/vllm`；vLLM-ascend `releases/v0.18.0` 位于 `/mindspeed_ci_deps/vllm-ascend`；verl `v0.7.0` 位于 `/mindspeed_ci_deps/verl`；mbridge `latest`、transformers `4.57.1` 通过 pip 安装；默认工作目录 `/mindspeed_ci_deps/MindSpeed`。
- **镜像 tag 解析（原文）**：`--base-image` 完整值原样透传，脚本在可能时从 tag 自动识别 NPU/OS/Python；其优先级高于 `--base-image-version`。
- **API 兼容补丁（原文）**：`WorkerWrapperBase` 构造从 `WorkerWrapperBase(vllm_config=self.vllm_config)` 改为 `WorkerWrapperBase(rpc_rank=0)`；删除 `execute_method`，改用 `getattr(self.inference_engine, method)(...)` 调用。
- **运行时环境变量（原文）**：镜像内预配置 `ENABLE_ATB=1` 与 `PYTHONPATH`，便于 NPU 开发。
- **用途边界（原文）**：该镜像仅供 CI/测试场景使用，不建议用于生产部署。

## 【表格解读】

### 表格 1 — Quick Reference（逐字还原）

| Item | Description |
| ------ | ------ |
| Image Name | `mindspeed-ci` |
| Repository | https://gitcode.com/Ascend/MindSpeed |
| Dockerfile Path | `ci/Dockerfile` |
| Default Scenario | MindSpeed CI testing (includes MindSpeed-LLM, vLLM, vLLM-ascend, verl for ST tests) |
| Base Image | Configurable CANN image, default `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.1-910b-openeuler24.03-py3.12` |
| Default Working Directory | `/mindspeed_ci_deps/MindSpeed` |

解读：该表给出镜像的最少必要标识信息。`Default Scenario` 明确镜像为集成/ST 测试而生，覆盖 MindSpeed-LLM、vLLM、vLLM-ascend、verl 四个上下游；Base Image 默认锁定 CANN 9.0.1 + 910b + openEuler 24.03 + Python 3.12，与下文 Build Options 的默认值一致；工作目录落在 `/mindspeed_ci_deps/MindSpeed`，与 Included Components 表中 MindSpeed 的克隆路径对应。

### 表格 2 — Included Components（逐字还原）

| Component | Default Version | Path in Image |
| ------ | ------ | ------ |
| CANN (Base Image) | 9.0.1 | `/usr/local/Ascend` |
| PyTorch | 2.9.0 | pip |
| torch_npu | 2.9.0 | pip |
| Megatron-LM | core_v0.12.1 | `/mindspeed_ci_deps/Megatron-LM` |
| MindSpeed | master | `/mindspeed_ci_deps/MindSpeed` |
| MindSpeed-LLM | master | `/mindspeed_ci_deps/MindSpeed-LLM` |
| vLLM | v0.18.0 | `/mindspeed_ci_deps/vllm` |
| vLLM-ascend | releases/v0.18.0 | `/mindspeed_ci_deps/vllm-ascend` |
| verl | v0.7.0 | `/mindspeed_ci_deps/verl` |
| mbridge | latest | pip |
| transformers | 4.57.1 | pip |

解读：表中 11 个组件共同构成 ST 测试运行时栈。CANN 作为底层；PyTorch 2.9.0 与 torch_npu 2.9.0 提供 NPU 加速算子；Megatron-LM core_v0.12.1 与 MindSpeed master 构成训练核心；vLLM v0.18.0 + vLLM-ascend releases/v0.18.0 构成推理路径；verl v0.7.0 作为 RL 训练入口并依赖 vLLM 推理引擎；mbridge (latest) 是 verl 运行时所需的 Megatron bridge；transformers 4.57.1 在最终 RUN 步骤被钉死以防止被中间步骤升级。MindSpeed/MindSpeed-LLM 默认 `master` 而非常规 release tag，说明镜像用于跟踪主干 CI。

### 表格 3 — Build Options（逐字还原）

| Option | Description | Default |
| ------ | ------ | ------ |
| `-t, --npu-type` | NPU type: `a3` or `910b` | `910b` |
| `-o, --os` | Operating system: `openeuler24.03` or `ubuntu22.04` | `openeuler24.03` |
| `-i, --image-name` | Image name (default: auto-generated from branch + config) | auto |
| `-n, --no-cache` | Build without cache | off |
| `--base-image-version` | CANN base image version | `9.0.1` |
| `--base-image` | Full CANN base image name, higher priority than `--base-image-version`; passed through unchanged | empty |
| `--python-version` | Python tag in the CANN base image | `3.12` |
| `--torch-version` | PyTorch version | `2.9.0` |
| `--torch-npu-version` | torch_npu version | `2.9.0` |
| `--mindspeed-branch` | MindSpeed branch/tag/ref to clone | `master` |
| `--megatron-branch` | Megatron-LM branch/tag/ref to checkout | `core_v0.12.1` |
| `--mindspeed-llm-branch` | MindSpeed-LLM branch/tag/ref to checkout | `master` |
| `--vllm-version` | vLLM version | `v0.18.0` |
| `--vllm-ascend-version` | vLLM-ascend version | `releases/v0.18.0` |
| `--verl-version` | verl version | `v0.7.0` |
| `--cleanup-on-fail` | Clean dangling images/containers if build fails | off |

解读：Build Options 给出一站式可配置矩阵。NPU/OS 维度负责切换 `chip_info` 与 OS 段（`a3`/`910b`、`openeuler24.03`/`ubuntu22.04`）；CANN 维度分两层：`--base-image-version` 用于指定版本号、`--base-image` 用于透传完整镜像名且优先级更高；Python 仅影响 CANN base image tag 内的 `py3.12`；其余 `--*-version`/`--*-branch` 全部与 Included Components 表中的 Default Version 一一对应；`--cleanup-on-fail` 提供失败时的镜像/容器清理钩子。整体设计体现了「单一镜像、多组件可裁剪」的 CI 构建策略。

## 【公式解读】

原文无公式。

## 【关联】

- **训练核心链路**：MindSpeed master（位于 `/mindspeed_ci_deps/MindSpeed`）作为加速库，依赖 Megatron-LM core_v0.12.1 提供分布式训练框架原语；MindSpeed-LLM master 作为上层 LLM 训练入口，二者通过 `/mindspeed_ci_deps/MindSpeed-LLM` 共存于同一镜像。
- **推理链路**：vLLM v0.18.0 与 vLLM-ascend releases/v0.18.0 组合提供 NPU 上的推理服务，是 verl 训练中的 rollout 引擎；文档特别标注 verl ↔ vLLM 之间存在 `WorkerWrapperBase` 与 `execute_method` 两处 API 兼容问题，由 Dockerfile 在构建期打补丁解决。
- **RL 训练依赖链**：verl v0.7.0 依赖 mbridge（Megatron bridge）作为训练侧桥接，并通过 triton-ascend 3.2.1（已从 rc4 替换）使用 NPU kernel；mbridge 必须在 verl 安装后再装，否则会触发依赖冲突。
- **命名空间兼容性**：MindSpeed 自身 `requirements_basic.py` 注册的 dummy `flash_attn` namespace 包（`flash_attn.flash_attn_interface.flash_attn_unpadded_func`、`flash_attn.ops.triton.rotary.apply_rotary`）直接服务于 vLLM 的 `find_spec` 检测，避免因 vLLM 在导入期探查 `flash_attn` 子模块而与 MindSpeed 的 stub 发生冲突。
- **transformers 约束**：transformers 4.57.1 在最终 `RUN` 步骤被钉死，覆盖其上所有组件（Megatron-LM、verl、vLLM、MindSpeed-LLM）的间接拉取，确保 API 形态在整张栈内一致。
- **环境与权限**：镜像预置 `ENABLE_ATB=1` 与 `PYTHONPATH`，为 NPU 上的 ATB 加速与模块解析提供基础；运行模板通过 `--cap-add` + `--device` 取代 `--privileged`，挂载 `/usr/local/Ascend/{driver,firmware}` 与 `/dev/davinci*`/`davinci_manager`/`devmm_svm`/`hisi_hdc`，体现与 Ascend 驱动栈的紧耦合。

## 【使用方法】

### 构建（原文）

```bash
cd ci
bash build.sh
```

默认配置即 910b + openEuler 24.03 + CANN 9.0.1 + Python 3.12。

```bash
cd ci
bash build.sh -t 910b -o openeuler24.03
```

显式指定 NPU 与 OS。

```bash
cd ci
bash build.sh \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.1-910b-openeuler24.03-py3.12
```

使用完整 base image 名，脚本会自动从 tag 推断 NPU/OS/Python（原文）。

```bash
cd ci
bash build.sh \
  --mindspeed-branch master \
  --vllm-version v0.18.0 \
  --verl-version v0.7.0
```

覆盖 MindSpeed/vLLM/verl 版本（原文）。

### 运行（原文）

镜像 tag 形如 `mindspeed-ci:master-910b-openeuler24.03-py3.12-aarch64`：

```bash
docker run -itd \
  --name mindspeed-ci \
  --pid=host \
  --network host \
  --ipc host \
  --cgroupns host \
  --security-opt seccomp=unconfined \
  --cap-add=CAP_SYS_RESOURCE \
  --cap-add=CAP_SYS_ADMIN \
  --cap-add=CAP_MKNOD \
  --cap-add=CAP_SYS_PTRACE \
  --cap-add=CAP_IPC_LOCK \
  -e ASCEND_VISIBLE_DEVICES=0-7 \
  --device=/dev/davinci0 \
  --device=/dev/davinci1 \
  --device=/dev/davinci2 \
  --device=/dev/davinci3 \
  --device=/dev/davinci4 \
  --device=/dev/davinci5 \
  --device=/dev/davinci6 \
  --device=/dev/davinci7 \
  --device=/dev/davinci_manager \
  --device=/dev/devmm_svm \
  --device=/dev/hisi_hdc \
  --security-opt label=disable \
  --shm-size=32G \
  -v /mindspeed_ci_deps/models:/mindspeed_ci_deps/models \
  -v /home/dataset:/home/dataset \
  -v /mindspeed_ci_deps/MindSpeed:/mindspeed_ci_deps/MindSpeed \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/Ascend/firmware:/usr/local/Ascend/firmware \
  -v /usr/local/sbin/:/usr/local/sbin/ \
  mindspeed-ci:master-910b-openeuler24.03-py3.12-aarch64
```

进入容器（原文）：

```bash
docker exec -it mindspeed-ci /bin/bash
```

### 注意事项（原文）

- CI 环境不允许特权容器，必须使用 `--device` + `--cap-add` 模式，而非 `--privileged`。
- 该镜像仅供 CI/测试场景，不建议用于生产部署。
- 许可证：MindSpeed 主代码遵循 Apache License 2.0；镜像内其他软件（如 Bash、间接依赖）的许可证由使用者自行核查合规性。
