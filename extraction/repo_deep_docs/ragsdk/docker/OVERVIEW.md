# RAG SDK

> 仓 `ragsdk` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ragsdk/docker/OVERVIEW.md

# RAG SDK Docker 镜像总览文档深度解读

## 【定位】

本文档是 RAG SDK 在 `docker/` 路径下的**镜像使用总览（OVERVIEW）**，核心解决的是"如何把 RAG SDK 装进 Docker 镜像并在昇腾 Atlas 硬件上跑起来"的问题，完整描述了镜像标签命名规则、版本/CANN 对应关系、构建命令、运行命令、进入容器命令、样例代码位置、自定义开发方式、支持的硬件型号以及许可证查阅入口。

---

## 【技术要点】

1. **镜像标签命名规则**（原文模式串）：`<ragsdk-version>-<chip-series>-<os>-<python-version>`，由四个字段按顺序拼接而成。

2. **CANN 与 RAG SDK 一一对应**：当前文档给出的唯一一条映射关系是 IMAGE `26.0.0` ↔ RAG SDK `26.0.0` ↔ CANN `9.0.0`；CANN 基础镜像版本由所选 Dockerfile 中的 `FROM` 指令决定。

3. **构建命令**：
   ```bash
   docker build --network host -t {your_repo}/ragsdk:<ragsdk-version>-<chip-series>-<os>-<python-version> -f Dockerfile.<chip-series>.<os> .
   ```
   Dockerfile 命名固定为 `Dockerfile.<chip-series>.<os>`。

4. **运行容器时的设备/卷挂载**（原文逐项列出）：
   - 设备挂载：`--device=/dev/davinci_manager`、`--device=/dev/hisi_hdc`、`--device=/dev/devmm_svm`、`--device=/dev/davinci0`
   - 只读卷挂载：`/usr/local/Ascend/driver:/usr/local/Ascend/driver:ro`、`/usr/local/sbin:/usr/local/sbin:ro`、`/path/to/model:/path/to/model:ro`（最后一个由用户按需替换为模型目录）
   - 网络模式：`--network=host`

5. **进入容器命令**：`docker exec -it rag_sdk_demo bash`（容器名为 `rag_sdk_demo`）。

6. **样例与开发基线**：容器内 `/workspace/RAGSDK/example` 提供示例代码；二次开发时以 `swr.cn-south-1.myhuaweicloud.com/ascendhub/ragsdk:26.0.0-910b-ubuntu22.04-py3.11` 为基础镜像，并通过 `FROM` 指令继续叠加自身依赖。

---

## 【关键机制与数据】

**工作机制（一图贯穿，原文有的部分）**：RAG SDK 镜像以"**CANN 基础镜像 + RAG SDK 软件包**"为内容主体，在 Docker 容器中通过挂载昇腾驱动设备（`davinci_manager` / `hisi_hdc` / `devmm_svm` / `davinci0`）使容器内进程能够访问昇腾 NPU，并通过 `/usr/local/Ascend/driver` 的只读挂载复用宿主机驱动。模型文件由用户在 `/path/to/model` 自行放置并以 `:ro` 形式注入容器。

- **原文：** 标签模式串 `<ragsdk-version>-<chip-series>-<os>-<python-version>`，示例取值 RAG SDK Version=`26.0.0`、Chip Series=`910, A3, atlas 300I Pro`、OS=`ubuntu22.04, openeuler24.03`、Python Version=`py3.11`。
- **原文：** 镜像版本对齐矩阵只有一行：`IMAGE version=26.0.0`，`RAG SDK version=26.0.0`，`CANN version=9.0.0`。
- **原文：** 文档以**两块芯片系列 × 两种操作系统**交叉组合后形成的若干 Dockerfile 来支持不同目标，例如 `Dockerfile.910b.ubuntu22.04`；具体支持的 OS 枚举为 `ubuntu22.04`、`openeuler24.03`。
- **原文：** 文档没有给出任何性能/吞吐/时延数字，仅描述能力（功能）与配置项；因此本节不引入性能数据。

---

## 【表格解读】

### 表格 1：标签命名约定字段表（Tag Naming Convention）

| Field            | Example Values  | Description              |
|------------------| -------- |--------------------------|
| RAG SDK Version  | 26.0.0  | RAG SDK version          |
| Chip Series      | 910, A3, atlas 300I Pro    | Target Atlas chip family |
| Operating System | ubuntu22.04, openeuler24.03    | Base operating system    |
| Python Version   | py3.11      | Python version           |

**逐行解读：**
- **RAG SDK Version**：示例 `26.0.0`，即 RAG SDK 自身的版本号，定位到具体软件版本。
- **Chip Series**：示例 `910, A3, atlas 300I Pro`，对应不同 Atlas 家族芯片（Atlas 910 / Atlas A3 / Atlas 300I Pro），用于匹配目标硬件平台。
- **Operating System**：示例 `ubuntu22.04, openeuler24.03`，基础操作系统类型，标识容器底座发行版。
- **Python Version**：示例 `py3.11`，标识容器内 Python 主版本与次版本。

### 表格 2：RAG SDK 镜像版本匹配表（RAG SDK Image Matching Table）

| IMAGE version | RAG SDK version | CANN version |
|---------------|-----------------|--------------|
| 26.0.0        | 26.0.0          | 9.0.0        |

**逐行解读：**
- 当前文档只给出**一行**对齐关系：镜像 `26.0.0` 对应 RAG SDK `26.0.0` 与 CANN `9.0.0`，三者版本号同步增长，确保镜像内 RAG SDK 与底层 CANN 算子/运行时版本严格一致。

