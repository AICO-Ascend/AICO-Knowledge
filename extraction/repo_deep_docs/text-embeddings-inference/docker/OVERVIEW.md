# text-embeddings-inference(TEI)

> 仓 `text-embeddings-inference` · 路径 `docker/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/text-embeddings-inference/docker/OVERVIEW.md

# docker/OVERVIEW.md 一体化深度解读

## 【定位】
本篇文档解决 **在昇腾（Ascend）NPU 硬件上运行 text-embeddings-inference（TEI）推理服务的部署入口问题**：说明镜像标签命名、与 CANN/torch-npu 的版本配套关系、容器启动命令与设备挂载要求，并列出已验证兼容的 Embedding / Reranker 模型及其必需的环境变量。

---

## 【技术要点】

1. **适配能力**：基于开源 TEI 镜像改造，向 Huawei NPU 卡（昇腾）提供 embedding、reranker、Sequence Classification 等服务接口；接口兼容开源 TEI；镜像默认以普通用户 `HwHiAiUser` 运行。原文："based on text embedding inference and is adapted for Huawei NPU cards to provide service interfaces such as embedding and reranker… By default, this image runs as the regular user `HwHiAiUser`."

2. **镜像标签命名规范**：形如 `<TEI_version>-<chip_series>-<os>-<python_version>`，例如 `26.0.0-910-ubuntu22.04-py3.11`、`a3`、`Atlas 300I Pro`；OS 支持 `ubuntu22.04` / `openeuler24.03`，Python 取 `py3.11`。

3. **软件版本配套表（唯一一组）**：`TEI 26.0.0 ↔ CANN 9.0.0 ↔ torch-npu 2.9.0`；主机端必须安装与容器内 CANN 版本兼容的 Atlas NPU 驱动。

4. **容器设备挂载（26.0.0+ 启动命令）**：通过 `--device` 透传 `/dev/davinci0`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`；并 `-v` 挂载 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、`/usr/local/Ascend/driver/lib64/`、`/usr/local/Ascend/driver/version.info`、`/etc/ascend_install.info` 到容器内。

5. **NPU 内存配置**：通过环境变量 `PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256` 控制 NPU 内存块允许拆分上限。

6. **模型支持矩阵**：覆盖 BERT、XLM-RoBERTa、Qwen2、Qwen3、RoBERTa 等架构；其中 Qwen3-Embedding（0.6B/4B/8B）、Qwen3-Reranker（0.6B/4B/8B）、jina-embeddings-v2-base-zh、Alibaba-NLP/gte-Qwen2-* 等模型需要额外通过 `-e` 注入特定环境变量（如 `TRUST_REMOTE_CODE=1`、`IS_CAUSAL=false`、`IS_RERANK=1`、`DEFAULT_PROMPT=…`）。

---

## 【关键机制与数据】

工作原理与数据流层面的"原文"内容较少，可逐项引用如下：

- **镜像构建机制（原文）**："This image is based on text embedding inference and is adapted for Huawei NPU cards to provide service interfaces such as embedding and reranker." —— 即在开源 TEI 之上叠加昇腾 NPU 适配层，使其能被 Atlas 系列芯片执行。
- **接口兼容性（原文）**：接口与开源 text embedding inference 兼容；支持的模型类型包括 embedding、reranker、Sequence Classification。
- **运行身份（原文）**："By default, this image runs as the regular user `HwHiAiUser`."
- **运行参数（原文）**：TEI 容器通过 `--model-id $MODEL_DIR/<model_name> --hostname <listen_ip> --port <listen_port>` 指定模型路径与监听地址端口；26.0.0 之前的旧命令通过 `/home/HwHiAiUser/model/<model_name> <listen_ip> <listen_port>` 的位置参数指定模型与监听信息。
- **旧版本差异（原文）**：26.0.0 之前启动命令额外使用 `-e ENABLE_BOOST=True`；新版本（26.0.0+）使用 `-u <user>`、并把模型挂载到 `$MODEL_DIR:$MODEL_DIR` 后通过 `MODEL_DIR` 环境变量传入，旧版本则将模型目录挂载到容器内的 `/home/HwHiAiUser/model`。
- **性能数据**：原文未提供吞吐、时延等性能数字，**原文未涉及**。

