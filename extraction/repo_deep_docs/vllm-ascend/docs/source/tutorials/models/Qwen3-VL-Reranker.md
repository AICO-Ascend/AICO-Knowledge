# Qwen3-VL-Reranker

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-VL-Reranker.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-VL-Reranker.md

# 深度解读：Qwen3-VL-Reranker 部署指南

## 【定位】

本文档解决如何在 vLLM Ascend 环境下部署和运行 Qwen3-VL-Reranker 系列多模态重排序模型（2B/8B）的问题，描述其基于 Qwen3-VL 基座模型进行跨模态信息检索与文档相关性打分的能力。

---

## 【技术要点】

1. **模型归属**：属于 Qwen 家族的 Qwen3-VL-Embedding 与 Qwen3-VL-Reranker 系列，基于开源 Qwen3-VL 基座，专门为多模态信息检索与跨模态理解设计，可接受 text、images、screenshots、videos 以及混合模态输入。

2. **模型权重**：提供两个规格 —— `Qwen3-VL-Reranker-8B` 与 `Qwen3-VL-Reranker-2B`，均托管于 ModelScope（链接见原文），推荐下载到多节点共享目录如 `/root/.cache/`。

3. **三类硬件镜像**：
   - **A3 系列**：镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`
   - **A2 系列**：镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`
   - **Atlas 300I DUO（310P）**：镜像 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p`

4. **核心启动参数**（`vllm serve`）：
   - `--runner pooling` —— 指定为池化（重排序）模式而非生成模式；
   - `--hf_overrides '{"architectures": ["Qwen3VLForSequenceClassification"],"classifier_from_token": ["no", "yes"],"is_original_qwen3_reranker": true}'` —— 覆盖 HF 架构为序列分类，并标记 token 维度上 `no`/`yes` 对应二分类输出；
   - `--chat-template ./qwen3_vl_reranker.jinja` —— 自定义聊天模板；
   - `--max-model-len 1024` —— 显式且保守的上下文长度。

5. **Atlas 300I DUO 专属配置**：
   - `--compilation-config '{"cudagraph_capture_sizes": [1024,512]}'` —— 因硬件流（hardware streams）受限，需缩小 cudagraph 捕获尺寸；
   - `--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}'` —— 关闭 norm-quant 融合；
   - `--dtype float16` —— 强制 float16。

6. **Chat Template 三段式结构**：`system` 提示判别文档是否满足要求（输出仅限 "yes" 或 "no"）；`user` 中通过 Jinja selectattr/map 提取三条 role：`system`（Instruct）、`query`（Query）、`document`（Document），由 `assistant` 完成判断。

---

## 【关键机制与数据】

**工作原理**：本文档属于"部署运维型指南"，并未详述模型的内部推理数学机制（无 softmax、logits、温度系数等内部公式），其核心"机制"集中在**请求侧协议**与**服务侧架构映射**两层：

- **请求侧**：客户端 POST 到 `/v1/rerank` 端点，提交 `query` 与 `documents` 列表；服务端把 query 与每个 document 通过自定义 Jinja 模板拼装为多轮对话，再送入被 `--hf_overrides` 重写为 `Qwen3VLForSequenceClassification` 的分类模型，从 `no`/`yes` token 上抽取相关性概率，作为 `relevance_score` 返回。

- **服务侧**：通过 `vllm serve` 启动池化（pooling/rerank）服务，使用自定义聊天模板控制输入形态；`classifier_from_token` 控制二分类输出头映射。

**性能/Token 数据**（原文示例返回）：
- 原文示例 query（`"What is the capital of China?"`）+ 2 篇 documents 时，响应 `usage.prompt_tokens = 179`，`total_tokens = 179`（原文："prompt_tokens": 179, "total_tokens": 179）。
- 第 0 个文档（"The capital of China is Beijing."）`relevance_score = 0.7209711670875549`；
- 第 1 个文档（关于 Gravity 的文本）`relevance_score = 0.18871910870075226`。
- 这表明相关文档得分约为无关文档的 **3.8 倍**，符合重排序模型应有的判别行为。

---

## 【表格解读】

**原文无表格。** 文档通过命令块（shell、jinja、json）和分段式文字描述配置，没有以 markdown 表格形式呈现参数矩阵。但文档中存在若干"功能性等价表"，可用表格形式重述如下以辅助理解（非逐字还原，原文以代码块呈现）：

| 维度 | A3 / A2 系列 | Atlas 300I DUO |
|---|---|---|
| 镜像 tag 后缀 | `-a3` / 无后缀 | `-310p` |
| `--compilation-config` | 未指定 | `{"cudagraph_capture_sizes": [1024,512]}` |
| `--additional-config` | 未指定 | `{"ascend_compilation_config": {"fuse_norm_quant": false}}` |
| `--dtype` | 未指定（默认） | `float16` |
| `--max-model-len` | `1024` | `1024` |
| `--runner` | `pooling` | `pooling` |
| `--hf_overrides` | 三项 JSON 相同 | 三项 JSON 相同 |
| `--chat-template` | `./qwen3_vl_reranker.jinja` | `./qwen3_vl_reranker.jinja` |

