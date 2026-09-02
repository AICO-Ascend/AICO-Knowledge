# ModelAgent

> 仓 `model-agent` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/docker/OVERVIEW.zh.md

## 【定位】

这篇文档是 ModelAgent（昇腾模型 Agent）容器镜像的官方使用总览，介绍如何在昇腾 AI 处理器上通过 Docker 镜像体验模型适配、迁移、量化、优化等自动化能力，并给出从获取、运行、构建、二次开发到 Claude Code 配置与 Skills 调用的完整入口指引。

---

## 【技术要点】

1. **Tag 命名规范**：镜像标签严格遵循 `<版本号>-<芯片系列>-<操作系统>-py<python版本>` 四段式格式，例如 `1.0-a2-ubuntu22.04-py3.11`。
2. **当前已发布的 Tag（v1.0）**：仅有两款，分别是 `1.0-a2-ubuntu22.04-py3.11` 与 `1.0-a3-ubuntu22.04-py3.11`，二者内含 `modelagent/torch_npu 2.9`。
3. **容器运行必需挂载**：除 `--shm-size=1g` 与 `--net=host` 外，需透传至少两块设备 `/dev/davinci4`、`/dev/davinci5`，以及驱动管理设备 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`；并通过 `-v` 把主机上 `/usr/local/dcmi`、`hccn_tool`、`npu-smi`、`Ascend/driver/lib64/`、`version.info`、`ascend_install.info`、`/root/.cache` 挂入容器。
4. **本地构建命令**：`docker buildx build -t modelagent:0.0-a2-ubuntu22.04-py3.11 -f Dockerfile .`（注意 Tag 段是 `0.0-` 而非 `1.0-`，原文如此）。
5. **二次开发方式**：以 `quay.io/linxishuixin/model-agent/model-agent-a2:v0.0` 为基础镜像，使用 `FROM` 指令叠加自定义软件。
6. **Claude Code 配置与 Skills 启动**：编辑 `~/.claude/settings.json` 配置 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_MODEL`、`ANTHROPIC_SMALL_FAST_MODEL`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`、`API_TIMEOUT_MS=600000` 六个环境变量，并启用 `ascend-model-agent-plugin`；进入容器执行 `claude` 命令即可调用 `/verify-agent`、`/optimizer-agent` 等 Skills。

---

## 【关键机制与数据】

**原文：镜像分层与依赖**
- 基础操作系统：Ubuntu 22.04.5，Python 3.11，包管理器 apt，深度学习框架 `modelagent/torch_npu 2.9`。

**原文：硬件兼容机制**
- 通过 `--device /dev/davinci*` 透传 NPU 计算芯片，配合 `/dev/davinci_manager`（设备管理）、`/dev/devmm_svm`（共享虚拟内存）、`/dev/hisi_hdc`（主机-设备通信）三个控制类设备，完成昇腾 NPU 在容器内的全栈调用。
- 通过 `-v` 挂载主机侧的 `npu-smi`、`hccn_tool`、`Ascend/driver` 等目录，使容器复用宿主机的 NPU 驱动与版本信息，确保"主机驱动 ↔ 容器内 CANN"版本一致（参见 CANN 兼容性矩阵）。

**原文：Agent Skills 调用链路**
- 用户在 Claude Code 对话框中输入 `/verify-agent` 或 `/optimizer-agent` 触发对应 Skill，由 `ascend-model-agent-plugin`（Git 源：`https://gitcode.com/gmq123/ascend-model-agent-plugin.git`）解析并调度 ModelAgent 自动化能力。

**原文：性能/数据流相关**
- 文档未提供任何性能数据（FPS、吞吐、延迟等均未给出），亦未描述数据流图。

---

## 【表格解读】

### 表 1：Tag 规范字段说明（原文逐字还原）

