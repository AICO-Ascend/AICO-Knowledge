# MindStudio Insight

> 仓 `msinsight` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docker/OVERVIEW.zh.md

# MindStudio Insight Docker 镜像文档深度解读

---

## 【定位】

本篇文档系统阐述了 **MindStudio Insight 工具的 Docker 镜像交付方案**，解决"如何以容器化方式快速部署、跨平台分发、且兼顾安全访问（mTLS）与轻量访问（HTTP）的昇腾深度学习可视化调优分析工具"这一核心问题。

---

## 【技术要点】

1. **Tag 规范体系**：镜像 Tag 严格遵循 `{版本号}-{操作系统}-{Python版本}` 三段式结构，例如 `26.1.0-ubuntu22.04-py3.10`、`26.1.0-openeuler24.03-py3.11`。
2. **多架构并行发布**：默认镜像以多架构 manifest 形式发布，同一 Tag 同时支持 `x86_64` 与 `aarch64` 两种架构，由 Docker 运行时按环境自动选择。
3. **双模式网络服务**：内置 `nginx.conf`（HTTPS + mTLS）与 `nginx-http.conf`（HTTP）两套配置，前者对应生产级双向认证，后者面向开发/测试；`ws-map.conf` 专门负责 WebSocket Upgrade 请求检测，以代理前端到后端服务的实时通信。
4. **构建参数与架构映射**：提供三个构建参数 `VERSION`（默认 `26.1.0`）、`TAG`（默认 `26.1.0`）、`TARGETARCH`（BuildKit/buildx 注入，取值 `amd64`/`arm64`），并在 Dockerfile 内完成 Docker 架构到发布包架构的映射（`amd64`→`x86_64`、`arm64`→`aarch64`）。
5. **安全下载与完整性校验**：构建过程中自动下载 `MindStudio-Insight_${VERSION}_linux_${INSIGHT_ARCH}.zip` 及对应 `.sha256` 文件，构建在 SHA256 校验失败时会终止，保证包源完整性。
6. **进程治理与运行时依赖**：`supervisord.conf` 负责容器内进程管理，`requirements.txt` 声明 Python 运行时依赖，`entrypoint.sh` 担任容器启动脚本。

---

## 【关键机制与数据】

**工作原理 / 数据流：**

- **镜像启动后行为**：容器将根路径 `/` 重定向到 `/?proxy=true`，前端据此连接当前浏览器端口；nginx 将 WebSocket 流量反向代理至容器内后端服务（原文："前端会连接当前浏览器端口，nginx 将 WebSocket 流量代理到容器内后端服务"）。
- **HTTPS + mTLS 模式**：基于 nginx 本身的 mTLS 双向认证能力，在 TLS 加密基础上要求客户端提供证书；需将宿主机证书目录挂载至容器的 `/etc/nginx/certs`，目录内必须包含 `server.crt`、`server.key`、`ca.crt` 三个文件。
- **HTTP 模式**：直接通过容器 80 端口对外提供无加密服务，原文明确指出"不提供传输层加密，也不适合作为生产环境默认使用方式"。

**性能数据 / 关键指标（原文）：**

- 原文定位描述："通过可视化手段呈现真实的软硬件运行数据，帮助开发者在**天级时间**内精准定位并解决性能瓶颈"。
- 端口映射示例：HTTPS + mTLS 模式将容器 443 端口映射到宿主机 `9443`；HTTP 模式将容器 80 端口映射到宿主机 `9880`（宿主机端口"可按需替换"）。

**架构标识映射（原文）：**

| Docker `TARGETARCH` | 发布包架构 |
|---|---|
| `amd64` | `x86_64` |
| `arm64` | `aarch64` |

---

## 【表格解读】

### 表格 1：Tag 规范字段说明

| 字段 | 说明 | 示例值 |
| ------ | ------ | ------ |
| 版本号 | MindStudio Insight 版本 | `26.1.0` |
| 操作系统 | 镜像基础操作系统 | `ubuntu22.04`、`openeuler24.03` |
| Python版本 | 镜像内置Python版本 | `3.10` |

**逐行解读：**
- **版本号**：标识 MindStudio Insight 自身的软件发布版本，与 Tag 中第一段对应；当前示例值 `26.1.0` 与下文构建参数默认值一致，说明这是一个具体的发行版本。
- **操作系统**：决定底层 OS 类型，原文给出了两种候选——Ubuntu 22.04 与 openEuler 24.03，覆盖国内外主流服务器发行版。
- **Python 版本**：镜像内置的 Python 解释器主版本号，原文示例给出 `3.10`，与下文 `26.1.0-ubuntu22.04-py3.10` 对应；openEuler 镜像则内置 `3.11`。

