# 快速入门

> 仓 `text-embeddings-inference` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/text-embeddings-inference/docs/zh/quick_start.md

# 一体化深度解读：TEI 快速入门文档（昇腾 NPU 版）

## 【定位】

这篇文档是 Ascend 社区定制的 TEI（Text Embeddings Inference）镜像的**快速部署操作手册**，目标是指导用户在昇腾 NPU 硬件上以 Docker 容器方式拉取预编译镜像、挂载模型权重、暴露 NPU 设备并启动 BAAI/bge-large-zh-v1.5 推理服务，最终通过 HTTP 接口获取文本向量结果。

---

## 【技术要点】

1. **镜像 Tag 命名规范**：`{version}-{chip}-{os}-{python}-{arch}` 四段式，原文示例为 `26.0.0-910b-ubuntu22.04-py3.11`，对应 TEI 26.0.0 版本 + 910b 芯片 + Ubuntu 22.04 + Python 3.11。
2. **环境预检查**：执行 `npu-smi info` 获取 NPU 驱动版本，并通过昇腾社区"固件与驱动"页面确认驱动与固件、CANN 三者配套（CANN 已预装于镜像内）。
3. **NPU 设备透传挂载**：容器启动时必须挂载 4 个设备节点——`/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`（可通过 `ls -al /dev/davinci*` 查看可用设备）。
4. **主机侧 NPU 运行时卷挂载**：需将 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`version.info`、`/etc/ascend_install.info` 等 5 个主机路径绑定到容器，使容器内进程能调用宿主机的 NPU 驱动与 DCMI 管理接口。
5. **模型权重获取**：使用 `GIT_LFS_SKIP_SMUDGE=1 git clone` + `git lfs pull` 的两步法（避免先下载大文件再拉 LFS），从魔搭 ModelScope 拉取 `BAAI/bge-large-zh-v1.5` 到 `/home/data`。
6. **服务端口声明**：容器启动参数显式指定 `--hostname 127.0.0.1 --port 8000`，但验证步骤的 curl 实际访问的是 **8080 端口**（原文存在端口不一致，详见下文"关联"）。

---

## 【关键机制与数据】

- **原文：** 镜像内已集成 CANN，宿主机无需重复安装，只需保证 NPU 驱动和固件版本与所选镜像标签里的 CANN 配套。
- **原文：** 硬件需为昇腾 Atlas 系列（举例为 Atlas 800I A2 推理服务器），CPU 架构区分 x86_64 / aarch64。
- **原文：** 数据流为"git LFS 拉权重 → 主机目录挂载进容器 → 容器内 TEI 进程通过 `--model-id` 加载 → 监听 HTTP 端点 → curl 提交文本 → 返回 embedding"。
- **原文：** 验证请求体为单条输入 `"The capital of China is Beijing."`（虽文档为中文版，但示例输入是英文）。
- **原文：** 性能/吞吐量/QPS 等量化指标**未在原文中给出**。
- **关键差异（原文）：** 容器 `--port 8000` 与测试 `curl 127.0.0.1:8080` **端口号不一致**，是文档本身的命令不一致（推测容器实际监听 8080，或 curl 端误写）。

---

## 【表格解读】

**原文表格逐字还原**（镜像 Tag 字段说明）：

| 字段         | 示例值                            | 说明         |
|------------|--------------------------------|------------|
| `TEI版本`    | `26.0.0`                       | TEI 版本号    |
| `芯片系列`     | `910`, `a3`, `Atlas 300I Pro`  | 目标芯片系列     |
| `操作系统`     | `ubuntu22.04`、`openeuler24.03` | 基础操作系统     |
| `python版本` | `py3.11`                       | Python 版本   |

**逐行解读：**

- **`TEI版本`**：固定为 TEI 上游发布版本号，本文档示例为 `26.0.0`（注：上游原始 TEI 截至 2024 年并未发布到 26.0.0，此处 26.0.0 应为 Ascend 内部定制的镜像构建版本号，原文未说明与上游 TEI 版本号的对应关系）。
- **`芯片系列`**：取值为 `910`（通用代号）、`a3`（新一代代号）、`Atlas 300I Pro`（具体产品名），示例下载命令用的是细粒度 `910b`（即 910B 芯片，原文表格未单列）。
- **`操作系统`**：列出 `ubuntu22.04` 与 `openeuler24.03` 两种基础 OS，文档示例仅展示 Ubuntu 路线。
- **`python版本`**：以 `py3.11` 为例，说明镜像内已绑定 Python 3.11 运行时，用户无需在容器内另行安装。
- **缺项说明：** Tag 格式中声明了 `{arch}` 段，但表格未列出 `arch`（x86_64/aarch64）字段，是原文表格的不完整处。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档中显式引用的外部资料与上下游模块：

