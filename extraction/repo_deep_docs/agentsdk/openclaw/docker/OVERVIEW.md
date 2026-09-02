# AgentSDK Openclaw Docker

> 仓 `agentsdk` · 路径 `openclaw/docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/openclaw/docker/OVERVIEW.md

# AgentSDK Openclaw Docker 文档深度解读

## 【定位】

本文档系统描述了 AgentSDK Openclaw（一个基于 OpenClaw 构建的高可用多领域 Agent 框架与服务）的 Docker 镜像三层架构设计、构建流程、部署方式以及二次开发与动态扩展（Skills 挂载）机制，定位为该框架容器化交付与运维的权威参考手册。

---

## 【技术要点】

1. **三层镜像架构**：基座层 `openclaw:base-{version}`（基础设施）、应用层 `openclaw:app-{version}`（OpenClaw 官方构建产物，多阶段构建）、定制层 `openclaw:{version}`（集成 subagent-coordinator + Hermes + skills），三层可独立构建与缓存复用。
2. **统一构建入口**：通过 `bash ./build-openclaw.sh` 一键构建三层镜像，并支持 `--skip-base`、`--skip-app` 等参数跳过已有层；构建参数涵盖 `VERSION`、`REGISTRY`、`OFFLINE`、`SKIP_BASE/APP/OVERLAY/PLUGINS`、`OPENCLAW_SRC`、`HERMES_SRC`、`DOCKER_REGISTRY_NPM` 共 10 项。
3. **一键部署脚本**：`bash ./scripts/deploy.sh quick -n 1 -m mode-name -u http://xxxx.xx.xx.xx:xxxx -p xxxx -i openclaw:2026.5.22 --skills --name openclaw-test`，支持单实例快速部署并自动处理 skills 合并挂载。
4. **Skills 三阶段挂载机制**：镜像内置 (`skills-shared/`) → 主机合并 (`openclaw-configs/skills-merged/`，合并策略为"主机优先") → 容器绑定挂载 (`/home/node/.openclaw/skills/`)，无需重建镜像即可动态增删技能。
5. **基座层预装生态**：包含 SSH/uv/bun/pnpm/npm 全局包/pip 包/Playwright/Chromium/gosu/ffmpeg/rsync，为上层 Agent（代码生成、网页搜索、研究分析、数学计算）提供开箱即用运行环境。
6. **多架构支持**：同时支持 `x86_64`（Intel/AMD 64 位）与 `aarch64`（ARM 64 位）两种硬件架构。
7. **镜像分发源**：发布于华为云镜像仓库 `https://www.hiascend.com/developer/ascendhub`，完整样例地址 `swr.cn-south-1.myhuaweicloud.com/ascendhub/openclaw:2026.5.22`。

---

## 【关键机制与数据】

**镜像命名与版本锚定**（原文：版本号示例 `2026.5.22`，对应官方 OpenClaw release identifier）：三层镜像共享同一版本号 `{version}`，但通过后缀（`base-`、`app-`、无后缀）区分层级，便于版本回溯与组合。

**构建跳过链路**（原文：默认 `false`，可设为 `true`）：`SKIP_BASE/SKIP_APP/SKIP_OVERLAY/SKIP_PLUGINS` 四个布尔开关允许开发者增量构建，例如只改动 overlay 层时可跳过 base 与 app 重建，复用已缓存镜像，显著加速 CI 迭代。

**镜像源切换**（原文：`DOCKER_REGISTRY_NPM` 示例 `https://registry.npmmirror.com`）：构建期可注入 NPM 镜像地址，配合 `OFFLINE=true` 参数实现完全离线构建（仅用本地源），适用于内网/无外网环境。

**Skills 合并优先级**（原文："image skills + host skills union, host takes priority"）：容器启动时 deploy 脚本将镜像内置 skills 解压至 `openclaw-configs/skills-merged/`，再与主机自定义 skills 合并（同名时主机覆盖），最终 bind mount 到容器 `/home/node/.openclaw/skills/`，由 Gateway 加载——该机制实现了"镜像不变、技能可变"的解耦。

**动态生效路径**（原文）：新增 skill 后可通过 `/restart` 命令触发 WebUI 重启，或 `docker exec openclaw-1 pkill -u node -f gateway` 终止网关进程（健康监控会自动拉起），无需重启容器。

