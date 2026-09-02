# AgentSDK Openclaw Docker

> 仓 `agentsdk` · 路径 `openclaw/docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agentsdk/openclaw/docker/OVERVIEW.zh.md

# AgentSDK Openclaw Docker 文档深度解读

---

## 【定位】

本文档系统介绍 AgentSDK Openclaw（基于 OpenClaw 构建的多领域 Agent 框架）的 Docker 镜像架构设计、Tag 规范、构建参数、部署与二次开发方法，重点阐述三层镜像分层结构与技能（skills）合并挂载机制，为用户提供从镜像构建、容器部署到自定义扩展的完整使用指南。

---

## 【技术要点】

1. **三层镜像分层架构**：采用 base（基础设施层）→ app（OpenClaw 官方产物层）→ overlay（subagent-coordinator + Hermes + skills 定制层）的分层设计，每层可独立构建与缓存复用，分别由 [Dockerfile.openclaw-base](./Dockerfile.openclaw-base)、[Dockerfile.openclaw-app](./Dockerfile.openclaw-app)、[Dockerfile.openclaw-overlay](./Dockerfile.openclaw-overlay) 三个构建文件实现。

2. **Tag 规范与镜像示例**：Tag 格式为 `<Openclaw 版本号>`（如 `2026.5.22`），完整镜像地址为 `swr.cn-south-1.myhuaweicloud.com/ascendhub/openclaw:2026.5.22`，托管在昇腾社区镜像仓库 `https://www.hiascend.com/developer/ascendhub`。

3. **基础镜像预装组件**：Layer 1（base）集成 SSH、uv、bun、pnpm、npm 全局包、pip 包、Playwright、Chromium、gosu、ffmpeg、rsync 等基础设施，覆盖前端、后端、浏览器自动化与多媒体处理等多个运行时场景。

4. **构建参数体系**：共 10 个构建参数（VERSION、REGISTRY、OFFLINE、SKIP_BASE、SKIP_APP、SKIP_OVERLAY、SKIP_PLUGINS、OPENCLAW_SRC、HERMES_SRC、DOCKER_REGISTRY_NPM），支持分层跳过、离线模式、NPM 镜像替换等灵活构建策略。

5. **技能合并挂载机制**：通过三层路径映射（镜像内 `skills-shared/` → 宿主机 `skills-merged/` → 容器内 `skills/`）实现"镜像技能 + 宿主机技能取并集，宿主机优先"的合并策略，并支持 `docker cp` 或宿主目录直接操作的动态添加方式。

6. **多架构硬件支持**：同时支持 x86_64（Intel/AMD 64 位）与 aarch64（ARM 64 位）两种 CPU 架构，适配昇腾及通用服务器部署场景。

---

## 【关键机制与数据】

### 三层镜像构建流程（原文："构建 AgentSDK Openclaw 镜像"）

原文通过统一脚本 `bash ./build-openclaw.sh` 一键构建全部三层镜像，支持 `--skip-base` 与 `--skip-app` 参数跳过基础层与应用层，复用已有镜像以加速增量构建——这表明三层之间存在严格的层间依赖：overlay 层依赖 app 层，app 层依赖 base 层。

### 技能挂载数据流（原文"技能挂载机制"小节）

数据流向为：**镜像构建阶段**将技能打入 `/home/node/.openclaw/skills-shared/`；**部署阶段**脚本提取该目录内容并与宿主机技能取并集后写入 `openclaw-configs/skills-merged/`；**容器运行时**通过 bind mount 将合并目录挂载到容器内 `/home/node/.openclaw/skills/`，供 Gateway 加载。原文强调"运行时被 bind mount 遮蔽"，意味着容器内路径在运行时不再可见镜像内置技能，仅显示合并后的视图。

### 二次开发叠加模式（原文"如何二次开发"小节）

