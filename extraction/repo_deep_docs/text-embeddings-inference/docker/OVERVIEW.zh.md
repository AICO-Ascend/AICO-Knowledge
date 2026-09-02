# text-embeddings-inference(TEI)

> 仓 `text-embeddings-inference` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/text-embeddings-inference/docker/OVERVIEW.zh.md

# text-embeddings-inference (昇腾NPU版) docker/OVERVIEW.zh.md 深度解读

---

## 【定位】

这篇文档是 Ascend fork 版 text-embeddings-inference（TEI）Docker 镜像的使用说明，解决"如何把开源 TEI 的 embedding / reranker / Sequence Classification 服务化接口运行在华为 NPU 卡上"的问题——给出镜像 Tag 规范、版本配套、容器启动命令、参数说明、支持的模型清单及接口测试样例。

---

## 【技术要点】

1. **镜像基础**：基于开源 `text-embeddings-inference` 适配华为 NPU，提供 embedding、reranker 等服务化接口；接口兼容开源 TEI；默认以普通用户 `HwHiAiUser` 运行。

2. **镜像 Tag 规范**（原文格式）：
   ```
   <TEI版本>-<芯片系列>-<操作系统>-<python版本>
   ```
   例：`26.0.0-a3-ubuntu22.04-py3.11`（由四个字段拼接而成）。

3. **版本配套矩阵**（原文）：`TEI 26.0.0` 配套 `CANN 9.0.0` + `torch-npu 2.9.0`。

4. **NPU 设备透传与驱动挂载**（26.0.0+ 启动命令）：容器必须透传 `--device /dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`，并挂载宿主机的 dcmi、npu-smi、Ascend driver lib64、version.info、ascend_install.info。

5. **NPU 内存分配调优环境变量**：
   ```
   -e PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
   ```
   限制 NPU 内存块可切分上限为 256 MB。

6. **多模型族支持**：覆盖 BERT（BGE/zh 系列、acge、jina-embeddings-v2-base-zh）、XLM-RoBERTa（bge-m3、bge-reranker）、Qwen2（gte-Qwen2、Qwen2.5-apeach）、Qwen3（Embedding-0.6B/4B/8B、Reranker-0.6B/4B/8B）、RoBERTa（unixcoder-base）；其中 Qwen 系模型启动需 `-e TRUST_REMOTE_CODE=1`、`-e IS_CAUSAL=false`，Qwen3-Reranker 需额外配置 `-e IS_RERANK=1` 与 `DEFAULT_PROMPT`。

7. **版本分支的启动差异**：26.0.0 之前需要额外 `-e ENABLE_BOOST=True` 且命令结尾格式不同（`<model_dir_path> <ip> <port>`），26.0.0 及之后改为 `--model-id … --hostname … --port …` 标准 TEI CLI 风格。

---

## 【关键机制与数据】

### 工作原理与数据流（基于原文梳理）

- **进程模型**：以 Docker 容器形式拉起一个常驻服务进程，绑定 `--hostname <listen_ip> --port <listen_port>` 监听指定端口，对外提供 HTTP 接口。
- **输入侧**：客户端通过 HTTP POST 提交 JSON（`input`/`inputs`/`query`+`documents`/`query`+`texts` 等字段），请求被送入容器内 TEI 推理服务。
- **模型加载**：通过 `-v $MODEL_DIR:$MODEL_DIR` + `-e MODEL_DIR=$MODEL_DIR`，把宿主机预下载的模型权重挂载进容器；容器进程以 `--model-id $MODEL_DIR/<model_name>` 指定具体模型。
- **NPU 算力调用**：通过 `--device /dev/davinci*` 把昇腾设备节点透传给容器，并依赖宿主机安装的与容器内 CANN 版本兼容的 NPU 驱动来调度算力；`PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256` 控制 NPU 内存分配粒度。
- **用户与权限**：容器默认运行用户 `HwHiAiUser`，需保证该用户对宿主机 `$MODEL_DIR` 有读写权限；如需以其他用户运行，使用 `-u <user>` 覆盖。
- **输出侧**：服务返回 JSON 形式的向量（embedding）或打分（rerank）/分类结果，对应 `/v1/embeddings`、`/v1/rerank`、`/rerank`、`/embed` 等路径。

### 性能/版本数据（仅原文出现者）

- 原文：TEI `26.0.0` ↔ CANN `9.0.0` ↔ `torch-npu 2.9.0`（版本配套表的唯一一行）。
- 原文：Tag 中芯片系列示例包含 `910`、`a3`、`Atlas 300I Pro`。
- 原文：操作系统示例为 `ubuntu22.04`、`openeuler24.03`。
- 原文：Python 版本示例为 `py3.11`。
- 原文：`PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256`（内存切分上限）。
- 原文未涉及吞吐量、时延、QPS、显存占用等性能数字。

---

## 【表格解读】

### 表 1：镜像 Tag 字段说明（原文逐字还原）

