# Agent SDK

> 仓 `agentsdk` · 路径 `docker/aura/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/docker/aura/OVERVIEW.zh.md

# Agent SDK / Aura 镜像文档深度解读

## 【定位】

这篇文档解决的是"Aura 镜像怎么选、怎么跑"的问题——即在 Ascend AgentSDK 项目下，告诉用户 Aura（Agentic Ultra-fast Reinforcement Architecture）框架的 Docker 镜像 Tag 命名规范、可用的具体镜像/Dockerfile、前置驱动与容器运行所需的设备挂载方式，以及支持的硬件平台。

## 【技术要点】

1. **Aura 框架定位**：面向基础模型的"训推调一体化"框架，基于任务轨迹和奖励信号，通过强化学习等方法做后训练，逐步使模型具备规划、工具使用、长程决策等 Agent 化能力；通过统一抽象接口兼容多种训练引擎、推理引擎与 Agent 框架，支持自定义模型与工具链接入。

2. **镜像 Tag 命名规范**（原文给出格式与示例）：
   - 格式：`<AgentSDK版本>-<CANN版本>-<pytorch版本>-<芯片系列>-<操作系统>-<python版本>`
   - 6 字段示例值：AgentSDK版本 `26.1.0`、CANN `cann9.0.0`、PyTorch `torch_npu2.7.1` / `torch_npu2.9.0.post2`、芯片系列 `910`/`910b`/`a3`/`310p`、OS `ubuntu22.04`/`openeuler24.03`、Python `py3.11`。

3. **CANN 9.0.0 + 26.1.0 Agent SDK 镜像清单**：4 个 Tag 组合，全部为 `toolkit + Agent SDK` 组合，覆盖 `910b`/`a3` 两个芯片系列 × `ubuntu22.04`/`openeuler24.03` 两个操作系统，统一使用 `torch_npu2.9.0`，配套 4 个 Dockerfile（910b/a3 × ubuntu/openeuler）。

4. **前置驱动要求**：宿主机必须安装与容器内 CANN 版本兼容的 NPU 驱动（参照 CANN 兼容性矩阵）；Docker 版本建议不低于 `24.0.x`。

5. **容器设备挂载机制**：
   - **NPU 加速卡**：通过 `--device` 挂载 `/dev/davinci`，按需挂载（示例中挂载 `/dev/davinci0` 到 `/dev/davinci15` 共 16 个）；
   - **NPU 管理设备**：必须全部挂载 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`；
   - **驱动与工具链只读挂载**：`/usr/local/Ascend/driver`、`/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/etc/ascend_install.info`、时区文件 `/usr/share/zoneinfo/Asia/Shanghai`、`/usr/local/sbin`；
   - **运行时参数**：`--network host`、`--shm-size=500g`、容器入口 `sleep infinity`、镜像内默认工作目录 `/home/work`（不要挂载整个 `/home`）。

6. **支持的硬件范围**：`Atlas 910`（产品示例 `Atlas 800I A2`，架构 `ARM64 / x86_64`）、`Atlas A3`（产品示例 `Atlas 800I A3`，架构 `ARM64 / x86_64`）。

## 【关键机制与数据】

- **原文：Aura 工作原理**——Aura 基于"任务轨迹 + 奖励信号"对基础模型进行持续优化，通过后训练（强化学习等优化方法）逐步赋予模型规划、工具使用、长程决策三类 Agent 化能力。框架对外以"统一抽象接口"形式屏蔽底层训练引擎、推理引擎与 Agent 框架的差异，从而支持灵活接入自定义模型与工具链。

- **原文：NPU 数量与设备挂载的对应关系**——以 Atlas A3 为例，整机具备 16 个 NPU，因此示例代码中挂载了 16 个 `/dev/davinci*` 设备 ID（`davinci0`～`davinci15`），每个设备 ID 对应一个 NPU；这意味着容器侧的设备 ID 数量需与目标机型 NPU 数量一致。

- **原文：共享内存配置**——示例 `docker run` 命令中使用 `--shm-size=500g`，为容器提供 500 GB 共享内存空间，配合 NPU 多卡训练/推理时的张量通信需求。

- **原文：镜像内容组合**——4 个 Tag 对应的镜像内容均为 `toolkit + Agent SDK`，即在同一基础镜像中同时提供 CANN toolkit 与 Agent SDK 软件包。

- **原文：工作目录与挂载约束**——镜像内默认工作目录为 `/home/work`，因此**不建议挂载整个 `/home`** 目录，以免覆盖默认工作空间或引发权限冲突。

- **原文：性能/吞吐数据**——文档未提供任何性能、吞吐、训练时延、精度等量化指标。

## 【表格解读】

### 表 1：Tag 字段规范表（原文逐字还原）