---

## 【表格解读】

### 表 1：Tag Specification（镜像标签规范）

| Field | Example Value | Description |
|-------|---------------|-------------|
| Openclaw Version | 2026.5.22 | Corresponding to the official OpenClaw release version identifier |

逐行解读：唯一字段为版本号，示例 `2026.5.22`，直接对齐 OpenClaw 官方发布标识符——意味着镜像版本与上游 OpenClaw 版本严格 1:1 绑定，避免了二次版本号带来的追踪歧义。

### 表 2：Image Architecture（镜像三层架构）

| Layer | Image Tag | Description | Dockerfile |
|-------|-----------|-------------|------------|
| **Layer 1** | `openclaw:base-{version}` | Infrastructure including SSH/uv/bun/pnpm/npm global packages/pip packages/Playwright/Chromium/gosu/ffmpeg/rsync | [Dockerfile.openclaw-base](./Dockerfile.openclaw-base) |
| **Layer 2** | `openclaw:app-{version}` | Official OpenClaw build artifacts (multi-stage build) | [Dockerfile.openclaw-app](./Dockerfile.openclaw-app) |
| **Layer 3** | `openclaw:{version}` | Custom layer with subagent-coordinator + Hermes + skills | [Dockerfile.openclaw-overlay](./Dockerfile.openclaw-overlay) |

逐行解读：
- **Layer 1（基座层）**：最大、最重但最稳定，包含 SSH、多种包管理器（uv/bun/pnpm/npm）、Playwright + Chromium 浏览器自动化栈、gosu（降权运行）、ffmpeg（多媒体处理）、rsync（文件同步）——是上层运行时的"操作系统级"基础设施。
- **Layer 2（应用层）**：多阶段构建产物，仅承载 OpenClaw 官方代码构建结果，与 Layer 1 解耦以便独立升级 OpenClaw 上游。
- **Layer 3（定制层）**：本项目差异化核心，集成 `subagent-coordinator`（子智能体协调器）、`Hermes`（信使/调度组件）与 `skills`（技能包），用户最终拉取的 `openclaw:2026.5.22` 正是该层。

### 表 3：Build Parameters（构建参数）

| Parameter | Description | Required | Example Value |
|-----------|-------------|----------|---------------|
| VERSION | OpenClaw version number | No | 2026.5.22 |
| REGISTRY | Image registry prefix | No | localhost |
| OFFLINE | Offline mode, use local sources only (default false) | No | true |
| SKIP_BASE | Whether to skip base image build (default false) | No | true |
| SKIP_APP | Whether to skip app image build (default false) | No | true |
| SKIP_OVERLAY | Whether to skip overlay image build (default false) | No | true |
| SKIP_PLUGINS | Whether to skip plugin preparation (default false) | No | true |
| OPENCLAW_SRC | OpenClaw source code directory | No | /path/to/openclaw-src |
| HERMES_SRC | Hermes Agent source code directory | No | /path/to/hermes-src |
| DOCKER_REGISTRY_NPM | NPM mirror URL | No | https://registry.npmmirror.com |

逐行解读：所有参数均**非必填**（No），默认值/示例值已覆盖典型场景：
- `VERSION` 与 `REGISTRY` 控制镜像 tag 与仓库前缀（如改为 `myregistry.com/` 推私有仓）；
- `OFFLINE=true` 切离线模式；
- 四个 `SKIP_*` 开关实现分层增量构建；
- `OPENCLAW_SRC` / `HERMES_SRC` 允许指向本地源码目录进行内嵌构建（非拉取远程）；
- `DOCKER_REGISTRY_NPM` 注入 NPM 镜像以加速/离线。

### 表 4：Skills Mounting Mechanism（技能挂载机制三阶段）

| Stage | Path | Description |
|-------|------|-------------|
| In image | `/home/node/.openclaw/skills-shared/` | Skills packaged in the overlay layer (extracted at deploy time, shadowed by bind mount at runtime) |
| Host | `openclaw-configs/skills-merged/` | Merge directory (image skills + host skills union, host takes priority) |
| Container | `/home/node/.openclaw/skills/` | bind mount from `skills-merged/`, where Gateway loads skills |