| 字段 | 示例值 | 说明 |
|---|---|---|
| `TEI版本` | `26.0.0` | TEI 版本号 |
| `芯片系列` | `910`, `a3`, `Atlas 300I Pro` | 目标芯片系列 |
| `操作系统` | `ubuntu22.04`、`openeuler24.03` | 基础操作系统 |
| `python版本` | `py3.11` | Python 版本 |

**逐行解读**：
- `TEI版本`：标注当前 TEI 框架版本，文档锚定在 `26.0.0`。
- `芯片系列`：覆盖昇腾训练卡（`910`）、A3 推理/训练一族、以及 `Atlas 300I Pro` 推理卡；同一镜像 Tag 通过这一字段区分硬件目标。
- `操作系统`：基础 OS 镜像源，含 Ubuntu 22.04 与 openEuler 24.03 两个发行版。
- `python版本`：标明 Python 解释器主次版本，便于选择兼容的 torch-npu 与模型权重环境。

### 表 2：镜像配套表（原文逐字还原）

| TEI | CANN | torch-npu |
|---|---|---|
| 26.0.0 | 9.0.0 | 2.9.0 |

**逐行解读**：仅有一行配套关系——TEI 26.0.0 必须与 CANN 9.0.0、torch-npu 2.9.0 组合使用，对应宿主机的 NPU 驱动需满足 CANN 9.0.0 的兼容性矩阵。

### 表 3：文本嵌入模型（原文逐字还原）

| 模型名称 | 模型类型 | 模型启动必配参数 |
|---|---|---|
| BAAI/bge-large-zh-v1.5 | BERT | - |
| BAAI/bge-m3 | XLM-RoBERTa | - |
| aspire/acge_text_embedding | BERT | - |
| jinaai/jina-embeddings-v2-base-zh | BERT | -e TRUST_REMOTE_CODE=1 |
| Alibaba-NLP/gte-Qwen2-1.5B-instruct | Qwen2 | -e TRUST_REMOTE_CODE=1 <br/>-e IS_CAUSAL=false |
| Alibaba-NLP/gte-Qwen2-7B-instruct | Qwen2 | -e TRUST_REMOTE_CODE=1 <br/>-e IS_CAUSAL=false |
| Qwen/Qwen3-Embedding-0.6B | Qwen3 | - |
| Qwen/Qwen3-Embedding-4B | Qwen3 | - |
| Qwen/Qwen3-Embedding-8B | Qwen3 | - |
| microsoft/unixcoder-base | RoBERTa | - |

**逐行解读**：
- BGE 中文/通用系列与 acge、unixcoder 等 BERT/RoBERTa 类模型使用默认参数即可启动。
- jina-embeddings-v2-base-zh 需要 `TRUST_REMOTE_CODE=1`，因为模型自定义代码不在 transformers 内置支持中。
- 两个 gte-Qwen2 instruct 模型必须显式设置 `TRUST_REMOTE_CODE=1` 并把 `IS_CAUSAL` 置为 `false`（embedding 任务需非因果掩码）。
- Qwen3 Embedding 系列三档（0.6B/4B/8B）文档中标为无必配参数，意味着可直接按标准 TEI 启动方式拉起。

### 表 4：序列分类和排序模型（原文逐字还原）

| 模型名称 | 模型类型 | 模型启动必配参数 |
|---|---|---|
| BAAI/bge-reranker-large | XLM-RoBERTa | - |
| BAAI/bge-reranker-v2-m3 | XLM-RoBERTa | - |
| Qwen/Qwen3-Reranker-0.6B | Qwen3 | -e IS_RERANK=1 <br/> -e DEFAULT_PROMPT="\<Instruct\>: Given a web search query, retrieve relevant passages that answer the query\\n\<Query\>: \<s1\>\\n\<Document\>: \<s2\>" |
| Qwen/Qwen3-Reranker-4B | Qwen3 | -e IS_RERANK=1 <br/> -e DEFAULT_PROMPT="\<Instruct\>: Given a web search query, retrieve relevant passages that answer the query\\n\<Query\>: \<s1\>\\n\<Document\>: \<s2\>" |
| Qwen/Qwen3-Reranker-8B | Qwen3 | -e IS_RERANK=1 <br/> -e DEFAULT_PROMPT="\<Instruct\>: Given a web search query, retrieve relevant passages that answer the query\\n\<Query\>: \<s1\>\\n\<Document\>: \<s2\>" |
| jason9693/Qwen2.5-1.5B-apeach | Qwen2 | - |

**逐行解读**：
- 两条 BGE reranker（large、v2-m3）为 XLM-RoBERTa 系，默认参数即可。
- 三档 Qwen3-Reranker（0.6B/4B/8B）统一配置：`IS_RERANK=1` 告诉 TEI 走 reranker 路径；`DEFAULT_PROMPT` 是 instruct-style 模板，固定 web-search 场景的指令，并用 `<s1>`/`<s2>` 占位 query 与 document 文本。
- Qwen2.5-1.5B-apeach 作为序列分类模型无必配参数（沿用默认 Sequence Classification 流程）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档以内嵌链接和外部参考指向以下对象（按文档出现顺序）：

