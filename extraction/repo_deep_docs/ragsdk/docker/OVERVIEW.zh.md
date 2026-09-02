# RAG SDK

> 仓 `ragsdk` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ragsdk/docker/OVERVIEW.zh.md

```markdown
# RAG SDK Docker 镜像 OVERVIEW 文档深度解读

## 【定位】
这篇文档是 RAG SDK 在昇腾（Ascend）AI 软硬件生态中**面向镜像交付与容器化部署的概览说明**，解决「如何在昇腾芯片上以 Docker 镜像方式拉取、构建、运行、并基于此进行二次开发」的问题，描述的是 RAG SDK 作为知识增强开发套件在镜像维度的交付能力。

---

## 【技术要点】

1. **镜像 Tag 命名规范**：`<ragsdk版本>-<芯片系列>-<操作系统>-<python版本>`，例如 `26.0.0-910b-ubuntu22.04-py3.11`，将版本、芯片、OS、Python 四个维度固化到 tag 中，方便跨平台分发与回溯。

2. **镜像与底层 CANN 配套**：当前给出的镜像版本对应关系为 `26.0.0` 镜像版本 ↔ `26.0.0` RAG SDK 版本 ↔ `9.0.0` CANN 版本，CANN 是昇腾计算架构基础软件包，版本必须配套使用。

3. **本地构建命令**：
   ```bash
   git clone https://gitcode.com/Ascend/RAGSDK.git && cd RAGSDK/docker
   docker build --network host -t {your_repo}/ragsdk:<ragsdk版本>-<芯片系列>-<操作系统>-<python版本> \
       -f Dockerfile.<芯片系列>.<操作系统> .
   ```
   使用 `--network host` 提升构建网络可达性，并通过选择不同的 `Dockerfile.<芯片系列>.<操作系统>` 文件实现一码多平台构建。

4. **容器运行参数**：除常规 `-itd --name=rag_sdk_demo --network=host` 之外，**必须挂载 4 个昇腾设备节点**：`/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`、`/dev/davinci0`（`davinci0` 是示例，实际可指定其他 NPU 编号）；同时只读挂载驱动目录 `/usr/local/Ascend/driver`、`/usr/local/sbin` 与模型目录 `/path/to/model`。

5. **支持的硬件范围**：覆盖 Atlas 910（Atlas 800T A2、Atlas 900 A2 PoD）、Atlas A3（Atlas 800T A3）、Atlas 300I Pro（Atlas 300I Pro、Atlas 300V Pro），三类芯片均支持 ARM64 与 X86_64 两种宿主架构。

6. **二次开发模式**：基于官方镜像 `FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/ragsdk:26.0.0-910b-ubuntu22.04-py3.11` 叠加用户自有软件包，实现业务定制。

---

## 【关键机制与数据】

### 工作原理

- **CANN 基础镜像驱动版本基线**：Dockerfile 通过 `FROM` 指令引入 CANN 基础镜像（原文：*"CANN 基础镜像版本由所选 Dockerfile 的 `FROM` 指令指定，请选择与目标芯片和操作系统匹配的 Dockerfile"*）。这意味着不同 Dockerfile 隐含了不同的 CANN / 驱动组合，用户不能跨芯片系列或 OS 混用 Dockerfile。

- **设备透传机制**：`--device=/dev/davinci_manager`、`/dev/hisi_hdc`、`/dev/devmm_svm`、`/dev/davinci0` 是昇腾 NPU 在容器场景的标准透传设备清单；其中 `davinci_manager` 是设备管理节点，`hisi_hdc` 是海思主机-设备通信通道，`devmm_svm` 是 SVM（Shared Virtual Memory）设备内存管理节点，`davinci0` 是计算设备节点。

- **驱动只读挂载**：将宿主机 `/usr/local/Ascend/driver`、`/usr/local/sbin` 以 `:ro` 方式挂入容器，使容器内的 RAG SDK 通过宿主机的昇腾驱动访问物理 NPU，驱动版本由宿主机决定，镜像本身不带驱动。

- **数据流（模型加载）**：用户把模型文件放入宿主机 `/path/to/model` 目录并只读挂载进容器，容器内应用通过该路径读取模型文件，实现"模型与运行环境解耦"。

### 性能数据
原文未涉及任何性能数据（如吞吐、时延、显存占用等）。

---

## 【表格解读】

### 表 1：Tag 字段规范（原文逐字还原）

| 字段         | 示例值                       | 说明                                       |
| ------------ | ---------------------------- | ------------------------------------------ |
| ragsdk版本   | 26.0.0                      | ragsdk 版本号                              |
| 芯片系列     | 910、A3、atlas 300I Pro     | 目标昇腾芯片系列                           |
| 操作系统     | ubuntu22.04、openeuler24.03 | 目标操作系统                               |
| python 版本  | py3.11                      | 目标 python 版本                           |

**逐行解读：**
- **ragsdk 版本**：采用语义化版本（示例 26.0.0 为三段式主版本号），是 Tag 中定位 SDK 功能版本的关键字段。
- **芯片系列**：原文示例同时出现数字（910）、字母+数字（A3）与带空格的复合名称（atlas 300I Pro），暗示用户在构建命令的 tag 与 Dockerfile 选择上需精确匹配；910 对应 Atlas 910 系列产品，A3 对应 Atlas A3 系列，atlas 300I Pro 对应 Atlas 300I Pro 系列。
- **操作系统**：支持 Ubuntu 22.04 与 openEuler 24.03 两种 LTS/最新版本，覆盖主流昇腾落地 OS 生态。
- **python 版本**：示例仅列出 py3.11，意味着当前 Tag 体系以 3.11 作为唯一支持的 Python 运行时。

### 表 2：RAG SDK 镜像版本配套表（原文逐字还原）

| 镜像版本 | RAG SDK 版本 | CANN 版本 |
| -------- | ------------ | --------- |
| 26.0.0  | 26.0.0       | 9.0.0     |

**逐行解读：**
- 当前仅给出 **一行配套关系**：镜像 `26.0.0` ↔ RAG SDK `26.0.0` ↔ CANN `9.0.0`，三者版本号同步。这表明该文档成文时仅发布了一个版本组合，未来新版本会按行扩展。
- 该表提示用户：在选择镜像前，必须确保 CANN 9.0.0 与宿主驱动匹配，否则 NPU 设备无法正常初始化。

### 表 3：支持的硬件（原文逐字还原）

| 芯片系列         | 产品示例                          | 架构            |
| ---------------- | --------------------------------- | --------------- |
| Atlas 910        | Atlas 800T A2、Atlas 900 A2 PoD   | ARM64/ X86_64   |
| Atlas A3         | Atlas 800T A3                     | ARM64/ X86_64   |
| Atlas 300I Pro  | Atlas 300I Pro、Atlas 300V Pro    | ARM64/ X86_64   |

**逐行解读：**
- **Atlas 910**：定位训练/推理主力，包含 Atlas 800T A2（高密度推理服务器）与 Atlas 900 A2 PoD（超节点集群），ARM64 与 X86_64 两种宿主架构均可部署，意味着既可在鲲鹏 ARM 服务器也可在 x86 通用服务器上运行。
- **Atlas A3**：示例产品仅 Atlas 800T A3，原文未给出更多产品对照；架构同样兼容 ARM64 / X86_64。
- **Atlas 300I Pro**：覆盖推理卡形态，包含 Atlas 300I Pro 与 Atlas 300V Pro 两款产品，常用于边缘推理或单卡推理服务器场景；架构同样双兼容。

---

## 【公式解读】
原文无公式。

---

## 【关联】

文档虽未提供正文内的内部链接，但通过"快速参考"区块建立的外部关联网络可还原出 RAG SDK 的上下游关系：

- **问题反馈通道 → 维护方**：issue 反馈链接 `https://gitcode.com/Ascend/RAGSDK/issues` 指向同一仓库的 Issue 区，与 RAG SDK 代码仓 `https://gitcode.com/Ascend/RAGSDK` 同源，形成"代码 ↔ 问题"闭环。
- **代码仓 → API 参考**：API 参考 `https://gitcode.com/Ascend/RAGSDK/blob/master/docs/zh/api/README.md` 位于 RAGSDK 仓 `docs/zh/api/` 目录，是本文档对应的程序接口文档，与本文（镜像部署文档）构成"部署 ↔ 接口"上下游关系。
- **代码仓 → 用户文档**：用户文档 `https://www.hiascend.com/document/detail/zh/mindsdk/730/rag/ragug/mxragug_0001.html` 位于昇腾 Mind SDK 文档体系下，作为 RAG SDK 用户手册（路径含 `ragug`，即 RAG User Guide）的入口，补充本文档未涉及的功能说明。
- **镜像仓库**：镜像仓库 `https://www.hiascend.com/developer/ascendhub/detail/ragsdk` 提供了已构建好的 RAG SDK 镜像（即二次开发示例 `FROM` 指令中 `swr.cn-south-1.myhuaweicloud.com/ascendhub/ragsdk:...` 所对应的官方分发源）。
- **模块关系**：本文（`docker/OVERVIEW.zh.md`）归属于 RAGSDK 仓库 `docker/` 目录，与同目录的 `Dockerfile.<芯片系列>.<操作系统>` 文件共同构成镜像构建资产；与 `LICENSE.md`（许可证信息）属同级元数据。

