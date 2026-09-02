# Agent SDK

> 仓 `agentsdk` · 路径 `docker/aura/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/docker/aura/OVERVIEW.md

# AgentSDK `docker/aura/OVERVIEW.md` 深度解读

---

## 【定位】

本篇文档是 Ascend AgentSDK 仓库中 Aura 容器镜像的「总览 + 上手指南」：既从产品层解释 Aura (Agentic Ultra-fast Reinforcement Architecture) 是什么——一个面向基础模型的"训练-推理-微调"一体化智能体框架；又从交付层给出 Aura Docker 镜像的 Tag 命名规则、当前 CANN 9.0.0 + AgentSDK 26.1.0 组合下的可用镜像清单，以及在 Atlas NPU 主机上拉起容器所需的驱动版本、硬件挂载、Docker 参数与快速 Demo 入口。

---

## 【技术要点】

1. **Aura 框架定位（原文核心定义）**：Aura = Agentic Ultra-fast Reinforcement Architecture，是面向 foundation models 的 integrated training-inference-tuning framework，通过 reinforcement learning 与其他优化手段，基于任务轨迹 (task trajectories) 与奖励信号 (reward signals) 持续改进模型；后训练 (post-training) 阶段渐进式获得规划、工具使用、长时决策等 agent-like 能力。
2. **统一抽象层**：通过 "unified abstraction interface" 同时兼容多种 training engines、inference engines、agent frameworks，并支持自定义模型与 toolchain 的灵活接入。
3. **Tag 命名规则（六段式）**：
   ```bash
   <AgentSDK_version>-<CANN_version>-<pytorch_version>-<chip_series>-<os>-<python_version>
   ```
   例如 `26.1.0-cann9.0.0-torch_npu2.9.0-a2-ubuntu22.04-py3.11`。
4. **Docker 版本门槛**：原文要求 Docker ≥ 24.0.x；同时宿主机必须安装与容器 CANN 版本匹配的 Atlas NPU 驱动（参见 CANN Compatibility Matrix）。
5. **设备挂载分层**：
   - NPU 计算卡 `/dev/davinci*` 按需挂载；
   - NPU 管理设备 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 必须全部挂载；
   - 驱动与工具链 `/usr/local/Ascend/driver`、`/usr/local/bin/npu-smi` 等以 **read-only** 方式挂载以保证运行时一致性。
6. **运行时注意事项**：示例命令设置 `--shm-size=500g`、`--network host`、容器名 `your_container_name`、主机名 `agent`；容器默认工作目录为 `/home/work`，**不建议**挂载整个 `/home`，以免覆盖默认 workspace 或引发权限冲突；Atlas A3 单机 16 张 NPU，需对应挂载 16 个 device ID。

---

## 【关键机制与数据】

| # | 原文要点 | 出处 |
|---|----------|------|
| 1 | Aura 通过 task trajectories + reward signals 持续改进基础模型 | §2 |
| 2 | 后训练赋予模型 planning / tool use / long-horizon decision-making 能力 | §2 |
| 3 | Tag 命名包含 6 个字段：AgentSDK_version / CANN_version / pytorch_version / chip_series / os / python_version | §3.1 |
| 4 | 当前仅发布 **CANN 9.0.0 + AgentSDK 26.1.0** 的镜像组合 | §3.2 |
| 5 | PyTorch 适配版本示例：`torch_npu2.7.1`, `torch_npu2.9.0.post2`（命名空间为 `torch_npu*`） | §3.1 |
| 6 | 芯片系列：910、910b、a3、310p | §3.1 |
| 7 | 操作系统支持：ubuntu22.04、openeuler24.03 | §3.1 |
| 8 | Python 版本：`py3.11` | §3.1 |
| 9 | 镜像内容描述均为 `toolkit + Agent SDK` | §3.2 |
| 10 | Docker 版本要求 ≥ 24.0.x | §4.1.1 |
| 11 | Atlas A3 单机 16 NPUs → 需挂载 16 个 device ID | §4.2 NOTE 1 |
| 12 | 共享内存设置 `--shm-size=500g` | §4.2 |
| 13 | 容器默认工作目录 `/home/work` | §4.2 NOTE 2 |

> **数据流 / 性能数据**：原文未提供 Aura 训练/推理吞吐、reward 曲线、benchmark 数值等定量性能指标；本节仅保留原文实际给出的版本号、容器参数与硬件数量信息。

---

## 【表格解读】

### 表格 1：Tag 字段说明（§3.1，原文逐字还原）

| Field              | Example Values                           | Description        |
|--------------------|------------------------------------------|--------------------|
| `AgentSDK_version` | `26.1.0`                                 | AgentSDK version   |
| `CANN_version`     | `cann9.0.0`                              | CANN version       |
| `pytorch_version`  | `torch_npu2.7.1`, `torch_npu2.9.0.post2` | PyTorch version    |
| `chip_series`      | `910`, `910b`, `a3`, `310p`              | Target chip family |
| `os`               | `ubuntu22.04`, `openeuler24.03`          | Operating system   |
| `python_version`   | `py3.11`                                 | Python version     |

**解读**：六段式 Tag 是后续选镜像的唯一寻址方式。`pytorch_version` 字段统一以 `torch_npu*` 前缀出现，说明 Aura 镜像栈固定绑定昇腾 PyTorch (torch_npu) 而非原生 PyTorch；`chip_series` 中 `a2`（在 §3.2 出现但本表未列）与 `910b` 对应 Atlas 910 系列的 910b 硬件，`a3` 对应 Atlas A3，`310p` 对应推理 / 边缘侧的 310P；OS 仅列出 ubuntu22.04 与 openeuler24.03 两种，均为 LTS / 长周期支持版本；Python 仅 `py3.11`，未提供 3.10 / 3.12 等其他版本。

### 表格 2：CANN 9.0.0 + 26.1.0 Agent SDK 镜像（§3.2，原文逐字还原）

| Tag                                                        | Dockerfile                                                                              | 镜像内容                |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------|---------------------|
| `26.1.0-cann9.0.0-torch_npu2.9.0-a2-ubuntu22.04-py3.11`    | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.910b.ubuntu)    | toolkit + Agent SDK |
| `26.1.0-cann9.0.0-torch_npu2.9.0-a3-ubuntu22.04-py3.11`    | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.a3.ubuntu)      | toolkit + Agent SDK |
| `26.1.0-cann9.0.0-torch_npu2.9.0-a2-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.910b.openeuler) | toolkit + Agent SDK |
| `26.1.0-cann9.0.0-torch_npu2.9.0-a3-openeuler24.03-py3.11` | [Dockerfile](https://gitcode.com/Ascend/AgentSDK/docker/aura/Dockerfile.a3.openeuler)   | toolkit + Agent SDK |

**解读**：表格揭示了一个「隐含但重要的不一致」——Tag 中 chip 字段写作 `a2`，但 Dockerfile 链接却使用 `910b`/`a3` 命名空间，说明 Tag 中 `a2` 实际等价于 `910b` 系列。全部 4 个镜像均锁定同一套底层栈：CANN 9.0.0、torch_npu 2.9.0、AgentSDK 26.1.0、Python 3.11，仅在「芯片 × OS」两维度上提供 2×2 = 4 种组合，覆盖主流 Atlas 800I A2 / A3 硬件及 ubuntu / openeuler 双发行版。镜像内容一致标注为 `toolkit + Agent SDK`，意味着 Ascend 基础 toolkit（驱动接口、算子库等）与 AgentSDK 业务层一同打包，部署到容器内即可开箱即用。

### 表格 3：Supported Hardware（§5，原文逐字还原）

| Chip Series | Product Examples | Architecture   |
|-------------|------------------|----------------|
| Atlas 910   | Atlas 800I A2    | ARM64 / x86_64 |
| Atlas A3    | Atlas 800I A3    | ARM64 / x86_64 |

**解读**：原文明确支持的仅两个系列——Atlas 910（产品代表 Atlas 800I A2）与 Atlas A3（产品代表 Atlas 800I A3），二者均同时兼容 ARM64 与 x86_64 主机架构，说明容器 / 镜像本身是架构无关的，差异由基础镜像与宿主机共同承担。注意此处 **未列出 `310p`**——尽管 §3.1 的 Tag 命名规则中包含 `310p`，但当前 Overview 的 Supported Hardware 小节并未将其列为正式支持产品，意味着 310P 仅在 Tag 命名层面预留，目前可能尚未进入正式发布矩阵。

---

## 【公式解读】

原文无 LaTeX 公式或算法伪代码块。

唯一具有「模式化」语义的表达式是 **Tag 命名模板**：

```
<AgentSDK_version>-<CANN_version>-<pytorch_version>-<chip_series>-<os>-<python_version>
```

符号含义（按出现顺序）：
- `<AgentSDK_version>`：AgentSDK 业务层版本，原文示例 `26.1.0`；
- `<CANN_version>`：昇腾异构计算架构版本，前缀固定 `cann`，原文示例 `cann9.0.0`；
- `<pytorch_version>`：torch_npu 适配版本，原文示例 `torch_npu2.7.1` 或 `torch_npu2.9.0.post2`；
- `<chip_series>`：目标芯片家族，原文示例 `910`/`910b`/`a3`/`310p`（实际镜像里 `a2` = `910b`）；
- `<os>`：基础 OS，原文示例 `ubuntu22.04` 或 `openeuler24.03`；
- `<python_version>`：Python 运行时，原文示例 `py3.11`。

---

## 【关联】

文档通过三组内部链接与其他模块形成上下游关系：

1. **多语言平行版本**：`./OVERVIEW.zh.md` —— 同一文件的简体中文版，用于母语用户对照查阅。
2. **快速上手文档**：`../../docs/zh/aura/03_quick_start.md` —— 在 §1 Quick Reference 中作为 "Aura Quick-start Documentation" 入口，是本 Overview 的功能层展开（如何真正用 Aura 训练/部署 agent）。
3. **示例 Demo**：`../../docs/zh/aura/models/qwen3-4b_quick_start/qwen3-4b-hybrid.md` —— §4.3 Quick-start Demo 直接指向该文档，提供 Qwen3-4B 在 Aura 上的 hybrid 模式实操路径，可视为「容器环境就绪 → 跑通第一个端到端 agent 训练/推理 demo」的桥梁。

此外，外部链接指向的支撑模块：
- `https://gitcode.com/Ascend/AgentSDK/issues`：Issue Feedback，问题反馈通道；
- `https://gitcode.com/Ascend/AgentSDK/tree/master/aura`：源码树（`aura` 子目录即为 Aura 框架本身的实现）；
- `https://www.hiascend.com/document`：CANN Compatibility Matrix，驱动 ↔ CANN 版本对应表（§4.1.1 强制依赖）；
- `https://www.hiascend.com/en/`：昇腾社区入口；
- `https://github.com/Ascend/cann-container-image/blob/main/LICENSE`：容器内预装 CANN / MindSeries 软件的许可证来源（§6）。

文档内部的层级关系可视为：**OVERVIEW（本文，What + 环境就绪）→ Quick-start（How，框架使用）→ Qwen3-4B hybrid demo（Example，端到端样例）**。

---

## 【使用方法】

### 1. 选镜像（按 §3.1/§3.2）

依据本机硬件与 OS 选择 Tag，例如 Atlas A3 + Ubuntu 22.04：
```bash
your_image_name = 26.1.0-cann9.0.0-torch_npu2.9.0-a3-ubuntu22.04-py3.11
```

### 2. 安装前置驱动（§4.1.1）

```text
- 宿主机安装与 CANN 9.0.0 兼容的 Atlas NPU 驱动（查 CANN Compatibility Matrix）
- Docker ≥ 24.0.x
```

### 3. 启动容器（§4.2，原文完整命令已逐字保留在原文中）

关键参数要点：
- 使用 `--device=/dev/davinci*` 逐个挂载 NPU 卡，按芯片规模调整数量（A3 → 16 个）；
- 必须挂载 `/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`；
- 以 `-v ...:/...` 只读挂载 `/usr/local/Ascend/driver`、`/usr/local/bin/npu-smi`、`/usr/local/dcmi`、`/etc/ascend_install.info`；
- `--shm-size=500g`、`--network host`、镜像内执行 `sleep infinity` 以保持容器存活以便后续 exec。

### 4. 跑通 Demo（§4.3）

按 `../../docs/zh/aura/models/qwen3-4b_quick_start/qwen3-4b-hybrid.md` 的指引，在已运行的容器内执行 Qwen3-4B hybrid 模式快速开始流程。

### 配置项 / CLI flag / API 端点

原文未涉及容器启动之外的 Aura 配置项、训练 CLI flag、HTTP/gRPC 接口等；亦未涉及环境变量、奖励函数定义、agent rollout 配置等细节——这些属于 `03_quick_start.md` 与模型示例文档的范围，本 Overview 仅提供「环境就绪」层信息。