### 表格 3：支持的硬件（Supported Hardware）

| Chip Series                | Product Examples   | Architecture                                                         |
| ------------------- | -------- | ------------------------------------------------------------ |
| Atlas 910                | Atlas 800T A2, Atlas 900 A2 PoD  | ARM64/ X86_64                                                     |
| Atlas A3                | Atlas 800T A3    | ARM64/ X86_64                         |
| Atlas 300I Pro                | Atlas 300I Pro、 Atlas 300V Pro    | ARM64/ X86_64                         |

**逐行解读：**
- **Atlas 910**：代表产品 `Atlas 800T A2`、`Atlas 900 A2 PoD`，支持 `ARM64 / X86_64` 两种主机架构。
- **Atlas A3**：代表产品 `Atlas 800T A3`，同样支持 `ARM64 / X86_64`。
- **Atlas 300I Pro**：代表产品 `Atlas 300I Pro`、`Atlas 300V Pro`，支持 `ARM64 / X86_64`。
- 三行覆盖了"训练/推理服务器级（910/A3）"与"边缘/推理卡级（300I Pro/300V Pro）"两类形态，且对 x86 与 ARM 主机均兼容。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **与 CANN 的关系**：RAG SDK 镜像以 CANN 为底座，版本对齐表明确 `IMAGE version 26.0.0` ↔ `CANN version 9.0.0`，且 CANN 版本由所选 Dockerfile 的 `FROM` 指令决定——文档未给出具体 `FROM` 行内容，需要按 Dockerfile 文件实际读取。
- **与昇腾驱动的关系**：运行容器时必须挂载宿主机 `/usr/local/Ascend/driver`（只读）以及四个设备节点（`/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`、`/dev/davinci0`），意味着容器内的 RAG SDK 强依赖宿主机昇腾驱动与设备文件。
- **与样例代码模块的关系**：文档提示样例位于容器内 `/workspace/RAGSDK/example`，并指向 `https://gitcode.com/Ascend/RAGSDK/tree/master/example` 中的 `example` 目录；两者是同一套示例代码的不同访问入口（容器路径 vs 仓库路径）。
- **与 RAG SDK 本体的关系**：本文档不涉及 RAG SDK 内部 API（文档专门给出了 `docs/zh/api/README.md` 与《RAG SDK 文档》链接作为下游查阅入口），只描述镜像层这一**外围**使用方式。
- **与许可证的关系**：镜像内置的 RAG SDK 与 Mind 系列软件遵循 `LICENSE.md`；容器中其它预装包（Python、系统库等）的许可各自适用——这是与上游生态的合规边界。
- **与开发流程的关系**：当用户需要在 RAG SDK 镜像基础上加装自有依赖（`apt install gcc ...` 等），文档给出了以 `26.0.0-910b-ubuntu22.04-py3.11` 标签镜像为基线的 `FROM` 用法，作为二次开发入口。

---

## 【使用方法】

**1. 构建镜像**（原文命令，逐字保留）：
```bash
git clone https://gitcode.com/Ascend/RAGSDK.git && cd RAGSDK/docker

docker build --network host -t {your_repo}/ragsdk:<ragsdk-version>-<chip-series>-<os>-<python-version> -f Dockerfile.<chip-series>.<os> .
```
其中 `{your_repo}`、`<ragsdk-version>`、`<chip-series>`、`<os>`、`<python-version>` 需替换为实际值；Dockerfile 文件名严格遵循 `Dockerfile.<chip-series>.<os>` 形式。原文 NOTE 提示：CANN 基础镜像版本由所选 Dockerfile 的 `FROM` 指令决定，须选取与目标芯片和操作系统匹配的 Dockerfile。

**2. 运行容器**（原文命令，逐字保留）：
```bash
docker run -itd --name=rag_sdk_demo --network=host \
    --device=/dev/davinci_manager \
    --device=/dev/hisi_hdc \
    --device=/dev/devmm_svm \
    --device=/dev/davinci0 \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
    -v /usr/local/sbin:/usr/local/sbin:ro \
    -v /path/to/model:/path/to/model:ro \
    {image-name}:{image-tag} bash
```
- `/path/to/model`：模型存放目录，需加载模型时填入对应路径。
- `{image-name}`:`{image-tag}`：指定待运行的 RAG SDK 镜像与标签。

**3. 进入容器**（原文命令，逐字保留）：
```bash
docker exec -it rag_sdk_demo bash
```

**4. 使用示例代码**：容器内 `/workspace/RAGSDK/example`；仓库地址 `https://gitcode.com/Ascend/RAGSDK/tree/master/example`。

**5. 二次开发**（原文 Dockerfile 片段，逐字保留）：
```dockerfile
FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/ragsdk:26.0.0-910b-ubuntu22.04-py3.11
RUN apt update -y &&
    apt install gcc ...
...
```

**6. 故障/帮助入口**（原文 Quick Reference）：
- Issue 反馈：`https://gitcode.com/Ascend/RAGSDK/issues`
- 仓库：`https://gitcode.com/Ascend/RAGSDK`
- API 参考：`https://gitcode.com/Ascend/RAGSDK/blob/master/docs/zh/api/README.md`
- 官方文档：`https://www.hiascend.com/document/detail/zh/mindsdk/730/rag/ragug/mxragug_0001.html`
- 镜像仓库：`https://www.hiascend.com/developer/ascendhub/detail/ragsdk`