| 字段           | 示例值                                      | 说明            |
|--------------|------------------------------------------|---------------|
| `AgentSDK版本` | `26.1.0`                                 | Agent SDK 版本号 |
| `CANN版本`     | `cann9.0.0`                              | CANN 版本       |
| `pytorch版本`  | `torch_npu2.7.1`, `torch_npu2.9.0.post2` | PyTorch 版本    |
| `芯片系列`       | `910`, `910b`, `a3`, `310p`              | 目标芯片系列        |
| `操作系统`       | `ubuntu22.04`, `openeuler24.03`          | 操作系统          |
| `python版本`   | `py3.11`                                 | Python 版本     |

**逐行解读**：
- **AgentSDK版本**：第 1 字段，标识 Agent SDK 自身版本号，示例为 `26.1.0`；与第 3、4、5、6 字段组合形成完整 Tag，决定软件栈基线。
- **CANN版本**：第 2 字段，标识容器内 CANN 版本，示例为 `cann9.0.0`；CANN 版本需与宿主机驱动版本匹配，是镜像选型的关键依据。
- **pytorch版本**：第 3 字段，标识 PyTorch + NPU 适配版本，示例给出 `torch_npu2.7.1` 与 `torch_npu2.9.0.post2` 两个候选，对应不同 torch_npu 适配线。
- **芯片系列**：第 4 字段，标识目标芯片系列，可选 `910`、`910b`、`a3`、`310p`；决定了后续 torch_npu/CANN 算子的支持范围。
- **操作系统**：第 5 字段，标识宿主机/容器 OS，可选 `ubuntu22.04` 或 `openeuler24.03`；影响系统库与二进制兼容性。
- **python版本**：第 6 字段，标识 Python 版本，示例 `py3.11`；决定上层 Python 依赖的解释器版本。

### 表 2：CANN 9.0.0 + 26.1.0 Agent SDK 镜像清单（原文逐字还原）

| Tag                                                          | Dockerfile                                                                              | 镜像内容                |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------------|---------------------|
| `26.1.0-cann9.0.0-torch_npu2.9.0-910b-ubuntu22.04-py3.11`    | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.910b.ubuntu)    | toolkit + Agent SDK |
| `26.1.0-cann9.0.0-torch_npu2.9.0-a3-ubuntu22.04-py3.11`      | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.a3.ubuntu)      | toolkit + Agent SDK |
| `26.1.0-cann9.0.0-torch_npu2.9.0-910b-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.910b.openeuler) | toolkit + Agent SDK |
| `26.1.0-cann9.0.0-torch_npu2.9.0-a3-openeuler24.03-py3.11`   | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.a3.openeuler)   | toolkit + Agent SDK |

**逐行解读**：
- **第 1 行**：`26.1.0-cann9.0.0-torch_npu2.9.0-910b-ubuntu22.04-py3.11` ——面向 `910b` 芯片 + `ubuntu22.04` 的镜像，Dockerfile 位于 `docker/aura/Dockerfile.910b.ubuntu`，内容为 `toolkit + Agent SDK`。
- **第 2 行**：`26.1.0-cann9.0.0-torch_npu2.9.0-a3-ubuntu22.04-py3.11` ——面向 `a3` 芯片 + `ubuntu22.04` 的镜像，Dockerfile 位于 `docker/aura/Dockerfile.a3.ubuntu`，内容为 `toolkit + Agent SDK`。
- **第 3 行**：`26.1.0-cann9.0.0-torch_npu2.9.0-910b-openeuler24.03-py3.11` ——面向 `910b` 芯片 + `openeuler24.03` 的镜像，Dockerfile 位于 `docker/aura/Dockerfile.910b.openeuler`，内容为 `toolkit + Agent SDK`。
- **第 4 行**：`26.1.0-cann9.0.0-torch_npu2.9.0-a3-openeuler24.03-py3.11` ——面向 `a3` 芯片 + `openeuler24.03` 的镜像，Dockerfile 位于 `docker/aura/Dockerfile.a3.openeuler`，内容为 `toolkit + Agent SDK`。
- **共性观察**：所有 4 个 Tag 固定组合为 `AgentSDK 26.1.0 + CANN 9.0.0 + torch_npu 2.9.0 + Python 3.11`，差异仅在"芯片系列 × 操作系统"二维维度；镜像内容统一为 `toolkit + Agent SDK`，无 `runtime only` 或 `devel` 等细分子镜像。

### 表 3：支持的硬件表（原文逐字还原）

| 芯片系列      | 产品示例          | 架构             |
|-----------|---------------|----------------|
| Atlas 910 | Atlas 800I A2 | ARM64 / x86_64 |
| Atlas A3  | Atlas 800I A3 | ARM64 / x86_64 |

**逐行解读**：
- **第 1 行（Atlas 910）**：芯片系列 `Atlas 910`，对应产品示例 `Atlas 800I A2`，同时支持 `ARM64` 与 `x86_64` 两种 CPU 架构。
- **第 2 行（Atlas A3）**：芯片系列 `Atlas A3`，对应产品示例 `Atlas 800I A3`，同样同时支持 `ARM64` 与 `x86_64` 两种 CPU 架构。
- **共性观察**：两类芯片在 CPU 架构上均覆盖 ARM64 与 x86_64，意味着宿主机既可以是鲲鹏/飞腾等 ARM 服务器，也可以是通用 x86 服务器，部署侧较为灵活。

## 【公式解读】

原文无公式（无 LaTeX 表达式或伪代码算法）。

## 【关联】

- **与同目录英文版 OVERVIEW 的关系**：文首链接 `./OVERVIEW.md` 是本文档（中文）的英文版入口，两者内容结构同构（均覆盖 Tag 规范、镜像清单、快速开始、硬件、许可证），英文版用于非中文用户快速查阅。

- **与 Aura 总体快速启动文档的关系**：链接 `../../docs/zh/aura/03_quick_start.md`（"Aura 快速启动文档"）是 Aura 框架层面的快速开始文档；本文档（第 4 节"快速开始"）更聚焦于"镜像选型 + 容器运行 + 设备挂载"这一基础设施环节，是 Aura 总体快速启动的前置/配套章节。

- **与模型示例快速拉起指南的关系**：链接 `../../docs/zh/aura/models/qwen3-4b_quick_start/qwen3-4b-hybrid.md`（"Qwen3-4B 共卡模式快速拉起指南"）是 Aura 框架下的一个具体模型示例（Qwen3-4B 共卡模式）的端到端启动说明；本文档在第 4.3 节"快速启动用例"中直接指向它，意味着本文档的"镜像 + 容器"准备是该模型示例的前置步骤。

- **与社区/代码/issue 的关系**：第 1 节指向 GitCode 上的 AgentSDK 仓库（`aura` 子目录）、issue 反馈渠道，以及华为昇腾社区 `https://www.hiascend.com/` ——这是用户在文档之外获取支持与查阅源码的外部入口。