用户可通过 `FROM openclaw:2026.5.22` 继承最终镜像，并叠加 `apt` 系统包、`pip3` Python 包（使用 `--break-system-packages` 与阿里云 PyPI 镜像 `-i https://mirrors.aliyun.com/pypi/simple`）以及自定义技能目录 `COPY --chown=root:root ./custom-skills/ /home/node/.openclaw/skills-shared/`，最终通过 `CMD ["node", "openclaw.mjs", "gateway"]` 启动 Gateway 服务。

### 健康探针与重启机制（原文"动态添加技能"小节）

原文："在 WebUI 中输入 `/restart`，或执行 `docker exec openclaw-1 pkill -u node -f gateway`（健康探针会自动拉起）"——表明容器内置健康探针会监控 Gateway 进程，进程被 kill 后会自动重启，实现技能热加载而无需重建镜像。

---

## 【表格解读】

### 表格 1：Tag 规范字段说明（原文逐字还原）

| 字段          | 示例值          | 说明                             |
|-------------|---------------|--------------------------------|
| Openclaw 版本号 | 2026.5.22         | 对应 OpenClaw 官方发布版本标识        |

**逐行解读**：该表定义了镜像 Tag 的唯一字段"Openclaw 版本号"，示例值 `2026.5.22` 采用 `YYYY.M.D`（年.月.日）格式，与 OpenClaw 官方发布版本一一对应。该设计表明镜像版本严格绑定上游 OpenClaw 版本，便于追踪与回滚。

---

### 表格 2：三层镜像架构（原文逐字还原）

| 层级 | 镜像标签 | 说明 | 构建文件 |
|------|---------|------|----------|
| **Layer 1** | `openclaw:base-{版本号}` | SSH/uv/bun/pnpm/npm全局包/pip包/Playwright/Chromium/gosu/ffmpeg/rsync 等基础设施 | [Dockerfile.openclaw-base](./Dockerfile.openclaw-base) |
| **Layer 2** | `openclaw:app-{版本号}` | 官方 OpenClaw 构建产物（多阶段构建） | [Dockerfile.openclaw-app](./Dockerfile.openclaw-app) |
| **Layer 3** | `openclaw:{版本号}` | subagent-coordinator + Hermes + skills 定制层 | [Dockerfile.openclaw-overlay](./Dockerfile.openclaw-overlay) |

**逐行解读**：

- **Layer 1（基础层）**：镜像标签 `openclaw:base-{版本号}`，承担基础设施角色，预装 SSH（远程登录）、uv（Python 包管理）、bun（JS 运行时）、pnpm/npm（Node.js 包管理）、Playwright + Chromium（浏览器自动化）、gosu（降权启动）、ffmpeg（多媒体处理）、rsync（文件同步）等 10+ 类工具，覆盖 Agent 框架所需的全部运行时依赖。该层变更频率低，可作为长期缓存基础。
- **Layer 2（应用层）**：镜像标签 `openclaw:app-{版本号}`，承载官方 OpenClaw 构建产物，文中特别标注"多阶段构建"，表明该 Dockerfile 通过多阶段构建减小最终镜像体积，仅引入 OpenClaw 运行时所需的必要文件。
- **Layer 3（扩展层）**：镜像标签 `openclaw:{版本号}`（无 `app-` 或 `base-` 前缀，为默认入口标签），在 Layer 2 之上叠加 AgentSDK 特有的三个组件：`subagent-coordinator`（子 Agent 协调器）、`Hermes`（Agent 引擎）、`skills`（技能库），是 AgentSDK Openclaw 区别于上游 OpenClaw 的核心差异化层。

---

### 表格 3：构建参数（原文逐字还原）