---

### 表格 2：当前支持的 Tag 与 Dockerfile 链接

| Tag | 操作系统 | 内置Python版本 | Dockerfile |
| ------ | ------ | ------ | ------ |
| `26.1.0-ubuntu22.04-py3.10` | Ubuntu 22.04 | 3.10 | [Dockerfile.ubuntu](https://gitcode.com/Ascend/msinsight/blob/master/docker/Dockerfile.ubuntu) |
| `26.1.0-openeuler24.03-py3.11` | openEuler 24.03 LTS | 3.11 | [Dockerfile.openEuler](https://gitcode.com/Ascend/msinsight/blob/master/docker/Dockerfile.openEuler) |

**逐行解读：**
- **第一行 `26.1.0-ubuntu22.04-py3.10`**：以 Ubuntu 22.04 为底座、内置 Python 3.10 的 26.1.0 版本镜像，对应源码仓库中的 `Dockerfile.ubuntu`。
- **第二行 `26.1.0-openeuler24.03-py3.11`**：以 openEuler 24.03 LTS 为底座、内置 Python 3.11 的同主版本镜像，对应 `Dockerfile.openEuler`，体现了同一主版本下通过不同底座 OS 与 Python 版本进行差异化的发布策略。

---

### 表格 3：构建参数说明

| 参数 | 说明 | 默认值 |
| ------ | ------ | ------ |
| `VERSION` | MindStudio Insight 软件包版本 | `26.1.0` |
| `TAG` | MindStudio Insight 发布 Tag | `26.1.0` |
| `TARGETARCH` | Docker 构建目标架构，由 BuildKit/buildx 注入 | `amd64` 或 `arm64` |

**逐行解读：**
- **`VERSION`**：控制下载的 MindStudio Insight 软件包具体版本号（`MindStudio-Insight_${VERSION}_linux_${INSIGHT_ARCH}.zip`），默认 `26.1.0`。
- **`TAG`**：用于拼装发布 Tag `tag_MindStudio_${TAG}`，从而定位正确的 release 下载路径，默认与 VERSION 一致为 `26.1.0`。
- **`TARGETARCH`**：由 BuildKit/buildx 在构建时自动注入，标识目标 CPU 架构；`amd64` 对应 x86 服务器，`arm64` 对应鲲鹏/ARM 服务器。

---

### 表格 4：Docker 架构到发布包架构映射

| Docker `TARGETARCH` | 发布包架构 |
| ------ | ------ |
| `amd64` | `x86_64` |
| `arm64` | `aarch64` |

**逐行解读：**
- **`amd64` → `x86_64`**：Docker 生态的架构命名 `amd64` 在 MindStudio Insight 官方发布包中被命名为 `x86_64`，映射后才能拼出正确的下载文件名 `${INSIGHT_ARCH}`。
- **`arm64` → `aarch64`**：同理，Docker 命名 `arm64` 对应昇腾/ARM 服务器包名 `aarch64`。该映射是构建过程中"自动下载发布包"步骤能正确命中的关键。

---

## 【公式解读】

**原文无公式**。

（全文未出现 LaTeX 数学公式或伪代码公式，仅出现 Tag 模板字符串 `tag_MindStudio_${TAG}`、URL 模板 `MindStudio-Insight_${VERSION}_linux_${INSIGHT_ARCH}.zip` 等字符串拼接占位符，本质为 Shell 变量替换语法，非数学/逻辑公式。）

---

## 【关联】

文档虽未提供内部交叉链接（原文标注"内部链接: 无"），但通过外部链接与目录结构清晰描绘了与上下游模块的关系：

- **与代码仓主体的关系**：镜像中运行的 `MindStudio Insight` 软件包来源于 [MindStudio Insight 代码仓](https://gitcode.com/Ascend/msinsight) 的 release 产物，构建过程中通过 `https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_${TAG}/MindStudio-Insight_${VERSION}_linux_${INSIGHT_ARCH}.zip` 下载，是"上游源码仓 → 发布包 → Docker 镜像"三级交付链的最后一环。
- **与昇腾生态文档的关系**：用户帮助入口指向 [MindStudio Insight 昇腾社区文档](https://www.hiascend.com/document/detail/zh/mindstudio/2600/GUI_baseddevelopmenttool/MindStudioInsight/docs/zh/user_guide/overview.md)，说明本 Docker 镜像仅是部署载体，真正的功能说明、性能调优术语均需查阅昇腾官方用户指南。
- **与镜像仓库的关系**：[AscendHub 镜像仓库](https://www.hiascend.com/developer/ascendhub) 是该镜像的官方分发渠道之一，本文档描述的 Tag 与 AscendHub 上架版本保持一致。
- **`docker/` 子模块内部关联**：
  - `Dockerfile.ubuntu` / `Dockerfile.openEuler`：分别对应两类基础镜像的构建脚本，与 `requirements.txt`、`entrypoint.sh`、`supervisord.conf` 在镜像内部协同。
  - `nginx.conf`（HTTPS+mTLS）、`nginx-http.conf`（HTTP）、`ws-map.conf`（WebSocket 检测）：三份 nginx 配置互为补充，构成容器对外提供 Web 服务的完整代理栈。
  - `OVERVIEW.md` 与 `OVERVIEW.zh.md`：同一份说明文档的英文版与中文版，本文件即中文版。
- **与许可证的关系**：镜像遵循 [MulanPSL2](https://gitcode.com/Ascend/msinsight/blob/master/License)，文档"免责声明"章节进一步声明了预装第三方软件包（Python、系统库等）的许可证约束自负责任。

---

## 【使用方法】

### 一、运行（推荐 HTTPS + mTLS 模式）

**前置条件**：自行准备证书目录，包含 `server.crt`、`server.key`、`ca.crt`，并挂载到容器 `/etc/nginx/certs`。

```bash
docker run -d \
  -p <host_https_port>:443 \
  -v /path/to/profile_data:/opt/insight/data \
  -v /path/to/certs:/etc/nginx/certs:ro \
  --name msinsight \
  msinsight:26.1.0-ubuntu22.04-py3.10
```

浏览器访问：`https://<host_ip>:9443`（原文示例宿主机端口），客户端需提供证书完成 mTLS 双向认证。

### 二、运行（HTTP 模式，仅开发/测试）

```bash
docker run -d \
  -p <host_http_port>:80 \
  -v /path/to/profile_data:/opt/insight/data \
  --name msinsight \
  msinsight:26.1.0-ubuntu22.04-py3.10
```

浏览器访问：`http://<host_ip>:9880`（原文示例宿主机端口）。原文明确警告该模式"不提供传输层加密，也不适合作为生产环境默认使用方式"。

### 三、本地构建 Ubuntu 镜像

```bash
cd docker

docker build \
  -f Dockerfile.ubuntu \
  --build-arg VERSION={version} \
  --build-arg TAG={tag} \
  --build-arg TARGETARCH={arch} \
  -t {msinsight_tag} .
```

### 四、本地构建 openEuler 镜像

```bash
cd docker

docker build \
  -f Dockerfile.openEuler \
  --build-arg VERSION={version} \
  --build-arg TAG={tag} \
  --build-arg TARGETARCH={arch} \
  -t {msinsight_tag} .
```

### 五、二次开发（基于正式镜像制作自定义镜像）

```dockerfile
FROM msinsight:26.1.0-ubuntu22.04-py3.10

# 根据需要添加自定义构建步骤。
```

### 六、关键配置项 / 命令汇总

| 配置/命令 | 说明 |
|---|---|
| `<host_https_port>:443` | 容器 443 端口映射到宿主机 HTTPS 端口（示例 `9443`） |
| `<host_http_port>:80` | 容器 80 端口映射到宿主机 HTTP 端口（示例 `9880`） |
| `-v /path/to/profile_data:/opt/insight/data` | 挂载 profile 数据目录到容器 |
| `-v /path/to/certs:/etc/nginx/certs:ro` | HTTPS + mTLS 模式挂载证书目录（只读） |
| `--build-arg VERSION={version}` | 构建参数：MindStudio Insight 版本号 |
| `--build-arg TAG={tag}` | 构建参数：发布 Tag |
| `--build-arg TARGETARCH={arch}` | 构建参数：目标架构 `amd64` 或 `arm64` |
| `/etc/nginx/certs` 内必备文件 | `server.crt`、`server.key`、`ca.crt` |

### 七、访问说明（原文）

- `<host_ip>` 为容器所在宿主机 IP，需确保对应宿主机端口在客户端网络可达。
- 容器将根路径 `/` 重定向到 `/?proxy=true`，前端连接当前浏览器端口，nginx 代理 WebSocket 至后端。
