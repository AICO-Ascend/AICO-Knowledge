# MindStudio Insight

> 仓 `msinsight` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docker/OVERVIEW.md

# MindStudio Insight Docker 镜像 Overview 深度解读

---

## 【定位】

本文档是 `msinsight` 代码仓 `docker/` 目录下官方 Docker 镜像的**英文总览（OVERVIEW.md）**,系统阐述 MindStudio Insight（面向 Atlas AI 开发者的大模型训练/推理可视化调优分析工具）以**容器化开箱即用 Web 访问模式**部署时的镜像规范、构建参数、运行模式（HTTPS+mTLS / HTTP）、目录结构与本地构建方法,是社区用户在生产、共享分析服务、跨 OS 一致性场景下使用该镜像的总入口说明。

---

## 【技术要点】

1. **镜像定位与价值**:将 MindStudio Insight（深度可视化调优分析工具,面向 Atlas AI 开发者,通过可视化呈现真实软硬件运行时数据,帮助定位并解决性能瓶颈）打包成 Docker 镜像,提供开箱即用的 Web 访问能力,适用于**快速部署、隔离数据分析环境、团队共享分析服务、跨操作系统一致性使用**四种典型场景。

2. **镜像 Tag 命名规范**:严格遵循 `{Version}-{OS}-{Python Version}` 三段式格式;当前主推两个标签:
   - `26.1.0-ubuntu22.04-py3.10`(Ubuntu 22.04 + Python 3.10)
   - `26.1.0-openeuler24.03-py3.11`(openEuler 24.03 LTS + Python 3.11)

3. **多架构(Manifest)支持**:镜像以**多架构 manifest** 形式发布,同一 tag 同时支持 `x86_64` 与 `aarch64`,Docker 自动按运行平台拉取匹配镜像;构建时通过 BuildKit/buildx 注入 `TARGETARCH`(取值 `amd64` 或 `arm64`),并通过映射表转换为发布包架构名(`amd64`→`x86_64`,`arm64`→`aarch64`)。

4. **构建期自动下载与校验**:Dockerfile 在构建期自动从 GitCode releases 下载 `MindStudio-Insight_${VERSION}_linux_${INSIGHT_ARCH}.zip`,**同时下载对应的 `.sha256` 校验文件进行校验**,校验失败则**立即退出构建**,保证镜像完整性。

5. **两种运行模式**:
   - **HTTPS + mTLS 模式**(生产强烈推荐):nginx 内置 mTLS 双向认证,既提供 TLS 加密传输,又要求客户端提供证书身份认证,适合生产、共享分析、需要访问控制场景;需将宿主机证书目录挂载到容器 `/etc/nginx/certs`(包含 `server.crt`、`server.key`、`ca.crt` 三个文件)。
   - **HTTP 模式**(仅限开发/测试/临时访问):无传输层加密,**不适合作为生产默认模式**。

6. **入口路由与 WebSocket 代理**:容器将 `/` 重定向到 `/?proxy=true`,前端连接到当前浏览器端口,**nginx 负责将 WebSocket 流量反向代理到容器内部的后端服务**;同时提供两条 nginx 配置:`nginx.conf`(HTTPS+mTLS)、`nginx-http.conf`(纯 HTTP)、`ws-map.conf`(WebSocket 升级检测 map);进程管理由 `supervisord.conf` 统一编排。

---

## 【关键机制与数据】

### 工作原理 / 数据流(原文提取)

- **镜像加载链**:用户 `docker run` → 容器 entrypoint(`entrypoint.sh`)启动 → supervisor 拉起 nginx + 后端服务 → 浏览器通过 `https://<host_ip>:<port>` 或 `http://<host_ip>:<port>` 访问 → 容器内 `/?proxy=true` 重定向 → 前端通过**当前浏览器端口**建立连接 → **nginx 反向代理 WebSocket 流量至容器内后端**。

