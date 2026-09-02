# MindSpeed CI Docker 镜像概述

> 仓 `mindspeed` · 路径 `ci/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/ci/OVERVIEW.zh.md

# ci/OVERVIEW.zh.md 深度解读

## 【定位】

这篇文档定义并交付了 MindSpeed 项目的 **CI 专用 Docker 镜像（`mindspeed-ci`）**，统一规范其基础镜像选型、组件版本、Tag 命名、构建脚本、运行参数，使 MindSpeed Core、MindSpeed-LLM、vLLM、vLLM-ascend、verl 等多组件能在同一可复现的昇腾 NPU 环境中完成持续集成与系统测试（ST）。

---

## 【技术要点】

1. **统一构建入口**：以 `ci/build.sh` 为唯一构建入口，通过 `-t/-o/-i/-n/--base-image/--python-version/--torch-version/--mindspeed-branch/--megatron-branch/--mindspeed-llm-branch/--vllm-version/--vllm-ascend-version/--verl-version/--cleanup-on-fail` 等参数实现"一行命令、可配置版本"的多组件拼装。
2. **可配置 CANN 基础镜像**：默认 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.1-910b-openeuler24.03-py3.12`，支持通过 `--base-image-version` 或完整 `--base-image`（原样传入，tag 必须与已发布 CANN 镜像名一致）切换；操作系统支持 `openeuler24.03` / `ubuntu22.04`，NPU 支持 `a3` / `910b`（小写）。
3. **Tag 模板强制规范**：`{版本号}-{芯片信息}-{操作系统}-{Python标签}-{架构类型}`，例如 `master-910b-openeuler24.03-py3.12-aarch64`；其中"芯片信息"字段强制小写，且与 CANN 基础镜像名完全一致才能复用。
4. **多组件版本与安装路径锁定**：CANN 9.0.1（`/usr/local/Ascend`）、PyTorch 2.9.0、torch_npu 2.9.0、Megatron-LM `core_v0.12.1`（`/mindspeed_ci_deps/Megatron-LM`）、MindSpeed/MindSpeed-LLM `master`、vLLM `v0.18.0`、vLLM-ascend `releases/v0.18.0`、verl `v0.7.0`、mbridge `latest`、transformers `4.57.1`。
5. **构建期版本补丁（修复已知不兼容）**：
   - **verl ↔ vLLM API 兼容性补丁**：`WorkerWrapperBase(vllm_config=...)` → `WorkerWrapperBase(rpc_rank=0)`；`execute_method` 移除，改用 `getattr(self.inference_engine, method)(...)`。
   - **triton-ascend 版本修正**：`3.2.0rc4`（verl 的 `requirements-npu.txt` 写死但镜像源不可用）→ `3.2.1`。
   - **mbridge 安装顺序**：在 verl 之后安装，避免依赖冲突。
   - **transformers 末端锁定**：`4.57.1` 在最后一个 `RUN` 步骤中固定，防止中间步骤被升级。
   - **flash_attn 虚拟命名空间包**：在 MindSpeed 的 `requirements_basic.py` 中注册 `flash_attn.flash_attn_interface.flash_attn_unpadded_func` 与 `flash_attn.ops.triton.rotary.apply_rotary`，规避 vLLM 的 `find_spec` 检测冲突。
6. **非特权容器运行约定**：CI 环境禁止 `--privileged`，改用 `--pid=host --network host --ipc host --cgroupns host --security-opt seccomp=unconfined` + `--cap-add` 五项能力（`CAP_SYS_RESOURCE/CAP_SYS_ADMIN/CAP_MKNOD/CAP_SYS_PTRACE/CAP_IPC_LOCK`）并显式 `--device` 注入 `/dev/davinci0–7` + `davinci_manager` + `devmm_svm` + `hisi_hdc` 设备。

---

## 【关键机制与数据】