---

## 【表格解读】

### 表 1：镜像标签字段说明（原文逐字还原）

| Field            | Example Values                  | Description                       |
|------------------|---------------------------------|-----------------------------------|
| `TEI_version`    | `26.0.0`                        | text-embeddings-inference version |
| `chip_series`    | `910`, `a3`, `Atlas 300I Pro`   | Target chip family                |
| `os`             | `ubuntu22.04`, `openeuler24.03` | Base operating system             |
| `python_version` | `py3.11`                        | Python version                    |

逐行解读：
- `TEI_version` 指上游 TEI 版本号，示例为 `26.0.0`，即当前文档主推的启动命令版本。
- `chip_series` 标识目标芯片系列，示例覆盖训练/推理卡 `910`、A3 系列、以及推理设备 `Atlas 300I Pro`。
- `os` 为底层 OS，可选 `ubuntu22.04` 或 `openeuler24.03`。
- `python_version` 固定为 `py3.11`。

### 表 3：Docker 镜像软件版本匹配表（原文逐字还原）

| TEI    | CANN  | torch-npu |
|--------|-------|-----------|
| 26.0.0 | 9.0.0 | 2.9.0     |

逐行解读：仅给出一组配套关系——TEI 26.0.0 必须与 CANN 9.0.0、torch-npu 2.9.0 同时使用，主机驱动也应匹配 CANN 9.0.0。

### 表 4：Text Embeddings 支持模型（原文逐字还原）