| 参数               | 说明                               | 必填 | 示例值                                                |
|------------------|----------------------------------|----|----------------------------------------------------|
| VERSION     | OpenClaw 版本号                    | 否  | 2026.5.22                                              |
| REGISTRY | 镜像仓库前缀 | 否 | localhost |
| OFFLINE | 离线模式，仅使用本地源码（默认 false） | 否 | true |
| SKIP_BASE | 是否跳过基础镜像构建（默认 false） | 否 | true |
| SKIP_APP | 是否跳过应用镜像构建（默认 false） | 否 | true |
| SKIP_OVERLAY | 是否跳过扩展镜像构建（默认 false） | 否 | true |
| SKIP_PLUGINS | 是否跳过插件准备（默认 false） | 否 | true |
| OPENCLAW_SRC | OpenClaw 源码目录 | 否 | /path/to/openclaw-src |
| HERMES_SRC | Hermes Agent 源码目录 | 否 | /path/to/hermes-src |
| DOCKER_REGISTRY_NPM | NPM 镜像地址 | 否 | https://registry.npmmirror.com |

**逐行解读**：

- **VERSION**：指定 OpenClaw 版本号（如 `2026.5.22`），非必填表明脚本有默认值机制。
- **REGISTRY**：镜像仓库前缀（如 `localhost`），用于本地构建场景；上传到昇腾社区时应切换为相应前缀。
- **OFFLINE**：离线模式开关（默认 `false`），设为 `true` 时仅使用本地源码（`OPENCLAW_SRC`、`HERMES_SRC`），避免联网拉取上游代码，适用于内网受限环境。
- **SKIP_BASE / SKIP_APP / SKIP_OVERLAY**：三个布尔开关（默认 `false`）分别控制是否跳过对应层构建，配合 `--skip-base --skip-app` 等命令行参数实现增量构建，可显著缩短二次构建耗时。
- **SKIP_PLUGINS**：跳过插件准备步骤（默认 `false`），适用于纯 OpenClaw 部署而无需 AgentSDK 插件的场景。
- **OPENCLAW_SRC / HERMES_SRC**：离线模式下指向本地源码目录的路径，是 `OFFLINE=true` 时的必填依赖。
- **DOCKER_REGISTRY_NPM**：NPM 镜像地址（默认 `https://registry.npmmirror.com`），可在网络受限时替换为公司内部 NPM 私服。

---

### 表格 4：技能挂载机制（原文逐字还原）

| 阶段 | 路径 | 说明 |
|------|------|------|
| 镜像内 | `/home/node/.openclaw/skills-shared/` | 覆盖层打包的技能（部署时提取，运行时被 bind mount 遮蔽） |
| 宿主机 | `openclaw-configs/skills-merged/` | 合并目录（镜像技能 + 宿主机技能取并集，宿主机优先） |
| 容器内 | `/home/node/.openclaw/skills/` | bind mount 自 `skills-merged/`，Gateway 加载技能的路径 |

**逐行解读**：

- **镜像内阶段**：技能被打包到 `/home/node/.openclaw/skills-shared/` 目录，是 Layer 3（overlay）构建产物的一部分；运行时该路径被 bind mount 完全遮蔽，仅在构建/提取阶段可见。
- **宿主机阶段**：`openclaw-configs/skills-merged/` 是部署脚本在宿主机生成的合并目录，实现"镜像技能 + 宿主机技能取并集，宿主机优先"的合并语义——即同名技能时宿主机版本覆盖镜像版本。
- **容器内阶段**：`/home/node/.openclaw/skills/` 是 bind mount 挂载点，Gateway 进程从此路径加载技能，是容器运行时唯一可见的技能视图。

---

### 表格 5：支持的硬件架构（原文逐字还原）

| 架构 | 说明 |
|------|------|
| x86_64 | Intel/AMD 64位架构 |
| aarch64 | ARM 64 位架构 |

**逐行解读**：

- **x86_64**：覆盖 Intel 与 AMD 主流服务器 CPU，适用通用云与本地数据中心。
- **aarch64**：覆盖 ARM 64 位 CPU，包括鲲鹏、飞腾以及昇腾配套的 ARM 宿主环境，适配国产化硬件生态。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档作为 AgentSDK Openclaw Docker 的总览（OVERVIEW），通过以下内部链接与上下游文档形成完整知识网络：

