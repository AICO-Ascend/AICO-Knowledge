# ModelAgent

> 仓 `model-agent` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/docker/OVERVIEW.md

# ModelAgent 镜像 Overview 文档深度解读

---

## 【定位】

本篇文档是 `model-agent` 仓库 `docker/OVERVIEW.md` 的镜像总览页，面向昇腾（Atlas）AI 处理器用户，描述 **ModelAgent 智能模型代理体验镜像** 的标签约定、镜像清单、容器启动方式、内部 Model Agent（基于 Claude Code + Kimi）使用流程、镜像内置软件与支持硬件——即「拿到 Atlas 主机后，如何拉取/构建 ModelAgent 镜像、跑起来并使用 Model Agent Skills」的入门指南。

---

## 【技术要点】

1. **镜像标签规范**：`<version>-<chip_series>-<os>-py<python_version>` 四段式，例如 `1.0-a2-ubuntu22.04-py3.11`；当前 1.0 版本仅放出两条标签，对应 `a2` 与 `a3` 两个芯片系列、Ubuntu 22.04、Python 3.11。
2. **镜像内容**：两条标签镜像内容均为 `modelagent/torch_npu 2.9`；底层系统为 Ubuntu 22.04.5，包管理器为 `apt`，Python 3.11。
3. **主机驱动先决条件**：宿主机必须安装与容器内 **CANN 版本兼容的 Atlas NPU 驱动**，需查 CANN Compatibility Matrix 确认驱动↔CANN 映射。
4. **设备透传与挂载**：`docker run` 通过 `--device` 显式挂载 `/dev/davinci4`、`/dev/davinci5`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并通过 `-v` 挂载宿主机的 dcmi、hccn_tool、npu-smi、driver lib64、version.info、ascend_install.info 及 `/root/.cache`，配合 `--shm-size=1g` 与 `--net=host`。
5. **本地构建与二次开发**：`docker buildx build -t modelagent:0.0-a2-ubuntu22.04-py3.11 -f Dockerfile .`；二次开发以 `quay.io/linxishuixin/model-agent/model-agent-a2:v0.0` 为基镜像。
6. **容器内 Model Agent 接入**：通过 `vim ~/.claude/settings.json` 编辑 Claude 配置，配置 `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/`、`ANTHROPIC_MODEL=kimi-k2.6`、`ANTHROPIC_SMALL_FAST_MODEL=kimi-k2.6`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`、`API_TIMEOUT_MS=600000`，并启用 `ascend-model-agent-plugin`（Git 来源 `https://gitcode.com/gmq123/ascend-model-agent-plugin.git`），随后运行 `claude` 进入会话，使用 `/verify-agent`、`/optimizer-agent` 等斜杠命令调用 Skills。

---

## 【关键机制与数据】