- **HTTPS+mTLS 证书链**:宿主机需准备 `server.crt`(服务端证书)、`server.key`(服务端私钥)、`ca.crt`(CA 根证书)三个文件,通过 `-v /path/to/certs:/etc/nginx/certs:ro` **以只读方式**挂载至容器;用户需自行负责**保护证书目录和私钥文件,防止泄露**;浏览器侧通过**客户端证书**完成双向认证。

- **数据卷挂载约定**:profile 数据通过 `-v /path/to/profile_data:/opt/insight/data` 挂载到容器 `/opt/insight/data`,保证宿主机性能剖析数据可被容器内服务分析;同时源数据可在宿主机持久化。

- **构建期下载路径模板**(原文):
  ```text
  https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_${TAG}/MindStudio-Insight_${VERSION}_linux_${INSIGHT_ARCH}.zip
  ```
  配套 `.sha256` 校验文件,失败立即终止构建。

### 性能数据

- **原文无性能数据**(无基准测试数字、吞吐/延迟/显存等指标);文档只描述定位"within days"缩短排障周期,**未给出具体数字**。

---

## 【表格解读】

### 表格 1:Tag 字段含义表(原文逐字还原)

| Field | Description | Example Value |
| ------ | ------ | ------ |
| Version | MindStudio Insight version | `26.1.0` |
| OS | Base operating system of the image | `ubuntu22.04`, `openeuler24.03` |
| Python Version | Built-in Python version of the image | `3.10` |

**逐行解读**:
- **Version**:指 MindStudio Insight 软件本身的版本号,与产品发布节奏对齐;示例 `26.1.0`。
- **OS**:镜像底层操作系统,目前支持 Ubuntu 22.04 与 openEuler 24.03 LTS,反映昇腾/Atlas 生态在两类国产化/通用 OS 上的覆盖策略。
- **Python Version**:镜像内置 Python 版本,直接影响 `requirements.txt` 依赖兼容性;Ubuntu 镜像锁 3.10,openEuler 镜像锁 3.11。

### 表格 2:镜像 Tag 与 Dockerfile 链接表(原文逐字还原)