- **英文版**：[./OVERVIEW.md](./OVERVIEW.md) — 与本中文文档结构对应的英文版本，提供双语对照参考。
- **基础层构建文件**：[./Dockerfile.openclaw-base](./Dockerfile.openclaw-base) — 实现 Layer 1（基础设施镜像）的 Dockerfile，定义了 SSH、uv、bun、Playwright、Chromium 等组件的安装逻辑，是 [构建参数表](#表格3构建参数原文逐字还原) 中 `SKIP_BASE` 开关控制的对象。
- **应用层构建文件**：[./Dockerfile.openclaw-app](./Dockerfile.openclaw-app) — 实现 Layer 2（OpenClaw 官方构建产物）的 Dockerfile，使用多阶段构建，对应 `SKIP_APP` 开关控制层。
- **扩展层构建文件**：[./Dockerfile.openclaw-overlay](./Dockerfile.openclaw-overlay) — 实现 Layer 3（subagent-coordinator + Hermes + skills 定制层）的 Dockerfile，对应 `SKIP_OVERLAY` 开关控制层，并直接决定了 [技能挂载机制表](#表格4技能挂载机制原文逐字还原) 中"镜像内 `skills-shared/`"目录的打包内容。

此外，文中引用的外部资源包括：
- [AgentSDK Openclaw 主页](https://gitcode.com/Ascend/AgentSDK/tree/master/openclaw) — 上游代码仓入口
- [AgentSDK Openclaw 文档](https://gitcode.com/Ascend/AgentSDK/blob/master/openclaw/README.md) — 功能与 API 详细文档
- [问题反馈](https://gitcode.com/Ascend/AgentSDK/issues) — Issue 追踪
- [昇腾社区镜像仓库](https://www.hiascend.com/developer/ascendhub) — 镜像托管平台

---

## 【使用方法】

### 1. 构建镜像（原文："构建 AgentSDK Openclaw 镜像"）

```bash
# 一键构建全部三层镜像
cd AgentSDK/openclaw/docker
bash ./build-openclaw.sh

# 仅构建最终镜像（跳过 base 和 app，使用已有镜像）
bash ./build-openclaw.sh --skip-base --skip-app
```

### 2. 部署容器（原文："运行 AgentSDK Openclaw 容器"）

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

参数说明（基于原文）：`-n` 实例数；`-m` 模式名；`-u` 服务地址；`-p` 端口；`-i` 镜像标签；`--skills` 启用技能挂载；`--name` 容器名。

### 3. 二次开发（原文："如何二次开发"小节）

继承 `openclaw:2026.5.22` 作为基础镜像，叠加系统包（`apt install extra-package`）、Python 包（`pip3 install --break-system-packages -i https://mirrors.aliyun.com/pypi/simple extra-python-package`）、自定义技能（`COPY --chown=root:root ./custom-skills/ /home/node/.openclaw/skills-shared/`），最后通过 `CMD ["node", "openclaw.mjs", "gateway"]` 启动。

### 4. 动态添加技能（原文："动态添加技能"小节）

```bash
# 方式一：宿主机直接操作合并目录
cp -r ./my-skill openclaw-configs/skills-merged/my-skill/
chmod -R 755 openclaw-configs/skills-merged/my-skill/

# 方式二：通过容器内路径操作（等价，因是 bind mount）
docker cp ./my-skill openclaw-1:/home/node/.openclaw/skills/my-skill/
```

重启 Gateway 使技能生效：

```bash
# 方式一：WebUI 中输入 /restart
# 方式二：命令行 kill 进程（健康探针会自动拉起）
docker exec openclaw-1 pkill -u node -f gateway
```

### 5. 配置项（构建参数）

见 [表格 3](#表格3构建参数原文逐字还原)，共 10 个参数（VERSION、REGISTRY、OFFLINE、SKIP_BASE、SKIP_APP、SKIP_OVERLAY、SKIP_PLUGINS、OPENCLAW_SRC、HERMES_SRC、DOCKER_REGISTRY_NPM），均非必填，支持离线模式、分层跳过与 NPM 镜像替换。