**工作原理（容器→驱动→NPU）：** ModelAgent 镜像把模型适配/迁移/量化/调优等自动化能力封装成 Claude Code 可调用的 Skills（斜杠命令）。容器启动时通过设备透传拿到宿主 NPU 设备节点（`/dev/davinci4/5`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`），再通过卷挂载与宿主的 dcmi、hccn_tool、npu-smi、驱动库及版本信息目录打通，使容器内 `torch_npu 2.9` 能与宿主机 NPU 驱动正常通信。

**Model Agent 触发路径：** 进入容器 → 编辑 `~/.claude/settings.json`（Kimi K2.6 作为模型端点 + 启用 ascend-model-agent-plugin 插件）→ 启动 `claude` → 在对话界面输入 `/verify-agent Help me adapt the qwen3.5-0.8B model` 或 `/optimizer-agent Help me optimize the qwen3.5-0.8B model` 等指令。

**原文中的数字/参数：**
- 共享内存：`--shm-size=1g`
- API 超时：`API_TIMEOUT_MS=600000`（即 600 秒）
- 系统：`OS Ubuntu 22.04.5`、Python `3.11`、包管理器 `apt`、Torch_npu `2.9`
- 当前发布标签：`1.0-a2-ubuntu22.04-py3.11`、`1.0-a3-ubuntu22.04-py3.11`
- 构建示例 tag：`modelagent:0.0-a2-ubuntu22.04-py3.11`（原文示例中使用了 `0.0` 而非 `1.0`，原样保留）
- 二次开发基镜像：`quay.io/linxishuixin/model-agent/model-agent-a2:v0.0`

> 原文未提供性能数据（吞吐、时延、benchmark 等）。

---

## 【表格解读】

### 表 1：Tag Convention 字段说明（逐字还原）

| Field | Example | Description |
|---|---|---|
| `version` | `1.0` | ModelAgent version |
| `chip_series` | `a2`, `a3` | Target Atlas chip series |
| `os` | `ubuntu22.04` | Base operating system |
| `python_version` | `py3.11` | Python version |

**逐行解读：**
- **`version`**：镜像的 ModelAgent 语义化版本号，示例 `1.0` 表示首个正式版。
- **`chip_series`**：目标 Atlas 芯片系列，示例给出 `a2`、`a3`，与下文"Supported Hardware"中 Atlas 910（Atlas 800T A2 / 900 A2 PoD）和 Atlas A3（Atlas 800T A3）对应。
- **`os`**：基础操作系统代号，示例 `ubuntu22.04`，对应镜像内 OS 为 Ubuntu 22.04.5。
- **`python_version`**：Python 版本，示例 `py3.11`，对应镜像内置 Python 3.11。

### 表 2：ModelAgent 1.0 镜像清单（逐字还原）

| Tag | Image Address | Image Contents |
|-----|----------|----------|
| `1.0-a2-ubuntu22.04-py3.11` | [dockerfile](https://gitcode.com/gmq123/model-agent/blob/master/docker/1.0-a2-ubuntu22.04-py3.11/Dockerfile) | modelagent/torch_npu 2.9 |
| `1.0-a3-ubuntu22.04-py3.11` | [dockerfile](https://gitcode.com/gmq123/model-agent/blob/master/docker/1.0-a3-ubuntu22.04-py3.11/Dockerfile) | modelagent/torch_npu 2.9 |

**逐行解读：**
- **`1.0-a2-ubuntu22.04-py3.11`**：面向 Atlas 910 系列（a2 家族）的镜像，Dockerfile 位于 `docker/1.0-a2-ubuntu22.04-py3.11/`，预装 `modelagent/torch_npu 2.9`。
- **`1.0-a3-ubuntu22.04-py3.11`**：面向 Atlas A3 系列（Atlas 800T A3）的镜像，Dockerfile 位于 `docker/1.0-a3-ubuntu22.04-py3.11/`，同样预装 `modelagent/torch_npu 2.9`。两版本仅芯片系列不同，软件栈内容一致。

### 表 3：Image Software Information（逐字还原）

| Software | Version |
|---|---|
| OS | Ubuntu 22.04.5 |
| Python | 3.11 |
| Package Manager | apt |
| Torch_npu | 2.9 |

**逐行解读：**
- **OS = Ubuntu 22.04.5**：基础操作系统为 Ubuntu 22.04 LTS 的 22.04.5 小版本。
- **Python = 3.11**：默认 Python 解释器主版本。
- **Package Manager = apt**：使用 Debian 系 `apt` 进行包管理。
- **Torch_npu = 2.9**：昇腾 PyTorch 适配版本为 2.9，是模型适配与训练的核心框架依赖。

### 表 4：Supported Hardware（逐字还原）

| Chip Series | Product Examples | Architecture |
|---|---|---|
| Atlas 910 | Atlas 800T A2, Atlas 900 A2 PoD | ARM64 / x86_64 |
| Atlas A3 | Atlas 800T A3 | ARM64 / x86_64 |

**逐行解读：**
- **Atlas 910 行**：覆盖 Atlas 800T A2 与 Atlas 900 A2 PoD 两款产品（对应 `a2` 标签），支持 ARM64 与 x86_64 两种主机架构。
- **Atlas A3 行**：覆盖 Atlas 800T A3 产品（对应 `a3` 标签），同样支持 ARM64 与 x86_64。原文未列出 Atlas A3 的 PoD 等其他型号，仅明确 Atlas 800T A3。

---

## 【公式解读】

**原文无公式。** 文档涉及到的版本号拼接可视为一个隐式格式模板 `<version>-<chip_series>-<os>-py<python_version>`（已在表 1 解读），但文档未以 LaTeX 或伪代码形式给出任何数学公式或算法表达式。

---

## 【关联】

- **多语言版本**：文末内部链接 `./OVERVIEW.zh.md`（同目录中文版 Overview），两份文档结构对应。
- **上游代码仓**：镜像所封装的能力由 [modelagent 社区仓](https://gitcode.com/Ascend/model-agent) 维护，问题反馈走 [Issue Feedback](https://gitcode.com/Ascend/model-agent/issues)。
- **插件仓库**：容器内 Model Agent Skills 的具体实现来自 `ascend-model-agent-plugin`（Git 源 `https://gitcode.com/gmq123/ascend-model-agent-plugin.git`），通过 Claude Code 的 `extraKnownMarketplaces` + `enabledPlugins` 机制加载——这是"镜像"与"技能实现"的解耦点。
- **基镜像（quay.io）**：二次开发场景使用 `quay.io/linxishuixin/model-agent/model-agent-a2:v0.0` 作为基础镜像，说明该镜像同时发布在 GitCode 与 Quay.io 两个 Registry。
- **驱动依赖**：镜像依赖宿主机 NPU 驱动与容器内 CANN 版本兼容，需查询 [CANN Compatibility Matrix](https://www.hiascend.com/document)——这是 ModelAgent 与昇腾 CANN 软件栈的耦合点。
- **模型端点**：文档以 Kimi K2.6（`https://api.kimi.com/coding/`）为例演示配置，说明 Model Agent 是模型无关的，可替换为其他 Anthropic 兼容 API。

---

## 【使用方法】

**1. 启动容器（原文命令）：**
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
其中 `{model-agent_tag}` 需替换为 `1.0-a2-ubuntu22.04-py3.11` 或 `1.0-a3-ubuntu22.04-py3.11`。

**2. 本地构建（原文命令）：**
```bash
docker buildx build -t modelagent:0.0-a2-ubuntu22.04-py3.11 -f Dockerfile .
```

**3. 二次开发基镜像示例（原文片段）：**
```dockerfile
FROM quay.io/linxishuixin/model-agent/model-agent-a2:v0.0

RUN apt update -y && \
 apt install gcc ...
...
```

**4. 配置 Model Agent（进入容器后）：**
- 执行 `vim ~/.claude/settings.json`，按下 `i` 进入编辑模式，清空后粘贴 Kimi K2.6 示例配置（含 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`（用户自填）、`ANTHROPIC_MODEL=kimi-k2.6`、`ANTHROPIC_SMALL_FAST_MODEL=kimi-k2.6`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`、`API_TIMEOUT_MS=600000` 以及启用 `ascend-model-agent-plugin` 插件），`:wq` 保存。
- 执行 `claude`，一路回车直到对话界面。
- 调用 Skills 示例：`/verify-agent Help me adapt the qwen3.5-0.8B model`、`/optimizer-agent Help me optimize the qwen3.5-0.8B model`。

**5. 主机先决条件（原文提示）：** 必须先在宿主机安装与容器内 CANN 版本兼容的 Atlas NPU 驱动；具体对应关系查 [CANN Compatibility Matrix](https://www.hiascend.com/document)。

> 原文未涉及环境变量持久化、容器重启策略、Compose/K8s 部署、HTTPS 证书、TLS 配置等内容。