- **与 CANN 兼容性矩阵的依赖**：第 4.1.1 节要求宿主机驱动与容器内 CANN 版本兼容，并引用 `https://www.hiascend.com/document` 上的 CANN 兼容性矩阵作为依据；这意味着本文档不是孤立镜像说明，而是与 CANN 软件栈的版本对齐深度耦合。

## 【使用方法】

**原文涉及的启用方式与命令如下**：

1. **镜像 Tag 选型**：根据"芯片系列 + 操作系统"组合，从第 3.2 节的 4 个 Tag 中选择对应条目，并按需打开对应 Dockerfile（`Dockerfile.910b.ubuntu` / `Dockerfile.a3.ubuntu` / `Dockerfile.910b.openeuler` / `Dockerfile.a3.openeuler`）查看构建细节。

2. **宿主机准备**：
   - 安装与容器内 CANN 版本兼容的 NPU 驱动（参照 CANN 兼容性矩阵）；
   - Docker 版本建议不低于 `24.0.x`。

3. **启动容器（原文给出完整 docker run 模板）**：

```bash
docker run --name your_container_name \
    --hostname agent \
    --network host \
    -it -d --shm-size=500g \
    --device=/dev/davinci0 --device=/dev/davinci1 \
    --device=/dev/davinci2 --device=/dev/davinci3 \
    --device=/dev/davinci4 --device=/dev/davinci5 \
    --device=/dev/davinci6 --device=/dev/davinci7 \
    --device=/dev/davinci8 --device=/dev/davinci9 \
    --device=/dev/davinci10 --device=/dev/davinci11 \
    --device=/dev/davinci12 --device=/dev/davinci13 \
    --device=/dev/davinci14 --device=/dev/davinci15 \
    --device=/dev/davinci_manager \
    --device=/dev/hisi_hdc \
    --device=/dev/devmm_svm \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime \
    -v /usr/local/sbin:/usr/local/sbin \
    your_image_name:your_image_tag  \
    sleep infinity
```

关键约束：
- `your_image_name:your_image_tag` 需替换为第 3.2 节选定的具体镜像；
- `/dev/davinci*` 数量需与目标机型 NPU 数量一致（Atlas A3 = 16 卡，对应 `davinci0`～`davinci15`）；
- `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 必须全部挂载；
- 驱动/工具链以只读方式挂载到容器内对应路径；
- **不要挂载整个 `/home` 目录**，避免覆盖镜像内默认工作目录 `/home/work` 或引发权限冲突。

4. **容器就绪后的下一步**：进入容器后，按照 `../../docs/zh/aura/03_quick_start.md` 的 Aura 总体快速启动流程，以及 `../../docs/zh/aura/models/qwen3-4b_quick_start/qwen3-4b-hybrid.md` 的 Qwen3-4B 共卡模式拉起指南，执行具体的训练/推理/Agent 任务。

5. **许可证查询**：如需了解镜像内 CANN 与 Mind 系列软件的许可证，参见 `https://github.com/Ascend/cann-container-image/blob/main/LICENSE`；预装的 Python、系统库等亦受其各自许可证约束。

> 原文未涉及：环境变量配置项、卷挂载点自定义写法（除上述只读挂载外）、非 root 用户运行配置、资源限制（CPU/Memory cgroup）、网络端口映射（仅使用 `--network host`）、容器自启动策略、健康检查等 Docker 高级配置——这些均未在本文档中给出。