- **Ascend 原仓**：镜像源代码位于 `Ascend/text-embeddings-inference`（issue 反馈、代码仓库都指向这里）。
- **官方 TEI API 文档**：`https://huggingface.github.io/text-embeddings-inference/`（接口语义基线，本镜像与之兼容）。
- **华为昇腾开发者中心**：`镜像仓库` 用于拉取 `swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:<tag>`；`社区` 入口提供交流与文档索引；`CANN 兼容性矩阵` 给出驱动与 CANN 版本的对应关系。
- **CLI arguments 文档**：`docs/source/en/cli_arguments.md` 给出除 `--model-id/--hostname/--port` 之外的其他 TEI 配置参数。
- **环境变量参考**：`PYTORCH_NPU_ALLOC_CONF` 含义与可调范围链接到华为官方 Pytorch 环境变量手册。
- **下游调用**：API 测试样例给出 `/v1/rerank`、`/rerank`、`/v1/embeddings`、`/embed` 四类路径，对应 HuggingFace TEI 的 rerank / embed 兼容端点；Sequence Classification 章节（原文末尾被截断）应当继续给出对应的 `/predict` 或分类端点的 curl 示例。
- **模型权重源**：所有模型下载链接均指向 ModelScope（`modelscope.cn`），说明该 fork 适配链路以 ModelScope 为权重分发渠道。

---

## 【使用方法】

### 1. 前置准备（原文）

- 在宿主机安装与容器内 CANN 版本（即 9.0.0）兼容的 NPU 驱动；查阅《CANN 兼容性矩阵》确认版本对应。
- 提前在宿主机的 `$MODEL_DIR` 目录中下载好所需模型权重文件；确认该目录对容器默认用户 `HwHiAiUser` 可读写（否则需用 `-u <user>` 指定其他用户）。

### 2. 启动容器（原文：26.0.0 及以后版本）

```bash
export MODEL_DIR=/home/HwHiAiUser/model
docker run \
    -u <user> \
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
    -e PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
    -itd swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:<tag> --model-id $MODEL_DIR/<model_name> --hostname <listen_ip> --port <listen_port>
```

### 3. 启动容器（原文：26.0.0 之前版本）

额外添加 `-e ENABLE_BOOST=True`，TEI CLI 入口为位置参数形式（注意结尾不再带 `--model-id/--hostname/--port` 前缀）：

```bash
-itd swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:<tag> /home/HwHiAiUser/model/<model_name> <listen_ip> <listen_port>
```

### 4. 关键占位符替换（原文"参数说明"）

- `<user>`：容器内运行用户；如希望保留默认 `HwHiAiUser` 可省略 `-u`。
- `<tag>`：镜像 Tag，按 `<TEI版本>-<芯片系列>-<操作系统>-<python版本>` 拼装（如 `26.0.0-a3-ubuntu22.04-py3.11`）。
- `<model_name>`：必须与宿主机 `$MODEL_DIR` 下实际权重文件名一致。
- `<listen_ip>`、`<listen_port>`：服务监听地址与端口（默认常用 `0.0.0.0`/`8080`）。
- `PYTORCH_NPU_ALLOC_CONF`：调小 `max_split_size_mb` 可降低 NPU 内存碎片，但过小会限制大张量；原文默认 `256`。

### 5. 启动后接口自检（原文 curl 样例）

- **Rerank（OpenAI 兼容路径）**：`POST /v1/rerank`，body 字段 `query` + `documents` 数组。
- **Rerank（TEI 原生路径）**：`POST /rerank`，body 字段 `query` + `texts` 数组。
- **稠密向量（OpenAI 兼容）**：`POST /v1/embeddings`，body 字段 `input`（字符串数组）。
- **稠密向量（TEI 原生）**：`POST /embed`，body 字段 `inputs`（字符串数组）。
- **Sequence Classification**：原文末尾命令 `curl 127.0.0.1:808` 被截断，原文未提供完整示例（原文未涉及完整命令）。

### 6. 其他配置入口

- 全部 TEI CLI 参数请参考 `Ascend/text-embeddings-inference/docs/source/en/cli_arguments.md`，文档中只展示了与 NPU 启动直接相关的 `MODEL_DIR`、`PYTORCH_NPU_ALLOC_CONF`、`ENABLE_BOOST`、各模型族专用环境变量（`TRUST_REMOTE_CODE`、`IS_CAUSAL`、`IS_RERANK`、`DEFAULT_PROMPT`）等。其余可调旋钮（线程池、批大小、最大序列长度等）原文未涉及具体数值，需要参照 TEI 官方 CLI arguments 文档。