- **工作目录与卷挂载（原文）**：默认工作目录 `/mindspeed_ci_deps/MindSpeed`；运行示例挂载了 `/mindspeed_ci_deps/models`、`/home/dataset`、`/mindspeed_ci_deps/MindSpeed`、`/usr/local/Ascend/driver`、`/usr/local/Ascend/firmware`、`/usr/local/sbin/`，并设置 `--shm-size=32G`、`ASCEND_VISIBLE_DEVICES=0-7`。
- **环境变量（原文）**：`ENABLE_ATB=1` 与 `PYTHONPATH` 已预配置，专用于 NPU 开发。
- **归档文件（原文）**：`ci/Dockerfile`、`ci/build.sh`、`ci/configure_apt_repo.sh`、`ci/configure_yum_repo.sh`、`ci/configure_repo.sh`（支持 apt/yum 双源）。
- **镜像性质（原文）**："此镜像专用于 CI/测试场景，不适用于生产部署。"
- **性能数据**：原文无任何 benchmark/吞吐量/时延数字，故不展开。
- **数据流（按原文描述）**：`build.sh` → 选定 CANN 基础镜像 → 按组件版本克隆仓库到 `/mindspeed_ci_deps/` → 应用上述补丁（verl/vLLM API、triton-ascend、mbridge 顺序、transformers 锁、flash_attn 命名空间）→ 产出 `mindspeed-ci:TAG` → 通过 `docker run` 注入 NPU 设备与卷，启动后默认进入 `/mindspeed_ci_deps/MindSpeed` 执行测试。

---

## 【表格解读】

### 表 1：快速参考