| Tag | Operating System | Built-in Python Version | Dockerfile |
| ------ | ------ | ------ | ------ |
| `26.1.0-ubuntu22.04-py3.10` | Ubuntu 22.04 | 3.10 | [Dockerfile.ubuntu](https://gitcode.com/Ascend/msinsight/blob/master/docker/Dockerfile.ubuntu) |
| `26.1.0-openeuler24.03-py3.11` | openEuler 24.03 LTS | 3.11 | [Dockerfile.openEuler](https://gitcode.com/Ascend/msinsight/blob/master/docker/Dockerfile.openEuler) |

**逐行解读**:
- **第一行 `26.1.0-ubuntu22.04-py3.10`**:面向通用 Linux 桌面/服务器场景,Debian 系生态依赖最广,镜像源在 Dockerfile.ubuntu。
- **第二行 `26.1.0-openeuler24.03-py3.11`**:面向国产化 OS 场景,Python 升级到 3.11(可能用于支持新语法/性能优化),镜像源在 Dockerfile.openEuler,适合国产化替代栈部署。

### 表格 3:构建参数说明表(原文逐字还原)

| Parameter | Description | Default |
| ------ | ------ | ------ |
| `VERSION` | MindStudio Insight package version | `26.1.0` |
| `TAG` | MindStudio Insight release tag | `26.1.0` |
| `TARGETARCH` | Docker build target architecture injected by BuildKit/buildx | `amd64` or `arm64` |

**逐行解读**:
- **`VERSION`**:控制下载的 Insight 安装包具体版本(用于 zip 包名),默认 `26.1.0`,与产品发布对齐。
- **`TAG`**:控制下载路径中的 release tag(`tag_MindStudio_${TAG}`),默认 `26.1.0`;**注意 `VERSION` 与 `TAG` 当前默认值相同,但语义不同**——`VERSION` 决定安装包版本号,`TAG` 决定 GitCode release 路径。
- **`TARGETARCH`**:由 BuildKit/buildx 自动注入的 Docker 标准架构名(`amd64`/`arm64`),与发布包架构名(见下表)需做映射,镜像内通过 `INSIGHT_ARCH` 派生变量使用。

### 表格 4:Docker 架构名 → 发布包架构名映射表(原文逐字还原)

| Docker `TARGETARCH` | Release Package Architecture |
| ------ | ------ |
| `amd64` | `x86_64` |
| `arm64` | `aarch64` |

**逐行解读**:
- Docker 官方约定的 TARGETARCH 是 `amd64`/`arm64`,而昇腾/Insight 发布包以 `x86_64`/`aarch64` 命名,需要在 Dockerfile 内部做一次映射后才能正确拼出下载 URL 中的 `${INSIGHT_ARCH}` 段。
- **第一行** `amd64` → `x86_64`:Intel/AMD 服务器场景。
- **第二行** `arm64` → `aarch64`:鲲鹏/AArch64 服务器与部分 Atlas 硬件场景。

---

## 【公式解读】

**原文无公式**(无 LaTeX、伪代码或性能公式)。文档中只有**下载 URL 模板**(被当作字符串引用而非公式),其形式为:

```text
https://gitcode.com/Ascend/msinsight/releases/download/tag_MindStudio_${TAG}/MindStudio-Insight_${VERSION}_linux_${INSIGHT_ARCH}.zip
```

其中各占位符含义:
- `${TAG}` — MindStudio Insight 在 GitCode 上的 release tag(默认 `26.1.0`),用于定位发布路径。
- `${VERSION}` — Insight 软件包版本号(默认 `26.1.0`),用于构造 zip 包名。
- `${INSIGHT_ARCH}` — 经 Docker `TARGETARCH` 映射后的真实架构名(`x86_64` 或 `aarch64`),用于构造适配 CPU 架构的包文件名。

---

## 【关联】

文档本身未提供内部交叉链接(文末标注"内部链接: (无)"),但**通过文档内容可梳理出以下模块/上下游关系**:

1. **上游社区与代码仓**:
   - 维护方:[MindStudio Insight community](https://gitcode.com/Ascend/msinsight)
   - 镜像仓:AtlasHub Image Repository(`developer.ascend.com/developer/ascendhub`)
   - Issue 入口:[gitcode.com/Ascend/msinsight/issues](https://gitcode.com/Ascend/msinsight/issues)

2. **官方用户文档(中文)**:MindStudio Insight Atlas Community 上挂载的[中文用户指南 overview](https://www.hiascend.com/document/detail/zh/mindstudio/2600/GUI_baseddevelopmenttool/MindStudioInsight/docs/zh/user_guide/overview.md) — 与本英文 OVERVIEW.md 形成**中英双胞胎**(镜像仓内同时存在 `OVERVIEW.md` 英文版与 `OVERVIEW.zh.md` 中文版),面向不同语种用户。

3. **镜像内嵌模块关系**(目录结构体现):
   - `Dockerfile.ubuntu` / `Dockerfile.openEuler` — 两个 OS 变体的构建脚本,**各自**消费构建参数(VERSION/TAG/TARGETARCH)并自动下载带 .sha256 校验的 Insight 包。
   - `entrypoint.sh` — 容器启动入口。
   - `supervisord.conf` — 进程编排,统一管理 nginx + 后端服务生命周期。
   - `nginx.conf`(HTTPS+mTLS)/ `nginx-http.conf`(HTTP)/ `ws-map.conf`(WebSocket 升级检测 map)— 三份 nginx 配置分别承担**安全访问/HTTP 访问/WebSocket 协议升级**职责,共同实现 `/?proxy=true` 重定向与 WebSocket 反向代理。
   - `requirements.txt` — Python 运行时依赖,对应镜像内置 Python 3.10(ubuntu)/3.11(openEuler)。

4. **许可证与下游责任**:镜像底层 MindStudio Insight 采用 MulanPSL2 许可;镜像本身是**社区版**,以"as is"提供,仅用于学习/研究/开发/测试,不构成任何商业承诺或质量保证;用户需自行评估合规、安全、适配性风险。

---

## 【使用方法】

### 一、运行镜像(从镜像仓拉取后)

#### 1. HTTPS + mTLS 模式(**生产推荐**)

**前置条件**:宿主机准备证书目录,内含 `server.crt`、`server.key`、`ca.crt` 三个文件。

```bash
# 容器 443 映射到宿主机 9443(端口可按需替换)
docker run -d \
  -p <host_https_port>:443 \
  -v /path/to/profile_data:/opt/insight/data \
  -v /path/to/certs:/etc/nginx/certs:ro \
  --name msinsight \
  msinsight:26.1.0-ubuntu22.04-py3.10
```

访问(以宿主端口 `9443` 为例):

```text
https://<host_ip>:9443
```

浏览器侧需通过**客户端证书**完成双向认证。

#### 2. HTTP 模式(**仅限开发/测试/临时访问**)

```bash
# 容器 80 映射到宿主机 9880
docker run -d \
  -p <host_http_port>:80 \
  -v /path/to/profile_data:/opt/insight/data \
  --name msinsight \
  msinsight:26.1.0-ubuntu22.04-py3.10
```

访问:

```text
http://<host_ip>:9880
```

#### 3. 通用访问注意
- `<host_ip>` 为容器所在宿主机 IP;需保证客户端网络可达对应宿主机端口。
- 容器将 `/` 重定向到 `/?proxy=true`,前端连接当前浏览器端口,nginx 反向代理 WebSocket 流量至容器内后端。

### 二、本地构建

#### 1. 构建 Ubuntu 镜像
```bash
cd docker

docker build \
  -f Dockerfile.ubuntu \
  --build-arg VERSION={version} \
  --build-arg TAG={tag} \
  --build-arg TARGETARCH={arch} \
  -t {msinsight_tag} .
```

#### 2. 构建 openEuler 镜像
```bash
cd docker

docker build \
  -f Dockerfile.openEuler \
  --build-arg VERSION={version} \
  --build-arg TAG={tag} \
  --build-arg TARGETARCH={arch} \
  -t {msinsight_tag} .
```

构建参数(默认值见上节"表格 3"):
- `{version}` — Insight 包版本,默认 `26.1.0`
- `{tag}` — release tag,默认 `26.1.0`
- `{arch}` — Docker `TARGETARCH`,`amd64`(→`x86_64`)或 `arm64`(→`aarch64`)
- `{msinsight_tag}` — 自定义镜像 tag

### 三、二次开发(基于官方镜像定制)

```dockerfile
FROM msinsight:26.1.0-ubuntu22.04-py3.10

# Add custom build steps as needed.
```

### 四、关键配置项汇总

| 配置项 | 取值/位置 | 作用 |
| --- | --- | --- |
| 宿主机端口映射 | `-p <port>:443` 或 `-p <port>:80` | 暴露 HTTPS/HTTP 入口 |
| profile 数据卷 | `/opt/insight/data` | 持久化性能剖析数据 |
| 证书卷(HTTPS+mTLS 必选) | `/etc/nginx/certs:ro`,需含 `server.crt`/`server.key`/`ca.crt` | 启用 mTLS 双向认证 |
| 构建参数 | `VERSION` / `TAG` / `TARGETARCH` | 决定下载包版本与架构 |
| OS 变体 | `Dockerfile.ubuntu`(py3.10)/ `Dockerfile.openEuler`(py3.11) | 选择底层 OS 与 Python 版本 |

> 注:端口选择、证书生成、WebSocket 子协议细节、镜像内具体后端进程名等,**原文未涉及**,如需请参考镜像内 README 或官方用户指南。
