# image_download_mirror.inc

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/quick_start/ascend_image/image_download_mirror.inc.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/quick_start/ascend_image/image_download_mirror.inc.md

# vllm-ascend 镜像下载加速指南 — 一体化深度解读

---

## 【定位】

这篇文档解决"vLLM Ascend 官方 Docker 镜像从默认 `quay.io` 拉取过慢"的实际问题,提供了若干**镜像加速源 (registry mirror)** 及其使用方式,属于安装/部署前的网络层辅助说明 (被归入 `ascend_image` 快速开始小节)。

---

## 【技术要点】

- **默认源**:vLLM Ascend 镜像**默认**从 `quay.io` 拉取 (原文:"vLLM Ascend images are downloaded from `quay.io` by default")。
- **加速源选择**:提供 **两个** 加速镜像仓库供替换:
  1. `m.daocloud.io/quay.io/ascend/vllm-ascend`
  2. `quay.nju.edu.cn/ascend/vllm-ascend`
- **镜像地址模板**:原始形如 `quay.io/ascend/vllm-ascend:<TAG>`,替换为上述前缀后即可。
- **TAG 处理方式**:**仅替换 registry 前缀**,完整保留**原 tag**,原文明确列出**四种后缀**不可丢:
  - `-a3`
  - `-310p`
  - `-950dt`
  - `-openeuler`
- **TAG 占位**:原文用 `{{ vllm_ascend_version }}` (Sphinx/Jinja 模板变量) 作为占位,实际使用时替换为目标版本。
- **拉取命令**:使用标准 `docker pull` 命令,变量 `$TAG` 由 shell 注入。

---

## 【关键机制与数据】

**工作原理 (registry 前缀替换机制)**:

- 原文:quay.io 提供的是 container registry 服务 (`vllm-ascend` 镜像托管于此)。
- 原文:当用户网络到 `quay.io` 的链路拥塞/高延迟时,通过**国内/第三方镜像缓存** (`m.daocloud.io`、`quay.nju.edu.cn`) 拉取相同 image,可获得更优下载速度。
- 原文:替换规则是**字符串前缀替换**,镜像仓库路径 (除前缀外) 与 tag 全部保持一致,确保拉到的是**完全相同**的镜像内容 (包括 chip 后缀与 OS 后缀)。

**性能数据**:原文**未提供**任何速率、延迟、可用性等量化数据,仅给出"slow"的定性描述。

**镜像 tag 后缀语义 (基于原文枚举)**:

| 后缀 | 原文出现位置 | 含义推断 (原文未明示) |
|---|---|---|
| `-a3` | 原文枚举 | 原文未说明 |
| `-310p` | 原文枚举 | 原文未说明 |
| `-950dt` | 原文枚举 | 原文未说明 |
| `-openeuler` | 原文枚举 | 原文未说明 |

> ⚠️ 严格遵循"不臆造原文没有的机制"原则,后缀具体含义(芯片型号/操作系统)原文并未解释,故仅以"原文枚举"形式保留。

---

## 【表格解读】

**原文无表格**。

(全文为一段 tip 说明 + 三段代码块,无任何 markdown 表格。)

---

## 【公式解读】

**原文无公式**。

(无 LaTeX 或伪代码形式的公式,命令片段为 shell 与纯文本。)

---

## 【关联】

- **上下文**:本文件路径位于 `docs/source/getting_started/quick_start/ascend_image/`,作为 `.inc.md` (include) 文件,被 `ascend_image` 快速开始章节的其它页面 **include 引用**,而非独立文档。
- **被引用的下游 (推断)**:根据同名目录结构,通常会被 `quick_start.md` 或同级 `installation.md` 通过 `!!! include` / `{% include %}` 嵌入,作为"镜像拉取慢"的旁注 (tip)。
- **上下游依赖**:
  - **上游**:`vllm_ascend_version` 变量 (Jinja/Sphinx 配置中定义),用于渲染 `{{ vllm_ascend_version }}` 占位符。
  - **下游**:与同名目录内的 `ascend_image` 镜像构建/拉取主流程文档配套使用。
- 原文**未给出**任何与 Ascend NPU、`torch_npu`、vLLM 推理特性、模型本身的交叉引用;本文件**仅聚焦于镜像下载网络层**。

---

## 【使用方法】

**启用方式 (原文命令)**:

```bash
# 1. 指定目标 TAG
TAG=<你想要的镜像 tag, 例如 v0.7.x 或具体版本>

# 2. 方案 A:使用 DaoCloud 镜像
docker pull m.daocloud.io/quay.io/ascend/vllm-ascend:$TAG

# 3. 方案 B:使用南京大学镜像 (quay.nju.edu.cn)
docker pull quay.nju.edu.cn/ascend/vllm-ascend:$TAG
```

**关键约束 (原文强调)**:

- **只替换 registry 前缀**,镜像仓库 `quay.io/ascend/vllm-ascend` 与 `$TAG` 必须**完整保留**。
- 若目标 tag 形如 `<ver>-a3`、`<ver>-310p`、`<ver>-950dt`、`<ver>-openeuler`,这些**后缀不可省略**。

**配置项 / 配置文件 / 初始化步骤**:原文**未涉及**任何配置文件、启动参数或环境变量设置,全部为一次性 `docker pull` 命令。