| 项目 | 说明 |
| ------ | ------ |
| 镜像名称 | `mindspeed-ci` |
| 源码仓库 | [https://gitcode.com/Ascend/MindSpeed](https://gitcode.com/Ascend/MindSpeed) |
| Dockerfile 路径 | `ci/Dockerfile` |
| 默认场景 | MindSpeed CI 测试（包含 MindSpeed-LLM、vLLM、vLLM-ascend、verl，用于 ST 测试） |
| 基础镜像 | 可配置 CANN 镜像，默认 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.1-910b-openeuler24.03-py3.12` |
| 默认工作目录 | `/mindspeed_ci_deps/MindSpeed` |

**逐行解读**：
- **镜像名称**：`mindspeed-ci` 即后续 `docker run` 中 `REPOSITORY:TAG` 的 REPOSITORY 段；与 Tag 组合形成可寻址单元。
- **源码仓库**：所有归档脚本与 Dockerfile 都源于此仓库 `ci/` 目录。
- **Dockerfile 路径**：构建入口文件实际位置为 `ci/Dockerfile`（注意与"源码仓库根目录"区分）。
- **默认场景**：明确说明这是一张**集成测试 + 系统测试**镜像，并显式列出下游模块（MindSpeed-LLM、vLLM、vLLM-ascend、verl）——这意味着镜像的组件拓扑不是孤立的训练栈，而是"训练 + 推理 + RL"全链路。
- **基础镜像**：默认锚定 CANN 9.0.1 + 910b + openEuler 24.03 + Python 3.12，可通过参数覆盖。
- **默认工作目录**：`/mindspeed_ci_deps/MindSpeed`，与运行示例中的 `-v /mindspeed_ci_deps/MindSpeed:/mindspeed_ci_deps/MindSpeed` 卷挂载一一对应，便于源码热更新。

### 表 2：包含的组件

| 组件 | 默认版本 | 镜像内路径 |
| ------ | ------ | ------ |
| CANN (基础镜像) | 9.0.1 | `/usr/local/Ascend` |
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

**逐行解读**：
- **CANN 9.0.1** 作为基础镜像层，提供昇腾运行时与算子库；安装于 `/usr/local/Ascend`，运行示例中 `/usr/local/Ascend/driver` 与 `/usr/local/Ascend/firmware` 必须从宿主机挂载回容器，以保证驱动与固件版本匹配。
- **PyTorch 2.9.0 / torch_npu 2.9.0** 通过 pip 安装，必须与 CANN 版本协同（这是 `--torch-version` 与 `--torch-npu-version` 参数存在的原因）。
- **Megatron-LM core_v0.12.1** 是 MindSpeed 加速所依赖的上游基线；通过 git 检出到 `/mindspeed_ci_deps/Megatron-LM`。
- **MindSpeed / MindSpeed-LLM master**：两份源码均落盘到 `/mindspeed_ci_deps/` 下，方便容器内直接编辑或挂载覆盖。
- **vLLM v0.18.0 + vLLM-ascend releases/v0.18.0**：推理引擎与其昇腾后端版本号一一对齐（v0.18.0 ↔ releases/v0.18.0），这是文档后文"API 不兼容补丁"发生的前提。
- **verl v0.7.0**：RL 训练框架，其 `requirements-npu.txt` 与 vLLM 的 API 冲突是本镜像构建期补丁的核心来源。
- **mbridge latest**：在 verl 之后 pip 安装，用作 Megatron bridge 适配层。
- **transformers 4.57.1**：通过末尾 `RUN` 步骤硬锁版本，避免任何中间安装流程静默升级破坏 API。

### 表 3：构建参数

| 参数 | 说明 | 默认值 |
| ------ | ------ | ------ |
| `-t, --npu-type` | NPU 类型：`a3` 或 `910b` | `910b` |
| `-o, --os` | 操作系统：`openeuler24.03` 或 `ubuntu22.04` | `openeuler24.03` |
| `-i, --image-name` | 镜像名称（默认根据分支和配置自动生成） | 自动 |
| `-n, --no-cache` | 不使用缓存构建 | 关闭 |
| `--base-image-version` | CANN 基础镜像版本 | `9.0.1` |
| `--base-image` | 完整 CANN 基础镜像名，优先级高于 `--base-image-version`；会原样传入 | 空 |
| `--python-version` | CANN 基础镜像中的 Python 标签 | `3.12` |
| `--torch-version` | PyTorch 版本 | `2.9.0` |
| `--torch-npu-version` | torch_npu 版本 | `2.9.0` |
| `--mindspeed-branch` | 克隆 MindSpeed 使用的分支、标签或 ref | `master` |
| `--megatron-branch` | checkout Megatron-LM 使用的分支、标签或 ref | `core_v0.12.1` |
| `--mindspeed-llm-branch` | checkout MindSpeed-LLM 使用的分支、标签或 ref | `master` |
| `--vllm-version` | vLLM 版本 | `v0.18.0` |
| `--vllm-ascend-version` | vLLM-ascend 版本 | `releases/v0.18.0` |
| `--verl-version` | verl 版本 | `v0.7.0` |
| `--cleanup-on-fail` | 构建失败时清理悬空镜像和对应容器 | 关闭 |

**逐行解读**：
- **`-t` / `-o` / `--python-version`** 共同决定基础镜像在 Tag 上的后缀，必须相互匹配（如 `910b + openeuler24.03 + 3.12`）。
- **`--base-image` 优先级高于 `--base-image-version`**：当用户传入完整字符串（如 `swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.1-910b-openeuler24.03-py3.12`）时，脚本会**原样透传**并尽量从 tag 自动反推 NPU/OS/Python 参数。
- **`--mindspeed-branch` / `--megatron-branch` / `--mindspeed-llm-branch`** 都接受 git ref（分支/标签/commit），因此既可复现发行版，也可指向开发分支。
- **`--vllm-version` 与 `--vllm-ascend-version`** 默认值已对齐（`v0.18.0` ↔ `releases/v0.18.0`），保证二者 API 版本协同。
- **`--cleanup-on-fail`** 用于 CI 流水线在构建失败时清理悬挂资源，避免节点磁盘被占满。
- **`-n, --no-cache`** 是构建调试常用开关，绕过 Docker 层缓存。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 MindSpeed Core（主仓库本体）**：镜像以 MindSpeed 源码（`master` 分支）为底，并在 `requirements_basic.py` 中注册虚拟 `flash_attn` 命名空间包，规避与 vLLM 的 `find_spec` 冲突——表明 MindSpeed 需在此 CI 场景下"假装存在 flash_attn"才能让 vLLM 加载成功。
- **与 MindSpeed-LLM**：作为 LLM 训练/微调栈的默认组件，源码与 MindSpeed 同克隆到 `/mindspeed_ci_deps/MindSpeed-LLM`。
- **与 Megatron-LM**：作为上游基线（`core_v0.12.1`），是 MindSpeed 加速 patch 的施加目标。
- **与 vLLM / vLLM-ascend**：推理引擎栈，版本号必须严格同步（`v0.18.0` ↔ `releases/v0.18.0`），且接受 Dockerfile 的 API 兼容性补丁（`WorkerWrapperBase` 签名 + `execute_method` 替换）。
- **与 verl**：RL 框架，其 `requirements-npu.txt` 锁定了不可用的 `triton-ascend==3.2.0rc4`，需由 Dockerfile 改写为 `3.2.1`；同时引入 mbridge 作为 Megatron bridge，且 mbridge 必须在 verl 之后安装。
- **与 mbridge**：依赖桥接层，安装顺序敏感（verl 之后），由 `latest` 标签管理。
- **与 transformers**：通过末尾 `RUN` 硬锁 `4.57.1`，是整张镜像的"版本钉子"，防止上游组件的传递依赖升级破坏 API。
- **与昇腾 CANN / 驱动 / 固件**：基础镜像提供 CANN 9.0.1；运行容器必须从宿主机 bind-mount `/usr/local/Ascend/driver` 与 `/usr/local/Ascend/firmware`，否则 NPU 设备无法被容器内程序访问。
- **CI 平台约束**：通过 `--pid=host --network host --ipc host --cgroupns host` + 五项 `--cap-add` + 显式 `--device` 注入替代 `--privileged`，反映 Kubernetes 类 CI 环境的非特权容器策略。
- **上下游文档**：文末未提供内部链接（标注为"无"）。

---

## 【使用方法】

**默认构建**：
```bash
cd ci
bash build.sh
```

**显式指定 NPU 与 OS（910b + openEuler + CANN 9.0.1）**：
```bash
cd ci
bash build.sh -t 910b -o openeuler24.03
```

**使用完整基础镜像名构建（脚本自动从 tag 识别 NPU/OS/Python）**：
```bash
cd ci
bash build.sh \
  --base-image swr.cn-south-1.myhuaweicloud.com/ascendhub/cann:9.0.1-910b-openeuler24.03-py3.12
```

**指定自定义组件版本**：
```bash
cd ci
bash build.sh \
  --mindspeed-branch master \
  --vllm-version v0.18.0 \
  --verl-version v0.7.0
```

**运行容器（非特权方式，注入 0–7 号 NPU + 管理/共享内存设备）**：
```bash
docker run -itd \
  --name mindspeed-ci \
  --pid=host --network host --ipc host --cgroupns host \
  --security-opt seccomp=unconfined \
  --cap-add=CAP_SYS_RESOURCE --cap-add=CAP_SYS_ADMIN \
  --cap-add=CAP_MKNOD --cap-add=CAP_SYS_PTRACE --cap-add=CAP_IPC_LOCK \
  -e ASCEND_VISIBLE_DEVICES=0-7 \
  --device=/dev/davinci0 --device=/dev/davinci1 --device=/dev/davinci2 \
  --device=/dev/davinci3 --device=/dev/davinci4 --device=/dev/davinci5 \
  --device=/dev/davinci6 --device=/dev/davinci7 \
  --device=/dev/davinci_manager --device=/dev/devmm_svm --device=/dev/hisi_hdc \
  --security-opt label=disable --shm-size=32G \
  -v /mindspeed_ci_deps/models:/mindspeed_ci_deps/models \
  -v /home/dataset:/home/dataset \
  -v /mindspeed_ci_deps/MindSpeed:/mindspeed_ci_deps/MindSpeed \
  -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
  -v /usr/local/Ascend/firmware:/usr/local/Ascend/firmware \
  -v /usr/local/sbin/:/usr/local/sbin/ \
  mindspeed-ci:master-910b-openeuler24.03-py3.12-aarch64
```

**进入已启动容器**：
```bash
docker exec -it mindspeed-ci /bin/bash
```