| Model Name | Model Type | Other required parameters |
|---|---|---|
| [BAAI/bge-large-zh-v1.5](https://www.modelscope.cn/models/BAAI/bge-large-zh-v1.5) | BERT | - |
| [BAAI/bge-m3](https://www.modelscope.cn/models/BAAI/bge-m3) | XLM-RoBERTa | - |
| [aspire/acge_text_embedding](https://www.modelscope.cn/models/yangjhchs/acge_text_embedding) | BERT | - |
| [jinaai/jina-embeddings-v2-base-zh](https://www.modelscope.cn/models/jinaai/jina-embeddings-v2-base-zh) | BERT | `-e TRUST_REMOTE_CODE=1` |
| [Alibaba-NLP/gte-Qwen2-1.5B-instruct](https://www.modelscope.cn/models/iic/gte-Qwen2-1.5B-instruct) | Qwen2 | `-e TRUST_REMOTE_CODE=1` <br/> `-e IS_CAUSAL=false` |
| [Alibaba-NLP/gte-Qwen2-7B-instruct](https://www.modelscope.cn/models/iic/gte-Qwen2-7B-instruct) | Qwen2 | `-e TRUST_REMOTE_CODE=1` <br/> `-e IS_CAUSAL=false` |
| [Qwen/Qwen3-Embedding-0.6B](https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-0.6B) | Qwen3 | - |
| [Qwen/Qwen3-Embedding-4B](https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-4B) | Qwen3 | - |
| [Qwen/Qwen3-Embedding-8B](https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-8B) | Qwen3 | - |
| [microsoft/unixcoder-base](https://www.modelscope.cn/models/microsoft/unixcoder-base) | RoBERTa | - |

逐行解读：
- `BAAI/bge-large-zh-v1.5` / `aspire/acge_text_embedding` 为 BERT 类中文 embedding，**无需额外参数**。
- `BAAI/bge-m3` 为 XLM-RoBERTa 多语言 embedding，**无需额外参数**。
- `jinaai/jina-embeddings-v2-base-zh` 需 `-e TRUST_REMOTE_CODE=1`，因模型仓库含自定义代码。
- `Alibaba-NLP/gte-Qwen2-1.5B-instruct` / `gte-Qwen2-7B-instruct` 为 Qwen2 因果架构 embedding，必须同时设置 `TRUST_REMOTE_CODE=1` 与 `IS_CAUSAL=false`（关掉因果语言模型语义）。
- `Qwen3-Embedding-0.6B/4B/8B` 为 Qwen3 embedding，**无需额外参数**。
- `microsoft/unixcoder-base` 为代码领域 RoBERTa，**无需额外参数**。

### 表 5：Sequence Classification & Re-Ranking 支持模型（原文逐字还原，已截断）

| Model Name | Model Type | Other required parameters |
|---|---|---|
| [BAAI/bge-reranker-large](https://www.modelscope.cn/models/BAAI/bge-reranker-large) | XLM-RoBERTa | - |
| [BAAI/bge-reranker-v2-m3](https://www.modelscope.cn/models/BAAI/bge-reranker-v2-m3) | XLM-RoBERTa | - |
| [Qwen/Qwen3-Reranker-0.6B](https://www.modelscope.cn/models/Qwen/Qwen3-Reranker-0.6B) | Qwen3 | `-e IS_RERANK=1` <br/> `-e DEFAULT_PROMPT="\<Instruct\>: Given a web search query, retrieve relevant passages that answer the query\\n\<Query\>: \<s1\>\\n\<Document\>: \<s2\>"` |
| [Qwen/Qwen3-Reranker-4B](https://www.modelscope.cn/models/Qwen/Qwen3-Reranker-4B) | Qwen3 | `-e IS_RERANK=1` <br/> `-e DEFAULT_PROMPT="\<Instruct\>: Given a web search query, retrieve relevant passages that answer the query\\n\<Query\>: \<s1\>\\n\<Document\>: \<s2\>"` |
| [Qwen/Qwen3-Reranker-8B](https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-8B) | Qwen3 | （原文表格行被截断，仅展示模型名与类型，未给出参数） |

逐行解读：
- `BAAI/bge-reranker-large` / `bge-reranker-v2-m3` 为 XLM-RoBERTa reranker，**无需额外参数**。
- `Qwen3-Reranker-0.6B/4B` 需通过 `-e IS_RERANK=1` 切换为 reranker 模式，并通过 `-e DEFAULT_PROMPT=…` 注入指令模板，模板包含三段占位符：`<Instruct>`（任务说明：基于网页检索查询召回相关段落）、`<Query>` 内含 `<s1>`、`<Document>` 内含 `<s2>`，分别由 TEI 在推理时填入查询与文档。
- `Qwen3-Reranker-8B` 行在原文中被截断，仅可见 Model Name/Type 列。

---

## 【公式解读】

原文无数学公式（LaTeX 形式）。仅出现一处"伪代码/模板字符串"形式的 reranker prompt，**逐字保留原式**如下：

```
<Instruct>: Given a web search query, retrieve relevant passages that answer the query
<Query>: <s1>
<Document>: <s2>
```

符号解释：
- `<Instruct>`：任务指令前缀，描述 reranker 需要完成的动作（"根据网页搜索查询召回相关段落"）。
- `<Query>`：查询行容器，固定前缀 `<Query>:` 后接占位符 `<s1>`，运行时由 TEI 替换为实际查询文本。
- `<Document>`：文档行容器，固定前缀 `<Document>:` 后接占位符 `<s2>`，运行时由 TEI 替换为待评分的文档内容。
- 三个标记之间以换行符 `\n` 分隔（原文用 `\\n` 在 shell 双引号中转义）。
- 该 prompt 通过 `-e DEFAULT_PROMPT=…` 传入，用于在 Qwen3-Reranker 上以指令对齐形式触发重排序打分。

---

## 【关联】

文档内嵌了若干上下游/工具链接，可视作模块关联：

- **镜像源**：`swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:<tag>` 是实际的容器仓库；`https://www.hiascend.com/developer/ascendhub/detail/07a016975cc341f3a5ae131f2b52399d` 为镜像详情页。
- **版本配套**：与「CANN Compatibility Matrix」（`https://www.hiascend.com/document`）关联，用于校验主机驱动与容器 CANN 的对应关系。
- **环境变量参考**：指向 `PYTORCH_NPU_ALLOC_CONF` 官方说明页 `https://www.hiascend.com/document/detail/zh/Pytorch/2600/comref/Envvariables/docs/zh/environment_variable_reference/PYTORCH_NPU_ALLOC_CONF.md`。
- **命令行参数**：链接到同仓 `docs/source/en/cli_arguments.md`，文档本身只列了少量环境变量，其余 TEI CLI 参数以此文档为准。
- **API 文档**：上游开源 TEI 的 API 参考 `https://huggingface.github.io/text-embeddings-inference/`，表明本镜像接口与开源版本兼容。
- **社区/反馈**：提供 issue、code、community 入口，分别对接 `gitcode.com/Ascend/text-embeddings-inference`、`gitcode.com/Ascend/text-embeddings-inference/issues`、`www.hiascend.com`。
- **中文版本**：文首 `中文` 链接指向 `https://gitcode.com/Ascend/text-embeddings-inference/blob/main/docker/OVERVIEW.zh.md`，与本英文版内容互为镜像翻译。
- **上游 TEI 代码**：原文中提到的 `https://gitcode.com/Ascend/text-embeddings-inference` 为本仓 fork 后的代码主仓，与 Hugging Face 上游 `text-embeddings-inference` 同源。

---

## 【使用方法】

### 1. 主机端准备
- 安装与容器 CANN 版本（9.0.0）兼容的 Atlas NPU 驱动；参照 [CANN Compatibility Matrix](https://www.hiascend.com/document)。
- 在主机侧准备模型权重目录，例：`export MODEL_DIR=/home/HwHiAiUser/model`，把模型权重预先下载到该目录；并确保 `HwHiAiUser`（或 `-u <user>` 指定的用户）对该目录有读写权限。

### 2. 26.0.0+ 启动容器（原文命令）
```bash
export MODEL_DIR=/home/HwHiAiUser/model
docker run -itd \
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

### 3. 26.0.0 之前启动容器（原文命令，新增 `-e ENABLE_BOOST=True`、模型用位置参数）
```bash
export MODEL_DIR=/home/HwHiAiUser/model
docker run -itd \
    -u <user> \
    --net host \
    --name tei_container \
    -e ENABLE_BOOST=True \
    --device /dev/davinci0 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v $MODEL_DIR:/home/HwHiAiUser/model \
    -e PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
    -itd swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:<tag> /home/HwHiAiUser/model/<model_name> <listen_ip> <listen_port>
```

### 4. 模型相关环境变量（按需追加 `-e`）
- `-e TRUST_REMOTE_CODE=1`：jina-embeddings-v2-base-zh、Alibaba-NLP/gte-Qwen2-1.5B-instruct、gte-Qwen2-7B-instruct。
- `-e IS_CAUSAL=false`：Alibaba-NLP/gte-Qwen2-1.5B-instruct、gte-Qwen2-7B-instruct（关闭因果语言模型语义，改为双向 embedding）。
- `-e IS_RERANK=1` + `-e DEFAULT_PROMPT="<Instruct>: ...\n<Query>: <s1>\n<Document>: <s2>"`：Qwen3-Reranker-0.6B / 4B（8B 行原文被截断）。

### 5. 其他参数
- `--model-id` / 旧命令的位置参数：指定模型路径。
- `--hostname`、`<listen_ip>`：监听 IP。
- `--port`、`<listen_port>`：监听端口。
- `--net host`：使用主机网络。
- 其余 TEI CLI 参数（如最大 batch、pooling、量化等）请查阅 [cli_arguments.md](https://gitcode.com/Ascend/text-embeddings-inference/blob/main/docs/source/en/cli_arguments.md)——原文未在本文件展开。