| 字段 | 示例值 | 说明 |
|---|---|---|
| `版本号` | `1.0` | ModelAgent 版本号 |
| `芯片系列` | `a2`、`a3` | 目标昇腾芯片系列 |
| `操作系统` | `ubuntu22.04` | 基础操作系统 |
| `python版本` | `py3.11` | Python 版本 |

**解读**：该表定义了镜像 Tag 的 4 个组成字段。`版本号` 标识 ModelAgent 软件本身的迭代轮次；`芯片系列` 通过 `a2`/`a3` 两个枚举值对应不同的昇腾 NPU 硬件平台；`操作系统` 与 `python版本` 描述基础运行环境。任一字段变化都会产生新的镜像 Tag，是镜像寻址的最小单元。

---

### 表 2：ModelAgent 1.0 支持的 Tag（原文逐字还原）

| Tag | dockerfile | 镜像内容 |
|-----|----------|----------|
| `1.0-a2-ubuntu22.04-py3.11` | [dockerfile](https://gitcode.com/gmq123/model-agent/blob/master/docker/1.0-a2-ubuntu22.04-py3.11/Dockerfile) | modelagent/torch_npu 2.9 |
| `1.0-a3-ubuntu22.04-py3.11` | [dockerfile](https://gitcode.com/gmq123/model-agent/blob/master/docker/1.0-a3-ubuntu22.04-py3.11/Dockerfile) | modelagent/torch_npu 2.9 |

**解读**：v1.0 仅覆盖 a2 与 a3 两个昇腾芯片系列，操作系统统一为 Ubuntu 22.04，Python 统一为 3.11，深度学习栈统一为 `modelagent/torch_npu 2.9`。两者的差异点仅在芯片适配层（Dockerfile 不同），上层软件栈一致。每个 Tag 都可点开对应的 dockerfile 链接以查阅构建细节。

---

### 表 3：镜像软件信息（原文逐字还原）

| 软件 | 版本 |
|---|---|
| OS | Ubuntu 22.04.5 |
| Python | 3.11 |
| Package Manager | apt |
| Torch_npu | 2.9 |

**解读**：列出镜像预装的基础栈。OS 锁死在 Ubuntu 22.04.5 LTS，Python 锁死在 3.11，包管理器使用 apt（无 conda/pip 多管理器并存）。Torch_npu 2.9 是面向昇腾 NPU 的 PyTorch 适配版本，是后续模型适配、量化、调优所依赖的核心框架。

---

### 表 4：支持的硬件（原文逐字还原）

| 芯片系列 | 产品示例 | 架构 |
|---|---|---|
| 昇腾 910 | Atlas 800T A2、Atlas 900 A2 PoD | ARM64 / x86_64 |
| 昇腾 A3 | Atlas 800T A3 | ARM64 / x86_64 |

**解读**：硬件覆盖两个芯片家族。昇腾 910 系列覆盖 Atlas 800T A2 与 Atlas 900 A2 PoD 两款服务器产品；昇腾 A3 系列对应 Atlas 800T A3。两个家族均同时支持 ARM64 与 x86_64 两种主机 CPU 架构，因此同一镜像可在鲲鹏、飞腾、海光等不同服务器上运行。

---

## 【公式解读】

原文无数学公式，但给出了一条 **Tag 命名模板**（伪代码/格式说明形式）：

```
<版本号>-<芯片系列>-<操作系统>-py<python版本>
```

符号含义：
- `<版本号>`：ModelAgent 软件版本，对应表 1 示例 `1.0`。
- `<芯片系列>`：目标昇腾芯片系列枚举，对应示例 `a2` 或 `a3`。
- `<操作系统>`：基础操作系统代号，对应示例 `ubuntu22.04`。
- `py`：固定字面量前缀，用于标识 Python 段。
- `<python版本>`：Python 主次版本，对应示例 `py3.11`。

作用：以该模板生成的字符串即镜像 Tag，是 `docker pull`、`docker run` 时寻址镜像的唯一标识；任何字段改变都意味着产生新的镜像变体。

---

## 【关联】

- **同语种版本互链**：文末内部链接 `./OVERVIEW.md` 指向英文版 Overview，两份文档互为翻译镜像，内容结构应保持一致。
- **上游社区**：文档开头的"快速参考"将 [modelagent community](https://gitcode.com/Ascend/model-agent) 标记为 ModelAgent 的维护方，issue 反馈、许可证查询也指向同一仓库。
- **CANN 兼容性矩阵**：运行容器前要求主机 NPU 驱动与容器内 CANN 版本匹配，链接 [https://www.hiascend.com/document](https://www.hiascend.com/document) 给出版本对应关系，是镜像运行的前置文档。
- **Dockerfile 与镜像本体**：表 2 中每个 Tag 都链接到对应的 dockerfile（`docker/1.0-a2-ubuntu22.04-py3.11/Dockerfile`、`docker/1.0-a3-ubuntu22.04-py3.11/Dockerfile`），构成"Overview → Dockerfile → 镜像构建"的纵向追溯链。
- **Skill 插件**：ModelAgent 的能力通过 `ascend-model-agent-plugin`（Git 源 `https://gitcode.com/gmq123/ascend-model-agent-plugin.git`）以 Claude Code Marketplace 形式注入，`settings.json` 中的 `extraKnownMarketplaces` 与 `enabledPlugins` 字段是该插件的注册开关，与 `/verify-agent`、`/optimizer-agent` 两个 Skill 调用直接对应。
- **许可证**：文末的 [许可证信息](https://gitcode.com/Ascend/model-agent) 链接说明 ModelAgent 与预装 Python、系统库的授权情况，是合规使用镜像的依据。

---

## 【使用方法】

**1. 准备主机（原文：前置要求-可选）**
- 在主机上安装与容器内 CANN 版本兼容的昇腾 NPU 驱动，参见 [CANN 兼容性矩阵](https://www.hiascend.com/document)。

**2. 运行容器（原文：快速开始-运行 ModelAgent 容器）**
```bash
docker run \
  --name modelagent_container \
  --shm-size=1g \
  --net=host \
  --device /dev/davinci4 \
  --device /dev/davinci5 \
  --device /dev/davinci_manager \
  --device /dev/devmm_svm \
  --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /root/.cache:/root/.cache \
  -it {model-agent_tag}:latest bash
```
其中 `{model-agent_tag}` 替换为 `1.0-a2-ubuntu22.04-py3.11` 或 `1.0-a3-ubuntu22.04-py3.11`。

**3. 本地构建（原文：如何本地构建）**
```bash
docker buildx build -t modelagent:0.0-a2-ubuntu22.04-py3.11 -f Dockerfile .
```

**4. 二次开发（原文：如何二次开发）**
```dockerfile
FROM quay.io/linxishuixin/model-agent/model-agent-a2:v0.0
RUN apt update -y && \
    apt install gcc ...
...
```

**5. 配置 Claude Code（原文：model agent 使用）**
- `vim ~/.claude/settings.json`，按 `i` 编辑，输入 JSON 配置 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`（需替换为真实 Token）、`ANTHROPIC_MODEL`、`ANTHROPIC_SMALL_FAST_MODEL`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`、`API_TIMEOUT_MS=600000`；并通过 `extraKnownMarketplaces` + `enabledPlugins` 启用 `ascend-model-agent-plugin`。
- `:wq` 保存退出后执行 `claude` 启动 Claude Code，连按回车进入对话界面。
- 调用 Skill 示例：`/verify-agent 帮我适配 qwen3.5-0.8B 模型`、`/optimizer-agent 帮我优化 qwen3.5-0.8B 模型`。

**6. 反馈与帮助（原文：快速参考）**
- [ModelAgent 开源项目](https://gitcode.com/Ascend/model-agent)
- [问题反馈](https://gitcode.com/Ascend/model-agent/issues)