逐行解读：
- **In image**：overlay 层打包的内置 skills，部署时被解压，但运行时被 bind mount "shadow"（遮盖）——这是一种"出厂预装但不强制"的模式。
- **Host**：合并目录是真实生效层，镜像内置与主机自定义 skills 做 union，主机同名文件覆盖镜像内置——为二次开发与运维热更新留出空间。
- **Container**：最终 bind mount 到 Gateway 加载路径，路径 `/home/node/.openclaw/skills/` 即 Agent 运行时查找技能的入口。

### 表 5：Supported Hardware Architectures（支持的硬件架构）

| Architecture | Description |
|--------------|-------------|
| x86_64 | Intel/AMD 64-bit architecture |
| aarch64 | ARM 64-bit architecture |

逐行解读：覆盖主流服务器（Intel/AMD）与 ARM 服务器（如华为鲲鹏）两类部署目标，与华为云生态紧密契合。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文末提供的内部链接，可构建如下文档依赖图：

- **同级文档**：[`./OVERVIEW.zh.md`](./OVERVIEW.zh.md) —— 本文档的中文翻译版本，互为镜像供不同语言用户查阅。
- **三层 Dockerfile 链**：
  - [`./Dockerfile.openclaw-base`](./Dockerfile.openclaw-base) —— 实现 Layer 1 基座层，封装所有系统级依赖（SSH/包管理器/浏览器/多媒体/同步工具）。
  - [`./Dockerfile.openclaw-app`](./Dockerfile.openclaw-app) —— 实现 Layer 2 应用层，多阶段构建 OpenClaw 官方产物。
  - [`./Dockerfile.openclaw-overlay`](./Dockerfile.openclaw-overlay) —— 实现 Layer 3 定制层，注入 subagent-coordinator、Hermes 与 skills，是 AgentSDK 区别于原生 OpenClaw 的关键所在。
- **上游链接**：文档顶部指向 [`AgentSDK Openclaw Documentation`](https://gitcode.com/Ascend/AgentSDK/blob/master/openclaw/README.md) 与 [`Issue Feedback`](https://gitcode.com/Ascend/AgentSDK/issues)，说明本文档是 AgentSDK 仓 `openclaw/docker/` 子目录下聚焦 Docker 交付的专题文档，需结合仓根目录 README 理解整体框架能力。

---

## 【使用方法】

**1. 构建镜像**（原文命令）：
```bash
cd AgentSDK/openclaw/docker
bash ./build-openclaw.sh                    # 一键构建三层
bash ./build-openclaw.sh --skip-base --skip-app   # 仅构建 overlay 层
```
配合构建参数使用示例：
```bash
OFFLINE=true DOCKER_REGISTRY_NPM=https://registry.npmmirror.com \
OPENCLAW_SRC=/path/to/openclaw-src HERMES_SRC=/path/to/hermes-src \
bash ./build-openclaw.sh
```

**2. 部署容器**（原文命令）：
```bash
API_KEY=api-key bash ./scripts/deploy.sh quick \
  -n 1 \
  -m mode-name \
  -u http://xxxx.xx.xx.xx:xxxx \
  -p xxxx \
  -i openclaw:2026.5.22 \
  --skills \
  --name openclaw-test
```
参数语义：`-n` 实例数，`-m` 模式名，`-u` 服务地址，`-p` 端口，`-i` 镜像 tag，`--skills` 启用 skills 合并挂载，`--name` 容器名。

**3. 二次开发**（原文 Dockerfile 模板）：
以 `openclaw:2026.5.22` 为基座，安装额外 apt 包、pip 包，并通过 `COPY` 将自定义 skills 注入 `skills-shared/`，最后以 `CMD ["node", "openclaw.mjs", "gateway"]` 启动网关。

**4. 动态添加技能**（原文命令）：
```bash
# 方式一：操作主机合并目录
cp -r ./my-skill openclaw-configs/skills-merged/my-skill/
chmod -R 755 openclaw-configs/skills-merged/my-skill/

# 方式二：直接操作容器路径（等价，因 bind mount 互通）
docker cp ./my-skill openclaw-1:/home/node/.openclaw/skills/my-skill/
```
添加后通过 WebUI `/restart` 或 `docker exec openclaw-1 pkill -u node -f gateway` 重启网关（健康监控自动拉起）。

**5. 拉取官方镜像**（原文）：
```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/openclaw:2026.5.22
```