---

## 【使用方法】

原文给出的可用命令与配置项如下：

### 1. 本地构建镜像
```bash
git clone https://gitcode.com/Ascend/RAGSDK.git && cd RAGSDK/docker
docker build --network host -t {your_repo}/ragsdk:<ragsdk版本>-<芯片系列>-<操作系统>-<python版本> \
    -f Dockerfile.<芯片系列>.<操作系统> .
```
- `{your_repo}`：实际镜像仓库地址。
- `Dockerfile.<芯片系列>.<操作系统>`：根据目标芯片（910 / A3 / atlas 300I Pro 等）与操作系统（ubuntu22.04 / openeuler24.03 等）选择对应文件。

### 2. 运行 RAG SDK 容器
```bash
docker run -itd --name=rag_sdk_demo --network=host \
    --device=/dev/davinci_manager \
    --device=/dev/hisi_hdc \
    --device=/dev/devmm_svm \
    --device=/dev/davinci0 \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
    -v /usr/local/sbin:/usr/local/sbin:ro \
    -v /path/to/model:/path/to/model:ro \
    {镜像名称}:{镜像tag} bash
```
- `/path/to/model`：模型存放目录，需为已放入模型文件的真实路径。
- `{镜像名称}`:`{镜像tag}`：例如 `swr.cn-south-1.myhuaweicloud.com/ascendhub/ragsdk:26.0.0-910b-ubuntu22.04-py3.11`。

### 3. 进入容器
```bash
docker exec -it rag_sdk_demo bash
```
容器启动后，可在 `/workspace/RAGSDK/example` 路径下获取预置示例代码；亦可通过 `https://gitcode.com/Ascend/RAGSDK/tree/master/example` 获取最新 Demo。

### 4. 二次开发（叠加用户软件）
```dockerfile
FROM swr.cn-south-1.myhuaweicloud.com/ascendhub/ragsdk:26.0.0-910b-ubuntu22.04-py3.11
RUN apt update -y && apt install gcc ...
...
```
基于官方 RAG SDK 镜像做 FROM，可继续叠加用户级 Python 包或系统包，保留昇腾驱动/CANN/Python 运行时一致性。

### 5. 许可证查看
详见 `https://gitcode.com/Ascend/RAGSDK/blob/master/LICENSE.md`，并注意容器内预装的 Python 包、系统库等第三方组件可能受其各自许可证约束（原文：*"与所有容器镜像一样，预装软件包（Python、系统库等）可能受其自身许可证约束"*）。
```