---

## 【公式解读】

**原文无数学公式（LaTeX）。** 文档中唯一的"类公式"是 Jinja 模板中的字符串拼接表达式，例如：

```
<Instruct>: {{ messages | selectattr("role", "eq", "system") | map(attribute="content") | first | default("Given a search query, retrieve relevant candidates that answer the query.") }}
```

- `messages`：Jinja 上下文变量，代表传入的对话消息列表；
- `selectattr("role", "eq", "system")`：筛选出 `role == "system"` 的消息；
- `map(attribute="content")`：抽取这些消息的 `content` 字段；
- `first`：取第一条；
- `default("...")`：若筛选为空，则回落到默认 Instruct 文案 `"Given a search query, retrieve relevant candidates that answer the query."`；

对应的 `query` 与 `document` 字段采用同结构表达，仅把 `role` 改为 `"query"` 和 `"document"`，且无 `default()` 回退（默认必传）。该模板把 `{Instruct, Query, Document}` 三段拼成单条 user 消息，让模型在 `assistant` 位置输出 "yes" 或 "no"，再由 `classifier_from_token: ["no", "yes"]` 映射为二分类 logit。

---

## 【关联】

文档通过文末内部链接与以下模块/页面形成上下游关联：

1. **`../../user_guide/support_matrix/supported_models.md`**（"Supported Features List"）
   - 关联点：Qwen3-VL-Reranker 的能力矩阵（支持的精度、上下文、采样模式等）由该页面统一定义，本文档只指引读者去那里查阅，并未在本指南中重复列举。

2. **`../../getting_started/installation.md#installation-prebuilt-image`**（"using docker"）
   - 关联点：本文档第 4.1 节的 docker run 命令依赖此页给出的镜像选取方法（按机器类型选 tag、按节点启动容器），本文是该页"Qwen3-VL-Reranker 落地"的具体示例。

3. **`../../getting_started/installation.md`**（"Source Code Installation"）
   - 关联点：第 4.2 节"若不想用 docker，可源码安装 `vllm-ascend`"，其安装步骤详细指向此页；多节点部署需要每个节点都按此页配置。

4. **`../../faqs.md`**（"Public FAQs"）
   - 关联点：本文档在第 5.1 节末尾与第 6 节前后两次提示读者，遇常见问题请参考 FAQs；尤其针对 Atlas 300I DUO 因 `max-model-len` 自动解析过大而触发的 attention mask O(max_model_len²) OOM 问题，建议用户显式设置保守值（如 1024）。

5. **外部依赖**：`examples/pooling/score`（vllm 主仓）与 MTEB 评估平台 —— 分别对应功能验证的"更多示例"与第 7 节 Accuracy Evaluation 的 MTEB 评估方法（原文末尾被截断）。

---

## 【使用方法】

**1. 获取权重（原文）：**
- ModelScope：`Qwen/Qwen3-VL-Reranker-8B`、`Qwen/Qwen3-VL-Reranker-2B`
- 推荐路径：`/root/.cache/`

**2. Docker 启动（原文，三种硬件分别）：**
```shell
# A3
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
# A2
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
# Atlas 300I DUO
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p
# 共用 docker run 段（挂载 dcmi、hccn_tool、npu-smi、driver lib64、version.info、ascend_install.info、/root/.cache 等）
```

**3. 自定义聊天模板 `qwen3_vl_reranker.jinja`（原文逐字保留）：** 见上文"公式解读"中的三段式 Jinja。

**4. 启动服务（原文）：**

A3/A2 系列：
```shell
vllm serve Qwen/Qwen3-VL-Reranker-2B \
    --served-model-name Qwen/Qwen3-VL-Reranker-2B \
    --runner pooling \
    --hf_overrides '{"architectures": ["Qwen3VLForSequenceClassification"],"classifier_from_token": ["no", "yes"],"is_original_qwen3_reranker": true}' \
    --chat-template ./qwen3_vl_reranker.jinja \
    --port 8000 \
    --max-model-len 1024
```

Atlas 300I DUO（附加 `--compilation-config`、`--additional-config`、`--dtype float16`，见原文）。

**5. 功能验证（原文）：** `curl http://localhost:8000/v1/rerank` POST `query` 与 `documents`，期望返回 HTTP 200 与含 `relevance_score` 的 JSON。

**6. 常见问题处置（原文）：**
- Atlas 300I DUO 上若 `--max-model-len` 自动解析过大导致 O(N²) attention mask OOM，须显式指定保守值（如 `1024`）；
- 其它问题请参考 [`../../faqs.md`](../../faqs.md)。