1. **镜像源**：[Ascend 镜像仓](https://www.hiascend.com/developer/ascendhub/detail/07a016975cc341f3a5ae131f2b52399d)——决定可拉取的 TEI 镜像版本及配套 CANN 版本，是本指南的前置依赖。
2. **固件/驱动配套表**：[固件与驱动文档](https://www.hiascend.com/hardware/firmware-drivers/community)——当 `npu-smi info` 输出与所选镜像不匹配时，用于驱动升级指引。
3. **CLI 参数文档**：[CLI arguments](https://gitcode.com/Ascend/text-embeddings-inference/blob/main/docs/source/en/cli_arguments.md)——本文档只展示了 `--model-id`、`--hostname`、`--port` 三个参数，其它 `--max-client-batch-size`、`--max-batch-tokens` 等性能调优参数需查阅该上游 CLI 文档。
4. **上游项目**：`text-embeddings-inference`（TEI）本体——本文档为 Ascend fork 的使用侧补充，不涉及 TEI 自身 API 协议扩展。
5. **端口不一致关联**：容器内 TEI 进程的 `--port 8000` 与 curl 验证 `127.0.0.1:8080` **不一致**；TEI 上游默认监听端口为 80/8080 系列，原文 docker run 中的 `8000` 与上游默认行为存在差异，需结合 CLI arguments 文档确认实际监听端口。

> 注：用户提供的"内部链接"为"(无)"，但文档本身存在多个外链（昇腾社区、gitcode、ModelScope），上述关联均基于原文实际出现的链接归纳。

---

## 【使用方法】

**原文给出的命令/配置项如下：**

1. **拉取镜像**：
   ```bash
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:26.0.0-910b-ubuntu22.04-py3.11
   ```

2. **下载模型权重（以 bge-large-zh-v1.5 为例）**：
   ```bash
   cd /home/data
   GIT_LFS_SKIP_SMUDGE=1 git clone https://www.modelscope.cn/BAAI/bge-large-zh-v1.5.git
   cd bge-large-zh-v1.5 && git lfs pull
   ```

3. **启动容器**：
   ```bash
   export MODEL_DIR=/home/data
   docker run -itd \
     -u root \
     --net host \
     --name tei_container \
     --device /dev/davinci0 \
     --device /dev/davinci_manager \
     --device /dev/devmm_svm \
     --device /dev/hisi_hdc \
     -v /usr/local/dcmi:/usr/local/dcmi \
     -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
     -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
     -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
     -v /etc/ascend_install.info:/etc/ascend_install.info \
     -e MODEL_DIR=$MODEL_DIR \
     -v $MODEL_DIR:$MODEL_DIR \
     swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:26.0.0-910b-ubuntu22.04-py3.11 \
     --model-id $MODEL_DIR/bge-large-zh-v1.5 --hostname 127.0.0.1 --port 8000
   ```

4. **验证服务（原文命令）**：
   ```bash
   curl 127.0.0.1:8080/v1/embeddings \
       -X POST \
       -d '{"input":["The capital of China is Beijing."]}' \
       -H 'Content-Type: application/json'
   ```

**关键环境变量与参数（原文出现）：**
- `MODEL_DIR=/home/data`：宿主侧模型权重根目录。
- `--model-id $MODEL_DIR/bge-large-zh-v1.5`：指向具体模型子目录。
- `--hostname 127.0.0.1 --port 8000`：服务监听地址。
- 容器网络模式：`--net host`（与主机共享网络栈）。

**原文未涉及的配置项：** 自动重启策略、健康检查、资源限制（CPU/MEM）、日志挂载、`--max-batch-tokens` / `--max-client-batch-size` 等 TEI 性能调优参数——均需参阅上游 CLI arguments 文档。
